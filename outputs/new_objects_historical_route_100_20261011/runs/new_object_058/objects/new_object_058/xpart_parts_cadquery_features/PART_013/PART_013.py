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
      "start": -41.584137566582996,
      "length": 5.042164888724846,
      "loops": [
        [
          [
            1.162769,
            49.893954
          ],
          [
            -3.851421,
            49.877971
          ],
          [
            -4.101396,
            49.690234
          ],
          [
            -4.248519,
            49.133101
          ],
          [
            -4.241467,
            -40.57958
          ],
          [
            -4.141464,
            -43.365234
          ],
          [
            -3.735401,
            -46.136339
          ],
          [
            -3.648333,
            -49.479126
          ],
          [
            -3.294283,
            -49.862411
          ],
          [
            -2.737154,
            -49.977982
          ],
          [
            0.605631,
            -49.995785
          ],
          [
            1.162769,
            -49.81301
          ],
          [
            1.368056,
            -49.479126
          ],
          [
            1.405606,
            -48.921992
          ],
          [
            1.319765,
            26.833299
          ],
          [
            1.347091,
            40.776136
          ],
          [
            1.543131,
            49.133101
          ],
          [
            1.394777,
            49.690234
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -36.54363604336081,
      "length": 73.08893545222428,
      "loops": [
        [
          [
            -2.55273,
            42.447529
          ],
          [
            -2.520532,
            -41.679287
          ],
          [
            -3.034146,
            -43.047187
          ],
          [
            -3.027037,
            -48.921992
          ],
          [
            -2.969944,
            -49.479126
          ],
          [
            -2.737154,
            -49.770347
          ],
          [
            -2.180027,
            -49.948377
          ],
          [
            0.605631,
            -49.9778
          ],
          [
            1.162769,
            -49.738969
          ],
          [
            1.324599,
            -49.479126
          ],
          [
            1.412926,
            -43.350681
          ],
          [
            1.010544,
            -41.679287
          ],
          [
            1.064815,
            41.333265
          ],
          [
            1.125429,
            43.004658
          ],
          [
            1.412702,
            44.118923
          ],
          [
            1.341221,
            49.133101
          ],
          [
            1.198552,
            49.690234
          ],
          [
            0.605631,
            49.963565
          ],
          [
            -3.851421,
            49.894102
          ],
          [
            -4.096071,
            49.690234
          ],
          [
            -4.292786,
            49.133101
          ],
          [
            -4.203839,
            43.561789
          ],
          [
            -3.851421,
            43.203089
          ],
          [
            -2.737154,
            42.914859
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 36.543636043360806,
      "length": 5.042164888724853,
      "loops": [
        [
          [
            2.121631,
            33.688822
          ],
          [
            2.045125,
            -9.365678
          ],
          [
            1.757655,
            -20.508301
          ],
          [
            1.607609,
            -43.350681
          ],
          [
            1.300544,
            -48.921992
          ],
          [
            1.162769,
            -49.603437
          ],
          [
            0.605631,
            -49.955754
          ],
          [
            -2.180027,
            -49.953682
          ],
          [
            -2.863926,
            -49.479126
          ],
          [
            -3.019129,
            -43.350681
          ],
          [
            -2.875659,
            42.447529
          ],
          [
            -3.12644,
            43.004658
          ],
          [
            -3.851421,
            43.236791
          ],
          [
            -4.201649,
            43.561789
          ],
          [
            -4.324918,
            44.118923
          ],
          [
            -4.311341,
            49.133101
          ],
          [
            -4.102815,
            49.690234
          ],
          [
            -3.851421,
            49.891703
          ],
          [
            -3.294283,
            49.984597
          ],
          [
            1.162769,
            49.842804
          ],
          [
            1.487156,
            49.690234
          ],
          [
            1.869251,
            49.133101
          ],
          [
            1.972856,
            48.575972
          ],
          [
            2.23345,
            45.155162
          ],
          [
            2.524704,
            44.118923
          ],
          [
            2.463636,
            43.561789
          ],
          [
            1.868462,
            43.004658
          ],
          [
            1.688516,
            42.447529
          ],
          [
            2.005982,
            38.261522
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.47365216499999996,
    -0.00046717500000000023,
    -0.01146156999999999
  ],
  "construction_scale": 225.94153622666386,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
