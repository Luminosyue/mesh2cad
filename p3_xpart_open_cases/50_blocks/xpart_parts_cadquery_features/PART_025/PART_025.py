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
      0.11284854513870636,
      0.9936066596316008,
      0.003318402599128849
    ],
    [
      0.9936121658635122,
      -0.11284879924145891,
      -0.00011116555698718715
    ],
    [
      0.00026402291096730147,
      0.0033097500651030616,
      -0.9999944879080134
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -49.98116203181253,
      "length": 99.9646984830475,
      "loops": [
        [
          [
            13.404579,
            -9.853842
          ],
          [
            15.564015,
            -9.697582
          ],
          [
            17.813271,
            -8.75047
          ],
          [
            20.165849,
            -6.89365
          ],
          [
            21.585918,
            -5.163815
          ],
          [
            22.720274,
            -3.150974
          ],
          [
            23.550597,
            -0.032761
          ],
          [
            23.4573,
            3.190349
          ],
          [
            22.141285,
            6.552328
          ],
          [
            21.484256,
            7.697788
          ],
          [
            20.504289,
            8.879925
          ],
          [
            18.965643,
            10.173356
          ],
          [
            17.891908,
            10.798964
          ],
          [
            16.863475,
            11.172385
          ],
          [
            14.752238,
            11.440497
          ],
          [
            12.03662,
            10.91247
          ],
          [
            10.318407,
            10.115774
          ],
          [
            8.853217,
            9.132346
          ],
          [
            4.426282,
            5.379653
          ],
          [
            3.326201,
            5.122241
          ],
          [
            2.308639,
            5.591376
          ],
          [
            1.352675,
            6.60287
          ],
          [
            -0.340172,
            9.105638
          ],
          [
            -1.43911,
            10.307451
          ],
          [
            -4.420804,
            12.339917
          ],
          [
            -6.480301,
            13.063594
          ],
          [
            -8.187313,
            13.389607
          ],
          [
            -11.811444,
            13.266802
          ],
          [
            -15.131701,
            12.318302
          ],
          [
            -17.536319,
            11.058674
          ],
          [
            -20.448835,
            8.176946
          ],
          [
            -21.614501,
            6.521231
          ],
          [
            -22.28395,
            5.172853
          ],
          [
            -22.993246,
            3.111735
          ],
          [
            -23.217112,
            -0.075354
          ],
          [
            -23.012022,
            -2.240323
          ],
          [
            -22.241004,
            -4.469567
          ],
          [
            -21.135081,
            -6.736849
          ],
          [
            -19.645512,
            -8.567669
          ],
          [
            -17.66741,
            -10.00801
          ],
          [
            -15.638541,
            -11.001348
          ],
          [
            -13.1758,
            -11.553647
          ],
          [
            -10.365859,
            -11.719275
          ],
          [
            -6.023886,
            -11.20336
          ],
          [
            -3.804385,
            -10.518233
          ],
          [
            -0.861699,
            -9.039379
          ],
          [
            1.430538,
            -7.158039
          ],
          [
            3.078874,
            -5.203571
          ],
          [
            3.895446,
            -3.154637
          ],
          [
            4.64322,
            -2.138772
          ],
          [
            5.515255,
            -3.889235
          ],
          [
            6.686985,
            -5.613359
          ],
          [
            8.848866,
            -8.000569
          ],
          [
            10.289294,
            -8.997604
          ],
          [
            11.30729,
            -9.46292
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.19463806,
    0.08106196,
    -0.076936595
  ],
  "construction_scale": 215.7492694891547,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
