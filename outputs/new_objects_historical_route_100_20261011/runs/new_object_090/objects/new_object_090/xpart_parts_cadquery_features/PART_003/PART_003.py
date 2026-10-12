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
    0.01379370756149612,
    -0.00480016687492417
  ],
  "profile": [
    [
      0.16835337930623645,
      -52.03809772097871
    ],
    [
      0.8118721405172981,
      -51.39777833245368
    ],
    [
      0.9029121321508968,
      -50.11548244633334
    ],
    [
      0.9172808479366475,
      -48.79726851049877
    ],
    [
      0.9189219067918426,
      -47.47909813682881
    ],
    [
      0.9159634583008842,
      -46.160903658181056
    ],
    [
      0.9112464729738485,
      -44.842670026623225
    ],
    [
      0.9125460072303775,
      -43.52445777046162
    ],
    [
      0.9183179361169596,
      -42.206267125365216
    ],
    [
      0.9217131826733448,
      -40.88792470134625
    ],
    [
      0.9128299476473922,
      -39.569581103484616
    ],
    [
      0.9009645786723298,
      -38.251451822904954
    ],
    [
      0.9011148343827704,
      -36.93328273142137
    ],
    [
      0.9043093686653355,
      -35.61512560963796
    ],
    [
      0.9057970451908831,
      -34.29684759248198
    ],
    [
      0.9091567474396665,
      -32.978513508329705
    ],
    [
      0.9085211958615755,
      -31.660252936108677
    ],
    [
      0.9041323319579251,
      -30.341966146776183
    ],
    [
      0.9052545981902222,
      -29.023674928613303
    ],
    [
      0.9026106057914427,
      -27.70532484307784
    ],
    [
      0.8995581423465306,
      -26.387139825052074
    ],
    [
      0.896818095170506,
      -25.068834862469014
    ],
    [
      0.8974788006377152,
      -23.75060601607175
    ],
    [
      0.9011908753361842,
      -22.432338607080343
    ],
    [
      0.9029456731410693,
      -21.11407235620596
    ],
    [
      0.906275423974914,
      -19.79602658322801
    ],
    [
      0.9079732969676182,
      -18.477938958569005
    ],
    [
      0.916693350334175,
      -17.159752851396313
    ],
    [
      0.9232669747122815,
      -15.841463872007484
    ],
    [
      0.9250293412983382,
      -14.523163704878119
    ],
    [
      0.9211883930093359,
      -13.204878377549244
    ],
    [
      0.9180088109032678,
      -11.886772015584164
    ],
    [
      0.9165064009498372,
      -10.56876545093446
    ],
    [
      0.918321052915857,
      -9.250726616572702
    ],
    [
      0.9265295553898585,
      -7.932373267498063
    ],
    [
      0.9223662469170124,
      -6.613841733827417
    ],
    [
      0.9164513640118537,
      -5.295289653925497
    ],
    [
      0.9186935111505007,
      -3.976755599111783
    ],
    [
      0.9145120497016792,
      -2.6582271899951198
    ],
    [
      0.91315817387235,
      -1.3397457135173374
    ],
    [
      0.9069222640643647,
      -0.020730705314139244
    ],
    [
      0.9055062510549983,
      1.2980391363169932
    ],
    [
      0.915110868817133,
      2.6163710640892415
    ],
    [
      0.9237027316755113,
      3.9346383649120202
    ],
    [
      0.9246278795727179,
      5.252661971658484
    ],
    [
      0.9221325542583512,
      6.570674765630762
    ],
    [
      0.9233423934448217,
      7.88867469875861
    ],
    [
      0.9287666131957717,
      9.206703413952734
    ],
    [
      0.9270011755685386,
      10.525191556284208
    ],
    [
      0.9240484060067437,
      11.843669424661973
    ],
    [
      0.9238279658388713,
      13.162054077815563
    ],
    [
      0.9227175872561229,
      14.48055852118156
    ],
    [
      0.9206370724774318,
      15.799200851314104
    ],
    [
      0.9188724970014863,
      17.11782713844788
    ],
    [
      0.919024052087809,
      18.436479139876347
    ],
    [
      0.9159925309670092,
      19.755155168062622
    ],
    [
      0.9093709559310021,
      21.07379093275835
    ],
    [
      0.9076526293335361,
      22.392446990445986
    ],
    [
      0.9044774698486895,
      23.71106143079996
    ],
    [
      0.9043533466922156,
      25.029746508097777
    ],
    [
      0.9024071838016992,
      26.348361731975196
    ],
    [
      0.9026906071040028,
      27.667051340161137
    ],
    [
      0.9100788495839641,
      28.98581455734551
    ],
    [
      0.9161371254969979,
      30.304526852073884
    ],
    [
      0.9193592954671702,
      31.623112998544464
    ],
    [
      0.9160492836831808,
      32.94121359192565
    ],
    [
      0.9126048446614823,
      34.259051327997284
    ],
    [
      0.9153855851446531,
      35.576987031953124
    ],
    [
      0.9257381298798614,
      36.895178477026064
    ],
    [
      0.9317520022991055,
      38.21349884914838
    ],
    [
      0.936182289194716,
      39.53171950811868
    ],
    [
      0.9366024125196724,
      40.849814978380486
    ],
    [
      0.9278298755412935,
      42.16857053718856
    ],
    [
      0.9212143965406676,
      43.48755117642861
    ],
    [
      0.9180791002944996,
      44.806643803302556
    ],
    [
      0.91285057297701,
      46.12572719751486
    ],
    [
      0.9097923330519397,
      47.44462258670407
    ],
    [
      0.9090634258939286,
      48.76281638050992
    ],
    [
      0.9212556701681203,
      50.081040294313496
    ],
    [
      0.8443208738326566,
      51.35665705914481
    ],
    [
      0.16920329323424543,
      51.97769825886386
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.27875321495220895,
      -0.9361585188522702,
      -0.21425189085310536
    ],
    [
      0.061527817806954425,
      0.2052275663559659,
      -0.9767783646475396
    ],
    [
      0.9583897812423302,
      -0.28546256074646803,
      0.0003919468678275098
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.0045872849999999965,
    0.03206848,
    -0.24133195
  ],
  "construction_scale": 106.52991180420561,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
