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
      "length": 100.0,
      "loops": [
        [
          [
            -10.859519,
            11.849008
          ],
          [
            -12.018977,
            9.878639
          ],
          [
            -13.328122,
            6.787671
          ],
          [
            -14.402663,
            3.116286
          ],
          [
            -14.712577,
            0.646412
          ],
          [
            -14.653297,
            -1.823461
          ],
          [
            -14.232481,
            -4.293334
          ],
          [
            -13.15198,
            -7.751157
          ],
          [
            -12.208128,
            -9.880348
          ],
          [
            -10.202151,
            -13.184879
          ],
          [
            -8.545292,
            -15.214551
          ],
          [
            -6.9507,
            -16.728783
          ],
          [
            -4.77521,
            -18.124625
          ],
          [
            -2.010953,
            -19.101257
          ],
          [
            -0.035055,
            -19.325959
          ],
          [
            2.434819,
            -18.964709
          ],
          [
            4.652724,
            -18.124625
          ],
          [
            7.428847,
            -16.148727
          ],
          [
            10.058455,
            -13.184879
          ],
          [
            12.356778,
            -9.233081
          ],
          [
            13.234009,
            -7.257182
          ],
          [
            14.186141,
            -4.293334
          ],
          [
            14.70388,
            -0.494829
          ],
          [
            14.475067,
            2.622311
          ],
          [
            13.302261,
            6.805626
          ],
          [
            11.87961,
            10.031931
          ],
          [
            9.301441,
            13.983728
          ],
          [
            7.86854,
            15.568526
          ],
          [
            6.296547,
            16.947576
          ],
          [
            3.422768,
            18.596006
          ],
          [
            1.940844,
            19.050967
          ],
          [
            -0.035055,
            19.32112
          ],
          [
            -2.010953,
            19.064673
          ],
          [
            -3.492877,
            18.583457
          ],
          [
            -5.96275,
            17.262076
          ],
          [
            -8.55279,
            14.971677
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "center": [
    -0.0030437500000000117,
    -0.11529855499999997,
    0.0006999450000000074
  ],
  "construction_scale": 50.08218361125147,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
