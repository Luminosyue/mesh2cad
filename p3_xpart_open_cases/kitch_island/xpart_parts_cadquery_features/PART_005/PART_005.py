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
      "start": -2.048274865112036,
      "length": 0.49663341344600703,
      "loops": [
        [
          [
            -46.30735,
            -3.658987
          ],
          [
            -46.289253,
            4.712479
          ],
          [
            -46.629344,
            5.669085
          ],
          [
            -46.845031,
            5.81969
          ],
          [
            -49.100728,
            5.669085
          ],
          [
            -49.411358,
            4.712479
          ],
          [
            -49.620727,
            -3.89699
          ],
          [
            -49.106705,
            -4.853599
          ],
          [
            -48.758246,
            -5.036891
          ],
          [
            -46.845031,
            -5.131934
          ],
          [
            -46.479097,
            -4.603814
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.048274865112036,
      "length": 0.49663341344600703,
      "loops": [
        [
          [
            48.772546,
            3.712683
          ],
          [
            48.821102,
            3.755869
          ],
          [
            48.815733,
            3.122544
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.5517233826606334,
      "length": 3.6000801787672736,
      "loops": [
        [
          [
            0.985352,
            6.034413
          ],
          [
            -45.888423,
            5.944382
          ],
          [
            -46.845031,
            6.413047
          ],
          [
            -48.758246,
            6.197983
          ],
          [
            -49.811691,
            5.669085
          ],
          [
            -49.920694,
            -3.89699
          ],
          [
            -49.765481,
            -4.853599
          ],
          [
            -48.758246,
            -5.793208
          ],
          [
            -48.362024,
            -5.887942
          ],
          [
            -47.801638,
            -6.318329
          ],
          [
            -45.888423,
            -5.146583
          ],
          [
            -4.754295,
            -5.159428
          ],
          [
            -0.554613,
            -5.212322
          ],
          [
            0.384607,
            -5.379432
          ],
          [
            1.941958,
            -5.3077
          ],
          [
            2.315071,
            -4.853599
          ],
          [
            2.334594,
            -4.51966
          ],
          [
            2.33347,
            4.09897
          ],
          [
            2.42816,
            4.712479
          ],
          [
            2.889124,
            5.669085
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.5517233826606334,
      "length": 3.6000801787672736,
      "loops": [
        [
          [
            48.815733,
            6.086213
          ],
          [
            4.81178,
            5.97951
          ],
          [
            2.909338,
            5.669085
          ],
          [
            4.243256,
            3.755869
          ],
          [
            4.455355,
            2.799263
          ],
          [
            4.730546,
            -2.940384
          ],
          [
            4.619654,
            -4.853599
          ],
          [
            5.768389,
            -5.074258
          ],
          [
            8.638215,
            -5.148328
          ],
          [
            45.374187,
            -5.191848
          ],
          [
            46.902514,
            -5.335576
          ],
          [
            47.859123,
            -5.929695
          ],
          [
            49.614493,
            -4.853599
          ],
          [
            49.736289,
            -3.89699
          ],
          [
            49.641761,
            4.712479
          ],
          [
            49.448033,
            5.669085
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.41498534,
    -0.426942,
    0.561910675
  ],
  "construction_scale": 96.98675253097842,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
