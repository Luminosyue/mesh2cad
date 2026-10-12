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
      "start": -5.705135460330872,
      "length": 10.718967555130966,
      "loops": [
        [
          [
            48.089349,
            15.907319
          ],
          [
            -49.468604,
            15.964421
          ],
          [
            -49.838386,
            16.245621
          ],
          [
            -49.990465,
            16.817808
          ],
          [
            -49.877798,
            23.11187
          ],
          [
            -49.468604,
            23.446323
          ],
          [
            -48.896416,
            23.488647
          ],
          [
            49.519819,
            23.425672
          ],
          [
            49.805911,
            23.176157
          ],
          [
            49.880595,
            22.825776
          ],
          [
            49.84566,
            16.243045
          ],
          [
            49.980998,
            14.242965
          ],
          [
            49.878825,
            -21.804841
          ],
          [
            49.756413,
            -23.23531
          ],
          [
            49.519819,
            -23.477695
          ],
          [
            49.374041,
            -23.233101
          ],
          [
            48.992899,
            -21.516539
          ],
          [
            48.804945,
            11.954215
          ],
          [
            48.661538,
            15.802063
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 5.013603889381681,
      "length": 0.6917597763676109,
      "loops": [
        [
          [
            49.233722,
            16.077227
          ],
          [
            -49.468604,
            16.140496
          ],
          [
            -49.754697,
            16.378716
          ],
          [
            -49.877641,
            16.817808
          ],
          [
            -49.774792,
            22.825776
          ],
          [
            -49.468604,
            23.194137
          ],
          [
            -48.896416,
            23.26874
          ],
          [
            48.94763,
            23.303926
          ],
          [
            49.542677,
            23.11187
          ],
          [
            49.715811,
            22.539683
          ],
          [
            49.788586,
            16.817808
          ],
          [
            49.5812,
            16.245621
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 5.013603889381681,
      "length": 0.6917597763676109,
      "loops": [
        [
          [
            49.875565,
            14.242965
          ],
          [
            49.865414,
            -22.090937
          ],
          [
            49.805911,
            -23.021391
          ],
          [
            49.519819,
            -23.539297
          ],
          [
            49.233722,
            -22.70236
          ],
          [
            49.113889,
            -20.660468
          ],
          [
            49.116866,
            -3.494844
          ],
          [
            48.983341,
            0.813142
          ],
          [
            49.047989,
            13.384684
          ],
          [
            49.519819,
            15.376713
          ],
          [
            49.805911,
            15.03389
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.004490239999999979,
    -0.33921928,
    -0.764760485
  ],
  "construction_scale": 58.01187166544136,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
