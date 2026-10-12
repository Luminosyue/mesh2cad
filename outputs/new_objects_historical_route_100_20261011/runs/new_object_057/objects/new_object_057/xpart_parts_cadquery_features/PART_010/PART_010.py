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
    0.02609450793218131,
    -0.016912582026209284
  ],
  "profile": [
    [
      1.3919988018997949,
      -5.871855053311171
    ],
    [
      2.783420900496969,
      -5.870877429078232
    ],
    [
      4.175161418161188,
      -5.870873777915596
    ],
    [
      5.566918872157608,
      -5.866779705166136
    ],
    [
      6.958645518758311,
      -5.863838197060526
    ],
    [
      8.35039568448419,
      -5.8587177849401595
    ],
    [
      9.742075136529122,
      -5.854311752333064
    ],
    [
      11.13377616535384,
      -5.852531753013219
    ],
    [
      12.52551271266962,
      -5.852061308316209
    ],
    [
      13.917253639880327,
      -5.8504568974155795
    ],
    [
      15.308957449730075,
      -5.849027034084158
    ],
    [
      16.700692600979817,
      -5.847768932968869
    ],
    [
      18.092368284270393,
      -5.847336571377892
    ],
    [
      19.484023557296958,
      -5.846337357897145
    ],
    [
      20.87571849480894,
      -5.847170145278074
    ],
    [
      22.267438663256534,
      -5.846092223430986
    ],
    [
      23.65917364114276,
      -5.8431589493011105
    ],
    [
      25.050931769018725,
      -5.8467896885468775
    ],
    [
      26.442691972367175,
      -5.849790336660367
    ],
    [
      27.834427005442958,
      -5.8546443343905405
    ],
    [
      29.226108320734394,
      -5.86631680299185
    ],
    [
      30.617216634729267,
      -5.876479572048597
    ],
    [
      31.96069976987097,
      -6.052993617298863
    ],
    [
      33.0038484340135,
      -6.869740443779589
    ],
    [
      34.04370044350121,
      -7.734880454764239
    ],
    [
      35.3618183477036,
      -8.023262341958386
    ],
    [
      36.75190446971463,
      -8.050018508386874
    ],
    [
      38.14356313989136,
      -8.04728105420489
    ],
    [
      39.53527102269916,
      -8.045802580368978
    ],
    [
      40.92719448206982,
      -8.037354556263523
    ],
    [
      42.31930929498322,
      -8.031470068612059
    ],
    [
      43.697618558344956,
      -7.920534986834716
    ],
    [
      44.96122602993945,
      -7.402017867521195
    ],
    [
      46.107569828024204,
      -6.611805409776558
    ],
    [
      47.16438160260202,
      -5.713268684869304
    ],
    [
      48.087494589600325,
      -4.669166113215975
    ],
    [
      48.834876816480026,
      -3.494030886741199
    ],
    [
      49.344771941795685,
      -2.2063361795721796
    ],
    [
      49.686331077962706,
      -0.8633280705994923
    ],
    [
      49.91279973779761,
      0.50570955127207
    ],
    [
      50.00124769507596,
      1.8921643082467474
    ],
    [
      49.88042558633708,
      3.273847216547845
    ],
    [
      49.579389142134296,
      4.630007010517266
    ],
    [
      49.14887165544702,
      5.946788299765669
    ],
    [
      48.41800621667694,
      7.108923767430161
    ],
    [
      47.279654853139284,
      7.839512476802884
    ],
    [
      45.926542211641916,
      8.036126662063886
    ],
    [
      44.535964529036214,
      8.024209899246936
    ],
    [
      43.14438948959321,
      8.001726401587767
    ],
    [
      41.75266122545412,
      7.98990312735108
    ],
    [
      40.36092669839617,
      7.982031644374926
    ],
    [
      38.96919615710431,
      7.976649366870016
    ],
    [
      37.5774407248181,
      7.971502962969561
    ],
    [
      36.18567109116513,
      7.966518578577096
    ],
    [
      34.79392988182935,
      7.9615657535776645
    ],
    [
      33.402163490980854,
      7.954741752495318
    ],
    [
      32.010411860668,
      7.950384934967655
    ],
    [
      30.618663021407052,
      7.948847016315124
    ],
    [
      29.226892757906974,
      7.944437124282903
    ],
    [
      27.835127384405833,
      7.940995188690071
    ],
    [
      26.443377849476747,
      7.939633336040008
    ],
    [
      25.051625133668054,
      7.938016065676997
    ],
    [
      23.659862598525343,
      7.936408466104893
    ],
    [
      22.26810042695503,
      7.937183942483832
    ],
    [
      20.876339099842813,
      7.936645226713173
    ],
    [
      19.484573419943388,
      7.936846416945581
    ],
    [
      18.092811213709076,
      7.937448703517957
    ],
    [
      16.701056019189352,
      7.93663473675352
    ],
    [
      15.309312138126417,
      7.936774251703356
    ],
    [
      13.91755531521806,
      7.936867745580702
    ],
    [
      12.525791760850643,
      7.936759320142492
    ],
    [
      11.134038208235005,
      7.936983349525623
    ],
    [
      9.742286053287618,
      7.937539364104632
    ],
    [
      8.350541194119488,
      7.9381049181041945
    ],
    [
      6.95879014848293,
      7.938556786714912
    ],
    [
      5.56702449727732,
      7.939939741032827
    ],
    [
      4.175274253383356,
      7.9395588630061456
    ],
    [
      2.783508487767179,
      7.938714522477874
    ],
    [
      1.3920564507826523,
      7.9384556583390085
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
    -0.305237305,
    -8.573000000000608e-05,
    -1.2590000000006762e-05
  ],
  "construction_scale": 311.5511126705283,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
