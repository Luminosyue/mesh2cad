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
      "start": -21.733420555701127,
      "length": 7.903931357077183,
      "loops": [
        [
          [
            -0.054148,
            -44.289804
          ],
          [
            0.483136,
            17.508333
          ],
          [
            1.262787,
            48.407401
          ],
          [
            1.155307,
            49.437372
          ],
          [
            0.726785,
            49.975029
          ],
          [
            0.173334,
            49.437372
          ],
          [
            -0.316178,
            36.755131
          ],
          [
            -0.620146,
            14.610798
          ],
          [
            -0.622176,
            -8.563504
          ],
          [
            -0.962377,
            -47.894695
          ],
          [
            -0.871801,
            -48.924666
          ],
          [
            -0.303182,
            -49.144817
          ],
          [
            -0.1625,
            -48.924666
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.830358535446171,
      "length": 31.613117417842048,
      "loops": [
        [
          [
            0.598314,
            14.373072
          ],
          [
            0.20672,
            -40.215285
          ],
          [
            0.033849,
            -46.349742
          ],
          [
            -0.301878,
            -49.439652
          ],
          [
            -0.818168,
            -49.676682
          ],
          [
            -1.016816,
            -49.439652
          ],
          [
            -1.034689,
            -48.924666
          ],
          [
            -0.728902,
            -46.349742
          ],
          [
            -0.60282,
            -42.744851
          ],
          [
            -0.430132,
            -14.466059
          ],
          [
            -0.142097,
            -5.150984
          ],
          [
            -0.226057,
            12.313133
          ],
          [
            0.108171,
            43.772542
          ],
          [
            0.299919,
            48.407401
          ],
          [
            0.726785,
            48.766927
          ],
          [
            1.130369,
            48.407401
          ],
          [
            1.180173,
            47.892419
          ],
          [
            1.266415,
            39.13768
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 17.78188954557365,
      "length": 3.952400346949703,
      "loops": [
        [
          [
            -0.59904,
            20.59824
          ],
          [
            -0.357317,
            27.683337
          ],
          [
            -0.438465,
            37.592727
          ],
          [
            -0.30857,
            45.317495
          ],
          [
            -0.160395,
            48.797701
          ],
          [
            0.056247,
            49.437372
          ],
          [
            0.2118,
            49.51033
          ],
          [
            0.520964,
            48.922386
          ],
          [
            0.574756,
            46.737763
          ],
          [
            0.516786,
            24.203131
          ],
          [
            0.259475,
            19.053285
          ],
          [
            -0.300945,
            -41.199898
          ],
          [
            -0.499863,
            -47.77001
          ],
          [
            -0.658097,
            -48.924666
          ],
          [
            -0.818168,
            -49.164866
          ],
          [
            -1.102431,
            -48.409681
          ],
          [
            -1.158348,
            -46.349742
          ],
          [
            -1.087589,
            -20.085534
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.01970473500000003,
    -0.006718095000000007,
    0.7948692500000001
  ],
  "construction_scale": 52.21228816724139,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
