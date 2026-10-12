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
    -0.007768518855485373,
    -0.15488699468185274
  ],
  "profile": [
    [
      0.6468131736091276,
      -48.901941034248196
    ],
    [
      1.5628888173230537,
      -47.932113732971644
    ],
    [
      1.9764025097370959,
      -46.54486486849472
    ],
    [
      2.1716328534207405,
      -45.09787815468529
    ],
    [
      2.263892428137808,
      -43.63884058507151
    ],
    [
      2.3257940138419095,
      -42.17776155561476
    ],
    [
      2.3708930252172293,
      -40.715893640159564
    ],
    [
      2.388384633087968,
      -39.25349796879158
    ],
    [
      2.3969613857077476,
      -37.79189142316366
    ],
    [
      2.4038909080948176,
      -36.33317677276794
    ],
    [
      2.399576449090068,
      -34.87507821406957
    ],
    [
      2.3953184342288933,
      -33.417045704726405
    ],
    [
      2.4084214918266023,
      -31.95942537627149
    ],
    [
      2.4372647042499036,
      -30.501811790189727
    ],
    [
      2.475773215497771,
      -29.0438706354537
    ],
    [
      2.503864252787133,
      -27.585847929676525
    ],
    [
      2.5129253311330473,
      -26.127819318935927
    ],
    [
      2.5257088527342555,
      -24.67008358614571
    ],
    [
      2.545748758255928,
      -23.212230232597392
    ],
    [
      2.562520231449167,
      -21.754357450452453
    ],
    [
      2.5813565061779276,
      -20.296322486417957
    ],
    [
      2.6101271780534625,
      -18.83827107564277
    ],
    [
      2.6629274515491543,
      -17.38020126686902
    ],
    [
      2.727421375576782,
      -15.922484530575122
    ],
    [
      2.781375804391008,
      -14.465037998122147
    ],
    [
      2.838967342981123,
      -13.007254448793795
    ],
    [
      2.8726482779274267,
      -11.54926308756123
    ],
    [
      2.8944890610467295,
      -10.09113722088879
    ],
    [
      2.905113268311377,
      -8.63295871450117
    ],
    [
      2.9143448627527615,
      -7.174818823133391
    ],
    [
      2.931851851907733,
      -5.716900414908215
    ],
    [
      2.9674155299636604,
      -4.25957372101556
    ],
    [
      3.0208146697459823,
      -2.8025087267788926
    ],
    [
      3.0553299058133376,
      -1.3450799420617061
    ],
    [
      3.0436308191827326,
      0.11179362270514037
    ],
    [
      3.309213803874234,
      1.4674518411743651
    ],
    [
      4.238507211878025,
      2.536322373049761
    ],
    [
      5.0415091934203815,
      3.7358190120909045
    ],
    [
      5.658195138992802,
      5.055828851120563
    ],
    [
      6.23277805625423,
      6.399441291159787
    ],
    [
      6.806220099011199,
      7.74481410022364
    ],
    [
      7.371497007460544,
      9.094379836407802
    ],
    [
      7.934415833496362,
      10.444195646845799
    ],
    [
      8.493969768753859,
      11.784006568899995
    ],
    [
      9.038762799318445,
      13.026768639033586
    ],
    [
      9.585361781285968,
      14.165979336917067
    ],
    [
      10.138569189758124,
      15.492570619043995
    ],
    [
      10.709676287673929,
      16.836456022733557
    ],
    [
      11.299422528465547,
      18.193084935215794
    ],
    [
      11.965423770115635,
      19.54555679491385
    ],
    [
      12.907533719726551,
      20.654298400214437
    ],
    [
      13.816907892966416,
      21.747820374772303
    ],
    [
      14.234561241948217,
      23.121834584292078
    ],
    [
      14.455213897256812,
      24.566867273432727
    ],
    [
      14.64504795410934,
      26.01564105370217
    ],
    [
      14.526228716957753,
      27.424763875796927
    ],
    [
      13.551541522591346,
      28.297577011466228
    ],
    [
      12.15547635613043,
      28.47429160357017
    ],
    [
      11.367884107272452,
      29.265356125828852
    ],
    [
      11.306920101154692,
      30.70017605464231
    ],
    [
      11.306023879472395,
      32.162441099900384
    ],
    [
      11.31125095294555,
      33.624471190074736
    ],
    [
      11.324833446719424,
      35.08636030739017
    ],
    [
      11.342656646458483,
      36.54801821961081
    ],
    [
      11.354037821759292,
      38.0098639473282
    ],
    [
      11.356100918074453,
      39.472602497713474
    ],
    [
      11.362169542236195,
      40.93818531914415
    ],
    [
      11.369481740400731,
      42.40435285730322
    ],
    [
      11.362772631637089,
      43.870470658558474
    ],
    [
      11.345607436229052,
      45.336576241564295
    ],
    [
      11.328070372701553,
      46.79912958092356
    ],
    [
      11.286955058978446,
      48.25289913424972
    ],
    [
      10.796787726625643,
      49.50347164120503
    ],
    [
      9.50336441208464,
      49.9221401635163
    ],
    [
      8.043519984090564,
      49.9230697174509
    ],
    [
      6.581088441760846,
      49.92077754622855
    ],
    [
      5.118626657417209,
      49.91885868414492
    ],
    [
      3.6561360969503727,
      49.91653453430714
    ],
    [
      2.193687167548719,
      49.915163627367775
    ],
    [
      0.7478909757607279,
      49.914671821382
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.8246919797232752,
      -0.5655821126459751,
      0.00011151242211946155
    ],
    [
      -0.5655692040622567,
      0.8246744579290396,
      0.006596503303280557
    ],
    [
      -0.0038228257206092886,
      0.005377015376612175,
      -0.9999782366177526
    ]
  ],
  "axis_candidate": 3,
  "center": [
    -0.647262425,
    -0.595396815,
    -0.22884773
  ],
  "construction_scale": 81.40818047034358,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
