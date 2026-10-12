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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ab9804f981184f8db6f1f814c2b8c169/part_006.stl', 'relative_path': 'ab9804f981184f8db6f1f814c2b8c169/part_006.stl', 'source_sha256': '1082b74ff831941b278e7a20233ca7cb54763a5febaf26afb173db449274a667', 'input_faces': 591, 'input_vertices': 460, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.7915747761726379, -0.5346465706825256, -0.8030763864517212], [-0.15248525142669678, 0.8967461585998535, -0.006808757781982422]]}
GEOMETRY_BASE85 = 'c$}r21yq#l*Y+O_MC4!>)*KZBQLs4n83R#KvFo6YC}5!&i0y-&D0ZL@BF3>0MZp{su@yUT#6s+DeZBW}`G4_U@3+>szR$Jxx_+~{XFqq>Gs`yKS+f<;@b6D8w{dtab0tkv=AaeOM)(gM-mka+uquOsN7-n3#IOGS(gm$MwrbPWMjN4xDc{F`Snr|b>ln({3#e7z)lfcQ@X+BydkyM2cxWGg<!{<+;4uH6{$YK41^fT}T%m@CyQ`skMOVW(!~f$ydzF=i9UdQ4dD#}cTl7fiiGwH(`~@l`DAj#4PARpN%n5(9>;L|(w6o1I@z=}&|J#ra;@|QqN&I&|ri(xJ!dm6m?=_b=M&Il3pI@<B{LibMQ=bhpFT-ECZldVEDDi7I!{M)WdA>?-@%Fl?KAQ#x!Cz|Z9(mrj#}_2dn)c#1&M$US{%%b@E1zxOKSF-ehD)5Q4=$<C*0~w*A1$&^%4;kkev|uc_=gRXIF@(4CBF5CxA=|oib;922|+3HxpZ@+Uv+c8XnN}_^1bjy59RZdoRUu8__xF{o_X*<p7U@x{EbQ=&Zw*6H(pD=DD`<F?TGqpJ`nLBb3TopzE>swpf2!NoP_jGXC9KcU7W;k8C~v<{Qa7Fg*<22v-|S>n>$j)?{H|N_&sjJ9~OW(0U-zEbNOWP>(@#mz4h)q@i$0<f6BS*l0L3XviyDdLGfF?@>%7xL0>EBi^PlHH2pL3Q}59xNf)&d&+Qy4`PTNdL%q#kB!08i32|OtnJL;X80niWLLB|x7>T>4AM$f`74m6x-XU?e^hJ8-YkaPAy!4ary~MBeZh-O*wU>UR8+yV&WE7rjm$Wjo-#R`}>RpQ*a9*C<`X8iEv|f|`Y}_K_NN?wk^448|IGayMd9^PN$mf|mw~?Q`+oYWCZ|+I_oD;2?^QpCe3IBx|$p6+C(*D*Z8RFOWTCd7;BV**brs&7w*UgS7m)*i$c;5MYD0eXGXJ1j2w@IY<O^XxZ*B!#7zGf^Izh!@S<mdf&d9Gpie5B9c4f(gat(VUwXCgmeULv2Sx)U<{^_P)I?=(*GW9&Uy{Kj>w5#Lg5ij?c}XvAr3xgz<m)>X=7aSB0tb1@kY`nvJg#6PqP;(xh``1eidN3U9;-m)g4z3k4&xYHwyh|~4bE%EPM5r_P`p}cvH!C%MmptQ^8{P2$-b6M&+=A6uL`p$1@694{*o08t$d9TF%^g;ZVVRok_-K;}0pXi~_#IFw+WR*Bsr^(+<;ZNW<eaCaJ)m$z9n8)x(1f5jrjlmbBo{T9E5PwNoq<46-Sw4H55WiOa*$vSiAEcfQ(+<I3_Wcfd?zLtT$C42(eq(55$&VH>2J>8_Y4G2#jyO&BNc|Z12O>X#_0hiW`=({~8?)|{dDgOhgN$F}lio=GHWKx-VR($_n^r7ud#O*OdCgt%+qXnMoetlTeEvv6e|Bw-^7ivVKRKUGo@>eLf%G@C<NJobGerH|#BW$O_qu$}c4&*lS>b{>g+1X<_K^A8oTW7493Cq9vvk{v@@@JqaSiXcqn_PwEEb*eRQ!6w0?6mww$dMrO_IcK?tW1ErKSbRxUl#fzx!LeEIe(N?;qZWI1!_ze)L`i&dA>{&J(|-`6*fdjDx#e$9SHAILCUV%5xLS9G7$_0}$s%N%a3+Y0|GOAN|B{oRk;ezug?|Gp7^s+3XO;Me##X;?M7aIGs#b*ZL&Ne5DVrf;hWJaK7C+N3>%x@mqr`pj;nsV|{UOfd5`I)SKbeLaF~U_Q-$F^|z(J-7;bS;F&}GrtB+Z{?VUd+?Z$DAia<KJt=R#V9CFB^sDp(eQc`C1I9`#F>g(Kit+Jiq@*{+dEm3<k*J~D7_K7&!o|Nm1%AgN(qDg8%<{~BE&n9Rr>W}(^zY$EkUj<F)~@Z2ka9ju6u-&sn$&|nsITNx58jIB2Ru)c{EwP1<<iD(!T3w+by?EQ*Q6bcr`Mre3xblRegem0-dVl~@iT_Y{G~N}wnWmspM&&yp5K!Aj<1i(=frX1w+^m=em*a7snlodA;{0^D_Ez;TVqANec?ageMz3{T~XF2%eoGTUvjnNU$ZYR{lbvk7WGs8PQ27l!n?HJ{3Y)o{hUPf8!s>T56wb<xKaxHv5>~_`~55Pqt>R2^b><mRn*VRX_z<WT@=41E<fsj{~xkX(qh}pm(M-ENx!so9Q;7?Gi$A+GZ%a=eq+=}^bd0&_AS%zi(mg5iT-aLf#;q{g`fKzeZPZ@N2B9W@tbp%ko8`xl}+XWi{E^VhlDvYUz_V1F|VzkjX2Xa$&coE6XmTMCVuN_w1Z|XCGDVB9*F#>Ps8`7wUv6d8av{-qxYkqgl3WUv~+Hda((uGB=L9V#rIA&hX$vjeXD(u{e#}7BK$*Y<GD-gOTV@B&WAV+a-hA2G{E=5KS}v5u8lFSD-^@{oq1pUhN!ucA1ytX)Th<uD(Y+D!TS=YMiHqu)2CyI)4MDBf9|eWr|WDIzw!P@NpJNpk9Blk2;%(F75(|$4eXPe_7}gk4#(xSmWw3*@BpNrtVunXoBu$6J>4As(tR*raNah3_7uOl-$6M){AWKoxeoGkC-JU4m+Ow+t|I(LyBwD1@2!b>%}@mXiIpBodX9JNUxna*FjC5;J8Z{1I`5Or%f@`G)1`i<VBc!p{|<h?4p=V|MoYVxLLQ3$*S<^lc#iW_w-n6p`J+!r{6jhATwz{)2L35UWIP%V?38`K*>M~ErK+I)KUTx~9xz}0hEaJjF0@jZ$JU49xi?&JZYo|+_A{nAeZ;RPJ&^vaFN~3S%v!lK^1q}%>TS?QoFAvwLHu$r&`)ALXG`4id61t)6VUGU7NI{Ju}7TBE2TcQeq*stUwI?*h3Qs2+Kc-Qy?KWCEerceeVQX$V?MUIiTNdq2ggO4^h5n&lK6GcV~@rE<~{18!6xw=-Bx0p1~riOGEIs>oLe2R9^cO{>$O&PDW1DFAw{LPJom)8ZtNJuPrE1Uj@I<5j3d+BKH@j*{zKLm{YqJx&kUD(Abyz>k{?U7i<HkYye;CFPnP=BQj6mp*w~2l{o--1ykAQCgY|R`JoidT%tOtVNjqxJMNqEf&*-0Tt6@Fe>VWvk#nG>{>exTnzPyQkxFtjK<8%t=QSS`wOP)t!JcZ52xbREIynH!Y(wpw*!1}R1P5hQ6Q)OM(2WH6nZ1uW~I7w@tNc?JcGLM;~&mjHG322uK5jampM#DeU731Z!3G?udC_H!WBGmIGQ*vg%vHVJjW7seo{UP^q_y-QebA4=at_+)pI8%*MKc@8KIM2MDiuA5sP~VodST9OXLjLn7OB~(5G3vK=nE0((rlWrbdrX)3FNYxht3M_G7Sl!P&*qYYP_A9iFupuS$@#)?r3aqtkPGu?3eMq{5pB_5D!Opqj=;Kqu{rXyJ`nA-cZ2K;Oj=VscZvn=J|sn+W318$=^Y-TKet@>uf!cz59!AyAb$88oHwItAwM@;NqLP+zGHp*>JEQvH?)_JMdm$2S_#B|8GBR4weNb2i#$%^H=l?^{Bq-DzhRDbfZu;K{J!U9-)-po4g06%6;RK1e$o%EN8X9w(#{Fvv~eS8cZ=Oiq_??+zb6LDJgWCe$LCFXpGyA!*d>0W#ftP*Ud#NT4^ENsuBRkpoqPLM)(Jx+++UcA92LK@Y6AAn?}M@b=zaj{y_%vQ^4`PpEf)TvVbU(fx3SnycijkoY+kh2<#N)`_2Bi$=P0A(Q}31y{VG06{N}j3n5U|_$-d4qa6a-g_>k0(=CTv}f;-a@e|0*>OUO5zEB}}Re`*@q(fbD0ofaM8pO+i+|JRk62S&C<{IA=wZ>->p^{8kQ_#d7@{ckyidyw-r5U1ZT+|yZ?$bE}xx-<N<FQL4BJf(kHg7P8GdvElgPfpn1PR@gRNKHVyjGKQF<##~(bBU5(Z&?ZZYO5XEF**h7EY}@F*cas6!5!<2Y4iNdenXQWjMEdn7i9M9)nY8-ANLLOTR^(_jnn={y*VAhK6X<Y{NABB|F6s=^=3S5#dBXqN&V}KW3cYmyo&fSftY`yTrjU*PDXmKA$L(f5g0FX_Q0Q>ALI0SDcN^e(&Mo23v-cvVrel|`m?$67UZY0FZ$1}byx@TFUNBO_T%#<2kc)uFND9PC)Qb~n<($y>4=lvgnG8$F8#+?KMejU{iPkXG5c^&J8=x+I1a~ieU4!~mmY-tpE!^68uur9oBl|@`2y;5*&^w;rbT_=Z<h`Iq0v>`4<9ihj;{mmF*|R-KEbyl(yx6aam?#aqg~FGLjCv*M*TZ(m;PgISO{_2OhG>x-52*rQ}du)?j@u@8!H~de(97w`boX5*yqP}OU&%oC%j0)I7*RwUOf%#n6X?5sUO2K+&39J{=j~&Sg&2uUXGI_y*23_+O6tD^iPNGM>G44M?Rze`)ri<x2C>9oEPsgpFFRP`>Vd`;y2vLg?Yr?P1ak}gol{_n&@cv1J~sK*1Yiy?#b+JF)pWX!2UV=al|k5g7<hmSBdV&d}%qf2IIvpC|csUZ9)8$-e|{++UU>SH^N`~2KIZ-M=}4biAJ1=ADA~h8%g~e6Ql6l3oS72-7tR{zOR74S~%86{|PvcxGqKgq=ch>ayLDl*>7=;#5`ZJ2j;h~3*qlw0rl{-U}9#!zRVNz%knwcX9mwl{4BZ94}aYY#m`2Zy=$agmKUd`o~(C<Ax?Z-%vXLHJTLS|{<ojTyy{wS$8Y|mXEF}80S!<;dI0=fFZ8Hz8DFNYet2$hAmRj%l=a$t$Q%7<Tz%Xp7751s^}-AJZ$Ak0gY#kBTTS_b_XEA2VIHm=hI`e>Pq=R|<;VI`%9N7XZ*{VjcGr7kNImK8GsJJ|*a_)UgJLuLwH4{ee_LP7^W!eyxl#A9kFs4Q<Jeg9F#MtQWdE$`wdFmHX-<sz_3}G#zDRO7k=bvV;evJTuSwD$tp6;;b9d#%KA-Qc%x7mJeL+w3^E08c|1`z=!QbgI%KNRfl*8~2?@u)E0Z9L{>l#TnzAf_8JB!q(wyPc5qnI1gf3YGzT6ffssUqraWN++e3TKyf$`tO5=T?ctey09P%zH6q5XU(V@xLxdd)X96`da^>KM&}F{iSaK_$y%FsoAH?J-lUR9>iI_1oKkYz;x8RBl5$02211VGEbNj91y3=b=2FGM9h2V>=EbnMXWnfpLlMvgTL<*<iFx(-kblx{qExN7%#0C<Ne^LSGY%WYa#QVDQ^+HpDTME=|fthe!SwOf0>V-!nx@22jqwQD8tx&h-24W<|)0l3+B(~aqzdQDEmxH>Qsqu$Py`jvu8uh_vM>nJ@;A+e|rt%?9Zdv$IY6DbHKH;SO+;T>EEX!{-rV~@5G7HPfV_pkbd$5+?RA%A?;{v9ES8wTVemyZ7SA{U7=Udp098|TQeT>o8v!-vvnWVsYQ7(4;}M{zwvUkd&X{@x9poDzDE$&pN6)Wrw@A|eZ*tbzuP2fFG~qG)Mwz;Cz<=LxkhEwze_VIukq7SS(l9m{zUwHeuy)74DR=`78k!Meh1EV=7Q2*){uON^VwF$uPNyS`rGV0$d4%q>%!OFQa|QB4#>~(vQjS7!UU}2>2~m6u7&w3!UgA$-5*e|FIwUJ+pjL-=X;5D<v<MPv5V_)4_fXz(uWq7_1$P(_$agA61(rW`Pr~&kNB;*lCW-BPU4>QWgOx^@I$-Qb&>k9<k$}Xhc2jxZ+~IGtxbcLtd4zAgsZf>Vc0mNFYyNXH2;hKv(pdx?0z2S?qBbJPnqD)It$M=W#B&0p(*0@J&g74T@v;KH)_D&*#+}ec#NzU)>qXKCt)7yzgsuVSEbyL&mU!FelTyarf2pW&(}u$t242Vj46+Ln>+#gy4SsMUzTFeb$yoHFKOFnrvK*e{_TdukHqf=^b9*Z_e5Fr!<uj8vti9A-19ccCi`#g$5xE%Z?D8}Id}y7-4cf%WcKUjUSt1U*dFK1;B>^v5rTbD;0?U@|9ngQ#=j0=-g8Tq&*l@S5GOhi{jGll=COVU@LZqeGA=Axo1p(3+Xa8YRhXaaRKoih!#2dJz7g?#yfCk}-h}7OcHlkw*Q=TRCf8-??`9468;7Fc-~Cbghh<!2?BlXbL%D|8p#LNXVm{duigI~xLwO^v;Clswk$(4Sj3549LLbr>`QKF<^WHq%`<hnwK^)tbICqr0g7tToAN^R@OjoB#|2KT`MVy>B@g8|^b7@~oTr2o@*OPH)S@kFSL$WvWGrAMj$9-wIpXuKK^;Tv&=9xuxaE@E(jPyOSq95`+Zkd+{zsulys=rA>`m8zd++G^?8OsLX-oq(7@*i0r?KQn1?qQqRAbuTJzGuIRd-xIGP=BQ~+!Ni+jdWcu<M$V5YhzrW&5Pfe)IW^<!msz{X{or6>R`csXmtqknJWtGWo!cC9FE8SGcgqR;ngPLx&KB;J`F{lqaRfng!yRLA=J;j&FELY{Skjvnv5^wnK-F`Qv&Wqw0ZUAzQUL#8`i;ZzKD}J5$7nIT6o?{AEdAM3jO@p4(aEn294m~*YbMierT9f5BcAGL&l>X-vaB!Yy3XNvbX{A$@dys>q1Chya(<x8(zYB*1rJaw|K<&)^$^U^PiiA`D5uv+><=FL!4~6FdufPgmb{9cQ}U>+KGO3)`b24kQDL%obRMR8#@PL{<)Wo`_z~_XqTP!v7h^#gg6a{NWV2~G)ukd`g-hllkZ@Ce>4*368Axf|D&h0m$?Yu=UJw=Mf^7=_&tB%y-&WTh{O3ouhj#eD>lJ?r(r|f|2-{>@!m57>wsT=^jF`aw}12JZ6WKIrA2=1qdc!--E+Mm?^#W=YT<WIgAXA6yHlwDySA9eb|xVGv=7L)VJ6n;+}m-E{BaZc@fnPLacnfk72mTP%ZD)TN>THrf3SbE_rUs7W;y;o;2q}e*m#`x?WQ5lut(Uhwz9~)WQp=Y`W@@BUU$fc_S#+s`7DX|?#4X}q<)O=OCWur9@rPXj>UWWx<!z_;9%^N0#opwJj-p&mk(#4U+vD1`v0DUcw85Z4-&CH1#J|+rQGD-e;*PTEq<$m7sk^%yf3nB4ad0Lc^B`s=D6U!g-;mbctm0!d+#5tv$jK#p9Q<nAI?0$KCW^Tq|arK`}1WVFkS`}fPc#x)Z6-txOZKe2l;o5L%*r^1n<S(+QEOeu$*(W(9fv<(%F%JzsJ}Qhu6mVs+|?<&*qWHhlcjnc0R$nv8|lcv$c9B^yg*Q;2%2@?Y{pa=J6Z*QQyv~xL3&+gmyI4LOXjd$Nh|l1^L{gWB$Ip3gsEW`S`0p{OfCDpYDs_(`W;{uuqRG$@kAzw8Qbg@t$o!1>8e_8j1F*@&WtbhBvX_t26-PdgBuKn>k_KOo>B1zsQSo&Z!nS&$|{z`9|4_-@Kz2^11j4=8GxEFyEX$iFWBY1ogIbEAGi|IpQA4c`<$mdHi3zZz*^S?K7vh>}T{%OOXEIY}C(*9{AnZh#~l$(39@C*UW+QpuW2ke#ddA8RmzNAMxC$k8rQ=`4Z*LSq0_2a0&1Cj^~#0nuFV*ytQZJocbN-Bx~osxCcn9fcdrZGpPr2(JH8i3ARYz$W!uZa=ec8pV#3&CfQlaYZ=uC<(=-1`|tC2(SJi?@O#7$d67QxH0IOQX(*Rg5BG4RpI{wXcn0Zby5oMx&MM_H%}&5QoAo>HS$SV)c=ZDFVU=j{>yy6Xyw&6&&KEZ?;r)|Cyu>lO6hfThd&F;SwN0LD{^*A1Mo-5085t(&4T(J;9&Gd5uX{^5PFPi=xTYz~sTI%ydS&`)uX3t?zx03qX>Y$8|5rclty#P3|L;$GXaCGYcU2s!H(BZ5<dNhcn&JRzJ+e|yasYV%wHJ8+c`8luI_hNdUg~n{Wb$(I6zU+d(jH``!^ldflc$hZ&=jwvjw36bOIEs?ypp_wx`n)he3p8Me3pEddWn3O{F<gXzYR=rI!*C;>Ta^qZRGRhWSZiO)Scvu<ond)<oo37)J<fi`^neI=cqAcrLknChso#2x2P%PTjVD+#V=`!?@_mt?~zZ^6mO)iB5x!wq0S*I9YtP3o<vjJhw4jKT8G?+Y@`+;8_8v;dC5xilgp4RPz#YOkgHM+WTh3!O8+7&?MALjZbwr*i`tj0bSYWs8S*T09Q7?Zj(nS@IGYW$m<?EIO>#DJ32Jk439>s)aUE(KvXR=6+J@Yb984WVRyviebQ)RdL~<~BFimj)bqrbQ2yy_qJ56zGY9P5axiPgXS!sK6V{!wUVo$0sS?MscC%F?%@o4I7@@R4-brV_XA#x;n4^8ng>PfQFQ)H#d<YVLmG{wiMNo1vm$;Zk2sR`u$<Q>#4<Q?Q_>T+^4IfABm0(B;N0@*}U97LT?4kGubDegiYOIA9N+=bkTrnmyN16gTjas_ggpVo~!j@p^5bUt|;c`0=Rc_}%OdW4)vK1e-5R(h0tki7S&t)s?MkCK&I$noSg)NSN7<R#R#<R#>h)EVTK)E?9s<R0V@>O!*8)nuiU$suGPn&NQkYO>PJ<Z$w0>UOfyUF5~&71Vv?737uF-Q<<zWi-Wesc~eb|B~mDb(-QnR5MxWDsmsPKQ)T%PaaAgPgYusJd|9CnwwmSY)iFjU|VvU23=29x|N(p-a}nX-b21dQ+$v*o_vrTMN>S3+Mlen6L|(Xlp07@I+Pqro=H<Yks3@^Y9dc0htL%Fqjn_sBX^;;CM#`D?n3sVDQ-e-NLJc_+=N`8rnn}x7P%(bjp{*GTAi%ah3rNyNmE>kTAr-bm8`TJS!r2vDY6qyaZ&1@WTnN)Maczdic3)4$tB2DXo|h4&B#jq$X?{0)M@0N<Owvz8>sup8_20N#hMLFabD^%vNFYv)T3mj7P8WuHeh9n%TvE=V5LRruTCvVElMs){>-$GHLx<pm#G)Xm&u!{|B^S87g8h0N=K8Gjv+53kD&fT9zh;VZBJI(hCG<uo7#fho7{n>xCXT}S!r%^4RRiuVh3tYvQmxwtJxI)LA9mYkd<a3E6qw)nvHBrwxcP|Ma@pmMRug-AS<;eE6qoCB-f@XZcHskR$7g$v@KcbSaM^szl!s-FelXWss3btrctbPEm@i3dQ=A+urkH{Xo{!M6t|$B*1#>u_SD&AWr|<X6rZAwBr6RfpCT`y29Ot!=hGCgp$;G`ol0IqK0;IcfVz(S>rDQDruaEc@jII0t2D*&)a7KQQ^-nJkmJdT)Rp8!@(t<^@(uDw>RGbVyX24L0yZ$kuGH6LWr~|n)j3>oPpUIDKiQdVM^$HaJL-9|GR4nmiXTyv$&bh{s29mf?~`AUv)I5C7qNjU{>r~!Cx0d9v4JUmO5Zv1Q}P$;E%Fy~4jbqbveK7iWr}mzz!bmX-|vx?o+Q5^-=rx%K;1}Ix`cdyY^Es=r%oa(?L!VH52PB&1IbOPWyne^keiZQQLB=bwj;M9>(p6fog7V#BP+d4jwUBj)mb`;pA~0lFvWk^KueI7x|9DP7pK-C7blmdDXwhu-)Ha2G{yC4irZ2<l9dLNl@2B=4IsBAx1uTbqIM^Hkv*ub$x0iOJ;-HgivOfGApc1&NA)Bt?L;m|u1izgi#nRDG?LtlJcp)uD|HW9=`pg>1LUpboz&xGrTfV{$uZO&<QVb-YBYHPc@i~(Jc&GjI)SXzL>@r)rYUxzDgK+LxEVEwth7J58M!G<aW!feay7COwGmlq1+o+Qg9cOliCTsH>x`{fnc}K6#sAP0hf&9ol`bWRk=Iib$x08B*OOyuiZ@dCl7F4IH_{X@qA8w7jVCKzL!L*TMO{LkMea=<N&a=-?oCtt*H0@*Ek$ifE=6{u_8=<_A-j<qQhmq`$rXQE8LA)EhpaT5taLHik358?cocO7c@#O6x{|DP899_ZoI000oZOeDxE)m|EA2yWN3KCroRy|HA5C!~sy|ujP_oiWWTm#`Lga56RGq88(G)+V?jb9^Mt(?s|I-TFKy9ek$Vv~Al_|bMUljQcIf14)k~)K|G?c7#CRyo3awK^fHH5s3JddV0jM|T^v<o?mJcOpWE7gbGmE4lrgsikaxh1(SO>t#vO|nuqa%HkJwItb@T##Cdtkj9Dv?y6=0dhfdVQL9-VR9vE6|zz<awT#jn&QsXo@AvH$eqc<X^Iz7H;@;RcTrQxSExUzspKDIgAG(2yc8?VOK#(Blchk`|I>db^xyx~xYB<6&xQWyH-CRsnfaTkKV$vp#bq1s?CNay^Wc|7I!G&ZgP{EvYJc!@'

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
