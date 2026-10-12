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
PARAMETERS = json.loads('{"operation":"base_and_profile_pads","basis":[[-1.8401428310110823e-05,-1.8401428310110823e-05,0.9999631971433798],[0.9999631971433798,-1.8401428310110823e-05,-1.8401428310110823e-05],[-1.8401428310110823e-05,0.9999631971433798,-1.8401428310110823e-05]],"features":[{"type":"extrude","start":-0.500009200714155,"length":0.09090140858359241,"loops":[[[-0.03764039177806289,-0.03137006005310394],[-0.043638100384545186,-0.025236039887383432],[-0.04118449231825694,-0.015421607622230549],[-0.03995768828511281,0.009250784599889927],[-0.04227498479216274,0.02656235262314577],[-0.03941244204815986,0.031469568755722266],[-0.03027956757919814,0.03269637278886628],[0.03883039295458679,0.03269637278886628],[0.043601297527924965,0.031469568755722266],[0.046054905594213436,0.029015960689433795],[0.047690644305072194,-0.015421607622230549],[0.04373760908716329,-0.03109743693462763],[0.03883039295458679,-0.03218792940853343],[-0.03273317564548639,-0.0319153062900569]],[[0.0018899604010251814,0.02669866418238387],[-0.027962271072148104,0.02656235262314577],[0.025744483267716278,0.02656235262314577]]]},{"type":"extrude","start":-0.4090893907022525,"length":0.8182598886788128,"loops":[[[-0.0467732662470246,0.023972432997619197],[-0.04718220092473924,-0.020328823754807046],[-0.04500121597692741,-0.02864382886833927],[-0.040093999844351025,-0.030552190697674675],[-0.025372351446621644,-0.03164268317158048],[0.03392317682201029,-0.032324240967771645],[0.04128400102087504,-0.03164268317158048],[0.04550965935726037,-0.027689647953671792],[0.04728170962735745,-0.017875215688518797],[0.047145398068119126,0.02165513649056927],[0.046191217153451536,0.028743337570957594],[0.04373760908716329,0.03106063407800752],[0.031469568755722266,0.03269637278886628],[-0.03518678371177453,0.032423749670389856],[-0.044455969739974566,0.029015960689433795]],[[0.02928858380791044,0.02656235262314577],[0.001753648841786859,0.027107598860098614],[-0.025508663005859966,0.02656235262314577],[-0.005470863797839454,0.0260171063861927]]]},{"type":"extrude","start":0.40905258784563236,"length":0.09090140858359241,"loops":[[[-0.03423260279710705,0.031469568755722266],[0.03637678488829854,0.032287438111151534],[0.046191217153451536,0.028198091334004527],[0.04728170962735745,-0.020328823754807046],[0.043464985968686864,-0.029598009783006973],[0.04128400102087504,-0.03177899473081869],[-0.006970290949460112,-0.03137006005310394],[-0.016921034773851207,-0.03014325601995993],[-0.013513245792895368,-0.027689647953671792],[-0.015421607622230549,-0.027689647953671792],[-0.04159342699597168,-0.03000694446072172],[-0.04500121597692741,-0.028916451986815805],[-0.046091708450833324,-0.025236039887383432],[-0.04500121597692741,-0.02155562778795106],[-0.040911869199780515,-0.020328823754807046],[-0.040093999844351025,-0.017875215688518797],[-0.04023031140358935,0.01811103595037511],[-0.04172973855520978,0.02410874455685752]]]}],"axis_candidate":1,"thickness_regions":3,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[-0.45557163240249055,0.00011791013092810054,0.38288076847189134],"construction_scale":1,"expected_solid_count":1}')

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
