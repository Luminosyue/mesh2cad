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
      "start": -50.0,
      "length": 6.062606060606062,
      "loops": [
        [
          [
            41.625412,
            31.031186
          ],
          [
            41.763563,
            -31.326383
          ],
          [
            41.630383,
            -33.133845
          ],
          [
            41.044378,
            -34.037582
          ],
          [
            40.133853,
            -34.279024
          ],
          [
            -35.401726,
            -34.300012
          ],
          [
            -36.683442,
            -34.237877
          ],
          [
            -37.158892,
            -34.037582
          ],
          [
            -37.587171,
            -33.676332
          ],
          [
            -37.862077,
            -33.133845
          ],
          [
            -38.006388,
            -30.948402
          ],
          [
            -37.983171,
            27.794237
          ],
          [
            -37.934639,
            31.934919
          ],
          [
            -37.85401,
            32.838652
          ],
          [
            -37.500787,
            33.742385
          ],
          [
            -36.683442,
            34.242236
          ],
          [
            -35.401726,
            34.323298
          ],
          [
            37.422654,
            34.223553
          ],
          [
            39.608103,
            34.139889
          ],
          [
            40.873072,
            33.742385
          ],
          [
            41.463789,
            32.838652
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.93939393939394,
      "length": 87.88078787878787,
      "loops": [
        [
          [
            -36.456958,
            -32.859612
          ],
          [
            -35.779709,
            -33.499169
          ],
          [
            -34.875972,
            -33.625328
          ],
          [
            -33.06851,
            -33.531667
          ],
          [
            -31.261041,
            -32.924356
          ],
          [
            -27.646114,
            -32.817194
          ],
          [
            32.903987,
            -32.876973
          ],
          [
            33.807731,
            -32.898602
          ],
          [
            35.615185,
            -33.484499
          ],
          [
            36.518925,
            -33.60549
          ],
          [
            38.326394,
            -33.550068
          ],
          [
            39.446455,
            -33.133845
          ],
          [
            40.094937,
            -32.23012
          ],
          [
            40.245252,
            -30.422651
          ],
          [
            40.291096,
            30.127454
          ],
          [
            40.142411,
            31.934919
          ],
          [
            39.444143,
            32.838652
          ],
          [
            37.422654,
            33.167369
          ],
          [
            35.615185,
            33.028056
          ],
          [
            34.711456,
            32.131733
          ],
          [
            34.472221,
            31.031186
          ],
          [
            34.400058,
            -25.903987
          ],
          [
            33.807731,
            -26.713767
          ],
          [
            32.903987,
            -27.010808
          ],
          [
            32.000258,
            -27.061831
          ],
          [
            9.787292,
            -27.098262
          ],
          [
            -29.453579,
            -27.055699
          ],
          [
            -30.357312,
            -26.840702
          ],
          [
            -31.261041,
            -25.975265
          ],
          [
            -31.456706,
            -25.000254
          ],
          [
            -31.351097,
            31.031186
          ],
          [
            -31.486977,
            31.934919
          ],
          [
            -32.260738,
            32.838652
          ],
          [
            -33.06851,
            33.05635
          ],
          [
            -34.875972,
            33.174012
          ],
          [
            -35.779709,
            33.052109
          ],
          [
            -36.168492,
            32.838652
          ],
          [
            -36.899105,
            31.934919
          ],
          [
            -37.079792,
            26.512522
          ],
          [
            -37.053921,
            -30.422651
          ],
          [
            -36.789573,
            -32.23012
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
            -31.221758,
            -23.192788
          ],
          [
            -31.116525,
            -25.903987
          ],
          [
            -30.444409,
            -26.807719
          ],
          [
            -29.453579,
            -27.069658
          ],
          [
            28.385334,
            -27.030469
          ],
          [
            32.000258,
            -26.912603
          ],
          [
            32.684051,
            -26.806745
          ],
          [
            33.478572,
            -26.259386
          ],
          [
            33.747572,
            -25.903987
          ],
          [
            34.032046,
            -24.096521
          ],
          [
            34.181662,
            -15.962922
          ],
          [
            34.148376,
            26.512522
          ],
          [
            33.923544,
            31.934919
          ],
          [
            34.423637,
            32.884892
          ],
          [
            35.615185,
            33.52662
          ],
          [
            36.189768,
            33.644119
          ],
          [
            39.230124,
            33.765965
          ],
          [
            40.133853,
            33.489477
          ],
          [
            40.895119,
            32.838652
          ],
          [
            41.168057,
            31.934919
          ],
          [
            41.217177,
            30.456608
          ],
          [
            41.206231,
            -29.518921
          ],
          [
            41.019572,
            -32.903291
          ],
          [
            40.948851,
            -33.133845
          ],
          [
            40.133853,
            -33.89371
          ],
          [
            39.230124,
            -34.174164
          ],
          [
            36.518925,
            -34.274212
          ],
          [
            30.192788,
            -33.969556
          ],
          [
            21.484621,
            -33.815602
          ],
          [
            2.177072,
            -33.909766
          ],
          [
            -5.956519,
            -33.720683
          ],
          [
            -28.22069,
            -33.593406
          ],
          [
            -33.972247,
            -34.253713
          ],
          [
            -38.840716,
            -34.037582
          ],
          [
            -40.298376,
            -33.560818
          ],
          [
            -40.750001,
            -33.133845
          ],
          [
            -41.044117,
            -32.23012
          ],
          [
            -41.082619,
            -31.326383
          ],
          [
            -40.973058,
            31.031186
          ],
          [
            -40.8656,
            31.934919
          ],
          [
            -40.512892,
            32.838652
          ],
          [
            -40.298376,
            33.036287
          ],
          [
            -36.683442,
            34.228682
          ],
          [
            -33.972247,
            34.181183
          ],
          [
            -32.241357,
            33.742385
          ],
          [
            -31.261041,
            32.855697
          ],
          [
            -31.0674,
            31.934919
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.344206375,
    -0.08220226,
    0.059346815000000004
  ],
  "construction_scale": 366.50395723485224,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
