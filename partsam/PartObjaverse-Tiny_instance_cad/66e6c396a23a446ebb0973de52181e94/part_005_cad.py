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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_005.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_005.stl', 'source_sha256': '3c28052f445b13c724647c524f029550f93cffe5e45bd4183126d9b4e8b82154', 'input_faces': 600, 'input_vertices': 379, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4253350794315338, -0.358684241771698, 0.030531764030456543], [0.023644089698791504, 0.05272701382637024, 0.4999997019767761]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@zsFCE5`<xd81<@Af*@K5M=uE?h&tSekf;$6HC#1`8YMcpMsEosT96}p7esVdbYsk@qkGxE@7H7AdT*__-phaO|Mzph_T6Wny??u%bJuu#{*={G!(S<_rFXG~_GL9qB?rw>3kwJd4e}2dUUf+DXge*R`0DSQ&TrSbt#>y&EleBh+&5sje~7cY$+<zly3Q^p=YB&&LPPw9^d1`0H$eF<{00pV$n=K?`UMAMey&inPCXY>&5ACjaMS<sFIQ$2tlR3|NLF=u`*nxt$MfeJWs2cd4St#TJ4GLMyr_KZ$*}9{v!&tDT}t(bPHD=wJo*j(q?qlJzrd7};&<+LP5evmCBM-nC|&usXI<bwDZWjqxy$Kea@`<r@wM==o0OVzIvi2Herx?z$^YdKsgL>U->B!;Y49IjlkzPYhf*6!c_HF!y%w#Kdiqv1q?}Cw$p1N1?pJq7J0<1ZDU19k8sollFTSRHt${uK&84KC)`;lil0WiUx|B1*Yq!*MYr)G>{_)4+YkKSMQqQ26y;9ECVep6kBll%YSt<8r@%;^cuemYOE{^U=($14y;1`NoDA%!#mvSuD0=Vw%`f^>ZSiLJ!{)wko#9!o-AZogW_8GBBd@U|@jrb1|4@vu^%!Xe$XpGc5A#|tsjUwp3mU6U}+iyrY7s60}@?VIDxo*<VmS-7h;%B=m?WXOnd{zAUHu1GL`NTKPsC!B3`Cvc%=ob;v4mIi}$bA=_0{=>KthDpYr3d7?fg@4=ln~sPhgt4Re^?s%&&DI(^i!whx)q&}Ke`j@v$~ALr*`<xW%T2$%~JmID2X>c^*H?I<Koe-J5L~<BgMD)f0ll?x%Iv!`TYmL|EqtZ#7U9+5+}AXO;C<!Nwkl<=LNa$Ne}oLNlT=hsos0UU!NcTsr4vl!Bgo+V{=aUTKNWYou-~!q&^2OUXssi+e&_|s9DCNKL4!vnqB*iQqJVMN5yyS4!^`TX&=3d^^9Eic5V0_52Bns#UyU68*g2d&w;z8{>Fvz(vNzPJ@CVxOZ)3@+e<uX#!C3vE5wNZFq_1W?i>YwZ`4|;@2RaRQvVha@V9S`6TewoX=lAj6ZqAf&<<4-rN8uKclhO|Nq?D3Cft^G9`-U-z8|?p?#p~K80{RN4*%X%8Q0eL4<$bJW%E<fzhP2;Bgby(FU!8U@a;V!<@1ZuYoz^8jD}xeCE_7WlX$aT@Im<lYonYa4J4jTciiDuOp<o9-mQW8O+R@-%6X9!^Gv=@Hzj}j?eJrsA)X_~qMaWshF>6j72>d{%vaVjG4L-AnlD<XVZ79{@ND=SowtZit1t0yoikE=%b+K6T~mBC`ggn^@|W8u`HgI=rQP&yo#3YpmVPk?|Bm_7zA}8@W*fxcHdy8>TelqWpLLdbO#9sCywvC8hx79Jk6Y4iTGM3`pXOC};TJ0}^)YG(T$k%k8wvmHQHc{{=i)n(zw{9CEnSZ8mGLq?RO)GzYY%_f1@Vm&L!_RX^;eWLuq*OcJS+XBJ$FR@-rJKT|K4FJ=f<OR;ul#5zj=Qt$ChI^{M%n-UbQ7#5LdoC&SAX0kao~o2c4C83D^$*&!%#}rpFU7zYSdle@C@F5}&5-Qoi9BiSn}yz;#nHP*1mM@R$2xeAOI=`LpR%lrvzh+?Pe`F70WI@JD`+-dJ}|G?ezYmg)w-bS-ITOP{<lpI8<*K{@?~%XRf^KA1N;<b==rwYpRkUrV`nR=&S-IqE+zN#+eB>9Y9R%<9q(Ca1!(zU$F@;7^&1_17mt+RZwD3H*}B;cs@wdeLYO{9&W^OZiTN&@Wpeaa~)i__ikXQW5_l@b?F!obuD9{k1+rP|m%3GH+NW#3Bx-_k>^ViS&!vJ(tYeMxZOoxwvMZ==wrZj(Joy<hP%-T=M&kmvzTFw*>P4b{PAX=XX$lqbTx^uPgncJ<N)E;7LyS>y99PJg=fX?|nEU{-ITJU)r%3sXzLbkFTX)EV15Ff34XS<Zp05>Z$GjivF6J0zWXT+^;!HbF72!li;_C+bZSs(`CGyqZYu|uC9~*-BA+#_;wbq`%lUN(d@p`{^sSO^hbzqJCg<T=Y2EEacCVa|2}KvdTEEx?cv`Im-aF1gHg{H)ltq3FIhJ&WuIWY&#D0b(w$`aUd3AI_tRxjju9!>)oXM?JN!`^{?7BW<@27Vv2xusNBF*FQ2+2%=$C<?PK%$Xw6wGJRV3Pf(>wUFW@%?r-K=Q0$FIdVH}*Ir{rfV%)W?$J74m<LlX{v5T^HZ9^_uvWu*KpViTS0Twya0tr;oyVYHcL#Y@2vMd{eNylyBLXjQMu%ew2UhcZm}{%S4&Cbz?95;ipnWN8gh2EzWCD{$K|w$Lf<L^|yALg#6uaNPhG2b*O)~QOIB2Rn{ZRV_o80_YZ;Jw3J-ec;8Cm*77wF_0*Rgk#f4vJO86^ai}TxYYFWu?QHs)`Ik(`bxZU?dyex%eP#}odBfT!M9Md}?2K}9=al|3l`D&V>CSe@pM5LlfvY9ZUzfe$A89A+oi(u9J}KY99p&_jz&sybK-$@yUIl*4A^2{6F%M_2EWUmxS?<f^I0NxEueA8a%v|V~{oWXlJ4`6&Y;&|j&K#(xtvLJ)%rmw^XQZB%q<m<H=If4$y0nsZ)1T%+{TF>YDD{uBN&DNf-##Vf{<dG*%^J}R>q4y?;%mpOvY)Zo@5TJT;}Y^m#2He4!bB;@lyXsg%bkws-|Rs+muctWuV^Oqu}1%nexG#={`KqPTY`rmp3`=SZz}uZgtW)TSLnwwai~w;B~pLm@dfm|&t~|Rf>=j}J-~Q>Jnt0x!zB0hZC<rCpM~oN&Xjq~e6uv>?cU?W*T?RXcGm0GKs)3LK{-3eNqua!8zBFc09?09)ss@6GaWEr^=yaw|FK)z$B0VCdNI}u?G}Fiu=p)kNu202JmD7%LjTlRDfesgZG`fDY;s@L-UHFU-AwTB46sT$U%txz#1vE#_cggI=5t?ntRs=dkw0{h?2D{>EHV#kHhcKXZ%g|dbBd?_%YWZN&SkpmY3$!TeiGkEe1(7Cb3*EG8uwN1U)#O~_3v5(`;!W9#J8>4dsMDlzQUOweN*4@DL=N4Zq7hCcamj&G)nZxK4F3lezD@x@7lNzQjVqa74gl}a>#zc_*6^U&HVR1<j?uHjBD*+VQDwh-~{-SlW~5G4@aETT`#`nbRHQ;rmk<{C&r@we(onRUh-l;c4Vb|)~D8#{?$t_z<7_Hi*n+9a87SO0OLJA8u@o+9GCiLi^qBJ&zUH{l&93+cESPkuxAAP=FwQUceTa5ojxA*e>{D)lou1m^I$mYH!4!%)>11G{g@Jr`b3Q8K5B;4M<3~n`slr6zii!-jCfA-M)@t5$o!+(6~(%Izdg!1yiw*)OOElFp9{1_-0$jzc_2Lp=1C`v2lExK8z~=gUl&WG{C!1b+?j$Lq#RqXA}Buu<HlOQ6xwIVugJd+=LjP-MD|OzuDNmDm<dvUy~}p&Gt+)TIre46Hy=oma!igI{KZ+ZzdbSo`&H{dGM+7e?vwb}cdt$T(KqZoWSm;|EkHSIuEKXcB<CulMSaX;FE5F&o62LJX_F7*wCoP?wF=#(f6XKBV*hDufFFDW=P7ec3dYwe`0pxUzfrgb>S-S%zWLrW>@V_8$8(`IGsL$pG|BkV`~Hme`d$R;S^TclQ}5CI{Exo2vpL%HZdW`%DK!PYd+r3p5%%-i!7;e6VG&Y}>2`UvL*-EMO@|92j<&2!{n6JPe_0^^{yI&b7ioWYMST{y;C$crAja?7hNyo~1FUQ9?J-V0%i+4)rlNmu?Y!`#ul0N@>%M7DQLHcN#n6u)?PT52bDZUQAuq05wuy{8(<Y0wn{8$mlt0%~>SMcjSLO}NayyiBYn7bOOiwf99AR$qSiWx^^g_=4W|s5KH=Gw@zjk2(=J{EP;#*F2m-)o%h4Z*kaf|rcxRQwfp#u;nT{psCza7s5d9E>MjTK+7`v~Xwno*cn9arMICzs0e7+bg*^FxzmxNdSV*8P&N(Jz~(qW(`;U_8~mE%#;Yor3x3&Hh6_wx{{zWR$beAJ3^qb;UWtc|82*zsP<@KlKRn<l#{GQT?%B8l4CCwY4Aat93ZegH63K|K#>Vea^cfu9~_@eQY(`qo2}UasE3Wj`MzqC(7}*TQBz=(hJWsSG9tFeVjZW&>TGF`H5b~75DWtUfRd}X%fz}F_lnH?sH6)hhkk@QxWC-(Fg6hIJ@+({>c&k;$;@m39saQVRg@sdN%b&JYO<n|90UW_A%U-8a_|3uKoN*d|Spb#@z#)3o6`4{?#~tSglpjFXmMAU$x6J|CrxqLp&GSjr>l*GA?Xx9nimhcObv92=RG2MAikZ8uovNU95~RBk>Q!Z7whI&F{UX-)(y@VO?w03iIIQhS*n@PQyAf*A3-NjJu3}FLU8v{;o4P--nHo>)Lu$5MPVGfcd9?HT2`svdABh3+>S|1HMynd_H|lo{!oJe#N*;D1dU>l~^LzYg&JmsGb}58-EbxE$S%uWpVsV=0UAvbJ-VZBbH(x_2i=X#=HXP-?XdpoZP&9G3L#Dsj|)*of6Ove=R`%VSO?GSBgV_eVvc;t<$DU`-M!z^YDJ-QI4gS#DnQ9&!=JG$bbEuJU7->HAP&#8iD<g_aQv5TC-K^V>J&&{zu(0&$%4Mbu0VB-~Iye|1<{AIUjX_KNRbs);wO?&HC0CzVn~IOMYt$oOe2PfIkNBFRa&!%lX$FUmX4wJ9(aOes)pzleX+R#kbXeF8!iUi<5Q4+~_Ul>(dRT{>J?oSU20f!TzJ%IOOkn2=^8KQhY56&u6T4X308ks`m)zpAAdVeuXEZ-Ll?5{)RK8-Hd+YCEjeIiSSbsr2e+E&t-pTT9APHgr3CySKEmCtlok8jEKf_@y>}@M>672PWGb`Cwi5e$p2!i__i?>@O*bxx;%%soUx*wzeM7EW|s@``K$xV$+ZH{Wn18RouzFR)Tb-f2i>kG#_67S5>KYQz7lWNebaEizdyw|@48vyN6%dw@0-HTA^)#=vA-?X9^*Rt0Q}?Uq@7JEZE(Imw-@J%xYzPN#CGg3&WR4Y#Mde;kmn?(Yqyi-x+gXvzB^{YJQnVOcIbh)H~O^4x#U4Z)W3Ig@ogEOWqs5W%*a2h3Ci!t=do2r$~<iKaYj8?JLA2_dKcVR@uJ8d7`{UErK{|t4A+k`FYA5r+}E<QgT#;K{T}D}Nq%_$FysZ!S%s4^k9WI-`~7>g#HT503G$D=Ec5EObB%2ho(otT^_2dyZEubHsvC^w8k$>PX-98coYenSU-*G8at<;oHpjSg@j>}5H=zCRhhbmWpXbckNtpL~>vF%Q)@eA;CyhY6<@*QuBT})?&NwXbX6@pNc<7mk=PA?n%6;jHoAKPqcOCMV@L4L?uOEl_+}8*G2QR#b89Y+nvzRBegdg`@o*!Bg`d}YEx-RO|xhm%K8&5GVHq=7??mc9lwd8xSPPA$X_!sBmJeU+G>#r%PApA5h8Aq1WZDpOZ70yThu*^S}*h(_qtqw2coM0Z{i1yk30M~tVUwkd{mYi#}b&Q{q7sa<N#``y0V>~CfC7lr8YJP}u?a~(Sl@5EL9G8Vr;=gp2c}(kA2>#S@($0o`D%R`Td+@w(Uy@wcQnHFX-!S?_z;}q5A=e!jAp3J$Tn_l|n3uF8hRmO~4et)3pI)N<4=uv_IDQVEv-I)9eE78*uKT$o&ZP~!CrZ9E+vNR}rBGA&!FT0-oVDf_?B`E?!SmL<Zqo0j&%^P)CVv_Dud2(w(U=?|^Pzss9{!ODQjX@Fh<(w^bUYWn{s!~jnIqDVmdc~xw_dwi>a*M|@vnK^l=GgpGgR)^;=c|1y<0`#->fX{qZb%1acDhl#e3gr9hONySMtLB{xloDZR!BIuO4plzRb8>75hu`j%fM*%qV%DrtOW#d&<At&lOGYAmh%QJPiJ{kMjJ@SQaAvrFnnGdEQ|r@`tp*`N(@4{AQ!19ZXsM&_3z4@q2>M(Tkwv@jHQ41@XSN=OB6CrnQYtlyXXj%JX7v+lZl3&-;(1{k4D^@LM!nEbYMazBSDO{<B^3-dr!ULf)4d5#{jysr09L(muAr*q7GrgZ-<`m?hezhrFjVR?pvx`n8=Z<#+yy_k$O!;=S6qPO@HWU*}@pnDiR&f%MCbC4ZUPvQBBmddR*(YjuB$^yA?tc<*d+f*(0W+Ra$e3G>5^iE9yW=N8EQbSy9L*Ni-7`0kz8%J&oU;5~SmWQ^NEKS#;;<NPsC*4!xLU(0ttRL0TiX?UNw1o5ghOOyK8+{<46m+$R9Q0i%ibwO*BUE*GQonP`BJw31=E)^v0uAPVsll$fKLoF!?{hD%Rp48vp6YJ*Yxp+@$YS>ZAnRf}lPY8G>{h{UFC-a?Abh?aptwk@ylh59{5`P&R@w<!KdvG4;gSgfG5AwOz@c!Z(_U)wp)gRzF+q)0_#GjvagXGWciFIwy-hrZP1}u_##;uZm*Dkz)Z`CKsb@#{Oz81e6E2@9#C7Qkm?a<<?<kNC~-6Zj`&L8bowaa|bV8<15U)igm-#xELziK`^WxQLnb;3TsLhZ$(SIWtL+ej#Xsgd`;enr%{*|ka5VwqpbOgS}2t)JfyKOs`4RGa$W|AZ*W?SJ(XqS~&m|KFbw4Yt#?VVP+_X6j2FL>)#RL>`fuLNn8l%ruG`LLNmPLk%O3A&;hxAde=Gqz)sGBoC(!CJ!eMr3R3PlKWAABljbBr*<NDC%31zCbuWMQ>&5P$r|-<4XlxeY0yFBVdPrW2IN}g^3*Ei^5i1avSg)2$wkQdsgC6Q<eW^3vr~U2XD4T)I*^s-B4;E2#FUGntTc!A{VxY^U8()|W)RLo%|p&Y&Px4-oRyrLT9}-hT!>nlT!>tX>Ow9>u1>8-R@#ePo!p#B@hYl8UPb=d4qCtttdim;R1b0!a>vZngX&53AbXNssRhWc<lIzsz1;k)_#BhsA=F-ErOn7g$lgqf-KlP5cXC~7WpZ7zE43Wim0XEQaS3W+a$)va2`0tAQuC01B|A~=$@YvJCu#w*6S)|*IJp?PBGp8$NUlaLNmg2cth6e*8o4pGK3S=m+?aflI*qLKB3Ws6JFwC+WTnl?Dk-i_uLD_W7jkWK8z#lQsC~#v2avzb%e|Ns`%wpx{m28UBgjg_$OFki)DUtI*`GRu>`xA)hLV*AlLN_SYJaks+?m>g+=F97aa(E&swdf#<3w>Isx#G<>`cx}%}vfre#UX7#?mt;#nIFu<RKhC(M*arF)8jybtk)X{B)$ck~@+cQY(=glIt)jcBYmfm*ALjW>Q>+>O^+pcql`yNUlMxO|3|-P4=KxBYTj$P#crGkatl}l6R5q8Q&^)?U@u;q_!c~rTS3YklQeJeW-q9A97FXK=MGwWltu>-KhTLZse{^ihEN7$$^Z;-b{*psh!E+V$qjLaWiTQ^0!!QMs+4PBNw9PCFf-f7NSOzqZwO@|Ddj>Dt|ST;y`Lgav-@awIR7Jxhb^{S*O;d)*;tnoYkb3A%BafnoKoVhE8rotxax3ZbJ1SHz9jbyO6!eLDXI3Ao5zOimkQ$toRPKB3UKHS(p?T{2~4n=gCaJW~K(zg5-kC(|}2_H`Ryi!<h4CQrwQ(jogmxMeR!N$~g0)`jUMaD_%^B>r)Gnzr{p-Y99J|Sl9YgZ?ZS*QJ-bj=jVc%-_4tu@@1wTnQ35V>dT}!gc?Q;Ay1@^CQl?!r-qZKljl&Q$aBa`sSC(U$!n;~$!o~lsO!nw$Okgh3F=Pjdh$;47AD29)aB$@atw6=Ifguo8bzK(wot>#7V=o?X!2O{2x=I41bHZRAbBWx0JR5s0J(c+YE5lJ?Llrs?nLcN?nLg#q<A<rggl%)l{%3;mAsHToxG5|f;xx1g1nKsl)RC=o4SU)n|y@2jeLZhN<BbMCEwJ(_x(*K#ZNQSTWT8h1UZd-h`N(}h`g7&g?xdULft}6AtzE}$%*83)EM$Q@-pfy@-p&#s)anCJcBxxJcB%mI)XfjJdQe)JdQk)I)FTq98B#_4kia^-{UNRNpbtk)QZ}I+M3*g+>+Xc+>+dZ+KJqO+=tqaJb^ly+K)V$97!EcjwCOlP9-lQTd51lR`OQr3i4L+e(FZ@e)4hZZt`*RW$F>~WpV~Jm7GC-MZHOWMgBm2O8!93YWF>+6|1B;f2J0*gMQ{`<$q>UY@?=;ZRE4mL*%pMW7NImZ)4yXlj0jpivM9!{Dhi9enP%ZO(b6@pQf%OpC%_$mywgn3Do)I1o8&z4Dtr@O6nx?O7ddrIPzlhT<S>jT=HycFnKn43N?T{g&az4PYxyb*1nIQ-b{*pGgD8h549E9hwMphLG~oKqqZcsBX_2DAa^GFQ~Qv=jW>TL#WR@{$1^G3L7hzALEb}+B<~?7Q5TVu$Ooxb@<H-p>Q?e$@+s<m@+tBa>T&WF@_p)M@_q6fY6kfY`3v<G`3pIh9rOcPCB;ruH4dGa6qlgpCzl|XxBEU;%QGpiN-aySN_L}GCcBaAF)6Ojq_`B5;=<Ij<ig|})MDgfoHKIpv*H&T)JA?mzD7MuzDB-8Jw{e~gM5kn7n9<j?4bXURZ?8i4oPtl>Jzd`igQx0lT}juiQZ}QC-Q4*GWj+69yNh{k9?K7fqa#GhPsk`hJ2K|n0%DHk2;sUkG!2ao4lR8nL35MnfyC7l>9q+3AHzQ2|0r5OO7Cq(Z0_wW0(|=%1q;_{i!|4{mH*keaOF&yHY*LUCG_3?a1B8e$>unKk{IzKUwKa@?i2jCdF~ocyb*1Jd@&d>JD-``4)8#`4;&BHHrLy{Fr)>{FwZZdYJr>e4BcTe4G4;dWHOm{E~W~{F3~h`iA_ToXrmUg{+cdN2;2e9GMgsr#g{~lgm*{kjs&)P|K66kZV$_l53J1Qr*Z6$xW&C$W6&DGgB+7POV3-$GJ>rQe2Bku?w{n*@ax1NpU`EVRAn5M-7^TtW?cwADI;YNxeq?lYEzYiLCT5@?G**CdI$lLDjtW3zOms)RN>1<i<>j>rji3>yT?ubCPS2D^b;aSBak$o2akJDk&~Xy+>9_u><ugStZ4G)H7t26u+Z)l>CnTJTrNF+GTP4>3{l9Bz*s~*s1^j@jsaGU%&b9*P=guvqffE|M`;C+cTSbXQgGy{GWQ6R;sc3^dCZAEpz'

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
