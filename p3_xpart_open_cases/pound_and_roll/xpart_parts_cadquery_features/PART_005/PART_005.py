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
    -0.47985890808780013,
    0.2398726359909259
  ],
  "profile": [
    [
      0.9961980230606355,
      -50.13908636739882
    ],
    [
      2.9200286939770352,
      -50.06050486936656
    ],
    [
      4.861355993349834,
      -49.91527009670021
    ],
    [
      6.794193584815012,
      -49.6932427584008
    ],
    [
      8.71555161936697,
      -49.37290075186051
    ],
    [
      10.626579525616352,
      -48.9815179017647
    ],
    [
      12.523399811354833,
      -48.49807910752959
    ],
    [
      14.392906894740547,
      -47.920032794608105
    ],
    [
      16.225519561018807,
      -47.2651684222866
    ],
    [
      18.029463688743878,
      -46.554654501793536
    ],
    [
      19.816652069051422,
      -45.765106327704785
    ],
    [
      21.567069756700572,
      -44.91073249152423
    ],
    [
      23.28463003432653,
      -44.019219662691754
    ],
    [
      24.971860297777397,
      -43.065491589443255
    ],
    [
      26.611425162040383,
      -42.02953480021091
    ],
    [
      28.202679726584194,
      -40.89642321134079
    ],
    [
      29.748440820101152,
      -39.70348930479207
    ],
    [
      31.243018592973904,
      -38.45867661307039
    ],
    [
      32.69551422442348,
      -37.1596614796114
    ],
    [
      34.080137041081194,
      -35.800285776745866
    ],
    [
      35.41647971486533,
      -34.390724377902814
    ],
    [
      36.68962667281469,
      -32.92099074240454
    ],
    [
      37.90898092043632,
      -31.395966995565505
    ],
    [
      39.067993215037106,
      -29.83370142486119
    ],
    [
      40.17229287856617,
      -28.2459974742896
    ],
    [
      41.22447106662096,
      -26.618910635106573
    ],
    [
      42.20364217812257,
      -24.934271539210116
    ],
    [
      43.11979924273811,
      -23.197676974866653
    ],
    [
      43.96137932436679,
      -21.429008185830888
    ],
    [
      44.723533608004445,
      -19.648898800138227
    ],
    [
      45.43048701241145,
      -17.836184930751585
    ],
    [
      46.07756063204144,
      -15.989872896818243
    ],
    [
      46.661118289633855,
      -14.125488823196198
    ],
    [
      47.17866570783247,
      -12.238087258421434
    ],
    [
      47.6290691673439,
      -10.334039903504422
    ],
    [
      47.99967859318999,
      -8.42063536689101
    ],
    [
      48.29228994925823,
      -6.493316451867194
    ],
    [
      48.505656723797784,
      -4.558106760507933
    ],
    [
      48.64567062778069,
      -2.615457885002063
    ],
    [
      48.73752912969808,
      -0.6679136643224135
    ],
    [
      48.76514795064075,
      1.2793351753345314
    ],
    [
      48.71394870892174,
      3.2273700211912013
    ],
    [
      48.58701861809135,
      5.174133334336844
    ],
    [
      48.38821103617104,
      7.116140890070609
    ],
    [
      48.146406752581285,
      9.050189421759145
    ],
    [
      47.84400140204427,
      10.97224105482469
    ],
    [
      47.414052426841344,
      12.8751584300627
    ],
    [
      46.924302802939366,
      14.763607144180082
    ],
    [
      46.3726559850755,
      16.638737686120095
    ],
    [
      45.745521527210904,
      18.4950984716726
    ],
    [
      45.057921550042764,
      20.321517051846342
    ],
    [
      44.29153264503492,
      22.117806493065643
    ],
    [
      43.45852037337241,
      23.879066541989186
    ],
    [
      42.561258048477306,
      25.613880030329085
    ],
    [
      41.59734244732712,
      27.305414303537958
    ],
    [
      40.56246517132658,
      28.96037292999781
    ],
    [
      39.47724132263589,
      30.577657985454053
    ],
    [
      38.29732526654071,
      32.11776242694852
    ],
    [
      37.043849307909596,
      33.607903035591804
    ],
    [
      35.74237241794627,
      35.0559640067356
    ],
    [
      34.37949198884142,
      36.43842670022824
    ],
    [
      32.96240174209282,
      37.762347122321174
    ],
    [
      31.514409123346084,
      39.04609306403299
    ],
    [
      29.99405413488617,
      40.26254204931526
    ],
    [
      28.417542571454778,
      41.40703343756762
    ],
    [
      26.79692770470995,
      42.487314793172345
    ],
    [
      25.14105636873841,
      43.493538450710695
    ],
    [
      23.43930027688011,
      44.43029875016953
    ],
    [
      21.692330873965624,
      45.29984719302944
    ],
    [
      19.90735043459796,
      46.09327218075522
    ],
    [
      18.095187222480842,
      46.82581317442856
    ],
    [
      16.25506619777007,
      47.48335740302115
    ],
    [
      14.39585219419531,
      48.06904739454452
    ],
    [
      12.521986664979716,
      48.601776106313295
    ],
    [
      10.628512049214777,
      49.06079859228913
    ],
    [
      8.7185383478499,
      49.44323392084904
    ],
    [
      6.794023523928944,
      49.73735786811005
    ],
    [
      4.860511023281971,
      49.9775844311459
    ],
    [
      2.919624592029877,
      50.1528181633352
    ],
    [
      0.9961553551502467,
      50.24679592724142
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.3036663340221032,
      0.9090620140772349,
      0.28529460587858524
    ],
    [
      0.9459229725270988,
      -0.32350405159894474,
      0.02397620997082125
    ],
    [
      0.11408982262705991,
      0.2625859538530352,
      -0.9581399319577582
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.110433425,
    0.274399785,
    0.55884987
  ],
  "construction_scale": 232.38155117288082,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
