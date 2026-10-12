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
    -0.23522715795447682,
    0.04279135219030426
  ],
  "profile": [
    [
      1.0031825600904734,
      -50.09136172121171
    ],
    [
      2.940326110896799,
      -49.98571586346142
    ],
    [
      4.895206736856368,
      -49.83393541028887
    ],
    [
      6.843486173872888,
      -49.573714613443784
    ],
    [
      8.775279174648487,
      -49.227587933045115
    ],
    [
      10.6910389213527,
      -48.801173662497305
    ],
    [
      12.586569532257577,
      -48.323955180456615
    ],
    [
      14.472999438229973,
      -47.79222071733696
    ],
    [
      16.33231577972929,
      -47.190084061488406
    ],
    [
      18.169429858498596,
      -46.50493552415118
    ],
    [
      19.994588392051593,
      -45.77716688432977
    ],
    [
      21.770837871967153,
      -44.96239273224067
    ],
    [
      23.514184418280664,
      -44.082949325368006
    ],
    [
      25.233605562440417,
      -43.140073151336594
    ],
    [
      26.903154470026927,
      -42.12660739046711
    ],
    [
      28.519643521522084,
      -41.01529391008829
    ],
    [
      30.088510433890644,
      -39.84130281963204
    ],
    [
      31.621840093048807,
      -38.5953610429697
    ],
    [
      33.10736316157924,
      -37.29629978352903
    ],
    [
      34.52778360034573,
      -35.94299489698625
    ],
    [
      35.901268987572166,
      -34.54027267723208
    ],
    [
      37.22175159768588,
      -33.10496835346658
    ],
    [
      38.504491948751316,
      -31.616774959172453
    ],
    [
      39.71934976864867,
      -30.03901740269402
    ],
    [
      40.84175077074664,
      -28.441537471330093
    ],
    [
      41.900053754344185,
      -26.815023154011
    ],
    [
      42.894061463336215,
      -25.119383383799537
    ],
    [
      43.801359117954604,
      -23.37133189295576
    ],
    [
      44.63445632577518,
      -21.591821059445735
    ],
    [
      45.41101620414801,
      -19.78964252341961
    ],
    [
      46.1576984899917,
      -17.983544594903954
    ],
    [
      46.81526045092011,
      -16.137301133537235
    ],
    [
      47.4018977877064,
      -14.259331505351462
    ],
    [
      47.89591613973903,
      -12.366019246937078
    ],
    [
      48.31715918133648,
      -10.447691112607277
    ],
    [
      48.65518593491467,
      -8.5134901835699
    ],
    [
      48.93433720844696,
      -6.564427702976919
    ],
    [
      49.17910533384446,
      -4.6109604036930145
    ],
    [
      49.32946725711339,
      -2.654096738097058
    ],
    [
      49.38594135125547,
      -0.694618576765442
    ],
    [
      49.391874216675525,
      1.267317178369936
    ],
    [
      49.363842791410605,
      3.2273541154848133
    ],
    [
      49.26755479457735,
      5.181874725411106
    ],
    [
      49.047553080136545,
      7.128422273325118
    ],
    [
      48.72584393172737,
      9.058858710633874
    ],
    [
      48.33400567460893,
      10.983251068129736
    ],
    [
      47.8876962309293,
      12.900864583939327
    ],
    [
      47.37963784132288,
      14.796109388706613
    ],
    [
      46.77721790147788,
      16.681759436090893
    ],
    [
      46.10395413882292,
      18.538117701830338
    ],
    [
      45.34945228704806,
      20.35824237469742
    ],
    [
      44.5521465507521,
      22.142492329584975
    ],
    [
      43.67505987206997,
      23.89115020962629
    ],
    [
      42.73068749981698,
      25.592701895207135
    ],
    [
      41.70774144586359,
      27.265418689224923
    ],
    [
      40.63354575638684,
      28.903342980527192
    ],
    [
      39.502304639264906,
      30.505248105774456
    ],
    [
      38.31460877592945,
      32.056255387680636
    ],
    [
      37.020436655922694,
      33.55896255580694
    ],
    [
      35.691396120563084,
      35.03053409767358
    ],
    [
      34.31984858449324,
      36.433305367920475
    ],
    [
      32.89535181766619,
      37.78581573908633
    ],
    [
      31.41377668493077,
      39.08040741694979
    ],
    [
      29.893685104807915,
      40.307571727788506
    ],
    [
      28.307558614806133,
      41.46450547915205
    ],
    [
      26.686456067764958,
      42.56918356699083
    ],
    [
      25.050459203725964,
      43.660379692697255
    ],
    [
      23.385382747261836,
      44.69288983494481
    ],
    [
      21.672245094254023,
      45.63947052576887
    ],
    [
      19.922052965884433,
      46.51680107123036
    ],
    [
      18.137767563091842,
      47.368911696450155
    ],
    [
      16.322981005374704,
      48.12670347100706
    ],
    [
      14.470842606463593,
      48.795794700329566
    ],
    [
      12.59543632877549,
      49.36917636840917
    ],
    [
      10.702873292527883,
      49.879694175184866
    ],
    [
      8.785733909183204,
      50.29457553715411
    ],
    [
      6.849731332878141,
      50.615829800440125
    ],
    [
      4.897522921036716,
      50.82124106293671
    ],
    [
      2.940794751907136,
      50.93849362644055
    ],
    [
      1.0036309120901226,
      51.010857950241274
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.6113956439474625,
      -0.5217259291157851,
      0.5949768242968283
    ],
    [
      -0.15223306411969348,
      0.6602830505254264,
      0.7354259904147846
    ],
    [
      -0.7765439206836902,
      -0.5402113920282584,
      0.324270244043598
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.40744475999999996,
    0.36321717,
    -0.37772445
  ],
  "construction_scale": 651.2255870180004,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
