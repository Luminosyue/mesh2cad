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
      "start": -6.726095942146889,
      "length": 0.8155534004615516,
      "loops": [
        [
          [
            -49.77975,
            9.211067
          ],
          [
            -49.725102,
            -16.831624
          ],
          [
            -49.605991,
            -17.900908
          ],
          [
            -49.104529,
            -18.302276
          ],
          [
            11.278481,
            -18.297524
          ],
          [
            25.112404,
            -18.055865
          ],
          [
            47.678362,
            -17.933515
          ],
          [
            48.681295,
            -17.771951
          ],
          [
            49.084308,
            -17.111378
          ],
          [
            49.209728,
            -1.718222
          ],
          [
            49.112914,
            13.482643
          ],
          [
            48.9464,
            17.086745
          ],
          [
            48.630069,
            17.588208
          ],
          [
            48.179828,
            17.735703
          ],
          [
            45.090015,
            17.973319
          ],
          [
            33.38659,
            18.180371
          ],
          [
            11.38914,
            18.147401
          ],
          [
            0.596533,
            17.893093
          ],
          [
            -1.273539,
            18.089675
          ],
          [
            -12.497527,
            18.339096
          ],
          [
            -39.325946,
            18.465442
          ],
          [
            -48.336486,
            18.09899
          ],
          [
            -49.104529,
            17.661522
          ],
          [
            -49.30955,
            17.086745
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.910811585523024,
      "length": 6.114901718516676,
      "loops": [
        [
          [
            -49.121281,
            -18.530952
          ],
          [
            -49.603298,
            -18.266591
          ],
          [
            -49.742274,
            -18.015859
          ],
          [
            -49.912724,
            -17.012927
          ],
          [
            -49.994691,
            6.611093
          ],
          [
            -49.49458,
            17.086745
          ],
          [
            -49.260599,
            17.838944
          ],
          [
            -48.853793,
            18.169405
          ],
          [
            -48.101594,
            18.315721
          ],
          [
            -38.628879,
            18.585004
          ],
          [
            -13.304857,
            18.442956
          ],
          [
            0.039117,
            18.188324
          ],
          [
            14.777225,
            18.371194
          ],
          [
            39.349045,
            18.275521
          ],
          [
            48.430559,
            17.913779
          ],
          [
            48.932027,
            17.752949
          ],
          [
            49.356724,
            17.086745
          ],
          [
            49.829245,
            9.314023
          ],
          [
            49.586107,
            -5.980681
          ],
          [
            49.689127,
            -11.998269
          ],
          [
            49.533303,
            -17.012927
          ],
          [
            49.228111,
            -17.765126
          ],
          [
            48.681295,
            -18.189615
          ],
          [
            45.366635,
            -18.352443
          ],
          [
            10.765499,
            -18.58482
          ]
        ],
        [
          [
            -49.130832,
            8.311093
          ],
          [
            -49.142159,
            -16.707063
          ],
          [
            -49.078934,
            -17.514393
          ],
          [
            -48.853793,
            -17.690394
          ],
          [
            47.372499,
            -17.522746
          ],
          [
            48.430559,
            -17.327102
          ],
          [
            48.712931,
            -16.762194
          ],
          [
            48.755626,
            2.794969
          ],
          [
            48.931867,
            9.81549
          ],
          [
            48.701578,
            16.334543
          ],
          [
            48.618056,
            16.836009
          ],
          [
            48.179828,
            17.1593
          ],
          [
            44.614437,
            17.318009
          ],
          [
            1.543514,
            17.257196
          ],
          [
            -1.46528,
            17.383943
          ],
          [
            -48.35233,
            17.482083
          ],
          [
            -48.603061,
            17.339335
          ],
          [
            -48.672501,
            17.086745
          ],
          [
            -48.892862,
            10.818423
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.20382108915596664,
      "length": 6.52254389682861,
      "loops": [
        [
          [
            -37.998021,
            18.099057
          ],
          [
            46.675431,
            17.792859
          ],
          [
            48.179828,
            17.717517
          ],
          [
            48.932027,
            17.453157
          ],
          [
            49.23728,
            17.086745
          ],
          [
            49.389856,
            16.334543
          ],
          [
            49.408957,
            -16.260729
          ],
          [
            49.133803,
            -17.367837
          ],
          [
            48.430559,
            -17.946606
          ],
          [
            47.42763,
            -18.218638
          ],
          [
            41.911506,
            -18.33662
          ],
          [
            -40.505349,
            -18.343925
          ],
          [
            -48.853793,
            -18.199307
          ],
          [
            -49.355259,
            -17.841757
          ],
          [
            -49.530149,
            -17.26366
          ],
          [
            -49.429408,
            -16.511462
          ],
          [
            -49.607991,
            9.564758
          ],
          [
            -49.494714,
            17.086745
          ],
          [
            -49.093985,
            17.819113
          ],
          [
            -48.528802,
            18.024501
          ]
        ],
        [
          [
            -31.098681,
            17.335466
          ],
          [
            9.566966,
            16.956121
          ],
          [
            46.675431,
            16.97921
          ],
          [
            47.929097,
            16.946616
          ],
          [
            48.430559,
            16.786759
          ],
          [
            48.582608,
            16.334543
          ],
          [
            48.669647,
            5.478772
          ],
          [
            48.559295,
            -16.260729
          ],
          [
            48.340028,
            -17.012927
          ],
          [
            47.42763,
            -17.38745
          ],
          [
            45.997492,
            -17.480339
          ],
          [
            -14.252657,
            -17.54674
          ],
          [
            -46.095731,
            -17.449632
          ],
          [
            -48.35233,
            -17.397574
          ],
          [
            -48.652804,
            -17.26366
          ],
          [
            -48.535461,
            -4.550544
          ],
          [
            -48.740732,
            9.564758
          ],
          [
            -48.54964,
            17.086745
          ],
          [
            -48.027335,
            17.232861
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.31526202999999997,
    -0.139837285,
    -0.0077821500000000154
  ],
  "construction_scale": 101.68335161667784,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
