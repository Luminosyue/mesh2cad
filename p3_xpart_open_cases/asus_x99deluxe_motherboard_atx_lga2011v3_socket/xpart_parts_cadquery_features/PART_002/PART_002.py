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
      "length": 15.153515151515156,
      "loops": [
        [
          [
            -9.730559,
            19.098709
          ],
          [
            -10.041275,
            33.832332
          ],
          [
            -9.895096,
            35.580387
          ],
          [
            -9.40666,
            37.504587
          ],
          [
            -8.407771,
            37.650155
          ],
          [
            11.070578,
            37.506479
          ],
          [
            12.069467,
            37.787755
          ],
          [
            12.184502,
            38.077613
          ],
          [
            12.069467,
            38.405466
          ],
          [
            11.819745,
            38.628259
          ],
          [
            11.320301,
            38.727648
          ],
          [
            0.816846,
            38.469202
          ],
          [
            -8.657492,
            38.535943
          ],
          [
            -10.155827,
            38.694971
          ],
          [
            -10.904994,
            38.440389
          ],
          [
            -11.260308,
            37.827888
          ],
          [
            -11.546629,
            35.830108
          ],
          [
            -11.627013,
            33.332886
          ],
          [
            -11.481848,
            18.599263
          ],
          [
            -11.48154,
            -15.113262
          ],
          [
            -11.903358,
            -38.087724
          ],
          [
            -11.790095,
            -39.336337
          ],
          [
            -11.404439,
            -39.629381
          ],
          [
            -10.870857,
            -39.336337
          ],
          [
            -10.691413,
            -37.588278
          ],
          [
            -10.141675,
            -13.599815
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -34.848484848484844,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            -9.74815,
            -8.620479
          ],
          [
            -9.554558,
            6.214872
          ],
          [
            -9.954086,
            22.594822
          ],
          [
            -9.741984,
            38.429063
          ],
          [
            -9.906104,
            38.936114
          ],
          [
            -10.405549,
            39.10186
          ],
          [
            -11.035074,
            38.82678
          ],
          [
            -11.253287,
            38.327334
          ],
          [
            -11.555544,
            31.187113
          ],
          [
            -11.190293,
            0.868972
          ],
          [
            -11.961919,
            -23.00265
          ],
          [
            -11.912969,
            -29.34744
          ],
          [
            -11.585171,
            -37.088836
          ],
          [
            -11.418524,
            -38.836891
          ],
          [
            -10.904994,
            -39.290543
          ],
          [
            -10.302954,
            -39.086615
          ],
          [
            -10.164818,
            -38.587169
          ],
          [
            -10.456985,
            -23.502094
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5151515151515156,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -11.242253,
            -5.873533
          ],
          [
            -11.930243,
            -26.013603
          ],
          [
            -11.79393,
            -33.342997
          ],
          [
            -11.468076,
            -38.337444
          ],
          [
            -11.224259,
            -38.836891
          ],
          [
            -10.655272,
            -39.057123
          ],
          [
            -10.155827,
            -38.848161
          ],
          [
            -9.97781,
            -38.587169
          ],
          [
            -9.877428,
            -37.588278
          ],
          [
            -10.513316,
            -22.105489
          ],
          [
            -10.009544,
            -9.119924
          ],
          [
            -9.927164,
            1.368417
          ],
          [
            -10.420558,
            17.350652
          ],
          [
            -10.361509,
            26.840103
          ],
          [
            -9.805442,
            38.077613
          ],
          [
            -9.926655,
            39.076501
          ],
          [
            -10.405549,
            39.404384
          ],
          [
            -10.906441,
            39.325566
          ],
          [
            -11.244614,
            38.82678
          ],
          [
            -11.927641,
            29.674496
          ],
          [
            -11.882287,
            21.845656
          ],
          [
            -11.380426,
            9.609257
          ],
          [
            -11.195142,
            -0.129917
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -10.372087,
            -7.932687
          ],
          [
            -10.787051,
            17.600373
          ],
          [
            -10.581877,
            29.087606
          ],
          [
            -9.837433,
            38.077613
          ],
          [
            -9.965827,
            39.076501
          ],
          [
            -10.180289,
            39.326225
          ],
          [
            -10.655272,
            39.428311
          ],
          [
            -11.154717,
            39.184697
          ],
          [
            -11.284474,
            38.82678
          ],
          [
            -11.863393,
            32.772066
          ],
          [
            -12.038516,
            27.838993
          ],
          [
            -11.8451,
            20.34732
          ],
          [
            -11.336392,
            10.047327
          ],
          [
            -11.21959,
            1.618139
          ],
          [
            -11.274167,
            -7.62159
          ],
          [
            -11.715293,
            -19.10882
          ],
          [
            -11.839035,
            -30.657427
          ],
          [
            -11.505537,
            -38.087724
          ],
          [
            -11.154717,
            -38.774229
          ],
          [
            -10.655272,
            -38.878494
          ],
          [
            -10.13891,
            -38.587169
          ],
          [
            -9.929632,
            -37.838003
          ],
          [
            -10.600949,
            -22.854656
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666667,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            -11.31961,
            1.292758
          ],
          [
            -11.946431,
            27.838993
          ],
          [
            -11.858856,
            31.834552
          ],
          [
            -11.2692,
            38.82678
          ],
          [
            -10.904994,
            39.325319
          ],
          [
            -10.405549,
            39.393277
          ],
          [
            -9.950816,
            39.076501
          ],
          [
            -9.881929,
            38.327334
          ],
          [
            -10.912317,
            30.010835
          ],
          [
            -11.055481,
            25.016387
          ],
          [
            -10.619578,
            5.038594
          ],
          [
            -10.880409,
            -26.35077
          ],
          [
            -10.827701,
            -33.418657
          ],
          [
            -10.587703,
            -37.838003
          ],
          [
            -10.696698,
            -38.337444
          ],
          [
            -11.154717,
            -38.584465
          ],
          [
            -11.654162,
            -38.415989
          ],
          [
            -11.803134,
            -37.838003
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.008800584999999972,
    -0.011498294999999992,
    -0.002365969999999995
  ],
  "construction_scale": 50.63678209366718,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
