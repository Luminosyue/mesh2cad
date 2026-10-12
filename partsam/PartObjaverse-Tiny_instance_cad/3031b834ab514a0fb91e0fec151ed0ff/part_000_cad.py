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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_000.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_000.stl', 'source_sha256': 'b1b474677f5ae93ef5c38e32d4d6ed61e3f9e690573efd6c5644cd2819f3e1e0', 'input_faces': 1054, 'input_vertices': 651, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.023256748914718628, -0.4999999701976776, 0.05581945180892944], [0.2815413773059845, 0.02554604411125183, 0.12586292624473572]]}
GEOMETRY_BASE85 = 'c$}r31(Xy=+qP#GCpe4S5S#$Pbzuj0SlnT7_hoSy+}(X}g0A2?IKc^oV1XeCgeU}(7YKxWQ}tXubkDp0Isf^-ob#OfntQ6NtDlmt?qN?N>L*ATYLowR+rq;y6r5h!W>b;E7HW&?J|wbt*X~1$4Hz`iZcC$m^`D`O8ntK`(Z+6zvW+g#t^3ffLkd)M6bS24zCaO2fgS^gL=NdZpwqx1-MTBkR_A_0yZim2y*dx-?*Ck{Y?%^89Hj~sag25RFaJxf+OYQevT(n6LpEGL;aAs^hkMm$N5#6!wg0x^4YTjdw_5w|XSFQ8yTT6b+txR;_#W?_75e+$f8I3v-u6vaYQM?Wuas|Fl6s#mzigcL9UFeJ_}+o1wC~MR`KH<T^{uzs(*7fTV&e1N1DhVy?Mr%E`?emfbUSTxA}qcmaZT-e*Ywl%IDCoM=yrB(Ealr*KWO%Ce^u7L@9Ich-uo(p_MIs^Xx}}u>Or&bD_u|W6Ej-spZ7xh-m5PkDc`fV@<Frj_MVE@_qg|4eBWoi*P8R}-P$fDKHo8^v((dLsrG&U{%fu0`5NupHlLFGx7%#>Kg{~d+<s5tOKZ*j<y|y3Uf(@pqvRnZ^*Y_2oE>kP%NxF}P<CnO()DuQ@mW1ucVD?{9zV|3Ma3_k=8<I_j<2tMM}x#x|MQz3bDmwP8^^`x``Q#aX7-Kz2bVYe;POVl1eZ5_qr59gruCNm_Z$@$pYOHXb$Q3jOY6<oYdh2_Ha_1sxWfTm&&7w@_e3suXvy2W@7A01<ILAPHa_2zsJX7k+w-sW=KOoBCyI^Fcl>xjmv=amZqWUh<@C4a^SXNG*S;&P-^2KP$Gs+2e_t2vyX$RuVD>#D3UAcyJ-u3&_ndqjYxaHlrfT2W`~H4iZ(OU5=Jwcz-j0pW_Z@hu%lqtIrJk;Bq@JM{t^S32a^3?kB@gF%Y&2h&W96Um`ri2$bUn7PlN-&~WgB}oHa_3C>$S8$G|?uRAFOZv=kJcscm5f9Sm&inRqY$=kMr}vR{v=g?K@sC)AjhG8))B`yoIb+k?jwgedoFIvcB~@smpsRHW$BWS6L4iwmoe2-E(Tl`dQ+vF7K-FqxNm9Zt8Wwaq!+@v+qbcTKk^wr%U-&_RZQi){Skm<Mq8?-_iBBr{&SU`|gmN=KL7G_h}OCJ73+_<sG++NqJ+P?B8j3e7-Gmj?`anht$LR;JsfhI$pn4cCXnt)`#Ho0Y9j`u|5Qs5BQY#t~jfGV|{QeogN*ZZ>;CRzVqhG6T05P$+l?UST|nZjE>KDNBpSkae70wA6QpE`93;6-<|88F7L^`K>My+8};~iC)*lh_PwFwWq#$(DEHqJTeq0!i>LV6nD~6>->>yL<D0ZY{Pi8A{DZd^-<PhIly7ue&O7kR7V~^}lvo_E?|obFpxF<sd-O}N?`%BkkiMR_O}1L*udyEp@{Rp~bKlPG@m+7QZ(Oe<eDC)7uGjE`uh-S|^!E7jZ}`FacT~x^Bfk6u`$m4eap61S8xO(0F&^BNYimDv9Sio2b<7n~e@A@dGuRJ|&k>R02d!g<AH0q^DvuC9XdN^B;C0L!F-^(`t*Ze)XkB&Ro4X^vc^d2+^EB8u=BYdE3&~IL`V;IM>k0mUtv|tjQ2GB_e}a9=J0cG5h;N(+`+;#j{I-mrp!MJIgV%p==x^c&t^dKkvHrWxrrW8{8?^o#e(?J5`DLM$4_g0&ePjK%4ZF0{Jl~D{1pCH1;N11wF7x~~_5;CwU_bEwjrN208v#FPzu|dTNVoUD_CNT+`ybEWvv!;3ud)9L_Kp3ICq=P6=5_}5W9=$vKX{+!8&GGDx!;ZbOt5e4XMDK^NIgOO&tN~W|NLT@_JjAaj)~K?|6lvzAm7*zyGuUWW4_+NbHV<c(U$qhK0Mer_TkPA&S>+zGxqtxzOm0Y{NU$^U_ZEg@N-14Z<P0rY8GwIbD+OQO^!C_)9`I`7e$-%6UgVFCDQ(&=jdSHc#ifR_sIP}=sDN$gP)fTKlu6A@PnVDUCZLc4|+~F{NU$wXZr(EKIpkM;0Haoy5^jbdV-!?gMH(<)qVU%w0XW8&q2Yy@f_sq{*B}z=sDN$gP(I9$3tQ)<B<D;Gh?wB^SBE3gWnGre(?JN+tON6KIr{Guy4E{@O~c`V;K*|eCdBgjthFvWBC8|UZ~`W7;}CC<88u4DIfIy$CvyoId9N=Cui(8G3I_T%Dc8blk!3Dg}l*yV$IhTcz!JT#U<VTdWn|k??)$*_3+O<;wMkHSl4^Ki9E;MJ|O<mF$;D3-mu<Y{2+c}kGwzYv`O-^EAeHif2MvP=KSl0jH^AV#b0|=-iJM!ChOj<PsKl8P`}^ueVJ3wcgNpl#2-~fmv`>nC+pJjn&P)SpzC*?{zcv!JZ>z0#w)r#u20)a-kx{6qW#ccXXyINyps8Hqo4STGfmg^)-Ea66&ES~nOakHJ^c^K{p;;?@h7*RtlO8Vkv^~I{(SK_{V+?Hzs0<+vPS&(DW>Y<-99OwXE)_L>GOIX)RgyuJr0TA{Mk%%`+et+iod$mJY7Ef3d!fiv*M>(I$xI?a8Jg;<*VY4`&9RrBV!NA^9`T)YdzAB|GbjxP4~U{k$2~s&+B^qO8k!d7iir)Uh=;x<f{Ih^Rhm#XY4n!J|9mZ{?kO-_cjWZ>uT0U{98{Z==1izAnnZH5`X@O@w%Nylj-)jzUd);ud}1|=dMd+96uN#e(Uwx_e2bke#|jid{_1nT2mI*?eQIVi+}LR7+wC5P5SZC1o0azouune+C=7|dzz)Z<GcBiw=VO<e{*cC<i)G&_dZ=Me#D#My55VeVk|!G^j$43`6;l@a=os_1!aBMwo&|F!zXH;SW(8$g-zmb3ma)3x9&dM#eY9cmv`I?+iUTQ?9t=RmWKPnj-BGC**r>@TR&Ikb%R*)kk+j~AGsc9@plf^<I}fckF=*>9QipgOxIJZp48v?i1?Wu!(|-(YW17nmhpTkT>7!ZY4JyN)BWXh&9?eR-sYE!vzA})HeatN{Uxh^B)80q=2ygDyj#ylN8A;uKk_PmN<9u;zfaz4@gL09^W9dr8PB2D$#c%B=JPs+e<ObTuG94K57){4=D=P0>*N^oe7D`XC%$*G?ng(uFc}YR9*Ljgf?k*0_dCe?Fw$r7y%);L`>~aenHK}}`0@NFt@KN~XW|#{I7nYtSbiCYM}HCDmUx`5-_=a6_n+Uy_njV~k6*JU#^Uc?qWj%gZ(SY#V1A|VuiM{T_L<&sFU5C!smGPE4m;MpVqC@Qe)qn*CiB|yM*Q-Jr9EXg?6vq~%IkI2YbzUL@sF0){o>ft(^@|4iS8G7;@2`x*1xBn$$IF|sY}Ut{?vZW+>hSnvm|em5{lpJCmC;fyGs3M5{rN4lFozUVGpUl<|pD`elGbrS5(%MsVOb>xSKDR{nL+Wu9?S!?On`Xi(g~NBy)c`>x7E$itVj6%Qo3}PR}TQw`qF3IS-weag{t9?P;y^<7wfRey^89e9zB=_2<~d((ki!iT~&L8RmX*?{MHh)AcwTd?NEJMPBi}13GAbW<smq{-JKaqrY4B)kX7(zqpXjkF91Qc^*k!RQ&nZWxmh(OUmCUCI0G4av$^!l<Qhl5x?Pdb32`(;o|2_tk3H%F<<VF`)Y{qe%M~0?@h^Qiyzuk_q*%(UAZqTYaqU_Z<MZgV0wA3xYNjzXZMCEY0uln;%~Yq_x<#F<-Yc<OZ;EY=)Ae@Po#YAe&R>w*X3=?O31j%GmQRi)Z~P!XU%7NpJwYlLwwtdmM2X8{?VV;O!?knlVo4_#VqmJhuE6Vlks+OHue9m*8%Us%<|lre4cfjoC=fms_#Pa8)Vbh>wWp7jGtMH$WMhX`n-d)%Rc_{67e1GR?7F?7$WoN*QMk?yoJ85#K+~juB{dS!E3$Vx<jr=-cqlpyr;FUe`aOr-<U1p?;Sb8+>h>(JH#LJShv&HCtB8%MZ3vQ(egTPp*iHa_uxtKqmK>L?F>mQ>+RiB;-@Jr>rdD&$<N!<;x`Z1^*g>FA>(A_myDklvTjWLN!G*cSB-wu<IQ)s;ckn+c%h6F)+<ld$CUqOu+GoutFoSS`-ORtCd%Bu&S`&%?;JKl`OXY~%5y=%cU)JhA-Y^2d0*tL`ySsuO4r|~ioC~|V!v+AzvG`8GR~hS6o14*eIId_oFVT!4kQsj`=7E8*`HeW^FO5&zuOBv@0`W%h`%FL{G^#9b^DLS$oq>*8N{ETr<d~GPe;l7tI?UnU%g54^Wz5T#~eAtFJD{d$CYBVjQ@_g#JAnAulw<f4f6gdRqpHN@$Bl<SMEEH@`&%aKS<|cS_2u+^YU4)*D++FtUqZB)1LjhJ)Rmbq@MNoNeAkB+|?Yij)fExe^akXx?d`d-f!_Izn`f6jrqi1h~K=9_~Dy%KRPmoiNCG2?svz*M^gV5e3z?>ZuiAZ@;>XEYU001K2%@tx|%xA-fcC-f7Wr_3DbD?t*A>ro9OZ5tCf7W#jkTq_GyPJ$T~T*A^F)fOqVaZF3#fHVms*e?_0Ci;zyk9uE#@`oU$&pi=f|I$o{9KJkPs}G^1bUj@I>@ttsoqgXYxVqL@B!8;7pPJ*TDkgPsh~e#TC_EI#`O$1j&<9ZS{DQomzXRJ6r^(R{ehPt;%ROFM|)Z>-)o8qXKbwB5*mZS6a=yJVg&>?MAhKDvHa>96Fz`Km9ztS7c)Hpx%I!T9g>{l)j!I`LbM5Z~RVwr)?|^zz<y*(mW3=F{`n)^EAoN4^+Od-inF$FB~P_3Eby*724gT=q+cC(|!irpP=Bk@3)Hs`xu+>v3zW|IS&{#CIm>spoIn1hQ_opDDhtqKvEU@}45#8~t9XioE|CGmGmQI8~oF$&1|<KgIWxb^Ytc$^7j<kNiB>^*alli?R5=tbO%(`uweo&m0RFC$|!Zo7(BDve0t9w(Ns-{hr?!iSMoK*4G<-hW+Yd@)@Vs8Dn4MX}nB)_Rq%ism->6dTz;lFIyzq;$I(Xso(L(YT8+Ff-XPgfqp;kS-)2N3#0V9?OQuV_VcIKF+QUtKc(`>?>jd)F;DaA{&oL;b*J?A7V6)s^XAyTAkO0ZPD%Ys>dHE{X)E*PwjQ^(8W&`JPP9Y(%<0FQ>v3m{rahkw)a@|dtJK-g_<TJ?Ul;3t!1wKOX=Q)wzJu=>rtiOwBirP>Sq_Om{a3xtIFdh;{Xm-|;xC`2>-UvjDDTY+AE*8lGJn5(!anw-WnQ~NTgv({<}BBBK(E_QS2wvYH@rZ<uhHv?@to!D|0V4iJW}UpZn)HQ^)mexK2*1d`@6T}73RzF2;J|${wDjA`8UOnPTt*eU5;DK3)$!RcKjmqrSomZ)fb(0J<sI#N_W$H;unmSbuxO^UW@Ol-_x82XP$2@^Vg`y*Yy$Oq}SiaRr!0vWWCz-n00>l7+rqg3~6V+r<7mr)a_g`RMx{D&*;bEZFGAg%E&&d;B)%r58Zy_Im>+zKcjuV&gV~)WF5%zigpgEuE#;;ujM(n!k^;jFQ>~J`vlL**WwpzYVn=--;%dC)ph-)SM0U;?vBNEf4~1q+F8_oL(coIfqA~WkKq?@r|WmTdnfa>N@DRFotN{zd8vKp^CaSTOTEDCyKbZw|5>7WIzNw=Yu}MBo%k14%r%dHXM&94=gcno>9|<Vn<ta_Nq?JVF7J)Qul3tn-Cx<t%X)q@v-nk}Tj~k;q1$wOT;*2DygQp+{K9qTTl^L|#Ls?Nm-qhLFgiZp@%%rs4ll`NZU2O(vL5Dlh(D<396f$2Y?A$Ct=!@}^6B!<qA%omw#TP8%>5gvCsSTazZm5`=ktmG;IYo9EyFn3*R{$o{+VfW&F8f}!|%3ohAyAwbGhCT1;p=Id!4>s_E)yMg{{}yY`DB<@BJC|znH1>W~_&A@teP!t^0-dioOcP#J^Kxsjk1@g54IMJQ(#m+kP&7d9UtYTitt-x1aHUoh|kB953@?RB^7WgwC_^zSNt%g!l;`E;Y|P+baAQ3-!2iXUxCH;{Px}`?iF?%XJ+oDSrE0bEN&rCI5X(iyt{s`|irA<o-3g4DD&7^XWMKUay~y>}8opNwsh6LtH!Y-|W}t^`@vK>up#$@^C=s!P&<iZShyXmh%p|B-eWxKh3|E_WRnG7k^t(Jsw=UQpmU(Tfx#_Mjl*iDvH0iiOf^p6MBzT5`S?c-S4(X{QIbfVdDE<S?YHUs4V{VW7;>~S9o`aiy!i}?ibHL33pli>3imw^Wf@KRs3|J%XB+gXWY;63%1eiH}>J)@zt2u-F122$k(zCtg9}5zvFuR`<kbceO>Vy;)liQdW?N(z|VVXy7mjsk@eGyZ*$Evw=>`~PK@_s0som>_lxm6g~wOZI$t7J?X~!&=gqd{c|mRQtKFA%@8CMw55&|VZzuJ6js3Z|b3IFcxtFBbXYpAF+`Z??zGz~7+MiPDStb9@$Ca*u_(!|yesr(t7H9EyZnM<y-e4_nv_Ie<ysXO`?^Oc+n8eyQ_Fax<jl}=1myDC{d*nVcw6XXfE@|KGS|j(J1QFsN|9Oe_dF~7NBfgXCjg{Z;-HY(^Hq+z8(RGXbyO2Ch#Q&<KuHU#X1pH0e=9=^4sL|B2E*bseyoH}RkM2iTsh_3aCpWjOw~m%h{#{B-`Z2Gxzv>C;-xjSb>xS_@C*UW2A?sn~+R+xDab^7O;C+I>bAzrw@LnQu8`_y)@^GSlw8c;UR@Tp-f3W(j=T7foYdx%=uE>0{&Ma+XnMdB$`=p(<+FA3@c>{jd&$aLD`;**fd$eagnKw<>lQDz5H+YR-u)U?cXKP3C>p10p=jku=;(RB|d^g(ZPTEEM_ot*E`5n!>9RKJ;8RywzqAk87T3?rKc@}BUp|0GopK9OuJ;-sloA{|hq@4=}$^7cwoq0E1x6{=slg!f@J-E+?$hyIMU|*J=>^G`f>TztxcP(D5>*0Nfvtlpt=Z5Qk4?Hio?JfRQhg`3tp7=lG=dC^4e7&yE`dP-auXALa#iyNt=WfHl6Q}#jxG#I^_ZNTu0sUO;85$?+<of~4yFxOqjQic#p_cjO{w0ysFFtm*`Me*?ztiV+mpLr^>XebJdl~e39gdl@KUsr6=(^6o_jo$FPZb?z=`Z8F0e{0doloOA%h4!G{L7gnpY!X;ec@r0WglXc5BN2T>GL|Gj!GW(jO2d3Lf7w^@|nC3yf#YwaW+{W*#Embjke5d+Yf`S{;l#dAO8)N>w1o#;)Z^{_Iy)H-ouO^!~7j=*<S^G)+KMV{PKHEnz7=~E^G0f9(;E)Y0uY%`Fo#n*83^HZwCD3U+R8w&MhYEzkP!EvBz{hj@C1D|2h}oKkOvqgx{OoxhJyD|E|Zs`^?R~7Jv3;UB9n&d1+6~L`ypziEc|Cs!kIBLL%wMG0$Ty{`8`j@~(+f#4kTozi$aVkEfd|{+mO(9$(_(u@-;1OYV34p6=a%|01QV8!IYGo=;B`|8^zm7k;O6e?MLP22E#}^X3^k!*YKN{H~X0mSuf&9{WR{XKT!6{G^q2wcgK?hd<|7`rT0?tE>Z?=W)F=*X#1jHd=k|M@Ibt|8l78w|OoO_?g#EH=oy4X1=xlcX{M`&*C4vCgbhN1X&MnFA;zLIq~^j#?f=B_yaEL@!;81OWu#Y#vk)q*2z1YWj&d;%z9oU&xUV2cTm4?>vD^4>p3;f;<ulr>ks@cS$>6OeA@EYm-bv(Vac=MyIQZbtlQrApUC(bv5J2GcddDxdy=lUT(7(0WogfH{E6w7n0;HJHR7`mH`;Ied!40zZ>}bLEk5f~;P*JgXI(OWr*>{%Z&^=_^6rWoxL>@N_VC=~9KFeMUdQcp@^^nnwut|1)KYVKZ}#n$b<b6`ygsjO*LF)kx@vZj@o;5_r5>ZaXY4NVhuqY8GxnbW-&s)lacg7wz3D@YrG9r@Vma@;Sn<28(dB(VHj#eZ6K5H3?t;zb{(fz*_=}TBJ8l2S^P_8@^}0S=D(xwL(2^h5yo|CwJU(P;kF(3J7>mz7&8WvU_^{=?#yoP{kBHy2r?k`fcVD@Wa-aQak*<HrOR1;JaZ7uAM-R&UZFb5!K08;Ee*FHF^?t#>-w61vN6LBmcMIO3r^SzYV(}e|&sf@Tyf+K@<x@(372YlDcDM7E_1rkGbIJwQ+a&tBJlh7z{VVFSC7+%-<D)J9kO$J99kDVF^IsLeRz>Z5TSZ7ddtMj6<V#(@uh1}gK7D=NvW^AnG5n14q&&a-c&6PDzsH`%=6XD>Z&})Dyhn8;yKTMy-fb@XiWRplc{BdKqT}zo;@7DzdApxi#_h~|;`2OZ)D!TTFGhLq_WRa(QNO(&hu(`1to_Avv8&&AmT}_DTy}4KzU%Ow`2D7dBtP%JvyNwekM?wVWAWXIQp<T4f3W7k_+8*!!mlj##O#a<kFfj|cb^pJ+deDdUqMQ!U$sJQJvy8Igj<>FKSSgH6Yk!n|G)l(yF~FarT=e#!=3!1zYVwiamgRI{c+hJU!#}cOO#Q3%^wf_aTWa*z6xJKAHX;K@z@{N(MRxg_!{~UzUhze{qYt09sCu11APpu^StuM9one$2SV}B=qvcXKVGW-MD2Fr@A1;{S^0|Z`uSIX+@riY{yBONzDJqo<nXCKzCoYCw`kMX_^R9!^lSKQ$~++-Z^@<7|G?kE571Yz%10u*<WlJe@~Ywk^?jhOhg`3^zVFaaU=@lVqlw@oe*MR<S?v;v)7T{x+t3%V!yjq=Q3U-IE&>-L6c->AXCV})CKUf`6HN=NcyIeyMsYH~Ca{bC#b@RJMf`4)@0GrTQ*ul~RQU<{toUz2@t=g^U(nxS6+iL4(m&w8(KqNH@EiCwq4+mK@sH?Fa8`1i0}X|9z<CJ8nFz&+3B@638d#|f&ciYJ(OhtT_%lLrK0<LuLUAfI6P$^2r{Y+3Oi{EDTog9OLm|^RDa1H(z}eA!a6ZnRoiSO`F5^^bW>}4-yo@iU72slMb+iJk#zSs@WT3n{J|~(1&OjN(s(({3UUGAMdNd)dGzF~sI;mayKLy7pN8iA2D3hFiDMLRiEp6)e(p-0Gt~o1tcG7Q3!%Y1cMtxz_m4`f3ryrD7HT6qX>Z?j!io^X;${&@;u{v*Iv=Us2GKxR<M@@f}Kx@Gz;PQmxI{s*dwnl5gt>HFkO}Ljoy7?o5P}~gd4L5^Z5{mozV;VXR?G2BEqtI?}6g&j&1rLEI_+u#A0qq5MfE%I_a9OlC8UYuF%c0HSa&SeoC0r4%LMU#F_JiBPgG|>y2wepag2(%#yFWVnV;DLf9tO`tSHbh(1%%>tgyNa#G<X`ho=GU4NGKkKM!`|!dK95Jl2AMaod6sCF@;b(f>1n`P&|@Q+!5^ncZ3_E4Pm4I8WD;s`=cP54J`|2gOj4g;iPbKv>coqPJvd0Q^4ubDsXx@H=(!&+7_+>yU;=KAo|jUc7_Xt_~)@d^7!MeUGyDV7=CIO4dt`)LkY#{(E@OKI31cFP6ywzi~eR8R-yPy^a=bWd>p+EABX1?ikJFh33?5^4d3SYYlPx^=x^{n_%We4H*HjH%}pr&6fFQ3Ab*OllP`OSv~33MRT^z-e>B&p^q}c_50Ve1$4vQAtn#PyZ~Mo5Do&4nuz$?|2m0#+ZBeZBDgL*9z2J}g=sEa4d>1_p--UOgTVSP|;hpdfLh*KVBfK3p=B8pbU#FnE(T(s%j^9lvjzhP=aqwP3@k{hH{1W~PJqP~<zeX>>XVDn+0vrRMK);36+__?xaWK^`V{sRH4c-OsLGQtP;8^rA91Fid)%bhCXT^V@pTa5>|B2>-m8!NWZt3UN{;2PdVdxmNH9QgRh_;41!tK$PaC^8FS{H5wXGb%@+2Ks+CvYY>C7J+E39qqBC|+Tg`K9y~s{B{zC$I{|A$S?!5I7m3*ooGKop5cmCESvHDeg(WD$~B%c4@ED@9iJkuQ(I>v;E`sD$b7n$Nn)tid&(@P5CTNzLi!o<-ZdBQ;D{8L?^-t{gK2U|Jp?p!73ELM{TeQ#fQ-&c44K5;KT3%Lh(LyKfDh%?$L_X{d^R96x|Q+=lG+9VlR3G_QGcf#mQ--YHM;raVj(soC;2hCV}grHPIw+O}HwW5LR=i1LI%@WAPID3cdv2MAewP$!EpipvhnrinHQ5;jC~rv^Ja#cA)j)`m{}Pls`uLW2ir-qchNv@J!T=j)dLtSTqVA3lB$!z{BC{Xa!hlF}OM$MkxLq%?W=FZ?H=!_AvLAX6Cc<GgG!0oEgrAR)BNC1qsD{&>?UicmNs&N0BeZ)5upZ+PBy)?Nyr8)c&MgpVBm@>rF!rlx8&LBqRA#+R2p9PUKr@cT@hm(?8v5iyNH@m-k0Cf0RJ0z$M^(Xc;&keAzB~$1bcw@p<%X_&j_Hy#b$sjXk_#wcnqKeuv(GZ*cr~gyJ6w#lN6;;9uZcv{ALS7NNKSS_N(ZH%F_%gVEk-HMlq24J{9=xigM&Fq^UXJF3Rq?|fGL2F(TMV$3O4q4*!WgyIOk?*m7`ZO{R58@L@h6dp?36i51Fgg*uniU*;i;mPO}bTm8_oq&#pC&1&;5%73;6dDPSf@`1^;Tmu_S_%$_%b|tfa_|>+3B}u36O?A*v+}c0wiKKN&Vg2hbHI5C#eLC8IFj7;<=m_7(iWwOO>Ij|+m)t(m8LdbS8CI>rzST_U8Y>Q$Yp=}pes57?h1E7$HU_}R&i;6l=MeYLh)C2(I4!>N*}>r!50a|C(#G+N!WOPSFE1(7oZQ(2k--qe@G~PhW-FQgMTFy*P)H7t#t^+jnL9?Be*eI7H*3+LCeA|&?0DAxCs0iS{g1*?i8yz(j!FXhtg*7Ab23!H00x4Ys#2e%oz2dYApKrtoSE12dqNzb2KlkLUBX9zHnd8)sVKSw)SJps4+AJ?FaXxjAFG;sI_cTh}<jG{cHw037$k5#cCg+_Bx$IWG|`qyJOJKaA(RWR?k6K?ee^#_#L0sd&Syzd2d(>u7<XQtHDhO#Xaou45gl_7NV2jh44VM2i${W6?gJSSAPsA6pyy6-?>G5qFvzzXnnLRTpzBBc7p4|^$5l73B`la;qYL15utc4IvSn}FEh1u8KHQkKh~m?Q8zpp?t}J(jce;eC~oYJ0sd&=kLHBp>V)E|gkmS!6n4U4Xk$1GE`v6J%fO}4`fzEuBw80P30Fev!Ij`}LUC=hJzN`ZM<^bM4u%K93(-aJ5_BoL2wn=$N9Wo<zJpS{0$m2LfY+ca?H`|E6?;s5=^+$vK-b$p?tv9=LpQ<OVB`L%cq^fJ4*jci7P<-EL|wB8#naKXu+qu!bht0t2kt{3_eGn+ec}FS3%CVs>W|KXXK@b0??QW5b8XAft?+Vq3_1s%!?9y%Lx1Y^_#Xo|_~QtA6dvi1F*f;r4Bshk>W>C|-+=EF=krG{zR$&XiZiI+OZh$x-zgsLkFow}jy8nz`@_L;4vxvd_xUN)kni%-R@LV9=tg)wJQ^JftLxZA*`x3=bPKHXIIOO39LH^dH=%CW%`uy}?nWFp1|Ek-z!4lXj(p_ixCU?|G!LAIV;Yf<v>cZU&W)yn({W60u6sN=YX~<+C%{UZz$&kwa-KABS~M@5mvf}0PUAQS{3+T5Zo)C2lJjHq$wqiHdK^}|72b%BB{tLc&6F9BPJmTEtf3C2+hLXO!F)fM@3xTF7JT1=@7(0C0N)qjy9lm32jA!5yF8qK2-m8#rRlm0a$G@<Nym3B`MxFJ<)y9LxhAD+;jQolbO^lEAFKT_mr%Tr>sv`3+u<+Jh44bkf5EZpb9X{<Z}QQf`qscJ(cW-x%CF>D^|>9PxDEMhMSX+e{%9Mx4dwfDtomG@P+XFH7pA@za4WPVT$1vwI97fBoKRede#l9E1>nMHA-E9b6}R_CTYvN*6!)PY2GEBs;nrv$xDVx9(*{*<1wwHt`u{W9l>^R+mV!%BJ}1YPqFwFbwzQ!&^%aCaL)*e_DX(~*KNi_!94&>_m{4Ozjf=H};#KHscs1o$k&`~uHxFLKv8%|_5O@H(2wp^a#cEAg>wR;y8QdHmO(-5kC>}{DZi;4rjr)+g?|5t<?{6dFQRsSjJ?BuY=EVY2eiSc57sJcob?9<<9lQ-a0B?iOpeNun@R#Tz_)GW#x(~hppGWt?=i#&H9{4PL3XO$N!ROFu_#Av1-2tD5Pm+^mrhZpEA6*B}hnJw+;3e=1^bEWLK8St^AB4T=1=tH8M$f~C;r-}Yct0G6o`U1xUFbP@7aW70hGXE}=t+1typx=$>o?X7#XZp_a8I}&x&rP8PeKpEli)e17oG#pLJz~U;2G$Ccm_NTjf1DblhIx9WOx`F0}q3Tqr2hZ@KAIoJQN;8PSo`q>zLvWXg|0E>_R8OF1Q;y2kr)UL1)2T;QHtcxISDLod(y1Yon9l+HehY7+eFch7O0T!Bx<qa242z4uYL<Wpbjf-?(2WE{nS0vTzx+8(apigm!@|!9~&fa8WoEtqX_3+0fc>HaH7f1I_|xM61CW;Z$f9I2D{6b;8Nv6li5Q1)PkWsOvZG?~03~W#Hm)F|-m~3@(8dg-gKM(NH)$oDj_hCxnxrS>PmaVl*S17*2$yf)l|B(ByCe*p8-v?QjU13=V;9<V0P+v5!(*4lM?kgG-|&;L>nKG&@`oE`lb6i@@p8Byf5-E1DS23TH+W!I|MqXaYDBoEo*mso_u15cm@~C2E6H!b!=Ax_)E7s<<Os8tw>pLMy_Z;I3#9xGUTlO%Hd5>!DfUdT<>yGh7F*g=T_l!8Os;a80;6`UzYe4o6eM;c!(nDO?o}BPZ(mjpqWzz0gi@FSsw-748d9L_5P1;n`?Ccs4u}tpm@5r=zvt>F`vvCOj3Mf>wv8z)@&890iX+tHLATNHh$Nga?unb^XTkm*NFzUw8q$7@Y_&hL@wW;pOlFbS8WNK7me$Pr!%Jsqi6qA36oz2k%9r;Jxr3bOgKyjzuHkSU4IT2uH(ej~G$k9uk`1|MkE6`}m)FCu_6(kN<*?wElUC`N(trx&nV}5>Y>qT1)&BK14rg{-j!B`ya_UB3='

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
