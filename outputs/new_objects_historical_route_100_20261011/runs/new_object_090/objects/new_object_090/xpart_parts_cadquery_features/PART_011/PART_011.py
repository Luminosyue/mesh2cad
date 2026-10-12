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
      "length": 90.9110909090909,
      "loops": [
        [
          [
            -2.124801,
            0.218259
          ],
          [
            -1.997593,
            -0.794657
          ],
          [
            -1.519551,
            -1.067188
          ],
          [
            1.519201,
            -1.060364
          ],
          [
            1.85684,
            -0.924465
          ],
          [
            2.117782,
            -0.457015
          ],
          [
            2.105844,
            0.555903
          ],
          [
            1.85684,
            0.930766
          ],
          [
            1.519201,
            1.077497
          ],
          [
            -1.519551,
            1.065083
          ],
          [
            -1.885552,
            0.89354
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 40.90909090909091,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            1.930243,
            0.845785
          ],
          [
            2.089647,
            0.555903
          ],
          [
            2.098014,
            -0.457015
          ],
          [
            1.973868,
            -0.794657
          ],
          [
            1.566957,
            -1.042078
          ],
          [
            -1.519551,
            -1.066737
          ],
          [
            -2.002051,
            -0.794657
          ],
          [
            -2.100243,
            0.555903
          ],
          [
            -1.85719,
            0.92401
          ],
          [
            -1.519551,
            1.070504
          ],
          [
            1.519201,
            1.089648
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.49229223499999997,
    -0.0036572849999999824,
    0.23302129500000002
  ],
  "construction_scale": 136.92771319011655,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
