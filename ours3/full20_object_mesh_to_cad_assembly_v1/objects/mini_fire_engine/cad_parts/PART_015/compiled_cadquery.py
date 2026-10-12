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

PARAMETERS=json.loads(r'''{"operation":"extrude","basis":[[6.103888176767214e-05,1.0,6.103888176767214e-05],[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.260697064029787,"length":0.5214551669413416,"loops":[[[0.03790514557773306,0.08466092901178057],[0.02313373618995307,0.08807910639077088],[-0.006409082585607018,0.0896661173167308],[-0.02130256973692246,0.08820118415430622],[-0.04095708966611733,0.08295184032228531],[-0.05084538851248244,0.07867911859854737],[-0.06073368735884754,0.07281938594884951],[-0.07550509674662764,0.06097784288591823],[-0.08539339559299275,0.04925837758652252],[-0.09284013916865042,0.03631813465177314],[-0.0979674052371361,0.02154672526399315],[-0.0993102606360251,0.006653238112677817],[-0.09650247207471163,-0.013001281816517163],[-0.0912531282426906,-0.02777269120429715],[-0.08356222913996214,-0.04266617835561248],[-0.0704999084416773,-0.059390831959958534],[-0.06073368735884754,-0.06866874198864681],[-0.04095708966611733,-0.0811206738692547],[-0.02130256973692246,-0.08807910639077088],[-0.006409082585607018,-0.09003235060733683],[0.013245437343587962,-0.08978819508026614],[0.033022035036318176,-0.0855154733565281],[0.047793444424098164,-0.07941158517975955],[0.05768174327046327,-0.07367393029359703],[0.06622718671793937,-0.06732588658975769],[0.08002197399743638,-0.0525544772019777],[0.08905572849905385,-0.03766099005066226],[0.09503753891228706,-0.02288958066288227],[0.09894402734541896,-0.003112982970151945],[0.09931026063602522,0.011658426417628043],[0.09747909418299461,0.02642983580540803],[0.09235182811450904,0.04120124519318802],[0.07831288530794112,0.06097784288591823],[0.06757004211682838,0.07025575291460662],[0.052676554965513045,0.0790453518891534]]]}],"axis_candidate":2,"center":[-0.05926875419642308,0.2776658731612036,-0.376548861624855],"construction_scale":1,"expected_solid_count":1}''')
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
