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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_005.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_005.stl', 'source_sha256': 'b29a08411c5be11a7032f7aee688f48759ad8e3f15b44e4adb5daf739e83ca1f', 'input_faces': 576, 'input_vertices': 467, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06375520676374435, 0.06542974710464478, 0.05872213840484619], [0.051784664392471313, 0.2661195397377014, 0.2914625406265259]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@zsJwj`$X?tgoF@`UNWxEL@#5Ec7rgC5p9&w4iUXalp)+Gk%H)5TrEV2$Y_HZcNoSnqnFWN_V4?R+;jf#t@YM>X6^O;+;8^%oqhJ+XSaLSbnwrZsep!mWwenCqjI#WtZ6Fc(h6v!14oP+)Gu(P@6ci6ESiV->R+0Mw(HuqLwAcdS{v`xKX7Ef5nlDJUJVD-^{Q<38W1#M)QEtgeS${x4^)1OfFUCTQ~i<O1`G>K{p?+{cAd)B8Wk&BCtClH|8k@j!PTVG*2Af)pI&sJkt$QZ!ih><tqRA9Uu)|=_1T)I_bKuJy1q&LJ)Q^EXGh0`)1u`Q;K#SyBl)U!JS6&Z9Q?2r;#(~{Pl_KhN_?%xi(Tro)5Gc%Et4C5hcSEAXTAKk{Stp`R>WC0S3cWI#L9K8doIUH{(E0Y9Gm}~Ba**sNR0R;&ckmxM#`gG2g4uNey3b7<mFL`cQ6C|xdC!r+uWiO-*xmtv|Kk=aVftR9wOJ*V`IhFe%mc^v`e+5{I2h^!QatY>dn@nvc$74JR2o`+-a#dEuz+0xo&_Ce^gG1WBvC>DZg#<58~?&ZtjrltsQb)%Db)}@_TjLE#J@3Ez#hI&6oSM4Q+_{H_O34SseFU#yeiFQ!gX@z%|nDu3^0;zoSvgM!D|S&7|Hmzbm-kq_g5{AL`-z*WRCz>qNFk{`gW-PUqI)Xva;Z;P-nc^`PDAC-H4f?nR34s3`ee%}z=E>(e5{*Y+HT|FU#~#HnM4AAd~hU++3uuItFq9C3nPiSI0U4u4<$>jv>>&)+WBeKhL``t|Ge5+~*>X%G8IUCLvPcqYD{e*^lN?*R12S?Az4JSuS<_fn3D7CD7Dt=dXGYr$>Kp<l0s|13eiuU|PY{YO9YVIA(PVLaNSt>m}Qy$!!mE9npR*J0voF<0TQKfO)jo{Br_?&}Fr((bm~52YToZl{p{WDW5hL7VXWJ+;H%wT<nSUE;euzCxUwcJ!<I6Xbcc&8&p{&S<$`=bEoh$lvc>T`T@ZZ;9(z6C?HJimC;_)HkRv*I6l#vsqGv_=7y8JkIk|(662x5?_yahv&LtS=7_&&B$--w++vE*fBhhYvGqaD{)*8bEBT0|LhR|Kp5_~z##Y$$Kc-{aaiuhzj%^-@5W~F^`sTjpY-JLt@6ED;mGfO3+2z4PvST>E{0#dx7@#@>JiDW*PaLeMjeS`AMi%v>nCQwFPS3Ob-mq#_U$qi*Y%H=`gM+umpHZ&V~~H~9cdTG%gGYQx+MVlCuWoKxI&lVd6`@g`ENZ$y?p#@E9&*PHK>O`X)o8<2~sXc&P4cM`b+=Q^aE0_wu<rM>+Qdj@;DxrKQG^#8jk#{eb8PV?@RghH^bpCz9G-E)jAXRo7Dq;mI*R$*v2o|;qL48?#Vo1D|u7OsU1jKE&01+JaLs>je7oko%njyTv9&QzQr=W+2&4#-|7<jVbD5>=e!dDKhFy(k1Z*Wl;8REW4Of6TTY%6SGO+^&*O#odfZ@)t1+MBy1w_}k1i<r9l4529PL6!#JSN_`nfIaHomtuGxFc@#(4YUd6K)YH7_mgr04xZ%4>7JStb7dYunM!TT44Q-~ItVGDPaZ(RCf_v(9<(^$ejB-|Fur<*^-X3_oD?PSi_l^yeCd5NAVcjI(v)w;B9`&!ryiUE?H<BS?c^t%iKxk$o-td(~bmCBFA*X+QglKQTVE?IgbTeWH{{XFu00d69qfN!-`qV2nR`;(o$)?@9l(#r`hWwN_pazi)SGKYMQn$`cYSzCI^6=DBHa#ka2;3qL6XuIrm<@NM@!ljV9FT@ufFvoG=&o`d?Vv;VxiuYK5sdBx)*{CZ80ziB3k;|yCZ<B;pCI`D7j!~DMVX0pMLd5!sN#WeKuQI!$D<9;c>wf+s1Gsnvn=(qn!d)X_7z(2GTzJGDt*M>C`U%wtLzBYZal*4)4=Ym{!*hu(K%Awtx)JA{E;s?LdDU|=jA<QRN9xs>pI}^}<5>KOlwm%`hwzoaXUE;dYpEE<^IEtT@=hzXop7{q#ecCSu;yMW{mb>?VTVy!uGs86a|JIjzQ`_{Tl;8Pt9r#aj;`x1ZRmLUjXJz5P8ja_z=_0J(23g<_eu;7IkpBsH-?sgGl+&jr){WC&E|YR@`xooEfjRKpm2kozK3K|c{mzE|vV9hO%VVt5-qaW0R<SqyZ@XfhFdXY2d&|!76VA%I%Eo@E1-62JcbLrA`nV}_zm9k>_zm0Rxq4Jr;@jWk72o#DFQ~`+$rwjR++8a7Tc8)#V_#NGcK5Z0cjf+VqpBlLzykQ)d{O^H?HKo7evLSzmrDEEYGlNHb*L-8%?H=DwfX_;hoM#AFOS9buFQ~e!g0rfIBg>F9L?Z!b}1%Iu6z3y>i6+MT-PHk4A*@r{YFndF7;rI><$07B=qx1jSPP3It1fSbOotr?N%%JEB-{iwa9?_{OE@`j~8GbeK`_3CLjEK8RU7?=MCTC?rT%BV_jXnzm(Uy<J}VY?eKiHm?`n?l`g=ax)klwBcJq7?cFr-^$K3{ef#?+=iGfQOHGusTq4?~P7vcf!8$+c+y#UGvJS@Q8P&wsyY`3QG#c|<KRe<qYKQCkjFIuvS-c<G?Oa{tckITz+3*AEzd{k@58i=wZPXErC(Uvr|J>+!_x_pY>kVU29`D=+Ut3p0;@I>4X^gX}n)Dl6>(zMv`euMXD^%7wdfm>r-_?JIqCAH&pJtze@?X0Q|J5~_pR{VNFn`@0CBC+!9M*q6(P#%-7x=j|qMjG7L_a){uvp^s50d9!YxWKN(vjk8nX}9NIx8ojJUfHn|8Y*nC1<5DJl~a@A&%Az>#D3*q&&{n_29RR!FpzM-W17S@75xT!|_mGFdOZa6brxqDz48PVSMnO1K)EN_64pSh|@xc|L9kYZ~InbT|H$m{G=4D&sM}@-Q=0FP<;OfSPvI@D&vs8G7|p7spt=$UC=K3R>HUM#=3M&@i@^d3&q#RPsDh#pt1O_YQx|^`3>v9!4t)IB-DfdhX>XV&!Q0L4`2BG9-lJw+cf{BFUH9ztK6T<FAw}q^ROQq<;48+?C}CA=f`NdFMV+5lLp_fzSNsDyra~cePf*X`izozekWhXcv5N_eDBuM-<(5g%XRJF3`Lx&N3d`0+v9?}ujh%x`1yO7(f9Zp<H^R&SVxC_jX24N;Fl^a<*|lXkiSVOoF}X-Cvj|bo%2!8`(!?|cY1?%?$;Uq;Ym1GIn+(!*w*-o?;PNV=j~%nwD0`8^CZ7@B-UF~Mx&h*li^pskNkn3$@6E;asa;X6sb?=*n83s^{BG&7v9JE;hPueCp~_ji|68v_^!ZgSZ{neTYP=-J;XU({fxnHJr?t3&}+2&^ilAK`(gd}=NYW)j`l|U!;55`aeNnxc5!T-BmU%P7@s#yPjUD4ySL^3wHwV*&Ko}=Ki7K>&lT7&b`FBS;g<9#t^76o{pID^;y0*+bAwu#-}LWe;lJC0{qN`+xWDKy@%7WK@m&9UBiY@z4PA%tKX@+f=Iq%8`2(h79-Kc8e}CA2mc(B(9phV(Y6f5LIvV@ld_m|}726|!ribYN#X6z<5#`{2_yy1Deq7&ncK1y29dj^We^`X)C0m5}dX7UFe_}YFHk$*#WnbJE*O{(Ytq~`F3)Z9iuHjrOCL8?vOHiIF#W3IXJ~>0`q0}ynvsqkHE_>Ty;%mF6;9TQ?FURL*@RNICyjty(Wbi|hB(AONGVIfRj!u_yj*FB2U^}=$zGok}NqpOq4``3O<uJe9)WvruT|vG0Hka{9dwnoO;tZMML_7Aq;O=Y9JmmY%$~Me*H8;Y)7=eAq^wI`jZ}A1zNd>YS{Zi*J4>o^-at&LAI1Td4b+vV~F1Y*pzyO)Y^*O&9^6T%<;ry=he)N++1L2Q2A<v05-?J0$zBch4_ESYq;=cRThrh6|Jpaz)+b|yHe?3k7mCbRE*Sa9~XS?j;>zh2$?=x09@9t|aZ({zt-v#GjRcgWKd6D+>U5sy`+k+)eVmS7>PgAguXgOSbEw&=&-z{bFTyK6jRs58nan2TY2Ipt1mWi)d^uv7TymQ{&*Shya|6a8P{i@N&De&jwTq*Z<^k3g7_#KO3-_gE1)@#2H5MRGmMXswI$&}*mYuiuBc<%hNvC&^}82gBBf#N%pKZ9RvAJ?%bE*Sg?5jY1QzYNc1t~a_|ciu(J3r81RaQC%{Ss4FMk4OCAB>3&B<2mit9r;I&f$#G##%GHc`r(!U#OL{#)&~0*%_n}c<ll<(4J`xmTNgDDU*G=}=NF4V$2fl}$0W&r><Z@N9$B#7_M16T@}I5_KRN~DQn70j#E%NbxVJLg;A_q@n6LM&NHOHUv>f|7?q9SV!N^}=1?IW_!_ohzc7s32h5oQ?F#7pxAH+F`c}u%_3FkUjCXSc<`CFo%KW4%_US<7{;$QBG`7+N5lrvQO=L_XqoS2VudL|fruE(@vZ<7pu(Yx?7A31OE1HEw0!t=3Deyt8DKlhuTe2#~%^$*Xw`+Dd|<iC*1;A@%3VH}Q~a?+4Lb_M*}&rTcsdFwH5R$q3?;0MK_pInMaG{o=r0rN$HU}HJ6Zp1!)(mtcFwUz$hc=p8L>uK|Eqp}wa`PmO$gBlop_Gi6uGlQ=`%8hk?cypuAeSy7TF=L!FoUfaYG5Ues&>w1iW{fkx&n`oMPV;m8!}VLVF@KLg<$2dUZW-gZiI;V({qpPW2LHh{tV>IKrx^SJ`LG|%A7sd{k1vb;NRt3#{ySfbpEhoP%HJQq%h)+Te#+nWA@(Wr7a8Lm=JOcpZOqT#DfCVojrnt3#qUI8Cm8)4Z883rsb};HUc$bz`Fmsi{OXJSV3Czu4Sw$N@E@Hv<}X<a^JdaoqrY?({3DZ$ey!`+x30=<jGwnK=5ddn#{5BX;=2krH2Pn(#qWHtJdN${xeEK%&9&nUey#`DUp&Zb%s*+yG57K3lOJ6H^Skq3<8ySj&vEp_iCYZ$7u?4>rokg)|9p~w-yN1$Fy=p(LB=oJQ<pLSk+(R%xaeWXuYJVtI*tp8#`1jYjrnUxs4;$_IE*7RVvPCQ2g^8OZ!^<aKZOq9cSq+4WB%U9vA*o$WAx9I!0&~delfOV?_}}yt4j^ztv-4l_UZeJ8K1kZ53t^y9BUZ2^&Q2qF3CC8I6l9xhjaE@aXSt9_rJjRj}0}B!#CF9e6vBFGX{TmF|6k%XWZ-VJAY~ke?wQ}c<U93^}(=#2MqbEM<M_2CB|`n;Tg<#L!X~8<j-&m^J4if#|`m+KtHoJ_CM_I+v>hYy?1(l)ZiDxeou?7hu_Dm9{Eu|o90dZ>QCdvH_fxI*R3XqZ<?>ueDi$mm^KReP4m7p^bCB{`XS9XuOIYMui%^3A=X{vCW>!bw`lF(iLcr7qx|zf;<~?hO%mU<{;}q$GFd*G)=S#@IPuNvE7y15=#t;G9&=P3Ccb(7X3g{~eA9YQPkf3vrgdYQZ(cXr=4G2ApH1u1Prhkg>I&~8zIi>I=9|~UpM2AL*md6l-?ZM=-@bxxTAy3HFPtiWH?8wsB_gLHzj2-KsPZ1ZX}{piI5-&n)wI7Ta3mP@WZaLq?p2v4`Az#5ZA5qR&HJD<-@FfUoPPq}w4buOT7`&j-hZv{E&hM(;|7gFe)B%A%53<i{iF6|4Sdu7G|e~fPe1vl{ply)v=9B{oA#m3ox9+h_R(p+c^_@-vtYV>Htolqo*TqB@84~klEwdz{r*(H84}-gZeVTE8NTV<KriML-+V5i546mb&!%$>>)5a1o6bG#mTBVu$2rN&IQXV>l{DXc4x{xcF-z2RZsUsWCBFIm$2xHSZ1GL!PHDdR+{smGz4+$yE4{&6#Nm4a&L-y(XGQ27$!|J0b2j~cuK1>NIop}#;+xO?tbxVniElbTbot+eZ$6()^G)ZIde7SPC9dh5)A@X__~!Fc{rZFjqNa0QZR=m+o6n6Mt8y%q&!%%`muGGGrgQ91zWKa*_!#)6^KiZJa`>k6bK9G>;+xOmKl!F}cztRTeA9Wp)iq#|_@?uJ*SZPtO}`gd$NeR~KBgYp{nF@UcmF?rr<l?sRD9F#DbC!sCFsw_-<9+|MZ-i*zppulE`rbB*|mQPp?_7#zEphE?}mEBQt{2dSK3N?E)(DMJE?7VBz(SqlJ>i~cJlo)w72nhVeRvp%h6uO-<KVpOW~V-r?z*#1>f}hxT}A?6%vp8KG(%xF%N`>zz@2~_f>XdUfWgUCy8TzAHc7V_*#?NcyGkB7RIrCe<Od(AMxJQjXJn)V$+r4w_b?*O?!_eww?Iq_b!};LXdykR=htM5QFh>?B!LGe@sWb|F*0r*0aY8hs)o$H^BQ04~D?6+D?4)`z@{&)8I#j^Zm?s7<Wg;td=;Y_j7dL>uV&x>AfT8x!4HtP496ztOp~|FO2VfIlX<?Nq*D&X4>=w_@?*S^e=C~H@z3<+Iwcb{N4PX-nr`=#5cVM=vvz<Qhf7!gTwE_H@%l=ztnc4_~!Q;hbF@}zb84_D+=W|zHjMRI0?S#Jx~2wbhP-U_egF1E{Sh`?^Fv3juCZ#ueF2WE#xxCY!me2sb5V^*|h@NfB?5wkd>+arRjhF3i6<u|EpJ!Yt^a!|9u5{bZQy8r>0d*ipNtMk(JgVEA31kPhLR%n!JF#klLHPoZ6S#o7|V&lKLfCX=8Frat&%-veJs=8e~suVY1TvWKVKg>SyG#<bu=;<bvd^RE@0uS;$$*IjNb*O7oF(l1os_kxP)hs8z^bWM66nvM;$7lj3I7*5qd7j?}JXrGv;F$pffU$Vw-Y2ax+we<b%K_o9v>_agV8jwJUW4`EWQQ-31s<Ou3vas>Ibs%H!I13w=oe;~i79wEOcf25uye<Z8MQhF+_F)d&V^(<K>#hIz+$to#+NADb2=^^qv@+0b6@+0zJ)D`5v$XBUz$XCgim=vc_e;}ujoz!k*rR~U0awN3{Ig-2~HF;Q|as1qZ97i6?q}Y#IiR?%Ap%y1A%}e$nm!ak$mmwFUW+N9Pdr&izJ;=G46lbSqBxfh*qGlm0%|p&bE=jeLOOmTnn~<xL1E@2}N>`Hu$TO(B$TP?fnG`>zt|mVv-=oeX-y>h6jv!wnCsI3+6UoP@t;om7+o=u7+sU!i+T>VrG_@u<njA%~M~))LP@9rt$eXEOkT;X}QrnXEl9QMeAE0(2A0Q`C`;ZgJXQ+e8XUGSs1IbFqkq?ruQzwzHle1Wm6yKmXnS6tMnL3+%nS6mdoP2@2pW2hGG>E*Pe33ehe35*gN%1e#>EvI?e^b|x|0X}79wk2^XS6`CkX2HgiF$&plHynNHj!VEA5&M6ACr@*<H<@Fkdw)OP#2Q_Am7!}*AsV{6yHuw>r#^=HEm5z$Eo|M4)Q+o?$k6lHSI}FA=Dk@5OOeeCpnlri@J?Gi#(6Io4lLXn#ZJgDs>%sDmgqg{Yia5T}OUE{)f7i{15qs+daQvQk=npr1&+xedO2V=hWTg=j3P9ZRBU<m(-o)m*jt`JIMc%-%$6E-;m!jDUPSkCC8Ijrlzsf@2GRh-;w)ML&*Kfc4{!$P7b8bA_tPcr_LkKW7~Ysq<9Q9oIHjc>ehat)LZ0G@-phL<Ynaf)ZfVS$xEm=$xFy#R2MmnyqNksc`<n@^)^}Qa`IC0H`Ko5Z^-qjEy+r2kd=Cpm6j#fCzq!dB$p=_rDi27%}G{Tf?Skbn(9R^O|DG!C08a_r`94@Cx6bQ*hXzewvpRYJCc<SAS>-hZclDQ?L}@w?m+E9?m+&EI)wZc`CBH%6R0|Q0(lWNg1m^lk$RfEk^HlkzHa`RpA~0IO{J(MsaeS-$wjGZZC#X~6&IntC#$5mF!du@CB=oPYHeMJNpV4{g<OzafSQ?HfSjAE*3-GEkH{)1&Pn}?tdim!)T?Bb6z8H|BCDi0j|EBbXVet3N{aJRon)nvWR(=>r*0tU=ejzdC4HT(Sk~L*eB}Jp^_KMSu4ineVPvIqEa}&s!!jzJX-O~hOiTKG&E&l*4Y8!(dkE`B=_pHjU5#R0DjjM`uiK%ld!>EJO1oLo+oc=ZP-#!MHtoqaSK7<15A<RmQQF6?&-7uRQW{`M?_-LKQ0<oVKB>4U^(#wyA6BgTcqwXE>R05h<k{2(<k{r4)F|>=atw7dIflH2x`Vuhypwu>tn?6hCwVW`N#097$fS55HJ-eWyo<V@yo<b*x|_U}yonk|-bCI=jV5m-FQzUfFDCb<_9OQu7iUsjjM|@Ej9h{mNG?GxO&v%sO}0`8k*(yi)WPJkWKZe<vM1S#`VHBOT#-p}CF*zNN@O4EaIz1%GIb=mGTE0phU`nOO8t>sm0XRgldF+Gr%oY%POd>6Pp(0(Nu5BhNv=(uNUlw;L!CsfL#|65N3Kh*Pn}GzPi{z^M^+j{Zb<%u`YrhjvW?oEY$G?J_8>PQH>G}0Zc1)W9YJnRZb_X^Zb@!M{ej$y{3VlOf9fo<Ke;V+1zG7_a$9nH>I`ywatG>EatCrp>eu9s<jzcryHJD4UC5oN%gIU?k~@*xQA5e?$Ze?0$Zg22sq@LL$t{=^H>3VUZboiQT|;h6ZbWsE8<G8}>&SlO2Gj_019Cm;YH~etE$T{gEpm105^{BN73v~#6|y&V8rhp%fjXL8fn1(Cgj}9njyjB7j$DRGaX2-W98Nw=-9uJ-oP3y^Ks`-PAfKaNAS+EFpCczxlgUZsvrLK;sprXw<df7h<dfuM)KlbR<RjD*WTi*RN66c#+sWI=kxYumQdg13lCx7i$V$~YW_Es7d`E*0CEp>hXHq<j>PH?%Zcg<fD=kBAPOe5RMy^J#K=mM3AeW-%CYK@?VNzUxnw?yLT!@;Bth6M#5ZRkrmF!LSrv{Lf&LI1fw@@FFw~*8Nt>SXjr&@a7R$QKXPfLFm6jz{L)6$<E#op9JE&W+jT!nf}OMf;MSEp{*(w}9;wWzUL`m?WCjSU_AEg1@A{Ga|8Lh1k1T&o%WheGCW8h`e4|K{}6Sf73b?BJhSojq$AQvXv2evQ=$toC0GN~L4'

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
