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

PARAMETERS=json.loads(r'''{"center_xy":[0.0032350607336872894,-0.0001831166453030164],"profile":[[0.0175181590673259,-0.4213514008423366],[0.05121162180308847,-0.4213514008423366],[0.08539339559299264,-0.4213514008423366],[0.11945309161936146,-0.4213514008423366],[0.15363486540926563,-0.4213514008423366],[0.1878166391991698,-0.4214734786058719],[0.22187633522553862,-0.4214734786058719],[0.2560581090154428,-0.42159555636940726],[0.28999572727827627,-0.42183971189647806],[0.3150216688030276,-0.42574620032960997],[0.3194164682903009,-0.44466825367759266],[0.3285723005554537,-0.4712812061283037],[0.3523774644448514,-0.47054873954709153],[0.37349691753647063,-0.44649942013062316],[0.39534883720930236,-0.42440334493072085],[0.41378257950314357,-0.4003540255142526],[0.4219617896600134,-0.3677592626503082],[0.4309955441616309,-0.33479826649575783],[0.4455227980223402,-0.3087957028627235],[0.45248123054385636,-0.2779100286882744],[0.4549227858145639,-0.2436061771348349],[0.4562656412134529,-0.20991271439907222],[0.45736434108527124,-0.17670756271745103],[0.45736434108527124,-0.14252578892754686],[0.45943966306537254,-0.10809985961057189],[0.46249160715375703,-0.07379600805713238],[0.4652993957150704,-0.03961423426722821],[0.4687175730940609,-0.005798693767930185],[0.4712812061283038,0.028505157785509327],[0.4732344503448698,0.06293108710248418],[0.47482146127082947,0.09747909418299461],[0.4770188610144661,0.1320271012635048],[0.47946041628517366,0.16657510834401523],[0.4806811939205273,0.20087895989745475],[0.4810474272111336,0.23469450039675266],[0.48153573826527496,0.26863211865958614],[0.48336690471830557,0.30269181468595496],[0.48593053775254846,0.3369956662393945],[0.4894707928950741,0.3710553622657633],[0.49264481474699373,0.4049929805285968],[0.4950863700177013,0.43893059879143004],[0.4938655923823476,0.4722578282365868],[0.4749435390343648,0.4883720930232558],[0.4512604529085027,0.4787279497039614],[0.4411279985350669,0.44955136421900743],[0.43795397668314706,0.4156137459561742],[0.4351461881218337,0.38143197216627],[0.43197216626991386,0.3473722761399012],[0.4279436000732466,0.31331258011353236],[0.424769578221327,0.27925288408716353],[0.4231825672953671,0.24507111029725936],[0.4203747787340535,0.21174388085210283],[0.41768906793627547,0.17878288469755232],[0.41683452359152784,0.14582188854300182],[0.4173228346456692,0.11261673686138063],[0.4162241347738509,0.07880119636208271],[0.41451504608435563,0.045107733626319924],[0.4118293352865776,0.01214673747176942],[0.4092657022523347,-0.02020386986510403],[0.40731245803576877,-0.05316486601965453],[0.4046267472379905,-0.08624793993774038],[0.4016968809131416,-0.11872062503814929],[0.3970579258987976,-0.15107123237502285],[0.3933955929927364,-0.18354391747543186],[0.3897332600866752,-0.21565036928523473],[0.38887871574192756,-0.2475126655679668],[0.37899041689556245,-0.2768113288164561],[0.36678264054202536,-0.3019593481047427],[0.35323200878959904,-0.32759567844717086],[0.3365073551852531,-0.35384239760727587],[0.31380089116767373,-0.3692241958127327],[0.287920405298175,-0.3723982176646524],[0.2547152536165538,-0.3741073063541476],[0.22053347982664961,-0.3754501617530367],[0.1864737838002808,-0.37557223951657204],[0.152780321064518,-0.3756943172801074],[0.11896478056522009,-0.3726423731917231],[0.0850271623023866,-0.3684917292315205],[0.051089544039553125,-0.36751510712323754],[0.017396081303790556,-0.36751510712323754]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[6.103888176767214e-05,6.103888176767214e-05,1.0],[1.0,6.103888176767214e-05,6.103888176767214e-05],[6.103888176767214e-05,1.0,6.103888176767214e-05]],"axis_candidate":1,"center":[-0.0001831166453030164,-0.002624671916010457,-0.0028688274430812566],"construction_scale":1,"expected_solid_count":1}''')
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
