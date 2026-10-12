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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.999368540413342, 0.035531963527313984], [0.9994487664411639, 0.0011796201228794524, 0.033177880517017456], [-0.03319884424548223, 0.03551237711660639, 0.9988176549362212]], 'axis_rank': 0, 'features': [{'z0': -51.96383109010069, 'z1': 51.043198783367785, 'outer': {'kind': 'spline', 'points': [[48.94021751408982, 2.5141334718830697], [47.90366836498607, 9.98956091356487], [45.61468990548927, 17.17685888913388], [42.00242916168542, 23.804373153753957], [37.41448070801975, 29.800604012190128], [32.08147945512327, 35.14546022923777], [26.03474346382029, 39.66330056306686], [19.403153111951816, 43.27384623432019], [12.277762111769013, 45.78272763929805], [4.849582971134303, 47.10363147518284], [-2.70033044647222, 47.23192022486934], [-10.179627542473375, 46.22013870756834], [-17.395461570643235, 44.01335545993191], [-24.16435479988821, 40.68127696029121], [-30.290272725365366, 36.2724530383938], [-35.91578027801104, 31.234288446169266], [-40.68531663432573, 25.38197317486779], [-44.54150628093027, 18.893628483707207], [-47.352638207680165, 11.889761453332394], [-48.8897888227177, 4.499371586715803], [-49.12640630393714, -3.0386508784401496], [-47.90566645976008, -10.485760922756416], [-45.630970059345366, -17.68284865601973], [-42.262297998850904, -24.43799050087672], [-37.81736354306747, -30.540068526951107], [-32.50617476237934, -35.900879929641754], [-26.35860942472602, -40.270776571632275], [-19.559765404832174, -43.55264447272686], [-12.405650520967319, -45.959243016464846], [-4.981706924238277, -47.31459794300397], [2.5619479038561566, -47.57668664202854], [10.041877533150602, -46.5667451648824], [17.255635568855563, -44.328558722277755], [24.078553604208505, -41.091648259347934], [30.31442143422595, -36.839147218429105], [35.92893193326331, -31.790388517659242], [40.79517654340179, -26.017402890338676], [44.637193513617596, -19.52105402250872], [47.25895474881734, -12.4479179323344], [48.64772874850934, -5.0278002865969]]}, 'holes': [{'kind': 'spline', 'points': [[39.77755568590564, 1.7648653811475619], [39.04687882380825, 7.9148338980035415], [37.293273752326364, 13.84546988564749], [34.3745317951058, 19.299897908138576], [30.862187960299256, 24.40195103408986], [26.648789158139472, 28.946519217361665], [21.8305502177198, 32.835767468010815], [16.455838769021522, 35.905031550410584], [10.65940291878127, 38.07328502924558], [4.608821863076154, 39.375721625253036], [-1.5770167966981306, 39.58449935247218], [-7.725705185264942, 38.86846213834308], [-13.645658640515775, 37.096705408771854], [-19.19618126148524, 34.35127970469141], [-24.248687264100855, 30.778073552642688], [-28.734897582756684, 26.50814526853855], [-32.56797026733319, 21.64119474801288], [-35.527730225756365, 16.2056394527695], [-37.56594498536312, 10.360934941939513], [-38.77121623048545, 4.2849316807104385], [-39.1553703778078, -1.8858358463431177], [-38.17596062568174, -8.000751152625725], [-36.491104124214125, -13.959342497941163], [-34.011302457719545, -19.634047472961427], [-30.710023713371825, -24.871442115077524], [-26.559695343493857, -29.459314342167428], [-21.637489314320277, -33.19717094133931], [-16.167522137793686, -36.09673512198072], [-10.324797413539475, -38.12836178310135], [-4.2316839841416165, -39.21640410018621], [1.9559715466622838, -39.40660432447133], [8.092028374273825, -38.630095581449275], [14.017037887414078, -36.84129357638331], [19.582340821357953, -34.132512080184526], [24.739264139408345, -30.715456833448084], [29.2862453629109, -26.515864149538633], [33.151996394435045, -21.681660683312664], [36.230866773034236, -16.312111194833154], [38.28839196889092, -10.471511482278991], [39.578114699773764, -4.413867943966053]]}]}], 'center': [0.038450675, -0.6251152200000001, 0.41651669999999996], 'construction_scale': 481.1012831740985, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
