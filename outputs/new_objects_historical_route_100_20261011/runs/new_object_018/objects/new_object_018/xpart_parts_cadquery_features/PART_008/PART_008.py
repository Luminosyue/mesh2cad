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
      "start": -10.711783573053996,
      "length": 1.2988264801979514,
      "loops": [
        [
          [
            35.048012,
            12.596818
          ],
          [
            6.784565,
            12.33153
          ],
          [
            -11.90083,
            12.447437
          ],
          [
            -24.759457,
            12.708593
          ],
          [
            -37.871497,
            13.226101
          ],
          [
            -40.499111,
            13.626716
          ],
          [
            -41.229917,
            13.905317
          ],
          [
            -41.547402,
            14.225238
          ],
          [
            -41.45603,
            14.47759
          ],
          [
            -40.657645,
            14.826204
          ],
          [
            -39.560169,
            15.070362
          ],
          [
            -34.385815,
            15.954728
          ],
          [
            -31.899906,
            16.169466
          ],
          [
            -17.693597,
            16.473951
          ],
          [
            -2.260185,
            16.536335
          ],
          [
            29.346032,
            16.346176
          ],
          [
            44.889747,
            16.014046
          ],
          [
            46.792871,
            15.876011
          ],
          [
            48.170323,
            15.541325
          ],
          [
            48.700427,
            15.007694
          ],
          [
            48.9906,
            14.225238
          ],
          [
            48.755673,
            13.720533
          ],
          [
            48.170323,
            13.316697
          ],
          [
            45.899153,
            13.01094
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -9.413385564198967,
      "length": 11.686010551038189,
      "loops": [
        [
          [
            -49.635838,
            -5.070022
          ],
          [
            -49.55129,
            -18.075842
          ],
          [
            -49.237622,
            -18.367735
          ],
          [
            -48.732916,
            -18.465219
          ],
          [
            -45.199985,
            -18.337145
          ],
          [
            -44.714198,
            -17.82349
          ],
          [
            -44.613309,
            -17.318786
          ],
          [
            -44.699683,
            11.197009
          ],
          [
            -44.647137,
            11.449365
          ],
          [
            -44.190575,
            11.724444
          ],
          [
            48.675028,
            11.770986
          ],
          [
            49.432084,
            11.97702
          ],
          [
            49.838998,
            12.458771
          ],
          [
            49.919772,
            15.234646
          ],
          [
            49.791833,
            17.253463
          ],
          [
            49.432084,
            17.745965
          ],
          [
            48.675028,
            17.877591
          ],
          [
            -44.190575,
            17.724367
          ],
          [
            -48.732916,
            17.567342
          ],
          [
            -49.237622,
            17.235909
          ],
          [
            -49.506936,
            16.12756
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.272196515496301,
      "length": 1.2988264801979532,
      "loops": [
        [
          [
            -49.663404,
            -17.82349
          ],
          [
            -49.52234,
            15.991702
          ],
          [
            -49.237622,
            17.121262
          ],
          [
            -48.732916,
            17.583218
          ],
          [
            -46.701355,
            17.703715
          ],
          [
            40.107797,
            17.789835
          ],
          [
            48.43542,
            17.917272
          ],
          [
            49.432084,
            17.791201
          ],
          [
            49.846968,
            17.253463
          ],
          [
            49.956851,
            12.963477
          ],
          [
            49.682064,
            12.453508
          ],
          [
            48.927378,
            12.094063
          ],
          [
            -43.938224,
            11.964749
          ],
          [
            -44.579602,
            11.449365
          ],
          [
            -44.661104,
            10.944659
          ],
          [
            -44.608448,
            -17.318786
          ],
          [
            -44.72206,
            -17.82349
          ],
          [
            -45.199985,
            -18.28909
          ],
          [
            -45.704691,
            -18.388902
          ],
          [
            -48.22821,
            -18.469805
          ],
          [
            -49.237622,
            -18.338608
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 3.570594524351332,
      "length": 5.843219511190555,
      "loops": [
        [
          [
            -44.69528,
            18.136528
          ],
          [
            49.179733,
            18.288193
          ],
          [
            49.719821,
            18.01052
          ],
          [
            49.921152,
            17.505814
          ],
          [
            49.910571,
            14.225238
          ],
          [
            49.684434,
            13.593953
          ],
          [
            49.179733,
            13.270217
          ],
          [
            43.880336,
            13.105502
          ],
          [
            -19.207711,
            13.122216
          ],
          [
            -41.471124,
            13.070119
          ],
          [
            -43.938224,
            12.947817
          ],
          [
            -44.576261,
            12.458771
          ],
          [
            -44.723412,
            11.505787
          ],
          [
            -44.694661,
            -17.318786
          ],
          [
            -44.89917,
            -17.82349
          ],
          [
            -45.187345,
            -18.075842
          ],
          [
            -46.013465,
            -18.26798
          ],
          [
            -48.985267,
            -18.264564
          ],
          [
            -49.489972,
            -18.139623
          ],
          [
            -49.792622,
            -17.82349
          ],
          [
            -49.909076,
            -17.066434
          ],
          [
            -49.861853,
            16.496408
          ],
          [
            -49.710567,
            17.505814
          ],
          [
            -49.237622,
            17.911848
          ],
          [
            -48.480565,
            18.076163
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 9.413385564198965,
      "length": 1.2988264801979532,
      "loops": [
        [
          [
            -45.364266,
            18.234277
          ],
          [
            48.927378,
            18.404647
          ],
          [
            49.432084,
            18.253977
          ],
          [
            49.85638,
            17.75817
          ],
          [
            49.843066,
            14.47759
          ],
          [
            49.678224,
            13.866368
          ],
          [
            49.179733,
            13.45743
          ],
          [
            43.627985,
            13.200933
          ],
          [
            -18.198302,
            13.280272
          ],
          [
            -42.171761,
            13.145841
          ],
          [
            -43.938224,
            13.01635
          ],
          [
            -44.656771,
            12.458771
          ],
          [
            -44.761829,
            11.954066
          ],
          [
            -44.799062,
            -17.318786
          ],
          [
            -45.199985,
            -17.964387
          ],
          [
            -46.209393,
            -18.208318
          ],
          [
            -49.237622,
            -18.151322
          ],
          [
            -49.791756,
            -17.82349
          ],
          [
            -49.956974,
            -16.902153
          ],
          [
            -49.931766,
            14.894223
          ],
          [
            -49.829716,
            17.253463
          ],
          [
            -49.699292,
            17.614206
          ],
          [
            -49.325692,
            17.953002
          ],
          [
            -48.480565,
            18.15913
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.317177055,
    0.016669275000000004,
    -0.009580460000000013
  ],
  "construction_scale": 102.34005446865187,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
