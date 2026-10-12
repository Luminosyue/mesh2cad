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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.9995326816359766, -0.0, 0.030568257091193516], [-7.102184727231932e-05, 0.9999973009361156, 0.002322299804240177], [-0.030568174585514796, -0.0023233855649813996, 0.9995299838334145]], 'axis_xy': [0.03763161345824347, 0.05811622378871335], 'profile': [[0.9801536542797715, -49.867735042344506], [2.8749595383620306, -49.864585217703215], [4.791556045320826, -49.85987743722826], [6.708167367174199, -49.86313129164226], [8.62485850132007, -49.85955149563244], [10.541491126635506, -49.86564779276204], [12.458083960949855, -49.86536957546488], [14.374639924748898, -49.86867866351989], [16.291155721059887, -49.86384705970299], [18.20772350832648, -49.85848585996098], [20.124303416986933, -49.85233141491708], [22.040945757787107, -49.848254785653495], [23.95586042041435, -49.82173029184826], [25.80188860292263, -49.47043069256777], [27.18997193527566, -48.18523812603755], [27.68825719926365, -46.40427947719542], [27.736484257261274, -44.49859595447951], [27.727145452649182, -42.582806830148634], [27.728862407483042, -40.666692669730566], [27.731413462562003, -38.75068821992582], [27.738912871825185, -36.83446799409943], [27.745403577106437, -34.918017630307745], [27.743873273462544, -33.001858630048574], [27.74370442265802, -31.085625165882117], [27.741159358193272, -29.169280824877685], [27.74411846667716, -27.252679386166527], [27.736648956563478, -25.335152264326922], [27.73992345538596, -23.417639361116866], [27.744233313442138, -21.500240873012217], [27.745781171801365, -19.58280515885742], [27.747882114825508, -17.665568008608716], [27.753295403931453, -15.748224262511066], [27.766395759203014, -13.830943503357176], [27.775261914928457, -11.91340792475328], [27.77804808085424, -9.995981802852146], [27.78188439206759, -8.078831814865584], [27.77750506808031, -6.16167317350065], [27.775727540984935, -4.244084240295696], [27.770445757800804, -2.3264368472571952], [27.75389981723071, -0.4088501881870142], [27.748835285657933, 1.5085210657861854], [27.741728247735335, 3.425988434642056], [27.75106440837415, 5.34363572843877], [27.762735435570576, 7.261223407287657], [27.759474682558547, 9.178446609159145], [27.767035234943243, 11.095898949105838], [27.773916519504212, 13.013442454549553], [27.77556700783075, 14.930858184333662], [27.777355877629674, 16.84785701706074], [27.779256130336577, 18.762039191545156], [27.789922442444244, 20.675685160537544], [27.790084691466152, 22.58926794930983], [27.791559823577426, 24.50268548487806], [27.797091703281662, 26.416075153948867], [27.80668941505047, 28.329375881071094], [27.811371776482716, 30.242909554122043], [27.825127291872803, 32.157965356449495], [27.835429676305772, 34.07448838752882], [27.84127023346774, 35.991114455168955], [27.847012386179184, 37.90771934555188], [27.854342121102526, 39.824312397296815], [27.863376565578967, 41.740883899156145], [27.866305551356064, 43.657169527014524], [27.87842158956088, 45.5735700774858], [27.86892608473572, 47.48035794399877], [27.43794253514708, 49.15347696045149], [25.85972583766452, 49.84522670907401], [23.955823627456237, 49.87632159836343], [22.039917307281918, 49.86321344733342], [20.123813920773607, 49.85153653489817], [18.20740059770433, 49.844186043157265], [16.291047899453506, 49.835809141349046], [14.374555086927465, 49.83695195008852], [12.458121216631197, 49.83513477876801], [10.541482483947489, 49.8347173422777], [8.624818244367614, 49.831138575369536], [6.708170587427036, 49.832279986453955], [4.7915760197284545, 49.831160088937516], [2.874917185803736, 49.83544969891242], [0.9801693721417826, 49.8335837889517]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.672527815, 0.77077657, -0.57699939], 'construction_scale': 198.41565890030742, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
