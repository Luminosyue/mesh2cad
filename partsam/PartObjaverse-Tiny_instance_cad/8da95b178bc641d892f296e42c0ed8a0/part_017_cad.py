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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_017.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_017.stl', 'source_sha256': '1636dea0dd0ce22173d621a5ebeeeb4c024b8ce2a39ce9816e2dc1c121075bb4', 'input_faces': 992, 'input_vertices': 578, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44927018880844116, -0.12439817190170288, -0.4013776183128357], [0.37495332956314087, 0.432731032371521, 0.40060874819755554]]}
GEOMETRY_BASE85 = 'c$}r32apt1)V6z<AQ^-urvb@PSaNJ77(hTkMFAP2AV?Mrpe;&N5Ks{TVI+%$B?p0Ra!v~p1YyW3iXsRGz;Et7&mDSu_pkcv`=~ngKJ#$4r>E!ky*)ik(W+URv~iaFDQ5L~dqm5G8kVIhixp=L={|69uddw(RqEUS%@`|(_UezxPg*?pOsf}TtRdFhrMq<>)OBF#I)T#ldekaiAyB$Uzk!1XcJAA$-@tC&m2cX)&!FxRKd5Kt{@o*w%T%vft3n{YY=yw^!2j}3rpPY1C)_iMYG0-;`&Q>Wzb7SneBcZ5&f&*huXm@?KV#oKueXiw|JuBU9v}W3KdY?k^%mZ_d@;%E-6rK%r?x-t<Kq4OPP;h$e73LOc^OZ?)o!-<3a_oyk4LrF`)|B!eA|0-b=ICKzEH6Q@Ajj<DBf)U%p~y(GOtySo&5LoaWmff8h`boJ`UF9+o$z${&KK>>~vjvAkpLPnc}SzQx51HnfrUa{q0@#adX!XK9=b5&KB{3TRo3?`<)VJR;AW&7ZdOAx2CVq$IaT{+x}PL!#Abhp7z@*?SI?8Oh10VneI2<x-CBNa|7v5zd?JuT;G-6{W0DuE#B-;)Gs(b+q*x;J4^6p{}<mrsegWcXp8h0JDlk8&I0_c+=un?K7RRx-rn6#^1fHPsmFuyj`8<Dm2uSkd+ptAG4ekCo_R~6$6GtZTitHS`&s=B@smH_q%+I=2NOL$I0>J%#s;sqjNdx-E3Xet#D7}nEARGg;}@mb;Ps)8#k)@LgL?mi6|@gCew-yczf1IZGk(HXH+<*qH{-|OA7K3W`_1@q{o7~!gy^>(D<k_K$|2`b_PM&>cxR4yYslx)KW*mmRL3(u#dtQ}H{Og-G2ZSr&^{PjQpU;T>Wg(>zUtZswoVb>y4Xg&z2ilsf8W-v+W%8&vDb%;e{}CR`h9sgzxX_9wrT%R5xpI!cV6*F&gy=rSm7gHA5Ic)w}1GE{`;wUj;D5B81FwXqW!+}I@<3$uZ<5@sUiCrn{BbTKV*E;GX1*jqdCM68zTPo+j<-s9~h4Bxa(WpUnsr!V&&!dSRd8Y`*-%9e*Xg%L&<&9JL2=_+OGF+W1}5<e_CA<e=YY8?ejdI%!l#TxN`FMInPLcx>4ej3QIpejCY!(*Xd?hA%513o!a02bYG&^hw#0I@6-Jy7HS`wTXmP-eydNU-}rgr?QL)CetUgL`{4dBwRcK)*Zom{K)gHc8QK1bp|bz!JMYzx)0Nia#Q5Mt;_Ze7^*C`ezApPYX1w;!#W?B52gZrF3TKpYwP}Ft=b)A1yRX;tr}5#z;+=hq_55k|ZY}5QSI_Br#z}lj=39Jlrg-=7zPjJN{+Mk4{gJYsr7dzO(c{A(;D@F^r27xmm;HS4i1>^{r5_)BNxU<x(;+#2H}tr658Rjey>)(lJdL*xinoeda{Rkolk=cTY5n@GEdAv8<E^UV-ILGherL;Y+5Tcn&Xb~-wkLYLy+ph{dA}Z~cG;oQ-=Tu^+wpq58E<tIZ)Yta<L--`vYm-XkL&%p+gs*oykq>7+WI_lDrJ`Kq)T@~`zL;qe!Ojbc#ZD2+&_=X`!P}8uLHC8Bzk-RZ^frs<MrXc@D;xL((4`L=bo71-M(#np<}DPK6HoYojz)h-v7!6Wq+oPKB@cGY+96<n*X`oB7K~0?2zYOkSKm{i*FJ=-Zg&m@4DYwxk>u{>jgf=dSSeOy}<j|3+vPM(mx^YlzwbYs43@Tf;{ilmdU)cvAFb~yR%07K83b;y%WaQNh9mb#dLD~^D*!Bij(V4e6WD{;G7I{{W<Dy{r3URM|<lyeZCuSb3QtE-;weD<`(Upv4doty;4usZ@fJo|IDL$9J#Ys$n)=z>jZ0KGr1nZ2f2Q59%-1YKg99(_gfr)f4?(L)+5{BKO0ZK-Kf2I|Mel>zYa$Ged}Pf-+z5urVQ8n9b`NwERp#E@756SzVoTf4{OqjpKvl!_b)s?HPPc8<C_<ls-OSIWBUCG-WezBQU8Z_C3^i|;+>1X>2=0kyGwkU`ttaXB|7cV8?+DSd{Wk(`g`^#dVC;Gypt(mzyA9dmS`V3a$Eexy}IA{aFTd8VY&4G6O!j`JbSn9KRiVG@u4Q-?M9t+zuRz(jJuC{y`}1}Nc4Ey9Ea_hR_OlsI?MAmzNwF+HRd@vj`(2Ho6NsY$>+W<9p!nyDXX8)Y1&Zw@qs1c15Uj3H+oUFzpk_P_JqZ<4&s9w#D{Lpl67!je%Vg0<$7JQK5s7TAU+r;K6tO8tTP*O$o9s_=L-AgXVQ;%#)@}e94qV3TbuOX+clfWdAqcm98bJeOS~I+Mvi~4RnmXveeInBx1=9${UF{Re@2e~*aq6WlRlN}=0=TnCVIR*S-iWtyj;J`t0vnids2I6z+T;Nyo0wIESLV3m9-Bs{+$vXWgX75^N>7FKHnPepKqhyH{TlXpKqOaM~Hv#jLh@b2g~#0ZR1BhzDZ~A-r{GMmwC8Bv(1Sf@8F$cg*NNI&vjFOKC|m?{9Zq{56Jbu-}mpiSpVFLliFKX^PJXx{)Q!qsrfz~mgt<gQ?_Hb7SFn1wcae=Tu1%8Eh(8d*HP8i$#@yJNIpmYusqpzoWcdQ5097g%dXp2){PgB%Y5+fud=>0Dlh8}-nlE@S(8hzJI<=lWqkQRU*J=GzA*j%&ljfOH?LYZPwv(GnU?Eqr>?B8_+WbchRR3feQdKg*?4=Xw_NX?&$L&@X)pQwxMsb4&d1wdi+2hy(c{7?-a%jQ1X#b^Mn|O|Z?k^c@9av}@0#)K>kkJQ&%S=Me);>&`em8^>6v$U-*<P(e{vmw5AePRa^KX)!Kw4gHocv^m*oB0Tvy&lyq!<HTeXB-KUB}QEw%H}_!QSa#`~{-@F~v61(mnz$E=U;%DpmQ;2qwtK*7y2?+uyirZ%pOPjNrT^!x8enSTGcn!Het`|#v$GEZ$gCF2So{8W6P+yNO^@1&8>-&3o|_-Xx#+;76WGw|z2$^4ObqKps5k3D#v^y34JA9v{&$@;?_e}BKr_zC&?Epz?j>vtGGj_Gebc&&b2X5Lt^P>v7YV*FSaX2|h*e*G%%`x08!T&@Fa{I1_uEB<?#AL=&O<H~ru8a`vZjH~huv=28PC!g!<{vqSr_$K1*rQgeSe#y&v{SQB~L*}DXadO@oUqZa~%st(2op-elemGLDZ<?l;*M$#%BtE?OZ+RbIy1!ieCu`}Sx0`2?^$Z_)T6}1vCF^zbo!SS7+|}Mq$|&O&9~vs&&VN_tnes!Ir*<A0pJH7z-oLKlQ=CVmYRUdw>ZgyJv;U0DBgS7AZ%x}K$Mf@H3EJOluJ7x)Ij_mQfe+so?=(Lr^TxrR(m(q{@#T+7KR!H1e0b7M>HoWs_HLW3GX68pl>4oCtDShK|0EfQ)9)|S+rOPp_AmD@vQFbecf{KllH_`7{!dGjoku+u$vDSH&!f=HQ{MjQdF1Oi=aIiZdLH@u&3P0u{lmYN?LXg49|!BTpJd*^2iu7c&i_Hi+XvHRKktr}<2mw(^y5SK#D}kKm;Mjml>PC~d-xRdp6U0`d#2w%?=|S6KL<zWft`z`A8+P?K+IRtzb(hty3fo5Rx6nYF5I81kK?qXvc4Q`E%N~0njzkPqOQyXn{&_BKVPbW9EX?-avbo1GUDx?-^p<(nO*zvzG32@*dzV;-~sWjvq}0NeQ{=L=biB>)-U7z>lZ%7=l97ke6IJW>_R=CSbM5UKR#Gqd?>cG^bgFSeW?5oa-a50N16AGuOQz2y0Oe-hqp}D{)gWB^O5!OFLGUo51+-yekbE@UB^k@_r-1AM&6g>rzYy3E0QGNv;4Y1#xve2B|cPohK%R!V?Xwe2lsM<ye@onJOt()^Y*70pZFBx)Aaktr|I{P&p!LddCzyZe1hyh-kk5@$#YJ5`_1|8?~k7EzJ7DQ`}@uL9_@FE4$!{EVOiH6ZZG2;@3s_gk8C94yjGnN4O1J3_!Q&Nc>g%Wrx=HAdwtn3wd0RZar{lc|M;7J|MCB=<5Impj0bDr<I;~e*O~UI>eBzj{^fc*ukMt2V0>>mK6tk`zI|&sKGR;;-;)KG6_)k-$T2yu@!<sVR;}H#zC3z+WopOM_!R4@@&5G`pJF|Iy2mR0y3G2ryrisO#+&<8*Ycn8_M7W`f4>=T{{HCt;_Elp`9afPslWI;JM_Bg{#`)&@$Nt31D&%;|MwTxr#2ppPx1N7^!q=5nSTHGJNeQi>iruyTE1r~kXt_Q;{$`lJ6Hde&tV-)i(frN-p6vU%jY_La1H)Wd%0hccANhGGq@#<+;4fSsEh}Ec&m8pd`_9?XY3I_X}#S4Y5JJ-<Aa}wcNSOE{qEz>$^MPnDCcjtxAgcl-W@I8J<&zR=kRB@dB?vqC=Kg7p79_4{<hp-X}@QCs^b%%Vtg9!AD{RX-!r~mdq-;Tukk7FTbh3VeM{5tdw&D3w$SfKu>ErV{O%`v<-RaJ+(Eo^V6)t38nIQ@A#=WDnkM&M@#b@}J7D|?Z-4ZB@%5Ygy8eFix!Cddo9i+9?fR$Xd4C?C;O#fwx-LG{c!F#{%V+v~snFH`^yfCK;7++8hYw#8?>x6bucv`7+xPLjGJeA2^!PE}o`Y{YNROZ3%Bu%b8xO|&$3xWn#)I+x@es}xdoZ=}V7z}kMEiZ?A=>X755ZIWrGM*O8UOX((AO=-hqmAo@4H?f#9JdXE%*9>@!@}`czxK#x2-zG`@A9J`<+hk`XJt}cGXR`pQb-^Cw(0i{`i#s+z@V1MLr*`{Zj7d;)AyM;EhT8{k1>rBljD8-%A?r|6Ve*FHvXsqxa-|J<vkWhfzOXyfdx3%yaY3$mhr#edPO*g7Uq-@z$UC5n1&2b%7k0v=7|5Ex+e+hVRAkp_}3ZjngLUcc1UKDz$#Qjd;@^+;#nMvh(Zhc=`SwZ_Y30LMiFb^@qH!m*Zvr&vi-ekKmn7;+-YS_55yEDk;~YUH0n7)<@;!z5w1fp6~08ca1Ogm%h*M94?TQ+Bi2p#kywt{p*_P_kUj#?<A#mo*M5zPov)d`$%~IdFr}fh~K<Wu75gAmvskkCyKYrjgWQc#(eFA^Owpvyx3N*|M8abcj|8U`p`V_R=1~Cd416MRV}9{+m7*NMosfRuR9kXlXq3J{V~2ziS1r*8NZ^gd_KFfUS8LfU-bKDg@%L@Q}f|BM|r(t{JJY2G)&F+%@@*-e@v^_^Wd6sa^GOq9l0-$53R-bIjhg}P^qli2kuo9Kfbtp4}lNf7jNy#Bjf(eB<cTSj@;L-QC02>;hme}gZ)d%`7mLhTwgp@T&{mJ71^EW@lG@R$+WWmjr&KgUoy8|p#A!get)Ar3x3TPTfE-MCf<ybsLw9mswnpl+zz$mdc57Aa(|BfiTdZo+wZ2=`xCy^fX`b~hv@#kXXU!a_;&c`mu*Vczox79_KbOlll6}i?;QU^j%WN6vi`XD<@bSd&XVzrcN4{1oEOGho5Z_^-{0chj<r#|J$kgP6HoU!mfHDfy#IWRdf$9ve2VL+J-cK-eZN0xy#MznquxKC;8V;e_!QS^W;_1t@R_;f`?hy~(VyR~dpTr&!&{@o+uhPi|MjJM{tnG;Bfno*<*fdFQRCft`2V)+>x@vH74rKc2M)>iTl*I1e&g*!;@zneq`$&iS${U2lkbHS|J2v{#s@d!<In2r_wbsnvOgWih~LpdZ{PUv%i`TyHRXD!Q}z?7onOZL&#zGaGTH}jERg%38E)%wWqcU#ynR-Wt8m>q+K0~Ok^VL{^!E_P2hWLj0)=JWYv15RYUgj%`_5nE{pWAg`_5mx)wA+?PtBC;$@oR``=WU3w0LL!WSNKdw2|xIt^xVI8T*3nH{R(c-p;y5=Cg0x$@Wk5m;HG4&4r1ndDdm)!^Vf=7V5s|UlTvjb-n#jpKq)9?W-1gy_FyTS4+JetLG4T-tOmQp8q{buNNu&?t7!W-s*v$`s&Drsd;y>UN5ZkZ^-e<{DK}QR)HA(`>`p!Q+2f0JH`iRjck~jZ#6@<UvZc`uW!DMdf$8-u!hU)`a9<e?|3%e`4`W44*c<6s^i~y|M(B=7$MK=o6n=(H=jqnZ$6KD-+XR&94q@X>oI-(Y5mwwe(wiw<DI2n?Dl$hCjA8$tn+%u`1=z>ULP>NR)tWq=lv4DcJMl{58~}dM(p<b@C@<6;@#x>Bh826ee03&{`JUs|9TYlzV#@0TzshM0l8mvBuReH2_G<iV&OerA8I1rx?66&*W1RgyAtyHaAW+qF`;D7Yy7mo)_HvZ?{rGLCs}_Z`m^jxO6J4+)_UK^s6Q*-9B1RL`At@*_Iiys<0R_m;TaFcyL0i32jhdrGajO^%Xr2^)Xx!b-uLM9;{C7J>9<_}`wiQ_pReP6+i|Q@+PnVOn_hf4Gu!|3W9hHoLe}N@1nI|HjquavNdNAM;(x!VfB(bj`K<Kgoj=8g4mH;O;lWF#|HavQK6M7(mfz<v{w4gJCR@DT=^)<9TWO1TJ5ERX?H}ZG_4S0**E{3=>m5GDdS|?Ey|diwsn4Ir`{qyUli$Q=xUwo)KR%FNe008T_h;(!q4ECt(0KoRXuNMe4BWq+eEXY!)%T5}-fVx~=8ehv&GvVnKb)-JY(Mt6%(qkSr9NNbQ_NTR6!VqwzWK_o_n(|!*;>l?g!^yF_VIRB{F6^?@p>ndczaXjEy=c%QM~n7Wc;*B_OIP)rq5d4svN;cWwhd~9-Te^)J^||Wkoaff9lq&+W*%-b*o*w>i_khy48;CL*qz2PAMKhDSm})2EPJ#C7*@6!kr@3o_v9P7JdP4Nj?Rud<Jd_w;?};+rTp@#Z$;hu*%8s6nHAR2v#{Co(hM^*>DJ+ODSGR&W9Jmi^)asVt6&V5?&3jC)dL3;Z5WQcoV#iTm!FzSCK2=Rq!|D*YG#+0&*U_0G>lB{)$pOi~Jm(1%F0PgjIe5e+Ew{o5R!L)|BEFk$Ndo&qwNIvK9O?+=Wv7G}!`v8h(;&4y$|ueiE)j)`aW8wa6N<$|i6vxGDKK+!TI;900#b4k8D@gWz7|D{wEkJJ}WP4tFLy!JXlb)`N4bBc=E`@&#CBOIT$aSmg}(Id~>H1y(r~RvCg-&V^^fW;=7)7nKV=`?ipMSGm~pS{CzKRj&5D_SK%_vzp_lay_haljqoO;@H0l4<y&YDp$b+;hvP@Zsa$x$^~#YI7rTcgK&pPwI#nK=fEnzf>q9fRelDmoDP2pw<TM{DqFxRTfr)yhugv($d}*_aFBf2v;Qyi`c!uDyxuMxn}K8xvJ0&8X}Aa6h<p-OSqE+eKStJqRW^lHz5zc5_qQILSN+L>@IaosKiLT09us-*BXx&ToH<r<2dql*f4D91fAB@}TlgY;np_K?hA)sCV3mpR1^6DNI8&_Tc6dAcs#ulc%CS<4>yv7~>r;xWlWM=K^H_03@*=EC@xQp!@V{_{Sjh|U1@=|3D#h`!Qi|)5YG3QI&z0eNa22vXTm^oNQe2y?4%dduk`>{y@ZY>1wcmeJip${CzLsI1<KZ%JO-iv%)`RP@e>SDKAekFpAKCtzNPSN!4wLKPFnphM;rnogSjnxhD#f>P8{xXKk{QX3u*z+)D#dqko8i0gd2&6xp8Y;gDgK92TrO5J469OHjl2)5Qe1~rub~dF<u<+!Tq*X!>#0O3Zb&JvN@j#rs@G7J$BN67=i&40w_;U_|DqI^!l~C#ic(yQtOnPD8<2J22JoX~CAbp%{V1h4j#8YDQe1<q3fF*3ljUKRYQIbKSn)ARaS5Dy4JCLjwcrwP5lV4hvH{$Hea%b8!4?@q#=&vCh8Rk5ETuRNnIBFArzH!(Y2kEaK{y?pp3DtDL>3}*!z!!5Dj$Oj!9~g1a8bA<Sr%5Q=8KX%R{R}vh?*n5<FVqaF;a^EBx}MdZP?~DC@#qBRIEzzEiyl>O7TrHAFN98A7l+!mEtR8X;`HiA6F>FNtEK^{Jk0<#Th3>;NozAQk;j(3+I8ec*aT=N^w>)2F?m+BV*xgaCR~coE^?VriF9B50mNOhvA%LdN?PX%QJ>@k%iz~aA8VuF|sIJlrd3^Qv3*|_$cE>jgO<0;>+Y!_%eKh{1d(b|4!b5e}{h~Z^FO9*U3NN>+mJ=3Ven4UUAMy<xq1kSplvDHz4c54dAwv;?|LRlB`44gX_RW$qH~$_#aC$2dql*2}?@xX)-6Q@&`*;mEx`Bc6cj1Hc}1956SKDhwx}h@gedD_z--RRL^~t$BHwtUzOlYa5b_4Tn%nPwuM{3{Uh}$*^_Jwx8<1jq!jn?9QPh%H@F8pjC>0o22Uryg7=WS$gkjC@GMI48{}K?8*mr08{7qMN<IlUg=>*@;978DvM5{_{>ze7<Kr(%@pt42_&azRrFc1c8a~bVSWYP(N{)qx!qq)vNO3{3Fxdbu4BO;~unkuxN5fUf_sG%kd+;9e5WELIPhN#psxfz-$BJVaht=R%xD2JZ71;uA1rH?q!vo<7o-sOsQhbC`e27x~4%rj#$+&!n90tDwe@RY<zl0BY#;Do8;sfL^co$>z0Ht^``35{0?n`!o`@+r1rf_q(Dp?Dz3TGe-!x`YqmZTb^mnp>u$nW3-@JMnQJQA)Lsodo2<T7{}WA}A(DEvAcPgaNH;oP2aoSRadmn;kyX6)uAE5l~&=A{(prxX{Z6xSo)gX_V=$vyCJcqe%t-U**0)i^%KW5s`vWnfi`i{V<q#o)%2;#bLm@T>3`asoUCUQHf>kCJN5UyWCMgfVKa2NV}055zpUW>9RdF%+9?55@cFoeb}TCz5^PiEtmXIot<+nyd;x4L?dLPETflGcbPB^H}jk#_$37BD{|r3Gaj7Co975!{t3=x;&*gSESOB50Say+>En_D8(7c{BTA%E2a2hvMBs8oIO(YBQ-8kW5{jr7<fyhz9-L++u$?sK}zu`avVGgu0$zrNY;lN!i6GLfUHK=hwHOX)hNY7$Sv>?IKi{u3FL7&0bWWeK1TixAA|3ZMPh{Sz=dKYYr}=$n&cC3O}Gi!6>b7|Cf|fR!$ZjsJQSWuDc%{W-Q+Yf1c&(fX_Vr($*%C*aCh<vxI6qTSsQ*9u1gky>%!$pb-c>+SaEjpIDDM<L$NBw50htLRf@0R4#HR9Fr|1mISSqlJ7gu;fgg=jJ~9tk39iIg%tID}&A7}%DUKtn!Eta^atK@%9!w^{35>tN{H)3f<Wjf-`~i6k{s7)j-hubSmq;}(FY#FMLyXm$@I!DFvI$%TZbo*7o58P<L*dupN#sm;61<<>37fIIpHh5~oCY6+XOM5hGvMK5cla<r^9eZ|{sex7><)KlOus@YZbR0E+rah7@^F2)BAFe|&e*L;Db7f$v73>{ietzye1kkoDu0$zyo1~g?|_Gq4m=F5OFjzMg^PI30ma$K9ArK?2b_gcoPo>(XMod_ad3Lr{85~ftN`bP%aI?z<=_$Ies~1Dm%Ie;g)fk5Okd!!;&hDjDsVcuGT98S3_nG_20sP&CMUtY;g8Av@W=4p7`f-8G7q^w=D|H8#R2kQ%!7MMii?wn;Usbusr)KR@p$qRcs$&Xd<A}mG2M?+{0vzieg=*wE5a2SyYZCb(qs%=8V<xf7}JWY<MNQo=i#y9YnJ3$_!^u<?tqivL~<CM2){+vh2MgUlSN=N?u%2317s#R02d=O!z#1G#o$NCqOi((@FVcs<Z$?H*d=$uE_{?c2OouhA^(7Xf%C>ls_Xl_l;Rp>W4H$VIQc64IQ%j>27VbHLav5~z;j|Ad<K|9UWVtu%g7t>GI%NZJG>NLLjDFXfftk4;l=Q5@)E2v2~OfXnN2BvJyIRX(c~&v<#>2BJb>&6_v1VnKq+oX#>4TP4=u?6+!AgS^WfZQL_P*Lf_sr2;g0N6FLD4pfbA;2r^aX`Z(34{)5J*TgVVqz$o6mv_ytPwibx%g)X7LCkSpK>_(ifk{32X{%m?RVKMGKavyy7Rv+`K+f0pD;_&@khO7U-$;$JDn|B~u;{>x*<#d+-|;1ayf;*{d&B6UB~e=Aa1VkFbX2&+<@pDYRIhdYq%;12Lg@*{X9e2P+hE>hPb^=qW2Qi{Kz6i*?~!RPqdDU{;p$#(Gb@FQeNxFoOP5lZo0UaNY|cPYi!DaF52if>bjEq?AkY;hd3k?PoGqZAh;^TP$<m&gwAOYm}XCA^Yjx13UZf;<PGfPWx=g@1s5Ca=Li!#`1qe~i=_@)z<Ne2w?%7xHuX7x+W+Gg#$wu*w%;l`CMCC*cp_v*dC3IQw*#`~_Cu=`4zo?|f8#9rNHjAjLVzg)tAlGg6$LToCi%J0`{1$oVl3zLQd%m7Evz;5#hES;)CD55DtKtge03pArlWl_ehx6V0(?DL58RLzafqz-h@ca9TJWSr$$Q=OSN(bHVDqi@F!2?g5pf6vvV2;W+pwOH$qUQGAL#LSBSb?t_oO8_D<Kjqtl<dAL0L_AaG(Jf*lFSr+aG_a)1~ec{*0((r3=AF>qO2kuRlgnPrUk|p3*;g2ZA?MMq&e{#a@;CIM!@H_Cg<OujAd6*mltK178hJPe4z(2ydVkFgde=bUKS+X)*7H&vB1vi8{k-gzg@F4PIco006+zapJyckO<ewR}0kn>;%evh0FzXy*X7r-On_sNCu`|t<k*YF4MNOBQ8iu{IL1TSKK`G(8|t5Q6URQG4cQHlqX6XC&dkn95oVVis!ewuUArWBW=6z3-6;N0-fmZUl-fA*ZKKU0c#kw@SooRhmK#Y@O{;deO?myrG7CGciS@iek8+?R828m0JSO7R4;4?F?>g6s|V=G;@<s##2IT$=yae--oKj~Y)_vi~^7|C7mo?cV#7*CX4C{t|wxX6e-D`^W?xtA8Q4tojW?>wf@c0amg'

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
