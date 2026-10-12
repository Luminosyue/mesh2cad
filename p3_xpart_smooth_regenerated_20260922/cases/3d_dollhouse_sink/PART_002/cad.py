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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.023924401109544722, 0.0, -0.9997137705521264], [-0.0034824620912461243, 0.999993932737735, -8.33396741886852e-05], [0.9997077050264905, 0.003483459159838135, 0.023924255953928657]], 'axis_rank': 0, 'features': [{'z0': -43.48795666955859, 'z1': 44.24738263766207, 'outer': {'kind': 'polygon', 'points': [[-8.998396587228308, -5.933851645366429], [-9.042091179689068, 1.7522181888800794], [-8.733113337963637, 12.139044638920192], [-9.068128441219624, 13.842692921696859], [-9.40312355901008, 14.281531207483958], [-9.87826518259029, 14.578006999549187], [-11.248820010031386, 15.077600286994134], [-13.197046544720868, 15.526259194777458], [-18.143804080869693, 16.20293478519875], [-26.70822881626456, 16.726051866175652], [-35.50290677053367, 16.935612484355122], [-41.26257578779471, 16.784962827308085], [-46.06153244383999, 16.411501028574303], [-47.378390106600676, 16.108637301656188], [-48.25628400619196, 15.754474502975793], [-49.13349425735214, 15.155572212916384], [-49.42740812910128, 14.720368603428556], [-49.773595518245116, 13.842692921696859], [-49.89295364811573, 12.965016350122665], [-49.940497681328004, -5.845586518368852], [-49.9128081612451, -6.3438700041945735], [-49.60415755732355, -7.289126246655732], [-49.132232138345785, -7.92976107703957], [-48.25427937134649, -8.292428481085524], [-47.37634037828127, -8.479191325557446], [-43.80027508644671, -8.554126702113376], [-36.62179752844408, -8.370284672317625], [-35.088158109319544, -8.533171607180698], [-34.64643605191711, -8.788758645010184], [-34.32059219750092, -9.415738004704249], [-34.105133318460666, -11.706785943613673], [-34.12029992572771, -15.120639279306495], [-33.85536140662263, -15.998314071195695], [-33.328908060844235, -16.526920408079995], [-32.159502979676134, -16.84229825438981], [-30.04559146215619, -16.88361315498768], [-26.744466498421673, -16.77617832426568], [-24.998367040584785, -16.360089778143777], [-24.351300091596748, -15.559474895566094], [-24.09559210724773, -14.681800103676894], [-23.977257377391958, -9.416110234678284], [-23.74695120614113, -8.976902388444644], [-23.372005242272728, -8.611616758675492], [-22.794522264472576, -8.293236962603743], [-21.681379674510357, -8.13021384034261], [-12.907232502828673, -7.985477906072417], [-10.942603985556346, -7.840916181196582], [-10.072779225035578, -7.607945133924412], [-9.59395716466711, -7.25486274863003], [-9.249582992741853, -6.782709179824168]]}, 'holes': []}, {'z0': -43.48795666955859, 'z1': 44.24738263766207, 'outer': {'kind': 'polygon', 'points': [[26.291206320014705, 11.282630095352003], [26.73200699875878, 4.96338376397089], [27.173349786290583, -4.58851597120369], [27.454172417876904, -5.905034387934968], [27.683694253263425, -6.34094713973997], [28.1470196398418, -6.7239299767071445], [29.002803889747536, -6.968215249712984], [30.160553740837717, -7.050780082953018], [46.19925245986763, -6.689197187043113], [48.317066793696, -6.531583203195867], [48.805156919785574, -6.3828679911246935], [49.23371522219143, -5.966233474295777], [49.551124610828445, -5.0273560366757835], [49.67076384777622, -3.6371490128658728], [49.74503768428122, 12.087339778548472], [49.39567121269246, 14.281531207483956], [48.784550992476134, 15.190973682061932], [48.315224311605235, 15.570191684480768], [47.43726114423843, 16.03626381753248], [46.120341607732165, 16.464938808345853], [43.436115326085385, 16.706533213285816], [34.425529154832304, 16.68919896068924], [31.509410304027757, 16.511270433079584], [29.878788284321786, 16.27035170363826], [27.968765007550886, 15.643555060368666], [27.153170068730297, 15.18465226341093], [26.75628748850806, 14.760163822509142], [26.308662799043383, 13.403853746067265]]}, 'holes': []}], 'center': [0.0033570250000000135, -0.36270716999999997, -0.27592821], 'construction_scale': 88.9837099301905, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
