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
    0.3239265221360013,
    -0.019097363909865547
  ],
  "profile": [
    [
      1.75684030117859,
      -42.397667757480264
    ],
    [
      5.153092958978563,
      -42.396289213090725
    ],
    [
      8.588441403746945,
      -42.39663901563125
    ],
    [
      12.02371978337737,
      -42.397259619050885
    ],
    [
      15.458995528383788,
      -42.399379963168386
    ],
    [
      18.89418583966196,
      -42.40215022438649
    ],
    [
      22.329386136390177,
      -42.406302322479604
    ],
    [
      25.764545816315138,
      -42.412432044004305
    ],
    [
      29.181930481068555,
      -42.43873513234696
    ],
    [
      31.697035655387246,
      -42.830945400534915
    ],
    [
      32.13808633434354,
      -44.74439895431148
    ],
    [
      33.05647675106893,
      -47.41644676475646
    ],
    [
      35.451813775210155,
      -47.34764231795164
    ],
    [
      37.57466305410668,
      -44.92696294411475
    ],
    [
      39.77807968694944,
      -42.70256513376749
    ],
    [
      41.63518404515284,
      -40.2773670638932
    ],
    [
      42.44981867560228,
      -37.00308626789732
    ],
    [
      43.36405783409155,
      -33.687601030188006
    ],
    [
      44.82953611062153,
      -31.064294344052946
    ],
    [
      45.53002115396602,
      -27.960410506889954
    ],
    [
      45.77631099416767,
      -24.51359670053898
    ],
    [
      45.90460456059783,
      -21.125008707374775
    ],
    [
      46.01813285470823,
      -17.78249641668102
    ],
    [
      46.01515021277599,
      -14.3454114155062
    ],
    [
      46.22254254304289,
      -10.881628771933128
    ],
    [
      46.53124076772691,
      -7.421496591132445
    ],
    [
      46.810452516122474,
      -3.984829090860578
    ],
    [
      47.15844223384043,
      -0.5854477123094852
    ],
    [
      47.41766521021742,
      2.8654749344014876
    ],
    [
      47.60761936330887,
      6.331235038306341
    ],
    [
      47.768319472886574,
      9.806183575749376
    ],
    [
      47.991802706098184,
      13.283575496578305
    ],
    [
      48.24426854056917,
      16.758995663234263
    ],
    [
      48.36455439436287,
      20.206247724372318
    ],
    [
      48.40160764033191,
      23.607788635990474
    ],
    [
      48.451063284575454,
      27.023592469504955
    ],
    [
      48.63330902302202,
      30.455015890143393
    ],
    [
      48.89033864622141,
      33.90379802430225
    ],
    [
      49.248981992892695,
      37.33077604013058
    ],
    [
      49.56380553960866,
      40.74604702314975
    ],
    [
      49.80698551880343,
      44.16687940861188
    ],
    [
      49.688702980750136,
      47.52137081914479
    ],
    [
      47.784419464628826,
      49.130882701512505
    ],
    [
      45.39834443880708,
      48.172007088869535
    ],
    [
      44.3817608323304,
      45.2353152619339
    ],
    [
      44.05848244818557,
      41.81610681303573
    ],
    [
      43.77760964456492,
      38.37507179528888
    ],
    [
      43.465302233319726,
      34.94434643893542
    ],
    [
      43.059662164606934,
      31.524470743868747
    ],
    [
      42.73301004327059,
      28.093263723992266
    ],
    [
      42.57468543049207,
      24.66281338793354
    ],
    [
      42.289155186763224,
      21.305619970818388
    ],
    [
      42.0214731980999,
      17.992299355126733
    ],
    [
      41.93426877597893,
      14.671163811879431
    ],
    [
      41.99271841932411,
      11.32885804052216
    ],
    [
      41.87547550296624,
      7.924020042983013
    ],
    [
      41.6995671359435,
      4.543767637839828
    ],
    [
      41.436425773160835,
      1.2273087860933298
    ],
    [
      41.1759546636311,
      -2.033004879788696
    ],
    [
      40.98251843550782,
      -5.353380207459649
    ],
    [
      40.70994016398644,
      -8.681428154279217
    ],
    [
      40.41147087084525,
      -11.941195607146549
    ],
    [
      39.95243582234761,
      -15.20229946562178
    ],
    [
      39.58314804173169,
      -18.470286339928105
    ],
    [
      39.20618750283336,
      -21.698314554656733
    ],
    [
      39.12953729110718,
      -24.89974277575243
    ],
    [
      38.127471090371884,
      -27.849563581691747
    ],
    [
      36.90825806991852,
      -30.379940567477284
    ],
    [
      35.534810783633006,
      -32.96483263908146
    ],
    [
      33.85802928724607,
      -35.603858766963555
    ],
    [
      31.569028049561886,
      -37.148484720618136
    ],
    [
      28.97020165300104,
      -37.474048312073066
    ],
    [
      25.623565380248813,
      -37.64547281222078
    ],
    [
      22.18977295382271,
      -37.7724977323118
    ],
    [
      18.759492429462945,
      -37.784523757275956
    ],
    [
      15.373163546809325,
      -37.79827189631827
    ],
    [
      11.97052815899512,
      -37.494744493431014
    ],
    [
      8.556623351881534,
      -37.07064895787705
    ],
    [
      5.137912779223697,
      -36.97817903923771
    ],
    [
      1.7553768593928702,
      -36.97877213467051
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "axis_candidate": 1,
  "center": [
    -0.00048354500000002965,
    -0.005295125000000012,
    -0.005638564999999984
  ],
  "construction_scale": 50.30650976649826,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
