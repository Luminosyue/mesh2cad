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
      "start": -1.3234821006588766,
      "length": 1.68448470375896,
      "loops": [
        [
          [
            -33.774784,
            -49.989956
          ],
          [
            33.115459,
            -49.990716
          ],
          [
            33.773052,
            -49.987782
          ],
          [
            34.161523,
            -49.801238
          ],
          [
            34.258997,
            47.904628
          ],
          [
            34.248254,
            49.54832
          ],
          [
            34.01958,
            49.936447
          ],
          [
            -33.692804,
            49.990009
          ],
          [
            -34.147048,
            49.794846
          ],
          [
            -34.263576,
            46.096971
          ],
          [
            -34.234488,
            -49.554711
          ],
          [
            -34.021312,
            -49.918556
          ]
        ],
        [
          [
            -28.844286,
            45.92973
          ],
          [
            29.255392,
            45.850447
          ],
          [
            29.314589,
            -45.610314
          ],
          [
            29.089079,
            -45.834967
          ],
          [
            -28.02273,
            -45.861863
          ],
          [
            -29.090812,
            -45.838178
          ],
          [
            -29.333049,
            -45.610314
          ],
          [
            -29.384599,
            45.603923
          ],
          [
            -29.282623,
            45.850447
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.3609496638160572,
      "length": 0.9625853761268458,
      "loops": [
        [
          [
            34.181306,
            49.301796
          ],
          [
            34.178583,
            -49.00325
          ],
          [
            34.049521,
            -49.801238
          ],
          [
            31.242134,
            -49.924126
          ],
          [
            -34.021312,
            -49.822893
          ],
          [
            -34.168331,
            -49.247347
          ],
          [
            -34.18007,
            -17.318356
          ],
          [
            -34.181959,
            48.127703
          ],
          [
            -34.051944,
            49.794846
          ],
          [
            -33.774784,
            49.914308
          ],
          [
            -31.309537,
            49.91922
          ],
          [
            33.773052,
            49.914289
          ],
          [
            34.065023,
            49.794846
          ]
        ],
        [
          [
            27.703105,
            -46.031116
          ],
          [
            -30.119845,
            -45.926346
          ],
          [
            -30.379494,
            -45.668728
          ],
          [
            -30.414023,
            -45.177578
          ],
          [
            -30.354353,
            45.891264
          ],
          [
            -29.937481,
            46.038263
          ],
          [
            -22.434639,
            46.047903
          ],
          [
            28.59603,
            46.045815
          ],
          [
            30.321705,
            45.910801
          ],
          [
            30.364281,
            -45.658441
          ],
          [
            30.075179,
            -45.929091
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    8.664999999991041e-06,
    3.196499999996716e-05,
    1.7704999999999804e-05
  ],
  "construction_scale": 99.97685435844748,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
