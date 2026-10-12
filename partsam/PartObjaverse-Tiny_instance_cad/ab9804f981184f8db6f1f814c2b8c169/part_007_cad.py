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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ab9804f981184f8db6f1f814c2b8c169/part_007.stl', 'relative_path': 'ab9804f981184f8db6f1f814c2b8c169/part_007.stl', 'source_sha256': 'b76171acd9b683af943fcedcd8904a2f5ef5af97168175a54f6e51a50af68761', 'input_faces': 956, 'input_vertices': 607, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.8003198504447937, -0.5507375001907349, -0.840272068977356], [-0.05780529975891113, 0.8867183923721313, -0.010306835174560547]]}
GEOMETRY_BASE85 = 'c$}r31yqz<6z^xS5xcO*1Qitv3w7+k4s0E}6@!a<jWJP-YX=6S*jL5C799h@Zbd;HvGdxZ*Ldvx|MTR&_1;=<z2{nc{eQFP%>K@I`ke1$+1e*n>YN7rD`Kdf>FJ4q)eQzQ7eh|NAN@v+8PuoW=yJpT#u*J+)i3{&b#coMEn0Ur8vZc+>DIU3=su&|YM9)-`&V=GFuC;~F>1`HUc-Bi7}d9*_#5>aI=WwyfAqj!e*Ka@yL)+7^)OW`<zbp=`hWcAoRkGiwbjp$OJ2Ub*r&Q7GD6h!_agXvRo$=p^wSAZ^UZPazqYI2+M`UQrq4G9{+2C~zCiYaqP8XN;ScjWpn57G`Z$UU{+#Zb&f4w8c~N_z4DdI(v#pM3N2A8KS4ju|NB=GA-|;m{<M&Ag|11CP>R;q`Qa)R@{CKAMo!RZ2ejoVbl&Is}H~1R{z&~lLUE@DURKH=@)eREI`mm|y$DH~z{2pC*X#81wj;VjwQ}~CPcdEZ~i9?#7=Lzb!r+3r%)|NvxpXP3Nkp9Z55RLz);$<zjpqua~o<$tT^1b@IyO-cU7>x2<G)wEpF=PkgH+4b$#aT6<2ID%UA2S&FjP~2EpJV64U+v~1@!NeGU(@TZZ-;VNlpp2bh`*#7nHA|L-N$v){tDOY?)&}}@y)20xt}-d@6&#Ue^<g7jeq;`4UOL_QvK$P74>?CR`pQ+CyuD!8aiJ6)}Ix%d`w-ZtKZUlDg6C%>V4VzPeb~BFHfO<H(u2H-#if4ty<)yUiYZ`RZW+w7yOrgp4M_stf=>A8c-kpqEB&Oe>n8MY@_PIzv9^@jo+!}Ce6nIZ}=<kk5qqX4b7)Di%I=9YXtHcd0xxS-ZL-Kzo~gf(|;X(TCZF9;}iAYih#e!ZtX|5UDwoa{Z%|l{b!uCUD-yTgulT$)JM+l+CI(pO^A~#6zO}+)qZ22zZCwL8LsQ^w${;du-6EL-?>UC+HKX1dS9piMEu&$(dzf`*7jyHjX`?L!MS?9f5zTYf7MY)f57FMmS=>EmcO<02&Au45B@trTF#cWgW&f%c~#^8c@*vZTQB(irbTFdoqmdTk<9}C@QH{s(@n<*Yk{8dhXi6=Y9FfgWr}E{e)Idr8sEI5J?i~_OXRa*W!%@6O4|NyW9q5jRH@uejWhK+#)m`Rh+p}nUe~buYb4rTImCB9b0uXy?fcx+Z=W-h{cViaiz%i!uIqjFlIADK_cr=X5yan8OygJ&MQFcpWXg#Al>7(z`84{B<|nVS`faJ#XgwO5PD6ZuC&USM!hN;R7K;3Reysk>Z4RpcXj_eE9(P;)=9sg%ujmBrcc#Iokls8|#~;J@9UJuXs2%FJ*O{vIZHO<d^=Lb`5b0059@TgayWzeb%vZm)n+4-|=~#@PC1$JNHZ|fZ`q_fxnr_8p#5s@)?RM7pRq79$h&a8o-_`OtSWEM7?K%SKyX@Yl<@xzQjD8+49O;h--O+lf+gS5sztb1~T*Ebvp_iv#-}Jo~;=G)R_=)ed9a_`TpYO{B^vB9~^>Ypj{FxhQdi%~nTJM(TUE%NVrhfDDLs~zMj$Kf0iO==^4bSRm|FsYAg!HARq5NM3ok0I@g?vT?A)n=^X+N@kFM{+33u(RDOPxhI7cPwSzU`1cuCTT{OQ(G5w?u!|`m%nCLVtXn32}C=i$VKed`IJz%%FbL-HccC`=KFPFQ#H2AL(an=t@mr;3e9_z&Gl*zTAXyFUE%YDtur4=2ijPPYhu-^uDZK_u!w>ANSkeAM<1FD8!j@S?kNNr`TC7w{=^QzGDE&<#1cQ5Bs8}>bE)aIn@95R*?E@2O^Gl!UgqLe5CnzTpzD~dsHv<qoVz_o!VXfabGJNX+8`!GHZHUqmhU+V9{;OkB?`Z`rr3fzvEjV+W*Y!=yyMRAx@v#xUW&phxPZSp74(xhkT}wT9eZ6m^1+Ow|a<{w`p5Dq`w=X^O3=`oTj(!Ym5BUJ9}Q+Td7(1G~GWfkp6a?a819nt>)8SsR`m2jl}q{KCP}dtZhBjZ>hN$`Pm-*x2kiI|K_K&QRgGOZyH>8QoN3XhO}!@568Yg)OxvaOY6xnA*Ysu&GUo$9T}z~zIO?X$L-$2e|7eKw7Y+_{4Jr+)o-<BM!BV5f_37>D-Thwe({?AXkIN(d*x`v8R;H_{?Q`pKmH{pF;C=vrg2QePpRMFS6%06`+{w;`nxIH;oo@z>x9HnA$mWvm#N<#(H;5!{8RI3csw8Zj2V4P`*ojAxR3915y!RkPPD^qm}fiAK%8z_AE@7RM6ky1Gaco&DFpHD`DbW8$4`adobG|<r`s;AH_N#{;eQu}`O(%`=QVR;0Q^&4IkY`ID~@?575vsuuDI@sX4}-C&mZL(kWKS#9l!NtO265bU&npxrb$|^=8|J@UnjF^e(YNYVZM0Y2ma-O+Mbfv8@7zS)Nflb0po`EVJ(0As7}bwzp-eqk1W_1OzMa@&Ch85&Ho(I-`Q>Lk-m3oy{@%f546X3Es)PLzff+Ss)hf@f9;mei-x|-Fu!E+LVNJrg886^E7q-+@~D@rk#Q;eyJJHs^;<4hK>UiqT0Z8elE_cd5Y4A``V*|PY7|7AR<X$c_~kl&+P3F_f6|{fHT}lRSO>n#gnUlxk9sURagX}Le<bMjA4SKaos>ADpKpCjK>Le9eva<^uRn0K9l!63dd&X`{&5v`d^f~-=>EwX@LK)WA;XdXRDn7!I##|=zqyXD_Al$^%UD-ze2(-Bhn>^=^1G_nHy?efep^K+tw-znjXJKIC*Q_(BQNNB#V|cY*N66?TZmsb5ashIQSZ-m`YO_2I*0q^KFj*!0{nN+VSIj-OWT*-D;oYvuQBiT_=0{Ncmn?7pZDs0#WX=a3+z+BWz!*y&(0HdTsKwPi~M}sjW}a-YPs2J@4@}%E`LMoW!_OO2kW%$>bHmY!T5P04faPh*C0;28|X(x{WQIO@^bhehM~S<)@eI8U0HxQZExzj&aiXjZvFn}T%`ZLTicCcTUNB&dV%mis)T$tIJ_sN-!^0t`oj&ElPUd%H+L`}zaOOgaa*&IY$rx7e}ikd*0UpcF#P_bF>Z6bGQaEt|H+KnFRb&Q==ZkIy^()o6#7x~i`ouNPVgJnU($S9kF>!0F0TdUIU!!_)sVxV?Yaljf6Jlsis8^#EgwtUuIe|{orv+O`6eB&EQ31Zx*2Dpe3I9_^qUs6Mt(+2#ymBq6a4vyAddF}ZHI;rEs!5eJME8V+j{-pUbPA0AN9Jf<x^)G&J9{Ng8#t?j-QV)|1LJ8{7>32j&10x<B2(KRa`gYJJiemF52(x*}QPSv1t&;G;p?R@A62$@-N(1>JvNAZ_8pF$l4g|;Ra82zie4m8rNOw!}6(iIHlj7ry=5;^}_zwsVM7ll<wc`U3O|awe-k`_?(xmi`!uT5|;)2rCuK7ztA&`OU^Fr*QZgAsn=p3wD~#8Z+uC#|KN>hQ~GVs3ZdV*ywv_;EpZ?Do|yL{+F_|(>i50}zx`~y)=TH>nlDF>yNF*d{Ui0qjMsRU!FSYeZR&>Kah$h4y99q`Kdc|h1*3g^yohuIQz1^(HQHV*xzDTLeEHi$O<#YHj$7siQOJMy<7iigVOsvylSdJM;drbYdgavd)tv4C@_BeW=7S9xwyM9-K3q5Y3gSP^qT`3nyodSji1Vl`9@<YWd$%A?^aG5ahWgr%trgb7f9hY2lT;q)N9|W3|A#y2yka<7U*p(UEJgg0&9r|SipHWGt}Q^Erss7(V;<2-+l!;@Y}{9xbsFDVE=1d%ZT1xSXH`Wz37fC|+Fr;X<<s{Y#<xbUh(B{E^7FPa%0K!1?OcDvxmyVRWk1&A_IbXD)8qu&TY(en)W4xU^51&vIE`~5;Y3Qm_2^a2r@6r@%s+Y1AMAd^;16q$^+OIXr1!O8-`)3+u5az7E91J8YhgUk`fjzR%WuMUZ*IrB_I0@4m!+69{5?0{)BMC)a9<76so#=j73R&?>Gi&BK}Mu+<%#ml?uT}9`a8;z<Dt3C8mwnKzg53|)O`GI?MSSr0$-`$*7*qM5ld7`zxnA{jc?iGh2Nil0{?~(#L0O~`>XlQL-+^AJl67glc@d3yc_+@lzAljseN8>O1~k;G`(L-=PekgqA~v`4TOkq?S*;p^F>^L;V;CW>5Fz%>>T`w!;n7f=Hn^-))tYP-tOXp_2igSNMFc`^oi5frSzMw=Z8P$z(W1payQ}}dU-<YC3AM2->re$;dk7_xa9c;>pgd@v(4{Zo@hQx#A`n?k6nT5Zrp<W_wAzX!XCU-{gxMFFb+3)y<GL>e5CJs9_!2x;n>f9o`>sZeG{kkp7}lcg%kXi^!3ml%cep7x1EXl9bQM<tND-R7+2O$MmfI<)B86xaK*kkasuL<7=`acYG7V&ITH7ky#Jcy&~eqVZy?guJEQkyC_WnPv`%-XACLRpego$oXWJlsq5BD%e%>MUXaD-}_uhtasdc9%n!Xj*$JWg+b$w{?3dT4bQX1)}o1bd@gzDPA&5w%1@AnnID_8zZO24^ZCrxiH6r%0NydXEykF1Aw;t_;?y($;{vvMK+v^?5=?0a&cokV0pzuwh)k$%3J71#U66ZP^i2>sVT72<SlbU^*R%iz4L#}92c_6{TTx|TT`P*1tupgqO*!F309()E$U{kHneMdHz}UQ|c>8Fm%>!r{GeE`Jm4#kzSe;><FjUNXn(_+YLuMg5Kos855V@L9B%p~%m(K>RMS4aT$YUEmMhqSv(=LbV<p<__w&jgP>&Sb!7Gb2_#|KEL^B{te;W|D9_J^@~UQsraw%(@nL^$p4gR^sD17kpI@DkpAxh&-A)$>S+C12DrgLZ+@)CKbe5^x6&h@1=nhNvpEjylz@M=J(^pWSAX*PzvXMB`t5x>Ydf@N>5TnS*3<A09;Wwe_}CKt#_c59^{K`fABr{7^@*vr9ph`$0q}EwXOG_l|H+NW&zl2UkEYWhh@U)Or9XyoI72YfyL>{ue@?{ty*&v2Y@ug0Kb&W+w`U<gzU$C$Ulqpli;V$@Kd%?!kN4MotF_T!tjB9`+>L3zRLfyZf5e$?(CgZoV!vx%-y7E*yzL6>U*|#7l^*clkHWcMSG&&Fj(Q!`ZwhLT>xLK5^9g(Bc1R!i1=k%{8_(m0d81ywmPPupE%kiS+O`z@r#or+I*wGq_^`Yf;_U1HT(7$$2m1TYBFMkXK9t)sUyP&9`QYEU2<abO!hB(JMf|B{(4L16)P7;x<^q4a!B|(+t%vb^!B@R+bM_FeN5hPzSl{|TQGfEejn(T7o)bNb!}{ZA6}_(Y+j?zpcE=v1ue%HWzNc`$w`4xn7p`M4F3on*@^)+vK>E9-k&go2M^gH&9`DgFJVLacILdZJK9>*1ImYm<*dNWTf&8TNf1&OF<R+BEUN895pVQ|`*4(?%k7|`coO>;hzRX#jw;jhn;rycP9$Yuj3FG;TIQV1o=|0L(+ci3+-)zXJajb`HVO%%HBE6Fr$A<)6-#W_O#yGb%9PQ*|JoZ`Lt|R^6<r>FqKZ5<@lPGAzNYw9#&#0I8GvV*<`cki3x`*Dcwb@|AS@lfg7%Gp(I)7|`oL|;2fOD{kKQ#ZAzxtxT9>|1q>|4cgo^YcF;uMS4>)Jz0<NPmgXT(`D2<;@eFV?^H%}76JpRSt?j|$_taJKUBKdg#;cAk#*u+s%`&K5wsGE~BTKkZwrBYN*Zz2rNOb$;bnn9p5rq1-+-)qZ2`{S52(o1vQC@+ckp_2vZi+n3M8er)Iqj2n$_B2Lr>&5yledYmtXUPPR8KlS;bHS}_HO20j5GRptzLT$H})uHf@@<2IUu;6?sOEB_3bSUDtN{e>oy-fX<X$d?B!}+<n=rrUf$61t5zxpVjLc<X!-36R81RmA-#Jr_9;xxL3I5#}Bzu5n1gL*5)^}>pUy1uerYl`@r2cSHUY(aY-?T!1La1iO|f53V2x@x#?YzxhgdHGMwH{U(sZ&@DY(8`W=c-DOCw?(f;oRSlDy=2?v0)M~p@OQhS`)1R?A2`<tcE|mu?~U_V*VF1ZS2&30xS##7{^))T=QWKRVc*B+7lt{9;qN#Z&nw5fVcy@jPW`q$4={gLERT8Q{w$;qd4~G(|DpQ}OQsp{$0y)^eePnuHw{<6Juv{~&*wgdQm#nf;Sl!QuSVm!_LP6o|0-_8bExG0HSr1N=edK|X`E{oP4DP^9qC)W#k}lZ9`}_a82<hdSTFEA%278r;<TRe2=_Y>@h3mQd3^&b(jSY_^@U~GBkZ@gEJpkvQF!jtd5QY%ecX|r=Yh6;bKyU-9_zn<E@1p^I~Z}IUgJ5%klI>qW*;;BM{?=&DeL{FcpqS7cK8cdMm{qJVx0UKhk0yQE#xO#Ba~<L+uX0Z<J>uQ0o4D*t9Y)s?jgnxJ|D5n+o*o4+g@GoS)*LAj}FR;^i5;2Pn^?6@7KQUGWKIljxACDST`N7Y?XFk-!}D$o*Ub}nqs}zeF>g}mG6%Dc^V=9oCWa5T*7*(VLkPm>rX-aMp)0;yUf(_!TKyc((jmvcKa+I^IOR~DBoR2F%R~BfpO-@T==*BK)FS_X#Pz>f5Lz4Ph9sFp7)y1Td>bdH3##Q<pt{ZT}Aj0E<k(k(gpQexIEUce9ytQ#ew%rD!IacY8&3)h<>X1w_SI}d2xw3`ux|hJ4n-8U!+I+=;9jRQ00SucKmp!^PaWjdyIQ|oH1UswZs1+0Q2Chc+A&_18_d%6NdS2;VrE5bNOK%(Jola!O&+i`q#hR;Li|?b<2^a`o59Fw*%soD~R&B^9kj7)(7+OcwhAQqX{U_6*Z8)W`5*z%rLaqDz3<9%t6fKj^da%^QA%h)wNz}oLRYa{baE{!h0TH{V|TM`-yR((@pi8FIC6<dnp^<^O<@S`>4vf7pQ;kcJ<qi&xOC`L%f$YdMD<)TS4$gmO#02+_RS(j_Zy-fpK`jcGOqHp}6ixALRevqMC18x50?BHUZDgFYeKDGe7BpIL|j>z6)!ne$$U`@E@9r_pXf9P%mp*A<mzj@jNsk7VY6{V|<@?E#{Xr7)Q*fiy(c0aO}(YoX8wo80jaPQSbhp&=21ignwCW+!yz8);H;KU#T;qowqN8estp#pGStHelJ;Y4(9q6{=(6y7iS07c~>0jHxGM-dMWb(^)>Q3{9U@}y2#vdfR=;x;aNQQ+jt-Alki#?cfLg-e%+DUK22L~cn_@Y--y#=tF}*5krU5T`mM(wV;vRO4{<$*BmJ+Q+OBM_J8_-4{gHl}r(N?Iz8Lras~fIsiP1Rbxbf%@-er+K^FFNePw{=U!KIM?brIZe@o?13$AY+S=iw;lE7|a#(j8~SS$Q4tAM!a*!`s+rc-+<Z4=i)4;eHQX#QQ$M7xA9PqN*>{f9bsX%@?Yp{D0wG-(2@3uH$|W^_Y4$&rOfPzhDsBLx;Plm+*tQF85P*QxNi#5RUX~Yh!$V&{XT)I%F%-&vw=4R)*t+P>)kL!(YCLwsX7hX0(5o)yV%38^&RtYuUHYNBmdK(XJxBFs}u*!F~A+Mfqg<f_hxn3jV#DaUR}2JL>(i58@9mjOTfU{V{Gn!90^R?x4N-K1F^4z2UF$PRq^Yg!PX(Qvu}vn+5gtITObB#s6ZS`7#pYVYaeb{${6pcuxFeHpcG*Irx5G6!!O3k0I{kLzq|G!;n7ugT9w&een?cfMHv)A1*l^^K*LEcd~!mQM9X5t+7tn6N>$u3&sQMrsHU5U)CU>*NS6&j`Bi%IS1mpA3o#UVDw7df7(&-FW!&-aPcwLL(iJRKX;x@)U>ZB#-Cq};V<s4>oLRj#mMjD%JA2;W84eafcBZa0?MId80Ogm<<Sna6hJ;t_QUzfo<X?Jd(McH_Au5t-`=2IeN2xym-66wT)?*{DgB0HZu)+mAvO!fjiPDbUw(VH#(C8RajK`neq#Gr+$YbSte1XjzU<kYG5%+d#d|m5FE69M`l6j=F7HU`w}zF}@x)Qd7tiNb#=t*eEYd|>!#sC40{2}a9_5gI81mz_AJ=_-0oN@%4eR_xJK=Bn5Bf#9aE$MBrX!B~Z0sw?w9;}mOz_0}hJXKsa(q-A^KprbSf}4<igxQa9_in1QorfOD&(_9MU=;3E9QZlYq1ac!vp*IA&s$4+*1hcq>uyc?o1u^JBGMp{qc1y%5y{<_Gj7rF&}Z?YQ4P}{xKWY>+gcbK1=Dh_aBD#S;8OV>H1-O&uc%{KV@Ix96GuV;<P=6_BQn)?(3gyi1Vy8_Mctd@P2B+%t#;Ri}$;BIwSqKw0IwFZ!g^MvX|(;o1E}`?8AA?vmslset-59?c(myU3%Rm0jS53aqw6ErSFwlXIrt~n-K~Bg>zU}cNmHBWyMac>sMJ&o<DoV{Kp@c8Ry$2mLY!E9`ILPgL<zwN%L<#;EQ?qeiNKCB_^W$OIE{m7u~@5Rn`Dpcd94GgRlV@AL8RtFX1Qf9{Ly$w8PwU(LWO+urBFY3j4m%f8n}W53AqdnG@q%LL$yb3XH=(qlXL5)Bm#Kz8voGFUzR!FPXjLP(H1k5x+<c=*5~C4;wo$KddsLedhPaIFq;u>ygi?^!cJaekRt{B}3ug<c4+Ty-_&-%hL+$Aj1c~AB^?1A;BH#%f8n3ZOdB@*U4G}={e5WDwy#ec2q8;FMd+no8#jhw4cdoG5^<VsMob*zJvFH-aN(rV17wl?`CU^0|9Y(?$PTw)?xR)p<jR7g#GB*5_n!Pt}p7nR}ZYC2VX<`eBT`99N~-j$?uQ-aSHwMN*$bAtlz5b#J16b`tqoT^gi2gj?VX-4YNG4&b{&g<A(o6yifTh8}f7L0`}!02`JB0SFs<u<cxLK?U5*lrapLoIdL`4>$6~;ZFN12zXMp8h;!B!BQY;OTnzuo@!G#^<?-ChuyYvvo^e=L5Aa5L`uO1exR1}VKfl=+{ra#6o-6KZ&gTsC(5{}j!=LFi-h&OAhkWKPfjARN;@sLJ53V~SE&MBS9%tQH2l;pW#B;KNCcHm)?^0|^zuB{()|ctsKWK;LLiyg!cf3d5;5gp9I%h?k&6!XR$J%0ijvs`5?6PfmKP^Kl<g-R^#3}g(?|WZK2mgFe__wA;c|UoG{&mzt{mJ9Mb;&%uN4qYs`fasO;M{a;d$hNGPU?3A4ZwKuc|H1F><ygXC7*kj&W-k8;4s!zEy8qNWJ@fM_}?a|-xg)ka&heZjPdzuE<8U7zJzfp_7K*Y)i2`wwOwbeUsKyjct2yyPMjOnPmA{7p)Ja@Vkn+N#>Z<pSW68-znHh`bjto{Z<GV&6FyA+=7THo9Hmwr<bP$C(`YxdF`w;Si1Vs?Urwd$FOFGb@pm<$)3MGNJ4MUEbcpZemuRJaOJXIgM;?qse`)6fzjr6}^O|eWzryOP-@foL@;~}8=DWB$xNfs9T>tYu-6fvzyLZBKhAAg7FK4-WGG)7R?B9oe(R42SJNBa-E{;O}H%`ZURjZ!sdc$6MDf-Lq`Y4wQ<xt-*`#@_{!+Fz>eaKJqC8)<`p76UYLc3dX9Q`Z83Gban+q7OChw;9MH82kEA3P03dww2?dUW25zyCP+0PV1E4DPRoKhn>*g69&Gx1&9G^g(*QUtyk-2jw}VF`id9Yl!xlZaUiGom_a&;+_fh5?>wXch_FxeDFjF)(MyQJWJ`fZhMOTQP>=m=WQ$e6Hnkg#B~SOnW-n@y|#cTth0{v#C3nP#e35^Ju&X(K9BKjM_$BPy9D!fwHGM=6HfTMmKM3t4wL6Kdk6g8z|)b)XYZ>>Kj=OFKIZ9K)O*K)$Y<pXc<+AqdYt2aKY)2=|1z9M=IVlZ!Z$U>n{$)#9JKLU%=`T&;C<^OW$?cEk}P;W;L-HffBeT=WButd6#aDVG`y$tHUQ=GF&OQ?!x;5jGyQ>mR{T5kmo6EQzM7Nf({!pQ=8?GCdX8@1Qw!y@<l^I$e*5N$$mcE}+^_cqeP7J*wTNEVGPWP`Kid!QQ~N)~^MM@BDAxgN^?g9ou1h%QIQSIp%GMe03HEQV_i1Zg8}V<xz<a)YPtRVF@4<XOs(#y%URdA$`x)*3h8^#R{y2m3KlmNv+e$yYcUJT++QIa?xbErOyHoZ%^O~Z#?*3`&H@C}$-yh4y^YM0J`uqG{(Er=>{kUZf!q8rt<NVd?!E@&o`u?5y!zg@Syfo%`>;L?f=Hl-^kG3vrFo<O^<TUi}mEun{#VP-i^?&~-nu99;U;T+@^(tQfzki}R!)P#!PqI-o;nvjNWYO~E)?^daKo)&#0Gr6^sTav&!guJ~ME*)WPTfQn{evuOB_Ag*pa~DA_8^P4AP**Yq}C&MBzL0;x2IMmi<Tsd)+djo4xrX2i`FC$Aa|z;Td0-EgQzvAmB}^8`KWoxqR!-e<P6kQ<P7BGf5KU5!Z~Qdd8paQqPfX=$R?U_DQaPIDRLcZ1+r)davgGC>S*#j>U!#Evgk>&=q>Vk@)>GLBlrwCH%-`=+Mg^shU`loPMt&^P994Wwo>Pi=TX;E=a5AYkk^vWQZJK5ACb?JZ&5#yML&~okz=VJ$+6@s)F<RC<a5+G@;UNRn(%h&3G#Mw2z3`ZguI5jle~t!fx3?@8b#hf-b)j{O?^cc&FTccP5x<w372q!dXY<z&D7>((Kci=xf!)Bxf!_ywKZ9^CAluO0ktJrv=Ldf4!JtD615Ilv^-hVjVxM#T#4*X6V6G^L>B#G1m`3>Il+XV8KL*dm#8PH_sODH$tTH&lI$S$2K6dg^aWY;HCglr`3CthO*p#~w3HKAOt>ty9$B;lxh%PHl2xO&qIMvQb|H)Ul0|EfTaimASvqPCY7MezQ*sV+ahh-iYCE!MM{)&nO`32+YA3R2S8_wL4^6lUwHsNq2e}EkK26x0+MO)gne0ujLTyj3LM}(GO)f_^(S-js!h{RbSCw3l{M87}LlzUhNd0C6i@qUWBu7%OlOxGXsDG1}kjGJHkjIe+QAd#nk*iZ%lSNHr(ez|dSzA;${$6ub=Xb&`)Z=6^;j8p5Ajea8P#2Iz2a|V@XVQd+P&<-EyOD>Gr%>CIlh+x-ho~Xckz~;U<Ph>Qn(#_$ck)W|YN~}SI*7cQypblnize(xtwHu9o2mK8W^#U-aAs--vZ#TanQWwHB^$|^lB{@=l}IwrBpa7x(MdL$CVZOuntYo4G|6%$1u`aC8mjoxP+yZX^7{|`EdCGtKAQZ2e1STSe1ZIDk~N|FP{)zSF|R%};pQ~qhScfghUCUH;W<fmnHoi%PM*%+M^R6cPqPf7Xu>b4QWh`ySvVETCl@&tIS);^Y?4)@)}RTOq2?l&Ay=dcyHeATUCD)wzw4kdP1u7boRundkd>c>f6#=lQ!kJ&unw-%gr}vbr)f0drfgfSlB_JXDY-1!gW81Lgmvjb6D~&+u1IZ8u1NNxHY7J>9edG)tJ8$5QQMKLk(*I_k{eO`(}ercg#D>K$)~8BsXfV?$;+wj$nBVq<<vRk<aW87CVV%^zEj^*FOx5`ExxC|B#TO$d(Y3p&TNNy$j;<~)UxD)<VrMQbBgvV+>~06T8&(fT%THlT%TNvT83PPZMqgs*o*2)c4a&EqI!_M$TexgjcLM_X~OxaS;?Z(*7NbRaBAvxvY2ozO*n`;jXaI*IEdPc97JwI^(40;SD}_5S0TGmUC5%D$f8-vZsgK5;Y!pTWYIk2N@Q=Ea09A|+<@#$EkzcsLl*5zPTqg|(uBt+*;?ve>O8XOda~#lvZ(Ai_wuuFIwRDVoQ~XpCOnuroGdz)JeWM1Y9)^*|49>`V*I@?6`oC9Mx94qM&3bPOBOv#7QIE@K|V|qK0=Kpi(VlgA&1k1!>H%TqDRSL<gL{0<gMft)DZFt@&f7_@&fW-G~q?m4P?>1<VECA>TPl;*-jIFO8rR|mHp>aeiqK=1T~Yhkv(a`wW!U=qAkeDd(K)k;mXto<m7#(a7k(zYIU+`C9<eHSu`iP3^_kdI0My*EGqlP4E!woo+f<H_<Nsuk0yMaCcKAwlDvn!g(e(KJw#64iw4t#SJQ+qP;Zb$ACsR`jZV<VWKr3F3X7H{8_9)e!WF5F$;o@siZtP3G~ry-R%FrA<mCNlE}C$n5hm=Q<{*m+zcs>yzf+5oMJtfSgq>-^S*SJ1q7BJe$oXi(g{eMd(I(`=<lHpj%+&g1QEzf)a(bF@8fq1?XgP8ka%!6JFC)}M7L|SJFPd;XP52m9_Nd3GU+EVUUP`@47L6o}E+LDKBQGWUQwNd#$pfg>$pgsVR2Q;0IVV;2iaCwH_mILx`28n-7XK%j@D=I~vgl0m74jCE@IvYkvgj1@Lh^aT@BQR?n(#fE@Fi*pS#%ls68Qv8_!xC1`51XWbv0RZBY8i08+8|X8#$CFye7#alk8QJ9Zs^HNwz!5UeJV}P!E%zkRMWCkqa521*osc`Hj#o{4D-2{63N_dXxNx{D>xegC-o2WD}EYagxoZ+Q_rX>!=ar2>x~*HIf|3dss&k{);9&gSwkMgFJz{lN>+|r|u+&liyHZkV_e%ZqyfKG2x=rC*&tA<D$mjWnGje+>u&<+>zX#CfwZkyFQxJgzM0R-KkOs?))t5M14dS6aGfu4e~egJDRYa8bOX=-Poy%$#(KSn($WYQu0>v-_#Xk(KY11$zjx8<S=p|)sGxVZc8<jMe~!}l8aI^lZ%qG(}bO<MzUxovZxE$iJYEVf-G8`oSs~a>PZ$YOBVGY7b6#;2^XT4BNrkUpjIS{dXWo|3(|zkQ>&B9lWS3{kwu%4llRQRWvH#GjmWLZqp1DKiAlCy%EJf~PM~iTIe~nXCcKK;pDfysyo$Vp>Q7!m-a`|9Zuq^27tU*h{^aLV<e%in)Xikk<z&&j<m7$(W14UVS%(;**{R~sPJK@nb!HmTg5>OEPiiHyC%G=wOs-3AK@;w3{Jn?oN)zr!6YfA0Zbhv}7OhWiMQ%qE?nx8&q1Gb%kUP_a8&SQ;jmT}NHOXzr-KdSpeW`7!jme^w$!*ECsrksY$>nImnW(ABqO$+b#LvPH4A3C*1M(tj8}cG@XKEF4XL4<-8(Fk8xi+~awGz1{xf4ye7uB2Gi#(j#fGp}u79CGc-nS2@3C~Tk`_#|WwPew~WKr3lf2KAdiwReyZ!ozkxfe}%D0MVh^iT3oasYJ-Ie<KYCOp~rdk-%>l{%j~n>?Sqj=GF2x`Qlwm@ImPypFt{CTydIlSRYGHu7?s@M7v#vgiu(Vsa2oIFP!497vu<{fjKRh&+uvizd8~8cG(mlNXY=QJ<2xkz;7Wshps)R~HubB&Q-5rPd-BC3{dSlau%49yH-1G+|e28M0`8vS<dfD>*Gq_?;0dd+&EN;k(p(<h$eu>T&XB>PG5uvgjW2M)FFU@LcK^vS=`QE_pglcqVl<c_w)`^#XY}`I_<fzWo|aIHMC(_UFQ)g~*~6$r;IcX~HhlVq_Pxfto9MF++Y}gvy@$0ZsTk)j>W_-b54LPZK^(eM=VoPCiY(LlaJ*%Dz2;pM_sivyjDvKTz|L#f1N%7A6<wUR_vB_@NOde3P1)oSA!dVKLz|Mwsv^Y8tYba5ObFIW_m|!lLoyX!0uRF|z1V@+$H~n(#=fKY1j1AawwFAh`+En=G1>+=SfH_<O(Ik|tb*CY*yRd+!|7D`YX@e`&&T)GcJug=Eq5<T&z2>OJyDa#|xy_!oVb$iK+XXu>hn6XY23S?V#e=zj89@<E#L2I@BQ268Yplq|Z2988{16P`s~L7qjPN?l48T}&38NFG5QMx96=Mjk_*O%`287X6DXI)glhJd`?tJd`|;CfwWbdvDyECft=KJeDSWfErE~eM3G#{)Z-9%=mjRE!>IPgIbC#>PGHC?oKUA?oRGP?MUuI9zhcxmSlfWhfq6`Mcb1_o0Er-`%vqU`;eQ_gey?p$)Zl=3gpaG*>7j&XW=Z=cVsbP2Yq(3gM6F1k1V>Ce4BiZCVYhYH(4}{EE-4_ZA(5v?n4uHrxqoPW+%Iob5WhhxyY%h>B*_dX=uV}sl~`?$?2#?$mz%#sfEa*1;`o6S!lvJsRhY7$*$D$WYJpW<UO!(U1}F<8FCl$Bx-B2=qR%2cCu(9c@p_rl4UbO8&VU=V#0n@*;o6~ge^4T(p1@F3%B+$I^|6DfBG+Te*cqaW`_U#2Ri@jFaP@*cgkOGN{aPAU+Qk{lSb+-sj{8)Wt<A~wvFL`09$%xB>'

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
