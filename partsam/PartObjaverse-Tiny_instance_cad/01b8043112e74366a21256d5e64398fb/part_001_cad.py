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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01b8043112e74366a21256d5e64398fb/part_001.stl', 'relative_path': '01b8043112e74366a21256d5e64398fb/part_001.stl', 'source_sha256': 'f8d5bbb576fa7e0dbdb3e20670e95b03c1afbacca77e105f64801f95992190c6', 'input_faces': 670, 'input_vertices': 438, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.48499923944473267, -0.12067358940839767, -0.43598783016204834], [-0.04337630793452263, 0.1166074350476265, 0.4395884871482849]]}
GEOMETRY_BASE85 = 'c$}r22Y5_*xW><@(IP~zL#*Cgw3UNZ!|J^a5j}bf!qLmBks!nxqC|usqGugtS6!=%kTvRRt1P=%?au#u-&`~Iaqn}Vdp*zhyuW$#&3FFo{Lh&)^JwFrHeD_a|B7klw^gdNq>QGi$g1Vi#s!WVGbkW%bj4vKf-Rbt`08J(F8jV?t2SLN+Bj`eseXZ@14fmqV=Yy$f2~sGt)==8A2nuFpJBa+kLnkw{3d;djt+GCqX+gG5$Jqfx_Y%*<*n7ql(&Xh|BwGNJDZ@_$$aauQ_TspqWqld==<&2!!EuaQgegyZC<|aeoC_Vj^>TU*G6Q5pE0A<vCU}j?ynrRQTg_i@!}gBJ>Xy4y<YNnkAYt}E!uOj<Ywht1MdDR{!beGcRz@4?>z6Eyg&To@8XxJ0Kb~=Z<4?C8T`{fNPF}Fap%Ra`c!;9XuDncX5@DG{`bT;`u!0ue%E{A>&Jda{>w?yPQ6{k1?gAUIOI?65utpeVf9OrmthP1y!S%IzgtCoV`7;2+R2-vq<+dw@wM6mk-s(1GN~V3?uyhoS`Yc3R?JkscKR;-fI9HI1O<uz+Y#}Nr=F;@?A%iMd+xPYMVG%z5uJT!r2Kul=QXL*(gDAE4BF%QkNC!?y(t*K9(K_OVM)k?uSL$DFZz>BeB<9}_*eg$EaM$?2KoIrqt3P3>*V#IKgHKKEQ3F}iTJultLvD*NvLBluw4AV!o=5Z^nqV^?Gn+u<&x$7>)NBv>bSMy|1bgmnQxGv^=HX9hHknc^$HY*-?+tUd413B<{K-ghDtlWKQF#<A`kNGK8z4uddA&%TnLlbwf_*`9GDArUWKoazi+&c`g8W*l)tZ=9wX<={WpjGT>V#b#n%Tv6JJZ*=az5o&`j~4M8Hq1woU2`pLj&xSAV$pw%Yx6$m_@@N9BD-1I4$uelEW8_kHn=o8?jG@NQZE#zl{x@%Iwq>w8b&y!bXF{Gg)n*J$hH{Cb}SzGq?hGir-(?Dv8{$V+_3*fa@J=f{cSYiqOPxDm%CUu*Z;&9}eIBKeLJA#T34V0P4*HC=rDc4i#+>1nBBe*V+l=RRYMiFWhN#k0iMGsU>)*9djXH+(X{pZgg79eo{syFD_Ww)ZV|%KPgrI4$j*n;^bpNkQ?gK4IdUiMz$OUg@?=`n5M)eB)I-{1NF<=cL`;AMjlAjcRLACu}F`7yc~s=&;1$xY`c1XH!VL_&E+Bzeb$+_6QHDZ}c<8*Jt89u(rD{`C9jMXT<-2^T707i*+@sf}5}RPPbjgA!8-+jR9+s-?qQxn_X+T`S!SF=+}%|;%k@IpiY2}{AG>Yd`I9!$v1~)JSBBJ;M;D`K>ID3+<bfHIq=J7b<Z!i27cRSXIy>9sOQpObD}?vn>zyI;P903H1iBWe~X2?9oI2$j=R6@Eb7>1!tWf0_Do!YI!zbAf4da*?VT|W(^lcQ6_>iL6Z4WC?X0s9^#j{t9-Aa0-!c{XKNpeppdBfFR&@Pj_#ThYU!OYg8%@MGXU?@%UKea7zJ6~!<}0T~e4|5m@r~BwkRO;)e6#ov_%B8y-%?6^y+<(Wl!UK`cZJ_*8jkyMIL6`l7VI-`S0dkU2<qgIl=Y*9??e8+>KLEC^|8+96oB8gD*TNe=<nllXiwPhvaeecf~3B6$bxh7_tPoj+r0X~4_oZ+_Z@)q<?}-E&A1!5PTDrCl=g+DO_KWFzlv{WjEa@KdzF*0Ue1cI{hDi<<XwDxP2P9+0P6f4BiDT`U^MCk?#K0cak)+6cUTC2&mQsZdbG4h>#vKizubxXInz&(_nkS1`URp<f7rUU@_NE-)bWTy{?mN{@;XiHB&>_IIPN*`Ez<7uYvJcy1OMLKIH@x(8ou`ew5MQJS#L)6&S=k>xv0NyT3gXd?U8?e7V22uNgZv+Zsgl0iSIc48SC8dAjWO&XtaOk6uCa?zxW`3*8q(3l~-~<X5{@%`m0?GK%F!BFz>-9P-hl=`>MR|zP&H%pJ*8-uY1I!&ZTx}=f%^q&*-x`Uq7@K-`3^DZpnX-`O<DTM}J3TXeNH?Ws+~+Z-V+u$H;x4cI+5@4ZgXhNwm~m_Xx-Ru@UM#+p|fI-+T)E{SDDCYYXhR%dRE4`qp;-Zobh;hhM}?+Ns}yZx*VK<5mil`z7;%C+e)NivA8=B<GiL;k_K!h%S$O|K%H{AOF5Y`wRPU{S+UK_O3vFaVz?Je+BM;CJjUWd{2!3=fcuXJ)akj8=MLKipqiW*V`NZf{&La-)Gex@fSv*U;AH(uaymqk@jYLfa8Air}%n8wjFZZ8*MRe?;eWp$W~Xz!Dv<-<KRty>P@*HFotT^#n0ftakm)o@23;rIB@Ih{;c!jTXVj__)o8h_1W|U+Iha0v_~@%(azw#IBvz3xDR<*3;m7VEWQz4VzcD;_CxzmhNDi0j<Ir_wE5s4TnOLOu~YQI0gUsoulxF+A!z^j=6fZtUL|S2?g8J{d=1(Y+X3x4G#UNM7wPUdnt*nO^o^JLV>aNpn+Az*`X=la^{xniN?+t(43Tj#uBCy$+lKb6T)rLau@L%Y>j=Nc(S7o|`d!Rdv6kr9z4TIFi`<HS6{(N$oDm}H#2hdp$<?<eOmXwg;&tJ-@{w`S3(|jI9QC&z-6idO_2R1de)-Uz7Y@lcV!B^<^&Q3TxcP=}Hmt*flTha`3)=Z4EAk%&yZiMrW8BJ|+9Q6xau|n&88L1<s)%p4S%q=C@(!O1{oW)<d+Tq)y4wA#_~zZmGCumMhthui@+o{?EYKK!#5?%koDkoh?FNo(k4Ag)9Twjja~9(hy9x7t_NTA<rm+ovmc08V@B7&phb>X!+ct+{9({LUUOunEaa$zsmG=Cz9>=W_i8{3!9FX^4!TQwRgrZ*oi}s18_r>@`EQDWl2KsgIotv*8+Obu}Cw^LztFN^y6)F8~_rl$G%+|#p_}z6^--zq8TG|&K;^vzLcHzDyXQZ2N4@ts4lWi^hcO%4i1m(y0_}OvZ?dpN?S#Sp9?}_!MP3w;14y^~j*C+S~N}^7>3j3vh^Y&srl(pixaSj<DBlZZ!b9M%dL*5Jr#E)r%{E+t-rB1tT(jMc%E6mGlhxpdLE#Y%NG-6YbKlm2>s@K2jn^WMM3D?B8tve?3Yn|_n^*R0=>WB1{b~>hcxchTkW8Sx>piYgwsGp@Bt_xWUV?3Y5i?92aM87`Zy00&=<G4QI2j%_im!eMgMaUnJOY-%w+sLmpUwpIMVYz=WyP&>#vxoTFnPW5Lxa&XRx^t%)>R*_ScHZ$tdzQnu#*R2B^&U*ZI&4}-e52dwWulKv)CtayeswA#`Fg{@F)#1)qMgydp<l))w6m_4_;!zTGVkWdYRE6)iT1zlEWWWs$9N`X!*P#wa`VmSpX51{?PFtUzgDm#=5g`^_?!31^)&T9&D?xIeEaTRha~UWUG(?Y_2Qek2T424@~zR|`H^^zHUC6{>pIlZEkXTJ#bjQzlff8g$1L~-Mjn!W@7jj`ww(%pQFh7KhjmJp{MN1EzuJKMIZh_I`NyBid8a)NMt;Ml@Ov%6af=NQ-*{9X{d#s1<3GkX$<@~rPq_K!wc6ran+}%#YFEZ#oFghDzu8mxpN7J(Y(aiXC+U|KSs(k%loxpZS4T_4y10UQNeUO=u}H)E>52VNn=lgo=jI39&aV_5b%OSzoey~(j4vR*_1_m5w`?zYzT_6)-nK!aynZrJ#=+Wkl|0vUOt_8wi^<~KSBAoOc;WMDQgQJeLl(hb@<{q+{=PiP)i-)SM1RYz5Z|^oNPOG)?_~Yx{<l!Sr7phtu!D?)K7Ix7_iBl+pKc(}PqgmEBwsU%;<$}JNxoTw_gC}si*K*`lZ=CQ^WL?u`FiR5;@c8#%JW@q-mmi{uapJ#ea69`Gz`!84jjWcdw;}p;(d!`AJ!KIx%u|SA8`NwZJ8S~?<HS~uYatwMc$XE3-<YhJ;-m9jCsuOkK?8Z6yG{AK*mQ~)DC`fPw}+`53KX@_?)8OxgyWA9n1I0JemiSFrEuf<2icqb29!$`a+nO4%@`H-S`pX9Q_#nvVP*5K0`2%%c_ZQxA=)~ow^R~v3)1~vW~9-Ke-9!v3pZD-<GAByMOq>8EI#t_fOJ~JO7~lM~;iHxBN+b-Hy+*W>m$~l3)8i=67LvjPv#K;#>FDLY;>`;@fj%LjJgW;v1U|V7=YBe@g03---Pscr5xm^{)8FiPEU=HwfqZ!U*y0ks9Xl>NT7fyL9Alsf+uQf)B5|`qpY5azCv3ZN<E|t}njXpqPALppUtNeI|SQQy7OX7@w3Cl5fVQ5#JWJ8@~7Q8|c^FlXBenjZ38d>)n{&kXzzgKU~MWukw?8$Bv)icglx4jtj_7I4HjT^$P6UA-`c=O`R;hR-pGhY45%X=x@QdC*-&fd&=hyJ=7EX=dfww+drI6bX))Q^)sj3{d4``zsraF^B%ZgvNwMFi`1DKig_t<2=mozw)l>q^jHtMCgOY<pG$nb(=+TR+A-`88IpgNI?3BG4#^W_9JDUKz)u&1{w8IFA8No4n=kFus;<25>e~Y5x%t+kpO4FUUK)Zrmw%T!`kn{k+YXJxdP}`8EqDTcR7S}+Bkp2e*6$SGuAP<h-B?#Zd|S;i$PbT^b!E=3ne6I2y79U6@K2~y?(H!--V`sKr%T=?x%zsm>~6lkB3^tg$9Rm}puaHAQ>Te<^(!Xz^#gU$p1_gfJGx}UIE*%>Uyirc#JBmh!TdHkgn3CWDZc4r!*ij|wNWSX%u#9Qcpp69s8bO8K;8c0Yn#Uz^7qLOTt}9+7T-QI0q0}wzF0pE8i;R8AB_F{p8`1U&lQpXWD)wy>!4Bm)e-5}kEd|`YT%3W==h)FJGQ6C^=|AI`1Nm#uMa9F&oQ)-W3kRlFBD&EyaMa9H|{@;uC0(i_nmxRGe_J(dkR$(-<B{K*K4B$*2CC;P4V}x#Ju0~xGCfF_7C{=E!hA2HNd*6e^7kKnKJN`vq-)%d#LzEn|`>jXxH$%t8XnDfcwKA;X8tJqE60A(jH^AhxALoox{!7TGLOwe^}a+G7|Y+(!jqrSbXc)Jh+YouSUP-HWEMe^O`xcOR}r4Ux~!$`od4$e8;n#SkJ!2rC*L&emH+NR7Cqn`XImfL0JdZl3j6sJKTnG9ybf??`#2F$J6e?ID9t~>*hujJ`WBX>E_#F*1P%E+1<pqkE)0J-nstRhmAt;yWGTaPnW~K?P-(#JGQPue)U|^em$_c__n~=;+vgXU|m(rEWW+a0o-T$B;veid_dZ5ulN+#kz&))p4bWEJKkhO{ZF}Xy85;<ncRH)uwJM$-y5IrHgv$c{ihlHmrrqjG6nnCfA!7N@Qo_pVI5ptB>mNz-@rIWMaX<Ostw0;l7M#De>|5TaGiJU0_T0$8+pGYun#_;&W^%yyWGR)(h;BVxp-h}Tpuf^V0;VjkbEs=B(76_mGSvxR;N``w@)?XSG+F$)Iv)jfA=Kh504YyUiS_@e_cI<eLmYZ_|duKbEtk9^Xmv$4!>6&xgHtae?xym0#Uzw!-3MS%kMCrS<2ya=`Y3bIoH6vn|Y36{))CjdzKc(IJEC3zA<&ydhu5-#Pu|+GW@n{@q8>zEcU&e#W0SCYl&}kbD%vdF;BL7`S5&TRt_AuZ4&0Mc%tO%2cj_!DO1F^S8&L474v8ltmoX_u@0WKk>`HqytHVKe?IZ8dk09q@zm?4t8afe(9PE`r9pcvX)w+W_hUa#PLcaj`>u3&-tw?H&X;AU#CL4;a%+!cNeu2^_bkTq*lo9yU446E4m?M#lvj?c6{sq{et#tPlVjP@{&t@5->;PCghr<lZhq?X!&KjKEI`_4^NzuD&cj);53lzX-@0ino{JtGh4y#4FXL-Xdj<JknK3@KlEk;2sgC+(U*me+(?tHbSmg75Oizpw-|@*K7WLC(eIB0zzi2x7T%c8MmHahdpA6sn`lDQLtXE_3+<Q=coEIH#i|?osDdVg^+JX85u841|dQtMV?HRG(j*G!{>)2Mg-s#r^uznhE`MUq22mI2z<a-D6`)=@;#mjiv2cN=z&g*`vZ;d?d=9|@nu>L+I;k?+1>zysWC-Q6LMSoi*VjTXiCcbT*2iosd6ZL)aAit-#`1-ofScmVP<9T|8E>hoY-Voz64$s-G=hI_d)&Gd``A`P=;lt!Pj5cp`^4EO*3VeN`C;TEW<#!jx)0NmC(maWiak#Ys^AffZ^X_em??^0<&k=!@;kP;{zV&$pJP*td-|$)|zENR`{0_v7x53w~;%nL?d~Y&&H0tEZjrF(lxjeVj&VN9AlK$N$^&jK=Xl-~|jKBXy@g21$<NLTOf1`eu2=TRS;}=N%d6O_N<r;}^&$=I<_s{)>IyMb;?zWKUZ@O8^&9~-m>E>HI1Y+HvJT+F1SL6oHm;PPh56s$KjyvQu#@|v4e(H1AR}pB>@xtOeUKN%4W}W9~f7pI`o@*@{iswA~D(o{y^24{@#rN0Uo*;kbXL+9GI9eOuC&m}WcxHVpzIiVS-*dGojP<tVkN?rP<y(jETgyB~{YvrT8$I^QeQ)ai;5fVEtG+c($Md!58<S+cRj-8pW=)UpvC8b1?*X+6-e_l24f$p2&XLzY;Pa+6=poLZqzZU$S;7PJlIg)$ef_U^JdfxUjP~q&j(N!&3BP-P`Tp7%Y~p;`H4$|>hRXNX+RfZJ?&D74oBDa&|948kao=QxKi@;1+nD_>BR@Pd>fBs|-~Y7wgn2)o9>;yKak(5f>p{$8p}(W0&gaH*+|<usj!KWj*IPv3dvI$O%uC8a@$E5BF~8>*!;c$>{H`x?++!y(&L0EeXa7;^=sVF)yZ##Avlf_)?|F00f}a#GzLEJ``Ci@(=?g!xFZRc3HDnx&_93W0qz3#t|H|(ejV5Dn__cBSHD|@hO@$s7)if2Ev|L*MJ}y7yRHpius$c&p=b-BUtDkb#^sW5={VC^Ii>3{+sQUn@AK6CkM6FNmME;(kxB)|PU54U{)MDg{<Wda91sRIHsUBo+avFx>_Zsw-23Dc?5%oIx5&0%V@vjWUzc3UZpvI98kT)|FZ(t~nU?^Tf-9cVLp2<)=nYxoanLLELi#&wfpBhi@Paa6!O&&-d%1}I#p*WbDKn^C)V<`TSp?D8N@nLE*`7k+&q4*E#Yw{oDPt;5n@F#K>hT@{s;^d-aU#d>_CAVZK?nxa=?n&-X9YIdZb)!+$TG6PF$tn~-Whiz~Q^+Y?Hx7p4v(#V6XUWGIiuY3wkoS{gshi2M<S6O}auhj?8bMaNm>fp_fuVQ`btZWx*W46_;$aNM1E@pDL%8M!FckNt4kY&_2QU;5q7Ef19YG#M4q_;tM4d>UM4m&POP)hsN?l7{N{*rKA;*x9Qhy>JCEuVXk#CTnQ2!u5A%CQPCVwPnwLsOH&dRl2l$@1Zn4!1^)t9Wa6}bkv8AEYjYEQD#0pz~qQPdISQREraiDad-$TP^H)Fou4E6JhcRn#BJtH|3Jig!}Ckd?-ecanEdH<NdeW2r01vE(S~LUI&&DMRrBszF{ro=F``o=F}}wUI}Y1E`(I0pu<W#qFuzliQP<QX7z!)*&|~*JCKIO07t)N-j+;MJ`RwOD#msOHND8MOK=ItU~Q;=@^PFRJF%h_*(HZ4eB62Bj08yzD7MuR(hO#jeMG+_#kyZ`5<{aHI}@cyq+3GUQZ6EhLM&2Kn^F*Vkn+KokCVRj68uHNF6{9B==z`?oI7WRvJL=O}0@7k!|FD48?<~LFB>YG1N)qG2|K4Ib@|v$ur0+8H%@2W5`O6lDCn6W+=Wyy+Ky`gnWtofT8#u^&|Nm+0z15dz@mWg~^`e{L~uc{N&0E#Vx4K$V&T?Taddl6c1!54yKMG2b1SfXONYKlIM{l7>eVltH?^Xk>kj_s5{BK$h)aK$h*l248`%(SaLjh9W{!qbSZfqc@cF1c@cRUbtYNqX!11jNNNCiBzX|E3waQ^7ejGdYJ0NMrsTHdMhwN@QtOeGRwaK+E>A5@R+^Vwo?L{QmRy9Kx{s+nD+5FEzZydEJ*wKj6f3<=zDK@Ay+*!8zDzw$zDzzxJxD%BKEhDEm%5$2m%Nd>p1hH~h8j**I*Yu9yquwU5p@E25!s*yk`3}$Y9I1g@+gMl;ndz_r8e?#@@Q&5@@Voj>R__cG306F+0+^2+2jQb#gWvN<Vf;X>NfIL@*(Qa<U{0B)Jx=3<g3&N<g4WS48?D#@5pb+UKWI6PqNYiTzmOk)?_}eQ>EXytlMw6u9a4IS?ASV&Wq|ihm<xXEA@9dzx-X!JAa;|N;{C1_Hj9X`|zAr8su`02XPNj8sf4iD4s^0Yx%N=C|*QeZuzqRC{Ep@6vtCHS-$LViW8_?$x63dzU+;PcT=M+U-nPMyQr%zU-nzYan!|@FZ;9N2<mjpm%Uwa>YlGSm^#Mt<$9rbAhn<6%k@QZS88+1muryX)N7OC%G63^r3EZsu5pU<Q$5M)Em%VzG^pCYJ}?x&pxz_DAm5?hBHtnZPQ6V2o%|d199iiRveLce-^eCI@jmKC@;>q=hGIK)4O!`OvYotwp?D#65m~80UPzuw9ZQ}{9!DKTRyv%lbToM!c|1dL2z44cggl)(n>?L7pSplNpBze!B!`k$Q@4^=lcO1m6RC&DiR25^Q{)TeyVR>>rT58q$^TH_kd>-^>L0#VoSkb;t+{;EJY=Ol<b33Bs1?XcYmvVpS7#`0Nd1niv<<l-*`L~->`(4M4J3CU_n{6a_aO&S$B~1`A=JrarL)N)<hj&v@?7$AhT=_BJ9!g%D|G`|>3Z^3@^*&eXzChrG<h{OjJ%q>nEC^GF?l+53R&p{@^tbT>R__cZsalKe$*!9e&puVn&jr>N>nSk61f0Faq9I^v07u9osrEMe`*NDFP-|gGyZZ$P76YD4(dztOXlZbC@#lPT$Y-dT$WtM86~M1shP<c$qzNCYSTl8;$sZOC#WyUC&(wMf00j;&rts+pCMm##ue&Y>fhwI<lGjh8jIWv#nl*!t59>0b8sxGFckM@DDFWmOYTALOf5t1Oz!A1b{!dt+i{(=<GN@<u1PIPu1U61Gm@?3><q<fAIiviNZpqny6j^Qx#vCPe5CGy$6WSF#akGPS1}YXV;pnYtB<+t=ZZt9C$um7zv9$ugyM13liHW-h~lZ#GuoHyk>Z8ai`tj#m*Ujxo#J&2#hYB#N9r|Haq6{IvB^+;o}oDPny&Z`^{w{h9zgMPhT_zF3B_u^f6H~3o}oAoLvaaeHF61Z1%~3<48@HZid!=jcV{RLq*ftU;d%{ZC?3X8Jf5L=5<~GEY7g=payYd!Ih?$fp?D)h@p@`U@_KS4L-8_(;`t24QyGdUFcc4_wj-yWKZ<KP$Gna+e4X*FGwM1+eOK6=+LEETjWaqrqmwf_P&<=5klRzclG~HNbB6AWhR$d}{f^v#+=AMb+=ASS+J)ST+?v{s+?xD7wJrI3vOl#A*`M5u>PPnDI5cA@ZbYq3ZbYt6^(FgqJnK{Ik-Iyi8>5;tsym~GGnzW1i8C5I;~Qs`a7IaI^mIlqXY_DJ6=zg-Mnz{7az;L96l5sQ%TSz)nuDB+oRgZ3oRjQH%|!MjXJ#n&U?|Q?%|^~j_M+w>dy#Wf^O19ti%<)Zt<>TS#Xg$)iW*v!T7+DL?=8wuT$oyrT$o(I8TqMss0GP+$llbv<h&d^Z)#4mH#s}ilboHLg_@b1g`D0QX{o9I6k8aI(=ZgLqh=<jBWGYJ&PeqjmvV;sUzbWdqk=QaI-@*8aXD%#mv`}MI-{yHDmkN#za>qswEx|I`Sj(V`rblw`wyW0>pR_lUf}x9bIw}-`D24N{^?bpoSjc2UkJZcyN~uClb)YB'

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
