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
      -0.2608484987464522,
      0.6229777136184,
      0.7374664935008997
    ],
    [
      0.30909618793278637,
      -0.6698020265974408,
      0.6751479776844339
    ],
    [
      0.9145586953865465,
      0.404059418279975,
      -0.017843183351257005
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -6.889988573853415,
      "length": 14.35425716414857,
      "loops": [
        [
          [
            -11.775996,
            26.152589
          ],
          [
            -20.169359,
            25.176161
          ],
          [
            -25.648915,
            24.215329
          ],
          [
            -32.224153,
            22.714775
          ],
          [
            -39.398429,
            20.532064
          ],
          [
            -46.270246,
            18.08714
          ],
          [
            -50.256332,
            16.363258
          ],
          [
            -53.942308,
            14.311564
          ],
          [
            -56.832308,
            12.25869
          ],
          [
            -58.898195,
            10.173914
          ],
          [
            -60.940337,
            7.193616
          ],
          [
            -61.930491,
            4.803391
          ],
          [
            -62.367601,
            1.807757
          ],
          [
            -62.102954,
            -1.349235
          ],
          [
            -61.215202,
            -4.752007
          ],
          [
            -59.643836,
            -8.146236
          ],
          [
            -57.645343,
            -11.061631
          ],
          [
            -55.218986,
            -13.099293
          ],
          [
            -52.174147,
            -14.536213
          ],
          [
            -49.185846,
            -15.195534
          ],
          [
            -45.153544,
            -15.258672
          ],
          [
            -40.811675,
            -14.519311
          ],
          [
            -27.920106,
            -10.041304
          ],
          [
            -18.700552,
            -7.685982
          ],
          [
            -7.543072,
            -5.980994
          ],
          [
            -2.961917,
            -5.775382
          ],
          [
            4.473473,
            -5.850714
          ],
          [
            14.600614,
            -6.915991
          ],
          [
            20.587971,
            -8.112859
          ],
          [
            27.744615,
            -10.05503
          ],
          [
            40.502219,
            -14.705366
          ],
          [
            44.406075,
            -15.372595
          ],
          [
            48.223563,
            -15.66709
          ],
          [
            50.340467,
            -15.374578
          ],
          [
            52.226547,
            -14.829937
          ],
          [
            55.565677,
            -13.267654
          ],
          [
            58.631016,
            -10.538037
          ],
          [
            60.388864,
            -8.116785
          ],
          [
            60.96465,
            -7.009174
          ],
          [
            62.038496,
            -3.816436
          ],
          [
            62.361524,
            -1.895946
          ],
          [
            62.424476,
            -0.086993
          ],
          [
            61.84314,
            3.964046
          ],
          [
            60.421837,
            7.447822
          ],
          [
            58.3955,
            10.168906
          ],
          [
            55.598981,
            12.698688
          ],
          [
            51.62301,
            15.24748
          ],
          [
            47.945656,
            17.078406
          ],
          [
            42.016231,
            19.440304
          ],
          [
            36.066839,
            21.412859
          ],
          [
            26.236898,
            23.938228
          ],
          [
            20.505775,
            25.028399
          ],
          [
            12.685991,
            26.053266
          ],
          [
            6.341743,
            26.607484
          ],
          [
            -0.955748,
            26.733259
          ]
        ],
        [
          [
            19.686407,
            5.084891
          ],
          [
            18.839898,
            4.272992
          ],
          [
            17.818333,
            3.652313
          ],
          [
            16.623149,
            3.221273
          ],
          [
            14.937754,
            3.006831
          ],
          [
            12.563337,
            3.424012
          ],
          [
            11.41642,
            4.107673
          ],
          [
            10.504535,
            5.009935
          ],
          [
            9.050672,
            7.158514
          ],
          [
            8.742228,
            8.20989
          ],
          [
            8.663135,
            9.42367
          ],
          [
            8.85269,
            10.8407
          ],
          [
            9.415154,
            12.443553
          ],
          [
            11.386932,
            15.018708
          ],
          [
            11.886665,
            15.341119
          ],
          [
            13.173424,
            15.672129
          ],
          [
            16.309788,
            15.561735
          ],
          [
            18.231744,
            14.822561
          ],
          [
            19.709837,
            13.571716
          ],
          [
            20.998615,
            11.366163
          ],
          [
            21.327391,
            9.370337
          ],
          [
            20.900453,
            7.231868
          ]
        ],
        {
          "center": [
            -15.613576823479992,
            9.670983060522028
          ],
          "radius": 6.368923344949899
        }
      ]
    }
  ],
  "axis_candidate": 5,
  "analytic_circles": true,
  "center": [
    0.23047496499999998,
    -0.40753575,
    -0.30385573
  ],
  "construction_scale": 118.86743865203944,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
