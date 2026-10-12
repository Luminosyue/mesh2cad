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
      "start": -5.201661300580826,
      "length": 0.630712466522426,
      "loops": [
        [
          [
            -9.167182,
            49.275008
          ],
          [
            27.955099,
            49.195325
          ],
          [
            28.177786,
            49.034876
          ],
          [
            28.287776,
            48.52635
          ],
          [
            28.314778,
            46.492257
          ],
          [
            27.955099,
            45.890001
          ],
          [
            26.455608,
            45.741848
          ],
          [
            8.63117,
            45.634516
          ],
          [
            -26.965532,
            45.817815
          ],
          [
            -27.982583,
            45.931465
          ],
          [
            -28.07348,
            46.492257
          ],
          [
            -28.055853,
            49.034876
          ],
          [
            -27.474058,
            49.142441
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.571156900510423,
      "length": 0.6307124665224269,
      "loops": [
        [
          [
            27.745038,
            26.763017
          ],
          [
            28.018607,
            -9.202422
          ],
          [
            27.791456,
            -24.192629
          ],
          [
            27.795569,
            -40.305883
          ],
          [
            27.491338,
            -41.482456
          ],
          [
            27.287138,
            -43.357124
          ],
          [
            26.938046,
            -48.960411
          ],
          [
            26.530067,
            -49.618849
          ],
          [
            23.886902,
            -49.765646
          ],
          [
            22.860911,
            -49.618849
          ],
          [
            22.681949,
            -49.110323
          ],
          [
            22.514564,
            -41.407036
          ],
          [
            22.361329,
            -41.090863
          ],
          [
            21.852801,
            -40.8998
          ],
          [
            18.801655,
            -40.850688
          ],
          [
            -15.377905,
            -40.865503
          ],
          [
            -16.514599,
            -41.202009
          ],
          [
            -18.320619,
            -41.223657
          ],
          [
            -22.703896,
            -41.675901
          ],
          [
            -23.463148,
            -41.933697
          ],
          [
            -23.631026,
            -42.274343
          ],
          [
            -24.00416,
            -45.042129
          ],
          [
            -24.246663,
            -49.110323
          ],
          [
            -24.931439,
            -49.287958
          ],
          [
            -27.789009,
            -49.323431
          ],
          [
            -28.240226,
            -49.110323
          ],
          [
            -28.24418,
            -41.200945
          ],
          [
            -28.56599,
            -39.956886
          ],
          [
            -28.604391,
            -36.90574
          ],
          [
            -28.581,
            44.458157
          ],
          [
            -28.722677,
            45.98373
          ],
          [
            -28.678843,
            49.034876
          ],
          [
            -28.491109,
            49.679487
          ],
          [
            -27.982583,
            49.928024
          ],
          [
            -21.371769,
            49.936806
          ],
          [
            27.446568,
            49.954893
          ],
          [
            28.463619,
            49.745851
          ],
          [
            28.711783,
            49.034876
          ],
          [
            28.749755,
            46.492257
          ],
          [
            28.333425,
            44.96668
          ],
          [
            28.505122,
            40.389963
          ],
          [
            28.467029,
            34.28767
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.9406525004400192,
      "length": 2.837477866768837,
      "loops": [
        [
          [
            -28.599719,
            -49.110323
          ],
          [
            -28.660815,
            48.429785
          ],
          [
            -28.491109,
            49.663865
          ],
          [
            -27.982583,
            49.932129
          ],
          [
            -25.028004,
            49.977294
          ],
          [
            23.378372,
            49.997646
          ],
          [
            27.446568,
            49.964521
          ],
          [
            27.955099,
            49.923835
          ],
          [
            28.463619,
            49.633062
          ],
          [
            28.602444,
            49.034876
          ],
          [
            28.632209,
            47.000777
          ],
          [
            28.427987,
            44.96668
          ],
          [
            28.437536,
            33.682581
          ],
          [
            28.197826,
            24.117184
          ],
          [
            28.072707,
            -39.956886
          ],
          [
            27.80501,
            -45.138694
          ],
          [
            27.243851,
            -49.110323
          ],
          [
            26.929956,
            -49.618849
          ],
          [
            26.429526,
            -49.909916
          ],
          [
            24.80738,
            -49.943203
          ],
          [
            23.790336,
            -49.85255
          ],
          [
            22.869852,
            -49.471316
          ],
          [
            22.69457,
            -48.601798
          ],
          [
            22.456603,
            -41.579022
          ],
          [
            22.264763,
            -41.210625
          ],
          [
            21.852801,
            -40.999606
          ],
          [
            -15.056271,
            -40.950243
          ],
          [
            -15.778,
            -41.211277
          ],
          [
            -17.303573,
            -42.683742
          ],
          [
            -20.513829,
            -46.153319
          ],
          [
            -22.455772,
            -48.601798
          ],
          [
            -23.405862,
            -49.475552
          ],
          [
            -24.422913,
            -49.77742
          ],
          [
            -27.982583,
            -49.771545
          ],
          [
            -28.320957,
            -49.618849
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.1033827001232055,
      "length": 3.7832344668744415,
      "loops": [
        [
          [
            27.225805,
            48.531162
          ],
          [
            27.198434,
            -48.601798
          ],
          [
            27.154606,
            -49.110323
          ],
          [
            26.757208,
            -49.618849
          ],
          [
            25.920995,
            -49.899642
          ],
          [
            24.903945,
            -49.912822
          ],
          [
            23.810442,
            -49.618849
          ],
          [
            23.459418,
            -49.110323
          ],
          [
            23.426959,
            -48.601798
          ],
          [
            23.507334,
            48.52635
          ],
          [
            23.572805,
            49.034876
          ],
          [
            23.886902,
            49.483023
          ],
          [
            24.395424,
            49.676352
          ],
          [
            26.604322,
            49.5434
          ],
          [
            27.154818,
            49.034876
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.1033827001232055,
      "length": 3.7832344668744415,
      "loops": [
        [
          [
            -28.590805,
            -39.448359
          ],
          [
            -28.556165,
            -49.110323
          ],
          [
            -28.164984,
            -49.618849
          ],
          [
            -24.422913,
            -49.720439
          ],
          [
            -23.405862,
            -49.491648
          ],
          [
            -15.793978,
            -40.973932
          ],
          [
            -15.193171,
            -39.956886
          ],
          [
            -15.120779,
            -39.448359
          ],
          [
            -15.269476,
            -39.166913
          ],
          [
            -15.778,
            -38.852971
          ],
          [
            -16.795046,
            -38.786257
          ],
          [
            -28.199749,
            -38.939835
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.679643700299213,
      "length": 2.522225666733636,
      "loops": [
        [
          [
            23.80997,
            -47.584752
          ],
          [
            23.744415,
            49.034876
          ],
          [
            24.395424,
            49.553719
          ],
          [
            26.938046,
            49.506866
          ],
          [
            27.476413,
            49.034876
          ],
          [
            27.14695,
            44.249091
          ],
          [
            27.320814,
            -2.026625
          ],
          [
            27.196802,
            -39.664638
          ],
          [
            26.868873,
            -48.601798
          ],
          [
            26.67384,
            -49.110323
          ],
          [
            26.429526,
            -49.303488
          ],
          [
            25.920995,
            -49.517016
          ],
          [
            24.931961,
            -49.604227
          ],
          [
            24.395424,
            -49.469658
          ],
          [
            23.979941,
            -49.110323
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.35514477,
    -0.0010499899999999868,
    -0.19502226
  ],
  "construction_scale": 206.2292791131811,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
