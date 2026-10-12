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
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -2.6507951991829186,
      "length": 0.6427230497917062,
      "loops": [
        [
          [
            22.666236,
            -31.497247
          ],
          [
            42.085473,
            -31.579
          ],
          [
            43.428898,
            -31.741003
          ],
          [
            43.868723,
            -32.198437
          ],
          [
            48.807517,
            -32.319336
          ],
          [
            49.554412,
            -32.362954
          ],
          [
            49.662603,
            -32.487899
          ],
          [
            49.554412,
            -32.891847
          ],
          [
            46.566836,
            -33.404436
          ],
          [
            44.326156,
            -33.472199
          ],
          [
            43.57926,
            -33.969601
          ],
          [
            43.446232,
            -34.861609
          ],
          [
            44.009402,
            -35.792227
          ],
          [
            44.8861,
            -36.222367
          ],
          [
            44.841862,
            -36.453553
          ],
          [
            44.643286,
            -36.96926
          ],
          [
            43.670509,
            -37.716155
          ],
          [
            42.749256,
            -37.769346
          ],
          [
            5.48768,
            -38.008952
          ],
          [
            -5.715726,
            -37.807051
          ],
          [
            -22.147388,
            -37.783462
          ],
          [
            -31.857007,
            -38.080133
          ],
          [
            -46.794883,
            -37.96199
          ],
          [
            -49.035563,
            -38.188515
          ],
          [
            -49.219154,
            -37.716155
          ],
          [
            -49.260363,
            -33.234791
          ],
          [
            -49.035563,
            -32.805572
          ],
          [
            -46.995892,
            -32.487899
          ],
          [
            -42.435285,
            -32.609664
          ],
          [
            -36.338371,
            -32.213984
          ],
          [
            -34.097688,
            -31.694173
          ],
          [
            -30.363219,
            -31.45936
          ],
          [
            -27.375643,
            -31.453472
          ],
          [
            -21.400495,
            -31.856094
          ],
          [
            -19.159813,
            -31.571245
          ],
          [
            -13.931557,
            -31.466595
          ],
          [
            12.209724,
            -31.619279
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.0081781811991797,
      "length": 3.5344996307185315,
      "loops": [
        [
          [
            49.973758,
            -32.487899
          ],
          [
            49.944946,
            -37.716155
          ],
          [
            49.554412,
            -38.162293
          ],
          [
            41.33858,
            -38.206727
          ],
          [
            39.844793,
            -38.500944
          ],
          [
            33.739941,
            -38.609463
          ],
          [
            -27.505346,
            -38.551749
          ],
          [
            -48.41837,
            -38.674054
          ],
          [
            -49.035563,
            -38.66682
          ],
          [
            -49.371716,
            -38.463048
          ],
          [
            -49.855389,
            -36.839558
          ],
          [
            -49.940495,
            -34.728579
          ],
          [
            -49.563147,
            -33.234791
          ],
          [
            -49.035563,
            -32.428462
          ],
          [
            -46.047988,
            -32.484965
          ],
          [
            -43.393837,
            -31.741003
          ],
          [
            -37.085263,
            -31.134776
          ],
          [
            -33.350795,
            -31.570587
          ],
          [
            -32.603903,
            -31.476895
          ],
          [
            -31.857007,
            -31.751375
          ],
          [
            -31.593751,
            -30.994111
          ],
          [
            -31.421777,
            -29.325781
          ],
          [
            -31.458357,
            28.933073
          ],
          [
            -31.407687,
            31.20198
          ],
          [
            -31.110114,
            33.632745
          ],
          [
            -30.457751,
            33.14422
          ],
          [
            -29.616326,
            33.20748
          ],
          [
            -28.869431,
            33.398135
          ],
          [
            -28.411009,
            33.835881
          ],
          [
            -27.665388,
            34.73254
          ],
          [
            -27.40793,
            35.479433
          ],
          [
            -27.375643,
            37.200329
          ],
          [
            -27.34314,
            35.479433
          ],
          [
            -26.935564,
            33.07041
          ],
          [
            -26.827479,
            29.355481
          ],
          [
            -26.832205,
            12.325727
          ],
          [
            -26.995207,
            10.831939
          ],
          [
            -26.80981,
            10.085045
          ],
          [
            -26.757327,
            -30.337705
          ],
          [
            -26.01156,
            -30.919369
          ],
          [
            7.598659,
            -30.822043
          ],
          [
            39.844793,
            -30.97217
          ],
          [
            42.085473,
            -31.12931
          ],
          [
            44.326156,
            -31.62179
          ],
          [
            49.554412,
            -32.022954
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.5262154177113842,
      "length": 1.1246858132795101,
      "loops": [
        [
          [
            -46.177277,
            -38.140491
          ],
          [
            -35.591475,
            -38.396218
          ],
          [
            -9.450195,
            -38.29171
          ],
          [
            6.981467,
            -38.481801
          ],
          [
            38.737335,
            -38.463048
          ],
          [
            42.688517,
            -37.716155
          ],
          [
            42.869098,
            -36.96926
          ],
          [
            42.512378,
            -36.222367
          ],
          [
            42.576934,
            -35.475475
          ],
          [
            42.340463,
            -35.220485
          ],
          [
            42.621407,
            -33.981686
          ],
          [
            45.073048,
            -32.641214
          ],
          [
            46.126571,
            -32.487899
          ],
          [
            44.422736,
            -32.215347
          ],
          [
            43.57926,
            -31.71946
          ],
          [
            37.604112,
            -31.28216
          ],
          [
            1.753212,
            -31.078457
          ],
          [
            -26.519327,
            -31.187192
          ],
          [
            -30.363219,
            -31.323348
          ],
          [
            -31.95201,
            -31.545157
          ],
          [
            -36.338371,
            -31.441183
          ],
          [
            -41.14837,
            -31.741003
          ],
          [
            -49.035563,
            -32.55429
          ],
          [
            -49.373846,
            -33.313641
          ],
          [
            -49.313167,
            -37.795004
          ],
          [
            -49.035563,
            -38.25095
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.94802823,
    -0.05274228999999997,
    -0.10359060000000003
  ],
  "construction_scale": 75.72467338698911,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
