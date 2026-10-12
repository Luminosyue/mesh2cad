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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], 'axis_rank': 1, 'features': [{'z0': -50.00000000000001, 'z1': 50.00000000000001, 'outer': {'kind': 'polygon', 'points': [[-10.42688252838887, 20.25279713456385], [-10.415788252097785, 43.37725121792187], [-10.305439207512597, 45.73906867863462], [-10.147512649573393, 46.66404864254433], [-9.729353032229943, 47.58902485525531], [-8.498689612499291, 48.61230576027253], [-7.576301310582977, 48.94370902550702], [-6.615828278745558, 49.10591102512957], [5.3759779609571545, 49.170529664759506], [6.299891992401365, 49.09611526096789], [8.15091035028882, 48.43510782939085], [9.169339385062289, 47.61620969540107], [9.654612665976783, 46.66404864254433], [10.15976858521732, 43.889110626414556], [10.280838630475305, 42.03915444979386], [10.298150359346455, 38.33924397215185], [10.02427583131481, 30.01443930175937], [10.369733333198214, 24.464570771897293], [10.341767224305837, 20.25279713456385], [10.116628136937072, 17.9897222781255], [9.528496030377376, 16.141629667643922], [10.254202136279634, 13.364831836573773], [10.526066020160739, 6.476865700895541], [10.603361486903726, -0.988787541918867], [10.4392226903729, -12.121440745408208], [10.353718857764974, -13.459536475624995], [9.815529557367013, -16.22941157510386], [9.943342292362065, -17.159450704465748], [10.47405013152961, -19.01509385069836], [10.606680184159222, -21.78434114601748], [10.307080286652978, -44.90879522937549], [10.080518866609795, -45.853121184650334], [9.054069683229367, -47.67135483688853], [8.135273408256415, -48.57806839430611], [7.224776476906799, -48.94419691414563], [5.3759779609571545, -49.149433899751045], [1.6760712345138815, -49.16472261634248], [-6.648742813875456, -48.962865996593344], [-7.573717150987064, -48.75908688496212], [-8.498689612499291, -48.36964354386318], [-9.326372296969527, -47.68372949430653], [-9.817845867119741, -46.75875140599618], [-10.08881737291467, -45.833771442086466], [-10.374601978409325, -43.98381901666452], [-10.436420055984808, -41.720743522761076], [-10.42281268104555, -20.85936118210776], [-10.33800115504786, -19.00940500548707], [-9.598819217557217, -16.234470740556034], [-9.594666603317293, -15.309492652245687], [-10.331673957581705, -13.459536475624995], [-10.482319576935442, -12.543881853315883], [-10.395734764822093, -1.0217018100846875], [-10.50750711871978, 13.369981816352738], [-9.796297398709969, 16.13976610150481], [-9.777635123327475, 17.0629989030783], [-10.2532238713298, 18.91470036643585]]}, 'holes': []}], 'center': [-0.007144994999999987, 0.02245561, -0.73881898], 'construction_scale': 187.5599371224067}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
