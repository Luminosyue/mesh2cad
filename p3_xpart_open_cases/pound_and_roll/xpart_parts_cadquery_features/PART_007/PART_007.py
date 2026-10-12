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
            -19.356993,
            3.040569
          ],
          [
            -15.08691,
            5.971535
          ],
          [
            -13.461725,
            6.373941
          ],
          [
            -11.200746,
            6.653355
          ],
          [
            7.665691,
            2.085197
          ],
          [
            19.041989,
            2.076077
          ],
          [
            19.854578,
            1.547579
          ],
          [
            20.13503,
            0.602792
          ],
          [
            20.142884,
            -5.085358
          ],
          [
            19.854578,
            -5.937511
          ],
          [
            19.041989,
            -6.43896
          ],
          [
            -18.337282,
            -6.615214
          ],
          [
            -19.962468,
            -6.512504
          ],
          [
            -20.748838,
            -5.897949
          ],
          [
            -20.960095,
            -5.085358
          ],
          [
            -20.912962,
            -0.209799
          ],
          [
            -20.747395,
            0.602792
          ],
          [
            -19.948361,
            2.227978
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 21.21412121212121,
      "loops": [
        [
          [
            -18.337282,
            4.422442
          ],
          [
            -19.15087,
            3.853164
          ],
          [
            -19.805032,
            3.040569
          ],
          [
            -20.911412,
            0.602792
          ],
          [
            -20.870046,
            -5.085358
          ],
          [
            -20.66104,
            -5.897949
          ],
          [
            -19.962468,
            -6.397646
          ],
          [
            19.041989,
            -6.27233
          ],
          [
            19.737743,
            -5.897949
          ],
          [
            20.184347,
            -5.085358
          ],
          [
            20.197567,
            0.602792
          ],
          [
            20.059485,
            1.415386
          ],
          [
            19.854578,
            1.727503
          ],
          [
            19.041989,
            2.263434
          ],
          [
            8.478279,
            2.283538
          ],
          [
            5.22791,
            3.712171
          ],
          [
            -6.172799,
            6.488144
          ],
          [
            -10.211355,
            6.094379
          ],
          [
            -16.712096,
            5.138102
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.696969696969695,
      "length": 30.305030303030303,
      "loops": [
        [
          [
            -16.712096,
            3.642567
          ],
          [
            -19.149873,
            3.210583
          ],
          [
            -19.962468,
            2.477953
          ],
          [
            -20.57303,
            1.415386
          ],
          [
            -20.684887,
            0.602792
          ],
          [
            -20.49534,
            -5.085358
          ],
          [
            -19.962468,
            -5.720202
          ],
          [
            -19.150096,
            -5.889423
          ],
          [
            19.041989,
            -5.671701
          ],
          [
            19.854578,
            -5.507572
          ],
          [
            20.335183,
            -5.085358
          ],
          [
            20.554501,
            -4.272766
          ],
          [
            20.441257,
            1.415386
          ],
          [
            20.195123,
            2.227978
          ],
          [
            19.854578,
            2.612945
          ],
          [
            19.041989,
            2.917553
          ],
          [
            9.290874,
            2.690969
          ],
          [
            1.164947,
            2.82699
          ],
          [
            -1.272834,
            3.034653
          ],
          [
            -6.148389,
            2.695399
          ],
          [
            -10.438807,
            3.331131
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.606060606060609,
      "length": 21.214121212121203,
      "loops": [
        [
          [
            -19.149873,
            -5.627036
          ],
          [
            3.087523,
            -5.633869
          ],
          [
            19.854578,
            -5.305552
          ],
          [
            20.179941,
            -5.085358
          ],
          [
            20.667872,
            -4.272766
          ],
          [
            20.597672,
            0.602792
          ],
          [
            20.424497,
            2.227978
          ],
          [
            19.854578,
            2.918292
          ],
          [
            19.041989,
            3.144342
          ],
          [
            9.290874,
            2.896816
          ],
          [
            4.712709,
            3.101238
          ],
          [
            -8.586169,
            3.075736
          ],
          [
            -11.023946,
            3.194865
          ],
          [
            -12.649133,
            3.62934
          ],
          [
            -15.08691,
            3.697739
          ],
          [
            -19.149873,
            3.095189
          ],
          [
            -19.962468,
            2.63476
          ],
          [
            -20.552131,
            1.415386
          ],
          [
            -20.448339,
            -4.272766
          ],
          [
            -20.221761,
            -5.085358
          ],
          [
            -19.962468,
            -5.363448
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 31.818181818181813,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            -19.149873,
            -5.350348
          ],
          [
            5.017486,
            -5.308523
          ],
          [
            19.854578,
            -5.053547
          ],
          [
            20.667172,
            -4.354916
          ],
          [
            20.79151,
            -3.670595
          ],
          [
            20.679984,
            2.227978
          ],
          [
            20.186683,
            3.040569
          ],
          [
            19.854578,
            3.27278
          ],
          [
            19.041989,
            3.428252
          ],
          [
            8.478279,
            3.230462
          ],
          [
            4.415316,
            3.427184
          ],
          [
            -4.523206,
            3.436233
          ],
          [
            -7.773575,
            3.182114
          ],
          [
            -11.836542,
            3.24494
          ],
          [
            -12.649133,
            3.386653
          ],
          [
            -15.08691,
            4.98956
          ],
          [
            -15.899504,
            5.11113
          ],
          [
            -17.524691,
            4.820496
          ],
          [
            -18.337282,
            4.43335
          ],
          [
            -19.149873,
            3.672798
          ],
          [
            -20.159398,
            2.227978
          ],
          [
            -20.428674,
            1.415386
          ],
          [
            -20.274244,
            -4.272766
          ],
          [
            -19.756965,
            -5.085358
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.557930165,
    -0.52020734,
    -0.02248738
  ],
  "construction_scale": 82.38564711528387,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
