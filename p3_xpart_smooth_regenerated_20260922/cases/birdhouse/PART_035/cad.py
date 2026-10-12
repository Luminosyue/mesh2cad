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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.08642741180688263, -0.9962581505254365, 0.0], [0.0450291856082608, 0.003906373027755063, 0.9989780341395024], [-0.9952400087073572, -0.08633908594260484, 0.0451983108840936]], 'axis_rank': 0, 'features': [{'z0': -39.00331108058316, 'z1': 39.79124129413956, 'outer': {'kind': 'polygon', 'points': [[47.4121987604625, 22.74671141646261], [-36.27328832812565, 22.690174130746225], [-36.85749618680442, 22.575366162590246], [-37.54031380954483, 22.243403749106452], [-38.130435890452596, 21.63200558216403], [-38.43853635508886, 21.049015170903157], [-38.95849719160782, 19.387929901689734], [-39.56117942481349, 15.752710251412367], [-39.74233132214671, -3.70206538970554], [-39.731636894448684, -20.51651110850294], [-39.51813434435393, -23.024768888877887], [-38.843506299932685, -26.254891511182468], [-37.77921998897589, -28.47161259057587], [-37.077364406454286, -29.057399634637957], [-35.94272211333402, -29.508587153472654], [-32.24614349833979, -29.64860321162348], [42.92895395683495, -29.659223674124178], [46.06359212757724, -29.62063105898231], [47.21719850501309, -29.474081502845785], [48.31905259850559, -29.00705066863369], [48.78401976397821, -28.45546191395865], [49.36213996091797, -27.347672668832438], [49.83872868399924, -25.095683732713685], [50.01873343327737, -23.435301531902756], [50.04364753256123, -20.669477834641725], [50.18678394638667, 17.161450519329108], [49.805898678298036, 20.37310077494453], [49.48552132592205, 21.61318797875959], [49.07196602881593, 22.116587476809713], [47.98019229625094, 22.662361476210297]]}, 'holes': []}, {'z0': -39.00331108058316, 'z1': 39.79124129413956, 'outer': {'kind': 'polygon', 'points': [[-49.91743666713491, 28.291007980233427], [-50.07824134330562, 26.199389301409504], [-50.14604618393819, -22.512333118340823], [-49.881101980220066, -25.124799122888472], [-49.311862566257695, -25.699307405954784], [-48.76432848261998, -25.78210070613078], [-47.98477024304614, -24.589496210402967], [-47.765686195191314, -23.471792988650808], [-47.11102789022807, -21.770313346360396], [-46.45684169753238, -21.324714156453826], [-46.30362915820869, -20.67087688502486], [-45.920286709022626, -20.122055193146124], [-45.777062272802716, -19.6005923568809], [-45.615358288938744, -12.902558935066606], [-45.32365041995548, -12.324265062430966], [-45.09446241789163, -10.388575932971857], [-45.00223260178353, -4.4788346464586], [-44.817061342070005, -3.1002327789670527], [-44.95159517386287, -0.04599938606931028], [-44.818864212425325, 1.7218441602439019], [-44.50995774467455, 3.5102978006367267], [-44.567664325251, 5.2227724656007135], [-44.84426568489049, 6.444174107471485], [-44.91922250581056, 7.499057894191693], [-44.503256135148696, 10.790199351896652], [-44.518021030670496, 13.562756459306328], [-44.33278852683348, 16.667788129448702], [-44.56510736299346, 19.946997095328417], [-44.1852081716277, 21.614363265328805], [-44.71614777671904, 22.163189215829917], [-45.52974054450832, 22.71934587408716], [-45.523532173449404, 23.252827619799042], [-45.23947111527368, 24.023037626708117], [-44.66185796111636, 24.68211193892801], [-42.63167100880366, 25.12985154133708], [-41.30344350277135, 25.7333241152377], [-39.62442498971826, 26.844013314520822], [-39.070417138525414, 27.086102476821946], [-38.50292294661858, 27.157444711235982], [-33.78166704240136, 25.97579296322104], [-32.588596812062846, 25.861062605433258], [-24.330463063890857, 25.795229130112958], [-21.11431940260314, 25.9316689355831], [-11.777764885224512, 25.730315980048694], [-2.7095385169988098, 25.896846841102786], [20.032538383477604, 25.57271657770197], [28.163194152557026, 25.766851673681973], [36.34832257832432, 25.492326906232474], [41.08741811704415, 25.635071867584635], [42.87336542316135, 25.47754707346626], [44.10121152595582, 25.55309714142425], [47.392880502254485, 25.220435313964096], [48.44202294357033, 25.356114610625287], [48.903518100934114, 25.645602004469467], [49.151123588878825, 25.92072127318688], [49.361638592721874, 27.185355837172782], [49.00376145139963, 28.280394830172913], [47.99944494310684, 29.213573141977253], [46.89159200218634, 29.514003588944615], [44.10031621489764, 29.59941799595569], [-47.43432384306974, 29.63199783849684], [-48.551787304355834, 29.536076714210168], [-48.87280674202586, 29.37399609432032], [-49.643846616025954, 28.783868214250727]]}, 'holes': []}], 'center': [0.00018242500000004158, -0.0013169249999999688, 0.06052529499999998], 'construction_scale': 56.375856527549296, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
