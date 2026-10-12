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
      "start": -27.98534624846887,
      "length": 42.40315918425731,
      "loops": [
        [
          [
            0.972101,
            49.332331
          ],
          [
            0.967655,
            -49.612702
          ],
          [
            0.710117,
            -49.950565
          ],
          [
            -0.548726,
            -49.962247
          ],
          [
            -0.831369,
            -49.864473
          ],
          [
            -0.960327,
            -49.612702
          ],
          [
            -0.971942,
            -49.109168
          ],
          [
            -0.966323,
            49.584102
          ],
          [
            -0.800495,
            49.894184
          ],
          [
            -0.548726,
            49.96452
          ],
          [
            0.458347,
            49.980775
          ],
          [
            0.875876,
            49.835869
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.416693521938502,
      "length": 10.177608958747715,
      "loops": [
        [
          [
            0.973026,
            -49.612702
          ],
          [
            0.952932,
            -18.896942
          ],
          [
            0.710117,
            -18.579373
          ],
          [
            -0.548726,
            -18.534536
          ],
          [
            -0.849238,
            -18.645172
          ],
          [
            -0.976627,
            -19.387008
          ],
          [
            -0.96629,
            -49.612702
          ],
          [
            -0.802678,
            -49.899962
          ],
          [
            -0.548726,
            -49.976357
          ],
          [
            0.710117,
            -49.96488
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.416693521938502,
      "length": 10.177608958747715,
      "loops": [
        [
          [
            -0.800495,
            49.861848
          ],
          [
            0.710117,
            49.905859
          ],
          [
            0.977326,
            49.584102
          ],
          [
            0.981675,
            20.630718
          ],
          [
            0.710117,
            20.140466
          ],
          [
            0.458347,
            20.112582
          ],
          [
            -0.800495,
            20.177417
          ],
          [
            -0.985927,
            20.630718
          ],
          [
            -0.970514,
            49.584102
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 24.59318306683628,
      "length": 3.3932825954825288,
      "loops": [
        [
          [
            0.979921,
            -49.466635
          ],
          [
            0.976542,
            49.584102
          ],
          [
            0.710117,
            49.90821
          ],
          [
            -0.548726,
            49.922498
          ],
          [
            -0.837664,
            49.835869
          ],
          [
            -0.975331,
            49.4784
          ],
          [
            -1.00602,
            7.433053
          ],
          [
            -0.966772,
            -49.360934
          ],
          [
            -0.843585,
            -49.864473
          ],
          [
            -0.548726,
            -49.980401
          ],
          [
            0.710117,
            -49.973776
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0023257550000000127,
    0.0009118200000000076,
    0.12126777999999999
  ],
  "construction_scale": 102.10335880128042,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
