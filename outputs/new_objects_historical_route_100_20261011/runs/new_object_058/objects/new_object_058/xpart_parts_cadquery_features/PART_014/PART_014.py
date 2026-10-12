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
      "start": -38.56740936636928,
      "length": 72.46152393015937,
      "loops": [
        [
          [
            2.92652,
            -41.67
          ],
          [
            2.977449,
            42.10262
          ],
          [
            3.24098,
            42.990736
          ],
          [
            4.171612,
            43.351507
          ],
          [
            4.473608,
            44.104696
          ],
          [
            4.443144,
            49.1175
          ],
          [
            4.171612,
            49.738513
          ],
          [
            3.614627,
            49.939481
          ],
          [
            0.272759,
            49.985169
          ],
          [
            -0.284218,
            49.878082
          ],
          [
            -0.508896,
            49.67448
          ],
          [
            -0.797028,
            49.1175
          ],
          [
            -0.817593,
            48.560523
          ],
          [
            -0.834766,
            44.104696
          ],
          [
            -0.643682,
            42.990736
          ],
          [
            -0.612277,
            -42.226981
          ],
          [
            -0.82286,
            -43.340936
          ],
          [
            -0.760969,
            -49.467701
          ],
          [
            -0.284218,
            -49.917287
          ],
          [
            2.500677,
            -49.925566
          ],
          [
            3.057651,
            -49.723061
          ],
          [
            3.268292,
            -49.467701
          ],
          [
            3.352164,
            -48.91072
          ],
          [
            3.433234,
            -43.340936
          ],
          [
            3.379815,
            -42.783957
          ],
          [
            3.033763,
            -42.226981
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 33.892571867415434,
      "length": 4.676380195328504,
      "loops": [
        [
          [
            -2.516471,
            48.533585
          ],
          [
            -3.704946,
            48.003545
          ],
          [
            -4.183071,
            46.155934
          ],
          [
            -4.277162,
            43.802602
          ],
          [
            -4.395281,
            3.057388
          ],
          [
            -4.154083,
            -42.255969
          ],
          [
            -3.916868,
            -43.340936
          ],
          [
            -3.626088,
            -43.562205
          ],
          [
            -1.398177,
            -43.903674
          ],
          [
            -1.069956,
            -44.285789
          ],
          [
            -0.889859,
            -45.399744
          ],
          [
            -0.841203,
            -49.486063
          ],
          [
            -0.284218,
            -49.962437
          ],
          [
            2.500677,
            -49.982425
          ],
          [
            3.166764,
            -49.713565
          ],
          [
            3.378495,
            -49.467701
          ],
          [
            3.46805,
            -48.91072
          ],
          [
            3.938604,
            -35.93111
          ],
          [
            3.499767,
            42.43376
          ],
          [
            3.530248,
            42.990736
          ],
          [
            4.326891,
            43.547715
          ],
          [
            4.457627,
            44.104696
          ],
          [
            4.370313,
            49.1175
          ],
          [
            4.155649,
            49.67448
          ],
          [
            3.614627,
            49.954282
          ],
          [
            -0.115113,
            49.967089
          ],
          [
            -0.64344,
            49.67448
          ],
          [
            -0.937682,
            48.948395
          ],
          [
            -1.398177,
            48.49505
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.47222996,
    -0.0004577199999999948,
    0.00038944500000000215
  ],
  "construction_scale": 225.87961474876428,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
