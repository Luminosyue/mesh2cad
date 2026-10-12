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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fb5b1704b464f5c94b667f1b630bb39/part_002.stl', 'relative_path': '5fb5b1704b464f5c94b667f1b630bb39/part_002.stl', 'source_sha256': '94c8449e96f9c7c5529cc6f1867bc8ad7292bdd64a54636a7c0ca108b7a2a9f2', 'input_faces': 560, 'input_vertices': 375, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1658342182636261, -0.49997636675834656, -0.220918670296669], [0.2733779847621918, -0.2602289915084839, 0.23458117246627808]]}
GEOMETRY_BASE85 = 'c$}r12Xsy8yT*4Aoj;=269gezB4o52MjO2jMms^&5h97sY;_EyjFODL4Td11N3`q+qZ6Wyx`)3m%7oFm=X;+gGbeZb?^<`=o3-9~e&_M!{oehxz0WzB_N_8!DX8JcQ!^5`-q}!2(^TZv3TmT*M}`mX7aUeCWW-oEEuZ-6CtVk|?b4=wcQ<X6Hojv2;IMupE7rADtUn;2qK~cOfZ-#<M+SxT89uUqu=1M)eH#|+^uq=PjR<zWuH;w8-^b?X?PHs0`#=8Vbe3SxTlYwyQ}t#s$qDLp?Ab*1+6rv)n^LXwX7RPh{Y>@RjNU809&$u{BjxHL@n=st>Y7KJQtP0+esEuWBVo7r)|F|JUwe@2m{Lc{lIN7KyQd^czb9tHZ-(~z<iqhw&D?3?n+eEon9uh~-WOSqE44K~EP2dRvkpuCOFrW3QR{JC_3KLgMx#37TU)bBdn@Neso&AF`Ek^>ANdOg9gypIdQ*J!{e<)4U#=qKrR{lnJj1v}mXDV_@4QY(`yaL;PoB|xBu|Z6;%l!i;kx2`no_TB7vIrqtJGtQt1aVTyzPPZ4|Yg<)A!5)X_q`je0$^@_)Yy~Jne_##n-deNRd1ruS=a~i$mhuw#T8p&%Ujq1+Iv1g&@Cm{OUgWy|dTRZ|3c2zrW*d$zyt)l=iJdWE`|=$x^2+zwb%cI*lxEcSyc%AtznekF_j^%$KdyZ1IgPKg;zRThg!|B7YU%-uHskZ?=q;b!HpC;iPN*j<hAe$iJ72MLhxVZDZ^^q}}g3;1Bx~<J@Umg4925ulQz3H|f`rH}#<8$$LnAJs;<5M8i1owfm?)*jwt+9*n}eTKrUeN0mM3cjAX_^7=&HQ_^p#cwDcWXLN##uUCmh{$9lwN}ZoOim#R43V&L|(enEEAo0yt(eT}y?vcDPL(o2FJFLSt%Vpi_(}$gMUAMMZ(_`hj+l7j6pMZJP-G}d$b!tq6|9LIef4Nv$hqme8!LO2t`rrH-BiFTHKJu>_cR|LX%M97iwipA~^$Pi&8*-9pu7k+4dOr4bfhgH`wvWlUu1*J0&yi=_rJwkV@GIX%{k8wvFRuq(L%(H?reNH<$$B=Xc%GL0i>pa~`@m=WWt<24pLV@oqgm)K`Tf8E_-#7LxS7pQC5ooD6W?*}Bi8e~F0!7}ef@_dtp8Fk*URrW?0MStdaV@q-SY1>dLjQ1-;474KodEqjO7ExPd^8&4IZnduHDPf@6=|}uYRh5tbe_FocP*lj*s`e)skm}iGHu{L_OZSx6A7}hcf0byKueyyXOhCcN;46<=9hC_EEZTb^RC4hdw(GN&BTKsDH)+?2GK}<lHv<Uq=3zGdP!Gy%S`d=G;4-VckZiESA@vPmw3&GS{=;Uip2Sc1HRge;Vs#$Wu8F9qY4;Z?45YGE0<>mAc&vif_-1^>4NKL6>oOR0!>P{#)Uhw@5z)yx=$Aj&sAOsO(eobp`RY@{eU+^yj!wXs>&UpMF2G`*}ym_3a2l`^0@%Z*8_ENu3i%qyD$=WWMaHU*i6FdaC%2Ak2&HMFm;UdgcYFfBr~mZ*5#B`^$K+5WeAsb@F2t?4#k!#kVzShWl4Q899d?+g_mknn5y;_ItPGx{R4G#n(NIOVVGBtGJ)JeZn|+W1m{}XC0Q`dkO#V`_8Dha-M7Bvz?Xp_s?J)?w#K${njZhzE-^|#^LObvR|ycp5oib4o98Wp2~S{rj<qeV{gUR0xj8(y4Fp6z2+ad-csk~dL4JWqu(7Hu?~F?$vI{fABQ|qhcLgnmi#LD?oJfnG5!VW-&s-4XWOEwXkR4->#Ep9Isc8u%g}G+4Xne#?SGN}Dy~5LX6JCdqsv4~ztcCM{rFq(zX^<zJjNc>c`6xxvD{nbb-RPe)5}w?%dvL;5$UIviSgN%iu+Wp#xbHV4kJ&#&X*-m)$O?7?>h#+SShT}!AW?ocyS5&vz(XlakxdvKGoXYM*h~zWL-I$Je2#FvG)n;|1u2cdC`}$zw8w=CySqFH2h9!avw?eP4DtJKUe>Io9Lzd;@f}kFYCulo-5~}*4RUQZR{+xpIR->)z|NKLH??y-1qJK;F}&%vOXOPcgT5YZ&w2Cy?jxBwQq1gDpm&V3y;Tsd6r4?TYJ6Ge&HJQTlC~E(OMNyPoRZyJ0AR-Xbk<&yU{+rz09xulQ;6bpNsRqO`@z5^P-RV#`9F1dpUoS{rk7yYbE?1Tco}A$rpZW9rugJpXK~Fp8KKS^^<V^q<Zd@{(Ac3x<<?v-&(v=_LuEgZTS15@%-agP1cp(s1EXM+=KC1x=6+|-PezB-j8;d_V$<n@vSBOCBHo`QpQcM@CE$Zvt=HQ+f(EmOZRO%=V9MPtjBs@1z-2*gy)=5L2_Q%7t}?ap{>Q&ulV9Qwr6wHx#<eV|J*vczgU}Fitk7$jrFtASDxGTRjshDI^@10^?1+1b6C;V@SAo<`|I7YK6AA}o{}TE4tHQY+jc;|x6&~FvDf9Cw6E%ndFj{_=j7(|vQD&IU!%RxBkZG&!P4H?+!NQ^WHRoLPfE)3o8{FD*V|zM#%)uytOxtxAk<lA7sfg3&+@*&y3iN?GKZ{lW6;sffiAw|UWDY)doGjvrg>o~`i-eA<7OP_D(@FGzYydx8_M}$L=KSqyR~vS{03c+e^wsxwW1^7A8stZ*2GKBbNf&59T&UeT)Ng-o`0;Vp}4LE6>tuR3_I-VTYv6Ao!PU?bs5h_BEMgRw70&rHc7v?!!Vwi^W*-~zqQ;K^d8~Jf3t_wV;viw;OZMORnf1<W9*j;Y(M5tjK7{+&H<}U1p0l~Q1aM2o|OHf+ecyC{;DM7<LL7l*X27J*Sq8<`fdAM)~D_@2J3uQD~#vTW%3-G?rU{Rh;MtoZ<lL(Gk%8DY4fQg=c=A_9O{{W4E6KAY)*x*t?MXx^gT22{xIG5T!ner=P&m`?IZoxnc)Zgh4&YOCLsT`0qA%A@g1(dzPG*j_Q~yVAMY^{^W`-R?QblTb!+<S$aAa#{D>$#Z%mzv@&BSW#=+}L?CWRKc+T&I-{6|;Q_VgTb=J1YKGnx<mGx%${($k(UgLV_&Xjqyd(A?fA>+i?Qme}Pv0s=6-*cK=uWd#DqjFuF79dZde7G+pHI?;aU%3$T82?oIHI3!6p7kP&Q2)?ssApEgEv~+!>OIM04o^j%K~Wf=@|k{@*ZbY&+}1y=MEmbnV;`B5<T=DjS&ebf3gBD{-zVdv#jin~V{?da<?%*6o7N)FZ~2kG<Rz)cEWZxx?e`>%&&x18SJQXwzlL)xr~v#N>)|hmlKl3>Xxs<?h(;d23+VUESF%ow@>|e8*GBPeCvHm~Jz^W?tA3i)qgU!A&(GGt?eO1}xGH&T{V4m<YP}QJd*K!G&+$rh^=<xNV;p|YCF|d+xf}ENu!rQ)bLZag>T4SwV;lmeW1p6f!?^9bBEIG^6YsND&|gtXe53DTyq}uC2mTR%@ojF`rC;qsJnDS1ReY=C%Q#oxj2?yS9oBE3t8Xj(3Hx+LO?i&8N9;xYoz6@Bj%W8`U40`W7Wc0c$(Wac`;cc<62`$V2=8xG_VZj?gnC9dmiwu;DFObQ9LPUujv=qhn;4(drubTy8!`^s{6yYoKVy6*e3o&r-XB8yw=;0=4W2Fe(|vnt2|VY|E-25LT0|1oxtsend40^oboI5rmPo(WmU*~ee{%$R`s%2s?JCJ{wEhj_5P1u}cjyNB{fJX&-)tz(hx1;Ck>?ERAOA?&+h!k<>(v62F>c;1uVMeM!t;OO6x8#_=<71RYX)MR=fSs59Y?<<ir~3!$_3O@sVMe)*01n6RLW)4^ZpmfW2DTN>(y&sg`c?ThW!4jV_5&?u3^8lsEhTVzmtqxy085lfamb_^^S?3{RZcyi{!CQ*^B(vEwp#HaE^I>!t;5Gg>_i2rOczl{Q<^@zBRqO)bA)bM|`v4ZPYVnE5;|r1J7Ob&0YrPv9p(qkG=3+^xOQA)MGtbDDSh<eMiLvX>YVUCiA7wWBa<v7>CCzlQ3TQkpIDb@y(0F@!XqwAJ=>Dkc@*_a0fo;9ryt4FAtIYmh}|tr29kkJ8*%Fzm+2s?&A#~W8P!GLp?`J#k=}?ld9r7GHt=St@#A)tBjI<t?z5&bKZ^cjbwkRQws~1akG}E;=0D1M4o1z@_C3g`5DH!Ul`_VV_&H!-M7yVmpZlbi{mr+XYXKt-FuCC-ow{k+`#qz(H-+1{v37gS$y4fzW(-$Z;|$9u1GvTbpI3eSIKr$>N!4I-j7(V(vW{(4Ay_2*;2p#2z=Ywc{g0=QLFh1d4B9IzN4($-UJul3T=z_KW;zZ>YLRXVVzuAa>&)!=dG50ZJ%Cb$ZzY>7~^xky5upJ|AqX0x1-<OBe2d3zs9&tya4~e#>5Q%qiI-IQx3{=a=LH3@Coa`eNPz&`#kv8uRoyvu`w72`uf`<;_H{~8QR;Pb;S6m`pbIIv%f)}2RE_KA1uP>x|8AS!{V{8pP!LDn)MFjle0YXEdD6-ZnpY>JQJRw{yz%I`zB+u+c~ML$wREq$meoCXx+1jZ_ex>^Q&dsjpv_+S>bP~hx>R+TY1jW<KXM3>PmY@|F2~p^~pKmUo9lQv2;DojqqIXcRj*=aM}aBpRJKke8;yj(%!Ts$i7bZwekJMPyd|IzC1tLC)nWMJtOPEC{zILOPoQTC~x_E)p+M2zU@^t)br3CpC{0_FEDTpS8XKEOJ-O>_$BrukN=fKSKpC$3H(n}j=1`^=Lax8yU*Y`uv=k_+o?+E_wZxfzs|$gdml%h%D>6{S`CVdZ{&8rCGB_JlJVE#;A`b{JP*7&gzukf6hprW*YVu4qNDU{M8mhv&Bguqd>}q2EmQ*6b!8pqt5+1B6DF5L{>Z+l=e&mZ<L}^G%Rfs!=CJYjJeIz`CJ5`~Y;&ncOD%=`z0ZqpoopiS`^;`-a9w>S!*9G0`!voIerq4xU)p>l?=S2%%4X=-dNkc|_4O@nFki+cIal@QvKi*x*1jg5hv$~hSbyNK<F3BeK8N@=_k~!u^vzs%aZWDVEaRz7_R5e)dpT>wfAa0QxgMTW$l%*TZ{YK#0Tpq*$Dg9k+)>!S^sQBqa$Q>9F~?;dyH$dps~+;K377S+wem)u)t9jTi}&8`>RYq@Wjz>MJ@NT`gUYzxEu~O@Jv%<1jINTQPRCh)e1BQi2lF^14eQn;N%n8Lul0R^`&TtzIXBE@J{j{AtA+1L>FcX+;d*!WmiBsBb<`jK6UMDk3EX$++XshXzV2<2=WXLj^^EIb&H#CzYX#RpJ!3q@*GJS^?CLwpuElfg#Bk}?ev9olFT*%ox-IL_I9C(-r*q#`c!AIH4*O>8x7laY)i;h+Mf<^>@%agTyZ>9cUi+eZc>mJCFXMVJ7RvWxT8&y*Z+aS@H@^Ez)|)-LR>tw%(NsPMNcW8~A2FVN{qX+1tUs>nQybKobbY+ME>s)izX<1;zRL52<eytRLw+OVz%*(9u1?1FyfgyOV_^X}X9Aky+!*~4`|e3V#`e5V*}K)v;Oi43_qh7{!uL2g;y&Sf;pz>LzxiyuzX(Z_`7(4n=5cH&o{P4&kbR+rHA0>XckuqM^h12k`~<#L?*q=ga@TO4Wcv#Kx?^~by7X4^=sJ93a5s#@>^Jyc=SfS<W6^SW4nHvg?SosPp436ef2X93r`D}C#y{#bp2L&s;dwq=NBGCS!Mx{deoFG)?40pD>0APz6L#%_afrKse*e7{*Lx1WIV2y(IT7D~oAtY9Tvtn8<D9SF4gS$Acpkf1`K09A0ACLsjQzWF1HKpc?2hX#)e!4sL=5ZifqMKm<2i6iIKGe9;aiq2`SpGerC+0KZ}<@#ux?xWpG5ue%`7eOey!$WjGNvcewsJV+ip*=KHt(mG8@lzJ0o$ukApLw=X<;2d(+?nsQ>a@yzgjN58tyU4@CQuy|G`;rs4a%mV?lK_W``GcbkLn>9Y>Qe8tX`JbGeQe1Dca0^?>Ij_0}p&#+FCLNm;lBRNQ}SFb-3?H{bcIeh#B^6!Fg-6@9gX*>0lt8aE#gz?XxDtXMM;ixCeB#c`>d{1fY8jp2Yegf9X=$06V4HK}Q>-EPvFV+G6oJsH>ZbSW(R!DwF*6)yK{8zZ|x9xK(uziNV^7&%lu$*Rb=RY|khgMJ<5ajYFKFU-->H44l#Ak4=|J9%P_}8xS|NRr6T5g(F${7_HiYrkIla)Twz?I0)7>ajN{~+%qPoW+oPay|W7m<U>9jHUeO1~j@Ah)2lCbuB_Q|prb$rTxji&LwSi<1j56qlyj$)(9Ps9ni5$X_xPccu;|EB%(-i#m$>EqN3<oH~LWP98&@NLD(XJcc}jI*+V$A$bOQJwx$N)CJ_9$n&Yo$x3&V=aV;4x003aAa5eaQ4f&g$Y&XfFH(<_FOu(5|4ml<7x_N<6ZHo96ZsuOv6mav<_1=w*v?Q~kD=I`s(#0t`jD(bu^%<38(4+n@(jfVsrNLn(rolqC@w*DBbOi-p+3;SMacQ7nj2V!;-b`Y<f3GMY8$dYxe-HgFKQ5Z1a%ZOh&+lMPIZvO$zjxi<S_DJYG1O_?&QJb;ndFL;pCyz3gn^WP7KA@G-xHV3dO%r)!Fn5LvaXoCt2wfatOIQLvcH5Fj;8_ayxQEY725ha!rO}PpUszX+^Rpxd^p5xd=HQwE#IEIVVGL7KY*+48{4WrOElp#i%vNO1~r*BUfN3_M>(t`;qHw|D0>}8H$@ygUC(EeVh?S9Y+l!2l02tQAd%LhLgvUComL$M;${}I)nTjc@}j&c@{a6`V%>lJcprpC3QY|C3zcl6Ip2-c^mmK^(^@?`7}fEW$H!pW%3K^eew(PTk0qBTXGgR=sU7fb>3xRC@#QI>`S$it2*N=XSAX=B)1|rWhkyl^(Ff<Peq2}2Gn}w2IR6-Z?aN9a#?b7YI$;Vayx24ayxQshT^u=66Chz#?&I@#^f)k`N?09t5b`TtCOoy{mIqHwW*EBwaJwkihEFdk<-uI9t_2UoY9;5HFX48=_vBo<RJ{j!>HlpVdQ?)FmgZgx75MpZ^<L6!^ujAl1GxuFchEEpq<D{)meO!p?Dhg7xFZ6e}>|Y)DW`L?&OZ-uc+<FUy%c-4aosyA8Jjq54i+Gu?N+Yth5N(gPfb1kDQyFouSyBnv<+F3)!8VNyCp)H)<BL8#yyI2RSo28#O;U8#xcP7&#BQFtq}?Fu4@fk6ememRg@&mRyC}lw5^eo7#t5n_Q3Dn_Q3FnCc)aZANZPF3(Wx#ZX+8+LFBA8K<0an|gtKn|za@_$l=<`6)Sv8$xkbH-zHfopGJ|ilO)}^)dM_`3&^}`3yOUdWxJxPN425Cy;kh_mFpyqp91;(d3`0vE-l021D@%XZ+}lxz5lTile9-$Wi2YhT;>{SaK};JHb$#%usxZx`%v;e22Q9yr1)QhoLyL8$xkD>P_-Z&Y5Bric7m86#G!sT>3B+H)AMvr)DL)lb>_$)x17uDE{cO4n8szTMWe?7>YkrUy(nPuP_v!r`{#s<ytw<P<)V@L{8%RILJ_Zgdv|jP<N3{att+^97A41{h7Rmyqao|SCf}A6fdT3AS<0qR{A4(G5H6E;_s<CS?NHs(r)DM$-^0n2RWmQGkQ9s2}5yv>LBtUwpZ*+ZA9%xZbWWN9Y`L?n%XiHf6Y)lfEq<s8c!ZTo<u!Co<#nYq4*p%nS74?l6r~!lAPTQdWWn+aUQDLGkF+_i!l@jQuC1m$sMSr$sNcYsXpY6<gV0a<gVnN48>g-iUX+b<N)#;4XXCo8;0V4(fdeNq1c0JkyR)zPW?bup}3G!b2}riGu~^^LgYeh^PZtNjry6a^a?qRoXSv~!cd$@Jx^A8keo<9N<BhWYLbtV_fliXd&wKAYseePD;SE`Qdg7Ll9y1Il4nw<QkRmIE+#Aefvog<@>KF<hT_rG;bf(Q$fL=j)Sl!}@-S)_@-T86XEdi)r*<J%C)c4iA=e>$Q`?i%_rEtoaUq7{G7QC)sg1~$$+f6$$+gIV)UU~b<W|%H<W}TP)Jfz{<i6Bj$x6?W`;tdeUy?_Xw@}qtu!XM`-_j6@bMdUmL(WC6Ni9aMN$y4sBzGeRQ#+7@$pfez$pgrJs9ni@$RX68<PdTMwF^0d9O{hz&iKX|Evcd8P_}7F4IsB9*QKiSr7mA9u0d7jOAUtNI#dsG9dZ+f;`Y?y<o4ti)I#JI<SNv><h(qasxTCnbjFv?sP7C<YDscQw((>r&csmsrv_DL*`Ex>PpE0+C*;@ERI<_(@@w){hT=mE#lKM#$x4rse<Sas?j<YTNZv=@%uu|Fx`Molyo|b*yo|h#x`dp5uB~Gzp3P7^mO7QJbTWA?c|3JAS!pPFJUN0oj2uB8LTy7HLhh&ibC&gEDDJ^f+`t(no$-Y;%26AT8?a3|hT=-p>g0mdqSWf-qGTJj4q2%;S!p4%jhxpRS*f|Gg~++c|Du*5E3Hg!-^wjh!OZ{D|Kk47kM5@a>-s;u|M%a___dkqZ{Bm}`uj_?_O0Aiz0Nn!nPhVQQ19@y{{r4VME('

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
