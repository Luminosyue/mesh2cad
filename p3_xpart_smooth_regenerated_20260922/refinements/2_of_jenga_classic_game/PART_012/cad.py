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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.9999156677432779, 0.012986816450332643], [0.9999990298256338, 1.809016352833018e-05, 0.0013928462000825496], [-0.0013929636718525288, 0.012986803850856226, 0.9999146976507288]], 'axis_rank': 2, 'features': [{'z0': -10.9613022383511, 'z1': 10.979544724135778, 'outer': {'kind': 'polygon', 'points': [[-5.190405082864524, 49.691642333749265], [-25.748922729090282, 49.990916956623295], [-26.67245406303554, 49.815162926740605], [-27.59599157317511, 49.298025943443264], [-28.033065055032402, 48.89049820956618], [-28.572082522839374, 47.96704517010975], [-28.732508630056373, 47.04359587565973], [-29.659415890126, -22.21525100834817], [-29.727331594485076, -44.37808276023197], [-29.602585685373185, -46.22498134913203], [-29.296627530205924, -47.14843438858845], [-28.455336743196955, -48.071885555541684], [-27.59776037428709, -48.470683677306994], [-26.674234507535783, -48.597123316459765], [1.3254968920124133, -49.10408005628193], [2.8786584678219267, -49.24417267598584], [5.649230397011422, -49.93695399934548], [15.91368698085235, -49.98261532209177], [25.0304088296886, -49.87164695494144], [26.890382990515196, -49.76157451329251], [27.813917933902477, -49.386312191570454], [28.73746438399917, -48.47853740056108], [28.97030726566714, -48.071885555541684], [29.19508986057166, -47.14843438858845], [29.3676366883499, -42.45160360240563], [29.485132432239304, -12.85841635625173], [29.719004654572554, -0.05241925646435895], [29.741530981284143, 31.3449260374549], [29.690927826011, 37.08018200881604], [29.44575035019084, 43.34978933534364], [29.2191180111821, 45.19669354175328], [28.82154974656079, 46.1201465812097], [27.81566249086472, 47.04232633845619], [26.892138678160947, 47.28230139755942], [7.498056329266286, 47.773716134336254], [6.574532401396899, 48.110834896760984], [5.651016026679931, 48.76193722591319], [4.727496064730061, 49.214758849694576], [3.8039710663656896, 49.389197707046485]]}, 'holes': []}], 'center': [-0.004651630000000018, -0.05859845, -0.045729535], 'construction_scale': 187.25013809697685, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
