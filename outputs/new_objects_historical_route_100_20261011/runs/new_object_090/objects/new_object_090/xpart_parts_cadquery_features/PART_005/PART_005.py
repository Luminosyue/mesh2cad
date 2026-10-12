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
      "start": -10.178774674910027,
      "length": 2.467988890359125,
      "loops": [
        [
          [
            49.472024,
            4.369424
          ],
          [
            49.861384,
            4.142266
          ],
          [
            49.950135,
            2.451946
          ],
          [
            49.81639,
            1.836713
          ],
          [
            49.307721,
            1.455409
          ],
          [
            45.238344,
            1.428997
          ],
          [
            44.675336,
            1.598905
          ],
          [
            44.349123,
            2.107574
          ],
          [
            44.29749,
            3.63359
          ],
          [
            44.464312,
            4.142266
          ],
          [
            44.729672,
            4.361264
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -10.178774674910027,
      "length": 2.467988890359125,
      "loops": [
        [
          [
            -45.28893,
            1.648538
          ],
          [
            -45.067747,
            2.107574
          ],
          [
            -45.01268,
            3.12492
          ],
          [
            -45.016819,
            3.63359
          ],
          [
            -45.305246,
            4.294161
          ],
          [
            -48.357281,
            4.40297
          ],
          [
            -49.046288,
            4.142266
          ],
          [
            -49.23232,
            3.63359
          ],
          [
            -49.215002,
            2.107574
          ],
          [
            -48.865948,
            1.602742
          ],
          [
            -45.81392,
            1.463271
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.711192935537898,
      "length": 1.234198020673061,
      "loops": [
        [
          [
            -44.287904,
            1.592978
          ],
          [
            44.220999,
            1.518739
          ],
          [
            45.238344,
            1.371353
          ],
          [
            48.799047,
            1.403661
          ],
          [
            49.307721,
            1.439374
          ],
          [
            49.81639,
            1.770674
          ],
          [
            49.954364,
            2.107574
          ],
          [
            49.991295,
            3.63359
          ],
          [
            49.902058,
            4.142266
          ],
          [
            49.307721,
            4.529842
          ],
          [
            45.238344,
            4.552028
          ],
          [
            43.683276,
            4.388077
          ],
          [
            -44.287904,
            4.370409
          ],
          [
            -45.305246,
            4.499145
          ],
          [
            -48.357281,
            4.481101
          ],
          [
            -48.865948,
            4.368003
          ],
          [
            -49.112801,
            4.142266
          ],
          [
            -49.25372,
            3.63359
          ],
          [
            -49.252118,
            2.107574
          ],
          [
            -48.978252,
            1.598905
          ],
          [
            -48.357281,
            1.431237
          ],
          [
            -45.81392,
            1.371298
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -6.477402065851834,
      "length": 3.7017797600451896,
      "loops": [
        [
          [
            49.664049,
            1.598905
          ],
          [
            48.799047,
            1.383016
          ],
          [
            43.108182,
            1.366218
          ],
          [
            -47.339933,
            1.399093
          ],
          [
            -48.968726,
            1.598905
          ],
          [
            -49.283155,
            2.107574
          ],
          [
            -49.283419,
            3.63359
          ],
          [
            -49.140157,
            4.142266
          ],
          [
            -48.865948,
            4.410591
          ],
          [
            -45.305246,
            4.535962
          ],
          [
            48.799047,
            4.54481
          ],
          [
            49.307721,
            4.532473
          ],
          [
            49.861876,
            4.142266
          ],
          [
            49.912664,
            2.107574
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.7760294567936405,
      "length": 1.234198020673061,
      "loops": [
        [
          [
            -48.793561,
            -4.505155
          ],
          [
            -48.378602,
            -3.996485
          ],
          [
            -48.275937,
            1.090237
          ],
          [
            -47.848607,
            1.469945
          ],
          [
            -46.322591,
            1.345237
          ],
          [
            47.781701,
            1.386028
          ],
          [
            48.970299,
            1.52234
          ],
          [
            49.307721,
            1.772827
          ],
          [
            49.477736,
            2.107574
          ],
          [
            49.486579,
            3.63359
          ],
          [
            49.381364,
            4.142266
          ],
          [
            48.970299,
            4.352178
          ],
          [
            46.76436,
            4.552645
          ],
          [
            -48.019859,
            4.494463
          ],
          [
            -48.528531,
            4.417869
          ],
          [
            -48.991616,
            4.142266
          ],
          [
            -49.12202,
            2.476539
          ],
          [
            -49.863075,
            1.427654
          ],
          [
            -49.934202,
            -3.996485
          ],
          [
            -49.374622,
            -4.56271
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.542238587107576,
      "length": 11.72142041300461,
      "loops": [
        [
          [
            -48.355622,
            1.598905
          ],
          [
            -48.397855,
            -3.996485
          ],
          [
            -48.791181,
            -4.505155
          ],
          [
            -49.374622,
            -4.57101
          ],
          [
            -49.883294,
            -4.192851
          ],
          [
            -49.992209,
            -3.487815
          ],
          [
            -49.938295,
            1.598905
          ],
          [
            -49.79571,
            2.107574
          ],
          [
            -49.374622,
            2.343121
          ],
          [
            -48.865948,
            2.322102
          ],
          [
            -48.536508,
            2.107574
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.478015805,
    -0.31928831,
    0.002627980000000002
  ],
  "construction_scale": 206.28910287303373,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
