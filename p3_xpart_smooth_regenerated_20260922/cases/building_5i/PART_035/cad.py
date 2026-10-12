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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999994002760851, 0.0, 0.0010951928916854564], [2.4270628674121456e-07, 0.9999999754443842, 0.00022161040582626082], [-0.0010951928647923205, 0.00022161053873140068, -0.9999993757204841]], 'axis_rank': 0, 'features': [{'z0': -1.3906255617440915, 'z1': 1.405555025288794, 'outer': {'kind': 'polygon', 'points': [[43.306370921154794, -49.985841203818744], [-49.0627920836964, -49.94934373897717], [-49.7093659377536, -49.651805123849186], [-49.941767927040175, -48.99018655391868], [-49.9765771192787, 48.69559578646999], [-49.753955184459, 49.42833247500397], [-49.33749006392905, 49.75005812234064], [-48.69222827047026, 49.9064908994989], [-42.26105572262319, 49.99271208031299], [48.32461285014731, 49.95099589390543], [49.31853522327912, 49.91285597642239], [49.77974971003025, 49.67674747629553], [49.923629152070085, 49.10948641103462], [49.959511112363785, 46.6032011542768], [49.95989012636532, -31.585609557421503], [49.92829276824622, -48.59370458507766], [49.8882785305524, -49.53729945266388], [49.72004174777202, -49.86766805083991], [49.342980617248024, -49.97716924755185]]}, 'holes': [{'kind': 'spline', 'points': [[46.180875092414375, -32.41746447664218], [45.87441763180022, -27.89200789687638], [44.33610740447661, -23.87197204296194], [45.24952117775212, -21.139757946306414], [45.27853763579877, -16.6562626254603], [45.00657414013507, -12.232012981986069], [44.93348999841981, -8.178491729811302], [43.92960178656759, -4.5673634383190675], [42.54209723774019, -1.3062236882334581], [43.04697597715641, 3.0202225193504306], [42.56880191686538, 7.412349949865655], [42.17779518531074, 11.91320155564038], [42.15332931995957, 16.426254931999267], [41.976365688799966, 20.95262676920087], [42.114404372251485, 25.40569177962317], [42.295793952735664, 29.83650731228179], [41.048868870802764, 34.17048886692286], [40.26811987459896, 38.52936171724419], [40.12586478254863, 33.98796544320846], [40.092908844619814, 29.405157010966366], [40.0916579572643, 24.822148313509675], [40.091478926083845, 20.239290255972527], [40.084787679800854, 15.656260694386322], [40.07847989926032, 11.073279126075155], [40.073061305675424, 6.4902622839193755], [40.07119929557557, 1.9073112917735235], [40.070633129946906, -2.675706646317759], [40.07154442133754, -7.258720600904647], [40.06655955699413, -11.841676749859898], [40.07015657711604, -16.4246920229669], [40.06871095473932, -21.007727131176292], [40.063641342498805, -25.590748039866313], [40.06932896562779, -30.173755507823227], [40.07370533243544, -34.75678559991823], [40.06949311212073, -39.3398171931199], [40.06623190169324, -43.92281320575591], [40.90229302100547, -47.09138810531033], [45.18036594086575, -45.647901131867414], [46.16090658734845, -41.472595173869514], [46.03483066052152, -36.940751345508694]]}, {'kind': 'polygon', 'points': [[-39.83397721318292, 30.100407602890456], [-39.80645319578644, -46.32376188943434], [-39.94223034093004, -48.0111581422963], [-40.42808773345618, -47.60210847573441], [-41.51240775368078, -47.283147180306514], [-42.255570707938624, -46.879465493782305], [-43.85483262128281, -45.584266136651756], [-44.352586754084165, -45.471029847563535], [-44.74595984969337, -45.61880191102065], [-45.114981124186514, -45.58205558929664], [-45.41997485551573, -45.24806689925134], [-45.70424221863953, -44.26867815136973], [-45.77139169337487, -42.515906474459825], [-46.151462148488505, -39.31192732133212], [-45.86488453147074, -35.84465369249666], [-46.09555153830066, -32.4001200983625], [-45.98159527822048, -26.853209171655568], [-45.662116079110376, -24.49847832464997], [-45.29040450041472, -22.933457319341258], [-45.53046064983812, -21.65162032763226], [-45.74635751020362, -19.05250176036353], [-45.60311733397872, -17.286964652833767], [-45.70215445387963, -14.588792905078792], [-45.55875033176355, -12.946679485481425], [-45.62701849816941, -12.626486043790612], [-45.26600650446137, -11.079484765655657], [-45.47277763614987, -8.947161611456632], [-45.35226365495328, -8.211137376199442], [-45.117605805029974, -7.768850130094334], [-44.93382830976513, -7.7235551982830595], [-45.093820398603796, -7.450266678543559], [-44.81273666337071, -7.677108732860961], [-44.60212275855975, -7.645229338465654], [-44.46474405034112, -8.054917862798352], [-44.22970760395221, -8.095228947005284], [-43.86452530304506, -8.053624871255753], [-43.62656955754755, -7.6058038653111195], [-43.305026687540156, -6.042623341289783], [-42.71981513280058, -4.370622470376053], [-42.63821873370969, -2.010882442747307], [-42.214955568173664, -1.0956207235221456], [-42.3487577262318, 0.12850681376402656], [-42.15878708740144, 1.4203493382393295], [-42.44485432893411, 3.3172551524968674], [-42.1617896470702, 4.97161113366045], [-42.124216443762464, 6.15592254972552], [-41.738587854607935, 8.174079442750651], [-41.831838686208435, 9.449463534473617], [-41.564797650974306, 11.16699647014684], [-41.67827420888575, 12.326145426115529], [-41.468262542405014, 13.791898783653172], [-41.681463550625885, 15.723438290461447], [-41.388964303577076, 16.964617119961957], [-41.36102094639447, 18.367055176741808], [-41.051553390885104, 20.030360265317842], [-41.10979774465938, 21.223302712695805], [-41.00307210566783, 22.36843225421427], [-40.694709617233904, 23.47374554829439], [-40.82979061959286, 24.470942763615923], [-40.66876924408567, 26.133065159498315], [-40.83197701870425, 27.60146851747102], [-40.425129370425985, 29.334533207409947], [-40.266698576874994, 33.503504422350105], [-39.94465470478719, 34.93676523126092]]}, {'kind': 'polygon', 'points': [[23.70381405996274, 47.468526662613925], [-19.65554139763201, 47.48853123130927], [-20.748452664197195, 47.45570653480474], [-21.291909033472734, 47.22473298421828], [-13.795038458742999, 46.70150238026934], [-7.563919192417161, 46.614200682292584], [0.045903965796864774, 47.060011140846974], [7.332646469670941, 47.00119539552398], [16.479900606305492, 47.141597671971866], [20.9199790547021, 47.22386651091312]]}, {'kind': 'polygon', 'points': [[28.75392452289705, 47.345517321710055], [26.295321014837082, 47.38658223290894], [25.290952152336576, 47.45601925521517], [29.3204786035135, 47.4658741967171]]}]}, {'z0': -1.3906255617440915, 'z1': 1.405555025288794, 'outer': {'kind': 'polygon', 'points': [[-44.359069633927895, -10.082779823465838], [-44.41734336614821, -10.418091198890261], [-44.111915557592305, -10.429770998795155], [-44.25818435103165, -10.177606974099971], [-44.06431996368002, -9.926209364174952], [-44.1640270023091, -9.872215145378803]]}, 'holes': []}, {'z0': -1.3906255617440915, 'z1': 1.405555025288794, 'outer': {'kind': 'polygon', 'points': [[43.45546543744429, -22.944723075292437], [43.45544691402253, -22.911825651709325], [43.44941246246072, -22.93346400076023]]}, 'holes': []}], 'center': [0.0008046250000000033, -0.06176341499999999, -0.0007087149999999987], 'construction_scale': 49.73767133564632, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
