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
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            4.2224,
            14.821345
          ],
          [
            4.20812,
            -14.764965
          ],
          [
            4.382462,
            -15.222387
          ],
          [
            12.600883,
            -15.322663
          ],
          [
            13.148777,
            -15.48071
          ],
          [
            13.446638,
            -15.870178
          ],
          [
            13.148777,
            -16.248382
          ],
          [
            12.600883,
            -16.418331
          ],
          [
            7.669832,
            -16.335425
          ],
          [
            4.382462,
            -16.417786
          ],
          [
            3.286673,
            -16.608867
          ],
          [
            -0.000694,
            -16.60192
          ],
          [
            -1.644378,
            -16.311303
          ],
          [
            -12.054375,
            -16.365777
          ],
          [
            -13.150164,
            -16.205452
          ],
          [
            -13.417254,
            -15.860754
          ],
          [
            -13.150164,
            -15.470083
          ],
          [
            -12.602271,
            -15.316701
          ],
          [
            -2.192273,
            -15.275291
          ],
          [
            -1.578081,
            -14.764965
          ],
          [
            -1.50697,
            14.273451
          ],
          [
            -1.284727,
            15.917134
          ],
          [
            -0.657382,
            16.465029
          ],
          [
            2.738778,
            16.607174
          ],
          [
            3.419789,
            16.465029
          ],
          [
            3.976244,
            15.917134
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    -5.907500000000565e-05,
    -0.147946095,
    0.0023389499999999994
  ],
  "construction_scale": 222.195682182406,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
