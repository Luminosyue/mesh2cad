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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_008.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_008.stl', 'source_sha256': '3d9c180f982e56a6ca1ed3c02548f8bc4cf127f2d02af98ee9ff44b05661e656', 'input_faces': 624, 'input_vertices': 377, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2945733964443207, -0.23224572837352753, -0.21624037623405457], [0.2776082456111908, 0.3242395520210266, 0.37740638852119446]]}
GEOMETRY_BASE85 = 'c$}qN33v`y+n(5ks(lY*4GE%lYMI2oBtjaodxMB2B81pus8XdZDXNxwHMUTDkp#&Q`xZM@+SgvSRjE?jH|Kfo@y&bWzpnrK|MWV&?{h!Tob#M*=FFM54eppdM^T0UDkyCx`mDZGNl`?~uM}0{B1VlKG9V(hR&>mG52YaK;?Kfwf<gm>dw3{u%0%yh5wQbCc{fqLn+|H^T|@OAG-A}~QQ^`3MvNL5A@nxkQLz!G9y>TZCc?~DtJ|<)4Yh9d8tP>A|M=%=hT!OM`AoWr&Mu91wGjC#hkq1kES*fc(KUp0J+5<_U3WekM7nag$yo9`8q5Bh?;jAlTBF_ufzHyQq-)RCub}HAKc({ZrzKh6n)@J?b0TvO`NzLJEp#RHB>8L3r*69I!>gn#Nz39Wj>9pe8^=~tJVvEos60zomLFq%K+<NBSAS|qx-<0Aaf&l7nc~z!i*Y&AhOMOQ@`h8KE>~gJbB9v7TEX^=0sovLeYx)s6wmxQZn~pbd(w^e<EUQ8$2Un=JC!~`?N8ggo8s($h;+SkUaD9B#$%6N*9PU_cy{a?K=nQSBa`|;`GU$(Dp#fccFx*Ey56UMBKgOB@1`5GyOVDGwRQttzib-m+Udd^NAs6do~0{}Hl!;Rx1>@0x38R}>*s9a@v2*i{c~*~UE6bTH`#-_Qom^l>qvK={gV2@HEZ?>yRPO)C0$GEL*=V8mUB5SuhXOtZnTl&s@;|AZJwLTSAM@7nw9SA_L|07yYnIIk<F<by~#q-oyVUYr+U7BLva{s!;aB>zj&K;ZJfG`aCwWQ^sMyu6ZX?}u3e-Xg>zDW>R)*ux9dvxXFrht%`0@BkvN^pxi^*KQ37vdP+W`uJxbTl9Yy`DJ@-08{S@+$bZtrW0V+?a-ZCp)f91>L(_<9r&WHI9(R|L6K=r7FI&%5N52q4-7Mz@(h3@z@<S6yeww9!;^>6dMoqe9lF{=7<`ExgOe$j*@RQ|mJq$}F?{nXB4PgbR8p=(=LQhT+UM~~1r&FFi`ZJt2a{dZFPjo~Y4+>Nh8+5h$}(v^}Ksdim&{F?R6f6gWB{p2v!`{js})W7l3r|i0`+7Z&VoCWt%d$cvA8%M9wcqtF>lfR`a1v5!EI((l&*xHwLb&qzI;z-Iy?Xq-Z+c47gmZiU=@*At9I|lwu@hU^w&LI5!Hnra|R_A_OdhMsIbm!mS9j5YgrjhQtI+4p+JcRmLnfT-&_3zAIXk1(mOHunQ-T9^n^^YF5pXQ<Z@G|LYyEq=72Q8@IWL*mhNTz!Gt>N-d?V@?2zG_1KChNwxgEDCym0Ci&quW602gTp#uwB<{FC|^8YHXtGCRSztfb?Tze=vA8wX<vvjz4t_kMn@OTM5tZrFpMz>(1-!W$&e=tHXIcL~Nz?;25;-9F3z_L(-l58d1G!>@Uacx?;p}JegN_P`$f;rG9rcESpGr@lYzqRqG(>O7?i3&xJqVlb(gH)_y?u0j={w$~(#gbDY{^YOiu)IF~;zjP+)Bre&oY^*7OT)-j+L>mO}AVqY(==1n+`QZ*@lhwoilFUqESG*2A|o6&fvRqIeYwGuZ-*F0wP{JeHLf%;+6$_)EF*W2>Eey2z6;`u)-fab9tkVv|7*d&@KuElSEqWa55lJ3eKdxFb*yq4nV(1-O+pYb>@7@v}r?s|NS?mv2B5w7=nb?SG0{pf{M|Mf-tNIxIV_s9D$3@WEYEz+GMrg6XJ`Dc4px?_E1x?fqk-YSjet@dL7X}fOCXC<sJ&$FlAq#I`^aXjNaX&lvfPtqMTH}kwbpPQa9YLTn7KGdXO?uT1zoatHUx*D>N%KP`=UiQmJ<r}5`r2Dh>=pnc7tBE|$SGw-YN_ToRr~8$w;APgEq;mP42GDwub?rn?dOkQ~{7846j-me7+TWw+p<_(@bhml<kFP=Hmk1!;`RW$mH(H*g`-8UpAw9R9bvp8Ve)>B<Pj}qq{X*csJnrEi(LB+gujJ?a=pk<NS<Tm(%c(J+<L{aLV|rG4voPAv7!7?$H#(o8_3pa<^#y8ItHHD`l>_x?{kn|Wr0WT7Xn&wJx=!;)`y$^aS})~Vk*=1Hrt%HHV48=@gxc&s_e)ww&d&Zk{}a#CeN@@do$nhF?PwioeU6Z>S66s{HTBs!yROZ+&+8~-1I-sL_yW(rct7$}^dXBVj&fh~{0m9tdH$q6uZMYYq&wH`pz9rf9OnH?ww9^(adA$W$@}qI+4*^YE<f)-Zt}Xebj9Jxdd+V9Ts-OGby<HZkNcnX60_1B1D?^mb$ot~bS=!_d0T%Q?QfM93GDA5#roz6-2Sb+?$tK2{QSy&i~3dRoQum@`y<~kRoqV{-AEkE`;M~dynit|@_eY0M9)oGS5ha_bH~*|*-7Q%KCBgLME&Nxno0KwS7cv~XT`AX)UMmRsXTRVSMt|~ZK3rp>&Db#wExwo4`hAE&%7>P)Sa82g|4mkqjjWx*<~Az)8KiB?eky%-o@*6bs(4j=q-<*q$}l<Xnh$6hqCT<m)Ft7%DiuxA5G)nT=*-k3$=LqMe=v#C*AnVht`GqB8+rb+I4E5tH?Euf6GAHSID{^GL84E*A&v7kJj)!PXCGeQPy2Evh)4+`OA$|Z*N~3Z)44PD$nuB@1!dUYf0BDH{gBeuSZGOriIb`ceXA~>(mIE#O3Us&g(1c&3P*SQ4iKLe&c;({;RwXEK{0vXX$Xdj~gp?@$+8N9RvU3_l&S1^giUQcAcM(`@UL2_N6^Z*H30r`D)Q!eBbTzn(j}^k-I#<Yy5d6E8TVD176<)=8&${T*K?)?1wadYMBW3uQHzfPAsJRmt$e$^>qF9x4aLXdSQBttn~PuDKw5N6V{PF@GAAA^}Z?VN~Z{ZFRt+gJ)fP22J>?~*vZcWNms`4epw&co9_qlJ$St&Y@q$EtZP5_-Ai$LE~5LLt8xs_pXc}az98#~<!L_aT|HM&z1tsCIgb8cQT(#5b&uiq&ftDi$#093=f4m4x2$W^${x4-t3UK(ef+G==~?KGq$s!Yom1v;KUedao1T>(Rm-sZyH0-Q_FnT&pBF^B^P|xH=~?KG8ZA!S{gtz;`T4Ur<Y;;py0WCjIlI4J?rI{J-|d21ITb3<dUrP8bJ49`p4a&PFx>l+UDuwDrTu|1yr-MLtINl<PPIC-&byW0VJffRCU4y1Jf6gQ@4Ifgwj#gVx_%db4xQiQ@_n|;t{eMj@bmgkwzF>Is4eC7ex|@&w|Mp(=jUd4&;hr2@=xUJXWq<ktGD4M*6aH&bBi-W<$Zrj@l$U7lireaM`q!pZgEZ=&d>XG<I>#9**S~#D_i*erR#Qz_q}<Zaq1hYPg*aogdPh>m)4z<XZvz0M_Rv*SJ&xWOui2|9?s(P7wLYYkJ`@jBX3RK-xf^GwCnHPmr}3r^P_$^_e0q<zRyFK?{8W{*Ohd=bf1)U>prPHSx35lVHS^ju4JAs8&lZdv4QW;X`3?ax_sX@Mh;y?x^(}Sb?g4`@Y}SC+q<9VRqoEa?7IAXaeRH6b?JGemQz<#-175leIwGXb)>wgMgCf&E~LxPQ{zp;HRLZnmz7dONSB}ETAAhSpAyIW`vZT|eZbIbuBE)ZAGleC-y^YqP(N4sy=Z<RItP{aA;!oje2y#aTU?v+Z>Dmk{f}BWf^}&h<(xcW3tfkOmvLk666(*mwOa|TecCxMT1R@jNP2IO_j}F>8%dY<jk0d-8(mi`(EiTaf4Y9##qV9eH6>ktU4iFqrEmHC1iHMBbyl0Qo#!{d52}~m9&TaN<^8ZLdN!9M?W>I*>$zTOe{SjW{#>nfkMwu%UsrkzA-|6*>>wTQ1=>r0dQVf*8k4TqiQ{$Tf1md`lj2EtJ$gy?xiXt)*me1RM1LK-lgg3bYceOZUZ5Gr9d|3$uFLO7j#ZafKTwhHFT-l_{iFST(yjL|txyo{<Mld^ck=phe_wOmES$pSxWC`2v293q#tx<VuN65*>q{SShIIKo(beD|_Ltr_U6lf<9rF9B(rrHJ*88mEXMZPMe{><~*88vi-4vcDE&oWhkC)y<okQ2JcuczWeyx96oYspge{Md1x8BEFO{a0x1AEhV0QtRM@tncBbUq;K*7<<8piw%Z_aQznnqK~dU6;=vj4u62m(MYjYI{hx&OMYb){Lg>i$3RamNw&aw{=Yq+x7R(PikhPeUp3+W9jlaj3Y8T>GC;`^LZ5eFZ1JhvM-t6gP#1(`otIfTu8sZ&#ueoOOC~LXx}QIQz>;mW?eeh(z=f&-8u(Tk9Sx`<t2<GT|Q6KB9mEfGLqxz^<Ao6fA3swe>(e@`<d=XMwvx?j{8XgYKMI8=h#-8bordn;ni}VeZIXrZ;Tkq@A1<4q_fpx(&ckbS+~wPjniAXeCfQ@@!KWRjiC0tpB$Z?=SAIo{M?q$W1-9Ev5p4*{N5>@>pJc(AYDEOHtJmB^5t{mdH<3wpEE0dBj|gMd|qwo@_Ds$%*6fn`DvYp%er+QZe-s?x_sX5ntO=-rE_~rm(T6>G6{6<_1^jarCp@I_Z>mft?vlVS%0%GeUEVVdduHyrSBS+E`QfB=1!vbB>B6ErOV$<Tq6&$E`67=^!L8Y{N_XRM*i+&>GF3USHSn|FMU_CboslIOSwV1{M|~{t?yQP)3^LwiE;6B^tu<H;~XhL{VIPiQ@qQQE`N8Eb?dvEGNKKSkM#Y{HDn*@?|lc9bn82yy7?rRFMUsRrgZ1?_35iPz77rOz1mfK9_jLTOiP!)W2z5QNteHqzNh0mseb(^>5eJwG44m`JWhFigWvn3yKp@1N6n--b$myazw=7E^_|zXB$mIoNZ*Uqweh6O-<>U8{_bp)oyz4%->)67HgmnJZ}R+|U6t(mwr>3Vl)jr=y8PYT_&I^?(sy}Fm%q#Fp6PrZe<Y2syR&5t^=q+#ynm8@Ct&IF?*#NYOG$UlY`}5(o*G5hpUdF;lk~d<OP7DQpj~{y^$r@#>wd~!j?;L<<w(DmP|_>#b6EO)g?_dt-zTKsX;`}aI}Lr-E!L&qfmpiyI}pd)Y`kvDl;-h@+17{3slw+g^6yWK^L_YSS^mAsnn>2A-@RD6{JR%NDDPj~em@iJ_N$=yL7kr%US^SI%BvJr28G*x5+p?NXJOVq2^v!GfAy1~26gKFe}59R-Hc(InYI8ofeT!3rbWPc;KC;r_Egve|H@2j%(M`=0bJltlqqmKxbR7aJsGwQsONLkC2$V7z^N#6D(YJZpOLVSgl&$k4N1U7;8sjYz%Afb9ZA52;MF}8rLmbx04stEtY)VCz<l7srycC=U=#d-S=I|Py#jvd!CYW*lqs+}xbX4xV7n)5AEKW73fCp@5xBr}C|}?M@cZcBN5FI7RvQWc^MhM46+nF@z^yt80AGQ3FjE&ZH3hZ+Z-Kt31FR0-1^v<j*ciO5nN&0R0PBJaY=$zMp}wZ@@rB(Nwz{aNIO-Bu0lW~(s{mdW`Qqr`3cy0(RvYR8>wsG^)dMyKuY>FA0e!&dVU5fJCV&fEZl>wL8Q|-&t`dOD!H1Y>xS9Hbk3oJ6*1#;_Jn$h{4`YCzgNu41QJ27>-~xN1%$}%cID7(O4}@)~tqqfa)4{EnCIM%GTXjqV4hO$yrpIQw1$+qp5bNYN@B#Q^tc!=h7x4YbOk2&A2|NWZ@C?d4gZgg4Ck6Ht*iNCIbEr$;X>fr%Q05NQmkFO_*pp#9ZEM3>;B9a#rnA6X;8q=Hftlc)%_N>PZGnx!1y(gvQ(#SS;o}FpA8dm6G1Fi(1p&K*3mkwl2cW*T@QHyv2Da{~rwQs3*alo+50u#h^##GF6YQN}Yh!CeYhY7wE2h@Kw%}GBt${({N6mE7OitiR@I$aI13JO?!?pyt415XrXy91z(coQypMZA-uMMnY<Gqj<*vQ7ikr&v?#v_my*a3W+nLdU6Q`o}MzE!ZVf^8bweggIru&qSQ6A;$~#PJE*=!D$~o8>zVe$!BAFZis4eI;yy`<rX9ftkt!OM$obU|SVndGPkIc>}9}dxPf!W(Us&enVlrrZ5-j8piV)#?s<fk-v(uxA-OGFQLCIegXLl=sUrmo9P+s&tMZ=w6B;4+XX&@uV{O1w7)idN+EUyaSObP7^|R9vI7;H?{mca9CZp_9_1;(=O|AzQyVjt16BsF4_irKIdDJNiULc57X|-YVf;s7E|TEqffvEggC7GPxA7~;3p`@uF60Fsu<;wn-@q6Oo(*F!?71-hf>*{|$p*{?-Uf54GSC}b#QYX<y+s@s(Z+JH3w*2m*H@Hx1?a*x<xt*R#E=a<uZbU-DG#s~_+8k32j&46?-0Uf0DlKJ!1n@gg6{=C2>b>7Aowxhc^iL&{2Pp)#l0}TUKnqSH$lD$=7-=_&D6?+?X6(*Li>VY4~DHO+8zRX2yB9jm~(h=Tms)9M$yJRunWv#^Q{WMs;Kh~d}_h37JLMMV%mzB_%E<D_-_i^E(8AsPlata@G|&r@IAom;CsN+fOo*}U@R?u7x~;6`#a!ykr%us@-@+477s)|5Pc_jB{K!U9srx*jbJMc9)NreXhpyqAunR~@Zfj^<_5ovKDiF`u=!SkUnSI;8+|Iu^FX<kz{P%2>`~)^iQr=2C~W<J@!&!aP<SsH2`vCv-^N3cuMh4E><I1)UIp0B#$%BeILgN7BQNk9@HFuG;OWRO#n{gWrhzA7t}F%a0bh=}l?dDoE@B>sxW*xlj%Z^%?D4Q!zDwb^6m`bJClU5U*aXjGrecct&yN^OfP27}6PO=dfh{{QCwO*nPvD2(p5SGG<-p5;*9LxM<CT#Y*wDsnATO|`jW<JHV0-ZLW~vK&UD#@%ebr#E23vWwy$bAAU@L)`3nQ+=h@%|Zm>>51uvxz4;a47YR)$Xr*h|1Bcr7!1tcYVDMjvo**t~!h!2Mt=3G@Ol37!vF5Ii4v4qz_u9N-Gj!^S^AUSJ*@FNJ(5^q0kbk@rR430_g*wO0!03ohCh0DAyz718!U*aKnnLCi%ER}sXK3vH|bdj;4m--__7h&n%jj}PoVun8{SN5ngh3M>oW1h(ox6}%H{{=n+s{@@LOmB34zseqY^1M}K=ZsY}Kv+*3r=fIc<UI=5E8<+!J#9I>flCTv*Tl`@6gRLy$DvG#@B979CS%qDN&GIb-ze1?90DQ{AUKTd;H7Cml9(+C`cuwR6ig)in6~=qu!p9SKPxuJ_mx+Z<d<rZGE>K08D(Vqj`1r!l7dF8~J!eptz(2qR{;F`90{;RRJ}I!Lz$UoWhS!Ksl<`{mZ%nU&AAnnRyaql6|I$plnHB(NgA1H#rf-3B!G%u@>@lzjF3u0cS;1!DkKh7Vqs-N)ZvlLgVNZtbN7S<pbqU-EE^sT#+=}`(!zTsy6xcS}+OQV*Ew~laTHpe3tB$q6&EVo(cB+{s1BZbN9B8Kgz+iCUGZOZZun9iGOkbNR8u$gcz%?jy4eFZ=pJdpRVfzC0XsAnI7`VVLD6<Rdi-wOM?0&F?+1d~V><@0m6a}0NZq*S5j0TS}=hpx;MFGRX$9k|W78nIS4z@ACSnx66(ZC_#(cpc6J;D2cw+FVh@lTK!=x^hlkQdm%#y>`0U~TXoW@-(4YuGv=hC!%j5X$X|n4@5ig3a>n0lyw7;}iIV!yXQs;Nm=3oc)FYgTTAM)(aR0-VQbguot)kd^m70_;B#iz)|3%!N&o|+W0W!hhZ!&-VgbH82cE++t5tifGxpATYO>ng)Im%M4+AslsgJBhru2Oo8{XLe%(;_F!%()9t4}<9nI9$Ox=OK!JEU@8Q2}X25gOhoxueL*mx-N0pNkazTko2A;A7NJ`{O@BW!#m@&e;*d^GZ-F(!gXVk}1jM}zmq*hd0~gNwGegS{PWy%F<3#5E9c^hF!H!`>Y>%Qq5!k*IShe0sy)8#clBnfHkA%#;CK44wgg7`OubF!%}JDjT1OyueRwyf^X!BW%1m@&Y@6hnT4z?Db&ljTqukPaMj%cnI<#@D=<sGYvA+6rcnAd)R&eP61DWZ5QwdaDOv(!}WqUK)w^SLE!$jIs}dfb^{mt1+h1H3H%vc>_ddD4Dcnm(8U_`1uuhqa7T}9MYI1;|4WGf{^=g#-}e7OgnXs@XJh-7#myIxcOQ|1JLaT)e>U?U@xUx3cG}8+0OzqF)&'

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
