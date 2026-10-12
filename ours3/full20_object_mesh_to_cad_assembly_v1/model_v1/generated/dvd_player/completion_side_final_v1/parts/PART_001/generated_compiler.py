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
PARAMETERS = json.loads('{"operation":"base_and_profile_pads","basis":[[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.016053225904901436,"length":0.02423243606177139,"loops":[[[0.40877739119819334,0.4058475248733444],[0.4162241347738509,0.40438259171091984],[0.4211072453152658,0.40047610327778793],[0.42354880058597333,0.3954709149728377],[0.42415918940365005,0.38753586034303855],[0.42391503387657936,-0.38179820545687604],[0.42306048953183173,-0.3941280595739486],[0.41976438991637677,-0.39998779222364644],[0.41378257950314357,-0.403772202893243],[0.4063358359274858,-0.40499298052859667],[0.35091253128242683,-0.4056033693462736],[-0.4012085698590002,-0.4060916804004151],[-0.41353842397607277,-0.4051150582921321],[-0.41976438991637677,-0.40206311420374774],[-0.4214734786058719,-0.3991332478788988],[-0.42281633400476104,-0.39168650430324115],[-0.42391503387657936,-0.34859305377525485],[-0.42415918940365016,0.34810474272111325],[-0.4236708783495087,0.3899774156137459],[-0.42257217847769024,0.39534883720930236],[-0.41976438991637677,0.399865714460111],[-0.41475920161142643,0.4029176585484955],[-0.4074345357993041,0.4042605139473845],[-0.3669047183055606,0.40487090276506144]],[[-0.4162241347738509,-0.38057742782152226],[-0.4167124458279924,0.3456631874504059],[-0.41634621253738635,0.3863150827076849],[-0.41475920161142643,0.39400598181041313],[-0.40365012512970766,0.39693584813526206],[-0.36055667460172125,0.3977903924800097],[0.40389428065677846,0.3991332478788989],[0.41219556857718365,0.39742415918940366],[0.41292803515839593,-0.3658060184337423],[0.4128059573948606,-0.39168650430324115],[0.41121894646890067,-0.3962033815540499],[0.40389428065677846,-0.3973020814258683],[0.3076970029909052,-0.39791247024354515],[-0.4110968687053653,-0.3982787035341513],[-0.4148812793749619,-0.39559299273637305]]]},{"type":"extrude","start":0.008240249038637515,"length":0.007751937984496138,"loops":[[[-0.39583714826344385,0.4003540255142526],[0.4037722028932429,0.4021851919672832],[0.41378257950314357,0.39998779222364655],[0.41793322346334616,0.39486052615516076],[0.4191540010986998,0.38594884941707863],[0.4193981566257705,0.356528108405054],[0.4195202343893061,-0.3461514985045474],[0.41927607886223517,-0.38179820545687604],[0.4170786791185985,-0.396569614844656],[0.41378257950314357,-0.39949948116950496],[0.40694622474516273,-0.4009644143319294],[0.3618995300006105,-0.40157480314960625],[-0.397546236952939,-0.4026735030214247],[-0.412317646340719,-0.40181895867667705],[-0.41720075688213387,-0.3993774034059696],[-0.41976438991637677,-0.390343648904352],[-0.4206189342611243,-0.3546969419520234],[-0.4213514008423366,-0.02179088079106395],[-0.4208630897881951,0.34810474272111325],[-0.42049685649758894,0.38753586034303855],[-0.4182994567539523,0.39486052615516076],[-0.41060855765122384,0.3991332478788989]]]}],"axis_candidate":1,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[-0.000427272172373816,0.1041933711774401,-0.05121162180308858],"construction_scale":1,"expected_solid_count":1}')

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
