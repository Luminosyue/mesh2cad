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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a8ae3794594941bb2f7091d608b336/part_005.stl', 'relative_path': '25a8ae3794594941bb2f7091d608b336/part_005.stl', 'source_sha256': '36d083c89704132fd6c1dd2d1be1555aa6bed057d39e1af892fdf1c8cb7135c5', 'input_faces': 1524, 'input_vertices': 857, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.015013536438345909, -0.49792400002479553, -0.1573754996061325], [0.06095288693904877, -0.47984057664871216, 0.1678289771080017]]}
GEOMETRY_BASE85 = 'c$}rY2b2`m7Pj3pLz0XjK@giDpdd*QkkqK;EJ+Y`h=SxG3K&`h1qIPdkO71ti6BV{0)o?kiXbW%l^~*{qKIO^e2ri4I?t||+TH(J|N1`Hde{5R>zPxhPVMTdt~x`vj%j&Hh1`FYLdzan)BI$&P)JlbR4O!S$oPrF2Mw7}d-T}JDWT$CF8`^|>(Z-px4tQ%NujCL2M?JrXnge>!quA%ZCt%pxcbmB<0p<EF#66h;|C9syv=}-6Nbd|3Bv}A9TNY!M&pK!YK5=6x>ops@c-q11>-}A-JSJhR@}qG$9&@Xfhs#%N}jRa%QK6O_43H=)dIP;kIifB<(V&E>+*Lt2ik|bR&jax7lZvQd3ui5f8&FJJaXM*E}!vcFdx!)wzs`^P6YG$H+y;X&69yVz30it<>&NuXM*it+T`V#e+Bc<dp}R|`uTaNn}@ke7bVNH$CW(b<@Mh3^6bTTxxD6vMalB?2TOSEqff60<l4W@wg1SOVqPBm-}7#q+rNJzD@m@~O~_9a5A>6{VQtcWG`Ia|uH%n2|MDJh9-edkhaNcU^<#70FPrOrX`bG9ZPI=;xBY1D_fxjCmxo?^)z#svRa||TJiE>ti;}gEJX6H=GwH%aFE0^udG*?^ACrd%zqKf7d-{oLPXD19d0btZJUnm5qGavU>v6oEKN09(`?0z9WAp6Ci@AO(oE`7=yYXGu&-m@GACqSnD3+0|efa)7uAeEp19`OZLf4PU(?|WgC|Ub(>HMyrb!)sly!NO&UabzheoUS|u3Sd4_L(1~x#M-o{ee8RBGVl&lV`5TlaZ`__)uPV{w^*w*4zH+58QZaPxU@`Y#uo`E+bj{Nci{tUjEFtV*>dvx4C{y9_u(TBWe5Hf4F{nEcWtf?c>4i+FZ9gvO_y>zWNPz^YF!~`N{Ik@Dpx-&#r3g9q+A!+&r{9JU>|;+dap%Pv6oy(9f3l=O@ia&35g3m%hpCch?%%PmPY#vy$ZgI8E-4Q}dClllMcO&=0xa&#}s_y!|Tc@<=S=`Z2k`UpCkM>TrL=%ZIE9_G5CtACrd<GM<TdwD8(h+3VV`-0S)=d9-rL1<Bf{FP|Rl=lCmbevUmK?1wzGyTF2E?L%#5xPC_7dqeI#a`!UVkI7>*(iS9ZAH6_7{jX`_jqm85;CM{#kH_XZo@T}BdgCbhw(Eb`%QLc)<k@+iT9B-LX8(z<pIfJ2>y2ZV%R?)VyM9cbxnlW(r0s`~cm1^6aaHdAL!phXACqSueSAT(_TjX9TtDFoRdV+qZF0o*WAgM-ix(toAKo#+^%J`Jn-<b;{(EjbC2BvGl`QYuabdFdnTu|B{Y3JXY?-_LXE(ZjOdj3WYhlv%Yi@J>M4OZq54Uo8Y+V)CkIk#LS(vPSxaA$LpXU$M%iX_!KelCk!`$uteC*_IEpyGYpMQ5{ck$TBBf-4lcejfBb*_2X<>B1}-TdEI$K?ZC_4V4%+8u0Pt!Y2;?4bh#_sKR-|E-40Yt6jP>z~ghzaP!7Toue`zB|Fo_4=suX>*-Vlk0p&d!P04^goUUj<3!2_$IXH_(l&^o|wCTt+#}ndb4@>$Nuj4c0T0g(Ibb0^>1>&{!Q-Jf5nd{y7@jFJReQ&pN}Tj^D(+N|2?_;*Utx=>*qs4dp;kcPgb}mcmMi%Wpn+!vbq0xHP_|Y<pu<=BR1!H6#ciKmq#X~2d?8b_pjqe$9Q@8^IgHuXOsJ%&o<}tIZCeM(d)0x{p;_F>27})?hIaEOzvM_Os?0L==cmb|M#s7Tz_q@^Ja6s{`z^%70LS{Pv}Q;o&ORC0`sHSahvOP+~#^6*If5Ez3J9KKmNRZS7br5_WpHq+l9dX`u9sF_wScX?jJAB+24eI$P@a}`Jtc4h#J$p{q4v7f8Q+`$@0iEi<c+O3tqQBX+O98;N{U~&AmK3pUYz>PkQ&;HjnJd%t+Qga^XjJ|GcJcu%CZdFHe?7_SSRbDSS&H_xH=>p}J2kPnM_mX^^}h-LDPvAMv(-isv3Z>%09jd2CAOjAZSzH~!`J>$2s6Jk%+)AS+28UAk>~vi9Mzb=^4cUl;6W>NoSVlH~e*$L9Kd$L7(umM>41`^Vk(Q__7uik;o+<<a`&-&FUuYx8KEb{Waqr}zBZ_22o`K(6zXkn8@MJT|-goMd^l%<UP;`uF$O=FGp%GY{2CI?mXj`pNV3KizS^yWe#0eEIpkkG<ol&+(d!@$$^Y?|XT4#MIYw=h|NHTN3h$Q(XIk(*t>AewEj<lI5RI-I^>9ZJv}g_s6+@qZ{Y<FT45Yd4<jOd4<h0E4%OYk&-)u?Y9<m$JgZ1&wrVpERU>ze|EAwwx(i6vi?I2)-O+%hx2A7&#Q2J?RNEZ#*TAlYGA*jD|fj3k{1Hw)I4<jl8j{Sb$+5#_6KsEADip=Z63S7wyU?#j|9iVeA--}^VnRU^VnSHGohc-^^$HkRL4CRifCTzj!$yeq0O}pZLW2g&`);7{mJrJ?}ACU>z^+jPk4Fgy*s!M{AE$HJUpm?>u1}i!My!sH%^nMH+gM&viAP-ZIkQqO30bdgzfTtOmlx8INxpVKliikhizV-EZ6r13H>l{Q60~tw+B8CZLZH1ZLXhhk?Fq%^7K!udgBlEDm2484)rqKc!oVZJ6W#B%jSB#{QT^)<o%E*^h2)w#P(hm?EkA`-uY<rSeZZPC(HfkpC<R8f0|s6i_NvJ61GeIB;?dj!uY8lKiB=Go)dDrzdE0Gf5{W}i#%b!$P@NU+v|HMyIs4#n%n)=@$3Fp4F~5z_t)h9c9;Lh%OhQP1lyb3Kd%cs>++>92R|Q7uI;1wc04Mc{lvjQdz<^?Y4L%V>wSek9+Uh1muWQ9`#pV5rTv@SAOFsDFAo=aCpdnS`{U_X()*qfTh!0Z|G7Q;vXbQf`y-S4?~hFGzh8T@td~bx-sZOZ^KP&Igk0a3ncRP0W^#RB7W%DnAlLERT*q&7|NW!M{r8Xa>bvh@%a*$SJG=4QT*q&7|9z#+d2gtBcDE&g`ANu4|C-zWHTU0#{@E-ze&)yKIzKk|-=CUX=SOqhuI*oQ+rQ?ve}BKUewGe(&k0_6$+a)?va27H>w8I?>w8I?`|l<5jB|N`ZGrx6?!T|J?e%@7ZEyS6?XKMw?4MlUKiXX1KiXX1V@4ZK3T!tPa{b%fe@|+1|2?V6{r8*azV-6(?+08zKW=pMZ*zU`X>$L)r^)rbXRPb*!G30Mar0wxeIIIby)Ux4-nWFN|LyAP;%ly-j&A%m_wS!g?%zL~+<#B{P5uSB^H9spZu~aa`v;Tz*IASM*Sq|yy*x6R=c@}>xc*J9?^SKC?>7^2-fzanY;w;9d0rZ+yV~_{bDlrgT%SKAwC8<m<mAqz<F~nv-{w00gq-n5n-+D)XL(<Dd>1y@pOqxn=WI6jpRbx+pR>irl=SlS-*0t!-A4PflH}p<Yfev^^W50x{&VBPRlGcNOGaS)Hus+sn%sX*XmbB~Be}m{pEnHjuetxe)wb8?<TmFyZ6s2|ZTIiRf$`g1$8U2Tzs>#UoF6p`wr}pnZ*v{L&2{`X*XPxKuJiV}>7P8Ie{FC3*Ib`t7jN$6x-KjGmD;X8O|I_?Y_9JM5^|nP$8NsSogc%vE?nmNx4Aw)x4Aw)Pv}SAgMZpRu-){5bzJ?J+<)(2a{s-9$@RTM<gz}2?dts4T<6E;IzI`yKDX~O$;-3*?04Hec7+?i&GkLF$^G}>CfD~$k!e%iaqrIc>yz?s{5I$Pm(BJ4S3-Mz|5fpcz;?rvE4unIxxS~fxxS}M=!f@ov0I)BZnu`3ADip@M4RjTM4RjT#OP1E+~<ZqmoA#$jo;+{drzC|dry<=d-mAeL+-fOI^^1y&+Eo-bKcL|T;I<owAc6Vue}o-&vrL{oBQvPZLaT;P42&!&-gpAUH!ghbN~BV!y=0V{pj~cll$KvE4}LF;TQG?+S}Z3zxQn~kLEG$P4189{jN(q-}hp0JSO+wzhBbJ%QGi#3GT1S{r2PT^z!WP?z$NnJk7N?xvndSw3_Jp`KOO-ug@n<?mwS2x&M69<o<et^$)u3rY#PR-{k)IHQ%u)d3$ny{tN70=J^+I1nSM^T5kzC^=5Oew^*|*FW2?J{`q2aJzq@jpD(t(u4g#)PH_Cg^11QbT+er#>-lbSUFQ&;^1GLZ?${Ujyt27|UfEnfuWYWLSFufhdwFDVEbw`2bN#%vxqjXz^rN4*9f~XujGya8LeBNV=6bzIXs_$39=ddS?(O>5JDcnE&gA~}&gA~}ZfhAY58v7+c)w(F|9;7~*ZU=#>-|#K>Rz5+X-n{a$>je1lF9x1C7bK|3i8bAn*;YVHrM+Zo9q3I&HZ&0n!niF?HAt{Y_8uI5^`N<Vsiby5PPInVBYk8+va+|ZF9Zfwz+@5{c=4o*Uu&Ye%s{!@in=Bd`<4(Z)-mMnPB~xJfVMWZ~NDr`iWiHEO6ZY`(cy&_roUl?}u$a+z<Qt`<nvwX>(m?Vsl+*Vsov}$jml@dGo(dncV+AWpe-fl*#?$t2y(Q&_8)X|Kth%>-_8Y<$>c@c>A^Jb=UsQ4EH?2<l*Q?v1ECA+b`!Q%R?o8pOds7)`!?!*S#d<tba)8hxH+`x>LM7+?wqUT<XSea$OH&b6pRUkh2~p`|$n2{+S<}N8UaYOO}VPJDoI-Z2n<>vON3a(@Ark&xHP&&xH1@x3Rgd=Sdh3@7Zmx>vIyetMgy@sFz2|WV!yUJm==$<hpJrp*`z%Y_98evY$H^$irWra`S0&U9VzuT~CtG59@hCtv(2jXVxnBywT)Z|2Eh4FgEx9-of^-fA3&&T@RDc5A~nW59@!jKRn^(v9bKU%waeGHrI7QHrI7Q3H`7xD0I(<!G4ar=Zy*ZDOcw<&un=rY3{GTvboNu?Vt5UHrMq<3AxUv&2@d39VhS86Sm9xqJ*6FMcHlta-U1}4+qx&B;<UrvAKS)vAKS)3E!Wx(%a6-!+~{5nrnOgzLSu%ejv0Z-^yg;Ovo9h&2^kM*KwwID(%L3t-C(zx*E+hKiuf%f6*qder&GqBW$kkBcflH4dmgBlU`lf++Vk2+v~a=o3rjn^X%*mfpI3}tS_>;t}n8=&O>Ijd|<oj|GeP!Z*#p~*j(2U*<9CU*<9CU*<9BVCG^ARf5LWIXQjEnUq7A*j8k)+f1B(4+g#Tb`1##E-FR4EWOH3#WOJ=^&C_4&;d0iuq+eb!c)ZqZ*q1ENoc&=eS+4VMbA1nGbA1n$uwCXqp&!;!B(!H8m*(judb#}6i-GZLuIp`VuIp`VuIp|5?dtsVIbd`B9EffU2l~-^u(|&{%I2(ZvAM2GvANbsLe9J;^w0Y^&Her2bI<1b9@FMp4>s3zI5yY!o;KI_o(bb&eNICEtOrZz$6pT?4%B(hdaz)gvmPv%>vbgitE-ZpFWEb;_44r8g@Jmrxz?M_wcc#5^`?2K%7Uc*Yi|43-1e`zzYeW?-Qf6n&ueo%z6m+?Y;&z!n`=EJY?t@Q3H|dP+2&dgHrMkaVY|BS)aJS_)Q(^O&X?Sue=|Rt+xhWxGe7?P>+@2Zn|bq(ubDT0JZ9ef?V5Sh+|HZkcHaE$ntAhcGjIO*nYZva^@H=t{$|eV>aLq}HU#qQy*-21ck=YV7rXxN-5dOzd~2nb>wTvGeE#&`Zo9f(Lg)GB0;`hc**{-=&g<v;u5Q0r=VNnS=M%pAH!qKzak;K*O2~Cx)9rtGdFb(A|2Fs65&f^wT5r2c<_7xDoLAK4Up?jeVZB!L+7f~G+JEN3lEL=m;rcbbJd%%pCxLZA=|k(fyvOs&bK2`VpUC2df%dvSCst^pm;3A6SyvN^Ob+H;N3u^%_44%d{M{DoSi(gg4&?s&lk)F+dGrd7JL@h&-QEx6y51u){nXk(o#;9Zll$vThKyO~)yc0N-FWmlq{;nt7ypj)^31L-_n(WJ++RoW_T)f6`kc__{<?)cv%NgK=bXTJ{5=2cKpr_ZFOd7|B1SF@^rO!|qc<$`^7QfU?@9gl)bD3{c{I!Y{i*-Fapm)Y+<#6;uKoD$(<kip^3Z0t{z{+QM~cK;KfSiQ@#y>I(+30X{rAH691gbU{YWVLQ`i2C`+Hk`4;$Ka-peC(`MY)A2Zh>Q2(;JtP_dWN*5}Us&y&lGdU<S?$$uT>^4qorKWAPa;rbc4HTZe8c(IqKZ*K37FYo)J!&Z8ExPSY={iMzP_j*g$dU^I+D}()Czux5!t_Y6v*e=&k(I=AU`(_36ox?YH<7EA?|6aJqNH5RSznjqctTZv$Uf+woGRezB``ZNS(B}U0@b9O3dF0L3f%C}b{`-Yl4|;iQbell^+uT1-FV1v1?_vG-Yfn7k<=Im<2kWixykL9kQ*&*v^&FeC$jhT|KNdK@{5<+-@O-SX#LYwF<$?3a&%b##cpml74D|1R4rosQe*WvqK>vFFMxI&|=-)rzADXqv+h5*m>+@Ti>+?OE>+|h|es~@m+4`iHM@N(M{5jJ3>0qwgHMu@Fwz)nBNNCS<W1H)9<Am)p&d|>1U0z^E@cEC;_4$v<{pUX>_us!?*y!bv?b`#-qY`rc{u16A$o=nSHrLM$ll$L8P416p?pZGnFJAA?7oJN;u09vY^?9<*{l9-aa6Z@%&xdX9*N@5lzn3(*|M#Kfk<4|j-gtf+{q4IzuFqW)a-O@|T%Wtz+~2P^(>6<<zPRNlxsQwH**~>#Io}5(1M|5&5^??TeNA)i$6vo;a{qJwuL6O7^m~NO_4|V6e*gOSRwmc`E}QH37n|$%4x9V`j+2gudC>36(S?PA<J9X^-J(h7Ef%Wc<>7*?7v;HPZ1Ght-}_83Z%`x9UY`@%Tt6QYa-NIYT%XH@-n}NUU40H_bN_pv&Gmbq$^E}4O{?qXv(v-DI??>!hXQ%DQNv(+?uTveKZmioK6f&?|9nYv-LCDQJfVNhZU5x|U;X>fh3t0a`)s$szlzwS_uex<v<-zsmxM}%h7QQ}Pa;Yv|EVYcClQA?`2Y1!BGzkIzrp|8zlm7z*0fNlPh2gLa0|RQ+ycHKuHRCf|Bd&C#czQ{!hfYY3IB<Ag2mgxBH=$$orHhIuY<*}fknc<q&f-zoa!W8p0?M*<>3l=ZCLyYSiCe`0lo}Blj>OfAT0h9{1e;0jB%9bcb|y!oVX6*Z^8NE|1VEmsYv+qROg?jIu;3kf`s4355b4%Q~1*O?-q%xC=&iA)%n+{j=#ds<6pz);S2b8@CEo=B>X)R&Y$KaTmb(X{+ewUK*A;POW_jmO>woyZ^kc$Z-$HEMd4y_AtZb*)w%53xm^2v4hf${!v96W@8jp;_u&ul3-AZ<3H)351biy4)A$egxA3>j-496kM<o0YE_3=1KMP-igbU&Y-~!BJK_pxUzX`4bx6U=!t&wmWyaU_@Zi|FFBH`|F^}>51;cj>bxEtIRZx6TUxOPRto$+FD7rZ!L3@#2A#tXrP;V)C2%klma34ei~g};E0;{Sz@!tWsAcaiWh{C)Ts{2u-R{2qK9KLH<yPvWQGlkkVRYUo2G{1Fnqi2nfpKn-0)!vEs`!2iM_YD?-VgoMi=;Tm{BxF9uD0}0o~Tf=qXdUzYS4K-8`3D-|^pWEWU;%(D%KHG)=z&obpTo;7@#Ji{ETswsSO3kTDz3vFhwMed6;!XHj@+P$H2{(b8BjIL9xCh=1?ndqQz&pcQyFE}B`VhZ9SD(UZNH{Ov1@1zv=fw-ddEpc!{8_4VsrApO`7hwl;E$2;5&S58lv+Q6gbyR(IY{_r{9X8EcprWY-Usi;--GwV2k_(Y0r)liB>WouI{qR2I{XIy5&Q;x5DAw|bAA!N$oU}rFXu!_&V@2?Nw_Q$u8G%xYf$$!k#H@%9$X8)8m|xQIdC=pGb|Fm9RCRx375hT!Ux%pQjEDQTna9S*Mw^_rgHez@YQUi95t4bt3HLZQ=LmaWm8ul!`bkg_!0OBHS{JDejFX9rhbp>f1IO@;{CUZt8rZO;y*8st7)3^hG~w)Z-g(C-%W|1(@1zZz6yQ@UxKfKm%wZB&G1_Ig}7eEx8j@Ot?(B}_&mM}Ud1@hBjFN^SH@ie2@i>D8a@)g3?2!W!(~6q@w4zHsZPRknTO@D?*CjQ`~(tii-h~&OW;26ZTMRFHh2*J0z3#Fk!$WoAmIr}_!T6ag>Qwk;8XY)@G1CPBzzG+51(g_FY>c+d**ov+#VjEYu?8r;R*O7@C0}m621=!Z;5L!z6S|!#vg$<!<+DF@HCF`CM3KPF9$z|UxAl{uYil-m%v5fdDMp-`*}$C5&Q}G5x67X7VZe&goIln;jVZexGUTPzYXpI--!=`?}YEdN5FT%WAF*^82DcN75HBG44wsNQ8#Ch@Td5<@Tc(AsZPR8@Qbjx)J+p4+#MeecZYAmC%_Y^n_G}@kGS4QasDPg3>FC=#_xkg!bk8eut@m*l$=@=76~7Z`+wtlC$5ZCC*isHarijx=hDX>crL8JE4&B^zk+XuH&e&2;45LR<5$pgx%v^F35%y7;k@{B@N?9CUc3mL7yc#1N%%2b>i#k6{}K2xcq$TZig$!NQuj@fa3duAcgRWjO0t&lm2g$OD_j+>hWCK0!8PzZ;TrHY_+9Wda4mccTnny^-wW4<>muPQsm{;9XE+~(KjoaLf`scK;hXR#a1+jfn~?C$_$~0waC5u|tmi{>{54o4d>y_Y7716y>%w&zdsW6<53UN=$8UmfVode%=5TYiQJ=b!deWK{eux@-41SCndI$+$hc|_rQa9Hj;a@^dji{y7asN85KjOMH)%lP7{5AX|{3R0JhJ?4^tKsMIrTA)i5uS;!hBM)R@IT;x;L@o%<13AXN5yqdTr=Vth>wCt(PkhL?tshwbl_*<@7TvL;qTzjkno52Huyt0hJ-iZTVS1w4M=z-5+00%`{PStov;2#_*Nv`4hhf3GvV3rQ}{pdQ*gml=Q584k?`gCDEM-C6+Q!A1#gWj3x5d-PseA#GdNDuk?=$$+zSc!#s|U!IZnNi@C~>eryKZL_!|5(SS0*0*@y7Q@E$w{?}2yX8{iEbvz<tIVq9bKVfaXRB*%3a5>7|LJ@Ni<e~xQUB-{-NNAPxV1il#wcS6F`@!9Zfj{S5bJRb=cO?57HP?UPO94-o1M8a$FRq$FkhHr(nK4M7tKS=m#B>XB8ei45Oei5FGPlqSN!|{pmaJVPl3+@TGK*Ft&a2vcg+?(2JgM_cguYs?JtKm{x)%aQXKI&}`yoVaP51$BYJqho}>*8Zma;~AmdTkZ1g%5*=QD=Hx7S?OGa1FdC+><)f>%Oqw8wgj$BXES8)B6fxz4s8-`xD{DWS!u~a5H>5+zh@SpAX*;&%~t`XY#Y~uXsgRB%F_IEu0UYg~#9+wKxk2PesDd#&tiw3<=*BSO2(fk83f08@w1^ia!fKOP@>er{SgW6eRo<{wgf@%;LxKSK(JVH-tsPdLJ%)1fL8~=G@SGcwxQI7k(4(3HRhY(eDVta<B9TEcZvR!3}8J8g2kL#M{7aIA<E-)!>HkRk+msRjE1WgYbT~cNN=iK>Iw@T?1U|On4T@G9R9rs~%Ew)l4dNB_2)5sj+CTI*d}MQTlF%H-_aH$#<S(aorK`=T51?wD>ua=KLxod?hYzuEf(}k#HCe=lWgYYDl;`60U^H?^ePGz*3)8(p=4oSB5L|d;MuQfV%F_@Ai}9m?rPrL!l+9&gC3ff|hZ9tc>sTS8@H0gnvN7XOZwrNO%*z5`GR}jIV?j;>+-r@G|%>{CD^-xKyf>aB=(xcyOxocDUs2_*wV@ZO_6N;A|v(5`PIk3BQVj*W;UD-Ou$%_--UT5DE9g7sEOi{g7~PB-{oGKaMYhABUgB|AL={3#2-i`6_^f%Oc?scyU<gaRd^67#{~e3`ddhSR~vP33tN>!-F{<-H>o&T#iR$eip8QXTu`lkH}8KAHlovSK;084tzblo@28E36GC!G(Hr+8@`+4HxvoqfrM|t`@#J<ezzduE=afq-Ue;~--v`eAmM5F<M87g<7r6vKS;Q6s&hHsg*onJ;lgkQB)kR*ufRvZBRJkGknl!43X5-mH^RH(+KIn_Z-8Hb@5Q6=z3^T5Sokiu3*Hs(0yjg#t&s4IcsIBkwRIyBu8Y@z>%x_BsjbTVEIf&N+YRrgh9=?TVXdc0NVpCXz7`4B#D~H|sjZqw_-Z6v9lr&>h1#l)gs(!vRqz&Y3+k*25-x{?{|q?^Ur*Knz8<~-p9bFmPr?5KPk|rBrT!k}XW^gm3b05x57`<xgg=9XAH&zc&)~c9HSij0cQ?Kf-bh{UM!RzLFT5~U9WO+}Pr~9yQ=Ej~PH__c0N)Akr0#`9!tbRx3BQHk3*SrK3yXvgr8o&6#Jj*<I0uA9!mp<|2_Hyt60S|#R&Z^&4t^tiBj-aMyfRz|u7pc{SHkPS;``uzY`YTUsLk*GOr6!I=A^cS^>}MNgs2(u2UBwD=fPYx_8>L*Abs3`Uk{gz|L$+H9VGlLz5-r=XW%Q~40sK`5ncnYL&7g2;m?uqIeZ1Yf^DBe!o?V)jI|gN9whsX-;I}q?}p3ZvTtShSvY^Hlkgn&{aIM|c@7eug@jup;a+$K+zalDuYvo*1Mqe50C;#@<M8eHI(Qv(w;c)ZMZzcW&*2mBH%Rz<{2Y9adHtTBh1)W>gW$IC=v;F>8VQfVAA-lgLy_<#B)mSZ9r$)6ybgZ|UI#yqKL|g_aeW>MXX0hx)p&Wl3|t;Agy)9~!B0~Ya=f2L!VlxK;D_P%cx$*l+zJUdN5Y-)UT|l)JKh)W4&ROsfNzI~;KSh|@TgohGztmdgM@eC+u`lh&@Lo=8b1M_hCji-fj@z(r#cBY!oP>brG^?I;g0xdxFg&N9|Mn}hB_hP&Z+KmTl^qCG&Se5UHA|_DK+Q1Ap91-J~ijsA^cuSPF?DCM_8^!a?KK-&Cin0rtNlkHoO1{&qu=B@OAJyYIhr+32W_cL#ydS{Lx%}3jdqpB%DUJ8eUDUr{RU*H29|!C*c{m)cOo+{$Y3qJQ)c$!P~>_sr4pExFHhO`z7IWWX)4@?x}>U;GI))?z@Dq!n>#B+_MQ+$8S%`xvvwx8XuC9b5AH-6Cah5bKfX@Eq+f*&ON8F-ir!fnd*EOyo>We_%!E$@F$!HS0dq>NVp~52yR5(w?x7byb~OOo8p~eJqMcN2Vjx#wfH_*Bpk-;z;zgVm@(Ic!*DIUCESuR)xw*?P1!~*YV4<!oca`g0G|QRpq?H;!u9Yba1&~%9uod3<kXP5dN;-0U&=Wu>z!n+ldK0%iT`{_id)|#{y?f@@#XMy@!ww%*J32x8}AGEz`Nmn;cjq$d?4H(zB8_2_z-*`JOrMBglFP?;l7MxCK6tSKL@XZKZ@&n{44x9_$zoFz8GEyKZ}Gr<Go?s|ISGGW+Yq|30K9t!Byevcz?J$d@X(_d@X!kuDQDo2{%E)BarZDd<Z-mz8{|f-w!{5grCG`!ZVrECz0@*_($-Y@Ta-v{Zl0T8U6$O8T>gC{sswO7O%~};$AWCSEM+<488&`g-iQV{487&{~rFH<1H)_E`+axi>5f=z|WFzK*E{$vv4Nd0q+cVfZO6X!)@X6cv-kSd>InH6bV<vtHKrGN_cg+5_}DQEqo1J7rzd!3tx{nfv<;~;v?Xu@I&}$cr-Qi5E7n-KLJmJw<6&^_>=IH)X*Lz{5Jk6{5Jd!{u%rkHS`V=emAc1_yqiOcmg~T{|252Pr{|PCh@cIWV|9Q5}txfy-q>G_r!HCo|fYLFIZgaI1LG>BH;>nDYz81TLCWwYwcD*MRWBd{J)T6@&6#<XK-or48DO}JQIEfehLY<!aKm?ZQ)jMb0l00FAs}f1{Z^iAmJ1woQ7W-^8Z}G<2-mpI1ii`uLS3X^WoRP`QZF`T{u5n0KXnC0AGSPg)e~%BH>N=L$LTXSbQtI34R#~AHes(;%~zT;MeeX;Md?R{9Rbjfh>F+oCR;k$HLp;&3Hk$AY<K(zYK4Ncj5=&1B_`Wo&{&I4PmJ(sVA*T;g)zSSiCvh5-x-ngT;%$g<$<pSn8->T(ja@7}siiE<OvM3qOj4ha%xYct7}dygS|x?uqxo`@wzSCHO*k3A{Gf_|_uf^KpF{*N<_X!Oz3zX>$e%AHwIthv3=xqws9_5hVNoJ`{cc9)pC_@j<Z8MLH60fP`x!;Tm{%Sm&z-621xvmqWs>@jh^CxC_1n?gB5v*TT!-_4s*sJzO}&`H!$jxNO`jr8qBxgfH^{q|HTs?@Rb1`~?#JFA_e6pMlSCoQ@&kz4&Z+FT4$Z1l|Tm@dw~2JQ5!RkA#Qg>2Ny7Y&a6WA+APvJ-h+jfa6*Z3D-ozmGK&I4UTJNBzz?jE{T_eOTwj*a0MjX4sQ*&=GeDG!X1(D3Va#7jAOq732#Kg#ZsJ09TY>tmGQE$)<<PjNiSaTzab~#FcL0}mw`*e7edaZhAtrCv-lVAS@<aaU-&2-L&C2k;WzMOu=rm14R|-c4c-mEh)3ZU;b!<qcqBE{48H-^dJ-Os7sMNda;~AmdTkXhfY*b?Yld>J%ffo?7S4xPhQ+T8<y`lL_1-`@4_*=$FCEIcuMpOIkJ34Z*W;pi1-K|&9B&5~hg;ws;TG_X_zL(&_-TA2{4~4>m%3cU&%%G;mEp<^R#+tbTgXW`e_X$ZoEM1egE$`#xpg$+@53VDe7LmD$M58a^Rumd_`kHz2mgwM|H0*a5Wa_O3LfUZI?TDD_tm9y-Fuhj{=78jjj;IHP|kh3u-@AXPr#4D;;~T9_X6SZNO&9)-hsak?|^sVZ@}WaVeuE?UGNsX8La2S7JM8$j%^61x+x76#*4y#a4Z+$^FlfGFfUil%%i5nBcYrc6V^HuE{+$53$v}_p`7nC_r-N0u9I=~Np)+S#P3AHx8l;~R{Rt!67CE4&Goy&=}34067Gk~@Akt#gr!zxZPN#Mf4D!t_W|vs{Rc?+y^veCB<q**rZ|_H&Wj3ge%u<@V{y$#!gG-DbR;|&2@k+;g>S>V;<v)L;Jxr$;a+eCJ|E72*C64Q_#F5&eh{AnAA}#rr^AoK4<q5J_+WS{JPHZlfe(OnKkq=o^^tHbBwP*e3hP`{L&8;%a2X_g6W$BH3GRevz@6Zw_!@XA{5%pqhp&Wn9?v1+@9=E+JNR29{0S0%3ke^=Ps67<9!HSyEBNE^EAUJB!|+S+gZNbVLHKTb6nr;)7k&qP2gl|vB-}WzhIk#kK3t#UR|g4SjfBH^HMknbFN}n*K*A;PGH?mF6cWB13Ae#-g2g+*ZQ%Aucsafl7JnXI4!?kei=;RS7sSuO;@`m{;Y;yvVet|vjzz-d<GLI#j+cOo!(a1z^7~&S;g9i8;E&<M_*?K{_*Epl4+-y&t6RsE)KY0V|5(tnht@Pd*)9J0+|7N~>wmJgHGTyhGJfK4{`DaHo56o(DEDucj(@T9|Iwjt9rMaPSNsB&>Rr%U$r%{>KYZ5mZ2'

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
