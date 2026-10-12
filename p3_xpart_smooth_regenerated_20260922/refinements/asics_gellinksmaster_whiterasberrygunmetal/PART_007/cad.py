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
    from OCP.Approx import Approx_ChordLength
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
    fit=GeomAPI_PointsToBSplineSurface();fit.Interpolate(arr,Approx_ChordLength,True)
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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.1818486043412808, -0.9833265404224216], [0.9975581993461324, -0.06867561933487505, -0.012700323864903733], [-0.06984009534144485, -0.9809254530330528, -0.18140456630029536]], 'axis_rank': 1, 'features': [{'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[-7.227689269594125, 13.441621008442366], [-9.744422679592574, 11.406114066868193], [-10.87504001618321, 9.804505223969269], [-12.265712333137225, 6.981053821222152], [-13.254506973207768, 3.2408781517629395], [-13.199477963330066, 2.036285880734747], [-12.070509036349527, -1.7110221417352522], [-11.005710549753665, -4.100735123402003], [-10.430720243495022, -5.069187894726206], [-9.712287412948463, -6.020762924538509], [-7.785663650678664, -7.974525680591222], [-6.65616942049261, -8.953157215250997], [-5.634307883728049, -9.573215187037311], [-5.467229470388409, -9.490259210699676], [-5.641813119799101, -9.2534297183776], [-9.0512433771711, -6.026059179653184], [-10.358007232440276, -4.239402601852587], [-11.711059977915445, -1.262252396622268], [-12.612841802844367, 1.813417191753547], [-12.62837039751738, 3.420326498936555], [-11.771576422378375, 6.825730755570255], [-10.549471540283852, 9.407676232038407], [-9.168234141093299, 11.297230361025381], [-6.857897430644858, 13.091168281882323], [-5.802566662562098, 13.588561776365717], [8.163713815481152, 18.395302277464573], [13.02166512258683, 19.263381857836087], [15.298077018703143, 19.338314911856955], [20.046312368873586, 20.16613772203763], [22.795689101823328, 20.30283592815625], [22.872648592591446, 20.483199983372042], [23.26323193419918, 20.564174971631886], [18.121423298200046, 20.201526804376755], [13.39841768045574, 19.3897842259701], [10.675877658266316, 19.333377471994737], [8.220894398264342, 18.820582212171093], [5.540772648087503, 18.05474213545575], [-5.255416394323381, 14.3240382133394]]}, 'holes': []}, {'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[5.982191298220034, -11.673280854756337], [2.455387603419364, -9.258829066193536], [2.5860464606874056, -9.045765585731218], [3.397191472173792, -9.398093881671253], [5.4920202560671765, -10.8594969795153], [6.889419765584156, -11.568905933016374], [10.383841177937736, -13.144863442850063], [15.274240333186942, -14.967697781404926], [22.848342778038273, -16.142219528015058], [28.40242287746254, -16.21989346042628], [28.72441165053348, -16.35223688593552], [28.70294974025652, -16.600555225765714], [28.375968256537472, -16.741815865564373], [27.713763034413322, -16.750656817699436], [22.608342858252474, -16.607879329054615], [15.11728934153489, -15.423394626411486], [9.314570434605958, -13.28344669703967]]}, 'holes': []}, {'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[-0.5017050274749958, -12.679237847570969], [-4.157479345234171, -11.038710001024473], [-4.799576860481421, -10.553050270442178], [-5.058459836137014, -10.183672332891444], [-4.847729973396513, -10.082561968832492], [-2.825774617278595, -11.178593664653842], [0.1178431802370416, -12.402174815719079], [2.8929883753008725, -13.160424372209125], [2.4136846765691886, -13.348699981184643], [1.697408000210295, -13.327442172250985]]}, 'holes': []}, {'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[17.037912404713772, 10.435127796543629], [12.609907486017978, 13.222401148115344], [11.68065982726464, 13.575369301700679], [11.439338059239956, 13.483524499494395], [13.227940091702195, 12.548314765240601], [16.823287000743257, 9.989533654494387], [17.19717491418668, 9.783776635394835], [17.660118801089965, 9.766608634272071]]}, 'holes': []}, {'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[19.842881505273294, 9.5518321838185], [20.9042455314201, 9.755210624686207], [22.526735825718657, 10.43946617412628], [23.024223368506195, 10.807256814828987], [23.097101994939294, 11.030810363591865], [22.83876239983246, 11.109073758859955], [20.774103245462186, 10.2505695640302], [19.931901095802402, 9.78931543100104]]}, 'holes': []}, {'z0': -49.18234816932424, 'z1': 54.7475958662691, 'outer': {'kind': 'polygon', 'points': [[-5.122510117140971, -10.012274702416494], [-5.062064384280481, -10.066329997704896], [-5.08433045120466, -9.948148607262198]]}, 'holes': []}], 'center': [-0.01637477499999998, 0.016288794999999967, -0.039739420000000025], 'construction_scale': 49.41006336045124, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
