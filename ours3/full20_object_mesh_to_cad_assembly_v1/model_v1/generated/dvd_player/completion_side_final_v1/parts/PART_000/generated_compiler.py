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
PARAMETERS = json.loads('{"operation":"extrude","basis":[[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0]],"features":[{"type":"extrude","start":-0.2000244155527071,"length":0.4001098699871819,"loops":[[[-0.3697125068668742,-0.05768174327046327],[0.3897332600866752,-0.05682719892571564],[0.3946163706280901,-0.05194408838430076],[0.39583714826344374,-0.04449734480864309],[0.39583714826344374,0.03473112372581344],[0.39425013733748404,0.05169993285723007],[0.3902215711408168,0.05658304339864495],[0.3802111945309161,0.057559665506927926],[-0.019227247756821053,0.05768174327046327],[-0.3820423609839467,0.05768174327046327],[-0.39095403772202897,0.05658304339864495],[-0.3952267594457669,0.05169993285723007],[-0.3959592260269792,-0.04449734480864309],[-0.39510468168223156,-0.05194408838430076],[-0.39193065983031194,-0.056216810108038806]]]}],"axis_candidate":0,"center":[-0.0001831166453030164,0.022279191845205437,-0.18708417261795762],"construction_scale":1,"expected_solid_count":1}')

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
