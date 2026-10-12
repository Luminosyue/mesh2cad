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
      "start": -46.29059412408841,
      "length": 19.640285494590348,
      "loops": [
        [
          [
            44.439177,
            -46.768721
          ],
          [
            20.747007,
            -46.827024
          ],
          [
            16.419546,
            -46.146866
          ],
          [
            13.899804,
            -46.951108
          ],
          [
            11.900251,
            -47.168615
          ],
          [
            -9.984201,
            -46.902708
          ],
          [
            -11.791919,
            -46.812337
          ],
          [
            -15.215521,
            -46.076015
          ],
          [
            -17.849959,
            -46.99171
          ],
          [
            -20.638674,
            -47.247437
          ],
          [
            -41.61927,
            -47.130056
          ],
          [
            -45.256501,
            -46.985092
          ],
          [
            -46.138563,
            -46.716056
          ],
          [
            -47.099393,
            -46.087849
          ],
          [
            -47.754448,
            -45.002516
          ],
          [
            -47.950236,
            -42.664246
          ],
          [
            -47.433454,
            21.701582
          ],
          [
            -47.099968,
            46.105777
          ],
          [
            -47.013713,
            47.009634
          ],
          [
            -46.722791,
            47.913495
          ],
          [
            -45.954895,
            48.817352
          ],
          [
            -44.139011,
            49.456571
          ],
          [
            -40.523573,
            49.542831
          ],
          [
            -20.638674,
            49.445014
          ],
          [
            -16.11938,
            48.94003
          ],
          [
            -13.407803,
            49.712521
          ],
          [
            -9.984201,
            49.828584
          ],
          [
            11.900251,
            49.320377
          ],
          [
            13.707969,
            49.172067
          ],
          [
            16.419546,
            48.571819
          ],
          [
            18.93929,
            49.08688
          ],
          [
            20.938841,
            49.175864
          ],
          [
            43.53532,
            49.069188
          ],
          [
            45.343038,
            48.913482
          ],
          [
            46.246895,
            48.672153
          ],
          [
            47.276107,
            47.913495
          ],
          [
            47.744722,
            47.009634
          ],
          [
            47.951125,
            46.105777
          ],
          [
            48.06223,
            43.394197
          ],
          [
            47.588058,
            -3.798307
          ],
          [
            47.44804,
            -40.664693
          ],
          [
            47.257245,
            -44.280129
          ],
          [
            46.920807,
            -45.183992
          ],
          [
            46.246895,
            -46.059475
          ],
          [
            45.343038,
            -46.561861
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 26.652160253263027,
      "length": 19.640285494590344,
      "loops": [
        [
          [
            47.042935,
            9.047555
          ],
          [
            46.591238,
            -46.087849
          ],
          [
            46.311307,
            -47.895567
          ],
          [
            45.343038,
            -49.212115
          ],
          [
            44.439177,
            -49.741348
          ],
          [
            43.53532,
            -49.936863
          ],
          [
            20.938841,
            -49.695783
          ],
          [
            18.575549,
            -49.578015
          ],
          [
            16.419546,
            -49.245668
          ],
          [
            12.80411,
            -49.705308
          ],
          [
            -1.657635,
            -49.656451
          ],
          [
            -11.600085,
            -49.470476
          ],
          [
            -15.215521,
            -48.983936
          ],
          [
            -18.830957,
            -49.662715
          ],
          [
            -20.638674,
            -49.757235
          ],
          [
            -34.752137,
            -49.546972
          ],
          [
            -44.139011,
            -49.574822
          ],
          [
            -45.946729,
            -49.43457
          ],
          [
            -47.153194,
            -48.799424
          ],
          [
            -47.845644,
            -47.895567
          ],
          [
            -48.162517,
            -46.99171
          ],
          [
            -48.271669,
            -45.183992
          ],
          [
            -47.556844,
            15.722852
          ],
          [
            -47.410197,
            44.298057
          ],
          [
            -47.195526,
            47.009634
          ],
          [
            -46.888339,
            47.913495
          ],
          [
            -46.114534,
            48.817352
          ],
          [
            -44.694585,
            49.428316
          ],
          [
            -41.98301,
            49.604238
          ],
          [
            -20.290391,
            49.437573
          ],
          [
            -17.927098,
            49.292469
          ],
          [
            -15.215521,
            48.759346
          ],
          [
            -12.503944,
            49.509859
          ],
          [
            -7.636365,
            49.682122
          ],
          [
            11.900251,
            49.300216
          ],
          [
            13.707969,
            49.05939
          ],
          [
            15.515687,
            48.402699
          ],
          [
            16.419546,
            48.315712
          ],
          [
            18.227264,
            48.76099
          ],
          [
            20.034982,
            48.891487
          ],
          [
            42.631458,
            48.68825
          ],
          [
            45.343038,
            48.411228
          ],
          [
            46.326678,
            47.913495
          ],
          [
            47.150752,
            46.879324
          ],
          [
            47.431362,
            46.105777
          ],
          [
            47.551879,
            44.646341
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.005750524999999979,
    0.014746015000000001,
    -0.35100069500000003
  ],
  "construction_scale": 183.27756105511645,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
