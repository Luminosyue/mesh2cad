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
      "start": -3.7756360915668132,
      "length": 0.45780388502751873,
      "loops": [
        [
          [
            -47.144669,
            -9.415934
          ],
          [
            -47.161759,
            8.457448
          ],
          [
            -46.909515,
            9.375915
          ],
          [
            -32.994703,
            9.224237
          ],
          [
            -9.140739,
            9.342261
          ],
          [
            -2.751383,
            9.135561
          ],
          [
            1.371053,
            9.282332
          ],
          [
            27.069271,
            9.13876
          ],
          [
            40.555012,
            9.216267
          ],
          [
            46.843164,
            9.034348
          ],
          [
            47.008693,
            5.224219
          ],
          [
            47.05448,
            -7.19295
          ],
          [
            46.858653,
            -9.18078
          ],
          [
            46.518508,
            -9.461765
          ],
          [
            40.395678,
            -9.340114
          ],
          [
            30.315068,
            -9.481576
          ],
          [
            22.66454,
            -9.342466
          ],
          [
            6.393687,
            -9.548995
          ],
          [
            -1.439407,
            -9.430767
          ],
          [
            -7.521907,
            -9.549779
          ],
          [
            -9.140739,
            -9.442862
          ],
          [
            -11.128569,
            -9.545133
          ],
          [
            -46.909515,
            -9.463571
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.317983231982957,
      "length": 0.9154567446113752,
      "loops": [
        [
          [
            48.019509,
            -11.425547
          ],
          [
            -48.897345,
            -11.43433
          ],
          [
            -49.150567,
            -11.16861
          ],
          [
            -48.918274,
            -9.18078
          ],
          [
            -48.92649,
            8.709692
          ],
          [
            -49.117794,
            10.697524
          ],
          [
            -48.897345,
            11.003568
          ],
          [
            -46.909515,
            11.167195
          ],
          [
            44.530674,
            11.052159
          ],
          [
            46.518508,
            11.069658
          ],
          [
            47.11755,
            11.242837
          ],
          [
            48.506336,
            11.129176
          ],
          [
            48.78383,
            10.697524
          ],
          [
            48.73441,
            -5.205118
          ],
          [
            48.901185,
            -9.77206
          ],
          [
            48.831433,
            -11.16861
          ],
          [
            48.506336,
            -11.528085
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.4026775128152447,
      "length": 5.034332480866081,
      "loops": [
        [
          [
            44.530674,
            11.784926
          ],
          [
            -46.909515,
            11.948776
          ],
          [
            -48.897345,
            11.843749
          ],
          [
            -49.788685,
            10.697524
          ],
          [
            -49.381857,
            8.880574
          ],
          [
            -49.441199,
            -9.18078
          ],
          [
            -49.909949,
            -11.16861
          ],
          [
            -48.897345,
            -12.194275
          ],
          [
            44.369603,
            -12.099826
          ],
          [
            46.518508,
            -12.189231
          ],
          [
            48.352723,
            -12.567767
          ],
          [
            48.506336,
            -12.566712
          ],
          [
            49.883535,
            -11.16861
          ],
          [
            49.461486,
            -9.335776
          ],
          [
            49.360967,
            6.721864
          ],
          [
            49.427234,
            8.709692
          ],
          [
            49.833458,
            10.697524
          ],
          [
            48.506336,
            12.501016
          ],
          [
            46.664599,
            11.873664
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.631503942607173,
      "length": 0.6866303148194467,
      "loops": [
        [
          [
            48.767845,
            6.721864
          ],
          [
            48.772093,
            -10.658651
          ],
          [
            48.889522,
            -11.16861
          ],
          [
            48.506336,
            -11.557612
          ],
          [
            42.994876,
            -11.399038
          ],
          [
            -48.897345,
            -11.415787
          ],
          [
            -49.141374,
            -11.16861
          ],
          [
            -48.973957,
            -9.18078
          ],
          [
            -49.07321,
            10.697524
          ],
          [
            -48.897345,
            10.923679
          ],
          [
            -46.909515,
            11.100822
          ],
          [
            44.530674,
            11.003026
          ],
          [
            47.911467,
            11.07741
          ],
          [
            48.506336,
            11.28004
          ],
          [
            48.934988,
            10.697524
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 3.317983231982957,
      "length": 0.45780388502751873,
      "loops": [
        [
          [
            2.786241,
            9.178721
          ],
          [
            38.567186,
            9.006904
          ],
          [
            46.99487,
            9.186055
          ],
          [
            47.012656,
            -1.229458
          ],
          [
            46.792529,
            -9.18078
          ],
          [
            46.518508,
            -9.411125
          ],
          [
            28.628036,
            -9.269665
          ],
          [
            22.411453,
            -9.433868
          ],
          [
            2.786241,
            -9.511559
          ],
          [
            -5.165081,
            -9.369583
          ],
          [
            -45.247131,
            -9.506227
          ],
          [
            -47.126783,
            -9.398048
          ],
          [
            -47.220722,
            6.721864
          ],
          [
            -47.171536,
            8.709692
          ],
          [
            -46.909515,
            9.175024
          ],
          [
            -44.570568,
            9.060807
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.141848855,
    -0.423944255,
    0.3215267
  ],
  "construction_scale": 201.5384315247382,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
