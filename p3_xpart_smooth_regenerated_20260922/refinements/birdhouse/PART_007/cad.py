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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.9948030817822839, -0.10181762360451396], [0.9999712340459366, 0.0007722789943629771, -0.007545506331714783], [0.007584924564363325, -0.10181469472343051, 0.9947744653225312]], 'axis_rank': 0, 'features': [{'z0': -45.77289369338641, 'z1': 50.25762892374244, 'outer': {'kind': 'polygon', 'points': [[31.646720493378492, -2.9768550605678685], [31.446767129197845, -5.941032038247068], [31.497343894963386, -8.90521202119737], [31.741984859617336, -11.86940101996078], [32.51209001250279, -12.777245287680993], [34.35347682914466, -13.721065270428628], [36.133726944288625, -14.833581002911082], [38.46827417872283, -16.604957278476537], [39.266710977254846, -17.79777000167449], [39.05230140203667, -20.761946979353723], [38.464503341851895, -21.462321220114625], [35.48481783361711, -21.587399457142148], [32.507829924750894, -18.264832617109924], [31.81096941380213, -17.976177176177874], [30.300587125631303, -17.04268573388052], [28.324055571565815, -16.263653873257436], [26.843092983278748, -14.833581002911082], [26.551778012805585, -14.23951943110224], [23.57343396002775, -12.636615899383225], [21.521918238995312, -13.011451912504018], [20.593347877305785, -13.304929197394976], [17.614583831746142, -12.24303495987128], [17.24367314515527, -11.983632048998782], [17.13311158494778, -11.86940101996078], [16.744306149611024, -8.90521202119737], [16.69529845479265, -5.941032038247068], [16.751855112306206, -2.9768550605678685], [17.708174965131256, -0.012666061804425593], [20.604102470229968, 0.548486812079878], [23.583347722328774, 0.13369296710634515], [26.563140197495546, 0.39655953499327756], [28.209084595232227, 2.350763954424401], [29.544545775066275, 2.737327035566054], [32.52443209969725, 3.1210848058419662], [35.506119761597624, 5.852455514443655], [35.42021312685702, 8.87987989758852], [35.511021695856364, 12.166830685698837], [37.388106770038256, 14.808260900386442], [38.49290157765231, 15.118568196336252], [38.90655885159307, 14.808260900386442], [39.81610782718081, 11.844071901622998], [39.60806162984995, 2.951513921145843], [38.45993835324419, -0.012666061804425595], [35.50034961485791, -1.58029845258617], [32.52028050608687, -2.2267469338001384]]}, 'holes': []}, {'z0': -45.77289369338641, 'z1': 50.25762892374244, 'outer': {'kind': 'polygon', 'points': [[-10.49754152600934, -0.012666061804425591], [-9.978030042806338, -2.976855060567868], [-10.052742978591896, -8.90521202119737], [-10.45573461051563, -11.86940101996078], [-12.182767917744457, -14.211420295381393], [-12.955177223953365, -14.833581002911082], [-15.163795493837707, -16.06526915978329], [-18.143825121821898, -16.645295600199162], [-21.122765791330252, -15.810917648649525], [-22.090590345704527, -14.833581002911082], [-22.689509907102664, -11.86940101996078], [-22.789837863887005, -5.9410320382470685], [-22.770994065514493, -2.976855060567868], [-22.50723628549456, -0.012666061804425595], [-21.10887769973678, 2.0788817866645077], [-18.128679571486735, 2.864286116623253], [-15.149132063144858, 2.8232751994730623], [-12.170258850535015, 1.9020033520402475]]}, 'holes': [{'kind': 'polygon', 'points': [[-17.36934532492721, -8.90521202119737], [-17.552124066956708, -5.941032038247068], [-16.542437586371904, -2.976855060567868], [-15.153440637156153, -2.726769196152638], [-14.883544087491359, -2.976855060567868], [-14.663866477330249, -5.941032038247068], [-14.77737980996671, -8.90521202119737], [-15.158798338269651, -9.628235658246062]]}]}], 'center': [0.60164571, -0.61160259, 0.42189509999999997], 'construction_scale': 300.5184604583519, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
