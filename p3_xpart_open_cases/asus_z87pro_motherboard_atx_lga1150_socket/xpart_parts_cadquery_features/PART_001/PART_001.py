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
      "length": 36.36563636363636,
      "loops": [
        [
          [
            -5.299195,
            12.612107
          ],
          [
            -5.08172,
            13.241254
          ],
          [
            -4.516197,
            13.701033
          ],
          [
            -2.62875,
            14.248119
          ],
          [
            -0.112164,
            14.629938
          ],
          [
            5.550167,
            14.870884
          ],
          [
            6.254126,
            14.499549
          ],
          [
            6.401895,
            13.870401
          ],
          [
            6.388243,
            13.241254
          ],
          [
            6.179316,
            12.973937
          ],
          [
            5.550167,
            12.749989
          ],
          [
            -0.741308,
            12.536195
          ],
          [
            -2.667534,
            11.982959
          ],
          [
            -3.44909,
            11.353811
          ],
          [
            -3.770701,
            9.466369
          ],
          [
            -4.032694,
            5.592679
          ],
          [
            -4.066795,
            -4.374878
          ],
          [
            -3.908856,
            -6.26232
          ],
          [
            -3.438848,
            -8.778911
          ],
          [
            -2.519953,
            -10.037206
          ],
          [
            -2.339424,
            -11.924649
          ],
          [
            -2.62875,
            -12.693834
          ],
          [
            -3.887047,
            -13.077516
          ],
          [
            -4.516197,
            -13.007094
          ],
          [
            -5.14534,
            -12.69995
          ],
          [
            -5.533819,
            -11.924649
          ],
          [
            -5.837855,
            -5.633173
          ],
          [
            -5.938009,
            0.658303
          ],
          [
            -5.688286,
            8.837221
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.63636363636364,
      "length": 30.30503030303031,
      "loops": [
        [
          [
            -5.790717,
            8.208073
          ],
          [
            -5.974925,
            -0.599992
          ],
          [
            -5.673853,
            -11.924649
          ],
          [
            -5.582167,
            -12.553796
          ],
          [
            -5.14534,
            -13.055753
          ],
          [
            -4.516197,
            -13.280335
          ],
          [
            -3.887047,
            -13.301077
          ],
          [
            -3.257899,
            -13.192317
          ],
          [
            -2.62875,
            -12.780281
          ],
          [
            -2.444168,
            -11.924649
          ],
          [
            -2.62875,
            -10.382038
          ],
          [
            -3.36808,
            -9.408058
          ],
          [
            -3.627536,
            -8.778911
          ],
          [
            -4.230884,
            -5.004025
          ],
          [
            -4.164638,
            5.062336
          ],
          [
            -3.912209,
            8.837221
          ],
          [
            -3.413979,
            11.353811
          ],
          [
            -3.211894,
            11.982959
          ],
          [
            -2.729386,
            12.612107
          ],
          [
            -2.665414,
            13.241254
          ],
          [
            -3.257899,
            13.725061
          ],
          [
            -4.516197,
            13.715282
          ],
          [
            -5.185985,
            13.241254
          ],
          [
            -5.518339,
            11.982959
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666667,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            -4.856665,
            -8.149763
          ],
          [
            -4.386535,
            -10.037206
          ],
          [
            -3.292794,
            -11.295501
          ],
          [
            -3.042429,
            -12.553796
          ],
          [
            -3.06456,
            -13.182943
          ],
          [
            -3.257899,
            -13.572946
          ],
          [
            -3.887047,
            -13.960642
          ],
          [
            -4.516197,
            -14.052652
          ],
          [
            -5.14534,
            -13.989567
          ],
          [
            -5.774489,
            -13.693279
          ],
          [
            -6.125728,
            -13.182943
          ],
          [
            -6.219306,
            -12.553796
          ],
          [
            -6.466105,
            -6.891468
          ],
          [
            -6.508416,
            0.086272
          ],
          [
            -6.261509,
            8.208073
          ],
          [
            -5.819967,
            11.982959
          ],
          [
            -5.14534,
            12.68425
          ],
          [
            -3.887047,
            12.899779
          ],
          [
            -3.321117,
            12.612107
          ],
          [
            -3.192904,
            11.982959
          ],
          [
            -4.343944,
            8.208073
          ],
          [
            -4.790111,
            5.062336
          ],
          [
            -5.059323,
            -5.633173
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.895800215,
    -0.01032035499999999,
    -0.004353560000000034
  ],
  "construction_scale": 63.7868421318522,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
