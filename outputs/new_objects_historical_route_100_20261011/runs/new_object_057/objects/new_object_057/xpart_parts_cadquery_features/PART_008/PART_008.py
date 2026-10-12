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
    -0.14208257567662178,
    0.04197119831261767
  ],
  "profile": [
    [
      1.0953129014707208,
      -49.432869873439756
    ],
    [
      3.212667623968252,
      -49.42613899345453
    ],
    [
      5.354469904413627,
      -49.42721347566024
    ],
    [
      7.496307723064225,
      -49.42035813600137
    ],
    [
      9.63808299961777,
      -49.417991290220016
    ],
    [
      11.77980252427881,
      -49.40649954175775
    ],
    [
      13.921463540966801,
      -49.39804659642475
    ],
    [
      16.063198385227363,
      -49.3926780504396
    ],
    [
      18.204926576354723,
      -49.386864253402806
    ],
    [
      20.346600369111023,
      -49.36562590462056
    ],
    [
      22.488089257049545,
      -49.331492065645236
    ],
    [
      24.62811926809364,
      -49.272186259774784
    ],
    [
      26.763517799038237,
      -49.06755618835267
    ],
    [
      28.813912290016575,
      -48.48058839275744
    ],
    [
      30.431266461871054,
      -47.37907082393548
    ],
    [
      31.76970294884996,
      -45.752981193245674
    ],
    [
      32.59029706406034,
      -43.77111835855359
    ],
    [
      33.16685852929743,
      -41.69051328321491
    ],
    [
      33.27078061772672,
      -39.714372091717514
    ],
    [
      33.28406663058602,
      -37.76844609362507
    ],
    [
      32.932284725731776,
      -35.77563544487503
    ],
    [
      32.46040067715408,
      -33.96708667829617
    ],
    [
      32.73643168875563,
      -32.175133609551146
    ],
    [
      33.032222065656796,
      -30.45716902908523
    ],
    [
      33.37365582838449,
      -28.74177449669925
    ],
    [
      33.418591914704734,
      -26.972555454588438
    ],
    [
      33.14697932970826,
      -25.13680012765343
    ],
    [
      32.90954054589036,
      -23.16557348100826
    ],
    [
      32.477468648848344,
      -21.13703866079487
    ],
    [
      32.81869420032553,
      -19.137081911029306
    ],
    [
      32.996439227346755,
      -17.217519296306804
    ],
    [
      33.15543598205281,
      -15.45108407136393
    ],
    [
      33.415298345583004,
      -13.733984972727495
    ],
    [
      33.28017096802,
      -11.967147828971022
    ],
    [
      32.893448753011214,
      -10.072276966869737
    ],
    [
      32.67438028784834,
      -8.184860410729765
    ],
    [
      32.584060665914656,
      -6.598093421322013
    ],
    [
      32.992716643032736,
      -4.812479156887987
    ],
    [
      33.16319335590629,
      -2.813298656347454
    ],
    [
      33.38352537976524,
      -0.8164071529224242
    ],
    [
      33.322185933112,
      1.1373379534899388
    ],
    [
      32.977769373642566,
      3.074227777447372
    ],
    [
      32.781261045892094,
      4.8927063205291415
    ],
    [
      32.48757343256221,
      6.447023452518804
    ],
    [
      32.88783268995562,
      8.371057864384255
    ],
    [
      33.11406055591016,
      10.38753040659126
    ],
    [
      33.35444597999324,
      12.462077424818546
    ],
    [
      33.391103619365325,
      14.340824127892862
    ],
    [
      33.364209511109934,
      16.201381488347657
    ],
    [
      33.013359474044584,
      18.069051576530278
    ],
    [
      32.384108364869945,
      19.593877468775418
    ],
    [
      32.37060207486431,
      21.339524832193867
    ],
    [
      32.95621261903736,
      23.24871731206995
    ],
    [
      33.24632483408002,
      25.27872380354156
    ],
    [
      33.38261816627889,
      26.973055332158964
    ],
    [
      33.39480742869527,
      28.766806403609216
    ],
    [
      33.02961708075517,
      30.839864145736364
    ],
    [
      32.34430557117195,
      32.66354481968684
    ],
    [
      32.204223371778546,
      34.07435083700177
    ],
    [
      32.406255438768156,
      35.756013041104545
    ],
    [
      33.14895103740173,
      37.676363242345445
    ],
    [
      33.39765525251222,
      39.57346227939202
    ],
    [
      33.349663096104855,
      41.55817818250445
    ],
    [
      33.0222306654049,
      43.6579508322186
    ],
    [
      32.224872045492454,
      45.570298304137744
    ],
    [
      30.667011664951005,
      47.07651596525494
    ],
    [
      28.623286113081605,
      48.14798679204257
    ],
    [
      26.627258775198506,
      48.86441534284664
    ],
    [
      24.60633235550836,
      49.52935584770101
    ],
    [
      22.487670847825655,
      49.82235471730467
    ],
    [
      20.347702220936156,
      49.88196092343298
    ],
    [
      18.205984432640207,
      49.90043503087105
    ],
    [
      16.06407145630664,
      49.90428790885447
    ],
    [
      13.922224744375338,
      49.89666889387897
    ],
    [
      11.780413761134813,
      49.89077695405483
    ],
    [
      9.638488801061985,
      49.88863559857436
    ],
    [
      7.496561275721758,
      49.894751400793936
    ],
    [
      5.354682517803117,
      49.903522257062264
    ],
    [
      3.212786317318439,
      49.90439979548452
    ],
    [
      1.0953292334736215,
      49.90189592379281
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
    0.432694385,
    0.00020883999999999833,
    4.6764999999997225e-05
  ],
  "construction_scale": 740.2001752942057,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
