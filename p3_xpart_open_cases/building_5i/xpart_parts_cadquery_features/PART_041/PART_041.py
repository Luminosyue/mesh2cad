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
            -12.277694,
            11.253031
          ],
          [
            -12.310446,
            10.571782
          ],
          [
            -11.846867,
            9.989766
          ],
          [
            -7.295565,
            6.004204
          ],
          [
            -5.050667,
            4.412538
          ],
          [
            -4.844636,
            4.44055
          ],
          [
            -4.621612,
            4.692744
          ],
          [
            -5.45198,
            5.803049
          ],
          [
            -7.950052,
            8.52804
          ],
          [
            -11.1819,
            11.39197
          ],
          [
            -11.863143,
            11.586129
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 15.15351515151515,
      "loops": [
        [
          [
            -14.195202,
            12.615525
          ],
          [
            -13.906886,
            13.244208
          ],
          [
            -13.71756,
            13.289592
          ],
          [
            -13.225641,
            13.299767
          ],
          [
            -12.544392,
            12.769109
          ],
          [
            -5.081914,
            5.746711
          ],
          [
            2.443058,
            -0.91155
          ],
          [
            2.877336,
            -1.690676
          ],
          [
            2.443058,
            -2.343412
          ],
          [
            1.761809,
            -2.336828
          ],
          [
            -10.203063,
            8.52804
          ],
          [
            -13.769581,
            11.934275
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 15.15351515151515,
      "loops": [
        [
          [
            12.661774,
            -12.567014
          ],
          [
            11.980525,
            -13.120102
          ],
          [
            11.114609,
            -12.590642
          ],
          [
            4.046565,
            -5.096917
          ],
          [
            3.510915,
            -4.415668
          ],
          [
            3.414368,
            -3.734419
          ],
          [
            3.805551,
            -3.365029
          ],
          [
            4.4868,
            -3.478689
          ],
          [
            4.77646,
            -3.734419
          ],
          [
            7.120102,
            -6.459411
          ],
          [
            12.406814,
            -11.909393
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.78787878787879,
      "length": 24.24442424242424,
      "loops": [
        [
          [
            12.661774,
            -12.446416
          ],
          [
            13.873631,
            -13.953136
          ],
          [
            13.343019,
            -14.735155
          ],
          [
            12.661774,
            -14.422404
          ],
          [
            11.980525,
            -13.732581
          ],
          [
            -0.375993,
            -0.757882
          ],
          [
            -16.631877,
            14.396908
          ],
          [
            -17.196292,
            15.340516
          ],
          [
            -16.631877,
            15.922593
          ],
          [
            -15.950633,
            15.732449
          ],
          [
            -14.614627,
            14.554163
          ],
          [
            -0.281934,
            1.126777
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 48.48684848484849,
      "loops": [
        [
          [
            12.61056,
            -11.23725
          ],
          [
            17.844293,
            -15.996878
          ],
          [
            18.001287,
            -16.678127
          ],
          [
            17.430509,
            -17.05083
          ],
          [
            16.74926,
            -16.720818
          ],
          [
            14.266433,
            -14.575642
          ],
          [
            1.310752,
            -2.318717
          ],
          [
            -9.138153,
            6.903661
          ],
          [
            -9.359497,
            7.165541
          ],
          [
            -9.397517,
            7.846791
          ],
          [
            -9.138153,
            8.095047
          ],
          [
            -8.456908,
            8.074549
          ],
          [
            -7.775659,
            7.534877
          ],
          [
            3.124307,
            -2.122094
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606069,
      "loops": [
        [
          [
            1.986558,
            -1.009427
          ],
          [
            11.81508,
            -10.176552
          ],
          [
            13.150295,
            -11.716668
          ],
          [
            13.194496,
            -12.442119
          ],
          [
            11.638619,
            -11.655639
          ],
          [
            6.725267,
            -7.285113
          ],
          [
            1.041832,
            -1.690676
          ],
          [
            0.470134,
            -1.009427
          ],
          [
            0.755368,
            -0.653375
          ],
          [
            0.399315,
            -0.865132
          ],
          [
            -0.101352,
            0.172483
          ],
          [
            0.933868,
            -0.182472
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.50273957,
    0.46068353500000003,
    0.436360125
  ],
  "construction_scale": 138.13815025115312,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
