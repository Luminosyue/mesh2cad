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
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -0.302044,
            22.034537
          ],
          [
            -0.008573,
            22.287805
          ],
          [
            0.438234,
            22.034537
          ],
          [
            0.489467,
            21.537317
          ],
          [
            0.240037,
            21.173896
          ],
          [
            -0.261267,
            21.288706
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -0.240584,
            -17.237608
          ],
          [
            -0.384798,
            -16.99724
          ],
          [
            -0.351843,
            -16.500021
          ],
          [
            -0.01992,
            -16.25183
          ],
          [
            0.240037,
            -16.31716
          ],
          [
            0.433436,
            -16.99724
          ],
          [
            0.240037,
            -17.256391
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 84.85048484848484,
      "loops": [
        [
          [
            0.793626,
            -30.919402
          ],
          [
            0.78153,
            30.984498
          ],
          [
            0.571302,
            31.978936
          ],
          [
            0.240037,
            32.295697
          ],
          [
            -0.008573,
            32.323961
          ],
          [
            -0.483868,
            31.953737
          ],
          [
            -0.697448,
            30.487279
          ],
          [
            -0.715381,
            4.631834
          ],
          [
            -0.693735,
            -30.919402
          ],
          [
            -0.505793,
            -32.160472
          ],
          [
            -0.008573,
            -32.527169
          ],
          [
            0.568862,
            -32.162451
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            0.297495,
            -21.894633
          ],
          [
            0.14333,
            -20.975
          ],
          [
            0.435461,
            -20.22917
          ],
          [
            0.422535,
            -19.731951
          ],
          [
            0.240037,
            -19.396069
          ],
          [
            -0.008573,
            -19.298006
          ],
          [
            -0.32555,
            -19.48334
          ],
          [
            -0.448201,
            -19.980561
          ],
          [
            -0.186474,
            -20.975
          ],
          [
            -0.310911,
            -21.720832
          ],
          [
            -0.008573,
            -22.151313
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            0.266287,
            22.292933
          ],
          [
            0.423876,
            22.034537
          ],
          [
            0.394893,
            21.537317
          ],
          [
            -0.021027,
            21.288706
          ],
          [
            -0.345713,
            21.537317
          ],
          [
            -0.372995,
            22.034537
          ],
          [
            -0.221888,
            22.283147
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0013162600000000135,
    8.502999999999983e-05,
    0.0009100900000000023
  ],
  "construction_scale": 100.82244904584658,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
