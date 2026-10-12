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
      "start": -38.19179994037207,
      "length": 4.630836755679078,
      "loops": [
        [
          [
            49.873915,
            1.241861
          ],
          [
            49.912057,
            -6.307345
          ],
          [
            49.642376,
            -9.81434
          ],
          [
            49.193887,
            -10.788431
          ],
          [
            48.627835,
            -11.148746
          ],
          [
            47.897267,
            -11.324696
          ],
          [
            -47.076617,
            -11.330362
          ],
          [
            -47.807185,
            -11.206678
          ],
          [
            -48.607115,
            -10.788431
          ],
          [
            -48.985132,
            -10.155539
          ],
          [
            -49.114792,
            -9.473141
          ],
          [
            -49.225347,
            -0.803998
          ],
          [
            -48.796022,
            7.232254
          ],
          [
            -48.294228,
            9.263348
          ],
          [
            -47.807185,
            9.663192
          ],
          [
            -46.833092,
            9.9264
          ],
          [
            47.653741,
            9.959716
          ],
          [
            48.384314,
            9.783996
          ],
          [
            48.871356,
            9.450472
          ],
          [
            49.339806,
            8.206345
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -33.56249085669061,
      "length": 18.518764006723465,
      "loops": [
        [
          [
            49.167356,
            7.475777
          ],
          [
            48.908856,
            9.410567
          ],
          [
            48.627835,
            10.345573
          ],
          [
            48.140788,
            10.798754
          ],
          [
            47.41022,
            10.986654
          ],
          [
            43.500463,
            10.824246
          ],
          [
            26.22374,
            10.72745
          ],
          [
            -47.320138,
            10.626664
          ],
          [
            -47.911389,
            10.39805
          ],
          [
            -48.562854,
            9.667481
          ],
          [
            -48.928439,
            7.94943
          ],
          [
            -49.596683,
            -1.304435
          ],
          [
            -49.405784,
            -9.570818
          ],
          [
            -49.158172,
            -10.544908
          ],
          [
            -48.772937,
            -10.964202
          ],
          [
            -47.807185,
            -11.353681
          ],
          [
            -45.385348,
            -11.462352
          ],
          [
            47.897267,
            -11.363452
          ],
          [
            48.871356,
            -11.056866
          ],
          [
            49.453447,
            -10.553407
          ],
          [
            49.751486,
            -8.596727
          ],
          [
            49.793344,
            -1.534566
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -15.045254521964758,
      "length": 34.721345799608585,
      "loops": [
        [
          [
            46.679652,
            -11.232154
          ],
          [
            -40.257976,
            -11.316545
          ],
          [
            -46.833092,
            -11.267643
          ],
          [
            -48.050706,
            -11.12749
          ],
          [
            -48.781274,
            -10.764207
          ],
          [
            -49.285031,
            -10.301386
          ],
          [
            -49.734167,
            -8.238893
          ],
          [
            -49.816448,
            -0.93321
          ],
          [
            -48.75192,
            9.667481
          ],
          [
            -48.050706,
            10.74995
          ],
          [
            -46.833092,
            11.079651
          ],
          [
            24.876913,
            11.030302
          ],
          [
            47.166699,
            11.252552
          ],
          [
            47.897267,
            11.124534
          ],
          [
            48.384314,
            10.789045
          ],
          [
            48.736934,
            9.911005
          ],
          [
            48.997833,
            7.962822
          ],
          [
            49.579446,
            -0.560475
          ],
          [
            49.636935,
            -9.083772
          ],
          [
            49.477366,
            -10.057863
          ],
          [
            49.236002,
            -10.544908
          ],
          [
            48.140788,
            -11.108028
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.674563605646213,
      "length": 9.260145839360533,
      "loops": [
        [
          [
            -41.232069,
            -10.630381
          ],
          [
            46.915178,
            -10.552075
          ],
          [
            47.897267,
            -10.460703
          ],
          [
            48.627835,
            -10.112012
          ],
          [
            48.873481,
            -9.81434
          ],
          [
            49.056623,
            -9.083772
          ],
          [
            49.000507,
            -2.265134
          ],
          [
            48.571599,
            9.180436
          ],
          [
            48.379784,
            10.882741
          ],
          [
            48.209251,
            11.128618
          ],
          [
            47.41022,
            11.570571
          ],
          [
            46.679652,
            11.652171
          ],
          [
            -46.581575,
            11.629967
          ],
          [
            -48.050706,
            11.269478
          ],
          [
            -48.435439,
            10.885095
          ],
          [
            -48.639517,
            10.39805
          ],
          [
            -49.742145,
            -0.560475
          ],
          [
            -49.787909,
            -6.648544
          ],
          [
            -49.396761,
            -9.570818
          ],
          [
            -48.781274,
            -10.190392
          ],
          [
            -48.050706,
            -10.510643
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.93318177300913,
      "length": 9.260145839360554,
      "loops": [
        [
          [
            46.6924,
            11.694223
          ],
          [
            -46.102524,
            11.67598
          ],
          [
            -47.320138,
            11.552378
          ],
          [
            -47.807185,
            11.361662
          ],
          [
            -48.335427,
            10.885095
          ],
          [
            -48.774905,
            8.69339
          ],
          [
            -49.701053,
            -1.778088
          ],
          [
            -49.716209,
            -6.87932
          ],
          [
            -49.436413,
            -9.083772
          ],
          [
            -49.226769,
            -9.570818
          ],
          [
            -48.537753,
            -10.106221
          ],
          [
            -47.076617,
            -10.338959
          ],
          [
            47.179446,
            -10.281252
          ],
          [
            48.128041,
            -10.073681
          ],
          [
            48.595141,
            -9.570818
          ],
          [
            48.758395,
            -8.827502
          ],
          [
            48.840862,
            -2.995703
          ],
          [
            48.631569,
            9.180436
          ],
          [
            48.384314,
            10.809247
          ],
          [
            48.140788,
            11.190939
          ],
          [
            47.41022,
            11.593041
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.013241245000000013,
    -0.0034446049999999895,
    0.01715797999999996
  ],
  "construction_scale": 49.37966719022776,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
