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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0c4e4a0b2a374553ae762bb33e8dd2d0/part_005.stl', 'relative_path': '0c4e4a0b2a374553ae762bb33e8dd2d0/part_005.stl', 'source_sha256': 'c2e0e16f3a4adf19c35b8f2860e7a69db26d93c8727553ceac7a73c2ad7b768c', 'input_faces': 320, 'input_vertices': 322, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15053722262382507, -0.09787918627262115, -0.14754176139831543], [0.2004907876253128, 0.0871969610452652, 0.17936155200004578]]}
GEOMETRY_BASE85 = 'c$}r02UJzZyTuP;1G{1k>NOThhyr3o<k(_Ytg*%mD3K5wVvCv_I~pulu<KPRV#Puc0gtG$#6td-XlyrXVo5Amq9$q{^X;Ag!?)gB>#g^2&Dy`a?{~kMJ7><!nYjjabu8+l;jfOixMJ~&DYZ0BmC~AvHgQB`RCwr!@eN0ho#LRC7hnDTqsw~q>mD@FL7S*ebsIind}yRwON(2pu;y-F7Pqi5kx`Msqlb-&96mz%p9Ft7enf#keq`|25e2W^8~gftSsHtIS*Bb5kAKbuO)$^2KXRx*jX8g97EPNsH?TnM3C-Z=R*qMyZSN7P)aKGqeC?ZSo0RIVf2~sS#<>!RPpp%m)EbzzSgHBdvs{V4x6h{3@@nW76>o-I5Z@S?A^A<#Ys4Rce=t+>XrT|RQcq+q{H&xc6938fQm?H`D*RV<6D4kJx%Hyj3e@}X^#+MA;k`}bn=L_nhYX3gHe0_);?FOHKYgL}gJqzHwA0eL4g8sPk|eJ83u&*lhd=zNB=NQ9t=5TO#}EGQaOofI>)XlFpOF>Np2;&MPTL!qB7V2yhb6w!!mZ+;8zK4aW;*<yt)$;<SKCUwt<f&{d&^6_eYVGT`F>3!#Mgd)xmwy0khxFATO0c!-V&ZH?`MzSCi%Xpiuf#N=^snWSrTvYerrm6uRqY9ql;6dp6Z*#*W3rKl+RzkpQhq9zgdVs-&FEy18YmXF|-fj)90_1*E_c(ez!N`<IYHXj1NNgN&8QZIV7+D_!D^+-PkMY5Fx(SJ$bprjrj9`%A?=9o+JK}7pp`^rHgN5Efe3UXp=nFhGo;_a|gC(i$5<_`pZ&dLaKbOWuI*H+oM?do?Gu^$@nb)uPpJ~_lT1`ch`w;lvyjj;Wu3J=;vZGByL^SLGkB??GRmMPnUXb{Fy25+uF)Fv)<TpNUnR?X!w_xEtCFq9U{J7eVX{jv0BK}<O<?iBpr~~UQRouomZ=iZ`KG${jFz2%llteJ1p(r>My==^c?cMc_Qt$v?+r4E9aKT=d)j!GOp%MlJ*+<X34MpVv%@#_6_ML!*`PSmid>^?|p6Pzl<F-<^9tga^?Dt?EpV2|69plv#$8&?2nP>sLw9(dpyg=I2|q5-{@Fge0%>kGCr)<Jh}eH!@c5LQy0lNFncFpT(~ZnBJY3F?}&`s;r-!1a-A#fe&Z*;U3-f0xHMk!7_(kWesfzm{O*l*OZ=e8;_LI??ZSO}?F)H5vHelG?x)AYZ`;HWe@O%J_4Vh`zq36hkM?G{+*jtihcZ5lzU$#%E`$56N-*v#^RTbP4X$)d`X}`c=8>&Eq9lLm*OFh`dO&>Rmqf{9nw4Z8F>gA;*WM!k*g2^8{u-IT^q)%0_cJ#}A^xR{_~z4(#MkEjEb;md1M`&SSeSfIYmT(XNT>+Ee09vfNlD^c?m5W)tXB?{JbGA~<hQpSwnp-=?F&Dxb}p{l8M$w@=J}JPzh-y%PR85dvhbIb>@D9v*jIeZo(D26_1{J#&y=f@$Ci-<zuH86FJH{d+Puco#6P_h{;*E)Q_ZRJ`qgTD-^5#(m#>$TaicX2n<@Ppnke;Z4#Osj@6v3Xw9{!7{4e7}<aPQs<iG5T{G;Ycf0<XZF^+nj6<_!N&5+OKosX9H-`FLOk=zdTb*lKaypH%$e7*RuvhL}vP2|aQ!1elY13sUB4ejr|9{%I@%O!r*S+wU`2IhDF1uG;z;Wgs(d*QlF>bFwrP5FGWyx;2uzE{mx@a^;Gh|Yh4{_lNio#gkpjP|VVhjEoLVuO6%tK1&(r#=+l;y8J;#P`36>$UzW?xS(FW&PAnyj}WUKl~LTzTWdg$z!ICM*EMBMSO0}n8NY;#9oQ=I`e1bzt;u#@4kp6c|X}(@@OrtU|pG!pZs2X26V>yab}LJ|61o>aiTs6lHa^{75=k`SZUwuWYk;Kce`lImXcrhYl!?tAMv$f-^uv3Zn}E_?~jFVT#)A;Yx~XOn?w5SEZm>k+Dlk(o=@E+@jHs+K5#yS`TFKE_-FgcdSPy!BfdE}ReZBZptQ%HiuKQ&<)2b`JQ%A2WZpJ+WQnic36k|iTN;V=DB=u!*B@h~ouBHM_cQOp|2}@TsHGjo$&^<qh3mBqY>M{BR^5YsIEnGNr<=svD<$nIJf1CI&yjUX4{+Zr@!R8<N}daU%X(lR<_|wQLe>lGM?YencsE9Tb3-es*D_<2tgm*reE1*i#Pz+q9sSe9Ri0nWo7Z@~{IP!Bnkv3F;gziK`r3&7QqP%X@M~0BAfK<*MSOimiuiii7OX!WuOyE(@G$aUY=-uD&64YD+vc-h{Lfa(I;LCWrGNA-QR3@cf0lUboVL;r*1W0WYokl87kzUO^Xi_B$n)_*X@^;?qg-EW+hoLhkN;A}r|kyrzr^kE-?_+qqrXf=yT+uzuhsz1<@v`kpKF=$TX&OwFpYik{p`cD;EydfQ2abs@om5T0N-?x`PDo*Onghw1^6Rh%q?86zW);Zyfe|b-{R1J4T`2pT;^lBuC`lu@V)w!65kxW8+o%HVVsn37hh}m!?%UMuXa8Z@%1WTyf&O7_qBCe4D!#|CjGCij*)SqdnY5$^0SMS+CKF~J$H^F{>fX(V-6^a`Rd$t#Cz_Ob;f@Gii|It^)7s~ysQh_hxIV;E_?)kkugKsnNUQ0YyW5Pwb|X|^X34K(>G}Uw2N|m?RW5eW#8?9=i-^s^Q8TuM^oPOz3`l4#w<s@p|#*&=pJ3TUNhTEeBHJj_rt7C^1W=YJ`>+;T0x$Jt&Y1eKMV;*p2tp0L}y?;7`G?FpIl|3eC~le?&F0Uk;m^M^6!d~{Fa0q_~FfPT{u7JMT(|Np16my?%1LxAWxb_d_CkN<e8Z+@wOUu#W#0i9<*P{L;GWbkf-l)$)mYqzhDfAL7u>qc%Hr881vz&1ISaVZwBu7YO=oA1|LD5kH;^;efa?G@qGqg_p{08tYvV&JaNpBxOHXaKDQ_BmHhg<hT?18;?|1Ru7!AqF!;_hWxVO<8eyJkI0|{Hti*V$KLXEP<znHt)v$j2&=}9Ru35-ap(d`&oM_A+K|a{`%uJB$sDF|wdF=Ze!}r;Me#<?8eUx9!fx_2OpX`L^^14?K6mF-nN5}mh`2u;u@1^5Dbi?%>>5wV?vOEFvawBIv*Eyz$ul?Ch)@#f2tGK@(9Y=haCV6Z}qHurRbv`KZr_&_fIA2t*qh(rG__234iB@eT&%I{UBKR|kZ<P2JJ@FiVbgTHLle6@Lt<!Pj@0x@7Q_SCet-NnM^uT^@Mt`(tQ+v!m9h+z2z8fd=jNR)f=8ua9;d`#YyfM2Y`lDv`Y{`=rE_t;YcI-1PLE>xivoT-&JxZ>-<$hoB^|1-4cZ(tOk`}ig@e3cz^|c+li}!!-lq2zRk5OM{JnoOOLGafcMZMov#J<!vP<*Yw<9pZFW=w~_V<XO4YITx*kbZDCe234M$@Tilz<pEdl=wznUHach7%K6$H$AZ*o%I~o{Zb<KkHNjgH+xl+cG^3-%lOrv4i;Y<s^NPLTZ{IT*$e;ddU@_L>sQA8^jSUGck0dqCC+>hh<W3~M&g@|`r`X;NWs3huebQxUmfLnQmfGb`}(&7;HP=6k?&Oo`{aW83i(Gq#P#s9W53xo1%9VosaGH1k9B!+I`YgMAkWd3vAZz7oDPd`yzQMJ?Mn8=KKIXmAwDTe)^X#w5BBYyA0j^Bl{^<~E4oO$HO(UXa(&$%%>N-VGJb4PKG?6X4MBeep20f!MS%F)@>E&JEg^mwCt4fvjj*CJU)i7Rm3T|%4e(1RiEq?%$9Y8QWYpVsi_~k&>WcXxEFJzaU#ZucG4dd;Z#L=;ydv|PH8%zIhCg~QzuhxV;>{+W=#Ofpl5oFj5@+@Hh94Us`v&cg`ZC^ZAwKZ^|Hge?^exuw0RcECh|R`xm}@zlAN6S`z8>r??X*00!E;^f!N_y}K)k%qa}VQ91pHaSa$PJpLh<}oE*8FfnAB@s6^r#Dd?WlJ5%S!tyPm=NI4%#q=W2PrHFBEE__36{fOb0mhW>mq73US7U&}2#o~?I&!2J?(3wet7LA}Y(@SMM+h}>t|s}i!V*^ee7|H20FC)}0x+wz03kJ#M;ewP63*M`=T@ne5J48GIHa=q*qx8r^s7=rtLXC;jDQ@1dm+b6-lv>fd$9+zF%H^OtaN}fAbxo<5Mry#%W))djX8!>;rT>?L+uIwW%wVZGtRZc;k(-URiX05#p^T?PS#E)#f6yrAx=UQJJg<tLE=i=+0SO*W>5Z~Nf8~cQ+EwPSQdWd*GuLYvlPT{^g?u7H02`3Tn+XL%$kJ>m#(Oip5dupD*bK~AR@Z0*!^Rq402jlsajy$jb!1}%8E9`%74MV)~<7kPW9gq2Z&^)YH-BwDx79EfMY|eb-d4uyav)u1kFP<zw9`{h3r<(y7Kk-TMXHS&<s3m_1)*=7xthc6*<ooAb?p-SC9rGIJr#uI+dZ%NZ{HeH{OWDVD!nxD&O!z!cGoFRwIb^{x_+g82K3om`Y|Z)(`FEsY-^%kP<Ng`=-_?GvUR(D(_@=hEa6gzAenEb%9nQD9_`m0Clbg$UvmH0(``Q{mLciTPgmK$0Sgw~nsDwOcX_lQ~@_9bTYTfX>roCz!De-IK(VuOq<GC!$Nq$GrOLjxO1DoT#?eF23Z_n(M{FWvmh<E-8zk^tCp00<4BfjTZjE9OBFh1u`M7{f;O_0xb=z;a?(PZ)UMIP7>eAM<(VgKLftNkjX-tIGy-+eyzZ!f2dZ`(5qe%q(}3fHTD6%D`DdFf}pV4H<;Iv@E@d&;?^cJ_^oH_PS~XlK#4vX9W6%i;PS+J*Q=x8*$27UzI^gEHV>^w=Tyi(4$77jGR#p5r$8J;FS?8rS{#uZW+%Pkv9a@3NqOroKV^*yi6z+_>U7g?(et3;Ztf*2Ht?+p0KksI^tjS8d;nNB)EE@K;@y-%ZTWvp9FU-2~@J^_JrIm@0#?u5Fx!_;-_LOFx94!1!-E5B|En@_T{)<=@CNG8+Dg?`KKe_s7uA1#6K%GDOCM=9_~2MiP9t>p0h`7J+@&u`|e%k}3ONvxp<k>pb${XWqg&PxrbwCrr$TUpyV>Oby~BkM;6X_;JY#rM^A&@x1N)9R85a*uO`4<2*Cg>A3i}JIHl0>Nw$i%&iQ3-+QvJv~$0#wHO2c_sP<q#<Hf||3<=}vShdD!n$(aVY5zyzoDp{7a5OB;2g{?2Y&W3=}+@|f2=Q0a>Y09kC*<jjp~T=l)lFhKUA0fwRKS|v@`El_)iwCki5l)i*NV44?p;@oEI61gApH4<Amg!u@UD|p|jB5fn!f#{Cmr5vq;8njN@3uFX)YZYWYEOu5E^`g@0_KoLAXLuEx4o^Rf8m#`!oWs9#swWtsjG`P+1s^Cu&Jp*$~JcE5uE<3wqX^_R@87&ne5<@5gYa2_!9k<@ET_YmLs{h*we*e6t(F8yybgkPr?&YAM^<+;P!IuLnUJQCl~YEPAV7Y!8Oywh9SZ_ZpP?J=W=A^y;QoG0a$l;5xHZp#s$-w@|#H7_E6&Pv4Jyou}Nyb1T~u4KfoDT#W!+ol8tz4vSP{F9$oFv=CYRZyHX7cDHf&`;gURDb{IfB#c=xZnTsr*7~6?@!$=910#83QB8gQ*vvvPHjn6+KQ}`+fe<<ZODNviUX+4$N}W$)Fx!5zU1cQ#?+6<jmZsJ6xXMINUl$=L9Ieo`j-Z-K`uu9jjW2|M=Xl3Q!kURlh0C5la=O>&yr1Q3fUy@VNtx9Y9ntZe@*?0tTclBHF*?u7<m-g%A$BMbs%{#xgWJJS!oY)KXOlM7jjQ>R~E$`sO`xe$Ze=PS!qjh8?ryODcPUgj74!{sxP@QxgqsqvQl?)L$W8e9@&#zpG9#Us)byKT$AcbR$7%@lU$uziCmprnMH90YB_QRa#^YqS!q#nS#l|A5ppSV2^Pi0s2aH#xj5B<tkjWQoa{_3Np>ceVNqP3TAEy*>_V+bR$7JZLas)wL9RyrfJJd_YAteYa$V|&WTg$rb;)j253(EiBNoMts9xkoWFM+GS*ah{hunnPoZN)mf<<uvwG}yl97t_VR@#;vNNz{{gxrqYkwtMQYG-mMayM#sveI7UZsZ_pA94`6H;dx_)KAI%$pff^$V!Kj2atzQgULh4pRp(&PW_xboIH~HC0Xe>@<{UNf)YucL>)(-M4mz&PgXjSJcT@mI+;9&9L=J5F?A|=F?l(4Hd*OB@^bPj>H_jA@){P!>#57g>&cs_E6GaNk~fhPs2j)$<gF}<w^QTE+sV7ANo1uv$V&H;m8O$-k@r)x$ot6$SQH;*QJhOXOwJ{L$D;TY^%(gSIgfghtn?f?k9?7OfqapCjYaWo>Q(Y>@&oEEveNtH2jpkeeDX8$YZk@D9iV@ZRZ;9reMMIKmaK~6($pdjU{w@XU{PF=>PW6gE>CqJEB#vomnWB{z9XxmxSRuu;!0GtAXH*eT$x&wtkj8InOu!pid>CclSOeIYE^O_vOCq4th6@So$N`iNA@It%%a$v>PGe^`%oK@mDVNukQ-5JksFb{SQL9uKOlRMEmRk>(voBgxjOYv4P2dE#sNif3F>pQDvICGdqP(FJNXUyCG{@(CHV!5;-}PK$WO_SsXvpI+R2Z}52-iE56Smf6#q*7iTo@14)sT}((~jy<eSugk#CZ(uqeJnJwv`k{(*Xetn?`P2lDsSL*(zt$5|8~p=Oegkh7_2WTpGa+2joBPI3l0l|}JxYBG5@c^h>LS?N0RHgY0$1v!ztkwx)p>U{EQavXIoS?Nr29C;~qI(aF1A&cS|>NIi;c@fnhE1f}JM2@A-BFB=KuqghPMe#Q*ile9#$Wi1m)UjlxUy#R;!>M89aPkNi#Ua#Ca!^-?A})^q(|=X}&p$)Wi|_r%_5b?G_qY9pKl!L2*S`+|g1Q!yXYwKi|I`CZvf8C+{{f*XsQ>'

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
