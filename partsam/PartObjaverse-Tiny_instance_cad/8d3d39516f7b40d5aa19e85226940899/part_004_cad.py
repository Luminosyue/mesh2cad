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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_004.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_004.stl', 'source_sha256': '15f0e730e50aa967d4cc732dfd34b6b601a84d132b81b99f48bfb996511e3cb6', 'input_faces': 960, 'input_vertices': 511, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-31.700786590576172, -34.863555908203125, -20.57037925720215], [-11.450677871704102, -7.51197624206543, -1.4442462921142578]]}
GEOMETRY_BASE85 = 'c$}r22Xswo`0jV~-bRU<gGhqtE&9=e5z#v*T11IVL>q1Eb+pmz(HUh#XOx3M2u4P4;}{0Rh(0?1yzleuaolz9T6f)R*0Y}9d9(BFuYceE_Q`}cPM#vWfqw;!H&f@n>Q&k>L>Y|i#-JY2F%jK*3@8~HHPp+<qH+0W`Hvy3nuNCVG6osL{JZxU&@I}(ip{@T&mjLmn}5&#(J|3skzM*nckdzb`eA(s^hk;i=oJ>#Bk6NMg)(IVZRLsv+D6#^AOEFG%7Uxs_L?s78t<x$8)?h?io44-(763gt{VFDqo)GIZ814DZe}Q=ar^ZOJ{oV=ML(N;THyMDcLLRWdm-MfFFYu1F7-h(^?r_4(HgfU)G4j^?--?Vb8UyJ8o%$0_{`k6zQGXOH#~nC&F8QTxc=N6jT=p4GwbIT&#USES5MS*jHoG@^z-v48n-!yYTQ2Jlcw(&x<cc|)-dG1&Q+w}Hd5pEm<f8ltFcSt#@?&?+3YYL_wBbXxq97G8h5lli2J4=oJ_CFxC`Z3d_eQ-s<N}JUN`$kjXRHTs-)MS&xQOPuZH^_X^Nlcyr$RNO8Fta{~4}#w@0}?`654y9wL6_v8H4Hu(yi-{>HtUZ~NWDh1JvTKzvHRAoY5i_2-U?gEa20|2z7{ckPO5x^<&8ZXbMJ<F*4AwVxPc`yig?9{Nw~t{)D`?>!6GxcPbp>fue1HxhRo?)g<Zj*(#{^t#_18n;!>q2)9kowUE1y&7xWWj}=bZXc%Qat*47>pR@ixO-hwo8HH_I?8o72<gmfRzTw`$|0TLwJ6ubP}E0Aag7@jV}d-}%Q+__@>#JT`unTQsQ>e65bysF;uU9j>*tKeDr>qyR}k+zD67VEY|^-~y`rY?`uSH)$3A-{;z3uC&uoKqyqKq^Xx#C%G{#F8|8ja=i7<`3KjziXW(iwPmP6yt$X0q^<JP=X>MgQp-2UUDAkX@DfBR8CJ2H*dbX=!XXnneGT|oYpKSus*Z^XDuJd6IZDWzTGosX69jN9)0hWflWQtQ)o{};rw%|?7&O_Xo<KExx_X*!N?j%dGf99n^Rct(x8JJ%?p>CbQ?Uc!y?Unrl+GwwKj6ZP=(dCjMJW-;Q!3SvBde*yjQ^<<6P-(=DBZRro7pOlV9xdO7GTn8g_YrK97)K}H!n3uA4#{G9T{i+^}SFN(??|Icj`W0THzZagb*W06NY22(-w!EgZXfpcS^t7nw+cVK#f7ec<pKtuG<JLZ`p!Ng%;DtI)ZF$dX+?{`eremx-t^L!La|Xuw%~Z(0?;W()u4#y$OGN$0?ZSLjWHRC<+M<4HRQRm*^W%8Lo99HkjIC5s@3&%<#%&+AVw_eSRMs<Y&lQMqy)y4>Nyq$dq{dxU|JM9FXP4FS>--^F<Ic28H2?0-GtvJ$eOC$Xl?VC1T&9@*zF#Ng$L|2<(U|yhU&VJ;LjU{seSS@+M_Y}X8474R&aqpIc*b1|a-x0agri;h)x`BF3!*>#7FbZ@sfr=}MJDQ}>ukN=eK7#>vxU&^X<Fpb>+_{Yx$<};KBB@mn(omj74>tELKW1bSH9KyiNB<AYhE=5ze%g^eOlwLyR%X6cY@LWp*xUHx{>IQTWV=NJ9^GVeEcKS|CB^c->5rX<Mx(*r8J)7LJloouLzAhFReql{HlBDed=}9xMNKLUEdt%-)ecCWm@6-Y-KPWE9NWX8Mo@q^;07H^T<ZHexhCD_VpV|ddAJX$xuHJHlf{fRY3k@>*D$ktI+PPN+bV?$+REaQk>9oIGg6zxUF_D?%TlTr|~u^kWSUcNdM(BZAbICfpX2ef_=iB6XiVPwswDD95;wYe{en4c5)_ff^=q<&8ye#yQXooOK*&;{SPwg{U={VyUy%`_~^CpqL(%9I=&S1I{S~UQi8^9p|#P^kLS*=_Zxd$<Bqw7c^}O4?w~cukJYbIY)P;2or^W@KGqET6wYt<#IZ;x^BLsBKSbNb_Nf`-_r~e<?iYbN{v1o2BA-*+p<kzOjPZ575%SR~Kl1--wV~-uu8sTdN{@b9`fsd{C#q}QzHJNYBjBK}FZMzu5dSqC?PaaAR=jCj)WiEiSQic#L%ii%te=~<qrHCfMZKK~!u4s~dcE^z0o-rJAjH$>(thH4<c)OhpF{pP)c5j?JA%K(JotMv?9&!z!S!t$`039#MCyF&XqgQ4A29^^AMIUSuM2sC`a3!T@$@tG_v}}1Y21FYF6w918`Nj6>zMZobVm7)R>6L+`#FufUW`QlZ<C>re)c(n>+_FAyL)HLr|}Z|alLnDe{F|fQ|r9y`e_^1gT4pQj!$N3dpZ5NPAnRV`U!cf{muLa^RF?xlcr;~U#s({%k?Aj|NbA$_ZcQ(pA$J%<IeDX=x@Vc=z3wFG78t94naQim^v=3xLI}q=Bpm7kj}Wih}Y#lYj^|gKQ^y!DDUZi&@RE%v_CtFH$!<tn_<6}`v%tEIaRQJJiz|l)w~1pH#85@$+R5p!hOhp@r5(6uAOY6`7!*np&oKYA^&UBYWj`~X%RoNN9)(IGcWdI15zXZ`!->{*gQ)6o8!;qi0|2k^)Tid%25jQsH<!f^sl%q_`LKLeAQ>{YZ4EY^^DtZ`l8+{xzcGlH$Fi;wk!4vCEnn9q$2i1uA8SY?>f4pT=lM@p2ChHoya~qZ@3DbM>^TJp+9VX<ENjWC*XQx4d(f{S=!HSVP`S^0=H>@cHZ(qzc)@JUglffw;5H(>iXi``4i$5_o6-*{h|HVp3I5)Z^}lj%a{6TKX=*}<G!iw=pXK5@KN(H|J~V&d|tYu=^KfdNA2H@L;txuMaQq}>UhML&Bl73JqPxm-3Ot5I{l7$VyR8%0sE@&aQ)tfsQ<HN^?I{*f8>8}ab1V3_O)e;L_Tv)K)JSe(C11=Y#&^o>JrwG3Ev?9OR-OMZQh7}J0S)7N2At=Zzzay>K%smozx8RsFheJi{kmr7SI&;U0EFSScUo-^!k*+xW0dDJO>2b#(Z+K1g`(3oj!j#OPUxzQ;MMeKb^z42wPFcGj2R{p<HA8U|+Yu2jv=c9{s7n?)SQ{2+EIkiClqkbha=)ug#6?tG>~CGdBF35x?)v`v0tP_skewmz?9W;l54&!aR9zLn^)gMJ9~D+}DxM_&-qp38@iZauDt7N`-ZE(F^P&p2uOo-=-<bwf-^2Q}=$@cNdP)>+R835wDm5<2Pq{jPu(Uk<RxwQLa9%bY8TZD8IA!4D3hVy~Oi{PXgAfZl$&U&8V`dw`)gGU!zXy_%UatM?0pB#r1RVW1df#tn;lAvl;mri+!=Z_;%edncLQ*9~~}@axF{zDsKM}gmv4iBJ$^2iFB&|iFULd(C0z>%oWH_<QVjyDWPbW>I;z{du!}>ZOwJPbA?YtJoj2WFShVP``sOZIOjb_P!Y_BExt#&`|ZYkBe!SK__-*~XaAu7gYRM8`J*?|Ih_vY6A48yFK>xJxvI^;xxv$|$vxwy+YkBA+7I(;{+_sg)<x|5+$(jzZ7k}D`}RAi`7<(SNul|@(gx{NpNZ#yHjQ*&XB5FY;F=VSd9ub~joW{1g!ql^n18Y!#(b5mKI+q}fPQu?d5rb*yV{6zzBRKJ!+v#CHN<~7iu0-zv$0-ws(}1k`=x9lIu96COQJoWy+Xal?}2Y9hIHb+^?AoSkFqrkKz#Uctsh&lP~_X&A0Av1`?&oxah~&_2(C}~g!yO3V~p25zU=>fwOnS}X!OtH1&~h3B52>d*Y)|-nJqigsagd41ozL_x0g(V{4aio@l|*^>L-I2=BF1av3_lQp#9FZ7wec~<iF_uj=p}Laq~k_wAbaI^m=E&E9{>F=U|@vHyYz&%_EHa^4XBiw33>RbNgTDFVh-foR;jA!!vH}|4rW@U8mg5?;w45np*mMLsRN`k?pw~>F4?#{gCH}M*qv$U&MWf{c6OdGM;gJt)du5M;+)7H7?=j>?bz=qS#Mny2yPG@4J2p&P9WcBAvqXur4Rsu`Z`Mf;jid#-@CjhyU7#bX+#A7o+uP-KRNQ?nXYBkHftCIaK#u?iV|d&d^fW7Z*5(`8fgSf7X0xra7I}Gj2St&U3s!Q)xO;8&RKAkKp<B=d=1;Y|F9%`;@u~T3&YnUyPfd*CL%3@mM#b*JyjW-!I1X!xy9f_~g)YMc0to$j?tFurH7Qp!HyQqhFi#mZE-6+(5s2g?2EP#o%0bT_x;W&W}bqyMoYOSGs6A?yMt_pJOM{UWG94xXhu5|M430Qt?+QJ>&MuwUN%mHQIlSjp4ZdZ8YLB^Ra%N=z#nr%YycOeM85EQL!!h)%@w02gU~LJZ8Vx3h~?>wEX7A7TRy!t6So})_%KJ+w`7sS417;-}i>rry0`%?GiH={h#|N#~rMb=Bav!pKFhHdDal|=s|cs&JeBR+WcGx<qF-0^T;wz^ryT*?6-!N(`?@i^X!!J7}rsSw7m9q5g149%OU^AM&kS<c|WvQQS85rp*3*su;eAK8|07tb3gB%|F)QC+&*(M%KK;m*4rFKkWOV^y{{QL80WDs@P5E{s1NqZZ4&id$bAIo8D{e$*iVLk)P0?6e_EvTY%0<(nhEn^$J8j-s&;z4qZ#&F&f=*Mue1vLmR!fQ-JF$;uhOv%%z}MI+Ru1CKmP{f>;7{+KXl}Ji}U^m4fVXjy?a8SXWXb2r1^F&s;~8JpYW=*XS=wL#eWqySI@(FuxpyOue%lYFSZ5P=Q|VTWBt#159jE`dSYL3xGd(6k5@{2){l8&DB8E`1>~~;_NQi_j_3~!&muo7!|~qaW`#h{xNG`a%p0p;V;yM|hxZa8_mEHXI_5+F6PSla@5g+#WtFav=J8*VKF=*}SFhlCxyKQlTies)=e_soyl13zAssJ2^oO)L^?A;Uo9}O8{yf@M_e*B8orouP#QE5$@tRLt!5v8FQD(enNWBgH<}A*|&3lm;k8zoFU2tbuhk7oB^Be1&(6(tc@)vv__dQ<M|EqY{WPa-0Kf8vlLcJAEt#Rk<V3c$6Qq<e77}UekVC>)CEM$HLqW^T6f_9%jAMyS{sE7TR3V6o<%TN3u?dN9rJY3)P1;+dI-KghOa}ck-3;p)_1MD9PPx?CjJsog<US<sP`Aa5@uf90Xv*PZS-OztR*Wh!$f$*ODu+OyB!8k3}AHVl@3;NaL<anRB5a(`YoeX%dGrFbLgHbsG^_Fiv-v87H!hUsdceG=cbeM;ym&xuKH&={DKEJ=J`&j!u2lCV90QT*H6Lq{eMm5Iu0XNZJiRj<9PIVFI`Gz~^P;Fnwhg!(bjeY1>^?pS@uT^1v9zePJx7B*K4-LY7^DMyrjpyN}cSY1^*e=XJLoVs{Mw>E7zh_yD)19BSKf8~W!1ddraUW}bo*Rht7gW=FaI|j};2F0cKZSPb{Xyp?S8cp^wQu*w^X%Uj^Lxgver}zgTXExQCw(96tojJ^-e@1he;bJRpIL*k{&x08enyPvxxv6Jo^fa0d^mS{6sGH)?Ng4g>dp8oMB~Q8G{|T5<v6D-v<35J+mxuELl-eWXMd{o=?K94E_;n8S`RLtx;~z9<IX$%?3y+V?-wRN#d&&gX1q_CkXYO^ZjLcgu9XF_Zl8FB^T^@B7#H@ccwbQHI_Bv+V{rY$JD7);Cm{X5uVTGhzPgBK+?*4KeM6Vjx(_i%oI?ER9y}ihKGo*~d(eKwr>;hOg>S|_JYg;F+btXV|DK_`A26d<<Gz31z`77J9r+1aige!R#(SUQRk0sSJ455{i61atnq1TUp?QBI_PNvY<2`JeI_S^cN1`5@=hSv|zIl)SoP0R;M>k)izCT{Vd2F@r$Y;b-ykAXLNXNICyA!VOunPB$+JSxYycW3cy^mNg9G5ZwTns@ve%)|R%JV?ux2nj`MIYp6$O*L9rt(O?bPKH?+s2Xjy|@6RA2tj9^U}XrJ>&M?_#TAyUeYY=jre?DyiX~+sGw)uIQbC$cL(;zuCQ+qpW&m|**3h=e&zZjE#h02p#O7yvG00<=bm)0zuFg>tsZOK)ps=B+jhT?ee#?KSkK>A!uJRE+(tjjdJEUbgrPr-jn)2cZ+HUlpJui~zisTR&&943dvSfa_m~fTQu(R7e$u$J9^NasRzA~nL3@|=NN06s)O(x{y!r~HGjNBN%UVb5H<sajk!>2@?}u(if6KE7<^8k`^%&a|=Yf@`Bb{>%aSmB;iJtG711BRL_H)zkTu#rpEAZ1-`ybc#aT<5T&Op80tBQHG#Tbp-E>6O}Wy9-io^k8Fr~O8B0nfN|Usas<E&4~_FT0BMLj4aZiFBTu*q26h!+qoSqn~iSGrEN$ojcu;pS$yLuCk&r@*mX`_1H9n&U<Eo+Nhsp4RF4Y*sq9Z+!2a>xAWN`jI$3_kpF#0@O>7pYp&MC&|YuR&&|1`ajr6;z*qgmzIdyS3wySFNauY3o{u<hn`bg2Zoi3h9`3tbebXbI3mveZ*y@k@<-|LjYm9rO?P#5En0FHKeUO2l@%^LPZuI9u5AohNJ}c&J&gbT!<A_g=)VMP?9qNDfK8-sbwXg1Zy-{`#=F5&b(Ekrd`l*L((zx?sd-R|4$?^WB_!?Y4JO##Gj1Sr?ekJnRF#+Y}{>n_d4A)OChVje&hW-9L#Ahu;J2u~n?+;9vgZvL&hj!1C66<fR35Z+o_q&xX<QcagIFI{U`>xw#QQpVintylHT+HX@Xp}2sSFMNt)|Zcias80AsE6|fy*=ahl9>vlJlG$Yx%(oW!;A3Tb8$Vco7a`^<BMQ_W6g)#TBCmA52Bw~^JlY`h<^^pc{SG^*TWi!HyMZWCM3gnPhAfEWa?au7i-^g#25Lm>%hDnaUK0FtPt|GClT!(RZ!18>^1WupI0uTo@-P=KhK{X>F3Okezood=B3JMP~Pd)G4HiKjDA?|mF_FuyKkYt{@YsX-`<qpd&q1<KdgVpPk-L$Ciblrzrp_8dY)}~3F!=Qqn~hHw&LdLv#5XWlg$)yNGHuSy#M09#kJ}f&OP_k!v6V><=Fo$-G+1`renV4KE$}O8F4=E{5RgMc>b4|M+V^e-?euw(r=ds@6$Q|oAZ|=&iD9^PCi)oXHDZdG0r>9O`9-J_aCouTPyTWW57g=-(rK2PGg&<Z_Urf_?}27t}f0gSFh7?ZTIbtdfS-??cOlN-!txde+cc=2=5imqhUzDMmOzm*7|NQ&<yF{ZGil=c!&7n2FU070a*9D4o7;~iX;6ZY0!VzKh01-<mYK;oFBC<j{2Wokk21J=vN=x74(c7cg|q{&w0s;JG*bd_Zhi<xzc;%`kdSGeY?7~QmF@I!1qKd4@UiG4nn((d5?WW-i{b|T;Gku|Dqgs&+2u?A#c1#TlNI|@eAj%ujYLCUwl&+<cIqKqsC*LyM#Bxb3{Z-%(pwvA<pMPBe);VPeOjd`Q__t=>OKdG;J65(L8UoXX=^9Gj4sK#CUN)_j|5Wu}GiievV5oF}{2MjPkCkivDS>QxjGp{k81BFB|Iq*`9n6(rNTP_VXO?#_ici=k5yBYgL}#9h{2%um2wP!+Fy9I05O@a3Y`mKcfCC^w+qfnu+(PoCjR}+Ti-JZ?SJ=|2L*I#(l$A<2j|}3iSV?4N(u-f-o+)uG!=2BR?0aVf=EPGS=2a``&(w{Qr0h&pAiRAztqj_E#J)E~6CURdOKC`O{vr81mB=?+0CZvf=xmKfFMG?<Pl_{n<?S5c63L&g)+F@Z7cGKH~hI<bUHU#bxyOyNgh7eE(vux`6aArTw};j6Q>TBJ>B$-+Uf4ZShF|Vs))wN7G)Iuc{r=xU<eltk>Cxpx)+h;q%`i+?VJ4Mw(H0Pr3aa^2vT{UpE~2Ec6=BLG0)DDlL&8V+YQayq04<FJBA!>4JTe_5DEC^wNkQFNb~B{*G9mJ{w3sSxM~6%a76bR`%hqQQwz$<N2g(XY7~qzQX=GXrIRIsX{Ry?R$>>)7yg@x7BDJ;2Ad-?#H=g{>s<~UcQHPmj8zM<lhT>#?2aMkbW%Av+V2lBL0mF<!TtG{oib`8}ZmQST7zd(E7CdEX93KOoxYtr_%fk7>dsg8sqx5YcRjf=!g6S;Q7z>vMb87CIr_n7=`_obCT{eje7k4!GQ6omw!6p`<zz_BR(k>*Po2g@7I|>=0N&;t6<+SHY>jelm+p7E<A6oxQ%izJ%{VcPDcCAaH8IP$Dm$k+(AD!GoyZ9wZwJFeQ<xC&)c_L$2iNn756Eax`b!k2;GS5&)v~|krCG&*LSXl{x!!B^UUDVxW1+n<6~cD)O&me#5cvEzgzRep?iLs&b3$gK10vxzOK-({z_p-!PdFV5=luUDXo#+=o#kmCkhgjf0qC6|3o38{QuRTC{(Uk`v3P&6h<WFp-+-lQ^GST;U6jC0hDm_Bn2d?N|MUaYm#g7=jABj+VnnT@n+=O<lOY4<V<uMy(rm64xu+AhmiYG!prC*$Rk+JWt8x5l<+%B_yi>!OP@)e$$E*Ugtt?|M=9a8l<+wE0P+CV%Q$*CS$s5Ed<j|nAbA|wO8=n8eTDy^gg?=5lf~0{fj^ObDB<dqa0N;@H~k+2EPjkE68@JGzC{0-EWUz#iF||-K0paCri4e*$B@N)l1GxeQ^HLs;ii;uOL|{&U)FC+dN?_p?a`86lPq3^+>&giU&Z6T!j&lD!t?-g8hS>009m{oIV0JdUYjhQn{15}Zz>aiFAY5{Jrh~nMovr4MhTapgsag*$eoikBuVY)-;vvq+fc&&DdEYK@D%zG@)YtsN_aheB3XPDc|G}8O87qAMZQmdMG5~-3Gb$a*U?vz*O4bs!V&a|<cZ8*1idp^{@&{wL;f@ko`al$oR#iN76m2AFG)UzEFFeXf)XxC_am1iSEPjN(}T$3UC8yx-6-L)bdx-mJc|<kff8Or3D2f?A<riFri2^PgUCTFXG6L#xgohOJqNiixibA5a%FN^O1Ky$oP`ojMNdagMNUZxr>2C{(=(7WFt6z;;mmYDa%OURdO>nQwx#vEJ|6e-@yLU4K6(jqK5}tNxH=_VgA%SqFG;RNZcML87OzhhZ$%c5Ad7b<i?<^;CfB03@witTkNmXp$fs~?N;s0<pDaF^97&!;32&f;f1-pp(Wj6%k$2GNk;T`OcaYCg!Y}B*lEv?nUyw6+!C#R@!a2Pl;euX}u$LDk{3n0!ce40y@}K16l<+o6cqJt~gT9VDgB(SlK%T(%i=ww8w_<xo(Yukw$C9JSGw8EC?lsFJKeIgYDZHE#UP}LgEWU=kl)Q@)en<(Qr-b*@XOs7nr_+0r#T$~RlY7wXlB1K_Vp)<7QNn*w!ikjdNlLgqC7hoUeqg|($#Dj}89z(B8Gn9=+>E@R5`IDdi~NH8hMq`%L%u;jNj}N^-JpbrQ^I*E;lB+?cq2VOIY0BgkrEzH3C9>;$|)R1-%O7q$FUAJ^RsXfN_YW%KY0Q98T|$M1<U-55`IU&L4HTRLkZ8I4<`?2`Df7W<dyVJbUWEdQraY4HsCi6u=q9dW%30|_%8hkS^OjUF8L)ToZ1T#&g2CNf8zxSf2M>J=}*W{c)vtS_$noQoqm&iljXV2&%!Av;o6jNFeO}-Zjf`(Zy0ccY_QI5P{R8t;a}(%$QM{Izfi(wDB(Nwm*khMvpf7O{KkNUvr)o%C}CfECUPd$uP-HBoDwcZ38$xoU$bqbJzle263MU0w<zIL^sD5ntoKut@JUMeF<si@F}*ffBwU!P&A!@+JcJS+K@TPev%N-8!u=@W<{s@Tygf-Zk~E$YPDTkYG9ck|1|*y^Ns&p)m89<Ul;o8B-R_idJbgPkp8O|$Jo!)ZO-gtpCES@3PB7rf$jO-B1m<}tIf2~Ez#dY(E`2C@D1XP=e+u`Ygs0Qbk;SE))*2+dpPtL>%laj3t#QH+>7~e}*bc(Y*)GC4IL@rKQrKEUg_qLzk@s<2S!=GawMGkXqn{z4;kdHabYW{xBK#-)4Ov{qo3)1#w)Q;2)?P@sBqdyqo`;-=<FFhh97G9MqZcO^=lHBf3D=^8tuqQ?>+C{U&NIZ*lf`A+T4x=?*4c>gQTi?NEsk63EJfHl+YyeXpCq5;xV6rLgsrn9;dgWy&+q7+$l`XgcwVnBXHde{*_7}yx~%KM;v0=GXIaA5*_Ut#eLPt_#`tnpCR~jYE@OOI?}ZyAsX&ri(EZ8&{CNv{7+HKXxdnMXCH$T)`-AuN1!R%%ca-oG`ZMwq@_YI_@_X_>^gCqn8Dwi8ApD#jOJ7M|$##jQ4<U<>AjgvTP{Ld2{mA_|uD4La^C{tx^ipK;Tx9V`@)i1ddL&uAJ6SxQ{4f0_J)SK7Ct3U^`6c-gCA^ltk-U~%iQbtkE^})oeiq(iz<ZIm(7V!mk*&G7E4?gPycoGFxdSB}N-shd&r1#^*P(=~(zBDZvmaNbHy{tBkD@mqH();=MW0We&;B}!623?YH)fxfe%zQ6eoTKte!{-{m=gX-|A%b#*N>F&D|#$BmVNOReGB;&`6(rQmp-37pMC4DN1wY(3BRVFCtLmOH6{Ev{U!M&`_td_wdB9a^C)3IdL^>B^c6p^FMUWjD}V0fXNf!c^RDEs>?=-sDA`G#N(m3A*CE$o+Yk5X6T+wIhv);z1KIY6=oiTs+5U(4S-33wz+-Y*@<U4a6a6FkBirv2CH#T@l>C(K^nnt7OMgv%OTI_{n|zNvjy{h(kM%sx>r1_lqlBLsaH-R0tlO#NsjQ=C9(DJO60YL~KSUOnx~RiCc}T89en9_3{={-VpoH(!-;&?5Z1*YQ9`teKaV$p<dL72=FkRvDNpbnVh&7@Ilf^rd8<9Iv!rxQEgDK%blyG}WxE?*29L)RGql8OQ!Z|77T$FHrdU<jodIfrUa(U*v0ww${CG4PgB6nhW9F*`dN_YV!ypR%}Lmx~Y%<|8ngy&Mi(<tF+O1Le(J-I#Wr7b0Fr-TFPrO2gNUxD;I<Uq2Vxu&Eir{^K(;qN4;guUpw$X;ZFp5OTLPdJ%JdnBWTQy6$hBVL$Zh+K$mQ<xIA-X#e)p?^#MmThCbdlI(Zg$a+O4<ip_n_2J9gspdN!qz)D;k}e_JbfWqd=5FDyps|>OrJ{@pGH1R-bx8uXTQSMnXqsqJ(?`u*7$OUENq=Q3s<Mx$>M>=mosYN;`DsvYe@}xD@oTWVK*gwoBjv+GW{I=5Ar$kUP|}~{TBHM`6wlPjDC%LjC`DaoxGgBn|__Vn|zuQ{+;e7|4vSz-zF!JfAuKauaxj+`Z@Au@{jbr<R8hC=tszt$W!S@$wyhvsg&?sN_a8-IN2({ut}duUrt`mx|m4`|3nG@LO)GD&3gHT5<W}`AEYOc6Id??DdDY@@GSaf@@Ce{EJ`?r67Ef(M4rUD=uHXtp@av}=aT2L`~y7dMYttBjBb)m)=L;AJd6@vNdJla6YFImCA@|b-atQ0KFoUAKnbs-gcs4blDD#67E!_jDdAT17;+5jr4=RIh!PH=_aXOT`9nPFMYsgLJiR5kCF`X;C0vgZ?n)m<9>#j<N(qmlgs0Qjkk_zYrc=VRDd8XJ>&WX^FF#PiqbT9F^nv7ote3Wwa79YED7_K65zAlHqh5rQ)6>vPkV~*$(on*gDd9r&dgOYnmqL_q14_6jeGGXF>!l|pJctq=N}o-h&3YM12@j@(yU|CHN3mYIQNmRy;q3H^<cchRc8_`yer~|s^yK8^tQTRC@LvWb{D_{JoSF3^EE4`;K*BcuyaBlZ>%~S1*QbQr&<BwRv0mCx!W}8$4)np~!K{}KlyFl@IDlS-T!r-!;88EaKPTx#l6KNBk+;#$&@YiM(67=jk*|_}qn{w3qVJ-gAfMp9cTvJlN_Z)KC)vu=Qc8FgC47K>hHT~a0402u623^kO1{ecUG&Jea2$Of{S^5W^SzG}UO@>@q&vw@=6fO~Jem@oLSIE*#e7epgx6ETF8W#WS?15>k#FHm^d0m#avbx$gA!g%2~VJ}Ag^G)Cs4xSl(2(7nmn5Mc2L57DdB1K_2l);-!zYW3rErC&^M7cG2e42;U$#tWcq6IYUX<~CESY=Zb%O&hcn*|DdC!wa45Ymxi9k<>XC2Z()8B!C~_3@-I@~qo)R8QUqW8Oe2=As`%}W-(tDA6G2h=(!hw`<0eVexP3EtFN4|yM8t{z#T$)^(`OZiQSEhu!(7z{t&wO{Ggd-^7cJ%(_{>*nfO1KOqoQfVu4rKmPdE{I89{mbk;=<w?8NWh)YCyvNELUZ6W#-$T5^h2Xx1dLmBbe_NlyF^2*qdI4T!wk~_WF`<;Vg_D=I48SCcDRcAEvH&Jkwp_bKVt}C!Q|(j;H4%iwBU!pY!_XTo<ipMz_Z^rkl^5ZmyRH=#Pvq&!ocE_eF&-(La#IWnHwsUn*>UA5~bsqbgpX9NO3`S@z`rr~k$Lmw&QvHop2F&i}8!`SsVnJ%4j;Qd<9g2|ToMO8GvTku2#y`66VPeB;XaAI{|5{Q'

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
