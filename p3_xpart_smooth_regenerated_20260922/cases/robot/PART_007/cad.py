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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, 0.0, -1.0], [-0.0, 1.0, 0.0], [1.0, 0.0, 0.0]], 'axis_xy': [-0.195963137001053, 0.23655361661086888], 'profile': [[0.9771326814722501, -46.38216806987056], [2.8653780517595404, -46.33332668532468], [4.772278764070567, -46.22659628527035], [6.675133299083743, -46.086499325679334], [8.579193157447346, -45.9288310105038], [10.48179180145635, -45.704174566297915], [12.377100741366988, -45.43667380253773], [14.266863615577613, -45.12823967897144], [16.145101024358414, -44.76135899394915], [18.009616830096064, -44.34445990559827], [19.854077177653604, -43.85450727264519], [21.677370498077487, -43.29417992236139], [23.47619500564104, -42.6533371432396], [25.254745789055303, -41.93389057075764], [27.003523420193407, -41.153642478023016], [28.71420782030517, -40.33088996910914], [30.40713253247386, -39.452417754695865], [32.0410120091705, -38.48344534310048], [33.615341069595694, -37.42921295134253], [35.1160267587842, -36.27518918967937], [36.535962114781086, -35.02346302075528], [37.897180511237025, -33.70333353307416], [39.211918907562605, -32.29296415653807], [40.457148709164215, -30.803234661173093], [41.592281071931296, -29.264151949428673], [42.6618020600025, -27.679811255522893], [43.67353457160742, -26.065845077100782], [44.57864873605918, -24.39279275124536], [45.4041652786029, -22.675513923227783], [46.18163104794797, -20.93431851096491], [46.867158581449814, -19.15840866345608], [47.46074235307033, -17.363393558351053], [47.98725032101685, -15.55318441129769], [48.466163524667984, -13.711853532498635], [48.87814798699362, -11.847397883124813], [49.21448172175159, -9.964255920619234], [49.46080452948469, -8.071901130970225], [49.60963946116513, -6.175182973502454], [49.663907274181355, -4.275651346498378], [49.66814094229695, -2.373813061284064], [49.63212311146262, -0.47171643527099605], [49.50502114739083, 1.4268578461271793], [49.29751986069549, 3.3176685210547445], [49.01668015052475, 5.1975044337629495], [48.62910558878365, 7.071287098491295], [48.22032340810888, 8.925144891104045], [47.77172111576066, 10.76381027563993], [47.21812733252145, 12.58364114134733], [46.56767078965474, 14.378546839512499], [45.86285090011947, 16.167555205045538], [45.111706364931564, 17.909703856957996], [44.25527863697301, 19.625590530407187], [43.31416473955675, 21.320354898778856], [42.35253930023083, 22.984757072887152], [41.347678534889845, 24.609629877541472], [40.3023942408807, 26.193933171977047], [39.180690312850025, 27.73993464184263], [37.973725160383104, 29.239908566875677], [36.72489874754116, 30.688658602790966], [35.40147458999128, 32.07603034102927], [34.00622633405089, 33.38498214089853], [32.57199369681514, 34.659721274124394], [31.077495462908175, 35.85577275487317], [29.550042428515773, 37.00337978120069], [27.986498753566913, 38.112292420328885], [26.389827324665678, 39.16250136752525], [24.74551854833212, 40.13645274245602], [23.05469891105345, 41.026320472244485], [21.332630365862542, 41.8534522509349], [19.583316501131236, 42.62759656262906], [17.801797331944336, 43.30310080825336], [15.991012062442381, 43.90727809364216], [14.161997420181738, 44.48252419761228], [12.313002804626871, 44.983166903055], [10.449462818528513, 45.40226220601973], [8.569735758509546, 45.74861873885443], [6.676116972769976, 46.01464544756729], [4.7737036181402175, 46.20853408948034], [2.866057923966474, 46.31980723966474], [0.9773886932307394, 46.37282559387222]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.221415435, 0.138170965, -0.028767385], 'construction_scale': 537.7805056395159, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
