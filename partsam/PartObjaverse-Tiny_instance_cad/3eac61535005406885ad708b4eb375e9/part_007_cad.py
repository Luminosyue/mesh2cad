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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_007.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_007.stl', 'source_sha256': 'dc360ac6c6e8c8253677201768081a0dddfa3d5f0fa0a288e8b193e1569a1965', 'input_faces': 672, 'input_vertices': 456, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10570096969604492, -0.383402556180954, -0.07587476819753647], [0.07552087306976318, 0.19707432389259338, 0.10702072083950043]]}
GEOMETRY_BASE85 = 'c$}qt33N^8*Zzs2W`a<&Yo3B2i21f=F+_|pUPB_3h=`biW2_oup5-El5Q0nyxn@nx6m7M=N{O*3N>zRD+0S$QZvN~4t@W+%^ILm8&waArz4tqubKdjb`>UUC_8cA>{#DRceP3#{wU(wCmS6MGA_Bw0M-B@dUneAVvYX~Ey7AA%6<vFE@e6R%BDAU1h6j!x7FMmPrCReKpK6|#YC&Ve!o!Ay3?3UcJkZeF4H-Q?Q0e1?hlB>I&(*yfHuAJIsNrduX8B+K%WKr&Q|L&#0)2h?qpcJ=o*Z9ipyqM$u&b_3p1wga_zd*S1)}SBeb<YA>=^X&L5Gdc*5d=#i2i7s=obGOHx1OBfg=RJ+$g%e=*1iIIZX=`96d8j9LKvnsHa4j=-R;Ph~p^Wk2oQsJL0~%C735Vu9b_fkIGD!I60_?j1t{e?gH{&p4Un6%ux7WDvbI|wnY8y`at(uhrAy1h6|qaMLm{e#Ob_ah+w(m@E?8(<CfViLa^(FL!uw3drUqTNtz_M<23Y#d5_5F(1?+Okq4j;{Rwfb9mWavoDV%HUUX}<FEB5AMnYeoEcI)*-Ukb6L!oC@K>Q9D2MNw<1$|8y#6P@cqo5Am$???P`mRZL(e;rSPdy*?J<UY7x^Kkz9Ew`)s_SLuaNb8ZllVEjMR#Og!MM5mwimsQ7yNHOgkH1_;_R&~y7qiC;!G;hT`=z-sp9`E33|Hs>MVMhm6*q+&9Ocg+!bB><tpNzzO_ow`?~11-=igt-hI^?S6#o*3hQuh=vs-Bd=C2lrxHikI1bdE*V7Q+5>;Pt_(J%5`D5NIFNhS33Wc8R2Hn5x1i{gDMYr}We@*`W+&4<};uiQf?Z9~~JVLO|vlJQ6YE8voi!KQN_4h@$m#d68Gk#o#^?Wl0^L`KO<XK*<t25t;ZjH!^IM4nH6%0=k-T7$TRcTjl_HyyxoQk}uhcRw-cdQiutqYL1qXlsqJsl?)Gah-r`V9K*R}rqdH7VjM=DYApTo(h7cli$(&lb;Cq`T<a%>nQ)@#}I|e@Fhl(8C+q1pT@o{`wtQC+FfY@3Cz~w*|ezJXRV6-LDbq{5rS9u{FvOEAivBtnoW|jTY42C5!&{OX$}4eu6$dMc0?L&pMBbI*V?bUk`efYN$WCp6GVw)eEOAlQ{Qk!~eBA#%=Y-34-^Fi|(|IK;DsMR!E#BxkR@fbU$mL<we1rq6fc9lF!FHv(E3zA4GT5n2k6+24Vc492VWadMNZ$ZAYPh2jM@f3-n1B`UrNeA-Z-VUkt|o{wRslsfg%0>(NTLSc-N9p{KiL;PVEIe>imQ{ARiTT6ebJA#vVjOTu-LF9X+o0@lNnzY?XMCp*r`=Z_i71uy?0x;`^Oblq|#O7zN^qH9Cv?ZWyig8TCnC-h?VQGdd-{#o>@4Yvu}c-{G5K>VP_sOM@|)bF1R|E|B<1tVUp7XRr7pr4LJJ!v~JzdfU&C+<N#o{h$ef3_&-agE}z-WH=y&k4|<1?-T1$5hAjan2a%1KlOBemw$t`}TvrYdLgV1Kh_FDnrk}IBR)MEtJpRC80OYyHm#dU1P*I^^OIQcgZN+R|ouiQ1l<m$lonPM{XCr;BnFQA$bnTJdX9oxJD(3?x<E3^PcB5*2DdH_#eKOYWVAeOKlgu=?=vIVHxJP;kd<uL0jQJ>Rafa_gsMZo8e#bDdsEmRo7Oodd=rsu?}w9L~p(naq9U?omzocsM8}7dN)7JZ}3{o*QkMrb7%zS>p7pZ>uW(ju{v7(oyS&*{-_e-aD22)1?CHuvOpgemTdSr?%7b+^Zd}4TSeDvwn9J7y*nVd|3~EYP7RazZ_YyB*GT5q8rlW(+1Vkw{x~n<G~A5%8Hvz8{EB(GHW2aOBtVZl1bul^_+Old_z#nIV7~mZeoXycs?3w4(*&#&%^h)kmjIhg!gGPTHsDWP^gS_aTy;IZVv6J)I2hN>t$+3lT9)JQ#lu!-(Q_1;DcES~Izg}3qFb|H{8m2KDvW;R_)T=(Ydo&IXR%vEuk#D^4;2wVa?C1MUAt9ps_2^*td-BX6A?cyJJxNTyBMGP35YW|1>@W|2KDFN1U+|0<n8h~@+L<>e|iaZMs`J=`NtyfnfACZ&Mv$vi@tU+?ssonpq?eevi7UheZ>E*KlBa0h-1sQ##Pszg-9HIX7%;BzFMGP4}O*Bf^|v$owy!ri|+7Sd|fajJl0j$%KilZYi`h2mP4F*^Wk4;6xM0WLa66aH16xCxlg06c{*f$=)ZTzJRZvqz19n0I`5OFp6W44(0K~$D)VE4w6EL+>nmi+QdeE`yFLx;`XQbR*0<2}oRRt+4Fb?#kKaXi25gi1tsYfS|CuQG*B^lU%;Z*beQO;;kk{>Z%;V!582`;d@Ly2|_l<3ZpuZUe|M0w+mzlkzTy;(BkNV!s!aQ60i*9W*AM?961nX*2718bepJ4n`l5xMPTpaNaufL8us_t;rwH24K-}pEU_tnn-?h`yU2=$zpyex~p@(9++oz)oU*!}xZ|7%>QtIqBg{h#Hc+fOE7+#cLO-aVt?|9HII&#g~l>EB3n^L@>hV+QWK?(utZz2z2vM~nOLPaO-r^Ux%TllK+oCHzLb=-WM^7wZB2Tnh9QH;L;wSOm|{^I^~@Oo0C<y$y8kyR<FeOaHW6ANPnpay9DD;Rk=ujnMgCX$>lj{rIA8qHDW~$~ttk@WB1S)T5eD5&gneT<=kN5oc};*7b{JTU>Q5xYKy76ASz^kIH!HUu2j2jCFD(uDdqL(4XCwemNF*$9jI%3F8-s`=#SS>8)Ax*z<B7=@a7+Kc)cURKmVSyUXVhb*;z*Ss#wDKj5#$$#~dX9>+S&`LoQE)^nlgme>$k50;3kSbu%PMc2nyz<PW1bc?I5bv?5j*YO<0-_r|vVi?A!@}TG}y0y0KUmaUpAWlL{(H%ASpq?Oa)H9$2>YVzG)MI;_9rYx*qn;|*uQ?V4Z*|qR;w7cO*0O)`{v5w6OMe5N>~+;0Z`XV$c*6_pCvB7H`mGF%f9@u@eyM9dVX}{RtUZhR)36`4Z5k_eIy==wo$fObztT#HZ}%uE^RJbtggE(5iLUi-j=ZOeif+BTPIPPcnb1R@%6f5h86o#2yIJSC-$mDbkBPs2@+VnGT6jA2NyBg-GxJuSg*b`HxPSg+!+NzqH{Uy)dAGs;dVj3b9&@m+_RhsPnEJ);av#)N@_MP>6S~jHj4bt2*E@4RUfnA?i+}QQtj}##F`k!e!{5D?#Bu6Ah;#iT_O;ELVH}QGQ0J{o(e3BH!~9k$EcXS?>yGG_=c{mkD|G<6cZTS;YE$sM8!{Q|Va`fie|&$jl-_~yJcsA1bxZx@#%Jfe(bz9icN}i=t)bh#roQsF+(*rG7~AI+vgqbHjI$*5s5Q9na-V6hvplgC)~7rl9K63--|oi!Jv4{t`V-ur^?a`dwKBiRdN<$K9F<z3zvok+x9$c1jHZV<ztERF%NnP83+ONRO8@OmPC}35dlcV0teacl{^D5({`W6sjXxjzb-iO0;=Iib-RlnYwZp~VxqdeEMbn^j9IPjc;X1iD0s8qd6301e80v|t0DW^b=4o>;#CcK@`sDVa+a`a&b1HXNtlw9+<$AGHI*4_Z+7kQk^9OJp{rMhxBHzcnZ{q$C<<Iq2M%J$*IT6?Cg~RaI3y5y5FiX~_t=wDaPRC}6^R7=umb^Y&MYsO77xA0+L;R>-&@1=E`d_#P`r1vKBu>6L8Cmjbl|<J%PtV8_M>~uAawQ*}gEe1;aZ9ZYeS0y{?eBlY_&Bb}b*Ovp#pf;6FrJfqp#Sqmbmy3cTqo~w{VzBu`7GmdLH8O5{rmIcuSZ@&JfGIk>p#SE@X~AO&IZtZ7K?6=+XOu{O!k9%?K&x0;y=H;80#dL=(_2D`P(@%E_>FW5PVpM<GDz5?dEFHE&gs;FWS~w;&<$f=r;3y;@(bl$G;BIowXc^uDZT@qv-ZSf%Jcb_ZhcQ$0dHNV$_$2?x+<cx;E_t;#ihWmpG5V5?#MH1pdx-vfp)_{6ciAdEd5{$3FO33(=jCjH6}9`KwL4cv0HL4&{3279jH!l;@K4Yk-q+x(}D}-BkI4#EUP>b-NJfJ&tP<$L4+(<LtaD=Zp3VkI#$$XPJnj=NvEdQMj<gw;#2`-!>s!=5=6AiEnu{7rJ#5&OcV&l=#*HywB+6<vi7L=efkUwDzOEbehDeUq|9N3nxH#KsWD`jv1FQ4$jNE`0xBx=0!KxzteN3tosK)h_1!HOU$CrND|#)KJTn&L^tpMwl5xFom{rg66E`c!+j?1OSVh1MIV)dyoClKjy?YzS(n%6V18{Ivgqdfg7r!}JpcS^!9Q;Qi7e|RAz1WJ=Yi(<`+Y6CV^2S<6Z5{L?STKwhL@$z;l6mT`Q3&8&E8m_7n`DAUVqIM<a?RpP&E1#6*W(EzDGFfZN_u)@&)MW^N=^NH}YPt@wMdrsAGLzea-7-1oVODQBU9Oe164<u01R-x^>u4)Tu4~M*LS)6W#K1F!oW_>I-Cif__7s{@=r2KQ6j?F5y`A3!X=zlNU;VM|z0A&6oQzi{B!N^XD<de{ux+<q*-$_jHGU4EB+Z4AGsNs*1n;c|?M%Zk{tZzFdI3eo0G2=lO;;^9J;&m!doVxsEs`wj{Xf=6kgD;Cqa}z3Wn`(_H744Ol16g`#VDj-p?Wu5x_p;e49s1J>A$Ja>ft>3g)KK)mnxY{B;le2zQbpMbxmmYiqn)2?D4Wv-tRW8{4L)4t+n8upC|3q^PQJQDjWbAD}cqFck$u+JRI`L##O`Lv_xY0;f8IKLg9Kz}hEam@Mc5FzJqpU(5gmE(PBrRbK|35a9vx2-XvoBJh4pHisDOOx|d$MpW#pFcL|y|d`n8Yd-=&79wJHk`xFABXo2bH0M(vF}+KfcGPF{1e*Axtjf6Ex8{$Z-0gLZ>=Zitd<_HaDTSdho0FD=dXMZvi_Wg{qx!o(ara3?Q(uRe|;9i-`pqnI)Z)7<%aV8q2rrExKHjMi}?C1=t~+%Jz7goT&L%jiEimo2iIL(AIv*-^S$QNe%@<~=;l7we)jwUSKZvlS~93xK8S98-U-i_rY{ak+)4T6`$;{ZD9#_IcyM1`S9Eh<Z7)`w`)cUszS>fpdT3L`={Xk9{W41tr$hk!i~KF)tfxkzzoEhSUetU~`S%BmTf#NbZKt2(ezG+K<6wJ<db+p4_++mLT^qAW>iF<p;#*F<MBapjqC3u2g#XVSab5I{6Wu%qa0Kn-_Y#LhcMd8l<70bvllzb=n<dUZKhdqrn<cyI`Xnz|2YRQ0@bBO)y7s{v^;f@(yl?$Qx2F9F-F^r4uZ@O3&oQ+8JSSg!0XpB`9XCo~fB*b8^s7FI<1CH%K2M<Y{NdC4bySUL*ZLhB_M=Xp4x-!p-^KV$YRvbt2+{ShMba<Jc6a#CpDX&O^NQ~dA-;1Z^x*GMPw5Sa<2(V~eBU>(BM;3k@jcsOoh%-S@k}cxy4K<n>bZUm{Yo7M|M_>s&(@sROW)VftLDW%Ig0a=;{)`Y4Y8h^aKG_((-zFrP<(&=_!;^YlP0?DS_bZiyLjDoehGi>tF30<HeI)hZl0?r^0}~fpy*n=CAd$T>$XiG{BJuEKO5KW%7xIKyRqL+?}s><`$f0(Oo#t%u3PWVwu#^TE4crg>uP>6(e?Hdk=I;TUPIwO@O${1>qH+1|EqV=uRQs9{uU*=_Fx9yyC-rz=*jTU3`Tr&ej|&-$haRJ4gYJLuh6-o>s`xYoKr8LUnQ<WpPzyLKIHQ^xR89Wr61`5{Z&JrPnLt8cn06&1ohsJ`Ax<5V69Hed4ztF=c@_n@NX0Y|269nXTVwLdof>@<9Qh8KH@a!hW*pA6r67lcn$yfg*fLl&rA2@!1tw9bK!aavHT)IzhLNpeZc+eMj+0gU(FL;pMD+V+_5d<*wdh2<M{t^GeO#Kyat`Wi_n+(qs~{qL7z7S{^oh_%69nvxem`og5oC2=jM^3>jjo!9D0m8Ao`Qp@aMio-?j*K`@}*2xB&I{jS7{|_s&6o`6bSM=FgfapPg@@KRAzbkx`AOyXyL%Yj9rL>#CjWQ@-an-z)7^Hlm)}m7(W)ih18#7J6hdbiV)U*=j?t{ylW=W3|)1nD<Hd@H>K*x3L})2lIRCKcV{;K>gpAg@5JjyQDsIKYy6>emSq`ddL-=WA|HZ&!YE<lkvBk<7p`+x|YfJmv)D+9!$Mnkj#rd<v^6HZoa=;Z$HNTp7()&<#Je8zdXkGu$Q5K`hIh*J{#9p2>fs1eL>gxeMk6Q=zKrYT1>$_jot`-#dVC&gn}3ckE>bg)TW$RBAE6Zc^Box`9PPp7{B1E_?_2BymxEX7x+C@{yL)T$ChCKw|67PEwv&1d#=al5<|X{&#9fEzX;&@>{fX%)pC!A?ztQFn7<!LoFck|@7G#vo1U(^ez6tq;|t>Pe6h_!oZs(aeQxeERX!&yV|>2vdzJ~3&wJ8ExAOc!OT2*f-}e{zZy16)Q-4DJJ@fCDywUTKcU6Am)jUMkn*52pqXW?|trq;pFM@v^et)V3z~B6xK;pZ3=$}pWPw$m;`(hn;SPh-;cUo$8tn*i!5GNk*o7#7OU_IE=;LrD8t;#m&ZGJ*Md>_}Ywa2`-c?mr&4d2VmKgE4--94h8?1=Njhy1>yd1KKXe2>;9IuYO675;0xz<(CMXIVK=bWO*5y;klH^7_O<KZSD@?fKxg^4aIO=vJQFXt%l#5&ibBh|hB&Ew-MVn`qvDK<D|AmjB9V(XTg)mpXZ#qc#BeU7WYC=%0Q+lTjSMbGS7U{yaz0ZZoeQ4S)0dtZ#?o`bmx5XQ27}BJCEh-{c?U`ZnJe^wtg0PwJn(=W0oPV@0{IIJn<-?4FoKw;sWM+iL1v^UMDI)9(qJmcjRl)Ia^6unqOzy+k+n^ZKwAS#)zhuMbzcUzT6rHhFk_o@P;0Sst~23mW3`(_8t2rhUTy|4(m6djF4pdfTXR{r~GvZ#%lFOGVjb4R}cdKdbl|WgUqf$WJOe;fBAT;NJ{>(zrB~wIuc>Z%N*UIGnr<`3>SP<TuFcy1@)yLt$+<;E()l=s(g7-itV#ycc;pVqfxh<QIw8$S;x?bb}c@FYzRKUiQ;Np|=~*&d-K!ry0Bvu_bvU@@B*~<ju&h6K{}TCvW5iG{&M4&EV-YgQpQ|kf)Kab^FiQttIXuUrRoZX7KgOjuTH4_mH0^Z%eFA-j@8T1~lg5D$U@Z6MK<=PM(L@jyw<fR^mnSt>m6=Kx1w^X$4vDaq{)VyyWZ2=Mg<z`fKobxBtv#Jk8+8lsSkkiQeQb$=7Q@W4_nZ44#|Vh&(rWabh#_;^bF|*U7J#Yrzd@%y%1_!A}v>$xo3xXz8pso$KHjEsgz4<J`v+=aK)aa@|q(1MxQb_sVW6yG8to{7+@imAxjuB7dUnsj@$aFUaq(jg$D2{3dh#OmvbzWv*w$pUGb{=1bx;@|*PeiMgDN_mn;_*!HDM?FRlzyhHv2+kH>GNq&p5pAest|H0U=Tynf(&Yzj@XVzoz_G+w$DeFWWLf%u^aAgCDLF99lO;WaqIF)>svc<|~5?7NCW1B$YLh|9v6-*2yU(8%9h{5EG7;_<U1^ICL1Tj}2<1MDoYPMbIQoDieiNnY{v0YE%aPonSJ&U-Qd?sU0b;&W6IfI!mnDrQZfwCB7%Za<lqm><0wuyLve4?_^$|8s($tNh&m5n1#BadO5-NY&62bn90xSL#OuGz#S@(9M9LYz&0kUj^PYd7QR^qI!CQ(S7F$bL^`n+5FiF7|sD<3_X32iU&@j5~pSo5uc|IYu&P67wao9)s6ZYr3eiYD5q6D#{8gt4u6Jo=-EjNSgK;u^f33W!aP!Bf60nWgB;5cJji^RgmaTo{hOQVnOoH7&ALjBQH#!Ld@mPc-iRV#<tmAYB#VZu_$>pwyQ!cOkSC>ix9Js7h~*lE;-6EXF=vG$a)MOt8A09oy2JJEy^}1+e}<XK2q5vWr4&{@===c9jm5&MGPR{#5Nm=LF5~lYYlNDxsAE{6W5RjGG-95KlujwtYfZ?jAx@y0NVz+)IO5^9?3Sb>~l2x9nH8~*ynZZ-#W$}#l8iw|7MO*=3K*kYgmuL&nrt*c7b?={5xeS%1#guk}p)YR@qGA3i6f87ARXz)X5XsW-oCzc?xsI6ZeuYV6Iujc=DNyIh#0(JcT|7nQJfOEufFiwzFMoU&wwhWSjHs^AYy@2;+XoJ|ATN4l?da_DyI1%^WM3GoJb4S&zX-DC@3lDAA96kTPFogNdEVdn+5QtPgPv`7mWYlm!!el6PmDPDFolU*>8}>_py!xw;ZtllNgve_~g1U;1=ru1<{CgFZdk*59S}-t2d8wi&@b`?24Cj5~;Z?#%vmX53-yTTk}i%rS;JTQgs4)?@G`$|fpXOq@c#OxZMLi-?oSyC@r?tUa+G`2c0zlno?yB%jDO<B4s_r!iMJaXfi9=ITHUCvVS~ZHXPor_pCJbB$-bZuIHMwryQ%@4|j}VVfoF^Az@b3ga$gpC_|_lNoma`__^DH*@r3&T!@nXFUct&I0NvYfh|7{)Mu}%DyD}kXKjML|F}DQ}Pzd>MOGny~yjZO)X+o^2W^7fLM#XK67~z8<5vv%&J6B^2YS>VXj(?SD!v!Y+Kc(_Ui0+b+&26KG$Wx>oV>a?6VL1=fk)y*f%fs-^|gJIU6uv1J+~kv&!}<J4H+)KcsAzvi-#E<a3m*QZ|*ilzg7D3CiXZL&*2B&2Hj!@?Ffejkue90&|TcZX=({nA3^l$am3aJ9F)3yb1IPVcY30wa;O{=djIL_Bo0DPGa0c?DKZ^Z#(18W8Xs9e>2BY=G?}7+gOjmyQodc0A;<2L&>`;3sCkY(T}{EvhvC*63dX6RaQY+abh|00c<mvSd%<}xq1-?lUHD_%EVse6&bT8u`+o8ef*efFymFAPdT=&=~BCaU5Eq7d$V0vVgUJ<j9r#kfxI|lmvPBahB<pNUoX~U@KMUbl#L~ZlYgZwRM`mP81g2{8YpW_^dhgPtf8_x#QNl6Y%`wNlsuHVLWtwZ8#0#<F@(G^V>TuFkcZM|40DZVyoU6t&$dlnYHz}RH({Gm>~lE#9nQF4vCm`JzcGwkkA17p{+l_xm@|a=LRgQ%&#5(?pzJg;nf$P3{9kI-I}mXP`CMhIl|>Sx$iG$=q3j#tSn>q6*+ZN`9>-iU#69E@%oRqAA&+Ft8N@L1IQr~hu04zwL7%Z~JHw@R1J4l?$WOD~VPYKl0mlBC7(xCGV@J8<h+@td=8IuH25+Uty05a%L>qZ)W&M=3Aa*COuB@c8O2i`MC6rZBR)}aJ@5?rWh_%T3F;^erAo42ARh8I>yb@#9B332uN1yJ@HHh)5(8t2IwOnd9uobZ{d1tn3P3%YBg0V{wtB@CB>>@5XiZEv%=Ig_H3_eHMR%PE1x0BCTwnf?3L_7H!Wz&_dB1V$WP!^?ZGI1&SR<?;FZY1BrT(QJB@+juoK#V0{#h4q38_2iN$Ie`Fj2A_prEI&=rS>)K_ZqgD!#;0kzqd2)eD>MS{@EFK2K%;@{Wo(&GG{FF#j+lQZ&r3l*-qkN@*T=jm2D%YkndNvQdt6V8TmS8`;;vq?j=9OHb;rc<f+Vcgm{#EA9E!VkB}!YW->96Je58v%ypFU_R(iA+a|lzzMuWx&o-Oc=fmvxVaDCTKBusMDU7?0ecQ|an>m&-=Mm;R!g>t;PTf1+D*KE0hWsC8@0EQd{!5-uwaKr{omiCob7jSpl_r)Vf6F$16AO^PXRZ&#zsZfZMy|rd59IEQS%6rW{5^gCW&M9MUNQQVVq3%4tUVw5osadsW1ru!-)~soKkTy+`*YS)jD0Q5*hO7(6lG4Mo&v<b$sG!hYQ}%&2AE2IT$%CxW(M(F^52x*Q}#PCll-Bw2g)83ACVtrn`6Yg<mt?HhIowp0dw6ao+1C8G4B%Zlc&??Tjn~(cn|3Fh;8q>)NY`Ic$7Si?T!=E$uk)HA@KqEW5&*O$&tyNXPEB{>oK^S8ta^HnjG#Kn4LVEvd@&|Am%3jLRm9q-H6S}t;+nBwIlW?&&f8qh`!{XF;^a9E^>e7>Ossy-i<MRi9N_aqfc(;%Efs8^y$yGzAm*J=tj&*uCZM<;%DSJ7~4wpCvV5t&0TUdXU;s#mxuKjyppl5m6amqB`>Kgm$EX%{N&}8)l*iH*pR%ova-s&i5Bt#Y?G5%nmiYC<sjxHFUwpdh&jkBGG=LF335MQw`?BS|GWQm*MI&Q=kr>Y|B%=J+cN9V4qRJKSFt|*2*J-cr*YP-WmEq%Uj7alCr;Xb0mfea`v'

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
