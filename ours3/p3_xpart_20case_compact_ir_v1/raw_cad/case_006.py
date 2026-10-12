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
    -0.4577901919661443,
    -0.3511397173103672
  ],
  "profile": [
    [
      0.13431282670627778,
      7.19528663739193
    ],
    [
      0.5253561236576287,
      5.7380691152777645
    ],
    [
      0.5392042809871314,
      3.7405356013722004
    ],
    [
      0.5355050426791561,
      1.7327653375313827
    ],
    [
      0.5281833487946423,
      -0.27593293643426675
    ],
    [
      0.5266872856997664,
      -2.283533620858497
    ],
    [
      0.526168681695347,
      -4.289530532401183
    ],
    [
      0.5273944347124575,
      -6.295032067237859
    ],
    [
      0.5244479530806994,
      -8.297886235862743
    ],
    [
      0.5259498328533585,
      -10.300197940564779
    ],
    [
      0.5269684946426823,
      -12.303891658717959
    ],
    [
      0.5243055103903467,
      -14.3093115583647
    ],
    [
      0.5190986813789928,
      -16.31480676117684
    ],
    [
      0.5156583483346797,
      -18.3203004685007
    ],
    [
      0.5133783585366686,
      -20.32578974034884
    ],
    [
      0.5128159934581005,
      -22.331267149721462
    ],
    [
      0.5132675552868202,
      -24.335988457189863
    ],
    [
      0.5213261530319466,
      -26.33938478234211
    ],
    [
      0.5255689117195862,
      -28.343224099487912
    ],
    [
      0.5259776770567438,
      -30.347189519433137
    ],
    [
      0.5195745689556545,
      -32.351179178748055
    ],
    [
      0.5120684544252253,
      -34.355130176612036
    ],
    [
      0.5087917353156338,
      -36.35912876922238
    ],
    [
      0.5067707339497154,
      -38.36311225058991
    ],
    [
      0.5061924571667198,
      -40.36719744158496
    ],
    [
      0.50283331139726,
      -42.372200620115215
    ],
    [
      0.5049587549627496,
      -44.37768000840089
    ],
    [
      0.5059750827953213,
      -46.383103849460156
    ],
    [
      0.5279678540500874,
      -48.377316718209684
    ],
    [
      1.1526544327366688,
      -49.602868163629125
    ],
    [
      1.6821839175243183,
      -48.2709105417166
    ],
    [
      1.695648297410433,
      -46.274248664677096
    ],
    [
      1.6977587727203347,
      -44.270363815359936
    ],
    [
      1.700768297919295,
      -42.26770314513239
    ],
    [
      1.7073367364708685,
      -40.26523842320944
    ],
    [
      1.7112623761172674,
      -38.262759656124345
    ],
    [
      1.7141216959076169,
      -36.26016502240212
    ],
    [
      1.714009470010124,
      -34.25757332021228
    ],
    [
      1.715731509893298,
      -32.255016540804846
    ],
    [
      1.7223008361609597,
      -30.252414031364797
    ],
    [
      1.7199185133667725,
      -28.249173399218193
    ],
    [
      1.7191547101036733,
      -26.245363197890896
    ],
    [
      1.7204417241051813,
      -24.240979186251757
    ],
    [
      1.7201770849944615,
      -22.236483416388445
    ],
    [
      1.7201968391499873,
      -20.23196730992401
    ],
    [
      1.7206216257840774,
      -18.227444988386942
    ],
    [
      1.719481648346504,
      -16.22297280149163
    ],
    [
      1.7221710161199812,
      -14.218485840727567
    ],
    [
      1.7210078254791732,
      -12.214032959691423
    ],
    [
      1.7223079502044691,
      -10.209593790399783
    ],
    [
      1.7211095238630003,
      -8.205100135075273
    ],
    [
      1.7227150556168747,
      -6.200607104866435
    ],
    [
      1.724479506552865,
      -4.19613333526128
    ],
    [
      1.7273052379071112,
      -2.1916660271925674
    ],
    [
      1.7291753991100718,
      -0.18720076410182884
    ],
    [
      1.7314513124089457,
      1.817303489609889
    ],
    [
      1.7336871147905326,
      3.8218192075427444
    ],
    [
      1.7384423681023753,
      5.826107160213281
    ],
    [
      1.8161778346416826,
      7.8240880880318135
    ],
    [
      1.8481683593819778,
      9.822632041583795
    ],
    [
      1.762802200815965,
      11.775292529332818
    ],
    [
      1.7307615530328497,
      13.762024326834652
    ],
    [
      1.7315999150403445,
      15.766221788430204
    ],
    [
      1.7318775508531172,
      17.77059514370895
    ],
    [
      1.731780706032382,
      19.77495823165357
    ],
    [
      1.7326113137964847,
      21.779259182471094
    ],
    [
      1.7315966637960436,
      23.783579955480082
    ],
    [
      1.7331314346507014,
      25.787969448247402
    ],
    [
      1.7355059978404759,
      27.792322197307783
    ],
    [
      1.7376521228505812,
      29.796621330396853
    ],
    [
      1.7370811756180404,
      31.80095138483199
    ],
    [
      1.7382873440791817,
      33.80529144040179
    ],
    [
      1.7409069299075228,
      35.809608527483775
    ],
    [
      1.738452061497517,
      37.813962846145586
    ],
    [
      1.7382218409046115,
      39.81834854828915
    ],
    [
      1.7419559166767602,
      41.82273164116602
    ],
    [
      1.7407411977329432,
      43.827094626006996
    ],
    [
      1.73238027106663,
      45.83140452642665
    ],
    [
      1.7188111944965327,
      47.83474320287225
    ],
    [
      1.3948776413694666,
      49.52848937783136
    ],
    [
      0.20448076276019253,
      49.39188133452595
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
    -0.6566286450000001,
    -0.27722699500000003,
    -0.5002742099999999
  ],
  "construction_scale": 69.21889611351888,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
