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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_003.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_003.stl', 'source_sha256': '0a49fefbd9e27cf27bddd77804cb61f62797dd5529433f571a745934efb21a47', 'input_faces': 816, 'input_vertices': 624, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4183112382888794, -0.375803679227829, -0.49999991059303284], [0.4003421664237976, 0.3991457521915436, 0.4887075126171112]]}
GEOMETRY_BASE85 = 'c$}r333yG{+Q;{ywA9?zRKqcoL@HvQvduH85>(X*V%8#t7`x3gMMcqalu(^aNeIGLHIG3gF(gM#HN;eNsJqvC|7)MUcF+Bu@A*FWdGG&s{#obUYp-dK=ibn^+249!p?_tRt?O0<EA<UDB9HREGCE?!$bo$#A_Kn|HrAmO;6DEcUDBaT`_S$VWwbKBQs0QkJ|imCb5?55uTG@^XQh5$ju<&2{EJ>+j_4b~{1)LuA|nhxazOa72;+0*TGeX=ID@MMI43&)kN<KTRnWdWaA7a2%jRO!n7YP&e{!$Yf2ZG2$zM4`Dz8P<OOSk&7rwIcGr9b@H76xsl!vdc=qi<0I(wo*tUk&MUs)N(eUD$>RPMKXFwN?_s~k(Q`ud76<bN@ht6E@+<cs``9!zGwx}vg_Uk$r>!0NlJ>`U?GE0^Z)^XdOMb~4w<Qi+l;+F{s&-Ms!QN=ogZN3@{!6h6ueUtNALO=^eX6OV^jd{IxkFY5U(U$lRyGfMJB`<Q;FT)xrf$&zoj=hu^Izb<lLom3-+mn)O+5cijpue=H(zeir~Yju*Te9r~Eo|=2(K`MVvs=wBqeEnPaXlHHg&OMSZ>NCcV``WjArSeK-p+w0y`(?^*@)NkPz23s>sSN11ljm<wzFsnx`&w3i?kjh<Ql860sGX0jOyK^vYo&G*^UL&Y^G;8jDYct^=OVSwvYB$beSVqR^A}BOH+|3;l-K0_RsD6z7yCQ$;9j0@*+{9LTF*Ay_gZ~XUihIS<a!3ZdxG)|m+Kjs3;tlaABV^Aaj2CYEZ4s%`O2~gsr|JtvhjXV=SRrx|8;im>;Ao@_SY8H+eLXoDSzh81N`r8b}X^_%H7$LuSbW<<J|6xab@P|NcFjUgz|h=`CG}qGgR{R=#I#bbt&w}Xvr7(;cL+W^89r*KWz2&3r%T%dsX1RD$0v~Z~8))e38G&7Vaz2CFOB=tpa@(zH(zQ*E`94J<^vJ#eOwj6Y@X!B9Feb5ar2ATPK&7eQ)_Zw2qa%yiG1I`=Y$IG>g{3D#PQf<?X(?U$OU6t>adGFPO&XQu4*PRYnT`4)>iw5!<bKgs%n--EQ5kI^$-lG@ciqr1AXCa_)<DTi^H1X{#^RZM!e}-SiiilIrRFeIxhvX{Dt7axK}2@<pUPu6?7)?^;Bvr)LKF`oiy0togNlbE*7f@<o16Q}VUa(J9tETK4Yb&uMyI8gF+FQ@;ow<I4ST%q8+0oTu?qmyaLyK}nlW<H}pU=6UP*@s=lF&APJAT3($KNO{WM+GZ^;d{?>5ZF2ci=dJzaJd=1X#NvzoviqW)g|EyhO7*ESKhC;c;k&9Vjk9i7ne)EfZsP(rh4}K-L7RCy&(2PHY7XBa)qmFJWNDn7*-G{KjC`{nr;)GC+L$bjlccX`zXHh@{p*T?|6zSOPy3OSXGT4FyGfDcX9i1ooQ)e(ea5CGS@%o5f92v{t1s4{r;9H0{);-DWF05k<61VqHLXi#`9n$8@!%~l{9Eg+<+Z3i+;^9Iz0F$Q>*t8ImRF*F;J(W*A<kM}_?q9oI4S>_8MNJci3zelB1vlhD-%=s-^cWp+DH5JQM^yTXF6Yp^en$5YrnX@Z^rYeqsce>#UuRk(stb$g=o7c%Oy$u)f4`xOQ)@Q-05j4e81l!Uu@U8i+p8m@@Z=x&$tcT*H8C7#(f-@^}qk&<JRk6;lAtTujy9bJRi1|7vn^f*G_jkM&kj;sTZHvd>SXByz6wkW7csZ%6t8X>#XI~(<=8p<vxhDmiPL_Vy)%fr%I6TcRkKpUigattvG9W=c(sMdA^WbyR5$F=z}BHc2J^v^Yhz(`4c|p=XK5_Be}2My7>p+pZkw4^7b!z{V*?gvg$(m{!a1_UL(JFCGI=#2|x9)HIF-UCimT+lCQY`B7e>-?rVoyN%`F+I&$CjM=Lr1-45JWhSZbtxGt5T{F@5zw~iC#*>OH!ygrQ+_v;B6R^L3nz;|sbu-`f!)K_IBU%C4+9be4yxhX%^2XA@uwX7HGtmV~BIl1pFUnSOB-s=a&TFW~(J^r2N^Dh{0EiZh{|ATmIdHuIPxvw_svfJuw8%pex=0%I^`$By9TC2go^LAdpUYEwhb5}a=hnOhc+Ar>B1-Y-ZgO7f6o*~~eYp`zZFVCWk%e;KdASu85X*&0v>l#S;T~8KrU;VYdl;3rdeC2kal;63aC-+@Nn#W4x;dwrqr>2kb@K0if)i=ije6>j9SQ-zs4ydpDNWM89%<^?9Kh^<ndGgKifbz~FHK~00nz7dMUcYXvwY;Zr8ScCNE5uvN3ttVW5^pW97cNMC%go(YUn%isi`1S=?(qK7^1a?7_4})a8GJkN&H0!`<<)#owphoH+J5DJU%u9{(jUCPqOVKab^7<Gah317v|Z=R9W<`si|u-zQ+Xxg&n;5Ff097sE&Z_Mdv4dD{CP%^U-az-yd7TN<-VRUg8XS&^ZECCk+0?%&VBvX3(Aw#h_{0l+@0zf@RHi6^v-mvFY-8_Q9V8Hc9-%vUs64F_@X{yztmqtr2L-vnw0<U>~*~SuzVAF{)$g1PX_#7@=m1vdQ98Rn9O}G^X~&x{}#Od`r1BH9(Up}YM=CQDUb8TmsFqh?ouAt%iqcOgpr>M`LC1jT2@W=H#eku&b=|+*Eq5JTE`FgIMLo6M%UGcBPa3wx$~OZVc>(QR^K&sEY&}GE%((HH)vk}e2n}$<t5)arUm(vZcO36SRY=5((%;h>yHjxl6|ZjZ{B2Bee-x~%VVy$wmjxKW6NW%GylZM`NcY8-!A-r)nBYXwmf3}v6t7f95KG~tK}QU`pV-f-#FG+9#{G1vA*(X0d?bj)+eB0yzlbl|0{p%v57wG-+FqYHIKeFWr}s2xF=`l<KMY*o$PlSP2*~OPM_n!?(2^dFUh_<9)xcn4|d<4$37l}Zyyh4dE0of`}XZ>S-E0-<<YZ>#rVo2{D0*s-#*q?9<BVxvA*&M-=4==b$Gn5JkF}4;(g^2zCDk9Jeb?HjR&)R_J<wxRbIXFfbQcwFD3g?cldn@_366HQu|EHL)W(td&~VeJ701L@3-t1C4WKB^W48yKTXQB<UGI5@uY^Fm&$*eLDx|yTAj7}?iF*>m~TFRx$}_UzZ2`5t8o$?AJg~9exYWx?p;4V(K-&rI&AmF@mec>ekso<ju-QW((%Q8U-HHANPF6f?nh$%ceSg}eRo0^$rr~9y^pey=NYt=j=zf|$ZzA6e0T4^XupO9lV33#<?j?s`_=Um*$<1O<5c6Xe&W8kzBt&I%Fm6F{i8R~Zt>*X+Q;sT<CMB-2l?WBV|sOJhh?df@0=4$`*kPqH||gS^DO`V11DXd!gtQPM)x~#A58e_{9rzQlxw-tB!9^-eEg`XCC*F!vN%3|^y4+pT7A#*aB2Lgcf+{v8nc<k`IFvs-{bBiDxcns=Ebwi+*dQ>ss8(}@#k3LyxQ)Y&nYr*a9?Y2Ww*7w-M5#wpRcO-^6~pyo`9axd9U3!_sjIdrSoCsK_K_V@k`|K`gHs<pTC%X>sUEYBkr5)s+os;J*!}hukyk->-nGs`Qmz0?3d}|{)4UjzpgtTgmK?~z2o)e>mA|SuXkJ_<9Au-g=c02zn*d*_-2=NJiA*4ldn2<OY>;&4f3Cr+%1j&ZQJO2ZS(3x>pT+Ip>|(u)q`J$s+Vih^QfsiXujM}=j*EQT{Cyme7U{gg4NgO<>K>2y_%A0^|i%Q=)O|Qi)6`<p3CQpcD&44DgW}?(tPn;ZcF~?ku+Z(m*MlmIDe++Cztl{`}oeMD}DMRk1KsV_nmu3&^*HZ3cGKP!;GcmH*3AyTHfy4%iHe*I5T3n?+$1#-%l|8*3vu@z8=tCy3gRs*iQLzeQMtKF#U$HzRNe1=9eoYk=h^UpWZy=oAb!bBm3rYFk`<i%_HRT`tm#yzWsiVC*z1N%_Fq4*O%`j3EzGn$(gnGkaawZ`)_t%8{dfTzrDIj&ttWhXQ*BU_&687d)g~L{+&1J`M2=(*=^~3!&5I+@)!O=$BXlGlO=!23Azt^?9Ve+UyUA{YHc6)tAh0W@aD8rJkP^Ube{9NAw54#8F7rM=h1PWzS+N{nsDE|-ar1+1)jG~NAksSb8Zy(UH?RK-?b}>A791&Tf1+rhi^7=-x>0Hr?tG@x0koyFLf8+Db>^ULj}5@dHJAJPiODHc|G+vr>K4Wi{ZSK?$g?R^SEaECF8Bz)s)ASzkC_#{;=1t5bL{q1!*3+73B!cqZiVBX|GSmDRY1AzNn{?=ZJM4nfqn>^8N6C`C^?^iXO4fBhfEjU%qcIeEa=*=ZA~=_;Zgxmc;eu-)UA~|LO#vFY49vsa9W^UV<MNT$lT#Sbfi&r8Hm8K0YUvU$~0T7w6HrXRN-qs7;ErUmu>Q?PhG|=SA+jwdg!QUtW6td8Xn~{=IvfefsA5oWC~r-P<*~UnZVs*?e=ox?7KqH{yBCL>Ha+<!?awZO?uF<@emfpZlmC8dDzeoMl*5Iv(bCkza31g0((&-yA2VFF&7B3rwKx;yHzQ&gJzp<9wGV-^^cpy0pK}t=DOPC(M=V?~d6@>sf(i^jx}Ju2}1Ky?$Qld7Rxhw_9Kh<;VRK^En`Vahx)r8`^wto}Vbc{rRKmH(ukry!>2JDY#AQM{}GA-~QaQa5*}Dj9E_marHu~<d0v$=aHImA;s#e+HLy#h56?te?}jgM@hZTS$*f6!8DH!*E}QTpI_v>b-&c&`T226Pfg{=1@*5I^uF4tx@WEZ>;CvD-;Vx+de+*%u7ZESpDLHnwVZEXduxtV-uXI$>Q!Pr_m#;XlAfGQ=XE6yQ~BxTDDS~|dahaODb;i4sdG~OOJ&jbPh6nm$?fP1zI=0@mimBy-~Cl0Zx7G$CUpH?nx128QxDMg4=$$XzNOpJeT4CAc)vK4L+QNKIf3diW4Kfw#W|JoZ<|5SX>grr_s#k{XVLlb=uUh*xYGL4`vGOP)Bay|pX7R}4j&I%nM+j98WB6J`R%^Bzwqtv6)0tIQU0;b_<reUpPVB<^PF`&o9`{yeYF#RZ$U5fi1OpPxp*%^_?lm$yl$BOKIwf4wd~t8Udla`-|H~_C)=cUGyNCx`yOTUbKiX4XXYW_e7<8VFMPAz$`;0bBHMc`rf++X#pav)Tef7f)NbOwf$(kb&nV?;Q=Y&6qT`sj4thksx!z`JG@m;+O191~_s$OFmmi7q&KvwV=((_u){XTmr97Umk5Kt{evtCGrbTmKuW*z5?xcMD_^4kQPwydBj->l#hg0eN_v#b8r?s8??o;#l`GO}SJNLCJ$Ef_-c|4DLsW`1~Rc?@v^+!v&P5bMYJH?vc>=(a6Dc17tQ<-%C#IG{>hrXus=qr=xy3)Ua<SXg3=shR@Mp7RA&|`W}!oN8kuQnf~=daf)()~dHFgZ_JOPZ$vW2HRi_zajTm3N;G<nv3txjx0({(9Sbe10pfe@(Hrzj`d0_nT66la$AGxENp0wW_~!U%by|))T(>eYW$oK2$wR`&DImoLruKr{DK+*7ADQOHw<S<GJcJ?z_ug*=Eh-^{;P}^4z>7?XQ+=F|B7+Z<CMXxOcm<@6CT(ZU?d62HsDx&Qnp|>x=grDZkSCf!xjy{Hgr|pQKplsW%UN^ZiM*XJ9^lJ?7c8fX2z6o9H+mSXT1&^jLZi@1q)Yzqn2$zmKb{qv*O+_~QIQ4Wa8;_~v`;pPxNs_09L#O~0XBpR^%#zxt!@lz;tljn|{iVgA0W>6`Dt%D(xYr093}=KJa$it_u*!Z+XBxA{t$CCR>g%^Bs>_Y^#q<g<LiINyFwzvI4qHOHf4KK*+i9Q5VucTXJfS^qojZT_cnJ2YvvNb;*3Px0j|WulXP`I>W_PhTmNl;q2I7u@C3*K;;H?$gha)2FZ9t9sCvZ{An2`*$LI`sTQ@`{w(}<g49#Q=Z6~bbfwt9lzhA>>5Dj-DBxJmjf3QDbGM@JS$19==`MGAgVvsF>}3bKZ5d$_kkZ`o!%6cYMt-eumGAb)y7KmQJWCGSMtsKKY{SaQ~P7xGq+n!liES;wSK$gi+OGOlc_%9Jv1}V4C*heW9IR$+ES?<+=naE`d=-Y>hn=CTK}>BC_(EfKi*R{{YUHN_FvM8e$Vn>d?n~7DZg09v`>DO`b%3ho8H_1FTN7ARcaq|-4?#>cN0ob9NL-Q4>#+7BVOuXJ>@1nCk)z&_N4PYZ#(Ri+QD3hgA(O_AJc-yq3}h&k4mTCm9$Kh#*f-{D&MXeq)YuJwyOmlkn`Alv%j!Dt3gMl{WaS;=#*T~5s&EiEW$T`=Q2a`MLUQ*YS3wE{Fvh^=$ur4?{?40<3}7vg3_ezn(bNrn%rL~uLs?d`vtyI{hr)zrvFfCA9KD}e=P5>S^l-W{xqmYzgH5zSbrK6px-xD|3@z0*&QYM=I_+VSE@VGtnDD`qgKzBCilxz`aO&AZNCfCsuxJJwvWi8RWF=oZ6D$5)jv$LwvX2@nPzPta~-Jel(uWOTW|pRsl^9{SlUOgUNz0y4thkBguPbZ{GFQ37kR|*`{0ZA5%p1mt4aBl2BFk1!Z-T`{S_P}mlwYi6u#~EgKBUCsXe{hZ7j8?@YUd!QhR#+c2a(`J%hVR?QG7MV3$-+^LLcOxBZS%4;~=3kGa0p7%b&+jax1I=6WdnG1C5e^GuZX*F28Ym?G`3*Pm(2kMp`3t8MkM`PTBG(ywRp6pMbPS2T(mkxO}B=@)MK=`1tZKcT*VIy<n&|LUi+b%JXBe}6jL$f!d@BkDoxg6n~6L2H8h81b<Yy%CH<q3?r3!S6xyg5Lw@K`?#?nhSj1h?7Q~MKC@FJpeui)}fogI{0Vkx8R?_OQDm&OTiPML%<WjeW6{zeZife)xe#=A3#fjndSq(aTx!VO;K`WBh3lU0WN@GT+oQ(Miet5KZ0>SXi;!Ja9(H;a9(g8Xkl<3@Vn3t!0&={L*EDI2Iqpl2hIh42U-aH4)|?oL2yCr7vsN;-7jRcMG+&a8lP(#Q4PVk9)j_62k9dRF$>0N&{S|5cq?=Zcq{lj=t}T+;L*@g;L+fw&?exf;BwH?;Bw%S&=0{S!Ns6Oz)TB)%Ny-b!iaJR#>Ekg1EE3SKyYUxE*o*th!kiNI0bwhdK7#dd<eQ1d<gs-^jGk2;N{S0@N)1J=vUw=;GxjL;Gy6!XlHO|><eSo*QJaILcf>A=RkNRp{2kVvHzE#>EOpkyyu|t^&Z;!Z~TpwIR{Mzp97zOo(7)){{cM={sX)Px)r<yyaM_icm;Tx5y3`OGNJ~8aTNsPj?lK?j^OUlZs6|VVbCwY!@$#_)4<bE2gaq)wj~ja%ODv4<siM~AZEch8G0U^4BiCY4BiA@1pNlQ2>b=~OYj$971|iAf=fZmf=hvmLrZ{*g9}58f(wJ$xM2DoxU3N$8c`j=xH9x3aAj~i=qKQI;I7a?;I7~=p&Iy0@KoqB@Ko?h=r7=v;LXr|;LYHJMkE_?%7`-v#z&wB!3R;EvA+?eS^pcM8sTR|2-qK=>l*!D&WJkMh|A;i$M8bIb@92j(Ux_Ls0VETo@eBmZ^RGKwcy=GBpPuKdLMky_|9P?jzEur|1$n|+lcGX8{kikzx6O;B6Je?ALDOt6si|fRwu@8gVz`_2Ravg$B0ZLc0zZ7HRC&zjpzyO1+IsE%u+~SDa2z8Hcsl4anSK#m+`l7BO;*vz@3f1g*oVZVfYT?9md}h6x#0u>@(x9jaX#Fdguo5_r`Zt8SyQ2Ie3Bbw}trLLVSnuIMl5xv>TZ11KXE>pl`s}(dO~c?cjAr#3;0#7;J-aPa{4z;xlkBd_Hb$<Af2Xpr^s#qRt1Qhrv717rUW};0UzgSm-!#SL{n?Xc+h{BXSrK1Puls!5I4<x(YlNImbYwz(M$K4QMU!7?g2A!@+Yf#^yoigV{LMFjgmFY-z~Fayp>dz^BkwYoRgVYv>EsCye9pIns!cX#bJu1IEvccxgl<2Wg0dI3C~I0ZjnE#P|+D`B(VtHe!u~`g0BX@;K%On<Jk>dw@U37#IZ|4Q4r?BQMj}V75lEwZaWu17>RkTPyBBGr?=oCT{2&@F;965;_vhzWV^*zlrv{1-%Wv1-=W-1ZU#Aj2{{C5cwX$zmI)j`|<{=U>$k`X8oEIV=+548<?pAW^<d(@paG`umk1Zg605UG5(feL@ab0I2ODL`aSpt_Wv66Pw-45W*9LWItv`m)-sG4rVYW3z-)XmeS)#p#E8a5G=(+;Hw8C`wg5K=w}iF=w*<F_wgI;WcYwABU&Fp!fo6d38g;v4#64&x_#XHn^a1!G_;2WA@ZaEP(5K*M;Fr)B;CGCuhJMNc4#vFijkywo&ugHQEOU$LF$CjP&`Dr+++geGc<3tdDwG)y?ExMS?uL4>b+Q(;o5Q>I)Uu3Q#&zIz19wB7Ita!MpuNBiz#-7y4)40dG#uI+91fm_U_2c<89W*7H66it1N1a_1NbcZ;4J#*EPT;lr_rCM(bl4WPoV!#pxwoIV0;gH*x?;NjPD{C{|;Ra{vEswIu^VPJQ5lP9tr*g8VqJy4b0|s9L9DW#{Ctnm#Y;z=CJiP9P1y`D9c(n8fE5!=R>2wY`tOY??UK&@O+e62ptDr2wsG>k*$S$po!o;;2)tIz(0Z)Ll=P;gU3V1fyaXfLi>RSf;%AkVV&rQ{TJ&-IM$VLw2@e6dSM-6+S9Tw^~Ac>1lj}I6Wjwl0y+{r0z4Z!7d#hz#CRrj6?8Rt6<Dm{tI^M^(Z_KJ#@nH5!P~(J&=@c~ezD`(E@%Qc0cCbUH-I;wpBOuh$gi+lnxqB5ITU`#Qr?0pU=`O1A<$6p03*IIVj%QO@LTw9LF8xK%MC3G&JE59Eey^H&IT<AE{L3rOQX&#cLgKZE!O~ORd4{fHna}7Hkkb{9I6UkGc|zL2iHfL251+ytzyu3!NtHu&{nMNvO^1jvxDD;76BK*cNvGEJ=;P*1GfdYhkg!j5AFty0CxiqfPMjH*L<%Xblu1J9|wJA!8n`Y1shS_h)U3k;7Z^U&=0{Sz}cbMz}b*LJH`PU58a{tz}>+eFqYWZ>IrQJ?g{P%?Evn8?=pVh*v<!RJyuBfE5uBH0{;%)2>k}U5xfLC3A_Y65jp@o5!@f+qCdt)fB1}9ojx_9s}X5ztQ&Q@pinR_gJ9eo+6>$r+!xvh+!wqAx){6!d;t0f_yCx-KhqNE7k2!e>Y!sXQy2KDQMVTgo#!!q4rb?B?0m}uy$XJYzrTb&2eaey3mlV~o&lc)Z-A}`vvVhQ-uw>qZ7^G7hby!OGyPQYuE~s>KpTVEy2{RhXF_Ly+Z(wC8!^O)`OtaL!Qgq|8Ah};+NgyQpCA}_f;Izp0(XQq1a}0thC0Bl!KIDZW^CgpBYrlbwGji1XoX<hA37V{A3O{CGx%rZnT23H6Z^n)BlIWmM(|GPHZap2;GN+8P!D)NI30QuoDRMYW&3v>>HxD~{HKG0@hfOUFbl>X!D|No2wWT50$dy12-*_d2;A6+rqEW<mf%+4&d^W5ox!~kjKiUwz~NvQv?JIB?g4EL?g8!sEe-Ah_Jgvv^TTJxx6z&+@NMu_=nn8zZ~}B2H~}0B{TUn!{slT4{0n#vbO3k`cp$Vjcp$iq5tX5ppsm4`z!jmbz!kw25R6+w`-5A8`$1=cXJJhDLokl8jQa@aU~mMu9ke~z59$wX5B3KKAQ*Rq4gq%r4|90elwk<Q3yrvD#BL)lA{fU*7lId}d_02jZ_s(*-@rdYXMmY*1pf%$1KkN`x*xm;d=8opJ_o)Gy$)vjC-^e>5`ys+=qvCQa2Ax!+bn!$?2oxz8|)7bfHndLfNMY-gKL0mS>|>v1mpTfG=MgTHU&2aw}G|-w*iMiJA=c(eW1O;eZWHzjE6wO!9&1<p)T-X@E~Xp@E~x1XcusQa9^k&xG%T~l&uR*@R{)w2kBMt6Yvda0{8}a7c>^U3mgai1sn(d6*>p}D|jw+Ab2i#5VQ?=5V)<wyLPliFs@=mL1+PJWpDv-erP3desDf$MQ}cFUT6hyUT_`+<MPm!;PT)W(0*X15n!h6z+z2lf$&3)JkWQce&Bb(xuO2x+~8c$0B|nw+X%*i(2n3h@W;?$;E%y0pbNnxz)PXK!Arq9^cq+PvwLi8uCa5w`p~Cf7L02_A3MDBlyME{1BZ8BGY)`eI=t%uV}Ix!hj-mzoCWWi!@JHfz5>1I@UBaY#oERA0yG}X^f&MY@LuSTV5WP(OwWP$f>WTE!I!bU6zB!;Y9m${F#*9i3K|WL0!JD#9Qrjh8vHdl5y5yLbOm@H_z-k8_z?K05htNPKv#o*0DlFY0R9U68G><lXcV|RxC=BA+y&gpvTvObj6;p+038Y)4ju|#0R0-g0K6TV2;L6PKrp@!-3Pu8ek&X4AutQZPUulE3&s_)dE1UL3&xcVt&)v237?stgkZc5`U7|!cnb6@@D%Xp(9gi1gX<$0*M)Wm*9F&vb^+G}SBG{2R|kIt4F!J$uFABnBisAg|J(m{g!dnN-la(YM-ujL%CF5?zuCyhWxhlg+BOHf_oHMp{=+W*>h@-z{sWfx{Lu'

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
