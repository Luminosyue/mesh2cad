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
    -0.08948824361216488,
    0.00719864242272527
  ],
  "profile": [
    [
      0.9952095404688628,
      -49.497002241156025
    ],
    [
      2.9170075444089267,
      -49.38052263265399
    ],
    [
      4.854953284858524,
      -49.19611181707418
    ],
    [
      6.788717518177128,
      -48.96525372370459
    ],
    [
      8.711489156986902,
      -48.64257371488998
    ],
    [
      10.616798165236636,
      -48.24583105617137
    ],
    [
      12.502833001650858,
      -47.759658259042574
    ],
    [
      14.370935078172167,
      -47.217910392732804
    ],
    [
      16.217732467896877,
      -46.59549227778689
    ],
    [
      18.0307780572738,
      -45.88239933473841
    ],
    [
      19.82518378354152,
      -45.096402969037015
    ],
    [
      21.60901282226903,
      -44.2641164679277
    ],
    [
      23.368223101748757,
      -43.37321820028602
    ],
    [
      25.052075220430872,
      -42.41324730699604
    ],
    [
      26.69920208726095,
      -41.40988528822501
    ],
    [
      28.313516758495833,
      -40.36646288210323
    ],
    [
      29.905654869100744,
      -39.23279284975287
    ],
    [
      31.46497211713521,
      -38.05478399352438
    ],
    [
      32.990314449240145,
      -36.83018777804695
    ],
    [
      34.44219540916441,
      -35.53913351501623
    ],
    [
      35.857133513725245,
      -34.189205375695806
    ],
    [
      37.19583701418686,
      -32.772848186415416
    ],
    [
      38.45828525708302,
      -31.31000449095599
    ],
    [
      39.68053694040649,
      -29.818001925040903
    ],
    [
      40.84816233553801,
      -28.28257928227346
    ],
    [
      41.92866183228429,
      -26.676899841634082
    ],
    [
      42.947748287867384,
      -25.00485221646365
    ],
    [
      43.90890373588732,
      -23.295697406512673
    ],
    [
      44.79869138023183,
      -21.550143021028646
    ],
    [
      45.59122042111502,
      -19.771177388684805
    ],
    [
      46.32298558909157,
      -17.960903103403645
    ],
    [
      46.98159031029488,
      -16.1222493926661
    ],
    [
      47.59171281741506,
      -14.2663084514707
    ],
    [
      48.12089586106352,
      -12.393043087469465
    ],
    [
      48.582141616379886,
      -10.497526480129554
    ],
    [
      49.00041874670748,
      -8.581323393160641
    ],
    [
      49.335270374128896,
      -6.655723662740818
    ],
    [
      49.603046959526885,
      -4.724654274477592
    ],
    [
      49.76605441663451,
      -2.7829490700304236
    ],
    [
      49.838821840041994,
      -0.8388330893368537
    ],
    [
      49.8323732397351,
      1.1107199711429225
    ],
    [
      49.74987237129022,
      3.0625721517865623
    ],
    [
      49.606653390606915,
      5.009149104453704
    ],
    [
      49.41236906878862,
      6.942513563333016
    ],
    [
      49.13688583460679,
      8.869755449164016
    ],
    [
      48.77987405938234,
      10.790969743376424
    ],
    [
      48.327135043255666,
      12.694207231546187
    ],
    [
      47.78782553969792,
      14.58232381445363
    ],
    [
      47.16204664846744,
      16.443581250430594
    ],
    [
      46.47123121200096,
      18.287238497437066
    ],
    [
      45.68192982347436,
      20.105950842048173
    ],
    [
      44.8369240202697,
      21.867775931363678
    ],
    [
      43.93468397226759,
      23.600796752122914
    ],
    [
      42.98797961817512,
      25.316007154689654
    ],
    [
      41.985886172745175,
      26.989397356683966
    ],
    [
      40.901382370816634,
      28.604321365266756
    ],
    [
      39.76603948792094,
      30.17167203960566
    ],
    [
      38.520795344287706,
      31.651454646753955
    ],
    [
      37.22402392374443,
      33.0946155148587
    ],
    [
      35.877282252427214,
      34.50121134369106
    ],
    [
      34.48095257614663,
      35.843530942921
    ],
    [
      33.040212566108565,
      37.126861840697316
    ],
    [
      31.548545208060414,
      38.394454311826834
    ],
    [
      30.00362318708546,
      39.617202436363826
    ],
    [
      28.409355181007903,
      40.78921436103174
    ],
    [
      26.7907017648658,
      41.89362879107125
    ],
    [
      25.134957629975634,
      42.90620573353388
    ],
    [
      23.421190719480503,
      43.8060950637131
    ],
    [
      21.67734675970954,
      44.671369188196834
    ],
    [
      19.900782463431753,
      45.479085194704595
    ],
    [
      18.093657153101503,
      46.207153277340396
    ],
    [
      16.25456204267507,
      46.85645242810412
    ],
    [
      14.396329874247225,
      47.43662184223811
    ],
    [
      12.52164070823204,
      47.987158731639475
    ],
    [
      10.631123760532418,
      48.45980959405663
    ],
    [
      8.72381095904082,
      48.85545402591251
    ],
    [
      6.799749017902188,
      49.13413282359999
    ],
    [
      4.863318073960616,
      49.33297990114792
    ],
    [
      2.920806509808658,
      49.46443171123568
    ],
    [
      0.9958171770688907,
      49.53644545803788
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
    -0.640649625,
    0.367466595,
    -0.368161995
  ],
  "construction_scale": 649.0634177148229,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
