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
      "start": -48.82298022158383,
      "length": 97.64596044316767,
      "loops": [
        [
          [
            -0.387224,
            27.198928
          ],
          [
            7.575807,
            19.154853
          ],
          [
            8.320803,
            18.891807
          ],
          [
            9.065795,
            19.151513
          ],
          [
            9.810792,
            18.698494
          ],
          [
            18.005741,
            9.102951
          ],
          [
            18.750738,
            8.627849
          ],
          [
            21.73072,
            8.385003
          ],
          [
            23.550259,
            6.639388
          ],
          [
            27.719439,
            2.048086
          ],
          [
            22.04584,
            -3.911876
          ],
          [
            20.985723,
            -4.22569
          ],
          [
            18.750738,
            -4.203487
          ],
          [
            18.125198,
            -4.656872
          ],
          [
            10.555789,
            -14.032033
          ],
          [
            9.065795,
            -13.770235
          ],
          [
            8.382272,
            -14.341811
          ],
          [
            -1.364139,
            -26.205101
          ],
          [
            -2.109133,
            -26.420602
          ],
          [
            -2.854127,
            -26.090529
          ],
          [
            -3.626416,
            -26.261736
          ],
          [
            -13.648638,
            -38.181661
          ],
          [
            -14.029058,
            -38.548127
          ],
          [
            -14.774056,
            -38.258281
          ],
          [
            -15.519049,
            -37.628904
          ],
          [
            -16.264044,
            -37.942872
          ],
          [
            -24.400242,
            -45.631616
          ],
          [
            -27.955483,
            -48.611595
          ],
          [
            -27.771583,
            -49.356592
          ],
          [
            -27.438975,
            -49.593972
          ],
          [
            -26.693979,
            -49.349458
          ],
          [
            -22.810975,
            -46.019386
          ],
          [
            -16.264044,
            -39.693897
          ],
          [
            -15.519049,
            -39.228695
          ],
          [
            -14.774056,
            -39.864909
          ],
          [
            -14.029058,
            -40.084438
          ],
          [
            -13.284064,
            -39.584356
          ],
          [
            -3.599124,
            -28.240651
          ],
          [
            -2.854127,
            -27.621613
          ],
          [
            -2.109133,
            -27.962883
          ],
          [
            -1.364139,
            -28.005576
          ],
          [
            -0.619142,
            -27.320253
          ],
          [
            4.534299,
            -20.848751
          ],
          [
            9.065795,
            -15.523603
          ],
          [
            9.810792,
            -15.184996
          ],
          [
            10.555789,
            -15.489806
          ],
          [
            11.330801,
            -15.086806
          ],
          [
            18.750738,
            -5.838345
          ],
          [
            19.495729,
            -5.32641
          ],
          [
            21.73072,
            -5.443301
          ],
          [
            22.475711,
            -5.087526
          ],
          [
            28.817775,
            1.303091
          ],
          [
            29.272868,
            2.048086
          ],
          [
            28.953047,
            2.793081
          ],
          [
            28.435675,
            3.367148
          ],
          [
            22.475711,
            9.391566
          ],
          [
            21.73072,
            9.667976
          ],
          [
            19.495729,
            9.68354
          ],
          [
            18.750738,
            10.028548
          ],
          [
            10.402075,
            19.927974
          ],
          [
            9.810792,
            20.428929
          ],
          [
            9.065795,
            20.629616
          ],
          [
            8.320803,
            20.431297
          ],
          [
            7.575807,
            20.700771
          ],
          [
            1.109331,
            27.377926
          ],
          [
            -8.069097,
            35.444359
          ],
          [
            -15.787339,
            41.532839
          ],
          [
            -22.969003,
            47.555898
          ],
          [
            -26.693979,
            49.946551
          ],
          [
            -27.510399,
            49.727788
          ],
          [
            -27.588493,
            48.982791
          ],
          [
            -26.693979,
            48.075878
          ],
          [
            -25.203988,
            47.659024
          ],
          [
            -24.458992,
            47.209968
          ],
          [
            -7.540245,
            33.502535
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "center": [
    -0.15521427499999998,
    0.609857225,
    0.051790844999999974
  ],
  "construction_scale": 75.53219969018656,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
