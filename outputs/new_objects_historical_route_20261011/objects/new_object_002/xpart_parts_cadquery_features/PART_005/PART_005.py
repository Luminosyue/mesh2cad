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
      "start": -2.068182798435265,
      "length": 0.25077155136469703,
      "loops": [
        [
          [
            -48.427529,
            -1.242244
          ],
          [
            -9.563459,
            2.037298
          ],
          [
            -7.231993,
            2.284287
          ],
          [
            -6.385683,
            2.531276
          ],
          [
            -6.946554,
            2.943318
          ],
          [
            -7.852574,
            3.08507
          ],
          [
            -8.099564,
            2.965136
          ],
          [
            -8.593542,
            3.132235
          ],
          [
            -9.396552,
            2.963215
          ],
          [
            -9.694614,
            3.159132
          ],
          [
            -11.557417,
            2.908168
          ],
          [
            -13.115825,
            2.948783
          ],
          [
            -13.533332,
            2.750792
          ],
          [
            -15.015269,
            2.858755
          ],
          [
            -15.262259,
            2.728729
          ],
          [
            -15.756237,
            2.858171
          ],
          [
            -16.497206,
            2.715763
          ],
          [
            -16.882422,
            2.887029
          ],
          [
            -18.028482,
            2.728926
          ],
          [
            -18.144351,
            2.860047
          ],
          [
            -19.046194,
            2.946162
          ],
          [
            -19.466615,
            2.77273
          ],
          [
            -20.449038,
            3.076687
          ],
          [
            -20.696026,
            2.949986
          ],
          [
            -20.819894,
            3.148378
          ],
          [
            -21.342828,
            3.119423
          ],
          [
            -21.442747,
            3.266495
          ],
          [
            -22.041326,
            3.161894
          ],
          [
            -22.295638,
            3.401561
          ],
          [
            -23.968437,
            3.704677
          ],
          [
            -24.055601,
            3.864503
          ],
          [
            -25.725232,
            3.923798
          ],
          [
            -36.451735,
            3.025256
          ],
          [
            -39.467229,
            2.580088
          ],
          [
            -49.099819,
            1.581109
          ],
          [
            -49.53821,
            1.29633
          ],
          [
            -49.26767,
            -1.094428
          ],
          [
            -49.152217,
            -1.225964
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -2.068182798435265,
      "length": 0.25077155136469703,
      "loops": [
        [
          [
            -6.164143,
            2.778265
          ],
          [
            -6.286686,
            2.615228
          ],
          [
            -6.090714,
            2.778265
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.8174939743825056,
      "length": 3.8857595001297107,
      "loops": [
        [
          [
            -14.328319,
            5.989129
          ],
          [
            -7.358595,
            6.59346
          ],
          [
            -2.665795,
            6.680126
          ],
          [
            0.264572,
            6.483108
          ],
          [
            49.448985,
            -3.207743
          ],
          [
            49.798885,
            -3.396471
          ],
          [
            49.911455,
            -3.643461
          ],
          [
            49.695973,
            -5.35659
          ],
          [
            49.329508,
            -6.607334
          ],
          [
            48.708017,
            -6.745612
          ],
          [
            11.778785,
            -0.049408
          ],
          [
            -0.689879,
            1.917013
          ],
          [
            -5.0165,
            1.944078
          ],
          [
            -9.828491,
            1.629087
          ],
          [
            -48.852827,
            -1.715116
          ],
          [
            -49.593795,
            -1.716454
          ],
          [
            -49.852712,
            -1.420555
          ],
          [
            -49.850223,
            1.29633
          ],
          [
            -49.755481,
            1.543319
          ],
          [
            -49.302362,
            1.790307
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.16501287999999997,
    -0.0005100499999999841,
    -0.20527589
  ],
  "construction_scale": 100.16523858748823,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
