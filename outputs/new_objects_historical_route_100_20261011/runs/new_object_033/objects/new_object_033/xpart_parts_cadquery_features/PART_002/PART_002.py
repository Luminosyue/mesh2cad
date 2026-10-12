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
    0.0987854815717388,
    -0.6045276731570515
  ],
  "profile": [
    [
      1.7098090143002591,
      -49.99109696739661
    ],
    [
      5.015109482447517,
      -49.984360995143305
    ],
    [
      8.358451182597992,
      -49.966664830210796
    ],
    [
      11.701506519953417,
      -49.92495135166595
    ],
    [
      15.043921676625022,
      -49.853049152538
    ],
    [
      18.385445760063767,
      -49.76007424158643
    ],
    [
      21.72663105528579,
      -49.662501733977095
    ],
    [
      25.067170179720137,
      -49.56835715693309
    ],
    [
      28.408446413084192,
      -49.466004598463286
    ],
    [
      31.750740187706977,
      -49.41618581411261
    ],
    [
      35.08158179845614,
      -49.243688348058924
    ],
    [
      38.169481200313115,
      -48.17108718995195
    ],
    [
      40.42056481138757,
      -45.84267814878254
    ],
    [
      41.40326644648698,
      -42.712557827277934
    ],
    [
      41.41730957937728,
      -39.37916641958894
    ],
    [
      41.248170454359595,
      -36.03790572491609
    ],
    [
      41.181173407948094,
      -32.69446493833669
    ],
    [
      41.15929677874277,
      -29.3501740472174
    ],
    [
      41.145890767398384,
      -26.005637719945497
    ],
    [
      41.12161748075762,
      -22.65979941636214
    ],
    [
      41.08108253006175,
      -19.3102842301572
    ],
    [
      41.05760880274333,
      -15.963033076078638
    ],
    [
      41.038196761978114,
      -12.617506314493578
    ],
    [
      41.03431757613333,
      -9.274078415445501
    ],
    [
      41.03728608411178,
      -5.929309698429597
    ],
    [
      41.028748820499146,
      -2.5788227962831467
    ],
    [
      41.0235256904281,
      0.7700659495046662
    ],
    [
      41.01946919872211,
      4.116535925228088
    ],
    [
      41.00747017853391,
      7.463234593439224
    ],
    [
      40.97307554149717,
      10.809489252127083
    ],
    [
      40.93935543291641,
      14.15558120562544
    ],
    [
      40.959300312984084,
      17.502050605809313
    ],
    [
      40.98880268629707,
      20.843858014945358
    ],
    [
      40.99066654290817,
      24.182322472842742
    ],
    [
      40.98598550188264,
      27.5223502272079
    ],
    [
      40.97178258334718,
      30.87227383385945
    ],
    [
      40.997526083998224,
      34.22541228005923
    ],
    [
      41.081921999657894,
      37.5768587012214
    ],
    [
      41.20960234616896,
      40.919169635369826
    ],
    [
      41.45862808040093,
      44.24794053939283
    ],
    [
      41.73654257397221,
      47.52420103550247
    ],
    [
      40.47784399634784,
      49.0073120407489
    ],
    [
      38.92097768747911,
      46.62289380288096
    ],
    [
      38.20610534315887,
      43.37202985779665
    ],
    [
      37.80574369483135,
      40.05221315494548
    ],
    [
      37.49580292036889,
      36.71794155383152
    ],
    [
      37.26197147713012,
      33.377866795842934
    ],
    [
      37.08029114040158,
      30.03125119340276
    ],
    [
      36.95366063145537,
      26.681452057418802
    ],
    [
      36.92588176339284,
      23.330407573322624
    ],
    [
      36.94158066163145,
      19.979708531839613
    ],
    [
      36.98598724256955,
      16.62945609277768
    ],
    [
      37.066983327335166,
      13.284633329456959
    ],
    [
      37.16656505601838,
      9.946971768705751
    ],
    [
      37.27262228850583,
      6.608763102671616
    ],
    [
      37.37186735367642,
      3.2658548204720814
    ],
    [
      37.46852873976037,
      -0.07819727757265148
    ],
    [
      37.53321890448492,
      -3.4225570691823455
    ],
    [
      37.586434513949754,
      -6.766843623556747
    ],
    [
      37.67899366819495,
      -10.11115670224168
    ],
    [
      37.77472826776056,
      -13.451589397879605
    ],
    [
      37.856518856133476,
      -16.786720267609226
    ],
    [
      37.949399849370366,
      -20.12060508996685
    ],
    [
      38.02409933856832,
      -23.453295549595765
    ],
    [
      38.113455814995504,
      -26.78709375166315
    ],
    [
      38.2049025340507,
      -30.122585347626714
    ],
    [
      38.28321068481957,
      -33.460072132976
    ],
    [
      38.357068839975,
      -36.79572359744536
    ],
    [
      37.794056357539006,
      -39.87666512121565
    ],
    [
      35.0959854704301,
      -41.00997377220763
    ],
    [
      31.762329564855115,
      -41.0500217335114
    ],
    [
      28.41901558243245,
      -41.04832969152486
    ],
    [
      25.07565754974426,
      -41.044119876769756
    ],
    [
      21.732300676371537,
      -41.04544168868394
    ],
    [
      18.38888937895384,
      -41.046042055552185
    ],
    [
      15.045496054749126,
      -41.045699457357344
    ],
    [
      11.702086887096367,
      -41.0463056707171
    ],
    [
      8.358638423357334,
      -41.04638557591029
    ],
    [
      5.015195261294625,
      -41.04688276186742
    ],
    [
      1.7098357369990984,
      -41.04530096847898
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
    -0.137955025,
    0.007876065000000015,
    -0.003083200000000008
  ],
  "construction_scale": 125.2101072553535,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
