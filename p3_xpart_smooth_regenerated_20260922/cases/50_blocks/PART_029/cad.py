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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999984611550716, 0.0, 0.0017543339159688941], [-1.437941257046311e-06, 0.9999996640861989, -0.0008196495725179814], [-0.00175433332666392, -0.00081965083383351, -0.9999981252417874]], 'axis_rank': 0, 'features': [{'z0': -50.004167730514325, 'z1': 50.004173438557686, 'outer': {'kind': 'spline', 'points': [[12.325598843718854, -8.220176463516239], [12.19845155316083, -5.320351414777007], [11.31716780093005, -2.569065940386272], [9.720000774040768, -0.1422640284943426], [9.651761708225807, 2.382153740708462], [11.251085504586896, 4.8062211660775835], [12.192541704998968, 7.543802974897741], [12.229288074964076, 10.445051912651317], [11.720486567505086, 13.301648914878921], [10.518493942861411, 15.941322296046696], [8.730302058786142, 18.22257101845076], [6.370999994545621, 19.90216258402496], [3.6072398521279183, 20.734086931039727], [0.739462544133154, 20.374289226372838], [-2.0401479654647217, 19.516545327851198], [-4.790031418647425, 18.56835238733588], [-7.48748688624644, 17.479660559748158], [-10.015740215559545, 16.0623894569411], [-11.319460847829715, 13.557635956624742], [-10.739437166976277, 10.742933991597267], [-9.311512065737315, 8.215260647939617], [-7.4857056608573265, 5.953252505499909], [-5.882409424537142, 3.5592356694548704], [-8.058108358728386, 1.652467889230999], [-10.012867171692085, -0.493224031465099], [-11.308830737721184, -3.0862210359845], [-11.997674926154986, -5.908183595931634], [-12.076528063442865, -8.809658076112228], [-11.62814001987354, -11.676501545255366], [-10.513122591401032, -14.353447043235555], [-8.839676112420467, -16.727215820085526], [-6.640168622744372, -18.618404611867895], [-4.037845508199998, -19.901363094450975], [-1.2188733616676677, -20.597261191248172], [1.6712336059978152, -20.474736039647514], [4.442574136766208, -19.601958512209322], [6.987073196153793, -18.215482430594662], [9.041000370552762, -16.165880174722915], [10.648252552627502, -13.747760106269725], [11.767155944672528, -11.068983554250792]]}, 'holes': [{'kind': 'polygon', 'points': [[0.67584464821432, 6.554043810317047], [0.4916213386288327, 6.738014430238209], [0.5220474254514373, 7.804617869717078], [0.675842639338404, 7.951091718030826], [1.742447245967229, 8.0316946758876], [2.1902197621118584, 7.804617869717079], [2.5854311034918767, 6.738014430238209], [1.7424496869732367, 6.334127240961698]]}]}], 'center': [-0.09057623, 0.08720484, -0.078670635], 'construction_scale': 216.27712453074622}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
