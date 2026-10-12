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
            5.876385,
            -0.447793
          ],
          [
            6.929801,
            -1.118819
          ],
          [
            7.719863,
            -0.941659
          ],
          [
            8.168015,
            -0.192197
          ],
          [
            7.983218,
            0.517216
          ],
          [
            7.521571,
            0.861219
          ],
          [
            6.929801,
            0.95514
          ],
          [
            6.403093,
            0.820571
          ],
          [
            5.876385,
            0.378393
          ],
          [
            4.822969,
            0.908149
          ],
          [
            3.5062,
            0.556519
          ],
          [
            2.979492,
            0.96881
          ],
          [
            2.452784,
            1.086035
          ],
          [
            1.399368,
            0.579954
          ],
          [
            0.87266,
            1.066761
          ],
          [
            0.345951,
            1.137045
          ],
          [
            -0.44411,
            0.636758
          ],
          [
            -2.024235,
            0.801857
          ],
          [
            -2.814297,
            0.452551
          ],
          [
            -3.077651,
            0.492043
          ],
          [
            -3.377459,
            0.861219
          ],
          [
            -3.867713,
            1.116519
          ],
          [
            -4.394421,
            1.10596
          ],
          [
            -5.184484,
            0.791544
          ],
          [
            -5.974546,
            1.26989
          ],
          [
            -6.501253,
            1.401354
          ],
          [
            -7.257661,
            1.124573
          ],
          [
            -7.511527,
            0.597865
          ],
          [
            -7.113121,
            -0.455552
          ],
          [
            -6.501253,
            -0.790356
          ],
          [
            -5.920551,
            -0.718905
          ],
          [
            -5.184484,
            -0.173337
          ],
          [
            -4.657775,
            -0.6314
          ],
          [
            -4.131067,
            -0.800657
          ],
          [
            -3.604359,
            -0.731286
          ],
          [
            -3.077651,
            -0.218414
          ],
          [
            -2.024235,
            -0.819815
          ],
          [
            -1.234172,
            -0.747897
          ],
          [
            -0.707465,
            -0.394537
          ],
          [
            0.345951,
            -0.925617
          ],
          [
            0.87266,
            -0.837937
          ],
          [
            1.399368,
            -0.418032
          ],
          [
            2.452784,
            -0.969218
          ],
          [
            2.979492,
            -0.860636
          ],
          [
            3.5062,
            -0.41428
          ],
          [
            4.559615,
            -1.082223
          ],
          [
            5.179324,
            -0.98226
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            -3.760645,
            -0.930361
          ],
          [
            -3.387566,
            -0.455552
          ],
          [
            -3.362492,
            -0.192197
          ],
          [
            -3.867713,
            0.482824
          ],
          [
            -4.657775,
            0.632109
          ],
          [
            -5.184484,
            0.145611
          ],
          [
            -5.447837,
            0.150527
          ],
          [
            -5.732049,
            0.861219
          ],
          [
            -6.237898,
            1.355044
          ],
          [
            -7.027962,
            1.442537
          ],
          [
            -7.434723,
            1.124573
          ],
          [
            -7.571471,
            0.597865
          ],
          [
            -7.507535,
            0.071156
          ],
          [
            -7.113767,
            -0.718905
          ],
          [
            -6.764608,
            -1.027527
          ],
          [
            -5.988325,
            -0.98226
          ],
          [
            -5.447837,
            -0.236582
          ],
          [
            -4.657775,
            -1.077798
          ],
          [
            -4.131067,
            -1.125648
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            7.086087,
            0.407467
          ],
          [
            7.719863,
            0.166759
          ],
          [
            7.911818,
            -0.56262
          ],
          [
            7.456509,
            -1.257214
          ],
          [
            6.666448,
            -1.434919
          ],
          [
            6.058047,
            -0.98226
          ],
          [
            5.96555,
            -0.455552
          ],
          [
            6.403093,
            0.159903
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            -1.497527,
            0.350902
          ],
          [
            -1.214763,
            0.071156
          ],
          [
            -1.029304,
            -0.455552
          ],
          [
            -1.226704,
            -0.98226
          ],
          [
            -1.76088,
            -1.330693
          ],
          [
            -2.463626,
            -1.245614
          ],
          [
            -3.008553,
            -0.455552
          ],
          [
            -2.807471,
            0.071156
          ],
          [
            -2.287589,
            0.449066
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            1.971242,
            0.118109
          ],
          [
            1.51903,
            -0.192197
          ],
          [
            1.222887,
            -0.718905
          ],
          [
            1.926076,
            -1.364471
          ],
          [
            2.452784,
            -1.433998
          ],
          [
            2.919918,
            -1.245614
          ],
          [
            3.251421,
            -0.718905
          ],
          [
            3.034391,
            -0.192197
          ],
          [
            2.452784,
            0.129874
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            0.609306,
            -1.351238
          ],
          [
            -0.024471,
            -1.407651
          ],
          [
            -0.571098,
            -0.98226
          ],
          [
            -0.729487,
            -0.455552
          ],
          [
            -0.180757,
            0.175093
          ],
          [
            0.609306,
            0.137124
          ],
          [
            1.087678,
            -0.455552
          ],
          [
            0.991182,
            -0.98226
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 90.9110909090909,
      "loops": [
        [
          [
            5.637187,
            -0.869281
          ],
          [
            5.086323,
            -1.296307
          ],
          [
            4.559615,
            -1.319653
          ],
          [
            3.919343,
            -0.718905
          ],
          [
            3.987282,
            -0.192197
          ],
          [
            4.559615,
            0.267724
          ],
          [
            5.086323,
            0.238001
          ],
          [
            5.384495,
            0.071156
          ],
          [
            5.747042,
            -0.455552
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.114201105,
    -0.111628165,
    0.00011690000000000311
  ],
  "construction_scale": 106.80178487997306,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
