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
      "start": -14.239072116108705,
      "length": 11.219232442243017,
      "loops": [
        [
          [
            36.431004,
            -0.559916
          ],
          [
            35.530368,
            0.140092
          ],
          [
            34.998514,
            -0.264185
          ],
          [
            35.130291,
            -0.714504
          ],
          [
            35.509003,
            -1.164822
          ],
          [
            35.980687,
            -1.36217
          ],
          [
            36.993676,
            -1.164822
          ],
          [
            37.486983,
            -0.714504
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.020409236750332,
      "length": 9.493284306957113,
      "loops": [
        [
          [
            37.66785,
            0.53762
          ],
          [
            37.796181,
            -0.264185
          ],
          [
            37.702027,
            -0.714504
          ],
          [
            37.340758,
            -1.197753
          ],
          [
            36.881324,
            -1.474758
          ],
          [
            35.980687,
            -1.512798
          ],
          [
            35.530368,
            -1.307492
          ],
          [
            35.034618,
            -0.714504
          ],
          [
            34.882646,
            0.186133
          ],
          [
            35.080049,
            0.702953
          ],
          [
            35.530368,
            1.19034
          ],
          [
            36.079519,
            1.36738
          ],
          [
            36.881324,
            1.323527
          ],
          [
            37.331643,
            1.086601
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.020409236750332,
      "length": 9.493284306957113,
      "loops": [
        [
          [
            45.870146,
            -0.547798
          ],
          [
            45.437378,
            -1.142265
          ],
          [
            44.987058,
            -1.349056
          ],
          [
            44.086423,
            -1.253567
          ],
          [
            43.636104,
            -0.874957
          ],
          [
            43.353969,
            -0.264185
          ],
          [
            43.490061,
            0.636452
          ],
          [
            44.086423,
            1.242693
          ],
          [
            44.987058,
            1.309225
          ],
          [
            45.437378,
            1.117439
          ],
          [
            45.845459,
            0.636452
          ],
          [
            45.974439,
            0.186133
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.472305507322137,
      "length": 2.589491765813497,
      "loops": [
        [
          [
            -30.216146,
            -1.026899
          ],
          [
            33.729094,
            -0.791319
          ],
          [
            34.693394,
            -0.649523
          ],
          [
            35.074953,
            0.636452
          ],
          [
            35.422016,
            1.086771
          ],
          [
            36.431004,
            1.417477
          ],
          [
            37.404958,
            1.086771
          ],
          [
            37.746124,
            0.636452
          ],
          [
            37.928893,
            -0.137037
          ],
          [
            38.232278,
            -0.615939
          ],
          [
            41.257362,
            -0.629056
          ],
          [
            42.735467,
            -0.474215
          ],
          [
            43.185783,
            -0.220833
          ],
          [
            43.636104,
            0.977109
          ],
          [
            44.086423,
            1.314493
          ],
          [
            44.987058,
            1.335297
          ],
          [
            46.394437,
            0.762141
          ],
          [
            46.70546,
            1.213919
          ],
          [
            47.403956,
            3.788683
          ],
          [
            47.688972,
            4.058128
          ],
          [
            48.139288,
            4.213508
          ],
          [
            49.167075,
            4.074974
          ],
          [
            49.570588,
            3.788683
          ],
          [
            49.664437,
            3.338364
          ],
          [
            49.122579,
            1.537089
          ],
          [
            48.027207,
            -0.264185
          ],
          [
            47.238653,
            -1.176539
          ],
          [
            45.887697,
            -1.777824
          ],
          [
            41.834828,
            -2.383361
          ],
          [
            -30.666467,
            -2.771491
          ],
          [
            -32.918059,
            -2.907575
          ],
          [
            -33.818697,
            -2.701603
          ],
          [
            -36.970926,
            -2.695018
          ],
          [
            -37.871563,
            -3.207663
          ],
          [
            -39.672837,
            -2.517641
          ],
          [
            -40.573477,
            -2.684924
          ],
          [
            -42.825067,
            -2.674021
          ],
          [
            -44.626342,
            -2.299622
          ],
          [
            -48.228892,
            -3.35457
          ],
          [
            -48.679211,
            -3.156246
          ],
          [
            -49.287927,
            -2.535408
          ],
          [
            -49.474346,
            -2.065459
          ],
          [
            -49.129527,
            -1.179894
          ],
          [
            -48.679211,
            -0.887241
          ],
          [
            -46.427617,
            -0.450179
          ],
          [
            -42.374751,
            -0.564298
          ],
          [
            -36.970926,
            -1.11
          ],
          [
            -34.269014,
            -1.10142
          ],
          [
            -32.918059,
            -0.916755
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 9.06122771025099,
      "length": 2.5894917658135004,
      "loops": [
        [
          [
            37.373454,
            1.086771
          ],
          [
            37.694896,
            0.636452
          ],
          [
            37.787614,
            0.186133
          ],
          [
            37.635807,
            -0.714504
          ],
          [
            37.331643,
            -1.151667
          ],
          [
            36.881324,
            -1.475362
          ],
          [
            36.431004,
            -1.560457
          ],
          [
            35.530368,
            -1.298581
          ],
          [
            35.039579,
            -0.714504
          ],
          [
            34.926837,
            -0.264185
          ],
          [
            35.080049,
            0.673067
          ],
          [
            35.530368,
            1.179435
          ],
          [
            35.980687,
            1.375441
          ],
          [
            36.881324,
            1.352115
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 9.06122771025099,
      "length": 2.5894917658135004,
      "loops": [
        [
          [
            44.016696,
            -1.164822
          ],
          [
            44.987058,
            -1.339746
          ],
          [
            45.437378,
            -1.169583
          ],
          [
            45.856114,
            -0.714504
          ],
          [
            46.035974,
            0.186133
          ],
          [
            45.887697,
            0.704873
          ],
          [
            45.437378,
            1.180808
          ],
          [
            44.536739,
            1.353321
          ],
          [
            44.086423,
            1.267794
          ],
          [
            43.636104,
            0.899942
          ],
          [
            43.446813,
            -0.264185
          ],
          [
            43.585699,
            -0.714504
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 11.650149913179845,
      "length": 2.5894917658135004,
      "loops": [
        [
          [
            37.667837,
            -0.39904
          ],
          [
            37.640976,
            0.636452
          ],
          [
            37.331643,
            1.072564
          ],
          [
            36.881324,
            1.328632
          ],
          [
            35.980687,
            1.374225
          ],
          [
            35.44706,
            1.086771
          ],
          [
            35.088248,
            0.636452
          ],
          [
            34.988154,
            -0.264185
          ],
          [
            35.120447,
            -0.714504
          ],
          [
            35.504115,
            -1.169512
          ],
          [
            35.980687,
            -1.421736
          ],
          [
            36.881324,
            -1.380597
          ],
          [
            37.331643,
            -1.039319
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.05135484,
    0.13588650500000002,
    0.10405509000000002
  ],
  "construction_scale": 91.31212769876873,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
