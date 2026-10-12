"""Editable CadQuery sketch/feature reconstruction. Approximate inferred design.
Run with Python + cadquery. No mesh or other input files required.
"""
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
        b = p['basis']
        shape = shape.located(cq.Location(cq.Plane(origin=(0, 0, 0), xDir=tuple(b[0]), normal=tuple(b[2]))))
    return shape.scale(1 / p['construction_scale']).translate(tuple(p['center']))
PARAMETERS = json.loads('{"center_xy":[0.0003051944088383607,-0.0033571384972227447],"profile":[[0.0007935054629799598,-0.012512970762375675],[0.0025025941524752238,-0.012268815235304875],[0.004089605078434921,-0.011902581944698731],[0.005676616004394841,-0.01104803759995121],[0.007141549166819194,-0.009949337728132779],[0.008240249038637515,-0.00860648232924377],[0.009216871146920491,-0.007141549166819305],[0.010071415491668123,-0.005676616004394841],[0.010925959836415755,-0.004211682841970377],[0.011780504181163387,-0.002624671916010457],[0.012512970762375675,-0.0011597387535859927],[0.013489592870658651,-0.0005493499359091603],[0.01483244826954766,-0.0011597387535859927],[0.01617530366843689,-0.0018922053347982803],[0.017640236830861244,-0.002624671916010457],[0.019227247756821164,-0.0033571384972227447],[0.020936336446316206,-0.004089605078434921],[0.02264542513581147,-0.004455838369041065],[0.024354513825306734,-0.0045779161325764095],[0.025941524751266654,-0.004699993896111865],[0.02752853567722635,-0.004699993896111865],[0.029237624366721615,-0.004699993896111865],[0.03045840200207528,-0.005798693767930185],[0.03131294634682291,-0.00726362693035465],[0.03228956845510589,-0.008850637856314458],[0.03314411279985352,-0.010193493255203578],[0.03399865714460115,-0.011536348654092698],[0.03497527925288413,-0.012512970762375675],[0.036562290178843826,-0.013123359580052507],[0.03827137886833909,-0.013367515107123196],[0.039980467557834354,-0.013367515107123196],[0.04156747848379427,-0.013245437343587851],[0.04303241164621863,-0.012879204052981708],[0.044375267045107636,-0.012268815235304875],[0.04535188915339061,-0.01104803759995121],[0.04584020020753221,-0.00946102667399129],[0.0460843557346029,-0.007751937984496138],[0.0460843557346029,-0.006042849295000874],[0.046206433498138244,-0.004333760605505721],[0.046206433498138244,-0.002624671916010457],[0.046206433498138244,-0.0007935054629799598],[0.046206433498138244,0.0009155832265153041],[0.046206433498138244,0.002624671916010568],[0.04632851126167359,0.004455838369041176],[0.04632851126167359,0.006164927058536218],[0.046206433498138244,0.007874015748031482],[0.04571812244399687,0.009583104437526746],[0.044863578099249235,0.011170115363486444],[0.04364280046389557,0.01239089299884033],[0.042666178355612594,0.013001281816517052],[0.04181163401086496,0.013367515107123307],[0.04022462308490504,0.013367515107123307],[0.03851553439540978,0.013367515107123307],[0.036806445705914737,0.013245437343587962],[0.03521943477995482,0.013123359580052396],[0.0336324238539949,0.013123359580052396],[0.031923335164499855,0.013123359580052396],[0.030336324238539936,0.013123359580052396],[0.02862723554904467,0.013123359580052396],[0.02691814685954963,0.013123359580052396],[0.025209058170054366,0.012879204052981708],[0.023622047244094446,0.012268815235304986],[0.02203503631813475,0.011536348654092698],[0.02044802539217483,0.010681804309345067],[0.01886101446621491,0.009827259964597435],[0.0175181590673259,0.008972715619849803],[0.016297381431972235,0.007874015748031482],[0.01532075932368926,0.006409082585607129],[0.014222059451870939,0.005066227186717898],[0.013123359580052396,0.004211682841970266],[0.011780504181163387,0.005066227186717898],[0.010681804309345067,0.006164927058536218],[0.009827259964597435,0.00701947140328385],[0.009094793383385147,0.00811817127510217],[0.007996093511566826,0.009094793383385147],[0.006897393639748506,0.010437648782274378],[0.005676616004394841,0.011414270890557354],[0.004089605078434921,0.01214673747176942],[0.0025025941524752238,0.012635048525911019],[0.0009155832265153041,0.012879204052981708]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","limitation":"Axisymmetric design approximation; asymmetric dents and bulges intentionally simplified","center":[-0.31282426905939087,-0.2799853506683757,-0.17084783006775317],"construction_scale":1,"expected_solid_count":1}')

def build():
    return build_model(PARAMETERS)
if __name__ == '__main__':
    result = build()
    assert result.isValid() and len(result.Solids()) == PARAMETERS['expected_solid_count']
    cq.exporters.export(result, str(Path(__file__).with_suffix('.step')))
_original_normalized_build = build

def build():
    return _original_normalized_build().scale(2.0).translate((0.0, 0.0, 0.0))
if __name__ == '__main__':
    result = build()
    result.exportStep(str(Path(__file__).with_suffix('.step')))
