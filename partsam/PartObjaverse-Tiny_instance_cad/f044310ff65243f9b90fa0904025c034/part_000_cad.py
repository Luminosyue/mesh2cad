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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f044310ff65243f9b90fa0904025c034/part_000.stl', 'relative_path': 'f044310ff65243f9b90fa0904025c034/part_000.stl', 'source_sha256': '55f00ffbce61dca686f3f3231387e0e3791ef257885f85a023baac6402f1b693', 'input_faces': 944, 'input_vertices': 657, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2873149812221527, 0.15427201986312866, -0.18928462266921997], [0.2873149812221527, 0.4961836338043213, 0.18941542506217957]]}
GEOMETRY_BASE85 = 'c$}r32b2{>+Wzk)sGx`e6cunlBxg~Oc!>%Kf@Dd90+Pcp%#f5TS&}0ts2E09F@ssxRqq8v5Lhr^!oZkyO{?y%qOShy?fO;G{Z4=9{LlA|=RMC;Pgi`ay1J`xmGtXfwp^8j{i~HY>D%kqSL>Kah@FtAk|-FLmp}2!akH9En=v<;I4RKO&*A#MgZlIvmP`~R=GPlLZq}7~_1fmtYd^kCy~a89#!t`7&l@vs^z^*3<3#T<X3DH_MxQld%#3j+T>paeTQ|-*uR-ISt8@OBe-%v?az|bHdd6UC{+16q87vu^`tC)8#dr4z^z2y!0zGl>7kQmRdg{%AfnL1v#JQOmJ#}`~x#9TfwSxmaUE`y?aQy5k;{!cgZB05(&mB>ej+8rkf{nlZ#_?f2yMK`__mhhjXJYi+dc7A%;-7w-&8NYxMVT1Ac<P=-k#Zk-#>W44P^6wt&uK9%QqROoyR1K-ZM`59qvy;yV?o3}=Y4GJ`Rkxrk$S#t_4Jn6`H_5f9I^Ge`sb_S^xR87jQXc@`40pCbbju#NVx~Co@iKnSva5cp$b;-+}VzYg3dPo*C*R{9sAHY3Fq`Z*Xob7vHov2a!#kPex$9f|Mr^cOpKm;Ozm_yeztoDt3NS#PB?!0ivBjAS9&dt(@QG#T^i0O-NlZ>oN`}GiPWcIf%V(_2UcWa^mNV}D<bvzdIRIIVI;oOvv)R$#Mk$cug~h|@J}*YfAsV<<s$XZwm)FwKTvB?CPvTwrp}^BxpjW9`3(7I#Q)i6te(Af*t|%&$5ambH}`}0r$zF=#p>ytc~c|)Tv;>FOL~4jB;wDSX9s%r($PaB`S+}2$J-J+esZVPj`T~q&-$R;?6<$Y7UZ*}y4CA;zNS-HAA7dFA9ww^I1{61k1x9<96#N)w)M{)ZLf*MXS^k*j$Ik2mpppa%5Xl}$sMiU;`5o2{6Fn($JK*}XNL1h|7ho>MB|s&#_2gTURfK?C)M}{oBt=jt;xjcJHA;H@xzoC?0A@eT(th^=@*ZW)IW9c+tzR8W-iOb=-G?%mqps!E@}I{;*qHT4_H0%ot^i*zM-y-|8T=uaeB$Jfq4<X9cdHj#Vgy4iqtcwt<7h4%~6qh=B4bo+ROZt^M<YGpx@sQ`gi^`J3phRcmEma>1AVr`&8>Wd&jN_$4|8@YyH`J@}hA3)T6bmKYu;5C{8b#bZSu~pQq2Y`X67<j_6-DwR*v4vm^DHHq7el_pOW5vt@U#i{x`?rLE`vT_W+Fp3|#aB!1$OtR4S%?z%n`qvw3G=lV$eFAm%GmW*4KiP5v?Ok5SI&z+~*{(bfRsQ+75vG@CKd!Kr}d}rIgod*@h>BR#sF9_$8O%Ap3$92CVQqP;Lo*mxiiby`ixi)@{E_R;Tzt6_sdNAnsl82TB<J{{{y<_!-Uj_GFDLwblnsEGVpAYP~x@z&VaQsx&GS+W1A73A*=brlH`fxs}&d1vMVb1<}5j}H?y-&Z}H7}e`wy=lw|FFcyI6eK!FB>BD<UObOoy#|5V)Wd3BO>ur{a>>2tK>!NkDmMVtVsRS<G!}>=VyyDF?y=T_M%9Aj%#T9clQ~~BmTe5>Zz}1t%%g~yfL<aD{o#9>6cwrPwj0#KT`kiueS42%iiN7`JcAXj?elX$4Bx%w8G}U*p8Fbvny@<NAI@%`^4kHICpw#`u$cveo%1VX+5!J@VZF+O^?`lY1-CRk@(XN*>SbA+0C)~`Sov(<dZG2^VLn0(_uYb^ZP*0_M4Cn=aU_1=b4;!=ie5mr(3nYEu2rbV2+KyAb(RPMlY#RuqjgR)vwrm%73si6QieQzqv6||K{%f^X3~fF?u3XbYmp{7CnM~$vJQ6>WDt%BHQnu+UKLMXJVxtSF6`v8`cvyqA%MO@mqHO!&YxoI615*&fjA5Z$4>qq+LCpv+qU8u6928`vP14Q{H<k&|jHr?-!+~n$5NM3wmPbTkizz-4l(UzUfe)7dN%>({n~yeNn%le~XWdC<^PTTEpyk82?Q$pF2JA<0LyCT5Z}8rx(9{+lEN~WgZCh)WA1x&&252{~WwMQtn-k+3`QP+OkMKy|>%(Ke*?Ta6WF_7EfxG4#&^F_Km$S4nLNT#AiM%sg*k~5<l-GJFXs^a91WqPk%M`u5kQB<LLb9<Ntn+&A;`o*^&BhYhvfs4iyU`^;zA{j?Zn)@*?>+>SpVc=$jYGpLKE0mjk9m{I+#K<o(v?v)Qg^OIq3a%I8yUlFg^Cov(a+)>*|x-xSB{W4<kp<g@7^oBykgPK(5U)vgzcn@_tvPS1UPdZgd8Q!Co%Y0J^KWMcH}8@abc{Q3Gsdw(V8-4M}#nPl&;@{89+{QTD!?EU`2=B1Hwc*%=4|5f)diR9DiOPl}mpU#NX^Ovve{GTX0Gm`&5ezEm0w)bzM^M#T7H0P0$>oPHV@tnigbqeX(&b{6Z^exf&PR}W{@r&<mVf}fey}d7*e_9;Y^?2608_zx;)$gTr`rYfQf3@!V*O#mMSL?2Sov!=W>#Bd9uKU-=SN-dC)xW+zs(*d{s(*7oZxr!=`sXhKzvYa1_tik3dHYMjeR1i?U2%Hu--~xf^nVR|IViWEijSTqeq!E1tLNE#vVZ<%XQvoFcTw)Hi2iSzPqB`Vo+5tE?mdB?-TS4T|1Vr~PbNlBRa|>dB>u*(b{<=qzc~}5=M0~{IUGOz^gUMpY~sC{7`^1FN%uzL^W7lzec|1i7(FLD=k7>-&b8wq)q2(~VLf%&j)#(>f7}|$XZoPSfj+zF`iOqh;6P8UJb7)TK4t%6^_Mr#iR53fIndMHisyv$NzC15<KNLe7(eOMB%4pO%#NVH=C$3OiP3XbZ+|JGw`vpgQ(DJIPZ2-+={T!5xA~-B+-b*)(z81{?vCi^+kA3$eDq@C7jM~pAa0y!-Hj8kt8t=rH%^?c$BEY6IPtm~Ct7#o#FwkaiPQBs@%gB6;&nAnyspNH&tHubr|WT2^3$*T16|ECT6gom)AjtXbvOU}eAN73N@xD}x|;vB?&g1AuA2X~?&g1|>-pd7YW{b+p8tJ(HUE2E&HuhWYX0~6tNA}&ZOFbrSMTRqch7yTyXU^v-TS=Lvwi#9_xUZ+e4L&wjOL@?|D9gy{om!|-YZmm{T@;(zAD%0X_bHC#vklF@Oz5|nHW81Ni+L<#MXEA1lRw#a(@tRe|TXgMo)k7{=y*LjC7zU{<vvR;D@Qz?e}e^r@NmOeBaLIy|p{8zqIc9OY5$`wC?)L>AJtP?)uB=y1$&R`^)E}`b+D@x?I&?T2HI|b$@By^;hbSr*_2oQ|r#3T6g}`y7Q;gwSSzh{o{1)AFVt8l!{*%txu`(T;{s%L4DLbtaUdJJH6DpQt5tO>GIL*FRi=vm(%q+OX+@{<;vCTET#K(7J8|5mech*3%%4j%f;90ET`*rmaC6mXSw|KJp9L9+k*J&Jw)s7J;dwkJw)s7J;dqyJw)s7J;dwkJw)s7J;ax*-b0+O-$Q&p>OI8k>OI8k>OI8guiitPuHQovzy6+y^Rw2SpS`a9taaySr)xiJ-TB$;%FkMNe)i=mKRaFf+2^DD>~-a5uPZ<M{FR@buKk?*W78J{UClFEck_(X^*p0>H_!Nd)I3v4XP)u8nrF1`<{4kEnrF1`<{78!dB*E%o^iUKXMB7$&v;$UGrm4*p7HtX?>RqgdOpzA^G@sjJCD-+cOIp?=bh8_^Umq|dFOQfywke>j-=xkM(d-WcfLLk{TO*4(7Jmc$o|=AMcla6x*NAn*W*^}Zru8O)VM9BGj6@E#;w-fxb@|#ajSJVZk?{jt=HAKb-Et6KE4{aURUGR*GG+8pTGW2wd}jO!F4rnYu(M;URU$B*4@1AbUklt-ObxxSM#>k-MsC~Rr9vf^}Ox#QS-Lf)x7O>HE;X;)x7QWQuFr4i9fy=Gyb*i=WVBdxz+v-vMO_5CPptAk-g8=r_=w?k73=v=lr)(u<xMM`>N9Y`zm^=_f@6)?*@0&dp?M#=0mN!`B3X_KGeFK51sDjLpSd^-OYz?o^-mN54G;*!&31JqxI4Ap|6jc54G;*!-RQ`#Q9(A&i_u={@1!+FC6(j6E_~T?!VKT_qw?FTKDnI`*vLYweITgbX|X~yZWbQ&)*R@ezfk_k4pFJN2UAqBf1_xPS@kd>7~|>O84tW9ltPIpHl1Vp119eYp>S*_Xnl>?+;4%-yhIReSc88|Nelk{o{1)AD@r@{-E??U9SHApmgn@Qr{nx?!P}&?H7FC(cgcx?!Nz&47}fl)%PW>yYEZs@2l^N>o2YQ?|Vx3-}jX6zwe=!`o5=h|9uZ#_m|UkfBAg$_dTT->vHw?J*B5rxuw4EDc$u~`lnw5|CV|lDcwJh&`Uj!l<wCxTXr7^bp3o(x?i8}-t%f)e69QEY5Q*iUH_h<b@zLU*VXSST6e#vqz8O!b^Uvg(*5s2PS?K&Dc$`Zlx|%8wb*g1bU$v<ON|qyyKy4FhsO5fy)7cT?|1Z4{i}5Uycjv$=A(Z1)VllK)9dPYPp$jkJ@ZFcUH@*YbpN}p)AjGRN_W58%07W0%zm5fim^pu-R-wYJoJ6APtxge`)$H{c)v}6G5c-8dU(H05Rd&fsoC|GMdG{tHk&S45{@6YPbRLvd_80KlSK5;ev&|s**6l_!}~^pa%1+5g!S;gkpNk*rE}-p5NR*#wQT<UbrJutUQ7J>z|u%Qtk+6<-n%4{59_t?{*WMF)@$MYBtiaay;kz<=*a!(->a4G-;>cxy(gpV=R(f2D{XxCAG&>mPS^VnweI#GdY%1;ZXcu9)&9d$I{Od3&OR=;&(P^^|DoHL=ybjRQ0s30q1V;^L#@00hrV33|4{30|DmtH+JC5ZxBt-R!~VncKL@Uk<j?-YbiF^<MC#A}!|eVWt_|yM|6#h@OA)`h{fBO!p^wl0L$@!{m#g+4ruOf%@!8Mp_91&+?Po5fv!B`NZa=fz7wvStpIPf}KeN}_zvuSdd7b^tZlAL+SM6uky4%m}b+w;a>ux`@FIVkn*1Frz>~y`KS?g{;voDwZ%;}}4Esyw_{mdmz3Rgtpv!6MA<HHNWy4%m3TWR?GNIlul?Dj4D`0QtP`<#9LYCp5=hY!M>j|iV@2<j1YJ|e7#&qoC5IUf-|XA$Tz=Oe;;_<Tg5b3P&)ItLNxoR7$c&P@dQ#+;7`>*4beK|V3(Bf@(4d_>^KnDY@~J$ybQ&|}U=g!S<Gh@f1~M<mw18}&cuBZ}|)=i*3vIR}y2KcFBJqi0_pUKoz=&PRmLK?LR9RQlXR5LV|SiogBM#^=11J16CJb>2$r?!1-P)%hu>>+?`f*XN!}>70A=`KxnJT6gE3d_L;jlh)n2C#Sn}PsNLWjQW9dPbJMc*XeZ5H{~Yneqi5T&NsPpOuk%ojwyY2kJp1R`-k0mSf}fAwOV)QYMt)R)w=V!K7VztR_pFut<RrxwK-2NA0LUY&edw&ovZb_I#;W8cdpi#tIpMG-JPp-x;|H{b$71T`-gM2sdo9ZBK2|SYFjPHkL1t!*>u;}B7X4aZC90>5NU7c==oV+?!oAJTd%8gwQ~O2j_=U9(SDIr<<oxtqer%}Dau%dM3uz&F`*;nBFdk`_#@>LTm63>DZj8)tN-hf^4Vn)i7Sm2g5%)Rj14z79UKYIGnQ*?1~>{n$JkZI=7JO9lZ*{8HW?fUpJ{Bgv0304_*i54#tPt95FTo5im|EiL4>9Ji;Rr`yTgYVOHp^hZt#xA29sWRC&GOxZ#=vYVQI%@#wLLM;o_%DX{%sAcrW}o27U?QVaB@P1Htwoe{`U}9jNON+R&Z03U-EzKYHVP!JcsGpC0&9@M5^M?{eBGyer`ev}HWl7k(vm9tU0uAC3=4f<555)L|5O5&SBAG7-ECK7h6l1UtY-Q|B>YFZfvc;tH@gd?-E{1a^c=`OWc}U{kpGwE=Y(Yyz)`Upm6;6Bd88rcA*L;L?tE_)M@ZT>R9AwhCSdKMz0lf}c-V#y}%{Ab2jkE_LkyZ$P*y?d%S3NLc*Q3f~L1gg3*FJ>V?}ccP75!N&0Zw52cD8h#0Nz7%W&?}iV1fX(1Nsl!EJb9g^|av9hT-k!F10PDgprp~><^Wc5xi{4->ctiTIGrS&QDZeT{6Fe0zem#-83!Va(bd~Up;PLS4l-C-57U3NH)ee3(;Tp8F4ZJ2{X-74DDR?Ga#=uGVK(J!SA16@X6R2wg+Hfju6|4+D1HZR|pH5i%rwYClJPlr-HZ}%NhPS0Ht-<Q>^Qm(ium-#dK5Pb7fw!a%&B3bh3-L)iFb94vZLbTS0B=E^&jYK$FQ6}4foH%Q;*)w{CHV5Bc_lQq0^A5+4o(6m!>1aXVQeM123}-rp|QKbJK@E~?l5*ecnw@EZR`ec5&Q=DdT<GRJ^Utc8T=;r&ER$Lo8h;BE8(}mZv)rBZ-d_su7%$Y-vq9PZ-U<nu7ckR-w3XNZ@{NFf=l5y!q<U|;p^Z<;I;6s##$Nc4qgBsXl$IZ%fKt)-HCG%*akk>*j1#viZlbcCUJU#ZQ(<WO(fk!(hTOB#JL3Q03U8_3hAbhW+>MrP9Lx%d_>ZYt>NGlcpu{Q13SY<C++wf0ZxVYBTj#?3q04@Ow!FH&1kMkoJ+wJe3Y^2q?=BfT&_u+zF;T#NMqATH;pu-xF&IWgYDs$C+$5o5}XF_O`Kj}JGglz4(`9p!O8Gm#JL!}5I)4%1kz0)%`mP>oE~6n_#k8BNjIJ}L%1e!x`F4z2N)Ymy0N4Ye$c$bKX2@H@HzNb#(p*SHTXOHEn~8dI0!xu|C%`8f`7o@k+lNpvZQ&7YZB*sFp;$UU1Qrww~aLK5KrR#6HLP2m!%l#ULuWfxh8Rb0?WZaFt(F)J4qv4u1TDKf#u<cjqM`cF472>YZB)_;IZ%zjlE2|mq{aBu1TDKgU7(%lcgT%c92H6T$4CIf@R@{jBO{~cG3u!YZB)NunhcdV;RzANF!XXNu2M%KNFU}Y3v2ky+E3`xh8SG0sjks!`R<Q_czkK$u)`d5AZkmYsUUcy1$a<4X#O?FTo@5+l?(Sb_=)>ey6c<Tp!0Z;ddG9%k{oo6aE)tt-0QsYr^j}){N`TxaPQAI|sZUE`O)PPbZ%6W5Js61Yt>c5Bwgk3%}dg1!xzb3oka-hwFW~Cj1U#W4S(-Yr=0eHlOSBxhDK(V;i`>fosBR89UBcMfll-Yb0c`Z^jxthwvH3${8yIKZ|ffV<#Is1>S&gQ)5+)od$10xREjW#BeISG2zO_>KQu;tPejHpCrL*@Uq6vq@HI|*JEf$dD<epI^ntr`CsFi_fB{n!p9q{ZLAV_F1!hCstRvNxIT413Eqfs4tZ68*Cu=dWmN=g!5ib7D)6R+tI@V3{7k}?s9R;Q9=ri<IvHM<aCzEZ20Q~U<+sH*f^Fd9zw@cP;DzuO^z|9=^9YMSx=^NIXLt|%)fC>Ha97&d2;Pmbw4)Qg48BLfFQEN3;mt$-Xi0rrQr8-^p$%;nYy}s8bj0_9?cwe4V{Lc`!e`OOW?*Z0ciP+p-i2_AHr0oBC7go~YlH3J?dgL$@V11z;j_l@9)zpW_A|kj@N=niJ+KqJ0ew*y><F)pPtE{az@_~D_)PFpxcK!F>Mqz1eldP&0q;e480B?=4<$SjfAxTmAbdIP><S-FcrbqK1Rp}U5ADAIei7lG)U_r262fh0ODnK9T>LQz-wO_aOaEMkF9ip}rG2ewqwv0jyVI5~;4pZKI(G#xhhK;f+kuzC+f#?OV1IZwe9{9P32#o@TY^2|9jJ3Ba4>u*ZSD*oM7TG7*b06zVJUwCJ`)@d7r$Of-370LkH#+-!^aSwL3zXA(+NvE^6{DAEV%e-CT$hWgHOeegW=N%%NQ7o4+KYr{E<t2bE)ekv|&7L6}$p2{+NRA1t-C!e<tEf!O3uGUtiiNd>r8sv}G7L13rX0Uk=WM_rr&mffL~as6&5n0(>|=842dYFQV-|!Cd%2>O2^n3Li>e3<9UXd*hRf!O?Ije<3~-yc#Zkok!gTuYnifm(lP!gvB4rDN}G6T-vb;p9!vni=S4|R>AAwOYq}V_)@|$2Ik`f!P)Ra>Y59mNBC;mIUYWju=ry!z8Aa}p2m+8;fn~5p^f9f1@Kw4Wd^t$K8-rh1XsYX!iN*VG<*_um;f$>=i!rla20$MZO;V@;ghNJRB#D=I(;z(TnwK}A6@}3AS~r?#%F??;NsVtsJq~8a7nig-w56S-%5GQ;adnlfxlM4A1C}M?OXwWjIgxhVSFk02wcX%27Dk`6!OP<>bsu0&Z7;RXsh6j@Q3jGV)z4urGM_jmx2$%=g`Il;70gL+Oizn3SUZ{SAdVgufd0D@ILsp)L|jG8Gao;Sp_};pH15f!S(P()OiW`Fnk$(u^4;^J{O-9fa~D*nitjkjQz#fW@GmlyW7}P#{O#T8DlRP%NYBctS@D~E-$y{W%NaZ&l`Kr*guSYBkNFOPaAvI*ptS-HTJc96OgsON%MojKa4Fge37vtW7inF7QVpP)$rBER>H40widq1*c$k9W7omc#^%B2lW!5_EQGHxwhX@5*i!gf$}1wjRq$(xS46rc@HNz_h%)EHmr|!9>b?TLkhTTwP1<j-@-0@rFUogY`NlXVX}=xHH^i1n`<+p~J3gDR-*V)ej(i6?k8eT0B<wdG`NlJrZ$nok?V9`Ngk5*b+FaJ^yAyWZBI_#oleJa_xU4J6!DWqfGF;X(RpGKmaz8E0y5%IetnZTWvgDhfobqs4&zu04HB}{eRmw|{->L8l#7mH_BD@N9N+gc1Ars_R8GbV5B`CiP{Qjiufid@-u^q-9GPWIj5WXG04SWFp0BN_8_V31C0$&aB!-NGt4qX#`1$;BaKPD{rMd+H~Zt!4;e?eIAbNDV}Zy0+Sd_BZJBP{r7=$hb8@U;;Cl(66@p=+<ve!)E<{t02h_u+fsd%+LjvyC+}mT#=Su{>i9z*+DH@P=SMJfE};NqeTT#$Zl}A4gd5#LzXtreN(5KasHDN$}e6bHJ0~b&Q>2>|F3vcnh!zSS!R&B`jDubgdTc5v&p7l?e+T53d2Q4pxMpWvl}2u0WfG?=$vc(vC;L!|<z(%`^4{_$YjVvAJBI%QfMT8{5kDtz26`nn$_*DAyjRAMdB%1RsFUf=eIDy(Z(}K`<YlPn-uSNAjElZh_B%7m&Y{_Xt=3FCfk%w86FS3F;_(zOlz>=VP>C9`%v>6{1VLhrvR4A#sG)P1<o$1w0vEFKNe0UGN-u)ubIa^}sstDx|Fno&rCcey#*ogx93+&jzc*Pe|HvP!l{0UWv3PfED0!56D<=2A%_N25+7`I=<_G&Ed_HNAC$4yD~-_g4N*-;c`#QxU5f|>Z6?ny0QGEnWLXFwkBc6xnM=`DY%&M3gDCQ3Z$2N;5hhduCIYVW9(^T*Mn=}*TdI<tKnyd{9Os3)ub<7KUblzgg0S)GzaIwWjr^=ufhum&n8|YunD|5X`6v_;d%J30Bj7G`pbOr40uZNXj^4Gtp!hni*GCA*UF?{gMTFL)8NT)@u&FYL~t$q?WBGFd<A|Ee=BL9J#T{t;a?{0bLcJb4ft22{Sy2PzCUT78ztZe@B>LZ$L$CA!aqvd`R)L?4_-prkH8P%yOT$sp9iUraCx@LGi)2U7rqTH?+7xV?x2hvX#2pu@ZXI6YOGcn`y3Sf0Q{A@d_bHJ!QbE?!VhD@YnQPo>4pDp_<xPnDP!@RGM0-8uLahI?+^K}1RorrZ(P59h3|#SbN>;1BDfVUev>)#CGcVR{lv?HJK?)XyBmBI{t&)<7<>sX^_TYvY2PP|hu;|+=g?N+9}|9`c(q7ZhxYzX+W&%|!w=)jkHK@`ryD!X*co6o_&dhlCHyX$<L?oEkMxcoB7BIv9Dk4e-Xr}xTt7sfhtPz7WbU&PV?QS?{wH~qe@s~Lm*i3Y31Pt_$)o%u!XJ^J@Cv5g#~M2hJO=(B(n(nGxH3oi5yCFL<3AG?l)NgC=2-GOmTSWInmW8<Y#+EM#P`zXy|mHseT4VXM#uLM-a{KdA<akR_Yv2Ge`f4cV?QM={+K+<KPN2sujEnw1!2K|Cy(;a2!BR?!poaBmNixmECc_MbP^UUSLP`HH({6F@t+6_N?zqjQ<nV7a!vRFQ-{ABdllRt;s<E+0ov&JtAt;rjgIdpyq`9HL7LCV?=!9mm*<r{tK_{vo?r5w<eppdY?Aj2d3MQrn>?rFStIYk?%5*m*76*Yc|zt0S(nJXA@6T)zK}UV)<ZI9$UB+L4|0!x8oH-tEhP7Ezuw6*Rm%QP|D@K@KUsGtBLBdaP8r=c9Zose<mER}_v>9gSnHNC|H%iy{_=$`@&5p+Bc?9'

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
