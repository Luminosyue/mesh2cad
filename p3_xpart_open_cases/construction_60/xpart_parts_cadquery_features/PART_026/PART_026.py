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
      -0.4873976995705208,
      0.866320543723145,
      -0.10923460063825624
    ],
    [
      -0.8731581401318224,
      -0.4844437941414207,
      0.05393581963224892
    ],
    [
      -0.006192315794756336,
      0.12166727514455078,
      0.992551625551033
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -30.1624140273623,
      "length": 59.80614600863264,
      "loops": [
        [
          [
            34.339436,
            32.221642
          ],
          [
            43.694488,
            10.837535
          ],
          [
            46.337446,
            4.09607
          ],
          [
            48.879418,
            -3.47278
          ],
          [
            49.353555,
            -5.486763
          ],
          [
            49.330565,
            -8.10701
          ],
          [
            48.62166,
            -10.344378
          ],
          [
            47.491413,
            -12.346552
          ],
          [
            46.121883,
            -14.215159
          ],
          [
            34.373727,
            -28.721962
          ],
          [
            23.101198,
            -43.494266
          ],
          [
            21.154338,
            -45.040606
          ],
          [
            17.726053,
            -46.138855
          ],
          [
            14.167283,
            -46.564378
          ],
          [
            9.115828,
            -46.106109
          ],
          [
            -15.140661,
            -42.839485
          ],
          [
            -25.343297,
            -41.286774
          ],
          [
            -27.573235,
            -40.52871
          ],
          [
            -29.520006,
            -39.264254
          ],
          [
            -31.284175,
            -37.673187
          ],
          [
            -32.808506,
            -35.653301
          ],
          [
            -37.426197,
            -24.927606
          ],
          [
            -43.501385,
            -11.5828
          ],
          [
            -49.355095,
            2.217064
          ],
          [
            -49.966927,
            5.191668
          ],
          [
            -49.531381,
            7.581626
          ],
          [
            -48.526434,
            9.653743
          ],
          [
            -31.172899,
            31.563941
          ],
          [
            -22.126476,
            42.312696
          ],
          [
            -20.093689,
            43.811077
          ],
          [
            -17.47495,
            44.982374
          ],
          [
            -13.87047,
            45.412129
          ],
          [
            -11.298933,
            45.259328
          ],
          [
            23.857074,
            40.636419
          ],
          [
            25.915237,
            40.095449
          ],
          [
            27.760809,
            39.16926
          ],
          [
            31.209654,
            36.116426
          ],
          [
            32.86607,
            34.332707
          ]
        ],
        [
          [
            6.297215,
            15.29528
          ],
          [
            3.410486,
            16.397943
          ],
          [
            -0.635232,
            17.135666
          ],
          [
            -3.393419,
            16.949074
          ],
          [
            -7.422421,
            15.673323
          ],
          [
            -10.673652,
            13.957098
          ],
          [
            -13.992739,
            11.441642
          ],
          [
            -15.56604,
            9.686781
          ],
          [
            -16.899166,
            7.797854
          ],
          [
            -17.845999,
            5.693292
          ],
          [
            -18.521704,
            3.437397
          ],
          [
            -18.923731,
            -1.331745
          ],
          [
            -18.698379,
            -4.363221
          ],
          [
            -17.978165,
            -7.477954
          ],
          [
            -16.338827,
            -10.94674
          ],
          [
            -13.600842,
            -14.426938
          ],
          [
            -11.455522,
            -16.451561
          ],
          [
            -9.375168,
            -17.477162
          ],
          [
            -6.905131,
            -17.805901
          ],
          [
            -4.069198,
            -17.795408
          ],
          [
            -1.361581,
            -17.384167
          ],
          [
            2.437052,
            -16.161038
          ],
          [
            5.590135,
            -14.444269
          ],
          [
            8.992367,
            -11.920983
          ],
          [
            10.563107,
            -10.164698
          ],
          [
            11.642856,
            -8.13433
          ],
          [
            12.468542,
            -5.962149
          ],
          [
            13.009158,
            -3.630842
          ],
          [
            13.268953,
            -1.142781
          ],
          [
            12.947452,
            3.458518
          ],
          [
            12.256289,
            6.96838
          ],
          [
            11.220461,
            9.861856
          ],
          [
            9.797945,
            12.063855
          ],
          [
            8.171159,
            13.900562
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 5,
  "center": [
    0.090634925,
    -0.62205866,
    -0.07116745000000001
  ],
  "construction_scale": 466.1927289225409,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
