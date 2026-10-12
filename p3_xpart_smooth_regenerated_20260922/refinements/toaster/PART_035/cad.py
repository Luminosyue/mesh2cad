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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_rank': 0, 'features': [{'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[-47.62112050934289, 10.702528704651465], [-47.66814705399188, 1.8738734041219747], [-47.87643443851779, 1.3460213933284375], [-48.383957277826276, 1.152736191910426], [-48.97270455551788, 1.3766276152119594], [-49.20187264668693, 1.8543544078917304], [-49.23940576363393, 2.3338984956146285], [-49.15583844994775, 12.621196286518508], [-49.030125138722, 14.876684701907902], [-48.42026223517345, 17.115954658500247], [-47.860252437424805, 18.07105404786167], [-46.965746045203495, 18.725747108576446], [-45.95040992631373, 19.061098760946237], [-43.45065482330612, 19.235371999009647], [-33.24841961732904, 19.263028990922358], [2.9415508162258157, 18.941495077132714], [38.14611960583005, 18.89272044671417], [45.88115906886663, 18.691026301628597], [47.3390216984954, 18.334238832636125], [48.344732010029254, 17.669785999820263], [48.73324182073957, 17.169865121128414], [49.057943361887446, 16.4402050011348], [49.495609448128626, 14.924523477354166], [49.65514987026658, 12.956725039669136], [49.629773313483895, 1.3769917662011908], [49.25221091410228, 0.7541796043627856], [48.77345963681332, 0.5739473243986845], [48.26814895083205, 0.8003023595577416], [47.98822794622894, 1.3914426628896894], [47.97986349905768, 13.15478884321902], [47.62066747042345, 15.250194166147862], [47.363542538154405, 15.7879768067842], [46.85505736279011, 16.018906674120895], [36.57479898832327, 16.036489570285095], [12.418377601729784, 16.376230264330452], [10.963322202739072, 16.61536672331612], [-0.26830661451519766, 16.58844546627126], [-18.669381369542037, 16.871166634222], [-20.203950421602535, 16.69838691704198], [-31.361864742370212, 16.883692637032734], [-45.44115198777495, 16.93533657821087], [-46.453909587612046, 16.646712778716747], [-46.91390615522832, 16.194956755351352], [-47.14307217303655, 15.735092387063856], [-47.47347042861318, 14.239927070164256]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[49.623811097057754, -1.967255027321589], [49.592866910772386, -13.992999594896562], [49.318613812996865, -15.94007114226952], [48.74672540160693, -17.277230731908546], [47.885252690634275, -18.31085330717272], [47.36187680846872, -18.754435064647385], [46.92133975342054, -18.943830215454916], [45.95585362950375, -19.128352036569876], [12.423571333209441, -19.234464229357194], [-12.056724834557633, -19.124720171458915], [-29.18345948555347, -18.749916793913943], [-45.607474264769394, -18.548041676128666], [-47.134790813174746, -18.29373687982291], [-47.48453530147737, -18.05868475290867], [-48.44603396930642, -16.78796050569261], [-48.81749312307238, -15.99484972159542], [-49.063259063507644, -15.025004593314614], [-49.344966732923034, -11.447028314454249], [-49.26479223559177, -1.1171462670587964], [-48.91495772211848, -0.4708823548633775], [-48.38358497792406, -0.34677462852852564], [-47.928878136591365, -0.5584992186544396], [-47.729373853212515, -1.0164156748665036], [-47.6697807582208, -12.463659742812636], [-47.55269666605154, -14.207281675643312], [-47.29461044947482, -15.38072051197222], [-46.94813371751864, -16.07201661887856], [-46.53438683176191, -16.392567145044765], [-45.773290062559944, -16.51676648024529], [-40.11435123438898, -16.423096781191685], [-19.65730787971877, -16.640060450987548], [-18.22535867196632, -16.388347267679173], [-14.52365242539602, -16.396065998310256], [-12.0332158513658, -16.41071734692988], [-11.051998881196822, -16.687660805233847], [10.949978144206852, -16.811334505940387], [12.417159580529228, -16.664685332155464], [18.613576654185017, -16.657066506188094], [20.426135072138376, -16.76354101388659], [43.486491219921625, -16.908314826876563], [45.88128212474938, -17.01891546860392], [46.86070056329528, -16.826914271146965], [47.34174173188305, -16.34883099826145], [47.7145661936466, -15.250654673087437], [47.889004554390546, -12.89243178235349], [47.96602235697961, -1.9884071334718116], [48.05499973003812, -1.495531877311118], [48.29205288742561, -1.1868297312630394], [48.76946781122076, -0.967974073059675], [49.25294460130472, -1.1718675946360944], [49.53072141070835, -1.4952940096100211]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[17.187859619816667, -11.94777312527917], [17.734622591326733, -11.59238433327242], [18.03431755009559, -11.069963533585574], [18.033625687413696, -10.588183594747123], [17.735220554425656, -10.061799819960923], [17.1866581243706, -9.70557718218132], [16.7135902575493, -9.59385093497258], [16.22795715802304, -9.641597893110493], [15.749940310846311, -9.90236799461074], [15.31755891279517, -10.589111681599837], [15.332126365311982, -11.070841133155215], [15.59493843729893, -11.54647287554909], [16.219695232724458, -11.984276128612743]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[34.44223796213098, -11.964763580660874], [34.898030109352696, -12.189973764792787], [35.372662949824736, -12.229191874985402], [35.89646795297094, -12.057972041745424], [36.40416417144168, -11.602912745350242], [36.577694990199, -11.069723776669262], [36.48526865441178, -10.589781671884085], [36.222480372740556, -10.184786898996235], [35.371073274927134, -9.726193946631904], [34.89376160818233, -9.769861614694694], [34.365215242359305, -10.059696707837977], [34.02851099767896, -10.588719076984356], [33.96290514861904, -11.069133772919605], [34.10075669909799, -11.5443415948587]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[-19.6121351041569, -10.010322697293761], [-20.088363185319587, -9.568246422812226], [-20.628308349733196, -9.39275513235609], [-21.103053309189132, -9.429562690439463], [-21.563185127959724, -9.65974779851095], [-21.940583959857797, -10.109665289592039], [-22.075107579980408, -10.592713776743881], [-21.944049152018604, -11.068836251525351], [-21.573711138187708, -11.524489281406597], [-21.10473842444987, -11.773064533838], [-20.622579471746544, -11.830121763897024], [-20.14393522614396, -11.681912911312576], [-19.530480100236563, -11.068107163663912], [-19.41982524852421, -10.589171866853262]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[-39.295983698955396, -11.815999184371835], [-38.814079851180765, -11.682027582617607], [-38.33334753754087, -11.298544383548567], [-38.08247619732464, -10.589337237259093], [-38.33355231002277, -9.914897355236361], [-38.73469956528683, -9.555353225391285], [-39.293345337192, -9.396717377822425], [-39.767886785508225, -9.455044221789404], [-40.22297965487738, -9.685693117568245], [-40.57671302109599, -10.11005526953595], [-40.71101332522501, -10.591569327108921], [-40.58578585016852, -11.063736890616324], [-40.22525982918698, -11.52149649933897], [-39.76925678434029, -11.762758472691388]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[-2.4512150945106437, -9.595697731642437], [-1.4867694015655895, -9.736323927502253], [-1.0623138808752104, -10.126879311108924], [-0.8710048160286357, -10.588168563193285], [-0.9097833003569407, -11.096134993123025], [-1.4795146785345872, -11.832929655838258], [-1.9588543822588096, -12.017630825217259], [-2.4393470693847985, -11.973849834766636], [-3.02142529410722, -11.616025730451074], [-3.3480343451974988, -11.066215954796741], [-3.3719304897529225, -10.5917158723053], [-2.912688702647591, -9.863657596091457]]}, 'holes': []}, {'z0': -49.929251334706876, 'z1': 49.923051099341, 'outer': {'kind': 'polygon', 'points': [[34.892819059664525, 11.616224296095345], [35.37256809299303, 11.54520047436737], [35.854039485247924, 11.686407640211744], [36.21449724717501, 11.920307886243476], [36.53715068142041, 12.385002950828552], [36.57749910532487, 12.863260399975895], [36.34776757755689, 13.358485941681165], [35.84278389049304, 13.79972245987115], [35.37550774386397, 13.947802670706402], [34.87181153179842, 13.86334912538339], [34.274862161647704, 13.341076886695035], [34.08479978444256, 12.867484207442931], [34.12400342958747, 12.386217738602683], [34.413209280361976, 11.898202328955488]]}, 'holes': []}], 'center': [-0.206519195, -0.18293233499999997, 0.19517889000000002], 'construction_scale': 97.04966966184915, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
