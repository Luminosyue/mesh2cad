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
      "start": -32.43141879700064,
      "length": 51.10535111869228,
      "loops": [
        [
          [
            1.320504,
            31.995578
          ],
          [
            13.931468,
            16.658031
          ],
          [
            23.61976,
            4.145815
          ],
          [
            38.890526,
            -14.017074
          ],
          [
            44.238232,
            -20.61291
          ],
          [
            48.581321,
            -26.651362
          ],
          [
            49.50111,
            -28.143768
          ],
          [
            49.544456,
            -29.084444
          ],
          [
            48.729375,
            -30.212255
          ],
          [
            46.25633,
            -32.103038
          ],
          [
            45.449093,
            -32.10936
          ],
          [
            44.641851,
            -31.407363
          ],
          [
            29.370166,
            -11.919248
          ],
          [
            19.0669,
            0.342502
          ],
          [
            7.508832,
            15.398246
          ],
          [
            0.243675,
            23.740357
          ],
          [
            -0.159945,
            23.988947
          ],
          [
            -30.367855,
            -13.280531
          ],
          [
            -44.558123,
            -31.518374
          ],
          [
            -45.365361,
            -32.1533
          ],
          [
            -46.172602,
            -32.114517
          ],
          [
            -49.285997,
            -29.636497
          ],
          [
            -49.690333,
            -28.951008
          ],
          [
            -49.734803,
            -28.547388
          ],
          [
            -49.448741,
            -27.740147
          ],
          [
            -48.729228,
            -26.742092
          ],
          [
            -40.562946,
            -16.387616
          ],
          [
            -36.255322,
            -11.191736
          ],
          [
            -26.258123,
            0.109617
          ],
          [
            -19.001726,
            8.809155
          ],
          [
            -11.459903,
            18.670279
          ],
          [
            -3.6584,
            28.170577
          ],
          [
            -0.967184,
            32.060176
          ],
          [
            -0.563565,
            32.412066
          ],
          [
            0.243675,
            32.594443
          ],
          [
            0.647295,
            32.487795
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 18.67263506493976,
      "length": 13.760080988812756,
      "loops": [
        [
          [
            -2.475518,
            29.996408
          ],
          [
            -10.956335,
            19.483366
          ],
          [
            -18.437029,
            9.796496
          ],
          [
            -25.587476,
            1.291466
          ],
          [
            -35.732984,
            -10.384498
          ],
          [
            -47.781532,
            -25.474078
          ],
          [
            -49.403799,
            -27.671868
          ],
          [
            -49.805178,
            -28.448558
          ],
          [
            -49.889472,
            -28.951008
          ],
          [
            -49.521096,
            -29.758245
          ],
          [
            -46.576223,
            -32.345172
          ],
          [
            -46.172602,
            -32.497597
          ],
          [
            -45.76898,
            -32.39972
          ],
          [
            -45.054454,
            -31.776346
          ],
          [
            -32.465269,
            -16.054098
          ],
          [
            -21.659491,
            -3.119341
          ],
          [
            -0.933668,
            23.115949
          ],
          [
            -0.563565,
            23.541476
          ],
          [
            -0.159945,
            23.735443
          ],
          [
            11.222928,
            9.777572
          ],
          [
            21.635523,
            -3.833693
          ],
          [
            35.899585,
            -21.703407
          ],
          [
            43.834614,
            -31.374333
          ],
          [
            44.641851,
            -32.205331
          ],
          [
            45.449093,
            -32.538607
          ],
          [
            46.25633,
            -32.171016
          ],
          [
            48.321221,
            -30.565487
          ],
          [
            49.482344,
            -29.354627
          ],
          [
            49.709949,
            -28.547388
          ],
          [
            49.61342,
            -28.143768
          ],
          [
            49.163158,
            -27.330577
          ],
          [
            44.661837,
            -21.301154
          ],
          [
            35.358597,
            -9.766383
          ],
          [
            26.478961,
            0.686604
          ],
          [
            18.810185,
            10.24185
          ],
          [
            13.270039,
            17.471735
          ],
          [
            4.539818,
            27.951484
          ],
          [
            1.858154,
            31.464007
          ],
          [
            1.373306,
            32.008953
          ],
          [
            0.647295,
            32.495898
          ],
          [
            0.243675,
            32.573928
          ],
          [
            -0.544641,
            32.422719
          ],
          [
            -1.030903,
            31.995578
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0014886749999999949,
    0.28043383,
    -0.02251310499999999
  ],
  "construction_scale": 163.6858089527004,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
