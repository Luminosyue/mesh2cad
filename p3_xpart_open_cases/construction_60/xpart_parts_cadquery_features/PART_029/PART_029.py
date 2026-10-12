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
      -0.06013813899705675,
      0.30849967762122743,
      0.9493215225336299
    ],
    [
      0.2290700326890162,
      -0.9213962494883847,
      0.3139360946953876
    ],
    [
      0.9715504744282841,
      0.23634064469814964,
      -0.015256975514146287
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -5.231194819518416,
      "length": 11.2165087031941,
      "loops": [
        [
          [
            37.427201,
            -14.58674
          ],
          [
            31.025157,
            -16.900571
          ],
          [
            25.045264,
            -18.622412
          ],
          [
            16.82615,
            -20.27388
          ],
          [
            8.982103,
            -21.174266
          ],
          [
            1.28888,
            -21.553947
          ],
          [
            -6.576606,
            -21.412719
          ],
          [
            -12.736762,
            -20.836172
          ],
          [
            -21.588733,
            -19.363417
          ],
          [
            -28.638476,
            -17.748357
          ],
          [
            -38.155372,
            -14.58367
          ],
          [
            -43.517031,
            -12.162397
          ],
          [
            -46.860385,
            -9.93348
          ],
          [
            -48.119462,
            -8.879913
          ],
          [
            -49.527483,
            -7.337407
          ],
          [
            -50.568799,
            -5.672121
          ],
          [
            -51.340951,
            -3.916713
          ],
          [
            -52.026206,
            -0.47006
          ],
          [
            -51.757174,
            2.657046
          ],
          [
            -51.206391,
            4.855394
          ],
          [
            -50.56247,
            6.439637
          ],
          [
            -49.137277,
            8.773426
          ],
          [
            -47.743733,
            10.470309
          ],
          [
            -45.130529,
            12.419607
          ],
          [
            -42.769216,
            13.160305
          ],
          [
            -40.926249,
            13.49817
          ],
          [
            -37.669809,
            13.50236
          ],
          [
            -33.511302,
            12.749045
          ],
          [
            -31.356062,
            12.142615
          ],
          [
            -21.746529,
            8.715017
          ],
          [
            -16.021049,
            7.237692
          ],
          [
            -6.826648,
            5.973074
          ],
          [
            -0.356205,
            5.594014
          ],
          [
            7.189997,
            5.918123
          ],
          [
            11.578904,
            6.43839
          ],
          [
            21.292311,
            8.590328
          ],
          [
            34.853725,
            13.101223
          ],
          [
            37.882532,
            13.590701
          ],
          [
            41.214904,
            13.365286
          ],
          [
            43.385391,
            12.712746
          ],
          [
            45.767008,
            11.421759
          ],
          [
            47.816536,
            9.814894
          ],
          [
            49.504533,
            7.90623
          ],
          [
            50.845793,
            5.458641
          ],
          [
            51.347695,
            3.61275
          ],
          [
            51.548024,
            1.665888
          ],
          [
            51.386563,
            -1.073423
          ],
          [
            50.8597,
            -3.263764
          ],
          [
            50.008594,
            -5.345081
          ],
          [
            48.736002,
            -7.30115
          ],
          [
            47.135567,
            -9.083866
          ],
          [
            45.258077,
            -10.682725
          ],
          [
            43.675326,
            -11.656082
          ]
        ],
        {
          "center": [
            12.541100723525446,
            -7.3031146770997815
          ],
          "radius": 5.096098592635178
        },
        {
          "center": [
            -12.858748761972608,
            -7.472812469012114
          ],
          "radius": 5.061166079008156
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    -0.123056265,
    -0.59856383,
    0.05903497499999999
  ],
  "construction_scale": 125.42374254639623,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
