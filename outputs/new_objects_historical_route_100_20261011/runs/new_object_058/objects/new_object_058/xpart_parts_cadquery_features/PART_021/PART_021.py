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
      "start": -11.085445557952836,
      "length": 7.390740456457541,
      "loops": [
        [
          [
            -3.057668,
            49.234671
          ],
          [
            -2.983732,
            -38.630931
          ],
          [
            -2.749296,
            -38.937865
          ],
          [
            -2.235467,
            -39.060663
          ],
          [
            7.013541,
            -39.161178
          ],
          [
            7.793079,
            -39.658597
          ],
          [
            8.040097,
            -40.172433
          ],
          [
            8.03582,
            -40.686267
          ],
          [
            6.551295,
            -42.7416
          ],
          [
            0.333705,
            -49.711684
          ],
          [
            -0.180133,
            -49.910219
          ],
          [
            -6.859969,
            -49.975205
          ],
          [
            -7.373809,
            -49.912879
          ],
          [
            -7.887639,
            -49.493953
          ],
          [
            -8.147943,
            -48.907609
          ],
          [
            -8.135215,
            48.638556
          ],
          [
            -7.887639,
            49.5301
          ],
          [
            -7.373809,
            49.924516
          ],
          [
            -3.776968,
            49.961939
          ],
          [
            -3.423673,
            49.748507
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.6951485193176126,
      "length": 3.359669344474693,
      "loops": [
        [
          [
            -8.123036,
            48.720842
          ],
          [
            -8.130399,
            -48.907609
          ],
          [
            -7.956182,
            -49.421443
          ],
          [
            -7.373809,
            -49.9186
          ],
          [
            -4.290798,
            -49.971299
          ],
          [
            -3.776968,
            -49.813877
          ],
          [
            -3.490297,
            -49.421443
          ],
          [
            -3.067014,
            -46.338441
          ],
          [
            -2.657718,
            -44.796936
          ],
          [
            -2.681967,
            -40.172433
          ],
          [
            -2.91491,
            -38.630931
          ],
          [
            -2.938618,
            -35.547924
          ],
          [
            -2.933293,
            48.207006
          ],
          [
            -3.035473,
            49.234671
          ],
          [
            -3.380424,
            49.748507
          ],
          [
            -3.776968,
            49.962331
          ],
          [
            -7.373809,
            49.95123
          ],
          [
            -7.887639,
            49.542969
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -0.33592259266523783,
      "length": 11.421811568440392,
      "loops": [
        [
          [
            -2.856918,
            -44.796936
          ],
          [
            -2.714997,
            -40.686267
          ],
          [
            -2.914582,
            -39.658597
          ],
          [
            -3.263136,
            -39.373905
          ],
          [
            -3.776968,
            -39.302583
          ],
          [
            -5.318468,
            -39.329017
          ],
          [
            -5.832308,
            -39.587021
          ],
          [
            -6.153526,
            -40.172433
          ],
          [
            -6.227946,
            -40.686267
          ],
          [
            -6.237583,
            -43.853933
          ],
          [
            -6.040547,
            -44.796936
          ],
          [
            -5.318468,
            -45.435911
          ],
          [
            -3.776968,
            -45.494183
          ],
          [
            -3.263136,
            -45.421599
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.455312335,
    -0.002017679999999994,
    -0.16561054
  ],
  "construction_scale": 208.38255502935257,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
