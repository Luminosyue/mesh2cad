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
    0.7101063216627673,
    0.7053814070658893
  ],
  "profile": [
    [
      1.5025854549696822,
      -49.877348138196396
    ],
    [
      4.4031036043107985,
      -49.733409383801
    ],
    [
      7.321310241013801,
      -49.430390797355145
    ],
    [
      10.186505621225756,
      -48.81656804433365
    ],
    [
      12.78955776770184,
      -47.60959735233337
    ],
    [
      15.34993938977928,
      -46.320192547671056
    ],
    [
      17.343536014162307,
      -44.2589785583774
    ],
    [
      18.99603882321025,
      -41.836617983118565
    ],
    [
      20.881839559825274,
      -39.66763011404542
    ],
    [
      22.865464383734356,
      -37.875353894507114
    ],
    [
      25.183509281591377,
      -36.207487772155226
    ],
    [
      27.228545723381448,
      -34.040611894689214
    ],
    [
      28.21102225401112,
      -31.24525382547679
    ],
    [
      28.000400609245276,
      -28.376374736752105
    ],
    [
      27.04868208024375,
      -25.607935104112123
    ],
    [
      25.897397912465767,
      -23.00509845524772
    ],
    [
      25.180571486410543,
      -20.152141415676354
    ],
    [
      25.353810815344566,
      -17.322897595855117
    ],
    [
      26.23229289627119,
      -14.75107464993662
    ],
    [
      27.413898932798546,
      -11.998298577964782
    ],
    [
      27.875289156151503,
      -9.037437667547334
    ],
    [
      27.711257832914924,
      -6.077082140389075
    ],
    [
      27.036840702342726,
      -3.2406956151746775
    ],
    [
      26.183229331368757,
      -0.5096157529049105
    ],
    [
      25.632532878091688,
      2.277724930604295
    ],
    [
      25.876105286715013,
      5.084092151873186
    ],
    [
      26.779426919178285,
      7.816147711476699
    ],
    [
      27.310190046028623,
      10.608155191106844
    ],
    [
      27.30334797399639,
      13.53176680794538
    ],
    [
      27.109892551631244,
      16.499861841365146
    ],
    [
      26.688266344224257,
      19.404350280684454
    ],
    [
      26.33054614817832,
      22.34716299816516
    ],
    [
      26.098662606423517,
      25.292504428191577
    ],
    [
      26.1812264993225,
      28.225810401278657
    ],
    [
      26.161390682629857,
      31.156200570851784
    ],
    [
      26.016563292667342,
      34.09296882787552
    ],
    [
      25.97115940095101,
      37.027748236238075
    ],
    [
      25.874069717801433,
      39.96288563039215
    ],
    [
      25.696803565189235,
      42.90017032280018
    ],
    [
      25.55810196164324,
      45.81588880662194
    ],
    [
      24.85231007486432,
      48.21467155116508
    ],
    [
      23.388488292559614,
      47.806336179957825
    ],
    [
      22.71464697692504,
      45.10033651430893
    ],
    [
      22.737382898011585,
      42.163380770380556
    ],
    [
      22.77100631958591,
      39.226165535058044
    ],
    [
      22.771010570216447,
      36.28903402849079
    ],
    [
      22.782862243116025,
      33.35226678096256
    ],
    [
      22.826818807641843,
      30.434045329321176
    ],
    [
      22.839320767430138,
      27.51895999444055
    ],
    [
      22.89020254350966,
      24.55170667474093
    ],
    [
      23.08838454775644,
      21.617619408986066
    ],
    [
      23.426330882020828,
      18.696558734823192
    ],
    [
      23.895558354689374,
      15.793953115394597
    ],
    [
      24.20913590222027,
      12.92248222560287
    ],
    [
      23.911355059589305,
      10.051563695556203
    ],
    [
      22.89914345796788,
      7.220002023038443
    ],
    [
      22.38448414359981,
      4.406729639815259
    ],
    [
      22.311896800173038,
      1.5252791741819398
    ],
    [
      22.754444680055137,
      -1.3934070397018885
    ],
    [
      23.527054300350013,
      -4.144920822270549
    ],
    [
      24.246413990878672,
      -6.935769813352394
    ],
    [
      24.43927993385431,
      -9.728288668101028
    ],
    [
      23.40545455878987,
      -12.426740895669475
    ],
    [
      22.393199655888044,
      -15.124471360160483
    ],
    [
      21.879111453437517,
      -17.958705286015874
    ],
    [
      21.803803137576296,
      -20.8896774774366
    ],
    [
      22.359968200887,
      -23.805527505322154
    ],
    [
      23.52899594327015,
      -26.41319205341133
    ],
    [
      24.601433958209274,
      -29.10592115515351
    ],
    [
      24.166128123003592,
      -31.678804441078995
    ],
    [
      22.072901627067463,
      -33.814776436526344
    ],
    [
      19.871475030751377,
      -35.57224221067753
    ],
    [
      17.854714172159163,
      -37.460983508326635
    ],
    [
      16.094537927817047,
      -39.85004160831978
    ],
    [
      14.368182480997778,
      -42.1559643837999
    ],
    [
      12.229852848772072,
      -44.068085978832436
    ],
    [
      9.898782166688132,
      -45.58730850660029
    ],
    [
      7.334395105376897,
      -46.649977535522545
    ],
    [
      4.406622657438342,
      -46.83997409916521
    ],
    [
      1.5026853053025027,
      -46.871578232622014
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.8300935615541181,
      -0.5572049760136277,
      0.021616978791033897
    ],
    [
      -0.5575470926892355,
      -0.8299993809802246,
      0.015564928725334028
    ],
    [
      0.009269223278167326,
      -0.0249728307986141,
      -0.9996451566539615
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.192795195,
    -0.015814835,
    0.860731975
  ],
  "construction_scale": 359.6475324708673,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
