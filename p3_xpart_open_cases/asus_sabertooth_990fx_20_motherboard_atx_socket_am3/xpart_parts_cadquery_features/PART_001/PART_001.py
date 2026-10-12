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
      "length": 30.305030303030303,
      "loops": [
        [
          [
            0.144837,
            -5.648669
          ],
          [
            1.517321,
            13.797291
          ],
          [
            1.246516,
            14.074934
          ],
          [
            0.608942,
            13.98505
          ],
          [
            0.306616,
            13.478506
          ],
          [
            0.197882,
            12.840933
          ],
          [
            -0.684159,
            4.871277
          ],
          [
            -1.166427,
            -5.329883
          ],
          [
            -1.126993,
            -10.111677
          ],
          [
            -0.82919,
            -13.618325
          ],
          [
            -0.666201,
            -14.059487
          ],
          [
            -0.198188,
            -14.574684
          ],
          [
            0.927731,
            -15.013766
          ],
          [
            1.267122,
            -14.574684
          ],
          [
            0.355411,
            -9.419462
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -19.696969696969695,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            0.06913,
            -5.583023
          ],
          [
            1.509912,
            13.797291
          ],
          [
            1.423424,
            14.162488
          ],
          [
            0.927731,
            14.368522
          ],
          [
            0.301234,
            14.116079
          ],
          [
            0.118936,
            13.797291
          ],
          [
            -0.275294,
            10.675076
          ],
          [
            -0.818188,
            4.871277
          ],
          [
            -1.344486,
            -6.605028
          ],
          [
            -1.139824,
            -13.618325
          ],
          [
            -0.984986,
            -13.980477
          ],
          [
            -0.347416,
            -14.540065
          ],
          [
            0.927731,
            -14.90192
          ],
          [
            1.226458,
            -14.509038
          ],
          [
            0.234065,
            -10.111677
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 57.57775757575758,
      "loops": [
        [
          [
            0.686086,
            -12.89677
          ],
          [
            0.157916,
            -10.111677
          ],
          [
            -0.012222,
            -7.561386
          ],
          [
            0.514352,
            2.639773
          ],
          [
            1.519871,
            13.797291
          ],
          [
            1.401216,
            14.753651
          ],
          [
            0.927731,
            14.934987
          ],
          [
            0.608942,
            14.90667
          ],
          [
            -0.028627,
            14.450228
          ],
          [
            -0.290782,
            13.797291
          ],
          [
            -1.158604,
            2.40497
          ],
          [
            -1.522034,
            -7.477404
          ],
          [
            -1.350668,
            -13.618325
          ],
          [
            -0.582218,
            -14.315536
          ],
          [
            0.37414,
            -14.726136
          ],
          [
            0.927731,
            -14.738519
          ],
          [
            1.112963,
            -14.255897
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.97602196,
    0.013410610000000003,
    -0.006240084999999951
  ],
  "construction_scale": 64.64101254923165,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
