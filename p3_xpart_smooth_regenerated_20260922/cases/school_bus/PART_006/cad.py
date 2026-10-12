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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0033000922035428797, -0.0, 0.9999945546808984], [0.0005738659532637478, 0.9999998353371271, -1.8938208707033589e-06], [-0.999994390018922, 0.000573869078164001, 0.003300091660140216]], 'axis_rank': 0, 'features': [{'z0': -18.344683951147207, 'z1': 18.341266474982937, 'outer': {'kind': 'spline', 'points': [[6.31563844083834, 9.072697862256106], [1.6747188628632927, 10.708716904721078], [-0.23557422764477381, 1.6383419040458778], [-0.9162205011540967, -7.625297773268782], [-1.0657993244348867, -16.797061446635386], [-9.80272535913322, -17.96609373405409], [-17.709685319239387, -14.789746048455008], [-18.917723962947285, -5.581842933916744], [-19.524215710514166, 3.684200238124442], [-18.14950213218024, 12.782398236893345], [-17.446043786210247, 22.002053655384557], [-18.055164016155924, 31.269098040481715], [-10.880277596549902, 34.76977566271031], [-1.6024413975612863, 34.47845385779281], [4.4132993145922335, 40.506749530104976], [-4.088070182597598, 42.12366649004071], [-13.375292651835714, 41.82500304931362], [-22.66566510672074, 41.661632241074415], [-31.94880457949809, 41.26256357102877], [-41.237927517303845, 41.02594653963786], [-49.67610848609227, 38.75301436490929], [-42.57008839408483, 35.182574702738464], [-33.278657580913716, 35.246174774758], [-26.66198261473543, 32.198961688768634], [-29.020631836447663, 23.214792603656583], [-31.167612261266726, 14.176826456975729], [-31.418660716132198, 4.934553200848447], [-30.599029739953245, -4.320908896705465], [-28.53857393611584, -13.34573180167771], [-31.991430400651367, -18.648245423697652], [-41.27727955540514, -18.966440107460905], [-46.911773394931586, -23.083103323586354], [-38.18674507890943, -24.390563572017502], [-28.895758179517397, -24.243890716687087], [-19.604781298240965, -24.102404491258085], [-10.313435265549689, -23.982128223180027], [-1.035105506697663, -23.745052144039747], [5.164253193981939, -18.10399503476311], [3.6739715248566487, -9.269352496351125], [5.471757002324006, -0.16086905742040436]]}, 'holes': []}, {'z0': -18.344683951147207, 'z1': 18.341266474982937, 'outer': {'kind': 'polygon', 'points': [[26.343118160084053, -10.416165366900024], [24.55694700105229, 3.548697597125066], [24.240418080386846, 8.004636917726597], [24.205071702190303, 10.531124359660163], [24.36084831152514, 13.074379828583464], [24.93501484339971, 17.51355112219527], [25.90267389288565, 24.28214717224452], [26.440109130725872, 27.040658094772823], [26.711523297202056, 31.478414086220358], [26.20526602455381, 33.80588810057291], [23.910922066860437, 35.58787314751879], [21.583440282890756, 36.729098809473605], [18.707671675043464, 38.46084084875547], [20.051649027422293, 40.7883243020629], [21.583449017394152, 41.341180116811174], [23.91093413521513, 41.960328516139555], [26.23841994148686, 41.696979849138984], [28.658821415188516, 40.7883243020629], [30.893394300506305, 38.88244526234513], [31.123726849049664, 38.46084084875547], [30.52629342167741, 33.80588810057291], [31.216770618792452, 31.478414086220358], [31.563436924960854, 29.15094243160652], [31.47624826036694, 26.82346133803781], [30.502096414009245, 19.841032215763985], [30.088363737465084, 15.186079467581429], [29.90014918707913, 10.531124359660163], [30.224886150562426, 5.658753610328322], [32.257963350814684, -5.761212618717473], [33.11438924302529, -12.52712843008386], [33.74638418148161, -14.853854611698189], [35.3267025251209, -17.39859212943512], [37.58611628153804, -19.726070863265118], [36.52965648178549, -22.053547237356387], [35.54825473482603, -22.84174796367223], [33.220768454211225, -24.074886567328562], [30.893274811585716, -24.2113096858855], [28.565791717322323, -22.515938796147324], [26.648586563264896, -19.72607086326512], [27.413428338263433, -17.39859212943512]]}, 'holes': []}], 'center': [-0.17706141, 0.359766185, -0.68326144], 'construction_scale': 235.97383333356927, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
