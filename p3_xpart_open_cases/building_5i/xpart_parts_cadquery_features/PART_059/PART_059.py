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
      "start": -41.38254883484828,
      "length": 7.5257550901076256,
      "loops": [
        [
          [
            0.758923,
            -34.035745
          ],
          [
            0.771654,
            35.525257
          ],
          [
            0.904518,
            41.189458
          ],
          [
            1.124229,
            42.799707
          ],
          [
            1.324693,
            42.139345
          ],
          [
            1.439326,
            39.13361
          ],
          [
            1.432001,
            -20.553448
          ],
          [
            1.763144,
            -30.175719
          ],
          [
            1.43916,
            -34.236208
          ],
          [
            1.324693,
            -34.690049
          ],
          [
            1.124229,
            -34.865066
          ],
          [
            0.923531,
            -34.8376
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -33.85844904669405,
      "length": 67.71855339534149,
      "loops": [
        [
          [
            -7.820798,
            41.590257
          ],
          [
            -14.311498,
            48.13289
          ],
          [
            -15.191365,
            48.833832
          ],
          [
            -17.719385,
            49.952603
          ],
          [
            -18.120313,
            49.952592
          ],
          [
            -19.0916,
            49.557734
          ],
          [
            -19.08131,
            48.75588
          ],
          [
            -17.402089,
            45.147526
          ],
          [
            -15.184346,
            41.416725
          ],
          [
            -13.710106,
            39.295458
          ],
          [
            -12.707786,
            38.505322
          ],
          [
            -11.104074,
            38.131265
          ],
          [
            -9.90129,
            37.219659
          ],
          [
            -4.851321,
            32.518298
          ],
          [
            -3.539952,
            30.313194
          ],
          [
            -2.711846,
            28.308553
          ],
          [
            -1.97581,
            25.580069
          ],
          [
            -0.795839,
            22.573109
          ],
          [
            3.041577,
            14.755014
          ],
          [
            4.643509,
            9.264476
          ],
          [
            6.56688,
            3.9744
          ],
          [
            7.912111,
            -0.480248
          ],
          [
            8.500918,
            -3.364755
          ],
          [
            8.669787,
            -4.768003
          ],
          [
            8.570242,
            -6.371715
          ],
          [
            8.949817,
            -8.576819
          ],
          [
            11.054661,
            -14.913655
          ],
          [
            12.004754,
            -17.397234
          ],
          [
            13.739249,
            -21.20605
          ],
          [
            15.958563,
            -27.874261
          ],
          [
            17.161346,
            -29.940918
          ],
          [
            17.562275,
            -30.425428
          ],
          [
            17.963204,
            -30.627104
          ],
          [
            18.312188,
            -30.226929
          ],
          [
            18.283397,
            -29.347062
          ],
          [
            16.637689,
            -23.21069
          ],
          [
            14.605044,
            -17.397234
          ],
          [
            12.581624,
            -12.987026
          ],
          [
            11.630051,
            -9.579139
          ],
          [
            9.624651,
            1.045452
          ],
          [
            8.289473,
            6.057052
          ],
          [
            6.719537,
            10.840499
          ],
          [
            2.695653,
            20.289994
          ],
          [
            1.616714,
            23.497418
          ],
          [
            1.454979,
            24.700201
          ],
          [
            1.830726,
            27.707161
          ],
          [
            1.72611,
            28.509016
          ],
          [
            -1.369246,
            34.12201
          ],
          [
            -3.31256,
            37.128969
          ],
          [
            -5.290619,
            39.307679
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -33.85844904669405,
      "length": 67.71855339534149,
      "loops": [
        [
          [
            1.256614,
            -49.471472
          ],
          [
            1.345044,
            -38.445953
          ],
          [
            1.573385,
            -33.434353
          ],
          [
            1.887893,
            -30.427392
          ],
          [
            1.5244,
            -22.609298
          ],
          [
            1.351291,
            -5.970787
          ],
          [
            1.681813,
            12.070971
          ],
          [
            1.494081,
            14.877467
          ],
          [
            1.324693,
            15.511343
          ],
          [
            1.124229,
            15.663945
          ],
          [
            0.883329,
            14.677002
          ],
          [
            0.780681,
            9.943879
          ],
          [
            0.614151,
            -6.694632
          ],
          [
            0.803701,
            -26.540566
          ],
          [
            0.625787,
            -30.627858
          ],
          [
            -1.487117,
            -34.637136
          ],
          [
            -4.293308,
            -37.841011
          ],
          [
            -5.090155,
            -38.328513
          ],
          [
            -7.495722,
            -38.869476
          ],
          [
            -8.309371,
            -39.247807
          ],
          [
            -4.428346,
            -42.455231
          ],
          [
            -0.902359,
            -46.063582
          ],
          [
            0.312545,
            -47.667294
          ],
          [
            0.808964,
            -49.471472
          ],
          [
            0.923764,
            -49.679735
          ],
          [
            1.124229,
            -49.702142
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -33.85844904669405,
      "length": 67.71855339534149,
      "loops": [
        [
          [
            1.638397,
            46.350313
          ],
          [
            1.254481,
            49.034355
          ],
          [
            1.124229,
            49.299583
          ],
          [
            0.923764,
            49.319492
          ],
          [
            0.751924,
            48.956343
          ],
          [
            0.717959,
            47.553096
          ],
          [
            0.883363,
            39.13361
          ],
          [
            0.935193,
            38.409763
          ],
          [
            1.324693,
            37.64553
          ],
          [
            1.64747,
            38.933144
          ],
          [
            1.744079,
            40.135927
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 33.85844904669405,
      "length": 7.5257550901076256,
      "loops": [
        [
          [
            0.728089,
            24.700201
          ],
          [
            0.775021,
            -34.318458
          ],
          [
            0.908102,
            -35.716973
          ],
          [
            1.124229,
            -35.892741
          ],
          [
            1.324693,
            -35.265279
          ],
          [
            1.729843,
            -28.540968
          ],
          [
            1.438894,
            -21.606978
          ],
          [
            1.367901,
            36.126648
          ],
          [
            1.324693,
            38.526841
          ],
          [
            1.124229,
            39.294505
          ],
          [
            0.923764,
            37.210028
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 33.85844904669405,
      "length": 7.5257550901076256,
      "loops": [
        [
          [
            0.921603,
            44.853956
          ],
          [
            0.805089,
            47.753559
          ],
          [
            0.923764,
            48.414773
          ],
          [
            1.124229,
            48.453278
          ],
          [
            1.302697,
            47.954022
          ],
          [
            1.365143,
            46.751239
          ],
          [
            1.324693,
            45.127281
          ],
          [
            1.124229,
            44.30009
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0003818049999999573,
    0.43098528,
    0.003870539999999978
  ],
  "construction_scale": 40.6485376627603,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
