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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.050607057213605686, -0.0, 0.9987186419408515], [-0.009479217992708509, 0.9999549558397951, 0.00048033080304277605], [-0.9986736554983444, -0.00949137984877017, 0.05060477766121306]], 'axis_rank': 0, 'features': [{'z0': -36.06618472293969, 'z1': 32.72172966753891, 'outer': {'kind': 'spline', 'points': [[42.985355351123125, 8.143679633649135], [41.86665176734854, 15.623311064248131], [26.75175786627055, 23.3491419236827], [12.370549535253492, 31.954653440504504], [-2.338038754004199, 39.855888050181896], [-19.17764332740727, 40.83571601851046], [-12.598029991998297, 31.678293782807845], [-2.831835319052927, 28.70183090256823], [13.834179212368547, 26.465053889765134], [24.60787317200315, 14.957015243924745], [21.983599928714597, 4.576597450977079], [13.056075517058392, -1.5820063359948846], [-3.7605596290282595, -4.053251158104711], [-14.517214814507241, -15.004088826419249], [-0.80879406844038, -10.06622697528431], [8.423264388815758, -18.623260120762776], [-7.818334746098775, -23.980113397341384], [-22.42279972618716, -24.540434658942566], [-21.59265945773235, -9.45077805558917], [-21.06026195392317, 1.3900687277697659], [-20.59721182826526, 14.301833419771329], [-22.515777355243017, 29.991772532398134], [-28.30976403204308, 45.97765947662648], [-42.432700943294975, 48.62287342054646], [-30.206881706600704, 42.668884719736994], [-29.819597259898092, 25.54041721237141], [-30.73938539289604, 8.458837671128608], [-28.075959405387977, -2.9559803227464827], [-29.291542181954004, -20.01829821946653], [-29.983322813186774, -37.12984446935832], [-36.23014910730755, -48.33283377003311], [-29.825992407607416, -49.45032704506375], [-23.456851429762914, -36.07913249173644], [-8.460078753839843, -36.5469775745928], [6.697034885835457, -28.635755616139704], [19.478302356356895, -19.545495687497052], [16.861348406929427, -11.265325793069273], [9.755844847833245, -3.7765495181900697], [26.153526553856793, -3.2575566179262188], [42.78271579376736, -4.580299946932175]]}, 'holes': [{'kind': 'polygon', 'points': [[-9.878945716902306, -29.50746720754817], [-10.80132326107228, -29.11154124426155], [-11.54334060171031, -29.043305626131975], [-13.474802235235707, -29.504065140607434], [-14.608519440818396, -30.093728704380148], [-14.891397937767366, -30.584831693792783], [-14.759852047910186, -31.10562238076372], [-14.357670944776714, -31.561688194488177], [-12.441230611690784, -32.67161085812861], [-10.17124829144868, -33.52359889201231], [-9.300711052978095, -33.55322726448887], [-8.686794277782003, -33.121585405876566], [-8.518713481163946, -32.271206646032105], [-9.033868703013017, -30.30984212336411]]}]}, {'z0': -36.06618472293969, 'z1': 32.72172966753891, 'outer': {'kind': 'polygon', 'points': [[6.131301499484583, 17.665612395522167], [7.734401162130372, 18.11617989728313], [10.881917222691309, 18.42193608255872], [13.854205082285674, 18.19144560610701], [14.90603460142266, 17.746756020955846], [16.732035488299562, 16.537765336397293], [17.51033405094305, 15.698317817921746], [17.5376156275058, 15.256590711758642], [17.259206925506046, 14.389443589881719], [16.409189252646396, 13.666305663633802], [14.407109356870162, 12.680861625314384], [13.110470307625976, 12.21143104782606], [11.351164668206609, 11.934315687621979], [9.68650577114334, 11.87838881008092], [5.21193991869691, 12.35993900235432], [3.411359481387998, 12.28104282937962], [-1.182140173753395, 11.134694144021543], [-4.8755794084734845, 9.250223822884927], [-7.448928317168616, 8.15325325778848], [-8.806593666317308, 7.046498348482328], [-10.74582700003122, 5.012362646987017], [-11.877874264548055, 4.167910011973605], [-12.631196759069843, 3.7943400239520297], [-16.27476093122406, 2.511052352413211], [-16.94477837035371, 2.496201462006983], [-17.714877606436087, 2.941276117807457], [-18.220336028835654, 4.520481605253433], [-18.221513692317146, 4.936211595053248], [-17.608397154312264, 6.3351351453774045], [-17.04498764913662, 7.087766873100658], [-15.755374891362074, 8.059169617603496], [-12.315083160648015, 9.65465797289422], [-10.785995190894514, 10.126258383475104], [-8.266951451058032, 10.580986951062954], [-7.314362369614507, 10.905766010964106], [-6.3966502093000415, 11.418964862860998], [-3.126410307409215, 14.541341763438787], [-1.6467259566962438, 16.89889038342031], [-1.0352585050423015, 17.57335745778421], [-0.2044613580339659, 18.205069177011502], [0.5648227500231062, 18.628060712409287], [1.4348709289735522, 18.848237020040724], [2.6121480471137457, 18.388526750805045], [3.7959330718447495, 17.675813410840142], [4.874071512471313, 17.46798667600419]]}, 'holes': []}], 'center': [0.000867585000000004, 0.0008444149999999873, 0.03069735999999995], 'construction_scale': 49.9293392501531, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
