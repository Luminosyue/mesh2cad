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
      "start": -1.124150953594037,
      "length": 0.34069677015754884,
      "loops": [
        [
          [
            -49.605115,
            -32.612833
          ],
          [
            -49.364569,
            -33.31696
          ],
          [
            -48.648959,
            -33.116701
          ],
          [
            -48.5271,
            -32.864767
          ],
          [
            -48.658636,
            20.847268
          ],
          [
            -48.622886,
            21.063452
          ],
          [
            -48.268018,
            21.212456
          ],
          [
            -46.593284,
            21.044601
          ],
          [
            -46.34135,
            21.310249
          ],
          [
            -46.284642,
            21.805135
          ],
          [
            -46.34135,
            22.145819
          ],
          [
            -46.593284,
            22.406951
          ],
          [
            -47.684844,
            22.560942
          ],
          [
            -48.379837,
            22.812876
          ],
          [
            -48.518501,
            23.064811
          ],
          [
            -48.475965,
            29.111252
          ],
          [
            -48.322131,
            32.386408
          ],
          [
            -48.157085,
            32.890277
          ],
          [
            -48.492476,
            33.142213
          ],
          [
            -49.112636,
            33.271099
          ],
          [
            -49.469676,
            33.142213
          ],
          [
            -49.502235,
            32.776008
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.124150953594037,
      "length": 0.34069677015754884,
      "loops": [
        [
          [
            48.638159,
            -6.558235
          ],
          [
            47.378483,
            -6.250769
          ],
          [
            47.126549,
            -5.999854
          ],
          [
            47.125153,
            -6.915458
          ],
          [
            48.245779,
            -7.026949
          ],
          [
            48.953512,
            -6.915458
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.783499149474632,
      "length": 1.4989129041635267,
      "loops": [
        [
          [
            -49.616503,
            33.286943
          ],
          [
            -49.682019,
            -33.116701
          ],
          [
            -49.364569,
            -33.488276
          ],
          [
            -46.593284,
            -33.464757
          ],
          [
            -46.339504,
            -33.368638
          ],
          [
            -46.169214,
            -32.761672
          ],
          [
            -46.087659,
            22.057071
          ],
          [
            -46.162266,
            32.741437
          ],
          [
            -46.40211,
            33.394149
          ],
          [
            -49.112636,
            33.488394
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.783499149474632,
      "length": 1.4989129041635267,
      "loops": [
        [
          [
            49.866791,
            32.890277
          ],
          [
            49.868793,
            -32.864767
          ],
          [
            49.659948,
            -33.368638
          ],
          [
            49.393963,
            -33.444112
          ],
          [
            47.126549,
            -33.447057
          ],
          [
            46.764899,
            -33.116701
          ],
          [
            46.72118,
            -32.005866
          ],
          [
            46.668535,
            -3.136433
          ],
          [
            46.704216,
            32.890277
          ],
          [
            46.874615,
            33.374787
          ],
          [
            47.126549,
            33.474538
          ],
          [
            49.393963,
            33.454804
          ],
          [
            49.752971,
            33.245308
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7153687886507509,
      "length": 0.40882713098142986,
      "loops": [
        [
          [
            -46.339699,
            19.285786
          ],
          [
            -46.404622,
            26.088032
          ],
          [
            -46.593284,
            26.664355
          ],
          [
            -47.85296,
            26.705362
          ],
          [
            -49.112636,
            26.528395
          ],
          [
            -49.364569,
            26.351524
          ],
          [
            -49.376744,
            26.088032
          ],
          [
            -48.967208,
            23.927126
          ],
          [
            -49.287074,
            20.041591
          ],
          [
            -49.291085,
            19.195641
          ],
          [
            -49.112636,
            18.880229
          ],
          [
            -48.286517,
            18.711606
          ],
          [
            -46.593284,
            18.77176
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.7153687886507509,
      "length": 0.40882713098142986,
      "loops": [
        [
          [
            46.938587,
            19.285786
          ],
          [
            46.897219,
            26.339966
          ],
          [
            47.126549,
            26.62265
          ],
          [
            47.63042,
            26.665598
          ],
          [
            49.14203,
            26.406834
          ],
          [
            49.394741,
            26.087254
          ],
          [
            49.227186,
            23.73546
          ],
          [
            49.282743,
            21.301266
          ],
          [
            49.508478,
            19.537721
          ],
          [
            49.393963,
            19.005154
          ],
          [
            48.638159,
            18.819755
          ],
          [
            47.126549,
            18.809088
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.002609674999999978,
    -0.040810879999999994,
    -0.239106205
  ],
  "construction_scale": 102.17088090047693,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
