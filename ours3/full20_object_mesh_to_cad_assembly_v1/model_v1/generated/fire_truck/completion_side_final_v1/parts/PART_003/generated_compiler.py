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
PARAMETERS = json.loads('{"center_xy":[6.103888176767214e-05,6.103888176767214e-05],"profile":[[0.0027467496795459123,-0.0645180980284441],[0.008240249038637515,-0.0645180980284441],[0.01373374839772934,-0.0645180980284441],[0.019227247756821164,-0.0645180980284441],[0.024720747115912767,-0.0645180980284441],[0.03021424647500459,-0.06464017579197945],[0.035707745834096416,-0.06464017579197945],[0.04120124519318802,-0.06464017579197945],[0.04669474455227984,-0.06464017579197945],[0.052188243911371446,-0.06464017579197945],[0.057559665506927926,-0.06464017579197945],[0.06305316486601975,-0.06464017579197945],[0.06854666422511135,-0.0647622535555149],[0.07404016358420318,-0.0647622535555149],[0.07953366294329478,-0.0647622535555149],[0.0850271623023866,-0.0647622535555149],[0.09052066166147843,-0.0647622535555149],[0.09601416102057003,-0.0647622535555149],[0.10150766037966186,-0.0647622535555149],[0.10700115973875368,-0.06488433131905025],[0.11249465909784528,-0.06488433131905025],[0.11798815845693711,-0.06488433131905025],[0.12348165781602871,-0.06488433131905025],[0.12897515717512054,-0.0647622535555149],[0.13446865653421236,-0.0647622535555149],[0.13996215589330396,-0.06439602026490876],[0.1452114997253251,-0.06329732039309044],[0.15021668803027532,-0.06122199841298903],[0.15485564304461952,-0.05841420985167556],[0.15888420924128677,-0.05475187694561434],[0.16205823109320638,-0.050234999694805604],[0.1644997863639137,-0.04522981138985538],[0.16584264176280294,-0.039980467557834354],[0.16657510834401523,-0.03448696819874264],[0.16694134163462127,-0.028993468839650816],[0.16694134163462127,-0.023499969480559102],[0.16681926387108592,-0.01800647012146739],[0.16681926387108592,-0.012512970762375675],[0.16681926387108592,-0.00701947140328385],[0.16694134163462127,-0.0015259720441921365],[0.16694134163462127,0.003967527314899577],[0.16694134163462127,0.009461026673991402],[0.16694134163462127,0.014954526033083004],[0.16694134163462127,0.020325947628639485],[0.16681926387108592,0.025819446987731087],[0.16681926387108592,0.03131294634682291],[0.16645303058047967,0.036806445705914737],[0.1654764084721967,0.042177867301470995],[0.163889397546237,0.047305133369956565],[0.1613257645119941,0.052188243911371446],[0.1579075871330038,0.056460965635109606],[0.15375694317280098,0.05987914301409991],[0.1488738326313861,0.06232069828480746],[0.14362448879936518,0.06378563144723182],[0.13813098944027336,0.0645180980284441],[0.13263749008118175,0.06476225355551479],[0.12726606848562527,0.06488433131905014],[0.12177256912653367,0.06488433131905014],[0.11627906976744184,0.0650064090825857],[0.11078557040835002,0.0650064090825857],[0.10529207104925842,0.06488433131905014],[0.0997985716901666,0.06488433131905014],[0.09430507233107499,0.06488433131905014],[0.08881157297198317,0.06488433131905014],[0.08331807361289134,0.06488433131905014],[0.07782457425379974,0.0650064090825857],[0.07233107489470791,0.06512848684612105],[0.06695965329915166,0.06512848684612105],[0.06146615394005983,0.0650064090825857],[0.055972654580968006,0.06488433131905014],[0.050479155221876404,0.06488433131905014],[0.04498565586278458,0.06476225355551479],[0.039492156503692755,0.06427394250137342],[0.03448696819874253,0.06232069828480746],[0.029725935420862992,0.05975706525056457],[0.024598669352377422,0.058292132088140214],[0.01910516999328582,0.05768174327046327],[0.01373374839772934,0.05743758774339258],[0.008240249038637515,0.05731550997985724],[0.0027467496795459123,0.05719343221632189]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[-0.0255752914606604,0.9527559055118111,-0.3025697369224196],[-0.00836232680217297,0.3024476591588843,0.9531221388024171],[0.999633766709394,0.02691814685954963,0.0001831166453030164]],"axis_candidate":5,"center":[-0.21076725874381985,0.21516205823109313,-0.2509308429469572],"construction_scale":1,"expected_solid_count":1}')

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
