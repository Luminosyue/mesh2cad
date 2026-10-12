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
      "length": 57.57775757575758,
      "loops": [
        [
          [
            30.99648,
            6.914215
          ],
          [
            31.165044,
            4.333969
          ],
          [
            31.190232,
            -6.534224
          ],
          [
            30.722828,
            -7.877559
          ],
          [
            29.614575,
            -8.728397
          ],
          [
            28.271251,
            -9.037102
          ],
          [
            23.01962,
            -9.15556
          ],
          [
            -28.148153,
            -9.110034
          ],
          [
            -29.491472,
            -8.71371
          ],
          [
            -30.647797,
            -7.877559
          ],
          [
            -31.109798,
            -6.534224
          ],
          [
            -31.134543,
            5.555643
          ],
          [
            -30.981229,
            6.898957
          ],
          [
            -30.44213,
            8.242287
          ],
          [
            -29.491472,
            8.961089
          ],
          [
            -28.148153,
            9.15753
          ],
          [
            -25.33988,
            9.22326
          ],
          [
            27.049577,
            9.218511
          ],
          [
            29.614575,
            8.986822
          ],
          [
            30.495506,
            8.242287
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 15.153515151515142,
      "loops": [
        [
          [
            24.86329,
            9.238056
          ],
          [
            -28.148153,
            9.157511
          ],
          [
            -29.491472,
            8.927041
          ],
          [
            -30.353582,
            8.242287
          ],
          [
            -30.987667,
            6.898957
          ],
          [
            -31.167644,
            5.555643
          ],
          [
            -31.161935,
            -6.534224
          ],
          [
            -30.834792,
            -7.994908
          ],
          [
            -29.491472,
            -9.072013
          ],
          [
            -26.182843,
            -9.23757
          ],
          [
            28.271251,
            -9.228969
          ],
          [
            29.614575,
            -9.077642
          ],
          [
            30.912834,
            -7.877559
          ],
          [
            31.202001,
            -6.534224
          ],
          [
            31.030635,
            6.898957
          ],
          [
            30.528501,
            8.242287
          ],
          [
            29.614575,
            9.0356
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.72727272727272,
      "length": 27.27472727272728,
      "loops": [
        [
          [
            -31.11424,
            4.212335
          ],
          [
            -30.903712,
            6.898957
          ],
          [
            -30.213012,
            8.242287
          ],
          [
            -29.491472,
            8.807605
          ],
          [
            -28.148153,
            9.107657
          ],
          [
            22.897985,
            9.23557
          ],
          [
            29.614575,
            9.045756
          ],
          [
            30.588916,
            8.242287
          ],
          [
            31.055149,
            6.898957
          ],
          [
            31.209172,
            5.555643
          ],
          [
            31.227498,
            -6.534224
          ],
          [
            30.846691,
            -7.877559
          ],
          [
            29.614575,
            -8.955639
          ],
          [
            28.271251,
            -9.164276
          ],
          [
            -22.774877,
            -9.209039
          ],
          [
            -28.148153,
            -9.184628
          ],
          [
            -29.491472,
            -9.051305
          ],
          [
            -30.834792,
            -7.893945
          ],
          [
            -31.071423,
            -6.534224
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.19961846,
    0.48296602499999997,
    -0.00017746000000000428
  ],
  "construction_scale": 544.7758340054959,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
