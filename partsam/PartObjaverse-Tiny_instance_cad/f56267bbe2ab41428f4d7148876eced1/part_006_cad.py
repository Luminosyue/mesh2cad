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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_006.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_006.stl', 'source_sha256': '9adabd42df8bf334dfcd5f042356fcf6661e99b51776b22e261fdb9d88ebf6b3', 'input_faces': 760, 'input_vertices': 481, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22453834116458893, 0.11711496859788895, -0.04221104457974434], [0.06950556486845016, 0.3380773961544037, 0.141168475151062]]}
GEOMETRY_BASE85 = 'c$}qt2Xxd%)U`~tF$ow<hp_ZsOf#LOH`6g-z<8-P)nEgr1+OWlV@l|4DWO+`X{LzYyXgcJAS5ItAqh#S;oG_IF4>jypYxyZGv}Rq-__I8=*?&(jrP#CW!iN9n*0^gwhT#FyttgEDa)++Ya{zc4e#H(Z*=(~Lq~gQS)r>x7tU`T+^TJemo`!xTcS_j=-yE!YFbLv?pM7;Sxbq2kx|2=dJYMTjOx=@=}meLitg*wqa%6_?d$YQR;eCP)>64tS<9D}|K(pMXA>-24_`d0@Z;;_^_=Lq*=?gj?cO}-#><T-;kOvN3fnK#hHhQd{h0FYr#|dZXq#C};^#&p-q=42dF+?7N&W?1r{UkdH4}O2`ari;%nx0gIT!h@P2XNny4G|Y+N0O4vlH8IAAoL4cy<c;8y}PWkL}Ryk-wjSzdjuCw(Mo0JDTo1gX1lqI0O5=EFgO28_=~)VRGCbGD`k(5y-DUo`*cvM(@unT|cl(NB-KycOy^Lm(XnsS|g9%xl%8*JI@{H#<xu*zS{Cc<cYclUGsCCac{qtk}UauK8Jd0VdIhCZf`F6BWvKiv^j^NYuCz3{`dmYeq#~Z={SDt9O@7+{iQGXfOuQ~`OqDUpPWNnY@MlS&!brAM*5-9^_RiXh}#$m-BvQ&dE_rKX(e!4cj%V>IdEQ%Dc6&bf4f!m#=Vc?yu!;sw-zlY$1Rw07XJ98c{u+r1)%FQisO78E9>sX_KEq~o=0epEjASOvF^$#=XI?e#)<7orah?7t(|8v4&TqlI5C#ZLLU3k+0ZQw+98jY*g?ima3j&v{Ed1VgTFz%_9poZj+-YE?X(Zrv)f&_1kSmDc2*7_1HaaO=nmr!>f?CzY61Mv)zI}4i)4H*et`V8prz1l{#g;PTX(NK>Za?by)Pn9$nkg__d<-scS?|YKJT<2dA9U{t~I`L1o77$`_SG>U7%Y7$|H}~tu*>eZ&*|EAGjs`HSRp}IR1Hk8s{7L0_SDR{9%LWH=x_?bx=>+>wE{0=jmMNmcKX1xP4U{=jFJX0NvqtS?aL<%o^<PHCf_YHbZ`G)Jx0{TG1iU^#^NFf6MT}$ZwxfO4@UwhFqt`bo8$!sHEhd(hlck#64YvxXfuJe^^r)pJ}Z!&O^UDh3$#uFCovV?jumILXV(p3!0%{YzqT$Tw~i>=#CnjWt=?wxC`U0(sI$mtIG8<xDdv(rT1Lu_6;*7fBSEyBTvl;=$7&`q`z*)9>j5Sgh`$g*QCFWos{DSHiNGB+=B6@9odKWTk=(eZoNMa`L*w+%Y3`LwCMdW>k{`2`HgXTC4Z;!(vNTRevR`F{O2Sva)8t`;GT>V>v`yU^K#O^mkK9i`-IcbwIzNyt`U++=B1+(pj!ijpxdt77h_yr>JQykdZt`Qv0=z#v<{a%fz2<<br_9)cNA#|-BEZd>S>(bj(R$LiZi~DjFa+zVxDxINhkWdW|!gTyAqE2di`_)dbKKYeT}<{I#^cCg>KpQlU%1emP;MhO@VH^AB#MC(}+1ZkKN6oTN^~6zZ@NHXus`z6VdPbqR!fJ|3lCxRDf=D87$*})>d3cmK<3m{?BrfzuYwk;+JF;{Vy-MKQ0eO9%J3*<Iu<5Mm;U_Ph&hgMsJ30`K~GY#on+x;<X$O=vwgv>6h}s=od$?smI;Ntz&SKjL(4`C4XLr)c-I49nznzB!9{*xj*LUh5XisjiKB9Ls2(9Wf$sibT0zkR`a3MKP;vb_8*vu`2&#OcJBT<#N9EDVO+H@A^oy2PR3RAOz1|gKcznTBj;hi`N0z3EduqlT)Hmx+}29;1xe@^`vI@RXs1sD=#Jc#<bLY4?Xbj`gl^gChy1nyhh!f9;0xV8dMI>jhyANj&w&}CTZ<Nwei?oOdGwXnbsV?a4!Q3%4o5wWNlDO++@bOuviwWLJFcvOZauk9`thGl(l7o?p=*63P#??60c(->Ni1~Bu@KbRUadXqY|A@Pj+?kt`s>D_?Pzb6-jaXqV!7{c&vDpY*Jk)$!SM?2uLAV*h3=?Z4E1*mIfMFJ&QCpxJm)h@{KdjwA>Y$((Cx=^qdr=PLAWpLxq>7<yrc9>@r&peqf9C2j(HC-kLk^;p?|b2e$Z_f9q{#|_htU`JAMRt3Ozu7S?k}G_zClm$aOtf#>2d*HK;?Cc<4sYX)-@ltA_g9*L8;O*iswyw=S)VJQhn1$$w|9)NNCF+;^<KUK~cAsw+@8>+!s3ul@NW=#~PdP=D(Vf7D;E_Yk^u^Ax$h0-nnAMuDr)^}H`-{O>N>A9?&2K-XFil>6+*VdyVg`3T8Bsv_#IRWE)>uFIW=pbsc5^TxW|nE!3j>!Dj8K9~G&3ok_eNp+#?$%Um~zAB%9`iA_O42&x$*L$b=@_glg7rLe1JB$x|o<zAn<Vu0AuWlpbf93B|=apxmTkG9LU5wIc<vK7{ivD0J_SYM|lj|(5uN*h}8{B8@zg3mz*pQxb+<hg{FP3lO5pN^}iC%M%To+RxOFc^#hOX6YB>k1oD&suKSM+&%Wt@L3BG<k5se>4w^KVOiJ`5X)cCDWy`o2!6v;CiGsI$FrYv{Hkf68;z!K@e$+LLb%K=;lk<9Y9F)L*-@7rLeMwacO(UxYkOD@c6p7q~AwR@ac{$sQS@>(83VxINK$EinGre#Ea%l=_6vmHI5$2wi&}DRp>y3w6*h%!h8B(?G^gRNd{8CkDFXW*_PI*;!{Ju2oaX|EiMo*ZUZGKZpy2Zsf@;*WKE)(2ZT`_Q|;VT(0+++@qmCD7F`M^U5my)a@POZBZI@ZH>3Y_ieox?X7$-33=Lfmgk2v>EwCi=xFE`Z7z;$je8_{B8NdYM&*+0cfe!R&9c6`<XJKi=Vk9O9CdTF4}q>X$t34<#ZSgj(;|}p*QZj?wrS<LuCy<7`-WXo&r*M&o<_zGd!Uz@Ami$f$*8C0hv(3(kzdREY)Z7WGkB!L|D09E{V(_A{UhJ|-DuBUiMRUJl=z7cpj*pX<^9(;n_OS-9ws7Bxz@ZtUYv~fEWZZbGVfcN2MRrwd0_Y@=#Eo0CC|ZSGEbHr1l?#fN5*GpDXDX|Hj;lwkkqqwB|N_wlk-Xb4Y}lgUAd|}H}+4PDA&6o&!uy2pgy*If9;a%ZnxB@`6SfGk^hY7x3Z((^(*ZsV4UUK3f<l)1?{)S1j+M{V}r!cY>WK%43C$iJrR-6_31IvzdKSe&shElg>IWvQs%4Gm*jn6Rac4sVWgbzyUj8mhSrdH|6k<&=$FfKfBdm9bZhK3>GzKQa$ZexNjslU#(C+(Hg7|FPye+Y?VLIp=Vh6>8qcfx`5U758;yADz}^^#*7QGag`TbJRkYtL^9txydTl}eOiQ3Uc8<lmfwlgd&1g^U^w9Ot8<HnzC3MS&{qp>oY3h3DlaFsiey?L_kNr%BRoH()9q86vHLgiN=9!Q4TJ?Mbj@w+nfpL=D8PEU5<|(4Lh?46xed2m|U0Z)d+WBir7wB8;(DkW@t|QNHJ7j%kM<2=K7Y*I9u+?V7?+BGVX}?8#9D}xOfxfeo<f+mMy1ii<)Y+EUO!Vx*&@Dmz)*(KrEOhIO707R$G7jUx*jr5WG(R9-yZx)I&+N}7?J0E(=j*80aSGy-->pafVMC>z4Yx}EL$9Da=J?BfJi@lqUDy3vOMBk`v)*0T>~Eybz1N_>Y=?h_ZlCZ}&ewANYs4Qr58e9vARJd8RA(;YPaKl`W3x;9tNO}w@|_HlC*xJL-(H{&t}o->YrKD0jNCV&hnCt3J!34Mm#y*l5N`{LlIP6K-9^u7m3C%qG!%OF0?_RTDxf{a=~WV+(_8d!cgg&7DBC9J`ETQS)B60lwC8AYdFTO!pxXnYkjI`YB@B9%%%ablc1^CUwUWQaV|kC?xJky<uECPO(G<C_E~pP(`)jhiU$p2X&tE4mNc`XgymuQd+en@l>!p9MMauhc@VnK};~q<V<IQs1;8)PK@pm!KZMAMVkf+;u58XPqimbo&*e-c$KZmZhJRx<C{)qkT(fQ<l`fQktllUIcwf8?>@i^Z(ndCTctEWJZ{T=hI9vFt})t=@p+HV=wAJ4=3m)Tb!&!&@7=dnY+#Q2!CU^(hgy(a2xSy~6r;rg;-(Dl-*rOqdw$-2r4ALw>}i_8!GhM=ALhNNZ4U%*?&=Zge6?xnb;(1%r&^Gd%Ib<nRwi+-b@TrXn_qW=1|zR>MY&&&LlaC#i{+vOxaISX`4+8c7d->+UG$Gs=dMGLEX>h0ogNWG@ZdA)ms`PI@n1a-5-RF`(9Jq}$vcS7RNZ;<o#nGW6h<PXswy_WZjf+=_pw*DpK-_d%ijFSqTpxeiNFZZbq-qKI?&M(Ayv|J+fY<yGV!*sm=X>q?xo<m>A{j_HybbGr9nIFz?m-sJFeud*EjFtGRT_rwtFLb>^jHiBd4c?QiYu-!yLo-R9Gu@%P<^iLQzr<h3De?P@qRzG(Jth9e+quZ!=&X!?pWCBwUf<cEYcXw*M}IY3)(w6xDf+A>GM~ThLOm~ZyS`K2UvA1e)hE5=S-I}^_nm?KZ}!iDKBO_9Ti#3kKPw1bn>R}4rG&+@o|7f5#K-Ty>T&(L^n^(=&gaaP@lfPPyszjfU9Njv7qyB*x9({x_20Z7_0c;wk>}j2QKDBG>7nb-6J;Jg*je5?qg%{EeCDsD-<LE>cGvB`%b**1>U-*4YRLTQNH6-7H8U}8w{6C_brhBLG<{Je=vt@Fa{oQp<A}TNh|MPPw;IcM{&;z+yKb|7l={@V9gjTIPRaaWt20~1Z8CIAyXlBGvPVgsBXdng{IWc9UK#Iu>I)mndCi^Zp&K7RPjRoC5&dow>h`*fjN1yux*%@s3Fxl*S@)Sb6ng9i==O?3B|b4q@+9Pw_@AVnjtq~J-F5qqYotB#4?T2kVUYBDxA^hMzii7y<hj*C=A|`%Oa2Q*@Vx1$um<->W6NgI?=Ol|y6uk`sSoEF<NJot9Y?cD{VhJyk0nOMBEJvscLAql{Iw~G<J&W_ol|a0Jaye?lZ-d-6wy1s#5mP<4HCU_q>P8K{m`xXvv}0OrE7o7^V_HSFtVA%FX$lSt;o-kC*}_3UF+1%S3UG85uz_CA@}`)P1+uH)AdeGrJjw;<2?0*iqP#5d#<_nqrT6;cL`gTwWz0K!zIo?BYI-IJ?ky+Q@P(Hy6ak-YM3|l7Qwqb^ckIHK1qI?<gVMtJQ01T-6OyK$ZdJv9u|lD#HT#GzkHg9UGYC`koj=!OAlRZbVcq{or{LK=dsrQ+;bed^4u*Z`lFzh9`S+IJ^JNSepCOtbp5&Kc=(im(-z4;^{S^nb+<?TKjmN4*rUHb>A}Gs<KdG&ccjdplV5n`w+<aId4_B{<Pkq`qs)gp5|4PaC#f68zjfnpo;shat@HBEac_?;EW6BC`6_!H*Vr>q^vt_Fbl14DmAEG3_T!tpxE_o3m-n?57i3&Ly4kDVe~rV05q%YEHNTVhQ`bBb`yF)i_;=~%ac)Eg_d}j{pUJp7oJ;ahH(xJC*eQu`86w{=YX2?cxlPsZdjD}f8uh*w-F*EP{4)Z&c^;siY97ea7wd(o=97;pvW{q;m#C+jmv#&vgyWj#H{+w<Fto!o9~$5P20hjMdB!Iiapw6pJP+2@Qq9k8-iU6V|EZ^%|EX)<`#k&0rJL^yfvaPn2YSi6ef`&RKP}-m3UQ|UkzS%Xbp7;R>GxufJaqGYP0w{e;!XEKJ<D&<wf7k$&#_l>T$gUT|9;X<_g|N8zW?eOOJTiDJ3CCqxiuw8`cWH)IMaP!-!K%q`8h#vYLA6}=!LxRS6GYp0V8`wJACu=hVLZk+LanIpI@pi^LcWSiE{m|Lcd#*LZyGV%!h7%&T;AH=Nx10_t4GHOU8^XlTd%t^O#FFKaYLVP0wRS<P5BznV$oV&Ta5L+)^-y9QXSJ^1Rw%3Ut@J;V76j*+VxyXBxFyVqL-fTxtY{Lr?X5>(axMJ;$?4H$C?n6;?qvKR@eP_ThIHmK^=1-}%0v``&<Veh%0FSU3&3>3QCzTdN01dv?e5KI$HCdd}B>O@wZKU(lZv#`kLT`-Oht8Fb5=CQ|3<j?$i^ov`j@eoxW&&6f2r(|e7+AuoQ{V}1|P7p;eGes9tzR+@$Qpq4UjZ~q|g>AvCkPMhle%Vz}iRPSp)_rf|&s`tB}hC;Xc4fszz)qCQVw)j42jSi9cM;~RpUFiYczPq!G^M@HE&xJA2Q@w|t(4kv4HOKwYdh>&v*MSUJ=W`BFSx3$EaJ##n>OFTy1a!x)Idc7WZXo%$OoE>3eR)AmeBVp;ex1+<y1m&D`CUQ(5NS_Blza~~y{8*fHh(3@^L(#2VqZcx+D(-49KKidm}(1f{yrCEUOG^d?<4J@o7WRQ>8AArqxVD6P3says5ickX&ZDo-@sw`J%G_Ir+havt#26Jib}j`J;Vs9B)Vz+#HieFk+jouy~QYXP`(S9)@O_ox1gt5&ncwg`-!%%mRzUz1Mqt=Jx`Oxa{Zdtg?vs*ym=kzM3!an&FfCd!O$Hc=j3-Uzg)ojo4)N7^i=Cts~TdRUVnC5=7(>8lsroYLpQI3=@W}!{o9eNqxA2Wn#4!%fNow-)B6_0?~II<xn-QhAC%)Z48*#%dA&{#T;id-*7x+P8=#xl1NF)$<o7SG`;phTlE2)~&~1r!(SKSf{k0$+et%&plvSQ{%7^2-gE7|vJ=Hqoobu39ty|9M0zK6_=a{FG$Glz|^G0;@`s&Dx_}zi^^l4c?kMSN1eQ+!2j&8~F{QTgEjH^CNq3gY0%6-IplZ^kKJ0y>JUALP7J=HpJ$e*H{*Nxj%!FqhEb>`M>MK`ZYTdrZfJk>h(7muK)TKD!|fOYy*>*N{NLN~9g8);5Uym{T8daCvLG?$>KTK}hRUgtNwQY63mJHp3rC4cdg5+6_k^QrOSSJBPiBi?_I_M5(681K@dU8%lzytY73^?l^;5~7>Frx<@$g`VpB%d6VZQ+==bt&7B)zxz-(fA=w7hDjdt_oJuBL^pqLx|c(~Uzxs785ib5H-FF4=Z?g8IrH}~J^q?}|2KUv)5lcCI5mG?(_0?L`I*1R=~=g8+?l`M>6x#HZu;J5J278=?`is8X{)zebklcFqre3`FME8?ZR_!??wXOUKC={c9>Qrpn!nbsr`u1um8kw)_}@S2?qB8q>nGiT)hhm9f6~3p*@lfy+eO?&zKcAOxPd&8d?#@|`A+if#IMP>lkXs|CEr25g{JsA;%f4B<PPFWa)nFD9ptNsUy-jOUqn-UE^!|DT=Fl8vE+k@gNd=^gUN>w?c_tqhY=@`4<nBzP9~2gA4Qx(K8k!AaUr?F#pKh-XAqZ>&mf;gTtPmIJb}2JJb`>RaS8cs@|na1<TJ^q6X%mpCyyu2A&(~?OPorsFp7LE`2b>X@&V+b#LncQ<ZXz}$lH+DC)OdaPaZ%lM;<_4m{^otVIK0r<T;3+k>?=yA*LhuAx}^AB2Q1AmZ*`ZCC@-iL!N;=Gx2kBg}KQyljkCqAkRf!oLGarIC*tq3-apZEs5R8TatGt4kA}Ln7liA7;y-B7<o_PF!G+{{fN=z{m3JTqsSx3M-!)!E1W?-ntU8_7Wp{xIAQ{M9Qh>TZ1PFu6Nxj)Cz6jRPA4BvK86@iK8AcGaV)vQ0puge!-=8f;pCl&ZOA*3HzC$1Z$e&~7(iZ`yb!T4xxyUeg~<JhKIH!7nTYAhGm&Q`rX|lv?oG@<?oFPRn3-H*F7mA8d5Oiz^OBb$Rwpk-UYppGyf%4jVs~<dVdSmJ+Y)<{w<YgL>_^^_ybCdcybJk2;%IV(<H!e+4<*Kt4<#Q?oJ2mHJcc-tJcfJ(aXk45@<`$s@<{Uj#F69*!^!)ThY&lFhmbcXHX(0L9!RWA9!Oq{ScqJqKY20ooWxAzImxpSGm>W^_a%Ch`;z++vyv;!OYTQrfLMyW0C^c=ZSpeY^@y#>6}Ba>N8W(gk-PzUQ(_nLrsQ3T1IY)n@4M0zw-JYv+sOM6W61lE_a%-X?@Qi`7)joXya%yAd4KkC51Qhwh|S4ck=G&ylGh?HNi0TQjD1;>rg%PL7V>=L*@(X6*~qgK{mA{;XW40r7bKP;FGya2SdY9O`=$a-@hZfo<W<Onh+WCMvJZl2ink~BA#YC}OzcY@Ox}Umi@XDQJ7N#=9;|gcn&MVsEpjV)X<|w8lB{WIn&Mv&vyp#6o}ZYVJUeTbpQd;bVg>RFtWgn~;&q8Z<Uy=OU7F&Jh{5EI$Qu(okT)i8NNh*mj_2Hvrg(W`Y4XxMxAHW_EyVof`Pps@P4TkCy5x1)zOppMs}UQMS0k@PY)Iaa$F4-QkXx9m68Eh{zoyeFI<2bHzIEEKPBVzg|Ak!PYqxDb(-i-k_A6svGhRJR{!Kr#m!Q%<^ZM8SjK0#dQCEH@qSCUs`B`X6&quDXq|@@!FUj~U)Jig@KG909umgF0@`l7d<PFI?5(klYB=1jCd@gOV({@u^OwIXXtu3NIi2h=l(i6!Oxv$c;&{vpDo=C2f>x|z`evEj;X~)Tv>ASWarz!0QP4RtByGUR0YvfA1O8+8J`R8b-opy=ZX*caGb%iI%FOgqx+D-ZwXi7gs+wZimsqLqx_<8!u4mfQkwF7SYO744r+iuYmzf3#NcAX_ZN&S@5?h-HaJWi9V*!$#nne#F=*FGt3{zIbD9=Q368;n!hJ#wWzqObUMa;1GkU-8>cOQM!UUGZ^FTT5*P{Uq92#;u^Qa`a$~(&C6a$a}c?D;VE}dJ|$7?(gy&(|RyR6Z(O~P^VQQHfD@#TP3$`6`fX&*pC=W-j93^F^+r=xoU599$V#ZMy|AW^cAm5U-7=wl^;T`v@hu^KAc=>YHY0}U&(EXk7P}hznuPX#w;fv&X^ExU(UW+OMaAifcyacm5e#cespcSMXvCk+qQe`n~~hF3;8&nUkK|G!fj2skIJLQq8g)W+}<G`Cci^|hPKsd2dQm!(-NpF{EGY_`39Qevx$?*XOlM|s%>MP)|<ZK5#%l{g7FQ=OF6AMxr!-G-kjSasFfi$XI^!zRc!xi@&x*;xIKY<6=Sv&_mV5TLcX2+1i8Y^+;=<qX6if16)vHza@&59+Z662SLh&DxQu)m_jl<Ns3{x6Z4=0q7Us0B^e50CL+i@gj3F)|u5#mDS!acf$a|AFCzf|wS*JB6Z^Zbf<c+w!jN3kCxV-}RX+hqUyeZonMy~P&F-C2-(RXo$-DxejUlg}>Cs#Ov7{+?Ie8uO{caYDdKZ4sG)S{?ObJ`4Qv*^#H&0yRt`YPWP#wcw%eHT}_j;8n;+AQw7j{ZL4JhsQ>E56ieqZqq~zT!uS`^fjuSFthVF>Ht8yPUR(amn;ue2-g>O+1Fe^-f#hv~A>@xZgJNP29eeINxa#89U#!Z4_}Lxx#SraQXv@lgQ_jyR>1{htapw6kkZ3Pri_RBe_ELT(*e*7Vf){+I+TqBXJw~M)F<cySVQ#?mwDlXC7DkM)SOsKZrP*T<N`d?tSPFq83g~@mR*RC+|hBumi0Z<LfwW0Jqnp-=12mo8F%L<!4Mia)tS5id$**7@v)C`N-dC;`=gBermp6|LV25Ed#mI-fQCfGXA~xub#$<HN6CtueR4BS9&exa>W*5{CHvvc`f?NT2fcM2K^%BE=~E>$g8=<6r``PDtR^Xw&ZOYuduVzg2~&^cWn#ier?>gS8-Zv>Q$(<q1K7}w;@+rH}X#8gBhdzA;iJt%G6vmoqRC;Ncz*sJJSy)k0g&|-D1e6Glx3vQ1W=@jHf@8reb<JZ7Tg}@_4tHp44X$qsXVyS7xIg&3GGgx1!&ZJcvAqF{)OTxvd-hRy3stkOy!dr4^<hKwgMkVFktokgM%}+@>t6(~6S&(XT+iDC2W*o5J+u%F;33k9s<yip%KcztY4M|4S1~&ltrO{z=T~G;eOpLEp8_n_S@^L?1Vvi+)aWZ}KnbD^u4)9`Y~f`_Naqg}Q4$<yRqBSe5&H;q~v>x3C{7lNToDaI2q%IemDXG{hoqydeGGH95~eXg-Yjo&FP|(w-1Ca%Fd&c8&Z6{hRca{*?SC*GOK_SNiYdFUghmjJ}IM<-Tv!?p~t(NMG@L#GB+l(pRxB$=^`_NK|n@x%ofQl>Ugi@;?xj_Pv|`Jx%EkXy3VM7pW;cMt++y52)RC<7eqByhX0?8}i%a-x1Ze>u&x-+Bej%Gv*L=<)5J`zMpuA{1%UWh_=sZd&tky-%o!JO=(+cNlsfsEy+zg=(N2~J5HX&nB(M0+`fi**lC-|uhKtA?jE<9rnc`U-XY&jet`I#`~dlV+FPgnM(wSemfbmSig}5y_*?4!UJ~z5tr+7}ObIX1m0yXdv_LmMkf!wNwBk-HK&`mfzwhtWsTZLBIWaf+=j8urf@#SW{-6n0rubuG3i)I58^jCbH^@)X6hGm#Wcnv)=bd(%+s{!uNBso*_ALE#^v~0ju9NG`bDI1p@uVBSNdFkQ&K$?wV%2qjg!`N%S9p)xE|R-quQBEb`6c2N@=N5Goz}LcR~rAc|F8ct^4~x8OsjeP2a@JJJ%5(uzUM7xu1`NwYTGhBev^>K`A>bQ4^S)n+W!DNX5Aq'

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
