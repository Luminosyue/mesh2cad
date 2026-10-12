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
    -0.040608338782930506,
    -0.00041476667602651613
  ],
  "profile": [
    [
      0.8064314647351882,
      -13.472023740170759
    ],
    [
      2.365364166249773,
      -13.472223595228426
    ],
    [
      3.9422586246023807,
      -13.472640878126782
    ],
    [
      5.519159378269089,
      -13.472750670359037
    ],
    [
      7.096067645873905,
      -13.472879577797608
    ],
    [
      8.672971556600087,
      -13.47313970142026
    ],
    [
      10.249851057379926,
      -13.4727385984603
    ],
    [
      11.826732216753374,
      -13.472961426537905
    ],
    [
      13.403631721614573,
      -13.473341819489136
    ],
    [
      14.980515301583646,
      -13.474004564522195
    ],
    [
      16.55741892563927,
      -13.474594245625516
    ],
    [
      18.13429489387521,
      -13.475010623849407
    ],
    [
      19.711179121297867,
      -13.47507120672798
    ],
    [
      21.288083941926804,
      -13.475442991884439
    ],
    [
      22.86499801213744,
      -13.475906016494935
    ],
    [
      24.441904484374366,
      -13.476344873090312
    ],
    [
      26.01876721232276,
      -13.47671447208592
    ],
    [
      27.59563056465728,
      -13.476072947199988
    ],
    [
      29.17252525737875,
      -13.47642100896169
    ],
    [
      30.749406076221604,
      -13.476876100127456
    ],
    [
      32.32628632896649,
      -13.477075625294589
    ],
    [
      33.90318125418664,
      -13.47741939798018
    ],
    [
      35.48005475264105,
      -13.477008260552765
    ],
    [
      37.05690964365735,
      -13.476321255521452
    ],
    [
      38.63378613551685,
      -13.476388449720218
    ],
    [
      40.21064782093533,
      -13.47644769848164
    ],
    [
      41.78752238313038,
      -13.47670382072724
    ],
    [
      43.3644044761036,
      -13.477676464832225
    ],
    [
      44.94125754324598,
      -13.477476255837558
    ],
    [
      46.516472557235076,
      -13.476018018481941
    ],
    [
      48.08699620768253,
      -13.456446976349707
    ],
    [
      49.489604453489875,
      -13.083913533905122
    ],
    [
      49.910761488764436,
      -11.738730513154824
    ],
    [
      49.88295247145499,
      -10.164766494034499
    ],
    [
      49.83123370527902,
      -8.588731150365756
    ],
    [
      49.77970869850992,
      -7.012896556007506
    ],
    [
      49.72706988577082,
      -5.4369722766019795
    ],
    [
      49.668252760548285,
      -3.8613471062656908
    ],
    [
      49.60988655710511,
      -2.2847868535365032
    ],
    [
      49.55700252381699,
      -0.7072578219709782
    ],
    [
      49.50291221489128,
      0.8697727531498769
    ],
    [
      49.445531640323864,
      2.446850146533982
    ],
    [
      49.384527079728834,
      4.0238339789088196
    ],
    [
      49.32672379448606,
      5.600218556422659
    ],
    [
      49.27590426842579,
      7.175724124201816
    ],
    [
      49.22418946751246,
      8.750732175843687
    ],
    [
      49.16832639329145,
      10.325815435338928
    ],
    [
      49.120637011546364,
      11.901078058088896
    ],
    [
      48.99344304397631,
      13.448816820029247
    ],
    [
      48.066951314086786,
      14.383260921927658
    ],
    [
      46.518464756519464,
      14.478812045174134
    ],
    [
      44.94161858970865,
      14.479142653883837
    ],
    [
      43.36472111269401,
      14.478587580902174
    ],
    [
      41.7878239403539,
      14.477987581554912
    ],
    [
      40.21094129137431,
      14.478383146833217
    ],
    [
      38.63406359706158,
      14.477668429316793
    ],
    [
      37.057165584585285,
      14.47652612520342
    ],
    [
      35.480279663312395,
      14.476472666663835
    ],
    [
      33.9034106532581,
      14.47605566213462
    ],
    [
      32.32650940625784,
      14.475387938158882
    ],
    [
      30.749606046917833,
      14.476189842025828
    ],
    [
      29.172710759768897,
      14.476305915090709
    ],
    [
      27.595807844528185,
      14.476096847548543
    ],
    [
      26.018922297868965,
      14.475879586460481
    ],
    [
      24.442024458976455,
      14.475537483171472
    ],
    [
      22.865115245903233,
      14.475876559052015
    ],
    [
      21.288208372136985,
      14.476070074018342
    ],
    [
      19.711311166515824,
      14.47601755206724
    ],
    [
      18.134404341485105,
      14.476279601318478
    ],
    [
      16.55750568340567,
      14.476367385941117
    ],
    [
      14.980613808943497,
      14.476565375354127
    ],
    [
      13.403708570618285,
      14.477470751348175
    ],
    [
      11.826802937115836,
      14.477990276220618
    ],
    [
      10.249894604847462,
      14.47847394897985
    ],
    [
      8.672986077078585,
      14.479131355265519
    ],
    [
      7.096068971672161,
      14.479048423025757
    ],
    [
      5.519158501476814,
      14.479267700792285
    ],
    [
      3.9422604049087333,
      14.479918372647958
    ],
    [
      2.3653577477017613,
      14.4799680535224
    ],
    [
      0.8064257680987529,
      14.480038975805519
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
    -0.00020485500000000378,
    -0.10901115,
    -2.7045000000003316e-05
  ],
  "construction_scale": 100.06298865072574,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
