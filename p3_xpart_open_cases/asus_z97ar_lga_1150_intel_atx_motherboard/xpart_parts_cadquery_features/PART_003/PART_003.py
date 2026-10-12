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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            9.997853,
            39.634472
          ],
          [
            -8.549064,
            39.76466
          ],
          [
            -10.520429,
            39.519243
          ],
          [
            -10.940904,
            38.984249
          ],
          [
            -11.116912,
            37.445378
          ],
          [
            -11.076585,
            31.802852
          ],
          [
            -10.520429,
            18.976239
          ],
          [
            -10.013247,
            24.621454
          ],
          [
            -9.796154,
            38.471295
          ],
          [
            -9.494516,
            38.785154
          ],
          [
            8.971938,
            38.644765
          ],
          [
            10.105714,
            38.471295
          ],
          [
            10.486051,
            35.39355
          ],
          [
            10.214535,
            28.292615
          ],
          [
            10.51081,
            23.925847
          ],
          [
            11.049649,
            28.725109
          ],
          [
            11.15231,
            35.906508
          ],
          [
            10.926222,
            39.064711
          ],
          [
            10.629209,
            39.516252
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            10.265597,
            10.771612
          ],
          [
            10.51081,
            18.25346
          ],
          [
            11.023766,
            19.878063
          ],
          [
            11.24215,
            13.929818
          ],
          [
            11.023766,
            8.671197
          ],
          [
            10.51081,
            8.581253
          ],
          [
            10.384383,
            8.719785
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 18.18381818181818,
      "loops": [
        [
          [
            -10.961922,
            -9.233712
          ],
          [
            -11.240108,
            -40.011134
          ],
          [
            -11.033386,
            -40.740713
          ],
          [
            -10.520429,
            -41.024735
          ],
          [
            -10.007473,
            -40.829718
          ],
          [
            -9.760874,
            -40.524092
          ],
          [
            -9.667385,
            -38.985221
          ],
          [
            -9.499541,
            38.471295
          ],
          [
            -8.981559,
            38.779466
          ],
          [
            9.484896,
            38.76332
          ],
          [
            9.997853,
            38.805198
          ],
          [
            10.51081,
            39.154407
          ],
          [
            10.51081,
            39.665338
          ],
          [
            9.997853,
            39.968869
          ],
          [
            0.251669,
            40.197937
          ],
          [
            -10.007473,
            40.164402
          ],
          [
            -10.627072,
            40.010165
          ],
          [
            -11.039589,
            39.497207
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -25.757575757575758,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -9.718958,
            -40.524092
          ],
          [
            -9.67905,
            -10.772584
          ],
          [
            -9.483286,
            -4.104142
          ],
          [
            -9.430861,
            13.037347
          ],
          [
            -9.552242,
            38.471295
          ],
          [
            -8.981559,
            38.913209
          ],
          [
            9.484896,
            38.889737
          ],
          [
            10.51081,
            39.105306
          ],
          [
            10.722537,
            39.497207
          ],
          [
            10.51081,
            39.968883
          ],
          [
            9.997853,
            40.145142
          ],
          [
            -0.475195,
            40.351477
          ],
          [
            -10.007473,
            40.336543
          ],
          [
            -10.757028,
            40.010165
          ],
          [
            -11.031545,
            39.497207
          ],
          [
            -10.705172,
            3.590214
          ],
          [
            -11.177583,
            -40.524092
          ],
          [
            -10.520429,
            -41.012733
          ],
          [
            -10.007473,
            -40.865823
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.666666666666664,
      "length": 33.33533333333334,
      "loops": [
        [
          [
            -10.475922,
            13.849355
          ],
          [
            -11.036189,
            39.497207
          ],
          [
            -10.935261,
            40.010165
          ],
          [
            -10.520429,
            40.419999
          ],
          [
            -4.877902,
            40.524789
          ],
          [
            6.920111,
            40.373719
          ],
          [
            9.997853,
            40.225542
          ],
          [
            10.51081,
            39.925929
          ],
          [
            10.615325,
            39.497207
          ],
          [
            9.997853,
            39.039172
          ],
          [
            -8.981559,
            39.15764
          ],
          [
            -9.521527,
            38.984249
          ],
          [
            -9.375574,
            -7.110297
          ],
          [
            -9.603558,
            -14.87624
          ],
          [
            -9.664218,
            -39.939546
          ],
          [
            -9.739001,
            -40.524092
          ],
          [
            -10.007473,
            -40.945345
          ],
          [
            -10.520429,
            -41.099537
          ],
          [
            -11.033386,
            -40.820679
          ],
          [
            -11.218744,
            -40.011134
          ],
          [
            -10.554206,
            -8.136211
          ],
          [
            -10.462926,
            5.642042
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666667,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            -9.671559,
            -40.011134
          ],
          [
            -9.494516,
            39.670553
          ],
          [
            -8.981559,
            40.000073
          ],
          [
            -8.468601,
            40.017173
          ],
          [
            0.251669,
            40.161009
          ],
          [
            9.997853,
            40.032525
          ],
          [
            10.556662,
            40.523123
          ],
          [
            10.039991,
            41.036078
          ],
          [
            -7.173325,
            41.208672
          ],
          [
            -10.007473,
            41.092063
          ],
          [
            -10.520429,
            40.92193
          ],
          [
            -10.850045,
            40.523123
          ],
          [
            -10.981158,
            32.559404
          ],
          [
            -10.884744,
            12.823441
          ],
          [
            -10.997793,
            -10.016032
          ],
          [
            -11.330442,
            -35.394522
          ],
          [
            -11.194826,
            -40.524092
          ],
          [
            -10.520429,
            -41.023935
          ],
          [
            -10.007473,
            -40.87774
          ],
          [
            -9.736685,
            -40.524092
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.013047644999999997,
    -0.004839154999999998,
    0.009872615000000029
  ],
  "construction_scale": 52.00673472652823,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
