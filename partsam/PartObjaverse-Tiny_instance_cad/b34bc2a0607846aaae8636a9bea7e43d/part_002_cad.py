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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_002.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_002.stl', 'source_sha256': '266c0e0401e8e14b594ee2a9297fa99dc47f332050c3742a667af1f102eb5b81', 'input_faces': 1128, 'input_vertices': 796, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17790964245796204, -0.22168734669685364, -0.1615927666425705], [0.18588706851005554, -0.21548667550086975, 0.21152788400650024]]}
GEOMETRY_BASE85 = 'c$}r2d3+65*vBUlOYQsKxNR*_yP~uzW8Yf)zD^La@3k)@wxXKYso;hXLP#WtM3NDSecx*xRP9QsQp(%soZsBebKO7Q&-?m(exKhrPfyRBdFGij_s*QTZCZN!6jbEDPm~HLt1NJ|R1{K9rJyo4aMYNAeFH~V9yVfvmy%b+>7V6`TXp=dO;;~vtTL%wzrfLbN0s}^QLb+P+T|)b%Jm;UYRssBVZDcs>K91yCILf62mTu$Js@C2;J<(SeOaegMaLKAD>|k){*V8%|2qUVCF4Nqzi#APdX(HTY{^!C8r$ZLEUp(y+D>u(^lTP4`izPd@%tK!tJQttD6V>aE#kV>-fLOBXg}D8#g)dN?V`Am=XQp@ALUBbZKD18;~A_U@9n!qd};=3Z+sUMBewfElEuwR&31_XhlH|z9JOlg5$$`-V{s+7DaNlH9m3-3lW{vm`vdJ|++RB;w(}?@QH<w(9o|oa9CDn&Ie9<1)xDzs8d+J~xpYl}=>Ib>KK`c1W&VBdrHeSW>&!bt=Ku5a>GpoK`_;sFjAAEQdv!`FxnEufSbH@-Em>^$;w~0f9wdq5rSx9M+wVJ&B({5Ibvnz#<*wp5D&r=z_Ga4#sUjXWijTADOOYSL7{K~*=IkuT6WElGCw`GQUizn1SbO#Ay%f>U7~gbOhnM3;J?NE7^6^Ae72`Kjvh)0$?I`L*Is5m1*1w~^A^OSo*M3%qZC;6d8h<@yac92c;`pkK5AuErj1=QkI<8^u)p^-P|Hi$sJbwDR-0tRP`|aa2iq00t-Kg{Bes-R&sUVN<k7fCIip>}KH?o%D{g*y1k8eg!zFz~v#dcNWd76Fvdhq0ZqMyq@u(%r9PPA7Bk4t0ykEtfw>(0?>>^!~FMdVqnKY;aPXa&+l|9|vh{TKti<TxEYL|n;_{e9%zE&k5hp0zh8Z4u|G@$lh3Px&<R-r8s1uF@b)j8mO?jm1^}C^?>*m-gAWtEOE{5bc()*=Ij4TJg{2yjOcMYj5URwo9}d8p6h7*0?D4OU*K!#kJNm<$RdZTK1!2oNv4nML%y_vG)48!7|UgzGdS#^0ZI$6jv73-7or|pPTh>oI4=$sUACIu=ZWwi2c%&(hSyqjbD=Zd&^$d-n?}}_J1#l_oGD1`LoAvgB_P^w`HDN#`5-;UdiK<c{^)wZtNxJjnJ8fJ<rD5N8-2`r5dquDtC9v{12?k+N&EH>=mBrQ?^~TZHIKxzi%Nv&aeB*{c4zl#kES`%RFyXSX{4oP8?se!k?*ZoTUqh<LFrXG}Yc-(dLQcu06ZK;?5!s#C5^ZZXD~!oOf9qFZ1Ubsce52w@()TU*%k>tR7N-5&LEOyi2k7<IKNpr)byYZVDSu_uFEB9nTN3xDotJ?62}LBgMX5)yr4ZgLBI86i>(995Rsg<7hNc97kur{%kx(<@X8l_y@4|>JMea{I6yFlgy4|P<PSJ%>97HjSa`daaYn$B(r?p=$aww>gYNaHxv4Z{5YbPCA0my?kDTy_T*&yerZ1s6Zz4OjOOF1w=rJy_fr+#&x3#Vi0wDHv)A5_<8?Oq`QfWud)fZ_H512O*>;V^^|P}?oj8hJ*vs~}_Crw*Mz>TsUMpU_v#f)zp}e2>zlc0&=X$faap{)KLz`Z#f7Q3V+@E7T_Okt|n=I-_X<dcwm-+hxSwDMTC9(FOzZ3QEtoR~{_5W@|obc4uti5sjwx|cK`vehJ5!Wx57U!E*J}8Ne|M6pyPe-=yN$hx`e)K-yvA7Z`=M%GSQ?^|_<-DjLwSIlpUTxIofT*9BW!U(Qp5<k|R>{f6qpj>L>n-X^qP-vI%K(vQ=gRYm_U&r7<3#=FxA(EQe&?;+UdWh4w%wEsJH)td_GNMXr>mmgl!l)t+ViFqSs~}C!P!~=%C*CCKJoiQ{C}!-o*v8)`>W)=zlY_s*J<%N%K1cY$Er8=ZXr=`TH7;wSUnH%5ywSYoW$bV%bKFjjd=;Ie@DsVB5!(@-FsLb4(${5X5^Z`hwX2fe?<Lh(`U2(t$9xkYQ_4|vTPRhrq8Ls;zsfXkr(aRiv)YzIdwy<7+3N03HE%N2eQb|0h3nAxHbMaH4lpYy}OvTcaFt%!f#4~ef&z_czK<gI3$7P;bgq{JZawPm%#SxYJG8B9Hm;axOVKO$g`HaG4DU}H*x-|U8=G6&I4^ko}EoAu<a^Ga?9^W{(d|UXQD-YYMY<!W_38=q^M7$#z7WWwyl-**<<`}dmhyO!{z6X4&U!){ny(NBm6|8-S)b2MvX97+}htN8)csB=VNib_im9NbKXC@Sbc6iEzVOl;K?p_-0!W~X^*?EoBk{0_mL`BSzJGUP~^>cw0{@NXN)1wi&`<e?0HbfCd+wq{7TkdTYXpLS$VOXjYsdYLe!^YYCRS=Pc0F3Xe=nSi=Eeho)-C3z4Ec`>R~gsi+-xV*lBNXTsP(XIr#EUcD`?TFY@V}zk8=WZ$_mgabBx!*Rl3mrtG4<*>uEC`+n&)rpWJQ`-kmh<H;6{>*!F{-Z7wvoL7AVcCzC#Y_6y`HL))5KkpiGUKkZWV*NY%&J^`##a-9;5r#Z3A}__WJh$E=>dmaajm6cZz0u-$Zrd8q&i7H3)8u(Go5hu$--!G>vW<wh=S?rx-e7U-{4L(~kQo1+8Z52_^_2N+Qz@REM}=3(>&t{(@vPnkmXzP`TEC04$Bj%ua(;MmmBpQx8;N>WI-iMS=kJTr;&0<Y6l<>?94x=@A6~=SE2m{0>ferJajV``vw567pUUMww}}3~svBp|kG5`>$fwz@7>k=lSIT@Yc`xS=>wKKHRpiZ?_00}@d&luD^7H-mhb*p^o-02ezs%TS&$FIAM&#KjyLktz!_SiC{R%CFZC6{pOXSnoJc+f}9S=l4wTJz7u=Bm$RPnc2u@!5t_!bd$>*!yDwKp*D>CZmm@s%;64vl<wV_80*R)`Yg`s!e;y$&7k&&%)I*Eg`ZI{SAyKR7~S?fYf^`d;Kyn?EO()oqHm%>Vh(JU*kO$g`TIb1bXd=uEPoE=^+X`>Q^wEWUR;9{IBEDz&r7{NFCY+B+YFih0AF_E(HO59Sy1<o*wT7Q^yCCQZ%*nU2J;^S941QHT1nb*vwC`8838j?`clSMmgI678eEi(&PX>l1N*MC((X#huR^i#%(K3&pUy@@sln)X)6<F)aV1ddTnLp)a=E`%%6hBR>!1NSEWa^3!sfykGHm@^*XP9M77IJS$&(zn$fwYAsQ>`i)Mkz4^YC%yXaeti9vtP*JzKU%~D6JZKA-$Z`9pZe#UUFGSYiv<chT`Mxx}s6)puby<6((wdDT?zcADzQ0DZK#@;#;ecp+ew<T6L_QsbzUJ-A?38uuQ!|?7A!>ohvvaH$>&NJSOy+agyRG(o8h1{}`&9RjZ?*Shj0%<W@W!26?fKEhUJ?0pULV5Z#)jf4_PBN2&ABV&=a9B_wz7J=qsr^=^v7H5`O%BV$ocSa6pt_ZQq-ZN?zk=XevEG~MhHK<EXtlAZS;D1A24Wm6wBw~Ut~Tnf6d~K1TT5N>~!rYdmhwlCqzEA!!@JW`P-nByuTEfkN4B1v^Xx#;x9L|_PAeaUc9#1-oN(Zg2=PlH;%V|n<4V4{WgoWHw)a7*TD(BHnV(g>LQM}mROX<jdy3o-$sF}n^+x&^b>WcEZ???weOQ_z36Y;{78E~^#xZ%J{_fpM%u@ztQ{`%P-0LdtG5Op%lRSFpT*T5zLR-gRwt6>xmBJcqTXhG5oxbab^l_KH)r)itRF|6u_Djf-ParK<1yQfl-H@02OI5msEqws97p}mDi$|aSCDnSZpKD?e$>80Wu3if$l}VC7h)V*|GX@2)}9;A;?{9luu#;eV@_m*eVooZsUmMquW=FVygrvx-j{zpI)dfF@2<#$b}5LpSNCdi-WaU1_C|-?vfdDP&CkVumi1rWFM{QN!8aoR=KG=%_B<=a56SsC;Kq8Ew?A6QdFJS*^{jr%%6c_cE?aN!UkT_g>%7wN_3XU1>dh_g$dlR0;?{LxcOjYITi3(w`>QR>BksRB0%KWRJz7WP*}OZ0#TBKW%+I7A;r9G!IckgiD}y_+_69yrn$25;+w)^KUn0+oI*nLA#)CT|&*~GuaQkuB&W;e*7w55(tiAK^VzT|-!r}J3IkFEH$3+|Y#%Ujq<C_fe`P1|{=VZqvdYm{eju*$BEYCMrin?`=D~G*S+vC=KdnNqNJbw>yN6f`_p5l6!dz(DQ&&}My#^ZioxW%pW$kmT)p7~*lzlXRwe#T-?apjXGD?P=vgf(kD#dRNZgQvK$_30K*ai{Wno5y~llvsP*^*Q8Sws=o*r{98|9^1Fex7%a;$x9PF#y1v|_xCz2VfCPvo-gOOxz*R$+bhp|%jXNRw^y_CrRoCtJnPbu)%N!4mOb)w*Zan-y>j}v{GL_ruQ1lWrJww~+G-Pv>lwk~bE$S@T$uel(uemD=bd9t?=V)k-@jgIkGtx#^rTRK4{_~s_XtmMXYi0HPjP)|y%>-Eq^8B%<F5M~1&+phiW}dw-sLeKbauC=xS4b%(H?hQXD`a<qpm!-&3o=~>w4`Tx8_gRep&hdE@-5`hq(Ic+)Ph#=dt<AJjJy!VPT%)=B)PN9{aD{FVa(7zc41+WBh)TIF>i-d|cRB+!rz%HD&eVm|IHZ&G|)rp3f_T<@IjLyHz4?9pCtca$Z&Eud<&n&H)i({xk~uvbc6PQJhD*fA|VEp4Kt)IoFDQE7*B-_J%l*lv|&$_Ijs0^1A=|jpg?Cjxc}ue0g-(a(jET-gR*vsmFS=xN@YPxQ-ZwK3;CGTWfxHk6ZJz6?fG$<|X&Id1`f%J?=hlyT`40+dXbwUp|O``fQm!?wYsX73t{jDUSKyJ#IMVb;><%T^By+2iFDnxOH7{k6YJ;54MZzf_vP$E_~1rt_vT;aeZ{<-|f2K9=EOwAGF7H;e$A?3&#Aa%k1Zcp-dF>t=ZLgnf*LcJNzlnqas;Ydo{3&h$}B&FSWNfPesf7RQk!K>^ySp5$BgWXAFz$cTUUCjSGtLc+>-VpJe^zh4#8Nj@?_F>LIQ)8QR@ryp^2aK8WLb@j-mHoUh#D)^)@^Ze2&*<JLU(K^)f?EABpTyT`40+dXbw2VMQU&D-vAYu<K`EB%&*d5T-}vwPgS4!Xy!`B~|j7-Fvz$Ml8r`%A5DEUx7FRIV#JGdILuKU)2TqOR11BYAtD-{t+fgMK0QI??W)5p|{4UjCCkt|UK`^Y-C<GHxB;RRv^xX5G2sZ@16AR@}ATX@VK*DQ<lpcJ<>v@43ZY^PAO=HO}>KM|q4}^PYR$n)g-|m|@SGGBjL%UK*cu2FrhJV~=s?jUzJ81#btleqL9V_enx_1l#kbZhIuZ56)~G%+Av#`DA>;)9EZezplu$st%vR^42V7eyXQ9&Qtfej(WD@?&pPj+&V8@{aEue<_-6_^6cYj9^=jAe4-AF8_4P~`&L=czXh|n89KmY+;RWyevk1dqvZT~+!$cbv(`^JD$b*%cR}`inuDv!IuEZKWN&YN(_iNK&m)?rx^<6R^=8H0ugf3AQMaysto($po#io(y8R%Ix^)&WI?&%%Z(9ECB5zjQ{d2w*cdwrh;y8}3{;liOfFII5#r60q9^=l3yZ5vH-Rj3ZZq<o<-1=Ott!^g!w~lYawnse0^)3aDvbZ(BRSuE&sqP=q?fJ2eixqc2zOJ}6pQ9e!<JNKfAdcgxbqWf$kH@Mv<LYuAM}4XRhgjUIXXDPRVEb{m&I?!E?L2aiTjz_KE%OX}+&Ui}CtA<9=fOH&?s4mLf-CMij<T*kh@-B|$RB=U#|!hD5_|tA`~JG-!=x4=_P8~FstqQE*z;h`w~mc#S==>myTz?}+c>Z#gyjMAzux7+BK!Wjj=L3iKkn{v)Q|b5!&3YBt?Q;5x17guoi!(#EN)$wjq5(k*f?<=*OYuL?z-+*|7;n{4?ZV28<c15t<M!&V%Zh!_~JOa;%>*$84<XO9WQ*&RM!|hj?bm$@)BY8xb->Kk+Vq{t6O~TbyjK@W*@)xIoTXBh{y4{+E_Q4_2c>+USZ&BkH@RfPN%&Nt?!}6mWM2EeQ$L(FB8t%<9n{Up-H%XyVmz&J-T@~t3!N`R!(+gaqGT>`ZR#|gZnmWK;nA)cCGtPTHe1|+`2!h9jqH+k6ZUS9hVwJu=>Y+QD>t;EN<OjH9L%mV8;dbW6jyYEN<P`RX6P2$m$vQrIn$XBkghP{<fLjKa$la?uR>Tw2EZ=Yu!H|+dtC2UF&|kd3yot$GUIt%(a@uUHAW=?%T}9gXa|b;k;37{CKWmeDie_J74g8L=W%H+FQ?A%pHMIY&>`_qm&C}{aDX&jNn)nx1I-S&$eu3$Jcs3b;~>2zFq4%mp<alXf{qfFVnB~V(qQxZq7Ra(X2l4oK79Rl=Wjh*HdroWpV2{pyR=!?JS?xbICuSZ?})%dhV(2D-gr-faj;ioJukFeyr!MYG_s79?xg>R!w7AJ>z+<v9b?~ThD*>@9V{~eBwE^!&|;r<l3(Fyt~zcSXQ5SZf=Bbh_#Q$dd_aH*u?s`p39p-8LYka9AAwyc|UmWZ$69NVeiMaZXw5m9qhPc{e$C5mN-^FSTEsNSe(bPzCtPcX&lP~)?=u@)@JRk^&6&tw>VZOSnuHs{50O)k88ckn=bM8ak|#M+@2cG`o}sMJ=aexZmp{^RxV=wyVl`oTjTBHvDWQq>PZ&2*7-O)E)@5BT=x~RPRZHH5b+PzJ3TzOljRxfqm<m<yI4N4&dL?H`o}se$FX9py|rFTkN0PBYkim6Sds5<S@Sm5r)h`1cH75kt!Gm@*WAs<iFI*~g)Mfo^9AeZ%n?Ibd)K<VFX!xL=Zm#YZ}BG9k88bO-G&MF@wnC*)*PN-&$G2&(HR<=VDH~r59w?Yk-*Lute;fRT})u-3)W$};@19R9i|zOV-Kq<Yn|uznS1QxbgdWdnZC!KXKOvGTJVx=Z=LU0zp6d_YY(d*tb;Wkl}%*h#5!B&^va1W&sdl1EH!|&x7P703*`HJu5n^LuwzcKB(`0wE7l75Cb4?JI%G#^%OqAm)_Ud_!;@J4v0hrQJS&Nf6YH+cX30tHxMTgc`P)mrU99(Z-0!fL#j$SO+&*ltef-w?bFJoD7Pr=`JKiR+eysKFO4D<!y|o_R)N&@<_sd$JZ=_dEX8mA2znL;W*?xRo?*(*_?<2aN3*bEhrPDLkkM%x+<MJP@z3csj-k+tg`p5eYy4Eg*osW1w!s$CO#XcS<-luRbNlRhd#d{pe{XD5G4|pHM++IGF?HAr3QBK!n?XCAsjKcveZoQx4EI1{V<qhw%IFE$#{_*~cHt02rTkp|m<0~3${CH1Ce_P35d9&W@Df<nJTkip>vzoDftoMf0;%#_8)_VI>eOY_!y(FdLEEc!kW73PJ8*Kb|PfFF#u(&=gM6Q25aL%xwUpn5yGQzL3xb@zaGV385r}dtf{^&K&58eyY*X7!0k2~-lnO>k3i(BuVsgruJxbx8nxsLY4#C`0zU&MQDH*^+vy$4rmHgAvj>GXO(^6ldNJH6O49&fl%u6xdXiN#I4-=~+m$;YWSm+M^X6i#Eu5$_MW$F27V^=U;}+<Fhus9!9N9e2F9sD}EoxKU!TT;H73gT<})C6#l5Y3#Tc{Y<WV9~j2kJ6e4y^PCXQ+B@)`rjj)>jnxC*>(m!-;roU6K=oleS$hrdjjBO6S^wsV{<8k{2W&k0&DUbRpOLx5e%Ai2mt2>=uFQVc9`CWL>DBhL{9EtCK34a$@mTNG_H4)6JMbQ^KDImSUo*>!JR5_C@$JrylItdKtYG7GY&j;^*G^u~`w8wN-#0kBg~iqJiE>?F!(=ud>wRHm_IcLc`Tae)zPZ^2wqMqJ$4cG%ti96fpjgji<bKNA<Gp5OPvLa?_?5WIa-HkplIg78f=kNtBBCshH##TRlMPnW+4*R_f8C@7@Ba^{ti!iGd3;Bst>XX7)sOYBSN~N$H@O(Z`^S6VYL-wwo<YauI`~5}?y6h7KduI@;{CrrDerGjjo|Ubo^qY##6;GQf%nsutf_4L#;~s9xEmeQ`8ctjQ+;!qk8|Zk@%&Ydy~FxfHsJmG_YZjcJ)`CN#SO1m{|>yruk3oq$6tTEtdsU1$@grmJk+=$pBLWCn_=Is1HTWT4#}UvwwvXWT({h?I*TiN=B~HLU3H7!A259Dvi^1aUV*wrmE*D6uRcCU^z*tg>&N=t1HEo9)?UeZaICDazzlo-^~(Rq^QdDGAO8%wKHiGE<_G-Vf^l;&8>fcfXHX)B@co@KPp;oOK8cT~Su20huA9#Kv3~!-m=VIZYyDn?9=3w@<NAGx-Ya?kXJRIb_R(v2KJhyhs!t@#gSw=oSdXHI$Fk#Y{oaL9CXVmdmxblJ-lx0RcD3HS=8AT|9%k+JK_lh*_>D(cd)M!5Y&*{Pt8QMozGBxYmIv$iI`qsJc>b;5_b7ao^<(t>N!&lu``u*wrThAd^#MwiJ8s9Nu~@&MG<(APnbc0)FVi2tVf`2#CW>_(%0%UWeSg(@RW_vB;;#Mrxv;!H80>w(zF*ewmMB~EAF%gtt+!F;lw|!VqgsmR&`R@<SwBwvE{f8p>;e1nHMXu5^Q7@zE!N)peHGpD4eMX;c2himRUWErzw{hmtP}AY?fLle`z^-rU0K}vy%#01C)+Q@=USlf5hGdL`rR0P;S@H0H9bYH`z<t$_jBRr!J?gSFyG&Oqs4ke)hmRxcl};Xm*ofS^<(1qZPe{+dHWM>#PcD2(N>;+>vwVj<5=AEI~yY6YBH~f@&n~MEyP{xD7;>Y`<{A<gM7RDK9|oYo*ZZUrSCr{*Ow#inm6!!K33dy9IK{@`@hEN%Y2-_50=jf!mhKp(fdbnU)z}Tgty1KJHz=G&;R;<i-gbgIcPub*6$9fZ;Kve^%HeduD8xr>LBZ<QtuzcehvBjAUj|1yGHtiCM>QD%`{&0*P#vT$NGIF<IA3WyW{T2b-?F?ct56EN&H=51dF?Vf2rzR9-nw&g4nP6AuMkFj+5SJ72B@bBvH<*zlE`JIuj;{c~Tu6&iXN;`-yqR2#ew4tdL#Ihw6qno}b4x<b0whv$#2-vzW(JpH$v|=}h8ziBaY#8;?%w)7r3K*Gm88%sH(l-KtQOkCcK+{{Y)hYf+H?S?>9#wFcJsU;VUJwQALC|NnklD|@&XolF0gAw)a_A`XVH0Fy5V2ZN_W#G~QMz~pPeqro~vJPN)POuhs>3Oo%Wo(f+BCSMJn3Z4QHPlhiBlWze}28Th!G4Mn%`EhUzcn?H;41N(zegk|Ad;uc93cm*?e*wM<egF|ahyMd6&zwmz`CG)v{{TM+--n2=!S8~}uYj+C&qKsV;3vW4hrvg{dm-Y@@FXz#R`6!<&k*rA_)0MOSnxP-4~V!9ygQiu3veB9S%|nW{8KP_A#h=EHi-CdMS4~+`D;ZoiTDvjd>#G}Onw!79efHRPJ^ESlN;bPa2!Ou5grRBcY-&9mqWyJ;Gtl09Xtm-79t)19|`Ub?*|_VCZ7uK2ObU)PlnG2ldk|z2LAvNFM&sZ$+v@-fY(CATj6`b<cGmq!FwR$L-31W@;l%|;0qA(ukhz!@=RWme+55Nq=?_c^MT17U=nd|h}aii1x!8w><g|05eLD41e0$72Z859#1Zg#F!_FP1UL>NPJ^EVpM~Fsp97QM0pA8cg@|9npMc3<fnS3&Ws)M!4)@9=nfxPgc5pt3xF|d?n7lB!D7X|vTo(Q@n7lN&EVvRx`~|!Mn7lgp3-DJEaea6lFu4k@4{in#w}v+XlYa+p4ekgL_kgztlXnC60QZH62f_ou<O9G1!6P8zaq!__^0DA?;HePtEcj$Fc`$eu_(zC%F?<e~{3q~Y@XrwOYWPwxc^G&#I07Qx0$&d%j{<K2$3esi@Mti3EI0w20uiUfcY?|HfYZT8AmVfIWH5Oe_#F5OM0^K+5KMj?d<Xm(B7O!x2_`=eeg^&%B7Oz`1x$V&{0jUQB7O(I2`2vy{0{8pEk&Feeh*Ck2uvc*>Mcc_1^xg`eiuw4_VJb?R^Y#a$xSec_#cS)Z}?R(`6ck*;Fl2bbNB@?`5EwY@KcERA^aGa{1Esd_!dNb8NMG(o(jGUJ_`{ah3^Gtz!Twn!Q?x@iQpKBI1;`IOdbx71Un((W$+bX@(}Pca41AP7ybj7TnEnuPlt#n!pDQjM}jAUM?=Je;e){BeZYgk{UG9=@a|yp4&a{PP7rY`__tv4#^6@qrVz0|ydIeRORzt<Hbh(vUKLDU9$XFlIYj&!{8KP_3Gip&k`QqrctJ3EE^r}mZiqN5JPVlootNaS;P(*mOZcB)@`vD;;71VgO}GgrzYM+!z623xzz=}QcY`y)yCC97_$DxU2sje_6GS`+J{U~i3_J*29U}e&{u!9OAovq-0f^WKo&`+)N|EdX{u3g;3%?I0zYM+$z622;fgb~tr+|-ulOW<~cnp|)9XJ}i1|nVrUkWCl3tj}C4G~X(PXv<>15W@ChKMzIA24}mum<h~5q}H+4ouzz{4KaKL|hO44Vb(JxE{DBL|hqO2~1udTp3&eA}#|j4gMHj0$v(S{u#IgxClgC0A31AUJ_gYoEIX_4KEHRFAB~L&Iu9cfENan7X;@3e*_U{gNXA(#18nUVDitw4zM3YTn+vOnEY#SHSkvuaU*zBFnL>WBXAptxEs6&m^={N4cs3h9s?f@CJzRW0ndbp7sD5V$-}{m!RsO79q?^n@?`K1a4JN69DWo`{tNgx_zFaP5B?jN`~~<P_$5T_?IqpIOEP&*us1j_L|g)13`|}QTmtL|5x0Oh2a^v0lMe-x4+FOVw}gnlg%1alj{tuQ{thB;1s@3}{~p{5+!Z435B~v7J_p<%+yx@;44(}qp9Ss=?gSAB!pDHgXMzL49U<Zl@EKt8U~mU;KZv+Jd^(tXG`KyuFGSo9u7k-(f!l%mK*Ry?X<+iH-~g}&5x0d;0h3P#w*~ixh$q3rz~nLDN#I2g@pkwgF!?d?c5o_0d<cF4Onw!72z(kMz7Br?CVvhlzYiwA2EGnH1rZ;Fp9hm40Urb>L&VYWy<qaq;ArqFh<H5wXE6CV@OW@fi1;gb4={Nh@K@l{5OGm>SulBFa8d9_5b+yDdNwdQ-QRoz5kH2AZ@?dc$*+TNfKNlj`{Ad+<Z0mj;GGb0Bs>mGz7ZS=UI`J;gD(e@&jHT^PlAYt!pDNi2Y`oydqKqQl>hFB5;udlhIa>(_XD>EcY%ll;KRY>lfePtArSF+_zz(6CE)Sk84z&@d@Y!KD>wuk1`$WW_khU{fuq0)5b*){1u*%q-~-@u5b-VeGcfsk@GbCDi1;0x?vuWQ`+`Ztxgg?_@Je9vAaF@=MToc?d_I^w0^AKe4<cR<j{}pZf!Bj~K*amJ{=0uld<On2{4ALKHuzWY?-23d@TXw%*Wkaw-kGF`bHM4oDlvI>a1L;Oh`1O$ADFx-xER<05toCP0+W{omjhRZh-<<tfyuuB*96yvh#SJc0+ZJVHw3qUh}*)OfyrBg+k!ho#J%7h!Q?%_y}*GG@ep`lF!@065b!97cmjL`n0y>~0(crkJR3e0Og;-d8@vD_UIPCSOuiVr1iT6&UI+gfOuibt4!jv6-VTodlWzfU2k(Z64R{=wJOONg4@1PK;3;78bnq$gHHi2={0Nx*9QZ!?4~Y0R{0f--4)`_rJw%+%Tl!-#`7<zyIES|saW43uVDeXB5^-K{DdPO_w_x&jU=nd5Zz<v;aJsKr1ou}ngNuNRLBu8CS;1Lx|Fi@|TpS`U3iko~;Qnb*h`2CBTmVk@RSUrX29t>Mc}o%JhQ9=pKL?YDb9ze=e*}LDCVvPf5qo<}5x>EIzXc}041NQC0TDlep9Pa21wR4bhKMg_`tN=#@d@}ocm|j}5xft)3nJbIj{%cMg13P;Ld0v~PB8g0@LKS4h<G796ihxBybwGOBAx-C4kn)no&lZ&5s!h729pm4j{y&bi2K9)fysM<`-6K!#9iQ>z~rsKUBGQ1;^y$CU~+$Ob8rKQ_-lA=FnKlb*WeluaYgv&VDitv6~Sd7VqbVkFnJ-cFSrOqoCls8Or8~-2b>KeR^W6WR)N0+lZgL<h#$irfyr-zAA@f}#J|8Vfypz#zkt&r;+^naVDd=tPVh#Ecmez;F!><x0`NeHxGKClnEVrPRd6YYI1ju4nA``P2dqHEe<;%FJ}fc$UGN{^+Ys@2_$4s;5%78NL5MgJo&+Y31}B2IK*X!zYry1-z^lPOLB!MHv%%yOz|+CwAmTyr!C-O?JP6zyBJKe11SbC$+yUGYB5nw83?{D!ZV2{=h-<-Xg2^j`Yk{jm#1-Kcz~p7X6~Sd8;!l+S?#~hzgBOB-3??rDE(Fd45$A#z0h1R1=K^Pkh_k};g2{7(vw|~2#6IwxVDcPbA22Stf-}KC0+VM`T+@JHtJI0Df5cfJ;(YM@U~&gIAJ`WnE(iAmlUD<m16P5FYs0?+lQ#m_2G@s(Tfy6a$-9ADfxAM)LGb=y@-g5b@b?h$Eci??`C{-a@G^*a1AIN0d<S>~I36P22Tui)9|!LPpM;37!LNYH?}4v@A3(%^!C!*O>3;5C_?tL0M4TU<7ffCPoFDu#L|h*32PSU;CT|HQ{}x;xTmd4k4F3*H-U?h9Tn!>_3hxRg?+<PYZUPZEhIavzcLp~GH-d;8!aIS<1Hlc!wISjL@Qz^e4&Vmh`Vg@S?*}Gt4_3inLd5>?zF_ipV1IBeh`1iS512dvTo3#WL|hlHfyvu~>w;@S#9zaEgUKg>zXtb$h$q4qfyuXnCxRD3#M|JhVDdxYZQvA$_$d4|nEX1J{1lk{AowUa0V0lqCxgkO!BOB)h<E~g6_|WHcmlW$L|g;j6HNXUxCXckL|g=38cbdkTm+mQB7Un#{|HP@_gmjW#7`h%6aE-XegkZR&p^cK@Y7)O{or))E{J$Dd?%PZ61*9_3L^dyz7kA65Bwu|3Pd~tJ_$@d6g&dl7b5Nm?*%4r2kr=N4iT%$fA?pJ>%gl+#9u<hb>Ypx<gLMV!3`kd7Vs`$@&IrPaC?ZjCwvH)d_1@(cpyYP3O)l&9s(W(o(2&wfQNy}qreNmKSRWu;0a*z1K>^I-4JmG{2ZA47B~ZZ79ze0e+njl2fhjZ9U}e*PWN;FftLi6h;u;1#o-mf<lVr<!Jk9Kt>N>)<m<t$!E+(vb?_Zv@_pcS;8=**@cQpQFYyWZZ}2l<@?XKffuBLdZ{WX!$^Qnw0sCZ<BF+h?`@h8GIlwu=1t8+$@cdx%V&LN7PatAHxC2aH4(tc60uk4OR|b>U1lIz80}(fZ*9DU|1UCY=goxY0TY$;ig4=<+Lc|)pGnl*=SOW(^#KYi$VDcg0Vc_o};wkV^VDbszDd3q9@qG9+F!^loeDETOcqM!Rn0yI%C3p=)yaB!nOui1h0lXC=j)!jslWzydgOecQ1MuBoaszw-d>SIY0Y3~TKLx%4{v9Iz3w{kuejof7IFq*&ad!A0VDi^s5^)}HDdK|g_uw`yy)qT_{_o|i3MZ>9aQyovmy}ca?;ky1SCp}Vqs9!x+gk4bCx5NW{(tuRw=dUAUTs=trtf6`etF9zUY>ZZ(_jAsfixqx'

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
