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
  "operation": "extrude",
  "basis": [
    [
      -0.2377244802372993,
      0.6625233290650216,
      0.7103167673232182
    ],
    [
      0.3266747390827528,
      -0.6341505582778758,
      0.7008114470248569
    ],
    [
      0.9147517074819381,
      0.39864258161975047,
      -0.06567652379975156
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -6.965111489043012,
      "length": 13.839668367936802,
      "loops": [
        [
          [
            -28.78976,
            23.722567
          ],
          [
            -20.156049,
            25.274699
          ],
          [
            -9.158879,
            26.507379
          ],
          [
            -2.962964,
            26.812481
          ],
          [
            2.922991,
            26.766737
          ],
          [
            11.673421,
            26.293754
          ],
          [
            21.023138,
            25.153246
          ],
          [
            30.244534,
            23.27371
          ],
          [
            36.481471,
            21.629584
          ],
          [
            46.552494,
            18.087764
          ],
          [
            50.433961,
            16.517519
          ],
          [
            55.865485,
            13.753996
          ],
          [
            58.505268,
            11.824074
          ],
          [
            59.827911,
            10.393207
          ],
          [
            61.02162,
            8.730475
          ],
          [
            62.104573,
            6.715293
          ],
          [
            63.067346,
            4.204434
          ],
          [
            63.488663,
            1.824152
          ],
          [
            63.519717,
            -0.371785
          ],
          [
            62.864039,
            -4.07332
          ],
          [
            61.990541,
            -6.581502
          ],
          [
            60.853675,
            -8.822743
          ],
          [
            59.447915,
            -10.791442
          ],
          [
            57.5791,
            -12.683707
          ],
          [
            55.835935,
            -13.917527
          ],
          [
            53.586251,
            -15.030858
          ],
          [
            51.413098,
            -15.71948
          ],
          [
            48.817458,
            -16.136056
          ],
          [
            45.336654,
            -15.997157
          ],
          [
            42.458912,
            -15.404544
          ],
          [
            39.732032,
            -14.562839
          ],
          [
            30.319953,
            -11.059354
          ],
          [
            25.493955,
            -9.642012
          ],
          [
            20.287471,
            -8.41483
          ],
          [
            16.42808,
            -7.616763
          ],
          [
            12.331208,
            -7.039972
          ],
          [
            7.471192,
            -6.467507
          ],
          [
            3.874162,
            -6.270626
          ],
          [
            -5.328288,
            -6.280762
          ],
          [
            -12.161335,
            -6.929859
          ],
          [
            -17.764083,
            -7.853681
          ],
          [
            -22.692929,
            -8.981151
          ],
          [
            -29.740977,
            -10.990818
          ],
          [
            -41.409603,
            -15.267182
          ],
          [
            -45.03301,
            -16.031425
          ],
          [
            -48.299668,
            -16.113981
          ],
          [
            -51.555413,
            -15.622358
          ],
          [
            -54.644301,
            -14.506856
          ],
          [
            -56.879915,
            -13.092244
          ],
          [
            -58.800425,
            -11.348431
          ],
          [
            -60.781308,
            -8.730127
          ],
          [
            -62.333481,
            -5.663939
          ],
          [
            -63.058992,
            -2.927625
          ],
          [
            -63.219745,
            1.293384
          ],
          [
            -62.674535,
            4.42109
          ],
          [
            -61.833488,
            6.935588
          ],
          [
            -59.934577,
            10.101217
          ],
          [
            -58.757823,
            11.453647
          ],
          [
            -56.470147,
            13.376853
          ],
          [
            -54.949313,
            14.380537
          ],
          [
            -51.013551,
            16.346736
          ],
          [
            -45.371281,
            18.668425
          ],
          [
            -40.736586,
            20.3362
          ],
          [
            -33.972388,
            22.396275
          ]
        ],
        {
          "center": [
            -15.122565971784574,
            9.324024010510815
          ],
          "radius": 6.467737999564174
        },
        [
          [
            21.813764,
            11.03697
          ],
          [
            21.98547,
            9.966184
          ],
          [
            21.923733,
            8.577291
          ],
          [
            21.559141,
            7.250065
          ],
          [
            21.001432,
            6.118575
          ],
          [
            20.274015,
            5.159093
          ],
          [
            19.369647,
            4.378964
          ],
          [
            17.012749,
            3.374304
          ],
          [
            14.655344,
            3.203244
          ],
          [
            12.37187,
            3.941785
          ],
          [
            11.309198,
            4.706692
          ],
          [
            10.431853,
            5.665217
          ],
          [
            9.525896,
            7.531413
          ],
          [
            9.362639,
            8.583028
          ],
          [
            9.486824,
            10.153922
          ],
          [
            10.607576,
            13.259878
          ],
          [
            11.275592,
            14.279564
          ],
          [
            12.165059,
            15.074799
          ],
          [
            13.87624,
            15.826648
          ],
          [
            16.299977,
            15.958571
          ],
          [
            18.610457,
            15.147306
          ],
          [
            19.696029,
            14.406321
          ],
          [
            20.610255,
            13.48633
          ],
          [
            21.29728,
            12.415372
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    0.5408597900000001,
    -0.28382348,
    -0.32700478499999996
  ],
  "construction_scale": 120.55940673873314,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
