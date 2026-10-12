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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_xy': [0.0683329458474107, -0.03671118910916249], 'profile': [[1.0419018121688164, -43.83200488934126], [2.2259144184932484, -45.40800231031011], [3.060921570884502, -47.551353663901814], [4.86622687251173, -49.02049268348641], [7.146314771909315, -49.66715417299767], [9.469478776497887, -49.83104265025222], [11.79608503024444, -49.83346992503614], [14.122761686483956, -49.82988924293889], [16.449362657533925, -49.80643405634285], [18.775772776540563, -49.77123092212774], [21.102353586566963, -49.75715772545082], [23.432489016233664, -49.68500978487623], [25.684909125064102, -49.263962054438935], [27.636343121792706, -48.05111528771915], [28.900693166563833, -46.197525189661135], [29.380087226892666, -43.94084891538558], [29.525469142009605, -41.608244652339984], [29.582446399042492, -39.27171511875502], [29.631800721366844, -36.93418551412567], [29.63373414751283, -34.59678849332358], [29.783363319445648, -32.29221551491192], [30.66882871432062, -30.8155371784165], [32.78639301917003, -30.6960244696822], [35.09975647025186, -30.85319946794855], [37.43427257648339, -31.16260578207465], [39.7708718552795, -31.146215940557422], [42.01225048531101, -30.62261718137527], [43.9621673111511, -29.374184992850434], [45.55965136685519, -27.666990637006414], [46.770265679168816, -25.716547602562365], [47.453981422625716, -23.54284441746809], [47.71590852608204, -21.261561926528316], [47.79568673702231, -18.953424285414194], [47.89576441253328, -16.62927428076349], [47.91486926727901, -14.294813059812258], [47.83728079619412, -11.957743447530778], [47.864740901242875, -9.619455653948163], [47.93642251436806, -7.277040907809943], [47.84935897422329, -4.942247164979092], [47.66706139795267, -2.62168809305307], [47.36721362551677, -0.3697017870021444], [46.59001604003666, 1.8377512411960126], [45.367353218251466, 3.88402138175284], [43.721194728561514, 5.590788574716129], [41.67184237883305, 6.715566368915769], [39.39549027311229, 7.171423398066919], [37.05356724945366, 7.276962006258428], [34.70899290426117, 7.268436446334727], [32.3643213301335, 7.252102067509256], [30.01969568417684, 7.25787049880476], [27.67943388213011, 7.2444682606335356], [25.33995577841091, 7.218095547379502], [22.99526928226509, 7.194519936145355], [20.651678563589286, 7.192946484478122], [18.383690683328, 7.17476847767033], [16.738827157750606, 7.439567020622888], [15.46643098247727, 9.303268248935176], [15.301244210484501, 11.598035886406834], [15.089025365833606, 13.878980237912137], [14.969947176136458, 16.140570771606473], [15.099184211206037, 18.372579001040705], [15.125181938441607, 20.539600499156734], [15.1787703147971, 22.759798809803158], [15.150567134993624, 25.013166985747393], [15.064322686910323, 27.258244634365383], [15.175117119803472, 29.479506631519065], [15.273363504991678, 31.692275789526164], [15.354940972023726, 33.975575990227036], [15.194183843918, 36.211893230950956], [15.04131133324115, 38.38613551523915], [15.016293538614438, 40.56084540868765], [15.163730059564127, 42.72975651975414], [15.166919981154201, 44.9387829614586], [14.108567543725513, 46.783356421109104], [12.3665844816489, 48.3261242607727], [10.338065400405144, 49.27171935610234], [8.149860918997287, 49.63187952418501], [5.846581310781184, 49.77512680616131], [3.5088499356359537, 49.84641183405434], [1.1962863239411448, 49.88131571058152]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.783946645, 0.28465046, -0.56977883], 'construction_scale': 250.15428265382678, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
