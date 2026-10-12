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
    -0.5958537323569192,
    0.269383048501573
  ],
  "profile": [
    [
      1.0587584560045529,
      20.406910113075025
    ],
    [
      3.103894295236588,
      20.32713841180875
    ],
    [
      5.171593335576872,
      20.189756732593295
    ],
    [
      7.237059452090871,
      20.04829512093862
    ],
    [
      9.29553510631326,
      19.855383327990076
    ],
    [
      11.352833912624785,
      19.611269084581714
    ],
    [
      13.409459802230632,
      19.355299939121938
    ],
    [
      15.458201093387677,
      19.05531187937377
    ],
    [
      17.498900241688972,
      18.71825186868072
    ],
    [
      19.535435645201368,
      18.35071629263475
    ],
    [
      21.566168557619257,
      17.96352134350615
    ],
    [
      23.58825811831791,
      17.51583820783947
    ],
    [
      25.60501387544657,
      17.03416251776001
    ],
    [
      27.61587103590815,
      16.510288547287924
    ],
    [
      29.60868311202548,
      15.909581386336384
    ],
    [
      31.58276930028846,
      15.253122097652938
    ],
    [
      33.535755897992125,
      14.537748605887959
    ],
    [
      35.452336813339215,
      13.759144707172801
    ],
    [
      37.30209254272721,
      12.881705639899856
    ],
    [
      38.95516372298597,
      11.726964253447672
    ],
    [
      40.1918946795428,
      10.105900417844357
    ],
    [
      40.98538504353687,
      8.224893778023102
    ],
    [
      41.34281616565354,
      6.190054756134267
    ],
    [
      41.42725984719025,
      4.123573018329415
    ],
    [
      41.460020450747386,
      2.049532182601406
    ],
    [
      41.464832616170725,
      -0.020381094059919194
    ],
    [
      41.46851887691359,
      -2.090014131061798
    ],
    [
      41.4702033061814,
      -4.159478994221563
    ],
    [
      41.46433615974491,
      -6.228679898889499
    ],
    [
      41.450330430379694,
      -8.298066744068985
    ],
    [
      41.46006127546241,
      -10.367370806631678
    ],
    [
      41.48701030875411,
      -12.436332568236384
    ],
    [
      41.54528511023675,
      -14.504739306565616
    ],
    [
      41.62477728764655,
      -16.575817105146434
    ],
    [
      41.87071602853791,
      -18.63081019859699
    ],
    [
      42.452974887701316,
      -20.570023269630056
    ],
    [
      43.728761746434934,
      -21.99957179060778
    ],
    [
      45.57645355638873,
      -22.559892357028886
    ],
    [
      47.43021936693114,
      -21.93218757115809
    ],
    [
      48.50556009468418,
      -20.32610853444558
    ],
    [
      48.86246750867278,
      -18.340595470396593
    ],
    [
      48.8872369736205,
      -16.27394280607782
    ],
    [
      48.80642357554934,
      -14.203681220318476
    ],
    [
      48.67407001166659,
      -12.133180622650785
    ],
    [
      48.574759898119886,
      -10.062395350501241
    ],
    [
      48.512311899431104,
      -7.9921151254586
    ],
    [
      48.46681532817817,
      -5.921771427326637
    ],
    [
      48.440025136419216,
      -3.8517106105931536
    ],
    [
      48.42444928667794,
      -1.781733333617788
    ],
    [
      48.37304533945912,
      0.2887209927243933
    ],
    [
      48.3441630615809,
      2.358494669552215
    ],
    [
      48.312228392245174,
      4.428074400216763
    ],
    [
      48.26724059859987,
      6.494570722985046
    ],
    [
      48.073205139399775,
      8.553583098290447
    ],
    [
      47.56867899964338,
      10.599531275202729
    ],
    [
      46.783241877569466,
      12.546643188032697
    ],
    [
      45.806659641639655,
      14.352910790029322
    ],
    [
      44.53008526105325,
      15.944407879217154
    ],
    [
      43.022385869899566,
      17.362920705149538
    ],
    [
      41.31420256563389,
      18.51882120076646
    ],
    [
      39.44674969472472,
      19.36936756005276
    ],
    [
      37.536739349828295,
      20.141644697220016
    ],
    [
      35.58891624336916,
      20.829027803168053
    ],
    [
      33.62169981533764,
      21.470495977261685
    ],
    [
      31.64230577570168,
      22.08059015214815
    ],
    [
      29.64540740105181,
      22.654805763380807
    ],
    [
      27.644436432922728,
      23.190153438094317
    ],
    [
      25.631385332115183,
      23.689061433688742
    ],
    [
      23.608852123329406,
      24.143438764707472
    ],
    [
      21.584534479367022,
      24.573913191583568
    ],
    [
      19.55240058769855,
      24.973168410964945
    ],
    [
      17.51195820682066,
      25.33465376867952
    ],
    [
      15.465440873667756,
      25.654407919070614
    ],
    [
      13.415273665245605,
      25.949531252934733
    ],
    [
      11.360037478291389,
      26.2120605339628
    ],
    [
      9.300789456268223,
      26.45118489164981
    ],
    [
      7.239844432272214,
      26.655985753133102
    ],
    [
      5.174850932016637,
      26.811663303796976
    ],
    [
      3.1059359175061196,
      26.88119301199055
    ],
    [
      1.0590397453171363,
      26.9118050081478
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.23721471232514513,
      0.9687402999828156,
      0.07260448640203586
    ],
    [
      -0.9714572285018411,
      -0.2365372021149511,
      -0.017916618184037718
    ],
    [
      -0.00018288799975169114,
      -0.07478223856528733,
      0.997199871313241
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.1009224,
    0.09866276,
    0.41778527
  ],
  "construction_scale": 663.5736173216071,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
