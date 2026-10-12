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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -30.435812,
            11.484513
          ],
          [
            -29.700357,
            11.324797
          ],
          [
            -29.268147,
            10.63559
          ],
          [
            -28.852999,
            9.007524
          ],
          [
            -29.062999,
            8.632276
          ],
          [
            -29.320476,
            8.518255
          ],
          [
            -29.920863,
            8.82513
          ],
          [
            -30.687541,
            9.779949
          ],
          [
            -30.899715,
            10.809848
          ],
          [
            -30.716946,
            11.324797
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 30.305030303030296,
      "loops": [
        [
          [
            32.988416,
            -10.803843
          ],
          [
            -17.734109,
            -11.483787
          ],
          [
            -18.76401,
            -11.108244
          ],
          [
            -19.27896,
            -10.749834
          ],
          [
            -27.725288,
            -3.608738
          ],
          [
            -28.805525,
            -2.843977
          ],
          [
            -29.835422,
            -3.249732
          ],
          [
            -30.865324,
            -3.386324
          ],
          [
            -31.036128,
            -3.866213
          ],
          [
            -31.002274,
            -7.213385
          ],
          [
            -31.637747,
            -7.674145
          ],
          [
            -32.667645,
            -7.420524
          ],
          [
            -32.984152,
            -7.213385
          ],
          [
            -33.154499,
            -6.698436
          ],
          [
            -33.223446,
            3.858029
          ],
          [
            -33.10251,
            10.294898
          ],
          [
            -32.978983,
            10.809848
          ],
          [
            -32.667645,
            11.216721
          ],
          [
            -32.152698,
            11.344286
          ],
          [
            -28.33652,
            11.388695
          ],
          [
            -27.775624,
            10.991386
          ],
          [
            -27.593928,
            10.294898
          ],
          [
            -27.536171,
            -0.519042
          ],
          [
            -27.358059,
            -1.291465
          ],
          [
            -25.883612,
            -2.836315
          ],
          [
            -23.223214,
            -4.864036
          ],
          [
            -18.249059,
            -9.053249
          ],
          [
            -17.265107,
            -9.622174
          ],
          [
            -12.584614,
            -9.754609
          ],
          [
            32.988416,
            -9.40527
          ],
          [
            33.335547,
            -9.530657
          ],
          [
            33.456949,
            -10.045608
          ],
          [
            33.457034,
            -10.560556
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.63636363636364,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            -18.971232,
            -11.075506
          ],
          [
            -27.596899,
            -3.866213
          ],
          [
            -28.548052,
            -3.18512
          ],
          [
            -29.062999,
            -2.996411
          ],
          [
            -29.577949,
            -3.278749
          ],
          [
            -29.957882,
            -3.866213
          ],
          [
            -30.125681,
            -7.728333
          ],
          [
            -30.607846,
            -8.036184
          ],
          [
            -31.122797,
            -8.054225
          ],
          [
            -32.6346,
            -7.613462
          ],
          [
            -33.223665,
            -7.213385
          ],
          [
            -33.358169,
            -6.440961
          ],
          [
            -33.149358,
            -4.896113
          ],
          [
            -32.925122,
            -4.621516
          ],
          [
            -31.895221,
            -4.406323
          ],
          [
            -31.774077,
            -4.123688
          ],
          [
            -31.65673,
            10.294898
          ],
          [
            -31.588972,
            10.809848
          ],
          [
            -31.122797,
            11.302916
          ],
          [
            -28.290574,
            11.356184
          ],
          [
            -28.033101,
            11.269232
          ],
          [
            -27.670107,
            10.809848
          ],
          [
            -27.51462,
            0.510858
          ],
          [
            -27.241735,
            -1.291465
          ],
          [
            -24.685928,
            -3.733532
          ],
          [
            -17.476635,
            -9.585557
          ],
          [
            -15.674314,
            -9.815416
          ],
          [
            32.988416,
            -9.390631
          ],
          [
            33.268449,
            -9.530657
          ],
          [
            33.39212,
            -10.560556
          ],
          [
            32.988416,
            -10.828297
          ],
          [
            0.064693,
            -11.169977
          ],
          [
            -7.1446,
            -11.326638
          ],
          [
            -16.961685,
            -11.787408
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.5151515151515156,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            32.988416,
            -9.416551
          ],
          [
            -14.129464,
            -9.749185
          ],
          [
            -16.704212,
            -9.736368
          ],
          [
            -17.476635,
            -9.528207
          ],
          [
            -17.991586,
            -9.253052
          ],
          [
            -25.200879,
            -3.321537
          ],
          [
            -27.478902,
            -1.03399
          ],
          [
            -27.688895,
            2.313181
          ],
          [
            -27.862517,
            11.067323
          ],
          [
            -28.290574,
            11.494972
          ],
          [
            -28.805525,
            11.60359
          ],
          [
            -32.667645,
            11.530516
          ],
          [
            -33.154482,
            11.067323
          ],
          [
            -33.321209,
            6.261347
          ],
          [
            -33.309103,
            -5.92601
          ],
          [
            -33.164448,
            -6.95591
          ],
          [
            -32.667645,
            -7.295928
          ],
          [
            -31.895221,
            -7.343705
          ],
          [
            -31.386072,
            -6.95591
          ],
          [
            -31.494849,
            -2.836315
          ],
          [
            -31.38027,
            -2.522783
          ],
          [
            -31.122797,
            -2.461783
          ],
          [
            -29.062999,
            -2.635304
          ],
          [
            -28.805525,
            -2.778073
          ],
          [
            -19.464634,
            -10.532427
          ],
          [
            -18.506532,
            -11.178136
          ],
          [
            -17.219162,
            -11.537857
          ],
          [
            -8.465019,
            -11.183991
          ],
          [
            32.988416,
            -10.821543
          ],
          [
            33.435078,
            -10.560556
          ],
          [
            33.352086,
            -9.788132
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
            -31.469028,
            -6.698436
          ],
          [
            -31.512181,
            -2.836315
          ],
          [
            -31.38027,
            -2.095246
          ],
          [
            -31.122797,
            -1.578814
          ],
          [
            -30.865324,
            -1.470697
          ],
          [
            -27.775624,
            -3.212681
          ],
          [
            -21.081282,
            -9.052095
          ],
          [
            -18.76401,
            -10.891893
          ],
          [
            -17.219162,
            -11.378329
          ],
          [
            -15.592927,
            -11.075506
          ],
          [
            -15.345212,
            -10.818031
          ],
          [
            -18.002252,
            -9.292914
          ],
          [
            -27.534339,
            -1.03399
          ],
          [
            -27.747128,
            1.329832
          ],
          [
            -27.845335,
            10.809848
          ],
          [
            -28.05012,
            11.324797
          ],
          [
            -28.805525,
            11.671789
          ],
          [
            -32.410172,
            11.661655
          ],
          [
            -32.925122,
            11.524577
          ],
          [
            -33.212014,
            11.067323
          ],
          [
            -33.407156,
            -5.411062
          ],
          [
            -33.383425,
            -6.440961
          ],
          [
            -33.198905,
            -6.95591
          ],
          [
            -32.410172,
            -7.320017
          ],
          [
            -31.637747,
            -7.068578
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
            14.192759,
            -10.749663
          ],
          [
            33.245892,
            -10.755551
          ],
          [
            33.451962,
            -10.560556
          ],
          [
            33.431951,
            -9.788132
          ],
          [
            33.330138,
            -9.530657
          ],
          [
            32.988416,
            -9.396731
          ],
          [
            16.047451,
            -9.473294
          ],
          [
            11.205437,
            -9.788132
          ],
          [
            12.527767,
            -10.560556
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.008092710000000003,
    -0.35075265999999994,
    -0.231708735
  ],
  "construction_scale": 52.20874199465086,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
