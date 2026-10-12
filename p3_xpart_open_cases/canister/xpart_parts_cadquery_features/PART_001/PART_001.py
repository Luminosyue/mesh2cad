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
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -3.8374711173610847,
      "length": 7.674942234722169,
      "loops": [
        [
          [
            -26.894835,
            49.829821
          ],
          [
            26.04282,
            49.900591
          ],
          [
            36.149837,
            49.052657
          ],
          [
            40.139447,
            48.046043
          ],
          [
            43.374526,
            46.522408
          ],
          [
            45.373176,
            44.926564
          ],
          [
            46.653471,
            43.330716
          ],
          [
            47.547071,
            41.734871
          ],
          [
            48.462888,
            39.349905
          ],
          [
            49.177144,
            35.89224
          ],
          [
            49.539282,
            30.838733
          ],
          [
            49.626032,
            -26.079734
          ],
          [
            49.425832,
            -32.995062
          ],
          [
            48.653296,
            -38.855294
          ],
          [
            47.483896,
            -42.312959
          ],
          [
            45.991054,
            -44.440365
          ],
          [
            44.926984,
            -45.547827
          ],
          [
            43.597112,
            -46.551722
          ],
          [
            40.671397,
            -48.154823
          ],
          [
            38.279593,
            -48.961905
          ],
          [
            36.149837,
            -49.399764
          ],
          [
            28.693762,
            -49.935992
          ],
          [
            -22.639249,
            -49.962392
          ],
          [
            -31.68237,
            -49.804804
          ],
          [
            -37.790975,
            -49.171753
          ],
          [
            -40.991325,
            -48.021769
          ],
          [
            -42.852822,
            -47.100492
          ],
          [
            -45.108761,
            -45.504647
          ],
          [
            -46.544303,
            -43.908803
          ],
          [
            -47.635088,
            -42.231593
          ],
          [
            -48.629963,
            -39.653216
          ],
          [
            -49.162337,
            -36.7275
          ],
          [
            -49.525596,
            -32.20594
          ],
          [
            -49.630994,
            -26.620483
          ],
          [
            -49.598668,
            28.976913
          ],
          [
            -49.197927,
            36.424189
          ],
          [
            -48.713222,
            39.341105
          ],
          [
            -48.163966,
            41.078788
          ],
          [
            -46.429597,
            44.128638
          ],
          [
            -44.100632,
            46.520197
          ],
          [
            -41.780589,
            47.833287
          ],
          [
            -38.322924,
            48.860091
          ],
          [
            -35.663181,
            49.215928
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "center": [
    0.01029100500000002,
    -0.85826866,
    0.00041991500000004844
  ],
  "construction_scale": 53.932182771831265,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
