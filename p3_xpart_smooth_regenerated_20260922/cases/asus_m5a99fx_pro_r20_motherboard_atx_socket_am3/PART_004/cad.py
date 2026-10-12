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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999853936063908, -0.005404865758895269, 0.0], [-2.006458148236841e-05, 0.003712263968475459, 0.9999931093230798], [-0.005404828515711527, 0.9999785030301186, -0.003712318192056175]], 'axis_rank': 0, 'features': [{'z0': -8.505252989815707, 'z1': 8.280500416275043, 'outer': {'kind': 'spline', 'points': [[49.81699947253909, 28.874025675446862], [44.46228186028017, 32.40519004277382], [35.463785008144086, 31.680671848216747], [26.441834276451836, 31.364459894493383], [17.415109457745157, 31.449041705414277], [8.399014423895231, 30.980957934555693], [-0.6226889309986746, 30.642877733009794], [-9.553127003687425, 29.381593024939598], [-18.5746517886462, 29.55029018712277], [-27.59423154168156, 29.94126375755714], [-36.130359207737506, 32.13469800820563], [-45.14921023392943, 32.489890848202826], [-49.89603763050849, 28.073706409139522], [-46.26297479710059, 23.465770027832562], [-38.714298723823696, 25.45227226376296], [-37.3869031460188, 16.530193371881627], [-36.00542870578248, 7.627425537125726], [-35.171005844391175, -1.360603303877014], [-34.40399696707882, -10.352440031276254], [-32.855994643910236, -19.246405174567627], [-30.474538033408876, -22.62824362760016], [-30.48007744879211, -13.73531262439549], [-30.42921450195021, -4.869040874109629], [-28.680591713357746, 0.7012101512600811], [-21.199437099561663, -4.34110222482489], [-13.244477722432716, -8.594952016679908], [-5.0482002477287, -12.371389036677073], [3.5323094061669287, -15.154925394197702], [0.41913494730948003, -20.964446931138426], [3.8763452241374794, -26.34745674664652], [12.716190855434059, -28.155576364180185], [21.66479027652154, -29.318598132061883], [30.664100454272866, -30.04154051716676], [39.591755563424506, -30.87102100595513], [44.51068738825375, -25.003462489209202], [45.969916314464065, -16.09770031851363], [46.84532165857787, -7.113579506017818], [47.5328455362393, 1.888384058872992], [48.23317305185875, 10.888383245490983], [48.9818572802131, 19.885527087096015]]}, 'holes': [{'kind': 'polygon', 'points': [[27.5891217603841, 16.168694368319763], [27.702094664795826, 16.345185780994075], [28.2759047091927, 16.538125671073875], [32.21291309968266, 17.618512688115523], [36.67390021613127, 18.535199130440652], [39.95374680222087, 19.710350598068977], [40.97804177210303, 19.736485696716635], [41.49824608746796, 19.4897714709387], [42.22428771025768, 18.116967288540103], [42.18257596925345, 17.127644567378457], [41.7885466171776, 15.666766144624733], [41.45036695967285, 14.905020636417493], [41.29555791722848, 14.073811813781507], [41.531683010132454, 13.454534021585092], [42.77559272134305, 11.625286920152627], [42.942178929026916, 11.049755115951543], [42.90450499151719, 10.326944881669425], [42.3988832424766, 9.382154366614191], [42.020557632638024, 9.088616694629996], [41.03762941115118, 8.715483674904053], [39.77936424280446, 8.432409509639092], [38.864267594579374, 8.46737423760566], [38.45690568483694, 8.710792228908172], [38.22161857030031, 9.02598498962648], [37.98404720748984, 11.677679036475343], [37.419961450091215, 12.563284210381092], [36.72025740091506, 13.21144581517362], [35.752068622161495, 13.492697344270299], [32.16512381883927, 12.603242437406653], [30.588886726709, 12.644059175872625], [29.183794829307825, 12.910070248429465], [28.2864738430149, 13.363652501691536], [27.86316705257399, 13.752143390203573], [27.542674248835432, 14.298350971401506], [27.453637698699, 14.905598628916112]]}, {'kind': 'polygon', 'points': [[-13.20736470499389, 2.572256073015234], [-9.206384025866395, 0.148926061973315], [-4.849524961676105, -2.122044057154267], [-4.77214040287931, -2.774190830507585], [-5.173018128212484, -3.5027506376905375], [-5.963062302769064, -4.154554300348647], [-7.422504647492663, -4.821045049741233], [-8.742232944066348, -4.851197090489821], [-9.615518209467075, -4.633001466126232], [-10.952838852303543, -3.9836186361741315], [-11.876029255724395, -3.372741561083916], [-13.64475571118129, -2.5860442863282707], [-14.627242957315826, -1.9445115958738122], [-15.941872310212181, -0.3833422583339121], [-16.46063491869176, 0.6955914560209189], [-16.378983386494546, 1.6417094749389662], [-15.924430890585272, 2.3743200764977352], [-15.479737083755001, 2.6889244145783744], [-14.607607181304276, 2.937025778813355]]}, {'kind': 'polygon', 'points': [[36.14720077188275, 4.581807710393495], [37.65893910137255, 5.098786625647937], [39.05413680840677, 5.779869242754465], [39.54055993982973, 6.205838649596328], [39.58142568051684, 6.451700501020319], [39.09961205372582, 7.093186189608847], [38.54290549709266, 7.423714576301316], [37.7892734360651, 7.530713475004077], [36.3447342920663, 7.272595746375143], [30.6594948699661, 5.1524458846442736], [27.9163266153006, 4.386426430028115], [24.407478899433837, 2.617123667899397], [23.828172080320332, 2.159875842506762], [23.84006130881483, 1.9319965513736004], [24.37573893251573, 1.789733390600574], [25.44916352365623, 1.9930325886269022], [29.734892543793666, 3.3788487302405588], [32.68230222561782, 4.15585392104791]]}, {'kind': 'polygon', 'points': [[42.342445359124824, -1.774352901521412], [40.76118475662203, -2.510876927652549], [40.01522744240472, -3.0215984525487927], [39.92602212828184, -3.234404652685533], [40.62658625926198, -3.4705812235781934], [41.6944106633742, -3.6110333073444334], [42.648308997439024, -3.2786582408022107], [42.928742001616875, -3.0214273397295677], [43.03723112234858, -2.261609981915186], [42.889752581382396, -1.9204075150744049]]}]}], 'center': [0.13279676499999998, 0.048857525, 0.056176895000000004], 'construction_scale': 45.581271541623465, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
