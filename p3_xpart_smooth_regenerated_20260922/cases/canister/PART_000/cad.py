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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9996592317719019, 0.026104029060876423, 0.0], [0.00010435088420789714, 0.0039961388526926055, 0.9999920099606612], [0.026103820488657323, 0.9996512444553145, -0.00399750107405043]], 'axis_rank': 0, 'features': [{'z0': -47.246812893242605, 'z1': 47.253878299911605, 'outer': {'kind': 'spline', 'points': [[49.92956726998339, 18.992539477537044], [49.897494914413215, 28.25264128080103], [49.21855959148014, 37.47756897521586], [44.92993342312763, 45.478046005361385], [36.623408309601615, 49.13516576268293], [27.38411121191444, 49.72508403856229], [18.12498737092326, 49.86518894931247], [8.8643817838051, 49.9072772836032], [-0.3962645987033178, 49.93948192909304], [-9.656960629097643, 49.95007694996697], [-18.91766018273929, 49.94152985402461], [-28.17733022850516, 49.84331613420419], [-37.395409527758524, 49.09045723356819], [-45.430682533722624, 44.866708811271515], [-48.98094990554551, 36.48680440837025], [-49.595878866709995, 27.25245135492216], [-49.741509418540296, 17.992926876410664], [-49.8291278827866, 8.732650454306276], [-49.88127481254967, -0.5278907195773899], [-49.849746010458816, -9.788518637054416], [-49.83188251354074, -19.049190936197302], [-49.68922236368061, -28.308268008308797], [-48.97403520520964, -37.53214791869662], [-44.7620853296315, -45.61697776362557], [-36.38215246861561, -49.1803056887447], [-27.14073861429381, -49.70502581290518], [-17.880947111859555, -49.81448988786511], [-8.620278294903096, -49.793323810006505], [0.6403882464692465, -49.76786562230891], [9.901001181655865, -49.727729334060726], [19.161676483820997, -49.709185836260424], [28.421915978679188, -49.633892844254746], [37.65467652271265, -49.02091632119265], [45.9418010970428, -45.253714342771715], [48.8329481969407, -36.547215614864264], [49.38544886482804, -27.306884849883886], [49.48341307590889, -18.046880623209514], [49.57435156217694, -8.78666126698179], [49.76005325383284, 0.4721555651322177], [49.88584713759771, 9.731955882274024]]}, 'holes': [{'kind': 'spline', 'points': [[47.57474732920964, -11.75556308530535], [47.52862771175744, -3.025101819875767], [47.45556098586798, 5.705185422641352], [47.465280808183145, 14.435780266323434], [47.331912692501845, 23.164670353538792], [46.65282650107527, 31.866519429857814], [44.45392544639042, 40.253815633791945], [37.96744081782561, 45.694725107755666], [29.3590796180954, 47.05161035187481], [20.632337901092342, 47.26738207245747], [11.901727845414605, 47.25302684164273], [3.1710897149330757, 47.250579995928646], [-5.5595464346653625, 47.25611912531704], [-14.290172820088717, 47.25352793231068], [-23.020725910538726, 47.26576303002148], [-31.73511947761796, 46.83877565388039], [-40.03238753641368, 44.41003169642755], [-45.06988815313141, 37.570080543953175], [-46.381368440050856, 28.9535495254561], [-46.81454286698081, 20.233920274637235], [-47.1291265564557, 11.509002770722233], [-47.32779161486771, 2.781184202701319], [-47.32284696140849, -5.94941786369369], [-47.20342252252855, -14.678775799953938], [-46.939944828999465, -23.40529938135345], [-46.14148665582777, -32.09577351412961], [-43.929529734712276, -40.48036973242487], [-37.42806621044373, -45.79210082324516], [-28.79263957807805, -47.03431844834919], [-20.06508527419561, -47.2097257818906], [-11.334473943196649, -47.23160915650249], [-2.603852011421235, -47.22123848835649], [6.1267261123419, -47.18815974288453], [14.857325723582747, -47.1625003593036], [23.587944980014516, -47.178566716381006], [32.312837403686665, -46.9432354424956], [40.69120190549242, -44.72287335614243], [45.449833500818016, -37.78214142595333], [46.953122855550696, -29.19459841290931], [47.46729086952574, -20.485320854249387]]}]}], 'center': [0.006436520000000001, -0.06820839000000001, -0.00016383500000000106], 'construction_scale': 50.784191713980185, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
