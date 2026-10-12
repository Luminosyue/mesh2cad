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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9689138815295393, -0.2473982420700722, 0.0], [0.0023152170110189527, -0.009067347778866685, 0.9999562105284657], [-0.2473874086317934, 0.9688714533027047, 0.009358259750136782]], 'axis_rank': 0, 'features': [{'z0': -6.478240451305766, 'z1': 7.447652590667032, 'outer': {'kind': 'polygon', 'points': [[-49.49337387017319, -13.179494847968426], [-35.65445923478419, -3.2853147900599655], [-31.112860455953523, 0.12803249948663786], [-13.773063655082497, 12.117784780232617], [-1.8005711660563173, 20.908585766027134], [7.5230344694780324, 27.224272787511087], [28.492624074014163, 42.14382010831677], [29.012270145893037, 42.49182140623998], [29.83325119246167, 42.80350273514189], [30.658145165252286, 42.790334215663464], [31.370790360987918, 42.50539796609114], [32.45602935188631, 41.53386595153893], [36.41679772306694, 36.16738664524185], [44.43810265939492, 24.62585020197899], [49.57117438938092, 17.572667544535776], [50.48272228272844, 16.11436833355031], [50.68218526000781, 15.315053243679671], [50.54051342282886, 14.515734912223229], [49.99371470794171, 13.716419822352599], [49.01847490045705, 12.917104732481958], [31.194219327653173, 0.12803249948663784], [22.84407622433594, -5.713119175331446], [9.66734899740666, -14.259669913249956], [6.593622442810242, -16.50316391060569], [1.8966341992829847, -20.284512106720573], [-5.349486645713393, -25.59709795937697], [-12.185811298664651, -30.26481896797773], [-28.93923769803856, -42.057179434651935], [-30.178738509624345, -42.66923637259619], [-30.590744043052457, -42.74998926460379], [-31.49335567644921, -42.60667945057046], [-32.239177828061834, -42.15623859159835], [-32.84015284761547, -41.43644131739607], [-42.52756558476451, -27.84805399453011], [-50.82600369143612, -15.858303334577032], [-50.91051952173007, -15.058986623913496], [-50.32011321911729, -13.937912681442256]]}, 'holes': [{'kind': 'spline', 'points': [[12.726717564258584, 5.978026506344734], [12.610401133284167, 7.354637344770387], [12.191140898139539, 8.668984879289845], [11.558168370075046, 9.897530203562038], [10.768767001846998, 11.031218818966378], [9.700143849794799, 11.893941198976941], [8.39645129286052, 12.339659812794805], [7.019585474374383, 12.410354242708447], [5.69818000046146, 12.016377042598371], [4.457052248707011, 11.404576492962551], [3.2133599041909027, 10.798062051019645], [1.966136092557209, 10.2002864907053], [0.7324825567066702, 9.573802779762861], [-0.4882509423996747, 8.922257243832966], [-1.7008502532912653, 8.255721410933148], [-2.9174232803746754, 7.596915063790188], [-4.122125280117047, 6.916268785339384], [-5.298255094989872, 6.188160328403731], [-6.375796629146419, 5.322109822668064], [-7.337510440497035, 4.331826907234063], [-8.008606741159173, 3.1357581829340924], [-7.879647598844413, 1.811494204498486], [-6.999587713492152, 0.7521870274488559], [-5.948235711742428, -0.14569922712268862], [-4.819145445203848, -0.9454599802576591], [-3.612162472730798, -1.6198245351354181], [-2.328141547795688, -2.1320514494701985], [-0.9878628929998058, -2.473835170727213], [0.3749199483431048, -2.7105747878896227], [1.7544534387976112, -2.6835590006644905], [3.0878517406480954, -2.3195131992076536], [4.4091758469299975, -1.911085723921758], [5.7500511302577015, -1.57136953757506], [7.060182644411162, -1.1277358686608285], [8.306717655277213, -0.530608271930859], [9.462268785707355, 0.22961821661865858], [10.540104835926181, 1.0945335508322012], [11.48412257682522, 2.1033605578401295], [12.206584405867305, 3.279114550138642], [12.587614879948923, 4.604640942521627]]}, {'kind': 'spline', 'points': [[33.214300165655175, 18.432024518104352], [33.139119609715365, 19.468078174091072], [32.890266050772716, 20.47710852061845], [32.505986146168496, 21.44306541767815], [32.017735631496635, 22.36043055335578], [31.407225682799968, 23.20176921574921], [30.66924433915287, 23.935371396653423], [29.801697701179357, 24.507307066893055], [28.856400588294097, 24.940137062038513], [27.849834976312696, 25.202799965884623], [26.821548953140297, 25.359149555727768], [25.784384136823814, 25.322536314381683], [24.763753654395412, 25.124120469101868], [23.797531382010813, 24.742193254422467], [22.898412906577086, 24.219422183993544], [22.081319647063307, 23.576900952747042], [21.3700976995938, 22.820539421652434], [20.807597850827687, 21.947744077143913], [20.41270844964609, 20.987206933406057], [20.173103985587815, 19.975135247865822], [20.037807493177894, 18.943790579302757], [20.055010630004777, 17.907407470898523], [20.314118916187173, 16.90270817874178], [20.73190800017722, 15.950095665709968], [21.26793250022633, 15.058271151420836], [21.89343853333533, 14.229035001364888], [22.62522804165352, 13.492601773937299], [23.482432064602694, 12.905138896703717], [24.427580661704763, 12.473875672164214], [25.42540466276879, 12.181892616649627], [26.460156394312122, 12.089355183075938], [27.497007799941375, 12.178183117509763], [28.521731851897595, 12.357078625421122], [29.516760356152542, 12.658856379582794], [30.447040344965256, 13.121049298207348], [31.283974124891603, 13.737191528898357], [31.96713765060344, 14.52112476277649], [32.49498229285746, 15.41741820192236], [32.87185202273408, 16.386665937627978], [33.10988987022076, 17.398209110270436]]}, {'kind': 'spline', 'points': [[-20.513275821723955, -19.248852996662844], [-20.527839535350324, -18.235832028484417], [-20.70210383099438, -17.23650512552889], [-21.012212602267834, -16.271859391090068], [-21.438121025105758, -15.351914883009279], [-22.045570086277976, -14.542600400820008], [-22.77275634215986, -13.839200143438383], [-23.59242891728862, -13.24302621156123], [-24.475662664656518, -12.743926699276981], [-25.428291583794362, -12.396580170112808], [-26.425538123005964, -12.217906759191761], [-27.440487740455524, -12.215650589788096], [-28.446529417002086, -12.335363735461893], [-29.41510916383958, -12.63390715675407], [-30.33079349201038, -13.068979138424579], [-31.1791550277023, -13.623220080101966], [-31.894852394383772, -14.339476574100663], [-32.446531396763206, -15.190500174672657], [-32.86739839162062, -16.11310184834554], [-33.155142879673264, -17.084641080392466], [-33.27208076276302, -18.09019639441901], [-33.1673371660516, -19.096425137045557], [-33.013030191556126, -20.099658131382505], [-32.79750806101619, -21.091267318736406], [-32.44257696789081, -22.038630032858112], [-31.907254214809047, -22.897730601365854], [-31.220357274633592, -23.64005657632139], [-30.402643522013577, -24.238549334782324], [-29.507876747083678, -24.71230682470195], [-28.534552796865405, -24.996584997096498], [-27.53313646733957, -25.15642792749044], [-26.521360962822953, -25.121074599474678], [-25.53782471942215, -24.875365243760694], [-24.574647347780804, -24.554700975874983], [-23.64450579557159, -24.151824675697142], [-22.78901678672346, -23.610580360608488], [-22.038680128844604, -22.932655447931623], [-21.417628196179432, -22.132002297480472], [-20.98747764978184, -21.21340999212732], [-20.675289338367378, -20.24930134289387]]}]}], 'center': [0.12916369500000002, 0.75989928, 0.206310975], 'construction_scale': 162.07219282169618, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
