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
    0.09351243846448677,
    0.06226386287164923
  ],
  "profile": [
    [
      0.9128574992248881,
      -49.78520051445207
    ],
    [
      2.6775424660264733,
      -49.796094281700626
    ],
    [
      4.462499414253454,
      -49.81012428955178
    ],
    [
      6.247382203875672,
      -49.829481539715275
    ],
    [
      8.032365825036658,
      -49.837129541591466
    ],
    [
      9.817270834297391,
      -49.829516220875654
    ],
    [
      11.599434824377301,
      -49.78024186326601
    ],
    [
      13.353988376244587,
      -49.57509595540358
    ],
    [
      15.042779909102528,
      -49.00170616790367
    ],
    [
      16.648964324431162,
      -48.050992109564056
    ],
    [
      18.060674352161065,
      -46.90281318264411
    ],
    [
      19.35401512435495,
      -45.68508962708076
    ],
    [
      20.38729629450361,
      -44.39045984066205
    ],
    [
      21.219357096131816,
      -43.01509474517175
    ],
    [
      21.527495055910386,
      -41.45844139806747
    ],
    [
      21.901862309998634,
      -39.78651718149272
    ],
    [
      21.865070080833735,
      -38.09317842429857
    ],
    [
      21.919289955280565,
      -36.47535469419004
    ],
    [
      22.169369941988727,
      -34.873250163866956
    ],
    [
      22.262227353575184,
      -33.22842380556881
    ],
    [
      22.169046934526055,
      -31.544206375677835
    ],
    [
      22.05723357258248,
      -29.856402244147997
    ],
    [
      22.004816995409307,
      -28.21683460395129
    ],
    [
      22.141015481012786,
      -26.571452764101707
    ],
    [
      22.158764579384325,
      -24.93687547012768
    ],
    [
      22.328939559175495,
      -23.271273529821556
    ],
    [
      22.304693050391535,
      -21.563253408503442
    ],
    [
      22.122651857506384,
      -19.972840296426853
    ],
    [
      22.06658224465455,
      -18.372208765312955
    ],
    [
      22.04818581252988,
      -16.72678986454614
    ],
    [
      22.204251950516728,
      -15.12075006487854
    ],
    [
      22.213374385544284,
      -13.452058720247486
    ],
    [
      22.343279843881696,
      -11.869712961827437
    ],
    [
      22.186780795165546,
      -10.159903392893375
    ],
    [
      22.00808520189106,
      -8.45165350779132
    ],
    [
      22.01769956964842,
      -6.803497413493977
    ],
    [
      22.221611076786644,
      -5.139888225921993
    ],
    [
      22.062183400655975,
      -3.4993261767860577
    ],
    [
      22.14749793857493,
      -1.843683712183766
    ],
    [
      22.24908160329236,
      -0.1395175890295189
    ],
    [
      22.252567299589657,
      1.5172766947327228
    ],
    [
      22.08324866092144,
      3.142596301285109
    ],
    [
      22.05465445362312,
      4.815926650652067
    ],
    [
      22.142236336549097,
      6.404116553412052
    ],
    [
      22.01294759623577,
      7.979042260695083
    ],
    [
      22.220617600340894,
      9.63508953310933
    ],
    [
      22.1096371609273,
      11.336187753481143
    ],
    [
      21.920409615975135,
      12.99629162790913
    ],
    [
      22.03553432759169,
      14.607584142047532
    ],
    [
      22.23788746051867,
      16.211926801596064
    ],
    [
      22.200704659219227,
      17.81539127220279
    ],
    [
      22.06093911386388,
      19.460301066883137
    ],
    [
      22.161921156617147,
      21.163365246170592
    ],
    [
      22.15863964098469,
      22.893057772881658
    ],
    [
      22.11641300992659,
      24.582828737690527
    ],
    [
      22.310695643591473,
      26.23058248761126
    ],
    [
      22.387421979232528,
      27.87837507103717
    ],
    [
      22.0484504603087,
      29.503872257912306
    ],
    [
      22.207316074378483,
      31.146763994081432
    ],
    [
      22.377034385879067,
      32.855562329678165
    ],
    [
      22.25192868963164,
      34.597581227415944
    ],
    [
      22.214867108447464,
      36.28380234021027
    ],
    [
      22.191402271163753,
      37.92373018123004
    ],
    [
      21.995065310939605,
      39.57898676078443
    ],
    [
      21.81990763224008,
      41.272344482568116
    ],
    [
      21.579232204834444,
      42.9357635318995
    ],
    [
      21.275274467848902,
      44.5456973791268
    ],
    [
      20.717423252525094,
      46.15140642191025
    ],
    [
      19.868839998527825,
      47.69854245596818
    ],
    [
      18.599014583726415,
      48.83820345769399
    ],
    [
      16.931055752729304,
      49.30608945035808
    ],
    [
      15.164051319975606,
      49.4743381160543
    ],
    [
      13.383020139424502,
      49.5364790149478
    ],
    [
      11.598538890853803,
      49.59481938177295
    ],
    [
      9.81370140544097,
      49.642400768499726
    ],
    [
      8.028893038533596,
      49.66100150157936
    ],
    [
      6.244276780842115,
      49.674091744220576
    ],
    [
      4.459662075231154,
      49.69656193770579
    ],
    [
      2.674897065001254,
      49.71658966829371
    ],
    [
      0.9112620486789991,
      49.740746673371206
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.9740094508732046,
      0.22600778294832036,
      0.015035679448009629
    ],
    [
      0.22601467294274094,
      0.9741230804032911,
      -0.0012616814927288813
    ],
    [
      -0.014931752216810172,
      0.002169394475003994,
      -0.9998861617721027
    ]
  ],
  "axis_candidate": 3,
  "center": [
    -0.550063085,
    0.011559549999999998,
    -0.37826129000000003
  ],
  "construction_scale": 367.63784084531414,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
