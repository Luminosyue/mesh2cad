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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_000.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_000.stl', 'source_sha256': 'cc013efa13726f841ebc364b7c9cec6eb2bffde39331341e842c930896169496', 'input_faces': 1128, 'input_vertices': 595, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15127965807914734, -0.22168731689453125, -0.04609590023756027], [0.11642051488161087, 0.18538355827331543, 0.07233932614326477]]}
GEOMETRY_BASE85 = 'c$}r32Xu^C-2b16POylUD5IAk(ObyqL`g&^m<VDm5uz?(^cJE<XNWF(@1wUUtFyw0-bGt&?VI2Ieuq5af6o8B@1Aqd=aaAN&QpH(J|*L<U*i-hT{QexKx+_e9NMsorb%<wT(p7R`t|=ks9RW>kkBCp?KhRne-6%U)~cyrJA*b*8(OSux3Hjo#i|*Ld3CQ+tdy}>_dfml_X`Z^+^1jHZj#pz>=o86F%Rnz7}_oI=i(KsRxD*KU!s&T-1xuzFMZ-B*a~z!a!{CM_8Fn2<)2Hu<>$Gzb-DHT=JO;sT`aE4?NiIlRC%LJy4=(==Oi`GXv<-hdz)ib|E>*|O0MniepuIE>$gyi^P!2ZzqN>Ol;oD)<#f3zpxiW-ugs;(ZAIM2sL##&?NHM3wZ_N$sLyS4U!QBnK=t#}eTR~cW69LqqW*mKa$Rm)^4Bu;xuz)HIF>x^Bh+@?ouun;9T%aFr^U6euD|*0036S#KKjp{Rd$x*^wzrmCYR1Q&d(dFT+7Pb*>k??ciKz8Jv*kU<FC~&sNdg-$A_uoGok>-G4Xgda<wWBO{?#}Y(sO^|H@}u($BR-<cU`O?mn{V`tLpvrvBXhvQ0Psg?uX&V^8Y(n{IYkuC}w`37hUXOnx_3{dua5y8iaDEmZwjLRaa>iAy<M{k@vAb-B6!LRDAVwQ;)bw}oY%qqzM~U4LurWYk-Y?)vR_c3q@?er4A6w-p+y>QF1*K)?MTFRMD#me<pLuE~GKQpF{ubp5qv!F|=|#um|k?(A91)p*yl>igI4-9fQ@D*b-lowrKuccC{2b>}4^?+BsM>ES`$cBZtikk7TwKA`X4aMNTp&e&bL{>Dw$RQ;RNPS%gJYq6?x`{;?facr@VXR5z9xubsk0<%>8n?JNVm~?+F13t}DpPR{3H@<1`XjT8V9t963-CtwoRH|;R)17qvwWSYG|7~6z&>f#H8CBg{T&^6@ZU2%9;c9zM?bh|zc4k*~Ynij^fNuN0<!q&no9mzYJo;-tRi}%Z9MEsi5>?OI>*~7PRHo}HwO_{k`h19en)=+)F1p;z`C^Ms*st5pf(cQof6f>Cb)P#9^Tp_KLYG@OFYHB+>c=@{P<3uRvSk0S=7n)>)c&OB%U)%os%LBK!TQfFjCo-!{kv{_)0F9|o~=*)bmN;iUyM%f`f)ffj8Q3c{k4Xue`|?b`+imDwpu&%IqTWdZkjGPw|%@?o%btKb@}(Y9TmFoSM$aAd+@%b`{k%xOHp54f5&{WfA!v%^td_dR`d1HkI#8zb8*#;|GjSCX4Lg}%p)z&%e}he$@yZo#p-gK74yRWIA-s!>fe%OiZ0i*T&m9P+yBsw<EV4X?Z*0?b#5C~QolW{XVbd$dw*58Hs2?Ek{%yN9h#2Z-;;EEtfP9ZRr~ezv@UndBh%nhdy<a-y*?{$*7g5Bk3#0?a>snpR)_0y$9yr}4chaod0~obsLLJK1<Uy|y4+Fc*0kC6pUXP8*ZQ*iS9NY2dRL#b&du9SB<qhlx4u}vJL&k2dbTc`vHMqbYx{ff?qAiXadS1@__mnW>(uf2QdE~a=8>&#HeLSx`ZD#uT}gAtys%t<rpwK&e{;d>y4+Fcrd~&Nxueca)wbwzN1YqTEY^?1I@iuk(&t>yZ8-<+(w!I9xiv6I-=B4ES?8<k@2GS0`|7)XRp*u?CG<J#-0B*+Q&(?S`>$8~HDIJJchtYua==dAabW$MHw5c**12&?2VL&CkFq{$s{dTpxv{oM*WXd+c4Gxy?x=I~(4zWr9P4>|S6zQgQ{LxnbJq2D+|QV1YWm!<p1*jr<5zWVYWP5xJL+63c4Nn{>fAi$-ge!7X`eQz^BxwrT{mA?=f<FGy8ezjH=R4L%N=!Y*?&rxJL+6pe?&LFW1TlG+^@^O-xsCXq01e0ZvU`RH~#lJf4D}MJL=rje3?FX)VXP)K4+b4o>BVkVVxTnOx5-Oet$A)!uDU)xv^i>ZNEB?Kjl2{$@A~^lf1v<z9Ly}bKIXKA7^&WO}ae!^*vecsH^0;qi&Puj^~Tyxnq7M&%e*d<T>Z>PoK;A{!`BN!FJ{G7Tx~xy#JIt?kkezj{5wmKkGSp{(ZhU@?`apJpX<_kUVF-{ggZEGg<Da^PfJ~@m!F69L}TU`S<Ho^6@#}ljoMT+GaJ6s?Oc4t3${7lRW2j{HL6Cn>_!1Uy&?#+@B=R9qa#3{SO}2Z)dXmgr9QWS0v9J_b18o@Ao;$az~y2G>+qbELr~jx|TfWJhd)tut|5^c>kF^chvb${rTMYQ_gxwo;&J4dG4r(?|HI%{wa6dCnU=q^_e_(+~*|Ezuzw<@6WnTo;&8_Pvfv|f66b9*`o4h?rVgWqHPZg?d7Xk6$>^;UUA|fH6JR@RJk=eT;*Cw$s_9L*Zc9jzuJyGZE-b@mT{h{6LZW{jI;ZQP5pfI5ytoajJ$s@)!%l)6YEUC7v$Rl@VObE%u(a*$*StzvVNh;Ez_&0{`M(Va37T8BgR>8nT<cMjs6urV>`W5VLNNJK%T-|<>sJN_+0<77$;_d+D@BOPuyqDT!8*(uc+MeIiKpU&3=de+nka2Dv$c#{vY}eKCZ^MUs*j%ajcuFBg?2vM^(S;d$9iB9)$bofI}+Ryjm<){hAL$e&^CbwVkQ5El_#&NaR=ZsLwS$j924Wc4{$-i`~@m(K^+ORO63Ki`@0D%8ipIOjdv1&jWeC**Ko}L)CG&t}Cl@?a>r$Px)MG`%MF?qJRA$b(~GTHmm;T&P|YCzKs4wo8x&Zb4QFbDG=LP{lRqAZ(k7dxQho=ztRJ7-2B3jZ;wI!Y}hbCvCVjlU*m!r$Lju8)xR-t1^VABkMnzY8|tRY739<AsqyV2FXOr#dmnlJmnzq$j#Jxd9hXh5Ll);hkE!j+w|0?Yj@&BO8i%UmZ;2d^<FMHac|tC=J=)yrn2%{p7$<75+8$e>W8*M?!q7j|fb+g#Fpk@#W9a{-f%;tS+XXzQ7r2AGM}*2vw%BO3A5Nv!{MJr2P}^_49iZlg)yo69^WOcc-?I%ko*5e>k9>^dys+6S)NioLEgs%#du%)7#;S1&j7R_6k!l?4nN_L|t(|5f_qd>Pi@UQrZsy_(kas$c^S;c0`Cm5eM#YHy$1zWSQ^(U<(^KV^wy~%OXVWN^7q5f<{oHUot9%@<{=Cv3$TLhreKzwSs`{_#gFI`0)Oq+tbzaRW!ZH5st!f<m<P<75rJs)eXZ+Om+d72ISN*OnL%!*wIzGnYE2gUPgI6QJ9;^Cmr^~KXfA635$iKcqovgj4&X>hyBR<!?2Ij@rrnn#LdmOo!r#cSyJ09vhnjc?AKGT5xeft>qb;Ir>fAtyXrMUt1Q|dkP?0%RRYbNzq{dc8T*GVl;xY{1$Ucc2i4|$Q_OQ-5kdx7h$=35xK%k_O~dwg%={dpYoyAN=Df-|fA(hSv*H#(w@kEzIbb$;!qYaySzM~!1T>aEsuQ_cFwb3anK<>LUgzqYGgRc>jQ3)^E34OQ$r0sU8BR=LTy0gl_odB{zv)%KY3x~e+24_b))_B1uV^}ofcu1s5_k>7|>$Jv~9GT!rFSdKj80rofc8P=u0)*z4CjPdI{!Ms>?8QVE!CC+bxhpIzc%IC-fjcR<$#6NI9)8Q5J(j!%Fs#;2|59UH|kWY=n{@zO+g7feRdDLFai%-MV{f5yayShGGqUWgdZcKet)vdLUyUMk5oz(Vg)!JkIH&jBN^%9PAj-0AK?M3~NkMY2HY5!53U%Pu}<RgqKH#aGc=lyPh$bBoT+}Pu!+8&cjZ{$k{sq=2R=%&_TYtBK)XDw0dp*C%}MU9tx81kFpsGsMp@mw}-67q|iRDXNL)!4675y+orP@iiX9-`_;t1%t9trE`H>T%JSC$o?*ABj4&eOB|umU<qJ+tX3FuLw(t=aF*@(7*dY%&+%3)O@j|U5xyX`B<-p1gknUrjJHmYbUm6@qg+(8sBY4?qb1uSS}5&FaI1w9??|QiDfD756v!zus!kBu`X>)qvowG;xdnO4Rzj)H3B9ox?Mru;>}()e%+mT53ueg^2VjHJs<NfPnuh7?ihdg+91XCceuYL&_C-l+_$v7i~bq&olyCCH#ILTo1UP53eJ~BZBRd{Um!PaLH(S*fqa+K7Ht1Fe6H6z?AO<V$lv^f{i<{t_c?t_A-_>leXeD}K|KFH@I>x$UG1;A{a1B;vE?g|{Mu8D-*QVGbv#m3MqVN>w&(5$+%Gi>KtAvo?)O$c#k!oWEAp3(a9$3LROj7%a<s}VFB5Q`-Exulb2HGt*ijt+^y%>XtSwQ<=N>>_&!)E1+<6i5C#f;-hDKw10+(U@RU5EAhep*nD90h=8uYL70sC7Bzvs0F??B#k9Om_ZMyx0HQ^+&?f%BNjAICFyEb`0|xX*cYOzp4nQ5^Ennz&A#?1THaEl;sMj&<hH$OtuliBIUiAQ$Foz;kuIvyJ$Qyv=I0o!Yi^st%2r{zcv;k2;T5TOK@*luEHx<^C^Je<SasOt!4Zo0i17F>f^PQ%@8{{<JUF!?d3o$nmibD2F^DRE=+}bwaIg_Q#cwr}~2XjT5QVb<k9}Ci3NvaDKZsQuhOv1Yea~E;PaYRgN0!_*h4_LjSgP)%s(*(?nfg%-!1|uQ(UmKlUu<-RSlh=Qj)1`4c#vmJglKzw{*>pWG$X{@OqFK>p58ZNGWxX7$`*I}(a<st?7y%ljVdTc3XDU;nfk#}<)7-G`W~jX-W}f%Q4fLpAR#PNR^QaK?JOv^IWUe|Z^l+f+4<CF^iCzHQ+Od~TQ8xWAfn2+xDNSE7H^Zq?u96{XfyQ`}zkzvqGVa8tq3a$bxv7ty~g#y3@}uI8`p!DZzAmLvE78^6yQa1;6Zf>>{x-s`RQBj6s!-|eK%m$`2XwLSKy$hF?Har^_FaoxF;fc$!K%!{xhIG)`N+tfIv-r)ZK!wuB`{*)@$s=mQ|$>WOpw`D@!3hSQber<I<vL4Hed}j#G%aTL5zC;$m_~t%1@8NaTeX0FHarAdui*?}L1XZ8L)D@7|&xg+qD}(cut|rDYp2u<UAECZ4q0ME!;2p+4c|py0?O;dbGw$*DcToK;hl7z%h{1jDWZYMo?+?P~?y%u=?c=duDMzD!rZrgKrf0%?m90~eUyDY4cAtX#hfdQlPUd5{|7qib_Z!xA$m@*9I{Y!9k<^3b^Dc~YZju_uH0y?XuD7k&gZ?Y$pq|IyS%mp<5c$$|ST{-)RrP7<a~OHW=a@%XoblY9@*46Kz18|@t^Ehy(+2;G{Qf@}zj>g#5481g+OG1iQ?QPO%vJX%_K#_hkDh?zFss_{iW4&;k6DIwJI-0%CtFr!L+)~0oflhVD%|H(&W-#F>eDp08{T{5$%}m0VXWt|3sn7B@8?He`UIXg15V(1)lgtN=4X9e7jFI5NzJb_#nJy{6LoyFHwINd)^;V(Ke{^VWbk0ThwM}Zxo;5aHvO6zibbn$PdXnh9i4Ff%2*fuTQ5cZ7x2aJ9o{uTezy#sPmLXLKRS0R#&MmDb-RV@NX0Ajk#|Xhb$gw&`hJvk{3hfb64bh6YETl-lfAZK{7J6Z{xSOpsr{;Y9Q}WPf&2V9+12No9{+_r>j>0yjy^M!=9WS`ab6PUVjZ4&3H`I(!n#rSf?7XKweKL`*cSH*2fC=^sX0GFJ|qCwk=(oR++Feo#_zZt$A3tunisZ%h8-&Z#}oODgX;Qdo|q1Kx8;~e3u??&49U0y^}h#oo?<PYm+xjl|7GJ;ZZFB_<$F2M|LHLt&#x!i%JH;Sbw&PqGu|`Y8$CevAK{I>^kS?ho)y%(XIf}N?jNnz4ePCHxc|x333=liI6foYmgw^4QMezlZN+nUb2IWkCgS=#E)eg{Ds@F3=!)x6>iT%U<kkcGwPh>ztJFC)FN`w=qJMZU)Mx8(wZ2*BM<Va@67xuVrmiFAozpN*csSO*P^W@&984dUqJJeX+|T?uI}+zR8vWac<2ZDT>#oLIy%YJrP4J%N;1fJQe%pg_*4IZprzwK<&3Fd+6JM-vP2<#Yvv+xjJhmO4JBr!yzR~>&#(&Wr^{}c4e!sBqE&6B1{IbS=#dB8hd*u1Qpbl$I!|!n>Xge|AKVn{_SgYPkTfU@39#jJBRctr2>fbLL^1&T(UhbDw>!c~5sLCzp%V7JPo%K`OGrKtYZ+?Jrtlnz<v0tl$yzNSCr+0{|bL%)?jMFC_)}_K()O@rx^GCjG5$e3-1w2PgXo=jo2IqGc-sfmBzhit`3A|4mo?AWF*xQDpfA3?sPYZn-ruL)OaO63sVZXk1Qu9bFItuxy6}Z0mMXGtEWf+I?)3?X_&(D0%m@t*&^u&9Wy$#o*9;48|t_j<}<dAybXdXQe`I(k@&aD@!w%^!vDe`t}@IIl><>g6pi~AECXKmV^1F~Homm%LY2KA8T7@ps~j$oV_!;$Z(q3XvJdlLOKF2wc(9mf0TRA<nC=5clWEnyn2?*ZqKH)w`=dNiL}hm9F-BF`9#b#l~6yx)8K2)XeZ>MBQObzQS(d5QdmGv*QRqb$9(UFzpC=WyLj7m4pX#bi;r<?|}k!^hK}G9Qfv+|d7GPp*>_@q5*pd5|}^sn4~h3sL9Y=3M~!oGG~Ogx1G<{xpS=JJrJVVo%g)^|?Dd@VP1QoT!<j@qBT$8uIz0@VwLDPpo_U>tLLb4e`D`LowXvtZI$^{<%><>D%Ewb7WWa?-+=>y^;mj>sevwf2upyVcTp^_4kGjL!Pw_#>vtW`&)c8@=>^-HwE@q`(?IFMt*+~w*M{e4{g~NAa7e$t#6it({bM$dlcJKC>8Fzu3p9cWQSwu->U%D!>fjNYCCJ4Ltd#S_V=joaMk|;axI}J-uIrXi}m439P)2<xjjqqJ&m{bkcYiS|6Lo^{eyATedI@iu|BN#$8&`BDL!}ULp)C%Zmf>8-Saj2w@JYJ)e{@=JeBhk@|$Pzp1Elo+=o|Axf^wG3Hw#+dN0*~Lspe*-HV_;AI!&l$eOv3YacMLXTF(^`CkO%^s0vI&ZIcp=gdW}O&^E#zr_|jZ+0n-{(*zB{`}o}h{~^3LO#9{>$4Z;>8L6gr_dD4qfh14??;TmUg)2qB|bNA0=|#r;f?-Joblf8Xg5{Q_BbE(|LlT!;dK`G8@(DMk4Qis*ixM@^O`ouvq$1{udTs*fE3*@e$Z1~@2X!{_fd)0OZ3lL8udJSiCRC6T}GmRcx`OwwexEIG-aNE+;h2F$4pCZW4^ep!#Mp*pq^9ZQTI{Smg|wvu7G+N*h#IE<}-US&Ifml-~IruBZZD4H+{qU-!cNvBhQXw9P16NV|n;}l?)fr|425hhdoQ;_pMiMAa8;9&qlYlcrJc(6ZxPwc>dk_0PmmQ-$y>D9X|KzEF8}<50KBa;<>5)TXo&B=1aFn<#z+H-fq~5<It!a@?q&vw{?Q>oSU_p$}Jy*aDMNcR`(&+3O?xHaX0ek&2V2A(ggjBcf|NFw)9hUYk~gXj^j84*k_~O+as@sda%vOi2I^H`(PZeoVZVZUlrS#Wg_w}_<fVT!2Bs{d&W#bzW6$xuTQm6>##Oq4)TB8)Hs%#`SJd9@=|<m<b13r7c1iX1FM&zzkdVNr=>OSpR27$|MXnvH($hk@A}Q??{gLJ4_&?SeUit!&_CCCJYTF2#`SuO4f&I5n5Q!@VEvzS6#10v*v?kP2dh7KK8L);F&rN+XZ-#y;V<N;U#atD{`?j7pXn0vl#y6xVm7OFQrmk2+gaF#_xWeb<9b)-Hu~@HgZDz?592ws$$jMYEx4}^u8;Mk_bZGOS`5Euxo}I>q3KZ?JjZ@(i1lhD{#}M`b~ZeZr5um<q8-=bdo}Mokaw}+JXTFm_kpIy<uT6Q9C%NDy%4VN|29NEy@9G{d$)RcZ~1ow^3OFfey`1H9W#EOf$_(7#`(%M1HYG<g!f#Q9y@S<=vPv$tH#Jx$WN!nd2Ce?_dhXs4``{78SBri3u=6G>{fj4=rFZCR?iBm-mHVRqyN$tc<&T)2H%UWwIBVD*2ntRDHQLY6V9T4z*mgZ*9G6>^>V`VdBJR0x3^fQ;{5%Fd{iMEH(MOurwz@9yl5HRw+so!?~CWU;Qi6dFzj#ma(qu93*M(&T5iXChWE>`p4jW4|LHEc-i7a0>%aBiy2$VIy-Ld?>UyeGZGv%vpX2@WxJbNzXw?+C`(@P0KjFBprNncER%bhYPtoC8lrA6s7wYZBOEvGzPXaJb?zL)O7~93*_XS(KBA*$8`O@$m>bX;QjN|zg^Lo!FtcSb8(Emjt?3XPAzOQ(5H1aaruwTs{s`FwCJc|6<DV+D*s2|()ix@v9CFXB*dTf8wTj)QdGWPdkXIz)d*^%$;j_(^B&5rMZM7+Q_hc~F)?AsULqj-}S&*y`(sBx_6L-2dO<>hgIFuVn}Kh0FNep>HTL;g>GocEzKRBo(<_u!T#{NBR9p7?!h)rQFLcSrx=%(!35*97CF9*XOQYaP^8v2Mt{=VKk-?W@K&n}d<N#T`zX+k^TduW}RT>(MiO?w<bm-0=nQJ&?Q+cyAmx5qWjgoB5H3>$PzO#_3ZY+d26z-orOIiu@Jo!LoLt>Tle47P-eO^mj{Khy8T_3eof+tc<y0;zuO5befCSJut~XL6lJbbMV*y1o8I@|6l(Ev259LRsL`P1~Gk##BFd&Y-!lUQ?rSuA`Nr{cQX~4k}h<nr=n+K6VF4s(uF1IdFZ9s#J$LBbfFL3i{6AyydxPv7xtoer1xeMA4U$P3n$Ts(I>NsuOb)Ig*)i0=rL^K$H@J3;bpq;5?y$aevE#UO?)4DhA#YzzK?!{O?)qTfi65v-%CHtCccL}PZyq|@1Y-J6W>jqqYF>cchhZb;=9Nbbm4LOF8V<>@dM;px-gb5+({R%ryrniU=z2JOX$M6bSr%hoA?BBB3<|=eFA+5n|M$154x}uy(hf`o47C8oGz?O_odfn6R$v4q6>@Dg+=M*$iie%x-d6gn3FEdPA^O^z$Tub%t{yjM$b>r%O>tdW~2)<(B0^{*u-;?>FL6B^c-{-Ht}p^TDmX|JsUj>n|Nk2HC>pBF3dz1=Amb%=VKEuO_rhyz38RsHQB_Qkxl5rj`U{q&TQf#WN*4~7(Ij@&L$o~PNoZ2(Ie<9*~GV#F?8WEy6`AnxR1V_zKu<M9eIQ<+)H0aU&|)GhCECc?xC-tZ)FqTLLQ<Echk4fH?xVaCT(=#F8XTvCN}Yn<UzXd0A09&F0|4&(&w>>N0D>r!U^;!`gk_+!Q>FSuqS;m{dYF;_GAaT(3jqx-jq$;MAoJYE6^S5f_M$mlPpIU7N!de(1rQwp7b(o;_hT#y3md8PA|bGUX08|7v`WBqZeTlFGRY~h1uwZ=mputjbs+OFf(14k1i}tH_|=W#J$OybYU~PH{Fj-+)Q?+3q$B;dLK6N;bb^n7(pLSpTZ`-f?P=#Zl?>k(S_^iE9lGF#G}czbm1C$G<_MH_#$#EUATq5h`x|bd;z(cE?iAtKwruxKA+q~7jC2r=h1~x^!fDJY~tg{@pR!}`Z)R^Ht`<h?{r~%dJlR#Hu1(}Q@YSZ7uKLRBCC@%=t57runb-3POna{$|hcgEI}6*qgSC<W)rVS7NH9Z(JRu+vx%1_3(|!~y3m6z^rn}k*J2a*C;jL`Gu@va$R-|2_Mr=h(?jVa*u<xjQ|Q7Kbm4NkFq%G<9?2#?ja)_-E}~DPPiGUKK`x{V7tm+WXR?XUBA3#I^XbCbbm2JqEc#eB@qy$Zy08a*AU&8(ye-*|E^JJ9)TMYEvLV@sF04)$R;3H8&>PYlu!+|vE7OG)>GkRL*u?9Q<>|t*bYU&J(4St1-hxfM3mHfkhSIyx`?85!$PskmRJt&dE}TZU&_}X~k0Phjg)``*=%d-h$B;AW!dZ0TSo&C=*D-A31K7m7lfm?0p1<x%&TDrz@z!KRdPAPG)?|HpYkDg-@s?ygdOe<lmShWh3m)s1Y~n#|;{C|J^u9c%{m7B@kvw+&*u=xw#QT$@>7#j!`jZ3b1GxYF*~Gh%t?Aw9UCCDTR@{fKWDq@w+tif|qlfV`x^m2}{P|g8yO-D=khkd%=r73o^cQp|1Nez9O}vN!P24q+*$m(t{w(<$Ht{>;efk~xHS#w78a<A@M~|bwW)uHNKBIr6|CiW)Gk~A@^E3Kq`g`&L{XP8)`GWq1p49-#{%2(quS^!9SEh%siFYJj=^g3K4L^=ub2jk?iLDlyk<3QVNPn(@a(th&iQgpe&~MVOkk{x}=-0_O`gQsf@-_VlJ+%Q%JPY}eE=@c)`5!$u&qX1_k8@LqO}s*4Ye*W&-{?lVGb!iKnLmrCAm7uaiDx3e(4~nNAm#iOU=wddR;D+ihm#@naQYTD@l|9;`YQT7vN?SoeHPh(K8rp!$+;iPCO$N=^(Cv2wdhsoX~>N9H1ww$DE0A_P5c&llYWbSmApc~O8=X@PXC+!n0!KiOiyV5rB+h1iI-;+_ad{<z3BDG-1K_%req;{Q+hkH0=*r*XOi0L$tM11Vw*q)kPYbp^s1zhUX@;ubfy=i=Ot6n^U@2GndpV--edu~H{DD&qMPZ{$Z+~J`hIc?eLwvToA@(w75y3g9yyPGkN!6~i~cwLJUNzro_>%VN<T>7X82LN+t|ccCbl_b53(=42fZ9wg<g)HmP|uWOHa^1sqX|f@w?<L`d#`B@+$oX-A?{Zx6@yekLfSzsSKdhcPcjVQe=60DSCG{@!q5ty*GU@S&u%LZXuh}E%d2mJNi_56xov=MPE+-NncLiX!tQVHnNHDNo+^Rx#R@;T>1bqfIfiUf~-n!L9a~~q}Qg`B=gd1((90g>2>I>NpE^<`Vi7gA3|S1PNOfNpCI?sPtZS-Z|EQC`JB+i3y{y~(!`DAJ-RgUT;$($Y2v?;=jqbK(~$@1(!{?p+eZIJe@?EXKd0X^{Fr;U*u;+~wyoq8at?h8y%X7k-icm@EJrUx&rGJJXQuz7fige;VH1Bu-ladH$CEec@$`qJo&J#ifqY5-Ku>P~Wqzh-6L%*|(cS4C$nNwG^zm%sv&r7{+4L3UVEPLBX3|36Oy5UNrSGGkA*1ML=vT<)^egl`<VN}(`U7$g{Q>=@;m6#5$tM0*&J%foJVL)fUqjBNuc1#O2hb<c!^jr&FnSlVHoXhIJz109o*qQjp$F0Xldb9f>5=3RdL(^4xq!Z&evv#uzexW~ex!e<XLkZ+Ey&I$UXo3`JXwHVo?eYK(yP&HlDX(L>0ab-bT4`ZG9A4F-Gh{M!Gk}G7bTz5rHQ+cx9HNuQ<KN((!^gFeyklY*u*a<wq4|6aw~l?eFQm$K7!ts>_l%%FH4r8m!;<*Gt+a>ziFVXFW=b2-;s~#@93|{c={{)Tk;|OE&VI`f&P`A-2lq^lATSwH0e$+O>aqdptqzCBgfN+(dV;?Zz5;YH_;E1E9i&mH^|NO8}x_dKKeuY7xE1K3q7q9c!e%aJR^CBE=@ce`G77>+?9MumnNQ<d`p)mp4;ii+9WPbJZmB|IDzl^v*hpD#IKPT=-24G$u;!dbSpWDZlzBr!|2oLBgroGk@VqYd-`ztXflXCnm&{4PoGJTCL`(5^u6SI`d<1?@*@2v{S*0_{)z7F1j_p5%qCulEJ-g!FU}@jg)C36La$9$qt~W4Bx}+e(wmZA^rrM?WCeONdLz<<-iTh8EK09SuR*%dYtT!Rsp+NZ`AJ#V^7Ci$G~{KvH1S7<A8X$uHu2MmZ5_FY+(lnRpGYpIPo(!FN6`Dx{mHg;e|jadEWHvvKbeD`pPqq~^)Ul~7B`UZ=+eahW%i2xFI~QH^@{7G`tp?lo{s!VmnQB;%KGTWCSH*&O|MAzBU{q_=%M5=dMJGyIiEg`zK~6PJGqIzoqmZtOus~bLf)W1p*uN&59!jxvyflt(!>jsvThb;6E8((q?e+XBeT)V(JPa#^vd+=WL|o8dPOofy&~O{%u4s9mvH*Aww7QMFPPXektxUw^c3{h22j@D*KFc(<TZL6{Uo`Yev-a}w9<Fb*OJreYw1hLk@ThXCFF4W68bW7G<_L8hMY-{q3<N4={xDM<X(C#{Wf`%ew&^^exfJPQ#ygN{-$IT&rBAgXQt;Qi_>$`-Ppv-kX7hq=-y;)x;MQZ*^pk3?n^eM`_h|}&FIbP{$wM%Ki!Y4OZTJukTvK&bQ4*cZlaeZ^V7@Hi;!vPMd;~CS(nrEXYp4C@HG7u{V&6hwfiqN@ePS>1{p!Fqesxkkc;SJ=!3|K^g;A)WIuX0x-aQZ_obW2N^}#w7@415jGm9oK+i|dMH=Y2=q{wJ?=JjVJSQpZdrmg-JY+h09(qyIjb4;qgRDreL2pL-(VNk`lA-jj^nv6!`at?9av}W>ax%G)KAFCn+)iIjKSf@mpQ7I<pV05qQ#pZh4M@c%o`=jr&qH@73)9`{RmoEHs`NT!IeHy>1F|x`0lf)Xo!*4rn5;-|Os`LR((BV}ktOK0=#|KV^h)$%PCu>_#n{AiB)0g(<MUr)`$|gomCQts=byhLC4WbzpvUviACr<lCSNm;C+*~Gx-gC&PhKVC=)#lqc=9ZHk}ljqk0+0kJLtl-^mx)nuB8i?(&Nbk<WjnD2|b=XL@uEVm(k<NW8^ZrFoqsao+D%E!kzSZ@;bSbE{vtelXuBjy6`qVo_tE)rVA73@#F_Gfi9G5;Rp5+{!2>!FPWJh&p+4rv*a58JSRP#e{SH<Iq5<-y7UqLN4n9axv`#wW#~ER#YpcY_3zF3A*`2VzSQG<68a{YU%s4w!sbclV{^_|p?{M3>(BWu^h+||{kR?oeUhvXK3qS9rX=f$cvZ5j(~tE>+?_1q^kcme&qJnn`mw%=ry}K=>R1oOWxW*sW%#jvik~7k7=Em`;;RimuDg!)SzOj{9|P9+KICNjWcKO9KEht)47xCa?nC}gM$m<0=ssj1IfgDAME4=vkb~&LZgd~A3E7P<^ricd^+{j4&_wqktCJ?Wuo&Hk^dyVXh56_{WJxj~U6_mRLl!4<(S<H_AF>4LLKo(w`;Z=FPP#A;-G{73=AjFV(tXIfWKp`X2Hl5jOxB<ao6&v9R%A1}uq)k%>`Zp03kTAD$Y63HT{w#FxEBd#`-6Yaud%_&CB^^ie-ZcNKlwd@ru!epCI6fHf7X@sZ;neG>-#_Q@@t$*{>?$+y62?6098P~^{f34>;5kI'

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
