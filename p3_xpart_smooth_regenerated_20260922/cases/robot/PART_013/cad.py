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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -0.1227245905911893, 0.9924407664259993], [0.9992449292098596, -0.03855950339388382, -0.004768243534025382], [0.03885320383678433, 0.9916914033923266, 0.12263192483760198]], 'axis_xy': [-0.4715879110872224, -0.18501093492083728], 'profile': [[0.8470977827497924, -23.60085867756051], [2.484682372500278, -23.606604044669048], [4.141132953324794, -23.61664940953402], [5.797619050485428, -23.623923559089842], [7.453942953169975, -23.627208016666955], [9.110388877192449, -23.628872643795514], [10.766883603600629, -23.644225452014517], [12.423380315138527, -23.678736212759226], [14.07989402997617, -23.690836356442972], [15.736209158819182, -23.709073613658823], [17.39245778346526, -23.729916578912725], [19.04871576897642, -23.75792352191639], [20.704968133589787, -23.766749944380265], [22.361001473689356, -23.75125830577676], [24.01677153356426, -23.731320289177], [25.672072653267335, -23.694855124383164], [27.32716222279057, -23.623805561785446], [28.98083305328061, -23.52727211809784], [30.63120027105265, -23.39225023772974], [32.27829767239682, -23.202416674857012], [33.9150838220003, -22.91492654400343], [35.52341159639925, -22.53103943889787], [37.09090101225197, -22.01078493332445], [38.590049246036244, -21.338074412883305], [40.02654402089529, -20.55166289062964], [41.38387949902486, -19.6149910854518], [42.65369715674453, -18.578585827579893], [43.846113116727864, -17.44819964744149], [44.95354270825418, -16.190202067473127], [45.936216080341595, -14.833310713332022], [46.77001341908859, -13.385365583160398], [47.47874867808668, -11.869056788881704], [48.067291672203076, -10.323673734057607], [48.53005950976736, -8.760626209522997], [48.89789616256681, -7.160100998253499], [49.16016229844878, -5.531115791768389], [49.29842382244868, -3.8818040735501387], [49.368118147333206, -2.228222012124804], [49.38795217234728, -0.5732664024523607], [49.387305868648234, 1.0817662048248513], [49.38539720119579, 2.7361765234494237], [49.38287559773745, 4.3905183544671225], [49.36887601277867, 6.045517641166403], [49.36038709176025, 7.700771311428136], [49.38446586915437, 9.355912468048007], [49.378009019931724, 11.010276862481675], [49.3558568481031, 12.66375692542556], [49.27400393399714, 14.312919511143392], [49.0235576965699, 15.949659012363385], [48.55068472811534, 17.539883992791292], [47.78303235032793, 19.005664806887076], [46.70807482150009, 20.2436353889644], [45.35411217671461, 21.14294863469292], [43.80440359932997, 21.65575827593692], [42.17420838527704, 21.827633535457487], [40.52206835748075, 21.822471597350727], [38.86724807725699, 21.79218533209619], [37.213827435283065, 21.72467737148048], [35.559110767197225, 21.651621729325555], [33.90300212686853, 21.621507841292324], [32.24799432127775, 21.567912634380484], [30.59420592863578, 21.535261840650875], [28.938922830211403, 21.473598693205044], [27.283318962360525, 21.45303008969854], [25.631215036843358, 21.439034719946186], [23.98327805688283, 21.37080838430618], [22.338606257842102, 21.304054835764276], [20.688657428249936, 21.310813558820783], [19.036593375767175, 21.31963064666025], [17.383206289564548, 21.312015751971423], [15.72775048955223, 21.294206536891902], [14.072809307189114, 21.252766002989052], [12.417343085786577, 21.20845420205238], [10.761765436838708, 21.156091810433473], [9.106454483528314, 21.083282351927096], [7.451089706580838, 21.01437757886533], [5.795767237240942, 20.981416261909324], [4.139813551384664, 20.970779249661696], [2.4835387533108806, 20.960271063451607], [0.8467559137417202, 20.92956104907389]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.017810640000000003, -0.374699755, -0.3240245], 'construction_scale': 388.2607649373816, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
