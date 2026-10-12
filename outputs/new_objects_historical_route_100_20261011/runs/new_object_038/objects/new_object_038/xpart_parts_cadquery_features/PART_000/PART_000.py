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
    0.011058267981657615,
    -0.04923382500567581
  ],
  "profile": [
    [
      0.8253068347866119,
      -16.138528915884756
    ],
    [
      2.4196639316020927,
      -16.09522666102204
    ],
    [
      4.031054047724624,
      -16.017189978790896
    ],
    [
      5.6432634622150974,
      -15.93795330925051
    ],
    [
      7.256370512689029,
      -15.896813039933715
    ],
    [
      8.869761331025945,
      -15.869419622712847
    ],
    [
      10.483499629072611,
      -15.846334720403743
    ],
    [
      12.09739073514836,
      -15.826661405188567
    ],
    [
      13.711309295250295,
      -15.811992127503308
    ],
    [
      15.325225799120858,
      -15.801365552578956
    ],
    [
      16.939151901397228,
      -15.796080186913095
    ],
    [
      18.553085327341442,
      -15.790258411240199
    ],
    [
      20.167059919260005,
      -15.784708992940805
    ],
    [
      21.781064695031336,
      -15.778969577855388
    ],
    [
      23.395070068558994,
      -15.774229786724941
    ],
    [
      25.009043786838056,
      -15.768507407497886
    ],
    [
      26.623066698857635,
      -15.762392686682222
    ],
    [
      28.237079520853634,
      -15.75521406373661
    ],
    [
      29.851077450148004,
      -15.7489525916098
    ],
    [
      31.465102435555245,
      -15.742056381397205
    ],
    [
      33.079100126374684,
      -15.737118237157581
    ],
    [
      34.69309116498897,
      -15.730496907193205
    ],
    [
      36.3070366348862,
      -15.724012553321344
    ],
    [
      37.920855555536896,
      -15.71709984777224
    ],
    [
      39.53463066878426,
      -15.709795866821178
    ],
    [
      41.145384220931334,
      -15.690066658781298
    ],
    [
      42.66979458225699,
      -15.470416599028738
    ],
    [
      43.51665955019352,
      -14.325833301921449
    ],
    [
      43.91349013621007,
      -12.901310759785762
    ],
    [
      45.24135107828677,
      -12.488344464543179
    ],
    [
      46.85063121183526,
      -12.45865978585394
    ],
    [
      48.45848710708901,
      -12.410293851567218
    ],
    [
      49.74573546013039,
      -11.841344753147897
    ],
    [
      49.970605807945546,
      -10.3500301818544
    ],
    [
      49.92843409714864,
      -8.737661046662499
    ],
    [
      49.87065962227964,
      -7.12534474860455
    ],
    [
      49.81797883918543,
      -5.512887558799525
    ],
    [
      49.76533346746767,
      -3.900550364418876
    ],
    [
      49.708417748079,
      -2.28833978098143
    ],
    [
      49.64648778894224,
      -0.6759152965160129
    ],
    [
      49.59058056973181,
      0.9363655884243445
    ],
    [
      49.53615661700805,
      2.5484726153069484
    ],
    [
      49.48125747315019,
      4.160699575740715
    ],
    [
      49.416220380763676,
      5.772814244612325
    ],
    [
      49.35193479399873,
      7.384877150781939
    ],
    [
      49.28459119128803,
      8.996370241433373
    ],
    [
      49.22057933622362,
      10.608283643763201
    ],
    [
      49.154850760323356,
      12.220938428754238
    ],
    [
      49.0630562397998,
      13.83245600976868
    ],
    [
      48.79001209093555,
      15.368587064234895
    ],
    [
      47.60408595456478,
      16.08111621295886
    ],
    [
      45.99951988935537,
      16.131056250096332
    ],
    [
      44.38554217970709,
      16.136722862175347
    ],
    [
      42.77155642779323,
      16.138771615148002
    ],
    [
      41.1575605197926,
      16.139761312056947
    ],
    [
      39.54356844849525,
      16.1403010237528
    ],
    [
      37.92955981650506,
      16.14123180130245
    ],
    [
      36.31553993952531,
      16.14193644189846
    ],
    [
      34.70153874779599,
      16.14186827050123
    ],
    [
      33.08751734173888,
      16.141417090822628
    ],
    [
      31.47350492771712,
      16.14155058325215
    ],
    [
      29.85946969153308,
      16.14117884126708
    ],
    [
      28.24545121527799,
      16.141761393160692
    ],
    [
      26.63145799341166,
      16.141801005461062
    ],
    [
      25.017430578220875,
      16.14178277544747
    ],
    [
      23.40340285756472,
      16.142104896848664
    ],
    [
      21.78937791374035,
      16.142744673589462
    ],
    [
      20.17535545132307,
      16.142904745153217
    ],
    [
      18.56133495632832,
      16.143566548707412
    ],
    [
      16.947304028987702,
      16.14364503065452
    ],
    [
      15.333274006000874,
      16.144374809802734
    ],
    [
      13.719246338083538,
      16.144809602622754
    ],
    [
      12.105218399909212,
      16.144702037938277
    ],
    [
      10.491198218424051,
      16.14515454903788
    ],
    [
      8.87717592346131,
      16.14615572873639
    ],
    [
      7.263139536413345,
      16.14641914612711
    ],
    [
      5.649107076783698,
      16.14673161314787
    ],
    [
      4.0350687970573045,
      16.147354212232862
    ],
    [
      2.421030262103514,
      16.147669805655767
    ],
    [
      0.8253990026815612,
      16.14824878919576
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
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
  "axis_candidate": 1,
  "center": [
    0.0003458199999999967,
    0.16951769,
    -0.0008313749999999953
  ],
  "construction_scale": 102.3971479527175,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
