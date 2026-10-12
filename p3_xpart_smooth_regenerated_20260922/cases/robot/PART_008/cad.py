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

PARAMETERS = {'method': 'spline_revolve', 'basis': [[0.0, 0.0, -1.0], [-0.0, 1.0, 0.0], [1.0, 0.0, 0.0]], 'axis_xy': [-0.23771417686765983, 0.3977171987001934], 'profile': [[0.9784877975313532, -46.42070879932517], [2.8666754338549545, -46.316724180484485], [4.772332239017444, -46.10521878339248], [6.669378674585324, -45.82177006110135], [8.556478606758498, -45.49324848837725], [10.436088207903165, -45.11459577661222], [12.303774718196522, -44.65595299743048], [14.154610662836847, -44.16873199031218], [15.990366705416953, -43.62759229231068], [17.794584793093627, -42.995532660002596], [19.567133896940845, -42.288413025713396], [21.31470912171261, -41.48978496362426], [23.032733486225666, -40.614637455222606], [24.730941135797046, -39.6788697771595], [26.399079969488007, -38.696646334508], [28.035573372849846, -37.6569348747895], [29.625314376013677, -36.545154142956335], [31.164827498233016, -35.390741786721605], [32.640513373153006, -34.171336349535984], [34.0438193177775, -32.891806291622196], [35.40450544488209, -31.576437023368406], [36.720749135176135, -30.210276489310896], [37.9910267117062, -28.784084598729148], [39.21343463407784, -27.3158112195673], [40.38025102904187, -25.805943248084777], [41.48730466782554, -24.261143922941343], [42.46084507816615, -22.66990658151778], [43.41877249319403, -21.030747213496454], [44.334075366882175, -19.336559298108035], [45.15860144214549, -17.58412559225237], [45.90641454131093, -15.809152359855116], [46.536077017259885, -14.004334286104857], [47.136997653031926, -12.192684998057963], [47.72633009423809, -10.373900504188072], [48.25181757142229, -8.532425378031506], [48.682674706696105, -6.669305065454308], [49.05051974289095, -4.802112991147414], [49.35065025177005, -2.9043660553423107], [49.613270741391474, -0.985236747358005], [49.8001670731546, 0.929876878754576], [49.88577882001076, 2.84938146596626], [49.879060404743754, 4.763615540571248], [49.786333993159815, 6.671417629237771], [49.61857536094276, 8.574248935476446], [49.36294523980557, 10.472894455202976], [49.045062551008996, 12.361077898715688], [48.64318010771429, 14.235914332736623], [48.17461854369675, 16.09181108745454], [47.654237209714054, 17.936228136586422], [47.04007052776578, 19.754422677123777], [46.37552112897076, 21.547214627771957], [45.65753640907212, 23.313559018977564], [44.853397528887506, 25.04502842028461], [43.96460827356417, 26.740113999972586], [42.99787953355772, 28.383009440686447], [41.92201711762765, 29.972873426387636], [40.77121897427534, 31.50175522304059], [39.531309338956795, 32.963648795790704], [38.216108607389586, 34.374415131822964], [36.83170205243889, 35.71700112135206], [35.38966802774104, 36.98682454268902], [33.86225265411218, 38.13511966121519], [32.27005108219424, 39.207723217854294], [30.61863023575646, 40.1809017130216], [28.922757887166284, 41.05392472167853], [27.178392318192408, 41.8800096338816], [25.387747947205213, 42.6300352764236], [23.581066381027856, 43.301715140820185], [21.76507139418993, 43.87166330035046], [19.93439226989019, 44.345086912062996], [18.080575571892165, 44.78602403215865], [16.206792685112188, 45.170958832014534], [14.314781643716591, 45.47680913161505], [12.41545826953581, 45.75083934215988], [10.510208098422527, 45.977045829461346], [8.602675003782915, 46.164966170765084], [6.694282948419071, 46.32232868904009], [4.783521006415578, 46.453205531945166], [2.8710188960037826, 46.53727321719029], [0.979070421998764, 46.59110039880395]], 'breaks': [0, 9, 19, 29, 39, 49, 59, 69, 79], 'center': [-0.42850826, 0.150718675, -0.026799165], 'construction_scale': 536.6544372064667, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
