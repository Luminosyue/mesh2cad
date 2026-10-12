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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2084a523a5df4567844524afef5912db/part_008.stl', 'relative_path': '2084a523a5df4567844524afef5912db/part_008.stl', 'source_sha256': '8872083da10f45e93c9838f97ddd67b6210f27e71bd4ea4d9008f57efc4fa436', 'input_faces': 604, 'input_vertices': 593, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.001818307675421238, -0.034089189022779465, -0.47143369913101196], [0.11986750364303589, 0.14072611927986145, -0.27317944169044495]]}
GEOMETRY_BASE85 = 'c$}r233N`^`|nT8C1y3W!7;S7O=(d@4X5g-#v~<0OgV<AF*Fn*I0y+6kxAy{Bq0fz2sMjSYWOMD(M(Tktg&KfwA8<QKi`wP_g%Sb-F2_E_WFL_ubt=F!?VwO-tz{pffXw?Q0Pw!<*8Sb<i=eTg*8{Dfil-GV9t~YezV*8&kA%=>TsX^aWvZF)4^UoF3MbGVVjA5vnK?!>87^nKB-F^ceTx=nE`VG#`*is44CN0{J!I+&-VM*pFMfpEWdwWw|%c`M|ZX38}8~N_5bltbvA}o$H(;gS2VLUj;Zpf^`!$$!;g<;udOkQxADJ!)Pnn(hu=8vhgFMaYCed#$bGMC+*c+PZ|7PPPW}+T@$9v_IW&>Sc|7Bi=<A~{7cn&+Poun}uTA9rudWN_{qOC$!2Pj)emw7#fE~R5y`9`Qrua?f{q$ew^1r`z?!4$LBUkeH*5h@TMBkY8`Y!(Ww@*|5Y1gQKL_D9DT9SHE^wlk;Nlfj>QI|yD7@vswCeeK7U7N=JCZ)ak>l=^GiN5LGZY!U6X`9QUug^QZo6qCMAJjk4Z#p0M`0XaoU-|~`uPpWR=kceE#X1!8b+DFQ<G!N*63F{qt$j}P&Fk;1;_>c%CH1!#`R}FmuEG23Uw4?r{c&^oyo{2~d|vwD0Pd@iZDaU2OY&&GM~cWlUl_vs+3%bceQnffX@9k&CEPbQ=g9SNti$I#@A6yw_<Gpx6z6ym_th8k*0I;>CEqimug_}6_tD0_t0y`HP#un&$A9kjMe<JukY77AhQB@^f10n;sS@s+Zl!Vj^_fdQi@v_9cQMyXK0L4TL(y#h`i(A0e7--u&HHO-I?Unu=6%ceQNQtk_VH{0_x15na-G0e*9IKm<3AV4$D^Gq;=a=0j~-I}z&9dxN%g6nFX6t{IW(2Mw!aVgN%YMz{_^>~(BTXII=xH0c-|df9rdkz9xoMf-^x8J?U!=7gyQt?W$`#?ex`N%r2{{Qsv2hU^*MF(NABAJbUqhNmFi9TwTSz=_bbx5P<|`nzTM&(k7J)0_@n4+6E4c<;z|d;-->UVRR4}|4anu=)PHJ4<GdO`{ad=G^Kl;E@&i8?SBt2>Pe2i!_sC14uMGN|$FaT-;_GZ(E8)J;vJ;P^9((x*(bu;2OQtw<-LS5An9t+18qNEghZlY?`r6=LUvWKkk<Zt<5x{+O{ATI8YTYd2zTvTo_qR`I)c^MqiobS*bbWSwd--+gd|9_T1aklEOzHeOzTtU_$2X2=)4c8!abNSQc#yCEvD(}>{wP|&<NWiPbWV+j0SkHmRo$d>WIQV3zFBKBKacjg1YZBf;}Y(x<CkrxI!~rL|1%(n|NOdAx&BLw$alLbonObdNA8iYKTk`zZ{{^l66;xeR<wxLZK`}8pO<joZrfNo?@GnlOX%Fqm(E?8KhZ5+s!#a#(7(1wbq?PcH&VLZDwQ8n|EPHBdh7UV{|}^dX9p)3ynpi`>D=inc5~kxSs<;0z2Y4C`6HxtaC~b(wsc<Xl}(oNykk6YJ!#4N>mgmaZ?$+Nom0oxGmlBv8OK)!J(kXq9vaAf&BsGNccBSO%RQ&?jcsS;^95fU+*LY9+UloE%R8rzZ;kVp>kYo<u|hgu+M2G*$~(V~uSa%?5$n@h<Fky;(KpgLQp0yIqjU7)E9o3Xo?Fge5B-+ciBZ~?>LltZ_btEaQe7EQO@hVq;#?n;=&sz?Mn*~dZbbW#zwRbKN7jRN)ITPW;uP+Z>mh#k3b8(&^|2G4t`O_9Y`#f>E4lBpSjuZ9@8-U?rCPEW-%5E({)lGMzH6yXLil>_h)?13dJ;|jQ@e8C)Z0nt#Y_w2z7;znmd;B)_f<22;*4%4)vamnCO<1QL99<T{T%nT&wi5Dxy&DuDD8`x{xn3aE9F>2zK>=`SGs@oJS6XXrVsbkRuiTAQ8pxSU-5b>)q|a#!0+3Xaowc#H#VQ+z7bO`R$PB2_bK;vpONyu=Qdf*Ul+wo>u+pLSi@gW@y?Ly%JDxLE6rCcI!FGv0rGwRwkBbG|Dw;vh;?Oc>&kt7_-|XKa}8hd>0LzQnNIt@-G}_`rP4Ud{5_$mQa$YK8qVYE&7}3Qb_H_ZSRX2_kGAI=`J;X-66?X(^EAA?eRO<f^ZZ1yP8?tJ+$-&`vd?F2dHZYZ3tUV4`#{=XWq$(qP2YP|pC!4pkHzQ6PZ+UYtY_swlL-EL+C^!<%6zX^r2R6iK<=v}8cOS|e3ig`b4N~!xX$X8pmluze4lI+*VDX`%zZn)?Rs%N9bX%kDDAI(C6D41=cI}IrC&Wk{_wxHisLb_UgW;9t1aJO{jop!*W4oc&!@%|^8T2wea)SG|Da6r-=z88NanunTLJa3me%d&KJIJrrLj_d-n<i8-o87&bNzJc#PJo+ZSubV{*3zL`svh(^}BmidG+A<mgfz*9&UA~{=VNz>u=l|P5qOON$c<U_OK)Jdfu8&arTu;>#5!j<Gzt}r$Ag!{dO|>vs!Nu*HgW7g8TZ|M5#W_J9j8=YJ8knpZ1++<a_ttO8ZXl%j#WM{(hs34>rYmQ11=mzCJ8N9{;`Rbe~r|KTRCJ_Qyr)Kl`dQPRBRn-KBXc4_sqt{HgMKK5*y0nHtK+Z$C(*c|F|6eS1V_zVG^@R#eXqPjKJ(bdoeq$G1GP<?H;Ti!tTZmE&96+wya#K6>qv=-YZHQ=G5<=njoDc6vVdojQN~jN;GTuu)tG<%t{Bx90_^uCyoav0@!shl9QsePifvTg3e;^T%dv6VH+Hq&xTRiG9+=eYBno;=Z0bKTbSfYH41qSP!~$oq=yTpHE9t=s82_zF4tN%B};YC%A8>_luYI3%(K+lP9i^U3!t?2L@$H_57DRKR@>9ZgM^UHHiDl#<mG!J?no5(Ro|soh`<3d~5B#Trscm{0?2O*Ie8z`r7kn+&7I*ITYtD+Q;XvRDVPN*&?ow_1um7>O|LcaUGO@-08ecZoseq*5eq-SA!dD65~6*74mG8R40!A$pW5Nb@uU}(KMdXouz$IUQDOwgTs$+70-qCA}CH=H)mfQ-`aaNRjhMG$tT|<K{_wGax$*G^I|HOXud;#kk-dm?sDJs8!fGm?oyN2hv9irs(;g^DfhKj)1~^?D~895^L6Unu9zP$&nuGNFDl)o{+<=&b%U>r{-;P<x604CZ%un9?Uz=$CXcJ<R7;fB4ZbpDwKQL&a#I?|XOE=$8db({UmbOXu2=Y+XjPd(b)0uIk^BORU+pCMpNy2_SGz?1ltCF%e8>NE*jCy{ysuTe%Y9?qXj9x@v-%9WPfB(z6xYYDzKG^I^I4|24r-0?L>m7=Y26&(@K__&iCH5*vD`X=Z{}4?64z6Ay+q^js!sPs&h^CgF7=;wCxiT%G)~v&^qk9czf?bJ&6-K&)sIzc5%<m1?S*1|rFJ;=pW&S;#y4u`)BV9HdM;r(&u41yr*Y4&v{76i$5-Mj@%J^`Iq!8&a$n7Fn<Uj|o#*6_T!!_;=YqO5`Tewk&tJ~^IKFefoc-16Hcb}Km$ScC-5%86r>|6RYP~V!<G$UgH@)5r{#r#nl&ycgMch|rJ(JeQtiPXrKKfCfIA6Q|N%H5rWsx6C<9zup`H9H|VtnJ}=QRG$CvFhqYmH{m=SiP#()u{Q<`F2>o6%?y_pPAr*<xPDS0jGP6~}2c3g^C!_xG}OZk&=*Ufn8<^C^DZ9sd4qI^%4-pT;w%!A5cXN|U?fFCCpDj>qwh)p`7VM|mRqif6ujKhWfPN_q9{_{t}Jc|B;@ccV#7ejT@`%*i1Cb((LJrrg)&hDqaed}U?uCUKl){`w$kzSgTL6n{iJdJf<`mvGDHzWL>d6tT`7Uk&V&C9My9JL>B^X+7QcbKe?XvQ^x7%k2`4XLlFU5|iRLy-WRv?V$HN+z)6?pHtrbZPUa$cYJHXc4<6i{Ug1l@mS5q@SnFA&Ea*WKAt7{`r4RWvA@wgocq?2J5qng*TUSS{#Nr8@>50^iu?HQ1%vyh|AtI)A2oG9`OETh#Q2V{uNu8soR^`V<h~KydXqFB#}B!>Njlf-s_^#-b6A$N{`R_tbf1U&{Id0rY(}3GJU)}pV`NWLJV)xWMs$6Sn#6tQzM`zoqx?;=&dtM%=<|5gVv6H@j=(xNz8T-TKwLLFYCXjn7PVEX&*)V059~^l>Jz^H=}7t<R6^GQH9Cv(j`KFf`Ih<K&E$HEE}-}mPMBi788QFReCNAoN#lpFMqi}+VP}71JJWUCyMi<xJ+>#^$4`7FjmL@|M*iZUZ0Wqi*VcyRit&y0E6HE}Qx5rUB;N|{v{@P_d}HuX`Ezt!R(iSn8&^PaKAB7J<IcH@+rfQvvKu`QDJhhEdq~k1X})pA<WJg=F3#8St)aKjpZ3v+J3{_Mcl3{<^@%%8^TqSwvgdVim($CuH!YzvT{k}&M(?vu-h`fX|AFUk&Uoy^l{BB!utIUZO43@2gXbP)^G!;npZBUD#n+OuD9-ds=$}sWO4>p9qh8&l`I<?^G@hw38RC5P<a?BNa1Z(WpyVnPH>FRZnAc9OMc0>^UrTwFl!lq*?XQv2Ig`$v8=X7M%S`FXeS7w!4dQ&Ql)l_oJZ8%4pW?xNz119P{nga5G@it;0%?6xC(-x<f;NcbG*cH-{N!iok9|*FN%3d7Zjja|t$^Zu(PyI=$MN;J6Zv9ZBW(xGD{u~--;ynouSX^4iR+-6*J(U4uKDCse9gQ^dFMZq@*3tp<QvbjrTFl*um-ted?mdZpO23BaqB^}<ZBC0WJ&wz_;`PJ;yb<)*(XmNr{k-5-*?v2Oz%s17l&m_>knUD8<Z=?vC=&#{@~Z->qf>{y3fOXQQ0`*+pD*4mewu9pZW*8Z4&!Cz7=vu@{NqeG|rapQr(&vD=AKpTei4vj&DZX$rb0TWfoBU!NcY6eKLzTh;?fnUi`i2+sn4+i1Ew%ukzk3`f7Fo-G>dTDXov4eR-oi{>C)^oQ7HAxh^|LIj?7xHy%5$7N4gw=z%51H}iW^owaN&#WxD((z*<4A;q@}R%VwMUoD!%=V=W5S&FZ0OU)@SzP0T%`GYFU&r!Eu&k^IBhnLXj{hh^pUzLG7>HE#&IrRRr>j~|5OE)RLy1O&2@4#!87+>GrcXN61?R~ZQep>_Lr1<uJkKFR&Tg7Xsz6Tzb;wuMIbLI6h=zF4rW9eKCm?y_Sn96;nWdkX`edux?jVDuzuYLU_uiW@Yv-tTm`VW=jE648Ti}AH%P00UmJGx#ESR%zY{_9atUVQDuJ?<<0+e`6{lRf$Shl$_!aN--^F6O?~-$x$*sVus$E&KdJ@y*GN=($F}m!$aGl#jS?sb5R+ttk`eb58$`h+l{Hed<E)n=Sju>oaW|-G4+JJRrumrrn_T(dOPJt^X^OcX~yBzh(5RA;mYRx1#$zd~a?YUP|YEh9~*>y&xyP?jJ&Ny7Wt<@xMy@>z~Pe6XS8>>obp1oaS?+`1Z^jbpIFLOp0&MYD3Q>-i=QY<7=PyqR;vGy$C11{rNQdez9vjACG-_8J*vNB@}1Pkz#56XCLCe@@7sFt&bb+@9Z=5c`vM%6knTDgPuQjtd=Uq*XPvdzP@@Yk8d2`MC<>>D0+U^GADt?-<0Ze?lkTjYl@1+_{Q7_ic>3x|Ne<_d<V^IZYKAw&{|S_du}%Q?jw?EJ(p8G%zwyz`<1hCVqR_j3mVVrAyQszesli4lvTAfO3bSSw&%VUQm|jls|EHV|MgvoVqR^*a{7L&LEH6WUVT9X_w~?w`=z`KvMG+sh)6N7x^ORzXT<<1ud(n)`hLB6wFEJ*9#s2F9>3=N7%{II)SUbF%GFX{JE%SPl_wDqVqSgGN8Hzf>GzS!)_Ktc?puvV#EE&0#Yq&W>e(nM@8WEVv!W%>s~xLLaTaf*{=a*MN%LKDl>6qg#Zq2t$$iROH$GO%Yqa9OXQ?S|BgMRy(VqL}@*Vrcyq3|CelPRF{ZKKlvGil^TSh%8ueNL+_wDLuqs6@TvP_Coa%!!ZS6#l1`|7t5E2MeBSC$Qs#-lGkME#d!?WOa$neqnzO?fLej*{{Qx7x|`UiDlfo>OJTTiiFT_RILXAODi_uIR{p)i}Rb%&V>FMR68&mh-M$!hQSM@O9$3wpM0x-#UFNM9k~>nxF3?F|QI*$bEhBBq^^FvW?;_JhDg3tA_qf{;m6AVqP<}(Jub;{hH4e<C~$cl7Fmyur!{~Hr!Vh43XkHz8O@qM;g!SdE8eodae@lYO6!IZwxD*A?DRrM^OCTGYv7Xu{w_Y`ImQ#dCk>H+_x4ikn-AV?vsCF<_a;dz2+h1eJ^N?w2xsgDE_Cufnr|A*XB-=^6Fu=`D=52g*|lM>yaNmocoI2r!m#}b{c=UFZYf85lf}@5C4qf&bdY7I-X1G89tNZbWZzRs>8Jlxo^!~xm(PuMC|3SZN0ZH=G7v;p}Yb9QhY7q6vZFyyHFgD9&v{ITD#&2bnfVV(1^G~@#j>R@*3-!^Z8q;2WN_T&2?{4eatG^Ddx4;eL(Bg-FG&fJ9=N%BYSaQ`Qm;LDR1OJ?%M&YcZqqmsD-rOGk={Yt#ece_YMC5Id4=NjVB{`L@yz}5}ixqpH*FoZ$|$}<Ba%qi5TCC{)OUCFWDijXUq#4fAqoWVtgZ}20x#c|H_?Wd^@HM_m#7Cg2ni1Y)9@JQ~eP?kH!-_oX+{w^tobuD|Q0KpI$+VudJU<ac;g7N^!Q)IM*+sIFqk`DaKdg3TZsyE$H_vasQ^q?c}~WbpgE(9IH=p;tp`%F7*l%<LhzXQ2a^brTA+63mVUv@0N@4wfL(1dTj^yTPKYZzCO9+OEIqzU!VKx#Pi$5_<F)X>VLCNs2Jbz)$qwtVtgZEDEZ@uNO6pW;q?A7X_AyzOI*W!Wj+1AU)g*Uqq%QAofRhKb$s6={65G$o=^Ljm?n+iiLWLdqP(fQ*7JEBFQU9j-*Dd?(@lzFBwe8Q(G`=|iFwVWD>TmW9#VWI`A^E5eKTH+uO`2sIHTzIW1aYVawEE*Sep|?aqxL0xjFYu-(tGIJJx{eF!?R&zlFY!bK={{9m)4;DaTJ4O7~lFH)F*3ddhI_Tf6A{4kwP0GK%_-X(#11Qhd3u45#PPPJAVG3HR-<;^}$(@vSu9)aB%RSE0`n#|vnkQ`gYE%(ijTcv7Qj{G(Ef#Jpx|Ci#AMOfkNhnoZ*zg6Fh|ucRH|zP@R4f*4;(J4EA|;+i4GDf36vlJcr)M={P5g<^a??E=O3@02OVG17ja`_beL1!8|Q?KZ7*5&gba+2`@J`?Q|3y*G$)9N!$aV5_w6X%8t*Trho~b-a+qZ&u{@{pP$NdhUYXTXuXqYIL61Uo&gd=Y*gQSz>?3*VlH>mHXG{zO}bnsyKe#Y(&2Cb+#DC@wF9qa?11VRSh<m=j-0r>GQGk?;6ba>2uL|cT>!(rGLPEWylb@fBJCpKl4tP);WC?#Yqb)6#J_gvuQljf-}VaWq#tI0<pi55khfh<<av_=Xr9*8p^xAb-py7j5u27FD`Bn`&$`FG~dWa^qdCY&)ON86lZ~Jme}9U$fogxo!Bh)S2A;H-xt&O#ZG_6*Fux&`BPc{Ldv^*dQMq?FX>+uo*VE*weQ>%g|(NI2Fj#y!apfwCi~-P`TwMFN~iy;e^S`_olgJ1|D^Cs7e(3gZ`*~&ct0BBgU|!ugW#jkufa#bC!qfYGyN8P0{lH1<I~U|z^B0%pl84rz`sH-f|=UjU%}VW7~h6o1K$QefZhT>06&4=12cUHeggg*jqwX;Dfk7rVg=IYVAdE{g}PKAW?C6s6<h<2ac$^J;M(B&(3;@-;KtB8V5SYgjloUP7`K2n0=EFa27ML$8u%?}b1>6Z;J3i-(HOr6eI5KBxCitNa1U^A=-XhX?|^%Q`=BxI3+)K*3+@N)4DJUW0PPB9`T=+Vcn}(64`@%Y2iObR3+x5<glb@>-NByV!Dx&JLc4(ng8M_efct|#hIRro?EwB5{2w&NA3@uJKLURUeG~j4_<d+wFw@rH_rdR?F?NTlV0UmEs2jKqxFxg+nCZ*lmf&V+j9-D)1HS@p2(1Nf2(AmQ4rW>fTo>$$#<&`^0=OEu67(Mz;!0oz`V`Fc5tuc`&(IkE3H<~7C%6Q92V4Ta3%vnm`WyHz_$C_TE6~f}E8t7ebKpzhv(TTwOizK&f`3F~d=h#bd=h*NdKi2Rd<bfRneGK20vDq(-VNOW-VNRkEdp-`Z-EwonQjJe0q3DH&VgoubHE#*8Q=|I6PgNUng}+*$!Lt@q3gl%;23BWI0n29x)#iIHFzC342^LpbR{?x91L9s4h9?0#bBlZU<14Wjqw=haPS!LVCa9qgTWo4?}C}u0Cxm8Kx6zwA$_0_v&Q%`^gQ@7xEQ(%%rpaB4Bm*wI070DjsP!&27(uY{h$-Uy`djMCxSl&_kfNAGaU==0sa6w68r)9edsXo``}K{A>dBnx1j^UZ-ZZh_5r^JZUOBDZUKH3+8+EW_+@A-@XO#j(5B!z;OfwN;OgM2(3;??;EHIBUC<a;Mq~UEv?2H<a1&^2Fw^c}rf-0mz6EXqu8qdHGqf+5sTa62xIa_}Go1`(IvmW@8{8lK4jSW8(CJ{N0pL;KDbOG=(`8_$bHGgf!BfDVXpCn;L%~effoFjiL)U|urh=KS1~Xj&UJRau#yA+71!kHD4hF|Sw}Y8}1!kHKW||0&0nbBY91lGVW_lbP56*#}1~aw6Om~2pZUN_jm!dH)fL;MJy$LP=?}YvVX8ISH=@~H7ufaRP(P)e<=s#el6<mld@ORMaV5YBvnch)|nO+2c2Tn#~{4=z<3o+9cVAdF4hqebZeINWj4l84(w-jR57;i>n{2R2Z3o+9Vz^pNT1nmW8IuOjXA(&~YLd+WDZD@?|LHoN9GyNFM8skdvJi$yq1v7mE%(NP~5_q3Njqx++P%zU^z^pN@18)SF={PXc&S0jmfa`#dDbyHOf#(ZmItp9`+zdJq%ycH0X-_cI*5GE~lL|G)HQ{{*W;zL66Z|^VAIvlm%(OR{X<P8?;BOUbjO)Yu9L#hoxIWk&ItR>j5twNoFw=HmckoXNHO5Wg%>^@^0d4|*8~O#9X%Lv{M_{IJf!_xIs8C~E58iAr(<$J3;5N`%V5alIOg{uOeGS|Od`h9l*cIM%FjGIUE4USOGMMQ!Fw-7jrcJ@Ez$X-HjH|+%0A@NGTov3Hs)L!12Qz&S%(O1JG5Eg<HO7BKeZWkIfLUYw5<G7((_vtyZ-SXt2EPQ}uTW!rAL<2W+7HYc<EPL8V5Wn>OdEljK30fXV_byB_$pL$A!gbg%o^j{&~9L+UBFCTz)Wu_#H=ySMPvK}^c@#srY*s&F}?&<!A#x2Oz$ehOuq+T0;ixcJ_xPlLd>)xm^H>npf40+rq97l&w-il1s?%Np)oFmJ_IxU9b5?B3cUtq`YV{}9x&5Q;H_W-jd23>ESTvx-~@0I^eC9=Au!WSFw<CY5_m2e;}GbVV5a%t5b#Q9HkfG|m}wZ8=@Rft@Mma@KZnMFnMQ&?2hW7A0yA9>X8Hw~=``?6um>9BG0;U|rnA9gz@I{AfSFDOGxY&89RU6m+yRYoSLg&V(@(%%!S2wH!AyICnZ5~T`U=<`To;Y8E3^%mX(O;JxDvDmxDwd;!x)c(I9Gu-09OH5gEj**eH~m4TnpL}Tnk(ujd5eB25t;?gMI{N`X8_xxH+^RxH(uwW84xt2;36f7CIQrbSStjxE*u^xE=Ui=xFe};P;@u;P=4ne_!kd9S`*dGo23}4_*LW16}}Li^g~Z)C6w;AAs%#Gra&l0R9D90{#X3CmQ3IT}W%Y5VOX(6SM=EX<u+Bum^M`*aJKkjqyV0Jn%yBQs@#e)8*i$;1$pi@CxuMG{)i3HQ;b?Bs2odG#VTUj)lg7W5Ee%j8mXV;1qB=G!4u&6Pym-2+am>1aCrPoDa<f=YzLG3&BjcfwzKpLU)08g7={@{tCJu{1x~J^dOk&QScG)H_#K{Z@}N7G5#6)J@{wvdFW{{(+lA9;9sD>f`0*DMPvLs^g8%=@O|iQFw+O%`{2jWC*a56zy57r16?XKsQ7>SFINB8ANDL#k^aNg|NSTBuTjOH9QJRlvM*J=23BU*)PFCy75E$7IQA~0{12gr0$c'

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
