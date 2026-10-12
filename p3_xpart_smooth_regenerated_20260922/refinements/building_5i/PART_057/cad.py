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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.023745083990898915, -0.9997180457440314, 0.0], [-0.021749966695272675, -0.0005166004436722324, 0.9997633080248227], [-0.9994814205051636, -0.023739463720068354, -0.021756100920520497]], 'axis_rank': 0, 'features': [{'z0': -21.071404625060058, 'z1': 22.01188855928546, 'outer': {'kind': 'spline', 'points': [[45.76753723999726, -14.364907956871098], [37.655706233129166, -9.626598418664612], [28.043195358476712, -7.826911218500705], [20.16777108461526, -2.0634683359822055], [13.334891530194772, 4.983550843919544], [12.542920627911268, 14.413379325736777], [15.760724222701882, 23.69750395420232], [18.86479899902371, 33.008058521541564], [22.15946053236311, 42.13653587089584], [16.144939737385698, 44.17379876756314], [6.731461779465671, 42.13290560412496], [-1.2354208068154355, 44.651930605343495], [-7.12481474260718, 47.74005197852267], [-12.282516340153684, 39.38169774521188], [-6.307254621684308, 37.25528702913877], [0.20105031584304078, 35.17593760092654], [-3.9824890596961806, 26.320132314738352], [-7.511035301094356, 17.178873323465908], [-10.919026034094273, 7.977515529543307], [-15.381334747755064, -0.7733774226806597], [-19.802941378406267, -9.545726195486315], [-23.979353420854427, -18.440619015368906], [-27.450844442001973, -27.605158678422544], [-30.731507057788395, -36.86255329191838], [-35.78038423377367, -40.748871885452765], [-34.24271296371739, -31.4531782255827], [-36.715534641994424, -25.909868642846895], [-41.08819841840478, -34.70637286449825], [-44.83691902122276, -43.784721429338745], [-41.92182174382635, -49.92359211043697], [-32.09468854063315, -49.911820433414114], [-22.267544127526026, -49.909395004338535], [-12.440413483465596, -49.91063337942777], [-2.6132633195663315, -49.91397221408066], [7.213850184338913, -49.922511825744905], [17.040975270848826, -49.93310332555324], [25.78242910341991, -48.01325688166227], [30.21348649144993, -39.277785365858186], [35.40741508320716, -30.936466113661712], [41.11796048440065, -22.94317094892992]]}, 'holes': [{'kind': 'polygon', 'points': [[2.9696084439832795, 32.91869884597913], [1.8605679586474455, 29.928987085062708], [0.7163588191988124, 25.641081249046536], [-0.5648808784443357, 22.189388949027414], [-0.6731324630228068, 21.592602128385213], [-0.1267424368863374, 21.19761263149778], [1.5129945215991305, 22.420918655718985], [2.575550199529886, 23.77239935201876], [5.125633321615565, 28.39594650527231], [6.95550894716264, 31.342401064647717], [8.216738310941343, 34.03284577903933], [8.43021839291438, 35.65301040222935], [8.227473300462336, 36.73567250488285], [7.487506257189246, 37.81205513744746], [6.362402316841092, 39.05194183506408], [5.800050581182241, 39.95584349454568], [5.259171568752128, 39.98442546657828]]}, {'kind': 'polygon', 'points': [[0.9370145857272129, -11.430097999535572], [0.9878505367649282, -12.311956127596012], [1.5108070581139512, -12.538404414056785], [2.0564108683034528, -12.698759596195783], [3.663541049924233, -12.44058135825354], [4.775144302574083, -11.924676868665347], [6.268889257844766, -10.894170497696665], [9.311011875138462, -8.25938805766925], [10.52639158303933, -6.923985405923328], [11.510460169396435, -4.764897896193414], [11.4794512730144, -3.697850937752177], [10.825049803458095, -2.5746240531547464], [10.115807655393311, -2.021559430171788], [9.599253147477096, -1.8438992837016268], [9.052451456110443, -1.9131358305580557], [8.518219327617892, -2.338151365305254], [5.6512144930950186, -5.596852570260704], [4.319471312802304, -7.325312078171797], [1.70176576855851, -10.159160634864984]]}]}, {'z0': -21.071404625060058, 'z1': 22.01188855928546, 'outer': {'kind': 'polygon', 'points': [[35.09210760580912, -44.74643804628705], [33.16065089529612, -45.68775688904626], [31.30539372489788, -46.8280774648147], [30.631307295665756, -47.37720256632309], [29.06847398337406, -48.96588498241936], [29.179047737983876, -49.51267265395189], [30.38545159724876, -49.75248031360961], [31.83295154552251, -49.846145722416225], [39.24274875672612, -49.98595688364118], [39.804012054627144, -49.827294185099475], [40.140673247780256, -49.46796773507192], [42.27591938887633, -45.97120836403339], [44.761882801495304, -40.61572601364223], [45.26175096435697, -39.29139527922775], [45.49493772814883, -38.03932628656386], [45.473417709678294, -37.103930514908875], [45.21449159760713, -35.92687433498639], [44.66251181720668, -35.32595717677251], [44.100332445495575, -35.38099408111445], [43.030552573001785, -36.092999358501665], [42.43681282971825, -37.00884336960649], [41.98639549975644, -38.72293064262545], [41.42129372819786, -39.46704472368368], [40.338911357429986, -39.88676140474707], [39.261969749605775, -40.62333290755492], [36.591918270539075, -43.605480058312025]]}, 'holes': []}], 'center': [0.03334121500000001, 0.41337861499999995, -0.005585535000000003], 'construction_scale': 109.26688161574774, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
