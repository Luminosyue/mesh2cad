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
  "operation": "extrude",
  "basis": [
    [
      -0.2735700821784328,
      0.32936909956684124,
      -0.9037009496439701
    ],
    [
      -0.38906447192790766,
      0.8213566110711906,
      0.4171356543537212
    ],
    [
      0.8796523442930984,
      0.4657137679950818,
      -0.09655278079620097
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -6.613161249885788,
      "length": 13.256829182960413,
      "loops": [
        [
          [
            46.563843,
            16.082797
          ],
          [
            22.195826,
            16.255757
          ],
          [
            -22.595745,
            16.140641
          ],
          [
            -45.481132,
            16.339908
          ],
          [
            -46.91702,
            16.187648
          ],
          [
            -47.731956,
            15.484708
          ],
          [
            -47.967541,
            14.383694
          ],
          [
            -48.16547,
            -15.049217
          ],
          [
            -47.862178,
            -15.792183
          ],
          [
            -47.388528,
            -16.19139
          ],
          [
            -46.760758,
            -16.256704
          ],
          [
            -42.882579,
            -16.138882
          ],
          [
            45.209627,
            -16.556006
          ],
          [
            46.58433,
            -16.438592
          ],
          [
            47.335446,
            -16.123014
          ],
          [
            47.797839,
            -15.584558
          ],
          [
            48.041117,
            -14.283597
          ],
          [
            48.043223,
            9.293053
          ],
          [
            48.202064,
            13.932306
          ],
          [
            47.995013,
            15.108218
          ],
          [
            47.652656,
            15.600379
          ]
        ],
        {
          "center": [
            0.4091203435051387,
            -0.005243792749366816
          ],
          "radius": 6.504468495688462
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    0.161103625,
    0.527876755,
    -0.3484987
  ],
  "construction_scale": 120.56054189938166,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
