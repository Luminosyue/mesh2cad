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
      "start": -39.59086454683629,
      "length": 50.38995669419171,
      "loops": [
        [
          [
            -49.500153,
            9.846567
          ],
          [
            -49.194227,
            11.361134
          ],
          [
            -48.540185,
            11.614168
          ],
          [
            -43.744055,
            11.385915
          ],
          [
            -25.821676,
            11.109723
          ],
          [
            -14.967279,
            11.242693
          ],
          [
            -12.669285,
            10.85063
          ],
          [
            0.456964,
            10.749954
          ],
          [
            48.392118,
            11.591243
          ],
          [
            49.195699,
            11.108706
          ],
          [
            49.377363,
            9.872709
          ],
          [
            49.172559,
            -2.017544
          ],
          [
            49.526971,
            -10.095235
          ],
          [
            48.896975,
            -10.996041
          ],
          [
            47.887261,
            -11.380938
          ],
          [
            34.029873,
            -11.65084
          ],
          [
            -3.077026,
            -11.789008
          ],
          [
            -47.278045,
            -11.609245
          ],
          [
            -48.792612,
            -11.130534
          ],
          [
            -49.309343,
            -10.095235
          ],
          [
            -49.064693,
            -4.010824
          ],
          [
            -49.074874,
            1.516447
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.79750851277354,
      "length": 14.39826165161325,
      "loops": [
        [
          [
            -49.108484,
            0.169433
          ],
          [
            -49.085578,
            10.098994
          ],
          [
            -48.882803,
            10.60385
          ],
          [
            -48.287759,
            10.850808
          ],
          [
            -17.491558,
            10.693474
          ],
          [
            -15.219706,
            10.557554
          ],
          [
            -13.285158,
            10.111463
          ],
          [
            -11.18086,
            10.06308
          ],
          [
            11.285221,
            10.083448
          ],
          [
            24.411471,
            10.66701
          ],
          [
            48.139692,
            10.874083
          ],
          [
            48.644544,
            10.657657
          ],
          [
            48.873674,
            10.351423
          ],
          [
            49.023794,
            9.341711
          ],
          [
            49.341516,
            -10.095235
          ],
          [
            49.149401,
            -10.707824
          ],
          [
            48.644544,
            -11.318646
          ],
          [
            47.993037,
            -11.609803
          ],
          [
            47.129978,
            -11.746921
          ],
          [
            -47.530476,
            -11.749406
          ],
          [
            -48.792612,
            -11.328525
          ],
          [
            -49.596401,
            -10.600091
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.194186529804917,
      "length": 14.39826165161325,
      "loops": [
        [
          [
            48.659269,
            9.594139
          ],
          [
            49.284838,
            -10.095235
          ],
          [
            49.079806,
            -10.852519
          ],
          [
            48.712513,
            -11.357374
          ],
          [
            47.634835,
            -11.767049
          ],
          [
            -45.763479,
            -11.80265
          ],
          [
            -47.530476,
            -11.740313
          ],
          [
            -48.792612,
            -11.516944
          ],
          [
            -49.480249,
            -11.104947
          ],
          [
            -49.874886,
            -10.347663
          ],
          [
            -49.638711,
            -4.289394
          ],
          [
            -49.036475,
            3.989716
          ],
          [
            -49.006717,
            9.341711
          ],
          [
            -48.792612,
            10.03884
          ],
          [
            -48.287759,
            10.278982
          ],
          [
            -17.239129,
            10.185629
          ],
          [
            -15.724562,
            10.101357
          ],
          [
            -13.149274,
            9.666755
          ],
          [
            4.268249,
            9.560812
          ],
          [
            12.54736,
            9.659974
          ],
          [
            22.896904,
            10.214331
          ],
          [
            47.634835,
            10.424672
          ],
          [
            48.392118,
            10.151223
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0014463849999999945,
    -0.004968359999999991,
    -0.014176219999999962
  ],
  "construction_scale": 51.18537523269192,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
