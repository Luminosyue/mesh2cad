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

PARAMETERS=json.loads(r'''{"operation":"extrude","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.32320087895989746,"length":0.6463407190380273,"loops":[[[-0.0025025941524751127,0.180003662332906],[0.05011292193127015,0.1267777574314839],[0.055118110236220375,0.12506866874198863],[0.060001220777635256,0.1267777574314839],[0.06488433131905014,0.12372581334309962],[0.11920893609229077,0.060245376304706166],[0.12409204663370565,0.05707135445278633],[0.14386864432643587,0.05548434352682663],[0.15595434291643784,0.0440090337545016],[0.18354391747543186,0.013611670634193995],[0.14594396630653717,-0.025941524751266543],[0.13886345602148564,-0.02801684673136784],[0.12409204663370565,-0.02777269120429715],[0.11994140267350306,-0.030824635292681424],[0.06988951962400058,-0.09284013916865042],[0.060001220777635256,-0.09113105047915526],[0.05548434352682663,-0.09491546114875171],[-0.008972715619849803,-0.17341146310199596],[-0.013977903924800139,-0.17487639626442042],[-0.01886101446621502,-0.17267899652078378],[-0.02398828053470059,-0.17389977415613744],[-0.09039858389794297,-0.25276200939998783],[-0.09284013916865042,-0.25520356467069527],[-0.09784532747360064,-0.2532503204541293],[-0.10272843801501552,-0.24909967649392661],[-0.1076115485564304,-0.2511749984740279],[-0.1615699200390649,-0.30208142586827813],[-0.18500885063785633,-0.321735945797473],[-0.18378807300250255,-0.3267411341024232],[-0.1815906732588659,-0.32832814502838303],[-0.17670756271745103,-0.3266190563388879],[-0.1509491546114875,-0.3046450589025209],[-0.1076115485564304,-0.2627723860098883],[-0.10272843801501552,-0.259720441921504],[-0.09784532747360064,-0.2638710858817066],[-0.09284013916865042,-0.26533601904413107],[-0.08795702862723553,-0.2620399194286761],[-0.023866202771165246,-0.18696209485442228],[-0.01886101446621502,-0.18281145089421957],[-0.013977903924800139,-0.18513092840139167],[-0.008972715619849803,-0.18537508392846247],[-0.004089605078434921,-0.18085820667765362],[0.029970090947933903,-0.13800891167673812],[0.060001220777635256,-0.10272843801501552],[0.06488433131905014,-0.10053103827137888],[0.06988951962400058,-0.10248428248794483],[0.07501678569248615,-0.09992064945370205],[0.12409204663370565,-0.038637612158945234],[0.12909723493865588,-0.03521943477995482],[0.14386864432643587,-0.03607397912470245],[0.14875175486785075,-0.03363242385399501],[0.19074650552401873,0.00860648232924377],[0.193798449612403,0.013611670634193995],[0.19160104986876636,0.018494781175608876],[0.18818287248977605,0.022279191845205437],[0.14875175486785075,0.06219862052127212],[0.14386864432643587,0.06402978697430273],[0.12909723493865588,0.06415186473783807],[0.12409204663370565,0.06634926448147471],[0.06891289751571761,0.13190502349996946],[0.06488433131905014,0.13520112311542443],[0.060001220777635256,0.13654397851431366],[0.055118110236220375,0.13520112311542443],[0.05011292193127015,0.13703228956845503],[0.007385704693890105,0.18122443996825988],[-0.05340902154672522,0.23457242263321731],[-0.10455960446804613,0.2749801623634256],[-0.15204785448330582,0.3147775132759567],[-0.17670756271745103,0.33064762253555524],[-0.1820789843130074,0.32918268937313067],[-0.18256729536714889,0.3242995788317158],[-0.17670756271745103,0.31819569065494724],[-0.16681926387108592,0.315509979857169],[-0.16193615332967104,0.3124580357687847],[-0.04986876640419946,0.22175425746200328]]]}],"axis_candidate":2,"center":[-0.07758041872672894,0.3048892144295916,0.025941524751266654],"construction_scale":1,"expected_solid_count":1}''')
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
