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
    2.0888001527514293,
    -0.059109653365176575
  ],
  "profile": [
    [
      1.0670868462262415,
      -29.041143458900283
    ],
    [
      3.101860283240293,
      -29.415064483194257
    ],
    [
      5.105580978826143,
      -30.108427249066107
    ],
    [
      7.111655773976996,
      -30.937538415742907
    ],
    [
      9.106449650535865,
      -31.81450997579728
    ],
    [
      11.094493999881436,
      -32.58109113338024
    ],
    [
      13.063615325993872,
      -33.20481289791389
    ],
    [
      15.012095993464095,
      -33.882270815391614
    ],
    [
      16.969540201405955,
      -34.62173700649003
    ],
    [
      18.973123763752838,
      -35.344776958233055
    ],
    [
      20.961389804415738,
      -36.05389006629658
    ],
    [
      22.968426252005717,
      -36.64567222170741
    ],
    [
      25.04825095984599,
      -37.086335155221285
    ],
    [
      27.127561987727816,
      -37.34974588734056
    ],
    [
      29.19830404671972,
      -37.43978823384937
    ],
    [
      31.25672986754187,
      -37.58020779954198
    ],
    [
      33.37648034770142,
      -37.83008999744642
    ],
    [
      35.507326455188284,
      -38.1034141931988
    ],
    [
      37.65641673952793,
      -38.31500771821023
    ],
    [
      39.67523786232397,
      -38.239359220217175
    ],
    [
      41.73050989297565,
      -38.01815430296067
    ],
    [
      43.572291077429256,
      -37.21341245353055
    ],
    [
      44.87379485888537,
      -35.549095547126264
    ],
    [
      45.78395816688155,
      -33.552604438021916
    ],
    [
      46.54687257447026,
      -31.500534587350977
    ],
    [
      47.13177910537679,
      -29.53099211616956
    ],
    [
      47.43050912882597,
      -27.456416627280046
    ],
    [
      47.4673311707882,
      -25.3169681939118
    ],
    [
      47.49846654769357,
      -23.168630299977025
    ],
    [
      47.54824958327477,
      -21.02148944104882
    ],
    [
      47.5465911648263,
      -18.888830025649128
    ],
    [
      47.55785244374154,
      -16.76404062524096
    ],
    [
      47.569397452171195,
      -14.639453157950484
    ],
    [
      47.57444253504505,
      -12.508343006945196
    ],
    [
      47.585430286988824,
      -10.35829333369798
    ],
    [
      47.594699415861186,
      -8.205404748978959
    ],
    [
      47.60848872509435,
      -6.05231562668245
    ],
    [
      47.62893074719838,
      -3.899378950868414
    ],
    [
      47.651853061241724,
      -1.7463969934868908
    ],
    [
      47.66460959486001,
      0.4065647307943337
    ],
    [
      47.668381716671036,
      2.5595154357213854
    ],
    [
      47.65465719420354,
      4.712633345611292
    ],
    [
      47.64667638756072,
      6.865680973541044
    ],
    [
      47.64391801596104,
      9.018709087716976
    ],
    [
      47.637626510604406,
      11.171772499971365
    ],
    [
      47.629424001688946,
      13.324760700482704
    ],
    [
      47.618343566846434,
      15.477606534944835
    ],
    [
      47.61525767936753,
      17.630586393423727
    ],
    [
      47.59511653270722,
      19.783703770695382
    ],
    [
      47.58469712329513,
      21.93688164405183
    ],
    [
      47.584872079565656,
      24.090201760906268
    ],
    [
      47.59196265242345,
      26.24345399862058
    ],
    [
      47.594901659772276,
      28.39647485218116
    ],
    [
      47.565084225460275,
      30.5485248859069
    ],
    [
      47.55321658812393,
      32.69097354329138
    ],
    [
      47.48163551253316,
      34.70020235945755
    ],
    [
      46.869432146689206,
      35.881256035567496
    ],
    [
      45.05550414339691,
      36.04972340899417
    ],
    [
      43.012448564118685,
      35.8617480933316
    ],
    [
      40.92713938631375,
      35.59925502822599
    ],
    [
      38.8706261567326,
      35.28855169292929
    ],
    [
      36.819623503595004,
      34.94652725475477
    ],
    [
      34.70685799014227,
      34.476681441214126
    ],
    [
      32.6025143791585,
      33.851572423641045
    ],
    [
      30.542515907677487,
      33.07917098769168
    ],
    [
      28.408120393142852,
      32.46812808811846
    ],
    [
      26.29911793739757,
      31.94453326457371
    ],
    [
      24.318057894038194,
      31.6110503017154
    ],
    [
      22.346375363860677,
      31.203025795058004
    ],
    [
      20.383112962866953,
      30.43441889935692
    ],
    [
      18.545066643864544,
      29.513204951931236
    ],
    [
      16.765458056587573,
      28.52074275696196
    ],
    [
      15.002019580809304,
      27.406467511884685
    ],
    [
      13.210208334509796,
      26.304191179251255
    ],
    [
      11.342918933515612,
      25.210601583881367
    ],
    [
      9.427299829001917,
      24.25317484908803
    ],
    [
      7.431587126278863,
      23.371803120699973
    ],
    [
      5.34284931991785,
      22.702640000953608
    ],
    [
      3.216499837778372,
      22.231559729946625
    ],
    [
      1.0992317665455096,
      21.98525523119192
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
    -0.034162665000000036,
    0.03609146999999996,
    -0.28011296
  ],
  "construction_scale": 56.23800910744189,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
