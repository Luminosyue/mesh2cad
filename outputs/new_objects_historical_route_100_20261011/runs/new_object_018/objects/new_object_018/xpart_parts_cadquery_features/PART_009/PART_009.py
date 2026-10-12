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
      "length": 15.153515151515156,
      "loops": [
        [
          [
            13.452797,
            -3.432758
          ],
          [
            8.385849,
            -3.172878
          ],
          [
            -2.281414,
            -3.160532
          ],
          [
            -3.614821,
            -3.235902
          ],
          [
            -4.414866,
            -3.49812
          ],
          [
            -5.21491,
            -3.225951
          ],
          [
            -8.613037,
            -3.233185
          ],
          [
            -12.415312,
            -3.63392
          ],
          [
            -15.615491,
            -3.651414
          ],
          [
            -17.215579,
            -3.603201
          ],
          [
            -17.697854,
            -3.092092
          ],
          [
            -17.482262,
            -2.706543
          ],
          [
            -17.146845,
            -2.533216
          ],
          [
            -13.215356,
            -2.697704
          ],
          [
            -7.812992,
            -2.301821
          ],
          [
            10.321352,
            -2.27556
          ],
          [
            16.652976,
            -2.59205
          ],
          [
            17.041108,
            -1.758684
          ],
          [
            17.029767,
            0.641449
          ],
          [
            17.186339,
            0.938454
          ],
          [
            17.568377,
            0.908129
          ],
          [
            17.724879,
            0.525043
          ],
          [
            17.771486,
            -1.22532
          ],
          [
            17.45302,
            -3.631877
          ],
          [
            16.919657,
            -3.837303
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            5.153326,
            3.381371
          ],
          [
            5.188558,
            3.574946
          ],
          [
            4.918988,
            3.765635
          ],
          [
            4.524512,
            3.574946
          ],
          [
            4.652306,
            3.255528
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -34.848484848484844,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            -5.21491,
            -3.212737
          ],
          [
            -16.757762,
            -3.538617
          ],
          [
            -17.215579,
            -3.492069
          ],
          [
            -17.648073,
            -3.092092
          ],
          [
            -17.627422,
            -2.825413
          ],
          [
            -17.344369,
            -2.558728
          ],
          [
            -16.415536,
            -2.468707
          ],
          [
            6.710213,
            -2.270931
          ],
          [
            16.652976,
            -2.535552
          ],
          [
            16.914158,
            -2.292048
          ],
          [
            17.186339,
            -1.348498
          ],
          [
            17.45302,
            -1.291995
          ],
          [
            17.703579,
            -1.758684
          ],
          [
            17.545796,
            -3.358773
          ],
          [
            17.186339,
            -3.818938
          ],
          [
            16.919657,
            -3.843881
          ],
          [
            9.719256,
            -3.195984
          ],
          [
            -2.890322,
            -3.16662
          ],
          [
            -4.414866,
            -3.465238
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -34.848484848484844,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            5.145999,
            3.308266
          ],
          [
            4.652306,
            3.236239
          ],
          [
            4.542444,
            3.574946
          ],
          [
            4.918988,
            3.693761
          ],
          [
            5.160325,
            3.574946
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            12.64896,
            -3.358773
          ],
          [
            8.652529,
            -3.166566
          ],
          [
            -2.548095,
            -3.146744
          ],
          [
            -3.34814,
            -3.175794
          ],
          [
            -4.414866,
            -3.470554
          ],
          [
            -5.21491,
            -3.181359
          ],
          [
            -16.948897,
            -3.604869
          ],
          [
            -17.482262,
            -3.537345
          ],
          [
            -17.781695,
            -3.092092
          ],
          [
            -17.482262,
            -2.575821
          ],
          [
            -17.215579,
            -2.488252
          ],
          [
            -11.615267,
            -2.55595
          ],
          [
            -7.615044,
            -2.314679
          ],
          [
            9.452575,
            -2.281811
          ],
          [
            16.386294,
            -2.552041
          ],
          [
            16.652976,
            -2.500725
          ],
          [
            17.062273,
            -1.758684
          ],
          [
            17.080787,
            1.441493
          ],
          [
            17.206444,
            1.698192
          ],
          [
            17.61247,
            1.708174
          ],
          [
            17.769434,
            1.174813
          ],
          [
            17.757824,
            -1.492004
          ],
          [
            17.403899,
            -3.625456
          ],
          [
            16.919657,
            -3.844076
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            4.523617,
            3.308266
          ],
          [
            4.918988,
            3.204536
          ],
          [
            5.185669,
            3.305263
          ],
          [
            5.197389,
            3.574946
          ],
          [
            4.652306,
            3.630671
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.606060606060609,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            9.985938,
            -3.189073
          ],
          [
            16.919657,
            -3.831926
          ],
          [
            17.42733,
            -3.625456
          ],
          [
            17.752355,
            -1.492004
          ],
          [
            17.669612,
            1.441493
          ],
          [
            17.45302,
            1.601614
          ],
          [
            17.108927,
            1.441493
          ],
          [
            17.057961,
            -1.758684
          ],
          [
            16.824669,
            -2.310767
          ],
          [
            16.386294,
            -2.546897
          ],
          [
            9.185893,
            -2.285352
          ],
          [
            -5.481592,
            -2.284691
          ],
          [
            -13.215356,
            -2.581455
          ],
          [
            -17.215579,
            -2.426938
          ],
          [
            -17.524789,
            -2.558728
          ],
          [
            -17.631994,
            -2.825413
          ],
          [
            -17.544692,
            -3.092092
          ],
          [
            -17.215579,
            -3.32147
          ],
          [
            -16.682217,
            -3.361365
          ],
          [
            -9.215134,
            -3.362166
          ],
          [
            -5.21491,
            -3.203421
          ],
          [
            -4.414866,
            -3.452701
          ],
          [
            -3.081458,
            -3.159251
          ],
          [
            5.208789,
            -3.16042
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.606060606060609,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            4.585317,
            3.579286
          ],
          [
            5.185669,
            3.591435
          ],
          [
            5.188494,
            3.308266
          ],
          [
            4.652306,
            3.237147
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
            10.252618,
            -3.147775
          ],
          [
            16.919657,
            -3.628958
          ],
          [
            17.360278,
            -3.358773
          ],
          [
            17.37221,
            -2.825413
          ],
          [
            17.186339,
            -2.456371
          ],
          [
            16.919657,
            -2.407221
          ],
          [
            16.386294,
            -2.677863
          ],
          [
            10.519301,
            -2.291743
          ],
          [
            10.252618,
            -2.306058
          ],
          [
            10.018156,
            -2.558728
          ],
          [
            10.012448,
            -2.825413
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.018589090000000003,
    -0.04301667000000001,
    -0.464573615
  ],
  "construction_scale": 108.15124467049593,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
