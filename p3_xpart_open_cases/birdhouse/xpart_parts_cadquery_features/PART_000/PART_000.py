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
    -0.027575914391283717,
    -0.0690133182229979
  ],
  "profile": [
    [
      1.0731917692660373,
      -18.793914134037234
    ],
    [
      3.1478449674745708,
      -18.795340004209038
    ],
    [
      5.246412952422375,
      -18.799017619329284
    ],
    [
      7.344961690179163,
      -18.801217253372517
    ],
    [
      9.443516839030888,
      -18.806279187957752
    ],
    [
      11.54207583822361,
      -18.81125936567179
    ],
    [
      13.640645823280693,
      -18.812872449566786
    ],
    [
      15.739207805988766,
      -18.815963775444082
    ],
    [
      17.837766110426955,
      -18.82034395698612
    ],
    [
      19.936328118382878,
      -18.820125833596606
    ],
    [
      22.034895444456808,
      -18.818966435399634
    ],
    [
      24.13347211917535,
      -18.817870893722088
    ],
    [
      26.232052091180016,
      -18.817220124012014
    ],
    [
      28.330626471018498,
      -18.81764151613185
    ],
    [
      30.429197509759447,
      -18.817308086585314
    ],
    [
      32.5277622258633,
      -18.81855419503323
    ],
    [
      34.62633159227448,
      -18.817574680860524
    ],
    [
      36.72490858964656,
      -18.81383130345213
    ],
    [
      38.823473591227675,
      -18.81339841581207
    ],
    [
      40.921998444718724,
      -18.81662151782187
    ],
    [
      43.020533504719545,
      -18.809598030349882
    ],
    [
      45.11896247916824,
      -18.813946553262284
    ],
    [
      47.19884460007907,
      -18.700590599543972
    ],
    [
      49.00997871273958,
      -17.884376222017437
    ],
    [
      49.782797983195536,
      -16.124189132250486
    ],
    [
      49.854520204379924,
      -14.03294834799536
    ],
    [
      49.860689514489096,
      -11.93376523133437
    ],
    [
      49.85143871224197,
      -9.834554501116445
    ],
    [
      49.84627435959787,
      -7.735097237025988
    ],
    [
      49.847336156920676,
      -5.633451461964853
    ],
    [
      49.85878271559745,
      -3.5314963786882263
    ],
    [
      49.863397875982855,
      -1.4313790106567212
    ],
    [
      49.86444552122972,
      0.6683932433678246
    ],
    [
      49.854805347473366,
      2.767391264642532
    ],
    [
      49.85162094448211,
      4.866121117702534
    ],
    [
      49.85989626244151,
      6.964856264707262
    ],
    [
      49.86800762553363,
      9.063604214468935
    ],
    [
      49.8730469408664,
      11.16225139230452
    ],
    [
      49.872672424059374,
      13.260943392176905
    ],
    [
      49.86993990320384,
      15.359400766124509
    ],
    [
      49.66291468723674,
      17.373543283606725
    ],
    [
      48.29126761906643,
      18.431069742771967
    ],
    [
      46.78169192217775,
      17.563720155146754
    ],
    [
      46.46594950245091,
      15.5947594086173
    ],
    [
      46.45014203345295,
      13.496286320597942
    ],
    [
      46.4468517911659,
      11.396526246294677
    ],
    [
      46.43954931573406,
      9.296959975230147
    ],
    [
      46.444586621126554,
      7.19861907006566
    ],
    [
      46.44553006777935,
      5.100585340293609
    ],
    [
      46.44986850561876,
      3.0025351477641173
    ],
    [
      46.45090647315651,
      0.9045113919801584
    ],
    [
      46.4424016196387,
      -1.1933841018988907
    ],
    [
      46.43813294679045,
      -3.290863118136528
    ],
    [
      46.42763518375074,
      -5.389524903469967
    ],
    [
      46.42439279710386,
      -7.4875651852853515
    ],
    [
      46.429708605407725,
      -9.585590270377086
    ],
    [
      46.40800218827201,
      -11.682653157954793
    ],
    [
      46.13870182721908,
      -13.736423936881085
    ],
    [
      45.01670772454307,
      -15.209684854679736
    ],
    [
      43.01959345582548,
      -15.492952623008396
    ],
    [
      40.921757161794744,
      -15.510774308012174
    ],
    [
      38.82325485795174,
      -15.518142463461086
    ],
    [
      36.724689058536185,
      -15.516375044147583
    ],
    [
      34.6261241335411,
      -15.514923758196316
    ],
    [
      32.52757065295063,
      -15.514932673675727
    ],
    [
      30.429024075644143,
      -15.512672608005348
    ],
    [
      28.33048409332426,
      -15.513769663564922
    ],
    [
      26.23192789936596,
      -15.515127291039361
    ],
    [
      24.133379440170863,
      -15.517520168748911
    ],
    [
      22.034853904122016,
      -15.51858674523335
    ],
    [
      19.93630474941913,
      -15.51819896339476
    ],
    [
      17.837756033889793,
      -15.516110900138996
    ],
    [
      15.739213628438076,
      -15.512653004334357
    ],
    [
      13.640644791777671,
      -15.514220867390495
    ],
    [
      11.54206849855555,
      -15.516444491584013
    ],
    [
      9.443497145619302,
      -15.515885261397969
    ],
    [
      7.344972802656024,
      -15.518646946593188
    ],
    [
      5.246426111874081,
      -15.518349836099654
    ],
    [
      3.1478643862655042,
      -15.5208593298597
    ],
    [
      1.0732059070030047,
      -15.523281233148406
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
    0.2506559,
    0.403038495,
    0.06703188500000001
  ],
  "construction_scale": 207.40510474984444,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
