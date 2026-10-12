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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_010.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_010.stl', 'source_sha256': '195e77f5b9f03ab541271e2fa51e07849816d8cd05c16e133c78ad39c7ca0bfe', 'input_faces': 114, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.046554502099752426, -0.1914556324481964, -0.14868678152561188], [0.05913810431957245, 0.11808942258358002, 0.14973580837249756]]}
GEOMETRY_BASE85 = 'c$}q}c~BN*9LFC~%mY&d6eMLm5XI{S#S?s2@W?YPZ%r2EB}wE(K(w^l%4@tPkC^dZfik@E0F9A+H<^gC$;uSXtar32OVh^j56#i(d4Bud+T9_isdwf#-|v3*+28Yfjy>j09ow)`C^LQ?+2;=zCF;!?6A{EhS)nJdAZxBCzjsdVOAS~n;^JrO<_VL>r%rFc3fa<_3{U>tyqLjKOk(E1n4VHhrZ=x3FFhyCo0s7cd}MldzK8StdFi<xe%viC-qlm;+r6jsiu50U&3Fm^hv)bDL@noT9U(o{HQCKYSs76(j@5f-i7P3m4+}2uPuWDg>}CzMuQA%I!)I+2$8vrhapms8<AO5>XWE+Gg6k;;H}k7s7N4X%DUS9D^LEj(gDcZL$LYM8=SKTdsxLlSr#wSCFQ@bAm#Dq;?SKlZ$HC?IYKy7;AP3JIP)x@TuDEZP)3G<>RiS=YUM=zUBZ$k#rfe4ZG|Z2G;igKrg|n((jXZTFRFCdxFBf&!tlVs`e->6Ej{V@0xn9w|eAKQS{AA!K#LpV*BA46qGu^e@XW?dkY0GjNuL>^jdY#6lohzepY0mbEGb^YrM}Gf>(Un%t`umN#*Obz_uyv7pN#l%plQD1lnW^u&t@Drd@;kVK^^!ifa|!FEIJk`Uk|wV!b6fY%z_}+Vzk{ng+nu26E;Kqo`=aLK59s>6uA^=X*RXH3t523wJCpC4QBAxk^MKF7)q;_GC{NVa71s7F+m%i_U@O(5o9(?mA6>t{#bKY7qaO9=8%M019g3oT#@5DGlh!%v9946S`meLsqol2;b(HJu_2}DEPguDgIpma3rE<eQ%Io0%Hy)PJ{<>(dN9xgp=0pA?(%}0NHc+1J_dcZgd|>DL<zpYxxDIzFt|VSD)~o2scIwB$<=B(kXg<CfY>aF29O_Sc;Mz%bg0m}M(0odjg~t8mXfHo#zr$zYa?49J&)VHd#kTgIA80;hS6_PGu=Doz>Zxj)SCi{ek7!?N8}GbhZO?u>xRAzGR!R4Rbl#p{zrUx1`f=p(2WP!Q*E#cacNx#|HA@cI?)OW^bHL>K{rS~aE`zf%-}~z0(z5FxSh)f&o6jF`)$I4vic%}r%>0+bS6aEWb_vECPW$JtI#>N@^gE>!JxBZpla5%q_FFF1qklEY#-+L!jQ7+pk;mv5TtB@-qje9crTbI{XDqA}<^M{d_ml#zp3L+a>%Q?2t*4_N>DE2EA2mn6+JtjQsV*}Q8)2+_hwO4IH|vp;-!$GMs~z?952yE<{zdD9#{H3C?9anFw4Y6`)`sYG{o84pjdv@g`u*RnC+-KAs^h4B^~<DUD_37zX6)PWY~t*!y<a_f9NiZtXIc5iJWm=!`(HBKM|U-zzZFg2rQ@^qex+>(=)N$y*{`(qs*RiZr4E%PHeR)03FTi=O!tdw@`wv1#=1<T`$Bcpqa~;|ZsySfBj|q7+YB@K(IgtL`f^Z4eVlnqv)vXhzZR+2*WTpL_EOObS{J2HKrYQcxO#If&4WC@U?KI_*5JBp7|ok}=l4vXg`4f!qVri+F0C4M^l{wGFM(^T-lus}uTLwWx*c5h?(+I9oXv?|{WxysQEr_v>b$tyc>jmyS5f}k4*pVX73FDt&B&8DYZ+aCcPXu}$@K--P8jRi;xrvQ+RFuZ-t}3ydifFc=YK0=KaDrU&h;6q_ffqe_Wb_3>mL!HKI#y0=BM^jPP4`Jaiz<arS4SQ*T1X9;%gTJ`5TZ&Q~vdznQr;?7f}36t^d<MtKYx-^pETJe?R?a@*0Nl7!U0ZKY>RqkLRI@@Xz2l71{%SK93Y0v!RLbX*`m6WJ8C;&qkYPpt11Ncnsq4A~Xel43B6YqoG~k7a->>=wSHKXfq8u2!5{ED?FZs_Jdb=i1nNTO@N<+b_&!DKaodY9_dgw{0lsW@t6S}2tSWUGR`OCobVp_ENC+PDB4PlO@{V|e-U%C06H9g7REjX8V&z6k4`+MLI=Q4Le7!Uj_}W6PBNe}{7{TB4%!!9ti9L+Y0xD2Y}7U%ngTEOme^wxpt11NF;|(;Ven&lbmcJ)8Ux>%M?9i4)=T&T9=&)JLPx-RdAN8ig7$`A1YZE{1)qoUc%d%%g*>|P$bt5O&w<Z{M#C>g4f)WX@NIas<<Sn>0lozje;F9(gK$pxraT(*Xa;Qr-wZw&+6q3BM--2i&?n)8(dH>=9K7gX;?W)&4=?%;$N6xa6F!WGc;q#QHimBw9|U~@Ui9A@wF?cjjH3aM04Rfx$C?g>y5Za7To^PIJ_voag@(hoMBh!J4dI`{*dw7)@Qu)aD`<$tH^y;e^c#Y)L|{BZo4}`zZ4eOJ@Spw?`unHSpsjxpIj^+8POMix;<^5MxulK_Y-~(k0BzD>Q5pLa&95X#'

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
