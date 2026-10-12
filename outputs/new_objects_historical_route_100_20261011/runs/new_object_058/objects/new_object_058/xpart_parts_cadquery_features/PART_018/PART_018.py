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
      "start": -8.574850144932554,
      "length": 1.0397187691491376,
      "loops": [
        [
          [
            3.460141,
            46.631553
          ],
          [
            7.146568,
            46.680476
          ],
          [
            8.32905,
            46.994677
          ],
          [
            8.570257,
            47.510148
          ],
          [
            8.54606,
            49.056557
          ],
          [
            8.099365,
            49.545608
          ],
          [
            3.335197,
            49.572022
          ],
          [
            2.845459,
            49.056557
          ],
          [
            3.01227,
            46.994677
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.535474369789214,
      "length": 1.0397187691491376,
      "loops": [
        [
          [
            2.822683,
            45.963736
          ],
          [
            2.722994,
            -36.535928
          ],
          [
            2.463813,
            -48.882669
          ],
          [
            2.80665,
            -49.398138
          ],
          [
            3.460141,
            -49.820449
          ],
          [
            6.552956,
            -49.859115
          ],
          [
            7.068432,
            -49.749372
          ],
          [
            7.488139,
            -49.398138
          ],
          [
            7.691665,
            -48.367197
          ],
          [
            7.702058,
            45.448268
          ],
          [
            7.725998,
            45.963736
          ],
          [
            8.891891,
            46.994677
          ],
          [
            9.013722,
            47.510148
          ],
          [
            9.014559,
            49.056557
          ],
          [
            8.873671,
            49.572022
          ],
          [
            8.614839,
            49.831707
          ],
          [
            8.099365,
            49.98311
          ],
          [
            3.460141,
            49.988254
          ],
          [
            2.944674,
            49.889297
          ],
          [
            2.429198,
            49.520656
          ],
          [
            2.268623,
            49.056557
          ],
          [
            2.253708,
            46.994677
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -6.496098594645874,
      "length": 6.23659764486584,
      "loops": [
        [
          [
            2.718354,
            -35.995928
          ],
          [
            2.735497,
            36.19741
          ],
          [
            2.863069,
            45.963736
          ],
          [
            2.252082,
            46.994677
          ],
          [
            2.225911,
            49.056557
          ],
          [
            2.429198,
            49.577033
          ],
          [
            2.944674,
            49.906914
          ],
          [
            3.460141,
            49.990699
          ],
          [
            8.099365,
            49.939613
          ],
          [
            8.614839,
            49.746924
          ],
          [
            8.925726,
            49.056557
          ],
          [
            8.825386,
            46.994677
          ],
          [
            8.099365,
            46.384157
          ],
          [
            7.853439,
            45.963736
          ],
          [
            7.84738,
            45.475862
          ],
          [
            7.841234,
            -48.367197
          ],
          [
            7.650155,
            -49.398138
          ],
          [
            7.068432,
            -49.865604
          ],
          [
            6.552956,
            -49.971331
          ],
          [
            0.367324,
            -49.79372
          ],
          [
            -0.663617,
            -49.518402
          ],
          [
            -1.835332,
            -48.367197
          ],
          [
            -8.265982,
            -40.764833
          ],
          [
            -8.729612,
            -40.119687
          ],
          [
            -8.798905,
            -39.604215
          ],
          [
            -8.395658,
            -39.231047
          ],
          [
            -7.880191,
            -39.034042
          ],
          [
            1.398265,
            -39.049718
          ],
          [
            1.913733,
            -39.017873
          ],
          [
            2.55017,
            -38.573278
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.25984394378583175,
      "length": 3.1184703194358177,
      "loops": [
        [
          [
            2.81955,
            45.963736
          ],
          [
            2.809716,
            -38.057806
          ],
          [
            2.370199,
            -39.088745
          ],
          [
            2.31627,
            -39.604215
          ],
          [
            2.331357,
            -44.75891
          ],
          [
            2.906228,
            -46.305323
          ],
          [
            2.969081,
            -49.398138
          ],
          [
            3.513046,
            -49.853346
          ],
          [
            6.552956,
            -49.888739
          ],
          [
            7.068432,
            -49.77807
          ],
          [
            7.528111,
            -49.398138
          ],
          [
            7.676284,
            -48.882669
          ],
          [
            7.756816,
            -44.75891
          ],
          [
            7.738559,
            44.341241
          ],
          [
            7.786841,
            45.963736
          ],
          [
            8.750592,
            46.994677
          ],
          [
            8.8721,
            49.056557
          ],
          [
            8.711264,
            49.572022
          ],
          [
            8.099365,
            49.929189
          ],
          [
            2.944674,
            49.955736
          ],
          [
            2.365285,
            49.572022
          ],
          [
            2.201363,
            49.056557
          ],
          [
            2.263287,
            46.994677
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.8582833816441884,
      "length": 5.716909757294169,
      "loops": [
        [
          [
            2.353297,
            -44.75891
          ],
          [
            2.372,
            -39.088745
          ],
          [
            2.802821,
            -38.573278
          ],
          [
            6.552956,
            -38.452778
          ],
          [
            7.068432,
            -38.597191
          ],
          [
            7.385767,
            -39.088745
          ],
          [
            7.433313,
            -41.150623
          ],
          [
            7.406795,
            -44.75891
          ],
          [
            7.068432,
            -45.374056
          ],
          [
            6.552956,
            -45.518079
          ],
          [
            2.944674,
            -45.510463
          ],
          [
            2.566217,
            -45.274382
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.8582833816441884,
      "length": 5.716909757294169,
      "loops": [
        [
          [
            8.519751,
            46.80353
          ],
          [
            8.832365,
            47.510148
          ],
          [
            8.831977,
            49.056557
          ],
          [
            8.614839,
            49.659589
          ],
          [
            8.099365,
            49.916267
          ],
          [
            2.944674,
            49.978116
          ],
          [
            2.313214,
            49.572022
          ],
          [
            2.112619,
            47.510148
          ],
          [
            2.197956,
            46.994677
          ],
          [
            2.793256,
            46.479207
          ],
          [
            7.583897,
            46.385399
          ],
          [
            8.099365,
            46.47152
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.456885435,
    -0.0028817250000000016,
    -0.17983252500000002
  ],
  "construction_scale": 209.04588801825687,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
