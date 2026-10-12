"""Editable CadQuery sketch/feature reconstruction. Approximate inferred design.
Run with Python + cadquery. No mesh or other input files required.
"""
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
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS = json.loads(r'''
{
  "center_xy": [
    0.24952871218804848,
    -3.4560617349213336
  ],
  "profile": [
    [
      0.8575953557308726,
      -12.73035350346707
    ],
    [
      2.516278920761178,
      -12.525308533299732
    ],
    [
      4.187963017328509,
      -12.055298820573114
    ],
    [
      5.802133816013244,
      -11.249573089697286
    ],
    [
      7.221119249189527,
      -10.102992443890802
    ],
    [
      8.412474221700801,
      -8.801615436560395
    ],
    [
      9.376624784916032,
      -7.315908166319952
    ],
    [
      10.281126664046754,
      -5.789955490009859
    ],
    [
      11.133453173649869,
      -4.233564979312689
    ],
    [
      11.961130620614242,
      -2.6643599380154823
    ],
    [
      12.71759894713832,
      -1.180144758032474
    ],
    [
      13.783211683655445,
      -0.5817868412094727
    ],
    [
      15.039725432372435,
      -1.2115661355045044
    ],
    [
      16.408129585171203,
      -1.9510007222241441
    ],
    [
      17.917644220525826,
      -2.695442149419324
    ],
    [
      19.539628966942686,
      -3.406580332368204
    ],
    [
      21.27064949394776,
      -4.100848244045649
    ],
    [
      23.075838727220123,
      -4.552523504592633
    ],
    [
      24.739924034143666,
      -4.68829534940852
    ],
    [
      26.34224776565779,
      -4.808061721304172
    ],
    [
      28.061200375526724,
      -4.725472501720205
    ],
    [
      29.699439224576114,
      -4.826651289053932
    ],
    [
      31.035494569952917,
      -5.889300560121583
    ],
    [
      31.912465286254292,
      -7.442431023928318
    ],
    [
      32.82143479991428,
      -9.007264799960684
    ],
    [
      33.70848953235251,
      -10.415698690470055
    ],
    [
      34.55546631240673,
      -11.708548498689954
    ],
    [
      35.61512493105235,
      -12.688296525726745
    ],
    [
      37.18619446226438,
      -13.313743476415548
    ],
    [
      38.91326288881794,
      -13.544367695339886
    ],
    [
      40.645678877987805,
      -13.610301888673138
    ],
    [
      42.34063796213327,
      -13.518672145912184
    ],
    [
      43.83773492386617,
      -13.110909147995072
    ],
    [
      45.09659731046439,
      -12.439808193172645
    ],
    [
      46.189389849292155,
      -11.247046142050259
    ],
    [
      46.677491048198455,
      -9.651344094579573
    ],
    [
      46.87954671237901,
      -7.922116138916718
    ],
    [
      46.933298183758,
      -6.151668346419796
    ],
    [
      46.95229328153421,
      -4.380245924852064
    ],
    [
      46.95454626773913,
      -2.6088602749600978
    ],
    [
      46.950967392157445,
      -0.8374244956553103
    ],
    [
      46.96558642748657,
      0.9339106986503571
    ],
    [
      47.01406286402836,
      2.704925109628066
    ],
    [
      47.075025144625144,
      4.476189897711787
    ],
    [
      47.09226423731822,
      6.247178082471111
    ],
    [
      47.053773663955866,
      8.012870720363432
    ],
    [
      46.52029772293909,
      9.745419158080223
    ],
    [
      45.655796815081516,
      11.335989329814577
    ],
    [
      44.352285973784305,
      12.554755564261141
    ],
    [
      43.45442062377384,
      13.245234149341035
    ],
    [
      42.51019814013736,
      13.576503882439745
    ],
    [
      40.965950355622894,
      13.603046829506628
    ],
    [
      39.2097470800464,
      13.542963255738586
    ],
    [
      37.47623047749288,
      13.497070949168382
    ],
    [
      35.85295238254709,
      13.375680969423854
    ],
    [
      34.20118359664697,
      13.348157779959644
    ],
    [
      32.47072212191556,
      13.342791162970638
    ],
    [
      30.813554270414944,
      13.334266121966703
    ],
    [
      29.100120137722904,
      13.39655180812921
    ],
    [
      27.334019568042216,
      13.380319810296617
    ],
    [
      25.651313090772376,
      13.09355982967038
    ],
    [
      24.059179293562597,
      12.510118504915592
    ],
    [
      22.433632737976204,
      11.772189419498627
    ],
    [
      20.823870205749905,
      10.910904223548727
    ],
    [
      19.227645837004083,
      10.049782033734324
    ],
    [
      17.774326290182067,
      9.087571752099354
    ],
    [
      16.597547648446216,
      7.958326703951008
    ],
    [
      15.545545305559642,
      6.52281585424805
    ],
    [
      14.480612836032764,
      5.1481710018298745
    ],
    [
      13.318767245250427,
      4.227514848851956
    ],
    [
      12.012643113065252,
      5.169351877663905
    ],
    [
      10.909172698228302,
      6.270658130425564
    ],
    [
      10.028219600532816,
      7.177576867440688
    ],
    [
      9.236726077193499,
      8.22772337953529
    ],
    [
      8.119461538424034,
      9.3061130349978
    ],
    [
      6.983582869603404,
      10.628261418545755
    ],
    [
      5.751525111146901,
      11.665985138466525
    ],
    [
      4.186837751285892,
      12.335301519092038
    ],
    [
      2.5289032966827065,
      12.885310467241267
    ],
    [
      0.8700806834456706,
      13.116619410382997
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "limitation": "Axisymmetric design approximation; asymmetric dents and bulges intentionally simplified",
  "center": [
    -0.6257100999355316,
    -0.5599354952573776,
    -0.34175732731819153
  ],
  "construction_scale": 508.6775599739555,
  "expected_solid_count": 1
}
''')

def build():
    return build_model(PARAMETERS)

if __name__ == "__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS['expected_solid_count']
    cq.exporters.export(result,str(Path(__file__).with_suffix(".step")))
