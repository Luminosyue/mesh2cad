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
      "start": -1.10265800791142,
      "length": 0.33418289659650446,
      "loops": [
        [
          [
            -36.206088,
            0.966907
          ],
          [
            4.594034,
            0.897127
          ],
          [
            6.369958,
            0.859307
          ],
          [
            6.387104,
            0.695145
          ],
          [
            0.0453,
            0.508132
          ],
          [
            -30.464704,
            0.451856
          ],
          [
            -36.448542,
            0.262453
          ],
          [
            -43.250002,
            0.387218
          ],
          [
            -45.47972,
            0.192422
          ],
          [
            -47.358863,
            -0.738564
          ],
          [
            -48.763811,
            -0.352952
          ],
          [
            -49.222592,
            0.131952
          ],
          [
            -48.99655,
            0.616856
          ],
          [
            -48.086217,
            1.015652
          ],
          [
            -45.904154,
            0.923798
          ],
          [
            -44.449445,
            1.114944
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.10265800791142,
      "length": 0.33418289659650446,
      "loops": [
        [
          [
            25.134165,
            0.670602
          ],
          [
            28.909985,
            0.131952
          ],
          [
            28.313993,
            -0.138454
          ],
          [
            25.018533,
            -0.237319
          ],
          [
            24.005835,
            0.131952
          ],
          [
            23.425574,
            0.616856
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.10265800791142,
      "length": 0.33418289659650446,
      "loops": [
        [
          [
            29.553095,
            0.077151
          ],
          [
            29.17184,
            0.131952
          ],
          [
            29.674111,
            0.131952
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.7685192176352321,
      "length": 1.537082541590781,
      "loops": [
        [
          [
            36.771843,
            -1.38122
          ],
          [
            24.891715,
            -1.43726
          ],
          [
            23.921908,
            -1.10891
          ],
          [
            22.320346,
            -0.231564
          ],
          [
            21.350539,
            -0.034301
          ],
          [
            2.728511,
            0.031402
          ],
          [
            -34.024024,
            -0.014001
          ],
          [
            -35.07738,
            -0.205877
          ],
          [
            -35.963637,
            -0.960469
          ],
          [
            -36.430777,
            -1.090288
          ],
          [
            -39.532477,
            -0.062293
          ],
          [
            -43.722091,
            0.119102
          ],
          [
            -44.934345,
            -0.163579
          ],
          [
            -47.116413,
            -1.202076
          ],
          [
            -49.298476,
            -0.363012
          ],
          [
            -49.546128,
            -0.110498
          ],
          [
            -49.680781,
            0.374402
          ],
          [
            -49.39427,
            0.859307
          ],
          [
            -48.813572,
            1.186302
          ],
          [
            -46.534117,
            1.446604
          ],
          [
            47.682164,
            1.50925
          ],
          [
            49.195878,
            1.344211
          ],
          [
            49.60725,
            1.101757
          ],
          [
            49.771198,
            0.763709
          ],
          [
            49.531015,
            0.131952
          ],
          [
            48.651973,
            -0.249029
          ],
          [
            47.682164,
            -0.303402
          ],
          [
            46.323053,
            0.001571
          ],
          [
            42.833133,
            0.004709
          ],
          [
            41.525276,
            -0.28979
          ],
          [
            39.19636,
            -1.226223
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7685192176352325,
      "length": 0.3341828965965048,
      "loops": [
        [
          [
            25.134165,
            0.908252
          ],
          [
            40.89352,
            0.874678
          ],
          [
            41.620874,
            0.791162
          ],
          [
            41.894743,
            0.616856
          ],
          [
            40.946109,
            0.321813
          ],
          [
            39.863411,
            -0.352952
          ],
          [
            38.469006,
            -0.699368
          ],
          [
            26.831326,
            -0.967416
          ],
          [
            24.562224,
            -0.750817
          ],
          [
            23.812243,
            -0.352952
          ],
          [
            22.65838,
            0.616856
          ],
          [
            23.686534,
            0.852229
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7685192176352325,
      "length": 0.3341828965965048,
      "loops": [
        [
          [
            -48.394178,
            0.374402
          ],
          [
            -48.489221,
            0.131952
          ],
          [
            -48.169023,
            -0.110498
          ],
          [
            -47.116413,
            -0.398412
          ],
          [
            -46.038753,
            0.374402
          ],
          [
            -46.009839,
            0.616856
          ],
          [
            -47.116413,
            0.688721
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7685192176352325,
      "length": 0.3341828965965048,
      "loops": [
        [
          [
            45.940912,
            0.859307
          ],
          [
            48.167069,
            0.934784
          ],
          [
            48.585346,
            0.859307
          ],
          [
            48.851473,
            0.616856
          ],
          [
            48.545418,
            0.374402
          ],
          [
            47.924618,
            0.347972
          ],
          [
            46.042952,
            0.616856
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.008219740000000031,
    0.899806245,
    -0.08647698000000001
  ],
  "construction_scale": 49.162463357987,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
