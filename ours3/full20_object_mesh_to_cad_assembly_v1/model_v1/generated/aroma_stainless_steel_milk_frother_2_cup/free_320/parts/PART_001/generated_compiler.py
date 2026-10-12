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

PARAMETERS=json.loads(r'''{"center_xy":[0.0001831166453030164,0.0003051944088383607],"profile":[[0.00970518220106209,-0.4461331868400171],[0.028505157785509327,-0.4461331868400171],[0.047549288897027475,-0.4461331868400171],[0.0665934200085454,-0.44625526460355247],[0.0855154733565282,-0.44747604223890614],[0.10443752670451079,-0.4486968198742599],[0.12323750228895802,-0.4505279863272905],[0.14203747787340526,-0.45211499725325033],[0.16071537569431738,-0.4549227858145639],[0.17914911798815836,-0.45577733015931143],[0.19794909357260582,-0.45528901910516995],[0.21674906915705305,-0.45577733015931143],[0.2350607336873589,-0.4572422633217359],[0.2530061649270585,-0.4554110968687054],[0.26973081853140446,-0.4517487639626442],[0.28572300555453833,-0.4505279863272905],[0.29023988280534696,-0.4356344991759751],[0.28169443935787086,-0.41952023438930597],[0.2783983397424159,-0.4019410364402124],[0.27717756210706224,-0.3830189830922297],[0.27717756210706224,-0.36397485198071167],[0.27717756210706224,-0.3450527986327291],[0.27644509552584995,-0.3261307452847464],[0.2755905511811023,-0.3072086919367637],[0.27412561801867796,-0.28816456082524566],[0.27278276261978873,-0.26924250747726297],[0.272172373802112,-0.2503204541292804],[0.2716840627479704,-0.23127632301776235],[0.2710736739302937,-0.21235426966977966],[0.2705853628761521,-0.19343221632179697],[0.27046328511261675,-0.17438808521027893],[0.27021912958554606,-0.15546603186229624],[0.26997497405847515,-0.1364219007507782],[0.26997497405847515,-0.11749984740279562],[0.26973081853140446,-0.09845571629127758],[0.26912042971372774,-0.07953366294329489],[0.26899835195019217,-0.060855765122383],[0.2698528962949398,-0.041933711774400306],[0.27021912958554606,-0.02288958066288227],[0.2700970518220107,-0.003967527314899577],[0.26997497405847515,0.015076603796618349],[0.26997497405847515,0.034120734908136496],[0.27021912958554606,0.05316486601965442],[0.27021912958554606,0.07220899713117257],[0.2703412073490814,0.0912531282426905],[0.27046328511261675,0.11029725935420864],[0.27046328511261675,0.12934139046572657],[0.2705853628761521,0.14838552157724472],[0.27070744063968744,0.16742965268876264],[0.27070744063968744,0.1864737838002808],[0.2708295184032228,0.20551791491179872],[0.2708295184032228,0.22456204602331686],[0.2708295184032228,0.2436061771348348],[0.2708295184032228,0.26265030824635294],[0.27070744063968744,0.28169443935787086],[0.2705853628761521,0.300738570469389],[0.2705853628761521,0.31978270158090694],[0.27070744063968744,0.3388268326924251],[0.27070744063968744,0.357870963803943],[0.27070744063968744,0.37691509491546116],[0.2708295184032228,0.39583714826344374],[0.27119575169382903,0.41475920161142654],[0.2755905511811023,0.43172801074284317],[0.28657754989928574,0.4466214978941585],[0.2846243056827198,0.45943966306537254],[0.2693645852407984,0.4561435634499176],[0.2532503204541292,0.4450344869681988],[0.2360373557956419,0.43661112128425805],[0.21809192455594206,0.43111762192516623],[0.19941402673503017,0.4273332112555699],[0.1804919733870476,0.42525788927546837],[0.16156992003906478,0.42440334493072096],[0.14252578892754686,0.42391503387657936],[0.12360373557956428,0.42354880058597333],[0.10455960446804613,0.4231825672953671],[0.0855154733565282,0.42306048953183173],[0.0665934200085454,0.42281633400476104],[0.047549288897027475,0.42257217847769035],[0.028505157785509327,0.422450100714155],[0.00970518220106209,0.422450100714155]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0]],"axis_candidate":0,"center":[-0.15241408777391197,-0.20783739241897092,-0.001281816517121448],"construction_scale":1,"expected_solid_count":1}''')
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
