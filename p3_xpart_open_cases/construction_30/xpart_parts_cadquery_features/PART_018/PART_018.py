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
    0.49489732720879376,
    0.04326680494001229
  ],
  "profile": [
    [
      1.2304710629582707,
      14.525685528609316
    ],
    [
      3.3081545077513077,
      15.714538814449316
    ],
    [
      4.90517056209175,
      17.560628811799894
    ],
    [
      6.1743723691041055,
      19.709492520148174
    ],
    [
      7.302486357877905,
      21.860760475172913
    ],
    [
      8.898353587408383,
      23.847379279134017
    ],
    [
      11.074814687164343,
      25.144637179946873
    ],
    [
      13.564002342968706,
      25.67667841186811
    ],
    [
      16.086144027017486,
      25.911578014538797
    ],
    [
      18.6065325787566,
      25.98208413937214
    ],
    [
      21.107827596837055,
      25.98142353165104
    ],
    [
      23.6036981868523,
      25.954803879554696
    ],
    [
      26.09890618110384,
      25.907681377099124
    ],
    [
      28.59570990750094,
      25.895099881959446
    ],
    [
      31.09201995929366,
      25.926066791015565
    ],
    [
      33.58732089969146,
      25.827156784347068
    ],
    [
      36.05714459525,
      25.487081683851336
    ],
    [
      38.285978555642615,
      24.3645364957764
    ],
    [
      39.612702136949636,
      22.418594379543215
    ],
    [
      39.99942026140995,
      19.97888893376623
    ],
    [
      40.09655505594921,
      17.48490886704171
    ],
    [
      40.13468923110309,
      14.987816236398018
    ],
    [
      40.153870471517095,
      12.490920426798628
    ],
    [
      40.180377050382454,
      9.994457936879506
    ],
    [
      40.183776095929915,
      7.4982665574609495
    ],
    [
      40.18591860673373,
      5.001989918239088
    ],
    [
      40.211123263015764,
      2.505553853507389
    ],
    [
      40.213751121259676,
      0.009000063718295951
    ],
    [
      40.213976295686656,
      -2.487924447578156
    ],
    [
      40.207865714662134,
      -4.984608417738255
    ],
    [
      40.200757141530126,
      -7.481244320458018
    ],
    [
      40.2114200979743,
      -9.978291035192806
    ],
    [
      40.18202762765594,
      -12.475464805318845
    ],
    [
      40.1372097101262,
      -14.969348734771057
    ],
    [
      40.10263033253364,
      -17.44224112011835
    ],
    [
      40.09606017752269,
      -19.906968450690904
    ],
    [
      40.07736955053268,
      -22.371868429322653
    ],
    [
      40.11601617569426,
      -24.82959255826529
    ],
    [
      40.759394678289624,
      -27.033617170271192
    ],
    [
      42.449658289747155,
      -27.79576434808313
    ],
    [
      43.568955019266724,
      -26.43561499985716
    ],
    [
      43.76999600061379,
      -24.093364270574938
    ],
    [
      43.82087900688986,
      -21.558256622566244
    ],
    [
      43.83830626734371,
      -19.02011818515367
    ],
    [
      43.85037199887378,
      -16.48198128383825
    ],
    [
      43.864016444999535,
      -13.942697992519948
    ],
    [
      43.8759312725532,
      -11.39954770131046
    ],
    [
      43.88104472775271,
      -8.85820857714691
    ],
    [
      43.88376663480817,
      -6.335545871225024
    ],
    [
      43.89328566835077,
      -3.7998938848946144
    ],
    [
      43.90264819750699,
      -1.2595617168415767
    ],
    [
      43.90893552612453,
      1.280659150372826
    ],
    [
      43.89238516328694,
      3.803466083839344
    ],
    [
      43.86702495016992,
      6.234349975296185
    ],
    [
      43.85941691481868,
      8.663607081617
    ],
    [
      43.86409447893798,
      11.186356883121817
    ],
    [
      43.83480946927125,
      13.735134503402385
    ],
    [
      43.76993301925932,
      16.28364784480685
    ],
    [
      43.70273058090797,
      18.830872350644846
    ],
    [
      43.51497074260815,
      21.370062049652603
    ],
    [
      42.93193365665393,
      23.869161782369204
    ],
    [
      41.89587417238978,
      26.20827357957328
    ],
    [
      40.294388606744334,
      27.96623756366473
    ],
    [
      38.22044104583539,
      29.090475593028216
    ],
    [
      35.875369365909584,
      29.617004604198936
    ],
    [
      33.375239867000765,
      29.868191386359523
    ],
    [
      30.838545501277018,
      29.869411164876656
    ],
    [
      28.30132102794503,
      29.699431525752164
    ],
    [
      25.764918223010014,
      29.640348329985034
    ],
    [
      23.258968889879238,
      29.649916514768385
    ],
    [
      20.791786274442508,
      29.66968427365145
    ],
    [
      18.250397149074992,
      29.701769705531404
    ],
    [
      15.705190425172123,
      29.64821638376071
    ],
    [
      13.216019171852484,
      29.484609579602292
    ],
    [
      10.73742420726148,
      29.019150474115477
    ],
    [
      8.257686990677886,
      28.07076915054641
    ],
    [
      6.031821743878025,
      26.584904796634007
    ],
    [
      4.092825305979433,
      24.963653123279656
    ],
    [
      2.419996186001516,
      23.73999790548141
    ],
    [
      0.6654989420614089,
      23.29841832679047
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.43425890587565236,
      0.844574271308958,
      -0.31323075026348257
    ],
    [
      -0.06344476835934214,
      0.3181888765363381,
      0.9459020034952736
    ],
    [
      0.8985510358546758,
      0.4306392214969346,
      -0.0845925343810162
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.34322700500000003,
    0.490113685,
    -0.1164968
  ],
  "construction_scale": 373.733431415935,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
