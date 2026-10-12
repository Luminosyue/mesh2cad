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
    -0.019640555508637542,
    -0.08064043001095297
  ],
  "profile": [
    [
      1.2447029063979471,
      12.691841099738237
    ],
    [
      3.6512334107167317,
      12.689726518382338
    ],
    [
      6.086287795795776,
      12.640254624611192
    ],
    [
      8.520696427888819,
      12.522582768939165
    ],
    [
      10.954073191703195,
      12.381914604538807
    ],
    [
      13.384222776250631,
      12.266479990543898
    ],
    [
      15.743734194174756,
      12.360729840262982
    ],
    [
      17.738123179252337,
      13.320842754835473
    ],
    [
      18.93424136774074,
      15.298680287665654
    ],
    [
      19.59814238356566,
      17.581205697692717
    ],
    [
      20.275205055904323,
      19.8498037086666
    ],
    [
      21.405862434805556,
      22.013780588521062
    ],
    [
      23.28160990361888,
      23.71874614191462
    ],
    [
      25.47680327220774,
      24.997473650637644
    ],
    [
      27.83933196027491,
      25.387888698264142
    ],
    [
      30.2571836430294,
      25.3785634506216
    ],
    [
      32.69451485622126,
      25.2828777522142
    ],
    [
      35.12761370382819,
      25.175190127791574
    ],
    [
      37.42791536334917,
      24.5467795792267
    ],
    [
      38.936322240106165,
      23.011740711478144
    ],
    [
      39.36134565580876,
      20.731063153863214
    ],
    [
      39.464056987135066,
      18.30022507702766
    ],
    [
      39.4456859715774,
      15.863846347807833
    ],
    [
      39.338787641918614,
      13.403010862539746
    ],
    [
      39.22677405599322,
      10.919240195256151
    ],
    [
      39.158781609664715,
      8.436535739308251
    ],
    [
      39.11592307907026,
      5.963648462062781
    ],
    [
      39.0997037445261,
      3.551682806809091
    ],
    [
      39.09940254020776,
      1.1559098436573652
    ],
    [
      39.08762133678876,
      -1.2674824063962735
    ],
    [
      39.08657760707834,
      -3.73439559017804
    ],
    [
      39.09291808667343,
      -6.20330454413517
    ],
    [
      39.10989628859272,
      -8.644564889129924
    ],
    [
      39.12984668886172,
      -11.06388664156448
    ],
    [
      39.13598423426738,
      -13.483251998538229
    ],
    [
      39.13568525859644,
      -15.902715384345914
    ],
    [
      39.10201001900893,
      -18.322082385209395
    ],
    [
      39.134660761270155,
      -20.72547563265303
    ],
    [
      40.04243793349981,
      -22.70330902000439
    ],
    [
      41.90061976738009,
      -22.584458618558813
    ],
    [
      42.64280446157016,
      -20.472953568727704
    ],
    [
      42.66369521671916,
      -18.055859974545193
    ],
    [
      42.638501551854674,
      -15.632953529131367
    ],
    [
      42.62953815542526,
      -13.223253918485547
    ],
    [
      42.63049972728461,
      -10.821048273959814
    ],
    [
      42.62849668198818,
      -8.419233352250112
    ],
    [
      42.617099660264664,
      -6.016813120113879
    ],
    [
      42.61770806565313,
      -3.5794084267096116
    ],
    [
      42.59175427899683,
      -1.1017907438714754
    ],
    [
      42.613933715647775,
      1.377719960087221
    ],
    [
      42.654458297469404,
      3.858825512798334
    ],
    [
      42.68874466092893,
      6.340123030822452
    ],
    [
      42.71507345311416,
      8.813154291731156
    ],
    [
      42.7888199295689,
      11.2596592464215
    ],
    [
      42.89286844000162,
      13.701896247606566
    ],
    [
      42.93179456751315,
      16.143784612126097
    ],
    [
      42.92888884986484,
      18.600109069499858
    ],
    [
      42.88340092251553,
      21.07147597531067
    ],
    [
      42.68168989260107,
      23.495291175384786
    ],
    [
      41.8994919504694,
      25.66343499287863
    ],
    [
      40.30568917893805,
      27.257757483631334
    ],
    [
      38.206328218875356,
      28.238407700153395
    ],
    [
      35.83018971042178,
      28.586504068778147
    ],
    [
      33.41044756055485,
      28.643653980026656
    ],
    [
      30.98527948391395,
      28.724923584400806
    ],
    [
      28.52280817387526,
      28.759290050603415
    ],
    [
      26.041792152458754,
      28.623575521108265
    ],
    [
      23.634971571063183,
      27.99402882273599
    ],
    [
      21.48132875002346,
      26.861030702581292
    ],
    [
      19.58178398368787,
      25.25191536159314
    ],
    [
      17.991868741185293,
      23.22157786438609
    ],
    [
      16.88737268783057,
      21.069424973198863
    ],
    [
      16.19348046612475,
      18.813879008245117
    ],
    [
      15.18655413416164,
      16.740175609346284
    ],
    [
      13.263351103726723,
      15.801731464933013
    ],
    [
      10.945120270531131,
      15.866521387727142
    ],
    [
      8.519710601256294,
      16.039787321136327
    ],
    [
      6.085707141204737,
      16.118945471827242
    ],
    [
      3.65118146726551,
      16.16193862236384
    ],
    [
      1.2448424256631814,
      16.154819203682322
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.433086836683072,
      0.8731341949931655,
      -0.22376878563706568
    ],
    [
      -0.03446255929171521,
      0.23203708891693026,
      0.9720962510852624
    ],
    [
      0.900693135256906,
      0.4287137353766422,
      -0.07040176986760607
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.735729725,
    -0.48413129499999996,
    -0.599267535
  ],
  "construction_scale": 347.056225711487,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
