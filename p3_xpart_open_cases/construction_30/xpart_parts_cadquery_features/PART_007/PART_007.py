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
    0.46045207190800846,
    -0.052439994173510564
  ],
  "profile": [
    [
      1.3376850742978026,
      14.076464473477479
    ],
    [
      3.7862182411419596,
      14.678736437085465
    ],
    [
      5.844731224917057,
      16.12235369128696
    ],
    [
      7.599281912546143,
      18.20214172905631
    ],
    [
      8.6438575373885,
      20.70186204890628
    ],
    [
      9.488942822107042,
      23.214976648646655
    ],
    [
      11.084952207820328,
      25.19183400193686
    ],
    [
      13.455986970308306,
      26.042434735593133
    ],
    [
      16.080208958312994,
      26.245483912120562
    ],
    [
      18.765850372396876,
      26.183178150483982
    ],
    [
      21.45447382929248,
      26.29092673053788
    ],
    [
      24.142296880540222,
      26.312011943375907
    ],
    [
      26.823388705719175,
      26.26385563781663
    ],
    [
      29.48990315614561,
      26.25407301041642
    ],
    [
      32.15363681315685,
      26.222705296219985
    ],
    [
      34.813711030828046,
      26.178477160632188
    ],
    [
      37.371369907873984,
      26.005499129209994
    ],
    [
      39.71107605613438,
      25.06253363335992
    ],
    [
      41.23200524310275,
      23.183209047618085
    ],
    [
      42.20019767524242,
      20.869243297297068
    ],
    [
      42.78267350468925,
      18.22566513867526
    ],
    [
      43.01273976563097,
      15.53935787869855
    ],
    [
      43.1072345131648,
      12.85381486681587
    ],
    [
      43.12534666827913,
      10.169601634991173
    ],
    [
      43.08245757799867,
      7.48413510775772
    ],
    [
      43.00418457233691,
      4.796589034707211
    ],
    [
      43.01932901275911,
      2.109465286474622
    ],
    [
      42.99870809928341,
      -0.576350158345028
    ],
    [
      42.99761010251375,
      -3.261308515241926
    ],
    [
      43.05472384081055,
      -5.949076033480778
    ],
    [
      43.02568720243754,
      -8.636999015298109
    ],
    [
      42.974628909249205,
      -11.324936277593242
    ],
    [
      42.98141408761421,
      -14.013237395642657
    ],
    [
      43.00442538335517,
      -16.701360837302687
    ],
    [
      43.03081442484185,
      -19.389562258311983
    ],
    [
      43.07235172237438,
      -22.07782144720656
    ],
    [
      43.139845431923185,
      -24.76665237951931
    ],
    [
      43.28194164746134,
      -27.43933823042039
    ],
    [
      44.27725251481063,
      -29.51833247204292
    ],
    [
      46.138902513332496,
      -28.919469461884105
    ],
    [
      46.96087681718565,
      -26.51539952194556
    ],
    [
      46.95784220362897,
      -23.953676052905912
    ],
    [
      46.91675071764054,
      -21.40220604319253
    ],
    [
      46.88227555053541,
      -18.75998448860994
    ],
    [
      46.85471987997026,
      -16.095097147467637
    ],
    [
      46.81835154720302,
      -13.42993232290301
    ],
    [
      46.824607440614926,
      -10.761292865566206
    ],
    [
      46.880511463337335,
      -8.079876478303644
    ],
    [
      46.90416923290072,
      -5.392403647961547
    ],
    [
      46.8831341309671,
      -2.7048705273672535
    ],
    [
      46.91557097588101,
      -0.017788854582054255
    ],
    [
      46.89766101164505,
      2.669413896186388
    ],
    [
      46.89896315830583,
      5.356113327816315
    ],
    [
      46.907002372849874,
      8.042202348877069
    ],
    [
      46.90512810474221,
      10.727937740791809
    ],
    [
      46.87467770103612,
      13.412297990862278
    ],
    [
      46.79692510867903,
      16.098308483733845
    ],
    [
      46.62054700013154,
      18.78458360744707
    ],
    [
      46.13904549016862,
      21.44264207976899
    ],
    [
      45.25603994377889,
      23.985736750502376
    ],
    [
      44.05480061787455,
      26.34974020652858
    ],
    [
      42.132560333679876,
      28.25572372551617
    ],
    [
      39.94463084222299,
      29.48198156798958
    ],
    [
      37.489475850990885,
      29.90292319152464
    ],
    [
      34.93312706490147,
      30.020195493502708
    ],
    [
      32.35470507484828,
      30.065935258850597
    ],
    [
      29.6911636588175,
      30.100958728114218
    ],
    [
      27.026286802862614,
      30.125036219828125
    ],
    [
      24.36162373430214,
      30.171074468007888
    ],
    [
      21.697454015262725,
      30.21716193240343
    ],
    [
      19.033556522888887,
      30.227862388908008
    ],
    [
      16.36794080980188,
      30.143006775388912
    ],
    [
      13.702899129684155,
      30.176927483137394
    ],
    [
      11.058380367418788,
      30.004206169107228
    ],
    [
      8.48640635440136,
      29.24289752950744
    ],
    [
      6.178858475781196,
      27.921780740574714
    ],
    [
      4.553158287341764,
      25.82209064684684
    ],
    [
      3.717796465622193,
      23.232679773211963
    ],
    [
      2.920673936996692,
      20.712104983776868
    ],
    [
      1.1740023675913855,
      19.187661614868354
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.20676770260565244,
      0.9755129126069311,
      -0.0749778266977853
    ],
    [
      -0.9783467271890505,
      0.20687180782469464,
      -0.006460381243939514
    ],
    [
      0.009208613231910873,
      0.074690109549292,
      0.9971642738174387
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.09253507999999999,
    0.397099035,
    0.196214825
  ],
  "construction_scale": 398.4082633698542,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
