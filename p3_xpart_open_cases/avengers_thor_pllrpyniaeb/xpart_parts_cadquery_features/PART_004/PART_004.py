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
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -22.086663309325402,
      "length": 18.7410826380812,
      "loops": [
        [
          [
            -46.343576,
            20.145822
          ],
          [
            -46.893605,
            20.379403
          ],
          [
            -47.140609,
            20.698092
          ],
          [
            -47.264999,
            21.133924
          ],
          [
            -47.111369,
            21.874929
          ],
          [
            -46.646604,
            22.360325
          ],
          [
            -46.152599,
            22.553977
          ],
          [
            -45.411594,
            22.580354
          ],
          [
            -44.917592,
            22.407865
          ],
          [
            -44.63644,
            22.121932
          ],
          [
            -44.475447,
            21.627929
          ],
          [
            -44.670588,
            20.606342
          ],
          [
            -45.29342,
            20.145916
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.086663309325402,
      "length": 18.7410826380812,
      "loops": [
        [
          [
            -47.098842,
            -19.867794
          ],
          [
            -46.399603,
            -20.529437
          ],
          [
            -45.382554,
            -20.609407
          ],
          [
            -44.959575,
            -20.362407
          ],
          [
            -44.647171,
            -19.868402
          ],
          [
            -44.661869,
            -18.880394
          ],
          [
            -44.917592,
            -18.508363
          ],
          [
            -45.411594,
            -18.260577
          ],
          [
            -46.618637,
            -18.38639
          ],
          [
            -47.0894,
            -18.880394
          ],
          [
            -47.194713,
            -19.374399
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.346464137776575,
      "length": 17.402496982970572,
      "loops": [
        [
          [
            -49.420747,
            22.121932
          ],
          [
            -49.274065,
            21.518039
          ],
          [
            -48.869621,
            21.114759
          ],
          [
            -47.63461,
            20.971844
          ],
          [
            -46.399603,
            21.083448
          ],
          [
            -45.968689,
            21.380926
          ],
          [
            -45.790638,
            21.874929
          ],
          [
            -45.896599,
            23.401116
          ],
          [
            -46.152599,
            23.774828
          ],
          [
            -46.646604,
            23.958348
          ],
          [
            -48.62262,
            24.070222
          ],
          [
            -49.285351,
            23.494054
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.346464137776575,
      "length": 17.402496982970572,
      "loops": [
        [
          [
            -49.144276,
            -20.115404
          ],
          [
            -48.732223,
            -19.621401
          ],
          [
            -48.128615,
            -19.432637
          ],
          [
            -46.047305,
            -19.621401
          ],
          [
            -45.766983,
            -19.868402
          ],
          [
            -45.585306,
            -20.362407
          ],
          [
            -45.658598,
            -21.976832
          ],
          [
            -45.905598,
            -22.26
          ],
          [
            -46.399603,
            -22.425325
          ],
          [
            -48.128615,
            -22.510202
          ],
          [
            -48.62262,
            -22.387443
          ],
          [
            -49.001253,
            -22.09142
          ],
          [
            -49.165715,
            -21.734528
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.346464137776575,
      "length": 17.402496982970572,
      "loops": [
        [
          [
            -49.146872,
            -45.062602
          ],
          [
            -48.869621,
            -45.602159
          ],
          [
            -48.37562,
            -45.890415
          ],
          [
            -47.881614,
            -45.729944
          ],
          [
            -47.553375,
            -45.309606
          ],
          [
            -47.406538,
            -42.098579
          ],
          [
            -47.567559,
            -41.604574
          ],
          [
            -47.881614,
            -41.372092
          ],
          [
            -48.62262,
            -41.38968
          ],
          [
            -49.110979,
            -41.851579
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.055149378661625,
      "length": 2.6780547767536347,
      "loops": [
        [
          [
            -45.575683,
            -20.85641
          ],
          [
            -45.764883,
            -20.115404
          ],
          [
            -46.152599,
            -19.774178
          ],
          [
            -47.63461,
            -19.598097
          ],
          [
            -48.62262,
            -19.680725
          ],
          [
            -49.116625,
            -19.999596
          ],
          [
            -49.327455,
            -20.362407
          ],
          [
            -49.281544,
            -22.09142
          ],
          [
            -48.869621,
            -22.63698
          ],
          [
            -48.37562,
            -22.833464
          ],
          [
            -46.152599,
            -22.709123
          ],
          [
            -45.584238,
            -22.09142
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.055149378661625,
      "length": 2.6780547767536347,
      "loops": [
        [
          [
            -49.382317,
            23.850946
          ],
          [
            -48.869621,
            24.271501
          ],
          [
            -48.37562,
            24.367785
          ],
          [
            -46.893605,
            24.267351
          ],
          [
            -46.152599,
            24.056953
          ],
          [
            -45.836118,
            23.356942
          ],
          [
            -45.96175,
            21.627929
          ],
          [
            -46.399603,
            21.288128
          ],
          [
            -47.140609,
            21.174935
          ],
          [
            -48.62262,
            21.163997
          ],
          [
            -49.116625,
            21.329772
          ],
          [
            -49.397863,
            21.627929
          ],
          [
            -49.550461,
            22.121932
          ],
          [
            -49.559116,
            23.10994
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.055149378661625,
      "length": 2.6780547767536347,
      "loops": [
        [
          [
            -47.568496,
            -44.82178
          ],
          [
            -47.443437,
            -41.851579
          ],
          [
            -47.58622,
            -41.357573
          ],
          [
            -48.128615,
            -40.961232
          ],
          [
            -48.869621,
            -41.146265
          ],
          [
            -49.211867,
            -41.851579
          ],
          [
            -49.250189,
            -44.08091
          ],
          [
            -49.112471,
            -44.815601
          ],
          [
            -48.62262,
            -45.361406
          ],
          [
            -47.979971,
            -45.309917
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.732320688882886,
      "length": 2.6780547767536347,
      "loops": [
        [
          [
            -47.955139,
            22.179344
          ],
          [
            -47.513896,
            -42.535172
          ],
          [
            -47.701808,
            -43.276178
          ],
          [
            -48.37562,
            -43.746789
          ],
          [
            -48.885,
            -43.523179
          ],
          [
            -49.215376,
            -43.029175
          ],
          [
            -49.321618,
            -42.535172
          ],
          [
            -49.621539,
            -17.834976
          ],
          [
            -49.861008,
            7.795818
          ],
          [
            -49.910902,
            35.954044
          ],
          [
            -49.808016,
            45.093115
          ],
          [
            -49.402174,
            46.575127
          ],
          [
            -49.710547,
            47.316132
          ],
          [
            -49.363626,
            47.964726
          ],
          [
            -48.128615,
            48.144948
          ],
          [
            -26.392443,
            47.645675
          ],
          [
            4.787216,
            47.344793
          ],
          [
            33.629036,
            47.393244
          ],
          [
            48.943156,
            47.669021
          ],
          [
            49.437161,
            47.578412
          ],
          [
            49.684162,
            47.351764
          ],
          [
            49.806471,
            46.822131
          ],
          [
            49.434303,
            44.976705
          ],
          [
            49.190161,
            44.578709
          ],
          [
            48.449155,
            44.374989
          ],
          [
            -12.255919,
            44.198517
          ],
          [
            -47.63461,
            44.631147
          ],
          [
            -47.758458,
            44.35211
          ],
          [
            -47.81813,
            42.129093
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.409491999104148,
      "length": 2.6780547767536276,
      "loops": [
        [
          [
            48.696156,
            44.298233
          ],
          [
            -0.543251,
            44.120169
          ],
          [
            -23.761436,
            44.244341
          ],
          [
            -46.893605,
            44.638231
          ],
          [
            -47.63461,
            44.533436
          ],
          [
            -47.874179,
            44.105109
          ],
          [
            -47.94532,
            43.117099
          ],
          [
            -48.055129,
            16.440888
          ],
          [
            -47.763192,
            -40.122563
          ],
          [
            -47.911227,
            -41.357573
          ],
          [
            -48.25647,
            -41.851579
          ],
          [
            -48.62262,
            -41.911398
          ],
          [
            -49.050793,
            -41.110573
          ],
          [
            -49.162537,
            -40.193737
          ],
          [
            -49.675861,
            -6.616311
          ],
          [
            -49.921717,
            40.314063
          ],
          [
            -49.867708,
            46.328126
          ],
          [
            -49.607786,
            47.81867
          ],
          [
            -49.116625,
            48.086002
          ],
          [
            -48.128615,
            48.110098
          ],
          [
            3.902785,
            47.476756
          ],
          [
            48.943156,
            47.765315
          ],
          [
            49.684162,
            47.547035
          ],
          [
            49.930494,
            46.822131
          ],
          [
            49.581906,
            46.081121
          ],
          [
            49.467965,
            44.846114
          ],
          [
            49.190161,
            44.450962
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0007341050000000404,
    0.03175106,
    0.03137403999999999
  ],
  "construction_scale": 50.08515151907789,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
