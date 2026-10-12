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
      "start": -1.6842969551171951,
      "length": 0.2042245785590768,
      "loops": [
        [
          [
            8.288448,
            -0.268539
          ],
          [
            9.177673,
            0.788422
          ],
          [
            8.983493,
            0.797856
          ],
          [
            8.120715,
            0.037174
          ],
          [
            7.257934,
            -0.326228
          ],
          [
            6.992259,
            -0.268539
          ],
          [
            7.257934,
            -0.191824
          ],
          [
            7.78388,
            0.594242
          ],
          [
            8.675003,
            2.319798
          ],
          [
            8.983493,
            2.684168
          ],
          [
            9.868136,
            3.204443
          ],
          [
            10.174717,
            2.648243
          ],
          [
            11.571832,
            3.108661
          ],
          [
            12.434612,
            2.892046
          ],
          [
            13.216164,
            3.101352
          ],
          [
            13.428788,
            2.319798
          ],
          [
            14.16017,
            1.605456
          ],
          [
            14.644256,
            2.319798
          ],
          [
            14.615413,
            3.182579
          ],
          [
            15.022951,
            3.398237
          ],
          [
            17.611288,
            2.980373
          ],
          [
            20.621208,
            3.604161
          ],
          [
            21.149319,
            3.269492
          ],
          [
            22.51773,
            3.775124
          ],
          [
            23.05919,
            3.453804
          ],
          [
            24.204016,
            3.735851
          ],
          [
            25.376304,
            3.421328
          ],
          [
            26.239083,
            3.55131
          ],
          [
            27.101863,
            3.227679
          ],
          [
            27.964645,
            3.532948
          ],
          [
            28.827422,
            3.562394
          ],
          [
            29.690201,
            3.211009
          ],
          [
            30.552982,
            3.635976
          ],
          [
            31.41576,
            3.509818
          ],
          [
            32.278542,
            3.957069
          ],
          [
            33.141319,
            3.91233
          ],
          [
            34.0041,
            3.528718
          ],
          [
            34.866879,
            3.959669
          ],
          [
            37.814439,
            3.541802
          ],
          [
            38.317997,
            3.731594
          ],
          [
            39.180776,
            3.664379
          ],
          [
            39.832935,
            3.834739
          ],
          [
            41.164699,
            3.440943
          ],
          [
            42.297731,
            3.711196
          ],
          [
            43.001809,
            3.552495
          ],
          [
            43.982615,
            3.670521
          ],
          [
            44.198988,
            3.024113
          ],
          [
            45.306367,
            3.268715
          ],
          [
            45.629097,
            2.728663
          ],
          [
            45.818124,
            2.319798
          ],
          [
            45.200259,
            1.43705
          ],
          [
            46.945792,
            2.495064
          ],
          [
            47.117789,
            2.491795
          ],
          [
            47.238038,
            1.749267
          ],
          [
            47.901314,
            1.549764
          ],
          [
            47.231388,
            0.594242
          ],
          [
            47.342763,
            0.128432
          ],
          [
            47.974667,
            -0.102444
          ],
          [
            48.169511,
            -0.770382
          ],
          [
            47.808573,
            -2.274018
          ],
          [
            47.116897,
            -2.856877
          ],
          [
            47.507284,
            -3.158166
          ],
          [
            47.808573,
            -3.072355
          ],
          [
            48.329807,
            -3.198423
          ],
          [
            48.671351,
            -3.867983
          ],
          [
            48.772053,
            4.045361
          ],
          [
            48.671351,
            4.137873
          ],
          [
            3.049464,
            4.150787
          ],
          [
            2.918199,
            4.045361
          ],
          [
            2.944036,
            -3.990047
          ],
          [
            3.459549,
            -4.066927
          ],
          [
            3.806817,
            -4.554762
          ],
          [
            4.669596,
            -4.083161
          ],
          [
            5.292181,
            -3.959854
          ],
          [
            7.143448,
            -3.834145
          ],
          [
            8.120715,
            -4.011381
          ],
          [
            8.726899,
            -3.719659
          ],
          [
            8.529253,
            -3.311119
          ],
          [
            8.591624,
            -1.523188
          ],
          [
            8.120715,
            -1.50165
          ],
          [
            7.257934,
            -2.212134
          ],
          [
            6.955249,
            -2.296782
          ],
          [
            7.052354,
            -1.994095
          ],
          [
            7.859314,
            -1.131321
          ]
        ],
        [
          [
            6.965884,
            1.457023
          ],
          [
            7.483645,
            1.682732
          ],
          [
            7.827866,
            1.457023
          ],
          [
            6.842317,
            1.041406
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.6842969551171951,
      "length": 0.2042245785590768,
      "loops": [
        [
          [
            -48.795922,
            -2.856877
          ],
          [
            -48.798507,
            2.319798
          ],
          [
            -48.58353,
            2.559004
          ],
          [
            -48.551299,
            3.182579
          ],
          [
            -48.02422,
            3.981095
          ],
          [
            -48.822735,
            4.186251
          ],
          [
            -48.918565,
            -2.952708
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.6842969551171951,
      "length": 0.2042245785590768,
      "loops": [
        [
          [
            12.249602,
            -3.719659
          ],
          [
            12.434612,
            -3.597419
          ],
          [
            12.651564,
            -3.719659
          ],
          [
            12.34154,
            -3.812731
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.480139748436323,
      "length": 3.1645040754317226,
      "loops": [
        [
          [
            48.671351,
            -5.139029
          ],
          [
            2.944036,
            -5.088064
          ],
          [
            2.437224,
            -4.58244
          ],
          [
            2.357421,
            4.045361
          ],
          [
            2.667999,
            4.908136
          ],
          [
            2.944036,
            5.111105
          ],
          [
            48.671351,
            5.138336
          ],
          [
            49.422292,
            4.908136
          ],
          [
            49.728185,
            4.045361
          ],
          [
            49.669387,
            -4.58244
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.480139748436323,
      "length": 3.1645040754317226,
      "loops": [
        [
          [
            -48.524859,
            -1.994095
          ],
          [
            -49.287135,
            -2.597059
          ],
          [
            -49.627913,
            -2.249801
          ],
          [
            -49.629049,
            -2.856877
          ],
          [
            -49.748285,
            -2.856877
          ],
          [
            -49.726086,
            4.045361
          ],
          [
            -49.20396,
            4.908136
          ],
          [
            -48.822735,
            5.090825
          ],
          [
            -43.922836,
            4.908136
          ],
          [
            -47.959954,
            4.799105
          ],
          [
            -48.463295,
            4.100644
          ],
          [
            -48.261525,
            4.045361
          ],
          [
            -48.259489,
            3.467396
          ],
          [
            -48.53412,
            3.182579
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.480139748436323,
      "length": 3.1645040754317226,
      "loops": [
        [
          [
            -6.546538,
            -2.137035
          ],
          [
            -6.453774,
            0.594242
          ],
          [
            -6.546538,
            1.495876
          ],
          [
            -6.701759,
            0.594242
          ],
          [
            -6.71411,
            -1.994095
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.845172255,
    -0.422916805,
    0.005796944999999998
  ],
  "construction_scale": 87.47388412518265,
  "expected_solid_count": 3
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
