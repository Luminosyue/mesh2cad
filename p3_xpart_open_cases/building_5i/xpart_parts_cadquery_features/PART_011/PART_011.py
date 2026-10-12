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
    -0.17588310258692988,
    -0.08380362632340577
  ],
  "profile": [
    [
      0.27374889891231285,
      -49.98419519725781
    ],
    [
      1.8329441896594885,
      -49.5987989430472
    ],
    [
      2.1864852426530934,
      -48.03189372947871
    ],
    [
      1.8516881927977313,
      -46.114882231212796
    ],
    [
      1.8449442690534639,
      -44.10297081794987
    ],
    [
      1.8469287522429845,
      -42.08825921909388
    ],
    [
      1.855690593694352,
      -40.07559068606639
    ],
    [
      1.8569943670511524,
      -38.065913734860715
    ],
    [
      1.8576302905045927,
      -36.05209136419624
    ],
    [
      1.8541936931808336,
      -34.0439211904533
    ],
    [
      1.8546500661427907,
      -32.03724171915668
    ],
    [
      1.8537298371804947,
      -30.0305851012915
    ],
    [
      1.8590321778292076,
      -28.023918454751872
    ],
    [
      1.860354238724856,
      -26.016425643768294
    ],
    [
      1.8679143378082324,
      -24.00810532736403
    ],
    [
      1.8809570385154746,
      -21.99977167125543
    ],
    [
      1.893911687606054,
      -19.99181109221106
    ],
    [
      1.795927786691663,
      -17.996949302960644
    ],
    [
      1.7485813262747731,
      -15.99389784412286
    ],
    [
      1.7465030040988228,
      -13.986093695971826
    ],
    [
      1.7459112453579646,
      -11.979142501714765
    ],
    [
      1.797092409038666,
      -9.99283234384556
    ],
    [
      1.7912135289690545,
      -8.035361205305882
    ],
    [
      1.6937021100799021,
      -6.041098481346527
    ],
    [
      1.6894795697930243,
      -4.0313558785298405
    ],
    [
      1.6893755765404532,
      -2.021226499566347
    ],
    [
      1.6858646526545282,
      -0.011096437022324948
    ],
    [
      1.6853313360431494,
      1.998985409026049
    ],
    [
      1.686145784514715,
      4.009070073440666
    ],
    [
      1.6866761952920122,
      6.019102469130126
    ],
    [
      1.686231098874701,
      8.029238199396033
    ],
    [
      1.6873045670031792,
      10.039350710785406
    ],
    [
      1.6878368595787863,
      12.049467923464597
    ],
    [
      1.687578014747686,
      14.059487273515906
    ],
    [
      1.6856668440587423,
      16.067541209032505
    ],
    [
      1.687709104332039,
      18.07404060766209
    ],
    [
      1.6899594154584552,
      20.080487590459075
    ],
    [
      1.6882439537062328,
      22.08694794271489
    ],
    [
      1.6865487847774299,
      24.093445391630624
    ],
    [
      1.6871549624537558,
      26.09995881885066
    ],
    [
      1.6855270688518122,
      28.106455534875877
    ],
    [
      1.6900162128290885,
      30.11294051175766
    ],
    [
      1.6910335354186143,
      32.11938447206803
    ],
    [
      1.688075415087567,
      34.125875766069335
    ],
    [
      1.6863615495324322,
      36.132361594537706
    ],
    [
      1.6901049230658782,
      38.13884461769105
    ],
    [
      1.6966719462964457,
      40.14526202422487
    ],
    [
      1.6987961027180483,
      42.15172105005018
    ],
    [
      1.7032686752467832,
      44.1585286747632
    ],
    [
      1.7103108165712686,
      46.16757798646892
    ],
    [
      1.715639790021693,
      48.17180744101567
    ],
    [
      1.258542083834377,
      49.58757958741032
    ],
    [
      0.5945310186449583,
      48.42493795864995
    ],
    [
      0.547727563967018,
      46.42577017724162
    ],
    [
      0.5430451903909752,
      44.41425707468163
    ],
    [
      0.5436930761735695,
      42.40272412171933
    ],
    [
      0.5474102969978769,
      40.39208524408075
    ],
    [
      0.5457948838126158,
      38.38322587175385
    ],
    [
      0.5454880427181062,
      36.37474458884506
    ],
    [
      0.5500924256438877,
      34.36812606955153
    ],
    [
      0.5554441567367778,
      32.35933086309038
    ],
    [
      0.5556605624499892,
      30.34843127223806
    ],
    [
      0.5503750993689469,
      28.338168717650298
    ],
    [
      0.5425734713930123,
      26.3279632235486
    ],
    [
      0.5394690439367628,
      24.3181810500353
    ],
    [
      0.5402552235066599,
      22.308663017476444
    ],
    [
      0.5409324422849562,
      20.300057071333605
    ],
    [
      0.5378388831049389,
      18.29318421774514
    ],
    [
      0.540603483429352,
      16.286789679366997
    ],
    [
      0.5488758749617346,
      14.280440807861268
    ],
    [
      0.5487177644613197,
      12.274151344764384
    ],
    [
      0.5458234681566589,
      10.267757015288119
    ],
    [
      0.5415653381059712,
      8.261482974857438
    ],
    [
      0.5442160541809488,
      6.255196750196239
    ],
    [
      0.546706816479503,
      4.2489024877027255
    ],
    [
      0.5457456174792275,
      2.2426079169337605
    ],
    [
      0.5428624099296582,
      0.23638413839015962
    ],
    [
      0.548673931743247,
      -1.7698734200195663
    ],
    [
      0.5472444002563871,
      -3.7762274904324435
    ],
    [
      0.5308758771204678,
      -5.774236843452897
    ],
    [
      0.1343396935576018,
      -7.248946397349508
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.7973562952747055,
      0.0006664584007912035,
      -0.6035084872800023
    ],
    [
      0.6035068638930023,
      0.0016883881508081388,
      0.7973560149515934
    ],
    [
      0.0015503611934215913,
      -0.9999983525879694,
      0.0009440347015374358
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.464102325,
    -0.27645674,
    0.4117777
  ],
  "construction_scale": 69.27515712783314,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
