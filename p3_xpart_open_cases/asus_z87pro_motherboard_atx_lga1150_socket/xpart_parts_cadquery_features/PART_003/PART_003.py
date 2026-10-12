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
            -2.982981,
            -38.04188
          ],
          [
            -3.985053,
            16.868795
          ],
          [
            -4.16575,
            37.309528
          ],
          [
            -3.952448,
            37.520032
          ],
          [
            -2.914068,
            37.720872
          ],
          [
            6.950534,
            38.61951
          ],
          [
            7.585479,
            38.867097
          ],
          [
            7.853416,
            39.386283
          ],
          [
            7.715735,
            39.905474
          ],
          [
            6.950534,
            40.381917
          ],
          [
            0.201069,
            40.418367
          ],
          [
            -6.029205,
            40.18502
          ],
          [
            -6.817366,
            39.905474
          ],
          [
            -7.183179,
            39.386283
          ],
          [
            -6.614224,
            9.273289
          ],
          [
            -5.592664,
            -24.272497
          ],
          [
            -4.990827,
            -37.457856
          ],
          [
            -4.746985,
            -40.049725
          ],
          [
            -4.667243,
            -40.568912
          ],
          [
            -4.471637,
            -40.784903
          ],
          [
            -3.952448,
            -40.887449
          ],
          [
            -3.25942,
            -40.568912
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 24.24442424242424,
      "loops": [
        [
          [
            -7.369337,
            37.309528
          ],
          [
            -6.772421,
            -10.975106
          ],
          [
            -5.964593,
            -30.886467
          ],
          [
            -5.211996,
            -40.568912
          ],
          [
            -4.974328,
            -41.088103
          ],
          [
            -4.471637,
            -41.403371
          ],
          [
            -3.952448,
            -41.479806
          ],
          [
            -2.914068,
            -41.135528
          ],
          [
            -2.498488,
            -40.568912
          ],
          [
            -2.321453,
            -39.530534
          ],
          [
            -2.274189,
            -37.453775
          ],
          [
            -4.010447,
            9.273289
          ],
          [
            -4.358284,
            37.309528
          ],
          [
            -3.952448,
            37.720682
          ],
          [
            -1.875689,
            38.027903
          ],
          [
            7.177936,
            38.867097
          ],
          [
            7.469724,
            38.960686
          ],
          [
            7.813292,
            39.386283
          ],
          [
            7.801686,
            39.905474
          ],
          [
            7.469724,
            40.368827
          ],
          [
            6.950534,
            40.533611
          ],
          [
            3.316208,
            40.587227
          ],
          [
            -6.029205,
            40.459947
          ],
          [
            -6.548395,
            40.418054
          ],
          [
            -7.209162,
            39.905474
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.696969696969695,
      "length": 42.42624242424242,
      "loops": [
        [
          [
            -2.206385,
            -36.934585
          ],
          [
            -3.356999,
            -8.898348
          ],
          [
            -4.594183,
            12.660989
          ],
          [
            -4.691911,
            22.006401
          ],
          [
            -4.542892,
            37.828715
          ],
          [
            -3.952448,
            38.382299
          ],
          [
            6.950534,
            39.647337
          ],
          [
            7.56309,
            39.905474
          ],
          [
            7.784362,
            40.424665
          ],
          [
            7.469724,
            41.126184
          ],
          [
            6.950534,
            41.349293
          ],
          [
            0.201069,
            41.400816
          ],
          [
            -6.548395,
            41.154991
          ],
          [
            -7.067585,
            40.952237
          ],
          [
            -7.28061,
            40.697228
          ],
          [
            -7.499333,
            40.424665
          ],
          [
            -7.570958,
            39.905474
          ],
          [
            -7.825517,
            32.390194
          ],
          [
            -7.75915,
            19.65708
          ],
          [
            -7.28259,
            2.277197
          ],
          [
            -6.440538,
            -18.76295
          ],
          [
            -5.106165,
            -40.049725
          ],
          [
            -4.849521,
            -41.088103
          ],
          [
            -4.471637,
            -41.398648
          ],
          [
            -3.952448,
            -41.540103
          ],
          [
            -3.433257,
            -41.497818
          ],
          [
            -2.641214,
            -41.088103
          ],
          [
            -2.246079,
            -40.049725
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
            -7.802882,
            28.681214
          ],
          [
            -7.551043,
            40.424665
          ],
          [
            -7.426211,
            40.943856
          ],
          [
            -7.067585,
            41.303472
          ],
          [
            -6.548395,
            41.496415
          ],
          [
            -3.631167,
            41.528724
          ],
          [
            6.431345,
            41.538552
          ],
          [
            7.469724,
            41.352659
          ],
          [
            7.754561,
            40.943856
          ],
          [
            7.774429,
            40.424665
          ],
          [
            7.469724,
            39.986201
          ],
          [
            7.080781,
            39.840858
          ],
          [
            -3.111978,
            38.624925
          ],
          [
            -4.397146,
            38.347906
          ],
          [
            -4.632827,
            37.828715
          ],
          [
            -4.711423,
            27.642834
          ],
          [
            -4.313115,
            10.830857
          ],
          [
            -2.21114,
            -38.492157
          ],
          [
            -2.312032,
            -40.049725
          ],
          [
            -2.485491,
            -40.568912
          ],
          [
            -2.914068,
            -40.968476
          ],
          [
            -3.952448,
            -41.193347
          ],
          [
            -4.471637,
            -41.033584
          ],
          [
            -4.855806,
            -40.568912
          ],
          [
            -4.941414,
            -40.049725
          ],
          [
            -5.751639,
            -26.550794
          ],
          [
            -6.92408,
            0.125785
          ],
          [
            -7.65572,
            20.37418
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
            -7.49111,
            29.002493
          ],
          [
            -4.71124,
            -39.530534
          ],
          [
            -4.471637,
            -40.617998
          ],
          [
            -3.952448,
            -40.949775
          ],
          [
            -3.433257,
            -40.983417
          ],
          [
            -2.914068,
            -40.865937
          ],
          [
            -2.394878,
            -40.339497
          ],
          [
            -2.210353,
            -39.530534
          ],
          [
            -2.192831,
            -37.972966
          ],
          [
            -3.162749,
            -5.490283
          ],
          [
            -4.61194,
            31.079252
          ],
          [
            -4.745777,
            37.828715
          ],
          [
            -4.471637,
            38.35362
          ],
          [
            -2.275823,
            38.839711
          ],
          [
            0.946522,
            39.327907
          ],
          [
            6.950534,
            39.946025
          ],
          [
            7.469724,
            40.123613
          ],
          [
            7.733481,
            40.424665
          ],
          [
            7.794657,
            40.943856
          ],
          [
            7.444071,
            41.463042
          ],
          [
            6.950534,
            41.600473
          ],
          [
            4.354587,
            41.627786
          ],
          [
            -6.548395,
            41.496943
          ],
          [
            -7.067585,
            41.384006
          ],
          [
            -7.53313,
            40.943856
          ],
          [
            -7.685426,
            37.602454
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00014964499999997605,
    -0.102452625,
    0.011233464999999998
  ],
  "construction_scale": 52.63862892205357,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
