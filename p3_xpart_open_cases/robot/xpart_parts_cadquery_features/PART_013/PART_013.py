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
    -0.06692668940473942,
    0.4522579611156738
  ],
  "profile": [
    [
      0.8464341093568706,
      -20.92727244391037
    ],
    [
      2.4828507215716726,
      -20.947668913306025
    ],
    [
      4.138386617700352,
      -20.94753372759976
    ],
    [
      5.793855045751628,
      -20.949829739273
    ],
    [
      7.4489516984401805,
      -20.98186422928177
    ],
    [
      9.103706641208984,
      -21.04036661546483
    ],
    [
      10.758306292613366,
      -21.082117227989237
    ],
    [
      12.412325093297056,
      -21.141203274955526
    ],
    [
      14.066440947509903,
      -21.18270410322758
    ],
    [
      15.720758110542219,
      -21.20504564900486
    ],
    [
      17.375877469498246,
      -21.220734515273612
    ],
    [
      19.03078772298756,
      -21.243271511268826
    ],
    [
      20.68467709798473,
      -21.280783310079528
    ],
    [
      22.33537797513749,
      -21.357690764412368
    ],
    [
      23.981488331562872,
      -21.428910703589665
    ],
    [
      25.634316602774703,
      -21.452505041734902
    ],
    [
      27.28893622400743,
      -21.46216037644305
    ],
    [
      28.942556124629917,
      -21.501186488877167
    ],
    [
      30.59598164020413,
      -21.55025640160568
    ],
    [
      32.249199083085436,
      -21.625420649795927
    ],
    [
      33.90221966190008,
      -21.663288644364005
    ],
    [
      35.55580633696563,
      -21.69313515978626
    ],
    [
      37.20966335709417,
      -21.72231692887967
    ],
    [
      38.86403821470108,
      -21.778410923632844
    ],
    [
      40.51858606983863,
      -21.82612154432814
    ],
    [
      42.172844335521006,
      -21.830788233238863
    ],
    [
      43.81432980319275,
      -21.679523362169622
    ],
    [
      45.36273365621026,
      -21.188374938816686
    ],
    [
      46.71436464143326,
      -20.23779679089887
    ],
    [
      47.79470132179898,
      -18.96282506807882
    ],
    [
      48.58712685443149,
      -17.501305741612857
    ],
    [
      49.047697113106004,
      -15.920201999664053
    ],
    [
      49.27731504723495,
      -14.287462372449216
    ],
    [
      49.36618158507283,
      -12.635499938543479
    ],
    [
      49.405630671844776,
      -10.97884594568027
    ],
    [
      49.40123401744377,
      -9.321944794420808
    ],
    [
      49.38578694424545,
      -7.664953008617843
    ],
    [
      49.384981669545084,
      -6.007907045050222
    ],
    [
      49.38342635844333,
      -4.350958639126519
    ],
    [
      49.37312395164879,
      -2.694212578085692
    ],
    [
      49.38697043738016,
      -1.0385762869077895
    ],
    [
      49.392815524938754,
      0.6157566460748608
    ],
    [
      49.38925558695962,
      2.2702901165847393
    ],
    [
      49.34455473532516,
      3.9235387760262004
    ],
    [
      49.20075718987452,
      5.566119174192742
    ],
    [
      48.93172785338798,
      7.1880546777043905
    ],
    [
      48.55797669937431,
      8.798867566668347
    ],
    [
      48.0576732100766,
      10.390667932581868
    ],
    [
      47.46846113471656,
      11.939873943958816
    ],
    [
      46.74586496051185,
      13.41762782814424
    ],
    [
      45.90713802964382,
      14.819646734653041
    ],
    [
      44.94887522154439,
      16.148488100755127
    ],
    [
      43.85678619712303,
      17.402717859119562
    ],
    [
      42.6440338255207,
      18.574214201675343
    ],
    [
      41.356638673739056,
      19.634878784840517
    ],
    [
      39.99745462169055,
      20.552031327880798
    ],
    [
      38.56787640259334,
      21.34403695963771
    ],
    [
      37.06710112244492,
      22.04779717666944
    ],
    [
      35.502707922656796,
      22.592270396865622
    ],
    [
      33.89300200973711,
      23.01180860260492
    ],
    [
      32.25978992793873,
      23.276995705651657
    ],
    [
      30.614501222907723,
      23.437090431364958
    ],
    [
      28.96501908320534,
      23.54934146783716
    ],
    [
      27.312873926055502,
      23.620407522683113
    ],
    [
      25.65896379962861,
      23.669862931796413
    ],
    [
      24.004130965700796,
      23.700174038350603
    ],
    [
      22.3490933796233,
      23.713882998386907
    ],
    [
      20.6935902220824,
      23.714946648655037
    ],
    [
      19.03797590933368,
      23.70162237154271
    ],
    [
      17.382407871594193,
      23.683801810960134
    ],
    [
      15.727030146782598,
      23.663494947874383
    ],
    [
      14.071640841794444,
      23.65876643600771
    ],
    [
      12.416132363166827,
      23.648116927787136
    ],
    [
      10.760802425055482,
      23.63915860704293
    ],
    [
      9.10535696631786,
      23.626816711865764
    ],
    [
      7.449806274851919,
      23.61495043380389
    ],
    [
      5.794287407340478,
      23.605482443183035
    ],
    [
      4.138763304440897,
      23.598728357552886
    ],
    [
      2.483298740132706,
      23.5945117806399
    ],
    [
      0.8466893810124747,
      23.590312666943472
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.9231615439679951,
      -0.024130715171427296,
      0.38365410505290165
    ],
    [
      -0.3837459021899911,
      0.11658665582582532,
      -0.9160494715001697
    ],
    [
      -0.022624020222260583,
      -0.992887335133582,
      -0.11688838026218329
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.017810640000000003,
    -0.374699755,
    -0.3240245
  ],
  "construction_scale": 388.2607649373816,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
