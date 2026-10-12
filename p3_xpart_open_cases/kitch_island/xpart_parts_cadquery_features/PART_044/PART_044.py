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
      "length": 30.305030303030303,
      "loops": [
        [
          [
            14.932478,
            18.43224
          ],
          [
            13.974952,
            17.752183
          ],
          [
            13.34743,
            18.477414
          ],
          [
            13.389198,
            24.046987
          ],
          [
            13.717966,
            24.975249
          ],
          [
            13.974952,
            25.154737
          ],
          [
            14.525833,
            24.975249
          ],
          [
            14.970078,
            24.046987
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.696969696969695,
      "length": 24.24442424242424,
      "loops": [
        [
          [
            -13.883871,
            -25.150905
          ],
          [
            -4.590287,
            -25.157489
          ],
          [
            -3.528144,
            -24.222641
          ],
          [
            -3.564872,
            -22.366116
          ],
          [
            -4.590287,
            -21.572355
          ],
          [
            -13.872907,
            -21.554483
          ],
          [
            -14.913946,
            -22.366116
          ],
          [
            -14.955693,
            -24.222641
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.696969696969695,
      "length": 24.24442424242424,
      "loops": [
        [
          [
            13.395336,
            24.046987
          ],
          [
            13.346793,
            18.477414
          ],
          [
            13.974952,
            17.745348
          ],
          [
            14.944724,
            18.477414
          ],
          [
            14.965381,
            24.046987
          ],
          [
            14.539229,
            24.975249
          ],
          [
            13.974952,
            25.156807
          ],
          [
            13.71998,
            24.975249
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            -3.576086,
            -24.249213
          ],
          [
            -4.590287,
            -25.147336
          ],
          [
            -13.872907,
            -25.156622
          ],
          [
            -14.929638,
            -24.222641
          ],
          [
            -14.898833,
            -22.366116
          ],
          [
            -13.872907,
            -21.553269
          ],
          [
            -4.590287,
            -21.586872
          ],
          [
            -3.591238,
            -22.366116
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.798383655,
    -0.176605845,
    0.02965299499999996
  ],
  "construction_scale": 94.1129090828171,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
