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
      "start": -8.184452940413966,
      "length": 2.976492083722694,
      "loops": [
        [
          [
            -2.278025,
            -49.206468
          ],
          [
            -2.136903,
            23.121239
          ],
          [
            -1.906232,
            39.061304
          ],
          [
            -1.840182,
            40.091726
          ],
          [
            -1.621515,
            40.56895
          ],
          [
            -1.465214,
            39.715906
          ],
          [
            -1.355981,
            19.677063
          ],
          [
            -1.291158,
            -48.267148
          ],
          [
            -1.239345,
            -49.547903
          ],
          [
            -1.132615,
            -49.832684
          ],
          [
            -0.682194,
            -49.990597
          ],
          [
            -0.320755,
            -49.832684
          ],
          [
            -0.211337,
            -48.893363
          ],
          [
            -0.126231,
            40.342122
          ],
          [
            -0.040263,
            40.968334
          ],
          [
            0.257127,
            41.259077
          ],
          [
            2.672845,
            41.281442
          ],
          [
            3.052638,
            41.594549
          ],
          [
            3.482987,
            44.725618
          ],
          [
            3.41211,
            45.049062
          ],
          [
            3.07509,
            45.19737
          ],
          [
            0.755304,
            43.786298
          ],
          [
            -0.426005,
            42.846978
          ],
          [
            -1.308408,
            41.902552
          ],
          [
            -3.18705,
            41.726237
          ],
          [
            -3.55035,
            41.281442
          ],
          [
            -3.374911,
            11.574398
          ],
          [
            -3.392795,
            -49.206468
          ],
          [
            -3.290778,
            -49.832684
          ],
          [
            -2.873942,
            -49.997557
          ],
          [
            -2.414788,
            -49.832684
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.208288234808888,
      "length": 13.393068553340466,
      "loops": [
        [
          [
            1.82277,
            47.201972
          ],
          [
            2.466586,
            45.351832
          ],
          [
            -1.038205,
            42.846978
          ],
          [
            -1.363568,
            42.220763
          ],
          [
            -1.282475,
            41.907657
          ],
          [
            -0.995301,
            41.667493
          ],
          [
            2.448875,
            41.780434
          ],
          [
            2.761983,
            41.834608
          ],
          [
            2.948129,
            42.057836
          ],
          [
            3.3698,
            45.038726
          ],
          [
            3.397063,
            49.553832
          ],
          [
            3.07509,
            49.952149
          ],
          [
            2.073311,
            49.422224
          ],
          [
            1.784132,
            49.109116
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.07309289000000001,
    -0.21129386499999997,
    -0.40579276
  ],
  "construction_scale": 63.489410642467064,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
