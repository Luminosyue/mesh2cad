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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.0, 0.9997777345136651, 0.021082731576415745], [0.9999829078487094, -0.00012326460422114948, 0.005845409846786838], [0.005846709368488083, 0.021082371227178022, -0.99976064616137]], 'axis_rank': 0, 'features': [{'z0': -36.92604879949364, 'z1': 37.26804803071599, 'outer': {'kind': 'polygon', 'points': [[17.97887650698179, -47.08436865772521], [20.30861732913106, -43.9483503659029], [26.214820171029597, -35.065851831619916], [30.542523309641684, -29.14418113897211], [32.156226050202605, -26.183344291710473], [32.79023219738886, -24.702930370892883], [32.97084600228953, -23.222510446324314], [32.49528884819141, -21.742096525506724], [31.699104927629957, -20.261676600938166], [30.59587010082288, -18.78126268012057], [29.162682915026522, -17.30083975367652], [27.38989325910749, -15.820425832858932], [27.624553479969453, -14.340011912041344], [31.275958322830114, -9.72256114214676], [33.06671684786459, -7.036012613575942], [40.565962952978936, 6.385831009412715], [41.714827271054, 9.34666485479887], [41.95390233986537, 10.82708177749195], [41.8624871399694, 12.307498700185025], [41.46082051883956, 13.787915622878103], [40.50395443694127, 15.26833254557118], [38.99235227628973, 16.748749468264258], [37.202297852730034, 18.313325166899563], [32.76055085442405, 21.705281250103653], [10.560884137991124, 37.057747839228874], [-5.633801888211107, 47.83751084856986], [-7.215583971883941, 48.69768940189286], [-8.696225606890337, 49.31488106091313], [-10.176910457071424, 49.65462002273103], [-11.657615961574125, 49.75377732211823], [-13.138377558603958, 49.44668327570754], [-14.619167999563343, 48.85693576916069], [-16.100015194027804, 47.85557583998472], [-17.580928457075853, 46.26963976552507], [-26.802623271075092, 33.0333386197636], [-30.56299146215321, 27.111670928991288], [-31.296568267774184, 25.63125400629821], [-31.795801769274693, 24.150834081729645], [-32.01060800243625, 22.67042016091206], [-31.68869835230597, 21.190000236343487], [-31.045303018758847, 19.709583313650413], [-30.550123465674318, 19.04588385926506], [-29.892963717278477, 18.229166390957335], [-27.949658384157242, 16.407213328389314], [-26.974478756742492, 15.268332545571182], [-26.953638524471558, 13.787915622878103], [-38.04156138861225, -2.496673528621236], [-39.907345615504596, -5.457507374007391], [-41.27919674331632, -8.34514932095522], [-41.79968533843771, -9.89875814208662], [-41.855958045653594, -11.379175064779702], [-41.42628105125666, -12.859591987472777], [-40.64495123297975, -14.340011912041343], [-39.79937039810476, -15.575014498121249], [-37.786396053887714, -17.30083975367652], [-26.474035206577234, -24.913812397236047], [10.540984231633676, -49.31017625446138], [12.021639214113856, -49.84346156432352], [13.502361023966813, -49.81036900782778], [14.983121518432473, -49.512217667413566], [16.463947851267864, -48.65571009210164]]}, 'holes': []}], 'center': [-0.11497730499999999, -0.14363580499999998, -0.18826536500000002], 'construction_scale': 300.18241785350546, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
