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
    0.02795936358572693,
    0.0522406369977236
  ],
  "profile": [
    [
      1.0180038027372764,
      -49.813530781400125
    ],
    [
      2.9859332490386628,
      -49.81312249450758
    ],
    [
      4.9765756904179055,
      -49.818207912820455
    ],
    [
      6.967195610503814,
      -49.82267130747367
    ],
    [
      8.957746773636181,
      -49.832866474799275
    ],
    [
      10.948347488825664,
      -49.841822260824486
    ],
    [
      12.938976355450011,
      -49.85055279469642
    ],
    [
      14.927470465309028,
      -49.84851928539717
    ],
    [
      16.757324600547083,
      -49.4479223537037
    ],
    [
      17.747269275615732,
      -47.89445130391273
    ],
    [
      17.88025589749111,
      -45.931199177759424
    ],
    [
      17.88382049250611,
      -43.94406980116819
    ],
    [
      17.8878653400864,
      -41.959882838722095
    ],
    [
      17.889198728984567,
      -39.975963659278534
    ],
    [
      17.89206817308862,
      -37.9920768631644
    ],
    [
      17.889670253900558,
      -36.006603216106335
    ],
    [
      17.88682867088422,
      -34.01674317540007
    ],
    [
      17.88922208903802,
      -32.026182684362446
    ],
    [
      17.89181894066161,
      -30.03560628571628
    ],
    [
      17.891620578041483,
      -28.04504799889098
    ],
    [
      17.892939384721878,
      -26.054335447094864
    ],
    [
      17.894836679059345,
      -24.063842581671913
    ],
    [
      17.8965845005348,
      -22.073617705172804
    ],
    [
      17.894002815450612,
      -20.083047839326074
    ],
    [
      17.896670598126207,
      -18.092698438684046
    ],
    [
      17.90214032731764,
      -16.10222441734757
    ],
    [
      17.906542301171108,
      -14.111702233664607
    ],
    [
      17.914591196336943,
      -12.121289386961017
    ],
    [
      17.925506279102002,
      -10.130873136892763
    ],
    [
      17.936722994523976,
      -8.140322371044569
    ],
    [
      17.945606037957653,
      -6.149648583314073
    ],
    [
      17.958078271110203,
      -4.158997674460826
    ],
    [
      17.966796412148206,
      -2.1685384108612205
    ],
    [
      17.973399427244686,
      -0.17791615821514822
    ],
    [
      17.97821583053722,
      1.8127437079377333
    ],
    [
      17.984301061851596,
      3.8033040304066708
    ],
    [
      17.99237884550126,
      5.793820338581639
    ],
    [
      17.999397328934897,
      7.7843573535087245
    ],
    [
      17.997740444430015,
      9.774808255655529
    ],
    [
      17.981289175404136,
      11.7638517842158
    ],
    [
      18.108575185109952,
      13.495711233972614
    ],
    [
      18.83739436648588,
      14.144142446981999
    ],
    [
      20.60586679669368,
      14.795882667424182
    ],
    [
      22.276404446503335,
      15.958890301016918
    ],
    [
      23.3136116080302,
      17.618737253125182
    ],
    [
      23.917687871390115,
      19.5342868064064
    ],
    [
      24.27236382953899,
      21.492916116377298
    ],
    [
      24.634580816756092,
      23.45018066853352
    ],
    [
      25.02167331891669,
      25.40655324430699
    ],
    [
      25.399320071615143,
      27.363777327113255
    ],
    [
      25.768083204057675,
      29.3221696151752
    ],
    [
      26.11745470339514,
      31.283694240070446
    ],
    [
      26.468007213987754,
      33.245608916806766
    ],
    [
      26.831825445407617,
      35.20589882303794
    ],
    [
      27.163661646936184,
      37.16941029601141
    ],
    [
      27.43719718353955,
      39.14118932996186
    ],
    [
      27.606685739178953,
      41.12361296877443
    ],
    [
      27.717058424979463,
      43.11076797862758
    ],
    [
      27.809192142601702,
      45.09900190518785
    ],
    [
      27.69693746914236,
      47.04079049490099
    ],
    [
      26.54181835336967,
      48.48447781377233
    ],
    [
      24.671706439670793,
      49.05235421832299
    ],
    [
      22.686985009176354,
      49.09202702775464
    ],
    [
      20.788035431604854,
      48.62627288636611
    ],
    [
      19.373670910587983,
      47.31478486022513
    ],
    [
      18.625979219997703,
      45.47752600634793
    ],
    [
      18.26446671946983,
      43.51870591180216
    ],
    [
      17.972745368470772,
      41.546771077510485
    ],
    [
      17.679570157224227,
      39.57219956598714
    ],
    [
      17.424175053581017,
      37.59409845540454
    ],
    [
      17.145537743059208,
      35.617525882824864
    ],
    [
      16.52905096985382,
      33.82554262476146
    ],
    [
      14.92113884413182,
      33.19679832821684
    ],
    [
      12.937627226954934,
      33.17062930485473
    ],
    [
      10.947077704511596,
      33.17311532068752
    ],
    [
      8.956688583217876,
      33.17036951120668
    ],
    [
      6.96635199258938,
      33.16833148803944
    ],
    [
      4.975992161629852,
      33.16734335578742
    ],
    [
      2.985672374716141,
      33.16631174985312
    ],
    [
      1.0178791320361988,
      33.165225866713584
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
    -0.713341735,
    0.78231046,
    -0.45241474000000004
  ],
  "construction_scale": 128.46663356681032,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
