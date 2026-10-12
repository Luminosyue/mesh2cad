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
      "length": 100.0,
      "loops": [
        [
          [
            17.160175,
            -2.022212
          ],
          [
            17.258058,
            1.388848
          ],
          [
            17.111695,
            2.052131
          ],
          [
            7.403291,
            2.326228
          ],
          [
            7.035002,
            2.700794
          ],
          [
            7.403291,
            2.992677
          ],
          [
            17.374083,
            2.882259
          ],
          [
            17.898862,
            2.709726
          ],
          [
            19.116372,
            1.913627
          ],
          [
            19.554493,
            0.86407
          ],
          [
            19.593803,
            -0.710267
          ],
          [
            19.199581,
            -2.242136
          ],
          [
            18.686031,
            -2.78902
          ],
          [
            17.374083,
            -3.076019
          ],
          [
            14.225412,
            -2.681881
          ],
          [
            7.140901,
            -2.449428
          ],
          [
            -4.404227,
            -2.455743
          ],
          [
            -5.716174,
            -2.751813
          ],
          [
            -6.765731,
            -2.497515
          ],
          [
            -19.098027,
            -2.757166
          ],
          [
            -19.622807,
            -2.636725
          ],
          [
            -19.783561,
            -2.284603
          ],
          [
            -19.360417,
            -2.006031
          ],
          [
            -1.780335,
            -1.727535
          ],
          [
            8.715238,
            -1.804144
          ],
          [
            16.849306,
            -2.220838
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    0.0009372250000000137,
    -0.03751724000000001,
    -0.17333010999999998
  ],
  "construction_scale": 106.41054924390251,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
