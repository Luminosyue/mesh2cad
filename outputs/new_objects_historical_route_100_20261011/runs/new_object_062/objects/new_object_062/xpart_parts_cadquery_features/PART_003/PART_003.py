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
            29.918721,
            0.842972
          ],
          [
            28.963925,
            1.254275
          ],
          [
            14.745085,
            1.110597
          ],
          [
            8.603327,
            1.293388
          ],
          [
            0.145847,
            1.246348
          ],
          [
            -4.742951,
            0.99202
          ],
          [
            -6.432193,
            1.15518
          ],
          [
            -7.058673,
            0.618097
          ],
          [
            -27.106031,
            0.723688
          ],
          [
            -28.045751,
            0.901496
          ],
          [
            -29.611952,
            0.924098
          ],
          [
            -29.92519,
            0.909459
          ],
          [
            -30.13597,
            0.695737
          ],
          [
            -30.242474,
            -0.434183
          ],
          [
            -29.92519,
            -0.996377
          ],
          [
            -28.045751,
            -1.079554
          ],
          [
            -5.492473,
            -1.068176
          ],
          [
            28.024205,
            -1.355999
          ],
          [
            29.903645,
            -1.275783
          ],
          [
            30.179121,
            -1.060659
          ],
          [
            30.162069,
            0.505536
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            22.597124,
            0.83555
          ],
          [
            7.037127,
            0.761671
          ],
          [
            -6.432193,
            0.93119
          ],
          [
            -7.058673,
            0.645548
          ],
          [
            -27.106031,
            0.658047
          ],
          [
            -28.045751,
            0.947081
          ],
          [
            -29.611952,
            0.984082
          ],
          [
            -30.095974,
            0.81878
          ],
          [
            -30.21353,
            -0.434183
          ],
          [
            -29.92519,
            -1.111794
          ],
          [
            -29.611952,
            -1.252232
          ],
          [
            -23.135914,
            -1.38354
          ],
          [
            -9.666595,
            -1.356966
          ],
          [
            -7.998393,
            -1.213143
          ],
          [
            -5.594476,
            -1.430198
          ],
          [
            29.277166,
            -1.488493
          ],
          [
            29.903645,
            -1.47157
          ],
          [
            30.198274,
            -1.060659
          ],
          [
            30.184807,
            1.132018
          ],
          [
            29.903645,
            1.478499
          ],
          [
            20.633661,
            1.445261
          ],
          [
            24.578566,
            1.368908
          ],
          [
            26.680095,
            1.132018
          ]
        ],
        [
          [
            9.856286,
            -0.860282
          ],
          [
            -2.69041,
            -0.747421
          ],
          [
            18.268965,
            -0.747421
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            -7.058673,
            0.635417
          ],
          [
            -27.106031,
            0.660122
          ],
          [
            -28.045751,
            0.917574
          ],
          [
            -29.611952,
            0.930255
          ],
          [
            -30.0605,
            0.81878
          ],
          [
            -30.226101,
            -0.434183
          ],
          [
            -29.92519,
            -1.085281
          ],
          [
            -29.611952,
            -1.198333
          ],
          [
            -22.09419,
            -1.378252
          ],
          [
            -15.924498,
            -1.373902
          ],
          [
            -11.444032,
            -0.997103
          ],
          [
            -7.998393,
            -0.928455
          ],
          [
            -5.805713,
            -1.198239
          ],
          [
            -0.480633,
            -1.435009
          ],
          [
            29.590404,
            -1.468239
          ],
          [
            30.036421,
            -1.373902
          ],
          [
            30.21384,
            -1.060659
          ],
          [
            30.139423,
            0.81878
          ],
          [
            29.590404,
            1.331037
          ],
          [
            28.963925,
            1.4493
          ],
          [
            23.907554,
            1.445261
          ],
          [
            24.578566,
            1.358461
          ],
          [
            24.969708,
            1.132018
          ],
          [
            23.202753,
            0.896077
          ],
          [
            4.844446,
            0.74603
          ],
          [
            -6.432193,
            0.903129
          ]
        ],
        [
          [
            28.0058,
            -0.747421
          ],
          [
            6.65175,
            -0.747421
          ],
          [
            16.937955,
            -0.883416
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            18.817394,
            1.458613
          ],
          [
            16.26565,
            1.445261
          ],
          [
            22.403177,
            1.445261
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            12.988686,
            1.463639
          ],
          [
            11.082316,
            1.445261
          ],
          [
            15.578009,
            1.445261
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            -6.432193,
            -1.441396
          ],
          [
            29.903645,
            -1.413214
          ],
          [
            30.19877,
            -1.060659
          ],
          [
            30.19347,
            0.81878
          ],
          [
            29.903645,
            1.251848
          ],
          [
            28.024205,
            1.32999
          ],
          [
            24.223721,
            0.972714
          ],
          [
            16.16269,
            0.815295
          ],
          [
            4.217967,
            0.761365
          ],
          [
            -6.432193,
            0.95656
          ],
          [
            -7.058673,
            0.583884
          ],
          [
            -9.292956,
            0.706039
          ],
          [
            -27.106031,
            0.638587
          ],
          [
            -28.045751,
            0.923912
          ],
          [
            -29.611952,
            0.9237
          ],
          [
            -30.057731,
            0.81878
          ],
          [
            -30.215433,
            0.505536
          ],
          [
            -30.088188,
            -1.060659
          ],
          [
            -29.611952,
            -1.284328
          ],
          [
            -20.703182,
            -1.373902
          ],
          [
            -20.686728,
            -1.060659
          ],
          [
            -19.943115,
            -0.924845
          ],
          [
            -15.557756,
            -0.831041
          ],
          [
            -8.311633,
            -0.928021
          ],
          [
            -7.537537,
            -1.060659
          ],
          [
            -7.125355,
            -1.373902
          ]
        ],
        [
          [
            -0.480633,
            -0.753154
          ],
          [
            9.501443,
            -0.946101
          ],
          [
            17.262459,
            -0.747421
          ],
          [
            -3.459731,
            -0.747421
          ],
          [
            -2.401676,
            -0.895353
          ]
        ],
        [
          [
            23.910481,
            -1.035664
          ],
          [
            23.325605,
            -1.148815
          ],
          [
            22.045897,
            -1.060659
          ],
          [
            22.970761,
            -0.96104
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            -19.707558,
            -1.373902
          ],
          [
            -18.376916,
            -1.320505
          ],
          [
            -17.587041,
            -1.373902
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 34.848484848484844,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            -2.798083,
            0.81865
          ],
          [
            -6.432193,
            1.013426
          ],
          [
            -7.058673,
            0.649415
          ],
          [
            -27.106031,
            0.629986
          ],
          [
            -28.045751,
            0.91554
          ],
          [
            -29.611952,
            0.910007
          ],
          [
            -30.045229,
            0.81878
          ],
          [
            -30.217198,
            0.505536
          ],
          [
            -30.22027,
            -0.434183
          ],
          [
            -30.150952,
            -1.060659
          ],
          [
            -29.92519,
            -1.277108
          ],
          [
            -23.191511,
            -1.409612
          ],
          [
            -7.371913,
            -1.427556
          ],
          [
            -6.601271,
            -1.373902
          ],
          [
            -6.664523,
            -1.060659
          ],
          [
            -5.963313,
            -0.862649
          ],
          [
            -1.308702,
            -1.060659
          ],
          [
            -2.360073,
            -1.3057
          ],
          [
            -4.127251,
            -1.373902
          ],
          [
            -3.768673,
            -1.388281
          ],
          [
            28.024205,
            -1.484172
          ],
          [
            29.903645,
            -1.389985
          ],
          [
            30.205825,
            -1.060659
          ],
          [
            30.228493,
            -0.747421
          ],
          [
            30.172891,
            0.81878
          ],
          [
            29.903645,
            1.096038
          ],
          [
            28.963925,
            1.286988
          ],
          [
            25.205045,
            1.268675
          ],
          [
            23.012365,
            0.982206
          ],
          [
            17.529686,
            0.824015
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0009670850000000064,
    0.001317714999999997,
    -0.487280375
  ],
  "construction_scale": 127.03276722577978,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
