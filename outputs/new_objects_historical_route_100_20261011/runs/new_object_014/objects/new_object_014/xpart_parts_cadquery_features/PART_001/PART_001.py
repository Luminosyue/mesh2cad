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
      "start": -1.8330549237694684,
      "length": 2.3330523160853653,
      "loops": [
        [
          [
            36.720643,
            2.980498
          ],
          [
            36.11564,
            38.079557
          ],
          [
            35.828944,
            38.82109
          ],
          [
            35.095374,
            39.673012
          ],
          [
            25.03464,
            48.955323
          ],
          [
            24.21961,
            49.366105
          ],
          [
            22.242198,
            49.534833
          ],
          [
            -0.498039,
            49.765491
          ],
          [
            -21.50804,
            49.557249
          ],
          [
            -23.485451,
            49.477157
          ],
          [
            -24.721334,
            49.163767
          ],
          [
            -35.43163,
            39.31544
          ],
          [
            -35.844275,
            38.788382
          ],
          [
            -36.150448,
            37.832381
          ],
          [
            -36.735584,
            1.497439
          ],
          [
            -36.183409,
            -37.309266
          ],
          [
            -35.844275,
            -38.441055
          ],
          [
            -35.241611,
            -39.286679
          ],
          [
            -26.159287,
            -47.937858
          ],
          [
            -24.721334,
            -49.1291
          ],
          [
            -23.960779,
            -49.409191
          ],
          [
            -17.800393,
            -49.590355
          ],
          [
            0.737843,
            -49.732576
          ],
          [
            22.489375,
            -49.496584
          ],
          [
            23.661719,
            -49.420915
          ],
          [
            24.582797,
            -49.173741
          ],
          [
            26.940378,
            -47.196328
          ],
          [
            34.848199,
            -39.734282
          ],
          [
            35.677817,
            -38.792329
          ],
          [
            36.084082,
            -37.94821
          ],
          [
            36.215669,
            -36.814916
          ],
          [
            36.695576,
            -7.400914
          ]
        ],
        [
          [
            -34.643278,
            5.205086
          ],
          [
            -34.332735,
            -37.80362
          ],
          [
            -33.766497,
            -38.582371
          ],
          [
            -23.979804,
            -47.7409
          ],
          [
            -23.485451,
            -47.805993
          ],
          [
            -21.755215,
            -47.251589
          ],
          [
            -20.976465,
            -47.159348
          ],
          [
            -20.519334,
            -47.214988
          ],
          [
            -19.702684,
            -47.704713
          ],
          [
            -18.294745,
            -47.818726
          ],
          [
            18.781727,
            -47.854651
          ],
          [
            19.980388,
            -47.731093
          ],
          [
            20.511962,
            -47.263024
          ],
          [
            21.006314,
            -47.179346
          ],
          [
            21.995021,
            -47.280466
          ],
          [
            23.478079,
            -47.8145
          ],
          [
            23.972433,
            -47.76868
          ],
          [
            29.163139,
            -42.732135
          ],
          [
            34.10667,
            -38.277553
          ],
          [
            34.415855,
            -37.80362
          ],
          [
            34.680756,
            0.014381
          ],
          [
            34.550425,
            37.585207
          ],
          [
            34.391066,
            38.007375
          ],
          [
            24.256831,
            47.434973
          ],
          [
            23.5153,
            47.799745
          ],
          [
            0.243491,
            47.975496
          ],
          [
            -23.485451,
            47.80267
          ],
          [
            -24.017026,
            47.664054
          ],
          [
            -34.227852,
            38.089245
          ],
          [
            -34.486847,
            37.622428
          ],
          [
            -34.456066,
            22.507441
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.499924070118946,
      "length": 1.3332041758474733,
      "loops": [
        [
          [
            -21.606379,
            -48.814889
          ],
          [
            -20.523836,
            -48.552106
          ],
          [
            -19.679465,
            -48.105438
          ],
          [
            -19.251059,
            -47.690678
          ],
          [
            -19.165898,
            -47.345165
          ],
          [
            -19.284866,
            -47.003455
          ],
          [
            -20.02498,
            -46.753009
          ],
          [
            -21.242379,
            -46.967057
          ],
          [
            -22.645583,
            -47.687379
          ],
          [
            -23.485101,
            -48.432212
          ],
          [
            -23.481254,
            -48.679386
          ],
          [
            -22.991099,
            -48.915359
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.499924070118946,
      "length": 1.3332041758474733,
      "loops": [
        [
          [
            22.888982,
            -48.926561
          ],
          [
            23.39853,
            -48.679386
          ],
          [
            23.455133,
            -48.432212
          ],
          [
            22.143858,
            -47.350245
          ],
          [
            20.511962,
            -46.841164
          ],
          [
            19.91927,
            -46.902899
          ],
          [
            19.608566,
            -47.196328
          ],
          [
            19.660597,
            -47.937858
          ],
          [
            20.363125,
            -48.538159
          ],
          [
            22.242198,
            -48.934827
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.499924070118946,
      "length": 1.3332041758474733,
      "loops": [
        [
          [
            35.589728,
            0.870219
          ],
          [
            35.727991,
            4.078117
          ],
          [
            35.589728,
            7.116211
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.499924070118946,
      "length": 1.3332041758474733,
      "loops": [
        [
          [
            35.589728,
            0.213792
          ],
          [
            35.566772,
            0.037336
          ],
          [
            35.589728,
            -0.131616
          ],
          [
            35.662342,
            -0.058234
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.499924070118946,
      "length": 1.3332041758474733,
      "loops": [
        [
          [
            35.615558,
            7.429675
          ],
          [
            35.589728,
            7.269662
          ],
          [
            35.589728,
            7.620926
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    3.676999999999153e-05,
    -0.00014345999999998416,
    -0.022929335
  ],
  "construction_scale": 100.2410757776021,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
