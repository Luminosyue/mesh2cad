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
    -0.019207031182628773,
    -0.00930048449209901
  ],
  "profile": [
    [
      1.4304238835637264,
      -10.42293393514459
    ],
    [
      2.8602818412839177,
      -10.422616951876483
    ],
    [
      4.2905101960853,
      -10.421717418489752
    ],
    [
      5.720706802282544,
      -10.422373226488103
    ],
    [
      7.150964230328766,
      -10.420575748659452
    ],
    [
      8.581204732528711,
      -10.419852695215386
    ],
    [
      10.011460576375207,
      -10.419446832009765
    ],
    [
      11.441691038866775,
      -10.418468351449793
    ],
    [
      12.87189402389977,
      -10.416707497728783
    ],
    [
      14.302149975682854,
      -10.41765518932202
    ],
    [
      15.732405956698418,
      -10.415711259226603
    ],
    [
      17.162627800956354,
      -10.416637777389486
    ],
    [
      18.592844399076398,
      -10.418399797105769
    ],
    [
      20.023072607097017,
      -10.417813318575085
    ],
    [
      21.453332811776818,
      -10.416527168811164
    ],
    [
      22.883584170112428,
      -10.41527748745932
    ],
    [
      24.31381031207635,
      -10.415616477628905
    ],
    [
      25.744016366715293,
      -10.413944839862292
    ],
    [
      27.17424508065944,
      -10.414929136731697
    ],
    [
      28.604475887765098,
      -10.41431344072371
    ],
    [
      30.034648267746533,
      -10.413737738389067
    ],
    [
      31.46483786843642,
      -10.412503814242827
    ],
    [
      32.89505310092267,
      -10.410888108240915
    ],
    [
      34.325271384039084,
      -10.410258162581314
    ],
    [
      35.75546357563897,
      -10.408521219729002
    ],
    [
      37.18569378787586,
      -10.407730155036987
    ],
    [
      38.615957785505536,
      -10.405977634720216
    ],
    [
      40.046166185119574,
      -10.406262090610479
    ],
    [
      41.47636195261507,
      -10.403683893846356
    ],
    [
      42.9056123891347,
      -10.393396325833208
    ],
    [
      44.28569462638312,
      -10.159321853362279
    ],
    [
      45.50003245633109,
      -9.430041919827264
    ],
    [
      46.62490488917233,
      -8.553007071205148
    ],
    [
      47.60326331551701,
      -7.527130410579808
    ],
    [
      48.398569908865696,
      -6.347934903246845
    ],
    [
      49.046974163865215,
      -5.0660417245705
    ],
    [
      49.485394349989704,
      -3.708768072686405
    ],
    [
      49.8035405339905,
      -2.3122551069838897
    ],
    [
      49.96321326035951,
      -0.8933629790421288
    ],
    [
      49.94823742982631,
      0.5353162526349583
    ],
    [
      49.827626159437685,
      1.9559024041534747
    ],
    [
      49.531836936688464,
      3.356111317175927
    ],
    [
      49.12439937483463,
      4.726539894177948
    ],
    [
      48.53852087613099,
      6.023359888317154
    ],
    [
      47.75492120635464,
      7.205827912385478
    ],
    [
      46.80850082263318,
      8.273732400173403
    ],
    [
      45.718372060759464,
      9.197422585439762
    ],
    [
      44.54980605802582,
      9.98704092631083
    ],
    [
      43.19773283683173,
      10.335574804346571
    ],
    [
      41.770428444258414,
      10.366899731900084
    ],
    [
      40.33999472209743,
      10.377601768984007
    ],
    [
      38.90904516670163,
      10.38136791011404
    ],
    [
      37.47812898980625,
      10.38013935691227
    ],
    [
      36.04786783832873,
      10.374796973090493
    ],
    [
      34.64916498135118,
      10.193828720542724
    ],
    [
      33.600742776602154,
      9.37245607463814
    ],
    [
      32.7970317809239,
      8.310950401048357
    ],
    [
      31.46343706477905,
      8.06573049913571
    ],
    [
      30.033855692566945,
      8.058261156250941
    ],
    [
      28.603689015705307,
      8.061910170218214
    ],
    [
      27.17358913945737,
      8.067745678701796
    ],
    [
      25.743408752104628,
      8.074729384506693
    ],
    [
      24.313228762401987,
      8.08024955771535
    ],
    [
      22.88309362038181,
      8.081893905739133
    ],
    [
      21.45287576650891,
      8.084657238798867
    ],
    [
      20.02262804203199,
      8.085102707876754
    ],
    [
      18.59243183405716,
      8.089954172564571
    ],
    [
      17.16232061915776,
      8.091801317047445
    ],
    [
      15.732093839194032,
      8.093706165973556
    ],
    [
      14.301830696129738,
      8.095213863544355
    ],
    [
      12.87166285427918,
      8.095773220141774
    ],
    [
      11.441493244433556,
      8.095543270609134
    ],
    [
      10.011331891879525,
      8.09523937010814
    ],
    [
      8.581182149206617,
      8.097447046477741
    ],
    [
      7.151074566433341,
      8.09744921951025
    ],
    [
      5.72088920891702,
      8.09639210827389
    ],
    [
      4.290659703506389,
      8.097129740069377
    ],
    [
      2.8604595658478367,
      8.0954613932183
    ],
    [
      1.4305494237576144,
      8.093328338711263
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "axis_candidate": 2,
  "center": [
    -0.23332659500000003,
    0.00011780000000000124,
    2.4455000000006555e-05
  ],
  "construction_scale": 243.22827550106788,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
