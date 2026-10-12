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
      "start": -49.99999999999999,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            16.567978,
            -21.726695
          ],
          [
            17.016173,
            -27.736317
          ],
          [
            16.929515,
            -27.97471
          ],
          [
            16.528875,
            -28.098998
          ],
          [
            -16.323726,
            -28.12406
          ],
          [
            -16.724367,
            -28.071579
          ],
          [
            -16.877981,
            -27.736317
          ],
          [
            -16.867297,
            -22.127336
          ],
          [
            -16.724367,
            -21.56957
          ],
          [
            -16.323726,
            -21.519507
          ],
          [
            16.128234,
            -21.590368
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939393,
      "length": 87.88078787878786,
      "loops": [
        [
          [
            -15.690243,
            9.122699
          ],
          [
            -15.462038,
            -21.326053
          ],
          [
            -15.121802,
            -21.584123
          ],
          [
            16.128234,
            -21.618397
          ],
          [
            16.502134,
            -21.726695
          ],
          [
            16.523795,
            -22.127336
          ],
          [
            15.934811,
            -27.736317
          ],
          [
            15.727591,
            -28.07831
          ],
          [
            -16.323726,
            -28.127494
          ],
          [
            -16.724367,
            -28.016039
          ],
          [
            -16.972328,
            -6.502319
          ],
          [
            -16.999355,
            26.750924
          ],
          [
            -16.933437,
            27.952848
          ],
          [
            -16.724367,
            28.121019
          ],
          [
            -15.923085,
            28.117582
          ],
          [
            -15.715711,
            27.952848
          ],
          [
            -15.6237,
            27.552206
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939393,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -16.796152,
            -21.604413
          ],
          [
            -16.110332,
            -21.504218
          ],
          [
            15.727591,
            -21.603738
          ],
          [
            16.154179,
            -21.726695
          ],
          [
            16.221443,
            -22.127336
          ],
          [
            16.420494,
            -27.736317
          ],
          [
            16.128234,
            -28.123317
          ],
          [
            15.940986,
            -28.127975
          ],
          [
            -16.724367,
            -28.065641
          ],
          [
            -16.867108,
            -27.736317
          ],
          [
            -16.90761,
            -22.127336
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00012770500000003349,
    -0.0025252449999999815,
    -0.08650325000000003
  ],
  "construction_scale": 40.61949193342587,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
