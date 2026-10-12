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
    0.06143221671611832,
    0.07465122203792503
  ],
  "profile": [
    [
      1.1639362152610044,
      -18.135586695647756
    ],
    [
      3.4140734481405315,
      -18.146902686345413
    ],
    [
      5.6904851372245195,
      -18.15864525732254
    ],
    [
      7.966901121447588,
      -18.175924390447875
    ],
    [
      10.243317327023718,
      -18.207698279106005
    ],
    [
      12.519640487596499,
      -18.239394991828323
    ],
    [
      14.795702843060567,
      -18.233109613372665
    ],
    [
      17.070933384950013,
      -18.174382444415865
    ],
    [
      19.344812289902222,
      -18.15563048117773
    ],
    [
      21.61381396389453,
      -18.26480659391367
    ],
    [
      23.867895801852168,
      -18.72678077791403
    ],
    [
      25.943589599633977,
      -19.600956422783554
    ],
    [
      27.68542918731724,
      -21.074653384069997
    ],
    [
      29.22776971537514,
      -22.84657938602657
    ],
    [
      30.655932080808878,
      -24.661862121218768
    ],
    [
      31.76902816454082,
      -26.560377974039895
    ],
    [
      32.40243023441705,
      -28.623110523192175
    ],
    [
      32.64970678380658,
      -30.838134299625178
    ],
    [
      32.77942819056145,
      -33.110105821929686
    ],
    [
      32.989924110178926,
      -35.38920957957184
    ],
    [
      33.72454110494473,
      -37.64335590502213
    ],
    [
      34.82638177681081,
      -39.51015222589898
    ],
    [
      36.43944377556042,
      -40.21558420824674
    ],
    [
      38.003116666436576,
      -39.7201996090834
    ],
    [
      38.81333591492235,
      -37.907586314414765
    ],
    [
      38.813939980450016,
      -35.69291099266831
    ],
    [
      38.61453346262357,
      -33.46092161303495
    ],
    [
      38.314453338675484,
      -31.232471370612224
    ],
    [
      37.98555838602656,
      -29.030750774379293
    ],
    [
      37.45516537925044,
      -26.958574664227356
    ],
    [
      36.481117078648204,
      -25.042325381974415
    ],
    [
      35.18560329227466,
      -23.14691016527545
    ],
    [
      33.974893116228984,
      -21.180606815480843
    ],
    [
      32.82908629094554,
      -19.181915293679246
    ],
    [
      31.601333433144607,
      -17.177921787076173
    ],
    [
      30.33454933377614,
      -15.10673642014301
    ],
    [
      30.00708026387094,
      -12.948230221723485
    ],
    [
      30.488952000698,
      -10.977242112591844
    ],
    [
      31.470495515452892,
      -9.342524149954746
    ],
    [
      32.98378292824735,
      -7.8180906822394185
    ],
    [
      34.72260100667706,
      -6.389524071655369
    ],
    [
      36.460638777232816,
      -5.170956519486007
    ],
    [
      38.19541071194827,
      -3.90629919300266
    ],
    [
      39.95056868485604,
      -2.6091456938777458
    ],
    [
      41.75747888587411,
      -1.2171629569460116
    ],
    [
      43.52571731300759,
      0.13240893800074732
    ],
    [
      45.150320544822705,
      1.7075230881507557
    ],
    [
      46.55128067211466,
      3.5846427908919907
    ],
    [
      47.651369408098134,
      5.566087322227842
    ],
    [
      48.503555873871484,
      7.656440215290847
    ],
    [
      49.14530747558388,
      9.814586106487695
    ],
    [
      49.54245538218825,
      12.032972483963917
    ],
    [
      49.67192005044994,
      14.282433017055695
    ],
    [
      49.62713341474898,
      16.545598158302067
    ],
    [
      49.253975742272694,
      18.808484678866318
    ],
    [
      48.65419257684645,
      20.988987152273133
    ],
    [
      47.822470140766484,
      23.06317420344842
    ],
    [
      46.79974092299281,
      25.0381870150509
    ],
    [
      45.55569615888011,
      26.82673874719285
    ],
    [
      44.0333309605045,
      28.407917153961932
    ],
    [
      42.33521783721402,
      29.83228056146031
    ],
    [
      40.53613043114406,
      31.173746618694004
    ],
    [
      38.64495433172475,
      32.48077772161844
    ],
    [
      36.658812333107946,
      33.64338397898887
    ],
    [
      34.601450071608056,
      34.67800403897867
    ],
    [
      32.48924398660051,
      35.56271292684062
    ],
    [
      30.340351966088328,
      36.34890629839759
    ],
    [
      28.16058235090187,
      37.05707103808814
    ],
    [
      25.962846680294724,
      37.69658771722182
    ],
    [
      23.74501730249363,
      38.277349732934915
    ],
    [
      21.515243883234785,
      38.78529648036401
    ],
    [
      19.273925948714187,
      39.22938256986207
    ],
    [
      17.025025566914465,
      39.613747687656705
    ],
    [
      14.767105335644239,
      39.92586399670106
    ],
    [
      12.503599952061123,
      40.17700764487851
    ],
    [
      10.235575141434694,
      40.38211184432289
    ],
    [
      7.963773178750967,
      40.55528605547644
    ],
    [
      5.689592202563908,
      40.657902809783785
    ],
    [
      3.414322253633613,
      40.70497276910935
    ],
    [
      1.1641077449650692,
      40.71386311479773
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
    0.360296285,
    -0.335604735,
    -0.047911305
  ],
  "construction_scale": 750.4384624326378,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
