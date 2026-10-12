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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9999945425022845, -0.0, 0.00330378050823564], [5.909496809315629e-06, 0.9999984002615491, -0.001788697688456973], [-0.0033037752230509277, 0.0017887074503237968, 0.9999929427725642]], 'axis_rank': 0, 'features': [{'z0': -49.988575618230605, 'z1': 49.99433039441481, 'outer': {'kind': 'polygon', 'points': [[-3.243520973679474, -17.637504819302933], [-5.234655580152573, -16.342085724059928], [-7.062055683567121, -14.717164391371808], [-8.171097032699054, -13.14750931105793], [-8.612090641821819, -12.082650506723935], [-8.891531647793578, -11.017789543151213], [-8.884614211070524, -9.952932898055936], [-8.113415005909044, -7.823213130149219], [-7.018609602769093, -5.693495521481221], [-7.086523325746472, -4.628638876385945], [-7.788368431667732, -3.563777912813223], [-9.789920839089465, -1.4340624633839445], [-10.586267179062416, -0.3692014998112294], [-11.195892750353556, 0.6956551452840533], [-12.143212673343596, 2.825372753952051], [-12.481469775198438, 3.8902358767634917], [-12.604635737700837, 4.955092521858768], [-12.451910885590976, 9.214527739194757], [-12.146195014115166, 10.279386543528759], [-11.646865882659904, 11.34424750710148], [-9.60665209438177, 14.538821760864755], [-8.12710269652734, 16.070633752715352], [-5.997386105657576, 17.633157738526435], [-3.867663691913675, 18.575729264731628], [-0.6730811688971741, 19.261860496663818], [0.39178322045613656, 19.377304394895845], [1.4566443224891714, 19.318254892380832], [3.586374268639608, 18.986205977902152], [5.7161038732252605, 18.346572101491812], [7.845838639538659, 17.19886378010078], [8.9107043884704, 16.353474341134103], [9.618822883894737, 15.603684883676197], [11.087515479366758, 13.473965115769474], [11.626710572107847, 12.409104152196763], [11.97333218870232, 11.34424750710148], [12.538389913282245, 8.149666775622038], [12.621212588660203, 7.0848101305267654], [12.374202083074238, 2.825372753952051], [11.975770244882739, 1.7605161088567687], [10.86339875960476, -0.3692014998112294], [9.975676695165347, -1.7926624255782853], [8.651504326332848, -3.563777912813223], [7.6032670695507685, -4.628638876385945], [3.4840175155752906, -7.823213130149219], [3.81033158523673, -8.88807625296066], [6.1329910751554495, -11.017789543151213], [6.997996023852663, -12.082650506723935], [7.579664713416456, -13.14750931105793], [7.960531650513741, -14.212368115391932], [8.0136751422661, -15.277226919725928], [7.573658669580012, -16.342085724059928], [6.781179524435012, -17.287339706437194], [5.716319600385046, -18.1583942968226], [4.6514632738304895, -18.90744277236434], [3.586601075331134, -19.393619081267392], [2.521740725526815, -19.461860385463794], [0.3920108441928168, -19.140779592447963], [-1.6266333970189215, -18.47180333272793]]}, 'holes': []}], 'center': [-0.23853367999999997, 0.213770395, -0.07660417500000001], 'construction_scale': 215.9235266236839}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
