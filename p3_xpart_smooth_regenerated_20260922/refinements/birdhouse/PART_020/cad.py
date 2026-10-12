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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.07687018252904411, -0.9970411100039713], [0.9982301285739348, 0.05929344388790547, 0.004571424195759364], [0.05946940732230118, -0.9952764754327631, -0.07673413218946955]], 'axis_rank': 0, 'features': [{'z0': -52.00577722178166, 'z1': 54.37273733042591, 'outer': {'kind': 'polygon', 'points': [[32.9059028955479, 36.56025868759253], [32.58210462608203, -36.514532427061766], [32.56267561947317, -37.017948722424975], [32.24691980787774, -37.3285104359659], [2.0485467507384763, -37.28787514099995], [-4.9513706597260345, -37.16638287799813], [-6.27965004136961, -37.039043489957244], [-12.7981992360137, -37.30257041316289], [-32.321911124117776, -37.32271937910228], [-32.826892165090925, -37.27891296952956], [-33.06335413845853, -37.01634099125945], [-32.752568409156765, 31.919942352282664], [-32.73831178210931, 32.52020721526689], [-32.506548222301895, 32.77400613873075], [-25.946972461293978, 32.8364066342998], [-25.55285055478042, 32.51879074368331], [-25.73215425784941, -29.890278845294553], [-25.221601361030352, -30.00195483746198], [-17.484922782859616, -30.043702984548272], [-12.736398572337743, -30.46871441207101], [-11.484404232280351, -32.74830120921829], [-10.448494654661062, -33.9592912419018], [-9.264504111887183, -34.73427634729924], [-8.046389465964227, -35.09859290262614], [-7.964397054014892, -35.21415682242298], [-7.7175372191876175, -34.97847620895236], [-6.291388083207931, -34.979518261409304], [-5.797091442968755, -34.47911314984705], [-5.57843581423922, -34.456259138197424], [-5.201344090266859, -34.00390886669143], [-4.342935639685123, -33.6182635051997], [-2.437681689828188, -33.20568234024129], [-1.357085135762834, -32.65634109746622], [-0.8185585172048141, -32.68632788722623], [-0.16578219427226035, -32.54484132236044], [0.008884549740779069, -32.27085691526677], [1.049079915788366, -31.406772279926976], [1.3631154883008918, -30.459896420374015], [8.304568583583105, -30.03379877971098], [28.390528801566788, -29.96310554492731], [28.68817284391505, -29.45635903869558], [28.971476826631474, 32.02529771111712], [28.724383475130683, 33.02374999288499], [28.909981812435824, 33.51881215675451], [28.966544089066982, 36.02879076932119], [28.646108405062428, 37.067609468104905], [29.61459860265324, 37.19586658893893], [32.59067688199918, 37.20867116357977], [32.79389436270736, 37.05410879956415]]}, 'holes': [{'kind': 'polygon', 'points': [[-7.472766735998864, -35.762998105225186], [-6.303839789302749, -35.82651703734056], [-6.163349186345951, -36.0185918372366], [-6.307025593162189, -36.378922939557974], [-6.942110515745789, -36.46002243862495], [-7.884055339221249, -35.656311514835046], [-7.639746792800342, -35.574805752487116]]}]}, {'z0': -52.00577722178166, 'z1': 54.37273733042591, 'outer': {'kind': 'polygon', 'points': [[-17.870154493701815, 36.290920389540446], [-16.859564481944684, 36.40001554488171], [-16.56827102535262, 36.057691010688686], [-16.42620452183191, 35.54255484505163], [-16.61837101748565, 35.03809426726872], [-16.859155631223548, 34.819086133990055], [-17.86670731911077, 34.66843761578977], [-18.681020034056438, 34.0410652396298], [-18.48621267499765, 33.52360578827018], [-18.608986749965, 33.0170695098355], [-17.841588847139427, 32.71765832573089], [-14.83802304120276, 32.5593189222528], [-2.305839400639484, 32.57751433907675], [-0.21353979826227892, 32.7962257602836], [0.8545171040863264, 32.773125373593274], [1.8427997518346027, 33.012324243575456], [0.645630992520875, 33.24891758787654], [-0.29018779252863147, 33.22911914805181], [-1.2989093349076526, 33.5128742731521], [-1.354250806531259, 34.025104477533716], [-2.3505041870571204, 34.681354526076625], [-3.7408828969811507, 35.1552347950976], [-4.506630405837539, 35.19156668440179], [-5.2134906290965395, 35.54592996498805], [-5.140054835996707, 36.04404270109478], [-4.7091630095130235, 36.272235337513386], [-4.238152033915115, 36.36171174593565], [-3.733933221207293, 36.27614661567173], [-1.2048764013132622, 36.89452883679847], [0.3698602291694502, 37.057076193323795], [-19.245569537375328, 37.059935866533415], [-18.86565488968948, 36.9765372405038]]}, 'holes': []}], 'center': [-0.0658435, -0.002954414999999988, 0.004434209999999994], 'construction_scale': 50.997733686213856, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
