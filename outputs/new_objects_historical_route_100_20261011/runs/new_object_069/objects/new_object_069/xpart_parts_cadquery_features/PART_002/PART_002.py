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
      "length": 66.66866666666667,
      "loops": [
        [
          [
            13.562182,
            0.203477
          ],
          [
            -13.324537,
            -2.205704
          ],
          [
            -13.943713,
            -1.959804
          ],
          [
            -14.256315,
            -1.219802
          ],
          [
            -14.14814,
            -0.726468
          ],
          [
            -13.817871,
            -0.448203
          ],
          [
            -12.584534,
            -0.314454
          ],
          [
            -11.844533,
            -0.003267
          ],
          [
            -8.144527,
            0.401057
          ],
          [
            -7.404525,
            0.278744
          ],
          [
            -6.664524,
            0.674322
          ],
          [
            -4.197853,
            0.929509
          ],
          [
            -3.704518,
            0.940313
          ],
          [
            -2.964516,
            0.682514
          ],
          [
            -2.471182,
            1.028006
          ],
          [
            0.242156,
            1.346764
          ],
          [
            0.73549,
            1.271491
          ],
          [
            0.982157,
            1.054802
          ],
          [
            1.722159,
            1.454547
          ],
          [
            4.188831,
            1.722673
          ],
          [
            4.682165,
            1.729694
          ],
          [
            5.422166,
            1.40988
          ],
          [
            6.162168,
            1.689808
          ],
          [
            8.135504,
            1.898423
          ],
          [
            9.615507,
            1.74083
          ],
          [
            10.238752,
            2.114133
          ],
          [
            11.835511,
            2.264871
          ],
          [
            12.82218,
            1.95894
          ],
          [
            13.808849,
            1.96047
          ],
          [
            14.113173,
            1.740203
          ],
          [
            14.29781,
            1.246869
          ],
          [
            14.157843,
            0.506867
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 16.66666666666667,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            13.562182,
            0.112764
          ],
          [
            -13.571204,
            -2.282636
          ],
          [
            -14.08047,
            -1.959804
          ],
          [
            -14.273104,
            -1.219802
          ],
          [
            -13.891699,
            -0.726468
          ],
          [
            -12.831203,
            -0.57186
          ],
          [
            -11.844533,
            -0.038584
          ],
          [
            -8.144527,
            0.349134
          ],
          [
            -7.157858,
            0.033975
          ],
          [
            0.982157,
            0.765471
          ],
          [
            1.968826,
            1.303214
          ],
          [
            4.682165,
            1.54329
          ],
          [
            5.422166,
            1.329031
          ],
          [
            6.162168,
            1.691509
          ],
          [
            8.478813,
            1.89381
          ],
          [
            9.122173,
            1.903964
          ],
          [
            9.615507,
            1.648239
          ],
          [
            10.355508,
            2.021769
          ],
          [
            11.835511,
            2.165848
          ],
          [
            12.82218,
            1.845083
          ],
          [
            13.808849,
            1.871981
          ],
          [
            14.055516,
            1.728574
          ],
          [
            14.293734,
            1.246869
          ],
          [
            14.217548,
            0.506867
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00010679999999999024,
    4.5094999999995e-05,
    0.004796355
  ],
  "construction_scale": 100.03451390798853,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
