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
      "start": -17.401748635946664,
      "length": 34.80349727189333,
      "loops": [
        [
          [
            -32.495159,
            37.24843
          ],
          [
            -32.546731,
            -33.637665
          ],
          [
            -32.437884,
            -36.027087
          ],
          [
            -31.993381,
            -37.221795
          ],
          [
            -31.553147,
            -37.77326
          ],
          [
            -29.960201,
            -39.025466
          ],
          [
            -24.783831,
            -40.953193
          ],
          [
            -20.801631,
            -43.094704
          ],
          [
            -19.748322,
            -43.991815
          ],
          [
            -16.627593,
            -47.974179
          ],
          [
            -14.428978,
            -48.961866
          ],
          [
            -12.437795,
            -49.264636
          ],
          [
            -6.46511,
            -49.583401
          ],
          [
            6.677557,
            -49.998247
          ],
          [
            9.863449,
            -49.80606
          ],
          [
            14.24405,
            -48.769358
          ],
          [
            15.836997,
            -47.67757
          ],
          [
            16.272135,
            -47.177708
          ],
          [
            16.429769,
            -46.381236
          ],
          [
            16.179145,
            -45.186524
          ],
          [
            16.273623,
            -44.78829
          ],
          [
            16.526922,
            -44.390052
          ],
          [
            17.608125,
            -43.593578
          ],
          [
            22.820064,
            -40.805922
          ],
          [
            25.792909,
            -39.742592
          ],
          [
            29.377036,
            -39.109372
          ],
          [
            30.571745,
            -38.444961
          ],
          [
            31.36822,
            -37.735532
          ],
          [
            32.322501,
            -36.027087
          ],
          [
            32.614307,
            -33.636797
          ],
          [
            32.618922,
            36.850193
          ],
          [
            32.176017,
            40.832558
          ],
          [
            32.257654,
            43.221976
          ],
          [
            32.053335,
            44.814922
          ],
          [
            31.387188,
            46.806106
          ],
          [
            30.339449,
            48.797289
          ],
          [
            28.978802,
            49.607032
          ],
          [
            -4.473065,
            49.510628
          ],
          [
            -6.066011,
            48.981046
          ],
          [
            -8.057194,
            46.428469
          ],
          [
            -8.754471,
            46.009634
          ],
          [
            -13.632504,
            44.365586
          ],
          [
            -18.013106,
            42.583985
          ],
          [
            -21.505443,
            41.629206
          ],
          [
            -24.783995,
            40.983482
          ],
          [
            -30.358438,
            40.356684
          ],
          [
            -31.736411,
            39.239611
          ]
        ],
        [
          [
            31.367725,
            41.737401
          ],
          [
            31.386886,
            41.230795
          ],
          [
            30.969983,
            40.999728
          ],
          [
            26.165138,
            42.823741
          ],
          [
            27.385856,
            43.50255
          ],
          [
            28.978802,
            43.454207
          ],
          [
            30.435474,
            42.823741
          ],
          [
            30.971628,
            42.425504
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -17.401748635946664,
      "length": 34.80349727189333,
      "loops": [
        [
          [
            -21.995471,
            48.791045
          ],
          [
            -20.800762,
            48.199214
          ],
          [
            -19.207816,
            48.059804
          ],
          [
            -15.89568,
            49.195523
          ],
          [
            -22.452674,
            49.593761
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "center": [
    0.0046018099999999285,
    -0.0098848,
    0.0022900849999999973
  ],
  "construction_scale": 40.37566063766266,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
