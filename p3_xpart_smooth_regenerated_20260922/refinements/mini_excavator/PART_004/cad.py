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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.9988374798750278, 0.04820465534472168], [0.9997449700065149, -0.0010886089950305012, -0.022556814427771122], [0.022583067698454185, 0.04819236171178316, 0.9985827463590425]], 'axis_rank': 1, 'features': [{'z0': -48.06358068913625, 'z1': 45.798738096816855, 'outer': {'kind': 'polygon', 'points': [[-47.56734572068819, -8.121864457064326], [-47.575882143159156, -11.639732721210445], [-47.43913706203879, -13.26278700182976], [-47.178500262792355, -14.271278823106918], [-46.18993359624012, -15.636014746807819], [-44.29006539014214, -17.101508656949015], [-43.553954227099226, -17.50752603113945], [-40.91954661854258, -17.936891064497285], [-37.25911597894937, -17.992307464274994], [-25.116087169371447, -17.770684308735966], [9.389896693864829, -16.941360040900072], [10.435854703372243, -16.90283026105543], [10.774911031538068, -16.681380792873966], [11.757599195769545, -16.418117102229363], [14.391034357233009, -15.955227333091953], [18.065423249189212, -15.765260805661777], [25.606700316329942, -15.60682442099298], [43.3639789827811, -15.59104976605193], [45.9973547004074, -15.07361816162134], [47.19885475585247, -14.271278823106917], [48.62862162171946, -12.618840686161306], [49.181826012569516, -11.639732721210443], [49.60308564543754, -9.008183951287949], [49.85969097181307, 1.6190912006698994], [49.831392583706965, 14.675757646040507], [48.944124629172066, 17.307306415963], [48.59557940632506, 17.69856740498575], [45.96048753524332, 18.753317414634708], [43.326774792540384, 18.545118307580204], [40.6928710592292, 18.50970964510907], [35.42486665689684, 18.624488305862783], [22.25525664082002, 18.543512593255816], [3.695262639004309, 18.662603295859814], [-22.521728658666508, 18.546422671339418], [-38.325457820747516, 18.630137338245476], [-40.959052560562235, 18.311216150426798], [-43.09543272258976, 17.307306415963], [-43.59114460840554, 16.615971853930706], [-46.22339501130663, 15.066023956399334], [-46.6280924883115, 14.675757646040505], [-47.9275260255019, 12.044211544144032], [-47.82619397330233, 11.08415025150549], [-48.26902559159152, 10.179852481055393], [-48.85162070369396, 9.823260984622328], [-48.976200136929045, 6.781114004299046], [-48.83609520322009, -4.421938015126362], [-48.45107565893026, -4.338049370376436], [-47.68627097240974, -5.219836070875138], [-47.676842668560745, -5.6465361105984435], [-46.52247543247904, -6.37663251333944], [-46.67725054897772, -7.0145911351822]]}, 'holes': [{'kind': 'polygon', 'points': [[-9.569496679135181, -15.544892884290482], [-40.92209769199262, -15.596190420427488], [-42.22271396335847, -14.980331093278274], [-43.55695565309304, -14.753610906994474], [-43.925600187810936, -14.27127882310692], [-45.31284155371066, -11.639732721210445], [-45.8974230412527, -9.00818395128795], [-46.204006824424425, -2.7233272368856913], [-46.88412819508078, -3.0934676653225686], [-47.47821404942355, -2.708438383108424], [-47.5054706231386, -2.262387622804391], [-48.38362808581693, -1.1135349734944542], [-47.53173935828448, -0.2691108883806558], [-47.50607827200144, 0.7114017923889482], [-46.67639186348162, 1.518013796428039], [-46.79853777481104, 4.149562566350533], [-47.542261338754564, 4.750091164956869], [-47.6377524565089, 6.2162490502267325], [-48.143788281143216, 6.781114004299046], [-48.101722843291114, 8.432439069756608], [-48.310334192461376, 9.41266277422154], [-47.04722004182729, 10.061863625597889], [-46.217504951094654, 9.661684174806922], [-45.31202998028158, 12.04421154414403], [-43.58812051898184, 13.841262226621284], [-40.956340290445546, 15.822611830180314], [-38.32272653040861, 16.12408128747697], [-35.68889110787305, 16.219717283798506], [-21.47713729091754, 16.43678301019602], [40.69451966894365, 16.99705158331428], [43.32855944176692, 16.907639153879355], [45.96319794779268, 16.266417478492787], [47.30984707963391, 14.675757646040505], [47.44240207286959, 12.044211544144034], [47.34285387936566, -9.00818395128795], [46.12647744321342, -11.639732721210445], [43.361085225110976, -12.935924159164713], [25.645771825157244, -13.70123822018249], [5.7548301016299925, -14.271278823106918], [3.8540337626842534, -14.818117743300052], [-4.04718528037988, -15.368564467981123], [-7.05344184899508, -15.380095932251164]]}]}], 'center': [0.152218725, -0.10378309499999999, -0.10288828500000002], 'construction_scale': 266.7345595032122, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
