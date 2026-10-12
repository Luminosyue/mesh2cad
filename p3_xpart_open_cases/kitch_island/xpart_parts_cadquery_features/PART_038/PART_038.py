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
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -4.116472,
            -7.829374
          ],
          [
            -3.488228,
            -9.73259
          ],
          [
            -2.632815,
            -10.268713
          ],
          [
            -0.729595,
            -10.708651
          ],
          [
            1.197504,
            -11.033282
          ],
          [
            3.112666,
            -11.098251
          ],
          [
            4.432561,
            -9.73259
          ],
          [
            4.461694,
            9.418972
          ],
          [
            3.112666,
            10.901573
          ],
          [
            1.197504,
            11.213097
          ],
          [
            -0.729595,
            11.196898
          ],
          [
            -2.632815,
            10.757598
          ],
          [
            -3.762836,
            9.418972
          ],
          [
            -4.156938,
            3.661563
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 9.092909090909087,
      "loops": [
        [
          [
            -4.297513,
            -7.817435
          ],
          [
            -4.300615,
            9.418972
          ],
          [
            -2.632815,
            10.757987
          ],
          [
            -0.717655,
            10.271016
          ],
          [
            1.197504,
            10.09342
          ],
          [
            3.112666,
            10.740788
          ],
          [
            4.333021,
            9.418972
          ],
          [
            4.415521,
            -5.902279
          ],
          [
            4.246241,
            -7.817435
          ],
          [
            3.342351,
            -9.721659
          ],
          [
            3.112666,
            -9.885795
          ],
          [
            1.993872,
            -9.73259
          ],
          [
            1.736697,
            -9.213265
          ],
          [
            1.065949,
            -8.700458
          ],
          [
            0.444207,
            -7.817435
          ],
          [
            -0.717655,
            -7.618159
          ],
          [
            -1.819409,
            -9.73259
          ],
          [
            -2.632815,
            -10.005482
          ],
          [
            -3.347362,
            -9.73259
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -31.81818181818182,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            4.341012,
            9.418972
          ],
          [
            4.367817,
            -7.817435
          ],
          [
            3.648466,
            -9.73259
          ],
          [
            3.112666,
            -10.110343
          ],
          [
            0.099239,
            -9.73259
          ],
          [
            -0.477238,
            -7.817435
          ],
          [
            -0.717655,
            -7.7129
          ],
          [
            -1.207251,
            -9.73259
          ],
          [
            -2.632815,
            -10.193094
          ],
          [
            -3.829345,
            -9.73259
          ],
          [
            -4.448665,
            -7.817435
          ],
          [
            -4.385235,
            9.418972
          ],
          [
            -2.632815,
            10.789901
          ],
          [
            -0.717655,
            10.471181
          ],
          [
            1.197504,
            10.505811
          ],
          [
            3.112666,
            10.770535
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -25.757575757575758,
      "length": 69.69896969696968,
      "loops": [
        [
          [
            -2.757058,
            -10.167402
          ],
          [
            -3.790479,
            -9.73259
          ],
          [
            -4.411886,
            -7.817435
          ],
          [
            -4.394647,
            9.418972
          ],
          [
            -2.632815,
            10.830148
          ],
          [
            -0.717655,
            10.455862
          ],
          [
            1.197504,
            10.821182
          ],
          [
            3.112666,
            10.709463
          ],
          [
            4.288742,
            9.418972
          ],
          [
            4.333883,
            -7.817435
          ],
          [
            3.752461,
            -9.73259
          ],
          [
            3.112666,
            -10.180293
          ],
          [
            1.197504,
            -10.139739
          ],
          [
            -0.608451,
            -9.73259
          ],
          [
            -0.717655,
            -7.778493
          ],
          [
            -0.802605,
            -9.73259
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            4.251153,
            9.418972
          ],
          [
            4.210432,
            -7.817435
          ],
          [
            3.723729,
            -9.73259
          ],
          [
            3.112666,
            -10.205946
          ],
          [
            1.197504,
            -10.276818
          ],
          [
            -0.717655,
            -9.611394
          ],
          [
            -2.632815,
            -10.211843
          ],
          [
            -3.933274,
            -9.73259
          ],
          [
            -4.369141,
            -7.817435
          ],
          [
            -4.327238,
            9.418972
          ],
          [
            -2.632815,
            10.54211
          ],
          [
            -0.717655,
            10.553403
          ],
          [
            1.197504,
            10.87711
          ],
          [
            3.112666,
            10.683709
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.950571,
    0.050123995,
    0.25376137
  ],
  "construction_scale": 194.17028570953687,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
