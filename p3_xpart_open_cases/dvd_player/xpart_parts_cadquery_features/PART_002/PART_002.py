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
      "length": 93.94139393939393,
      "loops": [
        [
          [
            11.079267,
            0.164844
          ],
          [
            -5.634187,
            8.653698
          ],
          [
            -6.547032,
            8.830167
          ],
          [
            -7.237297,
            8.247798
          ],
          [
            -9.087856,
            5.337628
          ],
          [
            -11.390315,
            1.381968
          ],
          [
            -11.925899,
            0.164844
          ],
          [
            -12.258495,
            -2.148855
          ],
          [
            -12.211207,
            -8.050757
          ],
          [
            -11.719816,
            -8.658271
          ],
          [
            -11.111254,
            -8.821488
          ],
          [
            11.405574,
            -8.777648
          ],
          [
            11.960092,
            -8.355037
          ],
          [
            12.028872,
            -8.050757
          ],
          [
            11.415157,
            -0.726913
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -4.659203,
            8.077233
          ],
          [
            -6.24275,
            8.75073
          ],
          [
            -6.862739,
            8.484403
          ],
          [
            -10.071686,
            3.51194
          ],
          [
            -11.731769,
            0.469124
          ],
          [
            -12.072926,
            -0.872558
          ],
          [
            -12.224069,
            -2.877973
          ],
          [
            -12.290659,
            -7.746477
          ],
          [
            -12.024098,
            -8.453115
          ],
          [
            -11.415535,
            -8.798777
          ],
          [
            -9.589846,
            -8.867319
          ],
          [
            10.063892,
            -8.853465
          ],
          [
            11.101293,
            -8.835186
          ],
          [
            11.709857,
            -8.629838
          ],
          [
            12.037704,
            -8.050757
          ],
          [
            11.673019,
            -3.666261
          ],
          [
            11.350897,
            -0.748
          ],
          [
            10.917319,
            0.040286
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.005263275000000012,
    0.04199966000000001,
    0.85543379
  ],
  "construction_scale": 61.699845172259515,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
