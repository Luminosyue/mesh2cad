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
      "start": -4.175133279989619,
      "length": 0.5062437665420622,
      "loops": [
        [
          [
            0.678007,
            48.644573
          ],
          [
            0.690295,
            -48.913217
          ],
          [
            0.354508,
            -49.440556
          ],
          [
            -0.322204,
            -49.625236
          ],
          [
            -7.17762,
            -49.604945
          ],
          [
            -7.704959,
            -49.430787
          ],
          [
            -7.939857,
            -48.913217
          ],
          [
            -7.95471,
            -48.385875
          ],
          [
            -8.003442,
            47.062555
          ],
          [
            -7.882642,
            49.171912
          ],
          [
            -7.17762,
            49.574579
          ],
          [
            -0.322204,
            49.599004
          ],
          [
            0.205133,
            49.458276
          ],
          [
            0.558047,
            49.171912
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.6690565187787563,
      "length": 1.7714356695692184,
      "loops": [
        [
          [
            -8.308137,
            -48.913217
          ],
          [
            -8.290429,
            49.05431
          ],
          [
            -7.825518,
            49.699253
          ],
          [
            -7.17762,
            49.940365
          ],
          [
            -0.322204,
            49.948762
          ],
          [
            0.205133,
            49.847022
          ],
          [
            0.732472,
            49.437901
          ],
          [
            0.94594,
            48.644573
          ],
          [
            0.983216,
            -42.585143
          ],
          [
            0.942049,
            -48.913217
          ],
          [
            0.732472,
            -49.491009
          ],
          [
            -0.295036,
            -49.967898
          ],
          [
            -7.17762,
            -49.941182
          ],
          [
            -7.704959,
            -49.766657
          ],
          [
            -8.082805,
            -49.440556
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.8977878545407374,
      "length": 4.301819475623532,
      "loops": [
        [
          [
            1.787149,
            32.244361
          ],
          [
            9.697241,
            32.287148
          ],
          [
            10.190547,
            32.824391
          ],
          [
            10.24335,
            35.461087
          ],
          [
            9.985088,
            35.988427
          ],
          [
            9.697241,
            36.176185
          ],
          [
            1.787149,
            36.206309
          ],
          [
            1.259814,
            36.301453
          ],
          [
            1.115965,
            36.515768
          ],
          [
            0.963266,
            38.625121
          ],
          [
            0.951625,
            48.644573
          ],
          [
            0.732472,
            49.441719
          ],
          [
            0.205133,
            49.875993
          ],
          [
            -0.322204,
            49.988645
          ],
          [
            -7.17762,
            49.971501
          ],
          [
            -7.862594,
            49.699253
          ],
          [
            -8.303709,
            49.171912
          ],
          [
            -8.360265,
            48.644573
          ],
          [
            -8.358686,
            37.043105
          ],
          [
            -8.524255,
            36.515768
          ],
          [
            -8.759638,
            36.303811
          ],
          [
            -9.980113,
            35.988427
          ],
          [
            -10.243732,
            35.461087
          ],
          [
            -10.321951,
            33.823139
          ],
          [
            -10.248553,
            32.824391
          ],
          [
            -9.953562,
            32.297051
          ],
          [
            -8.759638,
            31.948279
          ],
          [
            -8.510006,
            31.769712
          ],
          [
            -8.327294,
            31.242373
          ],
          [
            -8.332008,
            -48.441805
          ],
          [
            -8.112156,
            -49.440556
          ],
          [
            -7.704959,
            -49.777854
          ],
          [
            -7.17762,
            -49.952691
          ],
          [
            -0.322204,
            -49.98756
          ],
          [
            0.205133,
            -49.834444
          ],
          [
            0.741268,
            -49.440556
          ],
          [
            0.916732,
            -48.913217
          ],
          [
            0.927243,
            -45.277771
          ],
          [
            1.259814,
            -44.321269
          ],
          [
            1.787149,
            -44.066706
          ],
          [
            2.84183,
            -43.973647
          ],
          [
            3.109585,
            -43.639823
          ],
          [
            3.274846,
            -40.475787
          ],
          [
            3.148588,
            -39.948448
          ],
          [
            2.84183,
            -39.668394
          ],
          [
            1.259814,
            -39.560779
          ],
          [
            1.055043,
            -38.893767
          ],
          [
            0.964605,
            -37.311749
          ],
          [
            0.933231,
            4.348062
          ],
          [
            1.397716,
            6.45742
          ],
          [
            1.473374,
            8.039438
          ],
          [
            1.324952,
            9.094118
          ],
          [
            0.941507,
            10.148795
          ],
          [
            0.977392,
            31.242373
          ],
          [
            1.259814,
            32.12176
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.403864615751594,
      "length": 1.2653589083583554,
      "loops": [
        [
          [
            -8.498364,
            32.824391
          ],
          [
            -8.272671,
            49.171912
          ],
          [
            -7.725032,
            49.787309
          ],
          [
            -7.17762,
            49.952084
          ],
          [
            -0.322204,
            49.960909
          ],
          [
            0.442161,
            49.699253
          ],
          [
            0.871969,
            49.171912
          ],
          [
            0.894184,
            -48.913217
          ],
          [
            0.723897,
            -49.440556
          ],
          [
            0.205133,
            -49.822563
          ],
          [
            -0.322204,
            -49.961527
          ],
          [
            -7.17762,
            -49.934604
          ],
          [
            -8.112006,
            -49.440556
          ],
          [
            -8.312968,
            -48.913217
          ],
          [
            -8.33271,
            29.660352
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 3.66905651877875,
      "length": 0.506243766542063,
      "loops": [
        [
          [
            -8.035655,
            48.644573
          ],
          [
            -7.981411,
            -48.913217
          ],
          [
            -7.704959,
            -49.449853
          ],
          [
            -7.17762,
            -49.589283
          ],
          [
            -0.849546,
            -49.589144
          ],
          [
            0.269552,
            -49.440556
          ],
          [
            0.573446,
            -48.913217
          ],
          [
            0.629967,
            -38.36643
          ],
          [
            0.668902,
            48.117231
          ],
          [
            0.544033,
            49.171912
          ],
          [
            0.205133,
            49.477064
          ],
          [
            -0.322204,
            49.638652
          ],
          [
            -7.17762,
            49.612286
          ],
          [
            -7.906358,
            49.171912
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.24315701499999998,
    -0.008002284999999998,
    0.188721715
  ],
  "construction_scale": 213.85962190260426,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
