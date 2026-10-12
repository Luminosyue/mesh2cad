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
      "start": -47.83350317098849,
      "length": 5.7999137244890795,
      "loops": [
        [
          [
            0.567065,
            -49.374767
          ],
          [
            0.561535,
            48.768965
          ],
          [
            0.507262,
            49.747505
          ],
          [
            0.292352,
            49.96293
          ],
          [
            -0.002656,
            49.975095
          ],
          [
            -0.467789,
            49.747505
          ],
          [
            -0.551023,
            48.27247
          ],
          [
            -0.565043,
            -49.374767
          ],
          [
            -0.4447,
            -49.669772
          ],
          [
            -0.297662,
            -49.809021
          ],
          [
            0.292352,
            -49.789846
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -42.03550278662625,
      "length": 84.07291891337934,
      "loops": [
        [
          [
            -0.563159,
            -46.719707
          ],
          [
            -0.523405,
            -49.374767
          ],
          [
            -0.297662,
            -49.813608
          ],
          [
            -0.002656,
            -49.897048
          ],
          [
            0.422651,
            -49.669772
          ],
          [
            0.553968,
            -49.374767
          ],
          [
            0.569259,
            -47.783509
          ],
          [
            0.546288,
            -44.949663
          ],
          [
            -0.002656,
            -44.441924
          ],
          [
            -0.387265,
            -44.949663
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -42.03550278662625,
      "length": 84.07291891337934,
      "loops": [
        [
          [
            -0.428892,
            45.91242
          ],
          [
            -0.477138,
            49.747505
          ],
          [
            -0.297662,
            49.920546
          ],
          [
            0.292352,
            49.942776
          ],
          [
            0.511107,
            49.747505
          ],
          [
            0.551192,
            49.452499
          ],
          [
            0.543893,
            45.91242
          ],
          [
            0.336656,
            45.545801
          ],
          [
            -0.002656,
            45.346357
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 42.03550278662625,
      "length": 5.7999137244890795,
      "loops": [
        [
          [
            0.297382,
            6.077974
          ],
          [
            -0.002656,
            38.562754
          ],
          [
            -0.319683,
            -44.359653
          ],
          [
            -0.530722,
            -46.424698
          ],
          [
            -0.534628,
            -48.691324
          ],
          [
            -0.357231,
            -49.669772
          ],
          [
            -0.002656,
            -49.815343
          ],
          [
            0.412252,
            -49.669772
          ],
          [
            0.565816,
            -48.784753
          ],
          [
            0.427032,
            -44.359653
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 42.03550278662625,
      "length": 5.7999137244890795,
      "loops": [
        [
          [
            -0.550368,
            48.070893
          ],
          [
            -0.442817,
            49.747505
          ],
          [
            0.292352,
            49.920187
          ],
          [
            0.549176,
            49.452499
          ],
          [
            0.545313,
            45.91242
          ],
          [
            0.402734,
            45.523982
          ],
          [
            -0.002656,
            45.134107
          ],
          [
            -0.419344,
            45.91242
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.00042762499999998704,
    0.182515095,
    -0.116543285
  ],
  "construction_scale": 59.819192781029386,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
