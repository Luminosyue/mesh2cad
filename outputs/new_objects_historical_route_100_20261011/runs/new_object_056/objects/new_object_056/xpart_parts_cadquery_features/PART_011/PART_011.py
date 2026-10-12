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
      "start": -50.0,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            7.015657,
            -28.50999
          ],
          [
            0.758299,
            -12.616562
          ],
          [
            -1.293195,
            -6.015422
          ],
          [
            -4.954803,
            11.273271
          ],
          [
            -9.1268,
            33.277064
          ],
          [
            -9.185578,
            34.958287
          ],
          [
            -8.871238,
            34.697897
          ],
          [
            -8.546434,
            33.621576
          ],
          [
            -5.153529,
            17.383636
          ],
          [
            0.621097,
            -6.820537
          ],
          [
            2.149471,
            -11.609501
          ],
          [
            7.423167,
            -25.818834
          ],
          [
            9.252565,
            -33.225088
          ],
          [
            9.5303,
            -34.934694
          ],
          [
            9.360476,
            -35.454645
          ],
          [
            8.99729,
            -35.041694
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            -1.689598,
            -4.758064
          ],
          [
            -3.479643,
            3.100435
          ],
          [
            -5.596203,
            13.500123
          ],
          [
            -6.750391,
            21.332148
          ],
          [
            -9.905832,
            37.992163
          ],
          [
            -9.88558,
            38.935184
          ],
          [
            -9.499918,
            39.219406
          ],
          [
            -9.185578,
            38.98556
          ],
          [
            -8.839738,
            37.965692
          ],
          [
            -6.797727,
            30.448005
          ],
          [
            -4.583603,
            19.760449
          ],
          [
            -3.329402,
            11.299743
          ],
          [
            -1.620296,
            1.843074
          ],
          [
            -0.90879,
            -1.300324
          ],
          [
            1.501979,
            -9.464501
          ],
          [
            6.246751,
            -23.330591
          ],
          [
            8.020373,
            -28.962236
          ],
          [
            9.153384,
            -33.336523
          ],
          [
            10.035318,
            -38.392433
          ],
          [
            9.989156,
            -38.860527
          ],
          [
            9.674816,
            -38.906741
          ],
          [
            9.510394,
            -38.6803
          ],
          [
            8.164651,
            -33.677332
          ],
          [
            5.341245,
            -26.743546
          ],
          [
            3.263538,
            -21.103738
          ],
          [
            0.20094,
            -11.67354
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00010328500000000851,
    -0.014247999999999997,
    -0.142680545
  ],
  "construction_scale": 127.47883389246613,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
