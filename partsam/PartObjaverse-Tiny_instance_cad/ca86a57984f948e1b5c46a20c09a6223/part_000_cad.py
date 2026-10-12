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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_000.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_000.stl', 'source_sha256': '087fd91b564fa1ee9839f0477ed8bbee853de0adec011f9b8db4110edde6ac1d', 'input_faces': 308, 'input_vertices': 188, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31614387035369873, -0.1326122134923935, -0.39809897541999817], [-0.21732063591480255, 0.00527770072221756, -0.2879449725151062]]}
GEOMETRY_BASE85 = 'c$}r02~<_(7RL{Qii!$G0**&T0WnZhB0;$-&I1VHEMAlu1Oz1oheLowsacMZ%5@-z3^mbm<W{fp<y4B9KC^3+i49t*Pn+KT_W$qe_SSoAz4hK*Yp?(B{N3ztfBSsr-V4j<QO+)&8eW~W37Iz<>#a0Rg`4K7<tOFNNt>CJ7nGGV-$`>9U%eja%CT`{q9-|N`C6f0Vp87BT)%$0UwCq;Uk}|cIXibwZbH`d?A*j8<qu8B%uBNSd8r9GN%m|1UZJ5q^hX1F=nM7#@zvDcg0U~GuGX&Bp|9={jSjr1R2vo|zA3UweEnd)_(olj_{QC2@r_}j;+ygU#kXiP#J3$!7T<cSiTJko`!#aiEEx4mT~KH058~@{3Xp%|?m4M<&VRpLr-WnO^q=5g?jpW^JstV3hWM8K-O%Tj*68P6f%sPK<Zij1>x()uY2ur&cp$$=D)N_15nn5MQSy!VVo-nRSkyU{hd$%mpw7*~$iKWzd}Fmge2)n9+52m$V|jNH>a2K7eB(|$>Rih}{z6~z_4Ug!pKIfhAJrUndJPocQZx<ur9YpQb)y2Fmb^W)<l0nt6Mk+)f$T55K(39{tMKENmPwsyg}5&M1X@%qzIlBu`g5s8z0KpKf7_}yAB+FRHstqvAz$)M-{bn?7U<p5Qpx-1GOklL(XXzSKG!`Ybxc{6@aN_%kvgY;#d@zkhkheGWL<Nk+ZW_|&@%k{_1pWTpQsL~6Q2%$f{)BcJLm=9NJIVaic4g!rj0mfH>SaV<Gj={zxj8mZ?eQ<-BDH2r|tCXQb+4L2Ki5P6<-@yCBAjz<M3A);+w6zF`vrLsIwt*7v_2j>t5-E{9~2qzx*)r+qD+oQd%dzY4#4(zuZ`S-MkEa7VblSub)4ZI+2~8k~(dtqyBeS;9Khr$)7S7&-1D}@y)SUajqtxLw@}h@ojUbTID*g41J#}7hiulMtrlr8uMLOhWv~O@ht-`;(7RW5!Q`4zfk@?G3vb3IaGlB?0d)`xCZq*rHOC)t%vxwztz{_K8-}3_e|*LwL4h1cm(<h3qqY7FRa_8H~dDI;SXtsbG!N>@vXTn(f?<!W4}YIK9G7V&eqD$9h(O~woH7h&xi0kq@o||0`WDM{b>=(4{wb5Zz_NvKE|wk+fw*eGySPYCEt?vjhrjZZyx-_36if*gm3zC4*Zz4>5_j_$GNS^gP*-PNBole$bTjmzIRB1)UkC!zFQXj276H_r4IRPGvFVOl6>ng=kOezNrrzbbhh%fEMN40eI|V0$jk_N9{S?^n-bt}ub&}xz6pV!KOO$nVN%Dk0rj<)C&9myE_HODx6#k}@$d^gX3E^Ay(PYN(rEbpg;~ls9v_5#MU8-8(LG7|=1qgqXI>=k*QHdsUzXHn*jKp;`I8&w$-dqTMSdUp$9714v)5tt<JuqoFB7D`t=S>;ZwrH;Rx5S%%HPpvPzd}VeDZLA--Um>7yRova=-K!A~Bz$Ao!;%Qe<C04M9Jx0?_}F44k*dY4W^SKj@15K2J*>YxYs})1@=~HSbFut^5e~JERT#O>19~Iy)YN??k_Kd-$$H(dSlg_$Qak{W6t><2;Y@g5Tl79GSzuK=i-C6MoI-a-Pj6`{Ta+&=P*ruO#32{1W<{*aCjZW~r}#`d9d$xZ$~T&y@Wd6=U)K(7P$}jixxa{gH3<b%F1hnJaVfLO;eM&hT4poGbZnyNGYw|N9y7ldCesf24=_`n>z_(+Z@HzV3?Dx1G5K-?LWo%_HGkR(?<a8rF@#=ai+c9{!LU;+tpT^TM*`EBNnkkaKQ6i+tOetMHdsiErc~UvK=O_?EA|Uz6*^Fx0vA4*cY3@y-4t(WjdszP0cAotRrc@y&e-&R`y`<o=qz2t@ty6S3~Lamb&075xl|hX2-E;#)S|#J={l7T*^1(O#)j8H|479}?em_w+GYFE9o9KYL)^J1wP8>!ATy_wYBTMdw#b9m~|8ux?~M{N459TUUPxzj(d)#>(3}<T_w1)@{C2eC@rN(x+{N34ZGY<hR-)`NqXV=%-tp_@><@(x>IdN!<6^(a0}phB`fuBR@Atd~?+i=|>+KgE^P`pT_<ciEnd>#J(oGqW*6sSa-33{0)uZhkY;S*}SI<>Th>~U;iE6mkM3cPx`N?@O-qx=adckwpacxz9j^{-l7Tev+sy+{B#X<oCk<+Zuq14w#1c~=e=X7Q}eC(*3;govl`E-c?x_}@D0p)a6ZmY*md#EmtwHr8z-=C`Pb;v59^xro0z}vXQ*?(7wQ+``<11E4f&~D*X<Va4}6OJL8E0|^N9t>zjO}y(U(x)Jr@4a6WDLtR#L|r8H0YN92Z{?!uJFteIW8JZz8{YHR?ZEiu{JP@O>`gz7+9!-*ymlJ`jjLE3hv;<aN|HJaAu*ehPm|HTqu|hWb&b;osW=Kl-@TxBX>0=4`9P{7rs1CyD;JFB{fl&Jj(dzIG)Z{_qOqPcFfItSrIYwl0O=bG_8DT*v#NIpbNZ`{ldXSMW#3zfg|+-Ggu+f13|Kwgmesb;b9q!xzy1{RPO6UxNBI-7&W_g*aF5x5u2{j>EpHW+VTX6g<~A4ET$4(9gZjm|Jx_>}zTk&tZ-9sd>*pzBvQ_Op`pPwzUoA_ZQ3g6!;^4$2kv4!2R`suXjT~dh+M!zkNK`eZ*J#G50RVx|TT9iQb3Lmt7xY4$nrxulp6}%@dzf`bZP%R7}Udvd?19tNJ0oY%}if_mfcn(Z0yf_*Q&t;3Uqi7tZs7INZk)e(uBupiVfyf9@HMIy!u#XIreh^%VMC?$0@R$$U)HFJTU~U9s-CP57RW@Fn`M(2*bf4dzz-75cZd!FhY91<sr8F6!s|VBKNv+;0&2?DjC~zwIaMYEA*jclW@)3RYp=ap+%<bHlo8KE*tb3`3vYo#F3ViMh?f_f_4?3H2M|{OeYHU)5*)c2e^9UP1riKV#ic_@)zm(9bew)VXyR`3IJw{_SAQbK#HTYu7HIpD%*h4}9x9<ZEj^k$>zv_*;-~^LQBj{Bl%$BfweKwZ2u4b8Cq}KeLV>mHZ=5@_oKH{FZg%8%5Qqf58vF7xGQ9ct5cmY6O4yS@`33!tZ(cgj@$6M4kF+s2}hl{Gdbd_d9)D8~vxhE`?t^5`VLWrm1M6d1}cC4u4uwrg}ZlfB&bYv_AjUpOzl&`G5au=@EMme)j0VQ2a1MaT}^XxeeKy>P1%i5ZRmTNo_^$z`Bnz6!)OEA@?BnVkquO^(K3>UQdSNKx!+p((YuXLF7PkPik+n(!LHg`*MAyeH{Af<IraxhrK9{qD~?!-9wHd@1!0i?<BuLJxqRse1Lk0tn_vA0df^}KUwLEWTm;}1JpODxn!jo4(nz(^p?Til@22-4R+X9FlV4NfUL9&xeM>T;%Du#%pUpFVsbt?+aAf(+0<h4EPG_xqZ_p=xf|J+>Q440doUEYv`0f~W2!s35w$tho$SuK%^8Z@GZZILv&c#0OnX$?<2ie5rp_U6Ca+;AUO>$xXR^)$>MZgC@?vTlc`-SUI-8tFE~6Hc%gC#!%gC$9E2z(sSCAJ`^T~_IIn-=&4mri)zNRn~$JnDSHI|x8jwPp3XOm}hZ>bE$ovE|PO1qIelXa>uS*ZtEC%2%sB)1?p)&4j)O&N-vG`y6$P#cn!HYPtfTP_U6Zq(*vH*z~_dvZH+M`{weBRP?pNlqlEQ|FM=$#bdCk>`?MU?|>7tt4+H@1Slb?;x+It|2R3Kvue#tTd0Tw2Zu-yo0*Rq5dkauXKe&KP%X;(nSvaFXEn*<~Zyzhci%`;xLmG&P-_x`N6q-FweG}w+ru+dNrWBQr*aIyl1Wq#jU9w$sJj<HAArvHJ0o{?nF%`EA32Hs*^jBn^9Ykl{O_eBRf-_$Pdo3v%}t;8H$@wUCFNOy9w2Y?882qP@9pRsp@*PJx1AM5JPboLvaK{@o<LXIELb>48;?uqsj5qiPX{LiR5U8;t|wA<Pqe-48{GaVdVbgP=?|VY6Lli+>fEyL>*2xk%ur8kD<nq$B>_3D4s%{N}fVCGZZIKCy*b^C4r%MCPVRb>O}H%@?>f>c`|t%bp&}Fc_ei(c_cZK+MgUr9zYEx4<J8I4Iw{HevI0W{1`c$Y9fb|2U3TS2a<<U$B>7T$5Njlk0p<%P9cvcPotX2)5tTZ3FHLMT5+{K*4kqWL-A^c;w22lMGVE|48<=o6mO?ilXp{VsMX{e@@ovmyQo{pyU3duiYutA$ra?~48^6?CFD}_LWbh`)FSeHasfl}Q`B<uQ{-nDidRx!BCjNGWGLQ7-A;Zmmu(EiuQC+xqt=l3k@r$xBkv`@Lfu7vg>0d2B3sDos1@XO<fYW*<fY^iYALydTu5C=E+jumolky}JdavHo<}yQPmvAs)6{3kPm`agt|UKC-ay?*-avktx{bVzvsN5E%Bg{;^MCrU7=OGB`A~BFj~V~^lYjm-+wmvk?X~{-OLz3BhU$Bk{R6Cle0eNapG?|60IAdSM*'

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
