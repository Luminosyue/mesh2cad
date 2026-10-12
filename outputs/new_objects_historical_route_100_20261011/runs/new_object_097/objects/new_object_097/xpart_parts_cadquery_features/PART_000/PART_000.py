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
      "start": -13.931513434237347,
      "length": 1.6892255555964417,
      "loops": [
        [
          [
            9.063001,
            2.782371
          ],
          [
            -6.009317,
            3.558793
          ],
          [
            -13.916497,
            3.627734
          ],
          [
            -34.222968,
            4.258975
          ],
          [
            -47.328672,
            4.400223
          ],
          [
            -48.016309,
            4.342557
          ],
          [
            -48.329791,
            4.094496
          ],
          [
            -48.514931,
            3.070821
          ],
          [
            -48.29812,
            2.44385
          ],
          [
            -47.389338,
            1.851481
          ],
          [
            -42.707562,
            1.507697
          ],
          [
            -30.462921,
            1.502338
          ],
          [
            -14.437277,
            1.853014
          ],
          [
            -5.767773,
            1.568565
          ],
          [
            8.724478,
            2.08305
          ],
          [
            11.064158,
            2.44385
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.931513434237347,
      "length": 1.6892255555964417,
      "loops": [
        [
          [
            47.910103,
            0.102113
          ],
          [
            42.822562,
            0.804644
          ],
          [
            38.505554,
            1.112237
          ],
          [
            36.624643,
            1.750339
          ],
          [
            34.904324,
            2.130361
          ],
          [
            36.624643,
            2.466615
          ],
          [
            38.573592,
            2.511888
          ],
          [
            47.59662,
            2.208846
          ],
          [
            47.910103,
            2.047825
          ],
          [
            48.223592,
            1.525592
          ],
          [
            48.212169,
            0.56294
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -12.242845139178275,
      "length": 18.57590850618717,
      "loops": [
        [
          [
            49.957371,
            0.249453
          ],
          [
            49.776081,
            -3.825849
          ],
          [
            49.477529,
            -4.235124
          ],
          [
            49.164045,
            -4.131553
          ],
          [
            48.962585,
            -3.825849
          ],
          [
            48.850558,
            -1.200903
          ],
          [
            48.266861,
            -0.377514
          ],
          [
            47.910103,
            -0.163576
          ],
          [
            15.307664,
            0.38683
          ],
          [
            10.503303,
            0.888156
          ],
          [
            -6.424888,
            0.657611
          ],
          [
            -19.904742,
            1.065684
          ],
          [
            -46.135399,
            1.3957
          ],
          [
            -48.016309,
            1.655557
          ],
          [
            -49.605149,
            2.757333
          ],
          [
            -49.923057,
            3.070821
          ],
          [
            -49.992328,
            3.384304
          ],
          [
            -49.605847,
            4.011276
          ],
          [
            -48.64328,
            4.853058
          ],
          [
            -43.627518,
            5.071364
          ],
          [
            -4.543976,
            4.364057
          ],
          [
            43.20783,
            3.791883
          ],
          [
            47.808019,
            3.434572
          ],
          [
            49.358113,
            3.070821
          ],
          [
            49.540853,
            2.757333
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.332506106471522,
      "length": 3.377893850655514,
      "loops": [
        [
          [
            -46.135399,
            4.830977
          ],
          [
            31.991772,
            3.902512
          ],
          [
            43.904201,
            3.596978
          ],
          [
            49.227698,
            3.070821
          ],
          [
            49.580372,
            2.757333
          ],
          [
            49.66962,
            2.44385
          ],
          [
            49.791785,
            0.876424
          ],
          [
            49.542786,
            0.249453
          ],
          [
            49.164045,
            0.003258
          ],
          [
            47.59662,
            -0.108403
          ],
          [
            44.148284,
            0.096755
          ],
          [
            27.847062,
            0.315311
          ],
          [
            18.129028,
            0.928656
          ],
          [
            9.734336,
            1.216608
          ],
          [
            3.464636,
            1.268489
          ],
          [
            -6.949773,
            0.754893
          ],
          [
            -18.479315,
            1.254841
          ],
          [
            -44.254491,
            1.602179
          ],
          [
            -48.016309,
            1.906294
          ],
          [
            -49.466579,
            2.757333
          ],
          [
            -49.780446,
            3.070821
          ],
          [
            -49.852508,
            3.384304
          ],
          [
            -49.270246,
            4.251395
          ],
          [
            -48.677796,
            4.693326
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.332506106471522,
      "length": 3.377893850655514,
      "loops": [
        [
          [
            49.823094,
            -1.023535
          ],
          [
            49.600872,
            -0.987873
          ],
          [
            49.477529,
            -1.134333
          ],
          [
            49.414911,
            -2.014344
          ],
          [
            49.477529,
            -2.927552
          ],
          [
            49.791013,
            -3.012432
          ],
          [
            49.998608,
            -1.944941
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 9.709842696589666,
      "length": 2.533559703125977,
      "loops": [
        [
          [
            37.032655,
            3.717058
          ],
          [
            -46.040873,
            4.733448
          ],
          [
            -48.645467,
            4.638243
          ],
          [
            -49.164904,
            4.324759
          ],
          [
            -49.681225,
            3.384304
          ],
          [
            -49.270246,
            2.760124
          ],
          [
            -48.329791,
            2.196901
          ],
          [
            -46.448883,
            1.964377
          ],
          [
            -35.163423,
            1.70929
          ],
          [
            -27.012814,
            1.767081
          ],
          [
            -23.156466,
            1.535896
          ],
          [
            -10.711593,
            1.223802
          ],
          [
            -9.457653,
            0.871572
          ],
          [
            -7.890228,
            0.772783
          ],
          [
            -3.093426,
            0.724442
          ],
          [
            4.022202,
            1.257129
          ],
          [
            12.486298,
            1.255426
          ],
          [
            29.195529,
            0.395145
          ],
          [
            47.59662,
            0.04741
          ],
          [
            48.812912,
            0.268123
          ],
          [
            49.477529,
            0.701882
          ],
          [
            49.688844,
            1.189907
          ],
          [
            49.594899,
            2.757333
          ],
          [
            49.385693,
            3.070821
          ],
          [
            48.850558,
            3.252039
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 12.242845139178273,
      "length": 1.6892255555964435,
      "loops": [
        [
          [
            -8.363518,
            4.011276
          ],
          [
            6.843568,
            3.935961
          ],
          [
            13.113269,
            3.719172
          ],
          [
            17.404342,
            3.827432
          ],
          [
            33.392076,
            3.650001
          ],
          [
            47.498903,
            3.364821
          ],
          [
            48.850558,
            3.283534
          ],
          [
            49.298566,
            3.070821
          ],
          [
            49.575892,
            2.44385
          ],
          [
            49.621439,
            1.503395
          ],
          [
            49.376196,
            0.903698
          ],
          [
            48.537074,
            0.312475
          ],
          [
            45.402223,
            0.059182
          ],
          [
            27.847062,
            0.42439
          ],
          [
            26.906609,
            0.625277
          ],
          [
            23.144788,
            0.405514
          ],
          [
            18.129028,
            0.579027
          ],
          [
            9.493933,
            1.192316
          ],
          [
            -0.366587,
            1.06238
          ],
          [
            -3.187952,
            0.647536
          ],
          [
            -8.830683,
            0.587842
          ],
          [
            -9.8778,
            0.876424
          ],
          [
            -10.711593,
            2.289606
          ],
          [
            -11.898055,
            2.511327
          ],
          [
            -16.354323,
            2.498313
          ],
          [
            -22.401,
            2.980358
          ],
          [
            -27.598874,
            2.793591
          ],
          [
            -38.298274,
            3.012929
          ],
          [
            -43.073438,
            3.384304
          ],
          [
            -44.112298,
            3.697788
          ],
          [
            -40.492668,
            3.999628
          ],
          [
            -37.35782,
            4.059726
          ],
          [
            -28.009548,
            4.054298
          ],
          [
            -22.792098,
            3.843199
          ],
          [
            -19.175688,
            4.068983
          ],
          [
            -11.338563,
            3.753975
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.459146235,
    -0.0017566600000000002,
    0.007815155000000018
  ],
  "construction_scale": 127.13213785136034,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
