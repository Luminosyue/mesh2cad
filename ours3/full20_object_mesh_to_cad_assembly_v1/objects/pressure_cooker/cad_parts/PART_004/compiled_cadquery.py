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

PARAMETERS=json.loads(r'''{"center_xy":[0.01861685893914422,-0.0005493499359091603],"profile":[[0.009461026673991402,-0.25825550875907954],[0.02752853567722635,-0.2615516083745346],[0.04535188915339061,-0.26765549655130316],[0.0631752426295551,-0.27510224012696083],[0.08099859610571936,-0.28291521699322464],[0.09857779405481293,-0.28962949398767013],[0.1161569920039065,-0.2952450711102973],[0.13349203442592938,-0.3012268815235305],[0.15082707684795205,-0.30781908075444053],[0.16865043032411653,-0.31428920222181533],[0.18635170603674545,-0.3205151681621192],[0.2041750595129097,-0.32576451199414025],[0.22273087957028626,-0.32967100042727215],[0.24116462186412746,-0.3321125556979796],[0.25959836415796866,-0.3328450222791919],[0.2779100286882745,-0.33406579991454555],[0.29671000427272176,-0.33638527742171764],[0.31563205762070434,-0.3388268326924251],[0.33479826649575783,-0.3406579991454557],[0.35274369773545744,-0.3399255325642434],[0.3710553622657633,-0.33797228834767745],[0.3874137825795032,-0.33089177806262593],[0.3990111701153636,-0.31612036867484583],[0.4070683025086981,-0.29829701519868157],[0.41378257950314357,-0.28010742843191117],[0.4190319233351645,-0.2625282304828176],[0.4217176341329427,-0.2440944881889764],[0.4219617896600134,-0.22505035707745835],[0.42232802295061944,-0.20600622596594031],[0.4226942562412257,-0.18684001709088693],[0.4226942562412257,-0.16791796374290424],[0.42281633400476104,-0.14899591039492155],[0.4229384117682964,-0.1301959348104743],[0.4229384117682964,-0.11115180369895628],[0.42306048953183173,-0.09210767258743824],[0.4231825672953671,-0.07294146371238475],[0.4233046450589024,-0.053775254837331365],[0.423426722822438,-0.034609045962277984],[0.4236708783495087,-0.015564914850759948],[0.423792956113044,0.0036012940242935443],[0.423792956113044,0.022767502899346814],[0.4236708783495087,0.041933711774400306],[0.4236708783495087,0.0610999206494538],[0.42354880058597333,0.08014405176097172],[0.42354880058597333,0.09931026063602522],[0.423426722822438,0.11847646951107849],[0.4233046450589024,0.13764267838613198],[0.4233046450589024,0.15680888726118547],[0.4231825672953671,0.1758530183727034],[0.42306048953183173,0.1950192272477569],[0.42306048953183173,0.21418543612281016],[0.4231825672953671,0.23335164499786365],[0.4231825672953671,0.25251785387291714],[0.4229384117682964,0.27156198498443507],[0.42281633400476104,0.2906061160959532],[0.4222059451870841,0.3085515473356528],[0.4167124458279925,0.31905023499969487],[0.4005981810413233,0.3205151681621192],[0.382408594274553,0.31880607947262396],[0.36385277421717643,0.316486601965452],[0.3455411096868706,0.31380089116767373],[0.32735152292010006,0.31074894707928946],[0.3085515473356528,0.3064762253555515],[0.2898736495147409,0.3009827259964597],[0.27156198498443507,0.29414637123847887],[0.25251785387291714,0.28865287187938726],[0.23383995605200503,0.28401391686504307],[0.21626075810291145,0.28108405054019414],[0.19868156015381788,0.2774217176341329],[0.18122443996825988,0.2705853628761521],[0.16486601965451997,0.26240615271928225],[0.149117988158457,0.25361655374473546],[0.13336995666239404,0.2436061771348348],[0.11749984740279551,0.23383995605200503],[0.10089727156198491,0.22419581273271083],[0.08380638466703294,0.21565036928523473],[0.06610510895440402,0.20783739241897092],[0.047549288897027475,0.20185558200573772],[0.02862723554904467,0.1977049380455349],[0.009827259964597435,0.19550753830189826]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0]],"axis_candidate":0,"center":[-0.017029848013184412,0.018006470121467277,-0.14008423365683942],"construction_scale":1,"expected_solid_count":1}''')
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
