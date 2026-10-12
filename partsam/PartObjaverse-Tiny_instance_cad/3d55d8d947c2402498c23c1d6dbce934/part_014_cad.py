"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_014.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_014.stl', 'source_sha256': '91e88f9ea533fa628dd00d9da25b09d2cc9ff1ae6cfcac4bf9912aafc78ad541', 'input_faces': 182, 'input_vertices': 148, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1205979436635971, -0.462395578622818, -0.31060129404067993], [0.4189116358757019, -0.09065628051757812, -0.15881149470806122]]}
GEOMETRY_BASE85 = 'c$}qJU2GIp6rPrXfCUj3tVMBw!tzu3Ex01KD^#qsK!pMYD(phHP{6Wmu?PqbKVp>%g~os}AuB;1j4vf7MWSUTB8ngoq9rI1RAS<TCO-1yJ;QgeXU|*{qm!I`KmGRP%$<{FXDiFQ<pi9&*AQn>>(=IIU&o=!bplRPJh`!cWxR20Lt=B5)6eti(%3d<!R*S#Sx%F)HB=jKT$v0_4Th%Gg+qnGP~H0E#$>Ev`TAsSocx)wb&YZ5H?EE);!2O4P!ui<P8wAh+!p+gS8p{!ddH8Qrxm8woc@k5dgtq_r<w1<zgaaT!;k#5@LTWiBCmaC!QH%5d#l6y{GjdEcz@~Z{@Qoj26Wl-+BfrTD>z}DAHHvX_`dmtZ|0vkqTTy@B%RS;`euIk(UXfZ`b*#RPgfkbo{#WNfB3%h5x%+Kv(t~+`b%HtWq;}Gyj#_9lrZ?w-Yec5zudI?Zt;{1KRssHW$*7Iul<zH=bt)YJAdh$dEm?Qm%cgw-FJ3*&;8@Ft9*Xx>-n{x9)I(SEw6o<cTT)}iQljEQz9RE@B9T@Ui&8B<KpfT+x`gO><@h3{s`aXd*-y1Se~!+&Hcic&sX|p{v*yl&kydpmeF7MuE<9Z=Xcri5%?y5`-20XKX-8Ec?v%z^6BE)U)l27H~E@j2d(ELd{^Xs=OcWx|M5-7N-X;+eOKh=eo9~F<$g-vH;>p)>6`PJyZU{v&#GTP^Y&NYukh0%?|xX=Y0GP0=iRRI<DS3xaOV8NPsx1QxeL}je3^INIr^n7uYF(t<|}8d{o(6;<kR8pw*8d8%**|hzRB;5wA=Pm`mV^!{gl4B->h|>?`(*j<<Cp{X_1daThG|?+Lw7Z*7b=kuYH+!B9l9;^T0RxQ=?DV&R_Z|k(cK$eY5{p*LGO<U-)T}_wB#%P5#i04%_}qKPB^G|D`YUa{s08>o4|S`X+xlangD|!cU95?|g)Bo^SV1r*%JtFY~_r6u!*+_EY%2dE|Zy-{d=QcUt#T_$iV1?Wgc{KKR?)XKd#${j|u-^OwGv|6;*)@>4$_y5Z$Fw4b;6(Ld&Y&i%;JaX;Ad+IK}h_~-B6dvh%7^Nr1So7>NEKV84)y4PRiwXgH(<R$C;(%18AU(PRmSLEgV(wFnd`K9mWD>L3sXLOAJqGvDlO-xlU^>$hpW3Q%U(xuV<YFc0P?_N#A6aVk4=|nZdcvX{t6Ts)Gs#G-vSOi`KJsJ2s<MW^i=QBP9n(%SPi=d0pgLs3gb*kn7E5IwDX9HhkyaAeUJ>zqr3Fk6i0bPL}#J8(@Mb!#m6g&zY18!q{J2c^|jIV$uT*-J8I*J~|*Qi>pY8J2zybSs|U_Ik&pb6J9J`0+#obfW~GV~x`r>a)fOkgQ^DfBbIIOBEDgsT{z2~GGc<E7B0=s|pos+UzQ1J;1oK)(Ro%=i{)!mW%igC<<gcnx$7dJx~K%2kyFCcqQW8-P0)-w92)i}55hVI$)S=mdHYZ&I~U)e>Mecs2B5;7g1*K@)Cbd<it+QpT&HtI>n_SXG6p@_~8adC(65A7gwhG~qbL^Pvd`F`fsVhaSYItBR-^0W1J7fF2Hfn(^t-gfkc)0ZkZUya2iYJ%}$<Ri$bwFbp1sege3F@rBTYix{5@P530^VdyY=5HD6WP1R6f5IhJy1o#x=#n6N$j1Pq-9L9JMI*1;`={Loms<MF&xC5O9?8SI*Xu^9L&xR)K#<&CRpa=2(s`{zw0n7o<f$k2xpYi_Cgby&@1Dfz2#&e)^(1ZABRU=gm1O~tZ&;x*@7#|HyIEL|o(1Z^%9)J#@2l2tG9#+*Cm<yf@-3Ryx<Ab3IA7#8RG~s=W=R)VA2l4%?-cq#>*aF@Hy&L!%<NKirUuS$DG~ph`TcBIegLs>&1F8-JTftkQn}KgI-Udy$m+^zpgl{t53f+nx#4F3QvIE`z=_mfbFP9cE;|G8F$;_``{F6siFY{%rvb;O(np*U1@1ON8dfLukp_;?9'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
