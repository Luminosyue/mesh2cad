"""Editable CadQuery sketch/feature reconstruction. Approximate inferred design.
Run with Python + cadquery. No mesh or other input files required.
"""
from pathlib import Path
import json
"""Pure CadQuery feature builder. Input contains sketches, never a triangle mesh."""
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp=cq.Workplane('XY',origin=(0,0,z))
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
            features.append((shape,feature.get('cut',False)))
        shape=features[0][0]
        for addition,cut in features[1:]:
            shape=shape.cut(addition) if cut else shape.fuse(addition)
        shape=shape.clean()
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS = json.loads(r'''
{
  "center_xy": [
    0.09007631462999678,
    -0.8750819170975184
  ],
  "profile": [
    [
      1.0546042724489886,
      -29.325643842216387
    ],
    [
      3.0932254085839945,
      -29.3104981082843
    ],
    [
      5.15544195577075,
      -29.316860038139453
    ],
    [
      7.217662478519547,
      -29.319406271417925
    ],
    [
      9.279819338090238,
      -29.335383780433375
    ],
    [
      11.34192425246533,
      -29.338319533286736
    ],
    [
      13.4040679340219,
      -29.33604292230575
    ],
    [
      15.466229369754574,
      -29.341120105122503
    ],
    [
      17.528502306927056,
      -29.349329836024495
    ],
    [
      19.59072055422653,
      -29.362356209492702
    ],
    [
      21.65293088990586,
      -29.374336137577483
    ],
    [
      23.71516695021023,
      -29.377437372384694
    ],
    [
      25.777408945152857,
      -29.385092591956706
    ],
    [
      27.8396340747246,
      -29.397481730551352
    ],
    [
      29.901832925787787,
      -29.40926748647096
    ],
    [
      31.964070891557213,
      -29.421781485321958
    ],
    [
      34.02626376454371,
      -29.43296975697785
    ],
    [
      36.08841123186076,
      -29.45604264569964
    ],
    [
      38.15034419431478,
      -29.48836059248919
    ],
    [
      40.21202719252301,
      -29.529000764831597
    ],
    [
      42.2725993056461,
      -29.558053278780818
    ],
    [
      44.320890883752675,
      -29.416577068565623
    ],
    [
      46.19762532171566,
      -28.782575535557946
    ],
    [
      47.48686550381359,
      -27.41103776559956
    ],
    [
      48.34606059048911,
      -25.567497763788992
    ],
    [
      48.64896858796203,
      -23.54387324134416
    ],
    [
      48.7883130908899,
      -21.49221100144736
    ],
    [
      48.84133149661422,
      -19.436160006466178
    ],
    [
      48.874492109769264,
      -17.379653103110805
    ],
    [
      48.925387491952115,
      -15.323074748762396
    ],
    [
      48.998861184770846,
      -13.26094686422548
    ],
    [
      49.07079750538844,
      -11.193380680812417
    ],
    [
      49.10843875326805,
      -9.126362408050188
    ],
    [
      49.0020964921345,
      -7.0754765990331325
    ],
    [
      48.54063997219927,
      -5.075594300759464
    ],
    [
      47.80285195759484,
      -3.1695676359797598
    ],
    [
      46.72233711929441,
      -1.4055117093303824
    ],
    [
      45.69137161843206,
      0.34048656112986747
    ],
    [
      45.84921805252051,
      2.1903503956352113
    ],
    [
      46.9895194954333,
      3.698734282013298
    ],
    [
      48.27350081188703,
      5.203437469212343
    ],
    [
      48.82277665149905,
      7.091384264153211
    ],
    [
      48.941691149421175,
      9.125075427422878
    ],
    [
      48.940131217035805,
      11.175669306749452
    ],
    [
      48.921256080819845,
      13.234975405318247
    ],
    [
      48.89424703487981,
      15.295972333078149
    ],
    [
      48.86384669047439,
      17.356997918090617
    ],
    [
      48.853186515355254,
      19.420089957931115
    ],
    [
      48.83098141462409,
      21.486506014908286
    ],
    [
      48.75649519987509,
      23.548289551253546
    ],
    [
      48.44983161461297,
      25.57159705383959
    ],
    [
      47.64989188317364,
      27.35309775376062
    ],
    [
      46.199732670280156,
      28.680148672426572
    ],
    [
      44.38074232027865,
      29.389862656102373
    ],
    [
      42.365902375018536,
      29.61436949862731
    ],
    [
      40.32478164552233,
      29.576476239432537
    ],
    [
      38.30575896602684,
      29.283458574063317
    ],
    [
      36.41182407584764,
      28.545706652584492
    ],
    [
      34.82248270182991,
      27.27560293544575
    ],
    [
      33.612013086811416,
      25.634472042272463
    ],
    [
      32.63611023899297,
      23.80397744917171
    ],
    [
      31.695691293159896,
      21.962848159517335
    ],
    [
      30.387398536092924,
      20.585447258551525
    ],
    [
      28.5075569203167,
      20.330572045528825
    ],
    [
      26.50897023111505,
      20.661440113668224
    ],
    [
      24.48281143768242,
      20.70841003872295
    ],
    [
      22.491140989507322,
      20.25670321557982
    ],
    [
      20.52787445642192,
      19.55018460632595
    ],
    [
      18.60316225473783,
      18.725240371141098
    ],
    [
      16.646238065028154,
      18.17000603502417
    ],
    [
      14.69045382489314,
      18.220200323757346
    ],
    [
      13.09091095242983,
      19.299712794458408
    ],
    [
      11.789896510404168,
      20.92845550361363
    ],
    [
      10.575238890160655,
      22.618895189095117
    ],
    [
      9.398277909172984,
      24.30800315289194
    ],
    [
      8.119709523393432,
      25.92034376791343
    ],
    [
      6.632922794866634,
      27.315247186607117
    ],
    [
      4.937302600552172,
      28.456549815227206
    ],
    [
      3.047375154657475,
      29.217235618924963
    ],
    [
      1.0463754359061577,
      29.541533537521605
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "center": [
    -0.24093256890773773,
    -0.5688102096319199,
    0.3099321722984314
  ],
  "construction_scale": 527.2777472138505
}
''')

def build():
    return build_model(PARAMETERS)

if __name__ == "__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==1
    cq.exporters.export(result,str(Path(__file__).with_suffix(".step")))
