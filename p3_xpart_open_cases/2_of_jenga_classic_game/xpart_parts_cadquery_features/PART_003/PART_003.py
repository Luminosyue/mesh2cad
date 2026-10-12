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
      "start": -49.99999999999999,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            -9.281168,
            -24.984633
          ],
          [
            -9.022067,
            28.162985
          ],
          [
            -9.096027,
            29.247628
          ],
          [
            -9.286379,
            29.789952
          ],
          [
            -9.832167,
            30.340815
          ],
          [
            -10.916813,
            30.643017
          ],
          [
            -26.101846,
            30.887726
          ],
          [
            -27.728813,
            30.85846
          ],
          [
            -28.271136,
            30.713769
          ],
          [
            -28.813459,
            30.368764
          ],
          [
            -29.263259,
            29.789952
          ],
          [
            -29.468423,
            28.705307
          ],
          [
            -29.537931,
            26.660287
          ],
          [
            -29.989618,
            -24.984633
          ],
          [
            -29.909411,
            -26.069276
          ],
          [
            -29.355782,
            -26.883604
          ],
          [
            -28.813459,
            -27.162549
          ],
          [
            -27.728813,
            -27.286881
          ],
          [
            -12.001457,
            -27.600815
          ],
          [
            -10.916813,
            -27.478835
          ],
          [
            -9.832167,
            -26.812659
          ],
          [
            -9.390974,
            -26.069276
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -37.878787878787875,
      "length": 75.75957575757575,
      "loops": [
        [
          [
            28.448118,
            -9.799599
          ],
          [
            27.973814,
            -26.682942
          ],
          [
            27.588092,
            -27.753544
          ],
          [
            27.045771,
            -28.18288
          ],
          [
            26.503449,
            -28.358931
          ],
          [
            9.691447,
            -28.05587
          ],
          [
            4.739202,
            -27.79494
          ],
          [
            -8.184886,
            -27.699093
          ],
          [
            -13.157444,
            -27.922546
          ],
          [
            -24.003896,
            -27.803299
          ],
          [
            -27.728813,
            -27.686819
          ],
          [
            -28.271136,
            -27.571892
          ],
          [
            -28.813459,
            -27.217756
          ],
          [
            -29.2226,
            -26.6116
          ],
          [
            -29.398413,
            -25.526955
          ],
          [
            -29.209344,
            -11.426566
          ],
          [
            -28.864449,
            -7.70165
          ],
          [
            -28.921785,
            3.687125
          ],
          [
            -28.528219,
            25.993694
          ],
          [
            -28.364041,
            28.705307
          ],
          [
            -28.243914,
            29.247628
          ],
          [
            -27.831674,
            29.789952
          ],
          [
            -27.186491,
            30.170102
          ],
          [
            -26.101846,
            30.303724
          ],
          [
            -11.459135,
            30.245049
          ],
          [
            25.418804,
            29.749651
          ],
          [
            27.588092,
            29.594917
          ],
          [
            28.276924,
            29.247628
          ],
          [
            28.674902,
            28.705307
          ],
          [
            28.87133,
            27.620662
          ],
          [
            28.984508,
            21.655113
          ],
          [
            28.882979,
            12.435629
          ],
          [
            28.573465,
            9.724015
          ],
          [
            28.8289,
            7.554725
          ],
          [
            28.755627,
            -5.461018
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 37.87878787878788,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            -7.772706,
            -29.323213
          ],
          [
            -7.591548,
            24.909049
          ],
          [
            -7.699374,
            26.536016
          ],
          [
            -8.173681,
            27.543314
          ],
          [
            -8.670684,
            27.845599
          ],
          [
            -9.832167,
            27.546266
          ],
          [
            -24.009393,
            27.568142
          ],
          [
            -26.101846,
            27.449428
          ],
          [
            -26.64417,
            27.207437
          ],
          [
            -27.246789,
            26.536016
          ],
          [
            -27.483147,
            25.993694
          ],
          [
            -27.630386,
            24.909049
          ],
          [
            -27.703967,
            -27.230761
          ],
          [
            -27.594365,
            -29.323213
          ],
          [
            -27.383108,
            -29.865537
          ],
          [
            -26.888765,
            -30.407859
          ],
          [
            -25.559525,
            -30.777712
          ],
          [
            -9.832167,
            -30.898195
          ],
          [
            -8.747522,
            -30.762545
          ],
          [
            -8.179895,
            -30.407859
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 37.87878787878788,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            29.757566,
            -26.069276
          ],
          [
            29.282177,
            27.620662
          ],
          [
            29.108089,
            28.705307
          ],
          [
            28.738496,
            29.247628
          ],
          [
            28.130416,
            29.65403
          ],
          [
            27.588092,
            29.781921
          ],
          [
            25.341965,
            29.865884
          ],
          [
            12.40306,
            29.845094
          ],
          [
            10.776093,
            29.679629
          ],
          [
            10.076889,
            29.247628
          ],
          [
            9.734155,
            28.705307
          ],
          [
            9.588123,
            27.07834
          ],
          [
            9.817503,
            -19.019084
          ],
          [
            10.020783,
            -26.6116
          ],
          [
            10.311542,
            -27.696246
          ],
          [
            10.829527,
            -28.238568
          ],
          [
            11.318414,
            -28.43665
          ],
          [
            12.326221,
            -28.515155
          ],
          [
            27.588092,
            -28.499918
          ],
          [
            28.803955,
            -28.238568
          ],
          [
            29.215062,
            -27.907426
          ],
          [
            29.61356,
            -27.230761
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0006398249999999828,
    -0.014451259999999994,
    0.44899496499999997
  ],
  "construction_scale": 109.96799260610408,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
