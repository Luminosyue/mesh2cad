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
    0.001514686013677588,
    -0.01315017158064904
  ],
  "profile": [
    [
      0.17546937637266619,
      -49.99212452672286
    ],
    [
      1.1869150388983878,
      -49.83687506534088
    ],
    [
      1.596271940750551,
      -48.83177284243001
    ],
    [
      1.6041882112944759,
      -47.55059466354397
    ],
    [
      1.6035737019438638,
      -46.265689878445585
    ],
    [
      1.6032720456431306,
      -44.98084094652357
    ],
    [
      1.600401352311125,
      -43.69614907067181
    ],
    [
      1.5989657035784028,
      -42.41134257922255
    ],
    [
      1.5996046483998285,
      -41.12645350736899
    ],
    [
      1.6002289239185121,
      -39.841590181136965
    ],
    [
      1.5981192421221002,
      -38.55677981437586
    ],
    [
      1.5978278273554856,
      -37.27193688517872
    ],
    [
      1.5938734513403494,
      -35.98703260709841
    ],
    [
      1.5944330630043693,
      -34.702188115191355
    ],
    [
      1.59642557869665,
      -33.41743522667481
    ],
    [
      1.5973535390285944,
      -32.13264807010721
    ],
    [
      1.5964866711005294,
      -30.84786429689476
    ],
    [
      1.5953324218455773,
      -29.563300918373407
    ],
    [
      1.5928458984823741,
      -28.27881289350119
    ],
    [
      1.5941484752899608,
      -26.994371564523078
    ],
    [
      1.5941717436704224,
      -25.70992337540425
    ],
    [
      1.5925798576343708,
      -24.42546847912578
    ],
    [
      1.5934906606924473,
      -23.140942477710833
    ],
    [
      1.592882183307342,
      -21.856368278645043
    ],
    [
      1.5916041239403782,
      -20.57181096451252
    ],
    [
      1.5928236683254369,
      -19.287254600891277
    ],
    [
      1.5943248779124044,
      -18.0026962040224
    ],
    [
      1.5934752611492797,
      -16.718138366018046
    ],
    [
      1.5939848841081825,
      -15.433587345073951
    ],
    [
      1.5940733120799488,
      -14.149024099758536
    ],
    [
      1.5920248567477604,
      -12.864474722800153
    ],
    [
      1.5909733552215757,
      -11.58005259223442
    ],
    [
      1.591591604291227,
      -10.295422079398806
    ],
    [
      1.5912328615345697,
      -9.010265873003402
    ],
    [
      1.5920423170226827,
      -7.725074501881787
    ],
    [
      1.5915401439127017,
      -6.439896604547606
    ],
    [
      1.5894953847698314,
      -5.15494973257798
    ],
    [
      1.590545005804136,
      -3.8702854876518247
    ],
    [
      1.5908606498358056,
      -2.5857766189399705
    ],
    [
      1.5902643897341686,
      -1.301218065707321
    ],
    [
      1.5896680254493054,
      -0.016480242594257663
    ],
    [
      1.5902459547612113,
      1.2684484366197772
    ],
    [
      1.5890954281825078,
      2.553353754660364
    ],
    [
      1.5888990595692836,
      3.8379634632640056
    ],
    [
      1.588133675502777,
      5.122422623859078
    ],
    [
      1.5894978482852067,
      6.4067976115561525
    ],
    [
      1.588062426624908,
      7.6910682925453875
    ],
    [
      1.5865778620059603,
      8.97539584497353
    ],
    [
      1.5863337228518852,
      10.260064185075343
    ],
    [
      1.5863839877025105,
      11.544337090572064
    ],
    [
      1.587298423495256,
      12.829081702785704
    ],
    [
      1.5871324476318964,
      14.114021343025845
    ],
    [
      1.588084113412056,
      15.398952930163357
    ],
    [
      1.5877593002599941,
      16.683629188168943
    ],
    [
      1.5872545209234987,
      17.968164114847077
    ],
    [
      1.5860030529920977,
      19.252832400867433
    ],
    [
      1.5863462913798418,
      20.537694766965526
    ],
    [
      1.5866572636683618,
      21.822590402325403
    ],
    [
      1.5851032817201776,
      23.10754644390114
    ],
    [
      1.5861658044645144,
      24.39246737819982
    ],
    [
      1.5839356576862693,
      25.677432134626205
    ],
    [
      1.5841293162471668,
      26.962373937481953
    ],
    [
      1.5846525991405906,
      28.247338018794107
    ],
    [
      1.5839107766674063,
      29.53218381723135
    ],
    [
      1.5844289822858961,
      30.8171142651261
    ],
    [
      1.584565519389981,
      32.102082821162206
    ],
    [
      1.5847829573410004,
      33.38703380882496
    ],
    [
      1.582623107458076,
      34.67203701303038
    ],
    [
      1.5816181551514485,
      35.95701758427485
    ],
    [
      1.5812895042617627,
      37.24196611193614
    ],
    [
      1.580019954459706,
      38.526850956686445
    ],
    [
      1.5803630583892192,
      39.811660232116445
    ],
    [
      1.579787430215816,
      41.096581864625385
    ],
    [
      1.5782135449572507,
      42.381514593735304
    ],
    [
      1.5797597084133006,
      43.66647729705363
    ],
    [
      1.5812364552893519,
      44.95135700728322
    ],
    [
      1.580336226801224,
      46.236318347899584
    ],
    [
      1.5819404776998525,
      47.521289257147174
    ],
    [
      1.575129527730502,
      48.8029066487634
    ],
    [
      1.1820947424534562,
      49.82109586862985
    ],
    [
      0.17542447142456974,
      49.98567043329287
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
    0.731238685,
    -0.338272395,
    0.295492465
  ],
  "construction_scale": 62.882035483439694,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
