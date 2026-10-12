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
    0.6439915618401366,
    0.10644536503967492
  ],
  "profile": [
    [
      0.18994161846200944,
      -51.41855567462269
    ],
    [
      1.3894235988884698,
      -51.40463082303735
    ],
    [
      2.7769006802785414,
      -51.38013050824787
    ],
    [
      4.0129187388182865,
      -51.098758427620794
    ],
    [
      4.442492917971551,
      -49.91156284730933
    ],
    [
      4.488159630993566,
      -48.5263058119019
    ],
    [
      4.477004053007717,
      -47.139406260670285
    ],
    [
      4.475877347724826,
      -45.75193303608079
    ],
    [
      4.469558452054166,
      -44.36452872839073
    ],
    [
      4.447058134296974,
      -42.97700050270525
    ],
    [
      4.438464728552157,
      -41.589309939886434
    ],
    [
      4.415852244695557,
      -40.201828969231414
    ],
    [
      4.395254383322252,
      -38.81451980126171
    ],
    [
      4.38627770706135,
      -37.42702540867114
    ],
    [
      4.388582581943959,
      -36.03936510154894
    ],
    [
      4.3995420212192595,
      -34.65196135958617
    ],
    [
      4.406763165048634,
      -33.2649789213384
    ],
    [
      4.407931216425837,
      -31.87728040788673
    ],
    [
      4.417508218051281,
      -30.48953734825198
    ],
    [
      4.422603252994065,
      -29.101797153522845
    ],
    [
      4.426954334473045,
      -27.714078982233094
    ],
    [
      4.422363828893849,
      -26.326438128120774
    ],
    [
      4.435129371200119,
      -24.938800085115048
    ],
    [
      4.449800080445073,
      -23.55113591853715
    ],
    [
      4.430759381101823,
      -22.163521040459806
    ],
    [
      4.423125084767685,
      -20.77599803156229
    ],
    [
      4.425537381873374,
      -19.388430271241518
    ],
    [
      4.432737944068246,
      -18.000884384830357
    ],
    [
      4.450173631860855,
      -16.61320978190636
    ],
    [
      4.458939485206833,
      -15.225676910020743
    ],
    [
      4.473197565381892,
      -13.838163779156405
    ],
    [
      4.471910349512559,
      -12.45073622149047
    ],
    [
      4.471479642089103,
      -11.063391101913462
    ],
    [
      4.475504050145471,
      -9.67599057700988
    ],
    [
      4.473283392541005,
      -8.288398563897209
    ],
    [
      4.477457985562151,
      -6.90085105143478
    ],
    [
      4.478406035205756,
      -5.513356149311285
    ],
    [
      4.46716980149861,
      -4.126076665460625
    ],
    [
      4.465427295370374,
      -2.7404495616623663
    ],
    [
      4.456981450662627,
      -1.356308926659093
    ],
    [
      4.43619903539725,
      0.02777855355189765
    ],
    [
      4.4333307805705315,
      1.412027973472247
    ],
    [
      4.449535537624624,
      2.7961928203868816
    ],
    [
      4.474663840597701,
      4.180323975901114
    ],
    [
      4.488266613048909,
      5.5643538011723255
    ],
    [
      4.485724613166491,
      6.948463557788519
    ],
    [
      4.478983130929064,
      8.33242100695202
    ],
    [
      4.47751806561577,
      9.716505468403646
    ],
    [
      4.475067396399794,
      11.100766352191396
    ],
    [
      4.480580277816854,
      12.484932165776087
    ],
    [
      4.4658755377238215,
      13.86905154894917
    ],
    [
      4.4582370561871745,
      15.253159323280222
    ],
    [
      4.450683131473632,
      16.63741581212077
    ],
    [
      4.450297080475478,
      18.022389839932174
    ],
    [
      4.4573117206569295,
      19.409757411340678
    ],
    [
      4.46234012124386,
      20.7975261436942
    ],
    [
      4.466893351555582,
      22.18524920863463
    ],
    [
      4.4619576466324276,
      23.572897230129144
    ],
    [
      4.45972334327653,
      24.960553993025435
    ],
    [
      4.460458849200615,
      26.34565026588838
    ],
    [
      4.464284476395919,
      27.728372616326688
    ],
    [
      4.4714814698534395,
      29.111018685147044
    ],
    [
      4.460923054290811,
      30.49377139915353
    ],
    [
      4.454043757598805,
      31.87631428647476
    ],
    [
      4.451091447294254,
      33.25888868263506
    ],
    [
      4.445467302819173,
      34.64165606013273
    ],
    [
      4.443306015962904,
      36.02454137514847
    ],
    [
      4.441006194375349,
      37.40745194801525
    ],
    [
      4.436510318819676,
      38.79014094465468
    ],
    [
      4.438610400417565,
      40.17279450036037
    ],
    [
      4.437989115331794,
      41.55535726282915
    ],
    [
      4.439572724417914,
      42.93874409801119
    ],
    [
      4.449508243906816,
      44.32337790282185
    ],
    [
      4.455023169668735,
      45.7100852307198
    ],
    [
      4.466117290686848,
      47.097451470153494
    ],
    [
      4.473462457661341,
      48.48844897230593
    ],
    [
      4.328700225187001,
      49.86168046661291
    ],
    [
      3.769189851675104,
      51.10257741901092
    ],
    [
      2.713662532444464,
      51.97732155840455
    ],
    [
      1.3855721186093661,
      52.330380132444034
    ],
    [
      0.18991125948561904,
      52.38329732707034
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.06607179042645119,
      0.9469168448780303,
      0.31461565027200833
    ],
    [
      0.9977832390265478,
      -0.06018886547217172,
      -0.028388525690215112
    ],
    [
      -0.00794521412765567,
      0.3157939032967678,
      -0.9487945426766833
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.89982491,
    0.28843755000000004,
    -0.11848200000000003
  ],
  "construction_scale": 56.71335427197934,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
