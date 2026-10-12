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
  "operation": "extrude",
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
      "start": -22.801338195738623,
      "length": 45.602676391477246,
      "loops": [
        [
          [
            38.041611,
            -32.158902
          ],
          [
            38.125734,
            31.199306
          ],
          [
            38.043151,
            32.620051
          ],
          [
            37.705638,
            33.217092
          ],
          [
            36.873825,
            33.522962
          ],
          [
            35.381222,
            33.601547
          ],
          [
            -46.043021,
            33.610238
          ],
          [
            -48.204521,
            33.555277
          ],
          [
            -49.400955,
            33.217092
          ],
          [
            -49.787316,
            32.32153
          ],
          [
            -49.870798,
            31.199306
          ],
          [
            -49.953023,
            16.5718
          ],
          [
            -49.904471,
            -30.964818
          ],
          [
            -49.713825,
            -32.755941
          ],
          [
            -49.398606,
            -33.221513
          ],
          [
            -47.834143,
            -33.553001
          ],
          [
            36.276786,
            -33.539974
          ],
          [
            37.470865,
            -33.363117
          ],
          [
            37.841788,
            -33.054464
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.801338195738623,
      "length": 45.602676391477246,
      "loops": [
        [
          [
            38.886399,
            -32.684083
          ],
          [
            39.26199,
            -33.312352
          ],
          [
            39.85903,
            -33.509535
          ],
          [
            47.919085,
            -33.545546
          ],
          [
            49.113165,
            -33.102842
          ],
          [
            49.429954,
            -32.158902
          ],
          [
            49.468932,
            31.724489
          ],
          [
            49.113165,
            33.213462
          ],
          [
            48.217603,
            33.539556
          ],
          [
            40.157551,
            33.534393
          ],
          [
            39.26199,
            33.147706
          ],
          [
            38.819896,
            32.02301
          ],
          [
            38.395106,
            -10.665423
          ],
          [
            38.66505,
            -31.263337
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.07526155500000001,
    -0.183142375,
    -0.026530465000000003
  ],
  "construction_scale": 121.06336881656284,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
