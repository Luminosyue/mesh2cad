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
      "start": -27.062593630641807,
      "length": 54.125187261283614,
      "loops": [
        [
          [
            -34.967935,
            -48.182126
          ],
          [
            -34.411525,
            3.441459
          ],
          [
            -34.041016,
            8.420383
          ],
          [
            -33.382107,
            11.564968
          ],
          [
            -30.170166,
            20.73667
          ],
          [
            -27.971702,
            24.405353
          ],
          [
            -26.992267,
            27.025839
          ],
          [
            -24.209572,
            31.218616
          ],
          [
            -21.395387,
            33.797857
          ],
          [
            -19.908112,
            35.935493
          ],
          [
            -17.731226,
            38.1038
          ],
          [
            -16.702752,
            39.604174
          ],
          [
            -11.704108,
            44.638052
          ],
          [
            -6.201085,
            48.313466
          ],
          [
            -3.318549,
            49.595856
          ],
          [
            -0.173966,
            49.877785
          ],
          [
            2.446521,
            49.750229
          ],
          [
            4.280861,
            49.243553
          ],
          [
            5.853154,
            48.448302
          ],
          [
            12.615985,
            44.059
          ],
          [
            15.344378,
            41.678315
          ],
          [
            17.999001,
            38.818028
          ],
          [
            22.123049,
            35.414121
          ],
          [
            23.672463,
            33.70624
          ],
          [
            26.817045,
            28.084255
          ],
          [
            28.685128,
            23.881255
          ],
          [
            29.811663,
            21.810415
          ],
          [
            30.389957,
            20.212573
          ],
          [
            31.519811,
            15.757746
          ],
          [
            32.909933,
            12.089064
          ],
          [
            34.009963,
            7.896286
          ],
          [
            34.292792,
            4.751702
          ],
          [
            34.961681,
            1.083021
          ],
          [
            35.040589,
            -35.603791
          ],
          [
            34.748174,
            -42.941154
          ],
          [
            35.041476,
            -48.156576
          ],
          [
            34.8505,
            -49.492371
          ],
          [
            34.15441,
            -49.905892
          ],
          [
            32.844166,
            -49.978613
          ],
          [
            -31.357756,
            -49.949977
          ],
          [
            -33.716193,
            -49.897622
          ],
          [
            -34.502343,
            -49.614106
          ],
          [
            -34.817484,
            -49.230323
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.0008288399999999974,
    0.012001394999999998,
    -0.002225394999999991
  ],
  "construction_scale": 106.27240906511726,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
