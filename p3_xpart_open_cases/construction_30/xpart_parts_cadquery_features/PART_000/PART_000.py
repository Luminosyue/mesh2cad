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
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -8.706555,
            -4.115574
          ],
          [
            -9.237897,
            -2.785113
          ],
          [
            -9.727438,
            -0.302162
          ],
          [
            -9.739245,
            1.332159
          ],
          [
            -9.229007,
            2.966478
          ],
          [
            -8.53606,
            4.600797
          ],
          [
            -7.287133,
            6.235117
          ],
          [
            -6.086813,
            7.394173
          ],
          [
            -4.452485,
            8.48694
          ],
          [
            -2.818166,
            9.086227
          ],
          [
            -1.183847,
            9.265275
          ],
          [
            0.995242,
            9.15425
          ],
          [
            2.325704,
            8.787043
          ],
          [
            4.26388,
            7.841802
          ],
          [
            5.692333,
            6.657955
          ],
          [
            6.628486,
            5.690345
          ],
          [
            7.603316,
            4.056024
          ],
          [
            8.04766,
            2.966478
          ],
          [
            8.300328,
            0.787384
          ],
          [
            8.072976,
            -1.240529
          ],
          [
            7.497802,
            -3.405898
          ],
          [
            5.898198,
            -5.791521
          ],
          [
            4.755408,
            -6.839439
          ],
          [
            3.082223,
            -7.928987
          ],
          [
            2.084791,
            -8.344985
          ],
          [
            -0.094307,
            -8.795463
          ],
          [
            -1.728625,
            -8.806889
          ],
          [
            -3.362945,
            -8.467183
          ],
          [
            -4.997263,
            -7.731668
          ],
          [
            -6.086813,
            -7.0178
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 69.69896969696968,
      "loops": [
        [
          [
            -3.335677,
            8.894917
          ],
          [
            -4.997263,
            8.095482
          ],
          [
            -6.631583,
            6.923132
          ],
          [
            -7.721131,
            5.68884
          ],
          [
            -8.832324,
            4.056024
          ],
          [
            -9.611145,
            1.332159
          ],
          [
            -9.566619,
            -0.776256
          ],
          [
            -9.320763,
            -2.481254
          ],
          [
            -8.631192,
            -4.115574
          ],
          [
            -7.464503,
            -5.749893
          ],
          [
            -6.272938,
            -6.839439
          ],
          [
            -4.452485,
            -8.011011
          ],
          [
            -2.818166,
            -8.612229
          ],
          [
            -1.183847,
            -8.940286
          ],
          [
            2.084791,
            -8.551938
          ],
          [
            5.353429,
            -6.637028
          ],
          [
            7.380276,
            -4.115574
          ],
          [
            8.104798,
            -1.936481
          ],
          [
            8.403804,
            -0.231483
          ],
          [
            8.405996,
            1.332159
          ],
          [
            8.038129,
            2.966478
          ],
          [
            7.333971,
            4.600797
          ],
          [
            6.442977,
            6.003086
          ],
          [
            5.096876,
            7.291212
          ],
          [
            3.719109,
            8.233705
          ],
          [
            0.995242,
            9.22702
          ],
          [
            -1.728625,
            9.247572
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.75757575757575,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -4.656627,
            -7.52329
          ],
          [
            -2.818166,
            -8.554368
          ],
          [
            -1.728625,
            -8.947218
          ],
          [
            -0.491278,
            -9.048095
          ],
          [
            1.264999,
            -8.889589
          ],
          [
            2.940956,
            -8.473759
          ],
          [
            5.353429,
            -7.346683
          ],
          [
            6.987748,
            -6.25545
          ],
          [
            8.202288,
            -4.955132
          ],
          [
            9.022192,
            -3.570801
          ],
          [
            9.510207,
            -2.206239
          ],
          [
            9.723568,
            -0.846935
          ],
          [
            9.730249,
            0.787384
          ],
          [
            9.238508,
            2.966478
          ],
          [
            8.481125,
            4.600797
          ],
          [
            7.823658,
            5.434826
          ],
          [
            6.442977,
            6.716994
          ],
          [
            5.083672,
            7.544704
          ],
          [
            3.449353,
            8.151112
          ],
          [
            2.084791,
            8.322275
          ],
          [
            -0.094307,
            8.242894
          ],
          [
            -1.728625,
            7.801028
          ],
          [
            -4.452485,
            6.456096
          ],
          [
            -5.542034,
            5.55114
          ],
          [
            -6.703956,
            4.275845
          ],
          [
            -7.539254,
            2.966478
          ],
          [
            -8.080509,
            1.332159
          ],
          [
            -8.259879,
            -0.302162
          ],
          [
            -8.133189,
            -1.936481
          ],
          [
            -7.68974,
            -3.570801
          ],
          [
            -7.176352,
            -4.694921
          ],
          [
            -6.034597,
            -6.294666
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 31.818181818181813,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -2.498558,
            -7.384213
          ],
          [
            -3.907715,
            -7.606886
          ],
          [
            -4.997263,
            -7.144401
          ],
          [
            -6.086813,
            -6.259012
          ],
          [
            -7.176352,
            -4.675456
          ],
          [
            -7.817035,
            -3.026027
          ],
          [
            -8.102008,
            -1.391707
          ],
          [
            -7.979548,
            -0.302162
          ],
          [
            -7.401208,
            0.787384
          ],
          [
            -6.086813,
            1.845554
          ],
          [
            4.26388,
            6.702149
          ],
          [
            4.897887,
            6.856963
          ],
          [
            5.898198,
            6.784146
          ],
          [
            6.987748,
            6.210446
          ],
          [
            8.553419,
            4.600797
          ],
          [
            9.290649,
            2.966478
          ],
          [
            9.774922,
            0.242611
          ],
          [
            9.612241,
            -0.810256
          ],
          [
            9.268872,
            -1.355028
          ],
          [
            8.077296,
            -2.25299
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 37.878787878787875,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            -6.994178,
            -4.660347
          ],
          [
            -7.511875,
            -3.026027
          ],
          [
            -7.233735,
            -2.30617
          ],
          [
            -6.136459,
            -1.391707
          ],
          [
            0.450471,
            1.729813
          ],
          [
            6.442977,
            4.335307
          ],
          [
            7.532518,
            4.578105
          ],
          [
            8.077296,
            4.431726
          ],
          [
            8.652849,
            4.056024
          ],
          [
            9.365555,
            2.966478
          ],
          [
            9.562351,
            1.876932
          ],
          [
            9.34325,
            1.332159
          ],
          [
            8.861133,
            0.787384
          ],
          [
            8.089549,
            0.258001
          ],
          [
            -4.452485,
            -5.307749
          ],
          [
            -5.542034,
            -5.553329
          ],
          [
            -6.486489,
            -5.20512
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.91149982,
    0.111231455,
    -0.301422925
  ],
  "construction_scale": 110.46490247810443,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
