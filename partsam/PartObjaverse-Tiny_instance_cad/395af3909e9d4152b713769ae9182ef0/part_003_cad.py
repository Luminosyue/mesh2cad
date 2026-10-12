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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_003.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_003.stl', 'source_sha256': '754c135b4a08de0cc361bc5faa8504ca50a3591eac88d1107a39993b36224d3b', 'input_faces': 920, 'input_vertices': 518, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1159215047955513, 0.026035048067569733, 0.1752110719680786], [0.10616566985845566, 0.18988704681396484, 0.2837052345275879]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@-}g@tMDHaSR}F&EML&88CPa&RL!y@uz2!&<GZLbcAU8p@2qAjO5xoYZ*BiY@XVfSA_x*at|5?ww*1O&}vwrLQx!>&Uv(N5l-(x)7(`U%1;irVwVQGP^xvFZKifmdwZLII8(S!Q=`d1$AH^D*6CBFLksSDb7Zs+0UppDfgx%l|{_Z#I>*WyyYzne=%i%b6zqehSN9^PlfC?8+tx9}e7@0;fP5A^o)P5WG~W>vR}mg?mzTBcb3AAho>6~U5u)BeOXwVi&tyOH|*$~dFcwl7e8%Oq`w`fR=XPJGLPG2&ahjoBmVCM2B||G1C%_Ji#tAMN)hr^R2{0qJu--7lXfWJUg-?Zr3J2TA^>y;QRJ%^M<p(9rGTZ#s^AA_~E;Gwy)o-^3Hw4a|gc-f1oQ>*J4}QfmMG;y&eT4?VVuf3vToxBHml+e<%|@|$Zu%XO`vSBr1!a}??4`ipO0wn}_!kyI(C_OkRjN&kE$^69>Mm*n#}k6hR4vsiq~{!{Vlvys#Z_4dbf_}@+^i2rc|%9-0=d}I1EQ~v(xQn_FIhCaA%z2|bj_TYIaPlbl?%dglc`IMe_QvBuh#Me(&IVk1vzm9r7UjhD)<&wW%zPnu4;*}NUS?#h-(q(HX_ho6Cx>xF<Zhe$L))VE4S}VTMNQ)ES;h5B?_4oqu?duxum3$KBpng(j!B5b4ivMI2{NcgKr^;X{r)JB8`acsOzW)B0<Zs;;C%$EwKm47=Hc9$?DRN)-_depA?ycm$>~|}iL_h2&z9r{-xvqWa_Y<NudZ0X~T%`VOV`EODT$RMP+L|TG=iI$e&H_bn-M<efNxeO(B=ul>mJNQ{ky3B=0lOu=t>(8qa$ga{HcL5Pw?sY@zKU-d`Bdu1?mJG(qi=eM^aV2>lKOnqQ|`<7`@Z;^cllVkU!RQdFWy5wp=-BD`_>tR{uX%|`COSO<uno;(67#WiEoZtg#HlkEafrY)<gPI^$(%m0;L_b3+2VPx~E7zXafpJIn80Ekx#Rya$m;IEx6xxMUhWFSJcn<dy?K#+X?9lS=UMV))z&;y_;Eleg0@^7yVC{^Wxud!2KSqxKYxVXoT@T<?C+ghu6nQz3Gp0N_yL|C*qsGeUtp{cP^m+e7PgOUOsNEe6BoD?#nEYjC`g9p`ZI4LH+BA$Y*g2lxINB6Bq~E#J46#qJ8g|mFrqF&p|$0CQJQTV(qAhyMf53e876S-o3`++r0yj&$hhMUdGmy(%-DD{E*)7WsIboun+A!qznAsBMwVG-OoxpnzQ~8-#*7p>Oo5iIxc@#(?xuv$Ofd(en;v}uUA5R?Uj$TuXcT5GR9dU)X&L^l3r_UqW{19zDx3XQ&h@nxtSgHJm;<W=A^6Ae~c-2<hoj;Ye+vdMef&Vwh;Y1`~v(ORX0d^w#=9E+k%teXN{M9tPdh2y|!gP@=tP+da#@>j`?a~DE$4`abHUwVZ67VA-?@WHK~8Aw~Lg=oH|l`&FKN|*ELbvQ9D!(`5c-h?Q8rND)(ii%O<|%OFY`QUEq0)Cnxc(&1OqIo8}~>Uz8c;ANXOFT(`Zq)Tfc>?M|uBkiM(sbK-6IE^ov)mlc<KuzKD?{p@-vzP<KCtS{AaVSH77F1~SWlH{*HyN`ZbDH*;)-!<~t7wdxd_ALBz*)Sd_f02BQ-(yi8=Y3KhvrR?0u30|{<+(le5c+pB%=5J(k<a#z(Q@52!?8XdS&VY_swn-z7S%)QK`%B>eCxvbQvddi?cux3MgCKNNPFq+Z%aOg-vH#_DH!cO<ohwXZm$0Dw}wl3^j#OF9WC4XqWmLt=~p(l%+i1Kq?Ra;`y5%X?b8w^ALDZ^<g@;V+^?3&7x(qNCh~cC{fPK=redD7mPYzl!{vSrGac@?U=Ec3Mz*7p{+X}TvvJP>`LvCed~EJZvA%d-*&+SyTWx7y%M@qSL(^pO4RbH%+x?j^zpaXce`huNNmo~_r(c#JpUoAdeeFY+U|blp#n+qHlJeLKx0L>G{TM91<^F8!2dWQ{dN2zbNPpmAl$3MY8jP1>{^Fape5L$m#D2_st!kn?e-{wn(rP#MUAha(^CL#ah1LDIl;2Xa5d4tIGL9_v>zEH$I3S-R9vF93vq(GY$3JhEe)7Jg^dGC!5=pOF?uoC*XO{I{_X@^1t$9g&b4oq*^U#Cnw{y>kZ)q}B#-ma1Eb4RqY52vuY(=}zk?R^oPl<1QoQ3j4uSb9QYKpHN?1%NjXSKAWK6f{+TlJ+){{B7oSDF)ieT<LPr#Y$n8T8Yw$bUp<X%{1=5c+vw9Q^KOB)#_OyyT-d+KB7!*o^#xJ7Pc6X90Y@Jo-<)*62TF!%&_aWzlcFK46}2`4{f@Wk<>1nm#l7NuHTVA72~$s5-5sKiE@(P=5cRa$U1q0bI9Ae_VIhN110d{T9YoYI~$#F-G#YXk}3Up>5EPqh`o>H*Z9vKa^^Y>#i*;`P<vyk$TX_eM?Zjt^I7&Lp1i2cFPCxjTTj<eXR*8D8JY11oW$<NcsCKo3Wq2d>MY07m~kadTG@E++^|fy`QB1&0;#%$KqSWH@_B_``0^tz<BqJLHb6gkv@91w7d34IQ-NFxZmG8NqO{T3z&Yp)Thm@JMOpP9F+e_akNWzH<Z6oD6ZRe5b{sGfby3JK|WI&$bH%S{)zegz7_XX@{!Dw#^ct~zP8F8;D2z!e(ZC9jO)6skxzgwpKbNl%DiE{R!4k$X$R~B9S>l=w$(!V4$GxH`pY{QU+1c!obTRZy-pl}@f%nU?UghK_3)Pu_J@BJLi*H0E5*-;b-}i{p!n880Wv@6Z{A~EyQD|?=VX)iHTHi%{hUh&|DaX+n;EzT`+?<Ow~3#$O7>}b^bqWe3f$d>{y#(7U5|IfzG!PQ{H!jr|JTEs%6(bQGw>UG$h>5(&wc^pbqo9(f!J5~`-pv7Y^?ZJ%VhM=_9HMqEQv&Ua(SWud~?Tqn-YP19(qYVSUdDa`(~aFf6ZX2XRD6#*nUhA-?Hy2o|}@JqJ5wHh_A0smFE;Q`!TFDW%`J3_xc0-+r}BB{F-Mq<bN?4^}jzB^T{Juq+i!l%5T5#kA9o04D!!D68TOVj(tdfXYq~1^pcO6tp~<w!;J8spOy8<e)R|1{oAXplFw)CCv`upvz9LR#W%NA!FccS1N+SV$>Lj#&e#uJxrX_9!y)mtz;N`p&!e%A3fLvS5iwBm)r#E4bMep(xbC8=SihQ#!hKC%4}XX=*552s;n!J)@~l0)LO!?j!T6f72>I8ngL=5W7xiCvzWBCM4`tmqYp+E=bnK7x1;b<?r5(chV(a0H>lQj8&o#CyuO&ZQ!@5Wxb^zlur2w9z4^<N19`+Ue)_XAK&lfJp=W!<V^Lu@ypBt6SpnguRz`m$q80u|rX{29v4fA-%g?Ns;QVi)IN8-9u!!ce?!Pi3~r5>zF6Yv~2H8bva-b86%OWarNKVQ6#mwd|C$8*pzC+Tli$4BBDUmnPOrA6k(KK$w}@y)NPxNf-|X!kqkkpA9O%u8;i@f=ZckNB38iRdT0dt%&u--zp0Uxadohhsj;w+{J_8zIlRmIXDjKiRlKd_7?}_Ibm*A$^`dk&o9<jJq}u@Lc(2H1c`wgn9T>d+b9_4i?{<>?retwyqTBhgAbne!GTrQ2}_~bnXv-$55F!ER`ytKR9)PzqKdY#d8<-+wVHTZ!$&h*A~zk<0!u;%74GO^nb0hALiQ@f1sRa{W1S9?}7Wf+zR(KI!5ZpoPPxOyQw7n<ssOg?>UI|u5e-0bJ8f8XDn@M;6A(xApf^paL#jiGS-0uc~Q>AdGK7&>;>ATf&=nNsg3qJR2BWC_s1=A-7DwOUY9@NoX7ti{DkFL*H+iVJUR5T_|_U4o|^)SNIhHDoIv{Mtaxr5c3<k*9Fhdz^*;JrqXHN&j{D%(EGYApJ-Hh8V+Z5KH`mm~ypg{L=KoLONMElP_7BBgVV`qh8T|1XW!^C2H)5VYwFLR}93}bNZu?1kv&%g3jRx;<u5}OlUh9Dn<P&GdJe;xx`S0|C?>Geg|LJzD3tK(K*P|B6^Q?97H0(ECcEEMx!Z4rY*o=PKqOSP%2N`hQvi3EuJG(0KagC65)86U==Dk@Jaott7<-YU;_TN7FQU2z$P!De=VZU@cBd&WXC!Ukz+{D+0+}SMYU(CY!%m**b&pwyn=XJ(9m=n*ZM&v^AEq&~=-?p4cC+%yr3=`k<>w)<(sxa35>@$#$Z&&o&9pBM!pSg*zyN#83&pvrA_PyVKLq5k#qnwH9CB1ewzxY~mQ=9`_D~a}hkQwRcSHr$Psi~wlGG##iGoHvflF_CY%HKO3(wEPVe%RqK_W%D}jFa?t3t>NeG#2A`gekuHu>sPbpN9NbZ4+Pf%7Ew9QnMr<v&tIy_tv97*EolL%fdg9Ps{Ac=j(X*2U?47tZISspWKUmc-dMg&%-yU|H2)R|My(T$L%YgI|^P$Jsr;~zV%Y1oJ;Euim+WWBA+QOWgfG->ZoUrH=D%Y+6(!=eS>xLY>fD3&bH`JIZ{!cm&?RA8rHz`T3{^mnU8!P?85Wo$G?%^{5i-cGzH@#ss#G~z!356o5S$jT^8%OF>Z+X*5>789@9OoxUcF1#MfT_kovU!sDX9uQD5Z$VTy@%9ESNVs6Emjy|EVKu^RTJUCP4G-!TT`JQ?*_`dh5r*Sc0HPqm&nSLyf|zV<-+n>{!Y^U@T%_?jEm6(gfF(w96ezWMAN?!OYwVRXl(;@cb-;`@<ydC@NW79*c$ndG{b8m%y1PEHnI4{nP6!}u7qi)|3{FO2?X<XDCNW9tO}L|>Ut%-m7f?*zCY|GIZEzcj=C$GHD>qojY1_BC$T#X24d-?l0U&$%D7;eOMnif_rc0?%LVEtn@GAB(TwZ-{e=-W4z}y}v2Gw&x($v)g#?Fuxr_K5kBUzDQhw`TX!O@r{rXGN0IdQqW$0L*ZX7iu1`L1(Dz67UEk27vp=M%1_V_Gv-73&Mi^@gR*1aJ0d&ochzswAB=w3|7dj_QT}GF(9ipOU_A<autD-Uy-el}b2ip@Gy0zR+Jpq`e~O&L^VH;H;@h%%OFL@8mvLTHCSH8AK{%chV^8Am&W=F-@$WEyHQ$c;+314wVO{09#=3MO=Hc(I;_Ic(pns<(puB}jqdX;aoG-PBMEbb&$iKgid1;{+?yLLD^^$+nM$-SavMn$V$J)i$64s;MuAIjGUb`T^alS0Z;r>jRhogs!ZyjAy<{8_G4`{E+^~KkXd@|3N1Km)bT^jO<s)_ygA6+nB+WoUmu3IM(`|wo*(Vsis7GFOfh5E{U8RZGOBEI4HRi1P0*N&iE6_&%_)eZAN_hpzD3oJuEMRrR6vCi6sd8Ykn@y+l%$Uij>>tK^cD9_7+*iQ!Fdp+$&HTZGmP(QzAK)>o$75Qx6kLy)ChVe8tGt#$fEaOo-aUAW|KNHGnEr)ZQkQQi{v5(eDK9yFWJR#3;zgaJcuiXs7zNPX5^q0D)kiN!zoS%5%`9k~W5d0Pz#!Ivt(jSc%-}X2M&P$&^!}+#j4AM_>z&W#TcFe24Ef(K??uE?5+TSr~->qZC*I)OS{kh(=CdOSI3-YO480%U?oM-Caiotj8jr08Y6s#jZiopLnNXC~vxEa>pTj|9&?nYp}@W}>$-Ln{}hn5$xU-iw0`>lUfd^0!*=Lu~OV4m!`Onh62Mbhg*qcP7U|Al;(A3;4A4MV%1=nOwJGy3O=3^-S*(-!%MB%uA=Ud!*TNiC6oVh)*qY@bckXGjC2&$1HF$-Qdhe7I)Z8o93;AJHBiFJb?%JY0Nj+$xmEHW=$;k)h)2uhJpC_Z2*+Uu%GT=6^#!e>x8P!<|*&A4LDqTdl-%Xx9qxz2?jJ=JsvdF&>|l65lKti~PfJ{%KY&g!B!ENV{mI?_fUPpBv?wGZxR?6-uI?pG#RS>F-@cdp+{TIosG9;+r#fBLDSwk$;xI#n<+3lKx<Pj=*!)prh~)u0_3-!TGA$^9cNoXfNx=lDMy+9q?a1!o2z$&p(?)i*G-Zitnv@d1L+U9EtKIU&457mlx-Fx#u9CAMx0)&Zvs{yxu7ITc={(FNJe>^Jx?0(=Qd@Q_KlQx%8Ui+p1bIUfeokT-45t`dQip=REfBSeHLPSta@Ot|aBLWGT((hBM+DuIsSwbo+wm`bHh$uN*Gt!?wUlD37}v@~J!%<tUyL^Jho}@vT?K$a@#Y4vb%8QVH=jp9-=LT4oNz^IA}5<Wp@2=DlMxaDG+&MzmZv<_hMw);PDcU;I;i?anBCj}Q}pb!Ju#_<1MFbFQ8{2hMxli;AyjIVab(Z*Pz1$33Z0;+OQrx^9oh_aM=y#n;RwIG-O-3+G+IC*i*{QI89r;(PpZ>&3U69VPF3*tu?M`TfN=lD6RaXduqbEIo#bZ|`~<-$%SlML!Q81V8V4c^|-Z#`j!WC1>%?DULGlnH?|VyeKsb^56Uv-=p>VhW?xLvrWqRx(UYhm*%)HhY#Xgex#RvV$Q6HbCRNV@y#peQO{X>!jIe`zL6zf`j2fJ_OX^l;o|ET8{k}SKF(Fl;_$WJ>o8x{D~kE>bszY5O5nUAFd6etmLAAIDHPw=*T!?DQLz)!e;SW^`}_~uw@XJ{x87rvGvyNcr-uvtX6ez69X&Y@Sa4r<7v%4_1@-ZCO{83Ra(%p~(JvhH)|U+{WgKm&E$yQ1orwE7+e3Wg$yvNt6WId&c~xEU&1p-q9yy)CdRlAZ3Q7NBEcT@r7h;~j*<XCynn-D1{qkhY520nnH^WEceqWV9fBT$Od_8Cu=9xkvcz)a$y<EoE5fAi}c~8-QN{<m=^L>N;&*P=or;W`azV6|Hb4BYr>>r$-M@V^Y)|UQYKUy67tKt{M*RuA&`SyZK*dMx8NBY^v<vkyBd?Cy;tqO{-e{YWGvK9~VJ=Dd`;gV02<`^$7pRn&5;V-_K;Ung;k6BR9Lwu1wUlhjmwJJEDtWyW+2Thmy*L%Fh{C{ZmGVwoDLHl0mkM;k(zxdjMUTELtJg<nTf%L^2VcuIg4)b>WtEJ+%$dBigMs2ZwxOzf-WAQ=M|G^aO2hs(IZ@D`g?>n7ai0jTAB)%3`6YEsK81(<a?Znp?wUF`{b9|BBxh>LPeT@Cp$0gVgdwyRc`7hjv?>##V<o7#w#Mj$p#Qv(9C-!M^C&agov`GDE#gdV}+%)m+WB$ataG)ysXPgt#U%8C;jv54DeY6x<B>vm1a$RHhR`iqADGQ~33U0zV<N$Z{&vm!N*MdKwJPm&CV=s$u4}Fj4=-pk>f5rxgZ&_bJ>dhXr664)6S$tz$8Jw#e!1=A#s)6{rdn>f>`Np{46&c_c7%$Ij=FVXBw}jmb<hm2~Nj+G@K4W~9${@b+>A5_oSn_8={ai|!FXiu=5&IeE9_S~<Z;5XyGZN>tckq6KQ72k_z29yrr=|Pf=+6g7BA=A@I7fZqh;h`QE7JF<g#C{ejs2%zJEWg(#k_i^8`k|xCB(PqJ%sU9dkM-v;=(*B|5*e1N4~)P`D9y|<a4kuzE^r@MSq*uRD3<#Fr4qrbVGewXU~=PJ#Y-~H;(I$_RZ)hzNMT^%4w-|9rtB@JxBc4{qTMFvD~P)-VZ{hoVWAI`fgS%h5NO(hQF->^50Pe`}r}6A<}>PgyZ{#^-kCipQsG~hcn85yAS%$?5DGpZ}aXY=aBlYD3r6<5%EorKQXQkW4~%R?-AdKTfy^(#;Bj8xBrrSmK4T&o?mvO9){`S>qD-hehzoQ{jQCfCG}Hpr#z?V^<JVrZx<8aZvRv6*EZ4{&(}FqgC(E2ZE#=aGxYNgBg8j*CQ3OiW*FN2NN4daSqmcny6dsejNLm!^8dUI?@^2#g?jU>DZbSwM9Ob<d4qa(Iz3(5JxarSPzMrGp4bUNlK-m$$Y)D+)Mxr6yvH`jPwLa~&5nIhhQs39p7=@oS~s`FdHcvXyyw?x2>O5IWSmz!Es^=%-sm5^Z<c8R#*0^s_?C8Gao+yrBJvp*g!h3Q-{E~HJsqA?Dm!EUQM?}BFAd6ob)==M_|~11r2ku@T49~t6oC0_LVk?XEPRgXABOqGaU|B|eg4QlLxT9WE~W8a>s`LLFf<R|b2|J5=e^hQJ%DZU0Qg7zWZl;rY{dSv?rY31CAOn~X6b_Ul;2kwy+&d_AJ_}~w8LHTJy!pxnBRJ>g8#0s_-4W8vVYc#%)opb5RCaf+Yh|YaIP)(FV?N%YtwFFK94?)`<i+k`R{s<-&byeb<p<#zW>hf80Rn>Mq!_oKM(c?*M7(P_3Z-AE7}joynm+|_Bk0G@Sf!PDX6cGt8u?aagJ(4tUx}`x5@LYwZvqMuje)KK6Jqk_+IH5&keG)5#Lx{66@OHp{V~tLy$geZ|w6!r(plwGeUg5@d~uBS2(`s`X@<z>zSt5S9{}J&P;T|d(SHe;C%8xFvjn~+~V6?)|7E-osaJmwQ87;v@L!p|E+&84;*iddFoXsDUZdWHs4#Tg7+`$cfh`-en#|%gvRhsRKt5LT`hP{KM;;_G9+h&Tt6lp&q4F=!nbtBxxt)BwEF|B(|Ym!nE$oic#f{s8S7T!bi6mdSi?E(F!t|xN5e&(@&2~8dMNT~j&n1uH{L(77hNL0kpa(NTHSK^p7Cmg__oHyr2N|SYnYcVdm-IIoY$D+a-)7O^}+Mo%XM;HqjM>~cXR>1M`QG}-Q}?_%GXHdH7z&#vHeY3%+KW`#5aPvp+A+Mi1)+GC%}(O#`9_BU3k9ecn|p$=X)o;H{%?m>wBCZ9om5UIr9VkBp@H=ogSl+e)dz8-@5|dPc0QL<<*<GNIlp(R)oJO4CRU9d&{wvkWWG&>T_`UQ;j_S<6l!`ta0*?%{48Hv~be$Y5l!_`KJ`hR6jrUfB&ZxgKGR={ZooM)vEme{!@wpX=UiCx-YdRxjy+fhT`JX8sq|07itZ%3%L&U4{{xHN9rhYNAd`U;^ov;WTh9#%gINmjt<}><hRtSWEF}n^m>sk<Yv?f<Yr{wv=~dBOPxSg`X_lVc{M}vChB6c(&gk$<n0W_3DlM3jnpO7m1L#U$xFyV)PCe3vJbTy*@x^#%|v!1=b`?sf%A~>YtYr?`{W(eDdZjGFsc_hj695?xI05}V}@c^YD=;!xiqytxjy@4X@=tL)Z*mq<eb0s*PIN+IT(tIG8C6(D6T?vAy*+crPd+WVLxulP~3x|cr<kcc?A3MXoli&>Jf4{c{fAxJ?dMsQq_;|@v~wlhT`(nX5{kZrc_^YQ?l1D{a*1P>P+fb@=Wq7>Rj?%j)7GS#oHK)_fa>I_mK}#x0AQC-ydQqKFCnK>z8q|i=lV}Lva*!2|0=!%1}Ix8blsP_NMxfeK=0M8HyWF^N<^mi!c<w=2%i=<~7I84)SYqGBu2xOx{QxM&3xCOYKgcOP-V#gQ%^j-N~)Um8gx$mB_`Yu4Gq^t6~hrd8paRdC2LhImzkC8L2tQ8Ocrz#RaKF$<?TpsYS_^$<-N(>r%^-l~y6wB{!!wB{wH`p!OhlAp1~9lYPhm)NpbDc^P##c^Nr@dXJnyKF?76lB&k)OMX_Ih2yt8xje^b7KY-IR4;N#^6w1AjeZ%!id#~LQwNcUlf$Sp$zkMm)K%nl<UQ1F<ZT?!dl-t3G8CVp9wMJ2AEzE9A15bKcaf9GTd5n!Tged&#fzv><VED!48;aDlpM<OZ!i=OrFxTxlDkkFkh_rUF%*}g79khmd{By?6{mARD1M|tlgW?B$Eh31$I08MbIEf#=C?5vM{EDi3(*Y43)13GsyB5I*_+&m+KSwWT#j0aT#lTNT8x~JoSB-3tTa72Gg+f%)c*ZZ>_BxQJCL(d3zD;vi)jDOBZ^B=-Kf>by{MklYGhAxJBH%6)XHR~)yZwi9@M&I4{~Q}b8=^LABN(A)DC2&KIDPqu?)q*)Bv*5W#nLT1T}#iL5`)KC&!Xa>PxaozCu;=&J})E{8&RM{zNTFF3CAau?oc*=`|u}B<Er%F7V4drMNJ)6}2U~71@tEoUAmA>_?u@P#jBLM~)@$r|u!|C!e4mB`ZBeK0!XiP<)ztoUAm7e42cip?C*%D|rVwk{UsdBnL7SPopj(Pa{vH&L&SJkE9ypk>tVDq2$5jKGZJcK4f=>;@Z@DWTmCZwaH}}it|#_k@J$jYEU)bDOP%%{FVHSq4*|s8(C>I`6l@^Lva#y0r}_Lm&8!KFD-UbXHx$p&m{MzdXsyT>roq#>yb-P%aN7lBbOlOVkpi)%}iFRku#9fG1QME)q$)uE7_5pjiER{wFvp={FtAixFSPw6RI2e=e*g3>Pv1yZqHEMm+D7WI-T5?JdvSzA$2KP=?3ybavb#lIgWgmq4+8FB3bD}@>6nV2k3jU(%&4wDioKYHYS%L>kP$xsh!D6N0a-K$52DaN~6hR$iZnbkGh^3O;);vtaL9~sYzZ>-b_6}RvJg%OkT!NypS40R=R?`ko*@z@f7MTveE(MDdg^H;hGke)1nTw23cuqa%-lo!}Lm<P`i`6GtVYWqqGfm09ok>vMaScbp%=Ic(N<CBXvC4mD-g$p4^o@mAZgDl^o7c98X<KjwdHlcanFqZ4w!Zk1-UVq?+WD<RjF*<Rj$W)GcJCHu7%r8iwLI)EVSC<YCnQ<YD9%)cWKW<owi}<e0Q^bSo{cQ<Zm}nv<+F1389iFHx0$iN4Y^ROO$czNi15WBClzD?LPgNPfuie~4+6?xJ2KU*vqTi)oZ@p&lR~;JmYiX_T&|ZXm}{BdHt68#tFmQm2z+sEer6$uZQwsME>QIfwqmG)jZ0eq^P-<QS?!^(8CqMONxbj-gJbdXkm4Bgat3Q`?c1wk5|<$57jnW2h6TZOKYK$VxktW2jT9oyki3kYlKU)IQ`G>I`ZhveJQMrDMr4)H&3#WTnC680unbFj;8?IffcVjUX$HCC5<LQ)9_7)UDK5vQm?*^a?qKx}SQ5978=!y+T&{m>ferM}16I`iZPm?a|LMz0%86<zJ@eBFFIeH>k?LK`lUz;qUKIm4Ao6(iE!lQ?!4d0aBPo=`Duh{QO;E&Ob_9k@J&VQ2l<HyZnBc-~2fLDV_hzd^n%;rPA16=FeEpsY>_%GRN-ce5~}uFZ1&W&fiMU{4$@P;e4<3G+F6khkw@s#Xr{w#qrb~WTlY~|E@KPf38Q0r&0qQ{#~;at2ND)+JhQMcBOWs29lLdBP*RqcBOWrP9(ch|DaAJD;-I8rM9DvBr6?ER@#T`N^MT<LssfecBR&(x|3b0RjBS{rM1aQ%aUEG6{uy&uGA9LvSg)s$*$Bw)VyS+>UpLR^%>cfzt2upes=0jvMYa|o~r!x^p$?$XXSt4-<>8aO(MH8?MHr2A}ifTR%w*J<L7<kpU+6|m`3R<e%?t|zS1{jr5_lI_flVxU-57EG8E6E&LqzwTdBRtR&oPsJ#qtb8EOf#(p=;+<h%^UnW!1aO4E@uk+V=8$x5@4vyclj6qlstCo8Q;E=ks@O~^{yla=-*>*OxfiR3Qi;naoX;pF)Y#oMWIWTj`x+sSt7Q?i}x-~d(6NQ#w~Av=(rsXE!2T#=#JliHW8bPU;(Jdhep9!MVL@bB}|D2C#t)b(Vgo5@O-k(ZJK7>XxT7m_EF{i%PE{mDb9Q^-oYlZTK!sIAFLYmhz2wHS&^Q!A5|mLr!Y=cX1XE6qpFP5wuNW+SUm{Di8JRVcnj{j7miC_c$he31HqtaLB=AbB2j7I_}IKh;X^Pi{eNKvr6Y+=5(zq1c(4m+VZ=P0d7BnuVO3T!>njT!{QTLvbx?NpeY!w_4OL<XYr5)Zyed<RR4g<RRoG48@7m?d0toV~GsK&#7u$J*PU8RVe;Otw>g(xFJ1HvM0w+L+U7ULvmY&;z`t{<fR-ZlNgG7GZb5?lgU<cPpUuJpJSsZ)r0K8G0>BtxF$n!F=}aYG4c-$nwzXb@m;Fw_jehJk5ZqIpRlhVWhmavP;8@~Br82gKFI!UV<;X+?N1&@?nZ4v?nZ7%tw658KHZR^xI9C#g_@h3oBddEZE96&A+pln$yLd%skO+p*mqk~hmc#7hcXnepe`XVVSio0P<(>=ocx^q@&rTiRfggm?7ONj=3po;N^MInO71|NM4rUH*ny$A5<_uys+DYIKdVlyNv=*VNG(P##{N~1pB2Agf4fV5K|V%3N<Kzj$50$f-AvxhJ`_qFM-C+qrgkF_CU>GXBsXMV>BLanjA|kO>?_R}in}rtyHl%@tFj-sQ-_k>$s-wx*HBlGSFpX;P_L5LkRMQ0dq1ESC96>ELazh41KZVwq4>LoP@I)sb#isKSyrlQr>y*}_%_?_82L6ip1O`4PY$7ml0(@ZAq>U-)J|l7azAP_ax>O@KZfFIRClsF>vtM;4S5=Q6ZHXk6FHTt>L``^oqj6o>l9Vh#VP7-`nP${rx=P?QbWigytkDM#j~mX$o*K>+0;$s+2lRcRB|e>w}-ltJe#UMe@rW9hO`a1V>+<XbmVmWazwGx?+#$4-^fb8l9hf=i&ts!Sk)Cn@e_vPdkn=ls1L|D$k(WM$=Ar2sdvb4)!LL6FR8D|SJNUTEv{4VldqF+Qy-CUlOIxFk{^<vQ(u$cP(M&#lV7tO9~g?iq(%C)`g@<IpB$ji$e+kBsJF;3$ad-_vYmW|dVzd}{C8TMqb5@?kdw)08H&$SFOkoaFH&!jFOqLkpOJ5ppHknGpOW9D#Sf}OS{-<}JEY5({{Qs9O8@sqeTS<3$NxC}fBxlvz83uJU$#%n>%U(T_HcKUcOcTG{ig<fd38#w{TDjn<XH'

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
