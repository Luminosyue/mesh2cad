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
      "start": -10.11965399592935,
      "length": 1.2270295129391522,
      "loops": [
        [
          [
            -1.087989,
            49.267788
          ],
          [
            -0.047434,
            49.578977
          ],
          [
            0.534759,
            49.492043
          ],
          [
            1.021971,
            49.267788
          ],
          [
            0.945389,
            48.6856
          ],
          [
            0.534759,
            48.210888
          ],
          [
            -0.047434,
            47.865821
          ],
          [
            -0.984502,
            48.6856
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -8.893029269150034,
      "length": 1.2270295129391522,
      "loops": [
        [
          [
            2.691865,
            -48.53968
          ],
          [
            2.637224,
            43.311569
          ],
          [
            2.499421,
            47.386881
          ],
          [
            2.788898,
            48.6856
          ],
          [
            2.685272,
            49.133441
          ],
          [
            2.281321,
            49.706127
          ],
          [
            1.699127,
            49.893642
          ],
          [
            -2.37618,
            49.80539
          ],
          [
            -2.823652,
            49.267788
          ],
          [
            -2.397917,
            46.939038
          ],
          [
            -2.518821,
            -48.127868
          ],
          [
            -2.463257,
            -49.121865
          ],
          [
            -2.149721,
            -49.704058
          ],
          [
            -1.793995,
            -49.906462
          ],
          [
            -1.211803,
            -49.957547
          ],
          [
            -0.395698,
            -49.704058
          ],
          [
            -0.047434,
            -49.34699
          ],
          [
            0.534759,
            -49.470924
          ],
          [
            0.982597,
            -49.846436
          ],
          [
            1.564781,
            -49.989137
          ],
          [
            2.146973,
            -49.829199
          ],
          [
            2.651988,
            -49.121865
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.666404542370719,
      "length": 2.4536542397184675,
      "loops": [
        [
          [
            0.822873,
            -47.805535
          ],
          [
            0.755047,
            45.192478
          ],
          [
            0.534759,
            45.949725
          ],
          [
            -0.047434,
            45.978109
          ],
          [
            -0.355844,
            45.774664
          ],
          [
            -0.493854,
            45.056712
          ],
          [
            -0.380164,
            18.836534
          ],
          [
            -0.500742,
            -46.210936
          ],
          [
            -0.657493,
            -49.121865
          ],
          [
            -1.108582,
            -49.802534
          ],
          [
            -1.793995,
            -49.976672
          ],
          [
            -2.37618,
            -49.745551
          ],
          [
            -2.696186,
            -49.121865
          ],
          [
            -2.751233,
            -47.957496
          ],
          [
            -2.601064,
            47.418006
          ],
          [
            -3.011777,
            49.267788
          ],
          [
            -2.37618,
            49.896484
          ],
          [
            2.228894,
            49.866698
          ],
          [
            2.863504,
            49.307421
          ],
          [
            2.965409,
            48.6856
          ],
          [
            2.763127,
            47.521228
          ],
          [
            2.904855,
            41.699353
          ],
          [
            2.963106,
            -48.53968
          ],
          [
            2.922271,
            -49.121865
          ],
          [
            2.600366,
            -49.704058
          ],
          [
            2.178098,
            -49.954595
          ],
          [
            1.699127,
            -49.967989
          ],
          [
            1.258234,
            -49.704058
          ],
          [
            0.910799,
            -49.121865
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.213155088812089,
      "length": 1.2270295129391522,
      "loops": [
        [
          [
            -2.186316,
            46.356852
          ],
          [
            -2.307839,
            -48.53968
          ],
          [
            -2.253747,
            -49.121865
          ],
          [
            -1.793995,
            -49.74621
          ],
          [
            -0.608339,
            -49.996444
          ],
          [
            1.116943,
            -49.985663
          ],
          [
            1.699127,
            -49.874989
          ],
          [
            2.281321,
            -49.374814
          ],
          [
            2.470777,
            -47.957496
          ],
          [
            2.39241,
            46.879724
          ],
          [
            2.464494,
            47.521228
          ],
          [
            3.096826,
            49.267788
          ],
          [
            2.863504,
            49.741797
          ],
          [
            2.281321,
            49.942676
          ],
          [
            -2.37618,
            49.943759
          ],
          [
            -3.003238,
            49.267788
          ],
          [
            -2.347352,
            47.521228
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.9865303620327737,
      "length": 14.10658914412196,
      "loops": [
        [
          [
            -1.793995,
            46.838396
          ],
          [
            -2.958373,
            49.331241
          ],
          [
            -2.37618,
            49.935476
          ],
          [
            2.281321,
            49.938024
          ],
          [
            2.863504,
            49.690213
          ],
          [
            3.070744,
            49.267788
          ],
          [
            2.05583,
            46.939038
          ],
          [
            1.116943,
            46.162387
          ],
          [
            -0.047434,
            45.887257
          ],
          [
            -1.211803,
            46.322068
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.7302846000000001,
    -0.57515417,
    0.352435995
  ],
  "construction_scale": 118.05144752914188,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
