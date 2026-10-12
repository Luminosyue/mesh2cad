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
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -49.48946227594369,
      "length": 6.000702278605423,
      "loops": [
        [
          [
            -18.070569,
            -35.336162
          ],
          [
            -18.780649,
            48.271584
          ],
          [
            -18.945885,
            49.05296
          ],
          [
            -19.351082,
            49.496134
          ],
          [
            -20.132465,
            49.716927
          ],
          [
            -29.50903,
            49.486852
          ],
          [
            -30.112288,
            49.05296
          ],
          [
            -30.375725,
            48.271584
          ],
          [
            -30.429225,
            42.465745
          ],
          [
            -29.650312,
            -47.056874
          ],
          [
            -29.52871,
            -47.884505
          ],
          [
            -28.727647,
            -48.553817
          ],
          [
            -19.351082,
            -48.563101
          ],
          [
            -18.569699,
            -48.331363
          ],
          [
            -18.162839,
            -47.838254
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -43.4907395758293,
      "length": 38.99367712923455,
      "loops": [
        [
          [
            -30.449404,
            45.062211
          ],
          [
            -29.664989,
            -47.838254
          ],
          [
            -29.50903,
            -48.133825
          ],
          [
            -28.727647,
            -48.735897
          ],
          [
            -19.351082,
            -48.812725
          ],
          [
            -18.567561,
            -48.616591
          ],
          [
            -18.055597,
            -47.838254
          ],
          [
            -18.036434,
            -47.056874
          ],
          [
            -18.326911,
            5.21179
          ],
          [
            -18.180313,
            18.495262
          ],
          [
            -18.63093,
            31.778734
          ],
          [
            -18.814907,
            48.271584
          ],
          [
            -18.890991,
            49.05296
          ],
          [
            -19.351082,
            49.728808
          ],
          [
            -20.132465,
            49.995158
          ],
          [
            -29.50903,
            49.721781
          ],
          [
            -30.286784,
            49.05296
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -4.499042025085792,
      "length": 23.99687037894858,
      "loops": [
        [
          [
            -18.089366,
            -34.056642
          ],
          [
            -18.566927,
            31.862582
          ],
          [
            -18.509243,
            36.550871
          ],
          [
            -18.273211,
            37.332247
          ],
          [
            -17.78832,
            37.691522
          ],
          [
            -17.006938,
            37.82363
          ],
          [
            -7.630369,
            38.196927
          ],
          [
            10.624629,
            38.169851
          ],
          [
            19.219818,
            37.961848
          ],
          [
            28.313147,
            38.030041
          ],
          [
            29.094528,
            38.248274
          ],
          [
            29.545551,
            38.895012
          ],
          [
            29.302519,
            45.927436
          ],
          [
            29.201647,
            46.708819
          ],
          [
            28.817058,
            47.490201
          ],
          [
            28.313147,
            47.793466
          ],
          [
            26.750385,
            47.84886
          ],
          [
            -11.537272,
            47.616654
          ],
          [
            -17.505079,
            47.710285
          ],
          [
            -18.569699,
            48.019699
          ],
          [
            -18.994733,
            49.05296
          ],
          [
            -19.351082,
            49.369
          ],
          [
            -20.132465,
            49.568319
          ],
          [
            -28.727647,
            49.542507
          ],
          [
            -29.50903,
            49.465041
          ],
          [
            -30.089349,
            49.05296
          ],
          [
            -30.435524,
            48.271584
          ],
          [
            -30.449381,
            38.61177
          ],
          [
            -30.070539,
            -12.17798
          ],
          [
            -29.997169,
            -47.838254
          ],
          [
            -29.965976,
            -48.619635
          ],
          [
            -29.50903,
            -49.378583
          ],
          [
            -28.727647,
            -49.644136
          ],
          [
            -19.351082,
            -49.622181
          ],
          [
            -18.569699,
            -49.306036
          ],
          [
            -18.217413,
            -48.619635
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.495848775371748,
      "length": 14.998786328777008,
      "loops": [
        [
          [
            -18.182827,
            -47.838254
          ],
          [
            -18.548107,
            29.210791
          ],
          [
            -18.559168,
            37.332247
          ],
          [
            -18.339268,
            38.895012
          ],
          [
            -17.78832,
            39.482271
          ],
          [
            -17.006938,
            39.54388
          ],
          [
            28.313147,
            39.581246
          ],
          [
            29.094528,
            39.768032
          ],
          [
            29.574276,
            40.457771
          ],
          [
            29.258797,
            45.927436
          ],
          [
            29.17016,
            46.708819
          ],
          [
            28.82958,
            47.490201
          ],
          [
            28.313147,
            47.797527
          ],
          [
            25.495274,
            47.942794
          ],
          [
            -17.78832,
            47.996505
          ],
          [
            -18.569699,
            48.24406
          ],
          [
            -19.351082,
            49.145414
          ],
          [
            -20.606192,
            49.290736
          ],
          [
            -28.727647,
            49.285514
          ],
          [
            -29.50903,
            49.163763
          ],
          [
            -30.290413,
            48.374574
          ],
          [
            -30.419791,
            34.206729
          ],
          [
            -30.045816,
            -48.619635
          ],
          [
            -29.50903,
            -49.562882
          ],
          [
            -28.727647,
            -49.852931
          ],
          [
            -20.132465,
            -49.912596
          ],
          [
            -19.351082,
            -49.892946
          ],
          [
            -18.467099,
            -49.401017
          ],
          [
            -18.193935,
            -48.619635
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 34.49265552565772,
      "length": 14.998786328777008,
      "loops": [
        [
          [
            -18.638345,
            48.271584
          ],
          [
            -18.280269,
            -47.838254
          ],
          [
            -18.288978,
            -48.619635
          ],
          [
            -18.522267,
            -49.401017
          ],
          [
            -19.351082,
            -49.904365
          ],
          [
            -28.727647,
            -49.859859
          ],
          [
            -29.666396,
            -49.401017
          ],
          [
            -30.048845,
            -48.619635
          ],
          [
            -30.073445,
            -47.838254
          ],
          [
            -30.377789,
            35.311265
          ],
          [
            -30.290413,
            47.967179
          ],
          [
            -30.243183,
            48.271584
          ],
          [
            -29.50903,
            48.884996
          ],
          [
            -28.727647,
            49.041292
          ],
          [
            -20.132465,
            49.140014
          ],
          [
            -19.351082,
            49.04769
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.35727485000000003,
    8.214000000000832e-05,
    -0.396846775
  ],
  "construction_scale": 79.22117975071788,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
