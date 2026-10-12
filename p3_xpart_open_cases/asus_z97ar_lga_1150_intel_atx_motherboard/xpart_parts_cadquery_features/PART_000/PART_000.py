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
      "start": -13.96533951059273,
      "length": 1.6933270391068156,
      "loops": [
        [
          [
            8.209921,
            1.002136
          ],
          [
            -19.150976,
            1.269447
          ],
          [
            -21.048431,
            1.333036
          ],
          [
            -24.967789,
            1.814654
          ],
          [
            -44.574825,
            1.887083
          ],
          [
            -47.737252,
            1.622739
          ],
          [
            -48.5613,
            1.101067
          ],
          [
            -48.848621,
            0.091889
          ],
          [
            -48.782192,
            -0.163907
          ],
          [
            -48.369734,
            -0.316909
          ],
          [
            -46.281786,
            -0.459015
          ],
          [
            -28.845614,
            -0.838752
          ],
          [
            -13.083664,
            -0.929481
          ],
          [
            10.329772,
            -1.36623
          ],
          [
            48.400483,
            -1.775332
          ],
          [
            49.174484,
            -1.428874
          ],
          [
            49.12761,
            0.46858
          ],
          [
            48.400483,
            0.593297
          ],
          [
            21.960554,
            0.616977
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -12.272571085066337,
      "length": 24.5457007837131,
      "loops": [
        [
          [
            43.340601,
            -2.072906
          ],
          [
            22.468592,
            -2.12181
          ],
          [
            2.22907,
            -1.729484
          ],
          [
            -44.574825,
            -1.316695
          ],
          [
            -49.002221,
            -0.846708
          ],
          [
            -49.634707,
            -0.594807
          ],
          [
            -49.879642,
            -0.163907
          ],
          [
            -49.634707,
            1.096936
          ],
          [
            -49.002221,
            1.432855
          ],
          [
            -43.753407,
            1.767435
          ],
          [
            -26.865244,
            1.631017
          ],
          [
            -19.718974,
            1.325699
          ],
          [
            7.921436,
            1.442573
          ],
          [
            13.613802,
            1.170196
          ],
          [
            40.178176,
            1.000141
          ],
          [
            49.032964,
            0.696255
          ],
          [
            49.704242,
            0.46858
          ],
          [
            49.905443,
            -0.163907
          ],
          [
            49.735855,
            -0.796388
          ],
          [
            49.157259,
            -1.428874
          ],
          [
            48.400483,
            -1.638467
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 12.27257108506634,
      "length": 1.693327039106812,
      "loops": [
        [
          [
            46.933494,
            0.675285
          ],
          [
            38.711189,
            0.932458
          ],
          [
            33.22084,
            0.703804
          ],
          [
            30.690899,
            1.04801
          ],
          [
            28.160958,
            1.160846
          ],
          [
            24.998533,
            0.376992
          ],
          [
            15.511257,
            0.411582
          ],
          [
            12.981317,
            0.254614
          ],
          [
            12.348832,
            0.282478
          ],
          [
            11.022732,
            1.101067
          ],
          [
            9.818892,
            1.41945
          ],
          [
            0.9641,
            1.546671
          ],
          [
            -9.312264,
            1.121036
          ],
          [
            -11.053117,
            0.652871
          ],
          [
            -12.950571,
            0.383276
          ],
          [
            -18.010453,
            0.145468
          ],
          [
            -25.600273,
            0.587524
          ],
          [
            -26.232757,
            0.711654
          ],
          [
            -27.42854,
            1.733553
          ],
          [
            -28.130214,
            1.853235
          ],
          [
            -43.511872,
            2.27307
          ],
          [
            -47.104766,
            2.117151
          ],
          [
            -49.002221,
            1.85168
          ],
          [
            -49.258153,
            1.733553
          ],
          [
            -49.669254,
            1.101067
          ],
          [
            -49.733472,
            0.03811
          ],
          [
            -49.634707,
            -0.319651
          ],
          [
            -49.204237,
            -0.666249
          ],
          [
            -47.737252,
            -0.765502
          ],
          [
            -27.497727,
            -0.961208
          ],
          [
            -26.232757,
            -0.807983
          ],
          [
            -12.318087,
            -0.912886
          ],
          [
            -9.155661,
            -1.199293
          ],
          [
            9.818892,
            -1.432276
          ],
          [
            12.649646,
            -1.301907
          ],
          [
            39.976159,
            -1.878319
          ],
          [
            48.400483,
            -1.7778
          ],
          [
            49.032964,
            -1.728018
          ],
          [
            49.550214,
            -1.381762
          ],
          [
            49.708729,
            0.46858
          ],
          [
            49.032964,
            0.866743
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.96404556,
    -0.003868645000000004,
    -0.0051713700000000085
  ],
  "construction_scale": 64.12522003607377,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
