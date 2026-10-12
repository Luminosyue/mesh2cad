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
      "length": 6.062606060606062,
      "loops": [
        [
          [
            -4.779515,
            4.160363
          ],
          [
            -6.053912,
            3.795086
          ],
          [
            -6.692934,
            2.648156
          ],
          [
            -7.953116,
            -1.079377
          ],
          [
            -7.824678,
            -1.458353
          ],
          [
            -7.124563,
            -2.170325
          ],
          [
            -6.677745,
            -2.412442
          ],
          [
            -2.950215,
            -3.254809
          ],
          [
            5.65178,
            -6.253178
          ],
          [
            7.945646,
            -6.242665
          ],
          [
            8.506398,
            -5.95384
          ],
          [
            10.128447,
            -0.50591
          ],
          [
            10.151435,
            -0.219178
          ],
          [
            9.952777,
            0.093719
          ],
          [
            7.512438,
            1.501221
          ],
          [
            2.497715,
            3.042486
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 39.39593939393939,
      "loops": [
        [
          [
            -11.703298,
            -0.50591
          ],
          [
            -9.885307,
            5.228752
          ],
          [
            -9.550642,
            5.515484
          ],
          [
            -7.385969,
            5.798611
          ],
          [
            5.226423,
            2.88834
          ],
          [
            8.657734,
            1.354196
          ],
          [
            10.269374,
            0.354289
          ],
          [
            10.619645,
            -0.219178
          ],
          [
            9.160691,
            -5.667108
          ],
          [
            8.904881,
            -6.018293
          ],
          [
            8.519111,
            -6.183524
          ],
          [
            6.225246,
            -6.306295
          ],
          [
            4.218114,
            -6.133803
          ],
          [
            0.915939,
            -5.208745
          ],
          [
            -1.781178,
            -4.233441
          ],
          [
            -9.850204,
            -1.94787
          ],
          [
            -11.265476,
            -1.111685
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.545454545454547,
      "length": 33.33533333333333,
      "loops": [
        [
          [
            -9.986612,
            5.515484
          ],
          [
            -11.521071,
            -0.219178
          ],
          [
            -11.265476,
            -0.795565
          ],
          [
            -9.635583,
            -2.087306
          ],
          [
            -6.964478,
            -2.826093
          ],
          [
            4.701074,
            -5.492499
          ],
          [
            8.232376,
            -5.777692
          ],
          [
            9.952777,
            -5.68177
          ],
          [
            10.36934,
            -5.380373
          ],
          [
            11.950934,
            0.354289
          ],
          [
            11.673175,
            0.701699
          ],
          [
            9.666043,
            1.92249
          ],
          [
            7.568405,
            2.79996
          ],
          [
            4.218114,
            3.759335
          ],
          [
            -0.460122,
            4.920543
          ],
          [
            -5.24408,
            5.898139
          ],
          [
            -9.545077,
            6.002348
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.787878787878782,
      "length": 15.153515151515156,
      "loops": [
        [
          [
            11.392014,
            -0.535072
          ],
          [
            11.749791,
            0.354289
          ],
          [
            11.513143,
            0.927757
          ],
          [
            9.614176,
            2.345458
          ],
          [
            7.436934,
            3.508355
          ],
          [
            2.784447,
            4.805479
          ],
          [
            -1.516549,
            5.70776
          ],
          [
            -4.670613,
            6.17156
          ],
          [
            -7.187586,
            6.070208
          ],
          [
            -8.971611,
            5.76554
          ],
          [
            -9.258344,
            5.546939
          ],
          [
            -12.077428,
            -0.792645
          ],
          [
            -12.030166,
            -1.079377
          ],
          [
            -11.552209,
            -1.678535
          ],
          [
            -9.831811,
            -2.419181
          ],
          [
            -5.817547,
            -3.06433
          ],
          [
            2.784447,
            -5.443871
          ],
          [
            4.79158,
            -5.778782
          ],
          [
            6.511979,
            -5.827111
          ],
          [
            9.952777,
            -5.560189
          ],
          [
            10.222619,
            -5.380373
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 43.93939393939394,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            10.295457,
            -5.093641
          ],
          [
            11.647922,
            0.641021
          ],
          [
            11.386442,
            1.020011
          ],
          [
            10.526243,
            1.497126
          ],
          [
            7.085446,
            2.422863
          ],
          [
            -6.391012,
            5.192386
          ],
          [
            -9.258168,
            5.414165
          ],
          [
            -9.831811,
            5.114076
          ],
          [
            -10.164832,
            4.655285
          ],
          [
            -11.69249,
            -0.219178
          ],
          [
            -11.677675,
            -0.792645
          ],
          [
            -11.265476,
            -1.209814
          ],
          [
            -8.684878,
            -1.821989
          ],
          [
            -2.950215,
            -2.68399
          ],
          [
            9.37931,
            -5.445036
          ],
          [
            10.052917,
            -5.380373
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.05941294500000002,
    0.10181140500000001,
    -0.414838775
  ],
  "construction_scale": 116.28306530765097,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
