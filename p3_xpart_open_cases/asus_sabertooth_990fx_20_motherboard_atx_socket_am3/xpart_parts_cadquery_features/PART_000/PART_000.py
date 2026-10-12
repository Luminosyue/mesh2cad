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
            11.760055,
            -38.516236
          ],
          [
            11.878205,
            38.39882
          ],
          [
            11.644323,
            39.016149
          ],
          [
            11.138303,
            39.322783
          ],
          [
            10.126262,
            39.45227
          ],
          [
            -10.367552,
            39.438616
          ],
          [
            -11.429025,
            39.157855
          ],
          [
            -11.801546,
            38.651832
          ],
          [
            -11.931457,
            28.784438
          ],
          [
            -11.828895,
            -38.010784
          ],
          [
            -11.632603,
            -39.682103
          ],
          [
            -10.873003,
            -40.191746
          ],
          [
            -9.861532,
            -40.374313
          ],
          [
            -7.078422,
            -40.443939
          ],
          [
            9.367801,
            -40.479086
          ],
          [
            10.885292,
            -40.325338
          ],
          [
            11.385328,
            -40.034296
          ],
          [
            11.644323,
            -39.648745
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            11.932162,
            3.200765
          ],
          [
            12.128022,
            10.567714
          ],
          [
            12.142519,
            20.911468
          ],
          [
            12.069853,
            37.639789
          ],
          [
            11.806243,
            38.904841
          ],
          [
            10.885292,
            39.473462
          ],
          [
            -1.482542,
            39.69735
          ],
          [
            -10.620562,
            39.624905
          ],
          [
            -11.632603,
            39.258109
          ],
          [
            -12.010834,
            38.651832
          ],
          [
            -12.119082,
            37.133772
          ],
          [
            -12.060188,
            -37.533856
          ],
          [
            -11.879782,
            -39.275266
          ],
          [
            -11.379592,
            -39.776502
          ],
          [
            -10.367552,
            -40.112004
          ],
          [
            -8.849492,
            -40.18946
          ],
          [
            9.902911,
            -40.206682
          ],
          [
            11.138303,
            -40.096587
          ],
          [
            11.80773,
            -39.528278
          ],
          [
            11.968738,
            -38.769245
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 30.305030303030296,
      "loops": [
        [
          [
            11.745782,
            -5.371919
          ],
          [
            11.977197,
            13.603835
          ],
          [
            11.695287,
            27.161091
          ],
          [
            11.697215,
            36.88076
          ],
          [
            11.590526,
            38.651832
          ],
          [
            11.333503,
            39.410862
          ],
          [
            10.632282,
            39.905259
          ],
          [
            9.367233,
            40.136845
          ],
          [
            -9.861532,
            40.277193
          ],
          [
            -11.379592,
            40.02158
          ],
          [
            -12.070379,
            39.157849
          ],
          [
            -12.175167,
            37.639789
          ],
          [
            -12.176769,
            -36.850455
          ],
          [
            -12.073625,
            -38.516236
          ],
          [
            -11.887392,
            -39.022257
          ],
          [
            -11.632603,
            -39.22183
          ],
          [
            -10.367552,
            -39.604129
          ],
          [
            7.195429,
            -39.669017
          ],
          [
            9.873253,
            -39.811191
          ],
          [
            10.632282,
            -39.721947
          ],
          [
            11.251688,
            -39.275266
          ],
          [
            11.608106,
            -37.862493
          ],
          [
            11.812497,
            -30.925935
          ],
          [
            11.985818,
            -15.745331
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.72727272727272,
      "length": 21.214121212121217,
      "loops": [
        [
          [
            -12.203517,
            -35.480117
          ],
          [
            -12.079836,
            -38.516236
          ],
          [
            -11.632603,
            -39.007394
          ],
          [
            -10.620562,
            -39.350384
          ],
          [
            9.766253,
            -39.49454
          ],
          [
            10.76636,
            -39.275266
          ],
          [
            11.275872,
            -38.516236
          ],
          [
            11.428525,
            -34.721087
          ],
          [
            11.623606,
            -2.228799
          ],
          [
            11.484661,
            38.39882
          ],
          [
            11.342181,
            39.410862
          ],
          [
            11.043191,
            39.852901
          ],
          [
            10.632282,
            40.086983
          ],
          [
            9.114222,
            40.236198
          ],
          [
            -10.114542,
            40.441567
          ],
          [
            -11.379592,
            40.115983
          ],
          [
            -11.885613,
            39.670628
          ],
          [
            -12.130672,
            39.157849
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -12.100781,
            19.676076
          ],
          [
            -12.053922,
            -37.504198
          ],
          [
            -11.971171,
            -38.263228
          ],
          [
            -11.679359,
            -38.769245
          ],
          [
            -10.620562,
            -39.198834
          ],
          [
            -7.584442,
            -39.30632
          ],
          [
            9.873253,
            -39.304433
          ],
          [
            10.632282,
            -39.229953
          ],
          [
            11.138303,
            -38.958371
          ],
          [
            11.44759,
            -38.516236
          ],
          [
            11.538974,
            -38.010215
          ],
          [
            11.650971,
            -30.419914
          ],
          [
            11.499039,
            11.579755
          ],
          [
            11.590718,
            38.470913
          ],
          [
            11.455725,
            39.663871
          ],
          [
            10.885292,
            40.137544
          ],
          [
            9.54815,
            40.30773
          ],
          [
            -10.114542,
            40.500043
          ],
          [
            -11.357471,
            40.143335
          ],
          [
            -11.891538,
            39.663871
          ],
          [
            -12.021025,
            38.651832
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.003106185000000039,
    -0.005045864999999997,
    -0.0037873150000000133
  ],
  "construction_scale": 51.303425341426475,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
