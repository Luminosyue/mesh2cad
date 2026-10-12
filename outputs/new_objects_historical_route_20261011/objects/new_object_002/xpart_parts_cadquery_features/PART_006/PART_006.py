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
      0.9999619534317068,
      -0.00795605444910809,
      0.0035767145046659387
    ],
    [
      -0.0016922953056839746,
      0.22530226828041727,
      0.9742874442608288
    ],
    [
      -0.008557325846514165,
      -0.9742564288242089,
      0.2252802323086845
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.96131890536753,
      "length": 101.94425261192066,
      "loops": [
        [
          [
            -2.09386,
            -3.522707
          ],
          [
            3.238809,
            -3.328486
          ],
          [
            5.01755,
            -2.566228
          ],
          [
            5.847549,
            -1.612003
          ],
          [
            6.123136,
            -0.700867
          ],
          [
            6.065211,
            1.123635
          ],
          [
            5.625459,
            2.037389
          ],
          [
            5.026399,
            2.662929
          ],
          [
            4.138519,
            3.163185
          ],
          [
            2.361767,
            3.574235
          ],
          [
            -2.970581,
            3.569483
          ],
          [
            -4.893395,
            2.988148
          ],
          [
            -5.902902,
            2.079711
          ],
          [
            -6.347194,
            1.169203
          ],
          [
            -6.433788,
            -0.65477
          ],
          [
            -6.165177,
            -1.567903
          ],
          [
            -5.646789,
            -2.361295
          ],
          [
            -4.759095,
            -2.969642
          ],
          [
            -3.870946,
            -3.309094
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.053386425,
    0.28407517,
    -0.22009668000000002
  ],
  "construction_scale": 360.4032970558582,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
