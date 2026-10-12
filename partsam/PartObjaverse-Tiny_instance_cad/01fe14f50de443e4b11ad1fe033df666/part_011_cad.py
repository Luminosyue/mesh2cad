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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_011.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_011.stl', 'source_sha256': '91cad4a1e09bf521ec2fec2e962a8ffa0f07589fa675896ef6a6c32874201dfe', 'input_faces': 1332, 'input_vertices': 1063, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4999985992908478, -0.3326432406902313, -0.3567521572113037], [0.5000011920928955, -0.08914774656295776, 0.3575245141983032]]}
GEOMETRY_BASE85 = 'c$}rZ3Ak0`8~4A@IVqJXN@+ZCniCbt*x_dml_o`;Ml-1lW!fZDqGXJ+4Ut(S(sW8mIgO`;N+%g2p@atNUC&vc`{}IjTL0_%U+<gizP_LJUH5+Wv)5YBu-1OI)3JR{xvHt~U;R{#t7f!q+%J`KaX_kS>X!b4hFsmZ|KJuk3>=!3I;7Nh|4heT)b+xSJ+e}_q;7B2um9k_gBqQb+vt=5Z5uVuZ8YG<K|==hzTt`+2leak{Ih#sH@JV`55B7R!2ZE@<Ce#^Y27@xb(7|~cjo@z{i_sIA$Ql_^|J#lDS!Sdr>P37zMNgw-!Jsj?`-(8T^T=>^<{BVer_uCEkFI+;p@ug7w#!sIlGLXPk#QZi&vJ-&);3JA}POMSLj=QLEk>5`}5x%I=3|MvmM1{{Z!W-Gs^mz;g^*91%KE5)M@6AsGooA^>fSmB^A3z$}egAd7_`&rOC>&zP+#Jn{WBKFJBa?Pww4C#YujCp9Yb9tEc9hZ~3Xbw$XadeX%&n&%dr?B;VIl^3AvW^lPo6^{@4Maiag(xsiNdf64bg`30vPQR<gm-fdp#dEq>!@<PAx<Ok=M>K{=*w@R3Ae&O^gk^I!h-zEC#CI_!9>svXRZ@%Rhyj>+y&%!BTzWS+QVSZ}i!J)spP4shJQ8{v63OhZL?62*=vaE0CMf1H+er9H+us!Wu8fg~=wJSyHlUw*xvcI@uc%7#!M$T`#=aa=re&PL>Me^<ZYQFiFpK7~*q@IOG{8^mj7YyDL`b%;`|FEhv%YH8JmyC>j-rSMd(Q=O8n&{{5Oohko=dAE}?tk#ivh`8l>SKQTrm-`U^3AvWl2=n<Ia`j3Tn~kd_Y{}CK65`=ndlcZs<X1JZ`Y^hn{WA<xuI{@XL?nbuYP`yFh93`=vzH=pZKFV$<ODwdB5Pl=y4W5SMt+iUrNk3-|`E-{kJ&jI#J(_bNad6#bvMO)c)%d{rnMC!{c+wu1Gol`uS*QSpU<0i@dM;_P*w)Po9#PZ@#}CDusS#)|uh?ZU0ZAZ~dG4`A_YN_~{2n&noq$9P=|$j`_J-PW|U+B$k68D+fPT&e#_|PAmsMRt~<ElOD1oJkD?b7&$NIr_Y`iJzs5iM2}DL_GJH{|02FW4wCPE&9~31`Q~fBeJ;&6pZs*oe<JOx@WIWAe(KfoVL$Nr-;vLiNrmOBpW5(W#JA6tmVEO|N+h4p70btu<@32>`S_M!uw{Fso+U^BndoOe*c0)so`sU{KbPiH&se^FF3qQ&v3&bn<fj*G3(w1nV<O{`_fKye8AsIj{S|(CRF%-DKUClPL+^jHYerJ}=4<&nPxkqr{*ml|I62v$@LKZw;>SMM=Fu|}KNo)NbG03oTt0rR{Q3i<^}KmoWZbm=(|q3#T)HjM|NqRte{aP1{ezUF{cS8?%dvh#%aQ&zmapYlf1>3`e;doEoZMx9B(_KOtv#Br?NR--=1Y52Kb9};QGLtLH2poXKUClPL-VyiRNwk5?@NEEek@=5L-j2`-RrmH{$G6S|MN#|NgVHDKI4n|I^M;6&6n{m=4-x;cQK#*!kSwW$9MB}e9yf9YvO!KeQUq!+kDA<oiC}Mk#cmt<b9bhsUIsx=1bm}`I7pva%8?#&}MVud{uqxKh4+qs`~!^>&agd=gH|me@>oni*NJof`d0D&*#PW^W^J)id_G8Kcc?fk9c41N7T=ie7zr0-`^+x{$pf(vHLIe{rwld-mj@|`RSt2*ZVc~?S3tP)Ay0%VE2^;6E}vw+|R1-uLpd+pH<(Vmz<5!^JT|Pd^>KbIU7P>@88Xr`}b7$b&1!B`hGre%Gy$2pI4}F&mYX!=N0N(e!=o@BG<Ejexg3lPt1?Cmq))2%a`XrF`wr-=IisHm~YREK3f&3kAKdPwK8&j`sZEZ`{!f$vFBsrTYkxg;>h)B&&Sla=VJxW7A4Np%-838nT|z~a_n=JRQn)ue(iZ<%;$Nd`TBe^=G*hkg>Oa9i#;z@-#;(K*XOJ1TYl!8r=s=bd9V8Ryw`kvKCHgwmuwsrsi%KlExv!gjURiyExv!gedQyOdfGT;zCLfyG#egyUq8O%>wQYWQ*A^4y~Wc@U-x9)<+Bs~%;Qy;Mf|rzKetZ(W$hCDl6uXSNBjXRrY4q;A1l9a=*P;(xAOCUXd3ndkGwszZ29V2`QCph^sRjLt^AUW6HC7@Ngwsm?6T#nZ{>SGH}tK1^?m)j>{%YR|Gy&n>c{fs_^Thwm*c6v<rh}j9s1M%ihN%6?eltHt{?Sd`Eos|@6Xp2!@}!j#GWro>zVb`(spJ1eEi(~)62{Hg>Pji=4bFNKlko|Vg3!n3QON-?(0jF{7j=;BKhfNe}(f&$v5BfGrPNmeqn>~`dzekX`+8?uW0@wEsILue_=Gg0KepxFh9ReyYPB^zC!8eO8u|=vLwIonX@AKsS3+VKUc{a(R}kWlAq2w^y8#_^DVz{bYA2-DV($>JdWb0j>s%4>!&~A`ag8xk|aN~ty58wpBnM?!o+g=_gRow&RLu1Me1XIgCTR1{E~tH%uezPkF7X8$uHPib83>GKD_DVNPVV}|IV$G68&Cn#wYptvv=K_<fp4Ya$mb7zvABUNq#10?WD;0vhq*AY;uyHu6^OuBtLc8$<vek%;KtriREt@IX6-t`nSTK<>n{(>0!4oNb>W?ZCjXFPK9fWlKg`67cWUHztMLQ-}>8h-B*_-`I(pBO7v4(zh9nMPU}rk|M5BD_4(qND<bFdG5lFO7Dw{UKcT~lB)_Ctr-+}vv2u8Sy=!%}{OdwLcf|M6a>nJ9`l*#g(c|`P=;t>7A)0Uf`TFX`vlIMSd&iHp_jeh;w7uiU+B<%%y<0ij-mM&M@8)ZJ$B(sl^R>O>r?tIX`P$y!Az#}&exbH^^R>O>r?kD}=W2Vm_to}p`P$y`3$(rCms~3C9Y5CI@nh|s`AMw3<Hy=NeyqLYXC`(iN-SUd0sL4$VDGE_fce@F*!yZffFJ7ztQ_qJ>~md{7e2>3bY5xuh|L4V_wzdQbsi|b<)=o?41Jl`sc-Wx@5{VSeLwFVRWnkK^#kf#KVZI&`|4XipuY73v2y4KV&%{e`1;7WufFvI>f5-lzK#3p+qm!RBjbL|ryo$?#(ni|+>iP61M1tj@9Qb!zWO%qt8e4J`qmG`%BLUj^^tL3ed`C*w|*d24((liYwxl0Y45(CGVZHy?OlCq@3C@d@7|Yj-`7XReV;GmyU&;L-TN}W`*LJ__r8qd>c`rzjN|@&WgJ&O)_!FikCmhCSH^K)9~sBhkF{SJ$JI}3`;~Fr*GI;2^$WHA$~dlmO53lD<FWVE_ABGK`UTp4WgJ&O)_!Fi_w|u+T>V)4m2q5s8^>eiYrB?lJodiYu4NooKh~~gyjI`F>yk(JE-gKda^J1K-FKU>_ucAeBwz2l)wlf2ilw2i&l%LW=M3iSa|V2U&XBrkLaDFMNz}LJ9_H(F67~IamG>SF-&daVn6J-y%-82U=Ie8wg3MvzahCa&`u@44`TCqwd_TXck_vsDUy1MMSLW;dN_@*tFBxByRDboYKHiu5tM8w4Rv1x~RDbpTe9wHTzxuxZ=QmlDSby<-{ms|<i|^~dr{bc-`it-DZ@$)FeE(efvndM_uOIRK^<%zXKjQoRzaCwXRDbn-eazSA_Tu~JsAuHQPpZHA{{F&zy}uCOU;igno1b|7i|?<0^Y!`{-#<5=`NiC%`m67sW1BDaSKnVh$Bvtuc>Rd)uOIXE`VrsqGnKlO`r5ylul<|(+P|5v{afLA`C-2F&+1!$Yrgi+>ihnA(?Ovx<4eqEeDS`FFXrp`QqpYwoYHL_PsR7+DSm7`6+a{SvGG)VKb~%%G$(RB4EQSi{y_YavCl3m>-+oD<EJc%<TL+IzjelnNdB16Prbf=am0T<oVTZ6{3?>4!q3e5peW+Yd|v%n{qbY<xB0o$-~9CGHsSl8*u5~RJ*sc*%lpzE)%WeUQN6;X_Ncz^AI#V9p~Uy?ab1(yiRV{*e|+#`=hyP}{93-AU-R|+S~+@t&DZlQeysj_e(inr{EBbqH=UX@E2%xIZ|%{1ZI9|_BwyR3`j(%1uy^Q7{}c1+f4ndKkNL6wXXx&59gp;%>RW$kzV@H$TYmnI;&45XevgSC`yLZN_B|%P_W!AC=TA>+kLvsJ+I(q`>c{fsdt~+feCCvMrzf>v_5FOte4WpT@8>gP@}`v@XZfC8eLudBJmjNNU%vNO-|}<&uAQ26eAJKS%kfd)&##(ZJT>X~sP8|o`Eq>JxBT21mrYJ8U;S9Vl&`*@zf~@plvKX@v3#BHiSOrEPtJR#^t@zNgzF{-t)AB|!Oz^*WkFd#cf_`Ey^Z9j@bk$pSUh`t;`J%Mzdp^^>r;GxzRE8ho_K!6kLBz672nsV$BXGm`SkzlTmNsqj$b}s#xI{Q<Cphk{PN|<_~m^WztoS_U&b&0zA}EP@8>6bC#2gY93S=l_=q1H-z{IqcgxrD-FzM2tsEWS&DZf={8;^Ue7E=2@m+j7KDi?|438WiYwzOw{=t0hAH?_btIVwNN#&~_%a`)i_t*c{d9RdyF6kfCxBkI=?H|n7{vmzy7n73eufBi2VZPK~{eAt(rIVA&S3i~?>wluYuh05UQxoeiek@<>FTU^3Ype}@oj-{0=MU!V{6Ty_|Ia_<qtf#r<F)$!dC}Q<(@It51M2(ndfPeE6R&^q{q=9YUjO3z>p6FR=<EHF`2POLe7!#sKb9}YQ+<E@8?KyLdcDj1(|nzOny>Ru^L752|Jv>_U*^y1`}r`w&Y#uy&nrIcJ*(80`G3r3{_lO6|C=9MN7rIbsUKTMC%#`thaX!<Cw@lqW9#U|_s<_%G@l*0KCS;3-}nFcvGL1%`99Q_Bj0<fZ{KfvU&lc!U&lf7<@-%vj;w3)`8sY|zK)yb%lDhU99h5Q^L3mRKX#mToVD_GoE6{CL(G@&xzvxH7x~^w{n&Yt@267P^$H``kIlEm_x-u~IzJcR&sVE<FD!eV`1>#M{r!&l`aD^Df4^4yjX6ozzxsAw%-8GR`??;$%F*xr#rNOun=jYDFJG>I@9X#bR*qc%K3}eXpD)+H_x1aID@U$>pReEhiyu4Aa{c@A<@#6Ou7B_A_q^iA&WnC;D}L;}$n~E&V|}Tw{ki(qpPR4!x%wH&*Zy36|NME+L8afH>-ZJ(8Na+Q<Cpn5eiatvhwJS0`M>ynJjIVa{}<o#3+i_X-&f`j=Ii{ye4Rg-ADcf^9yd4A-tGQZeBb|=ulLL1`}y-TU(7AruKo9M;``@U=Ii%&;`{k$)oSyT>aV_^Z=0|4ZSj5mYv<2TtiSla{^o1_#rN~=I-?gP)n9%8yxn|#-Y)*W`@1O%lIpL%pWm9V^I`G*c+s%(qNMt(@1HN3uixK^?>}!|lSN7OSKl8`^Y!~j@%{bCclQ+~)n9#oKVrV#kBINDx4$P8CDmVje?6P8-@l9R^EdBZl6d`#@9Sf}UjO3z>u1<uOB1gj@%{B<zFt4#`{Tdh;jn+w^(XkT^(XkT^(XkT?`I#F5aw(DEWYob@nik7`2KfBKQ9e^UH_xLt^YA!*Z<(hz8{&mHynTT`&se*_p|u1?`Or&NPg`5S@A7D_x760%3fEtUQvBpuV}umH&)-)E2?kn6=UVFUNKe<>lJ-{WWBNawq8+vTW_qstv6QR)*Ji!$a>?L&w54mZN0Jjw%$1AvtChsTW{>^DeH~ZxAn&A+j?X5ZM|ZweAX-a`p9}?^=-YP`nFy%Ru1bDW96{^(AP)S536tM481SwguO58f&Kf+dSLI%dSG9U%>UJowIf;g>&usQzv{=@k*xcTm80!Q*8TeW$hu$kW9>-R{i>hVb|mY5eSKuzulj}Bj%3}h`YCNkvhFwbzS@pt-LLuu+Ky!1ullieB<p^CePrFQ`muH->waV9XgiX1yuLoNURV8CJCggsf?+cw<AQ&FF20{{o3GE?#rOGpKaI3&Ki?ML&(F=*`MLOhetT!$^0M{x>+{9;>+|trzpoMBug@3Xug}+VY<<3#W9##+KKlC_@%{RI@%`^>#P`3i5#Rs5#_FTLuTkID=Zo)uUn9Q%eU19IK3{zQ`x>jK{=P<h|N9#8{qJkU_v`bud|RJy_0iwgi0{|ui|^OxYdN+KU(2!e_EsPLy^Q#NUA_7GyBPEJ_b>Lo`ui92_4hAUjy~@aKh}=)cP>`G{?0}GSUb|+xoA1sj`VjfRv-PHi}<m2q`z|!KdtRZf9GQL(cig<U#RU!f9E28O52hC&PCr>+mZgxMf?J7NBTP#@nh{sf9GQL(cig<A8SYYI~OfS+mZfm#p<KKPZ2-Xj%2(mY}_u~FZXNe+x?pPdcUTAM)LK3O?`iVSH64b>+?_b?fIwq`ur1L?@tRJ9vIe3?yuGN&olA${#t#1KYq=y@OAQhz<hl^V7@*dFkhb!l<e6R8OQhi9wF-Q`~AYMNPiW}*Y#B9%l~&peLtT$eNUv{_VW|*{d~rJozI9L%h&(UkNE!k>*W(m`*r>Q@Tl*<&oW=u1E}xoGqhRw|B;gakC6KQ_?R#26V&(5qlULFPC8%e`{!Ne>+>t|W97^FRX<j~t{)KJe}A|0@O7oW{2dDO_3u!4U;Yk-`TBP#(%Gq!uzg4Wj)wQ;?`W8>e@Dao$luZE82KwB8}}Zv=8w}-DHjz}RZ|0cm-!PT&UF7wlmEoX)yMt+`x7IrTetdu{1YQ@WTjG*f>=&CUW&d7FGeR5j^9RKg@*;vD~LPLOJJv+;5*>E(9ZB(a2o9j--}*OIPQUVg)8TzQssiEgr;DpyR$>C1Xo0N!7d!{kM4vk<b;|-INr-Xm*e=SAT|cE30)66{Tki`|BQYE{|x_vu7NkB-xH2Y&^7S$K|CGAbLf+>)3NY#@Hq5wcpUsJItG3QeTs1W1Ud$OB#4KD7==CvI~@U!f*(cihaZI>Lmz-gqaz8&51|jh=LYe=AkINghn=>A&w<ZIPlL~f&q7ay&qU849Ot8_!p8>DB8Zk~bJ%GUxFy^QZ3?%7Tcge3<IrOW$48^h-~)qex?&JV5svGlRbZ#pV5jxq`tZZ(gYd)fZ|JY^Z}8vfcKC025Be{>2QHr-YPsx?T{u1nJpeukJ{+wI9}b^_o&=u)_e1-@{osM<4e&sC2s#KJ0^f$-0^bIw(YxR@d>?u*d>@=aC%_r_74#+e75FXm4frkiJ@g&;J$MTGK0F03L}$T;@OE??yd7?s6KY;g$SxeWK%2uY;5O)Sa2xnE^c46s_-yn{_-yzh^aA)I_ziRt{03aUT&U&Bh3xbY*lAVRX$^RPv^H7;t`$V}ASw`!_d^eZogNH3&4KrWU(X5kwVaS$IKB{V4_^qMh5ipd3qBP+89o(09&HUD4<C&-gO7$Aphv+C;6JlN-I^V;3&*q3nec4*19UR{0sJodHvBI9Ci*)3Cj2t`BK$J^0y-Xk0UnOt0}qGqM(>30hHpi0hHr%jqc_2W;TzHG;Tz$;Xm7YLd@_0>d@@`OJq)e}ABa|l4}|wabKw2p|FS~eofWbR$A6)J!hgYA(9Q4`_#yNG_#rqKtqUKC9zZzWpKyE#;kYVV7ycu-ewGFCJGumRS_J<N|Au}6{|0YC7r|TLU(to|ukdE{b9giS3%UUQ1^yZR4E`D3gwBUI!9St%;Gf_h(NEzY;UCbs@DK3!=p6Wacq3W}Z-l=?XT#sY8_-$s2Dk*B375d@(HZc1_*-;3{4Kl={RCbIuSKW9YvDEM$M72X8}uXi8~AH<D*QG475X9k6}%dq0<VU@L_dJPgjb>O!>izx=wx^$T#UX47sD&icj4veQo`|K^j-LYAVvi7AUYg&+8=%peh3`^KLkIFUI{-8k3_G6N5YSwSHq9MqtI*MQShVaweX|xW9W78WAJG7dU!NE2E73u13!-52tN*wMF+xT;V00W;3wcG(LwN&@Kfku_$l~lbO`)3{0w?C{0#godJFt4JPy4T9tS^%-UdGhKaUQDpNGez!{G7o1oU=z0{jAc2mAt@LGOe!@QdhO@Qd(E=-u#3@XKf#ei?oRy$5~;o`~KHJG~En6}=z54_+CJ0q+G-jJ^XqeG@K*SD>%ME8u15Yw$972|5v80vDmLz(w#E=*#dI@FMgjcoDo1eGy&=e~xD0&*25=3-AK?Gjsy{89W~y56_3^q0htf;7`%#;7{SX=s0*TJO_Oio&y)6&%lN7Z1ib(HarV`3Z4beM4yCb!ZXk(;2H3AbSyj_{ses-{sf+ej)AAaAETq;kKvEd$Ka3PspzBdRQN-56#OAP1$_jb0)K#xgx^QsB^<wnj)boW;?f`r(C)C)HgEyl8$AK;4fjFY!hPVr=!tM&xF32F+z;-Lo(%Vg2cW0G1K=ysQ{gM&tI*TntKh5AcJS5kHE2G34SX$nI(#jB9eM_Q9eh3dKlpn12J}q$2KYwwEcixvAbK`D5WWdL2fhg&gq{lzf(N7L!Gqx;==tyv_-3>{d^3CtdI5Y3d@Fh(d@Fn#dJ%jZJQVE!4~1_>JHofaccK@=cfxn0UEsUnd(dvM)1L6X=w)b6_~0Na2T_M`Tnjx6c3K^FdIVexz8}30z90St-30#vZ$tlpx52y69q=wVJ3G`=cE~OqS3>uPE5V1NhroxzZP7MxTljMHGT7+=*y&ZU(`(=Y^g8q!_}U<@4&n;JaWC{r*lB;*>7{Tl_yqKL_yo8LdN5oCu83BEE5cdm-mH+b;GJ2a{sZrXx1ztpTj8J4pWvV25$JGu1Y8rX0oO(kA{<vD93M(JJ{+w9e;m|#Y7n0hj_0ADz)oktPUph&;2r4S@D8|XPN<D@LU!S}6?!b(3O)&K3!em^f#$<!z~`gq!so*mqaERk;djut;CJ8y%7t2~T*yujg`FM_JFN*Hgw{oC!gYc;B8USC$Cc4)u+u8A(~59q`0bof-^>Zwh2u_W2e=b_9(oRZ9(+354n7?|5j_Du5pIbd1Gj{mppD=r@ITq1{*@iF3&)?LbKv>tM}*@K3CGh2$J5a{@F79@<%2jF&4!)s$qxBo_#pH@*oET*(SP9sazfpYaGZs@9LK)~`a=*~&<(KDweS}BH*_8R8~i)^E&K=iBjNZv^jmmR5U&RD8affaJ&2(}+<^{*Cz3Z59ae@Xu|0`g<JZ`>a*ZdlJ&`gT9~E4O4T8u+8^Wn@Xeiz9)a`Se6@C?1`Y(qZ_b-pvy8TYwKFf96xrF0-Xal$&T#ol~WtJlx?}z5VPF-1!>j!!yWgN+S)T1o7zdTw2&Lz)zPAjDLaecO(mQU^DdTd*{<vA{PobveG?q7|dqDKaC33@TyGl=tpsEOvmHQ^)Bqu}a6)Xxsft4~=q*ynP3py$EegXqNTI`Nw7>^qP5KacnBNu4g{br<s*$6bTCFo<sGMR1oOE(oGC+8(YOMB^apppD>KK{N=WHrf!b4R=8=fV=Ttb<xIf9m?#AUI=%l4z<t*upR3fXw5RmtvcJ)@oJVic1NJqVLL`W(C%<Yj#n;vB<zlNJ+|xN9m#R+!2S;GtIumYvcDtyI&ps7G08(4!VNgz4beQfJ?FIndK7#CWwl4ogY8^)MLWZG&g!DI;SSWV9-0f=IjfD<g)ib9HAWl3cFyXcwcrLp!#O61@6m7JAA|TZh(>5jxDnhCJr>RjqD59%UJJ@<z&@Ar1G);{7{oeWw~p83v2PXczl!(%kve_L>%QeRjyDAHbr9d7-@qk7d=<ocbT!;8h~tB3iXI0y4x&{MP0-eG6SxHZ3jU7wYK9&UH>J!C=-2Ri>d+W%1>3Q1fHo>~-16AY!)sLL*fm7+U^_-Xpc~<}9IvC%V_<i@o3q^<?--8j8uqVYUkhHlmi=qlw~q7Uj!8?jHQb8x-5PBPujahALXU;NqO8^ED%j5D26R1a=d2mp1YSe^nxjX<cFvlh&ERi1N5`Yb!FJA?qK)A$!Qgj!PB=I^-34a{u`S?kIiVK7-Qce16>#SudgX-W^`gu!>~lF;<wD&G?+tV(uiMFMI<wE^WTV?)S0`7uz0`3h{GXdox_KP>H~eo9+k@DR{t5RCqF)d_(7tf@AbJOJ3EBs~1pXJ@4)5W;dZPW{9+deX`WL*LI&?>S!*;B@@HxAcIc}Xf-ktHfl{t1@`TU(>J4RXPUUGMEye>m8hu!hMl<iCLF6X%Z!~TER*NfNgVE+#G?d1Gy=UUj#F)HBmUBUJhczyWnTiL&reZ6_@Hui60-=Ag9<$vgI*v?r`^b+_V>USx68Eoh560|4$H|MAy+84HS)&uPhe;$l6E8Mu16Kc(zkdF-F&>$9Nhq^L5WEYMXqQ&rnAeLu`<t?Yo&)Mg4>gR-7B`4&1K^&12zRu}#%5eLt@cvb(!;#dfCa<f>YaQ1KqFNAj(Zk`|K~xQ*7J3-GBzTXnf>?~MhQA16RS-q!mv9m6%5z$kvg`6*t~{r%tR<A?%5?Q|T8%o^q7LqToUY<M?O3~GbtK2zj@tr`_X4~{+53*2+h334w=jF(F{+Q&gKKcSmT_*~d0ECeTFQA^inoGuQJwSQbSb$tDeDNdI(#U{cO}Q>ORkGmocAx$mGEJl*Hv5##pG6{ti#YMu${{~Xf4>z*%Gt}u1@`2y=(BfmuBxfXD+WU=dFlySB>*mjdS)@_P%rG-lrDl&2inJJF4UEhtOQOzPtZPh5PHV&#_x}dkXtcVV~n=K`dea681UX62xZqZ)Tt4Z9!~h|5o-n{w;`K+5ap194`-IDf^eQ&#_xed@B1-W#4i>LoWMs+2{DMl=~A7!7)JHb|thjTnRn|Jrq6!u7TEsYrsdN$G}I!>(LGHdU!kfH@qGG7u^H@3zy3Zb-%2TT{!*^Z*MAO7moiz|AGI4OVID&61W9=EZhP<0<8txv2%P`5IuqzfV%BV&`aS<;O=NoxI5ez?GN{buSai$uZM3&Z-sA$$DmKZW8mk|@$hr-%jiV-W%zCMUHENy8ae}>27iLigg=3&qqE@Y@H^;x@H_A;=&SH6@bl;d_<49N`V>4Cz6HGvz6HJk9SGk5_d^H3b}k)v3!-xneNeZ3G1?Wr81962fjhxhpuOQM;H%MV;j7`B(82Ic@JRGgcqIHZ`Yil3`~vzS`~v(s`X>B3`~f-@{s5kWegsc}KSV!<KZM^v--6$OGw4fj27U$|2R{RkLPx`+;6dmRco2LIdL4WXT!8k0?OZx`{o=!^u-{w?|4KOCN;uw3I9@_HK80{xk8oUvaGZ;t3cLQ{$yC@MTnhIj9QP+2-$*#Vm2mt7;dngZcp~BWUBdAU!tqSP@hrmedxYax3C9x%$4?QCZzCKJBpeSwFN0m5=K8P4(VJnXV_>Jx!A@U>oxTk_od!Go1a>+dcKQzN^cC3Y^RUygu+v*$r#HY(`@wxt>$e?S-|n~v+7EW^%eB47V5e^qj;9iiKO!7|OgMgvaQqVCcpTw)G&%&n4t|XHe-w5)7<PIs?6f!Rv<vLCE9|rzd>z^c?Uvftt{zG4Yj=*VZ92C0>)6`3;|$^0`U=O^pE$NY$FcQGj;-%<Z2g;K>jNEIKk3-|QpeWcI<`L9vGv=It#5bS87+Vh4&uNds-tduf3zaJKYRds5PSe!6+IlT3O7U>!wumd(M|A=@D6kryaRR*>78b0h3vv{d9(st9?n8@;4FA&D%9PnkX<<b3H=%V32uZofg8cq(CV-qJI5yn(IANb5ssUqwPB}u@EJig<8>#)4bY?Dqj-(uD}y+n*PQ`3L-XN$UgP++Am;J9E8+9e74QmP<M{I+HuAdH;Cblp@bA3F@yZ~6;dP(G8__@EKY5Mgg+YAJ>sG?Qpnt%B@EXUHf|$?i7Q)}7#c(mNaeP$}?RniKcs_bMd^)e0&pB$&>#l;^qj_*1uW@{N5FLZK06h<O+N%s-#C9+E9`tVb9(XcZ2s{0>3@>2Y>HB4PF5B<J_oDZ~_rjN>9m~}H9O~$_4SXJa5qcJU7WFf}lkGdHpYa!L7s3nBZ{P*+Ty!zKnEDyt&-VS))%YB?PojS3z^&MB1D}Pqh1*g;<J;N3o%$Jn$@Z7j&-h!mzkwH{U%_8dKjR14evmpEpTzcY)bAv?Dcen{pK)up+rqb_L*b#+&v*^nYp9>`4{ZNH{fyVLy_WhJKg9M!)Y14jwojyf$H6VxZb|)&Phk55>SsKR?V<1*bQQdc`WdfddmZ&NUd{Gu>Sz1_+YeAj;}gr&`E2Uw^mw=>d;)qVd?xiXzJu*MsGsp7wpYRH(68Zj@M^ROUJXBhj(|r{SL3tG)V%|Bbb2m)JbWg4A$%eAGro)MyQrV>Y_=D{U!$MFU&BS{9C!}(Gak<NaO!H@f$htwUkCUCwlAQ5#=Y3S5WWk&2fhoQjZTIqQ$OQR+5VLJ8Nbi=9C$c-FFYLXfL;!}c~LqQ&Vwq#2N8}BCmc5>9B(2VySYrq_F36gbN2mMzQ$EE+BOa*-7XGD?fd6`;~mWA`wtp&HNT$MS4MwkU-p#)g0lRN?mM>M&#iw*We5Mc$>SJzH<J24#VaB}'

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
