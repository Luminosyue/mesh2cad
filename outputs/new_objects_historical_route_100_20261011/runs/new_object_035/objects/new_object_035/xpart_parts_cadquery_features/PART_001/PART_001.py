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
    -0.031076762208537338,
    -0.6937071443200329
  ],
  "profile": [
    [
      1.2364737084756303,
      -1.3836623160910495
    ],
    [
      2.4724115172562517,
      -1.3828881285942878
    ],
    [
      3.7086182565386228,
      -1.38216328658548
    ],
    [
      4.9448260588148925,
      -1.3817602623561949
    ],
    [
      6.181036362369165,
      -1.3815280960973073
    ],
    [
      7.4172393100919685,
      -1.3812013379193453
    ],
    [
      8.6534479880885,
      -1.3805550086791416
    ],
    [
      9.889661440793962,
      -1.3803836610784104
    ],
    [
      11.1258733253947,
      -1.3801711229366669
    ],
    [
      12.362077108065899,
      -1.3795138822576556
    ],
    [
      13.598289112813077,
      -1.3789077643348688
    ],
    [
      14.834499204668976,
      -1.3785955392605285
    ],
    [
      16.07070865906179,
      -1.37761249379803
    ],
    [
      17.30691679502316,
      -1.377410558272199
    ],
    [
      18.543125396956015,
      -1.376835853096938
    ],
    [
      19.779330558808574,
      -1.3759995648166052
    ],
    [
      21.01552875056933,
      -1.375429810951669
    ],
    [
      22.251722150159175,
      -1.3752667504451583
    ],
    [
      23.487937452418688,
      -1.3739317596879594
    ],
    [
      24.724148897944232,
      -1.372595087684728
    ],
    [
      25.960352009234178,
      -1.3714576735843726
    ],
    [
      27.196559163909374,
      -1.3711551096445618
    ],
    [
      28.43276378302791,
      -1.3708246356840683
    ],
    [
      29.66896912422459,
      -1.3690918124637714
    ],
    [
      30.905178558893205,
      -1.3678467240582306
    ],
    [
      32.14138371608662,
      -1.3663092860352952
    ],
    [
      33.377587340579225,
      -1.3661853288046006
    ],
    [
      34.61379539745842,
      -1.364848172410713
    ],
    [
      35.85000359361946,
      -1.363032478556406
    ],
    [
      37.08621387989619,
      -1.3608220225391388
    ],
    [
      38.3224175051679,
      -1.358730153814451
    ],
    [
      39.558617971369905,
      -1.3569322070806629
    ],
    [
      40.79482333261939,
      -1.354372629287441
    ],
    [
      42.03101975666577,
      -1.3512572110365428
    ],
    [
      43.267216451980374,
      -1.347645406993267
    ],
    [
      44.50340133780033,
      -1.3433205189592972
    ],
    [
      45.73959122332079,
      -1.337871547194771
    ],
    [
      46.97459665349901,
      -1.3299022431595118
    ],
    [
      48.07532199673591,
      -1.0539191133481136
    ],
    [
      48.4202036912684,
      -0.00663284279435728
    ],
    [
      48.06835371159532,
      1.0526896092440254
    ],
    [
      46.97298244802738,
      1.332009067865821
    ],
    [
      45.73807539002608,
      1.3246998945425523
    ],
    [
      44.50192718396101,
      1.314645675243793
    ],
    [
      43.26575911589926,
      1.3074308671705417
    ],
    [
      42.029574423479545,
      1.3033054703566873
    ],
    [
      40.79339150916272,
      1.2990948779707308
    ],
    [
      39.557195184328265,
      1.2943862488140532
    ],
    [
      38.321009504634944,
      1.28702185152859
    ],
    [
      37.08483599105598,
      1.2793245635883013
    ],
    [
      35.84866825882743,
      1.271922913515935
    ],
    [
      34.612501354118805,
      1.2660970949583135
    ],
    [
      33.37631729481172,
      1.2619468149271444
    ],
    [
      32.140188740188634,
      1.251227628721106
    ],
    [
      30.9040900437396,
      1.2440590242002019
    ],
    [
      29.667912720691234,
      1.2368779934677008
    ],
    [
      28.431728642686302,
      1.228148258306145
    ],
    [
      27.195548884917265,
      1.2193693435310897
    ],
    [
      25.95938473011124,
      1.2076839426269113
    ],
    [
      24.723222562488445,
      1.1966250082480299
    ],
    [
      23.487058413495078,
      1.183851788171427
    ],
    [
      22.250905524958736,
      1.1686051105233042
    ],
    [
      21.014752131823343,
      1.1525403402125955
    ],
    [
      19.77860178631326,
      1.138010958230105
    ],
    [
      18.54250991034418,
      1.1269445965086073
    ],
    [
      17.30641273948314,
      1.1163215377907383
    ],
    [
      16.07030163911857,
      1.105231080921985
    ],
    [
      14.834174717356106,
      1.0955634141083883
    ],
    [
      13.598031101119577,
      1.085167432380486
    ],
    [
      12.36187182634104,
      1.0742233518332622
    ],
    [
      11.12571157655546,
      1.066407200441017
    ],
    [
      9.889531103455276,
      1.0587386862270547
    ],
    [
      8.653347135136768,
      1.051206164489361
    ],
    [
      7.4171624276205215,
      1.0440572190690691
    ],
    [
      6.180976803861505,
      1.038921512496905
    ],
    [
      4.944781054721041,
      1.036333007305754
    ],
    [
      3.7085931593091455,
      1.0328300805309054
    ],
    [
      2.472398805777561,
      1.0298414024956541
    ],
    [
      1.2364706876522829,
      1.0276819273694047
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
    0.000666434999999993,
    -0.0028294700000000006,
    -0.01232784
  ],
  "construction_scale": 170.49754183464083,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
