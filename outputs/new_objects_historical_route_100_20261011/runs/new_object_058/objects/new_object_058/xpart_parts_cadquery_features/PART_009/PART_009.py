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
      "start": -6.7021566882395955,
      "length": 9.342668318359088,
      "loops": [
        [
          [
            -6.001308,
            6.966051
          ],
          [
            5.28635,
            6.90404
          ],
          [
            5.79943,
            6.812127
          ],
          [
            6.135287,
            6.492027
          ],
          [
            6.351434,
            4.952801
          ],
          [
            6.284664,
            -31.47555
          ],
          [
            5.511486,
            -33.014775
          ],
          [
            5.339487,
            -34.040926
          ],
          [
            5.544871,
            -35.067079
          ],
          [
            6.31862,
            -36.606305
          ],
          [
            6.357669,
            -48.920112
          ],
          [
            6.618681,
            -49.502028
          ],
          [
            7.338656,
            -49.912633
          ],
          [
            14.521712,
            -49.800183
          ],
          [
            15.047241,
            -49.433187
          ],
          [
            15.192552,
            -48.920112
          ],
          [
            15.220047,
            -44.815507
          ],
          [
            15.173868,
            46.101568
          ],
          [
            15.063654,
            49.077281
          ],
          [
            14.901515,
            49.590359
          ],
          [
            14.624448,
            49.76051
          ],
          [
            7.338656,
            49.897267
          ],
          [
            6.825576,
            49.816529
          ],
          [
            6.509818,
            49.590359
          ],
          [
            6.312503,
            49.115542
          ],
          [
            6.347189,
            34.300836
          ],
          [
            6.063406,
            31.119646
          ],
          [
            6.230013,
            29.58042
          ],
          [
            6.303331,
            24.449667
          ],
          [
            6.092718,
            23.936589
          ],
          [
            5.79943,
            23.664364
          ],
          [
            5.28635,
            23.863069
          ],
          [
            4.260198,
            23.943589
          ],
          [
            -4.975156,
            24.008655
          ],
          [
            -5.534235,
            23.936589
          ],
          [
            -6.669331,
            23.320779
          ],
          [
            -7.015895,
            21.884288
          ],
          [
            -7.069209,
            20.960876
          ],
          [
            -6.567641,
            17.26661
          ],
          [
            -6.428003,
            7.51818
          ]
        ],
        [
          [
            6.213145,
            12.135857
          ],
          [
            5.79943,
            11.082708
          ],
          [
            4.796543,
            12.688842
          ],
          [
            4.504954,
            14.701234
          ],
          [
            5.28635,
            20.939825
          ],
          [
            5.79943,
            22.863076
          ],
          [
            6.020092,
            22.397364
          ],
          [
            6.165966,
            20.960876
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.6402435438519625,
      "length": 1.6250333440225824,
      "loops": [
        [
          [
            6.667892,
            8.031253
          ],
          [
            6.366382,
            32.084651
          ],
          [
            6.589637,
            34.1981
          ],
          [
            6.618907,
            39.841926
          ],
          [
            6.793105,
            41.894227
          ],
          [
            6.36827,
            42.92038
          ],
          [
            6.334345,
            43.433453
          ],
          [
            6.320957,
            49.077281
          ],
          [
            6.487111,
            49.590359
          ],
          [
            6.825576,
            49.841397
          ],
          [
            7.338656,
            49.932105
          ],
          [
            15.547856,
            49.998055
          ],
          [
            16.060936,
            49.876459
          ],
          [
            16.584575,
            49.077281
          ],
          [
            16.552222,
            46.511907
          ],
          [
            16.060936,
            45.921441
          ],
          [
            15.126544,
            45.485754
          ],
          [
            15.046831,
            44.972681
          ],
          [
            15.050762,
            -48.407035
          ],
          [
            15.036947,
            -48.920112
          ],
          [
            14.789297,
            -49.433187
          ],
          [
            14.008631,
            -49.719906
          ],
          [
            7.338656,
            -49.734437
          ],
          [
            6.749096,
            -49.433187
          ],
          [
            6.553722,
            -48.920112
          ],
          [
            6.52615,
            3.413575
          ],
          [
            6.415605,
            6.492027
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.6402435438519625,
      "length": 1.6250333440225824,
      "loops": [
        [
          [
            -6.909441,
            18.805836
          ],
          [
            -6.940183,
            19.318912
          ],
          [
            -6.675601,
            19.831987
          ],
          [
            -6.001308,
            20.296829
          ],
          [
            -5.488229,
            20.305415
          ],
          [
            -4.975156,
            20.030973
          ],
          [
            -4.511569,
            19.318912
          ],
          [
            -4.513545,
            18.805836
          ],
          [
            -4.760539,
            18.292761
          ],
          [
            -5.488229,
            17.868375
          ],
          [
            -6.211088,
            18.007082
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.265008801607015,
      "length": 2.43741597290011,
      "loops": [
        [
          [
            -13.184363,
            17.750708
          ],
          [
            -6.514382,
            17.887605
          ],
          [
            -5.504955,
            18.292761
          ],
          [
            -5.178546,
            18.805836
          ],
          [
            -5.176179,
            19.318912
          ],
          [
            -5.46211,
            19.831987
          ],
          [
            -6.78433,
            20.335102
          ],
          [
            -13.915194,
            20.26992
          ],
          [
            -15.749741,
            19.974908
          ],
          [
            -16.52119,
            19.318912
          ],
          [
            -16.579101,
            18.805836
          ],
          [
            -16.262814,
            18.313983
          ],
          [
            -15.236662,
            17.931435
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.42090747500000003,
    -0.001610589999999995,
    0.188102025
  ],
  "construction_scale": 208.07492162025775,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
