"""Native sketches and feature solids. No mesh import or triangle-face sewing."""
import cadquery as cq

def wire(data,z):
    plane=cq.Plane(origin=(0,0,z),normal=(0,0,1))
    wp=cq.Workplane(plane)
    if data['kind']=='circle':
        return wp.center(*data['center']).circle(data['radius']).val()
    if data['kind']=='polygon':
        return wp.polyline([tuple(p) for p in data['points']]).close().val()
    return wp.spline([tuple(p) for p in data['points']],periodic=True).wire().val()

def loft(wires):
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    builder=BRepOffsetAPI_ThruSections(True,False,1e-6)
    builder.SetMaxDegree(3)
    for w in wires:builder.AddWire(w.wrapped)
    builder.Build()
    if not builder.IsDone():raise ValueError('Smooth loft failed')
    body=cq.Shape.cast(builder.Shape())
    # Partition the SAME periodic NURBS surface into editable strips. The geometry
    # is unchanged, but STEP contains useful section boundaries like the tire CAD.
    return body

def partition_periodic_faces(body):
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    import numpy as np
    sewing=BRepBuilderAPI_Sewing(1e-5);changed=False
    for face in body.Faces():
        ad=BRepAdaptor_Surface(face.wrapped,True)
        u0,u1,v0,v1=ad.FirstUParameter(),ad.LastUParameter(),ad.FirstVParameter(),ad.LastVParameter()
        if face.geomType()=='BSPLINE' and ad.IsUClosed() and len(face.Wires())==1:
            surf=BRep_Tool.Surface_s(face.wrapped)
            vs=np.linspace(v0,v1,7)
            for a,b in zip(vs[:-1],vs[1:]):
                nf=BRepBuilderAPI_MakeFace(surf,u0,u1,float(a),float(b),1e-7).Face()
                nf.Orientation(face.wrapped.Orientation());sewing.Add(nf)
            changed=True
        else:sewing.Add(face.wrapped)
    if not changed:return body
    try:
        sewing.Perform();sh=cq.Shape.cast(sewing.SewedShape());shells=sh.Shells()
        if len(shells)!=1 or not shells[0].Closed():return body
        result=cq.Solid.makeSolid(shells[0]);fix=ShapeFix_Solid(result.wrapped);fix.Perform();result=cq.Shape.cast(fix.Solid())
        if result.isValid() and abs(result.Volume()-body.Volume())<max(abs(body.Volume()),1)*1e-5 and abs(result.Area()-body.Area())<max(body.Area(),1)*1e-5:return result
    except Exception:pass
    return body

def section_surface(sections,inner=None):
    """C2 periodic tensor-product B-spline from ordered fitted section curves."""
    import numpy as np
    from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.gp import gp_Pnt
    from OCP.Approx import Approx_IsoParametric
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeEdge,BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    sketches=[s['outer'] if inner is None else s['holes'][inner] for s in sections]
    if len(sections)<3:return loft([wire(sk,s['z']) for s,sk in zip(sections,sketches)])
    count=max([len(sk.get('points',[])) for sk in sketches]+[40]);rows=[]
    for s,sk in zip(sections,sketches):
        if sk['kind']=='circle':
            ts=np.linspace(0,2*np.pi,count,endpoint=False);q=np.c_[np.cos(ts),np.sin(ts)]*sk['radius']+sk['center']
        else:
            q=np.asarray(sk['points'])
            if len(q)!=count:raise ValueError('Inconsistent section sampling')
        rows.append(np.c_[q,np.full(len(q),s['z'])])
    arr=TColgp_Array2OfPnt(1,count,1,len(rows))
    for j,row in enumerate(rows):
        for i,p in enumerate(row):arr.SetValue(i+1,j+1,gp_Pnt(*map(float,p)))
    fit=GeomAPI_PointsToBSplineSurface();fit.Interpolate(arr,Approx_IsoParametric,True)
    if not fit.IsDone():raise ValueError('C2 surface interpolation failed')
    surf=fit.Surface();u0,u1,v0,v1=surf.Bounds()
    side=BRepBuilderAPI_MakeFace(surf,1e-7).Face();sew=BRepBuilderAPI_Sewing(1e-5);sew.Add(side)
    for v in (v0,v1):
        edge=cq.Edge(BRepBuilderAPI_MakeEdge(surf.VIso(v)).Edge());cap=cq.Face.makeFromWires(cq.Wire.assembleEdges([edge]));sew.Add(cap.wrapped)
    sew.Perform();body=cq.Shape.cast(sew.SewedShape());shells=body.Shells()
    if len(shells)!=1 or not shells[0].Closed():raise ValueError('Fitted surface and end caps did not form a closed shell')
    solid=cq.Solid.makeSolid(shells[0]);fix=ShapeFix_Solid(solid.wrapped);fix.Perform();return cq.Shape.cast(fix.Solid())

