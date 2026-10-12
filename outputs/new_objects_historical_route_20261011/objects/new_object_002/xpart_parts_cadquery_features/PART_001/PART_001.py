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
      0.01065747165478766,
      -0.9999420120221079,
      0.0015462506608355316
    ],
    [
      -0.9941261775707457,
      -0.010428908572584078,
      0.10772363220093974
    ],
    [
      -0.10770125981856506,
      -0.0026852298157548074,
      -0.9941796760014414
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.38355865175445,
      "length": 100.88486221260027,
      "loops": [
        [
          [
            -2.447345,
            -3.470104
          ],
          [
            -3.667258,
            -3.28762
          ],
          [
            -4.27977,
            -2.951086
          ],
          [
            -4.647779,
            -2.364977
          ],
          [
            -4.754866,
            1.921843
          ],
          [
            -4.340198,
            2.842826
          ],
          [
            -3.735232,
            3.229771
          ],
          [
            -3.127502,
            3.352681
          ],
          [
            2.961568,
            3.44524
          ],
          [
            4.182491,
            3.166063
          ],
          [
            4.780198,
            2.638123
          ],
          [
            4.915626,
            -2.239321
          ],
          [
            4.596896,
            -2.878437
          ],
          [
            3.641885,
            -3.391849
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    0.1855061,
    -0.352804065,
    0.028213895000000003
  ],
  "construction_scale": 246.96399139053892,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
