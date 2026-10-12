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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/649dd4c47d6d4dd099e518d6393e7c5b/part_004.stl', 'relative_path': '649dd4c47d6d4dd099e518d6393e7c5b/part_004.stl', 'source_sha256': '8d3e4c774951d2eaf0b330c5b5aa4bc753924afc12df745d9fe700fac6ecc822', 'input_faces': 763, 'input_vertices': 475, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44182175397872925, -0.4869077801704407, -0.4999999403953552], [0.27318769693374634, 0.14344054460525513, 0.25584447383880615]]}
GEOMETRY_BASE85 = 'c$}r22Xs_L-^On!f*24bpjciOrHG0mMNvSO-a_bv5@0C_q-^>wX@pBtx^xf_m)@iYq@>)00HH$&y||KurXZjw3JKrNJkOGy_x-+ezVm%}{^$AS$z<-_|IEF2?#w-Q?^3#qkA{CWHT%k{cgxq;G!fpKk7f^yjtw3j81qqhWW1MFS^DCiTj%=q>Ds-&muA-z>y8MF86I8t3sc?ZK~3v^XsR0&5gi*nG<--z^oT&=w;vi76X^0|Mh%S&bp8BZ<IkFWXlhjNL(>@3|M6c1R}+jA?XP5rwzRLcv!zSSMFBr$c>4XFdxWnS4W!==e%R7<_yeTxIJW<?^andO3tua0Nk2>adaI^c@S98DeBj1KS$;ryS>7m$k-q6bf%Ns(0VrP_LH|0+cY2I=7O$ZH^F_~g{)Zo&ohIuqUXJ!>?}tCk*n;DRpq<%SIIj6#Cj61~Gf=*B`CX`gvg-H0vIp(_ntnR`hTdCozF(^TsFXC+^A*~;FYr9dSC-}V;)V2w!#C$<qWnDi7Wj=CqkK^?{Xy`3=gD?z&oZU2?F)b(REv2q=np)vw4ddjd;Q=KzJ-1%UW2^t?Rp;l_)Zquxsv6(puD9i^BKqT?b)6YXpdH``XhTI4_XoZwrYD=-m>jso@amQ#SZ!p^3Y#*GT|?!{~O9TEWZ`)iNtu@b`O4+iLyP$v)@&}|AjsOtsm4N4ef!iZ95PD(^}imFO%q>Lwj1Z&%}5bkNj*si}IiOZbN_dWBD`ieI2{d{?#m>tG1_jmFfpoPV@9F8ycTMdwR1yvsK^M;CM(?{pa=XQ~kjEsh+-b<^0pAXX!4_@$lU5m$yf0zuOP;PV@8~D-&3c&hhX_^;wTQ|BjXMtmnftPhW4`>4ax_*NM?@2fs@I`}g1ck-ll3<&8#fD)pG3Wzl~PzVCGAZNKUVy`JV-UN`kREPdXW^x|o%-|rOfOH=9hfFHaL?J1su@n&iRztv-m=cn(Ye2t2%|JR+K`F!rP{{QfKpK*^9y+%3s18!}?aqaM{&OV6ouv^w+xqRrH91lJ%;rp&b9&SX-`<L0L1^j-g=&!;k)ep=|_4J*ue1AY5r)3JRizlhq<j=3nkiKTl!TCP9C4JK?Hu#-=(T@*$Tv7b~**M<^-BmxRd77v1s5}V%;GE6K=W7^OmAk+Xh~smr4f0<xF&q6-UOv~fr_W@2oZchpzXiXj0mg&(Ao%@|H{)p?`u_0wJT;zvjN^KDQOcW({BhlRw`2LrC|_j3{h@4dmaH#!t~?*}An&!}_s%jyr0=v{l)f=6Y@P5OW&EY@upL49j@ip)f0pSWeQosHSEb+Ssq{@{K1co0RZu>xV1ul`^t;m6W4@HW#pWZ&i(a~{^v$*n($|A-Et2I+6=uqE_CMhde!M`QN2xQ?H%Erc=f5es@ei_|QpcsQk8Ug5;|K|p$2FJQCVgkz0_huF=B<$JEVY*P#9|(in1cTFnt^&^nsfg0cozIg(s#s8Mt;mM;5n)FLOrpOC?BzPs;6&QPhOIL7n&m5W6_#P-xN1ewny(bYQ8N0%v<_e)KbiMVoyzz`F~ac^;>tydQ7ob<oTMO-7{qUk#o`hwlB#0w6pk{f%E+qd5FBS5&i|~Yhi<BJ^H}ZHMqVF>6;TCq942UUMcfdoGyJw@~gQ2+WgWyeJv>n<JdNU{$3n6xjM#QuU#qdceDIRS>8<FRGfn2Ms33R_US%BwzFuB^ey2JWjnRDlV$!LMYGTz+fn47=c^Y@rk{=c_lca~>Fc4*WIg8g0T{PMcGMphg**&<Z;_{O4y}jd4lN_czo}>xeEVJHx-gyw;Jn7x#P#XdR_4v|v>)n^|54`C6cg|R%J-GNX>=`&!>+Yhz9;;o5Zu4~e5G%B`X$;QpK%q}cbpt2=BG{3?+LHS@<#WRm7cyi)`~ntH~+!Y*TS#iyuxNpk>~Za0gh{3Cw+^4OwNOxPkeCPkYe0_J0!`x=}*d|9{Ua42iy4}|4&{({_SNjo+B46k>~qoQ3mqg62~3*y1ah1KQF>hE|2+Tcdu+u-;vl0<H~RKe)wlmKFW~e#OV0Oc6nZpR-=4Wj`SU)=i&MDXm$q9|02d!fHPK>|HBGD;VRlW@G<iFdv)nMV;A5)(_{Bs+5U$`>9XFC(zt#{{kmSB@54vZH|!PBFWn-?$$B3CoQ~r<aonzd$oq`(;DGd<Q5WEM4nq4Mtd_nhqMr0EQQqjU`+@07e|2jxUe@#5=hD}$8PYe}T$lGB^KaFqZ;Ad3^|xCmuNUK9MYJ>c1p2X48QC85y`R(M&!g+1{XHs=hksW3TIkz2Zm)jx<oVv+DSeA|53Zx3K63n<f9)@QBib9|O*e<j{Que&endC4r&~vvPwkhQ@U3~W9%tJ+m{<Pt3XW@Ci1X@_D%+{wxtoge$I+hfTZ^TCdmH=^Z(P6O0rLK4zP()frm^qgIp?=^qHOQ&+0r*BMaXfb`QDelakB-=$J9pq+gc)JJ8xD@MZHgP+%}bUS%2ZCeX^e9B8<;rTXH;oXK*gw!+cYa=fe5>kk1;(TV$SWr%@0ueLc|+?HSrk)}t3hp?=<f^j;m2|LYI-%KF1!MLvB`$@XYJ&yc<;1n;$muaCSBXwDvcaosgXJ-siWo-_4-l=Y9Thy1kZy<GnOOik%qlA_R_wz1OJ4$n`)by^Phw}h#9FVBgRz9YF3o(uk2a(<!Z^hiN|ig91+xfa*;q3Y7tlJ8?4W*>K4`Uel}kbj?y`IEW#s#Tu8Ik64e6Z_<t%$qT3yZrm)N63Gm?XWDLHhY^aH?{`O%i>6q8uZd;oG<22T42h0*{;ARn{d7y4?%g-*G5d(gm&JAAG1du*W7FPdW<U*>WPh8CbebEDp}u{eB8G)hn$k_Y&l%|&V)MBcNq1gueZ3oQu<?V;yD=K<%IM<zq|s+y$65POGo5+HQuq@^L({F%?`-&ABQ?*`#BCBW3w`(-*?wC^j8`5%fJ(O|Lf3x3Hqxd`mui*JolR&T!{Qv!+CW#!sXvLyfGi`EJS;3t<YZ$s?A59-)8yg@;vo=2j?O`HJP6P<njGob8+4AxfVMSeyV>g^5(=iNmwrPplv@NC4ZmzA&wjOBK(wvQJ#6T1p6aDPe&!Tl<lvI;|6tHERQq&4_qI~zv8%k7b0)jKHs#I`TPU<Y#nS!-#$QIAC}~QFs_DN`cd|KTm|`j(8gkXY6BXt&G7I|Nfy*UpttmO{Rrl#%(H8P)<Tw_cxRzJPI76y7Yz=O^KE_6``^j(V}3?^LK5Y9IhWj#zLxkt@-y<b9OwGbNAmi1+RouQHLN-2=fmpby0NXq{KWkn9AT5bY4m$|-VN)GdCTxI(l^_-pdQ~mJf}wNM0xuiJl~V@<b2o>RB^S;kNt0y@0hyW)7N<aG_~0-pGT%qGo-J_e1Y<#7s>N61s{;U5ySVW4(am#uZ8xJ<IxhCgy(y^zL-~p21?%)8;tvN$hvRkajkcy?~I&}d2iS#`CM>>*T#EH++xhHhEJF0t3~!fz9T1~{?1e7^Vf*9N#7XV4f$#HscgR^awqDsp2xhX_0+96UZM20xS^OQx0&vc^+r|1aiSb(Prn?Do9HHZPKMvbec1MRDe|6%eu$li{_?G`1O0aZ^>BV}wt35bblA(vd56Wi8}+oGvkm=GQTpbv5Ii?K`Qo`by0-M4iT)T@0UZ~~`bO7ZuZ+)u<)yFN+oAr@Pf`DnrSd#Yag*TNcAy{qU&nkY{yWrfJ%i^X-`6aO?eLyArU2K4|K$T1$6cjw3ayQH#y7_ManfqM4}~^_-_{4?YRo3o6S)NMcioG3z%NAkkl*o~9Wqb0)0|up?>D^PYJH>Rah=Icq;E?274w`CsmQNBX(ReAgYQjom@kc;vC(t<SlVnxzw1|}ZwcOkb=)C&7*FHMV!jr?3H7%sgYht-h4dXE<&dAmj>}}Z3GJlsw7-G(GLBF4gfV!Zv){yZ6kj0w-8o_P4>;eyaNJe{FyEWB6XmUIIA6-ec%FCw?XmxkamDuwZPFvO$94jKw}UdDmaod<{X4lV=Hbkbb5d358}9iDee>6YHhEr;Mw?4m2c2xiI87*v=X+q@I>omhROd63H{t#ieiixYd||dMH|4-4<a0Z&$2JGID!%<b#-ZQiIjH|C+8>(?KdCA5JhiqQU#8$SnD<(;Wq(<wwZQ!>{vhff|M+`ZZd$v|$nzhVM~z)2--FE42f^oa!7}2;ZckrN?1bkOeakc(%3Jqx-o8QRS)V=w<wG7{^c)Y48LQz(Wy*1AZlAo((|3fFLOpt%Y^O2vk@U?Ww`Dz+R;{;s`g-t>INu?waG#o45$oDf>A3IpIw9Y?oipo8U$f_9ymh~U>uY8c`0n?ni1PA1PMdQV`H21veslx5E@8}mgmrn&&-KpbWxwdNi==OgE<}0TR;**>ltO>nU%>U^movxH*CO6R9@^}}c^$_6*b)|l`YnH;ACKU?%@LpA`sMS*IMNf(AM0A=t;^CCC_k9~2HaQuzLMwbJQ9NACf~uhZTq|7={uqh;k~T)pE7TbBhhG2Vsku~+Z1B{aKw&!tV_^NdjQ7k(PW$l=gC^E5$NeZzdu{dBhdb-Z09Pa9_P^&IA5;+xZ7_WU4#0gPATowk8Wo9tx6uWW9eI!>zc=P9L05}C$>}0%k7&Y>MD7DUOp^I=@<Rj5#){YPxtv6$F8BC<cCV0_2Z@FcsKZ7<L-CMajs)o&nn}}I9?6&h3L!5xYCdR3(v#o$IAFLAIJNpZhv~kbG+#%>^N@JNoAb7eRJ?8<vKE-On@KqK)voxOobnnqFi74$(d+B*HPWqm+9nUv?q%DnZw%RetU8SeE0o<*SmglGkr~YjyO-I^SHaz`^Kq*C~wVD?mwnexorO(<^JY8b&2P@S-DSYrz>s8IR8?)zd2963O|0Ia{qLk#(Ip2?|1I|q?Y?W{P05MK5v|Eh<ajU)cbaBYm~PaD))Kk>CW46Ui*~ih$FWr%Ezx&pBK5|($``KE6*wI%y=9(;UBEaxt~*KR-k^ace$Uljx%evdtTS>=d6Ba1JstKJWtJe+u^(4Tlw5{oXNs*lmEu}|2N-czokB}^UmRU9#T>1cT3)l?HE^AlzD>XY$-fvg7+%(6Z6>@aG$VOQsx`Zvmar;8NWiAw;1RAFfWMOq0WoWg`l3end-dg+<1(ykekYUOgq0A^(Q!$d6(n-8k7&Mqs;eA7q+83-}|1=-_GyFaU;J`=7HLUTxe)@bv}8ij=cV~<lD;p({ZsO?%(ctNFe8{m-=FT+P&Vwd9QYP7}lq4Ym|Af<x({24;!S+x3$a3sK>fdnV*|3FOa?w+C!PoTP|-vJxK$V`MK%Jc08ZC-tL~C8<*43{@AaT_XYEn8>lDzC*}P@yIMi6$2cSBsP7}!>g+@w4lD09=4)SIe`s_s<-NvvZ5Y0X;QomFy-B|oj{U;Xt(5mB?WYB(Kk_T(z0CR3V$>fuU3o9FIIpw*aOJ&E`}q#mlVS%d?|tU$Utm2Wrj_#kXt~}K-%rGRpuTVB&yl_}x~lSi>d0TV3)kIk<$cyva0KOTmz4KkbHR1&Q`#KL`?9m(9?IKaSKhCk1r_A_fqQ?={XXt2tRsDg?V$4hZoZ!`_wAes^_2I0?Ljg2|F}-#ULVl@{%0S?&meXE;qMBm7(YJhdc~9v@ZCwmJIcC>F{Oj_9b?WZ>oCq)Rk7}#6rir#%zk@6>aU`%^DNnk^_7Gw%6gY$NhbU;r_}YaRd45@et%{C&AF;>4(hL@tk>zA$6;N>{eH*wKyAyGBd9-DSy!~|{8;|pnb=)f&$R4phIK^lJGj?BP5V}3eT(-K_j;*gU#9dO!G^NFs;54YzB&9J?$2D0)zg~D{5e9(D9<TNT05-sh5U`@EZ2b@Y2Bpno^QC<jU8zNvF?>vPhB5QPelD=E-35IdioUfoAsQ!UY)TK$Bll5`3Bdwof&7OZwe{I^MdQ=CgUc?1>bAj>*QwR5ssT&N?BJo8GoT3&bM_d*XNCLC*|?OB9--g!*~V0b(6aOpZS6GO%d-Y`vsQF&)~b?Be=id$m}nDBW#YcA7RQGDSb=GBjl6&7v`+7sK@<2$bAq;)+FgW?4^`_5N-cL)X#bK^Zk^pCDM0>EmZbj^!+=euUmH_|9;%B*?$&(xR<iOqh<esJVb3#_Jg$Szof5)T$1f{?>AYlmy_3x$zFi_A@`ds*DFciz2EnI-|Bi@>09DclzlGebzGO0sIAJrn3i8(`dZZY>ONZj=hAmZE>QQ~@|&Z4Xf<VD&ywHnl;^m0@86m8JD{H6JY_%8oZk`mgE7}|{c;~r&-X<=_RBag?k8IEyQ2NJRQT@w$9#XRuZJZo`<Qxu0Lt^dNejikr;$G#<zw0?`=rkN5ac=GCi2F8RU<zX?T?$M?89mWHq>wbN14Bw3gS?IVoPN|*X=v_9CYssKQABh4C9vj&RRh{@)O!#*{3!aj6r$#{FD39=7Mo(Px7C*pL0LjTreK>gj81d!3(A%&$e&Xee;4@^zpoNaG%{$Fc<Y$4=MZdM!_<iSLAqQAKxh0fc9{G&;7lDQLqtyVl(A?0IhHn>f!o~#_tfc!p#`xiC-w+8#oKLpuf0ZV|iZBHncza2Fv5S1+8!|>WQ;*pBmpqxP4RPNaZ^Ub73~x6ZW<8-GyFw81+O(D&J{13vZ!cMmJNw>u?s{MtiI)l<z>Cg}<SG_c#pacOy4mJS~48Gf?@?#B#%1`bPB2>USwOs!87w(Lwo+#kf&R`lh&1%6Bi?%@3rnN0^oGXSACQa9n#e_4}Ed%}~EBNBIs%zu6h}#3m`<?dUiC+0M$!cRt3=p=b~9=O%s^q}{Sg-)z5!?}hjsk#;NQG{)f)<+~&8)@anj?}eU^|67SDA3LJtyQc2SSJZW?dtYo@%QbRc@uKFV1r7E1gj$$#SX2M|PpE?%|F1rw{_N96|KCrj>$%$So-5v=)*`<{evA4qve4JbZ;`7}UnN%~SEg1XS0-1WmL*ppm!p;@mu5=KF~q;}R4=m7QsnaF7pY~)LSG;YeTn=c`DKP+AL=V)AMzX2*T`>>Yf|4P3w@VdlU$ej0l6;ueTLxr)Q`yZ$qlHVkQ<O2QX7*SlABOJBR3&`PW^)XIk^S(OL7ZxH-=zehTwM8W@Mpl$wIr3+mU@)kI=5vF66G{4%Ck14&>I<He{h@vd~s!q3y}7$?kgE^Eg8N$la*jsea_{<j&MiWT7p|LYtF2lih#Y+#_$znM<KfJ#yQWxflAWM_+u(z7pEVqwgBAZ-svB(bs|-P(Rd4#)jbf)OuRUSQ6|WZ-Q%6-yzo~*Py;d7Fvy5gIt|jnOvP*g<64Jh3ri&NA@OHq?RWOeUU8mWpYJwRjLoUD)~+78{{|1CTdNxiCl+Tmt2>5sY9(zuFZ3<!>GYJYVe%hbynvwtMi=QZK%RFR^d5UrB)={T`|=aV;O?KW(fX<A$UGR@FIrbg$%)S8G@%X1W#lLPGAU*q1wsaT{qKDUE#+N+>RmmbB5p#8G>st1i#J@{02ktdkn#!Fa)<^2==9RCtq;2>6R;gqCO!1M7~WG4}shKS@5saiewRj?@?bSixB(^wH#T5;C$-e8d!wj%hbE%%j9#^pULOQxeUQqT=9_lg!(i23AwTt^e$P1;CHEiliy|A8c{`C8!-eor@l;XPHsxANN!55Pu0lv$yKQ$*H!tm;L_AvWD$b@U<kfOy+9UvhJ1~Di6QuuD^5^PQ_ql3lh0Bwkk67YQhy>}Bs;0M$xd<s^;dEM`6l%q`6l@~^%wGW@>Oa+`6~H5^)mT9IgfgdoJT%M%_W~CpJ3!NAGsVirx;h5Klj*j=Tq=~S3IMZ@`64jixB(@^$A&o;968M{%SD<e?fhh`~|rKwGp`kxf``Pxf{7FwJEtP*-WiZHj_W5RwaK-u0}0Qu10==D#qdq{P_>&;~B^3ed;yxHRkR<bN(m$LFiu|{qh(4O=z)4KNho}g?f9H^t<4z)YrU9#);tT)OWl}#+Bfk)Oube<4|w`wYFEuxE1VVJ4L(yp`IrHLoVY5JxdlL_*LpfvIxP|sZO$!#}a(R6{)V+!4SNXx`w=xyomZec@g;=>SFRY<f+sp<f-K8)D`6E<k{3M<k{q9)I;QD<aN~J<aOjUR~)3~Qje2!$rl-d&r%PO&yr74w~$YgbEqrGIpiOyOUOTxH&PdqH<H&=zbCIJZ>6pwZzX3?Q^^_RW7H$$W8^ao!KWC4v#2}BS>){u!K<k&$*ajrsf)-<$+M{6kY|ynP^XfokiVu*Cx1<zOr1@hOrAzvMxI7qKwU>(KweHwBQGa!_9_`4n;C+4@!WSYAG_$g^K+2-6PoLhPr>J@7s=<z7Z`#sQO}Yuk<U?2lFyM(Q*+3t$w#R_l8=%N>PE6b-bY<e-bda|-Adj~PN!y&)5(Xa$H<4tC#Yx0C&+m`_dMn!kN$b;DRPP{HhJV~6Uz!+Mb0CiV3|w&yA<*s>N)Zr@;2&e@;35X>QVAqvV&@n9prDR`^evt=Tmo+=ac7A)5-J53#o_63(4P6PmoXWd<Bnnh3<+(Y7$v!966CZnjzSqe>;JHr;{gAXOJh7XHqwiXOe$l2tGjFPd-4-re>0}$$P0g$$QCjsdLCeCz0opzoL#Ke?=Zo9YY>ZPG$&BpvIGh4kag$hf!;ihmlPT!A~`4kp>naxIDcVy}%*_e?YBEuFHP-fFXDQHIAI^swdSI>8{v8-9k+zZz2Cc-ADd`yq>z3yq>&{x`(`uyn(u#yn(!#`XhNWc{@Y!E{5PVhT#3w-Q@k`0}R0jse8x=$%m+W$%n{Csr$%B$w#QEWTDyQ8`K<XHaVL)&0z@6@W^`xL-1CH;5F1O<Td2Q48gI~AIP!f5bAnz2zeBB9eEUa9CZVE9C;aaGkF<#BXv7@JNsrMLvRX1a3(d4oJl@L-A~@nK0C$`e1{?UEidRnvIxN~sfWlS1b3kxC5sUJKJ^IM-G732vfWwKOmZgMl*JHyoFVu(>K*bOw(&RqEcjmx!7ZpQ$t}p8sa?pO$#tmjlZA>l*Wu5C3wa(n<U;achG2u5LC)ZqGZ=!mQP+^Sk=Ifelh=}$Fa(dL#*#;qL#ZL;P;xMJ6gikYo;r>^j^l4UL-2CyM)Gp<CTa?K6It|aFIV)?ux@21$58u_W5@|CGnRkXi|kMRn(R*=ME!<5h&+rspFE6gr7j{{$x+mW<S23^buKxQ97LT?4kBBq6Ui2Ge`*3bf#)lDfGY;Oq9;ReU+M^QUvdC7i5x&4PMu61PL8I|B1e<QQ0I`xkag+|vQAE<P9i6g!>AGDF!B&r^rH@?Mv#Y+;~0XcP$!Y6kmpfnkmr%Vqs}3JM_xglMP5Pvo;sQQJ^5Q|68T&5OzH^oO!5TkVDbcVICTIyoE+$icvsk5F_Icc9!VZZ9Y7vP?oI7U?oD=I7lM0G`;vQ*`%nYOeaQW(!^!>07HYIsGHwM2QO9T{<6LkgRo6<c3&By;M6KjH5^SZ0X(iX4;9=AuTFG@Pc#u{yhTPY+V1J&wKl9;F-<_X+%%9Mq9{C)~d<%{9$bTIBC!YKjbqe__@@(on@@(=_>UZR&<dxJF<dx*r)bGiw$*ZW}l2?%()R|-lc>#3-c>#GEHJm(+oJ<WQ3$>BO`n}x?YxqKA$iC!O)CjMV^?$*iP(!>*_6P*OM;+l+vX3D64eDU8lD!7OuTulOO7<fJ*PvRwO7<)Se@G4TD%sZ%{5dtut7Pv(a64+GSIPc}U_YL(IDZ?}kL<@Xf;+ilxGNe{`;i-y-=uaVze%n{ZAPv{E=z4lE=zui`Wg8pvJbTl*@yfQwI}%_a%<`!a%*xAhTxH|h@x7lgUD8LAhjnskUWsuhCGnmm--pGFS$3hA-OlXKeZXTKY0kXBY6mU6ty3D6giwaoE%P$W(W?Zb|MFpd%2=5wF$Koxe57gYGd--<O<X`$rZ?tHE1QW2*JNo%aTP1enfqVEJCmsJs+|cxeE0oausp|YHM->@|V;e<S)tX8G`#zN0R%HL%mAIN+?5ctQW2wp)u4batt|wY9&XIL#Tn|5b_A>K=KIkU}|6TU~&MpH#vZ8q4p<R$U)R0<REewbrd;_97zo)N0M#SXtIrLXGAj}LW9Y%WRbt_UA#*9l>VRoH;yI$#5#_q{7)VK{V&x|mpuQny{oS0A2N0CQdWFNqm^>~CmzTL#4JJkFX%dPr~'

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
