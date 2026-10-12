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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_004.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_004.stl', 'source_sha256': 'e5c19ed39a93dff6fd34e9807af7acee61bcc5ecea6f6f1c35c776cf6497e745', 'input_faces': 861, 'input_vertices': 514, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25595059990882874, -0.37427300214767456, 0.024251848459243774], [0.10400077700614929, -0.00879824161529541, 0.3203565180301666]]}
GEOMETRY_BASE85 = 'c$}r22XswY9PUqu-ib2m9Yl1AF4`e_^yn>D7X%@C#EBk6^cLlcE`$&zLEH#IkZ93oTwQcV4aUp<f1elg)_ZHc^`2RKeZTwJ*=L`<|GVCpj_w)l9W?y;Q+u<i)`5M_nx;}t%|V+mc&xA2z`^6Hjv6!BPRlF4`twVdweQ-lV^2G6f;QD@(BN?c$2z&1oEi+N>r~m~G-UKx-?9Bid5#`CXt45I^dC8HaGF1ESpPAD(>|B4<x;b<sYZp$rfH`C$3NNAs$lW&f9Zs(i(~X|rPfTFFEvh6y=NEr$=>1Odxu_DzO82#_%FNe68+I8N%_`qsY&wr#b0|x-9oM?U+cC%Q9c)Yw?nkG*G1(UgCpR-a+Ca~XVb5WU$Y+k#HHdJ1J_G^OtH@58*zE}N&X8Rq&~*M(-$RwmM2nA-Q$wf$EY3yf25=2*PGc%ee}gg;Ln<QNXqLxSIW06TLZt;8TetYQoc4|6#Rz|4~jp1Bg%i)O?;!j%YOO$x69FP6>B2D;U~VSN+l`B;!qCx-y4zAp6!D1+$AO9_l=Y1T3_Fj{Q9O6@VmuFNd4b`kmu?R9pDF@l5#8~oFu<#NCrH2^r$^jPSJowslUso3zEN)o#fYFK9+K{Pq)R_Mm?5xwtiiO_E~rm{xExaUvq}$QjRs{7|LlGEbnD_Mx&lzk0O7oaCxpVM8BqdbKr9L+RbfJ&;6w?NI9Q^P|lhMQXgaHKEzeuNyvY+mb|a_ElHkhsXGGxrN#%OKL73$-}uo1{{3mvZf4zE>TjK&dS1$1+6VpewTAe%xfjm=-frfbCE?qjhJRy{ysu_yEcMiv91~x=6?$0OEknS0X}6M*@QY@U@nSh?NIdIT*TB#DQR2|@F(cwR(<GGd;*9rwrb~V;b|mtT4M2RpN`Zg7H~glC)ZeTnp!}S!D5u}tD5bV(1yIjN|0amv>Z7!qW$he!FVo2@@b7uxxtYE2zRiQ+4_g>5<=-tW<(s@p!JpaVm^{CmtN7-5CB)Z!N6L7&95JMSHCtBrUpsA)`a7SO_Oa&94FBv*jNi`-@m^K!;TLg~a%`Jx;k^=4&x!x#xwNOT=nrW({b7puM!uu+UZ$cWF>g$_A%F1_F`|B{(hj!67vcNWll-<5%Mj0wXHZTRSBW3P>!Rd0c^^RjnJ2{8_D)0loZ2A1KD&lhwDfYxuN7E}{FO!_e%!(k56K<jw_Fn|YFF&S@4m5jBgS>343gj0BM1DY{zt^Gu^a7X`FvJB+ck`nzmHxnzUj});v2R*((jt%Nh#kbyI*|m+(?NZt>Z|{w=I_-f4f;nrN6d3!?@eB0QsksllU}(-$;8}|C|NiHHWl=Wl}FG$M`-0e)dh$U#5hoh^x@P@ONgFb~YE-g?`M_9lp0A^SsWu)x0~QKKJS!mvY`7l=@h16o=oiJ?5n>7xCP6cJLiXpOE@I?}_?XPdOw0`PLZMt|d^u{~__UI{hTxEKf2^IhLS<$e++l#<itw1BokZh26;SS4!gFG<rCm+hZsE?Gc-#K1+|vbItY}#W!CrDE(_|kb-`9*dV_3+}djxk7ndQHxtiYIZ*mto76*|YjX03|2n_)qt5o!<9y)<4wZ3do}3Hy*)s(7X+2HmACp^KDaU+wAp9<7X$Sr2bIku9?cn!qBJ;56PDz>P&12o+ceL9s^&Q&}<F`n4_(|8XE<f==ed;*leV^}@_cDK<fpug>MbxwJv6E7MrO}AzIHxnek1xxI@8aucvZDOt8xo(^9tl#8?RpmY4M$0R%&En(f4KA|UdqW?L;Bs?IYr*fZ2JuVkR#eHt_I`kjrdwb0j&F*`(r=g_Zt4xDCu9L-f+op$$18T0e{SIZoM$S&D@9b%Z`zDwj?&d_^q}r9^-N2Dba&35~O_ZP~`77Sl-t*pe_3A`C62}ysEUn<@GdK-?a*>kpHq5*3*uDXt!$%k$+DF*7xqtsQ-^C$ZvO6<~P&ff~ddy1mrK*PTIkk`%&^+pN<sYGX8zC)aUQ|h(q5&$loDE+SxRJEb`y)i}Gj197XwCv5t@Giu@~cN`9@+M5(_K<N?1m))&poPx{gHq8<FrUorpWZ6W#1+1rY5{@M}aCF&~nQA=u~Jp;n8A^yuCf8i41+s?<M{sn)YlX`A;fM4s1%){1*DD;b-LwwWT7?iilL;6K?{eD{B>()0Z$K>vUeS*Uq@imX;7SZu*#W%aXME<08(#|&b322A0DahZdu*}bTp<&X$=B$^IzgxpdjK2u@e_D}0_$T`1&?!9EYd8GkUoa1!+X8<^2>fL(D1X;BjIY>L;_HL_Pa@vhUHIMCJdz}TT03ID^k%vER-ZvwFDiy(pP4Wh^(+{Hc`~#O-s|=pl+&xL)JJ=%p`5I<;NPqy@o5UafO+7b@$d)N#rpL!9`F0tQ26$Bun%;rk2rrd1peefSeL8z$9p~P4u3S(J+1j(>0isIZt$I6g-ZFB7BautY^}sM*VPa|yF1~%veiNUr2bLp_vVP7gO%~VT<<i$^4M2*Duevl8lpayB*gQNBJhtKLi_x9CgaN%m>1<t?Tz`i66O<I=4|5I>c5t_(&vQBd}SGw5&5GB%lu%Ql`P}ha{rrrHXRC+xHWEP!~VJbNAV3uKa|ra_Kb|9dQXvm$6EA%kpR5!#D~Z~y`0qFD5l|jVSfkyuXQ0u`~Ub_qXiqKeTMks+?14v`Yq0NL;Nfiv7X+HK{?ImVx1alhyIG&hjN@gUYGhrj*;<YdJqmj^Jy7JdX>AFuP#_n|NQf0e`>YMF8yn&7=q`X%Mgb+FN6H6mcwr!EA3+m3Pry-1fl$r>v68Bdl>tZ8Vlg}+mHEn{8Y5hzy2sEGNZhgVIPM1yw7CRXZLU!N4n1z^l#x&$lrex=97-0SRcLGh;L~%7xQRXE9pnWqXF6{Y8lRJ8Rui2wbg*X#7*j>r`ACn{&Yb-Yg%O->8FG6zU``rZ|?C-);-;>57xCCpQK$ZMIxl0+O5%O2gmo~o6nz;_P6#8Jo~$^-KivTV(RxE&wcwCzWFYmJFT(!wyF;>FN99Pdi}XR;&$O(@oi3?sMq+qSYNUwBmd~hX#eMRr5x*oMDb03<d*Zd)v*KWlNcqwHT;9r(-t3x^}YH8_~S3iKF-qkpu~^0H|8npfDUpFFh6dD@zuN=;$y%Wtg{Y{5V!tr$nP*+eBJ*B;&ZzT-Zy0&_9?l}VZ3*CLOnM-$@nt1SB{r*7C7L2ht9@&HS-wa-}xKjV-W5+j18S+Jn9kG;MX{X@#51I>uHe_Xvdyc@xE^-OMBX0hNA!a*XH>z55`O28u87OugN*p8e9VX-fWThMkRZxzhz23yl?0{lwUMio@=^U82ilUzNk<4Xz?x0zRUR1vyH<#aU>k;ZOt)Qm+Owfb63wm{FM4z+QF88Aj-KNE9IDN8FB9W(M5dQ^eZ@*tlo*Zs!$ew+*$PFVjcVTp(fOS(b3CNo~JJ5Tir9_x%Jme`8H2`%mb~HWga(<j+gr(J@03fU*ins_aRZp&-0z$=b-qOIZ>E@4u;{rW$FR(&9Aq}J%|3d9`*^fcZhGT)(7j$nVY!Z@S212hkeI+qEP|F=c<_~=X93~h`Tu$chLiIeoJk8Rq}gJJT2t}w?O`l)un&UnfBtm_R}Q3X<mTTUk|D$<HFpx7~Z$UA<Rn^N8r7(<wHFSeSmL$i+QGe9^_yB2>#o5SRZq~mwC!O+yU(z@fhPe_J;VT@qgn!U|aykbt&wVY^!HsAJxPM`H!B(JZpX;`!1t$J9#g2fk@1QzHe~f*0Cqz@Wf8>wLl*!-}G+?;v~yT<R8CT`o$Q&1pD^;^WZnnCgaF7u@c&0Z3oo9Z70N`Q)a~BO?T8Y$1Akk@)OusKWhX3#eBqnZai1p(irvmceC`nsh@^%;ZX?wY`-f~e%8y_hg5tj=LhqpQSx540y%MS*7`Bd72{C8{<#z8v4&H`*NrbyzIA&cJog_@l#}Zs?mLfRpJUuEBfjCh5^-DUGVULCe2GE4zDNATu0nf0+b+KO>UzZUy`R_*46=xCebQ6<*EoMw+DG#b7T+?UKlTYftKq#i=-9^`j6|Gtn}B_<LvEB)6zi;cX=kg%gX?oSZ|hldT|zkx(avF~#JBnc;=K~EFSS<j7vDC3^WVfnapD`jk$-PZwzCQKDbX4Ei+4slWZR1SsCTu*x0Gs)c{MQ*^R2aj_{J=Mta}6ZM2X+wp`6D|9h}iGBXUW<*h-EN-`enlJl7JDBynp5H%I<6(=iW!Du?=qI>OJ=4D+PlYK+sw53(<`o<AV{V&(m(;rm{EJ+vX#!I|5n-K>*t!*`6w{2KZZal3OZ&P%=PV|}UI3gyfS65nX-f_Cur<oRU*p8K$a)YEcurIcf=@`m5}mGrx9NPE;j=Wvv7kNu#z;_GPfJqn6%cD{mphRA)=4%V#SaDNw80MBhZNBUPU{a$?Av{1x@>sIt*hL<=GoBAQ%OkJg(+B+Zk)3(ANmI?j!$U}VHelX&;RxIwF5>vVV#y(5WpYMQ_(<~C_pULB-oo&}rv48XHf_tmj+=%CM!I%%d+rytb8te9_d04Mc@_uAYOL?xzWRHH_d0oywmZ&zEe=hxv@jLe@&P79UFQHqKFn<;tDZZ(H820H+6C>rht^;uHiuf*ZrJu4&Ioj$zC}(j^slQ%zJ<jRt-0<8-&e-=IyC895UieP--{xnJah{#o3;C<v5?{;k5B4+vlsYE$9J)$;TfqzHN3ZSjTuaOx<ZrSB`;=3|(O<(taPB(iiT#dN5^*)XD88R4R22Q2?=9x@C5N&9i=HXtOiOKq{&j2ve|sR#J&$i6l6uxl#y*ephQ7B2`n_=^?u)~GkU!I=Fv<TgMfSU<HQ7*~a;>HQrXPL8x8^8|dxbWUd!?MrPPh+hIuH5R^yU3<D$b2(yb-@^vA@-vb@45B<*~n*b_Vm<X?*{obv=r8*nH`v^rQQB@r}GAG5-av!+P3n819QlZo<Co(4^z?+`k&*zH)JP>;r4H-!Jul@j>n{EQ!sq|83O;^QvaxUcTQvtn)D+Pf0o1o8i90H%$7$Qr9N?M$Pq@+&`K}mq$JQE@D3EQciqZ)7j|Xr`K_h?fD$v6Wm7oTkY&+KGXxM;C^;<ZOkhl;xMk)Y{R`C>!S_$iuq($3*0wdoQ{1#RC8$`Bl@M>r)#fM(Z9(zaqoRJ1^4U;m9ailNZuv&O!5`qcCL!FkKVid7I|)RH<S}|9rxkWcg0A&eV-a8en2Y5Me^iLQhpX4esmYyPdYT0_AwXuCilqJ!^?1Qv#Hh&d9G6+zDLaGjrF|S7-?s-{&S~%?r<0TxFu1Dlb++nw`TUidnN3{edAzf@%8RuShxKK;ygICEXwillyPRP!u^tYWH#|l^<vQPuHR&Suuk2N`|Bf%5zp}%_DKBiIJ6yc>4teODSo#+_n;5%*Iv~^J>B}rylpyJ0r_Vf!#zO#;n*jCeYaIU`xM81aN=WWAB%Qge60xD)ri<6`E_Tje7~akbd>eYHgFF1;q?RH&tHOl!G~|w|M-OqVO;w5#ysG8bhE@ss4M#GIL>SOp!MS0&i;!yFa8AQ3rjn>m(e$L#ys}&DB5$EgZSFyces~$mn`#@7M2gb)lTLctM`j=X}2SBa-VMMunXt%$j&nEELUp4&r}HG)O)wgOXhDKa8Fke^R7NG8vDJB<={sw!E-KS-m_%R2fuTY^t<*TVVl&yc%s~c7*oSB|C9*F{8n~@`1+XAc;Bt<B(8MVa^h==MPxi_*Ddh3Tw5pkZ#Bfd^^-#D#NR(heDlc|d=IcLI#kBp_2>|3=Q&%jFK!ls_5DVq_}0rqF-|jAL;t>U7GEz=ndkTl5{JgSvf>-wxDVHF?U!{#E9|jWJ~t1?bC(3mI5PU4SuOcH<i`A#zgUR){bI$}mU_#)Wz3tnPs$nP4gXUT;$&MM%%3~Ttdh?;PGJ7=|FQ%9TX+@Tw>0{z(pSurWhO0`&((Xaka|rlihWwSA@KWoN<7*c9pgOtVVRU$b2IjXFJiIZ9+Vw^&RN(;C)Sj>GESy0miFA`i}k2<Kb-H*T^C=k-WK;}&&x!J|M*t0eD0Ql{a~nPtoU|~#Mc)4%KWOeZH)RC3tuGl8`c){YU46oH^(kQyf(r;YcCV-A4cC^D4#E3zOuSqm-$ND-)n*Vd^ZowGeyhEx~WCghJUjIzVEm@3iWKzd!G0oN636)>huQpy(2v4BA$BVJ}IFv+UIPC+2Y^7gMH4kRP4L*9+@fSwhO>HuTbz2@tZH4AwPe~UeqXC0`(knGeG<eA?W}2>v8S~{$NP?<L$A2t*VLs+S68iefKr&>wC;NA^xRaljP@%Jdk-y_j5tJHOM$YKJRpwa`ehowu(Pzgs-&oGu(Gs^De}=-VruV@>OVqbMX4zICmebA-)#(65kJ2uZ{L;FldbAtFl4X7wh46GCylZg%RSHGBB@}8jd)zPVOi_pAX-oTH}XoNBw<UOZi0uWt?ewi?Ti4nkhA3c!}>bZ+gqRrtSN?r&3GDtB8|FQFvcVqh6xlx6hI1?CFg9_gFMQ#`p5x*q<b{$8(qeHALdNU>EE!igrUgoa!?|sr6M=eD4`J9r1Q-;RuXZXRK?1J~61zG33ARi~Eg%J=Y)(XZwieJ|XXAnsOceXlxxT`By%{cuA>%I1HUNQPio1tUK1GcVz#jeR7*B`2#EA`<4y4P#^0+Kc%+M!C1#fIH8>fjPqA&>dx;QrzEdNJGcahzFj2a#!_zRLHX>_T6|+_LF~`-d`17(y(PY>&vL|1*V|~%OJ!$?R?2~U{(2KIE_Qy0pK=K2iJ^Ww(ay$fwBJ3f!?|5B-a9>;BhSs#1m})n-_h^xIp@lA<9)Fo@WA(U+AF6(>Bk;B(eE>Mqdo5p6yLUQHsU!~9hBd8<3drb8s68xJH}Us`in)MdCIzHizy)Mpw_O5_@@5(asLqzBK>RVfyn=TGR^^yr=ooxE?p{re=ZUG^p77f&&0J@CfaW$*0(DMaXuQ@XN8o{{fRa_Q1+RcTcMSr!=f;s=RGIm)NqUuU%$Np`<dD$F`t(?1^-PD=ARW?aQ-d%Kz!p$g6yxY9T#97$uxGAjF({t&_2g2%6Kts4G|Y(3SoV4J1gs*wt1PvuQ_XN>_4|z&_46atd%$%y-@D=tU0F1`x-ub#MegG#P2V8)<fKSpAcVv`X}!7dw5_y9d<)}lUHHvX9A|6ziMX0dcOVy)|c3a==bW`;77efzf>!Lb)<ZA@h#_Z@1>nygK<&LU3~5Or6p2+@1keWp54Va+X~?RKPWTy|HXpDH(fwEdPp~{<C!w8mvUN;!@hW?5AJQE!Z(O!#P2m&SJuJziHEG>oBL0|yxsFN_WxT=8^w2w$GvXKX4w}RrtKCf-}3;z2cKrfIC6LczeZ>5Pu(xd{9t_-hWRhf5#Q6D%!z({8!5i^V?8NHuf7rIh*$CObG*Sk+~qHcAN`sK_D4}&QJ)YiK1bSbmU_<f!niA6S=KKjqLBDnop1R4s}K0zO55p%{7ap2p8A%E@wj@M_?DVE@Z8RuWt}qSWR`P`^$PB>^<AU!+)mXb-gVCzSa&Q*(r#M&W>~LA-o*D}N3gyaZQEdcT*B`IXmMx<t<?bd3p?WXiv|@({Ff^&?QJWyAM@Lj%d)@KGQ2=PO!dP)ZBZ@s@8dwM5An^h|16XRe)2={4X0@QUQ)_unXim^SDc@|-@$xqsg38Ja>IUY-y5{g$*qXbQ!Nl*L(DiI=jw-jVE8HV%@^C@9J($O=AW=j@b^E&zO-^I&YLTn%lv8@^&S1y!dd#=2p)-fxAPX9KZ4KVyyn$X{@!$B557l;a790QP7_}*gnNC>c_+q2&k*sot)uaKDLWTo9_X<N@iliOo_o|D^OAdt_?GZ5^1YHRHVg9C=`Hhw#kT>zzg<}eaZ+`O_&VR$*4TvcV!A87IfTE*m2^SQcSg2eIOh%Ai0`Fu9>G35ix>RG-q^2hn~e85n}Geu>lL`i>ZfBqIqW3oA-(M^jNiylsL%Rn@vT)Z;+}PA9+}6C#TlUPG5CFhC1nr~lMV4Lk1NXkyuLoG^rJC;wfLsW-l%7$MA`2dBND~8{n|gT+=6*5JU{xs-D})i=tXhvb8H5GUIvWQ+!wKqZ0ZI7Yj?z9jTqcd=HG+o?`kRMH6t}1`95^V{$fXQd@pvPI`ThTDZVYxEd6Dj-$CBrcoHhU;Sz}7d)zZY`q4TdN_^A(JMvtM_iWU&`xo&o-UIPoAxF^u-M_*AV-xmo(YdgHxc(E*ZJr13<>V&qU~SV7@lxx7%(v$Dfw(6;x?(@Z?<0J#6}$}nShfhpU+HADLnSljx6*%#Z|i~YD~zV&ac@)53;DC1!@84j4ejDE7WwPO;QP?BU1JeXvyp$JJMN+PjmN!TCad_?xTpA@J+%t%&u3gk{_K^pPgt`M<1XN?_?E84@q3p+^$|bsT;%;M@wsr%w&KTrjJv~l??x8Xr$ji$SBo;TU(<QdU>flp`=u?9#5aOcq~C2(-|_RNFXEfdA4hy{Ya{Pve7%DCuk&hrkG8!A&MD6;9G0Ksy_u~(=5xcVlK57a$A}a6yqJIb_YmLM^Dp*qLDvwUo`c}uPLlP=(l;N*SDy*++fTuL?Kj-RXssWJZ>wJj^YfU&*cTnEB=s^M*Re0^^$_j6b({F6g-6i-+nZn<ZP|<U%Ks|nf%uLR=SHFL^j&dZRPhD;`(;Hn$3eK?_-Mub$=#;no2^yxTs_K)c=i-O?fimuDsM2xb+-ZVcckE4wxy)_da@VB*=PQqKs}q3qj#Kx=g-X|^)b(0i~Gro%iw1TMg23a6W=($5q|5lSntMHINiA8fBv<@PfKcryXDhro|dv{4%(3Zzx`7OWy)(&|M&mY!K>!~)jxHpTifOT_n$h{Ppd;+)tpR<+fr+j+mc&QtCL%hn^7x~n~@t)E0P<L8&I9d4alz4Kgq7-dQ=m+9=Q&+EV&N3CX-?pCdK8L6c?u!A{Qq+P;-)%W+yw4^H6h;^N{mX^OEzEi&9IFi;_!GE09Z(%QGpiL9IouL2gLZ$qmV^m=t%WHYax`51_Ut4<JvZwkJ;{8`Mr@gB(EZKn@^Jptd1TAP=Q>Bo8GIr}icfCy%F&B9AA}p-v;uA+Mn>Ca)oHr*0u{C-0~3CGRI&sZnGrIe~hLoIp;dUM44#?^FLG-zUGMJ|w>+f1o}ge;|KOOYf<Vs87g`$Tz50$x7qNH^_IG6em&-lM~6Ose8z$$tRc;ucs~~uP2YAjwUPZMjl5VMr}t{I)*%qypl=rHfk_=8##u0fP9g9i+X^p^cwjV`74v+@6_|;@8oyXljL{g$JB%5$K;#T-Q=6(Gt|}OGvp)GS>z++aOzlcIN3t&PqvVQsNKmy<f+uQ<f&vIY74Rtc?h)`c?j8)+KB8)?niAv?nmxJbtU&9o2m84X7V6v9r7S@4{A+v4{}SY3%Mn^X<BMbtx9zvS0y`A%aI+)#i+%}#mM=n4&;2~T+}?|T;$x;{N&u^!qlSV!sL?FQe>s&$tB5Um=rrxYmlAEO{fjYO~_rTt;k);UQCMnQah9Tk_S@<kO!0fsT0Zm<aJboypFty8bIDe-b|f9-b`LV9ZFt6_M;9b`;n(p$CIa%1F3V!f#kK+HRQGAt<>%0t>k^w{p5Y*XsVSQO+HIaAfF{)p(c~BkpHIMC;v@;PJKy!PEMtMAg7Wu+Ce{)RZ?tkm%e@|R!Om)9g^Z#{QF1bSL6rO8)T(-$PdU#)I_q<(`2P5$Vucw)b->;<mJ?HWTnH%N>`GXlaEoik&lt%s4?VUYeO89;(OFvWTjup_sDP4(idtLJLp%k((h!I6z8G7Bder1JM}SHCB;AK-6a1cr%=z3Q^<FzN62@{7pURn3*=a;g&a$cqy~{A$-Agi$-BrKs6ONk<VDmW<VEC}R8R6u@?>g1@?`QPY9I0>@)W9>JcYc1I*7c29763u4k6E{wj|FdkEAvwk0kfh($|unOo~0yQZK3-wK3U^T#Z_lT#a0s>PRk4E<i0tE<nyo%}35k&P>fk&P>ii%}vfi&PFXv&PFasElE~dhMb97gj$BI)R|m_T$xF67itr-(yrt#<k?g&@@(=dCdJE`6px_xC66Evqz)zzBzsf+$=>7{)OF+;<WTA+aws{Bx|tkC-a%bJ-a%eU^&>AO&!tW$&n3^J29oEImr&P|mykD7w~{xKcT)F}cakHh(c}p7aq3y}aq>Cp74kXqb?V>b>tq}CIoU>jO-&`gCTn(3wI*pyigQry$vMcmsCMLB<jiU5hX(zJYDZS8)-A<KACUhcKcyy-pOSAgDZa#{_$c)dS?O}J(qrVK<V(~zveJ9x+tjDjdt{|=$-mZ{r>wKmAJi}8A7u63O0%#{vT(i0%#??1mWS)juQtriHdd<En_q4IlYOK#MN99a6!xLgyTA46UG}-s3%|v{1;&Wd*xzC%mNBI?^0ydMe4M&VOOHv#5!4M@dJHSxNnNC+$GqZ=)R|iP7*V{0I$28}Q;O$NCu!+pQ1M*q6fJ$sDqc!mp{0*;#XG1WTKb%zIE*@9OP@m&hf+ss>2r?a8PuLy`W&U$o9dyZ&uNMWYUyjzuQ^b$nj@D{eW|_3zGQc*8(C>JvOBp7lj1+9rOAJg?WqOG_T&uItYoE`$r;ERHH()1NAa&ILUBfFHnP%!<X>x*;@GqwIFpvHGAX`BO&}|^lCP03Fe#3r?juK$H>9Qc)aBHD<mKc8R4e%a`5-lce2^SYJwsL+OIEs{taJ@IoV<`4L{>VHypTMCY9=dfLmolyz@)ey)s^f-b)mYFU762?NwLnPxI5KMHnSexnG}zv29ZaT7f{!b7mznn_mel04>Kt~M~x*by-Geu{+mhhJ?b^`J@O6e1@aB@F=`a~7<nC&;t=Wv@~^lFVNyJuNpW8$#Y64X|AqiMj5?pJbUAq>)sMQI>_=YAq<9nc09oll@+R^QCdDhM;bf%?$t%fom=uqpjvy=TKpsOLz@)f0lj5dKik+$T$j;<H?b2iMPbS5MnG~C-E@TtAI#nlEC%2|{C$}aKp^hdGA<w2RAkQXSs2j-^ay0cYIhveAJx5mhH#v#?fJyOV>OJyf@-6BO@-6aN>M`<J@=oeH@=o#uCdIzg5VF$gWM6V;YF~0^a&0EX&8S1kzhb%>lj7#oVdUoIPIl?>-HF<d+=<+f+MBGjDOssAS!sE4Lvk4=#l@-4WTk(Si<9$H3zIWZ^HB?v^O66cn#g~UD^RPGE0CK|Ta%lR`%{OI`;!Bxv&jMEEmRA63;8%TntYsmoti{e`ha|${DMjGYwBb2Yw}a-E%H<H73x{?74lx{PV!#zH0lKMG;&)e#qFrRWTl<S?a0-rwaL}UMVJ(qqBbL!BG;leC)Xm^rFJ4KZAh+5u1qaMu1qdQElw^*&P&Zt{uNt!nH2w<wx4;SK|fKI|B0U!XJy`e<gDa^)IZ1t$z`b($YsfmsZGd@$$hB($$iK(r~%{|<n7cg<n82B)Z^q+<h#`CWTh|2Db#n=7vy*3&(zoC&*V4Mr{p)}+te%M+vG^<UUDRPCUqKlCfS49mh3^U!lbwowH;Y$HF70#A!-qFA#w&)XAPQ-pNo){mLg{(J5Xzp9mtN<x@4u5$&Tcb)MDh4<eb#JWTh(pa`Lm{k6L<+exyDlD}6)$Nd87u_5Mb6AgiP}H$6wPBkPo#nv<+lm8*DOT3VWx_An_v#H9EHlj8Mh$)Jv<E+vm852Vf`ccV_G&Lhv`^CmMX-pZu-d|H~DmX@TY!BijeU~&s4#a)>cd!{9CY9N#1DO4Y_56hjxq<A%x;t1+oas+u-T6&w79;T)HOo~raFOpA_L#eySq2#I5x#X$jUev+lUgQSU7UTxxa!iVAQoE9Ck{dB8cBguhf3=r8lj5FCiia~P_NNAt{mILi6mO$WAx~kOZevn>lu7XsY6STRIgz@Hyo>Fa$fWoQ^&$BQ`5)?A@;~Gs)bHdUWOblc`pqu=fUWooy-(yX<d@Xv<d@`2)bnJed&rl_H>ronH_3OXC&)HxJoN-Qo*YJ9PYxpo+og|H#k11V+O#yD8cYsmp7BhI2Qew`LLE!)LUyALB>x)cZcK{nq@{|~R@83fR^(CC$>dSw71XWd737oD^W>A{N7U!!N92#xPvno}f2rTd|B~(4=ikY8jEVR3-jbExC%-5E#iTffdYT+VUPTQhuOg45P9={cx2N_Zw<p)2HXzp^m!Os-mmn8lQe2c;lU$Tsn%an5np~Ahaeb;gS!qvleR4}C#XYFQ$vwzkOo}H_{mGNai>S-Ui^!Xq6z`^PBP%^h-c62UQk+aZLQW=MrY4e=J|SNwKcoIben$R4{XzafPNk}OB$b~P|D>vU<R_Ejuhf_1ujE&0siV7H28WFQr~eIf`X4n`wg3E2q5s#P{O_++{{EA%)5`jvzhK$XJ(JumW=Q)_eL0y)-EwOG1FwHQ{Q'

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
