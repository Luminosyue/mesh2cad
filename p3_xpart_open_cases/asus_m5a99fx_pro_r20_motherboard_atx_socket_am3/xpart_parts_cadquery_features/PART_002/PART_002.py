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
      -0.012377652042007727,
      -0.999865075747696,
      0.010799260621967784
    ],
    [
      0.9998396587575202,
      -0.012236126953610682,
      0.013074171974584485
    ],
    [
      -0.01294026682773079,
      0.010959356606540254,
      0.999856210660912
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -49.871483192444124,
      "length": 99.75842709163226,
      "loops": [
        [
          [
            12.810926,
            2.240282
          ],
          [
            13.496967,
            0.437484
          ],
          [
            13.408596,
            -0.825285
          ],
          [
            12.856623,
            -1.493813
          ],
          [
            11.911618,
            -1.593926
          ],
          [
            -2.391921,
            -1.690495
          ],
          [
            -12.691907,
            -1.467348
          ],
          [
            -13.519559,
            -0.843229
          ],
          [
            -13.779956,
            0.730638
          ],
          [
            -13.52808,
            1.995431
          ],
          [
            -13.243755,
            2.314367
          ],
          [
            -12.739498,
            2.421528
          ],
          [
            -12.420428,
            2.324559
          ],
          [
            -12.101607,
            1.843665
          ],
          [
            -12.065684,
            0.121028
          ],
          [
            -11.444464,
            -0.307258
          ],
          [
            1.801452,
            -0.200917
          ],
          [
            9.117225,
            -0.240058
          ],
          [
            10.635408,
            -0.403263
          ],
          [
            12.145369,
            -0.210086
          ],
          [
            12.198741,
            0.105992
          ],
          [
            11.622828,
            1.360536
          ],
          [
            11.865459,
            2.177899
          ],
          [
            12.483986,
            2.382397
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.95603276,
    0.0034689100000000056,
    -0.007494759999999989
  ],
  "construction_scale": 63.94776623674072,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
