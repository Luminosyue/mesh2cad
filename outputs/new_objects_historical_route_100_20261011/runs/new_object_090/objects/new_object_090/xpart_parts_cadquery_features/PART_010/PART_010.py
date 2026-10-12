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
      "start": -2.3858634458705996,
      "length": 0.4338887883324894,
      "loops": [
        [
          [
            -0.074694,
            28.767167
          ],
          [
            0.058956,
            21.750957
          ],
          [
            -0.604041,
            21.082747
          ],
          [
            -0.677211,
            19.746326
          ],
          [
            -0.524723,
            19.412221
          ],
          [
            0.192553,
            18.923983
          ],
          [
            0.281617,
            18.409905
          ],
          [
            0.121249,
            7.050325
          ],
          [
            0.383474,
            -25.695938
          ],
          [
            0.276148,
            -48.745251
          ],
          [
            0.34657,
            -49.413459
          ],
          [
            0.526655,
            -49.645261
          ],
          [
            2.197183,
            -49.725283
          ],
          [
            2.778498,
            -49.413459
          ],
          [
            2.828401,
            -49.079355
          ],
          [
            2.866737,
            47.144345
          ],
          [
            2.858614,
            49.147587
          ],
          [
            2.803824,
            49.481691
          ],
          [
            2.531286,
            49.725398
          ],
          [
            1.193478,
            49.574634
          ],
          [
            0.526655,
            48.741695
          ],
          [
            0.192553,
            47.487866
          ],
          [
            0.135636,
            33.44464
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.952070092075945,
      "length": 2.024464418912889,
      "loops": [
        [
          [
            -0.265368,
            18.74401
          ],
          [
            -0.272425,
            -11.993672
          ],
          [
            -0.475659,
            -12.430817
          ],
          [
            -2.512132,
            -12.327778
          ],
          [
            -2.814394,
            -12.451187
          ],
          [
            -3.004079,
            -12.995988
          ],
          [
            -2.848662,
            -16.671147
          ],
          [
            -3.032305,
            -19.009883
          ],
          [
            -3.030543,
            -49.079355
          ],
          [
            -2.822752,
            -49.747567
          ],
          [
            -2.48029,
            -49.888702
          ],
          [
            2.531286,
            -49.963642
          ],
          [
            2.971781,
            -49.747567
          ],
          [
            3.142508,
            -49.079355
          ],
          [
            3.150326,
            49.147587
          ],
          [
            2.948773,
            49.815799
          ],
          [
            2.531286,
            49.990193
          ],
          [
            0.192553,
            49.757705
          ],
          [
            -0.141557,
            49.532597
          ],
          [
            -0.229697,
            49.147587
          ],
          [
            -0.209195,
            30.771797
          ],
          [
            -0.537715,
            30.103588
          ],
          [
            -0.344403,
            22.085063
          ],
          [
            -0.475659,
            21.905115
          ],
          [
            -1.812079,
            21.554006
          ],
          [
            -2.026627,
            21.082747
          ],
          [
            -2.005379,
            19.746326
          ],
          [
            -1.812079,
            19.257397
          ],
          [
            -1.477975,
            19.067915
          ],
          [
            -0.454535,
            18.921701
          ]
        ],
        [
          [
            -0.825191,
            -14.985192
          ],
          [
            -0.475659,
            -15.060165
          ],
          [
            -0.434403,
            -15.334724
          ],
          [
            -0.475659,
            -16.620852
          ],
          [
            -1.355918,
            -16.671147
          ],
          [
            -1.533753,
            -16.337041
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.0722988922991088,
      "length": 2.313659988109326,
      "loops": [
        [
          [
            1.082447,
            -49.413459
          ],
          [
            1.066902,
            49.147587
          ],
          [
            1.194867,
            49.698545
          ],
          [
            1.528971,
            49.956801
          ],
          [
            2.531286,
            49.981151
          ],
          [
            2.934554,
            49.815799
          ],
          [
            3.135031,
            49.147587
          ],
          [
            3.146954,
            -48.993583
          ],
          [
            2.950926,
            -49.747567
          ],
          [
            2.531286,
            -49.950719
          ],
          [
            1.528971,
            -49.948065
          ],
          [
            1.196214,
            -49.717441
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.47694804,
    -0.00025179000000000173,
    -0.233029835
  ],
  "construction_scale": 135.4945619257571,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
