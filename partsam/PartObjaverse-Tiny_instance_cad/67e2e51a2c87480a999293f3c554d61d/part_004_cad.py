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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_004.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_004.stl', 'source_sha256': '96b1334d7788193a18b0893ef943ed91e94de98e925cbf69918f7d392512b1a8', 'input_faces': 344, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18375998735427856, -0.4999999701976776, -0.3272606432437897], [0.18630145490169525, 0.4999982714653015, 0.20682066679000854]]}
GEOMETRY_BASE85 = 'c$}r02UHc;zQzZ84Mc^gF>;9Ug1uphnq)M#h~>l*yBrG^G>AYf*v4L>lEfYrj~#2Upr9y&C@LDo4k~&~V$`c9ns}eS=+!s-`+r={dF#Ek-g=j{{_FeAclPZ4-(~icg*~KjkqVmp1!$E5Ze|<4nx>+RRzVvV78NscNLX~;h{%avnh$*Sm#<5@^z3Z!<E4$$CIt=+iyjgc*xVM_a#*v#+P1)9W1?cB21SI9i5eQF{C0yzM~7K{^oT)`Vb*a_!-m1NZH;QwwoS49KmSUpRH9~|Oj9~`LiQ(0dsaQAj$Pgk_*#tyCzS69jLTHVwsMhBBRN#cx8HIa<)S}@uf3j&^2W<R)T2ENlJaGno66U#+&zKg0TrQIW)^(2w&daPPdl#EJlOXt%2(cj`dw)kGf+P2<rUO#`kz6$k4B5%W!?e!TboJ!S0^5W-@z{#^}M=^JanI8@QuTza^asDn1yoNTc+dpS&MU&Z)<#3>K}C4MEMSN_d?J8n&R$j`t`Xu?|u?|r#%wBE%MH7{NB6XTzB8dt$qu>bK@NJxBMva|7Zx`7Ca99*Ov_!f7@f!<J@h)cdc|tyDJtVAKRC{=)Ws>p!hGs=0Q_lOFy^XNkh3_mr;-T=gwp3cXG~Al&hSy3&(Hvp?>4w5Acn4Z!iwVtHT(7eZ-3+IR8pd_*&R9_~yH*@b&F|ZeSh<{Dtw<gE}9PJTnuO?|M2^*2lDUsn8oCGX5RTqaMR|EqvWS8TIQ46S=M?h@bf<@^^hRI?LU+*_&eA9DakvpE?e{nUsDV>-LM#vp9cF^TTMTR4=K&{!+>R=E6fzUoYfio;)P^lo$!$nDFc*^3Pk7jpLz*FwdIb-1AU-opGqoEG_=9S*I~>aXT&`zt$zhKRY-R^`A|IuXp}48TIwQdK~9p--!BM_DArw@_uJfzUpf6`(2arr$(Y4t!Fi~Z{}SRf8%_#>+D?xzVZIRgIG7Y0g`uvw&^%8<-!5fKW1(o+HDjo>%4hO__jZv<>B`>A-Ilg9dnbA?|)poiF_8_I4jq~+$8DO>J1p5uHCSHoYlS(|E+kePqX88x&B8!*$=;7D13eYR;*X^k6Yq9%g#r+<x6CpO#V@PJqf<^^O`c=YZvdAbv*n>l<#wHE9U?GS@4bc`Lch^2*-SD2@~P#T~1ztZ;X}oaDS}SpZR7B`sFGn?H=vA-(%h<Y{B^HyJPnukMWmy9XU>6o?G{Tuhp1_@psfrlKDMuhi`Na#e6vvlEpvYLj1LtG4HkmJF-3erR6a1&c8Ouyyy8#{a+77J+3psGVh^P_PMV&hfi(zj+ggjpBlYG_U)~~7u|g=q(K(e!Hzoc&9W!Nul&_nwA*66te3cS@xPDAz&Z*3LGoO3Nc>0r7oZ&L*EYy}8||B+e%-spIn-ZmwfMg#As=&oTllW7?cqBXwUm8tUN+{_?5<1sHqT|>n{^GoR`SLkxlVUp#_t#QpdKwJ4!-te#v-&EUIP1_5wS>o=NR!f-NXK_Rf`pWPUB4|x1z9=PZ=+M@8<Ab&F`YT<LXD^?<~B;y?#gG55+I?*LUvq+h#mV#5f(fgX_pBRC71f>t3RJp4#Ku*k{eUKP9^7=^ETq?pr^fOZ3RIa**uTK3R$Gd78&Rm-3_Pz;|YZ$ov)WDf`5--_gEasXWHZ81Vq}<*f8<7tZ7T!dN^S`;@-+lkM<Nr6M0=W=*uKKW{9)u}#LaZV$9;Hmo3inLx=Wu{z2-7nTy=RSUlD8#~I|25#CW<9SxrPlrk}pP9?WUt_~Kn_4lM7uzE7U--c{#{4Sx>GvKaxaXN)Uhnve_%7ER^#A=;o_<hMC+Z13jr~m@e>=gwU;nB<-{0iB0{%;Hxi4S1BEDHBQs$$a)c-o0<!4XFI4o%|`&;jm;@^zHIJ+WaalbZiCnva%n{oWLtcNoDJ$%Q7pJd(slC}j}KSZw6Wjke_?<K=G+AWdm^n5aWbJv#}WPB>m#rPyIPxJ8YhnAt9pwh=Z{3rF+p?t3l8J`kE#jihY4BFY^o#x?B2w#lyYrm4`fX1QXmkGr<*h1T39Q46`#SiL*^0v)BSPyz!PqzDf67m_kRs2-D_-(pi+-xl;W_b8dwnrnM8daqJ2O%E5Gt&E*hi?n*mgZK!v1Idl_&F7^U)id*lYMMOy!bz-V!v`V?<D^HBJ1V60F-xTeTwVJ`S71k`0*!Xzn#%t_C247b@0ce-p2Smy@&g(vv*!R{O4uhJNxyN`&hDL7S8*{5BDeM)u*^F%*;0MwOO{Wp=D3P*8<kgME}bEj`?=}=L_85^d8+X?#A?sDCcZ_LDtF6?FNpgzmn(DR#mfQo|2-ViBB=k`aVsb&s;UCq5T(ckf;7m-Wgf<#ml2y)gJI|e{_@mxx>LQTyK|C*FbOYm*@KlMTX&6uZio|HtD52uLoa+Z?@_x_mxKxxSwi$dxXRP$5rHMRGNtKHXobu`29^e8P9okw5xm9!g|%pWk{ZXzk@vWlxXq$$6(wXIZZJhu8_Ak!?%aUL8}kPx^-0b6Td_^_^uHpu}&Pv{l!msJOw&nJ$%>l55(_~G#2agaRt-E*WYf7Jc68_<$Lc!Ub_7V#>Wv}!?T{?630Azv*~h_e^gkW|8ru*@9r<_?AcqGcbgfx4gSI!cwW+)m&Nm|%dvb1d|O57Z_*z}J^WXTupgQ!X_8N))#B$AL3!uto9P~Yrwr_ejs?XfpH=I2$ok$V>($>!o<p+IrF^sOjTncY9!tAxGsQ1`MSRC~)bDKa$xa!Eb4%Rww3TWjzVkSI$Ll<lcYWMN{Fs)QU+1|YxK3TZtKsXmH&{Qm&p$lp;g4){ORlfF;=3O0bRQpmeI>N(*!Og&`#9+HI?B9sthmdgUt#5>{F8uP?)|d;y`9Xv|Crra_p2Vr^FWJ@KVY1?Y{7exQ8HVeOXu8{=j!(R;cH8apkHRMmGV6QaPS`Z(|XAMp8C7IXLr~vewpgHpPH46;yv0l>g+|{m)BsPw68nMd(@O*_}aKL^8VP_U*7*eY_ZpU{p;r{$a`QJUHlQX;2YgPll}8aC-}zqv*mfMStZPi`I}wJA5F(Nm@mEMzLwro{O>a18%b^Dxn*;l_{|>5eLv)hJm*YUD*iWjWIZgqA@}8<?|bB#U*72SQ2gYN<2=f*d?tC;m?Zn`;0<`5Fjl_y$kXtCAbEOu?Q_r5Su0oiRrp=_&M)6!9-T8!$o}SgXFtj}x{39sKYfVz2EB8768!6Pw#xXukn#b)iy!>}?^BxZkC=Duom_ms(B`bddzm>qT;9u!8{*HZy%FnwLu<KT4=ac78nzy_Wj(~E;5&*o|G0ebn7>Zmm&_NPa6B~^zB&I>tbbP_FWDzw-GuLYBiD<5w50eUrw?J=>ifxiabkje2e=!4812Nz%J+d^40(@^-js@R>vHhk?JU&^{W53f!q-EGpq~8i3Fa5K#4mYX>ghjB-n;J~JA!($S|LwkNgWxt;hEy+-@m#x5&!xv_{Q^-vJT6h$#D0zSGqiBRy-ij52IXCzV29juh8@E%J+(YbUKRqFHZ94m*%?|zLxL-t}|n-9q)-|+;39;%{%CqHhHU*U)4Dc<+hEK_ut}<!|uM;M&4)5_nOG}h(QP7n}JWIU-K4x3w5QyckT(6??nfiz_%5DOXk@Xi+#oQSv;TL`pWmUdOu4&y`ISX{sV_-tL@S+zx^`5ldI!9khUuj`Mbuq#W*;kyfdW!#aI_w%o+68xk<zOs&=U8LDb`4Rh|!b7K3jLe;42DoP~>^epj>K<h#b?$?(mf#WL?9@v?8t^hREKixJp=Y`MGfzG4JVmwu$n_2syKNc=w8a-Oq<d{@jkA^xv3@f}hRm?!IV_BC98MztwYenkZGcctWr9}$o8=81ovOtX7@y&W;aZ;sQ)>Vg#|wF=s>L2jRJm8t&n^?&|!J2LqH^y#)y@W1`(Hp0qbh!sPv7)u?+P#nroJcv4k98Mj{P&|;KcrbMcc`$i2HG&+$wntM(l1K6!#fetzv0^nt@fs`kS+SGHO4pP3kk>F2FSp`*>PG5%@_L@Xk)ikphT;R%edHZ#4z1YDP`rVmcoo}P#dcORkEPV*<mD{0l<FieC9kILaO?XHjz=PSFLgIrX%ab!`R=9eBkv_AQumPiS<&B$P7KAJt#DY;i^ods<o@K&48@=ETy@-m`Wd+cxg$ey2t#o<s-0|Sd)*j{`!Ey_qdLf6Skcvr-VDW`GrGF9+tn?fuFSV9&(H7s7aWg%<N?&)WTj!`Ft$H{>L3pw_oMbFM_CbV#UkoA<VEDg)M)Zzatt+!97B$zeo2lbk6|cY!1@=H7mycHW5_W)e<5`Yc_I00>H>1Q6(_7X&QSa#L-84g;$zfwvcDDYTJa7;u^&TmWrkuK)t{VVMPn<@QY(?qlCM%rl9d)EUnO6s7A9XO-=r2I-z4Wzi<9%nIn>hR9P(vqRq|zWh82gXwW(Ff6R9<+RmnBU6{)4k70IQj#mS|}#Tbe;Y9X!QPq7!ZFxiV-gj$qbgj|AJl3bEwU4o(5m)e-@ORl5IeL-m`wXs%kuTeaTI+Gkuokg8V{+1d?ok^a_^Wzwbmr+y5E2yc|6mly0BK0i!BKaEiDp~1u@-^}e>P_+u@-1o}`4;&$HHUngoXb#rg?gEMg`7prAZL*eYX$4<FhlV?hT^%@+T^+9Sgl|!#!{z~W63k9^T_jf{tS+7D(B~0@+?Lw=QEr<h@rR+^&+_r*_V1vD_Bd4OHglU1#3@n5$Y|iVBISAqTbdD*12MhnyVH3DK196q7__6ic3+mw1R6*aYgE3t>D^JoPYfu=2#x)cuk~EcN^;&97na^s{K{%vu|19ZN=MEAM)GeD%AJLRmknAZOLtUT#M>Mu0`&`@L@Z3t*B>3Icgbleg0OST8><nT83JVoM6QgD^6RHZN*6|E-(~lQcZFuIgJ`mR=SRSf#o(a6d&a82U+GIeZ||YIAz5y>N)ax@@eWRasqWb^%Pn82K)1!6;rI3#8BMBiePGc>J)N&@>GW6mDKOZE6JO!*iYTYT(>cYZS?c=QM!e?nY@|xY+)!~%TPR@I*B}=Jei@mFSQ4`FS#{CaRawLE3QwiOAXcv){)Xi)L?QWaziVUt=MYC9O`Vc((dFr<faV86{t1HZ&AIeHONZeCwr5-P#cmPGN1fwL2>>yqPQ)!J-I#S()}8nMx9EIr>>(;B~RsiucK}zuOlC1DBh$Mtcgw3qguiGSA2nbgq%&iL_I=2!tuRCO(v_kQ`c=zP1b{22l;D8asFCToWM|Q@En7681(Bi6gOZfZcXh=Zec|;EB?k%T#X#W-&>GBq6U&bBDbVgC$}Uwr+z?gPX3Tuja-fG=5v5sJ^^eqh#bfWVBOWpA5g22)i;7BR_F}HpE4A;VJL3JQ2a6V6S6vYIFFTnMb=r@aE9XX)HdYt<OvMLBdD#&t=P^8hT?Hn*h9PuRVe(w{cBpmpP_D~9{;HJ-_P{?EaHCVQLC<heI&7m6jk?F>tVDIJ_f8(qp$rJN?HsU'

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
