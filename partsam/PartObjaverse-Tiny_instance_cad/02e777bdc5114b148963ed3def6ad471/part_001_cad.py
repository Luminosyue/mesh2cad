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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/02e777bdc5114b148963ed3def6ad471/part_001.stl', 'relative_path': '02e777bdc5114b148963ed3def6ad471/part_001.stl', 'source_sha256': 'a4b8794d947380ee0365c489fe0fd52e0bf024940ad45037e23a4e1f2b42752a', 'input_faces': 1024, 'input_vertices': 549, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06572520732879639, -0.14439541101455688, -0.1477387547492981], [0.07115300744771957, -0.10792842507362366, 0.11826230585575104]]}
GEOMETRY_BASE85 = 'c$}r31yoe)`|tOlU?74DChAxRyAF1Z&B5*l>@MtrvAerRL2N}uvA_Yly9@h>-F^Je^M1eEnYruUweGt2{MWO-pZW66^FI6C?|yfU|6k*JDN=fC_%Dyv?e^^TU;oxLiFBH`HneN#;GUhk4l3SnzzBoprF{8M*ZB=wG-%w$pbgbV`E}_!sB@@aMWbKkZsq-o8vVNU4;>uZv0rfi&@NrYuhX&5psqH5P>+rSy4pS$EaP9HsPXSYMU7*O|BwHrl^TLBM<23@x&MfGQPYNVG3v8h0{kuRheWMO<8~=6w@3Nfl1Fjs^Z0qYmHs;s?GwwW_96Z*J5|1*A@IBOR_%>FHmmmLg`w~ljYq%lvZ(y#g!=G5A3*-vl~7O7GU&IZkIHXyJF7lhhvq<gFC+3Vey!ST=~AM7Y|nV;;2lb*p4_h5*I%jpkawlf?(jk7Ylij6lWM7|Un{f^{-qLD<p)pPqrN|6A@YQzN1de(qW+O%m2ZtarrKL)bw>R!TA=;nbJ*S+2V>ReBlVEKMIPl_U7KNhDwjh0YL!q=&2Fk5bN&qQm#$HMNWL6uyUfRqZ&P`q-l9&Aukbteg`e%SYHwbCS@o+Oh~BC`PmNdYEt#T`H>@K3cLP=Xr1Xoiy-lZVQS}Aq!*)IKQSG!-dAH#2%~X3+qX`)QF+VmdKVA6*<&W|~zfJEeUz_(>`62Dzqy5h)_+G`;{x!M;ppNii$TO#c>NjL#;9m84)d2Xt)?&MU7sB`$tHb}R3C6kePmJ&NBJdMD5|w{#F!pbe0h^RRx-{lh&Jg4;o4iqdjy$C5G%t9E@p<m1e9do#%AXYU2;)<E;0ER2c2(`I#R4%dQHR%KJcnZ*E(pW+x~@>Z$u)<n#~k<w{+WgFV>hTg#$B9m`2v-1y;M()gDLbBwx?ZI<S%<m`P%0(80VC3XkVZzwm0}Vw)e)*D5du<q8`6%m?z~D;lEy?#=-2q1oNguYUNw~yJDWy^2fZb_hy~?`<%2Yzwuraj-!BUk*dFkc`*-fepAQ0Rx(2Q*4+azKDoVAesiTm5$f~vtID@rE{<_9#Vg-5FO$k+&h`w)mo*0MU#`IX>Ftg6WcdW;YfV0(eLH{5&m%pMr+hN{b^C&OQlbg+tZt6|yLtrb?BlL{bB9Wp=V8;ZZj?_6f6{c!!z-a&M~<&m?cQHT{+Wl+KGlx3s6RV=Ykkxi>xTAkEbw>V!|}fI+Zy$GB<rs-1>=yjt@2IVd*C?QvJmYHv{t?r@e=#}Mhi7QT0(&G%~__Y_S$4$jN9Zd7L~u33&#0qD$Iw+pOmlFE(!mQhWQZJJ))XuwTze#om=fwpHEGNzdH-&!~RVB<+FAB66I@^Qmc7o**;YHn(GC$f07UD?WZYwRr>;$(7wJu&KFty56EZJg;!`FmPsAgT8$0pxAaHln`#w8zcHm$9@F5j%D1LjtNf$__xGai%#q698Hx4<qEY9vAmy94WyScM>8J9Wf_p1pOFJItyBq^!m7jk&{MeGnGw-6R(|m3|{0?2PPDX^ow<N+pHVW%@ff$v?8g&`{whF^I)G2w;$#2-}plUzwD#j=99`c+Rr+n-8IMna?0^3zK8|JN+SM_Th?y^p4sXUk`b2p*iA8D1ZjUNF&#WifNHH-31<#3+T_GiKNdRBF6Z+(*=<GHVm^38eQsQS&-x9m~vR`-B^ZX4!p-<sI2RA%IfT&c!W%XJw3nHi|F^$@IM9>Y`~)AwlPS(SW1<uQK4ejl?Bb^bn#<Go23>Zz1EN@>aC%1>(Lp~lC2KO_9=L$H3X55o9NEv|g+dLhiKG%ry9OMkSliR%Yb)?ihqxqlV356P;=KdGy`>Q~F&M){_SI3JlquI*O&E4D-X24M+~<6|B-K>5}<oJaI=)_rZJhZ;{~)32&u)03g_J-VrWO=<S3`Zc!^sMF&&ws-JOjKg1}P|xH#nE%ZS$Eo(4#&f$W;kaH?4E227h<XlZKs_nLvAru|(0<Q4%+KUEYP-yFd(eK_7ql-Lig{J^KI**u4g2xkR@Gkn`V)En%Z&5Fp>vp5ZBwkralA(DU+dmVn1}y)C||2!z&v?BRMl^t?5BKdlUS^`Lpo!ei<CzDS<h7-;|6z(&+@it-`_RSaXx7EC&Mpq#5})RPUSIen~8e7N~!jij9ajOGb})R?>OiAV~Iz<mDZu2;X$fS(}|17<6Z&%KAnaAoB1o+Pdcl%D=EVnY}Zn4gZlfk!nkhnE`xcPkV*O48ebgmA<Z#v$MY-Slym~~?eo(Zm1kZJ<y&ubz<hf&TJ1;eQvmX>`wQ2Her~9<N)Y^On=x)nyWn^U>x6zMuEq7z?Es9=#6f89cNOc{kZ|NF6b8S^3LF>t$D-ewiSP%n!~QKh6XTga3H3i~mFRf<Y9C*t{*(R~|5~>&AIf}iYH!`yCf3O>m>c6zd_#<*Z~id_*JEuSV4TNi+o<~4R#nxhJ@|t4Ip8nlo7a@X`F-vu950LO!;gB6c~Y(|{Pu0&Ti;>*$&(-RP3xk3YmM_bFKp-=gX3i<`mK`>^SN2Rc-1arGV*-cs>a9C@D#Q;ce+i=zvGGV+}a=K!N*yZZ(6qi^RPj6jI(PF<!kFkVE+7AiT&kX6#n`?80S_QFb|tmhu`1<j_bvTVx0U-p{m~yw|!V2zSKiK{|>->4lRcBY=Hr2--_4yReEEb(}ttHmZ*G72P^y{W6?fMSsX7l%b?%4GnH>O49E3hi8mPM40Dj@@MqLB!X0_aM_?RsHbXtZ!_~N14{S#JCu?xso~ybVXD!!G^jqOR=E-4q^jq&5{AQok_?sGi!}z>Og8$MV^QT)1?5}Y5&B{-=5Bp{O2AscKyp?Zmnh)p4=-jBYWO?PAmgdIs*bMVmn_pG=)`tzSAN~8mk1?VB*-Tg`m&D@yex(NT|0sa@mS!}LgW(M}JI)hRuJ>rav=Q>0Xpi-|&J<kl?{9*Bc|Bls#X6_mZU(<ZJNQ+D;Qwra?ag@==aJDRkte7<`b~8Q>wN!?XrIst?f=Gov^C&wjN5}QXrDL~bw}*P`8{eN`VAe9^HIfc<kx+_Qt-#DfFC#-{%BnHTF$S5-#g5yPVM3kjQ8tF=(k>1oF9+W#(mYm+3+I^Vmz;>bM~7*$2=T19sZ9E$bVrH#<TJg^y|ABegJ&)avW#Y%3G1=;Vg{L`0DUGY)Ae5Cu9CkOocqw-N<u)f!dFMu9uQxk!QvzwA*kH^Rs3=+8f^Cx~P6_tQ%dd$e*)1>MXby{Z2?k`=&#2y%!B%OMM#t9PCGHx6_!vy)Gh;aS+<i<UHAO746+pV!O^%!tvEO3BGA1#{a)iv>*7;X?wMECz0>+zi2<L9O^8FbyWM9jP@UXp#6lc$W!(W{GcVMFK#l%W7r4yyBA_U_-;r0eP5jXq;%~t4&Q&^xG1Bcj-|(Tsn3T}Z&BmQ^~yTyFxH=%8I*5LjKw?|cLD2g=S=WB;r=(N%VXr3;DbCROt_vj1|ZL|Z19sNW1d_;jrt23;dlOk^Xz~+7|&k$k-yz~tXJ*_R37uRzu@0(f#Y<*S!|a_3FJ965!+?Tk9k|X6nxLRm~XlBqWz8v$~P@~g>kO1KEct~wwloX?PDk3?9mD5ueI&5etMhW58HwB-Ib;2m%cV?4*aA!$kU=0`hB$#bsn;yo}qQHT|+iue5wsYp1py{e+KoL?;M8Tz6J7hMIK{7LyYH`R`4&?$NpM%AN|I+Lp=|JalWYh4%f-|J0O4i=GflTEs>wTruks~FIf!Nu{FBDpFRcWyRVb6&UfmD`uliezAZeCdDwFp^4G3`aR`sVcDxLSAHEFj{coZE9W#)B?O=?{%m%m)T)Z6H)qg3zza=}`-&hTQ#zCj!UH8p(`eK}4-*xh}t_^U%R>VuqH`BK@sDDKq@2BRX{_K%x|J=ptI!db)h5Ti3|6+XD1MPMH_adAh-IH;=jNasQ99i04LHqFs;Jf$0`jd$DUyF=GzoQRe|IM%A<eMhrd0I$o%q!j3@ApGaV7)iF9YLPJQn)VqnF;m#9YgyJXK?(kjz#`}6R1DF8tR`g0oTLnuA=>A<TV$$fx2ejh3|s>s+D}0=;)hn;<;Q>NOyei;sdmQn-=rIBXy#quhspH^Z1>3-1jYdjXdR2A<yD-$dm00+DGI3XpF=B`QyK>isuzoYhpcV_XFD%TpRPvZx_xlqkf_NkqhvfZbJPlexrTbv)Et3XOKV6uvN8xatYhtdz_Q6k3)#r6XW^Y75)MrtTP(!hs@*BE8koZ*8`@BWz>01i|~Tq{*u$WZT>5p@=cHSVf%AGK%G-^qaL1rt>2!)-<St^w$8<UQ|C#@|Dpi==7p_}^WR#uFzPIf_0bq^RQui3uQ=K_D1!YvI%1cT-vj$mpNFQ56}CDZM+5z^eS2!6&Zu!{ziJiyQH_y@*Nw)jlM@_$YmS2$x2QmD_uZCgKM3oxsqgYcM_&sYi*b8=8-M?=HT=>^_`KPQ{bK5X@yzFkc@-3bJYze;A0CAHxw-<rx3)9-9X9~ahxet%x^cKG@=thz@!@%2_szdvApbMYpOZu3?>djXwQr-n`zZLYu#T7u`e5A~JP+fLsR`OYe}ekyn<jW;-FVm%`+va#_^YmA-X>SWeAvARzRzaV;~J;-qxs7+)c+9AUCr5_BmcqmsE7A=Ney<Qu4>V!=iNta@0)2(zPbMayr<aB>zT1J$iIIVj_aQb@!TMBFMQ8~SclJNSL11Zv>$m4zPNtKum;Cz?F6(B-jC-7feEO0@=^G_U$gq$!*jy4=a8q?Nu00a@IJv*<O15?eu(+G<^s02{v~Wz8;pZ#!5h>+>l*xYO|hM>vv6N|{uah_`%$O+V%;~dsD^P~GY0(*dV+qlM_^v{i$TA;pToa~=kVsAZQx&ffjs(pRd+V(%JLRIpLd1S<@LYrhu_9^=`<7SZ}Sm;{=s-&oyUmvaO7wBUs~h)4eR52VA)q}*EHORTH5=f-vi${PZBZyt7ag7qWd=G8;_wLKCd>X@KXMt_3FeU^piiM@~zoDF<-abbn^A%(Nu%$O}EU*|NDvR*HXO-_QU$@@Y{Sqo&yQUbHW$-kJUuKTcfaE%`BvR^L|gPKVb#&yl86?wEsQ8Y5rT!6@!2JJM!lmf_`Hv!yk$JJ<Ha$>NvH2G9iDzjCd}zx(?=Tx!Uk~onQ&Zdp0d+bND`m(4WNx*H=|rV!I08!2NrE+>cs=TBF~E-0usv@qRN1d1j4sx}Mh_hG0A!r9itSGtp12?r0ye2G7-pl*Ik=zXOrKdk4Npn~(OrN1`76{5btO@|`my&&potHv!kDy04Xt$Ng`$x47PTGY<9eJZ`zo=K!J8(f(dd_<T-c-ZdNfpPR9sWX5%@>C=4fUl-Kpx-!wx*Y9i09{-?y=0#|Ki0_>_PqcDN(C_QT=yxxk`<jQZK%QxzG0tzt;X0qbz8}rqGvhhi(pB)YPr&{P*^hC!y%zoE$9;r#v8R)7ZuTDI)A|+i|A>Tt{-)FY<{!V$RKEYk{x^3yi26^@!g+HquDi?=<KdStjs11^4*b-|k*Dqt<at^K{q#NyKYkYc5%YL`eG%jE;t}c|aunlT;uidhUomcV6V!aOHok*A^YNb4v?3dyC)`6l5g&0qxu^ry|I3dtKK{*6f9{+(UWUCv`|wv7fBk-B-v{`6aow+t?1|@Hm47<*t8IB2=jdyV{>6RDrxuupt6jFMzw6JvQ}o7m8PX`<d>iYmex0e+^nhQWF^=nZ_3*s0izj^j`6rJ@(=i|Ao4SPYykK$iwa;tuUhgpOORWFoLOpzsU_FleK2t9v@_+e>>y2kOaehf(1bzp+zcwHGh4WE~V(54CSJd+z$FJ771lsH8<;TVGy}5tG_vP~+-Y;lAl~E7xL;u{T&^OILfbBYx-Ko9y7VCyK8uumUy>-z3RWi<lFOMWT`Mhok8Iud`^8}&agP0E?AFiT(jS$os+#U031FxGVbV2*RxV}kBH5bpr3-(9*9euF9C2+rG4HyXjVgl|9<}`8gwYj};ejJYLIP>OVs54{->Y0Y)&gv0{JQ)VyJwocLcpmj(2K*Mo_<M<!XzxE4`3GOZ_;_E&Jg0B&T^ZvL%jbeE=A(W51LV0?)!DB-6x$X34ddTF5_PuZ_0Y6<w6DGk`R4?n{zC6?UU(V@|C<H%B(25%)qVH7SeHtyz<dihf^p{cXNX}w#-F~vE``MKxy$J@X#e~aj%z+&HN8BCI&<;&Lf?H79DVc5>A0>~i2FgU_+@NwUjE)@umR)N@G9EB#PO9h)C1#8-*jM<)A`*r=O+A7=~2h~w!5AD_YaXLjL+eA+(!PA&r#2aYVa@Jg<qj0p6C0n!1dCiWcd31S}TmFIrb&|C85~PUq_vM(>T;^a^e2U_5tHIumS4X)dc6kil30j+!O0t0le2W-}{a6IfVQ0keuxko&10em?v=yuphl#qE()&7Hn5a)MYWIQ2w9$>%IXvo=T=f`^$kC|0gBYx*by86@IH*=(pWijBBS<%GbUY!F7A}A8LJ08kZ*8ao$=AM&Wz&(;|;w6z0z*??fj*MJU?0!uiMg$;-+Ab6o5G!~Qs4n()3nb0+u`a6Z$f2jY5<zBRrr=1Is1%(oHQ(0<Gn)R*=+&dd9AqW)WaZv6WU{$8vA+VlR`I2*s`()t%d`#Et~Pa1c_{t7RQ_Jt>6{YkgN*)I}<adR!I=6TZWBG@l{eiCve2aYF8QMCUy7UPiN8K0|^K)-o;UC!smfBdjSoUi#F!Q%2a@)#E)PZ)m}lgS@`M|aGR8{M3IZ62O4S*Q4+-+X1zKHqU{mp|^ajJ3+ae=`^JHXPSe#@MRxqjU3jfPtv<cs2O_is3l=u?2b3)WSIY`i1@aW2rjsEP(;=`JO1r_q4hW59u9<I&<RvpuV1%?lplQ@fQ2#>SL@A^vyHw!T&D=``5FD)BM!O$7*VgeiK$<J{V_V-gaz@_L<jV9#(me{s*>0`-~%;-V2z<wTJ&t9?YLMRnYIQVANSX8RL03C+|DEqW$tn^joSj^3?5#_B#$?oSTMYzqIOwdidN}Ym4U!N!@!Rk8e-RD_=Z6GjHsVJba#JO@)3!P7Q>gV8uAJ`H6h#hT=G?dmQ%*g?Qff9fp1{CL#ZCygxEl8G-hN%440;-$OMRiTqQ4V_k~vg8V_FkSBG3^Yx7GyG3GqZ<NM5xjNiwebdI`d9d-pc;uh{82u&&sr|0GOoGqfAz1rP#W-Y~j665D;XO#Ff@<Bf)SQO)+ue8`$Mvms@JzH{bPoOUJ&tAJY^UwD9>eo^<MsK-6Jx}CXF~&Zyjz|vK%S|m@m#JzapfBWmvh}~jPLirbFV+X{{pnPbir{weKq>6;e~!L_e*f}wN5Xw-gcOR`MKNze?tJ~;hNK^=WZnO@O`L0Z~yrE`>a5`hcV^eh&=P(U>vUDzC0;pEBvmw4mA4BMEil;P=DG+sNbt1#&hg;j?X)+|F`kJOPd#sdHd))@=O|p<8JK^r}L4yb84&uy3gO^Y1uL$|K%9unb#3@)b_=3k#aBEU-^J}cpv8-lg~c1Kg@Z#x*poMjDtU}A?kUK=iAm{hu~XsVY`yes4MvxkC)VZU%b}IH#a?w=ktZ1tMg`v`$>!g-!oc<?811~KkMXMJ#n96>~IeG&m+Hnzns+fJnC7A=YFOOcu%DJW|soUQxne#OxrK>JjLG!R>pH>%b_dqJ>4)aEqQ%+;VOOnp4^-ii2I{=*Wp*ia~SKlqcKkY#*WDUjn9V-H#wfXF3Q{7*)NUfHl}uo=r`|e_^*m!drvRM_nO_q`0)3NCi6+m=Lrwse@lVil|7k^-`gyF2){;W)H7>3@*jJG{QRAX#o9_;H(IVe#W)wo?;g!ZvCbQ_zJNau?+f(z)Vgo_g!f{Wj2e!kf-li;<}BDxmy0?1rhorNJ!hhkfBJjm=ksvO%F>BWzPSw6x0&}a-kU!nf4mp=%jZ&f4|VVp^1I_cPJdpZ``S*fS8*pWKhJzd{;>W|$B{YLPx#wIvChBRi99=9cc}b)E^3|QmFVc}zi%=3`-J?7ZqDsD{)^-6aw_GUm*Ko=NsH&%Nwq!E-Z}{T{aaSGUyK=wq5S}V<Ud*dprfz-(*o=K({}K8mqYs|eR01N8?44BX+$mL_u7T=sXhX~YiiUKc}ir!`e67D|3iD^S$h=gdH5=4Kd?RC8+QDK>)}kn@JnMIv_?Hv>y`2TXyosO`w?y2L~K{U0@O1R_aT;FdG|Q_))yHuJ`W=CTxI`q<o7v?{XRQF&GV4hgUBED7|#>ZR8-IXLfRci{?t=3e~KjF_knLNpnccVScm&$#r*m70RF3BTrb^SrrKNfc<xmF-U!EaLWB3XPHUST{;np-Kim`j`jk_?X;XUCf2aSxYK@)#)zH-Xu8++n<yOpAt>&$D>*(-LhQyTrbp7A|lcApe|5yKHs8q?){{MgfW+?4ggQlgn#Uh5VA9b|`_9Gv(#cb+$>T2?M@+j&;@+k61>OAsDvY8>gfSN>JK)yz`4U^()<f;Z}Jh>`)9yNmtcpmvOH9J{C_$xIBSyUrSOkrEmjt2X8J2JOuE`z<VT&zX(jApOx3~Lu%s@b<?DYw;3olIRyo=l#}5MD(+LtaHbNtM1&^0Tlz>*+{#Cs(0PAy*;SwM9$n2I>^@6pqUVs*KeJ>L&UUo0y{|xdnATxdpivbs)JGxd^p7xd=HsH6=Ma`H6-Q-lidh4`>MCdm2L6pWmxa_9u^~4kV8zAEeGFA0$7cZX$2uSUjU<Ba6C_C4>)B4>;sJz&=I0In>aNHA?-WY5BPuS+pE^r7iB;;vzMp3-}`W7uA<6A)JYxk(`N~nVN^3nVf~1i+t0T=Zh`8U7+H5^KZGxqFKq_<kZwR25@TfRReS_`6}7M5bjL<huoQ*kNQaii{G2y6P@FbXO2UD;qBDk<n81h4B-OQ8sq}xR~j@QIUj3y#SmW4wRAn#(e?BXGCpzb6_su9<F>3d*w<v?MbtM2`x-9%A63TmKYkX@$#Kp_&PmQo%|p&h&QCRx^ON&YeaZRAxv3e+xye3MnTtOBEPTrr<EhK2_sRD;kA)l9;%{3Fpmrzs;NPaP?KJ+aJ9z-L0r`b(JfCa!{g~e&x9Beonx8Bod|pEcXXf8~kVPeDX0{XEN)>-AL)gL)mRbUB(b5*psqM+l$sMTO$sNdps6)tu$P*dD6KpYwI-EL$Je=H*+MV2w+=tqp+=twS+LHXh7N<C#r?^eR%Wb;Y7H6ps$Y;qPsM1z=jxDCzVn0K84Rsv(EWfv$x`w=lZI)BR$jix#Ip$K^66z`PDb}%sx|qC}-(5l-OI|{@P^UQT(<$7~qO&yneiuGZU8&jUlJGBTf@Ys@!ZII4({OG|q~W|4ZR9Y|8*%QhBroGJC0dl)h+LF>L4&3tUtnL$sM7Z`hVV4%O7b-F2<j~I2=V~x6!HLaSL#@DS8@n7j2y;&8Nv|mMx9FTMh>OUA%~K~8N#y}!t1H~$)c|uSmx7r>Id?Es=kH`%X<HvZ3=K6_uzS;zl}TEq8+s{xgEI)wGO!nxdF8%xdFKmwKlmCxec{Gxed7owKcg1c^I`9c^G**bqskrc`bD=c`f-rhVW@ytfS7L&Lz(v52cPF4<!dtdy#|4O{uNPP09aI>yrbhHK_H;^*Jsz7{b-5HObY<wWxK-wa5*rjmZtk!PJiAV6uL{BRrnkpFEoyPVG+?ZKv7is<1wXg}YIkX!bcT971iN*^d$7uGB`F{rD0dKy9Phk4NDV)E=7s_!XW;9j4ijcj0B!>6(3g5WYZNtJ&8RVOeiP|I_U2kMMY|QNmrQr^yn+<qY<@B`hJFmb!v0A$*VCBF%oCFRWkx3+wj<!t*tpA4Mln7m*h+*93;}MCv-S=nTz%&J`X+9je*S%fcO~L7M$MF5H~jRI{J=g#)SokoCD9NNq+AB<ts6(azLn<j&-tw&-h%wze2Z?L-zGOdd!ct>J!CbTV}?*-Y(C9Zc>`Zbj`xZbhy~ZA-34uFDW^LG4TK%i3E|n~|GwELt!Em_xJ%S+u%C{_5;gw3b5+wOFHQLx-9ha+^eh9kwx8vp>5K9!VWVj<v;hTkK&7?_daTutg+w6LmXz6L}Xkmb{B>rJf*L$(N{i$d|}Zsc*?o$u0(ju!l`^8lbLJ@m={@_$9x0hy0R!i+X~5i+qe4OOEAO2>-T)!In4KrZ;VI+!nVP!si&m@f^2!em|bRKDNi1^Eh)IW87pdqR9@mCA0Qq)}U{Tf!ivY#bDp|EF7Dh<Py|8<Pu~PwG`Pz4qym3VF=e@2v=qZ8>xB7Msfyf7IGHWnt>`~nt_^$zC<SGs7x(H%|tFl&c+bdsFF+LXW?hucgbXZ|2?DLCcD|%zqaWYhVWzV)5mQ0n7+Q>U-P@q$QpCFv41z#C%nxTGi(t<T}2*ci!ruXPK_e3v&9ZuOrp+q;Jy4T8tK4^{45$v9>sj&4B_?ED6;4!@;d4c>Lv0H@?L79L!a{bH2F09jwK(p#Wm`6>S^+6eph(7Et=V4Dnqz0wK%yiIgpy397rxkeWQVkk-e$+$r8dTsF%qS!r$m!C4VFTU<ju(Kp&AMgng-B$r8d94G3W$o4%*spo)KkA$*wnh<up5k9w7Sm9_3;2=ArdC+{UEQs0mh$=9hecEU&LeWZ&2ky@NAA)J+7GjdjP1?q5e1#$<5@KT2GF6vbBF7jc9@J4E1@<#FmY9M(6xhJ(4xhJ_H)tlUqT#1^3T!~zeD)XQqKMUuj{vb;T|7Ac3m!-=5D9aG8P4y+$CI?X~l7q-27{aZoKIGQqG6wtHD#OphUN(J4y+RfL3Pbo1^#=J6c_;NS`7r0%PKNMi>R$3@@)l|$c?)?r^*ULfbGsQ)Y%3b!@ZAW9{1NP5bfZH(8(F((jKj9Xa9c%>IBdJ{JBILG4c8%}R_YPWe%&IxiyEWZuXBVqQ8#M#>muPuY6Llg+ZM?Xmg}h<)M#oHIf~;FO+88$jUz{s^=mfac<M!RJoy~;U(J5qBK(+|$^d>${zA=du%91=_4Au(d1`KQd2)M(a5ZWway4=es`Q<MpM`(2o{Qw4<cHKaavaCvA@w6!RMw-1{4D&FTESq?S%H04;M%0u(1A6!r;em{Ad4;~%Q<eJ0p~Z-)#Rh(Sn5QB{ro5#NgYIvB+sUHBF`pIqP8RJ=j?FmB=RJ-38ywT*slSEM=^xQP+O75kjGJj$>Yc~sQt(@$g8MfWbwE0d!iBKG1Mq(1UZ83q8P%Ls4?VAWGi(Q*-G9@4I^(QFEn8N6b+(=8SHDUaBXTogMCdFE=vtI*w=93zo@MY_BCHPFSRkbG53Lfju0+L?PRc@Q-mu~2N~?=AmN78i3a;QOSmU>wZVRl6P`fbXRx0Wh2@-in0k)7k1TqP{LmK3w)mI&k^C>)JfvPHU+2DgNKJOg@t)uRNH)0Gj&~R6JAM}b9siz8PG+um)VE|&SKD`fP}7prGOutd=KkUE9pRa_=xU1<)c)iZ<Tcb#vS=Uj8uDUWOs0lV`;bG(`u&k`9crk-eh($wgxcR=zt0lZ@4tji)UIS1hbP<~(bwdAwzx}A^cDFE|8|M`ge=E}90P}_TgZpV=cz}?SE%<G=h@GBwz*5aLB30VMSbZ|(<|03`%Y^A$!&N|e$6&NsV~W*zsWzzl0!6|3s@o@=Y*&iSu{O4Ejbm{ot%nnpnfxe4P=?WqK^&s`7Ep-6Qbv+kICoA`gN@E9qKpo9r6dN^!<UKh22<Bda@hYgX%^0AbT=|(@@iq(~v)L%w+67F@zsbUy>h?Pf~A?Pm-glN669SS=24$S>zE^eLdFamOl4{kCTrZ>}$BNzRn-#96rwW!ozIQ+!k}GL&<Z=d#DS@d&p;~yUAzBkEo}}kI0{?x5=N$DO{k>$r8dTsV~T)Nn{D(@ANK^zmuQZ;w*JP^#XZ6d5JBCP<K)<kS{RrPKIy-^#wVBe1ai-jQX5>j2uV3O*T_EQ*V=RbBs1Kgr`$?lc$phQx}j2lbce9lADrCQ=5}Zlf4+iWvIgp_WK}VxlbBFokbmHu+LB7XzE;peLf4Hr0y};=fCg+>KTLmcoF_YePpm7U&3<yiGDWNk4IroY6^$rHwBOB6r3v_RGA<8@h<E}eQL0;55gZD=8(Rg2+MkNn7WI4)?mNy7G6r-Z?NB|3y-8OA&(@tH`wQ*e$6jjo?6dfzb_EhpWO+|^SsK`5NbVx{d_7snL30lx|1xLK%PuqOg%wfOxDli!Yio94EAdP;hEGpvOd>mQrnVelJ#@5XbEatgZ){nu>P#NumR7oMKc=g&$NZ*Ik)I%&Hmi`vu1xb{+aiq@2H*z=x4Ggzgv<jxk@sG>r)Gp>yvviglkeg$og~kn$))Bwj7I^3^Q|xZYGOPcgR1TeToits9`W`6m9BIb5m}UXla9e8--;IMD=GI?zV8#<Oi%!S8^J1DqEDWh5UcM&&Lq<vqceVIqKi!YE%>TZ?cJ8nOcHenOu<}T%I9Zj3Jzdnva}^?890`vrzMq^Rd1x4B;FO+mM4HoXZwDsfDRU$c4#espZJ}HkV}xS78WOrJBelZgW*?MRG-Mb5(}0KeZUypInF`oST}5oSU49>O;;%PT??KDX6aG6l4QKSfjdW_Wy)k7{VzT!l|k5<kVyjTV$YSq`H$clD(*D$X?{M)KuhD+?Q#oIml_rUesI;d2+EIeIM)n=5(k_G%GbHIV(9owJ<q9xfHc5S+ok-Xp5q@@TC?c`;xOUg#WTd0cuHxaA|5ma%plIhHwRHQE~-xC5CWus*zlroYxkasoqp0*_-T1^(A|f(^0dL(~;9NgtJrsBJ10kogu8xTVZ`}3;R<`YWDdrT$NgyT$*E1m0E#Zf!nViQ<b=HDslVu<Fq*US8;BCDMnuIXMK$H{Vpu?!h@Qcnpv~YdEt~)Z_R#;2)j@{HT!WStWncx_Wy(p)byJD*c8@}S>a67?BwhmQ{l$-3@+X&{!jmtC-(p3Jfu1O51{<7-*o<G502j~Yuh=0{t-mudai1{aIyWL{LtW?{Axk_AMB0*pa'

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
