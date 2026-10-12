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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9953356462184575, 0.0, 0.09647254203598853], [-0.000890610257738422, 0.9999573865006645, -0.009188688488007002], [-0.09646843100338258, -0.009231748629637902, -0.9952932314835587]], 'axis_rank': 0, 'features': [{'z0': -54.309373907714495, 'z1': 51.041284279067796, 'outer': {'kind': 'polygon', 'points': [[-41.71966443504675, -10.368776291438879], [3.484691949979184, -10.513141723145432], [41.73887518118203, -10.379513782625308], [42.250059789837096, -10.031596656406089], [44.579178176103056, -7.638864883357488], [46.614067901525175, -7.523344925037044], [47.00534773153619, -7.420726892168617], [47.2215511676096, -7.176672174892522], [47.33988292922936, -3.1492664877921372], [47.178677191816476, -0.40701909340019765], [47.352474816402726, 0.33434101305422465], [47.22676227719176, 2.661696695672922], [47.29177489162209, 6.194724365369218], [47.18365237881342, 12.035741143737008], [46.88177089537529, 12.280444554791274], [46.45734491530588, 12.32949094966792], [-37.01936336172674, 12.366361441659043], [-46.369945276030215, 12.342862709693776], [-46.659949253203585, 12.277680390986998], [-46.93822816218234, 12.016588805371018], [-46.87475847285926, 8.916542630990142], [-46.75140398826822, 8.306385792540972], [-46.950050034809614, 8.180921700229394], [-47.12997950990089, 7.710879218373269], [-47.12026145472029, 6.306207842595649], [-46.951921422487914, 5.738617528212061], [-46.36916319154143, 5.605753845578587], [-46.02782211568565, 5.694636395557963], [-45.86904901687435, 6.018464512872645], [-45.97537751844337, 7.704112521404532], [-46.12890716212706, 8.287442295902649], [-45.86174219639849, 8.875313739873103], [-45.93666484231051, 10.58948343803946], [-46.095644555226514, 11.169576441020949], [-45.78828107344689, 11.377061811009815], [36.81736729526683, 11.332429581549913], [46.01750993582241, 11.299233900921964], [46.251347526422634, 11.16239990184945], [46.387228204211134, -6.267524123487866], [46.292688068991424, -6.533033777545925], [46.02305894229163, -6.6399759903641895], [44.67318737908993, -6.644539937010778], [44.032403679122744, -6.835454965430253], [41.737166698449045, -9.174532709972542], [41.44719823413984, -9.4005253554505], [41.067867310745356, -9.476918399980404], [-41.192951742297055, -9.44684836770065], [-41.4826818248047, -9.39493995775622], [-41.77787275418031, -9.144947184401865], [-43.88406487422008, -6.860170933503281], [-44.366736797581666, -6.698599551221825], [-45.8606687372714, -6.573766550837728], [-46.07325767994097, -6.244254238751983], [-46.063755447949816, -0.534921798364764], [-46.36611130333556, -0.3507238804018123], [-46.655893777354294, -0.4175183960270863], [-46.9508984003605, -0.8292703511793063], [-47.00917753158778, -5.881900296929868], [-46.89964335404855, -7.114118459579976], [-46.64611739673452, -7.4016308959134625], [-46.335622071318475, -7.501851736045145], [-44.61762939664055, -7.654968134782399], [-42.34300303630976, -10.030858103077275]]}, 'holes': []}, {'z0': -54.309373907714495, 'z1': 51.041284279067796, 'outer': {'kind': 'polygon', 'points': [[-45.95455690867033, 2.3133953172868496], [-46.143842343603666, 2.5879304698782595], [-45.884224524241944, 3.1968982108348216], [-45.92754137382496, 4.847974908733084], [-46.08671204043813, 5.110550216270287], [-46.37254370416942, 5.184016101235854], [-46.80457671551293, 4.8724233587660555], [-46.9227850311229, 4.107065114973535], [-46.92102685599706, 3.19885956486472], [-46.81389706595018, 2.884768955272971], [-46.49681684702989, 2.5927157614073186], [-46.737991527142626, 2.429342371998407], [-46.93056896651717, 2.0172412769265238], [-47.049429460282745, 0.593957356043872], [-46.97581984851363, 0.23918117489418098], [-46.65582272884257, 0.028182018644824343], [-46.37162972331786, -0.0031620330352382583], [-45.8650726662783, 0.31602201207660163]]}, 'holes': []}], 'center': [-0.0006723000000000146, -0.02530178999999999, -0.13716694000000001], 'construction_scale': 57.91682918611576, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
