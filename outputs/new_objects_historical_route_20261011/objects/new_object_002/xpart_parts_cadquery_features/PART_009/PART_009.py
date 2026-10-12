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
      "start": -2.017240369791231,
      "length": 3.7900474449801376,
      "loops": [
        [
          [
            -49.447249,
            1.87999
          ],
          [
            -8.189053,
            6.653762
          ],
          [
            -4.483228,
            6.754159
          ],
          [
            -0.530346,
            6.583847
          ],
          [
            48.717534,
            -3.057667
          ],
          [
            49.761483,
            -3.376107
          ],
          [
            49.937432,
            -3.623163
          ],
          [
            49.935838,
            -4.117272
          ],
          [
            49.547228,
            -6.340768
          ],
          [
            49.374776,
            -6.658685
          ],
          [
            48.880665,
            -6.788862
          ],
          [
            12.647495,
            -0.245467
          ],
          [
            -0.777401,
            1.913113
          ],
          [
            -4.399304,
            1.946943
          ],
          [
            -8.189053,
            1.727756
          ],
          [
            -49.200196,
            -1.89217
          ],
          [
            -49.694303,
            -1.809051
          ],
          [
            -49.966485,
            -1.399667
          ],
          [
            -49.974737,
            1.317939
          ],
          [
            -49.903714,
            1.564994
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.7727263855741149,
      "length": 0.24459467383191055,
      "loops": [
        [
          [
            -8.498267,
            1.925095
          ],
          [
            -49.447249,
            -1.696816
          ],
          [
            -49.779769,
            -1.399667
          ],
          [
            -49.783058,
            1.317939
          ],
          [
            -49.447249,
            1.672751
          ],
          [
            -48.459031,
            1.829658
          ],
          [
            -11.265458,
            6.011985
          ],
          [
            -6.706723,
            6.354426
          ],
          [
            -1.271512,
            6.285321
          ],
          [
            4.682515,
            5.27082
          ],
          [
            27.331846,
            0.768798
          ],
          [
            48.024076,
            -3.129052
          ],
          [
            49.62183,
            -3.557851
          ],
          [
            49.714983,
            -3.958368
          ],
          [
            49.374776,
            -6.292135
          ],
          [
            49.127723,
            -6.580598
          ],
          [
            48.796387,
            -6.587823
          ],
          [
            16.269399,
            -0.543218
          ],
          [
            -0.283291,
            2.209053
          ],
          [
            -4.483228,
            2.182235
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.1634296,
    0.0003616700000000084,
    -0.20548813999999999
  ],
  "construction_scale": 100.19183530321837,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
