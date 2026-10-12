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
      "start": -2.9118016306691064,
      "length": 2.1177903852791213,
      "loops": [
        [
          [
            0.23799,
            -33.532969
          ],
          [
            -0.493107,
            -34.264674
          ],
          [
            -0.500784,
            -35.074392
          ],
          [
            -0.40199,
            -35.545281
          ],
          [
            0.217335,
            -36.218969
          ],
          [
            0.70888,
            -36.264606
          ],
          [
            1.563478,
            -35.795228
          ],
          [
            1.793678,
            -35.324341
          ],
          [
            1.806143,
            -34.853451
          ],
          [
            1.597512,
            -34.382561
          ],
          [
            0.70888,
            -33.60199
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.9118016306691064,
      "length": 2.1177903852791213,
      "loops": [
        [
          [
            -0.232897,
            -49.040627
          ],
          [
            0.751824,
            -48.772735
          ],
          [
            1.270037,
            -48.038348
          ],
          [
            1.282346,
            -47.567461
          ],
          [
            1.047353,
            -47.096567
          ],
          [
            0.23799,
            -46.37426
          ],
          [
            -0.336096,
            -46.475239
          ],
          [
            -0.922267,
            -47.096567
          ],
          [
            -1.133464,
            -47.567461
          ],
          [
            -1.038434,
            -48.259288
          ],
          [
            -0.703787,
            -48.7781
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.9118016306691064,
      "length": 2.1177903852791213,
      "loops": [
        [
          [
            0.806452,
            19.024563
          ],
          [
            1.650659,
            19.375706
          ],
          [
            1.986751,
            19.769696
          ],
          [
            2.118936,
            20.240585
          ],
          [
            2.035653,
            20.711475
          ],
          [
            1.699656,
            21.246567
          ],
          [
            1.17977,
            21.576182
          ],
          [
            0.70888,
            21.666952
          ],
          [
            0.087307,
            21.403305
          ],
          [
            -0.209159,
            20.240585
          ],
          [
            0.004922,
            19.548755
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.9118016306691064,
      "length": 2.1177903852791213,
      "loops": [
        [
          [
            -0.115089,
            39.572888
          ],
          [
            -0.208141,
            38.791854
          ],
          [
            0.068992,
            37.913434
          ],
          [
            0.70888,
            37.631976
          ],
          [
            1.348247,
            37.913434
          ],
          [
            1.79518,
            38.605265
          ],
          [
            1.829252,
            39.076153
          ],
          [
            1.650659,
            39.56452
          ],
          [
            0.70888,
            40.315516
          ],
          [
            0.435178,
            40.291633
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.7941277174552117,
      "length": 2.4707360374814367,
      "loops": [
        [
          [
            1.306195,
            -33.440784
          ],
          [
            1.62075,
            18.827918
          ],
          [
            2.192503,
            19.769696
          ],
          [
            2.256167,
            20.240585
          ],
          [
            2.121549,
            20.844419
          ],
          [
            1.625148,
            21.653254
          ],
          [
            1.582785,
            22.124143
          ],
          [
            1.677258,
            37.192596
          ],
          [
            1.998464,
            38.605265
          ],
          [
            1.717233,
            40.488822
          ],
          [
            1.793745,
            48.493939
          ],
          [
            1.718628,
            49.435716
          ],
          [
            1.346623,
            49.906607
          ],
          [
            -0.072255,
            49.978272
          ],
          [
            -0.583793,
            49.435716
          ],
          [
            -0.669725,
            48.493939
          ],
          [
            -0.94053,
            -25.435668
          ],
          [
            -1.020932,
            -33.440784
          ],
          [
            -1.177958,
            -35.324341
          ],
          [
            -1.045461,
            -37.678785
          ],
          [
            -1.071628,
            -46.625681
          ],
          [
            -1.634033,
            -47.567461
          ],
          [
            -1.697381,
            -48.038348
          ],
          [
            -1.174678,
            -49.477658
          ],
          [
            -0.703787,
            -49.849473
          ],
          [
            -0.232897,
            -49.929124
          ],
          [
            0.70888,
            -49.92059
          ],
          [
            1.17977,
            -49.675768
          ],
          [
            1.57319,
            -48.038348
          ],
          [
            1.216558,
            -46.625681
          ],
          [
            1.286448,
            -36.511135
          ],
          [
            1.783068,
            -34.853451
          ],
          [
            1.773078,
            -34.382561
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6764918479609983,
      "length": 1.2354262547733321,
      "loops": [
        [
          [
            -0.232897,
            39.34511
          ],
          [
            0.23799,
            40.187136
          ],
          [
            0.70888,
            40.311461
          ],
          [
            1.679733,
            39.547044
          ],
          [
            1.832639,
            39.000908
          ],
          [
            1.666705,
            38.134375
          ],
          [
            0.70888,
            37.289974
          ],
          [
            0.23799,
            37.580399
          ],
          [
            -0.082715,
            38.134375
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6764918479609983,
      "length": 1.2354262547733321,
      "loops": [
        [
          [
            -0.232897,
            -46.993832
          ],
          [
            0.70888,
            -47.453643
          ],
          [
            1.181424,
            -48.038348
          ],
          [
            0.342696,
            -49.451015
          ],
          [
            -0.157653,
            -49.57525
          ],
          [
            -0.5161,
            -49.451015
          ],
          [
            -1.167395,
            -48.038348
          ],
          [
            -1.062762,
            -47.567461
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6764918479609983,
      "length": 1.2354262547733321,
      "loops": [
        [
          [
            -0.232897,
            -35.778227
          ],
          [
            0.23799,
            -35.9427
          ],
          [
            0.709835,
            -35.786241
          ],
          [
            1.081106,
            -35.324341
          ],
          [
            0.924642,
            -34.382561
          ],
          [
            0.23799,
            -34.126961
          ],
          [
            -0.232897,
            -34.284714
          ],
          [
            -0.437341,
            -35.324341
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6764918479609983,
      "length": 1.2354262547733321,
      "loops": [
        [
          [
            0.23799,
            21.457389
          ],
          [
            0.054867,
            20.711475
          ],
          [
            0.23799,
            19.371748
          ],
          [
            0.714945,
            20.23452
          ],
          [
            0.827059,
            21.182364
          ],
          [
            0.70888,
            21.355955
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.327980775,
    -0.18239058500000002,
    -0.25290543
  ],
  "construction_scale": 95.48327537387122,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
