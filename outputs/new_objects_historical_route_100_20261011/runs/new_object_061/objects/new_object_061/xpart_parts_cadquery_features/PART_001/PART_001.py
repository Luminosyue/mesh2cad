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
            13.314559,
            2.844508
          ],
          [
            -9.169012,
            2.912215
          ],
          [
            -12.78969,
            2.844423
          ],
          [
            -13.14307,
            2.562409
          ],
          [
            -12.900192,
            2.279188
          ],
          [
            -26.968265,
            2.225833
          ],
          [
            -27.447797,
            1.998389
          ],
          [
            -27.491748,
            1.716374
          ],
          [
            -27.475375,
            -2.23179
          ],
          [
            -27.250277,
            -2.74081
          ],
          [
            -26.968265,
            -2.839726
          ],
          [
            -21.328031,
            -2.596605
          ],
          [
            -7.227444,
            -2.482347
          ],
          [
            -1.305197,
            -2.514858
          ],
          [
            6.873144,
            -2.805122
          ],
          [
            23.262338,
            -2.806583
          ],
          [
            26.928491,
            -2.932096
          ],
          [
            27.409282,
            -2.795811
          ],
          [
            27.929536,
            -2.23179
          ],
          [
            27.705575,
            -0.539721
          ],
          [
            27.700255,
            1.998389
          ],
          [
            27.460001,
            2.333332
          ],
          [
            14.20545,
            2.411941
          ],
          [
            13.239388,
            2.562409
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 66.66866666666665,
      "loops": [
        [
          [
            27.460001,
            2.958935
          ],
          [
            -21.610042,
            2.841802
          ],
          [
            -23.302113,
            2.612501
          ],
          [
            -23.419959,
            2.290606
          ],
          [
            -27.250277,
            2.260576
          ],
          [
            -27.947819,
            1.998389
          ],
          [
            -28.195333,
            -1.186908
          ],
          [
            -28.151391,
            -2.5138
          ],
          [
            -27.811327,
            -2.796101
          ],
          [
            -26.603086,
            -2.89245
          ],
          [
            26.895977,
            -2.908095
          ],
          [
            28.024025,
            -2.474668
          ],
          [
            28.154719,
            -2.23179
          ],
          [
            28.1221,
            1.998389
          ],
          [
            27.812572,
            2.844423
          ]
        ],
        [
          [
            23.229824,
            -2.670168
          ],
          [
            13.060782,
            -2.5138
          ],
          [
            22.748969,
            -2.34204
          ],
          [
            25.791231,
            -2.5138
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.72727272727272,
      "length": 27.27472727272728,
      "loops": [
        [
          [
            22.101778,
            -2.409603
          ],
          [
            -18.507914,
            -2.391768
          ],
          [
            -22.738089,
            -2.475269
          ],
          [
            -26.900977,
            -2.866967
          ],
          [
            -27.814301,
            -2.734449
          ],
          [
            -28.084475,
            -2.5138
          ],
          [
            -28.120351,
            -2.23179
          ],
          [
            -27.633574,
            -1.385755
          ],
          [
            -27.500006,
            1.998389
          ],
          [
            -27.250277,
            2.217548
          ],
          [
            -2.997267,
            2.39101
          ],
          [
            -1.434151,
            2.562409
          ],
          [
            -1.820837,
            2.844423
          ],
          [
            1.864221,
            2.881697
          ],
          [
            5.771948,
            2.844423
          ],
          [
            5.641915,
            2.562409
          ],
          [
            7.222444,
            2.468903
          ],
          [
            20.476997,
            2.3825
          ],
          [
            23.511837,
            2.496723
          ],
          [
            23.923187,
            2.562409
          ],
          [
            24.153678,
            2.844423
          ],
          [
            25.767932,
            2.911938
          ],
          [
            27.460001,
            2.816854
          ],
          [
            28.078157,
            2.280399
          ],
          [
            28.028578,
            -1.949776
          ],
          [
            27.742014,
            -2.536244
          ],
          [
            27.17799,
            -2.82881
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.72727272727272,
      "length": 27.27472727272728,
      "loops": [
        [
          [
            19.707419,
            -2.795811
          ],
          [
            5.248362,
            -2.84248
          ],
          [
            0.572443,
            -2.795811
          ],
          [
            8.914515,
            -2.520709
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.473224985,
    9.916500000001216e-05,
    -0.0009168800000000088
  ],
  "construction_scale": 114.3683274301168,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
