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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.9994865848879034, -0.0, 0.032040078481739016], [8.121587724282989e-05, 0.9999967873350232, -0.0025335200046521676], [-0.03203997554770102, 0.0025348214202758033, 0.9994833738723572]], 'axis_rank': 0, 'features': [{'z0': -32.8231898210645, 'z1': 31.59567133155078, 'outer': {'kind': 'spline', 'points': [[49.78632745840932, -2.8100241380018507], [49.24787936929322, 4.4440891852596], [47.59767220353737, 11.482895397650372], [43.55660729728722, 17.508322923165895], [38.93760610652638, 23.10689443673273], [34.246532828774846, 28.661586671602716], [28.86901855100328, 33.532741188362806], [23.005732608253844, 37.838357631866266], [16.45400759057126, 40.90338259656619], [9.37114213855494, 42.56566546182013], [2.3500031463506805, 44.412231870089684], [-4.8266489126527725, 44.988904714317506], [-11.776041545335843, 42.85164324865134], [-18.58286537782844, 40.28370464744144], [-25.150803483491295, 37.17712718923447], [-30.716138283704545, 32.534524073103476], [-35.34306633792725, 26.928119596174778], [-39.22975109566161, 20.781365652190793], [-42.56194140105166, 14.319069302968012], [-45.933806241394855, 7.876225060767421], [-48.53473124925913, 1.1160201058401344], [-48.67170953234004, -6.112875809043638], [-47.38705156312938, -13.270614153642253], [-43.99655653021704, -19.492243001202226], [-38.740376240765556, -24.509761798320405], [-34.41193384123482, -30.350839140186835], [-29.30664036896714, -35.528849514117255], [-23.47222996197215, -39.83648905828428], [-16.382785151879055, -41.23599448759665], [-9.131992467937152, -41.84354028742309], [-1.8893348746818783, -42.5402494538606], [5.357601549118696, -43.18650906213349], [12.603365710502272, -43.42263377139925], [19.465656212754666, -41.1169332473267], [26.025483772173825, -37.98964878839103], [31.53490229665456, -33.276674753799405], [35.9926441617059, -27.548040987122416], [39.86524578050826, -21.388285955051952], [44.22472855795592, -15.57004095078359], [48.73876247625922, -9.954738953006656]]}, 'holes': [{'kind': 'spline', 'points': [[45.91969542264833, -3.720101811014969], [45.5115329692262, 2.81250223148702], [44.02515575378488, 9.17844730975142], [40.25530721249185, 14.515604698504859], [36.06607206754314, 19.533945628682833], [31.769294252605835, 24.472677369498722], [27.028972038300303, 28.986382541630274], [21.78429279732971, 32.922885577398844], [16.087987877271154, 36.057996709610194], [9.792361994326116, 37.883235546254895], [3.39801605504435, 39.324468302770185], [-3.0559226840900164, 39.993177453407974], [-9.405943020124969, 38.443415246046726], [-15.639025164029265, 36.412102099765384], [-21.64497522596929, 33.8414831671044], [-26.833341177332684, 29.861228811816876], [-31.106555016119277, 24.89906412497897], [-34.82008377331403, 19.49529916535539], [-37.902541511939454, 13.715670696738213], [-40.98568123876256, 7.936162517481629], [-43.630143627033796, 1.9854280398333677], [-44.34297870681198, -4.475522428546727], [-43.34444662078137, -10.954597066527061], [-40.440387045133676, -16.630418620516433], [-35.745143881325646, -21.204017840706207], [-31.43466764174477, -26.144486307524822], [-27.151184339014755, -31.109515807659307], [-21.99654771491778, -35.10196771069891], [-15.700938012815183, -36.68622459374523], [-9.1663175875904, -37.23828011411466], [-2.6436920647444175, -37.89138832158296], [3.8944730811753754, -38.38587529059937], [10.436976618886723, -38.765050299222196], [16.749615343017545, -37.15277039033221], [22.735449358302684, -34.49093206964774], [27.7795431673127, -30.350654112737878], [31.924605812259486, -25.27644898203795], [35.496985783050924, -19.781414887153872], [39.33637731010252, -14.478663078745242], [43.9082813213997, -9.790911827271064]]}]}], 'center': [-0.015105179999999996, -0.463750415, -0.16253276500000002], 'construction_scale': 315.03848163549327, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
