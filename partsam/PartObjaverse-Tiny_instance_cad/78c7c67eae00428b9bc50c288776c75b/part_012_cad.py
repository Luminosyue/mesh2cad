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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_012.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_012.stl', 'source_sha256': '1ccb358a5408d9147c87868f7e8e083b444fffb8a925c513c3391de82819cefe', 'input_faces': 604, 'input_vertices': 412, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24017474055290222, -0.4323368966579437, -0.13103172183036804], [0.275121808052063, 0.08404278755187988, 0.036836177110672]]}
GEOMETRY_BASE85 = 'c$}r22XswYyv9!?B#0JuwA|<=TA~ZC7Ktd)qRW*?bcuuz21ghrQKLm7Tny0}qh!<*y^Fyhqujyhj6TXR@9zKid3fu+wcdKqti8V9`R=~|v)kEc?|ri-Fu>8NkcNLATF)Z&ubV1rno6!(AuT2>YUH5Mu;}W;BV!%3{Nk&BpLKrwuI&PQIA}52xQhM5qC=x9HZ)cA39nz#(^N4$B5Gt*zv00VQT@Y|@7r%^beP?b9@sB3%zj;|b}cVYlXqoL(|FVW@n0@`5scjX&mK@^$+d2s=+SerO3f)h!*BB2D$)MGj~BmC8vG@;wW6m@7SZ@P_}5qd__c3jD+=G7Z>i{*n?pnsUEx1Euvt`hXwg*V_jH6GopY1ukM~9>-yHJnj9gFcuuRm&+)Me|xDD{#E}}esYsM>IUs4Z#m;7^3{tEpi&gDGtUzJD{_3Hk;-1pjz({epx#tPBt+Ej_(HClZAf&P>Dhf7S7IOV$`f0xv)qM;8ZzwTcUzDwchqV3AekoYJ6IwjXzXHOChygFIpuek`{Z~sQoO0Mw|zlaWhr^^D-dBf&O{)X32%Jr3+t3{h1o+a@|riiZ(HvKIAjoy;qC^`=LkCxpgS}t|Il(U)3$*;?)FYdEg{F;|fh`;^v7V$fkS}1XD?1De0uC%}2!byB>*A)0~&682To{OaX=10fny2Ng|uO6~JMe@7ch3_^eS@cbElH|X83;sWIFb;JK{9l*AkI|)G`sP&<M;{*oKd4ZW=+Z>wFV+M8fja1~3r&~FeS5TqpAm`ixvthy@!d`ylj~V~(C>eAm;APAtKk>_N8%X8dsx5m%lDJ<Y0S<N-`uGO{NP4b^h0ThV@#<IKe9c>=fdMFly6z6!7t)0{b>I9Kzz;d<x%u+ZE1h=+@O_G-;mSr7YxMs4_qbnHGZB6zuz0Fmww}u#4)vqgMa#0v}dhr633QhfuFP*@%JxA`B(mP<m=~GAKrPnl=Jj`_!FwEm-?Rg8~IyZgJ14?ifHMT)8xL+X-B>;zg}^nj0aoI+VCIkLwU-S#dtea1-|<unP>E=Z5K%XIhzlQ@8f~_!FUlY`7@WopR!<yXq!2@Qj1Fq`0h{8&iDO>NqhcP3I3$gn8)<#9VE`p7YFhEVT+a8y6u+!*RN&4Pskz9qd8!Tj8j{c$?*SlO~dm#Q@&>%G6H_3&KN(%5~W<$sKyy`ZK@*AugUe?2GN8ihWOr%q&;nyuZik|7QsK>TgH#^;E~kBm^&DL+HO4WVM*faM*<JXwWU_1lymJZDX$Un&py<1z(Tox8Z6^ff9nW;>~@K7Zt=?&e1E`RjH{v2@0Pa5WW1X@CG1A|>&}(_ezsJ~Zyr$K7xc&UZW4b>9<<Y3+b+3Jy?$5Go~z_}HQ!0!h4@wD<=U?*?rVLuQ?BEyNq#L`M|}UE9pY<=HRj9pRY%Mpg-5`@cu?}|kIrnD`^PznZ|U~#inQ;<_fl^2&}`zHy5-7}{6VAEh(5WoL*g9Xl`7-)crMiI(^m1#JEur|%VXDciEph1fAf2kbHq)2|NA1MmQFuhl=~d)C~=Hm9-~}tzLMWq*J_VwK#KU5_9(w4WkWi~<#h3F-XD<vx7MhqHClZ0-c_hqR<r$5{uv|0*CNAbtMXgJFQfcxdyB7^n2GY#YL9*#*B$u_g-SbE54V=*Pk-YC-{BbU+vigH*S>Aw4D@4Cw3J`JxKjGlQht)e*Zt<8d@pCApNkbmoT~k#oZ8Sy@Xsc~-_;lGFubAoM$kIMX&bpn^6k4N{cM@rR_bf4J|g2@e{oKHv!_Mkn5!4x|Fy3Lc9->m5fvlj%J2#n-@1R8<Tn||W!xK{HN>~oA0qd)_@BjiD^d;P%k7@r*J9o)_ccFF#`|M%U5vM&VDXLh3*hU4og`n=q4@rx4)7~gz<f8^7xQJlrs7*F`=Q^P7s2!F_7>}gOpkFYzt*UOJg3%XJK*Q+Amuc67nOF?o-Ks0jh1zl$#EXuOVL%uH`&H#%I8V1F%C*M#dD^2i;(-ijeuV~m&~X7_8%m_DXksG`MAbdZ*57>!uPJp^QSG@DC0|yN<jP>E6|UgL8xD=hsfX2BI`Tz;o9PxbJUl0fwiZ*JSRr4f|%!$`e9u5^1%Gk{yp9YnZEKK(RUX^dpaG4Z{9arwU4=iugtsVh-L7{G?Dz)!0~t<PX}XMcUp<~i{Fc{*KLUW-3y6ta#)0M^PwdCr8i_9pf@-#^Mes{0`HHyn`B&SZC0cHdDmh-&TJ#~GU>5+ezQBkFS$$Rd)qu`wDW{lQeHj#Yv~_-^&-r_EiU8z;Tj_GtzPHR{?~?!Z!PD2Nj@*vH&n*OsCLNTf9yJGht``=z6>A4|7)Av*YaCijOQbpQIEDkDCeB>7(dHOimz?hg6Hg2Ues&SLwT<l_2VUu)iqZ7ML(B__sx`4SvMJdol~V<FYm+psl>lqrF<b_nEyLIT`B%6_o;H<R#thh7~x*<^~-%lw>@1h@z1-$-x|7Io?rh!JU^qI;KzL6I%<UE*AjPIF-|(ky1}Lmk@v0PQx5s|x=Z=Z?hWL9t#@dMby9hE^v4BP>_1Y&p_%j2q&>SH#=2luqP)+w;?1O9mdVa&-(MDBpYXQS&yv4W=6Z~uhw?tt3S?njIWlvi=)xA$FmBI|5#4xvw&+=pDY)J#>l@8u51y~xFGq_`3`05UI$?kC+qEdsqYu}}eV^vUI?LoQ`zQU{8qD8Cf0gx*7VZ}&?J?C0>yDGR;9GjP5N%c%^|Jhlb}V)e`=@=H)XOwuC;GL)q!`K9<5!Hs3o~Ut({6doJY~d1{Vx9dfGF`#`s$+l=fL-Jmi?o4z+0Xxqf1ll58f|{mVV3e6V}~UKeW%asWLz51!rNM?wN#r#h?r+ziEe?tV6Y=8)zTXn`ZL7KJ<}wsJ6S^TG8|f+2`pIbKw{B{YmmwUo7h&E%|r&lUGQ6wWp^sU-iz8b@!=jG7c@ZO;`t&t|7jj?{~EGm8_1EZ&`k<$73vL=joPCQm>eOKPt73a{5im5fCT)6ib(D(to!0^Uyw#?IuV*i;s*y%fJoryN?^L)K<i0quj^V8SQA~YcJ*LR384F;%J`*e~uD=csKZM>Z1Qjz7Lb~l^H0$`E?lD|L}0RuW@7z@`rqq`)ePE&yde;?wjPge;u@2gLE19dWBT@)lW#f8O#2Z^{wUao8s%AT)3W^7%ur<4BISzNDSI%WB!5iy$f;TYZoW)ka8`!EYGj0XgK1Yb49y7X_+kFZytepVfsq6kE!W6xo^X%;%kvMJV%zuVe<Kgx#F8o%tikA$+9lcG7^#B<qhilxR1<F#<>mfjXPr{|FaS8<i3@+!yh#X?K%Cd>?15E8%VizZ2;PH<FHXuzH-gQ*Mdq)yJ-nQb0xl4uN~jCPo@>~`R)Oz|4-x5J}#rX$aT^o#L2Z8<I}AY_9YzxcFJ|}7KrCI2=nLckp1ExU%5^Ebc^`5`-9;R9=t{TYCSQpoty~2&I{Db63|uRR8EI~wy=y-?b!u+j;xn%!Y|PX<&SG3<IOgv^Z}`N@;H<~qmewP`rdK}@ckN?ced^uC~^Gz!4G_th<drmJgIk>C%*oo9olp4hmoR=PYua8F&XpE{Hbz&Voon{Q1Wl+g#OL38T0&di}+flU>RSgt5-0;^^QRPPa$~k#`?>6G4F{&{=C)TSMG-AsbjkMMh|bqAJk)>)OY+|<d5&TTE5>aRqkufb`0@%<&`-4`H499NWYK#&&wcwR)6uWQ=JY;{zH$jZl1AN&Ml1nF7W$=BhKpnQXXsXV&ZFw&+tCnn;Y+o_Z8spb;UW(!gTEO3Rgs&jKhdC@2z}p6l{k4kqMY@r=-bqZR*w<e$QFxN3X-!PtV-|e@koh%kl*>essT(!&1LVS>o&A*QGx#X<_hVUnBnj_<D{(;v46$Ab*iZQXX^JX!sd<abA^jU3_bUSn;*q{#gIb?1^>D%4GOH3uT_NKK}vrYqt+^x}HM(0|lks%!7}iJd6HCc?|ga-HV8GAr<+X=Rm&?xCVdYJIq^!-r_uF`5)rzKc!;7QfwX8c{^?+{@J|T_dk*Su=Vm?<ga`I<$rbr>#=takpF%zsjszBU0Gk*&OL<xdmPH+>>=aR((@zgm3K7CKRON1O+d~gXa|d|Yb>!AS<jg~OT)hxFXc2HX@vF8{;J~ZH=9a1jm7D*uQXcKNB*tZQJyhpzV%1uk$J$<s)md^TVMmk>2n18x#l6Vp0zaYAimMkU*cOTMBwwoy%0ys=q=@colE9<TkUZ8ekU=$gPPzuO&Eaq@i<4+S9#!EsNo>w-@KXaql<5>j)d?02K$SA!*DLxEgEs24@J90c;LC~F$sPzPs}HY<tO3!n1=F?3P$|9Go}5FpJ#|~yQ7_#{G%?*`rLFN9`|jt8_#3ISnS9Cm<2yM73<WzJF%Y6z7FxDCSc!Jt}f1N+z%mtsJE<Vtc6xee_0<~65qP<gY2`+_j+O9)cz*oR2z!(hooH+$F#fHQHf*PhWJ;G;2h^#3Gt0$cd;*X?3MPlZ|i?h_LW-76B(aIopQ+k^fmT(k+)<WZk^zb_~mkA9bdVEtcT2H8j7#~QA+M>eN#d9v!;Ni@c-(#7ti&0S#KFVS|U!qyF3R;z<R57SCl7dHO?8<x?rFFq8H+9`x*5qJ4e=khW}Xj-MgZHwfC}4FufZGzv?9P<IONxcNyVRaNh{5KlM}ZmPq+Sr-^U&xr6fruXZ>udcFv8ik`xG$8vXB=b2p>i*Gt}8~gFVF*x6`CL#XITAY8PaQ-}h72=1L%|gE%l6JN{*?{_v`a#Yabe;p4($Wzp;U(_-{Fbzjv2h>D^U)%4%o7@7KYP{?-?}Ck<Ka$uX*a9)N%Z5}>lhEg9i?8Th<oB&;!`D#X<R<M|Cc_(eS4O{`Pi5QoYTF_eN4)~H4OLdpMm+rDUbO2-H*}^=BlM}{&3b^d@a-Kd%1SXhvy~B1po6s=ujNu{OKXSY3L`M!wk-b^Q+mlkpJVqXy@STI1g^#9RB3z(r%i6CdNgNmMD+Kihf-DH_j#dw?cl`lmuy){zuVnC)&gJ%q9CaYwRg0zg{a6KG)kekAf)As2H@vqQ_|Gto=Bzd_D>JYtEb^?Hzm%`{W)8@PDg_@p<K@>}M=4vk+%pXZSu%FrG&(MEM^VfM4lXIgivLSHt(MkMp{}aE_*JT?aqX3HeI~V1HF?2kxs)ttp>ZPLp}bHtG`mS3NNv%En0hn0<>Km-2L7j&^f5&^{kaiLW)zkN7uY@O#Hbck%Vk@3GHK+J*Apu7LbS4$HpODCLiJ;yrKp)1FFx-K7ckb*md9jzc|(Z*G1`;#=HWpghfoeB&GD)`(NZP0k%GJHusM*<N)M-@5ZQ%D=J*-nS(akU#UdoVVK!I^Z18XV&qr`^CIy5ayrt3*jH_^Nnx5mkPi8qv>*=YSA(tY`52;{Kv|meeQc=fB0fE`~!`@@onA#CnR2m+aW364M%z3nNCECul=zHe$RzCS1B7SzCJ$?>x$41vaZv^C&FL2Ue;+wFHh{7mQR82^c~`4MM=G_JEkJO?LB_SeVaqh`%Ifs;cp3*`e>c&N`KkTr=y&Gj!7Kz!3#1!m~!n${$m+94}F#{>s4FYY54y5y;2YSB=d&3)$j0AgCvf2{*<g&t>bMcI6mb)Wb4xn=Wh#cq5M7;sjsQlZLGU8?!v#FB=0$+@Y7Wo&-W3hU1OQoEZ4Dqw_b*CzS&QH=dpz@!h1EZc2eS)Kgzhb)NYISi*t7PNw=`BYw#ZDVUzQVZ{#u1p7~8!=Z~w1{Kbyq`5Aiyzq355CBF8cwZyeuohSWk>FonQ<0a-tXGgqGOSDHEzh%;%mS;s|J!$LQ8Gh#wX-C^7i=0c^x^`jyTe$CrPcrXW%2?nJ*oXJlqY8N6mJWwMwJ?5{@TraU!<>QNw1YYJoa8q*9Sr|O8?@)V35cIM1AbiS9*oP;GM^YV7NcHzIL2qLkv~W|7g)tNy9Y}9Telv>dhd1`^1q&p{lya}oQpNt3cqh0o`;~8a!zeCA4mI#pFuz7&4%B(_Fh2z**9?Ct3Eid$dT)mlry~@)>XZ)$~l`krH1(0kn%X^ZZZYq|5O0-H>iYm^KUKZKc@0s#5e!j8sm233!Hmwv>?BCef%C0QWEEZyJN*SMx2#$8f|*ZI^44DD*Uzho!N-PKE-C-fN#a`)wVyTi*H)`1m)~sNPhpc4&Q^{1ADx|eUqCbfBiJ<BS&keB~Dh%H@@{*xzpc_+wA}1eDk03;_DYnOMD|R56;Jn)ED2p?YaE^Y}6Vj{ch6Qi?0=UExv8xRlH~ScR~EVgE0T+>x2E*upq=wafa_+5%pR;4)I^#Lcd4uXeIgUtwfwYq3Fjk9^sOInSnURf0z4OV?N2aGu69-{1tDaoJpY=w{8!RKie~ubM-2Wf3KQnr2MyHF%HLLon!iUf%y8nwKDz<-)7jaowCB;-9WBwkCUL;cOXuoTX^3jU&8#c={$VvFF5yqe+Bt_Ux4qsS<0gayI>tR@jBwa%qi_}xo`*L$M*s9ul@=7%M6zMw#*OWoAraJ@9a%jFSjgrR^s@lU|(@=w%pgWqq6ws!g(aV$^Vx0uem@?<j*=I`K<@rOMbmnfcQp}@6i4ua?AQf{}c>={ucQAM#_1vG33r!w8KP{)6Wh2R;PauzswZzExAX+zv+5T^0%Ll@{ity_2;A>=P({ZrC&^Qd*QtP<xuhUDuWPb)<Ue`uE)WjF%<WG{t|xe72+HH$HQM<6Y;|{;pe)9IDP72KHL5n<tecj^>RBKC)YLKBLCYgl;>D0ocFHJnJNB5Gx9%dEPv0S`Q?GXY#!oYe1P(#<^RUlkFCRam{34`?dB2q-Z&pHS1$<v-uiFzA1VvK>@kend`<B?b^Hj#|8yVaX?|4BGcBR1;(wlRwaPf(Gs<j%|7Qg951lhc;?BO0IF93yKQj^g)IE>I*8}Qd-WwbvzeDKN^PR_d^FjVIudv?O<R!lLE*<gb=7^Sh#dbvg{IQ7B@iqS5$`+3N1CL`~@^X;%gVi}%eDnVIh?9ojNA#o=_}RxGPNN~o2LiwO>$)WkJpRlqX|I7j<<tsk;r+h)(>i5J^{D^-pVkek{lEIty1F%M|9}6qF3~~Lrr1+FHJThxj%89jh)Hn>bs#x}+?{G6cP9r>TaW|D4XKUE4ap6tjmS!yksFYGsO`u;WM66^*_Ygw+Me8&+=kkc+=kqg>P>D+u12jyu15ZjY9fC}cBkIc!0zO~HRvB?rH{#flkZcXkZ)5TP@j+=kRMWCkROsiP&Ehe2ePXJv?$q?T#{OuT$1cYEk$-CXJ=Ae(4GoYJ*cI~9^@+2%4DU*$yLZ+)DmPbav|y~4XpGiStZ4%=xrsRBLB>!_($q0veHH5AIXcE6c3?}BM%|_Q+tw?wj=wKTTnZbTaa5({m4q&lUtDk?5P7ah}xbUMDER`xI5L4+@0K!+Kt?i984WZ4kiz#4kr&LkEV_xk0y_|rwD2^bqrbQNOCkek~)!G!k*mhsR)ze{PyHR%}sS9=O!0mQe2c;f?SmBZcml%sk}Xvqq>vJk;_m^kjs!uQ;U#GlfPq9T!=|=9%_E_=Q`wJQk=t{vQZtWE@VftGc`BanVgGSfSi|Fm|B2bm|UD%lw6!_qPmma*)Ap~#g(X)$x1!RmB>|@6xXEIAlD?<rh1cWlj~FKk?WHiQGLjb$W5qC$xX=3sV&LP$(^Wu$eqYx)B)r$att++taKt-=?roVc`B3QMCx>MB6&V_5?Sdi@_h12>JqZjb>x-g%}k1SQ+JV-9wF~0AEf?9R(gqikeoq1N6sLhr`{v~WltCF=_&O*`8@MHrK<PbQ(h}B!*^dLav5@6syDeVxe2u;xe2)^wLQ5fxi2-4+?U*s+K$|h987IS4kq`ZHX`>S_h3@ojoO&3v^QC41i2e|I8`SPCr_l#AWtMGQ0I{o$n&WS$@9sJsY&F;<Yej+axyuEx`3QQUPO&2FCx#S#**if$5RK9$CJaTA>=S}FKTykFR~vsfULA3*^g|dHXxhHt*AcaR^$#;UvdX>5Vb8ih}@alhTNIloZ6J!oLq}qja-XdjQSn97`Zgnom`syUW2N2o?@l<$?wT;wJ&SFw@iw!F)99?N%1Y}1M)5M9qL2!9r7FM2l5;8zf`pr{Fm2?^Ep6ElJk+XQQgSd$p2{2>|~V`ztfNuf20;9tE4!W!<ThrE+)l!?Wq8@2(>V|2)P2)gRHa)S*aJf0{N2$EkstT){CE*6d$AhOg={biAnKl>W^fli^;3WNlc1|QHPL+k-Jd+$x2(0yO3K`TalFpkUy^%TQezcYfpjHuG9|XuH+unAaW0KUuti1UvhsY#r>$=$^FO{YDcn#+>07a?nMr#4km|_hf+tAhmt2y$CD?Jb?wV~RA*8g%cOWRlj5<|X!2Nc6g85pbO1SuJc!zdJct}ZZAlIx`%;^deaU9357|s^NUcY1NUlruCf6m`qSheSB3Gw+lB<)eP%D$GkSkEjk(HJqS0H;(OOrjwC8^($OOgvx3y}+wU8#A<uH@|09OUd|P5ZKj{`^m|1J#l2Kz5=!lby&pskz8G$@#P|YwLVWii=STlZ%l{QHzsHk;_s|WTlnJN~@B~k}EPPu12j%u15Bv)+T$A>rm^H>yR5z8<8838&jK*8<U$+o0FT7+fX}^+mJ)4VdPNq2x<&j=~S}PDdZ94QTFtMJ;mA6OeVz%Op4>F-;?9X)2O4!qZo4<lj7ObspQ$@xzt4RQtAq7B3bEtveK1grJKns$eWlH|3ckOR(g=EG=sd8dVrciR(hU%fP9F0k$i~!EA=n3(nsW9$)~9{veM(^)8zfsedPV*J=DEqrCZ2*$QzjyFQ;0`N*9uslNV4E$O-J%1x$+PQKymTk>^lnljo3=sdLGn`!$(K@mlH%@(T9ZTIw(4&waC&N%0Qq0rCO%!44+HhpE4k50ee*Y4T~dufe1^ow|p-hi#h9q<909;$_t3<mGI;Wz>1(W#m-q9C9i-g_=xGA+MpXC9h>Y*DxvGMm<d4M&3>}$Oh}Mok{U}>IU)#mUTTfmAsyuMol57upDXBZRBmdM;gDI#_P-W)ZhMcxIzwfz;%|L2iSF}J)N*~YX^L;G?YAm`99~rLhjEz1DF(tQ(Kdj`jfBnyDG+2mP1{iBwr<;;I&eJ#yG*x)OBrps%cMk?5UnT&9SFh<odj>!#uO8)5#O;DL?b)=XYlDd$al7`ux7So=NXB&*Js><eB6NUzMQ_W7K0=)pc&>`JSBrtFqK)-u(PbU8}mDVSQCn+|dC^aTn@Ya*RDW*wbj<V>DysCOc6b$ip1)y&=@D<iXTV)UM=C<O{s#O?%3u{z+DPm#p*xS*iMNCa)ErWt^@KU&=qto<>opl1Ea1piU(_@H>vwQRJ%p%#-R!u1?KCbtLB?kEDLSXHI)6Z%-AO$}>iFvL{n{-m@yXEHx*&EZLd*QUg1apRo;}vHg_3{HiULzNWq;zb5Bl3>7yI<5wid+0$5i8pEVGk~)GMNgm8Jf_*-OJd8<k6m={)iad@QM;=F>%zm8AKATMcbN?xwM2#cIv8;-p+v|1Ro^CK*=e&_czRGl+^TJ8;8K&#nmoavoZLIV;`6l@p)x`n)jI8=cX*q{4{Z)?rS(RGDo&p0LvK4atpZ-@PU;e4{FYTNE@yLJu=C?nie*Mk9_E`V<qiSG4cG(YPv;U_Sl7rOFO8XDzJGE*'

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
