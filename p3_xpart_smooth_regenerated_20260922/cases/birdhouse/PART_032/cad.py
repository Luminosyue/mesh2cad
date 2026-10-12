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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_rank': 0, 'features': [{'z0': -44.1956651104314, 'z1': 44.19607322244575, 'outer': {'kind': 'polygon', 'points': [[28.695042339251813, -49.77474825065383], [26.280669191831482, -49.89136257104415], [25.116315998559216, -49.563234663220776], [22.71268818324888, -49.5635885246237], [20.962451641363824, -49.393090465585495], [15.457773874196283, -48.5737868483429], [14.493604896737425, -48.28018499781765], [14.170950373845425, -47.76551189670547], [14.044747059508158, -45.24115605430975], [14.0631373791706, 38.17782243227512], [14.101022431473872, 38.98869717151831], [14.284728476496403, 39.576129736478855], [14.480426517719074, 39.779248408912586], [16.005331724999262, 40.136011466526924], [15.587912201641627, 40.746142693944684], [15.490179382649009, 43.75471922414665], [14.86171743987056, 45.449036055600956], [14.842673856214795, 46.18389746774376], [15.03858983159898, 47.235399348077884], [14.602353609755935, 48.17513098690622], [14.484757449870703, 48.216049337146366], [14.268947619729913, 48.968409622683254], [14.400555360025635, 49.65704590187297], [15.115790952013311, 49.921115034122224], [24.066639787847237, 49.842662102827006], [25.09657997077262, 49.807743267277964], [25.69536535147578, 49.638734774549896], [26.08581485096454, 49.026214438778304], [26.18817631578473, 48.031591506901314], [26.258437030222918, 40.14482017923257], [26.86860345444122, 39.830428116821224], [29.230372682702367, 39.81924161399557], [29.672440215304125, 39.57386157920339], [29.906631244890015, 38.97653910299963], [29.918706147851807, -48.37707962033678], [29.81019119216863, -48.94983259310108], [29.440771321944126, -49.535255808663784]]}, 'holes': []}, {'z0': -44.1956651104314, 'z1': 44.19607322244575, 'outer': {'kind': 'spline', 'points': [[4.57697705378607, -33.50386428753519], [3.4796087258259374, -29.903111565877357], [1.565627297916277, -26.71901690465586], [0.3717104687813001, -23.16249142109439], [-1.095643894759537, -26.56713366667671], [-2.362315959610875, -27.54979954338058], [-2.540858815473887, -23.62615474496249], [-2.5715396113595785, -19.675285143194277], [-3.0389864133578643, -15.885115130276796], [-3.9615887124106295, -12.343264057478606], [-4.8846811967484935, -8.879799486711551], [-6.6012364705023385, -5.715862941840669], [-8.414471725984344, -3.5414414982746902], [-11.910849910322556, -2.2400949821057674], [-15.134573375243496, -2.9052074762085827], [-15.913476488488582, -6.607788521810898], [-18.711623502365157, -9.382646632924766], [-22.131853861911427, -10.946292547504699], [-25.236760250550997, -12.297607068932727], [-27.19168272621371, -15.473243207189348], [-28.826090106857905, -18.876173245584308], [-28.367869646738164, -22.546112156846508], [-28.806640272759527, -26.387335216289536], [-29.440206453489065, -30.14115642923935], [-29.635141788904605, -33.965576652057784], [-29.48208754458689, -37.89572176246829], [-29.58287427116476, -41.84946136257044], [-29.38064203157098, -45.84256180790132], [-28.089737486075972, -49.54574016427493], [-24.113186908721122, -49.73507077969505], [-20.10748525873888, -49.73620082935615], [-16.101783825457453, -49.733716318827355], [-12.096083024458803, -49.73031411567282], [-8.090380973472383, -49.73044112323562], [-4.084678965432376, -49.73177148428642], [-0.07897759313367203, -49.733875648918435], [3.6413558508423596, -48.971189194925294], [4.472324790563044, -45.24686733996782], [4.339608684252621, -41.41781666540137], [4.524051555232339, -37.47311288939521]]}, 'holes': []}, {'z0': -44.1956651104314, 'z1': 44.19607322244575, 'outer': {'kind': 'polygon', 'points': [[-0.818940125780884, -17.68480036132372], [-0.8306828685247488, -18.891282184828313], [-0.3407655700722222, -19.288326071336996], [0.35338373827675235, -19.559941874335845], [0.9199685983138076, -19.079296294205065], [0.9932111387442436, -18.25921721278165], [0.8944000021765447, -17.674258089213954], [0.31240392840188247, -17.501728230777402]]}, 'holes': []}], 'center': [-0.0005900100000000297, -0.49780905000000003, 0.058426630000000035], 'construction_scale': 59.830058939907325, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
