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
  "operation": "extrude",
  "basis": [
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -45.93556897872026,
      "length": 91.87113795744052,
      "loops": [
        [
          [
            -49.799685,
            20.167592
          ],
          [
            -49.389563,
            34.48559
          ],
          [
            -49.049408,
            37.490982
          ],
          [
            -48.021195,
            40.746825
          ],
          [
            -47.338853,
            42.35673
          ],
          [
            -45.62893,
            44.754016
          ],
          [
            -43.569874,
            46.487262
          ],
          [
            -39.770747,
            48.401264
          ],
          [
            -35.555492,
            49.251973
          ],
          [
            -25.036618,
            49.760111
          ],
          [
            0.759668,
            49.857577
          ],
          [
            29.353281,
            49.533491
          ],
          [
            34.069437,
            49.260391
          ],
          [
            38.327076,
            48.697623
          ],
          [
            41.332467,
            47.756907
          ],
          [
            44.17592,
            46.006264
          ],
          [
            45.08921,
            45.231146
          ],
          [
            47.092805,
            42.812162
          ],
          [
            48.65058,
            39.494577
          ],
          [
            49.447024,
            35.236938
          ],
          [
            49.81414,
            29.727052
          ],
          [
            49.9522,
            8.89737
          ],
          [
            49.768358,
            -26.415993
          ],
          [
            49.506066,
            -32.384394
          ],
          [
            49.070336,
            -37.185316
          ],
          [
            48.222241,
            -40.441159
          ],
          [
            46.836368,
            -43.404167
          ],
          [
            43.836962,
            -46.496218
          ],
          [
            40.873954,
            -48.248699
          ],
          [
            37.86856,
            -49.136336
          ],
          [
            36.32348,
            -49.399374
          ],
          [
            28.55955,
            -49.880058
          ],
          [
            8.523599,
            -49.868491
          ],
          [
            -29.795157,
            -49.297414
          ],
          [
            -34.804144,
            -49.017805
          ],
          [
            -39.197972,
            -48.408993
          ],
          [
            -42.067174,
            -47.574334
          ],
          [
            -45.07257,
            -46.053962
          ],
          [
            -45.768141,
            -45.450147
          ],
          [
            -46.654382,
            -44.17675
          ],
          [
            -48.091202,
            -41.400572
          ],
          [
            -48.983326,
            -37.936664
          ],
          [
            -49.401925,
            -34.38799
          ],
          [
            -49.697724,
            -24.620464
          ]
        ],
        [
          [
            -47.17056,
            24.718065
          ],
          [
            -47.18292,
            -25.87271
          ],
          [
            -46.972746,
            -31.92588
          ],
          [
            -46.724705,
            -34.38799
          ],
          [
            -46.141331,
            -37.142933
          ],
          [
            -44.734029,
            -40.649224
          ],
          [
            -43.765865,
            -42.194303
          ],
          [
            -43.091246,
            -42.903268
          ],
          [
            -40.564479,
            -44.559039
          ],
          [
            -38.768951,
            -45.217963
          ],
          [
            -32.299649,
            -46.61081
          ],
          [
            -25.537516,
            -47.322599
          ],
          [
            -12.722214,
            -47.554258
          ],
          [
            20.54517,
            -47.40625
          ],
          [
            29.854181,
            -46.855671
          ],
          [
            34.820784,
            -46.254644
          ],
          [
            36.82438,
            -45.796651
          ],
          [
            40.080223,
            -44.520805
          ],
          [
            41.582919,
            -43.654015
          ],
          [
            42.921157,
            -42.65282
          ],
          [
            44.066934,
            -41.276945
          ],
          [
            45.254227,
            -39.146528
          ],
          [
            46.103592,
            -36.349201
          ],
          [
            46.851333,
            -31.590663
          ],
          [
            47.131412,
            -27.918689
          ],
          [
            47.269441,
            -19.152961
          ],
          [
            47.213481,
            27.222558
          ],
          [
            46.781604,
            32.189163
          ],
          [
            45.724893,
            37.448599
          ],
          [
            44.283953,
            40.231513
          ],
          [
            42.835166,
            42.149801
          ],
          [
            41.625302,
            43.198059
          ],
          [
            40.330671,
            43.96275
          ],
          [
            37.826176,
            44.993418
          ],
          [
            32.316289,
            46.070195
          ],
          [
            22.340699,
            46.712674
          ],
          [
            6.812837,
            47.268209
          ],
          [
            -10.71862,
            47.284476
          ],
          [
            -23.992437,
            46.912896
          ],
          [
            -29.752774,
            46.434608
          ],
          [
            -36.807739,
            45.343107
          ],
          [
            -39.312235,
            44.48023
          ],
          [
            -42.131005,
            43.000869
          ],
          [
            -44.083079,
            41.247725
          ],
          [
            -44.594063,
            40.496377
          ],
          [
            -45.584819,
            38.180291
          ],
          [
            -46.286717,
            34.693655
          ],
          [
            -46.905646,
            30.436018
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "center": [
    0.006436520000000001,
    -0.06820839000000001,
    -0.00016383500000000106
  ],
  "construction_scale": 50.784191713980185,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
