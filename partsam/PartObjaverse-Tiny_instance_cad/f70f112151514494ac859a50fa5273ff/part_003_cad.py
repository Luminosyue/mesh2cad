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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f70f112151514494ac859a50fa5273ff/part_003.stl', 'relative_path': 'f70f112151514494ac859a50fa5273ff/part_003.stl', 'source_sha256': 'd4217f15e89e4cb17d0097cbe490b730b7425f7aa45a9097e57b38fa604916b5', 'input_faces': 1224, 'input_vertices': 708, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5, -0.4753577709197998, -0.41103097796440125], [0.5000007748603821, 0.4753553569316864, 0.41103097796440125]]}
GEOMETRY_BASE85 = 'c$}r31#}eI7Otxk+$GH5G&4Yu;BKLC4Fq@SObD(?a4X#1Ei@Vk?h>Foc(4Egg44Loz+9YQug>0orK{@pUF)s)xNG14>pwfEP93XLRSgr^*gKhz#DDTjS@*>(ch!<45$Pl!X-G(Dc(34)uoC?T4!1~|$QOS!UC^|3Kwx`|G(;Nd+btw4IMla_)wf#rO1^$p-|hoK!$X7mcO4MgEkyYBg8GJqsD4<_pn)Ok=fV|BRr0fzE#hY#ZT)}zlLobMsQ)KVSQ#VKUbSVSzs^^NW<Ki4cRpXgU+>GAzda!TpWqV)-*Sh1>2cAM2EWrS^5xIncI$oRd-ezV`Y87*M>{<D*87#CYv_Efp5}bbH|J~hH|J}<mM^<}4Cf_Dr6}L*+f|?PFMqhNKVN6$^TQ4gzHQU<!y@1L<NbX@JM_px<(qwL&n#5F^U*o-o$IUYG_>2G!{pmbKQ*@VoHzIM`O@RWLk<tVqWaW6|K7i+FGrpmc98sE!^pQu$4?o`FR|&a!7p%WALSPqan~@eUI(0Wc<^1Sug^~!Z>D_BH|HmfLsP!yYx#1jA$RrtWzA5B^3A?Y^+mo^tNmR=fBpIy>-Zl&)n`DvyZZjJ<t)tgG5L1Yr}`95%jHbHbJoz06H;?~o}0z}m{^UDEC12|j=sNam$G~GU8+y@DQvr=??>C(h%*ikzEkz7K3nVE(bvcJGI)=}gD<@b-b3YIy?C3B_oQ!}VLS|Jcw0XnoK-WCntiESrc*SYZ~7R@aptp8JDGi()wY}ZWzyqY^mDH(@rL70Z$`d#^^yd=FP$u7$hYn3PUV|@X>WHbU$&;Zr9WReDEhd=gRiJQ)hGVKO)BTtxZ8$)e7g3gzCO0m4mz&cm&Q2wxNjQW)XxjK_Oh!E557(H_4(SoFz0K&IbWL>=6uah%3ojqreVI^o5%Scd}@b_C2#8Ig{xx_<(qw}QxN4Vi6w68=Y`U2H068psr)<z4ehLS`^^1l@}-c^JWhIgb2%ql-Zk{g^sfo}ab+DG!`B&;Z&Q7$=j}HM`uV8%CtRW9^c#?%pLf>dM?Lzo>Qj3j?UrDekMnn5c6jjZs!#dZgA?@ix2}kw^ELZ+)u;0fD4Adw&)rVbd6|8y>eIZdvi*jB96G1wp>b~Zt<&<*I9D=EC*Sq8{XIi_dXKxIpV!vVGZ!5md|CDBxXY^F(D#>Is0AO_<l9uA^0R)ru0O7Fy!9@J2j6<4^)70Mz&Y3T?PJ^co!i0W+f`rW+tQ7>ZkX@ON7K4(_U)=q<qwFsW*8@7Ir+L^@)gw=`S#omt{Lhd=x{nb_)gWQ{Jz!6SKhp1KSiU&W8yfazQ!B+H)Vc0uGzP$z9`3)u#-N^n?6uEa@Ts>93Fh<g&Nzae?QKN*Y~^hV-=Ne_N}T<{qnGEykR~jKBs)MZ&!WFx8LOTL)+I4Kg<2?!Pn;}?dweWdS9QPw68Pe>wTJEMQ*T<bxi5+pnS7$SAA-q>8E);)An_}Cs4j8pT^0-Q+!_9b^qi>%J<}peCwtSSM}plZrY#P)9l++pUziVO1`!(*&f~I@p`-g*Z*t<+7H_14YZP<#h-m`T^f4i`v3Cjd~cN}Ut5=yLE$_uO}<_ADZgAfu20pEG_G8SmmP6<@_iQ^p?NoK`4z+X@4t=qC!Tzo7t<DzpR~^`S)J=)@?EM=?SG>w`PL(KsU2K>POf!$@NJvMuci4??*3){e0LtKOrJgZRQ~iDm-X}A+9l?a!-H>Aeahc^EKc7J%78Z1e%6df4ZiDKtCQ58S5|SkD;rQfl|^Ou(a)<dG5F5wsc63~EnCF<C#(a`#j#u;lP@ocrTSPSEOGjIt=zHkXOl18wZ&2S_is>nuC>8*Tx;1f^{C!HV=n3EyWA)`&XcdGK9w_S-$lbXZ{|z+X5X&*)Gy7dUeJ#R`xuGx%)V3gDZgjC^M-aS^vXfHvZ2A3XJ2rLe0iLee0g&Z9w#d-kyM`!Sq;9N$Fh;iAGIge(2oTqUjNJPH2C(hKhM%Qufso2+P^jLLHkIv?^Jz#e$xKUl&|^b{G|PxDPQxod}Z}d9>?1KPQ5OaZ}t_{r}C%$&HH}s{{3!FF5l!kRbQX4t#8g2wG8=spXzh_2;XmL`>Q@(dB1qZ#`V$mS5K;W^cB^oa%Q*V>onFSYx+1|pH04^`c%)GJ9)j)){UEOXniyL)?008eX|{Zf0~Z3-5+)No!2#!uc*GrcUGTr+Aw}D*XQfcg&~|@yDyKo!=GBw`P}Sa$akf9OY>U(7D&Ffo=95?()#7er+n*=Q~Gi48d-(g!};9c+h3HWbw+BI!1rm|`f#QQ?_*8AP4(%#QcmY`wEL{^F_driU8+yzN7UnTwDqCiE-v4L&*eYh=MLKXP_Zk@|8HO9Tf5}q`wgrEu4Bb${WbemM={=4&)?7YbK1V>^k<&u|LisRPSvM=&s{l2-(O0uwzNJdNB)e__m{2h2wG=c{ZbqA|5{4xhO+Xp(~zIqM(d9<(1(2OdSq==g~p%!%iG{PRiD~tQqBYV@})P0_<k<qdw$-5_1QKxjPK7LU*h?X{eWDe1g|5_&hmKF_L*-pUDW$Y^Ko9aTY5ifzW4lP@RQb)p>=NS{iNqSt(qGAq~|#%Kk2y*e0%a!`}OCm-FIldR)3dT{~9`9>v!ApW0xKO!`J60U3W76xZ?2OyHsDFpR~W7)8eYbgYQ&*eSXsQ^j#i9zUIrSZzx~8jwhZn)JOAOs&6=7ZNG6p#*m-%Tt)Tu`AO^5xoAUu^u9hnY2S4<<8_Az->Lfg{G{iHl_L@y9(+ah4fWBDD?>Zz#+9MJbmL0z>&KO$9NoAwl!NP$yvx@x-t@kq99(yt6?5Ejc<^1SFY=|(V}^NWQ|F!VU3Hfm=BZPir^2_zg&N1XI<KjmZE3dX*8y#Pu)R1NrT4Y<!CGl1txwuI<4k3vb;<ee!$y7iwxFf-Sw1*pqds41H-gqBXQc{;e0%P;kyQT=_3V^yUO$6mgRiZhN^plo`gy0V&t_j+pC!K$v-R^%TmL=zlpiZi)z7=6>x&1U@{6CFpr3cz^~>xhUB3pt9<85uN!Le{uU#LdCig~CIodu`z0Oj8z0$)C{-`Q^{k_(wpMIWd*LP1o<%fUht?w_Jx=)~=kNO;J=&uK#T2X$_{ay9>E_EM5{)-uHNKN}0v#;%Eq}VmnYUsv!(tgb3Yx^<jbBTGRrhTK?*Y=H?Z{9b0@+m*kLB4q(YxcE$ta9lBmt)$8oBgDHGJNws-0Yk4&HHe(ujNa1nk=Dtue)EM`Y-5i@LlTt1?3+rv!;fwAFa79Ja0SpF!<6c3(ZsKnY46Yn{=Nz>jJL>U+Nis_5O&;Uwm}~&2Q6vmf6?tv!uGwTj;pv`#6)Y-N#9h_qJ2LO!tXqU%O9~dsuhUakX`FRGE5|_iQlv=KEH&uidxG_g2w!LGyjF+1KuiCEqo>^z9?7_t&INw;O!x;<9|-9sBn#LqDqb?{xgE{~COkdcRNgi62PsPt4B^%)a*Az&ZN$KK*>uo=bT0seJG42dJL7F36GN>A8p5m-?Ngap0VJ_n@JF@f^mJPvd-a?P&dZ$-WEtIgiO#qL<Ng9_4*+es5`d?&Qg*&$}0~kL#v%aFCVGvvKO9hVh2yV`g7_J|@kW#=iOan+Kojd3`4N|Mh&&gHQR*&XaF`erWc!=ZDVX*ZH{S=bs*Yeg1zv|McMN^Z)Dlrw5;Yzf3KMVcy~St=ZR}-&*DNPQ(1d^I@~EJs-9uUqQaMA5hNMpy$tK-)5^v&!27ki^b^YW76|&ldnDBwwKt;?`N?8*X|3PvtwiQ<5qj#ZuXO&x0fAq+%WI(Jm2hV&-1PQ%b(QGJMDde+1K6|C?DING>lKYk1+e%`w07}f~O4i$NLVmuf6ZEPTPA*-(TAM6tl0rPqBptoYt44wVUnyqSN|*)ZPb~eeHda{q2%7hW^6)CbO@-Z?aGNbw+=_+WRcCuf5N*m&{Jj&&==F%)a)1&DPs5R^MORdp)zSz1Oo9lw%FYMLSsMOo%ni3%qAE``UX(YojGxj_Ez7C!db{b}6q<ruU>~Uwcn#jX2B4HNA)R<kNYUj^pE+-XoiR?LDvNo8KdweRIC~J+j%?@@>|!=k()8dk=2*wfEq*Z&%Oh+c~LU7B@d{n0I(DZ}zqK^0s>s=k?=Id+%@dwfFw^UN_I{>!Tgl)s^=<=I<N0QUqVrk1Oqa3ua&Y-hw^x+9kc8RL-{3ar*je-@7pT+V?J`i)k+F$G`SH5VNm+4@8QOysR%L>H88nKVH_4Pwo3EW?%chit}&w&EJRd<kROpS*{qyC%$iE_LIJE6ZhK{{rJ?r&tvwr@AGKB`TIg<-<)s$zL42Z%C9oxs=ht7?@gKgr0-45>JhK^liGRH+;~HK;`?1@U;BQSG;&_NzCE??kC}b#`(x6KUGe(%)V`l)_LIJ!7P&88-=5m{-^_l}_ut@~zh7te&H3i<*O`4SUrIUTnxTEP>-d(T*YxL`<VP>LW;ieHdk9f0uNlUV$v1zGQS;5;W0V{pxt!sjXrJWjUqq&U@Jr<S^nOdez0uWa<lp*5zTN*{_P3v%LU~ep+Rxf{Sm-&IE!|HlNA}H3zEt8H@56i(sT}FrZ|oQP&hL-A-==buR|VM*J<9K`?`K>}<+Llx`{h3yQ2CO7WGyPENhy8~=Tno9`~K(*t|$9Wf4t9b_jNIqm%9S_uA{Xm-<75p-Onq<s`Go`=I1#7K?yppGiL+#YhGYKQ(C%Tl~1(b^9@Z)_y6*51?y6MZgeJJ{_&H`Uyyq)jf=M3xIURIlyBcOV;0w^2j{=cMEOe9xMg(QXM?z&mHOVN{Db|QQ#ma{xtyv#lyAK?cPY=q!CcRho%wz{<X8hL=i_v4&-gn0zN*`k1=OBn=aO#?TENfyzQi`B@=ML*^XglZ+y7l9dd?+<&F6N08E}t|m*!R=w=?_J==xm#+Gg|Vc)RSJpS}+7*Rz&fO}cdh*T;U0`)i(e1eNa}#r3x~<M&mw8`5!|uXeCMWdPMvy-Qv~e$U-p{<`A{+|Tn@Qhi??<o2<KasJPti^yMbi2a!6+>c(hsXj_v47c;jv2<S2yJ>vBdoFVMS96i?N)@@9+GoTiE~oY+@~v&-BdDCkx7e?rpL{uCz$z*)|7-RK7Ugm#UZsANbNqwxwv6Y|Kf!D0yn_G3<6+`s8Yiw7v-v%KvL9T}N2@r$aFm^X|B1x?^y&qV!^^w*`AFwfJf9ujcc~r;)%ds-GH`#Kc+2^fZc)EGLw@6ON<Amv`m4Y^%D<MI=jW7{JZ?K5pG|qk^Km^U^Ei@kIJo}df3m+bk&bJt^!F<AkC)*3#QY-Pb#VR)`n@A1`THPM9^IkyIc{4{?cAm`*R%fu^s|M|OKDn$>sj$FKQ|wFXakkMwK5-f-!m#l3N1wQLONKL>%Sp_+dK3!)l-`3&wiLUKhNsbGl0%FfXAzR_apm7kF2M>4|Um({KoCD{UXh4xo<-*r-UDm!&Cn2sXnEeu>bQ1_hZ%<G~cBn0X+V8uHkt$HVvJZbiE^=@9omOzCG!-j&wp7KJFh|`Ms}wKaE4@ygq!saXYym*TnO9n-<RPnQiKAeZMQUhw{8CK9$bP8k(8ruM(kfznmY-^LOkD>USyq6h7|3@!Zb7h34=)W8d|BD3$O0wr(NS=iPKJ|K$m;&v6Ua^X6=Bhe{)Pok<bK>qEp6_CwC{d0kFU^;goY;r6le{IIS}xsK}jj(zFFXc|BE|BR*kYb7v>{f$@nI@V_}&r`oW+&(ql@%)SM<L5t94sksjOyzRC%55e81N-*g*ZBID?KIWLnQ(;jUHy37YuAhJPvs3KxE*%n<@24JWiuVO@+mIo<}DhBw&AB*QhT<D<@P-JfUm=S7jpajyvXO9vLUx~(~7+QbmI5+_C0;699P{jn<)S4P0ru?h|hQNb*|?N_MN^XsGiD>1N3~*nfW%?GkGDZr!6?$Ci?ju_HEmn(sAX}GOc6stw-FR^#}8D<?8%=wbgSj|IAVH?Y2U+4oeBIxO~6v)Sk|fm+1YC)5`k>Ia6`!cX@C|>PPtn_7mG;xE#mAg;bwbKe_y!WjTMz1D+Qdc|W1N9zf+=Cx%Cnzbzxrw<X!>yqxnI&^n-;W?#<kPwnG+w`(yS_f}5!o5|e%pYGCeoh|<0>vRR4XSNM~{2nNnedQYZcVlT<2b7TFTu!p@yiWRdp>Zf3EXDbwn{dAzy~M|@Q-RB`Sb^7#rKf0pkSkZ@{6XFLyw4S(=gx|)DxcSBiT81D1NptqIrgpdnsWV9zo7cd>3QEHKeF(C?bDQr^toCc_FI49eRS09rgYps^?7}9CF6ZUo>DaamBqZTQo`{*<HR~zf1FD@@p12Er1Gs7hjD%C{>AxUG8vB>&%S)9Jg?hRFVS^YZXUw^*OdJI5^Gd5s!z?nT+WTIy#9yPrGAtujAq}z2aiLq2fQBEozC??@8o{>-OKs0E4iH)pT%`>D6iX@ob1b?y#C~B+J?qSjk8>Swn5}81?JPb=gb_(<$Hzm`qpqFt=rC1S2;g+3bmWF%@m&RmEyU-zGvZ|4<1G1Uuyf1{bFl*9Db-v`%kIhWA?+xarw)d&^jP3f5GpE-_7N9U{_(9r_!~*xm*{IUu*SRH2&p?w_MJF$z0BpUcCRQ#`{hwg2#oj)}P*wIt%l@Q#vw>^QZRX`?=ZJzeY~r{tBGT>*Us~?61XsJLofwPw9&fmvgW^A3t?tY6mGpZq8rSi~Di*1^)XKee!TW^;^d6T)p!S%8O%P+Sr}z`F<14J7s5SzFzj-OXWE4Zre-cN0s67qxx|>v~5TAaTf9Cc@;O5^5tR{{`(re8}o5<gz$b~&1!zX-LW;7U+o01KgsTKzJq<`>1r<j#=fnTAJm7}&6%NGpR<?vd)Iz_xjx?xaDKO3{CuueKR)g{JMTYlr{i)0CUO4hDDrI|L#ZE?xT)L@@n5(dDn;@8?6T81KjsOKx9n4S-;!lI`%`21xY6h6eUcJChwJ%cG3C3C=cVzie3{4fNjHnH`|<1BQ8^nIb2}VZ#_K?HpP5vy_foFUg;%`)`SqISuaqHz%kR$P$U37sea}bg9m(xq71!UBZ<g`-ykb8@;p=G$8{KC~{a<r^<d(coX}pg2OB+9M`^OCAa#B=nP4(~dnU5Fqh3^}F|3Sxf9{S1ojob6O9aM_e2c_9BuK&Che110)cs~B%eV%jYSYB_B=cVIH{eI)?-{Ka0-HRSf<IwqpeI<GlU*ATr<#`d7oy*y?fsZq;249bM^Zk`F2ld??+kwgttH=34Twhn*JM6D;-EC^&eb-k%T4$7t-MK#=m*k&U*~ag)>_fPmp8fgySxVvcr^`@2?t}{5zf0cHeSy?r3ifRsx%}y``R@_TU|)IhJFknMy!pDhVLAKb^RYj^C$*=XdIcZ1?NZ)Hg}<Zyys|fv^DFe^pO;I??-w6z;(Eug<okjG=a-Y;YCGrK&v8F?sL18a+spY&BKYS=!?%-vCYtMgkngvwp%RrNPj~Wp-sR^FuIxGJe4WKka6KLebNeKGj^c5Dnadxynf3K@y531a37kJ;Jl_|zt<U?ehfld4pBv#m+n@IN(u!y7%TxHc^_uX0`}cpip1A|~y!L;jaW21n&-Gj<bN#=S<?#^kfsZ@-6KlXS{yu}upIwP#x!snXnM3_v=LhHI<9gaQ<>z@+)WYj{na(`k#=hx9`G>rC-`^q~@1t%v;`OtcH~aP>*Y)F5zLJ91qkp>cx)QX7?`y87=kg=};_{#POsC&(kc-Q$&%fu|ZQo0I`||Vp?zfEhEyWeOUr;*p_lcxG`1hPIn$dde?C;0d<5%-|-RrTR_P5fa5}a4cm(RDLo$o`}m*?YV9nJfnydAjytt;?4JEI8qOX}ggj`gg``8l(5KNfD$k;YY;+Fbs_<$T->FKIoI7u4nY7w*pMQh}-TT*4XGnCoxDy8h)oKbPp$lFR9X`!GjFx}SA!XvOVvU>MgYawyGT#k(VyQ#p*+fnj<1xj|eA*E4Z6?oSWUc$TX#;qss5;`J@XTJD#y2+m)V_lCY-oYyvT`GvFG(2oaa8@}Esj|cMa`HbSf51VW+=Z~w)$F2N`);HPz1RwW<g~#*L_w>9-%6WmyIh2gYPxpp%DewLzF1Ox5?yv33d0lODll!;F1U^owp7efQ3UhIO`xm@#oV&F%)hG8O&a1-X(>^qMEzirJ?Ef{2uRp7D@Ou6>JztNzdhxhzd2t7wZ;C9u|0sa#^6dls{H+rEw#m`lp84L<^;DVTgXaaecs~<0o7N>M`|rFzuukUjpEJc~%1fJr^B)}IeNkWle;?>7{L5Q;pIf`Rjm|3~KkrK>+~@jq7{S-a?tgIpi5RZWurIt%E>?_>`yf4!lhMcMeX(;%DK01N4j%vehtqwu+@UF-Z<;B5ogMnR3mx}hEAp+m?(@FAKqa~#QFe4;ztKaUr#~8SImJeCIf;kZANQEPM<peW;p6V$>#Y5^Ni-gmj#D`QVkf>n&U{GEg`{Uo`MhH4^Yye`Z*GT>XfEdkx2G%RFS;Hn_2Rgk5^eZ;p0P0P8<o~~Isfwl_H*6i``HTra(>!i_B$r0_f5*x6m);6?B)9dd!<i&zxgT+-<M7v!~IzG7nSdHW@rB(uRqQ=d-(a%?2`Pv?EOsMzjV9Ge_wS|EzaNinA@RA2L5{!6WWq5-+j$~*g3vW%r=|rGb;m+hkZBc`+v&7CH&kWBi}DL^W@|2WA!+|`Ca(_*mk4<eZS2)@dcOPDv;Z=Kq5bv?*E?ehx@kT<7O?#_tEKc(EY!CvmckUU;ve)gj@N!KuNxjRG#Oc?^7yOE3w}W_lx-#)BV2kpGN!~v(9@iC(OzB_1U`db5idgyw3cpNb^EY@h|x{zll5^s@7jg`2pYgxyh}mT+Z@0bRVRAFGSC^<@crdyx#nzc_(KnOTH~z3w-b7bO_ZmZ8`FlWEJ>)<CiVvdiNvW+44KD8|A-n{*Wo;yB=5J{hoH8m1`0ClCR9=EZ;}-QFg6jf6)W3&tIK*KfgPg%lCPW=PvhXKH4pki$34t=g_vfKYBU>4gWgEm|t-(T$R--sF7Ook-7)z|7ncMoTjPge;T7#x&Nzw8l!ZXGUfjN{%wpj6TKv9rW&&mf>%T5f>(prKxcv1fbD9`gHDFd0#63_LkJ!NoeLfV9t)ib9t$1?od_NU?gQ-%?gMTEtqB%d37l7rKh?+v%>&M-MnU|%Abuv;M~xh6<c2Tu{($BN=SGg;TxzsXql_92puM0iz`ejT)L5m)a5W+jf=8>-9NG*z9NY}t6d|}LbQO3N%I*nm0d5Md0Br$ofqDxriM#^P3gB#LD+@Fg*aCiT;WiNMl^puh!kirZ%EI~>{0e*pdI5X|90NT9jsYKr9snN(AA;@&9|A{14}zn?$Dt1Jaqx9$9QZo;U+8nNP;u`6LJNRJ2>u1F0Iq;`7JOHY%W9m1o&=u*$3jnlW5Ji8r@)uM_o4CN``|QQ9D@I&#y#j+Xgv5V*a<xac7l&WPk@htk3mm@kAY7^FN05m?;r%ff!+lR_4Z<Z1O5#mxP%(Dq1mC{;OyWR_&rh93xwdS&~xCc;PcQ}@Okhx=q2zq@ZZq;;J?9EFILgkRzw=C0S&-qprYN&;IrUdUhclhg)t)d7sk>rjKN>X(Z;0U<IuAf_ZSu&4Ru=FV_xtf=uwM%jtD*sJ!WywDZw$&(-!v}6nq7G$Ksx|g0*=q_&f9sSg7br!G~3Ks&Pb(LuxqG*oP1tqs9SfG}Hl(1|LHRJ^?)hK7_JQK%L-Y(4$Z%_$c@wLhy0uVX)BsV4+*V2ceswTfv*a!w`b!s4)T>3Ec|bigE>qs}ZHfbTtM-H$tPp8^H$<QD~=q&<)Tia1_cFTuluxH8LOsKe4dhurP}dd|QpDYTQ&Kix-FB)T&Bethex4__q*(FCqk=fj$L4McHSdH^3L63D6th1n>{2sOt}W7F-$UQ4L%fJP=V0?H3NM0j&nEhPJ4IK9bQt!=V098SD?15Hi{#3$zwg2FoZ{u%bqg8Y`d^z!}v@p~e>r>n97d2*DqqAHl8EoO)^$hZY7G2WNz)&~Z+D{(y24p`XEt;LKheg43${4f+-;{I>|fuc05oufhL7KY{-Ne}#&=e1+x&i*u=p`c{Qs7;PllY8`YccpZ2>bQ-vw8Ubi;1snve4i?%L90Z;K?E#(u7G)1c`JvFM;Hk*be33T=ItV-kJPsNH9tXDJe8u^<hT6b3<OmjP&UP<ew}kHTa<5~8k3si>x1;U$pk4N&&Gy1u2VDW)t;Sk4wt4Xw>#D{`=mPLa@FM6o@HYJJBGkVX>fQ>!V?&I@d5=V{)((r%PK!{E)^2OjuG7Hlp}WEB!P+?sjfU>_a$h?HAAoN2a<89)H$oS9xz||11EF2L-0O+p%Fyy&?lniSSd)aN1b4;x3oj%5;?VNo^2iaqSdGnUjEBw#j|X>xb_aI?*N4^t*9VtE2rdK`S`3;VETW+<zah%#1nmHA2<`xGj}Y7lS`6F>TojrfEHoLoDA*603G4?hixBJ!7TN?_7u*Eg1=<_j1w0A51Uw1693gm%8bj0wQ)8JLyP!LfBYwUVx)Zz;IZL5oV4*|7OTpT)hT`}_JL>Aw5%m??SXckXIKQ$`KWJlJTQ%0TXJfQ|W0a-!MMv~iM;yC7G)&izVd&d1w1w8!g0=A`Sd7QT(1p+;;2~&>g}QbWycxf<1G*5r5IH*#f{!2sABOG(9|rG-ZUOHHM?#l?Bf%q}y}={EwV-vuwZK`RzFzMAk6^KX5t<1sLhx;9GO!52PoU|&-1{rR8Q>N2a_`3k*MQam*8qn@yMx2Q8=&*S8^HUZo4wq7Y{7@1JHR`<-23qXUVPo^@5R@&ZeDy{>jp0rIv8Bei?3UO@Wk&Ag7yUu0*65V0*8QGLj%EqC{yq|>=&}a6UWO5%?cJOa&n@cqTVf`ZNV+U6`|F^6~VuwjCa_l2z{vAw>-qYMyN}-&v9WNB=nJPUnKY&^gZ|+IKLOGIA(qvyE?eE8dbd9doaQ2ym+4})E`>K%e@yBtlet}4u+Nn2ZP%|i-6mKwLMV)>JR`wKSHopf5B<tl?InaT?N0yK2p>%5qn9&VsHNd_Xpbfh+Lt<dx@Vt06)M!_a!tDEUu~I+L-`-rn^UYhI@!-`2CB>$%woU@V`KxfrW}3!NbsAo1iPb-1l^X4??$tgVBz{TLE8zt^}_{j^LT<DeqTfsv6^=d!hTmd%<rJg8xzDHS{2KKUnBYa78uRt5H&oqR>ESdvG9lJfc00KNA`RZ4Yjbas?MuBfA>EtC1D@8#FukH*irzb{xMV)DM~+oE_x~zN$vN8b8&@U}61^&+*{z;A;rMm(@51y$Fp5$D>@qz0{bdMtA5KaCdNTgy8AWY2fMLC6f62Cam+I)4<bkjClyb6Vy1T##%L2A_Px@&H+yXcY{s<cLR5V_5ybTw}o~Gw*_~G_6Bzbhadz`giZ%f1kZ;q0nZ1o(VhPqgy6%_Ltvp7z=y$?pm)KSz~2ypEoz@<5!Y9-<|70bhL#2w23JG~t|9Ipq5ja)V1IB0s4utzxCk^0xCl4{A`8aiRgA@7P~rcAW(5nifQ8;g{x6*4Rp<rqRq#dVA@D`;F@)d<s2yy_IE#Qz08hXeia^Xk8FMh^v@!)>hMogo25a+6@O3rrL(f9bfrYLFcU8}~vKqCaMZvYfT7MNq9}4x+^{J1p-+j=I-_VW{KKp<ra7JiRa8VpPBSLT?HT<A8p_RcxyMnK%#oklnJVNjTgy7^BR&NWl2yc|_2QGx;3jHCmdV_!9cfUeKSzl516|m4m@K><-y^JVBf+kAtc1YCCBf)XdE8sY=19~3p0IySH6*Lxl9(*3>AB&v1__@&4;B{aJG+I}FG>-obdI=gWxz_=~+FBua4Rp2SUS|Z)ht8GU>yluxZiPT6L+66$qTYf>t1(WECJ4dJ)My8t0v!jQ0^WxZyazfOEOaM$5BLp2@C`K*pj)9k!CS#Yp`*b=!L^}Hz_r2o5rPXrn}G{~i|Ed+2tsfPH7Y=D&~{)Ocm{L|cn0_YbRYNt_!UC%-_SkaJ!lKT&DF80sL>1|cnowEcno+2bSroTI10KK90lG3-3HzR-U5vPZvn4_jsvd*kA=1Xj|B%p{{RPqt<d)pvlaYKVvPj918;zaf;WH%LjA!5!PTI-!PUSyp{c<+!6~5@a7wTQO(nVi2u=ab1x^9Z0j&<s0j{dX0O%lSb?_i?7(#FjXfALKa2{wXa2{|Ps0Ew`>;+9NB|Um4P7BQqP7BTp^#|t#%g|7;3=W4zg2Ta^q3^+)!5^Ta??2$P-~t#AEx-l9t)Sz;t-uqY5#R}6J9Hb^4&DLX3*G_V2i*$Z2i^`{1>O!`4OPIa!Q-LL!Q;U#)%X*dAKDz8ADj=`44e;~2O&5BItCm79tB+i9tB<ojRG$NZ-VXtZvyXzZUOHGZ-%Y}Zw4=ijs-6VkA?<<M}wO}t>C8MyihUE^WwAM|46JG!2bbnfer+30S|#z0}lb$g60I*0$ZUe!B%j3s02<A_J*badxO(KbAZ!<^FgbE^MPwh?zNyMLhxWUqM+-c1HkLS8=-^18^N2PVc<>R?Fhlcp*6t6!F8c|z;(fYLeqf%1ZRSJfir=VL(_tjgEK?(f-{2)KxJ?Na6M=^xE^=}bTfDacn9<YcnA0sRIDSP@L6zf3u`NIZg3;$1aKqpaHt(T9K0C11H2f#0lE*o0lX8s9lR5~9=aO59=r%T9=r%V4B8Sr4BXJ-UTYd61m{8sz9Vr6z75R}79sc+G#^-m;G57qU=f1F9xVZ!13wP{=Kwc`jsiCZkAN-%j{q-$ZUQd>Z-nj!Zv^jxZU*lHM?#l_Bf(3dqrpqTBcV;fBf(9edBIJ<IiX^0%8Ac{|CLy`fd2(=gAM_20}q4N0uKY%fm*?Jz<)r~gZ}_$gnENBf|Ehhfs=tVK=Xk!fb&CZO71<g;M&l^l6zk*c&OxFzqEb0;H?-NTQOd?!q>)66vmg(^^$wMt;cv2x>0hE&y5(rLN`h7@htcwbUXMX_%lNAF6eOZF7Q}rUGP|N0Q66A0N59r3G55@fhGt0fU`g|gR_9MK?{JhfeS<HfeVA1LPvm`f)(fvumau<{RG|({sI+i-xquqoZZ6O2%H^U7djkV7aR&*3=Rb^fNlUU0I!Aa1g{0JgRTd!1FwND0<QtjhYkbJ2M>Za1P=n&f#w3&0sn5{u_5#$G#6Ot9gL$gYLrr=oEj~mji9B#jldNUf{RJ~j8<rIXen?hlv^B88o33*;<;``Xk%z;u!vy%ydpSA;%Cu9XG4R*B97wcGr{7y_iN}&=uxnU%ohInYw&MsREJiDW(HRUmq!Rr4;5vl$7jLMQT|czb8rlFHaG^n5E=|#2<{1O4DJbT1uYG31uhRQ4la)N7u;8^+axvmBLq)}&Hzsb&xB3{&je3{_5n`=_k*?t_XBrSqa3shv@N&{xFkYwYiJ*EYj98KL~u{=5a<l>5b$K^B=BVLP-tK9P;f6bI;d^bM~!}JEQKzD_5m*fFF*+Hfe_pp+5s%IKDafwGPDx7GPo?X0k|x<3bZ4*3b+llKe!FJFLW8WFL*KZ6nHWC1oScZ1o$a5wT1a9IIV@X6gVxoEVK={EVv!C7q}PNyd6StCuo0gCvXr#a5!{2I2=41Iukq_JO?@rJO?}r+7CPn90u(O4g=eC<Jg7}Tt$sc&~(sp;B??L&@$jO;8f6(;8frg2*Jgnt--~?^`Sk%^}*esL%`j@1E7<^1Hgl!L&1Z=1EIaZ1HmECHsBC&186C518@mwYH$f~N~joHDe+nGLyWgm;D_Kd&}HB=;1$sR;1%Fe(2n3y;I7aH;I7~n&`RJI;D*rp;D+Gl&<^0{;4aX9;4a{ix;14aLhy1mPD4*Zmx51%k3$!MkAt1i1z;!m2tx2IXb<o#@LveQEupQ!LMww?g3Ce6g3E!+K&ybufXhSMfXjnhLHkPXYnI@i(8ZGb8Yg%m^n~QTCJK&$K9$_pP{GfkVm;EXxq`(tS!h{{`x-5{JhUBHXeW#N`YyOCG|1xK0|>5;5F88*2M2?vLT7`gg6Bc!faif1LT7;&g6BfRz;nS<pf>On@L$j>;J?7tEbcX{8bWY33qPM1`U08>EJE-zXgaV6!B3!Rz#;@cf~EqC5bT1c0E-YT-XGovC&SN+gOh=aLF<Es@1^@)!Q$PccrPjRJ5>1EcLM}#?`;JageC(gL)itPmB1OGMWB@|?svh0D?n>m-0zMB`$OAX-0zwN*Fy;I3>I1g+5ubxti2l*EZ&!Ph4z4U0QUg*hIR(`26u<H2X_Z|fz|?d0n5-z;7Vv08CoAKv>R9kcYzMjl{o;%6gpT}hry_$(1E%-55zeM4bh!r2--ks18`SxO=t;lO|Ty{rN#YDR&a9YL&^Q#R<L-lDfEowe$Oj77P<l)3tj~s1zrW74DAXIY;5uJ@%~@`>2&uW@tj>U{D;)dziIqyrTX8@TU&DfCDXvh$;Go<$xHp8cz{}2yfu{m4;~$@;{'

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
