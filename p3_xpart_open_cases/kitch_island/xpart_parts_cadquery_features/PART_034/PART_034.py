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
      "length": 48.48684848484849,
      "loops": [
        [
          [
            1.481056,
            -2.596002
          ],
          [
            1.545443,
            4.205495
          ],
          [
            1.158094,
            4.666295
          ],
          [
            0.186449,
            4.562423
          ],
          [
            -0.079871,
            4.205495
          ],
          [
            -0.120555,
            3.23385
          ],
          [
            -0.082505,
            -1.624362
          ],
          [
            -0.01907,
            -2.596002
          ],
          [
            0.186449,
            -2.823211
          ],
          [
            1.158094,
            -2.916288
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.5151515151515156,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            0.186449,
            -2.834905
          ],
          [
            -0.042001,
            -2.596002
          ],
          [
            -0.132891,
            -1.624362
          ],
          [
            -0.113458,
            4.205495
          ],
          [
            0.186449,
            4.598713
          ],
          [
            1.158094,
            4.626969
          ],
          [
            1.543386,
            4.205495
          ],
          [
            1.62437,
            3.23385
          ],
          [
            1.537376,
            -1.665843
          ],
          [
            1.382804,
            -2.596002
          ],
          [
            1.158094,
            -2.819625
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 9.092909090909087,
      "loops": [
        [
          [
            2.129738,
            -4.64641
          ],
          [
            2.733334,
            -3.567647
          ],
          [
            2.620153,
            4.205495
          ],
          [
            2.129738,
            4.61912
          ],
          [
            1.158094,
            4.406238
          ],
          [
            0.186449,
            4.628315
          ],
          [
            -0.149797,
            4.205495
          ],
          [
            -0.320325,
            -1.624362
          ],
          [
            -0.231973,
            -2.596002
          ],
          [
            0.186449,
            -3.312254
          ],
          [
            0.906344,
            -3.567647
          ],
          [
            0.904367,
            -4.539288
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.636363636363633,
      "length": 15.15351515151515,
      "loops": [
        [
          [
            0.186449,
            -3.05477
          ],
          [
            1.158094,
            -2.810869
          ],
          [
            1.302071,
            -3.567647
          ],
          [
            2.129738,
            -4.342466
          ],
          [
            2.764473,
            -3.567647
          ],
          [
            2.640335,
            4.205495
          ],
          [
            2.129738,
            4.601377
          ],
          [
            1.158094,
            4.454505
          ],
          [
            0.186449,
            4.592452
          ],
          [
            -0.12181,
            4.205495
          ],
          [
            -0.174922,
            -2.596002
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.787878787878782,
      "length": 21.214121212121217,
      "loops": [
        [
          [
            2.670096,
            2.26221
          ],
          [
            2.533559,
            4.205495
          ],
          [
            2.129738,
            4.547078
          ],
          [
            0.186449,
            4.521508
          ],
          [
            -0.066853,
            4.205495
          ],
          [
            -0.127071,
            3.23385
          ],
          [
            -0.097771,
            -2.596002
          ],
          [
            0.186449,
            -3.097195
          ],
          [
            1.158094,
            -3.003705
          ],
          [
            1.474074,
            -3.567647
          ],
          [
            2.129738,
            -4.016912
          ],
          [
            2.64769,
            -3.567647
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.958630965,
    0.558969585,
    -0.0015922800000000015
  ],
  "construction_scale": 98.51108183668237,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
