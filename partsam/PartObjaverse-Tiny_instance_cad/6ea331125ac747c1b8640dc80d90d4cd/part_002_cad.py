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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6ea331125ac747c1b8640dc80d90d4cd/part_002.stl', 'relative_path': '6ea331125ac747c1b8640dc80d90d4cd/part_002.stl', 'source_sha256': '184db88cd43b3861959e798684aeb3cd477e3c9127afe716065f9e992f62bd0a', 'input_faces': 1280, 'input_vertices': 723, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08143124729394913, 0.06489631533622742, -0.07617220282554626], [0.08144528418779373, 0.16022977232933044, -0.010196216404438019]]}
GEOMETRY_BASE85 = 'c$}r2b(9oG*!6oC2(Cc_1Q;y1yEhtKgWKS4i~Hd2&LRUWx~$<&FYduLz(8<G$i|RBzIp22o|*19e|+bC_nhb4Utfya?y|0`?%u}r;>Ay^;U~McFG<Z8wQFdaL^3U{HmqC7kX~K74KCb&;K(2?mGb4s)I|-OH)z~CNE@b&&eOHq;4UF~$~*E@>|QocK}VkM144#`bn4%6KuFha;@9fbcW^haKe%V7f!(~vdCL?pQP5E$UqQ!M$N%ytiT4!T5w~|8^{Ok`lATrLc;D*fM+5yEWe$q(ym5Aw^5>m~e`(1s@jbU^ue131OC3`AO!aI~{vHGVjFc*W$AI=LEPk)-Djy?#!sQnKN#p_Xwb?UPTl^D-Iv-cb66$=M1-HY0kWA&{*!5<e#ebS%x5}q}HmhHLyUNGYNe{F5Rrjj%_k0LZ=kMt@6n=#jDu3tOUCS)~(y}VOGs&Y+b^Kuv{CR73h_BzwztZBjtg5cdy|L>WbzS$I@I$7k^E3t?bzA&PxelxI&-S%CAALZ3_#>99^3)QPU2pMOU!EPaa9tI1!v8iI(pTxV(BiY4T}_KEQP&ldg5?&f((7FlFSPhoD<J>jR~D<|nn~d=pQ^6cvAOgji~mP%T<?J|Du1JIeE8ulRC;IS_bV-a*VmSE_W6T9>{t1>%eB_x7o3awI{1q!f9K<0cPjtYSyi5{@B6teeyv`rJe_|Us@$|;Z{R<!rmokcx3T(TPpN#|oy%^v_~B30bs4`zgjxJM-B4etW^YyX`1%(7Lsj>v@(hXEWbr3IQR&@|cu1e-3j8^h&>qsS-E8q+{iLqfbs|os*Ed~+KR*-7?R2h%7QfYDRbP&KZ&ZDG%AJEh;#*bzuCgtx{`G^ZoIUljE<?F5g1>B?I)7)jq?;_hv&IpX|HTelR5=`*0>9BQbv}B5Gn*}bcqeuKjysvRspIAo;k%RbdNB_8{GQP&z4lC3{oV0$9LuLB`j=;JsKtNz1nuO@0o6|Q^ZnrW8HMp`PsBote<~x|&*({L{~db6PjnCG)4Gz|;&&OP>dTdIfodnNxbCd?2QjK13ock<@i#dz?)7YDO<!sp$~mt4a*IFUIL5v7n^n8go8^Pw{<bQA$HsmeE&hSws{B1oV^ul3)@6o2q_etSZQV|*UonBYUZY_`RsP!5e|9K;;y)NadxtN#_zyx+U(;@3{O|Sw{+S-C{N0H$?)m&Tn^ZpT5@Cxhe(r?mFN?l%Tm0R1aKCsza;Ylk*>Ui-+p0XZ92cy9yWy(bj8co$eZ+C^3H%HDRDC(N6meVp#cfr6d74jB<!|(V1pj0)RWHV<oK}C%b&Q93hpX~;r;UVv?w%@tqkEjy|8BG@e^=UCs+^6#R>7ZI9PNL2C#&D^2JT<EcdPzu+@1yh_x+ag^!aOc;r{68v%=yZY=`sgo7`>jKQu#mR$8X+o6f$|;eYK$d&u{2vBm$X8pe}~n^k|;^NfQ(A-*~v&zfUa|NaJ5{;nM})wu0>G#LJd?yCIt!>!yF|4RalhkdrA{SO@of9puxkD6RrXYmtcROMrQ$%S$**ARZnXR7>Ni|2$}{9Dt}{;NKUQ1w1tx74p^!KzS;A66aXWcgYvEk5hr9d%}{#qak_osZr!MBT4lnJdA6)PAoz|Ee#yS^TZqQI-EM71jB8dKG~`%c;&^tNll~#UHo@ekFI9#eeayDmVSF?;|aK*?Q`FjaR>`aoDjSFZ}FBP@eA+gj)Qu?NOe|i{rkTD>wYJKO_C>-s>zr#|=G8rll6YQXIz5lB?Yof5BAbU-!rci+?!??dtKb%Pszj1sH!Gzr%gDepdGDu9y$Zt+(9b|6U5?lJnsvi@z@(+W!yPLoGi0mnV4%)xWgD$>BHXh3iW7*=_N+Cc^#YNMp=bV-v$4+EnGQUn(<S`7eUuKiQ+|-H6Gt&Ei*Sq3T_84%?3Y@ID6qW1MIBvw5ms%KQmG?t<z^+VeCE)cM4{g8%4|>POD2iMCt(N)s?oaJ5tI!PxGB|HFIC+at>@v-r`=P!5Ars&?+w@54{{Gy3(0A<HfP<tb?Ydn>B)^z1%EKLq*nzU=c0ra}Jqe!~2=&Pn*kdZ54j>{R9ExE~8Ys6NI|&P#oM``5UivVQgW2jN%lj`I0!80MeL_QnL(qvvVWO%^|0GPJ8jOE3=^wF!Pi6y`Y%9?Y@$?;omqbk}LV)#Cp!Ue%-L?=7mIYVDT5=loFX&|Kx?{&fNTeEC)W+Jwcbe)VnB;1?RL>e2J$cDTi#kqP~JVL?@o&e_A@AHR(8^YpGTi$CnrLA0xu3oL%Nfhr%z&_tLY?i>Jr@ddQ=K4BXz{<}VC=NaFt^p5ZQ!XI8lm9rk3THP14;Lh+rp1}2{O*dDaf4;WxuYHes_4>3MEq>@Ltb-c&RQY=jwPd-S!hL*&L!H0lZCUs`Z>aKj)ZDPe;-?&n@{juq<7$>nY=<0AGM!cJ!Cm8P)^7n^@4giCE&fLx<$1A1xW#Yb!ToXcHjK}Gl3B{Z`NwI@-~LSmKWaASbs6z{UDHlPD^0sxoxi70_AM6wr}FCj^?O6q`5Tdk;d9>QX)qq;d~*+cbDlQDrOHSD92IS8|551Iu3TH;e>-2Dk1KSL%Ez&9BmCMWaJ^^4wpskJt0=c&@6~vsPw4|c$$9i&j`Qwsdcv>tN?n(J<W{7`UpWKUwP%Ss_EhNv-&qXld%W6g@j1R31&S`W_<65my^yXl>i1fE_!~OxQ~B)A9cl6Z{j7ekv9qE&cJydtDL40@c`?u2T_66i<Eng&7C)<cbkwN>|6E7R4?Er3YVi+rRp;-jS2N1u=l&PvmZHFRi=RHeIv>}V3n+&pCE;`2GxChX{=m~h@H<7Q>oV5Xjj;Gh8maNtu^;;_rmuJS&QSH<aE&@2XGsUroA(jDHPWB{7XI!XSeKnku*Kr1Zi;dq(OQ+WGkr?<9d~0t<U``E7XQ!>SQl?<kN#3AQFLJca&o<|Uy0B9dW`kR=cZ8>zt0r)d-dkmP(JTIsed=eNqx%mr53+<A)NoXzFRE*+zYth6*SOJnjC?@>PM94r#9OIeWQ3el-ssQjH|z_M|zH9#-%*?y%m?h=Y7GQx;gHfcSgb=Rt59M6{(c(KG7Kd#1WW(PEHYJ@gHPR*Xzs}qpsKa@*UdmxFhO3&H1Y78*dA%^EBtHu6C1<K50pnzdOmGNQ-~<Cg#uWI;;GR2|3|^HA?00<~V8kdQ38ugB$J5een=}&zl@L|MeTJe(ht(zwzJddORC?!+(}i<?mP@zRlwEy4+KCMO*x;QRo+q{@otvo7Zc!d!WWs$N4Tu&+*nVscm$iulMeu((7%eVEm0=2<bnTMZMR19c}Sj-p0HuXF4?x)0<_3pSLF3)vW{DEk5^K4A!IPOcMBKM`8T$eA?pcXXfI3rYBeDqs@7NcK72PHEuZBK7D?HLKv^^e2w+U+I{e!Ey6tiDdqz{ziJ7zAI=BdZ@0m(mk8?%&v)S#fAePaueqZzo}>+f&v~hqJ1*Mdb6#qE%B;%AnP&+6<tuQ#9Oq46FS-WT%W+;$6&H?ju7h!&<DSpo`2y?TW`Ci6Kb?WU;V$l9N3+dT=U?X_{Nz(`UkLjrBGA`MEmXhPl`k*a!}18E@7EjS-j7RXsB}j+!FM!A{>^`zrP^8lw(#5ij{TD~C)DpX4mE&(`#1E*BJb3E#^Wjg|6zQL|4m0lTm152SZC!6Q`co2_yglmzDj7fO<P3-`bM?>IRAgcRr}G3dXS#$FV{ciFmK#=ep_HaGCE>j=iU$k|HT{Z6P`*IZSiZ&#yWRZY4nS^b>MTJ?<&?z&3}yD)!=iS)bf56Vez?t;@);SCeYW%ltI1UY#n9s)67Bto$yh$AMJhx?%Tb<ys_etm_Xl{dlKVYnl&oDBYr8Qe;teQq;(B-zt$>$QTHEL%|9`o+)uJ2&^H>_Rrxq~l~nsy`p%a~zo`V)WxfB24)pa2FEQ>_{SND~yN{86Us9~sQs#`Z_+N*k-F7&La$aM=pV9#HkR6#KEdHZ67~h=zQNM3@z|S0t{nY}xnjadS*TB#E5AvD)5&JE-XTVR?678)<`ACa@<pb*XeJ$Kaz8eF-|9PaZGCjiLpX-fz@|%0OA2k>XzwltR^F66|1p4}?Bxs*=DsUgUHPUmP>nSiHI?y*>yhr-ra8<va8%2?x^BgDF3(j0Q;d8!fxJs$}tn=C}%!^0G$2{}F8Z{qtf4mI8@ULh;gN~^5TAkzY*CjwZN%1De;(rdq^*%|*{pj8B{~m{V)V68ZuQ(D3zjg(z%N{0I<A(NZGyHMovCb`?Dmu_N-o8P5OI#k~SldNNpXxl;kB!~a)pbpr4gbV$tZRloRO5`NSXKCo8}CGa+@XH2(^Ufg*ru4ba~<kh7!Us8!x*<mERC`FQ=AyL8ycv`7LTxx8ybgw<J4oK0)73{8Fl{dhtE-uzn?^U?hCmx<(;jrvu6zaJ(+Pn{V!pizPm2`lN&M4zs?(D@#ogYzSgm(IG-j(;B)`MT>tufj`PmgqEUgqInF!F97F#-or(G9Q0L?5c@X{RL@b^&EIEPpuWyUC_`h{g=i|t59pzR&0{-8@D4&qZQGvdmuZjA-j#OuHe~Dg>^u{NgfBC&?9QNd%3_rG=Wu4^;9RQ#6BG27Y(H7sF|HO2}xO%K7{D&@#!?$-t1^PyoR5+jN@zBm!q(}PhXHZ|4r{g)=^F;8uj&{%Aj`iu%!)pEQ%GwR{+h5Y*`P$(<@UJ$)e4G8z-6j<N%7^F|d>-fgbqw}j&HHKksZ&(>bn6K}(KU=GDF;up_#FSW>EEdIo;Nw+#}2^tMs894!jU!${5$<{UoO&Vs!Ct>u-b=n^{9ySz4p(w_}%Z}zVAW*b$zS~e|s(5H;;uZu=w0J){@7do#zW(8(9A4eaGiN$cFXW;{Mn-h`osY-M+sd|LB#AE&il87-zU2rC+T9pZ8NOew8H_f6MFxX#W@|-G?*7=W`HGr9`O5*Yj2V_{Nh4jZmI9d%&++6z#Bf#c39w&%d<TN0U`OK7WAxx?PS|>7NanY4OKi!Z_9=zbb#{_|))|u15NbJ?2{c#1+vFcOF#Zo?};D^n)iGRC+z44(2Vvnc-I)hV<1(sq%N0DUS9#>5)qB<T~BwPjsQ(7R9_p|FJ9fSHkMC9I#K~^Yb>qy6j#9><2!$hx%W1U8UFEIhR;`&r7WD+W)0~pMGu!d_K2w-o^7!_lP|Us{Dtq&v^*nmcP%p<?kNbb77VLI?pGi7FGF=>vbMTy{5{4v<J7VHhf#V^7*!Q<rsJczOCK*d|SJ9<yo+{%73(f$DK9s?fvCSb$6Bj=yyKf-tWrngKzJ@sgA<8^>^p%tm~9-8#jEuZQO92$gO;HUaDus{*|j?dF30!tK<Iiq_M@<vtGh{W*zF$(WMLWw~ue8ZyVnnr^dmzkCXKEJsRf83ot&Lz7hK`#(BqRl;^0Y$mhW#+%L-E`Mc>G{WHd@{D)#c(DShMdX<jrIG4E}PG7H|7U?ftSLNx>dIRZuG(vjr!<)WQ{BO*YE2mfMCfA3O8&Liek$&KX*@3>^*FgGrlQ9m2j70iXkCFZ|)@7!z|1lcr>tVdoZ!A{6k+LNGTU#-X6<fVg{eRp2$Z;qJzU}_yS-cOv?S7{%OT7v0&3fPTtmqBjc3(Dq`~BDS_3WLFtNzG!pD+FD70P!vtf72&<Rav6pFfn{f_!ZA4WGaDuFA*B{RI8^A>?D5&zQbGqJm2An)eO%H}VzRtbF@CioUTc^9iL<U#WbYv+FD0K7TWPBUM3_zg~VB{6aq?f7^W0=Z|ix^4D4w#Qd;#f-Ne4+kDmZ^<(8!{@UsIYToYodA;)O^KH}D`wdh1yC;l8IrQI){O$AnY$xH{)&-`oe`%|Juko&h^4;&xBfV|i;k<GczHOc2`jl&{@@?xH{dxiTwsnvZ+gADZb(7EUIZ<7gXVkB_-dw}CqMWVkGSfFsEJVF0aN+zvkHzn`ulwj5Pb#Bb1s6em-JFc{_H`wFeMfxM`=D8v$Ch&=y=~p9y^eryTj#n~9fWUN7n{EEZamI^_&e-l4?VUuuw6N4t-x~)?|`7vr=NgwXmVNk&O7&!zipjv`ugFdYTPqYY*-rT8;KttQ`dX*U-Y|~uaVxiKVbTXHdxh*zP~s6S2}H*^6mQ%^!3ZvFb)(PiFyex3V&@y^cOy_ao#JfeEYtK=^M^U>ipg2{b*Mu<YU`!G5!CsuVSYEDXltx$H&S$E$Le|z;(@fjO(3U1L<x1Jf?4aGSE*?J;pkvTRoh=ZGXu*Y6yJWew67O>wZ+_ucsT0b(tQ{^G}HS?VC*1mm_W;&L>4nRSq7Ok3RMy^0)7gC43Cuwx6ag{0sTp_uowa*xwijl4iiVuT`ONmCm-mXZptKd+PkP^)LARvMSQQx^B5&Yl|Dfx9uw$eOn-(md#_)FL3^@n(dL^wm+#Y+XCOdpE)23zJ32Q`(fqV_e)LR9RIaaz0m%zo<lyi{aEMZ+wjL-!T!09_d<;nZ;^lHvY1!2sixNTuIIlay=}kO^z}QRQSax=V;?WH&31L%HyHiy{S3@Q>i1N>Q79hD=lXLs-*9{xiuAVqXP^HuH|}e(H!)tl*{FQ`ez?!K?R%TP(d<6zcU-(ki@&xc+W!zI&VS8L_~yJNJ)VOb!ww*S+rGW&>wAu%UgjT|73dp|4fws2cH@1XJ2&888HW6`V1LFn>u2O|d%ocFZO<1>Ur*=2_<wE{o;$dcMJV6){KDriOpozFYl`_ylT6CDKOZrD{n%)A{?4JxFh1NXjP$nWFQ%`D55@f@v^B=7vmM~up6{5x@$wz|X}422pHY30zwJ4c&$m5qGJX5=Cet_Pbq*c-s6M~nK8)wrbKpEL>_z^z=VGR>hxJA~cj#z`t#U`IW7~5#pI>Y#@}GYV&yz|{QNI1Tp6Tl)2BVy>Z^FK`5f>SFUFLH`(>KrGRlGNz|E+2orH*aSB~9PxzXa#c=R{h}Xr#A2_terZgKv9I>OL6;-~L>+(SGD_dk*XKd4F-QEQ5A+`ZMyeJ?Axj<J16kp6=?^@cipg0_;=Ro-doeKK`6a@4A=)`)T<SBfahUwR1@___pWWrf=LYfquH|8Q#;Yl?mzX&)H4i_MF|}$PVB3yk75C0O#4k`h4H#KZwG*gZt9PmBPr!_MU)iTPgUq_YK^?R>Apm{^`k%_eGs&Y9YPty#>=ZW+t_)M~sqnk>2+HgXtS-5~F>77lG%9$(z8BAA@mkMHGJTvzExm_MV30Xb1TA_d4hs<ENva7Uc7Y0-cfG_MVB)x4mcL^X>1M&^PY?rq16;a2n6GmvuvW`}-~Qjrt97K85e1y$$Tkda=Gg<LogR={XP4lT}mY;MzWy<ugFt?;KwW;C<RM*hl*x@8{6hug2m2Xg=qC5smb=_ky&-2f2S|eZR;t_#}MW`$(p*m(7j#cK$P-+vU2(_ER49I1le(dV1Z5-(#jaALkgnCvUV&j(th{ds9Wz!neI=W%_#f2bGWBrv%2U#C#56f4^%{5xmD!Av?-5C*A{h_AQO{w)ezL-$+;k*OhoAp0n4i6cc#<#;3d3uS;w0?_1wnGkqh&XOzGG8`@j(ewOR?y)U<RAbi{Vb*8V6IEs9Vj>2=M;lq*M_P(Fbx4rM@^KI|@8TqEbx4lnj`ud6Vs+~JH4!eT!9-A>Gn`IwN+qEJluzl*B2fDj$M*g<<Ax+=NR|n(y^I~{EDg*Yf?eAflzA<wi=J}Jds^^8CUk}Du+B5gH+-Hu#x4jo?`bOdLSl{uzdPgZd7qP#0>RNY}?aKQ8s?WE-ze?X&k_P9=@41Wu_^!kL-mK5Jy*F$6=6cX|1^ZDxKjs|9|K$zwJ<IY(ENAO`yguLd9<OKM3!LY+3TRiyu^;Qa{~GCS?+Kf}p0zH<?SW6x9`?i`z3n|@=e!T_ZSO6+uE)dk1N(c<^v(IRVZQ&PCq#PNd(?VF68N_Fu1#ORJ_qeE@{aPIacPl1$5rPUe&2LHGt#g9i1DFx0<06uWJCV8_rra@?fr1mH`>lZ{*!XA3iS0nL$FT&auDwchvh&%w)fsm-$+vr=iiy%6{h+Q>22@T`+VE``99zF{=Cn(y+3dIzV+JQ+1-J@Z`@A(2fiN}lMg=c*G43s<2YUx<o95<?+fVb-6Jq>3?7E@uz69Ww|%Ez`o`cHm`6Rktb8qDW!Ag(`v}uFvL?d%>)}b<F9ugddfRsyKHvUb27NtM9Qs#neD|m2#y+zBI}y`2N?pKwpmi7Ak2(!PdfRs>rmqL5NB#2qEaT!3q_=(NV*2{{WaxJj3*&pzG~<!p{v8c{qkmhR{~~<1;(k2^>22Td_<Y;<JEpIf*^2g%Wk1@_iP=bR`)<hR+rJy4ujko=`Q)T|mh{G$otV#L-Kxsp`FORZf0^GmnZ7<K1m(v0m}gNq(%ZhDGJPY>X|$h$_<qpw%L7Y$Fu%_-eP6xnAMhQ`si#P9`~J)H^~I&IUZ|B!)r)Jy??`X^zRdKELNzhYq~E0KOK<WK>22S&`Fz`VZKiMT@0sQ4^V>wCzV6OKJs$pyeC*%f(Kq_vLci|$Qq`AZ&bN5}Vf((%^!2Q>alfcMAM32j`H|lC{h;X^?M`C;P`xg`r+Cl<>22RF`h44Wi>9xytc`Jo>k*&N{a9zAe0VRRZXe`h|GtvGzM~fU5x;}>?CFp6_U||8>s^*&zGpr!xIP}~ZQqCbeA{=Xrf)va(g$>RTl_B%QJ$xos`7V5OhrES?_22`%@3e{e_M_DcHDfVw|zfr`o@Q?7?%z|SH5%qX{5J(pKJQ&zKXLT)<KSimyq7}{jcd8L%X9t9>jAu*Ox0uZ~MO3^o>9M#`SU?q2IcV^tSJpP2Wg53jM3h6x?S!y=D1Wznk{?_V1?YoA-CeS4B4l`bOW1*dNf+;r-i7?~srE`)>M1j>;&{WYy7rUI(f1)c#$$>Fbjw^Z9aS^wU-eklyyax#{amFQdJ^io?9F82%oC{rh***GH|wcomBM7T4;ONN@kXp1$tLgYmW%zH2b@<U)Ge_xq-=SA2;4OH@buZ_@$kZGRuY^!47k(H_nv$9FxaJ0ZRO?+?(|pJzt>mR_QK$I}p`xBYzs)7OV?LHoSk6Zi2Z!;s$o_Y>&r=Qmo*^P32yxBcA)pKtrS4W@6b>WFe{de)L&cRWRVe)S3IOCPb6r}=j$Oka=l;QafBV!p9H7U^w&kHYlz$GxzQNLy3o<4JK6>1}@>!}RrZVJQFMy>Ol@?pW%}{QDcGZ`PM*_r29e8(aPg$%?&)LtGW*R-kE#wX|CIP62;{L`?ZH^}qiFNw1RsUw?w6Sn;w&|8IYTB*|C7n)V{dJMHtv7HTB*1v!#zQ2!t=qn@SyK|V|VK+P5m{y@$j4E>&*pWK%^lH8X(lRA++lf01Hi@cCLj+%=+j$Dv>AP8KLe9{}EsUxWe$Ro)^s5{6*$RX4yatL`aLpYlHbuc)Z{7o>l9{C$`BWh1_Bl2KsTk>FX7iwv87jil3SLAZ!q*STnq&yaW63`BwFod^xV-|Hbbqjemc^);AJdeDHYLLx#BfP`=doO!qJM}DiJ2{MMki*D}8NxB%*h4)*HOME(7pP~+7sywsm&sSjml(q5s5{8#$dTR{NF7SuK^{u(Pu))LPyT@#M*e|ZnYx%<nOuY+Jee9po=jdDP!=m0!t1;-o4SI!hrEKkg?fU#g?xZ|fqZ~`gnE^HgnWp4iF}B>jUjxBdX9XGe2f}NK1SXYP}Z9m!mSv>nHj>_sYA)x$?2&5$?3?6s6UVsk^c>XRwhdbf1(y4O9=lRgb@CY|2~=g9k~;ACAkxMI&~d+I(c3|{mo+tkM>3ZYBB0;axroh>I!ldazpACazk=E>H%^)a&PJpa&K~b>LGG_a#QLya#OO-5MDz)MP5VRM?FT~N8Ux<MBYVSN^M16O0MRO_|#O?R%Fr4<W%H$K?vbLsoBXA!oN_{ktKvZ)I?+n;oDScH@6wW=c%8_=gG&Zf0K`scQS<EP^CS+;jwTAwy{p+4CETr>Es&Z;naEL;p7R_(c}qaXF!{CGK6zV9R)#8Pz#VHgfCEwktKw0P^*w7gzr!rk|l&6QQMIvgr8D-lO=?IrnV<b2;ZePB})k3r0Qe|;Y&dX;gbCKHRO`y`P6;n`Q-J~UF7xTRn(>ARphDEYUHWp5&><x1Vi|<_q?tJL4Tr({}YdeUr|$$Q?b3jVhA5$2p^{YNj^;8OZ|nsm%NGUA#WnDq24C1A+MmGC$Atcp&lnMAupirBrhP(VhC@ez9DZTKcPy0Fy}MEN!dqg1pDVd!sV#LgZ=X*;V#q(!T$M`@L;Ml*gqc=ZbZ!)?4Q30e-qGW%=w<M%m)WkM^N{XN03KRPmo8E$51bj$B@TSZ;;24UDP{d7kMJ}5qTncGW98WGI<j9XYwTS1nOP#1oC+5P4am1Sn4J6Sn_Cw@JXulx05^;F33JOKiEH?7am7lAMBt13ooRu3ihuTglAHx2K(0+!hNYFg8l0e;rvwTZ|3?%Sk^aYpETDy!m=J(Mh&H2BZrd1s6Uaz$h)bp$f8Hc$-MF0yM|2T)l@;yr#u$_DMQ$xo+2CM#nk2G#pHg}q2zvKC$$&ZNp?{ul3nBj)I;P0<V-;b;VfRw7zEwNWAXPfgvU`QlE;xdQG1a)kq1zRk_V6%QkRn#l8;bNk&lpnramW&O1b~cV_}UUT!bN9lA4BGl3YH>UuWeR!ezZtoSKB1ikyV}P=iXnK4b{*p&H~p<muGK<mu$L)PCf)<fc?7xhXk>>LQ1bBdG_-k>qcJpi;-*Fof$dgd0$^kQ<O21^L@VBZhE8Z`7w|pk^dzAaB#4(r&gfg!@y+k^7UIQ9F^Fky}#-kXw_dP#2P?kfW$a$Wi3m)St<s(pH31dn2hgk~4%8Qsa>ml7py8{LM}ASKdfT{hFGD{581<LpTpL9yt#=Cp9TKCpkAYH90rAkT)t(vr$u%vyrn<lasTMOEHA=Q4^B$kuy+($Qj7#s9%xOkuwIAMMj2j0dJJ2eoIYB{+67B`ZYNRxeB!ixe9q6LwF1|4|xo^J2fY{JGnhIH@Q8z3$+lr3wcC9S&v`{&+^8P-Z<lpQ0gplD7gW(61f4n3^g0M47nIJ3%MA%Cbbl~CV3S@cmXvZc>#G6H3NAPc_cL*c_eulH6wW#c@(t(c@%kSKpjtI2rtp(*#z`^YI*Ya<Py|x$tB1Ys5!_L$c?B~$c@Nrsq@Hd$yXS{7pY^&7s<z|-O0zvd#UZod&%3WUC7(XG1L*{81g~tEVAes@<H+=hVX0ZkL1_nciwnUy+-|!e2u(;8cN<k?m=xp?m@0YEkmwDu1YONu1aoBtx0Z94x_Fjhmn&9A%s8ETR{Fy{y?2X{y_enI+FZ5`8Vn?@^9o{sH4cgkmIOR$#LXAs7uIykUwhvw)>GG9N&8#DT1Jzcr5-VhHy*j_vDu38q^Zx8svJ^3gmj^!PG|N!Q`#fwdAej8`LZ08{~f&!hcaOlK&#Vr5-20CBLNZCBG!!r*0?TC*PsQknfQ1Q4f+uACd2o;{_pv6H#B2C4|#c-;pJR9YOxSAuJ)Bm-E29yjka^Z{ECxZ}b0MBi|-RQ8#G*xrFc(Y7fmn_YiJPt)uzpD#FdERW<+IMz}w<x#ph>32&o@Y5uvBu*|JQlLySTl5;LrpInzJ{i-gHg=<qkkR^m`QGX{(2-l$gMwSq+M*W2>A*@s5$P&U;seh0qgsW3Ok|l&|Ql($jWC(vB<nMdmGlc7K9$SZV+dA~kxvsFxg;TJ<nsZ~}5Nb=!KbID6O0A*!=ib6?sr5AfTwQoNb+G22+Y9fZZq@v20pW+#8=8OZAS`PO(SJ1mT0>aYBE`uCseh3rgukP{B})i@OMOX}5Kc?IPnHn=ih74EAsj@#M;4X7DtzA?3A}6X=RpYJ<iXHV<mBXv)HdXb<Q~*+<R0V@YF%;&xd}A|xd}OqH{3zcRn!z@3E{Ot2;tQH_qycN<ObAk<ObwH)HdWn<j&Mm<j&->)CA<R<RnxnyCggoe(a5{)XmiU<jv#=>T~i!>QU-*@=<aeRq7y)$HG}zFBQpI$+f6G$hF8Ls3GJLWEZsw*+uS7O+)TZ&Jj>gIe09*-W$EBJ*aMS4{|r^Dsne+cj{VlcXCgL@H(p0@j4z0XJNfJAZH<WpbjE;AdjbZCXXi%qn0HPBUh&;Ay+4-r%D~C=dtkXfOhbjAspk4`P3QIt>hWxnbghXndG_D2(sC36nlT~8E-^We<Vkf!>Omq;p7br;iKL-PCZXOO+HV)Lj93^g?y2EhJ2BHk|7*RjUdO8H!_3=FocItqsc?a{ixyOe&lA<4diCzN(|ve)T87@<fwq_k75Y#_Qo>mX6kYBX7YaOdGdbpVd@p~Ve&!hMe;%NR_aOeR`P0w@Lp;xc`tb<bt8Evd5JfwQd?3tk~gxfTQY<*F@zn|A!G+REwvvxEjb~z895>OOAxdYSwi?@5JI>x|9ug;FnJO+iad$DoVuI5oV+%m&ek%7XL+L#wG4F`xeU1`bu+mpxjA(|xjDHt^)R_Lxdrtgxdpj4bt}0xxdL@HxdOQ;LwGKAFL^H6P2EX$lS8RX$f4vZ0c~OmL%6s%{t1G{<8f7TJaS5EOR{Jta!T^AK?vdBsSdJ)@LOtHvV`yhYC^Jv@GYven_CRwbJUOIbL3+T;lHTTp8n#oaBjA-N#xw*j@0Gkj^t_7wd85!In-I?Ipk3RZEh4pIFC2NgP{AVg~$@Zr>JGf62cd$HOUgfm#NLk62jN1t;rI?SEwz>62d=HYm+5}Pg5(9C4^(CMadGv+k+6odHL^i$$80Rsc!OE@&aloc>#F_bqaX~xev8CxeqyCK%36TW8wGSI77Wk{fB&&e2*&a{vMBoUs6+&Q?k9kWC$N(2p^>WPCiK9Lw!r$L*7VzK;B4RO}#~4O<qntM_x`|Og%<kOrFmWj-mcVjv>FMN`EltEyC&9M>+=k=Q+aFsnde}^CID4)H%Wad6e*Y>ZoA<yi2$PHBYdAo+g|npwF1|I$@dj^`!QphLih{`%?Fl`;rGxPmu?Z2U0JR2a<<UFO!Fohf}YUhm(g<uaJk42T^|{4<h%co+kGv_oK#=`;mK7x08F5dohI9Q>DMH=do}O_QA2i{&~A_cj|&*|2$vVMV%4sUl$0Ep!Ny&uOozOQS$}+*B!!HsnXxfb&9a8W6VBju4{y4-LsIolzN7|l)RF9mAsO?fqIX;fxL_Qk}P_Ne8RgHKIe^!K?vc>)bnHs;VNFO6a+oXWATOiP{&fwlgE-LP|uMkkjGO`kjIk;dZPt(C-nq*C%H7wU(UNUL%20VxGl9Zxh=UpwF<dCxnq$3Iy*9iJ9wiVwF0#gxdJ&>gUa>C29%5N5O4JM#xm+6@-p&C>QVAZ@-ylaa?&7ZYU&fRgm6l)CJur=;Ia4*7{a@#N6EX$)2NHc)5vY8y~%CJjTyons6)sd$UVK$k=mC!gxr@rpSp}ZpM02ll6;u_nEH%tmdj%v3xClN!i5>aC8(*%CCKHdDaqx?WrF-=T81H9%o_!$pEPJ<vV`z;s+9Y6hVT~ZF7g)gAnG*oAaY%58**K8HELsWHF67v@IYz@@<8%<YERAI?}R4=)S1~&g{2?&p*Ep*BsU?qqV^@XB2T8yCr>6vP!E$M$Tz8v$&Xo=!aKaN(Ho_L5W<D1tH~0=`KU|D62dvXTGSi)y|GzC2(P2&B1;IbpynV;2+yHrB})j;pk^ma2+yYGB<JM$%w`CuX9(w|t|sRtm!xhamn2uG?jTnu|G>Hvjiv4&$C70X+re@*$Fx!$^V*TyPz#aUkXupnkz0{lP;-)7kbj_NC;vchO3g}cN^VTeL2gWLLd`{PLT*OQPi{tTPAy7qPHq{5`-Ny}YSAG7Jw;gVIYrrC%zM!0fW9VNi@J_ni(Hnvf?SrIpE`$}pZpDV2KgIuTIy`_Y_=8Q!ru7K8>1P*U8&j0UCHgJxybFvov8)Moyo(g70JWNGre)i8>hXok~)*Tl3br!kzAi#njxH(T9BNToQj%@oQj;7nw^}O98CR=9869`Elf^CPU8&+wKBCZxiWb!bu@V{`2s`u7_}?;7<o6f9eFo7oZ6WjPL8GyCr6X_Q)iNAvaI(rggp%5SJX@7SL9#4@i+A<^%D6ic|CO{c|ExswLZBUxi+;lxi(p62p6ShB^M=UrluliCMTmNCMP2&pazo@kTq%|&Hp1DpPGgopPWMT*L@0xa3*gQr<S8S$mPflsg=nM$!n-{$!o}$sTatX$$v70-%yW{-;iHWcavX`f1-wye<I(aMw4%m?^5@ZMLp!Z<lrELa6;-UvV?Ft>aS!8;cP+vwk0efoF@qLF3~SM7T=tk3E!k%CEp}RP}ghzxq<LxYB$Y4mk@46t*!az9>Ptiy5^s&2=`$K|3EED{()SbnpyMTPlZcTlWG3@uW(*!0?mKF7EVvqH2?iwe$3B3<CD{pzoDkk{NulHerhJof4>ketNGimd4Ca>`%epMHEMCqKUWm4OD(7Q=a#~Qs0}s$TvT`qb&ckqy9!^YUe^3`UExpEKQ;f{SXk!H62iHuZ^#nDnW-<x62f0oe<Di=C!pRUO9=l<?=D$X+Pd&`uO^l~n;=aMB2%OvP^XcnF-<T-xGO_=3`000Rr1ZqW8pd8=t}KEolfpT?o6FV?o4)4r;wfGP7L9xRJn$!JQfb}Mty1>sz$CuZcGg(2lLv5pLz31=GEVV5W?REL(7vJ*9!_x8_)mo^1dWBU(~MQ?RPcMAIu;5PC(O!bqg8Ni(fO_|EKk{=fM9t)ti^^Bk0EU63Ba+-g6FC4YTS5Ir@Klp#;q'

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
