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
    -0.026194475342230145,
    0.07092542231332326
  ],
  "profile": [
    [
      1.0953085696535032,
      -49.92394092154244
    ],
    [
      3.212576255528493,
      -49.91716936992225
    ],
    [
      5.354199901157012,
      -49.912030559826746
    ],
    [
      7.495936023400445,
      -49.906832481640336
    ],
    [
      9.637696821232847,
      -49.904535183853255
    ],
    [
      11.779505913742938,
      -49.899280810450875
    ],
    [
      13.921300911935143,
      -49.89765513152882
    ],
    [
      16.06309051143474,
      -49.90108424310658
    ],
    [
      18.20482632600637,
      -49.89804344491229
    ],
    [
      20.346278945021513,
      -49.881597755673425
    ],
    [
      22.485416209028692,
      -49.81181195973022
    ],
    [
      24.584118815598792,
      -49.509503010549395
    ],
    [
      26.587905866427537,
      -48.816297897549624
    ],
    [
      28.444095323474023,
      -47.83316284117474
    ],
    [
      30.310585271607955,
      -46.65236212491998
    ],
    [
      31.82110549653071,
      -45.22259101271741
    ],
    [
      32.79107869387599,
      -43.43502160460923
    ],
    [
      33.0807309877325,
      -41.361322318099184
    ],
    [
      33.01387722304014,
      -39.45411482312942
    ],
    [
      32.55882364129293,
      -37.469617868041766
    ],
    [
      32.19415125455215,
      -35.4885295317881
    ],
    [
      32.198158278697754,
      -33.69779029023877
    ],
    [
      32.43437204774847,
      -32.08533347870768
    ],
    [
      32.93668096079,
      -30.245983917994856
    ],
    [
      33.1342859329766,
      -28.264488467451677
    ],
    [
      33.10309858561541,
      -26.29176738904477
    ],
    [
      32.775340975694675,
      -24.630573736726998
    ],
    [
      32.663273694076665,
      -23.061219495311224
    ],
    [
      32.0539435688584,
      -21.278330741571992
    ],
    [
      31.775101642091997,
      -19.37382055866634
    ],
    [
      32.54238681362904,
      -17.33749548652251
    ],
    [
      33.03770509935534,
      -15.283157327320623
    ],
    [
      33.082544778918646,
      -13.332294371772337
    ],
    [
      32.889293957391956,
      -11.470454772514756
    ],
    [
      32.459631465059886,
      -9.813785327783616
    ],
    [
      32.28807992943584,
      -8.016157610606092
    ],
    [
      32.214613325211246,
      -6.312556237307186
    ],
    [
      32.614738787087425,
      -4.58887748348365
    ],
    [
      32.95999395422922,
      -2.5271443415046635
    ],
    [
      33.131448243305776,
      -0.7345715179164508
    ],
    [
      32.925635138319876,
      1.156120252635728
    ],
    [
      32.61925765287778,
      2.9915495525187543
    ],
    [
      32.466473902462425,
      4.516690925593363
    ],
    [
      32.196080611792496,
      6.4477853821049536
    ],
    [
      32.421506008018184,
      8.431865080211676
    ],
    [
      32.80580923735368,
      10.448578638775157
    ],
    [
      33.06656527093206,
      12.228164188418372
    ],
    [
      33.059730482953874,
      13.978846437901701
    ],
    [
      32.90595820101379,
      15.798655639939467
    ],
    [
      32.53720976577035,
      17.693757676836448
    ],
    [
      32.06210678375834,
      19.697712825292882
    ],
    [
      31.940766317266394,
      21.579041152220142
    ],
    [
      32.451013823994586,
      23.574367819291965
    ],
    [
      32.921207059277265,
      25.444523883451232
    ],
    [
      33.08128310824881,
      27.086194085136256
    ],
    [
      33.038972596412506,
      28.709613126080328
    ],
    [
      32.56126217291253,
      30.263197479611712
    ],
    [
      32.158671704481556,
      31.83714929721009
    ],
    [
      32.110150543609166,
      33.772600453226794
    ],
    [
      32.331286992738434,
      35.66495193493344
    ],
    [
      32.68424334892487,
      37.59973186303557
    ],
    [
      32.95629917207622,
      39.55052340908536
    ],
    [
      32.91652986349856,
      41.62303351401765
    ],
    [
      32.58114512648779,
      43.71576416297356
    ],
    [
      31.881776803822962,
      45.75816935389943
    ],
    [
      30.675961121391442,
      47.38849389835862
    ],
    [
      28.827936691077603,
      48.40173882428596
    ],
    [
      26.733874157093616,
      48.85605363388366
    ],
    [
      24.60564526326275,
      49.200478184615285
    ],
    [
      22.47840344933674,
      49.48499271071998
    ],
    [
      20.344095185896514,
      49.67948781101552
    ],
    [
      18.204115877749256,
      49.788311684966224
    ],
    [
      16.062571515786757,
      49.84325178994313
    ],
    [
      13.921024314570865,
      49.87911818588842
    ],
    [
      11.779711603859198,
      49.913392181960404
    ],
    [
      9.63800684112528,
      49.93726379772042
    ],
    [
      7.496247946142496,
      49.954560742908185
    ],
    [
      5.354466822355903,
      49.96697312385943
    ],
    [
      3.212681305696198,
      49.97749440137886
    ],
    [
      1.0953169355434813,
      49.98215284062971
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
    -0.43231522499999997,
    6.766500000000147e-05,
    -3.660999999999942e-05
  ],
  "construction_scale": 734.6906449121831,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
