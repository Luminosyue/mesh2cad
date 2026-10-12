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
      0.7894975295524147,
      0.20358772680577444,
      -0.5790040486254753
    ],
    [
      -0.561811152855306,
      -0.14010039877372352,
      -0.815315955192118
    ],
    [
      -0.24710702005007137,
      0.9689808644950121,
      0.0037689367827802535
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -6.541545459288716,
      "length": 13.911852669919895,
      "loops": [
        [
          [
            -15.248186,
            17.88491
          ],
          [
            -48.256416,
            17.819776
          ],
          [
            -49.612615,
            17.426167
          ],
          [
            -50.190366,
            16.856125
          ],
          [
            -50.491151,
            16.089399
          ],
          [
            -50.635728,
            -8.316278
          ],
          [
            -50.51547,
            -14.983555
          ],
          [
            -50.193404,
            -16.497103
          ],
          [
            -49.742338,
            -17.172863
          ],
          [
            -49.067042,
            -17.646575
          ],
          [
            -47.762775,
            -17.869205
          ],
          [
            -21.873631,
            -17.845002
          ],
          [
            -10.835316,
            -18.090957
          ],
          [
            4.211313,
            -17.856385
          ],
          [
            25.294324,
            -18.12367
          ],
          [
            47.931752,
            -17.914899
          ],
          [
            49.48177,
            -17.654596
          ],
          [
            50.218938,
            -17.197769
          ],
          [
            50.615944,
            -16.499373
          ],
          [
            50.768352,
            14.763076
          ],
          [
            50.675708,
            15.809202
          ],
          [
            50.443717,
            16.313873
          ],
          [
            49.49699,
            17.251858
          ],
          [
            47.85416,
            17.543256
          ],
          [
            19.320603,
            17.776948
          ],
          [
            10.33392,
            17.640147
          ],
          [
            0.373115,
            17.220362
          ]
        ],
        [
          [
            -10.798085,
            -6.626703
          ],
          [
            -2.597238,
            -7.828679
          ],
          [
            0.245212,
            -8.102326
          ],
          [
            2.327496,
            -8.021526
          ],
          [
            3.730084,
            -7.711301
          ],
          [
            4.572357,
            -7.329111
          ],
          [
            5.175141,
            -6.776852
          ],
          [
            5.401107,
            -5.956988
          ],
          [
            5.36404,
            -5.207315
          ],
          [
            4.850569,
            -3.053236
          ],
          [
            3.834765,
            -0.664829
          ],
          [
            2.621905,
            1.035341
          ],
          [
            0.877574,
            2.745128
          ],
          [
            -0.603959,
            3.508548
          ],
          [
            -4.678387,
            4.896307
          ],
          [
            -6.459731,
            5.238409
          ],
          [
            -8.784189,
            5.254288
          ],
          [
            -11.080964,
            4.767569
          ],
          [
            -12.575436,
            3.868213
          ],
          [
            -14.14282,
            2.040305
          ],
          [
            -15.021339,
            -0.276807
          ],
          [
            -15.170899,
            -2.73509
          ],
          [
            -14.931052,
            -3.820727
          ],
          [
            -14.486403,
            -4.618562
          ],
          [
            -12.871166,
            -6.081334
          ]
        ],
        {
          "center": [
            -32.55252702512585,
            0.1786661335880808
          ],
          "radius": 6.6294847461270106
        },
        {
          "center": [
            32.79986803974048,
            -0.3939944563891231
          ],
          "radius": 6.472389466646297
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    0.12916369500000002,
    0.75989928,
    0.206310975
  ],
  "construction_scale": 162.07219282169618,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
