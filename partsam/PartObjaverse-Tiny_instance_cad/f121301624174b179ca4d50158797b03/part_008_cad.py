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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_008.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_008.stl', 'source_sha256': '4496ae80354073d2c6cf47dae4157acb3c0ee392199b20be3bd49df64694796b', 'input_faces': 1358, 'input_vertices': 795, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0987323597073555, -0.15462331473827362, -0.37414994835853577], [0.08314426243305206, 0.01579686999320984, 0.14098644256591797]]}
GEOMETRY_BASE85 = 'c$}r2cXSiS7w=ax-E>SZ5xoZp1PCpn8bS!Bw*aO?AQWRd1krmlH4s3UW_rhT%RuPZhR_odLr4g{_mVev?svzU`Q?vy-t#&4e82nA-Mh0hqm{L*-H?U>$$~8Y%Ws_vp7TqphL%N<)(Wx)cMA*e)ur3OPy6;C=CCqKPJgz}{ia2ukTwo$ur;D+*KPy5gcYsgDq5|3<)WorMZ5P43lHnmw`0GsuHA^&>(pmpH^B$??9{)TST0uSi_c5B$`>!?8s++b{7WO6;F?%(Zw$3%QruQj-=HN2zVzdsLIWgET(V2!R_m5qq~5-x^La})%Q_*}L5<(9y-C(9SX$@BrfihjAXw*bD{mn6&Ksfgia)HE`f-lVXBAmT>N<Bw=cjr{$vQ8u==@C$$$bsRuhICXX=_PC^K8?3)`F6I^E}h*ob0zoZnsvtLmIF3dbP~ok#nuaf2c0G?_(pKug@sCJ4FM%&fhIo$^4RCbRP0xrR>jAUcJur&m{K_xuEk~*H*~=TJU+4#$7JSJvVyk{MPd2a=R0c==|Ff%cTDDO6QLkEs^siZ>e<}?_O}R)Lx-FFV=0L?6)VEbsq6?zU+tUY1b3?wSK-w@_d!H$@)Et9@6-Mt2{qv)YQ1=a2B4=dBXJk*gkUJCf1s+^SOECy!B+=tMm9ya^8lHj@Nn7G;-d0P6fnhyh~#_Z#|Fm>iqM6<@~f#2J3u4opn5popgTSot$sJ^rLlt`g@*--TJK5_$#;M*3kKSe##wke)_h0_53S0c)q>9pyyBjbTyCTBb{e0D!C`#u}b41edPS~<f^Fi^+9qTCi-US{I52VGJoy?okypZ^Uznk@M?`e`^GEzpf);R@NlW*ksEZLe%McvKm0@It8V`&_jh~lH5yMlW|3^?`1(4JJ1pm+XTouv*J(6Q_W!wee0<o~jOSa08*;vRLLVLU=ho%U+|Lz$l>HgHJvZ})X}0;#L&ZlOkolo^^7tfA_z*4mvcWPxbbsa;f9`pmhxv_C8n<dU+v-2B6hC}V&i~K_Lv)Vgw$*Eu&f^m0{CCYdq;vbYo$ry(yT-}+Z$&24+mGXRXkc!ghaKVfg}aE(_YarHXLq^Jb^a<w&hy0DwRC>^p`7R5L-SW?{7R_gR*_IWKV=2U-E$7>`7<{0@wxK%dj1kG&+}p>BQ<UxhX;1l`MUXXo`-t3=^V#l&;7r2zI!Uq^ReHo)bnv1jvK4<MUUk?_rANJ^Ry%6ao87}dX>f_@5p)Xi>R*iG~?uP*!q2d&d(f`^W5|MW1ZJ&JXh+ry!`$;@iWiE^vC&lTXW_?e{LU7tZbF#Jn^JG%>1E`|4%4aK33zo7RdQ#J#DJ<m?v_+`Sz6dX&m#-JG7DHu0Q%k|JVCVapV2vdKk*>FSSm#-~GjXjawzg@&7rVvoRXql8m=|_s3X`zo{nYvwOfiS;srKD%UrT4>mWC4~Zi)GcR3?-`Aff_%y!2E$g^&oL78v3VwfO+!?F!*ZhBud(c+yw{_ij%XXxkv5ohej}MBkE+e_O=?INm8+-BiF5RN@uhQ~<r97r{jIaCJQ=LbqlicM=p|!_)w~IedkLS~QrFY!V*GlSq_DcRguud(V*LlpxlU9v&K5H%izt`(qou9rhk0+jyy>$LMmX8m=z4mH+!wkti9VY4d<x@(YxVi8Ojo&`M+J8PMUUP&zp1A7G)bmIA<nhElE-8Mgr#zlmhk_zCK6RHop19LA(D|+Q@_6FL@kj9*_2luy3jbZ_j~B?}i92WIl^SndRvu40_<tj5e3!}Ni3k5zDBiueJf3)PTvEJPZ+Sd%y>GTk<I7$|$Z?7DFb}ND^YCRe{{E3FW3)f_g}jxYlZgY0Xxw_)g89vGJ%8?N`95%eJx%8$L-_qs_q@j4xt?*o-uHFhvNCg5r9Ikq*A?d1+YDNx@#oie$@bT6qUQ&nkUX(uq@Mp{Maf-d)@u3g=p2%VKDw^u`zl`DDc={(WA*$N`z3cBNwZd~f3~*dz8oL)_8bdjKEINl-}~<!vYj=u@6~wM&64{Pd+YhlYe??y(@W3ad~3U`gYPM7e4ivr?zuQx&;NQ7^MB9i`KN;=_tuNk@;$xo@^OC4EuBw3Be}25Q@zg3FwS39Bue88YVh&!U5<Sk$8p=0zr4=zeOWYEt78@B@5`=+9-UVWm!BiPyqk1Bc&|JjCic3a^926h;l}qY#RJ#M<D@$uf6r3<ey}`F`fm2nd9fM%xv*=V<d!d^c6_!!e-$@Ae-$@Ae-$@Ae?7sexqqr<m*ZvKU7~aQ^JQt-7=LcfEXK#@cK^g`JhTlTZ*Sh@&%x_Y<@>?cz$cFnp*0rm(fIAok|%cAu5qiuVLm=!{;T}IyYBIy=ZeQ4;NwH34jT7--%)Z``=J`Q9(cLEnUCmvT5ZX_m9FbN^Fe;U4{E>CpS$lzvSPle{H-0C`{ro**3`PpgBxl2?yei<``R6NOwR{TOfyBx_Z(^}d1$M*dcLzUA7{ds>+QL>M!w&z$R|24vyyp<qN}v}lN(6xJs!AU%RgI}j~j#9>G_?v@^N5fOD*5iZm8tG;K_RaftEbqBKzz0-{j)s558}z{5$J;9zIy5*MHJw8^1qp==qZx@o}T&e!c#z6nvcVrC+V(SLiH{1EKS(YTP=XjE@^Vdg^>WfB$lA|4HZZ{Qb)};iS%2%$Dy**P}mle*L0+Kf0>~t<m_Q!SXoZ{m@wFZ}+d`_Y<E7^K`q%yvH$lymEb-JyzpiyyEuk%;eL!m)qle(O1t8i(Sv-$p2qixuUs$R(IYn`}4rJyZyO)NalUAot<}U+*iLge?P7=f3;QzpVyuV{Qcei{3qTn`rlpRoloOmyx`+rr+YCP_eSt>EccXHjo&@R=Vv?<xK8HL%%61PdG&g_#yxF^%lY8?H+_tjUuZ6$xB2>2tj7DE=I@)^o^gNP@5=p9?X>J4-_u*s8c#n$_K&Z5tv&wSx9yrdF8NxFiq!bHsW`6l|8=hL_PpJ1QpopR=;V3lV*L616+C}#R?&I#8vMPr+KmLM?JF>EdW63hEc=_=Z}Y*?e4e4<;TVl~Ns#lww`OUq#y6$nc^J5u=gEq)+@HY>`8YQAUP6o?7yod}aSZ)!j?Uj4=l`E8R!-plcrVwtPW>xC7hK;=lE-12`+7w3=ScKYjk`}eB=;7(uk#+O<U9<GaPHIUG=9&Y7t<Q({J}EGy<59z-2Htb&)aUBHEsotliW4!gr48$CXZ)$zWo|cGlBWy$~uo2h2!hQ6<YnWE}lm@_iNmJ>mDEfJA`X>tg$nhkDsY=&#gYZUe`x@{jnLCZz&k5ar{5&ees)KKlK#JUAbTBd`lPp92pm))$x4I^VW-buJV^ZlkZ3O^tuPM{AvsM|Hc>XG;aM`nLkJH{Yd5G|4CQP*?Ru4U-|z-d~Z_u_V?)ZYxM07D8xK2V5L?k1J0A+dzRum3-IRx{vS|$)l@$JfX{u!=kfV!Z^R*;*YCy0=j%^(z9JK!udC1Jg%rQuQoi3^bF1t8&?|mFwj8GOw|suX7r9Atcd_-%alXYDf6?d9Jv*>pIIpPk2h@_s0oUNou^O*EkpB;SAH{WAjN<v!stV8ZDFx+m$>yG4@OgUcWP(4pyvyWq)m5WEAFo_t%-?6@|9=uUoYVM|!+f5zYEzwe>L`yV*8JC8ziVIK?twH1<om*TK^})~?w+|%9-rM&rT6-C>$4?%eBQjq>(4#G!Sekc`nHXHA9;u8!2FEn`Pp!|&!2m&3;6zW=a9zll-$Ps6sP4|>FaCfixfY|<Li02D^}wv%WCI~6mN2y&!b)mJgo78Ir#IdLkd3cH0B(?Z!7)5|6fhbe?G>acW)-Qn|SLukK>{dJN|2bZEo(b;>P}}I>!DgZtSn(#(pVo?3brYf94gkdn9kNF+RqhCtMyZwNWSj-1)Q{x3hdUo)0k>`Evx^eQuBb`C{|IL6ZA^tg=tzLD77jA)txIJ$o}t?tZ^e&u_Jh=Ue{mdj6%CeE#6ld!2{>$mb8<XWQ@3eK}w7`HH{#XxtOMkUwA2PSW#>_2BpE-8){5A4|=3D&||E@kUPmoR2@O*T1)lzjxT57vNT<w*3Ab(^RWtU3|}Kf8N=3E`S#-b3n@vTh9Gte_q(UZX@Q!HtO~9x#RgTSI__R5r6IsOw{x5M)7>^zFy1s3@9LZD9+<4p6vtA=k34i_0OE(?;{a4wR~&9N`7Bley!I}nV#$1@2=Nhy_NqTuCzq2lQN^^-Uy%0zv?DGcf8l1>%0p8|L@+Kf2GC;RpaZV?^@_Q?iQbyu&-CzJWUDa_H{{{-{b$c-QmCKyhuiV|N1h@&mHS+8+^~id|UY){~u`cwdHufK4jE+UA`{w+tQcczncs5JWTkKkHf8ZCHQlz5kA+BwAFc<ZT$ayUWep~!*VfC9M)U5zf?rL#=R|C$ofTtWxn@JO6Ff?<@0QHvY*%ZkQn}4UVcy>C%t#?@b_EebJphO=d8*%K4%p-K4(L#UuIq;zx-VD4lJ<OpZi`V$m3XO&XF4ToEXp7H_oK?`g8Z<3jDnz$3Z?04Cuo3jqeMJ8{ZccH@+_@ZhT*G4a>v4^^<W@TbzoE@#mpmj+X5jaWh`y*6Lw$yV>d|XxtUtSN220^E~cWR_4a{KAW50`&7R1y-#uDdtc(UxBNagzPBoFd~a3U_};3x@x9ek`XA<x4~EM+i;l_uQQZ1aQTF4Ljr{qQErz*!PJOxl{HS=1C*JBP$GdiJJwG)6B$;2np`M>=$P_t#&R_X`w<(Ibd7i=M=6MF2o97v9Zk%WEoSw@6f1BqaZEl{21plA&kTy5YLt4$o;XILX9@XaNc~qO5=TU8LoJaNT?1b@}(nZd<lL7pFykSG;m9vbM?Wxx~UgKNe$nmwx&5+{~+N(74`l0gwlhENics^Gs!2IV-e4TMj+w&TK$Jg1tzgjwXO&cQltVaC*+oTMbKL<+5<x>^nHU9X!9&%n4Z;_z!ZwpV5`(N*BoW|1*oF?;!7UAP+sk{7sxPt#%KAEX;Po|%Fz2Ox!Zsq=j=YP~Lo`+wZVLmi|f~>dg4EN9Zqs*W2``UV5>Ac1hTl4Yro8QlA+*N#{tnVx-xix7v^TE0J`+Mbj2^!z>4{PD8@fvU0oqy+Zr7-iR6PO#<e-$^b|0-@=|5e<${_87L9={9GuXo$ryxy(2alKn{<9fF*_93r-zm@D~Pw#L!zKVCf#q%~#fq0FFG?w$qS9GYJzbN-Wxm-6YLF2xSJ>~woKj_@krIu{Z#ngKJ#AhMYK5y|0dcJqdce361|3UGfu<??IZPeS-yvTG}=SDT2&l5H<H;w~}8^-~~jpKmg#&ICAWjp>|&eshV_|G5r+)tQ07x3@paK6qHerVHwz3&t^-e11BuFRbg^17|B;CklQTk!Gs2fj|~9vQ1~&s#pP?zz-M<JLp|-0_x8&+o_k^_UySC11{5%#UT@|A+7YdrsrycXFM2Yxw<D`8}V%m>MYC>BjrZlV&~hMKSz;MXN&RHC`-;e=oG{6xWIC&fNH1Q{4Fcau-X--1yv7-2B{pyN`eWG?35#ga%jAd5gdJ{a$N7Z+Ffr=EnamiW~p8C~o|JV*PfFe-H6hLpdMp^C7N-!<Y}`?;YOPw{-r;RsKHSbQ-s_Sr`5sO`Vqi&v`%koIke$H*tQC!pu{ZVg7WL+-~B*vRr3Y6#ovx_<vY&<NsmLf%oz_WliDhs;>QW&S^Z&XR_biSu5+@{621T<NLUkZ6$O2|M{1fbRMye=Sj#YeqTFFE~Rk|J^E{`?6=HMFZ**}g;J7-4*p%|4_n4ap0S(8JrSQDl-oVJ?UKf$o5=sSU9+MtYIWA&`pB!7ay#xeJLPqc(Cw#=$U3Rp9rEYiz2lhQIKEHIH`@>H%ls*~zn<rk#?Ac#cNM?llgp1@UG(RkiHju<y>V7+r?*~J$$bIywEX|+AG?m(KQ=e}$F5`akEe78d7VEr^18NPiW~i4bKjmxvHtsIb8qohT0hv_V{@Z^Vx{`A{{3KcD__8W)^}gJtM!k~T}zMn{;Q6+YInUqzb(zz^Icn;OYJ{1UgO@F&a%CY5)(A;&elh2o4?~Uo@~+>sWn#UJUrF(|IE+RVWw=CSwDU0*>eBT9$(pu8~&@EiW}`z+-RrbMmrTZ+NrqFPQ{IOdiu`aB)ReZ*XHK;Uz?lXe{F7l|Fz1;Z<enc=L2nSo)1*qI3K9EaXwJhH_ivDeB*qe$~VpjDsG$)w7GdcP~{uv1696pK2UMve4ygS`9M|QI3H+p^L(J<#`!>1$2cFT@{RL>iW}zx6*tZYDsG$)RNOcpsM=$k4^-SZAE@dW=K~ct&IhVG#`!?Sjq`!3j&VLvapQcT;>P(v#f|fUiW}zx6*tZYDsG$)RNOot_<N_Va=(o0GB!7_%h=q!E~Dxg*Ja$kkDPB@N4B|n9ogpQb!5ej>&U8(aUEH4<2tgcV_Zj8?KG|<t9;`+vf{>dWW|l^$f~|^9a-fY*O67eaUI#_=5^$xeEmAI;>LAk#f|I8iW}FF)pm{R$SU8sj;!*H>&PnKxQ?vyjqAuN-?)yf@{Q}riW}FFRUP9xvf{>dWW|l^$ch`+krg+tBP(uPM^@apj;y$G9a(YXI<jYd^KJ5V^LH;cH-Gm6{y)EavAOZPm&D6!BsYI|WOMU(M>aQqcckhVzdN!Tyx@G}cZrG{ze}{a`MX4wZ~QJ%apQN1HaCBlsOlTPOH|zWU83T~?-Ffp{w`7F8^23b-1uFhs$={vQRN%IOH})1{4P=D8^23b-1uFh;>Pb1Rej@ki7MatU82f2ewV1Y@w-IDjo&4z`o`}PRlf1NM8%EYB`R+GE>YDtewV27jo&4zeB*bCiW|R6RNVMoqT<Hy5*0Uom#Db$yF|r}-zB>C)!r`KZ`>DPbMw9co16CqsC?tT0L6{_0&H&H7ofOtUx3=KabJMq#(e>b8}|h$Zrm53wrkuMpxSTT7ohTu`vO#b<GujJjr#%=H|`5i+_*15apS%K#f|#{)c6|r1*m-Ez5tbP+!vs@abJMq#(e>b8}|h$Zrm53xN%>A;>LXes{O`&0g4;<1t@OZ7ofOtUx4DqeF2Ia_XQ|!+!qiU)Qj71+!v;}abK9t&HKU>H|`5l+_*1HapS%)#f|&I6gTb*Q{1>OOmXABFvX4g!W1{|3sc;<FHCXczA(j&`@$4A?h8}gxGzj`<GwJ(jr+nBH|`5l+_*1HapS%)#f|&I6gTb*OB!GOzA(j&`@$4A?h8}gxGya9RlrW>#(mJ>|8pO-op0U;ZFBQJXq%h&LEGHC58CGDeb6>H?}N6vc^|aR&HJEjZr%rNbMroEo16DR+uXbl+UDkc&^9;kgSNSOAGFQQ`=D)Z-Un@S^FC;soA*JheB(Z7o16DR+uXbl+UDkc&^9;kgSNSOAGFPl`=Aq#yku@Xr$TY#ITbcHpHrdojptM-Zak+#apO4^iW|?VP~3P<h2q9@Dik-KQ<1b^`g1B2H=a|Wxbd6{#f|4wC~iEbLUH3c6^a|rsZiW_PKDyeb1D=!o>QT?@tg|9jptM-Zak+#apO4^iW|?VP~3P<h2q9@Dik-KQ{jG6f0yLObAD`YKIcc}8_)Ss+<4B9;>L4+6gQspqqy;$AH|L5{3vcb=SOklIX{XU&-qc@c+QXF#&doYH=gsOxbd7H#f|6uC~iFGM{(mhKZ+aA`BB_>&X3~8bAA*zp7WEGuRrHUapO5ZiW|@QQQUaWPtv&S&-qc@|2aP)+EcVvFKSY|m|LtVBDED{b?@Z&2rYuLEcCx0q1CIx|J5V3%9a1T^8ep6w9-^`h(o4`3L;90C@rD{v?Tmq5i>>1K<okA3%?(_4}LauA7U2RZ1|bb8Ge2rmiM8S{n}pCvg;C?AYz1w_0To&>)|&**TQdrp9mcZKLI)tF~YC*NaU_XE&H|gel_hHMMRVpQ4IPSd@=aq(DLv_q2&?fz>2~bftL02<*{5Iwe0N`M~+>W`~xwsHjB84$N}~M{vk9c{1%HfC)l506n~=DpQvTm{nIa>YT2(nKrOp2u?-^HiD-*h54Hh*6Lcf|CiwQyZ{gd+w}ZCz^Bb|e5w+~sHu%+S57tveXF3KzufQk5-+*3)?*+Yz=mORYz9+P^U+pe_`B(g2OGGWZF0oJ%-9=o2{tkZ${xb9r_{;E}pgrI_!G}V-`_=A&+&@su-ri;8T*mt3`-$=FAz})22>cZIsnDVD{h>n<J;C}xdm?%`l4|$#%OB$R+7#59>Q`fwh)E)%pc~<%;MYMn!LNh=0XiA}2l!FYNq)5_BX<*O*{?<U)%*cW9LTL+A_gF)fenKn4xJ7^9R53K7<?~i7-E25-7w@%M=krcVSY938o5N=663ZN@yKFEK|VM1G5lZ9$6(tmW`Duof^M~v>Ta`=@*nxVM%&2kNUBS$iioNrDnq}3uMFQBobozCJHU5@?*{D(-wnPEv^9Kd)Fi({#0#n?+VZc^10rT2>VSRk6#w#w$R(nyh{+-<BgkijQVsGuP;U~HYLTb)>tLBUtwVk?YR|&9$j^pOhNtb<1S8D}|Iy+$)<#>YK6z4ly*4x_{C1HuQN(lT7Y_CxQDYx;hQ+?OSZ^k_ITLlrcM(xZL<Ynpu$kBn<x%|^s5cYK<SC!FOUpB{zU?PrxhD3xH}re>-taS_v*BmLPl8T{p9J3p+7-SFd?jdQ_)72@pc&yaVtnoWB~SZM1^xF0`u`*5&`0#&0mMGcseR}Zdk(z7SUkr(+z#CVza4%ebQ1g|)R+jJ0Usc0`h?C!)ORo&Alh6{L_WkkC$sJ%rqcc($Y+LDbFhD9vEOBJke>pjZIGw@xnNYkz9Xp(Q?bpd*ls?wr7k>aUU(<k8w{-vUmtaYp?Tq7iuyb0J%p$V=EQo3EY>*|d)ih%5fO;I*!~wHGKuI0odO?$?NA=opM!c4SSC;Tv|U<`!1}hIg5|o{=YG%u@crN;p!59NHV^C1L*Gq7OhwzKV*I)xx??}OV=TWwR6!f6U~Dr%tD)_g;AtPKq5rC)|DBjmPV}V@aR_632z_FYJ<XMuh*ub!SC}_D5xX!}yD)bqL+8TJMNRTOMcbxR`w--V5aer!ZN9Nsqb&~d(<~113!#)x{%4CdrGtZfBL@fhg2<zM@?Sv*Bgij;PKT$Q24JN5;ZtB64WW(TN$K^5(ERY>LKmP$1Ni)i1;|N(8b>S+^7AbY@>8LdPky(>`WivLx`Ts!7UWSr`Kr(!2=ddQ3*Z}IpTnVp;ltq<Ko`L;fS(4P4nGaP2ehZ(c6*{NJu&uG5!KL^YM2LEpftu=uv`QCNBSE3n-YCT<DUZk_cP)M=EM>7qdjNd`1RWx^yM4Ov)zbj^l3Ea+*Ig7_=TuR{yWjOS=2rR`D_UCZn4dG7VBP%gZxa3gZvUG<&!^Yv8Hu!kZ<DPAYT-Dluy1fbU1?iPtaNLl+y@|v@m=cY@;!>2|TH+4J`~mROn*VXarvvO0O42P4dSr4)Q-*9OS1%X&v%=EY`OO@?Rn^tCKzDW<`E=_+AL|GoXv%8)2V^LWjc-g<lN)34SsB4CpNQ8SuTJ-}!Bqe069I`0DUkq1oWGVJ>9FGI`oB(zn=O>VN7x8viutzmtgLm=nj*kM^8-=htuV(3kHp&-NhpqEGi?&P|6dfnS1}<Ufe0CF&l8Mp*3KqRo9p%thpIG9yoUw7lHnd|IB1W%6e&_8A-;<eNiFIN4Kv39Qo;{s#nkFLW+E<um~!Ee@X^+h_)D4o^z2H-i?3-!HZ|Tf}>4O$Ymt)E3lUj(pqGdd0CV@~15h^2?x9i#+Ae2Fvc``m@2a<Fzm0`yj~Afi8z{f_)wd{Q-U?{Bo!lemVRc=v??Y@O_|t{kBW~OQ;+EOZe>29Pl|X?%A<Sp7yO4`mZMXKRw1jJ^JY^;xy*OX}g~=S3Y1Y-eWHAhaQCA4?i0k0Uv=Hv!To2Gl`n<LRTVMI+)cFZ4MK$5Ru2pjC?%@FFPFUV=WHy3!qesd?_c_TnSF=lP4_&-yGh9AioN_5T0_HfsvMk&xrQ6fVPAurPo_POTyE-qiMT{lBic(L~arNq4VKaV!e{s7Wp`fgM1`(p2eQ>=Yi3=Z}OIdgM3{mZG-$uY;PXcosZ>a*yqtu5BzBOmC#jw`?3n_uR_1gM=Zp?EX0`hM}%R&!!WkB5p~dpIvDrdP#VA7SSDW=<8Q%J|7XN}%7}i7N5o-%#o7IY`QUIQ^^XI6=D?haLBygTV=<@ZL07`BL{0Kp#JcB%u12(WFl#B={Hchs&^7RbL@W_eA3@#){mQ{Uxr6;ti-Y`PC~bp0<*x>#`mOQW5^T@*Yp_i1X#r1K8a^}H+X~tmzBTH$f|iCqEb1;2k<7u`z`;Jj;##c`t1M=;tufRdL}_e)HR{na)uDV^UX5k)pE$WbEffC)uLZ*oM3Daxx*EO(_IV6+Ec_Vw)zCG5ZCitN*I+z;L@dE}mSFts?UE0M)`t&<{{-rScVT=#!7}*<80Td0)c=_=pE9FQ&mj^pzY@?__Sh%K`pMvFe3E1C97Y_)m>tF3Sp;1TzZx~kpAnHxtlt!|0xU$dd6bAqL@_5b@{~u*luLdclwKo$(PGW+;2{64gM<8M$fJDnZJ`qp<kv$Z;VGvL7->29Y}iIS=(q5s^m;pJIe1!k0&O2r4)wkfQAETD=nD9CSg#zmMgD@tK|TuVwb)a>7wnY9KG4BIKE%O6z6f&HVVmo)-6CjHTeP(;`eg!QB6269Z|r?pkM-B1-&P<Zu`iJr(-DYK*zZvo+iwsdXhR6by$F=XxCoY;Vn3Q<-$Ky;)JHV_+0aiH5f?BgF4+BqIg`$j)IaIaXQVU-Pa)2rA4ylhuRskiGzvbii0UGGBOG8~i6~BEffx#QOYDmkU|A=e9OO4bX?^m6s6)%d1L5~NxlSPXUgTbMvVV*qp9Zf}9{Fm*=CP9gzO$GW6;WTrU_=_QU&Oi(MWhz%{weghhz*E;oy>m0>(NkJpS*=Sv`qQmVVkr}c@}hoGs*vp+Enu*wtW%%^APbE+j)%rON~f_^+_%Gf3fd>LT{nX6t}QHw=f3Bp&Q`$V%xtUqQOW9V;uIv4@C^d_zp&YeuaK4j^*ND<Y`+Qu|3k>R#M;g#@O`6_<V<Ti(=f1qHpavQ5|{J;PXK9!smgvpbmJ4J&&Mi;OTb`-;4MJ8UWu&L}?Kj5F^0;7HxKlq*Kt%&LmIk({cvXp=IJ3;14*tP6qG;$i3oZ{~SR+Jzl3g^7&{T5jCKF;7f`4TEuWfda%nP>6wUh0UZ0C%*az7Ejy7<%fy}Vo19$V3BC!rC!Os7LXdahb;=`8+qi;lU%~!7Lp(>`bL^kpw)9w+)Cuo^{|kNax8HWjpM;)*KZW+3ME_mE{!;7*BOQ)$H~>EaF&yJN9R1k{{a6~yrNPM4wl-sXq~D{@Ho^D7c-Me0janI?>8+$W@g?$Vz~_U00-q1w2@QY`u;&ppJ$z#kWkh5_i~_qRUOXh?B{XvY`!gc`5s@r_V=EZ>eikp+wAklIkWUWH0#7wZVVO9sp9M;<**-ItU9>F14ebm6sfcexj1+NI<h>A)DS+dkli6tzTSVN31_ZFD99oa^K1Gep&}8tG-xtfoX`N(Hdd>C$Sf=e=Lp!da|6U+oVw*3~pLRPlWBttN(*Q&=w3GB7wEs5x|1|Ur{2A=qX^hu3w1wgz80kp#{UP{Kh>;lgk?7CH=-V<_E(1oMwzU=8BkhNN+5+DfW9o)4gIZajnf=DSCi2|yE@*yu7kn~ka`@z^kqnv{{<UbsZz6n%pa5oZBJPSv5x}t>jQjwLmup+>3nIv;gl2`O{H$Q*z?&e*kA~8=M<btnR`?(+*AmMGh#~r0%wEyl7dgK=ImpLAf3VnxSnSIp$Ol1Fz;APM%@p9YehMhPM*ggm{T&4P<anL(lA|5epRb^=;a|aLLI2WzWkCdC-5~UJas>H1=<~aN+a-S%8V4VT_MF8y{^m^TlNd14AFQOY{sH|z8vEP?8UkMyV-^B!0#Do8j_r{SK>uxn?~n1W1z!%evO<Hbq&ZO=d9~mRKnubbfKLHU37--*Qb2>?n~5kdB0FLXSb}KVeG#bw*pu#r4z$?Uwb&O%kWUTG4o~^n!45mQes*wLCjYyW{aXb2Y<QjW$k!2hg=jrQn8mEA2#<)*pxNN>iFM;e>_DUpV3rCwl>3I>H-cYxa*&U8a*(GS(p1Q&I$_v8@g2@2pAySdhxX?U^ey}wc*=c?{mY8ThV@BP!KZ}3hd!XOxQDopeIrePPr!c0W4qVUkJqt3hoK&f!(sR_2oJ{HgFbDBek_mW@?cFdH+Eusqyw#_ejbRi8Hn)-!@8eg+&@GA+jF8W^6J1Bf)<7^1fL3;8a}l>kD%G$&x<xZ5|K85W4DtT`9T&h2V3lmA;_nL=7gvGoM4}Ww?L2|2R-U!Px<7DB|6!^N085f*C~&DbCEYzL<MLL_y;2AoQPeBzyN0N=)EHRA5ISPN1(Jm`Lw7*%f!>d7qQsaLy!-L(l)}8zY8_U2V$AFm5A*pVt?Kt-eddkv47bSIk0{Xj6onGE%t?!#^?d!5%&2J#_Ak&7yMCd+urvhV5DO)21nt?A;w~?NSnh~z*shiwt%N??Z);<2U$t|KL~v_2z?ihbt_=}E1=Kqxf1Nx&%x;XV9c{3h+^pbV)k5v=7i6Qn&f{Gu~tM@2Wwjg`_`guWkrmKM!^pgu}s9*&_aIx8wW3^cCbHTagbjMrEQR>{Iy_Izb#%{hV9ut3d_`<R`8@{;DgZKHqf^4ZBe%kv<&<)QTHc$FFRPjcCZh^dgm?HH5Pl?);MYpq71gb7WHVE>a4+fYq3nefRpRfGVua<ts(pn1o@@VweYR5&*Pxu;m5(Rg+}?cEeh*KVLX;1mSH=~Fn;!S$v1?44c`#H0JIQ%A&hSUER+8l<D3dUEBcY<R1o^|7sPqYv-9XHd+bwV{Z#NYKB+Nxjv-E9%uZnL`~+PKzZNxR--;L}q9imE{72E|n<9=Oas@EEB;u)vi~$_`z{u13w457tXqk9!_(~T0RtWMFptOw%$UlY}<a1%Ufmkj<3^BxFc0;`OK}5~~j-Q>($d9*pxuwOvB7%G_#CX&rrFF>fadQ2PV6;sBf|LCd1o;ejo$|=vK)-!}euV!3pA-F<D<G-Oxv*|7^l1hJ`6uYxr+(Wde*t<4{u0`A0poQO{Xp?E80mN`X-vnX|0iJoTR~gGSHzgLgtmgGZSBMMNQa@%_P`IpcsGErgj%_wxvZo)(GYnJ;7dSD!k2*02+aha2{kf8bHU#caa}}V2Wwvk`wF6M-#Y1;QXFZW%*gj~@N#-5=hJ!x9n5cA9OQqsIQk%ml-9qFZHA&oMQ8^E`OeT#c*^-4j5Hm5A++~<XkU0zdi{H7I{3fEcCU#j;9%|TVBcQ6-U+okA)kCZ5#>b$B07R~LcMfo1Nna}4)VW2X&dBe-QHLxPV1BJgu1rxh~<K4S089^c+x<OK_JG3e0hvdAT%xf=jglk&<^nJ;X6S)!*_!3h&tsl56WY|zeTje*tA1#D6}&?jRo}!&96e}n>&bqF#i9bZ?0oJ3SxW;VjlgCxQ#Kpjrnv9dL8~c>X3gR)_o`9p@^3v?umE>y$k;e{tfg#{2Tc9(1-93QS&|YHT-jI;~Df7{4@9$&^Pce;NL>u!@oz(w`k`hw2SmH{9X9_&?oTs;U7Yu!asz6fFOSx`VTzSxrO!q#%q5;pTIvs4*44*Zqk@y-|t|*U&7ym-h{sg{|Gf`dw)V7!9PL{`IKVbq!5uxL>g#n1o`C96!4_U;Qtlt(+S%T4i54kg*u@DP~zlC9nK`49P1`WO}kDq)J}%&k*7$38l)-VEqDhs6}$sJz;E9I5agZE)bPpCrqq7>K>oV$2_nuR$ZvsehTj4|5S}ywLB5iM>(Kf~5x;{);Pr3>`O5I5gAn8gV?A2`JailUdHC%J@^i87VEDQ4^!j)a(IS?>FUIm|5iufmL!;rNk+U25<FM=zu@iL%!*7S4^=r>rw2}0hUz@M_^#$ow=r#DO@TU;u4?)kupT+hLA;|B7df<1#|0rUNh|wYzLASy$g5Lo>1Ahv76?(?6ZD-K->+lKCt?&u(o1vrOH^UD^knaK=15Y{@ejv0Gf_zu#SopEnzphXZd?jdQs0ZGIF{_MyJdOQ3jd9+A*p0r~jWM_TYBAbKIu3pe{8;FCzjlqq@@Z@@26_lS20j|P3qBg&o~uhxZwWa0g(8-Vh=iYmWzu=@2Si*EaU4PZ7kE-1g8V@d`9<Utao^$~{|wq0o`QTwux0Qa;a5YCz^{gnhhBt_hfjoFhEIh54SEdzH~5p#74RqF7eKqiFMuxtb-|Z`zh|-Lg{L6@6xs=%f_w+CrSKi#S3wWMuY!+*UVx8-{{wmn{tx(Hp+Cd_3V#CXg+Bp5AKDFmKK!T9PvAd=ziYAPfu|t<1R4rYLB2iMPw?&GS3+aqLmE1qK><k*88{a_=a*FC%K}AOE9sBkd*a>KEiAkjo;qNzsXv~;f6aQLmU>u0NW<iGPF{QtI_1g!b#xbm^?v}UISGU'

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
