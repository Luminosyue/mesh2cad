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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_000.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_000.stl', 'source_sha256': 'eca3f4602689767ded41f5f427941c45d9f2cba720a1a0126f3d447f47be5a45', 'input_faces': 850, 'input_vertices': 633, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13137221336364746, -0.16164946556091309, -0.4202198386192322], [0.1672361195087433, -0.03111511468887329, 0.24359220266342163]]}
GEOMETRY_BASE85 = 'c$}r33)D?j*T=U@A(AMOa71)L<QmE@mq;XCQ9Kf&NR(8n{dQ5hsYv%a$}K8N5h<HQN+nV$aVlMiUKJ9hZ_mAcYj@T>yD`4;eT^~4|M&dYdgfVs&9&Eg&aw9UcJET6<YAuqua>v>j|caC-rDmd%6W%*qXvw)W^n%jBO4AIetj{oLhQ?bRwr~jziaoN#k^78jrA@YFtY!MdaW|`+6-)2uYRW9z^g`FGos(HzE_R7Y=HP3`&~J5K;)0Syx;Hv(a*;=Z_=cGrpa;jGdE@akN+JcWB71&*jDu3-LEc=#IF>*+cw|7ds*yz)xKSk<_Be~ugv!|6`LA=$oX!6d~eZAw||*)=f?i`o0mKN@dLlwdrtouEnX2nGxJHeKYm!{Qm21*{$F$A{LkOEJk8hF8{mgkZ*=km_un}??R9;8{kp-b?k}cYmyfTnD_n5@th9Lx@b$a}?+u-qRu}8*x&+J1%yh1I){fZE?RqP&OYVj{K3|;Y`(KTZ{p=a5Q~jd8tsOsCy|l@5ZKd_8exp5~<@>>^lT6*Kc5?a`;b%82b^7Nj)-`osIK=56;^($yo&MfbQ^%rUlsld&#?RJ$*d5QXnX}XK`}hU<_dW1p+W5o0#@FNbF8Y2}+WaKGnje4tr!!OMA79VEH)Hfnr;baQ&;6#p**&fwyiI*OuTJ&->8)LVa;ezQ{9bW=s^5w6TYpT`xQ>|-ot*wf__<X}o&MRsO&zm03~}>Ye_7V;ztGe%=se2pk6&=T_~EXJP9E>48MD(~H{6P^Uf2KSz8BN3%fr{#6;AtMR@%HJzM40$|7SDP>SBFe7k|5{dvd)m7GIKjU*i|t*UC@UmCd8?Ywg>0i(hbG;}_i5Hjloq@eA&2{DS-1=F#`H9gn`R?e*&W+UD2ywH=SXuWf&QUu$2@Pr-eyd_DgK_w@_SO#fNDf7Lqg!?yYUnB8Wb|J=j%cdRq-7gftTzW2}y#}76(H~lMkFUS7a3mo6u|E76==~B-4BmC6yB)%F?;;ZpkUymo8a$4$mtY0vm)!j`0&3nu`x$5n8i}U>8&1U9(_Wti;-``;ToPXoO{CQ6NOiAOPaN7EOKg17KuKX<D&(xbRFCJ&htG{sa)HQxM?D0>XJb!%iYU=B%`!~t|_1xGG%dJiI{l{B6zP{hJZ`Ygky*0JXetve9^=W?Y!rz?h)%!z%&-zdD4B2M(fvPK<`N<A8e)wfOXMX(Monqggf3}l9gCG3&4JW_ef2^<fpJe{)H8y`YmKo{v&*JBveAK;OwO=K9)P9wWll?0Edb4xAb|3Rr-@HD}xBFZ2x@vz*Uf24^+?(p>D%Ex7Q}2h#JgfaM8Bd3av(x4$Y;Sx$KYIU6`m6mj@uy$*Vp@Fzd|h9?-xm0Kz3q5uR_c1j*XvpD&)P4zUoM_FGwpt~zP=yzex6)!wo$sjdfl{mKGlBW;p_dx+xqOY@y}mwb?0-7@q_m>?)*&M@J#%=YJc;l7~k%1UWx8zJy$aOaQ3++>m2_jv)(eFE_M9ixcbh1oA?hO9sB;S&9NU&>Y19y`g%XNzTVFhU%jrsvRCT(t*^)9ce=~$11r|V{ex#u_$XelH;glW{dLAK)zJ0-rN2L^)QmXqyjMPS{Nnqk$Mdpfu6bYH@L+2G#8>&Puk$Cq%I~jx%H;WYxp_aWc!{}Q<!47<?D)al`{Mk;j)%=WmwLwZf8zbPf6=Dijvv;%-Hhi#`Zu4Jn&0|5zdv|-YJThM{9fH9X5IcgXIbn|tnqr=JU=(KXY6|qY@D0#hxp;6eHP{W*}i?>j{BD`JtyA}@cjpl44pg^zgQBl+pl&%@ASv_dYgGk@=xBlIKHm7<)`KQp7n2iY-zslKlSt*@qPOIyeZD>K56`-Ejyh4-eY~{$Kz4?gGY_;tNh-fcg63IMH}4lXDb*#*UKG$aNUjO^H(W%elqx;o}Y8doBe#eJO2T`ujb!hG%vm%!wJ-}<A(J5;uq8xzo5SO1@*-*sISeV>udY#`r7=uzIOb&zW4?8wXdt|YxC&(+VSZ6+Wxw}cAUDtHjl0^enEZhICXt(9$jC1y{f*!L*tgF)z|vEzSh_EwZ5*e^>uxdJgUA)e^uWkzp8ICepO%V>-r|ItLmHNQT0v6qw1UVSM^QCsp^~LQT4UHu5U6<Ro^6!s&8_=s=og0$*J|VzOJwJb$t{6(?;oe-mI4D2YYg+?%V3Wn&x|LDmeMGo8FK8aBs_3(|rH<Vs3x6-je)ky(Q!Se$Ud_pZA2@A3q%S^x}NK=;QBWKlpT>)8EJUdW?1Y>-C)ESL-?H-+FxPXID&`<@CqTeACkDA2hhl_?6c?{fqF!Rdt>I`hH2)gSuZ5zrzEup9ywPck;By-<fgx`%V56``HccXE@h&lJPTNmUa89`%(MZzvoO#^D{%rI^#+1-vzywruqJw;i<m8-xI&Yg8AnDb;s}Hdusf_t`}lIcZ)ke9=@mMNAD*|9<`q&ue+(a`F`MVx4yZJ#?PwydT-Y-pZAx$>nFR^_?}undcR8gtNqIQnTc1LzgN}z&rL9XaE`nFGef(?e)yVuf90+;zOU{ty&ood)P9)s|G9nq`PWzbgO48`=k5>QL%Uy!{h!?ZCw$QOL2Gya3C5H){nh>%R+;}|s;~CvB#+vklX2?z-}9E3`L9{regDPxI=mL|V?nu2ujc!?_QnsZ{Q5?|@3&fO_NBd_%yIJI`wcH&obQL#t}*+`4Gmt%_XGTFvr0=Gzt)KOzRq=>I>X72U*zv{`X~4AhAXB!ugm?IsdoBOC;#E^#`i^5=g0R|ey_y&=6<=}9e=jC@dGt}Z}}v%ZvSxSCw#~FVFP!5f}*MMy7JWg`}n?^|6teE&ie6o9`$xS9{st}`ucOF_0{LE#8;o=tY7f`0KWeIHtDawH?aNn_uJN2-vcDR{@xp3e?O4;`g;lMtM37l{QCQIeEofO;;Zkall<y)uJsE(&)V13pX;r!zc(0}Sr+FXF*=NW`}qjJsLO@Me|Ge|RDbNU1^K=|cYAyvg<t>qYQFE`2Oa%4oY%c;W$b(V4|~n=&ko;;^W5~&Tqi%iH*@GBr~ipljX!mV)4%9~?Qh0;9v|V1-=B15><3?b<h*WXe0$?hD(mF&@WcBWzUkz@safp%?>2M#=cWgX;{N>xyZPBq{7x%hN%O;-c00a@@3rXQ<jJxBcpHX0;|Uj)T9`H-Z`Pg#Y1b9bG`_yBOsR)okNqj`e1==c#D1XalEn|7ck7aQX?VQvg@3vA&5b=f_5-y}LVRDZlaF6B{|++ycDIht-EaKK?)uDF{|<M37M;`C`0Q`tQNGDDd2_sevO9XOS)AtwS>uPVbX%P7htJ?&-tm$AJl?K_v0v2cDJM^Er}4dARUO~6{`TX-G~Zv=@vVHn=r`kss~S&m#*gpU9{7Yap83AHu3ewIuZv&w)5eeUeSe<ubNwf~<G~M}?)9cKKd<38*mi&Z>lWdM3oAe4jAz1F^ZPfKTI<ZuL&nd}neB`xWBqIQyW_#n%zbK+Gd~X+KPXpioHIZ8xh4lp&i8|<kHo*9DPPwakM(nF9(2YNPQjnpdP%;Y#m}~>>x{?452|&(BmZ@C&(XiuPIo*vKV<&SzrK+(o+5m`KCPb{bf+`U>`nMXx-Uuf)p`!BKmN}*oVtuLez0KQZEaJ0U#<TTKXbzw&*uA?2ku^&HqRcuo@akNzMAI@zMkjce&Yv6y7OFwU!>+aH~8rVY3ne=*Xz);{na|mU2c3|twSF_DC@4n41QLv!|>*>&HkzG(=2|V?$g{&#@F|0h##u^G=m@1ckfdV-&gl(uGA3IU+-i1dLPT+XY@XXU!?c31C8(NeGET5+TF*3-u~-p>p$#ed~dG1o<00zeQpj+o<Fvk_f7uJv3_pX7PHQ;J22Jv=QMZx@Q1HVp58ytPxFJ7U7Y?!Yu-10=S}m|{BYwXPXA!RJd?lm+WBdIxNWf0-~OEtv{*eq&G&a)>E;i{rsv1k`LlzrP94AX_4tc=^i7=~>+AW+v_Cg>{;jX)Kk&P|bsTuB`}dOlJNA}`%sBPu5q$mkbMW#6(_ei~vA+I0Jjgwsnm_S%9{hjHQ}FkEr6-*{_TSxt_0x>6K9^Zv|D7L}oniXxe`mzkpBMb0b5ipszRF|$f6G%ao*J7>ebwha>lggH>Nz?7o^(I=Szmv?vwp$39qX&lap5aJrjEz^ZcFOxTEF0PC4Rx@N9*g)kJi_pA6INO`;R(bl=$j=k@fZYBJ1n(MM)lYz9`9~&KD*9_4z=XU!5<~zCF)i{ets^%1_R-;p_87+PCL1l5y(uhuXL2>uer%zR3Fed{Ht^b-pOMUUk06`UU43@e9s3+WA-Ki<0rE^F_&Z>GO~_k3J7+$EnU2CG()p7im8^KWSfApP#g^tIii`-<~f@=0~5mwDYXbTiWrc^F>L1b-pO+ug_=N{`!2T_0{>JWSr`JQIcPu=hVJlZ|Z!J_Vs!$IRB~qg8N0CFVeog9}CWl+Ur&4ixOX*FG}*L^F@iT&KD(l)cK-+)|-32DDl<#BEQ`pGY{%}LhBct^St&C(_f!EwZ1-gYJGj~6u;mcY?%`8q>ab=1>f(rDfv#?coJWKKWTmay&`_Wcy>3BeZ6m6U+=@(x9cj&qxRJTpLK41z3*9H?|VrewU1d}?_<{2`%;oe?Mumc)IO73ui9sl{A%Aw#-sL)q`%q+3Vby``o7k_p8taTbWf+$`dYu>eOCF&zG3s|_f75FeGI?geGR|hea+_4?^E~%?^E~%?>jb+e&4a<(eESndiDE=&9C1V?0EG1g6*&OdF`wDDcHA_ujgOaHyGC0%%^%D$NKtt9PQiZJ`!I&k5l0DTuI`q=W&wpsONF4ub;<B@~G!=lK$#>oTR^c9!LB3c^vEO=W(pBpU1JjejX>uqn^h}@~G!=3Vbzh`gt7f>$>RYas2&*On>!!W#X&nE46Q*<FmegzB1{rp07;$tLH0|{_6S4q`!K;GU>0Lue82?zEb=8diC>_iLaiow7!16GU>0LuT1)@=PRwRpRY{vsOKvaUp-%`eO(vl`O5CjQ^7^IcIkZ4vC+;FMH%lfZ(zT?M}oza|E#7z5<Ix+|LT$8mdzUde;*0HxL7onC@vv{d!rY?qCMf>a1q)E?uTAR2=_<(z@nGJ{o#S=Ab21=7##u+hOb12!dJpqp~K-eQH<bc;Zylp^y)l5g`cm6hoP<EVel2`$?z5M<!B4|a(DpR3?2aYMVr8V;a+HCxEFjOdLn!wd_LL$J|8|8Jpn!!J`b%Ap9f!nHiR#Ld!mito^T)ZB)AWJDcTgi6dr^&hX=t!(3bEJcqrNm9tsaf+vL^sXlf{07p_bFEZ64eQ{dKUb+|QrGI|7jGTZ_^6m9`GLl1_V!A;OIa1*#OS^{nipNRhD89otifc_3k2%mud21^LnM|Z;#!VS?sVF}?zXmRQ(QJflzmWEG)o1*35rf_q#0^A&KiB^VN!mZGw;8t)O^k{f_G`26IScZNMza7PAQM`k$hnGaLj`nr53CkY6miD!@3BMV|$FzS;oA4V^d_?<4v<WYW;se@0piOvw6z|jiK5fFUMX{3hm9z=J8pXR&%tcqg^P+f<_V;KLem#m+w6CH~cu^FqqgaT32)`A@8rs*;CcHF?PooIYPvB+D?NanpSmyj^Jkf3NJIwiVVm*CDx5L}{oiC`vPqhC;+j{D-h4wA9eMTLAp#2Bh)=`J=X#bA3wbbET+P|gkW9slV?O)UO5p~!^`zG2xphjQO{uOQSQ=1jk^EG%S`X&4&zq69MZJ>PvZ7ZnTM%p*h_AWKe(VnC2J!&a6eVzD_zM|j2-|#!DsPkspH`698Yv6m@zo$(&^voJ~i}-}TqCdhv@;kz^F1FIXl{R5n6WeItMw_tQ$933)MeD(J;o9giaBa9cS`)4gAAwedkAM$FE5V1t2czZTgW)o0DYy(=0xg!eAMf+bUMso_mc4YRXZB9fz3`u~?46<>`>2G+-YI$@TpBKimW9i~70`-s1-LR=1+EMqh1P(Nf{#Y)z%u8@GsmLG!N<Tg(OPg#xGGu=t_oK|4~Hwk<<Udn@^C5i0Js!f4E@{trv}BS!(Vv&(7&mP=pXPtco+H$ybJyn{V)7GZNH(v!oR`0iC?Mnul(*#bO*c>-iz*m_rg+h(fzQ5@PTMa>Mv1}nu{I;mxU{$hrt!$D(I1L6}SePfos5ZsJpC#W6?Tr9r_5r9mP9QEJv5YqDx`X5Egw47F`63E`&v2hehYXqOZcDufU>nVbRxM(fP3G0$B77SoBR;bTKTt1YW{*3QvvVp(vgqgdZb>A0&kDCWLP%gl{H<M-#%=5W?3J!nY8@cM!t&5W*7(;l~N#EFnCN5PpFWo<j)FLZ`yhqj)%q$%OC|gz!W{_+CPIEFl~a!Z#4Y*Al`v62ku>gzqGT?<0gK5yDRr!p{=IGYH|A2;r9r;TO^A@N-d&kK!pp_z^<*enR*zLikofcnl#tiVz-22wz7C-$V%CMhK51gdZS;A0>pJCWNOD!ZQis*@W=(=yPzzXm64Ky|2Rv;Yx(?p@i@ugz&+Ha9KjQG$DK-AzYFWE>6V%J7fHJ&_CN=%q0ln0|?<#gm4)`xEvu|o)E4;2+Othi(a^Y6g|;PVbLO3v=1zLF)Z2(7QGM_Js%c57ZyDS7Cjpl?GB6ffJM)PMK6FwFM>sT!=jhKqJ3e}e(=fBH8+W(H6eToA>4)#Zbb;UB!rt2!c7U`#)R;Rgm42w_yj`uI70Y%LbyI5+>j7%L<pZm2sa~yTc9VyqoQjb9mO#8I#~2tSac*TdNnM16)busEII@hy&M)D2#a0@iw=NA2f?C)VbLpK(V?*Da9DH%EP4$rIto4~y5_T^I2Nr7clS(NJ@i<(8*Rs+_29E;tBoE5pGjLSv^Fe$%_us-weo(h9z{pECO@~wtA<vGPp7RaS`GGTI|8i=pGw=|=n-&R+A5=m!>7?!1+5IXqwPqv3fzIVqtGMaGia-U9tC%%ErZs8yU=ztnt`Q8U8$339e8{c_fV^Q=qG$HZQapx;Jaw+hIWT<r|m4X8ywJfCVCb;hPF=Vneb@ZI-;H6YiMhac7%t~b~@S~9zvUso(>PB?Nro<2h-LTJry2G+i7T9cqDD@(9_`SXzPHsgKwnm473A$3vHdzGvM23>w<QM@1(6Ob*+P62d@iy8+;GHb2i!)ejtkbsO^396TY9ed(rXm-L&0>-V2YV?RNAo_*U8i^mh0r+Qy&(Jc_o_=ookeZP%cq;VWqyhF$|-PTLT47(9Tsf#?u;5N(6ef$$Zy4MhjTSJO5U9SUDd+jZzj_y*c;M6ZMYL)$Irjqn|`-G<%*OO3`+r*YI$cw!WjnEOf8M))Dx#-ew_!=t#FxxAUV7QT$O5$GtmD2hv&n@gEH;eNCYLI=QCMbV#Y?ay2YUr*Z&=(X^KC?4dRZsWS{K*z!3=p+0vzjGft4n8Y-Pih%OH?$Sp4epAb40naQpe^7oaA&j`+!;OtZ32sS$m7QREZQ!QPvqxz@M&lR_%ygJdIH=QJ_S7vJ_T-#)`MHaZO~)kHt?zF@$jjzkJg8M_;j=(+$f5UQM89o;^&TVC$uSiW)#hfoBA}THnvuWP!rKga4Yy^v;urG+yX5Jw}6|WrQv396SO4U1a6FaaAWvH^v`03PlOwwdteFS6VP8_3E|_=pJ55%dgxYILikv8J1il5Jo*bPAzUB*9hMMoi0&))Pt6)qul8^wRQfbR|Ar-mPeMyjPl*!LRkT!Ijhj;EGvVfFDOj{D+#GI+9+I~f4yERzhryNL3TQ>R0$dI)50`^WqX)sI;gaZqa7oxhi@_c&H5c7m%&^2>)`945cn|z5x&!_d{u$i{{|s+Mx4>KB?dVVNcK8?czwj^c@8~Z0cX%KA2fPpd8{H584NGlB51`Hx2T()NGH@xlEP60p7Cr<$6qXttNliqnz~$kC(8{pPd2!}lbSLvIv6DF#{SlTq{GK@z-3)Jme?q^5Wlnxz4n%*0|A6<Sf5CE%hjUG$N5BWehoV*C)1%*M7sYJPgzz(H2UtS*3G@tDLikCvGb|ze6nZ8sA^bGj1(p!bMmoncdNx0cFZ>?59_<3JhrdG4guj9}pq=3j@R#Tr@R#rxXb1QU_;a)!{5iZ5Jso}@U4fnsuYgY@gkScI%Dlf!2){@O&mx3pqR+rH;YZLX;78y`(I??Y;Xde7a38oY`ZU}ZehkgRkHL?7|J3YpLimL!ULsyWUw~hr&ntv*_hLq+uHEzM-JKAAH;NCHz6XB@e?SO-i>`;ig}*_+g1>>kMmNA;!#VUzI0tV+zkoNv8`00<jqpc=@G5jAY}bvjA4U5prh6uYFGf4U62cduonQ&!p6FSygm5pkD=Z=08|?;52wxKE4A1B}{4BokTJ)&mM!Ufh!WpzHEFoMIJqwl)u7P%fC4{S^9bpOKYG`{{LU;|H4}XHLMtyiS+?EiY<{6cFpGF8jO9($l2v0^Yh9|=ppclaxz&+5Oa1Z!gv=@9Xd>+~xJ`X-0y#ziVzR>%pW)~8|Q=*tkJdaL+r_kqlLbyjUqf*x%dG+o=2!9;KXG+(?pTVCJ!bcZ3D(mBDLbxuPf$PG@pf%xR;5ujxxDH$!tq#|QYoXQPTJXAJCM=7t!L#c|xO<mk#Sbg-Z~s>%|NJNae&ad+$0hnV-Q$e;zgfAB_s`+R?p+R$e-nuQt}7mYD1BZ&@p}IQG4H|{'

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
