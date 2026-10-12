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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_000.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_000.stl', 'source_sha256': 'ef5f7cbee9ef66cb9c992314c9665d9485a3022fce027a9c26f53113fc2dcbc0', 'input_faces': 472, 'input_vertices': 298, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1224968433380127, -0.4578052759170532, -0.048298180103302], [0.2683338522911072, 0.29852890968322754, 0.4677484631538391]]}
GEOMETRY_BASE85 = 'c$}r133OG({l^C|>_UWqB8vgU1O!9`1O)S>O0{4M3Mx<~0fKCX5F%p1@+hc)1=+)*A%uM`B0ET)Kv)wNSp-3dAZnG?7OhrFYwyhc%zbm`-TyiN^Z#?s?|eV^`{vG_?arN<9J+NWb4!A7|J4^Kr;VDCSw{#Nl|_OWm7bM7xPSV{<{6o<mJ;#Gm;bcR`gPAIyY(t1Mu{;=1JXzK&q`{anABll+oYz6Ndt#xWoM;j^c|ixAYJ;M(}s;qcl?oq(lXPX>*SX0+BQvmpmEd0*AoAa|0>EdeBY;_K<c_pA4?4%8hSiMUU$set*(c^y+i#zy!}VY&#j{T$XYjjX!X{U%FjHtOJ3)ZzU02v$4x&KKXHA^DdqROzSH;IYuk&I-}|!ryycDd`kwpx<n5-P+WU{kO}}KB>qjPh<(8*oz3pZ>!{?@-R{nwFZK~W2SDp9O7eB8}<fO`9`(;APk5K-|KW`S9eh5D=?FTpi_9a_YIX7pV_q7jxc<Bw5f1>uk9<W8FzgFeEuN}0X(fgFjNBcc?ZC3tQ(@v=L32%I8`l;DJ7pwG^pGdofk3W3W^mV(5Q9a%AH(j;a*Du}Y98&)E!<)?KilN<i2l^wg>@|H|p70QV`Vf93i}d6AyZ(%6pZNL<KYZ{L)efoJ|1NQ(zdTRv2=YUpeqLz$x;%DzT^>RDaKmrkbNl`JIkO$KANqRKX{Fj<z4<+JyooQ1&jk6QoNqr>eyeolmoR=pdo~_6{Y3rVy;l2U<-b*agV~Rw?Q=z@AJP4|=W+F1aii;cRqk#n=gjihzAlgUBh?$9QRVu=pFR)YOaE$_bt>J|=TG{^A$~Zy-(lZ4?9gGYnLbqStw^9>ar_?B_xd+y>DC}WeBhx2rXSY*Xr<Tv8?w_=PGObD^L2R!U0JQ#p~jK}ZvQYZjqRlT2!7rdr%sr@PM=qLk(<7G+-kGF;y`AB=|^-s{Hf<&)7Rw*@As$o%Bj=0TeV8v|MC&_zKF|xi%ehCz3R5x-WLi@KQC=gk@~$sHJ@KnlD|)tYxIg@<!>3a(pTT*<4%~qu5Y;0_ilY_-CUv4zc|f5PPCsb{NrToJYV|I(sF@*B%|yepHDu*PLChf>Cg64zIeO4dVeD;#~(5MP@l(CyG3e0T<lB#;LwkhKRLY5m%dD2)t-@?9rl}kq~=_Aep~-@p)a4Dxkr>g?jB!0;Wdj3l^-|fs4t&;^WE>-H_ZR@H!k;$A3YD_>+$2w!}#9#8RAc`eQzG_^73-CokiAyNRS`iGGdR<r=24stn|8nb^6Uk%gpgp(ya3d)7RrCw6mG}eQbJgsjuIcb&mx4f7r3d=j(pA(`#R+|8Rf4yiVPa>mQ%^-Z<RdHWK7VdYty<<IRV~fBC?dUiV9<8v9J&o8MZ$za_{Ijox&?^u77bO7DHY?DTqmu*&20`y>AHc<+&2U)^q2eZyBS9rC@unR&`jJa)!EPvYx-PmOPR!t`~&N6tQS(w7h4yGZexBffm}_pWsA8PnI_)A0VQhkW_y_1lf{>U%2A|F~GCTi^9l^?beF!xz1Nx}eIb*J;}SRhII-b(+p6^nts6)9VxM-@N3mXY@Ks=Tqm3|GRAY-gj2}tjENSl?P1UURQX}tvlIWpKNM$#Pm}ie_i?B_Z>fkACu4Xlil^FUH;-*T|a(7u`i!mYu)v;)eez6e^B#h$ZEGxVZQ6nxqF}Qxs`@1KhbLc(3(2RPqq51Bs<A{U;aLCzc0OBXZB0;`FZV{x%2RmeS3ZNs!(aax^MdrM}6&fw5@O5C7vzJQ}^5RlI`nxM*H@>Wcxb(+8=Yx_r;qh@nh!6j25}(bG>=n^1XRm`}VwT`QE&JYV*6Q9QJnyKjyoGAM@R@eDAwc`Rj#dIlb?`<$K?K?c3jd%lE$f#~b+a@#cB$+v||kOXi#H@2zw2W7au?Dk?u_U4b97uF&c2b%joEuPg9l))hJ*dtHGav#!wj*z1aw@j1T!)$3CHm~|<B%(~R_y>)55%5#0~sn^N)G3(^chi99<_Z?aOn(|}TxA-yZTl|>yEq=`Uc1r$CvmLyBitX!t0e;Lr#qzy<3VzH!1wUq=qSM>^6x-M3Nl2JsmeU*O_%ZvkuEX9?zP(SheDAw}AG1%ykJ%?SEtshK&)T<YKW5*$?fsD|Uu$2ieS2Rlj&C2}Yk$43w|ws$06*p&0N*|b5RqoTQRTGu^|tTTS4^p{eCymm`}VnkXb}ph_{z^bY5RI!#g92x!H+ptIXGs5^6hgK{Frl<d28P^pX-eu{Fw8l?8u}P5pceQA9KDmY06Zk_W9DZy)%^B=V02m&%wI>er}2gIG4kZIhQ-SAxEiwE{7j;E_cg|3spY$IU#<`IpI@Fl^=6Hi63)5IcfeoDaQEm`Xza6o|%t#{<-bu5?{ONb`XP>s`A+9uJ|$Mu76#)Le<wk*KN^yrCA=YeJ&hZ?Rzfu4fk58G}O4Ndw(c?UO|vQy8etnKm7iXKwlgiX67HxectsGe|pDEA6`=A`crnS4D>7Z$qV$Yd?MPPJ|-OKXO<psmPgd8?Y7Is&dUpe{4GcG1AVJ~Jl|>u&!-*4#Zu}!8R_4~EziUI)IK@JpV@6mpg*y4PN3hS(ab<UGN)glA9`;<V0jKUnHlKUsg@Jyzwq>uK)?KfWu`CQ?dtm3Pvra3Uw_H<H-%Re1o;<dFAns-ny?_y4?j0G(9cYMCD3otW^`bAHuRqw=!YjS2=v$HEDlaTVTG?92JH&0ujgC!^?a+oo^RFH^R4=NzExk(x9S_s-(O$Px9S^B@2_v@;&*}L-1Dt*?)la@_k3%dd%iW!J>MGVo^OqF&$q_8=Ue04^BL!nw5G}rH=E=71E;v>Q?`F$-t0hMj7|*9Cp&j`px<)p(v)t#zgCvrUN|tXrt|4=qJl^e1JjH@RZ3I-(;EDz%E7JvSAVK(^<c~Y@1H9F>6GC+C#sba;zvhoJ9-_x4Zh3K8cy60uKq)~T-V|1PW&WX{a(2I7bpJi#DCBVrCgTrGrvpyD_qn0J<*9DgscA&E(?cCIq|J<^>4!E(hes(Q3jRQw;I<~2+4Oi(Eyd#jh(o~iL$7?j^nrbq?LR-*NsVA6)%}*#qnD_A^A=x?nWCE^1fQI)P`_F(%y9H)5y_(qw>0(ab2E}Ec>VqDzB4Dxoub3iHc6#<3s`~`=%aToojhdZSs(PA%BzoAoID4K1f1qa_@iWzuUOK9QWMAGiCZpjE^MxOYm%6mPXuPn>3Y4mqgl1q^m$#lgLk&>2)W`@15w1{tE62r=SnRDe#kM7x+nd68Xq{m!QkwCGbY{eRw0h6kQH4h5vv~f+z7T$yc5D#);Et349u!KuCVWi8s;9XbF57zJ`7SUxPm*Bws?W!k6GvPDIcm^eS8g??F$)d*E^C1b7^LFCn=O`UYGFu4>e+Dq0Dy3YSI&TpF%|R)j~RqtJ@*DEMV3UP0s0if}v}hYC0jz74Ge-v&=a--IW^7tqV_1^7$!8vG@E9{mhH55GcuMtMJ@&t4`jQNK&{nXd0C+C%s2XhQPuoEU?Ch(_QK;bOE1mbwQnhW8SZ!{|6z>b-CnZc0eL+leM<L-bx)Y8|*CTmh{LODzpofNP^wU_B;kqrZb|!;Ou$XpA<2oAB($Xa#tR6MuAKB`UAGqrZWrhT!h-Bj~T;N8oPgWVjpr7P<m{3tok8f>*(t(UtIKc(qYh$?crTaN-w)<UWMtOhWQZLUKMKc>^K&Jwo!I2+4~H$upc7>BN2~_7RfLqMyQN;VbA@@D=zA^lSJF_;d8n@aOP3^dfu?E<_K&g>V*{4QIj0=smF1Tj6B526_uz11^u2g3H5Y(K2vZxEvul0j&%tz)5H$I0+tsj)X_j)+300^u-K#F?!bMue0>wS=wFq=@t6<3hl1@UGfI>a}gaIlJn7XB07E~&qNDFbc{*PM6*P697^tkCd0|JuO7FOe}R@4(XlPL9a<J{2S13GgCB(35|TTi32-O4H<|?ZhKHjg;1RU-a5MuR4(od}jQlf<GGtJ$49YEex)XDqcnQsgrRKp>--V^lfu+6;OC1VJeF2vG94z&5Sn6Z2)F)u6y<n+*;g{fHP7FbNqJ80>a7VNk+!1brJ^{CZo1>4x&EeMQ<8W)Z1Nt1?0q%jm0QZ0gqeJ1r@O<=bcs{%iodd6fccJgXyWj#e4=#W|Ky%>_;PvQScs;xToesBjqLmZ%&_uW%d<S|bd<R?&tqxa%Z%1pvx5IVOyWqO;{pbVm{ct+^BAgCyLwCU2;DhL4_#k{7{Rln|pFux{&%h_plkf@n5PAeY1aBuK@1#w4(%w7qb^9Noe~yrs?yr;d=SiNe`&aTV^dk`+50clRhedS!NS=@G5Yh1_c`*8-h>lOmJ<tb4bUaJ$fZipd<6m-Xw3djzFOr+1)kXCElH3NpQ$*iK$sN%|5q*Cp_e5KX==&~t2qAe8+7ccF4|HMx`ZU@Sej0uVtp`5@w?OZJTfoiGYH&07KJ<3@KDa$v7j6$fh29T81@}kO;r?(Ax(&{O*PsXCHSiYnIJ^bkjh=yb!&}i4@K$&&dI(+%&qKGvGN$pn)Y(S*+2kkn9V7pDc)rv{MtK%dUa1R>@-L)*QfC?Uoke>{oocktRN7B!n$ezVw71mX8twmE`bX+BMt?m+e@g9a^lxYSU+SYGIvymqKz}Ks<45vC=(8d^-XuSbJ};u<Q}O^paz8?HD*7z^EcvFQkHU{qzEt!X_!;V%il)J7v{x!R3!X*0r=pACMf6`PIvbWc4Nisoq4SKo%%gr%w;T19JP_Rp4}=Ga=-jH`cgaK0=^{EmNFIj11j~KmYa+UrlpH1`>piJty;qg2_qLM95R#jqdOs@n+OG<C|1I^Xi0;QFe~Eq~qWgEr7tmuOy5E;P5gjk0=L3@E`9U1o038oEfXAZ8;A1>vEP50^N?FGelIx?dz*6Jk`fyD&4vyp5HPNwfeN<k{y|dg0%l&Y-E~QE*l=+|jD^B!ZSZ;KD|1rnD(|;^(-nrh%%R40R)+J7^*_};(X|=eXEWc{vze=&D2m'

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
