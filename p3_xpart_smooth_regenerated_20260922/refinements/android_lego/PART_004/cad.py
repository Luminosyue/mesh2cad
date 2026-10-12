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

PARAMETERS = {'method': 'profile_extrude', 'basis': [[0.0, -0.9999493393807907, 0.01006571765550314], [0.999993311486164, -3.681491742962288e-05, -0.0036572705119523484], [0.003657455800927954, 0.010065650330811332, 0.999942651205799]], 'axis_rank': 0, 'features': [{'z0': -50.180726226933125, 'z1': 49.98885216583253, 'outer': {'kind': 'polygon', 'points': [[26.893615188657172, -1.9391854820678742], [26.238553415664573, -5.806993601519179], [25.185256394019913, -6.6128956024165975], [24.831219201963016, -9.033845159411124], [23.577236056295774, -12.58117319983306], [22.691372115108027, -14.029636350141294], [21.19906719136701, -16.128501240254995], [19.144051732036782, -18.474585750520347], [17.908596415156484, -19.675829280676933], [15.209993791053996, -21.91522486554448], [12.049279819266483, -23.80234200129649], [11.001743781563793, -24.081246260357958], [8.50183810073786, -25.04932592068103], [5.9558623507918105, -25.378375930837095], [4.954386696539399, -25.93554155897106], [2.930978943822064, -26.224365532569706], [2.208784753464112, -26.770488958020174], [1.4069385290798195, -26.909671964702994], [-2.865943204028736, -26.770488958020174], [-5.688058638244446, -26.119170776605774], [-6.564398521382117, -25.612864752830326], [-9.235594730482424, -24.70513002201019], [-10.071673586684, -24.258492649783594], [-12.783164471360784, -22.3771408446473], [-15.88698320033718, -19.973752060078994], [-19.89176091905805, -16.128501240254995], [-21.921515571430465, -12.581173199833062], [-22.668211861231327, -9.689793637305899], [-23.426109433147953, -9.087828895653201], [-24.380461791739705, -5.486513522489809], [-24.697159718107898, -1.3342190680454125], [-24.540294868649042, 2.2017551685142314], [-24.11707513043519, 5.155467002276619], [-23.42671181265842, 7.2737178796143835], [-22.072246087143245, 9.295307881678553], [-21.205230056038754, 12.250123083120492], [-19.88632473794656, 14.28037153702241], [-18.769375294857877, 15.797454720041804], [-15.745463776512612, 19.344782760463744], [-12.650153724972174, 21.51459188561176], [-9.23736019087561, 23.247468465890094], [-6.385385741486959, 24.326845397367368], [-2.8714899898550135, 24.819465204688207], [-2.1424610333264114, 25.119062338010036], [0.5965322891595243, 25.00857336200961], [1.4050191864020065, 25.22260420821806], [3.698248177120097, 25.297880197984828], [4.952505281163592, 25.16657121191241], [5.768590706091664, 24.80346461857663], [8.50000092771193, 24.85109711076332], [12.047526952630207, 23.808190830013665], [13.22637648019331, 23.297909794842848], [14.02594447854948, 22.892110800885668], [19.142653580867393, 19.50133368105599], [21.667534151335456, 15.797454720041804], [22.69032059717958, 14.531195272217385], [23.866933063445863, 12.250123083120492], [24.59578807990976, 9.763349360500932], [24.88571716386591, 6.2318554949841305], [25.367676465130813, 5.459318684623688], [26.23816386845319, 4.773703134446519], [26.880898307281402, 1.6081425583540616]]}, 'holes': [{'kind': 'polygon', 'points': [[-12.784616161694041, 17.052983981812826], [-9.49159926874562, 19.1922023434826], [-6.397448072172766, 20.961782307805642], [-2.142341784149442, 21.880072709404043], [1.405122674676698, 22.411704737662408], [4.952613141422518, 22.236921977636243], [8.500129635663196, 21.355192737563442], [11.16277186209786, 20.841175020485743], [12.047647275538303, 20.540037025450783], [12.48835486520822, 20.201804930964105], [12.961923119241602, 19.344782760463744], [15.595237109146154, 17.666298652244784], [17.443618203893802, 15.797454720041804], [19.531568190548114, 12.65814247853391], [20.14861781675393, 12.250123083120492], [22.402967969322653, 5.256880934991243], [22.690716749521407, 3.7710931136495396], [23.907289889332613, 2.687643565447943], [24.100613805627898, 1.6081425583540616], [23.95083417786892, -1.9391854820678742], [23.813257752121338, -3.0386840672645103], [23.006066483273898, -3.727827060462043], [22.691010515849506, -4.208048664371159], [22.45239565219944, -5.48651352248981], [21.257626530172853, -9.033845159411124], [19.472550580078114, -12.483661575318179], [16.555931679524775, -16.128501240254995], [15.59651753906449, -17.112131950275522], [12.049126102183203, -19.62715143706643], [9.523437918800836, -21.095624664276244], [8.501707163878187, -21.492880993660226], [4.954253722513304, -22.32376408308499], [1.4067936357397866, -22.974147732613687], [-2.1406932887587184, -22.895577815339916], [-5.688210322666632, -21.999190389585156], [-9.074016722366922, -20.09011279934239], [-12.783344186018098, -17.495816495612466], [-14.328607124745318, -16.128501240254995], [-17.15030361466809, -13.216284337594365], [-17.62525135426471, -12.58117319983306], [-19.262904641674037, -9.274319222770188], [-19.8786828386072, -7.430054385270603], [-21.01043287789338, -6.14618953318768], [-21.618876425988727, -1.9391854820678742], [-21.621282918337368, 1.6081425583540616], [-21.187417769282003, 5.155467002276619], [-20.916242694161387, 5.742128935258047], [-19.879191078571175, 6.374518643873765], [-19.006296942477196, 8.702795042698554], [-18.617216270176133, 9.32995895052624], [-17.30946080521631, 12.250123083120492], [-17.084642591646652, 12.553435042861798], [-16.331952560496596, 13.043046284961612], [-14.059319527426188, 15.797454720041804]]}]}], 'center': [0.192795195, -0.015814835, 0.860731975], 'construction_scale': 359.6475324708673, 'partition_final': True}

if __name__ == "__main__":
    from pathlib import Path
    p=Path(__file__).parent
    shape=build_model(PARAMETERS)
    assert shape.isValid() and shape.Solids()
    shape.exportStep(str(p/"model.step"))
    shape.exportBrep(str(p/"model.brep"))
    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)
