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
      -0.0077776897242173345,
      -0.9999696162906453,
      0.0005234864782752399
    ],
    [
      -0.9964328363677831,
      0.0077061873419346375,
      -0.08403699949846921
    ],
    [
      0.08403041205782887,
      -0.001175232823800848,
      -0.9964624973761937
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.1364057665582,
      "length": 100.11778699274436,
      "loops": [
        [
          [
            -3.446497,
            -3.464912
          ],
          [
            3.820046,
            -3.431074
          ],
          [
            4.428173,
            -3.092887
          ],
          [
            4.75903,
            -2.580916
          ],
          [
            4.866417,
            1.671951
          ],
          [
            4.557599,
            2.889703
          ],
          [
            3.872152,
            3.330365
          ],
          [
            2.662208,
            3.473569
          ],
          [
            -2.787579,
            3.462752
          ],
          [
            -3.39343,
            3.421141
          ],
          [
            -4.102302,
            3.084626
          ],
          [
            -4.647221,
            2.35388
          ],
          [
            -4.749433,
            1.747008
          ],
          [
            -4.72352,
            -1.899232
          ],
          [
            -4.651499,
            -2.507462
          ],
          [
            -4.227525,
            -3.118446
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.18043722499999998,
    -0.351743885,
    0.026675119999999997
  ],
  "construction_scale": 245.5590884414453,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
