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
      "start": -50.0,
      "length": 18.18381818181818,
      "loops": [
        [
          [
            14.544959,
            -17.772822
          ],
          [
            14.567148,
            -5.160687
          ],
          [
            14.829519,
            -4.662305
          ],
          [
            15.092272,
            -4.67533
          ],
          [
            15.312607,
            -5.160687
          ],
          [
            15.38112,
            -6.228016
          ],
          [
            15.570763,
            -18.035577
          ],
          [
            15.38145,
            -18.823836
          ],
          [
            14.829519,
            -19.316085
          ],
          [
            6.158676,
            -19.505609
          ],
          [
            -13.810539,
            -19.490173
          ],
          [
            -14.86155,
            -19.337854
          ],
          [
            -15.589417,
            -18.823836
          ],
          [
            -15.597113,
            -18.561084
          ],
          [
            -15.387055,
            -18.318731
          ],
          [
            -14.86155,
            -18.263948
          ],
          [
            -0.93565,
            -18.479085
          ],
          [
            11.676486,
            -18.287854
          ],
          [
            14.304015,
            -18.391373
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -31.81818181818182,
      "length": 24.24442424242424,
      "loops": [
        [
          [
            14.553602,
            4.08851
          ],
          [
            14.829519,
            8.223481
          ],
          [
            15.092272,
            8.776292
          ],
          [
            15.417194,
            5.665027
          ],
          [
            15.541076,
            1.723734
          ],
          [
            15.529192,
            -18.298329
          ],
          [
            15.446624,
            -18.823836
          ],
          [
            15.092272,
            -19.276894
          ],
          [
            13.253003,
            -19.529413
          ],
          [
            8.260698,
            -19.692996
          ],
          [
            -2.302264,
            -19.775915
          ],
          [
            -11.18301,
            -19.704233
          ],
          [
            -14.598797,
            -19.52809
          ],
          [
            -15.387055,
            -19.23764
          ],
          [
            -15.502829,
            -19.086587
          ],
          [
            -15.165837,
            -18.823836
          ],
          [
            -13.863388,
            -18.682875
          ],
          [
            9.31171,
            -18.63716
          ],
          [
            14.304015,
            -18.452462
          ],
          [
            14.508599,
            -18.035577
          ],
          [
            14.537777,
            -17.19447
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            14.54592,
            5.174103
          ],
          [
            14.541319,
            -17.772822
          ],
          [
            14.507262,
            -18.298329
          ],
          [
            14.317912,
            -18.561084
          ],
          [
            7.122257,
            -18.714659
          ],
          [
            -13.109711,
            -18.675535
          ],
          [
            -15.124303,
            -18.832891
          ],
          [
            -15.387055,
            -18.949394
          ],
          [
            -15.387055,
            -19.226488
          ],
          [
            -14.336044,
            -19.544888
          ],
          [
            -8.029977,
            -19.801824
          ],
          [
            13.428324,
            -19.601266
          ],
          [
            14.566767,
            -19.497686
          ],
          [
            15.092272,
            -19.261716
          ],
          [
            15.448459,
            -18.823836
          ],
          [
            15.550029,
            -18.298329
          ],
          [
            15.496655,
            4.823919
          ],
          [
            15.261583,
            16.209722
          ],
          [
            15.092272,
            16.58472
          ],
          [
            14.826596,
            15.596785
          ],
          [
            14.686227,
            13.757515
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.575757575757578,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            15.355025,
            19.179893
          ],
          [
            15.355025,
            19.590293
          ],
          [
            15.092272,
            19.80178
          ],
          [
            15.092272,
            19.320653
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.5151515151515156,
      "length": 24.244424242424234,
      "loops": [
        [
          [
            -14.86155,
            -19.613881
          ],
          [
            2.218102,
            -19.952546
          ],
          [
            7.471722,
            -19.877052
          ],
          [
            14.304015,
            -19.659515
          ],
          [
            15.028392,
            -19.349342
          ],
          [
            15.32484,
            -18.823836
          ],
          [
            15.389269,
            -18.298329
          ],
          [
            15.497078,
            -11.729508
          ],
          [
            15.524844,
            3.247402
          ],
          [
            15.355017,
            7.535122
          ],
          [
            15.092272,
            9.277398
          ],
          [
            14.829519,
            9.155262
          ],
          [
            14.751292,
            8.765212
          ],
          [
            14.576111,
            6.400437
          ],
          [
            14.5311,
            -15.671521
          ],
          [
            14.471776,
            -18.035577
          ],
          [
            14.304015,
            -18.528271
          ],
          [
            14.041261,
            -18.639398
          ],
          [
            9.31171,
            -18.691421
          ],
          [
            -12.759527,
            -18.645498
          ],
          [
            -15.124303,
            -18.883673
          ],
          [
            -15.515755,
            -19.086587
          ],
          [
            -15.387055,
            -19.398238
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 22.72727272727272,
      "length": 27.27472727272728,
      "loops": [
        [
          [
            -6.01369,
            -18.635937
          ],
          [
            14.041261,
            -18.982113
          ],
          [
            14.304015,
            -18.871565
          ],
          [
            14.450711,
            -18.561084
          ],
          [
            14.591151,
            -2.007655
          ],
          [
            14.761222,
            -1.567884
          ],
          [
            15.092272,
            -1.461494
          ],
          [
            15.355025,
            -1.589832
          ],
          [
            15.474913,
            -2.007655
          ],
          [
            15.423074,
            -17.424335
          ],
          [
            15.289715,
            -19.086587
          ],
          [
            14.829519,
            -19.643488
          ],
          [
            14.041261,
            -19.87165
          ],
          [
            9.31171,
            -20.020896
          ],
          [
            -9.080988,
            -20.020087
          ],
          [
            -14.86155,
            -19.814745
          ],
          [
            -15.378636,
            -19.612094
          ],
          [
            -15.541869,
            -19.086587
          ],
          [
            -15.369441,
            -18.823836
          ],
          [
            -14.598797,
            -18.68068
          ],
          [
            -10.217735,
            -18.765947
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.017761024999999986,
    0.017561334999999983,
    -0.371644255
  ],
  "construction_scale": 53.27898904865831,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
