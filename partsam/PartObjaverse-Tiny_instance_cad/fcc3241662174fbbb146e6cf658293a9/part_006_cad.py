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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_006.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_006.stl', 'source_sha256': '690144aab70caf28106d136364661d8aaf13f901a567684baaa5840e8aace0a9', 'input_faces': 994, 'input_vertices': 578, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14357247948646545, -0.18023574352264404, -0.23087012767791748], [-0.08816033601760864, -0.021155618131160736, 0.25434768199920654]]}
GEOMETRY_BASE85 = 'c$}qu3D}Hf|MoqPUAFAXGA)*h6tc_6mQX^LL}Oo)vKGRKRJN#>@LDFK)wA!4v6StxRkCE6R1%>b75%UCI?ty+<NA){JHD^u_#O8%=Uj8$zvcWb*FEEXJGIY~x3tIqZt=Rcov<gdzUM)Tc%{8@14oS++JE5ayGJ}b-shFDIR4AMzVYy59Xs{(dE>l^)dvh5-G5Z|#{TL}2Q{o-(_ekiGo!|g>O11eXGRSe2)s?-;iCr{eDsjM&ki)NYuwkMVNHMCJ8JqT`TrmPD{NE<EC_Defa`<xKE>60cvxC<7ryq6T^3*Y_eQ)9J?z_RuW{#7T)4l$@SLmh;N;&wvG4!#d(H+I-tV?d*ZM$%8M`h1_+J)}lv>91J&&fk@MxWH?0q9ir!5{n`W5#%+B(IBhsTt&>w|Y3=RRN8;We;3&4mZo^s;{NdVXeK2Yz1~vHGl-lj6d?ZcV7qPdhE{_1;ST7o}Q1T!+VpGhFM#3tCz~MBd#&eGWBde2zBRxxs;Z4HHsb>%CiZtUlqrpE6#@^4NF<YNutm@W}p-_P(Kun=Bs9*tMSV%b)JTg9n}?PrPjEf2ND|L!`o==`K9_`p<T~Kbp$8G^j+r-E}U}g-5%b-f=Y^tW$>iRBe;$!Xup)T6?`kDZKBjd3K+`pEqZ@aR0QpJ=PCXRx^$@3R}NL^7q@Z!G+KKE7`R^-2RuH)<5sOMf|G)yq@b~_qh&#{CKi!y?5q>-6vRX1>>?Xj(O*;NOI!&TiNx23yT@|afi6y`nee{JosG`=2yZZt{YmGyxnmm*@Z_}er@;nS6OIrf6HOyRlPdtF5DlULq41v&wcVHSU!6z1|_-h(EjSwzw9{bnRcA`W8HUcaN#vhX1dk~mVD2AxjdNo{WI6u^?jzMxp4p4x>nE7$Gz$IRh=Wu<L5G6cqEiazkSk``)n_|!LDz-Z~F!p{>z~x*LweyzSdrE^&^bq_;VlG_bV^YaN)UiAez&j`V2m8{T!M*F2#ihcGb50k2Y<`eS#G?TYPDwG#4K1dZYD2<hQoO->7Eq>orPBcH!Y$cUk=-AGVR6HECb*Y1R+1cxYL(B<K3BrO5N!n-EXSqW-IDWxDW4@tM{S!T&TQzG^w^My1hNE<8~BZsv6pKlyg@PvZC0vU*;JpPHZOTJN9mv8_MRI|~uty^Z>RJUh#Ud&?T}z7u@H&su&)e!aA9g98r?yerYQKHPAoy>IyR751Bshq#Y_dzuRmmF-DBKmIrQddI#@yWik&x(g3yZL#ZvjW00I55HpVjcl%$?!>>J%e=nn7uE~k+6;T&lq#t%Jo4mp%R~QXKM}w1BjcF3Cdq{dkF{l9B%dK3-SM&2Keukj;JI}>ROl;<2PcdtA3C;7ap9qwW!d+C*iXB1ws3x!Upm``M`ld2`}-U1W?d+Io_MGADK0!5-^K19%FH7EMt}0*LbpU09`uE6e7$Y&5dXC<``WhIi7wo~GK)NHu$pn7(3N%IzJ`e|JQAMA_3x~-c(}|qo9~f9<5OL@zfltBmM7n`xc}^S@@n6O3>WS_^DO6tgvIpp`YY_$c?M*=aQ`c77_S2hXxHb3vh6-^cgu9)!FkJfUxS~mm}d2_*DKwH2mLEq$0koA&+j^rY_DskrMmEN&ved3^<N<V?FZHmUeP`oE<7;%HrAi}N0W!&AK?4H?6r9vi+i6YCpgzP=xgH=_;NV;7GGj3^JbylCl(J~`83|OKH9n(<GY|A_wV&6<N5ZaY!@CZk-X<>JevM^y1n1Qw~}3WaMUNP^J9Bo%l}O$lU#UU#UQS)^~5!K6iWOl%ZVQwZuJT5>Ofx2_>p+~V(j}dc%XFGOxOCrgUfbbjeGf$7_TOIQe1fGwm&$}tZmDD2{a>bpBlQ(h5MJ6-fQ!*Qft~fr>C7C0+-%Rbm5Wgtu`)^;msKDxR=;po~WJX!lQMIu&!>Y$$i#TCU4*TDBXp7Gxyo`(O;|3uI@Dw$wM#Ig@^wc!+GF?%Gdh8%_E6U{Ens6e^v$hx!-!5U*0W0Ww`Lr!r{!*+e%&AFRqMEap9q6wOEJq6uYKA2Ub5~<9;2!?aNH(`jy8R_jN_c`-^4SN5-XOJMk8~$^X({+c_+Bu*-XPpJBhHx^VxxbFAm7`-pe{n{#jUn=BXZzk49}ulupZbLY%}_d}Ko53V0<*GE=mTRi&C8@4Zpek_vY!u@~$$#c+W(=8s%@3C%_|8lJhk8D1*-QM?>Nt{Plj-~&rElhXfi#PCGHnl(XJiMCzdEqX5ZjHqw<L0Kj*84ZEBR}`{BA(rce*1e&ybBL}awF#)e^>hRownqE>yF7zyvBcR{)Xp0O8xu%MBb*3S?j`sDf_G+g3ora_`h?@`?qB|@m~3DT)c2|;_;{0?>=~FoePhgEn@3KD4`bbdm!IxyN~9gSUh(w@*b&7eB5RFe_h{oE<Bo4lJ#f9&GcJ~LCmkE_uA(Gv3MY3Nvd=G;z-WbxW5|b5pU7ywJtpR%~|WWNU_q~=jmhgL-jc}Pp`vs9?f#DA6|)b)ZBmU9OHHFw#Di>{WhzAEFPILIn}j3xIKmQNyp!L&VT)7+S}>PBp2?#JHYdJ(KFm9Z#?}_?A0_E9xmF5^YElo+$X+Sirqg?vrHErF7Sq}KmJ`&&TYB#e1-T#7ao3n=Z>rK@Te;G8k(FO@4|ysZ{d7c=@9Wdr;;bz(-K{H^w!;+2WEfCeK&PjY4yGFbL;0=Jn+`hG}roYxBi@?{{EbL9BRaV`sJgEF8tqqF?=8A)JAO?_mcxsU3fHcb<WjzXy#BGU$5QAe6AIPM~Ww>xz<PKbhLVgkL;!&>a6?F>e={kvJ20Bj^RC#O?_@pAs_O#NOj?%f(vr4#=WDdoDUm*k?F#7`%!q-TJAIc^|f}N%g<yu@uqj#_1+DOsb{M!*0Id<YhAck^E~U=%;^@-?Wcjwd2D^Y4$s>>-MK#U`mU?-P`-n_@2FDgPQ3YK&L_jB(B5C3rr$2@Np|8d9^o7~{%PK~(lmQs^A2pvcHxnq_p@(as7<`+KKirgT6<2v4!`I1B-eU>x2DYZjH=}4g|mE)c(~a*CtjwIt*id;%QH_~W%B&^N$+$Q9vZTWeyH{*&!0KZaUPl2eVq%BOe${ok3M$xW9IdX^v{Q5vs`%aiQ3i=!QYQwgNIH;?eoLy@CPoXxYh@%kIcCmkKR<+&Kut5quVw(@KAx139j}2f+KiN*?-XD!O$YxAH5L)KJSXbBRw+{UF*Zids)Y-?jsMX9kcms=0eNcSUlJNv3TzJF0^H%#Y4ybVm}=*gwI!F@IbGEDX#U=l#6`cSUQ`}7mB>Yel&7(iVF|k-!12AJX&r(pR2?#&vN1Zqb=F*1|)Nzr)F~wId~@9g-1u8<{Wt2yNu%vtI5N}w^Lkr;8+{h&o@@nu6^$<u<OqhOmpFZzb^8en`agIxnm^xb8=9!6Hi)0|7>2weL7DfK6vj3F5Dj;V(XHB)f>dSU1GgDQTHPk9%|Bd?=|>c;dkuy+yu^<F?gU?tqj-taNQgDT=bV&^iS)LI8Szq&vxPdq@B#Kq#pGD>p}8xOHJ0#SUmsybl3Vop^rJ=c527{dv@gdgKt_M#^Qmy2dB8!2P@Ucxf&0B<nf$!aeJl<k4!y8dn0YQPxds%<<$%6F5I8zJo{sb=EQU7hlEK<E<Dn^F8kxWJ9*#GEAbZpqN24c7Wb-;Om?oXu=d)0^3Pdn*Z;gf&4ouMKS_T+Q<XgY_C50FySWK2+<&1P=Z)jHGA=K+XWR=6u=On#50(FCt!us4;WwU-;`6g!4cg4QUAD8`Cl(KN%UJ7LA1d`V`||qV?DKK|@KpM<bhmUD9-g;?ePsE0i-(r2dduol@@R?+4;1fDp6ohd@qo9Nb+O>_Y!~j|bb|GyS(MN5|C+<NcTY}t;nATvtgCYlT0HnxN1ki+9QZn1&w+!N_fyZ|X{=-6xNH|5nLCDg_w?r$k8VF@pYH`m7SDF!-h~OA2VU4nJ;RSC*=wBwnJzq1`FYM=Ia&N3rNW!`oEUoXNRkT=Z0*PM;|>4i_Zg)>VZ9wtJ=KZ-G=t9pCN82Ms`O(%R+*UO!b4^1kpHu0P|x>=)BkIxrn~THk2KEPhbI$1c7*e7nI5T5d|sIK|DhL%AN-8-T9a<^E<9Sgu+5jyozF2Y`ra_|LTH@}_ph(OxursocGdrlb^E=<L>K<=xu#G%^037b&KpC1PjKSVkz7B%%{6`qv~Hj3!b8zTIalMMLS4zLAC9NGaR0<_Ik*4NlDx`&?$qB)cH+;B-gz}1$@2=Ilb^1Y<-&t?3-7rGKUk9AJGCph&WXQ&nd^JDpj{aSSs#uLPjlh^-|uAIF5iHDo1LZS17*^jc>jOM&x`l+zV)BBb4a9D*DM$Q?|HmNRqpfJo$uOx)bC>P+<xaDoS*xQ@60)^`52zxWAM;lRnna6r{|?zCx7O1vD4!i_u;KFTzGU{Sw2_ncAog|fmwE+YR&EZ8H?whi(~QJb8)c#Y2s^szUFyREdKBFBH^J+_w(FWsmk^Z4m^@EHqo`--!FkYFZ&(mX+5v@pXs{Jg?opK@j1^Q$GOi-pYXn2en@iRq1r=v&Pv<Q=ZTvp$e&eGTzK@?IPxUlZsy^#vwV)%<3rBRv3TuyDX#V5WlcFxevw2x=?b4yW}M7+;r<if^ZU?N3DjS|7xH>U*Sc_j*E970f8JqSHa@t<>a+cDsuMr`HS5EemAvnl8+g9!;jMGw!C}8LAGa)_f9gC>za1`{<-~vehu{0WIN0L<p0m#0m*m2uFBE5g8QF<;g*`rJJGL?2g-0&m&U4mVEs1~n2cILI`YO|f`zM^>bEm2IlRpEla30fnAr{X)FL-?$@%xEN5zb5Mzp;4u{ukJ<qqkf9-#YpJl~flV`07{s|DH;`@0fFZ4ii5<&58HEm%pbfQJ(lO5!*Kdk2Ohl;gM7GtUsgYOA_BUI@Q{HXuX}=WAWVIHO1o5N{?_(*i)4HPv1;Gr*}wn;lZz$uy6MH-p(bVImP)r@WVS&TzIH-LHfB;s>LI#a_oE(xV=@n3->Qt$hmiRlEuTX+<(pYP_el8XDM4BB7ev8zDp+4|8JB}cj1veA<h-UKjd7s?`D1<J*``U3lATAkaP8s_qflGEBU<T{QDU$JbJku{n_Ci&U0<wV;?K`M4}6i%wI`=e)P7*qr+xV&*VQ+TzL5SGklJ*bOrVNc@*csv<FjNcyQ61oQobGPW+D_Sm&qZOLpPjgU_*kHXh9TemR}?>GwskxYzk4`_arN8ONminMa2=+4Djy?hTlb;9Os&3;V)DkMVvp2J(4=e)kfK=l<@+%kE4*^xn?6><#l=7K2ABk56%}50<%?=ZM7}HD}+*@0X|6N^s%flg-J8A6i@7-@7^cY@KhDTzKyHzrj-#iI*Jx>D74}i|6KPES{UEfo<jJx66}wZri;o%Y_G@Zo_%z-ICOQ>qD#qNt-#J#NeUm`ZU*i?~g95OXW+@|G9l?Oy6uL9$3wD)`5K7r^p)e?ZGpdPW;Z(<WKc0)?fcVSMM92<if)v9^zcu;786eZF=+j`r@-vTzIr-V?L*<wx9bPZp!{r`$(1xk1p%SzPviZeVT6KIWDO}whQ+^IhFQ~d7F5pldPYWNAP#8F?cAuREBH4|K`g)Z`NBv-spR}+~;qxc;t_+wClIm$iIh=@LXSZO{NPE%-_m<`C=yR)%+8B`oR<z9{H#|>vpSGEFP(Pl=Y!yhXg17X4@TC<Nk^Z8OONq_<dX~{-Q74wccwxmVBEw)Z*dj&-`97Yk8sz51iP{?|1qQ;6A-q@_f-}O_mGy(%Q0*$2~@S^*fx<w`CJucrbA?=a5mIxzGFrKJV4<im$`<yJBx;YwGz}JAQwi{3HDkgGWx3NO!FdBuwPFpl=iMWZY8r3;j+k7SH{iSZH5E&G$2D*Ya6uE<E>py@0PK@2lT|ds8M`J!A2}3-!`m>-}4b@wrE^B>7hCBKf(dPofJC9$LjZ?=MI`H*Ltd_2{q+7asYr2A}Ue<1sFe=J32TZ$*j=k9KUu{&@E;`gi4{{Qcl-BX~}U#g~>&a;*=|zDzxbzr=Xl{WtwNvvQUT5A4jt`ME=g_{}4jk2^lM_q`4;c|6IrKKD6HbloKK=Ht<<^RIr&xh@9x=55JvuHW5_e!FX;#iI>x;eEUI$#mk0tFBq^zoiW4bNvqOI{e@Y){|L%xli>%Jb!g5K%U3oxxY(~#dCj`9$NAU@%`VjPS)yWzfX_FBL~lBy4HtBone1G-In-*=lT3&!|N$7Jn~&L{d<Qy=>M?^oKH@rrn~U)rQMuM8<r#9A(46U&)6gv9(k!Y`~JZK^xLUTyze~;)<3a$;P`?x=lZeDnWq=NVSV{=B6<5rc7_WNuYHt$82mNy^-EYkXMUFK#CINL-RQQ%;{Nn?jPL2MlU;aV;&=L8dW7F&JvD^=^v_BeE<D^Mjy(Azo4D#mq)_237w(^RiRa4iR`GWy?Rx9q<Frn4;elG^c3zF={th$JDTVV@EUw>^$KtuaCl9rnN&ieJL;t)y*2XIqkIcF?&9y$fGauuXH)Qc(!jBuT;b9D(%fra3XX%G(`8a=0D3syC11&G{{8DPfHGa$eeQzxO@9%qC_NAWs_Z^Wfy)s>RV93hdSL1<4j*$<&d!)JWP^zE$bbf?!slSKzPM(qG#6M}k^_w~n*W4JGzb(auhh}u=Ir`_a)boW^w5$4}R2QE6d!A^=5A6IG`fUU4D)>>V3lBZ8kNtY>eB$NGbA6R?nhTFEXtk?(r)&PT+ldN$_LZ+~CSfCmywcvFzE}NIH-Pvr_v-$qZbR$+U;R_JMvdzI|Nc|A#XeKgjU*e%G5UOKWIpI)UjNs~Xd_AHbuDvkXJihPHrKu8GQwQf8~N5qoj8-a=GxR;TbcI;7#U)uhmm?lx*AD0@3%J6OzRGr>mBA=!CWU8DQ={{k&9;SZ$>VfzrQvT_Hhl~&oKCMa~*1AosmzB%rY|H$O!Y^gGS02X=wH>X5{WT-VgUZZ}8jAYoC#NanuLzZ8g%~NN*zpjTF^deC8`7$9=Tz4uiFUZ;Z?_ub(tB89p$t7aMuaNE6u#oA;XcvW(=Ft<Z6|_PGH*)wQURs`?w(Qbrn^&zv@EtHse5D~(iEEZ#73Ofi{i<P9S~8rcE8jg&ER*1Uh&$aEvak*7vJGx*;|HW|4;jxj?V)|&VBqegi2Dg5%MkNT97o}G=nY^0mV_0VCAN8aGRD}7v3NB1iiN8jNd<;?3!vM;~E&X{WpAGrZOwUA$7<8qJwgfHJW@{d_}(uf~%G_PMZGR#PAgH<&0lo9-^(Fz{@`h|IY3cAOU3qk1wUSmCUKdX4Hmrr)cf8C9Irr3f*`HYnC$g7~Z1-{-BhjWbQy(E5~)@ScUd=V$}-p}UmQs(-lk9@n)NC6|a8mSpa`{9Q_JmNR#y_?PJPDa`*e~?Gx;ZL(Z#avGsSz{!Rk9jytF@}EqJQN(WpGQ3w7<mzKlb;qVrj^9GKaI2$FH0!K`0R(u=`wN5NAT}eA7hGmf|K>7Z$%?-daN0vJmzIl<s1G+u2z$O#>z*xnstwRjOS9t8oWXtexcZvQw~*<&u>@GPFDUc*LvjdH1U49YC<ddY=C%D%13@f*M`y^9M~ovyeOZeB%fAHQG0qBc~dzKyOA@<%iGQCN1>;Wd9YTw)5J$#PnAynWzXY^WrFeo{=2C7A2G56G4+uvsDo9+*?iLJX2lh24{3c3AM@i+<;hb04PT><r+MTY{09H+&}XAYHft?DgWN`rqqm{vz3tJ*u%(cEhq|-CM-B{=9^*W6e3NPl@(;DIoP63%afNR`6CaVs$PMH&`U^PRPC18I+-d%9<S~ACNjKC5<aJ-^P+45st$l%isQ3Elel`!{$X~>}w)meLo0nBH;Rn<-^c2KttK#NY-$3m_o+3vZ=`$;(^AiSpRyKo=^`$3jOl|RPtGJB(h99#$;^>*^4d_oHk2M`R-PXrCh4^(be>X4^@yG|%Bh;U}<v(y3YvPT(=3_iJE1!2Or@vG!JnExADkwfTh_BG+4fz}Vyj3<-&>GaQo8lO=qKXOnQy;|_aYp@rTQwAXX(AubQC#m-{-9T)FQK<jQ{JM_z&GeM=&|S*smeR>ySe<FCSQ+LZoVY@&{IEAj=d^dPb+t;ski;1b(K|j;kPvL9Chjz#Tc{90@VR<=uPSIh!Ol(Ksg9b9Tn%mv(EAd`pA#U1=!eMT!L>Fi+{)D^FrFYx%Mw5-({%|pawkVV=hBS)Y0Lp2|<tZ1h@$<yz8+qlv8fN52)9_n(MprPfKwf^HWpRgMexf{EeD~J+Rjc9(98MpY_q_*c*MPp>hhmT_?TL#XZDhmiUf1pw_Nb{-Rc(pH=r*%gQN+xL-YUecs3c<p6pbW`dg(FT`z!{J30vN8Ld!X(3KlQf>KJaRz^%P;Nqh)C<gzomCqU%XZ3T)S>pW8~U}DO|T993^NMmxyj;hFA4s>tlZ3}{4B26wNwnyqgF~zc#IFYF<I}u;A1U7Kf#=ce1G4^Ism>@lzy1OQ7hp`)ahZ$hpw^_dXAB<cwJ9<{;c9?<KwYUVI6W0wH~@eJ@$ng#gPozG00;aFz3Idyo&gEZ_Hqy%J;2Q6QKWI#j*@j#*6b9v$tgv{0|<Z<|5u$`-^OOQ}#TiwQq}mv&3QaDAXs+45$|cRGUgDFR(Ybu}M70k}r`bs70tls6j`h`ytgP^qn$_C;mPwKemt`F=M0dw-dK3YVPrio2V!6N>}LFMEQ&!gZliM;))v8U-?-`H3q#Mc?5efza;ut2Xp7o67nN#!ddJy@oT;~hI~Qq05|SYUSme;sJsKm9+%&S$allUp=$DTj<_*KJVLL-T(U!JP%Dcn_plxq`bv(Eb1iH}jr~==MLh-AVZ&tE^qOJ;KcF@gk{?lbP=8SOF&klKi+J=mYG$(hxL7er6HmaGT)pucXEyZb!A4L&ddl}9k3IsAF&`Y&{X?=hNj@$hKV#-CrW)5mdtz_!b-Ho`F+klwO+wCK4s0*M-#9~}@1Z9w7S}K*f^X}z2WEEk8{F?h<qUEM^#FQ>#6fTbT<NFJWJnLpb-NV@#0I?#`MgqoN){iH_p{_%)Y${d^Fz`J_UE1>8!4Y#NRa=)P@Aw8c2v@uqT1&M**seO1W%EZm>bXshbX4FKjt;`81z`otC$U!>RxknKh#Cog4&Jw;$^MDdwa!=mz7_bu`=XSJR9)jE7TnHZuBtZCHU1{IdxHfnk@gr_qRxJE=A12%R-tPQJbDuT;gTtCh;p?96O*KgN^5v%kaTT*$cbVWD{)r!Q;6TK3K24_bNsa#VN1mPjC@A11zGv%&$CqRriIC;PnF81N+fq(aXZJ9X_Zp9V*CQ@SB}6bf&|(24}OA(z%CtI7fcHS-wRaJlXzV<pOd7Jb^B-XS!mCT94XrT=ij)_yArtlm4$N7A?f3XB9WZ4?X=K)ehuSXYrz=Vpw0gj8;q<>x_n4h`BaP{O+kW@rpIh3@4PEugZrDR2xvAQC}x0zfi-#C)6?fOv+<jMV{gw$f5e;3u1<T`-9?}D7%l#zJaO_=ugNG<jHHY6E;?sUeFJ<4QB!LY}C3p#UpSEvkK-^)N#~#oRivX|H1NKqV&c*i8$v-hu-ot{DPSixsSewnuU5bNBV*@s56+IcPrK%74QA>ZCLiBH=+k!7Qf*G^jh>+^i|9Um=n;4zLZWm@=c=j#aRhG9kW-8>{}qa(U-c4F9#H_zKSI{k2wjxLVv<+iJ1>G3;K5pk9BK=Y6a>j&cv_{{R=budBx)<)h)b6PXc$58`uxIgtNyu`MkOEu8itMJ?#hXRgljoD4zHXa(1tB8+jd3E+LQVYu3eFf&3VxT2M-Pf_uFt{(>u$mCNA&qsl$|EY@QTFvH-!D|K(oN0?J_ejKYDN3Ns4^ik|D%0|R}m~!KY{05%|J)Ru`$}!Y~+KSUX!tmZ@#UC?rVcf&W-9~mASz+WSBg@R1SBz{ilGnT*W5j19+sJq$_Zi6-$JZ!2x0>rw^Jf8b?EssNOfqt#k^DyL8fk5$v5^Tz8fq`>gU9mKjNE4Auz6k5>~|;hH&W0@EhC@$_}&Hh7<@tQo9k91zZ$9PqiitpjFHm@yJ7^-|GyJn-0ZW&Tvvm?Mt0#nBd;5I*t}jUJCi;7;~^t+J=(p`<G$Dj`_+x3F3sX-*FYmfjr25fpOMFmWSIBc7`b2Tpg-)o$y_HIDPd%QkxORn??x_xi$>n^aSh(j^ca(2Mn3Y<53`ND4m*+8M#>s#6i54N$MJr+?@#cHc^zluzBuZG_qHKMM*0{TWTcqZ;xk8#MCIo@k+1NLk-6q|(8v@YeY(WRJn&7n!sdO7X+GHs9rtLTBJioM#T4%%x+4Bf%xBJ+wbkS3i&e-6#o|9kjw>eM>VJ%!6<@*CvPRA+-Y*$>8nwsB=LWxQWV4axaf}(_0RDhGZ+Y}7{PLHN`jnQQUBv(H9@j&Mu^xGY`>yhFO<moud>nm;dz3e?E6YCQ!;j|rfREe&pB|83VdDyM6u$hxV=jGf*4~0RnwK+;Jca!Ak@LfiG%&Ak^61z7=JgNIJ&s)HE1kYmjzITwiq{7DWT*Vs!^r1~ZCT|h^7R?*gZ;qQdogPpnIV3j(P!%*zK9d%Fyyhh9`KQGC6&9kDSsc3A1-*ri|D<IsudlSKLb@C%A576=K8&ncRbc0<l$_^82a@$g8v=Jf*$o)Xk;4VCO<7vOe>3Xe;H{dUf!q}<Fjj((`DnBkKo@-A7hGmf|CuTZzUs(R5M0<%*$fRH~fuUtuFtJlaEl>dU=fJGQ}FaLLTl{?8+;LD$D0pm9tZne=D>e`8!>_U!j`NT0R>no|N{H-_W&@bO#5viwD!>^LsqT5-~;XdBVsd<v8p{&LA&QS35&bAM+qyxzp4~U%x1w2FRXXie;km0{*+C_@hVcL`;3;3hJO=oXsztDk`p6dsyr5@G(FBQl2c+-|#i+c)CZ<RaNiUsn34xv4{Po&mgyv;{lH~Z?#7s!<NGG9qP_PA35-p^mxuA$2Y5{ApcPN%FCzS6<7H7bMX;*jNCvjqrZT|4=Lvmi@SX6hlpQI>DE?x-A_7H5tsI8U*K!?-jlkY&4W1d7xBJF{LhWeE2^3B18N$23gWa)al1u*!&9CjM;q%itE6*pgN>BU;9~>ni5hc{__j@4Mt;MO*&cE9O!Nlyr>P!mI&%6!AL|t2*VV_FV53JqpdO+A)RzCiVXR3oGSA0&Zc#q(QBEIFEj;F<KW<Wdiioe!=Rfi{_<5UbxJheDYvw@AiYX@OPfseoh%@T{YSmEirKx;8S8=^d`Ga1GzJ%UBU3rT>1K*(6pvR(Lq$%&f?|}TAE?<vRZqAT>=&7G7$7agbGs@lS>TMUau8Qg|{FW}BqfTK?LyR%YEL0r;hZaeXPCk2Fvvm<U2u>Xn=fJZr@(23JS>*z393U>iH%r97<MMf7?H$nmrRBS9)dAFiZa(HRbVMC}S~a1s$9cjNN8j_<7s@L);0M&}-^}$r`KOh*j`^vX>Ol+DAov?K3435K%&48@|B*iW9DAehG*V81w;xHb3~>+fm@U2|4yd)Ol)tDI=w~%N*0S=7A?}BH7xVK$<p6pbW`dg)FT`!9{J27VN8Ld!c|e@3tlIL6;tc-wR&GLn)C<gzT~r$o%ZHT9s6!oOH}q>Gn_wII8D<pBb5q3MCnWg$igGi*^0S0u*Ge%!k6I=9#$$ZIjVXF>l8?0j{RDF&^8EuJ>j3ytN%~<1N3Db(10HMeNa+O|q32lXir4ok&qpebHa;Hv6xJd4Q0t+~*B<*qNpU1ob`16y2h901lvf*lyf<dBt@3?q)dc9jPqBnAkTZEa#%#50g8#u|)Lg_HYk!q3i)7Dmtz9kt%@&7Ct3F|7K)ooa+H|Ax0(*lSo5h1{`4V}8T7)`;8gx{;A69Kb-zlqj;_q|v;{);|W^B~`hs5nlntN^$H&IXCldjOSsqz^;2K9NK;))tIK>1l%H3q#Mc?5efza;rs2Xp7o8|6pXgtOS^;@9iq81e<Z1KhY*d5szAVdWh-)=PdHD&IXN4po<*cZnNg#Uu1O%q2Uu2DP%7au4f)p|9-naju2UsIkAvx2UJ!I&7FCo8~DN@B?Z?Vfhht2lWSaAF~l=wv8VBjhdMvKQ2)W(!~?-C0B2}#+eQMd5Dko<8k?Zs%i>&jQQZ0?mt!bCd<bK<!8*i#Z}`T(4N>Ee0@o|ff%4}pe7+_Fb8&!;BTBE(f803mWXSZ6T!ESv<GH(^c&o7t#SsrgL(kHriz2$2)NQ;pUIRSnCtc^4u}nU8S;6R{FEX-BJXF*x2UrRmFI`06YS4DM>bYIKOjN=14C`XTG&xpYl>-~BC>gm_z9jOCowmm4-QpKaevHf=rQQAm{&0yF4Mi{>VBw;um!cdyXwR;y|+)?ct!bz87osh#j^pQe1)2W-i;oHyac~`D5oyTPgCT7`2JQ2&ZUSscv)C;BWlxl#U(*@ZWg~1#Ib|QG1&N%av47OUiQN7blC*k@Em4?e6T@#?^BF6djI<zskZtoat7E&<z)fo*-YIRI)c{=We@B}k3}zgOSZ!Y4Wz?O@)!JOXAGU`aIV4G?0f0lQ#_n2zgCoQ5eJ`aU#eU{PJk!S1@^q8*rC>=Hbhk)28$2i)&0_creg7cxHM96L;TRwQNK|;kWXF2i-#4%2GV7WV$wusG}J=Owb|nL<64uTSmVs_jdF9Qe7I1x0reU6b)xbMH4J=09kb7*Jl0j@Dei$BY9PKKX6U!472hP;9hH59R3FfvkRQmCd9o8WR*_!N548<v0rYItx<%p<IE7gSb85h2oyR$;gZ3XH|0PLp%#(=oF6q!meuiH#b0YWA_fWG?ujWc$a0Yb-v-2Ls`eDWUOZoOK*^l0c9&|<gh7Ztd(O=P5F&|(~Kp#3Fop#ALNzxZ*CG>R6Ua7Kgq3lLqdQ5ydsCe~LEWvrqN$?f=6J|@ye3)78Q++|*dPcPZb+oFU$Dn^<X8%d?xLI`zuhEmhUE~J#LoVU$@tk}fP~MeQy|_>NfqOT}=MxoAd<HqYPq~e}-l$wc9yQRci@5^%F<7;rwDJV^nkW8(D^rxq;D2Z3o_!YUF$S1naNkwBH|8V1$MfSj<v4O3{pCr;{*r7&+@Dfz9F^bTv%VhB4lR^ps0a5bPWKAKdsh^H%*X|e)HD(T$BdjavdqYT&6-U{W+1)I>wnC3l(}ZY-|(@KJlIQ^AAU3P6}V<(qLD|86vw@d<TcXL$n!=T8mX^+@Y#|ce%|hRw}U(8bq%v`2_qGZ++`%ckuAt=AK(Abtoy>q&F1e<z*%$sS=XnHd~D>DdHu1Gzu{-|x@a8nPVIehrStrs{x4+y_doc<yXOB;Ciaup{v7}6Po6V-{rltmPVMvI>|ttToE?f<;9D5)e*hz%sw@'

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
