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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_008.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_008.stl', 'source_sha256': 'f65a881e3e90fd37eee9d6aa6f0eccdd53893aa139c28b87ff572d05d26b7c7a', 'input_faces': 124, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11800524592399597, -0.138811856508255, -0.4999975264072418], [0.11668876558542252, 0.14707815647125244, 0.4999997615814209]]}
GEOMETRY_BASE85 = 'c$}q}dr%cs9LHA?pO6x!B&nO4R}mFdj7YhcL|zx{`pUQN1ui~PKtLEmam~iGaw;9QrfIs9F-?CsBc*x82a69%f$*7W8dn`nYfQzlrqO}U<GXlvU1yrQ%y+(DKAij8vuDr#b_bU;phHiIf1Z~H{pswjb(18jAgQNR>?tT(oaHGTk(*!IPU^up{ph}V()0}1taehdRA$Te6lN9J;$+*noLF0=Y|F_jC@OI0F32m$_E4VWURvlOyl{~_-$Q;M5<My^QXV}tQeGwh$4^%>1$A4@!D{0E1y0RQ{a$HPwZOeW(;4^X*ENb<E-zx-(Y)iLo$+YK)gMEvd7U+=1Mc)OF5SDy#>-o89bolSN_SFsxUbe#3tR>F&)j`X<kIFC#-(|6$2q^r$M@UxHT!*X<#!_2Qr1?o<9PZu7{-Ik)5^XVxnfV{+;h8L<PLEEw68G!8sq*=%fDrRciL)2uGXyH&3Jl=fos>N?qZ&C9{e&N|3yd*8(+2Zgvh0m%Rcsd>h`0YU*g9d`$;vM@A>UNiCh7f4<9?l#%<wTeG+ep=ht&@^a+tm;7W4LQIUInYxc3f?;U6uFN1rNCu5%H`Fw6qVdo|NKJF49&$&aZW?W0^c2wljY9He&>gZfW9q;|tCM*6}{Xf93M6I=p^}+qCGxv*Jy@l~-s?Jz(?cDCOBA3Cv&4(_E+}oPK>$J8uiCjx-(b&A+C~YwCrU#6xD+7Ko92eYidc9#j%Dvwhmy_-uF|6Bwa!p(}dFx4DXZ<ohe_uGRmo=B(|C?PuZNu3bcD%cHe=+bgy$-SaHm|f%<lf;Cj4RIIT9G>*lrrvD`y8+f+`r^wKE9->UgXk>)4cwjD7K!;#tP1BqBQZkt8X6jiR&!4K4j~xme=fIf4@<~?~D5_Y`iyTOQqF1>)gD~sykt))jG8Cwsk0D>)=;Hc3NI{ornKrn2+CgWe2OX@ADe*KJxl5aBk{XIyd(#otyiW&dvQw=jML<sJ^k^>fGFKy}na?o~Az5#?goUi+*hoxw$_pzT=FW`=`#${ZsKB;`2B4ADx@~kIo<KpT4RcmiG&|xgWNTH}yk#PXS-&tw#*~O8e-Y3akCo#<72tyj5)fXxq{%toD!2<%&+4VLvxVHXpPYuXAOB-EzEnK5g7IA0;TM!fsJt=Tcmt;eJ$t*D-FcFNcTjw5p?XbyJw3j(>3fZ`k+8NAl;OGrE@ZfsCttue0&~+>LzQhArI1>Q!Fl=Ue_RyRUVw-fCc6JC)7uYe!@r<I>0xtWU^lw?>i64fSk4JJvQb?u|XX$7=pMS8Tlu^Y<oi-^b7EQ{#Chf4R?cJyRO___tjAd32|iubb;M>zB$01MoaL$mXwexgm&;&kw9K@XW4!e94FPBA3ABl{Xs<{Ouct^=aepsfP8GT;~pm^H&~bG>Kff7RLF+3idqGxxA;0-(OnjDJ$;ZZ#yY+?Xx`IhpS3Y7{<pe<IlSb7ukD`!}T-cYH_*YeL!(F9kALzIydhhFSruBu8NJv`Rd%fPjqhBCoaR=zdLjIRaZwcbD}Qf?LWsYy!unfP77}R>c4o*zkKx{^M7CcUnFyQm1rzP^Cb9m<VncW;4_iwCxECOM00zH<_>fl(zPWjhA%)aMqYvOQK&(EBr^38$kc};Q;!sm8!0{d&^(N2C{ZZUvk=Ws6ZIgXmnwoNoG62+4@7f6i01wf&4VDCUw~*H1JN8q_XW{lwhg#w9stoi5Tbb$JO+6bax6RpITqPPw3H~DC<mf>3EYjm1bIGu7V_&v^N1EhG%tc^UI@{=45GOZqInK{KJt9jp99f6mne@YpC}iic{xP02VR6+0MCLKA!i|H!sjAqBF~1;LZ<#2@@(W8@F~bMkf*|3$WxIg!!wYn$01KfehH#^G(>YWJOcSScwcw~avJImfrldxLAJsBAde@a|1EeK-UXQ+%Za)X$j?AD_l74U)7}+`dV#1#b0Se^qH*x9$Z42UI#CEwDp43b1vw147d#y~9pCMRTC`?7JP0`+*#Yl}>_AR{cS24;w!;IFClUn{CBdIUPC|YK-W{2)-vq2-XPkd`C=p|VQ8xsdi1SXzd8WZrk<*Yfpj2F+RD3rMo`jr)<HW%ekrT0AaqxKLc&tktJOMcYYe2Kh*{*%hfG7Pc>d{A~jnnXtDf2gtk1_F^Eu>c4L(Sz3WRJ4;<cHqe8)%o6{sCh+-e>'

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
