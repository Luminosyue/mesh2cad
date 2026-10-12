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
      -0.004361337314357753,
      0.07971129351468854,
      -0.9968084512197143
    ],
    [
      0.9999903495611232,
      -0.00017936944757813286,
      -0.004389602627132614
    ],
    [
      -0.0005286978846607094,
      -0.9968179761184168,
      -0.07970974197505809
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -9.837583960483274,
      "length": 19.570833481503577,
      "loops": [
        [
          [
            0.330245,
            -9.677071
          ],
          [
            0.473856,
            -49.215369
          ],
          [
            0.26751,
            -49.713614
          ],
          [
            -0.347057,
            -49.931828
          ],
          [
            -0.567488,
            -49.717256
          ],
          [
            -0.100606,
            -49.247158
          ],
          [
            -0.065153,
            -48.969048
          ],
          [
            -0.208445,
            3.500221
          ],
          [
            -0.011205,
            49.008145
          ],
          [
            -0.035491,
            49.266007
          ],
          [
            -0.633708,
            49.751447
          ],
          [
            -0.288185,
            49.998821
          ],
          [
            0.250787,
            49.755305
          ],
          [
            0.505044,
            49.259068
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 4,
  "center": [
    -0.0001957650000000144,
    -0.04480613,
    -0.01304254
  ],
  "construction_scale": 100.84679744808793,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
