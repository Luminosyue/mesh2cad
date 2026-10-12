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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.9997714340023498, -0.02137942358636316], [0.9999520557553887, -0.00020935051060805228, -0.009789911283353776], [-0.0097921494357587, -0.02137839856604909, -0.9997235007161626]], 'axis_rank': 0, 'features': [{'z0': -36.58315334917275, 'z1': 36.79765100994931, 'outer': {'kind': 'spline', 'points': [[49.87772844613638, 2.9824927785476336], [49.18692739385499, 10.705695351519743], [46.67480840198933, 17.99661021982837], [43.50884181121721, 25.058140250670316], [38.97140514129275, 31.34556877574555], [33.5584691341524, 36.93035930596657], [27.323338517954127, 41.519742382770936], [20.609335797514653, 45.12580823148421], [13.2093884959484, 47.19400092015665], [5.6923253101210065, 48.87121131252587], [-2.087068722061498, 48.986067358306194], [-9.737415139495473, 47.822171143856686], [-16.952653603332738, 45.50950745881026], [-23.832870577587567, 41.941038928183765], [-30.032528037838084, 37.301294115835056], [-35.772122124311565, 32.07076721016171], [-40.47333387451871, 25.9072689543574], [-43.52501699295047, 18.829299176050483], [-46.34111965867403, 11.681059973109527], [-46.53927666410085, 3.912053289013686], [-46.61419877234243, -3.867517984559587], [-46.12091891237039, -11.613957427948803], [-43.57957730486276, -18.929005430027093], [-40.07309435223468, -25.87074588895967], [-35.53908225814711, -32.15898984079328], [-30.06752121209524, -37.68904626704377], [-23.75121941952346, -42.13682800625004], [-17.05867762382916, -45.73387491975831], [-9.417118816808905, -46.88875692235887], [-2.5433089329887753, -49.391180310598415], [5.2277703174207435, -49.3318535125189], [12.057716659164319, -47.204380768204835], [19.69914024162705, -46.02025170574543], [26.383429003185572, -42.3668732768829], [32.834238838153915, -38.141234054065094], [38.360057227478514, -32.6636892531116], [43.020169408970936, -26.442296348784197], [46.188315383366145, -19.436094566953546], [48.61080615322485, -12.459777637099872], [49.863627370470915, -4.794202201438843]]}, 'holes': [{'kind': 'spline', 'points': [[46.19268453572623, 1.5381781101776864], [45.83393845278366, 8.728328904824206], [43.63877106315914, 15.369398101180133], [40.694240241957246, 21.930388653515443], [36.88004879191598, 28.01487023704486], [31.8556810072664, 33.169259809424545], [26.435456821144765, 37.761531765236256], [20.16019141371038, 41.236968414672866], [13.283430001804383, 43.26208251823165], [6.6229656545355855, 45.729051506959856], [-0.5746943977099255, 45.70102711595332], [-7.533762527246283, 44.435038127608834], [-14.285427163650764, 42.180839562048945], [-20.750076620347503, 39.135088055097754], [-26.624289997792793, 35.12161260487162], [-31.987016361845757, 30.321524790222995], [-36.48821949883154, 24.717339840995702], [-39.806949167109664, 18.548768575750344], [-42.41676432810604, 12.328538075041608], [-43.491891521281616, 5.212376427335546], [-43.6894740083541, -1.9634046506875547], [-42.70157395533911, -9.091850151527861], [-40.583684540924104, -15.7934765134104], [-37.52248657864093, -22.30325734784932], [-33.89066208765686, -28.51850970256399], [-28.79579022842382, -33.6021639637962], [-23.440780787656124, -38.23376422208622], [-17.1375855028079, -41.589141811793944], [-10.351319794093984, -43.69815599999281], [-3.9204941564236764, -46.45561592541181], [3.2714350679705158, -46.45931047910064], [10.076678478917133, -45.00260036784576], [16.92791543183843, -42.8626653968275], [23.261037481747007, -39.7321086219457], [29.19159495616988, -35.950650611568406], [34.37974010474451, -30.96424872567161], [38.85666394299005, -25.416061999442643], [42.287964302819574, -19.102546480729128], [45.43811724448568, -12.754499379172573], [45.97360063535189, -5.653482254787955]]}]}], 'center': [0.08970941, 0.188297005, 0.8694657699999999], 'construction_scale': 407.66024584114194, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
