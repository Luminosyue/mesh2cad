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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.99980594180664, 0.0, 0.019699713910046844], [0.00024054615034807826, 0.9999254473342235, 0.012208272236586512], [-0.019698245243859817, 0.012210641811676252, -0.9997314036084191]], 'axis_rank': 0, 'features': [{'z0': -50.620641261423444, 'z1': 50.39632030100099, 'outer': {'kind': 'polygon', 'points': [[-16.13823597430555, 32.50563389867506], [-16.036668150409007, 27.97673277785446], [-15.736787962181147, 24.1064599979359], [-15.694002036651375, 21.451375207308573], [-15.945465899706349, 19.984919081510817], [-15.931861971712161, 16.94426186950989], [-16.087043807146802, 15.185471105181927], [-16.199346816949742, 2.8917354985930115], [-16.22550264881879, -17.63725297331243], [-16.153435905564365, -22.575312588963442], [-15.963856118609467, -25.895105517282627], [-16.389823136698563, -32.74042198023817], [-16.04539399811348, -33.23823831553606], [-15.529860047636191, -33.37049153177729], [-5.163784543911029, -33.02140886218849], [6.375231769680912, -33.01628077167141], [12.91493188797844, -33.31222562399748], [15.076094065062865, -33.3539807839887], [15.79312840452577, -33.24477343846246], [16.20799593306452, -32.741344370949356], [16.04495400414879, -27.23505140119906], [16.238568831030037, -17.378346524781826], [16.22539437754196, 13.226307935373928], [16.109336443115566, 19.85647614850307], [15.886553040417583, 21.46207759113619], [15.84478053981525, 22.854204864519303], [16.295257556365936, 32.48363377682843], [16.10842452255389, 33.01102390873617], [15.595706263693836, 33.39755455010933], [15.092157914841904, 33.41379926208935], [-14.931746000965763, 33.40916775757961], [-15.52764335913652, 33.39055876878571], [-16.046838213745307, 33.009335517491195]]}, 'holes': []}, {'z0': -50.620641261423444, 'z1': 50.39632030100099, 'outer': {'kind': 'polygon', 'points': [[18.109460113097562, -2.6604248156143004], [17.961643370606243, -6.258889269222874], [18.26301806012874, -10.82004620722432], [18.196846491461482, -14.596965922736812], [17.274221869341176, -21.603485068158392], [16.92463388182735, -23.231073636721426], [16.7646382901957, -26.12658959275833], [16.995353805046193, -29.38668080739191], [17.309032557493566, -30.631871912458852], [17.318492492003823, -31.54746594983851], [17.200615440108468, -32.23013514657668], [16.912117119723014, -32.76107313256869], [17.579663767615116, -32.96039238953013], [20.597747903961697, -33.01666426313471], [21.09919070594114, -32.969617319817736], [21.320704899417915, -32.74333580271038], [21.38074911135368, -32.190005845166695], [21.443244004946937, 31.370510780581267], [21.3743068301166, 33.00373203196147], [21.114786927504483, 33.32531201585871], [20.607814249554867, 33.385555252085396], [18.10391223446185, 33.35951247809576], [17.59929662820662, 33.27349148687813], [17.22400522630421, 33.00097569625982], [17.695024540829113, 31.771631744644846], [17.909384960530353, 30.525453766727747], [17.84802092506518, 28.443796915252697], [17.506577150398083, 25.9761976031271], [17.533160608800806, 22.43646506769513], [18.00937719720506, 21.167965247962492], [19.152821199339503, 18.93900825350386], [19.35010456000886, 17.974203835391478], [19.102971685391093, 16.043875869557056], [19.331800997274527, 15.179240019076268], [19.949982635516285, 13.721055091983347], [20.09928475417883, 12.595771291866653], [20.03747699141397, 9.438647694074282], [19.398694789216126, 6.9083824692840095], [18.82465386632527, 2.7421723137091982], [18.78919646351344, 1.283031146357241]]}, 'holes': []}, {'z0': -50.620641261423444, 'z1': 50.39632030100099, 'outer': {'kind': 'polygon', 'points': [[-18.22843194743902, -27.746383606064526], [-17.871494107843116, -25.770574958449092], [-18.20548915717298, -21.629261082526448], [-18.17895653737441, -16.70911245585931], [-18.483349513209728, -13.664143461971797], [-18.478534216918142, -10.672219080324087], [-18.155887006433556, -6.203512566516736], [-18.177379091801143, -2.195338100294981], [-18.286925116671767, 0.10359831060570338], [-18.96611178535988, 3.847728958492233], [-18.52449415672954, 8.812972534264917], [-18.4658441532584, 10.970953255870151], [-18.00912756162945, 15.38643593721895], [-18.29757308938549, 17.46437105251493], [-17.982916225556593, 20.387201081145648], [-17.574132126651765, 21.927080975973443], [-17.566769371925663, 22.700042191541606], [-17.990481951286643, 24.825481441970645], [-18.135580960764965, 27.678180135812], [-17.92322845477079, 30.60211327919696], [-17.67552793605355, 31.537487661448075], [-17.744287588706523, 32.50842635101863], [-17.62370969760614, 33.01039750734561], [-18.538711762168443, 33.293718779795924], [-20.52894622815117, 33.38320936927028], [-21.04847613576555, 33.33625031145185], [-21.363474856684277, 33.006748179539294], [-21.419570405385613, 32.49424701477532], [-21.41383708447988, -32.2287821989004], [-21.336695314425395, -32.74271360799991], [-21.063752132268416, -32.992066941770226], [-18.08933472511217, -32.92729636654027], [-17.4783767549791, -32.725938060526836], [-18.111271468629152, -31.59145824812036], [-18.156985517871615, -31.222192901651763], [-17.916497472581423, -29.742107896524864]]}, 'holes': []}], 'center': [0.0004534250000000073, 0.02210523999999997, 0.007495319999999972], 'construction_scale': 50.8820241145991, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
