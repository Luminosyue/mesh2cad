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
      "start": -50.0,
      "length": 33.33533333333334,
      "loops": [
        [
          [
            7.319038,
            -14.461294
          ],
          [
            6.931027,
            -39.469788
          ],
          [
            6.834909,
            -40.18634
          ],
          [
            6.32266,
            -40.601093
          ],
          [
            6.059998,
            -40.494285
          ],
          [
            5.764778,
            -39.982034
          ],
          [
            5.648283,
            -37.420791
          ],
          [
            5.810756,
            -28.712557
          ],
          [
            5.810079,
            17.309037
          ],
          [
            5.754192,
            29.683833
          ],
          [
            5.503272,
            37.879817
          ],
          [
            5.298162,
            38.34567
          ],
          [
            4.785913,
            38.385797
          ],
          [
            -2.385574,
            38.218781
          ],
          [
            -6.995815,
            38.371031
          ],
          [
            -7.541439,
            38.904313
          ],
          [
            -7.63274,
            39.416564
          ],
          [
            -7.508064,
            40.110466
          ],
          [
            -6.995815,
            40.483406
          ],
          [
            5.298162,
            40.300374
          ],
          [
            6.32266,
            40.148903
          ],
          [
            6.628502,
            39.928814
          ],
          [
            6.889596,
            39.416564
          ],
          [
            7.447011,
            14.224653
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -16.666666666666664,
      "length": 66.66866666666665,
      "loops": [
        [
          [
            5.719036,
            33.295353
          ],
          [
            5.857582,
            -18.954051
          ],
          [
            5.665682,
            -37.420791
          ],
          [
            5.759743,
            -39.982034
          ],
          [
            6.32266,
            -40.456249
          ],
          [
            6.834909,
            -39.995023
          ],
          [
            6.882139,
            -39.444013
          ],
          [
            7.327492,
            -17.443079
          ],
          [
            7.520979,
            3.559132
          ],
          [
            7.359567,
            24.587118
          ],
          [
            6.892626,
            39.928814
          ],
          [
            6.639571,
            40.441064
          ],
          [
            6.32266,
            40.650366
          ],
          [
            5.810411,
            40.659695
          ],
          [
            3.249166,
            40.49028
          ],
          [
            -6.995815,
            40.502677
          ],
          [
            -7.508064,
            40.060355
          ],
          [
            -7.568209,
            38.904313
          ],
          [
            -6.995815,
            38.302198
          ],
          [
            0.149896,
            38.291109
          ],
          [
            5.298162,
            38.462552
          ],
          [
            5.589079,
            37.879817
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0018822399999999795,
    0.07552371999999999,
    0.010375679999999998
  ],
  "construction_scale": 51.934951390287736,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
