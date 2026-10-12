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
      "start": -2.9580847593991524,
      "length": 0.3586740518023942,
      "loops": [
        [
          [
            0.080664,
            -47.215617
          ],
          [
            0.108641,
            -14.060794
          ],
          [
            -0.022965,
            -12.62048
          ],
          [
            0.110699,
            -8.045709
          ],
          [
            0.117498,
            10.933
          ],
          [
            -0.072585,
            24.187999
          ],
          [
            0.057256,
            47.115989
          ],
          [
            -0.253511,
            49.191354
          ],
          [
            -0.698511,
            49.431779
          ],
          [
            -1.556945,
            49.461009
          ],
          [
            -1.924364,
            49.431148
          ],
          [
            -2.041406,
            48.429265
          ],
          [
            -2.047032,
            -47.143768
          ],
          [
            -1.924364,
            -49.533281
          ],
          [
            -0.121788,
            -49.482967
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.599529030987134,
      "length": 1.9721748296564763,
      "loops": [
        [
          [
            -2.513666,
            -49.148797
          ],
          [
            -2.492127,
            49.431779
          ],
          [
            -2.258538,
            49.858056
          ],
          [
            -1.924364,
            49.98522
          ],
          [
            -0.58768,
            49.988356
          ],
          [
            0.071295,
            49.765953
          ],
          [
            0.271597,
            48.74633
          ],
          [
            0.259324,
            31.052351
          ],
          [
            0.498158,
            26.10537
          ],
          [
            0.749009,
            25.569886
          ],
          [
            1.083177,
            25.488867
          ],
          [
            1.186545,
            24.048041
          ],
          [
            1.083177,
            23.540183
          ],
          [
            0.414833,
            23.240611
          ],
          [
            0.368402,
            23.018947
          ],
          [
            0.430734,
            19.022179
          ],
          [
            0.225341,
            18.332996
          ],
          [
            0.327394,
            -3.367308
          ],
          [
            0.296011,
            -8.398527
          ],
          [
            0.160599,
            -9.716566
          ],
          [
            0.34487,
            -10.384909
          ],
          [
            0.130452,
            -13.05828
          ],
          [
            0.327314,
            -13.726623
          ],
          [
            0.349436,
            -20.410052
          ],
          [
            0.249562,
            -48.814627
          ],
          [
            0.080664,
            -49.715097
          ],
          [
            -0.266801,
            -49.913829
          ],
          [
            -0.92185,
            -49.988203
          ],
          [
            -2.258538,
            -49.857601
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.6274725247210338,
      "length": 1.9721748296564767,
      "loops": [
        [
          [
            -2.514012,
            -49.148797
          ],
          [
            -2.540448,
            49.097609
          ],
          [
            -2.258538,
            49.862292
          ],
          [
            -0.92185,
            49.992104
          ],
          [
            -0.444077,
            49.765953
          ],
          [
            -0.355139,
            48.763439
          ],
          [
            -0.452405,
            31.386523
          ],
          [
            0.206155,
            30.049836
          ],
          [
            0.414833,
            28.954025
          ],
          [
            0.842113,
            28.044807
          ],
          [
            0.770728,
            27.710637
          ],
          [
            0.984088,
            27.042292
          ],
          [
            0.590598,
            26.198187
          ],
          [
            0.561645,
            23.700578
          ],
          [
            0.167827,
            22.945073
          ],
          [
            0.249027,
            19.35635
          ],
          [
            0.187876,
            19.022179
          ],
          [
            -0.281468,
            18.619556
          ],
          [
            -0.421779,
            18.019665
          ],
          [
            -0.451069,
            -48.814627
          ],
          [
            -0.58768,
            -49.678831
          ],
          [
            -0.92185,
            -49.961544
          ],
          [
            -1.256025,
            -49.986187
          ],
          [
            -2.258538,
            -49.845387
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.6274725247210338,
      "length": 1.9721748296564767,
      "loops": [
        [
          [
            2.085691,
            28.503934
          ],
          [
            2.085691,
            28.102663
          ],
          [
            1.835828,
            28.294672
          ],
          [
            1.795579,
            28.044807
          ],
          [
            1.726967,
            28.044807
          ],
          [
            1.716252,
            28.378978
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.344583981545067,
      "length": 0.35867405180239376,
      "loops": [
        [
          [
            -0.552957,
            -49.298988
          ],
          [
            -0.519339,
            46.274046
          ],
          [
            -0.370373,
            48.763439
          ],
          [
            -0.481882,
            49.765953
          ],
          [
            -0.92185,
            49.961595
          ],
          [
            -1.924364,
            49.943537
          ],
          [
            -2.319249,
            49.765953
          ],
          [
            -2.482296,
            49.431779
          ],
          [
            -2.567323,
            48.095095
          ],
          [
            -2.381206,
            47.092581
          ],
          [
            -2.359975,
            41.929816
          ],
          [
            -2.35213,
            -41.278874
          ],
          [
            -2.462963,
            -43.133707
          ],
          [
            -2.343455,
            -49.482967
          ],
          [
            -1.924364,
            -49.87218
          ],
          [
            -0.92185,
            -49.860857
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.7031397099570849,
      "length": 1.2550633728324398,
      "loops": [
        [
          [
            -1.924364,
            49.704037
          ],
          [
            -0.92185,
            49.713974
          ],
          [
            -0.515966,
            49.431779
          ],
          [
            -0.436874,
            48.095095
          ],
          [
            -0.58768,
            47.728056
          ],
          [
            -0.92185,
            47.55488
          ],
          [
            -1.924364,
            47.558741
          ],
          [
            -2.258538,
            47.748859
          ],
          [
            -2.385002,
            48.095095
          ],
          [
            -2.395616,
            49.097609
          ],
          [
            -2.258538,
            49.470604
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.7031397099570849,
      "length": 1.2550633728324398,
      "loops": [
        [
          [
            -2.258538,
            -43.188464
          ],
          [
            -1.924364,
            -41.987511
          ],
          [
            -0.92185,
            -42.025521
          ],
          [
            -0.699042,
            -42.799539
          ],
          [
            -0.76197,
            -43.467883
          ],
          [
            -0.92185,
            -43.669297
          ],
          [
            -1.924364,
            -43.711781
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.481430165,
    0.00018885499999998778,
    -0.228683435
  ],
  "construction_scale": 135.52140961130576,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
