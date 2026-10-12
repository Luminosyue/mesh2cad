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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_003.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_003.stl', 'source_sha256': '5aeb891e51a49134136f088333ff5dcedcb85cf0385bcf6cccaae908ae1ebca0', 'input_faces': 956, 'input_vertices': 695, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16257020831108093, -0.22168734669685364, -0.1540503054857254], [0.17244482040405273, -0.21548667550086975, 0.19968204200267792]]}
GEOMETRY_BASE85 = 'c$}r32UHYE*Zv#KIblv?!kjS&+Jsp#pscPqDyW!q4sFgE1I9rR#0Y|jAljx?S#w@>b#`6MYuME_?drF;>gn0O<NVM0pYQXWd!C=qTU%3o`&Rc%b+xZ=`*i6&6#1u=lDXSW&z;Q_g(AD+p-c!GGcI^Q(Aa7tMoo58atojS7`mpDUq|2X+>{B*)bfErV+V{W-_TON@xc1!t60hp964s(n0_PrjvNyhM7~eIVPk{-^~VnGH!A4gzgMW+piUJ_?TS?_(=GqYKUx1Bf?oL2sbi$x*7Kz5^pbJjq_+};ujN_$BdPK%Ii7s&>K5svy?*Dr1oD;5V_17@>%R_(eu7%_e&Saj7X4H!#(aB3jb!0xet**J>%Jevc=Y$LnQzN;;fQG8_2EhLc$9Xb2gT=ZzQo!qEgH)4v^vAutNBJB6@LBQ{Bt|}k|_Lj3%K87VUqaVw*#1Oy;oI^XQemm-}>l!ipbAWPd@&_OOA=-%2bZ|YS}9y&-#tLeEhp6h&=1z3iGw<#l$$3ZI4f|^U~{*$g_I;!U^`dZnI>b^Tab>ui_=fsb}BB{cC9=Kl+`8tbcW7S6zH=rf#gged=zJf91R8+|SZo<X;<Ji}^~iFJk<9i!!W#?YCr+XQhY-A5V>`GS9Em^L{?om*f25-Enh2wpJfxo}WKI&hmWaz8JrnaTfEfo#%=?YxhPo-yU33=6U=8*1tCQzO3gb0j$09N3_VZ@_jGn+wP7PdDbrZ@o~2G7UNWA`Lgy}=v*;Q{qIiPzdrQ1@Y~1gtp0C*5WbpWzs|-V86fhn{Ii?+YVI7Oz4l@U?<ZSnd45Z8=YDEValFb_n^XG{avm+)$ojWUT_?|1)3tm&qx2+s-m@{^T6O#h(LPdPzE*O97^h|1>tig>{+q-&t#2M2Gmpnos_!x88{;Y1T%1Synaj-AS1l0d#n$2y^DXT^h~u>v)_HsP7;%0rf1W+c{Mm2B_|>v|xIau0zU}Ec<|_~LiQ}@r9&*$?etVgTBA?3beyqK^u$&l=^-OQpUOWGb$frHQkG0owZx#7hA5Kd#x3_K_aZ<FO;FrSA%i+mloJve1=BqW9iE&!DW@Ns8aG=a{x93M#J#Swo@~O6ea)h<-_@l_1t$7-2Z~2&6&iBsMnQwpfOpH_Mq_BRJOn=HcnP5+5<4n#V^L)m}eC1JPIp2?M5x%10I{ENnqWJvR8f&k4O_$e`i{p~nI4{MEd|E3GV(s<ce;4Cdcil~5dHAc}DUoMeH1pN&!({#&&ttxpd8VwNUj_(Y$&2wUzjs*VV_f4Tc3k_z#c|n}7GV8Yn-3M|MH`wm$$Y%Z&*u(_|NY|E!z^#UTjhN!_tV3ypMWdkd|7ABXYKW4KZ)bgCw6DPb-*KWT-t)lhgqIeZi;cJ=_;}I+M4&`cr9CRCbBx5SX9<qmP?7|e$<Ia#NYM3ds%zSkg6gNmaa>gZ@aQUoJXy~^h9$$l>zYyqMs?l5?!5N)xRe1=Lg@@BF~+^9%AP!rmx6@HTumVbN~9_OQJsP9WNhZd9#la`B9_R9Af#&vtQ<={TSB2k}gDEpWC%y?Jbjc$ae4@<FCC#*29fLyq|8PMLnqfUM8^5eX{l7F_Z83{@}eq&fn_yn6F(pBl2LY8<Su@UUfo>n4fys&IES6|J)Y&v3QJUzP&2ubt`|?kFqCB)QLVWJ8Q3;&nD-^lT56=mT!ZczmIPpWbGRkll7A+;UMdO>T>bl+rHazkj+QbkG=IM){o;laB>9eN6Wky*VEywy=8F0AH+CI^gGD%JYrG2(5m%Wd;LOLna_Zttbf%fMAVP9Y(_Rtd!srcpK8{N@vPn|E)w;lF0;k6@!aVluagz0#k2ZZHB;1wea?t@RzGb9iM-jqG-3T{N2kdA_*P|~s}$HI?l;y`6}ay<S&n;h4%Uw?xS0Gt*7-{u%Y*wMkvHw{2XXAU0vC$9QhHwH{@bzQ@AkuISU(o)Xqiv1^>OUDvd@xrxN|k@M>#cBULPa9ct4(D@;+io&wMo`R_5pBn*-*2YO4p!y1f5f_^NRp%Ptb%8*Je>53uu?_pJP0=NWx~eQuc)IZro6u>O^=Q)Inm*mA%;e!F{rnRn|7`MJh*drN}Ir}cRtYp-^lA^)E0&-&MY8Yb_HK0VoZtTj^Pb+2UwHh$~9^CF*G^VC?DAFmf8Z`PDh?%O}h?{7E8#+vh^%_%0n=P4IP@%DrAi}p(Vpjh)b)zIOh-t_7NnQsm0BI?cR@5B3fSxw|w%TYPjoCn*rLE^kxUX)<{DC7DbG5bb7mHHXah&;@EAH(urd$IiQuRe-lb*^L)`B(f7Ghf?NNaWMfJAnDt=Jn)#;eL%6mgko~^847BEWH2Z{_?)C^6h?eK9%v~beX@j{jARYy2yFh<R)vcekdyHQ_pv1Kda}QU1hyxJGI|D9;N+E`MaR@c-FrbF<jQigC6_Md9#1*B=V+J@L=t&t3t%_sHa}-Gar}za(8(hNDX1WJ}pqr>&L(CW%=}-E%K(nTgrU3;VPN8YAu<s<c^W^cY>SnRipj~o|nHjMts?0K3+ZTqO2eIj(q0tBI?JM_0Ara|DLHLpLTod9#&VM(u=yav=3qZsN>~)u-zXf`!VvcXoJX`(xm}!pQi4Y^DifBZy69K@@9XQu-iO-`{Ml~Z+f8|yIK7NTo8G)R!`i;>Tv#D`F(8Cc<u-OBk!l@>M&nzUQ*_BxW_J54>x>eJp|?1WzMt3zpVHj`)`7x&Az=?W08ORjvtw?r5zG^QwPLFoBOx;OcwQHeKaqc)my$_<vg7nz}l-j{be1zt;*V4YyU3trsuo2(|lZ(-k)XO+SXydZC62Y-LnmT7{&Y$Pg#el(NU~^65GjqmL1O8E89lO-+kk%Mw!QHE8JDqL#_N#EN=}ah`gzLe~UENo2^5LobOYwMw<K4t9=pk$1?U(B&+l8!{qPSv`vw$-nLXeE5^TlPNcbR)d9mr-6%Oavi4fK2C_cAzU*N2P`S0N!zq23Z%^zmzb9|c$$aDcu<mg;g7uSQgUs84DCXN59Fz4n%_oA*$2(m_J=nh%iZCCqQsk`2n{~~ba8?hOvxs`I&3+!v=I^xUBA<G_%i%2lwp_xu{kW6$qkGEw(?i#Vo9jyH*IVZEC*N>$-jqv2Mc&jR*_dx_HB;oxvT5daHt!OmWWC*Oz<j+*vdmjR_U-0+)B2^!>)x;T!_2;QT`u9<r+y#C^57LN>cn=wSQx9TPle_B+V0$8=6cYA^NM=VJHN7-+iSa<i#+RpUuM2Nf3V1#<?RI<>*tqHQQwvxAvSX!)Ur!N-jt~B%(rdaD)MGk3Nc?Rl_=-$#1`9FoxFK2f1ftIyp`o`QU>YwpS9JTA0?rd%;%z7tiAGQU-`Qu<MYj|-VSaT*I&zmzRcIMm56rbD~Ixn`D3fyY%|N--Jv4SYWo+P%=Ko!6Dsm)UlYBFweNUR)~82_O{{(%CyBhNPhvK*dW*O$^LD>8^KFe@%ik%93qsAuYpGg8T=&#{p3K+h`^t5UzaDO2^E9g_fA4#TF<<W-BY$^n2;5-KvwH1;{9gBKDb`-=kxS0&N)OhX+gmn!%XOQvo7bD$+ne5(>y798GG9q;D%Y{|7hi9#H>J*YaUU{#$9(ycIo{iaZ@;`Hne}7Lchs%3uP$2^VfJ;$I_=y8tbZf_6_y=z<!fE@9CF!y+S){yeq>>}ZuZy5wXA+F?-h0B>|3+Gk@w%?yVsiQN<CRj__k$**RuJw>zTZc%}xvvzLB?)>4b0F6&zx2uNSN+>dp4?$2Dx6mB!2OZ<gt6Se~zLly$Y(hquS~6D>ml=4;Qs%HL%pAFO6|HKCTAr_c7SX7z9?NPbW5K8g8y=MAE+Y)6|h-=45m{{Cu^hxyivpF~|*!|$vz*OiL-?(FLca=shB@qA4wJ9VYED}R2sFjv0yPVWd;zHRofU9NoX=D58s{k2VF%)X=k^Zgj_%GU>7JH(FHsQ>;s!r5^d=j;5Eb>1#~C2-wlSH4;;Fv^v0J$542m9IVZiDTn5&SR6#2`>FrJrBF|lkX<E^wavvb-z`kSD5F8lKz#LNBW2$=39F-a_Jl2)AVzBmYe5`vMJv=(SJj2nR&k0C)JVnyO$Z6ue|LizbA~dEM@gP@UWOiN`<H;=JTbLOq0LI0|J(?_HjkzdeMX|ynSn5IluPli_PsVcjw7@bZRK`)se|^9{pXK`{~}u>$AtjMQpyT_msbzI?Q9f?P`KtPn+9#5v%{Ow8gG`b<&(QF58z133cUbiCee1^!=agbm{L>V$J?H_XQ{4aou)qZ(O&Xe8+vn$yYv?N-_K2++Uo0$Nk00x7S}3X7-KwVu`u6-P?t)rMK^J<?DN1?{?+el#lyd_G8@FjN@{?PdWRzPpKXcXN%)8?#mx*i09e1KW{SM8aV$1^NsI6gD=SMMU!98GS3%nNn<g;l#wf#Z*4hP%r9${5A&6r8|D0Zzf)uN9QKc#Upcxn-}qjnEi9w4^PXw2oL}i5%`~^Shuh@$$-~2#ug<tFzn|~THk0*JB#-nXcFkb*^R|urzSN`U4A#%8S#lkw<K^k*_SW9x<o!z>Ii1z{hwF1)`NsXo**C7w&c1Qq`KEu|U%v5i-8Otj{pbEI#q2wOPj>c=`;N13$(6xo_MPuX&c1O!a`x@><o(y#S8@M!_Ko|jvv1tL9LH<4$9>k>H|}4~z76-^Z`$L&_KlDG+BZJ#YucmP!RC2nc{xVRJN>6p!RC2qi@AKlm2ba+{TX462MOP(&n5%Kywg@p8EBqg_Kq9neNA~9WcJl(SLM8WmuhA8hU>iHJ74#ledD_4>?`NowwQg#dEd5hy0;5ox5@jCtw^C@Z`1LrEvCrp4}8aS6V#ituZ{m0YWAJym!p5<_x1BbCy%-E|1QFO=lXZ_Z`4)CL8HB0_$ubRbxRxBzj1v?pY1I3jrN5vxb&^nR><@FG*vSnuaSRe-^l+re(5*s%)aCLfb-(;jq~-Tpr0$>IA6+$ytCQ(QCIdWb(wF}p|!^#?i+O*VV`Y2?~Xb*eB-<r^CIm7^No3Ax!8G$t2%M^jXE)WBM<udCu>~!iqG)g%y&BP&c5Tk-?+cbe7wf}PT5j^IXl0&KiZ=fE;rYSaX-~dj$C2Rk8xji_)hm_wfR)m-nhSO{?AsstP^M7s1x{(>%(OGN>{$4ehl9@-tfQ29CPKPt}M$gg|PhK`?kd^`&x4zjPK|6&)wIu_V_+;z4&FV`FM@*{|?{z_rm@3>&(9K`@)*!xxrOEIQvSQm?dW4vF?Pra<n(b`KI_xmwp>rSI)jsSGs<1qxpD^-}QQE`b}ovu?`Rs#C@zAC|>V3nUB|4XRu`V+05z+>k<y%xXxo8!(KUfi}`qsIx&1l{i9BteI;z$JeNM|<QpG#qJHXVGar|+Zf2V~gZaifo0k8e&0Igmx}0+3la0+6V;!$Xu`qVLSoc$R_%PpCCsZ!^g|T|T`E~fl`9l3T`$qkI>&tquXKNa69>1}^svVfZd}BRU?U%%SWBu0l_0Mou^Vi`!otJNXoEJUQ`*3re80*Pu@B9%gKUjaZ+-@FWZf~q(>*Z=jvh#xVc0FwZ^BwE+_18wa%G)<S@~`eV63OZT>;Gztzaq`!aXd#@mM6+Qe&e}=J*#(=xxMlHLh~*gEzX0}a~5rM-Dp-1$fs6lY&1KMcwVEuJ|1lzr}5m!GUHve`E!luL~3HzUFLBb&ztlnjhJs-_v|Iy_n60NJV#TM?t57N@!ZY&W;gSV=XXl%n?3CO;yIx5JmX$AU+~;e8&!|_#&bsdyL;mItMl_v>l3g2<~$hBPc6?@Gv9a)Yk&S)_>Sujp6BXWl^Av&@%&dko{#y)^JQh|&oSow7|*rskF&<IaT?FT$2W~-`N8va>xv1&cYa>4mYor6K99!peWlYf<{SG2^j;kfn8#!6Pta~nK42b?v7f>ICiVcEFUGzI_>TNwABA@K6Z4Jz8<x8n<JkGdJ`iiW<T&$qjD040`)6_H@fiD3^h?j<%>5htSZqP1<5|67Ka9mzFW#ItV_%K_a7Mg&JjT8qeQ&vg?6|OB$l9>dLGyTw{YBPey$-Va$9^P>`&ibGv9HPIw~Dnl_CeWt==^iB&q~kLFM;)geP5PJp$X=GjD2F3z<sQ}v9HWl`$yK^*oUUJQVy}>!hSaEIk!XRevJKZmX{k3ne%DIemuS1bLKnt^%c&X$i|6%fYzu+%s2K8s*PJDvhib|p;BigYj5mJwD{gkG=HwKPg39Gd6?x5`z@{A1{^jYukk!u**}-J$9_(|JKkS0J{S8x^**OqKgNDhOSRld>^x%MshX>Ql6joQzE*qYlq7RM#{O7k*-_Syv7c6({y2%v7wo^aEGV4J@`?SrO7?ci=6-BvkIVg^qqi{Mf_=jFM}INj*oUk&FLZ?E0sEG%k&Ta-$8YR&wrm@Gg!S_<PV7gr?;pYXG4@Mad)_%>&X0EVhTN}vszwUSgRy^m8s4ig?vL09ZmG3^wO7CF5c_uYZfjV3V?VjA`w8Y7`_Hv2uTt3gYMdhSW-AeV)a={pKNopZPwzO&@>zI;*bk#0ym*x52m9)6)1Dk<pNoC?mdhEBvGF&Jl>7aj<~qiX7yJ2b9@ANSeaCrOZ~mv4Z|qyMJkF`JJSQ)c`FZc5o5yLvdkV_hlFT>WYta6d`)3{XX1oV6uZ_;?E$=>&H+}qQ=IfoN$^Bpvp=>;AgYj}7(beOuf8)Imtzs(kjrT-U?J7U6nJeV}w;!&v@oRYBME&P08;_Fulh_xbmMM3foySAp%YA`Uzh}Pf#VC<Cb)?+a<2a95<$E;x%<;^3ymxbP3U7Z)zQ3dUtYH0XUsLvo|89E>^Q~Sj<-Wl3zwq&>ZDrnO7COQ5W4t$%t_b(>o{_q;#0ge!cy6wBEy>&CeI>1LBi=r+r_5W94kyg{SKK4zKBwzJ%-0H)k^3hXPiDS)CQ|P2X%)$Q>(VH>?lj`y3G;ch;(acy?J+)1y#J-$|ACED@9Qb^IrbuJ?|6^w_%(i9aXsX^qV|mW+AkmFzQ$pnobo33nJM0GC)sf|@t6ApK2|-+`f;x**1h%QYVx^(F^_KbmCq^rbUkSvrv>ld>Gi*7?UfTJ=8Mm1+n@EX->N6p549D6C(U`Y8}IiG8NtW1XqVg{88V%HuJN9r_UA(Wxi7=V3%#|L^<$4{B=`OFUeEe*yoWd~ocHtgpVp!dukB|2sFRZ9{*6+xydUE|#}+BFA7fruTryR(3p~e<>+M{z4@UP)W&Jqbqdb3$jYl0)P^>p<{`XjW<9$q}@l)2n5^zTD^IQCqwRgPNne#QvzmE4n6~8~&_>~pa<a&7gKRiDxmWurr+7acH+1IvKmfxrIWjVz@7w@0yMYFT^w%{(}`KekZFZ1<6^X2c5fU?ZDdL9?Qf3yhCQ>?C9UYGmx;5)|CeTsMvt4*xR#$&uEt2e93+mH1U&%d>mb(yaeogjZt4pmQ?^P{f6D4uVsC))7w=c+7!#}@8#iq$#Z+g0E8;-8D>p=ypmc3fJm-{f`XQXp@CuCsWKs3ebL$K`lm*ncJ;f4egS#CXrHWaDwXcU&@*`4;0nW%!PMa%jVaAGC>&^XnyfUAnP{^<%sTt?Z2B{d`K9Bic<#V(oR~ed;ATKQ80_>lzn%KTk5r=Z2rJ@OlWnCHE&ayUyCH*Zkz~#@IAI&K>f-Z~gsaetz%7$1vaM=V4v3eyZ>N%-UN{l$XErHTTnI-+HmHSWi^CWnsSR^+4`x3Cwkxo!>LRiggX;N$%6^yx_fcwRJJpk3F!pSVvQelwtko*KKkg=W<=<8_yH<5{+5^n(@B;Zk3N`%Y_9(8wW67$$n;n=+AG^X?DKwKE8foDsSJWleZXWFO7Y!<GudP8~8Z!?*J%$LwP?}W2T7qVX-U^w%l{%dc^Al*52ATVUakl$W-RrTVIgZlYJNX=QhqQu6s&>dpw_gmW%6vQa#P-xLS$pn9}AYZ$GuGTrd0mGaILl>yk1>`GI}z#sXrUPT7<92Ub_KkHVMzD-Si#Zw&XXswfm$6c1%!Khr<)Kqmb$)b&5{5bX8;^-nxBs8jd<`cFL6`gaVq|BcGfs$kNx;L6}~2;$<<V&MEx4`?wkX;H8TI3I#IFM_xTg19ua44AYUxHPyrg18>E4w$qNxE{DEg17~=IheF9xCOX9g18&BE10x5xEr_+f_N}=AeeMCcrbV@f>?vj0Fy2OYv82_;!x-YFzF6(C^!;990xrBCOrm@1M3Ll3()gm(x1Q=z;_VDkD-siq<?}RgWn>E-Q1)qZjwn0gWbSI5X4QOjlrZ=Flj$9X@77Na8m@aH*^4)G!X0!RuRO_pg~~Lf#7D~<_O{z&_Q6*!Qd9)mI&g`(2-!$8Q{*~P6*=fpwq#m)4<<>{Sm|+p;N)6Q@|a;9T3Frp_9R+Bf#y!JrTt1pp(F)!@=#qJrKlx(1~EuVPHRSTLf`;=uj}}1aNn7Hw1AT=y)*cIB*+qYXq?mbS#*39@qyw1VOwQx*SZp8N3+020^?Lx)V%#0K5?#g&>ZH>R{3z!SUc@2;x-e4KV3la4PsJg7^;fS1{=lFzGK~(x1S0z}FGPXQ9`?q-Vfq!N~~X7-$NZbU!!-9DyL-01XF|t_N=bFGUb9fUW|Q&Id05k46x8fsO)``hvTF%OHreLra56vw*XMKPWPYUqIh0l1ZO|Uw|JVh_69^29sU}Ujv^(5GO%Tf=Lg7lfZis#M_|JVA3t%ZQ#`i;yKV|VA7f3IpA>!;z7_c;P0V9&@o`r>EIynC<O6T=wdMGTJTixd<5|-s0~cI8@vj<89}@YdKgUl19%rW5kY(!dL2yq3-~nnDuUP!eF-N08*B&vjv)RF&F?0ev_6=E*aJaa5BfcrbQZWCxHp1WgDwHDgoZ(vfJtrOFz_A(@nPs*Fli$AF!(fr_%ieqnDi3(GWcf%aT@d<nDjSr8u$f*_z&oFFzFlcAK(uN;xEwmVA6lUU%=_zWe{hDrgN7}ni-rGoC`th0nH93%?tJb7e)}5gcbsmmH?LomqQR&hL#1BRsvTB*F+H4gH{KVdV%YK8zYESXag{*H&_MxAc#9aTY*X2gFAq`B8dH=UBIM0!2aOA2;u?I@4%$J!2`fS2;yMq_h8a~;9&3w1o1d%AeeL@cpP{df_NTuFqm{Wcpi8uf_OP}6qs}@csY0#f;a>^0Zcj-90FdCAl?j}2_~Hb-VEM~Al?pL047}w-VTmH5Qjq-f=TCt!@)KL@fPSTFsTOK0^Wom4uwt!lTHSQg4ZF4*FYzNNymfNfL9`jmqEvXNk@X0ffpf&=R${pXF!KQhk;40;341u1hF5qCz!Mo*bm$pLEHw~8cf;@+y>knLEH%15KLMd+z4C;L0k=56-??0t_H4vATABHfJuvhOM{Cdi1S19fk|_K^Mi9Dh%-Smf=Lx{Ca@cV__LeTPi~S)--17b-yw)!L0^JNAA?_kpCX9u&<9}Bn_xTm7J~Q!^gNjKIQRni1cEpLdJs$+4Nd^>LJ)6-ZUK{qfVYCzB8cZe=YmQ5g6Dt(5X23kjliUZzzx9#5yW2<sb3Yzq<?_FfZrg9e}krhNpFLH1K&arr$T=OlO6@9f>RL0G0<2rX#_Y19F8Df2VD;)T?AeSUWg!`0-XjX9SNQS9)Te44-Ev9_5$|@`y+@uLw&)dZNQzutr5g3v>BMRAy@@BKoHl2)&i4O2G;~vLJ)gG%YjLYgFV3|5X1$P|JM76b3$`K^Mgq}z&XI#5yaV``M{)k!P&rB5X6}g#CZ_Jg`q{jq@}@y!KDzyRiM?ur1ij6z;zMCO`uJ|q%FWrz%3EP9iZ*Oq}{+Bz<vng0B9dD>0odGI2b`Z9y%6Gs)5IYXCa7JK$n6^L%}P+n-IiN&`2<895@Obk03q{)xo3}z{kNC5yW?)cfh2N!FRz=5XA4GZ^5LrKKKrQCw4~=7ljr9lQsd9HU*P<gNuTTA&84ZRWNBYaB*-61aV1db1-QOa7nNQL0k&j5=`0|TnbzVLF@(X1Sb6s>;<lkAg&Dc2a|RLR|eNY5LbeB0F$-{R|3~W5Z8eA1e3M{*8o>U5LbZq0F(NGD}c)*h^s@}f=RoBtAjle#O0vfz@%-!<-pYt#8siK!K6Oms^GE+;#SZhVA93lR^VU+@gnFNFzH6{BJgSi@g`^#m^2=|2^@(aj)NWplcs{>z(*0p=b%@?q<6ri*TJM`!RNq75X7<2WH4zAI2ODEK^zK=0F!P2hk}<Oh!;Yaf=L&E7lOwih`T~ZgGsx9yMn7Ah;u;8fJw81bAUf8GKgP6X<d()^ac18_*Vq+P3QwK={4|8@HqtW5$G8(X%hGdct3)8J9ICYbQ^d(I0Qkw0J<7XItRP}JQ+be1Ue2(ItV-j+!sOIUHNalkGLJQ3-o(1X%M&z_&Wsg0O%+%=~VCl@Nfk2MCg1l=_>F<@N5L}a_D9-=`Qec@J0mjPG};S^fY)U_#lG#6!a>X)DAuczJegW5B(iX`Wbv5{2W322}<jLpP==?6vX)u#C4&)!K50vF1Qzhc&6Kb>x0BApxdD<!K7i}?cjX~;w0!EFzI1%68HxM@fGN4FzIFR74Uro@gwNZVA3@3Bk=DC;y<A;z@&eG{{(+T5PyY!0F!<Je+6f7mqDBjO6!Kiq*=k)z<ChF1);gXq#odc;9>~kQqaO+(vsj(;PMFKD$sIZ(#qf};93ac`p}wS(t6<f;HC)Tme9svQWe}1+!jIH5$Xdb?Evlw?uH=l1?>tZ^#}I?_eT&9h4uxL4ge1Yk46wrf(C&}gTa%)vk}Bgpd-Mf<G@S6s}aN-pwqyl^S~Rx+YrQ&(4}C~<={wg6oNP!x(ZAh0*(gnK@jhQt_PED2JZvMAczk@w}MHxgAah?5yT152ry|lI01YRK^zCQfl0T3<G`^9;{DJ~VA4?Ve(+ud@owlkFzFibZtyMy@lNPUFzGVzPVf!{aTs(Fm~<{U47?FRyw?4{^+e(o&?(RvVA3JrDd0f};y%y-FsUE754bym*caLvOxgzQ3vP!XZUJo$CT#?60d9gIt_!ULCangp3$B46t_ZCFCM^xF2rh#lE)FdUCe05n4laNo&JE28Cd~xS4bFlfc89uwNohUN9e*eO8$tXR^c|S=75FdkYXtE#=u<GM9sCUZ5J7w!dJ9Z?0el;L5kY(sdIC(E06qymgdpAx-32Dy3f>Lgh9F)CT?;0i16~K7jUes=4FHoi1or_qKoA#z76g;hdSU_mo%kOF@oVTCFzIjL*WiZ;;v3LgVA53Z4e(h6aWXUoOd11D2Jb@<he5-^r0c+8;57*1dC-Mm(kbA1;7JJLVbBp^(*EFK;C=|=o=|@<X=iXxa3=(@541IyR0aEhy%EIqp$)*KHNo}4H4wxVpq0R+p5O}L@(ALR&=O$M0^pM1f(YVV%75#R#95)4pgF;$Il!5~84$$jq1nNt*}&<+=@7*3&@5om%wTu08-m#QL!1#ooEw@4Oj;P68(auMY=M>nlU4y+z!ee1UeLN=(k5UpaAO2<D`-nFX$NpCa7P4j52zoQGyvQKY()?cg$9F3$AgE0Cm@LDLT7<VSAge&S0aeFLN|d)qrh9idl1A4(0DNEac~0o1cLYy^dgw_F8C7o9)kEO^a+^s9r!8uF9dNqH>tFaNlaQ4Oj-;~S{$4XoE|}(0a^k~S`wTAoDo5s32Fh8mI7x2XGRcbgVq6)dV#Zn^CF1zKx>0ZD}(cZb0dgzL2H3YD}i%?vm%IdLTiG3+q=1Yr2BvUU+(?)hkolS?Eiqz`M>1bxXu6NqksEyZ0h!HpMmD|zmwlxY~USDPlJ^I0aD(5BL'

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
