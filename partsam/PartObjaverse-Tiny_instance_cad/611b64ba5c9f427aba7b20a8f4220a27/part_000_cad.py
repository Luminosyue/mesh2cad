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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/611b64ba5c9f427aba7b20a8f4220a27/part_000.stl', 'relative_path': '611b64ba5c9f427aba7b20a8f4220a27/part_000.stl', 'source_sha256': '49c09d135b698453e9a38e2c71e30c5ea45112c940250e1301da80401d6b83d8', 'input_faces': 1000, 'input_vertices': 596, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4495393633842468, -0.4312227964401245, -0.4999999403953552], [0.4379963278770447, 0.16662263870239258, 0.49999988079071045]]}
GEOMETRY_BASE85 = 'c$}r32UHZv+wL1oYgls@b;N`Uii!aYw2ETJoKPHdPGF90&WZtZ7z~&rW<}b7iaB6L9bNO9R@bn`JM})#T-ZI|J?EZ#_dD--e)CZCc6D`Cb#?Xl{hKsMkutl6{|adh4i#!(t*mJ(GHBVgq1{3U_v+FutaSf@BV4r1;;a9hx}b5(MorqfXhXG8#k+P3>k?Yr&r-Z<_sYdREycSJ2pt^Ssei`-p<TNvzfPyVVci^lSkF!ayE#64RPe3nX(?aA(=x{L|M*`zM-@yxE-_ZsWz4O^{;Fzqe_T_ajWS2!Uw&;W-}w3IruuB&Tn|5BzyamknjO9(<xj1G-y`&>^6gjlUjLV0tU|2v^)K5bzrJR<_(sa%$Ca;{+a<qV%s~0q=cGP{YhTH)yN*HmaoJ8P-&}5y&${nul<#>$>Zvd2C&$%etneQ<kCXEIp4=6`SwrOU>~>7@Utf4j{B(6tzH*OsQlEtlV#F_7p68o#lkzQZFB}p7cW>kgUoZ7H-nErHTEj1L9PMj?HB$a_<N+xchU06gk3>m3H!E@g$D0a2dsp$bw<}Hg96Aub{lpeIuL3Q^H+Iyzo4lTuuyRsQW49Oll&7Vh_K%TLPc!Q99r4S%#Yj8MO(*TFm5YX-<&w0sK4z-4n^t!z`~csTa$Xy+MoXS~3*q1DCfD7VS{v6f<81iT$Km=uICeumZ<z$Ym)m|RU+Bwa$<tvR{QiGQ{q?6sCBK$p4E$A%<T`4$9OyqDL*U!K?~y$1QldW$>?^*}@B_+E87#*&mUck-6y@Z6wXlS%;>Wgx-($fp>9@gCE=YZ9)P`R(V2Svdrf-w-|5S&6_RK-KUUe3r{;f;Fe=}6BuQs#HR`F*RgYO%4NY1Nmgp}9A3&Nk*ai92+YtD=RPJ?ew>?wJ6ZQdZ~7y0J49Dl|R^v`Z@(EqkP7GLu&K10gi9WU2eKkxwllBP25ENjZ*xLdCx&+QM=KlM@j*uT%A{QPCo-}LK;Pf7iEokaPRelouF^usZ}?kq$3o>f;%{<GH)i|;)Z<yWUXA@#}K^}dw5Fc#(aotJ*4MSMqpI5r6W=xf`ge|n|DajVdOybb+!;>kmj_hWzLzZxz1jW_irzj>+)%A4IW4|sXvxJ^34_k0l{<y)=aAoc8C7ruM0NXg&1O%$$|4&VN0sa)TpUG|ATt~&g|_4kS&n_K#u8CI6Z-LPBo`_zt;{2NQdpV$NQWY$GE-!`S-k3BG7>iH{Iq?F&63;v5&(ogK$c4NLOl9Tmxk$zx#&~&f(m9oNL_+yo{XU;{d#c%Wl^UcnQGQPC&gD`JbdkQ~f`a<c?#=D(Te(FQ`*$&D$HI~-Ec;9v#ezROMzVsH}7+-Zy!JoVY^V{MeX=lB_ark$Fj>viS)o|QTN8o2oiGI8868hVX!|*q@lksj2KDtBNv(_Q_dAIMB`o|>7c+{&Ngzx4m<JX>HEc$cv&Egw(YoovQuZaGzXAR0nK9zY%8+KI68%0*5{FyK4KQr>6pA?&k@&`K3k@_6?CjCLbH5Go7No%Fuj@3Rb`Lj=g-*b%g2Yun!^JuT}@H6@2{&j0D#!KO$IPR4ha$NIuAKWLVc0&25+oT^_J#Vj*^05K%Gc1?>V0yaB{A_%v0srg{xsJw!57HmZo8Isf;wH**A9yYi|8qL{-`B`E)l*;CBcFZKz;Em-{l|!Vwm|Y*Q^5}ykNMCyE5_qOSNPkvMoWF}HNyRU%Lm*yaztXDuMvrU-tHy*pKaGm`C8*;J~#aD!awy<>SsJVC-bOYIsyKip$jnXU&*{^UOfcAXAiX7uU`+OeRdy!?^b5Id`|ri^XrTK@a<10h>o}=<3QgO34eDQnIE*cXOhSCS%!8UxI=tn`9<-y)N@h3^=zy+p6o;asXqsP<A*DxK7ZsrDxXWtMxN&Fao<_B2mO3&SCqF+*(mL~GOgT~&4?!Ozg)CQ{fyV>SDES~&(GO1Ud;C6(NE@9fWPW4`c-su<o{kCdCpH=tbB|AMp-|YtJA|zF<RPJYn2b*@4)-K{kB{e`<F%grTw0yfuB*ICwYF=gunD1?w`D07}3wsK06=cI)_C_J+;d@WE>f}6X8#LiFy7hKI<j#!r!UOxHjj;O20C;-G*PMH0Hx)6>#7Gb_vIwIS1o<#wA?$A@L|*{cmYEd-Lbg|BWeUP`;?Q)YFXmeoxAuKZ){(JuyEYUx0ZmE7v3ad~jb2+K>Fbj=-<dRqmU{k`?mV9C;Xi$po~2y{Gpu&UeBu;D!02MUmZ7kDN2$Ur#Ch*p{mr#!JU>@V6eHF75nk@)kL6t`YF-u3xLvo}wS_8<U2@e;Og<ORKU~uDjW?5B!R*m>*6&#5!bpE8b^bEt9<2en}qla|@13L)y*k*kzOaJ-!}%Ti_tce;~_f(F8B}&UMteemHJm5!SQdSjn@-W)pv3A^2@eNPp1tr9^+YT@e0?<uYFMM;p$_=We;-_uMmA@}HPAP0qK<FRbqdA3c`5osEzmxG(JtST6prj`K0Dzry#~Aim-GeT95J{TX@Yl*BscQbp8%%4_&XL*V~;3Hi-L<O%;I<3hWi0`*LN8-CTfv*bE%JtgBypScfy*GIB$G2S)7_?@>J{(#ZazLq1w(tq`UdGL!&mU-Body0%NBi9J{1x~Dy^6kH(zo!U+zi`n^(S)D<<+wNE6XbLI$+AAtd@_%h>rm(b{K4g?N<9a4#d>LN6#U*B*NcAYAoowBR2clOPZvpjCQLgh<+lugzapE=&w8M{^gHuHd-yp&V&3cV0nabrs>Am<Ggowa*(u`ps>b6smvx3U<nbw~@5jRM2ac3}qyN<&>y!hz;7@#wcKbQuwD_H$T|+<L7$Lf6Bkt#&j>31_KS_?4BBzW4t=eMviT*MlYDT7<Qr{V^;Ja^=`>Qd@z`Qsr0RH8xvR>EIS46+KR~o+M@;oUY{c*lr-(U;;-|{aKy%B(UZsPCo%lpXqHOlA4`r>s;_`{D!Vq6Acy%1rS=MU{wJp<QmVz_*-=63knlva{AcGV22*Ms%&SG1A#)!&uJeXaA~GOuV;Zpu7jGz-Ldeg7VQx?R$*bk|oh|C!Am!C&@sm$Y-f7<mrX%O8dRva*!delLalPvNcb7l&+CYQJv7b=*4*ev2Zw|2|lYbz=Hp%yYFC$vVRx(GdCX{E+!c^UN&AwdF~KU-T7xdnnp%bPL=c)^3O2<`a&aB}|TMXe;3FnY9eZ_m_2w<~JYyM+5o)zJzgC(tv+qf!rr7F}35Ryl>~r9FMc)x_UO3_R-R}hu;|Uqb2`t+#kNxgFp79^k@5%;%B9v?J8kiu=b~%udU7lIj(iq$V*awYDu{+wo!J;W8K^7BF0NjsgE^fYw72<%q`&8^@D$;t@J}n+y`0z8n^4naV@caXQX_SiQ;R|<|F?PtdFb>YodJD=2(~PFL_nUr^^igSAKc^*Jg%@Z<!Gx>sDi1TkKziX1t<&d%s|;XUoQ8UU*R-{?Y*W*Mm{dyoaQ}S^N^uiEoWX`+w^w{l{+HgugeN>{FN_S+7ZX|Ml=oe8hU_TOIN3m1Zzcbs3Mg4tdcI{e$7BdXMrWZlXR-3yE(`>m<*g+F#jlz6~_^K5=qh_MY`GieIMYSt&R7?*pj+5%DdhR>h0&ZISb`f318;+H+St?gR7hN*>Fs`RC=hce}#>k>{A`x#d!SYx6?l8v$ivMfE>$UXkDA{$P}PAig$ju+-mD^Y&?syTUkb>hKFvzSdlncgZH_WvqCD^NqTLbyM%$$3?R*PLMn<=ioPdAoaA)N|gR-EwEU8E%PF2e|^S%DQ}Nx4!^&v)L##qi2kt81$nNOLw%;cIfv`=OrC4C-IcMgH1%(kPk;HOe9oVM<DSYP<I6sM3;a4cP|t{YXot_6#Mdeh7vCK68uhsm4*z-;v`>85%W}OMk3^n)Ii(-k&K{KfmI2*Q{;U4s<*rMfQvN94IYjc9p()Tlo2$c5K)<zl4wm+@J#|N(seR>ssYk7q<66gTIU)Y7(L-hYPdO>)Z~3xGeBF{?)N~D(<JxwNL-{=oW~<NUtUglS?$Q(GTWvUocDgR*t*=U>ysdjvsb8VuQV;960`RRrWF2OlyNf(yQs8(6JfMb6&dXK+zUJmPNy<;YB%dw5-_gE*?qhxPq5aQ37hgNE6a8V2j(+&-Ec}HfWF2P95G%*Erj3ICb&Wi4nwNUQe-jDcx~H4?C(-Wqf{Ssz(;mluWkeP^UrXz;D1UZPxRg(~9(k6Hf}eRoAJHdq;@j?wM4n3XrC%9mc1b<0=Yvqb$&R5?&g+C6*OsXfe9ar{(o}`Tx1@%zkLxV$Z+_?`?O>}^2jzE`8z%mSGsrW%1bolDQcwGt^Jvd^+2LD)x=1@WT7&*@$_4(HE3)pgrbvr+FkWI_(0o0lK8sf4`p$kpf64pm>T~Ax@avv|KP^P+V{E=D<IsM8Gy2Vgf|$?OZN@y4DGKFn#%THb_O4Ri_H#6ReRFH^H^#v46$anu&#Cg+uOsUJFa-Wdcd5UAdIS2~pkR!v&wdymeRp7d#kE8EoyWS#_qW!U{1*3`@ICuakn?@l7wzfkkNPh^0bL!0`MIBl@&glOd>MD<p`I82!G3m&UFf&=3Md}|UyJG|&!<-JN$4lp-r~OUFah;7EH|Y5jYO2+Qw;k#ZR?>v7q24!^ZnAEMzksU?L&^CyiYXt4Zg;sKBdFq*X<+YLigw`zIAb5_?7QW7T@zT>Qmba-;y{@+Og>kv~$V!@NF-ppX*(s&~86V^SGDgyo|SjIPOZ^FEwp5_HmX!kaerQdwTe5=1c$7njydW;Unfv@4%6whj(KiGUhdW>wbKH#y_(EX_h^M`_t)EXop+pr5(&~`<SO^sGR5J4tTD)vKIdE9mAx(d^%!ZXhS&s#O}-GbL!Nx&NVL#fM3L8rkvNTlhXd?q8{)^FB&iT(=S8*60PB1$RYb~wy}A!4_2cz>KS$e^Vy7$Yp7=?l-HuYq(5Y-A$jyapJJS}zar~ueQXNU)9*I?fN<&O#>y(<>-i7E_f94An7(`@+HJ~Wj<<TUzBLc{BTvr}@WVTWN}f!`aoh&M@T2F-I@UU1!bb5Yw?zA%?~m)Y`jXUNf9a3%_N9HLT<lX^$G#=SH;YE0|Bq=V^PX9!ILaq9l;>Ofm&4evp8PHb{y&CXmlUm$XYgtG8=gx$S~{&2HCu0juUD=o<0Rx9&UaZ9{cWA4+`NUjF45uecczv7W%Fg?8q~8R{M?U*OFxYENBQ&Du)chEWVqz@_d~lyoP$5B^BRnc^w@t`H48rHRo(S5>TmRizplMJSL$u2%k!&lR)YW4ly<h&@`S&r2>fMVrJh==CDQ(8ApHlQux|PGR@zgq`4j8Ku{L?Gv|mfaes78U@Eg9seRW%3xzC!L@4)x$gXh5do6*l>!{OIxh0lQp(ax@O;ICLI<HFj|8}+$05`KfX@;*tAvx}PBd%$ng0sEqHKk(evFO~S_y78FbxPH?Ie3tc!HYsS8T;J+VaomuL@PCb!{d9}HpR}`?XodgrKH5DhAC5nvgZO5irE<Q;px(0nF*^sNe5Uw+mw&Nc)?wQ5HuBtIIk6G_{9S+X^&WL`pY<}4=kTHf$=hEW=!W(Wn+sp7Ec212)P2lL?m@CIqMcqP=WlHNfqs7Dg}jH+s{6=upS}A&c`h`ICBol%WvP@OyhVIHuMXd%o7B&?HgUU@-&zKK?!ROl8FMQm|D8*Fkv|0Il_|G8Z<#xf!1tMqeSkze+9S_W`2D|1|FduCh5YRo!SC``%Gq}hMtzodgnyyEl(T1y#rv1CSZC{hx?}t-DR)!aCx0=NfB#yZgAA`TQZKV&X87}WEENB9KRLcR#TEYBb89iKTv(sC*zb3rfp*^Sf_5tu4L|KO^b=lRGeax*Yl9`Pv27{(Pl;@M&|g1b9^W+t^(?v+`?a^uNq)n%FwW~rDEwOMFkcumP@hHLus?eIIM!tc4<gT&SK@24gYn#*{XX_ZTc3hIrnK~LE!-XT?`W6jOwDbWj5|xWY<Pb(coF;>D<zK+mQg<IS}*8>9C+TEU0>D-=9-Eqe>FAcZD;@4|4Pn7`{apw3_67Ozx(6lJoMYqSohVwDS5Quz9{!8HJ;lBbdmLv(PlE<H@;hk_3Y)p;qOh2``hnda35+mTE?|jz#ZfM8P=o5#na*&t%GI1%s93b_ra98B#-uJmb@=9-EzqDu70EJUGaDR#C}|=+VWg$n7!a<sD}NTvqRC}rmltGK6RLU&iosmvlHvy5&!)`d7osa{D$Y|ZJlq6Z<NM;J<l@um#y&cRFL(SetVA`*9;#AfBGnSk8XZ>E#=L*qi%^m^{DLI>JRhd`MdA|_&;)CpYe3Kl-DCi!e6i%zdyLJ0r{IOgP+$fzFF}Y&iC+5)IUA}@3*3YaNQStlJdsy)ny;tm{u$v?eP@lM>Q5-%k}6C`fUc3FW*Pr&l%5`;ragD2Pto~j1gZi=MVqyySToQ@%SA;{9*Kma1Ye8ReE_(pg&rV`m}h7@}n!`cMmo5!f*K*eq(>xkJb+_!gUD=y(fNj1$j?zCZhfIJ)=>dzRmD^f!%hTSEEum?vO*`o971Mdi9@k57%p_yq7ZP3`TpNSb{tYF35X#?Zja@FTFz`+Tr=!tx7Euk7M8H*RKcSH<}{*;98wHsi)a89r7C+w@dv;W<dSl9zgyZ8)RR>d{PkmqnS#|{l-#1R(##9KHeWcI48dS#ZB=oiz|q4&C^cq6XvDID1T}u%7@>^?-2YxqI_^~<p1C*_Z$0+tg?Tj$J^oe43ztl<)gd!)@_HxH#@jt-^;y@_-5xo*`Kyve28_}sJh5=q9XEKJcs?iCvDDS+!sLkFDs<}){T9{*R~8rd2JZ>BmKu9|K%7dZ-(l4E^mi@CT(lD`1TPEu|KD;7T<Q|2J%c<FZVNR@E+_-9pd}@_%v8Ad^?Xkg)`#4N6HjZfBnNV<Y{?Ud|UssC?D%0`%h-|^7tLkrj?klbEOpDm=}TaUOTZaPn{d({Tt&wUui?;Cwo9~lwUdm*QHQ3{9dSh73^>A#QP$BsSVF>nQOqm9f$XL@p-WRo!wD<J)wxapR{IQg#C|$R`D%W@qWPk)Lq)&+9VYI<!#9Gxgpjg2}9st48`x&{``vd-Mbm$+rIO?aY6$;Cr()*zV-2E{QfLD0`qaDNYrOnN#vQ%=lQrTsDIjuc+bE5DfR(2A3*->1Mz#ZU*%<eYm_;H{4b_T9$P{%?k6#);2Zq?!kED*U*IzG&$x#7xW!{||Gbod`kaZ!agShM#rXZP_}W$czC-uL{*`|8IsD%F#kZ{gf%}QaKRE7FZ)s1<^CP(bmD6N@)Y=!nQ_w?w(QY9w;+r#H<G91F;kdEs;CEYv^6BT|di|YMeC<_&_;!!ySZ{7GAihy5wfvq%Z|!w5xo?XbDfO{MHIe(YX?mhQVP5$C%ZZL?=bu%O|5<?eW}k7$6Vw)Y1_!}!w*c#x4Z%2Wns*pS2YX0Ax7WXeJh!(=d5g7_)YCfP6OQY*A9;S&f<G{~>=QfZF-zgwvQDtN`-^YX>xcR3?KiA{0>{8F`4Y!<nIr9NtT`dRmXKe5|7FI+VLaAM6yK5-zaz6``~&^@S23)wSALQALbe6-ur6xj2meGM+O5hGycb&BPJAukJp5PNv7V0%Mfo+e@Vm23y=6SwOOJt{V}bbgF*C7m(()emM<?aP`Tmnx)>+ntKahX=D)>{<V?AWeg?;Nr?<9|Yw+EhwBMRcVcHu{y@6+Al+xt$!^Ff+ta$eR<5m>kOj}qTF5{7nbv=Hm?0cTLYVh#D7qtR;u=E+AFaoi@g@1p+LpEe^rWS>LJwF~dlCO^aa{~q?GEK}-XJ{en4^4na;!0$Rl@|dsM;r^0;JocrY4~M^N7oO8@#bQ6HOHb7Q*D=X&dG!{@J;?Wj-MiuW;I%vU12SF5akVe9-nV#`ga1BU^4lWs<9+U%^4R~dFTi<quYl*qr`5za4E+8^e_Tr5CmHtwk;l^w_3`MA_2}Z}DBoZc?o*u?W4sqLu)jF`kd)W&r^I@=*?8m`YRLR=U2_Nbh4$EwG~Dp}0$Z)(cn&#z2!4S%xQ_&Wl>X+Jfbst4cuvm474bWhD|k<06km$-Em0Tk+~YCI`!2%oSYtlmc{SvX_}cj0_#J_n3GdHlzJ>3x8ub~G4}PI{@Qd}qd*<@KcpmtzAfE5N>f*jRXCCfT3H7k<euLjH*eXB4bK1%Nc>Z4bLVWwTw0MrKF&pK#%tZYw-Nbdd3E%!=3Fhr)cd)J~6OQ$M%rulgI|1)`D&u{Qy~I`g?&RiCyyuHqhVngPaeceRU%)ta!TW^o+fknx{>Wd-9nS|x@cScuc|NpfkQesj|LTwN;>LZMMR<Q=>)S_s%WosF?>?yl@?>$r^_o}(?-4sy5nq4&2JL^a*1vosG6em+MLgEChdaWrUJC1+Ti3B(jvRwLGw;B^xEJft&67}{$euXg=T~vvpD#dtqT9>$vKJ1<`nUL6<gaxEzngq{O?+eAdX(Q-80&{k(Kz1*+fm+{67{#1!Shqj{n+PzTLbOCcof#N-iJ}of~#>}1FmDA_F*jA)23q{m|q6-+tE1qgR7za-KNQU*?f5l$DLdi{khB|ywB`#0e+Y#%KtMP>uZZ0dHM~M_A%By#eU--?@^zFxlm7+eK@a`KjBv|jQ(8kEY|Ohv*UTU9DZ-5=Ua+>#*sP1*F831eRzJ5w7=cG2%c*vzQXwRj=}rCprY`D(%`s9|HSnQ^@i`-1pUw_5YHLaeZ{xVn~m~I7Q)}<kMh=^xUaQJi*?}V0F-Zzb&(ml4%a1XJ@`BRk@B{t=du3W2;W?ORO)XThy7oB?*_<!=Op@7w~N@fZ`)XW`}3g~kHt3PJ@J^{XoqQ2q@I@ZU2(t5)(826M`PVvd5^TeeRn9{GgPdD`SZdwyeA1BkNj^uu%5h{@z}ro+8WwFYX>}E4w;NRT{=mA^Xn!Yx7ke8=h8ydGcDf7Sj)`AdF{vVCG8c*{>wLRbVNI+yovYIG0Wknd5`)O*oOMNSb^j2-Gu(X$}>K>Z^>5z^ZeLFc&|}oHI7?$J?2j>0PFMjYmq-91;*p>4_Kenk3#(iJx6_t@cA;sMqI~y<uI>CuRwi#H=&*TN8$JT)oNh<a|ym)Ej`w&-|?PD%ee!`&3zx|rO(H{!l`KFnP<bgVqqb?cl!Mx>hE7&^4Pd;H`c<}?_B(M9^XUoYc5AWtm=XF_RFKVj#cbvw^5a_uVcibK0RMx9NC6pU+45m<XO@d`HQs1db`0HwDULv>*Ru$aK3)$&^{j@p+ES&KAzk+-p@w<pt^X!nd=J9*LxMm3*WykPrz}@;km$4gYTc|+b{Hz`dgz4VIOGQBlHJjGv=Q&pN}W^&29W0<&g-?KP#T_daXkq{~=iC&v=e{j>hj&?OZ3@OT0t=4Ox-@D1P^#Pk4{>&2$sxGkfEGYsW9hA68MWqt*N5@#Ma>@<`O@RSNXaM&D3=OiQ$L`E1hv?NxrlZ(9@Xd@d+Hxv$Of#`s#F8t-8jYO)_``J5BwN9m~lgcRZ%38hh=uA6aP?xwn#yg%p#ui*W~$F$<x0(~TpHE#nsuBCAX@wKrbcn&IG63;=IGs2JVfch^nFrOUDiv7_J8}Xc#>dEoszVWmi+ViXrez!3zpZKQldie8VB#+*!5Xxtmfb&i0fc_ckA-;9cU+_=G;rYm?B+6gL^N!{IU_4KaDua6F+H))Ub+l#iMm_J>Mm@a-qCMYKfFJ(|`F~YKJttK}o&npD|E(3}&s9PB(;Lt}?JuK$&aTGuEsy7~+GUaFUOk-eaS!~vkTmXiulmIc`(7*ll;26(d!Ltek=cD3{3&+Xud*CWd+2}i?PDjR{FzAju72D9RsKJ|Hjd?Q24TN*eKy&bu_SK9`w~kZ_?E@8uc<N5e|?k3)h0}W|Fy}=f0h4_?<{Yc+`l~29lwiiR|xei^jo5|Tk&AoA2F_eI~d#KU;jGs*{q7!tYy?KMAOo0*|qMSlK<1hGAQQM|M{OL_VW3^`lpFyy}iBv|Nd=ax~ndlcFz%s48>2VPsvJOk)M$NWGMbZ{YqAv))oAPoQk2?jarbbv@+R^T%Mu02DLU>X&|`<xei0IP7NR{tw`3%-VDWgsrkuDQ<L+OQ!*5Pc7gum0#^Ex{F(fMq4*K?F<I$d@+0ychT<#K%VeeJ$XCec8H&$PPm`6NAfF+hWGFVNv1Fx($R_zPL-9W9Ub52N<bC95hT^RZ#TyxlH&AzxmF^&KAg^aAUQ69hR=SP6mb`|c*hbw#R=SC7Bd=yCUPX-}D_uukMPANOyo?%2R=SeBjJ%kkcp-HuS?MD3Lh^iu;<?lXWToNcx#XD)#nY*?$x3ICr<12L6i;R-p2ko-hdPg}bOm`1c?m=DPU;@A(u3rk<O2-FG1Q}ErN_xJ<YNrQanw^}rDw@;<ambS3)G9`Yt-x1i)5vj$k)lY7>e&x6Ua($knfWpFcjOVH_1wGlkMb()IZ1%$<L_I$x1(vpON1&6o04wBr8ql3jR(`!%&=wp*RmiaUtsOWTlzOg~){&iY?SEWTn~27IJZh;*!*SWTgejCCOzNiYriykd=CnmHLvaQT?gDWTjQeN^6pp)*}0pt1}drrj{cs%}p*%&dyNmN=-pl`q2ff^l!4#_hc1{U0e~0fAQ~sk(ItB|04fjDE>x$Lst5ltn?FEspbm)M*fYVI0rQYS!qsk4stPu;-b`C<Xr4eMX7nndDw4?G8B6<6njw%lMA!ocu|X!i?e@tF%<hS6#G%jkjt<i_$BKfehkG`ss3btUi+%l(&Vb-QVhjesoBZdc`dV2UC2t+HOtD+iZi+*6sM>DAphXCNzdz~u1$Jgqa5V)WOs(*veaVaVr=WOR8O)e+pa9thwQ_4Da%k?iCUFhiCltOid>54R)U(5oRM`cL3Jm)^B9VcIL>i@vUy&y^S+>XCv`JfX@pDCeMGVIzN2^!brxCa6qls?lw#+7O|kQSr+AVJ&anjR_nYH$YDaw35Q_iQ5Q;PL?^(!73y?FBJsFD2FccS8^MNDJUygW7eN0wrCtDoles@G3YC5vg?;1D{`KtzfOMc5dihnxdizEIazv5@b)m`xU6}hw{>bijQQ?rt@^7BuA*M*+ajO3p@j`Ea#A{TT-Ge?vl=jP{T<T?z+m8q`e%H+=)eD(bd)STqpR9EUR4XoPW3EM%nRSrj#<TX;)rVvB18?_|4B+I)o6#vkmdB{pt?jJnH6Y>x8ORAl$^bz?b`3?0?@*8q`_BmD8^sI9sa(Z$~svFsj^-4*7Nq)(^iY=_a7qukWi(H24N&d+CJY)ZS#`Ca~A5s4#4|9Acz!8lc5$cH1ju_>L@ze>_(c}r_i44VK7>b86PgzF{p$3ox`1c{y(d5zm&X8osR-Y^J`-7>W<WQCw%rZ)=G87MW#8~Qh>R|FXM-1oR$C8KgyGm<Qhm&iQTQU@nq>dwxBpYlKgY9I{cedNOWOW!zZtjQ?Z2v~&VQkM~%r}hw#AL@9$@+|Bj^^YM)QMy@9@SVZM}1FLbBEGb{QREtikeH+SWHd*#W_^Xg=+j3rxqluxlYX`>8KgWZ#kd*P5p;l(eXELN93YrCM(TG&PC44P+X1bORh$4L2XQKLAFvmkgep7Jg%xo18P%p19E$6M{-AgS8*v9^f^Dac{^SQrNPPiiQ?MSdM-(QNpV%GAK8yNtFk_RJiZ^xHD%OeUFtD!M@BHuFPQako^Lz0htej=+NTNI&yU9|Ma@MnMfRZPC3}!-P^*!vF=q`Pt2sX_ZA5NDuEBFv$0$qnAeSWvP-~ED@Vkmtzg71&om!u)!kvFFO)f_*MlMHo-lr7%xS&5M%}gyu&P>imbth*d`%-nXFS#+bKDjZu1GP1|1Gzo54Y@tJ0X5JisecBtzTRXXo{Q2t)IgV{d$i(a)HW_j_i@DysjbNk$#tpq$@SURiq)7`W4{cwgiF$TNwK;wsd+%n3;C%Qa(;3Vsu$Ud-&OoK=Ze3mU&w!vA5&kEACsR^-;<w_KXPrM=C#k9-<0>6e|t|>bC#OB)VfTm3;8?OL~p5|xL#9pqM94CP}Mpn3qx@MYEE)po_|AXkz{RNgx919+d;8fGpPH&S_kxXL}y2YQoE5u$wR5#$@Lu3*b#w_sO5+nj%Y*;BnPsL;$W5wp*A9ikULTvlLzxy16iLwJboW~-KgEkUXCc{h_ciY<g(;))KX+sCU-JVX?|*Ma(=Q0wJ_O(T!~tST#4L<+ML{mJcT-mJcYc1x}3a%ypy_}ypw#E8c#k;{zm;k{zh)=0&V32R-w2TLvc?>^q>Y&Takmv&zVEzdd^UMh8j;kL*7Q+PToddN?lG~N*+g@L>@<ON^MSVN-jw)LoP|qLoH0sL(WdkP0r1Jpm@3?ra5A=BStx5f+Gy-Wb$N|QQXrJ{TvZS9Zn7-Po&NuPbAN$E+o$<+o<cvHu4VYF7giYG3s&hG4f67UGhz`zYDac3s{BXuGDViuH^m<#RD7>M(s}RM($3oMXgD$MZV8ts$<`0D2}5ZC&!WZP<N5{kk?b!k=K(KQ5TXIk!Mk7kY|xcQ-_mBlZR0Ik%y3{G5Ybk_v5v9_JL8!`ibJc)XrozAFBDzi&~7_hh>7Pwa6ikwo2uQ&J4vxspm9sQSwy{x}SWNe2BW1e2Bb}8cyCwUQF#xUQC`zZ9tw$?n<pl?n-Xuh$ht1)QaR{)a=xX<m}`;)COA8m{nYo+FMH+<BFS7!?mP2LGd{1S}kb~QM{D8UrU;E6mO%R(~{;W#b>Ch-JNq<D$apQLtK*Pz!1)nJ*d5@A>`iVKGe?SK4j-u>&)@jnb+7k9*c6kDpl9mIer!2<aIx!C5?B*$EX{%r1?Sd4(ehpX+BYGqt4Wl<{!oLsa>_C`AYFbYAY>iep4KltRFb%L&eUqqO>!$3Ar=57PU0l*>4o9v82`_6BvpoQ-_k3PAAJ)(lE~YkOxvblAY@e#cE8dwL%Ss;y`LSveJ6VxD-FvBR8hz*OJyTjd_g0Was*+JL@`~tmc>@)YjDQ<ksZM)W+n-JeJ}?oTJrzT*vXbr6a5i#r>&+$o<K47>egP;(#MAIpPRI@pWo;7w~m*c}H}icA{n{_oB9?W>2>EQ2dQKR9@#=Me$kc0WE25qj)DZN=sS`DPBRHrzNeO6i=ZJ(vsF%irY|IYDsG|#g(Xaw4}A1Vh^^l2iw_$eq}}-UY|N_Yv=W{YDxDI#iObHwWRxw;#t%=TGD+=vGZQ0cqMfnc^=PsCCeyv-V+sXrACpX*mhf~N671`d#FdWq<gO7IO=sR=^m~4KDE3{(mlOA@A=L?;amfBNw!W<JcyyVAGH(N*>C!>%s}?(F!BIuA95egn*%ua_I1I!wHLJ?wJ*6J*;$9a$?^^4JUx(pZ)y*68b@f3s6wqk{zJpx5;cV4*ABg=K`$^A-*d!C>QRQ`8;&?lH5rO8GZa5yD1Jx1M}9|6>jHgEPRqI!rmDIX=DAcMn><D=^&<HqKi{D~AUpqdilI2c5i!&g48^w`ah`gGq4=pIZc`sJ6l-i-#TD4bit|x#kyR*8K}{g5Q2c`4Me;?~U2zrWElkZvE=*2KP2rN%hKk?u7%!5w`3tto3+7kc-VtjY(U!WJJl7Fh95I`^DH)I9=S}31j4}M~80K~6?7+OM$?X`5i&Be|=khqqs7uI7qsdD5k@xZQVd_D$ioO3SH<z)G=dq7voaeNK^=?mg)_o1@SDYNdP#nonyqUU%yoLEU^Sco|N2LqM3;1~zHIl4i!+**-+id~caskV%rtVI5{Z=QtE~|O1R<q0|>cM2!braio2|1d2ki3d@+d$n+-ay_>-Amq0K1e-GR&$OT+qbFCv8Co5H5Z(xI>+J_mbpfC&Q)qIQgccS)j6gUna?@TDRquh#Si(n+vM}icOlvFocUEg=lpk)b-G19L5(4s8s-}3ym*>*N+6%2#*&LTqM#!hQfre{)aBn(Q&Tb&7oyfB|3*#4P+Y(fzf;pP6z5|o_Gc)rNi9S!#QZh+UG<$b)Ewj-{Om{dC#$ITpK|FKigQt`k(KIX7itQIVmGQz*4b8yHL5Gajcw`1G6h*5e;&u5=TwbRllf}$e04@$e!niShhiT`1UaHSwLUqoBLW<elUki@VHtO75V?vY(rfB})&pFDpL6o>d6RwLo#oWuGckWA9-}%rBQ-raiz6~SA{+B(<1s3bvr;pYeRv*KslH^T&B#hykX!KcRO)!L^KU+k7Rk;zi074;>^zSEo?iyCv%Xb$9$CoV48>g-ihEH5$i2wJs6pgm<gwHi<QA;^SRTup?V{9^?8(oas9ng;zhz~3CcBmucr7xLoqeJ@ud9XZ>_he0-oE5!jQVWf@#GQI>f{mR0n`fQ0puQ3PqHWL-h<~op65QExyCX^u+2s=*Dz|YWZWZJoA+S5^k9C)YA#Z9iVM{_zSTUY<`<3XmW+SnXE(BQ9{7#l{f&8@Ie%x~Tx91wqc{yUE!jDr7Gx-P&Ks#&ht#Z}`mdg=`hRurXm4r|xuGMPI-&u!2|0-6no^r2<9hsDk7b=)pP!w1ogBo^LCm4Jt|J;bq8YV0xk&>T*X$|&Pyf?FN&l&L<l4XfhlKw7&42%_KlwLTIdc8)ANe<FkV@Li)$xDo!PHmnjA;K0NYhVX'

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
