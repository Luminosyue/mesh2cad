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
      "start": -28.10451289585078,
      "length": 6.814339427994813,
      "loops": [
        [
          [
            19.24545,
            4.8623
          ],
          [
            -4.87714,
            1.679946
          ],
          [
            -9.895162,
            0.691184
          ],
          [
            -11.397151,
            0.230244
          ],
          [
            -12.33089,
            -0.230694
          ],
          [
            -13.020215,
            -0.944958
          ],
          [
            -13.254662,
            -1.847954
          ],
          [
            -12.958664,
            -2.535384
          ],
          [
            -12.24929,
            -2.996322
          ],
          [
            -10.254585,
            -3.283281
          ],
          [
            -7.181829,
            -3.238247
          ],
          [
            -1.189636,
            -2.596199
          ],
          [
            20.782078,
            0.248078
          ],
          [
            24.008644,
            0.804033
          ],
          [
            26.313334,
            1.437202
          ],
          [
            27.53951,
            2.073996
          ],
          [
            27.919009,
            2.534936
          ],
          [
            28.205632,
            3.456812
          ],
          [
            27.892966,
            4.378686
          ],
          [
            27.295112,
            4.839626
          ],
          [
            26.159523,
            5.220042
          ],
          [
            24.776709,
            5.337844
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -21.291297648371803,
      "length": 5.111035616125065,
      "loops": [
        [
          [
            -29.206001,
            -6.357733
          ],
          [
            29.386089,
            1.186353
          ],
          [
            30.768903,
            1.295974
          ],
          [
            32.612657,
            1.095776
          ],
          [
            33.534531,
            1.16513
          ],
          [
            34.570255,
            1.61306
          ],
          [
            35.329999,
            2.534936
          ],
          [
            35.597016,
            3.456812
          ],
          [
            35.563715,
            4.839626
          ],
          [
            35.16769,
            5.761502
          ],
          [
            34.456409,
            6.373312
          ],
          [
            33.534531,
            6.636435
          ],
          [
            32.151717,
            6.580632
          ],
          [
            21.550141,
            4.898521
          ],
          [
            12.792318,
            3.799026
          ],
          [
            -28.745065,
            -0.754229
          ],
          [
            -30.588814,
            -1.078073
          ],
          [
            -32.287891,
            -1.613506
          ],
          [
            -33.418247,
            -2.453293
          ],
          [
            -33.659532,
            -2.996322
          ],
          [
            -33.653826,
            -4.583518
          ],
          [
            -33.453761,
            -5.301013
          ],
          [
            -32.970857,
            -5.774115
          ],
          [
            -31.918674,
            -6.180864
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.181386212762572,
      "length": 32.36389660604097,
      "loops": [
        [
          [
            34.917347,
            0.846168
          ],
          [
            32.151717,
            1.107613
          ],
          [
            30.768903,
            0.988879
          ],
          [
            -20.147648,
            -5.320562
          ],
          [
            -41.870965,
            -7.552374
          ],
          [
            -43.253778,
            -7.484764
          ],
          [
            -44.175656,
            -7.135723
          ],
          [
            -44.964447,
            -6.222889
          ],
          [
            -45.134902,
            -5.301013
          ],
          [
            -45.024829,
            -3.918198
          ],
          [
            -44.364004,
            -2.86124
          ],
          [
            -43.253778,
            -2.232248
          ],
          [
            -41.410027,
            -1.890589
          ],
          [
            -26.199069,
            -0.663912
          ],
          [
            -15.597493,
            0.655864
          ],
          [
            13.253256,
            3.552711
          ],
          [
            24.315771,
            4.997609
          ],
          [
            34.456409,
            6.760142
          ],
          [
            35.839223,
            6.756263
          ],
          [
            37.222037,
            6.339003
          ],
          [
            38.36035,
            6.721821
          ],
          [
            39.987665,
            7.018234
          ],
          [
            47.362674,
            7.523722
          ],
          [
            48.74549,
            7.139685
          ],
          [
            49.405769,
            6.22244
          ],
          [
            49.448418,
            5.300564
          ],
          [
            49.206428,
            4.735072
          ],
          [
            48.368279,
            3.91775
          ],
          [
            47.362674,
            3.436848
          ],
          [
            45.518922,
            3.052036
          ],
          [
            42.753294,
            2.835447
          ],
          [
            37.222037,
            2.912459
          ],
          [
            36.440421,
            1.61306
          ],
          [
            35.839223,
            1.132559
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.18138621276257,
      "length": 5.1110356161250685,
      "loops": [
        [
          [
            25.047992,
            -1.333205
          ],
          [
            -34.684302,
            -6.926157
          ],
          [
            -36.799341,
            -6.793465
          ],
          [
            -38.255583,
            -6.222889
          ],
          [
            -38.776101,
            -5.761951
          ],
          [
            -39.021036,
            -5.301013
          ],
          [
            -39.16317,
            -4.379136
          ],
          [
            -39.088299,
            -3.45726
          ],
          [
            -38.518955,
            -2.535384
          ],
          [
            -37.260276,
            -1.911316
          ],
          [
            -35.416527,
            -1.536045
          ],
          [
            -22.238979,
            -0.549535
          ],
          [
            -0.76454,
            1.684442
          ],
          [
            15.557948,
            2.909403
          ],
          [
            24.315771,
            3.962643
          ],
          [
            28.735497,
            4.704637
          ],
          [
            29.657373,
            4.695
          ],
          [
            30.580735,
            4.378686
          ],
          [
            31.142611,
            3.91775
          ],
          [
            31.632488,
            2.995874
          ],
          [
            31.77717,
            1.61306
          ],
          [
            31.572812,
            0.230244
          ],
          [
            30.975221,
            -0.69163
          ],
          [
            29.657373,
            -1.334868
          ],
          [
            28.274559,
            -1.437528
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 21.291297648371803,
      "length": 6.814339427994813,
      "loops": [
        [
          [
            12.792318,
            2.504229
          ],
          [
            -7.577754,
            0.83912
          ],
          [
            -15.223813,
            -0.128997
          ],
          [
            -17.513503,
            -0.69163
          ],
          [
            -19.459032,
            -1.613506
          ],
          [
            -20.214075,
            -2.535384
          ],
          [
            -20.265336,
            -3.45726
          ],
          [
            -19.791859,
            -4.23671
          ],
          [
            -18.609342,
            -4.840075
          ],
          [
            -15.324903,
            -5.141489
          ],
          [
            -10.715523,
            -4.954105
          ],
          [
            6.250387,
            -3.539778
          ],
          [
            15.437965,
            -2.576099
          ],
          [
            19.617592,
            -1.856496
          ],
          [
            22.011081,
            -0.928692
          ],
          [
            22.472019,
            -0.55472
          ],
          [
            22.947735,
            0.230244
          ],
          [
            22.988141,
            1.15212
          ],
          [
            22.760227,
            1.61306
          ],
          [
            22.171533,
            2.073996
          ],
          [
            20.628266,
            2.519231
          ],
          [
            17.401698,
            2.708927
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.00798144499999999,
    -0.213916795,
    -0.12205690500000001
  ],
  "construction_scale": 186.93092967574307,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
