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
    -0.8692584715461183,
    0.012148389435996883
  ],
  "profile": [
    [
      0.18850391998738947,
      -51.83598600873994
    ],
    [
      1.3766246941744549,
      -51.81479766551402
    ],
    [
      2.6912310487884445,
      -51.52637667391325
    ],
    [
      3.7629327390971072,
      -50.69301054513336
    ],
    [
      4.40874722154155,
      -49.51409208032649
    ],
    [
      4.590111288075827,
      -48.17318453261757
    ],
    [
      4.573269814841911,
      -46.79604340071697
    ],
    [
      4.5611717343302836,
      -45.42758581461257
    ],
    [
      4.551927296135595,
      -44.04816088558591
    ],
    [
      4.541534033921689,
      -42.6582856834034
    ],
    [
      4.5517976498822055,
      -41.26854393100001
    ],
    [
      4.570930632226789,
      -39.88790664678543
    ],
    [
      4.6024778812276885,
      -38.50856819781049
    ],
    [
      4.6266490790562,
      -37.12892542475718
    ],
    [
      4.6470841124126006,
      -35.74913289434526
    ],
    [
      4.64745161280356,
      -34.36933457391875
    ],
    [
      4.652809717183684,
      -32.98646671097909
    ],
    [
      4.655759017104758,
      -31.59972958329638
    ],
    [
      4.64239984564562,
      -30.214968148227392
    ],
    [
      4.636963100938052,
      -28.83201618788578
    ],
    [
      4.652811505199376,
      -27.448888036878714
    ],
    [
      4.655941322833188,
      -26.06569985558115
    ],
    [
      4.670213660145555,
      -24.682517650621087
    ],
    [
      4.675014557101738,
      -23.302096812362414
    ],
    [
      4.671492128411174,
      -21.93102967208583
    ],
    [
      4.673938200360626,
      -20.55468030437089
    ],
    [
      4.662803129783284,
      -19.178362344036103
    ],
    [
      4.633908256320685,
      -17.805286319053735
    ],
    [
      4.63384100101495,
      -16.429980225343737
    ],
    [
      4.64342444911403,
      -15.052772867878915
    ],
    [
      4.640934259280018,
      -13.675415898979345
    ],
    [
      4.6391266371168545,
      -12.298137223611066
    ],
    [
      4.641983461505372,
      -10.921203055565483
    ],
    [
      4.638858811457057,
      -9.544267070553573
    ],
    [
      4.640981488972217,
      -8.167175976650093
    ],
    [
      4.643937298038914,
      -6.790084736718926
    ],
    [
      4.6488648450792365,
      -5.413144579322665
    ],
    [
      4.655718595681941,
      -4.03607559884152
    ],
    [
      4.654729304018908,
      -2.658926688470779
    ],
    [
      4.654783944129502,
      -1.2816856249611712
    ],
    [
      4.641534694880225,
      0.09549233377129508
    ],
    [
      4.632347364700518,
      1.4726826956272152
    ],
    [
      4.634618920397484,
      2.8498453797268337
    ],
    [
      4.625412700027187,
      4.227009682880356
    ],
    [
      4.616030069142926,
      5.604181501798613
    ],
    [
      4.6105190793388875,
      6.981376086372608
    ],
    [
      4.60669620528578,
      8.358540401711435
    ],
    [
      4.600195740325888,
      9.735782173759059
    ],
    [
      4.591296886600748,
      11.113066988693337
    ],
    [
      4.584866703624255,
      12.490344735677368
    ],
    [
      4.580390049028188,
      13.867544848319692
    ],
    [
      4.584286382003997,
      15.244677250618444
    ],
    [
      4.5866282416766015,
      16.621849860972233
    ],
    [
      4.588434163179386,
      17.998797316514374
    ],
    [
      4.579651057356191,
      19.375605845077395
    ],
    [
      4.5712805143417,
      20.753025955697446
    ],
    [
      4.56491944426577,
      22.131574017952765
    ],
    [
      4.56148293553722,
      23.509720314080926
    ],
    [
      4.5683225929596105,
      24.885328922987263
    ],
    [
      4.565698873575256,
      26.263007061787466
    ],
    [
      4.581135885022156,
      27.64165456397376
    ],
    [
      4.571192917007982,
      29.020516306329974
    ],
    [
      4.586344880798629,
      30.39927211957216
    ],
    [
      4.625079580005854,
      31.777981707567715
    ],
    [
      4.637008960891382,
      33.156746181578676
    ],
    [
      4.622645216266067,
      34.53504895967317
    ],
    [
      4.5874965904381115,
      35.913479558355455
    ],
    [
      4.566890370507718,
      37.29196747768605
    ],
    [
      4.56017374121537,
      38.670344942785775
    ],
    [
      4.565129610214097,
      40.04872803183622
    ],
    [
      4.567069251842714,
      41.42719680483268
    ],
    [
      4.567175652777637,
      42.80565913853218
    ],
    [
      4.551305350003062,
      44.183877693493415
    ],
    [
      4.4341101654932125,
      45.56168116270777
    ],
    [
      4.337199546882189,
      46.93984784117055
    ],
    [
      4.2078370796884155,
      48.316620035186716
    ],
    [
      4.003503745744317,
      49.6803507946953
    ],
    [
      3.5520863668890756,
      50.935478611987534
    ],
    [
      2.644692693279138,
      51.885383225977776
    ],
    [
      1.3590750631560764,
      52.25806090196624
    ],
    [
      0.18567720256606365,
      52.287877996451286
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.17425174527083295,
      -0.935745528779848,
      0.3066213212393954
    ],
    [
      0.9846533380262472,
      0.162512503969406,
      -0.06361988657144217
    ],
    [
      0.009702225715686335,
      0.31300158373739545,
      0.9497030459012148
    ]
  ],
  "axis_candidate": 3,
  "center": [
    0.898991675,
    -0.32603307,
    -0.13919469
  ],
  "construction_scale": 58.2663638198603,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
