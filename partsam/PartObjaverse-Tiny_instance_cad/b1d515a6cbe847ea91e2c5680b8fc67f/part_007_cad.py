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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_007.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_007.stl', 'source_sha256': 'c3f05875ba683c8bb6ce808a43e432860899ff9efa11e90f33d3416b753f9749', 'input_faces': 924, 'input_vertices': 557, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.3832411766052246, 2.3971121311187744, -3.3409128189086914], [2.5997390747070312, 13.591876029968262, 2.512822389602661]]}
GEOMETRY_BASE85 = 'c$}qu1$0!&^X{GCK@uRi4Nd}!1X*BN7@S~>+aeR3#R&unfr~6G1ZT0u23<7xCJ<zBclW{F5@hk$UEg>Ancwfccg{QSaZa7;`flCoy4BUyGO*jIUXr8%2L9wVKIYqzG`5UkXi8%Q7~x$84D8XVOIYzf{f62Mf5G)1i_dJ>yg{SZHY41KDBQVASf>GnE7}WJ>RP^VF?->zeFqF25Zb3h-vOPwXuMWvudpr(59=P<uZxn4lr8&XF?;F2V)jV;|KlHD<$~MepTw=WV|V`K4$c3KyShj79G`sz-!>KakaHI`Ztwg_a3f?Z@TDJai+;#!!QF4qB-6P2pO>QVFzyQOc|A>V=M&F4!Q0&y+)S}jaL<J^H#Kgwzb3fzV<W+hFQu<(-2M0>{Ha_=`gJXRb4T>woEO}6@Iq4YCt}?`jhmCt!v1PM`1AL!OVaQ4WAHy+KhZaugsm66^I`aZw~^q^;t9tDzqSwkzJHrU@Zs~^;!lDb_P-q#f9yYZKP&y71@4$wMQ~48a`|5OBH+$X$Hk7jVZB(<pAv_DqvJ*27(4a4=oi}#`-j_$zTvtSD){kO*h%^Xcs2LZDw@w;54`4a#I0`3bn!oU9lp2G9QfJ!+HtXSVmbQ#XkZ+B|8`3BGXOWPb%Xx_84n45cme#Wn^f$ZIpg>0ejV*+Vtg+?h5u__+?VfaISp}mdP?GHHV-_c^<5WDj8{Yr*lE7zAIYm4L#SUah1jX$#`r!Ahd(t>V!R#)ju!i21JG}EkJxdXD|Jrd@JB!BPe=y;r+z*yctAJ!zabcQcAeR*ardltg4^F!fSp`_U8y4P0XHI3h(Gr2rsR)%Kx@S9-;S{3*Jq>H>Chbboh67v&fr*y&+ewc&lZP%|B2g0e=%^UUk>E0?b}(wP2x9}%J`a(QydpNv2_u*w&gJHB|Tx<AJ^L2@bheK>DO#`dWC%N^IFiKI2ZZ$)4@22XGl%N`Rh*D>Agqhi>H2d#Ag%Y@BTUUEz!?k75<mcAb#3o%1WNN;vI-v{}b^4Y{V6@^PnQeC4Mf(vEHSJ61PGX;7_gqjC<djH$=aDdGy<*m*B4FFQuLs152ad7T+)~pOf4ZJH3HB7fgbkcfF44?{!WJ23~Nb#KE0&<qphi;P&mO5udoRhb4brl|;XL_aOfZHkCLy;sVjH^FF?-!=vjG&)~wazr7jy{XOEOjLU{J&~GzE;_10l`)`fg7Z|XgmH7}e?IGs-SDVD4;0CepUOV@K);Gic72LgKR7&Z$Y5B+E&rfd!H)bH;93TC!O24h23vLc?jrvx&{w={rJOZ931@i5|Ut0uU_Yih64@F+p$}D+h{%{BQfB@;&Xqy-FF2p0a(_IjDqH4>0F=yNs+);fE@GE&H$hZUnH}}lOe3^1n>X>=@D(r76fV%W^^R0p}I3u_{<Ok&8l?#*PdoLVAd`gbPcoodQTJ(<qH>N!neaGzYGG9C`kHVje0n)D{*RN;9PN@U1Utk~d=jj$1N3)w7aXvf<<9_JoMX{4-2gk)PmH2a_spOk^CI)t1PD0!gmhY1Mp8?zmMqPFLN1c~E388+He=uIt6439+Xz2Ia2>+k1*e`W2^J4hZus`(E-@AZ%vH<ZcG6ZorIC-1scbX@-r(ROj)k`;IK03!w0N#GP;I7y%G9S&}!0peoVm|KcxL^DX`~&@tDhk{z_(bey_#OS`tc<vo>?e8UtP~0R9g-ve{i@6Sb*CN*JLx8KKhRd@ow<Jq`rXxnc9MD|ubhKmfB#Ixv-030;!ml*(2sqOe7HJfo8)c2K8Ra|1mF+9u9NX<{2S~n?|^yqIi1vPb8C0x?f62-&#r!}1aHv|c`^e1y6<(ICiun1&>wUNaY)xk_AN%?2CzSVJN%DmBjf1)R1f}q84UaF(=C<nO<NcGC3_$rifoj;a$l&9euqV}PTrS1an`MdxK+7|cn-)Z`Q}{jfIm}wu@5PAN!CYqIS1$a1k{uIt;CKeunO##^p*MR9vJXU{12;ud~Uf8@kx8`n)oxUH2hzE6?u56{Tab41tR{#A0e-{W!WSBR>%*3?thVfomX}ol=-zY5BfcTeU#%`KdGzEqB)Q!7nvug6R>_=$Oiq;AjI>g=Z4@lGQpo3{jfjz@sQL>qgqDzb1OI2g~0F&g4@%>e%kJ+C*ysQ=av0|U%)zUe);FH*w5$-|5xP0JnC8Nj^JHVqTk0h)D6E``vkXrG(>;%cf{@Sz)O;!-ToEa?6d~^Rr{^mvY#pb2Kpg?!_U^ErS2K0UJ33lHUfU$-Y0d*8S`9lqfk%8`PLWd*IDS9;PzJwWgMM7YhA{;KNj3GXd2e#%YmoG{)b1fpQIe}p{Id$YV#fVIeCfHF;9=$vafcex-Gclm-)!s98Gsg{#3YyehW>(xCEw>JaIg~4Eyuq;QxXw5`RzUOYlGU9Oy5<Ci&w`e*yUBB=DzLr4cf}J{&`Q8kGQ^X_eGB*Rlifvo!3x?_N0}`uFw;?i%98IA%;P^V(G(xMR<+ursfh?DrhAVi2F`PVh6vwo&pSd>!mB{tiEPR+M<!U#^9p*P{iumsl<SIM=O$od<=HhmB54y>gUW2|Ghh!_Mwem&Koo3*gVP2;jd~l6-J{n2xwD;=U!I*AW@V^%K!=xk%W55sy6FF&_G*lgs#;ArVrC-J!q3e$}$b+sJ)V=iLP&q5moj`0=K49x<~Iga3KXp$?~wa7#Xf4Tb*?J3+s8mJKrBXAXj$iEFt&=8^9*tM&(erwQx?b;mkBu^;S*2C)7-i;{f!(3yF)7x5q0ZMwwgMhDnQxQ+cl#fNg9GDCrz{d?ma_xEEtA9>QWN1oi8kNMSNv(z^;pbg@7_%8CqC#S^Cb*BmNr+wjnrjZBbyQ%=US6GBPd~~gxU!2Dpz|YV35eNUE7{N1DLcSG&pT>+-Qa>GsE5M&89q?TZYRP%WHLo1v;M*Vgpgpoani0UA<wqhu{R%{gKdXY#@26<=>w8GfM~=qD5r@GCU?)0muFS{CK;~y4>`W`+6#E8nNByJFe;pq#@tl_r{>02KB=J16caQYj)(>`84TJv0U|IJ)v(rL9)jph$PPN8<K3^L6^UFNwS1r0*_OY3gqu(*uj~O!_$o|byCJExaw=VMe<ZKxicWWE^O*#YPGW?R%Pe-#C-^E`W`nBIFg8je!so<{Kuc3eNo76FT?Q?=V+fBv2!R4Wn53Ykp1$Si541Yq?E|+>Ze2?IsD9lqcw2Mdj{bw8c4L^vwx4*0G+nv`|!p{0p$n)YA_KJM{FZkoP3h|jcR_cH=^;q~b>?rE?h>vpaaK#OSevL0!e~acm!+nn6#viX?r(J@qkM>a=1b06l4F7jeo+fgaHt;972IkA!;g7`b<_gg7*%fhEu~O=x<EP@#kN5-gV$E_{N6g;}A`U4Q!~UwXQ$#+P6Z(BKi=U=rrkr<-6gl8$LDUUr2RG_u20!RW&PF^N_1-DpyVeH#16lzem2rpk>q+<~agMnFfBp!^IlAX-!Hq2op}%aOoJZU*?n8e}CY(D`e~|Nz>+TKcZ~ufme06fI*a-q|*8U)Q?wQ?N&ZnLXmj!nhdxh_P95+YCsm(dT9eE0gzN2=Dhf)tO#|Z9RihAWbu^#K)O5pB8udx45zhCx&W}A7y4{t|&zCDxib!DC<xNBSt{8{s><byeCH1IA_$mbQuWqmQ0jKp`PxC%cz&%G;l+vkKo`w>r9s)|yF9W@fZ%JZ3<5r=I!H@UX$6x^J94fz%yD0yWBZV=o!GamW#Ztw&7{?s!C_q>h3KJCjRtk>TL3+@a|Sy;Zyr#|k-&iy91{kLhz^VlP&L_bwW;LA1^6o1YwohRQrB@}-C5`w(imRa)FJ-a#lDYguCcvph#(;QW50l)GF^RZq<xfk**wF~abQU!MWhRb=!Gc6DNAK6;sY*ftnNaB+=0Cs-G{h?9vcg)`jX<?@c?3<fDOWih(J^LchdsoN!e&{IoV4e*R1UJh6h`e3gPUev@{SffS6Jfvfamjy2kBx%c<K6)OnqJN+uJdD|-(v>$jSZbrXFP2Nq2HmXZ|3y=CnWB>8VT+mogU-0YKr8ubIvcY-{=|QT)4KJ$L-td1OI*l`Ew>^l*B){_7}u$F2480W88-nED8Omnc-)Flv8BhUHST1`YDv&SMbF?a^LH$<`LX8qqFpDZxSW-+!J#a_`F4!r!l#Airqd3J|mxV!v3Vt#qvEZR}1cVGz;T+ppC3|u9o3~yCP0v9~)I%^50C-7y4<j-!@Y}#Qj)-7J{3Tn!|ovNvRt~Scu^6jpcwJdmk<GrXs)xuK*sKQ|@8hz3zV!KdW=U6rBY7jbYaXHy8gb`R{JF=e2y-tgC|CJGRAs!1;8l_&sP3@YXSsKaOAO%6+fB=OV!!vo=ZGoCW+7ByP4y!QFStV7y9R94~g>3;`ZB6ZtUqFYMo5l!N`6xx~Knq_3<y9{(KhKLGX3eeSr-BWI?YA5ph!i~nZS5!tuczZ@0Z6^3=qaLtl&as3zr+%X#8RkF#SBFFzDxVy$N;Ct<I|7I2+E4U+D8S%%gwElqjbFGr#p5pKEy{m4;>+iKkXM_EV+t9DWN6y90%K`8+%}?+@PlBvF?#t-}xBr2AW_RPlCq>Tq^k3n}Ccz(L`b2r(en)V3ujKHjV<%asT$N%3_e7<a`e5Fv`bO{+^P%7T3dVilBN;EJy|3VAmJ=M8)UyP?&=UHd45$y~LwAcGiweP?rU$V<FP>cbb*{_`JDL3@4vsZPUr8N!dh&z#8+IJ_7hlHy|F0;)-FL5IUNrqv^3e4qH}qXQp#M){*{{0tq!8TRe}VMtSr#Sw_B`9)i=E)pn2&zz<vi$I*9v&fv4~s7O<1RThY0S7o(bH)@GKdx3i0p6-Y^gPHTKUC|39u3+z~Jf`Wx@MME`kn!JQeOKtFba;LfH^VJCbS{3-LpCh7Nn>|4<<5DmOe3Ax9!XCE!NJqo`o8Rfsq?;xJo$hXMPUdZRBb0ogb@a%#++Sf(CooVt>{5<0;xVw8K?4P=a`?SB}6C|EdgD|g)+(LhkJ%ZbPabIW5eX?2X`$r3IMl{CvuGuB`8_tlS(0|zv_Rp`9dFokMLvT;reAMU0Oa2vq_5`5cIt^hbZK&kAbJfmx)c-*26MD}^zOG*?xP9k(=nr(_9^h3y!3|$`0m-Y-$?v3|{80^dhH$*xmnVz<)z`@P>0{t$kqMh*yncTqxUsDi><^hQ`*~-&HG(_l4h0??yi)u)8ISrmsUz$-Pc0Pv@YjMnE3B69b-nMJ%B{OE>WBNn$`i4F7_|lafVQawcNCwE_*boq`R_^p81YXjc09}4eU<uLWbq@+uTZQz7u$Z3I^VFi+ymKbSCF{bU)RQZ@5u@L)&#_-zC-fCQ(~vgZ^x2o>DNAHGwSl|-7-JSs71glcENu7$P%eH9<wd_&2$$2<PDd7fh+jC*msw?_f7DOVRC+THYp&u>&Dm*g0HKIbM2OS*k?BDEAevpw>&EPhw{PCzaPF4{eX;84~!jY@Lkn?kT)Z9<NoYs4Z)p%9Kn9KW|l+9=XJ>c#?_=QIObiKdTge=jClHu$NgaU5rW$Tn*m>BV7<8(F8Sz+yaNB%9l?I(YEs!Zc|v!JzFBgIueM{{&WL<ZTMqik44k7{n)qEMv{8QXzeFRPA08#axiBV6KEZP@7W<y9F<a#Ml?c1U^XCOp$BZTM8^oWu&G_D|osgGlN6C6_kMZP@JiIeQ&WT3VV{7C)&Rq~YX6ofwx9){V{u*twh`#$LQ}(?^*OoXJ7OI1BIe!}SJV`rQ4;?i#iXGSKdDstqe>PwInKLxE;AxA$693O^pDfR_782aZzaMqyz?nf}zi$q~9aAe}|B)rQzxco5FzgJui1YC8BbLbcA9Wy}joU~*7-y5Ml=)h$q2SK6d*2IQ@56e*4?n`ZbMBTpYqTgIt#PyRL99E;7fU{vUmsw9bg31-cY3Von@yTve_F8s?gxHrFYAHfNERpddm;X2v+DS+&|b11caIH__&DnSjD1p;4RTNKt~eEW^=>@kAJpZT^gAjo>?f4LI+}l};Er-X2=1;nKybr9J$`q3cvbAU5C4mGvFt*@otfIgj!zw|yHR~*A8j0OE%9`J=`G{vK7L1VR}#0(Ye(z{*l(Cxe(!aTtcdZNzeM~ryN(jvanyzHU0V@xJGkf!>USLM5B-4iTh{A>n>%J8&R<?gUGnrCBfmR21A54KnW47Vg2(ybzG_F-ykh5>ANF%AtKh!>>u1ro?}?Q>vBx(M-2H1Q)SsgtrT%!LnhI{ev<CGm^$472cBH}YLZ?%pZak~@5qTMe`^zLlF~4>VkUD5o-U|I*Bav^9^2<76cg5p8`l+$Z7xV4|*`M3*_~Q49mG1?&ml-Vgey&ah1b1Y*EAeq|y8c}7`eX6C*|w6HzpI|ZpOo(fH?#i=KaYP!{SPwb9>{e!e?HN-yRh#sYv8=QFem2qthQJmZ#EX(er-JR=TR!`7awlHJ>~O#SbvLlMV@qABKHmMB2^IQfpZbJw!!$lG+8^TSI&_Kaqj(m@GA0f3G+WE_8U7dL4VREvE%txROX|7*t=`Uw`5qy1LtEO++v^HSGoF>N8b8vk#YBwdWCzeBgkjF&pF^T+TnMPUB957x4k0vosE|WZq9xvarR`Yi@J1ZBlL5Q#`*X5JnXY`oE6;Dd5rjJ9Io<0{P;Njrq~&D6nRxYQtUgnzmt1P<N98)Zzi;ndE{u9U+%5dc^mN$PAYZVIqNun-|*jq`t!Ug=4qy;a<At4g!8zkdIg+MVp<694y^<~ixk27o9i&{;fgN9dU~XyoR3WZBe2uR7j|~mMxJbO;C?ql2*!89k2r^{pMd+tki8hMksGAGxjP>d++H5{pUw*(u|DSf>8^Zln-lQ=>#Vn^zk~0I{_JF^WA(p?KgPHBf;&FVMm*QHd?L6b_kH03yHT$KTB8o{&nvjw-5u-Zh^%k%J*x$GL>HHMdP-M7z0JKxaQkRC@?>0Hskfe54+QrVTL}GCm1W=Vj(7t*1(9#|7(c}Sxc>v`CwLIPci>aOJs<lEZp_YsI#4(3RmAg!;EsfOSRYTX#l2H}Hn|UTuRer2^QtE5|604?&PP>YzxOKC$@)VC_q41ec3fXlK9x9!PZQjHR06o)3R%aU>*l~tcqjCm<1)tU$a2^j`UH7$rGxC3+@<#6e$M?7<8mWf_I2jfQF7m7d@hT+`b%Ea`GBK>J9C{x9rjNyb=aI6FSzUSE7XBc1Cjri>pYfzTXB3>Y?rurCY6zKw)c#bxY^ea!+z;*cfsAa|3rSaS%`IKY?$DlV{<WoKacq&_Roh4?u;#!PwWS;!#Wr`0s1Xb&z&JTfV<xbZXQAXH=OI?|CcY&_m2iXc(35bn4(XmpN!eCuded}_j^CA5Zu_b1^!H{kMl!B`DdaZTOZ%sCOf{XP$S^BhKTd7^D^#6y^eyL?RrR^^!yTxdHwZY!CiB{!hXd;s2lCGK9}!Z*aCHOYly_t-ER4F%!3-(_eSr)IL5vb+-Ol3_59@)?8oN!m%8O_^$_~*3NlV+j*Y-mZbF_I173*#Ybwb(+x}N8880JAGT4c_BDiOHSIpB=sW7fDu|7L}OB5CTE*+5n%~Ap%F*s24Fa9X!5Xadd!R_}aN#1(87smOqP*3OwV%!}+-<JHhKUjis8?j8{<|>m8_2M(e%@x^P^43xN9)3UFb`txA-LnNZvrL6N@;vkp@5K1Vbb|dBhU^nvU4|fTt;<WD@dPCk-2Au_`?Q$CIG1)VfOE#dQK$oxj>_MkG<OEU&fq8Te_@>57nw$J>_fli%O~So%Z_`JLnVL@<Ni75s^~ilmW7=G*^oaq9>}_DuUS`cN5Ew4H>yO*e0Dt#g`Y)kVSO1qU&hIJ+Ffw_yfT>At{9w$yUm3EZ{txnCi%<Xi!hd-5Zv<@)=e|?3&x}W8Tj*O1B_SKf>M9%KRg9~{|5Z;^MjlN?K9uQe(go*xA-~a?UZ1-$1>{=gPm2&B>rZCQ*h71yNGAGP0%0RU2w<5<cNRWw8;D9dj&V*l1e_9twy50PX+FrTN(9yGwvH*hmJu1<yy@5N7?ZEj^jG+)lTL@+;WVN_&CSk5!@YA3;IQl%kM`<k9gQWI7{-!xRDFz(9-W=r`%%XVV{q$Q4f7&-E*Z%CVo1OPnUD4c`T#g&dPZ)zh3+y{yRGa0DqJU-<7$%+yi^w=f--z{3ppD$KY_>n>@$^{blV?H>!2U?@AT0{(J0sF|U&jKt3D2VCVcU_&N8n?1LS3A_RArcq{geF-_#$=qx)8_InpbK5uR!`%=fnXsqW`aNaR|I^pkmW{88G!0-63*$X8P9a+zy-|5dVj(MBP{?%3513P(A;2e78%w5#eyMo)hPK3Ur+)Jq^v9Do2^hd1k({A8?Z{%mh`N}%f$y^6ze2tzq`EGL$?p2I^k@!93-(=WF_}7uT<oKnm+((!l%Lr~CHUx1VSQYDfzRH3-$6|ltYVt+ujALCD?03%QK|EhB!~E@874Z(ukG#6SMfT<PuN}~Ds)dO2KV9d__~z>h`-hGN37(J+f4`#sVCaVol6)|h#i3577zX>*T4Vi9Qy=$wFUJaQ<h+D@D|QF_q1EG||MNWTL$cM!{lN7Zupg9wx|jQ+)N{w4d5FV`Y&hRl+lqZg|25FR>?`BtSg}L)@%Gwr@c(Qi>dBLGxW_DZ1a`uZ=dP%1Sf9qff&QmO*sm6f#CQ*DAm=A%v$Uw&(e<P*c~*45xhnd;;Kqq#zl&bqPJ)|fwxLcIAA@<(YZ36x-H<=MXUM&nS!osUhMzDl&*J4C&vRlU?*C4&!MgTpsO(cc>y8NSXx>8N=9)1M=hE@l-l5JHf}Nrd@Voz^syN5&tcm^q%@f$S{ZLnM*ZGD#-#y3qGetA(o4Vt^$avCrnZ#|16LuW=urIoMM1Hq2*M<r1_NyZKW0t}15uUXZ-(!B2!1`D%JAUVBFa>tDl@Z(>c1*s@-7yyDp_Iu{pT}hvKOHYm;9jIbMa<s;eNczj-hlofAAE21JgEOAUO~S^7m1IjL_JvtU0Gj4f8A2#NvmYIUoQO){;cuEJpHmv&Y8w3Kiu<eJB{&Oehd5TvH5^!3_@Nl{EBgD94xqV>PnnbMqhi3?<^;{k>ycNjoW{lD(4obr@Y{f!XGhT{=O*ZZs*_-!CmLxV7=S(SnhE=*H#Pexw%~8?AWkD`ZWrrlY3~Ray7w?8DnIhV~q3@+>C;so=iLk`nD9@KBm0H&6(^l&Yw>@LjOtt_8~pz%kPPvcE97E+dl;PvuzgsUfi|Sg1c{~miRcc*Oqg#ec(CR8POj5^RNZjZ;Uz*I|m~%?xsuXw&%?g!5tmjqMp1h4*R8Y%l^@R3G>UnYl)1DJ57Dy9^9+A8|FhD=r&4lcamttXKYsd{gW-@@w-9!g81G_HROKEo@D{-w4aFiwQHor&CzVN;KuQvk^gm?%kLWQ&)H?a?-`d;{Bea(mV0~8!U(}#>EclzMh3~>|F@@K`U&-_G4A&!O~mhOh5rG58uin0J+s_Lo7>L|?(DZq{C6L_D*wK~^ZY*g9bF%OI_KiPug7!fcWH^Z{hV%@eE(0iKFjm1!x86|+2!{{*RJx0^mjBC_qUmHd`DfoYm@KE%X3XQes4Bv;P3Z)-qpl9Rrbo`J&pe3Up*Bo^fcj2QNz%b$_OyJhI;*zCk^U97XRP>lcyeK{;&SYQ-$C%|G)p_sgKPtIw<N-uH|19HK*K^)PZ<SJ_{i==kxNEE3#daa*U!?iuNd4N3P|^e71*N%U2bhWBUR5IpP}??NhWx(HU|r4^uQz(PVNhhf`jmXeGJz{0~Jl6pdD-2E-W7_7dV#sWX-GP{w9B`B27aIQ2%84^lLq{0}evL2O%g$J6cxMYG9gu>aA-#*mNZGaaw#jNf$1le}WOmv;72-ax(C<Qs_VnBG%#i`<IwJ=)q!e$OlRXBg)*lpnDDfOdw`-y!5f>344%^2N$0Ew^U7nGHG9jB;zfH-!3q*zWD67ed~cZOtpP-HNjHT+3}3qu&{W-zkq`Tl2x>1K4iEcf0XhrhC0_jmco@cO!4Zb~AoQEBf7ya%;9*@tX$od2hD6u@5VLLn!NK_Z8*!F$|jzxRz5ZUQkg1Vg)D%`e2US=XhzZ<^49ypPM$!vzwIteGrdvjKMg@XASu(wr{d+&EuQI2Y9{LhH^_%6JnZIR#b_+iP!VS)TzjJCE}GRSEg=fwl%LpY#ilrly%=a4%roDBQL<1=y(-jtcp<1!I)b0MsqFule7)}o!KaBTl=VUj@*jzD;w-tcD0<$2XRmBHD>#%`%=*hMXO1=y_Vmy#tUCV-J9gzvi9qxE%94*TXSt|prWdZ!pOB;jW*X34`X{E<5-oktxDO_v0^-q?`v$Cq6Lcjl61Qh?Jc9tfo$vN8I@m86i-5~<qzc9IYydmS?koMy%x4az3qJepyF3-;Fdj0UPiuvZEf=k<9mg&ey1<vVZ}wu)fHW2UxD;R%WgjJM4jqvYaa`G<y2ngiIqdvywrJ+n|YC&at6wU_--Mu=UElyQIwBd%b64<C-;_9&{j^qo0D=HQdVMFDJQ31e)gH)>%E-pGe5cad)np&8``&RuydQT#&!E0aZS3Ng8aLpv}~uP&zjQmJ2J5yz;*z?I}3RLpKCh-lyy4`xgT{u*^mn#$hCZzq}wT#&RKF_wl#liLtFEINK=SSp*)Xm&HIsbJA!Q|bJa;Xg6+CqctgtCw_VKBU6d_9Hxrw}w)VlrwuQN<v%t&7F5((9soRg-<g-p*&leCgiT9(QevD~6$Mb-qljQF>&L{c&JKNv+YzOsjv#t3BlFpw;HqZ`Y>lMY?P!lzO<<&k#S@UG9r`pCT+Bij7Kif!K`^mMuSkaG)Dky41((PXq^-$DN(O5;1<Q=JFJ@3J`#-kK1r0znm_ZCyOo-bzK*1URV1L^j^w#0d*+nRLyv*L#0-)zWrEAI`j`LA_8^Z7T9kwLw9zHeb#zC%p&1Vxt=Jth8>*d5|`yvFk+<!^jHf$apo_b>gpPSS0UqGKF)Yy7o*f;!goV{D(`d*3K~*nY}q9{S}Wc8R!^gC{9pVjdi0zXe&Vb=}tO%Qnb2Y>D;t2FK<Z@q(<q1^G<Bqiepd_j;{K$(nMUq}zuS?I!<3`ao<q+xlHyGju&ULayt~5!yWNCHqqDrKp~ww&eBMZm+0;4fR9whHST`PJ8kOZ0njdSJ6oNaKsCnM>&G+kzRd_<TuWt&K$mTgwN*E$2sJ4`R+){(-d`AG?ToiSG$IyT5Q+iv)>fe;k$MC&As@n7N6JRv){b>*6lyZy=AMvo|F%f&tZEGzi;M$jp0n{O=H^{$L+-aQuMc?O^S|^YgwNoC)jY#)O-ZnBN<Pt{zp)@_8)6Wx~=yoy6)=wtLw1dPv{z~*9cwb^?GoY+*-Ttsj0bB-y4u?`GTSteHWo<AGww<DSA!**h|*WpD5a^Xg9f*Zz;;I`pBfnpQPKqih>m7RaBH*%lQ@M(sw0_>XLLjMA0xsofZ8?uH`<8Iw=ZOG*;i~kZU<i(HKR4l71&vL{V-<`N_2$tms$TY(xGV+nTEKc~#2#9;c?FKt=V*wOp7!h117y%A@&Q>vkn|@Uo%bOV76Eeu~~GN>Fr%{4U$i6@6D^vw>^*y`t8NN-63>uH}-{^HcP}0O@uLJr7m;x}rVgT7IPC!STpOUW8**gji-$L1LO`Q4~mCkk1QK&O=_9IzhzplLztHM}DLAtsm)63Il(9$hDkIQ7c7@74;(5@*G9_zxb0^QCe~>*HLtUb`OysU_1}8AM5+A=YLaY4(R}&&7tmM@;Sr<*jHL|Etgf4j+l)+9iP>qUN7=iY$u_vL7s%~BxBnk*K%@2jp>8+{f+7SZAHfw#j>sWIYsjnITZ~j*K&j+ha!D-Se;zUISl01Hv_q*c@pNGUC&kKNM4SoojIcMtmIZ6X*qy$0CU93r%cR|OqBKW>|R(F%6Uk3um1Az*#za&07XN{wLD7EU*z8Mbn3M<Fi%=~y{DfqqRt}9Ye?G_ZDV^IpKI(a<+GG;8kl>@y~at)CD>ny|B`k8L5BWMSs6w#l5VF~)Xzwq)BVURke8(WQsjDWd}9Ci$+aBMcl7hD<dzLRzPg57Cp{vj`A3fVBXW&@puVmv&nfHtdTOAqd?tU&XHWUuTTka@J?7mA@_Nj<2tFS{u4OBCue0yxv~`Zp_ON}<NUUd-73EP>o;(BFZTYM`sROYNlxva~_G+g$5^HpM+VUg!^^)~-JrDJKZcJX5?ZxzM9=TON^fwnbFxQH6d~{pa2WyTFr`*d(oU7H@u1=lqeE%nMEjK4spxx%=mY%~a?$&#GY0t8o*UOj1^nWpB%b$512kYBn*^dvu#m7j@yCAM7)>;tgwKiDmNfF9LxmFp>D}!<x(idWyYdICyx-`_&?et#y>8Yc6I<|EU$;eujfjlE?N=C2eTJ~oh(|W1NtvVOLc4|^`Vw!wyiTj=aKC5A1KatNsTl4IS+EeaH-ky4Yu-%hf%Oef!EldM@4U@9o1JyRL2WdpE<=@EL7>WBEE$jVEA+`&W7b0GfawGDJ)X~0XQIwH9JHJ7<ix4kDS?{m<F%PGaDli{kDmt&|3b~eFDRNP-J9%@qXB(*1QRG_IwO!Xay?2Nw*Rrl(2WdBs{2=?%dFgLpt@HQFQ{A@q4rwXd_}w}Nl^D-<l-m*0?G}o9DC$eD<%WuWCij-h@x6v@H>9l|<PG^e+{<2HuW{CU+L?;Rv#q(_<JxIIgxpU1ddz-Ql#RR~zo{ahTY44QZ!-h?;|Anf)_dl4?APjF%R3a6=JQ(QS}wwGwtNYp9LjG9<u~<ZTR$sA9}AEdqOZEIZv4(}lm{7@2YO#Wl3dGU7^ik#V-?OA`g0zpBTvG12G#|uW@O;J&&YY7o;)4fsi|x2udRAu?aPz1ot)1!=1bX^vhG{2(K=^e7-(yLme?E0Z;ZseK4D=0;U?Fz-gDe1_m;IiJwNmwW&*jEH?X~db}U;O)ALI2NxG0*^Gw@&YhYfzrF_*$oIiQl)?BY0oB18PNz1&j&CHn{Y_Bx17y7}_KWw9|x!yPFJ(=FO^(P<7c3I|HWAd`hxxXpTCI6c`dXLqVwwtoA5_~T+-_1-}@6YvqZiaz9-VDm?=u=Vyd+?-`Q}G)%v)|3^SGTA0{VC+uzA_#A3n15WCib(#NSs&JzH&Oh-HO3<+Du13GLfgFZ!H<SrsVzEo=IN^k<Vm5DZOlDqMV&N&8Xju@?82ihTk-X@}FMv6q0W1IhmTaQ<0};ANpH*)4$%7d-C0$|0QcX8R=hk@{Ek1e!mI7v5A*GJ<i40-w))esPlu7m<vs)XVtH{r2PDDO$``_Zsb}{#+s0nJQ?>DNm*O0GgDG8J&k=L>Gnt3vF6q%%361@YR^(MnOw``6fLD3O}>;m#}rLfw4Pkc8x=(=8p!rQKGW^}d^eh0%UjsTVCs$|kL2_9)LBp2>T?0H1(XNU#san%P@c^8QrcNcd9v608ed`H-f17XmX{c)C2QGULR@3k-P1DiwQTD<Dt%vN-AO&6taHbj_oa=*J&Rt8^u3aG2NgnWtART&>n=>o7wE%Q;#(;%RJ59WEomX2X&-jc$6b`Kk>6wc9_7dE;~v}Az1s!8yP9_PvTc2{j>%^7zm3G&`@%@9$uAg-*W@pZ#P#MixyMMn<J0mTj)&$4ykrmi*++aIW!=A?4?3^)KK(6ao!^uA9abE*yp!Lr?;}r<Tk%*(ovq|ro~UROV{wgiir6N`#EO%a=d(T0>;2WlkFmdvM&f;_HFtJ;`4>t26yLGtfaUKv>P#d>^4(3;i6-CAb~O99{IllteDZN@kE1=k?&@{kO|E6V9_x+j0|Wc#2b8}s?pKLj^%{rI)YW@#AE^J&e%HEhdu1e^z4Tt-9|L=c*=%nhcN>ZOiGSFSrqk^AG-dtlychO>vhGLk^OqYqD=eoRXC&_3PqTfR&ks^|k>dEyY4)RaqR1_|i;;MzVm;UA9KGMHN^YHpsu{Q&=t!>R%H(;B#5)Ep=Okq?67L(dtnUZ(+VYEm^+od_wzKoOrKe@RCZ-`z?Ir8ydL7hv$GypW(zo8UYxQG2|ApMTced_1+EVUFyV|}V^@6;7wC=WRP}l0O2ERFo?^*8$dFki$ic1ZCn?48X`~BSHTGnR~y>Hj&R_m@@%fFMx8i{9GEnEA4U6-vIt>p%!T*Pu2iDwt<EMc8b^HJ9K{Q6#BpB>thTXGov8A(2j{$}C3!A9a)YCL@zOK$mS{bpdD;R~>D{f^y8{H;UF`rK7U&9PF7ejwNKPm12@cNI@*1J`m6#ZN2p@zMY074(r<oTAryAL4_y=I0e(r0ANWrQ}*ZtZRg#!b&H-54e_dDV|gDU_~X!wOmNiQPqE1#s4MO@-s!N6dhLdkZsK`8?c*>cGIz+%!-yPxt*d}<XY~ksH~zcibBb?TuxC*MfvDQNpkI*4}H-7Xs+cOif>c=xuS>UTHb1dkJ`VBB;7u#=&Q~b#`hiDIlSUEpQPJ6`7K`+e`5nr$M4ePSDNEjn&VmAhA}F}anhvQMHMAg6r?EH2GZ^KHvMl0m5!pH6*a17^9e}ufBIh_B>vIA`x*c7KScQNH~;gm5qrP+UfKGezf|0)UNU{QQ44{OY^H5`2W0#&48*#k'

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
