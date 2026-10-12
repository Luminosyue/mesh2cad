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
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -14.998345821064074,
      "length": 1.8185812454769732,
      "loops": [
        [
          [
            -17.281236,
            -0.299103
          ],
          [
            11.552656,
            -0.652853
          ],
          [
            15.840099,
            -0.488391
          ],
          [
            9.803148,
            -0.163799
          ],
          [
            -6.766122,
            0.177734
          ],
          [
            -21.826216,
            0.14889
          ],
          [
            -20.569068,
            -0.169753
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.180364509419944,
      "length": 12.726469115341754,
      "loops": [
        [
          [
            48.677203,
            0.548648
          ],
          [
            4.38627,
            1.736232
          ],
          [
            -36.718263,
            2.132997
          ],
          [
            -44.046979,
            2.079202
          ],
          [
            -48.826574,
            1.676842
          ],
          [
            -49.463855,
            1.372389
          ],
          [
            -49.87765,
            0.786166
          ],
          [
            -49.782492,
            0.377895
          ],
          [
            -49.145217,
            -0.12624
          ],
          [
            -26.975553,
            -0.030805
          ],
          [
            -1.484369,
            -0.415527
          ],
          [
            12.352265,
            -0.763097
          ],
          [
            39.755289,
            -1.836996
          ],
          [
            48.677203,
            -2.00991
          ],
          [
            49.314484,
            -1.999362
          ],
          [
            49.76714,
            -1.762953
          ],
          [
            49.853507,
            -1.44431
          ],
          [
            49.676264,
            -0.169753
          ],
          [
            49.314484,
            0.391171
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.4544953279110331,
      "length": 7.272525180409361,
      "loops": [
        [
          [
            -30.443524,
            -0.092095
          ],
          [
            -0.711966,
            -0.579881
          ],
          [
            45.490803,
            -1.933666
          ],
          [
            49.314484,
            -1.984996
          ],
          [
            49.633122,
            -1.919626
          ],
          [
            49.871031,
            -1.44431
          ],
          [
            49.633122,
            -0.115539
          ],
          [
            49.314484,
            0.227527
          ],
          [
            48.677203,
            0.359472
          ],
          [
            16.715166,
            0.991347
          ],
          [
            8.528588,
            1.359355
          ],
          [
            -44.68426,
            1.902057
          ],
          [
            -49.145217,
            1.679594
          ],
          [
            -49.568496,
            1.423446
          ],
          [
            -49.896233,
            0.786166
          ],
          [
            -49.59087,
            0.14889
          ],
          [
            -49.145217,
            -0.114151
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.817429918665486,
      "length": 6.3635345245872985,
      "loops": [
        [
          [
            48.241696,
            -0.190042
          ],
          [
            9.165867,
            0.540396
          ],
          [
            -45.640179,
            1.229932
          ],
          [
            -49.145217,
            1.130424
          ],
          [
            -49.782492,
            0.813107
          ],
          [
            -49.98037,
            0.467528
          ],
          [
            -49.782492,
            -0.163489
          ],
          [
            -49.463855,
            -0.308762
          ],
          [
            -45.958817,
            -0.541665
          ],
          [
            2.272657,
            -1.088746
          ],
          [
            29.240175,
            -1.607048
          ],
          [
            48.35856,
            -2.162853
          ],
          [
            49.314484,
            -2.051674
          ],
          [
            49.623101,
            -1.44431
          ],
          [
            49.251283,
            -0.488391
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.180364509419942,
      "length": 1.818581245476975,
      "loops": [
        [
          [
            20.636899,
            -1.407883
          ],
          [
            -42.524629,
            -0.548944
          ],
          [
            -46.348305,
            -0.650874
          ],
          [
            -49.145217,
            -0.257441
          ],
          [
            -49.352452,
            -0.169753
          ],
          [
            -49.482125,
            0.14889
          ],
          [
            -48.826574,
            0.496186
          ],
          [
            -47.304228,
            0.594331
          ],
          [
            -26.91128,
            0.205762
          ],
          [
            16.423733,
            -0.069698
          ],
          [
            43.260327,
            -0.680237
          ],
          [
            44.853522,
            -0.87307
          ],
          [
            45.686064,
            -1.125672
          ],
          [
            46.107053,
            -1.44431
          ],
          [
            45.616146,
            -1.762953
          ],
          [
            44.534884,
            -1.926198
          ],
          [
            41.416942,
            -2.089525
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.964297205,
    -0.004270299999999991,
    0.011019219999999996
  ],
  "construction_scale": 64.61131692543584,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
