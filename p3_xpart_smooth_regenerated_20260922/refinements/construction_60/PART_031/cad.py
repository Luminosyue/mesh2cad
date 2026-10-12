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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.35438244904355676, -0.9351005720294961, 0.0], [0.07126913725745626, 0.02700942781769796, 0.9970913703786319], [-0.932380710806733, -0.3533516817549757, 0.076215478194797]], 'axis_rank': 3, 'features': [{'z0': -23.489846973746328, 'z1': 31.14960202571523, 'outer': {'kind': 'spline', 'points': [[47.13619558798298, 5.412585257932364], [45.50804730694706, 12.977146526567386], [43.14267737624149, 20.336210325403833], [39.29402831374514, 27.048830837290897], [34.472493687612314, 33.096827330835524], [28.76351401866196, 38.320442838989], [22.222946322532916, 42.4384647119421], [15.266760043853893, 45.83448428678231], [7.89169857292766, 48.16696459425526], [0.24234975935104708, 49.32662206199877], [-7.489712816450644, 49.05229609363063], [-15.170987403491159, 48.05833539091884], [-22.488869835403403, 45.586363515114954], [-29.31680831600212, 41.93620813428949], [-35.529874559829516, 37.35111696683123], [-40.041433233881975, 31.09090228570402], [-44.72538193718363, 24.937737513907656], [-48.377877214979605, 18.119504067600097], [-50.431036582992945, 10.686181088831221], [-50.92674921028562, 2.956856222198248], [-51.088434624447984, -4.785161146196712], [-49.77408012942311, -12.401207515831752], [-47.637789203913925, -19.842814160976285], [-44.05785780822511, -26.69169688220628], [-39.38701038130798, -32.85334595166401], [-33.757327552047876, -38.1648524997312], [-27.289435796841662, -42.39847410201783], [-20.234990466104673, -45.591418982745786], [-12.95002652450801, -48.207338052718775], [-5.282186026070434, -49.15917105998293], [2.4441805674971064, -48.72493956898811], [10.043608689468039, -47.36312712775793], [17.26868684211289, -44.58387103676958], [24.01375941939127, -40.789956239480524], [30.104922653826378, -36.02997742688225], [35.500156144193646, -30.480791731418964], [40.21413116087711, -24.34971871832523], [43.50232843021142, -17.348965748406627], [45.73656798530788, -9.937802742816565], [47.10317662077611, -2.317122431844571]]}, 'holes': [{'kind': 'spline', 'points': [[41.92980925105541, -2.0175463158127958], [40.773751695692226, 10.624673802588836], [36.121599407862945, 22.41899076921027], [28.037427485406386, 32.253332065425], [17.403274478077698, 39.234196405816796], [5.397460020696261, 43.450583999886724], [-7.2916984776178015, 44.01161374792995], [-19.63773872282815, 41.17088355824082], [-30.6943612885341, 34.84348045586039], [-27.973626744646932, 24.213249185868335], [-19.927261548214442, 14.353362799735168], [-8.930628102214591, 7.8923767389082915], [0.8025306801301597, -0.29218729118162073], [10.43134663294104, -7.412711182234496], [18.146420799939207, -17.53467722802575], [11.599419720345992, -22.701362042060133], [0.924755364532607, -27.310845954887693], [-10.058175673176336, -32.9544593245572], [-22.779528122531655, -32.43028298008085], [-27.505411877068028, -25.366624622946954], [-15.76280225856062, -20.62657807966219], [-3.442411303615948, -18.597561915544578], [8.18356583494882, -17.449160425781557], [2.2166243647916724, -7.573803553971508], [-7.659567664025545, 0.48130622850112337], [-18.95877400123537, 6.2981113927755965], [-29.10825644228349, 13.941962808867709], [-35.46627836130503, 24.87749940184462], [-43.389147631904876, 16.838163940772397], [-45.66981991325754, 4.371367917335934], [-45.51971801089321, -8.350612061651098], [-41.75894450272896, -20.53007425055163], [-34.19150418561927, -30.772457678798304], [-23.953018196526067, -38.26669202081167], [-12.161915088947936, -43.13224311225857], [0.5039017289498038, -43.788637780078524], [12.85558330968586, -40.8865803865872], [23.857641201398863, -34.51400420544729], [32.77727803473642, -25.430129001924666], [39.0785672026027, -14.44517899739089]]}]}], 'center': [-0.38102157999999997, 0.2737254, -0.51188372], 'construction_scale': 519.8568688480138, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
