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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.02219880182967958, -0.9997535762363278, 0.0], [-0.013974003621713717, -0.0003102825981712909, 0.9999023107021455], [-0.9996559110114376, -0.022196633244315624, -0.013977447997055685]], 'axis_xy': [-0.038965229386467716, 0.010863352027707402], 'profile': [[0.8370968665790038, -17.11600943908166], [2.4545107707512117, -17.13193932120041], [4.089648625194015, -17.169666019328055], [5.723362908809857, -17.23958727903147], [7.34003089259814, -17.442498368948716], [8.885274279993043, -17.981972941468825], [10.327045121996107, -18.746927754481924], [11.819682440771988, -19.212150648384096], [13.434247326064373, -19.26861548057565], [15.070691927168543, -19.265490229475798], [16.71089963261003, -19.290582410330188], [18.35153448077525, -19.333681563532508], [19.990877672796607, -19.350712371932175], [21.626945064584646, -19.354905434587124], [23.262367551441127, -19.343535258231], [24.896580661448276, -19.315091928531782], [26.531968761758876, -19.29266349210853], [28.16821936479178, -19.28017675351432], [29.804805435724347, -19.262768193588762], [31.441906545303336, -19.250438855821812], [33.07930326294033, -19.243580100429227], [34.71831995876255, -19.235776517114783], [36.36176600109289, -19.23790208342933], [38.00586426528383, -19.239285340816274], [39.649938571199534, -19.210021573593806], [41.28944690278264, -19.122627058627547], [42.89313594706961, -18.908694260346735], [44.450733980965694, -18.50510469811695], [45.90706300290401, -17.76184063880268], [47.15927850851536, -16.74920246852102], [48.17544686046253, -15.474895171563809], [48.95173100231341, -14.019462390692793], [49.48138710113416, -12.466112863903586], [49.79024044490804, -10.860103079652415], [49.896549512523315, -9.235624937734196], [49.86150958268246, -7.598974587832407], [49.87021345990573, -5.961914647518419], [49.87815633348911, -4.324553311441728], [49.87448875343794, -2.687126571541143], [49.849976862061354, -1.0497313001937991], [49.84932155462885, 0.5873212455045856], [49.846337124973104, 2.224318634445238], [49.832040829815554, 3.861501810093998], [49.86309781765922, 5.498335141933998], [49.88735618695965, 7.134872010803782], [49.850907708307716, 8.771213422164529], [49.76019832423567, 10.405560249067662], [49.554398278826284, 12.021745192537757], [49.140275494912046, 13.578470584253477], [48.4631410249941, 15.057378860970406], [47.503176436585306, 16.38238256794773], [46.28564403865478, 17.474599605975232], [44.89126442075645, 18.287670148727305], [43.3715537449002, 18.884977426637583], [41.768317552776054, 19.250945494694417], [40.13662280298294, 19.367589653747395], [38.49895316648683, 19.366463056872117], [36.86091085304191, 19.354429187820674], [35.22288212924597, 19.34937518893531], [33.58467002638912, 19.34855899345933], [31.946363120725906, 19.34653620630788], [30.308051581338983, 19.338743734011878], [28.66981545812513, 19.3294860206896], [27.03157069489003, 19.328530391498195], [25.393318870398694, 19.331576761151293], [23.755049447900475, 19.336027629795353], [22.11679750618299, 19.339332257778594], [20.478520527290577, 19.34221197450107], [18.84023595710174, 19.334607049385134], [17.201969705328292, 19.329832364168645], [15.563677709976627, 19.330016581489453], [13.925385118771425, 19.32374400920319], [12.28709460398927, 19.314598053209508], [10.64881004159326, 19.309335623576317], [9.010525724133668, 19.30166041098384], [7.372264188060913, 19.300226812652582], [5.7339604271123275, 19.291877868657437], [4.095674678025645, 19.284697993451623], [2.4574705105744625, 19.284313047712367], [0.837827530985213, 19.288668507553815]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.42143035, 0.430363005, -0.50196222], 'construction_scale': 149.40260546490526, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
