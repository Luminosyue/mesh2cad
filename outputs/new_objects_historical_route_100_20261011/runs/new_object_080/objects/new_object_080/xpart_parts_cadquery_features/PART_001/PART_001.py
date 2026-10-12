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
      "start": -5.356640057798859,
      "length": 4.545242193431648,
      "loops": [
        [
          [
            -19.261427,
            -44.53169
          ],
          [
            -19.496395,
            -45.029322
          ],
          [
            -19.937413,
            -45.312568
          ],
          [
            -20.932675,
            -45.552946
          ],
          [
            -21.927938,
            -45.496459
          ],
          [
            -22.440967,
            -45.029322
          ],
          [
            -22.535631,
            -43.287615
          ],
          [
            -22.179514,
            -42.833085
          ],
          [
            -21.679122,
            -42.603184
          ],
          [
            -20.683859,
            -42.450145
          ],
          [
            -19.80323,
            -42.541168
          ],
          [
            -19.406806,
            -43.038796
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.356640057798859,
      "length": 4.545242193431648,
      "loops": [
        [
          [
            -22.576645,
            43.591539
          ],
          [
            -22.443186,
            45.041942
          ],
          [
            -21.927938,
            45.5086
          ],
          [
            -21.181491,
            45.56704
          ],
          [
            -20.186228,
            45.40738
          ],
          [
            -19.551775,
            45.094223
          ],
          [
            -19.329364,
            44.793127
          ],
          [
            -19.441101,
            43.051416
          ],
          [
            -19.936724,
            42.592012
          ],
          [
            -20.960924,
            42.548377
          ],
          [
            -21.927938,
            42.750706
          ],
          [
            -22.351375,
            43.051416
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.356640057798859,
      "length": 4.545242193431648,
      "loops": [
        [
          [
            22.430718,
            35.586946
          ],
          [
            22.403585,
            37.079843
          ],
          [
            21.835368,
            37.697365
          ],
          [
            21.08892,
            37.810611
          ],
          [
            20.093658,
            37.679309
          ],
          [
            19.596026,
            37.493422
          ],
          [
            19.242897,
            37.079843
          ],
          [
            19.344963,
            35.338131
          ],
          [
            19.844843,
            34.873596
          ],
          [
            20.833448,
            34.855947
          ],
          [
            21.807119,
            35.048421
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.356640057798859,
      "length": 4.545242193431648,
      "loops": [
        [
          [
            22.292521,
            -35.325512
          ],
          [
            21.807119,
            -35.062927
          ],
          [
            20.840105,
            -34.913307
          ],
          [
            19.543335,
            -35.076698
          ],
          [
            19.330091,
            -35.325512
          ],
          [
            19.2353,
            -35.823144
          ],
          [
            19.193713,
            -36.818406
          ],
          [
            19.318962,
            -37.243266
          ],
          [
            19.789352,
            -37.563798
          ],
          [
            20.765936,
            -37.811615
          ],
          [
            21.572287,
            -37.81367
          ],
          [
            22.055934,
            -37.615526
          ],
          [
            22.325442,
            -37.316038
          ],
          [
            22.44345,
            -36.874566
          ],
          [
            22.462538,
            -35.823144
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.8116121299695234,
      "length": 0.9741488215657409,
      "loops": [
        [
          [
            20.436104,
            47.606917
          ],
          [
            -19.716847,
            47.707134
          ],
          [
            -20.463293,
            47.582984
          ],
          [
            -20.687112,
            47.281281
          ],
          [
            -20.737315,
            39.358195
          ],
          [
            -20.700178,
            37.328657
          ],
          [
            -20.558282,
            36.831025
          ],
          [
            -20.081584,
            36.593786
          ],
          [
            -19.219214,
            36.547055
          ],
          [
            -8.271326,
            36.594758
          ],
          [
            -7.943921,
            36.333396
          ],
          [
            -7.903336,
            35.586946
          ],
          [
            -7.929394,
            -36.071959
          ],
          [
            -8.052541,
            -36.320777
          ],
          [
            -8.520142,
            -36.441968
          ],
          [
            -19.468031,
            -36.462012
          ],
          [
            -20.3289,
            -36.569591
          ],
          [
            -20.650703,
            -36.818406
          ],
          [
            -20.75826,
            -46.273401
          ],
          [
            -20.703593,
            -47.253358
          ],
          [
            -20.463293,
            -47.562642
          ],
          [
            -19.716847,
            -47.666202
          ],
          [
            19.34721,
            -47.592268
          ],
          [
            20.591288,
            -47.529186
          ],
          [
            20.921963,
            -47.268662
          ],
          [
            20.927428,
            47.032467
          ],
          [
            20.840105,
            47.353821
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 0.16232242599390556,
      "length": 1.6234385255413604,
      "loops": [
        [
          [
            21.858863,
            47.281281
          ],
          [
            21.874706,
            -47.630416
          ],
          [
            21.835368,
            -48.021202
          ],
          [
            21.586552,
            -48.359664
          ],
          [
            18.790617,
            -48.482314
          ],
          [
            -20.712108,
            -48.50661
          ],
          [
            -21.380164,
            -48.43775
          ],
          [
            -21.609575,
            -48.248327
          ],
          [
            -21.716263,
            -47.766295
          ],
          [
            -21.680997,
            -37.316038
          ],
          [
            -21.626886,
            -36.818406
          ],
          [
            -21.458556,
            -36.639434
          ],
          [
            -20.214477,
            -36.436756
          ],
          [
            -8.271326,
            -36.412005
          ],
          [
            -8.022511,
            -36.27935
          ],
          [
            -7.894117,
            -35.574327
          ],
          [
            -7.942492,
            36.333396
          ],
          [
            -8.520142,
            36.596979
          ],
          [
            -20.214477,
            36.533362
          ],
          [
            -21.133263,
            36.586209
          ],
          [
            -21.446573,
            36.740565
          ],
          [
            -21.642548,
            37.079843
          ],
          [
            -21.667761,
            37.577471
          ],
          [
            -21.70317,
            47.032467
          ],
          [
            -21.688149,
            48.027728
          ],
          [
            -21.458556,
            48.399204
          ],
          [
            -20.214477,
            48.536875
          ],
          [
            13.375635,
            48.496795
          ],
          [
            21.08892,
            48.460346
          ],
          [
            21.680822,
            48.276547
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.785546685932954,
      "length": 0.9741488215657418,
      "loops": [
        [
          [
            21.835368,
            -49.186546
          ],
          [
            -22.181112,
            -49.203729
          ],
          [
            -22.557332,
            -48.76156
          ],
          [
            -22.534414,
            -37.106899
          ],
          [
            -22.259762,
            -36.569591
          ],
          [
            -20.463293,
            -36.43185
          ],
          [
            -8.520142,
            -36.428558
          ],
          [
            -8.064041,
            -36.320777
          ],
          [
            -7.925904,
            -36.071959
          ],
          [
            -7.894096,
            35.859655
          ],
          [
            -7.934358,
            36.333396
          ],
          [
            -8.271326,
            36.596962
          ],
          [
            -21.20974,
            36.529591
          ],
          [
            -22.038981,
            36.582211
          ],
          [
            -22.433768,
            36.831025
          ],
          [
            -22.563732,
            48.492483
          ],
          [
            -22.453819,
            48.972758
          ],
          [
            -22.181112,
            49.183565
          ],
          [
            -21.233632,
            49.241721
          ],
          [
            22.332999,
            49.06633
          ],
          [
            22.616912,
            48.774179
          ],
          [
            22.676597,
            47.811627
          ],
          [
            22.686525,
            -48.232548
          ],
          [
            22.581814,
            -48.939215
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.759481241896384,
      "length": 2.5973730815047884,
      "loops": [
        [
          [
            22.536596,
            49.712567
          ],
          [
            -22.205003,
            49.782703
          ],
          [
            -22.95145,
            49.624027
          ],
          [
            -23.18437,
            49.271807
          ],
          [
            -23.167378,
            37.328657
          ],
          [
            -22.906231,
            36.647177
          ],
          [
            -21.956187,
            36.513852
          ],
          [
            -8.520142,
            36.60418
          ],
          [
            -8.212605,
            36.582211
          ],
          [
            -7.929847,
            36.333396
          ],
          [
            -7.889005,
            -35.574327
          ],
          [
            -7.91918,
            -36.071959
          ],
          [
            -8.271326,
            -36.409208
          ],
          [
            -21.956187,
            -36.436479
          ],
          [
            -22.926098,
            -36.569591
          ],
          [
            -23.178209,
            -37.067223
          ],
          [
            -23.200266,
            -49.28373
          ],
          [
            -22.906231,
            -49.676785
          ],
          [
            -22.205003,
            -49.784344
          ],
          [
            22.830631,
            -49.744146
          ],
          [
            23.190669,
            -49.508006
          ],
          [
            23.291977,
            -48.965155
          ],
          [
            23.22888,
            49.271807
          ],
          [
            23.030918,
            49.556522
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -6.253000000000508e-05,
    -0.148514735,
    -0.0018671450000000006
  ],
  "construction_scale": 100.90583165072859,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
