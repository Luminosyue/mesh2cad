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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_xy': [-0.0948126798904772, 0.09992280368458975], 'profile': [[1.047921624494477, -43.98768410096703], [3.073850711867963, -43.985687530006935], [5.1231670654887544, -43.98819407801882], [7.172494084385967, -43.99488017865865], [9.221772950375806, -44.00174774623076], [11.271003252729882, -44.00315563876457], [13.320322082803951, -44.00761239671243], [15.369686489611531, -44.01322264505898], [17.41903100215149, -44.01645305023416], [19.46838178843493, -44.015778768474675], [21.51765724829439, -44.01810467217861], [23.566941478907903, -44.02496353961167], [25.616291294334594, -44.02997188481631], [27.665604183987845, -44.03114687039523], [29.71491413484876, -44.03860493960585], [31.764152052169813, -44.04111707569972], [33.81342529994512, -44.04791061047912], [35.86270667089424, -44.05437637936693], [37.911879620733544, -44.0349146735357], [39.957550269411854, -43.96097531002637], [41.97373153672331, -43.65374326851782], [43.90466413327163, -43.00036513550182], [45.691711941343826, -42.0303486594454], [47.23741454437791, -40.68125167321453], [48.39259319363599, -38.963976410357276], [49.16361062036278, -37.082431567544205], [49.62885214813228, -35.088146464333455], [49.779189566242124, -33.046352293887225], [49.73134929886641, -31.001267650576786], [49.58491060439047, -28.96123905648247], [49.42333730815786, -26.92442702711392], [49.226094618821676, -24.890878336399922], [49.03234695918941, -22.85585405207771], [48.85971416983244, -20.821682107342937], [48.65975634274342, -18.78895371483415], [48.457203554056505, -16.756998337024783], [48.22617706968447, -14.725897571526469], [47.98035807572204, -12.696044123876817], [47.72331169660873, -10.664932718863088], [47.45778697548394, -8.633450129734074], [47.16085993356916, -6.600196234136463], [46.848030440582555, -4.565710033896261], [46.5453631963117, -2.5345938235072234], [46.22539737760586, -0.5048596787382413], [45.902373357256096, 1.5195402072730393], [45.589473364563894, 3.5437303354726772], [45.25574181684685, 5.564823354262707], [44.91141557995586, 7.585431301663851], [44.55497596850739, 9.60338925591329], [44.18719305510233, 11.620927805718637], [43.807462976869374, 13.633752976795348], [43.392610899750935, 15.637078849564121], [42.908456667170405, 17.62009892710206], [42.38644068965169, 19.596605520071464], [41.82059309801495, 21.568589804351262], [41.17277253365596, 23.51680457410378], [40.39473454862653, 25.3941518493317], [39.455348243029164, 27.212300827021018], [38.402369503690565, 28.97457689361196], [37.24012627619175, 30.6724650392666], [35.9866048513647, 32.295077242289835], [34.62067795576189, 33.82346701867827], [33.16304748652596, 35.26671023540237], [31.62639549890928, 36.62053048910533], [30.025968388431885, 37.91257137982228], [28.344996969568435, 39.11205703950968], [26.597463085121028, 40.20404951286578], [24.808095443686277, 41.20282529348504], [23.010608849628674, 42.18914203703298], [21.204098128498828, 43.1351467932899], [19.305710411907565, 43.59244871437271], [17.372801610215234, 43.24564068226089], [15.362857130302814, 43.14629781420419], [13.319862004730076, 43.20263829043968], [11.270910848348045, 43.20019294773065], [9.221556686483293, 43.167028315456044], [7.172347626459285, 43.15020436390884], [5.123223742488294, 43.1512020961531], [3.074057883138593, 43.154562213098785], [1.0480558450508295, 43.15898233335974]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.55546284, 0.010639645000000003, -0.63563058], 'construction_scale': 361.8840552437723, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
