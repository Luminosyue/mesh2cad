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
      "start": -28.806516502422383,
      "length": 5.238700715645985,
      "loops": [
        [
          [
            2.816441,
            -47.428505
          ],
          [
            2.807035,
            48.038306
          ],
          [
            2.74691,
            49.553655
          ],
          [
            2.482152,
            49.892164
          ],
          [
            9.3e-05,
            49.589804
          ],
          [
            -2.456661,
            49.553655
          ],
          [
            -2.569002,
            49.186529
          ],
          [
            -2.537873,
            48.038306
          ],
          [
            -0.043425,
            47.972342
          ],
          [
            0.120551,
            47.882483
          ],
          [
            0.33852,
            47.028076
          ],
          [
            0.306328,
            -42.882464
          ],
          [
            0.211872,
            -47.428505
          ],
          [
            -0.043425,
            -47.683882
          ],
          [
            -0.419715,
            -47.750199
          ],
          [
            -2.893647,
            -47.933618
          ],
          [
            -2.694089,
            -49.448967
          ],
          [
            -2.569002,
            -49.562839
          ],
          [
            -0.382182,
            -49.623831
          ],
          [
            0.371082,
            -49.954079
          ],
          [
            0.83798,
            -49.967907
          ],
          [
            25.768775,
            -49.954079
          ],
          [
            26.12527,
            -49.448967
          ],
          [
            26.129138,
            -48.438734
          ],
          [
            26.095493,
            -47.933618
          ],
          [
            25.71746,
            -47.635158
          ],
          [
            3.492383,
            -47.627032
          ],
          [
            2.987267,
            -47.597391
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.806516502422383,
      "length": 5.238700715645985,
      "loops": [
        [
          [
            -4.084348,
            -47.878884
          ],
          [
            -25.80431,
            -47.931389
          ],
          [
            -25.805096,
            -49.448967
          ],
          [
            -4.165156,
            -49.519724
          ],
          [
            -3.561477,
            -49.448967
          ],
          [
            -3.284303,
            -48.143803
          ],
          [
            -3.323575,
            -47.933618
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -23.568968047436496,
      "length": 47.13908835553308,
      "loops": [
        [
          [
            2.739711,
            -49.448967
          ],
          [
            2.802565,
            49.553655
          ],
          [
            2.482152,
            49.971982
          ],
          [
            -2.063887,
            49.978561
          ],
          [
            -2.569002,
            49.931229
          ],
          [
            -2.839291,
            49.553655
          ],
          [
            -2.841674,
            48.038306
          ],
          [
            -2.575416,
            47.533193
          ],
          [
            -0.043425,
            47.478844
          ],
          [
            0.343051,
            47.028076
          ],
          [
            0.311965,
            -44.414227
          ],
          [
            0.296872,
            -46.923388
          ],
          [
            0.05525,
            -47.428505
          ],
          [
            -2.569002,
            -47.509768
          ],
          [
            -2.919834,
            -47.933618
          ],
          [
            -2.924454,
            -49.448967
          ],
          [
            -2.569002,
            -49.943848
          ],
          [
            1.977036,
            -49.985743
          ],
          [
            2.482152,
            -49.907754
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 23.568968047436492,
      "length": 5.238700715645988,
      "loops": [
        [
          [
            0.297951,
            -46.923388
          ],
          [
            0.334803,
            47.028076
          ],
          [
            -0.043425,
            47.476765
          ],
          [
            -2.571517,
            47.533193
          ],
          [
            -2.83607,
            48.038306
          ],
          [
            -2.836063,
            49.553655
          ],
          [
            -2.569002,
            49.928906
          ],
          [
            -2.063887,
            49.978364
          ],
          [
            2.482152,
            49.970114
          ],
          [
            2.797382,
            49.553655
          ],
          [
            2.741812,
            -49.448967
          ],
          [
            2.482152,
            -49.903172
          ],
          [
            1.977036,
            -49.98112
          ],
          [
            -25.299195,
            -49.945885
          ],
          [
            -25.80431,
            -49.937787
          ],
          [
            -25.975404,
            -49.691139
          ],
          [
            -26.128154,
            -49.448967
          ],
          [
            -26.117387,
            -47.933618
          ],
          [
            -25.80431,
            -47.58445
          ],
          [
            -3.074118,
            -47.574321
          ],
          [
            0.080601,
            -47.428505
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0010221100000000205,
    0.05030380499999998,
    0.0008479550000000113
  ],
  "construction_scale": 51.2117000626186,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
