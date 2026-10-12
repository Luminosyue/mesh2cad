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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_011.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_011.stl', 'source_sha256': 'dacea938c9cafc63a1be32092ba36cd6fd4c4c4cd44a8144fa1a61bbfaf820ba', 'input_faces': 1068, 'input_vertices': 584, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03640754520893097, -0.20357534289360046, -0.12748053669929504], [0.2510678470134735, 0.09577751159667969, 0.03539751470088959]]}
GEOMETRY_BASE85 = 'c$}rZ1yohr-~GMCP7G9RObl#nlw)IKW8tyE#8yPzc4J}(b}JS(9u>PVuXPm_1N(ZdYySCu=R7`~|9IXp-toTo8FS3fo-B5(@7n9Ey$?P=-$qH3xfu8_zp<_5VHZm!!w{u2T#R8o1`P@9)?;v~{y`&?7#TH}|Li`$Y3nAw?UES7j8X30dkpS2$i1qYyI0T3?jCOLJqHXLGN?=c&I1N@?;&};E`100NXQ2VbP4K_uwAr5Wls;c^2I#dM!Wrg{4Y(yDVR>{)*O>_Ni}q;dd=q3#cdf)<gr}>yv0Xd3DrDrN8}6q=SprKeLGjS&5Om5$4y?Lp1$5>am$upt93j4`AThHbLRrx&&V&xXYRmpkEWiao+BQ4OtNX}d%X3y=IKb}Hm@GKpBv@pI^_2A3_d>1A-AqxuX*nqi*)<uJme{M<2+NGG9B{w|IN|%L$=M={j8gTywxbZUZeVJJs-<>tK)vgdTPI!bG(rE>$^$4S?D;2JnqF7*^jM~|1#}|(xs5!Z;Sp}<iF4%@1AUx=G|J()8jUN7Or`LC|p;QurO_(>ml;ojgWU9x<rrr-yY<%7vX&7<s6~;xoyb5RokiUOHN*;dA-5NF9)Ojge6)R+tcpIE9Tm&=Rc~X?%z_#2l<1cdR>+@H<oMrt|gGa^4+ET&)yK@<62haAxn3uyPnbWF;*T}h5byx`OG)buZMz=FF3SA^Hl@z`-|%$FLH9X_RslD>-GF^6~%Q_-;e$0{@F);-_Mome!DQP+8-FL?PB&JkL#rMGn_(ZYaX<5rNeoSn}Kn%b2{>Xf_wFP!;_((nuZ`xAA;+>*HP<dzUha&!PfoiK9PeQa*k)C^vemF&+LrcxZtn(@{>Bw4Ugu?gOcn1V{5$7{xo}gBKP#g_}o(#<3Du~<e~oX7l(&9<aG+@I5&UzEx`4SM1K#8#(Ca;*~ua2{cG3?YyTK-eUSI<wnF!lFYO|S{7%w6lDqlVT<4HSHQA@<-_CohZg*~qd{+;xqfvG~>Uc0-$B|L>-XUCHr-2T6j&(TC9T$Tga^4qa@h5t}m=z<CPdu?s^XK`OVw|i-K5xICXYA0RO%C~!{#svSe}j#>J#;?uq@Pgl`-^+3J7?D1EcXWIxp=Z);@r5JKT_|PG?{j4yYq*aCBBc0Q5*DrH+pYhhWgyVem1lVPMjM>{zgBAeb9N;tUn(4`ztulm0?>Qa;J6L&*AfSZo%)jMgHu;X6=Wo-LStETeLrnN^5bRZ6@e=H}B0tKc)P5LVq4zxTixtJ0ACi+m-5xb0cU8?%!6~aJ++Ek(b}9=VL@QM?ZY2i`+gh^=v-@{hSVYhX#5+W}kd$@A6CM8>8Vr+qGW#H|soLmWf2}@)PIZv&$acj@gJj{0q+Coaw5^f8AMgTeT0!AMm~?UK{OGgzEhj-ncsUzbQ5HA=_}hqg+k&^Y_K-9{*w-E*{rX_y7F0=EllG`*pie`hD82aLnSw;~~6R82UN-IP=g5&C8@)tK0q-<QLp^d>Sn)A^%wxd99<oPyf+*%(#~V`OO@9T+4w~k-8oH758PjBzk|jo!F%Jmyz=&^0_DVe2mXSa6Vt6G&hg99M+$wTHHbFFk}+i&+tV*Po0T=-V=cQ?z>a!)*G$$_y1{x+}MHZeVtwV!6;LDk;DCR3+HcMaYOs)Dtf(^4Z|@mG9=^qPt|cA+pzTpZQuAg?wdVtb^oz0)emSMxC(jPC(W(R7wLJLspjHyHSPw^Gp2kSz3xrpHMi9GguJL%e{DahE%p;Wy{op1<UC`~4|YL)cX;Bu3O7JLV6h(8;=5M+-|XgrJntjik9WRr*4!yCau4?z@MJ*_xl3Wp=c~_;cgPF0(0;I9UXJ^HY@B}n8;^r=K3h)WxSb9nH$G$D{?`Sc3(J=y4;m4wb=^H1>zrz#Z12@X^XA{?VEhc!+!Ek)Qn%N=3DlqG=!W(iW?}r4|8h{b{pukvv~;<)^BaZp{!$5flYSUKAyp1wyr#qcll{c~n3?MV=0>WFv(y8J!H4|9=T+s3`23H+d~0TTkKDd4O7jk%Q!TC|FWOl9Cp<+L9QVo+=BKnj&6X)5Fs`h~$28N=3)`^?OC0hf#V{|u^~1bW=!Ev4akh-k=Vrxo*zUF-o;pD5ZCGyA^G=-KcE&jITXp!@|CV2Sf&LuZ3Hi$>80Y)S=zU|}{i>gDwo~C4w-e6>>G4Ot)I4DTV4nBckI$#J$MAU=af{>s=3w2vF$wL<MPlB*+8Xm(|76HLj_SB|yAgx?DE()wN4EY#zjgeKd2#!5<UT{u{(Op~y50B=*6CY{?AGmo);;z2UY$q#H1n_?C^cF8!JK{s`756@IM4nKy%Xo<PGbF13hO1K_zvW+{ZW_YpAI|ZqlaJ~i2i`{JhuwD%W(Z1v21UIc|PR?<Y%|&{BNoJ6rYdvdTMT4oDJs_VePHQdD<4&HK8%`#Vy+F_QVF*&$p^L?%ng4hdXV>{nV_r&hxQ{cVInycOdeP)v;bm`W@>=*VdZbX6!qyKi~0Yuy>-|=#doT>f_O|iQ60B_i2AxyA0jukZ&_|{9F6pKpn$!X>P7chVy@4rnhc;rbk}C4DJ(`4uf=DJd4HswBR7-u~mam-@?(zYdL9du{=DY+iRyI@3kE3;XHNlxzp~rK0g`Bmtx(Lvv!njFItD^Jo~z$xEt0#bIYQA>8hCDS}wtSo8c?wgM~XW4v$p8{+ryJm3Z8S4{e0&@CiVkGf4Ln>+v(vA>Tb1`){!x?I$-vZj0-r`RUZUZZ}SqLY}G}#@P<*5dC@5%*gZI)X!PlfS*`5*7`J4{nJl;UWelO>ra01GM+c@j=|@6a1Z2`JD9g?)y8x2K_BFMujBLLeKM@iw|B+1ecoF+810G|LtghQ*0=WccJFk^%ap?BNa^%Z4*A<V=(kdZFutB&!*h|_U#OSwQMB*A1bM)`S=#@3e`4IP37MXFycr$B@HzjeGjd}}Ma{p4g*xOvzAw{!a&pZ3`D){NI$H&<LmmxRzxNu?Z#l<c{`XzuqraCU26<6$tg9d8!2GpvA@Z3ebUrtnt6-g!{w3Z!#AL>KjKq5bqkenjT;~|oTy>r|CRIoNGXp*c#|#YCpVxdo1^s^)^QV11Z_n!u*8VpwJ&)=3*z?HqHq-gp)@~Zs$x+*pUzmt~531Hn_xEEC@>Q;=R}HTSoNrs?Sx4x3x-ARFeOEk}J|7tWoYecyHqIT-AsZj*II@Ig#`&Lqhw=P08sm%eq1h)8{d&F6L~UQY7d|i66dbMRlewAZM%oIP&%=WU<Gv|}d`$+uUR&!jxZXKgkw-SydCwZ19rIrL`<TBcwZZzfXztYxdD+d#H$Fe+kguPC=kBh7IDX?}$d8}Ly5i%1m_MekLC$%=Jd+XQc0>bRPZ>#O;ksO(^i|*Qft>SIZ1hSzx4vJl?{AFuUC=K<6Lr2dilxVUom{?{KOamQuIJn9J>C;=J`CUNwO6+{T*q@m=~ZYSeXx&rqTFx_#XMi66Z$zW5;@l=My(z=p9i%yx2-n$dBpM0+`i5+j-|kH^SI-<t9>!A1#{eb-otfFE`{-ylk2XC)yShx>pT{o-4FBFj#8T2e9z%Lr}k~9zWgTUE&Kd1upjE>x*U0EJ@iAxN0_%W7el^zg66iu&X^achlHs2*o*o3<~6i8Vn(TtOOJYA>pB>9EQox^XVkZDAf6XK#^ZCN;3XYDf1ZDbL?AcUb<y*T@$TV}e?F(jHRq4P`MgYuJR%#`;bWQ()9tQpM{0k52*td#I3mP5QEp7}!+NISe)RW)JjnST&$xL8<EhO+^tb0y%)7>PJfB{xgxqTxKCg3Bz&fzu49tJA<+0z2cpvg7&-@tkf7!2?r%E**s?K#$c-xpAy1gwka?aaEfcG4SJhry3+l{&1vF<F;a|q5aUscU#<ecG<2M@%2d%g+w6YhchN<N2mwUNz4-R$$W-vGS#vgdhgVt&rK81v^;E9R$)MKK=6mq&k(3C49VD2;iW@0pDeDF-^#Wk-ZQPZ@(2!26`v`Nv#y6zll6?U9Gi$MdF7bDM6*Tp6IAaWK};-CyAOKRRBY3yrD+aK9{0iFxlpQq3(TvteHSP<x!_)BEUp%9!vR>%iMJF@7h04OD;f9P_hJ8NBZZ$&8%Oxqs%j-UoZ3AJ*vnY#VkK>(Xoky6E+;t&Dcxw&1?b_`|B(^?PByjjxP(HRCko4~OA;XSm@#YMN};#N*Aj-xc%5kIw#jUG0nDx?;NrsNde+LEJX3A?D9C87Js*FP_o$uQ50^?(1u<u^;QM7V2MjVO@Rj0N!I1z3hYg>no0X<}>d1vny)qby)^to*Cb5ymzA9821$8YJDK~V_oa5?vfVc%07?T^R~?~KNL-l^<K<fPj%OJm_JW+9jp6~ZB;_AYfCp=*NCR*7qd_y^??m=-#zPOYJ0;uCHmzz=8YYPF>e^>pVbhvuLJM(-hjMnCT-VoCysmi;85>Gx&65*yj&3WWBXY|^UtmrZ}n>9eh7M4Mf>sE6znJHM|W)(KD@emiH+zt<J$Wu{kf&N9ydNU#!0Gm7?;eAx2@1W?wK&pOihRPSgUhl-bfvS`F~qfYt1>Y8dJ{UyrP5ra34&=Jn0uUz#%_73G-h2x|sK4+O)&@p2K<j2Kj1!->bcDe+$9=yT^+A$ey1rutEL&JFHjM71Md#%w7z2xt$jGNrW@r*Z3dAyi{^N*5#4okr&;I_2!F3`d-U;F-xCE?aztk91G^jZ_lv)a+-#D$v$t`^G}|bPcoFiJelGWzJE&f81tuJKdgr{@6q=q_W95lI1lT|;$!jo|M4N7XM^$l{wM#sOW)5JE4ZF7^8tCAb2={>O><)%>vg*?#u47z7;T-gF7zqe-=ROx;{B~*{W(B$uT*&7-fA}X<DGY)j;rMc?)SekPxMZd8^K>O|8)L=^=jR@$nEcE?o`G4>FjyrZQU_Gy1S0l?Hdtzj<i3=ExUtt+Jl9dN4d_iKFfn~+Ak8%RZa^rkMTL(c>fN0<waOm{~m(=%QJO^<~jeyJo9=V)|uhQk)O+m>x!t{!6AR~2KVpJc)ZUn_+4{z>UW%9*Fw18H+brGn0{q3KSX?=gzI^P>kIS5edOwnc`wQsr8(DuZdHczdEXoByP5{h|A7_Ht=(QD_o#C~-TDpl;j_YHwBH|g#eH408IC*Pn&y`HdVHVrq`vxxw3yFEgkT-gnfv)VMsrJuKjw|8w{%`LZCP=BO-G?0eK^k~?~8m*7~b1YY>e+mPEXa`oEeGzWJ{*&AA4>ru;}?)HeTZQT_=#gb;f-feGtb@{Sf<ExD?lQwn=O3*A@3Y-wV0ToP+%|t)RK-G#kfFHXHZL)&6MD=Um&gV^{~a+JyY^Ic&#belW`=({XL~i$Z;4`5Zm^62^Om>3HtjIBC1KA7?>-Z)}MBC}tHt@2-VRR_FJC;r8!$<}X2B?F!C&>Y+C3x8EWEu^jVQiQ)LZFL%8ux;@=JT-}YIUk|z>H(YSv8%r`f<lQ~Csn5cC%v?E^?OV=MkK^}K?+#DZZLS9luYGuLRX+1H-Ol&|>%~_195EvsA#dCQ-=kGydwXu(so(P&&$Hk;{rhU<`=8-HT3ZX>Bm8!muK58EyvJDk4D;CWvdH;d;N}{R_T!ssZayoCeh%XI2vd(EANBz6hs#w!KQ?@T{TRDCt6y$~=drZkk-wOX_bPM8Vtsfi`wZQlT@~LK-`}h2Of%FI`Q!)qetGdz%!j_sk=ws_TZ8v+M%<H`*nbQ@M{=`XFWX=}ZT~(i4epCSIls3x2DV<|(Edae)?@2h;5}`r?Z~6+>wOfS_B7tt4IdVo_`Znse2Dq#$VJU9-*aFdICDnFf$5!MHpY`L)*%a1U>%sGpysv>Ptl*&l@)dWbw{H8jqF&zZE217kd0oWy?y?v6RP{SoNtf*-8lfyS$<n|J@zM$ov7#k=Q(c28szrx0gHI*y22833Hiq}m_J=2(Z1|`<n_nter!#)>-}VDnNrsombmtq2a0h%+?y5a54Tu+9&%k_b18(sQ^~Rt_xq<v%p*g~p?#!3?xR*)^ggoOvS@DmwhGtV7tbm7+)}7K`gsoC=i76`Z4B<a%5C~3-j9*@EbjM13-KPLQZwX@>)?K`HBz5r&98lsx4wn`ui}sSW7K-&Pvg<gqn_yavfbN*>-xAG{m^d_=Gk8l(0*z)+}8(ww{^&qrNH^T-HFd_d%k4^zQ3qh6yFmZ`;L6sJjeCwI9FV!Eez|Xbp7%CY0qC&$9gZP#}tQrM1Rab{;@irSk~4?Zg}H<m~-6fkbmrp<DYwk_Zq#gBX{eK_80qLePhp!)xB{(QGpKa=SAba+`LyhUzsJ|BloR=_kFI}_3uM0Gk+oXGSNRClhA)}(#_ZHkR15=bkE@q`QoIg<D$564*9ig7+2$K&34FRHej9kx#~8pW0PFSrxn7yVcTQT^Kq_>ymNW1({kat*cQ_Yx&7}+uHf^?)-n|N{WjRo=~crV@{4nEJ!Rr_onTuOhkV0WotMlDf%+V3X_sVy=7qgbua@KHJLLBF?N0;n`8di0d6G4FE~s%8>qFak<l{%Ia2SWRk05`03D-3>zdpBFPJKdNECBbZ<y9H)#CeW*J+3YJKUfDANfxI0s8=|Du7}O%ZpcG?&<_jneWkIvI&%9u;aM$RkJ)BU(%d{WntzY<66={a^U*$&iTT!l9iHQMMj(%N!spa2tdlKQ?;$VjgMKLa8}s?zf(ua>6YKvAi}5`5-$>0(|Dk+tZ0wEmScvv@Mq@o3+!XV6$R4zxHVo&vU;)<C%ng@`c+VT&$lD>`l1ArGYl|89e$$qE5$b*)=i!pp>YX@`w&8R6@-1y|t5qBM+KiaD$6e8Wu$>A)ery8HzZ=)dFE%3I8;I{Kf34N;9c&lgA)j=}@pJrb&c(QoTHw0+p6%(7^Y4YsDZYBYSgv-}{LlLV-yyobvCSKc_RHe&eS;hO^WRy>XNTZCqcD$I+B+}Nyy**kZ)LOLJac&<U)US%C+64ZI@`(~nw#%E9X@9**73;gf6wq7?*}ZlIoMC(HuxO0zSZX%^YLNi+5g3H=YG=MHpOkJZpR-(|HSfs+0saJ+vq#E-ggi1c~^3h=EjQ6_<N644N>2>t2H-YpG5l?4|JZi=YRU=v<K#grV+^bp3ri9DBjn7biwyAy&t3fRP=)-n+5rhw0J*xr8(LUZ>qViPYQfq3{In;v$nrF@_U``crI9dU7wFEx%X&pdS*g<>oI+Q{wLqjo_|l0P1mKizpr3F&tBm@$?dbcADb;Z{?4G)9`svn6VDg<i{LqYRtr6@`RIVY{|R?rg8bb*{5`<-?b`ot@%xZR#^L+Z)1x9Ca{irznRSb{w_N;*oX@kiy~~g{tF!|B)E4KTI}pzm5p^}U9XNpVd>yUN;kJye@b`0W`;Z%3^*x^D_7lwww<oCY<b`^@*25*Rp5}9kt@UipV?%t9FRF;^Iyyu1@W0z2_dkv2?uA42x~w&N;O|Wb_s4ni`(=A>I0qu%8=}vdvEvUT=l4yfS1aAmpS)ilyr)gpS##UU@fc4_=3qa&@ja>83;k#dn1<Y|7@kX?+{Sa4*GS~6)@Z+3XP3bB_cf7oJ!X4X1=kan596ordVOxUHE54|*uSqIK3d12CGBuLpX9iK`{GwFJU=d<iS~EjBOm07d1*hs53qR0qb^@B=zA+`vrE{|V?Ufv+PpgdSg)nPI`z_Q>}SDw%u6dm59<D`8*o0?@VOjYYMtihq_g}U=Z(%A*7r8F_uG&COvLwqwyDv`hxfp7-=}Emt>g2W=C<miu%A*Vbbhde6+Wc<51fwuOpDX`Dz;fG<okRa&fgXrsQI7w*p^XlTE`Yw4{Kg@7xq7IhrZu2_dL|xY<M5}I($E9tMf^7<NYBV_v=%A59pTOIHK)WPD6X&p1N+ao++id<@{o_e~bCev{{Zgj8AiHEj^#U^U?lZZ{(5vwO-+&QJNd356*uCpSvgBJ*wyBcL2v-!1?^?3(bxCPm#B8tn-gq@5@n#abj#NuE*P$JW7A>@*K3^8jSZBT|6~6-6PPx;lFraU9dUYFQ4M@KH1toO!GhAKVHN7&63K=runpE91qJ{=<oMUiG0)(<R6=3-l&{fb2DWU<N>(e*qC%^Z(p|u;r*MrB)iSwx++KFzJAp}bIakwoUicw5^lE9+%|o$!#v>Tl=Zl_-`^1Xzm4w&+%9KBKHw+z@0DIZXKnvh*8I<V8=j{z(+lk*IwC*oq0epBBejn^jFZJze04i>KeSKt1?RIcKh{6a!!$R#XUB1yF4ymqEOC#}{&*?muKYX3h$q;8WCP?GgY^4f+xlN<|FS;cv$bii`>9#vr0(B1jlXxf@I}|nZWVVTpS~D*o9DXzvlJX0t=D}#!+FWgWq)gX%U?FljkML#-aT5^0hZopG`B4LeNJ;*7Tu5a?N80kV#75zudmVP53_3EDc#SG9mrFfx~_8DG*ENf+sD{XD&&?YlQlQ{ThTtp99>UaMqEQa^O64DfcYg{KX1avls~QeFO*huTd^Xmb-(TEAa{PI>t0)<8Jb)Ab<o_LxCeiKP(4(i|J?o?g}lT#9QR=ltPgrl#D4nj!+Cc1)7<jULbT6*0e=U!D&HFIhlz{PerGwff7uu7xpp(osNZr&e*2+*4p~#p(%iDSC33GCdOo(HVVaxqQ*b`EGWd5Dg|}#KdzTFD4>!Pi;%A<-y8r4Kkv|xw&w19I<u$jxdUICudR6fGx4x?8W|B(U-csu(+Gnn<xusSghdkVC*4f18Z&?_q{TZIYIIsJ${M7Gbte%Z^yu`L{h1}<{=9aC$P`9R5&5h(obe(1kD2%$z4sh6yW#kpjt+nIP{^u-hA3JHY_IGT%&lj})(pq|5v6VOKajkLRG&jbU)Ar%bcf-F|x~RFw2fa_N8~FDps~c)=$y)*Y+1U=`J*t)FHvd5Mn{y}4&3<h(H<zVEp3fcmdmHv&^q%hDt@Up`PfO-_w0C;1dF=YNdR({A&uBl~Rrh0C5rzKw{tM@`zcJ3|$8pUqm(yL+{TP2~|Co6WqrZd0kWbsJ+in-V)nk+I)7)@*tnaa7m)=DC?N^b9AH@6ZZ?`oMpL<PnTflbAWBF5|pJTpjZZS`2ZVTP6xphU#%etSBFEtOJd=}SxD3j)<XFgolQ`{f6I)#uoSf<CdT?xf?jEcLA@jn*(d7Tk;ewglx?!W1L9C!GB<Q;NqZVo)ExjEn({=W2F0nIJD|8dB}-TNVb8-V^#9ft1>Jy&aP>pmLoSK;qetzXaJxaY%hKEKLq?$$E~?bF=E_~}#$&lx`HV>Dkm7x|5N^#7Plni~&KVgKdd96aXh@UQRQC-pl%r<`GkQX4Kt&n}7n>79h~pWXlWe|i__`Ty#l-jyv=vGV`Fe|wiEkCS2KO;EuEWlK>01ZAfeB<G?RrWYg^CKsZF^U?E?^O1AXbC7eAv(Ph>#WRvE396Hzx|DEzO1K^+T%8iGObJ(_glp3+<l1C!dNr~)xhlOpxhlC_g38cK(aV#I@n`PzQsg4^67*8!66Dg9uqVAd*^}%=uSWJF*Q8s>7WS8L2JSZ_Rhs+DNYBDrWa0j@F!y3j^KoDKxIa7R<aSQB6)v8jq6tb*Pe(3JcTP~I1iA2M>B#Bnxyk9t(%v;eSrb%%5_Y3IlbzXKxK@H{B&Z@KT!H5!=TVXpE=%_ymnB!BS0Gp5eyXs&Gk;!@KXauj@VqMU=UM5_<cCQN<5`0KPSCFeeM!&{O865c{D%IH{D%CL{(}5B{Q)H$OMgLrLXW4vAiv<g;wj<xl<-&j7xGu~Z~8BCQYUzF`Y-Y?UYoE;IE51=oGiheoZvqbwqGacZGt}1Ka<6Ol0TBa)8%)+(|<7k&f|Whe@gVbpLm>4?9<our{ve<xJ3OMM}J0+Biq|QOLV^C|InY2{~<r8gzwWIk{|LI_bK5!l<-~p1M&mb@-8KOj}m^IsP>QP@#M$kmz3}a`g`&R@;CZd@>kaU8zr2?2@+1}^gm-lI4NtNk`hi$38$r}AgADXNJ|N)p@dU8{m-~bMVE1qird156D0f}$H`~%XV&9CO88$&_!a#*`8n(HivEZkmT-u_5;QA8a}zW(K{518Wbrgfz%k?$l&}}wo9spIOCLnuO+P{(M2<?(sRRv6P+fX`N_ZUo6nPwZH2oy`B=<L(K8QSs=P{ZRu0;tu)6<Zh$ya!-a{X7>4>QT)lgX3Wf5PK<jQaFiiLOOBGu@f&%;RL{w(vFXYZiGHYjlnJi|y-jzgg&+$>P!`3)_gNrAwZc+rsB5;j#2Eau|<2mJ+s7!hZD0<jL$8KT5bWB|Mrwmpqr_X*4B#oDz28n3HklL<v`-dy&03o+?qo0hI9mMB{Hi{RnwK`7$MZi++-PlH=?aC47?-K247zM{&HKri6!6!qpRv_3HGr<m%)kl<+auOzL!u^%_e)Mh>Ec8`7<0E9=pa60S)JH=uVWcV;~rP{MsF;r;aE<m0T>er^kYH6Y;<tX(B?335kz06Bp5=tv3gq=e7XFOx5`9%m`x7)tmG{U-S)>v4q=K1>PsrVl3%XFYmT!k+XbWKZ(H23+d#FD1N-5^hfqA_uV^?J41ElyF&kO>#}vqbwy{nG$Y8?@R8>dbFX0*HFTb>0il@$+=iRsZ%c2t0OrVxiKZYhQ5=$ll53b2_K+@kI`euF|5ZiO87V>yoY|6e3<pvLkV}Fgp1KV$)2oFF>VV#r-awhcae9o9_uLK7L;%~dNp!2)}tIHT!<1bL9a}%%zBidgqu*p3+ZdfYgn6wl<*BoI9(FB)FvGzT!-G6+?e&KLkZ8LgtyZVkPomP+bQ9_lyD^dIQcm15lIQJr-Yl*JCHlD9!)9XJanl|9&QWYXT8>u?~|8N!j0)I$Sqip#*}b=N;oII5V;WRk&_b6O9|JaHz7A+J!(<H6Di>n^c&<8<ezk@(@%OGvPifhB|L;ak35g{7(xk$Q^FhRd&zrQkByXY1SPzTzMj0E^;kv;H>8AJ=y}NEQV$ny3*V%K=h2sum$4r6DB-%4a5j2=a(>n$8zr295_X~ICFf;5Tqxm6l<-LUMDj$|W+Wwim=gX%|4IHrF2$Njol3D@L&&Ab-6-Mt^l)-G>oK1aUP%dWp+}G-SdT4~@El6G0lgu)A?wkA63#@I+GOIk@I}^Z9{D193MK4CuS>4WdU#R7=_%o)^bF(-tVdExI1MFSj9!UciS;N(2@j%#che7(caz`IzmUJMR`0kiT$mE>LhnZI#(H$2gr`u#OXw@fD_M^vl<+1>coKaMc@FC_i4wL@!l~$)$l_9uRNNNcM+pz4Pa#iXJqA+3Zj^8edU|qt)*}TaZ2wO<IXw+I4eODd63#~n_n;3V4`OY4P{JE2;ivR><fr6(teMm)AM4eHoR8d^5*|aJLY~5UjG=@VP{Pyco5-73kLi?fS4y}f-9omo9wjN^53G~a<^v_XlRl8VliY_AE<$%ByRjZcDB+Zpa1y#fHdv1&lyE9axG+5*IUnm$m=f+n39qJaB(Ekvq(3D;Wvw1^TR0~r+??K;+?w@hP6-dDgs0LMkQcBXQz_x`lyE0{S8`X@qZ1`uloEbzz@;{?S)-lg*W~S#aBq4aav#>CHzi!05>87`NlwXnq@{%UYDYO8Jry|>>yeHUE=mdaq<0~AVQqR+!s{vFNA!o}M`TylOzPyydNn7zl3P;3Bj|(4gISLel<-VScrtxFc|7YenG*J=gp1INl8drdMYt{ek~P{+eo2m?_a;Y>`%}Ut>BY&#S&x#Ga7Icv8QqEO#Cjy7gfmgX9`vH*qO6ApB^*czZ=kOyZy?9fACVuiR&m@G&Or(L(p!>SvL3#aa4;o2i$0S)ll7QI2~VJe+tK~W{;WqkO1K~;{E9V`+Pq?oBFL}Ednw^z^#0`jtj91)*pm{@LeEIf$a-X<gi}+(ndzCxnOKj^lyG@UcrZPX9LU-Xri3?9!Y}A?<QL@JteMm)H|ym~&P{Gc36G=)lY?20k(BTZN_Z@N0(k=KF_sc;LkZ`n7bF*Ct@3kQ_&sa1m;9c5h(3&bh&+Z8_NIH1Jy{QLO4yYWcBZE$r)E8zDdFsta8-JFa(ULHDkVIE65d1KMBYPwLw`Yj!CJlHws2lbxCOl#xf$!xf)XA|35U{WkY}(Sp_H&m3Ad%UA-7>Y+ET*ql<;TPOltF)H9AE8Otw+N)9GW#V_1*rlyH4YI5*vu?8<uNri8On!nx?#$=O+tT$FHaO4y{2Adg^eOiK6wCH#^8hWwFSfHjjk6=1zukPDDoQNk1HL&-x~kBOA<LP~fV-6Wf=$23aVN(p<=-O28(l?S(lf3QY2@(*$}eL6XsJev~srPn9dXFYr=VRuS62R$n}E9;Si5-vyyH=@@j*JeE$QNlAQ;VAk6auoR+{UiA!YxRxW!o?}!&h%E~R;)*7N_Z|Myn?=vypZ)+K?#RZ!rkdsvX%AdP6?N#gnzMSQk!3_Q8f7%`2r=pgg%=*oAp>i3Adtz%h27)?yN@{N;nTCT#8<hT#)rBMF}^jgy+y_kY}(qb130cl<;r*H}Y?CIo3?-RF3uPOfE<6K?yIW&n3@gJr+~KYboKS^e}Q5>#>v)4y1(3)60^}vR37}Eu4&gfh-cf#cT=r7I`ft+=1ST+=}(+KnYi%gbUE~kn^w}1t{T)lyFCSb8>Umqa!7}f)c(;KSjPuPMHM$oBW%#N=XS<p@jR;dyspu9(^d`<&^LS`dac@)?))DyowU;M-L<ivL5{?;i{By26{5GxYQ#9w}l^2!kg)9$!l4U&6IF2O1L_`0=WX~QJoSlO$pbaS0q<tJ!(+G-6`R%^cCb4tj$(R_-{%$TN1d`CL1MOlU{{fh4rXO2@jxzSJRi1m$M$LDdBCD@H+Y`@+#J29VHw>3H#8ilB=>FK9q2Fy3{5+w}s!bUYp5p$ww&Rq4ZwlUaZGZO1KUsT!mhmT$=T$LJ8NSgoo3+le@DX!ztlNN;sbWH#wf{mIN+!a$~(}lHJISDB;=k0ptO!$81V?2PM3ZzKy(%_1H%V@1lek(L=}~tj8isxCtd(h@PD+F7+tHZQ<{f@EQ6M@)6eK3?)3C5^hGXL$1SmG^2zqlyGZ$J#szPqctTwjS@afk0eL3HfJf}|0v<oN#IhO(v+|ty%D()>)}TUZ>EHg(sz(|upUP#;S-dwjlPS#i}kQk!doff_Vgy?Cagz$O1KPNYEy>W!b$08$Rgp(l<+wEc=CAGV;m*imJ;@%TgVpH!-wuqZc6V;_a`r>FQEIA{rUR~=+ns4Sic37@O4U9UV@!vUF|P1g)7jdt`%5cKXL_fPfGY8eKUD8>vxb6K2Hf>qMsn2VEryp!WSvwL-eiWt*qZ6O1Kv#T$x^mT!!_lObMr^gzvD%QrA1I?>O=u@_b6T9lb5NE$h@SQT>Fw(Oc4+lAE%AE$IQ|r3so~$p7n6NO%z?Je3|y7Vk%%N)DlfhtNBbJMlO}=mF$#`YL(=Ie_Q4D$)28j-}tDFDEbOIJ-x`PQK3Zb&uP^$tmG#^a|u^<o@)Y<enT){VCySO86@MJo!Aw(^X3NIwgFKevy2U<LMeDe1;MZqW2>A;&=+8glo`KlWUMO(q%kl<hJl#N;s50pFE%ACN$A_5?)CkK<`HG#<~umcOrM<I2b?)kD`Pp(Syms9A}d#;l-5j7Wz{1N%}$hQu0!c<Aap&X-fDLC48F_K1W|fUc~WzjuJjf3GbkXkV80*cO)9$!vD~p(Zk8%9LLWRjqhiaaQY<hdt`ALyXh(6+VpDVY8<1rDdB;X@Hu)kIhtei93^~%6248pPQK1DdYcmdixR#-KSMslF?xX#9z_Y)qt_tU;25n(31_8*pKu(@*cJ9|l*Gv;>HpLJl+^$HC+~C&hyP)z|NA!`{~1i;-yD;$uRs4N#<x*&{VvWa;s4}Iyaw`3gYka=^D+iy'

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
