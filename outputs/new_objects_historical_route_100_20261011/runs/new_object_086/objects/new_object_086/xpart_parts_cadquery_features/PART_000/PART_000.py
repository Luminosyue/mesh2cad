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
      "length": 9.092909090909094,
      "loops": [
        [
          [
            -1.390077,
            0.068345
          ],
          [
            -1.157461,
            16.082583
          ],
          [
            -1.283395,
            34.181873
          ],
          [
            -1.030089,
            37.601715
          ],
          [
            -0.97999,
            37.851935
          ],
          [
            -0.497795,
            38.06778
          ],
          [
            2.755097,
            38.156906
          ],
          [
            3.048373,
            38.352381
          ],
          [
            2.975246,
            38.602602
          ],
          [
            2.755097,
            38.676317
          ],
          [
            -1.498686,
            38.681681
          ],
          [
            -1.958806,
            38.352381
          ],
          [
            -2.115435,
            37.351493
          ],
          [
            -2.277834,
            32.347041
          ],
          [
            -2.223825,
            16.416079
          ],
          [
            -2.455439,
            -12.609726
          ],
          [
            -2.818833,
            -34.962798
          ],
          [
            -2.765373,
            -39.216583
          ],
          [
            -2.499575,
            -39.66466
          ],
          [
            -1.99913,
            -39.785727
          ],
          [
            -1.498686,
            -39.633375
          ],
          [
            -1.378771,
            -39.383531
          ],
          [
            -1.653913,
            -33.461463
          ],
          [
            -1.487217,
            -27.956571
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -40.90909090909091,
      "length": 9.092909090909087,
      "loops": [
        [
          [
            -2.268276,
            4.071904
          ],
          [
            -2.750031,
            -36.213911
          ],
          [
            -2.650438,
            -39.216583
          ],
          [
            -2.499575,
            -39.521307
          ],
          [
            -1.99913,
            -39.708285
          ],
          [
            -1.498686,
            -39.61371
          ],
          [
            -1.258227,
            -39.216583
          ],
          [
            -1.658662,
            -31.96013
          ],
          [
            -1.283876,
            8.575909
          ],
          [
            -1.085805,
            15.442821
          ],
          [
            -1.281072,
            34.348821
          ],
          [
            -0.984069,
            37.851935
          ],
          [
            -0.156355,
            38.352381
          ],
          [
            -0.99824,
            38.804647
          ],
          [
            -1.748907,
            38.624572
          ],
          [
            -1.977083,
            38.352381
          ],
          [
            -2.243735,
            35.099488
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -31.81818181818182,
      "length": 57.57775757575757,
      "loops": [
        [
          [
            -1.493968,
            -34.21213
          ],
          [
            -1.817039,
            -24.703678
          ],
          [
            -1.18769,
            -9.440108
          ],
          [
            -1.046742,
            1.069235
          ],
          [
            -1.744286,
            24.089702
          ],
          [
            -1.770345,
            29.344373
          ],
          [
            -1.312139,
            36.542888
          ],
          [
            -1.111395,
            37.851935
          ],
          [
            -0.67815,
            38.852828
          ],
          [
            -0.853756,
            39.103048
          ],
          [
            -1.248462,
            39.220034
          ],
          [
            -1.929299,
            38.852828
          ],
          [
            -2.116833,
            38.102161
          ],
          [
            -2.532832,
            33.848379
          ],
          [
            -2.765756,
            28.285546
          ],
          [
            -1.98014,
            0.819013
          ],
          [
            -2.152461,
            -8.747378
          ],
          [
            -2.782236,
            -24.453457
          ],
          [
            -2.76905,
            -31.209462
          ],
          [
            -2.339013,
            -38.465912
          ],
          [
            -2.135955,
            -38.966358
          ],
          [
            -1.498686,
            -39.271108
          ],
          [
            -0.99824,
            -39.110593
          ],
          [
            -0.799926,
            -38.716137
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 25.75757575757575,
      "length": 18.183818181818186,
      "loops": [
        [
          [
            -2.600957,
            -26.455235
          ],
          [
            -2.476736,
            -38.21569
          ],
          [
            -2.249352,
            -38.66361
          ],
          [
            -1.748907,
            -38.854427
          ],
          [
            -1.248462,
            -38.614085
          ],
          [
            -1.104246,
            -38.21569
          ],
          [
            -1.462435,
            -33.993734
          ],
          [
            -1.679514,
            -27.988395
          ],
          [
            -1.134979,
            2.0383
          ],
          [
            -1.197299,
            8.293862
          ],
          [
            -1.679,
            19.30365
          ],
          [
            -1.842079,
            27.843039
          ],
          [
            -1.680543,
            32.09682
          ],
          [
            -1.20368,
            38.070335
          ],
          [
            -1.05148,
            38.852828
          ],
          [
            -0.600425,
            39.353274
          ],
          [
            -0.617953,
            39.603494
          ],
          [
            -0.99824,
            39.816468
          ],
          [
            -1.498686,
            39.694006
          ],
          [
            -1.885043,
            39.353274
          ],
          [
            -2.130195,
            38.352381
          ],
          [
            -2.457957,
            35.349713
          ],
          [
            -2.806295,
            28.593705
          ],
          [
            -2.052276,
            1.287633
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
            -1.280003,
            35.483689
          ],
          [
            -1.465486,
            21.971676
          ],
          [
            -1.375317,
            3.071014
          ],
          [
            -1.495802,
            -19.449006
          ],
          [
            -1.851252,
            -38.21569
          ],
          [
            -1.99913,
            -38.509921
          ],
          [
            -2.499575,
            -38.646257
          ],
          [
            -2.908505,
            -38.21569
          ],
          [
            -2.942259,
            -37.715244
          ],
          [
            -2.498401,
            -26.071036
          ],
          [
            -2.397432,
            -17.31325
          ],
          [
            -2.465831,
            24.724124
          ],
          [
            -2.327094,
            35.483689
          ],
          [
            -1.974504,
            39.103048
          ],
          [
            -1.719328,
            39.584738
          ],
          [
            -0.99824,
            39.876916
          ],
          [
            2.504874,
            39.76704
          ],
          [
            2.824451,
            39.603494
          ],
          [
            2.844864,
            39.353274
          ],
          [
            2.504874,
            39.173473
          ],
          [
            -0.748017,
            39.155683
          ],
          [
            -0.99824,
            38.99036
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 2,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.0027644450000000043,
    -0.096193105,
    -0.000673510000000016
  ],
  "construction_scale": 101.4763561663016,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
