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
      "start": -5.1889848331188215,
      "length": 5.346434357152114,
      "loops": [
        [
          [
            39.992322,
            48.525681
          ],
          [
            39.442265,
            -0.028438
          ],
          [
            39.140174,
            -7.63242
          ],
          [
            39.21645,
            -38.694685
          ],
          [
            39.124449,
            -48.776296
          ],
          [
            38.922661,
            -49.581148
          ],
          [
            38.377708,
            -49.781262
          ],
          [
            24.208955,
            -49.734499
          ],
          [
            -19.932158,
            -49.391286
          ],
          [
            -39.550431,
            -49.005765
          ],
          [
            -39.780667,
            -48.503821
          ],
          [
            -39.566909,
            -42.509348
          ],
          [
            -39.586584,
            -31.61031
          ],
          [
            -39.265773,
            -25.615838
          ],
          [
            -39.550431,
            -18.675568
          ],
          [
            -39.274713,
            -13.626893
          ],
          [
            -39.076425,
            -13.354417
          ],
          [
            -38.513289,
            -10.35718
          ],
          [
            -38.224937,
            -7.124354
          ],
          [
            -38.290082,
            -5.827119
          ],
          [
            -38.860467,
            -3.272804
          ],
          [
            -39.066096,
            -0.275568
          ],
          [
            -38.796954,
            15.255565
          ],
          [
            -39.112285,
            26.592752
          ],
          [
            -39.123303,
            34.601363
          ],
          [
            -39.012425,
            46.045355
          ],
          [
            -38.733003,
            49.456434
          ],
          [
            -38.188052,
            49.686271
          ],
          [
            -36.159142,
            49.70912
          ],
          [
            39.195136,
            49.398175
          ],
          [
            39.740089,
            49.303268
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.15724196463996698,
      "length": 5.031950427872185,
      "loops": [
        [
          [
            -0.072718,
            47.952684
          ],
          [
            1.634144,
            41.685737
          ],
          [
            1.447718,
            41.140784
          ],
          [
            1.048494,
            40.850494
          ],
          [
            -6.362795,
            38.779222
          ],
          [
            -9.57807,
            38.211546
          ],
          [
            -9.975026,
            38.416026
          ],
          [
            -10.43565,
            39.287891
          ],
          [
            -11.911197,
            43.593071
          ],
          [
            -12.209837,
            45.227927
          ],
          [
            -12.030354,
            45.552519
          ],
          [
            -11.485402,
            45.896656
          ],
          [
            -0.858837,
            48.698854
          ],
          [
            -0.387567,
            48.497637
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.15724196463996698,
      "length": 5.031950427872185,
      "loops": [
        [
          [
            -26.129067,
            -35.697448
          ],
          [
            -26.155828,
            -41.69192
          ],
          [
            -25.654154,
            -42.278331
          ],
          [
            -15.027589,
            -42.605835
          ],
          [
            -14.210162,
            -42.494421
          ],
          [
            -13.74227,
            -41.964395
          ],
          [
            -13.630505,
            -35.697448
          ],
          [
            -13.827171,
            -35.152495
          ],
          [
            -14.210162,
            -34.945625
          ],
          [
            -25.654154,
            -34.989737
          ],
          [
            -25.933431,
            -35.152495
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    2.7980000000010774e-05,
    -0.452878235,
    0.042293685
  ],
  "construction_scale": 110.50116188656689,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
