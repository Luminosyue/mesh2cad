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
      "start": -7.909990332835612,
      "length": 2.3972831671392565,
      "loops": [
        [
          [
            -45.577572,
            7.010373
          ],
          [
            48.23008,
            7.011699
          ],
          [
            48.919845,
            7.050238
          ],
          [
            49.60961,
            7.305821
          ],
          [
            49.817612,
            7.999362
          ],
          [
            49.60961,
            8.413566
          ],
          [
            48.919845,
            8.777989
          ],
          [
            46.850559,
            8.863988
          ],
          [
            -42.818521,
            8.876511
          ],
          [
            -48.336615,
            8.789358
          ],
          [
            -49.048319,
            8.689125
          ],
          [
            -49.591533,
            7.999362
          ],
          [
            -49.2471,
            7.3096
          ],
          [
            -49.02638,
            7.187909
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.513023565309669,
      "length": 0.9591031066236907,
      "loops": [
        [
          [
            48.919845,
            8.926715
          ],
          [
            -46.267332,
            9.036988
          ],
          [
            -49.02638,
            8.93015
          ],
          [
            -49.716145,
            8.653047
          ],
          [
            -49.994358,
            7.999362
          ],
          [
            -49.716145,
            7.254854
          ],
          [
            -47.548048,
            6.619836
          ],
          [
            -47.393461,
            -7.175406
          ],
          [
            -47.112784,
            -8.070769
          ],
          [
            -46.267332,
            -8.440849
          ],
          [
            45.471037,
            -8.535574
          ],
          [
            46.160797,
            -8.45164
          ],
          [
            46.850559,
            -8.051721
          ],
          [
            47.060977,
            -7.175406
          ],
          [
            47.025758,
            5.930076
          ],
          [
            47.153498,
            6.619836
          ],
          [
            47.540324,
            6.863947
          ],
          [
            48.919845,
            6.916358
          ],
          [
            49.60961,
            7.152319
          ],
          [
            49.983934,
            7.999362
          ],
          [
            49.60961,
            8.725987
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.554236858299292,
      "length": 7.670610055696333,
      "loops": [
        [
          [
            -46.93111,
            9.006256
          ],
          [
            45.497021,
            9.02989
          ],
          [
            48.919845,
            8.909291
          ],
          [
            49.60961,
            8.676133
          ],
          [
            49.896282,
            7.999362
          ],
          [
            49.60961,
            7.228499
          ],
          [
            48.919845,
            6.922331
          ],
          [
            47.540324,
            6.837041
          ],
          [
            47.231338,
            6.619836
          ],
          [
            47.037307,
            5.930076
          ],
          [
            47.148409,
            -7.839184
          ],
          [
            46.542301,
            -8.55493
          ],
          [
            45.471037,
            -8.883769
          ],
          [
            -45.613281,
            -8.823403
          ],
          [
            -46.267332,
            -8.798592
          ],
          [
            -47.007821,
            -8.528946
          ],
          [
            -47.496641,
            -7.865168
          ],
          [
            -47.534211,
            -7.175406
          ],
          [
            -47.4507,
            5.930076
          ],
          [
            -47.646859,
            6.712276
          ],
          [
            -49.02638,
            6.942802
          ],
          [
            -49.712364,
            7.3096
          ],
          [
            -49.907234,
            7.999362
          ],
          [
            -49.535026,
            8.689125
          ],
          [
            -49.02638,
            8.905111
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 3.1160567977837275,
      "length": 3.8354632276548224,
      "loops": [
        [
          [
            -45.913669,
            6.831998
          ],
          [
            48.23008,
            6.873619
          ],
          [
            48.919845,
            6.910926
          ],
          [
            49.60961,
            7.218953
          ],
          [
            49.895545,
            7.999362
          ],
          [
            49.60961,
            8.65429
          ],
          [
            48.919845,
            8.912618
          ],
          [
            46.514461,
            9.009392
          ],
          [
            -9.020174,
            9.053295
          ],
          [
            -46.957094,
            8.999891
          ],
          [
            -49.02638,
            8.891587
          ],
          [
            -49.479355,
            8.689125
          ],
          [
            -49.882297,
            7.999362
          ],
          [
            -49.69077,
            7.3096
          ],
          [
            -49.02638,
            6.932663
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 6.9512036258252365,
      "length": 0.9591031066236889,
      "loops": [
        [
          [
            46.850559,
            7.030009
          ],
          [
            -46.267332,
            7.020604
          ],
          [
            -48.336615,
            7.087672
          ],
          [
            -49.02638,
            7.267983
          ],
          [
            -49.326034,
            7.999362
          ],
          [
            -49.02638,
            8.425379
          ],
          [
            -48.479982,
            8.710543
          ],
          [
            -45.796358,
            8.827496
          ],
          [
            -2.812316,
            8.851897
          ],
          [
            45.942011,
            8.808565
          ],
          [
            48.411618,
            8.689125
          ],
          [
            48.919845,
            8.494231
          ],
          [
            49.37034,
            7.999362
          ],
          [
            48.919845,
            7.24212
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.00019042499999999407,
    -0.05818664,
    -0.154711435
  ],
  "construction_scale": 279.7292858295941,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
