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
    return partition_periodic_faces(body)

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
            elif spec['method']=='smooth_loft':
                secs=feature['sections']; body=loft([wire(s['outer'],s['z']) for s in secs])
                for hi in range(len(secs[0]['holes'])):
                    tool=loft([wire(s['holes'][hi],s['z']) for s in secs])
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
    # Local basis columns -> normalized source axes. Rigid transforms preserve analytic surfaces.
    from OCP.gp import gp_Trsf
    b=spec['basis'];t=gp_Trsf()
    t.SetValues(b[0][0],b[1][0],b[2][0],0,b[0][1],b[1][1],b[2][1],0,b[0][2],b[1][2],b[2][2],0)
    return body.located(cq.Location(t))

def build_model(spec):
    return build_normalized(spec).scale(1/spec['construction_scale']).translate(tuple(spec['center']))

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], 'axis_rank': 0, 'features': [{'z0': -50.005087991069196, 'z1': 50.0, 'outer': {'kind': 'polygon', 'points': [[-25.501947616838066, 12.803491127487952], [-25.54527322616176, -12.244504935298874], [-26.39586614755266, -15.217685827373302], [-26.383942378373096, -16.127951018366133], [-25.742034061198368, -17.92817825437019], [-25.56153708690822, -18.824757175129637], [-25.497226078660727, -20.805105008827987], [-25.522544831085032, -35.10042134961454], [-25.68058295280474, -42.88230254734682], [-25.805957510830154, -44.139972063833895], [-26.40770979035554, -45.95170148187818], [-26.962699860154363, -46.85680044012158], [-27.863063373191974, -47.52907829256489], [-28.76672816306747, -47.86854338384319], [-29.67079244617133, -48.0170341642961], [-41.420956979019834, -48.01377940012392], [-42.66894566832379, -47.86696782204827], [-44.14643789338697, -47.411064179882025], [-44.986396883060486, -46.80377635527457], [-45.617118484384186, -45.95526697241734], [-45.95174726731625, -45.05252315588265], [-46.11747091318606, -43.23515374320684], [-46.091958574128185, -19.744374263574713], [-45.745154032825944, -18.15465857043403], [-44.97875616596603, -16.119430909604187], [-45.08493591982321, -15.21956715422938], [-45.61901356672159, -13.871239515477741], [-45.9574497993363, -12.517037263292778], [-46.08976920218111, -10.696226001613248], [-46.12460259652837, 11.900251443984335], [-45.81966170916643, 13.69963453403976], [-45.1819471238676, 15.52807074203344], [-45.154906010118985, 16.4170387541626], [-46.066928776801895, 18.84387711014427], [-46.252517198115044, 20.034982004801027], [-46.08110128900163, 40.062854008981006], [-45.87367625320142, 43.53532023437607], [-45.67212694695094, 44.4394166893409], [-45.17947639282581, 45.721251598975634], [-44.909264408164276, 46.247466876681514], [-44.10014937758981, 47.07150280354833], [-42.31593197302429, 47.831055779365514], [-40.517103526144794, 48.051803426522255], [-30.574653230148787, 48.11527298388308], [-29.670989792452946, 48.03204740351134], [-28.795587225285505, 47.88545689624844], [-27.861822165177855, 47.55577001238548], [-27.233147932513212, 47.15302547163004], [-26.533766548839907, 46.24689525520602], [-26.15152751401225, 45.33843525358323], [-25.721459910214744, 43.53532023437607], [-25.613500694608902, 41.73143621963829], [-25.5052050706808, 24.80915444184678], [-25.67443303946249, 20.060729149650253], [-26.46182619926303, 17.320943119240468], [-26.494869407833363, 16.415423751502253], [-25.630393614893336, 13.704589996679386]]}, 'holes': []}, {'z0': -50.005087991069196, 'z1': 50.0, 'outer': {'kind': 'polygon', 'points': [[33.58208315521922, -47.82509492183438], [41.734073862653226, -47.79018525075881], [43.5417854792492, -47.52343190749239], [44.46442164755474, -47.14017275230847], [45.359320833207136, -46.33523792893701], [46.01906625941035, -45.04286294627651], [46.188612258175915, -44.124532014208825], [46.13823294154595, -21.542535248811113], [45.952496951970296, -19.734815513631794], [44.88353221899596, -16.11994805832882], [45.03038379996821, -15.214948908298554], [45.79911343262243, -13.407802855218812], [46.05128513879756, -12.4979372549562], [46.13038763525807, -11.600084952815102], [46.10790708432471, 10.99639249278248], [45.98114910045978, 12.815260497374899], [44.605680175685954, 16.42140685580869], [44.68396885737796, 17.319744178146184], [45.55883027259639, 19.130820210673832], [45.80490575292667, 20.027714979183223], [45.976188494517025, 21.842699907204736], [45.96316582505665, 41.727600499196754], [45.780511566507926, 43.53532023437607], [45.532889210227815, 44.44006701615389], [45.09542671288336, 45.34175992115975], [44.43570288404242, 46.1083940407346], [43.55222272391599, 46.651232036908155], [41.734073862653226, 47.034792375820075], [31.791623566657222, 47.031636249777115], [29.981930818105035, 46.815304695563874], [28.61988182792885, 46.241950736194966], [27.65722776033987, 45.34554575541461], [27.20023137577114, 44.49739478134566], [26.917143654913406, 43.53217456387005], [26.823085532725475, 42.631457617623], [26.839400840207194, 22.74655885840659], [27.015637286524772, 19.152452765894484], [27.570814752401557, 17.3252542668428], [27.646480740013825, 16.419988494270005], [27.064833609424493, 14.618892740933749], [26.868714604547286, 12.804110395186187], [26.811919225757915, -11.159662661872177], [27.016290458554877, -13.070162173827907], [27.776658719608903, -15.212186075368605], [27.751580806868414, -16.1223504533455], [27.159511578399858, -17.923244360062125], [26.87273523067019, -19.734815513631794], [26.78025624815152, -43.23515374320684], [27.06251130755332, -45.04276305357611], [27.48966154553072, -45.94986953938034], [28.223087181601983, -46.78555778602615], [29.06526668866344, -47.286369441765274], [30.56906021631128, -47.72146601566647]]}, 'holes': []}], 'center': [-0.005750524999999979, 0.014746015000000001, -0.35100069500000003], 'construction_scale': 183.27756105511645}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
