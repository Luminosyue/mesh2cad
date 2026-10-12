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
      "start": -28.023581020560584,
      "length": 5.096317492433657,
      "loops": [
        [
          [
            17.167821,
            48.988253
          ],
          [
            17.126284,
            -48.98539
          ],
          [
            16.947045,
            -49.470355
          ],
          [
            16.479272,
            -49.771819
          ],
          [
            -16.013617,
            -49.83641
          ],
          [
            -16.498586,
            -49.767781
          ],
          [
            -16.983554,
            -49.485137
          ],
          [
            -17.197084,
            -48.98539
          ],
          [
            -17.342339,
            -40.730921
          ],
          [
            -17.31921,
            46.563409
          ],
          [
            -17.245795,
            48.978251
          ],
          [
            -17.03096,
            49.466775
          ],
          [
            -16.498586,
            49.823621
          ],
          [
            15.994304,
            49.885109
          ],
          [
            16.479272,
            49.822459
          ],
          [
            16.964241,
            49.49039
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.92838447136775,
      "length": 50.95308643516916,
      "loops": [
        [
          [
            15.929654,
            47.523345
          ],
          [
            16.010921,
            -44.135706
          ],
          [
            15.892287,
            -47.530485
          ],
          [
            15.509335,
            -47.951805
          ],
          [
            14.539398,
            -48.076334
          ],
          [
            -16.502652,
            -48.015451
          ],
          [
            -16.995034,
            -47.530485
          ],
          [
            -17.144119,
            -46.560546
          ],
          [
            -17.252956,
            -31.526522
          ],
          [
            -17.225557,
            41.218752
          ],
          [
            -17.141826,
            47.038375
          ],
          [
            -17.040003,
            47.523345
          ],
          [
            -16.631176,
            48.008312
          ],
          [
            -16.013617,
            48.158119
          ],
          [
            -13.103807,
            48.184645
          ],
          [
            14.539398,
            48.176616
          ],
          [
            15.509335,
            48.041251
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    1.814999999999456e-05,
    -0.35752298000000005,
    4.910000000000331e-05
  ],
  "construction_scale": 196.6763351441848,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
