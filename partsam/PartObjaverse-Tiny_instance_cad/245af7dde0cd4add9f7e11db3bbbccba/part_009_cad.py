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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_009.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_009.stl', 'source_sha256': '42afab9c7d2d1af098ce2600ccbf740b6419790126c3ede5b29ad47ab876b067', 'input_faces': 900, 'input_vertices': 484, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.320886492729187, -0.49999988079071045, -0.4453279376029968], [0.3209107518196106, 0.28250837326049805, 0.363783061504364]]}
GEOMETRY_BASE85 = 'c$}r22b2`WqK12jl5>!-4nfI5$q4L-fMf}h5r&)*VM!v`<e*5BDButz=NuN8Wy!nX!V;D|U_voo^&%J1w^jAkY<IEuoOj;CQ|J5Ur|9YFs_IZ($5zeKrps%oKgFz-Uk+Ros$f~7WVP~IqxuYw8qllHh>AmpjrCYLWiI|`E@;`VMXOF8Ym_yvRPR0`dJQjC+gqwm-<qY$drS3wXL!``9z(moGrV^nkvHlwctoG%d_?~q!}=tDE?u=|)$-mdWy*WUd;gDrGAHkX-EZdQW62D@Ipw6Fx6KDTBgHQMbUo3T+k1aqbu5)Uc<jkZQQsFoUFLSN!WW&}3FlE8b~<xA$Dfy++p#hYJajCTJk);A1ySGHcu(fmKVKy{_s7ij{^;EP+uoI0eVvEvKg~?OGQqh&W**)ja;w3@-Ko{rxvn30`13{gaXxum{=M&^EB8lvFNylz{S{q#uwj&>?@4x*A8eW6+>Xwzj#u|MbGub$RsURz1n2g3Zhdikk1H>-LLFcG@>N%Rky|;_E{t^K-Xa}T{hN6cockHh6OQb4=E1r-)P7$Xa@E-`X0F>s=T<`Q*^#N#*SW6m9lPs-{QG9#U2(RHnd^4Zxz#G|*vM4s>s;6OZ+`iLYg}};uF1dObo;!ky=pd=x%GNlnFngMy5ejXom*CxfzCV-_at8K-{2Nkob94>%m3~mS3kM6N9Cu!k^5y2`sb=Mw|BjMz?u6N_g4AD3m2UG8O~pgI^fLx>(9o?&-w3PcDAF=t%7e%apr;8US}l#wLQ`Ky*js!zO}-c`&TtN<2-J@N=4-O2{kJzbMNTxH=X@Z=hn)>`<?yJn(LLhZ`<NT*YPK}@}FDj%KvD8TGn53@rJV>ntAyAKyH<&wl^}B`Z^Ey!!FOOJY&Z5&fn!7UqI&e4;iAJx$l09Q}XW@7rx=_w`Q*Uq0X(Iopwd0QeWq~esES!)h`z|xi0^{@@d)MbZ#9gzAe&`d%wu4@`nwsyZW2XZ>5v<eZ7jwJY>~8;cCaeO;mr$RYvA^k6lU5exh@$;DC*hj@+KHHdg-oW#3$M9v_`s#sApiI&Q^kt33aSIOq53+`jP9QD<&V-4Y{@<Gd`_oc&PeR>`O(k&fIK@t(@R{r;+Jyy$$)fJKqce)W0hp!~k+yAxdBOK#t8wA+<WpDFu6@cl)Xoxe-xR-L5TuHRd@*FjnTrKWeB<3i{5whv>R<H9#@mKy(Q*WPyab2ATL$H}c(b%T+q)Yo}<T<kirU+%}&pD($77rB-9^R=%2FyY{SXFmycp0C<r&TyIgJDk7e?Ehx2`?JoiUfv^-snpkb_<DWm<9+h`8dN&#{9c{gov+6@^I*QhGWT0oZ@R_{xs~ztgU<01>Qq2&zuiSyKRhnTt*(_1I>(Duy{Nn{hBlVG=^Ph2x3-So=NuQ_LfQAK_DZkD;rX%h{Aag#S6;t;FXxhZ@IO;!?mv=2=2jn7-`C^M9rEvMq?ftvOQ-VPkL7U+M2y<)+>SR`MfIP*2D|gJS7d!}-^%K~=d1VQoyRSlk1lY;nTMtgl=oZSh^p6}<4)&R)P$|hap#}*ip&GwXT9zmcRII{8f<ZmyR@0){bjIJ26Y^ER#_*v_b9#0tqEz>aqsd_jt~3T+#Sx}WiNRw>swhTyYhhVxUBELRdBm%-`uMHjDGSs`|e%Z=IYOd*QxXOfG)1wo>E%&-@uj^-1*+qvc9jwf40hh_vlS|p7BK#z2wSsc9<FI$h{ZlZFOxYqOaP1_SsvV`)S>88ZCM5Jy#wmF;QM0g1OqO?H~H)v~&N%d2ESTXKpXOBhSBf@7t%Hzbl*<tPtzWgSS`9+={z)+WC8R?z>z$)|uO*ipV^;IR3Qrcj?^DSSQw*dk=*+%g+yreBtVcIv;XvzcaU|t=Q~pFQ2W>H`y9(lB~b}bgKEQy<(ktuy~e@GT*O`XJ}x1d0w<8J>4LG*P!m|e6G)j<W|+U=R5Pz{GU|){@KnskF(B$d7lQIxqtNS4X%Dzx0)OWcFyB!J2UD3V@@xX?fm$#`rgB7WbR*B?}Qw`6KBiZKJuTl&h`rD$8y9tbN?Q{+D`vp&pO*HoYyE2<I3k2*x(#T*5gy3%I}SMyxujwMx;^uQ|CLG+jnoBb+s>f@L0JRXC6%7ex2M-?oZCT+J)R2G%CiK+i}HL%le&zajyPMZqJ%~)R_l<%(2?pzIM0l$L0QdlhpG^z727%aZPT0apI_}|1a9J$~7K)xA|Od=iDxt+xM5pIgeX7uXgjOGY_rzt32HYan9oq&a34)=E{fH4ao1UUMS9a9CU6c+&bnuZr!VVCij13UezuatE=nFzFI4txz+1yc^&h<r|#o@Ir=8J#vQrs8N0`oe|BfNb369f#e3wq`8(4xS^s<0Z>?WG`A}~EL0Xk}QvEixJz6~v9(uIYxgGB-etCZL_wTgS*{|$k&(D?HyIa+j`}|RIJE4*}7s&mqbtB$2?#S(F{%BW!h`2Z3`Mti&{g0|~c2efSF46I>b|<&%FOPQhlL`CgJNuRI_mZ*lcWharwljEZytCbPZuQw0?dm7FBUPUGVZ5{5b)I}Zi+1MzjML^h`(dbI##M6vd*@Yo&HVAM{y=Wcd~n2-U)cY#^Emi(kC*oq{sE;YJM&<+^T%XAD!0Lw-(N22u55?Z3*`0O%&n=lE<5wk_(+-CRazvv@}^#u@0{w|PSBrK<u&TxaOS?U8Rd5E!n2Z`x&3on^?d3%crCTuU;Bo7o(Qy^Apbt=?`l843tUev56*u1vNQJ{ZKLv4)f1h$l_sCc^ZRc&^WfKyWIb!++9YT0>s>?bXCU@kYPo;eBsIR9b{Q?}{qv7H4mH<ZPc8S=sd(9$`}cNM_1jlSbmoD!1y#O#@C{e}AAVK)*?4=BD}T3~`kl*9UrQ|y#dK5i1;?_Ca*d<M@$xy+{(aP~dREGKx4QXGxpIAe$kKVTGY?;1zAZc>wcPLfT|KAVANHNdt>ew)?+VWwko%h~zoW(%&-F$ge%{gB8F)xOH(4i#96FXt9)9l7`QY2``vJZELpxmOPn`#c)Kc?F`hHU9a|)k#o=<dc2eO`bo*%;BTjo30`5~Ma80;GF;q9CEMSA=3b&jN#TN~;}r@H-vPY$QLKR0h5PIdo#tvsCC@3q>s+@0F-v4-86lG^dKsts26VR}B+$e(GK-zv%Ly4mhJH{0F*>SJ}j*7Ksri{_U7xX=UFeY?)B=n8UvAe_$_RYiX8uv7ki{XD31D`Jnjp0z2iu5ZI%sUi3KmwoDZWk0LtXUMIyr_}wu&U3e|EkAR82_{UG`|Ix)-$>>S|8hNVhVv_T<#j#$9GY+Fn=;qu`Lb2z@$+|`(LvUm`Y+dWoX)MJ1M0Yt2iuSCC_hJ?bv?)F+**)V)(=0&6*}*ipY{DxzL}q?cDo(r+#laVpFD5)V;YT?+c(a8X0FeBIycXIIycXI;rhmTFPt0aJu}zmz0mvt6Xf=d>xh}_>xj<H>xj<H>xj<H>xj<H>xh}_>xlL33R~{KalJNkeZAJXdA$zj#`Rj~=Ji_V=Ji_V=Jndl_4V3ry<xhmpZt+m_FM12XU}ovWqNLx$2~F2Jk|f)_dhx}?|;1SHk>bW<GxGh=6#o)`7@cD_jNjd=DzORXjR|1pVav?_mc}UE|B$&`&gZu_p!m*y=AV?5B}Q`^864gIdGvf4}G*+-XGe*YYUyn&HlQ8ysxu;<(Inha#`g#_7ANo^YDDpHzU=&;-jvv+|Haw-k*p3o@Meg*ZsioBeK3dI-|;s=Yl{|=M{20f4iSMbpFh9$DFJyo%?C6ZYt-md`GJXT>F1K*KWE0WoyaYd~VXY`P}5a)=M2H<GC!H8_#9I$9q+7Joklj<GIhbEpC--|Kol>B$<?`?%$2)P@S94p`l3;tL5)Do_}?2KK};mRbTDw57ykw>iO3ixY{+23Vf{Idu0E&J8#(Ffc#v({u<|Yd~f$q^K8{RNt(~^Iyax+Lj!+UFZa`!AJDluKj8oM>3U~>^F^nV^9**cA{$)&Fz%3?mk18(DsyvwBb*!a8+Of^GB@W>!nrYjV#gd&+hHEY*D+GfdnCoG{bAn5>KUWvZDM{^xiK%K^JnITYCTr<jd>^EPD{RDu^P2>&pSnv>voylU7aWYx#P<1bmQc_tpCJon`CaxkA-t%ek@dX>1Mf~#{FdQ!Iv^O=j+0`F<<BX`~@}7Ys?4g+?)^eXI-~NjT85Lqt4CwMyvG=wH;$VGn||AnP*$e<MGUVsm_i0Qt!A?TV3Pm(kywu=AAZstMmAT&kt|@=Bgk1s*pM_{g_9+pEKr%!?`&>+`I5L*Y<V4^>%RQ`uvdNsw)rg|Lro{o%<84eN)YQKbf|}HNH;8s(JFNi(Gkd;%{m^_jpb{Z!r%aEc%12ANnSfy8kog?ftL)Th32EGyhL+&i@CpmypNFe7~S`^Zi2b>B}lN-d}`s<Nby8XvA*k@3N~U$?J%{V4N!t?5Qk&PoQuHIlrafvsksB$ol?O8D(z1m$4d;+2cBHyvGSW&92@z8}EGr{l>`Le1D{K^Zk+Uje6>H-vn7-KVRrvzn{{%eYBy>?Oa#X`!Aj^bRK^H^}{*!{%gQowSD9Ln$FGlYu-{(>OGZy-^X*bnTOYDkel!O%sgB_|Ka_v{;b>a<Kt@Gfcd_X+<aeY4ViI39e?-xQ!@`gCz6}*Pt81B|B+ukcNy<<b#A`T4K19np7->7Va9u~^&*)EXD__$%7=B4-)Fv$*17pUI`HJC{66!2cQ`lRcZbeAC+`bFc2?K>be)^;)2$zC%ll39eZ9`@+%sM8>q9v<s^{0uU#s;1*&;4E^YD5A^59R^PdM8>{JS=_SJ!`I9fHoybqJw;5vqOudR@);y;ee<k9FSrsXU+P+<W&$H9x(sv3ky7T<F}Yug=Fh_a!u!^IPHd9`t`R53lzie`dXhk%!lNq$_e-jZ@a2=;K2kUVoyG=lymvH`l|Mx$d_*H`l|Md3YUHffvun-({@l(Yd*v$J?y=8CN^9pMfEhWNxnW(Yd+K$NzPV%+2*kI=2!Uy4EAvJ^zT4-)pRQ()ly%ouW>~%YSFArwZrBdMaP<Z0F_i8{hnjvtQ}l3OyL)%!5yJ%RIQ|fopx2&dv2*!Grl#{ibiq?FY`rt91+H*04zfow+?D@`Cd?hv#9=&vE79b!Gi_s@z;hr}M54t~mR%&co~L{!1S2w`+1F$nBZy1C2b~ugITSA86#de&F$7nVahs!@03uF)(R`%8m7qIycutS`~9&l;3x=d4jVYb*|T2>O63|fU3`WPTej#xANTB<H|p2aM9IXdLA$0H&<>|E~&ovz@M&MZznV&v%1df^{%vwnd^4Zd3e36QQute8hYWL%8m89W*$DDkelmu&0N>_kNoqJ>-VxhW^PyAr_P_R%t(~mG1n*S+*qF+c<V-@Ydh?ZnTOX+ou7Hxnal08a;*+OaH-?y9c3*`luTA$t8Wj-(r^)qKbom84IfbTf3-BcR^`h7-=*Q7cr0sKa#>Chz7ej(H{v_tr}$2M6I_UI!dJi#@fG-d_!d4N?+^cFDesRzwiM^!kMZ|mC;WZ9HGC6qjlTh#;BVly;p=#9yfSQzSH^3>mUu0^5$uRJ!dp><f1F&l!Wpn5J_8>DTjE3T?yxc59q$ZZ$2;SG*aY|EL*bkFP<$rrgwMpc!8!Og{8#ud{8zjR?Izl?3PpGq_#xf}9|afUqwp#4Q+x_O6RyN(;*;Srd@?=~eu9t0J13V{;4JtFJ_}y}m*bzoeQ-Ix4?hPt;^**7a3_8VkAs`=ID9``f$zrya6TTuC&2#r1l)pR%vgLD-j{LoKHe8^2wUR~@e1$_yaN6_tc^d9=Yo~-TzElP3onS5hmG*^cmvo9Z-DnnF8{!Buod2laW#%2{42-U`wD)Ie}%X8D2hJOmcB6yZ;SVX3vk^h`oZydKm1QiQS9rV?DIH$9N+yXY)k$8$)#{|NeiFD)8ZCPW2O8No(^Wl)8PeRQM>^D3ap90g13bo@V59P_;36XKF^~#$D>>n;XB|qd<T9Wp2g4OA$SW9;a^gO-%l=gU=qBAC*ddIS^Olv0dB)L;4|PHd<OnIze)VI-zmbo!47ygydJEH*Taj!qIfYpJIst{$1}h*cm_Nxd=AfwzW@v4FW_}3!mGplcy;{c<Wdb5g8A`6ct)5O&xm`VWra^I@=qq14$p)afd%j)cn$apUIT9r+v4r<Kj0($5By_~qUe7gQ-p7YJMgXe8F(H)gWrT9{3d=6eu>}1uTzBIh4=Bh_zg$j6@D6Cg?I3)_yvmaM3{sp;$Og%_!szLxB)+muZA=5)wm5s|F-!o{0V)&8~z0E4eQ~(@%peBULP+7v*V@kd@uu^56=m+;yLlW@C7_C{t~Q%zl6V*TzbK-unt~_G0>GFyd8WQZ-=+BQpQOeitx9ROBeVmtcJgeN5DdO1fB(E#IxY(p$AWoXM>sWY`7N|!M%80SOc$%zYW{tZ{xqgKk(o1=^jNfmZnpLuZLUl_4o;R20wvcgE#SO_-%L(zl~pk*YPWOEJgS!co#o~$HN=A9&hm!;oB*~w<MQ!@Hjk;pJq%RrwBg;FW`G%G`xUE<1sK1kHL??FYqJyUU(Sai!X(%@uheawDBlBEfnK6EuV!CvlM&d!|-OXKHdzk1WVzS@G>wTUIs4?bK=GE(l9Sx8m|an!YkrU;cIwP{2eQ0Y`;Shp2nk!@c&SRe+j$dg6;4x@q4fheh<G3-@@<WAuDD4hbY4DQ-uFT5#9s7iub@HVFVtDmxNjHl6Y>I9?y;EfZ6aIcpm7*^WZPSy7-H@55A52@SgBDyeIw?iu1x#J`113xney&3116O;A`<?@EU#$zX)&R7xByR3Vs<+fU$T2el)qPfuF-zT<{eBIldXj<AU4q&G<(Y;d9{@d@erQlX8BUO%XngBK!l2@Kx|QE_evn=bBY;3BC%~+Yvq@xx5P(!6o=2d>7n<@4^qjX#4;kgfVy!KM0TD2l3r-FTNXJ442}I@!>EEAC9MoY4P;<a7$5~zlKwUw}8#?7I;-y39pKmgJtk?cnMe>FM*eZrSY<O6<86kf;Wdv@#gru@E!bJJe@~ToXgTt($Jpo;v=9q$Bp2#aNP%lPlI3Lg7>VHz9)P(ylbWOPvLW6$V%zY!asudt(5*Re5ywk;S=FsxOn~*{D;pX|A!*H5A1>W!5hFxE9Kc=czIaTN|`GVUJ&NCQsx$f=Ylz`l(`7u&%-=c%G`zU3h+fMWv)YbL+G<o=0=3~g*~m5xfJ2zhE4D(E{gC8P@EI>T#fJmT<b}h+Y!DW9`mHk1qqLX7d<I+N5U_`%bt|ECgJB`f+uBeO87o_)RQuoCHyl_%6aoM${N~pJU)@KhV~cy92eY-Z>FyZ7jrLSuJbdB@VRgZJ{PxPcihIuz|Qy>d?NJY6Y+U)C_WDlz?pae-v_th`|w}julO%`8IPiv>nuYN?t@)$AKnIz!rS1z;1s+UJ_ydl2jM;8WV|Qd8ji$U<B_m49*LLsq|AqwrU?JWQWW!I-%y0_g<J8hwB=rk@Xsm27sI*uVtfj;@hSLwa18z)J{3;Hr{YWCJbVeh4hHabcr@IHN8>-iU+|ys7d?uiU0<XKe---hSMlbs4c;8@4twF<@d0oUJ^=3qd*a>jX0SEh46h9%@!EJvSQ;;hKd=-<yFQ=@KMeQcduhwV6yd8W!WY8D_(FUVoPtln$HMpUvG`;-6`zbRf=lp4_!_tlUxOcn(fC39XZRETGhWK0DB86YMR+~<Dqat737g|B@gA@{-UA;92jBy7KkSD4@fNTd-U6=+YvXnCmtaZ!CHz}UQMBu~6yXQpVf-*{d4MAP2u1jMxDa2De+nnzpW@TtSbQ2j9!|!`<I~|Hd^)}yuECe%8{k2F1AY|#j332+grZ%4<g@S+v~@ka1YQfa#B1S=VGq19{x%$lzm4~Se!LIf6}G^;;%~sZ_#1dl_!3?dFAhb!7U#3@?`Z1-_yOATJBsk{DZ+zrJs!k2!cXyy_zE};Ux9xJ$KxO3v*2`m7XA@jj(>!&gd6ac_$GK1--O4&AMqIc2PoS02R;igMqAgyi{Uk3W4s352)>Os!aKq~ct^Yw?2327JHR*a4tPUY6K{xDhsE*gxEG4H^uq6PQG`Dv3*tfA?;%`)ub`bC!ddt%+T$TyiLd0iKZG%O49E8&6vy--tby0y*a>gM@e<yVV<fy2$3=Jtj)m}s{QighPC@ZmylWHh&BXh&3&}j6T&_@rUxxAcWjqmnfhXcuVFG>?zXmVj*YG5G2~WbW!wdKY_USrBcxI2{Wn2{DnLMfpe-0+%iR_bbQG{pls3JToyoO(6pM;AdJex-q;o0GJ{5t!RogzFRMR+cl3D1S+gwNqQ@f<J<o&(Pfv*Nk&JTM!c2hR($<Js9K;YE^5(d1H)?HAzt3y|skDaig7q`uz&qHL=u+tR<ch-3SO@w|8*_F1qHEQ}ZC-xQ(<e;yXZ3$lODQ-tS-Iq)2OM}Alc7ya`r{Za57o`7G3arj025@SL1#gi1_r{E?067^5PbNDIzG)4Fscosj)_&EdP@iX`dcpg8`ew=`(@Kb!p3I6Q~K0nVf5XWLy^5-qdWkPc4ms|!VmjTHoD!F`;Tt-oZFM~VrW%wR=6W@d1ft5YV@8A_Zif`f-@h0#cya_%8j>U)Iqv8AbXnY)e4<Cn*fy3}I_)ypiABs1HFXK(|O7NDYyb^xfQrv;x#&^R7_-=eD9Dy&zN5TR40NQ0FMfe94;iD<S`@?>?;6S`TJ{U&fQMB=3ityPK;j7>>d=-8O?!gb?f5SWY-*{R2foSit6ydMICirW3J2(Vyhxdk~@!t4gI1V3-_l0BdzIb~$6mO3=fKBlRcsW=JFNbG<qP;WlS@<#fz;65)z7{UU*W&ZxNPHx1Jf9+bJ4N_rI2zxKZ=ndE0Q=+pY2yiSHa-F0MG?LquEO`@vG5Qci+enZf8(MEkAR}RBPhbl!`JZgcvaXAuZq`!z41Eu>u@msI$j_4#p~nMV0*k8UI8}1E8s7{a`+2)MwkK5h~J<ei1xlg5q><mv})!_lQ->u`(Gia{1NXRE!Y1T+5DI8WwOqH8Bx(nSv1?KS$eS+z)F++pO_%eBvv9?{{v~ZP%Z'

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
