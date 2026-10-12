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
      0.5005714289823657,
      0.8656948252909162,
      0.0008449562610634076
    ],
    [
      0.8656940573719549,
      -0.5005688963395677,
      -0.002139871087214218
    ],
    [
      -0.0014295165039352766,
      0.0018026319419066547,
      -0.9999973534968217
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -49.99200497117502,
      "length": 99.98382972302704,
      "loops": [
        [
          [
            14.200105,
            -3.699958
          ],
          [
            11.497526,
            -7.063028
          ],
          [
            9.733317,
            -8.505801
          ],
          [
            6.717372,
            -10.479456
          ],
          [
            4.307737,
            -11.525793
          ],
          [
            2.653858,
            -11.800914
          ],
          [
            1.020018,
            -11.813835
          ],
          [
            -2.316101,
            -11.194321
          ],
          [
            -4.854839,
            -11.325493
          ],
          [
            -7.971375,
            -10.326233
          ],
          [
            -8.929515,
            -9.853572
          ],
          [
            -11.394404,
            -7.727334
          ],
          [
            -12.927697,
            -5.275992
          ],
          [
            -13.758129,
            -3.296457
          ],
          [
            -14.067932,
            -1.702548
          ],
          [
            -14.09181,
            0.385845
          ],
          [
            -13.463022,
            3.665182
          ],
          [
            -12.729252,
            5.714207
          ],
          [
            -10.957939,
            8.384318
          ],
          [
            -8.033395,
            10.8634
          ],
          [
            -6.21509,
            11.878329
          ],
          [
            -3.223151,
            12.793276
          ],
          [
            -0.594322,
            13.080248
          ],
          [
            2.855969,
            12.658191
          ],
          [
            4.936311,
            11.996602
          ],
          [
            7.668232,
            10.332181
          ],
          [
            9.343971,
            8.970863
          ],
          [
            11.299353,
            8.093166
          ],
          [
            13.962711,
            6.464171
          ],
          [
            14.706617,
            5.467007
          ],
          [
            15.426979,
            2.979306
          ],
          [
            15.275165,
            0.604197
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    0.021387725,
    0.067191045,
    -0.07925387
  ],
  "construction_scale": 216.1666170780447,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
