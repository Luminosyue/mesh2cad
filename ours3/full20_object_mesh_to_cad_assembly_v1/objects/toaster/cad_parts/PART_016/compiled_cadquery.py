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

PARAMETERS=json.loads(r'''{"operation":"base_and_profile_pads","basis":[[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05]],"features":[{"type":"extrude","start":-0.04364280046389546,"length":0.015809070377830636,"loops":[[[-0.239699688701703,-0.009094793383385258],[-0.23469450039675277,-0.008240249038637626],[-0.23188671183543919,-0.010193493255203578],[-0.23176463407190384,-0.021424647500457805],[-0.23225294512604533,-0.02264542513581147],[-0.23469450039675277,-0.024598669352377422],[-0.239699688701703,-0.023866202771165246],[-0.24092046633705666,-0.021424647500457805],[-0.24116462186412746,-0.012146737471769531]]]},{"type":"extrude","start":-0.02777269120429715,"length":0.05023499969480549,"loops":[[[-0.239699688701703,-0.03241164621864123],[-0.24116462186412746,-0.02935970213025696],[-0.24079838857352132,0.0001831166453030164],[-0.239699688701703,0.002258438625404313],[-0.2371360556674602,0.0032350607336872894],[-0.23469450039675277,0.003112982970151945],[-0.23225294512604533,0.0009155832265153041],[-0.23164255630836839,-0.002258438625404424],[-0.23176463407190384,-0.02935970213025696],[-0.23261917841665136,-0.0318012574009644],[-0.23469450039675277,-0.033022035036318176]]]},{"type":"extrude","start":0.022523347372276126,"length":0.010559726545809722,"loops":[[[-0.22480620155038755,0.013001281816517052],[0.18452053958371484,0.014466214978941627],[0.21650491362998237,0.01532075932368926],[0.22138802417139725,0.01641945919550758],[0.2267594457669535,0.02044802539217483],[0.22895684551059015,0.02484282487944811],[0.22920100103766106,0.02984801318439856],[0.23029970090947938,0.03228956845510589],[0.23127632301776235,0.03277787950924749],[0.2371360556674602,0.03228956845510589],[0.23933345541109685,0.02984801318439856],[0.23982176646523845,0.027284380150155663],[0.23847891106634922,0.01995971433803323],[0.23591527803210655,0.014954526033083004],[0.23127632301776235,0.010315571018739034],[0.22138802417139725,0.0067753158762131616],[0.2090581700543246,0.005066227186717898],[0.17133614112189455,0.003967527314899577],[-0.22480620155038755,0.0025025941524752238],[-0.2298113898553379,0.0016480498077275918],[-0.2306659342000854,0.0001831166453030164],[-0.23200878959897453,-0.007996093511566826],[-0.23469450039675277,-0.010071415491668234],[-0.2371360556674602,-0.010193493255203578],[-0.239699688701703,-0.008484404565708314],[-0.24043215528291517,-0.004699993896111865],[-0.23994384422877368,0.0175181590673259],[-0.23872306659342002,0.01995971433803323],[-0.23469450039675277,0.021058414209851772],[-0.23188671183543919,0.01995971433803323],[-0.2309100897271562,0.014954526033083004],[-0.2298113898553379,0.013367515107123307]]]},{"type":"extrude","start":0.033022035036318176,"length":0.005310382713788586,"loops":[[[-0.239699688701703,-0.0018922053347982803],[-0.2371360556674602,-0.004455838369041065],[-0.23469450039675277,-0.004699993896111865],[-0.23200878959897453,-0.0027467496795459123],[-0.23078801196362086,0.0076298602209607935],[-0.2311542452542269,0.015442837087224603],[-0.23225294512604533,0.018494781175608876],[-0.23445034486968197,0.019227247756821164],[-0.2371360556674602,0.018983092229750254],[-0.2389672221204907,0.0175181590673259],[-0.23982176646523834,0.015442837087224603],[-0.24018799975584448,0.002624671916010568]]]},{"type":"extrude","start":0.038393456631874434,"length":0.005310382713788586,"loops":[[[-0.239699688701703,0.013245437343587962],[-0.239699688701703,0.002258438625404313],[-0.2371360556674602,-0.0009155832265153041],[-0.23469450039675277,-0.0009155832265153041],[-0.23225294512604533,0.0006714276994446156],[-0.23164255630836839,0.0023805163889396574],[-0.2311542452542269,0.010071415491668123],[-0.23164255630836839,0.01532075932368926],[-0.23225294512604533,0.016297381431972235],[-0.23469450039675277,0.01727400354025521],[-0.2371360556674602,0.016907770249648957]]]}],"axis_candidate":1,"thickness_regions":5,"limitation":"Inferred few-region profile pads; curved transitions simplified","center":[0.15021668803027532,0.08331807361289134,0.07941158517975944],"construction_scale":1,"expected_solid_count":1}''')
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
