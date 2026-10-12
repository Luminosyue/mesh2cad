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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, 0.9993306307894501, -0.03658265116089798], [0.9996011651055566, 0.0010331025664518457, 0.02822132914483884], [0.02824023228683042, -0.036568060723083766, -0.998932062862805]], 'axis_xy': [-1.0099091112459448, 0.8772025279233872], 'profile': [[0.9858403791213135, -41.73028794837265], [2.8777217008673652, -41.846462524270606], [4.718087173739467, -42.271291752054815], [6.309094527940772, -43.1254484984533], [7.35959750524065, -44.629520606336094], [8.056425824067546, -46.427521437325645], [9.125370903247639, -47.981679874029055], [10.846091298911908, -48.728287951373005], [12.776453620192733, -48.903574088725335], [14.714246792214535, -48.8754020561809], [16.655887078713402, -48.82684753997876], [18.623182079964703, -48.770712731381074], [20.59771097324561, -48.72406819474645], [22.57267538388885, -48.749338823734234], [24.53914902381876, -48.70871048737366], [26.311838049708463, -48.13771178564298], [27.29396914169636, -46.70336500154527], [27.55091365162251, -44.84405726950614], [27.629314174438697, -42.881872006369406], [27.673360263501053, -40.90755263492373], [27.696026912259725, -38.95794840105399], [27.68073184343116, -37.028979248690874], [27.675333101481883, -35.099917722089124], [27.699367587367817, -33.171381666547404], [27.698178965880373, -31.242823520354264], [27.689341805568617, -29.313987331801293], [27.67078447306469, -27.390813984648705], [27.643833025602028, -25.478266880210043], [27.58878996792688, -23.567350070297095], [27.481621385374826, -21.656133553701714], [27.44561792709039, -19.74472209089274], [27.35146902663057, -17.829526901397365], [27.085458161198478, -15.94263372614971], [26.327713946037036, -14.659371320897364], [24.63626479478291, -14.12281861227344], [22.691364153278382, -14.065249079879647], [20.72859054174239, -14.067796546445221], [18.7540692779032, -14.037590048632369], [16.770508884632136, -13.892391426094036], [14.805006910377912, -13.770761264110227], [13.04953936307449, -13.061448372062715], [11.978272565017328, -11.684578796798299], [11.501664496296897, -9.987875338786536], [11.276960923708609, -8.155011505501587], [11.108141519733891, -6.318141159752571], [11.066621504724436, -4.462611416395106], [11.20622339586722, -2.6285580556172663], [11.175505183500032, -0.743220916793637], [11.069482882050519, 1.1596972879756442], [11.115204240220631, 3.027845989282404], [11.24734271642582, 4.8929486458483105], [11.184168688274024, 6.635549841493875], [11.024576468394676, 8.469760293332149], [10.956811597347578, 10.278458190239558], [11.031186942234932, 12.147915794313693], [11.274108356833581, 13.949726801050044], [11.174200648833569, 15.860760418246189], [11.096364319829377, 17.71465312925264], [11.172350576126107, 19.551142402876252], [11.319069615713296, 21.284214172984164], [11.22736894616071, 23.089239818200802], [11.09776195687763, 24.941573687971406], [10.993550348594994, 26.849622708300807], [11.135447434044558, 28.68454233530172], [11.316825730302478, 30.52945585585067], [11.193275849979628, 32.3882928578528], [11.126083905505302, 34.25402653802911], [11.332658891612905, 36.11030480628509], [11.401522567579974, 37.883419192237795], [11.213987536483577, 39.74660857011382], [11.079890757567544, 41.64915411916124], [11.167898456647517, 43.55917558343744], [11.530709041670516, 45.43018220825496], [11.234559261821234, 47.25455143846976], [10.315699905432174, 48.821502322912295], [8.687116278887519, 49.775870018750226], [6.796888968191996, 49.935373202785726], [4.857263460536034, 49.92924091927464], [2.914543011136681, 49.924107520551054], [0.9936022302275291, 49.922742948583306]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [0.8809288200000001, 0.71560012, -0.569878465], 'construction_scale': 271.7206932996965, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
