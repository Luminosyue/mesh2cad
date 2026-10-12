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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.4732916328954764, 0.8809058009975491, 0.0], [0.08805478054616207, 0.04730992896374606, 0.9949915206897055], [0.8764938025189345, 0.4709211615443839, -0.09995936052010068]], 'axis_rank': 0, 'features': [{'z0': -6.677010171905724, 'z1': 6.892739507291928, 'outer': {'kind': 'polygon', 'points': [[-33.817165640235906, 37.44476263377653], [-11.565393997765277, 47.61774959275934], [-6.980453347783393, 49.59736970905553], [-6.026079990662699, 49.80854979757677], [-5.45214139315069, 49.687867442309795], [-5.022783408848773, 49.40023669155629], [-4.293900495920038, 48.213061441282065], [5.160996781100237, 27.298666831934224], [10.538463081348395, 15.945140303014579], [33.91120381293288, -34.84695569822705], [34.13555370983251, -35.44451578443525], [34.23621166876998, -36.308637844072905], [34.20101682296355, -36.63962626345913], [33.647728525693836, -37.411851084670296], [32.97797837376707, -37.86346821844344], [27.19356537267019, -40.34719073056808], [7.157419057937489, -49.61557152182619], [5.9720383343397, -49.92278866988441], [5.330414981144814, -49.78790869225167], [4.637312086778101, -49.188257213032315], [3.954279316384712, -47.993146734008455], [-14.490016310863906, -7.359471629358827], [-22.757606886883917, 10.370197108060692], [-32.62993989470041, 32.079100266311286], [-34.417709052485165, 35.66442443333855], [-34.58777054241969, 36.2650682911026], [-34.41619946758375, 36.85953248901429]]}, 'holes': [{'kind': 'spline', 'points': [[6.641105606368206, -0.25032817103917016], [6.592732378795149, 0.7680394673392941], [6.372168884866184, 1.7622877775843424], [5.952496373793147, 2.691353656038544], [5.40229917701425, 3.5501875916797725], [4.728617170599812, 4.315667799783721], [3.9642252986475786, 4.990855833326477], [3.0810446648203422, 5.5022613934719855], [2.118036952623103, 5.836591050464628], [1.1144320381900832, 6.0206703752808375], [0.09711810126028525, 6.090548591590124], [-0.9183752245069541, 5.9989411225934], [-1.9105003397051936, 5.765167965205136], [-2.844204951989302, 5.355415502160951], [-3.7000650124208496, 4.804134477088686], [-4.449542334544165, 4.111841005353764], [-5.0765052771406465, 3.3065978818087145], [-5.633153895257576, 2.451530050206741], [-6.063968916878399, 1.527445591058585], [-6.319842964585008, 0.5428809989864691], [-6.372978162791562, -0.47364638512695645], [-6.2501686550374504, -1.4859394783893896], [-5.994021632837826, -2.473355318708987], [-5.590796407902645, -3.409851595536431], [-5.068669126854593, -4.286144406882748], [-4.428861508722509, -5.080336114674134], [-3.645566295298462, -5.730581211514122], [-2.764497556920461, -6.241597228545913], [-1.8046221208736954, -6.5881088857336785], [-0.8033206466812525, -6.779717034703875], [0.21605650491696815, -6.821139164172978], [1.2303723436300549, -6.7152272109693385], [2.2169607643929274, -6.45866135625994], [3.1630253791239435, -6.076515190186167], [4.04060885298667, -5.555314414989971], [4.823227644867724, -4.902391722274522], [5.458351570096107, -4.104513384929359], [5.959502983683172, -3.2176354017466764], [6.310159425333667, -2.25996873276467], [6.533158549029992, -1.2650579763594083]]}]}], 'center': [0.161103625, 0.527876755, -0.3484987], 'construction_scale': 120.56054189938166, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
