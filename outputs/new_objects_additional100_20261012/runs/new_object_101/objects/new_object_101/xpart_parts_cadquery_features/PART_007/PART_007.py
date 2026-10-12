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
      "start": -50.0,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            -33.950724,
            -12.975426
          ],
          [
            -34.917841,
            -12.566003
          ],
          [
            -35.187248,
            -12.16064
          ],
          [
            -35.320211,
            -11.552596
          ],
          [
            -35.332082,
            10.336987
          ],
          [
            -35.119219,
            11.203193
          ],
          [
            -34.308495,
            11.703672
          ],
          [
            -20.873824,
            12.017089
          ],
          [
            3.390232,
            12.083419
          ],
          [
            31.968297,
            11.811053
          ],
          [
            34.400473,
            11.660613
          ],
          [
            35.008519,
            11.427207
          ],
          [
            35.220392,
            11.147713
          ],
          [
            35.330272,
            10.336987
          ],
          [
            35.294151,
            -11.494893
          ],
          [
            35.126748,
            -12.36332
          ],
          [
            34.400473,
            -12.928865
          ],
          [
            29.593825,
            -13.145172
          ],
          [
            -28.836099,
            -13.150143
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            10.078716,
            12.675284
          ],
          [
            1.768781,
            12.927723
          ],
          [
            -10.636245,
            12.395428
          ],
          [
            -33.741914,
            12.144662
          ],
          [
            -34.805257,
            11.958438
          ],
          [
            -35.238839,
            11.350395
          ],
          [
            -35.343289,
            10.336987
          ],
          [
            -35.326303,
            -11.188698
          ],
          [
            -35.119219,
            -12.307564
          ],
          [
            -34.91129,
            -12.566003
          ],
          [
            -34.344897,
            -12.814892
          ],
          [
            -32.93119,
            -12.996217
          ],
          [
            -0.299497,
            -13.142461
          ],
          [
            31.157574,
            -13.113091
          ],
          [
            33.792429,
            -12.980316
          ],
          [
            34.603156,
            -12.802629
          ],
          [
            34.937798,
            -12.566003
          ],
          [
            35.20447,
            -12.153322
          ],
          [
            35.293649,
            -11.594061
          ],
          [
            35.20383,
            2.229734
          ],
          [
            35.008519,
            2.483911
          ],
          [
            34.603156,
            2.563407
          ],
          [
            28.79143,
            2.837779
          ],
          [
            27.232337,
            3.040459
          ],
          [
            26.901265,
            3.267585
          ],
          [
            25.782258,
            4.864592
          ],
          [
            25.434387,
            5.716783
          ],
          [
            25.285425,
            7.094087
          ],
          [
            25.38611,
            7.296767
          ],
          [
            26.090539,
            7.4999
          ],
          [
            32.129515,
            7.623376
          ],
          [
            35.008519,
            7.865715
          ],
          [
            35.196956,
            8.107492
          ],
          [
            35.259997,
            8.876753
          ],
          [
            35.26948,
            11.106247
          ],
          [
            35.118776,
            11.755757
          ],
          [
            34.359008,
            11.966195
          ],
          [
            20.576679,
            12.047856
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            32.455543,
            -12.813405
          ],
          [
            -32.889725,
            -12.849135
          ],
          [
            -34.916539,
            -12.520956
          ],
          [
            -35.227009,
            -12.16064
          ],
          [
            -35.330891,
            -11.147233
          ],
          [
            -35.392911,
            10.336987
          ],
          [
            -35.119219,
            11.583568
          ],
          [
            -34.511175,
            12.145412
          ],
          [
            -33.092404,
            12.322065
          ],
          [
            -26.524723,
            12.322968
          ],
          [
            -1.797601,
            13.055793
          ],
          [
            15.22763,
            12.665476
          ],
          [
            22.726839,
            12.775398
          ],
          [
            33.792429,
            12.169848
          ],
          [
            35.051964,
            11.958438
          ],
          [
            35.221679,
            11.755757
          ],
          [
            35.301382,
            11.147713
          ],
          [
            35.335437,
            -11.147233
          ],
          [
            35.246175,
            -11.957956
          ],
          [
            35.008519,
            -12.332535
          ],
          [
            34.197793,
            -12.689253
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.06590375500000001,
    -0.268777335,
    -0.005436109999999994
  ],
  "construction_scale": 82.1963063478695,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
