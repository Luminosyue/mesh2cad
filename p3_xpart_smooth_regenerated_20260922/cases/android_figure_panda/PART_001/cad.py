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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -1.0, 0.0], [1.0, 0.0, -0.0], [0.0, 0.0, 1.0]], 'axis_xy': [0.02265590526107765, -0.1096218226446872], 'profile': [[1.1419168364818644, -42.09988213432871], [3.3493959722963433, -42.102374188339496], [5.582213821913275, -42.11676308484245], [7.814979082602816, -42.146586263000074], [10.047523254436697, -42.17954783048121], [12.278491173218116, -42.230854634448406], [14.5086341327507, -42.28670330439644], [16.73804891154977, -42.34315645336373], [18.9664504726628, -42.4015920826986], [21.195161299702626, -42.46285975099047], [23.42583842827096, -42.52984060842929], [25.65652673319005, -42.58876747088601], [27.88602544854646, -42.66344018182741], [30.1155454864563, -42.725060721821635], [32.34641255483066, -42.80143779883823], [34.57838896851057, -42.87703259967368], [36.810241072785786, -42.90664203908728], [39.036875914498275, -42.82105125650463], [41.21953989852824, -42.474399778860565], [43.26941311006185, -41.723039060373196], [45.131063353340714, -40.47389647415994], [46.73671665843061, -38.88822923693976], [47.983692675072575, -37.034371791480574], [48.77530265580327, -34.965161182977056], [49.210178648780854, -32.779101372032684], [49.373893604659145, -30.555883137578967], [49.420416108638534, -28.32474808636099], [49.43566705135227, -26.092853301625244], [49.44021154087275, -23.860852056101855], [49.43447635379015, -21.628832796327487], [49.43088834695456, -19.394373746661536], [49.398446101973605, -17.155811176696357], [49.41005699255433, -14.91695247645389], [49.43331704740683, -12.677995653559266], [49.459944507031736, -10.43906930440022], [49.47915396201756, -8.19987423406113], [49.499017126637376, -5.960643501460185], [49.53085703438491, -3.722807202163653], [49.53161941237945, -1.4887310760156298], [49.53641242880751, 0.7444723994000153], [49.55245599505582, 2.977998490449627], [49.566064864286375, 5.21243171657442], [49.581338279854336, 7.447143391891255], [49.60549773888222, 9.681933296756727], [49.62824521338038, 11.917628928391188], [49.65012350636539, 14.154740396911068], [49.6727957387217, 16.387401682167013], [49.70454352236757, 18.619405311148803], [49.73067309875396, 20.850973957659953], [49.733382476909725, 23.08230935385022], [49.74205421930834, 25.312534984945145], [49.75487155120197, 27.540159602209396], [49.743607797625664, 29.76761549839312], [49.650167385981035, 31.993710522602697], [49.59230273493659, 34.22071470718546], [49.54509997332748, 36.44941801867202], [49.47975252862537, 38.67607917794538], [49.16965128479564, 40.850795914622054], [47.85016358296758, 42.471586456371995], [45.751656401624984, 42.936066567223946], [43.532106996887265, 42.878708329287576], [41.302666095269814, 42.86150433196788], [39.07260133361561, 42.923040543559075], [36.840978868600374, 42.984774613772906], [34.60847911954147, 43.03650184269321], [32.375681734968595, 43.06770415364479], [30.142845646584302, 43.090054824355875], [27.91001251853522, 43.09960677468524], [25.677145443323624, 43.09981253384452], [23.444279853794185, 43.11247985991646], [21.21138775060828, 43.12968060884144], [18.97846491345701, 43.15836912581415], [16.74553986691012, 43.18163864424372], [14.512629757080951, 43.20877938869405], [12.279730571487509, 43.224861722550976], [10.046842189144595, 43.24802517950869], [7.813959987979803, 43.25826015489486], [5.581271112046417, 43.260781584339625], [3.3490130820386006, 43.22405688084258], [1.1418982902856274, 43.19336989869174]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.010696054999999982, -0.00041210999999996556, -0.09977275500000002], 'construction_scale': 81.48487608105985, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
