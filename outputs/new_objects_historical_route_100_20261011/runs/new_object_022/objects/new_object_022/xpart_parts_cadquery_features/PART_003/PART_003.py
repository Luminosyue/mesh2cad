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
      "start": -23.749450301236692,
      "length": 2.8796712266468,
      "loops": [
        [
          [
            36.725762,
            -8.153545
          ],
          [
            29.270066,
            -6.569188
          ],
          [
            14.358674,
            -3.819037
          ],
          [
            -47.942582,
            6.349314
          ],
          [
            -49.657474,
            6.711947
          ],
          [
            -49.915645,
            7.024173
          ],
          [
            -49.143287,
            7.096926
          ],
          [
            -45.029798,
            6.481892
          ],
          [
            19.757625,
            -4.213787
          ],
          [
            40.325063,
            -8.347453
          ],
          [
            43.924364,
            -8.94379
          ],
          [
            49.752742,
            -10.354153
          ],
          [
            49.971233,
            -10.458149
          ],
          [
            49.971826,
            -10.715241
          ],
          [
            49.186354,
            -10.701909
          ],
          [
            43.924364,
            -9.481006
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -20.87072905260194,
      "length": 11.515834972551053,
      "loops": [
        [
          [
            36.725762,
            -7.341908
          ],
          [
            20.271812,
            -3.296189
          ],
          [
            9.216814,
            -0.829706
          ],
          [
            -8.038875,
            1.994342
          ],
          [
            -18.292133,
            4.193867
          ],
          [
            -25.747829,
            5.482098
          ],
          [
            -31.94852,
            6.410997
          ],
          [
            -37.059918,
            6.8149
          ],
          [
            -37.543644,
            7.037733
          ],
          [
            -38.85957,
            8.594885
          ],
          [
            -39.343296,
            8.885889
          ],
          [
            -49.400382,
            7.169433
          ],
          [
            -49.806176,
            7.281267
          ],
          [
            -49.780112,
            7.538361
          ],
          [
            -49.143287,
            7.845273
          ],
          [
            -38.829109,
            9.437506
          ],
          [
            -38.345383,
            9.117728
          ],
          [
            -36.941247,
            7.538361
          ],
          [
            -36.515274,
            7.29968
          ],
          [
            -32.175153,
            6.954855
          ],
          [
            -23.948178,
            5.694074
          ],
          [
            -17.808407,
            4.607317
          ],
          [
            -7.414435,
            2.398833
          ],
          [
            5.905067,
            0.308834
          ],
          [
            10.986005,
            -0.647018
          ],
          [
            33.640648,
            -6.018013
          ],
          [
            46.20774,
            -9.302298
          ],
          [
            49.991033,
            -10.458149
          ],
          [
            49.837501,
            -10.736876
          ],
          [
            49.323319,
            -10.690115
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -9.355844058062939,
      "length": 8.637113723916302,
      "loops": [
        [
          [
            3.378213,
            1.581068
          ],
          [
            46.75978,
            -9.424595
          ],
          [
            49.58041,
            -10.21536
          ],
          [
            49.982258,
            -10.458149
          ],
          [
            49.837501,
            -10.679586
          ],
          [
            49.323319,
            -10.662834
          ],
          [
            4.406585,
            0.780813
          ],
          [
            -10.247714,
            5.016204
          ],
          [
            -20.60597,
            6.748836
          ],
          [
            -27.290386,
            8.357262
          ],
          [
            -29.733083,
            9.093722
          ],
          [
            -30.964224,
            10.104412
          ],
          [
            -31.403874,
            10.286298
          ],
          [
            -49.400382,
            7.213074
          ],
          [
            -49.739943,
            7.281267
          ],
          [
            -49.832108,
            7.538361
          ],
          [
            -49.143287,
            7.868933
          ],
          [
            -33.203525,
            10.547147
          ],
          [
            -30.889687,
            10.785509
          ],
          [
            -28.990622,
            9.595102
          ],
          [
            -22.40562,
            7.776191
          ],
          [
            -19.150237,
            7.05481
          ],
          [
            -10.504807,
            5.617673
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.7196803121586868,
      "length": 21.59135934277268,
      "loops": [
        [
          [
            36.725762,
            -7.431427
          ],
          [
            49.58041,
            -10.721168
          ],
          [
            49.837501,
            -10.670874
          ],
          [
            49.970987,
            -10.458149
          ],
          [
            48.809131,
            -9.990136
          ],
          [
            39.810876,
            -7.661809
          ],
          [
            31.326807,
            -5.76621
          ],
          [
            25.542505,
            -4.205204
          ],
          [
            3.817863,
            1.124341
          ],
          [
            -13.150273,
            5.813728
          ],
          [
            -18.934577,
            7.257124
          ],
          [
            -23.176899,
            7.833426
          ],
          [
            -39.502015,
            9.500254
          ],
          [
            -49.014453,
            7.910232
          ],
          [
            -49.847381,
            7.538361
          ],
          [
            -49.761498,
            7.281267
          ],
          [
            -49.400382,
            7.231644
          ],
          [
            -39.502015,
            8.982232
          ],
          [
            -36.159805,
            8.734516
          ],
          [
            -19.063411,
            6.766533
          ],
          [
            -13.027118,
            5.251875
          ],
          [
            2.532398,
            0.92915
          ],
          [
            25.670764,
            -4.752413
          ],
          [
            31.326807,
            -6.280822
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 20.870729052601945,
      "length": 2.8796712266467965,
      "loops": [
        [
          [
            12.044837,
            -2.186061
          ],
          [
            49.58041,
            -10.803327
          ],
          [
            49.943505,
            -10.715241
          ],
          [
            49.837501,
            -10.374363
          ],
          [
            46.2382,
            -9.423801
          ],
          [
            12.30193,
            -1.70315
          ],
          [
            -5.66534,
            2.605481
          ],
          [
            -36.288639,
            6.334884
          ],
          [
            -46.529596,
            7.281267
          ],
          [
            -48.629104,
            7.405751
          ],
          [
            -49.20389,
            7.281267
          ],
          [
            -42.20178,
            6.280965
          ],
          [
            -26.48987,
            4.628848
          ],
          [
            -5.437485,
            2.013627
          ],
          [
            -0.038532,
            0.834998
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.002694450000000001,
    0.01763031000000001,
    0.21373353
  ],
  "construction_scale": 104.2626512978792,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
