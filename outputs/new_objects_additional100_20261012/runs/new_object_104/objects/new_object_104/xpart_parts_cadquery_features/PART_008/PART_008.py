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
  "operation": "extrude",
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
      "start": -30.181893138146282,
      "length": 60.363786276292565,
      "loops": [
        [
          [
            -42.559995,
            -13.649505
          ],
          [
            -44.373603,
            -18.879664
          ],
          [
            -49.035481,
            -30.570611
          ],
          [
            -49.950265,
            -33.401338
          ],
          [
            -49.870605,
            -34.016651
          ],
          [
            -49.475605,
            -34.500782
          ],
          [
            -45.168414,
            -35.898135
          ],
          [
            -44.5531,
            -35.709009
          ],
          [
            -44.048866,
            -34.93962
          ],
          [
            -35.330367,
            -9.711787
          ],
          [
            -27.760204,
            10.593542
          ],
          [
            -15.879228,
            18.028339
          ],
          [
            -5.78838,
            24.068447
          ],
          [
            0.364749,
            28.370176
          ],
          [
            16.362886,
            18.320256
          ],
          [
            28.669148,
            11.517191
          ],
          [
            28.954835,
            11.208856
          ],
          [
            36.634966,
            -8.198645
          ],
          [
            40.15172,
            -18.941482
          ],
          [
            43.218322,
            -27.18639
          ],
          [
            44.667283,
            -33.087485
          ],
          [
            45.282597,
            -33.451478
          ],
          [
            47.436195,
            -33.028463
          ],
          [
            49.589788,
            -31.964048
          ],
          [
            49.902521,
            -31.555398
          ],
          [
            49.261615,
            -26.878734
          ],
          [
            48.666818,
            -24.158043
          ],
          [
            38.360956,
            3.209785
          ],
          [
            32.513294,
            16.131358
          ],
          [
            31.745713,
            16.804732
          ],
          [
            23.152404,
            21.672864
          ],
          [
            12.363352,
            28.297813
          ],
          [
            7.26872,
            32.098951
          ],
          [
            2.602865,
            35.17438
          ],
          [
            -0.22426,
            36.131104
          ],
          [
            -2.096502,
            35.570239
          ],
          [
            -3.327128,
            34.884142
          ],
          [
            -10.485019,
            29.360589
          ],
          [
            -20.863548,
            21.891367
          ],
          [
            -28.55496,
            17.503913
          ],
          [
            -30.59345,
            16.131358
          ],
          [
            -31.580499,
            14.28542
          ],
          [
            -33.627465,
            9.424733
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.005389229999999995,
    0.213458625,
    -0.019231099999999987
  ],
  "construction_scale": 124.76841734057415,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
