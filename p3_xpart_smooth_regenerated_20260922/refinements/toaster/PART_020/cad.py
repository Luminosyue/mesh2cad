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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9999984565857156, 0.001756936591543059, -0.0], [2.1900619641002083e-06, -0.001246521129145494, 0.9999992230898374], [0.001756935226561166, -0.999997679676752, -0.0012465230530469798]], 'axis_rank': 0, 'features': [{'z0': -50.03606809784618, 'z1': 50.01165042469306, 'outer': {'kind': 'polygon', 'points': [[20.533769342216416, 2.8339075453838984], [20.23521586429822, 2.729445254536288], [19.882694005442413, 1.9972636189259316], [19.218520312303614, 1.406868081823568], [19.147813574260258, 1.1116721090066843], [19.352986149620108, 0.7350472801196368], [19.94337999771318, 0.6196335389309151], [20.194467036331456, 0.8164719461431083], [20.523119306946608, 1.733169621017193], [20.82896887712663, 2.1306918240088337], [26.829603429970692, 1.9972636189259316], [26.982710103062924, 1.7020676461090483], [27.02787788544259, 0.22030664813996628], [27.32331749301211, -0.015991265485460475], [28.799306071979725, -0.1989054909841954], [29.06019365883956, -0.3643149380149197], [29.15808635932111, -2.430692733514092], [29.389705382807115, -2.8086440371604815], [29.684903599727114, -2.9100556975578655], [30.275297700544158, -2.867549682949089], [30.576978771399066, -2.430692733514092], [30.605376393271047, -0.36431493801491976], [30.865687936141285, -0.24020956161090382], [32.046475657421176, -0.2091796410925114], [32.34370916713126, -0.07095493292855247], [32.4897978531593, 0.22598845699801423], [32.34216605077071, 0.5217330230465601], [32.04647380381471, 0.637190747350403], [27.91370959090274, 0.667750346953501], [27.786145654264573, 0.8164719461431083], [27.518312987140302, 2.587659156028295], [27.02811324296543, 2.8401905665046034]]}, 'holes': []}, {'z0': -50.03606809784618, 'z1': 50.01165042469306, 'outer': {'kind': 'polygon', 'points': [[-29.345962664212884, -2.139958027706016], [-29.243132870595442, -0.3637855492577148], [-29.059393111800972, -0.2250046099167606], [-27.288207353410016, -0.03560186372929176], [-27.110371914792527, 0.22608119766553997], [-27.070444552230793, 1.702067646109048], [-26.993015506489627, 1.951629149395938], [-26.697817779560268, 2.0739508308735375], [-21.089066332348665, 2.201146944041735], [-20.720691594362652, 1.9972636189259316], [-20.484566159630397, 1.1191890325784641], [-19.90827285765882, 0.6983889644830149], [-19.45632538956867, 0.8164719461431084], [-19.413437232994244, 1.406868081823568], [-19.908275529597685, 1.9184159709748827], [-20.199612278823185, 2.597901886813633], [-20.49867406143714, 2.8058859385396238], [-21.678725226687735, 2.9051989445258717], [-26.993017495278856, 2.859724989113663], [-27.5860604308134, 2.5906336744930436], [-27.892196533635737, 0.8164267570720507], [-28.152869499680204, 0.6875413794863003], [-32.01136884625065, 0.5841113838503121], [-32.46320968522192, 0.22608119766553997], [-32.36788077205147, -0.06911896519804281], [-32.01136701383698, -0.252582221260033], [-30.865545653946658, -0.3641751911815077], [-30.761217499682672, -2.1354973592753113], [-30.535373888935027, -2.5112036173905192], [-29.944979546210124, -2.579154515977973], [-29.466659124371144, -2.434760285839025]]}, 'holes': []}, {'z0': -50.03606809784618, 'z1': 50.01165042469306, 'outer': {'kind': 'polygon', 'points': [[-2.1964312429023454, 2.231218724961616], [2.2312295062686713, 2.2303275897541837], [2.4523465363721964, 1.9972636189259318], [2.5454062068748446, 1.406868081823568], [2.821928432397193, 0.9791982325488946], [3.4123238399433102, 0.6983574975729147], [3.707521255480862, 0.6895475898818602], [4.00307605117707, 1.1114277216720068], [3.927322448536525, 1.702067646109048], [3.7075186443520445, 1.8818082793918485], [3.1673867757381435, 1.9972636189259316], [2.8219245562130055, 2.7490925406525624], [2.5321698784197184, 2.8862847587743437], [-2.3455154786417576, 2.8970579820630364], [-2.7868274116389307, 2.859624645609746], [-3.082024317065554, 2.6355141385338947], [-3.3772204494298195, 2.0584176531105167], [-3.9676146194256785, 1.7741838064392756], [-4.114644055091741, 1.1116721090066843], [-4.004451116271834, 0.8092604040128976], [-3.6724147927020394, 0.6644085355272106], [-3.2082697137333334, 0.8164719461431084], [-2.6240119553767727, 1.9972636189259316]]}, 'holes': []}, {'z0': -50.03606809784618, 'z1': 50.01165042469306, 'outer': {'kind': 'polygon', 'points': [[-21.334849650393757, 1.1116721090066843], [-21.438125988463824, 0.8164719461431084], [-21.97465516682767, 0.6695712609723665], [-22.367448902786045, 0.8164719461431083], [-22.452063697578172, 1.1116721090066846], [-22.269854412977033, 1.2409366446837342], [-21.67946030216089, 1.2788769985390962]]}, 'holes': []}, {'z0': -50.03606809784618, 'z1': 50.01165042469306, 'outer': {'kind': 'polygon', 'points': [[21.949795439410874, 0.8303230991288193], [21.419368101054296, 0.6538938833449262], [21.057347245331716, 0.8164719461431083], [21.026217098294165, 1.1116721090066843], [21.419366915993486, 1.1950013975755711], [21.846957575377008, 1.1116721090066843]]}, 'holes': []}], 'center': [0.0021729050000000028, -0.103527645, 0.691584125], 'construction_scale': 59.85776346842027, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
