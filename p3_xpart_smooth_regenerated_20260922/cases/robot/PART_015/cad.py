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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.1322642706378522, -0.9912144887523775], [0.9997634775341651, -0.021557239999234867, -0.0028765243626056656], [-0.021748310021545942, -0.9909800442573263, -0.13223298716641907]], 'axis_rank': 0, 'features': [{'z0': -48.75022529715307, 'z1': 48.26015356231125, 'outer': {'kind': 'spline', 'points': [[24.67484362341406, 1.6222313839587046], [24.072326138165764, 5.4059497321002725], [22.863328183372353, 9.04486199154964], [21.044910432729736, 12.420201178572517], [18.808893624702804, 15.536042964856327], [16.09150340427769, 18.242104232248497], [12.997913724118852, 20.50828054932553], [9.593601866283732, 22.26548937808326], [5.948235263279662, 23.457613721766034], [2.1604771623724472, 24.06431933546402], [-1.669216123073933, 24.096070880261394], [-5.454969325729726, 23.471652571137678], [-9.060895548239506, 22.189533676598025], [-12.487677877736749, 20.460521412453815], [-15.615359984832434, 18.240280615819696], [-18.327240380129012, 15.529092133902942], [-20.646511397089146, 12.474575246916306], [-22.466395079072292, 9.10085924594372], [-23.68362911300359, 5.4683580971148205], [-24.413750969690042, 1.7031911842456013], [-24.356150052370634, -2.127625631619188], [-23.692250148924497, -5.901077053942948], [-22.534231655687112, -9.557401016848653], [-20.725125577348837, -12.929241097887841], [-18.461262990381808, -16.02711769873319], [-15.740233745596335, -18.72863787934728], [-12.622074545022551, -20.96171903380426], [-9.172552904569471, -22.638537216658452], [-5.50693299423918, -23.759587535839852], [-1.7264145122263037, -24.414724342370544], [2.1082014126594926, -24.485010562434958], [5.911232791368268, -23.99419687247518], [9.573945784820829, -22.85936239646337], [13.015235783910589, -21.170341599439926], [16.12878145524673, -18.929720041182673], [18.844014791182776, -16.221771574434744], [21.03949184044409, -13.079017707523755], [22.766046734986244, -9.655657660862902], [23.906655685582695, -5.992785783357814], [24.558400802077028, -2.2124911654753374]]}, 'holes': [{'kind': 'spline', 'points': [[21.76845557851874, 0.20639590935723598], [21.55159239343938, 3.5783599596712943], [20.65663631910378, 6.8342197687369985], [19.21716537233309, 9.892091505442616], [17.387192436884245, 12.736018941637317], [15.141407846104734, 15.257317957766439], [12.52806360098345, 17.402304207672515], [9.621556696251814, 19.12499271812174], [6.4818013678458675, 20.380372348625205], [3.1827543250034713, 21.111266284177393], [-0.19253218681252227, 21.287503359230225], [-3.5515566187661256, 20.916913471563213], [-6.806534364986506, 20.01551455430734], [-9.861700359607218, 18.56906828004933], [-12.740915053276503, 16.80090020283975], [-15.270401100776636, 14.560080712953567], [-17.448925792342354, 11.976191444169837], [-19.253990622677954, 9.118194633761954], [-20.501941856615854, 5.978211521348508], [-21.3743358679979, 2.713593144248171], [-21.600418169335757, -0.6471556278237436], [-21.19734775234619, -4.005419861839226], [-20.27542535917707, -7.256094184070506], [-18.900221559351586, -10.338000322544085], [-17.01591885193626, -13.142863235430337], [-14.760298620979555, -15.657015118016837], [-12.153509203452886, -17.80844087074222], [-9.221281259157015, -19.492303261474838], [-6.0497372396266105, -20.651982285279566], [-2.739786390560659, -21.343925582933995], [0.6302392487184498, -21.571900717980004], [4.000986546298795, -21.329862522058974], [7.284403916547948, -20.525143148876698], [10.403232077788472, -19.224460093802602], [13.263443224216552, -17.42012783904762], [15.835484501546603, -15.227273457181369], [17.928559779489227, -12.577003131599247], [19.57261479380408, -9.622877830159032], [20.770361341493167, -6.463670877710119], [21.485495368242557, -3.1619039318665907]]}]}], 'center': [0.02532658, -0.13797516, -0.29751716], 'construction_scale': 268.4907426539859, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
