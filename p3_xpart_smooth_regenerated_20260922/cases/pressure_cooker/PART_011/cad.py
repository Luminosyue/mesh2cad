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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.9999939163430335, 0.0, -0.003488162399075729], [8.067509550206068e-06, 0.9999973254164514, 0.0023128110297797647], [0.003488153069693961, -0.002312825100214298, 0.9999912417757559]], 'axis_xy': [-0.3119537010847715, 0.49464997745836553], 'profile': [[1.447448840357891, -13.687207832854941], [2.894260382933891, -13.683195625742496], [4.3413339924712275, -13.666732662788966], [5.788412187839948, -13.649906631772076], [7.235455363470578, -13.634615315320756], [8.682410011491536, -13.611961868724613], [10.129239499620518, -13.576595136154268], [11.575869003972159, -13.541242184455442], [13.02219359358552, -13.50811512342138], [14.468165900463504, -13.469962406232721], [15.913877549088962, -13.419731768908772], [17.359335896895058, -13.367561646036553], [18.804653054795267, -13.317308412892817], [20.250039978574687, -13.26141412638933], [21.695633182227112, -13.196642429056016], [23.14153345618874, -13.126199768603833], [24.587535918671932, -13.050103726755632], [26.03339478582702, -12.972634488814453], [27.479046026815315, -12.895712130362575], [28.924138697194163, -12.819389095767956], [30.368958456403842, -12.753654655858515], [31.813669635608264, -12.677755910595103], [33.25823785233331, -12.60947273919232], [34.70293488768437, -12.53288584018411], [36.147714502166856, -12.443998442673667], [37.59227666613684, -12.33115302685588], [39.036435327871374, -12.215634891701482], [40.480319109868105, -12.084129264710612], [41.92403680266392, -11.954444110513789], [43.367759484516526, -11.804030237633832], [44.80834006707239, -11.621209489138575], [46.228712401805055, -11.372988423387469], [47.49621598724694, -10.855857620590669], [48.078386892185755, -9.719615191063586], [48.18898625024681, -8.272516746093556], [48.216559718034475, -6.794225448823962], [48.218256302685404, -5.335116120348395], [48.21956348495766, -3.886467936128143], [48.223781472790726, -2.448475853166708], [48.22890573944191, -1.011647245845164], [48.23355699957084, 0.4346432983099717], [48.235317529457426, 1.8817228955115737], [48.238396435131065, 3.3288716180178257], [48.23362381750212, 4.776199333770963], [48.20720093017983, 6.223059253639017], [48.07168818133593, 7.637051502183745], [47.33529319582709, 8.750200729821582], [46.03565791490297, 9.274459495460038], [44.61773027941182, 9.554659482645832], [43.19528627453666, 9.721134921706573], [41.76482028625387, 9.879896930516367], [40.32926814366466, 10.034648939694858], [38.89223672966344, 10.167328000560616], [37.45959556146717, 10.316382940719821], [36.025422100531344, 10.489516468096829], [34.59093287906335, 10.697235955875986], [33.15506801580591, 10.897816134706208], [31.71274569649224, 11.055254405409919], [30.268960859943505, 11.196875495730195], [28.825352829971493, 11.33200909078134], [27.38203060111897, 11.459083432143611], [25.9392742939352, 11.58908956013127], [24.4970468582393, 11.745883082959116], [23.055339565569426, 11.904988508109554], [21.614400081395445, 12.077345304363408], [20.177589558688503, 12.257578180589082], [18.743014879308774, 12.430107386961005], [17.307783158741685, 12.584950899899464], [15.871930286583876, 12.735059520302018], [14.434141130467827, 12.861580853729546], [12.994722827903749, 12.970050930009814], [11.55490104770749, 13.102936114591813], [10.113564961483188, 13.245570162424546], [8.67221508173775, 13.374306833398817], [7.229787230620593, 13.470437247003288], [5.785413880332747, 13.547475030574152], [4.340118346946284, 13.602662400692925], [2.893563743961497, 13.652178439358313], [1.447015699095763, 13.672843044998228]], 'breaks': [0, 9, 19, 29, 39, 48, 58, 68, 78], 'center': [0.019098820000000016, -0.03239933500000003, 0.474687105], 'construction_scale': 63.20745616896334, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
