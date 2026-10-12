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
    0.14695164505311614,
    0.026525276562882227
  ],
  "profile": [
    [
      1.325026279716683,
      -7.0296101940571125
    ],
    [
      2.649441438733904,
      -7.010435292957972
    ],
    [
      3.97400188635425,
      -6.974885397382639
    ],
    [
      5.298254792235442,
      -6.926668823166729
    ],
    [
      6.621931641646516,
      -6.859785783318264
    ],
    [
      7.944821996938723,
      -6.77848653084741
    ],
    [
      9.266581732376238,
      -6.684730547045822
    ],
    [
      10.587679128541849,
      -6.583031223343268
    ],
    [
      11.907818268928112,
      -6.470963240726947
    ],
    [
      13.226879811492163,
      -6.341088848299055
    ],
    [
      14.54412877664127,
      -6.200549980303375
    ],
    [
      15.860346302727667,
      -6.047673128589809
    ],
    [
      17.174940707821918,
      -5.886136971113447
    ],
    [
      18.487885928621616,
      -5.713258712164904
    ],
    [
      19.79876150461662,
      -5.526066516657613
    ],
    [
      21.107140625986624,
      -5.318948483940319
    ],
    [
      22.414176789736707,
      -5.107962019547399
    ],
    [
      23.71701240032658,
      -4.874391520215877
    ],
    [
      25.01551993263122,
      -4.637549618310625
    ],
    [
      26.310154323796745,
      -4.394410231621356
    ],
    [
      27.60141041166504,
      -4.1360763842868575
    ],
    [
      28.89097577322829,
      -3.8484289686625046
    ],
    [
      30.177717498984645,
      -3.5327943195764524
    ],
    [
      31.458796549159196,
      -3.195262871889124
    ],
    [
      32.73633837255727,
      -2.8330690483203718
    ],
    [
      34.01226143586473,
      -2.4724194284247685
    ],
    [
      35.28149266240979,
      -2.095999269384705
    ],
    [
      36.54338301800641,
      -1.7024251089157962
    ],
    [
      37.7994273204619,
      -1.2975655908766552
    ],
    [
      39.053691838608515,
      -0.8724317594885849
    ],
    [
      40.304346968220116,
      -0.43227579167249114
    ],
    [
      41.54914960469857,
      0.022480637277885084
    ],
    [
      42.787213329875016,
      0.48858652505483957
    ],
    [
      44.01581803808479,
      0.9465817525923413
    ],
    [
      45.2412452912975,
      1.4267749112290198
    ],
    [
      46.462470728620055,
      1.9436569282521794
    ],
    [
      47.678303914350735,
      2.468451836027721
    ],
    [
      48.85703419710883,
      3.063254680909989
    ],
    [
      49.625411598950166,
      4.051560087217496
    ],
    [
      49.71176591404294,
      5.31601506442458
    ],
    [
      49.12528004461403,
      5.471776179459927
    ],
    [
      48.65564023268155,
      4.338381044285303
    ],
    [
      47.690324902937434,
      3.5561582530234723
    ],
    [
      46.475512695192634,
      3.0290395470419433
    ],
    [
      45.25124460901691,
      2.535783295889054
    ],
    [
      44.0172998064554,
      2.0608101684227558
    ],
    [
      42.78284429401327,
      1.607090285534742
    ],
    [
      41.54770876821512,
      1.1651322125044188
    ],
    [
      40.309758440888615,
      0.7237512043347767
    ],
    [
      39.064361185158425,
      0.27282868245835207
    ],
    [
      37.80746112442506,
      -0.16544706040288507
    ],
    [
      36.54578488989925,
      -0.5684921139437312
    ],
    [
      35.27670111659171,
      -0.9474903244462469
    ],
    [
      34.00132073726998,
      -1.3156093830216817
    ],
    [
      32.724354647015545,
      -1.6782724635302513
    ],
    [
      31.44702646083296,
      -2.0386742564129143
    ],
    [
      30.167568788963543,
      -2.381998354973066
    ],
    [
      28.884058991086018,
      -2.705583224007359
    ],
    [
      27.59652907979563,
      -2.9939030463816603
    ],
    [
      26.307805852954136,
      -3.2561941202355418
    ],
    [
      25.01665550110708,
      -3.505905879553687
    ],
    [
      23.72106904242935,
      -3.761686635612241
    ],
    [
      22.419776944195952,
      -3.9855920573531947
    ],
    [
      21.111952702354586,
      -4.19544553563245
    ],
    [
      19.801027353874975,
      -4.399136942584187
    ],
    [
      18.488375801768534,
      -4.5867036739594145
    ],
    [
      17.17429330985506,
      -4.756003968359195
    ],
    [
      15.858787742442967,
      -4.910538547441517
    ],
    [
      14.542501775392262,
      -5.060912967235964
    ],
    [
      13.225647391986818,
      -5.209207449306843
    ],
    [
      11.907588805920955,
      -5.34610692110261
    ],
    [
      10.587662931773508,
      -5.467803202091838
    ],
    [
      9.266918459838202,
      -5.5755535338299635
    ],
    [
      7.945057383307467,
      -5.664389306874181
    ],
    [
      6.622321205581718,
      -5.739073219966452
    ],
    [
      5.2986136496565095,
      -5.80038928438411
    ],
    [
      3.9742109793824136,
      -5.84466611578031
    ],
    [
      2.6495977282473646,
      -5.880422936607074
    ],
    [
      1.3251151928287923,
      -5.90392587600372
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.1317555476348199,
      0.002764918490280013,
      -0.9912783821375257
    ],
    [
      -0.9912263288175688,
      -0.010988115871020545,
      0.13171798042958943
    ],
    [
      -0.010528092243772807,
      0.999935806207252,
      0.004188405228661192
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.0003974699999999831,
    0.0035720999999999947,
    0.0003055100000000366
  ],
  "construction_scale": 100.04515437997784,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
