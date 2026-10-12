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
    0.35573847575796724,
    -0.8189590131213489
  ],
  "profile": [
    [
      1.3391164964027353,
      29.62793543298386
    ],
    [
      3.9155840702699063,
      29.69114609013882
    ],
    [
      6.51525414350357,
      29.96550719835303
    ],
    [
      9.128837205010925,
      30.320208075215106
    ],
    [
      11.751290019855691,
      30.584764810107536
    ],
    [
      14.336937834980464,
      30.703558743811747
    ],
    [
      16.934704495476073,
      30.759424675816575
    ],
    [
      19.54876836976412,
      30.78806183795791
    ],
    [
      22.164476178228803,
      30.826622905699573
    ],
    [
      24.755756013047897,
      30.877676306260057
    ],
    [
      27.317546725975177,
      30.810251689395944
    ],
    [
      29.81119842605473,
      30.06893815003246
    ],
    [
      32.03267903782954,
      28.875743157307898
    ],
    [
      34.0403291443278,
      27.127140815896077
    ],
    [
      35.95992738333476,
      25.2881280717609
    ],
    [
      37.76390016185462,
      23.412488450392228
    ],
    [
      39.56654252969306,
      21.48317718973583
    ],
    [
      41.354702982098246,
      19.594521879186914
    ],
    [
      42.98377903212723,
      17.535275031260912
    ],
    [
      44.2804628986037,
      15.325272436847484
    ],
    [
      44.945756755164915,
      13.045090826821884
    ],
    [
      45.439928718254734,
      10.582077391269525
    ],
    [
      45.491487059652556,
      7.949137975876189
    ],
    [
      45.45535242098083,
      5.308046369853651
    ],
    [
      45.43424373020564,
      2.6664387168870975
    ],
    [
      45.44012349717528,
      0.03749370525978531
    ],
    [
      45.4208933281549,
      -2.5626131867615216
    ],
    [
      45.382606397702716,
      -5.159142103056007
    ],
    [
      45.361820887281006,
      -7.764315202127898
    ],
    [
      45.31917738135067,
      -10.403421832723378
    ],
    [
      45.21488780981605,
      -13.047731110386032
    ],
    [
      45.321431763344904,
      -15.650492096828595
    ],
    [
      45.38017557743686,
      -18.147863236988393
    ],
    [
      45.41043721513165,
      -20.741353959699207
    ],
    [
      45.410128301229136,
      -23.337974732628755
    ],
    [
      45.427839188859764,
      -25.932760251538134
    ],
    [
      45.2540882769482,
      -28.454674960782977
    ],
    [
      45.3228952927526,
      -30.993551478442697
    ],
    [
      46.50333734409661,
      -32.9700864188277
    ],
    [
      48.20230926636063,
      -32.98943425499169
    ],
    [
      48.88794138005153,
      -30.731621385181622
    ],
    [
      49.05858787487557,
      -28.118546027654773
    ],
    [
      49.10039648626511,
      -25.489075671193593
    ],
    [
      49.10712468151057,
      -22.84839177240247
    ],
    [
      49.107980372397506,
      -20.20696165329838
    ],
    [
      49.06333251313346,
      -17.56510382826611
    ],
    [
      48.99273017709956,
      -14.925075828340422
    ],
    [
      48.95781426975492,
      -12.339615951089321
    ],
    [
      48.96409069910619,
      -9.80268820992301
    ],
    [
      49.0179440758783,
      -7.188495342765007
    ],
    [
      48.92681427385044,
      -4.5640511813371045
    ],
    [
      48.86840578510952,
      -1.9174408256305464
    ],
    [
      48.876467683314985,
      0.7327380502227617
    ],
    [
      48.84663219136088,
      3.3831062868723114
    ],
    [
      48.82478640578077,
      6.033103001015853
    ],
    [
      48.8041237206249,
      8.682064386164829
    ],
    [
      48.75740118446357,
      11.330586687928513
    ],
    [
      48.62797280441646,
      13.965411316194915
    ],
    [
      48.17664253777967,
      16.354399755134267
    ],
    [
      47.100841896922105,
      18.717932977454005
    ],
    [
      45.566762856906934,
      20.819081770076732
    ],
    [
      43.911538445280954,
      22.74248883282644
    ],
    [
      42.04590548416558,
      24.67492779788438
    ],
    [
      40.30142725159477,
      26.59820704030391
    ],
    [
      38.504633109092694,
      28.4544597281821
    ],
    [
      36.63679050446522,
      30.22432092286585
    ],
    [
      34.6131166656125,
      31.90569745502188
    ],
    [
      32.255585833259566,
      33.318321538188044
    ],
    [
      29.82244870257955,
      33.968115315021976
    ],
    [
      27.269997940014633,
      33.89679802691364
    ],
    [
      24.636358735441064,
      33.8015376949242
    ],
    [
      21.996727639684586,
      33.75206041723099
    ],
    [
      19.421172988602574,
      33.722299923937115
    ],
    [
      16.94000872683352,
      33.71077787781684
    ],
    [
      14.34781304734571,
      33.712973794754106
    ],
    [
      11.74312570059371,
      33.73165875355325
    ],
    [
      9.122276401944454,
      33.712151112292915
    ],
    [
      6.509627849541079,
      33.618854599389955
    ],
    [
      3.9079116511955174,
      33.463990910683805
    ],
    [
      1.3280474777565847,
      33.267743371742625
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.7883214857228549,
      0.6152364819101418,
      -0.005771176183613157
    ],
    [
      -0.6152565715294752,
      -0.7883225379000639,
      0.002632000873403335
    ],
    [
      -0.002930245297997237,
      0.0056256169113676445,
      0.9999798828460802
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.08970941,
    0.188297005,
    0.8694657699999999
  ],
  "construction_scale": 407.66024584114194,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
