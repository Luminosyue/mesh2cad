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
      "start": -15.776396318030175,
      "length": 1.9129215186442583,
      "loops": [
        [
          [
            -17.205211,
            -48.083129
          ],
          [
            -17.247902,
            48.039791
          ],
          [
            -17.038138,
            49.197896
          ],
          [
            -16.050648,
            49.55573
          ],
          [
            -13.505062,
            49.605112
          ],
          [
            11.01579,
            49.599712
          ],
          [
            11.973304,
            49.543319
          ],
          [
            12.552357,
            49.341331
          ],
          [
            12.782121,
            48.939411
          ],
          [
            12.899567,
            48.039791
          ],
          [
            12.775717,
            45.403727
          ],
          [
            12.72754,
            -6.09504
          ],
          [
            12.892864,
            -48.083129
          ],
          [
            12.85341,
            -48.66218
          ],
          [
            12.552357,
            -49.342327
          ],
          [
            11.973304,
            -49.574296
          ],
          [
            10.815196,
            -49.64487
          ],
          [
            -14.663167,
            -49.666333
          ],
          [
            -16.40033,
            -49.579276
          ],
          [
            -16.959437,
            -49.241234
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -13.864105855238638,
      "length": 10.518228601206175,
      "loops": [
        [
          [
            -17.465496,
            48.039791
          ],
          [
            -17.428648,
            -48.66218
          ],
          [
            -16.979384,
            -49.510575
          ],
          [
            -16.40033,
            -49.858907
          ],
          [
            -15.821276,
            -49.939589
          ],
          [
            10.815196,
            -49.936793
          ],
          [
            11.973304,
            -49.879308
          ],
          [
            12.552357,
            -49.694215
          ],
          [
            13.046803,
            -49.241234
          ],
          [
            13.253162,
            -48.083129
          ],
          [
            13.042597,
            -45.766915
          ],
          [
            13.00618,
            -5.542195
          ],
          [
            13.131411,
            -4.471855
          ],
          [
            13.710465,
            -4.550146
          ],
          [
            14.289518,
            -5.077419
          ],
          [
            14.868572,
            -5.244449
          ],
          [
            15.447626,
            -5.154393
          ],
          [
            16.026679,
            -4.825695
          ],
          [
            16.599619,
            -4.075045
          ],
          [
            16.729318,
            -3.22598
          ],
          [
            16.605733,
            -2.643978
          ],
          [
            16.160259,
            -2.008178
          ],
          [
            15.447626,
            -1.736396
          ],
          [
            14.868572,
            -1.833208
          ],
          [
            14.209937,
            -2.297846
          ],
          [
            13.710465,
            -3.170924
          ],
          [
            13.406881,
            -3.220521
          ],
          [
            12.984563,
            -0.600723
          ],
          [
            13.131411,
            3.589512
          ],
          [
            13.398943,
            3.141131
          ],
          [
            13.710465,
            3.304843
          ],
          [
            14.033148,
            2.603588
          ],
          [
            14.868572,
            1.814797
          ],
          [
            15.447626,
            1.649808
          ],
          [
            16.258514,
            2.024535
          ],
          [
            16.58099,
            2.519573
          ],
          [
            16.735986,
            3.182642
          ],
          [
            16.597754,
            4.031706
          ],
          [
            16.225968,
            4.61076
          ],
          [
            15.447626,
            5.149083
          ],
          [
            14.868572,
            5.224714
          ],
          [
            14.289518,
            5.057881
          ],
          [
            13.131411,
            4.160507
          ],
          [
            13.043521,
            4.919803
          ],
          [
            13.04768,
            46.30263
          ],
          [
            13.25274,
            48.039791
          ],
          [
            13.070161,
            49.197896
          ],
          [
            12.552357,
            49.697023
          ],
          [
            10.815196,
            49.911875
          ],
          [
            -15.242223,
            49.907225
          ],
          [
            -16.40033,
            49.830951
          ],
          [
            -16.979384,
            49.515307
          ],
          [
            -17.433932,
            48.618842
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.346508309885184,
      "length": 10.518228601206173,
      "loops": [
        [
          [
            13.150123,
            -0.021669
          ],
          [
            13.002753,
            46.30263
          ],
          [
            13.216418,
            48.039791
          ],
          [
            13.070389,
            49.197896
          ],
          [
            12.552357,
            49.6977
          ],
          [
            10.815196,
            49.904054
          ],
          [
            -15.242223,
            49.92213
          ],
          [
            -16.40033,
            49.841495
          ],
          [
            -16.979384,
            49.537364
          ],
          [
            -17.264293,
            49.197896
          ],
          [
            -17.475197,
            48.039791
          ],
          [
            -17.471434,
            -48.083129
          ],
          [
            -17.213628,
            -49.241234
          ],
          [
            -16.490986,
            -49.82029
          ],
          [
            -15.242223,
            -49.938482
          ],
          [
            11.19204,
            -49.914553
          ],
          [
            12.552357,
            -49.681267
          ],
          [
            13.00789,
            -49.241234
          ],
          [
            13.219353,
            -48.083129
          ],
          [
            12.996387,
            -45.766915
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 7.171089235468267,
      "length": 6.6936476756231,
      "loops": [
        [
          [
            -17.464844,
            -48.083129
          ],
          [
            -17.464989,
            48.618842
          ],
          [
            -16.979384,
            49.554218
          ],
          [
            -16.40033,
            49.865613
          ],
          [
            11.39425,
            49.935566
          ],
          [
            12.720357,
            49.776952
          ],
          [
            13.131411,
            49.604704
          ],
          [
            13.696239,
            48.973726
          ],
          [
            13.949743,
            47.514649
          ],
          [
            14.12855,
            38.249792
          ],
          [
            14.035306,
            -45.766915
          ],
          [
            13.97247,
            -46.925019
          ],
          [
            13.554991,
            -48.66218
          ],
          [
            13.131411,
            -49.351816
          ],
          [
            12.552357,
            -49.78258
          ],
          [
            10.761283,
            -49.924201
          ],
          [
            -15.821276,
            -49.963054
          ],
          [
            -16.561327,
            -49.82029
          ],
          [
            -17.239146,
            -49.241234
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 13.864105855238646,
      "length": 1.9129215186442619,
      "loops": [
        [
          [
            -17.063183,
            48.039791
          ],
          [
            -16.962709,
            -48.66218
          ],
          [
            -16.40033,
            -49.393365
          ],
          [
            -15.821276,
            -49.482418
          ],
          [
            10.236143,
            -49.492018
          ],
          [
            12.552357,
            -49.3432
          ],
          [
            13.131411,
            -48.220385
          ],
          [
            13.293755,
            -46.345968
          ],
          [
            13.449156,
            -20.549857
          ],
          [
            13.221044,
            47.460735
          ],
          [
            13.174563,
            48.618842
          ],
          [
            12.922392,
            49.197896
          ],
          [
            12.552357,
            49.478119
          ],
          [
            11.39425,
            49.642827
          ],
          [
            -1.923986,
            49.679688
          ],
          [
            -15.821276,
            49.588574
          ],
          [
            -16.40033,
            49.482208
          ],
          [
            -16.810085,
            49.197896
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    9.227500000000277e-05,
    -0.399349685,
    0.010658850000000004
  ],
  "construction_scale": 234.83208414014788,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
