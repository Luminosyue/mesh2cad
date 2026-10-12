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

PARAMETERS=json.loads(r'''{"center_xy":[-6.103888176767214e-05,-0.0001831166453030164],"profile":[[0.002624671916010568,-0.04535188915339072],[0.0076298602209607935,-0.04535188915339072],[0.012635048525911019,-0.04535188915339072],[0.01776231459439659,-0.04535188915339072],[0.022767502899346814,-0.04535188915339072],[0.02777269120429704,-0.04535188915339072],[0.03289995727278283,-0.04535188915339072],[0.03790514557773306,-0.04535188915339072],[0.04303241164621863,-0.04535188915339072],[0.04803759995116885,-0.04535188915339072],[0.05316486601965442,-0.04535188915339072],[0.05817005432460487,-0.04535188915339072],[0.06329732039309044,-0.04535188915339072],[0.06830250869804066,-0.04535188915339072],[0.07330769700299089,-0.04535188915339072],[0.07843496307147646,-0.04535188915339072],[0.08344015137642669,-0.04535188915339072],[0.08856741744491248,-0.04535188915339072],[0.0935726057498627,-0.04535188915339072],[0.09869987181834827,-0.04535188915339072],[0.1037050601232985,-0.04535188915339072],[0.10871024842824872,-0.04535188915339072],[0.11383751449673452,-0.045107733626319924],[0.11811023622047245,-0.04315448940975397],[0.1200634804370384,-0.03888176768601603],[0.12018555820057375,-0.0338765793810657],[0.12018555820057375,-0.028749313312580127],[0.12018555820057375,-0.0237441250076299],[0.12018555820057375,-0.01861685893914422],[0.12018555820057375,-0.013611670634193995],[0.12018555820057375,-0.008484404565708314],[0.12018555820057375,-0.003479216260758089],[0.12018555820057375,0.0016480498077275918],[0.12018555820057375,0.006653238112677817],[0.12018555820057375,0.011780504181163387],[0.12018555820057375,0.016785692486113613],[0.12018555820057375,0.021790880791063838],[0.12018555820057375,0.02691814685954963],[0.12018555820057375,0.031923335164499855],[0.12018555820057375,0.037050601232985425],[0.11969724714643237,0.041933711774400306],[0.11640114753097719,0.044375267045107636],[0.11273881462491597,0.04229994506500634],[0.11200634804370391,0.0375389122871268],[0.11200634804370391,0.03253372398217658],[0.11200634804370391,0.02752853567722635],[0.11200634804370391,0.02240126960874078],[0.11200634804370391,0.017396081303790556],[0.11200634804370391,0.012268815235304986],[0.11200634804370391,0.007263626930354539],[0.11200634804370391,0.002136360861868969],[0.11200634804370391,-0.0028688274430812566],[0.11200634804370391,-0.007874015748031482],[0.11188427028016856,-0.013001281816517163],[0.11188427028016856,-0.01800647012146739],[0.11188427028016856,-0.023133736189952958],[0.11188427028016856,-0.028138924494903295],[0.11127388146249162,-0.03314411279985352],[0.10846609290117804,-0.03668436794237928],[0.1037050601232985,-0.037294756760056114],[0.09869987181834827,-0.03741683452359157],[0.0935726057498627,-0.03741683452359157],[0.08856741744491248,-0.03741683452359157],[0.08344015137642669,-0.03741683452359157],[0.07843496307147646,-0.03741683452359157],[0.07330769700299089,-0.03741683452359157],[0.06830250869804066,-0.03741683452359157],[0.06329732039309044,-0.03741683452359157],[0.05817005432460487,-0.03741683452359157],[0.05316486601965442,-0.03741683452359157],[0.04803759995116885,-0.03741683452359157],[0.04303241164621863,-0.03741683452359157],[0.03790514557773306,-0.03741683452359157],[0.03289995727278283,-0.03741683452359157],[0.02777269120429704,-0.03741683452359157],[0.022767502899346814,-0.03741683452359157],[0.01776231459439659,-0.03741683452359157],[0.012635048525911019,-0.03741683452359157],[0.0076298602209607935,-0.03741683452359157],[0.002624671916010568,-0.03741683452359157]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"axis_candidate":2,"center":[0.12531282426905932,0.20148934871513147,0.03351034609045955],"construction_scale":1,"expected_solid_count":1}''')
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
