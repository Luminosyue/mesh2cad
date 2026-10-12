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
      "length": 21.21412121212121,
      "loops": [
        [
          [
            -20.27339,
            -29.596135
          ],
          [
            -20.414477,
            41.102587
          ],
          [
            -20.336743,
            41.638184
          ],
          [
            -19.961483,
            42.034704
          ],
          [
            20.208245,
            42.073287
          ],
          [
            20.743841,
            41.941086
          ],
          [
            20.896119,
            41.638184
          ],
          [
            20.743841,
            40.945662
          ],
          [
            20.208245,
            40.738885
          ],
          [
            17.530263,
            40.49119
          ],
          [
            -17.702037,
            40.66617
          ],
          [
            -19.46686,
            40.566989
          ],
          [
            -19.668783,
            40.031396
          ],
          [
            -19.680409,
            38.424607
          ],
          [
            -19.619975,
            -29.596135
          ],
          [
            -19.466343,
            -40.308061
          ],
          [
            -19.597888,
            -41.262194
          ],
          [
            -19.961483,
            -41.492896
          ],
          [
            -20.199705,
            -40.308061
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.78787878787879,
      "length": 78.78987878787878,
      "loops": [
        [
          [
            -20.149756,
            11.644786
          ],
          [
            -20.125754,
            -23.704575
          ],
          [
            -19.795871,
            -35.487696
          ],
          [
            -19.802716,
            -36.023293
          ],
          [
            -19.961483,
            -36.262581
          ],
          [
            -20.389914,
            -36.023293
          ],
          [
            -20.497081,
            -33.257065
          ],
          [
            -20.846361,
            -12.785847
          ],
          [
            -20.804966,
            18.071942
          ],
          [
            -20.366197,
            41.638184
          ],
          [
            -19.961483,
            42.148528
          ],
          [
            -19.425888,
            42.180539
          ],
          [
            -1.42241,
            41.999997
          ],
          [
            20.208245,
            42.17274
          ],
          [
            20.743841,
            42.014306
          ],
          [
            20.880346,
            41.638184
          ],
          [
            20.743841,
            41.038293
          ],
          [
            16.994667,
            40.569033
          ],
          [
            -19.425888,
            40.740012
          ],
          [
            -19.599981,
            40.566989
          ],
          [
            -19.682372,
            40.031396
          ],
          [
            -19.861366,
            33.275441
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.00995415999999999,
    -0.046656875000000014,
    0.012410770000000015
  ],
  "construction_scale": 54.30204886951986,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
