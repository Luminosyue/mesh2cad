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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_004.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_004.stl', 'source_sha256': 'fad6dab7ac2cfab5b3b4a9c2ddda7d93649dae10c2b5cf38ec2b4c08666a031e', 'input_faces': 960, 'input_vertices': 566, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09171456098556519, -0.07911732792854309, -0.3044366240501404], [0.17859895527362823, -0.003656262531876564, 0.39748603105545044]]}
GEOMETRY_BASE85 = 'c$}r32XqzHw}&SIrAp{ZzlikSK@bNNL@81ds=!4FQUpSg4vr$yi+}}0jSZ!SzgR%pRRIyD1u+B>Zs;{smCnna^Ub__j(Kan^&V@@`u)x~`|h)I&diy)GuLIiR#~zZwA8=SmQ$r+<GFP$OSarrL2G3Euo3-Vh#y{UaKe}<E3eDtpQrQN#<gkJHOd-kjVs?Le)tQ+%0C(?-?(ps@>K%m`wkg4Vp#9Ny@m|y6ED0)@0W(hXYk?udMCtZv@6uDSFcK-cEu`z34#CPznoITdt<+SJVTtbecswEnihB9@ko9~@z80-L$PyRZr%F*U6&s*_)YjpojX0^-8}aFvovnsRr&4HCH43hufFN#IcDVPtGIPe@xa{ARG#swUn|>8jax^^bE=fiM=EaTQt|fWJ&He5Zn2w(zsu(_)PLU(I<MApR%AUsuL8fKc;dq2s{S@AzjJJ=#;voA+wsjhKd$O@PV3xhqVk85jXcHSIm@WOH)~+6%a^KtLqD(6xU>5yRp%ka6SFr|yie^9-M{y8oW|`0H4fHKS2S*2uR6ueA7&hGJfq^*s65vCNjgtszII;Jxb+9~wMXa95S8EFrSgPFIx5e4^6yL1xHXk|JbY5;v-x{38+@k9?|iTF1P5(Z{WiOl=+<*JPUE3cjKjhbsTyCl?^TyacT)LJ{O0oT!{oU(UgM!P%=^|Nsgc}X$#K3z=T?W`RQ@9>kJU3p<=M_SJbysr&LYO`WyJ#>qu06hmQnTC{XW*XRg-Z`$djt^`_yq|_tLr3QPtygP<etetz8}}O8#S8bUszp8M=E*<5oGw|ANk)vMRrQMdh&<CaCz_IX-sz(Kwx7R_lrNvz;2roj}@HH~u2)+fU<FJ-Ns;YlOz_kJY?5O&h01a%VB~(p=|ODV5(^r1AtOCh~Ww{MMB>H69wO#@W7HEj5xmgVgaEI-+xH;}Mnrp30LrI!V>ZJUXS1Y20ebywrdXI;iqj;O{NCQsdT-96z=?-u!rupHMZOTYFVKq0%Z(aA<|^-2IjKdy}{5JeE46Zfo4Sr_LAW+%1heY2-hm@`V1b?Q(m6s+-@r8K?2kZ}6y28h1EPo%C+0k=)waZG<}x*T~bovC5z4psGLbK#hmfRDSEct#Ru#>)7vcsgc}CV;xI1cu&=DC|c!DOp8@{3aEbV=C5en8Nl`8pBAZF{2*_gf6CzGe@^8IhR3V%zpU!FFTAO7dmi)d9dB@}s+xD}iott#Rr#~bQ|re3DJoAR=6%!wjaw7K>bwgoZcqJE)pM8eWZm$1xB=@%P^~i_w_jJsNocUntzW2zbu2N*HI*k?ji<9IN#j;!Rc9!CQs>9i@n)wR{5<*ht31}VZ0p^5`K;R~E@%Dmxc!OZw$(}Jt+-yC9FQ8xt!}XiZk?y}JWeb;o$F4%+%69-Qu&?4pvLVN;mulU+?mPoxhy_a<8N?$t~7Y9PHw;U3O&D*r0TIMsr;dh52<?IQvF(m2Ws4Y3BJ?TxYdB;c^Bt}$Fp;NNi%pERgZONfSxC$>akN*e*1P6)i3knu%7$eo0quyI$y-`-&(Eb9=D$6di1ElnHOuJp5J<sdU~t;)`cc&eC}7rVd$rI8h1*w{(Pr+Xmm@J=MCyVK3?PYc=+9F8c!_6eMPcbpZz?|xo&PW_>4GJ|0O+t#=y8dl(V|3^JssU2PZL)dnak!nF!BcLF0A{)`9I8HEwNE>wvT0;BTsa?X`M-t0Q%mB>$;7D*xxq<Eg0{cRpf#Zau8Wv#vV#HtX@PGyYd}ZjEJrckB7Bx}1;M)O~fh-a3~D-eVlXr8FMy%lZ&KQ{z?xbv!%g^muE9${#vAL-pI~xSHQ9lU4q+aT>Sap-Vasze_#VER6^Hd+Sw6Jx>m<JBQDtL~{Eq>+{X;wfJCb?jMd{(Re5ZerK(gCs2Xov+-<=hYG_#QTNY&Jtz3yQEi|eKale@+1BIV=YI8{c3QmU@O|faH!a@T#d>&rfX3~GirYtREsyge_YadB>G`kmy|sUWo@YDXD^KhBt@+$Ho;31*%lDC-?e+ZAxDVWC)PIEQatVEWtP54tdKEIpr#s&lTIu6&JqZ8O82@bQKGxZ(&##q>>toJ!di`~{-`JxcKUP_;n|XiG^OWWI&#fPy)@IJT9mesQc6E>&A2yEvjf#ivaR1*bW<zG@qsPtj(c|X%=yT(I3@>Wna&!IhxVirL@y7b&@xY&)Uw6)>XnBlv$>Y}kE{b2&<IVNT=f-*!*wNGF=6ddNb3OOCxt@DGP#9ihLrNq!*Lk1Ea{NRa@y7b^b7TDv)^-#(u8$r!ua6!#ua6#g;LZc{QndWWb<@w^kn^Ru5pP^ieQsP&?ak9%Zr%@g+&<6um%LX}BDr~=;Bl+II=}4lDn2y%J(b6}|M9tT|Kst{2DPp_bB5@7jQb*wJFoG5@MAsRykGLUalhnq<9^9WPg3<5_mdts?<YO(bmn{X1D#SLxp|-I$9Ld9^LCsbZ`^<S+_?YrxpDuQn6N?BZ`_}I+`K>cxV4|_PSX}Ck=(p*_v3eSeQ9pQ8~5`*H}2<sZrsn?YeR|~-)lT>ey{Pl@x8|9g?V0jTwU)xZhqhK`!&Ar*rR__>$dSd&g0f4*3TlhQzCh=CifxMR*jqA`+Q!F_3F$PJ>K{}=yT)ypw9=xbE$g5HwtZZ$J_Xx>v8)U{EZwMcUrSvz4E@6$NXOGaqEcsUThE0<IV5Oe!TI0+2?cMqp2s|R(Xu?^&Srg6n6&fONr#>_kE8$3)FZzqlo{dmCHj>tcPcd9EjxR^9qmKTUoDekJs{;&oMl1&1b!enV`j+&o_L2gLU;!y&m(qM=)`?;>L3ukB5)2p3keIar1eO$L+GLW5@fXX!(ujJU&n7{xI2$H=h4^{hn9%524ppJx;rss$b)Im&eWLT^=`|cX`|y124on>~Z5cn9qlEKU~C!H=d9A{oYdbJBRtcKVyNa-*_JAar1eg$DPL9&s*w#+vmn}LXTTJR6WiGJ^#O+ALdO|dA#)}=2S`~H=m38+;}ePajPch`;jCqkNLdR@3#;9f)QVX_3ipejhoL`or39V+-g(j&buj*+<b2Aar3#c&u8;JE;LWiV?0mxc}@5#J>F_Y{om;In9rY`97Q&{^J6>@_jsrn>*}WMDUsZKPVVzciidtx@!_f!Tpp;$x_6QF0d79$_xWdhKlRohxcU6w<IX;HUORWjYw_lL0Y85n<8#2M$9P|0ooJ={HQ#r5JO@0szQ&!++@CB}_j?}y*ZUEVujBq?r5^vU_a<=jy@}8B!k_1U^>k;&jrTqtPo#e9p3a>C>bwq>Ro|EWJjQz>pO@qN?`b2C@%|_@Y`pq=AK|#V&G`j4-+%dh7w^9gCF$|Tdohn&OE@ns>hb3LGLJj0`JR&NlooHkM+<b_=JJ2N2ZVd)i^ctb&wFzH8mR6!JpQluh8~Yo*Dq(H5pTXvgq!aZ{dmqthx;YF?PXPu@!r$p4(pFIM%{1t+;|`Aac?|BGgW+W+f|pF?`=IED9$=_uA0Wp_qiUoR>2>cr{#Be&+BB>x%vLr&tts*^?4Q6s~bEYE|_Jr%b%eB^KlwC-)sBv%{X6bs^>)>H{W;rc~<hi`<9-^d=DPT)zanW`+AQ%?{WNRSNG2z4=vz$yR${(=KFo0ui<&xc_ZF<@9%Tty}w_N&HZ6<?&qgYQ1u(XXYjc7DaTu&g2v6?Ie6T0I37xD(DIwVfB5fsj*~m<wfKMiF2du_@pr|jdJ;dGqj)^mWu7Pd-2A-<{9nKK@Hp#dD2sX?=yCIRAb$RIIM3@s6TVRK#_v*mK7x7A&+`qq`Fj;VKA!7lSrzY`KBnT0-`jZHZpQWZ`okJGe~07enZP_AJ*VY2f1l&WkMf@P>hb39cKkfX?{>ns|54odJ(9<r=KNi^4c?mj*fZ*Rte?mD{gTg(-!J*x`2A9NbiR<A{{-W6tdz#h-(Pv${QZ^Bjo)7-7A~&1@w+mg8^0^_xcR#>kDI?M^W%-*mHFKGU72&WoZ`ms;(TuWE-qYW!xp#S^Etk7`QD%Qx}SR#Ui%@JCoW6Pl!vc>?efH@6}MV6ak+i&Y^FT0_EVQzeaW+QvdgU(Zf42@Uo3EWXc~D6hZSFzJvlRO^?t*Rx4%|AFtg24x6XeGBxlBh1;(lP(~3K}cDdYYT|7B6Zf_o@>MXU<<>8nv%iO<nN$KRwxYK8l8i&q`JHMY)d`Ow(%y{B^164h96}R4hd3j`hlY9BCpA-*#bZ>cN{U-P758t59fU_cUd`#|*Pq6GJ#oxZLB69pq?vMY|iaS|au8f>tlY8^)#FMA*oRyKskIB8`Cvk-0iDSNA8F_q~+&ez)v5JR6Kdy{C&I1KzZgt0Vc((T<$0zu_;-Lobxa(D5NkAQkM-_KQmvpZ?!H4$maqFBt%jI?l`y-df%y+pJobB@9JMGkS$n(#+JoMTemH*YMOSF1sD(<vt?(%T{W$N!*qIfWUisHp*t9jg~c(~k6mj{a#OU{gkFAi6KSDv}5-=tZeyZwGsGdVNv#P(4AKBjo$vaH(rU_SxBoL^fXOzw?;u!G{ktPQpG!Q|fjnmk;fxEjwciaV{IQh7p8CTGU2R?n#V2lIEm=xFPV$^GMS9{v7yP+MnA?jPq%`Fk%FQ0vB!4yv9_)bmVBZT&I1cYcL0DQ@l9uB|^N_m0m{mN!+uy|266>E2zfC*>8lcXiO#C6jyWh8<Kqydcfxp=0CrWy&}7NY0FV>zK*?b<B)!TQl>1Hy3c{H~g;RPWJ?D-7~pYe`tf^f$ck%M~;KZt(JAvyzeGYubbLBX>xCz6Qk#;aXT_rTPIEKuagfd9&V7dBJy}Jd0=s4wQg4<Puyv3T{XFPyoK8<ZvD_qTUSl)9nXpV;D^Vpj67dV?wv38VEQdPUB&-1Y+t6F^Vj6w`D=3T{0&Z^-v+C-b=&0Lx?xRHJn+gUZQZuNWIV^zUFCAtF_U}iSm-=F`e&DW>!iuOb<!$2U)A5JQIeZC-Ac}kd+V@M2YzUR%Y)aCXUe_xJp7pA;m_Yniu}9635tgb<XY{H=lpK_GUcP|xZ{}^T%gA7>4yJt<4V@rml^l2JAqnnsdZyu(=XkAZ{14HjC<Fw@Slo@{w}h{jlZ%kIWz8E2koA3t32D*yWEN&oSYf=uBXmQ#jUlazH;M^tMl<++`I4EuDFxE=~t2CW>rtw=8osM=RVbrlg5hMzfN$u)#6g7-0AV5y8Z?g4>UaBa{F@O<ji=u$Y^!kexP`$#mk?$c^WlJ&Wv0AV%6V!kvh*cRoCT8-I6ooc9`|5;{lgD6`Hu$Wvk1G<jlCerl>l8wkV$Xb$9nV<@BDCoEcACnoZT;G}YzS-nZ0s<f-||neot%x72;h_lk!TQq_7s^qu6)xK-=AI^LQcR6K8q6_NQ(?&sg6xK*X|%E<an?$vMA_(RR(x)G})$H(N}_*e@R5B-&p6gmDT_r~8op}4cN<m$-zHMu{(We&MK7&~Zn<nd#2|M+=I@zC@|t0Rw3lY7T!VyxofTFY1a$9X&Lzvc=YE<Mnxn(>j0Er(Um>f1ZwKjjiA|2)n7KjrFQ=YRE|ay6`1<Ny1gaz#`2eQfeC2YNrgU&i)A#?~5r3NQN$5F`Ep+7qKJYf#4adX)10Xg{B^y^^u@$B(8h`&$tsz6I@9h?$2@$IJfG#E36Wdmb_Gq3_^J6LZm0de%~2_J2f-_z!4*g#Qp-h(Dh3nGzX#-cr7BlxoZVw}=rxm$vMan3kxGe~Xyc(TRAQv1y5ap0?C5pWLFe@rS5EY7w7@eijll7oCcieR;?&S|2}`n2G2}e0^%L@ttUoWS%DCpQGK0d3qk7K)W9?EzrmCqluZ0zJYH+OmVazemXJlpfmBsiII5~J!&aGld*e;*!i@jwl?%B+7mCeb)-+xn)sgdmw+Ei`!Qk)qPg&I5Hk}Ui!Vrw)F*n-Qhp{e^U>GvuQ7j~A5Z%?=33@l{C&*lc;;_5emL#>n7=&u%Cv_we^c>6+Lalj`uH}qgN)Hgd`H?++d%phjmK}NHmOnkP1^DFHy+=Ww(OIb%4iw-?@E8e@$G4sp|;BSI<$ktbVTdn+Yr+eeHP!5n3`xsd{1JAqMh*-na7%Vi}p}r#-e@j7IU2ozspkXvBbQF4#Za=Z#{fg+EPO`a*H;^XC-e%{B=vUI}_6fZHl*ukvc@T;hR!JA7Y=TJrEy{K7kK0r!u$Vuh4#id5R~t5$&7A$Xtm=GjCmqX^+;xM>9`l@a1T?C#D`+0bh<Ws)MgadoBG+jpFyvE=qq=qxk%^_fXpvVz1I}L`)4d2VVA<qek(!XxAX70(!?%UiL{$H8dNwRv;!T`WIgIWn&IS^WtUSU(BIsGCnW!*O1tUXkRC08@dVKl$fW{QutDgjpvKf-cKLd@PE?YLSCsw{07>xPhuWIPvDb@*@S+Lmwggb3QfnSGiRPZMSBhNBy%hNJKC~OV)CO$@Oy~4ivEC?{W+Lh@hP;g5_1dPftP&}bBEYp@wbSP@e$pRzeCJl=oY-hEF@0!J^WH)e#Nh#y`Pvr(f9Ey7{@L6m9+mP<^-CEU&)wnz^|r#f|zvlBYZmk6#6NC0pqv^{}%02#2i6C!+%H259qu2BgCYjpW}ZZW(T?upF+&9=u-Tf8QUysnUk@7$=@b?D*I-_=fGcM-y86m@bT<(;BUZ3ux~Wnfe&WiF!*SAKlZ%@9|nJceev*@;BrqV_nBwm7vYE4cNBgW{u}!a!jHnYvu_vtAUwprZSY<2wd~sj-v(d9zOUh%;0xHd8ZP@|GPW!kTP}Qd+RtWeeKWRa@B?XQAtnmVijTr)Lv!L^%-C9HY|rCc(auIp9yC8*_SYgtd|leI{~=<;7pGl|n9}GYc-dcu81dz4%l^W|h%Z9B3^8@k2Kd6n<U(Wc4H%m`_-APsqQCt30BxzQA$^Kg!UyQDIKC?FO7!;#z69;6^j99=n066jV$g#42E;szcEraJlO4^Af0mem=umuiVzQ#S@mcXX(R_HB>p{$+XghpPV)CPf@U4ici#Ehd4V|e&bQHcQ{pH0!NIN$^A6g7AH4G=WXe>S-F@?}l_*iOahku-QAz}h(MSMeIDxuZz0b;76HSv{*DS=kN*JPfm;+xSfK}<okB)%DA)EM8Hc1gyjAigMVsqG2+6nzX|gZ?Vwo6vrY{;J`t({4h4HSsNIS0JV&S{dJrn9gVqd}V4Yi7!jL2XoyS{|fD*#5{;TjDMK<^L#nl<CwqU_-?d|5mO4Sg73x{#p0i!U5c2BXbrs7P>()EYvXH^*Yovhze?V5_@1=O5mN<igzrYo6KEHF6=G_jP4Qirrzh}F(yl>F6SO)0F=DEtHogflEzqv`>cmt=AH}yIrU%*^UzwP)Xgz#y=ClWXGHt1?6Mc$4hnL#A)2C=0zBw^n(I7sK{%m}E+Clp3iXTh6J+(cGZ$o=5we`l&pxuUft%rY_c5Qrpv@L!L^Y<!#4DGheUwwQB+C7Qsg7(5UBBm+Y3Ezd7C(-VBsi6<KMF-%ehS}s6orZ5qOb0XpKaIR&@RMjKP(ug&NZP%K>5fjocOvFFbRxbxF>&b2_~(cTqOarQh-r@w!3T*Mi%!S4C#DVBA3vQr9gCk!yFX*s2H%Ia)Ub@)qRa78!(wuaet>_SnCa*${19ULqaWf|QNwh667BxP^g%zy_rVW9Kf%vuo@V3Uragd|1at|08Znd5ckl_sj6}b{Pa<Xlx(Gj#n2G2z`~+fNMi=A1qQCk0b+o0n)AT7C#;>ElxAEW8UP8<l=mGpY#4JL8#(zP~GV~YxB4QS!zvGt?vmE^qznGX0(8KuU#H>Qs<3AwgL-Ztm6){QZH~0^U`53)`{}}%XdK#ZSO6C0>A46Me_?z6Kd-1YQVostD;`dU+di+M(vi}0Lh!4<~P5f!J2wvv&Tjol1H(vHhOc>3F-_1O&!(XE<`wuX;;&ameo|vD}+j!Y0F~6X9nYW*b`5l!p`kj4u8K=99(T~*jB=w0l#!GFN=~FZ+O8I=m<V36EuMu+_EsM`djPxm59xwYOCOffJ@v{GKY80P^c2(v&JF$<_mi>GAd&K|4d_Kxt#}M0$_CL(E#E9QYyBTx+AhFNT4&aNRPvT{+H#3Ku8Kd3QP>Fs-@6k^e@=7h@U!X1f?oo&6PJA<Bo<U#2zeEk5?@Rk9YLHsQ-=O^@F^$n~_#4dAWnv$RQtigXR7X4DA7P%N@U>}IC#F1F7hjf`s%SfWUFNJjz7p-K#5{_2!QW4RQlt1Pw57HY^eNg4{|GU)(YE+r^w$9&OS?8P?a&_hSZb?_uSL5DwY9?!qg{y@nM2Xs_+iXn7h=cImi;@KbMdLn{R_mrguaS@3EvkThu_Ei$(-+FjHKO{m~Q9@{ABVD!_S~CH58x@(KJi>8T2=X*afs-#g9X0;s2lpsYUz)%;7j<MxayhvhM-rO0)rf1TnqPm+@7IX^Y0;dl3_hcE`stPi^r-Xm@A6V)0FA4`FP2;3v~=!Wh-U7oa_d{-)q3(3aXBr%%z|_zCp)GX6!{z3DFwKZ<sDVw#}M@k5B2j84NhA*KLY3_qEe8R)zCV$5{`{25ENXArXheINfm^XK_Rv}LZ3G2fzvn9o_nOhM=1WnUr2sSsl%{$Xk;hQDN~w$!kgK1DyqzmH#pCgRUggVZ9vB>gNRW)Au`z9cmi!aqg(ZRTkXeiH4+iRq0Fz)xbHCg2Ct?oG@n)WHvCo?gVarag+7Y3Q5y*346L{KK@T5%Vs(7(dTa&#L74q&(;PkENb-3LnJ2q40t5;p`g)9||AGzE|L*;IFc8GW-?z6!y)4%l^6e8N|#cPW*h@NyN;Bf5pCU;7Rar*|!n?4SX~Ew!$~Ue`4QG_*VEn_NBsi!vA1j8ax$#jD2U|Y4CIGy9Ag0Ycl5G>x}I`Y~qv9Z}Ca^mFPOW=z9E0{Bm?7emQ<AoA}Ss&3Mu8@t@;ALw~@3hW~_3{HJIL|0#Y6x(P430lx(Q1)KO~=y!P0wfJTD73eqk75G(b;#Z?z;aB6o%-G6BXI%R;whHLO_zL(+XaHXcUxiJ4HMAtY8omZv94}fFUjtu@O?(~nA-rf|d>wpUHu1I52l1js@U`(Z*~C{zi{V8};H%@SvWc&Zmcomc##hEyM9bhS;>)v%FB`3njolnCqI>ajy#39wCVC4m$IKp%sXct=6OQ3)eC`^b*~sye%;%E%%%_|Sm-yTzKC_-<EQQad@R=o?N9lYnozJY}csau{BYFZa$6+e@QpqJ=&eOBxJ4>!_ISwz7?*h5L;<!CTzC+{^FYCZb@|`5t*BtW~$#;=l-f@4Je22*;Ue=JK<U2~PHJnpd$#<1pYdJ^K$d^Vg@v`O|A>R>liI?;AFY^6GuJ0J56XZKVF7dK1{Ykz*$t7Oagq!5MNiOlSULE9f2l<S6Sx@fpxjTGDysT*l_}l?LBVN{}dwlL5pAj$X+de+GkI#sgweBvTyUS<1wQnz<+skLfhcmY08QU>7@i)+O_#5~f(Mm7lWfPwZ{Rc0b_y<rcT6x*T$Dq;p7<@i7D?T5-0D3>Z0KO2K9bX7v5Y2`!h|iDShtH4Ci)O*+#pgkz@OkjL(d$vl=f>wmui#}9e;alle;a=~WBUy~g`UTsM9-q<@n`Yr=oNfA{t|i}e+hpLmAbFd7XLSz1uvWUTj+gw*~H&Pv*BeEe-F)$mreW~^nSc-;%}l^@v@2k3ysFhCjKgF;jeOBT}0(LyT~T~0(u#L0e=QPhd+ZqfgZ=7z^9>Md>Z~R`Un0n{t&t!e+Zw7?!>3!Q_x@VDR^1m<s97+rOs{9U-1X<2hm;lgLrR!68#<Bh5rfNhVH^|!*4}@#c#!LL3iM{;D2Nj|1-J|FS-~1Gk$x<)~;1lbipkD)BlR&zyHbi0ZaQIbC{phfA$^u$z2(_{2zh0YjvOeRyyN2iFR-Dr^zostp5U<iRB;'

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
