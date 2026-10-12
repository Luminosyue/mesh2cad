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
      "start": -50.00000000000001,
      "length": 51.517151515151525,
      "loops": [
        [
          [
            1.570749,
            -3.046978
          ],
          [
            2.336182,
            -2.912961
          ],
          [
            2.938614,
            -2.434636
          ],
          [
            3.18741,
            -1.669203
          ],
          [
            2.849905,
            -0.903768
          ],
          [
            2.336182,
            -0.498075
          ],
          [
            1.188031,
            -0.363567
          ],
          [
            0.853101,
            -0.138335
          ],
          [
            1.009036,
            0.244383
          ],
          [
            0.8528,
            0.6271
          ],
          [
            -1.401075,
            2.540683
          ],
          [
            -2.25642,
            3.000613
          ],
          [
            -3.021855,
            2.986023
          ],
          [
            -3.173259,
            2.540683
          ],
          [
            -3.021855,
            2.370336
          ],
          [
            0.798128,
            -0.514702
          ],
          [
            0.196783,
            -1.286485
          ],
          [
            0.233609,
            -2.051918
          ],
          [
            0.805313,
            -2.774985
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5151515151515156,
      "length": 48.486848484848494,
      "loops": [
        [
          [
            1.570749,
            -3.038925
          ],
          [
            2.336182,
            -2.91331
          ],
          [
            2.718899,
            -2.65205
          ],
          [
            3.101617,
            -2.122866
          ],
          [
            3.179124,
            -1.669203
          ],
          [
            2.718899,
            -0.764893
          ],
          [
            2.336182,
            -0.496735
          ],
          [
            1.570749,
            -0.343465
          ],
          [
            0.983307,
            -0.52105
          ],
          [
            0.484597,
            -0.903768
          ],
          [
            0.16827,
            -1.669203
          ],
          [
            0.474225,
            -2.434636
          ],
          [
            0.903341,
            -2.817354
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0004263600000000145,
    0.477855245,
    0.36672396500000004
  ],
  "construction_scale": 77.60437889847537,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
