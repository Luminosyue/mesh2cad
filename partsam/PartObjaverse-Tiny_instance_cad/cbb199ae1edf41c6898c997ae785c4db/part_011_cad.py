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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_011.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_011.stl', 'source_sha256': '960057b3b24f3d259d0ee91260a1bcfae2586259653f989b60bfb587bb571a32', 'input_faces': 1054, 'input_vertices': 818, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.17155829071998596, -0.29979902505874634, -0.1979151964187622], [0.49999991059303284, -0.06535477936267853, 0.1979115903377533]]}
GEOMETRY_BASE85 = 'c$}r22ecH$7Os2d00vNr0wOS=NDxJg81RgMASzLUVj4uiNEQ`QMij3(Ttv){$VCMdL=Xk^jEG`DB#0Rq$tDb#5QSGY_3b|0yPLJ%dXKgC`v3WA*Y29?u9`Z5)BUWH3N=0VuaQ@>?7B~n>f(7es(3ZM(E~?}x_rREkw*?0c74LDTIBYh=)|tQyL3M<;f?lgXnN_ukpo6FJt@`nltFEpwoEl0G<3wM5&ef;JaojR11;~^|EiG#4Ig<~|6v2o>t=0Qw`rL=rg_WMjj8{~fBTvtq@Viz?NU3It^2PoGm<}j_tLT$o;z{I;vmm$aXedZ#^TZd&%$#}cQ3WC^G^+ar&wqGs1-$ieD62Q0=)2z<N5mz+I4Dx=i!+;z26Mh$vyRL-g57RaGf+fGq7r?PT@)NsgucF>*{PCwyN0wjNb2+#c}3Acor`6pm~<}B|I%$UDxN#oA8v>XWlf=x9I&|@pW#ZtFyIL=zeJ~;}l-l(kgVngy-RM-CS-4^Dr{>zJzDtsk-%x^DI0q`Mh7@`o0U-_g%QY?|z-B-xl9bp~n@kgvRrX<LR1Lyb{WP`sL#FviIFkCz!9FAAdaRIq~1u5j$Tij&slzWx;%}rQ_LVSCobF534-CI6s*?7X|ZEO&l*Yx^q!De|Pcyc$p!g{B#q?vyFy?^7FM9&MwZ+4UbO`%>z7D`NleNJTql{?a+1M-mb@{7hgYJt9btln;!_RiwKwf0iK8Z`-9^0{0PqqXPzTm_7iwU>hpYRF6$!qjBEEcy|=RXe*0E0-k%8XG3b>b&u?_RP;<~Lr7_&ASN*k6eV*s6t}k5Im*-s9hZhcV_49kEAK}!`@1efty1rgt-gB#q^Os++bXoEJc6RqY!aKVAE<6V>aNjl0bKiv*UUNLHuIqE|yMJAHhWoC0R`$c^&w9UDXJP4w!SM^v!(}|eJ-Cd=ud~2$sh@p*c#)?U?iH#Z;mnWl6kO&<a~Y5D%!0i_<B4$Q$G<LI=0|gX{Iibvu=svo9{gTt{P4mY$NllZQ*eJgQU@;eGqbNL^6cD-?+5D(&%mX=@Z8IeOMSl%T<Yg%zu?9*cU@@w!acau7oL83U1<D%9k|rby<Fp?;yfHX^!4KSE?Tg#EWq>d^tr5e;m0_hVtr|zPAyni9N(A86-9p3eG7y2HJAE6Z{@hu*W9nacKHf7e{J6ltzUQ=UMTJTb{zNDDLgyNaetjEo@vzk?a+1MGM~Z=FHT$<H=aCPk4Ly3j|bP|5w6Emc)@Xhe^|SX_uD!&Kf+URe}8~yX0;B@gI@<O_0#J<URk{U=40HssBPyZWdWYs<aoMa=Ow}X?8e)RpD$^ZpMs~z&#l|-@;80&K94%xQM|tJG(7cf`~Gn}d;Tf?gLOQ3zS$k`26=wtv$6HF@Vu%oywERPKP~yHe&igec>bbxi-J6IK9q67y~gbpmBw)Y+$i;*J-Il)xy}pbgvLM3aj(jPIiY-g&Xjz8&Xjz8&V)zKnNml1r$=83-7od^i(em}+UL=ig4d0lS0(?%rp0q==Hl>tX4*KOy8D3ee4aplqwsuY+f;V>7q<x4Il=LCqZZ-$Kkj?C?+xgc3%xJlTh7Uao)dkpmhtOzwdCt_H9T^z_Vd-bTDU$}%ll2;Ft<2Pbzf4#n^g(VTSLbSdx!5!<a{pm_4!<J|9mdvROj>jx>~D>^TR&lr6&~kPvNr96dFx<JD4x~OiJa;K9l$J>r%gktJBf#1H$v09M5ib`+(-D3*0^+JPR+d50uw$zK8nF_fWt29_lxbt)Jd_S!f^guM5w77p^Zn-7j1}zu~gbK9(wUcGun9FEoDPX}HJuHP11A;hxk{_46CrgvRe*7hd=-Twi$pym0-raG9UN?XEswr~C5{m#^#dTbLik3o`$3`Fg*g>gP5z2+uz}15bS)t}i@$Ubub=?thMavn+P}!u9wym+=eN;}@>SFI<mba~Z#IJ^s}C%By3aA9&>XQQUui;F0GC9(jJ`y88K1+<$)Ly6XAKu0NUUhW7{IdVkPd)~|5AKa|&RzK8nF_fWt29_lxbt*`e7|GH{_&|LNh|GH{_$gS_qb=5fy9yzBe?w`}(k#ib6a!!-$>T{an{y9yqtIuh2U40%?Jbl5@3xhmzPLpv8Z+P^=(irZa-=w}irzxK5H2tN}`{MkT-Dmnsr7_$;*9q6>F2%DQ?wlREFZw(t<ALWZ-8s87hWqC<;rcwLctOo)<eVn+#yKse=To2G<bCP$o8q|(4h&zHb6vi{fuZ`5^PXH+pZDN7cy7^UkB90@{*u9uhn_=yK9q6l^O)j!b-yC#G#Mx7w5+;c`uvvJbp6Lg<?G^1yW#JY1vy{m77iKyPB34-&ei$yb*SX$H%<RIZXIdv^=rH!$Rj@=fy+8d*KfR_G=|H%^Xsd1q<OBxqqBot)={C-qq9q6xU4&$t92wiBkSeXA6^Xd$j@uwDXFvf4=;wsuhyN<)jIO$jdhe$^QqUDpU*nV9jxY4tvmnys&%A!s$Zqhb+fFa%)ymH_4T?FuGdk7&uR8>=zYmLTF~_2(m2k#^T(ssk)JQ?XhQgY>GkE$59`QN_e-z4%+@d01lO1UeL}eYK9z9&eJ8(;`o5EJ{e36l`uk48_4kqdI_mpKxvd*Q<IkUQda=IG<@;tWP7meFcyzwhm;C(J-D_g^0mc2F3&11$13dEmf5rWML+a~&K<cyJ)3;Wc734YL`&5|~tP|Nc;E{bm^Kr{&26<$EfXn_+C|NeMG=}^8hKyhD1B$244bNv}e~^6kfwY>>$i5--p!WgAy>tI~HN@Em3U&W@wKRtN`-aTF-Uk%-rf;1XdSCGDOIs$E#&Cb%5U%$D&9mYA71<x;d1D{QsQab&joi1xKMC#w*%NOre!oq)>;r{^ZeASBmvyc4WnD{t;rm{n#;qgGz23X#2f1Ef!ppzkxNClC43~B1*HP<8^TN0vW(K*xzAF4Mvowyg?u6@gq<L=4%;`a{*OzdAeeIety)=$<AN}#Gb)<Pt&8J>pem?6cUpqXXdff@v>qzr#@6Dm>$~wx`-W;m0*PTDlY90Cc!qctqi{qJYt?mom7q#wuuGW#}sT;!gORq0~eq?>A`=!@i;fF6j4X!Ww9MoKX4kBFtJV<l-+!U@qXEoRL_0M-S_v>$){#oogRXp2s+bcmHS-)_9oz~j+N@)!D*R|Bq>s0eG%ccjptkdl752lyKaDQFHBkNT0{57{e7vz!k3zv18`uncuN@KXcu4Vjsoyt7OIz1;mpON(|^AAs}`HZY<cx0XW^;y^FtO{LM)@iENs!;vNx)!e2sp5shU%D-hXHK4VTU;G~UCTK2I#oP9I()w(>sRK7b(-4|zF&G>d%y1fJnlKy-0S}Jydc-lzi@fZvo*e+R~o}*UHEm>a~|Q>%zQ4${pbJh8PAo*an^-!{hUYmuuG=}xqkkI%X6OoeZaKR7%uC=f4}NE*F2}@Q$PRy{KE^?!}F=vMR}d@bFO)|`{K}b{pY;;;!u6PE_|+@bItRuE*Trgb6qbQ8&^lxg+EU9ocs4h`0()k($ByD{P3LTe+%C)y)L}%{l6$GKmW>J$nQ}oF2DCBJkQU?<oCEVPc?GCN0Hq=ojR>ter9>``(~QU?~e)3Z*p9Ie@yetA<Gv9d1m8;m2vfj>-s6Ut}k5b7q)+1<b{n3RtD!sbD1CEIk?P^=KlQrR_)8+Jm>p%bU&ws%Y0_*b$l(DFF$|O`DwW1d%yP#)%Wi&T;DI@QeWpw{qp=?uKv~r#ou==Y<??K7Q?d_FUkb-^IIwud8SU|>&jwywpWAeg8At!AG>iLRBe1&49}l%!1z%8&6C{o*0{%nvKXEz?KUAa{>?pIeU&df9mx+r&zj5g=3iGm&zj5gCOo^ThPz+t{R+>h_nX?Z!9CA)!}BTJJ10D!1%3}R{ayHe2~S-RzF&HMX|CU|USFE)_Z#_~RlLw;`P|Sr_2;k5r~DkG+VZ)jG2H)LmOA=#R`X%EP78ARoX!1y%e2xM?td=J{OHeF#WPoRm>PPX_2;k5n|%KM+<t0l9GA~!dB6H|R`G1t@O(x-e`WsRnX2LWjC?Npb=2pq;$GJ|q3g=$Y`W^4Q2of~vT*%5t9bT+C4=I4uJ58jadrI9Wto5dIjeX<-LJ^!uRK5U`TJA&e(BHU>>s;h_fO4b{}itGPt9fj6t4GA&1L`e>!|%xbJ;)rajN}O^R&v>`<vz&H6FdcX)gPlaJ|22?(c7ZP5-K>dY^$u_8E9&pOJjMZ@?q_20XG4z$5EjuB+Ft)Y0o#-j`m#e!g0d@W^@;uGg31{`!JP){DF^y<TMA)OyM7=(V<3Z{sDQ&mGMR=Zu~o<oOMbr)!U%UmC;Zb4Peqe*Z+(7cM_95T1t1_xU4S*I)nYirD&auUB~dX~|dP7q08)Uc1=+KL4Q6Wo0ourRt~Po~kcA-F$ReXx`>e{GeE0jbC_L&kx+w^CMi3e{Ng%d+B=o@U$L3yl|izKRm_wQ#*IZK0lhv^CMh8Kbp()BV0c}n#=PeTt7b%uIsDkM{{|8{5tCS(OlQp&yVIQRbM|pny1zL>*q)Fw4NXJ{6x4Ozj}T&PwVlk=SOpSelnxHuZ!1R+x4U3_<O$oa#?_9$5t-#tl}AXu4TKaaXdY$;gmR@`nB5AalCNtj;G>ycI4Mj#9nvrxsS!xNj~yOkf){2t{W%E@`>k6isOZQ+Dwe)jrV^bj(cr4-xJ4EgCDpfj_1!me?n~i36*Y+<C(v6*T?a6=Rb$V<_|rve~{<A7x{jXy1($k5$Zm|v)8Em2+wR+_fhy5bsy!rqt$(crz)%aD0M1^@1tKQans~j{!sWn`gQIP-$$P}3ExNIh10_K(XW4%x{vT&M%_nv{!VotrA~#XuaDz}p6WhIo$=xOm@RD@x{rlJ8^^9+;d=cF*XvhvS-+ag`qf<4ujaCTBiCj9M(VJB{r9ETZ-ldcHJ9}p;jCZHW&LU{>sNDGzmfW^U(IFxYA)+HlF#}TuGg=Bf7SZ+=Tog;&1L;Y_!xB`)%w+3)^DUv#qfR9>o>w53g1V)ej~g|_&)0O8>xSlx{qr8YA)+nb6LNd%leJf86Uondj019neO<8bm;p?n*0Bc7+zTaPx$`@EAIc^&Ob}sJZu~n`u=T%%l`|8r{FRk&1F2obL-y-|NmmC56`PQ!eyMPe}60T{Ki?KaYi`xg=gV1PR(VU!qe;T4gLN`gsb`<Jg@2t*W*vEzbCd%;hTG6>j;-RnSXb?`P|Sd^nQhBh2L1O_;sc53|!_xczVNrD}&<^o`R=)hU<86|GE0N%DN)o*ex_3;rR`Yr>40&niq7P4co&1&t36C3sq<Rw$Qv4{ymiO3=WM)^V||wM|gh2;Lvz{zW$TYcr?#c3D?QO{pb1Lquq7Y-wlXxSr>5qcLOx{*O%1MzrUxsuCM=JzvA+|dAr&dd3xih@b|ajDR^p)n+M?@-2c8eJiq?E(0GLB;Q5^gh3aI5`*nK7&S!-C^?Sw6r{@08@1%~JH$Pv^Pihb2N$ugfDP3RX>+7b}b@Qr@9#3Z1z}WjGT;DI@`hE%5_e;3GU&8hM%Iz8*J3kRF>m45XyBUi6pLbG6|J@ADb$$JJGZdHk%<h^HyPs$-`-yP9pZHwuCz{KCB3$n$xm{1h@3-*Ceyeyv*U|f};{JXsb@YC_Yr1<L)aQ|K{dpu@e;x_fpGU&==aF#zc~sankLM(OPKa>7zT^6wpt=9^Yq&lqM7XN2&k36Qzt0Kx&k3r&K0gT8=LgOG=Xv)gH~;Fq7vb`J!u5GibD1CE{&`Q;*XKb0y6POLxr{%zdpFOOIu9%E?+@_Ed06pc{qCW^ws!2y4i9f_?Rhr#@oIX5`Un2hnuYeCX#AgAyZqSyt3S2Y`l#cM{r~%0Yx{nXH1Ewsy%Ntm%tTWY2ch-wo{6PN=dEtU+xAVyC(w8C(&nKFe1X2!Tde@M?G;UYlXPlpeUmJ2D^S<60y!1Pt3WO5-{N%vZGgA^8XCU@tr+kPc-?@S)-N(`jZ0iTt1a-h&*8?ujvf;5EqHCUG5#L&7N(kLfHn*GXLxP3DgIy+hnTnveH{M`zA1VLzLAM0CLTqf#5bhvUi4A?3=?BbY(dxIUodeK?KjajgEpJ<E&2`Kwr5RjK)2v+-|@7Mr)?~4HfIz1E#9`jY~oXN1K#$XNBcb5vb5Qp&(TfzkI4BFU5K}_mUgQv@voCJ4}BTGl-D1jZ{a_p?^5(V{M+QbjxNNP@p>ux0e&fc%g{IRACmJn`WAjZuglQY_%iy=M_<FQA?HK%1N<yr&qvqc=hJr<`V#&da@L@$@t2txVxm>T=`jiCZ5)+w?N%=*_t=EX8A`70WBujmW#|xmEAo#*kHw#0;zSeU&|B~}&ZpgKW&DNY?1!F+uZ*66o`@eu-udW-_#@4jx|!GyZI3^~b8S`7{qQ!YD|uGi1^Tonr#-w1b-GfcEB&o6{{2f6hofiXZM3A_YGr&Ea!y0j_{!+MXc~Vwc`eZ{c#pj5Xcv49#+L}ZuSB5DLlgL}^lgWp7U<KCoOW=JI$fyIh5pu`!I&>Vd*LrM(c464v^`$h&Okfkd(*c)nhx}7PfmOI8Pw@Tjb8M({#;&<LWkh5F)_@<d1!CEw4IBdhaX1Y-e|8tpWfuin9rro5NZsezxA??#<9j^U1Uw%YT^pdsm;H_D{r&?vb0}L&MoBKLM`btjGSR!`P!BBl0|RD*EOGowe9C^!s)t%^HzVxTm2Pp^ADqs)kE<%>d@b6ff_caNz(PV`U|xR=sNTld~NdUpoazgA@sNU6MfdB1@tF;9r6!Co8W&Wrx7)5oAtKN#)NC%NY0Ps1?wD)-$HxCWO<(Tw(sVIYu`-H7V;X=-)aN=Cfe&K%k!+aeYYlD`&M!`k=Ky^R#W&5wAV|P=UH$2ZcDiKZRBhquRi^)HpYKLd);Jtp7q<*^ROZCJk+CqJ)Q^aKQXbw#2WM?{2Khng!Rkq^JC6l)lAeutK;k7>!LOAw&rU3TU~|!2)~@Lex-?;CGHxv&^q{9_yf_pcw6&x`dj@BzY4#Su>MmM`<J+D9DvrsAAqll9*Ezcw!I1K_d%=Tt?rBelxwXetpD1sH}rG#GyLB4`#b5v`km;$c&q;;onK4;?+NRFu+KKS4wY;EO~0*#_1~iZ;H`d#|DOK;64viBu^asnm1}OL-xq}SU!vdPt$v07m;RMYTv%Vl=zb+mck^1V`33#tIsB4m^Gj;3K|jG)rcO1YO5k~{&ULDnlwb1=)8|zaN0m5jS>k+a6GxaROFDfm>AY=gNqb9jTGMxdi6cv#+C1x9(Qf-&U6^$KNUqZ=aJ^RaebYp<5~nuL`sTFT{#F+!oo~i<ng_0D{lO*SI?Iyfbv`t{KDrp+EYQzteSFfydr9Z5ZpPd8EykCi@8hK{iI(8k)7N^dmEg90FB2P*PHn9X$?~@K)U|9qIhDw(L@n#z=Jk3sg}4108UGHtSHP!uoucMmJP(JKxO#_jkF9?v8Gas`1bj<gTRjv%&3u;s&qNEfIsR@FPnf8W9vbk|cs-3=>mM`ml!?aZVfg>jmO>ljzcaDk#Ea-S{EPUR=#BWTCJOW`(8v1C=s5Hi{5brL=*{?z)Y^<njW5t!&{y!c;BQ9f;y<I-7pT<u+Qb_sR-v!pzoKmgx(aV|7Lm7z`qJke6YryM;8)Q0F8V&+<}4v^3ALopaubWucku7hmPZ%kZO$_CmQhRkd}3k&x*VUU?NxLE-sXHv-pACEKK9<tK|jI2O51F74t_oN`xEqI{L$vDaJ-4DJ*Oi*=UXRS+g0RPb`?3tk!N*;SKenNIaWvDTa$k@dOUu-iQ7!HK~KV8KwA~G4c_KlM4r|C1AR^+=OlO)>Rd#Pi|B9t{$@-aOteC~<82(}xpu1u;CqmBI@$q$0J=Zg0pE(eqtG7sqfMM+q8i!>-<r0nXf?de=}Df|j)6X%$ms;HN}Zn6=t+O;lZ>w>+5=yUypllul0aJ$Ey4GsZ%6d>K%b7}bc83V(}Nm4=x_a*%+*C`AN<88`kFWk?Sz-MGtsl~ed*f??GWhGiJVUGGpW;u8hz+*eLr50Mu+3C_1trOKH3*AZT-;m@gwQm7wr@1)0Z3>b3f_~r^aylTYn|5Z%#O!kZ@ksi(ON<CCb;AwAp^+X}^-33FJ+nmh>4x&Iqn`C3PlHYeHbXd|=`u6W^lS@!y&F&BQWv1zy@dK$qcvqwfmzqd=b(<g9>yK%MQ>*iL`z+n9$dZK6ARF5X6uq-(c&BK|ybPD9i96VWzk8sD9~9_V@a4kpevaRGWM{z4N2O`MK)!An~Q^mP0{`gTFj4)p0lP8WCw>Rd{VOX+X@DJIS^(F@Jsdz<KQqAl7P-xhxgdIr81eS4$*@z0uP;&~HaCY-KKIRB}M&rMwCIUVCUFKxEpr?fvy&RX);QcL=bA!iKNdX_qCskN4CS)Va&mzr3baJo9-{JSPTHqqa6I?!`o+HAjfY0r?en!MH2l0E~;8OXIV)LBif)m+Q^lTF(nW}bdC@n_QcQ((5u`rl3LWpe8zoVLLKV)$+oH4{!7C!DwKjmd3HoAo8IUwCc#FZ8#0hoLR-KbW?^O&pMLT0i0ZeV+XtMKfl!Qo{NBO+4+n_NQsH{tgolnfMvqg}427k++LB>mNq%Kp(>YOkR?Hw!ifgjGt)YdvpgrVdk)giI(Vb_<v2G%0^oxowmjwhp&NF#vg#%el_6Mw;=Br^f>%qrmd3Erb(wq;$JfSt%O(nV6$31>HG`EFEsHFx^L2X+rBTkRu|I041EDzi2sMY{pnX7|D55knD`T|m~{RD6VI5KjV{LDW8yIrGtmY3#rS8?$M8>~_n?pAXOi~@x)^`EiHGbON9W-$H*tfB`_U=*fhI<pxEp;GKLvjSIud^^IuIR+zni=#(JA<hi6JKbgHFPqZlbS=%g{0S(@b<TaVa_iKL+0y?S?-GJq_)Kzm&Yu=otJdCeAc*F?uz=u8G4<bU^#yYneF2L>ldi?}I-aJp|trt%V+fPm|XZ?SrpsqJfE%(a!h^b{{cuD|#>fL({g>#P{g$_#aICVPZMD3NLLRqRa7r(03KOGSFugIji6wQs;MS{7!%C&oR&Y`F1}=+v9sCUE4|M$#|R7k36gG0)5(((;j{jb^1}GAN{TGXril$i_k&%i%kqR(FyH_m$r^*C;VXgc0;=c`g9|w8@wZR22o=W{jERM#F-}gpqJqLniycB6g>-Hia!-S6W@ovebE8<>&?Bt!Ng|?r(YzT|H{PICZ6-0PWPObHrwwj+OH?)3-Z38mh_oU&UCJIJ$1gI))!pM`b$jPAQSH;oUTbY|GtS&Obqax4)&avHrwxg+Akqz4S8#*C4B~yGni{#LY+0#TEn%hZ)@8AGV}Dii5*GjPleew>kl@0N1FK4bGi@SeqQgLaG%XB@GZ%0NnT61^>xTQ2yKZ!2!C*(zxB0EG%@k3=hO@MBY7?3kv6Lpc)bt4IeE3wCiogA8kyMUIsM0T-kv9_CEQuVhV?(9HSjg)_ao<#ot#B%Sl^J^4XN7@{txx*bB+4sR3jR44e4+FU#8E#Mjt?@c+TfI)7UeI4eRY(@5`J|;kD&cI2+l#KhVALe~|ZApuhFo?KB#HCpy_H_xti%#v^T3A3>+!E0VvR`~?0d6aSj{4>}3|J@Yz&u>LmmC;U(3-p2XrLC#n^@H?rwle#<Mlc>LgdOK+Qk=RLX>2LiJW-Xjxq6Dplx96^!Nq5FN4u3p3$CGzF-1@^!9BpD(!fBO&KY`a$U)roz<#jFmvE&_&9*u8q;wTe;C!Fq$x97ZONp}XcVf_xYIlei$*4y*pUP*UGJQClE+O4SD3T}M`69<}jIpOr}g!A?sxFq4ud^W7FNp4N@YQnAe$V;L%@kxAzWO;w<cbh)@8GR95lqmNH@><3tZC3N>+xTka?<Rjg{7$=v7(X3-HR1f9%+qs(_0OX_@jJ=2-kxvgC)^p=hV^#t_F)cR<+bInQokbir6M^ysBitwK!5A!ns~>=MD%}nd+wc@aA(}b_$A~lA#VxX`q|{oL6_j?;O7SVTR+Rh>n83+9}oC<crD|RHmf=GfA}}an}xoPpJC!PyZ@jM<DX?-Zzrt31D%1NL9X@oJU=<%&h+!}^Qk$Xy7S==Q-2=y=F#>%F`wGf-}(nlOfzvMdL!PR^T#IKnSKg>Dmhchn+mu7e)9f{PR0Kh|6riM_4k>0!o(nSRKQQ;wTwsFtX_xSh<}>A`_L!wcbRy^#3kr3{C}9&3}JnL^e+5e<XUgPei@o@U&BnoPp0N%>Q06aqy8l7O``1%VluU*zx7v{xXDB(^gO)%y5`)3`x<5pek?g-$r}r|{xb5eK*!>*z+V;UZ~b5s*O+LBb`SWQcrD|RHmkkR^YGV`HyFJJKfuIr6Q`nQ<1c1jPa&*tiw?jKAlG{P_1akp_chzq_@UGsO5LIGv#EbI^{%F^KQWZr(%<?sO!PBR4?O~JzmBu#xjsZo=DHtx1lkhcfxM3Bx%iIwGXnjsZ*QW9i38C?1HK=xWjxYmwHbN@zBhU8(H{6x6J1PHM^pHdnb)d>_0`Z)d?~rs+pkaUd9E|jkh$)HrqG7?lgVp~o`r9VFAem!{&vs(47C!v5B^rpM->R`E26jKZztD!`}OkPp8J~lUi|&kyq~)F!>zZ!-(Jr|9m4wB=t20}_yY;+>zX*m#0e(0na{AFO#EukHJ;Npp7YXXbAO`U`r}NTXyRwXelfA#p0hlsCwb0Go6Y@&cIz)Q{&ExdqYvQ6nz+xzRCGT61{3$1cm{n1f4zyjO+1ax#ZNIY&%_w?9{khfOhM=2uQhR}iKoyx_?$gYnYa$U3;z^3IrL@xH70I1@dP>>|D=hROpHeFz&}CGljuwMktS|4@fi9d{&5qtOpHSRgMW;i$I)5%;U;c1@d!E-|EP%<OpHJ$;2$C9QS=4;P!r=#Oh%{UA2u<=#4z+0{A6+-MrYu!Hjy<k34IR#kcsC_3_)+kPa@|b^m+W1CT=n@5uJvA(8RMQu0qG*CzA6Z`Yiqm6E~XpFZw@x_p=honkD7`Nu*@ib)O#9#hksnxZeeqfA;q%&7B-LV$|jQuMyod{NGE0J%^ZD{(m;<epW@h{>|AtS^R<71NOHfy#E8oYx11'

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
