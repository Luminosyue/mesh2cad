"""Inferred standard-feature CAD. Approximate reconstruction, not recovered design history."""
from pathlib import Path
import json
"""Pure CadQuery feature builder. Input contains sketches, never a triangle mesh."""
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp=cq.Workplane('XY',origin=(0,0,z))
    if isinstance(points,dict):
        return wp.center(*points['center']).circle(points['radius']).val()
    if smooth:
        return wp.spline([tuple(p) for p in points],periodic=True).wire().val()
    return wp.polyline([tuple(p) for p in points]).close().wire().val()

def build_model(p):
    if p['operation']=='revolve':
        pts=p['profile']; n=len(pts)
        wp=cq.Workplane('XZ').moveTo(0,pts[0][1]).lineTo(*pts[0])
        bounds=sorted(set(int(i*(n-1)/p['segments']) for i in range(p['segments']+1)))
        def tangent(k):
            a,b=pts[max(0,k-1)],pts[min(n-1,k+1)];x,y=b[0]-a[0],b[1]-a[1];d=sqrt(x*x+y*y);return (x/d,y/d)
        for a,b in zip(bounds[:-1],bounds[1:]):
            wp=wp.spline([tuple(q) for q in pts[a+1:b+1]],includeCurrent=True,tangents=[tangent(a),tangent(b)],scale=False)
        shape=wp.lineTo(0,pts[-1][1]).close().revolve(360,(0,0),(0,1)).val().translate((*p['center_xy'],0))
    else:
        features=[]
        for feature in p['features']:
            if feature['type']=='extrude':
                wires=[sketch_wire(q,feature['start']) for q in feature['loops']]
                shape=cq.Workplane('XY').newObject(wires).toPending().extrude(feature['length'],combine=False).val()
            else:
                wires=[sketch_wire(q,z,feature.get('smooth',False)) for z,q in feature['sections']]
                shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()
                for pocket in feature.get('pockets',[]):
                    pw=[sketch_wire(q,z,True) for z,q in pocket]
                    tool=cq.Workplane('XY').newObject(pw).toPending().loft(ruled=True,combine=False).val()
                    shape=shape.cut(tool)
            features.append((shape,feature.get('cut',False)))
        shape=features[0][0]
        for addition,cut in features[1:]:
            shape=shape.cut(addition) if cut else shape.fuse(addition)
        shape=shape.clean()
    if 'basis' in p:
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS=json.loads(r'''{"operation":"base_and_profile_pads","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.40523713605566747,"length":0.7613379722883478,"loops":[[[0.08978819508026614,0.001281816517121337],[-0.04571812244399687,0.07013367515107127],[-0.05304278825611919,0.07159860831349563],[-0.05865836537874625,0.06683757553561609],[-0.07367393029359703,0.043276567173289315],[-0.09235182811450893,0.011170115363486444],[-0.09662454983824698,0.001281816517121337],[-0.0993102606360251,-0.017396081303790556],[-0.09894402734541907,-0.06525056460965639],[-0.09491546114875171,-0.07013367515107127],[-0.09003235060733683,-0.07147653054996028],[0.09247390587804438,-0.07111029725935425],[0.09686870536531766,-0.06769211988036383],[0.09747909418299461,-0.06525056460965639],[0.09247390587804438,-0.00592077153146553]]]},{"type":"extrude","start":0.3560397973509126,"length":0.04913629982298717,"loops":[[[-0.0377830678141976,0.06549472013672708],[-0.05060123298541175,0.07086614173228356],[-0.055606421290361974,0.06879081975218204],[-0.08160898492339619,0.028505157785509327],[-0.09503753891228717,0.003845449551364233],[-0.09784532747360064,-0.00701947140328385],[-0.09906610510895442,-0.023377891717023758],[-0.0995544161630959,-0.06280900933894895],[-0.09747909418299461,-0.06854666422511135],[-0.09247390587804427,-0.07135445278642494],[-0.07770249649026428,-0.07184276384056643],[0.0816089849233963,-0.07172068607703108],[0.08991027284380149,-0.07159860831349574],[0.09491546114875171,-0.06988951962400047],[0.09760117194652995,-0.06525056460965639],[0.09454922785814568,-0.029725935420863103],[0.09198559482390278,-0.006042849295000874],[0.08844533968137713,0.0003051944088383607]]]}],"axis_candidate":2,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[0.002624671916010568,0.021058414209851772,0.4276994445461759],"construction_scale":1,"expected_solid_count":1}''')
def build():
    return build_model(PARAMETERS)
if False:
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))

_original_normalized_build = build
def build():
    return _original_normalized_build().scale(2.0).translate((0.0, 0.0, 0.0))

if __name__=="__main__":
    result=build()
    result.exportStep(str(Path(__file__).with_suffix(".step")))
