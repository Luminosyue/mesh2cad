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
      "start": -39.876136727440375,
      "length": 12.08527284166315,
      "loops": [
        [
          [
            49.85088,
            -0.058204
          ],
          [
            49.091763,
            0.18478
          ],
          [
            47.573539,
            0.325669
          ],
          [
            34.475788,
            0.53626
          ],
          [
            5.822358,
            0.505051
          ],
          [
            -16.697976,
            0.183549
          ],
          [
            -36.181862,
            0.245449
          ],
          [
            -48.580695,
            -0.111765
          ],
          [
            -49.339811,
            -0.286082
          ],
          [
            -49.492191,
            -0.719271
          ],
          [
            -49.210134,
            -0.972308
          ],
          [
            -48.833735,
            -1.014536
          ],
          [
            -38.712234,
            -0.689227
          ],
          [
            13.919558,
            -0.298973
          ],
          [
            42.06691,
            -0.383387
          ],
          [
            49.59784,
            -0.660929
          ],
          [
            49.958866,
            -0.466233
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -27.792458931246323,
      "length": 58.00324846720054,
      "loops": [
        [
          [
            -40.558146,
            -0.440725
          ],
          [
            -20.2405,
            -0.002357
          ],
          [
            23.281944,
            0.214448
          ],
          [
            36.365242,
            0.11433
          ],
          [
            43.956367,
            -0.117325
          ],
          [
            49.091763,
            -0.539305
          ],
          [
            49.419881,
            -0.466233
          ],
          [
            49.571262,
            -0.213196
          ],
          [
            49.344803,
            0.17321
          ],
          [
            48.838727,
            0.365283
          ],
          [
            43.524943,
            0.735781
          ],
          [
            32.138256,
            1.03443
          ],
          [
            20.751568,
            1.060145
          ],
          [
            -23.27695,
            0.829144
          ],
          [
            -36.940974,
            0.601864
          ],
          [
            -48.580695,
            0.110876
          ],
          [
            -49.592847,
            -0.047979
          ],
          [
            -49.983002,
            -0.466233
          ],
          [
            -49.845883,
            -0.769605
          ],
          [
            -49.339811,
            -0.886436
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 30.209194490485125,
      "length": 9.668537282424348,
      "loops": [
        [
          [
            -30.615037,
            0.252352
          ],
          [
            7.846658,
            0.204077
          ],
          [
            37.958118,
            0.671331
          ],
          [
            47.826579,
            0.476638
          ],
          [
            49.091763,
            0.257907
          ],
          [
            49.402078,
            -0.213196
          ],
          [
            49.212709,
            -0.466233
          ],
          [
            48.838727,
            -0.539504
          ],
          [
            44.56548,
            -0.330499
          ],
          [
            33.937907,
            -0.228468
          ],
          [
            8.352733,
            -0.720563
          ],
          [
            -31.328445,
            -0.710482
          ],
          [
            -49.339811,
            -1.075272
          ],
          [
            -49.664836,
            -0.972308
          ],
          [
            -49.808556,
            -0.719271
          ],
          [
            -49.573128,
            -0.213196
          ],
          [
            -48.580695,
            -0.067539
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.004980299999999993,
    0.231010595,
    0.0019706400000000235
  ],
  "construction_scale": 51.30898349905143,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
