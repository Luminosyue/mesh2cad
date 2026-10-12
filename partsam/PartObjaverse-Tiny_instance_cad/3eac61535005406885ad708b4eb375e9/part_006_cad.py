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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_006.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_006.stl', 'source_sha256': '2058fb93b1b4e11c6094e5f873b7a15caffa074cbef056e2f58cf297c4b02422', 'input_faces': 698, 'input_vertices': 480, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10973584651947021, -0.39474692940711975, -0.0829688087105751], [0.08130645751953125, -0.3359781503677368, 0.10438943654298782]]}
GEOMETRY_BASE85 = 'c$}qt33N^8*ZvVx%qc3U;Tmdgil#(O$2^vpW4?%(f`}nzN6cynB7)$WBgPOC5poSRt00J>+)k#VrmCv8-+TA-96jmkf35%eKEJisv-AA+`|Q2nbIyCtdCy(-Z<94!VGaMvXhVwM*<*a7X>QA_71qWL3>`CMz`)TyBSI!*(Y%Cr|1)t}yDne)ch91Y(<W6695{MFXvHsV73&50Rjg*K7&J0;OlZFmeMg1{4s`R)`vs34sQA%?`-Kcte^>JLt6t6aS><ZBDYpORzufK`ws@zcDsbJ8&q$S`qNb->cqe)1(CpC--F(;MhunYLi{C<g*D%DB*G)dPFycKDgm=ayf$z9tLh66;&gDZ_Nxa=(c&&v~cs=~qhExmhY7SltS~c3rJCl;H%ip01lmC-%w{fNDd%a6`|7}coC_2XVE6^uzC$9xkKjNA2&f!O)Q>1q$-a%gf`1jSKfA5m;+VfNB>tx!-)c@eMxlJcoc}KnJqGQi9H%@d0pG2KE9mxAdPQ?F<cdpKlc^kSL`mtf)qw9fxv{86l$7#@U4ICucI0ktOeRECzPSFMmK3*Wa%li!aipaac$~(zx3C)HI7M%zF;(FnY{fkk5<5{RD=WN9LPuVVf(NNSsX=&y<$!oo*BHo#=qhQk!(4R9A^-R8rc^)wo$E(x@)SouHwcxWp!t0Ncg}295N8aY$khl6u=og+HD0sRJ=BM&`i8p5XL!Z26I{^K*TlxvUs*b#u=A)jj9&07Ob>+<S>@$3V@Z<8Mp2SPwuV%sd@NfRz`7xRJ)FYDD)wI+O(Q)Jk|JOy~okO0+2!A#Q>dE*G=hfq`(^CI~H+H|p_4wKY$Gy&O)c^3>`qcm6wWdD@36B5mpycau75e(IvH!*EH~V7VHoOG?^G3|));^g3^S^-qJ4txG>KeqCeIUF(G7jgDIiKVmAFs+hpXDzJZ<Lq`-nY^i;oDshURx4@zD|wC{G=U4{ONQY$L~|72><Rd>X~;Oyxw%3@H>Ve@0two55mS<c`eQfe%vopg%9tF`dgg=AHRQ%@Vh!9udx&JP{#rN@P^=P=eQyH@7i&Fk++lAHq9R?xT7xee!T(LOYNU<y^z<vVlWQ}BciPF@8`!ATvy_6);?%GZ=D~_!2D$M#XMBKgZOM-$op@8=+n&c4=$l!uQn}&_o<G&w;zHp)D-pXDv$b~t%c6`q8$Wp+k|&zO~7&A{WI2$93>H7HyU-mbm9ET{Y#R>J>3tTRA1=N|3P@|&Sm8NI%7G`i*(`bKdpm)hvh4*ywUM4j*I6C9IpeX!N)%VuLU5UyemBg`nHIgf=Tg7*7H`2EihSh{I-Da{ut~3q}sUN|HW%HCyul7#>+I(cRZMm>pgju@Xp3xL;w4Fi2oO_*J#B1&NS#mAI7}3O2%~*5rTOz*U8a=IF1F|p|55upuZ_RO!&s1p-!%!`npS8w{syr?JTbM+lz4ClD9A3ih0g61oIj4C{f~49wTqS<w?S?x|f*gdVE=ay6`8y2VeR%>Yq0l`sD58wKokz1Yg_{-dW)|*0-U)n}iR&0-YU~5x=hf`v2r@J9`MOO@a=e6O2!{L|S=!@<#A~M>>Qr8wEb=D;(c58#Y>bXA2kB=U?M6|819oZ`et69KFI4th_eu1lIY&O&r2+n2$QMuR-30Utk`}P7~f{e2Mzge}&GLUc$SU-oSj;f4WRCEdV;74U>4A#|gyye~II=Y72Bu$KiU3ZHB&rUg7*N*9Uxh73hRcM!cf}=F`ZAzKS?-o-FWze!%kslCRq;oX=Tzl0PoI(e4S(f1mMd1@~+M?>8Gdo`Vs;ccJi(+0Vf*KZU%v=LxT+EWmkkehlV+{zUM+|2hX<+b22+<G`01j_aklKlr>O!TX)$JS<x!Xdi@n%yq2BTFn1}zQVgcm<9d8ZE(Kz_lM5(BC>AlySm{#$=e7zQ*J@0!9CRPS6_H@U2=Noht7k)_e;McbEBSO$?F8`y%FBIdlUGlOQ7@Uf$-X|2XX$4&56FEw+pX-lZ5kUQ8`{m5yBhhb$Tfm`hB_pIu+ic&I%suth{-AUC(vs7hJYa^j|l|`K(V(5`OTQeb)0_KjHv?Bv^Q3n;rd*XbZmSXZx(@v;DgQ2ZeuHZlCqM)gvw=KDsdYk9y*{uIFzDgg@y8-q`~Bk7gxVd9!})d1dg;vm@_?#W=4*J_jHAXm6(TWJZ}pEAQ&r1?Tghqrk7dD7>w}Xk0JT{lK3;C%nP+*7-IvF4e-D*M-(_Ir6?fg}i+3)xSK1ct;ZQZk&wxvCp7?Hes*zJU8C11HWOt@J>F@J0rulr&{>;*H^PT$opoc@H%z$`>}{`yA<&+wqBKf`>n=2Z<-JO@K_wL^ghV@Hhi!3Jk$=v9kBAoibx!<;`NcY-6X{Gxmthq4E=5yjd(tv>(5J}o_E90SIrGlk1J~t<h>jqyo2`<=ePE)68~3c=>Ihm=fj8jx5?j~YaxEfNyI;l-6DLP5AvGNMaR=(t-S4SPxR{_jlAT|=O4Xn*G%!w-^U1VE4gLAHC`{gNb0xG`x^6;UIlsioaP)e89F<>_gc?eJ$EwVP5zTPI1d|C1Ap_Ucp0}0>%Y^tG3FuL_rmL^$3Q>$7wFHthIl@YIgi~3@0kGpDxP!nNjC5`_XzJuJ1X@X<yxaJmqU2lfmrn0rBkAn*TSQ4UGzDFI&-fP-n^gcb?;&RYlTCn;7>SzQk!5sOl}!(Jr8Z;LXbD52Kc&fI6vPa{@y3TyF!+suSWBsU$6@1A><0~*MIr#7QR6N#PfN^-m1|a;U7H^G+3wez^Glq7ye0jy>WJ|^PaoGN8J$K)_y1A&o$pE{L^IN&F2$WgeT@DG#dK6zuU@b$lH9Dp!r;3Z<GN3<OJl6Ux<10t-1r(Pfze~zs=m&xK7aL{o1+b0_rSZ1U&D*dgb%bNy~vce>jl2e*gQ><Nfjdx|FT9@W$B+n1{x_aGeGeMLh3=&SHC^lhR1?oA({(j>^y(lPdqed7siJ=fe3mej<49T+nIm4SnO8)a$y`n(yPyljVFcZV2zxzK4FHk8!<M-zU62YcTF#7xN<CcZBff{oN7T8S^|h2=RQMa;+W&{>MJxdB3wYJqR5?9Xh<PX)h;%k0>L&jqfA&3pt@vuOQ<2{^D|!1^?h@=}(Vok9vNq1s(FP*cEdA>m48A{usSNc=P_{T;Blk&&CUHzQ5SV)Q5i4QNo+g8;&*pnRsK`Osw-BQP7VW0-pC%y~S75?*|>O|9bCMh=0`@$7kgf9G8U}_?AtCcbfOF*zdu&y)VaKA031B{Lh=<WA6&@;&ZrOC_m2I&Kra`?<3m8!l);970x4b-80YI&R+>{uG^0I0O)6%EW9&$0Ot8_1@L<+LWk>>Hhci?Q=Tv6JTmw^{Qi8lKN8-2e%6CCzz3!XZ?1>NkKggRXtVIn-fOY`pJ)o+YZ~|^dxY2Sody3mUDhpI=hLV&$6Bl#(Yu7#Z_mSd*mEcNrt5?^B9Gy?ulx)5zi2~v2k$SAC;9f_y8cjjXP0<f7quHeN6Xl3?aMZM8~Dy?n{mFzVV(cwHT1Qk;JJU|c+e60@3sl=;Qpk&Xm0R3Rw16x&$jyg!7pep&!={-&yG>`@jUw2LwKF*sw=}U0e#(;=U;Ojw*B@Pyu$#`b<(zI9rX9a%k#LoPTER)L*H|t@aDQ_pItD)%4-w1L1*tG%!6k;#Lv2f^*n4m=HYa@JTE)A9y*SFfV`D@;5qvK+|2b<uO__n#U8Blo#r90-v)UfGPW#2eCjn^rx6u}w{xAeCAQ-I+f#T)_}{4K^$gVGe=SCE%s|Aa3`bsVrSQftcQDVFBawH{JmJmt)>iUs=mbm@-p2jgf99vY@UDWppws3Z_@uvA3(s}fKGTUh(>!FK#=-p!SH0iSSEae~erfJwIOYc;K4ZM_2KUn(FXQ)eK83f}{Qg>|^VwBGczs6d^-T58%?BOc#~qDIB0jo{yx+fHCkOq?b=XsQC-*;Hhq9p_$2obQHgev}T#x@E@Vu|tMjr<6>@ZdSj@l0WJl&zAm!2Z}+|P9R27|W`lJ6DzcbhWzW&drW#PNCNef{>bVWP|R-`3!J)Nea1`^OIM|2X;%hQ4ze_LY6`+-Mu&0UhTl`Ho>++l)Gwi~{et9BRETT*1Y_>&u0=1w}$Xc_#UB!40*4_Eq#Zk$4WUJ3`#NV{Q|iR|#R9&!J=8yt!{?o6ryQrmq<%I=`01b+mXckFU4vOX>N};=F2-gY{n&-c|Gk&O^^<<mbqKt$mw@=c3o!QIFvv`^V1tkI~oW=E&=4D7<ZdCFFIcVm`Gg!s}BvLBDwh>s%%Ke74{W=+uc|-omo4?C2YT_?u;LT^KE}Pu%tv=56N{9{0p)!iQZ)UvGk;Z@dD}?_Z8*cUfm`L-ft-{cu;VCquD+HsILxOvll7Qh0l%9nhIs8TF+7D7<6(HOznR8;ma-E`5z%g!rpLh>w`HT=e<A=6bpi^OII8O7wsJ0eQU&qpwOn!aKR|?JBj4*KaT3b$(}ge?A*4g*R$_oB8^+B?)gn54eU_N4(eC6;coH`;KDsQBTq%;T>g9Bfjw(@By{uyNAyG^Y_>Lp60@v>yo2Y9M`>N(boBN-C7@S<=?L}=Jo#IrF>V^M|HyUgV7%EK@ZwvpT5#Y-1p7>inIZ;U+Wr`g5#JggzF@DyYE*L@659i@#F6ZZ%iD5`HX7={XJJ?AJ;iLJ9K{Vflkt=*niEA`<?5a#`}9i@PR+$_*STk`ro`>W4$iyFHVDx{ZRHV_44uP_tbgb_dgci-t0Q=Uq2Z*E-ii6TCcnJ$Lmc;;mz;7t~|%M&Wr+Iqb&G^wNU3919|Va#Cp|u5T1+l2=E`@MEyRec^|wjylrhX=DB16#QPP;_ZIFG+RF{$ePI^(TlUQRLas>Roh@^rub4E(?-O3HcNEVL=5tHNGvSRm1JAJ+l5t!H*Oz@<=ey=OUQfC~KX91vj==5LGhG+tjeSvg&pq=ubi77Gr+ysr+EyU`UBG&&=j1um`DaBQFT3#ObF%Y~(s*BP8zsD}<q+f@d7k_&=$PwU+sV*rnQMdS+z5lt&IIhoE=UvJ{7$W(xCNc^k2eaQn1K6;-&~xx=gVvoow4n(Pqo7reVvFDUdz!N@9&RFAil&V@TC`G9?E^U7sv00@XkuX(5e2%0V}T!90r|Z^RPb|{2h36f9c~&c&|(<wOMq`{h37ubnKmlw{33)eUDEPt-QI9r{|lF_sXOJo2}QoBlL6bGcVa}z23EU-=hA6Sj6+W)ERLH`x0*gw#ff~BN6i%P@MaIi-fl~-G%qcHX7pF?iAkfb^px!<S~z+vpgL0_R|~G)AEJzdZXLW4{C$@pH<u{{k~{{dB`3G9lf^j=KHm4p*Q%)UA9`UFT+(Ie7%9f+da;qFLOVQymRg<)H5U%^*opXp3jH+jm_Ana=jK_?-Yyg0$XF`Jwdx&K33xYIEnlC;$NXZvxo5dhl!Yn)(<gn)gpw~{*FexxgVIe3-R1{)q6h1JlKkFlfKN~OL(3Hf8I}c`=7g^^B@&@OY{}q#osx+-(L-$h4=+m!6)~C&WT9jomKYZI_lIHb$UI7j`^Nj{0z>|z&FC1`z_9m`xvjucTwH^9%}B_k+=6;4xPW-bAM(&zM~#X<34;f)U#&^be4aGzRZ2mUMqz+-`DiDZ>Vz*I*0dTzbK^%;$uJBZoS@(jlp~5@6P3fcV2n~zGdlXiTD3Pc-P#G$ZH#p`r8f`-qw04_);@7@%qrk8JUh(%P7P<=VWA>2S<wVj;8r>{RU3Qcj1^v(5W~B_pjt-@i-5=$oExe;u4(azfD5@5nl;!8xn-;F1QlnU8jXNUi}Wf-SHKI)qQtLUoX7y{qgKTd{0T=CA{&h56(ANI&{vz6kabh0{5c|`>;No_S+@=kK=GZ+U*OzXkX#AU5AjjS*<mx7T)|WU<+Ig{g4sDJC?V>aWvOYXQc4vexnxS4IT1&mky{WqXpuVo*{28{LaKk*edUJT2jv4qGNtP&G8fXUY&(E-#fHZlkwi`IbV3&sF&#LGQT(NxCR~WzZw2h@xJ<3E;$a4xOrFy3iO12$6`1>+Z>qZC!JCMJDc#%hi@~_&!&dL+jzg$9)*LS*hF}}+FE{(i<Nc9<h2O~j@R#dv7Y+3fIff!U<B1eJ>y0penmR?y3RFL-r)URkKKoTgjbWHbMOb$f21UIN*n>t`<ioZBdlL1zeb$_$Dy;YAaux^ze6+Hc;h=@k>Yav9lnv!H@`nVE-Ab{Yz6wYU+5;dv>wivn&DixqcIQU-~Y~`+PNjd57vb@J`KU~TDlwW0|i?m@3=6`bBD{w`=AZ-cAbcNiZ57a<!$?}ai72HGSLYdfqKl}iD`3e&>t6XoloQ4G3b-mj&6lcOa4yDYa#ThV~kvlya%=m@0=M6{g54jGQL(K>f}DT;hhil+&O~0=J&GBeIkYL^&NOV&uEo;4i=pI3VfeI;4>1t3(n3X*OPf4c|Q-m3JC8yw1CeuYcS8`&AeI-d#sf=_pzOihvIno6cXP2E^HjlfPQ!#;cYKNz>l7U_a&46yfcpbqX-;FpGMH<d!n|ZeyH%*T0)=uUB+sz8<VFB@0c+S^(=Fso_F&y>1&stqkjLDSXbK3L|+k4It#vaKxfYd<jvNxpTwnYLf+tL#BU10@!b-O`DwWg@ju)_J>z#k#}nWCZ1bxi@0&!#Z{G%;s}C{H?M{K`eyK62HI94hU-xFZUd%dezhi#*o!Yol2l}n^%5#m;yc_0WLTSu%DKFvmG7T{g=I<@ZJMJFJTu;k#h|e8>_yAs~r+x6;R6G>tVbpXSub7(PTj6=$Ft4NH4WK`03UqE9f_}7JcxSEpne~Gw32%$+4;}M*C+})H0`qffKKdHG4LWCfV_n+6HrmP?MRe#_OOW?=t#JH4>v7Sl7a1TJ^c4NhUc&1=`2&gfdm+5NQ9bDQJ`DZbb>(@}+!xi7_&e3TA>bz;;_sHZZrq$9ysdN;_@rKT;f*xm^@hv%JH}H@Q~fjjdOPoyz&O7$suE?nw8C0YKg&<I-K3OB{O_M`5Apr~`ssG9I)4AxpKgETo?>OCrF2dEP+3W3EtJ)FpB|d~)j`vmxKA<nVIsCAmZ9I6;~Ee@qTiI-c47<qL#aK?l4BTi7G}P}tjFzlR`#i~*2IeR-N&MYvU<eg^lK~Yp{y3MJN++})lk-jSd;#z9AhK;(l5bWg@`u#HJGa$u@L=Q)bu5mqhEqC#hJ@Sy&8<E$+5nc+H14#+8ooFJy&Gk6{*{hJr`$x#i{!xd#lO*%^cmCvk>zYVm)sEM`c%){Y1P;|E{t$Wf{aX^fxJsR~ALwL4T{}{)DG#8;Nu1U*(uf#2ET%%yo)*iT*<7T0lHSKZ=?$#0B)z7;}cXE>UkGW9D#djHUKX?0XZ({K%efvhSPJz001@u)j0Z-OAqPuzxeh4(2??e5Y8C+wYl0T}#Ra5J%AOuWXpI-o!!lzf@LNSxaIa`t_8xR^~@+PJb}R1QY$~4`Z&O#9;cZnX4UfDE*ey^e48XKa4Shm@Alitr^ptWBo0)yRj#6F#Q1>*Pl3yes5~mBetgRN9{V69Ces;DDw?vJ#N3Nnrk0r{=^FOn=31(tQoN={W{79D)S=_px;SZb!7p>&*=MbOex~$^ouc<7qJxm>daM^=tbX;nx7NP(l5rCqRdr_des^88OMHZsojlTi9YoGIj%Xe82x6{?nJCkKY-c;EI9@+rx){iu^zYYQg%bx55(K_?<l*b>^kuR{YYh7l+7bX(_gA=wz98?Gw9#on9Ib)^sh13dE#aIvzcoa@jU%`)LcxQMgJOOE-=?+>dj`%431rFsXdZ?M{<mdJ>O>Ex2b!FJzrpd7pS|Gz0F|%W{zm)JkNaRS&!S_rEH0^oy3*&*DIT=Yz1*9{Sal-l?^9Op+8#L5M^VCf%KPf%zWYq`g55poH(EU5at?045vSwnj?sV=+9-$Oy-(Ty&;SV<k%6G+C$iP2*>PV&nwyYO6sm>&okNIOzMtiZ-MOJ%rS*I!<jFf^|*aQ*#u>ih@<FFRu-ykDsdwHb;|ZAizV)*zgw9@**@Yn`V%;29B~c(Q059Fj-&5juC>H4`mxkpLtINglra;TYaI0)jM>JqYb>>|W8dpI#$eB**!L*vPG-*&+22I!?q+Y>*uR-$FLQ=5Ul{9g``eYRQnrD(i2i0}5z69-tLcBE>|145h~Lq_rR<`z?}_R3S8>cT;#v9;%(a}jjQ&ODI!9bi{|YtF63@|(V9aXfT1LH#j7jI%vzFSwVc*|y%y#y?h<z`j?q>G9n*FV&?k)C~&i>6D-!bQM=3CBs-2NkFkCojcKA?YJ*+XSN6Q9!0q3)g8l;tJnrk`Dzr?Nc6eDoi4%oAcx`VX1w7vdB8?y>G%xro2e&r8jm#9Z_rGUh4ke?mP^#^mEzcdS{v8y~Tr$DD(E9Cx4ikp9oq&dz!~*=rtZ=eFd?&7AIfauT1=FQ}}rviw9Z`URAIpsWzF2z?)A)s%fstV#b9W!05^MyyT0FvomI{FMF&%;in|kbZUMszLOo|2Z{3CDx$-0b`0V*N4=r&Y0R9`>CaNANK9TF$LMP7yI_2ZUOdOg#8tv?kDW6Hv2bo)MQR?=JRGfZoiMRG0OT8L+KAx7N%?naT5I~WiynmB+jM3P}v$~3yACKkKvdJ#8vden9CqepudK>HV_T^E2+7PxPg8cV<s`z1nR9}%zBPpWvM-ieMfOjANCx|zC)=ykUdXgf0L-YkiD&E|7MQ4%xN&6!Ft^OHf1N2?IoV1pQ!8`Wl6*|`e&4FS9X@Tn|`vgE6Vm0FVjE4G3SUE>3_pq>BMvNuQ1nDVmke^)VxT%O8*<iq%qey>Rn;XWsbdQsr?N5KEpBF*z-yDeUiF~>^Y77rBOGTy<KMiW{%y=na+IatjF!|P<BDt0pcb4smd~x9U)$)pQ6m6>=1Ds{WxW(m2D;-r+<NCt`U#X&tR@w#B20VGuL_IE&7M3d5n0Teg<Q%GuJihoo38&jy-0nJ%xRzaLf+&e2INuqHZdCzRv!xQ#X#i9cTY$j&;m=i}`M`9=9K^Y>~40#HIAVQnp;#JmO;dJ(P7-7C`JoznijN$~qIf(_h3f5yZaqmowKgVg&tO%w;DoqaQ%czC=6y<&0U(ToKgk#hC6K+t*Ti5BA-IW5U_<Que)+x?i#9#q4h}b-S^*?(E;p(TO>iG2b%Q<MzudtE8+nu`K;E%E~FLK&(t(S5{wH8)7s14V5)k)`HlUekG2nLTp069CKAAR-xaRxtbEI(r-h}Cd8)n%Q2=hb5)^UW5%@Q*d~_Rb@r`uOnLTPmVK9{ZW;Dmnf+C!ZbSCgmi?PKnlWcp=Bvtj-2NZxx#KTouZh3Y|4rFjWq%U?re9o*DXQ#aVk!E?lzpVkMyyExFOJEQ1z3XqTjuh}0(5g89P7?ilIZ42GDk&@uSl*0bvzjR7j@ivA2FsP$Ck+QPwmCocX8JD2YddVegDp$e`C*X?PARF5qq^!yObqIDdzNGJ`eWl_D`s>N0c2U9-#032C!e*apEERFO|Jh_A4=K7Wi+Jz0ll^0$<TT!ZFFj=k)h8*Fj=3{TIyjjChd#uhe`_d`5piV-B(YWa_<O%qxz4ZmHdkCx}PrALY1I;(q$asr`odg1)=ASM1-+;r5@gp6A45`qPvJD;rDfM}MTUZpy|J`_oTR_O<5zJrM9T{bR}!m7OFWrXS2PLBu5b-I%L4F^GO5b0rXa(|1xciI_mY8)N!2R}l3Q8FQFplPtBTu<sO(nZ};`vG0D=9m$^iv%mh-J;vS+vwt(kY3A(Be7#wZ+wY+417$ifFa2uDvMH-X^q^lwSs!KPi9P9mq0If?|7l0ePyYjs@gx?ZpN+XRq9^^_%$0+v(JxQUBE%f@voXelxjd<tn=$!0wuq(nD(t%o$8=!NdD(Yf>Q-aV9_-J9x?ixj{OsS%(UUnf=F?b@+wZ8Xpt459eDvM_<)-Y)DigEPud1xCvX6<q=+{-2M_GGf0r~|wCKu70es<={Ld-=!4|C-tW}*KvHNA;B>1St5R_4k@y*!L5z_H$z+N-kfsvOgiJ?CTJ`KbE|d(O)KvQoD$dn>^H%^ba$GYj)&VLfi&SN+jSSuJ8C`d=vPpsWG0BmJ?;0+mfB2GJj-Y`U@#;w<{DIHo;u3jGeu)rHue{&eP=P3%H{GBu|VXVdS%n2yZVo_f<6GmB%VSZa5pFR>N<S{(NUu><`E)E-5gPCta&L6#gr%-Mzcy09L%KU~>FWh05>>5o=6P1!i&O!^y@Em5|GxPpF+vRGxSiM!}e<d~_%t@Nic*Bs(h`mxNllQ@U|7HV!K?xa7BF*BKKD)nL+vx{T5T58|OzBh8raP~Z&eUGQ^X!bml{mrCq413$f{>>aKm~#&E&0#%mKT_E~WzocV`fHUPRJMtDl>QB6dz9TICeZ&{*|*A^#5?r&am-=jZTbh9>lE=Y{coA;F7Xuoo7B8byi5NeV~#S{Vd{O$m^&PM+fw@t_I-n6BH431`;Mos+xKsi#iMZ6|JQ#q@1K9}y$mhWe?afwBQyV8!#eVa(t7{n4gWUTWsUbx|8sAI*Kn^;+W!D)aPAQ'

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
