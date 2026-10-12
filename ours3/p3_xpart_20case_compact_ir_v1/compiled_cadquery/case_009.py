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

PARAMETERS=json.loads(r'''{"operation":"extrude","basis":[[0.7917318287699828,0.20747641541611728,-0.5845142560191192],[-0.5585473487589425,-0.14307683259620063,-0.8182164213606598],[-0.2469444616368861,0.9735001795911842,-0.00025884266526077226]],"features":[{"type":"extrude","start":-6.5439194722285166,"length":13.918003448786749,"loops":[[[-15.242833404386026,17.890940259593023],[-48.25975598569429,17.826022991442585],[-49.610035163223216,17.423535928909928],[-50.19429057657708,16.852263969186154],[-50.49291001006905,16.086240205011094],[-50.635728,-8.322652619550276],[-50.51887691732923,-14.983164331784309],[-50.19429057657708,-16.502228406504344],[-49.73986969952408,-17.17736799526881],[-49.06473011075961,-17.644772325951898],[-47.76638474775103,-17.86549103766336],[-21.877378209359883,-17.83952413040319],[-10.841442623786925,-18.086209749374817],[4.206380133482554,-17.852507584033276],[25.29150882874194,-18.125160110265078],[47.93465195961163,-17.917424852183707],[49.47968294159185,-17.65775577958199],[50.21973979850674,-17.20333490252898],[50.62222686103941,-16.502228406504344],[50.765044850970355,14.761927934742332],[50.67416067555975,15.813587678779285],[50.44045851021819,16.319942370352635],[49.49266639522193,17.25475103171881],[47.85675123783112,17.540387011580705],[19.319120158902464,17.774089176922246],[10.334570246883061,17.644254640621384],[0.37626131260723383,17.215800670828557]],[[-10.80249226289667,-6.621820194009032],[-2.596949568682426,-7.829281381607011],[0.24642677630637877,-8.10193390783882],[2.3237793571201095,-8.024033186058304],[3.725992349169381,-7.7124302989362405],[4.569916835124957,-7.322926690033668],[5.180139155738992,-6.777621637570064],[5.400857867450448,-5.959664058874651],[5.361907506560186,-5.206623748329676],[4.855552814986851,-3.0513704457354223],[3.8298599782100666,-0.6624149777996351],[2.6223987906120882,1.0384174477416082],[0.8826160041805764,2.7392498732828585],[-0.597497709649204,3.5052736374579254],[-4.674302149496157,4.894503175877098],[-6.466018750448001,5.232072970259338],[-8.790056950233364,5.258039877519501],[-11.075144789128473,4.764668639576243],[-12.581225410218423,3.868810339100328],[-14.139239845828726,2.0381433772582227],[-15.022114692674563,-0.2729113688970557],[-15.16493268260551,-2.739767558613366],[-14.931230517263963,-3.817394209910489],[-14.489793093841044,-4.622368334975818],[-12.866861390080317,-6.076515141545428]],{"center":[-32.54977709329044,0.18150950815594058],"radius":6.634285962308603},{"center":[32.79594502693156,-0.38976245156783307],"radius":6.478484518747578}]}],"axis_candidate":5,"analytic_circles":true,"center":[0.1295756936356014,0.7657649215098061,0.20747641541611728],"construction_scale":162.07219282169618,"expected_solid_count":1}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
