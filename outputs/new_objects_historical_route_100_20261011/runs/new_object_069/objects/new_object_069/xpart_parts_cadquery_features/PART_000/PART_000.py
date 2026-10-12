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
      "length": 9.092909090909094,
      "loops": [
        [
          [
            4.84865,
            -0.447748
          ],
          [
            5.079107,
            2.198291
          ],
          [
            4.913617,
            2.485206
          ],
          [
            4.561021,
            2.198291
          ],
          [
            4.330467,
            -0.405175
          ],
          [
            4.028423,
            -0.902881
          ],
          [
            3.611883,
            -1.097777
          ],
          [
            1.529111,
            -1.359095
          ],
          [
            -0.814008,
            -1.387229
          ],
          [
            -4.719207,
            0.245146
          ],
          [
            -5.024178,
            0.115518
          ],
          [
            -4.985193,
            -0.144828
          ],
          [
            -4.719207,
            -0.302664
          ],
          [
            -1.595048,
            -1.678343
          ],
          [
            -0.553662,
            -1.940678
          ],
          [
            1.789457,
            -1.879329
          ],
          [
            3.872231,
            -1.579641
          ],
          [
            4.489116,
            -1.186214
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
            -1.074355,
            -1.916546
          ],
          [
            3.872231,
            -1.714103
          ],
          [
            4.61291,
            -1.186214
          ],
          [
            5.010503,
            0.218213
          ],
          [
            5.138806,
            2.198291
          ],
          [
            4.948197,
            2.458637
          ],
          [
            4.616159,
            2.198291
          ],
          [
            4.387713,
            -0.405175
          ],
          [
            4.159062,
            -0.925868
          ],
          [
            3.843546,
            -1.176154
          ],
          [
            -0.553662,
            -1.478279
          ],
          [
            -1.074355,
            -1.341297
          ],
          [
            -1.958089,
            -0.802259
          ],
          [
            -2.636434,
            -0.699662
          ],
          [
            -4.719207,
            0.188021
          ],
          [
            -5.017302,
            0.115518
          ],
          [
            -5.030245,
            -0.144828
          ],
          [
            -4.719207,
            -0.357734
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -31.81818181818182,
      "length": 39.3959393939394,
      "loops": [
        [
          [
            -0.293315,
            -2.218607
          ],
          [
            3.872231,
            -1.903908
          ],
          [
            4.392924,
            -1.663855
          ],
          [
            4.741925,
            -1.186214
          ],
          [
            4.953633,
            -0.405175
          ],
          [
            5.114349,
            2.198291
          ],
          [
            4.913617,
            2.427952
          ],
          [
            4.623447,
            2.198291
          ],
          [
            4.436067,
            -0.405175
          ],
          [
            4.29188,
            -0.925868
          ],
          [
            3.872231,
            -1.367537
          ],
          [
            -0.553662,
            -1.690959
          ],
          [
            -4.671672,
            0.115518
          ],
          [
            -4.988006,
            0.115518
          ],
          [
            -5.070979,
            -0.144828
          ],
          [
            -4.719207,
            -0.405248
          ],
          [
            -1.334701,
            -2.012164
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.575757575757578,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            -0.032969,
            -2.333652
          ],
          [
            4.132576,
            -1.890714
          ],
          [
            4.659323,
            -1.446561
          ],
          [
            5.001199,
            -0.144828
          ],
          [
            5.106773,
            1.937944
          ],
          [
            4.913617,
            2.272146
          ],
          [
            4.65327,
            2.169234
          ],
          [
            4.567185,
            1.937944
          ],
          [
            4.340093,
            -0.925868
          ],
          [
            4.132576,
            -1.256802
          ],
          [
            3.611883,
            -1.502648
          ],
          [
            -0.814008,
            -1.797059
          ],
          [
            -4.719207,
            0.004598
          ],
          [
            -5.118911,
            -0.144828
          ],
          [
            -4.979553,
            -0.419111
          ],
          [
            -1.074355,
            -2.26666
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 40.90909090909091,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            5.101167,
            1.937944
          ],
          [
            4.948111,
            -0.665521
          ],
          [
            4.671428,
            -1.446561
          ],
          [
            4.132576,
            -1.917853
          ],
          [
            3.439835,
            -1.859873
          ],
          [
            2.830844,
            -2.173073
          ],
          [
            -1.074355,
            -2.117081
          ],
          [
            -1.855394,
            -1.625137
          ],
          [
            -2.896781,
            -1.397113
          ],
          [
            -4.45886,
            -0.695504
          ],
          [
            -5.004027,
            -0.405175
          ],
          [
            -5.134768,
            -0.144828
          ],
          [
            -4.979553,
            0.021992
          ],
          [
            -4.719207,
            0.00438
          ],
          [
            -2.896781,
            -0.846031
          ],
          [
            -1.595048,
            -0.988621
          ],
          [
            -0.814008,
            -1.603077
          ],
          [
            2.570498,
            -1.635077
          ],
          [
            3.351538,
            -1.25472
          ],
          [
            3.872231,
            -1.341036
          ],
          [
            4.228304,
            -1.186214
          ],
          [
            4.468991,
            -0.405175
          ],
          [
            4.566364,
            1.937944
          ],
          [
            4.913617,
            2.227012
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00016868000000000438,
    0.091547605,
    -0.00602575
  ],
  "construction_scale": 105.58214043463605,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
