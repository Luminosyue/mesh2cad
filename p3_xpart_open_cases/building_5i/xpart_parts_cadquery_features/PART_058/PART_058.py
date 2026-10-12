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
      "start": -18.4088301305146,
      "length": 36.817660261029204,
      "loops": [
        [
          [
            -18.344962,
            32.486825
          ],
          [
            -15.117702,
            28.038198
          ],
          [
            -10.811526,
            22.605696
          ],
          [
            -1.504347,
            13.159302
          ],
          [
            2.234414,
            9.758616
          ],
          [
            4.864158,
            7.785381
          ],
          [
            14.533509,
            1.340428
          ],
          [
            14.419322,
            0.846025
          ],
          [
            10.37787,
            -1.298456
          ],
          [
            6.406105,
            -3.729017
          ],
          [
            1.97077,
            -7.064426
          ],
          [
            -2.576954,
            -11.514054
          ],
          [
            -8.750021,
            -18.435698
          ],
          [
            -12.969559,
            -24.368537
          ],
          [
            -18.958454,
            -34.256601
          ],
          [
            -27.390043,
            -47.11108
          ],
          [
            -28.19317,
            -48.594293
          ],
          [
            -28.171885,
            -49.088693
          ],
          [
            -27.21331,
            -49.975982
          ],
          [
            -26.224506,
            -49.31687
          ],
          [
            -19.994213,
            -42.661454
          ],
          [
            -4.470765,
            -23.92796
          ],
          [
            -0.021138,
            -19.18667
          ],
          [
            4.040286,
            -15.963682
          ],
          [
            17.150953,
            -6.570023
          ],
          [
            27.799068,
            1.340428
          ],
          [
            28.213424,
            1.834831
          ],
          [
            27.665437,
            2.521267
          ],
          [
            22.72141,
            5.664643
          ],
          [
            14.810958,
            9.454853
          ],
          [
            11.84454,
            11.095421
          ],
          [
            4.428495,
            16.2831
          ],
          [
            0.221453,
            19.645689
          ],
          [
            -2.493148,
            22.00418
          ],
          [
            -4.904079,
            24.577377
          ],
          [
            -12.875618,
            33.825533
          ],
          [
            -19.869818,
            42.375891
          ],
          [
            -26.718906,
            49.696026
          ],
          [
            -27.21331,
            49.990306
          ],
          [
            -27.678896,
            49.791939
          ],
          [
            -28.11068,
            49.297534
          ],
          [
            -28.183769,
            48.80313
          ],
          [
            -21.718177,
            38.420664
          ],
          [
            -20.215518,
            35.454247
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    0.27149436,
    0.675845595,
    0.0014242350000000237
  ],
  "construction_scale": 100.25125470710968,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
