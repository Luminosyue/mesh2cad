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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_016.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_016.stl', 'source_sha256': '9872a4c8f752461348222027793353e35ed2ace2a512e57f6df81ff1e2833f1e', 'input_faces': 1292, 'input_vertices': 870, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12131836265325546, -0.16059836745262146, -0.46267378330230713], [0.08373842388391495, -0.04733465611934662, 0.27481019496917725]]}
GEOMETRY_BASE85 = 'c$}r3cbFB$7VUe^fPzGkU_clo3W7*RkU5ehiwc4uFh~+XK~PbG92Ksjf(nXW6&w{MBRRty6Br4im_WyX@ft9|MGS8j{o8fB>hvG)dyo6AZ?9TwPoI5uS65f}fVXGY>>}lZ@K3d%*7I2-%3dA>1|@^?!7ana-86E@u<;FU7<*e*Q1*mw{%D-jqj&e7S7ima1e0nH9X5W*xY`%y)NVbzMeXx)Y7ZYX?xt~rZx}RY+|Xf0?>Kn$_+g@tzjpB0VKT1MqItvfavGm|Ue1)9|HnV4NC|lxOBWPKOh33}tBJ|0Uw@|{q9@zd-Qwuy?cQ!;a8j>rvHH7rZI0?WN7rwU9>1{X-?4h|{2WKu&-L?FxA}8sIQ0bo{Uu)iXTGabXGXs2<fqE_JfY{L|9<&|{zl*JQN8fnwJ$~Wbd4`gd|rC;tXJany!thr{GdwVwrHJ&Rg3P6)AJvj`A$@~=j-C~`{MNUx+zY+J&#_#>VCfVA)_92ttVafqis%qwzRu1s@wjc=k46+<{y2%AWly|``y;4Zja;TtFHOM^NYjdv}k&w|M@GvOh@(L)SF*+^x64N-%=OU-51rhKdPs5u6NFFVdqH&aeBIE%WZMG?GL)n2md&#`^T~KhvNiiUKi?P?s2~_diuj^?)N=uursgh_f?(qYrpT8mpT0m9{aghZba99svdmO!_7ad=Zgg~dh*qY>8Ngx<K?Ta`RP5Kob#1aYtX(pJvr&OccQwUM?c?Q7n;8{*O`Z@Tl&q3(}S|lO^xb05B+>QZ#92WGpGN${$%K^KUVkFs|;Q9Q#G9VkTbI7i*b7T*9X#3UFV6Pue!}2eU?*adRDJ}aeDIIf8KF)>deU3`-SHBE$7r}=Nr1#qk3Wc;?8;3`-QLT{X%vB{^IMJpQ`@HR%bpJUXvHAce-s{ZbY~9*~_;&`N@jEh3hrzL+U`i*#$9ru=V^qqq?pGe!g8F$WN6yywy1`+?TEH-LLZt-rDN)f6?gPvHIy9$K*zIdtSVJt84yUtF}7VseUfHzu(9&G0FMdbknO}jMMXKU!RWZcKts->BTrbIk>x%Z|@6UzFmL3e0yDZ^{8&^IeKIGxvU$>1;@7JMs!^td|l61&hNwa6~ySl4L`mU)$Mxt!Oi>P^x(cvoP4_;dii$#d-*y~GV0OwhkA0J?&8kdUcVK@>K)Ttqq<#JpJ|wm)AO&q!pXPms+X_2pKq@VuO6#YPkx_s-Rrv7!i~8R-Cn=wd0ncz*TuAvLki;blJ#$j=G)_!>_4g?P9OODglN9~Trc11UcSBVyn3uoJ%uM1b<T^<L)EoER)6!`Ezb9%531YaYk!t}v?cnzQjeUy#L@LWJK>(qaeDfV5!<4=eqaAM_WtV~$L<gHICJ-IapvLo*$)@Q>HBw0j_UsX)YtX?sJcCmckbJe8>1)d-@eJwb^b5i@JK<NzW<+_qq;rs-tp~v<sIL@zx%phzrDV^daUl%W3MBxpH|m?-uYTsr?-Fbb=?nG-P=F-y5{FMTHwylPyag6pA7x=o|~e&zhCur-G8d??^k`@&$riwSC7@HC#UB8Q1|w?zOMUK)&2dguWNpOl_#7&=yjyJ*5m7WSNs|7%m2D>cT~@rvN|2rlYiakUPm?G-yEygsJtzz`_C^n-+O+s`8uz><6B*i|LvXb`g8c^MR9u2>CL54-L5lU{{QxGUcUD{Wp(d)D*4`R?mT3_l%ca<Qr+KQW$2ney|;UQm%gzmP7m%FyELlX^X}!_<7@tn-JHJJ^Wy2c@6FJ4-;3@)kNdiRoQ(bRfOgJxVf&2kKfed9o49?@=T>z8`6Ai$0%sjg4!V7JRJZ##^!x@5LcPrWFFDtX>g{T{*GsiJ&UK;h0eoHG1E}u5H}G|vzc<^tev{w5yDK+F5ALb9C#vgp?dRL;o&3CQe{6Q<TZfGsV)bk0Zi?!5K5V{qL!6%e@jWNso_8-_bwA(EXRjWsQ%|t+H@6<059t2;jr7C=o1^nV-$(hnzK>Gfe}CocnxE?M%I4^K*LkJ7-H)LMHP&s8&bQ>YKX%3GsrjY%I6Ct%BOhJ!(-mKE>ap)LJzbweGxB*3Ro#F8>FfS+{O8$Z*=6p$x-~akuY7&=@ugASuK$D63*+?Q&56sRx?TUhd^;b!d^@kadaSPXeDiO2o^;*0D^AbZbmpF@Zs&=Yue#=^9vbH!XUsxJxB2MFX`|iwcILp%v3i}^+oHN%59=P@6sw>9kCSiLNiW~(UcQ~@UOiUVdd3cMK3Ctr`MSP;Q{8`G=j--;U5{SQywd$!hR*&?b$`E?p=<tyUEMxc{b5&}p1=F#JyG5E!OK@&^9yUWb^E||r@H_9i^6g(-Rqb4%&PnEp9{aM<z7cTkNCPikErfHzxcY%Us1yCvp#R4`_G&CPZxFS*LkkG)~|Zu;|X`&VE^Omy8lt#-!J*P-7mHOcvH0hd5600iPKa6P3(>8dS3i|J8#Jkn!mRx+GpLb`nv8{RrmL|zOMQC=k9ioqkTsA--iU%-*Uc}{XGS`|NEf)tZkc|{_ArGy8k?qw_tX79Nk~F*uE=P|LnXyQQhuy+RfM%r>FW~;^f<Xj+d{xpKtedem$yFPkP=1o1FQ%dtj`dF8#Bk+j;Bd+x?#A-#o>g5A;p-jQ1x+x;US!&r=yX&r_=V&tDlj`8iwaILApozH(Qbo>Q*Yo~Ul`BhO9R6{qLjpLFu=eZ<SR*O8ZR*H5n=+h?t(&+(1Ub;|oCU)T3bs{8Mwd|mSkkL}s$^he*bq5JRO@@tIU7@g<3fAe+SzggYe@A<mjA6B{EsYm<f>-m?J-W%2JeuKXGdf}UOoP4_v@$yyo^R*9tJ@$U5^_())`CRRr>i+xooZD-J$MK$zd|jV+RQI2ceBI`^E$*IQ?$^Gq_iNSt`@65({Xoti8=~i3pDV5IJ#VHT-n_w?x9lf<UH6l!`}<E{xBJiL4{mV2uRgz^`_C_h4QFm}`b?dw`|p<u7j$>)Z?VwPZJp@J`CXiPbp7;oT|ZU#*IQrL{QOI*JN4N20O%R-2af)|KANxhcVE~0yXyXaz}M}5U|r#Q=X=oy)ouOg={b9yeBBqR?(dg!E?eW&8PxiDSDc<x>wG8Q-uJzHJAX94!ej37ho>Fg9tS<OWQ0?H>R5%{ae7|s%1*w0-t_YAIzxWpvqRnQrTa#7|9L8>W<BR~ZT;x>{)k?<GjNWdJTNp~UsZW;RJZdAJy~ttI_Es@n6M{K4^ArX<lB1C({(#I`RVZ=?uyfsQ!m^T)$P2Ux?oqFo_DO5lW*s(mv85}mv85-SC3s!s3-sF*=wEe+o4~qp6XP4Z&bJQt$6O9I6XD3t&?x-_jEh2IDWA79QSjXZ@#YcO?7{M`nu+)Pd&KiL|%th;rZI%Wp7l^t1{{3sGchF{+hV!*VpxWRNcRRecfKa3zw~N<`3(P>KW_L^m%T+){ma^b#1r)p3|N0oA-HzSUov2<>=Z6KVNmtFRV7!sYkCPU)SqJb-PY_`Tq5l|DQhY@mp1k*PGnz=-LNA-|FNiH{?3!(cTBqGwzR*YB>42{$%L7&Y;`%$IH)Hmnt1y?evXxPj!Di%v<yNYUey|e9h7A`9e=kSm7K$=d?0=<Mh18|K;d<{NR^=_QdI_DRZ5C{aim^bwA&p7q1@GwVt5COs7u$UaD)p{l2yDUF}@IdLKmh?~lPRH#*-dCov~hPv7vjqwDwb^X+;<esWfOxBva;$LjeNesy%)A1_~Zo1ZA^9-sN2q3ird_pg@>o&3TDAFYb^LDvUgx9bDCzn=KI<_9ASRz>U7bxd`Ceao*p-^tJa?fyM+df}uZPQE>lr%u@us}C&i<lFP;<y+m$x97#HM|G_yI5^e)T>ZZ28TX?lzpad$KfbQ>L3Mxr_`1#SxN~LP{P%U8&#L?L-`DN@KlKHtPQ6Z5_pjgN^fAuo`ntcqB}*5qFww5(FE`s9)$Mw&`kdn@^kkz|VO`@NJx~zQgZ>LvIQoM(ykPY7)K077^kB`H<xxGDf71!wuAe*ihwl&3?K+8``r)zg_&WcoQ+2x^(E5+he<50bPX23QJ)WK{KEl!Ud-?gQ+x$g8yb$eYYTj!n-dp;5@ZEwfQQhwMynMUfdimPV{9@ak&sDwfld+DjefINJ*ZkDFU!8v1KBMb=Q$4?8g_Y6sm8y3B!dU&*X-lHIy{~!sR@eNAZC6I?Nqv0R!Z<xxb*_`Ib^7_Xe)3ayba0Q;zWk;*J=N~2Em7U>E4+NWuh#s<eZoHUAGGYm_1Aw)*k{!*dwOwH4}z&D^yIWJ!uk(&FNo^-KTdurs;5d#U+K)NIS<|$)$RO259&O$(zzbLfBQhJemu|7^}5LGdLUNMdGc~c*XzR1x7U%Me`Mxzrw^*@`ry@Rb+69U`f-b#J`Y&z^gn0EQ?YvT{5G!6dCAB}xB1K84*PKIoD+S>-&*EiR1cn9x+JRSZ{Fv8-_*~K9EjC-baHh4UVgsS$<O)r8+Sf0`S0_&ar&2Qmqc}Yoj!Ei^Kp7`yz$bguJbe9ec86?=i2MnJC0qqz2n&H(W}$yUY$Ds?dSe=*!^D2bJgv2s`J0d@1fp*YIwhXrA<LpPgVNt#i*WYbjqseJWsW5e;}&se71VO%B!5~aYxpySUojmbX2$3sh4kc@`K6sRz<H<UC(`8*K^hV_21X+`aie%D(Af4c<{veQr(_MUw`YYaG$ogQGs(D`l))(s&-DD+Bem;9$!!8wq6vyj)ILHS4Gcb^6SIfqPl*r)j#a*oJYNn`?}u8Rrl}vzOMPHullcwUKgp7gVRynuG^ljpIdnC%?D!jy{9?4ey*Qyb@B^;9qi7xx9;8<)$P1OPyI1;RrESaCg-2nhxmHB`#W2ry4~mWykKLTp1vq|YgD)U953JQGrfHK{>`h$?(3+h@Z?cWox$t{;ol$d^*YDKMRmJAc==ZM^8J0R>i#}9Rr-cd*ZbPO=i>D*S~$AikAlW)WA*f1bzPnNQAR#`M!w!3y?U%pJwb&V!+FSkt#JRigK>JgaH*58_d7pdb<IzmGr>JCx}Koh^<VX7DQBHYwyzxiJ6Uvly`u*g-Q}FGyuH^Qh|^OG&vtY@kAA*gm&i{IobA-F`%GWA`%HAZu5Ld+Uav5Hc~rOSt(R|gFW=wy`ns*>Uklvzvu2}kT|&40L=R>zbk-&NyoT;S_XSU{biP-r{pZi+Ms&MRKrh^~)$Ql>dzZxO-Rmxo>h}A3`Bo=C^-_Ub56>MLI?o-d`_CyEI{AgWUv=(Ng(C-^nE$?>?w$_&bMQ@PJ_o}qq@%j_U-iN-cDeIP*K>5cUa5ZceK()yHP!v+xS;;eZlCphq1%3{e(^D9olkz+=Cy(tJ=nBoM^v}(Z@qkbKO#TxnqsR@e2%wI&d}NSs_yTTGj#HUktJ3;*WK(U3v%Q1Z)Yrw>h`+x@~uvO>aI%ear8MF-G7e}JaqO6-L6Y(Cx&(U`YWXz-R@_~&xq9vhyL?%RJZ#XFW>GT{Cr*ayn3vz^=vvn{J!3Emapq`lhwWFEMM3Byd6zfJM**O11I{Qp*Lu{Fsj>m>*ZUW{M6U&o#O;0&p0tZeLZ>qksVRpUUy!;-M5gR_v0nbyw&GZ)&1wz!pZ}}^T>WOZ^Z7cQC;_wR&O}mt-seli*sZ2)XXi*qq<%9TBR1p>A_=7Rz!8X?s@rkK709go$>0i{imM1HlxGia6if))gk<M+UU9-s$SUl)-Ye6JN~-c(d~1G>Z9*)=ArGg>fU>pyoq<a{p3B5uj_jr)&2KEzOMO&se9eyujutaL7ZN4@9?N@*VRe`ABxp;hF>1l?YipaTiwgI^?UXFZ=O@nmm8dQN%u>>uKOj`{r#1%Ykpqs{m%E&_oBY8??qMj-=q4v&2ROo+vhq(7R2fL_w!Y^*F~A>&&KKc_w!Y^*M*n=zx{)oZ?6}x9(%p$zZYoxxx3EuJeZ;LJgB<={FtHZ^JAw&&h-_nZ<&tjc7LM!)jvAdZ{9!s99{FRKK7_PPk7!}-G2{II4xKcJumt`Uv*t4lUZ}q(R^Jeeck`PfIa@ge&KvReEY#@zCQ1y#yuIU2OaKo>eS~QKVNk}U-yUp=c=yv$HM2zIDN4DUSHRJGJ3{7+1EAy_r`0Y^T+ld-GARzSp1?j&UL|aN`}sJit7GzO@>Z>UT$yad+GC_>i%<L-iQ%Se)6H-C+^D``n_9rM0LB5Eq?!Nae7|4=}x}g$9nnp?-zObc0b_NV|D6D-*mn6xjH{p_kSOkUU`pu-r475=<IV;_xD8^I{Ag$W`%XK4y5Pp3Gb)qdR?oYeDh)VymMYu_un6;gXQk|<vmP>&U+Zu{r5H*y5^T(@7BY<Jws>TuDZX^&(O(Fp0z2|^*OrgqhTM=?Q=AGVdq`$dC})zbpJUkIqIO(|5VLS!+(#7uE$qBz5KW{fAoEFhR*wB)&2L+89MoSYyWoETm5&Ss@wPT`rnm$uhiOTpY?mG?!N~}esS8`Xg`BC+2P-VMz{AJ^t>X~*GBsjY<_inRJZx)$r82JI`fL(3#jh@z98MQRhZ9xL7(eY_n-HDU7z>U^R9KiSN?Nbw?}omzg2zJjccQQ4rbL(M|JJ9>N#J}aK9JNBfhTBBdYt)FTSq%$=@Cb>+#+P`ntZ~Q{8_b=<AxFbA0w%XMXDManSwWV<!7<bNXz5zc%wd=Q#SF!PoUYgX;c!318RzoF_hZ&P)E3CEKIAo)^{g4=2_+=Y{t(s{8M4l2<og7wxBhFV!=CpZM9Bb<X$F<D)z8`FlG5HObNqFR5Pkq98CR9+VG;503t)BrginG{*m@Bu6&+zxq!}UeKszqyNAEmgFf{WCuYfK{4XV@T&wv1f7Y!;avn*;$Mkpcqu^%{1SME=O<(?B|_iC66E$3-ZT;VP02C*DZ$i4=ugEnyrlfhDcPZK;#6`wQ(H;mDexiGa1F6ngqL7!V(|z!H54b_9^p+Ho7g16r!qEiN`#vlrVxuocyGogUID)bK7`mCUQUoDIF<<Gw~3JdA^0v4`rqLhz7cP8BIMsO{ukOc@QsW+39dxH63_6#g6a6v@eJR9w+TL-@waHl;2Rj9CN+I8F_9he<B4$mAHkpKf0AeTR=n+rkpIbeDB3;nt&IDabC2E`&+xkiL-2>-8NLN?8+-`k<7nT*w=h19`pOaii14k9x6(`HLm3aHm&!Xc?o2P04`DonUMk<hcniH$ew^`f`n`#oj#2M1Ji|Yh_@<zMxE!7qtVo3Z3OvJa!Mhc{g7F1{=IG7w49^jqhkqWP;SB}N@SEWoely+#cr(TY)HZ>5GyE;V0l^Ez7vU=fFX6w0XZS?C$?%sLw-hu+Z;WSnHN5lTjTyHPG(vBLXZUS+li-aQzd&u1h_}HHP{YT>bc9c2Jds{1Z_Kzcy;NR}aW#6Wyb<F@^iuh4jBlft%3oysB7L7gO$F3jfM@s|!FWM`Vh{M$f=lr)#WVa|L2dlnc!r-WD1%=H&+xyq<mQJT;2D0BpfrAIJj3fqtc72ToRg@@)K-UB3x1Q}VL?yg0QhBsf%pUQ3~wN)hhGoR@KXiF@r&abo+bDvEA&k)PHtI2G5lh9hSwL=#jlH3mYN3O55TKWT?6UuKzgaX9^-oSQh9O4#p$JTQ^U!`zazXDy)8yBmDgolmtHC#z<2<CuR~4!skc9#;U5Y<GCA2{JU2V!cL|?{KaCv2dkK0cLccej;ZF;m!G8wN@V`vG_<!RW-a<a3Wp?PB_&2%jg?Gpf{SM?9Zt7}JZRg^(r{)i++r*~$rmlX}-H)7)sOu8yz65U?b<M_~jn|u+gY3{ZaW=W8u6ERIVgNUFb))WX<g}!wrqtaO&+xb9XWmbk$GI>z$qsoN;a4R>|0;3}KS$6p5&9kR3?C$T2>&5G!;8qV{=xqT&+zV|x6Kayw&WN-P|!6y^t<A9r=}+OP4EWN^Ii1a#9Y3g>1#Xs-j19P=xcTQULCI=J<r3>!@Go@7p3ne=8<dq+JnCLASa-&gXsGpymr)-i=T_vjhfrh+jjI)d3DCs>80{K#(DHoxv60gu}FmXVBCXVDj&pn5WQ5M%Q%<54`iOSq24xlhW{vQ!Iy$U;sN+)f`eJ1e-O{`*YVzjA7s1*Z4LZ&#)||i(O2RbzFM#ue>0xpZwOw)e+_Rnb-h7t2k^}Jkl-i5C&bU;p9;Rf{{qkOxAAtvzhJygunv74p5dzmi}4rZ8NOAp7Jn_C;kyKH;lG8qm6|@s{~T`@b$vl^zo3`O-)8(ay;Q!A@j7~`d@<w2^iug+#%t-N^0yejMK6_q&iHfs{RTA^Qg0!i;Tz?$d0y~Z5c0<vFBCk1{sf-kBLySyN8lOWSkMl?9iHJig1Y#1@eFSyXp7$#&+uyn!|{jXHKL}+@gK)Ce3RgH^ICwo2tH4+7=JOI;nxdB;g7;Iyn~=Aep5Wd>z#O25c<{d3~w)Jg5Lzs@aynK!<#UElG;WSuY<o%4X+UwM))Ykqv)mbri`1?OXbxVSEHB8n=o!dFO^@%_&R#2d=cYC^!-|DdY*cp$1}W_pp&2<{6fZ^1+CCq;Te9K;8grm@eD5-n3pi2UmVYH^Cy9yz%#svpcsBJJoBfVpe%k_ydu<eA^wGUhW8fq7qljJfp^8b2;QG@B|!!B3V4Q>5S)yEGM?e)wv>gRg=e_={{}e;|0F!aD+<cvm&ZGWn!4b3!K+AJUFmICda1ku;|lar`N@n=rkBdI7-!K-<tH&diC!u%&$v9jRNjSg7y4d~nmSQ$Cp^RdkPrB;;5XvW@ZSZ8vqJwcp5fmLzQ+F=&+rfN-h+S5c!yvQ`W`&P-xYj-{{f!i-w3|K{|fJ2>iUM-e#SH7V}j#?Ux-KGzY31xAH_5Ld%PduM;X75_A&f>#(M=j(Rbn*{*hom{(d~ezr*_vd_UtOXurU}V|<(%{viGy;omd<o?a?{pYi+jQu$8CJL#qJ{fzh1OXc4&{*GQMKf?G3{r-lUexu&s@C+X-xK@xyyc|AQa0UJqc!oC>G{$d?XZU+E7rzZc-^9k`E)%{h2>o5;82+x{n;`VR!85#x{7j>)&^PfLa`ULI39%7;q~JzDFXA=u-hv_cL+}i5DQJ%09MACY<ul$7Lf^#Z<n9)}JP7^e<QV>)V1E$$`|%8KAwSbBEA&m=Pi`-2Ye8%VzmXco5(h_kbH>f-rSkXb^ZWEt`Etg~>80}hjQ7(^<<01GGkU4~8phW!7n)F09`)wo89vlJQ<&!!;-&EZf}Yu--xJU9vju12pM_`m61f4rmI!?l&mwo2@MjaD|13F%FBa@fg#J!E!z;_roS7Z^ChjD+AGK8`o(UgpK0|OB@oM<xf&usg@C>gesES_|&+s?oGnOSn-^8lqE)YIE5&FZ)G5mGG(nRPl#WOrdex^!x=$p8d+{>sfhgbzZj2ea#`$u?H##QO1@@4dS8NF0KobhmaseCEprSwvH75ZF-UMjzu@zu<Q%GA`4di&uS-bc_;a3S$Lcq>7D{Q7u?e<`2wc_Q>ptWR!N;bRk_Kb9QBYY5sWLccwp;avn{@W<d8{)ON({Lk<VzmVFDZ{la<ULw4&paHQp{CvSh*`a?Cp5fof&wP~#eG@MtcbxF<iO}y(j^P~yH4~v<6VLD)1>Nww;Tit5;1K>HJi{AMoAFINL~dW|>qBf6;a}0`ujr-n?u@(BOXW2g*QA%qyD{!YFO?r+e288uZ%v<DGZzf+1Mf?04L?VaE%+f3#)FBF|0wt*5&ECt8GfDcYw@oo$M6#7I!J{6*?5NkDQjF2{33XUpCYJ?Um4HvkrGGXk09q1YBIHrB#wZeBsEnRe3}U3Pl=Eh3Vz1_8PD(=gpbA_O^)GJ1*H<9UkcCgqJqD&Lf^zv<W>=s#4m|w`1OKO_@nTuP}5KNKjB?ZT|d+3pXsIY(TqpaOXZ~)m!g--O${Z8e@1vodRvlSDj&so6ungb6XT!g`$%f~fqH+yGyHTxc|l!xX~q=<Wzfsu8UBv^+@3_}n^=b2`-MN22>r*%G5m7D9f{Dt1JCeB@$Q4)!FaD=H~MZo!^=~f@lD)K?is@C3Ca>H!cP@c$`1WXc!uwnpLsVC`X*K)_i^E~5}`kf9K-JvT#*R<EAR~ew_qmzOgzKi6YRs^hi7<MYBRox`^c?FeRYWyBK%$Y{4TvzK8x`zda3*h##hiw<ue)2q?gL~G2TZnl~<(C6`2c$*M-+3R)i-7%>)gJHQ*NrYU0<#GyFF>)-Q?BH?bzUtA)Rk2>n;cG5it1!bIpV#4~)A;AQ-m@eKb}a2WqEp5YCt&G;rBCbzlpiv_iajo`Hfjk80)F`nW7m7h712z?V9le<Is+C=EDCCBhZg1L#%pNnVstAaK7Yw!#|D)=4$cRa&uQJe8i{GHs3sV_;qAi|H(=Ogq|`C7(n>80|yjOWrz<!czPp_j^kXZ$<8RNja_H)1Xro`hdaYy@8?-gAN{h%?|%3hqsW{=ImHUnFRS-wMz03W786&%iT0At;Am4$tuNg46L&$1}XO;6nTh@yb)v4Ez~*hCeS@FL;1B5B{KFKK^_>!`qr(;3x46KTA*vzY?C|rwOw0v+)c+Q&17VBA($F3v%&u@y?{CdHD12E~c*e^mabIRGws<q?gJoF|I@}m1i@~rkBbqGOkE3mFF_frI*U*F`h@?TT{~$)cXXU;cetz*icZ1m;*moP%SI;tKk{`yFBCl8ic-y)yOq}$IE!@f{_2pc$#1d`Vu_D*9x}dZ^twIH^DFXzu*~OhuVy9;xFW0AUs!a4zVu0x}aWG=-0zD{FwaA(IE6qtViyP!Z!q=zkwXXmkRC<LjP_&!_$KG`0Mcu|F7T({t-OG&!INsn|OrWT<U8>JU7CR(&wY}QuzkP8|bC-yBXh2FO{!nyq;bvKf?G3y;NS8KG$U~7~Te+ORNho6z>he%f!v_R|H#v(BFb*_$0w?__yI1-d)fKzYm__=LtIEcf>Qio8U_PEAb4UD7Y2>R=jT1v>AUhp5bo_J`-#u?tpI-?8M)RXZTdX6#OZ8hF>MP6#r5@!!Hrk$FGlPcwa#e{2q9Q-!7PpKN+ttHSNIPfp<G~?WDIm>80{1jHl2`<(D$PlwK;Y&$vFlRNjMe4|=J5GULhgQuz+XJLvmFYI>P^U&b@Mfy|+bf?~uUf{+&%{D^O&@eF@R_<cd>oA@KVxx~wY(7%iv!%r8~2tvOGp5e^|J@I?u8UCQ)Ui^FUno-ja_&?woUP<)x1wRL2JOzGOP$DbzOORvuzeRr(|50)bze3P52>q6LhSwIHfqw>`;pYEgy#;;?Ji{Lo%*CIJXSk`!)b<#0F1hDZUjt(C2!E8`K1wf@w`AOsUMfF>@fq||c?-rZ=%w<xjOWrz<)*#|iN)Xz;O7%hftMHjNBqx&Fz$hWA=n#){$4!8Z<II&e+)T>pCzasgno5A!%GTE<Cn%W{7k_)_~+mmK2~r8{tb9%Qqvy%J$Q!yB&Z;Dy+iym2>Cw2A^bylhTkk0k3SyI@LGbi@z2IHyo{g}eknY|YYHmkSH?5^Cc!xTad<VU=}Y`C@ou87L-h6#y;MG)@pyWv{A|W&(@W*07?+}#$}2OjOfQv>V?2&tD*ux4m-KxsHGNLKpW_++lEjsQeB%A^rv)>E(4UEC_#nXm`~i4|pD)P8&&4ymil7dD9X!Ju2-@Jc!83fI;A;G<@fuLm{rLCe8NN#Js^DSbGw??Q&*DFeXZR4oVEn;&hF>hW0RI9!!_O5|#jlEIcv8?1zagIC*9h|P^YD_?^bGzpc-K(Zv-I{^dZ~Oc<H7V&`2~zGpqI+4GOkK5l{aMEkX|a!W1L4Xl|RGy8Tvkun)0bPAJ6dfWDZppoK7qWKSNL|EA&g@8UC^S%!fhfn^=n62ZTQrg#J_H7=DZ3&LH&f#4~)BU_SnQJi|W{e1QJ}p5docoAFKjfZVf%*B6u~o(V4_I4djk&%!hOQ~8;LLFk)!7P-#}pA&@s9C8f5OE4h_{Rw!6FA&VepN(huCxQd`2k;CpO>M?E@c_B?sqZ}E84-SvJ|Co)%I7eiLobz2U_60dDxb}GHoa7Sfbju(sr*d(d?s_@Bj(BJ^zn4Qi{S$WJq6u}NqBd`#rPNF8J;c3!q37p{9p1JF9e})VivhWg{OkhPmyEzbis-s^jF{+p2!ML{G|iqo4A79Zq$|_2Jp)Sg9L4fJ>cyGm*QWFXZXp2qWDGe3|}LMoDqb+iABl1L-?>D^oNmS_-esDLFnIuXZT6-GexpO-^6>!ZA)z@5sSbFQNuuD_Xsb_xG23;K7&5bpqI*rF&;)QmEXho9(t*~2z@R>FO~OT+=IE0pr&rr+YQg~TLm`=t|JbGj}i>SABJc6C4vt49q<f4E}wlW{;7C|za{!tLFj))j^Td@%Ho@7Ji|K*Z=V(VCYFU?M{OO6?crktw+V(5N5e-5uE)O~&+x8-&iI}23_nfqR}lIpb|&|0;co|_Z{lC@a)LjD(EpPh!@G#y3BMCL<*3Qj)`i#!ej7F1N*op8of&tgm&#2Imk^If_}h%%rkBe9Wc(+6SKf)<cA}TcM>8JHT<Azm*HQ0vc!qBmtPm_AE`To;Jcs`rp5gx%Jc|D)p5b>1X5i1jGkl!jcKqA%48K!w5B@!PhCe2li$53dPHI|!zW~qh7X$@@=ZVYU3kA#Zm*W{ePw)i(6L^N-Czy^u9nbKog7Ns{@eIFLFb#hip5adl9>;$i?_O$JhQAE&N$OfoZ<o_c<xenvf?g`0&UiY#R6d^ZczUUP8slm7Qu*VIAE%efmoZ*O-yfr<CDgkF&+z*NDZxbIP4G#AoAGbPGyEz+AN)RehSwCd!f%CV_}?<8tKe6`GrWf2Li`Ky4DT!PO8hIysX<Mqw!XwG;dcmT3T`1zhEEVo!JmR>_y9qF{Qh``UnHoFUmMTxs)B!l&^NI*xvd4Y@N3~2ezl+<em}g{)HE4?GTznHHHF?zp_j`0Gwx3>mDgrmn_en6HPj^j9pSa;Z7q7KydUF!^iug`#*^uLUuv32y%X^ae@F0&AWd8ke^Iaje*>Q3PYa&He+tj=hXfDfKa6MizXY@JXW<$CpkNOE96ZDG1@rOe<2^`C>+#p)8UCtZpI{^LCHN-6%lI$j8UC!`8T@DP41Yv08-F&Q;SUJz#=jfS@Sa_>66Lf1_m8P-J)bqA?B#O5y*zwA)<5RDli4$D+)X3-*VX<{y8jG2`jb86SoR-f_v~8q#NR_r$p6d(`@hZZIQTyq>gOu'

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
