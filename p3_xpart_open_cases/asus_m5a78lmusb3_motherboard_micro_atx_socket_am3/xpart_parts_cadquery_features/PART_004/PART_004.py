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
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.0,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            8.936695,
            -1.135557
          ],
          [
            -9.189101,
            -1.083762
          ],
          [
            -9.699686,
            -0.863516
          ],
          [
            -9.93556,
            -0.494754
          ],
          [
            -10.008134,
            1.037002
          ],
          [
            -10.210273,
            1.311467
          ],
          [
            -10.473432,
            1.037002
          ],
          [
            -10.301454,
            -1.005337
          ],
          [
            -9.699686,
            -1.493482
          ],
          [
            -9.189101,
            -1.596558
          ],
          [
            8.936695,
            -1.651979
          ],
          [
            9.44728,
            -1.50695
          ],
          [
            10.338231,
            -0.239459
          ],
          [
            10.21316,
            0.017428
          ],
          [
            9.957866,
            -0.001036
          ],
          [
            9.213762,
            -1.005337
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 18.18381818181818,
      "loops": [
        [
          [
            5.60291,
            -1.115079
          ],
          [
            7.149644,
            -0.926989
          ],
          [
            8.936695,
            -1.018005
          ],
          [
            9.898095,
            -0.494754
          ],
          [
            10.371214,
            0.52642
          ],
          [
            10.21316,
            0.771511
          ],
          [
            9.957866,
            0.694607
          ],
          [
            9.44728,
            -0.197251
          ],
          [
            8.681402,
            -0.506171
          ],
          [
            7.149644,
            -0.397776
          ],
          [
            5.60291,
            -0.568475
          ],
          [
            3.064958,
            -0.410511
          ],
          [
            -6.125586,
            -0.445241
          ],
          [
            -9.444393,
            -0.349882
          ],
          [
            -9.845127,
            0.015832
          ],
          [
            -9.971865,
            0.781711
          ],
          [
            -10.210273,
            0.985817
          ],
          [
            -10.437179,
            0.781711
          ],
          [
            -10.324569,
            -0.239459
          ],
          [
            -9.954979,
            -0.670401
          ],
          [
            -9.444393,
            -0.918543
          ],
          [
            3.064958,
            -0.895681
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.636363636363633,
      "length": 6.062606060606069,
      "loops": [
        [
          [
            -9.444393,
            -0.695686
          ],
          [
            8.681402,
            -0.984413
          ],
          [
            9.424032,
            -0.750046
          ],
          [
            10.163204,
            0.52642
          ],
          [
            9.957866,
            0.749945
          ],
          [
            9.702573,
            0.665695
          ],
          [
            9.196204,
            -0.239459
          ],
          [
            8.681402,
            -0.449293
          ],
          [
            0.512029,
            -0.223954
          ],
          [
            -9.189101,
            -0.177445
          ],
          [
            -9.800052,
            0.015832
          ],
          [
            -10.210273,
            0.936308
          ],
          [
            -10.465565,
            0.794613
          ],
          [
            -10.516417,
            0.52642
          ],
          [
            -10.297636,
            -0.239459
          ],
          [
            -9.954979,
            -0.536832
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.696969696969703,
      "length": 21.214121212121203,
      "loops": [
        [
          [
            -9.349336,
            -0.537314
          ],
          [
            8.936695,
            -0.663342
          ],
          [
            9.383766,
            -0.494754
          ],
          [
            9.650773,
            0.015832
          ],
          [
            9.726999,
            0.781711
          ],
          [
            9.44728,
            0.866573
          ],
          [
            9.066164,
            0.015832
          ],
          [
            8.681402,
            -0.138786
          ],
          [
            -7.306993,
            -0.09108
          ],
          [
            -9.444393,
            0.028486
          ],
          [
            -9.796699,
            0.271124
          ],
          [
            -10.079414,
            1.292298
          ],
          [
            -10.316226,
            1.292298
          ],
          [
            -10.435705,
            1.037002
          ],
          [
            -10.265028,
            0.015832
          ],
          [
            -9.699686,
            -0.450401
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
            -3.82795,
            -0.497785
          ],
          [
            9.191988,
            -0.479326
          ],
          [
            9.712466,
            0.271124
          ],
          [
            9.705599,
            0.781711
          ],
          [
            9.392273,
            0.781711
          ],
          [
            8.936695,
            0.056414
          ],
          [
            8.681402,
            0.014593
          ],
          [
            -7.657343,
            0.082918
          ],
          [
            -9.548363,
            0.271124
          ],
          [
            -9.843994,
            0.52642
          ],
          [
            -10.003537,
            1.292298
          ],
          [
            -10.210273,
            1.522762
          ],
          [
            -10.474308,
            1.292298
          ],
          [
            -10.347608,
            0.271124
          ],
          [
            -9.954979,
            -0.167819
          ],
          [
            -9.444393,
            -0.320942
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.010794175000000017,
    -0.034549369999999996,
    -0.932385925
  ],
  "construction_scale": 51.766320431256105,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
