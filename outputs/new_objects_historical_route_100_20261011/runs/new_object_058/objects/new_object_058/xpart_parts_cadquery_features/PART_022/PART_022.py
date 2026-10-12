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
      "length": 36.36563636363636,
      "loops": [
        [
          [
            -6.433811,
            1.788605
          ],
          [
            6.786786,
            1.746438
          ],
          [
            8.589594,
            1.994335
          ],
          [
            10.392403,
            1.898762
          ],
          [
            10.993341,
            1.383516
          ],
          [
            11.213023,
            0.416539
          ],
          [
            11.161329,
            -5.592822
          ],
          [
            10.935983,
            -6.193761
          ],
          [
            10.392403,
            -6.657094
          ],
          [
            9.791464,
            -6.773195
          ],
          [
            6.786786,
            -6.748546
          ],
          [
            6.164373,
            -6.193761
          ],
          [
            5.97748,
            -5.592822
          ],
          [
            5.948038,
            -2.588144
          ],
          [
            5.584911,
            -2.105223
          ],
          [
            -5.832873,
            -2.074439
          ],
          [
            -6.398125,
            -2.588144
          ],
          [
            -6.598534,
            -3.189077
          ],
          [
            -7.034748,
            -3.53682
          ],
          [
            -7.635684,
            -3.699334
          ],
          [
            -10.039428,
            -3.711935
          ],
          [
            -10.640364,
            -3.501578
          ],
          [
            -10.960396,
            -3.189077
          ],
          [
            -11.199252,
            -2.588144
          ],
          [
            -11.185827,
            1.017475
          ],
          [
            -11.047152,
            1.618409
          ],
          [
            -10.640364,
            2.107566
          ],
          [
            -10.039428,
            2.307804
          ],
          [
            -7.635684,
            2.290117
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.63636363636364,
      "length": 27.274727272727272,
      "loops": [
        [
          [
            5.939793,
            -2.588144
          ],
          [
            5.97527,
            -5.592822
          ],
          [
            6.156008,
            -6.193761
          ],
          [
            6.786786,
            -6.746163
          ],
          [
            9.791464,
            -6.765375
          ],
          [
            10.392403,
            -6.656239
          ],
          [
            10.939633,
            -6.193761
          ],
          [
            11.161883,
            -5.592822
          ],
          [
            11.211712,
            0.416539
          ],
          [
            11.161642,
            1.017475
          ],
          [
            10.809292,
            1.618409
          ],
          [
            10.392403,
            1.907375
          ],
          [
            8.589594,
            2.00233
          ],
          [
            6.18585,
            1.718681
          ],
          [
            0.777422,
            1.923696
          ],
          [
            -1.025386,
            1.754314
          ],
          [
            -5.832873,
            1.756435
          ],
          [
            -6.433811,
            1.784745
          ],
          [
            -7.635684,
            2.307422
          ],
          [
            -9.107603,
            2.334711
          ],
          [
            -10.376324,
            2.219345
          ],
          [
            -11.066042,
            1.618409
          ],
          [
            -11.197217,
            1.017475
          ],
          [
            -11.208693,
            -2.588144
          ],
          [
            -10.968638,
            -3.189077
          ],
          [
            -10.640364,
            -3.496264
          ],
          [
            -10.039428,
            -3.709536
          ],
          [
            -7.635684,
            -3.69239
          ],
          [
            -7.034748,
            -3.53064
          ],
          [
            -6.602973,
            -3.189077
          ],
          [
            -6.385587,
            -2.588144
          ],
          [
            -5.832873,
            -2.072791
          ],
          [
            4.983975,
            -2.035918
          ],
          [
            5.584911,
            -2.110286
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.63636363636364,
      "length": 27.274727272727272,
      "loops": [
        [
          [
            2.199125,
            4.623092
          ],
          [
            2.312339,
            5.224028
          ],
          [
            2.187081,
            5.824962
          ],
          [
            1.378358,
            6.664069
          ],
          [
            0.777422,
            6.768877
          ],
          [
            0.176489,
            6.63986
          ],
          [
            -0.604596,
            5.824962
          ],
          [
            -0.73811,
            5.224028
          ],
          [
            -0.621139,
            4.623092
          ],
          [
            0.176489,
            3.79796
          ],
          [
            0.777422,
            3.633929
          ],
          [
            1.378358,
            3.765637
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.636363636363633,
      "length": 36.36563636363637,
      "loops": [
        [
          [
            5.584911,
            -2.128557
          ],
          [
            -5.832873,
            -2.104728
          ],
          [
            -6.382159,
            -2.588144
          ],
          [
            -6.557042,
            -3.189077
          ],
          [
            -7.034748,
            -3.581758
          ],
          [
            -7.635684,
            -3.717086
          ],
          [
            -10.039428,
            -3.704995
          ],
          [
            -10.640364,
            -3.497272
          ],
          [
            -10.957185,
            -3.189077
          ],
          [
            -11.193799,
            -2.588144
          ],
          [
            -11.166421,
            1.017475
          ],
          [
            -11.019163,
            1.618409
          ],
          [
            -10.640364,
            2.07561
          ],
          [
            -9.438492,
            2.311186
          ],
          [
            -7.635684,
            2.285355
          ],
          [
            -6.433811,
            1.785383
          ],
          [
            -5.832873,
            1.741325
          ],
          [
            6.65648,
            1.737924
          ],
          [
            8.589594,
            1.991936
          ],
          [
            10.392403,
            1.903241
          ],
          [
            10.993341,
            1.405129
          ],
          [
            11.217581,
            0.416539
          ],
          [
            11.188679,
            -4.991891
          ],
          [
            10.933717,
            -6.193761
          ],
          [
            10.392403,
            -6.67011
          ],
          [
            9.791464,
            -6.772923
          ],
          [
            6.786786,
            -6.745503
          ],
          [
            6.155526,
            -6.193761
          ],
          [
            5.972528,
            -5.592822
          ],
          [
            5.946814,
            -2.588144
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0038893049999999957,
    0.186678165,
    0.19309062500000002
  ],
  "construction_scale": 243.70640990994096,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
