"""Inferred standard-feature CAD. Approximate reconstruction, not recovered design history."""
from pathlib import Path
import json
'Pure CadQuery feature builder. Input contains sketches, never a triangle mesh.'
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp = cq.Workplane('XY', origin=(0, 0, z))
    if isinstance(points, dict):
        return wp.center(*points['center']).circle(points['radius']).val()
    if smooth:
        return wp.spline([tuple(p) for p in points], periodic=True).wire().val()
    return wp.polyline([tuple(p) for p in points]).close().wire().val()

def build_model(p):
    if p['operation'] == 'revolve':
        pts = p['profile']
        n = len(pts)
        wp = cq.Workplane('XZ').moveTo(0, pts[0][1]).lineTo(*pts[0])
        bounds = sorted(set((int(i * (n - 1) / p['segments']) for i in range(p['segments'] + 1))))

        def tangent(k):
            (a, b) = (pts[max(0, k - 1)], pts[min(n - 1, k + 1)])
            (x, y) = (b[0] - a[0], b[1] - a[1])
            d = sqrt(x * x + y * y)
            return (x / d, y / d)
        for (a, b) in zip(bounds[:-1], bounds[1:]):
            wp = wp.spline([tuple(q) for q in pts[a + 1:b + 1]], includeCurrent=True, tangents=[tangent(a), tangent(b)], scale=False)
        shape = wp.lineTo(0, pts[-1][1]).close().revolve(360, (0, 0), (0, 1)).val().translate((*p['center_xy'], 0))
    else:
        features = []
        for feature in p['features']:
            if feature['type'] == 'extrude':
                wires = [sketch_wire(q, feature['start']) for q in feature['loops']]
                shape = cq.Workplane('XY').newObject(wires).toPending().extrude(feature['length'], combine=False).val()
            else:
                wires = [sketch_wire(q, z, feature.get('smooth', False)) for (z, q) in feature['sections']]
                shape = cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled', True), combine=False).val()
                for pocket in feature.get('pockets', []):
                    pw = [sketch_wire(q, z, True) for (z, q) in pocket]
                    tool = cq.Workplane('XY').newObject(pw).toPending().loft(ruled=True, combine=False).val()
                    shape = shape.cut(tool)
            features.append((shape, feature.get('cut', False)))
        shape = features[0][0]
        for (addition, cut) in features[1:]:
            shape = shape.cut(addition) if cut else shape.fuse(addition)
        shape = shape.clean()
    if 'basis' in p:
        b = p['basis']
        shape = shape.located(cq.Location(cq.Plane(origin=(0, 0, 0), xDir=tuple(b[0]), normal=tuple(b[2]))))
    return shape.scale(1 / p['construction_scale']).translate(tuple(p['center']))
PARAMETERS = json.loads('{"center_xy":[0.00042727217237370496,6.103888176767214e-05],"profile":[[0.0015259720441922475,0.028383080021973983],[0.0045779161325765205,0.028383080021973983],[0.0076298602209607935,0.028383080021973983],[0.010681804309345067,0.02826100225843864],[0.01373374839772934,0.028138924494903295],[0.016785692486113613,0.028138924494903295],[0.019837636574497886,0.02801684673136795],[0.02288958066288216,0.02777269120429704],[0.025941524751266654,0.027650613440761695],[0.028993468839650927,0.02752853567722635],[0.0320454129280352,0.027284380150155663],[0.03509735701641947,0.02716230238662032],[0.0380272233412684,0.026796069096014064],[0.0401025453213697,0.02484282487944811],[0.04071293413904664,0.02203503631813475],[0.04071293413904664,0.018983092229750254],[0.0405908563755113,0.01593114814136598],[0.0405908563755113,0.012879204052981708],[0.0405908563755113,0.009827259964597435],[0.0405908563755113,0.0067753158762131616],[0.0405908563755113,0.0037233717878288886],[0.04071293413904664,0.0006714276994446156],[0.04071293413904664,-0.0023805163889397685],[0.04071293413904664,-0.0054324604773240415],[0.04046877861197573,-0.008484404565708314],[0.04022462308490504,-0.011536348654092698],[0.0401025453213697,-0.014588292742476971],[0.04022462308490504,-0.017640236830861244],[0.04022462308490504,-0.020692180919245518],[0.04022462308490504,-0.0237441250076299],[0.04034670084844039,-0.026796069096014175],[0.041079167429652674,-0.029725935420863103],[0.04132332295672336,-0.03265580174571203],[0.04242202282854168,-0.03521943477995482],[0.04498565586278458,-0.03619605688823779],[0.04767136666056282,-0.03534151254349016],[0.04901422205945183,-0.033022035036318176],[0.049990844167734805,-0.03021424647500459],[0.05145577733015938,-0.027406457913691007],[0.05182201062076541,-0.024476591588842078],[0.05182201062076541,-0.021424647500457805],[0.05182201062076541,-0.018372703412073532],[0.052188243911371446,-0.015442837087224603],[0.054019410364402054,-0.013611670634193995],[0.05694927668925098,-0.013245437343587851],[0.05975706525056457,-0.012635048525911019],[0.06134407617652449,-0.010315571018738923],[0.06122199841298914,-0.007385704693889994],[0.059390831959958534,-0.0054324604773240415],[0.05658304339864495,-0.004944149423182553],[0.05353109931026068,-0.004944149423182553],[0.05072331074894709,-0.004211682841970377],[0.04938045535005808,-0.001770127571262936],[0.04913629982298717,0.0011597387535859927],[0.04913629982298717,0.004211682841970266],[0.04913629982298717,0.007263626930354539],[0.04913629982298717,0.010315571018739034],[0.04913629982298717,0.013367515107123307],[0.04913629982298717,0.01641945919550758],[0.04901422205945183,0.019471403283891853],[0.04901422205945183,0.022523347372276126],[0.04901422205945183,0.0255752914606604],[0.048892144295916484,0.02862723554904467],[0.0481596777147042,0.0315571018738936],[0.046450589025209155,0.03399865714460115],[0.0440090337545016,0.03582982359763176],[0.041079167429652674,0.03631813465177314],[0.0380272233412684,0.03619605688823779],[0.03509735701641947,0.035951901361167105],[0.0320454129280352,0.035951901361167105],[0.028993468839650927,0.03607397912470245],[0.025941524751266654,0.03619605688823779],[0.02288958066288216,0.03631813465177314],[0.019837636574497886,0.03644021241530848],[0.016785692486113613,0.036562290178843826],[0.01373374839772934,0.03668436794237939],[0.010681804309345067,0.036806445705914737],[0.0076298602209607935,0.036806445705914737],[0.0045779161325765205,0.03692852346945008],[0.0015259720441922475,0.03692852346945008]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05]],"axis_candidate":1,"center":[-0.13568943416956603,0.4071903802722334,-0.13190502349996946],"construction_scale":1,"expected_solid_count":1}')

def build():
    return build_model(PARAMETERS)
if False:
    result = build()
    assert result.isValid() and len(result.Solids()) == PARAMETERS['expected_solid_count']
    result.exportStep(str(Path(__file__).with_suffix('.step')))
_original_normalized_build = build

def build():
    return _original_normalized_build().scale(2.0).translate((0.0, 0.0, 0.0))
if __name__ == '__main__':
    result = build()
    result.exportStep(str(Path(__file__).with_suffix('.step')))
