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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, -0.9968127528887427, -0.07977678658836991], [0.9999997038714085, -6.139481218462961e-05, 0.0007671295669330676], [-0.0007695824162661864, -0.07977676296418246, 0.9968124577039862]], 'axis_xy': [-0.4769039891330204, -0.049915727523543583], 'profile': [[0.9708563771183407, -45.99465391459738], [2.8466479260598083, -45.92795960839314], [4.7388977783916335, -45.782347113860915], [6.6115339921320295, -45.487001671111216], [8.459459829614293, -45.06182280951996], [10.280135585321936, -44.52591497298258], [12.07770088549173, -43.9170250255724], [13.857723796882187, -43.25841039235584], [15.615441197396198, -42.54079161721789], [17.352701759572987, -41.77424892162921], [19.075622152643245, -40.9906212186895], [20.78343754322721, -40.18483630291484], [22.46349794517311, -39.29236045327038], [24.11731498094919, -38.3392626573019], [25.73707063736329, -37.321497318449175], [27.30370113855441, -36.22588216371746], [28.823943653323134, -35.07517666585123], [30.309308893443347, -33.87510461071567], [31.75997234315613, -32.652480098698426], [33.17842215477546, -31.40289492877352], [34.51078984087586, -30.07770770128966], [35.77684840411619, -28.683236199361495], [37.03705444678003, -27.262423301372372], [38.238986798624225, -25.79667432408973], [39.383498882508675, -24.300477257230305], [40.49294473832537, -22.759883083256177], [41.557668698735654, -21.182413036374264], [42.554741010541434, -19.567164850027435], [43.48852503653661, -17.914690064634257], [44.36795326115028, -16.231026765677107], [45.18473559690125, -14.516384460811185], [45.92700402405873, -12.77771743924696], [46.61548731696948, -10.99086516701971], [47.2206479377652, -9.192637208687728], [47.74403137893238, -7.3833821953308], [48.21981459806635, -5.546891041420669], [48.623693376468665, -3.705411898756241], [48.978183263006045, -1.8528761421669562], [49.27411754060867, 0.016591955017397117], [49.5270489374664, 1.897041729921122], [49.72710086851155, 3.787874943495388], [49.883331178719686, 5.6903046956663195], [49.97429852439993, 7.597852843923933], [49.960842968386494, 9.50398041705037], [49.871184010406665, 11.407426291650516], [49.72348171589995, 13.304822577009583], [49.49427202566849, 15.193885140349128], [49.18679340181224, 17.074960866727864], [48.771768927488125, 18.94308310672968], [48.24540127943215, 20.789268902238977], [47.60436351410296, 22.591563788141244], [46.818408425175996, 24.329402341385556], [45.90166131153448, 26.006234900701273], [44.87076761441605, 27.649888332463053], [43.790457597542854, 29.189705364848173], [42.542586676293205, 30.59534502797281], [41.16621428772784, 31.892837986041897], [39.74412074743032, 33.103115133777486], [38.23332958769131, 34.24345071339229], [36.7116665445497, 35.344303496732174], [35.170436807908615, 36.424325830806865], [33.5791271878929, 37.45457826120021], [31.92114729725403, 38.378707888598015], [30.23130319337608, 39.24421295894952], [28.51663540601438, 40.05861087188723], [26.770961418444912, 40.80393713524807], [25.005371484785357, 41.5012871891686], [23.226971205231116, 42.16579738881731], [21.436709918875458, 42.799142239905166], [19.62328920871884, 43.38392099409616], [17.797220712638868, 43.90243445201281], [15.964065128024139, 44.38050807231644], [14.125598906973133, 44.82868535764182], [12.275690565062309, 45.26528762525118], [10.414524798895972, 45.62874087654532], [8.53314400212008, 45.88341015985606], [6.64117436576933, 46.03709510330938], [4.745178886672531, 46.136594171192336], [2.8477165370718986, 46.203929849101996], [0.9709775028044317, 46.248618924188406]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.009219024999999992, 0.52313475, 0.74778702], 'construction_scale': 268.27742579332386, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
