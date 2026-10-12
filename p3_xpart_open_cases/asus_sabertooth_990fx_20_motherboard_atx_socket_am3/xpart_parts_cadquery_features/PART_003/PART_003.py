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
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.0,
      "length": 21.21412121212121,
      "loops": [
        [
          [
            10.675215,
            37.316005
          ],
          [
            -10.671134,
            37.646735
          ],
          [
            -11.1734,
            37.71395
          ],
          [
            -11.50627,
            38.198028
          ],
          [
            -11.278058,
            38.700296
          ],
          [
            -10.893896,
            38.779442
          ],
          [
            7.941117,
            38.439952
          ],
          [
            11.177483,
            38.286835
          ],
          [
            11.720343,
            37.695764
          ],
          [
            11.905952,
            20.618682
          ],
          [
            11.63725,
            -37.142025
          ],
          [
            11.567756,
            -39.402226
          ],
          [
            11.177483,
            -39.874541
          ],
          [
            10.76612,
            -39.653359
          ],
          [
            10.620899,
            -39.15109
          ],
          [
            11.027792,
            7.280237
          ],
          [
            11.001634,
            36.942363
          ],
          [
            10.926348,
            37.202559
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.78787878787879,
      "length": 33.33533333333334,
      "loops": [
        [
          [
            10.936322,
            -12.782074
          ],
          [
            11.145098,
            10.394043
          ],
          [
            10.926348,
            37.236069
          ],
          [
            10.675215,
            37.503234
          ],
          [
            10.352248,
            37.532375
          ],
          [
            -5.39733,
            37.843901
          ],
          [
            -10.922267,
            37.792385
          ],
          [
            -11.423215,
            37.946896
          ],
          [
            -11.581839,
            38.198028
          ],
          [
            -11.630618,
            38.449164
          ],
          [
            -11.424534,
            38.743945
          ],
          [
            -10.671134,
            38.898305
          ],
          [
            -7.980498,
            38.929944
          ],
          [
            10.172948,
            38.558406
          ],
          [
            11.177483,
            38.39322
          ],
          [
            11.731651,
            37.695764
          ],
          [
            11.908801,
            9.066542
          ],
          [
            11.697944,
            -19.993111
          ],
          [
            11.403668,
            -38.648826
          ],
          [
            11.265717,
            -39.402226
          ],
          [
            10.926348,
            -39.638015
          ],
          [
            10.521627,
            -39.402226
          ],
          [
            10.457546,
            -39.079257
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            10.833919,
            6.425389
          ],
          [
            10.274237,
            -28.603485
          ],
          [
            9.912528,
            -37.64429
          ],
          [
            10.081236,
            -38.39769
          ],
          [
            10.424081,
            -38.48317
          ],
          [
            10.801992,
            -38.146558
          ],
          [
            10.932875,
            -36.509938
          ],
          [
            11.445293,
            -11.656224
          ],
          [
            11.628923,
            6.927656
          ],
          [
            11.600976,
            38.449164
          ],
          [
            11.187357,
            38.951432
          ],
          [
            10.675215,
            39.170892
          ],
          [
            -8.159798,
            39.551097
          ],
          [
            -11.1734,
            39.443521
          ],
          [
            -11.675667,
            39.228611
          ],
          [
            -11.832351,
            38.951432
          ],
          [
            -11.675667,
            38.684834
          ],
          [
            -11.424534,
            38.419435
          ],
          [
            -10.922267,
            38.293849
          ],
          [
            10.302766,
            38.121706
          ],
          [
            10.830075,
            37.946896
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.010760574999999994,
    0.012289025000000009,
    0.009357895000000005
  ],
  "construction_scale": 50.92291390629464,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
