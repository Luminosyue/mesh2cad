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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            7.99685,
            0.540903
          ],
          [
            8.587927,
            -14.674992
          ],
          [
            8.366532,
            -39.426532
          ],
          [
            8.249417,
            -40.228
          ],
          [
            7.744284,
            -40.689249
          ],
          [
            7.23915,
            -40.499524
          ],
          [
            7.012797,
            -39.931667
          ],
          [
            6.955286,
            -35.638033
          ],
          [
            7.361841,
            -17.837311
          ],
          [
            7.272056,
            -5.835156
          ],
          [
            7.491717,
            -1.477729
          ],
          [
            7.744284,
            0.389193
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            7.43524,
            38.364027
          ],
          [
            7.700443,
            34.575523
          ],
          [
            7.99685,
            34.210743
          ],
          [
            8.273912,
            35.007741
          ],
          [
            8.408665,
            38.111457
          ],
          [
            8.30061,
            39.121727
          ],
          [
            7.997167,
            39.626861
          ],
          [
            7.491717,
            39.831402
          ],
          [
            6.598213,
            39.847056
          ],
          [
            4.808335,
            39.626861
          ],
          [
            4.349435,
            39.374292
          ],
          [
            7.23915,
            38.811889
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            8.800611,
            17.771612
          ],
          [
            8.444513,
            38.869157
          ],
          [
            8.249417,
            39.463695
          ],
          [
            7.744284,
            39.957099
          ],
          [
            3.703216,
            40.122465
          ],
          [
            -5.13662,
            40.14864
          ],
          [
            -7.662287,
            40.08716
          ],
          [
            -8.419989,
            39.842992
          ],
          [
            -8.501838,
            39.626861
          ],
          [
            -8.187312,
            39.374292
          ],
          [
            -7.409722,
            39.111764
          ],
          [
            -0.961047,
            39.05572
          ],
          [
            3.955783,
            39.198083
          ],
          [
            6.986583,
            38.932188
          ],
          [
            7.23915,
            38.875268
          ],
          [
            7.364307,
            38.616591
          ],
          [
            7.573296,
            17.013913
          ],
          [
            7.471633,
            -12.907024
          ],
          [
            6.751134,
            -39.679102
          ],
          [
            6.970939,
            -40.436801
          ],
          [
            7.491717,
            -40.663633
          ],
          [
            7.99685,
            -40.304324
          ],
          [
            8.354156,
            -39.173968
          ],
          [
            8.723772,
            -17.453227
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 24.244424242424248,
      "loops": [
        [
          [
            7.23915,
            39.127382
          ],
          [
            7.55037,
            29.271624
          ],
          [
            7.639606,
            -4.572322
          ],
          [
            7.469876,
            -19.726326
          ],
          [
            6.937101,
            -35.132898
          ],
          [
            6.649913,
            -39.679102
          ],
          [
            6.765033,
            -40.184233
          ],
          [
            7.23915,
            -40.513923
          ],
          [
            7.632688,
            -40.436801
          ],
          [
            7.885965,
            -40.184233
          ],
          [
            8.290282,
            -38.921398
          ],
          [
            8.842148,
            -17.200659
          ],
          [
            9.046395,
            19.029964
          ],
          [
            8.905284,
            27.869801
          ],
          [
            8.454621,
            39.374292
          ],
          [
            7.931825,
            40.131992
          ],
          [
            6.986583,
            40.351243
          ],
          [
            -7.409722,
            40.433531
          ],
          [
            -7.914855,
            40.338966
          ],
          [
            -8.231013,
            39.993004
          ],
          [
            -7.914855,
            39.508083
          ],
          [
            -7.409722,
            39.284162
          ],
          [
            5.471183,
            39.369804
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666667,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            7.615366,
            23.319616
          ],
          [
            7.258971,
            39.374292
          ],
          [
            6.986583,
            39.513702
          ],
          [
            4.208349,
            39.642566
          ],
          [
            -7.157155,
            39.583133
          ],
          [
            -7.914855,
            39.825745
          ],
          [
            -8.143588,
            40.38456
          ],
          [
            -7.662287,
            40.690227
          ],
          [
            -4.884054,
            40.747966
          ],
          [
            7.491717,
            40.537584
          ],
          [
            8.021426,
            40.38456
          ],
          [
            8.449264,
            39.626861
          ],
          [
            8.930229,
            20.541381
          ],
          [
            8.829676,
            -12.797429
          ],
          [
            8.257931,
            -38.416268
          ],
          [
            8.068614,
            -39.173968
          ],
          [
            7.491717,
            -39.596018
          ],
          [
            6.986583,
            -39.400849
          ],
          [
            6.75213,
            -38.668832
          ],
          [
            7.51927,
            -17.453227
          ],
          [
            7.636605,
            -5.330022
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
            6.919677,
            -25.030229
          ],
          [
            7.23915,
            -19.049027
          ],
          [
            7.715587,
            -16.695527
          ],
          [
            7.99685,
            -16.519983
          ],
          [
            8.249417,
            -17.612412
          ],
          [
            8.353905,
            -20.484027
          ],
          [
            8.191675,
            -37.658567
          ],
          [
            8.011372,
            -38.668832
          ],
          [
            7.491717,
            -39.073611
          ],
          [
            6.986583,
            -38.903963
          ],
          [
            6.790844,
            -38.416268
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
            8.307214,
            34.705091
          ],
          [
            8.087086,
            32.807558
          ],
          [
            7.99685,
            32.503711
          ],
          [
            7.744284,
            32.504878
          ],
          [
            7.474367,
            33.504783
          ],
          [
            7.403176,
            35.080657
          ],
          [
            7.693877,
            36.596058
          ],
          [
            7.99685,
            36.836481
          ],
          [
            8.249417,
            35.999862
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
            7.744284,
            40.422817
          ],
          [
            7.744284,
            40.210357
          ],
          [
            7.539505,
            40.086569
          ],
          [
            7.251554,
            40.131992
          ],
          [
            7.140725,
            40.38456
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.003569835000000021,
    0.023025030000000002,
    0.00025501499999999733
  ],
  "construction_scale": 102.42706985211713,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
