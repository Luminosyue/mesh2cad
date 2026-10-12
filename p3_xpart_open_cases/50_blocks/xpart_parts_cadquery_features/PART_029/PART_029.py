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
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            12.113916,
            -8.194401
          ],
          [
            11.928307,
            -10.327605
          ],
          [
            11.376669,
            -12.460807
          ],
          [
            10.969432,
            -13.527407
          ],
          [
            9.681955,
            -15.660609
          ],
          [
            7.856954,
            -17.710544
          ],
          [
            6.790353,
            -18.522526
          ],
          [
            3.969831,
            -19.927013
          ],
          [
            0.390748,
            -20.68752
          ],
          [
            -2.809055,
            -20.179447
          ],
          [
            -6.048311,
            -18.860412
          ],
          [
            -7.514541,
            -17.793811
          ],
          [
            -9.208663,
            -15.968558
          ],
          [
            -10.769805,
            -13.527407
          ],
          [
            -11.676225,
            -11.394203
          ],
          [
            -12.206574,
            -9.261002
          ],
          [
            -12.362819,
            -7.1278
          ],
          [
            -11.917482,
            -3.927997
          ],
          [
            -10.875067,
            -1.794795
          ],
          [
            -9.34936,
            0.338407
          ],
          [
            -8.994827,
            1.405008
          ],
          [
            -10.507961,
            3.538209
          ],
          [
            -11.664346,
            5.671411
          ],
          [
            -12.244198,
            7.804615
          ],
          [
            -12.270813,
            9.937817
          ],
          [
            -12.036493,
            12.071019
          ],
          [
            -11.341864,
            14.363634
          ],
          [
            -10.238588,
            16.41116
          ],
          [
            -8.142062,
            18.763627
          ],
          [
            -7.04856,
            19.537228
          ],
          [
            -4.942257,
            20.496776
          ],
          [
            -2.809055,
            20.77062
          ],
          [
            -1.742456,
            20.622294
          ],
          [
            2.52395,
            19.366531
          ],
          [
            7.67582,
            17.399786
          ],
          [
            9.661164,
            16.337425
          ],
          [
            10.750073,
            15.270822
          ],
          [
            11.251428,
            14.204221
          ],
          [
            11.364269,
            13.13762
          ],
          [
            10.859749,
            11.004418
          ],
          [
            9.757503,
            8.871216
          ],
          [
            6.346742,
            4.60481
          ],
          [
            5.873882,
            3.538209
          ],
          [
            8.923555,
            0.829987
          ],
          [
            10.17952,
            -0.728194
          ],
          [
            10.785175,
            -1.794795
          ],
          [
            11.842231,
            -4.994598
          ]
        ],
        [
          [
            -0.491507,
            6.738012
          ],
          [
            -0.522001,
            7.804615
          ],
          [
            -1.742456,
            8.031654
          ],
          [
            -2.190231,
            7.804615
          ],
          [
            -2.585471,
            6.738012
          ],
          [
            -1.742456,
            6.334149
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.09057623,
    0.08720484,
    -0.078670635
  ],
  "construction_scale": 216.27712453074622,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
