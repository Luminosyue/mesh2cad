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
      "start": -13.979453586720313,
      "length": 1.6950384007762338,
      "loops": [
        [
          [
            48.660482,
            -3.10669
          ],
          [
            47.715958,
            -3.234379
          ],
          [
            11.194318,
            -2.966925
          ],
          [
            -14.307862,
            -2.634854
          ],
          [
            -42.328774,
            -1.99808
          ],
          [
            -47.681083,
            -1.691411
          ],
          [
            -48.242274,
            -1.304576
          ],
          [
            -48.361402,
            -0.794019
          ],
          [
            -47.758176,
            0.20114
          ],
          [
            -47.231494,
            0.515979
          ],
          [
            -45.477194,
            0.694632
          ],
          [
            -13.678179,
            0.132845
          ],
          [
            -0.769667,
            0.223711
          ],
          [
            10.879476,
            -0.030611
          ],
          [
            13.852679,
            -0.288919
          ],
          [
            24.732512,
            -0.598143
          ],
          [
            32.46496,
            -0.567139
          ],
          [
            37.834418,
            -0.235152
          ],
          [
            43.638845,
            -0.100598
          ],
          [
            47.086274,
            -0.333749
          ],
          [
            48.699616,
            -0.743385
          ],
          [
            49.075702,
            -1.058231
          ],
          [
            49.150966,
            -1.512271
          ],
          [
            49.027659,
            -2.705709
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -12.284974364087548,
      "length": 21.181549461053034,
      "loops": [
        [
          [
            48.660482,
            3.167559
          ],
          [
            48.975322,
            3.614175
          ],
          [
            49.290168,
            3.659507
          ],
          [
            49.605007,
            3.535083
          ],
          [
            49.763603,
            3.261475
          ],
          [
            49.721957,
            -0.113706
          ],
          [
            49.870761,
            -1.687915
          ],
          [
            49.605007,
            -2.825579
          ],
          [
            48.975322,
            -3.19122
          ],
          [
            43.937859,
            -3.639502
          ],
          [
            37.099419,
            -3.74265
          ],
          [
            21.898936,
            -3.635885
          ],
          [
            -42.95846,
            -2.863598
          ],
          [
            -48.310769,
            -2.49694
          ],
          [
            -49.570133,
            -1.86724
          ],
          [
            -49.96868,
            -1.37307
          ],
          [
            -49.690799,
            -0.743385
          ],
          [
            -48.625608,
            0.285883
          ],
          [
            -46.333639,
            0.92562
          ],
          [
            -29.961868,
            0.681369
          ],
          [
            -16.108832,
            0.748755
          ],
          [
            11.194318,
            0.349982
          ],
          [
            21.672174,
            0.419149
          ],
          [
            40.78944,
            0.220099
          ],
          [
            48.345643,
            0.359079
          ],
          [
            48.598317,
            0.830819
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 8.896015918822018,
      "length": 1.6950384007762338,
      "loops": [
        [
          [
            48.660482,
            3.003801
          ],
          [
            48.975322,
            3.25363
          ],
          [
            49.290168,
            3.271944
          ],
          [
            49.68218,
            3.043032
          ],
          [
            49.780749,
            2.71987
          ],
          [
            49.912285,
            -1.058231
          ],
          [
            49.655133,
            -2.317595
          ],
          [
            49.290207,
            -2.944668
          ],
          [
            48.062216,
            -3.182919
          ],
          [
            43.308173,
            -3.45552
          ],
          [
            25.047353,
            -3.541941
          ],
          [
            2.410168,
            -3.042117
          ],
          [
            -43.556722,
            -2.616999
          ],
          [
            -48.625608,
            -2.345846
          ],
          [
            -49.459522,
            -1.687915
          ],
          [
            -49.729151,
            -1.058231
          ],
          [
            -49.286705,
            -0.490481
          ],
          [
            -48.625608,
            -0.050788
          ],
          [
            -46.736559,
            0.286333
          ],
          [
            -32.852105,
            0.47281
          ],
          [
            -26.870113,
            0.758073
          ],
          [
            -11.159444,
            0.850434
          ],
          [
            2.063908,
            0.509332
          ],
          [
            29.171715,
            0.491894
          ],
          [
            42.048809,
            0.238623
          ],
          [
            46.141748,
            0.471289
          ],
          [
            48.030797,
            0.314394
          ],
          [
            48.530178,
            0.515979
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.590495141454783,
      "length": 1.6950384007762338,
      "loops": [
        [
          [
            48.660482,
            -3.217665
          ],
          [
            49.290168,
            -2.998927
          ],
          [
            49.533855,
            -2.63244
          ],
          [
            49.868632,
            -1.058231
          ],
          [
            49.766565,
            2.71987
          ],
          [
            49.636506,
            3.05898
          ],
          [
            49.290168,
            3.244164
          ],
          [
            48.658202,
            3.034714
          ],
          [
            48.4774,
            0.830819
          ],
          [
            48.345643,
            0.554322
          ],
          [
            48.030797,
            0.470604
          ],
          [
            45.826908,
            0.531292
          ],
          [
            42.993334,
            0.288881
          ],
          [
            37.32618,
            0.202401
          ],
          [
            22.995151,
            0.478278
          ],
          [
            12.768526,
            0.320379
          ],
          [
            -4.396079,
            0.586472
          ],
          [
            -28.160899,
            0.512791
          ],
          [
            -32.568682,
            0.263337
          ],
          [
            -47.366244,
            0.049669
          ],
          [
            -49.004941,
            -0.374651
          ],
          [
            -49.57085,
            -0.739291
          ],
          [
            -49.765692,
            -1.209918
          ],
          [
            -49.570133,
            -1.719987
          ],
          [
            -48.829271,
            -2.290737
          ],
          [
            -44.847509,
            -2.527519
          ],
          [
            4.419488,
            -2.983069
          ],
          [
            23.939675,
            -3.492506
          ],
          [
            40.474599,
            -3.483916
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 12.284974364087548,
      "length": 1.6950384007762338,
      "loops": [
        [
          [
            47.109132,
            -1.350211
          ],
          [
            46.898032,
            0.20114
          ],
          [
            47.595704,
            1.460504
          ],
          [
            47.541629,
            1.775344
          ],
          [
            47.086274,
            2.153689
          ],
          [
            45.826908,
            2.422324
          ],
          [
            45.075354,
            2.28316
          ],
          [
            43.96562,
            1.775344
          ],
          [
            42.048809,
            0.3741
          ],
          [
            39.715724,
            0.404046
          ],
          [
            38.44604,
            0.20114
          ],
          [
            37.645197,
            -0.113706
          ],
          [
            37.406545,
            -0.428546
          ],
          [
            37.189908,
            -1.37307
          ],
          [
            36.324543,
            -2.002754
          ],
          [
            36.554505,
            -2.317595
          ],
          [
            39.215233,
            -2.715304
          ],
          [
            45.684985,
            -2.774361
          ],
          [
            46.839086,
            -2.63244
          ],
          [
            47.412767,
            -2.317595
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 12.284974364087548,
      "length": 1.6950384007762338,
      "loops": [
        [
          [
            13.713051,
            -1.411916
          ],
          [
            28.29893,
            -1.687915
          ],
          [
            28.965009,
            -1.37307
          ],
          [
            29.096297,
            -0.743385
          ],
          [
            28.894821,
            -0.428546
          ],
          [
            26.421785,
            0.20114
          ],
          [
            24.102828,
            0.51761
          ],
          [
            13.083369,
            0.256517
          ],
          [
            11.824001,
            -0.029998
          ],
          [
            11.430485,
            -0.428546
          ],
          [
            11.54301,
            -0.743385
          ],
          [
            12.138843,
            -1.098917
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.47008115500000003,
    -0.0012359399999999979,
    -0.0038352949999999886
  ],
  "construction_scale": 127.68234593532127,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
