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
      "start": -6.803952632971657,
      "length": 1.6497152206439027,
      "loops": [
        [
          [
            40.123258,
            -45.366817
          ],
          [
            40.087873,
            47.875053
          ],
          [
            40.152351,
            49.4189
          ],
          [
            40.380881,
            49.674621
          ],
          [
            40.638191,
            49.704108
          ],
          [
            40.895497,
            49.67207
          ],
          [
            41.130908,
            49.16159
          ],
          [
            41.146305,
            -22.897334
          ],
          [
            41.121903,
            -46.556687
          ],
          [
            40.963753,
            -47.071299
          ],
          [
            40.638191,
            -47.222326
          ],
          [
            40.189914,
            -46.813993
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.154509570433073,
      "length": 0.8249936893746099,
      "loops": [
        [
          [
            40.06303,
            48.132363
          ],
          [
            40.11437,
            -46.556687
          ],
          [
            40.170378,
            -47.071299
          ],
          [
            40.380881,
            -47.327272
          ],
          [
            40.638191,
            -47.311886
          ],
          [
            41.049527,
            -46.813993
          ],
          [
            41.094988,
            -45.784766
          ],
          [
            41.08584,
            48.940828
          ],
          [
            41.052698,
            49.4189
          ],
          [
            40.638191,
            49.727436
          ],
          [
            40.315955,
            49.676205
          ],
          [
            40.106534,
            49.4189
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.154509570433073,
      "length": 0.8249936893746099,
      "loops": [
        [
          [
            38.079714,
            -46.115801
          ],
          [
            38.071823,
            47.875053
          ],
          [
            38.009987,
            49.16159
          ],
          [
            37.807812,
            49.496833
          ],
          [
            37.672475,
            48.818425
          ],
          [
            37.729304,
            -46.556687
          ],
          [
            37.550502,
            -47.0705
          ],
          [
            -36.386365,
            -47.071299
          ],
          [
            31.687043,
            -47.274003
          ],
          [
            37.293197,
            -47.074196
          ],
          [
            37.807812,
            -47.177102
          ],
          [
            38.013637,
            -46.865473
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.329788039163782,
      "length": 1.2373544550092572,
      "loops": [
        [
          [
            36.778581,
            -49.607234
          ],
          [
            -40.413578,
            -49.707047
          ],
          [
            -40.710469,
            -49.644372
          ],
          [
            -40.928193,
            -49.23162
          ],
          [
            -41.061807,
            -47.328609
          ],
          [
            -40.995921,
            -47.071299
          ],
          [
            -40.670884,
            -46.886521
          ],
          [
            -36.811278,
            -46.771209
          ],
          [
            28.818314,
            -46.765514
          ],
          [
            35.749354,
            -46.729665
          ],
          [
            37.328692,
            -46.556687
          ],
          [
            37.455496,
            -43.999869
          ],
          [
            37.446389,
            49.4189
          ],
          [
            37.550502,
            49.76186
          ],
          [
            37.807812,
            49.884125
          ],
          [
            40.7658,
            49.676205
          ],
          [
            41.022282,
            49.16159
          ],
          [
            41.056633,
            45.543034
          ],
          [
            41.037184,
            -45.27015
          ],
          [
            40.895497,
            -47.07181
          ],
          [
            40.638191,
            -47.363897
          ],
          [
            40.138344,
            -47.57406
          ],
          [
            38.741324,
            -49.129757
          ],
          [
            38.211507,
            -49.387067
          ]
        ],
        [
          [
            39.86627,
            -31.448101
          ],
          [
            39.889413,
            -28.545183
          ],
          [
            39.86627,
            -23.738933
          ]
        ],
        [
          [
            39.86627,
            -20.371269
          ],
          [
            39.86821,
            -20.825966
          ],
          [
            39.86627,
            -20.888672
          ]
        ],
        [
          [
            39.865955,
            -23.141732
          ],
          [
            39.86627,
            -23.599365
          ],
          [
            39.86627,
            -23.133632
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.092705742259844,
      "length": 4.9486013457210705,
      "loops": [
        [
          [
            39.885269,
            35.267003
          ],
          [
            40.207187,
            49.4189
          ],
          [
            39.86627,
            49.757919
          ],
          [
            39.351654,
            49.719657
          ],
          [
            39.068954,
            49.4189
          ],
          [
            39.045764,
            48.57123
          ],
          [
            39.082972,
            34.67664
          ],
          [
            39.351654,
            32.50761
          ],
          [
            39.693328,
            33.647411
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.092705742259844,
      "length": 4.9486013457210705,
      "loops": [
        [
          [
            39.650715,
            -45.012845
          ],
          [
            39.094345,
            -36.906108
          ],
          [
            38.837039,
            -37.225446
          ],
          [
            38.127583,
            -40.638619
          ],
          [
            38.359542,
            -45.527456
          ],
          [
            38.475914,
            -46.042072
          ],
          [
            38.837039,
            -46.30259
          ],
          [
            39.094345,
            -46.229541
          ],
          [
            39.495401,
            -45.784766
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.8556234453559073,
      "length": 4.948601345721069,
      "loops": [
        [
          [
            38.763519,
            -24.095002
          ],
          [
            39.180159,
            19.571264
          ],
          [
            39.077951,
            48.980242
          ],
          [
            39.265596,
            49.676205
          ],
          [
            39.86627,
            49.79688
          ],
          [
            40.123576,
            49.702117
          ],
          [
            40.238626,
            49.4189
          ],
          [
            40.373121,
            25.746636
          ],
          [
            40.291035,
            -2.738504
          ],
          [
            39.933175,
            -32.586138
          ],
          [
            39.648635,
            -40.381313
          ],
          [
            39.803302,
            -45.012845
          ],
          [
            39.60896,
            -45.930616
          ],
          [
            39.094345,
            -46.314762
          ],
          [
            38.837039,
            -46.289979
          ],
          [
            38.521045,
            -45.784766
          ],
          [
            38.349466,
            -40.638619
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.03482654499999999,
    0.12373085,
    0.01017659999999998
  ],
  "construction_scale": 52.17476607821896,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
