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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d5cbe3dc52d94d78848c111fb959e8f2/part_009.stl', 'relative_path': 'd5cbe3dc52d94d78848c111fb959e8f2/part_009.stl', 'source_sha256': 'fa217944dfa339b92aeb5ce8d8fac5fe1032533002b1a24dd4d860068a601230', 'input_faces': 1152, 'input_vertices': 661, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05691120773553848, -0.2596682608127594, -0.15759462118148804], [0.23860964179039001, 0.0724838525056839, 0.2473301887512207]]}
GEOMETRY_BASE85 = 'c$}r31#}fh`1bb(cXzuu#UZ$5(E>pN#r38T2oAx5FP7jETzi24#XUG&G!UHP6u3Z<3R)x-TE08)^Q6h0e&0FY`Tu*)d!FBYn9R=Z&d$uv&YTALCrX^zz<>FTOZ`he46S7tDpDJnjbT9{Lwa=!8eF>nz!5ehz4+?CIGxw5b<=?MHe;AEs%ZD1!QDcNR<jqa(W6SylJ=rK280X=3GCl>KuGr><u?fIJ2=SW4-O6-807g~tWu?NCGEc7l(dhr{}2C5=_!Iayx^9j9(DSTJFL`xvC2L_@pFsssGi!T)G~+ff}cfv``&#A<lplZI}AUW_^zOLdzBjf*X>olYq%l4*}m2>$tU}nEeU-`vZa!b75Hc;{7;+JZ}*`bd*t7*Ej}dqhyE_UD^*G<r*VAhX7NWH5Z_U?!*R){z_ZANzH4}ll*hd*<1xv9#9Hyq?cW}i^y5~pfxi;@oXfLQuE!r2T;h)|jr8+6pOE7|TDe&AACp6TtM6vHK1Rnk3&bCHWRv{PadEf&-Q%zmlFzv9;=9V3TjlQ#)P+C3nfPW}|C91}&#R1+d?u8KAG%VmoAG1)A(B39^hWWcdx~!sI=v76Q1RWfx8ORoOt~9=fANj)Q%O0U`?tyca)q~tpXV;l>+$=o34QDL+;aV``i*xc^qq@($@Q_)X2$&u_ec7#pXI!adnpgWuL(cHLez)HEjEciC8zlIz(3`DtzCuJ!Ow*9?5H94*ZrXt?$^|h8^mu^=#=RB8sm>9^h?~|FFK*!>V)adWG{adKO#)-qdD!7_|}Wja(#^7UWQ4!X?MkUoVc+=%60qRDZd21D>_*6F+Z$?KVt#%Fa8$g2`I5ljyod+<(cu}py;)_^TeN(7wMbU!}HSkB<}mHY$%WQ>uT{^{e4{WpSuUgOY!q*$)|7ZBuPJaiTJLQk5T_!k>86yKbQDc&{LEr`rcys`vpmn{zzlo-=7aJli!Q`u9trwwk2BpcUy<c?<H-;x2}#~D(SYh#rZA?fFHP3o);rz;SBlrC3TQb%ldME?fEjEmh{W7u9Nh!PvpF;3zwp$oXby&?+Sg4_Mm&RGvcqAvsUWWhoq?gNq&>xt~FCd%@JGhe3@%j%I~#x#kVH!-X^~9-W`4keB){vJRk3;MoIo_Yao4}s*&>Vuf`vg^y^CFI8!^JKIbg7QT+9<B%O74lRUr1n;fgW{DZ}pi+`v#+J_C};E$<1NBq-aa=zxqLE^hQUx*Svc<&rZzp1?V&dT*Af7i^?avjXgc~HK;i%3512T`aG+t#g-^r=qm!*xhfQT}d6G4UOVhogOn=#2ZZCtR+(G34YBNjEq(?qgJl`0k|3r5+j&|CZypqM9T9FT13EIGizOrJQ?x#dq}`hv%sINAW!mgj4Q!c>6=*pV}qAtrHcTxc+5F%W)QsMLs9;!5>`#&)px*ao?uh`$07EtAUa()>p2ZF=LVV?jHT+d31D17o&V@?o7G=)|1Mpx8`bT=Z&TLSIG5An)rzLRZrk~SiJ}Jz4|RlZ~0}A_Q%@!NuCcY-!rt6vEjQ!_ZAi37&vT-O6NF}SITc49Jff$H>(r<#q4(5MK9K$FXj946y<SLmil8oIwjZD%()o-X6N#9pRLCm#J4WZ#`73l8SP^J8WTj%wnP88>pJ}4=VPS&!%O42=(7g*t?ZdblCJ2DGoo!~;XasC>PdS4%s8*r<<JfVoT($_X?-5;$zK)NeiSGu*E#Eq^OF8fcGR!#X{22-o<+yV?{{wG)2?QBsYlUAQJyOYkx!4Pp>qE!mAWXum-n14n*M<$`7}6#`yN~l_b2^l@twV+kUk~`^&sWl@sj`ZX(&&SAC4RQ8`{6oY0jeD4zxq>J4}}R1B&DN=dhujcyvVWpR;(LOY-~XAM#uncW+FU^slbtyq0Z3d2WrJCi$N;rTuj6uZjECI>}rqPwMZHPtq$=Z>?q}B9w1m*a!D<dk-A9X*coRiv~*hjRSw<`c$gFP>wrnoaAHOi$Z;?I0k;(YB;YK&ykPs3HWV>qu%bWis!pTO&NE%SKpWNn+qnPoJG%y@9^7#_P>1}q|bU-`Xy`RQ{=yW$sWH1zTv+U^=ELS1Mts@Z+7S_$F+YbepLJ{x8XNVc23f_%_;4zl{wLJxz3wIaDBGdmU?St&LF<4y}w)sSHHZjgueT7M%>@IlQu{`nevHmpOR7Pr@L|*Y4?l_vyp#}<QF9WXK07xe5?Nlx&E%w6L7w1)2xtuZm*E~X-^k=Qp%C~JMmr1A0wYBN9De{l8jg>I&cl@p=)$IInTrw#CN|+F8P~hkE353o6IT4U)2ET8<1+I9Dl?)@$DPGlXAG$-H`U&5t<U^U0)6NeaA>VzoFU1cdb2(e143OcFjFxlla!Y9&*22ub(5o!55Lf>R!}`($(=ig?uC99qaiUsSj3`k&@myV3_!BXXeY2?$=i96Z%%yU!~sLi*A&5)f})ye8<Kws6P?iC4YP0^fE3soV!{{`F?$V(J!I@%a!5s_iK|%y|VgdgMTY*n3Vf^(d}M-)ur-$Sg%qXKt6fl8wJsCj(jNNKu4dF@TdEsp4|LP>d(J^hE38Q8;5O|<hu0ng@0n$50d};j7O1AwKX{2t|gMb$S|qLj^2HcKD5y)@rMLYlzP@H9O;W+T`O9|2mNpGQKXOQgYm`U&SRxs1YdyPbCQhnoP{RI^>O#ShWCjdDq`H!BL>&4=OghQzqdjAnV}c1bB|2Yk6GKx<9<E%+ver3zajP0I`5D7vmW{3S4brNnLW5O>UmHl@m&QS7>D*9gmGZt6QmzlUB+ET@=-F*usgEKc^V6D%l$WA-@M?L(9iiu-Ukf#bgBPFr}N^wXHAj*&xo2P??29t55;!|RY&>T4UzWE>`+whrx86>>Vfm?M0qZZHkZVA#x}rnS7D2^=Vt5Q#kZ##CF3#URW)dUd%cuDb!p_^J}vskW_5m)^F25g{cGQ3GR`uajEC<xU!EiL*fv~e|48wTUC-n>a?MSA0{%|;%k0v=nT^XydPk$L@COc+dT8F7BhQzkVOeRn%rs@By>fN`M)I-hoe<wqeGbNZ&6mh~iL35s@!i8xNcpWY?eV@_*GI++uGSM#A6n#-d>qw#%6)ZY-;e(I#BJ%{t;)&eeb<?GA=;A*O{G4V<uc0qv{B*{@_n@j{bMP-XS?$(M1QgODB6Gej_W~aXMX7~&!e;CCA^ovh(bHx#oUq5cb6<6{e>~M8Ty4%H^euK{et_r?};4OS@NFvR?IQ<gE?>Fx|I9{<=hc1*UemNm*>k_!azMcw;Szq?SazXxr^r(-`v^){qojXQqP^m%OQQUIXG^uzUX(0jm7)x?WSl~&4+<fj$-q~cSaw;^{sbb>a)GrkI27x2lUe~GUNUhd4}}IULv0+^QKFA3pLs%>Gyxadw2gYQlH%g28-`{RSESo;F^p_%>paLw?`gF{aNrHe^+3W_>R?W<T@MEw;xaFn~^Tm+g>$LukuHWZ+uN9*Wa8zAN}6!H1b>-bsM1`{<PQ2cV0_^b~EjLjGxnG5Z}xfgmR|-Ebn8^S+$Ul+3Y*{yH7o&T{UObhd(&ULdn-PMtm!6Bjn$3I^N%Nu0uKLdmiwNs1J#@Croe5&mS&Y;o)vCe|%jTzgWc|@5gbQz<*S3vgC6r0_{TD0Qd!K$hh0cd}XPZe_@%lWA?Uhj>!E;(}n4Ct-yWBI{|(W{A9=Qd{2EZ^9;_J15n=FFXg(pANpNN=o_vZGA?uG{#)8}N1DO#lkCU)Q;jK>Xqu7mk6F0RpI^wlh<nC#<iGU`o{xHMr9N9TB9PvSlH(fDg{8l8rg9<u%cYnXNpU+ep>IUrk#^njwZ4?cnjQmx;#>S(o;et|q<n+>UNsEu&#nNp&naV(zOsdRn@7K5zHDj=dG3v;$z|Thy0r-J=~HUM&sbI7%dC4n@!p(l7{-I`hv0mly_fdSk#vdpE_)-4ckfg}`<(bQ+Lh|PWq!$cepcE^`=o!6Ps7G2XU5jjp1Ez^r5w(VYcamGWkf${v&1)!CdP3$JJ24EyNvm&s|Lnf>ptPVZS0@o+kdW)_A^l$jJN-;DD#@m`BU*8b+RVLU84qJzH{3bv|}-Ne|3x+C%&uTL_EJgf5G$nc>??z59Il^TFk-w!Kj(yTW&j^-~NAy?;N>Wd`H?=Xb(%KmFLOz=>XE72t&UR_!0foliD)h=Ipr=*Jpa&T?u_-)>2%DP8YW(^sO{AkiPkgsD!@b;5ej@zO~LP|HoZfPrf^l(6?`IiS)e}tw`vbzh_7KfBGKw^7Cgx`UyFvC-mL1VQ5#~Z@c*=@Li{Ri0{gs-Q|@}zq4rPL$*dFOmED8DgA}@aN4SbzV%yX^dmn0$Gxt@yw4a<9(c3C>$p*`<vzN$Hr?Ts|C9L`4;;+mb^RS>u425M=iDBz;}-Y>?RM!+Ug_-(op}F>4Ly)By;-XZ`qL-vk9r-qNm103w<%6~T{lM(8Min;7CG*9+;^xyR=Sd2=^eXgNxx}sTzE2JdUtk=H(VVud8N1RzQg;@PtQ+#<sVTR^?P#4vk85Ba3%CF@886DUC*Zt@Eo;hdd#alA=^1mo5Jh<I>H)bJQq;NtNyqbCqw(N>h6B8>-pj#+MNvzyy~;L>LTW4j1fD%{0gfv?roiXi`V(qJAiSr&zs1EzH9n3w8NK!FL~XsL{~BX|I%}b*K;@J8r~x!Q;+xZi?@{dC*$do@m|-n_ml<VPx{d-f8$QS2=RYfw$#fHSRnaYg+kYP`RR{#6utb%HZT9oeuw;SJ;yu$(`TmPxxBgC%P;nIk(BFHA@B653Q0L!CvNWdDu0Cq@*ZQ}es;twee6oSAFS$q(aZ050ORGD*T=m4u*6bsYi}E``swO568%iy`Cj$VY&r}5QJdA6FAX>^&y(Ixx-R`9zTU1Hmp&oA)(#t&44Dts+iiEV#PGFt-fET+^T%4hU~k$&{QvYL{&U3F`yF>o6!O>lDf`((^8G~b*Boc^iLdvA#_1{I>-}b&ulKX=6Tjj6jMgt3bu-9!A-x~BYS$6}KmEQr623N0@H{~9wQ+^viokb5Z5(18J%seyxW!c~8s*W(KXJZ3{&CfO1790QIcmltA8p)a9!??kS0AUj4yA{$jqBWpvWc&c5954&eCVuE0KPWPv<?-9uZ>IXhkWU4<J&l2AKxCV245Q||LbexYNJLi@%3?goUf1b|Mj);{J*|7o_AKS4_|waa2*H{Uw`kgstrSW?fu1ZU<Asky}!8juR(h4J;+{ltN8l+lw<!699MgvGWPF7yQRICIrm+_b=BVE>{T8hAN{>ADwFiv`g@|IlCSvsd!<pS8q#a;q0Wj8#n<0kUAz0^JzIOvb?qLC{I&ODvqCu1>+jLN3&hvo$K!ncecbK49QkYS^>MyFKj7N+gZTP9L!7VAGyI!gn@_OH{e$vo^BDF;_|B%!dpK_N5?`Muv1dMk?{eC_ih1p%`1(AI=Q%?@+PsZ@-bZ{l*5-L!R};x|tj`OXEwjMa=8?>Zoba`ICnF+1zHe*uRL&OV;A`_*_A8CherWSx*5xipKm4G~>smt}$aCXL7mof`n@_VY&Bpt#HveX&-G_2&^L6H|vq-Pa?-{c$i?7cI8W&>We_V=w@Iz<JM>YL|{I&T;Bh5eXwfRO@lax{)^?6IDe+BXNc}~l}I?`+NqSm=u@U{8Xe|>F!)lB6t{(t6a&o#ku^?6<Y0DP~|=7EiK-@(`Bjh!)pIIcF&Y{dj4y*4jxrW}fY*XFU~e0|>Aj2Q-Bn?E<Fh4Q<K_x!n$ax{Ex9^M`^2EI0*|F5rq7l`w<?*jk&+WfzjVlmFE=0rS)e}+qaF&nMG_1C{gq*#acN&Bu5=j-1!TvPVK*S?R~8(zeH)V`;<lifsm?fZ-K+sF70FsVD{3&OD8#~J;U`S-_rXu92KucALAf9?B@{oAj&4*K_?Z<ES;5NE-`QV!SlaEu$1rW0TPuH>#?7VAffj+J)LI_fX&l{1MczW#m6Sua?8{d<;U(h%gMegCp1E`qOpFLNYXjq+&U*NhW8P=5V89ew>foom7_q~G!y?bX>>QCFQq@H0$8JG}Csj9Z;PM{r#2`=E9FD9WjSXQcn1?~D_UA%E?ArQ`T%@&EIEbHW+;+V@aLofw>#_FXm3|Ic^TI=94k6g!LSGia=|Gfp!buHVp;`0k%)3f_xd#l+XY=eqo=;XBW;g;<vo`9j9yuCLX_*S`z9YV|?>+IM8DRtS9UyR-GrV6>Mng0Qa6IRx$hKO>P|`+jX4nTX^1rNuaBRY7@v9e+o{Z?_%&PQLfDj?MZKjeK%Fk@m`YuYk1wW{qp`LsFq01|5^<!u9zv%CjgH)>Z78i+WrABl6e2vzwn|@g7<A68fW&_hfyHIqD01?R&j7GM}uAanJdJ=Q_zk)W^RHV7-j?-QTEINqj5#I{KsK^`#wkRjmnsMn0^Qd6FFOBcE!)FY}GGr{>%KIG+)X#CM)7E9)Dq>5uRn(>Id8o+0Jhc@X{M{%$Bw+27FLy*@ueuJgW7q;K>^zCXLJ<;1*D=y>?|qtWl2*^YG*`@&G3=QpsvYmqPdsnFR-ANygb_}Oxx{Cnra9~X%JXk)~3FaO#*S?}l!^vAgN;}Y@pbrjCwE0BIwBlKSbgYZ4?qZ5AlJ<?8D&w6h6@(1qeE%{uix5vxR*&6fs_3Gh0zw$cx`nryfTXEg$eZu#%w!NiaF!t`n_1D&iSRZ0=eF~IBJv^{T+6UMB7sy{*XJWm7hx66erI<s%BA<(GrCqkl2A~}ql1u8Z`|3CN`ytzK|KAnHJiWH=#s1D0?+4mCnK)lxS7ZIz9O?H|LH_5~Vc!1D0*t4$^*OFVPL${NB#a{?CrEo@?%0L=ix)!r4p}h{-F^xA)O?8c=<QPZZN0t*4fK_I?q1FByaOMgJo&=V?wMaJ$?t7%alYC*B5T_x99LU+WDZDybz!5|<GxM|lIO+!G85L>B|3?Apvy8@UuTuJi*Ns{ALens!~Bx#Wq#z-vd<DJM^v8klKy2e<TG{`=1I0>!MfX*m9TEH@>9H5uAPqOY)b?2^>tIOQjNv8T0fNYa_)bLaq|m*9Jl^!oL9^jnGdk~wZU<<by<#5?cfi4gmFlxTk>4Q`TF`U^F@0cH?1G?>HY%m!&^GS*Vc)}`9_zc;=5M1-;*%C{pl3Er}(GB`&!8%NWWzw)-}}Hg8R35GRpbnJ??L^mS}f3&lBI7-i>}@LJDbz?VAoG{ew!F&#C<nuK&iX$bWvItP69cS|z@{_aj{A^Y8HdrZ|W7)Wv^6{tJ_$f7!Vd^QpyuM?NFp%K9C%a|G^tvD_FpMQ2C(B8v}}^Lt(h&qw7nvOdwwo<-VQM{pVOt*sf+56!56buz`up<Z{}B<qH)+aIKyj_2i(kG4+F46cOq$>+|O^O<6zeJ)l7>x0@yVq7{R3h%GaP2>~17T5E}ar7rY)`7nz58kh?VSSrbv=#C%&>Qvt-V!{gMLQz>Ko{1%rOdd}FM)4dEQ57+byncJL(iV@we^Q_zN=SKxqrsGyqL!-+6(CyCmJZvSL9-hbDs5v-~2e%U2fxd%JqHW|NcGJKc2vN$@K*DxX#GhXa|$V%KdSzjYRsyT~VL=r^I}~lMP6JZzk&VA6=z=HG>W!{h85H-&}VVo|E5eqv6jRBkRAc<HvDdBYzgPm#%>8-029`r$)X(`tIrFJ<i;C3g68OCX(+SjxzPpPE8%o>t08Eb7wfdYy6oA^}0YKd?!g?4DCbjJ91vm{B4oXjWxJmiTlr$e}C8x>rAzEp^m^#$X{DW>Uh{ye0RPcs6X#2qusJE#QNOccV!;ZUhyf~>#nQCciyRn`LvP!(Oy5;h2xfvMf-O7rM%BMe%J%Q%u}q>PO}l$^T9FrNzdYYO`Df8E^w{9!gax?0^~U9DoT3S%3JXBJUoT_H4EQ`@83f{p=EF%8$U$(SH8pfmMD+%%zrXd(sfRZ=Wl0Wd_S(3TYfw9Bo%ceJ%Rq{WC@H5m*>TOn-`6IGTp+ssk0q^t-o=+#-rv*{moqf`Sojo_PN<a8K1g36~%brMt>QPS-xj6ep~K~?_Jt@V8`-mD34JkZoWy{|2W@Vat`CsI~(Nsn4N0yJ+&Ri4>@Y$`N~}%<?MG|z6ZIpgyH%xZ;0|}>ywR6jgfv(L(Hf3=lX-6o1&b~CHUT#Xo>U-?q$v4_bh<-f*Z!3gub)OGrV`SiIRC^>+bi+Ut2G2F6)kb=4QwHh~rw2_;-6DpUBj>p2kqTr!2Kl{)UJ8%6Xr`JcXGv0@vYKHniu%Tyni#Ikw`urMr*uckO?ENa!0+cgeiGV~G#u?{XYMIWL#N{+ppG@!e_3QKYYW5%cQ7_^xAbe+=o{X2pE;z;Zjh{J?Qo*PbM~>?3ezzk+fOZHRhx<f_zv^VTz*ueSc&%>DxPVRuW^|EAY*e(l~OpN)qwp8QY{`;D^s;67g{h;?II0?=OFs387-*26EXiS+vV`Gx-Q_4W2Q0+3IK#i(yawoM6recitEdKdBS0o!pOvq#ADVk{U6Utj<K(|+---qqj-)WJC6r)c<hzTmh&hV+s1yLu7rgtouH6>$^g(f1=n+(-KG-RNhVKEr;qmTsJvwy(ju`WX5A=8NlGAr$+yBA&q4_D5J5QlmfD_ET6HGGUz3pghXo;nY;W1itw`CH%KJ&`)0Z2I;%hLHqE}XUq%CEg`<XkHflLANj;K;e7Z6>936R{^INVL0ruPkdL;1#MQiu`2X2&aw!ny(e|fUv%4XmBH7XJm!E_A<>o;sPyQBYAO3D2?`uZ7p~yd5Evz>PON@0zvqRy(ABXvCvlPCUG#?3nbSA7rI5ulH@)?ctJpKvm#xga;_o+)`kUo4P+LJ!^RSA84-;FhECerKschb&9dTqatHETY6ZQoFwukRZ&nnmI|X#0<hwCix)^!-XrH(}hGt0(T`m>dg{evA0-=L<2O2^}WoGS9z5`L+E}#te)r_5D-U^o*D<(e_(esj`Z%@6WQP=YX&6=Q7UaMLzoeuW5C~*Y}H=(;6cmZGV~7C>ZIr{b*K-LC9a<zjh`Z`DpvyjHy$RUfUmMHgsO#_3+wHXEt1q^xFPAD|#QwqwUwT!VloM+P=RyU*Gp<g&)Ilwf%<w`r3ZOIR8KU4WmyZy|$mx3_pW)*4q9@<J&7Jr?y|x48H+i+h1vXdkem{Pt!<t2glX+b;kMs*}oZf59#&&p-CT#|DXM&^#8N}w0?S-H`4d3T9dQD*Y>v>NlIg$N!t%=)aSgEwtv>F*AVL*_5HT>nj?R0f38)x4}5K(Z=A31^ED?9M0vFR!dBf7q}TQr8z)91y}lng(FE)R(DpAICnlmi+CJzwU*88E=j;2ajk@9Z-lFZlb{(IFe6;=AalY67?f|b{>-H2$mRprPf8vQ0MrNZ&V1g~{%2fZw>HmGpdanxqUt8A8m8)3(f465n<+q+PH1b4KPc-!L3>!QV%uw8q`W?9+c@VWDc@TLxwKG}iDDrUfRO(FfRPqe!Z1N29Na|Q}0JRNuEV&K2ttZ-3$5Y3W$CKw#XOriV=TK*o=a9!xN0G;nyHY!oyOJw16#G&;l6}eLsNa#xk;_t>lgpAzQ5%v=k@I;X8?_F#A-N7YkQz)5B==z`9zyL$9zvc-9Ymf;4yO($59hrMXDFURok5;L4xx@D$KBTuhT<lk$U@CU4It+t+o^5Hc5-2ATXJD?F`xMQQH-IuxF<?bJ5bw`JCG+($CD?J=TqmA=ac7B=aA=;$5F?S$B`Y>u4D(f615_^5;-wLaU!ZOIT6`LEl0MI|FJ>Kl2s`FLM=sBq4*s&A6bRsx3>8Dr&xvJmo~N59GZr|m7j*8xC*rnxeD2z8c6mhe^2d0{+`_36HTdoseQ;whmiY{hfybzhmj{y!^ujgkSCG*Q$xr~n~?jH>-ogj-Fnn?<a*@V)RbhUmC3cq-Kb5;O?eL8sKdzJ$i1nP$dg#6-qd>JdOU_=H}6jphT;O$D&zv>T2y~>E%LY2@5$ei8&SKH8<G7I+%rFh;=I(#<h<n1HfTz+3dJ!tgyJjIbYvBZuTis*RVcnq%|%wB_#V|xR-yPIwJ=$Q;$Nu6$SM>+r4}cvQ2d)MzO7NLLh<h&eQtw(!{5qR+?v{sT7s;!1Gyd9qD~-N<Ou3~as+u6buM`pc{Ft#c{I5T)j{q;u0X9su0ZyoCMNrkqiqPqr>Tj^Dioih+Q=#tpQNfb>m)<*G3pocG4c`WJMt0oA?jQ5A@W}8OY&awE?a!Nwu_;7t0&e|uT$M*rRur5&fkjPc+{X~pekRn(gNfR<dW1{<dWp7)NjdE$<?Th$koWDsea_r<h0bh<h0}$HmG{uUN96#QDewa<RJ{j;nXYSaPlnbHS#R-JnC)oJn{nSJ@NwbLh3{ELh@qjFXYAKmDH!?m1HONH?otwn)*9=HF=FK{#jkaP`t_$%c+m4&&iL;1%06E87`RM*)GUX+{_a_sROC4$pgtFsO`w@_?(YmD4tG@AWtVxqs}5vBZpE)lS9d!s9ngN$mOXO$mPjjZBQSw3dP5%>X|>zP&|gAcoOwAc@lXd^%Qv`c|7$bc|6&o9wS@i(bOa4(d1FoL*!B95!Aip5#$i+E^-KY5Ophg5V@Z%zK!U|P~6KCJ*dm5>&eT=7pd3DO5cz#l7F_vw<$mKx8i3Wy<>yMQk5Ue--^@wKr@gtuzg9-P@IEWm7If|lUj|Olbn%Snw*jRw+)(>tU~b(s%l?uFcfd5Mv*s@`%;IH`;yBr6j!8%lPi+zQD>3sk^QOj$o}M})CJ_G<N)eIasasnbuqaG`8(=L@^|D`R42I=xh-`yxh=UJbq%>4xjl6ixjngqExv8)z);-U6D_HWsLRQV$oHv_$@j^5e4wh$%EPv+895KRZi2R~E<<rkPt>OdQG1eu$U~_E$wSFu)Dh$nY}djViYHU2ktdS}P(#TB$StUy$SufasO8CJ$e(Ob)vkSFC_YR*PCiT?NgYETNv_IJT!T7^T!UPTI+0w9T!%WIT!&nnYLRP`Yf?v(Ym%!|N0F<Ot5HXgtC1^FL&%lLzSKcvUvfEWKXN&8X=*QWX>v(he4AL3p}4pwzM(p(J;)An1a%oXf_#8_k*xG*@&WQC>ND~s@>N@W8+w(Y_=G1mP|s8Ekk6B!P-DqY$Vu7$s<t&L+t?iBq~v7OoaAKWziiNqWEF}ZQB`~Th@to#^#=JI`3LG|@(<*m)V}1N<Py{}<Pzjx4TR!n)QV&kil0;KkyR-Ejp|QUq4*DKQ?d%hFR1}!6^dU`TaZ;Kenb6^tU~cyYAdn|#qX$X$to1Tr?w-jQ2deFo~%OgCu#?>3dMg>Ta#5N{$j+p#fnuZ{zpv?Q=3zj-<+X%K6Md!KKUl~KKUj&vkz3Y(V5v+*Cl5rSEsflS0~p<(012gC@$oQk2Yu#{;p3hLT*3}A~zuSpbjPXAP=U7k;B-I4`wLtMIAuyMQ%)OL2gXWPc1{vPyW*eRqgnn48{AYhspcNgQ+9QgUJ=BRml~|IT?y`P-~ELkh4*1k+YGrQtObjk~33llQWYuQfrbkk~2`NlQWRhQ>&5FlhaZwk<*gXP<_d1$f>F2$f?OGsiny&$tkEM$tlRmsm003$;oW-eLymX;-sEPLM=-DhFp}~nd%^SCQqhDkSCM3P!EumULtQH@1b5L?;-D|o*?fgud~JX8S5B|r+K1>=eZv3i6DmJQPdyEqsS|%hsZ0*2dTf150W2KKa(GmW2yOU;8?QV2K|<7CpV&YCpRJoQKylE$kVAC$kWLisprWX$rq?k$QQ`JQdPhBD>WHeh2pzZ)fe7nD85X6M7~VkPCZB7PM%HufjpbsmD-csm0XNkf?SOJy8%`G;_nQ_cNvOrQJ;}-k*`soldq94Qhy^~Bp;>zK|V^}M}0}&M~<StB1e&TQQwevk#|zxl6R7~Q{R!dlebdeledyLQ9qJ5kvC93kvEVxQvV`vByXmEA#Wycqy9tQM&4n>_oF-bTk&p>>@}b^{#L$?p|}aPIk^dWE_FV6F8L?wP4Z9V)ILzvzouqCTb-PmoSRyMoSU4LT8NyL{N5Jd?<!X6BEKgerA{CpC6A-lC66PU)J$ZPoX!)+45*8miL65Lc>|$13;(??ISaW8bpp8xIh5)mhmsFcKavlUUsKiC;x&IO&d%{h19En<N$o*4$*rh^$%8qDXvI)mliHYElbnf~pPY&OhYhO65PvWf@1X7{?;sDP4kiyIm!(!9mnG+-<|OAL|70K(U!vw9t56(6%|=$C_zX2GS%u<L)XZcRiceBAl2s@^LCru`q4+d4Jz0g~Xlh!r3dLusX~-%RU!bNYt5AHInv$$S@fB(cvI@o5smaMI6yKyKBdbt+o0^oYLh&6Ve*B?Wh2oz*df$L1=5OUEW+*O9ElMs-?nv!S?nv%WolNdeUP|3UR=S70l)RR@o4l61gu0Hrgd9elMpoLL97YbLeoGD{*Qe$q*C*$tsxe1i{#N|A0sV#iH~9(m5cvuDF!cxWVe)F~X!2^ZMeRYh$iaqMR}Sq=?LqEL?nDhDcOrLXDDFueMea!+LtRN8Lv~URlAYuO)W_rl<VVz4@+0yGsv4ht;BUqGZO}&K{N#qzAaX-;H|lh9H}X{KM)FkhkJJm~AIWE^zmk>SC7&Vhq+TZPBu7%WlOxGPsk6yL$(^WO$(_hWsKv-d$S(}28i&1LD85I%OTI^5&rlpmy+w{BFQ;B3FDEaiUL-Fj&!HYA&moVc?jw&SkEBMCN0NtAcaevahf;Tvhmwa-x08pE2T`|@2ayL*H<1UB`%*WM`;vQ6H<Ejids8=)dz1T6w~_mh2U2&C2a*R<casN`hZ*r>xM2*%p`I8=Jwn|}K0@}fLDe|VhoQIuwF$Wac?xwdc?$U~^(XRK@&~FK+kK$sCaX}KoL*LPa`G!1RE^;jD?LhnMczjpN8U#sPBqEH$(5<;$d$>dZ1H2eRQ#>@oF`^c!>Px};pFjD7kNB+CiOgdCV2rv@l~oC7hdIW#o2ApD&*|s^3+grdGY}2LGl3dHtK8gHu3|i8W%p`Z^fxNRy4_}$VI8G$gMd3E6Pxuf|`k(f_%#cRpY-~48@zMJII^JeW(M;eaNM#Wyz(;xv9Cxxyd&Ss2U62U?^U~P`r?OiM)^;L5(3tkf&46kf)QUP*0JkkS9@3k|&WTP*0F2kS9`4lP8iVQ=`d~$y2Fk$y3SGs29l7$TO&y$ur3Fs8`7I$n&Y!$@9sJs5i-r$jhj=$;-$qsCURK$ZM!Slh=^f8S!JsbqvKndSVaNO}$TclM~sXYJ8c9p|~KmFu5SP8MPz189A8RpBzk{L0w8#x|TeHJcqi3Jcm4t8b($cNFGM+Lak5kLiVHPCHs-{P}O)b4}UBEYCxZmzmlI)50jsgk5gBZkCWF@E%I9OY-%uhHaWzIA5(@f6o2oDa-PWNiIUU|<dWo~)HLLx<bu?c<bvcp)MVs5<Q&u_<Q(Lz)I{X0<ZRTW<ZR^Z)Kui`<h;~$<h<m<)coYa<Px5!LM=_rPcBU^!%%FerX$<QX{o8mX~`+5Ny#b5KGZ~HAF@GBV#NQa*hWo8wviK4Q<4*tlT*`>lao_ZGmul0(^K=2)01;E6n{f4NB)Lf(-Tdo4XNeG4as$=CCPQje$=95KXMIfL2?apRcan`RdOY24ss=OMQT=ZMRIv+Hgb8gFEu;amt29Gmt28dnOc}!nOvP(f?S<k%ZRUYwHS))d%~Yums*8fmuyl?lTC7MY8i5Eas!6qYE(P98o3lTEx8oA5H$t45IGmshn$O?nQD;ZwwYw4+Q=EnnW%}$naEkF$;nyBIjO11Imrd6>B$AiMX0&SMaab&ii=UdAr~W;rPd^uCD$|J>v}zEGjct0V`>1oF}XSQJ92Y!3u=3E3vyfP_hh9Ga$9mMYG-mQa!YC_a!Ya>YFBb=YDa2Uaz}DEYEN=Ea)0U=a({9d)kzK`uc96xuOjcKJ|gcYKcs#jKP3N2Rr3XZ^0(pwHfTd~0diw%H*#b0_tdH6@5y7SKa$6iS5VK8mF^_3AkU;ml4p{8Q-_j!liN@`k=u|9QHziZkzX57H81d*q4)vy9{B-z3w1qt3wbF+@my*oc`kVbbvbzixgT{gxgWVZbq={ZIgmP*97yg$9ZBv&?m!(*?m%wmi2#3_Pv%7bum9z0{C{fwkm2<|VAcQ9d)r&Wzl`$a_3tLQ0RJSafA%zLKA3z^vlYhw0r(&@$N'

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
