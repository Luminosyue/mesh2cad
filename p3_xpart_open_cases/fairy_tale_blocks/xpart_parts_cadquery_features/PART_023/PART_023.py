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
    0.0577527576598462,
    -0.058049485960622156
  ],
  "profile": [
    [
      0.9801124367856124,
      -49.81757234207812
    ],
    [
      2.8747738821428195,
      -49.81795401058854
    ],
    [
      4.79124384797131,
      -49.81542571020812
    ],
    [
      6.707786143067283,
      -49.816354620347624
    ],
    [
      8.624329349542265,
      -49.81336077341395
    ],
    [
      10.540872390712291,
      -49.81222262253409
    ],
    [
      12.457369532032429,
      -49.814996825143496
    ],
    [
      14.373867690566865,
      -49.820546073814356
    ],
    [
      16.29043657530861,
      -49.817927049204776
    ],
    [
      18.206954569662205,
      -49.824304681223474
    ],
    [
      20.123486493633504,
      -49.832554662501224
    ],
    [
      22.039871148213827,
      -49.83540722608947
    ],
    [
      23.956301881855296,
      -49.847187112292374
    ],
    [
      25.864110559361208,
      -49.83891570634682
    ],
    [
      27.435038282613824,
      -49.12843768009131
    ],
    [
      27.86935993248772,
      -47.38766741638032
    ],
    [
      27.8439547681016,
      -45.473557490226895
    ],
    [
      27.81773725566129,
      -43.55732760322995
    ],
    [
      27.797738159142938,
      -41.641091138481045
    ],
    [
      27.789670780812777,
      -39.724930797910055
    ],
    [
      27.78949128441788,
      -37.808702288392496
    ],
    [
      27.785090351920818,
      -35.89246818868065
    ],
    [
      27.78571898270734,
      -33.97623366599707
    ],
    [
      27.78215903045239,
      -32.05997545562691
    ],
    [
      27.780457746778357,
      -30.143718420754077
    ],
    [
      27.782778295475087,
      -28.22744839796523
    ],
    [
      27.773801055395325,
      -26.31124390373939
    ],
    [
      27.75389532909543,
      -24.394989005125534
    ],
    [
      27.737147307144156,
      -22.478714256791534
    ],
    [
      27.736883083707824,
      -20.562474205251803
    ],
    [
      27.740576479635216,
      -18.64631961885658
    ],
    [
      27.7547599153852,
      -16.730121890764703
    ],
    [
      27.758806384309484,
      -14.81383058868374
    ],
    [
      27.763729192831782,
      -12.89755678274338
    ],
    [
      27.757509505213143,
      -10.981319169788446
    ],
    [
      27.753314929557675,
      -9.06513909418933
    ],
    [
      27.7467103550521,
      -7.148971458938818
    ],
    [
      27.74838905513929,
      -5.23272867099387
    ],
    [
      27.7492459475948,
      -3.3164409267383217
    ],
    [
      27.754519097897735,
      -1.4001520302597394
    ],
    [
      27.754358445944767,
      0.5161134064279945
    ],
    [
      27.754100559226885,
      2.432349251352355
    ],
    [
      27.7482801926232,
      4.348619633167822
    ],
    [
      27.751405954327367,
      6.264873182941052
    ],
    [
      27.7558407104922,
      8.181037572662362
    ],
    [
      27.75445352387392,
      10.097227938173575
    ],
    [
      27.7527741887047,
      12.013320638709029
    ],
    [
      27.748829522977175,
      13.929422127951465
    ],
    [
      27.736813147105188,
      15.845512639810163
    ],
    [
      27.72563894537379,
      17.761599314489523
    ],
    [
      27.71531255542608,
      19.67763042712547
    ],
    [
      27.710720852418124,
      21.593721952461692
    ],
    [
      27.707360497499323,
      23.50979722567086
    ],
    [
      27.703979066323853,
      25.42586199838926
    ],
    [
      27.701705271195223,
      27.341913856622114
    ],
    [
      27.69890281565299,
      29.25810113321848
    ],
    [
      27.70192483696618,
      31.174330090521387
    ],
    [
      27.70914173166095,
      33.09050318053356
    ],
    [
      27.7138927593178,
      35.00673444911311
    ],
    [
      27.704842615367053,
      36.923001083232805
    ],
    [
      27.70996558608201,
      38.83927374488418
    ],
    [
      27.708607399648084,
      40.75554851503168
    ],
    [
      27.716139689509436,
      42.671737569340806
    ],
    [
      27.713914490605674,
      44.58783753048268
    ],
    [
      27.62272144338509,
      46.49803672203301
    ],
    [
      27.109194004769734,
      48.28190650147771
    ],
    [
      25.788964804493695,
      49.46405696354889
    ],
    [
      23.95440523034955,
      49.8220233015134
    ],
    [
      22.040202051919678,
      49.85012776826628
    ],
    [
      20.123648440985193,
      49.848530485981485
    ],
    [
      18.207098401291162,
      49.849004529909905
    ],
    [
      16.290542664319442,
      49.85607608454373
    ],
    [
      14.374006037447657,
      49.85157814619502
    ],
    [
      12.457467537741099,
      49.847925562130044
    ],
    [
      10.540910065461691,
      49.85152254959753
    ],
    [
      8.624343832602412,
      49.84428281089997
    ],
    [
      6.707862841466676,
      49.84160638323272
    ],
    [
      4.7913969235145455,
      49.846004331668595
    ],
    [
      2.8748378583106855,
      49.84699442447541
    ],
    [
      0.9801086879814201,
      49.850127594835044
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.9520460248982093,
      0.3056181647942947,
      0.01434934922865803
    ],
    [
      0.3056440089730302,
      -0.9521457723874017,
      0.0004097605309017577
    ],
    [
      0.013787902466036533,
      0.0039956817397958835,
      -0.9998969588277693
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.672527815,
    0.77077657,
    -0.57699939
  ],
  "construction_scale": 198.41565890030742,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
