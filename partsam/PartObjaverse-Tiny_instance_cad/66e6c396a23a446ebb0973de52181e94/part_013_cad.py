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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_013.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_013.stl', 'source_sha256': 'e3eb316f978d3af69afbe28fc9009ad123ff6c4eaa2eac7b6692a070a8bb1614', 'input_faces': 559, 'input_vertices': 318, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3656953275203705, -0.3663947284221649, -0.4999913275241852], [0.27772608399391174, 0.2758827209472656, 0.13660719990730286]]}
GEOMETRY_BASE85 = 'c$}r12UHc;yTu2^zhFV6h>GP}0Xt$r6dAj*Vnt%R7VH(UqmCL4R_qn^Di-XbfL$ku1$#Fd%e5CQ(OC13@p1OIeM#PWZ>_i9GwWOXH=A?MocZRonOO;Kp54(ylYb?&yFW){h8EK_6?rrdZDd4bbpKuvQI&=a8{?q4!dL&k>4H`rT84%@Xd|_8KD{HNdPVvKS$yjB3G}I8@#!-(GCH!yknTexdq*h0agRY!5m|mzzaGOPvW|TN`~xdk0{kji##{c6|8iwD!8*I|^&_e+uL2K+WQo3K;t6$Z3^;cU`tI3o_&v@ZSI1_`IQUx6JV%vp6y1gLn*X?~(2Gs?qkNS*SJbgBe+Ti;G&7a2E%aH7dLNe&e~9mK<y%WHJ&EITNANrC^uJS3f9&*i>R3;l3g1X``U(E>UUEG3#bxN5xMQe)x|BC_Cc@X&Y}%}RbI}WF&zW`N=eV#<`L@f+xGt@I_$BDM(dqD~4nq4ZOB#zmeDf)scY<ezI<`Oa7k}j03|w!}@*V2f8npca{G&-5QO~KF(!PTW#1D5sKCQ9$l2HC>Vey-Wpgs0I*QGs8@`*p7h}54}9PQU{FFp_7J1!OeyY0WAJ(CBEA29qZ>aWo?1$nraSNs|e;cFQK(0()R&^h><?MG10@x3?U7hiD(e&omvsAqT|T&F&#m-sK6z}N4&<Gj|uq|>;*lcUa{{?}Jf-ae{>_-{gxPyL6_H}HG6^QWNAt0$rU52yE{y#FZi^YxT|5|n=*@;7g&w6}%-1>DC2;RkVFiu{EBVwl@dPSc+5LH_2nmwwdh>~{F2Dk7iu#dXE+_X_PX9;TwaH8n{5FJUL)ziaX{u4~Xd>DM9A3GmDLO8Wymq`rHfF5=iyzX9s$lO4XXdmiqKw%8#NI`+dcl#f^={qC^OGWdCJ!nd}H6aV+xOL3j$C&SlfR6+mICq&^qwqvc~8@|I%<M(Y6Fb=J)zZ1Xr2^lwCijG8kx)+st+U-LB(UMvs-)2T(DZgk2j`c}P4&(klD<FRDQ@DS|mKU2){-Ps%v&w6<!>G}0JM_`Vblis{$K|{)hO9+>P4~dJm#vTfYs|ZDgHD+X-&`0g{d!VLJo5UyFnoR2J=|Z*8GrNx!_Qs(jdx_6x9YVO_jiFSeCx~kGJllWj(pm0zCDWLgkbna$&xY;jGhVKxOi8}ck&qr{Td;Dr6)2zzqCz;W)_or+{Yn5w(vN)ufI9LHv@{w{Fm5lCa$;DoiyB^^hy_Gyj4Meww^f$-`q3gEXo(GH37%zbKx7~kIQ(R@@^r{;}rv6yVDPOusS56K7GRX;(xuq3*}?(&V+xgj?{l(_F2it5zHsHAyuV(9)I*(?er>{$3tAiZ`VND-ym>3@)r5!Cmdg@gZyeOK4D%kGj_u_ay-X<H*Xd^EcbmbeEnkQi)eS-=cw1(&|m85en9$9;~f|W_LpVhn^Sknc@J({fct(bH+<Wv&(eP?R>FL5>G#RR?~|Iyy!EjY+GX*74qqE`QtIjScs$N~^DcaSUnJ%y^UVw#TelpL@{fN&z51H=chO%@ES0~P|557c?zRE_wa^bzzC{a}pG!r`eTr=%{;7<EXt$$z2ggrz@e{V=zSxJom-X>LZSgZ7!q@XBV_mQvEd$>^Fq_PaO%rimJ$mO6l%JOm<Hy*QP3r${3w$%UhKz@W<M!jYUpx5rls?Fhy~1hf$LIZ}{H_S}b93i=%>Vk<G~72WyJZLNSC`Uqe;>rixWBX;{mpogZG(*Oe(>!tH)H;@M0LP;(^fWyZyuY7_G_;1=i+zXHKkv)9E|;d9-i|y{yuc<A(U_GCiORR#yB%C);c8p^WGZx6DD9C(MP$8Kltf7)blyJtk-FWFyCtrzsNl5^hWMq+*t9KmL9Fjn;WyEz1H3J;M=<vlYLF*isd-ZpRW!`zgapT_t*J|%<qX0;oGzKmi7(oV*cGXT)mS~zPdB=U>vwE^>kTx0_S~n2kWM#WGZ|!auU`P>xu=KPqg8a;amD_K!38tEyH>39omSW9xCk|7TFHhJN*Ujv*vyq>z+}B`>V*C;+N@<dD;H)1;(ZR{Ymi;n9|?gc9QaykBVQ#jK+Qc?V7CLledfCzL$*S=xyjf){dLRx7{0od>z+i{>`WZ-_~rK%p-yQWL>TB$3B#Awgm0elDA>~(#D+>zjx!=7`Fqa<Ggz68u5qxu@mjQ_e93Q`(^OW=c8mED71EO$lrWz&|U1i?8#@bE^E%S#h>wfG0IsEOaENb2EI|+1^3H**hJdBzaV^@$0fO*s8R=||F}!}+^)C}ddJF=@B4pZ{<genCi}aW4P_rP^BsKCRvq`t_;d#Q*l)fOwMwod`*c}%udjixof?jDZ8@7)+8@zJ>X~&C^SgbgtlwsAMJa!>k@SZrG3dA2aBuOw!!W-aE^}l(s^lnsx%ycD^w^xTZy%GiN6!BQ<?WAMFn{Q+wu(RKU)X2ryY}P!7JHodj&m?BY_5B8U+l><#80j#`|!gJ&|j=4$BSR=XW74X&xQ8u<%7i^ojC^e@3Y8yqXoh@jy=Y_V|=`ferjH+D&_Z_lllAbYpA*2MSRyptS{EK$uh2beoTe`Yk)itR4;<-)$_a*-#2|Wu4hkq_~x$%#CJP_`NZtTeZ=I|@D1l!ncsqn?!<iziG^=IC@J^%OE`X~^&KMhoRINv?X*hvspERUw-sC}`-<DnSnrH`AyQtSFh}~Cc3S#>koX(+VgGE2?kDp=*jvoghG$3VkMWt3w<XWvYuV1r^_~xvbwIa^e}5D9m->S>vfm!JPyAWsv7a#PvTv|jW5sv%U4cAkvd`0YN6C5f<VK$L_K~vRcsmfj)u}$lyM6K`%wzh|CQ{F?Fqxl6FPA*j3xsda7A5`mQraY($1@=1AN_Ww?B~pl1;n@P?FRqWb*y9hTu1Rke@EVo+6|<g!;@tmO<a#WShio2dARUq@e?M=e7}CbtV>fj!nf&d<alL%d433AE51WbnJ=O}Wc<{hEB>6}QodaW8`^(4O6o6k6YHjSqJ%szxepS*^$y%e+pV?I&e_4@$A6xN{Pgw1by;sYi{D`9dH6%Sp&wc{9p5eEw6pAQI#;^*55LB9j4yl3;xa#n1&BXr{w`eqg}#_q4b2a}-aAhA7tukouII3!oR&5L>$L4|P3#l(v{>;QdSiakUB=1&K_3I(etE9U=T75d;jb<v=UW^h^IMZ(nFsv8BuW0St;g|;hG+iar=`q8`A!#P-`wee_&aYbz<I)*W#2mJn)nSD$aB^o1!W(1?XvWnV!^U5d~lHY!B6(N+Mh>d9NlRv{h{9;@!jHazpPVs$v$V#6sad-tNi`p7}?k58Y+Inweq|&V783Y__k86={C78x5n~3P~T5{_X+Y`zoe-=x4GvK-}TW5$wysz?s;IxyrT7sk$L&&`de@wbGZ0s(qz>0be8OMwE^(;k0COS!n9TBhx1y(H!9r5KFaRXU!KF(l#qJbw~+p`&j#OK+)eyv-Laq2r|y@2QY8`lQ0-HRINbNklchgYm@fW-M##U;_1b!=yZF7E$++#73-gzyQY}3HY436_#_#+4pOx`nP5k{1Sl^BLm2h3=pC00uc!Yjr%N30B=DN&n_}!8*((ipj<$2g^B7EI1Rh|PpreJ*QeVW79Cg#IF)z;%TY3KgO$gA;3rmXWn&X#eIdIG*y&JXjI#e1mii)Te{mh0^%<G}Sg`m<&1^-cKQ$eglIaxW<Fd0Jh9Zw=id{iM_u^b^~Q0pdsYmwl0QL+pzzi>>gr^^G>7eA#)@-@?p9_%Z93pdEAX!`I#C%f9>SAlxs@^c!;iq;ebNer<|G`Kuk|`6|po%Fmdw`|tTQ3id#M)qb*~9s2r7Qh(oy;?I}o3yafQ*>9(Q#(b*v*^K;HyEZ{T*SExrAKzyQ`rFrz(tf|$;wRLWeS3f|`<Zx)JZH!F%lhh41N$#a|Jw;T&X|Q`ZSE-C7hCcS_}UAf>1gMXCgMkpTO;@Pt@QKB9@5Wyf5rO)vy~0&ly=OH{efw#0$)2jSl;7R)MUK>a&tBO-}hplVVRy2^SrHadGS*+F%MhvmOy*$(Tn2YU(Sbl-;!1i&tJA`)0Rs=n7sx0i4T!^>}s(1k2j#5T8=u{_gcSrES7$L2m4iP;~aQjWG^{uA^du;(H`42FS#!pn`0i-?m0=nS?enM`B{<k;m>|0?+3iH$vz~-3G=CuW4SzcxCY`rnu}fMqI_gWoL39~9s4z{e8LR)aV~iOX*8TF>)wPp;@|(gNv?N^?8EIfFyCv7?;Jq=XTtHktYyUfh`-0zlJ~uXM$7Y^|GLT0I=*sUzkHSQ*Ir{DG(5xPee8(@ykFE}j?4U*G8Ow4V{c`7&uM!S0j(Sc-`+q!`FGza-5Tql=GkEt{AsUyL!XY2_cOt(Wq#J4;Q2|buBV}2b&A1zVlB2p3*;#e-!ENCmG@72W^L3T<SftcZBNVd=cfd`&(j8P#5}JZoF~r#<vfO>-OsWiKStB`Qva(3Q8;exh<Q(|ohkc)mu>MLPFs3P)}yX5@*b#Iqw#Y6PO@M8GFsjjdg=y_t47Ito?mZbKd$+Vn*#N%Bm1;g?Pa{TNcsW(L|>fO+_xNgGmo9adavCWit?6a&t?B?*@O2k+L}-3|F+#_<asx4ue^uzdW(9jt5(SSny$xIqI}SL^gnyeu^2B_4_|pt(YJt{H^c?kYuT_HzP9Ts`ju8KNZwEE%ZqhdD-n)ys@+bJ=i@39<^5=3*<ab7=-4M&c2vT6Gy0k6&*uD8tcTX%74Ws-blHFYzEs|S7D$0_*6Awm85)kk{BFC{2<xJG$V29hjZ<acvh(FODIb9HdfHyu_Z~|_e==r9V|-~NHp=_n;tS<|#2rU@TlT5){AFv7_eAFYQPQuR&tV*yn?o_*83CoFzU2|}y(28IjLVUY@ZQaM?r>B3v%frFm3$-P{qX#$XirZ!=^slAW87IXHetMLBeqF@Ib|TP=D_dez2nTjdnBKEkbnJFSJ}t;KNdf!4Dw`O9w+mFXIDIDYw51?Jovyx*4tcO_<o~pnkDT$J|6o8ZPq#XMy#v6e-3rP^SA!I0LFusm?8aQ<vCejdIcVo@z)c7w=Vs93+?Q^5#O0Kheom=KCm3?wtm=xdBQL{%6ieVE#?_xQagMPFzRoY_7q8wewsc&z7u?UC*yQ%qU?X}t`I-8Bid;$XeaM?_oj%y*ahF4v?<kOoxGn5^M#Sn{v7JPKU~)N&Q-+EyGy<|E&c`f+qk+({N$UmKW{Kep6k+5;cJ^eNWJqP%Q&ieNc^BE>8JCYWM6Tnugs_R+xTu`nI`)*Gv^}loBs&knlw$GzdpEPJ~gJ?LI1S1?kVeSZg1(YTPDi&?yM^7RM+j|zfMJd%mDd*W`FA_-#Kms;=6zmu^Rh4<JD~VTKq8S?-v)z{$|G_DWASfzC+bqF8j%8TjaaKm}2tYuXu0luk?1VvJN%7E#Dhz6_V%s*fi-kF_Wdgg*TJu$6S}-8%=ZIJob=(%X??*Eh+E$Qr3mcXsLhZbotJ-A)9=!Z27&s$K6~J<HyKMkbZJw{W8>3xr>aeupM&WBF|(0Va_`${*CdnP8I1d@2S$iM?Wy$cS1ep4tZa0c8xhF{Wj(>^tvPV6V~(IGVi=>h<<5v8Y%nkSBu22nOp9Ea$VV%R=6+whJ`O=-|qER^4av6_~Gy6dt8|T*w5Ifb(i_eOvgB~JSmFzytW3%;Tu;%F^(;F@18vp`j4;CrBjyVNiLjq=B#kmJhVPN{`M(anP?XEzyB27zuN!mQ*`y}wf?`Kq8DYg;h?&FhT?S$#doQ{knfVeQs0r4{y|on%R%^G)M8ZSD^{A9T#Q_XnulD5Y@s@nE#$%s#ZJ^eHDM?6eNFTh`98S=bsD(?xd^pBxd_>VT7|5%Hraz*kQz=dNcN$wBm0ntQ}2?8lOIsOlE3Bg0gn~uW+?Wd79;zRD^SajE0BGu7P2q7EVVGXEZLRnM0O=VX0BCEA2SpOQ9F=>$nMl4WOs5Nss}j_IX|@^IX~G#^&wlxJ*mUVJ;_g~56DVY?w;^iaejv4ic}wRMRIj&1#)$A6{;_}3b`D$EV&%ni|R`DB0tqcRUV%*6#G$w$bRI!RCjV-at>-9at?BCYJPHVav`dPT!`F>+LPRg{DS&~tW@Rh1&<XMVkoXktw^p)u1&2@uFl-mW+<-3P+W~#j$Dmgoa#mPVlIpGSn(?ce5xP0IN6Dsmz<Zmb7CmY#!#G-nwy-H>`5&|_9VBUb|QCTzFII8XHr$}GI^}no1wS{wJNy=Ihb0TT${NIW+<-1P+XH*ja-vlf?AxcROPM&j}`yMQ0z@DPWC1{Qk}?7%$*}c@wb19vr}`Dvy<JZo@6)jchnZ-7R=Xo48<?0Dt9k=thgXUu|Ks2*`FLl4JHROcR>urfegg~)SBd)%vS(IaS?{%kIbpc<41<#qEv6PH}h4Lq4-}6#ST=B>_B#=W+yw7y{K+vH|EQWp*WPG*iL;(R;qHRxCpP~cZT9p)S~2~Y-=fo;(QFnxu_20Tx1ujGuee)g6c)~Vp~fv6o1c9e1&Q!Um@q?HK=RJ$58A?^(Xt0D^r8WLA>{s8Hy`06qlz4kOO${%QF-gpsL&z;IZO=GZfdMmLiv8?&>fU7iK7SrRE~Lk_%8>$OXuCsU^rIn7g_R#bX$XuT!s(uak2+h^jp1WGF65^&=N0m!?)GS7z=?GZdF%C@x7YPcF}Vm1HP(p{m>|&Oz@DkCp$1p|};b4!I8V*ovXJ97Az2sw=q|xh%B+xh%OewJy0X^Vpf8csfII2K72QgY4iSs&eYUQ0zu6N_Hc=Q%jReGmq{J#U2dBp45`$lFXZ@!(VyyWaRiZ$&lY`5{mCoRetX<6h~28ky|mRQ4Gb+8H#IAi;-)Pb!u6%PVP(XOzzB__GKuZPt73DC+}e>{y<gv{lH_z*_m@Ua(1#K)t&6loH{ZTXQO(OJ()YjpES|8RE?}LuWuQOA2Jl*pxz<hAWx!3ktdORP@9vRGp9Wmid!-ix2Ni4oq24}P&|=3pFEMgo}u^<br1Ov`4RO4`4RauRps|H)sd`1@fT_~^0z#GVJQBUq4+iRE%`P18TBFg8TlSV@nz}_@@4V{>Ll_c=5Yf<@nnYLe$<xae&nIl_T-`DHPngZiOlI5hT`4SL*(7$qYTBjsgKByn8(`;#m}i<$X}Q{#b>kP=d2h+olRCTlYduwfV`AEjyjXvF)IdSMQ`e8a&PhoY7BV<c>?uE@&xicYAkskc}`Xg$%_72(Vd~VD|HTe4$F6CC|<!(98dj`98X?GjUg{1&!vtg&m~W#4j@k@M>7<6p>`xIZA$J!ZbJ<uw;=~pE0BZ9m8fONmB=NjzT}eR(hS8F8H%fBMNMiosxR4>byZ_14xm;b2au~%1Ig9N^{7qB^~i0h9m#FUeW<<3eaN$@BgnJJE2$I6E6E$F^T->?+o*HM+sHep{mDDX%c(=i%gG5@v59I>hmZ~Ocxrd@=B!wl6_M2O<nb&M$xu9y+Lf$y1$iKO3PbUBYCL&6IhDGMoJvln&Lt<4w^FB)w~`a7(d0z(YKG!o)GlPDZOFaIt*OD}*5q2$O5|GP%G8qN%H;CY(&X}Fe`-atKRJY2l^jBDsQont8Zs0&p;jX|AvdE2keiX)QLB^Nk*(BvWGi_rwJmupc@?z}c@;T@I*Xh_K1^LnK1@!hZX~CZPf)j!Pmt57JIHC|z0~F8z2yDW1oD3J5$&(BafG4RWGLRrP`rd{ke86-sN=~>7n0-1YZ;1nQ8$w>Q?F7tldqDmWyMYE0_tY6(nzw>fn=pq$P36f8Hz7bx05fD&r?&$=gH@&$>ek7Q`D{GQ{<D>MDj`Uaq4RFaq>@Dv5z`~x|*!C7g=d*@)rJPFm(ob2Fnbl)*{>Zn=tBN@?e$;qgE#Wz~3~chLOWqrZKfVc_e?+fZCYcm}L|XW4T7u2IK}T(}?O%RvJQ{&EF5AHX=7-nQwa`#oee4$=%2i)F$Kz@+fLEveI_sQRKx8#Yt2vIf;CXI+lEle44t7e42cQnnFH9zCb-pzCgZ2O(%yocgW_E{eSx3FaP>ysOOn~{Lh&G^_TzrRQC5@&dI9lKR=v>HqW8n4{6!5{!=gV$EzNr{RiJFu37'

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
