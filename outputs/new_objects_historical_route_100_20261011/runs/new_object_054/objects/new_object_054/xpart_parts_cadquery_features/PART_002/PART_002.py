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
      "length": 27.274727272727272,
      "loops": [
        [
          [
            2.73628,
            -0.422952
          ],
          [
            1.041394,
            -0.598839
          ],
          [
            -0.622882,
            -0.357483
          ],
          [
            -2.687353,
            -0.548496
          ],
          [
            -3.27968,
            -0.244036
          ],
          [
            -3.443447,
            0.094941
          ],
          [
            -3.365304,
            0.470764
          ],
          [
            -2.687353,
            0.827925
          ],
          [
            -0.653493,
            0.439075
          ],
          [
            2.73628,
            0.810886
          ],
          [
            3.137887,
            0.433918
          ],
          [
            3.075256,
            -0.100788
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.727272727272727,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            2.058325,
            0.874324
          ],
          [
            1.041394,
            0.587155
          ],
          [
            -0.324632,
            0.526155
          ],
          [
            -0.992467,
            0.332881
          ],
          [
            -2.348373,
            0.738478
          ],
          [
            -3.026329,
            0.780232
          ],
          [
            -3.365304,
            0.556749
          ],
          [
            -3.506453,
            0.094941
          ],
          [
            -3.365304,
            -0.244212
          ],
          [
            -2.687353,
            -0.563068
          ],
          [
            -1.331442,
            -0.27035
          ],
          [
            0.70242,
            -0.655617
          ],
          [
            2.73628,
            -0.40382
          ],
          [
            3.075256,
            -0.037999
          ],
          [
            3.096212,
            0.433918
          ],
          [
            2.73628,
            0.815006
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.666666666666664,
      "length": 66.66866666666665,
      "loops": [
        [
          [
            1.041394,
            0.544408
          ],
          [
            2.397306,
            0.933895
          ],
          [
            2.932786,
            0.772895
          ],
          [
            3.184334,
            0.433918
          ],
          [
            3.069908,
            -0.244036
          ],
          [
            2.634592,
            -0.549424
          ],
          [
            2.058325,
            -0.649504
          ],
          [
            -0.077224,
            -0.384026
          ],
          [
            -2.687353,
            -0.468286
          ],
          [
            -3.17293,
            -0.244036
          ],
          [
            -3.399008,
            0.094941
          ],
          [
            -3.365304,
            0.538273
          ],
          [
            -3.132806,
            0.784294
          ],
          [
            -2.687353,
            0.886979
          ],
          [
            0.26175,
            0.537382
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.47325954000000003,
    -0.0006906299999999998,
    0.0014960749999999856
  ],
  "construction_scale": 137.47028906193862,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
