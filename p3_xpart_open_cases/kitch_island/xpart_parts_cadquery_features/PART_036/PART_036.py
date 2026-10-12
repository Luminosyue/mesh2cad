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
      "start": -11.775285131248266,
      "length": 2.855085588677556,
      "loops": [
        [
          [
            -37.471818,
            -2.576148
          ],
          [
            -37.445431,
            2.91231
          ],
          [
            -36.877023,
            4.042648
          ],
          [
            -35.047539,
            4.24594
          ],
          [
            -33.685862,
            2.91231
          ],
          [
            -33.856887,
            -2.576148
          ],
          [
            -34.878499,
            -4.405618
          ],
          [
            -36.877023,
            -4.531106
          ],
          [
            -37.01957,
            -4.405618
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -8.92067055397596,
      "length": 1.427778300041404,
      "loops": [
        [
          [
            28.984324,
            -2.731386
          ],
          [
            45.449662,
            -2.897371
          ],
          [
            47.279139,
            -2.714549
          ],
          [
            49.204024,
            -0.746661
          ],
          [
            47.279139,
            2.440264
          ],
          [
            43.620176,
            2.293018
          ],
          [
            39.961211,
            2.922677
          ],
          [
            8.860025,
            2.933767
          ],
          [
            7.795337,
            2.91231
          ],
          [
            7.461904,
            2.480948
          ],
          [
            7.030542,
            2.566483
          ],
          [
            4.525178,
            2.236427
          ],
          [
            3.371577,
            2.448058
          ],
          [
            1.542095,
            2.210861
          ],
          [
            -0.813564,
            2.386132
          ],
          [
            -2.11687,
            2.692451
          ],
          [
            -3.946351,
            2.178534
          ],
          [
            -9.434794,
            2.432558
          ],
          [
            -12.373578,
            2.192128
          ],
          [
            -13.093759,
            2.322303
          ],
          [
            -14.92324,
            2.098803
          ],
          [
            -24.07065,
            2.694584
          ],
          [
            -25.580941,
            2.645723
          ],
          [
            -31.388576,
            3.181864
          ],
          [
            -33.218058,
            3.721647
          ],
          [
            -35.047539,
            4.484612
          ],
          [
            -36.877023,
            4.255115
          ],
          [
            -37.534819,
            2.91231
          ],
          [
            -37.565096,
            -2.576148
          ],
          [
            -37.139429,
            -4.405618
          ],
          [
            -36.877023,
            -4.636835
          ],
          [
            -35.047539,
            -4.682469
          ],
          [
            -34.293612,
            -4.405618
          ],
          [
            -33.295951,
            -3.543118
          ],
          [
            -31.388576,
            -2.873356
          ],
          [
            -27.729613,
            -2.678132
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.493363265339806,
      "length": 2.1414319443594807,
      "loops": [
        [
          [
            -21.851795,
            4.155995
          ],
          [
            38.521104,
            4.01753
          ],
          [
            40.350585,
            3.936487
          ],
          [
            43.620176,
            3.479945
          ],
          [
            47.279139,
            3.556959
          ],
          [
            48.002035,
            2.91231
          ],
          [
            49.233851,
            1.259068
          ],
          [
            49.831809,
            -0.746661
          ],
          [
            48.131808,
            -2.576148
          ],
          [
            47.279139,
            -3.909686
          ],
          [
            45.449662,
            -4.227568
          ],
          [
            44.00955,
            -4.238752
          ],
          [
            -29.559095,
            -4.171144
          ],
          [
            -31.388576,
            -4.063524
          ],
          [
            -33.218058,
            -3.342305
          ],
          [
            -34.658166,
            -3.474923
          ],
          [
            -35.595319,
            -2.576148
          ],
          [
            -35.654451,
            -1.601708
          ],
          [
            -36.641096,
            -0.746661
          ],
          [
            -36.202669,
            1.082825
          ],
          [
            -36.054105,
            1.129111
          ],
          [
            -35.397587,
            2.603874
          ],
          [
            -33.555877,
            2.59849
          ],
          [
            -31.388576,
            2.974815
          ],
          [
            -30.999203,
            3.571622
          ],
          [
            -29.559095,
            4.368648
          ],
          [
            -29.169722,
            4.397346
          ],
          [
            -25.90013,
            3.961374
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.352402332385575,
      "length": 15.70085118640294,
      "loops": [
        [
          [
            45.449662,
            -4.298704
          ],
          [
            -30.687724,
            -4.112657
          ],
          [
            -31.388576,
            -4.05934
          ],
          [
            -35.047539,
            -1.946525
          ],
          [
            -36.877023,
            -1.520229
          ],
          [
            -47.853912,
            -1.362754
          ],
          [
            -49.683393,
            -0.974829
          ],
          [
            -49.876008,
            -0.746661
          ],
          [
            -49.683393,
            0.744871
          ],
          [
            -49.443149,
            1.082825
          ],
          [
            -47.853912,
            1.359365
          ],
          [
            -34.346687,
            1.337486
          ],
          [
            -31.388576,
            2.022766
          ],
          [
            -30.50021,
            2.91231
          ],
          [
            -29.559095,
            4.419051
          ],
          [
            -27.729613,
            4.556811
          ],
          [
            -25.90013,
            3.766876
          ],
          [
            -22.241168,
            4.117502
          ],
          [
            -19.710833,
            4.154294
          ],
          [
            39.961211,
            4.165931
          ],
          [
            47.279139,
            4.001515
          ],
          [
            48.443967,
            2.91231
          ],
          [
            49.574798,
            1.082825
          ],
          [
            49.967927,
            -0.746661
          ],
          [
            48.281856,
            -2.576148
          ],
          [
            47.279139,
            -4.039996
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.347977842612115,
      "length": 1.4277783000414004,
      "loops": [
        [
          [
            41.790697,
            3.523606
          ],
          [
            -25.90013,
            3.587585
          ],
          [
            -29.559095,
            4.075071
          ],
          [
            -31.535504,
            2.91231
          ],
          [
            -31.745848,
            1.860584
          ],
          [
            -32.255492,
            1.082825
          ],
          [
            -32.316042,
            0.031099
          ],
          [
            -32.541724,
            -0.746661
          ],
          [
            -32.289023,
            -2.576148
          ],
          [
            -32.105192,
            -2.787473
          ],
          [
            -31.388576,
            -3.382112
          ],
          [
            -29.559095,
            -3.592567
          ],
          [
            45.449662,
            -3.473959
          ],
          [
            47.279139,
            -3.071463
          ],
          [
            48.171731,
            -1.524421
          ],
          [
            48.927124,
            -0.746661
          ],
          [
            48.207954,
            1.860584
          ],
          [
            47.736352,
            2.541783
          ],
          [
            47.664844,
            2.91231
          ],
          [
            47.279139,
            3.312242
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.95271282,
    0.046590179999999995,
    0.23826813500000002
  ],
  "construction_scale": 185.48409280073355,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
