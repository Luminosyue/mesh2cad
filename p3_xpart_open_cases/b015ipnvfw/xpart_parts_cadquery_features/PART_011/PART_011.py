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
      "start": -6.328301554508024,
      "length": 12.656603109016048,
      "loops": [
        [
          [
            49.5616,
            29.937557
          ],
          [
            1.250352,
            29.924823
          ],
          [
            -1.42147,
            29.772699
          ],
          [
            -1.011144,
            29.723526
          ],
          [
            -0.469714,
            29.018865
          ],
          [
            -0.752243,
            26.506093
          ],
          [
            -0.494122,
            24.998429
          ],
          [
            -0.928322,
            22.802937
          ],
          [
            -0.848858,
            20.290163
          ],
          [
            -0.622664,
            19.721606
          ],
          [
            -0.607146,
            18.7825
          ],
          [
            -1.011144,
            17.581565
          ],
          [
            -1.513698,
            17.713373
          ],
          [
            -1.770042,
            19.470328
          ],
          [
            -1.596347,
            22.988211
          ],
          [
            -1.955604,
            24.178594
          ],
          [
            -2.267531,
            24.485246
          ],
          [
            -2.743913,
            22.988211
          ],
          [
            -2.686681,
            19.721606
          ],
          [
            -3.035309,
            15.635165
          ],
          [
            -2.832723,
            13.756953
          ],
          [
            -2.518808,
            12.951232
          ],
          [
            -2.267531,
            12.729127
          ],
          [
            -2.016254,
            12.887867
          ],
          [
            -1.453736,
            14.127501
          ],
          [
            -1.011144,
            14.399651
          ],
          [
            -0.358126,
            12.24929
          ],
          [
            -0.081965,
            6.655185
          ],
          [
            -0.571561,
            -7.350341
          ],
          [
            -0.505191,
            -10.431673
          ],
          [
            -0.217692,
            -12.627164
          ],
          [
            -0.577111,
            -15.457218
          ],
          [
            -0.902582,
            -16.647602
          ],
          [
            -0.779936,
            -18.65782
          ],
          [
            -1.011144,
            -19.395384
          ],
          [
            -1.262422,
            -19.505877
          ],
          [
            -1.545878,
            -19.226379
          ],
          [
            -1.577077,
            -16.713606
          ],
          [
            -1.764976,
            -15.895423
          ],
          [
            -2.267531,
            -15.611806
          ],
          [
            -2.770757,
            -16.405289
          ],
          [
            -2.682523,
            -18.723823
          ],
          [
            -3.152726,
            -21.739152
          ],
          [
            -3.55477,
            -22.995539
          ],
          [
            -3.253964,
            -24.754478
          ],
          [
            -3.64012,
            -26.262141
          ],
          [
            -3.436095,
            -27.769808
          ],
          [
            -3.871791,
            -28.774916
          ],
          [
            -4.755032,
            -29.528748
          ],
          [
            -4.655941,
            -29.780027
          ],
          [
            19.910876,
            -29.940956
          ],
          [
            49.495596,
            -29.939056
          ],
          [
            49.936254,
            -29.780027
          ],
          [
            49.969549,
            29.521421
          ],
          [
            49.930019,
            29.772699
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -6.328301554508024,
      "length": 12.656603109016048,
      "loops": [
        [
          [
            -7.58154,
            -29.528748
          ],
          [
            -7.593848,
            29.084869
          ],
          [
            -7.795632,
            29.90755
          ],
          [
            -49.507667,
            29.938641
          ],
          [
            -49.933556,
            29.772699
          ],
          [
            -49.953505,
            -29.780027
          ],
          [
            -49.256388,
            -29.947715
          ],
          [
            -7.795632,
            -29.912575
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -6.328301554508024,
      "length": 12.656603109016048,
      "loops": [
        [
          [
            -1.760782,
            -5.406126
          ],
          [
            -1.939917,
            -3.647185
          ],
          [
            -2.267531,
            -3.308469
          ],
          [
            -2.518808,
            -3.719244
          ],
          [
            -2.609574,
            -5.154849
          ],
          [
            -2.289796,
            -6.345232
          ],
          [
            -2.478435,
            -7.165067
          ],
          [
            -2.267531,
            -8.153446
          ],
          [
            -2.016254,
            -8.068266
          ],
          [
            -1.834935,
            -7.601619
          ],
          [
            -2.02259,
            -6.159958
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -6.328301554508024,
      "length": 12.656603109016048,
      "loops": [
        [
          [
            -1.764976,
            29.783323
          ],
          [
            -2.138722,
            29.772699
          ],
          [
            -1.603631,
            29.772699
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.009744839999999977,
    -0.18979626,
    0.04568017
  ],
  "construction_scale": 50.95207363373569,
  "expected_solid_count": 4
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
