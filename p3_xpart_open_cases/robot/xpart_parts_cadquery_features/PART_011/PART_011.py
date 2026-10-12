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
    0.6181975811930415,
    -0.16100966915742237
  ],
  "profile": [
    [
      0.8457709769834676,
      -23.19094644522698
    ],
    [
      2.4807534591172464,
      -23.214518603267702
    ],
    [
      4.134693583620279,
      -23.229496726900614
    ],
    [
      5.788664446572257,
      -23.237815349823048
    ],
    [
      7.442616650226891,
      -23.241484425199054
    ],
    [
      9.09662820246229,
      -23.25201327288459
    ],
    [
      10.75057030903952,
      -23.269027288422507
    ],
    [
      12.404581935424098,
      -23.289190890375963
    ],
    [
      14.058615549202898,
      -23.301528607051928
    ],
    [
      15.712631411267502,
      -23.3092290717667
    ],
    [
      17.366635193200835,
      -23.31548229477289
    ],
    [
      19.020488979593377,
      -23.32756971981533
    ],
    [
      20.67414684053208,
      -23.340156022048006
    ],
    [
      22.32777806269786,
      -23.33435322115588
    ],
    [
      23.981390493960824,
      -23.329891227313087
    ],
    [
      25.634894929616955,
      -23.337262510031568
    ],
    [
      27.28831197466593,
      -23.340393369462443
    ],
    [
      28.9417035260256,
      -23.312648755734152
    ],
    [
      30.595164965463482,
      -23.267657279080503
    ],
    [
      32.241369146702844,
      -23.170163066749716
    ],
    [
      33.87308695712511,
      -22.965421187787264
    ],
    [
      35.48436030871552,
      -22.60703553440522
    ],
    [
      37.05008575897088,
      -22.03589467940806
    ],
    [
      38.55673909529973,
      -21.347685454884974
    ],
    [
      39.98919877106343,
      -20.540206440268115
    ],
    [
      41.36770873140526,
      -19.60565103930407
    ],
    [
      42.6454821641241,
      -18.52694146895699
    ],
    [
      43.82298811528445,
      -17.357441322420563
    ],
    [
      44.87238655111807,
      -16.124046524505623
    ],
    [
      45.81787665596987,
      -14.779680280032725
    ],
    [
      46.67065599441993,
      -13.358655562320688
    ],
    [
      47.39725198398777,
      -11.866742302519775
    ],
    [
      47.97748418515418,
      -10.322538971116916
    ],
    [
      48.44371072621675,
      -8.739610619227435
    ],
    [
      48.83941842638122,
      -7.125900961066607
    ],
    [
      49.104253017304615,
      -5.491600983144996
    ],
    [
      49.26194947011665,
      -3.8428788953200135
    ],
    [
      49.341949734798874,
      -2.186700232616905
    ],
    [
      49.343046647549656,
      -0.5316841126742333
    ],
    [
      49.29958167833048,
      1.1208301540674577
    ],
    [
      49.28255439608888,
      2.7731410798355944
    ],
    [
      49.271571328651845,
      4.4265113064290205
    ],
    [
      49.276739788037546,
      6.08167660638618
    ],
    [
      49.29330782114248,
      7.737179546985823
    ],
    [
      49.333560329493835,
      9.392355699367311
    ],
    [
      49.39438500719823,
      11.047375443810864
    ],
    [
      49.4206946258812,
      12.701422290385423
    ],
    [
      49.32296350300331,
      14.348080077921763
    ],
    [
      49.04967827883867,
      15.975170067251547
    ],
    [
      48.54551587235891,
      17.558427691987
    ],
    [
      47.77367025736066,
      19.015565384626612
    ],
    [
      46.73406290563362,
      20.25053535424135
    ],
    [
      45.36516815107452,
      21.17298160961777
    ],
    [
      43.80231400258631,
      21.679531910776806
    ],
    [
      42.16274683118,
      21.839635487749437
    ],
    [
      40.510013327737546,
      21.789409732556518
    ],
    [
      38.85744072700296,
      21.762170223350473
    ],
    [
      37.204329237578996,
      21.703023937776727
    ],
    [
      35.550703855019364,
      21.648302388892414
    ],
    [
      33.897017353527076,
      21.56954147126322
    ],
    [
      32.2431684735633,
      21.52977008618648
    ],
    [
      30.589425099394973,
      21.477949799575406
    ],
    [
      28.93588910828033,
      21.417709162530244
    ],
    [
      27.283126247106566,
      21.33430927213214
    ],
    [
      25.630599781405024,
      21.25096984914834
    ],
    [
      23.977394376149,
      21.167362348593848
    ],
    [
      22.323982769174155,
      21.131942263925836
    ],
    [
      20.670683573171452,
      21.153163254617244
    ],
    [
      19.01735387246128,
      21.173448803833175
    ],
    [
      17.363804094823934,
      21.189923345229523
    ],
    [
      15.710480927994768,
      21.191371073227423
    ],
    [
      14.056889611858487,
      21.18347413360297
    ],
    [
      12.403246650013191,
      21.165967654540797
    ],
    [
      10.749441340369735,
      21.166822511859188
    ],
    [
      9.095637478381192,
      21.16113944270768
    ],
    [
      7.441843216966166,
      21.15467132424258
    ],
    [
      5.787998002451896,
      21.152646603088506
    ],
    [
      4.134283127905605,
      21.139067180449672
    ],
    [
      2.480769761608123,
      21.15527376062113
    ],
    [
      0.8457574157380137,
      21.148047590096823
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.8226876182687769,
      0.1288277196846112,
      -0.5537043447437544
    ],
    [
      -0.563927170414012,
      -0.06173003803277359,
      0.8235141461282365
    ],
    [
      0.07191125931377645,
      0.9897438158661748,
      0.12343398939745578
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.27144536,
    -0.36983505,
    -0.31730189
  ],
  "construction_scale": 386.86347804503333,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
