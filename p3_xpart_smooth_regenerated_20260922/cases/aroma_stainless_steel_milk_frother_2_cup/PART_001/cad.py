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
    from OCP.Approx import Approx_ChordLength
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
    fit=GeomAPI_PointsToBSplineSurface();fit.Interpolate(arr,Approx_ChordLength,True)
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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -0.9999772939847211, -0.006738806644678779], [0.9999961094714774, -1.879757700638005e-05, 0.0027893885637974626], [-0.0027894519011349493, -0.006738780427159322, 0.9999734035445372]], 'axis_xy': [-0.04720975519241231, 0.0268184342866273], 'profile': [[1.037999378031599, -47.625361182546655], [3.0445345489387616, -47.625226562719256], [5.074099287903504, -47.629391578737966], [7.102969256321771, -47.659339347986126], [9.126793652738295, -47.745567940050066], [11.148786867893968, -47.868377151314476], [13.152434094072966, -48.12536362567139], [15.156533878335786, -48.32606359464095], [17.15367759121385, -48.57979178017662], [19.12007880762802, -48.595656473350346], [21.119247665426094, -48.59128811661939], [23.1258641531448, -48.675801971475494], [25.09258297151958, -48.81816777458566], [26.99953752393988, -48.61453723638412], [28.790838567305784, -48.20264189936596], [30.473794354212906, -48.08973978672227], [31.09690554481761, -46.45866460682429], [30.28355648818472, -44.79624758976344], [29.789386248413578, -42.89640411993725], [29.63260467616133, -40.87681014945173], [29.535546583321263, -38.854014557247716], [29.44622779734894, -36.829414906747346], [29.3569242247638, -34.80241879600559], [29.26533589055822, -32.77487720374898], [29.168764854808146, -30.747339089820944], [29.080150188197052, -28.719393727578147], [28.997593655918486, -26.691112105934614], [28.899477064205847, -24.662734999594402], [28.87749444059002, -22.634447439931265], [28.81634800995857, -20.60591773324709], [28.79423305888632, -18.57699634817677], [28.79574220429781, -16.548005412425702], [28.801709645330483, -14.521317627601247], [28.838871246475506, -12.496260759011019], [28.85374895542006, -10.472282283062125], [28.73512946944079, -8.456809776132456], [28.71232784721934, -6.4600816275699176], [28.802878819150095, -4.443444075997698], [28.847574116007053, -2.4222511991801436], [28.833969537811896, -0.4008596810645255], [28.819064915596375, 1.6212625974062247], [28.828969581940644, 3.6467799762388626], [28.851459914576477, 5.673202386287991], [28.874834515778815, 7.699645744126894], [28.89569770943831, 9.726131993303877], [28.90942655677588, 11.752506623121452], [28.914558317094347, 13.778701397289524], [28.920689664949272, 15.804946788765655], [28.939992985018925, 17.831012367128395], [28.964542948567797, 19.857168105558156], [28.986746913311748, 21.88340542979934], [28.998544415879696, 23.91119023286234], [29.012522829521487, 25.940954869986026], [29.035477154591714, 27.96768423924971], [29.056847865316218, 29.994025941310007], [29.068679687687982, 32.02052404092778], [29.077526198774123, 34.046935767286264], [29.08912569642025, 36.07316011053942], [29.10956521319889, 38.099389847658664], [29.12700683183943, 40.12567228425162], [29.141217297345328, 42.151849088406735], [29.18413706715016, 44.17583549947892], [29.633524438831223, 46.08063778863292], [30.738655975007276, 47.658556323731354], [30.38898127882207, 49.04342144204996], [28.72034262180996, 48.64415997427528], [26.9875373132468, 47.62580180553633], [25.175505690942742, 46.756970658289234], [23.27342377537243, 46.0802397925211], [21.290232249832734, 45.67238993992526], [19.272283947453367, 45.472712380700116], [17.245233157555077, 45.339104355822904], [15.218643151145818, 45.28150921232516], [13.19092064730576, 45.244256064417954], [11.16192317810625, 45.196116948416275], [9.132923087852596, 45.157099076593056], [7.103818519516879, 45.13790537510602], [5.074334261455014, 45.11359056596177], [3.044628224353075, 45.095376326138734], [1.0380074341629129, 45.09547496616413]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.30483876, -0.41565362499999997, -0.0024865949999999803], 'construction_scale': 53.367151029597764, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
