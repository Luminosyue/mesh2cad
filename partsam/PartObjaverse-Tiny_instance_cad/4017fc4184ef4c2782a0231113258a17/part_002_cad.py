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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4017fc4184ef4c2782a0231113258a17/part_002.stl', 'relative_path': '4017fc4184ef4c2782a0231113258a17/part_002.stl', 'source_sha256': 'd6a7fa724d642cf6139e0a433373179d4192b020d48bd234784ef58ce036b9e1', 'input_faces': 744, 'input_vertices': 519, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16606375575065613, -0.24765031039714813, -0.1277901828289032], [0.02748674526810646, -0.012507498264312744, 0.23338842391967773]]}
GEOMETRY_BASE85 = 'c$}r21$0%%yTwm{1_~4>P>NjK0>z<F$O#Z!0xboCT{J<82Dej6u;Olk3xN<^izEb2kf6a^pe=B*;!@lSkNNgad*;91TkEa&vevBqyE~JaZ@!r`$1VgnOqnX1fuH<_&+xa;ij_4CRni;Tj6q%dhj;JXbwKIfeTVuOnZ#E=$vUe^i^jpNeT+fI@S<J14(Qy!XjNCyue((#>hCJrtxx~({vCUF=+nPTSLN5~*lR%7kN$wLj(xj+{9LSJ*{}Rv<%|2fM!NowKWRUPV9yFXxc8%4-}#<UYCh<<bFafUUrbGM`qqj9;@eNZ65qJraF<d~tCt7l_eb*`m--vqh;NO)C%*UW9%<k1^w)N!t|@oL_tYPPe&5uW`bOnT;+xr9Nc(o4Lvf<{R%-1V{s-Y-k3{>^C!n3q@XbjPdOL+n?U8;THx=JKyv|AS!=6YyR`xoYZ?tKLcm@TDZ>Rp_sC*8&D($=aRYyE~{SeO|O{INrlVak#&U_{9m~|OX{(PvPz3MTkA2>f=>ILN%-}v=2v>#ps?U#SIU+RCgM(W$S%k7olmwF5TdQYiuUD>}|^5}XczOf?Ui1>DuSn0R))&0)+t@lkNPNVf@)PKDm^-p@GU*qx^@y%2_#5b2AZ+6{L=y%r-hvjozBF0r=FxqK)U)r~W8`+}edZOP?rbr&F=(dticUt&X$uY?Dt4Z4={_;J<_Z*2p-cn;;T%Ee3{gqc%h#H>$0qXB(hUxyfwBb@ewvFz;ST<SJHwL!U{X>CMB%Vyc@ONbPh~Awg?c4nt>;B;!(!M*a=6}>*B<;KU25RkFZ|=-fz8O(fufMS#`u(%A9#5^N^JV;dD#7;~Iv3*_FYy?kSJ3_UcLqp)mzRZqYTIhjtS_V=k6&@U{*^frr&X_r9#5s`i1T_rJ)VY#JyO3*KE0jdO(lMBHTn}GCyFi{A#r*i<<i?XYs<LIL%H<&elH|`*Vb%$zez9U@7&L_U>ybyko9KWX^eH77QQvH$|2E04`m&CXJyvguQ^@DYqravt!MY>W>}vu((B_Y^F;Ds&G6OYHxDOD9_(7F^!AsxkUUs(Qfm3PZX~XhaT)LTY3*;TD|vA5f4NV~&-mBS@aOxq_B%b2c)S}Pz;859^5gmQ!%F3QX5JIuEHMLlcs^716YuW3@Xs|*6ir(L`{Y>oM$^-hPc!=^*-zYEZowb3VUGBlt1MIPyAS^fKSMehk8$)q##QW^7QZ|A<O*4z{#W7mjYa%vA~4<@m-cD-Y51wA+5Zpt6)Mg{|A&!>)PLxC2;H?*j<4X~w0^BF)g&Kg$qVooekc7IrEW#ZymvkiKdn!+)SEmeM%rop3;a}m(?z2)Es@_3KMTJ|ywo@D^^1{y+-Klddc06R?;af``Mi1(zV&p5e9o2|{k}W_zxLtfG9OESUnTQc4ZgK}EY7zb$I1R|_c{ju&;iWX(etvOyJC)TTt7*F)>_Xh$>)W`@ZU__AnH44ooMtSEpPVNn#*N9|B{IHkS8VP{ffWLyZKY1K95@~NSyX}^kYWN#`>)(<1l9)L_5LUFLPbnA#wc?ug^=q6_P)1y?AY1+0`e?y7lITZ^c~4d3Cp+<iQ)dOJ64g`>z#$@ec9r(|_Z7<osh<&+b>-wd2C58n{OCzkUniyfzHK&p!xp4%~=-llP5U*iXDY*K6zCs#9x?^w)l!zCNdS!0%Ie&_4GiPYdiP*1#qDy3HLa<26?;((>a9=r3`)(k{^F(bIRM=&XtQ{!nAF#AEFkrSB&ZeWe{M>j*7xM&6#%j%Q+jJ<pf-$6@{TM1AhJo{hCPN}Pr1=guPIF+*|wb%%D<`wd+p@fda&`nTn}(46*@oX1@&Iv_t!bIN+QvVSRg_6+Z!&5IR^>npop2Q41sLNAHm8`4(Gr)x-W8Lu7OT+5HwzZT*@T}R8OeLVjb(RH=p*JvX1ZVYQE<8xK0spolSZ|T=nrm{9(_tZdX-@B!f`0jF>dEN39`I!XYHE{*5Tk02(emz?&>VB(<k{|b}QfR-_CY;Ca@%k`DNv!j3bra<GA-I0_{8n6>UprksY2WOhL(7{zJna@0r~7O+EpP500ucY*^m_f<Xvg)zS6e4m?$UeE{s)P}dbW16)PI5NG^^RW1nqcV_o?)2zk8dYt)B#3?|G&_Ptev$LtfYUKh)Z>&$=*QWv(VT^KV{CgZ2k_#kXy)qtWkiz1j=Dxg)czH~afGnBSr2&`x+BtcU!G62CY6c!GAkgtx=EIvj)l{EVDOjUvM(epm0K@GH)exXpbzu%FyLl%UO*JrMg+seK80o-=Ke{O6%R$xr$-8jhFtynSrsdGrxnr!4Tt@zQoL{I$)oJ|16@{COAeK|ARqCduy;3rT*AUh!JL=7Y@AkDYqEp63(Cwo3hqKPPDOp7jc@2TE+#=G_V@g>i>%)aKV%`dIdD_tFi>|Nd=QzjxY8{>-);^nMTT+bZ=V)@kd(DnDG*$RDH4yU}yB#OXS>5`NqeIX>+f_kWi5yLsR*-H7$NJqG8~K1<<8@0att<qF1lL+J<hlKHd!YDmAX6-zLWS4`yLO;4O3;}@fTfje>@GOMopS+!#=SP1`FfSh;Dz*xj{Zvpb=zK!<YKaumeooP1eUp|R?P5zet&Ghu=?U3sX&!Z92z9;i6eSL16DSzi~Hv{cg%PRS`zHEp4yE~Kgb?CQN`t>fDsIP}MbrAo(aoRexXYEEjwc*?A`{Vrn=oRk!PDN<#SR-mlJl3~kwDoDnWJWyUBei)q1AQ>AVd2{GYhA)V<0>Am?=zb^Nj%2<zWRQWvWSe!n$kyGC)TBHa(tO1`)KRRxW7)0U+<tk`aY274DR>;?x7t==5tfpv48KV9q)!;Nwkx$qqaYo`{&?3Jq`U!S>(Lv8R*$A@w95J&*K)HFYLg^+VO68D}(*&NEI#5uKj;VJMM#3wE4AC<9^&zxtu<~KRiRc9m{I-YfZ;_#2i;tpRX~ve|Hbgryr+2=-2F)PTvQ%a6d2XtMAX|?^53=pF;e9&X4tRJz%B$5C1i;PwetO*f$QY#dDa|*#C_jf7{M^w@zZ6*!AAn+WgiyfcU%ph4sPf3Ogsx@1Cl+P(S&4AQ9Ia=G7Bu*BXiWn27VQ;g@7P=gTTzdzXx>_EF6@e3{P|+u<*sgyXSfDE6U?D{W_<jqxw>`-SlBe!-Z}Y%S%p_tFZqvuz))f3A;^e$7)+wsT%wQ*(&#`h7Y4?iVoc7pLMmRqZ9{cX|-={_r~HIc}cqoJaFmQ^YlGp6#4R<Gy#NjCb)AEzj1Bxe~vpRD_mK^TqvGRp0x?fB5fH<9wB8u$DKo&UUG9v>XIKpo-+nid-!FtyOxEp8rQjv7fgesLhwTxFX^?-wXARhs*tj-6KlsTNCJasSp3q4C&Ww5(d9n1?*pOAFxl(>WcP%UxfYoeH)3#-q#uRBQweUm(lWj#Q!2hn-_CzBluyh(awW;a-OpqBuabcq*mH`u;YqL`<}QaTK-+Nvq(Gcdgb+euFAh#;!o|btv7pLb*%f;MYQ$f4j&aK>!eCyJ^wH7itmlhsjn038LoF)ec0<9m;HPr+G(|Duk$!H-{r;iXKMIvpRG8q7cIp87rFp`=Z$#o_q-3T=c`QF>s*K4+d22hcw2w7*EwEqI{0?=zwx{$`8q20R=mWM2j?YY_IeqY_h}=kZ@u3KpZlKq=Eh!`7c**)vtR4$4e-1DxX0PA6+23Nt8{PpaW&<<Z~WE{_2;yOUnX-5#$O%v+tt<MERtJ%cl7&sXFS%t$+qPG*5!CDo+|ys_dMAh?;MwzR78BcPh7k+PP=bw8|$GQo*%c0MxLu5k^56Sv`oBnzKr>}Uo&G%>;87!XW4}^#XFBL<MqG<i8FW1ZfBfEU@P&>$<g8)HT*HIt&_#KYfjkhjMK18@vY*u;B!B5r3=_6^Y~@%-Ohg9OA3nbZI}}EZ>N#t)b%2p`0hb>asN8DmmFWl=v1h`;dGocPP@tz#8YWQoEA^N-{6;O6z7b`K5#+WvB&3+bH?Lx?S<byUz~Hip4wBzw^ARG{l+tYJo0}9&n>;7hwwaO!vf^FY7(9s#2ysi6}ueuTP>1#ar^ca-&j5q>)}Eo@{=J5`x*BQ*MK$qWxVI{yd*h(&#S58+Xe6M(&n+?VASuEu*<m)-HkiI-%??hvwiDW&;eP8ms9L=wr?~jA-=Wn+)iiv){;!(+f}1?I@|Y7e<SU?LfYegui0SaVc9d>FUGb-+@TZUzs0)sbZ^W1n~w0SHOBM2(2D4H`7S))T%Piv#Q*HW4lVv%w-Ha46Fao^7Ip&hpIExX8NX-uHt~(~?NGmT1KAhdbM{O7M*U)_|LP@<@3m{icjZpA!x@ipU<vB?KDON%k6r3V_*<rKcgACN>kfZ*i|x*M%;=_QzfL*SfBpdb;`u^}a@>VHm*c@x=o{o`Tph`e9s5*#BW)<wRpcwI!|w3imujNEf#=oUzfb+_jNclNL)v#8nD?_YezTd6`0h6$KWpou^&N@REE6ogT{J)52lfv-EPm7n+*kZK0oRYGUQ0XnucvU|J8&(Yb5;pHBK?ls20#C9Tp#7VEcLC)Tj0NFj`wm)GfVr%vk3Uf_o1Vb5a)?z@cCTDEb`=#tdpKKwmHXZp4}|<JsZ;DJW=bC#P9tqtHfi@_SxplgRy22;yHR?t1}Pw<{vSx^0==xx8S<l+WL+3Yu=cK>wvUgyx+^bP2zWlOcvjjvI^#9PF>7P>?GVDC%=Cj-9+Zs)fT?-sx<rxHwWOj9}53?7@jljIV}Aei`t8C2bDvfuMClKS&7ZJI`d|SR73rGUu<>e&G_p(iPIjNdaHKa)hUQ^tv|ZOnIBJ{&%}56uEX`au}_|}d5X<DD)p~K;<-+>{kT4_SX$cmJnxI^h=;wge(p6#{x_Rw=i&?8H_Xh0`ltWG{?7X#&)`?mul42__RZZMtdp1mXlKnPT<@NEiswRyS|Xm$M{m~FPmNy?|Cr{Ro%wX%8i;;F3gUVtt|;>Vbt-ue=)GQGv$jq?n}>YH<=?E$*Mycbzh>L~dONWz<$alJ>}RO|ZZqx&m%YR~_oLtLHQr-48jX1jd$&paVJ#%j=I%Hdm!18M`1S>V8L#V$9Po#~M*Uz9j`tKv81Is}P0oB;Va=sqt8pm&;m`5Dpy=UaQa`NGCT;zkEhqK8$4kM_{yE~z(oW*E6SAP4?#q$?A`=l$ct-K9p17W}>bayHmnQ+wzth;bE)U9z<7Fo97ymgAHt@whv#b{CUvGfp{bFV8CwD_}zOQml)|C<co%HL?)*jc>yifG>_LKVFidWV<^J8x8g7#lu65q~K2=i5j?|*}5t#{6scjQcr_q%Y^Kb;fr$0sh3yjimcpgx~J+aLVJw|DkkudRn~=i@!{yguSv)3!)E-rRSjzWY?~_0IfzJFUcgO|GZMxx_DA{J^ZJpXpoNXGc9l{ks|AzkP>&>GOOzE;7JRUO(3UXz|^-pR9G}%`Vto#%oNPvR3Q2*jBgH5B5j>HsO+gSLj%2#~7Xp_21sYx-Gix7}oi<HCj7qeSZ*t>~`D-zFLKKRjG}%<9U<|&%u4_;(7jrNytxD_{N(~cwbyD%W)ZR>klzn`}2LLir?%huH%=-;(HEjwo852t7S3T@tbs9-v64TJgCq28pbcF5&y0wG1@%dd?@d2-Gd@yoO!dnCnRs4znaE4^Y4mWBIB~Ygm13gBkRhYwH%M@)AHWWULS+^RxzigU$f!rRob{7jGZ9;MokvqY+YEskKyvZm2ugDWAGkyei`KR%kela{<^!;*^YHBdZx5rxiYR>yLH08<kKB-X7$7S;D&!l9=vClVVx)DU7^L3dE0#Hx5X*Ezij?O@@${Um?Uw&Iw`)lbxAz`DX~P}m$`B#q5kZ)Qr~;^xWsSnIv(ZBvv~^NPjKBlhWdPtZM=Jn^){3~zprAP>Ww_yS{LQavzc}!*7=?_@COdW`-POjXlL$%C~dtRxQ%&l58wK<B+j#64nQ6X#V*(KS=(o>^t<}^W#S)Og8g|@9QFa<+RL=OH5;^8;t7fHX#W1ASchvq#rvuSl_WpLhs!c9_pLXP@;UjvQa}o<6W^EO+fxr=KQtC&Kfm$}^|>!u^@>V6#@ol@Ta7wmABZ}E`upf7zfTNkiSd?L8|jSG-20o%qqU_j+K-RM_ltIC$GlGnip24@MCQfi*?{@on;q@kFO2ojttQ^*cB{2eYky!5`M!Z&)w4i8U(A8;b#%Uq_;;BLob^2?6V}Q)A9;Vi*3LnXyzjQ=+|+!d)&%*Ufbm@q_?Lge^~t4881I?<c%R**fYkRE@nYRJ&ZGO$cpvR5at`m&15#q&sCEnU{%Z^IlfReZ^(`m)@kY|G)C2oiR4n$fufLh?oG(v{7Ff@7nu`C=_u|%Fk#@{N@Qr6Fk^dWy(ay{I@cDf$@2ELa-xvnpvnj8{?>=hcy<yfa5%TwEZsU63<tya5NeA)&*$)TjLi^!uBAo48E#^x5_RtWt6P^S4FO2ujcCK$DoO!UWRzp0;n~QG;HAcU=4`Y8G**L-(r+pOfh26s&MmY1}4Y-IrJa2&Z-=)F)X2bhR*UtJ8&U~6T!ZEH!XM<(@DZ=FYgvN0^k21!b5#NYwiSHTOO;Nw~$zZMDBJqen;4u78>)?8z!wJ;Suovy`EsJ)l<9Um5at-PiP9wf2+hw_rHm1*of5$*P_v^@ghjDY3_^!V`h;Jp}{jU){8gXVy6yMbs&-0B-qr^9x`=j5Pn{l0ayC3{RSFlgc#reVr=^gCMk6mso{Lr4_dlSat`<!_<$a6v?vIoZ1=X=E8Js0-L;w@3%+X(gl43Otn#<Y6D&UNA*F$sAa7yv(AZj5)z8hIXKbSi^5`F&2a@I2Hv{E?s3S+L(0!@4ypmDKX)?vfSv-9rnAZ}-ZHyp=ADb`o-k?>TuxeDA(~@;=CT>4*9qGa~+KBXFI+GX>(j-vV)Fy@~6h3<moBVI|tnSQqaRUcGAST<7krU!mW+7l#Bm;<S&Z65r|=GE~-Yzb7(Yw}tr4JZ0qi$a?lE>d#({=TQa9!cX1@rp?50x1fUf|9qeGTu~esV=9X8Zuu+LL*D^1UTYEjfAW@PB<}mtRuSJ-bq>axF9`1`3c|N*)<-;dkOy;SRb0pMc=06p;W&z+zo!k3i>HUM|4*n6e@K3;+s_8!dEKa*;(Ps`qu>4bK7f@f2>mvAiR<K$r&yn^Agvu^)+Vg;zVws#rMA71hk<P8@Xv@p<7GKs>>I3~e11$EiT!p}UHF`LtH<X!&;AYHGi(s@wg=D8jfe)Em#V10-IVojoe#mhWPBm>>pAm_9Pj3=u0J^E-Q(L4$NP#JW2FDk-r{?624J0Bs3pF!Iv?T>?Sy@}QvGq_r+R?nB^B5Iyu|TN-}|Z}o{#x@HQ%nC9?zY8gC>f9_@?--;9rsF@B=@|@0UMD`-{UQe(P;jeD5+c6V7XSA0Tgi(@v4UJNpprn-}q1rOlKXTKg4{2kZ8X8P5FJbEnBVH&bky;atyFJdPJL%{}-d-r{@djXTJ?b<g>Frt`RPH)(^s*)_!X#IM78%g6VgN$```kKG;nq?O9Vb#eJ_@RQbKelx&N{{FlbogU|@%=E)*p#4DXhxX_|wC`6K$K8}bSr4v9wNU^3VT`w1w6x<bR2zPSQpitOex6@~#CJ7H!hY2c`;~iIote(#(YkvB`%*0Y<nPH_d+OkQ;`_R&zaj|ne2?>;mAc+c=ka1c55)CJV12~H{m00F^OqGeWwz+OrkIybmoV?MQZJCa<;g4Ucsjno`YfDxu{MvRj$j`cQCNH<??W7?Z+(*jg0+8T(Y;sN`tE`shx)O6YGgCIb#(j_3uUUGWc}~|iADDc|EqsuQMp2e|L;Gs@J;dYkos7BSQJ0;fqp_(nv$&ap$}LU#pkG($mhr>SrpsU-^ez37xgMxX##l{c{BBA@@8^0i{e$(^<<?h$g9Y6SQO8tE+Z?QO`c1h#-ex%bsl*Nc>;A7S?MJ51oANIXmW3AKNiKqsiVnCe;_OUiL7)ec{sTfwHLV+wH=G%4%A*`rQOLL$PHN(x1ffSTaa5)-DIU9<d)=bscpzg+me+wCVxu~q}C({k}FXwlPi%+QvJy#$%Uwe$%V*ysrkrx$vLPw$vMbbsoBU`$?2(?$iCFnEQ-@mGm({kN=`%ep{6AJklz{5w+2`h#m}iP$j`}7s4vM%Uy+smMSeoQO}$6HOufpY_!{*dS?NvkHS%fdFJz_r$fwCRi{dTRpUGRui>OP;N@tQ6k;hR-k;jn-QTvexkwdAS$)V)d)Nja28<Sg;>#-;{so#*5)*&mcMmEV6spZKP$;GLq$i>M;s9%zckc(0)lZ%r5skO-d<gcg=$X}6zsNa#5b|eRp8?h*EMeRja+Kt?b+>AxBn>vu}CikUAko%HHQx}j&lV?%ak!O*ksqy4!@-FHb@-Fgm>Ls$$-^s_xN2nLbN5~1(bL0f_9u~!Csn^L$?~;{XA)h55rT#%aN<KvWm3)Z2mqqaj>J73|FZl#HiF%8y^f$87L~;^&GmGLF>TYrjIf_N`M(Rnj(!*q>YsnkQ^H~&6r^b?%ddS_W7S%&mI)`kLds8QngQ*>;6Ua)#$x6Q^cOX}1QCybViL5k$T$b!dtw7E~%|@+2R+^KnG&4CHIV1Hmaz=7$7RA2QPsvKtkbTLYuqaMP%|KTAIXNBq3+iC<7v!PT{p6wKgVg)vgXD+Q59EjB_tcC&;P>PVKG0m`4CK$L#mJwNi&CqRi;}BSn~<xL8&Nxw8<E4P-;<U0C5Ms2sUyisEpj;dN9t6v(&=QSGsr)Z$FnG&PhCt_x|BSh>|s$HMO{u-x`iA?-bg)6-bjw8{y~l>|3dwntn@kg7qXZ7f$Sxpr@kbgCts%;DZtms7pZT2z^W*|K~0eYe1rTu^)DZ=DvHlgACS+GZ&DwVmEI*Qy+gi9K25zxK283U`iQLbDfv(GuhbXhU&)uL@5z_R7pSkv7s%JBugKTPx2bQ*O7D|TQEyT2la;<BD}6@3MLtVa_iShRS@9LBx;Im-^c?vL`5^Tq`5<`%i{edGo4kp<j=GDibTfG!c{MefyqX-zqIe;76<O&V@=WSD7R3{(bI23Plc{sbN~e*PP9ZBDL!L|?!J@c7bqcvZc`$VXS?MtHU~*5NfA8xQx2CpdQQU*to2;}SS?O@H(oW<a<Yqqq-q$G(qSj+k987IRR@#oNv;$dbLvk?LWKmq3MR6S##dWDI$aTpLs4dA#za=*y2T%ja0ptqQO5_UU64a9966Au^Lga$vJk-48JY+v=4zeFP3pFb_3ppJ%Jvklu6Q6(Y_da1!oPwH~tTYW-sSh~?`HcZp_jPYr6hEUrCqE-UramD*Cf}jnCf^}nH2%G>yU3#W6!j`u={2&_(`2PK`4l;hMezpe7V-x2Z0aJi(sAV3<T2Di<T2#_)KGGNau;fAau;$77R5EG^~g$1a!qn2YDID-atUg2atU$)Y7ue)vWr@j>>}r<`jhjM3sJu!7b2IY29ZmXt5O@0tCH(dTalGEBiAJdQr+Z0azhryZK!?8ZOCEN(d01l2<j~I2=XLqG<gzvIdvC#Ie8oPI9cft@?z>H>JhTi1o9^G8tNYM8uAJj#oMW8$x4rsmr}P<kCK%hB5x(Hr|u=MC$C~ryn}jztTc(NbTfGeIg&;3JZcPi9(f8iirj}fo*G3~x{<7OK6yNO7<D>1`Mzryi{cO##Z6fhx20NSrM=0?_h4;V6xU!;T#nj-th740961NIEIBJRJGCrXsUJD{9xOYH;!G@x(^IpNm1ZO>O-)WuPRXJ;1=W|V^b>LlvJZ>m<R8VUSQMwFrXwr;f}EC|i#n8?i#&vSkUWHZfclVpfc${^p8SCPH&xwt{msvcKl6cpPX3Ji1+^&o3vzL4RdR9i*VIPjugOiRVdSRduGDaHSMm_*k7T9e$wSD4SQJN4=aVDIi>My5(kSvG@)8!sYpEN_YsuTF@#JmfW7J>BO1<P`<UQ2$<UQmQ)a&FE<bBkO<bCAr)EngO<O9^-$p^@>)HCE*aw7F6IguPkJxz`yAEEw9K0@A2{gu3%e4Kije4M<OdV#!`oJ74wP9pE8-X`xS@9_EezGw%F;-l1C<fG(6)U)J6<ek(jWTgkmJIPzA8^~M9F)WJLP&bj+kXKUIk(I6{uOu&^Mv|2-Bq!hJEMQSQmO73+mOP3@@j&WC@<8$c>SVIg5oD$P$x8c>2avmcEZ<Q(Q~Qwn@NYV^DDFZXOjg>H+=blS=ihrF#kHvQSrmUmZB16%o~*P7S!px!H{=>V|K1BJ{*qdeMe$eEAhObWWTnAmr6#!)wJeL`@>G*to?M+;o2;}BS!rEzb#fJI1G3Tpa%pNA7RBYL0c52W$mPgIs3piQYJL{Q1*j#+N(+(;kaJV>kaLr>Q~k)<$(gBH$eGD$sp-gR$*HKHkW-NjY6_o!Pqd0(8&GwR^qNKSQ|dGFQ}QF~WAY>NpVT|#Kgs8*7s=<z$Ec^sO5@1K$U8rlWz>}{idR$P$VxYmSCgkwXOoqVAx|Zbr1mF|B=?|pA@?A+qqZO`Z9;BGuFs<QYibL!(wbzYmB?R{OHxaaOOgvx3y=$v^HN>pyyV=}{N&u^Jk&zuJmh@T(&T*P!qlqd!sIg4x@4t+<TB)9EQ+g88<MM#Yg5~hYm=K(!^q9aU8y6;UC9HelgI<e6RFF|O1F`d?~5j~DE@&(@m%UAveGr=x#Vfo7368;$<*!S<ohDU-&4m@my*Yl7gD#9m98f*B+sC(BF`ZIMBPDF8cFU+{gE0;RyvRTBY8M=3OV^6X*i4G_AH89ek{QaeNtpg`9J*^sQ><`=l+KFAEN%}U+Q1$asFkuk8S<)C7<AipQw9?k2en~<VCcPI=YPi0`GgvyZ'

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
