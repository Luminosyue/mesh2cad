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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.023845827346012313, -0.0, 0.9997156478310141], [-0.004134222692295512, 0.9999914492026438, 9.861200106683635e-05], [-0.9997070994650957, -0.004135398601857571, 0.023845623445174886]], 'axis_rank': 1, 'features': [{'z0': -26.03581198069086, 'z1': 25.97477046360998, 'outer': {'kind': 'polygon', 'points': [[-31.78238061679012, -39.45568198793134], [-31.800347059989686, -5.6521280271048076], [-31.72696826438457, 7.184334959340769], [-31.504088754008347, 14.952802363111982], [-31.077786152346878, 20.131782382548966], [-30.264044073154206, 25.310765027370213], [-29.522279884869985, 27.900255037088698], [-28.588635710936796, 30.48974504680719], [-27.300317166562017, 33.07923505652568], [-25.65162845947953, 35.668727691628426], [-23.6378466464912, 38.25821770134692], [-21.209903714512112, 40.84770508568114], [-18.481771133843324, 43.219102499349354], [-15.891735800930132, 44.986306159843366], [-13.91424285405686, 46.026687730502395], [-10.711574461455797, 47.521606383833564], [-8.121467594326756, 48.48373602169746], [-5.531343000421185, 49.23953075634301], [-2.9411689130115883, 49.60005936969189], [2.239213942075763, 49.889663104516174], [4.829431760303675, 49.70036177789054], [7.41967791549289, 49.30365346273397], [10.009946962963973, 48.64824302259537], [12.60024235537999, 47.752374102661186], [15.190577635329046, 46.42550741067939], [17.78094712121821, 44.751865344496075], [21.032096416544203, 41.955143958605625], [22.65624652134101, 40.330938959328705], [24.428569118271426, 38.25821770134692], [26.29022651139326, 35.668727691628426], [27.824209398107662, 33.079235056525675], [28.958446400414672, 30.48974504680719], [29.81527012241124, 27.900255037088698], [31.00022416640333, 22.721275017651717], [31.381636307527025, 20.131782382548966], [31.695972160720746, 13.629375290613147], [31.730299878790717, -8.352612975122964], [31.059947330215753, -33.15972259350637], [31.092857620739476, -44.60547573656609], [30.034794937009465, -47.19496049551606], [28.150990828748935, -48.781304589968066], [25.560872362687576, -49.62584575984813], [22.970685515005787, -49.80376609813458], [11.114981264437954, -49.831489317520095], [-26.243232487097284, -49.53443863205228], [-28.833499703811178, -48.84434187622152], [-30.64739102422723, -47.194960495516064], [-31.573200576703215, -44.60547573656609]]}, 'holes': [{'kind': 'polygon', 'points': [[5.771898030131558, -41.51196946567241], [-10.702800973021889, -41.42287885682638], [-13.29303751080632, -41.150293688297666], [-13.728438462414887, -40.86328579406945], [-15.883418418488603, -39.33423582120161], [-17.578597469011413, -36.837005707410626], [-18.099968536726905, -34.2475104469236], [-18.15616966498111, -26.479043043152394], [-17.736535017449032, -10.942097734072924], [-17.45649438148621, 12.363314978777751], [-17.192960171908616, 17.542292372830474], [-16.55313143127865, 22.72127501765172], [-15.838128704180916, 25.310765027370213], [-14.787315332234188, 27.900255037088698], [-13.414622276596166, 30.48974504680719], [-10.710194950203334, 33.5363006347845], [-8.12018286225104, 35.45928924575474], [-5.530063045788782, 36.263517079665775], [-2.9398677388279237, 36.4089246407517], [4.8307502260402, 36.33392753385075], [7.420979091748612, 36.1124977275359], [10.0112696452805, 35.239061638628456], [12.601684616969086, 33.130913598006366], [14.901436299533746, 30.48974504680719], [16.31271892658333, 27.900255037088698], [17.13380854249083, 25.31076502737021], [17.558635538246406, 22.721275017651717], [18.12264455030033, 13.954388644512363], [18.49005335413026, -8.352612975122963], [18.452741766721164, -23.88954778266537], [18.173076963231228, -36.837005707410626], [17.947892978388833, -39.426493091744845], [17.78927397904263, -39.66473683652914], [15.19921107635105, -41.099195373447486], [13.731158692216935, -41.227140571430965]]}]}], 'center': [0.298158825, -0.25422083, -0.30444113500000003], 'construction_scale': 262.53618142384295, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
