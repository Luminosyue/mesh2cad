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
      "start": -28.92520246878847,
      "length": 17.53158274675843,
      "loops": [
        [
          [
            47.876176,
            -45.058224
          ],
          [
            47.848526,
            45.281076
          ],
          [
            47.683048,
            45.908432
          ],
          [
            47.325927,
            46.187718
          ],
          [
            -48.03222,
            46.230853
          ],
          [
            -49.286935,
            46.218765
          ],
          [
            -49.795012,
            45.908432
          ],
          [
            -49.963909,
            44.760395
          ],
          [
            -49.945303,
            -44.430865
          ],
          [
            -49.917746,
            -45.68558
          ],
          [
            -49.286935,
            -46.232285
          ],
          [
            47.325927,
            -46.173384
          ],
          [
            47.828395,
            -45.68558
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -11.39477673012879,
      "length": 40.32113620701601,
      "loops": [
        [
          [
            -49.538561,
            -37.529948
          ],
          [
            -49.484983,
            -23.100754
          ],
          [
            -49.630163,
            -17.454548
          ],
          [
            -49.746872,
            17.761696
          ],
          [
            -49.647594,
            24.035257
          ],
          [
            -49.756688,
            37.837095
          ],
          [
            -49.969952,
            43.399008
          ],
          [
            -49.961913,
            45.281076
          ],
          [
            -49.691707,
            45.908432
          ],
          [
            -49.286935,
            46.094551
          ],
          [
            42.307078,
            46.185466
          ],
          [
            46.698571,
            46.157935
          ],
          [
            47.529727,
            45.908432
          ],
          [
            47.748397,
            45.281076
          ],
          [
            47.595355,
            0.195721
          ],
          [
            47.700566,
            -45.058224
          ],
          [
            47.564228,
            -45.68558
          ],
          [
            47.325927,
            -45.914091
          ],
          [
            46.614276,
            -46.064609
          ],
          [
            -49.286935,
            -46.040931
          ],
          [
            -49.779733,
            -45.68558
          ],
          [
            -49.880367,
            -45.058224
          ]
        ],
        [
          [
            42.676782,
            40.889581
          ],
          [
            42.660394,
            -40.666728
          ],
          [
            42.576264,
            -41.294087
          ],
          [
            42.307078,
            -41.561039
          ],
          [
            -27.413759,
            -41.684655
          ],
          [
            -44.895436,
            -41.661571
          ],
          [
            -45.522793,
            -41.544961
          ],
          [
            -45.757459,
            -41.294087
          ],
          [
            -45.839697,
            -40.666728
          ],
          [
            -45.965224,
            -36.902591
          ],
          [
            -46.053486,
            -24.898529
          ],
          [
            -45.90439,
            18.304757
          ],
          [
            -46.070284,
            25.205677
          ],
          [
            -46.012197,
            32.733951
          ],
          [
            -46.36348,
            38.464451
          ],
          [
            -46.024758,
            40.889581
          ],
          [
            -45.774899,
            41.516939
          ],
          [
            -44.895436,
            41.703343
          ],
          [
            -37.994521,
            41.737629
          ],
          [
            42.307078,
            41.628402
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0004379600000000011,
    0.167046905,
    -0.030667625000000004
  ],
  "construction_scale": 254.4209002495284,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
