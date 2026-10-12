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
      "start": -16.379081418514794,
      "length": 1.9859983655009588,
      "loops": [
        [
          [
            -37.91872,
            5.740099
          ],
          [
            -2.381447,
            1.811663
          ],
          [
            43.858817,
            -3.754219
          ],
          [
            44.668788,
            -4.045174
          ],
          [
            44.745293,
            -4.385176
          ],
          [
            43.518814,
            -5.900846
          ],
          [
            42.838811,
            -6.187972
          ],
          [
            42.158806,
            -6.167024
          ],
          [
            0.501499,
            -1.19819
          ],
          [
            -39.101654,
            3.262848
          ],
          [
            -43.698752,
            3.97698
          ],
          [
            -44.332912,
            4.501653
          ],
          [
            -45.157139,
            6.154886
          ],
          [
            -44.922336,
            6.494886
          ],
          [
            -44.038755,
            6.61565
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -14.393738216270576,
      "length": 8.934699573355717,
      "loops": [
        [
          [
            -1.02144,
            1.273601
          ],
          [
            14.945585,
            -0.399452
          ],
          [
            22.765629,
            -1.443563
          ],
          [
            37.398779,
            -3.066779
          ],
          [
            48.618841,
            -4.033533
          ],
          [
            49.638852,
            -4.317732
          ],
          [
            49.984788,
            -4.725177
          ],
          [
            49.503702,
            -5.745185
          ],
          [
            48.618841,
            -6.876708
          ],
          [
            47.938841,
            -7.1346
          ],
          [
            46.918833,
            -7.141108
          ],
          [
            -2.72145,
            -1.017405
          ],
          [
            -28.901599,
            1.99153
          ],
          [
            -29.908537,
            2.262146
          ],
          [
            -30.797477,
            2.754864
          ],
          [
            -31.165549,
            3.094867
          ],
          [
            -31.240944,
            3.434869
          ],
          [
            -30.571569,
            3.907397
          ],
          [
            -29.496288,
            4.127659
          ],
          [
            -23.121565,
            3.730567
          ],
          [
            -9.521488,
            2.341586
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -14.393738216270576,
      "length": 8.934699573355717,
      "loops": [
        [
          [
            -37.741649,
            3.071375
          ],
          [
            -48.621714,
            4.359775
          ],
          [
            -49.194834,
            4.794878
          ],
          [
            -49.884597,
            6.154886
          ],
          [
            -49.987441,
            6.494886
          ],
          [
            -49.882372,
            6.834888
          ],
          [
            -49.301714,
            7.128569
          ],
          [
            -48.621714,
            7.139272
          ],
          [
            -37.414713,
            5.072993
          ],
          [
            -35.495622,
            4.454875
          ],
          [
            -35.079007,
            4.114873
          ],
          [
            -35.064693,
            3.817933
          ],
          [
            -35.535562,
            3.434869
          ],
          [
            -36.061482,
            3.284552
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.4596938061715985,
      "length": 12.905385977844155,
      "loops": [
        [
          [
            49.298846,
            -4.126733
          ],
          [
            39.09879,
            -3.232603
          ],
          [
            22.440971,
            -1.40811
          ],
          [
            10.878629,
            0.053209
          ],
          [
            4.080866,
            0.572299
          ],
          [
            3.06086,
            0.406698
          ],
          [
            2.678283,
            0.03485
          ],
          [
            2.85342,
            -0.645155
          ],
          [
            3.370449,
            -1.325158
          ],
          [
            4.420868,
            -1.777486
          ],
          [
            46.578833,
            -7.058334
          ],
          [
            48.278842,
            -6.994274
          ],
          [
            48.896946,
            -6.425187
          ],
          [
            49.758605,
            -5.065178
          ],
          [
            49.878517,
            -4.725177
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.4596938061715985,
      "length": 12.905385977844155,
      "loops": [
        [
          [
            -21.081555,
            3.470064
          ],
          [
            -23.461568,
            3.543642
          ],
          [
            -24.8193,
            3.407527
          ],
          [
            -25.50158,
            3.198742
          ],
          [
            -25.857529,
            2.754864
          ],
          [
            -25.50158,
            1.978597
          ],
          [
            -24.481574,
            1.552357
          ],
          [
            -7.141475,
            -0.45664
          ],
          [
            -6.121469,
            -0.506218
          ],
          [
            -5.441465,
            -0.307145
          ],
          [
            -4.761461,
            0.332467
          ],
          [
            -4.589462,
            0.714854
          ],
          [
            -5.061319,
            1.394859
          ],
          [
            -6.461471,
            1.845808
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.4596938061715985,
      "length": 12.905385977844155,
      "loops": [
        [
          [
            -46.922235,
            4.099542
          ],
          [
            -42.501676,
            3.722082
          ],
          [
            -41.676014,
            4.114873
          ],
          [
            -41.445137,
            4.794878
          ],
          [
            -41.821671,
            5.500508
          ],
          [
            -42.841676,
            5.913661
          ],
          [
            -48.621714,
            7.10582
          ],
          [
            -49.301714,
            7.118572
          ],
          [
            -49.793826,
            6.834888
          ],
          [
            -49.976494,
            6.494886
          ],
          [
            -49.897023,
            6.154886
          ],
          [
            -49.213167,
            4.794878
          ],
          [
            -48.619438,
            4.398816
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.445037008415817,
      "length": 6.949356371111501,
      "loops": [
        [
          [
            5.34688,
            -1.921891
          ],
          [
            44.19882,
            -6.665873
          ],
          [
            44.878823,
            -6.580976
          ],
          [
            45.763542,
            -6.066841
          ],
          [
            47.009118,
            -4.725177
          ],
          [
            47.082046,
            -4.385176
          ],
          [
            46.487116,
            -4.013653
          ],
          [
            43.858817,
            -3.674454
          ],
          [
            25.15871,
            -1.63837
          ],
          [
            14.61865,
            -0.220434
          ],
          [
            -16.413244,
            3.34658
          ],
          [
            -33.321625,
            5.128197
          ],
          [
            -44.633405,
            6.736844
          ],
          [
            -45.901698,
            6.795479
          ],
          [
            -46.408088,
            6.494886
          ],
          [
            -46.188245,
            5.814884
          ],
          [
            -45.157483,
            4.454875
          ],
          [
            -44.449971,
            4.038316
          ],
          [
            -43.429965,
            3.80556
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.393738216270577,
      "length": 1.985998365500957,
      "loops": [
        [
          [
            42.461761,
            -6.291772
          ],
          [
            -17.923512,
            1.394859
          ],
          [
            -37.056039,
            4.120481
          ],
          [
            -43.521682,
            5.14033
          ],
          [
            -44.116499,
            5.581503
          ],
          [
            -44.472949,
            6.154886
          ],
          [
            -44.189438,
            6.494886
          ],
          [
            -43.521682,
            6.512068
          ],
          [
            12.881592,
            0.046585
          ],
          [
            25.461664,
            -1.647342
          ],
          [
            43.178812,
            -3.659504
          ],
          [
            44.501772,
            -3.890964
          ],
          [
            44.857407,
            -4.045174
          ],
          [
            45.001813,
            -4.385176
          ],
          [
            44.220089,
            -5.405182
          ],
          [
            43.518814,
            -6.020587
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0032422600000000038,
    -0.034511085,
    -0.244368955
  ],
  "construction_scale": 137.88593532159612,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
