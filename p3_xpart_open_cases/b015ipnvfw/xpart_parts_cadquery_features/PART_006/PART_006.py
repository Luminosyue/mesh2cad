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
      "start": -39.326169703993635,
      "length": 14.301998393694937,
      "loops": [
        [
          [
            -16.796703,
            -48.397442
          ],
          [
            -16.830841,
            47.704086
          ],
          [
            -16.710185,
            48.848144
          ],
          [
            -15.81393,
            49.721132
          ],
          [
            -13.033696,
            49.8904
          ],
          [
            7.559489,
            49.954513
          ],
          [
            8.211453,
            49.930676
          ],
          [
            9.355516,
            49.24296
          ],
          [
            9.596027,
            48.848144
          ],
          [
            9.718214,
            47.704086
          ],
          [
            9.772105,
            41.491653
          ],
          [
            9.856349,
            -13.423506
          ],
          [
            9.707291,
            -47.253374
          ],
          [
            9.691774,
            -48.397442
          ],
          [
            9.355516,
            -49.238084
          ],
          [
            9.078437,
            -49.541512
          ],
          [
            8.211453,
            -49.920167
          ],
          [
            -14.669864,
            -49.979564
          ],
          [
            -15.81393,
            -49.872532
          ],
          [
            -16.288375,
            -49.541512
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -25.025744357086857,
      "length": 38.13604063853956,
      "loops": [
        [
          [
            15.075844,
            -11.580973
          ],
          [
            13.931781,
            -11.448231
          ],
          [
            12.787713,
            -11.729894
          ],
          [
            11.64365,
            -12.998525
          ],
          [
            10.49958,
            -12.091559
          ],
          [
            10.16979,
            -10.643279
          ],
          [
            9.925502,
            -3.778871
          ],
          [
            9.775363,
            41.983753
          ],
          [
            9.717817,
            47.704086
          ],
          [
            9.582927,
            48.848144
          ],
          [
            9.355516,
            49.212008
          ],
          [
            8.211453,
            49.929027
          ],
          [
            -9.792837,
            49.930482
          ],
          [
            -14.669864,
            49.844439
          ],
          [
            -15.81393,
            49.700512
          ],
          [
            -16.705185,
            48.848144
          ],
          [
            -16.865855,
            47.704086
          ],
          [
            -16.806177,
            -48.397442
          ],
          [
            -16.24122,
            -49.541512
          ],
          [
            -15.81393,
            -49.825007
          ],
          [
            -13.525798,
            -49.952948
          ],
          [
            8.211453,
            -49.915401
          ],
          [
            9.106154,
            -49.541512
          ],
          [
            9.355516,
            -49.274221
          ],
          [
            9.695154,
            -48.397442
          ],
          [
            9.875601,
            -28.948327
          ],
          [
            10.49958,
            -25.359123
          ],
          [
            11.64365,
            -24.783571
          ],
          [
            12.186944,
            -25.516123
          ],
          [
            12.787713,
            -25.965308
          ],
          [
            13.931781,
            -26.255557
          ],
          [
            15.075844,
            -26.10439
          ],
          [
            16.219912,
            -25.372035
          ],
          [
            16.716752,
            -24.372064
          ],
          [
            16.801546,
            -23.228003
          ],
          [
            16.497939,
            -22.083926
          ],
          [
            16.219912,
            -21.658333
          ],
          [
            15.075844,
            -20.806076
          ],
          [
            13.931781,
            -20.653849
          ],
          [
            12.787713,
            -20.887632
          ],
          [
            11.64365,
            -21.990167
          ],
          [
            10.896621,
            -22.083926
          ],
          [
            10.49958,
            -22.322127
          ],
          [
            10.11582,
            -19.79579
          ],
          [
            10.123439,
            -17.50767
          ],
          [
            10.49958,
            -16.262174
          ],
          [
            11.64365,
            -15.455382
          ],
          [
            12.787713,
            -16.556423
          ],
          [
            13.931781,
            -16.781478
          ],
          [
            15.075844,
            -16.589883
          ],
          [
            16.219912,
            -15.749745
          ],
          [
            16.574581,
            -15.219535
          ],
          [
            16.847435,
            -14.075476
          ],
          [
            16.580394,
            -12.931399
          ],
          [
            16.219912,
            -12.385802
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.108723234664545,
      "length": 26.21901951611725,
      "loops": [
        [
          [
            -16.822172,
            47.704086
          ],
          [
            -16.811855,
            -48.397442
          ],
          [
            -16.174639,
            -49.541512
          ],
          [
            -15.81393,
            -49.778586
          ],
          [
            -14.669864,
            -49.89702
          ],
          [
            8.211453,
            -49.825333
          ],
          [
            8.883519,
            -49.541512
          ],
          [
            9.355516,
            -49.096413
          ],
          [
            9.660598,
            -48.397442
          ],
          [
            9.690822,
            -47.253374
          ],
          [
            9.806467,
            -14.075476
          ],
          [
            9.727967,
            42.351482
          ],
          [
            9.687135,
            47.704086
          ],
          [
            9.489741,
            48.848144
          ],
          [
            8.211453,
            49.769378
          ],
          [
            7.067385,
            49.812937
          ],
          [
            -11.237667,
            49.831381
          ],
          [
            -14.669864,
            49.738301
          ],
          [
            -15.81393,
            49.452136
          ],
          [
            -16.494048,
            48.848144
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.736308865,
    -0.021308295000000005,
    0.12734763999999998
  ],
  "construction_scale": 231.9848187278746,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
