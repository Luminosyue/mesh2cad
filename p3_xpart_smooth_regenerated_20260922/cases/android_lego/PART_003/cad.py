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
                secs=feature['sections']; body=loft([wire(s['outer'],s['z']) for s in secs])
                for hi in range(len(secs[0]['holes'])):
                    tool=loft([wire(s['holes'][hi],s['z']) for s in secs])
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
        if spec['method']=='tracked_smooth_loft':
            if len(parts)>1:
                body=parts[0].fuse(*parts[1:]).clean()
            for track in spec.get('hole_tracks',[]):
                tool=loft([wire(s['outer'],s['z']) for s in track])
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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -0.9991256484945851, 0.04180835467074432], [0.9997965171784705, 0.0008433733159666729, 0.020154725481887254], [-0.02017236321803472, 0.04179984738877242, 0.998922343588567]], 'axis_xy': [-0.2091086358116847, -0.3638352359815699], 'profile': [[1.0432052748212635, -48.80354953288307], [3.0596355104908346, -48.79146391484232], [5.099112442180985, -48.73838612292096], [7.1386044664971795, -48.66579738222501], [9.177264958932923, -48.579608831263414], [11.21578626087607, -48.51905162069861], [13.254423122695071, -48.46615810150213], [15.292483821668787, -48.40217726923494], [17.329983220236752, -48.353694096511646], [19.36465320249411, -48.29345855735639], [21.40117207867999, -48.22339134490379], [23.440618733458894, -48.15071439853854], [25.479773767165106, -48.060242107887944], [27.515943298087837, -47.9376471398939], [29.54747396430819, -47.719020883336896], [31.565840181728817, -47.30060755378088], [33.53936117597606, -46.837114914873474], [35.30569842540659, -46.00437928596688], [36.67428849206348, -44.63557074528935], [37.37813719502931, -42.85539595296737], [37.43355788839454, -40.85960150101336], [37.43022787416325, -38.82792955771484], [37.35780475697845, -36.79530833614109], [37.28219450012065, -34.75396546192858], [37.257034660874524, -32.700422873290485], [37.24420919224929, -30.651289080526478], [37.24539138043646, -28.60283475451638], [37.25453276399834, -26.55448821884385], [37.253436006137264, -24.506276949774126], [37.243797514468994, -22.45801745890681], [37.23918792591243, -20.40958308889116], [37.23707789791756, -18.361582283269776], [37.22348359995088, -16.313775395539484], [37.245406409475216, -14.266900366368876], [37.28753450909596, -12.220038515847499], [37.318121764746664, -10.172675265491712], [37.34078655208469, -8.124804779384265], [37.38216439973232, -6.077531523254159], [37.37173100489922, -4.030276109418256], [37.342279657347916, -1.982260754828577], [37.36864236311095, 0.06790195650317252], [37.38773882355446, 2.1287660380697644], [37.37268903258369, 4.189001622326573], [37.351259425177716, 6.232106527633178], [37.3928251071304, 8.290693915538597], [37.43665731433504, 10.353692567289894], [37.430324615432504, 12.415210318478856], [37.45273806467631, 14.475820323063875], [37.446568363245206, 16.536471470800088], [37.47244726923782, 18.597138311541897], [37.54008600841827, 20.658037085386596], [37.59817304542396, 22.71904460086256], [37.6604144576967, 24.779950525098766], [37.69562927773906, 26.84055865846939], [37.65527431288092, 28.901145779613866], [37.602734227767726, 30.961962316587062], [37.605122568454135, 33.02152430056726], [37.66191693290925, 35.080148509968694], [37.73132337768908, 37.140038051264], [37.704601957943616, 39.188217794425455], [37.38068814820198, 41.16822672178428], [36.45578756499036, 42.882386015106654], [35.02242938612932, 44.24470878830766], [33.25989728827617, 45.130292807745434], [31.274169297299792, 45.539799061684626], [29.26364030642417, 45.81501178257125], [27.256572526206256, 46.19268058953156], [25.238259386917395, 46.43148272736393], [23.24587972302259, 46.64312496635058], [21.23243305103358, 46.66509559030997], [19.19541050694612, 47.01498289358716], [17.17062310380608, 47.457035144163214], [15.17265900430192, 47.82664781623689], [13.14694934451995, 48.03860334798382], [11.113040806090833, 48.157272602465184], [9.085647159433885, 48.31503786512212], [7.062876492740468, 48.513411235286085], [5.045128958823342, 48.65609415927584], [3.0305138414347397, 48.76377145778413], [1.0337760635853346, 48.808656036873955]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.320867885, 0.008711339999999998, -0.778483115], 'construction_scale': 239.96190748695784, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
