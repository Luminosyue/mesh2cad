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
      "start": -49.99999999999999,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            2.848638,
            -0.381455
          ],
          [
            -2.038068,
            -0.601163
          ],
          [
            -2.715393,
            -0.279699
          ],
          [
            -2.84591,
            0.212463
          ],
          [
            -2.715393,
            0.552037
          ],
          [
            -2.376734,
            0.768412
          ],
          [
            -0.876644,
            0.580223
          ],
          [
            2.364535,
            0.759575
          ],
          [
            2.848638,
            0.694175
          ],
          [
            3.237882,
            0.405686
          ],
          [
            3.298738,
            0.067024
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.666666666666664,
      "length": 66.66866666666665,
      "loops": [
        [
          [
            -3.054054,
            0.812676
          ],
          [
            -3.4835,
            0.405686
          ],
          [
            -3.392719,
            -0.169556
          ],
          [
            -2.715393,
            -0.598058
          ],
          [
            -2.038068,
            -0.727251
          ],
          [
            -0.891084,
            -0.412718
          ],
          [
            1.818212,
            -0.579473
          ],
          [
            3.041861,
            -0.318525
          ],
          [
            3.390808,
            0.067024
          ],
          [
            3.3058,
            0.405686
          ],
          [
            2.7032,
            0.678633
          ],
          [
            -1.022082,
            0.460248
          ],
          [
            -2.376734,
            0.869877
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.473393105,
    -0.0004880050000000001,
    0.0014680049999999945
  ],
  "construction_scale": 137.3425396967666,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
