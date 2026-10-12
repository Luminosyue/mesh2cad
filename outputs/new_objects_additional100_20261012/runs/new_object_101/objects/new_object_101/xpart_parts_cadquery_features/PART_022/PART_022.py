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
      "start": -50.0,
      "length": 27.274727272727272,
      "loops": [
        [
          [
            26.18122,
            -33.824713
          ],
          [
            4.471063,
            -33.396126
          ],
          [
            -18.472627,
            -32.648685
          ],
          [
            -28.834292,
            -32.544924
          ],
          [
            -29.285817,
            -32.261648
          ],
          [
            -29.406573,
            -32.014942
          ],
          [
            -29.359666,
            -27.820935
          ],
          [
            -28.612031,
            10.730564
          ],
          [
            -28.402717,
            33.855648
          ],
          [
            -28.37774,
            34.349062
          ],
          [
            -28.204928,
            34.595767
          ],
          [
            -25.873816,
            34.589191
          ],
          [
            -24.640285,
            34.350194
          ],
          [
            -22.731945,
            34.254754
          ],
          [
            26.609321,
            33.318946
          ],
          [
            27.236436,
            33.115529
          ],
          [
            27.390893,
            31.881997
          ],
          [
            27.339812,
            27.506596
          ],
          [
            26.87521,
            18.31315
          ],
          [
            26.900183,
            0.368899
          ],
          [
            26.759159,
            -1.916769
          ],
          [
            26.703038,
            -15.485618
          ],
          [
            26.879977,
            -18.134076
          ],
          [
            26.633657,
            -24.54844
          ],
          [
            26.58645,
            -33.495178
          ],
          [
            26.453719,
            -33.741888
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -22.727272727272727,
      "length": 72.72927272727271,
      "loops": [
        [
          [
            -28.738557,
            6.117595
          ],
          [
            -29.416663,
            -31.875179
          ],
          [
            -29.080998,
            -32.482603
          ],
          [
            11.625546,
            -33.571646
          ],
          [
            26.428575,
            -33.741888
          ],
          [
            26.612358,
            -33.001765
          ],
          [
            26.779207,
            -8.438078
          ],
          [
            27.332358,
            -6.850896
          ],
          [
            27.303451,
            -3.997364
          ],
          [
            27.935966,
            0.936762
          ],
          [
            27.570561,
            3.017358
          ],
          [
            27.68479,
            7.211365
          ],
          [
            26.99318,
            10.17184
          ],
          [
            27.493722,
            12.778666
          ],
          [
            26.956051,
            15.59938
          ],
          [
            26.907879,
            16.832912
          ],
          [
            26.991285,
            24.480808
          ],
          [
            27.366146,
            31.775053
          ],
          [
            27.331415,
            32.868825
          ],
          [
            27.168045,
            33.173239
          ],
          [
            26.674632,
            33.355397
          ],
          [
            23.8211,
            33.438351
          ],
          [
            -22.312983,
            34.293335
          ],
          [
            -26.613934,
            34.630334
          ],
          [
            -28.219101,
            34.595767
          ],
          [
            -28.424942,
            34.102353
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    0.011760574999999995,
    0.0034885249999999923,
    -0.0027691549999999954
  ],
  "construction_scale": 100.05040839726279,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
