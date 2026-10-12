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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999796179987878, 0.0, 0.006384636794554571], [8.003142841166281e-06, 0.9999992143684449, 0.001253474548141078], [-0.006384631778582438, 0.001253500096981574, -0.9999788323832455]], 'axis_rank': 0, 'features': [{'z0': -49.968648971204516, 'z1': 50.03634534668307, 'outer': {'kind': 'spline', 'points': [[13.69931074717131, 0.22331143720769536], [13.470453016708445, 2.374084233788085], [12.96011276411433, 4.476387960158723], [12.071339287907366, 6.448373648936348], [10.914686376298576, 8.277901216729584], [9.519827190713714, 9.93049483174941], [7.9134119520106925, 11.379322163510725], [6.096056732492956, 12.553290636824407], [4.110138205166183, 13.408876997263935], [2.02103669293261, 13.96521893347485], [-0.13314049169572162, 14.092515529473928], [-2.289863774038787, 13.90107830141289], [-4.357179370445849, 13.292228018138307], [-6.319945570992401, 12.38704319691563], [-8.067165353993285, 11.112740589031574], [-9.655701579837784, 9.64360744066881], [-11.008496662055906, 7.955537665850954], [-12.098607054153106, 6.087731833503994], [-12.961214855303885, 4.104700214491046], [-13.501214430622735, 2.0105319186525588], [-13.707895099651639, -0.14045380726720944], [-13.448514375194236, -2.2876984762685266], [-12.858779958424286, -4.366137042226526], [-11.934711860602862, -6.3228197943600675], [-10.736451749092048, -8.124278632891038], [-9.329795203967635, -9.767664270936965], [-7.706163491167347, -11.196112833407055], [-5.901438764665157, -12.391919837072404], [-3.944301152507382, -13.309678135538789], [-1.881847050245587, -13.966995882010638], [0.26422959286813147, -14.19864874835416], [2.407447336982819, -13.918555877111102], [4.483522589344453, -13.313859853311598], [6.40187609375146, -12.319586125857674], [8.202731959787942, -11.122808416784885], [9.750005707823567, -9.613298049829485], [11.053948950769229, -7.886296493944792], [12.166916491412126, -6.031634067197444], [12.982878064722259, -4.027872342444772], [13.502042089728562, -1.9282983867284786]]}, 'holes': []}], 'center': [-0.342861305, 0.216618795, -0.07656132], 'construction_scale': 216.4114216581348}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
