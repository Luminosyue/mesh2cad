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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/26b87e15e15b449fae1b57bdd6d477ef/part_008.stl', 'relative_path': '26b87e15e15b449fae1b57bdd6d477ef/part_008.stl', 'source_sha256': '47580cf48aa9b8322e66b8be26cefbdea3be390c9d2b5fa44977f6855c71d515', 'input_faces': 1032, 'input_vertices': 622, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02345161698758602, 0.2050878256559372, 0.06638798117637634], [0.06944335252046585, 0.22513099014759064, 0.08400566875934601]]}
GEOMETRY_BASE85 = 'c$}r32Xsx@+y75O^yuB-sL_RJiFR}$BuYrsLnL~cBx;m{QO98P7B10y7yW7>dKpG{j5<1_jrw}__nRO0zy9x9?|NTrJ?s0qkA0v0>}T(N&c5efOHkuv$+K$sQ$Pz#mj1<AKTQ)$r)AX!ghxhq4-1bf)2H8HH!Y*`%bz5j-ZZ#LP^g<WK#TF}5*`&6>E)+;Rg0+NRZ91Y=o=Xw*{M&*zL8zR#b3Wuuc+{E{-|!9`h|acU93|1@}+d2;-&Oq`v3Aznr|tXTawMGDY*n6KQ8KM^?IwQH8q9uTL)v|e|cB=wdgF$?-;yL`Rzg<mESCrOZm;KLzLf)c%l4yLILI1y%66y^oon$s+H`7dc7#)Huc)_QhwvjVAWo)d<*TL7gK(F6yjLk8PI-J8RWA+2L0aDl;5aT8UB{ZReby1GZn|Vp$hUzi*af1&nds-V>R@fY!UK&fcWOzK;(IT=<y%(bS?@-`;5rbICw$Du}}9vJ=-5c-P{hNZts7F|Gqo&DSZ}ozBU|rPMC-M8y!MEx5uO3=8aT)D~%`m^_h)+9}PhMf1N=6m&{Rq=YrvgqkE%1Bj%&uf&r*o>8D$N^e4@)*{%xWw_E6vzty=m;;dYPJS%A`AM;UD_+KwaoW6BYhih05&h=|CUl+R|&n4wi&uKdurxxlNloE0J?!o%0P+!G&o_>INzquFV8i4vci`U%tqu*|J1o@xejJgHvM|~0+BYy+)ZtQj<PSJXpmtG%GhdGDP@7mdD|1ciy?;b@RVmqPVWYtx_cJoBUAMq9AO}ica9ypFT%?!l<z;&|l6!L7b0CBnnxcGGo^Xpg~i28V*L4C^9!TyR&j`m0YKzq+<#CdrX^Iqu^@_bp}Wn9h|*O2G41jO0Z26a1q6aHzazoSwv7r%C)HrlUGhkdl>HuC9#dOE#dq2KX$;rB(q&QaKRNq#d=N6gFm`pU1pyN5c23_|;uCh+S|UFxYn>Z$yW$<Hv}c+|o2$%=Jy^_9zd(@GR{@f#a4zs@ySSN7honD^F=5GP{=7r&hz<I*3$!@SRTpZnu}bfoBraSifNe!XkW6F=^2{cvjKw}v#pdWhgYEuR)~0^ql^`~-j7%*t=h`W^nDjaz^88}>fbt#=&id^`)<=WK)ce>B8=`DRmoXEo$+|5^(1S7e|2<9u21U$*|}*Pi!9oY4umUj32_{d(Yf;&>5)d9Rrt?LYaWK2uPC$G?S<&o%D5r~NRGe|n+c5AP7ab?nw3{q{AibK`J#%vT?8w4d4p@k@9h|HeM3XIxW^E3h!?f2S(ipFth8*9O|h)<XO7fv)wZ-?$6Eqg@{4xwJ9-`{x{Y$)`gzjJHa2#J`-y#s8oE9zGKFSsje_=XxUlJ&CAi&ej-jlm3V^6ZO>IhNAtrwpgD}D<RH>b{JRcNob#Q9pcpLfc2KM67G+2i*dcW5`p$@cVK?s&&K@T>W4gQw1fYTl8Aq3m}|cQ`7y4<ahS(Hk*Ds7>yln&f=iv9b5dZxjQ$OAY97YC^oeru>jj^oUuzuld^H*Cvp{#3`>ft+D(W*Ac{)5ZV_nsab(t6KoQeEB*1_Ln4C0SnkL&IJ&6xL9%zrno&yI&X(eK#?xQ~SNcJbSzCgA>c8RrnI!alT5-wop$aT9sQ?MEG6Pr-g4f%}^M>=5z^UWfKkQ_=op0{n3$Fkf3N<QaAb^%?gW^&A<Eah*Sl_){#jFUR{%zKihB;&pyg8La1RHxTD3>f_iNg!-p^g8XYoqCPY8x%l-=oUgZ?G4BJOGEb~q!wuI5<KRp9kKIQ6R0DDSS@arluJ=Jc2e7})$L~?k85ZK?+p+aWztM0S&N&+Po%Pavp8ER%{c)bTHw$&UmP`4aLAd|wr)!}7?LuguVkz=Br(m6Dtcdnkf5JRo2}hh0e#-ASj`NS@hx?<Qy{7VOr4C_T)yI7{$!~W0i2VCwy;)-n<u^LkI`N}lGwP$?5;IYUg{3i%^@EgO5ATM2YV=1P`nFbnEAvH+t8p*nlfp#58L+NQpK^%f*#mi=oPs=`;l6C28jOBVjmGu1#dC~z%~13kHy-n~I~m%)wa`8S=endiYyMNv?~(mzpT!sZqWp4<_p2w?;m^$w|M+^u+4<JxzGM8e4RMx+p#AI?Sm*0@qkYdRCtT{h<p}(-iHP&HEB0OE(}**2C&pX75aQptg!XN5|J6^fM0@8I_?L}E-TW(~{kVTn=SusrPtz~Nc=LaPKgTAQ^Ne}LZNB>ZzZ0+yGdYp}_T<WMFW-td`G%q2mN}GPUx(|zb4VS;Ka^AXjlwH2uFbDq{EmIkUG}f`BtQI%9GJ()S5fC|Udo?zz0y)tLBD58A<z6P;s3Wi+IOvpJexYvZ?-<@cZ;v`n+M9^y2tyAqd--}4?K>#x!uM(3<|)w9>!q2hsz?*eEl%4NpsMCT{T=EK1QOw+da(J5nQ+RgOlJlULF6jy)$$s@~?sQ;EXMVIxm}x{N49pUJ8uDe#yNIaV{M}dmo&~v};?Dzx$QrKl+XM9T;!De%PnCaSk-nB%sdkb*#^A*-?j#XVL!I7|i?LJjk>2P56_a!oFB?4S8xWk!L8b8%BeD@W-TBpx)oPIPz?q4fPC3t^AtT1GN9wK>W9P(7xmzwD0>B<K0mb{>z===XKQ{SXKFLzgNirQ)i4fxCYt>MPa_~XjmuZYbn2ZJtMBSAO1o7whfhEPq>db>1rdNPR$X2zz4L?G#2d}cSoF(S5VK|m@m8aFpO(n9@MR;C;Ckoj`(+M%!@}b=BvXv#QC}bc_w`xc{2s=m${)|?~90kej3`p|Ac;bu0TGwmZRSi$KY@7j(+#7a;cm4=;;=viF@G>4n+LB_?+t)eP{vd`x<!;#(m1@eHHy)`Wx$T0nSl&=|_k&Z3)K9&yUU%pU^%r1LA+ph&=tiApYEUX#a)lWLoxEHQqBVu#Y<5R(a~V4frehVP0nObKJ~e<+sn_zWJYZ__Vk3YhM;(ozy(4;+VdXh;#i3`ZaO>bpA6?`Hj=5;7?Zs^V0V>#931h@n2k3ah$t;hyMxJb5>k$9V6EupD6`Ts@H#eAx^bT%I^%zuKZ^06lmY@2>iS+JKIl0`yC0&Z+ewP`^*7o|MN+-zmrn=ovH65pF>xb-^%eD>b!Lu>Q?@`@;kEJ!g}a;1oP#%fjHrrP|qSgFu!f@pnV5i-?SdPas7-=yHLGu=8Jg=v{ihoOeW>G{7R{OlCG<E;cCjSr#XxGt#={+xeb)x*=iWZJAbu`<1jnHKP3$L515HM%o+;+u_7lC7w2SW=`qT0oGgd-ZC_)&VGguUh5MS*YZdapyaxH~X^uK{!8uJYu?zV(>4SM+vmEt2a1iZpV;?#0PD1>5H_*NS)`RYBgZ)+XIr{CB3-k468uGvW+NExGNk7!5VBtmT{r@g=nRmyoQp)e#xsB)NVd%GcMddeb6Zz*|2Y*a8<+pp)#(D@(#Jq&mMEin)%5TLyLHpXRlwVt)8vZ>vAKKeHp<nmbsB`Ab*k4;_DZgXlQsm<ujrddNqW$hkF6T+J%v$7AIuv=XIfUy>>^k)O5b+&VE1_<!w<y1n>R-ffGY0vTxQ%`X55YPNsgL#Plgy#Uv0w)3mL?MObu@+Yo58&>j~PlJpLS`K-?r}|&bVmA8I?}?omWsFM>d?_%#Io0{{?ln%BMm5KXNO-qy2M?Yk!dH*AA(P_B>xXLSr!AO105`{3*m~7K%7o>M6gqtrphF#C90(>L&2Nxr#ikI*1<|g>iXfJs5j&&T;-d5dIKv%wrd<Lo;Ns@@wgbBcBh`u)nH|bo{uU&GgkVkC&#SK9zXgUY#59J(eN<!@Stn9fA;l-b%FR_16056Y?y#3GI1K&^um7zi~TI2hVuqa|Hd`1<qr<&9M&cTDb2UC2zw&HVgb=+0p*-3)H#eDqjEn5r3_=She5u67{K94EuU|X61Ko_>A_?)2Q}F`eN|ca3G)fFx24){Pt1QUtgRS<K0|W`Hk(5P`9`g=(l@4w9kGNby)li>u_I)@@tE>^E`hJ{SNM+{N^Q`OZ7S%upf;<h_m=I^087QpGOOoUmuO@zq4R^<kNWr;%wn{X+P?tpW6ukgo>)YcK_yPrIE)FzXa-OzIccBS#0E4Hy`5P`a`w1R@{OA+CJo&$_L{;`v`TL@Dbz9egpGTEZGtjci01r_p}r1KRAQ(J5#5@JnlS?_<v_sey!;xw9gTT`c%vT|0mWn-hw~6mh#&@aZb?o{;A^Fg(H<;k7<PXyRhCg_x_0U8s|5y-~-j(`S@4mH%7KZeI~C`eup_5@o!@v>F;n(u)8lu{`;@vI#a;|@%L;+oO?O3?;fm2J@@ZK`#M!|Jz2LH{f<aPeFBqXA9bIBafMw%oL4xn+MWY(J~6H!PWHQ4&l_5z{kFSk-@K?xeDhqUIMx4|%otb9N{s7xE#-HfazlMQcA<UECdzN#42Qq@8uVMXkMbMk8)Kb>&cS-V55HD}=d>DEv91pPjDC%NsKfDri2rsR;;b!?dS)Go^;~2w`sMY+%F!MD{v3<=8!#`<ke{(mqL(0kOYYy3B`_}~<CNcaONTm?Xo5WR97dcJHQ^r~h5A=`f;yZif%<13iuy!lU#j9{#{JsPFa_)CL>c(64nrNb;d-urtf~Bt+MdYs$$G?(Z>0QA|ITP%q6hNv?4bPSnhEfaZ;19jrt)ju{E=rwFvc~e58~vmfcjjn0sr_Y<+m1Ne(i@E)<eVq<T<ne>Ks=Hb?!R`{=i;{U%U>+TWuBkoe_*Uxf);|51c~$B?kIE9HjjE)_*YG<Ymx)Zy4Gy&ALqaPfkM}UN=Ra&vU}R8u?hM$Dn<^Qp#@@8-V&(sEPV`R8xK}S9|1tt0cyCsJ`+$V;i_!|DCNHA^x4hh%@dA#x*Pe@du!8`oxduw?j+#eI4+R_(}N<j{)fS#7Ov;<bwaq4CU89bw|Hieyqcwt;<~2=lGKF8yAshDDLC-i<<Czzg>p??SuBViFvQ2Em!_AOOb!?A{cMp%*wBQ8jCm+a$;Zj=Tm;YVsES;-gm5kLdtJ0<#=~(L%)$l5PuTSZ?j&Z-@syMpSmvkjlPU^Uatk>KiY!!2VQSdae{j(zjM|MTu(Oqqx^dK80EJY4}t&k2jzE0FGTxVT`=#vQ)2zB-idxI2BH14ytqCzy@c_8!FtnYqHgA^SITd#+Kf2mxX!zNLBGt$$oU5I)g##o_5R1$@A`{b@K5zneycw6G`HNtdbpli`Rz40?-{Fiy7<lbFxUIk;8tkA`VivJJ&W;<3RiyT$2i0fI)}P-AGiYhY&_aOyrTSO%8BqN;yP*1d<g%jMd){ETjX=>i}E|J?m+&Ra9`6;=$OZ|f5CsVA@=o(A*l1FM~MGoFX~q77V@9`6!lpYg8G+Qgn9q;O!>8qi;&N%OYj$biE-`Ydi!OEi(gAV26<*kg#Uf}mFo4Z(^%)pH>&*Yd?x%SHy}>bCX9D`H|5ugO^5&BF0`N9U-|7lgOR`2apgDSet}=Zyy%7hLY?2wM*N1&P=}cw$Y;a><#%jp0)Glzuk`b0(0*J8#QAj`=Dolb<<~nzBcD5{k9qB;@>|;{VZ3cO!hiD)^2xOl?W1?&`m_7K@;kpALHr9&<TE2=m1_5SHtIZS5$4x!r~Jm}t(cdRGnHSP(;og2xbGNyP)}oFSNN0e*C!HDhnOD9@5pfu_4oT7^{mog`K`<?P>0t~QU5#hm0u6S`nStA!8)n30rA(FybngAZvXCszv@85NjDMWntl@f4w{Pg+2*32&dczJuSGsxmhk#~NBNyU9Y>tlW$4$d?rP<KG?>@DdDvgc8z{du5cgAO*f!Lygg@Gk#`>`ujEBE;Q{{K?bDXv4D#m-HmGYZ|)?vQ#3`P9Bec{iA`O-QK!1Zl&r1I<a0^pzKhdQ*Fh<xhfKBYx=#JI*dlwafev6lA7^~Zmk^4rZPV?8wg1^YMV1oAJu2Kkhqg!t=kqy4pGsL!Y0P@hkQ*Qj<E>LJc(?29D7&g;C{U>U~swYc&-r(*xwnI>Xg-KnJfR!8h#(*xtRp45YX9-kX@E{<_MZ>0Q2rTG}wu<oc&!A{C=Ct_V0e*|E>?%m<9js332c0&AeLy-UN9>`~PXVhWC4CI;b7u54}KdhgYn~+ah+^;p?!Dv6_(i;5z9>h-;gLUZp8FA87fxp}y?3e29Yn8t*&JX6BS*XKiPvtk8;(BYZ9fEP)%%%L=J$!Dm^c;vEs4IWc`PNxC0(E{-8SNWkUd%$in8%e>;J-Nv`L7N^J^{hXZ&huB_?rR|e^)Ezx4YrKX7>)l{_PNj{O6-zBcMIzW%hLCH@1w!Iw=*7>(YgI#Mu#x_Tk+yFVSa_e}h8EKkHiLbLa}%CzM0}Q^%p-Rgab5F`^FQJn4b@bb10m&vnL2TyJ&v<m=S?4&Xd#R&9;=snRRI!RHdj?V^~+%K4Sw*);<7sppS*sq2F{&Dd|dYH06PL;1B|aBkG!)<peBgrNNcuK)S|7;o}n==XI`j5nqk>O6ii;y8z+&OL*%-i#&4=Ng_rI5#XnKHJtQzxg|!(`wNJQJ+%#l;6sf3jIdlyrg*_Qhvv}qCA(j#rhAwiS{ijBmR&ExL$R;1OM=BXx}Ou@*ng``SsdZx7w*Hh_k|Tz0zl1=yxCXsr7Fj<=0oV!n!J07WtH|to-I8d=Aw^D`Wj^H<jO!&=l=`d0uT9h4vPohg-iQP8AFOtMB=J3f8}EjzhoKc)zgm`9kmdyYky_AEQ0**Y@Sv=$Fr{t%Sy?!;vkBzcdHx<6as4CdMnjRte7oo$cH)UkxrG&NbB8xv?15+km_1*NNv0mQPO9^Vw_UxdZ#!_$M#!3)3=fP_Owp)Gm(oX^pR@{LZB30C~%z-|lsl-_iRt^4TAQeK9i#?Z@JKA8j_*|D!O(Peglz=SDjuT>14(xZXMr`yhU$ZitiOA?n|$8uI*ojPh$4`P?HI<JAIwMLt)rA^w0DXg_kf^4ohoP@l%R&~Mjx<g*_0Yb3|{+?<`L{8rDbs9X8;SZ}ZHBhP@Zc)sMB9s4LU#YXiy4&P6i&-)^uur$hVOwNRHwZrEoZ9rP(w^!}N^NnEvi0_kK`JH@jW>)m(zRRindW+4-vw#!(y=Z>rH&gKYl#YdYeJ+YPvo0deuH0Bx>q{cfH+#`<sEs(9AL5j|gL*DZgMM$<f`2=n)9Q=fp>8pO%5U|1fq6Og1#xeLqTl2AJ|*e%j{UX^#v8}yqT736og9e3`##J?K0UDh_0N4!w|G2P*N1ceR*FQwqhIp-%}iLIF9xFD>od{*%@))%#c;%*x*l~{fqB;sk4OBvZZ7vV?av8l&*z^OKfh>MrlEaRJg2pOO2u<yEaoL8;#)T#V4e3|jePDMz<d?|it#_+q*R-S`dh8uqy5>Ph(BX6>feX=yOO)`zH|NgJyajmr|f>zVdx0d;dw>0pPC3ipR1cElA%6dk7Hck{9eBDD#Yn?68ZeZ-#?tyu}+#@LH@l)BmR<uSSPh^U_J1AG<|Uf^xOIl@*IwRXWmYY>rCdqF|HDm(Qm|`s9Uk;$nzb(r_gs~Lmgs2AfL_i(Eh}I<ay~c+84lcR3o=1;wQKv-$@-1=jUL|`!ILBFB$x1VsEswQlcMzPo&?e0skydjKg;Y=EZo0JUuWzYcIZca~zDtdWg=5zkdwB7E=Q6-;fiU4$m#Muym+@KI}hxVh`jq7wc0?$cOmP@H-zZdmhBK3d6q->&n=Sb>eJP6#2f6MEmIp80W3x7?;@>@ze2js&eReUo`et&g$s5CD)5P)`NcU5A>J5D*CV77;&y+y*ZD-?>y#@_3)-0;ta#}*un4PoS~o5ZyTIPjGAcg*wP5`E7yj9GQMYYM$JH+ll9Oqf0v$ge|PxtTo64Hb$EOeaZH?#jQy>V|J0>;eUJMlz6rnYD22EOTi|^&+QI+VX7pPQ>%|Dg?<kU<GZ-IRK^NnDcKekd#y_PE@=5wWEB+qhf5Ev%Kabxp*{wNVH=Os)fljQe(l61jeJA#h^=U*SuJc4^Xe*Q7L+wYqRpHP)RZ*Y6@!H;vbBAL%zjx+2Gs$n<tA_eijfVepSLBr%^Q+gIk9_9hbBxLFZM9-k@j3|ST;mOYe^tIA-roZEH+w`^%;Wi?E`G<#U(r75F~;K^>9UWktoWSns1t?w8uB#O8F;-J`D*+fyWV37`t!kgQ|IsK{!`~AgV0Yr_LrmmWaPhXF#LP*`+ut#=G8F``8uvlMV_lpBEJ7H#Gj7(7#lGkcHa@`XLNbAuYz$pM_I@>rWyKO-Vg0=!moK$M4T=-7ddB+grC3n)^lS0>rF=Cea9kP?mLc^@H-ln#dy<(;r-@l<h2ps=bGj4{KU-h3;e0exLgmlv145JSJLO5B)>fjbx3+1Vx`3M1MM@`zaBdruP5+x^8;`A8#Z<ETVHX1H@@6LT_S$N-}Cpz&ReLz{Rig9@v=AiZL$INc`ya-`8yWvzKQxQ!g_QrsE+!)pYP(=2L+&gs%@_Rqru4Y`6P_L`!w{sp$78g=QxKx-DUmjeD0CtcP{IW`1vj)zsv9&Q}O#2M_f;|_nF~xopiiM-Hau8j%D=lLVRZjwDae4or104FEh{8f2oh_b-)edHu*a-vnf7DJNn}Dne~OgPp*K^t;PxXjp=1v>Y3!X`=FlA%W;S^3imfh)~1O65YG+tmkZIqrw{5s6?L<AJ6!5%)xvn4k&EFUTiNCMW1fcJd8!E7-->ea+kS}e9Lwi^)sdH;SPJ!QGXeR(hTnOxAo5J;hW0_Y57@6U@7ng|E`G;N?w8Hi(5^F{51Hk8-;6qq__^^uga2;G=JP}6{FQj$#X`uZC9V(VyOpl%fzO4U>v7I9`1?t_AFhK&-ZjW;6Mk1_W;%@5gW)$0qYnB&T&E0g>{n|kuK)Hk#;vms<67(MGVk_6`0W*iT&_QQtM%}I!SBf({jlHcP4s67cDX-Vo*P{DyLAui($ew#Rqu=6LmI^}kB&!po^2Gb<FZf9`iSRDkM(bzL>(NT;Wx*ZL_TkDy*5K}KGKI2a=G3by|%jKV}HbT&?<y|Z*9eT)3RY)PAwkq<Nd`lnRh(=ngi?5s4>{ppY;1W?mM&ZPM3XW?V0Z4*H_{CZ^s`)f1~*P{&F$I?`paD9c7WfSr_|9y9s~NeJ$y^rNei(OC6H(G*)6?YS&9+oh0J=>*%-_c?EEN_J&{I4S&-8DCxPMejDSniWkMWTI2p<oI8ZS_r-lmdxiC3jmJ7Q8<cR_7sg$#-vlq0{cFuX0^Nc7Cq1vWo8#PS|BK(JnfY*i(bF77`$4$h>BGM5^B|Xh4ZG#d-7L2Ex3_+?)LK?8qSFum6jq$_CrSVR{}i@+h5yk%g)Qgp^MCxeuxY}+<uK}-MN+4dBgqy`crHzNGj#=7bPstmIf42IIe~nI`iOjm{ER02iTW>DG=&@Z6FHR|G&4CBIXg|b5LG9OmLeA-m!noAmm^oF3HwtUl0{pR{mH>plN?O$L=)~!?MD_JM(#}>O8u2QlsththdhBiizd8;x|A%sk-UVwp1Oy;p1g}DoIpKB7X5>qKt4~k$>+&8sZYo^$$!&?-%&r1-;q<fLqC#5)3}4hg!53-k@JxAQuCAZlFL(zkwq(#%ai@6#mIhSZ)#SuXl}A-VX`;5GEKN1wG_D?xjD58xjnT3wF+7EC$eY>aszUGny?o&Em<@rIUDt>8#E<Z^o<)>^cndp`91X!`4#mZ^$}V0I{6;?3iS;63i$+0cpvp3S#%qDA9*u%1$i@hIZb#Tbv{{i3V9xRGIcb0GI<nrAbAvd08O|DwI^A$Ex8A|J+&#hJvoqCn;b~4Lldq{tw<IvPOeNYNzF?xNzO+T&O*&d7EMmhLQYA2uYpsNKWfki<d5VhG~vtCb7axo<jdql>N0X7c?(T=A$2-gbR>BpdGa?KL5-%4BuA6GQ~Q%!Q@c?6lSN09yO0M^W61-^Gik!>soTk-C&}x{N2zznN69y+ugRh>$f8flH^`T0!e^)t$!EwXsDF_~Z<0@t57UGXP_L5@kPlL?kwuS?50ckVH<8znXHgfCMMsfmkq1%3$b-nuXu<_)!gXlEA=F562)QTKBKIT@rU_4?2`{0}C5vt*FCp)wCXjcMPf@RsPmyoYgkMpgkwrg|Uy;93<y`WWuZ7dmgmY7~lSK=WbCZiw%aMzc%hQBwP^*(g{mC`Rji|xoM&wpB;m*`fWYON_&g5Ryq2ylVA=C-vA>?s1;ThCfWYHz$8Ds}_J=sBCOB0T#?jnmOkmJdRsprXu$!DoI$!E#eXu=Puf0ISukspv>(}X?Tp>js?pb6)q<{?-8W+lH_X=*NVF19I66D~*1OU}#lN;#UaK@+Y?^&<yT8&dtqemt)<q*f+Z<{70SO*oh)+?m>(+?m|%hjUCfns7&I19AhNS31&!18BlNR4;PU*+sY@H8nLGIUCP1sj2VDV#3MXzn@)%KT)4j#s8Fle~<i>e4BcOe4BicCY(q;K^EOdP9*Q8ZYJ*~Z=wk=qb?_l&Lb})&!tW#&n5px9Yy|)Jd!5dpE`gn+JoGm+@0E<+@0K!8c6O)ZblQXORYl|txT><u0kzIu0k$N6D~l_M;6UOE<nykO-as1PD7QmOB%iw{z4OePJKcay-a>iwyB9^n|zukyo<VpEV_`qi@cILnY@xbn<hL)`+n9Dj`(H+zgc^la6jr8@))-7M~x=;BX^|<x21L`w<R~yzMq+dD^Y7xTa!h*kZY3zr~}9W<PJ39anzY)(e>nU<fYW3<fY`j)Ei{cOJvbA<h|s0n(#*I3GznrYU*LK=mGL-@^YH+D(XS9=o<2`)ZeLV$fC2zqJzl4ll#(yD^r`1MGKNElQVp?<ka-kg5>n%ywo~m(GYT8a#fmeb81g=b8=_uU~*^j&otp*Xu@--lgOe=$aBbRsXNJQ$@{6N$ot6`Xu|iXx5%Qe$oI(as9(wN$jRJb!WpP?-VzqgP0m2hLoG_qL-wKx`%uf1MQf0K$Tg{r$Ti80X~M0kt;nLC$*sv@)L!H;av$mtav$;_n($caII`#r@>udTs)Ia@ypSfmhPsw48c$wB-a$P~-a$S@Jxe}BK1CD0Oua@HeL%iUzDs>gzDs`j%`|tYJM}eLRL)+)S*SUv9%K)mw{lQRl5>!Y(}aDgRmr~OMl|8ZG~pW5(qz$cWKn}$gWQB#lbm#JYr>eKt!cucG~qVXK(c5<vS=__v@^L4If5qKi`tFci`<jikt`ZO?n!P-6K+Zqu1@tKC!OJh%Tlvb3z9`slSPw}vy(mDzn|fRQ_%M>UyEN@^eOpY@?+|4@?-KXn(zhcMY3oj`2zVUbualSc{fdX19cNwbQyUAIgUD)97mo_{f#`EJc%Z3QAd(R`;#qlG_^Z9n%s@rk=%{kfhOF7+Ken(m)wF}pIU`npX^H$E<-I%7A-(7LoP_oMlMLsK}|!>K~75()~Ir})2PqMV#5E>XOsUS-=ztkr=BK@?joNjJE<$lPVxqt@B->=vgjD{0`dgvK=K4~3^jrrL+(ZsZb@xHZb`0B6Aq+CkVV^*1IfYEeq_<EWYM<dU~*HMut9A^HppeQ@8?M2pQweYmB^yC$%V<qsR88TWN(^qU1|ri=s0p+@(}7$@(}WT>Rz&FJXv%jc|LgtO?V=8HF+X=Jasu)bQL-2j5wYq98Ue6EZUbWTA3V9&O^;W&O=U36V|lvXGHnqPIaRuCyS=n{<AF<r=baFq~;}OB<s|wWYOkio$N;w4x)A@2a(%Re<rsh_ofLCrwLD^{z4X=L!L&Cqpl^#k#|t{lXsAh(}b^5FOWs=k*|^;Q{RyvlRwaeJ=~yj))W@aK=vSKqUIrIBL74aE=Khti~5j@kt<MZk}Hr6ns5NMF<G=VIe;8O4I_t;yHNX(yO8_Rga=axkwwRn2b0H8r;*2yf2Rq@QWug%*N|h$tEfB3tH@iahsayWPMYvZ>M645W%5b#pETjWsCUVtFUfzApVNfDxP3o^3a6)Lpo(8u)SaAk9?d`#E<(*g7A;N|^(7Y}SNdjkss2=7vS=f+KRJXZ+=|+m+?Z!d;dWG$+L~;VyHG>Pp*%-+p+=Cqkh@cRk$X^kQ+ttn@f_Kk+Lqj#+=(XKg4&eaf?SPSot$*OtVR<qO3hBr&U0f?ns83{?`KNkOw{Dm6l763QzqwY;kRzk$K<!<hcw|E)LUfH3*;N*bJU~cbL1m5;hogoWYG=eo#b`YIPyC3V(M)2V)9Iy@I>k)vZzI#NFG6rCXXOTQM-|&$X#i|?Wi5dqAken$jzzs$<4_PXu?&gzGTrd<f>$EYC*C$xd=4}xd=HYP1uu~mMp4~J;`oVIa9jvweTC7@O|oCvgmp8eey-BlYEhUh$g(1x`8aZfV`FLpiUq=$iLBqhf!n5qTR^D$h~O7ZKy5Djj8_BmSoZT<YM2f^f${-6D~><E=lzvmn4^?Rw0YlB9|lkQvJ#P>{qxvwK}yvSu~Jbf!cr?NEQtyi#8=UAXlRam!TSD(X!++<N`F|T-x_DaW0y07HVN~7IHRfadI|tcA9VwsyA7*E;$Fe2z3a#2)Pe+K3Q}IS#%<~54jUfxFdBuSu~t1nupwxoQWpvK}}5-)yN*?lvH<eN^)9F{%Z+nDylm<6*(Ezjhu{}f|`abnvtA>>`B$hp5)9lVK1s5Su}|3MXpH`ZbEHGZbA;F_9lmtO`32NO?WJII9YTWc`SJzHI6)wypFnqypFt&CVZB9oGf~ke3pEh`j~v1{E{a8nfie&D(B$Od@Y>X4VsCZnw*s;oS*s=S+p2AKe+_80=Wda5>2=k)gX%okZX~fP(#Q~$f49O<WO=rP55VOU$W?6^3UWL>KJki`4^h-RO;_!(OB|S@&f8A@&fWo>Q?ef@)nx#eyWo!dXl`Ke4HkHiTWp5^e^%y@*V1P@*VOEn($}p7jn{B`7>V&XQT=1G~s+S;X>35<P1C$7ot`o7a~`n3D<J}er^^HqPC>gC5!r#MMKCf$zjx1<fL<R7}X?)k-Jj6kh}2g+x3StaaWpfI8C?%wKusp&%qt2Eyx|n&AwS3YHex@atoe=Ytw|wP>YhwkPA?Ak_(VC|8OSGOcQpaCMS!^+1HJ)h5w-m-={t#i{2pLCtszWBVQ$-rU@UQ9wCeFBp)Der>-M!C$FY1Ca)$hq6tr@&LoRYBu^)gr;Z?xCl9Aak%yBbX~GfIu4K`6<Op&bYIAZMau7|p9<>2kv?{qC*^lZ?_9K_279p1<7p4j4qUI!vdXjUI(^K8Z>B;Ui;kO!8&cwo^_sMU`e^W1#|0e%Q6Fx>gL>ApjK1SX~b&$7_7t@5NP=6zf4kJ$?52f}Z4<+}Y3AduQA-5to)V`mU8&dtrqP55k$@QpJ$f7>vdgK~3;fmDK<cj1{)M8}O{Nz&Pd^F*#G~t}oqU4<9+%(}r)RN>v<Py|!WKmyoP-8dutjYen|0?YJANf3~x%|gr|L;3p|5?S4?@V7+`~HtCf*O0sneN*`&|N)5EG{#o{TIL>L3I'

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
