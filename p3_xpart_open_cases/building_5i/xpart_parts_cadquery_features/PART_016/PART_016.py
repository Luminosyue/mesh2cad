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
      "start": -9.255052997134447,
      "length": 3.3658440192596846,
      "loops": [
        [
          [
            -3.215355,
            0.884387
          ],
          [
            -18.37975,
            -44.423656
          ],
          [
            -18.30133,
            -45.112136
          ],
          [
            -17.39769,
            -46.489095
          ],
          [
            -15.351325,
            -48.54625
          ],
          [
            -13.974367,
            -49.550072
          ],
          [
            -13.285886,
            -49.331678
          ],
          [
            -12.95829,
            -48.554533
          ],
          [
            -12.270385,
            -43.735176
          ],
          [
            -11.377784,
            -40.743827
          ],
          [
            -7.992361,
            -30.868372
          ],
          [
            -7.26609,
            -28.351188
          ],
          [
            -5.024125,
            -22.102477
          ],
          [
            -3.208102,
            -16.085984
          ],
          [
            3.237631,
            2.449473
          ],
          [
            4.770271,
            7.900822
          ],
          [
            5.378181,
            9.277781
          ],
          [
            6.280684,
            12.269128
          ],
          [
            9.6082,
            21.670417
          ],
          [
            14.479503,
            37.054405
          ],
          [
            17.695712,
            45.804465
          ],
          [
            18.297108,
            48.521134
          ],
          [
            17.695712,
            49.296653
          ],
          [
            16.318752,
            49.590756
          ],
          [
            15.630271,
            49.398741
          ],
          [
            12.71258,
            47.144178
          ],
          [
            12.157284,
            46.455696
          ],
          [
            6.421563,
            29.006269
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.889579179994648,
      "length": 15.14500237924898,
      "loops": [
        [
          [
            -9.261535,
            -21.25002
          ],
          [
            -8.780882,
            -21.924883
          ],
          [
            -8.119567,
            -22.24909
          ],
          [
            -7.089569,
            -22.32002
          ],
          [
            -6.401087,
            -22.077817
          ],
          [
            -5.732451,
            -21.329693
          ],
          [
            -5.354361,
            -20.326858
          ],
          [
            -5.340173,
            -19.324023
          ],
          [
            -5.590298,
            -18.651943
          ],
          [
            -6.219227,
            -17.947062
          ],
          [
            -7.089569,
            -17.585881
          ],
          [
            -7.778046,
            -17.689994
          ],
          [
            -8.466527,
            -18.132601
          ],
          [
            -9.132834,
            -18.949898
          ],
          [
            -9.421003,
            -19.638377
          ],
          [
            -9.470239,
            -20.641213
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.309226595,
    0.17519286,
    -0.069655435
  ],
  "construction_scale": 139.6046457857392,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
