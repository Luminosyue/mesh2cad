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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_003.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_003.stl', 'source_sha256': '6de03112de7d82190b6e7514d7dd8e4b26623c60adba1899789af99f3c0da7e9', 'input_faces': 916, 'input_vertices': 571, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13871079683303833, -0.1616302728652954, -0.3405901789665222], [0.16551154851913452, -0.053964488208293915, 0.0764872133731842]]}
GEOMETRY_BASE85 = 'c$}r32ecH$x`mrVk{}rr6c__Zkem$+h@hebNdgLk1WAGfksvTckqm+e2n+}k4jIG)2sDy&RuscrQNf(O#_OA!`l?UYKYiDF>pj-0wZGa`r>3WNb#<Rov}Lob*@`&&&n?dOrez+wuD0W-lGiEX4DB&!Nbhbv23PL?%<wEufuyhg7=5XE+ecb<$l?rjMwaW|V{o@Y<?4sZ-QBZpxk{mOJqHXLGN^0+E&~R2@1guAUHc90k?;ri>iSHNM7?~iI@KzLYE-Bc8Ws9K{>h!VglLm}`x>Zgd1TXpy{g`2z?!{2Kk`|Jq#qCcw#n~@@uQ=@jrsl98(sFRdidO_ZPqyW(c0tYSpL25?^E^AzW3hr`yqViyAH$se)RZ<dz1ChsU3db!FMWcYTv-$zvJRv$??A*vD4o_-a-4$pBc|s{l9oTc^$48KYmU7PRJfVa$@q<WIu8J4!-lVef{o-qmuLJ%K5<$*R|)z`K!=+Rgc_a&%gVp_M@Zi`42y_BVE;F5ppbeIXGYZlzj11^2JZd*Nh|cHNMOjKP6xMlzh$g%Y03LnJ<1yzNWv-*Yub9n(LSOn(LAI;-}<m#*z7&ab&(`9GS1lMda%|JLT=5e2p*jHNMQ(_%dH_9Fec*i+qhQ^EJNA*Smg^uh(DXYkZln*I(r8^%wbi*Dvz*u1Dl+e3`E|j>y*=N95~`Bl7ifk@s)<vcP<epK|}=r`*5zZmeqHIN@z20{wV;Jej-WuC>N@jsMh)Wqv=F>qOFbn=G>WNAbheSKIyNeqz3t+)waBQ+|6pIiL0FS^XXS@PbQot?zZ{YSMT6m$v$c@S_JB%(FgM?pLP2+^@{%4w{+t<Gu4({oR4ucQ%$DZ_UHBaeDmbSGQZAiyxgCo?!Kt`=R+<xgVO(?K4aFUw=8nng@L6;h|4jpF44U(hv3CV)c(t(7yA@lBcZek^8Oi!}CY(2=d)ME$r*ZcV;bX5a>Gt%KN`p%6@Lf-@hX{?_qKMA$;d^`}#v4txNhbF+c8y+IL#o^ON$tFxMlW7sjtrH@VItBHt)}bhe#uynCsnAMRtXpD2EGv%P*&o=0Zh<nze%f9vVZ$?*r+>)*k54vF<2doby{^8PaZLi_$odES|E<nzvauSWN8O!`gj{UMAWs$uUB&W;~9B<phj$<V&j%ie#&^K<L|V*iYOwq<>gpYr@Q<ICr-8DH$r;V<^-eXK^BwSOAlIlnErkHt?+-4x_IWe+d2{M*kb_oZ0=tlRv4{5I`J=j@ti^?zbWa^G+lyW9P~`?&U<!b2xo*O_OCzOVlppW*jI#?QC+X}|B?@4HLwus+w^ry1qj`2FxbNA>+E#*g2veW#E;zB99pevU4&uRk^ezo>ovac90>w*~C^i5h>dJwM_5S0&d~<fNE?e5ah4|NR54^%LF{I*|0Q40Dq?cCr2FuTKX0;ZE(7eyH>Ab%Fkrvaeg??`V|tBYl=w{o@(h54R25{qO%KnOA(x){R#G#@Y`Tt@xVtxx0@ieYZ%|>hIu3(>q)Jqht2&NshlT=Vogh{MeM!F{}T!m3#F4a%Gd>kKns+->}RYr|EM^-x2d1y4Eq!4_9ohKes~F^dLX{@`hE`I45c+{m7<JdXOI~u*d4}IA8BhUjN3!_Wb|zRnm6~-eApt_~?bC@9tW?F3_)Zm(|}L`(V<Kr03lb<VTB~TVajUp|S3t_oy}h4t}ipf+g1Xx~{(NfA2@@t^WAowb@r%-)nH4q#r-L)EeK#k9NIxsg-Z*=v&EoOS^1ce;D7{lhwZdw4q7gy>I!3AV2*4-FAQWllV<}w*>l);+q5g`nPQi@*}N3vpzRu-b4ER{#uY9+298Hu_1Ra2^^>3^u^XXZ*n;KJ`|VV7eD3u{_@t&p!p2p%lV97$gce(A}@Sb<P{5N)$eCwJw);4dWd}Y+m4|17RHZ@^%kxE1MfrjdXC`7#Cnd5>7{=kdrRCe#=leCFAuaz`mVSiWB6ftKVHkKuSeeR_z`ixM@oK~d_KkHeu5tr`$;tNNzxC=eJRVKK;QjmZqkp5{V;~_>=*mt(NWr8Wbd~j{J7X}BU1+^pQoXs_I@75kBj}>&Dv5wm)F|Qix_@PJTIb+-bg-=UGY4M;K$_i=s#2S`>uH2#s9_^&%4OsA^LeQ=WSdw%Xcr834AVizS!rbZ}xfP%Y8e=XW#b55&Np~<-Y2TBlbP%n|;9Z#eU^|uGp`PFZUU59I?+BU+x3Om-~P>zPL}l@x^`W`QpCI%*(#-yw8>Q(Vq=;?gu~B?+@R1I%oM=-qN{GTO8=SZAw^v^o@qP|Itg9A2I%oAD^}Q-!V}?Pru4}KFAOMveD}A)_x_KW9)JntA7kXlzomp{*l=_$Glao{t^68wHK`Z;f_;x28|!Wm*YozF4+-u{b780{n5++$_Shv<IDNEsZU1G{2M<m=0DQDVTM0P=ko^w^Ywg@uk=m6#+UgTU*_xe7x_xx%#ZiEB46Xne7$i*zTWkSe2p*jHNMQ(8%N~pjU)2)u1DnSjU)2)`ip#}9~bj4^K~1y(EI$JwaMRqBf<}tYLoP1U-v!l_e1!hpPQYv`aj)Kp9hxjdco?CA1T`IjMabP1%3Wj@b-&--@$htD|_1SyF1P%f8U8rUuN|W<2$P=o$~uJlW+YKR{s!wB*!}^{eJY_R{C5<jPKxw#Q32vp4aC#h3xB(UDJL@T)%VQz~uWxM9h!dNc&MaKWl!~`?#2Y2R|(4-@SKPx<B7&_CA668eisXe3`G;U*zlc7x{YqMZU(D`5Is5>y0DwHNMQ(yB?9R@nyc=^@x1EaYVk}=Zbv2aYVk}_Y(Pf-%I4{jU)2)#*z7sAELikuD<&BTys8#A3xVxzyI7Yb*<lb+ZWb;w(049KU`^@{(Z1hr*)Qp?9QYgZS{fe^PUsklY712kBrX0E2w{H@(jICit*#$SJ3Y{;(FX?ztHa|T)%tr+2Hp{<IDF+;d}3s_$lv`(l_suW*qrGiJ$U5X~vQ7lfw7j_lz&!C(Y-|_euPe_enF3e4oTmd7s2jd7m`n%lAn$zI>lFzI>nb@)GZp=5yuy<gX(F^EJMk);!QpIWH2vcV2|=jI5;nF2&M=d^d8$>Ys96Bz<#UWIlJ;F?~MMaDmm|!H>QEkkvmte#Gve?<MbR<HsKErpM_uZ*7ntZvWtFzc2Rz=|@+$w)&@>N15xF=TYYRn^o7}chOO+e+b`wxP;X|bWce4e|=eckna}1$C`h+Ur9f<tCiJ1I%>Oq-z)p<x*$Kkptn8$V&9W~Z2DxozdRokzIR?^=B@u={khAgTm9otYu|0s&gvikvAQ1T{y(kjaq%M~uh{c1_U9D8f0}*$@|;ch(amQ9{qU9w>jV3<|9d%_f9`O{dn<!{_xd-2{W^tL1p4OO4_`iCyz9Y_iSHY4n|oK_eBwvNe7f%+)#r7~?Yv_6GOv{LLvuay{Lp+a@f`Hl3BD`W+wn<y9I>85_|8ImJ<I2*_r364alb_Jl+@#_vhT+*eq7v-(Z6%+{;%5idjwzJ?<wb*W*m8*X|7W|_q}oOV`9H@pL$oHH_H7GKO*+SP=j+xKjpbo%?<RUX9j7%k-eWs@LjQ=r<|9X`IP6S<~mOn(7z9g=TQ{j=_;N_^1Rf0Zi@3#v#y$a7x<i&&tIo>RQGT3jsE9@!jG1{rtimJmIwOIPhrasU;NO#p9lKRq(YV-Iec8-kL|t>^uu$0TJ85kW!}`|{GM%XkRLnzp4H#%SMG!P*9Q5{(hFAq*lm*n$2Yz!#*d607<~Qs^7<o#y9CaU@#Xx)r#~7v|HhZ|AN#$9m1B78IQ#pWd>gOR_mMp3F}^(K5x#fMgP(HFgP(HFWBSW;9^rfEB<6GFIS+oyIgc4fp7WUNk>@=4Dd#-+Dd#+99C^-T#*ybd=6d8gj~Pdv^O*kfoJaU^G5_+MC)#wUzMlL)?+Nl{?q2_9$Mt*ixg~*qEMIYZ9I;NMZ`O(D57O`R;kK6peRt{yXZ^lhSH_p?%In{0rhb3EDbM*JKYnnX-CwLj>6;wAd1$d%zc+5Ea6ZV7&75xam+RK}a@~5LYu4wun&*Rjv!1<q5bIg`Zs+m#^^0|Ge7VlO>u<>WhWNfQeEEIlec^qsxG%i^wdU>!$}5bYl9#xTym7>R<c(A6Vn)z<3*o1%H*w!dKQ7jD{A|aJp!>!6uDD<R+kF}xTg5(ypMK-P<T&CS&-fwyaE|8l8~A*AzUTE9=X=JFmejs;Pl4h7aU%Gk&&sZ_#uw*--uU7?&>O#>_MJAR$NBvTeth4VbZdNZerSAoe&~&}K>Kc^d*}K6Fus%X=S}|c<$0smUz|63eunnlV|f<)efLfJ_rAKtKfXMl^yWvLPkR1g`k!@|TJv^D`_Z*?xBADI=b7I8i1SR(e~13Z?dy+T)V|xxzJ7WB>3uJ8{^^Z#mHv(G`48c{IqdnD=cV3!it|!${D%1L?e!DF56Sf-&R4z973Zs-|GM^_TK4*PS86}>slEQ?d93H(rF}Q6z8|9_s|4Ps#+Ub<@#THz^%wV%*I(R6o-ghT<IDTP^Tj$hzFg<t_Y&*YyH2rgjW5@s*I%qd&ll^;`&_ZEy#8XHc>TpX@vcYY?tNd8yXX7!ZE5{2vVTuqHRqX%j-yI0r-;+DtM9LnDO3G18vIwtde{74{S~r$)oTBL{|Z?+OCridX^8fN8^VpyA#fx3K6Ds-AKVy?!b<P=@kHuMoA`JN^(JsrbPn7UegJ(LegJ+DT>>kOCCYO2HF!C^6kP@@o$uoX)Rn&E<9XCyf~TU>;pY-%aH2emKJDYa)cZ2mhI>)(#atWiL%kn71RVqqfrp_(;bCwT9Suj}iRc7)B0L4122X+KpmX6l@XP2c@XPQLH0H};HS?`>9sC-+3|-@!`<2YA(nav7L>ZGPlhGI8$?#12Eh3Lac+=4rd^stdguVbzg2$p`;IZ&<vK&s%!||U(N5M)5!q35j(Wl_Sa9^|=+!yYJc7c1reb6W2KJXy4Cp-uqiarAmg-4^$!=vE|=y-SnJPn-zPlM;83*ou&E9eUN6*z{j&XTz<){?){_3%1)4Vs=MbA2dXKvBFBO^21Pf|V}v@nY(W;F;)bcqTj<eKAYs8hep!m5zi*lB?kX)CZ8O;U3hVg1ezz;cjpjv@_fVeiDtqPr^OX?r?W<HQb+ie{wZEg8K9Dcyt^*9-e{Df@hJd;a91@O0I@qr@jJSjjr`&-id6LJ^`<X)6vJ_$H~udN9wEK#pq-3Vt6*%4xSCah_-=Wgh!%}!Xx1UXiK;y`5A6by$9SCeHiWvcSawAJHrvQ861JTqmRIkke}fe)ceCD&{l9O@-y6;dTa7i+?LE{!R@KHCo{txsCOVg!<~G2e&guelzs=RqWE$2TUZsv9nr60RTMvlehI6hxE*>8Rz-0e^mAAh#gC$&!m224iGBjBqPRI4hgDJhF!~X!isFaR51h;lKXi0HN<W5GQQQLk7p#inR_GO26~(R5&z#KMT9cJh<+nwz!m224kA4BGqPPS46|9QlPUtsIW}ZjLQt1i!1UVW$O8qD~8a_z<YxqlaFT9r=4ey}7gB%TSqrQzC4R55rksJ-Lp}vM34ZlYHHF7k(l=@O~G`z@{tI}rVtN26O7QsrFz)Q&8@N(+Q$=&d3>Z{4!@CNEv;Lp&l@K&-moIyQ<tPSs>zK5(0AE17KtPLM=GBZC$wn|UJC*Y&#arh{F5IqbZg!iKR;l1z<beAvZH^@-wdUzwe23-lSBtOH;sJ{j;MHj<M;YH{|coDn=eHD(8$8vZD_0{kObRE0_-imI4x563dPB;VJgT4*FO&*31Q9l45L67;edWTGuz7L;-kE8Fx$Kk{1dH68AA3Y7LEVeWEO4H%>@Je(6yb@l9&V!f1i_zKeVt64s9bO2(iq7(7^D4P4hhyk0Sm|6i2CqP0fmgum(6#V7cni82R#}{4?v<W{55dRKcYK*#V(yh*hTn(ZMc;$ph0miG;q&lm^sFx%rRM%ox{b2Smz&bv=q`8{Kf4<}3oG3R?}oRdZ^GN*baWM*4lh9G!wcYf=u7ZCcs4o{o()e&r@_<VS?COS7CaZ71J8wDL0^Vnf!Ct1!)xKq=q6wGN_SEezlCmsmAddw^lggbQ>Y6oJp-SD&!HFKbMQOpCHO^0ubWHoRO(9K^YIkw@4*+*$?!$^EIJ833-3cG!294g(Q)vb@G3M4uY%{Jqv84ROX%~k(wROUL477X4IKtggJ+<_;TiB8bR;|nei<DFzYM>Qj)BLJtKqTK$C97n@zh=T3_1}$17AR2fG@z8&=-A~4j@CNgW<vCXZRWFQ{c&HA9yl63GEI~f+wJz;R*0Kv?DwYj-u`0C_EZ%36F-KM<0Tphex1|;SumKGz<@ehokqw!{L$WgYZar6xsqF1&=}7!eijEXa{&KJRW@l9uH4MyTKFT7tr4D3-F8R0Jw0XluML?Xc@RbqTHS+h0wBazC^i|_FHLFoHtQIw1;R@tp3|zrD!ijo8s#d<!0J%rcH5<L@7ag3EC8AOOzXFzmYb@X^B#d_F}Xt&YCDUBuW;vD4a7<Zc3EwXmL1KqLie)ByEcGBuZ)8OVg(KdPg0x>-Jk{Q=C6hZlnD++OB6#%g|niw*1WbU3g0C!G)Of!j!V~Razge&(D-2hq|=arL8PE)TX^QZMTy{P1<YHb}Knlr@cCDA#$indsW&>kwazLE7Nu}IaH#(5^W{O=nmTNpiQy*Q-nOz;9_WbxI8~oj4X>fnSYAXS7`;f0zaczt$~WPSENm`%3iI3td!#PReC3UCqJWDt&1wOSD{U@S{K!5uST0<wJvJVUV}EpYF*T#y%ueX)w-xddmY*ot2I%N_Ik7_R`>BhNAJN(hd7!0@gPU<wMzTJec<kBPq;hW8I8c5;f`o0xFg&SZ3DN1TcXY3mheO91Mov|W3&<67!IQi;4pk2+7P}Eeh_WyWbV6<IC@W2+8S;PcR(L=GWXXmj@~<!_JF&=z0tm~n)7FwccstyG8jS*&%lGw=U}Bn;X!aev_ISr?uqt-d%_X)NjL&`LLY}a!EMk-;Wlt{^kKL;`~cbnegJNS-U~N^8=!Z?4d908J#a&~DSE#zv!>+M0)7O&A6D87egtlfwt`#3kD={-89zqOPrzN!_OQ~fa2L1-`V`y)?u$O{WUdLN11O3IqEEw0pN01(HnM$*@;2(iO83A@--4Cygq3E%O1HyGx4}xcz)Cm4N;kktH^NFc!%DZpO5cE$z6mSc0V~}FE8Pt%-3ymaZ0@%uN?nTL`e<3WK3osI9j*u0K|^pIxE6XdTnny&-U!!#tD!~UYH$^_09*yW6U__X30Fj~gDb)n&}?u8xE$)h<>2yYR=7NT2bvSU1FnSTfh)n4(fn{_xGGv0t_oL2Z-A@AHPM^kns9BjG+df272lD__})aRh&F)BC(7Mfbo<@3DK48R^=Yq9o8sFOr7rDtX;XY_qSU6nHf@SSiBgmHnzSh{l_=F|uTGodn-irf?Nw=0Tq02_(_Wc2#U&G^TB6*9R)I?=N)6g;(5Cp7M5#r4E!q^{mMC>-uS1*SGKo@;_Ik7_E|(~G(S8?gWtdYnw-qRg??KC?X;yj*tmgaHG~KSW46Nq6RGMyAdMm8vyF{99S6T{I^Ia@Ww<|3HtNAXJrrVVkgVlWJOVjO23&Co>bEoNcrTJhr-#OBByVBgS$|5aIw=2y7-<T+s$gKoi8T|+Tho4bgJW=lC=Wc{6p;^*2EBy!mCbBM0sX||++0!&D%>t|ZbEWBarP*PX|Mh9QU1=^@<zFyOw=2CKR{0lA)9p$N!YcpbX}Vo$QCO{wl4-hKX>qs$>!KXx9{MU(YvV4oB%DQkUZP}0Z-BGHX=pJx4R+8Xumk_c(OL*r`j?Z*1*rd#DESin8=4nZ`m2-4xv8t7_-FJwSQW)TqB&qy6n~FqgH=)d1DYLHMe$E)PFNMizo5BbrT=y^IS+MJ6#tH159d$l-wFK_E=XM!#s8p%VO0u~Phqk#SzRC#rSHHuz{Svua51<DdLAwU7edd%h2R3{X<uea{~$ZX`Di;0D?JJ4gY%-t;k<Be^eCJgz79PMUkB$v55hU%Z0LSC8=M_I0B47DqKDv|a4z%+oD0r_9)t71*P|zV87uvhj1}jn?F6j!6r3L}h@OE9!iCXuaACM8dcn6AekXIKf5Y#<7tuf9i|~2$SNJ@97X1-E3!g^6g-^pL(XZf>@Nx7Sd>lTCehMFj52JDTFnkdG06qxsM=!zq;REPp_yBwe{TMz3A3?9cN8n@VRrnZu0{s#`0iQy@flt9_&>!G4@HzAs_#Auz{oR-CpJb@?Kk(o1ALw83AMmf}Z}4yAXZUC8Kf>Rl-^1U+U!h;aU%}VV&*5wEr|2i}r*Ito2#&)apzp&Uz?aZ>;Y;vk^gZ}8{4x3={4sn5{TF-%zKVVZUxmL!zkt7lzd^r)zkz>1e}aF2e?k8Zw``Urtw`4Y_P>0{{G<L|NyqvhK**o8|21F#Pc})6<^4;)Et_Rm=cS3?FVd2~c>d5;)&2)^L}L&'

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
