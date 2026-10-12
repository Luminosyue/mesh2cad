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
      "start": -2.879182444778588,
      "length": 4.537008716645869,
      "loops": [
        [
          [
            49.952501,
            -47.3847
          ],
          [
            49.969133,
            48.560968
          ],
          [
            49.864218,
            49.054264
          ],
          [
            49.546727,
            49.300908
          ],
          [
            49.522141,
            49.794203
          ],
          [
            49.321345,
            49.923576
          ],
          [
            -46.131027,
            49.971803
          ],
          [
            -49.830733,
            49.865544
          ],
          [
            -49.962462,
            47.654923
          ],
          [
            -49.988922,
            30.389638
          ],
          [
            -49.983033,
            -46.398113
          ],
          [
            -49.86714,
            -49.85117
          ],
          [
            -49.337439,
            -49.974143
          ],
          [
            49.0747,
            -49.967079
          ],
          [
            49.784567,
            -49.85117
          ]
        ],
        [
          [
            -47.671665,
            -45.26984
          ],
          [
            -47.610908,
            47.769192
          ],
          [
            47.34817,
            47.701349
          ],
          [
            47.66539,
            47.574378
          ],
          [
            47.711612,
            -44.797079
          ],
          [
            47.616041,
            -46.891404
          ],
          [
            47.032502,
            -47.631345
          ],
          [
            -47.052382,
            -47.631345
          ],
          [
            -47.610908,
            -47.057523
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.6577111045694903,
      "length": 1.2215865075068886,
      "loops": [
        [
          [
            49.843427,
            46.65444
          ],
          [
            49.817624,
            -46.151464
          ],
          [
            49.764838,
            -48.864581
          ],
          [
            49.567991,
            -49.80729
          ],
          [
            -49.337439,
            -49.906725
          ],
          [
            -49.830733,
            -49.752011
          ],
          [
            -49.897645,
            39.047451
          ],
          [
            -49.851689,
            49.300908
          ],
          [
            -49.718204,
            49.794203
          ],
          [
            -47.014267,
            49.794203
          ],
          [
            -46.377676,
            49.3869
          ],
          [
            -45.458239,
            49.257732
          ],
          [
            -38.829241,
            49.142886
          ],
          [
            -36.676914,
            49.300908
          ],
          [
            -37.487887,
            49.547554
          ],
          [
            -37.613226,
            49.794203
          ],
          [
            -33.058738,
            49.878489
          ],
          [
            49.210641,
            49.794203
          ],
          [
            49.253727,
            49.300908
          ],
          [
            49.719699,
            48.162614
          ]
        ],
        [
          [
            -45.637736,
            47.064735
          ],
          [
            42.661876,
            47.066346
          ],
          [
            46.114934,
            47.024702
          ],
          [
            47.000348,
            46.834437
          ],
          [
            47.130984,
            31.788972
          ],
          [
            47.11594,
            -45.658173
          ],
          [
            47.099281,
            -46.891404
          ],
          [
            46.854874,
            -47.228321
          ],
          [
            46.361583,
            -47.099922
          ],
          [
            -46.664197,
            -47.171008
          ],
          [
            -46.905757,
            -47.145433
          ],
          [
            -47.058383,
            -46.891404
          ],
          [
            -46.96975,
            46.735795
          ],
          [
            -46.624322,
            47.030314
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    8.044500000001231e-05,
    0.000284759999999995,
    -0.00010034500000000168
  ],
  "construction_scale": 100.02633193188106,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
