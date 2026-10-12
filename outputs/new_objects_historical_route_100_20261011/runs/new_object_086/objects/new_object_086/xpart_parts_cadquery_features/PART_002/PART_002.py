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
            9.040439,
            -38.98974
          ],
          [
            9.361075,
            27.384213
          ],
          [
            9.227504,
            37.189456
          ],
          [
            9.051886,
            37.44087
          ],
          [
            8.645307,
            37.516573
          ],
          [
            -10.210929,
            37.494093
          ],
          [
            -10.779211,
            37.69229
          ],
          [
            -10.735302,
            37.943704
          ],
          [
            -10.462346,
            38.064097
          ],
          [
            9.14814,
            38.217214
          ],
          [
            9.650974,
            38.100158
          ],
          [
            9.986852,
            37.69229
          ],
          [
            10.187538,
            34.419269
          ],
          [
            10.241509,
            26.629964
          ],
          [
            10.068317,
            -26.423521
          ],
          [
            9.856562,
            -38.738326
          ],
          [
            9.696869,
            -39.492575
          ],
          [
            9.399557,
            -39.622212
          ],
          [
            9.137947,
            -39.492575
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            9.912324,
            37.94809
          ],
          [
            10.070483,
            37.44087
          ],
          [
            10.275552,
            34.221075
          ],
          [
            10.546918,
            26.378546
          ],
          [
            10.71113,
            2.291179
          ],
          [
            10.398276,
            -30.692996
          ],
          [
            10.130911,
            -38.738326
          ],
          [
            10.039274,
            -39.241156
          ],
          [
            9.650974,
            -39.521403
          ],
          [
            9.399557,
            -39.457415
          ],
          [
            9.24491,
            -38.98974
          ],
          [
            9.611712,
            -28.178832
          ],
          [
            9.834127,
            -3.037183
          ],
          [
            9.814646,
            16.370503
          ],
          [
            9.679485,
            27.935661
          ],
          [
            9.283376,
            37.189456
          ],
          [
            9.14814,
            37.4525
          ],
          [
            8.645307,
            37.609735
          ],
          [
            -10.713762,
            37.696964
          ],
          [
            -11.095151,
            37.943704
          ],
          [
            -11.034436,
            38.19512
          ],
          [
            -10.713762,
            38.350421
          ],
          [
            8.345276,
            38.408639
          ],
          [
            9.399557,
            38.325329
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -31.81818181818182,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            10.511357,
            30.503047
          ],
          [
            10.111015,
            37.291291
          ],
          [
            9.996368,
            37.943704
          ],
          [
            9.650974,
            38.366862
          ],
          [
            8.142474,
            38.579984
          ],
          [
            -10.312765,
            38.579249
          ],
          [
            -10.847015,
            38.446539
          ],
          [
            -10.882324,
            38.19512
          ],
          [
            -10.713762,
            38.035891
          ],
          [
            -8.55285,
            37.877952
          ],
          [
            8.645307,
            37.796457
          ],
          [
            9.14814,
            37.56205
          ],
          [
            9.306553,
            37.189456
          ],
          [
            9.510295,
            35.178123
          ],
          [
            9.706042,
            29.245964
          ],
          [
            10.042772,
            10.539307
          ],
          [
            9.998676,
            -7.71226
          ],
          [
            9.724756,
            -26.065664
          ],
          [
            9.20939,
            -38.98974
          ],
          [
            9.327045,
            -39.285853
          ],
          [
            9.650974,
            -39.405032
          ],
          [
            9.902389,
            -39.305336
          ],
          [
            10.085822,
            -38.98974
          ],
          [
            10.164418,
            -38.133657
          ],
          [
            10.875567,
            -11.333927
          ],
          [
            10.947502,
            13.556306
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.666666666666664,
      "length": 60.608060606060604,
      "loops": [
        [
          [
            11.16416,
            7.270893
          ],
          [
            10.612339,
            27.887045
          ],
          [
            10.15157,
            36.344916
          ],
          [
            9.963412,
            38.19512
          ],
          [
            9.746403,
            38.697954
          ],
          [
            9.399557,
            38.898091
          ],
          [
            8.715057,
            38.928113
          ],
          [
            -10.462346,
            38.833708
          ],
          [
            -10.452064,
            38.446539
          ],
          [
            -8.702431,
            38.238159
          ],
          [
            8.212225,
            38.147758
          ],
          [
            9.14814,
            38.04911
          ],
          [
            9.315551,
            37.69229
          ],
          [
            10.001664,
            22.537549
          ],
          [
            10.33629,
            -0.089935
          ],
          [
            9.914169,
            -28.178832
          ],
          [
            9.648768,
            -32.704329
          ],
          [
            8.911638,
            -38.98974
          ],
          [
            8.990534,
            -39.241156
          ],
          [
            9.399557,
            -39.370208
          ],
          [
            9.737361,
            -38.98974
          ],
          [
            10.300564,
            -34.212827
          ],
          [
            10.681824,
            -27.997165
          ],
          [
            11.118494,
            -12.912177
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
            10.712168,
            31.15546
          ],
          [
            10.413488,
            -38.235492
          ],
          [
            10.299968,
            -38.738326
          ],
          [
            9.902389,
            -38.947854
          ],
          [
            9.650974,
            -38.859605
          ],
          [
            9.481897,
            -38.486906
          ],
          [
            9.652165,
            -33.458577
          ],
          [
            9.750721,
            -18.468568
          ],
          [
            9.933883,
            34.423874
          ],
          [
            9.650974,
            38.48181
          ],
          [
            9.399557,
            38.853821
          ],
          [
            8.740286,
            38.927347
          ],
          [
            -4.176933,
            38.934414
          ],
          [
            -10.462346,
            38.737257
          ],
          [
            -11.216595,
            38.910197
          ],
          [
            -11.10043,
            39.200788
          ],
          [
            -9.959513,
            39.456929
          ],
          [
            -6.942514,
            39.577851
          ],
          [
            9.243119,
            39.616256
          ],
          [
            9.966383,
            39.452203
          ],
          [
            10.322208,
            38.949373
          ],
          [
            10.639059,
            36.088811
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0028889250000000144,
    0.016307955,
    0.005129610000000007
  ],
  "construction_scale": 101.96058894924015,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
