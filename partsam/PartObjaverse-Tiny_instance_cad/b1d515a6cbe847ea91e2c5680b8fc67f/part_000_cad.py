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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_000.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_000.stl', 'source_sha256': '713d4cad79e90db873da9b3a2de83bca4abd998fd1acaba7d8f9a0cb7d9af503', 'input_faces': 564, 'input_vertices': 299, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.5794811248779297, -1.0832293033599854, -4.803489685058594], [4.143940448760986, 7.097517967224121, 1.6305946111679077]]}
GEOMETRY_BASE85 = 'c$}qM2XGZfklhbR2qa`O2n70wBr-ObY*>Pb28*0w2_hK_8En7-SZuPuCg<=?jwXXmTtr3)kxaDVBXZ6;=yqPeJ$+x@RbAbws;hh6&h+$j_w??}FGV#<n=ZR1e+9I6V{;xJ6RK&7g0$?~!07(p^zIftpma>^cP=e6aP{Z#DNR~7j%w@D25LVP?H)a#TmPa}+(oPPs8qD1yJ(Mo{lDqoC8l$~{@tS$Ubjo%0ns)-pjVgJXuBQpN#)8V-Q|jvbPsX=AOA8c8xAf^XW7hZI{sM=)eb0jZnw?!12cdd&9<i16`o<r6NS55{*qSV`p8C^6|SGV`4atIY0@ZMOD=g6?RuHgtF~Exu7>`>ce1Je-X2L;)pKpl#T4-5G@8P#6-VEzwzYVg;L|T;QMeh918wuv(GTFCo_?t8)YqiI9y7~(j5BAr@<2~=2<CSm?DS4?Z{<UGV9%@UAHj}c&E7))$&f8dkNdYQSf`%0@f+aR%$!P(J5MF(H;%1)4gK3T?ty(-2W5i4;&#76|1>x50>6>@2Id?29sFUeSouilH$zSYs{WpejRh~eF_+Ts8NcN*p1(T%0{9;n->bH#%u4vtlhg;exp|lP?T4vYzvo;7!AniRdcBWc!A>nt4dB+C2e}n)tk3ua`fmL79C*Waz^#=BfqPGO6ns#j5a4-QK1KW^lb=D~!fyM~zWE$>n+-1mx9S$UrEqIN2l&g=c;Zv6dvZV6<N2o%^c&Ul0XIIMfO*~3!;xR^LZQ<C!q*b79m_DU5fp`WSXxK)H=lL~u7?y6+#3fwz5e~4!*2zjKZgEg`QT6Yp%RFPHL~*~*c($m0D0SWrXTWhPPvD$_gPS0%v<fC=r26=0q_rzz|DR6#SdSO2Cm;~fqATlxn%v_TLAZteRCUrI#3}S^bh=S5A!Y_a0t)8^+>#iSip^OEhH|@BjE?Vd|BY`h(+*&`^h!LL$6j3`KnE5j(pQEWzC9wShHE?dpuX-_<A+`p!ezyTu)kt{b<Fv*Z}{GXad}u5GwP2a}x7<j+X&$1Z;*s&0IHLp#RLdw_xwfqS$xdgm=Hg551y+n}LgEzt4Pi7V&zLjD6-gS_8P|icEliCJqH|jB!Jc(IyK0y?=fM+}d*zxSl>{DeP$<3S8^IP3+G;J`w$D?3Vp>ex&Froe2G&B{KxyYGy_M#DUPGr*8vX%k7W-Vs_oQ3iHk`2i)B?18`4xdDJ6!mvG=#$DhRiZ*#(*Rzh~^zk9U!Ez>Lb&1jNd^shK7_UGMu2KFaTzK-?Q94>m+J(2j9>I>ZaYdhF!+&=^Ry?zaWd*%ng9=%)aDa_lwHgNZrLDIi=@M-8N^W8Ps7q?`+k&%Zne)ZO5;GHAkH#2SU74%R0`U>Xh_a|_7r-feNZGH#tIkgXQ*Yb>ciFHjF3*6l%i{SNsK|XlC{usFVMEt40OS%X>v84n*6D4+jTm2v8&xbJJdYudKn|EwI_|upaBK@bvh~H*5f<4~W@4fKnFA11ekF53@en{E}+<WGP=$X42c6vki0Jqi;f}gb#p|I0R{}pg|$ynfe#rBxjGvMH5tas5`iA(YZ^!F|p4cr*@gVfKTs!KiDf8rAGdA%^Nc6O`Sf9VKtYigL(?QLyP_ss4CfooOveT2Bg4LgN)WDIckmA@sQ$22?-J0g4k4gI<E!f$4C<0AaEYdE;KMt#&D_b<uFA8SKH;O<Y8B<|U^;Js|M`}@4uxlHQqo!{jB(V)~>%-{Gm`nzjIZH1mU3(r8$p%1`4brSwU9G4IL3;GTUZq>PmxELkRo`$_i=f%#Af9^;7tE0fRz~X{m+J<~{|G5?GHcsb4e657h$?*S>=#v<iyYMUYt34~gQtK?%<OKT1m5_Rpw>IXro_=*4eqFOt;_@UP;%*hF3EVShI{F*mzrKL=RD72Ndv?8*?}Q4k{=xXH;lTC%e~6u>y1<W`@#!((J7W+pBQE}m)UiLYFSQf#l0SWQ<cVHx@Dao%#fARb<{3v}cm3)+V9zI&fSVyh5~0Ujx&`>2Q^;o{_^RY{Oj_V(!5#9xo0VVIb@}in^v}Le=Dpt#^BPxAY{Wbr{*e09z7hPVmD;)<>kj`6xPCmF<nv0umB7DzBkS$D7yj3ams|!ti8&-LO_Hty*RCwZdT-{JJgHIr8uEX4k44Zk`Kjo+FdubWA2Dez`g_79pNm|(3j2?rm<ju{tPh4gEyf?j_;HtKV7=FWl=ybOBKi9E?R4;=cO>6Dc8OQ*QPE!m?|lZi9(xJ-rk}bt6nPZ<1p3YN`%l2mn7!jME^)8)zpxi^*Q-SS0(@rxaBcepsSA0kt;D#hOW<c?<~ZyZtzJ#wo;z2>|3)wI|Dwm6fcH8p@w(d-@zTQU{sDiS_$mYR9~&UwrT21dgFiyU<vV0wGx;vsG<_%V2Kgm_&c~gE9k(*<0e-hO?DVc1i|<#hO_6<w=hPFj-YOm8PyN}v!?It$l=tl29@yueM%j^f?&(#<&ui)-E@td-;F^C)@sCjhxb}UqV|d;wLiUTb8gcj5Z4KPJ>Y3E@wsny|#>P!au=Bt+$%j52WFJikJP!ZlN|Aa#zopc>rGAKymUX0jU+w%<-ly|^2X4%{FLAkZ?HueL(GLFbwA~<f7MUX7*FP7>drxb9S>}DeHy-`c=)kR=F6j5Psww+uL$cr>AC-80cU<cKt026ewQlk~>0Kc2HDiuj@ZGDW|Js7G-<z+H_xZy~f=54-_sh(!(!b^r+1Gb+z5%Z9l<%M&N9238>{RSiv*$^yPoH&2-lt7sfm>T%12@}FlsY^&BkHoTX3}}g8<QaWeL!{0>%O`SxZ$4>dfb6SuwFB4mEhgZN*upGCw1RHQr^$+=F2{v;X%E&M)v`3%<d?87&{7eOdB)!Z}k77f$Ya`vdQ<un}xuQ7E%X1g(^#Z-Z>xdd86nEnK#LhI`GUN&$V$E<U6FmbmWzuF)wg;yXWwyx&8p+;+>pN^fgVAI{)w?zI)y8)=U58M`S<7MaXx^A+OZwg)#7tr%z3ZSI!a0Q|(ko$*ZP4E&!i$TksNh#r})c#lMODV6S`EI@x#Q`tQa5@^i^PXcjMiK3@UxGJ^60_xyE6zK6>U!us`TRb_oQ!bH#0L;K+87gt43nRAl2pJm;Pb=J8j{YSPGKacMNT#txEJvMW?B!4>B!Me14t%19TP89rDZmB;7Is-TE)Q3IV?zHiU<KtPtt)5Y+KU&#lIIp@Jt&@5`xT3`C!L7^C8~Mo%tZPBMycbFp$2rf;Fc`QuXq42MD<}Ve{)!uJV%{bEp8x!n)FW?BoCD1XRpdO9Ctl)vI8n}rh4<u@xb&BE$2S9S1AjkUzH`nOM}Mu@F5udT^il_s=i_{CwOM-?`u88fIZnT^9Jsl2%6;gWQBmey{aWhUo8KN_eTARM_uhnNIInpZECcSDBKy%>x-k6dnYI_WdB3i_Pp{ULy0PrA;AOAB#d>}pi2AJeT#0)J@6Z+EXCv-U%=c3m&iO|CG|_WAt-P1lH3V)Qj*`4;z5(^Z%-0RLcIk?IXU0{>`#}3;5O8n6arwUe^jq;y-sz%edVBe9-n9Vl9Z#_%f?rONbv?|DbA*1(5BCb5?X5(A-NvKQ?{tvdH^iNi@5asr5f|^$?7;PNy|FIu#GkM)+^u#2clWv_`*GP_<gIteHQ-kF#ZnI|oJaufdH~#eDM<2m*kruNjU_JJ2UwdoiQlTPlJDK?MSz<fqA{PgswVC|ysIMQ{va%e%sad55$OH9quggiju3xt)aCv1U5w}-x>o9K*1mGzQ+~AQpLkH-`@=Wkp2o;C3%L8~Y01NhU&^^Rdam4yJo1-1TycV&ug5MD{TI81!k%|>uFx}|0<IU!BYvK|<0tf6aYp)=C?NScq&U7;tp;y_Yd^~S%e;9L-#^yI_tJm%aXF9gnuYVZb@7AXi$BQy$;l(T(ax*ke!_EinE3g28ac;~$Rc>k7V%rxp74Wpt^siOhz_DZ#b56EZZ-#Qee{o<YwE5+yu9}Z2|i>U?9@}T%elRsNA5+=UX*?P!^-9GXPVuD@7X4PIPwq9t9pdsR`4k3H!>E)J(70t0&w$oS@_dj6fEbu#*gGare+o3?%1XH?$`UJ$o)`-x6osas1JYYMT^TiqNVP6j%}4X)4ZYFGmY#i@115<QLl_ay(HgDOqcz2xg7jsl#qK*bCT>MbHHuno3V4Joa5`{k^8ZxpTN(?=>$2SwJt3CXx&!1Pk9+B`8f7@c7=PbVmNOY8`H>pEVQ0{x14DYf10ikxp!I0_v56S_`b9PD#`opOn~f{8!PZ#>zOr7`X|c$m0^y<y_6?*iu9j&0r!@AuerE?a&K%db#A*K^ys&P@g43yFSs|;4xH<?bT?+BU(fl#-Bmu9{CSgn5c54+CjF;N9QAYkQ3tf7qoP0JTgiur{m2Ka)C;*+D0^7)Ja87`Yi7)X_o|*)JqP-Kb^-SSR!}YZZffZ#_W<J}@!jm5(j2(=-Uj(jh<E`1o0FnN&&j&z?>V>#_a<hi9)g!&0R8&bqIfUswMPiPWFFolR_qJ8hczYw_k{0-o!-Xva4yxqIxpwd1*f6M%(VJ9tmk?foagjkzZX9gttR&xl|Ftg^?Q!oJ1v=q`zue2S<*kzANgP`^~!f`Z40>D&w_rV`E{Jby#a&pUFpqNA91uwUX}Oqp`E~u&o%k}i8;PU;*}fkCv#*z%xk=>jrYFs^KRgt5wB%G#%7RnQNmH+?yPUb{xOf_p5-sUcfdEuIaE7-_Iuzj{ef%#!IEz+zeRt~rZDNhJVNrVQCHk+cpujSZVq@Y_eE<rqQ5b^4{&eOva-Lr-@^VixA&F)i|2t`RifpdIbo9YAD9CFxEowY-1Q=xrGMh@QcvP~;vU(Yb_Td{B)!!C{L>Ghf7x`nPd8p4hn?QVFOknytNen;rO0|iHpxB0+aAERujP9{8+CmS;ur7%xOK3h;GQViN39xsK>xtDf``XT{j9eDxTo5BnRjvw-gjoLGr)~D9^`{w>-;6O+iNNCXWK5aFBT=>zCh2NAGkSTkL<^g?ee?H$zIaGP!;&Wyz$RQ%=dmUa4qf&eCO&z-@KH%S{lEv80U&e+&iz6d#cv$foluei=K+XyAZF7hTzAyi=DS`OFh3j0=S;{q2y=7!g603K3DL!rEz}K#`MGa*U;mEyY(${E}k_I=RITeI~V%5+AQ|$2}S-`HG<Q?&i<Wb-~C!n&Pz+efP42!{%c1A)<FNf@xZls+3((`O>rNpotXsOEY}8kXeCya--$kcCwkuWll*x+QSSAQ9LMilM$HhcOFQja1AitZ12@Yw1#V6(jD4yneUT3Bed)12&yvIPJ4eAsewc4uqfFp==RcM@+|wWZmcGac{qMh&`>(1~fO}6hm;G}81LC3whNj2(!sb21aZyR=w>mA9@8FfCQGbmxckz9zk2??udwP8fd-b!+@IB-H?mg}iEYA=*$L=YMIJ%>!$bCVsD4a{IVI8mSj{4WHnDJGT!ye_)G({P->{^d5K0je9Q2jalzyArdclrO-Pne%pDF6Tc2{Wxr(;nJ(_}g5`is!T`pG~=J%0pT40ybs#d7f;Kdu-Dcn@*{ex9KqXAs_i1+b79YTeHUp*p!i6wLjQwANw66on(L2FP%*;a%Y^H{|RkS>v&^R8kdki*OpBCF4LY<#E#f>L8UyoY9F;Jg*w$dDda&m-LvJlHf5l!_&bihXww6dlAo*GRB^WHF1c!-AXnHWl9I3U***4E{2k@z^jAjuNwx25;)@4-{+vEi*ezSWO<&w1f67=T(+`TS5ev1)WVI>8C2|h7<7w*wl9%=#r@zlpPG(!#zssgX%G=mhw3m1y<-f>}QU06UiTgQXe^YjH?3$15rx-gYe%DABeBy9lOZAs(pQU`3K36=6vYYv>^8B?X@<%>-pO3kpnS13G``po_otfAj;;$LE`;75j&aLM9i2d`Dl&t1|sY&iS@w?5o%ERn74|WMx?I7*}wQm9`E1t<Ed86{@19>3(DgWPKe%)i766yOJKF|MR?xdr>Ao6rR`|cY3{FvOueW%tCOrAnn?Zc~F(;LbvCv(xKPTk2xKL;`oGm!@}C)HXq_{drLOxgTGll}RYYrDZUywFmg-{QPM)SI2$S)a<Ym(07{<S(_<y7QRpRkErP@mlJhKEbw=_Zw{5O1{enx0w4D+p5n2=HVXFPGV=6=Z7gPeuU3<az4fXq<o!vE|DLgJj|w<HqD?sgzb4YO|$7Y@)?vT+qBH4DdeiX&?eKSUN#LS??d?~n|`!u07=O)HhpE&cQ$=ZuG&9vOdr~!cyG#Tu9Y^ermXlXn|`%v0c}`FdmL<$O^Ycn=JWZKooDm8)?aDsaPnWNYdG!hPwqTd>z~T?{7Cr+`f4csHI%k1xi8l_guE};K8$M|Lf)71Jg#>!`8@jnN6r&N`hmWi&OXk1ru)QiwU6&qdj(^>g0{_|{2SLXg}!xSyo&lv>NL5wY4pWp_I3R7BYo}IzK~q$>Sxmkn?{kV_LnxrQXWa_$37#;7m!9VcB8n~MdXgY`Q+2dP0C+Vb}-fM#dxYYekG0MJPPkmyJCqetes7t+0>bGb+(n<hHb^`P_AlIMVo37tHt&gHZ`&7W6FwGwyBg&Wo>Fqy-G((^3s&Ma=y-7Lra@lQ&wE<n~s{~YX|Ze%4)32m#@iHy9>v(rtN*md()N@w66@gYFD$VDQ#}bHB=`4iB09ms}Zl_gH<7~%CQ|ez9ZY6NCSM<(TVZsK;JYW??C&Noe{Jxg6&d1es4{x!?me(_oW~Evi&umwd2}*`#i5oo6Arx!#H-JZ@Xxzbxp}Nxz4JTtNO&g4DGB)UYhZ(L%9y0mF61Da=lF`f6QmjT1%6c<Xmc=mZVx-cSnwQ@~$Iocj8)^>#NMR+JDV$YC&0XwP#wf?d;c9>{pH4w_T2MIr^eGc?(h%+S`J>CFf}2BP*`*x+!&cB5%q$`V))wd8XupHYM0}+NOWVReLkr38X)W#o6?WO>@XSl-2X4Hm#w&hW*zNU&6kV*!FPzB#vKe(=3vbf46Ba$1UZ&<2hzDWra<&X@X5-$tO~0PhvfY_h5UVO+VZ8E%i>~JaZ{eq;2ZiCel)_>1U2t^LMwY8`}dZk0*`x!6p!!z;+KlA7|4T^3hz&LC%vvc@x{pAG_(3-E437(L0IqB%he9_3^8Ry4I3!CvD<9+sSv6lzf_Yjp4fE7@KkAan!Gl?Ky19M*4`D;&~}69zyw3o7B0#9=U24x2Y)m6e5LioRW+2c@6f}ea0xcl1*XM6~?yPrV8w%#z)%Jfb%+YE3A=Cb#1Cmu2b&8b|cD)tDI_YlVMYoCOH(XNiHZFNKEIv6)0Dr&QRix?V(&}6m4ry>ZYaUS9{tSNx1>>NZQwpya%7v=lbfi-H`DK;e0t52i49)f90mXa<i>de+}x6^zpgl<1p$gP98>mc{oQX_2nR@<ZNs=;F=rK)=Jb{$;WnsK5+bNaQ%TcWw9wAxoZ2{RNkgRHhoX7+WBotW0N2I__6I`J2Q1;_Ia+x1XIT#%57~*$3D({>3nqOqK;f_r{}mJj%`c12<J}k(@(WE${DF6BilJSE}Ub-+0MXcY1ua|+XZb3pp99{188d|K6m=5b^)7is<~_<vXGP<<`TUbeCBiJaqJ5wWn`bsY&-sQ{E>y26A#DVs{J|R=)|%-<G0+V!Q`sF&ZhG=y{D~;l$_rsF<R%-Pqo+cSwWi$lNX}=jL)3$s$GzJws7ng>S@dQ^3x~zsYA(r)a#5_?QoZj*+CsUsG|t`gwqbiBPeHM+ZnIgMO-pg#d|;b4(iFx=T1M>E=np!tQgzHT{1o!^<`sQjrp8D8%+K={jd6L@mWJQ+NR`Z^v^RsQ}}wuWgWTm+=<z8a_4z7&iM^_GtQlrc~F?#$=||!?(}n>tFg1GXSPqiY~*}5N#_|u^`~;**;nc>6URE^Hu~6GgfVhr<@nXN?kMim1mC)&xRdj~bw_a*W#77!Sxc=^`L)!#<K$ql_V2pmPaR5jYL25LmzG+8oVw%WV379jx|5!MP_k2VobegyC#U8(<5gSL1E=OV{ZzZ4_V2nANE-vR)S8o1ORYr(7#kHQr~ZU-e>*iNNK36nX|>e4>eL{oW;!(|zm{5ya%umrJI*tw)~HxIHK;ssXHP6AIkn}zmYPdWO>pww_r0UqY7aPd$F~j@V!d!`kMr!AmRh%*+OvgmbLx(79ddO0aja8|ociNidz`xA)E(bC<m9)r$DLZ_TYsGQj%usg;nbXLuGCuO)SjaMrCr>WT63K7&N$z?^Sze(K5*)fQ*)f!<<uO<N6xy}YpJ#6y_Q;|)@iAG*?D&;%(w0g)>3PWZ{5kKrM^Rb>yDEvg|*ZgHd{-rA%i)Wsv}PQQE^k4Q*)d>=j?;!9PiX0r)D}e$B9P-eHzusl_q=I|LI@;QvXcUJl}r+{I4Vb{WF{I$OE>n|NPM{s*#_nH+I2EgM<HLb>i0k1FAr!Y5'

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
