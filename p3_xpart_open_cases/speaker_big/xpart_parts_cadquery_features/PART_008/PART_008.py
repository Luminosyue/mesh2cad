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
      "start": -25.32624693644316,
      "length": 3.0708611633857186,
      "loops": [
        [
          [
            29.729284,
            44.794556
          ],
          [
            21.94329,
            46.801804
          ],
          [
            14.028492,
            48.561476
          ],
          [
            -11.694605,
            48.74884
          ],
          [
            -32.965626,
            48.692812
          ],
          [
            -33.460302,
            48.66447
          ],
          [
            -33.842925,
            48.25728
          ],
          [
            -33.711997,
            -44.741607
          ],
          [
            -33.681043,
            -49.193679
          ],
          [
            -33.460302,
            -49.627767
          ],
          [
            42.224962,
            -49.525728
          ],
          [
            43.21431,
            -49.467494
          ],
          [
            43.681092,
            -49.193679
          ],
          [
            43.790788,
            -48.204331
          ],
          [
            43.730785,
            39.847804
          ],
          [
            43.21431,
            40.488615
          ],
          [
            42.001496,
            41.065116
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.256398822934898,
      "length": 44.51381069574725,
      "loops": [
        [
          [
            30.858237,
            44.401561
          ],
          [
            23.921988,
            46.279386
          ],
          [
            14.523165,
            48.429998
          ],
          [
            -14.662655,
            48.727325
          ],
          [
            -32.948912,
            48.713598
          ],
          [
            -33.460302,
            48.677636
          ],
          [
            -33.832981,
            48.25728
          ],
          [
            -33.769061,
            -31.385384
          ],
          [
            -33.954976,
            -32.034774
          ],
          [
            -35.439,
            -32.729389
          ],
          [
            -43.600105,
            -32.86941
          ],
          [
            -43.577787,
            -33.364082
          ],
          [
            -43.340992,
            -33.858758
          ],
          [
            -43.321397,
            -35.842763
          ],
          [
            -43.80116,
            -37.816159
          ],
          [
            -42.859125,
            -38.276013
          ],
          [
            -40.385749,
            -38.127981
          ],
          [
            -35.439,
            -38.249695
          ],
          [
            -33.954976,
            -38.481984
          ],
          [
            -33.746104,
            -39.811572
          ],
          [
            -33.694412,
            -49.193679
          ],
          [
            -33.460302,
            -49.744962
          ],
          [
            -31.481602,
            -49.834334
          ],
          [
            -30.80132,
            -49.688355
          ],
          [
            -30.560278,
            -49.193679
          ],
          [
            -30.513486,
            -47.214979
          ],
          [
            -29.997578,
            -47.147078
          ],
          [
            -21.588103,
            -47.322886
          ],
          [
            8.587066,
            -47.484597
          ],
          [
            19.486628,
            -48.083226
          ],
          [
            40.246261,
            -48.119028
          ],
          [
            40.472557,
            -48.204331
          ],
          [
            40.735623,
            -49.193679
          ],
          [
            41.23561,
            -49.522826
          ],
          [
            43.21431,
            -49.54488
          ],
          [
            43.708986,
            -49.217196
          ],
          [
            43.769827,
            39.353131
          ],
          [
            43.695013,
            39.847804
          ],
          [
            43.255076,
            40.34248
          ],
          [
            42.291951,
            40.837155
          ]
        ],
        [
          [
            40.687336,
            -43.768969
          ],
          [
            40.67069,
            37.869103
          ],
          [
            40.644285,
            38.36378
          ],
          [
            40.246261,
            38.807306
          ],
          [
            34.310161,
            39.000136
          ],
          [
            -1.289718,
            39.301831
          ],
          [
            -30.263682,
            39.353131
          ],
          [
            -30.492252,
            39.143042
          ],
          [
            -30.567299,
            37.357718
          ],
          [
            -30.575488,
            -30.412748
          ],
          [
            -30.483233,
            -44.758321
          ],
          [
            -30.461672,
            -45.236283
          ],
          [
            -30.094664,
            -45.730955
          ],
          [
            33.320813,
            -45.837318
          ],
          [
            40.387239,
            -45.730955
          ],
          [
            40.663544,
            -45.236283
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.2563988229349,
      "length": 3.070861163385715,
      "loops": [
        [
          [
            -22.082779,
            48.667871
          ],
          [
            11.060441,
            48.517505
          ],
          [
            15.869354,
            48.224424
          ],
          [
            28.868739,
            45.087442
          ],
          [
            38.762237,
            42.215803
          ],
          [
            42.719638,
            40.54074
          ],
          [
            43.696219,
            39.847804
          ],
          [
            43.812364,
            -46.720307
          ],
          [
            43.684584,
            -49.688355
          ],
          [
            42.719638,
            -49.906779
          ],
          [
            -32.242696,
            -49.998459
          ],
          [
            -33.460302,
            -49.891871
          ],
          [
            -33.637654,
            -49.688355
          ],
          [
            -33.807388,
            48.25728
          ],
          [
            -33.460302,
            48.529473
          ],
          [
            -32.965626,
            48.560542
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -4.7760000000007796e-05,
    0.045775394999999997,
    0.004403780000000024
  ],
  "construction_scale": 50.153179848019015,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
