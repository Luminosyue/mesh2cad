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
      0.22666048974397415,
      -0.2919365349745877,
      0.9291921663122508
    ],
    [
      0.3906191586698217,
      -0.8466871896658729,
      -0.36129970348145546
    ],
    [
      0.8922116874761854,
      0.4448526299829395,
      -0.07787452939285935
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -6.857961523544811,
      "length": 13.187862693734155,
      "loops": [
        [
          [
            12.210327,
            16.196506
          ],
          [
            -46.216388,
            16.106498
          ],
          [
            -47.224109,
            15.725058
          ],
          [
            -47.876473,
            14.890461
          ],
          [
            -48.033926,
            9.343278
          ],
          [
            -47.949373,
            -14.603952
          ],
          [
            -47.727705,
            -15.674704
          ],
          [
            -46.995048,
            -16.351436
          ],
          [
            -45.513147,
            -16.542695
          ],
          [
            -11.589862,
            -16.290075
          ],
          [
            45.734393,
            -16.344385
          ],
          [
            46.92582,
            -16.070202
          ],
          [
            47.67408,
            -15.254494
          ],
          [
            47.877177,
            -14.073268
          ],
          [
            47.906145,
            -10.731464
          ],
          [
            47.734622,
            14.132388
          ],
          [
            47.522039,
            15.606055
          ],
          [
            47.001993,
            16.282329
          ],
          [
            45.793216,
            16.455283
          ]
        ],
        {
          "center": [
            0.5218494937080318,
            -0.21753823072247513
          ],
          "radius": 6.50721954204055
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    -0.13523438499999998,
    0.36439072,
    -0.32933892
  ],
  "construction_scale": 120.21098663023024,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
