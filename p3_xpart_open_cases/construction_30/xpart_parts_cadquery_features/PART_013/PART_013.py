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
  "center_xy": [
    0.09992280709918812,
    0.09481268927572344
  ],
  "profile": [
    [
      1.0479216243728409,
      -43.98768410093942
    ],
    [
      3.0738507115081033,
      -43.98568753006431
    ],
    [
      5.123167064887076,
      -43.98819407807174
    ],
    [
      7.172494083542332,
      -43.99488017871661
    ],
    [
      9.221772949290166,
      -44.00174774619602
    ],
    [
      11.27100325140279,
      -44.00315563880521
    ],
    [
      13.320322081235556,
      -44.007612396736555
    ],
    [
      15.36968648780124,
      -44.013222645018054
    ],
    [
      17.419031000099555,
      -44.016453050280134
    ],
    [
      19.46838178614096,
      -44.01577876853529
    ],
    [
      21.517657245758326,
      -44.018104672233456
    ],
    [
      23.566941476130378,
      -44.02496353969357
    ],
    [
      25.616291291315456,
      -44.0299718848419
    ],
    [
      27.665604180726522,
      -44.03114687036204
    ],
    [
      29.71491413134516,
      -44.038604939665774
    ],
    [
      31.7641520484243,
      -44.04111707573385
    ],
    [
      33.81342529595808,
      -44.04791061054067
    ],
    [
      35.86270666666536,
      -44.05437637940146
    ],
    [
      37.911879616261544,
      -44.03491467353057
    ],
    [
      39.95755026467302,
      -43.96097530980602
    ],
    [
      41.97373153295795,
      -43.65374326814248
    ],
    [
      43.90466413437893,
      -43.00036513561549
    ],
    [
      45.691711946164396,
      -42.030348660685796
    ],
    [
      47.23741454736933,
      -40.6812516716149
    ],
    [
      48.392593190023526,
      -38.96397640873407
    ],
    [
      49.16361061395758,
      -37.08243156497967
    ],
    [
      49.628852144683805,
      -35.08814646165898
    ],
    [
      49.7791895627472,
      -33.04635229321922
    ],
    [
      49.73134929158429,
      -31.001267649980235
    ],
    [
      49.584910598919365,
      -28.96123905425314
    ],
    [
      49.42333730591857,
      -26.924427025622297
    ],
    [
      49.22609461953642,
      -24.890878336592166
    ],
    [
      49.03234696086825,
      -22.855854052284457
    ],
    [
      48.85971417261376,
      -20.821682107520857
    ],
    [
      48.65975634609278,
      -18.788953714977225
    ],
    [
      48.457203554896736,
      -16.75699833713182
    ],
    [
      48.22617706924457,
      -14.72589757160711
    ],
    [
      47.9803580743811,
      -12.696044124192348
    ],
    [
      47.723311689547785,
      -10.664932719081408
    ],
    [
      47.457786974098795,
      -8.63345012974294
    ],
    [
      47.16085993135073,
      -6.600196233931668
    ],
    [
      46.84803044342952,
      -4.565710033465108
    ],
    [
      46.54536319638806,
      -2.5345938228694234
    ],
    [
      46.22539737810277,
      -0.5048596779107317
    ],
    [
      45.902373351834825,
      1.5195402075537712
    ],
    [
      45.58947335667392,
      3.5437303355437786
    ],
    [
      45.25574181484163,
      5.564823354335866
    ],
    [
      44.91141557994641,
      7.5854313017386445
    ],
    [
      44.55497596851008,
      9.603389255993214
    ],
    [
      44.18719305516751,
      11.620927805809224
    ],
    [
      43.80746297703345,
      13.633752976890001
    ],
    [
      43.39261089994338,
      15.637078849681739
    ],
    [
      42.90845666722274,
      17.62009892721146
    ],
    [
      42.38644068999991,
      19.596605520192288
    ],
    [
      41.82059309165706,
      21.56858980441583
    ],
    [
      41.17277252539981,
      23.51680457410353
    ],
    [
      40.394734546493055,
      25.394151849326025
    ],
    [
      39.455348242883005,
      27.21230082697177
    ],
    [
      38.402369503538175,
      28.97457689361935
    ],
    [
      37.2401262759999,
      30.672465039184594
    ],
    [
      35.98660485106761,
      32.2950772422008
    ],
    [
      34.620677952775765,
      33.8234670187594
    ],
    [
      33.16304748656552,
      35.2667102355509
    ],
    [
      31.626395497940074,
      36.620530490166345
    ],
    [
      30.025968385275547,
      37.91257138240577
    ],
    [
      28.344996969723763,
      39.112057039660655
    ],
    [
      26.597463085056106,
      40.20404951279626
    ],
    [
      24.808095443696786,
      41.20282529481852
    ],
    [
      23.010608850552565,
      42.18914203779541
    ],
    [
      21.20409812740169,
      43.135146794532346
    ],
    [
      19.30571041212457,
      43.59244871498423
    ],
    [
      17.372801609066258,
      43.24564068182153
    ],
    [
      15.36285712848537,
      43.14629781444713
    ],
    [
      13.319862003150853,
      43.20263829029702
    ],
    [
      11.270910847017786,
      43.20019294760275
    ],
    [
      9.221556685394525,
      43.16702831536955
    ],
    [
      7.172347625611195,
      43.150204363888164
    ],
    [
      5.12322374188285,
      43.151202096164894
    ],
    [
      3.0740578827756675,
      43.15456221308484
    ],
    [
      1.0480558449272155,
      43.15898233335557
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
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
  "axis_candidate": 0,
  "center": [
    -0.55546284,
    0.010639645000000003,
    -0.63563058
  ],
  "construction_scale": 361.8840552437723,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
