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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_013.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_013.stl', 'source_sha256': '0ff7d40cde290b094079e2832c87043be82583724efa49e08232fad8785b7640', 'input_faces': 690, 'input_vertices': 521, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20670078694820404, -0.3184794485569, -0.2474823296070099], [0.20769791305065155, -0.008591771125793457, 0.2893623113632202]]}
GEOMETRY_BASE85 = 'c$}r23D`|l+sF4~3L#I1NOBs@MI@DaP9^n5NRz1?NpF(ypsz@FZ&4CaDDz3LqRg4cZJwtmlDu?ep3*$Wx7J?2we5YM^Ig|>eV?xTy8q{Q-+S$Qt+UtKd!0?q8|N=j+A)8waBAN_aevF&j-#!ZQ`&jHV{Xq*9Xj^7?zwI+W;rE&uK!s7ZqtYFZ{8})dEV($`N@twI^<TqC04n?Q}rv?h*f^7Yi`fn_RqEJn)_r&%^S6Uwns<BdpzB~TSxV|%8fVFt`VzKwMMLO?Em<us45{<z1PO&%6p%e+o^s0&;?6!Lfl<%c%nq3)nOh#)qRKdu|`qu9W~tPRnTuI*3U7#|CG=D<670&wmih0c7`V>6x<l*$$fc#JIPMb{M0<d6EmavPUCC0`=5X9y(z-4GCVON+D@YTM_c^<os8ytR~Vic7|l;^Yq`>ocNg`)YPh=~T8|rhXsQ4C36VeGL7#h*O@5;B?;HHjRm%J09D8)7Kb`>}&Uns%zwx8b6MKhk_0Mxz+eKj>?`L>?{_<5}?yNX#+I#=;NPeoJ;jsbH{8TUc)iv7-^JGW(@@3KXyO@5(`bG1-#)c=hnS8hGeAE8r1^jVO-1o!k<st6DW1Dw)nYdSdU`8G<vu#0`r;7e*#=F5E(e~lq4a+0>&ffLw{C327Etls_E?BoNQ~NGFCE8EU?2|bkF7snUdS|T1^0aZd^&Y?7xM)8Kcj`pjkKdPL^2GRCF3)RuN}M-l+hP12Z<6WP88ffl>;c=t-0NrNZ@l~K5gyxhjXzJ_n$dh`z$AY@rml$cWF2!I#*2#fkG1fxH}{YJK2P2}+RT?vhx+p()wR4ok1S86%=MqRJj!FUA2rwc(I|IUnR%W1!ti*5A%@TE=wFA)t1GNoo{4{(=VjvYB5y=^0-k8!cR`rP4qxSS=a;sT_8rUf|203%lYehmmnlC1kIVedFJ{h%%lz1DmHh8LCh}9S8lKkv?0u{J??;SJz{U7jo)F{X+I+^x-SD*e-kVhR$H8q<b4{4LaIa*mNPfIe{nh5UXnqXtWSjiNy11$5*Y^JUoNBvyOPI&tiAP7S%n9-MZF^?>?LHRGkKbyz_lU`N#y`B?Z~u|&KJ(A}(QA2O9$!?$@E+w?MfkDGGku;c7vbIuhP%h3?Kt-y8}8S!;JZk^^VLzGyTe5O_))L;KK^|)f93l=kMA=1@t^NB_22fof8O}pFGqN)y5Y{w$veW_Y1-fCsaoH!3G+k)!{dwYULDE*@z6WI?-I>-rW&63Mda^4;B&WHv>xX@!=0|C9`9^zQ|IAUv;1}{>{=7%?xUxt`u$5Zk8o%AOJn``gg+wfIA_ib_5Ga-On-kfJh*<U?=|;lcyRq(J84xoKe&EsMDv5|=Nj_6R5bOA`>Eyfek!@Wk4SFsr$PJTej4P9`>Eyfek!><ue_gHF7Ky7zPO(T`Qm<RxxAlBo;D8Rej1!t+)pi+_fyH`dFA~ys7KsSJ+~t3@^91pynVg=>)CR*F}&O?a~<}Yyf)+Y3{ShB;c3^i<>Gqw4vseM9608;?;WQec+x%Mb0^Q#6Yuw);c|U|r>zh0wDkd=wm#T=xjtAf*9Xhx`e3<O9}@G18ot%6hpEIwpT}|<oBG9bvgPvm!E*WhV7YvLcINzQ?o0AH3NH6emfQVNa%PmLJ$Ko5*f%BEH(8$cJO-Ehrl1}9oMt)uBX2>pp0ww;pdB*~smY>#@mv@0eZtf^^<6V>YUTR(Q_H>1XUx3&@QLMN?o51eiSIufxIN6>R5PD@f4X@QzPG8*-QC$M!aV-3hD*$RoV_uU|3ppye(lXH8OcwzG52w|%qxETv9j~bbBx&c1)Tl3chKy|1J3^1>sc_$#Xiv)Qrzcu-xp`!ml|xi-9N_JKL%VpCtEI`lT*uDt;jU~mdo)E__<DIJii&cG0f%nV!8ZY0xrInfQ#|BT#kQY-=XDx-iQ|FcaM2>SBJTiz1g2%u}|xmb)#|hC7JRqPs^{cZL$CPT*A*!PK@$Y-X4=**|g);=rk)+zU4CCz5l4c4$5`aa=ETrF4w()i*?UkyvOiV&%u6v_viB>yk4%)y{TrMci)~jGt>B3F2~2oKV^o`i#$8p&wtspAMm-)7`~AE+M8{s`#itv->004CO_aaUN*cX^|Y_*-{+k8DRckoME#bZI^px!zqwBhS^r6<@w7bcJ_S#^k613o(<#*U!%X92dD{34FZ^nz`DMABUzW>xWVxJ20T=Vga=E?*`C@)qF6WmsENe_oruyM&^;<612g}p?1yAdj<+5Lv%lhH6ez)GTsW}<02g}pu7d&l#SuW?-klNF<PjqSP&+qsT<~hppWI1?EuIDq4&G6g#{agR~P2A4)40oFv?!L%;`K!%LGoQqKv0Tg-r)KUf-;4PYa4}!J{)cB}8XwE$_*gE-C*X2?*1hdtFUf`pe_lAH;tRsu9XrrG&-{?%bEnDfl^L%$c-r*_PrI(*Y1ftI^16bj%@><5uQ#~7-n;=PO#OMLzo`n%R)={q*Yr10-SE_Sv+s{N=J~;C(Aj@3vfQ1<@A>z9x<1SkJIr%J@*=^X<@fwU&zR?{cZZtay}IxAp953bts~rPUcj8Mbejl|SD9;mr$5&!!kwXm%yUq&XgkjIBIdcExoE%1Qvdg(#BGMBE<a@MCzo~bpEI4Ro0sN<c)Uz~v%hR6_$@z}_WR~r9OmB71I+g|4*pp+vu_w=`s<CZY5D>8>gM<BNR)_j_bvKcyvh17PyA&1o4i!;1E#<3o@hJq&rE-lYYmU>zumO|<r98?lg-WdZh2zIO=dsZA<AQ4nEpD0quj0ehTq@hSgxz-KdsF;f8lBK7oIkMEtm5*@1k{nopODHr>$?tOZ!~z`z)9Hz93)h`vNZaeX}bVF7|N&AIk4q_41kV`T824r|qNRY5Qn++CJKHxsP7h$>(ytvRtlL0T=g2%jG&|xm?ErF4nPti}lL#wEO$GvF5zueq_14A2~~Ft@poo@jIC1@^>)H<?mnt7r%qKUp4f(cl}M#_ez2X@0H+5c<??2?!trjO7J+`ZGZWYoD4jES&7M+xHG=ilrWFk{Kk9cMDlOH-sIc&IB*9ZytlIby3KI+z6pcF?Iht|kCT!1Qz!pim#KZr<6?X)m*eBXQ=%Rh?*1cMPr{y8jF08sxaj!AZ9B65gEKPL@4?gRfy;X0mW%ciE2d{02g~I+q`c`F`(?T8SFCFv^WH>$zwqEao$c3ihP(Gh>vt^|^}Bt0MBnQPF8gJ<>{r6JBd-6L<?W)^zhm2}5FH20T`>-+mkf8f{=KJX7%taac-ndkPg`#-7wfHCdmi&bJkP_^p6B6d&-0ec{ariHaB=^#T;9Ked~yE@xVV3LNB5ih#d{*l<$I!li}ys9%lAZ<J3~+V?}Jh={2a-b?}-Bb)*SPm=%b&a`QklMY;u_me*E~T$a_-DlW_aq)A9t|Jv?zxxScrMajMS^bGKZ}$a~Tt-*VndTJBiBz5nZxIxjKYoj5(xzEk_`x=ihRwa!M~lLqy`oo&(f<2GNmKVe$t_Qy}l+&(<5eVZ@aAJJlU#`cG|Se>zbxU*HXZ}VmQN3zX2Aim##^PX37`<~bG)M4_)^^k-+2cy@63y%*gGC3o!eB+cbPuTX)RrBkQUwemXU%cnFT)yYET)yWGxOmU&z23}>vv^N!xqMG;dEDlAaNi8K<G|z1o6QY#`Ci*{`Ci-dRByxG_R;o}aEJEeJKLCc#D3FqxqoyX=xOR)WcIUepQ7_~LOfaD@MMjptHRtHYWBHag(#1;HryFw+DZJDG`y$TuO<3UHTyHT_psTY#@%TV9;<2gYi{RgermYcuf<=8^5kr@UyCh?^7tcWzvfLg+?z5t<NB7yx&9@$e-FfRxgJ_B*F(#L_3#~Y{ipFN=K4?Lte=+4^)tv9>!;;%{S5jg*3Tecte-)?SU-b$#QGW3Bi7HLeX)K9?Ths@XkV<KLHlC;4B8j#XVAV_KZEwg`Wdt@*3Y1Qv3{m;as9~k({j0f2G^BXKZ82O`kBTnN3S2bex^FFHTASG^E!S{+f`v6`-FL2&v0k%ZqvT_oyzj$WZr+}eY-Wx<?mNP{$}2PjUoTF{pNcS`$5U=e$aBcAGBQV2Q8QTLCNiYP;$E;v|R27gM6_cv|R27gMNwqV9+nIAGBQV2PKb-@saz%;Jji#7>t|P4_YqwgOb~QQ!ox<KN!>__Jct^Vm}zvBld$q`(i&B)FbwTlFM<B`$5TNzvO-}_<qHHFzA=q4+i}b`@w*V{h;KsUvfVf^jGW$gZjmOFsNVb2PJpKILQ5A@?<{q`&N5?e|F99%mEj_KU*FzZ0_$)*C=<oaesd)%2R{Q{XMlj%H3k-{+^m@c<jM!(|&1wf4;*!pIGj^Z+@rsc8pvS;l<7G(y@o4`R-8j`>pqDG(VO7qhC*=ugKr^z4;xx!1jd^e&Im#JNBV%5$;VgzxT!mn|4xNIv75`y<ewWtWAU`E15cz=UPX2Vy-!F>fUI+v&ppY)i*rx<p?uAx0&xNR_Ar|_uJvlG4uPmTknks_j2Z$=dl|<ULWR(`uu)=Wt6*joA1lXjkfQ$UT*d+{S<E=`Bxd+?wqv$%b4S6E8>)Po@yWZCm9;*Kh|gdCmEgU{;&Q?M!lPB{eS;S#v`hRN0q&$tWuWaJf|#%?}C1d939tQ$F$bRK159Whn@5BXE|Q`&ge(U(Q)mc<vfom-9}kkd~5U@$_6MKh<_d3mYg^61JE6mwO958K7oEkSwG_ah-vLAdztvl#9rZ;1n~qht=lPUrR;HhOY|UR{fYM{ruCc3UL*b*u|XWul6XsET3@cl;xc6w@fFY=m32_|6#hwcMRGdgJD{&tcBQhb@K>N8SJswzTVh&2rmPL|HpCw1m@9~1K}_qds@BbVF5#D<w<z1>nD{1QTI+eTl=xC&TR3JJ@nyuc?yGF2vRCnI(Jv`mL3{-<t^cKL4e>R^UgDUw#Mctj`a5OcDm#S#27N}^Y2v4eX?;-H0pbUUo#B{oh<`&&>y65eDO-;}g5IF)DDk7jv|gv|F!960HgL=l;zx*S{e=1s63WWq%c9#WYnNr>?TBf8iLx@p%MfeNF=dIDC8qT$b&l(lKY_m#eNtIX;@V$_KCY~MmWgX$6RnTY#~#O*N4HS+fU*bi&C$=O_&=3(!at3EkQ^P?UdOa<!ErX{nb5I1?`ix4=s%SIUD+@AU(q#GtU7V+bxiB3N>|G=@oMB~{R_wHxb`|$mE&!DzYy2@XQits{~NwCTH8;KiEIBO`r0h>xibDYv_AG4j@SNL^v@it<Jw<C?w3mMR<;wr3!PH-wPWI66VrO1vi-#O6H9T-F5<h0?c<o8p`3l_&z1d0*%$b|Xl;4KwcmmMiqCuTU!e7|d(eBx+siRKi0>e#^}m&Us4R*906j<9XT(1vru8gkvx(0pHiu(AApQZdSsarL<;+4)P&QN9MEnf2w(-QZABUdK=Nb5kXnpK7^fdBjaLhR3<A`bfl(Hw4HN`hU4_4p(AZ4}j*P}bC*guusk8g&)LB(n*8-jle-IO+);qOP+rcHf*?VqHUAsjmxKM1YQ)sgdPug{_NcBQu|Ta90ZUZ8BgvU&Kq=q1V)D_ewLh%Tq>CS^nMZ=>t+`4W72ba{@s1YZ_CM2{WE52lT`Ikq0U9(gvWEO}*VOY4%#vXy1w^P%%Q=1)F+7W!jl9})kEnAVe(O(H&t*vGV4l6XmCTI)y98<kDLPes?|b18fobQz8*g})g6sj^Qv{uA1m%CU9Pb;+|i7n64}ZE2mQI+st`pIOGA%`&<){w%r_pZ`);MA_f?qG)}rZcA(J{|e=lBCix}X?>1?{T2UvmeCjEe@AEY`8Q=3==B?47_E;zhdxK1&B-P&o3^xGt!%WiRp>E%*8VTYXzl+*k5cx%(qr*IpjXqzSp2B0^ErQ#r~O~(0?G<0yAFRnTKnN>?T4WYDtkxS1^9Q-g=p&ne8Eu8F!F}cmexg-U8t-UzBXF>_tDyqL>E>zLRnG#d*};kt0=y3C}$*jBWX+PV#-P=y8&MZt^HWE_M_3om5ow%5q=E11Z`b}FCNMnP2OnQ()t7S9Zb~sTl_C*?F;8KTKfyo1(jW-tPs8=S|9rX`UCQ8jy|>|zA$=%vZTJZ<9|YHUnrl^+80FUS5{nE0elH`lC}!q^M`Wuu_f?@(BqVi*Vi5X2ekGD@)@mtesq?y3-x@(7ekMyt$g^bP>w#f7`_1dJ!S7JTZ><hUZ-pgpVz>&KBvB$vyO>tzlL1B!2a!+_}}Dc{XXY#@H(coUf1>dJ{Z%wEdCPb{2H(CANrn<-#Nd2e~g}t&qnJtQm>VtU|L^{FXfzHFZEii*H^u^=`~KTZAH+f@Oq8ZTCaV2ozv^0_NCF<pGE7nO0QWLU|MJ6e?{xHOs`wIVC^qPYyUfX6l;)Pd$ei&Cw??quT6R#T8;k;t-W6Rv@Xb+@(xyjwM6^t&=;_-6v7WjYkxhuFl)pJtO#p^_O;MOStl;UzmL|wHo7=-eiT-Wxn7JlV>D~Q7}kj~tOF(Rb<hQw!xv#6Fn6{88C{6EKM}9z^+fzH@chil;@AY{;soZp)&-c$NxYt?N&HXnEaupS*f{3aIOeX_`IwvI@p|5k$NvCd7n)nz)-zw$GbgovTiLtHhT?~#<H~ZB?ZUo*-J`6rvIE#YSQBOUD%+2J1G`h%9m;lNU&0<zc7nD}(3aLWD%->{n>a@6W}Igqb{KXiZ8pH?q2ttC7rznRgxVg)pG4Ooz7g91dxZE&>=f)l&VLv?4!c#^4#sW=W0yl)8;EZprgc4Ko9Xvv`g|jO$RnOdOzY;#jxg3o80&lCk5Jz!V$G@PIOBbsvDSJ9we7$@g&k&mKf~t3=5Vef*aBD{<31Cc3Y$b<He(;bHZZ>b#y*5Cp|<1LV%RCheJQpKcAUEAV~b(C=!dO;U#OoOINyi#cLz023e~eQRCgZznM(be8G|{Y{(c!6ms8ZYjPW@_pO%E`KMB({bfpgMd!Y5XdU8JPyP;pDkNxoT(fV8iIG^?|dOrQ{hiTo1^ZXa*`V>6_-v`}?{283P8)GyHZO5t`{pdy?KBWGc)ZP>Q0(HGaZ41zI@GqcWAb$@1T1uY=p!+ipuQ3LT(M$0C(f!F^!gr&;qi^uLv(C@^Z}=`wpby}8qxE&8ub(gQ2haz|vFnQVoAA5Q!<3Cs_6~j|x}mbWl<mR3g8f6;{mKqvU&ERzyH8mPI|OT_>~3XyvH!qYD*KkUzNIa#Z&tRAW43XO)(>!=ud$=BMznc5ekZyiHP^>)MK`6kR`@gMn}~14w!m5wKZAV-dzAAZ#ZJR+Q}#Jy_c>#C7yKsL-9k*WTa<05-`nZ)&Gca>@twr9ZlUZLV||RVz7O7-`o1I9f|^b<-lrMsmei$dn1!E)KFavc#TLTmajs+7BG^vGeKs~7Hif=y$3B5=VSFcJAHzIqJB=-eeaE=3z*fReQ`bUlIcyL8u=Rf(>gyKH_c8tboEoQu>e(8qdnf&wPW{^%gL$F;{wFjp-%;O6#^)G)@<R2Wf$18$Q-}7w(E41@b3W~J(XZ3TSMUqb`dn{vKJEX7UP%96!L;tnd0ymP)6lc<ebIf%pT)Uz8KWs^J65^$BbPpWO#QQ|{dsh6>Ux>l7NO_id!u`kKaYN`pigh22Qm(CFb2!f9)2KtAo(8OjsA`f;rC{ppZACOF1|${#P3Dx>qcKcU*Qj;50Yco745g-_oDApkFEDAYmEN~x~H;SWmjX@!n!GY&e4Ad(b$!+uFASAy9&Dk)<an@WtFjOV4ajzpsfnDrFCy*H8`dQ$7ua5=eZKQ9M*$2{|jFg-IJPM#8*dmrM74Am!V%EULC6j>rDJItRn1LYIqudDf)S3RT#S}j9o5mRU=-FnAUxi)ui7w>2q)TP?dO9Vp?}mR*A8$#8`KScc#9I#JW(^rHuEbjJ4KrYO8|X3A>!}y&Y=+%i&y=u-jl&8TUJ|yI_szOHJ$^ST)A?Zmc2fW@@_>s}HNlxZi@^3cHlL8esKdSJMw$|COPBR^xmP>2DQkY!s@edZ_NI^ye<>ugMtXg!+3;Xk02%->r;KCHizTwKs2^m9KRE|LK2KdH#=nwsRu?<4SpC^siHdj~uDm3jT6M^Tq}B?*mRg^`E{-rs%hW&VK_G{S^i'

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
