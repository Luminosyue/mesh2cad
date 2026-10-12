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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_007.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_007.stl', 'source_sha256': 'bc93e68ecc831dbaa67ac9cc03ebec5ea5bef650a189a1207bd1263bba3e74e5', 'input_faces': 949, 'input_vertices': 585, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.1124269887804985, 0.23691225051879883, -0.10162349045276642], [0.11240486800670624, 0.4999999403953552, 0.11233776807785034]]}
GEOMETRY_BASE85 = 'c$}r31#}fx+x_R_5-bF_i_;K-J0uqiTC6xUTwDsp-3E8JAPs{PTv9x6k>Ugjg+ig>;x467ph3QSp1srDoc6!ge|=xy^{oB7JBMe^oH;Xd=FFM(Hm;vIiJyW0@*0_2yvfw6ykV&DG5n0dUHT8~(W%RT!0-DGvl;2dSO3N7{D#fHZrs{t3^qm-?%ZWSr~ZX2*$Y?cTA^@&y>Qn){Rj5%@O}F}{X2J2en^L21G;$p0o^<F?c(`eq-=$<0rt{g1=vT~|Cj%z@>Ic{_|(C}O7q?SIat-{RFWm?x7m2V_*PhD_}%{)B>Jg^_|Epz;BOtgRDKWk7vJ9H@kQ~cr0%8EwV~$$<r}~CxukxZb+2tuza4jSi0@ps4&^fzvZVa74B}f8e5Jh6?{0+r`?r_(i+?!uviLr)=186?7sYpu+K2M5CQnl8Uf&9S*EYysph&n<=gf8c#6R>Ld4{%LBYC?PfZw(t@_dR|rPQ%5YOien;BE08+k5Od?CpQp{)?3VTw$Jfd8<RCE8;tBqa<&G{^C2kk4Bz)ze*l^*2R0Iy(>IL`K~2@kl)8ki|;zs6!{+}*&=z@<P+an`A5`$z}dCZuI2NH?;f)Js`%kk!=xR~<PhKJ+4fiQOU!Jk)E=5ue0#RF*TpyNv4>Rojj7=8>j%H-YP4t7<fzYz7pPB_bJ9M}&IbI&U!k2Z_1)y{n^Oz^hVom+Nx7(_yQTf&wp-@%B59A7>%}+PpG5gPd8f;M&S{16m-EBllnVW1aB=Zn;YTir|KxLoXsQ75owKW>9b)ZLPgjfF;+vUwquq|QS}!^(3(Bv2g#C)jx5nFd7wLg|x_mmxzh9jmd6rDOA->=BsZzgAFMbpqR}|%QH<5O;dR!IX_~SI{pEtYI$GUk$d}sgaIFH;nHcLDAIV8Rn{0YbFppW!hd*TD)+sCa({|qQC?QCDPM|^W`a^&B7VVczAw2AHBEF<k;){a~!+j}_-_3YOh^=!OY`bnJciphUd{Gh3(l*`!`^@-cx=O<T6zUs}ycYkhzdamxfTKs%9uwMl#qW!N{6yIv@gZf`MgnGWYHdpdKN`d@8%)xfeOQq!BmyL~-@`a1QZ!uij!TsWu_|B%6&<;tDNjsRCo`~-_7bwTqbp9m2t;%;rjXEi@-M}YOe`8y;_-5IPXoq<{rC*udkE8ssx!7*@yy%~Gb|K%FDEPY%$?<h8n~D0QbX>!Apassyz-h?y@D#3l*=wS`Rt~~`?XQM*o7P(ToAsuV_-^MBo-Z-dZtlqq;4fH?_W!F9+O4)f{9Avb{-4iF9@q1jU2+@?&XfLZ@_J=|b3%Ogh5{%bU1@{lckC12IbbgGclvd;w{Og-i~V(9pCozz-YUL1tUUI2K(lqC&H7=x7x$w6=T?aCc-|cO>&Bp;&kNly{dRqQ@g2R6Ab*Ktoh9#|RpD=I2>--EIWA5|3FJTc0`>RbxKZ-BKkk(MntcN0%iLcq?YZQ&`1UG!Q9fs|Tpyed?uqa6`;g!`n(L0D{Hq-3R|VTjJzeJxi0|CJ9_`aQ68kl2hxk^~q~e=Jo3EDNAC@DJZ7=dC`vd38j3w|px5asp=Gi7Ge`^5ptbdF087nN5a>H7QZ*1Fw_MDhpt`CmZwNd{ikFj4F=1c!~%zKafQme4v#ed+QC3%Nl5Z}lXg8boutK@h4b>h1R1;vPO6p`z{ec}rE_wpl8;Yrd@%;}TGH$%3g9m3bkc8#4T{0VcB$G7oZsZaeb=y%;BQ2(S?HhcT7XX{YjSw*ggMp#SKzhr6jt1GAEdSxAIEWR^h4$7~qhJJgz0=9d4CH%feyGgyv7eM_xPnP?FnWn`~Iqspk;O~e<`G8k*<oI?@iageG?C<0BE2JK|W4DX{%Mg@5@%2{8Q}d1Z?ucx+#J_Fg{_^W9_{DP~&$nr1f6W4S#kUgm#qrAYRQAhp&n3Ror+5s{-!N&HRQts@wxmJ+hI6IgS}iw=?}+(E%A56?N&j?~Uxqy2ZNqVy=alVQXBMMAS$uGRtUY>%wA-sW@B<>`er^7;M%u@nzm53z6*aJ3zmw8FW>gUB^XX4)H!4`RYYZtPzU#-_=>H>=t(W#1p9J~qG?(+;y!}b?$N9#iENGv(k2ib!*1~SsZnL*&&j;7H$^Jfjg#2&PN&Ov_E{X4IatigSh5a&LUl8AZ=@i-_O)T2y%W?6|);NF7huNjPD`b`UM#(_r$ueEayZtTkog)KqzI4rr?ap6-?I!MmdiwMJ+ja=@4{D9=rtgCC(;K2b<;NjUwaTdHheG1J%>m+@$<4J=54#=teZz2_d~sgd&7S+xR;kb1pHTmsd!(LL`+ZxzkC(YAJ+|BK2l3sHd{KVcN$l^z`r@0@AH%<LL-M<x)<pi$Fto!&3;pCwF!F@@qn<ae;yB**7vI(3JofkY&*D2iW)k0ewH5j6-@|$L-cNiZSr54{J9@Oi`1Lyj`6v0I{wtayf0+j|&UF;%j{I5E?~;F4@s9Y;u7l8?Lk~%LBPa%bBV0etrER7DMun~7yXO3j`|sV|vRx~5z4+#*8`2NWB=zKaX!$o6-}u}a=i~D6G7h)$<bj`Kr(DO(N|SKD<jsY8`W8YxkG7I}+Wj-5{G2mrhwZb_4i!>iySuKUo}DfrPp*%frT$aWqF?2#H(KhwVyE~n|0l@bVrHb2e;ffn<|dBUlAb%gedljOkZ0aFIe(pp7o)rj<0vy`qU3Si94)?mQ#9)Nbh!A=*v{gcQN7_eos+<~Ki>iWk3r(we{U?l_4<^IH(ZAw$bCA_cT9*teMStyxS~#e@!fU%<2bTD=Ach<KXi<GfOekuT-wtec1wJB^C381b=f~}t`*<)Fc9st;(+9FEQjxGzY*JQ+IWj-(h10)_8jWpxFEKhZUpkb-;MUUK2>~cU_tn<^4M<sU>x5YKW;?-8HxNEgV6s!M2c^{O^*C8@1otR)e+x#F#_Z8*&(=&PpXPM`;y~&*k=gJN0vsO5+OJ*hJS~4_~9$@oy*&!eL{}FfA}OKK|lGX+HU!K@{4$GUdi$E-O}Q_G98D1mdE|MzxeiI+u=9D{oU+YOnjr^0`VQ~dm;aTLgKr74-?;AY!&YB_n)CXmwqF@HDWZj8=G6oTidFM?`)nQc?!k;DE0Z05%u4ioY(*UvR{_*N#+Th^=@E)2kw>fR`Pe^+XHbNjW_V^4G)NK<-dpR_Bt%SnJrR$SIdBFIA30%9k=up-<|s=j_;WIxc(e%CBC^}K90-PUAxfVOCV2<D)6hNMt!mtMIK`??(YNMvVXjk`@DTtQPk5FD!w~qdEEbt&qsgDG6{K``-^Xm?TPl!UT=@=SNnYM>+$%Wn*o1ddOXiX^LYK$U3}M&G#EEk$pzn?R($tRpLGfPL(B2VGd3y8r@DarFZzgYUcD#xCD+lPaa{J#-X?jr+=8F_Fpf*Deds??mvA5JG64M{TQc-Rccl3C)Vbi#E-UTkPP$Nh_u1)ahfEDo|I*)!?>x`roBFBbaULuszS%Jx^%*!`j*BrS5ZjIT8+rB|M?X(dP<*RWDqPQ}RL1tUUYGeESC(10e&*`1Qu1E81V3$M<c|rODD{4Q4)a5c+Tyr3xhnN{#-0`5+}{=D^WpmA4p=6>vF0H9RnHN)PJY`TdEDu--H=Dp->eRy@YnlcoR%T+kKVq$!y4p&WzAOV2=o!(d2)HQ<XMyp*S(eR@cc2}j`DRQah-quSbRrFUChtC>xlEtc}0BV?j4k`(oLQp&F4;(pLrAG!y)T&9);u=-#sEX#&tEC<GjmIMDCwvr!44io$jMwWyue}1N*Z*_g>jfQD5<0PCnN>8YtzR#nP`z(9eH%N_jId-74>XZp2nWo?x5!jt=b4*ISG4to8-R)1UqMLy-9P?lIy!M>w(FLcgGY_Pi;+qYIw*&7dSw-m!VjO0>TX$8j*uFLTRk<e!1@k6Cbw_{PKj;#-M0&oDU?uAhn8Ay0Hi<XJob{d4F$OSaqiJo?p7$#L9ot`gtgtq}UH&m`&Ru4Iekxx`5J2=|2vvt%6T*qb6;j?4M=@E@7D4nL_Q;}=Kr);PYOE~DRmxU^i_|KN7i^X5~jza#q|@tsC?>{n~Fr@PxA@f}Bdz|S=U{*>0@n_GGPiQNFdQB(1aU9&I`v*U}*d%7a3B7eQO<FZN0$NB%<zkWWCJeRY<zg-x|x7~3Z$BSv;cS?u-`u!;S=j$)aB>!fPOE+gk`K)g7%_lREr}6;tt>Wk4`*ue=OlpgEm@q+nYu!imhh!(=FDr%e9rMV3xtcVW`C{XnD>DD>PK)DfEQ!JOD)JKiQcp3jxNHjMxqK?X5AwnF^W{SH!whXP@BZ;9`bn8_IKOt47vEWO9_9^pyvB2NdxtzPx|`%eKWSmdxMgQS@r|cNaK9^;665U8vlh#7Z1BC@r_7_d#CK%QwMg=BD~ID)y)ovQqq;2gZclSp8k~>!Ylv@sJd65QNrv|H%PGF=Z9cUB*)9out2f4t#>fa9m)w2}6Z8jjE&4-=B;p%mINn$~8~q{Z{Q}9K3jM^q{u9pkMo+{ytD~Qo-S^@8Q1=({jRP;yPr4+NaicZtg!uNBd@i%5BLD5Z;#>Y}Iqz2*^D_r#q5S<j$nQvmb{PG5zWlviWgM>~MR5N*9U;Db-AweW=xMlaxO0hbuFZ(+|Dxh}UOw?=o|J!Mp`JY&;yRG=q4@4I%W!-v7L@C+%QsYf=g@j6U$3gnle>=Jk$FMK@S3;|48eUl&UcPE!0}bOnbMz&Y!Kgg!*Nd87qVTW=pgt#-(kBM!ZF^vol1PyiOM+c);09=m=E$E#=R#N`L}nL`A_5XYxqY$a(s9f?XV|G=B3=x?{PnxI2Gf=tUbjy?tMo4f9i;FODBKKW6gMqdPeNTIQiM9nbLj-_8`xf`^Zyjg!rztCD4Cr80c?L28!>#lNaTG+Jte-?tJ1q=H9~nw98QJ?}Upp#Q)V9js83q*Uv{C#drUH0rR&tJ06tnF6}4B!TReW_P5;_?C<<=nUDYHd71se8Mah>=dwQVOQu6Thu@I*3D%GM(BJ;JhIYu;K>WDpU$a6=oG$@2#kX(Xnc%u-UWuHN;QZQ{3I1=}#doYOggmnY(EqD^E57lR^8*vh;QY#aOy+&v`>LX!f7Myq$1$R*jE|frm!cht9+h^m`z;?Y`&;-=K7Tco^Uk@|6yIF%vy?Xv9g_0SQ5EoB=yCznb7(iTo9*;i*{^+JXwP~-;<&_Y72n#j2>pEfZCod7RfAvXHqNimY?8;iSx|h}=u#*jUK!_Uu`}|1!`|pDw!7yi?APfK@y+u$&<_u~(68Qwj*<Ldk48UCQ5pTgx**T%=J9T5w<O;pf9)Rf-p{oS^Kxc*2*wE=hL4nXe#YzS54F)BQuvLK^7YaFM&eN9X?Je8w13B;s82rw<Ew1N#E-i_n&nEN{JrG;B!B7*oDW2Qb}R|&DfPc?p#H-mQU8^Hbd>VtTcLc~k!*)ep;CUq3HW`YaG#C3-c<H?80W)-o8mf?Y^nIpSCdiC6n^k;hSZXFo_iYm+suJ+(W6xra9lXQ)FKGy<HiEzCI4p5`&DXz`(ut`57qp%QQ#Y#r~UYRN8kPRX`H9e)+8wJNSOoY`@A~|{ji<z$N2B@_RWj0G49=aBSCp*`=Xe?`jS}QE64e+ZA;<5-nh@(H;(-&_kG8m9J{@J>*0L4k2^m1-s$bT+t_ix&h>h0f;_i7<GHfuy#&6aT1B4MZ?+`JlXM;0Gt%0Wpq{25uIFdQuJ`uMcHuZ*ZgpJk?K=ltM)`T)C1@X`Qa+s5ufr4gjvwm6H&@O`kbl}-_(Mu0Xiw|pVa|7Lnx3Hj7yJdkLDwDLzU#{u_@kD|{l#&(K>6VR=qIXQ1^-9Cay|^H75rcQ&}V7W;Q#2iR`jOO;Q#3V?qy*;#n;XwGkdY&vR&<bG(yjbub;nGO1}|OUOV5N9fyxZKTddkaK8^7BmYjj{<uBYD=DX4ugt(R;_KHpdr0=NXrF}FL-(e#;{WUVS!*?X?RsmBm@{7T=+}AA{X+6-_Y14)w^O8?c7L(o*e<?)KXP1+6kor8S@|1G6<@m#s{5w=UAu4E7lcofdg}MzChi%s9qs;Z<jR8akv1MMn)DD~A3qrT(#(=_+Bn4Q>@U7PZgFJmDgM94Irg36|7%=y+$QhS^zoJDJ8CYj3kk<*YFsD3wQ-&K;U?b8Y2(8<UmqXZLt4pt7JZy){QW|FeOwyn>*HAWiGuTGJKDI{<rzQAerV%oHQtsy+IZW3$|b%&K6iV@^YV9XJntMCExtbfcX^%{B(L_o;0S&%zW#h+dY)4f^g}+U*bjAquRR}Gb+gEN0sVQ(et(g?m)4)Zj0btba9$*QUUPb$@1*_o=ewoBOC-PcJZSi~6<>dTG(FF!l1F<!HJ1MdUw=N04p=7tPJ7OEd7g`9``UA{>3O~u)t;}_^SF2W#EnaxyE849yxQ}-<CkpkwdZ|fW7Xve+Mn|ValSrp;27UPe0~1GeX;Qm@^@`M#Pu{0)|F`UC-zEnR!BK*zQuiWm8?hj*Zj=TcjD{wIgUi_<o&-s|D)!SM74P&=jJsiugyDIJ#UJy&r_Mzz95e_-=*fqq`WpiW)@2?zCO?9aN6;HMw{QW+?~b$*L+~J>*DM4htA{=QC^#GbS{X+Iv{O+(wR3s{+%|T>1x&y>teKdQ8kZ>dL^7kwZFW8`Acm+);e_+>teL|-hX^;zSkXF1lLz>-q^TW9P4`Y`R6j<i?7dDJCZFF|6lXlryq&0&#ODfCY5z1`aHavx0m1AyuG7+zI6$XBi{>H`O9E^iuQiNo#nas`uhl{PjRfL(BEGiZH09o+ItZ7-bBi4?@cV9z2fWdS<Hq9HlSV!-^;j@zY|}7k7NFsMb<m$?}MC6nqeJ;_Fl=I={VN?Y45Yt`>zD;#`j<9eVOFf-<Pc~FYAf)_ipB-s^aVK>C7?>HsUxXe6QzvvlHdD_k-$vqHJG#pJ=5U0bhInXiqu;>w5I}m9rzTzEXR?sos-{YVS#ny7{rLP<!9%`s-_~$I;%;IxaTD`VsAYu6kcA_0rxKn}-*RufJb*Bv}t%e^0$)=jH_M&-dD9g;cU1`ulP9K3&S`@6&U)hOfP^cMM&FJlgwxSCdWR>+1pRK{4X%>j%_&1M#)>2KI@c(B9g*1-q}WtPj%HIjHp#vR!Sxgj!!As;#duZq>m$BW*o~TE8K`we=hBrcvVmYaK}LOUR?G8?k3BAlDmxor(3#AMf|Hbt!5ci~Kun9gA~P81iWAVbuB=`Mb7$#;UYVe0{x*)$9WDXzO{b*YNfAJZfE#?4PzS$dx`Z?$6q~qc~q*cNFLA>yGS6N@F|Px+Y_f19`M{P}Zo~*sivo%GGiad~N-ed3*`hC28xm?Dsa}eU7%i%UZk_+tt^D?YND<>+8yXevR#F>(Gp#zu;@@*6dk7ZAZNmu5)ud&4G0m+Il%>$wKh;^>y_dp<ih0^sKq9(I2&Sea>s0#Mjpc#`*gCKzGm>w4b)l(DR%GUt5>x8od(r)YdWDAJoF}(bi8oleNV8r>(biW(&jlt*zU1zYd45t@E@_M4>&j^`g$wM^Ii{U+OOO2YhXvs?j?Z=eM@5)qXw@<4tWHtjnx|byC{8S^LA5xPNNvZ{6-b$fK{<oxBD2J$-#|^d98V*9n_HVI7LLuGkv>JMwGmkj-C;;61s%Zh34&_}cnsXW&5G54H8u&I41#*Vk9ui_E~dQd^Jh?05p@wRPR@%I9(a(bj>xPu)g&ZQZzI)g#>Bv~}jL5ihY_ZC$#f_$Sm~TgUF&Rt@7~ZJoUHLQ{;7v~~6N%->=>uC2qjMh?YuhPIyHXfX!!8QS`PYxX{jqqXk{Ts>UKuYGr5UOk3-YTqe1zI}!5YTrAUgR^12P5Yk0YHY_iOZ)!9y$Itq{d)~Z-;$U=*1qp>geJl`TKnF_IGYr{_I--cDm&)kwC`Wcl6f({*1ngqhZn$enErjup|Z%YeUD@KF2QrK_Wh3gT3<ZxYTx^~N*%=Wnf5(VoUea3WVa5Zy!M@u=`6HQ^6TF#P2K=s`@YFlrsaO|_3xoFU4XBBKjnIHMST5xD`%1P2gKLD&vNw1F24Rfm$|B!`2YI;t8W0_7ir&%8Sh%*y^!{OnN{x~-m_`nqq*js5I@29YmF0pl~;Gy&F?-27>0_JhM&>3gV!f{%2fZw>3@Hc*Q3n;*C%-u%T)Zoev;SOQ-`lT(VN<g+?za{>Ld>*Pos7rPa{vK&LK}HpQZjxK1=qq8Aetc^a_6~{|ZC#66$>N5^`VacjUh0jts@^so#>@lUq@nlj~6HQJa(Nk!w-EAuDZ6R$7f*j=9QH>yhj6@8ubaOHiwkOOT6FtB{M5^HGbF^O18<i;#1Wvr+Ssvyn3~6lbR9Cub&Sr}~q#lXFtbkaLm?cp`vWnOcTinOv2jxGdG5?9c6$WhgF0^&=M|XQZYjXC$ZbL<(whYFct~aw=+iaw>8L>R03p<REGzau7L;p?D3oEqM(&lG>RZN#0BCP2Nl1M;%VyN8V4JM&3_8%}{)XI-RWaEcp!C*9KMRm@h+d8(aK&*oNAUtaKz<sYz}_9!vd^JeC|u{hh2dh8#)W%}{)Z`jmW#e3<$d`7qf<{X}+=k5Q8(0v{uvr}~gpD86b#D9*;ee?`tlE>EpME>8}kRwf6Lt0hwNu+S>h%H%5KveYu<vgD%FV&tM^JGBT|X<o9OoSmA3oSmGBp*Rb*Fj;8<au#w%Y96xE4CIXDGz`VbsL9DnZDgfiY~W<%#EB4!KiZ&g$sftjsaMF)$(N{G$d}0b8H!g@N0L{Pr!o}xrnV#ZCbwlM4y0x!2a;1V6hAbe>R$Dbq4)?xaX57eIh;I%+Lt_p+?Cpq+?Cvpp|}mTJy~fha@_r_4MTB5hT;%vIkM7{<Pfrh8bDTBnd~6fpjIW<AlGIn4yKkR2a_vM3y~|3i%~O@i;;6P6lbBPA!i}`8u9l4UutTyFS#(aAh|HPCbcKICi#1Y;;YnO$XCg^YzW19Z0Z>udXc}Cf03a$l-iRVO3q3xNX|-5N=;2pO14o`kZojxn%s#0PjM1zDsmFC4>beXhg_N(L@rI9Kn){LAirQJ{y<$r{y_f7Q2d!1Nmja-{F(fPx{v&YtaeuEej|S86{n`2CaX}K&W2E&fqI6lRNV_RFci0<wjsCSy{#2P@i=NEIg<CYaSX*17>XxT50NL6XHgH6XOU-9UF6y1In-n1W4xcuVJM!*P`r?OmAsG~&QN@ps_uDr`CD;5-UrK*^N}l2gUFT0HL2CeHOY0n?u&I8ifdD=l53M|Py@&{$fc<7ZQxSmMAWTh6^eIwVlZ_Gbt`!Yc_>5iX6k$LX7Zm5#eUqDs)rv#u|Ksc*`HjF>L4qvLM}%xO)X0<O)kMuT!>nfT!@^TYA5F=XQgH*XC?bmGm(ACsTqpXQnQeiW+W?3LrzOhNlivh#(R89hGK)N?(qhHD}HB#J}18;KcZeDKO#p{_miW^d#EePd&m}bD%m2Br}id~C-<VZCHEq?W+*O24J4N$r>CYQrzbx$plW>Zh@to-^$7VSc@;IByox-EI)prm+>6?k+>6|S+K$|T+=AMMth6Dy1-St=gsjv-R$7DHfZT*yo7|e(lv<nIlw6k@Os-3=POU($POd~PMy^B-q~<0o%|Z?&+o`@}J2?-vFgXvo6hm=+YE5!|@(Akp<PqdwsaMIrlC#^OYOIi*p}0OnaXo4tay@cgTm0CfE<<r0hT_@`#d)b}%#oMB6<=Z~?m-PD_aNt@W+mq$r=%t&rz9t)+Q^B?iKqry{g=e}=hPQYM)e^lBd4R5CZ{7;q)s4LBu}NjAWtQ~^F#w1^lR!1vI@lwsUOHH6gQ%NB&$%|nEIKlLU9x77qU{-08JQ*n^IGgo07kwrXzntZpKjDoSK2Gv=v$DII_|S<mTkKJQJ8(>13~MO=ew`&ho0;EY@A=Y_ifhUi&qNZJ>0XExt|WvCWh&w8gjKLbkEea9ezvhx3>;pe~|@lNXV1QSXv(k#i-2sxe9~hT@9UO5}><>eQO#>f{h=9kSBe<PdT#Y7KHNaxk?NIhb6MnuuJI{J{oQ<B|^y#oHN*2ifAsF@qS2<IZ=*an}LGb*V#a@z)B)^{7K_@z)l`an~QkBdD9nBgmVmf08$mpHS5p=m~!-PL~MkPfkb9&rn>PT8><t97ruq4kQ<(mLMxFL@r3qNzF~pNzP2oO3qA9PxU3IC#RyOCZ{4N^~5O8J}&jd7>42%)NSMy<XzMg<Xz;m)a&H4<U0(-uc!~mugI~~m*iOTXX+cW(!a@{$te;+)qbSl{-h==O-ojqlAMC9a-`(NJ1(c<Sn4~k`n+R(l|J&S|0C|7(rB;!jb<At-Q(3Jd)Q`5Ew47T*v3l7d$sv^9uuX#ypECLp48Ulp5&Gc#bv0a$YsbGsp-iX$&U@F8qYmuC_Ya;Nj^_rM_ol;N1jL>MV?6RPwhqSPwqzTK<-BFL~TLtL~coKKvvp>95+^LN$pN<N$y1LLsmM-EB_#FU#aO;ACvV}I?t>A^St(P9@{|acCR+s&Nfqe*{cmNvyGL$_G)v*>X<0a>~)MX^B5{E?R88`^O!4bL00;mSAY19eMIRf@+kHv#rZr@%oD{uG0wByS)LeRfLHMMMo+jrv6G?r1T}_yf_#ViC;25ghHSIpcUh0t^h7mv9^2rnzgMDPmVN>LO=%_iU-5TRawY!$!xJ|>agX{l`5yUK>QCff$)`MVz!Q5tv4Np@En|t7uXwp9I(VYJCwfr3l4p8ipeJTf`;nh{_ARkTlX;>bH8(XeIX5{QLvbQcJTah8sfo#nnfEC}@pVsZ_QWDj{NRaY)S1*p<eB72o)}MEOkG4?Ox{G@Ojde;yonq|y-toI-=sbx-y}b$s{Mb?--?rXwNVm=;v$}?NUcCENUlIGLCsArLC#OjM$S)8OHD*hOMYv_xBFX$;@=pGuTh_ppK?F1Q4f%>kq<ExZ=-G|Z|1St#!$T4>-eo^DBj|U<J9%kW#skb8Pu8N8RXH_N#xPwp<ex9C`0i;1J?qj<EZ1w<H!rCi^&Vg8>ySf8_6ze6gi50!o^S=Lw!z;A-|+1;kDu=IVt-|5pq)US6=<*D@H|I{53{tb!tU&b+Ut6f$Sg$QA?16$R(-y$tB5IsA<Vr$bTD9)wlj;D89?%tMnH2E%`0`-z|pXqtt8UYwTx78H#sMw~@E8KkcAyA@3j`^Xg~EsJF<sm{;*gBmREj@7b5ao=D+|KMZIp{w_>bT8NyA>_g2#_93V7L?&tgH3vC>T#j0ZT#j6YT9{mgT$Soiu1c=VP+XLuI5{;1Id0#Q^S9zxp4i}t1)iA8P&|gAcq~KlWQO9U48;-D4P>PU$r0qk)Enf(<lm{U$V&ep|4x2GRqg(U>O)qc_%CW2vI@oTjrilCScT$Pk3R6keNTL%#*#mgbF!Q&pOc}uJT-t^o*YaqM-C>}pjIK*AlIT+CD$T{P%D!|$Tb;?D=`#*MJ-A$%3~aN-B6sAs@ga1I`fLxp;tTxan~iqG1P-b{B=yRi@L#xzwRmCNS$lMUo#aiq>eG-ud#~98S!Jae$+AKe&oT_vE;Gre}fr{hk0TObvAV}c{2OxY=&Zsp?E7bf*iqqxs{>#C+hFypU7_N8}b|WIX6S`ZR&gSZSp;8EIF3_?;b<(IfmkB>I1UU3*>0>Zt9O@rOU~?$t$T-$Wz!ZD;bK{QZ4dY@-FID@>aIRE{5V$R5#hpeLh9KN502>JH=4EhZ;?eX1(`NSCUt<PJ5`k$f{qdG5<L7PX69VR$kl~`>`iZd*YfWeqkuS%}{)wq4*&~@ox;pXQ-#iXUI{W=<A7Tp6Kt1iJlnliAmG}<VoZy)c)lD{I^pWikErf2kLa{H1afVZ#qM9ABN&C48@(O{mGrkov8!Joypy)!^z#r-%}@&zbB9O#C+-k>O}Ga@?z>F@?vrrbqaY3_cM&4IKrzfBB&e55#)o^C~_2!%Rz?Xlhj|xC&?EXif>SFlik#3)Z64|<QLTYWTg+uFUYTL=!Z)0Q6JjkpY;^~O8w0i|E#C@6!i@G6!`!(ihO{)fx6Ka{|u;jIrRtfa`Fu7bn*;xKWZPc(k|qF<gN_G?HP){rFJ5JOAe)WCWn%p)b3;_xg+&^az}DE>S%H|@-SO`UmV6zJl7MesH>^-$*ak0s0+wz$m^(!$?M4LsbOTL5#;scebj?wr6<Yz$j7M{$;Zj(s5i*x$QNw!{qh3!GWi1e2=ypg=}vOv`nE)ViT_{!cP8=wsr7|Mg8y?9{a+?ra_#*u7kP61vjDqs{iN#sl99;sKXsEouU26i{{sRMW_<'

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
