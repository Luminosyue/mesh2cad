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
      "length": 51.51715151515152,
      "loops": [
        [
          [
            7.20372,
            -29.607363
          ],
          [
            7.236997,
            28.993635
          ],
          [
            7.08168,
            29.477943
          ],
          [
            6.833812,
            29.675787
          ],
          [
            2.475062,
            29.76085
          ],
          [
            2.008022,
            29.477943
          ],
          [
            1.909171,
            28.993635
          ],
          [
            1.959328,
            26.087802
          ],
          [
            2.255149,
            25.603495
          ],
          [
            2.959369,
            24.971726
          ],
          [
            3.443671,
            24.694318
          ],
          [
            4.412285,
            24.581664
          ],
          [
            4.654326,
            24.150579
          ],
          [
            4.60369,
            -29.123057
          ],
          [
            4.647215,
            -29.607363
          ],
          [
            4.896592,
            -29.910641
          ],
          [
            5.380895,
            -30.02033
          ],
          [
            6.833812,
            -29.989064
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 51.51715151515152,
      "loops": [
        [
          [
            -3.820912,
            29.922787
          ],
          [
            -6.242443,
            30.000001
          ],
          [
            -7.195197,
            29.477943
          ],
          [
            -7.198607,
            26.087802
          ],
          [
            -6.260582,
            25.119193
          ],
          [
            -5.758135,
            24.882281
          ],
          [
            -4.964301,
            24.87398
          ],
          [
            -4.311328,
            25.119193
          ],
          [
            -3.208474,
            26.087802
          ],
          [
            -3.042533,
            27.850251
          ],
          [
            -3.14311,
            29.477943
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5151515151515156,
      "length": 24.244424242424234,
      "loops": [
        [
          [
            4.657479,
            24.150579
          ],
          [
            4.592674,
            14.948771
          ],
          [
            4.729152,
            13.865293
          ],
          [
            4.896592,
            13.534317
          ],
          [
            5.380895,
            13.313609
          ],
          [
            6.349509,
            13.317439
          ],
          [
            6.778204,
            13.495852
          ],
          [
            7.066653,
            13.980158
          ],
          [
            7.186241,
            14.948771
          ],
          [
            7.233418,
            28.993635
          ],
          [
            7.074924,
            29.477943
          ],
          [
            6.833812,
            29.668987
          ],
          [
            2.475062,
            29.774551
          ],
          [
            2.001676,
            29.477943
          ],
          [
            1.904606,
            28.993635
          ],
          [
            1.959097,
            26.087802
          ],
          [
            2.959369,
            24.979452
          ],
          [
            3.443671,
            24.703539
          ],
          [
            4.412285,
            24.583504
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5151515151515156,
      "length": 24.244424242424234,
      "loops": [
        [
          [
            -7.211053,
            29.431287
          ],
          [
            -7.188761,
            26.087802
          ],
          [
            -6.72675,
            25.565763
          ],
          [
            -5.758135,
            24.894691
          ],
          [
            -5.158967,
            24.866669
          ],
          [
            -4.356813,
            25.119193
          ],
          [
            -3.213298,
            26.087802
          ],
          [
            -3.040548,
            28.139891
          ],
          [
            -3.148951,
            29.477943
          ],
          [
            -3.336609,
            29.711293
          ],
          [
            -4.100644,
            29.970361
          ],
          [
            -5.758135,
            30.051417
          ],
          [
            -6.72675,
            29.845493
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.75757575757575,
      "length": 24.244424242424248,
      "loops": [
        [
          [
            4.640758,
            -29.607363
          ],
          [
            4.644158,
            24.150579
          ],
          [
            4.412285,
            24.584776
          ],
          [
            3.443671,
            24.715304
          ],
          [
            2.959369,
            25.019242
          ],
          [
            1.956039,
            26.087802
          ],
          [
            1.922645,
            28.993635
          ],
          [
            1.996632,
            29.477943
          ],
          [
            2.475062,
            29.796904
          ],
          [
            6.833812,
            29.682014
          ],
          [
            7.090187,
            29.477943
          ],
          [
            7.252387,
            28.993635
          ],
          [
            7.24933,
            -28.638751
          ],
          [
            7.219064,
            -29.607363
          ],
          [
            6.833812,
            -30.002427
          ],
          [
            5.380895,
            -30.03165
          ],
          [
            4.896592,
            -29.924528
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.75757575757575,
      "length": 24.244424242424248,
      "loops": [
        [
          [
            -4.049897,
            29.961102
          ],
          [
            -3.336609,
            29.703463
          ],
          [
            -3.036724,
            28.993635
          ],
          [
            -3.216841,
            26.087802
          ],
          [
            -4.375257,
            25.119193
          ],
          [
            -5.273833,
            24.862388
          ],
          [
            -5.758135,
            24.927999
          ],
          [
            -6.242443,
            25.176876
          ],
          [
            -7.152614,
            26.087802
          ],
          [
            -7.185087,
            29.477943
          ],
          [
            -6.242443,
            30.013027
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.39891777500000003,
    0.17326635499999998,
    0.007092435000000008
  ],
  "construction_scale": 98.2037869403242,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