def build_normalized(spec):
    if spec['method']=='sphere':
        return cq.Workplane('XY').sphere(spec['radius']).val().translate(tuple(spec['sphere_center']))
    if spec['method']=='spline_revolve':
        points=spec['profile']; bounds=spec['breaks']
        wp=cq.Workplane('XZ').moveTo(0,points[0][1]).lineTo(*points[0])
        import math
        def tangent(i):
            a,b=points[max(0,i-1)],points[min(len(points)-1,i+1)]
            x,y=b[0]-a[0],b[1]-a[1];l=math.hypot(x,y)
            return (x/l,y/l)
        for a,b in zip(bounds[:-1],bounds[1:]):
            wp=wp.spline([tuple(p) for p in points[a+1:b+1]],includeCurrent=True,tangents=[tangent(a),tangent(b)],scale=False)
        body=wp.lineTo(0,points[-1][1]).close().revolve(360,(0,0),(0,1)).val()
        body=body.translate((*spec['axis_xy'],0))
    elif spec['method']=='radial_revolve':
        # Radius-height sections; through holes have an independently fitted inner profile.
        outer,inner=spec['outer'],spec['inner']
        wp=cq.Workplane('XZ').moveTo(*outer[0]).spline([tuple(p) for p in outer[1:]],includeCurrent=True)
        if inner:
            wp=wp.lineTo(*inner[0]).spline([tuple(p) for p in inner[1:]],includeCurrent=True).close()
        else: wp=wp.lineTo(0,outer[-1][1]).lineTo(0,outer[0][1]).close()
        body=wp.revolve(360,(0,0),(0,1)).val().translate((*spec['axis_xy'],0))
    else:
        parts=[]
        for feature in spec['features']:
            if spec['method']=='profile_extrude':
                body=cq.Solid.extrudeLinear(wire(feature['outer'],feature['z0']),[wire(h,feature['z0']) for h in feature['holes']],cq.Vector(0,0,feature['z1']-feature['z0']))
            elif spec['method'] in ('smooth_loft','tracked_smooth_loft'):
                secs=feature['sections']; body=section_surface(secs)
                for hi in range(len(secs[0]['holes'])):
                    tool=section_surface(secs,hi)
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
        if spec['method']=='tracked_smooth_loft':
            if len(parts)>1:
                body=parts[0].fuse(*parts[1:]).clean()
            for track in spec.get('hole_tracks',[]):
                tool=section_surface(track)
                body=body.cut(tool)
    # Local basis columns -> normalized source axes. Rigid transforms preserve analytic surfaces.
    from OCP.gp import gp_Trsf
    b=spec['basis'];t=gp_Trsf()
    t.SetValues(b[0][0],b[1][0],b[2][0],0,b[0][1],b[1][1],b[2][1],0,b[0][2],b[1][2],b[2][2],0)
    return body.located(cq.Location(t))

