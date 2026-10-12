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
PARAMETERS = json.loads('{"operation":"base_and_profile_pads","basis":[[0.9999999999999998,-1.1102230246251565e-16,-1.1102230246251565e-16],[-1.1102230246251565e-16,0.9999999999999998,-1.1102230246251565e-16],[-1.1102230246251565e-16,-1.1102230246251565e-16,0.9999999999999998]],"features":[{"type":"extrude","start":-0.049200341838603445,"length":0.09241850811866681,"loops":[[[0.41447930655597576,0.13710169698449493],[-0.4263215724575754,0.13759003784641677],[-0.42949578806006605,0.14003174215602465],[-0.4308387254303504,0.14491515077524086],[-0.42986204370650716,0.19924307166402144],[-0.4263215724575754,0.20205103162007076],[-0.4214381638383592,0.20241728726651176],[0.4268099133194969,0.20192894640459036],[0.4292516176291048,0.19973141252594284],[0.42986204370650705,0.1966792821389327],[0.42961787327554624,0.14003174215602465],[0.4308387254303503,0.12281772677328773],[0.42986204370650705,-0.18788914662434386],[0.4288853619826638,-0.2002197533878648],[0.4268099133194969,-0.2022952020510317],[0.42558906116469286,-0.2002197533878648],[0.4222927603467217,-0.18544744231473576],[0.42070565254547665,0.10303992186546185],[0.41936271517519197,0.1362471004761321]]]},{"type":"extrude","start":0.04321816628006325,"length":0.0059821755585396374,"loops":[[[0.4243682090098886,0.13856671957026],[-0.4263215724575754,0.1390550604321814],[-0.4288853619826639,0.1411305090953483],[-0.42986204370650716,0.14491515077524086],[-0.42900744719814443,0.1966792821389327],[-0.4263215724575754,0.19985349774142347],[-0.4214381638383592,0.20058600903430568],[0.4219265047002807,0.2008301794652667],[0.4270540837504575,0.19924307166402144],[0.4285191063362226,0.19423757782932483],[0.4291295324136244,0.14491515077524086],[0.4272982541814183,0.14003174215602465]]]},{"type":"extrude","start":0.04321816628006325,"length":0.0059821755585396374,"loops":[[[0.42986204370650705,0.12281772677328773],[0.42973995849102664,-0.19045293614943237],[0.4292516176291048,-0.19838847515565872],[0.4268099133194969,-0.20290562812843382],[0.4243682090098886,-0.1957026004150898],[0.42326944207056494,-0.17812232938591144],[0.42339152728604534,-0.03015504822366022],[0.4221706751312413,0.00695885728238288],[0.42278110120864354,0.11537052862898278],[0.4268099133194969,0.13258454401172015],[0.4292516176291048,0.12953241362471002]]]}],"axis_candidate":0,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[0.0021975338786470733,-0.16957636430228307,-0.3823708948846295],"construction_scale":1,"expected_solid_count":1}')

def build():
    return build_model(PARAMETERS)
if False:
    result = build()
    assert result.isValid() and len(result.Solids()) == PARAMETERS['expected_solid_count']
    result.exportStep(str(Path(__file__).with_suffix('.step')))
_original_normalized_build = build

def build():
    return _original_normalized_build().scale(2.0).translate((0.0, 0.0, 0.0))
