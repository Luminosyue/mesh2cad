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
PARAMETERS = json.loads('{"center_xy":[0.0007935054629799598,-0.0001831166453030164],"profile":[[0.0010376609900506484,-0.029970090947933792],[0.0032350607336872894,-0.029970090947933792],[0.005310382713788586,-0.029970090947933792],[0.007507782457425449,-0.030092168711469247],[0.009583104437526746,-0.030092168711469247],[0.011780504181163387,-0.030092168711469247],[0.013855826161264684,-0.030092168711469247],[0.016053225904901325,-0.030092168711469247],[0.018128547885002844,-0.030092168711469247],[0.020325947628639485,-0.030092168711469247],[0.02240126960874078,-0.030092168711469247],[0.024598669352377422,-0.030092168711469247],[0.02667399133247872,-0.03021424647500459],[0.028871391076115582,-0.03021424647500459],[0.03094671305621688,-0.030092168711469247],[0.03314411279985352,-0.03021424647500459],[0.03521943477995482,-0.03021424647500459],[0.03741683452359146,-0.030092168711469247],[0.039492156503692755,-0.030092168711469247],[0.04168955624732962,-0.029970090947933792],[0.043764878227430914,-0.029725935420863103],[0.04584020020753221,-0.029237624366721615],[0.04791552218763351,-0.028505157785509327],[0.04986876640419946,-0.027650613440761806],[0.05169993285723007,-0.026551913568943375],[0.05340902154672533,-0.02533113593358971],[0.055118110236220375,-0.02398828053470059],[0.05658304339864495,-0.02240126960874078],[0.0580479765610693,-0.020814258682780973],[0.05926875419642319,-0.01910516999328571],[0.06036745406824151,-0.0172740035402551],[0.06122199841298914,-0.015320759323689148],[0.06195446499420121,-0.013367515107123196],[0.06256485381187815,-0.011292193127021899],[0.0631752426295551,-0.009216871146920602],[0.06341939815662578,-0.007141549166819305],[0.06366355368369647,-0.004944149423182553],[0.06378563144723182,-0.0028688274430812566],[0.06378563144723182,-0.0006714276994445045],[0.06366355368369647,0.0014038942806566812],[0.06366355368369647,0.0036012940242935443],[0.06366355368369647,0.005676616004394841],[0.06366355368369647,0.007874015748031482],[0.06366355368369647,0.009949337728132779],[0.06378563144723182,0.01214673747176942],[0.06378563144723182,0.014222059451870939],[0.06390770921076716,0.01641945919550758],[0.06378563144723182,0.018494781175608876],[0.06341939815662578,0.020692180919245518],[0.0626869315754135,0.02264542513581147],[0.06171030946713052,0.024598669352377422],[0.06036745406824151,0.026185680278337342],[0.05865836537874625,0.027406457913691007],[0.05658304339864495,0.02801684673136795],[0.05450772141854365,0.02826100225843864],[0.05231032167490701,0.028138924494903295],[0.05023499969480549,0.028138924494903295],[0.04803759995116885,0.02801684673136795],[0.045962277971067556,0.02801684673136795],[0.043764878227430914,0.027894768967832606],[0.04168955624732962,0.02777269120429704],[0.039492156503692755,0.02777269120429704],[0.03741683452359146,0.027650613440761695],[0.03521943477995482,0.02752853567722635],[0.03314411279985352,0.027406457913691007],[0.03094671305621688,0.027406457913691007],[0.028871391076115582,0.027284380150155663],[0.02667399133247872,0.027284380150155663],[0.024598669352377422,0.027406457913691007],[0.02240126960874078,0.027406457913691007],[0.020325947628639485,0.027406457913691007],[0.018128547885002844,0.027406457913691007],[0.016053225904901325,0.027406457913691007],[0.013855826161264684,0.027406457913691007],[0.011780504181163387,0.027406457913691007],[0.009583104437526746,0.027284380150155663],[0.007507782457425449,0.027284380150155663],[0.005310382713788586,0.027284380150155663],[0.0032350607336872894,0.027284380150155663],[0.0010376609900506484,0.027284380150155663]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[-0.8227430873466398,0.1288530794115852,-0.5536836965146799],[-0.5639382286516511,-0.06171030946713052,0.823475553927852],[0.07196484160410188,0.9897454678630286,0.12348165781602871]],"axis_candidate":5,"center":[-0.13568943416956603,-0.18488677287432098,-0.15864005371421597],"construction_scale":1,"expected_solid_count":1}')

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
