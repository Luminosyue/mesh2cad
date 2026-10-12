"""Inferred standard-feature CAD. Approximate reconstruction, not recovered design history."""
from pathlib import Path
import json
"""Pure CadQuery feature builder. Input contains sketches, never a triangle mesh."""
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp=cq.Workplane('XY',origin=(0,0,z))
    if isinstance(points,dict):
        return wp.center(*points['center']).circle(points['radius']).val()
    if smooth:
        return wp.spline([tuple(p) for p in points],periodic=True).wire().val()
    return wp.polyline([tuple(p) for p in points]).close().wire().val()

def build_model(p):
    if p['operation']=='revolve':
        pts=p['profile']; n=len(pts)
        wp=cq.Workplane('XZ').moveTo(0,pts[0][1]).lineTo(*pts[0])
        bounds=sorted(set(int(i*(n-1)/p['segments']) for i in range(p['segments']+1)))
        def tangent(k):
            a,b=pts[max(0,k-1)],pts[min(n-1,k+1)];x,y=b[0]-a[0],b[1]-a[1];d=sqrt(x*x+y*y);return (x/d,y/d)
        for a,b in zip(bounds[:-1],bounds[1:]):
            wp=wp.spline([tuple(q) for q in pts[a+1:b+1]],includeCurrent=True,tangents=[tangent(a),tangent(b)],scale=False)
        shape=wp.lineTo(0,pts[-1][1]).close().revolve(360,(0,0),(0,1)).val().translate((*p['center_xy'],0))
    else:
        features=[]
        for feature in p['features']:
            if feature['type']=='extrude':
                wires=[sketch_wire(q,feature['start']) for q in feature['loops']]
                shape=cq.Workplane('XY').newObject(wires).toPending().extrude(feature['length'],combine=False).val()
            else:
                wires=[sketch_wire(q,z,feature.get('smooth',False)) for z,q in feature['sections']]
                shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()
                for pocket in feature.get('pockets',[]):
                    pw=[sketch_wire(q,z,True) for z,q in pocket]
                    tool=cq.Workplane('XY').newObject(pw).toPending().loft(ruled=True,combine=False).val()
                    shape=shape.cut(tool)
            features.append((shape,feature.get('cut',False)))
        shape=features[0][0]
        for addition,cut in features[1:]:
            shape=shape.cut(addition) if cut else shape.fuse(addition)
        shape=shape.clean()
    if 'basis' in p:
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS=json.loads(r'''{
  "operation": "extrude",
  "basis": [
    [
      0.9999998340334353,
      -0.0005750351282759313,
      -3.560481431437176e-05
    ],
    [
      0.00016604966810728034,
      0.2284845838592168,
      0.9735475167479952
    ],
    [
      -0.000551688869993957,
      -0.9735473610838263,
      0.22848464142280756
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -51.09293912164658,
      "length": 102.1165738000812,
      "loops": [
        [
          [
            -0.416582,
            -3.546535
          ],
          [
            -3.981383,
            -3.225031
          ],
          [
            -4.872628,
            -2.874746
          ],
          [
            -5.700847,
            -2.196374
          ],
          [
            -6.204798,
            -1.410064
          ],
          [
            -6.467146,
            0.420733
          ],
          [
            -6.282203,
            1.336145
          ],
          [
            -5.742183,
            2.251562
          ],
          [
            -4.873593,
            2.933536
          ],
          [
            -3.982473,
            3.337375
          ],
          [
            -2.200144,
            3.61051
          ],
          [
            0.36261,
            3.64729
          ],
          [
            4.038217,
            3.294885
          ],
          [
            5.592913,
            2.251977
          ],
          [
            6.13571,
            1.336599
          ],
          [
            6.310612,
            -0.494201
          ],
          [
            6.06096,
            -1.409615
          ],
          [
            5.409966,
            -2.325033
          ],
          [
            4.039288,
            -3.15581
          ],
          [
            2.25696,
            -3.435419
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    0.001154215,
    0.283943185,
    -0.22057007
  ],
  "construction_scale": 361.4159946166365,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
