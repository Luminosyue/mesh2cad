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
      "start": -4.485591390321819,
      "length": 1.63130356559082,
      "loops": [
        [
          [
            -44.633115,
            8.528438
          ],
          [
            -44.607517,
            -8.028277
          ],
          [
            -44.960806,
            -12.333754
          ],
          [
            -45.419421,
            -12.595195
          ],
          [
            -49.092289,
            -12.458845
          ],
          [
            -49.359511,
            -10.497316
          ],
          [
            -49.369417,
            -1.809196
          ],
          [
            -49.30966,
            10.197516
          ],
          [
            -49.256817,
            11.539905
          ],
          [
            -49.092289,
            11.821177
          ],
          [
            -45.419421,
            11.94741
          ],
          [
            -44.940137,
            11.539905
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.485591390321819,
      "length": 1.63130356559082,
      "loops": [
        [
          [
            48.651209,
            9.703467
          ],
          [
            48.644179,
            -8.660877
          ],
          [
            48.238749,
            -9.160661
          ],
          [
            46.402316,
            -9.029286
          ],
          [
            46.091705,
            -8.660877
          ],
          [
            45.94744,
            -4.988014
          ],
          [
            46.023593,
            9.703467
          ],
          [
            46.402316,
            11.665454
          ],
          [
            48.238749,
            11.897096
          ],
          [
            48.59,
            11.539905
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.854467248386612,
      "length": 0.5438874709673484,
      "loops": [
        [
          [
            -49.746729,
            11.539905
          ],
          [
            -49.79233,
            -6.824452
          ],
          [
            -49.640848,
            -12.333754
          ],
          [
            -49.092289,
            -12.932943
          ],
          [
            -47.255855,
            -13.143678
          ],
          [
            -45.419421,
            -13.135739
          ],
          [
            -44.029094,
            -12.333754
          ],
          [
            -43.582986,
            -8.912589
          ],
          [
            -42.974156,
            -6.824452
          ],
          [
            -43.116902,
            -3.751621
          ],
          [
            -43.007309,
            -1.315151
          ],
          [
            -43.242616,
            3.759187
          ],
          [
            -42.747973,
            9.703467
          ],
          [
            -43.582986,
            10.865348
          ],
          [
            -43.719641,
            11.539905
          ],
          [
            -45.419421,
            12.985123
          ],
          [
            -47.530065,
            12.906535
          ],
          [
            -49.092289,
            12.658718
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.854467248386612,
      "length": 0.5438874709673484,
      "loops": [
        [
          [
            49.732188,
            11.539905
          ],
          [
            49.728493,
            -8.660877
          ],
          [
            48.238749,
            -10.497316
          ],
          [
            46.402316,
            -10.328744
          ],
          [
            44.99611,
            -8.660877
          ],
          [
            44.853874,
            -7.108112
          ],
          [
            44.875577,
            9.703467
          ],
          [
            45.284209,
            11.539905
          ],
          [
            46.402316,
            12.699305
          ],
          [
            47.921181,
            13.021222
          ],
          [
            48.238749,
            13.058599
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.3107592010748763,
      "length": 0.8157414946232161,
      "loops": [
        [
          [
            -43.799043,
            -12.333754
          ],
          [
            -43.509957,
            -10.497316
          ],
          [
            -42.053601,
            -9.110421
          ],
          [
            -41.74655,
            -9.039001
          ],
          [
            44.565878,
            -9.011873
          ],
          [
            45.05767,
            -9.22147
          ],
          [
            46.164878,
            -10.497316
          ],
          [
            48.238749,
            -10.603786
          ],
          [
            48.610466,
            -10.497316
          ],
          [
            49.968587,
            -8.660877
          ],
          [
            49.990847,
            11.539905
          ],
          [
            48.238749,
            13.338329
          ],
          [
            45.841723,
            12.735137
          ],
          [
            44.565878,
            11.371433
          ],
          [
            41.233035,
            11.214644
          ],
          [
            20.139341,
            10.987019
          ],
          [
            -41.397158,
            10.889841
          ],
          [
            -41.74655,
            10.89452
          ],
          [
            -42.334251,
            11.539905
          ],
          [
            -43.582986,
            12.04401
          ],
          [
            -44.858829,
            13.094713
          ],
          [
            -45.419421,
            13.218746
          ],
          [
            -46.695263,
            13.161759
          ],
          [
            -49.092289,
            12.834585
          ],
          [
            -49.872087,
            11.539905
          ],
          [
            -49.906135,
            -6.824452
          ],
          [
            -49.756852,
            -12.333754
          ],
          [
            -49.092289,
            -13.060642
          ],
          [
            -46.695263,
            -13.28704
          ],
          [
            -45.419421,
            -13.283146
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.495197130107273,
      "length": 5.43725989677297,
      "loops": [
        [
          [
            48.919035,
            -10.308886
          ],
          [
            49.941144,
            -8.660877
          ],
          [
            49.973091,
            11.539905
          ],
          [
            48.238749,
            13.352664
          ],
          [
            46.402316,
            12.979907
          ],
          [
            44.565878,
            12.153205
          ],
          [
            -41.74655,
            11.95674
          ],
          [
            -43.771415,
            12.835318
          ],
          [
            -45.419421,
            13.199944
          ],
          [
            -49.092289,
            12.794795
          ],
          [
            -49.892429,
            11.539905
          ],
          [
            -49.889091,
            -10.497316
          ],
          [
            -49.784463,
            -12.333754
          ],
          [
            -49.092289,
            -13.092719
          ],
          [
            -45.419421,
            -13.323232
          ],
          [
            -43.77656,
            -12.333754
          ],
          [
            -43.582986,
            -11.317141
          ],
          [
            -42.860984,
            -10.292486
          ],
          [
            -41.74655,
            -10.033269
          ],
          [
            -39.910117,
            -9.972367
          ],
          [
            44.565878,
            -9.943779
          ],
          [
            46.402316,
            -10.675293
          ],
          [
            48.238749,
            -10.666378
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 3.9418833430100833,
      "length": 0.5438874709673484,
      "loops": [
        [
          [
            -42.885608,
            10.400846
          ],
          [
            37.220136,
            10.61348
          ],
          [
            44.565878,
            10.766566
          ],
          [
            45.572019,
            11.539905
          ],
          [
            48.238749,
            12.005441
          ],
          [
            48.695746,
            11.539905
          ],
          [
            48.651559,
            -8.660877
          ],
          [
            48.238749,
            -9.487448
          ],
          [
            46.979296,
            -9.920334
          ],
          [
            45.728513,
            -9.823513
          ],
          [
            44.565878,
            -8.965749
          ],
          [
            -41.74655,
            -8.955662
          ],
          [
            -42.432778,
            -9.347106
          ],
          [
            -43.582986,
            -9.424002
          ],
          [
            -44.590223,
            -10.497316
          ],
          [
            -44.820377,
            -11.734709
          ],
          [
            -45.126875,
            -12.333754
          ],
          [
            -45.419421,
            -12.507897
          ],
          [
            -49.092289,
            -12.395006
          ],
          [
            -49.257524,
            -6.824452
          ],
          [
            -49.092289,
            11.568659
          ],
          [
            -45.419421,
            11.832925
          ],
          [
            -43.917733,
            11.539905
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.835579115,
    -0.4306161,
    0.32284878
  ],
  "construction_scale": 186.1890198376953,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
