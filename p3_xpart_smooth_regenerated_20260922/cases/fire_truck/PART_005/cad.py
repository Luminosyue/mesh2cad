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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.049309209267373956, -0.0, 0.9987835610788888], [0.0024567453979072373, 0.9999969748410946, -0.00012128771203563855], [-0.9987805395999044, 0.0024597375183602883, 0.04930906009918042]], 'axis_xy': [0.3494983959980159, 0.10620671600897473], 'profile': [[0.8724586785294858, -25.66594264387379], [2.5590410749351253, -25.67019421075634], [4.264970383175839, -25.677525309382837], [5.970854302794921, -25.678538237780405], [7.676651226054966, -25.68634824559526], [9.382552504119076, -25.697403396552666], [11.088534650369576, -25.723520116450903], [12.794481781885981, -25.73711588297534], [14.500437269233819, -25.74260321527973], [16.206387623175218, -25.74359752264538], [17.912392158549473, -25.77555073004734], [19.61835207225093, -25.827045831082742], [21.32427868062379, -25.84799189532322], [23.030198163585442, -25.853411513052805], [24.736088862770224, -25.85125524175098], [26.4419255105628, -25.83917660710353], [28.14782647832464, -25.82489239286597], [29.853707094118995, -25.824734091950052], [31.55958114958078, -25.838293738859644], [33.26532757399993, -25.86152387405332], [34.9712271630869, -25.881659268118376], [36.67726966297592, -25.901325269215672], [38.38341741481748, -25.923090040545514], [40.08914155294098, -25.92576607159608], [41.787772556891184, -25.80184382757867], [43.43479651812131, -25.438832397370035], [44.96230575706346, -24.749740082716855], [46.30371630310151, -23.765897168483985], [47.460530842098024, -22.508866414724274], [48.36417597449223, -21.089432910239587], [48.96948199934856, -19.578466673183552], [49.385129101346756, -18.004799499770836], [49.61117068807982, -16.350640415744746], [49.691573813533765, -14.668330045525323], [49.7122738891794, -12.979449669794331], [49.69475446906041, -11.290078578293482], [49.6820676054924, -9.59784432843795], [49.673588230407375, -7.890842452554011], [49.680614274406004, -6.177149991817711], [49.731324850218556, -4.463728577475282], [49.784699948816694, -2.750837116722508], [49.79569615184437, -1.0372501110872807], [49.801338276274734, 0.6765517243167111], [49.803604469419724, 2.3890660120687057], [49.70240456764703, 4.091465331841848], [49.36651354771864, 5.762834721043073], [48.78768055710863, 7.382136928836129], [47.93531637486238, 8.84166417679499], [46.825364772391914, 10.042375355216087], [45.465244181982634, 11.042126554756813], [43.90276205991603, 11.850725412835097], [42.22736907856739, 12.287964806137762], [40.521763729821984, 12.412132631619597], [38.81467092488483, 12.439354661390851], [37.11757473444116, 12.44276278850797], [35.41798018425582, 12.430807766465625], [33.71661285275528, 12.444856155541261], [32.01420108281613, 12.481446696644605], [30.30490664551464, 12.48130960409395], [28.592442289828384, 12.476932534506481], [26.879825364541425, 12.495227061795712], [25.167417727496662, 12.486743081297597], [23.455034499204807, 12.46713967647737], [21.742050139753374, 12.50354401406386], [20.028994610391855, 12.63365902072077], [18.317174336046268, 12.732571186214457], [16.65842747142976, 12.993749642376699], [15.261168595841813, 13.678851286066562], [14.211722047602414, 14.9857894627798], [13.42188175554525, 16.479066758555373], [12.656885106566714, 17.98852862133826], [11.828430682885406, 19.483353271334277], [10.88851669407702, 20.919968186894927], [9.777376019573556, 22.240815741073767], [8.531325698550496, 23.435476428960087], [7.171453821515815, 24.485130211170738], [5.705484553607272, 25.38893467029574], [4.1496648698247, 26.110537949372144], [2.5193274857905372, 26.626518446237093], [0.8653091425121029, 26.894502587053204]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.37217166500000004, -0.374475885, -0.514669085], 'construction_scale': 152.1265272837786, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
