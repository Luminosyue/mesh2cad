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
    0.009322169134399923,
    0.0020178534276016563
  ],
  "profile": [
    [
      0.14953757292148623,
      -49.92146013498453
    ],
    [
      0.8217750018381575,
      -49.19348845677386
    ],
    [
      0.9596541079962544,
      -47.96955156510705
    ],
    [
      0.9537876889844044,
      -46.70740736920155
    ],
    [
      0.9526413582772468,
      -45.445042074534065
    ],
    [
      0.953984769848695,
      -44.182682675263365
    ],
    [
      0.9539843390256009,
      -42.92031736055124
    ],
    [
      0.9520819408977792,
      -41.65795364455873
    ],
    [
      0.9516039388963154,
      -40.39559513125833
    ],
    [
      0.9521800444188369,
      -39.13325495076162
    ],
    [
      0.9529671116570602,
      -37.87090069669114
    ],
    [
      0.9544638314494163,
      -36.6085426933804
    ],
    [
      0.954651623933048,
      -35.346290154464945
    ],
    [
      0.9559605854350673,
      -34.084061436608145
    ],
    [
      0.9570339195175794,
      -32.821828791076165
    ],
    [
      0.9559446962883283,
      -31.55961086252284
    ],
    [
      0.9546057305713412,
      -30.29737683267145
    ],
    [
      0.9545761932165804,
      -29.035158659797013
    ],
    [
      0.9537569453141881,
      -27.7728850745238
    ],
    [
      0.9543410674576124,
      -26.510518699603857
    ],
    [
      0.9548673453866219,
      -25.24813757837015
    ],
    [
      0.9556229139342229,
      -23.985764172219092
    ],
    [
      0.9548570890083526,
      -22.72343319872759
    ],
    [
      0.9529433003086474,
      -21.461337002775295
    ],
    [
      0.9507701425948396,
      -20.199087496081155
    ],
    [
      0.9516535450409317,
      -18.936693431817197
    ],
    [
      0.9522200837539787,
      -17.67448693976955
    ],
    [
      0.9525226449635014,
      -16.412318984678045
    ],
    [
      0.9525600541015858,
      -15.150155951636327
    ],
    [
      0.9533287880036534,
      -13.887997176994798
    ],
    [
      0.9530063546642094,
      -12.62557766750956
    ],
    [
      0.9523831348243408,
      -11.362692863047805
    ],
    [
      0.9511570782375061,
      -10.099475344824913
    ],
    [
      0.9520057491822677,
      -8.836401354519335
    ],
    [
      0.9521214059038291,
      -7.573281244991833
    ],
    [
      0.9515176895117206,
      -6.3104139100841135
    ],
    [
      0.9513724694125438,
      -5.048071057573763
    ],
    [
      0.9507641626070069,
      -3.785837300428603
    ],
    [
      0.9516447726624557,
      -2.5234111462939985
    ],
    [
      0.9508353116768347,
      -1.2608697482435822
    ],
    [
      0.9508727494762036,
      0.001379508935470726
    ],
    [
      0.9512637249164412,
      1.2636154442445808
    ],
    [
      0.9519751553650613,
      2.5258565910817783
    ],
    [
      0.9510463568033758,
      3.7881275112960204
    ],
    [
      0.9510616472390031,
      5.050390051149197
    ],
    [
      0.9518855760735081,
      6.312651427732329
    ],
    [
      0.9522311277643702,
      7.574928960711624
    ],
    [
      0.9514573094678396,
      8.837181258574795
    ],
    [
      0.9498497333388594,
      10.099449216798085
    ],
    [
      0.951305890666429,
      11.36170496647576
    ],
    [
      0.9519209541967192,
      12.623964313028006
    ],
    [
      0.9511343800887093,
      13.88624492240865
    ],
    [
      0.9507889521444637,
      15.148518144576796
    ],
    [
      0.952325078304382,
      16.41078791495689
    ],
    [
      0.9526439751949927,
      17.67308583358448
    ],
    [
      0.9515543212346991,
      18.935390740038144
    ],
    [
      0.9498972387624329,
      20.197672516931853
    ],
    [
      0.9521068975148652,
      21.459958632920987
    ],
    [
      0.9531449509563199,
      22.72225151016452
    ],
    [
      0.9532838407082982,
      23.9845697714892
    ],
    [
      0.953437928138528,
      25.246861529868937
    ],
    [
      0.9542684265175049,
      26.509158712387105
    ],
    [
      0.9536398828360985,
      27.771443354424804
    ],
    [
      0.9528846741153019,
      29.033775138107302
    ],
    [
      0.9517752372544435,
      30.296106210257122
    ],
    [
      0.9534587446774145,
      31.558407097781085
    ],
    [
      0.9530656303178917,
      32.82073837916198
    ],
    [
      0.9536814530055759,
      34.083097566520124
    ],
    [
      0.9539008942907299,
      35.345421328825154
    ],
    [
      0.9539971221815742,
      36.60775327163596
    ],
    [
      0.9526872034607712,
      37.870098226188794
    ],
    [
      0.9522221925962542,
      39.132416087486185
    ],
    [
      0.9522979659780352,
      40.39476381742287
    ],
    [
      0.9519233460932588,
      41.6571336191717
    ],
    [
      0.9504683149581727,
      42.91950385504073
    ],
    [
      0.950578756071583,
      44.18186469822617
    ],
    [
      0.9498588332919966,
      45.44423033174411
    ],
    [
      0.9517770651837718,
      46.706574089297625
    ],
    [
      0.9599747082718031,
      47.96871440049524
    ],
    [
      0.8190823714979879,
      49.19278147921922
    ],
    [
      0.14938480164584386,
      49.92319461006355
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
    -0.0025135649999999954,
    0.77736333,
    0.11465124
  ],
  "construction_scale": 40.87112937683662,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
