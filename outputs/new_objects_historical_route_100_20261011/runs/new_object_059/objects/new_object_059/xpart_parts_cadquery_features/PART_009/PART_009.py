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
      "length": 93.94139393939393,
      "loops": [
        [
          [
            23.647977,
            33.27696
          ],
          [
            28.737182,
            40.453481
          ],
          [
            29.265292,
            40.12138
          ],
          [
            33.460385,
            34.24699
          ],
          [
            36.610382,
            30.501813
          ],
          [
            38.243156,
            29.11572
          ],
          [
            39.299378,
            28.968388
          ],
          [
            39.827487,
            29.243053
          ],
          [
            40.171766,
            30.133102
          ],
          [
            40.043115,
            30.661209
          ],
          [
            36.680799,
            34.357981
          ],
          [
            30.321511,
            42.34039
          ],
          [
            29.793401,
            42.860586
          ],
          [
            28.737182,
            43.186455
          ],
          [
            28.209072,
            43.122086
          ],
          [
            27.680963,
            42.771529
          ],
          [
            26.780772,
            41.751517
          ],
          [
            21.021448,
            33.773435
          ],
          [
            18.027413,
            30.133102
          ],
          [
            16.73371,
            28.115394
          ],
          [
            10.434435,
            20.074522
          ],
          [
            4.444135,
            13.241879
          ],
          [
            -3.087216,
            3.727616
          ],
          [
            -14.364492,
            -9.508113
          ],
          [
            -32.620654,
            -32.646336
          ],
          [
            -39.388972,
            -40.420374
          ],
          [
            -39.908487,
            -41.161713
          ],
          [
            -39.954185,
            -41.689822
          ],
          [
            -39.457351,
            -42.217932
          ],
          [
            -38.860867,
            -42.39004
          ],
          [
            -38.332751,
            -42.273478
          ],
          [
            -37.804645,
            -41.871993
          ],
          [
            -30.732746,
            -33.683652
          ],
          [
            -21.205553,
            -21.705916
          ],
          [
            3.769991,
            8.503413
          ],
          [
            13.16326,
            19.492439
          ],
          [
            19.231206,
            27.427723
          ],
          [
            20.366054,
            29.171609
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
            16.912599,
            28.548773
          ],
          [
            7.612793,
            16.368841
          ],
          [
            -7.174278,
            -1.443131
          ],
          [
            -25.133534,
            -24.705316
          ],
          [
            -37.192749,
            -39.577384
          ],
          [
            -38.624614,
            -41.689822
          ],
          [
            -38.744561,
            -42.217932
          ],
          [
            -38.332751,
            -42.88356
          ],
          [
            -37.804645,
            -43.10743
          ],
          [
            -37.276538,
            -43.058536
          ],
          [
            -36.748426,
            -42.77458
          ],
          [
            -36.284643,
            -42.217932
          ],
          [
            -17.738559,
            -18.704052
          ],
          [
            -11.924023,
            -11.028864
          ],
          [
            -5.593632,
            -3.294421
          ],
          [
            0.750452,
            4.842532
          ],
          [
            15.375891,
            22.739566
          ],
          [
            20.288304,
            29.489607
          ],
          [
            26.090951,
            36.470416
          ],
          [
            28.211372,
            39.908985
          ],
          [
            28.737182,
            40.327865
          ],
          [
            28.882714,
            40.167188
          ],
          [
            32.43395,
            34.542903
          ],
          [
            34.178595,
            32.245545
          ],
          [
            36.658827,
            29.621739
          ],
          [
            37.715046,
            28.831552
          ],
          [
            38.771268,
            28.585642
          ],
          [
            39.299378,
            28.849074
          ],
          [
            39.58199,
            29.604996
          ],
          [
            39.299378,
            30.137293
          ],
          [
            34.107601,
            36.470416
          ],
          [
            29.950671,
            42.279624
          ],
          [
            29.265292,
            42.868584
          ],
          [
            28.209072,
            43.093081
          ],
          [
            27.680963,
            42.930168
          ],
          [
            26.934145,
            42.279624
          ],
          [
            21.847123,
            35.414203
          ],
          [
            17.646877,
            30.156796
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.139109675,
    0.298220225,
    -0.00015084999999999404
  ],
  "construction_scale": 214.17202871327288,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
