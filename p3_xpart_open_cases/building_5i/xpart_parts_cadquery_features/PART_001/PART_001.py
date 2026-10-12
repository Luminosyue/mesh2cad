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
      "length": 60.60806060606061,
      "loops": [
        [
          [
            1.873934,
            0.102067
          ],
          [
            1.532125,
            0.932779
          ],
          [
            1.190318,
            1.334077
          ],
          [
            -0.176917,
            1.740889
          ],
          [
            -1.202343,
            1.245738
          ],
          [
            -1.80481,
            0.087195
          ],
          [
            -1.202343,
            -1.235581
          ],
          [
            -0.176917,
            -1.742947
          ],
          [
            0.16489,
            -1.741596
          ],
          [
            1.291384,
            -1.280042
          ],
          [
            1.858473,
            -0.254616
          ]
        ],
        [
          [
            -0.268762,
            0.429003
          ],
          [
            -0.595788,
            0.087195
          ],
          [
            -0.518726,
            -0.262221
          ],
          [
            -0.176917,
            -0.520591
          ],
          [
            0.5067,
            -0.336586
          ],
          [
            0.617663,
            0.087195
          ],
          [
            0.5067,
            0.258199
          ],
          [
            0.16489,
            0.469859
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.606060606060609,
      "length": 39.39593939393939,
      "loops": [
        [
          [
            1.898088,
            0.087195
          ],
          [
            1.190318,
            1.328682
          ],
          [
            0.5067,
            1.667643
          ],
          [
            -0.518726,
            1.651884
          ],
          [
            -1.371239,
            1.112621
          ],
          [
            -1.87826,
            0.087195
          ],
          [
            -1.821196,
            -0.254616
          ],
          [
            -1.186619,
            -1.270398
          ],
          [
            -0.176917,
            -1.748455
          ],
          [
            0.5067,
            -1.671649
          ],
          [
            1.285924,
            -1.280042
          ],
          [
            1.873934,
            -0.300044
          ]
        ],
        [
          [
            -0.313752,
            0.429003
          ],
          [
            0.349575,
            0.429003
          ],
          [
            0.593902,
            0.087195
          ],
          [
            0.5067,
            -0.356203
          ],
          [
            0.16489,
            -0.592967
          ],
          [
            -0.176917,
            -0.559924
          ],
          [
            -0.518726,
            -0.291014
          ],
          [
            -0.637256,
            0.087195
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.6620978900000001,
    -0.278499575,
    0.41187874999999996
  ],
  "construction_scale": 69.30933119773725,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
