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
  "operation": "base_and_profile_pads",
  "basis": [
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.0,
      "length": 54.54745454545455,
      "loops": [
        [
          [
            0.04991,
            -1.698107
          ],
          [
            -1.31404,
            -1.157739
          ],
          [
            -1.769058,
            -0.143876
          ],
          [
            -1.764806,
            0.194077
          ],
          [
            -1.301904,
            1.146543
          ],
          [
            -0.625996,
            1.557975
          ],
          [
            0.04991,
            1.714567
          ],
          [
            1.063776,
            1.325571
          ],
          [
            1.715471,
            0.194077
          ],
          [
            1.743002,
            -0.143876
          ],
          [
            1.268492,
            -1.157739
          ]
        ],
        [
          [
            -0.296834,
            -0.448088
          ],
          [
            -0.626597,
            -0.143876
          ],
          [
            -0.625996,
            0.220893
          ],
          [
            -0.288042,
            0.542433
          ],
          [
            0.387866,
            0.429308
          ],
          [
            0.586467,
            0.194077
          ],
          [
            0.53051,
            -0.143876
          ],
          [
            0.04991,
            -0.480473
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            1.751089,
            0.194077
          ],
          [
            1.063776,
            1.385544
          ],
          [
            0.04991,
            1.768258
          ],
          [
            -0.625996,
            1.599825
          ],
          [
            -1.293544,
            1.20794
          ],
          [
            -1.772692,
            0.194077
          ],
          [
            -1.782079,
            -0.143876
          ],
          [
            -1.301904,
            -1.162175
          ],
          [
            0.04991,
            -1.719943
          ],
          [
            1.27556,
            -1.157739
          ],
          [
            1.743747,
            -0.143876
          ]
        ],
        [
          [
            0.576035,
            0.194077
          ],
          [
            0.387866,
            -0.342999
          ],
          [
            0.04991,
            -0.503321
          ],
          [
            -0.288042,
            -0.472062
          ],
          [
            -0.619834,
            -0.143876
          ],
          [
            -0.650704,
            0.194077
          ],
          [
            -0.288042,
            0.585249
          ],
          [
            0.294542,
            0.532032
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.101464915,
    -0.267918985,
    0.413529465
  ],
  "construction_scale": 68.5277426445559,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
