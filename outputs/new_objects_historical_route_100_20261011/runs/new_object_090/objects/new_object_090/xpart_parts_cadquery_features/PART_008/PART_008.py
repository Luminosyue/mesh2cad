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
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -0.8123817542984277,
      "length": 1.526325488194488,
      "loops": [
        [
          [
            -46.675281,
            1.278655
          ],
          [
            47.04004,
            1.245539
          ],
          [
            47.243237,
            1.076898
          ],
          [
            47.267917,
            0.751523
          ],
          [
            47.413735,
            -4.035
          ],
          [
            47.926388,
            -4.277073
          ],
          [
            48.951701,
            -4.163649
          ],
          [
            49.464353,
            -3.570846
          ],
          [
            49.769239,
            -2.837064
          ],
          [
            49.904501,
            -2.068081
          ],
          [
            49.881555,
            3.827455
          ],
          [
            49.720683,
            4.182479
          ],
          [
            49.136791,
            4.255306
          ],
          [
            -49.478099,
            4.241286
          ],
          [
            -49.767551,
            4.08378
          ],
          [
            -49.865798,
            3.571128
          ],
          [
            -49.921095,
            -2.324409
          ],
          [
            -49.578039,
            -3.606047
          ],
          [
            -49.221774,
            -4.035196
          ],
          [
            -48.709117,
            -4.257449
          ],
          [
            -47.572866,
            -4.118703
          ],
          [
            -47.389544,
            -3.606047
          ],
          [
            -47.283883,
            1.00785
          ],
          [
            -47.171152,
            1.178253
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7139112386258883,
      "length": 0.09850301094270844,
      "loops": [
        [
          [
            -49.478099,
            3.928567
          ],
          [
            49.464353,
            3.937692
          ],
          [
            49.691327,
            3.827455
          ],
          [
            49.621129,
            -2.068081
          ],
          [
            49.493678,
            -3.064067
          ],
          [
            49.208027,
            -3.570356
          ],
          [
            48.69537,
            -3.914764
          ],
          [
            47.649518,
            -3.862374
          ],
          [
            47.539384,
            1.00785
          ],
          [
            47.413735,
            1.342042
          ],
          [
            47.157406,
            1.502992
          ],
          [
            46.644752,
            1.51308
          ],
          [
            -46.895888,
            1.501567
          ],
          [
            -47.351952,
            1.444976
          ],
          [
            -47.582735,
            1.163105
          ],
          [
            -47.683808,
            -3.834059
          ],
          [
            -48.965447,
            -3.836357
          ],
          [
            -49.478099,
            -3.104113
          ],
          [
            -49.742877,
            -2.324409
          ],
          [
            -49.73443,
            2.197793
          ],
          [
            -49.651772,
            3.571128
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    6.611999999997509e-05,
    0.29113476,
    -0.23957045999999999
  ],
  "construction_scale": 103.95226511985696,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
