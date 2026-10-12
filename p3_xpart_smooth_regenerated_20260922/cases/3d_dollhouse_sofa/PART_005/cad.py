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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.007290321426998814, 0.0, 0.999973425253637], [0.004304776544120477, 0.9999907339140435, 3.138403870091174e-05], [-0.9999641594139244, 0.004304890945505474, -0.00729025387425382]], 'axis_rank': 0, 'features': [{'z0': -50.04673080626749, 'z1': 49.9474255457276, 'outer': {'kind': 'polygon', 'points': [[10.216970717207385, 0.6745762954764003], [9.660341774541594, 0.3759879964088923], [8.64236362643969, 0.0870918993413278], [7.016680193030377, -1.7235880524814338], [4.482466643629884, -3.4152502194366945], [2.8684799729229384, -4.052725094804411], [0.7688687593066574, -4.07327352498774], [-0.7988407093518908, -3.874762767868704], [-4.657887976627298, -3.825498232514123], [-4.994741984677768, -3.5725356991473065], [-8.14808269152607, -3.5314936918065385], [-9.730874794994115, -3.302718579089611], [-10.224167255062493, -3.0689192253361672], [-13.275631091524087, -2.773375544757029], [-12.878658005516037, -2.430857164977223], [-10.499622690848344, -2.6115265877851948], [-9.638303349029375, -2.7732574148006215], [-9.198473028320501, -3.0366564993781955], [-4.37457152816427, -3.2971172132084687], [-3.955275473277475, -3.492862576096037], [-3.45176543858961, -3.527970949118741], [-1.8556646700741215, -3.4592373705931037], [1.8186614217286687, -3.6590372852230586], [3.393365613002072, -3.488004420817181], [3.505213116786941, -3.298268758725258], [4.443151919678047, -2.9051714012809686], [6.017828462354654, -1.870142106694777], [7.067606037958034, -0.9582458146473846], [8.107792878576774, 0.3770364096151622], [8.642264890734156, 0.6065145723659922], [9.165248076352718, 0.6665211807803454], [10.306894219563105, 1.4257760208540553], [10.977728767053666, 2.4764643227964234], [10.897124005006491, 3.0000113215304127], [10.485621346536744, 3.5253515375748137], [9.781062739403998, 4.0505554212567425], [10.21679051179973, 4.351338397167251], [10.69615980504232, 4.050652559797558], [11.14423446984308, 3.488933829288592], [11.353298621926017, 3.000456727097878], [11.357896011069162, 2.4755624487905137], [11.266734035085893, 2.0407591156132523], [10.924921752313034, 1.4257760208540553]]}, 'holes': []}, {'z0': -50.04673080626749, 'z1': 49.9474255457276, 'outer': {'kind': 'polygon', 'points': [[9.16708458337886, 3.2894408464424996], [-8.151050170075791, 3.257086163464084], [-8.680143247324496, 3.000456727097878], [-8.154694816108345, 2.7572171658429014], [-2.0394484262018557, 2.742067394144553], [9.167101123885546, 2.762419219854154], [10.129719429121678, 3.0004963566431893]]}, 'holes': []}], 'center': [-0.001522490000000043, 0.259247425, 0.222266785], 'construction_scale': 53.2164637349064, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
