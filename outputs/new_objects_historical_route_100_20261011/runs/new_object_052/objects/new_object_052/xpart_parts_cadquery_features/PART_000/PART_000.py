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
            1.694739,
            -16.085735
          ],
          [
            0.868262,
            -14.72684
          ],
          [
            0.426636,
            -12.585852
          ],
          [
            0.504891,
            -11.029118
          ],
          [
            0.691082,
            -10.346371
          ],
          [
            0.861847,
            -9.978147
          ],
          [
            1.678614,
            -9.852442
          ],
          [
            2.495381,
            -10.512219
          ],
          [
            5.655452,
            -13.904874
          ],
          [
            6.561694,
            -15.538412
          ],
          [
            6.495063,
            -16.355176
          ],
          [
            5.883661,
            -17.17194
          ],
          [
            4.945683,
            -17.539919
          ],
          [
            3.530671,
            -17.399984
          ],
          [
            2.884656,
            -17.17194
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            6.579217,
            -14.366586
          ],
          [
            4.30194,
            -11.35013
          ],
          [
            3.475942,
            -9.821035
          ],
          [
            2.907789,
            -8.187497
          ],
          [
            1.459119,
            -0.836595
          ],
          [
            -0.192859,
            10.829327
          ],
          [
            -0.890519,
            14.681989
          ],
          [
            -1.588455,
            15.990088
          ],
          [
            -2.405222,
            16.800296
          ],
          [
            -3.221989,
            17.109138
          ],
          [
            -4.038757,
            17.022748
          ],
          [
            -4.855524,
            16.534956
          ],
          [
            -5.71145,
            15.49875
          ],
          [
            -6.058555,
            14.681989
          ],
          [
            -6.089471,
            13.048448
          ],
          [
            -4.965693,
            6.745488
          ],
          [
            -3.013707,
            -2.470133
          ],
          [
            -2.911863,
            -5.506018
          ],
          [
            -1.464458,
            -10.506305
          ],
          [
            -0.771688,
            -12.300123
          ],
          [
            0.397776,
            -14.494452
          ],
          [
            2.495381,
            -16.965794
          ],
          [
            3.312149,
            -17.300139
          ],
          [
            4.945683,
            -17.456892
          ],
          [
            5.88085,
            -17.17194
          ],
          [
            6.785413,
            -16.355176
          ],
          [
            7.090047,
            -15.538412
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -10.606060606060609,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            6.579217,
            -16.022618
          ],
          [
            5.76245,
            -16.703923
          ],
          [
            4.945683,
            -16.838731
          ],
          [
            3.312149,
            -16.501413
          ],
          [
            2.495381,
            -16.233454
          ],
          [
            1.137294,
            -14.721638
          ],
          [
            -0.851807,
            -11.454573
          ],
          [
            -3.489441,
            -6.553972
          ],
          [
            -4.61782,
            -4.103671
          ],
          [
            -4.828679,
            -3.286893
          ],
          [
            -4.70436,
            -2.470133
          ],
          [
            -4.038757,
            -1.577717
          ],
          [
            -3.221989,
            -1.099011
          ],
          [
            -2.405222,
            -0.98375
          ],
          [
            -1.588455,
            -1.14558
          ],
          [
            0.04508,
            -0.830034
          ],
          [
            0.861847,
            -1.123564
          ],
          [
            1.443612,
            -1.653369
          ],
          [
            1.747088,
            -2.470133
          ],
          [
            2.039162,
            -5.080147
          ],
          [
            2.496437,
            -7.370733
          ],
          [
            4.159574,
            -11.201663
          ],
          [
            6.843082,
            -14.721638
          ],
          [
            6.858299,
            -15.538412
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -10.606060606060609,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            -4.855524,
            17.065263
          ],
          [
            -3.221989,
            17.208431
          ],
          [
            -2.405222,
            16.846363
          ],
          [
            -1.588455,
            15.998559
          ],
          [
            -0.95013,
            14.681989
          ],
          [
            0.858423,
            7.331071
          ],
          [
            0.868332,
            6.51431
          ],
          [
            0.575731,
            5.85726
          ],
          [
            0.04508,
            5.302479
          ],
          [
            -0.771688,
            4.962046
          ],
          [
            -1.588455,
            5.095565
          ],
          [
            -2.405222,
            5.76614
          ],
          [
            -3.083882,
            6.674023
          ],
          [
            -5.122401,
            10.59815
          ],
          [
            -6.007119,
            13.048448
          ],
          [
            -6.351671,
            14.681989
          ],
          [
            -6.140995,
            15.49875
          ],
          [
            -5.672291,
            16.343248
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            1.74936,
            -5.737195
          ],
          [
            -1.556442,
            13.219276
          ],
          [
            -2.08237,
            15.49875
          ],
          [
            -2.494884,
            16.315514
          ],
          [
            -3.230054,
            17.133854
          ],
          [
            -4.038757,
            17.550561
          ],
          [
            -4.855524,
            17.674193
          ],
          [
            -5.672291,
            17.439399
          ],
          [
            -6.720582,
            16.315514
          ],
          [
            -7.037981,
            15.49875
          ],
          [
            -7.093659,
            14.681989
          ],
          [
            -4.341731,
            -0.019831
          ],
          [
            -3.713397,
            -4.920435
          ],
          [
            -0.146397,
            -12.271337
          ],
          [
            1.408297,
            -14.721638
          ],
          [
            2.495381,
            -15.80121
          ],
          [
            3.312149,
            -16.265244
          ],
          [
            4.945683,
            -16.55749
          ],
          [
            5.76245,
            -16.248654
          ],
          [
            6.224458,
            -15.816165
          ],
          [
            6.516558,
            -15.538412
          ],
          [
            6.876959,
            -14.721638
          ],
          [
            6.579217,
            -13.823837
          ],
          [
            4.024797,
            -10.886662
          ],
          [
            2.763147,
            -8.501341
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
            0.335998,
            -13.08811
          ],
          [
            -3.222786,
            -5.737195
          ],
          [
            -3.331003,
            -4.713063
          ],
          [
            -3.204241,
            -3.527017
          ],
          [
            -2.806098,
            -2.470133
          ],
          [
            -2.405222,
            -1.763533
          ],
          [
            -1.588455,
            -1.262112
          ],
          [
            -0.771688,
            -1.5272
          ],
          [
            0.04508,
            -2.36683
          ],
          [
            0.861847,
            -3.88126
          ],
          [
            2.239317,
            -7.370733
          ],
          [
            4.128916,
            -10.971499
          ],
          [
            6.622551,
            -13.904874
          ],
          [
            6.78495,
            -14.721638
          ],
          [
            6.386183,
            -15.538412
          ],
          [
            5.76245,
            -16.114535
          ],
          [
            4.945683,
            -16.47408
          ],
          [
            3.312149,
            -16.157659
          ],
          [
            2.1479,
            -15.538412
          ],
          [
            1.365848,
            -14.721638
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.007164839999999992,
    -0.009999374999999998,
    0.44637334
  ],
  "construction_scale": 331.23555233329614,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
