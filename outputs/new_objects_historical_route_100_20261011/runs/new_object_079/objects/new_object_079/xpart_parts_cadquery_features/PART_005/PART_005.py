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
      "start": -4.97092685962876,
      "length": 3.9166866658728,
      "loops": [
        [
          [
            24.163234,
            41.542621
          ],
          [
            17.344593,
            48.114843
          ],
          [
            17.270417,
            48.383183
          ],
          [
            17.519914,
            48.683005
          ],
          [
            18.593281,
            48.841027
          ],
          [
            24.818016,
            48.795905
          ],
          [
            25.123855,
            48.114843
          ],
          [
            25.211683,
            45.431423
          ],
          [
            25.220485,
            42.479662
          ],
          [
            24.986542,
            41.406297
          ],
          [
            24.685327,
            41.297131
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.97092685962876,
      "length": 3.9166866658728,
      "loops": [
        [
          [
            -24.6707,
            48.651527
          ],
          [
            -24.673947,
            41.674636
          ],
          [
            -24.341418,
            41.216403
          ],
          [
            -24.073075,
            41.228723
          ],
          [
            -23.502209,
            41.674636
          ],
          [
            -18.974581,
            46.712281
          ],
          [
            -17.496479,
            48.114843
          ],
          [
            -17.176902,
            48.651527
          ],
          [
            -17.35843,
            48.919868
          ],
          [
            -17.98103,
            49.046422
          ],
          [
            -24.341418,
            49.076081
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.97092685962876,
      "length": 3.9166866658728,
      "loops": [
        [
          [
            -20.852974,
            -45.587948
          ],
          [
            -18.016829,
            -48.488231
          ],
          [
            -17.973237,
            -48.756571
          ],
          [
            -18.195405,
            -49.024915
          ],
          [
            -20.316289,
            -49.249905
          ],
          [
            -24.073075,
            -49.118081
          ],
          [
            -24.415654,
            -48.756571
          ],
          [
            -24.489537,
            -48.219887
          ],
          [
            -24.551209,
            -45.53647
          ],
          [
            -24.427427,
            -44.41916
          ],
          [
            -24.198254,
            -44.183188
          ],
          [
            -23.804735,
            -44.183674
          ],
          [
            -21.92634,
            -44.838075
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.0544390308303448,
      "length": 1.205272015166205,
      "loops": [
        [
          [
            25.73515,
            -45.371489
          ],
          [
            25.730143,
            48.383183
          ],
          [
            25.677965,
            49.188209
          ],
          [
            25.559449,
            49.456553
          ],
          [
            25.301827,
            49.579207
          ],
          [
            14.568154,
            49.764194
          ],
          [
            -18.571819,
            49.83636
          ],
          [
            -24.496948,
            49.645494
          ],
          [
            -25.414785,
            49.527272
          ],
          [
            -25.723574,
            49.312964
          ],
          [
            -25.858258,
            48.651527
          ],
          [
            -25.880741,
            45.968108
          ],
          [
            -25.879645,
            -43.121394
          ],
          [
            -25.850045,
            -48.756571
          ],
          [
            -25.683128,
            -49.393994
          ],
          [
            -24.73113,
            -49.634068
          ],
          [
            -18.706239,
            -49.882322
          ],
          [
            -17.759384,
            -49.829941
          ],
          [
            -17.096188,
            -49.444605
          ],
          [
            -16.291161,
            -49.334631
          ],
          [
            24.931636,
            -49.384072
          ],
          [
            25.301827,
            -49.347016
          ],
          [
            25.57017,
            -49.115133
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.15063414726147517,
      "length": 4.820491549441667,
      "loops": [
        [
          [
            -24.821956,
            41.137952
          ],
          [
            -24.814951,
            -41.350879
          ],
          [
            -24.77643,
            -41.779685
          ],
          [
            -24.501879,
            -42.223225
          ],
          [
            -23.804735,
            -42.356846
          ],
          [
            8.127949,
            -42.356777
          ],
          [
            24.925606,
            -42.320827
          ],
          [
            25.57017,
            -42.196001
          ],
          [
            25.832783,
            -41.779685
          ],
          [
            25.899519,
            -40.706314
          ],
          [
            25.909488,
            34.321525
          ],
          [
            25.895015,
            41.137952
          ],
          [
            25.790633,
            41.674636
          ],
          [
            25.577156,
            41.942982
          ],
          [
            23.691777,
            42.052861
          ],
          [
            -24.073075,
            42.067484
          ],
          [
            -24.60976,
            41.891708
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0017155500000000101,
    -0.219631635,
    -0.005645565000000005
  ],
  "construction_scale": 108.8245832818321,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
