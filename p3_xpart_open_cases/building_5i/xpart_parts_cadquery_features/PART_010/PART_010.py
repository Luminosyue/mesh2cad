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
      "start": -4.864031696205441,
      "length": 0.5897741608079019,
      "loops": [
        [
          [
            13.090342,
            -49.035753
          ],
          [
            13.098351,
            47.949916
          ],
          [
            13.039058,
            49.671164
          ],
          [
            12.669703,
            49.789867
          ],
          [
            12.418403,
            49.671164
          ],
          [
            12.384133,
            49.40511
          ],
          [
            12.304927,
            44.714812
          ],
          [
            12.270616,
            -48.769694
          ],
          [
            12.331064,
            -49.567863
          ],
          [
            12.669703,
            -49.785299
          ],
          [
            13.052493,
            -49.567863
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.274452096665387,
      "length": 1.4741435601179806,
      "loops": [
        [
          [
            14.00738,
            -4.940076
          ],
          [
            13.96491,
            -49.301808
          ],
          [
            13.821963,
            -49.833922
          ],
          [
            13.467872,
            -49.97196
          ],
          [
            13.119735,
            -49.833922
          ],
          [
            12.979071,
            -49.360512
          ],
          [
            12.93576,
            -4.858426
          ],
          [
            12.440496,
            -4.870394
          ],
          [
            12.395383,
            -5.136449
          ],
          [
            12.513654,
            -49.567863
          ],
          [
            12.257383,
            -49.909292
          ],
          [
            11.871534,
            -49.978701
          ],
          [
            11.575533,
            -49.833922
          ],
          [
            11.441203,
            -49.035753
          ],
          [
            11.33942,
            -4.764189
          ],
          [
            10.934888,
            -4.641041
          ],
          [
            7.348576,
            -4.607336
          ],
          [
            -21.119457,
            -4.615363
          ],
          [
            -21.917626,
            -4.392759
          ],
          [
            -22.183518,
            -3.806168
          ],
          [
            -21.797834,
            -3.328788
          ],
          [
            -21.119457,
            -3.194433
          ],
          [
            7.348576,
            -3.206854
          ],
          [
            11.33942,
            -3.080627
          ],
          [
            11.449834,
            49.40511
          ],
          [
            11.605477,
            49.872712
          ],
          [
            12.137591,
            49.982059
          ],
          [
            13.733929,
            49.953728
          ],
          [
            13.983093,
            49.40511
          ],
          [
            13.999986,
            -2.774183
          ],
          [
            14.069828,
            -3.007999
          ],
          [
            14.412304,
            -3.126154
          ],
          [
            21.449564,
            -3.175531
          ],
          [
            21.981675,
            -3.432451
          ],
          [
            22.162395,
            -3.806168
          ],
          [
            21.98196,
            -4.33828
          ],
          [
            21.449564,
            -4.607187
          ],
          [
            14.412304,
            -4.691147
          ]
        ],
        [
          [
            12.35592,
            -2.475885
          ],
          [
            12.393229,
            47.542713
          ],
          [
            12.669703,
            48.851781
          ],
          [
            12.93576,
            48.529573
          ],
          [
            12.971051,
            48.074827
          ],
          [
            13.016718,
            41.597491
          ],
          [
            13.059613,
            -2.475885
          ],
          [
            13.05816,
            -2.741942
          ],
          [
            12.815967,
            -2.883997
          ],
          [
            12.403646,
            -2.790162
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.8005030978152545,
      "length": 0.5897741608079019,
      "loops": [
        [
          [
            13.833809,
            -5.402505
          ],
          [
            13.819518,
            -49.567863
          ],
          [
            13.467872,
            -49.949433
          ],
          [
            12.132731,
            -49.978533
          ],
          [
            11.762145,
            -49.833922
          ],
          [
            11.594589,
            -49.035753
          ],
          [
            11.607555,
            -4.870394
          ],
          [
            11.235454,
            -3.806168
          ],
          [
            11.466861,
            -3.535252
          ],
          [
            11.578382,
            -3.007999
          ],
          [
            11.619616,
            49.40511
          ],
          [
            11.871534,
            49.933745
          ],
          [
            12.664843,
            49.996705
          ],
          [
            13.733929,
            49.844205
          ],
          [
            13.842799,
            48.872996
          ],
          [
            13.81853,
            -3.007999
          ],
          [
            14.078493,
            -3.806168
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.8005030978152545,
      "length": 0.5897741608079019,
      "loops": [
        [
          [
            7.967574,
            -3.806168
          ],
          [
            8.146745,
            -3.882767
          ],
          [
            8.449422,
            -3.806168
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.210923498275201,
      "length": 0.589774160807901,
      "loops": [
        [
          [
            12.54186,
            -49.301808
          ],
          [
            12.52259,
            -5.521449
          ],
          [
            12.497326,
            -5.136449
          ],
          [
            12.022229,
            -4.551729
          ],
          [
            11.826605,
            -4.019616
          ],
          [
            11.928835,
            -3.540111
          ],
          [
            12.413146,
            -2.741942
          ],
          [
            12.403785,
            37.964544
          ],
          [
            12.519938,
            48.756703
          ],
          [
            12.669703,
            49.661921
          ],
          [
            12.940674,
            49.427356
          ],
          [
            13.003563,
            48.340882
          ],
          [
            13.022131,
            -2.741942
          ],
          [
            13.686824,
            -3.806168
          ],
          [
            13.595211,
            -4.33828
          ],
          [
            13.10413,
            -4.870394
          ],
          [
            12.961924,
            -5.358281
          ],
          [
            12.84331,
            -36.797158
          ],
          [
            12.953341,
            -49.035753
          ],
          [
            12.889191,
            -49.521294
          ],
          [
            12.669703,
            -49.646986
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.621343898735148,
      "length": 6.485570156208433,
      "loops": [
        [
          [
            11.911719,
            -4.251928
          ],
          [
            12.403646,
            -4.685699
          ],
          [
            12.93576,
            -4.712337
          ],
          [
            13.535521,
            -4.33828
          ],
          [
            13.6943,
            -3.806168
          ],
          [
            13.201814,
            -3.156076
          ],
          [
            12.403646,
            -3.109034
          ],
          [
            11.904284,
            -3.540111
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.223796035,
    -0.07246617499999997,
    -0.44407593
  ],
  "construction_scale": 53.94885757278792,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
