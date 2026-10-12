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
    -0.16041835752497197,
    0.07225976541054324
  ],
  "profile": [
    [
      0.7986873939031247,
      -7.331064881163319
    ],
    [
      2.342660973680143,
      -7.331446327162433
    ],
    [
      3.904444210181131,
      -7.332864749652683
    ],
    [
      5.466231333376039,
      -7.33275552992146
    ],
    [
      7.02799396391784,
      -7.332430796248749
    ],
    [
      8.58977648687182,
      -7.332053714431135
    ],
    [
      10.151550164733916,
      -7.331535559018599
    ],
    [
      11.71329939510461,
      -7.330486338048159
    ],
    [
      13.275081423619696,
      -7.329652140938734
    ],
    [
      14.83684400393244,
      -7.330381073507073
    ],
    [
      16.398592502633488,
      -7.328486200109371
    ],
    [
      17.960353771170848,
      -7.328174062628989
    ],
    [
      19.52210877224537,
      -7.3302270453340395
    ],
    [
      21.08387769847782,
      -7.331355644871364
    ],
    [
      22.645636912362654,
      -7.334423045787549
    ],
    [
      24.20739325624289,
      -7.3359554307237245
    ],
    [
      25.76911437553715,
      -7.337548837828372
    ],
    [
      27.330876160332515,
      -7.342091147254349
    ],
    [
      28.89265222439354,
      -7.338133014292753
    ],
    [
      30.45442691272242,
      -7.3359857373392074
    ],
    [
      32.0162088068021,
      -7.334313229078276
    ],
    [
      33.57794125954575,
      -7.331366454464116
    ],
    [
      35.13963465163901,
      -7.328385937150663
    ],
    [
      36.70134948539373,
      -7.3241894155453195
    ],
    [
      38.26307025299606,
      -7.320777365418995
    ],
    [
      39.82479989346366,
      -7.316188333315139
    ],
    [
      41.38655366353465,
      -7.30723701625835
    ],
    [
      42.94825069091548,
      -7.296893572686555
    ],
    [
      44.50990424751262,
      -7.282761762150853
    ],
    [
      46.07158137756163,
      -7.254354621452848
    ],
    [
      47.62791828028975,
      -7.150802192495913
    ],
    [
      49.02780546508866,
      -6.637137960979716
    ],
    [
      49.79813434174055,
      -5.375348071627819
    ],
    [
      49.93120866083987,
      -3.8436418560672254
    ],
    [
      49.90618764220536,
      -2.2835865329228526
    ],
    [
      49.8828544193454,
      -0.7213243661782993
    ],
    [
      49.87546981277093,
      0.8411171124036558
    ],
    [
      49.86663595042016,
      2.404698656871977
    ],
    [
      49.8516538330052,
      3.9724164508368687
    ],
    [
      49.83162180406292,
      5.538528311838098
    ],
    [
      49.47214922073478,
      6.9391355835072295
    ],
    [
      48.29962021340106,
      7.183474597150332
    ],
    [
      47.675062760551484,
      5.9859583793478635
    ],
    [
      47.658764110571866,
      4.426670597137867
    ],
    [
      47.680782441751674,
      2.858128195686293
    ],
    [
      47.70784115881344,
      1.2884471747641446
    ],
    [
      47.73128645714391,
      -0.28105534305325175
    ],
    [
      47.76373323837312,
      -1.847312804097153
    ],
    [
      47.80108540106845,
      -3.406594334739505
    ],
    [
      47.42267469763393,
      -4.73636366988883
    ],
    [
      46.06886099794998,
      -5.169730991192256
    ],
    [
      44.509696068372776,
      -5.1899578733270095
    ],
    [
      42.948081246422745,
      -5.180967222326164
    ],
    [
      41.386435623875045,
      -5.173416812500725
    ],
    [
      39.82477345587513,
      -5.165469601526277
    ],
    [
      38.26304270313598,
      -5.159870322829177
    ],
    [
      36.70129348646246,
      -5.1546783588742136
    ],
    [
      35.13956471332403,
      -5.150421449642744
    ],
    [
      33.577791742270165,
      -5.143792715964928
    ],
    [
      32.01602865601762,
      -5.136650444794741
    ],
    [
      30.454300870079543,
      -5.133627149827426
    ],
    [
      28.892530419220947,
      -5.129726928960736
    ],
    [
      27.330774078737505,
      -5.125000150499897
    ],
    [
      25.76903282527205,
      -5.122877183797425
    ],
    [
      24.20729571999884,
      -5.120525334868467
    ],
    [
      22.64552358246002,
      -5.118726811840045
    ],
    [
      21.083771112142507,
      -5.114900712799866
    ],
    [
      19.522036605418528,
      -5.114164198584492
    ],
    [
      17.960266909393887,
      -5.113767436604629
    ],
    [
      16.398496950958098,
      -5.110520971566355
    ],
    [
      14.8367125971204,
      -5.112160340013721
    ],
    [
      13.274938244059474,
      -5.114405618000704
    ],
    [
      11.713161371306725,
      -5.112228708119323
    ],
    [
      10.151445834755055,
      -5.1124293583395
    ],
    [
      8.589684835917222,
      -5.112825645599292
    ],
    [
      7.027910425896841,
      -5.11103107357161
    ],
    [
      5.4661370770363185,
      -5.1095552580192365
    ],
    [
      3.9043631372219862,
      -5.1105313075008105
    ],
    [
      2.3426338459647607,
      -5.111438324399737
    ],
    [
      0.7986811126314459,
      -5.113841046336127
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
    -0.004309919999999995,
    0.9158497299999999,
    -0.04844891000000001
  ],
  "construction_scale": 134.71039689454815,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
