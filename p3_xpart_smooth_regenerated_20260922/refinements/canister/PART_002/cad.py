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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9970404639083418, -0.0, 0.07687856222275914], [8.770124615043713e-05, 0.9999993493144399, -0.0011374001882840268], [-0.07687851219898882, 0.0011407763570853312, 0.997039815148509]], 'axis_rank': 0, 'features': [{'z0': -52.253439163070865, 'z1': 52.28423933366277, 'outer': {'kind': 'polygon', 'points': [[45.025446678201654, -5.86196096644187], [-44.41369154224597, -5.878174273647468], [-45.51848879495793, -5.836754023619448], [-46.374274675721004, -5.605669790803884], [-46.97548401687246, -5.122870666820614], [-47.25174944167925, -4.594983657299788], [-47.31258404707273, -4.100755322920091], [-47.11282947907934, -3.578322061422376], [-46.3886431860556, -3.171411419836534], [-42.77675012835493, -2.633893443719233], [-42.44982865971049, -2.105013484688386], [-42.15971774249835, 0.5597210095523804], [-42.30326296931257, 1.0925547277624148], [-42.87673068295226, 1.54998051996948], [-45.08753578705884, 2.020860131952562], [-45.86223266769609, 2.3191322677268253], [-46.104511262138125, 2.561391780635123], [-46.34864759031868, 3.063178947458143], [-46.46441512876517, 3.92445485955788], [-46.28136885190471, 5.289562987171257], [-45.85143751475033, 5.774322181923852], [-45.275413721087666, 5.8600491808869535], [-41.39001725838498, 5.735648568651278], [-40.84526547456738, 5.577372000137978], [-40.667355009276896, 5.276475290769829], [-40.64696530580264, 1.2529882962479708], [-41.19348688847133, -2.6623072929530167], [-40.89356714641897, -2.8427480307423307], [-40.11816386853152, -2.988779016504963], [-34.997189960522654, -2.7817267657573845], [36.18964752221007, -2.7534332158733488], [38.913189064083596, -2.9168750660173477], [39.40851661558634, -2.785058361530074], [39.6062961569046, -2.3507789607094445], [39.88919616199971, 1.2401010648717978], [40.73451226593958, 5.533493323484025], [41.15480568191378, 5.818966242029685], [41.72112322507049, 5.867313969182796], [45.35644152914833, 5.83112327779991], [45.85450910233888, 5.546448065318687], [46.06760873328302, 5.011575172126071], [46.02362792995248, 3.71527255225173], [45.8328930729862, 2.818271716105868], [45.362056373829304, 2.3215541986352393], [42.93783567681146, 1.5792281154162948], [42.38111356911922, 1.0948890071888142], [42.170162001706764, 0.2030198835241526], [42.18050742817379, -2.0784172634280798], [42.38301298362297, -2.5209272291467646], [42.87872518993228, -2.7560766295017096], [46.3766247913917, -2.8495421793083078], [47.1202091094148, -3.341300856387761], [47.29195342978569, -3.853642658964458], [47.1061562752003, -4.8727003922526455], [46.773214519808135, -5.331378081896248], [46.09561798538246, -5.714095423196534]]}, 'holes': []}, {'z0': -52.253439163070865, 'z1': 52.28423933366277, 'outer': {'kind': 'polygon', 'points': [[50.01139157156322, -0.6411634962771535], [49.36414604538598, -1.536932467278326], [48.826969777667415, -1.7801639419179625], [48.08342627958654, -1.7523615189576964], [47.558969991749336, -1.4490161910200778], [47.396811468089176, -0.88827966777929], [47.50481816804903, 0.021586927416937757], [47.69754514810501, 0.5944018278132968], [48.07688656195404, 1.0929554753686728], [48.57884853405559, 1.3545435231111482], [49.086989605293084, 1.354193806858611], [49.844689643528625, 0.8595655276631545], [50.083848143066355, -0.009880387460393453]]}, 'holes': []}, {'z0': -52.253439163070865, 'z1': 52.28423933366277, 'outer': {'kind': 'polygon', 'points': [[-49.07261227267745, -1.796374428257244], [-49.511160765849134, -1.6146731180941882], [-49.951504150764045, -1.1353918306568498], [-50.06771403535257, -0.017972576035976982], [-49.77692843805268, 0.7911935889310378], [-49.32773428595362, 1.1386385577238651], [-48.81980735464043, 1.246366302324697], [-48.33468390189278, 1.0551938341625995], [-47.86427548550135, 0.5227652798507991], [-47.659423397656155, -0.8413985078330973], [-47.81384215562778, -1.405193244032557], [-48.065919871342466, -1.6389211805961865], [-48.50151115798221, -1.8200565744287325]]}, 'holes': []}], 'center': [4.840000000005951e-06, 0.85610591, 2.0675000000025534e-05], 'construction_scale': 50.10777455744576, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
