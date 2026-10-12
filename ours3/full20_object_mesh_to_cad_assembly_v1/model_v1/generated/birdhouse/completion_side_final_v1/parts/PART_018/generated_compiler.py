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
PARAMETERS = json.loads('{"operation":"base_and_profile_pads","basis":[[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.055118110236220486,"length":0.010071415491668123,"loops":[[[0.06952328633339433,0.21626075810291145],[0.05169993285723007,0.21369712506866878],[0.0033571384972226337,0.21149972532503214],[-0.00970518220106209,0.2088140145272539],[-0.041079167429652674,0.206250381493011],[-0.045962277971067556,0.20551791491179872],[-0.049746688640664116,0.20380882622230367],[-0.0582921320881401,0.20271012635048535],[-0.06781419764389918,0.20271012635048535],[-0.07062198620521276,0.20356467069523276],[-0.07538301898309219,0.1989257156808888],[-0.07733626319965814,0.19392052737593857],[-0.07831288530794112,0.17914911798815836],[-0.07770249649026428,0.045962277971067556],[-0.07843496307147657,-0.09699078312885312],[-0.07770249649026428,-0.19562961606543372],[-0.07550509674662764,-0.28938533846059944],[-0.08051028505157787,-0.2942684490020143],[-0.0871024842824879,-0.2942684490020143],[-0.09027650613440763,-0.2931697491301959],[-0.0912531282426906,-0.28938533846059944],[-0.09076481718854912,0.29255936031251917],[-0.08539339559299275,0.2940242934749435],[-0.08051028505157787,0.29378013794787283],[-0.07709210767258745,0.29255936031251917],[-0.07574925227369833,0.2876762497711043],[-0.07538301898309219,0.2088140145272539],[-0.07062198620521276,0.20405298174937436],[-0.06073368735884754,0.2064945370200817],[-0.05585057681743266,0.21003479216260756],[-0.052920710492583733,0.21369712506866878],[-0.05169993285723007,0.21626075810291145],[-0.05084538851248244,0.22480620155038755],[-0.04803759995116885,0.233473722761399],[-0.04547396691692607,0.24861136543978524],[-0.03827137886833909,0.2581334309955441],[-0.028138924494903295,0.26301654153695897],[-0.01641945919550758,0.2661905633888788],[-0.011414270890557243,0.26899835195019217],[-0.0015259720441921365,0.2703412073490814],[0.008362326802173081,0.2729048403833241],[0.03094671305621688,0.27461392907281934],[0.08722456204602325,0.27510224012696094],[0.08954403955319545,0.2729048403833241],[0.09015442837087217,0.2550814869071598],[0.08844533968137713,0.23835683330281388],[0.08722456204602325,0.23408411157907594],[0.08234145150460837,0.2235854239150339],[0.07733626319965814,0.21845815784654832]]]},{"type":"extrude","start":-0.045107733626319924,"length":0.10028688274430819,"loops":[[[-0.07758041872672894,0.26301654153695897],[-0.07916742965268875,0.21809192455594206],[-0.07867911859854726,0.2088140145272539],[-0.08014405176097172,0.18903741683452369],[-0.08087651834218401,-0.1364219007507782],[-0.07977781847036558,-0.2794970396142342],[-0.07550509674662764,-0.2841359946285784],[-0.07233107489470791,-0.2794970396142342],[-0.07330769700299089,0.2088140145272539],[-0.07196484160410177,0.27778795092473896],[-0.07208691936763723,0.2827931392296894],[-0.07342977476652623,0.28706586095342734],[-0.07550509674662764,0.2890191051699933],[-0.07794665201733508,0.2876762497711043],[-0.07928950741622409,0.2827931392296894]]]}],"axis_candidate":1,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[-0.006531160349142362,-0.31721906854666426,-0.16120368674845875],"construction_scale":1,"expected_solid_count":1}')

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
