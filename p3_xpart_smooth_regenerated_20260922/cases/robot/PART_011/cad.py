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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -0.08423253525078214, 0.9964461249888154], [0.9978650842946533, -0.06507696149950536, -0.00550114784538141], [0.06530906174203428, 0.9943187965070447, 0.08405270588837406]], 'axis_xy': [-0.29972198049410825, -0.3916037751667298], 'profile': [[0.8457964838201644, -23.199575775656243], [2.4812117079013447, -23.218347890382464], [4.13538055872655, -23.243914293323378], [5.789452425457283, -23.246154704423137], [7.44346184372176, -23.245521914776926], [9.09719506413343, -23.268138108020963], [10.751515116045928, -23.285276509188783], [12.406048587266458, -23.30005290568947], [14.060639399032478, -23.311095841847596], [15.715325135647905, -23.322752301650716], [17.369890629167635, -23.3334866372737], [19.02388065001341, -23.343250590915265], [20.677752132741702, -23.37325796871767], [22.331799216067363, -23.41091458706157], [23.98609221325887, -23.430274129316718], [25.640025409437733, -23.442404366511287], [27.29346715987559, -23.43605833300918], [28.94647989972772, -23.40837219888102], [30.59902466308726, -23.325825568262943], [32.24774160046372, -23.183250875678617], [33.88208871199269, -22.936479707302865], [35.48592638431036, -22.51446962934406], [37.05696710816507, -21.940336394665323], [38.54890219883907, -21.22700333880055], [39.98902381340004, -20.410975425829932], [41.37156213925472, -19.47400348277877], [42.66451315879332, -18.459262868654037], [43.83471442195179, -17.316481278689047], [44.91861559252413, -16.074401726273102], [45.85786976138875, -14.731215336183826], [46.69846398416624, -13.298718005516108], [47.41078850277418, -11.798731007320406], [48.005064376089365, -10.252066909742014], [48.499671692844586, -8.662398651837176], [48.86662737248764, -7.042142779126161], [49.14161289513497, -5.409484290006294], [49.30397997374107, -3.76543938135442], [49.37105249316605, -2.1135669857670054], [49.35877985798562, -0.4575001405525918], [49.337187144083195, 1.1989651834483126], [49.311020180019455, 2.854495829645881], [49.27589301085244, 4.509677651206558], [49.27060435535937, 6.166385492577793], [49.28352080784863, 7.82313872406932], [49.33176185682139, 9.479413854753414], [49.39283033976956, 11.136002584200579], [49.40996131372924, 12.792624509451668], [49.334715244106974, 14.445973011013509], [49.06498450553211, 16.08119595864445], [48.55506924008439, 17.658129997152933], [47.770180657139065, 19.104910229356044], [46.70399059090563, 20.368404659740506], [45.343913606118264, 21.316134561077263], [43.78488710060482, 21.87510374108297], [42.143594132662066, 22.10550142885651], [40.49409468618394, 22.14197651347172], [38.84179442388613, 22.06260459539678], [37.19107762000583, 21.94906626597372], [35.54370206734926, 21.817366260955115], [33.89723515079967, 21.698923555121013], [32.24704256354428, 21.590669111377682], [30.594496383482063, 21.487928262511158], [28.9411269738523, 21.417367665181374], [27.288214482016286, 21.37766374948145], [25.63684646590348, 21.343614619241777], [23.984671821753032, 21.290987310879725], [22.331915421884112, 21.27076272909705], [20.680118996594736, 21.229471450797817], [19.027289181673595, 21.18927780513333], [17.37301640291094, 21.170470611868232], [15.719140837373367, 21.154858116333134], [14.064854231982654, 21.145625173551853], [12.410285042030495, 21.143896000362318], [10.755476351173588, 21.14913932525321], [9.100597940381014, 21.16179182563644], [7.445776731146868, 21.17276538647649], [5.791095760371211, 21.17501855594911], [4.136413363406275, 21.181520076230733], [2.481671107905386, 21.18213619243904], [0.8459878640081782, 21.178164034104515]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.27144536, -0.36983505, -0.31730189], 'construction_scale': 386.86347804503333, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
