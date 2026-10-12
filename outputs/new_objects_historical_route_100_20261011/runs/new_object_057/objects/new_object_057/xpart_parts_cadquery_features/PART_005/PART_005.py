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
    0.0023658486785083518,
    -0.0017377721956577852
  ],
  "profile": [
    [
      1.4332021577317056,
      -8.084794881691987
    ],
    [
      2.8657715945841398,
      -8.084315957941257
    ],
    [
      4.298628390098249,
      -8.085039525803957
    ],
    [
      5.731395584910082,
      -8.085317365666707
    ],
    [
      7.164198606847801,
      -8.084656707152869
    ],
    [
      8.59705810657448,
      -8.08439019277461
    ],
    [
      10.029928433132781,
      -8.08368487917941
    ],
    [
      11.462796362795594,
      -8.085347874192749
    ],
    [
      12.895676457661484,
      -8.086980601606129
    ],
    [
      14.32854408131455,
      -8.086878301044116
    ],
    [
      15.761401269405297,
      -8.086978047830936
    ],
    [
      17.1942715039872,
      -8.087089040839889
    ],
    [
      18.627151217804215,
      -8.08745509066977
    ],
    [
      20.060000408991552,
      -8.087891208854677
    ],
    [
      21.492829455415507,
      -8.08764531641949
    ],
    [
      22.925650294925727,
      -8.08709578110988
    ],
    [
      24.358418652120946,
      -8.088103516609166
    ],
    [
      25.79125816701514,
      -8.087000058731537
    ],
    [
      27.224136763770822,
      -8.087435902731505
    ],
    [
      28.65700125502812,
      -8.0856638613101
    ],
    [
      30.08984639210935,
      -8.085531755508185
    ],
    [
      31.52185987168992,
      -8.092823761147969
    ],
    [
      32.841590478207074,
      -8.343390169256121
    ],
    [
      33.62414630655261,
      -9.431778337283749
    ],
    [
      34.67094281830692,
      -10.273670839363401
    ],
    [
      36.07146584129856,
      -10.442391614230806
    ],
    [
      37.50385789323123,
      -10.453003819738736
    ],
    [
      38.93659869605913,
      -10.45495622582022
    ],
    [
      40.36932407656669,
      -10.452883936497571
    ],
    [
      41.801995171218934,
      -10.450587283449206
    ],
    [
      43.232495746237205,
      -10.440108814714508
    ],
    [
      44.59082417342863,
      -10.126218658262136
    ],
    [
      45.76776391702087,
      -9.318447290956914
    ],
    [
      46.86701711219578,
      -8.40840695947211
    ],
    [
      47.815531870987584,
      -7.340413777733264
    ],
    [
      48.59733416590779,
      -6.141053702108662
    ],
    [
      49.191722926237176,
      -4.8526758893797055
    ],
    [
      49.593390932226455,
      -3.482923497704422
    ],
    [
      49.88119106026967,
      -2.0825656673171813
    ],
    [
      50.00934391195337,
      -0.6573928525329509
    ],
    [
      49.995747418915194,
      0.7740104283277942
    ],
    [
      49.82845370090902,
      2.1958240349004186
    ],
    [
      49.527785011199114,
      3.597384614950251
    ],
    [
      49.10332059341581,
      4.963756900614875
    ],
    [
      48.46298208112134,
      6.2369433573442725
    ],
    [
      47.6584035099157,
      7.418509841056982
    ],
    [
      46.68469244997399,
      8.4610723915562
    ],
    [
      45.57521597182205,
      9.361156282379838
    ],
    [
      44.36678584916869,
      10.100135036434747
    ],
    [
      42.984213813628045,
      10.333565870241893
    ],
    [
      41.55227380238996,
      10.349956093501628
    ],
    [
      40.11945339687982,
      10.358816118391038
    ],
    [
      38.686609542218974,
      10.367784996171242
    ],
    [
      37.2537937579432,
      10.37345620812074
    ],
    [
      35.82098993864862,
      10.379156858201414
    ],
    [
      34.38820493510659,
      10.386231378265267
    ],
    [
      32.95537463424127,
      10.391996876175723
    ],
    [
      31.52254597203988,
      10.398292510248872
    ],
    [
      30.089765312175803,
      10.403854326585815
    ],
    [
      28.65698303725008,
      10.40674480366722
    ],
    [
      27.224146955643754,
      10.409839219575488
    ],
    [
      25.791321689339945,
      10.414526758898802
    ],
    [
      24.358526826411538,
      10.418023248151034
    ],
    [
      22.92567688998791,
      10.424302240824687
    ],
    [
      21.49281765562001,
      10.428812500988311
    ],
    [
      20.05997327995526,
      10.43311722890669
    ],
    [
      18.627130445150186,
      10.437350754001928
    ],
    [
      17.194311496970162,
      10.442684326147974
    ],
    [
      15.76146377157713,
      10.448082357843244
    ],
    [
      14.328607762765014,
      10.450564614004712
    ],
    [
      12.895775957789649,
      10.453755134834214
    ],
    [
      11.462921708973676,
      10.455545125764017
    ],
    [
      10.030053016740643,
      10.457968241652958
    ],
    [
      8.597186063287158,
      10.462568369386538
    ],
    [
      7.164320828860466,
      10.465751502724716
    ],
    [
      5.73147202664102,
      10.468031221316448
    ],
    [
      4.298615023084844,
      10.4700886300427
    ],
    [
      2.8657470394679567,
      10.472971402908605
    ],
    [
      1.433196908059927,
      10.47409474470096
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
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
  "axis_candidate": 2,
  "center": [
    0.23354384,
    4.118499999999914e-05,
    0.00010408500000000376
  ],
  "construction_scale": 243.59336657262259,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
