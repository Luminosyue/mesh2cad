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
      "start": -22.573608465987384,
      "length": 45.14721693197477,
      "loops": [
        [
          [
            37.304836,
            -48.708569
          ],
          [
            37.304836,
            49.365649
          ],
          [
            35.827923,
            49.537689
          ],
          [
            22.535708,
            49.659771
          ],
          [
            16.409798,
            49.978893
          ],
          [
            14.166534,
            49.68259
          ],
          [
            11.486754,
            49.638519
          ],
          [
            -36.540811,
            49.529097
          ],
          [
            -36.794511,
            49.263214
          ],
          [
            -36.812029,
            48.004558
          ],
          [
            -36.817767,
            -47.502481
          ],
          [
            -36.641626,
            -48.70535
          ],
          [
            -33.805244,
            -48.888302
          ],
          [
            -26.694724,
            -48.858396
          ],
          [
            -25.710117,
            -49.63608
          ],
          [
            -25.217811,
            -49.649455
          ],
          [
            -21.771682,
            -49.638626
          ],
          [
            -20.787073,
            -48.913929
          ],
          [
            -19.802465,
            -48.825189
          ],
          [
            -18.841286,
            -49.197651
          ],
          [
            -18.609367,
            -49.689956
          ],
          [
            -17.833247,
            -49.849092
          ],
          [
            -14.387117,
            -49.729512
          ],
          [
            -13.894812,
            -48.927039
          ],
          [
            -13.402508,
            -48.767283
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    0.004372779999999993,
    0.12056905499999998,
    0.009206535000000016
  ],
  "construction_scale": 49.91283447195573,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
