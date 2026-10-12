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
      "start": -50.0,
      "length": 75.75957575757575,
      "loops": [
        [
          [
            -8.074243,
            -6.711169
          ],
          [
            -19.959567,
            -6.385984
          ],
          [
            -31.349671,
            -5.69202
          ],
          [
            -34.073391,
            -5.262008
          ],
          [
            -34.428875,
            -4.813771
          ],
          [
            -34.490713,
            -4.231567
          ],
          [
            -34.319068,
            -3.328105
          ],
          [
            -34.073391,
            -2.915347
          ],
          [
            -33.296275,
            -2.337661
          ],
          [
            -32.835336,
            -2.210796
          ],
          [
            -24.577193,
            -3.445744
          ],
          [
            -17.73107,
            -3.922987
          ],
          [
            -13.026461,
            -4.074225
          ],
          [
            -0.311322,
            -4.254667
          ],
          [
            27.601262,
            -3.327125
          ],
          [
            28.75678,
            -3.080494
          ],
          [
            29.562618,
            -2.695173
          ],
          [
            30.14249,
            -2.090051
          ],
          [
            30.684785,
            -1.099606
          ],
          [
            31.848692,
            1.711095
          ],
          [
            33.007167,
            6.823942
          ],
          [
            33.27678,
            6.970799
          ],
          [
            33.772003,
            6.847056
          ],
          [
            34.26556,
            6.08111
          ],
          [
            34.437665,
            4.843055
          ],
          [
            34.256325,
            2.969811
          ],
          [
            33.551973,
            0.227327
          ],
          [
            32.781562,
            -1.670982
          ],
          [
            31.884336,
            -3.415087
          ],
          [
            31.080688,
            -4.56616
          ],
          [
            30.05784,
            -5.333028
          ],
          [
            29.067395,
            -5.721374
          ],
          [
            26.430657,
            -6.06188
          ],
          [
            19.745163,
            -5.921732
          ],
          [
            1.830194,
            -6.657369
          ]
        ],
        [
          [
            -31.436652,
            -4.021759
          ],
          [
            -32.20003,
            -3.599045
          ],
          [
            -32.835336,
            -3.448334
          ],
          [
            -33.207829,
            -3.575716
          ],
          [
            -33.367892,
            -3.823327
          ],
          [
            -33.362995,
            -4.070938
          ],
          [
            -33.082945,
            -4.154848
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.75757575757575,
      "length": 24.244424242424248,
      "loops": [
        [
          [
            -23.810559,
            -3.509221
          ],
          [
            -1.141137,
            -4.224868
          ],
          [
            28.819786,
            -3.538799
          ],
          [
            29.708878,
            -3.268952
          ],
          [
            30.305451,
            -2.860909
          ],
          [
            30.960434,
            -2.090051
          ],
          [
            31.481944,
            -1.099606
          ],
          [
            32.464469,
            2.119335
          ],
          [
            32.771916,
            6.328722
          ],
          [
            32.994547,
            6.823942
          ],
          [
            33.524394,
            6.864159
          ],
          [
            33.900218,
            6.576331
          ],
          [
            34.327439,
            5.338277
          ],
          [
            34.447075,
            3.220562
          ],
          [
            34.18763,
            0.881281
          ],
          [
            33.626696,
            -0.851995
          ],
          [
            32.615718,
            -2.943666
          ],
          [
            31.815765,
            -4.070938
          ],
          [
            31.048283,
            -4.644789
          ],
          [
            29.810228,
            -5.180256
          ],
          [
            28.076952,
            -5.55004
          ],
          [
            24.85801,
            -5.792772
          ],
          [
            5.159919,
            -6.279731
          ],
          [
            -6.230184,
            -6.356394
          ],
          [
            -33.330559,
            -5.412714
          ],
          [
            -34.073391,
            -5.255015
          ],
          [
            -34.321,
            -5.036499
          ],
          [
            -34.495611,
            -4.455377
          ],
          [
            -34.195327,
            -3.328105
          ],
          [
            -33.825778,
            -2.98925
          ],
          [
            -33.330559,
            -2.819342
          ]
        ],
        [
          [
            -33.082945,
            -4.400656
          ],
          [
            -31.543134,
            -4.070938
          ],
          [
            -33.082945,
            -3.930558
          ],
          [
            -33.363076,
            -4.070938
          ],
          [
            -33.357572,
            -4.318549
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.000965149999999998,
    -0.02850275,
    0.00027893000000001056
  ],
  "construction_scale": 100.4172618397776,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
