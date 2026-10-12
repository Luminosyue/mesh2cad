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
      -0.01854924818197323,
      -0.0005055083208743172,
      -0.9998278201036521
    ],
    [
      0.00012795180581114625,
      -0.9999998651982259,
      0.0005032214875529805
    ],
    [
      -0.9998279397077372,
      -0.00011859539481935989,
      0.018549310362204172
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -49.80839647782677,
      "length": 99.4745404949132,
      "loops": [
        [
          [
            28.328953,
            2.88676
          ],
          [
            -28.350695,
            2.855357
          ],
          [
            -28.753351,
            2.472618
          ],
          [
            -28.944743,
            1.873037
          ],
          [
            -28.962459,
            -2.024884
          ],
          [
            -28.653263,
            -2.461389
          ],
          [
            -28.053573,
            -2.651718
          ],
          [
            -19.367548,
            -2.863944
          ],
          [
            19.133175,
            -2.814142
          ],
          [
            28.326153,
            -2.676524
          ],
          [
            28.823849,
            -2.353935
          ],
          [
            29.100752,
            -1.454554
          ],
          [
            29.014535,
            2.143576
          ],
          [
            28.689108,
            2.743423
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    0.003949550000000024,
    -0.475415235,
    -0.01365242500000001
  ],
  "construction_scale": 121.59872261028293,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
