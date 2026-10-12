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
      "start": -21.737437490140053,
      "length": 2.63571040539537,
      "loops": [
        [
          [
            -28.480004,
            -44.259551
          ],
          [
            -28.226952,
            -46.060249
          ],
          [
            -27.944403,
            -46.820621
          ],
          [
            -23.33951,
            -47.14175
          ],
          [
            -17.308034,
            -46.950392
          ],
          [
            19.789232,
            -47.045406
          ],
          [
            27.490793,
            -47.379908
          ],
          [
            28.045692,
            -47.334055
          ],
          [
            28.517667,
            -46.965997
          ],
          [
            28.71683,
            -44.579061
          ],
          [
            28.843136,
            -39.119059
          ],
          [
            29.049667,
            -18.068123
          ],
          [
            29.033413,
            10.684371
          ],
          [
            28.835116,
            17.872494
          ],
          [
            29.071326,
            29.085142
          ],
          [
            29.020745,
            34.81593
          ],
          [
            28.602844,
            44.571242
          ],
          [
            28.517667,
            45.474349
          ],
          [
            28.004231,
            46.504765
          ],
          [
            27.490793,
            46.677174
          ],
          [
            24.008742,
            46.737002
          ],
          [
            -23.304686,
            46.659817
          ],
          [
            -24.867724,
            46.624992
          ],
          [
            -26.420133,
            46.372499
          ],
          [
            -27.07515,
            46.111554
          ],
          [
            -27.447011,
            45.55276
          ],
          [
            -27.966309,
            39.436864
          ],
          [
            -28.139678,
            6.203199
          ],
          [
            -28.473884,
            -9.295901
          ],
          [
            -28.620771,
            -28.483759
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.10259658224429,
      "length": 40.84090356988395,
      "loops": [
        [
          [
            22.563838,
            49.832168
          ],
          [
            27.308791,
            49.705615
          ],
          [
            28.21165,
            49.55844
          ],
          [
            28.719025,
            49.192177
          ],
          [
            28.956459,
            48.678738
          ],
          [
            29.128965,
            47.138427
          ],
          [
            29.393521,
            25.880074
          ],
          [
            29.212946,
            3.496248
          ],
          [
            29.247463,
            -44.766871
          ],
          [
            29.212938,
            -48.360932
          ],
          [
            28.983305,
            -49.387805
          ],
          [
            28.517667,
            -49.777147
          ],
          [
            28.004231,
            -49.892575
          ],
          [
            25.95048,
            -49.976127
          ],
          [
            -28.473884,
            -49.793687
          ],
          [
            -29.051393,
            -49.462115
          ],
          [
            -29.353817,
            -48.874367
          ],
          [
            -29.517684,
            -43.947413
          ],
          [
            -28.5829,
            -2.665001
          ],
          [
            -28.35934,
            47.138427
          ],
          [
            -27.963914,
            49.192177
          ],
          [
            -27.292776,
            49.705615
          ],
          [
            -25.185841,
            49.857962
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0018790399999999985,
    -0.006644425000000009,
    -0.25193421
  ],
  "construction_scale": 52.055436499566746,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
