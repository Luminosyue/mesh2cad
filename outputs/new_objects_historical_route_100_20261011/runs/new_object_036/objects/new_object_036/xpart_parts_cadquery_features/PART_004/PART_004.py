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
      "start": -49.386088994007906,
      "length": 20.95364956222978,
      "loops": [
        [
          [
            47.923199,
            -5.271876
          ],
          [
            24.18113,
            -5.436254
          ],
          [
            -10.168965,
            -5.338177
          ],
          [
            -48.858018,
            -4.420305
          ],
          [
            -49.581179,
            -4.152301
          ],
          [
            -49.926922,
            -3.481516
          ],
          [
            -49.841811,
            4.111665
          ],
          [
            -49.581179,
            4.864684
          ],
          [
            -49.219602,
            5.122622
          ],
          [
            -48.496439,
            5.210491
          ],
          [
            -37.409669,
            5.00791
          ],
          [
            -29.816489,
            5.046709
          ],
          [
            -14.991711,
            4.502323
          ],
          [
            -10.291172,
            4.915801
          ],
          [
            0.316853,
            4.947171
          ],
          [
            9.356353,
            5.402281
          ],
          [
            15.381004,
            5.12858
          ],
          [
            19.84217,
            5.16338
          ],
          [
            33.460003,
            4.358802
          ],
          [
            42.86108,
            4.332652
          ],
          [
            48.768568,
            4.522686
          ],
          [
            49.665147,
            4.111665
          ],
          [
            49.910299,
            3.388504
          ],
          [
            49.891741,
            -4.204678
          ],
          [
            49.835828,
            -4.566255
          ],
          [
            49.491729,
            -4.988542
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.434414875337886,
      "length": 8.981264351561201,
      "loops": [
        [
          [
            34.424323,
            4.560463
          ],
          [
            27.192724,
            4.914356
          ],
          [
            15.503211,
            4.569347
          ],
          [
            5.740553,
            4.754232
          ],
          [
            -4.022105,
            4.45087
          ],
          [
            -29.575328,
            4.306506
          ],
          [
            -37.530088,
            4.449366
          ],
          [
            -42.592206,
            4.811675
          ],
          [
            -48.496439,
            4.842622
          ],
          [
            -49.367413,
            4.473244
          ],
          [
            -49.663322,
            3.750081
          ],
          [
            -49.743575,
            -3.843094
          ],
          [
            -49.400569,
            -4.566255
          ],
          [
            -48.496439,
            -4.800069
          ],
          [
            -14.027391,
            -5.355327
          ],
          [
            4.051606,
            -5.468123
          ],
          [
            41.294341,
            -5.383226
          ],
          [
            48.768568,
            -5.269733
          ],
          [
            49.633047,
            -4.927834
          ],
          [
            49.876758,
            -4.204678
          ],
          [
            49.896601,
            3.388504
          ],
          [
            49.853306,
            3.773897
          ],
          [
            49.491729,
            4.216364
          ],
          [
            48.768568,
            4.481554
          ],
          [
            47.079619,
            4.568198
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.455125967336446,
      "length": 20.953649562229785,
      "loops": [
        [
          [
            44.068026,
            -5.423005
          ],
          [
            -27.163222,
            -5.385146
          ],
          [
            -48.858018,
            -4.972994
          ],
          [
            -49.581179,
            -4.696506
          ],
          [
            -49.846964,
            -4.204678
          ],
          [
            -49.814631,
            3.388504
          ],
          [
            -49.622469,
            4.111665
          ],
          [
            -49.226052,
            4.473244
          ],
          [
            -48.134862,
            4.632046
          ],
          [
            -43.958033,
            4.358906
          ],
          [
            -36.20272,
            4.463646
          ],
          [
            -32.025896,
            4.236131
          ],
          [
            -13.423184,
            3.986419
          ],
          [
            12.972152,
            4.162268
          ],
          [
            22.011651,
            4.06
          ],
          [
            30.165856,
            4.21924
          ],
          [
            41.374835,
            4.053322
          ],
          [
            48.768568,
            4.381446
          ],
          [
            49.491729,
            4.144515
          ],
          [
            49.759554,
            3.750081
          ],
          [
            49.813335,
            -4.204678
          ],
          [
            49.617094,
            -4.927834
          ],
          [
            49.130145,
            -5.257042
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.4965481513335774,
      "length": 11.974360654228345,
      "loops": [
        [
          [
            -36.564301,
            4.648955
          ],
          [
            -15.553885,
            3.992249
          ],
          [
            -4.706485,
            3.989773
          ],
          [
            6.140912,
            4.0152
          ],
          [
            14.818831,
            4.253723
          ],
          [
            26.350609,
            4.234754
          ],
          [
            32.497468,
            4.439843
          ],
          [
            43.022067,
            4.292525
          ],
          [
            48.768568,
            4.42676
          ],
          [
            49.491729,
            4.123218
          ],
          [
            49.796116,
            3.388504
          ],
          [
            49.757952,
            -4.204678
          ],
          [
            49.491729,
            -5.009868
          ],
          [
            48.768568,
            -5.298061
          ],
          [
            40.852589,
            -5.416541
          ],
          [
            -27.486022,
            -5.38172
          ],
          [
            -48.496439,
            -5.047193
          ],
          [
            -49.361186,
            -4.927834
          ],
          [
            -49.809434,
            -4.566255
          ],
          [
            -49.833857,
            3.388504
          ],
          [
            -49.586549,
            4.111665
          ],
          [
            -49.150554,
            4.473244
          ],
          [
            -48.496439,
            4.623655
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.468933362002161,
      "length": 35.9191310755655,
      "loops": [
        [
          [
            3.932653,
            -5.413558
          ],
          [
            -48.496439,
            -5.333942
          ],
          [
            -49.219602,
            -5.195671
          ],
          [
            -49.472607,
            -4.927834
          ],
          [
            -49.732578,
            -3.843094
          ],
          [
            -49.872353,
            -1.673616
          ],
          [
            -49.910709,
            2.665343
          ],
          [
            -49.728373,
            3.388504
          ],
          [
            -49.469099,
            3.750081
          ],
          [
            -48.496439,
            4.165683
          ],
          [
            -46.326961,
            4.051033
          ],
          [
            -38.614505,
            4.216924
          ],
          [
            -11.615285,
            3.892228
          ],
          [
            6.582988,
            3.966068
          ],
          [
            20.926911,
            4.241254
          ],
          [
            27.435349,
            4.209741
          ],
          [
            32.616744,
            4.403013
          ],
          [
            40.813808,
            4.373342
          ],
          [
            48.406989,
            4.71504
          ],
          [
            49.33259,
            4.473244
          ],
          [
            49.761462,
            3.750081
          ],
          [
            49.698855,
            -4.204678
          ],
          [
            49.491729,
            -4.746679
          ],
          [
            48.768568,
            -5.078879
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.004626624999999995,
    -0.462024155,
    0.0038259650000000145
  ],
  "construction_scale": 146.6367791583386,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
