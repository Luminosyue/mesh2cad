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
      "start": -4.097345694488769,
      "length": 0.7451358382802825,
      "loops": [
        [
          [
            29.522627,
            7.601006
          ],
          [
            29.659839,
            -48.868635
          ],
          [
            29.357846,
            -49.417033
          ],
          [
            28.124383,
            -49.4682
          ],
          [
            27.682043,
            -49.393178
          ],
          [
            27.259677,
            -48.94097
          ],
          [
            27.186171,
            -48.220697
          ],
          [
            27.178426,
            6.732856
          ],
          [
            27.273501,
            26.651642
          ],
          [
            27.634373,
            41.5025
          ],
          [
            27.784219,
            45.913532
          ],
          [
            27.878829,
            46.598078
          ],
          [
            28.308763,
            46.96548
          ],
          [
            28.833304,
            45.114166
          ],
          [
            29.319598,
            32.435433
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.3523737500362665,
      "length": 0.49681185679611467,
      "loops": [
        [
          [
            -29.442563,
            13.027366
          ],
          [
            -29.569321,
            -20.889467
          ],
          [
            -29.172611,
            -38.902329
          ],
          [
            -28.909432,
            -40.475958
          ],
          [
            -26.768183,
            -40.528479
          ],
          [
            -25.194556,
            -40.200581
          ],
          [
            -18.268601,
            -40.058327
          ],
          [
            9.949776,
            -39.943424
          ],
          [
            20.194722,
            -40.230053
          ],
          [
            26.210594,
            -40.659839
          ],
          [
            26.490099,
            -41.000499
          ],
          [
            26.711721,
            -42.049585
          ],
          [
            26.879588,
            -49.107316
          ],
          [
            27.030082,
            -49.401769
          ],
          [
            27.784219,
            -49.671004
          ],
          [
            29.357846,
            -49.678974
          ],
          [
            29.88239,
            -49.433105
          ],
          [
            30.055011,
            -48.868635
          ],
          [
            30.029276,
            -17.625686
          ],
          [
            29.737606,
            49.220791
          ],
          [
            29.357846,
            49.507678
          ],
          [
            28.308763,
            49.599509
          ],
          [
            26.140619,
            49.290766
          ],
          [
            -25.194556,
            49.26391
          ],
          [
            -27.81727,
            49.438145
          ],
          [
            -28.866357,
            49.323235
          ],
          [
            -29.075603,
            48.905495
          ],
          [
            -29.162099,
            46.893821
          ],
          [
            -29.20107,
            28.763637
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.8557257870679313,
      "length": 2.4834037086694556,
      "loops": [
        [
          [
            24.112423,
            -49.758302
          ],
          [
            29.357846,
            -49.836611
          ],
          [
            29.88239,
            -49.682506
          ],
          [
            30.14717,
            -49.393178
          ],
          [
            30.252023,
            -48.868635
          ],
          [
            30.24421,
            48.696247
          ],
          [
            30.223293,
            49.220791
          ],
          [
            29.964018,
            49.74533
          ],
          [
            29.357846,
            49.952871
          ],
          [
            28.308763,
            49.969458
          ],
          [
            -27.891789,
            49.952667
          ],
          [
            -29.75805,
            49.74533
          ],
          [
            -30.061279,
            49.220791
          ],
          [
            -29.972376,
            40.82811
          ],
          [
            -30.164413,
            10.330136
          ],
          [
            -30.195678,
            -27.362399
          ],
          [
            -29.996367,
            -40.475958
          ],
          [
            -29.316379,
            -40.968102
          ],
          [
            -28.341819,
            -41.116079
          ],
          [
            15.295193,
            -41.129032
          ],
          [
            16.244286,
            -41.659169
          ],
          [
            23.063336,
            -49.428451
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.37248597222625524,
      "length": 0.4968118567961151,
      "loops": [
        [
          [
            -29.8926,
            48.673401
          ],
          [
            -29.746438,
            -38.902329
          ],
          [
            -29.667127,
            -40.355134
          ],
          [
            -29.390897,
            -40.690559
          ],
          [
            -27.81727,
            -40.913429
          ],
          [
            14.670661,
            -40.892452
          ],
          [
            15.719744,
            -41.435817
          ],
          [
            21.183587,
            -47.788623
          ],
          [
            23.063336,
            -49.672533
          ],
          [
            24.112423,
            -49.946187
          ],
          [
            25.68605,
            -49.992432
          ],
          [
            26.735132,
            -49.614371
          ],
          [
            29.546457,
            -49.393178
          ],
          [
            29.88239,
            -48.960182
          ],
          [
            29.929482,
            -48.344091
          ],
          [
            29.864415,
            41.37063
          ],
          [
            29.816878,
            49.220791
          ],
          [
            29.357846,
            49.640386
          ],
          [
            28.308763,
            49.747887
          ],
          [
            -29.390897,
            49.708958
          ],
          [
            -29.875262,
            49.220791
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.12416199074208034,
      "length": 3.9733475975744623,
      "loops": [
        [
          [
            16.129062,
            -41.671566
          ],
          [
            22.775862,
            -49.393178
          ],
          [
            23.587881,
            -49.806719
          ],
          [
            25.161505,
            -49.918604
          ],
          [
            25.68605,
            -49.793902
          ],
          [
            26.054789,
            -49.393178
          ],
          [
            26.084964,
            -39.951416
          ],
          [
            26.059983,
            -39.426872
          ],
          [
            25.722976,
            -38.902329
          ],
          [
            24.636967,
            -38.728063
          ],
          [
            16.244286,
            -38.725571
          ],
          [
            14.973118,
            -38.902329
          ],
          [
            14.500995,
            -39.426872
          ],
          [
            14.479259,
            -39.951416
          ],
          [
            14.670661,
            -40.33061
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.350068795,
    -0.006992269999999995,
    -0.20073739499999999
  ],
  "construction_scale": 212.7253042833389,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
