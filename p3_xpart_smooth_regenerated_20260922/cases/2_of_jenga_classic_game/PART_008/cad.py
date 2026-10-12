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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9999987754695586, 0.0, -0.001564947086420409], [-4.5519885791001195e-07, 0.9999999576968192, -0.00029087136840284745], [0.001564947020218169, 0.00029087172458412875, 0.9999987331664295]], 'axis_rank': 2, 'features': [{'z0': -10.834857073007234, 'z1': 10.771194036642278, 'outer': {'kind': 'polygon', 'points': [[-46.562221480416845, -49.65970210127815], [44.13626691142419, -49.6648169135997], [45.98101524769192, -49.518943484777964], [46.9127549499674, -49.150988693816196], [48.0246428414402, -48.023340858600704], [48.38474874682396, -47.0978491456054], [48.52242138384128, -45.246861966325476], [48.782343482199146, -18.407544113477343], [49.237397333645184, -12.854580698992924], [49.557796125029704, 13.328712410273448], [49.81705229865026, 18.612205102055015], [49.85933736325552, 22.715176410258607], [49.94288495847366, 44.5260293652632], [49.865766033842704, 45.458759097305794], [49.508294903162195, 46.37701654454311], [48.664612965660474, 47.27997867152529], [47.83829182141453, 47.651220342284184], [45.328991054800454, 47.87891754200975], [6.191025846573002, 48.58581372888709], [-44.711186886918746, 49.694397404111264], [-46.562176331217074, 49.52583779899944], [-47.472321038481844, 49.11400275561816], [-48.303937474952434, 48.2280056004677], [-48.63523391453127, 47.30273936141127], [-48.77064366341781, 45.451521078258494], [-48.94814736082655, 14.910228866850513], [-49.47301964627946, -12.854580698992924], [-49.3656164597976, -15.631063344557468], [-49.71296342613638, -19.333037703117302], [-49.73628120308099, -20.80434380286328], [-49.97660685762836, -45.71034753695898], [-49.9356519715559, -47.09050507306207], [-49.68756026990534, -48.024025649898], [-48.98519235243609, -48.948838201529995], [-48.40842114151922, -49.35314577272479], [-47.48771613794335, -49.60201627499802]]}, 'holes': []}], 'center': [-0.008331245000000015, 0.029044610000000012, -0.84055316], 'construction_scale': 187.66445857536968}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
