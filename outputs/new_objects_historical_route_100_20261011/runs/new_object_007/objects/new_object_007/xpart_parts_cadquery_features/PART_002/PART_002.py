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
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            1.036151,
            28.70247
          ],
          [
            0.990159,
            -39.88919
          ],
          [
            0.81943,
            -40.61419
          ],
          [
            0.554528,
            -40.884852
          ],
          [
            0.179711,
            -41.03458
          ],
          [
            -1.31956,
            -41.039259
          ],
          [
            -1.694378,
            -40.954325
          ],
          [
            -2.000681,
            -40.638826
          ],
          [
            -2.063152,
            -40.26401
          ],
          [
            -2.068833,
            -31.643198
          ],
          [
            -2.058163,
            38.822549
          ],
          [
            -1.694378,
            39.34892
          ],
          [
            -1.31956,
            39.422685
          ],
          [
            0.554528,
            39.462473
          ],
          [
            0.929346,
            39.160259
          ],
          [
            1.075032,
            38.447733
          ],
          [
            1.29177,
            30.576557
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 87.88078787878787,
      "loops": [
        [
          [
            -1.752493,
            -35.766195
          ],
          [
            -1.946149,
            -0.908138
          ],
          [
            -1.930839,
            3.214857
          ],
          [
            -1.757937,
            4.339312
          ],
          [
            -1.787485,
            31.326194
          ],
          [
            -1.802972,
            33.575099
          ],
          [
            -1.998183,
            34.699552
          ],
          [
            -2.008242,
            38.822549
          ],
          [
            -1.694378,
            39.284564
          ],
          [
            -1.31956,
            39.425184
          ],
          [
            0.179711,
            39.490399
          ],
          [
            0.554528,
            39.464829
          ],
          [
            0.878004,
            39.197367
          ],
          [
            1.018562,
            38.822549
          ],
          [
            1.014928,
            35.977451
          ],
          [
            0.999568,
            35.449189
          ],
          [
            0.594821,
            34.259788
          ],
          [
            -0.197906,
            33.200284
          ],
          [
            -0.247088,
            32.825465
          ],
          [
            -0.217553,
            4.339312
          ],
          [
            0.852973,
            2.840039
          ],
          [
            1.125015,
            0.965951
          ],
          [
            1.558278,
            -0.158503
          ],
          [
            1.778166,
            -1.504331
          ],
          [
            1.678982,
            -2.067704
          ],
          [
            0.554528,
            -2.887199
          ],
          [
            0.050825,
            -3.531863
          ],
          [
            -0.204442,
            -6.155589
          ],
          [
            -0.20292,
            -35.391376
          ],
          [
            -0.142014,
            -35.766195
          ],
          [
            0.554528,
            -36.584988
          ],
          [
            1.010364,
            -38.389919
          ],
          [
            0.929024,
            -40.26401
          ],
          [
            0.554528,
            -40.709853
          ],
          [
            -0.195107,
            -40.958038
          ],
          [
            -1.31956,
            -40.941762
          ],
          [
            -1.877728,
            -40.638826
          ],
          [
            -2.038014,
            -40.26401
          ],
          [
            -1.97683,
            -36.515829
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
            -2.028394,
            38.822549
          ],
          [
            -2.012275,
            -40.26401
          ],
          [
            -1.694378,
            -40.848378
          ],
          [
            -1.31956,
            -40.985441
          ],
          [
            0.007125,
            -40.97507
          ],
          [
            0.554528,
            -40.864597
          ],
          [
            0.985544,
            -40.26401
          ],
          [
            1.105065,
            -36.890648
          ],
          [
            0.960074,
            -33.142471
          ],
          [
            0.964985,
            -3.157045
          ],
          [
            1.099862,
            -0.360735
          ],
          [
            0.973062,
            3.408074
          ],
          [
            0.970604,
            30.046076
          ],
          [
            1.155643,
            35.996593
          ],
          [
            1.129415,
            38.822549
          ],
          [
            0.929346,
            39.435368
          ],
          [
            0.554528,
            39.662386
          ],
          [
            -1.694378,
            39.422916
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.005974384999999999,
    -0.14728712,
    0.006215195000000001
  ],
  "construction_scale": 152.0053226183768,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
