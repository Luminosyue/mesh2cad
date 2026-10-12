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

PARAMETERS=json.loads(r'''{"center_xy":[-0.13777045888304684,0.11292773581173776],"profile":[[1.7149503458125679,-48.7609910494426],[5.029058187875357,-48.773220229671615],[8.35539521016716,-48.871053671503724],[11.693961412687969,-49.03003301448091],[15.038642205323292,-49.29907497951922],[18.383322997958608,-49.494741863183435],[21.728003790593938,-49.549773174214],[25.07879917334376,-49.58034612478654],[28.423479965979077,-49.59868989513006],[31.731473217927366,-49.39690842135133],[34.75819532460833,-48.26570925016753],[37.30797940235774,-46.09502975951755],[39.399169221519124,-43.45964142016504],[40.97673347106193,-40.598013246575775],[42.14462018293276,-37.5529473695513],[43.0556941099943,-34.299985428633576],[43.838361644651194,-31.065367258059382],[44.49873737701795,-27.794061546798147],[45.00013376640752,-24.473839114620855],[45.48318638545357,-21.15361668244356],[46.021270315530195,-17.83950884038077],[46.559354245606805,-14.525400998317984],[47.04852145476736,-11.211293156255195],[47.56826161450045,-7.909414494421426],[48.03297046320299,-4.583077472129624],[48.39373127995889,-1.2445112696088145],[48.63220029442467,2.087940342797495],[48.76672127694382,5.426506545318311],[48.88289848911945,8.771187337953627],[49.06022160244016,12.121982720703464],[49.262003076218896,15.46666351333878],[49.451555369768606,18.81134430597411],[49.61664930286029,22.156025098609426],[49.73282651503593,25.50682048135925],[49.80620159641001,28.857615864109086],[49.84288913709705,32.2022966567444],[49.8856912678986,35.553092039494224],[49.97129552950171,38.90388742224405],[50.06912897133382,42.254682804993884],[50.15473323293691,45.5993635976292],[49.549388811600714,48.55271062293608],[47.13412571637047,48.76060668682933],[45.9478952341561,46.1129891672478],[45.691082449346816,42.79276673507051],[45.519873926140626,39.44808594243518],[45.397582123850476,36.097290559685355],[45.27529032156034,32.75260976705004],[45.14076933904118,29.401814384300202],[45.00013376640752,26.057133591664886],[44.82281065308681,22.70633820891505],[44.61491458919358,19.361657416279733],[44.455935246216406,16.016976623644403],[44.32752885381175,12.672295831009087],[44.1930078712926,9.327615038373771],[44.05848688877345,5.982934245738441],[43.875049185338234,2.644368043217632],[43.654923941215976,-0.7003127494176908],[43.44091328720824,-4.032764361824],[43.15352755182641,-7.352986794001296],[42.853912636215576,-10.673209226178585],[42.51149558980318,-13.987317068241374],[42.07735969167319,-17.301424910304156],[41.60653625285615,-20.62164734248145],[41.147941994268116,-23.966328135116772],[40.609858064191506,-27.34158187832463],[39.93725315159573,-30.66180431050192],[39.105668896022785,-33.90253707119062],[37.87663628300688,-36.947602948215106],[35.67538384178436,-38.91650096508636],[32.440765671210166,-39.161084569666635],[29.102199468689356,-38.97153227611692],[25.763633266168547,-38.74529244188016],[22.41283788341871,-38.549625558215936],[19.062042500668888,-38.37841703500974],[15.723476298148064,-38.243896052490584],[12.384910095627255,-38.109375069971435],[9.070802253564466,-38.0849167095134],[6.037965556769002,-38.109375069971435],[3.6288170516532503,-39.748085220659306],[1.3419603488276408,-41.53354553409534]],"method":"axisymmetric_spline_revolve","segments":12,"fitting":"median of 16 meridian cross-sections; spline profile with shared endpoint tangents","operation":"revolve","basis":[[0.0028651137506088276,0.0028651137506088276,0.9995433024152476],[0.9995433024152476,0.0028651137506088276,0.0028651137506088276],[0.0028651137506088276,0.9995433024152476,0.0028651137506088276]],"axis_candidate":1,"center":[-0.0032494763638908353,0.0028651137506088276,-0.0032494763638908353],"construction_scale":50.576639950837894,"expected_solid_count":1}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
