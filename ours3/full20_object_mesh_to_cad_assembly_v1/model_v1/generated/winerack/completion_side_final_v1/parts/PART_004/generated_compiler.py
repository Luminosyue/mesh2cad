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
PARAMETERS = json.loads('{"operation":"extrude","basis":[[0.9999631971433798,-1.8401428310110823e-05,-1.8401428310110823e-05],[-1.8401428310110823e-05,0.9999631971433798,-1.8401428310110823e-05],[-1.8401428310110823e-05,-1.8401428310110823e-05,0.9999631971433798]],"features":[{"type":"extrude","start":-0.3354811487136057,"length":0.6710434047015195,"loops":[[[-0.000836270783739379,-0.02673546703900409],[0.009114473040651605,-0.02414554741347763],[0.018792593746566277,-0.016648411655374673],[0.024790302353048688,-0.006833979390221789],[0.026289729504669124,0.0005268448086428457],[0.023836121438381097,0.009387096159128028],[0.0189289053058046,0.018247347509613432],[0.009114473040651605,0.024381367675333943],[-0.000836270783739379,0.02669866418238387],[-0.010650703048892263,0.024517679234572265],[-0.017875215688518797,0.0189289053058046],[-0.023736612735762885,0.01047758863303394],[-0.026326532361289345,0.0005268448086428457],[-0.025372351446621644,-0.006833979390221789],[-0.020328823754807046,-0.016648411655374673],[-0.010650703048892263,-0.024418170531954164]]]}],"axis_candidate":0,"center":[-0.4554353208432522,0.44081318114814105,0.00025422169016642293],"construction_scale":1,"expected_solid_count":1}')

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
