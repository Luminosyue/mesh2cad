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
      6.516669359332571e-05,
      0.00840319516949452,
      -0.999964690408739
    ],
    [
      1.1095274707066593e-05,
      -0.9999646924765386,
      -0.008403194463803507
    ],
    [
      -0.9999999978150984,
      -1.0547274538623955e-05,
      -6.525762847758539e-05
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.0003211136273,
      "length": 99.99999978150984,
      "loops": [
        [
          [
            -4.135625,
            -1.336707
          ],
          [
            -5.524605,
            -1.192085
          ],
          [
            -6.16347,
            -0.714207
          ],
          [
            -6.259681,
            0.283027
          ],
          [
            -5.87455,
            0.862252
          ],
          [
            -5.211624,
            1.152175
          ],
          [
            -4.21455,
            1.267336
          ],
          [
            4.102216,
            1.297924
          ],
          [
            5.76875,
            0.925511
          ],
          [
            6.103958,
            0.624849
          ],
          [
            6.289294,
            0.055801
          ],
          [
            6.113962,
            -0.565585
          ],
          [
            5.783836,
            -0.869633
          ],
          [
            4.456082,
            -1.222885
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.11920548999999997,
    -0.029546125,
    -0.220130835
  ],
  "construction_scale": 67.45608726767027,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
