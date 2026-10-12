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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_008.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_008.stl', 'source_sha256': '97a9e90899fa7d1aa5b4dc8ac6db26516bac3c019733f46915b4d0fe14dbaef9', 'input_faces': 48, 'input_vertices': 68, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26229238510131836, -0.26373493671417236, -0.27297988533973694], [-0.08069881796836853, -0.09040671586990356, -0.21712826192378998]]}
GEOMETRY_BASE85 = 'c$}qHYfMx}6rN=Pkru>tt0LfDTI!-*QOjcSLA{DLHl%jbgrqgb?p7Dwb_HChsev}P+7f~d#uvXt_lGGZ@sU^y6cDa!RUWde#Kd>98e5X~htX(Fnl|msnRB-@8=5qFlauevH)p>2X7<j`b(NVDt%N_h<S+9&M>Lrb7B3Pj+2IY;`ZjrM3M#92nn(ul>@o1by7G5iADGAvQfJ@nt=SZ?FIDWzD~jz7#a>Yrs10~3KdcID_A>r0kH5xC`I@bsYA<c)FD`Z{g>xOs=gPA_smw#gV5FZ}s^4>gVer9*QHE~cMc{)~zDo=><kdZGz-zm|KQGp+Ev>-2x0MWv^}%nOx&Fb87a1zbcw{18Kl0mU=<oUhc+%AJlUN_mN3mY(sRLd=I%hzvkLL}2?N=9{zuq(~`cxjh&F2Z+48eMgd66f`8}kOAuIBok_XeeP#qqIqr8+s^GREia9|1n<OylFW-+{Ip{gBhw0i)xM!=k>y>&P4WWGKY<`*@qAqd9zB@2Y<U>eHV_CgR=bM?dv241Aw2Eb8dp<Iq-0(ndr-22YR=q8~Ns81TW=JV{4wDByhQjj-s);5Fn8Kg4_%bX9#zSlWj;-k6sZ?&IrRqmN4S*1gN?TdO6WWcBfJzo+ou0sX}DF+X2z<ojFSJSzD?UPV5(57#VwUl&~EJ_c^X@1{QZ6VTmI8IgSE4+0<TTq*I|yi5GOIsOrUFK!KSoqIO^er)?%_POZ#5MXafMB1OdyMR{@uaAg+^zd5XmAhFHN&m8kpXZdjvc7pCf4?^zl=VLz<L7NnyQJ^lcM^EgyhYZ(;y4HGobz3vqkVP->eHX-ppzfzgmzOE@In7k&bOC#iRaXPwj6l!a~{-3jo<NpTQAf<Z0;5H)%M3dFm7PDN7Pq~KIQGqPkKdttzdsQjJGuQi28c%d%&xUGWtb*?fu<9Li@hIPtw0&<GfAj7xncfKdeV-e5^}4zs&67{@s1jyx)8Y>r}#LbWvZwwFG$LwVspw=l;<Fbz{3iqCT<MfF~V8x~Q)f{rv;zC6<Roed4(WymF{p`k&NJe0PTXX$Zx1T+;36>PT$W6R0GO$@F%t@Ca8UBiUo%#8;!w`M<74=ks5UxzxieH1ZJbm>1G`ogFX4g_zH!kx%0_#Ce!!(y-B(iI{`=3>w+kpN)Mie}l$i8byds%wMK4hwU%otC(k^-gLy5FlS?z;&_I|n6o>78jW;B3+8Dwregn8>`TS5%W*uzC79=+=Pbn8LY|FnhO;m?(J<3ULY$0wB8?R6Pr*Kxze!^ijb(@{Ft?z$DTo=Evzk(@W4ID?e4Xg$7=I>V{sN6;?8mP$$W@%X1aTSW4jS`m6d*3Zd<OmoR>bL;yUI)nR`Y*-8vgreY_ZaZV*E(?*oY%%)5XLNk*h2znJ*%NY-eWR>+T;=_1}s'

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
