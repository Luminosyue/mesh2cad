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
      "start": -5.472524762029586,
      "length": 3.9802369097392662,
      "loops": [
        [
          [
            22.610947,
            38.611356
          ],
          [
            -21.895154,
            38.565681
          ],
          [
            -22.509496,
            38.741124
          ],
          [
            -22.764865,
            39.376925
          ],
          [
            -22.674395,
            41.920133
          ],
          [
            -22.356221,
            42.555929
          ],
          [
            -21.895154,
            42.90846
          ],
          [
            -21.259353,
            43.009499
          ],
          [
            -15.53714,
            42.913933
          ],
          [
            -4.607804,
            43.179087
          ],
          [
            20.703543,
            43.132825
          ],
          [
            22.610947,
            43.072839
          ],
          [
            23.355127,
            42.555929
          ],
          [
            23.339916,
            39.376925
          ],
          [
            22.878307,
            38.741124
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.492506753280801,
      "length": 0.6635552357819452,
      "loops": [
        [
          [
            -21.424467,
            -48.999476
          ],
          [
            -21.298771,
            29.839905
          ],
          [
            -21.446288,
            37.469521
          ],
          [
            -21.626516,
            38.105322
          ],
          [
            -22.927602,
            38.741124
          ],
          [
            -23.284596,
            39.376925
          ],
          [
            -23.166754,
            41.961188
          ],
          [
            -22.782572,
            42.555929
          ],
          [
            -21.830359,
            43.23531
          ],
          [
            -21.527313,
            43.827537
          ],
          [
            -21.455606,
            48.913948
          ],
          [
            -21.22312,
            49.549747
          ],
          [
            -17.444545,
            49.6877
          ],
          [
            -13.440736,
            49.549747
          ],
          [
            -13.100302,
            48.913948
          ],
          [
            -13.134102,
            44.323171
          ],
          [
            -12.983967,
            43.827537
          ],
          [
            -12.455079,
            43.335016
          ],
          [
            -11.818216,
            43.16825
          ],
          [
            22.610947,
            43.22178
          ],
          [
            23.246748,
            42.932749
          ],
          [
            23.472043,
            42.555929
          ],
          [
            23.494297,
            39.376925
          ],
          [
            23.246748,
            38.858023
          ],
          [
            22.610947,
            38.508245
          ],
          [
            -11.086531,
            38.48778
          ],
          [
            -12.455079,
            38.315426
          ],
          [
            -12.784368,
            38.105322
          ],
          [
            -13.045127,
            36.83372
          ],
          [
            -13.133999,
            31.607242
          ],
          [
            -12.995672,
            -22.295816
          ],
          [
            -13.081483,
            -48.999476
          ],
          [
            -13.629734,
            -49.69176
          ],
          [
            -20.623549,
            -49.72458
          ],
          [
            -21.140942,
            -49.516867
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.8291704184893369,
      "length": 4.975241411926462,
      "loops": [
        [
          [
            -12.586337,
            48.913948
          ],
          [
            -12.54035,
            43.827537
          ],
          [
            -12.358131,
            43.448472
          ],
          [
            -11.72233,
            43.139972
          ],
          [
            22.610947,
            43.218921
          ],
          [
            23.246748,
            42.930596
          ],
          [
            23.461175,
            42.555929
          ],
          [
            23.501446,
            39.376925
          ],
          [
            23.116077,
            38.741124
          ],
          [
            21.975148,
            38.467338
          ],
          [
            -11.086531,
            38.498617
          ],
          [
            -11.72233,
            38.487627
          ],
          [
            -12.434961,
            38.105322
          ],
          [
            -12.570576,
            37.469521
          ],
          [
            -12.612734,
            30.239827
          ],
          [
            -12.609546,
            -48.999476
          ],
          [
            -12.835587,
            -49.635277
          ],
          [
            -13.629734,
            -49.958275
          ],
          [
            -21.259353,
            -49.957412
          ],
          [
            -21.911453,
            -49.635277
          ],
          [
            -22.004701,
            -48.999476
          ],
          [
            -21.843863,
            37.469521
          ],
          [
            -21.897918,
            38.105322
          ],
          [
            -23.166754,
            38.668762
          ],
          [
            -23.500118,
            39.376925
          ],
          [
            -23.413196,
            41.920133
          ],
          [
            -23.166754,
            42.472098
          ],
          [
            -22.530958,
            42.725953
          ],
          [
            -22.010981,
            43.191733
          ],
          [
            -22.004217,
            48.913948
          ],
          [
            -21.923336,
            49.549747
          ],
          [
            -21.259353,
            49.95722
          ],
          [
            -13.629734,
            49.961872
          ],
          [
            -12.754904,
            49.549747
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.145852092446644,
      "length": 0.6635552357819461,
      "loops": [
        [
          [
            -21.592349,
            -36.464257
          ],
          [
            -21.518947,
            37.924514
          ],
          [
            -21.529083,
            38.105322
          ],
          [
            -21.895154,
            38.368615
          ],
          [
            -23.085897,
            38.741124
          ],
          [
            -23.386139,
            39.376925
          ],
          [
            -23.166754,
            42.318162
          ],
          [
            -21.780772,
            43.191733
          ],
          [
            -21.817164,
            48.913948
          ],
          [
            -21.685363,
            49.549747
          ],
          [
            -21.259353,
            49.837649
          ],
          [
            -19.98775,
            49.936899
          ],
          [
            -14.084727,
            49.903183
          ],
          [
            -12.993935,
            49.615354
          ],
          [
            -12.805173,
            48.913948
          ],
          [
            -12.877893,
            43.827537
          ],
          [
            -12.491078,
            43.191733
          ],
          [
            -12.177323,
            43.097489
          ],
          [
            21.975148,
            43.2261
          ],
          [
            22.610947,
            43.200267
          ],
          [
            23.246748,
            42.878254
          ],
          [
            23.433626,
            42.555929
          ],
          [
            23.482909,
            41.920133
          ],
          [
            23.468651,
            39.376925
          ],
          [
            23.246748,
            38.877653
          ],
          [
            22.610947,
            38.546983
          ],
          [
            -11.72233,
            38.538284
          ],
          [
            -12.177323,
            38.492353
          ],
          [
            -12.776276,
            38.105322
          ],
          [
            -12.825695,
            -48.999476
          ],
          [
            -13.072624,
            -49.635277
          ],
          [
            -13.629734,
            -49.869614
          ],
          [
            -20.623549,
            -49.906075
          ],
          [
            -21.585654,
            -49.635277
          ],
          [
            -21.782332,
            -48.999476
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.809188427238109,
      "length": 0.6635552357819443,
      "loops": [
        [
          [
            -12.195715,
            39.376925
          ],
          [
            -20.623549,
            39.122619
          ],
          [
            -22.058592,
            39.376925
          ],
          [
            -21.895154,
            40.731436
          ],
          [
            -21.259353,
            41.100504
          ],
          [
            -19.98775,
            41.227069
          ],
          [
            -16.808741,
            41.074561
          ],
          [
            -12.371381,
            41.271079
          ],
          [
            -11.842353,
            41.164306
          ],
          [
            -11.159068,
            40.648528
          ],
          [
            -10.979906,
            40.012729
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.809188427238109,
      "length": 0.6635552357819443,
      "loops": [
        [
          [
            13.953993,
            40.256993
          ],
          [
            12.691283,
            40.012729
          ],
          [
            14.833409,
            40.012729
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.809188427238109,
      "length": 0.6635552357819443,
      "loops": [
        [
          [
            17.914943,
            40.012729
          ],
          [
            17.524536,
            39.944865
          ],
          [
            16.4888,
            40.012729
          ],
          [
            17.698725,
            40.186917
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.809188427238109,
      "length": 0.6635552357819443,
      "loops": [
        [
          [
            11.576037,
            40.012729
          ],
          [
            10.970986,
            40.012729
          ],
          [
            11.369715,
            40.215921
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.809188427238109,
      "length": 0.6635552357819443,
      "loops": [
        [
          [
            18.796139,
            40.019094
          ],
          [
            19.449816,
            40.012729
          ],
          [
            18.766678,
            40.012729
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.47327507,
    -0.137008145,
    0.007563315000000001
  ],
  "construction_scale": 257.8458162982123,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
