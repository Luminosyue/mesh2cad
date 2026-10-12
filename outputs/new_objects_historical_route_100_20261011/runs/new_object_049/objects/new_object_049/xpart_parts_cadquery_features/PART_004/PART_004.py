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
      "length": 15.153515151515156,
      "loops": [
        [
          [
            -39.868345,
            43.208056
          ],
          [
            -39.844386,
            -42.345173
          ],
          [
            -39.751711,
            -43.533415
          ],
          [
            -39.500086,
            -43.837138
          ],
          [
            -38.905964,
            -44.017725
          ],
          [
            -34.153007,
            -44.024716
          ],
          [
            36.547231,
            -44.038435
          ],
          [
            37.73547,
            -43.89615
          ],
          [
            38.049916,
            -43.533415
          ],
          [
            38.114753,
            -42.939295
          ],
          [
            37.995429,
            -0.756799
          ],
          [
            38.000578,
            34.151601
          ],
          [
            38.124034,
            41.875155
          ],
          [
            38.119753,
            43.208056
          ],
          [
            37.857584,
            43.802173
          ],
          [
            37.14135,
            44.015661
          ],
          [
            -38.905964,
            43.98437
          ],
          [
            -39.500086,
            43.860484
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -34.848484848484844,
      "length": 84.85048484848484,
      "loops": [
        [
          [
            37.14135,
            43.995271
          ],
          [
            -38.905964,
            43.985809
          ],
          [
            -39.582483,
            43.802173
          ],
          [
            -39.884743,
            43.208056
          ],
          [
            -39.891913,
            42.613937
          ],
          [
            -39.756658,
            38.455097
          ],
          [
            -39.738084,
            5.684778
          ],
          [
            -39.741826,
            -38.186336
          ],
          [
            -39.893656,
            -42.939295
          ],
          [
            -39.811007,
            -43.533415
          ],
          [
            -39.500086,
            -43.898459
          ],
          [
            -38.905964,
            -44.0374
          ],
          [
            -34.153007,
            -44.048107
          ],
          [
            35.358992,
            -44.055609
          ],
          [
            37.14135,
            -43.980064
          ],
          [
            37.73547,
            -43.812276
          ],
          [
            38.029041,
            -43.533415
          ],
          [
            38.15931,
            -42.939295
          ],
          [
            38.038868,
            -31.651019
          ],
          [
            38.122004,
            43.208056
          ],
          [
            37.824738,
            43.802173
          ]
        ],
        [
          [
            -35.332395,
            -38.186336
          ],
          [
            -35.394066,
            37.266858
          ],
          [
            -35.341246,
            38.040563
          ],
          [
            -35.041061,
            38.455097
          ],
          [
            11.000087,
            38.570951
          ],
          [
            33.576633,
            38.564335
          ],
          [
            33.895719,
            38.455097
          ],
          [
            34.169181,
            37.860978
          ],
          [
            34.097532,
            -38.186336
          ],
          [
            33.576633,
            -38.486306
          ],
          [
            -9.700361,
            -38.518936
          ],
          [
            -34.653388,
            -38.503917
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.0006751799999999974,
    -0.24744412500000001,
    0.0011960849999999995
  ],
  "construction_scale": 240.94198485645893,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
