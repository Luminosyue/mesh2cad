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
      "start": -43.48299139448321,
      "length": 5.272404943229499,
      "loops": [
        [
          [
            1.575087,
            47.331056
          ],
          [
            -3.045804,
            47.364645
          ],
          [
            -4.298181,
            46.268335
          ],
          [
            -4.397664,
            35.48628
          ],
          [
            -4.34756,
            32.405694
          ],
          [
            -4.195587,
            31.425793
          ],
          [
            -4.066117,
            30.865401
          ],
          [
            -3.045804,
            30.428578
          ],
          [
            1.575087,
            30.383482
          ],
          [
            2.187673,
            30.865401
          ],
          [
            2.376169,
            32.405694
          ],
          [
            2.43983,
            46.268335
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.48299139448321,
      "length": 5.272404943229499,
      "loops": [
        [
          [
            2.16776,
            -33.826915
          ],
          [
            2.32468,
            -47.689556
          ],
          [
            2.11339,
            -49.229852
          ],
          [
            1.575087,
            -49.675404
          ],
          [
            -3.045804,
            -49.732988
          ],
          [
            -4.062452,
            -49.229852
          ],
          [
            -4.294819,
            -47.689556
          ],
          [
            -4.1711,
            -33.826915
          ],
          [
            -3.045804,
            -33.03198
          ],
          [
            1.575087,
            -33.267346
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -38.21232577090949,
      "length": 73.79105804968789,
      "loops": [
        [
          [
            -4.59456,
            33.945987
          ],
          [
            -4.462119,
            46.268335
          ],
          [
            -3.045804,
            47.57082
          ],
          [
            1.575087,
            47.538337
          ],
          [
            2.640706,
            46.268335
          ],
          [
            2.704018,
            32.405694
          ],
          [
            2.136286,
            30.865401
          ],
          [
            1.575087,
            30.527119
          ],
          [
            -1.505507,
            30.369852
          ],
          [
            -3.045804,
            30.590592
          ],
          [
            -3.465668,
            30.865401
          ],
          [
            -4.238511,
            32.405694
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -38.21232577090949,
      "length": 73.79105804968789,
      "loops": [
        [
          [
            -4.59008,
            -47.9596
          ],
          [
            -4.285887,
            -49.229852
          ],
          [
            -3.045804,
            -49.911652
          ],
          [
            -1.505507,
            -49.736159
          ],
          [
            0.034789,
            -49.859434
          ],
          [
            1.575087,
            -49.723644
          ],
          [
            2.167726,
            -49.229852
          ],
          [
            2.562846,
            -47.689556
          ],
          [
            2.557671,
            -35.367212
          ],
          [
            2.43636,
            -33.826915
          ],
          [
            1.575087,
            -32.983953
          ],
          [
            0.034789,
            -32.84436
          ],
          [
            -1.505507,
            -33.023961
          ],
          [
            -3.045804,
            -32.836036
          ],
          [
            -4.603027,
            -33.826915
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 35.57699295912262,
      "length": 7.907737755016366,
      "loops": [
        [
          [
            2.543904,
            43.187747
          ],
          [
            3.733328,
            40.107161
          ],
          [
            3.656343,
            38.566868
          ],
          [
            3.171077,
            37.903452
          ],
          [
            2.641672,
            36.525955
          ],
          [
            2.405546,
            32.405694
          ],
          [
            1.575087,
            31.531608
          ],
          [
            -1.505507,
            30.792625
          ],
          [
            -3.030806,
            32.355658
          ],
          [
            -3.416741,
            32.405694
          ],
          [
            -4.586089,
            33.09308
          ],
          [
            -4.733785,
            33.945987
          ],
          [
            -4.586089,
            49.383483
          ],
          [
            -3.045804,
            49.962215
          ],
          [
            0.034789,
            49.969614
          ],
          [
            1.575087,
            49.957106
          ],
          [
            2.294869,
            49.348919
          ],
          [
            2.464819,
            47.808626
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 35.57699295912262,
      "length": 7.907737755016366,
      "loops": [
        [
          [
            3.413137,
            -46.149264
          ],
          [
            2.153547,
            -49.229852
          ],
          [
            1.575087,
            -49.769571
          ],
          [
            0.034789,
            -49.98895
          ],
          [
            -1.505507,
            -49.822623
          ],
          [
            -3.045804,
            -49.972462
          ],
          [
            -4.590025,
            -49.229852
          ],
          [
            -4.700715,
            -47.689556
          ],
          [
            -4.66041,
            -35.86783
          ],
          [
            -4.384103,
            -33.826915
          ],
          [
            -3.045804,
            -33.387411
          ],
          [
            0.034789,
            -33.329868
          ],
          [
            1.575087,
            -33.514354
          ],
          [
            1.972963,
            -33.826915
          ],
          [
            2.444498,
            -35.367212
          ],
          [
            2.568519,
            -42.56806
          ],
          [
            2.931528,
            -43.068678
          ],
          [
            3.580986,
            -44.608974
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.95651552,
    -0.19764685499999998,
    -0.236609795
  ],
  "construction_scale": 156.16439019328234,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