def build_model(spec):
    body=build_normalized(spec)
    if spec.get('partition_final',False):body=partition_periodic_faces(body)
    return body.scale(1/spec['construction_scale']).translate(tuple(spec['center']))

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_rank': 0, 'features': [{'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[47.91298436495759, -0.7811824094492252], [48.387286878305844, -0.8507356066792218], [48.65474645871395, -1.0763635493148944], [48.78447014858984, -1.5460981060012662], [48.64548319387406, -14.221918632867707], [48.096389768892706, -16.217604018039705], [47.61959749947157, -17.163969256888727], [47.31692211105481, -17.542935070142857], [46.51809759952317, -18.116798201762425], [45.34603712729679, -18.423249068437197], [43.15144444036761, -18.561342035447517], [31.948653717518184, -18.692898380889584], [11.007877572039437, -18.700369930329114], [2.2357822099555875, -18.83609708761425], [-44.58988850491736, -18.59667251313745], [-46.72581516206263, -18.266069953030122], [-47.171658946680495, -18.079300116266516], [-47.68644451440236, -17.659604817323995], [-48.32553426827573, -16.50496863390122], [-48.841973812646245, -14.455763000271094], [-49.01578809726802, -11.515314889087023], [-48.99651699351476, -1.6175578430778568], [-48.92030299530576, -1.0750355417560449], [-48.614374748539234, -0.7214376971863875], [-48.14164327307287, -0.6442738144054927], [-47.66858133789238, -0.8731082981417786], [-47.45473314122868, -1.6265690122953098], [-47.37089025827877, -13.615098651721603], [-47.06701001214347, -15.226834854850836], [-46.79012334057871, -15.84253373550976], [-46.25136691918743, -16.179346717416383], [-45.602351880749076, -16.280510167843353], [-40.86736753148227, -16.070807035814568], [-20.793101505531578, -16.024403397394924], [-19.69828515700758, -15.812730950849334], [-19.306396120021006, -15.163639313063971], [-18.803543243588244, -14.840283536494205], [-14.083233068202883, -14.776864357669236], [-12.66665846905908, -14.828685864467756], [-12.176330489187086, -15.042460494063752], [-11.233290948071135, -15.918848915602304], [-10.712041984554384, -16.02015443117492], [11.020322688295536, -16.135054339036476], [17.655675310916724, -15.923146423676275], [20.151606937189452, -16.079978619147223], [37.90361396189821, -16.049276689861554], [45.52908979045346, -16.23598050886867], [46.02118771257627, -16.09656959447757], [46.448909829720755, -15.712192240679945], [46.87278151990543, -14.73707310787398], [47.037253108075156, -13.972199708063973], [47.24524163425414, -1.5708454007097112], [47.40177030542944, -1.0301108725690635]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[-47.76704128659549, 18.843584127233726], [-47.2390571655976, 19.308862817439987], [-46.72543885856836, 19.52907932535406], [-44.075531123565234, 19.80938056211679], [-18.265632767746855, 19.85389374240117], [-2.473752897862324, 19.727219646109855], [39.32607293501198, 19.904357505779803], [44.04768493879271, 19.8793003651282], [45.931340829629065, 19.719109477966704], [46.84276726824946, 19.31470439388842], [47.44208837787729, 18.81108411739139], [48.197661770654705, 17.32374719617098], [48.61160792655533, 15.78566091970838], [48.74571840054234, 13.33393871398261], [48.722083291423544, 1.2921299548161753], [48.38297525977444, 0.8565458003853602], [47.88048594853817, 0.7918841840186087], [47.4419451712959, 0.9634827970779322], [47.23100582835076, 1.2926989864995013], [47.02547241368219, 15.018348300488226], [46.897720768830325, 15.930851363362756], [46.498341665521494, 16.929884910059723], [46.0416182950988, 17.34943619880158], [45.51854386995526, 17.508019392964517], [38.45691278849173, 17.21707995515638], [-11.190982414916967, 17.29134131173364], [-12.675287443502121, 16.821977660134408], [-14.796501439226624, 16.81856757832623], [-18.281725020899344, 16.848742718560203], [-18.799205509461128, 16.920927990286966], [-19.276084300655928, 17.235994442680898], [-19.748926634670603, 17.312647582319364], [-39.17255319883572, 17.2294958661385], [-45.744634652678464, 17.50212162183226], [-46.286123837984725, 17.44244382225768], [-46.72333451936268, 17.174065450723784], [-46.94272157992635, 16.849282814423624], [-47.20420647653352, 15.925820068469992], [-47.424796940079034, 13.018974250999184], [-47.50591097605886, 1.3041763996763696], [-47.667014227276574, 1.0048645012444573], [-48.02555141135778, 0.7971268762356326], [-48.61752703049717, 0.8193681577275422], [-48.977450278190524, 1.2877219694853363], [-49.021690149096585, 1.847585693526868], [-48.99636037976921, 13.278663401230846], [-48.77104184388666, 15.943057746450307], [-48.33789545544799, 17.740852538471998]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[35.75064921308045, -11.48440485065175], [35.8923124829536, -11.95813918650217], [35.82020270843748, -12.433132372877777], [35.560463253439785, -12.866021938806533], [35.13527199347728, -13.173763811656459], [34.66362838500198, -13.310444545931455], [34.19307107078029, -13.260193929888331], [33.679902614227714, -12.94708609021895], [33.356297348332745, -12.43375073559844], [33.27293683593118, -11.955127036665942], [33.41046014281209, -11.485964165773643], [33.74111437864169, -11.042416419638757], [34.191351951620376, -10.807198379894917], [34.664158421184666, -10.766759225082172], [35.13960447696719, -10.89818436032209]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[34.1803979617815, 10.265476799212275], [35.13441860966124, 10.354654203545888], [35.606897347449866, 10.75729636026552], [35.810744951866425, 11.230829110373145], [35.83853497881506, 11.69544982468444], [35.63229827416306, 12.193405795796734], [35.12878705399122, 12.620189682391949], [34.668480118631145, 12.746187506402133], [34.171096438995846, 12.702021269016816], [33.48622900374292, 12.174862826131276], [33.29394869369887, 11.698626342253384], [33.312561131829376, 11.229574791342186], [33.72102887305512, 10.536528837072211]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[15.73801907501312, 12.601414902439734], [16.676408612594077, 12.58657666909279], [17.226859437457787, 12.224978470594907], [17.497876906123285, 11.702330148173614], [17.524077144299763, 11.248291532286046], [17.16094412026128, 10.571554200017575], [16.6808089338412, 10.27887252112418], [16.211425868735315, 10.189540892314037], [15.725414246846114, 10.258554737579823], [15.262217148451034, 10.594139763123527], [14.934934979846268, 11.224278549418287], [14.959633918962412, 11.695508758925477], [15.216294578719232, 12.220295311022038]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[17.487365209554493, -12.388325857505935], [17.55280531606304, -11.961662120260645], [17.39775185850141, -11.488745048093824], [16.73818914957672, -10.941859738916179], [16.209605532449533, -10.823643403314264], [15.689248159714179, -10.916367371025526], [15.26504687128443, -11.246724872570445], [14.938721609602123, -11.959609078976902], [15.012823272725297, -12.428240865275919], [15.277189134804166, -12.89853187428192], [15.738249040223145, -13.21397097627973], [16.20839833387736, -13.277844326168871], [16.682271295631104, -13.177109631321393], [17.160441292076406, -12.909981288942426]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[-20.134386560199115, -10.942510445229729], [-20.69987375882405, -10.763078125418318], [-21.170648873793468, -10.836708948909944], [-21.602997764220305, -11.09289175986988], [-21.91388394940555, -11.485329465836285], [-22.052456146277937, -11.95871683282057], [-21.954949026794946, -12.427283376873742], [-21.64089016888869, -12.899539002613853], [-21.175308085193574, -13.204921517040193], [-20.696447809574128, -13.275029697940395], [-20.21940772805583, -13.13661844526279], [-19.90022833437536, -12.907866577899462], [-19.592878707893973, -12.431227097793453], [-19.488271163736353, -11.954323063877704], [-19.621361599330108, -11.485933907327071]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[-19.87065681214774, 10.606398276357524], [-19.517449629442925, 11.22823329951032], [-19.536563262211118, 11.699506044585185], [-19.76613362080815, 12.161960740816152], [-20.22279843919862, 12.534017729259416], [-20.686083952251508, 12.681391976503486], [-21.16755336200276, 12.611536917798633], [-21.775195942349356, 12.167563828757439], [-22.01984754167241, 11.701608621599755], [-22.039846404252614, 11.217687248400521], [-21.644386959929413, 10.524416461799147], [-21.189896029765595, 10.241290203165029], [-20.695099948877765, 10.180569890196256], [-20.23264651485748, 10.316810380511017]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[-1.7689163930422769, 12.524134867633112], [-2.2376091491791525, 12.665986526721383], [-2.7168621869056313, 12.620693584218953], [-3.2855201262762495, 12.240036581181007], [-3.5859817431775896, 11.699709353475614], [-3.6146156089704014, 11.226292121895721], [-3.422044252224037, 10.751927794760725], [-2.738763738438921, 10.238010858243875], [-2.239339652831813, 10.209307596261729], [-1.7782736886510462, 10.349311725116856], [-1.3268739472915727, 10.766007855110635], [-1.1350655509034648, 11.230061406841747], [-1.1305266755141603, 11.697793240867082], [-1.338813295362178, 12.15400355055711]]}, 'holes': []}, {'z0': -49.522680740635195, 'z1': 49.52418102669892, 'outer': {'kind': 'polygon', 'points': [[-3.553268023742934, -12.43208738834437], [-3.646966224832056, -11.959539333257943], [-3.5207985468571854, -11.483138436702843], [-3.1725269077289746, -11.041811856375869], [-2.717541069299765, -10.807560878602818], [-2.239937483190237, -10.784104871867388], [-1.7408164438226177, -10.989102386135533], [-1.3051761578960828, -11.487164684480561], [-1.1682429599401825, -11.961144968626284], [-1.258064216110177, -12.463338318992337], [-1.7717993405259063, -13.06232193346457], [-2.2389855312378706, -13.239578484365103], [-2.710913146493249, -13.209143336666699], [-3.215489081733078, -12.93731827841608]]}, 'holes': []}], 'center': [0.19861419, -0.186122415, 0.19664958000000002], 'construction_scale': 95.94832944507526, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
