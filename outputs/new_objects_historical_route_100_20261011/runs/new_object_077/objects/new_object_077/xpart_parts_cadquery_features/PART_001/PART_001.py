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
      "start": -35.221261015218914,
      "length": 4.270652609861085,
      "loops": [
        [
          [
            18.794791,
            -17.231959
          ],
          [
            19.106624,
            -45.468275
          ],
          [
            18.969904,
            -46.425552
          ],
          [
            18.477613,
            -47.129236
          ],
          [
            17.524241,
            -47.41319
          ],
          [
            16.574974,
            -47.491713
          ],
          [
            -1.000912,
            -46.887948
          ],
          [
            -15.285166,
            -47.056598
          ],
          [
            -16.131954,
            -46.79704
          ],
          [
            -16.618319,
            -46.13266
          ],
          [
            -16.9991,
            -44.80389
          ],
          [
            -17.283737,
            -42.816157
          ],
          [
            -17.607019,
            -36.831285
          ],
          [
            -17.565475,
            -29.855253
          ],
          [
            -18.277192,
            -10.920311
          ],
          [
            -18.516525,
            10.007781
          ],
          [
            -19.288,
            44.223552
          ],
          [
            -19.106543,
            46.881088
          ],
          [
            -18.67253,
            47.622659
          ],
          [
            -17.942703,
            48.087176
          ],
          [
            -16.358686,
            48.282868
          ],
          [
            1.988815,
            48.528156
          ],
          [
            13.617443,
            48.876148
          ],
          [
            15.608686,
            48.376282
          ],
          [
            16.937452,
            47.267378
          ],
          [
            17.336157,
            46.615407
          ],
          [
            17.812387,
            44.381265
          ],
          [
            18.002744,
            40.500725
          ],
          [
            18.211935,
            10.339974
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -30.952017255798438,
      "length": 61.90544336203749,
      "loops": [
        [
          [
            -7.598077,
            -49.78764
          ],
          [
            3.88091,
            -49.978784
          ],
          [
            12.286765,
            -49.585386
          ],
          [
            14.612109,
            -49.280991
          ],
          [
            15.940877,
            -48.489866
          ],
          [
            18.930605,
            -48.179787
          ],
          [
            19.594989,
            -47.780901
          ],
          [
            19.980679,
            -47.129236
          ],
          [
            20.08142,
            -46.13266
          ],
          [
            19.760749,
            -40.052147
          ],
          [
            19.827149,
            -1.951129
          ],
          [
            19.332853,
            31.268066
          ],
          [
            18.917049,
            39.34173
          ],
          [
            18.262851,
            47.545474
          ],
          [
            17.784473,
            49.206432
          ],
          [
            17.502861,
            49.538624
          ],
          [
            16.937452,
            49.808384
          ],
          [
            -3.326256,
            49.814872
          ],
          [
            -12.627631,
            49.484534
          ],
          [
            -17.278319,
            48.864823
          ],
          [
            -18.307544,
            48.209856
          ],
          [
            -18.969607,
            46.881088
          ],
          [
            -19.385068,
            43.559169
          ],
          [
            -19.699742,
            38.244097
          ],
          [
            -19.94216,
            27.946147
          ],
          [
            -19.888702,
            -37.495667
          ],
          [
            -19.677393,
            -46.464851
          ],
          [
            -19.249089,
            -47.793621
          ],
          [
            -18.607086,
            -48.396466
          ],
          [
            -17.610509,
            -48.822778
          ],
          [
            -11.298863,
            -49.533797
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 30.952017255798438,
      "length": 4.270652609861085,
      "loops": [
        [
          [
            -18.759825,
            14.055875
          ],
          [
            -19.327096,
            -44.850589
          ],
          [
            -19.268847,
            -46.464851
          ],
          [
            -18.816098,
            -47.793621
          ],
          [
            -17.951976,
            -48.458001
          ],
          [
            -16.992824,
            -48.671718
          ],
          [
            -11.584356,
            -49.471009
          ],
          [
            -7.598053,
            -49.615872
          ],
          [
            -4.655025,
            -49.283427
          ],
          [
            -4.118521,
            -49.122386
          ],
          [
            -3.918514,
            -48.790197
          ],
          [
            -4.648115,
            -48.451091
          ],
          [
            -8.355107,
            -47.793621
          ],
          [
            -8.276511,
            -47.461425
          ],
          [
            4.314158,
            -47.069456
          ],
          [
            9.277345,
            -47.14893
          ],
          [
            11.538196,
            -47.461425
          ],
          [
            8.300463,
            -47.884539
          ],
          [
            7.37374,
            -48.12581
          ],
          [
            6.840047,
            -48.458001
          ],
          [
            8.208803,
            -48.790197
          ],
          [
            9.286184,
            -48.801051
          ],
          [
            13.947725,
            -48.104303
          ],
          [
            17.934029,
            -47.820811
          ],
          [
            18.930605,
            -47.47061
          ],
          [
            19.262797,
            -46.953873
          ],
          [
            19.357324,
            -46.13266
          ],
          [
            18.890768,
            -28.194292
          ],
          [
            18.681052,
            2.699559
          ],
          [
            18.796831,
            9.675589
          ],
          [
            18.69625,
            31.885751
          ],
          [
            18.266131,
            43.891361
          ],
          [
            17.964224,
            46.216705
          ],
          [
            17.601836,
            46.993448
          ],
          [
            16.937452,
            47.298835
          ],
          [
            15.940877,
            47.38058
          ],
          [
            -10.582011,
            46.933556
          ],
          [
            -16.276198,
            46.55444
          ],
          [
            -17.278319,
            45.985317
          ],
          [
            -17.560375,
            45.552319
          ],
          [
            -17.74479,
            44.555744
          ],
          [
            -18.171463,
            37.247522
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00011225000000000818,
    3.2190000000001384e-05,
    -0.12853458499999998
  ],
  "construction_scale": 134.7186379018844,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
