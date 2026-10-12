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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/70cae8050a1c4d3abd6681ba892a9a44/part_006.stl', 'relative_path': '70cae8050a1c4d3abd6681ba892a9a44/part_006.stl', 'source_sha256': '7d59306529f6fd8856fb9bac2102ed7dfefd53cc185e57bc4625c1a684278853', 'input_faces': 736, 'input_vertices': 425, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14971809089183807, -0.3214518129825592, -0.31950831413269043], [0.26785600185394287, 0.3970772624015808, 0.12363506853580475]]}
GEOMETRY_BASE85 = 'c$}r22Xsy88}4_MQAhMPjH5@H=rx9|MJGm!ej=hKL83(8B#1VmL<tioN{HS?%~pdU`e2kf+L#$e9Sk$L-uHR@um4^5u65VF)_T_SJMa1O?Qehk>-#Kzt<q=6Yv5mTqgYJr0)H>V5M?*=8Y6?kh7Sx33il2jI@-g?sd4%D$>+E2)W)x?hcVI^TefddcwkuBx{k8-`qeI5(NVVFkg(xl0inHzg!K)QxNkskc+kgq_<(?+K_5SRRj*p3qN7^5ijMJ)|Hpq>KNi9Hs@##3k8b;pINLzV^!nd};+FTC!xA^1A4}7C*P9wQPyKmF<Lhf_+!}L4<MzXg8aMB**L<v(c~ZpPF&5J2$gFX5YBo)81olCC|KOAQ_wSbO6?eY=O5?WcF5>4x_Gx}z*%9v?f$P>Na6r?){nOU`r$wC6{7Y5P{2lL7G;Y2gdrI>uU39;Gzh$<@E&B$_Gb>TcX*3#vc(gytKYKCqzt{u$H;vW&?S#&nkF}r`(q|g^qsD#qY1|!KUE}uUS*JDKxxSi@eWd{M$$do2Z#HVL_iM+ENzwE{Gc~=vey85A(c4GkMrs(YyRFq8%`c^@#;q57w0_LLUu!;Q<2MI2{iBL{zt-+|8n+@}XxuC_1LeHrrTN=YH#BaC??nC7xsH4;WJ3Dn0F?hqdcCe`l|P{QZ+@=jv5F7bq4EBE_iK4N&DH!3pEJq&eeP@;H;etL`ItR7A$`7^`%uq;dR=4LKGZ}0;~ICR3_qvoI$qhV-o@6q5%W~<*J!f_<&Q|zxHBaGd9C-qe75TM|3qrsei5(F(SE&hqk6smxNh&Ks2~5owVd|kj7VRgKiYYW*9P^z&-UtdE3QZW2N!MA^hbZwxb@_Pmea`Kvr9cGQRA+bDVpBe*d<Zp-kp)pyZoq!ot1WK{A@FgJFniu{SMf%LcLN0joVXZU(j^xW~|frf@gcQK3n){{TmnmTCbk(SB=||6*axH`J3%}{W|d)cmCW|%VX?2rRB884br&d{g)_zrFqLW{|Oy5ZdCQXsPPi7H)%d)E+lLIWg^i|YB<n7z4mF`5fZD{wTA`jec9z_Yuvn*4fXuhLG-)U;mD^+ytWgo<u%lUXDf{x$6`?b;X{||_j4K`eGUutxvk@F&1bGxGTP5AEvFf}QlGoI<MnR6?l%QAe{)oJZMXJLx5n)U1JIuL%-i^R+_-a6%Wsu#6Qf>uzQ)}zJ#pQlOVB>+#vuPO2lTquxa2tXTOBm+{O%~~dE2Rp>U|0$|CYx!fAe~(*1x&>*Il2tD?90y-j{JIUgOrIMVIt*$q#4`!J{>99-D{$yMMdpW6c_ge7ZG8e;o6xmdC7I7x5$2H6MHZVQmk_R&R~F{;=`f`!?*X-&ZNAaYu!H8n=D6VLYFo9_8tfjOVz$5&GTByE`?X*?DlkN19^XNZzM$<8&pYe_2GwJ+o-2#;wE&7$1h$#dz}VV5Gl?dN2+JVcdA%RpYkbPq^PH)wbyOz1t%m(c!YD%ieRX##?OPq4hI=4d$;4nS(Xm$u$~xK60V{SC>S8uMn+q>-`6`lbNTq{_VD1H16nd0QHk&_JPmipYGSpa!<?e+_Q1J=5O~!JL!5`^LNE9(YU>|67IK2U9BH?kx_`3YmIjJjjjF8F4jWhM$_E-yiC8mF?v76t0KO%Cgz30=QMvuU_OnTr%RxnBt6i6WJcyj`kxPL{TMZOYCCt8{&SnA@01<!x79{yxf5?|+)lR-<t+bL`;j{}73l-cp`7Ek;JUvZ)wnS>1@#lzNc*+(<QBve(`mnOoa(YzKX2}Wd>$1>zpkEp*ynLO+KqfXqcN{t^hEmP2N(}8RY5!Hm_g%?`8DwzcT`9EpKfo}e13Y0`!Zt3XnEpRXx#cf3i*sEsp(xeLlH0g6yteda=d=-6{vBu_ha-U&Ua3`G4k)b6!mlCpw@$#t}OC-{4eU~!54`4&7^V1(*1f}>s1c)m!t2uXnp_D9C4Q4$oNL%=H}nA-l%gA?I$`#<5u?K$Uo_+_Fq@Itw{ezZLC}J=R-Z5T7meEA5hN$p_-539jtM?>%pHi-K2r@v^?{^M*OCM>wZ5U`RvG`ao7EPsJG@XF@FC3ZnKtW>lyUN_N7+o_fHZuZq!(Ue$jdh^4SuDc;-jA-xK!}w0tj{YTQ1&8|$<pd(a=>7#er?n~e7GYhLXyM%{llY5J`DG2XUWfqvRxxyG$^`!Eiq#c8{>Crw8D2T$a`x+2EOEE$l`%jxJx({E$EogcbU%awNn#=UzLuwGiwMdNm!O&A~MOu@Y4Ul8f}+>PvedT9FiT^scI{(c4b8@v(i_LnUh|IfPO*P?hXuH}dqAA4GTLrv7n`UmUPk9(jV7SuvM8_yx$u>KW|H}s3w^6vE2xHY`PNiCPlK)#Xv)@gZ~bU39xX3a8<A8Vm;JH!*^jI6vu|9+m8r14)K;`!DaoTS%XzICmB|FDeKv!nkLTyI4r;<29kT<rSMc#cUqHEv$ciE*iNSG_NDr~evFA6{15p<TVWezs42SgrkK&I`=HM}9-Q%zjtn*08qd*Mol1_HUlui}V{#r)m4T(aWXj+iljk^XyWMyV5f0cx@C<Sf%;g$fNaUwT;zwXx)v_xUo9|{VVl#wB}zb9O=V1V4b#f1lFHk-WoS&zSMn^74Qq@n_=-QHJ?Xb7?<J~q8@e(Li~9hJg<8FR_k^4=Fqt1`UU;v(jAO1Q+nugaJ%A;>3y8PjP+dFX_R;K9qboIjr>8cdv2%3jRSc!?zox>>%A+Dke>6Doh=3J_UF7Bw{Jbt@;EzQTZGSNwf-#cml#h5{;Bhb^~X;-E*eFyX}dCd{1%FKkfL$N*}b|iG{3K){lR#*Ud!cpA9zmlonc~q7I$f>dg?Q@w|vJjZWfEuxV>{G+R4JNunug}bcxo(^fj7~d-Q;H`1@=cw<qsHzngtwiRO2)gU&N9GcFbPodf%y-`_4&?>FMAruTMD)9<tXu|Uh&WYT%fZ(AD5v$D&4{Ty%v?eoD>U2j`IRn>Xe{`)(vXII_Mb2Z;<+h^<Fy_$e^a^CtV{|DchTJHTRXrB{vO;XQYWQO|P9T=BpjnVPbs8%9c<6gZ{4-qlg=QMLqRo_zt^}IL<&#BYhDH`8VQm^Z*oCW)?pm$N4?yxV$jg4b5UWd%kxHWt+`q6-e*tbl*JX!PUG+gV!c>fmrlT8CGZGVlcqCMZQr292v!j%acANxStgKLT>_VZSf#_h*%wY|A!HP!MMOR|kue?1iQOY;Qmr*7|y(E3?>Q_JaEcL)15$BE&{Clt@C9@eEsP5*Gc-nz$VhlzJ|eQx-Mh3V(2`|-T)Ud8?)M}n^V%xA$^FRw0w{dT-ZUw!VkD_v0corCpC%<%8DKBhg=`Z1HSFEH#Ch1JJz!hY-KBAkOXFWFej{r(-wUwa~+*Q$cuv>YXuW1JtfwU5Sol?>K=6ON+a^<Rs1dFJ8~n%@5{)^S^&VBeLeT%^|5-OLxYoHZk{KF+ob@z5vO&n~)+@%KofX!Pf?dSA|~e!4%m_UzTT)pI%a>)p2=)p(L?y8eB-4O-7;#qL-KuidS2XTHWdA6az|;C@%-nW5>srea+>q=fDVjTvz>_5Pia+Rm*(Z{}!xQmI+u?$|c^_txcg+8?aIr?WMmwvRCmZz`erTD@C;uij@j*6q;`_3s@8HtKVBusz#{o?|@uIc$NJV{IVzeRHr+cc%UjtG@0y+JCvn*w5}bu~0wPLi@CT9=Aq)^OuYCx*cX}`!^r8!?--}+G33#IC4Tiub-;raAxz@@y2ew5AEjidVOy0%tJJ8l&F18zmG`7cs_Eq?!#QC_G&+J&ugmn?+Pub`&w801nd`fztj1|=)8QHmUmDt?N_drJCE!0ymUz8){T5x|JJz>&BxjPp2qE{uh9+{X4LWBQRSts3(Vj#+J3A}S+Q?P>Y?>vG%p*c_v;;rc_ua5rS)8CB=SjbYI$5ocWK<L@dch&pFpj5r|}B$extO%I9IgO@|dqDCTRW>LbV<pul`L%z1GtGtI@8Vmd90PAKK?1Z8dH${{`d2Ki#yQyYJ6OeDXld<8Mx)JgFlwUf!Rf<FWCq2gb!WoiVRIJEY@))90wBH~$XNxc&R9AN6|2uWLIn!w(|f?Hhewj$2V!w+(%yao5GIXg?`MbewmE6xQ<_^LP_Hr#QdCXxFjYj*RrVupY{gPuE%QjtPh-oWXcoE1$MAN3P3=rw-Knb=KQ;2<@l$TGVq-&EMUiC)!=gW9)0a@9I2g)b7$s+f}U)U6<Lu1+dRMu~_F{_vVKhcic$CK02mD6|IMa^O(n)_rUzpHG}q(PjTD#cdSn`|AYP>*97ND{ts~OwE7wPf7Y5C&@b{}9*-NL?cDkFBKDW-=3Ua~UUE0alSc(HPV_6P^RC@&sLsn)>8Xe(RMhlF=v!?Mj_Vb5o#ptWjNY%=zLmBscU)DC8yn)aeYqnYTF<VZhH2b-k%0Lk%YCd1^F?C4cHNEg9nFRD>~K>(Kd`&6*Ydl)BalzS_K5#-1NoFGhH>kC6wVvoebDj1Icve`|BAPJuJ!C#^Gfrvx*bA3lQ&{LwtJ4A&zf_>F~9lu#(0(R9ol1B6!t5lYhm0wI92C2N9#2>$I2R~{l%F#1>=0#C&*|0EN!Po=M37vT!G$t9_eg6Li@AXpfBdh60H#bXFHzP_QKjuor~QXcYp1|`lR%jDE+>gH`b5FWsLLgKrN^3*A@HD!vE;=Fp@uv)a!gd3Fk@CfjVzkdy_OjGs^{y+q(v$f1P};^RJ`%U8K*pPTQN~+Hbm^F;>>p^@Y>xE!s_wo_fDV_sxheXomT6#<ny1eVvmyKQ{L3eCJ9!p#9X2&8X`yS3nxtzt=+@hs+u|ur9l}4(FwB)3n~~IRP4X7JaJi%`*KlKep?S^!3B1>vapv#Qg6Wf^*Hv+x5A)mu1%H>yEyJ_44zoI{r8orq_CN4!DAN{1a^t_JVylUrxP`c=crL1LH^GzW!Z=ed-_|tS8?L()F~{CkgSED=~gVJUa4u-0<(I*EI_)*Y&iqBn|Nlhp<nccIB+5e_k8=fT+>vcdlDFw;kFY`{04+F~96c)pfSx>_Eh~^z5kjf2KY9<<vLG=iY3*f62O2^S7gN;@s{;gzi@z6UJdYEY=J0<=wPBnB~H;K3_f%`=r&aF;DEigLZp;EzX%T;r!p2=7Z<c<qpzUTZ(<znJL=d?0g?kk5Bq*yR!Xy>2=Kwb8&95;1$Nt_&mDq{J6`-xl4hCIEOv*9QW1l1@_rzf5ZM_@L}ywcHgWx_Z=B^MB7Wq1ifF^%CB&qcjy?}Ti9%rbNm>*zxuZn)-7Mwz`C^FB8|JYx6pOAStuFnrovls-jJ5@DDuC6e6F6s`A1ryu1~D9{V@Mrxrgg!`~~gs`3dY_E|k-ACg;ULTAzl`Y0Q&b8{_<`n>WtwTRp<Qs%;?7@8@1Pq4#||Kk6yL#CxrAUV6W-H%Cr?9ycm@<J|t=Se#opeGz~9)AwjsCAGXRvjxukn+52&YCT$|&)5Ds5b+IP<D78!UcIjK;9!m0&s(Ei&K#`g5ssS^k$;K1I9CdpsrTo&avkxF$93Ok9lEFEgnQv_l>eL$`pc6@ooAi-|3uulfb*PkvDp7zeva}iIgauF*JSLE{`vy%{kRUd&i{#Xft)QgZp1Fv=VkiZSU;Xxhxj+&V*Chysc~n}--!DUz<&Q-W1O4!DTDW@RW7A!J@{YKalq|SN#m~8*K{4=NPL2N8#fW}OEWjZ^{#EueYh*9iT9Rc%VA$x{yg5}29MLYJvkBMUbEUdUVhw1AfD1k`@6%n9`*m7VQaf8(;4mU!4tf{49Kc+^Xtc2KaTn{QLfNN8aJk9#JtvZI@Tj?n`+$hd~;aSU;YyF<M`Idr^*qmC-+Rj`;~`%HSVf=PS*j>xiz(a8Lh&R&(BSc>2tWU3H!FubCJ(0yw7!14$%A^SC=EbYYxu4crN64=6MM1wz!^uS-aP<Kb6zC8J2=^Z*d&X<=fWKxK;8r#)EAwbR2Na_C-D=9$+5(@`9GfJkSQ|r}fow*eISypRaR6H{{=<qds4&(g4i+KSyZXj+%;n+^@-+k9{Q(@ir52o>^fO#-)5`kx$wIZ3ous52*ji?=|l7y^iyiG1ajTt&&UY-AMGrx+>g_^H68O!|1oubsg=9s)>DZOfiky9p_-4YKrp)qn;D#xh^t&4(ooz7&JlS=B7>BUd^qK)_oqgD%Zz(T%AC?Cp*3u<w<$2&(T^jR{N8k{x0IJGok!n7Sj3O9-3Rn9dok>#@jA`VSf0bnSM4d_s9GEbIs6B&a_3G@2@Q*5bNiGQ#5Y%?xWAeol+U&>ZnAGyN|5F_}ua>`h{N+?a!{@c$|BGbrSVs7uC3tIug(EX>U9S&k`E9_HD#DU&&_}Pu_bY{f<<;Cywloef-z~8h1}zp?~i@5Uus;D4T@z=NoH1+t>H&I>i2U6Y?K82<<RqA?zP3duly88pi9mW)%v+`=@SU8aJX=9@l)@f1&fd^Y6K+_bYDfkF0K}x7TYmZZ7#w*ZGdA#q@q%hu&%24)M@=&|MeL-AXVtU&kU}{9a>ox3tgW=CmQ$Ur*15@p5QRjT^C}u<!I6j`8GlYs8oJ*YVx-&b{~ZxSiY|&$H!ew6`Av5l^bC<A!<icWs{zpCDYf(k6Z0#>y(#KUKSmc=cl1ubmACVf|V1zQ(PyJO^pA0`tsm4}Gr2#z|Or)-|*}SY}R*oBlyMKRSIqaGm%XXa^aNVV!>P0M_X}eKc;by?}G1XTjLVw{EU+*YvDdcfM(&>qf`nzmShR4eQ3V3EH0=JsauutOHr~xwz8(gYjX5FXAn~#dUgg(&uXxX^#2(awOJc!RvLrGS&^(xUuya)>9t6(0($-Y20pJ0sGJ6cXeEHv}vHftFSh1!~3@(*q7O*cjEUJDcyDd;J6lpd2IxKcVZ9hfOSjqJ)BpRI*s)2v(MH1>YhP+x$_&+pY+v!YSxd!d2Qtk`2EMFGrE5=d)&mjrVZX7JNQ1uuF?tXv2UuPpC4+3dfV0%`;@hlk#E6Xc#jY;7w2JJVzKVoT@UTx%yfN@&PERqua=1Ce=$t!(>>7>@A+nL#qSPI|A6OMXt>7RjeK#QHtGe=J!<U2dg%Q){O)4ZTP>&K-U+-%@oI<nCP&L-f9IJG?;8%^#QJ;?)|t-ijS+904d)3ry6br5m=T2d_)M6mwsz5ab9zldJi`KYN3GYW&yg;yU*DI*KDF*doV%<#h`85xL7HyQS-i(+bW7t-k9OGaXIZSz*YPwH)(xlHW1P60U+c}@+XKHta$QFM@GFY_#LcQ`f7^3lzna!x+p}xrBAkatChB>-RewDC^@78gZ>*!(FFX3<{neeD$fwvtoF{YNVHf)X=R}#V>3b4$?Ny{-o(u6?714h3_D27$Ul{vp-;H=L&UwV0VF%)q58=7r&dYNtyni)0Pr07g)^&t^B_rm83ntzd$9iC&n}XlXI8XG!KIL(gwnO9hq4*rTALjwz{)l;e;!Nzr*SE*|;mv8y--tSh^j$`vJ`1kEdHj*HNIzwdjx&xtrEuMo578eU1nYR_zW*NQ60=KTACmG0<7LAf=TiLs>sN^Z?^8mIk{|J-vKV=degU8TBvHRGjQ{xm{wIk8tN&m9B(YYtn*YB)NgVUB4AVYpJS9AV5?)AONftj$UP#_b3I9k5-=c&+P{O}b!l&pf$t!uiQ}m@|@#SRk9c1x+Wbun+@juDp|B%Hqd4NxmKb1%LQ#pmdriANJ!Zj)3vUJI}Ed5WiNI0(tB%Iv?5`IDnU!z|nU*!E<ql6Do!t3Ze$U9gs>nP#HlyEeCDS0XDH<~_%T=Zkv{66YSdIPd}CGwYKgA#sYz)O(Dzaoo-UmK9{Uj`&xfD$f830J3t>(fh+OYpk&DdBdMaBq48as%E^Z%R0X5*|wl_o9To=|#ye4fr4QqU55i7h#d`O#>3XLN~|;>*fk2e4Y|cqrWD<W__hm!e=Sr%arh2O1KE?TI#n5>$x1c2)R5ZT$~avO$pbcS0`6zz1O0IeJSCt^mgQStoN>z@Bm7996f{_!sjuL5}rW`FQSB_DdB<iUgTbUZUZUdhLmvn&z`IB8F~s`;=(WaTvI6FJ(Tb^`c3jpKG$uOa1tfFntq;qp3ikPCA@|b-bg=7KFjC5krLib2_L6~?@_{8Jm7E1Z`nq&P{I`{;kxwl<nnAEbt&NrlyE^x*pm{@LoZD(&32QA5-vsw*QWcDec5hmQ^Kt&;XwKT@&LA*KuUNNB|L>bgFJ)nX$mDgpA!Co5?)RT$I_$8(QIe2l<*izxHG*WxgpzNXG*vbCH%{0?NWH$M}7ZM@$@a^E&M*7eujL8?KPefUO)*?r|%)}VSAlU2}e=Fljuq0B(~Q{lyD>^JcYi7yoT*{3MD*;5?(^zP2SCRyo3^7O9}6%gny=l|EAv~-(!3Ko1cXplyEb8MRG;9?`D*6TS~Ywy#l!c+kIn7xC$klixU3VfP|mXJ;|Qz55gkhR|X`Uj^7s}7h``&M+xVrgukJ;CbwpP_=Xa0K?(Pvk0Os^f9OLAkD!Dn(dU!rv!6_&gkvb-#gy<$N_aJWIe9tz&uU6|DJ49OK88Go{bw2_97GA%pcf(+V&AI4&%)0s;iL2|<Sp!PM=4<!B|McLMi&2$Je53*67E3>x1faUP{Q>o;STgLau~1Ifj*Ahj6RS)jw~Ke7GFSKz<xfE67ER}cce#=qu9?oQo??eus=PL9Lav}PYL&?ghT0b$aC1wLn+~jl<-{oTC(_l@?3HPC7etNU!a5^(SIh3|4n{G&fx(Ge@mC~LfFA^;af_$CnX#}Z%b~=aUp;b?oJ7}qE{h{=OVWvSEGcpQNoW6NcaX_#us7nXXG2?OO)_c`YW=yj3Zb1S@@0t3BRD{C+FulA}kXAf)Xx8Z$WOsaikO_+>{dTK_5XL!EvMqB^*o%Po&3?V>rG{q=cta!m}vhWt4CteI;3ZH93*ImJ&{&FC~jlBPWo*r-X;mgUI4F$iv7@DB%or8ILm1kCH{gKT*Ov=`OPPRPs)893?!NK8!5hgFKlWLJ9Y!gu7G1ZRjn?;&sSv$W1BXx|HxYlyFsgeX@85@~3f4xB}gW-i$0hkSyMlEZ&jqL#{;$*P#26#r?@O$h9fq2K3%!@lbLDa&t<!D}5qad@i{wc@!l)gPuSZPbP~mBa2()8RTF}*q7dkEMAH1OD;tT=cj}VQo_Y3;d+#CKYAx}Ctj}~B|MW7UPWI<UdH=bMF}6Hgx&NDWbsF2H~Bp!T+#zB<F&B(x8#!KPL%LqdQY-=0C_NZBqcnQ-kmJoiaeCuj}q=kuSOQnM(#+iN(pDAgdZ4?@M*e?@516Y$fwDBDdFw(OJwn@<n82Ll<-0N9kTcf@<H-BO87oq#`pX5Qe=_vI|C9f%<r3$n{pg4ObPo?!tLq7<Y12D?J42DlyDe*I$3-cIgC7-5*|(o&!mKx(3g?L6Uj@+t0>_$^tEL11o9g43QBk`{d=<bF!Ee-1SQ;t-h?ckf!v0in-acjz-2xV7T-y}OFl#iub{_~#V3<jkY`iE5%dtUcwce^xj!Y`hY}t@2?x=;lf~PRgUG!o;coP%WbwM>ZsgXKa3e~%3MK4C|As7HmHcU55iU+IL$5#<_aTedB8%4`mm%})U%52BHd(v@xiq;vC0v=_oGjjzT$%hWCESiaiYz{ZEFMf2_a(O@SEqyv(MyrV^OFmab5X+CDdC)ya9(;rvUo9aUUEK4I1eRUm=dl?30I?pThi;1#ru(4lEW$CdGwiN@m1t`<V}?D3HmXzxSM=}{2L{l*#rKbEH3j+W=gmYCG4bkB8v|uJIUiI;VAk@viMMP6nQcwJb~ViEZ&hkfgDN+`_rqE#WRxq$(1Q#4@&s90SO<W%e*BlewuuQoJa{TqVFY(ZznGz&!U85=)1_`2gxzyA1L7s^mAnK`{WH|n-acGe@7OV`RO`83qLg=;jA8TAF_CRa#nH~O4y|LC5wlVP4ah?a5wsBviNXvH*yzBxH%=<pAxp{Gs)sh$QF44B^*y*MHXK}jwib);W+vVviMwb9C<b+98QlQi?<<%lUq{4`RKXH;xeD*<7eUDDdAN5A+q=iaw>T}B|M)#n=Bqdo=+Z22|MZi$>M#;PI7xnxGg0dKnahegojhYL+As@;z8sg<Uy41V0tgIcsKH3@=!{61SK3u33s8lCW|*BcOkc;giT7gCM8^sUWF{~MgBCu3YVZ4r57iQmm!OnB#W0O7bSm134cv5PZqCC{+jHdgv-*uC5yKsi&rO$7b2G>7odba>AA?_*~#LW$l@8up5$zla8^n<Jth3<pRfldoQ|G}oQc;<M+s-9gmchylEw3qbCAEJgtO4|k;U_nvyi`_gfmjYxhdfy^ulEEisT|>Z%Vi^CESn_ZbGj{7H>&zLheinkEVx{#pjVnlVd62&Gb!V@e}0D<dc-}L;7!IahdNQ^0RPGO1Kfd4q4nuZbTkL2~VYuCyPgsr;_JU!VBq>$>I~p3(0dR;YfNYS=^r-NghH8cc51$i+hkeki973PrsuO{`5N#;UDR@4X|G;k92v{|DXO#umAZ^<|^aA{)4ao^)LVXXE&e!<-(77{pUwGeyuV}oBh~H(&?esc^T1+{{c0U2Xz'

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
