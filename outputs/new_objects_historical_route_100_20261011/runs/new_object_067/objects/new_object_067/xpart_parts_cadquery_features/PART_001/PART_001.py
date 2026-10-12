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
      "length": 51.51715151515152,
      "loops": [
        [
          [
            -45.276145,
            -4.882482
          ],
          [
            -45.125852,
            -5.452957
          ],
          [
            -44.432294,
            -5.840059
          ],
          [
            -35.459052,
            -7.384434
          ],
          [
            -27.797706,
            -8.396606
          ],
          [
            -26.909862,
            -8.200554
          ],
          [
            -26.668076,
            -7.677219
          ],
          [
            -27.13248,
            -6.994077
          ],
          [
            -27.873901,
            -6.75406
          ],
          [
            -32.60903,
            -6.194378
          ],
          [
            -44.432294,
            -4.403018
          ],
          [
            -44.926576,
            -4.482793
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 51.51715151515152,
      "loops": [
        [
          [
            45.526735,
            -7.128673
          ],
          [
            31.02166,
            -6.838206
          ],
          [
            30.487833,
            -7.182939
          ],
          [
            30.360868,
            -7.848164
          ],
          [
            30.517481,
            -8.171499
          ],
          [
            30.945465,
            -8.434276
          ],
          [
            33.664006,
            -8.590637
          ],
          [
            45.108652,
            -8.484325
          ],
          [
            46.021017,
            -8.312974
          ],
          [
            46.325701,
            -7.924359
          ],
          [
            46.205088,
            -7.430079
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5151515151515156,
      "length": 27.274727272727265,
      "loops": [
        [
          [
            4.254324,
            -14.272796
          ],
          [
            7.467146,
            -15.044122
          ],
          [
            9.938549,
            -14.878865
          ],
          [
            12.889223,
            -13.887507
          ],
          [
            14.387072,
            -12.913864
          ],
          [
            15.192377,
            -11.878603
          ],
          [
            15.659598,
            -10.380753
          ],
          [
            17.847061,
            -8.125541
          ],
          [
            18.93842,
            -6.194378
          ],
          [
            19.270866,
            -5.205817
          ],
          [
            19.38675,
            -4.217257
          ],
          [
            19.310104,
            -3.213688
          ],
          [
            18.68297,
            -1.745854
          ],
          [
            18.888364,
            -1.498714
          ],
          [
            21.306997,
            -1.162227
          ],
          [
            31.454754,
            -1.093904
          ],
          [
            44.306042,
            -0.559254
          ],
          [
            45.032457,
            -0.336403
          ],
          [
            45.261439,
            0.231267
          ],
          [
            44.785315,
            0.660172
          ],
          [
            44.291033,
            0.72933
          ],
          [
            29.709763,
            0.24681
          ],
          [
            17.832027,
            0.444677
          ],
          [
            17.352196,
            0.725548
          ],
          [
            16.488105,
            1.714108
          ],
          [
            15.925533,
            4.18551
          ],
          [
            15.188276,
            5.915491
          ],
          [
            13.887978,
            8.139753
          ],
          [
            12.409951,
            9.852262
          ],
          [
            10.552818,
            11.352575
          ],
          [
            8.455707,
            12.462082
          ],
          [
            5.984305,
            13.304645
          ],
          [
            3.760043,
            13.631186
          ],
          [
            1.535782,
            13.538268
          ],
          [
            -1.4299,
            12.831561
          ],
          [
            -3.407023,
            11.997447
          ],
          [
            -5.384144,
            10.70022
          ],
          [
            -7.114125,
            8.970181
          ],
          [
            -8.334737,
            7.259703
          ],
          [
            -9.169183,
            5.668352
          ],
          [
            -10.564253,
            1.929129
          ],
          [
            -11.068369,
            1.506313
          ],
          [
            -14.019042,
            1.164568
          ],
          [
            -45.420854,
            0.924769
          ],
          [
            -45.915135,
            0.823884
          ],
          [
            -46.217753,
            0.478407
          ],
          [
            -45.915135,
            -0.127638
          ],
          [
            -44.664425,
            -0.315017
          ],
          [
            -20.444688,
            -0.229674
          ],
          [
            -11.315508,
            -0.358313
          ],
          [
            -11.037664,
            -0.510153
          ],
          [
            -10.774509,
            -1.004433
          ],
          [
            -10.393134,
            -3.970116
          ],
          [
            -9.405078,
            -6.67365
          ],
          [
            -7.871119,
            -9.145052
          ],
          [
            -6.372705,
            -10.735249
          ],
          [
            -4.133435,
            -12.300905
          ],
          [
            -1.909173,
            -13.315595
          ],
          [
            1.041501,
            -14.052946
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.787878787878782,
      "length": 21.214121212121217,
      "loops": [
        [
          [
            5.242884,
            1.73638
          ],
          [
            12.683441,
            1.313872
          ],
          [
            23.531258,
            1.313653
          ],
          [
            36.382549,
            1.681395
          ],
          [
            44.043894,
            2.06168
          ],
          [
            44.785315,
            1.897389
          ],
          [
            45.044716,
            1.466968
          ],
          [
            44.798585,
            0.972688
          ],
          [
            44.291033,
            0.806966
          ],
          [
            38.60681,
            0.471246
          ],
          [
            28.500415,
            0.096783
          ],
          [
            15.622773,
            -0.00855
          ],
          [
            8.702847,
            0.10367
          ],
          [
            -5.878424,
            0.814387
          ],
          [
            -44.900224,
            0.697772
          ],
          [
            -45.915135,
            0.82424
          ],
          [
            -46.162275,
            0.995686
          ],
          [
            -46.316792,
            1.466968
          ],
          [
            -45.915135,
            1.859205
          ],
          [
            -45.173715,
            1.929499
          ],
          [
            -10.574087,
            2.185609
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0005282100000000012,
    0.05933806,
    -7.659000000001526e-05
  ],
  "construction_scale": 100.22635922778878,
  "expected_solid_count": 3
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
