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
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -9.041387293677333,
      "length": 3.2881388531925957,
      "loops": [
        [
          [
            -49.663983,
            -1.880953
          ],
          [
            -48.642019,
            -1.703311
          ],
          [
            -48.056465,
            -2.109828
          ],
          [
            -48.03344,
            -4.448505
          ],
          [
            -48.131037,
            -4.702896
          ],
          [
            -48.642019,
            -5.094916
          ],
          [
            -49.663983,
            -4.948681
          ],
          [
            -49.928666,
            -4.448505
          ],
          [
            -49.968423,
            -2.512694
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.753610095976485,
      "length": 10.411656114877768,
      "loops": [
        [
          [
            -49.663983,
            -6.707051
          ],
          [
            -49.970099,
            -6.089562
          ],
          [
            -49.892945,
            0.042212
          ],
          [
            -49.663983,
            0.457918
          ],
          [
            -49.153,
            0.659166
          ],
          [
            -48.642019,
            0.633663
          ],
          [
            -48.131037,
            0.200844
          ],
          [
            -48.011503,
            -0.46877
          ],
          [
            -48.018902,
            -6.089562
          ],
          [
            -48.211305,
            -6.600544
          ],
          [
            -48.642019,
            -6.838956
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.657684363409537,
      "length": 2.192213120625646,
      "loops": [
        [
          [
            -46.598095,
            2.683244
          ],
          [
            38.224789,
            2.991597
          ],
          [
            44.867543,
            3.184572
          ],
          [
            45.889507,
            3.393445
          ],
          [
            46.981713,
            4.241355
          ],
          [
            47.433822,
            5.152023
          ],
          [
            47.484842,
            6.173988
          ],
          [
            47.728204,
            6.684967
          ],
          [
            47.933433,
            6.797467
          ],
          [
            49.131712,
            6.684967
          ],
          [
            49.599576,
            6.173988
          ],
          [
            49.691761,
            5.663006
          ],
          [
            49.424564,
            4.130063
          ],
          [
            48.899609,
            3.108098
          ],
          [
            47.933433,
            2.146401
          ],
          [
            45.889507,
            1.403587
          ],
          [
            43.334599,
            1.056651
          ],
          [
            35.501327,
            0.829438
          ],
          [
            -46.598095,
            0.516601
          ],
          [
            -47.620057,
            0.347436
          ],
          [
            -47.798937,
            0.042212
          ],
          [
            -48.080761,
            -1.659286
          ],
          [
            -48.642019,
            -2.095726
          ],
          [
            -49.153,
            -2.099876
          ],
          [
            -49.663983,
            -1.748591
          ],
          [
            -49.831393,
            -0.97975
          ],
          [
            -49.730968,
            3.61908
          ],
          [
            -49.457058,
            4.130063
          ],
          [
            -48.642019,
            4.35188
          ],
          [
            -48.056801,
            4.130063
          ],
          [
            -47.861228,
            3.108098
          ],
          [
            -47.620057,
            2.774878
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.849535828543436,
      "length": 1.0962873880586976,
      "loops": [
        [
          [
            -49.663983,
            -0.395612
          ],
          [
            -49.153,
            -0.919024
          ],
          [
            -48.642019,
            -0.964143
          ],
          [
            -48.080045,
            -0.563362
          ],
          [
            -47.825595,
            1.575155
          ],
          [
            -47.912028,
            3.20269
          ],
          [
            -48.131037,
            3.833451
          ],
          [
            -48.577491,
            3.976863
          ],
          [
            -49.153,
            3.937823
          ],
          [
            -49.530643,
            3.61908
          ],
          [
            -49.696208,
            3.20269
          ],
          [
            -49.777787,
            0.553192
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.9454615611103865,
      "length": 1.096287388058694,
      "loops": [
        [
          [
            -49.663983,
            2.756875
          ],
          [
            -49.663983,
            0.476012
          ],
          [
            -49.153,
            -0.182619
          ],
          [
            -48.642019,
            -0.201959
          ],
          [
            -48.131037,
            0.13739
          ],
          [
            -48.005497,
            0.495583
          ],
          [
            -47.894833,
            2.086138
          ],
          [
            -47.997503,
            3.165707
          ],
          [
            -48.131037,
            3.384781
          ],
          [
            -48.642019,
            3.567142
          ],
          [
            -49.153,
            3.510998
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.30042268,
    0.166697595,
    0.15876608
  ],
  "construction_scale": 103.61282589186709,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
