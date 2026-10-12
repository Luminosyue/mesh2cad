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
    -0.10083092901429458,
    -0.4273425051890493
  ],
  "profile": [
    [
      1.7332216106651637,
      43.4209257137432
    ],
    [
      5.083926674870458,
      43.43480847171778
    ],
    [
      8.473141331271583,
      43.43590345980317
    ],
    [
      11.862364415686278,
      43.426257250851975
    ],
    [
      15.251630561319441,
      43.4212031913344
    ],
    [
      18.64086007481869,
      43.38990580252597
    ],
    [
      22.030047192380586,
      43.35995431338998
    ],
    [
      25.41899921345673,
      43.32813338884402
    ],
    [
      28.806397635577866,
      43.19647906456544
    ],
    [
      32.159064057735776,
      42.8260484067046
    ],
    [
      35.26896086868931,
      41.62680299927689
    ],
    [
      37.628468924568296,
      39.232655951806734
    ],
    [
      38.960650120232955,
      36.17594205735389
    ],
    [
      39.42942613652585,
      32.84756635235664
    ],
    [
      39.46549916323163,
      29.464359163613906
    ],
    [
      39.440001069050666,
      26.07953745364547
    ],
    [
      39.43036393712603,
      22.692264972012623
    ],
    [
      39.40816608990478,
      19.30191260351284
    ],
    [
      39.40662371983052,
      15.911817610586862
    ],
    [
      39.42956332882911,
      12.52154016209596
    ],
    [
      39.46343859085637,
      9.13133433452809
    ],
    [
      39.48067550818093,
      5.740792584628558
    ],
    [
      39.44153642255711,
      2.3504366130137058
    ],
    [
      39.39527062857536,
      -1.0394356201798214
    ],
    [
      39.377346475079534,
      -4.426845446540813
    ],
    [
      39.33894120791008,
      -7.813068891401121
    ],
    [
      39.29335824383214,
      -11.200186487292452
    ],
    [
      39.28561906690584,
      -14.585534540148512
    ],
    [
      39.306771171111905,
      -17.959800373411827
    ],
    [
      39.27485525747794,
      -21.328696723754597
    ],
    [
      39.1348771617523,
      -24.700930196052933
    ],
    [
      38.994413230514475,
      -28.07477377810757
    ],
    [
      39.11401102053911,
      -31.44152528944104
    ],
    [
      39.472390863778124,
      -34.78219899876443
    ],
    [
      39.70085791050902,
      -38.15623998349085
    ],
    [
      39.78397343741013,
      -41.541256327405
    ],
    [
      39.96123199058418,
      -44.90905036248692
    ],
    [
      41.08843109926633,
      -47.96801822455057
    ],
    [
      43.70427115920603,
      -49.225610721833306
    ],
    [
      46.08341679563512,
      -47.35898329164448
    ],
    [
      47.03654917973506,
      -44.21766303655598
    ],
    [
      47.12749582695473,
      -40.830667349691424
    ],
    [
      47.1231430086343,
      -37.431654343701965
    ],
    [
      47.14829999247673,
      -34.03234666000402
    ],
    [
      47.20314538223176,
      -30.63353555689607
    ],
    [
      47.233250321487446,
      -27.238918924420194
    ],
    [
      47.24980336071878,
      -23.856634882349837
    ],
    [
      47.353606425783084,
      -20.470124025844353
    ],
    [
      47.53637716673775,
      -17.07985632911488
    ],
    [
      47.669372462326805,
      -13.695830478078744
    ],
    [
      47.941094869180134,
      -10.33192420925698
    ],
    [
      48.05796900764959,
      -6.957923482823121
    ],
    [
      47.8113970203938,
      -3.5827313718083245
    ],
    [
      47.71360718573435,
      -0.20349429246841708
    ],
    [
      47.63779204750503,
      3.1779253700083885
    ],
    [
      47.43596792715176,
      6.565503506163353
    ],
    [
      47.374440038300506,
      9.954496155666385
    ],
    [
      47.38721738229768,
      13.339950964325567
    ],
    [
      47.361527287131004,
      16.725806934534734
    ],
    [
      47.345802813421415,
      20.111773563760103
    ],
    [
      47.27824925417556,
      23.49710666682084
    ],
    [
      47.210865198619935,
      26.881419584906894
    ],
    [
      47.18871520891028,
      30.262992518872526
    ],
    [
      47.06738570777904,
      33.62966763201818
    ],
    [
      46.428792426077806,
      36.935602595788296
    ],
    [
      45.27619739335107,
      40.07696924134124
    ],
    [
      43.60080180182365,
      42.980474959537034
    ],
    [
      41.303207596330324,
      45.47450357305864
    ],
    [
      38.55229832237663,
      47.47315795409816
    ],
    [
      35.49915358537157,
      48.862827015310295
    ],
    [
      32.19210139854604,
      49.48964691844539
    ],
    [
      28.808304003482895,
      49.6991116683831
    ],
    [
      25.419652266815042,
      49.7158646387098
    ],
    [
      22.030451512582083,
      49.7113540485508
    ],
    [
      18.641163460591144,
      49.70402967325951
    ],
    [
      15.251840523443839,
      49.70573696229975
    ],
    [
      11.86252396041543,
      49.70724592342809
    ],
    [
      8.473387812852195,
      49.703814483307035
    ],
    [
      5.084067959311591,
      49.70371126233542
    ],
    [
      1.7333198268518122,
      49.69545106326296
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
    0.038450675,
    -0.6251152200000001,
    0.41651669999999996
  ],
  "construction_scale": 481.1012831740985,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
