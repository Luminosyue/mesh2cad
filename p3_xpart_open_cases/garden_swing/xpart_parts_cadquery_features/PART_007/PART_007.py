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
      -0.010924684142318751,
      -0.6092817053559897,
      -0.792878587675873
    ],
    [
      0.007415587021169382,
      0.7928547360686278,
      -0.6093655524910135
    ],
    [
      0.9999128263731403,
      -0.01253678635230619,
      -0.004143506055817432
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -50.02482231985153,
      "length": 99.9913912144742,
      "loops": [
        [
          [
            0.037073,
            -3.272882
          ],
          [
            -1.002253,
            -3.188383
          ],
          [
            -2.380684,
            -2.42129
          ],
          [
            -3.22952,
            -1.247222
          ],
          [
            -3.54908,
            0.333577
          ],
          [
            -3.461572,
            1.131371
          ],
          [
            -2.892448,
            1.964674
          ],
          [
            -2.011662,
            2.719685
          ],
          [
            -0.628978,
            3.308121
          ],
          [
            0.951004,
            3.14217
          ],
          [
            2.115366,
            2.494867
          ],
          [
            3.09574,
            1.056606
          ],
          [
            3.253375,
            0.081921
          ],
          [
            3.047237,
            -1.14252
          ],
          [
            2.207245,
            -2.294503
          ],
          [
            1.266921,
            -2.972046
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 3,
  "center": [
    -0.010303895000000007,
    -0.534496455,
    -0.86197864
  ],
  "construction_scale": 58.72471057775971,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
