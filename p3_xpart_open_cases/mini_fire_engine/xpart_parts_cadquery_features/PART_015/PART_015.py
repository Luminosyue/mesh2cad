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
      "start": -49.99999999999999,
      "length": 99.99999999999999,
      "loops": [
        [
          [
            7.270401,
            16.245221
          ],
          [
            4.437739,
            16.886274
          ],
          [
            -1.236787,
            17.205908
          ],
          [
            -4.074047,
            16.904958
          ],
          [
            -7.857064,
            15.902103
          ],
          [
            -9.748573,
            15.099529
          ],
          [
            -11.640081,
            13.966657
          ],
          [
            -14.477342,
            11.698435
          ],
          [
            -16.368851,
            9.439984
          ],
          [
            -17.813884,
            6.958615
          ],
          [
            -18.793901,
            4.121354
          ],
          [
            -19.049112,
            1.284094
          ],
          [
            -18.505809,
            -2.498924
          ],
          [
            -17.500943,
            -5.336184
          ],
          [
            -16.016496,
            -8.173445
          ],
          [
            -13.53159,
            -11.391175
          ],
          [
            -11.640081,
            -13.163377
          ],
          [
            -7.857064,
            -15.557415
          ],
          [
            -4.074047,
            -16.881017
          ],
          [
            -1.236787,
            -17.26481
          ],
          [
            2.546231,
            -17.222307
          ],
          [
            6.329247,
            -16.398935
          ],
          [
            9.166512,
            -15.231317
          ],
          [
            11.058017,
            -14.132294
          ],
          [
            12.692948,
            -12.902218
          ],
          [
            15.335723,
            -10.069174
          ],
          [
            17.07208,
            -7.227689
          ],
          [
            18.215711,
            -4.390429
          ],
          [
            18.980757,
            -0.607411
          ],
          [
            19.046372,
            2.229849
          ],
          [
            18.702,
            5.06711
          ],
          [
            17.699848,
            7.904371
          ],
          [
            15.022885,
            11.687388
          ],
          [
            12.949522,
            13.479278
          ],
          [
            10.112261,
            15.165405
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    -0.118422695,
    0.555378925,
    -0.75313792
  ],
  "construction_scale": 95.88634629727922,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
