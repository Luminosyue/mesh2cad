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
      "start": -2.9726487418676846,
      "length": 3.243008442532605,
      "loops": [
        [
          [
            18.056959,
            -30.142774
          ],
          [
            17.223292,
            -17.739148
          ],
          [
            16.990769,
            -25.934802
          ],
          [
            17.111017,
            -45.104447
          ],
          [
            16.95704,
            -48.975026
          ],
          [
            16.755739,
            -49.576301
          ],
          [
            16.060004,
            -49.724977
          ],
          [
            -28.596845,
            -49.424826
          ],
          [
            -38.882998,
            -49.595287
          ],
          [
            -39.350548,
            -49.555847
          ],
          [
            -39.568553,
            -49.312424
          ],
          [
            -39.429211,
            -46.039554
          ],
          [
            -39.593789,
            -45.104447
          ],
          [
            -39.618552,
            49.341135
          ],
          [
            -39.35788,
            49.808687
          ],
          [
            38.26315,
            49.889813
          ],
          [
            39.198255,
            49.858135
          ],
          [
            39.556878,
            49.471292
          ],
          [
            39.583294,
            -44.169347
          ],
          [
            39.569795,
            -45.234606
          ],
          [
            39.378313,
            -46.039554
          ],
          [
            39.577378,
            -48.545308
          ],
          [
            39.553077,
            -49.312424
          ],
          [
            39.362766,
            -49.779975
          ],
          [
            37.167732,
            -49.779975
          ],
          [
            35.229868,
            -49.312424
          ],
          [
            35.227166,
            -48.844868
          ],
          [
            36.413339,
            -47.442211
          ],
          [
            37.646856,
            -46.507104
          ],
          [
            37.537911,
            -46.018225
          ],
          [
            34.990284,
            -45.859703
          ],
          [
            19.430898,
            -45.778042
          ],
          [
            17.928908,
            -45.572004
          ],
          [
            17.630314,
            -45.23131
          ],
          [
            17.507557,
            -44.767054
          ],
          [
            17.618738,
            -42.299134
          ],
          [
            17.492309,
            -39.493821
          ],
          [
            17.860258,
            -36.220951
          ],
          [
            17.770678,
            -33.415641
          ]
        ],
        [
          [
            -35.947521,
            -45.897719
          ],
          [
            -37.915536,
            -46.039554
          ],
          [
            -37.551554,
            -46.507104
          ],
          [
            -37.227104,
            -46.6456
          ],
          [
            -35.813842,
            -46.974662
          ],
          [
            -33.056198,
            -48.085468
          ],
          [
            -29.999502,
            -48.479607
          ],
          [
            -29.064395,
            -48.767415
          ],
          [
            -25.323975,
            -48.512655
          ],
          [
            -20.648455,
            -48.517872
          ],
          [
            -17.843134,
            -48.217273
          ],
          [
            -12.726937,
            -46.974662
          ],
          [
            -11.297402,
            -46.810128
          ],
          [
            -9.711687,
            -46.039554
          ],
          [
            -17.505741,
            -45.807588
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.2702407947152454,
      "length": 2.7025268531021167,
      "loops": [
        [
          [
            -10.836485,
            27.005695
          ],
          [
            -11.084032,
            25.979216
          ],
          [
            -10.925366,
            17.080019
          ],
          [
            -11.13453,
            12.872048
          ],
          [
            -10.829851,
            12.054491
          ],
          [
            -9.894745,
            11.809905
          ],
          [
            -9.426294,
            11.964632
          ],
          [
            -9.124083,
            12.404495
          ],
          [
            -9.048142,
            12.872048
          ],
          [
            -9.213902,
            14.742257
          ],
          [
            -9.218172,
            23.173902
          ],
          [
            -9.03695,
            26.431067
          ],
          [
            -9.427195,
            27.145436
          ],
          [
            -9.894745,
            27.277252
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.2702407947152454,
      "length": 2.7025268531021167,
      "loops": [
        [
          [
            -5.424319,
            17.080019
          ],
          [
            -5.171904,
            26.431067
          ],
          [
            -5.318522,
            26.89951
          ],
          [
            -5.686774,
            27.179442
          ],
          [
            -6.154325,
            27.253392
          ],
          [
            -6.621882,
            27.251034
          ],
          [
            -7.089431,
            26.968663
          ],
          [
            -7.266252,
            25.963515
          ],
          [
            -6.980058,
            22.690648
          ],
          [
            -6.955327,
            16.612467
          ],
          [
            -7.18441,
            12.872048
          ],
          [
            -7.089431,
            12.325514
          ],
          [
            -6.731722,
            11.936943
          ],
          [
            -6.154325,
            11.829114
          ],
          [
            -5.60801,
            11.936943
          ],
          [
            -5.215931,
            12.397132
          ],
          [
            -5.164302,
            12.872048
          ],
          [
            -5.355139,
            14.274705
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.571267135,
    -0.254130925,
    0.16820321
  ],
  "construction_scale": 94.80666441930629,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
