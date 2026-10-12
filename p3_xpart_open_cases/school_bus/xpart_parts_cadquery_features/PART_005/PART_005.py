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
    0.024962601055218997,
    0.042210441041928795
  ],
  "profile": [
    [
      0.8438843173345756,
      -48.9669555902556
    ],
    [
      2.4598912533565307,
      -49.01568034140985
    ],
    [
      4.092117486004366,
      -49.091897986552944
    ],
    [
      5.729333178632507,
      -49.13558820725207
    ],
    [
      7.366516583892151,
      -49.095113888042604
    ],
    [
      9.001755742526338,
      -49.02210802530215
    ],
    [
      10.636098024126204,
      -48.92516370603484
    ],
    [
      12.271334018274407,
      -48.78297956415392
    ],
    [
      13.893817724364606,
      -48.50949262550651
    ],
    [
      15.473233783341286,
      -48.14115269314699
    ],
    [
      16.90292889005881,
      -47.41842344304903
    ],
    [
      17.981470933972496,
      -46.26133716082593
    ],
    [
      18.52061408434748,
      -44.722593033007
    ],
    [
      18.63394442775978,
      -43.09495102556294
    ],
    [
      18.496177588919718,
      -41.45855825380909
    ],
    [
      18.36733395804549,
      -39.80611079076582
    ],
    [
      18.40494172963235,
      -38.161216579532365
    ],
    [
      18.41594748095821,
      -36.51306787912208
    ],
    [
      18.42206129673897,
      -34.846422602512725
    ],
    [
      18.417869175390678,
      -33.17739474255133
    ],
    [
      18.413622320537506,
      -31.52386945551957
    ],
    [
      18.403597627454335,
      -29.868970860036967
    ],
    [
      18.3906993854902,
      -28.21141424788344
    ],
    [
      18.375134254523427,
      -26.561285000272807
    ],
    [
      18.356376070949157,
      -24.90873483762097
    ],
    [
      18.343817021078667,
      -23.256116570182723
    ],
    [
      18.326297513024507,
      -21.603536133448685
    ],
    [
      18.307050684533646,
      -19.950955221983058
    ],
    [
      18.29351033775268,
      -18.29837232481453
    ],
    [
      18.277885281531965,
      -16.645779957115828
    ],
    [
      18.25821748593055,
      -14.993204177268439
    ],
    [
      18.240342404946112,
      -13.340604799517553
    ],
    [
      18.215936011776584,
      -11.68806151130644
    ],
    [
      18.18265194962207,
      -10.035562260416373
    ],
    [
      18.151001163228976,
      -8.383058839831964
    ],
    [
      18.12126196548997,
      -6.730551964827213
    ],
    [
      18.100392381373222,
      -5.078076592282738
    ],
    [
      18.082680056499584,
      -3.4255738815620025
    ],
    [
      18.0637159726719,
      -1.7730366997528053
    ],
    [
      18.036719903574017,
      -0.12055716826070378
    ],
    [
      18.012612580892394,
      1.5318340287371435
    ],
    [
      17.98888428270905,
      3.184162167591869
    ],
    [
      17.96618810716261,
      4.836554718895075
    ],
    [
      17.946808337092513,
      6.488916796315729
    ],
    [
      17.922641352726515,
      8.141275047124827
    ],
    [
      17.89147978178589,
      9.793537628778857
    ],
    [
      17.85756639228319,
      11.445654649083515
    ],
    [
      17.81617029733399,
      13.097482673442501
    ],
    [
      17.76799764848314,
      14.74921067670545
    ],
    [
      17.715913927394773,
      16.401092920907494
    ],
    [
      17.65680967813563,
      18.052651877780637
    ],
    [
      17.59483627253681,
      19.704302849804577
    ],
    [
      17.52605664656419,
      21.355813235592784
    ],
    [
      17.44066955174724,
      23.006806333854527
    ],
    [
      17.347811605941004,
      24.657662506181083
    ],
    [
      17.259045169542688,
      26.307955996201486
    ],
    [
      17.16216796000687,
      27.958082446756215
    ],
    [
      17.058412660517284,
      29.607795207736608
    ],
    [
      16.958480600222714,
      31.257103558621296
    ],
    [
      16.866705326016948,
      32.90638852126606
    ],
    [
      16.76151377129686,
      34.55463710590505
    ],
    [
      16.59864560022682,
      36.201112593960865
    ],
    [
      16.338742078322383,
      37.84460621293327
    ],
    [
      16.303754568768458,
      39.481844481336594
    ],
    [
      16.886619124938,
      40.93446736003064
    ],
    [
      18.016750094512183,
      42.06434251557754
    ],
    [
      18.801897398119333,
      43.36685074374945
    ],
    [
      18.816863687131452,
      44.928794455794076
    ],
    [
      18.10212901767885,
      46.34027205464863
    ],
    [
      16.824619482707984,
      47.273428823772164
    ],
    [
      15.24837484400786,
      47.43553014164337
    ],
    [
      13.685155995944628,
      46.96843050138158
    ],
    [
      12.067140125268281,
      46.81478994717304
    ],
    [
      10.454984722080443,
      47.09038567802987
    ],
    [
      8.904902353161443,
      47.60096361583878
    ],
    [
      7.330442012732249,
      47.9152492903044
    ],
    [
      5.721279640203506,
      48.22226382144464
    ],
    [
      4.114564402451977,
      48.55622338183916
    ],
    [
      2.4753801742124466,
      48.72629616775826
    ],
    [
      0.8445472152422849,
      48.8099416993219
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
    -0.021918350000000003,
    0.41517545,
    -0.166799525
  ],
  "construction_scale": 91.37396509390265,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
