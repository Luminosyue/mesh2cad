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
      "start": -0.44222851682388487,
      "length": 0.8844570336477697,
      "loops": [
        [
          [
            -0.388207,
            -49.972796
          ],
          [
            5.708781,
            -48.894943
          ],
          [
            14.915836,
            -45.095274
          ],
          [
            22.737211,
            -41.350792
          ],
          [
            26.504817,
            -39.016547
          ],
          [
            31.701791,
            -34.613525
          ],
          [
            34.338495,
            -31.933129
          ],
          [
            37.541636,
            -27.769535
          ],
          [
            40.415666,
            -23.034553
          ],
          [
            42.082406,
            -19.666638
          ],
          [
            44.467114,
            -14.097248
          ],
          [
            46.369097,
            -7.80168
          ],
          [
            46.879895,
            -3.171454
          ],
          [
            46.91944,
            3.237413
          ],
          [
            46.733541,
            5.799611
          ],
          [
            46.398884,
            7.578251
          ],
          [
            44.639697,
            12.497867
          ],
          [
            40.657324,
            21.758321
          ],
          [
            39.396086,
            24.056362
          ],
          [
            37.811164,
            26.4099
          ],
          [
            35.206663,
            29.458096
          ],
          [
            31.733992,
            33.02025
          ],
          [
            26.632762,
            37.632421
          ],
          [
            14.94942,
            45.014568
          ],
          [
            10.319193,
            47.330922
          ],
          [
            5.731271,
            49.103931
          ],
          [
            3.952631,
            49.512231
          ],
          [
            -0.098818,
            49.98816
          ],
          [
            -6.354383,
            49.17146
          ],
          [
            -8.930357,
            48.28638
          ],
          [
            -13.067048,
            46.240869
          ],
          [
            -17.139654,
            43.970767
          ],
          [
            -22.942415,
            40.208036
          ],
          [
            -26.986879,
            37.29279
          ],
          [
            -31.642238,
            33.221328
          ],
          [
            -37.06144,
            27.21441
          ],
          [
            -40.034527,
            22.623921
          ],
          [
            -43.272079,
            15.349454
          ],
          [
            -46.111697,
            8.037819
          ],
          [
            -46.651123,
            6.131305
          ],
          [
            -46.941445,
            2.90572
          ],
          [
            -46.826817,
            -1.14573
          ],
          [
            -46.275445,
            -7.512292
          ],
          [
            -45.418261,
            -11.853129
          ],
          [
            -44.375362,
            -15.444737
          ],
          [
            -40.944956,
            -22.560529
          ],
          [
            -37.140633,
            -28.396364
          ],
          [
            -33.957351,
            -32.735276
          ],
          [
            -30.484683,
            -35.949255
          ],
          [
            -25.854455,
            -39.581355
          ],
          [
            -23.539341,
            -41.059027
          ],
          [
            -20.656057,
            -42.528381
          ],
          [
            -12.253163,
            -46.315418
          ],
          [
            -4.150267,
            -49.093786
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    0.0008420050000000068,
    -0.06421210499999999,
    -0.01443445
  ],
  "construction_scale": 117.3602070055664,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
