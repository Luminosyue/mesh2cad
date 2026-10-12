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
      "start": -50.0,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            -1.862803,
            7.361188
          ],
          [
            12.907807,
            7.361582
          ],
          [
            13.417141,
            7.313794
          ],
          [
            13.926474,
            7.024813
          ],
          [
            14.235737,
            6.044288
          ],
          [
            14.25833,
            -8.216993
          ],
          [
            14.240476,
            -8.726322
          ],
          [
            13.926474,
            -9.326022
          ],
          [
            13.417141,
            -9.656889
          ],
          [
            12.907807,
            -9.687319
          ],
          [
            0.174523,
            -9.671034
          ],
          [
            -1.862803,
            -9.602575
          ],
          [
            -2.482809,
            -9.235658
          ],
          [
            -2.773482,
            -8.726322
          ],
          [
            -2.806893,
            -8.216993
          ],
          [
            -2.705229,
            6.553615
          ],
          [
            -2.379159,
            7.093885
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -37.878787878787875,
      "length": 9.092909090909087,
      "loops": [
        [
          [
            -0.84414,
            8.912354
          ],
          [
            11.727411,
            9.100274
          ],
          [
            12.266776,
            8.590947
          ],
          [
            12.39848,
            7.53583
          ],
          [
            13.417141,
            7.311032
          ],
          [
            13.926474,
            6.955139
          ],
          [
            14.13546,
            6.553615
          ],
          [
            14.242061,
            5.534959
          ],
          [
            14.264149,
            -8.216993
          ],
          [
            14.239983,
            -8.726322
          ],
          [
            13.926474,
            -9.34242
          ],
          [
            13.417141,
            -9.672111
          ],
          [
            12.907807,
            -9.694182
          ],
          [
            -1.353471,
            -9.65855
          ],
          [
            -1.862803,
            -9.588186
          ],
          [
            -2.469712,
            -9.235658
          ],
          [
            -2.72945,
            -8.726322
          ],
          [
            -2.8638,
            -7.707663
          ],
          [
            -3.390797,
            -7.525996
          ],
          [
            -13.068095,
            -7.574225
          ],
          [
            -13.577424,
            -7.555949
          ],
          [
            -14.086758,
            -7.209472
          ],
          [
            -14.217969,
            -6.179669
          ],
          [
            -14.206544,
            1.969635
          ],
          [
            -14.086758,
            2.531956
          ],
          [
            -13.577424,
            2.937417
          ],
          [
            -13.068095,
            2.981093
          ],
          [
            -3.339631,
            2.9883
          ],
          [
            -2.804047,
            3.497629
          ],
          [
            -2.758879,
            6.553615
          ],
          [
            -2.568647,
            7.062953
          ],
          [
            -1.760353,
            7.57228
          ],
          [
            -1.3584,
            8.748408
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.78787878787879,
      "length": 60.608060606060604,
      "loops": [
        [
          [
            -2.80236,
            6.044288
          ],
          [
            -2.805201,
            -8.216993
          ],
          [
            -2.761331,
            -8.726322
          ],
          [
            -2.372134,
            -9.337192
          ],
          [
            -1.862803,
            -9.61316
          ],
          [
            -1.353471,
            -9.672245
          ],
          [
            11.926402,
            -9.697881
          ],
          [
            13.417141,
            -9.657552
          ],
          [
            14.013848,
            -9.235658
          ],
          [
            14.276826,
            -8.216993
          ],
          [
            14.259777,
            5.534959
          ],
          [
            14.137796,
            6.553615
          ],
          [
            13.816227,
            7.062953
          ],
          [
            13.417141,
            7.30025
          ],
          [
            12.435735,
            7.36121
          ],
          [
            -1.862803,
            7.315738
          ],
          [
            -2.372134,
            6.987268
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 31.818181818181813,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            14.153429,
            6.553615
          ],
          [
            14.254255,
            -8.726322
          ],
          [
            13.926474,
            -9.355489
          ],
          [
            13.417141,
            -9.662048
          ],
          [
            12.907807,
            -9.699175
          ],
          [
            -0.334807,
            -9.687479
          ],
          [
            -1.862803,
            -9.622263
          ],
          [
            -2.496949,
            -9.235658
          ],
          [
            -2.774798,
            -8.726322
          ],
          [
            -2.808728,
            -8.216993
          ],
          [
            -2.802099,
            6.044288
          ],
          [
            -2.69597,
            6.553615
          ],
          [
            -2.323344,
            7.062953
          ],
          [
            -1.862803,
            7.325102
          ],
          [
            -1.353471,
            7.381645
          ],
          [
            7.814493,
            7.473056
          ],
          [
            8.323827,
            8.004397
          ],
          [
            8.539654,
            9.100274
          ],
          [
            8.833156,
            9.526544
          ],
          [
            9.342488,
            9.681177
          ],
          [
            11.889147,
            9.571715
          ],
          [
            12.293179,
            9.100274
          ],
          [
            12.465969,
            7.57228
          ],
          [
            13.82482,
            7.062953
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -1.862803,
            7.322431
          ],
          [
            11.889147,
            7.407011
          ],
          [
            13.417141,
            7.308715
          ],
          [
            13.926474,
            6.9788
          ],
          [
            14.156211,
            6.553615
          ],
          [
            14.261202,
            5.534959
          ],
          [
            14.272281,
            -6.179669
          ],
          [
            14.250641,
            -8.726322
          ],
          [
            13.926474,
            -9.345129
          ],
          [
            13.417141,
            -9.661951
          ],
          [
            12.907807,
            -9.688244
          ],
          [
            -1.012369,
            -9.67842
          ],
          [
            -1.862803,
            -9.622361
          ],
          [
            -2.489086,
            -9.235658
          ],
          [
            -2.770084,
            -8.726322
          ],
          [
            -2.811775,
            -8.048764
          ],
          [
            -2.819043,
            4.516294
          ],
          [
            -2.693579,
            6.553615
          ],
          [
            -2.372134,
            7.020492
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.41886175000000003,
    -0.011278279999999988,
    0.16436504500000002
  ],
  "construction_scale": 206.55659375948738,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
