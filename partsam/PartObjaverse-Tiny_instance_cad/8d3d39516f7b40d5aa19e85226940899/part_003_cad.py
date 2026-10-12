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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_003.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_003.stl', 'source_sha256': 'ba0d20727c5d0c20bf80d426ed1a466df81023157e8dc375262a384cf7c1d672', 'input_faces': 1158, 'input_vertices': 636, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-38.672210693359375, -34.761375427246094, -20.57037925720215], [32.37151336669922, 28.372997283935547, 37.970863342285156]]}
GEOMETRY_BASE85 = 'c$}r3b$ArlAMPhXgA*W-0AcYYkU)?mKnN4uU5jlX32woy4DLl+;D;^l#kI&3C|2B^h2l<&OMCZx-*;iN<d6H@OP}xae)i4DnKR!bGjnG1w0^B*$+K$smsiUhv@E?PQqxqV)3R#);u89FY9H4-q<hbS9$F^x)jy}ssN1AY{T3ctKW%W~*tp*96AG8L6poCKC|uN1IKD?hpM;q1ZF?ld#wovQOxNCV4!?KDn4WQt&jDd2!-`r;1{SppwfsN+OQYJ5wrM3(>4*j4N{weV{B(z!2~FU~UKC%;S;IF;e}1+^<!ue-qn?SrQeI!(NPK&>J1BqkoRrtR;Tzd+qx_8tIb40S*#`JEI^<No?REq4t%cX4p6>6mOZ^+`i?6ryjF9pVd;2Eor@t@0#TUNi)_c^GwyV@{H|n81qr6bQXCpsX-_kfW{Lv|qhlh31o*&<$oooM=_E>k+!ErlgL-};8{9Juw@fjSqN&Q^X9!ui#+T#t92lGWO<RSVL%D2ye`uEjD{-X+`e*ZguuD&_j2mX^&a$c6g^wSrDf2lv}e_I{(L}bNr(@sD>L#m-YmCM2}_y+y;OI6g9r40N`)*MOtpVmr#Y;jdk|CxW${xJ{be2o*8k%zy+Q9kUIv{Rd33Hhv9C((J?lf&2iYA0&H(>F(yMm=W7?5@7O!Y3TJL_Z(N!%`jPU$jotFZQ(X^?j`p<=?m#1wW)kqI_B_!8guzLizP|{ak&0NykLvM9Weh<^SlBXncP4Pc%)Ge{)bI#@p}3QT}4C+*01JEb>r17=E7ea$dGa5jd|0{or%H=sUwverzAq|Ku6+GcFACbaF8AQ){WT-}bUJ+TXe;#&fB&k_X)^h5GAGLj5^TNqI{EeBFN{>d!R><LX@r_#4~7clLW*_!iGusHa6`UsvC_UmeHwX(HwAzZ8dG-^%&e%g5EXjjoFFD{{$sY0H98e*I4<Kckk^W4#`bxc!T~vb*}m#X+d&=uXMAZEzus!z%sZzuulrj_X$d=k;+t&TCvd$+Ph|AIi^Jhx)k=7_ai6{)Hy|)S2Xbt=3%Vm#%w||11mqCC{gFpq*ED;<%4aW|j7gOrLmND)Ly$8-IJDo&(9@XZ%sh+XGXho}Dkk<mcy2tk2U@q5b2Z!+&`|`pa_K6Z55FIvls#Jjt6al?VFkju-r<50U@n|5lXWpWg(>Z7@gLW6SnQeB)Yu<R{=5+Oy?7{MQvx&#K%~UfcZ!^^}Z49$K`MJlm$f65lyaw5l7>FLR!we6JbsOKz6(mdlUCw-26(dVcfGBYE!sKz#G}!->X&R_(s{)?H(`F2zVY&0p`K{+K^dzCaeNhtKS&f2SS(#v>T#C9a6CkGaA8^uTewF5rA;UPAqWsic1W&0(}>YB99`LsluT#U4cc3j$I9!B!}5>_B<WYwckU|3v<?+33gCH?WS?+m80^nI*mvvJdlj>{j@N5>U^@=E&RIjpExbZAU%PS20h6H=zAhx4<92NBZ45Z!OA4tU)^;PnYuMxz%X@rIo1P`zqGkLCa9jv_mMrW@`>tUwix#^&c4`=Vckb807<=!uQN6?KIENgzs4%dA>DK@@A_v4SC2E4*zjl$(uE7ILe=#0YCD-l-HLHMf<N$hM#6-7CG+hZpcsPN9ZsAu~OcivNOuByql;Wt@~TzxX$ZNmEO{R>(S;Iw_LZiVVRNVU+bcLY&ZCOPb1IwYNMUb>qyEi$aBl8@b`>MbUo54W<uV+oGL9kBog;UnKPpN@sp)p^K9Rn68_46P+p%e^T_%(Ir{7VbNCM$qrV=#j+XY{C>iFOXZ__X@%1Oc@T<jRe2%{^zBypL_<E%{i?q{vS$w1E2=t@BzvNk;ZKD47kHt4%&qetjyHS4G9hCpD##`ExaVh-%wI%=hopw^*ythz%dx6U6$5y^lzm|O>+H=Q7e+2q*^jOqm&VkSQWzRGK<+t60|LG^mk7Yw&lrMM<{T^FO@}vLJ73FPT;CEPo@m#7C{0}Eei68W*^oyCSqxjaN$4j~Pi#fI>%E!Nje|0O?!@@0aUVUD||9DKskKQ&K?eW*8zs%?3BoCI8<x&36aP)gvXUT)PIXCM6cZv9V-MV>|Z%pt-Kh~Oq@>{QFR=(}m*SfTGx;Ogeuc=aAAN^8%?N%!E%hCE$-n!~f@tyr^PO2g0HRCYKFX@l+uP;b>^T8qU&CfSW%J0o-gYm!p50syG9X{7p&3mi(dXaR<Lva)1aN{PF_eufZuLG_ZaVyXsjvxK_aLJExehH4-@G8dbW-G?Ytm&xdLQAQ~^wOpMW{N4OCvOAvW52~R4(;hC!T%hHadLh!)~mJS;ioBp@vv<-+VkIF_#C&|vc)*Bh*<cS4oUrbqXPM)o&DP4d=KozajmB_Nj)n|q5bbtOMbLuw<K@+fRf_d;#0tnevfgrEd=#D$4Qr-QosHt5a)X}l<Px?)Ne-T!Ep<PNj>JQXw1jkxlsSPVAS8J9?q-ms|r%S^bXWNEsxZ1zw%sst2S23>)v}Y9v(gvU(34&$6fHJ9M{<XKzt+DVAMaa0p|OZ6XKgIW|tN9evw}^elz^2kL9JjSE&MWyxKER|0N6h{Xqo!@xuhvpWg@l9y(L%*Q*-h+uFaz`R?D2{QuJ*{`0#ShXY$kJGJVK#kW-1FYVDo#s$c6-_%0=FS?@spmkVhN>)RD-e-@J`VSnF@?ZTEaVVd)F|KPn3ZS0HXHkFf3V*48Tz=&9&uN%PT>mY7d{91JL8)KARyvRTyn8aV^ICVzi!W*NOM4!FKs!pe!MO5llu`NCxY79id=D`WJvK`oOz)xa*Ih<EZ|g}O^vCVQw|{CHDt_K5Stso~W5l=2Z7jZXf56hBt@uWlMmT=ozlzH5S8fPD+OM3Hk6t3a_B2d<YtSgvvw9HbZ%_&R{-wb<ZlTG@+Zi9U^K}DUzg}*``nEnJ>d#aa{x4C|?`CHY`0cwwBfPRpyK{Vy@np6vi}oDt>!Z}R?w<I@lHgS8_qCvNUP<|eXX+A4ZL9B!uP@w$^=0_^<Yp4S5!^9U$}hbGKPnTRdvDJ9urDb;s$+5az52Jsx12vGdC>2F!Z=@GhyTm(n75g_oZgp|Kf^yn%Fn(jzP(ADj1R41zPA;U@QwGEgOu8*Ul-rz)3TtHfBxAkN&ml`g~gw8O?>N;sfDDT2%l_8`u>^nyZV;1@8Fl6E8|KJxr+AeJA{5OG92shF9(pH@(Zz^WQ~yXvtHPXetG;0`h8-!9M}3}A=>#RUgnW4-E~<{w1}Uvj`$u#`GIyk@AsREb~Z`CxIR;<xct0TPt?D>rHm8Hg975~pSq#_%gdLLpTB#TPt{{v8HaX;hQO~j3hQl+a2$8WDrt`;ps%bCw(A*C|8EB{-}4Tab-+G29sJWXr9E1`jTz;0qrW4SnoGxG-1eN1LE3%#q4@UQTT9?LbtKQ`P`mg>_GR$>7RowcUWi5cgd$jn!~T)>TSm5m|0O5<gM)BA`n{R>T6Bb5*X(7d%KSA4q(OVMPPpFfsVDQup63Pfb$2@Jd5wAc<$?Il>xFSYLHgIoKTCY)eS&_dJNkF}4DoG;)}sD%+0ifUrsMoqUqn5YLDKJrZ8H3T-ofJYzE0~o3H7JwD!w*g3HI^Y$BVD8^u#*ZC{%oVFDuF)I3nfsZ8qG0+FPN#{|?lX>J{$uixooo-LKG2`w!AD`o%OTzb!6Ae$MNr^=@+Ujpud5H-369d9XcsB-aCDP&C@VH9kU)d+!1K@k=sDx$DU-W)i-c_H>x&^}D#Plt_p5#J5W>GYQ{p|FE>2@44IJ+YjH6_8A|4MnAgwrhlJOQs0pq@cWOI`LE^vDZQDLA2UqWNz3jl;#=1?FCxB??#;d=d_B%z);)dmMe%JPi^}??Ev_i*mAh};KP&5%zV5vEmYh$EiJ!M#=A?XW^*;q%ef^P+b=JB5eBO!r*X+c4d-r!)H!Q<v;lAWUSTQ-zioRGcL#Dvbm_vMH^()-xoU-D$WwK!%u(p=@t`#Vc`tL@-pVmO;yD=sU@>U`<#`n;!s6Sa6^zUR1{-$VLm!~f-BcCHKqaN>mG9PU%e}X@5l$1A&tXS{8#=y_g7xg@Piu;`481bF+-3YcwznjZ)p#0ItQr^tqlTVd5H+ze3Zn=SaYTB_r*Zv~UtJVy|aes9@Io8Ql*#9z(QdrN=&Xjqi=h%bi+mNET?t9#nd8AFTiEjzEW8FAkO6HO6(G>CZqRmmyhKblm4Qh*e#`Y;BzQqIkV;{KB8`}*&_y4s&`Fwu&r1<8^r?}tnDhmJRZzz8<HJ<wxa3AMGLSgai4Us%(Lr&v);B@oCu6eLDYa_ndrWX49?r`*D@}}_n6ot?GeA5TdE!Ng{tfw_ol@~wDZ9HGKorV1Nj+5VW_w^q<%E`}D-9SB4_hFsdoI}pT-Phk;DI@Lwd|7<wJhdK=$!8|v8zcV>m-;%N$NlTC6$3@>SLD3(XXkJ|JKHl@>TP(;&rHHMOAVKGM!$Iy^^7hc_e0w9I9WH`eZAoz++RI7hU;RoJb}ok59Zfd_{Px}Qcl}Y>%_h!e4~dq)`{as@SKp$3+vZS&vZ%p<LBXi<mh4eejUYkt`GJ)HBf(K=^)X3LnRNEPdfVLRTlWy4`F^SKY`~Zd+H)mUvS@i;%_;O=kp!UQ9i|4TnBR`;Ql6IiImr#*wJreyQBPx>F{~o(Oxz~`GJG*Jg}`2_G9-o#r;j`uHqZ9!FZ4JJ__Z7o=H8%sH3=VpB9LA&dHAJ%8s<SUY{y}@~=~h@7yo4#-7IYvhGgtjWTm_UKNkx`Jv!KlrIp9{h#UaD8DqfT!*yhMKDi8W8vq`3cr6m-bd7Fj(W1r%qxDk1-NhgSP#$bM-#+1J{6R8UYl7K<$VuIJx1Vl$(!9X9RAc5sGs|jw($?K-VJ`8Tk>kwmiF6b-GTq~p!i123+xldoW#1ec#O;wqtjdT`^|$`r<%vXAJ!G)^N#_j=krM9|5+sF%aUFw|F|alt4bO?r}U|e`il>g>y5Ey4%Y2_k?^bj0DnL(?5j*DD8A+2)7U47StRSC)7M^^c<vwB1^0asxy844UxfXhlljrUe=>+#eXpUOKX2kXHt7R?@4*uEZ@^UKzsxK6Uq+#SGqlBZHsOl+W>`9@$Kq28&zE10qWp#0^4xB0n<ja-U)_)E*4h&AZ{@@O)!m`+cdbP`BMQp8Xfzsx`cI9<c$i!k?a>lY|NVIQ`!(dVM|b!g9u&aw|HHo7ubohj^*sFB(J~&il}&NnH1Du4GJ7koOZ4?G_u<bPAfK&G>cY=*M11>{0Q5(6wD^|T&&We;PPq=+hDD-1lkps5O+Fp@saFo|*%MMwe$Myl_I+t_oUUQ$$I->5yrr!d%Ac%`^?E@S<TKI}^`{DjpZm7t)3))WoQJK}Rmr1eM<-qKv*ta<OIRg5SFfxl{r;Wbt5=lh;y2>k>$S&o#kwiDUb*>tpKNmd(q_IC-@3f1+}GL8h2Xm9=4+|$l@%TR1lM)0|Mqzea2{^H+5MedkMw@`;a~hvQhhf1car-ScVGY1LDp|;=R5HK^OpN#?d*g1`;zbtzgD;(jJ3l*)>@9IX>(I1<r~IZTqk30VZ3BM0iV|kYpzqs=if6izm^Zief@#W@P}N&y0QE$o_9)Yz<uYXL-1?vm+@)TU5ev=@|JyE?a3Z|rmsKu#C~&FKN$!1PjlfXzl-siE)Uj`0n_2P%7*eiqj7)tW*q8U&<D>eE3j_bVn?IAw;!IL`Mz7<*9Yf&G7$SJ-jlG-zH5c?;NJ}A`^*>Xd+jo)XWcybQGxQ@qqRzf@vx)?o&y?S-%<aRTzt#1!imn;>04i;{YJyin71oG<9_t&8_c^Zsj#kP{~*5gVGZnKZ671!Rv+^Q_s9PfLH$8(@%vvc!*5s+_uYpFVm_xmhk4v99`y`<EA?1cpGNsQ6UDdf?1}RobP9gs$9Ue|8j5_@IEmvd?tuNR8>Nf7`sPo|@%*~<U26ILLkH3Ry4|tAd;6b~uD%xB9QzelF3Wha<lTaHKFNsZk5rp5|GTY1{ns~RfA{`U$-jO4eB7sR>w|jcSI55V`#EU;{k}Ngwi7TPLr0+eZyBV1t*a-FH?%+e*=uoL`4eQE+k<+b{g=Y=zM{phP*-2SoEQCAyBXH6GM&)QTr2UM6cvH|r0xj6=)V|0K@Uo}`r58DiN=r7KNjs@G#c$3bS0CN_i2aY?$<H?8xBPK{cAv1-$Osvt}gv$-%}O!U!H^Kyymz*Sz1>{{gsR0xy@%Fo&&Cy#rYl^gm&gVfa`AcaJ1jQ8}>^$FN_>vXiv;Gw12=w<hfZW%Ey<$INbUl*0;AIXph~%^Xr7)FmHb@it^<Xu<vqogyi3>$o;C#h0*>;7jVBbJP+zQ)feS6SC{)i%S&9Z%tL2!-HA^r*9Ci<9LP`QT-XPC5|dWyNtX%b^^s`*n0%=BJ;sH7TUzXYuey(Yl<_Zde=)+qaToi`by&}LO?>^Y5%3@XCD(I3VmGc!;cdltu47K$n79<@)nOg-@3R%<M^?eS?zjc(#@0<J|1kjL?OrtZ$<~N(8x@BA^;SOUmov+8-Ul(>^kD~Z-Oacd?VOew`)Uh|$UM^P&c|`zH^%$7K{JpSuPLZ!>}QO_I#)AG`RWr;zDZ&18^!m>{lx7)sDIu^)X({@x9Ng?hZ#e#zV)1h^?Y7D$_J;%I+JrB*5$}p_?_lsoOtHLK7(&-@hvTvpglde$bPt4EDGiGWI_J9|7ljqgS=(NdqU%02edmT3)(X!kMxse)f+sQ{Fn;)yf#$wX%A_M{jIZqL2C}ec({h=d$Y?)<S&<}oUe1;)>a=C-?C-B_|EmpoWBIujrr5Cf6w`)Uta)!?s4p^@w%Y5_!-B&QB(TGR%IRL%lql5pVt?A?jV%EI1%M}A84yM596fK2pqpp48~8zHJJa?hN67JCal}MPMPa^q5O|Munx3tgm$Km!Mb~874oxd9oDNAZBS3_4%Fkk9`*J|`7#+Wp5u<9pF%Rh-~18p#~PhL9s|B$o`vtkI>U9+9Pt$Efd%hXoa0CT{Q>SrJ~YPuH0Qe(@hANL<1h}nJ{yx(VBfP|ckB~$JvXDr;JEf);yc$>^L%Ug<8DT|=D~a%g?a);V85L6%cv59>qc-ntUqNdW4wJ#hxTMmhx-kVL%mFD@of{DW51m9+URlv&kfTn;JmmF7-P@CA0CYU^|^}j$&cVYRgtWCPkyUB*3Gutas7!rj(HbUzl5uA=C6ct=$!BKH{t$*_hZ_=PsmT?29%#3h;ev&KHB5A3hjAP8P_9!-cQV0h<c7U!S#sa&}`SXsB1qu$E|s*3EF8M!utY_6XRSl)bltu>T!<$_*5wGmk0Uec-Eq@FJRp=2kYK|0JJCDIq~hq@gCTj2V?qC>?2&7fP9Y00>9uQTu(AA#B*GVn>g;`S&8a#=GoXgQG8pi4VW)ar-i!u#zcDs*L>=}gHitQZj6&&xNp;@w!uEj$Lkdm<@s(|@y(!{6%yq+=Ns8q(j#`^I+U_L^1JJA@y!o=#kWK?#s1sK{djM~=PCXA*=Sw)LrwfVW3+s4%+@dz{o>|p1BS`-m)3O`-Vdi~ChyU#x7VTlZoc{B;0j9h#+z{5*FmzMWgRdS$9MCM7U|^q%ZOZ!;~sjBeYD2!<@wUxH;)~Y{Xnz8V)4H|2UW_4_XTdg9&%Ck@yr|x;Gf6)2`zaedGGn1|8Fzw^QHeE{N(4c{}?{YGfBVOn*h;Nv(e7(_2l```8=f^DDNwIsuha$pwq^R;%_e_zW(bFyw7`y>w>#)KU7`%%UBpHzIE0l+3(XL0x)jfeB0we(qG2dK=CaZAIf_Kd-?pBUv9o$!79(oTF<;VF83AnR}pyrb@Mf!$9Vp2?km1=xD}pn=dHy4kehED+>ZXyGy5jaXP~^NcK7vze@p(2Qt8Dv`!<vPV(nudElEFeMqncU^_6mo@~@5SCGU;z+(Vv!tcB+tH{Y6Za<prC>!E)npO#-&lrWR<&1JiE*Yf)P3V05Go~*c;gm3<IHY!nh=RR%04*_NpzE-kUIoI-9hU3U*+O8He313^1EIiTqavW-DPNp%F@Xa=bOC&1KylIxX|5ixCH?AKIOjLeI+sMRuzHUf<+TX!EukyK~_{sh7-qNifzw_CTUw!v}%;b;nU%QPTci%aFv|Rb%yN^#d-#I?DQbG7T4EOQx=6@ak&BCw`?KZ#M{jc+@M-;wK?KXeiedqku##Y5~-PZ><-?=_$Giu_v!(Js`XL>9MNSrsWWA46l9i#u<IyQJQ%Db(f-}ziWjY%uvyRFaezH@yxmTtgt-PeCN-?{#4yLX81etmKGo!1xbyea;7*Dp8UdHpi(9l~+lu8;1%^ZIB!IRd}Z4ctHSI&1uV2jkIgpUs&47xLu3U+3mK_v`cp_d;Fs=G+f-_nrHJ`szpU-S->aeCK|nw(S{w_x(&a-?^Wu{egM*-F~T?@7ymn&%Hyv?)$NBzH>j;y!8or>o^_v%Vj$2uKsuX!0tZxfsHT6FwWfGiy7K+`0nr5+<oW!wUj53U-$QSZoc#Vo$h@$%r$Rc-y6F5&i978|3&e?doStcJKsxc!Pmt9?tQ46|Mh)nIlK7o?_1q{=lfQ(@?RKd|GmIGtnXFc)&K52ubc0D&#T|ODE<H4_ZDtn692pJKe+i{zyI*yium7szrxLTe!oI{d0l+>?{B#K&hKw%pY3H`^Y-=oA?`lEA7XM`yMO=0-FJTf#LV;%>uJB)vVWl;>=NPXfA_r?H{bca7n9eY@4i>#<~zSvqy2tE`px}&YvzHQ;=6zU?K_{}e=`r=65sv%b>I2?ew}&zw)o$Df6vW#et*wA`xn~j{{29A-}(K(%lE{0|6byEzVmyD*Y4vvqt`Rs57jD!b@Ao{lz00+q`U9@KBRH`A?o?9G`?@?{U`2Y-F)ZwEsaWh<$7X9uEXEAWYY4w`g$)PU)O#ys_sMiKYHW)VO!r7aP{>Cy|TOZi&4WAUwc3IzN|+a|4!d%`&7n*w$wAg)z>fXlX<EwT8e(I{X6Q(Ut8|~jPdINU45fQJkD#Sm-y!7Vz^K7n`N)yY=8Yke_i}X`O{O6glU=zFD<JUALH_;#mZFwoSO8X7I!N3fAy!up`oQC{{Q~AIL#~%M~WOVn4x$)L-91~YO>N*<Z0xY48>EabID4Fla&r7D>cYU|3_9jpFEX3nW1<L^=GouL1d+U$c|)dT^uov+LOG@5%U}|i8_uvj%6lM`;nFYNS;KV&QLs?I)Xfc$DhqmJcFUQKeZ28X;pH6ax6n}U8+u2TAo~&T#KQ&HZ_W@v;w&{xem1wxemDjLvc51J#szfu^V+Dc>r|^bs%{lb2^1OkG#nd%N?<SI)yxiWi~JrZ>BCI@1U-vE+a2v->jrgCr@V|tYj!&!%)1KI)gleeXy9JcqBt{4{9tqmVMBJp|~?caR+KGaxL~j2ZrK~48@(Ob;zB_-Kh=84VdfhE`6YQ2z4TL0C@oOJCVAayqx_pk)hbeP`sX@cppRY9}LBNsT;@}*f)C_ihpM)-tW?viVskKqwXN@V4wX)T|-{OzWI%zcq2pc9O_8&NcPPfhT>ri#eJ!r$(`9ZeHn^-F%&0IJCZxHpAr~~dsDlUoqf}rq4+22MDj%D{U_>r@=xRy48=RCyU53=2dTTryIAfZbsu>j`|lt_@fn8VBh<a*z3jgu)cxcm<f9D5CtUhf@nNb-JwQId{xhi?$s5^ECPVSB48^}thmnV|pMGH|p1@E%irS0Zi~Tf;p?EYy@mOkaa&Pv*Scc+7)D`3v%=;pS;%zQ{vyGwnxFar8FHw(?kFh^4QO}UCQ_oV*kk7CW&N39AryeCAW!}#-6klK{KIhU;iVsouP!E$2vp@Dwe<lCQyzgNsUdvFtggSvdfq7rTP`rSlcp-H(c{KCBkh+Mxh&f%zP`s6ToV=BMlA-vDOCMaJULreleTAX;CiN`&Ec1Aiq4*Z{0{H@ScZ+(Je2aXMdXDVOyW&5oyQzoBhnU~p)V1Wb%;Ro`;_VE@Tc``j3z)Ah)UD(#<Wtm><de+BDTd-})SKjM<Qvpm<Xb$48w|y#UC#3~bvJo8+kKk4g}jBwK25zw-s-r2zU+u))YD|8N6E{`a~X;kQBRSTULr3duXn_sj`-CP$EoYd>sjVFL-BQn;$$8O#a|eTKTuDRPq7^z7>eIA6n~_iCZFbceq<=tJP?XgdLR`4#ZY{fx|Mu}x`n!xyp{Rd!ce?|I+whHJde7FJdeDDx}LnAxl??D{igcQ?ud1cxb28&M^tk}8HVE0)Q05J<dW1la!GPAhT`JXuH@q6Qq*{IDRLOK5jl)pmRg-$mR!*hgB|D7*%1S&9mxa91E?Ly1IU9IiaR-?3AG`$1Gyo&5w#<^5xFU~Gr1|bB|~vn>R@tL@=%82i44VKsRPMl$)l+Q$fL=lsDsF($YUHafjWdbh&+hrIfS9Oi%TxLFckmbh{{x*+Jvl=qo@tZQRE8LM&t_QXlhe(G`R}3CAkW@CPQ&+YFBb=a(C)ba(D7DhT^HziDVn~f7FTO|B-*8jwSy>o=zQ2o=%=d9Yvl-{+T+4{4;sBOFzwKC|<}=JcXh7N9qvr5cboL48`53KajhTTe<XQD~96g48>&`ic3><a%pmLY81IRIfz<;97HZcjV2c%m!MW5mmr5xYm&pr<s4C-T9;arth6<`F1anWJGm{nCv_OPCwVwS@l5JevU9A=WGG(ci1XBwR2%su`4IJg<U{0*)L+OO$?K@o$?M2#snf`7$s4FYlQ)oeQ)iQRlTT0=l24G&F%++)P9d)(&tNDvs6UdGb|V|)9@JLk9^^LE>f|=$It;~;)UxD4R9|XYvM)I!wKO>+IVH6?IVD-625H~^DNaT$LQY0bMJ+*2Mb1nOBWEW2Q_GS4$%VCV<G3(GaVSG^C5Gbq)VgG)ZOQe?G1Q*q7;*x2I5~kllA(AGbtYNqD)Joi8tvOyU&By*(GmYqKU2?>Ka<~6Pm<r0?@<qt?~(6NH<Is=Z&BBgZ;@|O*OG6NZ&NprZ<Fs*ca!gu-%(GH-;qC2&yoM7UZ9>MD_u#xKwiyIJc~MmJc~SnYLG{edr^Ckm9`=GB3r3-$X0SahT@9UNV0P-Rb(g*VJObaQ0zzbCHs-HP&1OVkke38lGBirQ#EpOvL`he*^}%+O{IOktrku}%}h=~PEYkGrzdBl7A9vS=ca~|bCU}?B9K~&8cJ4LiCl_YjiI<PwLV#C47oA6JvD*cp4^8zlH7+po}qXFbq-nS8u9}2X6i-qX7W|-+g!cMQ0(b}P+ZUhp*TPFGg*b=T-5hu6^b)b?~zp~PEWl<R-rg8^%hx$VlV1VvI@niskg~06sMuyC96=Jj{1(QLU9J_C$b8~**(6^ZN(}S=W}QQ52y!K`5x2@WEG09&|6KuLf%B3Mczc7&rm#$I)bdU7kM1HH`Pk+O>Rf6M{Y-Mz))P3T9K?Ygj|(elA$<&nwK0v&cjfglj=v#N%o;;A^VWMscFdG<P6m0<P7ArR8MkRvKQ5Z>_tvZO+ijgPDf2oPDjo}%|^~d&PvTq&PvWsElAEz&ZT`@J904;TO5&}8cYo&2a_YHrN~OFkt4{p7>b)y8<Ul`CpRa@QTveN$o;6}$^FQa8H$%u7m$^1CNCu)p<X2)A>W{?HRT3BD^9^sT$oyrT$o&wp|}b)Ke-AylA4PgNsgdqBu9`-P}7r3kVB|x$sy#TR4;N-av(J|IglJcO+yYK7onyj7a<2zGmwMHp$x_0)a>N!TzA45ipzO?Tbs%;6jydc4Qe530dgU7a;gVesamI!^Rwb>8gvu+8u>7FKKU?tF+=er>Nv8}-sDN-zSMT)zT{YH19B|68AEXmYE`n*lH?lXaE9Wd)Bti(az1Jvaz1hnYEH6JAF@(!veFD>rD@4Zy~s*ala;0;E6qe!nw6|HJ6UNivQi6KX?}7Jash_oV$@)AF>)Dd1X*b<av5@MhT;~~=47RD<QC+3YCm#3xj%I>xj*?QhT`SarDUZ?$jiycs5i*R$abn)Q|$b#I2A*25VbHlh+LmqliZaWPpwIgCpV&2AvYpdr$&;ilPgjq$Q8+DsU<wV?O`eoqlS2V+w)Xhidxj;+a9Un;?zKoZ+ohWi%|nSzU{#(E=euo@ok@0acOF>$G3f5#bv0W9^dwX6-QIU$<gF$)N<r%<c8GB<c8!pmvzdyHyp>@$I-9PsKI_yTF9jz3$dS-CMPRZ>y&d0T;sS<dRY55P7ZS%DP8O`t`@tDy~P}-N+*$(_H`M<eL1d`#=4C2Sk42b&0OY1Gncv3jPp!s4YJa3mpK^jGB?9HkChg6nb$=*@0I2wE6qX9;J8W3<cO@)jO483EROJ@rl)2krzijGfyl@Qw2Z9F`M{>wgQ5684`>Fm3dLVM5Q@_|A{*74nt_~w?ek_RE<nvfE<n!jat`?!iVHa+fSQBqL(V}?OHEHsOaANuRp<Pfq4+67@pGy=|L6Ry_$AeYtU~cC4}{_uRF#((48_l=U&znMPZ)|nQB}S^@w4JIE;&uZP@LTng{cLp*~kUS`KaDxZ{{~2LvaaeesT$NDQY2dDRP)gAA~U!M>wJ^HHaEO4kG(ebCCVWUevT?FY-qZsOqPW48@PBPsxwTtr&{iP@j|Akge30WGlHH^%c1txjjR14D|&$hTN9=jNF#on)-y?n%t71_!0FJ`4Ra8RrU7=epZ~CV<0;@HQCo?O!zVs2Rfn*HJn<Q98NAxEl4g+E=kQt&d2dllA*XFwG_D`xiU43T$x;z8bPi~uI@61sxuVVbVO}xB(*F#l3bJ;L@r9sMfD@+BB!EykyDZ1dqCAVd(Tk(kouVXko*I+75N9U4@0ppwGG*qoRexL=Op`6+mZdr7HWI4g`Ah6I1e?3oQIs7+LoM~>_=@)_9N$@wj}2uXJaUCL48DSL4H8}Kz=}eM^)qX9X~5h$uaCpPD##54J79z7jYTWMHq_9IieP|2DJ>i2DutFoLr4ug<6_ig<OeRl3bGGyAnfjLuzGmLvmwkRdQo;Q)+c`Q*v`^O>%Sc4=!`y2ZrKSj%Z7*ORY_=OOB#OlB38W)S~1NvOhH!*`J((nu?r){MG}i=E+-z;``Kx<oo32)E~&r$yupB<gDb!8ba|?sxMiE;^)+yWEF~EQvJy)6#q@NkX0ytP0dSIq4<r4Q2Y-y4_SrcSJd2O6^dU_{m3d5KcnU#t5E!envJYN@gohPI17K?f}DlijQW7wjC_y!j(m^&hN|Y<8-7-toO3WIIXO8uwFo&kIhb0G9850nGAGM36xVS?8){2xEpkh83u+B=3vx4RHF7g@6KWN56LKSJC2}Rs&qfTz?Wm2(?Z~mzrsP<1JheGFp4^f81Gyu)Gqn}DGr6nF9PY|c+`|#Qs4>*G<QQ@TYF%;zax^uH98E4x4IvjNTd4kI3pp7z1vwe{wFgwq^VbZ;cd7Tucganu&B;y4-qfsQZ}LM8s^<JdhT`oE#XG4_$vervQJ<54Bk!fYB=04g)W69lc|Y|vc|Z9e^$qzT`45KT1Jr-W2gtuuUy*+&@1wpT?<4P_J|piT@1i~-?;`J@J|gcRZ(}HaKvnC-1AbPVnQKTha%OT9>OFE3@?X?9<iE)OP}O?z4?ipR^n~Undy?}|gUNZw#i-@U#mG9f4p}GH_x!e|)MqHRI-)1FJGBkDJGl$BCAkZ^6SW1o6S)Jm8My;Fj@pDAM{ZATL{{34+@9Q<8cQBbO`yh-mBy0?Q~Ofm$x1tt2UGh{JCc=lCJ&|#pmruJ?Mfa@?N9AWR@#F+m^z5sgX~<(2C<CNfz)2)!PI^X#oegA$lb`TsWIf%<a*Qw<a*=^)M#=AawxSpIh352Y9Z$(XQn12XD0vc0afeZ-weffsCUVC$c?E@$&JaGsNUpE<og;_t%Hi|*Yfbpn(W&j!6p7*Y<~Nv{?<!N^grBm|INgIKIi(IZ5(xd{bRcNwNl8teNV@K>g8mN+S%9s4`O(5#Q'

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
