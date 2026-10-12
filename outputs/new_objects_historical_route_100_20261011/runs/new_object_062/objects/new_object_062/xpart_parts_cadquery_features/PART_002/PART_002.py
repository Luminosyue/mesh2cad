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
      0.0034125051794444646,
      -0.9999931642338233,
      0.001423479548810649
    ],
    [
      -0.00032158413713393125,
      0.0014223903508107094,
      0.999998936694101
    ],
    [
      -0.9999941256787677,
      -0.003412959319350009,
      -0.00031672802442063024
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.055550444225446,
      "length": 100.12362562220365,
      "loops": [
        [
          [
            27.548156,
            -1.471506
          ],
          [
            26.20349,
            -1.669805
          ],
          [
            21.258808,
            -1.259553
          ],
          [
            8.274521,
            -1.553032
          ],
          [
            5.804868,
            -1.243439
          ],
          [
            5.496356,
            -0.844644
          ],
          [
            4.877795,
            -1.127854
          ],
          [
            4.243172,
            -1.154384
          ],
          [
            -27.266438,
            -1.121666
          ],
          [
            -27.741463,
            -0.837852
          ],
          [
            -27.752419,
            -0.21968
          ],
          [
            -27.617378,
            1.016435
          ],
          [
            -27.262801,
            1.435395
          ],
          [
            -18.917806,
            1.334621
          ],
          [
            -18.299971,
            1.106637
          ],
          [
            -13.121682,
            1.427094
          ],
          [
            4.572529,
            1.553254
          ],
          [
            5.190543,
            1.452004
          ],
          [
            5.499117,
            1.096798
          ],
          [
            6.117841,
            1.493925
          ],
          [
            7.045132,
            1.532017
          ],
          [
            26.20806,
            1.543173
          ],
          [
            27.444236,
            1.442665
          ],
          [
            27.658659,
            1.246832
          ],
          [
            27.692836,
            -1.225838
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.0001995649999999849,
    -0.017786075,
    -0.48616461499999997
  ],
  "construction_scale": 125.34454866216942,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
