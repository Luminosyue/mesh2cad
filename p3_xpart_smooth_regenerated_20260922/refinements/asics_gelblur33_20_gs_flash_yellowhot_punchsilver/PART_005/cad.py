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
    from OCP.Approx import Approx_ChordLength
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
    fit=GeomAPI_PointsToBSplineSurface();fit.Interpolate(arr,Approx_ChordLength,True)
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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[-0.9999557440141841, 0.0, 0.009407976033109096], [-4.2916394597015044e-05, 0.9999895953777224, -0.00456150134084497], [-0.009407878146672074, -0.004561703223518127, -0.9999453398523732]], 'axis_rank': 0, 'features': [{'z0': -16.168774653533177, 'z1': 16.279448263399455, 'outer': {'kind': 'spline', 'points': [[31.930854900672557, -29.721554845226393], [29.065483225067997, -22.093078903221897], [26.23480297381056, -14.451063326542426], [23.412984760803052, -6.811742683497325], [20.92191830986128, 0.9475095385795009], [17.967714914623407, 8.542594974389184], [14.759229604998412, 16.02750615104115], [11.604702927050164, 23.523891880177334], [8.315047814365204, 30.97735525075407], [5.342716473365814, 38.544432920351504], [11.476607348222965, 42.49195638484516], [12.31768948226759, 44.820751919907316], [4.483333356278681, 42.59757249089856], [-3.3522435562390647, 40.60706294319902], [-10.620805011371111, 38.364126395375884], [-17.18687574862361, 33.546657957721045], [-23.17677240635773, 28.08438860258465], [-21.174801662202736, 25.095245262831828], [-13.303365891210342, 27.13102450559365], [-5.202931274817005, 27.128932217675423], [-2.893289866490159, 25.345300191599986], [-10.650019599120393, 22.885543681158264], [-18.62054500732542, 21.228077630506604], [-26.526528196137864, 19.25290392443827], [-34.11303743324851, 16.330215001168288], [-36.03875262673683, 9.23750693227846], [-34.55808499784954, 1.2246012566848485], [-34.189224850470254, -6.894446801487195], [-33.115913645566906, -14.685150607954549], [-29.74221561781914, -22.102891210454093], [-26.488821629165518, -29.574963312356278], [-23.411912076121727, -37.11549390801351], [-19.88348231275693, -44.46192807553488], [-14.489581933891968, -49.230084372891476], [-6.459866874054466, -48.01720170042118], [1.5329576600945134, -46.61381726489188], [9.233265366736735, -47.48432151670341], [16.91942473781141, -44.904992640897575], [21.95857554009344, -38.67269184624286], [28.92898899371245, -34.49952834096208]]}, 'holes': [{'kind': 'polygon', 'points': [[-15.953922859562832, -37.93460798202466], [-16.798085333607666, -38.736396408254116], [-16.407401300159083, -39.60544200099974], [-15.681365368663702, -40.34294016096354], [-14.935993270531123, -40.8824924030872], [-13.345635226769165, -41.43779096615441], [-12.535451218255647, -41.436707529700165], [-10.147687351204254, -40.73825343372468], [-9.479080940915972, -40.29671859802198], [-7.626587980552547, -39.55711294059091], [-4.551296303276547, -39.115016635797254], [-2.850934922468054, -38.65171977044539], [-0.5477108682427358, -38.356814162580235], [1.031529518216281, -37.79032966145221], [2.644086260920256, -37.56103459760344], [3.786008838749423, -37.115765197943155], [5.042537923779455, -36.83516464011566], [7.559653634493163, -35.54546736004399], [10.638888740374474, -34.27453427518266], [12.237841160361848, -33.43284225476006], [14.555025654227828, -31.54359942047523], [13.82991311371998, -30.84920726243548], [13.037217565474503, -30.667647293202574], [12.100701890733758, -30.64280371919923], [1.1505514003242814, -32.38576133761059], [-1.353582953556291, -32.96989293340761], [-8.54894116419419, -35.09131502201301], [-14.130964982974033, -37.13986987461069]]}, {'kind': 'polygon', 'points': [[-4.249599959999399, 1.8952835187080679], [0.794897896989664, -5.960645530802721], [1.4809850177751214, -7.559580756819028], [1.3660473869627612, -9.158515172286302], [0.49884294987109506, -10.757450398302609], [-0.5577238221316676, -11.726685087447304], [-1.354479894927178, -12.071080619744368], [-2.153982929677241, -11.866907462533485], [-2.95597268595429, -11.302287028468331], [-5.2645232615133155, -8.874377110868515], [-6.891330259774623, -6.743486570741935], [-8.36868710773686, -4.254282803223773], [-8.655498278562103, -3.5622447181508425], [-9.235039234517634, -1.163843094949934], [-9.644223534854332, 1.8865867594293415], [-9.565140080438503, 4.274837642178356], [-9.172397234183954, 6.0311121738742735], [-8.550728268781699, 6.548378018707392], [-7.754728091409698, 6.171431047618954], [-6.152160848160816, 4.577082014398502]]}, {'kind': 'polygon', 'points': [[9.837573665859722, 8.15032372975972], [7.439078986986149, 8.407844163129434], [2.642124683139742, 8.143899085050824], [1.3716092269875073, 8.429765018951775], [1.8490801623350228, 9.228512336008972], [5.2056063001674735, 10.02870024496808], [11.436640806036312, 11.282652863913636], [12.235922219878667, 11.278638674513479], [12.94786124020551, 10.829003327687348], [12.962934254987385, 10.02732095241227], [12.222677448903635, 9.033795687610432], [11.436544180996083, 8.570397197729193], [10.639488740759047, 8.310834737663257]]}]}, {'z0': -16.168774653533177, 'z1': 16.279448263399455, 'outer': {'kind': 'polygon', 'points': [[28.623419500749684, 26.337393850000215], [30.89593745369671, 27.537490780780246], [31.42307421357596, 27.890801958091405], [31.857938470992707, 28.414591995388093], [32.20999852072394, 29.223592686705782], [32.047677470855604, 30.013077754230345], [31.42324720933514, 30.73871988178564], [30.627102330992642, 30.689975897820382], [26.615745957266842, 29.69642244731051], [20.485068536999737, 27.89636958808384], [18.631193418281693, 27.21096034255219], [16.346539049857128, 26.018046020738876], [14.195132349492631, 24.428218246470344], [13.720533613442136, 23.62586581652523], [13.586606963640019, 22.820176379255297], [13.834439115174531, 22.28698056459259], [14.633950986299542, 21.876919098993746], [15.43338378896993, 21.72418611896471], [19.430930926552858, 21.543533656074583], [20.23126330310254, 21.783368913218652], [21.182339724286262, 22.8201763792553], [22.125190261790756, 23.61964439753797]]}, 'holes': []}, {'z0': -16.168774653533177, 'z1': 16.279448263399455, 'outer': {'kind': 'polygon', 'points': [[1.0424660218024018, 49.66644051200244], [-6.1294088879890944, 46.08034481020862], [-7.388712553434276, 45.2052622485423], [-9.134330078773226, 43.60632702252598], [-8.947657705816665, 43.27663769150267], [-8.55913982703892, 42.88034989112799], [-6.466697236841257, 42.00739260705872], [-6.1537571522542445, 41.77110687146738], [-5.354263797409841, 41.79247636190555], [-4.554781098963108, 42.08102735190405], [-2.2391859301966246, 43.60873260314086], [-1.6199320405814814, 43.78011937526675], [-0.5573892999519618, 43.934803768620824], [0.48601144310668054, 43.92579294644461], [1.0416025649935772, 43.85742481722534], [1.8492426957764523, 43.53940345984962], [2.640609622046087, 43.444954948635804], [2.797298463260741, 43.60632702252598], [3.0713920326215653, 44.40579423025962], [3.028135018004459, 46.004729456275925], [2.46236391564188, 48.40313026892781], [1.839237125644929, 49.86823012427545]]}, 'holes': []}, {'z0': -16.168774653533177, 'z1': 16.279448263399455, 'outer': {'kind': 'polygon', 'points': [[20.818567101998408, 14.8255034913699], [21.27152442078414, 16.424563633711475], [21.82645965420015, 17.26687692634689], [22.629081003743444, 17.512869139791785], [23.428573156023155, 17.56225849283504], [25.01018764545432, 17.202797158064758], [25.683062753319884, 16.426780116106922], [25.88329449219398, 15.59439560326979], [23.4775931877611, 14.83186313855063], [21.82971403886232, 14.584375466739075], [21.030215293240165, 14.669725066285658]]}, 'holes': []}, {'z0': -16.168774653533177, 'z1': 16.279448263399455, 'outer': {'kind': 'polygon', 'points': [[34.472970305432355, -37.82446314356291], [34.34685896375843, -38.73880834282313], [34.49549221017846, -39.53600007242294], [35.42346508429357, -40.1340544353935], [35.65887081550687, -39.53494984009459], [35.42339544178429, -38.5113778840201], [34.62294245713461, -37.538249550992546]]}, 'holes': []}], 'center': [-0.016710049999999976, -0.380169445, -0.009774035], 'construction_scale': 81.05406006717, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
