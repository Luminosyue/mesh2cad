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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999852969118507, 0.0, 0.005422726262485252], [2.4607371681629112e-05, 0.999989704028437, 0.004537756229280267], [-0.00542267043024986, 0.004537822949291097, -0.9999750010916703]], 'axis_rank': 0, 'features': [{'z0': -50.000778178964744, 'z1': 50.0434404679638, 'outer': {'kind': 'spline', 'points': [[12.701013814059788, 0.5749382397830023], [12.501283763979627, 2.6121375442147965], [11.894778989578178, 4.570322132951002], [11.024998244227811, 6.424454772608559], [9.858243841469948, 8.108796369557187], [8.463968662592244, 9.613771723018031], [6.8832690670657914, 10.916532464024348], [5.1323831233618264, 11.983615999929558], [3.2247465811571603, 12.735002103291544], [1.2434838997812525, 13.245144116260924], [-0.8008809989250688, 13.395974818521822], [-2.840841996940546, 13.231689164095126], [-4.816261094036686, 12.685798760455302], [-6.678188963455972, 11.831414357523919], [-8.349365187111577, 10.652857112592084], [-9.775759632655928, 9.182020792822494], [-10.931191058094228, 7.489228064051549], [-11.757777241325227, 5.6162451693621], [-12.301236383756775, 3.6387490451487015], [-12.619115793294782, 1.6122147023081315], [-12.617050610532575, -0.4378195560340085], [-12.428110395297162, -2.480349077406366], [-11.968430960262243, -4.478391899899766], [-11.179921050639601, -6.368468283000083], [-10.095869962293433, -8.107728292544017], [-8.773280560551253, -9.67403449447637], [-7.225708455072003, -11.017575479230791], [-5.4985399522305265, -12.123475274730227], [-3.6099566995635644, -12.923024965746201], [-1.6218669621877628, -13.405679047179888], [0.42613344775721596, -13.443262023996601], [2.455669713043624, -13.169382810400643], [4.39143363975318, -12.498454355824265], [6.2066984457166905, -11.547468640663332], [7.857731539991508, -10.332123210895455], [9.273036770218273, -8.852521806042853], [10.496004980225297, -7.20529894917736], [11.48611314122583, -5.411487888840523], [12.191731000093727, -3.4866233579254753], [12.564244343704296, -1.4706217854178925]]}, 'holes': []}], 'center': [-0.454456545, 0.204381115, -0.07518644999999999], 'construction_scale': 216.09993809601173}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
