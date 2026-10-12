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
    return partition_periodic_faces(body)

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
            elif spec['method']=='smooth_loft':
                secs=feature['sections']; body=loft([wire(s['outer'],s['z']) for s in secs])
                for hi in range(len(secs[0]['holes'])):
                    tool=loft([wire(s['holes'][hi],s['z']) for s in secs])
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
    # Local basis columns -> normalized source axes. Rigid transforms preserve analytic surfaces.
    from OCP.gp import gp_Trsf
    b=spec['basis'];t=gp_Trsf()
    t.SetValues(b[0][0],b[1][0],b[2][0],0,b[0][1],b[1][1],b[2][1],0,b[0][2],b[1][2],b[2][2],0)
    return body.located(cq.Location(t))

def build_model(spec):
    return build_normalized(spec).scale(1/spec['construction_scale']).translate(tuple(spec['center']))

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9999042925513254, 0.0, -0.013834946238906475], [0.0001801607958332059, 0.9999152081621695, 0.013020907345233328], [0.013833773148388592, -0.013022153662336599, 0.9998195088287054]], 'axis_rank': 0, 'features': [{'z0': -49.89640895728018, 'z1': 50.306014018586815, 'outer': {'kind': 'polygon', 'points': [[-13.49126914460225, 17.11812001025039], [-1.8128883677926775, 25.239827840391943], [0.20925607064954815, 26.45579771331729], [1.263207526729367, 26.812962996875378], [2.3172273295714008, 26.790799244921615], [3.3892755289815066, 26.315143946706282], [4.534076768075413, 25.239827840391946], [10.985902999596275, 13.645782642216014], [12.860448275325531, 9.791771260874727], [18.573548291314225, 4.159730191002244], [25.510944632168417, -2.986530069224285], [27.619546200111305, -6.173508932916781], [29.364706948711213, -9.542316303051035], [30.13346759565838, -11.650324909488258], [30.27751489403668, -12.704331349935668], [30.169784000692605, -13.75833565315428], [29.87187664058048, -14.812339956372892], [29.03375249134786, -15.866344259591502], [22.865406410460277, -20.082361472465948], [17.75004318086342, -23.76622950248634], [13.688406012813196, -26.40638729177762], [12.867918784939853, -26.73043387230223], [12.191764750840735, -26.77852865199275], [10.758974866669714, -26.606727566666695], [9.704838466360684, -25.93744018711832], [9.076424883682304, -25.352382988559008], [7.5135485782336655, -23.65286378033193], [-3.664048592105564, -9.542316303051035], [-5.054581913679873, -8.194373964180665], [-6.108682991126809, -7.7211307976264205], [-8.216080942338992, -11.238027908662186], [-12.431038651447812, -17.373784366212952], [-13.484939824311967, -18.010024811244953], [-14.539011892396443, -17.697785518553193], [-15.447440182949396, -16.920346425581318], [-16.304078748317156, -15.866344259591504], [-19.810421584003866, -10.324482698146626], [-24.126553474132134, -4.406490767741932], [-27.19044229331348, 0.27638388277938153], [-27.49935965474631, 0.9977267291350832], [-27.41777713327319, 2.05173316958249], [-26.522681097299238, 4.159741776019713], [-25.8822900733769, 5.213743942009525], [-24.029576748443468, 6.8359146142280345], [-21.921776303120385, 8.1189428785354], [-20.867810896990022, 8.3986844620086], [-18.759794417022533, 8.482706209474927], [-17.705935842139485, 9.367230147795592], [-16.81461077580855, 13.0404811056755], [-16.104127348481406, 14.69978480820583], [-15.5989950660164, 15.421479138996474]]}, 'holes': []}], 'center': [0.04337012, 0.17781486000000002, -0.07891535000000001], 'construction_scale': 213.70475790135941}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
