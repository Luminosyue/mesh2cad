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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_001.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_001.stl', 'source_sha256': '88305caa28960686b5e39d33ef3d1ea5017482f4197e5033941b88395ce0eb16', 'input_faces': 1002, 'input_vertices': 637, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.35673943161964417, -0.4999999701976776, -0.48388952016830444], [0.04837048053741455, 0.415962278842926, 0.48388952016830444]]}
GEOMETRY_BASE85 = 'c$}rZ1(X!W|Ha!oxZ6S?*ennhcNPzgJHb6+@I@C{Y+<28AXp#-*DzQh5Hz?=Bf%Yl69x+sB)EjY>+kp8`7z<_|D1Q;Bj<bWr|(o(S65Y6S6BC*G^i6VeyD+eVMeN`sV_^HHw=m7MyN5MQ{U*W9Xj<Z)T{U45F@qv@-LuM>Nl;|pk;_Lz!(zVu~WYeeZ$MT!^?Lr9bUj4-Z`pobl-Np+D7&5*h&2A?Rxa<<oNv}+x70`Z0Ct6UaEk*c-{i;Soi<Oe@UGpcu$@=>l1yo`m(5hPp0L*Am0l3$4>uTQOZ2Ms`_Rk<C3VoIFY6g_-^{{)w?vkcT7IypS$c;QIC83&%PkvqHh!!py|zZS&@I|&_6UC%k!~s96F)tt*|S<t6%LQ%30;ycfL4$cW>W#&415f^}PunsqZZ~Zj&#__t1A2@3KkK+h-%yw~l<J=jHz+;TT^WzB|dIZ?!z>;oGG;p?)HtYyJV>qVMi?O7pieg(3Y{KcIf{wVB|H!*{o;`kj`)N~rpN`hMS3l%KwrzFDQW=5KCGh4Tt&t@Y-)Fk9>AW8a(T8?7I2P8Z5a-<@-$<{$7)`gWdnn!oXzp}vv({$APkpAL`l#o>FeB^o5^9{=Es=09k{J}qCZuwt67`)u`%cdzz{@5!5WSe$;m3qw?^4~JiP)^Esv*;rp3zHw*f7(GtoK{#%_e=q2HoctC2ioS=w`%=&4+V0_HkWcS6`?a0C@$|et_U)m*fvPtnkblYXdS2ErkCx|S-!rlS%5(SKY0W2UkJgWsAV%B$W8a&+o3^{%U<dqWQ?(w9{HQngl?Ceid(XJ2$1C`HbFlBFZx%nhS&!4otG=~*y86b`d6q9OzfAJsTFz-baopEm;=H=<Mmaz7-A%n(PS3DN_&<E9_2X|@N!#&b-`g>4sQzBR0gn5A9j=$UDR=mSe3QP>=&$XXew!Qlcz#9t@u$D>#o>E4ZX2QHuO6ztXI$AUnl3tIr!UBN)Az*uu|v}rdUi_leZCs~e{<A!Uy$#iZ||t9<uUR;R^R{ry<T@##AZz&@Gbgg`DvQoljn%~UQZ1@uH7iXL|+`fHT;3rr<HK4`bM?L6IyR4{#=0m@T>Y}s~PHBZ)+^k@>g7ld{|CznjYW!f_#g<^?8#~nqRR6@M}FduKN#J@S~nr8!zgC<@e?qr1^a8`<r+)AN%Eel=Dz~EstGr@IpOq<|!y=?<wlLN1Rxq>CS%#|MD>P{V{Ks>haHxM|m>%wLHebgY)%xo-R0Ut)a-@h+d}otneVc)$o|+AM@R8t&h8nkiI~A<o|g#y{_H+>Z6=HDr<VP(y}?a{Y75nvpF5=^XE}IK3FrtkiJ6r5iQS)l#5hXXM^80yZW9gQS()&rbIq_iX;7f&rf>Xh$Qg8$%gc?KhDzQFG&PHb2|0?U8{Sw-=&F<{Lg1q-+f{3B0ZlxAxM98xR&3#bZUj_xR)n2{peIUZr<gyHT~!J)wi~r$UkEn+-Gm!gTJMq`gYozKk5E&PQ$-54E2*b|1X-)?E~-=*3tB4y3%@F^UZD?cTNT5Kk2aE-`#WPBmL>^I<ESkv|JJFdjkI3bSQuRxyWaAE#yCbx~BJ6osE1dwo%`^GxirfKWiM)FRpY*x7WvLeY)oig8yl8_5FFPYCX8?cK=U4o|JoWUVCe*?~ZJZaW9c?OR(?n0^gl{?iQ`5`Nfg{FJG$f>05T7FAm?@o3y{4S6B)hH*rrbkNfIw?T6;dWbg~0KcMMKES;l%)XNi^&%cM%_df`mtLdKk)wk|-*L=Jiu517FWH^oV9rI~=&%mKxt&bC1;D72?-~DK*_A4vLX5_Q@Ez&0s!@REDa`+|h>-g+;&DVbJ|8ueW-kwKwTs7~m^Z9~&GvGh`-lz5R>PO_WsG{a?x|86#-Zc?^<QtUdT_No!M#1qY=b4*0Zp;?#=k7D3k^aPXjOX8uoD%GN=-YE%P1bUD9E|iG%4z=gi%*tnx|an}&edP&xN6jkv4eeszI{B>)_kHK9@l)5*2DcG{@7W*ID9knzcckXy%wwQX|@LUg*pqhegeLmzSVFz>Sz0C<nuYkPkZ@!q^EDv_ZM8R>CMk8BL8D6Fn{}@$~0e)Z_+oGZJMh2U(Ba|V0`uzOQGolzBe$Q*ZLait;ff7|5a~MzQl_x)tIzLwVbc=YQ5Nx!gQSU)R}xl{WiCBe&Q+3c}V%5>KpEIyR|?48gHd;_v@y<oqhgA^<V7V8SI;G`V;5wRLy?ku;!OKhqkYGZ!>MLfN!UQZxpYl<?<|Ar@mDu;|1M5{g=*HKla_-4`RNZc9{Cc+NF9tyIEJAj~QEH;irJ_?hM~t(g%Lq=_ucC$Km^%!2hWg=5_fWZ`AG4#c*8L3Y2eFdc98F9m3(4&ZPBbgyz)rR;t^FbicA^k^bw;dcAm-Tv6ZZdt80*4}Ym|FW;@cIcC^--EV&06}}+fP2aQZhK@5<zWT_&Sz|4~cjkbp+P}i-52t^yzxwvSHPpA;EJnXt{L&8gE&Benf1+Qssf2tkHAg<92kUie8BY(YpQomd^Y+`#TY`N%9KJVXI>yzF2h=w&H-<m!`>%a*_?}$@(Lc9NP~U1WPWzh`w)R)8xA=qM#~+S<cy*Qf-YpR*&m!M>-M-UA=a~WDqHkHnFb`~W=76T}eSDX0-)Xd7%Tahc{3-4AdhyTcsq-20)i(I$JE-rz0pEVS0sd=``bKyJ=07cas_$)G1kZ!^O<%BY2K?W4>3&wLM(SH5+hhFPcy*hm-&X;Ci!4Y#JO0=>{k```YyE`gKzZ8c+lP8tfqdd+K>8cY^!dX7&+pn^?%O-}tDp9k)~CDoDqKh3Y*XI|sfB(pqag0@7uUhhQuRN+y^{XRD(YLA3aD>nSPg&Xk^km@csP#RC8<95+t*9zd@ta8=zFH)x-foiroQ>KA;$T8<1lW}_dkJe_ZW=pDb?$Jy8qe6>U(#j(SG}}Z=4yW_ZKVvG4=oVTyW@~&llteo(ufP_hTGwyH<T`TU$J5+(7w1_6?TbJ88W7f#(Q+!$+Ebzz;k}xLX`S|9WSs|G#;D?*1cuL4IJK@2%MIYi;*Ws-yhO$Bqrv^dI}?FK_kw^0%mfe6pX#^KsL=dOr>LCVe}x7xka|Gxd$W!_VpO?PqHGfbZ`E-#erU#<$JK_v-J}QsMe46RP8(dG%ZMJv}iWcXvQO0pFx=#~>g3Bz)ss9z37joTKRjzW*$IE3z@tXNcXS+tV6hUCKzc)feQO^xduQ>A2*d8Ku5`ry=^=neStLarpkZy>(r}j0s2nxe{rA_B`ua6#e_(-Rj>ukLxR8H~6Q1SKnyZ2+#G$508w?_fA{)jq0VH@Q-grJ+GaQ^%?s1G5E&LSgikSTBp7{2YmlOY0CKG@V)<sZ~q=19+z*@H&(2|dEH%#bqLmHz&8VaOVp=XZ~@9$9=?4J_4%=H%|d<peM51+4?o3v)%)LdeIwx858!)~t=IJp&z#;kZYB8cXIXps;_$u0u6EV(JnoGA6V=xCvNJcC<cq^M-cS5qHAP<dc?wR@?ds?Ce(Sybe3$zEhl4fW<}*>R86Lr(uu;oro>`3N^ZsYyXIQE0R8}VR2k+f))wjGSu>Lb_&*Zp#<9Y<<y#<;hpU45LwESc5pq*oD!%saH&r5$~!u9mLruy!r|LFbHXm-LE?E90z_Y_-+``gpf$fy6|jap6{*S)zX5B#hcugwh`(Vkht)VEu7!tn-N*%a(s^u0s2Vf}E08~F@m`dvsL@a+NcjiX3!`7$AWzTfa18#Wc!-_`UuuR|TNt`M2FOkBSE|M0C<dBWq&hrV?bzEKLkC;6Syarx%_6}ff0ePZ}kYHGhXULL`7W;yx;YT<e)aTL#iL+<GP%AIjL`g!vW%YuD_zTt^lrtMt(9DHkUB|Ywy?=ha$*rdL7^CiZgCfnx4<-0c*ny2-dWF7LUeHQiUX@~X7_0#Cr)c#`?DT({l^B(Ze9bKU1tW{FidF+{u;WsL_M$?aMi1V#M|7lV6%`f45BFe+>7K8q|CLW&W9+ZRM0?+yODVO@zk+LZNp@nGgf2V8?_D%X8S09W66^kRE-<RP%!#6LYeR25ak$ru&K1v$!?-kSMXDg-*)>BK+zfM0AzUSdpy>85G<1j7`xUJ8v-sbx-kNc{ZuE!a}o8Ub|rWNo@HP?Ex7QMpy$C4?y{^AeC^X6pB4)*PM@I4_>I&X2mYk+)g8|$crFm9N~>%pIUeuEzO<hSTYDSy-FEvsb=p0~>8#C$bsFrLF6{(VsMEuDXJT)roDVyqj7(w}@9^TwF=GktORo-4o45cQAg4}V#==~|xTCDFdwyTfl)`LG`MN}*+O`PPIxm?y+`fImO?TJ@uAVBV3oE&MsdG`%^nIPRy@%EE8I3+q#!Ja~^%K0EyD)v(UBpr?-8R+5MM9AGq<ukC9VHt{@~zCQei^YwUsvySd(ov8}nuB7ivjE2eaK4H>6to!B~r1fQgHWuS#_SNuL`*r;EJo`lF2gb{R>RVL~W1c+sHpZbRO_4s+b+qGy+~}uKRp56!r1{vZLUmr?ZfL?E^tINzeX;B%t)~{*;rDuq>&{&a?=23dg&*tI`-pk4`J%XdV@MiZ|FIXQgunRpden1mT^BHCq<~-kjr#tPwbXZeT=3W2(d*5~kWlBLW`z*=(_85Inx!)1K5)>0KN!AM0lsJRa6FfUzQ^;A_YTINXT#uIb#)v!a<0X=SC{^RR9JUj`(B?fOxF<j4W8q=8<SSo+pT@=;s3i#>(hLEeYI{6YYBgH4E&9UR;yMi5C8Ez%<tR(jd3z<Y519vXnUCzs~^>N&RGinm++0|@cm=fV1D$jmOf{Cx0TTT;2yjbeuo?DH2u(3xG(%Z2!7A1n%*jy2lK~H9pN{6f%U#COEIpFECT=LlOJ{e3yJam=SeR3iNf@{w#sAN@K?IC1?}ryiS|CA<CWFtI{fX2^}U6)ew((h@#q@-Z3prG;|zRn^eXrrW^L2-;U~4<+1VDtFZdVpnZ@_4v*F)As_z@jPLDC~i=BaWg2JOPuk8AZwu{#{3F$L#()_*I@2}B%>o5*}?bQ05Z(Lq+QuAvH-<&fH<MXToI<K>TAB*(mWA#0Xd1pW77u$xjJni&-m~nWC)`NYfH~fdSbv(CjywG(+_r+fDy*2UPr5}7xvKsKa;(R@`R%*MOL#o5C&-Ylh;oAiw;3q$?>v2}tR;)ueEeU^GHmswzZ#6qE-`aar*S+n3io@UZ<6=GUo-tSlI<|Z>`u{0?|7s_Dh3C{71K<x|zE$(d{u=k|H;LfiiPh`hDzXRtyx=3eXCBfU>wIPAeUJUGVZQckjLtvJZNFXC{eJP`z4!5-b$;s~okq9)XLn#e*sZ_j<1JWkt)^@61M+EoSIc8x|6AM9m^K1_o|}txd+j;A7hGH&{)wb>^|+P0W1T6y8vLON)wlkD?>-YBet}uIALZMk<Gl6R8-4Ed{I&_}46UBxxt_j3-|TYI7o6T5k^tjr>;I;=4f;&)AH;RR$OMBm-PWaAKj!OWSpQ4A0rQrWMRcAP@ICb11Ln;QPH)zCY5wk1|4r|v@9EF<3y$%)ITmWUcelnmkY_FY#J}Kvv(URe*tZkGH#!Z~ernf-Z-uA9dSizLnm*v0^sOBqrLTj0JRhg0?`C>);e3>*MGN$k4)@T1Kk_~47i;@lU4Ddr{H$Il{#%(aPp0ob2H!N!V*W693d&<f;dwA&Eu9Ahe3QPBHXQ505fhQm{uFv%{%5oG`RilfohRMo;Pl4*Ww@Wc_;31v@5znyX5k6&OZ*JKv{%!A?Aw)7;rT8{ca(oZ4~(04?#=MU;d|?~(EGo!xij*auvF{KPS_0ZNk8(<&8hS`!g!P#e(4)nS9Qh*{r&Bw4eCd<*ZY@$Y9AeMt*Zy&k1C?~S$ChxnE!vj|G()Ae}U(KNn7EktAP7p!-QBLS<_d2EAL{IvmEAc=Fx6Q-~0@|zsc7K{dOSzQRncynI67zr-S<5%$TRS>(>8O>!*KX<Ue2@uE(*X@ZHY#D#*wB3gs;F49`if^6>B9)8`_yb)>#GFsqh;-?lNnbE;DZ>xdg}>3XnH>Z#6utc};OUh?ufeB--}>PJo1`-ri44gB6kF|Yco8RltSXTcvmUgwu~(yF-sK5eSLr_(}=UuVCc9_*X+&3o~5JhPY9M?Rr1bpBwk{SEJ3D${TATzyZ%ed@a(*M|SuZ5?mD@AqMz)36%+H<9}Oz~~c#`SX(^@LiWNKKnwoKN$5A!guf0{$p)@f_2k22eciGeVy_A5LH9Z*F3ife#<-<FWP0ty4(An@Jm+K`?&wW8huY|9iYFm67KJ**W&%~rS|ZLw!%E*bv(?AYPN%4W)AKL&wJr}68hfK@V#&9VE$F24bmqXgn7dL5FLN4Vs+t{NQC!3C1P<OtXL9$o<$?I92G<GUarxTb?P5`sQupP*9h~s@;l(C@2TZCuUy5vV$^i_Cp)6uQzXLsmNb#@-E%u?{Y;vO`$elt@N=g88SPs4ikAOqPWY?#qg~pU!aQvR{i*byMqu8)J+=B)lIptdYUH+2&M^9~tHCc0-(Tpy-k*&FEA>8NG&zOm;z~#0H*BHLWkzHT%)6Q&grBTF-hZU6qUCpw9u5ERlKP#TdH=qa->NbUeve!_uXFFth<VYPSom9Vs_$t8-<lW+|F9R|XEZ8+?`5)7SKqUsJHFqWx?yHqzOg*7zPI(ZawDH<tJ!{8e((kP{;B-Vr|YCidVV8QA$`^~`n+WIERE~5WHR;L^SOS0r2M2{-=Ob5&`#G6?L2RB-ME)vyxlSu<t=gr{uh~bJTYpXM!Ro2hjF*aHEkEG!8G2Vw<7(cU+}!?{R!>3Vix?U7kJLfzXa>A<1v1lx4Yu~?YIh92gp_*>3hA?`+-&YPt0Ro^dsM@Z^pv6%a(&*Vy0dfX1#&<F7Qnu_?v5M{Tg3AM7?GWgTJM-o~Orsa!0W5-3;Hzy-Ke~|F+kwgWJXbcXgdV1bmzA;(d`*uX}InZG3KXVScb`Kjw8cH?96pyR7Vr=WY7_ANhX#*Xo#u{5cc(<jsxukz=N7fA&7F4?pZN#)aJR_5Nr_S5V(tb^_0>oF^M!{<2DSW?`h?S03YG-s$j{)zR;P?9i{VKG425{KW<JIl^u;3-hwhP2rE3uIFXmo`~;D%9Ms*wxq6a826ju`-rl6@xJ~1WWBzO_+O*{91epYc@6Wxam(<WmFTH{|6=@@RmT&nUmm?4{g>v!kD8~?%l7o*nvbz)Al}!#ov7cb7`v{c9#+)CeX-+aU9U5{)YNg_ZW4ujPtL)5&1XHZ?y~(Y<|EM)blzYY5f}%)>;wN!lPQ}2?lBlAFTd3HIo=`tP%nAcR*cIx64!BQea?sPS-|w|rkQd2$!;Wz%QuqJFLoa9o%{o^uKQx;reNQo@BL>y<|Ch<L;5E0t?R3ip1wifEXVXIm%)GAK<m@${SW39=X$`;=)rSz-+Z|5EGq~9SPj%$>Js=4B`Q7Y)n7rM2dvlO7?=8{#(m}89ISsPzqv8kx9Iy*@4|Xgm!wF4d<oW5Hq>wCi^I3pWUr&`;~09}%2%<D|MjZNsL!JCPp8xC*`8bh{kB?R_)Fni&){3@-syE>Om*qJ%Sdq-=T&Vj{8#1ieb}p=xbJKl55IH?ozIv>4&uE-`6F1zs`6Ctv-Ycp_`WCOVfcSNQQu1R2;T$!djS62KQVu*HW>Z9SYG(QPscjUxV^YekK}~^Fct2n<+9*A>7svYdl-4r==Xp2+k4ud&7m{Y_cuF&>#fTD;l8;11V>}FTpRizpB#9;^~`^WbrAY?7<~KHL5xq$nj(F#!<b)HpMmn<{sR5u>@qwrB+G<)|H${JJB@KAzkz%fM(B5D#?1$~pDtRA^|F%%k-pEk&B4A&-#Xk0_n&X(sBa96((la7?s>Hy?4@Ioeo_g{BfpN;b-|B)PlkND4sQ$`tiHGI0i92~e@xKX7l&^}>~E*#uih2MwfkUw=_$Sgw(b^$KXnh%#~Pc0eR~Rgd)yy*ueIiymfM(=Lf65pCCl|bVm`S5KYlTcd-Vt5e)VQ6{1OxN`!KUj7S#Wb-@;Fk8S~XcJ20*U{N2m(eaV6Z7!MjXgMYC%)}I%g!+6;JTmA0UxV9SW-lKElJxJd!@P|IZ{jTXF%o}5B!cWo`?fEDZ?mNCL@cpyU|2NOU^_Vvi{07lj-x$1eL|ne7<}Cewz>1or>xo9Zfk<C{Ci*9R+Xdh9_QU(Gr4y0<a6g>y>Rb3Oa>*F@1ESS8PQo{COxN+tFnjCwYDU`6P|tHlz>my~dH$g~7!R`@Mt_aigy)?Hw|G5W)p?)sT_#n#%O9xEfZrzy^ZB0+V4je|hCj2SUcbga9k70tzbgDOD=^M9O^N5V&UI&?KYWY)GZsfZm#l{8@-`;go8K)2e4D-<`USq1=wDTRGa-D>S2K{FzMH<6-z`|9^Xl`Tabg6XFZvY1``bdf;hPzeZ@LS5U;dwe?`y38*JApWpG?K|QWO2IUsA0fqf_B2$gi=^gRP&^p&mR%en3AOspFmzn-TYyze3<g{G;;<dvqVP*Uw&EUpJbpK)IJcyYe6Zi&5y$;i39`ZS-q1Uj04!G2Yh3-z&(AYt<2%wY=5_H_DmeSAC8*a!2ER<-ncD-~00@RnGT}cLgKk^8GuHb*LER2j=<yQl37(ID9i-yIz|9!UW{=`69h9+uyy?{$O0|1;59^aZr4}Z`}O?ejm)wjonXB|7mK&Z@L2G=5qSKbke_LuudJt_XI_j4~fh74~x<73ydz6)Hh1c9-zN(DvbJXTui^4^G@u6?=)tY`6<}9=zD*Cj`x%Q{*LwTClxXO?9?3NSdT_S(Z0K|u9z|${gb|3621|BL+7(b(%1U;G1k3CxDHz$LwfoqeQ%#}=%>q<;_rki*T!>kt-*Njb|63e#HsLiIFl}*-Pb+R^YpscV*Tv}*URX8==<Mv)A8I`HcowG>N-5X^lFCsse7%T>Tfmiey8UH^tb6N`l|kYNXIYh!b$Yc`V-MF0?#9(;^VmV|MxsH{u<V|woldXO#;sy-Zl|PPe1V7;ccG|<-8xNzH#v!-dFZofb-4Muc`Vw3*bG<r&}@3d*(J!J+U-Ok00TJZ)Gi_Ix{oAn=D!c`B(|zS9yo$v}Ivvmydk+t}AFq_ts*n#;rQqj-x(7e`xW#rK&vu-(gHRjP^RSRo5wugxN4pbDoQJyTB)%^?W|Pjqi9zcf@y1AN%X->UT}XcPYA|ybXJz9~4A;xeD|~dA`DRU%3#juL2wO`+D;)yvH?aja(F$?`iZo{$3+ukbX}TXcy1*D9j`22gV2MVP3pv$WTrHKFRnY7UNa1Sr}JG-q-os|N6tsYRHFvVBD}4zsGS8)X@8<F`yORkG!dd^NRjTeRJ=9tYc2SvoY8==$o^CLqF+_zh^S62aUBnS#P6#@7>XLD8v7*i{>}98tSL&Wc}XLC~;lOZ{}JKf2VJ(`ibY^IKI?quNU#~J=1~SI_}tc(jou%7S=x=;yz;K$cgk7e!_EF5nI29w*JVB{I_g?KN9PB#+RdzPobOe*A&uqZ6iry)I(~IzV`~OKN}-+Bfa^>G?e=Qo^Oi}Li^Hp)3+-WLp{HHq3=D6j(_MnxK;EP#^>%;@mx_gJJ#P5y+--xjm6(NE$)u@Zih~x{8j$NJYZ5h%=ad|!n|w5*abM>1$w@A_;Zv$JURMH`5E}Tqhu>l{<&r0pZ`nqvDdqhf10lFn^~Ceojr+p#ia(g{+5kLIr|(#IpgoeI{m7A_`9zR7cN(9@Sndr&R5{yLW2q$hC~u0)acwU=ueKtlz#z@`%jL$miT}5C&xvL6e;%q?{AKiT22|hc49n3cp5`^A$1~oA$heSe^LrvK%Gby{e~?1J$V6n1w(i_bply*DS5sVW26f@G0KUthI}9DOx>lsIPr@U!$ZJ7k|*)EHS{D+h7j-?@^EeoXXf^B@+fLn@+k5!>Zjyk<d)R*<iK$y@4#^b#~8)(NeGXl4kJqlPc;z2i>NKh62hwtgz!pgda{J@V(O=43E`R4tYit{@2Hu{-?8jJP~}{N8#&S3i8c)3jtt>$)F$L^<X+VJ<X+_N)Vk#E<Vb2gawNGEL-<RE@D~i>nhar+T9<5+%Tw!<%abcmn~*Dzt5KVitC4F_8<873(ZGqX7{Z;Y4auF!U8zmUUCF(vEy%se{iv<U{m4-a;Vul}whZBB4B<M|7UVkQ8q}ub8sw_fhUBW`D%1w#D&*=6;o8*3<cv;VO6$aJhff;NTU7CHaa;HkC-PByGlUyb(~=vKD^fF(E0P<9$g4AGeriT?e)4;kP0I0}A$-mFP}XY<;bTs`Gvpg<XZlAyMm|A4PCZFJ$#Xl-5dM=Y=kurW;hcp<-!aWQ=KCl2{gd07oya0(X9#C<VuTX~oG3&MBa7xBkDwN&<{*paB9EXJq~;=zpysCLB8z4tXJc7%Q?rmqP{XNN$XR$k;Y=g?88tI`1hoJ|I4d<XIWy}bD?|8GY9?|fmhV$)E^;oO|EJV2@~7mS)B@xJJVs8Y$;s_XPTLi9qAWERc?!88c_g=mf9AI6Y;q;?&*ZY)F6qSAPSjw!+1wVL5yWMKwr4Q?4Ei;wxyZSgZ-7T~dnET4uI$7zCz?`s1o2dEi!KV{0^AlYM{Y{4%qYj-e{>>|6L%TH@2LM6;4fX!@-Bq%Uku?SR7szN+ro1g!jl=ov#4?m;e1ZCcOpBrCD}zy$q>%N5cW`8l4nsTQ(KZ-GT%TM+6R?QxGyyyxi7gmLpV7#J2_Ck<P2ehn$r02PdF(<xCk{5xd^!j)k6-PPY;Ih5~|eO66%j+3E^K2gz#R5a19sqF8MCotcL4D8`oe6_o0?2_aV1p2v268kbW?k{UHf?GWlor390L!S?7JpKa&SCgv(KjlZ&%{%Q1u#Qw?$`H6hg?8?5()4B-q6;S$s$<Pzj)Y7cS`)^9ZRS8_CY6GM0(+d%4lA49m43o7;7iS^uv+=<+t+KSws9KjG?9|D#7UC$8SXh5Y-H?nRAl6O*LsRPNe<cidC<Z`UXib3^Tks(}}A)J~a9G{wyoRD=LpCO#qiPF>vY6fx!wm}3nnp~PXh#F0fX1xz$8qpYr@HXlu@;36p5U8}xL56UBr(WB-pmnL@*QIu%--&Hgm(ia4wI!FJMvzO8w}i+ylF*GIQ1LfX*VA9m_S_f})PDR;*k%Y1r^b?F*-pc$mC5m0*QtZrAT{&Z#xiYV-E3i<)MuHukW08e)RAy$=AWAR#RT<@7#=r<`46Ys<bh6}edRvmLI{8ELI@{uA%uG{gijd=;XMXI_zZO*Ij6Jl9}ZWcz9CBpSE43xfhB~SP&1I5kUys;BJXpK@we0)^*nhCc^CCES@aNj7kMr96!{d-M_A7N6W512`GjQ=4GAh+2+J<|PsoRJ`G@B#dV?&QlXW1+Im2U#9wo0O@1kBMi(U#U|0SNQ=u@)jzMwkk6@oetZBLdEzD$iKO9&sLddLzUw!4S@K)46f1p0~aC)8-Ngm4J8Jy}BdA9}sWy;xVm1LS&lBB2W*oSr(AEFm19+J!73{F>e%vglQ^<bT#cexgUn62e2Ne~=}FyHGEZC4>i2pOZgx%5Y8UHU!#@e3?9i`p^ImA-^=B2gvv2`gVT%mO9-47jyD|;A}T^be*H$IkAM=glsx7liPWnbdMcP<LD_zlXE+*qm5)Np|&CSbYh?rQ4HY$P84yXqZ74VICcRix>9SCYcow(>Hu;>YJZ0CVCn$!03K^FV<6KGWSIi{_GEqy$;GHqt`Bu1nuZ}<iyB3a;_+%xJCZx{JZmwE1mz=~mmyq+TAN&(by0>PoXLsNA<zfZ0%VB-Jdek0r(dXFhJZ!8k|m`5By9yJO=}n0G7a}HNENRje``&C!1gc1^aaTUnMOD*wGl%&lG>Wwh}wqQnk-s@+=g75d5ZoW0<A!<!14(%4uPJcihqiJTBaGz`dUmCKfr;qPjYyZ6BF70yYd?7N^d50Q_!_Blh?}<@-gZr@)GJg>L#-2B=S0P;QA9SM4d!#LQP3d$ug#M%6;2WeRy#qhYOx)X0qrVrcFn_%@AJ5ycY6YyOOt3?~p|$udPh8HK<RCUZQR#Z)N&RtanLwi+YKCiD_<8bC7fJd~R`H(LGf0_fT)szs<7l2|AxW43l{*CXZ$aC!nSzCm<(hTg!PipnggIlD{`#2xp?EB&TG1Wnu`|p-v)C;xXz_8;~<mWjmP@S)52n%}Gv3{+7CcEc&VI1OLfw(XuXZ7UtWAzdzw`62jrsHe?CmujnNs7jt5|6M3n!J%O5oEPBTPf9^yodZO12u;?A*gMY*L@LMtNC)zkD57F$@#^lCKmz`yL;^gtK0TwOB--WX?pX@wdcKSEC&lBTAIc~6gH|XDCp1FC9+&sqsPvCYsN3%I`-+&rq3E>CS5VC~uP3m0(EFt`w8ZQKFJ9^TIXAI#`7xV;KLO3P$3|T@rEA=>8^aXjjquZS*%n<&Jx|94FxhVB0xhT05bvIeGD!D4R(@|fN(~+}LUy!qrn^BLGkMq2mF@&p8PmrsTYg12>Ym+NbZL(-R@=KO4iwk;`EFqkjx|1v+oQk@gEFt`e-g0s_mfN6KBOBxpYHe}|S^7e4mhmq8hHyN3^+G=MmBQ>-h1q7ppRt_+eXJ<^VNteEpic_lH$JqPa8<UG@FVs=IlpJ@cY*T_WqpLQ&jsoyCF@T#tLsC33cqCkd%?Od;=~*0I4h{}L%<Tk52<y@56MrdyU1Zqv~pq$)khY+5X8;7EjpGQN^VXL<8~`@DEF0ZFGILGHIyuxf-GrjaX%lqIW+~jIa&5|IZ>S3Dah5SBgi9|Z*``r#r<655>zj_1X=c*=foT*#*x=>Tev*8MZX}2lgpD!b9)YX9HTUUk8om|6W=&dg&e`(%9A6=RjBjG^O(L0(|p7I!pVU$k7K%V^o3hHaoCCa)U`pplG~zlgSaNQMaz)ulUp;&@b^PbY<K#lkFlAaXmJ<#5cvxi)I-kiq<1^ffg#+AA>583oR=Y-iXj}2A)JDmpPYhRj3L~I+JW4MJeMInh1!bTishKX5T5NsV&}Zxk|o{-rFk2ar*Kjy?fnqwd#d>Fsfp=J2;XA}&u0k##I$m}pBTbDsqM(^SYJIE!bPd6$VJJ?7^yh)red9jP*Z#ul9iJ%gv(Nkk&CfT%QA!qFoc&;=aT2LZkBOd_=k`W_4NZoxSR|6o-85!l?x$UlX{PQk98+3A^aOdc)bCYdR)&C?oaJW?#cS<&k!z2O-3$B{)8c%h#Eo;VcjKS2&ZQVe@-n+F3Y<6oFP1vA-sXQj4UekwSoF8Swfj1T+)RQZb|)t`~&N_B}2F`^(*pMtkb>>;m%a4U*UT6_H$eO{j7hf>;2po-pu;%Pu@%(%n&X`ElDoPx-P{KF2fK`M@>XdM^3;HPD4#kPS3hd!w{}S9ZIf59>x$3jDMm#xIL6Slx?tsDs8YMu+8yuGuuYS$PH|t;*63(<ECf_YDscQwo?acUvgj8e+Sox_UOQ<$Nat^%Q#(+Z50@|_j7y~mG;=q5FSDuOdiZO7{VyUc1XZ_Oh>ImuEgI1JdE4JxPKYe;ShR09$U6$y<FC`J5w`|C4^(C3CI${kyKejk7NiBrv5=5$h>|x5W+{Pv1AG1tJFxcgzzQmV6x~l11#&P{hT;wAcXfC2;tKPLbxYGIH?OET+xLPPDmX<&gDc^C;TA@;n&p4WC`K;^qRUptOE<Dr&c73CL|~2c1CJbaz?U?TAA!3zvVHjlHamSH>tVEdwKrrsE5hx$h)am$orkx>cnG)@CE8_@@}RVmilZLRL{bPsr|_k!dIvr$P&UAs8M9m$3gi^9kruoBufbQr@F`z!X2n@dAts+qbTZ4vYhV=o}cJN@>cS0>K|m$BjnxWb<}g@bL@Y@2c3B2#4Bp|5b!H<ObGNkIfi_Nn%e~)?WCXK#9!1jA>cgD@7o+s?E?QBf^E@R<YbOt*oiPF8c6*yop|!wc&0fJ0v7$AY&o&oi55<rXF9hFe1O}MS9RtuA#6I)&535@FlsV}$$U(vaq~RR^ISy53!Il|7bm(?8&gx0Q!|go)Mn(y<nGjNL3xPwrgkHDW0`tWtCPD>^H8gktMmMYqn+sI#1MvX3`4jFqnZ=V8NziK)!0sj$$|P5Zb9uq?!i1;P@~CGmOwj)(Q81B4r+hVLDXn+G|N4RAv}~CLyqCGhceAj=GTtgi`s+SgXh_cX+%p=o0FUK{7W%SDc6VoE1I3#;%DdYb;x-fzpWD;ojB{nDso5iQikyF)U)Ix)Qi-!<ReszaWUu`Sj}tWd-6}zi{y*U=O=1Maz~c)Cq~<#eA@C_8&7sq^N{m7=b6okc#IS-c%u1TAAT1tO3hEsMm@)|K=c(={8#i}@!C62eomD%&#C#z`FZT;O#eJ+%n&_IeNJvrC&U#R@BjK=g?;!Zb#46Te;oGlp8x&aKX}gpPG0}}_`gA&1p57t%lS_plJd$IJjVY6nkWmi'

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
