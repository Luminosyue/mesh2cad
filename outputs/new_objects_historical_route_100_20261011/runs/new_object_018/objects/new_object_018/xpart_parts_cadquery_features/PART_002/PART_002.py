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
      "start": -10.434204530260404,
      "length": 19.60407436442803,
      "loops": [
        [
          [
            -26.657613,
            -49.835754
          ],
          [
            26.012166,
            -49.822041
          ],
          [
            27.185757,
            -49.665366
          ],
          [
            27.576954,
            -49.302677
          ],
          [
            27.768034,
            -48.697545
          ],
          [
            28.200168,
            -43.362626
          ],
          [
            28.249947,
            -35.788036
          ],
          [
            28.229861,
            -21.31374
          ],
          [
            27.873632,
            -10.502061
          ],
          [
            28.001509,
            2.798644
          ],
          [
            29.019557,
            15.849994
          ],
          [
            28.511799,
            26.270476
          ],
          [
            28.705276,
            41.66901
          ],
          [
            28.556108,
            46.221533
          ],
          [
            28.366166,
            47.536968
          ],
          [
            27.968151,
            47.831872
          ],
          [
            26.936402,
            47.882616
          ],
          [
            -27.973046,
            47.875671
          ],
          [
            -28.547486,
            47.536968
          ],
          [
            -28.740207,
            46.754572
          ],
          [
            -29.493757,
            6.070065
          ],
          [
            -29.257491,
            -3.069313
          ],
          [
            -29.494114,
            -37.744023
          ],
          [
            -29.263879,
            -45.567966
          ],
          [
            -28.834726,
            -49.088741
          ],
          [
            -28.505912,
            -49.479935
          ],
          [
            -27.973046,
            -49.76197
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 9.169452465986415,
      "length": 1.265169432455199,
      "loops": [
        [
          [
            -20.540298,
            49.740961
          ],
          [
            13.493857,
            49.591781
          ],
          [
            21.317798,
            49.389859
          ],
          [
            26.79456,
            48.935918
          ],
          [
            27.772627,
            48.710559
          ],
          [
            28.1908,
            48.319362
          ],
          [
            28.374825,
            41.277812
          ],
          [
            28.196233,
            -6.448247
          ],
          [
            27.855616,
            -28.355289
          ],
          [
            27.941404,
            -44.785571
          ],
          [
            27.892552,
            -48.306343
          ],
          [
            27.747009,
            -49.088741
          ],
          [
            27.529126,
            -49.479935
          ],
          [
            26.79456,
            -49.735808
          ],
          [
            -27.973046,
            -49.771854
          ],
          [
            -28.755442,
            -49.211484
          ],
          [
            -28.980705,
            -48.306343
          ],
          [
            -29.266935,
            -36.176802
          ],
          [
            -29.210129,
            -6.057048
          ],
          [
            -29.450836,
            11.940452
          ],
          [
            -29.233752,
            20.155593
          ],
          [
            -29.077269,
            38.541861
          ],
          [
            -28.85089,
            46.363376
          ],
          [
            -28.57146,
            49.492953
          ],
          [
            -28.364248,
            49.893474
          ],
          [
            -27.973046,
            49.998231
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.16401807,
    -0.141177905,
    -0.31191084
  ],
  "construction_scale": 158.6478935018267,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
