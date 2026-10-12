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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.001882340141098438, 0.0, 0.9999982283962273], [-0.0004922102203209351, 0.9999998788641129, -9.265086969753052e-07], [-0.9999981072605548, -0.0004922110923239632, -0.001882339913079495]], 'axis_rank': 0, 'features': [{'z0': -50.009232936182926, 'z1': 49.99057778987256, 'outer': {'kind': 'polygon', 'points': [[-4.113004100657227, -1.263492839799416], [4.203739726858422, -1.302713519142773], [5.2017490085076385, -1.1959319986363262], [5.719649263796465, -1.000961644441327], [6.106871418528085, -0.6682917913694634], [6.257051182941866, -0.3356232874195085], [6.285439276451983, 0.32971574416326466], [6.169268930171035, 0.6623849226741741], [5.8670904781211854, 0.9783234939597374], [4.86908156929063, 1.2739321507177468], [-2.449653073261446, 1.3155797196552295], [-5.111011036820128, 1.1612530466739284], [-5.776350717592039, 0.9177279123795673], [-6.254703045595138, 0.3297157441632647], [-6.229202634467396, -0.33562328741950853], [-6.041701102023299, -0.6682917913694634], [-5.111013150572608, -1.1201596832803526]]}, 'holes': []}], 'center': [-0.11920548999999997, -0.029546125, -0.220130835], 'construction_scale': 67.45608726767027, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
