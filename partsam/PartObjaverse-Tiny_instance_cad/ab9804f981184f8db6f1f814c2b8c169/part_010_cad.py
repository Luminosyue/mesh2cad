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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ab9804f981184f8db6f1f814c2b8c169/part_010.stl', 'relative_path': 'ab9804f981184f8db6f1f814c2b8c169/part_010.stl', 'source_sha256': '76998ece52b741356db5b4f088ba0457c4e2ab1350c45f8b10966d9d53354229', 'input_faces': 596, 'input_vertices': 443, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.82976496219635, -8.75677490234375, -0.7255859375], [0.0001621246337890625, -0.8063187599182129, 0.7007321119308472]]}
GEOMETRY_BASE85 = 'c$}qt1$0$cyX^`D2`<6yKm!y?afgzPJ0wVhlK=@64Hh(Iqs2WG=ipk3Yk|!VMFIp5k^lz@P~0g}cxQccp5A@lxNnR%?hRv)Irm)O`j+cHgP_LAef<^w3aafh<BOy&u9SY#DSs6eK48#KUBd^K>>D}EM`aRS|9Nmuv(`<6+WM#{HKJ&@@PS<i6s_tgT0Nq2(GrfL5&Z@X8W7gEbH4%I!nIy6toOihw?42(SY){S{oC^8%aw4HD^|i0?f4)5rEzD$xx3y!humnrx}Dl`qxnsjtARRi(c?dBT{U?GeRD6-9sYGiH^(Z`Rba+TV&CS<C-F1M*H83{Gp}gfOk4r|?{}%}_SXDHq8k;*rxgDcAD<QbTc19P{~W&XfARN=lJ10=&|l3Ed!tpF^P-;%72POZ5&6vIEB5B>dZMf1E??1`ZI6|FzUulx^aY=w=O}hY?C1aexA+Mwom|r0{m&8659AizO6&&xi#jIx@7Vvn*iYK%Bl?cMyT$+Jz3;?+{$1#q$L|$Ci@v@U`*Y=#=)u#sYuzYPTXfZ_1N7PN#omaT@<z(rrGm7Ns&Z_P)?Hhy*P_SG72T|n#u9t$>?^SweH`V>(R{zwoo}X!?sA0|6#wm?To(IM6Gb;;J3((9eOl|G%R57_*dF?aKMqPgFDeK<sUvh%rk>Qp<-DRBt$RRUR`rI|L*uNXht|&keaF*tlK(>Kkk6GrqCK;pl>D0=Q;F`V)`s~>*e`z5e|RYv(;RxTg|YhG`94YX(AO^=q91*}OY}F#M0Y%TFS^<B^nWDXSw}^;{6fT!5q{#fly}u0_%EGLbhGYD>F3UxyF^!8ufzY4p~s~jcWn~gc`Qimt&o!!#c#w?Z+pk`;Zi@_r-|-5SRUz44sc0*22Vl$eS0C@X?~I)RcxH-rg2;RgdXU0LHr&FfS>)@knX`gV(;pm9pycX_A)YONRa&0$p}4hiNju>p`+5k&-md;xBB=~(jP*SBi*G9p}$*n7xnh#1=1ag`tQ4Fzg;&c4}tyeN0(4<FGN?>-Xh)R&IBoMt9zn5Y7Aljc@rphC2qj}N(C7=>fDG!;y)n{_HCnJe}3#f^p{w#bk$u${2Ryii|*{z6ZKHFq~zc1y4O3O7pI?;_I|t)di6-jr!{r|8A<QRVx*hVh5nPK1<G}KChDQ*2-JVpjnXdv>hVLo+BdZ02>2;~0)8CpPD*|@^hCPD!r&*&x+Qi=;n0`fcX;V#TZ?WD-Gus_)IjDLt9KCWujiI|NJV};Ecwh^%d5Ob)fMRHFY}<Dzy2(G=+-P(r5<v;eJ<s=J;`Bj7bEOX=nJc%-tuHhl6u}4Bf9IiHn6|cL;96!|BLA6v_2^B>SH&=&)abL`NJ3GEjs9q^z+z2*jGV6RKu^udg-l(L7$hnPwH()3DHCU!g#U19=s>^&x^voAN!|KvXkVqTmI+vb}?hxW8G<%R&*mZ{lB}lN8*2z^i1>%%+KnvConI&p4sh9N6dBce=%NkXV_@u=gTdOyYv@CccpX{5I>~{|0(hRJ_tXJN5Rjcv*#t<K09IWWPYk<m;UpwzM%{2?ecBAz1ia->YwwiIeQ80AEEyk<2v7w^lHrzU2R4_owriN+jY;lwvtVicCn(Gpj;sr(2hxOFMH|BP%h`Bzofh>tcvK?%HMK{Uc^uOm6}ix`TTV+{N&CMCw`KAk)N!ua%<fYo93F>#k_ke`I_QHx$0h${;bTqqMPfkV*N>F%6x8>x-7c$>ZSZ*|7qEO4%u|8R<=B%SAVor(u>^={|mO~6Mfsu17bI9HT>5(FMgbLPhA(g9ZvWO9Fte<r&ic5`lR9T6a7HStMdLcOY(DMF#HVYi}72$q_mguB~o-pi?Jxz^{CBKt}4AnS2qgEI<LBq_*2?(eskt$o#fN8;-u7%(V!;$%<Cojarh@lJ(~wAJ+-&5Q9QrQ8){tu^7$kxr`BD^(q9()-5;LFIQj^CS1IQe(Gzcr?y6fF{jgv1`_j*+UKHK=wmtIiygpIt<yf5PMw@u?ua5QJBKBMN!+sm)8TDzK^mC7{@}I}JIDToj_<6kRiPyN}_%(}cgT8wN=lLtL{(5vXKXvYx{<Zh`$zKrTdeJ(hyM*iP>p09~@hiRkugER)k7><(VjmY~vCkL1^r%_c#XhM1SkaS)QZEU8X!7ae-!bTkeO#M8!)4wuV|qUEn%`d3b=h^tHyn>UyU6-wjS7K%r?060@-HxdzHN$joK#5CHPgo(M*nXJKaXFcp0DhZ{$Q;NL_G{0i+Ld5WEsE4j1sW-+mhMdPgG$3C-!ln4i?@iex7ASy;T{4@^;HD<IXIW7XG_F%pp4W32JlvWBa^h=E!~%{rrgN#>(lEuDSbrsedc|KGB_XcVV2)j9V+|mR$iq%`0b;{104%eCC@0KON4(|G<0kfi^ufV~(t1zjTMJ*H*}6_-VTg_LU=#N_)*7554?u)N_+Bavo7<Owk<y_fZcwdfdc3G*Wbx{7V+`lQ`*w<bQcP(apVM;O9$`9pXQ+HFPx@^NGX1yTs2CjQl_EE%oNuJ@=g01vi0x`;OR`m0ctAo|;-8_Venc5&JV&WIk8btH9nbxA-wj9mf2*wG`^}y8z6GJ(I1Kd_FD?KPk3IJsU?OWxZDMIZ&?8uhWYEu%Y7L%9IuUd0sHzeU|k_P4I(#x=twX%!pAKFTU`9`*-w{2757YSNQZu@^dVmw4?cVM66vm7A(X0adR?RH`T_MqB{!Lf}b;)q`j2mq3C9%`u^glRZ}^a88J7Z`wzf5!yG8OI(O}necp4<^KnUfJ@<&N_Wme-T<_0F{TsJ7BR}__$~xujHthz+?P}!b^iR@`R;@3I7)MUgt(;x6Nj^X2k@?*4{S|()alT!?74`XS>?8YlRH=s~c<J1y8NQ7$e-;}BKW)C|68lbtaNg`TTy$41*qe=8$UJFWi$p!2iH84IA7#E(le&1>d-|dAr48zB-3IaR7_wi=Wj?IyZC~-Wr0dZgH@l;}Go5kb|6<ukUh`P-wla?y4T?Ro&wGZ^%4OHpxSr|ZzXj@NOaRIo!E`4TlKrzsH)DU0e&X2J0Q;E(1<<~^&!C_5{UGN=^>=RAXDkJM=jYQHPuZb!|7q^1fPGz`%qXwtd~{&3%>UNuH-AYwVL!vq(YmKF54;dv&D)3jhcDxf$b0vTqK8KJL;m+(#Jc0NO?0#5OIbI~kYpUEE8%B|DY|pVd+eh=4TOEElBmz{-m)%R8^V#Ff+?ilJmbhr3WdGd2jl2m=eZa!9iX3^hI0V-SJv64NOylI#;<F657FOLfdBgwptl+*^O)*c0`{(=C~wkK%>S)&!9H?1=G9eaWt>_yQX<`NeNdm5(&1b-%tv%9Y@zu1cRt_o`JvcPYK(Ox`k<Uot!M8=S2Yystxw(KqIZ1;`zNa~PjVixDxZLTfQfsgiBspJ-|iLN_46a-^Gsb?kF1Vc;Ah(&?4MJ$mir1b{R-&!;;_!fPLXxNI50<a<JA<&r*W;?r9(E|`EI|gYyX}L-cN^pTI{P;U{SdrGwzH)KEIyF{g|<LvD9<EA+R5jRo1W2i_4`ySTBQMKW7Za(eWP=ymamZJ>x<p{s8?R&K<`5M>4-z*{gWzYEU29FB!q*k^f(LPPz5!m|b_3Z6x!gm8Jyz`xFt~(cVD)j4Cbnaz<2MFaM#3SIR!bqkGP4RzM!~hsRk^-qI%W6ZFFrd0*rUKW~GvUW~1TbEWm<f#6flC*jp)K2e_@i0&LoKO=W+x9ir7mQv4Vvs5@QoIMQt4sB!}bB%d^(XP98W{~<<4c1^Dpl;@<;oV+!_aHy3<E0)PF)2{bZ`O;hn)F3^r~Q@`Xw$9W5Y*>}A5m|mR>S@z@^4;SbsXc)iF7^t-a((QNxiLFgnVA=Bl-XL9+kQ>zL9m@v^HT}<eCkA5AI1qe|RY86g6Wa@^frH_G9x6Iro_-$HIT}kw|x|L+Zis9R>Ta=HlPlKNx;?M8bcj26E0;gTfDpeX;J)^WRS=eolnT`fGLV0{y6odTU$(>+jNzs89bAq8o{+aS!&zfZk%U)W4Choy;4?o#*!@JlvA`(Ag>Brd_xEE6IK-w97f<bM|e~&2DcnAI|s#`@pD~(0Ptir7y0M@FHVGclynOek|wuK$~to%ZmQlCpYSCeE5BPKR2hv;C%hDz39eb)Mx1N){;+;u3A<`Ke-fu^H)*>*z?}N75Nh9Q|hY7S)3O)HkI|xNK*#--O*C6(BQAQXBbsfbXR%q2bRr|@vd&Af&GoSSTA<ulzVUG`#MSNx$cMd%!u($-6-7|_UXo<K8qzJVchM*yqaq>)|amF@WXpEGhcm~Ppqq_;fLohSIwo;?yA|5B(Ho%t#L~JD{q1BIZw^(g7H3Zqv+PXw5Yd+$#HJ_Z4LZ;_74&H)<}ImTrRrmu}t=do^{76w1nl_kW$+_HfNLh-0Iy2{x?S=-P*x&@8r?V*w=D?H*!ytbF>lC4)%NAp&p(*$NkLdAfy|z7Uv}HldYQdQEw?P!+z_WIJ<6kx`}l*>L}W!M0xlrF&ch4td@HWV|j7WJ@=L>dW4*VJi2*zh};vJyN|}(?bWr_xR06oy?kFVj%9)U!DQHvy=p7tT}AmKpA~weK6$P*9)G-N?<eMg<G9BNeJQ$Ue)h~)YS9zX&2^2jE_2*jAJ4)*c_P-4RDCet7T6=YS|2ChH5`tjGCv#bwtM@(7Iq=frmLb6*#D=Ek$t1uHxKFVZGiP+bQ$c&R*e<ixpNTe|K#tM_-!>9_7#7}ed?WWkk9Fn@PEFcd>2wxoU-pSp0$MD`M%s^n{T(`{8+3xbe{*fr&&<o6#Bn`{0}ID{UpD0nG?&3Zl&9Tc8u&CBmOQVgP);)$agc<|EBmc#=N;J$nP)CPam(_b>%k{-@#&PV|^)mANHwBp<mTrh<Uj8ZP+`Lq@P$@Qp^6w2#FKjn)(szre{4$Wx;-CE7VUKf3(ZUUC<*&pj>swV*ZI(iF7L-N+I<hx!y}x`P<`r*MvTC=(kIuhhGrgx|L7v!K{P@$j_YqX!r8n<bK=C9wWLL7KZO#A-B=bk4=D|qxsOUq6T7pS7V^(sfP8j<8tixszpQ3SX}y>IsaSfSLT+1@ZWc|)K6%j5ANk2_r2>i9=r5AB>wwVMR_YdKsz?LCHG@0sWkGxr!D5Ihl{cArEca}j(x?l3OMh~Ed)O`%b~pgX@PZQZyM;4-Jxe+wAQXW2e*WO|G&>3`fqg4`PzJw0_g@Mmww_opQ=(mqPsqI=J&g@v&7HMS2*`q`w`_$y>O;rtG{sHT<itPyLr<Vu}_{LdT5;%@WbzP9^Lc3L+u`Y*sd$TnfSiBFGBWdYUy71Uz5!1+-m)^SajDQoG(<qBe;k8bp-Sp5tx@oPXE)ctKZ+?dsE%Rm^a4sfIid#KZ{!@iv8`z$p5=c-uHod>m&d9bIA8_&;61|S3mc~_sy+AnD<hZ7u~8-K=vW3f4exluIhEcJ#b=4>4$1$ap)uSV1C|s2=_?Y{h;@qf_+QaR#_J;^$y<$_<hz)UjXH*_7eBdS@0df+_+TExhm=j?0@O^Rs00bm-{{Q@>#6sgIasdpH`z|@Uz$t{nNjWd@nXOtcTuW3ibnSy2$r*)ou~=w1r{c-w*d@KSe_KKO^7Yt*{vR?q-~9iF6C!M!UZXl5@JzwJh>^_awe+AN^Ur&l;7}iEc$l$bK^Pgdf)3U!Ti-=KO;B$MxGk*jJ>#kNch`)iK_yu1&J*W}D=afAiWU<UeE==EV{R@m;=N_Kjk{e1hoe&|1u^f2G0to-kT;*Li>JR~z)eePhs2*l&+PJs-`6akr&CbkF&;TuQ7LkAH-|W-$8Cy7STxjqw#k4?T1r^J<@Dn3q0&hjQ&NiTl8Xld*mm@Q0tfDWsm&^J++U<Vab!%}4d%$9JOmQHh<go>wfCQtO`YAZp(^X*ad(K{B!baCEP{&)9(Wj4dqo=1C>%%fEW}JNW&>tIeplsBLm?v%0;;zTNr>_VF>eSGyG_^=#f*EAxO^VHot^FQ6WxkK7V_M+EfGpZGhDiE@5dF&&^E{VMetI(jzN@3M0fQEy{0|7XrB^Px)BS9F!D8t$K_2FrIMbJc3xi-+YA`_QQNxQ~4{7~i{6=aBU)G`_FQlV;5uQcvdLvr_+7jrSP8%PrL3s6klwOCP~^pT{#{A03METfOz4$bTK!ul|gB<Gs3Cnt*lhT3TsGSFVodz4ZC%@Vk`#^W=M_*>MHFr)_<X^7@{_dR=xT^yndyPxDwFtao{Tf}i;A7^jYK`A%w%zbp3*&Zpt<<N1Ew?;O56eLjre-E7*9?-$dD<G$*_L$ph_lGvYzT$O#X^V%Hvc`^a_a;;uV{ke?NUiWG0SzYYM9U0NDYNf;Pk=`d>!nnQ(`@os_E`0l>=;pFgG7lK{?&I7wxF`1SnM=z)))g=p<DyX=*bmAq`L~*!Lq02%f!-pA%nwRc#<{e{3E3~G`hAgZb3gfgg1XQHdikZOhqzkUhm>i8{l%ngsLvet<(@}H_=)ZcUJpN2-k_ha?1*{d`D4sKPot6l<TWo~T<=4EZtTT+(KP`2?I!TUbyMw{BK;yX=oEA-VX)ZG{fzmq;~CuBorsw&`a~1``gm#d!_7aVpLA>o`|~|9Pi{PU8s!ZV-I35A{x21qCwl%y7*9ur<2%5NEb={0o%kmX<F}r7f9U-H^Saqu+E<l3g7q=WF0}uGN6=gJf!?Ju`pbzLm<N(6{7z<i$)oaqaGA8bnUosi=)@8kH^!Xo=nv_>#rbwXFzzYOb%p=dEwB#0xQY7v{+a0Jq>Rw7pF;b5e_F<i@gNX>j_!dy?-{J?8}Hb4Gwmznr^`d^*Ug1;o-nWcg7d=h5i*~v&pl<IXquz2f9CJd)VVr`yylIK3-J9SVADadE4~=_C+l{gyno!6`Pgid2KCeJ6z0RcV`TqjzIui7`sccC*NqjUp~p6Wey**|)5f+e8MN-XuT!CFrTB5p!aZ}33@C5v9V<j%954B?8ot0jI4D@o>&Dk^;>S999rrfI+9jyZ+2~g}b7K8fMqx?6YN*(oR_%*+-7M-Sy6P2j%dQ*wH{pEhxqtBJ0Rf^LS(@Fo>sGmP$mf-t_q@_&yQ{xmp}%?jL@$7zdWn~AUN4J!K9?oYuB*-i(7qMdUH8(joWk#SA}XKr((4RE`|ABwkk_wBpI+VCDKfA7<mZ0;l)s7yv;Blri~7%l|NT!$e=7g~^%K$xRVw~(e?mIn$34ZkpJBwo<UhNg(e9@^u_t+V@;t=C<fj$zDzPy60)?=}#H-}`8Om^tL&(RFM-zvV?`GHzVl??~;tS$S@{&Hl^2C?qTG!Z#*p++`F^brgd=POQaXk4r@)^Y0<a3C>5@(bD!mz2tU&*Jket#kUOuote{N{eP5x0};XDh=sZnW_&eAl>{d?mwI5I2(RXA;9TPPFlkeAn37#-A#@YkWh#jeIuoDY<?YDTHg>W8(+;uJNReD<8aT%uL>fyg5;kw;_%q4ke#QoJAZ;K99JTxP<(7_p^g_yo2?u`ErIWCH_XPpD7I2IMc>^@Ll6T8&Ae}jm61dDeymu$;kEdABAv@w`}|z-!<N`@!URm*I0sluN(KdpVh=Q<g3YJi1W!~$cGb$k+&cQ6Nix(WLP$0FnK}ZTLpZkz)uhl5ucGSW!Nm@A@XpBbs)|n|AAqpi5<vuGb}5yG<g<=WhQ1N&&05d#LVOw7?z%xkvs!29WgC=I`T9`Kk_u>sfa1aQ<3`;lac$9`w%${R8RNQ%KbDY29o!1KcmP;(N6Q#d|yWFL9X>x)K<~nV|R_=8ZX#vHC`lMAm8oI)E@V<j<||^F>wKL75OxVO(rfNpGF)*980co0J+BgHXgxuja|sQ@Vyza19>y@V#JE%g^1q~E0Px?enV_TUYZz0Y($=)VLuXs$nz5m5?hdG<hZCs3?|RQu*$?*<o_sy1<<B4xz;s)A%0JuhFFfMb<NZJAgm0r9C>=8Kd};dUZO#)L|&9(O^F71J%+U>HYKk|Y)$M&9!88Lb|df0uo1*a^4<)KCXOKgiD4s&(d6wIHiS5mydAL=u@`wM^0dUZ<a*B4Se)-|$@Lnh=jb;?J#TA1Phrh_PJBwfg<-FW&&hvbSR(N?xyi6NVj}q@hMgzIkvkc7g?OI)H-@>0SIBoT>?P4fuJ=)TpR}ELmwY?<OyU{xpNRX3XUN+yY$I_$c^hIo;&SqK<lTuY$h(tA5M#(A$U})!$wSFQh(D8ukk=-5C9h3hjo6aB8hKS>FnLw-ro<lPAKlMqg}GDX1@epJK0d(D<bB=PTw(sz*ou6OLf9%|Px4C)yGUF`uH#l>e2szRDSQyehj@{^zZ)CVcVouae4Rqr8e(7ac!pgft|8ZP%QJp?rmeZJ58|XCULqgp#zyqri19UFuMoD5*q{6|!{UkS$aUN@j9-RnYyOpSbo!TRt9hgw8_;(H#@Bp<LfCrZK=K5JT_&z4*KtcRekrD{c}gF|`O3JL$p^Tfdh}h7@ipJXunojW@|z4xAZ{SnaZ50M38t;NpAX`sBqop#c4J-ouFLqEZ&e7}L>xeVpJ6wNo5*$C;*4LMX=|R-2XXv}H_4;i*pR*(GQQ@!6vDO=2a`Wx*nQ$wavk@3#{ZsaYo5;sadHyxlMi!a6Z&q#_?quj2-`)BB7eZJC&XRkI&N9UFUzzw&*g(S`G`-*hr2O|zJnNF^WPQ1b`pn?-(c7S;!biMw=&~bX4;yk@<E(j#0TWs=Lp8r*qU7X+{`pLGt9$v*mdF!^2&@?gV>t<I&D4>bv{1OzA*ErF(-LBzSkgDCa=%1*2Eg*gBUh~*qVGV!!{E~kl$n2b>e37bUq0CK%492WqlBqiui$LXz6}h`JnAI<|1#%u$;tv<UcUXkC>CZCc{z^{mAPuOppDV)HDxdm@iRln%D3_SPG&qc~yq_5L1wU%P_ruRHdeQ4u<LV=UZx;>uacN?8h35+jw@qYb;^oIry%zl#S=%yT&p$o|o?$%iDM%zH6*x<KOaKV<5R+Pn%L}N?mh(9{E*a4b}LF{1MB1jrfszFztE}myzdWU6dt$Pp<nwS@wgn>@S)ZW`8X}{EqxPzSktyC$CA~i#Uk97x^E=z2tw8e<I!^|3qGZ{aW|k0?b==_T}o-G!J0e3J?pE*Kt2ZnXjVEx8_IP&q$^}lKInI`%F#08b2`)Bk8Lbu_n3p89=`Qwz|=AkFp#`>H8DwxiQPpm}Su1!S)Cs<|J?7eo8XUl1xwYSobrIzQ?f)nrojK=r;q)p!qoZ8cD1}u6;V_*TFP3*KuQ6j#&Cm%`skubAZMMHlCdC8Z+7W5rub+r)+#O-!)FL@%DVz*w)6Y^Ic;V8~=vy8uQzD4!&#5PF|byPF-Rkd2M15qJv!HI|Z)sy^ULZ*Lc{*=ks0TbQ|x@ca7a_ycXXz8a7^m?;4Ad7bGu2tU#WZVTFiA$aR0veXa?yC3!=(PfKDGay?hqXFJztyLxy{)>BQ^U2Q%^7+!?-n)|aqWh3Sy&(F5VMa)LtfPJP3F{_R1evy@U*2bssUE@R>Z_9U$KiYT|zH6*#<N5iXpLwasKBN0k9%4T7Jmh(a1#NYok8P5Vaf&ew?XLx~B>7q9E0#Epya~(Rn3#clB7Kb`wji&_JeMRo$aP$uMh0Rmc{lc>_QdMshuI&G5GRxCHr4&Q3Nbm`csl#(WMX@AgXOMH{D%BJ)6nq`)3@fk+|LI0vy-^q#+UJ3qmz6Q`9k6{@<qhy#0lin$xUJ(@_xh+VjuEwhE*emkcTp?1hE>q*7f~z8)9ak|GI<M7nK#<Pj=z~1^i2a|E&<Vkf=4yA2Vz`aUuC_hD{@mCr@J765=%ShYVXuTtcp&#SGVYm0W*knxpVNO5-u|<K$zBbIA8GtPgQ4`C5i`A@(7k%dk$wF648GGl*g2Gsq_pJCjc!A5H8?KAOBAu^D+k^4`Q+<SBI@bU&%xPf%l@Wd6zjU;pLJfBoscqP+eCoc}wf_h(Lf%zAEL|9<ogYMer+uadd{=|lcYeVSDN2V?u`_5'

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
