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

PARAMETERS=json.loads(r'''{"operation":"base_and_profile_pads","basis":[[0.9999631971433798,-1.8401428310110823e-05,-1.8401428310110823e-05],[-1.8401428310110823e-05,0.9999631971433798,-1.8401428310110823e-05],[-1.8401428310110823e-05,-1.8401428310110823e-05,0.9999631971433798]],"features":[{"type":"extrude","start":-0.04922687431331274,"length":0.09240083573521307,"loops":[[[0.4145050502151617,0.13711102716535417],[-0.4264009587255083,0.13765627340230702],[-0.42953612458798773,0.13997356990935694],[-0.43089924018036996,0.14501709760117176],[-0.42994505926570237,0.1991327866187509],[-0.4264009587255083,0.20213164092199198],[-0.4214937425929318,0.20240426404046863],[0.42677309054660273,0.20185901780351556],[0.4292266986128912,0.19981434441494206],[0.42990825640908215,0.19667917855246264],[0.4296356332906057,0.13997356990935694],[0.43072612576451164,0.12279831344533942],[0.42990825640908215,-0.18799204161783578],[0.42881776393517623,-0.2002600819492768],[0.42677309054660273,-0.20230475533785042],[0.4255462865134587,-0.2002600819492768],[0.422274809091741,-0.18540212199230932],[0.42063907038088244,0.10303313735579533],[0.4194122663477382,0.13615684625068636]]]},{"type":"extrude","start":0.04319236285021022,"length":0.0059793071781721885,"loops":[[[0.4243194824803147,0.1386104543169746],[-0.4264009587255083,0.13915570055392767],[-0.42885456679179645,0.14120037394250118],[-0.42994505926570237,0.14501709760117176],[-0.4289908783510348,0.19667917855246264],[-0.4264009587255083,0.19995065597418016],[-0.4214937425929318,0.20049590221113323],[0.42186587441402645,0.20090483688884775],[0.4270457136650794,0.1991327866187509],[0.4285451408166998,0.1942255704861744],[0.4290903870536529,0.14501709760117176],[0.4273183367835558,0.13997356990935694]]]},{"type":"extrude","start":0.04319236285021022,"length":0.0059793071781721885,"loops":[[[0.42990825640908215,0.12279831344533942],[0.42977194484984405,-0.19044564968412392],[0.4292266986128912,-0.19835172011994162],[0.42677309054660273,-0.20285000157480337],[0.4243194824803147,-0.19562548893517695],[0.4233653015656469,-0.17804129779344458],[0.4233653015656469,-0.03014325601995993],[0.4221384975325029,0.0070697996520781015],[0.42268374376945594,0.11530117768723658],[0.42677309054660273,0.1324764341512541],[0.4292266986128912,0.1296138914072511]]]}],"axis_candidate":0,"thickness_regions":2,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[0.0022988950787399265,-0.16958998112067403,-0.3823723250915584],"construction_scale":1,"expected_solid_count":1}''')
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
