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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -0.573444,
            -12.528118
          ],
          [
            -0.678911,
            -9.659579
          ],
          [
            -0.35747,
            -2.328867
          ],
          [
            -0.596883,
            2.452031
          ],
          [
            -0.494561,
            5.868251
          ],
          [
            0.00556,
            12.970009
          ],
          [
            0.3934,
            13.607462
          ],
          [
            0.791588,
            13.733184
          ],
          [
            1.457721,
            13.288736
          ],
          [
            1.530398,
            12.013829
          ],
          [
            0.992665,
            3.318438
          ],
          [
            0.968691,
            -6.153587
          ],
          [
            0.753643,
            -13.803024
          ],
          [
            0.472857,
            -14.428825
          ],
          [
            0.154134,
            -14.51459
          ],
          [
            -0.290364,
            -14.121751
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 63.63836363636364,
      "loops": [
        [
          [
            -0.215027,
            -14.47263
          ],
          [
            -0.890074,
            -14.121751
          ],
          [
            -1.162168,
            -12.589084
          ],
          [
            -1.406221,
            -9.022126
          ],
          [
            -1.42463,
            -1.372687
          ],
          [
            -1.094803,
            4.364391
          ],
          [
            -0.249309,
            13.288736
          ],
          [
            0.034894,
            13.949443
          ],
          [
            0.791588,
            14.186271
          ],
          [
            1.228566,
            13.92619
          ],
          [
            1.380469,
            13.607462
          ],
          [
            1.465712,
            12.651282
          ],
          [
            0.845186,
            7.870384
          ],
          [
            0.43603,
            2.709791
          ],
          [
            0.381334,
            -4.62092
          ],
          [
            0.556458,
            -12.846844
          ],
          [
            0.344209,
            -14.121751
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.696969696969703,
      "length": 30.305030303030296,
      "loops": [
        [
          [
            0.382301,
            4.508395
          ],
          [
            -0.042652,
            -7.284488
          ],
          [
            0.000957,
            -12.846844
          ],
          [
            -0.118734,
            -13.803024
          ],
          [
            -0.483322,
            -14.216387
          ],
          [
            -0.802046,
            -14.111483
          ],
          [
            -1.159349,
            -13.484297
          ],
          [
            -1.504192,
            -10.471754
          ],
          [
            -1.447098,
            2.914762
          ],
          [
            -1.180916,
            8.651842
          ],
          [
            -0.70958,
            13.607462
          ],
          [
            -0.40763,
            14.244915
          ],
          [
            0.154134,
            14.545738
          ],
          [
            0.791588,
            14.333659
          ],
          [
            1.07172,
            13.607462
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.48695905,
    0.0032222999999999974,
    -0.005329029999999985
  ],
  "construction_scale": 129.2578338325917,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
