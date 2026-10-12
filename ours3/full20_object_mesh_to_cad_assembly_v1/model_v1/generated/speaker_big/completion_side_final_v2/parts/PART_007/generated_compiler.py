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
PARAMETERS = json.loads('{"operation":"extrude","basis":[[4.416000396756381e-05,0.9999535613285111,4.416000396756381e-05],[4.416000396756381e-05,4.416000396756381e-05,0.9999535613285111],[0.9999535613285111,4.416000396756381e-05,4.416000396756381e-05]],"features":[{"type":"extrude","start":-0.22608090406915704,"length":0.45229428815021655,"loops":[[[0.3737299780461454,-0.48791701818958677],[0.3737299780461454,0.4944737548098639],[0.3589065233095283,0.49622561764237316],[0.22576494803882063,0.4974384457571872],[0.16444974890099484,0.5006726540633584],[0.14194504943722142,0.4977079631160348],[0.11512807223188659,0.4973036870777636],[-0.3660951719904779,0.49609085896294935],[-0.3685208282201061,0.49353044405389723],[-0.36879034557895385,0.4808631281880609],[-0.36879034557895385,-0.4757887370414454],[-0.36703848274644457,-0.48791701818958677],[-0.33860440138802417,-0.48980363970151986],[-0.26745181865226153,-0.48939936366324843],[-0.2576144350543247,-0.4972153670698285],[-0.25262836391564425,-0.4973501257492523],[-0.21813014198315328,-0.4972153670698285],[-0.20829275838521633,-0.48993839838094366],[-0.19832061610785578,-0.48912984630440093],[-0.18875274986876645,-0.4927683306488433],[-0.18646185231856194,-0.4977544017875236],[-0.17864584891198187,-0.4993715059406092],[-0.1441476269794909,-0.49815867782579504],[-0.13916155584081058,-0.49007315706036747],[-0.13431024338155406,-0.4885908115867057]]]}],"axis_candidate":2,"center":[0.0022002988747482632,0.060281289706402896,0.004625955104376578],"construction_scale":1,"expected_solid_count":1}')

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
