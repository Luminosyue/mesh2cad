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
    -0.5939783676558636,
    0.8246933801349638
  ],
  "profile": [
    [
      1.0861984767106003,
      6.45626671051409
    ],
    [
      3.145659438907936,
      6.822329150409896
    ],
    [
      5.027807550898993,
      7.538386600239913
    ],
    [
      6.480862741334894,
      8.93499812568075
    ],
    [
      7.74307104195313,
      10.791842339323805
    ],
    [
      8.82590604527924,
      12.674003230132701
    ],
    [
      9.804857665467374,
      14.47318461420153
    ],
    [
      11.226694957143994,
      15.967846299963437
    ],
    [
      13.220614562216255,
      16.66458621477198
    ],
    [
      15.384897412080754,
      16.733825169839363
    ],
    [
      17.534720755009737,
      16.81200067335329
    ],
    [
      19.67762784251812,
      17.064526721398437
    ],
    [
      21.79222509559562,
      17.11331843383918
    ],
    [
      23.812677894360817,
      17.1191870565279
    ],
    [
      25.974333305200872,
      17.101480143484814
    ],
    [
      28.164505719184366,
      17.08931847486518
    ],
    [
      30.35491143761074,
      17.085266062007268
    ],
    [
      32.525248689779694,
      17.056984560805986
    ],
    [
      34.6276530538328,
      16.998456370522067
    ],
    [
      36.79340629695601,
      16.910444921367237
    ],
    [
      38.94859201689968,
      16.730404943606764
    ],
    [
      41.014886784397305,
      16.112486696246467
    ],
    [
      42.73052342191485,
      14.977340676459969
    ],
    [
      43.738235578982454,
      13.175012764379062
    ],
    [
      44.148184950376134,
      11.140864376366597
    ],
    [
      44.398432406111596,
      8.987554106668618
    ],
    [
      44.50065127383018,
      6.810520514854889
    ],
    [
      44.566407085713806,
      4.670267367082577
    ],
    [
      44.63701780203575,
      2.5376974396014145
    ],
    [
      44.676652544285595,
      0.4086112598338027
    ],
    [
      44.75446402267406,
      -1.716107141456847
    ],
    [
      44.78614006392971,
      -3.852748976393463
    ],
    [
      44.65066809915088,
      -6.024633076607451
    ],
    [
      44.55837829994531,
      -8.191918902253445
    ],
    [
      44.500981326706174,
      -10.357692959418403
    ],
    [
      44.42699334543464,
      -12.52378415341878
    ],
    [
      44.4178845222864,
      -14.686747383478245
    ],
    [
      44.92605404763743,
      -16.72933258504336
    ],
    [
      46.30949220855952,
      -17.697020488018264
    ],
    [
      47.799743324918,
      -16.86825473180859
    ],
    [
      48.384188998627195,
      -14.947355368468639
    ],
    [
      48.50820428668004,
      -12.896070341779252
    ],
    [
      48.55703449976181,
      -10.793417977473311
    ],
    [
      48.645127516019144,
      -8.63418240553853
    ],
    [
      48.72811613077156,
      -6.463630322808943
    ],
    [
      48.81501373370122,
      -4.284707626299371
    ],
    [
      48.75660609132929,
      -2.107838502361603
    ],
    [
      48.71788832009348,
      0.06991062874246663
    ],
    [
      48.67604724854589,
      2.246414270225298
    ],
    [
      48.61192940994361,
      4.39408792928504
    ],
    [
      48.50215552811159,
      6.527721788817281
    ],
    [
      48.420010679805294,
      8.662203852257054
    ],
    [
      48.352459176925436,
      10.78712471728964
    ],
    [
      48.10466507149064,
      12.87659481447281
    ],
    [
      47.61404718925735,
      14.879853351827371
    ],
    [
      46.71432126001324,
      16.825802670957035
    ],
    [
      45.382924539422525,
      18.601651276713188
    ],
    [
      43.67918146526257,
      19.716678952760695
    ],
    [
      41.653713496977076,
      20.456530133153443
    ],
    [
      39.54350536566376,
      20.814792550982347
    ],
    [
      37.410559643408135,
      20.97969585702946
    ],
    [
      35.25408773286646,
      21.07861534991234
    ],
    [
      33.071852872889465,
      21.13859271800616
    ],
    [
      30.88886750330895,
      21.157633434037493
    ],
    [
      28.775232181759087,
      21.1595423852108
    ],
    [
      26.64535320644388,
      21.15997448813839
    ],
    [
      24.456428292786573,
      21.178269278094138
    ],
    [
      22.26798579240102,
      21.20289365563368
    ],
    [
      20.141779523297973,
      21.222499336513145
    ],
    [
      18.112417320667156,
      21.203449422650582
    ],
    [
      15.984762598725794,
      21.097668541117518
    ],
    [
      13.841820073128448,
      21.027788050242577
    ],
    [
      11.704924486979966,
      20.80011733840803
    ],
    [
      9.602897672841468,
      20.447976886398592
    ],
    [
      7.580379884781154,
      19.677346868957443
    ],
    [
      5.750771487372582,
      18.531946136831053
    ],
    [
      4.329182937002465,
      16.97053826064142
    ],
    [
      3.3655522964245748,
      15.07105875763694
    ],
    [
      2.4691067819558814,
      13.16764340096389
    ],
    [
      0.9853995691526151,
      11.913687620873986
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.8300569452208705,
      0.3406899237787835,
      -0.44151539443852206
    ],
    [
      0.37747063568227446,
      0.23955324296089886,
      0.8944999513608349
    ],
    [
      0.41051356480415657,
      -0.909144993729011,
      0.07024239097055367
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.525039805,
    -0.58169531,
    0.37105049
  ],
  "construction_scale": 411.7802929775606,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
