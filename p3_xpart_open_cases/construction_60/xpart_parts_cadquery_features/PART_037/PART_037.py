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
      -0.22797447673563254,
      0.9477519545611077,
      0.22314540233380387
    ],
    [
      0.06183447964451514,
      -0.21462517853763946,
      0.9747371593741456
    ],
    [
      0.9717016697959342,
      0.23601327370147435,
      -0.009674686170948243
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -9.9574637825135,
      "length": 17.824302100156977,
      "loops": [
        [
          [
            49.414016,
            19.077482
          ],
          [
            -43.59991,
            21.136408
          ],
          [
            -45.440645,
            20.974556
          ],
          [
            -46.12135,
            20.669036
          ],
          [
            -46.758025,
            19.855487
          ],
          [
            -46.898362,
            18.928312
          ],
          [
            -48.253995,
            -17.214762
          ],
          [
            -48.202665,
            -18.185814
          ],
          [
            -47.752188,
            -19.248243
          ],
          [
            -46.992365,
            -19.98457
          ],
          [
            -46.098471,
            -20.394058
          ],
          [
            -44.162981,
            -20.56072
          ],
          [
            16.730927,
            -21.780327
          ],
          [
            43.340812,
            -21.907077
          ],
          [
            44.341749,
            -21.843838
          ],
          [
            45.691415,
            -21.454165
          ],
          [
            46.474552,
            -20.674146
          ],
          [
            46.84444,
            -19.799525
          ],
          [
            49.606253,
            -4.976583
          ],
          [
            53.303963,
            13.256523
          ],
          [
            53.802996,
            16.020181
          ],
          [
            53.780574,
            16.984617
          ],
          [
            53.326011,
            18.047982
          ],
          [
            52.528239,
            18.663195
          ],
          [
            51.60009,
            18.921377
          ]
        ],
        [
          [
            17.409799,
            -6.345984
          ],
          [
            19.006286,
            -3.833563
          ],
          [
            19.47079,
            -2.021298
          ],
          [
            19.561656,
            -0.566759
          ],
          [
            19.37865,
            0.877694
          ],
          [
            19.10827,
            1.900076
          ],
          [
            18.069485,
            3.833524
          ],
          [
            16.904544,
            5.126796
          ],
          [
            16.060211,
            5.75507
          ],
          [
            15.182515,
            6.236046
          ],
          [
            13.320039,
            6.725131
          ],
          [
            10.584785,
            6.691648
          ],
          [
            9.269341,
            6.264796
          ],
          [
            8.143076,
            5.648162
          ],
          [
            6.984064,
            4.787224
          ],
          [
            6.187919,
            3.897433
          ],
          [
            5.314079,
            2.178879
          ],
          [
            4.746464,
            0.39022
          ],
          [
            4.508794,
            -1.128222
          ],
          [
            4.564351,
            -2.445988
          ],
          [
            4.960714,
            -4.04795
          ],
          [
            5.651241,
            -5.355398
          ],
          [
            6.98899,
            -6.838262
          ],
          [
            8.089779,
            -7.657467
          ],
          [
            8.971217,
            -8.121892
          ],
          [
            10.832783,
            -8.614958
          ],
          [
            12.796574,
            -8.656652
          ],
          [
            14.012867,
            -8.446229
          ],
          [
            15.603728,
            -7.851125
          ],
          [
            16.631507,
            -7.127111
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 5,
  "center": [
    0.26443733999999997,
    -0.68398552,
    0.27345801999999997
  ],
  "construction_scale": 189.60542844892183,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
