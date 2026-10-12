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
PARAMETERS = json.loads('{"operation":"extrude","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.49996948055911616,"length":1.0,"loops":[[[-0.29951779283403523,-0.3105047915522188],[-0.2993957150704999,0.3503021424647501],[-0.3014710370506012,0.44649942013062316],[-0.29976194836110603,0.46127082951840315],[-0.2963437709821156,0.4665201733504243],[-0.27900872856009273,0.47030458402002084],[-0.20502960385765734,0.4751876945614357],[0.05389733260086671,0.4771409387780017],[0.21906854666422504,0.4736006836354758],[0.2708295184032228,0.4699383507294146],[0.28181651712140643,0.46383446255264604],[0.28450222791918445,0.4588292742476958],[0.2853567722639321,0.4515046084355734],[0.285967161081609,0.3282060672648477],[0.2903619605688823,0.16535433070866135],[0.2940242934749435,-0.1182323139840078],[0.30293597021302565,-0.4139046572666789],[0.3024476591588843,-0.451016297381432],[0.29927363730696444,-0.45834096319355433],[0.28315937252029544,-0.4704266617835561],[0.2041750595129097,-0.47482146127082947],[-0.017640236830861244,-0.47762924983214305],[-0.15827382042360982,-0.4768967832509309],[-0.25434902032594764,-0.47445522798022344],[-0.2838918391015076,-0.47189159494598054],[-0.2913385826771654,-0.4685954953305256],[-0.2939022157114082,-0.46334615149850455],[-0.29561130440090333,-0.4486968198742599]]]}],"axis_candidate":2,"center":[-6.103888176767214e-05,0.00042727217237370496,-0.0001831166453030164],"construction_scale":1,"expected_solid_count":1}')

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
