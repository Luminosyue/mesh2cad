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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fd5b1428b91c47f1a74d98bb92c9fbe1/part_004.stl', 'relative_path': 'fd5b1428b91c47f1a74d98bb92c9fbe1/part_004.stl', 'source_sha256': '28e4efd88425d8c6514512f0cb745bf5996bd9a912709a07f510f4bb83f6f50f', 'input_faces': 1207, 'input_vertices': 718, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.48304039239883423, -0.47910985350608826, -0.23737913370132446], [0.4830818474292755, 0.497791588306427, 0.1861478090286255]]}
GEOMETRY_BASE85 = 'c$}r31=Lj4`|r=Zgn)oZmoSucBLXT6ozk5{mxOdPN{57iGz|5U(p~SNyIYXoD4>W~U?Tdv?C1H+`=8m|yVhOz;(FHiGha6Q>~m(HefHTg)~}r)VOmH3<Zv4N^v2GMl^w@Kawn}bsB^yo-8**fU!-^6p&lod_~uVoXVq=;e*G36XOJ^IZ>P@vJNC<4&YSn$E@ko-^5*T*r{92n?R&TD)2~x!<5z3{LI2J#{QlkA_wD@RbH2BWmnq~enZJ;Cr1$^vPqG(9@a24TH_nu0bGKNdzT>s_$3^<*8-8Blg}85T*keA2@`lt;oo2bD8+Ybpl>g4z&657zQ77c@%kNUZK+(0Li+Zh(^2e82XVN>v%gFIVAGT1x+WB=x18JO@QU1YyR!jQl*N2(U?z$&mYWcsEe4Q_R<10k^+snsF`YW~O81;u{h#x3f@v!`Tn_CCtB7A56Uq?*3K=6%S^7)(b>YvYhNdDc$)Tbl;K)zRwN%~((AD4W-3uyXki#HhcrrH~<5a~~hTPfwKziXAz(1IcAZ+#e){JQ?F*E8(bcuTIQGk3pSPv?1C@!c=)9M<#|H%I!;TiK-iPL+boB%eZwHT|A!N96CPBwHBiJM(%R*6W$4hf!~Z2Y1B3U*~htX;U^t`NNW|FrR~cwoAD}9af4TSYJl--`%Ehr0@K2@sNBU9rG-ee3q6L-?y%uq<2T|nH%Xl?^cxbp=GnBUIh0Q(fog_;fmfYA=f|N{~-TS$v@9Hx&EPbIW(W~&!zl<!soYFi1a6CS|;i56x$`o{bkv0DbJ2Kr96Qm$5%)C&Vo6ve1BQ9Y?JGhp^f@=I&GA4RLH(J%K!7|68ZeB*M7;T$>T5NJh!AeFULu|M9w4Z2g;tgVAA=1*}GlpPxEiYcTPK6o`J)+R*3X7&WMxp&mOZ!j??m<`t_ckmHhKnITIJ*yN!BWlz%_(m1E-fj??sA7HD}g1-C}|2X3F2d=KBAC*>TpS^ZK|<$T?$I}TKc^gESaB%hQ1s^wbHOV6w6PR)Ny327(7zEdip=AW(IBuO7vK+E~fS*g$Ns5`qNedl4?gOYyVX3@}@wBq~Ptdsnmq{#wt5q@AvrE^kma+Z<%%#GP{OZ))=O`qt!Pa=IM@r1LIfA*Z4<UZcFR(!YU6uFMRgiS@mejv8z1^s^8%k>N;iM<tB9|9ZZOMQv=GiIDG$4j$G>a{=fc+Ee_bU9z&s8RbOeP_l4sW-lE=_GyN{rq~|U@^U(E9<X_^2aSbBiH}yCOhQ3V<+5{{A*><_F-(=xJcg_TuF}S9d%Id`@s59>fd$G$@#?A-yG#<pLklz-(jPcbMrv;KfN#am+#Nep(y`k($D1jbbToK`;%V1A?b2gl>FV*hjv8zfi0s>N&Y9g>UFEuN&Vn(X>WZKzKrsno)e_r`)+<O?Odo;dGXyIhot_y!9IH;eW$>xlTw}=S@nGTWES5$xbjs=|KWOV*YTZw-fNOBGxx=S)Z&MZZ@nVvW;Hk)>HGSxko4Xnf6DzD8j@7=N&Szs|IW-sa@=^oQ<hnh|0|zqJ3a2{btzBN(NZ4YlbzBIgnic&yejFs^qpZo2iJctez55%Eq~YMv5~%0Ew`k1pFf)|$GzrPzf%`U?~ExX`GkFU?A9xi{;T)b$Z_s8QUCrusrT-}Oa~%;=UT55^8G#CBjpb!Os@X0@|ypnSBFLV?%|4>|1Wd5=y|`Q>C<eGcF>n$?V%`ta8T}l-$#?AUH4W<B))IU;mdOU6E>IYANHLew#xbXp0ztF=T&9yH978*zxDfCwL{wDupfAR+hr-=**bC@r*|FkeZ#Kmb3N0|xJcibp7pqtzu}is9%oJ>&Huu3&A;cF4UvAJZ(_+m(0IOFx6p%rdR-D#()63Y-WKV*XZ)9>Je8a2b295|;s?qOJtg1k>|<_}-+r-_Bb1<*_B-B4srlDBuKlHaEssR`KWCjHpEsA3e-|wDM9SeS^FXervwYF6NZ-wHL!KADrimpV@BG5zJ6TR2kbk#${NX77)ARaVd{_HH?t%j9Pphfl*X*YIB7Jv!3eA7;LcN|Dt4q4jZ&NQB^(QQRFw%Ga+fkku-Y>W6`DU!9>C?`Y_9poIWNqj0-R1*sNxD>DNx#U=;uGK7Igz%D8H=Bb^nI`YF6sSiGwSm;e_qY!k29M7?}0lbecy`5H?@8w86)MW{<D<(#e-AZzp=;HM*8lL9VNZ5)QyFr-M4A_bXxwvxyPTyMfmPp_io7birKzijx%MD`d4O1|Hesn=uo8Zq?)OpFPzouKdq0ZFWFAZ<F3yg7wM1aAo+(9RhI9~cc6#(zSytjehQo_EY~OA|LU@oKUiwA_U|^97T-H~`9=A@Uink+7yLl_?(#f!XP1`y#(OA@9=B6sEl;KV^P>Fg2d~Tb_28%7l8+}S`36>gs_lBA#cQMds=rHn>kKHS{S99s@qOQ=({_4FqpeZ?rne-0=(@K5p<kw6kb0AUnVheGaHgG+zLRv8v?qb@Pw4Yy$Xx9={JvEB7r}mO<$2*9F;kz%f6do^$0_ZP2R|MszWc*Q^)oh!6MypH==5d3mh0(T(nx&&Z$a_BTW?4^=3UxAeDCc4Xgk#Yo;=sWeqicKZC6t@k?-9XTUC#H&(-|DdwZ|wt~{Fl*dN-@+EG->@9fE?=k@bC@%`^?lKzalH@o<ulfUTsW~wdc<#*F*J_i#@Ki3`bxx6>|P9@UvpZZykJFC3jN9X>LdKCELk{-82YPpZx3x8?-%FsgZ!yd0|yN4fW*h-$)zTP9G{sh0eCBCyGo%YjT|5@Hc!@hgssb05qxwZYje?|ST59@K4w2<=+ese+d`F5}NA9pO5`^o$8oF4bV0nO*1QQ9y2;fVUTFK9os=>t9A-*#v|-|W}x(|?GZZ}9nQJ?`P>n*W;bq&$H{^YnZ-<k9jMOE1^Kmu$wl$nVShw7sNvl26t2mqVIQ!X)xN`d=Hb<p~|9|657k2faDEX!^US^?W}nD&M0oPg^bLzGQOTP=RyW|1Z!~(_gu(=QZi-7Ab$xI-36UPhUip^PSS-`)^&*?>Ea{Ij+CDSIe_4qvRjB<=6MG8rj4TUcagN#AFaZ*y_3V&sG)J`qMhM^sn4@ziNN#;(aa8<JaW<*WdY(_`%fA<T(~PaZ38dVc*TVM4q$$;hm(O1iF7Me(1cuCj~y=EXQ>}xTEhy>+|aS*}}_O&X0ELagRRJ<9?7t%HyB7PW|J*tADnpzK>5^qWLc`t@-rHsn=n~BF+Eg6TSYua*H3F^_lpA(?4o?4iwh$i7kHhT}Q8jZ;<A*t+nQ}KZ(|pogbdmdaC`M!2Ig!H)yWoDhFz*zu2ecN!@va)|=ew??|iP%jX|SK7s35^}6j!rN{Md*5m#sx%xAjY5t7cg#B=N0`-2=ahrdyYQJ!D2lY!%I}zyzHf7iHq`0c%6-kb0`a}Qf_36A<-v=`<)AVZ#=y4N#qxHGKI88sNuIArm(n`_l^~4WuPp|nO`D%rvYxs`%{>`_wU*oQk{zKSzkM@%Om9Oj_sVC09k<!l#aUBAwm(14u`iLJG(?`qG{U5D|mm8@+wVkFPReQda^FeX(eJ%Fu^?Z^*(?2XIzB{%T<*d6u%3uGc`U9rUm4E+Te)Y%oR6lPI>1PEV=MvxlQGY$|@xjs#xIbr6e|!&3zoLb-OWr4$wEsF{q?Z41D=Clj{1x>_4%c#~&9qz2|9PUQeB3<m$#cq={E_xMhm6tubCl3_JH<osed9jR_M}ye^xuQI4~p-M>8r=h)=zw=)N=7d11G9q`W+qLD7{4U2@Dk9|LXzGr}`-I10zO=AH4RP_-^Aa>JJ{L<#e-1d+zU0SC89oy5?WIirl~6PPMfBb*`wtpu~|#KhSTQUe7IWAByySGdJBa^&>DV*Cr`<w@RA-k_wv7{+s6_eYa+@FHQPj!u~prIIxiB-)pYszq+QrR}S}T`VuiZ?p5{Bu1Mc^H>Vue>6Z0F`TS9O^?NMl`)#1_!PEYg@6+9qMg1o&21<Em{i=TNIqJ7<ApKtdf`@wFPw1xpo#W#~V=rsH@I6vLOOp+ezOU$v+j1R>50i1r!0L;de{4}rU%C57lJ4p#&8O8K_5V(~DAM<hNGSREmz3Km`c)UbKf>qr{RTbmx2-jOqZ4|a$4t@lO_D>~-M|1%?_V$=()XPj@`YTtrXS1ro^NRu^*jBc<0#e6>T?d?UHYw*C%F52`MyHs4@i3x=(=3Lulwnx-yW>IL;Z4p$~cmfEv3HizQ01-v%Sf+9{yZ=R;2G1Ix6oGp|W{pJTTa0ptfi0@@x6G<@!kS>;B=1sPn3`u7mNty}D~Y!E)+<JiWj1-6gMS`cA9W-+FPC<QwbJawZz9{kPGjb=(r)7yGTgcRVOA?~mS}M#^(9kS(v&L-(B&`rh<!dwoted7|S|MGEPAdf3mBTJi~u+pPWP#0}N&uwJi2y|1M`52P)p?<c7$>NsoBu6qAuDI&fvMKv9-y_{0p-`rW%e>9G9+&{FwRt;%CbYW#Z-_rlgkn-2QuKgF<H)l+nsdAm`Tvb2VQ@{80&$dVUzR_*ueJ8M}nT`|JKP$d>Whu=k-EAEw2@KHVw%w}rp<J1z^6!s6lYW^$({z1*`Rjtbr-Xf9>PGVZ;vBoH?_aMDRlm&+&8N&6d0vD{6h9hyzE0Nadi{Nw#CK=cr+phI;}ya8J=z~!H&Nbe{4Eaei}VBA3(0#;u*5?hpJ?!xzE2F8qUSZGy1Z`&TYanJQe02>W)2zu4osh<?{h8pY5Hp^=E!yV<%Yh;w63D#H#N5CcrU)&_qx1yIKQ@#`@&5gtLM@5kmi#!B;!j?o?+T9p53qQ-oGRCbKBI~zn;-t%X8_1&W8+mr1w4Tfb(6hDN^ncU+DWv-&x{&Po|RbPj}pD@k8_z{I{pcJde9&nC7!Gq0Vpoa98S~|8jY4kB2r?KM&(8Ph-@te^!q>r`mY={QQZI)6dPS^E}fgOTG2h?5gt+zonIaMd0h9avhw$IdnX0a!38%(;t)f*3gjG^*Q$bCC&eIjgRHHrB>_nw);}O4mt12{p&BgRDAEW)|yX+Ix-Fryf;t!5ib3c;I7ott_I)zYoDa!Iqpr+QpT~}Y7fMBd-jy_`#x`|<*$EDd~b&hTAoX3Wc(_$Gn3}?UYwrqxB9#fmMb9r4yXBaokyzsug<@8`9j{qyd^K|^=!Z3NTlx$+H_a0%aE};PTcdd_<^zIHT@Xh`AFX_R`fqoj`v>G_IcDs@trLHYWizacSri}@obv^=1&^P=NZ#9eYpSAd$-P;t?i)4Ef~`CD)(6Dwea1{<K;OXs{i_Oxt_O@sb6!grmvh&+JSh#$FK6d_8&SW*Vz~PSIXrZHB^tAuZ*;xp%m-IcLuc9@?Yw%^Az~*e!uoN9#xg`aQC&<;s;vpjrtygdsb=sD|fX%oGL2UE#6OgLHi-ebsWrTTu}Y3kF=ec`@XcFVc(Z$xjvWAKa%H^yK#c_M|_EzNP2JGxK&Yp>~49^2DePtd9YVQ(jWA;-lg?+)_~2CzAxtuc@DY_lgs#t+oHbse%^n*L#u6%^xY{L^tst%i;nj$y17HnkN%!-|KD;w{Z|Hv?-qSq-=~`8-W}!VeXi~NoKo7)|F*vR^kcnaI?A|EpyV;>hX$G)(fk`f)cKBf1GRs8CaXRNw`JQG>HDr7(s8Op<>Y=3CaJVd$~pOvw$Dq_9f<UurHyo6;Pfg@f8<Ab&vrhXsrT=juWr-)2CGj$Hu$Wij>~m9q4T;G{PLdbJ#aws@%7&%exTlYJ+EWm>-DMM_x?en``6yp`~9kX-(lZ5KS}(+PyIJW`hhE>@9Ouy|45YopzU3)M>S4I<?~}b^{;0MM)}Xms-LponMgmFA)%IM@b;*D+>9|gpC3E%<4E6^=X<^H`gS-UmA=JPy^mUqm=<}y!B|K9(7g?ZBh&jgKGFI-yTYo-^iGocdSC1)vpLEy`-fgnPrYqX*R%3{Z6_Da9U67MJU2u0lWmVGPpjSP`};-t;r@X8>svdb(legp4tcmM(hrQ*`NQDlZ}vv|Zskha583zC{wUwMB=yAEa^*zSc{RVP<DdKDqI`E!ExBKu-<w4HH>XH{&pWQ+@u>2b+aUL;ujPfKQU3Wp(mwbr6*v;**J~>6j5oN+jq=Y{mUhp#zQDey<F-#E?U?u2q^RrTrd%YxZ(qKs@5|j^Oxk~M;`z&?^6z$9p9{{{F;Vp=Lu+}yI7gmuh^lXwZi^pm@U8R%+^HGPmN)*9F|0eNe?HQ8oZqDWIp6DhOW1e+?Jvg-CF!d5u+T<rSFHQgm;Jatm#q6baB!gfz1<E3NBp3^)o%FXs_5Ta?N8XZ+n+$j0a_pJ_6^@|-<-!s#JAf?@8U-Kyt3NW(3Jk_TkUhaZ?(_C#y51n+HU7lHIngo`*{)e?dL_{(AVPI&!ez!KaYG}$Lsu}^}LJst>>MSqJW&oOV3mMm!795SBY;w$Grt&H6QCa9`9Sv@!-+Vbw0%EKZO04`VaH|(ehaR5bvi+W!}K<&&2yye<skrz4&&2DeT+*C2!47bRCM-?+U)PMSZLP7WVD_n?Ls@J+9S14EuKfFqr+8&WG6jPkg)o=|0V;>vXJsY^YC0y$`H@uP^aUT_<7nlimN`)A>xRUmf`M56#Ewhlds{ly=(gw+Egqmia5YpYJ?gE57|+;9N_k^T5`7g!imheEYp4xU!qp-<z{!T-5)28aL9n-(P~wpXfM&^}Z9Tn^5QHt@k6hNO|?G_bDgE2=VRruh3VgbX}MAzUIAoTjwvW_dEZ^?=&CleK4^1bs2|v>HRS<T-UML@0;CL>$(r?{WS3Y4e{;w+^}!I=LWx@sOvTC_vKv=b)L|AzxHnYQ`;NseLS=#M(4e)_xiAJzt;yBWz=yCYka^ry_op+ctWttF!inR2fz23KDVuLjIeKyWBBh3)bR{!JjB^>PJDa(B(VCL`1UwV*tf@F{INGQy)~ZWEc;52YmNUnA7wcndA{NCBJbeB>RaPW!M<hnJ-`}|@^x&W<0aPkRj_4y^{sKRc;6Za^VJ@y^G?=yTF{d~pSRYyT-dkA<wAd@65k%*3!Lhv<15y9p!Zl`O>d1KI!6YGZ;v+y)-KoQxixMX_U&;?cj<QZ|2s_A7wjADM*1&}i!L~*zBP{Oy^%%dajo&#uy2pYdOPMk8FgNa_lEtK#(OKZRo@yncHiqFzCF$yC>qdpVAgnb*tf^4g9$EbIjwQ;faj{_V~wAO{g=kifB#l|dmP^V>8a*#kJ~@`M}2FY-}y3~tdq0n1%fxS>-srsej)7J^9$Zf1;w}LDV$>!#kc1>!oEG<5pZjYZ_l%YeS1E|A6HwCYt6s-4%E}*+VePDI%|4s-Y2wtwEEUOQQ*_XdR%K>$vb12`1U-M8#tiHwdSpY-M-WFvgW_SzCHitZT^a^kF@8}yv>q|Z_m5=>Sj{kny2&Cc_S*H@Vs8IMlSWOc|d>F{JJjFo;R#gP<?CuG2XZ4A01yw@$GrcK#@k`zclZey^s3VJgGPRXz}fN)zHRrvOd+GpAGx={H(jYzWDY$uW$TVO>fN$hXw`3e`y}M(_u|-%{%*BUe)y0JhivQbxm*0YX{y*uIrhs`SGxC&yTw$vTAy3p50d@xA-s3%V(;kzBP~UzTRAYYu-QbTI;CehSv%BQ}{K#wXPue<6QNvbqK!i7mIJNX9)W*t!KEuR@X^e>mr;lcd2i!qwt-&t@&8%F5IK{^tjeKjliMr#JAUbgnfIxhqM2w9@kno64>>(rnlCagjT+x>%y&dDWMhF#kbe71V4LQe0$wXa7t}`{#ol}yyKgQZ?CIyKWd}tt#vs5k)1WYwQk4lF+s~?t@8<Vo1*EhbwR$)GsU;p5rx{%)%4c7Bd7UVO>eDJ@;BI_<+Ro{xiybyd8~C%-pUu$x7JNLl`d&M);g<@?}{GRUYGUWElqE)@4~m&cX<o_rRQa>9}D~T`ms>{f7G|uq51P9l69r_y0u`|bmH6V+?@0|#JAVQh0^BI{S4MRx=@-tnvb>a&KFbleB}2PUZ>~&U0>I^TI>D7zP;Wr@K<9kzqM}A{brE(_Buo7KV$W{*1E*N%^A_@S;y$T_L-iSweHcWJ5}~S*y|_5zP*0Z`Kh3;_qEn%#{1U#Om|~Ye0%+8yl<`l4D?AO&kuWjX}oW(FZH!9Exx^eHSF8#R|B_t=<~^19~<vm>tp@z_SNHB>u=+IYyEAo%wYAc^}S)=Uf&zcuuXky{czZSY5nl;KWTbveR9~h*C&T=yeaLhz5Y4u+v}g5(-m|a(^_90_U-l6?(wSP+v~T(zP*0if4rKex7LS;eS3YlQ?r1+w_EGa!@j-#+^tqb(_8D?<9%y=yL0;&@$L2VVgIG|^Jh}({a~%<5Bv7I{dnJ6w;!L6wf^5XyPu}F_7{YGdw+qyaw55Z?EMR2-`>CA&ss-(dw)dOxA#Z*o_?nJTl+7<zP<k<&?=GKpZ5Nauy610aCW?+zO{cO-naITxLaRU-`bxN_U-*C-pNhWxAwn;eS7~)U`%`Ut^GA&-`-#2Yq3#$d;d<@xA*V(OFk9f-X9e9U2A`kH*Zp%*Rl2=#rxL&BVW$c+8$Z^o5KD}`<vd#EWW*eD(u_)r@YC^YkOqv&kFnY{w(ir9d(?@+W!^y?fqZwt}9wjYkyhTxA&L1Z3k-mW$j;!_pSYF-WH?PxAw=y`_}$AxA6q=?frLQ-`;=c{+&<TJ8OSmyl?IA^PU{9^BLCu!La|*{=uEG>RbC0<9%y?V(7+N&EMMp820V`kIt6O>RbCO!@j-0(ixUk#&PWZn_=JHzZvLNP<(rTXxO*+hX!l()_kn}r(yr4{inIM;79LojrXnntxncB_3iz$_<@7BqV~`FlHAku*8beE|I+^4#NTRqYyWS&Z|(o}CwQ#+So@2^zP-QLd#v^C$odf8zZ~yd`<MMomx*uhj}H4U?T>DeL&uw}{nzonwf{PFqlk_ZS^K-=eQSTW|NYWBe{Ag^5Bv81@ldLjnvcCd9pB!c?)%}s`quvUc;DLp?!B$^*7pATuy60L53X&e>8<_yVc*`r@9Y|)zV-V6@xJx@0D-vy^{w9@i1)4EAMnlA`8@mg4Z^<t`v&f`8R}cVpAh!#-%s#0f2zLq`wa2E_4^EN_Le$tXZ`*|yl?&fL-6rV^{wBRi1)4Emk3@9sc-#$MZ9nQeuekqBjzcie;*^>kNka%`cc0IQuUipeoR}|aZDt2(mGw*NBk6sG0mT_{_lSZq<g9VtDgcXUZU9B|9`&)lC1TMG7R>-xZaM2;iry<;dcqcg9yXZ3B$Jt!*yab4EK%EF#K7JhT+XI8ix1BXc#^aqhWYUjE3R4F&c(HjL|UsevF3UF9^dk2*X1N!|xG>e|0nrf8=NwZsTYee%sM7{Dz}p_;p9aa4JW`a8^gdaB0+BU&A?Hlr!&(_}!yn_%E~&Y{Kw!kA~rY(W0=?!mtU$|9CVE|BV)ejpl<*82%H@1Di1XheyNkZ)kSdXlB@i;in!A!%xuku+cQI3B$jjDPa?ae?pVNCJaA9lfWhne~UizD4Q_+C3*_}5<Z7+gwMeT(B<#}cpKUR-UhcJ3}-^~!<pdM&}{H)@P8fE1h5IiKciP1WfO+KL65=T!1vH2@IClHXdL_>_zt=kz60Mzcf&@v!MEWr2*Wqgjj+)*@J;vzVfY%l3cdzkMwi1zgYaeeB4PMEx&$`53_cHEA`D+eW8tgtb#y&^9lnL`fN#NHqKDuw;fLr6_#ylgdI2{282$<VjWGNi{TqG`$9Pl|dz4KWeicmx8_f*A3a2Ctr$ckWM)Shy;EaUfENDqM3+zR!!Cp8wS`W?*w?{j|Mn}Ny;nnCkcs0BMod<7#x1cNGE%0{2@Gf)>Y;-HU3qD8~K7{UvjUI;&!Kcwn@M-uW`W1W;zDXFqi~bijnm9)JF8lyZ0h=)VGnx@LVfa@xC!CY#iQ(ig_;uRWlyDj}9h?SEk7k0?!<kVpoEgrJ=7zJwdC&rI9ylLb9L@(9MBjo7!iCYd;lglHv@Bc{E`*kb3&DBOVsKtKCz>D531>vJ!5QHcXeu}boEUutP7Isx)~E+IVfZWbK6Sywed><U%kU-mIC=~|4(~_z!298?=w^5;yatVh*T5^$W$;RP9y$%42aiKPg2%xl(4p`MxFhO^jW&ck!u8Nva6Pyh`VL$TE{PU^OTu~4JaAq(7n&8$1!qRnz?tDx=qqq4I5GN+wm30t+GeBQ!GFV#(X;Sl_yT$yz5t&<55OnjL+B>>5WE9j3GaZ{ql@76a4b3(j)j+@v*Bg%67(~82^>V{!9jRAx)@##uR>SAtKc>0T6hh-5&azA2ya8T!`tB9=q`9SycgXM?}g(~7mkCEpoifj@G<lpd<?#VCh{m>flc4dXm&UOoDD4qXM^*jP2v1-3&QYnGzc$;H=>`z8{t#v3HTKJ40Y%$KZ8x*+32fq5;z%}98MndKmGC+lw&Djcs;riUJsu{Pr)bQm>AV(a17;o4K?L>jWC=VO$MiiGoUHq4DcIh8u$%32bvzv0l$f6hTnvXpxNOfa2YfYTn2s*%?G~+mq!c2<zXLM81}&x(V}ogxB^-Tt^k)q^TOreQfN-N6r2mq2<L*+qAB3Ca8fieoD@!gn&(^sJ{$hVqxu#64SWT?1Ydy<qsQUH@NRTJyc^zxZiP3&tI##@DtHCD5?%q%Lg&G=;E&O9@W=3QbObyc?u2%Pjn;!Z!S&H<aDBKYS`w}amqGKwW#D{hE;t|jCYl+36Mh3t1-}8OMH9nm;bf?Jo+ab6;lCW!$M9e9x9A1<Tlh430zM5NMGwJ8;XUXMcn`b|T@SB==cBRke0UbR44wr~LzlqQ;HhX3o(g}0E{8vXr=zRj>F^A64Lk#$gKmW9z)R6>@KSg+x*J{%Z$S6L8{o}o9K0Fci5`J>!u!x;@ILq;dIdfRpFz#@><pg`C-kUhgA>9z(EM-?xDeU`E(AA6m%<BQ#P=`a2f}d67}e%6$|ekdj0WJ3;Wg+=cny3Qb>YMCS@bk~7CwibfzQE5&_nPMcrCgLUJH*wKZ3`=t<V;5EBHr`>SK?x3Bya!Meq`M06GvJ02e`v!A0PZqx!X@Y{GDVbRgUxu8qDA*M{?;`Qbe9t7r=NRoH_jfIYB-#yJ1;$8a(<Ih+j6jpl=M!?n;la4onWIsonm-$lQI@4|&Wszp7@CJZ-0Tft4>#pptKA$4~#VfZ0oxM_^4smDzT!z0j-;Sun1bPc>5-iscF_rfR9v+zmy6nYLm1@A+T!2948=vsIMJQ5uPkA$0{t>9+xcOF$!kG~@fFF=>T3*i3f0JuL~0xbfUfFC%jrXD{a3=c;8!-L@lXl=LwToBCz7lhNGufl2IM5qT&1SdotI3b)GO$Mii3!u5-0&sn_7F-`5g!Y36!S~U-@O`+rN7dBh;)LNwXcM>*JRe;QFQ)F!Ck%g07;YS+YU*)g!tgM31Uw90f-Z-bz`N1C@NW1xdJ;YkpFmH+C*VEkK6nqj6kP!?g@>af;o)!-v>Dt4zUNUj_4poPcrLmCo(uOw`@{X<x6l&sTk!Xes;S4{6NZPPgW;iYBeVhB2rh~igp0!I&@^y5_!Tq}{0f{HO$aB3)1s;2v~Ur$09*uah}MT2!b8wO@DTVBdLMoSm-48ZdR&Sy+!$>HH-<k$=fm@<yPpw;|3esV7^7<HaYMrJ5Of$k1YUqHffvBr(cSQN_$YcDJ_;X0Pr%3E9q1l-2fPqn3NM6*qQl{#a3iz{+z1YNR82h&5r*fWbKyDghiE_eL-=j<E%<HtM@QAv;~xpb!_lGeaJUKD2yOzGM2o^D;Y?^cI1`){eFaVmCqWa#N#KlVS~w$I0xbfUfE%L?;l}VVbO<~Q{sDai{{WZvsG53QnlRi9Z45VqXQQ9NpHX*b6NYaShU><tntEK9FgySq0uO-ap$p)7@K$s?ycIr(9)%CWap*BP4&H|DfVaW((S`7Qcpy3y9thV%8^QJ9J04Y2kM9tMKSk%jpTd3758=LWIrMF~9Q?#lHTC!jVR$q;93Bm~K%2lV;J46{@LO;eG!vW!ehp0uzXqp7lfWtA%xFe9Gh7NS0hfZCqmAL_@F;W`JPQ5={Q>?3F6&V>^|&lyxFy;QZVAssXT!6pyE6&HR|&&4VpL5%u0a^?jShf&!!yu%@C<kZx)t64??ey6JK<eu9J~wu9Nh+g4$nmA!!zMN=s>s+TobJa*MzTmR82j;Mi~AC{S^KL?t}J)`@j{@a&QIsPe;|%<39<*<IvIYIJh0!0&WMthrR{B2j@Vuz&YRy=xcBWI6ayYP7iz0%&-@J7cB+93%5m^!)@WQ=qPwB{0I6A{0Cg#qiX7LdBSjOv?bgco{G+dXHs{k5{AzchO5P>ntEJ~Fx&&}4flYjqBG#Ba4fn3j)ga(JK>G+CUh6P30{qU4zGqkL1)6Bz&+7Ea8I~8S`)4gU+}1!dVGN}JO%v(o&xtq`@p^7if9G6BK)tTYU=U7gy9M3ICuiw5p4%|ge#)&!4=`WXbw0poE^;oXNR+)>EUefo2VCl6ZWC+!aleI+7|8rk4MMC<KchMKj430pGVcyV;^C-E!rAx3r|L;!c(cclL^CT2*XukR82juLKyCb_JF&=6Va*gM0gPz3onA#p&Q|K@OpF;ydGYRu7(%Glh9A#NpN?xC)^#bidKiK!e>3IrXHUq3{OI*z?0x!Xm7X|Tp6thSB5>PsmC5Z8=geno&ZmRJEI-p&Tv(<B3u<Nj^>4n!@1Dxa4t9}nhnkg7en8Ki@{Y;A6y0Qgm!>C!4uK(@I=@Qs*I-|hX)W1S3*rau0$Aahqi^=!4uKR@MP-lM8fb9!f>S+Ra1{E5r#XU-QW)JSac#h7XB1n1b+$#(RFYTUWTrRm%+2p#qcb696AXe2X{of!yVzuXjQl}eAJ_A>hV#+@C0-cJOTay?FD}TS4AtsRpF$l2Tlr4p?;fsJcTga6YUK5glnQz;hOL}XmR)*xG<UvE({k!bHat-a%eHQ99#pf0@r|hpq=0z@MLr%JQ+^nQ8o2A31PSjS_!TKcR<_09pLfkM0g@~cRXP@jxhXAjH;=}?+}LDq8;G2@E~+7JP4kKehN>6XQM%QHarJi2G4<~qqE@Y@L+TtJQ!|=c7)r(@1m9AcVX9~YU;5|7#@pGfXBi;(GTFBa1FF7Tmw#lCWTYLpE|0h9)C(0?t}J(`@qf6ns76?0{RYI0WOOchRecb&_Zw-xI9`8E)O?FYrsw6-e?cFH#`%a49|p<dsIz5PEHuEj#h!I!=2F%aA$Z7IvyTR-5o<1-b)zH5~FJBaTdaGYqTxg8vXzs1b+aJN2kH#;mPQ1crrW%odZvSC!o{e32-lTFx(4ngSLa)z**6E;jHjJkE*H1`v}7UbSxZzd!Rkx9&jDB23!YDji!K8!&@CyQ;)Y2hCf96z#qcx(PnUaxH?(^t`1j5%fgl6N@y9l5?l=}4_AZzXj9k^_eFcdec>(WOn3|Yx<}R2<JSqpwbANuZMX~C8SVm)M#sQosJo*H!#fDW31d`EJx)j%u7$RSYr&n+58zI4KXg3Y4<3b1hDX7p(JAm~xIa1p?hkiGd%<1d+GrcNHk=5}3MYbhdQ?q4-bol9g$CeJaCfu^+#Rlq)`9E78PL>l2KbbtYU=SR!tfaMLwF3_6>Sf9g<GN3;Z|@xv@%=|u8UTJ>%uM3YH&-q3+jivz#pT1;g8{y=oa`SoZh2q>T!C)@cU?O_<gu5+6C?kk3>hqqp7<i3Bzj%!`D$$kFWFDa0%*mEw}_+AMFI!hy7?j*bjF`N5P%pF6d~u3)~*<54VRKpk3hxa7nZ_ToS(FQB4G!FuV>m^>`g&co;eg9tL+qyTje!254Ql0h|-f0Oy2%cT`P1{+%$q5FG<Agh!%X;gN7Jv=!V7?vB=jyTjekx^Or61GFXl0Xzcj0*`<fpdZ8aYkOkSCip-7@74e3k7)~>sQ=lz{V$`pVn+VUlrK8$@f$Pi*G^>Sf1H>X|Ct-TjkzMu{{jY<X|4'

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
