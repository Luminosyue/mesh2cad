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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_010.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_010.stl', 'source_sha256': '2d7cea92a31fdb6539115458c12cd8a4b5e289fe8c6b4976ca7eea1f76d72d33', 'input_faces': 576, 'input_vertices': 347, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.026728246361017227, 0.10096809267997742, 0.15863004326820374], [0.07434915751218796, 0.20375633239746094, 0.2322581261396408]]}
GEOMETRY_BASE85 = 'c$}r130Tc(-2Q*4ge-0L<&=<pjkIuNmq?=Q2i1(7YAjKXeakW$48qBpWsrT%u|%damdGx$hOvw#BfP%Pef$4;ulK#K_j=#vy081w-P8B?Y`^Ds&dK=u7P4^A@a3fCN7*`BJ87E8Msv`{hK5HD85|l>Z{+9+1+-Esm#=Rg*QJM_f3E`CSZ!jBkkE+1;Wa#THN3*yYt+%z2pbh189s32fKlNgp^~>7I6NZsYaa3Qz|o;!zjtliq*)zZ<C=AJ(YpWTSJAIs&~NO&vZeH8&!Q9JhP8(>#Em{V$S<}!DQ>#87rA+6yvp6)s$BnkoyxPDw^*fem&8*lUp8IkhNo%BeHW|xCa*ux-qT{Ws#myIin!S^SmnB1gH*1qZ=vd&y%Uk2zKZtMEl;cbW@XebZM#P0`<|=z##u|z&&@}XKiQ(%>q=fvS9KeuBlljV`kB39oNBM7xR_Kva)Iinanf(-XSt3l*Z%3G`f0rAi~dxPLVngwU03(l0<=G}19d9DQSA*!?2+%zLjEONwa+dajXIYqBw+rRs(zYgoLBuc=eQ#ep0E087}Fo)Ej&c!#?Yy%pIWIg$m=ddey_n9<tfup=l)9M<=s_(Ofws+_U0;S$aAWpKbAw$pL1Vu-PqfzeRgoZs$<wwbggQ?#;odRcdn26uj(UzmZ9nx5`t76)9g@{Yd2%mxU|WKRC|5V#mMipPF3y3XQruq+Y;ob$Eop}Ke%Jwp6*1xd^pzSy^qTE56<Db-Ab$e=qyH~KTAHK{eGS5zpi5mv|q1Vr`j(oj(*;2j`|6;RIZ&rfc|WVRQ)led!c>cI#pjkxw5KnO6iR}C`HxREUv0NJ7OX7B6~2Oy6U)Y$t2VdtE%c7Kb}$bwc>}7+lHw5$)33k^($RPezVe9)xLo(+8_LY+}&5rgE_BA#t*r<ubMZVWnrvuaN+gp_w(MH)%SbOVg9F;L;m7}x~{%VSFCT5Mk?1@{igbv-EpM4t}$W&@`V=I|A9AEd*g?3$em`W`O#)-D%af`kNWvfRX=qhpV9v18nhoiMvY6~eaoNfx_@s*`};GFtLp}3pg$LrksnUPb*F8_{oC&(>U4Rd`e`U&kM#=9Li>S*(Er%&=>LvaXrH(k=gEb~sFPfFgL17s&WD;mq5qehRBjx6RLxs<_#E`7mj~KU8-sPM(iiJ8(+9b|4&yy>8uRQw2z8cwVqM}=vA#`5AisT6UDq&IhxW(EAfMVw&5!21PtA{h>}=G(xC{GXs$S*U_Y;r@rK|p!H`rjjE=N(P)6ck1cj5jr-#Cl*H*;{Fj9i8B>Mo#t;t8D3U-o0XS+|he`>S;^f5CZ@z0Yc+sx$8)>Mxmz`!~Q9dF?qk_f}y(O&&Fo53p7JH#sD${+oYojl4*VnrHoo=BRJcQRT)dQ5f&1o~pg^IrD9SYP`DX9=Pt29>|l1s`b?dnJ}NbqftN374!Vc74=I@NBfK0RUN(cTUFmQbS~PDeva|ZpMd^*#-jb<d#XR?X_v4*R@>12&139C>*MHW>9fdv%((6^IjWzg1L?@WIH>tI#l~QsS3E`ijoujVvk{n|xFVa>_y71|o)ed+!R?T@c2xb;1vkXF`qfmqb_~y1V;1IL|F9WyzhihVPYytPJ3aFFzf^rw+b-BY={~4Gey!?{A^#t&+s+{5FW+PTUt55E=pKeTM|`jk2U?=e$)U(ST3~$}+{HeO8izWW>v7)tom6#nkxS5iM3~w?`pAknH!?P${fvS*FMb`2`On*r_U*lKo*VtJUSSuI`|MNmqmQYIc?h|I{9!Q8pKfKbUhYj3l{@6(+`d*5*Y)kFa;?lY)qm6F%W2=|#t|0S55Kp;efqQ~@;*n9=g)(Gh(?`b{c%1RN^pM~kw069c~};WI;Z1MXQ!sFYxFRx>*}mGAiuj*t)q57AM^Pr19>@n%+J=B*pGR+sQ>p6?5o!YlxI7CLi=LZ4yxbxYKi$=T5vP=xgM{_LQZqPIc~;%8m;Ej6n6^eUQ`+61#IxTYtAe5XG&kxNh*f@^ZFU;cb<gyA*t$noqHAZt4TESORKO?s)wV_=Xlhabr|cCm4^B6y$*S!1e^oCYGNHr9zvZL3y!Hev1QQDV&~AlrK_6%>?zwYuA_e=*Uvem#uej__4@J!b#^+ax|(q!)@M!eEvkKoVK~oyS7BXxl|nvkH13l*0dPBe<fm?^dDeYQ!Fe-25P8uyc;40OkMTMVSGhK~ES`5kVHmGzG;+_YIG<m|VqEdlw|qa(`YzaShAmss{%EM0Pu+;ZY2W9@R%g(^VmnfCy-c)sU4e0q{1fZ-=^FCmu4+Eb?-Fq?r9D8My@7|-_b+?n`hjnd*P4O(e0L4cVPih>iF0v2j|#=OUN~-5-uac92g88Yn1_wd$QOK6^QJ{~MZX?5MxIv~=f!YK)IZk(dGauf>yL*xhfa=Gx%SRWt(Wnb8|s&zhrCR2bzSZCOYEPty{I#&AjWgu8TFFP$OG2lbyrs>th>iw$k#l_d0y!=_Dit~$Tu`n^KVFBiu$i^AP?`L=FQZc{k(P)`9HirmwVy<b<1J@J&vgBjqZp0#o`6>LKl-&?&^l;*E8mKR;u|oTnS74Ax|21RJGrej`el4*{0ky5B;zV!MLZ?SGlpOr>c`(^)_DrS_UA$8iaK`@gDmjIS~28!+0KTx`e!b2=cnmu`d@d#QT!Zqmb9`gZUjY4&%+*hdc%6t!5L0d0TK2{k$Kb=1o_8EbjZ<vuJ<O2JhouoW}ELT{_zDby4$XN_c|t1?M2|a1P_L{TKbQdx(6!hngR~sVC+k=Mm~VzQ8;>?n6KKJVE<hOT0b|bHcej?Je^CbFnU_WSny;R)45`=tw-5V|QTx{!|qCgjG0qCY(io46Z6Sx|#7l$bKQl)yE5Y_juKR^X&*cxA*&?&eKTT4}<eC-YYZF{>3cp^L_pCd>A+nx&0~Zr>+%L9rKgr$hU{9dDdSljyi`{B45w~`!m%F=h(V<<egpc{H;5kuYcB}KlV;){>{sxaLxptK^{|1&9kBEJ-m+Sb^&#oR#w+FxGu$hE0&4&5nFK|UADqLw|a~`x|^D3L;dzxFN@d6*Cea+%2a$a`n$${yUOpK$9OKZ!#egVjr{g?JYT{Cuy5bhMV=Xn^_vug`T5Bkc{xwK?_T7N@fP+)e$@%{7Hf<5Lyh_&@3#s0+N2-z8MW2?=x;foKXu2b{M+kW{kb{VcYj5qedk5k=S$0DKU80ce3+G*&+G=_7~hQzsMC8s?mG>ie;Ah}qP<lx?$gKzn4d*Q(7tMEjF<DTvp9i#{9>H*US8O5M^B+nzKfcFV}%P?-^W*we|(A0kxJNLy&UeKPL-*6zHg1ib!Xj2`;<v)y|ncDSjTC3$cN~$fAWuDKlnQDP<1jjm1kcWgmw9)3G#x8*iYrM@Ort7yUMjvA2H9visIb(?1S7JuY0mjKEnHN@BXOsK0}Q+yUPLOB@D=$^uc-ZXfoC@X)yAOMQ~rgI*R^xo`L#>3aa@r=k&)qX2v1EUkmG$P!8+tumg3Tbi}#5(;L^-??;|o8~5)7ypA)a9cG=^=+E};I5*;tqJ4Hll^dEp$LC}tj-maNHh7MQ@5ek9&p`WM?xKH-YhZo5Wg@@Z7x!I%yl>MQenNh4A)ZI)oH75oUr>K>vYH3I-y-b0(*<^_y!{odW10c$QpFDW(j2vK%^9z8-9=6+H+tb5)28G7tMR!r+S`4`eD$4#_v?q;(f-{kRbTrv4D(jn1NnvPcwMnvk9}RY1?t?gSMy+K&-W`e{g973f&Qf9Ic3<>4SC#qjI-Ys^gliT`Idii-%iQG>$Ms|xUSI?&oA@R)bDfcPC?vvOP(Q59e_ONJ=QCC13v%r3`O2!E#@Kg2tKE2J_>na9PW4TX4r?PB9OQ7Q@N>iF7Ee5bC7qQkJr8J>~P)>oQHhwgJfLi;<xi3{rA{~=g5uH*gua~BY)l$^I!23=6Tg#)VWp>&p}gV{Cws<wC}nduWy4-V4i9mL;Fe#RX?>G6)>*qr??+>tNxf84LS2eo@~N>+jaszzbui0eDY1aFRL~hKmYw4u6zA3&aVO9n4hIrkyq)BdEe3#{cm~~byDu4Kdyr@UblzHBPU>flB_X5SN=x6yP?XnW0KJRNr5DlH~EZxWwRCS=UJ-U=+}?0^A7NRtrhb4et3>7j>FGCl|)_z_k-3Fp9h;uRYkt~0M5_jZ}Ib<)o|Tw)6_g0W7}Ze0&5}f=#Be2-36ahdUzmzV8;8SYM39>sTRmb#ACbzuHbWD_m;S>7KQP6W#aP;Cq3E^=Xu&B51+F(>W6&tWITW0T|xVe%oCnqeKV?J{`-d_Pt>q)R)%1GV}C|&Xo@=ZCZPTKQRvU`C76c@oWuG@5oo_*6UOu24WBo+`33De*2nv%d5+kJ>C?DgeQ-XcrQ-K&XQF+l^SIBQZ{mGk@fFBp_F`XMT8n<BBp@%<1pVkf8u#y#MC6g-=%-5w{5)<KuG{Ja=Kt7lI5)BmqJ3UG&bwC?Q2)qTw9oH_{;a))_vHoBkz04g`@1{qFy8flp^hhBml|I`ME%(F$e%XGc(?hZKZh=%PHI7%4;7YU9?oZ>ebe5!?rjt1;ow!|7PU}6pcU@ljECHx{qXzg!Pq}%-y)y$4Cm1oJM8Bng?6dy4r+}0eeUA($dn=~H_pTRGF`wejLWGM@}0%e?|&EKJ_;>^{9H87+tESThgLe&A8;M(QS2Agk78c-D(1mKhyFgVhCI&_^}AHU{j#wxa)-xw4sv}B^BW@{x(4%K><_F<WOMXqeIoX&T{7~vp2$m`L_aST#m^tMMqcYUzK`3F*LVBdqJHNynBVBG_&jxYFSK{xfzM$sY(;;j_d)xqn=rp=Z}Gn2Y(KQu8S#3|=LP0t#Q@}8{qY>N>W%lW%R^A-#jnUGRzv@7h9Y-!#=4BDjD0m^81m{PQ1?kV);%s7^)I$Y|GOvPb4TkKv=5n$I%DxV$Iy8O@@}ngj+GgU@m89JIx}kG?~nJBQ7>vX+P`gs-#=Cd_sgPKv|lk8^OJiS{jr#j_8UFXzV#z~9<cCN<bywA-^|3mGB#X-{M8Zcvrm3#UvL@fe+=a3<WX3+vB<SZ2lRWKJN9jEJldyTK>sT(Li@)FXg_2u)_WkII|mYxmrTd}G|R<0&fbB%_hF3l{fZy+@|o!WJ5Tg~-!5GDH0DuTyB*`OJBaof=9KU28-os`eT%yIe51Y%`Z?kl+W(o4{d3Cq$DDs((|UKs`7r$?>TG?C&s{xQWB=Sai}o&fovbxjk9FCZhWy*#BgUOaZoG&(r6=IJTMnQ4A#ct5p-VTk@0N)=x$E#gZc-J@|C=o2_1dF<HQ%NDko(oZ_vNrZjWIV-|MMiw?+pAsE&Jqcw7=|z`E`AdpP$G<zC07JdvD=<)~-E5ZdC)Hi$0G-`^CA)GcV!q#ZMw|-NDb0^K*N%lOx8J#ry%s-+egN&G$9>Stsel_xFo_(Hov8b8$a!OG5odd8pHNBL4mrwj1@w{fqV|Dx<!B{*U>J)%cwGunoq2N!zWypMuZZ%`czfI%NwX|NH=-1N2Bky+c;WNA<$GeCmw)^Q@64f5!a$S~I1k{}2C)qOkRfdd3R!)>6}oXbxJ~!0-MEg@p3;&Hw9vLNTPt|LC7kxHW6~fBh#E?ghTSwEC)!^ycJ_<PMZ@D|$n+cujIEax+S}2E7Wo@K=@iDhGN6as~d}fnJ3y?nrhZ7o~(hY49Rs@qab2Nce9`_%{6sS^O&bHaUY5-cLVC7XO31pS+$Dj-`Z`QNpX}d&%NQ$l@Ex;`7O?$a5&+arB8~@nPg~<ew<vKzbjtcx!SXxg{lBhZ1f`3A@odlEu4_-N+u4a0_}jvUm@23$hO-+@2mx7Vk}NPwqqs`%%I{l<**WC|Nw5JcvA!5{{-D$>K}M(d2oQZ~{G%EPj}rK;A<Mr_%o-i{B-ul5bGL&*=Y<#S0VwKO=wCAYtnQ@Zx0ga%5|=EhSu$UX?6fmt2utof5812{)pIz3Fab@fKuna(ha+8@(;LEzg&3lyDD9IFR0f+=1syASLWa3G3<2$jx|;=qcg)l&}-M0=WXuBPUAOjuI|J|Du7#Uy?<_?<nC%^lY;DMe-x^HA*<05<X1{AEJcMQo`5i+2m|q?>Z%%O9|)EzmUacJbCoO<mdc(K3(#Bx&zsP=dW;4p1b*!@M}u=KK*a9_-*oi@&!ux7(Ih5zMp)IyqOaIoxYwd9!vh6JcAOBq=Y9?!qe%?$l|NW;&aI2<H*y=V<=$*{U@?`AlX3fN(ncow<L?#AvY(xQo<D|;mVY-Grb{M+>Pu^u0{#hqI;0VTaas!>r%pv={{uf_T<LoW|Xiuy%Sm7kL*ouLkauSgUI58$o}L3l<*MxNV0e|c?fwtB|Muxk1U=*o=sjs32&qCA&aMyw~@`1@MZc9viLLdW%5Hx_znFdSzONRH~e0>ASG-=w<X*1ytbi)%TmHRdUbMjp5r=7*p(7)LT^NF#B;m}CESt{?o4k_ZqIYPGbP-U67Eg!LGHnGyf-D>ixLi?`;q;4jt5Y}Z7AW!^!nubJjWYT!Y-6>8M+<Wj^}t8O4y1Ley_phd>0mfM1D_xObKVvuaU*m$ywwxl<-0NX|nhs@<H-eN;sYp-cAW0rJp5>Und_WpQD8D&~wS+dE{@;1K~`14*fY<JfAH7nk;^woI}1s37?{0Ad4R(pCTtw!Yk>U$>P70SCZ#a!cp`YWbsIH6nQu$+@BH-p@c`!Cy~Xclf}o7#SP>U<bITJ2YOescyn?GauZ6pD&3VVUV&VdT$U0pNeSCh!VdJxWN~M*1GzLMT#jCiEMALTj$DZncB0oMi#H}akzFX^+Vo~*ac^>MawAIElir3b?oak4x1)r6(g%>mhmd=c2UEhM=;O)av&o~#lPTdv^c7_BZRADd4V3Ucx|u9~nY@quCnbE7{*WyGhJ2I!loI|xm*>O>x(!(*Y)J{1qL(F?<@2BvC0w2ou10qyyYhKZjS{X$34767l3Vh5;6({{qJ+ECdy;$ddC;8_4yJ^I=)K6j_&f-rg#9Vu*7P>yHhdnmri2?%!p?LTvJ0OF&Xlk{C2T>rB3toUVZrZ(-%`R4=#R<bS>y-gOO)_&`WdqLLGp3(PD*$UeJfc!p1g(}M+r}(gcnl6tLfXx;z!A=$vY_F6ZCUr@jK*i&kx~U^b~p~Sv-d<euXT4ikw2;O$o21Cy~WhlGl<KP{J|vxn%JuatwJiB|MNmoGjj-Jdhkf3AdtzeJSDY^boT62(oxTvUmq_ce0)mu19Y|7OzUKN3KE%JJQRN#Y>VM$;ByQD@xd!5-v)&C5t<di;`_9;S%)HWbtz3668{pusyvJS=@<iPcB0Vm#4ds#cPwxlXaAEb$TPRxF@+fxjrTAMQ=wI?@9I|ccz5<(g%~pN0IxIf2M@T(kGL}7m>%3XHmk-=^M!6`^d}5TPWdV`k!R+o8)Bjc}n;m{V7@e1Nk2L6(#(cF3*+E^ipJza4|}_G`&2zJf9z>DdEbLa4mX0ay>pjYEi;XDPbRaCvqn~KYS=*UrM+uJ(wKK=SNpcxC<rRj_yzP=kuc-CG1HF*P%BcH{kQ54kcWP5-v%%C)@M+QIZnYDB%|xT%Ie!;t$9#$hRorH2Nj7_;GR?`2Z!niN2F8zJ|Psyp$52Nsl9oPb1GHPoRW{Qo_Gb!c*xB$>OWYQ^~(l!Y29-viJ$|x95%UZ}fHaU1aeTviNSY_*(Kh@?uJO3Vi`tJcc}l96<?((MOZT2a?0cy(r<f^Z>GWD{@<MQ%bldCES1#cBlK2#k-Tm^<?pSWOs56O1L7u3R&EdT#;-?2^XUmCyQH=i;*oT;cs8U-?qANLAo_ryePRKxez66Nw*=3mmph`3sb^HzRKUXKtYE>|K0xr{r|s=(y1T*hv@(On?L^9@B80u_qEpl`y-&gucaDu!LR?x8^;3j4oCYB$!GAl'

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
