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
    0.04593907461766381,
    0.003451424434679015
  ],
  "profile": [
    [
      1.3915313259202402,
      -7.983115519621135
    ],
    [
      2.782454306620007,
      -7.983325245175013
    ],
    [
      4.173689432949997,
      -7.983067579767454
    ],
    [
      5.564923770273062,
      -7.9838774502724945
    ],
    [
      6.956158022878837,
      -7.98530856863734
    ],
    [
      8.347375714480147,
      -7.985881923055331
    ],
    [
      9.738558665388307,
      -7.986644109837905
    ],
    [
      11.129730498303367,
      -7.986614661690345
    ],
    [
      12.520949506811881,
      -7.98555583971719
    ],
    [
      13.912190579947978,
      -7.986645239354922
    ],
    [
      15.303426338472159,
      -7.9868073799647314
    ],
    [
      16.694609817380655,
      -7.985976263722748
    ],
    [
      18.085805528019907,
      -7.9867438650563365
    ],
    [
      19.477027909842796,
      -7.986507709694168
    ],
    [
      20.868262555914725,
      -7.988142915321607
    ],
    [
      22.25951251281261,
      -7.989694081612477
    ],
    [
      23.65076290404434,
      -7.990340725907169
    ],
    [
      25.04200855759207,
      -7.9924725499795795
    ],
    [
      26.433247848102194,
      -7.994530551585919
    ],
    [
      27.824488609138704,
      -7.996852759063092
    ],
    [
      29.215696898120925,
      -8.001165501119445
    ],
    [
      30.606825326235366,
      -8.003837161099042
    ],
    [
      31.99799492899202,
      -8.008634362700425
    ],
    [
      33.38921380922145,
      -8.010907837284204
    ],
    [
      34.78041339567954,
      -8.013758368628697
    ],
    [
      36.17165050832391,
      -8.018280897696734
    ],
    [
      37.562880291494665,
      -8.020046639808644
    ],
    [
      38.954112900176426,
      -8.022812142319774
    ],
    [
      40.345321216296895,
      -8.027647211973814
    ],
    [
      41.73651911858866,
      -8.034403694495044
    ],
    [
      43.127659554480985,
      -8.047777178450566
    ],
    [
      44.51850334825318,
      -8.072356606086716
    ],
    [
      45.90788930736745,
      -8.076650221174766
    ],
    [
      47.25345711777001,
      -7.8329799056927385
    ],
    [
      48.38048351870551,
      -7.078940342434086
    ],
    [
      49.12974025158408,
      -5.9277042952631405
    ],
    [
      49.56858808291524,
      -4.612679294220245
    ],
    [
      49.86977305172702,
      -3.256076223940892
    ],
    [
      50.007638602811255,
      -1.8773809700681428
    ],
    [
      49.928807553181244,
      -0.49208102412893695
    ],
    [
      49.68670048454635,
      0.876057708472703
    ],
    [
      49.34453674996415,
      2.224713476798358
    ],
    [
      48.838209888710246,
      3.505992776879574
    ],
    [
      48.09286828377292,
      4.676132152794734
    ],
    [
      47.17952603392058,
      5.729246758219334
    ],
    [
      46.13044689907723,
      6.631980619170175
    ],
    [
      44.972947197461295,
      7.4043965978898605
    ],
    [
      43.71385979415719,
      7.94054372122173
    ],
    [
      42.34208225213857,
      8.059954962975612
    ],
    [
      40.95081196087074,
      8.069664782072053
    ],
    [
      39.559782443223455,
      8.079020129730415
    ],
    [
      38.16878429751225,
      8.074265198382177
    ],
    [
      36.77774771836556,
      8.065051077974623
    ],
    [
      35.38782650154524,
      8.037247237453798
    ],
    [
      34.06353990709209,
      7.735956901960378
    ],
    [
      33.009072395066276,
      6.87207140393194
    ],
    [
      31.95606775706338,
      6.07120150346025
    ],
    [
      30.606533506068914,
      5.912331090623873
    ],
    [
      29.215677665299815,
      5.901865873308103
    ],
    [
      27.824548460576025,
      5.891432794285043
    ],
    [
      26.43332962806125,
      5.8871175818841674
    ],
    [
      25.042095795090365,
      5.891411290366053
    ],
    [
      23.650854861539074,
      5.893709210849934
    ],
    [
      22.259637841514127,
      5.894269343432014
    ],
    [
      20.86841277756045,
      5.893983936397041
    ],
    [
      19.477176618382437,
      5.890768983686776
    ],
    [
      18.085957254921578,
      5.890314293870818
    ],
    [
      16.694740498647867,
      5.890456458747578
    ],
    [
      15.303521887861525,
      5.889834586720381
    ],
    [
      13.91228385783429,
      5.889808681915761
    ],
    [
      12.521067981155722,
      5.890221705127713
    ],
    [
      11.129833282797076,
      5.891290219865273
    ],
    [
      9.73860596692533,
      5.892811769358637
    ],
    [
      8.347365794012646,
      5.896443993142439
    ],
    [
      6.956149334954956,
      5.900411806537097
    ],
    [
      5.564937118666356,
      5.902581501639359
    ],
    [
      4.17371962502498,
      5.904610267720016
    ],
    [
      2.7824855553142944,
      5.906602380089969
    ],
    [
      1.3915519245583603,
      5.906277630415428
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
    0.305120385,
    1.4260000000002049e-05,
    -7.030500000000661e-05
  ],
  "construction_scale": 311.5085655821787,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
