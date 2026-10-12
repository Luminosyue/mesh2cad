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
      "length": 9.092909090909094,
      "loops": [
        [
          [
            23.895343,
            -23.647507
          ],
          [
            -25.163286,
            -23.63633
          ],
          [
            -25.569454,
            -23.570681
          ],
          [
            -25.793895,
            -23.239202
          ],
          [
            -25.6899,
            23.499084
          ],
          [
            -24.831809,
            23.675352
          ],
          [
            11.375908,
            23.688611
          ],
          [
            23.895343,
            23.670557
          ],
          [
            24.558298,
            23.502469
          ],
          [
            24.558298,
            -23.405572
          ],
          [
            24.22682,
            -23.641247
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 81.82018181818181,
      "loops": [
        [
          [
            24.590272,
            -23.239202
          ],
          [
            24.527423,
            23.499084
          ],
          [
            24.22682,
            23.655597
          ],
          [
            20.912049,
            23.70159
          ],
          [
            -24.831809,
            23.696578
          ],
          [
            -25.494762,
            23.666899
          ],
          [
            -25.738689,
            23.499084
          ],
          [
            -25.821201,
            -22.907728
          ],
          [
            -25.813881,
            -23.239202
          ],
          [
            -25.594376,
            -23.570681
          ],
          [
            24.22682,
            -23.650373
          ]
        ],
        [
          [
            21.640964,
            21.8417
          ],
          [
            21.575003,
            -21.949269
          ],
          [
            -23.201423,
            -22.073851
          ],
          [
            -23.837378,
            -22.072548
          ],
          [
            -24.165177,
            -21.913296
          ],
          [
            -24.176468,
            21.8417
          ],
          [
            -23.837378,
            22.130058
          ],
          [
            21.243524,
            22.131288
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 40.90909090909091,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            24.507763,
            23.499084
          ],
          [
            24.5583,
            -23.239202
          ],
          [
            24.22682,
            -23.659258
          ],
          [
            -25.541953,
            -23.570681
          ],
          [
            -25.767738,
            -23.239202
          ],
          [
            -25.78579,
            -21.581818
          ],
          [
            -25.724695,
            23.499084
          ],
          [
            -25.494762,
            23.666265
          ],
          [
            -23.676347,
            23.705035
          ],
          [
            12.293641,
            23.705632
          ],
          [
            23.563866,
            23.686388
          ],
          [
            24.22682,
            23.660512
          ]
        ],
        [
          [
            21.660884,
            -21.581818
          ],
          [
            21.575003,
            22.002061
          ],
          [
            21.243524,
            22.138686
          ],
          [
            19.917617,
            22.149928
          ],
          [
            -23.94756,
            22.173175
          ],
          [
            -24.156906,
            21.8417
          ],
          [
            -24.152496,
            -21.913296
          ],
          [
            -23.837378,
            -22.12942
          ],
          [
            21.243524,
            -22.089311
          ],
          [
            21.575003,
            -21.993596
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0002662999999999971,
    -0.21610796499999996,
    -0.027339625000000006
  ],
  "construction_scale": 134.42878272949335,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
