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
      0.22412897447680175,
      -0.8867306399422231,
      0.4043203865595111
    ],
    [
      0.06735135568272549,
      -0.39978956805996785,
      -0.9141291463234958
    ],
    [
      0.972229395609738,
      0.23211435426978608,
      -0.029881915170284646
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -7.107981893653906,
      "length": 14.310228098607265,
      "loops": [
        [
          [
            -47.795203,
            -13.366221
          ],
          [
            -31.688644,
            -14.308148
          ],
          [
            -18.564532,
            -14.44236
          ],
          [
            5.823171,
            -14.96591
          ],
          [
            22.485499,
            -15.526928
          ],
          [
            45.03953,
            -15.855766
          ],
          [
            45.792049,
            -15.611679
          ],
          [
            46.422665,
            -15.097243
          ],
          [
            46.906247,
            -13.92938
          ],
          [
            47.677426,
            14.859733
          ],
          [
            47.658406,
            16.524736
          ],
          [
            47.458983,
            17.273241
          ],
          [
            46.85064,
            17.840871
          ],
          [
            45.182693,
            18.263427
          ],
          [
            17.193997,
            18.874087
          ],
          [
            -0.527766,
            19.555607
          ],
          [
            -20.176771,
            19.743977
          ],
          [
            -26.757363,
            19.68744
          ],
          [
            -32.901778,
            19.270697
          ],
          [
            -36.951497,
            18.687203
          ],
          [
            -40.064718,
            17.939701
          ],
          [
            -43.684982,
            16.403663
          ],
          [
            -45.590949,
            14.891639
          ],
          [
            -47.179031,
            12.674542
          ],
          [
            -48.061503,
            10.166083
          ],
          [
            -48.766416,
            4.716454
          ],
          [
            -49.81467,
            -11.527003
          ],
          [
            -49.673275,
            -12.301172
          ],
          [
            -49.174756,
            -12.917384
          ]
        ],
        {
          "center": [
            -1.1114722237852186,
            2.2297987117195177
          ],
          "radius": 6.378382783518709
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    -0.021546205,
    -0.676058475,
    0.44660107000000004
  ],
  "construction_scale": 155.09193097472317,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
