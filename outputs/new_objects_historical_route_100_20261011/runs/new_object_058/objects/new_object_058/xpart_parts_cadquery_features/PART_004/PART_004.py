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
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -31.754615772966808,
      "length": 3.8503145207481073,
      "loops": [
        [
          [
            -49.192424,
            -5.941731
          ],
          [
            49.199036,
            -5.910883
          ],
          [
            49.7847,
            -5.530624
          ],
          [
            49.941614,
            -4.766174
          ],
          [
            49.904111,
            4.60444
          ],
          [
            49.7847,
            5.232802
          ],
          [
            49.199036,
            5.75439
          ],
          [
            45.099392,
            5.926302
          ],
          [
            -44.924717,
            5.938783
          ],
          [
            -48.606763,
            5.843601
          ],
          [
            -49.192424,
            5.752298
          ],
          [
            -49.778087,
            5.206642
          ],
          [
            -49.969193,
            3.433113
          ],
          [
            -49.991844,
            -4.180509
          ],
          [
            -49.934153,
            -5.351838
          ],
          [
            -49.778087,
            -5.638368
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -27.90557143684962,
      "length": 59.661457394447346,
      "loops": [
        [
          [
            -45.09278,
            -4.972178
          ],
          [
            45.099392,
            -5.00376
          ],
          [
            47.442046,
            -5.479614
          ],
          [
            49.199036,
            -5.365441
          ],
          [
            49.7847,
            -4.937265
          ],
          [
            49.956607,
            -4.180509
          ],
          [
            49.945635,
            4.018779
          ],
          [
            49.7847,
            4.732169
          ],
          [
            49.199036,
            5.191875
          ],
          [
            46.856385,
            5.35263
          ],
          [
            46.107731,
            5.190103
          ],
          [
            45.607142,
            4.60444
          ],
          [
            45.480012,
            4.018779
          ],
          [
            45.384216,
            -0.666531
          ],
          [
            45.099392,
            -0.956494
          ],
          [
            44.513731,
            -1.046454
          ],
          [
            -43.33579,
            -1.06213
          ],
          [
            -45.09278,
            -1.008377
          ],
          [
            -45.528797,
            -0.666531
          ],
          [
            -45.633318,
            4.018779
          ],
          [
            -45.740424,
            4.60444
          ],
          [
            -46.238882,
            5.190103
          ],
          [
            -47.435434,
            5.411352
          ],
          [
            -49.192424,
            5.287825
          ],
          [
            -49.778087,
            4.735687
          ],
          [
            -49.979425,
            3.433113
          ],
          [
            -49.973289,
            -4.180509
          ],
          [
            -49.778087,
            -4.841526
          ],
          [
            -49.192424,
            -5.326231
          ],
          [
            -47.435434,
            -5.453861
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -1.3920000000000599e-05,
    0.187742815,
    0.056378115000000006
  ],
  "construction_scale": 237.51263092171243,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
