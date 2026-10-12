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
    -0.04661366081924209,
    0.005724706416135003
  ],
  "profile": [
    [
      0.18351347723154998,
      -49.98681278729926
    ],
    [
      1.3425124271712496,
      -49.9852700719552
    ],
    [
      2.681097320812888,
      -49.974421585701165
    ],
    [
      3.761604237666992,
      -49.55861337677856
    ],
    [
      3.966763769937195,
      -48.331674453101385
    ],
    [
      3.9496428685560403,
      -46.99128617692743
    ],
    [
      3.9389363203126133,
      -45.65065578262289
    ],
    [
      3.9402371047441314,
      -44.3079934987103
    ],
    [
      3.9415262324769715,
      -42.96542297921843
    ],
    [
      3.9426150613226145,
      -41.62362041532546
    ],
    [
      3.94024772216535,
      -40.28197634980883
    ],
    [
      3.9403153587872057,
      -38.940143727583575
    ],
    [
      3.9400435203460558,
      -37.59797212363466
    ],
    [
      3.9322548774283996,
      -36.25579958891559
    ],
    [
      3.921224494926433,
      -34.9142049220855
    ],
    [
      3.9199671427156684,
      -33.57307687594405
    ],
    [
      3.920639765568158,
      -32.23197901034144
    ],
    [
      3.922344443949709,
      -30.890943209002188
    ],
    [
      3.9213210413725816,
      -29.54991405134841
    ],
    [
      3.9201886368192733,
      -28.20885171912162
    ],
    [
      3.9160981735055547,
      -26.86708723361176
    ],
    [
      3.9134820655939815,
      -25.524127942891006
    ],
    [
      3.9096904910644907,
      -24.181061503953032
    ],
    [
      3.9074596960754704,
      -22.837940259825082
    ],
    [
      3.9053536515372733,
      -21.494858210450786
    ],
    [
      3.902130207299239,
      -20.153100197658212
    ],
    [
      3.8929030707727392,
      -18.815431478284424
    ],
    [
      3.8917710802875796,
      -17.475699213830048
    ],
    [
      3.8888312334348214,
      -16.134865094098338
    ],
    [
      3.891662341256129,
      -14.793882379453153
    ],
    [
      3.8910757521070165,
      -13.452139523304993
    ],
    [
      3.8970878393990978,
      -12.109665508026595
    ],
    [
      3.895751659494599,
      -10.767195454852269
    ],
    [
      3.8921770234838418,
      -9.425213283624217
    ],
    [
      3.8897652527014177,
      -8.086758758787246
    ],
    [
      3.885817090409675,
      -6.745488700342075
    ],
    [
      3.8833036971166024,
      -5.403119417564325
    ],
    [
      3.881244934427099,
      -4.060734731981444
    ],
    [
      3.8755645010986894,
      -2.719266729882112
    ],
    [
      3.868643074253521,
      -1.3805546182936612
    ],
    [
      3.8686730577879618,
      -0.044703800951012874
    ],
    [
      3.8752408674428604,
      1.2941382817373157
    ],
    [
      3.8906894559682046,
      2.6340326051096676
    ],
    [
      3.8986016755918165,
      3.9741640862897087
    ],
    [
      3.9082515941038105,
      5.314200732713436
    ],
    [
      3.910980879399909,
      6.654152379584893
    ],
    [
      3.897927341980119,
      7.994732671328056
    ],
    [
      3.8814494356245577,
      9.336425469571893
    ],
    [
      3.8753087387673677,
      10.678257420591116
    ],
    [
      3.8758558722044567,
      12.020045524131472
    ],
    [
      3.877840266832382,
      13.361852110036004
    ],
    [
      3.8823357444074045,
      14.703695258726075
    ],
    [
      3.8825874655604604,
      16.045529012886778
    ],
    [
      3.8745821126589197,
      17.387294887614487
    ],
    [
      3.8667194943420875,
      18.729044940084474
    ],
    [
      3.870901529429846,
      20.070785920567882
    ],
    [
      3.874049014001497,
      21.412586844828944
    ],
    [
      3.8725326461515124,
      22.75438318194919
    ],
    [
      3.8910618385595748,
      24.09677077098521
    ],
    [
      3.8972145162242913,
      25.439783836971085
    ],
    [
      3.8801509230137707,
      26.782561033840405
    ],
    [
      3.874647155405194,
      28.125180032029405
    ],
    [
      3.8849236150437596,
      29.467908180387795
    ],
    [
      3.890827494421548,
      30.810817763027455
    ],
    [
      3.8978466483945455,
      32.15377628771995
    ],
    [
      3.8960101784940067,
      33.49674819874957
    ],
    [
      3.8922534990573503,
      34.83978365617077
    ],
    [
      3.895721332299959,
      36.182723927885604
    ],
    [
      3.9005375414994465,
      37.525246896144026
    ],
    [
      3.912532103740365,
      38.86703542035027
    ],
    [
      3.9269636116220967,
      40.20905133243471
    ],
    [
      3.938670667375881,
      41.55190226144795
    ],
    [
      3.9394646813298806,
      42.89464205965106
    ],
    [
      3.9348912225901245,
      44.236716125007206
    ],
    [
      3.938228922410693,
      45.57815764148436
    ],
    [
      3.940275700137896,
      46.920653185906474
    ],
    [
      3.935002078296337,
      48.26271071734477
    ],
    [
      3.7461875298601637,
      49.50240949636235
    ],
    [
      2.6807901962218965,
      49.95674750353244
    ],
    [
      1.3425187432755583,
      49.96787440907004
    ],
    [
      0.18351907611263998,
      49.96448676687814
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
    0.9104581549999999,
    -0.881537755,
    -0.001307204999999978
  ],
  "construction_scale": 74.49454390413791,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
