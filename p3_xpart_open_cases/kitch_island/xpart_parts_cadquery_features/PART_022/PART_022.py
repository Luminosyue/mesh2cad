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
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            3.581447,
            3.301525
          ],
          [
            5.491005,
            3.18905
          ],
          [
            7.823805,
            3.286711
          ],
          [
            9.733364,
            4.046517
          ],
          [
            10.156602,
            3.927508
          ],
          [
            11.850991,
            2.349613
          ],
          [
            11.804743,
            -1.469511
          ],
          [
            11.64293,
            -1.886172
          ],
          [
            9.733364,
            -3.397636
          ],
          [
            2.095123,
            -3.153247
          ],
          [
            -7.452691,
            -3.404151
          ],
          [
            -9.362249,
            -3.337534
          ],
          [
            -10.117682,
            -2.907918
          ],
          [
            -11.271814,
            -2.721756
          ],
          [
            -11.556783,
            -2.532559
          ],
          [
            -11.937889,
            -1.892747
          ],
          [
            -11.907454,
            2.349613
          ],
          [
            -11.271814,
            3.255825
          ],
          [
            -9.785486,
            3.838234
          ],
          [
            -9.362249,
            3.964154
          ],
          [
            -7.875927,
            3.487997
          ],
          [
            -3.633567,
            2.870989
          ],
          [
            -0.237678,
            2.92631
          ]
        ],
        [
          [
            -7.452691,
            2.3095
          ],
          [
            7.823805,
            2.291504
          ],
          [
            9.549036,
            0.44005
          ],
          [
            7.823805,
            -1.37363
          ],
          [
            -7.452691,
            -1.373671
          ],
          [
            -9.362249,
            -0.663895
          ],
          [
            -10.197335,
            0.44005
          ],
          [
            -9.362249,
            1.749022
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 93.94139393939393,
      "loops": [
        [
          [
            11.242822,
            2.349613
          ],
          [
            9.733364,
            4.031186
          ],
          [
            7.823805,
            3.109892
          ],
          [
            4.004682,
            3.224918
          ],
          [
            0.185558,
            2.689391
          ],
          [
            -3.310989,
            3.073485
          ],
          [
            -7.452691,
            3.142653
          ],
          [
            -9.362249,
            3.778392
          ],
          [
            -11.271814,
            3.245522
          ],
          [
            -11.795104,
            2.349613
          ],
          [
            -11.812656,
            -1.469511
          ],
          [
            -11.271814,
            -2.327246
          ],
          [
            -9.362249,
            -2.5528
          ],
          [
            -7.452691,
            -2.269986
          ],
          [
            7.823805,
            -2.264923
          ],
          [
            9.733364,
            -2.861114
          ],
          [
            11.334926,
            -1.469511
          ],
          [
            10.895523,
            0.44005
          ]
        ],
        [
          [
            -9.362249,
            1.749181
          ],
          [
            -10.238268,
            0.44005
          ],
          [
            -9.362249,
            -0.549185
          ],
          [
            -7.452691,
            -1.254406
          ],
          [
            7.823805,
            -1.233884
          ],
          [
            9.443228,
            0.44005
          ],
          [
            7.823805,
            2.287949
          ],
          [
            -7.452691,
            2.283853
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.561248585,
    0.08649658,
    0.331228865
  ],
  "construction_scale": 193.60307184573213,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
