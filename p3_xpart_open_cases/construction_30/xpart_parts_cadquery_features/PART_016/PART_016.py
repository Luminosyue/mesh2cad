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
    -0.0364087803150461,
    -0.06638787067476874
  ],
  "profile": [
    [
      1.0418878282043176,
      -43.8317190743101
    ],
    [
      2.225097077297659,
      -45.409556935224245
    ],
    [
      3.0603463327578915,
      -47.552050627928125
    ],
    [
      4.866117083146664,
      -49.02107065276432
    ],
    [
      7.14611301555113,
      -49.667294051450355
    ],
    [
      9.469259652200584,
      -49.83099388203413
    ],
    [
      11.795852981729547,
      -49.83344564651659
    ],
    [
      14.122516532165646,
      -49.82978695136389
    ],
    [
      16.449109451001892,
      -49.80645912840009
    ],
    [
      18.775504465462852,
      -49.77122336315506
    ],
    [
      21.102079720030613,
      -49.7570954811565
    ],
    [
      23.432161061309294,
      -49.685024667569294
    ],
    [
      25.684031029027782,
      -49.26456703901012
    ],
    [
      27.63580462774155,
      -48.05233084457021
    ],
    [
      28.899584089065918,
      -46.19883708516243
    ],
    [
      29.38047143648897,
      -43.94210854186235
    ],
    [
      29.526017133117072,
      -41.609475079326515
    ],
    [
      29.582453536876965,
      -39.27294055367574
    ],
    [
      29.631321273065737,
      -36.93542271647082
    ],
    [
      29.63235113491336,
      -34.59801245216484
    ],
    [
      29.781580997058576,
      -32.29329457350797
    ],
    [
      30.66821609550403,
      -30.815534273492418
    ],
    [
      32.786398684509855,
      -30.696083925215547
    ],
    [
      35.09975647173991,
      -30.853314670925265
    ],
    [
      37.43426469438394,
      -31.162691062745083
    ],
    [
      39.770991707153115,
      -31.146207495646475
    ],
    [
      42.012259891096704,
      -30.62255505401535
    ],
    [
      43.962225104999376,
      -29.373668087909582
    ],
    [
      45.55923477359836,
      -27.666295737626683
    ],
    [
      46.770553301876376,
      -25.715960402125226
    ],
    [
      47.45448535853508,
      -23.54229687007286
    ],
    [
      47.715757818055636,
      -21.26091633245384
    ],
    [
      47.796087797590886,
      -18.95301431830716
    ],
    [
      47.894918926295254,
      -16.629037226174837
    ],
    [
      47.91469073787028,
      -14.293689998481405
    ],
    [
      47.83734840195115,
      -11.956646811151257
    ],
    [
      47.86546058636756,
      -9.618596251677243
    ],
    [
      47.9378438156192,
      -7.276457729525179
    ],
    [
      47.85132726081298,
      -4.941714445573268
    ],
    [
      47.66840089640472,
      -2.62136677685207
    ],
    [
      47.36696701639234,
      -0.369877879381457
    ],
    [
      46.59039245483477,
      1.8375652329940149
    ],
    [
      45.36683509500109,
      3.884020912018714
    ],
    [
      43.71960212710819,
      5.5908023671966465
    ],
    [
      41.670429935329096,
      6.715730734089261
    ],
    [
      39.39417910852233,
      7.171390581328875
    ],
    [
      37.05231159597715,
      7.27698332419981
    ],
    [
      34.70779568750386,
      7.268441540239073
    ],
    [
      32.36318261967548,
      7.252108946673446
    ],
    [
      30.01860099327665,
      7.257885388047246
    ],
    [
      27.678028821446716,
      7.244549758409722
    ],
    [
      25.33875288896128,
      7.21810210708272
    ],
    [
      22.994151224272517,
      7.194494350208173
    ],
    [
      20.65063742463132,
      7.192938429527883
    ],
    [
      18.382637699216914,
      7.174829698442803
    ],
    [
      16.738923527623108,
      7.439406389294884
    ],
    [
      15.466737416658297,
      9.303088234144766
    ],
    [
      15.301228705113932,
      11.597856410396568
    ],
    [
      15.08924255820041,
      13.878713708038134
    ],
    [
      14.969242562721707,
      16.14023441229952
    ],
    [
      15.099395904018323,
      18.372280382664094
    ],
    [
      15.125518298243946,
      20.539217867703833
    ],
    [
      15.17830771635233,
      22.75932453164443
    ],
    [
      15.15098197566649,
      25.012760454504352
    ],
    [
      15.064732233653416,
      27.257912808844456
    ],
    [
      15.175219148541709,
      29.47942588767615
    ],
    [
      15.272696118574657,
      31.692249064932625
    ],
    [
      15.354726677336688,
      33.975568766750484
    ],
    [
      15.194401431675383,
      36.21196395440829
    ],
    [
      15.041436384123099,
      38.3863872250445
    ],
    [
      15.016657492898812,
      40.561158220376136
    ],
    [
      15.16360828699198,
      42.730074146559204
    ],
    [
      15.167068956006112,
      44.938846297686304
    ],
    [
      14.108468744634841,
      46.78377187790802
    ],
    [
      12.366655210961584,
      48.32653747759471
    ],
    [
      10.33787074346806,
      49.271704084540914
    ],
    [
      8.149751589802126,
      49.631768093671745
    ],
    [
      5.846633851651115,
      49.77524907386077
    ],
    [
      3.5089144208751692,
      49.84648854101294
    ],
    [
      1.1963094364853823,
      49.88091101261112
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "axis_candidate": 0,
  "center": [
    0.783946645,
    0.28465046,
    -0.56977883
  ],
  "construction_scale": 250.15428265382678,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
