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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9e7856dd34ae444a934499782c5bd606/part_002.stl', 'relative_path': '9e7856dd34ae444a934499782c5bd606/part_002.stl', 'source_sha256': '5b64684d78e9171ce8d0a076c1196e04b489cace6d150f434e8cdf64334438fd', 'input_faces': 1086, 'input_vertices': 1087, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02707979455590248, 0.2988659143447876, 0.1459261178970337], [0.1276978850364685, 0.39948391914367676, 0.14781635999679565]]}
GEOMETRY_BASE85 = 'c$}r3ca#)G*ms*CK?DH_l9naA<SdzyARwr)WDr@>l9ZegXi!i=f?y;rIjdxe4nYA0kt`^%h=>G<B3VAS>sGxy5BtY=-dE3_-{n$NKT}iP(>v2$)3AQB<e5D4Umow!XSbVmiS@jMpQpS`-hfVh`gQHlsc-Qfy#^=o(g!}_KbuotY5H=*mPxz;-q1oFJN50*r%<KHLRDfb6e=27D7I&xetp{YXxp<-$4&|U#ddG>?ew4T+ofHvPXGP+xl$!7JYO`jOjOaxVUhp4|DOD>gwT&0rd9th{i^kkBxHE)xoy=S@u6)k67^o4Sm`%!34Hig)kM9wr?2q-``?@PeM%<k{e~lj4>vtx>baaZaesJ%^y&XFzH8=0y_aLU-0p@urk;GM68Ezf3-2|~Fg^J5%)5sZ_4(Jy_BApG-ha!CbLje}M7@9E7vb&r>-N^`_V#(v?X9=%{oJ{xKl*&x_S)<A-uS+WwzuBZ^B}+RD@)3Hl-KS33?mb5Z@q0FzWAK!r{!N_{H+gl+ac%S?vlnA%P0ER-u7?3-+V%%?X7q9e_d8SU(5HHdKOfW&%5&O`NI1jS269&S4-5p@wfh+klF6J%<_3r-aU`j&zP2Yd%PQmzP04@$abv{AMl0u+SfJx96BZU3+unyFQ1p{4Nd=V<dgm5-T2%7i#IWTb}Bhfly}by-pji<(e~E6@wwa9_<~vFIOE;8*?NBNY_>b$fPB1ouiPnl9N5|2v~PXyu&76QS3lnCvi3+~?X7pu*Sx-_pZHXAJn`O{Me=dAecL>bnJ<faw0Gl!_m^)!l307|UHw(Z89$ZBYsU@mMXi<f6q#tYTlZTrp3V=sB#+OB=a_zeikI~(@9M|<H-0*jSbOW;c<xwWe3Q$fe(S?Mw##uIvDWycUyJ&k58sjX*WYI99D7jKue__@`lnBedaU<X|8yiVAF6orNMik4?~bcmPn-TXFOkPpyuUNWQBnU_XHEOv2W36@(8d#Td}f_D{nYwSJYMbH_~X417mp;?-g-AanN!aQ{(jqcvL5S`T$IP*>*)jUt(_qsFW#@ZUeu|*8#jDt%<UtIwYOfk_tRz)<LPxRY1+TFUhXf}r@Af2vs@L^&#k3$Je7CjiTB1oaWt{^*1I}0)-v1eHA#+-^_lX>`LMLL@%@*{@yC0wuwCn8y9Yjeb*7yE%Dd;+`U4q{CfXkF+UFT+#-Z!mK|kKQbHaym6qoh?I@YxBF-z8u_nKyu^^cipwtN0VS-<kG9=v}n_tC`KTknpaxz`%set@Xo`cU4=vi|#<P5aK1W&QYY>)fLL(1QKuah-X`)M@8~@?krF@Zs4-<@{0J&9|J_Or2A^iu$b&&l+vEYwNK-Ur|{n-ixX$9&dQ=Q!|6iK1kHBy{+H*MHNN;+PnFmt*G&z4H9)aU$~;252;E9-k<WCoNsvVS`$%!Xm%abPjq)V{>r=Y$NRlrl;f|wn{Qb=n|^-kF6wvwdTlw*2L_maet1<rUwChQJ2~IRk1@W%>!N<`ZT;5!6&lO=ue_T-*B6^QQ?-@z#QF`<vi|9tjZaon){pl__K?Th=6g;1ZH+|z+S~fA_q`ZVzxJ;Fy_ZZsp=epZ^)=gy`om39%?jELDKF}`-m5oM)?Yfk@%L)U`jvO}<Nf#Fko7C?>R(hM@Zoi}W&PIg=`P1VZR5a)u0_f5$9o6fmHY37R;Hic73BV_yxV`R&p24_zskG)H)e==T*WKO{TCnpXppGin>*jM?~+R%Z}FklAIb5byx2Uh^F`$NEAPf1AD%W^j=%Em_@8RG@$-v{`mOg)y(7oJ;%!sssq}LE@!^@d<#9%Ncbu_4|73ZbQQlYWL-XV0^LsQ+T+ps{q#S>|*X2Vw{%s4H_D!CV<EgwGPkgw?OgWy)+d5;KMFl?eadI&}*85kMiTdO6mNV@$WD@mT@2#96>W`TnZTfjKrKn$fTfg<*`X!=%?QQ*$lbRV{|MsCr>$l#oxL(vB*(t`<zcZz%-+F)ZVmW_)8DZLo?;aBKM0qz)tlzO#&J*R`_-`F;>JMEK^;;i)`&&_e{LJyD{ib_|9<AScKjm6Ee=;vO?blou^=t3u58mImP0k<X-RtS~)y9{N7xi23P24ZX|EEpnaeZ|~)bD)8ZKD3Tswa*A^EXky_O^cO{o_B1`n7lUXZ+Lns6(=Tyx01KJU>Zt$+Vw;M$~V8_~c$ue`M^_vjczPh^SwCTfg<*!sDWT?cMw-ox}JxyX5@A`-RTS@z0Yx@S$Tz<@j5_^q8DKV`><m;RiW?ly~#T`o4e2`J=q8KdxRwGY*qBiTa(t@wa?^c_G^P`g=tE*82m`%Hz+Bfo6Q(`9{>Qy*vKk{p#1{@ke?0dem;Tsb@r3)`Rz+xF+jq@viA7*$Vl5;X@<6pT*-{_JwKx&nh|o%DeH$dwU<q@mJoBf6q;3yVqBX`mOgT-<R{b^A^+3fcf%xiw~uHO4J|TaMt)mi$wj}yYm_AbEN+H(fYM_^MCjaGyZcIi~60<o$BXD>yPVr$M`~1<$SY#T2@(qIATuFZ_637e&t>Lc&}R~S-<kG{&$K7KGbxktl#<)&xrcH_GL{!$0msStq(2DE9wtzX=!|#$@29}dH4Ed{nxog{o1?vKdQ5-=fx><{^P^LB1HZ1&3YTZ`)yIb^LL7g`Xg6;V*I@^^7yH|JAUH5U4=#c+Pm}N0rSk`D*v9S-}&)Ta{ko+!t}FYkeomGQ0j_u|6O#@_)A0O{;Ry(f35$loTy)WxBqrOZN{PCFuDI)-=?gnKUCt1nYZWP6!ly09j__J|D%j^gZ4Rk%kfv<jX&P&8j|C$ysbaJd1T;2&HBjm8N6S-x|}~5O9nptYzH}i@cxol<o-LbvDxm}Sh@cy@AhB3U$MU2f0cLV50%>)zoWCL-+J$1JyE~^PcQR$>$Z^R8`f88De8}p{>1p(twsIX+xngVp{b}}dw2evdyW~;(rx7Vfc2A_$noE`#ysAeFU#@Ahxc}n^%py4+Q&AM^(*h{$9oYmvVP@V{da#ik1IY}){pnkye{Yew7aIxIW^_{w?49moc~_Lyx`B#b>#e4-pzl!*SnjX|H`}L|DLG8hsM{H$A9a~ca_KgPA`~#8dj9Yf4pCIkf`53(B8E7s*3uxckf5x{df9_`n7kz=YG=5_`%iW`7qvlsjsL%T>L%rxT=&8^;_@P9VP0Io3hmOQ>2VM|5x6f|KmfS4Hxxm?~Xrh*O~2hDl3ma_;AE9Ie*R_Fzq`Rkn;!cz4n28{cUsIY`0mIeEn74z5ZJN=6mw>S9v%8^LX>kep*<a&*N{55%tF`$`N>fat?X^iT6r<BKP0SRgE8+TkgNgyZsj*N;X;UzskG%f2(Wiyc;R&w|>_oIsPrWnELN$kmHZ{cFq#@$Nc!N+3v;6^88<Ucm9v}Kc6P**WSJUPMu=v?3h)){#u`Vs;ocN8q-f~Dp^0?i&!k{AAZRAkDikCEAQ&Zhf2(s^(*gQzg~(rb*4=xU%#v$Fjvl>FOw|@{`|_rgJS+z-+!e%{uIa;c<-%b^7x~?JO1GPI$y}+kMi#LdAF$XH<QcbC*J#UnL7WBHg(>*De8BA{6=~Hwzs$Gr{mp&kJhifJAcFbZP&^3H|5>==j@@zpSXAM(fY0T{#YZ=A8yVuKH@J?zxDq79rE?7UpVmL`qxDL+Pl{;>nnui>zDFw{)G0JdXnD|^;;kMW{a$U+)dNI_V2QOe0ca?S^tyIEDZjB#h<c%<z4-FFXL`mzw++*b1J9tMJ|Z?t@m5*l=bJSYy6U5Wc~Q?vq$9db5RG=f7W<WzxM9<i4QH?FOQ$fyZZb0H1$k6E$hdJZ|sx5zpR^T`bmFK)bD)1lk)Ye{MV+RjYmcO+Pl{;>r)<=uV2c$`qOMP+bwrY)^Gi*Kg;7!m1{h%@8$8w`h9=M^M~zEEeiUL*(d7P-km?-y$-+0^9SYK@&B_d#%J3v>bKrs5-;kH+*&8_p`+VG{mx&yEa!itc7YGq+$rb3@^1d){m=zD|CM*YzZdLowtIh<sNZ^T=b!TUS$n4O8#l<~CqBIUA36UIuQS_?{YK7z<=y<pha#@a`LDb?e_OKEY&T-7sNeZ{SLOI``^WT?bCn!_ytnXQIsVb<7YBaVIywHzyYa{S_wLB?SKf_(q3nSV`RnEQTVM0God4Bc4SaamQaS&vubtx9qxHx9*v0e{^_8e!`~Nxr!B0(c?9uwQcjy0e`<TaddWERp`ta$8a{jDXY{o5Oo}52;e|}m~fBXyEjo-aU&L8F7{K0!0Q;GVucjphee=vU35>dbPe$tf39<ARmkbFt-=PlFa@!$IIGKu>AHMs&GUNl?Ouf03}u|9ixQNQ+X{!A%gw%cy5oIlp*ODF4}6cc#=*N<iWc<)>eQNI^8$ZYq!sq*|sd3XMU_wQ#B^=t3WA5!?H&Jok)`2*gom08pub8nN`?%fG;{#(B*udM&0L#CgzQ)K<hyZZ6|$y~C2<z4-~e>Hx_$FhFB9Z&cBZ<`!TgTHV7o~YmYaQ7%#|HG1j57ihi>sQ{@?|gn)zw++<^I#=YPsNGy{1fku%`58n!h=nnH%5y3o!?hN)E{a$(e!h2j68o(-km?-LuU(%`n7lUSNqh|fA~FFKR*1|b8`H%9XEdBP&xkA|6NXw|Hdn(&h@?=f92iy<NYT~$?;d-o&U_fX?*Wd^85$yJySyNzkMq$3%0kozubSV&sIf_f38=SnfW_Jj=%D5{PF(P@^bu@cjJGzsqy39lH-r}DwGrThxSeld}w=5QNQ(`S3{2fz%PvdtDhWy<=yz>{UcT6_$%-B-zIBKJ@W_1{nz?amE`d!;(_rwyUF8^^$Y9B`gf&Y9`skcr>tLjS3f>HtcI*#dH4GJMV7#O|Mrrvzj%L4NRB@~+`GM;S0Cjx?T5t3*B#~E^ZsJ-z=s;OHjj7iip0HrAO1)k<4ZOPytig~qTZi>(Tr!$w&rp5?<mI^??3&r*zRNA&i`zEP5&pl%K5LnoB!7TQAf^y<=y$i!$D>|KkhEiAFRJzTOL0zzhxfR@y_yjIW)?&|E-hUuJUgD$9!ZS@A?=y{@UAd$i2+?&svJ{*WQkQ{JQOCyY<`3^EB%RMvLt}=IwU79Tv}{8-L~9_~Y&K7*g%6cl&R{UyOevR_?#}(6jaBJoldaBKULOR`U3{@%g}q$F`N{Y0A6vwAoby?~Q6Fk9&1LFzp94mE)Fdx@jNRN}k6m?~Vf(W}7-ceNFDyA6_;7hlX;$XyAPrv@6q0p64s?>Mxxl@ZP27@^xo_v%rU6Zy=A)AH<sWI~&R8QF&MY&~AYbZD}meOEYXX{a>piUw;pMZ`!wdS@f^HJI~+nlX+Z|UX}IF%lK8$Z?anQ{A5hF!28|n$>Xr{?)RW!IZQtt>dXFj)DC>8aY#PD^Bb6cHrAHUukvo5&v?c3zp9R$Kc@zp_H(Pq{=Xd&_;8vUvVY}W|C>jOad5|_d&^Dx(iP?WKfTKMW7XvRSKf{P&uh#$><`KJJu;p#?Y;7H{2!b%eqm)f{>r=g`S*F#|E#KV{uj@>B50SkjGRBu<}`kF1v!6|cfY5nj|hBdStVJ2?FPoTEGg?R*=WV1kIU7sy!#xvNOa)6+t17QC0-k8{O`r&`)~C}2i_l7M!rv_yxYHOzH7ESs+^pk{ni@aqlm1(!v?e6ETv@q%DeZ$Uf*c8+n|g*u8zBC{J<!Ad>C@YY&W8WJU%Gz>K|}b)?@phnP+A2@BBh?etwwW_(H|x{8Zk}|M3L^@3$!-_pde00v}FMQ0`xgS{lE+h}^%FcjGg!mD%q6VzU2T9|YbTpI^>TykCC2e0>a0F#VJ*EXPfG_qeQ|_^x;zjNdrX)LEpcoDcC^&32>n$@jbPUhfI={feX8O+R;@ljE$s+fS|E{hmB8J-Ea4f32{r=f*A5zFA&bkM(a%l<)sszHR#Xw~%~Zly}D^y#MX{@;u?f9W!n>qhviPimwX#nVLt|gZHB*$$FBM2z=-TRgdzn9=u;cZr8ORHCFyUn60DnCn9A%cz=6Av0d%Mx*u;`;{7jFk1JEBz=t<HC-=vapPT+?%6hC1{UQ5_EIQS+udV7--qnc@50%@s-m5O__iOG;ydLY-cC`<ye!Ss{_wN<>Q0^Dao>-mecCFX_;~%RZug5L?W~J4MJ&)Gw=h5$4d39p*#Ci4nhW%cv6PusTt9j_Z)q8bf`-Sy-zli*7{_4c`N9!NkA15vhygm*%uZ{!$m&c9Q#~<s}@h80CSF>Gp+_PRE_hPoCUlWXjI^H_3kGJbH23{ZMt=Gr-@Uhx~*RLbaXC5Q_-&5Ck{W^vBHjk6<Gh7>D>Qt|T)_ZN<k;j4Ghne>3b=G=6`B*tVslGDxsMm4p{duG0@5T348n4b1toItcC;E@eeb#t=9)b_`@a6nTciz;a&U2h+Jl*ST<!oz%b`^%p_s^ft9(a9z6)q5A+N<+4>qDpBmi0%!5_o+c==`>!a=TR<n|}0pCf@5dQr6#Nl<7yE$2y;Gu$=!b-ZfsIC*!?=!{z=pdYx&n&%>?HF+kSeYm<1qu714t&QRI^{0pZ2`9A9X&x^*Z-!J0ET{T|)o?^WhJxCsZwnnTA{;YlvvfdxmQ=XqJ%x}E<J<ED8vcG(Oe~mWn)$eiEhf}^G_up+T0{__WiPrb(E&IPe+Vrn}54GOQ)<w?$lOGtbe$TZ&6n<0opL4zO>i1~p3wM<J@4w%e$EAKxx89%JRX)E}E}44N`vBI5@3)oxN8B)8z0Y91*Qt{{e#S(69sK*ho67wZ?@ekg`>$3o@Q=MuV*PFT{+Ktqq3K7z4}<rAZzkvM>n#JX-{*0@!E18=T|CNo^*)mG6{6+yJ8GP%Q@>ATef#Ee{P(Ul^{e;Otk>_Gg%@l#+g0!HIj`Qw^Zq$&wyWMRbzZ$M8rpYR)Z_LqyndfHE+Xstz^nJet=I2+hi~N$ynY|vdG$VgO#M26*Pj<yuRj-viEL#0QJ+&-uRo^<4H{^?{yYV*KR5B}jWUl*eU9V2`Wz>6{zB8g`n<_{{kc-O|4P%3{+!Et^*LAQ$Pv@O{yYw^KX;2?aN6{vJ_mGOeGcfSOtB&8M}1!TKVE(=8ToVi!0XRRt=FHE##Ja6c>Q^<_4;$$Q0kEBM}3a$y!sqDrcZm*kNW&NvPTEgUVRQ8uGYh}SD&+6uRmvxUpUG1qpk;VUVZK#>Nnkto4O9cd37B^`1EE|kGfvMdVO6)c=7kftLrqZ*Vk$IIWC&*s_RLdSJ#cipZmu=E_EG?^XfX5xRzNr2JO`KHrDIwYU1+b54^t4$9jF8k2k%B=|^3UWPPZOyzVHjZ9~(Kx(>>EeH~QH$v2Hx*K1j?ugi*@Gt_KXUnge0x=t({`MK#wUC(B{zHZI`eSxV*T}S7<x{l88yxn+py`S^yy1r16{iaTJouTvUIzxZuB~z!m9@2V!-J{p%o_W0LI!x>Jb(sEx%$tH#*Na-OuM3Uel;3!DovQWvI@S0F)r?oy(>kxNn+-knvgu!4$7{X5jyE(t*0fjG8(XihD~@a3Kk)iGXXn**&hb~qoBq}H*w*XouDzu*Oh4*6aOc%^;Nd!}P5<h8b?YCyF8$vfX1nS-dF%Cc^5I#>O+V^-e(Uvh`+l>F#;f}Xtk?Guc=sQg{%gql7s9u^&B5QR`yj$A(+6JPXJNg*&mz>KK;R#{AH;ff--q{fdDFkT55;<YA4>S^dd92!Wvtit#rQp28L#fsv0mS&6VCOf>0jMXWWBy`DDtP_roFn4$@)-Vbsy8HNrBh*TUoE~s|r<|ZQ85*xx8|7j92%6g)go&b*lT(tk?IQg=X$B?bUs7*6aJ=LM;!O$EEJqb6(w-7f$ns@#;Q7=hc0J;qPvmI`#dGczxeuXmH9c!QZR<D6QA`QN~xvY`nVP(|Ubhr+2ZCX|L`xwO-$6>a8jp_{Z*twO-x#>b0w5`ce1cTL0L6xKT~a<5l+yTd(g64jqj(?bUtC&a3;B!wY+x?W+5u{keUNSNB=RH5zTUtM22rK6F9e$L$xKXvS0BZ*Ki#_m%%N$JD9rb9Y|d=N_8B%xqWPkMF#?@7{0xjoGeR2f%v04nSPdU8a7uUV-&`T>}5eFQ&a(C&Bv1)=5}>#`L4sbFf~o+YoMZ%Z!6scfxtK?nHde2WGo!y$k2nx)%QV4BrI(s&zT6*Xwfl`?3aJuLokiUiZTvT*UOF*Db;8bxXn>N}B%FdMVcHby31;YZ<TBb+KNr>*C+9W4u~V#(KSOj5p^s(_XE6W4&JY#{0N!;PrYt&Z~8G{7U^y|7u+z>-D-o@udbBuht{7Uavb8b9AiPu3k3@uh&hAJUGsHwO*6;dR?ZtL2;&kwQiO5dVMPA)jCwJAGHouWW*ZtxYT-F*6Ve*;<K$a^{aKjtk>&+h4$<;{iyZIoNpx8C5zj>+w`N>NwZ$BljaXOZoFF0&3e6VoB!qs<JCHH*6VfT;)`A~b*lC5tk>(>g>zgrzJ^?9&w9Pio`2@P@#EBbfOx&`pLfm+2Y*)U5L&O-Aq>5mBJhu`mx$NvBF5B6ZM<5i(R#g3V|>wcrhm1br1N^+$Qc;|uh+e_Uaw;rmoBsMYQ0VC^}3q=gJ(_sYF$w4A6pmnY7WznUXK*7*By;)6KT9!H`V&b)=h1a*YvN~Yqegj%Nn`0py@}gE9<;kS2nKFbEY1(o~`wI-P*_k#f(?$`da_ky1R4nYF%IJ_4>X3_|m4mTCdo8y)JPmO&R0Wy2{q;b(Oul<xP9F{<HOZ-DbaU1vAcS-D&65y3=v7l}-O@eQfLXI@s~QR5ksmb-A5a>vG2(t!BJhKiqn~PPkvUhVg10b?4Q(=+^7?&z)E6uKSg1n|{>#@Yd^f;3L<(XvSHsWAD6L$3Fa39plw{`__BE%60W47u7TVjeLpv$G%^n;7g{x`o06}_4gfw^VB!()%Pq|ufI<rCRYRVe5vn!uwH+^Lui`u`g<#^*WWkcWqaAwslT`4Q{x}|9u4dD_h^i5XuSHK4(HYPbc7y8o9(La0kK|x4@lfUO-y_BJtNMm?-_~g)y!;HeUFLtkA06x_vT`pwb$R15<cIY<5K-Zz5X5+zjF&Q&Vg?zzolkO{ja-}`ESqp?<cjF$%}3G=vUN~G0kiy{uMP{%l`j<MNRqt<5$#dPU?AI|M#<jp9Ee*u7KCTUy#e-FW|-G0(dbzmyCnw!ZXOJ@C^7<@?-c@cnbL;JO!Rej)y10<H+~naqzq3X!u?DZE__1HavnH29JP;l7r!)@IbOZJP__n_J;eyJ;^uWo^W@vE8HFKOm>1h!yU+Wa0j?8*#>S4w<cS{t>NZmQ@A-CO}+w0!!^iia1FRLSsX467bXkBh2gwp1e_PnPG*6#!x_nRa7Oq^G6no3oRs`GiQ%O1-6SUef$zfC$;<F{_yYL{d;$KAJPH2>A19B%$KeCykMIHbd-6N@dw3hU1>Od4AlJeh;FaVT@Je_Ixd2`Q&mm{RbKt4uC-78wGC2XB438zpz+>T2<ZyTtJcJwo4}trTJ>WiYH!>FP2Dc|)hug!g$YyXWIGTI~j)q?%UxZ(RYmn988gM1DJX{GbO%{hs!-dI$aA7zv83E^ovy)li>~Kah9h?z<l1u?V2`450^$aJ4?|UZyf$zhAlb7MY;Y;Kn@Fn<n@+AB_{403`{uMq%{s<p}_mJPgd*B`9H}DR46Zti~30_Tp1+Rvek&EDE@H{dOo(E4SKZB>kACZ&bkKhl;_uvoU(WDQLhKG}b;NkE9vKKr6?m>2ed%&?|J2)18ooofa4!0m1!Y$xvvMwAAHy}fB1GpAh39bcKBTK{8;PT{iaCx{SnHw$%7bUa7Md5;EX1E}npL`n559cE@!1>?;<TG#qxDc5YE(8}NbHK&mQe+;u6#P6{7=9kEPL_qM!?npOaBcWyvIhJz+?ad`ZVb01o4_sMw&ZJYTevgX0qzX<B)h>q;eliycpyB290HGk$B?7oG4ObDEIc0mn4AoM49_5^!ZYCc<Q#ZDyqsJDFNfEVE8#WpW^x0(8UB{s3V#dlC3nGl;lt!l@L~7_`7?Y1K1;^KXW_rdKjFXNo8(paCj5ZB4L^XBB{AtGF`V#|z-h=-a2og-GClkZoP&H8&H?8mBjJ2-5%M{>2wa9N373H@lNI2~a7{7<*M#enb>aGOW3nOK7;a6rfLp^I$QZZ-+@0(KcZd6uz2Ls^P;wAF6n>lZ;kV&&<a_WqcnUcQo&rxJKZB>ibICY(F1(an1TTeGkzc{9;Em+h@J4t$8HTsRKajiNAK-)JPw+wb7xHKL7x)Yr51)ZAl7GS%;Tz;t_y&BByba%jlO;9jB{iJzlfY@nRB#&j88SWm44i{}7R~|ZBO~E_a1ru3xCmT^ED4u^Ymy<j5!sjw!HwaDWEHp}+<>eIH-PJr&%^cLI%GMx4qTfo3)hBgk>%l9@QY*x_(ixbSqZKSzeHArUxHueu_xpUWL5YDxD;6oE(J%C1>h(+519+j17{;M!`a{rWLh`_oSJ+BP7Nm^A0#oH1iq8R<W2Yve2x4Iz6PHs&%)>7)8q;GG<=La3?GB{lY8O)@NV*3csIP2+zfAp*OP1D_3#REIlKa1OwNZF!?Vd5@ND>V@?-dO_(O6${2}~4IU0T+9!U;^N5X^2{_tS9H~A*q8}3SWg1f@)$To00xFy*XZV5LcUxpjO^~l<AJ@^H(D*OUmkt_#SgiDdd;8JiDSpbfL^N_jVJa9HLGn@_1K&FK=z^Tb6;M8yu@}6fn34F&hc>}%!Un4KV*WmNy8TdSWn*0Sm4Id*9!pGqK<PY$EcsIEn-VJXf*TLK1jpUc`MtBvu5MBi@C1=4);ko3e@LYHrIT4-)Pa)rhr@-ULVemNkZL&Z7HawJk6CMipB|E`=;qGK}xI5gDd=>5pw;}7mZQ!P4MYt(kpDY2_hij4%a80->nGUWBmm{Bo%fUs+C*dM+UNRM&7tTqhfOEpnlF8v`;Y?&wI1`+aOaf<w(~};Y9?n80gR{Wd$tU3Ka3q-$j)bGg)NmABhD-yOfh&_~;mYs}WG?sxxE@&?t_L?FE5ME5*5r$DYq&l63fvy<N;ZSL!oA5DxHmkQd;=Z~k0krSBjNYSx8V2T56O4n58=<r3GnCeZ1NL$HoTae2``3MkPF}y@OttKcs(2@*TP|VC%FaQ3GXAnhxfrp$pi3F_!M~@J_Vm6e}m7#SI7(S75El;9lixWB=5ox;gm^CCQo8G;U|HgCZB?zhO?5H;H+?NGAEoHE=1;s3&ADGqHqcLd9p10JY1cu0#}FYkhS1C@T+74_*J+$*#vG5w<TYL+rpj6j&NtVC;0~46COzRg9pMR$hY7T@Vn$Y@VoFt@&kAx{3-bn{3$$(oDR=|7n1Yfh47c;GWbh)9l07_2Y*9ug1>=xk~`p?@IG=6ybnG~9)gd;r^sL7Q}8+RclaE9g}ek`fp3w2!?)mv<bC)doHD7&<Vg)D{3P(x<Wum|a8@!CoE6SZ=7e*@g~<GHA-Dut6fOZ*Co99%;aAD}@T+h$vI*P_Zbi0$TfwiBufeaw?a3IpJseARgk#}uWEZ#_+=F}r?g959d%=C+0c1aT06c^o1P_6SlW)Pp;ZdXykAlaL@4#c=vE+O3Sa<^Y0XzYoOiqF)!=I2J!Joj>$j{(u@N9A>JR4p}&Vv`i%gH71a(E^A6}%E&Pp*a6!&}Hr@D_L*xfR|9e@pI!zlC>`Kft@;z2rW4FT9^T2=9jvlSkph@G<fi_!xYGJO!VCPm^ch)9_jH9DEkOKwg9|z<-ff;J@H&<PG>5e3QHd--Pdy_u#wm1M(sK08Wz3WU^$26Mho-2{I-81e}^o1E+@5l25~F;SA(6a0WOtnHA0qXCrgK+2CAcZa5d5hs+1(feVm@-~w<ISp<%Pi;*SZVsI(43|tB>M?MdigDaAi;fioovN~K9u0hs>YrwV1I&f{c9$6o*2fs|d3cn0DA{)bv;HG4AxGCI{Yz?=B+mLPHHgG$#1KbYoM0SQd!ClGja98+EvM2l|+?(tR_lEnE1L6MgU~(ut7#>EBfQP}O$hYB9@M!W~cr^SzISzgw9#2k$$HO0zAHg5OACsTLAH$!M)8NnH8RRT@20WXb3(tn<lMCVb@M3Z)ycqt1{1W~GUO}#cSHNq?b?_Q^J-HEH4{s*Ffj7fj$?fn~_*-%({4Knj`~lt#?<M!ad*S`$L3lrWm^=y}hL4fIz{lWU$<y$!@G0^vd<s58o`=uC=g7a{bMQs-8hjDHLf(Y0z&FS{@D2DD`2fBJ-y@SGH+&C%NIn54{3LKPTxvKOoRWMRP6?+WpMlfBY00c`S~vrl1I_?vCiB3V;cR3fI2)XkED7g?bCadv+;Bd!ESwK6K$eFKz)@rcI0`O8R)UMb#mFjfF}MU-4K4u}C#%B6;i6<^xF}qhtOyr|3zE;n1>yW;IXFKYNtS^l;ap@XI2W9qd=AbIXCd>#S>TLh1e_60M?MRugP$TZ!B4@d$n<b3I63(woE-MZ6tD;1Pi8VHobZ#tx5<B#8BX{~;J?Yc@Za!N@*nsre2KgcUxNQ6FT;Przmpf>-{E-j4>%q^LH-7xfRB?W;p6ZT@@M!6e1JRzAAo-(e}aF6zbE&=-^1ULyWsEOZR8Gk8@z=K!&~4D<R*9nyq5eLUJI`zSHmme<>XiJa(D^33|;~+AQ!<4;5p<xcn&<1jDu&wQ_1P@RQMC}Gx!sDGC2jF3{M~@!4u%I<OlFrcntX-JO&;~z5|bhhm$@$93Dcx1rLD-kb~d>a38WC+z0MK_JVuB-N-lKZg4Ew1&)Q=lO5sq@atp@{5sr<d<|{|HzQlX&EROV2^<Z-LN<h7fnOpUz%Risl6B!1;TOnS@C$G?G6YwHE0I;;N^p6y0$d(0O_qgA!^O#xaB;XWSrje|7bKs93&MHH{BT}4f{cVC;Ot~hI6It$d=}0EXCyPh8R2wfdN>{YB>5ElB%Fdw1*d?MlF8wu@V`k-dT_!|0^cF;CpDb#lfeIwx8Z-_>*U|?b@(!Q6}}9gCojS0;XlYf;XmNt$lu}L;FDxLd=frR{t6$5kB~pZN8khGA@~6NBl#2jBm6zN2mT)Zj@$)*2X7~Lz}w+($T0j3ypdc7Z-iHotKn7fm*i6TOL!4EA6^8{A!osJ;OXS&aKrjZl4eTw$W1z*-EP(;_P=9Mtogjq{+Dn))_+ICPJQ}y<*uE_{-wCR=h1(;;J?1y%{~q5KaueHp_lZ({}VpEs+VwuqWAv*93a@3'

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
