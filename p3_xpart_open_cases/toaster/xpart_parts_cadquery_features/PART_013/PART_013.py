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
      "start": -5.938915181561152,
      "length": 2.5197773306029023,
      "loops": [
        [
          [
            49.541118,
            4.147744
          ],
          [
            49.094396,
            4.393766
          ],
          [
            47.782079,
            4.452615
          ],
          [
            46.785539,
            4.058739
          ],
          [
            45.215807,
            2.746421
          ],
          [
            44.980049,
            1.871543
          ],
          [
            45.15744,
            1.233278
          ],
          [
            46.032317,
            0.665396
          ],
          [
            46.469755,
            0.665751
          ],
          [
            46.907198,
            0.931883
          ],
          [
            49.817666,
            3.18386
          ],
          [
            49.961751,
            3.6213
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.938915181561152,
      "length": 2.5197773306029023,
      "loops": [
        [
          [
            33.346576,
            0.704922
          ],
          [
            33.784016,
            1.437994
          ],
          [
            34.221457,
            1.65662
          ],
          [
            35.096334,
            1.644844
          ],
          [
            35.506454,
            1.434102
          ],
          [
            35.841004,
            0.996664
          ],
          [
            35.99928,
            0.121785
          ],
          [
            35.881873,
            -0.315655
          ],
          [
            35.096334,
            -0.960319
          ],
          [
            34.221457,
            -0.940542
          ],
          [
            33.485665,
            -0.315655
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -5.938915181561152,
      "length": 2.5197773306029023,
      "loops": [
        [
          [
            -38.763505,
            -2.122722
          ],
          [
            -38.885703,
            -2.94029
          ],
          [
            -38.723607,
            -3.37773
          ],
          [
            -37.956034,
            -4.229497
          ],
          [
            -37.518595,
            -4.384581
          ],
          [
            -37.30315,
            -4.252609
          ],
          [
            -36.982288,
            -3.815169
          ],
          [
            -36.903493,
            -3.37773
          ],
          [
            -36.901871,
            -2.502851
          ],
          [
            -37.081155,
            -1.9532
          ],
          [
            -37.518595,
            -1.422783
          ],
          [
            -37.956034,
            -1.343885
          ],
          [
            -38.393475,
            -1.603043
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -3.4193754075655116,
      "length": 2.1598430771749544,
      "loops": [
        [
          [
            -38.393475,
            -1.418528
          ],
          [
            -37.081155,
            -0.917146
          ],
          [
            -34.45652,
            -1.077524
          ],
          [
            25.035231,
            -0.908158
          ],
          [
            32.471699,
            -0.740641
          ],
          [
            32.90914,
            -0.711891
          ],
          [
            33.23755,
            -0.435677
          ],
          [
            33.266135,
            0.559224
          ],
          [
            33.784016,
            1.363859
          ],
          [
            34.221457,
            1.623592
          ],
          [
            34.658894,
            1.662039
          ],
          [
            35.096334,
            1.6037
          ],
          [
            35.775101,
            0.996664
          ],
          [
            36.408651,
            -0.60787
          ],
          [
            40.783047,
            -0.723566
          ],
          [
            42.652825,
            -0.46829
          ],
          [
            43.953849,
            0.121785
          ],
          [
            44.342656,
            0.559224
          ],
          [
            44.034982,
            2.308982
          ],
          [
            44.12555,
            2.746421
          ],
          [
            44.72,
            3.386566
          ],
          [
            45.59488,
            3.663557
          ],
          [
            46.907198,
            3.572717
          ],
          [
            47.18365,
            3.460314
          ],
          [
            47.346155,
            2.74866
          ],
          [
            46.318946,
            -0.029025
          ],
          [
            45.875068,
            -0.753094
          ],
          [
            45.15744,
            -1.432812
          ],
          [
            43.407682,
            -2.188395
          ],
          [
            39.908167,
            -2.626209
          ],
          [
            -35.3314,
            -3.03143
          ],
          [
            -36.366945,
            -3.257707
          ],
          [
            -37.081155,
            -4.133536
          ],
          [
            -37.518595,
            -4.374225
          ],
          [
            -37.956034,
            -4.229477
          ],
          [
            -38.830915,
            -3.111146
          ],
          [
            -39.268351,
            -2.943199
          ],
          [
            -48.892017,
            -2.877381
          ],
          [
            -49.329457,
            -2.793485
          ],
          [
            -49.68056,
            -2.502851
          ],
          [
            -49.768692,
            -2.065412
          ],
          [
            -49.329457,
            -1.45561
          ],
          [
            -48.531996,
            -1.267952
          ],
          [
            -41.89299,
            -1.274725
          ],
          [
            -38.830915,
            -1.446552
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -1.2597698869978196,
      "length": 7.198922625166235,
      "loops": [
        [
          [
            33.48481,
            0.996664
          ],
          [
            34.221457,
            1.520634
          ],
          [
            35.307408,
            1.434102
          ],
          [
            35.772086,
            0.996664
          ],
          [
            35.96606,
            0.559224
          ],
          [
            36.084236,
            -0.315655
          ],
          [
            35.892934,
            -0.753094
          ],
          [
            35.096334,
            -1.410224
          ],
          [
            34.568725,
            -1.450846
          ],
          [
            33.864275,
            -1.190533
          ],
          [
            33.25305,
            -0.315655
          ],
          [
            33.281746,
            0.559224
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.050689395000000005,
    0.056163895,
    0.112286955
  ],
  "construction_scale": 88.70057008832102,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
