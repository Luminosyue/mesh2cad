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
      "start": -2.8918081315070485,
      "length": 4.2063820454264285,
      "loops": [
        [
          [
            -48.393681,
            -8.80079
          ],
          [
            -48.18419,
            9.690101
          ],
          [
            -47.890254,
            10.867279
          ],
          [
            -47.410621,
            11.652064
          ],
          [
            -46.521173,
            12.327068
          ],
          [
            -45.736386,
            12.559362
          ],
          [
            45.691128,
            12.641749
          ],
          [
            47.123962,
            12.43685
          ],
          [
            48.045487,
            11.855587
          ],
          [
            48.623943,
            10.867279
          ],
          [
            49.020183,
            9.297707
          ],
          [
            49.213365,
            0.272674
          ],
          [
            49.082676,
            -9.92954
          ],
          [
            48.809165,
            -10.714324
          ],
          [
            48.045487,
            -11.496341
          ],
          [
            46.083522,
            -12.176281
          ],
          [
            -44.166818,
            -12.369671
          ],
          [
            -45.343995,
            -12.237959
          ],
          [
            -46.521173,
            -11.868027
          ],
          [
            -47.30596,
            -11.403796
          ],
          [
            -47.898794,
            -10.714324
          ],
          [
            -48.224276,
            -9.92954
          ]
        ],
        [
          [
            47.83185,
            -9.144753
          ],
          [
            47.77201,
            8.856884
          ],
          [
            47.391098,
            10.474886
          ],
          [
            47.14403,
            10.867279
          ],
          [
            46.475914,
            11.324472
          ],
          [
            -44.607639,
            11.347073
          ],
          [
            -45.343995,
            11.307298
          ],
          [
            -46.128783,
            10.958747
          ],
          [
            -46.519795,
            10.474886
          ],
          [
            -46.777313,
            9.690101
          ],
          [
            -47.028219,
            4.148171
          ],
          [
            -47.094846,
            -8.75236
          ],
          [
            -46.913564,
            -9.6338
          ],
          [
            -46.499624,
            -10.321932
          ],
          [
            -45.758335,
            -10.792872
          ],
          [
            -44.951605,
            -10.993033
          ],
          [
            -42.645674,
            -11.125946
          ],
          [
            44.906344,
            -11.00021
          ],
          [
            46.868307,
            -10.611267
          ],
          [
            47.653093,
            -9.935229
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.3144582415941195,
      "length": 1.5774655622381981,
      "loops": [
        [
          [
            5.201169,
            13.295139
          ],
          [
            -43.382031,
            13.282634
          ],
          [
            -46.316158,
            13.221635
          ],
          [
            -47.30596,
            12.871689
          ],
          [
            -47.409814,
            12.540704
          ],
          [
            -47.70293,
            12.43685
          ],
          [
            -47.808493,
            11.762207
          ],
          [
            -48.090742,
            11.438962
          ],
          [
            -48.574752,
            10.174107
          ],
          [
            -48.875529,
            9.953372
          ],
          [
            -49.025176,
            9.447352
          ],
          [
            -49.267926,
            9.335311
          ],
          [
            -49.377797,
            8.512922
          ],
          [
            -49.518889,
            3.804209
          ],
          [
            -49.402893,
            -8.359968
          ],
          [
            -49.534672,
            -12.801934
          ],
          [
            -49.328881,
            -13.461073
          ],
          [
            -46.521173,
            -13.584545
          ],
          [
            45.691128,
            -13.540502
          ],
          [
            46.98181,
            -13.461073
          ],
          [
            47.927268,
            -13.068682
          ],
          [
            48.437877,
            -12.481781
          ],
          [
            48.611338,
            -11.672569
          ],
          [
            48.830271,
            -11.436766
          ],
          [
            49.222665,
            -9.259982
          ],
          [
            49.222665,
            6.791086
          ],
          [
            48.989421,
            8.746165
          ],
          [
            48.437877,
            10.638793
          ],
          [
            47.883802,
            11.813748
          ],
          [
            46.828586,
            12.868964
          ],
          [
            45.70116,
            13.221635
          ],
          [
            44.51395,
            13.260218
          ],
          [
            37.45088,
            13.238154
          ],
          [
            37.15312,
            13.127003
          ],
          [
            35.870397,
            13.232546
          ],
          [
            34.789373,
            13.136394
          ],
          [
            34.569385,
            12.963988
          ],
          [
            33.919346,
            13.093904
          ],
          [
            32.349775,
            12.817908
          ],
          [
            31.172596,
            12.951025
          ],
          [
            29.995418,
            12.743954
          ],
          [
            28.818239,
            12.878892
          ],
          [
            28.425847,
            12.784248
          ],
          [
            28.033454,
            12.963264
          ],
          [
            27.258055,
            12.819856
          ],
          [
            26.856276,
            12.952392
          ],
          [
            24.501919,
            12.872951
          ],
          [
            23.717133,
            13.169492
          ],
          [
            22.555469,
            12.813728
          ],
          [
            20.67965,
            13.119977
          ],
          [
            20.577991,
            12.822386
          ],
          [
            20.185599,
            13.03273
          ],
          [
            19.005484,
            13.224572
          ],
          [
            18.777482,
            13.06018
          ],
          [
            17.890616,
            13.162261
          ],
          [
            16.477833,
            13.005472
          ],
          [
            15.168118,
            13.13801
          ],
          [
            14.946891,
            12.966844
          ],
          [
            14.427796,
            13.221635
          ],
          [
            13.999988,
            13.221635
          ],
          [
            12.337743,
            12.948499
          ],
          [
            11.94535,
            13.222785
          ],
          [
            10.544587,
            13.052827
          ],
          [
            9.983386,
            13.233499
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.278353285,
    -0.16123949499999998,
    0.76169066
  ],
  "construction_scale": 79.5663766146017,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
