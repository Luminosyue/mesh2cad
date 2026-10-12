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
      "start": -22.834190478942016,
      "length": 2.7686940317333417,
      "loops": [
        [
          [
            0.691221,
            -48.895668
          ],
          [
            0.848871,
            -49.368762
          ],
          [
            1.11016,
            -49.416682
          ],
          [
            1.325138,
            -49.156956
          ],
          [
            1.572761,
            -46.021486
          ],
          [
            2.191499,
            -33.218308
          ],
          [
            2.161415,
            -30.082837
          ],
          [
            1.894028,
            -29.670182
          ],
          [
            1.632739,
            -30.954464
          ],
          [
            1.222841,
            -36.635314
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -20.066409814827832,
      "length": 2.7686940317333417,
      "loops": [
        [
          [
            1.60768,
            -31.254637
          ],
          [
            0.755857,
            -47.193286
          ],
          [
            0.731986,
            -49.679535
          ],
          [
            1.11016,
            -49.980187
          ],
          [
            1.498564,
            -49.679535
          ],
          [
            1.675424,
            -48.373088
          ],
          [
            2.669798,
            -30.082837
          ],
          [
            2.884252,
            -21.848222
          ],
          [
            2.757203,
            -20.803065
          ],
          [
            2.416607,
            -20.494339
          ],
          [
            2.124312,
            -20.803065
          ],
          [
            1.938964,
            -21.586932
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -20.066409814827832,
      "length": 2.7686940317333417,
      "loops": [
        [
          [
            4.44934,
            20.607288
          ],
          [
            4.245632,
            20.268004
          ],
          [
            3.971474,
            20.868577
          ],
          [
            3.984343,
            21.889856
          ],
          [
            4.245632,
            23.180198
          ],
          [
            4.506922,
            21.757186
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -17.298629150713648,
      "length": 24.910939344646817,
      "loops": [
        [
          [
            5.148161,
            8.58798
          ],
          [
            4.877017,
            5.191219
          ],
          [
            4.506922,
            4.426119
          ],
          [
            3.984343,
            4.372737
          ],
          [
            3.571448,
            4.92993
          ],
          [
            3.478816,
            5.975087
          ],
          [
            4.339816,
            37.591093
          ],
          [
            4.274258,
            46.997509
          ],
          [
            3.984343,
            48.083821
          ],
          [
            3.684789,
            48.565244
          ],
          [
            2.677897,
            48.909317
          ],
          [
            0.045287,
            49.349111
          ],
          [
            -0.140523,
            49.610403
          ],
          [
            0.326293,
            49.865673
          ],
          [
            2.416607,
            49.585103
          ],
          [
            3.984343,
            49.150232
          ],
          [
            4.618059,
            48.565244
          ],
          [
            4.976273,
            47.258796
          ],
          [
            5.373991,
            25.310495
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -17.298629150713648,
      "length": 24.910939344646817,
      "loops": [
        [
          [
            4.362252,
            -9.702271
          ],
          [
            4.416137,
            -2.289914
          ],
          [
            4.245632,
            -1.708362
          ],
          [
            3.723053,
            -1.483291
          ],
          [
            3.461764,
            -1.580906
          ],
          [
            3.200475,
            -2.115163
          ],
          [
            2.854769,
            -3.857649
          ],
          [
            2.729826,
            -5.686674
          ],
          [
            2.750975,
            -13.002775
          ],
          [
            3.185715,
            -15.189347
          ],
          [
            3.461764,
            -15.452521
          ],
          [
            3.723053,
            -15.333402
          ],
          [
            3.984343,
            -14.508741
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -17.298629150713648,
      "length": 24.910939344646817,
      "loops": [
        [
          [
            1.980422,
            -34.16721
          ],
          [
            2.108894,
            -27.112398
          ],
          [
            2.418637,
            -23.765668
          ],
          [
            2.677897,
            -22.715401
          ],
          [
            2.939185,
            -22.389592
          ],
          [
            3.200475,
            -22.357771
          ],
          [
            3.461764,
            -22.703804
          ],
          [
            3.600583,
            -23.454348
          ],
          [
            3.535559,
            -25.805952
          ],
          [
            2.970823,
            -32.95702
          ],
          [
            2.754316,
            -34.16721
          ],
          [
            2.416607,
            -34.64559
          ],
          [
            2.155318,
            -34.563624
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.61139682631401,
      "length": 9.688145692018802,
      "loops": [
        [
          [
            4.497717,
            18.255685
          ],
          [
            3.619278,
            -5.957394
          ],
          [
            3.136318,
            -14.057362
          ],
          [
            3.200475,
            -15.128862
          ],
          [
            3.461764,
            -15.588698
          ],
          [
            3.859493,
            -15.102519
          ],
          [
            4.321579,
            -12.228338
          ],
          [
            5.259296,
            6.758955
          ],
          [
            5.455127,
            20.346
          ],
          [
            5.26139,
            43.426285
          ],
          [
            5.170334,
            46.997509
          ],
          [
            4.996937,
            47.980427
          ],
          [
            3.902756,
            48.826536
          ],
          [
            2.155318,
            49.468151
          ],
          [
            1.788565,
            49.349111
          ],
          [
            1.894028,
            48.959656
          ],
          [
            3.483382,
            48.303956
          ],
          [
            4.277317,
            47.781376
          ],
          [
            4.520987,
            43.426285
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 17.298629150713655,
      "length": 5.536474695847523,
      "loops": [
        [
          [
            4.303376,
            9.633137
          ],
          [
            4.76821,
            10.301581
          ],
          [
            5.029501,
            9.795349
          ],
          [
            5.100513,
            9.110559
          ],
          [
            5.090856,
            2.839616
          ],
          [
            4.654703,
            -6.305511
          ],
          [
            4.506922,
            -6.967826
          ],
          [
            4.141099,
            -7.287277
          ],
          [
            3.867434,
            -7.137911
          ],
          [
            3.723053,
            -6.710741
          ],
          [
            3.665629,
            -4.786307
          ],
          [
            4.057449,
            2.839616
          ],
          [
            4.138453,
            8.58798
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 17.298629150713655,
      "length": 5.536474695847523,
      "loops": [
        [
          [
            4.546582,
            30.586905
          ],
          [
            4.562578,
            29.181303
          ],
          [
            4.76821,
            28.281178
          ],
          [
            5.029501,
            27.980079
          ],
          [
            5.290789,
            28.419443
          ],
          [
            5.456077,
            29.752415
          ],
          [
            5.290789,
            31.014539
          ],
          [
            5.029501,
            31.465608
          ],
          [
            4.76821,
            31.36102
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.534270345,
    0.13685904999999998,
    -0.009210855000000018
  ],
  "construction_scale": 52.98222844132329,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
