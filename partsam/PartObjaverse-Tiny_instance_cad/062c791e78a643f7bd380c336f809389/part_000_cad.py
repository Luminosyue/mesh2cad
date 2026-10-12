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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_000.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_000.stl', 'source_sha256': '86391abfbd81aeda85e2b899391e2d05cfe0f3818bbc85a1dfd71a5e1f88323a', 'input_faces': 1338, 'input_vertices': 825, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49934136867523193, -0.271607905626297, -0.22543272376060486], [0.46527042984962463, 0.500022828578949, 0.2774604260921478]]}
GEOMETRY_BASE85 = 'c$}r22b2^=8?I-TjG~ALiXtOO&KVS81Thl?1WYi1pacbpDrv|;kg!OSFyss(phS0<C`lw|SWyH~Fd!<5a{H@#x|pin|D1d7#q*u_*>|cdcXd_It_`2dkTG{a|9dE~Hne%%v3h}k#O;CHfu3!<c5mONZMQOScX=-u$f<n!=WAm97wa{ADH!M(=w0;nw%yuvE&52PXpMH&ik1o$ZP&SL_pYtpZrQo(>utq<vQ?*UZ9Tu+o2|OE^?oi^twQBep^C*zh5Cm6AOB_dst~Pw?QD{#p>kPML{qPnSeulNAIq>XS}PqtTI%@x^!()7M>Z=z@rv@pvl5f6{2kxq@AxKv$M^FO%(|@n)JOIwtIr1<-IA1!pL()VN_u{H!L=Rf<r6DEb(bpl*9*!|p8i}?eEzQQ=bt7$`MbWKe|X4g<wu&A)BRGl*pPJnR<q}+dj7mp_j8rDcDo!uQf&6R^!((liCfak$FFB{YE0KNVf7dB`MbWKzw7(?yT0j%?h|#pCRbf=^{3;T{&ds-k9_?8Or4gf{R=tP$Imy{_vf4I`}589{rMJptf%s0u~DDIk5?L>@ro^cThFVSO|9`w<C8u)Q&a7?9c1-`>zn>}eAEAqZ^k!g0p&-#%v}@T|E_P!b<_WkeEj~8B<0fmma@Z|pRVuM-}U|ayS`s;sBu<ZZr(pu$B(b;`{V2S{`k7S8Q+ybU2cvM)_UmrCV$5_`8&R!e=K<8jLLUMvy}M$cYVL#(xj&!T;K2iK#A+hkB+|nS$saOZ`KFLH|vAroBpqJQ2F5#N3C_w_5J)^-_PIm&Aj?`yYfRXz4vMS{gTG#eu;j&M)|Rc6O!Y{%k|Ck#qrJa#qrI2sPu_0_x-Nc^TqW|Ke*}resg?(ykd)5DnBwbw9y)O$M^fw_5J>IeZSnurH8d&X5Pm5`n$flPu=wYBOmj8EFIGG@UB4{t^Rj>)Blcd`rq-*{nF~M)5@=QeXZ3$j&J(M@lF3YzIpC9oT>cCgpF(C`^WXoedMP9ANiR3amWbmmwjk$eE+z<-#@PJ_mAuQ{S#i>K>6XPa?gyfzw7(;Pm`YdyS|y9k5$tCn9(!i@5eO0|NOdMMETKgKHI0}O~-eph^98ZL;KyQYX6P=qmt6`L#4x?sQepmKc)I9*Hb!uqlCpt>G_K`tyATWdr|q(23x;U{zp+&Zgj^B+8>gv{J@p1>Urh*q0hr9>bi3cw4c~!PJDaQ__Q~5$>X{{<Cm#?Vso-alhX0S#d|MP^~{}7``zDAezbO;xk>5yvvz!@^8fMold8P7O?CYr>9Q#)9Y6e9o^48#S13QS?W={>d~kd-AKdi*d~kd-A4bg5<({~@SJm&o9xId5@x%Qqe4+a7j_%rDk*xg4{u!H-((yx=?%JuYtJ6aJcaIxXE581YZ|d)+_v`QYX1_hFneqeg##Fh1v)4XPO2?0teM#M4k<X5vQ0-fAyRPTiK6;&W{8<0&Un(71P5Gh2P4=kqetnI8zB_)XRc76v1NIzOpQjw%t$x1ruIisOe&g?T{>?WjKV0_L(edN!`evPU)BF1e$2aSFo1wbg_DN&o=YJZX`5(%0hw`I&&(Dt^FV{EEM>oCyd~|%Xe)c+dOqIL&OI^QXt+pnm<A?H2Q<@w&rTp-?tLlDBP5ene&mBLObTyh@`slfodFlF3chddVX{9dr?~b$L^LKqef7kc(Pvet+WXxjahnfu6?QfV{Kd&7>mfA_(FUddlSAOK&{R>q-3n~vz*UxlTl^gz`q4o=vogP2FX?%Zt|ERD1W?3i4x7YRk_PV~`-ZZ}7-fh{mKW9cteEzQQ=kNM{{%L&jPYndL-}%{P@%@v=r+-2nPajqO&d?&Oy^e3@!-TEMj~!cL&j-i%(}%_<DL=aD>p5zi9$v2R3&)QQ?y2tgK%Y(8UpF!_K7ZHu`^WYD{z>CgpYXV4+Am&qetdmg->*+>#!}s`jU8sir+0lneQ5e{<%gHt|Dh_+UmqObtPgH_e|>O#bKWo4PnSEaw7wrEO;hWG>&G77r`L&^eYHQkr1Dc+KBMd7_@P&)>d(8qr^o%_Obg@N>-v6sQ$Osb>$$AjOe?+P`{|>j+iCw$H*39eeKViuSJCw>m}1R0*Ei|6RMzA8?5G7+ddD~OvtK#guF)5*_PV|q-z8;qJ_px~x9)e}&$M;CbssstSvMTt)PJ(}!<hz5xBAoZ{rZGY=GFZWoIE!Eeoy0bzejeTJEGdvWUkd-*EjS3>RIK7XWl!*n*WaPr%xWTQu)!V*-onR*bhgJEKz=J@RU#D>zT&)*QFy1wEyUr*0{UA-*3^_EM0EL7be7yi}9zooM6p2$M?s@_02r#fPY7Lfi+JY-^}w~F<s9R@5bWOyS_<(c#6(v#f=lHUpOzgzJFebG##bKD}$b&<~ic{e*FU%hABU}?VEe!)4RS|R~_H1tFG_Q+a7&%yN1o0ZOvQ9H|qv|bY-4->81C5lm2om?LWWaQ#HR?S6$y<SJR|tU3GnbT@4+0LHqw5(EZQ(D~-?jD|ESmp8rR_<~*$TEv|3&E&J}*`Q*s<QT+T*<NNdfbUvNW^W*jWW*_MK{ys49Y92lAJL*rd#@F%9_&UBBU)T5dEjhnAtn!;aPWJ=n%~<18+Fv_H`Tlv+_5Jf^YSlf;PkwHQ^3D0t@%{5-sK!d=$A10PUI!fCtgDW1)@RrE+m$#*`OzA!Rk{B8G>y;sG}0le{WUM?_HsUTegAwKXz`BnBZGG?wZ_Hq&A2$e85h_0*QNDu>UO<Rb$0x`O5-!HlK(EP{P3FtwySbEf2HyL^VdD4bh}y?SM4(AU&r^)zoB+Tw7+=h-1z&{_09grP4Dl29N+AJM%_H5`fu-@dLDAVc76YRojUxI@?$^LPLA(?*Z2G1_5J=&<J14i1-?~&@)!RdSL4L_+V%bOb?S*N$`2RFs`}YKFT1{fUQVslM*Bxrt9<<Pxa<4p@zC~yy4-=!Z;Maw`hNOwrmY86zg=#AJib1z@7E`KcAoO18+IIw?@!k^&r`=Y&t=#5&lmZpDL=B{z^?fGUEiEH9p9WcUEjao8xL20a?7b(<L8g-`{U^P<~@nyoA)_^=DJ;N@*R)AztZ^r{Z;!Z-OsOGKBRum(yvQ;eqhJ9^V9RgDTmd%ntUjiuFrwHx5nS6uJ7Ncfw5N)DF5r9_4gmFW3F%Bvn|}9{BYl8%J<jFG(PKO^1LBBpJQG0`)JmA*Z0@?z`SlcpTMj7`!Jp_feddcKYAqbn9AROAL97teMq(TI-ia8b-Q>TxxW8A3fxge`!l<#eEjFQ>zn8JFG1}$KdR>e`-C(;`-Eus&HL3ndU1^Q{e7L|n|<A)rP}|rr%vy`PyQ;q@>8!|*&lyjxV~A(9N(;CuJ7L$E3zp+RDJtV)lSZpuJ4~K!@II5KlbD{<@@JK*Z0qr;ony8Q~u>VN8|h1_5FU1Wu2k@XUiOmZ?Ef{b-?k>I^g>LdEvmb+W+{kBk}Xf_07B*RY&=eAHUM&cJ8@ewd=91dzF8v`|<eu*Y*AT*Y%UTm0F|9&+(4-i+54w`s+p-pLHX!YQ`SrkFTJ7f8BO{f8CDEeR;QP*Jp<hE8l;w>-gq5GQOtr1NDy|j_-fhH~TKfH~TKv_s<J+itbYR&FiCl^Bi}4e_f4zQP}eR_1X2!`keB}PUUy1rt8mo==%P8m|FG5m&)&0MCb2+@8J0UdKi0il=4$6X4dUuJxt^K-)lTwQ0MdW_j;Z8_q~p9_Pwod>`<Q%Jf(bpJ&cUFp!~?eBl@|(`sVuP`<?6eYX6~+bv~?DX?)hJ)WFp3$}inh`~LS<j_<EmsSUa)KlNmLou2h7yuOL@V@c~y#?K$u_ver6`|~G_@2^*f|55WL)INATK7ZFY?@=A!yhn9?e_y?Cw%*5WsC&km|Bi3wzvG+v@B03}as1<}RDD0FYxR%ooA>sPZ{FLxzS);%>mq(M>9ey|{*G_*cYKq->-+0xft8(9|IPjIRDAxfZ}x$XZ}x$%@9zT}E>-JdtnEH4f7dtbzvG+r-}U|cb2rxaW!XTgmA~Vg{2kxq@B04wRxH0-CsGS%vg+^p=6UV-=6UV<{`{}BMx7I)&*Znp*Y(Z(cYHJdUEiNSO-}3YmA6(qVa*@MH}l8w&HQnF|NhE$_-l22t-PnL`^)jo{pI-P{&IbPe)iSRoAB5j*7M8t&HQwHGe2G5@1M4(^}eC*4_5xJZ{EKpUe$i>#}CD)cYX67!12v{0N3}w*O-%C?VqAeZ#x>Fe|YF^mT&5lV~F}Wyr=aMt3Hlz+S_Qh-nUi#(K`3JzL^h>Z{~yR`{T9uM!NNPeN+FN+4Vl`+xx8jq3fIebbQmF_^I3TS^LA}Lgm%Z;a>f$@p64r|IthI^;@pk=VHe<^Ud+id~<!jy`#@5KY7I^d;U1SNgr#epJ$6+w9`Aj=^w{8{p0$6dk?qOe$5Z;`^)jo{5-!(?}M}Lu;!cVoBe>}oBe?6`}sG&pvztIo7G;|H~Blh$=~(;`7q^n{l4#Jf>nRlH}l`|&HQ(L|9SCxZ?%4fGPl;}ze#1M#QTAwjrF-|!#!i;{m8K4U#oVm=-)Xh&QHENQ2CK>u37m+f9aw8Sg+c%tbBq+lppP!dr-Wed~T;Y_e2wWS$;U{G<_bL`R%*$<wnoHqtlnHGt6pN`zp#0*9m+W@28fmtj}9de;2dzKmDN2f6~aQR((?Xex>{dk9LSJH{7VF^20rbZn65Ucm?GL-u~C}Q(NAr{AmC23#|NWO;YErSjETyE1yM!l^?BJ-AW(+HLCqh&(DqbV*}n(et2hr6;?lIs;SR&`@gl?75cJ<_B)^MW7Q}1ggVbfE8Mj5kJewL&v^yP54ZBq*j=Y@d*2+ZKCRm+Klbx^YyO1ZcuJ>#YRIJY{P4{FGp%xG->J(jyn3mXf2k|_9JydbS8H54*HV7u;r|v{{okmp@}o)Ly=eI#PgUo+=$_p3t^P0HUHOrsT}E2<tXp3DTS`s0#$`#eI^TrvsGnq|AJ|8qt8V5`w%S$bJ^g#(?|uE1Rc?nG+W-B*FXP)4sI*m|SM#^A{Aj@y`hDMDPwcb$=cg*#Z!yyLf9#}xU;5O4mLKR?QUAX2fqY+D^Wo2R`tKC#wNJ6`_YZce^J;kYa?202pQ+EW4aZpdg#KNwf6w;wL$?1<z6~mU<!5$U^QwK(WoldocDC9Z`Mvv6Rc_b*yW;)SMxjOO=YduCTK&9l-h5T=nIe0v_BQxyp6Z9c^?Wz!7hll7FSz)J9hQHfmGV<_<*@yW&6FSLQPiqWpv(*E_ZU-`j@fP1=RjuV2l8yU(#MLtHCvTCc(*klV)K(`srDAQX0<C6E)Y}x4}B~@ysG&O<wuWM?TWloSpD8n_`ep`xJTZ7=3_mdf8S;KH*zRH{LDft|46aFr|SFSvelo_x;Z{le*bNjANyzQI8~4CXYBkN92=?HJ7<v9-bkS;!&SK{36>u{TYIqbYjn5U+qp$wmH+K|oN;g5OVy`(9=rdO4y*Md_W8E2t#Ui3bX56wd&SNt>0&eG=Ss2to4e|&{96vU@`?42R8aRv-cEM?Z%(MI%9&8bPM>t6p-O+f?>;+ynPw{e%hUH;>EGC`-uFf7p0wLF=u7py3}wB?N*`TNQvW{Inx)pbL=ILTrSglsYWKsR)0Cf_FSk|y@aOmF-xu04(W+-?ZsJPy^Mb$Z`#Nt9^?i4s_Dy?z81%3H-u&JTwm-k<DpmeZ1Fd|blkQoq{4F&tKag9WvjbUoTKk#Q{*CnSE8n%up66G0>-S9;SKI4J%Z=*2s=Lml4)|WbZ%wRb=hN-b2IZH&YV}X@&mA@?UEa^We`jRT-^2a!inacS#+1~*e?KPiQ>#8}J8QqtoRwC69_XX|<R1%J&zJC^6z%t~_=VMP!76(H(Rb!XtDZgUsPlca_wtEJ>G@|zOh`BVr%UHq{_VAQr0Xwlup{04egDE+A6etLdAfc-(($2jRz6Q$)qY}1)aw5Ob@caGZ_S=<^>dxU%8wMt`DT2%vAUb|`|GxkZne_?bylbE*l4|#{_lI$b0{({_^~x!EemV^W~+79xNIq}zo%*Qj<w$l1uN?J$T{vC8=pQ@qL)rz`ub*T-d6ige{a!pcVDZ$3xCwl#ZqOh^r2>@_4kqmS~s%tA3aZhUsC-MYabQ6u~dIA*=^THR{aaD)%o;l(Z%YA$3kj-iEJ2e?dMb1y`q0#`t0deRz3~iR(^EMBi8(hJ+)NlGiQmlkBZFNr1L3S>m4iov{O2tr?1)j+iW$|`V||oVw_daHHWodC6l$Ej|894zYo7-NbmUc;n8}1kFJ_-)ic~wKUX4UW4%>=|8Cd)>70*@A8xA8N6bUtch60}A8vBD&gZsA7smV1X?N=MNlm(1`3zmH&r_R+EQ$Bs^Ox_t=P%z+E!an&zdH6AZ<Xtu%S`&N?Q}l9l19e+vCc2)^V)}3=2-b0uCD#;L*`labk29C-?HV__5W?kax49&KlM3o#YgkwefK<Q{DJy=w&?c{S>?LtL{m@aoM_rrzoquioU_K!JwKZMan6sXT<82~{BfV?b7IE#R#^3S&Xp#A=bUKLJLg0*Pn>h2Dc3nCn)W*9MAQGyInnfkb51n%an6aRpPh4}$=^9An)*2BL{qMFPIP_$oM_5*&WR>}=bUKz$2ljO{&&ua#&^z%rvIIDqN%5IPBis&&V9yr&T*#x&N<Hb&N<H1$2rFt-#M3=dOGJa<2&avGmg%=%=pf^%=BBQn#vD7I&8b;&)KEE7YygmYt=t>abx{^kR!A0vC{vyPM`0NkNnz7-)Xq^Ghg0nrFYJQrk^_<Q0Ku=&!_iWzH?4A{pOq#jsH&-<wt98xB4O4Euj3=vPZU9zH_cLzH_cLzH_cL<=%BbogZTZ7FzXp&zr`7;wkM<e|fuIu6+(Q^U67gx_&sv9&5Zp)qhpz)6k6u*0{LmR+GNpC3S8M9hhdNch9rtK0P~A{~hJid#rkfH*Ztt+)(F^+brKX|C;$(SO48j<oqS8T=!gT{GC^)sqxKw#p<_6>*dOiG~Bw=@||<E@tt$D@tt$D@!x5y{g)0}^>okI#?Q8Tf*P+vTX$RI+p2t``g#9&Yo560aZ_&9$JF=k$%Q-E{ZQy9bxsfUEnv6TIlmjf_g3YnHh<gh=LMfAKU(kyyFd3$)A=+#W9RR@2Qcj#78<7VpFPL!pD~Mus{EgL*_tQOr@kGc^2u<-nkUicIw?PNq?a{MqObH*?-?RLq}c0&^Zvo~=c?EMRiB$FR(;&}5~f{6C-+h1mK$aF!-}%+sr<9NWY^z$k70c0J%*{zu*GU0A1J=g?$0|Toz%~zdRXg>``*LkUv}2(s@yi8+v}V2KE(Jf$2V5(`m4XS4!iG3Og)|VB)8Jr?@3I0=RL`-^!9ra)2^07UQs_kdeyow-1jFYegB&8i>BV#V9yihy~?d}Gw@zzsy$xL`<7e%)<^vvU}|D<d!28PP3=bm&!pPVQ|JAR@tyZGX1+P^XUw|lyq_`81?PQ>sgLu%#iV!Mx0vUw^S;IS&ifNnf9L&)*-tv}Pt15Z?@vs7o%bH5{?2<3lmCF4)_adMKJPu!_`KgR`B$&4{K%k;3)AysEAxF~`TN2<(#t1YsoswC>SKJ~lbC!4PqW^W7(dHz)_W4u&(3=i)1S_J65~7XNsRBj4>9w~dB0(N=lzDM&#LdO_Z!A{-fx(4_m{QaZx}zzLhJp8DR<!FUFnUB@5f3^{nRRV^(WT*5HoN6_aXl^T4|-9vEF)5V)B0|=kD~zJ#wv(_5Q@<zdT~SKQZmf+SPi0V)D7U!g_yV{E3^b_a`R*ao<?)PfY&*g{}7|CZ8kQ_oUZ9sTWRK?^R4b_XPK**FUKhpS9k%nEU8PYwLZB@wfF(_kBya@}Rxxjic{}PyM%|RzvIm3fI2zKSio}pGjm3<PNlJ75Be{t5!=V^ELhdC0zST|5yJ@xbhV%R{Q_^f5K(IGeaP7hZhCB7@pwuix(r%f$#`;6#4-?3jPrN2>uWrM?R8oKXfSE5AKT&hWo<((IIeucmO&K9smzQN5X^PG3aP`3_KAX3r~b6qvK)G3Gifi8X-ItO@ybylhASSIQnD~Aw0#4d0tHSVgWi6UH~sbXTgi$#prB!F}x6+122T<qcM0sJQtk-&xJomr@&LFv+y}DE_!j25Wb9Ff-l4WpufWZz&FvW@J%>F2CaX<62ckLzhDXB1oTf>Lik_2Yw*ADb@U2+9ln760AGMlpx?qL;G^hSSo9Qp6y8q=A4bo>hv8%BIrtoXdW;Z0;>8v(zV>1Rx*OgAuSIvlYvIq(FX7MN_2>?GJ-iX!1#g76qI=-2@FDaFe1tj+Z}MWh7yHn?aFQ2ad9e=N2CswHpegVgcomuquYy;jU%;#3&(Y2B=kO+UJAB@Y-@W(|y#fCS|AGcGX#NHM4GqE)!at+`C1{oq{t5jX{t5mL{T}`f{suh`e*>TP;(!;aUK~VE!>37ekT_1i?}erRb9;5W+l%7p!?0*oxV#sIy{L#5g)73<(Bg1$t`*MXMNTjBqIbcfx!^)xl=Y$nS^+KrmqIJUrQp(N6}U892CW2_flH$0;F54Lv<O@bE{Hw|7lcFT{cs4*kKPC8hx4KL!ujBP(7bS7`b2mW<5L7J3qS8gBQNTqjp0wcSn5Rq^gdXgFS1?-&;+;uX+mf|csut)Nwhe;f-)XJ3&6Q$9tXWTqc>rx!xHiq%>&D`MxHBoqB-DI+^YrALhwp2KBaD=55dxw8MH?<3;duL_j-{Z%?rz#AnQd@v>3eHi)CKikLH7)^Wp_Bo<$qNA;z^+g4Q<@G-vZTlNSvVv_6xdxtSMldeIbZ2j7*TpU3|5_fEX5-nF-TQ9nUzlLXDpy=d>nOK3+}p4aj$&xYO(%kx*BAJx#Ra8B;YR}!?gOwcTQ3E4N~LhptPGQZ!Z?b24^+dR&aLC-%?nS+g~!))pydK)ZtI72-|tH61f_fikhNP_0f9%s*>=ewxPbzymi%JZ@uS^>_*n(|tL4&hhPoN!Ls{VHRWnQ_WYIl>F*i=1dK_#W=f7L+Arw4iR;s9!e5Us(2IvRBKFW`(7%veI8!8E4_l33|^rkGKQx5@T5%tp>~7xQ+R78{^P~YZq|+0_rX-&tchzRYo6y^Rfm>zl*j?&^(j+WJNQ>_p|oBo}jfuf@ZmwWj~k$%?STW8)~4{VYz2z?q)%=!BV$>sGn#ZI3Md`8^%KVz72K0k9v!?PS7lKSnjX8(YxTQ)afy_20WWFyA90_*P$N%zO*i0e%A3fsGHQ~4eD?|^|+sY68?j-YoU+9a_*2b$)7>3e*`txr96M%`xIr%Sw_w+SA$yr3TiIK^XZ)gt#XeF%f46k#9{Pt_(7g+GJc|65;V&hN6tKd2en=gYL+@=q#mMACuo*BOr##7{{}Ue<T=_cL95h7Sk6syUJ9a_VA*fWUi?wCCR~JPv(!)Y-2}}OsOycOR;i<~?D=JX|73#JCtx{0%GvVwpw??a&DZFonrIj<!~URWf>x=!u$)Qd{P}B8>u*8LQr30K6Ri!GW6vS=7JWZK^H|1S`gb(rFWe(R?_>OZi<H@eKAuefPNvU<Wp6F_c6qciEM--pJkdT0n&liJ`|?U?ML3Z@{U@kZ`chc-T2i0x)Jy6jEN5HUTVy~3u$&R(JWv=d0ZSb!QxDPJ37Vx2d#HzK8Cdp#vM=nFptW;?<_A2^;YHg7tuH2MmNX?uC)zbZv%J%I$cvW~w7!*~c|CP~7%dD--6~K&(f1NG%Xvr6LZ#7Cu#{Db@=DQ9!f$z9GRcch=tQ`u7mK~<g)V_Jd42t$7n#ul@EY&4@4Z-!o{wYstN>|+CH+}+QQ+3~iwNO`=xSKXlCsZ}x3K@2=owV}GyI&1axw*PmH8xXdkXCZ7YgXUD2R4~7n9c#^ejA)vKOOg;7PP$BDxS>!nKpoMQ~v+?(*VcG$;H$eRdvw5S~Q+mJn~zhPP-#FQO3bDvaJ0*Ur0$LX=mCw&tV_J*o3V*q;wi!ku9Mnu651ApXO|la&8tTwT_Ck?h50Lij5}_!J?0ju8Ht5WY?b|3e60CWKQ7;UnlCcrToSCc`Q426R1q#fxvexIqa2O$h%&2!BfmpC*L&5yD%DZ^(ZG?APHN>L_{?-avh}pqu0J*-YM>=|{h;uPFa3`qZz_De8EN{`Kp8j&_`*ul;uYOk01Z-~F~<r$4SU27dqiL!bS_cw8Ya)27Re%{N3U?M!8SjuQS@9bue=D|k`Si`NO^wuEpyv=S^@85Vs5ZqD^`-P8R1k{2I)5%BJ{sp!ps=Ive-@qXTc7KNvH@t+ry(SPBsUOeoj*@hN|qh3t#VgULP+|i2>UUWc*!~MJ%??rz!5pM6rFfZOjhr$!6>qqDgcm!=5j!uQgQ`bav8$67*4Miuz4|$Qri(=@#aC7?c1+)&_$cx5aJb~7Qi%LIwkr&Mazrq+bLR-L9yr>$u^{=WP9u>j~Xf;^0IxLz2mO3@`;x+VDSlUqBi!k~){9r)OxuR$-IKLOAy?6jE1vmAgwHM9MHt_vkl=LDWS^{q3MZ}92(N^&Dd{z&A5zawgx1;&s`jp)OZ3f>-UGG32fV0pi_oBJsjI=o~S`?OYvoTJhx!|W6n>uJ&SjJe!x*S>_mNM?6zwe{3i&2K;cQ={~mb_{+ZnYV+7pP|@>i8gBfDjI$nc>W|IfOn0Oa0}(e})i#7JV5OeFYYM4t|cGpFkVIGH+$AX@Q1e>7M|76rg>=)yb<I`UEWVP1dMd=xeatYi+6HOYqBRJGdS7co}^KewubxA%v?E!qw1cVZWW#(CTm&`ZNO}%=TJw5X}S!(2QuNz^%DffVNhED-yz$&=4GA>?)y^Vd<M!=^xRWu=H=4fSyO9wPES|TzsC3&&qO*Tw4?^0%xG@xzTcPIH1>x7HCUYKD#HN=ey{Auv}N3&&%^!ZmyAQ8=;M18TaP2PxJ*??(zDhYYf*#Yru8k@@RHAJLUR(2S49IJ%w9SMoY9YEPX5YU@JoSMYJ~jA}s5btQC*a$GPA#Xg#<d>4oKAM#e`pFI<`N4x`23+X8xx%Z}aw*Pt&RLmR+ZsZ$Q(cDzRddd+<ltq056F3;vtXa`s(u{=kMvKJ7RXRYW6cn9o1e>=h-!2_sM1KM$0;MSTg+6=xE&X2Z%^TVal0kFTHD9t!V`8>*J!m@{v{lQH_*x%<&fTzO4(I`9|?m&ObGvz))xHwu0E)M(m$K%xNas1Y32e<?I3(K=o_BtidH(}Xp$-bm8dn@5>c*Edru)m*a4=2L1kCJDN+~fXy5WXL+3EvNwL|=tPTfwc!uVmoX{!BO$(0jO6Xn$DtgtFiImk{>%jpO0T@KCfLJQS9`khv>!_z^<*c{CsVeBjnzBOm?OgeXBBOORg#?Fak!MmF?OxCndWqG*8oz`yryLmz{sz5g;^|1y5U8G`bAP~Ni(eFv`XMP)Dgp*`U|UgY%R{eaeY1Dc=Znkd>2?iSE#a*$T85w0K9*9=CZ@OuG$&0Sn8X@whd%}{hO+&iGJ$;-8pR`><38HNsp3wbdpps(xAb>cPPnjz>g_=A8>UzY16t#CcA8H5gjM+fvZ6}eW@3O~a&{n0`2xPZQ<F4sz0;aveeHf<QAw(#TR)fep#F9_(onvtjEAw1UO`CdE`)Y>$txe|HxK>NbG13ItQ$y4$W9u?4eRUl8vqXKiL67!}Kc?f4DuXd>9Av`jm^D0B0l1CZpwu}0SN?U~=BCoD!J9uC~=T(qAB@f|NUNoYw+Q3cGDsWTy3A7me1Y7~V7p?%8LGOUezy;ADToBHK{u<Dn2hNFp2TOd%To?TfmiUc1Et(M2EFqj1y%Ww07eeoY3&Ca4;&55GB3c!$2-ig$!*$_iXlu9`{5skRejRRyc8A-+UC};pSGXrS5bg>0Lr1{<;3)b59EAs?qv65uQ1nB1C_D@u1rLLVpd;ZS@E~+JJP7WO4uJc^ebL@<U$_U_4ekNIgLZ`9f!m_3V9_>k7B9*L^_r0Z4xwQ<1Xn_zgDb(0qfOw);b+k1@H22d^kujn+yH$QZUDc4z5>4hH$-288^ZO`7vcKwv*`2ivv6&+4qO|qjFyKh!w;cZ;fLUi=+1!VjIgX{qSN8s@B(xUyZ|1D4uQwPqtU+bX!rxP2mAp%2<-|Ff_tM~;+|_=crJ>*4ZjC>Lp#IW;CIn?;CJEo(eCj3@IbT=JP;m<4u(g<qtFlGQSexF8ax)BkA4Zyhj*be*LR^A;L40&PqZs6_lR862%QE?2v<Qrgx{w<vSttDIU_931^N6#(n@=Z;S1l3_6gj2R*3e&lm7Cb6{6koq<@3>!oT8m4%~WH{L0Ur8Ncrc;os0M@Ncj@AG$C<ge8RUM0>yz!uO$lVF}^l=nz;!xGFjZmJn`?PKPCgTcbPS*4$H_P`Tea5yIWk@^E*!4_XKA0}n)>hX=wV&==tm@CWEi@CWc{^c8qC{2}@({2@FFeHk7Fk3^fpBjMp_6L>g00DTS~0QW}2aBsL9S`O|8cSN(m9pP4}+yla2c>04E$GkY<#gATW^5V9j_P-#O<4FkTM(4s3!VjP^c&4ZK2ldaQ55%#2b~ic)-s{CzUTh<Tx1&4Y?Qn`0%e?Ed2le%$cgOKE+Ov!{319U5U%a^B#T75U_u^;t0(^lq!e^x)ytw4WaehwqVuhF2Jo;rG{owb}?ev}KPxNn+$H`uNP6)3hgx8@d@OpGJngYvMBvF>=3OLdGY=RfP2;p}L;rGyw;P=sq=tuBtUbOI{1|j?yAzTw}3D-g+XiHf7>ICDt7ygP6-iMxqMNh$^U&CM0?i6AN-X+HKIC=uk7Sv;Zi8&yjUE(uIvk~0{%Y4Zd)bmj^AH0k?xfGoZ-xJhxJwN&YoWl6|^HVs9*oHUDyM7h-hUlko44#RuglEDt&`;nCUR(|6`ikbG?sK?iHaY{A`8kU@I*an=(m&E)ccZ!BFIW#w5=ntup3LQ+h?96S&t=}<gXV^h1oi!P*o*UC91QCFO!N@^J$wN@3?JrN;h$t2gZiHQ1^$^3zJgwYFQY%8m*Df1cO@>Jcz=0qc+}HB(MMnj;Xlyou!Qh6v>II6(^A|MwcwhB@MCC6ShNHzS_78*NA9Ed3E}q$;djv%u;^>BXfL>f7vsHXkB)=e!*8Nv;Wyzo&@u2-FJ^l&1)T*?fhVIecrrW*oe9hOBJ0cyLU=kMJPn-yizdRNAH(y#nCHb}LU<7&ybzrWi_U>X7r@KC_{@uC=o)w#ycAsxFNK$&tKd()SQ*r7_Ih|7A-op-1QuNZi+&D&5!Cn0CiF183Eqevf;Yk&(1Wn7N3t%JCWK27!X?rBVbOfBXbJc;>a+&k1h0WtqZ{GX@G5izENk6gtZmm=$NoT925#L`E4k-ZlJ-yZFIeWV%te{AGM{9APDaNDZ_Pd7Dd;$O9M=lV+?&oknh(z-rZZner@^8h!yhw;gg5dWS&A-$XEV2EF+XN9cSK`xb4hp^It!k~wZbyD7csv+g;x@bm`9=uVbKNf0_K+RQ7^W5aT?tXpN79Bg!dD|JJBuhPB;lY8oc$46PD-PUi3J66h020MNh+L;UCa%;UD13gz$NEKYSiOi0*_B!W+;eSoCvv1H1}d0k49WpbOw7@Jw_LJQJRTehg27$DoPu7+BU-ng3t&oIc>iS}#5$*5c2A{r$&m_ARsVHxg^v<E$mG<HP~>Kk{ssXZ!{BNSD}0Tq2FXrw~1a9)J%}r$gurcn0-9#I=XmiyXoimJlw1egc=E{WZ{Qfm?e{;nz@kw!TIP_d?%*-=IH*WzQ&kL)jzBK64+u1OA%%Ci{U@Liii>M_BYHSo9n$djol<K0>)tk2lfk!CTKz;r8ew@FQF+yw!_iUhF~7z`M``=o$C`{9RD*e=bt5i+Dc~-%;1^NPmtHK7}5GPr+Xk$LPCb)bC3|cr&^O_UpQt5SHiOMQ^-*_u?QSeAtW6(f#P}@P1gHSE3i;{NyEjNZDJ8{>0B0<My8y*@IrBJb%9`EPGbj_saQb9hw9uk!Brw820PBj`*BB=E1Yj{qQV!6)N>!g_edTg#SWo!4kEYQ=$?0QMd#8KHLEwk4}Wg!&A{2@Kks<Iv<`5FGm-{%i+(^PvOttFVOYyddB?=Lih-J06xH6Jc3??<yj#2-U&kZB>D~f4RiM-dJ2Bai>JNlLI`(8pMszC;%$C@8&A05bHRk%8E*a2{o2sxamVU;bH1MbzSjRI-yZ}5J==Ee-k!h0cdxYnTtEKGJoN*&{&>IPbD89KZ~_V5fATVKguLMm{2z~`@45'

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
