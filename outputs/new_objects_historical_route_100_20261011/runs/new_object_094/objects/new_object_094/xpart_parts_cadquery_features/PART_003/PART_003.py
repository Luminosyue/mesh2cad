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
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -10.134075206373739,
      "length": 3.071337243727569,
      "loops": [
        [
          [
            8.293023,
            49.767343
          ],
          [
            -4.076713,
            49.769631
          ],
          [
            -5.107526,
            49.512895
          ],
          [
            -5.273,
            49.200124
          ],
          [
            -5.107526,
            48.625557
          ],
          [
            -4.175331,
            48.401439
          ],
          [
            8.293023,
            48.414797
          ],
          [
            8.808427,
            48.545669
          ],
          [
            9.045343,
            48.783337
          ],
          [
            9.081514,
            49.298742
          ],
          [
            8.808427,
            49.603974
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.0631433256544245,
      "length": 1.2287781152959816,
      "loops": [
        [
          [
            9.96318,
            -48.628319
          ],
          [
            10.033333,
            48.783337
          ],
          [
            9.83924,
            49.430775
          ],
          [
            9.347171,
            49.81415
          ],
          [
            8.907372,
            49.873031
          ],
          [
            -5.838158,
            49.81415
          ],
          [
            -6.632414,
            49.298742
          ],
          [
            -6.729889,
            48.366875
          ],
          [
            -6.75715,
            -33.166149
          ],
          [
            -6.582675,
            -49.143727
          ],
          [
            -6.138331,
            -49.534266
          ],
          [
            -5.62293,
            -49.702766
          ],
          [
            9.32383,
            -49.649413
          ],
          [
            9.895397,
            -49.143727
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.834770573366698,
      "length": 6.1422691244468846,
      "loops": [
        [
          [
            -9.752677,
            -29.042907
          ],
          [
            -9.889243,
            -34.196965
          ],
          [
            -9.762897,
            -35.227774
          ],
          [
            -9.230773,
            -35.484105
          ],
          [
            -7.484234,
            -35.62306
          ],
          [
            -7.169144,
            -35.817439
          ],
          [
            -7.04074,
            -36.138467
          ],
          [
            -6.971126,
            -48.112914
          ],
          [
            -6.915968,
            -49.143727
          ],
          [
            -6.653743,
            -49.551807
          ],
          [
            -6.138331,
            -49.863851
          ],
          [
            -5.107526,
            -49.992515
          ],
          [
            8.808427,
            -49.99163
          ],
          [
            9.83924,
            -49.658705
          ],
          [
            10.24435,
            -49.143727
          ],
          [
            10.312683,
            -47.202222
          ],
          [
            10.327469,
            48.267929
          ],
          [
            10.235762,
            49.298742
          ],
          [
            9.83924,
            49.778435
          ],
          [
            9.32383,
            49.951784
          ],
          [
            -5.62293,
            49.989873
          ],
          [
            -6.481665,
            49.81415
          ],
          [
            -6.925545,
            49.298742
          ],
          [
            -6.972954,
            -26.981285
          ],
          [
            -7.169144,
            -27.942707
          ],
          [
            -7.684556,
            -28.189938
          ],
          [
            -9.230773,
            -28.347846
          ],
          [
            -9.565385,
            -28.527502
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.3070931880719314,
      "length": 8.599014629022337,
      "loops": [
        [
          [
            -6.971318,
            -48.628319
          ],
          [
            -6.916279,
            49.298742
          ],
          [
            -6.414814,
            49.81415
          ],
          [
            -5.62293,
            49.966804
          ],
          [
            9.32383,
            49.946137
          ],
          [
            9.83924,
            49.771156
          ],
          [
            10.226978,
            49.298742
          ],
          [
            10.332414,
            48.783337
          ],
          [
            10.309307,
            -48.628319
          ],
          [
            10.244721,
            -49.143727
          ],
          [
            9.839405,
            -49.651609
          ],
          [
            8.808427,
            -49.982154
          ],
          [
            -5.107526,
            -49.980892
          ],
          [
            -6.138331,
            -49.856184
          ],
          [
            -6.653743,
            -49.549998
          ],
          [
            -6.932849,
            -49.143727
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 8.905702454086013,
      "length": 1.2287781152959807,
      "loops": [
        [
          [
            8.808427,
            -49.40879
          ],
          [
            -5.62293,
            -49.411852
          ],
          [
            -6.138331,
            -49.209508
          ],
          [
            -6.384157,
            -47.867092
          ],
          [
            -6.440647,
            48.783337
          ],
          [
            -6.260995,
            49.298742
          ],
          [
            -5.62293,
            49.531255
          ],
          [
            8.808427,
            49.518851
          ],
          [
            9.50829,
            49.298742
          ],
          [
            9.736432,
            48.370737
          ],
          [
            9.626277,
            -48.628319
          ],
          [
            9.32383,
            -49.30776
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.41650101500000003,
    -0.013932830000000007,
    -0.198991225
  ],
  "construction_scale": 209.01992896332303,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
