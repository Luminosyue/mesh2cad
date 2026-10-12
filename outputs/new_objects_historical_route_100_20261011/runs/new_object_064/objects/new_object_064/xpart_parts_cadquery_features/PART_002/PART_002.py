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
      "start": -50.00000000000001,
      "length": 21.214121212121213,
      "loops": [
        [
          [
            2.280967,
            2.089388
          ],
          [
            2.772994,
            2.272032
          ],
          [
            3.010206,
            2.646904
          ],
          [
            2.951525,
            5.468551
          ],
          [
            2.633672,
            5.847973
          ],
          [
            2.280967,
            5.97856
          ],
          [
            1.222849,
            5.94628
          ],
          [
            0.870143,
            5.602842
          ],
          [
            0.740609,
            5.115845
          ],
          [
            0.784494,
            2.646904
          ],
          [
            1.222849,
            2.159123
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.00000000000001,
      "length": 21.214121212121213,
      "loops": [
        [
          [
            2.280967,
            -5.113804
          ],
          [
            2.321297,
            -3.033072
          ],
          [
            2.15916,
            -2.290979
          ],
          [
            1.575555,
            -1.941341
          ],
          [
            0.517437,
            -1.974298
          ],
          [
            0.164731,
            -2.169154
          ],
          [
            -0.053165,
            -2.643685
          ],
          [
            -0.081322,
            -4.054509
          ],
          [
            -0.069731,
            -4.759921
          ],
          [
            0.164731,
            -5.380239
          ],
          [
            0.517437,
            -5.605886
          ],
          [
            1.575555,
            -5.667077
          ],
          [
            2.045501,
            -5.465332
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -28.787878787878793,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            0.647911,
            0.530668
          ],
          [
            0.708195,
            6.52667
          ],
          [
            0.94846,
            7.168294
          ],
          [
            1.575555,
            7.416219
          ],
          [
            2.675427,
            7.23208
          ],
          [
            2.946129,
            6.879376
          ],
          [
            3.057122,
            6.173964
          ],
          [
            3.023647,
            0.530668
          ],
          [
            2.633672,
            0.035429
          ],
          [
            1.840217,
            -0.174744
          ],
          [
            1.672061,
            -0.52745
          ],
          [
            1.693732,
            -6.523452
          ],
          [
            1.374944,
            -7.228863
          ],
          [
            0.517437,
            -7.455147
          ],
          [
            -0.187975,
            -7.268268
          ],
          [
            -0.545498,
            -6.523452
          ],
          [
            -0.683046,
            -0.880156
          ],
          [
            -0.437674,
            -0.174744
          ],
          [
            0.517437,
            0.218087
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.72727272727273,
      "length": 33.335333333333345,
      "loops": [
        [
          [
            0.870143,
            -7.51027
          ],
          [
            1.575555,
            -7.406078
          ],
          [
            2.024615,
            -6.876158
          ],
          [
            2.379004,
            2.646904
          ],
          [
            1.575555,
            6.002879
          ],
          [
            0.870143,
            6.542387
          ],
          [
            0.58814,
            7.584788
          ],
          [
            0.218466,
            7.937494
          ],
          [
            -0.893387,
            7.979948
          ],
          [
            -1.246093,
            7.86795
          ],
          [
            -1.651948,
            7.23208
          ],
          [
            -1.872879,
            -2.643685
          ],
          [
            -1.192967,
            -5.818038
          ],
          [
            -0.358661,
            -6.523452
          ],
          [
            0.164731,
            -7.328786
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 10.606060606060609,
      "length": 18.18381818181818,
      "loops": [
        [
          [
            0.31822,
            4.057727
          ],
          [
            1.286732,
            1.23608
          ],
          [
            1.232907,
            -4.759921
          ],
          [
            0.968977,
            -5.465332
          ],
          [
            0.164731,
            -5.76412
          ],
          [
            -0.589309,
            -5.417327
          ],
          [
            -1.459369,
            -3.701803
          ],
          [
            -2.392657,
            -1.232862
          ],
          [
            -2.392856,
            5.468551
          ],
          [
            -2.117397,
            6.173964
          ],
          [
            -1.246093,
            6.405996
          ],
          [
            -0.626517,
            6.147381
          ],
          [
            -0.430245,
            5.821258
          ],
          [
            -0.269292,
            4.76314
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 28.78787878787879,
      "length": 21.214121212121217,
      "loops": [
        [
          [
            -2.233252,
            -1.585567
          ],
          [
            -3.095521,
            1.23608
          ],
          [
            -3.044559,
            2.999609
          ],
          [
            -2.656916,
            3.358508
          ],
          [
            -1.598798,
            3.418268
          ],
          [
            -0.907987,
            2.875644
          ],
          [
            0.133392,
            0.530668
          ],
          [
            0.504961,
            -0.880156
          ],
          [
            0.437166,
            -2.290979
          ],
          [
            0.164731,
            -2.597801
          ],
          [
            -0.187975,
            -2.715118
          ],
          [
            -0.893387,
            -2.723712
          ],
          [
            -1.598798,
            -2.4167
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.15040275,
    -0.013480760000000001,
    0.0012216599999999994
  ],
  "construction_scale": 143.0379796446084,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
