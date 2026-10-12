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
    0.06172380271630793,
    0.09488064696657388
  ],
  "profile": [
    [
      0.9878844587791435,
      -13.088908496386937
    ],
    [
      2.894775013532813,
      -12.956596951725665
    ],
    [
      4.815526017066837,
      -12.724981085306718
    ],
    [
      6.715736112287216,
      -12.346391662376822
    ],
    [
      8.580881481016357,
      -11.828659835943881
    ],
    [
      10.384089423928579,
      -11.133367848561337
    ],
    [
      12.068055989700415,
      -10.196963267816276
    ],
    [
      13.617803576308669,
      -9.085278009502392
    ],
    [
      14.939141618927778,
      -7.700876523994503
    ],
    [
      16.214567145940514,
      -6.226351087067183
    ],
    [
      17.42910391113189,
      -4.693879780414372
    ],
    [
      18.41671126186204,
      -4.121840442644412
    ],
    [
      18.996358153090988,
      -5.692211691836226
    ],
    [
      19.45980399676295,
      -7.578208105265844
    ],
    [
      19.83946040507288,
      -9.466782142279373
    ],
    [
      20.32498660918004,
      -11.308795404820792
    ],
    [
      21.02658961054614,
      -13.085437771252433
    ],
    [
      21.994909434394607,
      -14.7635232138546
    ],
    [
      23.18733475947755,
      -16.289017827172724
    ],
    [
      24.644580351935957,
      -17.598605162910086
    ],
    [
      26.39507590785051,
      -18.57212009452845
    ],
    [
      28.274895572463215,
      -19.30307868113923
    ],
    [
      30.24015870588594,
      -19.750308544634187
    ],
    [
      32.24606911659635,
      -19.98885749415452
    ],
    [
      34.266473217607526,
      -20.183930358940607
    ],
    [
      36.297224162581145,
      -20.233057325768193
    ],
    [
      38.325649956078664,
      -20.141963114450277
    ],
    [
      40.324440386693624,
      -19.79880868442448
    ],
    [
      42.25646358242939,
      -19.225348504920987
    ],
    [
      43.976474246305365,
      -18.28031504572892
    ],
    [
      45.493760342524155,
      -17.040655816556637
    ],
    [
      46.789424359597305,
      -15.507545701981478
    ],
    [
      47.92217362484278,
      -13.784687101259369
    ],
    [
      48.66857579854372,
      -11.962981841607903
    ],
    [
      49.06412980377081,
      -10.123116721159366
    ],
    [
      49.272936222229596,
      -8.217958385294548
    ],
    [
      49.464983396643014,
      -6.296445295312585
    ],
    [
      49.583657609794585,
      -4.368394278322163
    ],
    [
      49.63093858083149,
      -2.4375409847491785
    ],
    [
      49.675849508733435,
      -0.5060448169759375
    ],
    [
      49.73284459669023,
      1.4257563328175726
    ],
    [
      49.77958949914229,
      3.358131591825672
    ],
    [
      49.841992557864884,
      5.290689659437515
    ],
    [
      49.87957689402435,
      7.222826436590424
    ],
    [
      49.855571294232334,
      9.151911953330679
    ],
    [
      49.70660479573181,
      11.064388512206873
    ],
    [
      49.31081145622967,
      12.90774278537775
    ],
    [
      48.43565012842961,
      14.600330195538323
    ],
    [
      47.2520011649145,
      16.112534716550705
    ],
    [
      45.84310378742206,
      17.426518215559867
    ],
    [
      44.26982398637562,
      18.51470713384851
    ],
    [
      42.51951080273362,
      19.25581855590273
    ],
    [
      40.65355994023065,
      19.551541250768572
    ],
    [
      38.741111558549306,
      19.723209686210133
    ],
    [
      36.81178790231169,
      19.95367878451969
    ],
    [
      34.87978819190246,
      20.019052417017548
    ],
    [
      32.95126633947339,
      19.935833757633056
    ],
    [
      31.03818127767167,
      19.734752921402766
    ],
    [
      29.163484729134947,
      19.36645821319184
    ],
    [
      27.344598650945002,
      18.733000753549085
    ],
    [
      25.6370119532924,
      17.84368593074964
    ],
    [
      24.124430819496155,
      16.664535055603437
    ],
    [
      22.837897764157887,
      15.243433359117684
    ],
    [
      21.895241495919453,
      13.57201640832313
    ],
    [
      21.245167664719098,
      11.755946976348525
    ],
    [
      20.700727892064286,
      9.902790344272827
    ],
    [
      20.24755921509114,
      8.032125190674606
    ],
    [
      19.631500626718932,
      6.772555431639681
    ],
    [
      18.607995902219887,
      7.800384345174418
    ],
    [
      17.57307694140752,
      9.490226100839342
    ],
    [
      16.43602122616003,
      11.196253582783715
    ],
    [
      15.120850809048036,
      12.758984254206158
    ],
    [
      13.599701020689142,
      14.077094416535612
    ],
    [
      11.965932094244849,
      15.202644595532716
    ],
    [
      10.25786638430047,
      16.124912227177667
    ],
    [
      8.498801668607651,
      16.86011678950845
    ],
    [
      6.678488255346686,
      17.40138872635373
    ],
    [
      4.798444924357014,
      17.714701551835816
    ],
    [
      2.891395667922035,
      17.857622203512847
    ],
    [
      0.9878373514601457,
      17.838633921172843
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.3745969582496791,
      0.23478419342154772,
      -0.8969690637861943
    ],
    [
      -0.7529841277818832,
      0.48744447841207655,
      0.44205518182025205
    ],
    [
      0.5410101867605133,
      0.8409959946307547,
      -0.005806447828268161
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.414458325,
    0.224936305,
    -0.06171807
  ],
  "construction_scale": 1013.965344692449,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
