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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[-0.9999727186783984, 0.0, 0.007386602665149423], [3.389742378280433e-05, 0.9999894702951042, 0.004588915981119576], [-0.007386524886403176, 0.004589041176227748, -0.9999621892607667]], 'axis_xy': [-0.1819566022184794, -0.09948956141972837], 'profile': [[0.6618424790943057, -48.898376549348605], [1.6266339901970734, -48.020784491102205], [1.9837634850386197, -46.62871422577324], [2.140340507935979, -45.18135219628924], [2.2176089575037286, -43.72747066026912], [2.2714532396779568, -42.27322456064523], [2.3045500003602974, -40.81768198125161], [2.315973815003648, -39.36162911267877], [2.3192669271305655, -37.90553592039774], [2.3244183169886594, -36.44952964612101], [2.338803456071087, -34.993527130090754], [2.3585285505440137, -33.537569686783826], [2.3827286553594846, -32.08178788738744], [2.4051308136675056, -30.626172183488663], [2.431989896370017, -29.170401851068394], [2.450300127519204, -27.71457999296917], [2.4698173009419557, -26.259091533998756], [2.497770046061612, -24.80391047345087], [2.542088656597202, -23.345892634381904], [2.591731712841201, -21.8854742597837], [2.64624891697974, -20.424680198197578], [2.6807925525332044, -18.963768092117178], [2.7226628755036533, -17.503119578771855], [2.775551457588028, -16.042927635086222], [2.8067954728052573, -14.582757590599076], [2.8276938823421744, -13.122447030488878], [2.862678470430744, -11.661725302460145], [2.909719137974232, -10.201036709815812], [2.940980791421996, -8.740100016294626], [2.9514591837524238, -7.279070231918318], [2.9647133249391064, -5.81830066571099], [2.993278968871182, -4.3579706074561155], [3.0187699622602904, -2.897623723574246], [3.047166067692288, -1.437206902867223], [3.049994503374545, 0.020227405507751522], [3.254466588122132, 1.3639957615442277], [4.128061590768336, 2.419609844648969], [4.98278938059943, 3.5913528697322183], [5.608977212952972, 4.908112390450958], [6.191055468033924, 6.254412057511981], [6.7772870907295335, 7.603271643316944], [7.34775397049836, 8.952301909614146], [7.895802433503572, 10.301734847293158], [8.45590562180699, 11.650960809260383], [9.040799506107053, 12.981785397234976], [9.621677012706083, 14.211409375738423], [10.17457800586385, 15.504371673581858], [10.753228445354775, 16.862545625496804], [11.352869546911807, 18.233990602160745], [11.98629333926625, 19.572078305768944], [12.873468794815045, 20.660690058339895], [13.801069580313273, 21.766997117951064], [14.249666293858871, 23.141752631099514], [14.472327186989098, 24.58775922278032], [14.653164185398904, 26.03624541904411], [14.520083980949153, 27.439422692887277], [13.555533851067691, 28.29560078319642], [12.164459826465624, 28.48204318481528], [11.385977571783211, 29.300431155737932], [11.323747158379847, 30.74154075592446], [11.313690572462956, 32.20365369064516], [11.322573834962373, 33.66512398641833], [11.340176189617708, 35.12438571196231], [11.360585543730142, 36.58323131080717], [11.3746334632071, 38.04211134563438], [11.370994745028465, 39.50104989628464], [11.369183048234786, 40.95987934223133], [11.355385319901295, 42.41870573425366], [11.337893869721345, 43.88033298866493], [11.32369232474462, 45.343367603833514], [11.314342769961929, 46.80173347565492], [11.286366251088573, 48.254937962585906], [10.791771681833684, 49.50107190026484], [9.484558164488552, 49.92554112688369], [8.027900103661455, 49.92520169806505], [6.568316192474567, 49.92067796173232], [5.108709841589079, 49.91879073475297], [3.649075313902431, 49.91657793921189], [2.18942839743312, 49.91353113330982], [0.7464359086058059, 49.91527728222971]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.647262425, -0.595396815, -0.22884773], 'construction_scale': 81.40818047034358, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
