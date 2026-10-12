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
      "start": -16.41969888627094,
      "length": 5.971456382963065,
      "loops": [
        [
          [
            2.882664,
            3.770405
          ],
          [
            -35.933715,
            3.568066
          ],
          [
            -39.132557,
            3.300466
          ],
          [
            -38.818694,
            3.10045
          ],
          [
            -38.709539,
            2.500402
          ],
          [
            -38.120648,
            1.707254
          ],
          [
            -36.932529,
            0.50024
          ],
          [
            -36.191964,
            0.300224
          ],
          [
            -34.733619,
            0.223431
          ],
          [
            23.484326,
            -0.00592
          ],
          [
            40.4857,
            0.235565
          ],
          [
            42.285845,
            0.303293
          ],
          [
            42.611765,
            0.50024
          ],
          [
            41.999239,
            0.900272
          ],
          [
            41.990778,
            1.100288
          ],
          [
            42.392378,
            2.300386
          ],
          [
            42.195844,
            2.900433
          ],
          [
            42.653854,
            3.300466
          ],
          [
            41.285764,
            3.517924
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -10.448899291263325,
      "length": 1.9909233196246556,
      "loops": [
        [
          [
            -6.31808,
            -0.12952
          ],
          [
            -3.317838,
            -0.332995
          ],
          [
            4.082761,
            -0.383821
          ],
          [
            8.683131,
            -0.223336
          ],
          [
            11.134804,
            0.102252
          ],
          [
            11.964731,
            0.50024
          ],
          [
            11.653525,
            1.100288
          ],
          [
            11.581217,
            1.900353
          ],
          [
            12.212409,
            3.300466
          ],
          [
            11.842514,
            3.500483
          ],
          [
            9.855141,
            3.73274
          ],
          [
            2.682647,
            3.944424
          ],
          [
            -16.518903,
            3.50847
          ],
          [
            -17.904894,
            3.300466
          ],
          [
            -16.11887,
            2.603516
          ],
          [
            -11.918532,
            2.598604
          ],
          [
            -10.346491,
            2.365008
          ],
          [
            -9.34641,
            1.716588
          ],
          [
            -9.218313,
            0.50024
          ],
          [
            -8.988016,
            0.300224
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -8.45863275959412,
      "length": 2.986056585459257,
      "loops": [
        [
          [
            48.68636,
            3.466422
          ],
          [
            1.082518,
            3.967273
          ],
          [
            -13.118629,
            3.506208
          ],
          [
            -32.120163,
            3.6878
          ],
          [
            -47.121375,
            3.547979
          ],
          [
            -48.721504,
            3.440723
          ],
          [
            -49.321552,
            3.202162
          ],
          [
            -49.799088,
            2.500402
          ],
          [
            -49.862376,
            1.500321
          ],
          [
            -49.782551,
            0.900272
          ],
          [
            -49.548614,
            0.50024
          ],
          [
            -48.721504,
            0.194342
          ],
          [
            -16.918935,
            -0.049051
          ],
          [
            -9.718354,
            -0.46325
          ],
          [
            -3.917886,
            -1.371252
          ],
          [
            -0.117579,
            -1.588941
          ],
          [
            3.482712,
            -1.452702
          ],
          [
            13.883552,
            -0.501601
          ],
          [
            23.846376,
            -0.090253
          ],
          [
            48.486345,
            0.166474
          ],
          [
            49.486426,
            0.405311
          ],
          [
            49.879055,
            1.100288
          ],
          [
            49.927224,
            2.10037
          ],
          [
            49.744619,
            2.900433
          ],
          [
            49.286411,
            3.295034
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.473232962090314,
      "length": 15.92278904130909,
      "loops": [
        [
          [
            15.883713,
            -1.228528
          ],
          [
            7.230193,
            -2.887858
          ],
          [
            4.082761,
            -3.24828
          ],
          [
            -1.917724,
            -3.246045
          ],
          [
            -7.118144,
            -2.64571
          ],
          [
            -15.186564,
            -1.099988
          ],
          [
            -23.9195,
            -0.215812
          ],
          [
            -32.320178,
            0.061702
          ],
          [
            -40.720856,
            0.191382
          ],
          [
            -43.921115,
            0.03383
          ],
          [
            -49.121537,
            0.230994
          ],
          [
            -49.521567,
            0.427597
          ],
          [
            -49.851728,
            0.900272
          ],
          [
            -49.939207,
            2.10037
          ],
          [
            -49.814446,
            2.700418
          ],
          [
            -49.321552,
            3.230539
          ],
          [
            -48.574311,
            3.459601
          ],
          [
            -47.574232,
            3.5255
          ],
          [
            -33.520274,
            3.724926
          ],
          [
            -21.519307,
            3.499297
          ],
          [
            -1.11766,
            4.005749
          ],
          [
            6.482954,
            4.056893
          ],
          [
            22.884278,
            3.968606
          ],
          [
            39.032761,
            3.546569
          ],
          [
            47.686282,
            3.572814
          ],
          [
            49.286411,
            3.301158
          ],
          [
            49.733081,
            2.900433
          ],
          [
            49.913682,
            2.300386
          ],
          [
            49.934155,
            1.447496
          ],
          [
            49.726221,
            0.674904
          ],
          [
            49.310657,
            0.300224
          ],
          [
            48.68636,
            0.187101
          ],
          [
            31.885004,
            0.038234
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.448899291263324,
      "length": 5.9714563829630665,
      "loops": [
        [
          [
            -15.065602,
            -0.073969
          ],
          [
            -48.468297,
            0.143283
          ],
          [
            -49.321552,
            0.295118
          ],
          [
            -49.721585,
            0.678612
          ],
          [
            -49.851764,
            2.300386
          ],
          [
            -49.684136,
            2.900433
          ],
          [
            -49.174725,
            3.277532
          ],
          [
            -47.321389,
            3.491917
          ],
          [
            16.936982,
            3.707627
          ],
          [
            29.738016,
            3.555324
          ],
          [
            48.339518,
            3.581517
          ],
          [
            49.086393,
            3.500814
          ],
          [
            49.486426,
            3.268784
          ],
          [
            49.810108,
            2.900433
          ],
          [
            49.94322,
            2.10037
          ],
          [
            49.908435,
            1.100288
          ],
          [
            49.686442,
            0.524374
          ],
          [
            49.286411,
            0.273701
          ],
          [
            48.486345,
            0.199549
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0010162950000000004,
    0.01602537,
    0.00157061
  ],
  "construction_scale": 81.115460224665,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
