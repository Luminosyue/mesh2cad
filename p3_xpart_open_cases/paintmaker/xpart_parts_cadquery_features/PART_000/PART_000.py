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
            -29.951232,
            -31.056941
          ],
          [
            -29.935604,
            35.037187
          ],
          [
            -30.15165,
            44.654209
          ],
          [
            -29.973663,
            46.133751
          ],
          [
            -29.633831,
            46.658921
          ],
          [
            -27.907699,
            47.033366
          ],
          [
            -20.502066,
            47.525336
          ],
          [
            5.389917,
            47.711079
          ],
          [
            21.903544,
            47.362373
          ],
          [
            27.08194,
            46.995508
          ],
          [
            28.178236,
            46.380343
          ],
          [
            28.455517,
            45.887162
          ],
          [
            28.533518,
            45.147391
          ],
          [
            28.594618,
            32.817875
          ],
          [
            29.031073,
            16.53499
          ],
          [
            29.409414,
            -11.822896
          ],
          [
            30.291955,
            -41.397883
          ],
          [
            30.248653,
            -45.104664
          ],
          [
            29.927373,
            -45.840156
          ],
          [
            28.314892,
            -47.044
          ],
          [
            20.424002,
            -47.487127
          ],
          [
            -1.769126,
            -47.760522
          ],
          [
            -15.824774,
            -47.689185
          ],
          [
            -25.441796,
            -47.449402
          ],
          [
            -28.392956,
            -47.190419
          ],
          [
            -29.140651,
            -46.866585
          ],
          [
            -29.396666,
            -46.337616
          ],
          [
            -29.556659,
            -44.865999
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    -0.00015847499999999126,
    0.0008598499999999953,
    -0.00042725499999995975
  ],
  "construction_scale": 50.00167930639951,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
