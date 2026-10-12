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
      "start": -3.2874732255662718,
      "length": 0.5978539035774357,
      "loops": [
        [
          [
            -21.630481,
            46.502573
          ],
          [
            22.441396,
            46.491912
          ],
          [
            43.629797,
            46.633711
          ],
          [
            44.477335,
            46.886324
          ],
          [
            44.642382,
            49.044425
          ],
          [
            44.477335,
            49.251722
          ],
          [
            44.038881,
            49.329204
          ],
          [
            41.934728,
            49.43302
          ],
          [
            17.356181,
            49.484055
          ],
          [
            -26.285792,
            49.415214
          ],
          [
            -42.516262,
            49.272084
          ],
          [
            -44.53974,
            49.044425
          ],
          [
            -44.513956,
            47.636027
          ],
          [
            -44.377761,
            47.349356
          ],
          [
            -43.66642,
            46.933542
          ],
          [
            -42.818884,
            46.868576
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.6897508209178587,
      "length": 4.383429133017386,
      "loops": [
        [
          [
            43.629797,
            -49.860794
          ],
          [
            -43.66642,
            -49.867832
          ],
          [
            -44.513956,
            -49.792524
          ],
          [
            -45.045213,
            -49.269761
          ],
          [
            -45.160256,
            -47.66014
          ],
          [
            -45.100817,
            42.167752
          ],
          [
            -45.221458,
            47.349356
          ],
          [
            -45.177548,
            49.044425
          ],
          [
            -44.513956,
            49.897785
          ],
          [
            42.782259,
            49.973812
          ],
          [
            44.477335,
            49.916559
          ],
          [
            45.228378,
            49.044425
          ],
          [
            45.049249,
            -49.269761
          ],
          [
            44.477335,
            -49.817731
          ]
        ],
        [
          [
            7.185745,
            -6.07555
          ],
          [
            8.880818,
            -5.775562
          ],
          [
            9.60842,
            -5.197884
          ],
          [
            10.037878,
            -4.350348
          ],
          [
            10.182571,
            -3.596204
          ],
          [
            11.204109,
            16.838052
          ],
          [
            11.12323,
            18.533126
          ],
          [
            10.73449,
            20.228198
          ],
          [
            8.488671,
            27.008487
          ],
          [
            7.72545,
            28.703561
          ],
          [
            7.185745,
            29.248042
          ],
          [
            6.33821,
            29.431123
          ],
          [
            -4.679759,
            29.441031
          ],
          [
            -7.222367,
            28.813187
          ],
          [
            -17.392801,
            25.10519
          ],
          [
            -18.088717,
            24.465878
          ],
          [
            -18.393847,
            23.618343
          ],
          [
            -18.451046,
            22.860434
          ],
          [
            -18.874382,
            5.820086
          ],
          [
            -19.149505,
            1.582406
          ],
          [
            -18.870437,
            -0.960204
          ],
          [
            -18.209713,
            -3.502812
          ],
          [
            -17.754978,
            -6.045421
          ],
          [
            -17.392801,
            -6.660232
          ],
          [
            -16.545265,
            -7.015329
          ],
          [
            -15.793821,
            -7.077453
          ],
          [
            -5.449006,
            -6.971246
          ],
          [
            -4.759094,
            -6.045421
          ],
          [
            -4.502752,
            -5.197884
          ],
          [
            -3.832222,
            -4.648362
          ],
          [
            3.795601,
            -5.507852
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6935468131705038,
      "length": 1.5940579113247906,
      "loops": [
        [
          [
            -37.380365,
            3.771711
          ],
          [
            -39.509703,
            1.663369
          ],
          [
            -40.994312,
            -0.112668
          ],
          [
            -41.225855,
            -0.85816
          ],
          [
            -41.262282,
            -1.80774
          ],
          [
            -40.886682,
            -3.502812
          ],
          [
            -40.547861,
            -4.350348
          ],
          [
            -39.316591,
            -6.045421
          ],
          [
            -37.733668,
            -7.478218
          ],
          [
            -36.038594,
            -8.38135
          ],
          [
            -34.343522,
            -9.040052
          ],
          [
            -30.634248,
            -10.071315
          ],
          [
            -28.41077,
            -10.478444
          ],
          [
            -26.508819,
            -10.48998
          ],
          [
            -24.50369,
            -9.9525
          ],
          [
            -24.173089,
            -9.551852
          ],
          [
            -23.508707,
            -9.25241
          ],
          [
            -23.325553,
            -8.876062
          ],
          [
            -23.095729,
            -8.817853
          ],
          [
            -21.860244,
            -7.51073
          ],
          [
            -20.782945,
            -6.834414
          ],
          [
            -19.936502,
            -5.197884
          ],
          [
            -20.174698,
            -3.502812
          ],
          [
            -20.782945,
            -2.273117
          ],
          [
            -21.630481,
            -1.568761
          ],
          [
            -22.542639,
            -1.743118
          ],
          [
            -24.173089,
            -0.47641
          ],
          [
            -25.868161,
            0.509502
          ],
          [
            -33.495986,
            3.795673
          ],
          [
            -35.191058,
            4.125078
          ],
          [
            -36.88613,
            3.940239
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.18504307,
    0.15353645,
    0.41556936
  ],
  "construction_scale": 171.85682291866092,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
