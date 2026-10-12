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
      "start": -15.098524758438552,
      "length": 1.830728154134405,
      "loops": [
        [
          [
            -0.20262,
            -31.322566
          ],
          [
            0.708285,
            -19.621157
          ],
          [
            0.819757,
            -16.418387
          ],
          [
            0.717308,
            6.186384
          ],
          [
            0.533918,
            1.866989
          ],
          [
            0.67239,
            1.204585
          ],
          [
            0.527725,
            0.082681
          ],
          [
            0.619569,
            -13.998385
          ],
          [
            0.4292,
            -15.3538
          ],
          [
            0.185013,
            -15.77011
          ],
          [
            -0.347279,
            -19.181836
          ],
          [
            -1.411864,
            -27.137906
          ],
          [
            -1.796829,
            -31.322566
          ],
          [
            -1.807312,
            -34.022005
          ],
          [
            -1.655557,
            -39.355932
          ],
          [
            -1.355129,
            -41.999086
          ],
          [
            0.66563,
            -48.355926
          ],
          [
            1.2496,
            -49.167044
          ],
          [
            1.78189,
            -49.037078
          ],
          [
            2.03859,
            -48.303331
          ],
          [
            1.78189,
            -46.422453
          ],
          [
            0.465209,
            -41.96842
          ],
          [
            0.158903,
            -39.706143
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -15.098524758438552,
      "length": 1.830728154134405,
      "loops": [
        [
          [
            0.185013,
            19.753701
          ],
          [
            -0.347279,
            23.824488
          ],
          [
            -0.879569,
            30.133793
          ],
          [
            -1.454948,
            41.069191
          ],
          [
            -1.508685,
            46.392114
          ],
          [
            -1.411864,
            46.927059
          ],
          [
            -0.879569,
            47.486594
          ],
          [
            -0.296443,
            46.924406
          ],
          [
            -0.094725,
            45.368803
          ],
          [
            0.335246,
            32.636831
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -15.098524758438552,
      "length": 1.830728154134405,
      "loops": [
        [
          [
            0.717308,
            7.727173
          ],
          [
            0.727578,
            7.534773
          ],
          [
            0.717308,
            7.077288
          ],
          [
            0.676834,
            7.534773
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.268400545294485,
      "length": 1.8307281541344032,
      "loops": [
        [
          [
            1.912574,
            -13.224628
          ],
          [
            0.194303,
            -31.322566
          ],
          [
            0.47328,
            -41.649783
          ],
          [
            2.100457,
            -48.888216
          ],
          [
            1.888377,
            -49.420512
          ],
          [
            1.2496,
            -49.816148
          ],
          [
            0.717308,
            -49.761035
          ],
          [
            0.327456,
            -49.420512
          ],
          [
            0.071768,
            -48.888216
          ],
          [
            -1.401664,
            -42.500711
          ],
          [
            -1.741685,
            -39.839247
          ],
          [
            -1.78128,
            -30.257988
          ],
          [
            -0.07049,
            -12.692341
          ],
          [
            -0.424205,
            5.724238
          ],
          [
            -0.309243,
            15.519157
          ],
          [
            -1.481449,
            45.859822
          ],
          [
            -1.301973,
            47.456698
          ],
          [
            -0.879569,
            47.824643
          ],
          [
            -0.347279,
            47.711726
          ],
          [
            -0.098245,
            47.456698
          ],
          [
            0.241624,
            45.859822
          ],
          [
            1.660208,
            15.519157
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -11.43827633215042,
      "length": 8.23616290013864,
      "loops": [
        [
          [
            1.117594,
            12.626112
          ],
          [
            0.064706,
            46.924406
          ],
          [
            -0.347279,
            47.696636
          ],
          [
            -0.879569,
            47.761272
          ],
          [
            -1.185041,
            47.456698
          ],
          [
            -1.30939,
            46.692823
          ],
          [
            -1.374127,
            34.450098
          ],
          [
            -0.691528,
            14.454572
          ],
          [
            -0.451177,
            -11.627752
          ],
          [
            -0.695066,
            -22.505183
          ],
          [
            -1.230868,
            -31.322566
          ],
          [
            -1.301031,
            -41.667709
          ],
          [
            -1.02096,
            -45.694462
          ],
          [
            -0.98141,
            -48.888216
          ],
          [
            -0.86122,
            -49.420512
          ],
          [
            -0.347279,
            -49.94539
          ],
          [
            0.185013,
            -49.859763
          ],
          [
            0.675217,
            -49.420512
          ],
          [
            0.884897,
            -48.888216
          ],
          [
            0.355285,
            -41.96842
          ],
          [
            0.44126,
            -32.387153
          ],
          [
            1.383515,
            -13.988506
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.202717373002118,
      "length": 13.72653553957084,
      "loops": [
        [
          [
            0.49695,
            -11.627752
          ],
          [
            0.147316,
            45.327529
          ],
          [
            -0.049087,
            46.924406
          ],
          [
            -0.347279,
            47.542918
          ],
          [
            -0.879569,
            47.788388
          ],
          [
            -1.326261,
            47.456698
          ],
          [
            -1.434193,
            46.924406
          ],
          [
            -1.540927,
            28.343709
          ],
          [
            -1.077075,
            5.405604
          ],
          [
            -1.09136,
            -6.255294
          ],
          [
            -1.386483,
            -22.805896
          ],
          [
            -1.297135,
            -36.063668
          ],
          [
            -1.418633,
            -38.77466
          ],
          [
            -1.183555,
            -42.451176
          ],
          [
            -1.342374,
            -48.355926
          ],
          [
            -1.235355,
            -49.420512
          ],
          [
            -0.879569,
            -49.889111
          ],
          [
            -0.347279,
            -49.859137
          ],
          [
            0.079932,
            -49.420512
          ],
          [
            0.25274,
            -48.888216
          ],
          [
            0.321459,
            -47.241805
          ],
          [
            0.245264,
            -28.661111
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.523214225578384,
      "length": 4.5759144738505055,
      "loops": [
        [
          [
            -1.960257,
            -26.434533
          ],
          [
            -2.085417,
            -7.272008
          ],
          [
            -1.799139,
            9.663942
          ],
          [
            -2.021334,
            20.842082
          ],
          [
            -1.768895,
            29.358759
          ],
          [
            -1.616425,
            46.924406
          ],
          [
            -1.411864,
            48.355555
          ],
          [
            -0.879569,
            48.918455
          ],
          [
            -0.363991,
            48.716404
          ],
          [
            -0.188535,
            48.423878
          ],
          [
            0.04037,
            45.327529
          ],
          [
            0.047444,
            8.599355
          ],
          [
            -0.162568,
            -24.837656
          ],
          [
            0.082526,
            -43.467891
          ],
          [
            -0.118965,
            -48.888216
          ],
          [
            -0.347279,
            -49.245201
          ],
          [
            -0.879569,
            -49.388259
          ],
          [
            -1.341106,
            -48.888216
          ],
          [
            -1.450768,
            -48.355926
          ],
          [
            -1.812032,
            -41.96842
          ],
          [
            -1.950245,
            -33.451742
          ],
          [
            -1.780673,
            -29.725691
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.227238475,
    -0.154190835,
    0.19147691500000003
  ],
  "construction_scale": 215.86826457824768,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
