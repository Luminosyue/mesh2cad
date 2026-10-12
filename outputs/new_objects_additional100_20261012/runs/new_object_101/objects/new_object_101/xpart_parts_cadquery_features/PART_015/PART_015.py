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
      "start": -37.374588867846796,
      "length": 4.531748179657356,
      "loops": [
        [
          [
            10.8124,
            -10.262695
          ],
          [
            -12.824201,
            -10.262315
          ],
          [
            -15.901208,
            -10.014517
          ],
          [
            -17.160836,
            -9.647835
          ],
          [
            -18.474521,
            -8.895592
          ],
          [
            -16.180989,
            -8.382885
          ],
          [
            -12.824201,
            -8.037206
          ],
          [
            -2.614746,
            -7.871657
          ],
          [
            10.8124,
            -8.073536
          ],
          [
            12.070436,
            -8.345556
          ],
          [
            13.121312,
            -8.895592
          ],
          [
            12.724563,
            -10.014517
          ],
          [
            12.52546,
            -10.065352
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -32.844335671744155,
      "length": 33.97839395432454,
      "loops": [
        [
          [
            15.122968,
            -6.657729
          ],
          [
            14.987493,
            9.00728
          ],
          [
            14.684035,
            10.126214
          ],
          [
            13.813862,
            11.245134
          ],
          [
            13.050263,
            11.766989
          ],
          [
            11.931343,
            11.948222
          ],
          [
            -3.733671,
            11.961459
          ],
          [
            -9.767364,
            11.810914
          ],
          [
            -32.825846,
            11.889049
          ],
          [
            -36.182633,
            11.737834
          ],
          [
            -46.252992,
            11.97531
          ],
          [
            -47.371931,
            11.851336
          ],
          [
            -48.490855,
            11.159242
          ],
          [
            -49.510928,
            10.126214
          ],
          [
            -49.851566,
            9.00728
          ],
          [
            -49.84636,
            -10.014517
          ],
          [
            -49.60978,
            -10.542822
          ],
          [
            -49.056679,
            -11.133451
          ],
          [
            -47.371931,
            -11.708524
          ],
          [
            -22.755482,
            -11.580263
          ],
          [
            0.742041,
            -12.243037
          ],
          [
            7.016578,
            -11.995502
          ],
          [
            14.169188,
            -11.187712
          ],
          [
            18.644905,
            -10.967678
          ],
          [
            47.737075,
            -10.709957
          ],
          [
            48.856004,
            -10.657191
          ],
          [
            49.653394,
            -10.014517
          ],
          [
            49.831874,
            -8.895592
          ],
          [
            48.856004,
            -7.884969
          ],
          [
            16.407051,
            -7.642788
          ],
          [
            15.288122,
            -6.993003
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.1325632990256693,
      "length": 27.183014160170572,
      "loops": [
        [
          [
            47.737075,
            -10.074409
          ],
          [
            7.455612,
            -10.2738
          ],
          [
            -7.856721,
            -10.112176
          ],
          [
            -17.160836,
            -10.380092
          ],
          [
            -29.469058,
            -10.128151
          ],
          [
            -48.490855,
            -10.033284
          ],
          [
            -49.60978,
            -9.269336
          ],
          [
            -49.803373,
            -8.895592
          ],
          [
            -49.896471,
            10.126214
          ],
          [
            -49.227769,
            11.245134
          ],
          [
            -48.490855,
            12.099186
          ],
          [
            -47.371931,
            12.687436
          ],
          [
            -42.896205,
            12.33135
          ],
          [
            11.931343,
            12.640945
          ],
          [
            13.075636,
            12.364068
          ],
          [
            14.185753,
            11.300255
          ],
          [
            14.784048,
            10.126214
          ],
          [
            14.963483,
            5.297815
          ],
          [
            14.987454,
            -5.538805
          ],
          [
            15.288122,
            -6.751978
          ],
          [
            16.75973,
            -7.180868
          ],
          [
            47.737075,
            -7.456988
          ],
          [
            48.493836,
            -7.776663
          ],
          [
            48.856004,
            -8.208979
          ],
          [
            49.103366,
            -8.895592
          ],
          [
            48.856004,
            -9.423359
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.314082475641527,
      "length": 4.531748179657349,
      "loops": [
        [
          [
            45.499216,
            -9.766185
          ],
          [
            -3.733671,
            -9.284771
          ],
          [
            -19.209623,
            -9.498795
          ],
          [
            -48.490855,
            -9.428332
          ],
          [
            -49.52911,
            -8.895592
          ],
          [
            -49.84839,
            -7.776663
          ],
          [
            -49.802097,
            10.126214
          ],
          [
            -49.551493,
            11.245134
          ],
          [
            -48.490855,
            12.532706
          ],
          [
            -47.371931,
            12.758237
          ],
          [
            -31.706903,
            12.589284
          ],
          [
            8.574537,
            12.872122
          ],
          [
            11.931343,
            12.77326
          ],
          [
            13.206463,
            12.364068
          ],
          [
            14.239229,
            11.245134
          ],
          [
            14.666735,
            10.126214
          ],
          [
            14.910566,
            -5.538805
          ],
          [
            15.288122,
            -6.66079
          ],
          [
            16.407051,
            -6.9279
          ],
          [
            17.525985,
            -6.948421
          ],
          [
            45.68829,
            -7.195079
          ],
          [
            46.618141,
            -7.384718
          ],
          [
            47.113906,
            -7.776663
          ],
          [
            47.299466,
            -8.895592
          ],
          [
            46.618141,
            -9.583404
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 32.84433567174416,
      "length": 4.531748179657363,
      "loops": [
        [
          [
            -19.622397,
            -4.419875
          ],
          [
            -29.469058,
            -5.781644
          ],
          [
            -47.371931,
            -5.771095
          ],
          [
            -48.490855,
            -5.907519
          ],
          [
            -49.588526,
            -6.634808
          ],
          [
            -49.696499,
            -7.776663
          ],
          [
            -48.490855,
            -8.984512
          ],
          [
            -45.134068,
            -9.035394
          ],
          [
            -29.469058,
            -8.916287
          ],
          [
            -24.993332,
            -9.070671
          ],
          [
            7.319387,
            -8.814799
          ],
          [
            14.169188,
            -8.994275
          ],
          [
            19.898373,
            -9.418467
          ],
          [
            43.261353,
            -9.725957
          ],
          [
            44.514821,
            -9.465661
          ],
          [
            45.243139,
            -8.895592
          ],
          [
            44.991571,
            -7.776663
          ],
          [
            44.380287,
            -7.432081
          ],
          [
            43.395888,
            -7.292595
          ],
          [
            15.288122,
            -6.876017
          ],
          [
            11.499804,
            -5.538805
          ],
          [
            9.69348,
            -4.736096
          ],
          [
            7.455612,
            -4.03675
          ],
          [
            2.979904,
            -3.432609
          ],
          [
            -4.85261,
            -3.239856
          ],
          [
            -8.209397,
            -3.313578
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.19599765000000002,
    -0.34438428,
    0.28098045
  ],
  "construction_scale": 453.7757271551828,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
