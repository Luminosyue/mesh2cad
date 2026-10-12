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
    0.034998114092466094,
    0.02240301220232029
  ],
  "profile": [
    [
      0.8385207777048345,
      -19.284562551132694
    ],
    [
      2.4594818844042177,
      -19.28411961726783
    ],
    [
      4.099106915383892,
      -19.28598776012586
    ],
    [
      5.738743310333978,
      -19.284033383335945
    ],
    [
      7.378397682850233,
      -19.293574185690243
    ],
    [
      9.018018659651876,
      -19.298464667887572
    ],
    [
      10.657620629680324,
      -19.306456490098014
    ],
    [
      12.29718910738874,
      -19.31432662301876
    ],
    [
      13.936788989575236,
      -19.319533489292695
    ],
    [
      15.57636334402962,
      -19.32111593711473
    ],
    [
      17.21595409896001,
      -19.32129385796243
    ],
    [
      18.855551670557016,
      -19.32647432741272
    ],
    [
      20.49512824026334,
      -19.33696664188311
    ],
    [
      22.134489252860746,
      -19.34608005501218
    ],
    [
      23.773504761786434,
      -19.354328468307692
    ],
    [
      25.413123498422095,
      -19.3522649240971
    ],
    [
      27.052767219001307,
      -19.34933722190509
    ],
    [
      28.692364879276425,
      -19.356147368353316
    ],
    [
      30.33178201957149,
      -19.36594909633464
    ],
    [
      31.971191506842267,
      -19.376544005902204
    ],
    [
      33.61063097137826,
      -19.377016160604406
    ],
    [
      35.25016000457125,
      -19.377224561078364
    ],
    [
      36.88976210837963,
      -19.372990359637104
    ],
    [
      38.529348546632136,
      -19.360692475451756
    ],
    [
      40.16877322227417,
      -19.338665443146922
    ],
    [
      41.803280482005476,
      -19.230624048451926
    ],
    [
      43.39495285610956,
      -18.896432645380116
    ],
    [
      44.902091455911986,
      -18.30767916391979
    ],
    [
      46.285527170866736,
      -17.469430885678946
    ],
    [
      47.48720509825703,
      -16.353641584039682
    ],
    [
      48.435290320885755,
      -14.99480868005764
    ],
    [
      49.14330322185188,
      -13.509536333040096
    ],
    [
      49.54611028558382,
      -11.939580643435026
    ],
    [
      49.7759351031818,
      -10.320596813328482
    ],
    [
      49.870258546100516,
      -8.681594220266307
    ],
    [
      49.87045009171119,
      -7.037551034169806
    ],
    [
      49.846853393461714,
      -5.392677990757141
    ],
    [
      49.840374655038495,
      -3.747752224578054
    ],
    [
      49.852248270716856,
      -2.103323179788949
    ],
    [
      49.87886078947076,
      -0.4622096571330693
    ],
    [
      49.89640976691285,
      1.1780607270664598
    ],
    [
      49.895053088771405,
      2.8176740993544547
    ],
    [
      49.88587051217503,
      4.454353305924128
    ],
    [
      49.870190272920006,
      6.090513801905097
    ],
    [
      49.86393360175773,
      7.727317859043737
    ],
    [
      49.858461647742466,
      9.364137928276909
    ],
    [
      49.734599772956585,
      10.996392098231633
    ],
    [
      49.45364608992212,
      12.603653495719804
    ],
    [
      48.96555099805189,
      14.148274200168045
    ],
    [
      48.21969049625501,
      15.589653955650771
    ],
    [
      47.1881371872597,
      16.871102610641838
    ],
    [
      45.926395428591135,
      17.90213346437122
    ],
    [
      44.46962046955588,
      18.623714093072667
    ],
    [
      42.90030523475076,
      19.041809388196917
    ],
    [
      41.27822256444185,
      19.26187833980743
    ],
    [
      39.648147335227996,
      19.3428399274922
    ],
    [
      38.013574809561476,
      19.38845819329783
    ],
    [
      36.37771957805029,
      19.396504560925553
    ],
    [
      34.740535944363444,
      19.406682885769712
    ],
    [
      33.103246612315125,
      19.40609780298331
    ],
    [
      31.46594869052403,
      19.404542615186163
    ],
    [
      29.82820600356665,
      19.394220491324862
    ],
    [
      28.18727531254838,
      19.375096422382907
    ],
    [
      26.545505111886584,
      19.37199435161056
    ],
    [
      24.908354725079754,
      19.388876296606266
    ],
    [
      23.2718648582025,
      19.415311214498303
    ],
    [
      21.630985449773206,
      19.455265472546678
    ],
    [
      19.989782185819347,
      19.447770761128165
    ],
    [
      18.348765548069682,
      19.408165974245012
    ],
    [
      16.70741568445061,
      19.389453456002897
    ],
    [
      15.067770954492376,
      19.396959137289766
    ],
    [
      13.435236845355192,
      19.349978654222866
    ],
    [
      11.80614461022909,
      19.210442244145334
    ],
    [
      10.300564834564447,
      18.619137518461233
    ],
    [
      8.896252750605626,
      17.84718003005056
    ],
    [
      7.346268110042004,
      17.401254826525623
    ],
    [
      5.723394847127171,
      17.233053085631568
    ],
    [
      4.090800648083244,
      17.153751946940858
    ],
    [
      2.4560876523465,
      17.11536163101686
    ],
    [
      0.8377231973743526,
      17.100301430838556
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.02555040488422617,
      0.9527942760975205,
      -0.3025396573113261
    ],
    [
      -0.008346467313843463,
      0.3024245881746612,
      0.953136771376892
    ],
    [
      0.9996386913748543,
      0.026878167779614087,
      0.00022539560745714636
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.42143035,
    0.430363005,
    -0.50196222
  ],
  "construction_scale": 149.40260546490526,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
