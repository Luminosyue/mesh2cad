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
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            -1.302818,
            39.451399
          ],
          [
            -1.324293,
            -39.53144
          ],
          [
            -0.945903,
            -40.040721
          ],
          [
            0.771115,
            -40.062029
          ],
          [
            1.22691,
            -39.776727
          ],
          [
            1.301133,
            -39.402932
          ],
          [
            1.308427,
            -9.477756
          ],
          [
            1.300704,
            38.844043
          ],
          [
            1.252103,
            39.451399
          ],
          [
            0.771115,
            39.78434
          ],
          [
            -0.945903,
            39.808575
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            -1.283479,
            49.508222
          ],
          [
            -1.230128,
            42.394858
          ],
          [
            -0.978913,
            41.658994
          ],
          [
            0.280538,
            42.583665
          ],
          [
            0.771115,
            42.55251
          ],
          [
            1.016403,
            42.234162
          ],
          [
            1.229436,
            43.130723
          ],
          [
            1.269654,
            49.262931
          ],
          [
            0.771115,
            49.863762
          ],
          [
            -0.700615,
            49.957519
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            1.104869,
            -42.474899
          ],
          [
            1.251819,
            -49.588262
          ],
          [
            0.525826,
            -49.959679
          ],
          [
            -1.006288,
            -49.833549
          ],
          [
            -1.309554,
            -49.342971
          ],
          [
            -1.327346,
            -48.723887
          ],
          [
            -1.06704,
            -43.81812
          ],
          [
            -0.945903,
            -43.17444
          ],
          [
            -0.358824,
            -42.474899
          ],
          [
            0.03525,
            -42.420245
          ],
          [
            0.525826,
            -42.742518
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "center": [
    0.0008046250000000033,
    -0.06176341499999999,
    -0.0007087149999999987
  ],
  "construction_scale": 49.73767133564632,
  "expected_solid_count": 3
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
