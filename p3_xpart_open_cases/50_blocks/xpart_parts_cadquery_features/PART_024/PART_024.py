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
      -0.8365520872001294,
      0.5478292559004473,
      0.00798196596520345
    ],
    [
      0.5478387371805116,
      0.8365831803638559,
      -0.0011403406329183545
    ],
    [
      -0.007302290433130665,
      0.0034188758180079127,
      -0.9999674933929461
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.008554916881636,
      "length": 99.80175911016094,
      "loops": [
        [
          [
            -1.721533,
            17.434528
          ],
          [
            10.027272,
            23.598557
          ],
          [
            11.547273,
            23.862985
          ],
          [
            12.733002,
            23.685252
          ],
          [
            13.624091,
            23.12218
          ],
          [
            14.489852,
            21.936063
          ],
          [
            21.419181,
            4.800596
          ],
          [
            21.528103,
            3.469488
          ],
          [
            21.35803,
            2.321076
          ],
          [
            19.938267,
            -1.863884
          ],
          [
            20.33529,
            -3.181401
          ],
          [
            22.050488,
            -4.409824
          ],
          [
            22.779768,
            -5.219978
          ],
          [
            23.524091,
            -6.656063
          ],
          [
            24.266142,
            -8.721585
          ],
          [
            24.499121,
            -9.814125
          ],
          [
            24.454132,
            -11.044447
          ],
          [
            24.05761,
            -13.304358
          ],
          [
            23.538755,
            -14.224378
          ],
          [
            22.573991,
            -14.852393
          ],
          [
            15.900362,
            -17.648629
          ],
          [
            10.915479,
            -19.489261
          ],
          [
            4.946946,
            -22.206255
          ],
          [
            2.466996,
            -22.771284
          ],
          [
            1.415599,
            -22.453002
          ],
          [
            0.881035,
            -21.345516
          ],
          [
            0.715484,
            -13.903238
          ],
          [
            0.878399,
            -9.806929
          ],
          [
            -0.261984,
            -9.624531
          ],
          [
            -2.163252,
            -9.991491
          ],
          [
            -20.914513,
            -16.121718
          ],
          [
            -22.323004,
            -16.379039
          ],
          [
            -23.574212,
            -16.365869
          ],
          [
            -24.563846,
            -15.953273
          ],
          [
            -25.405531,
            -15.314766
          ],
          [
            -26.051607,
            -14.377558
          ],
          [
            -27.556658,
            -10.904467
          ],
          [
            -32.841612,
            2.186843
          ],
          [
            -33.104242,
            3.971021
          ],
          [
            -32.288108,
            5.956153
          ],
          [
            -30.727048,
            7.453479
          ],
          [
            -28.815549,
            8.72132
          ],
          [
            -23.386206,
            11.352663
          ],
          [
            -5.399222,
            15.234955
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    0.04337012,
    0.17781486000000002,
    -0.07891535000000001
  ],
  "construction_scale": 213.70475790135941,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
