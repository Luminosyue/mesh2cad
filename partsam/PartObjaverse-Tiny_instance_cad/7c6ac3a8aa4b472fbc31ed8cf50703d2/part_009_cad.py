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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_009.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_009.stl', 'source_sha256': 'b6e3a5504530a446de147d4b0100ea4752314163378d858126cc6ab93e55f89d', 'input_faces': 1272, 'input_vertices': 766, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3395250737667084, 0.21519500017166138, -0.29832151532173157], [-0.31074997782707214, 0.32659876346588135, 0.2741560637950897]]}
GEOMETRY_BASE85 = 'c$}r2b$An77q2J5T@H58;O=s8!a2AWhl2%ocMtCF9*Pz(ZGpBFQZM!5euBHZ->$4*I(zl`{<zP*e9wB`m*2O~o}EcDvuDo)x0WeV=Fs?0Va+plczw5KnnsmT%b`siFn0Wqegno;7&&^1LCfmQ>5q$R+jMH}*3F<z)TWi}KVV$Hu_bGpO4c1%vt&6_$$_KBjvw1+WbaX9`wyVJNuS~41|;U=2KN~~Ao1^|{;E-<oT+N*a;6!k|HnV+6Ng|4_q%*9k=8PqFE&V|dCt^WqA54$rY7w#(BG}0heFicnzyerx7%lhs=2xCIBq|yPnc-`V7@bVH0l<v=8n>vxxGi*2sPJkUFY^aPDhFUJO6U#<_FtiME)wDbNtqXqH$_&uUe7wX_@0izQ3L`cT5<;`5<2&XQ3lJo^0*TtGPKekjGPSP^6mM^R;sJqwNfL_TxBt+L>E=`SJL?a$h{B<mO%-o$YNezdPI8Qgg1IdF33pqsCyLb4qSsla~AS+3cm}*2rSc+&U!SxX5RQBsjNg8|0_<Z@>D$nQL+90>pNI|8nMz=4QKSpEEb_=M=L8)!bUHBJYPAenBFy(wN&Xy%8+>aqH=Py_TNUoZGQ<KE?0*F@NX#YR~=p!Z{_^dcWnolTqZ>r@5n@ulGss1kpZk2hQj0h*xvdvt`cQaWgnh&FxhVIdfCPx3Ow&&Yqv&uNQ-()!bombLO_+oukBd+s<|7jwgj8#W;V?=Jzp2HGi?)6q}s6&Hsb1np+<2<Nfbj{*-h3`%ZE{v;T9B)3(<m=A4?By5rog_0r4;HP@yVaDHzcR!5k~8#Q$1+OIdEYHp7m<jifK-h`;RIh8Nxzb^)<xn;vgXKsB}FHp@*uUa@?mt}XJv!b7{HqOtdWpYLjHMjK|&Y#<mH}0Z+#0qC_Ub14NXus2g`-wlWNQ{4Bm^0V3CiO&q|1GzFw{^9;Keg!0&i!m|wtBnB|0(6nts6e?7W?0$fit&{iaj9m-yOLhul7gO+`M-PfA8MM9T)w#oXPDoygi}jHuD<(KI|~~IJti|x8L`Zk3V_3@^SdHmHVI5h`)DfyhGGnOVf$JcO^H5s<~;~AZKn`wmeMDt#_w7bIaJp;i8|CD>(miQG{r})}N2_W=EtL&yhRMT)TfFTFo7mU-Nc<FNqQT;QXSkDG?{~9r^kA9ClacearCqC}YcbHMj4n!pH4@XNlZVe-*bcQeN(#V(#4Dnu+&MQ;gp$Wh}S9={(LP<@;On=fCZX1U0v>w{rV?&1F7)H@{!0wwxFJZ>+<wEAJ^jes7q?uWNKDe_z_#oyU1suHAU-%<Wmfd8xU5d=~y*EGp}%=BE7~eB4M=)>rLcb34zUs}EDpsJUs<ef}JttaMJz?YF-<b6b@Qb}`Nm*`2S;=8--~<Sk0^=dg33V6ok}n*6?3`zCVxm_Gcz*Sj4k@|simyzr?2pD!NG<o#C4<~;t}{DYnEiz|0byyVOsd2c4Dx!v&HnOh3h6}h=e4L&cFo*6IN?;6R+)eKAG)ZEr$1)ncg`^SoYHV5(Nd-9YRHP_1g=KgIBqSf4*rwX4hs#lE?`9lkTANr(>RCCktcs@RlYZEB8+pn1O^Ps(JbykdjY<JEdj_?=bnKFhySDC8$iGD`c;?JKs%Rw=ouATWfye8cq(f;WgZr}3Pa*-E4#>d;zr-q7r#tmm~H{Dn!-bbHLoOdp}Ma{M8S@?6ip@O@bTdI`c&*6&?`_$aJs1DCtO7%M=`mf-|pXW|nj;Xo5Xn*csd*mtF|2di4uYT?&+Gk$IdC4><o%^o_##t!9`F?3`Bc112S8mSw-I<&3TnSTi>y3hZ+?f76RL$)v8}V^t!|M>yzRr3+zW;qINX@mN$-Lic8n-y}KWcOPy5IQw^1HF~xb4c#_cC8{_EV}wgqmA76?f+5Pkqm;x%Rs*=gpTziuPB!ICI;Bi&3JzVFveq;9!iJ+aIpre)cVPz79*jT0EZmJP+5}{ESm`ds=Tk4!67=tmclFq1-;hxeztivR`)QuIr1WewsYu+`mJZ*lzQ!Jf8KH#dfs@$9Vila>R?=D}dWK9V>GC#3*NO86C~%7q6Opd<d$;?_<65e7-<#pR|x)f7#m!YHkVh=k_D(h}?GSE5Gkur^Ji)&1&%cu*BpzHP=pb<@3VQy|HR;p0$wM-<%(#=GGNwdH$KFShVN|=NHSHLQ!J;DKheP$j{H`ML#|5Jpakv&Rw*}b%eP>qYYyGH|O%_^U0b(b-!8LZ|C!J!wW%bZuY(C+|SxMEkU$Dbc;WS6>9PK*of_h@8Ii#SL>Yn-<6wACOC8JtP=@pZqHbrk5`L3MX0%!3-i+Ir^3|Sa>&BR!xQ15qW^Xi`1{x*EJXBk#Kw6Ck03QSrw-(NcGf^Ko}ia}Ts<EUAo|IWk&ka*<NZYYf`4+peSxo<JDxY?^ZVMT-lCt`|MKy(T^=uy51GXMENpmO&8^-x?x)3|10v62;PZQyU-LyjT?_Gi?^fDY;(Zz4n$P<kf2>h+bHFg37ae%CL$qJFfaeuW-1msQ`%d2Ou9+Tcu4O-o>wV)<kq?gI?Jg<eDe{qbxgS$~FOi3Q;_-ay?4#zU$c%hkS~=sCXg{tTAD2dK@Ds0VdTahX=eQUk+ItUi=B6X9cpkOv=_Tj>oU_#V`82Os%b#21=E{M*u2IM{LCv*eS@`;{><`i28qtog?^;L6e(vmW=Jus`L_hX&7deluEBh~)jgKdTr^So*M_cpp;qlZsvE4kQdA@PPBUZG3xP$xou{cJwUw6rwTep;sR&&R!AKcH{(ot$|>zs?f7lqSAs=4KNb)NSg=^r8bPuqp_uOVULb+sAF-|LB&L&Z4X&*blQ=1U=BJZ%qhKc{?xM1CNW^N0BZ#eN>}ne+II0iykpocz73|G-a-Gq8v=x8B?AE5=j5Js&^2eD)UOzr^zv)0I+QqJ4(hoG)p0T=bvj5cd-|>3|sL@ksu@7aZg++Lw9F<E$}YgJ|D317G(QH7^ja>tJdAzL#p&T>U)T!@KbJsLi7_YHqeq<nQU8n>*Cp_IQ>2zPrYA)PujLg{F9@xt23fe&1dBuq*QW?#ct7bAH$CCB_qO;Onnb-F(D$w`Sw-@6lgzqJ2zm&a=%uCHkNE7k{r`Z}k)HXLaRyNavdYqJ5h2eB5Z=QXB`&6;|-NU&&R0BHz28b8B3X80Vn??q}$gV3Dti<Kq?90g~Pq?>pR2o3ROEJOlpY{jhUdsK{Hq<=30PQ<&)Ibt*ppnp%X5?XJ&@d1IRh(Y|G6K95fxd|tHg+noDZx-L?D9<KN0`PIPdQKFv?3pszhKSs1)w28Mne}1gkZ`=0rcE^_&@1tY2uQRu9%N{TKPZh!KH;xgxW6BjV-*e@rGk3)NB<XeidL-v3xwdlui+1tr*|DCF&&ah+*Z6w2qE~{NTkjj9`TLSv<l6h1&fH$9cf6XLjidRxwMWM|HFsUNTKg}JRdYvYKkg^@<QO$KrTfm;xt|L~i}6e-#n(HYMWV!b0^9NX;W|FM^4f=-x&7mu2$4rU=6)7_3R81?we)<QyFaVQwcZu^JasousCd2AXYqRDs;t3c{CiLF{JHqbK+(Q#dOq)Ly?a)?u9gk?^N}U(8L?f=t1UHS{X~1rpOemCu6)WPUZ3(VFZPc)TM9le%y{Z4_W#z>JP!<ca!B-ZxGbNKUJn=h&3>^l=eyGF6S+?-z7Dw=CH9-?dvBiKez_s`o2A}h9#6jtJH+SY%{cC7)%6fD9`D&a|L;3ut?0k*b{@~r%vLd;Ry+B7Qqw<3?9a}2-frr`;(aka;rk-i&i~C3-<MJMx&58z>(tzuo#)B6?6(5M_-p*&_OA1bYrEYu@Okj}Bk?{u>SpKj;O?S(#CF$|<m;Mi(+-I3Vx7UNZ9lB$ju~yapAJ2ai|t~*opio-eIA1Qa(hST6Jon*C-Qbr^!FC|>520E?#kcr`mp(Y|5IX|n71dL_g(M%Q%^p>KVRi1+FPP{yZuWAi1CNt<8iKBdQP;T@s;;Oz!$rkn=fYO`M}dOL82dA7no8xMDB<x&*%4PyMx8+#r1-@YnruUyCa5k|0mMy6#X||$n%q^6Y_n`VB>kn{&gN=oI!lOV1JtDsK_Itx&JnmJVjpc9_M@8c!_-cXC9|te;+ls-D<<<<!!IT{xtU=%IDwL9eKYE+`{dXtsA)V<m(2mJo&moQa{Po4U*a?TQ_j!$=3~BdGd9Gr2f+#<@x!K-X}%-aq)cowC?v7`R??5d`pozQq8R+^YG_$_cmWOcU`xd^L!KixYilW`FgmE{o}e{S-I^7k)Px1Q&XNC3&iV9Ym(QeuKiQ7Hh&IB_X$yRYmQd@`FZaaDsqor{Q1H9Qc{ll7xo-0PN{kF^{%AtUM$b^v=bhF;`6X{9``e3Q=ppLjXSuX;HyC*$GVv<qa#?&ldqd4jpu4K&zCC4#fyB%C1>uKl_Ej(-~BevmtOPn&vtS%=k>?%ek)-KS98~Wd~>cD5h6ddgZF<H|MP0@n$J6y&5TlWbFFyZ|HYa_i++0k$NRslAx6zDW3TXja9<EA+IM-v>rRC%VPd;jx3r}_Ec!{lZkg22(4CxHyTyrquzqOinKNFDzu#GBZtpUl^VDeH`UlUegFA$ae0Mfphiug?Le0(HO7V7Yjz6#F_Hzw*{`uM#Df;=V8^2#e9`O1>)sCD$b$9+<8y>>zldgQ~f1F40eG^x1FP@&~hgctQ<&H}Ycz(EeR=k>98cmMo{+Gt7x%uTrXKs0SCRXGvQ}Db|YZxuYbGj0*BVVf<CGy+e{66`viV*$8zT-UYk1)}GQ!bt#HpwD#dy#sa@5~yi=BBU9IA8KDNX@N%Ch`2_@1oB2cGKJryj|S)G56aQqvl%w?tCAoRDnp5FFech*kKFe)!be>g0EZhjSLid?(cj&U%oO<Y`1WJK91l%RPx+nn0Hp>Z#(gPwbDj^(SMf_eEjd!-cO9P*IYi%7pfht=2nlx+`eZ0D3K?-UzxPs+E2M3x6fXpeF#5iqm7>tA;yFIn6`A4Jw+Z<k=yUQ9;W8DV>S5r6>B~y#{b7Z-2VH+P&Icn?a1e&0+sfN@nF5kUgds>*lzzh+<&)oK_b7l%9&ewn^%ZDz@7UUSVX>$_9Hx=7FmXgaYn{EbJu!NQeNOXw=b7^c>{HvnD^SJUJ>t?z2ir2->cOYwY|B-H_ov>oYX!aKj&aA*uq`3pHrOAryq0f7x{ZU{}6Z6TkXemtv2V?Rvr@L#5~!)JiU0|UGrr7{itK2e|s11r(uQTVw|{7XIo@Ap|*FeS6jAZ^cMLUUI%lWEObEhgZp<{<x(fbI5AJwX1?DgUKj40+oNjws_pF+LOFlYW4(C4a6jGQIrfZbKkzR1zvRz(qJP|Hx1T6}PPE5;c1yNcyLes4ese$5pY|5}tr6dUw}+<)60a-S{dfI+=lQnzc$0OaJ?1%%g%xa~eVu`LPGiJg(cU<V`{~)~pctp`dYrGH9Tj<&L)`xPCQs3Se>;zV-Z?Lk`(5Vw{J+<HL_b)^b4*BiTC^XMf!D9r7xx$KUF-96CY%-RzcuCaZ_%w{Kf9houx`H-DEdh_$>-mg;ru>dXwUmU+4CW;+>xd&ALoDb^C7NW`!riTAL7bg&qry6H^->CIoAz7&g1zpS8hL2jra4bN5Nt|7yjY*Yr)YFHMe)}$osS3;!rhD{#;E`p6t1rq<)e;SCh2e<j=9Va@YEsYkkbs|D7Y4FY)t!jw0xP_A7pWt*c_xJo)oZuG~~7E5E-p+Qg~3b<q@FkM&F+tmes||4Hf}&;Mw5Glz=tjGVypsFkZk|7Pz+JWsCOBwo!e*EaI&s=k-cV`JON@6o{pVQQ}Zyv?s`P;j)Go4<JS_^)3LRdY)TzW;9iJ8i6J-+eIW=Er=!805z1N7H29pV=0LtGPMXGX6aL+8m+g*8J}LeSCTHyqa6?`|<kx)8CPzpWDGauReJqOyoVP^8T4!m!FHt&bi~lRXk^VFkH=D>&BLd@4OD&r!DWd$uGElaqkE<cT`Bh?I&E|_2hB+xqa)+JpZg4%Fpct=i~Oto+C}li~Qz!Z|W2xx5k#{d2h2m32JVi(VO#oJLA>dyx|njZ+E?mRddsaBI0?`r0wE)QHQZ_l<0r{C4O$C;o%51cip$r+UDLZ+7DXJ^MN(ToX<mA{=j(tzQ>=ZRS7X_u8o+^>#?gFM5?)IQg+-o%o48V4s#7YjtwmsCi*Yei$8zv`9ekiZ-(*lt?b!&HMg1e^E~$Xw>UMo_dO=&+eta*!{&;`Wc&BedArvK1d8p3SK|5Ymvzx<?poKiPV9MB<k|n_<L%pZQ6kSbjn{7rTl__SZ!Nb^`G=p_KW`(s|JK(c#CY(Ww(av!ACX^3#q+%`mBfBddVc%E1~1WmP#$M)eOF8De`{WTuG=;|;<)IiM>+22e0A}@*i!NOup?b_57Ce7`L0nJgT?!6n8=^E?!&}>wq@e^t?6SIu|Lf#_d9dTQ*E)>KYP#d>+RWI>`(Kg5bpoq6lO6VUp!Cq>xZwJTjsvu{KuKq4b*<F@ch<VzNy&HW`BNO!ZLKU*q^R>uhuzWyV{TK9zR#66)w0(&0Wv^ntQGm``OgIKKK9Y_W?1UJ9yq~VB`TYp0@lvusvw;5z+t0!Q4LJ{c$ySTp7jdy(Jg9i}7!n!SmtuxxK{r@tm-=bSWRv|E{&-es0qK#Pj6ZymqJ5_V!Z8cs%K!%opzqelK9XH_A`+9~jO3T)f;~^y6BW%N!7(=GO8&zctO-wN~_l-xpY(*0+m(@cRNw;i-Wl59QqY{Mt^@f3n{lB)wlREAx46Ox?YrpA;=Pzfj?z7*Bc&=i6eBiahaz<LrOPT2GOmT*B=e2Z{H^^}LGx=56u5SUtUYKKwb|Y4Q0vc#-pNRsBVt;sd|lW-HE$?Jmv2^RfMh<bG>ciqD&K-tauOUtWISll|Vrm7Cug`1ousc|pzXg{tsz*f=*q&0Wv=JGT9d5&gK<jm;AxML+oci@9w?ygDB3Xb0E2sK~9h9=!e;P(4A-O>q->UJ<&K=Zz=+<n3l_$ouDEXt0{QewSowv@b-oAKHiWp5sE*Jo)c{lJaD~19Iio76W<S)uo^qkNwsN9_QZncs>p7PdDKC(kWB0$j^4-ym`|QHMi{^#QW`h*-$k%6{x}U>Yd?nq95E(cZ}^DFLFG$X^#ow^G5qTJWj0N+NXC8Q}d+xcB)-5YM%V}UrFtM7vTMNre&PyKYSwRg+KB0neMqcFFKdkf%~-&S99B?+&uocTCr+wO;?&<@5+39etwsWw~OC@S;KBbsk!yXLf-DVi(#U@{|8<lel>*GFB>Aqb*tlfmk2et_d3Y)-kQVCiyYUjmZ7V7zPdUm_w)Bw-frXAa5c9-KE`?0TM=sRTA#NT{&`-_&3kU~I4_mt_3*Eso!?j6sO)^-yyF3$-y(NCPj2zO%)eJ^&bd9I8qZ6;?_E%H^Mi?4kNudS=9V|^Jb#|wLFCq**LdDLa&^4u|H=;DZvWQNYVNof$<L?#Xc;BicQ3}rjj-o&qW=ZW`M!Uh4G|(Y9_7zjwS}U8^U-U3yehv?^zXQ{kLSaC=eUa;&udxC3pS{^mZ=q=r*J<pX`C@_I4@I6w0GTawT`LA>l>Rt@i^-?<nM_+Gapxx+l%$$`Fu047&W&Zo5$^!7rY?y>0UfP&oVVZ^t1FC=QVxe)m&Tokv|VF%0#NUc|c>{pBZw-sk!6oBF^#LMN&WRhj||UPfD3Dzr@G?X@*dd7c0r@z{dZA#5nPMp!O^(Ld{J+{dj#izEPl>+qC8UeePI1T#U2K3C@pK7UQvu@Z-FHzO!PxKG%3WVP(WPE%iP)bMx{%{$l^kNzLb*(NVr)Jb2E~GTaa>#`CHwf3Er!^%4EF<>wEzt`_mST+eA}ecF17@!<Jk+vuie|5t9kW<4(QwKKS%JPpM7EgKebZt*@K-k1GLxS!Kc#p|;FahltE)DYvhHapMl_w^OyG{-;S^GDvrVmwysL(Xf=Ss?PkM*hCUKW-|%7sE2~{PWIHF;07mvV2}Njdd6K_zFD##C`vy*M;XEwS<U0YVP_yo%QS9`Qm+iHl61UM-F<3@zh(${gkWGQREx;^Eh)f_f&Ixb1$B^FAWmoG1ooA`O#5cVx0Hlx&ODXcK**i#atiJ|H6kn{%szoMEh>fIDgl0ugFIm`Fz)*+Ced%_!N9TJrn6C+E2_Q=CMinl%ja<I`3IA9@qM?Yn|4$Ki%r{dGO>2yU54<&GV?#p<+Ln2X)4F9X|gnw`MsKD8`d%n3xYI9XBeB;@5TlWsn$WswHBcob*28c~SGCrQ&sI3qtsO-SnUszt)=9-yDH2`9AxTkKE6gF?^i7{+icgUAbRMKF&-Z6shLstn2xFU7Vk5aOJN1_2%_%GH+Ib?>q0|&!eLz`VXGX`*YmqU^TaQo5|~e+ZV>Gxg%y7&y!2s7r8kkC(oB^<Q4s!I~U;X&TE7FDjzuivWEA=yPF{*AHIv<_m=xY)m-cFp7-;H{K2Aqw{$$7MU6y1+KRk9&q-Ta^y7Fqis#ks`8l|x_HJo-eeXvAACIrS=l$UNT~Cj5acZvJ`ojJ1>dD9TQk>h&p1ePw&J9y@^NG^DUCaAWk*DSPx$XVM7&W&qYs=e>=lMud`#!z#e1(<g;gjC+`}ixI`+v#TPp;ft^*Xmdl7riazvXcj59a+jYG$~aCp|aflPOxw9W`q6=W0h>nCR!h9^UTo{=EK|n{#{C=i>LLmO*cLzu|dlTi5v!YVLY2+I%A-Qq5i0ah76{;UW*T@aJ>o71571H_!j=J3ou<x<0q&4n_ER*oV(}yDy&eJm*d<Kc|G;^<1cB?$=l~cYRN7BSuE6xfZa6-=~2iqeMT)O?-YSS;0B4vsHg4=GCs>Q@C<#;SRh`+clHO?d50j=VR%R1T}X(pJ2_gFJ8@E>!_A?mtxf1(laxE4(|IzsCm-w<&S0!S99~}k$n8YdTi2m|5?xNXXg$T`JWHD|Hp5FM1DCdugk4#A1Gc|d~N<7dQ><o_JiyGc(&61qMzaYc>ZwWqOTYyey49OR>DWL|H;pV+V6Gr677rmah`kTagq1F%lXaS2SncV7x%w&xVzYIxF2o$?LS{^H)|KMPL-77ezDEEVXc}w-f!pg``uGJ)!goPlKX#V+N<W~!m-?c%RdgPdD8ExvmZDr`WgP2+drJ+spi(~8TotK;INk%r|bF2oS{CVee0_H{T=n{l<5DV8~4*TyT6)S?(q54I&<h*(H`ehlX0V6ye=I7&C_oLiuM;y^Z69N%eKsa%Htdo%GV3I-1z<ia@X$;tXU@TI^X3dyniai^6|=+M&z#NxLnVhnTm7n`aPFDuxyB$TVLGd@w;aWRde%jJ0E8T9pdxCgvZ?ezzNrS1)n!V9&v7Y#^=G!H~2i2gL89P{BE)FAF*m~{k?|!`RAR;wM%?I(R?R_znA?Va$fx#zh75R^7+X7fjE9@^PBQ<J_T~z*LM6k#^;3&_qiXew`lu)BShY*Dvz_v_46X{-kjSHOBL0?P5f&_>4(m3XsVkyl*CG><<JK9QT{0+3h9rF|NEaJ8dB~5>YpO2T;;DS|9}4$QTi}L;!8=aQ1D-PC_Du01`mP9f?eUU@XKHq_+|JdurvG;{36&Aei42FYyrOjj{%#*W8eW`1$Y4b3|Jn12JR1*gZsnxgJt3S;rqZc@O|(-U}^Xs_-?Qid^da-SOUHaz7s44-wEFi7KLwzZv_j(x5Br8CioWkCa@5E6MO?$5WWGv4$Kc<2VV>3g|CIL2LFVwhOY#3!B@hUgE`^L;Y-0k;7j2Xz^w2I@I_!|_#*fMFcW+Md>+^kJ`X+zG{fh>XM^eCv*9zrbnuz*8DLuY4ES^~4SYI$3YZ!`1wI~31s@L|2d0FNgO3GMz{kSJfJXQj_-N1o9}S-bYVb+$QQ&WleH45o_zO-&J`wy0ry?H#{(w`F4+p=)smO<c-{4f_L&2|bD)J$Tyq#Es6U$%YBL4yofe%6ZFDP<f&=2kl-v(}n6T8E=!Cl)T&kOc|=Y{73d&2X<^Mk$M`QZh?-tYqOf}jOn5MBuE11|(G0rrKLfSbU6a1*>R*dJaPUId&7F9I(KPJ)+&mjWllOTkNnQ{biHWx%QMGVrqC0C-t=IdCAn9K1X@2womu6dVjM3NHq>g%^Wo1>N9T;n~1;@NDqx;1GCrcm;4MyaK!;I1OGAUI`oquLQ3Q4u@BUR{=-BtH7&*BjHuy)xc5kYVhjdXn1va4R8#+2K+B@Ec`EcO>i8%CcG9n9$pJx8=L^I4KEJ1hZl$c0d|1@0nY(;gy(?g1UtcV!gGP0;kn?s!7lLJ@H}8wcpkU`tP3~5jbJ^v5uO694^IJ42{wSIgr@?{@Ko>&U~6~=ct)@xJR>|c_%}Q?JPr5{JPlj}>uCBP^0Z(hcv^TmurWLxJU!S1o*teFYzof=&jPlAXMz8TB7XwTg%kgS6I&bDiGgq`@`^^L9Zp4F0Xzq%A}<e~g;SAN2gBf0<ki4XI2CzAFa%CTZU$rFROAi7%Wx|4Cg3GF6?seWBAkl61$Y5YMcy2Yfm4zH0|vmU$m@e=;8f&QL4P<Ec@=O!oQk|MxDQT6o*&!;ry|b_?uJv5{|WAbQ<3KecfzU2bAsF9ROEkvTj5mX*}yGuD)Ox0CO8#&W^e<XiaZmz4o*d$0bC2GB2NddhEtKJ1y{nU$WwvK;Z)=)z@>01asxO4PDTC**&_HO_(O03{2}}&I1m04{vDhH{|^5O&W3-5e+Fm5Kf^zQGvFWLAHeDG5Ab*36!<&%8*n`Q4g3{24*m-M92^UO4u1xYfj@&k1xLf5!XJQ>;1A$Wz)|og@cZCM_<i_2a3cI3{4qEJ{uq8291gz=zXcA1--0{9p>PNMKX3^AKlmMRFr0WB{x<Qm<ds+-K!5lL_!rO){{sI82ExC=zk@;W@9-aBF#HGnCwK<_6aE!E1^){F2%d(2gnt5$!#}}4gP!ou@b};`_<Q)f#Ciqp2amz`!)u_(>w%u|dhoj7ad=&L9q=@~4!kjV3f>sr2s{IC1aAfg!<)g|f<f@M@HSu|ybZiHXot6kw*vj)t>8^TFL+b<-zf4U;9EHH4g3iFF!&sP7=8$R20sMf0X~KAfNuw%z_-J<fsf(a;9J2*@U8I8;6wOk_(t#nd?S1Vcptt2z7D(xUk6_U-i5D$uL2$LRq&PIfAE#?W#Aq7GWZhkHhc+u5qJx}2)+P}fG>de25-W9!{>rG;B(<~!0Yfi@LAwB_$>HL@G5*Jd<J+0J_9}-ybPZXp9)@rPlZngFTy9oCxRE?6XD~*1o(LP7%(0_20jXmgO7rb1Y_YN;lsff@ZoS97!J3=yMtly?(l!X82G>NonR<@Cwvf!JS4Fq6DumQI-tlqg3<7f@J?U|yc66F428SF+kr9gcJRJn7`!jMGZ+r<4DSNIfOmlp1Y_X?;oZPEcsKZ9FdjY_J_JmF4}lK_FTjVwhk+O2!{8&pOYjl!(coqHX!uz03VbYl9C#Hz4n6_A2A=?*1YU<vf=>Z&z^A~cfj8mP;61<ycn^3_@D{u$+zQ@?Tj8_8JMh`?dEkHWdGKDK1KtZhAG`~n4_^r0gD-?z!256ud@=X{z8Jm~d<b6(Uk*NkFNd!HAH!F`SA$RBtKn<Gr|`A#_24u3diW;rIeZg*3-|`U1-=J-3*Q6x06)Mz;0M7k@PqIZ;5YaQxG(q}?h8K){(zr_2Y^4}0q}F+SNJ)&ANUdO2loa)!M))=;AglG{3Q4ueiD8Zd<Q=Y-)q$8b9+(b`x0vx_!@i#e+@qX?uQ?M{{_~7{{;^=aFGXr_25+G(O_LT6?qg`2TnyE2{wjPktcwS;8f)CU^6%s`BktjoQnK9*al8TeiLjBry{=rwt`cUUjv)MsmQN@f5WNB;|yHnwekNSffEnIYr|`Shv2o~HNhS5n(&g~c6dp632+;{1iU!76<!=(4BQMa1}_S3gcpSu0XM*lzzc)x;DzBPa1Go9F9fcF7lIcASHcUz3xLbu1>pI>CGdRkJm4aD9(XQr0X!Ex2iO~)1D+k63(pSE0?vVFfoB9~!85|sgEQgj;c37b@HFt$;B<IucuH_8JSE%+PKF!d8aUCYFZh!GHZaG-smOnUW8hTeKfqCND)MjONH`Vw7jQV7iu@C3gHw^0L)IN$4*uT2{1;9|{ubN`ry?(lY!JLG{I!9LyeqO0I58UD6+Qrrf)9ZA2P5JA;r$Y;4|pDogrA4E2Rp#q!*64)g8UBH5l%(^AK1yLuX~U?KsTelPC|YQY-iNhRmksxeU17$4EbZQvr%8SA-@N9G3x6)<oCgWMtxm~{0Z32sIMcDKL7_C^>rumr{EByzD`B{3><3I*R{x>gTsvaIvDvYaD-7`HzR)ojyCG+Y~=62u||Dej{E~S&Zw{Bk$(gy81;2O^3UKTqrOf^{uP{J)Ylcszk}0^`Z^@}Pq2qkU$-QG2=+AU>zw3|K&w$-7bQ0!n{CwBQOQ$)^NjksD|srgmr-A*B~J^^H|p!U<mteLMtvQaJOgMk>g&ejnZU(HeVv&+Gq}{KuS=6>1(zH3b!_r%;0mL@?oIv&xZ0?%lauEJ*BbS8b@JTcdZWG$PyQ#k$*8Z}ljjAu81;32^8DZ)qjF!s$oCD19!C8>0(lkipi#f?KwcF*Vbt$akk<!&jrx5J@_)dyM*Thrd2=wpsNXjsZvmb&>i1d5TY`Q@{k{x&6VThJ-^U?u0Qwm9`#$7m@T5_{Pek4jJZjYME0I?N_Zs#4P~_FYeMbGh6?u81K9_af=OU;3U==}ka2MPi{t|o*e+l0W9)RzLR|5ZnSAzQ(m^AnGL6LVtk#_`x;2q%|z-V{}cwaCI-WT2njD+`rTfhXk1>PHshxdl}0<Xe*!3TlY;e+4<!JF`b@B!cr_yBl+@EW{7ydQW4-VfdrjDz=t_eiYv;CV0(PNezqd9W6oiaY|W38x|t2TQ`K$i2Z5a4K>yusEEG`~+AGPDSns7KKxh9|w!TsmPCkh2d1>M?n*uiu?#z2u?+Q7%T{<B0mHcfK!nl1oOeE$UVS3a4PZxU@kZn`Cc#woQm8X%nqj_w}DyUROCCrjBqOQZD4vh75Qc`4V;R6BbXXaMZO+P38x}o0~+B}<f}jpPDQ=~q&e{l6!|jn7kn9f3HSrP1il#j244(c2!4StgwF>*!RN#0f;1<di@%fmfix%fLy=p-w{R<b7D#jAS@=7-FG%xaUljSY#F`4e1Yg66G*^BJ4uDgUzX1EgsmRM9>jy6bFKyK4(51mraC(L<b7HkfEIU2FVxWI&idhFvMSeDs0UEP5{!V#q6!|F>`Dw5&{4{(rio703+pY%&!l}sXgF$dA@&;fqoQgaH7y_pv&j^OXsmT8Z!{AipS-@~O6?rx=0!~Gq9Xt=GBF_Ov!l}q}gHdoQ@;qQPoQgaj7z3vwF962EsmT8U<KR@}jlg&~6?qXb0Zv6;9J~OhA}<MEgj10>1~0*>$eVzd;Z)>J!7Feo@@C*wI2CzC@EV+oyb^dFPDNfByaA^ouL9nLQ;}B%Z^5a^tAV%SROHpcJ8&xU8lVGCMcxX$3#TG)1KxvEk^cqWhf|T)1Rubu$lHPs;Z)>qiF};Mc8Pohy20Jh<`If~9*TT3_yE2cz6rb!-vmDm-h-cpp91f~Pr*-u4){s94|oUe1NR1R!@c2N;4Qcp`~-Ltegf_Z-hg|;kAv6Y$Kl7oYw%<6qu^EeQTP$?3j7HCFnAe$7=8%61V04d2wsG5gl_;Zz&F4Tf(h`0a1SsZ?g2jl#=#H3_k*$U{qTKY416DaFBlEq3*Q4q!S}#-gOTvvaCh)L+#S9PjDYWg+rV(R4Zaf$gYSgz07KzB;OoH<_<Hy{Fc`iLz7`CEuZ6Dx1L14nt3f+_HGCC#4!#P$5<ClE316Y<=i?RNa`*~(D-?N4jnDDKW#Dr7GWZ!V0DcBu%fO^_d@U6DN$?b$<`P7jTbx8*3Udwe(%@-06?qwOvO%A>kkh>8B{&tF3@6ru6YImL!l!`^;M3r~U<QLeA0wXyW;E#YH*zcZw?Uupk^6yJ4Ep?#d@h*HpwB1C=Y!b|`uvl8A(+FU&sWJ8gSid*{FZzPn8%>chsl?L`3(B}nS2FUz@X2!$yb5@81(r$`5Lg1L7&f)uLp}5^!Y#eMzFX+zg{5U43;$L*B9j5z{UpsdW3uj*u<b;zmVI&rUw0bhuj@(X3(#X$oGO34f^#I`2nz!LBIYY_W&y!^y@Y9gJ2bdetk!N2&`(*uLsEwgVhZB^&|Nau)0CN-XuQ?)-dSTr{u@LRtEigmi#!_#-LySl6!)G8T9LA@)KZ9gMNKY?gh3r=-1=q-k_U7zkVkV2iqC+>wR)s4>%9D2iw7kG|y-cK7~_}_W+;4smObR&ozA=gS;R3Letkh$oqpYHGQ3gd;s`L)7MqV2ZFCPeI15;5co#Z*KNpqfp0Z^ork<P_)gQ;g~%=7dre<QBJTr!(DZdD^1k3lO<$)X?*M+%^mQ$ATKA$gG2&<Zo$}8p@~tTHE#OD^7Wh)|1AHlb3HTnq1il!22VV?d1ipnYg3kfpz~{hcgRkMU;a2b!+zOuszJ$+$&jeq<XToQI&*3xR)4^x(>F|Z%Q}{yo0`M_>0en9A2u_>_pAT=2B5ww6hBt%%3vPn{3-6X#ZY>SQ94Yi47klOoukV)lA5vx1^gnbS(zJ;K#*QC?UmGX?FXhjY)&FuuVqZx=Qg&;ZihdWO8593UKkj)-Bi8;8L?)p2'

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
