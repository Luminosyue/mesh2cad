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
                secs=feature['sections']; body=loft([wire(s['outer'],s['z']) for s in secs])
                for hi in range(len(secs[0]['holes'])):
                    tool=loft([wire(s['holes'][hi],s['z']) for s in secs])
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
        if spec['method']=='tracked_smooth_loft':
            if len(parts)>1:
                body=parts[0].fuse(*parts[1:]).clean()
            for track in spec.get('hole_tracks',[]):
                tool=loft([wire(s['outer'],s['z']) for s in track])
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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[-0.9998990455162431, 0.0, 0.014209108899089152], [0.0001232765702091061, 0.9999623638164834, 0.008675007402786738], [-0.014208574122459017, 0.00867588327210361, -0.9998614131322678]], 'axis_xy': [-0.025551488887738897, 0.06821974024776399], 'profile': [[0.8403771307224759, -49.971881640140836], [2.4644288156609306, -49.90209494503007], [4.104046039072109, -49.77631364165609], [5.729222772375681, -49.53091387494977], [7.33916745268214, -49.196666984449394], [8.92249116865478, -48.75711240810711], [10.47379999689423, -48.21419887882253], [11.972236425013197, -47.55328248419819], [13.426554030505118, -46.80324498533491], [14.845724046636935, -45.97479239472641], [16.218560097119443, -45.05278192477735], [17.52741922911926, -44.05484340718809], [18.766340392684086, -42.97503033780367], [19.9247432671351, -41.810941314506074], [20.99138626361102, -40.561835469149344], [21.993814857395265, -39.25896359372774], [22.87244670417744, -37.871305094015405], [23.71494684624412, -36.42323031211704], [24.563314138282454, -34.93505336615207], [25.266657327946497, -33.43026233205857], [25.828069453205458, -31.913209602358233], [26.315249474166553, -30.369566943694892], [26.77226186356221, -28.802545495322626], [27.184160172532806, -27.209373585352203], [27.53536605451552, -25.590135451702153], [27.804352022996987, -23.956844614332375], [28.037829867713405, -22.32544235527051], [28.20079289952941, -20.690172713933297], [28.307550343560862, -19.052127041605075], [28.3903378653376, -17.406359326750042], [28.42543942049288, -15.7595180952434], [28.448851572424473, -14.112347214808505], [28.480437656974715, -12.46452676851979], [28.523875622847733, -10.815721930973314], [28.540614142920393, -9.166785950724826], [28.52038040955765, -7.517997697513616], [28.500629723320003, -5.869483328035456], [28.4869653343249, -4.225538367698773], [28.482343205486586, -2.586040245841476], [28.46959356988588, -0.9400263017258235], [28.473006868802397, 0.7069701595199618], [28.476763848388643, 2.3539898970803517], [28.46788459114409, 4.000977536580823], [28.46569274267494, 5.647805038818321], [28.490368853293056, 7.294437579272655], [28.51896745071231, 8.940650519914609], [28.5327083033645, 10.58716626671795], [28.52322124673649, 12.233720074624575], [28.469475670729594, 13.878430748312724], [28.447671447485508, 15.513983702163099], [28.375956266327, 17.147456448768693], [28.272728503477076, 18.783401383238882], [28.17031015921373, 20.42415196113425], [28.02201401229081, 22.063577357247553], [27.79938734310867, 23.699244050678747], [27.508767712222728, 25.323365223547423], [27.17062432916397, 26.93587099952827], [26.764229744608244, 28.534682527315198], [26.28541810480475, 30.100605669006406], [25.728266696541205, 31.635226816309892], [25.10805450130499, 33.13779175421849], [24.39850228427151, 34.612953751546954], [23.618956271326844, 36.05597945723057], [22.744477917295917, 37.44269159317851], [21.8052138404165, 38.80673541479199], [20.827262166475993, 40.127222207778416], [19.759837132226874, 41.374868471204366], [18.604373807215214, 42.56050641142566], [17.393836933349704, 43.684391880526036], [16.11143003107957, 44.710170803301985], [14.771996782385997, 45.647665889501816], [13.371335595204862, 46.493968316694435], [11.909847899839612, 47.26855055684342], [10.419557395951987, 47.956042906562004], [8.873113876660463, 48.50537962877907], [7.316543874146799, 49.021373993217765], [5.7221349360965075, 49.4034685909739], [4.095306263603871, 49.646692861082556], [2.4619774260311678, 49.83268321297321], [0.8406224071009911, 49.92790974042608]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.0032942200000000144, 0.0013272799999999862, 0.0005686650000000237], 'construction_scale': 55.4114902984039, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
