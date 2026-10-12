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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -0.332797,
            -2.21468
          ],
          [
            0.537513,
            -1.317011
          ],
          [
            0.771022,
            -0.261175
          ],
          [
            0.111451,
            0.933147
          ],
          [
            -0.314612,
            1.287111
          ],
          [
            -0.773945,
            1.42806
          ],
          [
            -1.592797,
            1.303733
          ],
          [
            -2.018956,
            1.011808
          ],
          [
            -2.503841,
            0.164887
          ],
          [
            -2.322339,
            -1.113298
          ],
          [
            -6.726187,
            -4.09573
          ],
          [
            -7.199153,
            -4.521792
          ],
          [
            -7.317545,
            -4.947855
          ],
          [
            -6.653304,
            -5.799978
          ],
          [
            -6.279477,
            -5.935497
          ],
          [
            -5.427352,
            -5.799226
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 36.36563636363636,
      "loops": [
        [
          [
            5.475836,
            5.680158
          ],
          [
            6.076315,
            5.908539
          ],
          [
            6.713607,
            5.703689
          ],
          [
            7.311321,
            4.851567
          ],
          [
            7.217052,
            4.425504
          ],
          [
            5.340253,
            2.344287
          ],
          [
            2.955296,
            0.164887
          ],
          [
            0.963572,
            -1.2535
          ],
          [
            -0.256916,
            -2.34143
          ],
          [
            -5.001292,
            -5.538483
          ],
          [
            -5.853414,
            -5.897487
          ],
          [
            -6.279477,
            -5.899984
          ],
          [
            -7.077027,
            -5.373915
          ],
          [
            -7.310878,
            -4.947855
          ],
          [
            -7.131598,
            -4.477466
          ],
          [
            -2.278595,
            -1.113298
          ],
          [
            -2.466834,
            0.164887
          ],
          [
            -1.941316,
            1.017009
          ],
          [
            -1.166734,
            1.425722
          ],
          [
            -0.740674,
            1.436169
          ],
          [
            0.111451,
            1.120668
          ],
          [
            3.519945,
            4.178015
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 57.57775757575758,
      "loops": [
        [
          [
            -2.488247,
            -0.452935
          ],
          [
            -2.296074,
            -1.113298
          ],
          [
            -1.956494,
            -1.53936
          ],
          [
            -1.401037,
            -1.831797
          ],
          [
            -0.740674,
            -1.895478
          ],
          [
            0.111451,
            -1.430443
          ],
          [
            0.537175,
            -0.687238
          ],
          [
            0.579503,
            -0.261175
          ],
          [
            0.520905,
            0.164887
          ],
          [
            0.111451,
            0.878166
          ],
          [
            -0.314612,
            1.22602
          ],
          [
            -1.166734,
            1.421823
          ],
          [
            -1.971294,
            1.017009
          ],
          [
            -2.303894,
            0.59095
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0899362,
    0.511600595,
    -0.44082456999999997
  ],
  "construction_scale": 86.39351398965853,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
