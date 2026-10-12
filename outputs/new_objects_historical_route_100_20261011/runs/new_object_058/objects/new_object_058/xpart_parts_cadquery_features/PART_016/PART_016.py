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
      "start": -42.780044927138235,
      "length": 10.372631184133631,
      "loops": [
        [
          [
            35.810156,
            34.489857
          ],
          [
            35.896803,
            -35.073053
          ],
          [
            36.390927,
            -35.901189
          ],
          [
            37.233837,
            -36.276475
          ],
          [
            42.202619,
            -36.255823
          ],
          [
            43.030745,
            -36.106483
          ],
          [
            43.340588,
            -35.901189
          ],
          [
            43.896095,
            -35.073053
          ],
          [
            44.01958,
            -33.4168
          ],
          [
            44.006961,
            33.065647
          ],
          [
            43.823159,
            35.317987
          ],
          [
            43.030745,
            36.312691
          ],
          [
            42.202619,
            36.516018
          ],
          [
            37.233837,
            36.31583
          ],
          [
            36.40571,
            35.887701
          ],
          [
            35.996872,
            35.317987
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -32.40912494480169,
      "length": 5.1871711929653515,
      "loops": [
        [
          [
            43.859972,
            34.947132
          ],
          [
            43.869218,
            -35.073053
          ],
          [
            43.349679,
            -35.901189
          ],
          [
            43.030745,
            -36.1303
          ],
          [
            42.202619,
            -36.336776
          ],
          [
            38.061967,
            -36.458067
          ],
          [
            37.233837,
            -36.319598
          ],
          [
            36.40571,
            -35.887451
          ],
          [
            35.98034,
            -35.073053
          ],
          [
            35.872955,
            -34.244926
          ],
          [
            35.814819,
            32.84897
          ],
          [
            35.836988,
            34.489857
          ],
          [
            36.040841,
            35.317987
          ],
          [
            36.773971,
            36.146113
          ],
          [
            38.061967,
            36.512196
          ],
          [
            42.202619,
            36.562852
          ],
          [
            43.258747,
            36.146113
          ],
          [
            43.806987,
            35.317987
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -27.223664953633424,
      "length": 5.187171192965359,
      "loops": [
        [
          [
            37.233837,
            -35.282965
          ],
          [
            -43.922894,
            -35.131428
          ],
          [
            -45.579153,
            -36.375626
          ],
          [
            -47.235413,
            -36.636061
          ],
          [
            -48.891673,
            -36.502505
          ],
          [
            -49.664583,
            -35.901189
          ],
          [
            -49.928639,
            -35.073053
          ],
          [
            -49.958333,
            -34.244926
          ],
          [
            -49.989933,
            33.661724
          ],
          [
            -49.912866,
            35.317987
          ],
          [
            -49.449309,
            36.146113
          ],
          [
            -48.891673,
            36.508436
          ],
          [
            -47.235413,
            36.654315
          ],
          [
            -45.579153,
            36.495041
          ],
          [
            -43.922894,
            35.666209
          ],
          [
            20.671241,
            35.732635
          ],
          [
            36.40571,
            35.58647
          ],
          [
            38.8901,
            36.202145
          ],
          [
            41.374489,
            36.177348
          ],
          [
            42.202619,
            36.017293
          ],
          [
            42.959992,
            35.317987
          ],
          [
            43.208807,
            34.489857
          ],
          [
            43.242283,
            33.661724
          ],
          [
            43.244743,
            -34.244926
          ],
          [
            42.855469,
            -35.073053
          ],
          [
            42.202619,
            -35.550679
          ],
          [
            41.374489,
            -35.736597
          ],
          [
            38.8901,
            -35.624424
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.03820496246515,
      "length": 54.44904110906393,
      "loops": [
        [
          [
            43.336187,
            -33.4168
          ],
          [
            43.274169,
            34.489857
          ],
          [
            43.042205,
            35.317987
          ],
          [
            42.202619,
            36.04766
          ],
          [
            41.374489,
            36.175424
          ],
          [
            38.061967,
            36.087045
          ],
          [
            36.40571,
            35.562768
          ],
          [
            30.608802,
            35.714178
          ],
          [
            4.348545,
            35.757046
          ],
          [
            -43.922894,
            35.650763
          ],
          [
            -44.751024,
            35.94585
          ],
          [
            -45.579153,
            36.464173
          ],
          [
            -46.407283,
            36.607291
          ],
          [
            -48.891673,
            36.474798
          ],
          [
            -49.399882,
            36.146113
          ],
          [
            -49.719802,
            35.699798
          ],
          [
            -49.970042,
            34.489857
          ],
          [
            -49.957487,
            -34.244926
          ],
          [
            -49.919673,
            -35.073053
          ],
          [
            -49.667093,
            -35.901189
          ],
          [
            -48.891673,
            -36.502254
          ],
          [
            -47.235413,
            -36.61501
          ],
          [
            -45.579153,
            -36.351466
          ],
          [
            -44.751024,
            -35.576678
          ],
          [
            -43.922894,
            -35.156401
          ],
          [
            31.436928,
            -35.200186
          ],
          [
            37.233837,
            -35.257558
          ],
          [
            39.718226,
            -35.773714
          ],
          [
            41.374489,
            -35.744113
          ],
          [
            42.202619,
            -35.522674
          ],
          [
            43.030745,
            -34.816054
          ],
          [
            43.305084,
            -34.244926
          ]
        ],
        [
          [
            -44.5725,
            -27.619885
          ],
          [
            -44.593896,
            28.692949
          ],
          [
            -44.400258,
            29.521078
          ],
          [
            -43.922894,
            30.074776
          ],
          [
            -43.142304,
            30.349205
          ],
          [
            36.629689,
            30.349205
          ],
          [
            37.233837,
            30.066587
          ],
          [
            37.668086,
            29.521078
          ],
          [
            37.948466,
            28.692949
          ],
          [
            37.978353,
            27.864815
          ],
          [
            37.887166,
            -28.448011
          ],
          [
            37.559881,
            -29.276151
          ],
          [
            37.233837,
            -29.565684
          ],
          [
            36.40571,
            -29.776864
          ],
          [
            -43.094764,
            -29.783077
          ],
          [
            -43.922894,
            -29.594394
          ],
          [
            -44.27524,
            -29.276151
          ],
          [
            -44.537426,
            -28.448011
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 32.40912494480169,
      "length": 10.372631184133631,
      "loops": [
        [
          [
            43.824642,
            -34.932077
          ],
          [
            44.033632,
            -30.104274
          ],
          [
            44.094297,
            -18.107759
          ],
          [
            44.031575,
            33.661724
          ],
          [
            43.695723,
            35.317987
          ],
          [
            43.030745,
            35.956053
          ],
          [
            42.202619,
            36.207661
          ],
          [
            38.061967,
            36.260532
          ],
          [
            37.233837,
            36.135042
          ],
          [
            36.349166,
            35.317987
          ],
          [
            36.097747,
            34.489857
          ],
          [
            35.973971,
            32.408169
          ],
          [
            36.09362,
            -34.244926
          ],
          [
            36.204652,
            -35.073053
          ],
          [
            36.650855,
            -35.901189
          ],
          [
            37.233837,
            -36.243295
          ],
          [
            38.061967,
            -36.368757
          ],
          [
            42.202619,
            -36.21694
          ],
          [
            43.137309,
            -35.901189
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.349278225,
    -0.089875835,
    0.071604095
  ],
  "construction_scale": 335.8435737356489,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
