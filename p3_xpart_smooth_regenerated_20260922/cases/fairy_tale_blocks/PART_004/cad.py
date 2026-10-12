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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.9997675808835929, -0.0, 0.021558854658087403], [-0.0001567328754511366, 0.9999735732001084, 0.007268310409798627], [-0.021558284926549463, -0.007270000096797405, 0.9997411602257947]], 'axis_xy': [0.28383496447169576, 0.07279985668890558], 'profile': [[0.8125701794800334, -49.97779011599206], [2.383315672024792, -49.97661895451408], [3.9722184493372383, -49.97826291295779], [5.561064888345121, -49.97974594204978], [7.149935193686333, -49.98240915382222], [8.73877579853798, -49.98381453852714], [10.327649849619878, -49.98370082130987], [11.916488523876161, -49.9841957434017], [13.505418507446041, -49.98507279837534], [15.062379698210453, -49.799219249860144], [15.994753442289472, -48.75502578491748], [16.07660135156585, -47.207609242091415], [16.05811597133611, -45.619555984700355], [16.052794468691427, -44.031237081767905], [16.052802803638336, -42.44286288672725], [16.05388826377692, -40.85438515551124], [16.049973971443066, -39.2659843873612], [16.051381374927644, -37.677629796479636], [16.05071801425091, -36.08932199179782], [16.05188032926509, -34.500491484859594], [16.049683954028595, -32.91087617570011], [16.045805122275553, -31.32110404596891], [16.04501016271637, -29.73132439229874], [16.049343331795136, -28.142332834584394], [16.05101206792212, -26.557489684371347], [16.05360438674903, -24.973488523616666], [16.064418617086154, -23.389409065927225], [16.068638247933524, -21.805251590732354], [16.073052915495502, -20.221115841000106], [16.08072058323718, -18.63697334311922], [16.101286787789462, -17.053018018496815], [16.122647333087144, -15.468925815337865], [16.127300513210958, -13.88423056812091], [16.12642273455793, -12.295633629922968], [16.12291645939066, -10.705321761809849], [16.133369487690302, -9.1149556373541], [16.141888860414166, -7.5246380281856196], [16.157825043543518, -5.934335034407864], [16.163797154685057, -4.344096028796825], [16.163941593090367, -2.7539480045388913], [16.15416735418305, -1.1637695091424909], [16.14340953420817, 0.42650846333738546], [16.141014753845766, 2.0168234161381617], [16.13348161555373, 3.6070538175187576], [16.13398380749326, 5.197321691421301], [16.133115901742393, 6.787597876107208], [16.134640095733683, 8.37760295269109], [16.239409136814658, 9.904921975425637], [17.266045270101415, 10.695465231878934], [18.83311403359228, 10.848888198067076], [20.196515291238903, 11.47222490637876], [20.803869206722666, 12.824835817186063], [20.757736398368344, 14.393250959872102], [20.552134349171418, 15.967726660131328], [20.322174316933648, 17.54048517714856], [20.040516700995454, 19.102405093358097], [19.514163945869704, 20.576920026464165], [18.496463031326037, 21.743803150313333], [17.25665623848993, 22.660786602652948], [16.493465647014865, 23.98520126968325], [15.852794438573284, 25.438326928368177], [15.232430651078014, 26.89941594078079], [14.617888774281308, 28.357565403684024], [13.994301094270691, 29.81857031092565], [13.363362852569388, 31.27443265032019], [12.740087403174151, 32.69100135581377], [12.108170631665626, 34.123232160944966], [11.476775343756582, 35.56658503290535], [10.855675333081805, 37.018343635942045], [10.228966557551999, 38.47917031958212], [9.603499825832825, 39.94810584743301], [8.991952515102481, 41.41671691198786], [8.385923620203087, 42.88051416117136], [7.790476267408836, 44.336734421402745], [7.112915055195069, 45.75225670583771], [6.232254500038039, 47.0563737031183], [5.11901798435807, 48.202795724595994], [3.8152235900267235, 49.12938726921794], [2.3504323807888623, 49.700565567600286], [0.810062547076362, 49.95242354631009]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.127491665, 0.10674071, 0.383428135], 'construction_scale': 115.61438519038921, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
