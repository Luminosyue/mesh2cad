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
      "start": -49.99999999999999,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            0.407178,
            -1.207607
          ],
          [
            0.255336,
            -1.284194
          ],
          [
            -1.087446,
            -1.207607
          ],
          [
            -0.707116,
            -0.924143
          ],
          [
            -0.225891,
            -1.030353
          ],
          [
            0.255336,
            -0.930653
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -49.99999999999999,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            7.955348,
            -3.200702
          ],
          [
            7.955348,
            -3.100433
          ],
          [
            9.30544,
            -3.132507
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -49.99999999999999,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            9.480498,
            -3.132507
          ],
          [
            10.359027,
            -3.110909
          ],
          [
            10.412445,
            -3.132507
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -49.99999999999999,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            11.853278,
            -3.132507
          ],
          [
            11.323509,
            -3.119601
          ],
          [
            11.29183,
            -3.132507
          ],
          [
            11.324136,
            -3.164658
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939393,
      "length": 51.51715151515152,
      "loops": [
        [
          [
            -4.049889,
            -1.092765
          ],
          [
            -3.594465,
            -0.558811
          ],
          [
            -3.11324,
            -0.290266
          ],
          [
            -2.669822,
            -0.276909
          ],
          [
            -1.18834,
            -0.32153
          ],
          [
            0.255336,
            -0.75847
          ],
          [
            11.804733,
            -0.660233
          ],
          [
            12.330592,
            -1.207607
          ],
          [
            12.352307,
            -2.651284
          ],
          [
            12.133718,
            -3.132507
          ],
          [
            11.804733,
            -3.324079
          ],
          [
            11.323509,
            -3.348571
          ],
          [
            7.954932,
            -3.202721
          ],
          [
            -3.11324,
            -3.324222
          ],
          [
            -3.721843,
            -3.139482
          ],
          [
            -4.22245,
            -2.651284
          ],
          [
            -4.304453,
            -1.688832
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757585,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -11.77529,
            -0.737037
          ],
          [
            -4.07569,
            -0.740087
          ],
          [
            -3.421204,
            -0.24516
          ],
          [
            -2.632015,
            -0.140712
          ],
          [
            -1.18834,
            -0.155388
          ],
          [
            -0.225891,
            -0.65849
          ],
          [
            0.255336,
            -0.707682
          ],
          [
            11.804733,
            -0.668353
          ],
          [
            12.339842,
            -1.207607
          ],
          [
            12.378316,
            -2.651284
          ],
          [
            12.19323,
            -3.132507
          ],
          [
            11.804733,
            -3.355578
          ],
          [
            3.142685,
            -3.253977
          ],
          [
            -3.11324,
            -3.451299
          ],
          [
            -4.556915,
            -2.993166
          ],
          [
            -11.77529,
            -3.188885
          ],
          [
            -12.371141,
            -2.651284
          ],
          [
            -12.347336,
            -1.207607
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666668,
      "length": 18.18381818181817,
      "loops": [
        [
          [
            -11.77529,
            -3.191538
          ],
          [
            -4.556915,
            -2.997097
          ],
          [
            -3.11324,
            -3.455649
          ],
          [
            2.661459,
            -3.275845
          ],
          [
            11.804733,
            -3.358016
          ],
          [
            12.197655,
            -3.132507
          ],
          [
            12.382205,
            -2.651284
          ],
          [
            12.342392,
            -1.207607
          ],
          [
            11.804733,
            -0.656188
          ],
          [
            0.255336,
            -0.689627
          ],
          [
            -0.225891,
            -0.642819
          ],
          [
            -1.18834,
            -0.145869
          ],
          [
            -3.11324,
            -0.135172
          ],
          [
            -4.196248,
            -0.735045
          ],
          [
            -11.77529,
            -0.739637
          ],
          [
            -12.345967,
            -1.207607
          ],
          [
            -12.375722,
            -2.651284
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666668,
      "length": 18.18381818181817,
      "loops": [
        [
          [
            4.659229,
            1.598679
          ],
          [
            4.46869,
            2.160967
          ],
          [
            4.573299,
            2.64219
          ],
          [
            5.067585,
            3.269272
          ],
          [
            5.548808,
            3.465174
          ],
          [
            6.030033,
            3.412308
          ],
          [
            6.48381,
            3.123417
          ],
          [
            6.799439,
            2.64219
          ],
          [
            6.893803,
            2.160967
          ],
          [
            6.774987,
            1.679742
          ],
          [
            6.030033,
            1.065179
          ],
          [
            5.548808,
            1.017467
          ],
          [
            5.067585,
            1.175294
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 34.84848484848485,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            -11.77529,
            -0.739699
          ],
          [
            -4.07569,
            -0.734665
          ],
          [
            -3.379333,
            -0.24516
          ],
          [
            -2.632015,
            -0.154658
          ],
          [
            -1.18834,
            -0.163365
          ],
          [
            -0.225891,
            -0.632949
          ],
          [
            0.255336,
            -0.68298
          ],
          [
            11.804733,
            -0.661328
          ],
          [
            12.349743,
            -1.207607
          ],
          [
            12.385584,
            -2.651284
          ],
          [
            12.205119,
            -3.132507
          ],
          [
            11.804733,
            -3.364994
          ],
          [
            2.847253,
            -3.272688
          ],
          [
            -3.11324,
            -3.447463
          ],
          [
            -4.556915,
            -2.985912
          ],
          [
            -11.77529,
            -3.183221
          ],
          [
            -12.377129,
            -2.651284
          ],
          [
            -12.354676,
            -1.207607
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.21391512999999998,
    0.161435795,
    0.20345347
  ],
  "construction_scale": 195.15815734165864,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
