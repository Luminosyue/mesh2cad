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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -11.992146,
            -29.430998
          ],
          [
            -11.495115,
            38.024303
          ],
          [
            -11.330486,
            38.275507
          ],
          [
            -10.865429,
            38.387969
          ],
          [
            10.368051,
            37.956016
          ],
          [
            11.491864,
            37.784399
          ],
          [
            12.193299,
            37.019478
          ],
          [
            12.278583,
            33.753808
          ],
          [
            11.98166,
            -38.177984
          ],
          [
            11.926327,
            -39.347004
          ],
          [
            11.491864,
            -39.8151
          ],
          [
            10.738247,
            -40.014203
          ],
          [
            -11.36784,
            -40.034742
          ],
          [
            -11.870251,
            -39.946204
          ],
          [
            -12.236694,
            -39.598211
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 9.092909090909094,
      "loops": [
        [
          [
            12.477439,
            -19.501766
          ],
          [
            12.527989,
            28.980903
          ],
          [
            12.384036,
            35.427542
          ],
          [
            12.213038,
            37.270686
          ],
          [
            11.491864,
            38.031621
          ],
          [
            10.738247,
            38.229433
          ],
          [
            -5.002998,
            38.380406
          ],
          [
            -11.116635,
            38.666183
          ],
          [
            -11.553538,
            38.275507
          ],
          [
            -11.623887,
            37.773095
          ],
          [
            -12.456982,
            -38.929296
          ],
          [
            -12.272833,
            -39.598211
          ],
          [
            -11.870251,
            -39.885036
          ],
          [
            -11.116635,
            -39.945247
          ],
          [
            10.738247,
            -40.078549
          ],
          [
            11.240658,
            -39.971787
          ],
          [
            11.786336,
            -39.598211
          ],
          [
            12.077402,
            -39.095799
          ],
          [
            12.147507,
            -38.090975
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -34.848484848484844,
      "length": 12.123212121212118,
      "loops": [
        [
          [
            -12.39552,
            -5.722657
          ],
          [
            -12.539751,
            -38.379378
          ],
          [
            -12.372662,
            -39.393326
          ],
          [
            -11.870251,
            -39.746963
          ],
          [
            -10.363018,
            -39.811426
          ],
          [
            10.738247,
            -39.953122
          ],
          [
            11.615413,
            -39.583295
          ],
          [
            11.994275,
            -39.256225
          ],
          [
            12.167353,
            -38.593387
          ],
          [
            12.556707,
            -24.525878
          ],
          [
            12.660345,
            19.686297
          ],
          [
            12.574209,
            29.734519
          ],
          [
            12.338431,
            37.019478
          ],
          [
            12.218366,
            37.52189
          ],
          [
            11.240658,
            38.508352
          ],
          [
            8.728603,
            38.715269
          ],
          [
            -10.865429,
            38.98487
          ],
          [
            -11.36784,
            38.826369
          ],
          [
            -11.606017,
            38.526711
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.727272727272727,
      "length": 57.57775757575757,
      "loops": [
        [
          [
            12.715187,
            -8.375062
          ],
          [
            12.132473,
            -38.342183
          ],
          [
            12.034422,
            -38.844591
          ],
          [
            11.491864,
            -39.340255
          ],
          [
            10.664586,
            -39.524346
          ],
          [
            -10.687884,
            -39.486305
          ],
          [
            -11.870251,
            -39.446785
          ],
          [
            -12.486289,
            -39.095799
          ],
          [
            -12.6997,
            -37.76611
          ],
          [
            -12.817147,
            -30.303604
          ],
          [
            -12.743615,
            -1.090101
          ],
          [
            -11.71996,
            38.526711
          ],
          [
            -11.501359,
            39.029123
          ],
          [
            -11.116635,
            39.358505
          ],
          [
            10.664586,
            39.091136
          ],
          [
            11.240658,
            38.97501
          ],
          [
            12.152027,
            38.024303
          ],
          [
            12.459751,
            30.813002
          ],
          [
            12.750681,
            12.150131
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 34.848484848484844,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            -11.624526,
            38.937445
          ],
          [
            -12.759564,
            -37.245681
          ],
          [
            -12.587473,
            -38.342183
          ],
          [
            -12.269963,
            -38.593387
          ],
          [
            -11.710724,
            -38.654271
          ],
          [
            10.738247,
            -38.717214
          ],
          [
            11.743069,
            -38.446014
          ],
          [
            12.085577,
            -38.090975
          ],
          [
            12.255055,
            -37.588567
          ],
          [
            12.370241,
            -33.820482
          ],
          [
            12.663252,
            7.377226
          ],
          [
            12.396507,
            37.864774
          ],
          [
            12.24548,
            38.941415
          ],
          [
            11.491864,
            39.675815
          ],
          [
            9.641747,
            39.887131
          ],
          [
            -6.846141,
            40.057333
          ],
          [
            -10.865429,
            40.075933
          ],
          [
            -11.393589,
            39.782739
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.002552830000000006,
    0.0061800499999999925,
    0.0031203000000000203
  ],
  "construction_scale": 50.937518786393646,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
