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
      "start": -7.677928190913435,
      "length": 3.722938967267484,
      "loops": [
        [
          [
            -25.370658,
            22.592417
          ],
          [
            43.599796,
            22.657652
          ],
          [
            48.921691,
            22.431385
          ],
          [
            49.138017,
            22.295153
          ],
          [
            49.635218,
            -21.758076
          ],
          [
            49.592953,
            -22.258682
          ],
          [
            49.246122,
            -22.74828
          ],
          [
            -48.696261,
            -22.82199
          ],
          [
            -49.403926,
            -22.759286
          ],
          [
            -49.697473,
            -22.347745
          ],
          [
            -49.697473,
            22.416104
          ],
          [
            -49.196866,
            22.602917
          ],
          [
            -45.692633,
            22.559994
          ],
          [
            -44.691421,
            22.70331
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.9552963407735877,
      "length": 11.63353164881466,
      "loops": [
        [
          [
            -49.829114,
            7.277007
          ],
          [
            -49.732252,
            -22.759286
          ],
          [
            -48.696261,
            -22.918662
          ],
          [
            47.419877,
            -22.923782
          ],
          [
            49.422297,
            -22.776728
          ],
          [
            49.785218,
            -22.258682
          ],
          [
            49.789994,
            -21.758076
          ],
          [
            49.719086,
            -13.247794
          ],
          [
            49.459601,
            -11.245374
          ],
          [
            49.417352,
            -6.73993
          ],
          [
            49.427072,
            22.295153
          ],
          [
            48.921691,
            22.636439
          ],
          [
            47.419877,
            22.712698
          ],
          [
            30.899917,
            22.853085
          ],
          [
            -44.190819,
            22.921063
          ],
          [
            -46.193239,
            22.727974
          ],
          [
            -47.194447,
            22.844734
          ],
          [
            -49.196866,
            22.770846
          ],
          [
            -49.697473,
            22.610152
          ],
          [
            -49.825345,
            22.295153
          ],
          [
            -49.964192,
            12.162106
          ]
        ],
        [
          [
            -46.193239,
            19.955729
          ],
          [
            46.418669,
            19.757692
          ],
          [
            46.806341,
            19.291524
          ],
          [
            46.709517,
            12.283055
          ],
          [
            46.832817,
            11.281846
          ],
          [
            46.83294,
            -0.232067
          ],
          [
            47.03751,
            -9.363904
          ],
          [
            46.704826,
            -14.249004
          ],
          [
            46.718755,
            -20.256262
          ],
          [
            46.610348,
            -20.756868
          ],
          [
            46.418669,
            -20.891959
          ],
          [
            -45.571683,
            -20.908959
          ],
          [
            -46.48669,
            -20.756868
          ],
          [
            -46.623865,
            -19.876607
          ],
          [
            -46.593458,
            19.291524
          ],
          [
            -46.429848,
            19.792129
          ]
        ],
        [
          [
            -29.673276,
            20.999296
          ],
          [
            -11.651499,
            21.270474
          ],
          [
            -3.783453,
            21.794548
          ],
          [
            -9.64908,
            21.94358
          ],
          [
            -31.054141,
            21.96115
          ],
          [
            -43.690212,
            21.954424
          ],
          [
            -46.262259,
            21.794548
          ],
          [
            -45.692633,
            21.493248
          ],
          [
            -42.188398,
            21.319357
          ],
          [
            -39.685373,
            21.437171
          ],
          [
            -37.682952,
            21.138463
          ],
          [
            -33.678116,
            21.179566
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.014435630000000005,
    -0.48022272,
    0.012574120000000022
  ],
  "construction_scale": 50.75439660214338,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
