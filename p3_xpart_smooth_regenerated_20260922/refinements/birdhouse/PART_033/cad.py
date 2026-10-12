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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], 'axis_rank': 0, 'features': [{'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'spline', 'points': [[-6.329010215057537, -8.705607526500232], [-7.13617723874437, -7.635120121994025], [-8.368979769419697, -11.526971009821803], [-13.06906850731837, -11.520947894432098], [-17.76915855876974, -11.521428531811464], [-22.469220805572544, -11.537103576520755], [-27.169310665979786, -11.54409640553153], [-28.172122556942504, -7.667676108975537], [-28.16575700742136, -2.96804958077272], [-29.523122363551913, 0.4251050148792795], [-30.948439256345583, 1.4775055960046755], [-28.135530452816067, 3.588871038798636], [-24.230404328158684, 4.625976560845904], [-24.781488493522975, 6.865903724930476], [-25.72119766924179, 9.819458175974411], [-27.634554230538267, 11.34679115222714], [-30.505955787757138, 12.46868498830255], [-33.43263018318322, 10.600692923614227], [-33.452715297461474, 5.900669688775317], [-33.31039547423937, 1.2254210471342721], [-33.42019913325753, -3.4674180166819966], [-33.42138940150287, -8.167515340388174], [-33.407707912015596, -12.867575318987392], [-33.350166016107515, -17.567223541800622], [-33.388399585641785, -22.267149226711087], [-33.41044736806656, -26.96718491743284], [-33.428595149894214, -31.667219446695917], [-33.440117691156445, -36.36729154842695], [-31.555421956108532, -39.468791326444226], [-26.85533422358558, -39.45961522674411], [-22.15524380294072, -39.4532304708027], [-17.455148189075846, -39.45563851904311], [-12.755061423810764, -39.46372406811423], [-8.054978269354754, -39.47443211389168], [-6.6051596547641305, -36.73508136968915], [-6.495160805899486, -32.157274756502744], [-6.500639963348563, -27.45720590486801], [-6.498125034795197, -22.757124113544116], [-6.498531604500696, -18.05703250876366], [-6.500594433833271, -13.356969453547547]]}, 'holes': [{'kind': 'polygon', 'points': [[-21.288952988274914, -22.368767297304245], [-21.278226933240678, -20.981042402931585], [-21.73765427435324, -18.749843287524904], [-22.23760704192109, -17.47212029551764], [-22.273554142502974, -16.51738442070466], [-22.459789967132732, -15.675850561276254], [-23.353777343833006, -16.038594111790914], [-23.79354202652851, -15.830438099086917], [-25.140283542646877, -14.795318196702281], [-26.720402635256416, -14.498083763094956], [-27.372220591791297, -13.961259286459866], [-27.818686119720486, -12.955923584293496], [-27.964167576200115, -13.849153244856996], [-28.106187111997368, -17.182862156011048], [-28.16170861646537, -36.60936941307795], [-27.81910462225539, -36.869244662892484], [-10.905076323925169, -36.834414341660434], [-8.619560497257854, -36.75183257321216], [-8.026612823026916, -36.603975576005084], [-9.763787073033575, -36.1010165516118], [-11.277181660258405, -35.11242592886477], [-11.743343077951758, -34.99281538595167], [-12.637995442748876, -35.0977679536976], [-13.084924738536808, -34.97011993720641], [-14.35955509606613, -33.842800286137894], [-15.885856307426666, -33.063980725287514], [-16.17571463685582, -32.59561196285874], [-16.164144492423592, -32.15480291496461], [-15.563136379042554, -31.252922841850197], [-16.188460090025394, -30.613923496441988], [-16.64746682840383, -30.401347614405978], [-17.101520484418607, -30.41869072150617], [-17.599519243941565, -30.80369967727801], [-17.896419153072127, -31.251616834774172], [-17.376631010845376, -32.16066657670143], [-17.31705178361483, -32.59870714914092], [-17.795824474854612, -33.188202396027876], [-17.995436724619054, -33.33820624533526], [-18.435105476348216, -33.319630890829416], [-19.02065923691287, -33.04244407980364], [-19.506128322740903, -32.59405324154462], [-19.402277969513193, -32.13974457635107], [-18.545089145331275, -31.253731192426002], [-19.267617404874823, -30.652915724225608], [-20.22834986402574, -30.312208654176384], [-20.803934220941915, -29.92018856875695], [-21.202382440239543, -29.473027399754365], [-21.33711245141355, -29.025230211679318], [-21.44163744107186, -26.352013951192124], [-21.248659423664442, -25.438002837418143], [-21.599616230847406, -23.535114326482812]]}]}, {'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'polygon', 'points': [[-6.597120157195985, 1.6942610708202566], [-6.471262734559813, 2.4222764211411794], [-6.267357967038019, 9.810846777560627], [-6.23845188458606, 11.600224422535762], [-6.397052308056629, 12.03721242763394], [-6.834187913364068, 12.242161715005967], [-22.460809183526905, 12.297596144805471], [-23.027220147639483, 12.059269814542818], [-23.03044624077856, 5.364118008576581], [-23.205809207119398, 4.466605942738556], [-22.941132261030475, 4.0146269657765785], [-23.333713381551814, 2.681767990409938], [-23.382707443604204, 1.7597610318005816], [-22.907347794989807, 1.526813397306215], [-7.280084452876237, 1.3780760814587376], [-6.8361834581865715, 1.426061418599492]]}, 'holes': []}, {'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'polygon', 'points': [[-7.2831915956728315, 37.04161776004307], [-32.28363335809845, 36.97746943172922], [-32.8086274291614, 37.06025531466241], [-32.957996321169276, 37.881195051660136], [-32.72997216494189, 38.30193080796459], [-32.28363335809845, 38.36269471303312], [-6.8342140875365756, 38.367030504247616], [-6.388648082461031, 38.28390754555837], [-6.1834360319263775, 37.95227932779388], [-6.1515734436348035, 37.50675263403565], [-6.53037698349335, 37.06040297070251], [-6.697870311433903, 36.61478550022871], [-6.515043437384112, 32.452145241118906], [-6.52202180661972, 19.942337335680076], [-6.611752738236781, 16.70493892695951], [-6.836311472424969, 15.254715405090378], [-7.034305160522047, 19.753149939729084], [-7.06085907585503, 32.56365108960774], [-6.9205288205623585, 36.61563851023625]]}, 'holes': []}, {'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'polygon', 'points': [[-22.289410263501335, 33.731365176194295], [-22.27240728257636, 28.618008404249018], [-22.01622391668408, 26.575570455721962], [-21.805059727078095, 28.2030437123186], [-21.706166118611307, 31.21592606851487], [-21.54251214071791, 32.607472182529094], [-22.014852445431114, 34.70393118828536]]}, 'holes': []}, {'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'polygon', 'points': [[-24.700671381562447, 10.361406296027223], [-24.20143316069842, 9.774205847598195], [-24.687197434707997, 9.584952887445736], [-25.315500505793597, 9.818658495673326]]}, 'holes': []}, {'z0': -19.004200365217592, 'z1': 19.005145367254794, 'outer': {'kind': 'polygon', 'points': [[-24.10997115880901, 12.064284175836363], [-24.693269861070817, 11.967355776686684], [-24.941264182700067, 12.059054712172824], [-24.693269861070817, 12.087937246820717]]}, 'holes': []}], 'center': [-6.22150000000321e-05, -0.521851465, -0.006854235000000042], 'construction_scale': 45.26809174029661, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
