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
    -0.6142566976332801,
    0.0005255014915781127
  ],
  "profile": [
    [
      0.7640862921625802,
      -20.079533349721302
    ],
    [
      1.7385116157382479,
      -22.23630193786874
    ],
    [
      2.9577039564461263,
      -24.263253862941617
    ],
    [
      4.460655334532619,
      -26.076658117558644
    ],
    [
      6.303765103225529,
      -27.53660485943127
    ],
    [
      8.41880456759289,
      -28.563277534110014
    ],
    [
      10.685128149124827,
      -29.14272256943326
    ],
    [
      13.027336937614596,
      -29.33873618884315
    ],
    [
      15.393396595212721,
      -29.395848578148957
    ],
    [
      17.763155337449078,
      -29.492943065782427
    ],
    [
      20.133238791627804,
      -29.5109765048134
    ],
    [
      22.503462200603394,
      -29.52993233349156
    ],
    [
      24.873783503777844,
      -29.534699333041463
    ],
    [
      27.24379550975821,
      -29.541802574487473
    ],
    [
      29.61346476930611,
      -29.533414651432913
    ],
    [
      31.983267691746526,
      -29.53018526406732
    ],
    [
      34.34999688757721,
      -29.48835156495297
    ],
    [
      36.6765801372848,
      -29.247500156064266
    ],
    [
      38.803102041928,
      -28.59897408718337
    ],
    [
      40.676667387565814,
      -27.345373064084455
    ],
    [
      42.224376382047204,
      -25.52873912806686
    ],
    [
      43.19838874408876,
      -23.393942051148233
    ],
    [
      43.68795794146219,
      -21.095180863094978
    ],
    [
      43.902779955286974,
      -18.73985836498216
    ],
    [
      43.98575912254198,
      -16.371313430435123
    ],
    [
      44.003786355376214,
      -14.002134011608998
    ],
    [
      44.081522870471765,
      -11.632839940555314
    ],
    [
      44.129882444791434,
      -9.278159625267751
    ],
    [
      44.1253296013175,
      -6.93913436664583
    ],
    [
      44.12312976976554,
      -4.600641200031356
    ],
    [
      44.101257109211346,
      -2.255596339145875
    ],
    [
      44.07647938173197,
      0.10241437171556546
    ],
    [
      44.07690243465279,
      2.4619623877290078
    ],
    [
      44.061133065543004,
      4.821324678370978
    ],
    [
      44.05591632366619,
      7.184899603089065
    ],
    [
      44.0824845621941,
      9.570024509317491
    ],
    [
      44.100161471280614,
      11.958986051156081
    ],
    [
      44.1214179686136,
      14.347624051486617
    ],
    [
      44.11890731904153,
      16.716215502444243
    ],
    [
      44.00956017271694,
      19.06149939596791
    ],
    [
      43.97893367228308,
      21.409512419327825
    ],
    [
      43.85952026432173,
      23.758570472895123
    ],
    [
      42.99020544340351,
      25.900187962063946
    ],
    [
      41.15513557292735,
      27.46389909375148
    ],
    [
      38.90744120197992,
      28.27154763704415
    ],
    [
      36.54332055095751,
      28.57841284348592
    ],
    [
      34.15769927585218,
      28.717319419167744
    ],
    [
      31.764155248813278,
      28.824150033419738
    ],
    [
      29.371148186154308,
      28.812693221318092
    ],
    [
      27.044153734203483,
      28.47023152882445
    ],
    [
      25.155302702029665,
      27.358329900493807
    ],
    [
      24.0608133563424,
      25.55939710614566
    ],
    [
      23.567246834959917,
      23.389540956131384
    ],
    [
      23.216865237647575,
      21.119138483937498
    ],
    [
      23.0455852918233,
      18.808692063249328
    ],
    [
      23.03483850278044,
      16.482288117337863
    ],
    [
      23.019613700748394,
      14.15673112153582
    ],
    [
      23.006149206269814,
      11.83452067559616
    ],
    [
      23.01614644754029,
      9.515904820563648
    ],
    [
      23.036428365900292,
      7.197530373414983
    ],
    [
      23.07780179485195,
      4.8719447184223
    ],
    [
      23.11610256240251,
      2.5081114726534395
    ],
    [
      23.20815373516383,
      0.1277073518800065
    ],
    [
      23.31421499767735,
      -2.2534931141666315
    ],
    [
      23.330812294935924,
      -4.633887112023039
    ],
    [
      23.266176088189148,
      -7.013627797949312
    ],
    [
      23.141099865906746,
      -9.394040564170027
    ],
    [
      22.87675981143341,
      -11.682258946519639
    ],
    [
      21.778480326014712,
      -13.229656027989243
    ],
    [
      19.6563535321959,
      -14.010413719049044
    ],
    [
      17.28696144800339,
      -14.043619941676017
    ],
    [
      14.933457022819535,
      -13.985350203001257
    ],
    [
      12.685527132503376,
      -13.91247274011263
    ],
    [
      10.48754923608415,
      -13.733186518153406
    ],
    [
      8.157373016898282,
      -13.584228774884835
    ],
    [
      5.778683720250182,
      -13.39205486273428
    ],
    [
      3.503947808656134,
      -12.891948596256576
    ],
    [
      1.4242064222068307,
      -12.185699252656564
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.41705809179224723,
      0.8207093180649142,
      -0.3905109003754351
    ],
    [
      -0.10869627676091581,
      0.3815391482782156,
      0.917939539266856
    ],
    [
      0.9023567296191256,
      0.4252811935326524,
      -0.0699159419483055
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.182879275,
    0.226346925,
    -0.07015743
  ],
  "construction_scale": 372.9894887459187,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
