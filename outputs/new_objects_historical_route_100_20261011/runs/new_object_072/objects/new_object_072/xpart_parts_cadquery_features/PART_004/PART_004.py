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
    0.07880226500645325,
    0.030988141017801542
  ],
  "profile": [
    [
      0.7818684406586875,
      -12.210490267634096
    ],
    [
      2.293308259114835,
      -12.179291331015166
    ],
    [
      3.820648368281602,
      -12.141290823956226
    ],
    [
      5.343546390673765,
      -12.06826218861431
    ],
    [
      6.8544752903621,
      -11.945913307530233
    ],
    [
      8.37023089346603,
      -11.870707441578224
    ],
    [
      9.89222315576868,
      -11.888605188496475
    ],
    [
      11.413634522590186,
      -11.91230361114803
    ],
    [
      12.938130490654343,
      -11.940869793370256
    ],
    [
      14.446300339779988,
      -11.992911115665308
    ],
    [
      15.950183792530819,
      -12.047956355849962
    ],
    [
      17.453188585218584,
      -12.083394087268683
    ],
    [
      18.957189557504,
      -12.105323038136397
    ],
    [
      20.421748871864114,
      -12.225635972782596
    ],
    [
      21.81058457500232,
      -12.77373495140098
    ],
    [
      23.25438044371308,
      -13.479882449482272
    ],
    [
      24.774676681772945,
      -13.896744988952468
    ],
    [
      26.297602078848826,
      -14.11089024640274
    ],
    [
      27.745234760856704,
      -14.290835612090142
    ],
    [
      29.158401721254414,
      -14.493812527878937
    ],
    [
      30.631853014393066,
      -14.739761004622792
    ],
    [
      32.14423730661284,
      -14.716659753507386
    ],
    [
      33.63154950306844,
      -14.395254701339482
    ],
    [
      35.100329287588586,
      -13.94870138869057
    ],
    [
      36.55158414594296,
      -13.497471077982588
    ],
    [
      37.98326300188425,
      -13.010017358123605
    ],
    [
      39.40054200786406,
      -12.447574231090035
    ],
    [
      40.80849416140249,
      -11.815490798332323
    ],
    [
      42.207490414488355,
      -11.174780200344753
    ],
    [
      43.58041801877863,
      -10.485592552632498
    ],
    [
      44.92276381225905,
      -9.748354784912202
    ],
    [
      46.240688889788636,
      -8.970105128698311
    ],
    [
      47.48734001048113,
      -8.128679840223338
    ],
    [
      48.58390891965682,
      -7.12672675067999
    ],
    [
      49.363006523494576,
      -5.845060330837882
    ],
    [
      49.74677584117318,
      -4.404320104401784
    ],
    [
      49.7493825884017,
      -2.8919325985987125
    ],
    [
      49.428745509144456,
      -1.3992022719621255
    ],
    [
      48.84762257491862,
      0.009624320698723127
    ],
    [
      48.122948512980585,
      1.3543530091267977
    ],
    [
      47.935408834331604,
      2.766208669159909
    ],
    [
      48.50095294507348,
      4.14539426444485
    ],
    [
      49.215137623480445,
      5.494753098292457
    ],
    [
      49.66769981838692,
      6.947459727528962
    ],
    [
      49.73703548333718,
      8.460059149773087
    ],
    [
      49.53294855047332,
      9.968775074694884
    ],
    [
      49.139808111716846,
      11.430360821649055
    ],
    [
      48.437266120814435,
      12.743232016955034
    ],
    [
      47.364397657512114,
      13.782391440655545
    ],
    [
      46.0108448466547,
      14.421309580989087
    ],
    [
      44.528048665002224,
      14.710788339867117
    ],
    [
      43.0046802826228,
      14.798063886296475
    ],
    [
      41.476673102198234,
      14.778730402252496
    ],
    [
      39.955052804178145,
      14.666425596616216
    ],
    [
      38.45963558698981,
      14.409493434194497
    ],
    [
      37.01117428107871,
      13.975790713892607
    ],
    [
      35.58782224229445,
      13.424236305203399
    ],
    [
      34.1769644970779,
      12.866927098250384
    ],
    [
      32.75047263335073,
      12.335633260379762
    ],
    [
      31.2921249168308,
      11.853221809444541
    ],
    [
      29.803072314819815,
      11.510656785121412
    ],
    [
      28.28522531477892,
      11.34241214144446
    ],
    [
      26.75879889730139,
      11.270003759478495
    ],
    [
      25.230389374866924,
      11.225608653890287
    ],
    [
      23.701313168245605,
      11.200055414070558
    ],
    [
      22.17225279122612,
      11.206895138507392
    ],
    [
      20.643530639951003,
      11.231323370078126
    ],
    [
      19.114611653845742,
      11.257101434497718
    ],
    [
      17.585945241877365,
      11.275819214414412
    ],
    [
      16.05696760226194,
      11.30279478179656
    ],
    [
      14.52769764359514,
      11.30310018084943
    ],
    [
      12.99856229302316,
      11.310298021208066
    ],
    [
      11.469294371308198,
      11.313847939855847
    ],
    [
      9.940069376875801,
      11.307749733805196
    ],
    [
      8.410765699462212,
      11.312962265544911
    ],
    [
      6.881507041299615,
      11.308492884912837
    ],
    [
      5.352339443167342,
      11.302265260612167
    ],
    [
      3.8232681878586687,
      11.29834502891794
    ],
    [
      2.293985341155865,
      11.299813326219969
    ],
    [
      0.7820862531021209,
      11.305464260224749
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.2845508187171991,
      -0.9586486190446408,
      -0.004863822691528951
    ],
    [
      -0.9585937034531654,
      0.28446709800065817,
      0.013288410553135172
    ],
    [
      -0.011355318899812278,
      0.00844365790915704,
      -0.9998998756744581
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.022816644999999997,
    0.39600755,
    0.0003628249999999989
  ],
  "construction_scale": 492.24817420229704,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
