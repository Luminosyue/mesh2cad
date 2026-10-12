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
      0.9545102915306645,
      0.29552782830712443,
      -0.03966618280249269
    ],
    [
      -0.29817742001067105,
      0.945768932573639,
      -0.12888503549403785
    ],
    [
      -0.0005740712724553052,
      0.13484965285307302,
      0.9908659049374844
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -13.383071465609799,
      "length": 26.394537487436537,
      "loops": [
        [
          [
            -45.652482,
            9.060732
          ],
          [
            -43.241743,
            -2.037015
          ],
          [
            -41.249961,
            -9.099665
          ],
          [
            -38.697415,
            -15.320428
          ],
          [
            -35.997416,
            -20.531423
          ],
          [
            -32.649689,
            -25.721923
          ],
          [
            -30.070888,
            -28.854428
          ],
          [
            -26.988132,
            -31.681882
          ],
          [
            -21.949648,
            -35.622506
          ],
          [
            -19.13795,
            -38.66357
          ],
          [
            -18.632107,
            -38.881363
          ],
          [
            -18.019845,
            -39.098266
          ],
          [
            -9.951328,
            -37.391474
          ],
          [
            36.309394,
            -29.752592
          ],
          [
            41.63763,
            -28.751729
          ],
          [
            43.135454,
            -27.970856
          ],
          [
            43.563965,
            -27.464232
          ],
          [
            43.935024,
            -26.525911
          ],
          [
            44.092726,
            -25.401729
          ],
          [
            43.93786,
            -23.125996
          ],
          [
            40.374623,
            -1.369151
          ],
          [
            34.901093,
            29.447358
          ],
          [
            34.306518,
            32.072421
          ],
          [
            33.746184,
            33.604694
          ],
          [
            32.682596,
            34.901777
          ],
          [
            31.578759,
            35.382178
          ],
          [
            30.348461,
            35.457705
          ],
          [
            18.502031,
            33.660686
          ],
          [
            -0.069211,
            30.406111
          ],
          [
            -13.384391,
            27.82997
          ],
          [
            -26.838249,
            24.992641
          ],
          [
            -37.174975,
            22.050508
          ],
          [
            -42.121006,
            20.223271
          ],
          [
            -44.926517,
            18.957775
          ],
          [
            -46.030231,
            18.037171
          ],
          [
            -46.55324,
            17.349824
          ],
          [
            -46.756867,
            16.99874
          ],
          [
            -46.91229,
            15.78182
          ]
        ],
        {
          "center": [
            7.098679310280332,
            -2.0198603208047246
          ],
          "radius": 12.977190764972104
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    0.6097001950000001,
    -0.14235894000000002,
    0.487280655
  ],
  "construction_scale": 242.6894593487996,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
