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
                secs=feature['sections']; body=loft([wire(s['outer'],s['z']) for s in secs])
                for hi in range(len(secs[0]['holes'])):
                    tool=loft([wire(s['holes'][hi],s['z']) for s in secs])
                    body=body.cut(tool)
            else: raise ValueError(spec['method'])
            parts.append(body)
        body=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
        if spec['method']=='tracked_smooth_loft':
            if len(parts)>1:
                body=parts[0].fuse(*parts[1:]).clean()
            for track in spec.get('hole_tracks',[]):
                tool=loft([wire(s['outer'],s['z']) for s in track])
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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.9999760334475499, -0.0069233323265887586], [0.9999855929918708, 3.716340625238447e-05, -0.005367720892284524], [0.005367849541132096, -0.006923232582083649, 0.9999616267847072]], 'axis_rank': 0, 'features': [{'z0': -22.588140341502594, 'z1': 22.471873284641774, 'outer': {'kind': 'spline', 'points': [[49.30595720255582, -6.436098379058824], [48.50142186620046, -1.5481251488356826], [46.172955794131624, 2.823284111047517], [42.53588385269384, 6.182459026217335], [38.01495235151321, 8.208346121699973], [33.07847347833577, 8.691651866072002], [28.246722029845746, 7.5805558075735755], [23.82547487083227, 5.313319642043138], [19.530063595149635, 2.8017210619466395], [15.228597136320557, 0.3066102606102043], [10.90872156547918, -2.1621820771747515], [6.660310513225999, -4.751649551266343], [2.422715265002511, -7.359832450125749], [-1.8312872961375406, -9.939307409931057], [-6.085115019250264, -12.519681179534466], [-10.333695206900874, -15.10841594861651], [-14.566237196900351, -17.72433464987763], [-18.670797698840484, -20.531167729134754], [-22.20852843053289, -24.009359981031487], [-24.61147547872024, -28.3387730347202], [-25.34487358264035, -33.2374193075575], [-24.54808182974409, -38.12095414607684], [-22.271831948916862, -42.52213572537695], [-18.712145872283244, -45.96201178173273], [-14.170772353853522, -47.92397668776959], [-9.2453955876748, -48.37016772963514], [-4.455584186475309, -47.11351821543764], [-0.04977630788936316, -44.806562180194994], [4.241789412938161, -42.287987704662754], [8.479128700065006, -39.679855751470065], [12.696167943806937, -37.038354800987804], [16.98239452427807, -34.511403759136265], [21.21723027117461, -31.89902738137125], [25.45204886624509, -29.288832905199065], [29.74881159142232, -26.779399465191467], [34.009493963115396, -24.210653583712237], [38.28427119791764, -21.665812575591836], [42.50203091128707, -19.03411726622258], [46.12020934659098, -15.63659874041429], [48.53686843797296, -11.31871464458476]]}, 'holes': [{'kind': 'spline', 'points': [[48.08678485770011, -4.945767990232903], [46.80341438360927, -0.35275961701010095], [44.05517254949731, 3.5502487769563706], [40.11954389849482, 6.245258800505341], [35.508394535488726, 7.490980481932842], [30.747348693968217, 7.176251730498209], [26.28864360499644, 5.4414410767220955], [22.144995812689636, 3.017645328063994], [17.98069817223218, 0.6294343528690197], [13.829290377691201, -1.7807022088270108], [9.686613885243588, -4.206160845919623], [5.599611110791168, -6.7246106091321955], [1.5077030495952806, -9.23386075040048], [-2.5821992240396976, -11.746113257669604], [-6.700101036898699, -14.213109409726117], [-10.807445961888538, -16.697972325247417], [-14.884914156636807, -19.23148919955153], [-18.775834822439307, -22.03895506039846], [-22.00754490587813, -25.570069246254658], [-23.878044624557816, -29.953724335934652], [-24.175853540620576, -34.72544340330148], [-22.86508289062727, -39.32098032379194], [-20.169296180404558, -43.258643157481494], [-16.289228382011167, -46.03154705870772], [-11.669848885231874, -47.27303446909867], [-6.923721824941334, -46.78904483687816], [-2.5283414846727084, -44.89781368435108], [1.6447036105013781, -42.52487433942961], [5.771946691653858, -40.07311055301074], [9.837763524718735, -37.52084634961875], [13.936485924460989, -35.02362588788116], [18.043182975833798, -32.53784350170494], [22.110642296891502, -29.98824299220648], [26.22631817394435, -27.519167431121407], [30.36518680575343, -25.09216012113333], [34.487928262876586, -22.632479494498007], [38.61622069128756, -20.182238688642492], [42.6081856130806, -17.52791324534338], [45.890383450037966, -14.048422724303636], [47.84551975892688, -9.707006292895116]]}]}, {'z0': -22.588140341502594, 'z1': 22.471873284641774, 'outer': {'kind': 'spline', 'points': [[25.114967533829876, 31.305745366615096], [24.751847098906772, 36.22522373850911], [22.827331834370742, 40.77847963845801], [19.640617930741985, 44.55706838292709], [15.503621407098949, 47.24445259906071], [10.679143785376063, 48.29443582551579], [5.788968108164917, 47.50891915814955], [1.2851246906701734, 45.43614264623571], [-3.0432137370698378, 42.99945526721723], [-7.286844902768404, 40.41841332225488], [-11.507526861737745, 37.7994700882222], [-15.743462696301915, 35.20547495428242], [-19.97796019360461, 32.60956867546623], [-24.22278902547944, 30.031795143569198], [-28.496767937255843, 27.502963606921924], [-32.76115300629253, 24.958494795211514], [-36.98987277664159, 22.354394517960976], [-41.25214419379916, 19.80468837180666], [-45.11697953241816, 16.701838250902327], [-47.88681920930874, 12.614253830133658], [-49.227489263539525, 7.8607600529168735], [-48.99150625109424, 2.9287238721479496], [-47.153269196144876, -1.6547219243106028], [-43.9471243033024, -5.413698862936292], [-39.68746808281137, -7.9242020856581386], [-34.832522906836445, -8.872839321362433], [-29.943671743858452, -8.174650630366665], [-25.38117691143544, -6.244544149834089], [-21.08028124873366, -3.760447676476793], [-16.79657094322755, -1.2484646959955197], [-12.494543362998028, 1.2345688800702188], [-8.203258569187497, 3.733821614277842], [-3.9779720778929555, 6.3441664666471915], [0.2738548121803058, 8.908891439038127], [4.543987905135731, 11.445675061270986], [8.791199069892713, 14.020211814535571], [13.000454092237602, 16.656636094573944], [17.197141499250886, 19.309412947694497], [21.016239013296637, 22.474753771885773], [23.85296160578558, 26.530843486950854]]}, 'holes': [{'kind': 'spline', 'points': [[24.02951629004116, 31.72673921619064], [23.52727102403561, 36.46150864546013], [21.49519795555907, 40.77362626255785], [18.276307600331563, 44.294420915698915], [14.088868558200774, 46.548094239998925], [9.373024058276277, 47.06389795370534], [4.730256681641793, 45.948735455949866], [0.491339166606139, 43.724436715967244], [-3.665555012948595, 41.34145438283664], [-7.742337170325683, 38.8248101431625], [-11.823545617311819, 36.31476047800923], [-15.90421520517549, 33.804243289561605], [-19.98965976614662, 31.299881617007326], [-24.07413291675895, 28.79928203254471], [-28.201274180484308, 26.364583997710206], [-32.31333760507468, 23.90724903294947], [-36.41599223369947, 21.431634390894438], [-40.514429604543245, 18.94943893560038], [-44.24587198970426, 15.967514477809434], [-46.926946158333074, 12.040320938114732], [-48.14499354095211, 7.435855896452674], [-47.81311594375896, 2.6868495531244596], [-45.86405647494017, -1.662226380790907], [-42.55557370014675, -5.097427917985213], [-38.27607617548395, -7.1852678530911716], [-33.538800656072794, -7.765537642713444], [-28.894667667199027, -6.6621583782353975], [-24.61542536419578, -4.528290878953787], [-20.460979830988915, -2.140817449242265], [-16.326759820630418, 0.28106701660312394], [-12.173923055863629, 2.6714593001718625], [-8.049575784851458, 5.107959004721738], [-3.9918914705999415, 7.656735990190996], [0.13255747337869386, 10.095510080740338], [4.233287930549556, 12.574113174676206], [8.334704302082262, 15.052175926974613], [12.394299181821077, 17.59767452265169], [16.45253777090502, 20.143338210508645], [20.142050872423887, 23.1897000936386], [22.88042595321877, 27.102554471477852]]}]}], 'center': [-0.007991639999999994, 0.0014250900000000177, -0.803602675], 'construction_scale': 113.62732509913984, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
