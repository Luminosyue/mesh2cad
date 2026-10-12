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
PARAMETERS = json.loads('{"operation":"base_and_profile_pads","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.3998657144601111,"length":0.04852591100531045,"loops":[[[0.004699993896111865,-0.41268387963132513],[0.004699993896111865,0.4076786913263748],[0.004211682841970266,0.41585790148324486],[0.0025025941524752238,0.4175669901727401],[-6.103888176767214e-05,0.41768906793627547],[-0.003967527314899577,0.41585790148324486],[-0.0045779161325764095,0.4035280473661722],[-0.004699993896111865,-0.41268387963132513],[-0.0037233717878288886,-0.4151254349020326],[-0.0025025941524751127,-0.41634621253738635],[0.0025025941524752238,-0.4162241347738509]]]},{"type":"extrude","start":-0.35140084233656843,"length":0.7027406457913692,"loops":[[[-0.004699993896111865,-0.3904657266678875],[-0.004333760605505721,-0.41268387963132513],[-0.0025025941524751127,-0.41634621253738635],[-6.103888176767214e-05,-0.4170786791185985],[0.0034792162607582,-0.4151254349020326],[0.0045779161325765205,-0.41268387963132513],[0.004699993896111865,-0.3993774034059696],[0.0045779161325765205,-0.3756943172801074],[-6.103888176767214e-05,-0.37142159555636944],[-0.0032350607336874004,-0.3756943172801074]]]},{"type":"extrude","start":-0.35140084233656843,"length":0.7027406457913692,"loops":[[[-0.0036012940242934333,0.383751449673442],[-0.003967527314899577,0.41585790148324486],[-0.0025025941524751127,0.4173228346456692],[0.0025025941524752238,0.41744491240920456],[0.004211682841970266,0.41585790148324486],[0.0045779161325765205,0.41329426844900197],[0.0045779161325765205,0.383751449673442],[0.0028688274430812566,0.3806995055850577],[-6.103888176767214e-05,0.37899041689556245]]]},{"type":"extrude","start":0.35140084233656843,"length":0.04852591100531045,"loops":[[[0.0025025941524752238,0.05084538851248244],[-6.103888176767214e-05,0.32234633461514983],[-0.002624671916010457,-0.3708112067386925],[-0.004455838369041065,-0.38802417139718004],[-0.004455838369041065,-0.4069462247451626],[-0.002990905206616601,-0.4151254349020326],[-6.103888176767214e-05,-0.41634621253738635],[0.0034792162607582,-0.4151254349020326],[0.004699993896111865,-0.40780076908991025],[0.0036012940242935443,-0.3708112067386925]]]},{"type":"extrude","start":0.35140084233656843,"length":0.04852591100531045,"loops":[[[-0.0045779161325764095,0.40181895867667694],[-0.0037233717878288886,0.41585790148324486],[0.0025025941524752238,0.41720075688213387],[0.0045779161325765205,0.41329426844900197],[0.0045779161325765205,0.383751449673442],[0.0033571384972226337,0.38045535005798703],[-6.103888176767214e-05,0.3772813282060672],[-0.003479216260758089,0.383751449673442]]]}],"axis_candidate":2,"thickness_regions":3,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[-0.0001831166453030164,0.0912531282426905,-0.0582921320881401],"construction_scale":1,"expected_solid_count":1}')

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
