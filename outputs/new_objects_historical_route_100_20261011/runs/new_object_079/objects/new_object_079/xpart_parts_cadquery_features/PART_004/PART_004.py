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
            -19.005268,
            23.0829
          ],
          [
            -18.976341,
            -16.377565
          ],
          [
            -19.186527,
            -16.825737
          ],
          [
            -21.869759,
            -16.831377
          ],
          [
            -22.415707,
            -16.991601
          ],
          [
            -22.8103,
            -17.450858
          ],
          [
            -22.972068,
            -23.35397
          ],
          [
            -22.675302,
            -24.158939
          ],
          [
            -22.06316,
            -24.427263
          ],
          [
            -19.186527,
            -25.089705
          ],
          [
            -18.113234,
            -25.702891
          ],
          [
            -15.698325,
            -25.907913
          ],
          [
            19.1837,
            -25.984559
          ],
          [
            21.866932,
            -25.953741
          ],
          [
            22.671902,
            -25.675957
          ],
          [
            22.999113,
            -24.695587
          ],
          [
            22.946933,
            -22.817324
          ],
          [
            22.671902,
            -22.131361
          ],
          [
            21.866932,
            -21.714453
          ],
          [
            -3.623778,
            -19.260641
          ],
          [
            -4.079574,
            -19.060799
          ],
          [
            -4.150777,
            24.40757
          ],
          [
            -4.697071,
            25.243501
          ],
          [
            -5.50204,
            25.702861
          ],
          [
            -7.916949,
            26.008574
          ],
          [
            -10.868506,
            25.958745
          ],
          [
            -14.373654,
            25.404543
          ],
          [
            -18.113234,
            25.168797
          ],
          [
            -18.649881,
            24.89367
          ],
          [
            -18.862078,
            24.40757
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 93.94139393939393,
      "loops": [
        [
          [
            -18.988022,
            23.334276
          ],
          [
            -18.981732,
            -24.158939
          ],
          [
            -18.84614,
            -25.232233
          ],
          [
            -18.42376,
            -25.76888
          ],
          [
            -12.854133,
            -26.02119
          ],
          [
            20.793639,
            -26.013255
          ],
          [
            22.135255,
            -25.983716
          ],
          [
            22.65623,
            -25.76888
          ],
          [
            22.853831,
            -25.500556
          ],
          [
            23.071476,
            -24.051576
          ],
          [
            22.913976,
            -22.549
          ],
          [
            22.572658,
            -22.012353
          ],
          [
            21.866932,
            -21.687523
          ],
          [
            -3.623778,
            -19.276121
          ],
          [
            -4.064948,
            -19.060799
          ],
          [
            -4.036255,
            23.441641
          ],
          [
            -4.160429,
            24.398033
          ],
          [
            -4.458277,
            24.944218
          ],
          [
            -4.697071,
            25.257202
          ],
          [
            -5.50204,
            25.712559
          ],
          [
            -7.916949,
            26.004541
          ],
          [
            -10.868506,
            25.949562
          ],
          [
            -13.551739,
            25.559852
          ],
          [
            -17.864655,
            25.215424
          ],
          [
            -18.381557,
            25.062079
          ],
          [
            -18.775448,
            24.675894
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0005947050000000009,
    -0.05300214499999999,
    -0.004841155
  ],
  "construction_scale": 108.81703639521804,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
