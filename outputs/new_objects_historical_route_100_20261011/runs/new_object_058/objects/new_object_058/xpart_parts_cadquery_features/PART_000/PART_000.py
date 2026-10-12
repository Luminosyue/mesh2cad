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
      "start": -27.484425977347666,
      "length": 28.318386747639725,
      "loops": [
        [
          [
            -22.356159,
            -49.227436
          ],
          [
            -22.388172,
            -47.009217
          ],
          [
            -21.922564,
            -46.449705
          ],
          [
            -18.595239,
            -46.367762
          ],
          [
            -18.040685,
            -46.463269
          ],
          [
            -17.617893,
            -47.009217
          ],
          [
            -17.635968,
            -49.227436
          ],
          [
            -18.252909,
            -49.78199
          ],
          [
            -21.922564,
            -49.753238
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.8328613932529656,
      "length": 3.332544950050931,
      "loops": [
        [
          [
            14.123459,
            -49.596174
          ],
          [
            -21.368012,
            -49.838205
          ],
          [
            -21.922564,
            -49.746297
          ],
          [
            -22.369989,
            -49.227436
          ],
          [
            -22.459098,
            -47.563773
          ],
          [
            -22.40071,
            -47.009217
          ],
          [
            -21.922564,
            -46.459276
          ],
          [
            -21.368012,
            -46.380631
          ],
          [
            14.123459,
            -46.509693
          ],
          [
            16.552836,
            -46.665823
          ],
          [
            17.450783,
            -46.888932
          ],
          [
            17.584403,
            -47.009217
          ],
          [
            17.115332,
            -48.118327
          ],
          [
            18.753866,
            -49.227436
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.164306966264803,
      "length": 9.995436096074613,
      "loops": [
        [
          [
            -21.608965,
            49.722229
          ],
          [
            -18.595239,
            49.651705
          ],
          [
            -18.100956,
            48.928661
          ],
          [
            -18.081576,
            48.374109
          ],
          [
            -18.237218,
            46.155892
          ],
          [
            -18.250858,
            -45.900111
          ],
          [
            -17.524504,
            -47.009217
          ],
          [
            -17.501698,
            -48.672879
          ],
          [
            -17.553294,
            -49.227436
          ],
          [
            -18.040685,
            -49.747458
          ],
          [
            -18.595239,
            -49.806043
          ],
          [
            -21.922564,
            -49.746819
          ],
          [
            -22.456579,
            -49.227436
          ],
          [
            -22.550514,
            -48.672879
          ],
          [
            -22.50957,
            -47.009217
          ],
          [
            -21.857656,
            -46.454663
          ],
          [
            -21.778179,
            -45.900111
          ],
          [
            -21.861486,
            46.155892
          ],
          [
            -22.399932,
            47.264998
          ],
          [
            -22.443464,
            48.374109
          ],
          [
            -22.423437,
            48.928661
          ],
          [
            -22.132465,
            49.483217
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 14.158643685300323,
      "length": 8.329713309568685,
      "loops": [
        [
          [
            -18.259998,
            46.155892
          ],
          [
            -18.269951,
            -45.900111
          ],
          [
            -17.527487,
            -47.009217
          ],
          [
            -17.519456,
            -48.672879
          ],
          [
            -17.571623,
            -49.227436
          ],
          [
            -18.040685,
            -49.733741
          ],
          [
            -21.368012,
            -49.796306
          ],
          [
            -21.922564,
            -49.746041
          ],
          [
            -22.467792,
            -49.227436
          ],
          [
            -22.57851,
            -47.563773
          ],
          [
            -22.512532,
            -47.009217
          ],
          [
            -21.847265,
            -46.454663
          ],
          [
            -21.769548,
            -45.900111
          ],
          [
            -21.859743,
            46.155892
          ],
          [
            -22.409927,
            47.264998
          ],
          [
            -22.450992,
            48.374109
          ],
          [
            -22.428504,
            48.928661
          ],
          [
            -22.144726,
            49.483217
          ],
          [
            -21.368012,
            49.778139
          ],
          [
            -18.595239,
            49.650572
          ],
          [
            -18.091409,
            48.928661
          ],
          [
            -18.053444,
            47.264998
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.487257617829915,
      "length": 4.998267736556849,
      "loops": [
        [
          [
            -22.654643,
            -48.672879
          ],
          [
            -22.669108,
            44.164209
          ],
          [
            -22.539155,
            46.710444
          ],
          [
            -22.697342,
            48.046088
          ],
          [
            -22.679191,
            48.928661
          ],
          [
            -22.47712,
            49.583139
          ],
          [
            -21.922564,
            49.851537
          ],
          [
            -18.595239,
            49.906388
          ],
          [
            -17.073487,
            49.577622
          ],
          [
            21.893424,
            49.483217
          ],
          [
            22.033302,
            48.928661
          ],
          [
            21.981148,
            47.264998
          ],
          [
            21.887219,
            47.129886
          ],
          [
            21.332665,
            47.071282
          ],
          [
            11.905242,
            46.835091
          ],
          [
            -16.377022,
            46.679151
          ],
          [
            -17.486133,
            46.626752
          ],
          [
            -17.63959,
            46.483912
          ],
          [
            -17.818696,
            45.601336
          ],
          [
            -17.816601,
            -44.791
          ],
          [
            -17.691199,
            -46.22813
          ],
          [
            -17.486133,
            -46.449873
          ],
          [
            -16.931579,
            -46.524019
          ],
          [
            21.887219,
            -46.868396
          ],
          [
            22.070017,
            -47.009217
          ],
          [
            22.09602,
            -47.354971
          ],
          [
            22.03865,
            -49.227436
          ],
          [
            14.678013,
            -49.405434
          ],
          [
            -15.478684,
            -49.438204
          ],
          [
            -17.195051,
            -49.490908
          ],
          [
            -17.814152,
            -49.839234
          ],
          [
            -18.595239,
            -49.936327
          ],
          [
            -21.922564,
            -49.891315
          ],
          [
            -22.47712,
            -49.519884
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0005686650000000099,
    0.11968052,
    -0.1195137
  ],
  "construction_scale": 224.8964458692584,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
