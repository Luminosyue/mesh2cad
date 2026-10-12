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
            -10.439701,
            28.091498
          ],
          [
            -10.378656,
            38.953774
          ],
          [
            -10.242721,
            39.421442
          ],
          [
            -9.729978,
            39.705239
          ],
          [
            -8.448121,
            39.805042
          ],
          [
            10.52337,
            39.649915
          ],
          [
            11.292484,
            39.416047
          ],
          [
            11.603554,
            38.859098
          ],
          [
            11.548856,
            37.598955
          ],
          [
            11.292484,
            37.241444
          ],
          [
            11.036113,
            38.748926
          ],
          [
            10.52337,
            39.077224
          ],
          [
            -8.286424,
            39.297206
          ],
          [
            -9.484476,
            39.115472
          ],
          [
            -9.403413,
            28.347868
          ],
          [
            -9.906591,
            17.580266
          ],
          [
            -9.986349,
            10.957628
          ],
          [
            -10.172715,
            12.522842
          ],
          [
            -10.064482,
            17.067524
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 48.48684848484849,
      "loops": [
        [
          [
            -10.535746,
            10.914608
          ],
          [
            -10.498795,
            38.859098
          ],
          [
            -10.399812,
            39.628216
          ],
          [
            -9.986349,
            40.068344
          ],
          [
            -8.568394,
            40.161762
          ],
          [
            8.352125,
            39.929255
          ],
          [
            10.779741,
            39.761003
          ],
          [
            11.422973,
            39.371842
          ],
          [
            11.635664,
            38.859098
          ],
          [
            11.662335,
            38.210258
          ],
          [
            11.558668,
            37.0645
          ],
          [
            11.292484,
            36.47259
          ],
          [
            11.036113,
            36.507463
          ],
          [
            10.940363,
            36.808129
          ],
          [
            10.970802,
            38.859098
          ],
          [
            10.779741,
            39.150831
          ],
          [
            10.266999,
            39.312659
          ],
          [
            -8.704492,
            39.629091
          ],
          [
            -9.217235,
            39.582426
          ],
          [
            -9.568479,
            39.371842
          ],
          [
            -9.423412,
            32.570085
          ],
          [
            -9.449505,
            20.656725
          ],
          [
            -10.257298,
            -36.393844
          ],
          [
            -10.498896,
            -40.616061
          ],
          [
            -10.755463,
            -41.059365
          ],
          [
            -11.011835,
            -41.139001
          ],
          [
            -11.392009,
            -40.872435
          ],
          [
            -11.478356,
            -40.103317
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 4.545454545454547,
      "length": 45.456545454545456,
      "loops": [
        [
          [
            -11.141119,
            5.787178
          ],
          [
            -11.116317,
            38.338245
          ],
          [
            -10.968414,
            40.39733
          ],
          [
            -10.755463,
            40.668262
          ],
          [
            -10.156612,
            40.909562
          ],
          [
            -6.389036,
            40.992046
          ],
          [
            8.480511,
            40.730031
          ],
          [
            10.266999,
            40.627895
          ],
          [
            10.976065,
            40.39733
          ],
          [
            11.348982,
            39.884586
          ],
          [
            11.461608,
            39.115472
          ],
          [
            11.292484,
            37.2524
          ],
          [
            11.036113,
            36.818575
          ],
          [
            10.745745,
            37.0645
          ],
          [
            10.793659,
            39.628216
          ],
          [
            10.52337,
            39.980257
          ],
          [
            10.010627,
            40.116876
          ],
          [
            -7.422635,
            40.480817
          ],
          [
            -9.473606,
            40.40757
          ],
          [
            -10.13225,
            40.140956
          ],
          [
            -9.948645,
            25.784154
          ],
          [
            -9.983806,
            8.094521
          ],
          [
            -10.364342,
            -39.334203
          ],
          [
            -10.499092,
            -40.071203
          ],
          [
            -11.011835,
            -40.177799
          ],
          [
            -11.432247,
            -40.103317
          ],
          [
            -11.599961,
            -39.846947
          ],
          [
            -11.653607,
            -38.052348
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.007452740000000013,
    -0.00023350500000000884,
    0.011967089999999958
  ],
  "construction_scale": 51.985030723257125,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
