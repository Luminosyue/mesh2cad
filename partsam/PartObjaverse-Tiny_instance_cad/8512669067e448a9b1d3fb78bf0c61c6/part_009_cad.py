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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_009.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_009.stl', 'source_sha256': 'f4b2e7dc68e6e5dc54f51b49da3a450b351cc08ee282381250a4101341135096', 'input_faces': 894, 'input_vertices': 511, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08853154629468918, 0.0876394510269165, -0.14692701399326324], [0.11345624178647995, 0.4626443386077881, 0.060316503047943115]]}
GEOMETRY_BASE85 = 'c$}r21+-Mv+yBpyil88ukQ^ETL68>lfP{3HpbXLo_tGgabc%Gx(2amd$Du_LX^@aXL`tRM2ME5ipXYP#y)!@lYyH>zUe~j}pZU(7eRiMPSi4%nL{XOhWwXAUetu}XcP-0Aax2Q}*}7}@_AOg?D;V9mkH<<WzWH-?Qq2Z6YB%v%J*|FuTD9)hvTL5w-aKX6l+07Wo2N}o*X~_gL^qG=+N!njE4Ap@t#!!n)~-e8)}haNixn<h!290Y1-$*e|I5E*p&|sW6&rVj)Vbg2mk*6D{c*MV>>WGmJEL}T=dAJVtF=~{&%rehHy90!d`r^%TR&PS>C<cx-+SkZ`1a=umzmGL>jT8Mf0!Woc!$oB^uc9yG@pax#SdmLBF7E%IQy-nUle^de*X5&L*fT2=hfp@xwu4*_r@RVwVb)c4{W(6^$GN!F21w*yq3REJ}Hk?{7dn@S?7swW%@(wpZThm>)DrQ<L6_S_lR%pIi~q<?zTq!W69QvA9YXLZDhT<=Cgn9t#2eBZ|?I_uY7CgOS+1^#P|1Kpy?;CkaGC{E+D>jqwqONfB2!4)2UuUj^i!zv7`_7z7UXf`<81z^f@HHb#>x)NnbC$_;#|CTF!hk#kU5}St;$2q?6Rk+4zH`v%an)zJJ<uN$;H%vspfuDXe~?#@b)cH%tBfQQ20;?=S!H(t6w>SyssR)+BA`hPkBt{uw=%%lBy;?w0g@vn-e6PpvF|Fx5pp?*6;lo|)2#Z}<C5$HVxp+WswWFO__<Zk6=D)#YRyI5C^Wx6&SycJr=Hy-<$(i>>~(OzQW)Ddn-}-;nX*{FZyClxN<?74rS@af_s#V}8+bb+VS!D_Fjv_<{W^^tiR|OZ!-Vd&T!Xd#K~*AD{HEKk2Ro;_qyw{`*z7$?^UgD}LbIPf{MM$EB~NJPlikZ&i7`McOS_Z7Gj+@Sx=9jQ&*1zofg=%Q~=LkJC0FzJJc#U6StF5FKAfyIhcblBAv?`Tr3ue(=a?E&t%1GG2ozI%q!AJ8OL(K9_v#O<BeFW;m?lE%gkUpZ?aDb=-}P*(l}vt;THme)mrCeQ(ax`WD);Q_>AxBEC~2`i$hia)R_%Fv}$I?V@{heQ4Hag0xGeahm_yq>|n$cS4TqoJpnmWUnHAAaNO87dk(hC;6RDAbzl91}$gOE$ZJKqJG;YI&P~J7T>PZ|Fo26`DMw+YMN7gZ^7$Yo~nsu96JSX$~+EKYa;phmY$G&oRXu&_Z65X`PdIX)qM607T^2HRc+6q33OgxiqiDYcIkW^kXYx-ouuO1ixz2p)6dfNEmO-mlK%aQI{qj3)8lq%BEGfqdtEo0me+Z@qNw=(r<FHJd6ra_`DM*7BEEejkL2(DgLS8MA@Kvv>gqbMs)eir{%@Ymmh|=Bk$U;+)YJ9!)AQ<&dtLLXRZ+%||H(n|gCA7Vb@FtSuAf_GiXW(2SMmw&O04;O*I9gL;x6$myRpo7|G}2xTf?_%zf=!MIc<D@lh(S<^!MugT~|r{y(M%!<oHL<7xwadv!wlB?V<Tc71i<ZpZCOfo~~3sMH)$O75&dl`CXeid!!u-URfo_sdGqtU+=^^@1o~xy=trP1a-Z#%Vv~y&^jJ1zO^om<R7@uLeDqB65@M(MRc4T&ZX_P`+&~NRR5lm<2L+I>g$|JB);{@eetcf^`w2Q9%ZJ>_dnLubz{_FnP2uQ-!v&_n-{u%W^AMD-sjd-(IM-#e=lFrbtL!mDe}7wBjtSLBp<2yHqR!$b+VhDN5<ElEa|px6t!Y>9NL|iZ598WN$TIw^}%WrE$f>-EU);!iESmlFM8V!?bo`K<ok3397%uV@)~L9rb#ABIS=fSackv1HByeVr{;KRw*${~9(Ap{Q|Ir;;@eO9X?b=e(DUrd!s0szb4vTz*Vafmo#prsp6EKZv97M4Yrc_n*NWOM>79&qq#gV}yfs?%?iyXM+E>>0ITY?&0}u8S|C5!Y^moIzOZs1;v|fX!i*M~&pyiypT*jY0WsLaV{a@=k8SEjxm1UTwZ_-EmtNKOp{ed1MWqzeduj~95HFcgm%0EKd`SPdIk5=t}zL5L_HHN*kobw|5?K5NKI2*<c6@Se~;@ia&$#`=8K+z03@BS<yz7>()&EJYhAA8){Uk{OTW!s?sfVX6P`!{D3-|3_03;Xw8(#}??gM(jIPOJH9@$C|RO`rK)ohO&-hNqvMr>|(SlY_+H-&M}1&h5TBuixq=zFn^VMftq9{nzrjZ*lblXLY>YJtyPVpE8H|f%~6@)z|g?w_k*}Lu7il{E_KhfAK-T{BB_Dz4Ce7u!U0IQQgJ&CbD$CcdtEA(!IT7fb@I1PT~3BThs4^`$@8^KQt!1eenJH{|@(8t?nPzo<H63i)N@P_46jKpyOfQo$Z?Lc^?^{N4IPL&MT+mr1}o^$1l|Wsy9{FqiLhWxBeWh>CaWr^l1u-@6;L+eq8)O^K;?;fVJJj%K7;}gQZ;K|LQ7!vLm|A{CR7H__>a&zjt<cdi+4v-C@2}u4xx3&&K>Z9`@$Za$Y>wQQG0|SS|mr=cdH>{nM9deH#@B^DSHNo2-Rr)UW)N_`wg->Aag*D9pDPSK_?fQ~e6z=|d;Xe(`<pyboUL+bO+gU+R;8tY1DNA9wuV`;OOnsqek`+S!-+vB!1&a^zF4LHKxc{RUma`xoC^bxK6Ps2|(!H&zUZ?^`pze`$K>t3O|wzZLz;*|72y@7eNY<HYs<Yn-I**8FAT(E8`hXVPCOQpt6=mHd{hGuHLS)m}Qz@&9X_cmMNaY0sLYbX=9(rsv(>=_^UQ?V8W}{D%6!ulz{L^J0~rm%YEp`NP`$yo8je%{CoZ-F9mF;GUw=&W(%ddGqy7dcLl$zVDfyPp#)k^*rTt^yoN0rRUR{-|rURy7h3U`F+-ddY^l=BL3m$Wlg<CT+sW+cN?icGD(pSt(UAbC3BPze^t62@_AtOaiZ<|mlTa$$MFAa9ov_#oYDVUC-MJlovhurp3y+drgDF3KO3@0{1^QiO8&e4)$4@6i^%na)#{4+w~A=H74NL`w1fJw>%Tj{@MG71*N=`!@0KSzBE9QBeAgG&Zf<=K{wuzFe)I<?$n};r;ChR&^lm=aKlohy34h7?(ZA-%MDYtA6W@Dbx{j0gp3C)__3UC>`5auM`R_WV`P)(L_4j%`;QwRh<oJH<^}}m}#P^pEPj3z4d|Ey{eXJk7;R`u#_TD;vn&ooDe~__bSiRizk0N~PYZq+UMf?u;^tnpyHJVTB{oUob=VG+JU8+fa?QYq7YIz3gyes%X?oa&{%ZMLrb5pPXH#C&{W$Wlu@vRJL^?5?cO)`F*YD;>>FOU7|0&TbI>f4XTY5uEgYCG2mPaj*ayC3zD{2o`+>%cPQwEVpq^^?yD4s4b0laJAHyI`vLc0kY9-bB;&ej)#oFC~3}Pjr2FRzZ#%y!vpE)VEtxZHFG0b)08U{FUTWtf0(m|N7i=of>#}?`uh)wvMiE=L*U7W$=0b@!}t-uJfY77R`Tba~)q(OX+$tu%(vg>u}%BH(ah00{MH2AN=`u9S@6F%eoQ7x91Pi`-|6>N;_Bu)c0nYuI-$x%&z#py{U$#zhaB;#rHMLp!b7$=E=HeyZ&Ee<o?SaRatzeAb#z3+HR?ujFIx-Tb?!Q51%d9qgEmOiEn6q*JqXM3F~aKNm8EX+CJVvNA}2Z>!uRlximws=f6DPLB~ss_`#m1#P^;~CFujn)wdqclIvLOMh(3#yzu>GDQ9Vq9yk9Usc-P(cc;kb2_C)gJ5*5G)3;@}`1Z(VIxlL@koL4Mm!Bo+NA;F=u-6{Z=U_Efh;OHkl6G?*me%%J{6Ku~rER(n?CYh^FK$$u9e-TeJ#}0;)tZa%lvtqm@3(%?@zC+8K2Ms`Gb|t1ck>S%x)uoYn|aR0Pw$UNZx_xX_Y2-+v*$?robDHvkLw4oJqyo2BE6fB9g*Jk{nK{Mi9f&m%rB>V!nyJ1qs@HuFRwH&tleJQDbE2NeCMb4!`i|1?VM%8>KlyAXEoQ2RX^4AtTPVlOz`_n;s<|fsq?O52VI{NZ4=*J_Z-$e=kR4sKd@q0`?$XM(CF~;<J%Aae5vm%TjXr~e5{|s^LN|R^<(pQ>-AGa{t>>LznhP<J6S-E$2xC!)pg$TWfR}`qQBNRy1$Hn@8aH?zVjTN*9|hs{l7hQyZGMn@9BDY;hsE4aH<|r-`66%zWBijY0t*@t!feJ-SSt9NRRIumutS1&prP-dj1V2E+@Wq>JNQR*lmr>Yx{6r@q;Bl&~+fk6j?WX_*VN#x(@7nq}OAOTZnI8c%;`kng5k`aCUSTKlXZ{s9q2Fr}okO+ee+ze3*CmvEy*;<Aw2kU;UP6<EM8b(%XebO1=D*hiLjbF}hBkX&~hZcA2E*bgy$RbDfi8j<(O%mbz|#bwr=H&s?Z}j%->^cicw!es`SU2iwgLE5GY|N1cAD@1NQ5?91|ZeK&t=R(SqyeO=$p-}Sv4Zfbq2WYm5smqyle-+)vLWPHy4SI1``eLmoQH{*i%^T-`<t{*#(D8K8+&Z7w5okwmyc0~RT<I|2v@A|%o<GS_oMI6`loys-Dcj_e4=fEXu%6Z4TcC_ZheTtv^6nmZevG*x2^ghK~@TmH%+p+b+ch_y#_eG?SEoVe}*AKKmp}u=R)t&pPqt7%S_rB~e?#sMM<+)DmeOxKMkF$dd7lzFv_q>DeuKxkI{oVBL`H}LwzB`YcnAVHJeE0kqk={LzMCKnmPbrTN-@iIZ*nIazl;0iazKDDx{b0&2Ve5cDqQ36<@ki7*c72GbueB;+xKDi})4TO`^S3f}k?ZBy=Q)?oh5511a~c;2^JAaqEYjyW{)xR7y==U>e&l#_BGSi>|A_Rl<89JdE$780>R;6H?|m{)?=#%zRQvQfm2-W!=2JYIT%Y^DZzazG{NoEO4x7L9yX!};53V1%KDd7De0R@xk@?fkPDK8(^^M3s(vMtEtlW#lk6h1PKXTo6{m6CO^&{79Z$$p?xb;S)cYQnJxNiCFh~vht^ZAY}jz4Z==OcdP`P7a`ADcgZ<oVP)|D^b_&sWdu^VMLw^P0c=Jhr|*k9BTe()@X@>+oFHSKx}Kcc1G9^trB+yv!2${fT$={Z!rKTcln+`-tye&$#2k_1)_k*Y`%Gx7KL?dLz=izQ4{S@vRs2_5R4;^do7%*Y1k%pWH*wkMB3s_izVlE|qd}o#15A_XWOl4VT6rhi-XX-yMgs^8();&q2mXr0=-b{}K7emOmo@NZ%djk@?4te>eXNUx@F%H*v1&dy~MXVVXbhS^NX_J&W_jqNVZ2k6W)GzPsL9`?-(6ch^bRw>pOB<CfowIU>IMzS5U0qr7+XJ-@5@Z_@i^XM(;@bhh<bCh1uB-1<iPZhc+fT@NGEyS|&=er=fe)}iMo<on{!Wgm&Z*b2?R%wTPw<QwHW%3ora=99a)URPXgrtf`5Us@KwzV2}Y`0n}0ZJ$6ydbd2WKIbDhz5lyJ`hK4GeRfTK-{-5BM11%Cp#QSIA9TjOs_A*3=uFf1iB`X~x{s#PKpp>6s_OlIry9${`itW_e{a|H?=Lzj`46tD`=FY<q5EHQKb3Y1EKDQssh!Vzi|@Wy_48ge&=Q~bs?H{TuNu5POY^yXO7ANZjo0ThlMagSzPELD>U&$~_yh3+JH7fGqpx1aI?WQUl;aK4=Q+M)Rpol#YE@qR;L{U&zWYq~jd=TY*YpXmYCGpFtIvxD&Q(89R_be)8ZPhU11a{1?<>$wpKny0EBk?b#b?WVLd!Q-(g(b`bRSsP4XeVBdqnd0pFJqP(=CgvOZKCz((l1h$21?_n>)NWcUs@l^wkDw`y5ZK>*P;)SIg)3-qQ8$$D>;Q-QC5HeUJZ}zQ^}A?<u}-(1*HD<8tLqQvQ|!@x4##Nxi%!QtLjS^1o~PcVZ;Hw_I7-7iFKWB=4)8K4)|v!ns+xZ)|Tp@qI^Xao@31-~0bMQ~Y4Me7c`uOgU}OWvBJM_d#9H10NKZeJS3dcX-b~NcTllzVfZ)^X!rM?z-V^r~4f2lg}v6e9b?~(S2s)ntUUl-Te}cbiYI(e^c?jnK|E8?X1^D{_*Ow@4{i<MWE6G@q<g#>$qyQNcV>fUM#*p(c3!TzwIsShV^8n`0l<A`y%@~hHlmTGo{n#z|YzD_317x=a%<$-i;Zr`}0oh7vJ4a5@0`xeNz3{{UjgieiFM<(zW8VU&Z@6`&H7sBEG-;M7@4UJ5buwpQE_=!P<@<cgRTHr?|U>`0jofKl@?qz11}z_Rlyub^lE8mHOhl`)~p^bRUlOs`~Ce9A^Oga4Iy?a<ZStF2{bJM?Uf0{Xc$({XdmDYB||2WS`OfLcXkB#CP`>IqWZT-s_`2`;mg~exy6Y)n{LmeNFc@xxTxv$y%fPnw*Q1#CP{o`KRc9DsQS~TK-YP*f;Vi_1doavoFifzAR_$PHoSRGpax7zP4wjW9qZ-%R5Z>eOXg4=yBO67G$58^Ypf+pK(Xm)og8sOS>(2sO4wBS&;o^R@G;kPtKY8oOW6XxlXg%CtWAyWIvm=Lie+I%O@8<*l?z{=l#_>PWGl1-|2EfpZ{F^THnjRcuV|1k~aFhWks~CCr;zHH6QlT`P=C}I%j=J_1SmlFQxnL0tqT;{_NAUljuG@|DD>J{z*Q4j(wxC?o%v1SbTTCU%=h(cWaE+EBjp?Co3|_c_h$yoaWDdLTi=oC-ilis`)heRiE?EyP*3-`+TGM^c<t>c3<5$YwrzeeKQQ!^{wYx9p|O5iSIjlRFAt^_s2S)ys}=(-?|t3a@T7=o_|w(@1ZR^uG*xNcC*H165sd1E**z2bl<G~;$!uHJF4UD*bv<(87TX$q<d$jKF@iuPM^R1)LVStrj*)Wi|goq)*Um&cMhzRe0;x*ko7j`>=WOgTJyIaC)D%Enai3_spgu0Vcq}iWPKsNoxZQW$7!zTQ|Cpw4dRbwA9zmoW50b^e5Y3}ZO<_U<hb^QQ{wv@2DF?jZRy`YpEKfnGuPLAD&LfL@V)i7=0D<wmh(g_Jx`5D{GIsoFRA}iIvrOT+le2{Ih_44jr4xU?l1dL?W#L;9yRMC_anilA8wN47Sj6#|FucdZvM>Y)jxk*_hI^uX}kUWyZC{ae478$?Rq^huH$A&pYc`g_lh}npJe$l>L<t``TG*=(*1isuTg(iVm*&%jn?tsX|4Fylz()cAEx`>{iBo1`&aAvWqohX`1H2EBYv><5G_wkK{@{h?>ycn<!oGA>qS2X7yKyu&#X6->vc#j?XO_3*YrJl|Eqf5Y4d2^uG(S$O2PVj+Oc-|EX%~JR+QDIMf`uFkWZ7j`tpCG(7x#Z*FRAxS*qy&^`9uL4V7V}85ZbwaMe&W2}NI`NxbijevUSQ-!fgp@2bM?cSdueS>Xbq_#_k`pvPgO-QxMX@K%Q6vrx1l4A&(L7elMV#o)KmlJMJbezY2#A1*@}ZiIdcH-dYhE8rgRVZ!ir^cVO#oZF*X*rRO1@Mv@@JQ`j}7(Rt=fltAg(VyVU@FjFBd<p)6FuVwz1}}oUqDA1Y@V}OZ;j`#DOWB0sP3TH^C4IJuFx(ui3pa;zqs8Fda2E7!I18MCFq{d^4`+h2p=ID~a4EDATncWA_JEth$I!#@VfytLVfZFtIHO0^^l?VQ@I-VpJP|&Iu7r=l*U(e&Df;*tVfYSV_%?b8z779@{s8|0|AH=pe}NaEUEu|Aa@352<a{=Knz3;fJ`Ha~H^H0e?~R1v`e<&rKAaiN0%wL(q8Z?naB{-%8)zo@4LA*&4Ne1l(NeG%u7fs(>%fQ5WAHKh{t#jK24OgjN7amjG=$;l=tOur{5yIKK1P54P8hz2-huDI{~-)NMsLH9;rr+x@O}6%^cVOq_$0ajJ_*-Dlf(7kGmH;24$csU7or>Cjr8|I!f;+RGn^NG9Zd<p4ktvD!wF&c&u{|t4LAY(3YrFf1%4Ct!f(QP&^mA)cr|(mK1AQICJg^U7>@F&nsE?C7+#D{ho{ruiwVQm(R=W9_!;^i_!;~HeGI>VpA&}vLGQ!=z)#V?;HU6S^dx)}o{83jXTsMkRWlB*5r(^?3*m+Ix8WqAcr6rZ3BwuDbZ|yE2l@`218$72fg8gI(DU#C_yS=#nMd_akFp8FqtH39(ev;qcs=?jydM4y{Tu!bzJlI@ufRd{1{{PhqQAly;Z5jlcoRG%6tAIq(AjVvxC>$UXY^P2XZS991HKDCL~p?l;YaA-@FVyMVfX?1C;R}uik^qB!t>EN@O(Hm`X-zj{+&KFefc|Kcon(^UIphv-+}YNsnK+BYB(AC8k`JHgeHNFCWaHi9`se%11CjO!Aap1XdyTSoHG<{(SB$lcp2INEd)1!v!kit>~MPYRX9Byg(ij*Q@1EIEgS{Ek7k75hs&cm;PP-ov@zTe9)uo%2f-%@!@r^z;0w&-U-@kK2|5ZkVYma{dbk6;5d95a2=7C$!294sXb?UGe~(^-zlV3Do8aB>5_AZ>1g;xzKG!7-|HslWeA&`4{F|j=_zIc_HevWG+66Z2v(cG+HvUY$|Jf6_wi~{Q-u1+t3k*L+A9~`>9fsZWi{a<!BTwA<$nXpFi6`!yW%wETz!P_lGkhJr>WMoi8eWXf_r#q;4M(A=J#pt>!{+>K)T|Ni`P%Smbd?o%PB)wf&1c134;X$EO>M<pKNx-mO=iViZx~L1CW4K6thj3x!xoy<iu*I15KUplUH=$<9nERQT`w8VYsIY>?)8=7?(}<i`o25<RiZ89#b`g+U0>X>w2ZNK89j+EgHOU^&<5}rxE`7vt_N2_)5DeE578*t==<=DP-Be`#n*)4Zs?bAH@F?z9&QI$MXSM8;ZkTxxD=cTO$!^f;7stVgyFv}4Z|-i4a2GUJ}sOIE`gSWOHz&!gyHIFd$>CM1^OlY1>7GU5BG;BpfliRp(3>kMN7hPG#Ud(!-LTw@L+fx`V~A5UXCt>jXLmhcsKeZyc_<RFno$I`~zWl2kO8M$Jjv_UV?rFFM-FRL*TLSP&5V}3U@(U!Cm0iXft?0C}xKuKp37y7#>9!9zhr$O&Fd-7@m(Vfak;C5QZ0_0eBHS6P*RmgomM{;9;;I9Rd5{;pk|1I6N1f1J8vQqx0eUlyxy-cspTu9l8i!2hTuf!ZY9j=rDKy+!gi1UEzV~aCjg*51k9ogV&>r;l-47Jz;n!Vfb5g9sDgk6`cW3g}+1xz+b|h(XMc3xIa1&?hj8x=fTt94d{A!J!RcM82+9xycPWx-U?4ar@~X<-sqQbZ@4|$8Ey~vLHomf;OXczcsjfd-2iW(tlQ9o@IgLrMz_M7;fd%Jcp}^r?G5*Y+oA2@c5pAW58Ml$giePi!CTO6uv^wGgyExv;eF_4cpp3god{2WJEA?|j&KXK9oz!$g!Y0v!IRNR@ML&Dx&_`sS@)wy;3ItAgYJX(z+a;i;IH8hXh*mM>_c0?KKKi?6Z{1{9-R!2hxelUVYjS?zYU%9_J+bikH8MRA3X!_hmWFX;iK?r!te$34157ThaQ2?!N<|P@NxJ6`Yn6_UWYpHI(QGdAKn8WM32HpDeFPP@Q>&P_(%8zdJaATA4ZSEhvA**0eC085nTswgufvSZ$tOM+u&X3LHHo$+eH}Ofu4YOz}wNo@OF3uVR#L?6W&Sr))0nQq2Iu(;1z`7wdgi@ExZ}s1@EGKhW`nT#Y7>!hd#8F{|d$3P~1Tuz|TVA38hQtQOyFE3q|Qrv__l314Gd>6l2k$@K|^fItCsWis7N~qkZ9;q4*#aWeLMY3B&ma!`TSK=?TML!tmRK;r9r`WeCGH2*V8s!=Dm{TM>poBMdi0Yr+lTMug!H(X#M|aDKEXoF9H2%?G~@Cq%Qs3E`)fYI@j&;RJYII02jjeH%^z=SAOx^TO|=W#ISW`e+TfKHLdy0C$4Bqo2av;Q?qXcmUi3{S58_N23klhO~7wVYoSA*hW8uZ8$rcAASopbH#+=M0ok({Pag6!myc3uhSpyyn4vo`U}2`nlyLOr}%g2vj?c@CwCq`U@ks`J$z@<c<9p<um{e9=JmwQTchO&!==%@a9;YgG-0?ITHg~l&y5Zw4EIFq!}aO!o`m6{Xm@xhJO&-$iCY(pjw1{YM+d+I7ze`%!+p_cIGVn9*A$~|(dKYlxI(<Xx6ul41=1LPg>mtiv2hQ+Pai)*@4$&Y+Gkl&(+7sj(+57ZHQb9f9fppDhrwT=li(4wQ9slVx1eqxQI{OlBL`juv@P70-}s3Z@$wwO@g~9Uar?kV2f<&#!_eOG%HNy%8I6fo*Iv}WHSD%S3~aP9?1Rgr72~y~(R4)lc<o#fHd+AA3MWS2@Wl0%(L3~^VYeUOfQ=@BO&Gq9K94sR?lV5_!R|PD4jWDCQGN`Y@ntk+ys`EQefSn$4m4%F{xtdyni75oE<_m4g(ih_!5L6frVM;GoD(&5%Sjk6h`s?Ago~jC;9_tkv?5#yu7x&+Yr##>7`O@iIocck9BzXSg4@6?(LQiX_!Gi#XLJN?v>)6VZt97fS4|1SRnU*%k7)NQgyG_7A-FhP8O;UfqTMT_IpLhNZ)LO?T#R<CjMjo{(O#9&&*9H$m&#~MxFu~-nJ`=%?F@IO&b0}{AEQ;^D%9;`v@-l>X#Cs`#k(HWIv!;ch6kgwV56&Hqf6nzaDXtp%%j)CM&0XV!)wr`p1A93!yC}mp15mr!|t`ZVfX!u;f3fdPu%+&!yV8%p1AirhM!PBQ&0DOkYV?ok>QJk;Y;YB@Fh4%7`}y?_PWJq!<lKr!Ek1{BN~7^!gC43QwYN&3B!}oW$<KpUc9!RM;Km?u7#Jw-=Uk~-RSq|X4vQsPux2!!-vrA@OJvcaLrKND~94D!f*++99#k}f)<C1z=a9J?-7Q}qUGSSa0Rp?Tmi0y)`V-pHu@24!$r{&a8dYOv<UnzTo5e`7pANQ3B#q)vT$j*GFkzy3|B#G!Bybegy9;f4cCA_HfgGP5=15ZfBmnt<NnMwgcbHb){gvT`1aQLzg!Z^D|WMM?P`h5dtfU;=s)xDyNcN<W&IENE#&0'

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
