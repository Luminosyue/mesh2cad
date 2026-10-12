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
      "start": -50.0,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -3.765303,
            -3.13647
          ],
          [
            -4.365413,
            -2.52514
          ],
          [
            -4.117997,
            -1.53888
          ],
          [
            -3.995002,
            0.926777
          ],
          [
            -4.223502,
            2.652734
          ],
          [
            -3.941624,
            3.145866
          ],
          [
            -3.025607,
            3.263769
          ],
          [
            3.878232,
            3.265564
          ],
          [
            4.359579,
            3.145866
          ],
          [
            4.606091,
            2.899302
          ],
          [
            4.764298,
            -1.542493
          ],
          [
            4.37136,
            -3.105044
          ],
          [
            3.878232,
            -3.22091
          ],
          [
            -3.268557,
            -3.198009
          ]
        ],
        [
          [
            0.18336,
            2.672741
          ],
          [
            -2.798212,
            2.652734
          ],
          [
            2.574458,
            2.652734
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 81.82018181818181,
      "loops": [
        [
          [
            -4.679666,
            2.39507
          ],
          [
            -4.723313,
            -2.032008
          ],
          [
            -4.504999,
            -2.863765
          ],
          [
            -4.011867,
            -3.060298
          ],
          [
            -2.532474,
            -3.166587
          ],
          [
            3.3962,
            -3.238844
          ],
          [
            4.124796,
            -3.160173
          ],
          [
            4.549242,
            -2.771708
          ],
          [
            4.723301,
            -1.785444
          ],
          [
            4.716479,
            2.159606
          ],
          [
            4.617928,
            2.868696
          ],
          [
            4.37136,
            3.108623
          ],
          [
            3.149632,
            3.268457
          ],
          [
            -3.518735,
            3.235606
          ],
          [
            -4.443418,
            2.899302
          ]
        ],
        [
          [
            2.931199,
            2.652734
          ],
          [
            0.179747,
            2.709558
          ],
          [
            -2.543947,
            2.652734
          ],
          [
            -0.54885,
            2.600466
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 40.90909090909091,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -3.41942,
            3.145866
          ],
          [
            3.631664,
            3.224371
          ],
          [
            4.617928,
            2.823017
          ],
          [
            4.723339,
            -2.032008
          ],
          [
            4.352383,
            -2.960012
          ],
          [
            4.124796,
            -3.174822
          ],
          [
            -0.701439,
            -3.142788
          ],
          [
            -1.69787,
            -3.018272
          ],
          [
            -1.352653,
            -2.771708
          ],
          [
            -1.54621,
            -2.762353
          ],
          [
            -4.153356,
            -3.00013
          ],
          [
            -4.504999,
            -2.895577
          ],
          [
            -4.609897,
            -2.52514
          ],
          [
            -4.504999,
            -2.149915
          ],
          [
            -4.092923,
            -2.032008
          ],
          [
            -4.009022,
            -1.785444
          ],
          [
            -4.027617,
            1.807963
          ],
          [
            -4.17309,
            2.40617
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.911163725,
    0.00037175000000005953,
    0.7657407549999999
  ],
  "construction_scale": 49.996652224167065,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
