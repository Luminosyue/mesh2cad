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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -2.607592,
            8.346493
          ],
          [
            -2.722973,
            -8.41512
          ],
          [
            -1.548345,
            -10.128574
          ],
          [
            0.911086,
            -10.368762
          ],
          [
            3.163026,
            -10.277521
          ],
          [
            4.038871,
            -10.099511
          ],
          [
            5.175834,
            -8.41512
          ],
          [
            5.222243,
            -6.43013
          ],
          [
            5.08013,
            2.890321
          ],
          [
            5.189078,
            8.346493
          ],
          [
            4.165233,
            10.208892
          ],
          [
            0.314061,
            10.357132
          ],
          [
            -1.627492,
            10.208892
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 75.75957575757575,
      "loops": [
        [
          [
            -1.552443,
            -10.277521
          ],
          [
            4.038871,
            -10.214946
          ],
          [
            5.356947,
            -8.41512
          ],
          [
            5.210716,
            2.759288
          ],
          [
            5.353964,
            8.346493
          ],
          [
            4.342691,
            10.208892
          ],
          [
            4.038871,
            10.381304
          ],
          [
            -1.548345,
            10.36891
          ],
          [
            -1.823592,
            10.208892
          ],
          [
            -2.882173,
            8.346493
          ],
          [
            -2.896419,
            -8.41512
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 31.818181818181813,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            5.242888,
            6.250722
          ],
          [
            5.352725,
            8.346493
          ],
          [
            4.329097,
            10.208892
          ],
          [
            4.038871,
            10.367864
          ],
          [
            -1.548345,
            10.345942
          ],
          [
            -1.784689,
            10.208892
          ],
          [
            -2.881055,
            8.346493
          ],
          [
            -2.955971,
            -8.41512
          ],
          [
            -1.548345,
            -10.359854
          ],
          [
            4.038871,
            -10.338791
          ],
          [
            5.35913,
            -8.41512
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 37.878787878787875,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -1.316155,
            -6.552719
          ],
          [
            -1.239534,
            -0.965514
          ],
          [
            -1.613509,
            4.621689
          ],
          [
            -1.134102,
            6.48409
          ],
          [
            0.314061,
            7.55224
          ],
          [
            2.176466,
            7.452149
          ],
          [
            4.038871,
            6.774138
          ],
          [
            4.374755,
            6.48409
          ],
          [
            4.738434,
            4.621689
          ],
          [
            4.745963,
            -4.690318
          ],
          [
            4.386765,
            -6.552719
          ],
          [
            4.038871,
            -6.862183
          ],
          [
            0.314061,
            -7.540142
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
            -5.183257,
            -0.965514
          ],
          [
            -5.27314,
            1.009839
          ],
          [
            -4.284598,
            2.759288
          ],
          [
            -3.410735,
            3.397762
          ],
          [
            -1.548345,
            3.891101
          ],
          [
            -0.76507,
            4.621689
          ],
          [
            -0.538439,
            6.48409
          ],
          [
            0.314061,
            7.524924
          ],
          [
            2.176466,
            7.571213
          ],
          [
            4.038871,
            7.281053
          ],
          [
            4.700292,
            6.48409
          ],
          [
            4.916546,
            4.621689
          ],
          [
            5.009148,
            -2.827917
          ],
          [
            4.968123,
            -4.690318
          ],
          [
            4.695129,
            -6.552719
          ],
          [
            4.038871,
            -7.204169
          ],
          [
            0.314061,
            -7.403569
          ],
          [
            -0.532334,
            -6.552719
          ],
          [
            -0.725023,
            -4.690318
          ],
          [
            -1.548345,
            -3.289738
          ],
          [
            -3.410735,
            -2.808529
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.95840156,
    0.054429775,
    -0.24681229500000001
  ],
  "construction_scale": 188.82167026249215,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
