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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.24592551330861753, -0.9692887298962538, 0.0], [0.0015876158043676768, 0.00040280591281380545, 0.9999986586108274], [-0.9692874297028465, -0.24592518342679673, 0.0016379183574512463]], 'axis_rank': 0, 'features': [{'z0': -7.046151603013335, 'z1': 7.182052698409455, 'outer': {'kind': 'polygon', 'points': [[-11.599359306488871, 11.04573850444081], [-0.8674928315515615, 15.964321523457388], [11.52640514162117, 21.977205871220967], [33.85934665051112, 32.33654997520017], [34.6485690889098, 32.66300299549288], [35.437722522581176, 32.792604737163], [36.226740496442844, 32.627046182925135], [36.74908913024179, 32.26644052233521], [37.27131700940201, 31.69692681214741], [37.681272064510075, 30.93206046109523], [41.74555454202375, 22.09297418962876], [49.60220175276036, 5.6917283293242455], [50.2722941272134, 4.162008034591024], [50.38428137352234, 3.39714633630302], [49.862816768138266, 2.387155599804064], [48.83933138206487, 1.6354949417126061], [34.63287312622341, -5.10684906679749], [23.583478433118774, -10.190591698382425], [7.14988712054909, -18.24475467750933], [-10.354097844026409, -26.153670106395516], [-16.66795544505727, -28.868508383026775], [-19.89291261820707, -30.08317840725545], [-24.560004174732963, -31.579444426657837], [-29.29496927387312, -32.583489109187276], [-31.66230454591816, -32.73303652144011], [-33.240470003642365, -32.678912145469994], [-34.818515689674285, -32.355827579284274], [-36.39644392740862, -31.746271968724137], [-37.185351489153646, -31.299622958908223], [-38.49037240240252, -30.2566350091296], [-39.55170895669407, -29.096238459763168], [-40.70749167667049, -27.50245641143547], [-41.80008792811276, -25.66748187953686], [-49.80217961063755, -10.508160036799936], [-50.363756720107226, -8.840589655899167], [-50.169296076733715, -8.075729508532552], [-49.60089027040979, -7.412825968634381], [-47.60980495002363, -6.263782893791061], [-36.15212189153354, -0.42714354408032157], [-22.44557015735804, 5.8656954781590125]]}, 'holes': [{'kind': 'spline', 'points': [[6.254428057665906, -2.4026552737020106], [6.115969602530973, -1.4119643908850403], [5.862602430627295, -0.44356659498511375], [5.446087140419452, 0.4659924237540768], [4.885537087633998, 1.295496209656604], [4.228787210816512, 2.049706342613808], [3.4720628325299603, 2.7017612768524497], [2.597620487882507, 3.1855630784975744], [1.6673544907791096, 3.5498487332768036], [0.6971221302641707, 3.7967756670090784], [-0.2986941935985606, 3.8953460825790702], [-1.2945032172854878, 3.8313172613701743], [-2.2666938863252266, 3.5966739780673618], [-3.191120733098482, 3.2153121015722435], [-4.0293793344677225, 2.6692749848032755], [-4.790868954128095, 2.018748354266363], [-5.410379331207945, 1.2339443335400706], [-5.882662214139012, 0.3531270536518308], [-6.197559207250261, -0.596546450963793], [-6.378884869340994, -1.5803708000142491], [-6.411448772043154, -2.5808188323810373], [-6.292181101865811, -3.573272000140211], [-6.028630199124494, -4.538766187060896], [-5.653048613530367, -5.466489553823236], [-5.12690959065174, -6.315483518804298], [-4.49531129331358, -7.091048156005435], [-3.739151635346568, -7.740701731629104], [-2.877585965940732, -8.246812483527334], [-1.9430095593512888, -8.602065252424351], [-0.9609498426898552, -8.782876053465227], [0.039333792220606956, -8.786618434534017], [1.0353595822900552, -8.681726136974273], [2.0196519942829854, -8.501304385671792], [2.9722614925781867, -8.196777299682559], [3.8267366747629312, -7.68059572887206], [4.5381249216335195, -6.978134691331088], [5.126739024521249, -6.169758708389812], [5.623416488752505, -5.300961298265038], [6.010186810078955, -4.37814361996981], [6.21904122064385, -3.4007624611238287]]}]}], 'center': [-0.021546205, -0.676058475, 0.44660107000000004], 'construction_scale': 155.09193097472317, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
