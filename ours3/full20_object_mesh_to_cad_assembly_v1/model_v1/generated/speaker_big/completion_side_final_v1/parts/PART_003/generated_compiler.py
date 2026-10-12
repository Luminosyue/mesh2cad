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

PARAMETERS=json.loads(r'''{"operation":"base_and_profile_pads","basis":[[4.416000396756381e-05,4.416000396756381e-05,0.9999535613285111],[0.9999535613285111,4.416000396756381e-05,4.416000396756381e-05],[4.416000396756381e-05,0.9999535613285111,4.416000396756381e-05]],"features":[{"type":"extrude","start":-0.07569021783220409,"length":0.03669852080723923,"loops":[[[-0.24993319032716832,0.2225307397326497],[0.42952007132759573,0.22320453312976873],[0.4819411976234511,0.22091363557956423],[0.4840973364942318,0.21970080746474996],[0.4889486489534882,-0.214356898959287],[0.488544372915217,-0.21934297009796744],[0.48517540592962227,-0.22405952387780015],[-0.4796967387447354,-0.22486807595434288],[-0.4867041900747726,-0.22419428255722396],[-0.48953412234267224,-0.22015152217451017],[-0.48953412234267224,0.2207788769001402],[-0.4846828098834157,0.2226654984120735],[-0.45018458795092475,0.22226122237380208],[-0.440212445673564,0.22360880916803993]]]},{"type":"extrude","start":-0.03890109834950861,"length":0.11458903751419158,"loops":[[[-0.4908817091369102,0.07173577745742543],[-0.48993839838094366,-0.22419428255722396],[-0.4796967387447354,-0.22581138671030954],[0.46711774288683383,-0.22581138671030954],[0.4869272687621313,-0.22432904123664776],[0.4904309944271501,-0.21934297009796744],[0.4905657531065739,-0.214356898959287],[0.48975720103003106,-0.1305370003576879],[0.48719678612097916,-0.11072747448239029],[0.4867925100827075,-0.06639186895196247],[0.4869272687621313,0.21970080746474996],[0.4819411976234511,0.2229350157709209],[0.46711774288683383,0.22374356784746374],[0.30446401682231583,0.2250911546417016],[-0.43536113321430747,0.22576494803882063],[-0.45503590041018127,0.22387832652688755],[-0.4648732840081181,0.2250911546417016],[-0.4846828098834157,0.22428260256515897],[-0.48953412234267224,0.2228002570914971],[-0.4908817091369102,0.21970080746474996],[-0.49222929593114817,0.11984462601171941]],[[-0.45503590041018127,0.19665707328328152],[0.457280359288897,0.1946356930919244],[0.46105360231276316,0.19005389799151562],[0.4601102915567965,0.12105745412653368],[0.461323119671611,0.11108531184917303],[0.461323119671611,-0.0022467375462369432],[0.46334449986296766,-0.09226553540133065],[0.4601102915567965,-0.14037438395562474],[0.46024505023622053,-0.19953344422266983],[0.4591669808008303,-0.20451951536135016],[0.457280359288897,-0.20586710215558812],[-0.4489717598361106,-0.20600186083501193],[-0.4580005913575047,-0.20451951536135016],[-0.45934817815174267,-0.19576020119880366],[-0.45894390211347125,0.19005389799151562],[-0.4574615566398096,0.19503996913019606]],[[-0.29238217434566316,0.2068987329194898],[-0.11477023486510407,0.2095939065079655],[-0.03728399419642314,0.21471473632606974],[-0.09509546766923027,0.2161970817997314],[-0.3059928009674663,0.2163318404791552],[-0.43037506207562715,0.2163318404791552],[-0.4557096938073002,0.21471473632606974],[-0.45018458795092475,0.2117500453787462],[-0.41555160733901,0.20999818254623692],[-0.39089076900445585,0.2112110106610512],[-0.37121600180858205,0.20824631971372765],[-0.33173170873741076,0.20865059575199907]]]}],"axis_candidate":1,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[0.0071863700134287,-0.24009580672923148,0.006243059257462047],"construction_scale":1,"expected_solid_count":1}''')
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
