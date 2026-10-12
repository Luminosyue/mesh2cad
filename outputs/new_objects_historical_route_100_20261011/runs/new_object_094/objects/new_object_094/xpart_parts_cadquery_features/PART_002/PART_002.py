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
      "start": -50.0,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            13.408746,
            -7.245992
          ],
          [
            -1.37423,
            -7.309621
          ],
          [
            -2.401481,
            -7.025749
          ],
          [
            -2.744205,
            -6.515986
          ],
          [
            -2.818369,
            -6.006232
          ],
          [
            -2.846482,
            2.532053
          ],
          [
            -2.820606,
            8.266986
          ],
          [
            -2.773826,
            8.776742
          ],
          [
            -2.393746,
            9.368959
          ],
          [
            -1.37423,
            9.670536
          ],
          [
            11.879473,
            9.691981
          ],
          [
            13.408746,
            9.605476
          ],
          [
            13.918506,
            9.26545
          ],
          [
            14.204295,
            8.776742
          ],
          [
            14.264095,
            8.266986
          ],
          [
            14.189077,
            -6.515986
          ],
          [
            13.918506,
            -6.950098
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -37.878787878787875,
      "length": 9.092909090909087,
      "loops": [
        [
          [
            13.926406,
            -6.91528
          ],
          [
            14.190836,
            -6.515986
          ],
          [
            14.274072,
            -6.006232
          ],
          [
            14.267807,
            8.266986
          ],
          [
            14.217372,
            8.776742
          ],
          [
            13.918506,
            9.258665
          ],
          [
            13.408746,
            9.614827
          ],
          [
            -1.883988,
            9.607864
          ],
          [
            -2.46651,
            9.286504
          ],
          [
            -2.916141,
            8.266986
          ],
          [
            -3.413261,
            7.829248
          ],
          [
            -13.09866,
            7.696563
          ],
          [
            -13.608416,
            7.639062
          ],
          [
            -14.116337,
            7.247469
          ],
          [
            -14.260212,
            6.227958
          ],
          [
            -14.217703,
            -1.418412
          ],
          [
            -14.198001,
            -1.928168
          ],
          [
            -13.881608,
            -2.428845
          ],
          [
            -13.608416,
            -2.578465
          ],
          [
            -12.588902,
            -2.641012
          ],
          [
            -3.413261,
            -2.674573
          ],
          [
            -2.903503,
            -2.931727
          ],
          [
            -2.763397,
            -6.515986
          ],
          [
            -2.576025,
            -7.025749
          ],
          [
            -1.883988,
            -7.803724
          ],
          [
            -1.706502,
            -8.555023
          ],
          [
            -1.37423,
            -9.006998
          ],
          [
            -0.354713,
            -9.269748
          ],
          [
            1.684314,
            -9.398818
          ],
          [
            11.369715,
            -9.604991
          ],
          [
            11.879473,
            -9.482173
          ],
          [
            12.185475,
            -9.064776
          ],
          [
            12.391128,
            -7.535503
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.78787878787879,
      "length": 60.608060606060604,
      "loops": [
        [
          [
            -2.841145,
            -5.496476
          ],
          [
            -2.776327,
            8.776742
          ],
          [
            -2.393746,
            9.366263
          ],
          [
            -1.883988,
            9.631322
          ],
          [
            12.898986,
            9.690241
          ],
          [
            13.408746,
            9.625829
          ],
          [
            13.918506,
            9.292879
          ],
          [
            14.22608,
            8.776742
          ],
          [
            14.275826,
            8.266986
          ],
          [
            14.276044,
            -5.313392
          ],
          [
            14.166597,
            -6.515986
          ],
          [
            13.918506,
            -6.911926
          ],
          [
            13.408746,
            -7.237141
          ],
          [
            11.369715,
            -7.320702
          ],
          [
            -1.37423,
            -7.302431
          ],
          [
            -2.393746,
            -6.967682
          ],
          [
            -2.7247,
            -6.515986
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 31.818181818181813,
      "length": 12.123212121212125,
      "loops": [
        [
          [
            -2.840467,
            -6.006232
          ],
          [
            -2.84813,
            8.266986
          ],
          [
            -2.748386,
            8.776742
          ],
          [
            -2.393746,
            9.315992
          ],
          [
            -1.883988,
            9.606282
          ],
          [
            -1.37423,
            9.66377
          ],
          [
            12.898986,
            9.699679
          ],
          [
            13.408746,
            9.629123
          ],
          [
            13.945219,
            9.286504
          ],
          [
            14.22506,
            8.776742
          ],
          [
            14.272445,
            8.266986
          ],
          [
            14.280276,
            -6.006232
          ],
          [
            14.187398,
            -6.515986
          ],
          [
            13.918506,
            -6.926773
          ],
          [
            12.533904,
            -7.535503
          ],
          [
            12.285644,
            -9.064776
          ],
          [
            11.879473,
            -9.593151
          ],
          [
            9.330682,
            -9.696467
          ],
          [
            8.922026,
            -9.57454
          ],
          [
            8.549748,
            -9.064776
          ],
          [
            8.311169,
            -7.945041
          ],
          [
            7.801409,
            -7.405545
          ],
          [
            7.291651,
            -7.307307
          ],
          [
            -1.37423,
            -7.30981
          ],
          [
            -2.358902,
            -7.025749
          ],
          [
            -2.743277,
            -6.515986
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
            -1.37423,
            9.656462
          ],
          [
            13.408746,
            9.626863
          ],
          [
            13.95685,
            9.286504
          ],
          [
            14.231079,
            8.776742
          ],
          [
            14.283478,
            -6.006232
          ],
          [
            14.198158,
            -6.515986
          ],
          [
            13.918506,
            -6.959669
          ],
          [
            13.408746,
            -7.240063
          ],
          [
            11.641275,
            -7.350013
          ],
          [
            -1.37423,
            -7.297562
          ],
          [
            -2.393746,
            -7.035628
          ],
          [
            -2.762305,
            -6.515986
          ],
          [
            -2.855136,
            -4.986714
          ],
          [
            -2.845154,
            8.266986
          ],
          [
            -2.748578,
            8.776742
          ],
          [
            -2.419961,
            9.286504
          ],
          [
            -1.883988,
            9.598572
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.41865319,
    -0.011432004999999995,
    0.16445998
  ],
  "construction_scale": 206.72949575719753,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
