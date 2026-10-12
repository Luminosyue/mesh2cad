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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_008.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_008.stl', 'source_sha256': '4e16feffcb6238f8bfdbba311d6054138ce8c5a24c42841f34ef525952838b68', 'input_faces': 868, 'input_vertices': 524, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34722214937210083, -0.48611101508140564, -0.27777761220932007], [0.0978083461523056, 0.48207199573516846, 0.27777770161628723]]}
GEOMETRY_BASE85 = 'c$}r22b2`W*2lX+6c7WtC<^E(N>CJ);DQK)VgM8|pkjbo$)XFgpn!^vU_!wFBB<c-WC0h+K};|t$w|OKaum>KdZN6iPkrj^JN3K0-L?Il^PTV8bME>7>woW5->SOZJ6*NVv3>a?@*MMXhI7H2Bi~D3=s03koIL0L9s>sU>DHs@{KEc2T<7?lE<cK6J9N6XV`ta7-+8cZ_Z~&v2GnhysN14ve%%I%x;^_17&xGyuxq~o-Ft|BWx+i~J$${WcR~Lie!E_iiyAjbG^*bq@o?h*_*2<WA-O;Qqh&s(ns3=Fm>5;Cs#QpLDtFl<m>f88MOgPHl<dmsHP<W;>*;pCe3I+Wicg;U_{TZ4`cFRlthvs&m#>NFVCM0X^`a*<&--eAmb;FvuU@@RF#C<^$JV_*RX2zA1iJI`xFyTNI`fb@Fl1|-?%m#bX;|0!ar*b)7VbY&$>^DW{kJWP(^sCdJgldg&qU2Nk$#fsUX3-8epFA^SQG7s`A=B+q|nn=KB{|GKDu6sgG084`*G0I*8HgMSo5Rno3`g)*FFDmaikygOz*0j<8*IgbiEv%*Nr9X<8-fJ&Af0sLH#&)MRiB@O{O2ms*|K&S8=-2%;X>Rqk12czv{vL#eAxsM0f7lJ}%O~*4tABt0Lp1e!QZAE8=wLP|2Xkb*(zFb^oV#%kX?r4`up6Pg>X2bx&G(2KCT4IxbyDhxtr*?X)v@-+rIJFMMCC?oB?Nn}=lepVowRr`7p6J?p)`I;<xTA8F=cMfFvYc=YVmleaF5(Vg$USsK=Z=UeSDD<l1@K4E{PpWr^tb24E)RnXznoWJelt&x7v?K~6c-nY?w9Q2Hpf4W*-vtGla^Psx7ecqO^o>Kk8d0Upn>G$q@H>@WX7v$D4WzE0p$rjx<h4t(r^h>&JS{9=_t@7WB=sj!Z^o+IcY1O%}ZC&qcPj%`??`zdP)w!=dtF98{uX+;QBmXk`$v>@$)ftzqJ3q{v5!SVCbzM}?v^08#b+PrNU*~bUQ)t$!jDF_+$zeT3oogMco=|;x^;OGabmyGWFGS{9>)fyZa6iHG<nI2@MCL)`&m6Nd(!bWfeO=Y9>v~$}_PA8H<|n8_YrTRx{D)bW>{UB*zYo1iW6XWh{K8prdS+jTsk!;xKRu^ASG1g+yMEK}-wf+s8>46Me%XpYV|vbS#jEc0HSvx&$@H@(m8;9-n2+9!)4fq|MB|J1n&*ohkDehuTfcuKf9JAK=Y;hj|E<%e<nWDNk$LdGoIgKK&rE1MA-8^Cw2sct{%hukb?x7oxN%}M-pqp?uX>Vr=dNavdB`+tIzLYL+SPqIqB9R!J09I>Z{o8LSIg<iI(>4_-&AYn2i-wWGC!H8%bR|tKE5HhUMmmGjMEdHUMY^~tJmeepE;|nc=QbM+3Jh8hWp9v`)F>Q?k$@7T12Ox#AjB#_P^M~XX;Gd8aH0m?eRJfncqJ_Jxuy|QJn4!x%>%fr+**0HCzwbMJ*PEb*%^Ql~bRI#&cgRj>bD}&|f9~GH+{m-4nx3TNI}|1FDRU=&XCvj@No9GV#eS?IZbkRhO2;=~;Khw6N|y^_QuKylA}Y-Vr9=xu;%q9XnTD5T`pE-Wea!bsg<^^yEeppS`Gt(a&q2`~8|3IiMs~AA8L7u<i`+^<gfb$D;9pKF-7^TAv!7hvy4t$LY!8RbLP5!90wM#;fj(H1W>W`?rMiOb;A8D^Ab8{#_(K$a7FMUiHjW6YssfdrP=J^?9he{XBGzeSJ&#zQ}YM^HQAdt?BbzSP$xa+<WO*{kUO|<#5SMTf+Bac6{-|INdASGe4|r{@zu`FOJib%L;POf%GxMw?x+E*D0}jCeb1t)`Ru>EgB!_wTZu?U1VKSRsNb2r#n@KPYLU~E{S8J@xgi#?`>~r`qAgiNu%D1)q8g>%GK5O)1ve6-j2m#J@|dJec`ZZJo9742hX1!Cf=!1!}O!inV)Abj@1`D=|yyX{@C&Q{8?z?(~I`x-XnwGFI_HQ7^^S&>G_DxbHKCXRe#&Wr@kMzIXqscu;;uu-7D-lDXa(2w|>$1;Qk$G;+;C)=J2{_mKV>B(-SW?PKWiN9#%x-RnHQi9+GGJnY4FZE}!iyXN2`k^Vf3m$sOolPumoikF9Gys@wV4y5^IqFm6-aeA>Fsr|R~6+PcnX;<k31;_9J{PCW#=RS#u!t%t9U*%VjLWpwH}(5-s5b*<+_qVlHL`w_j&{TRes_oM38{g`U;%f?(k*7Ko^&hsHXYv0E3x(ClIOAnq`=w+T)mafmM%)#j!Bl+{ZwRL^os%}4T%ji6BQ}gaKy1sw0U!l70Gh~*VeTE>O_ofW{C#pNV*C%-2Poigdk52KPu6jz}bFKI+@1be>S6%mKG#}N2eVDf9dt?xA?YG#v?zbeZ@g{iB4f;pd{U2M`{U6nJ|0KzKdN5vn-{ieJxUSA8@9(PXK8eFVLolDbhw45<8J+!vK-YZ_YyLfS-QP&4&bnkTG1pZ+fu7;Is_VXlj#qWvPw*J8>S^6)*lxy~u+~@SKVhw}$2=#jy4C%Jgtd-N!_hB<_2B)TeU*egZ@lj(?D^6CUe&4Rr0(}xx@W~}oqLC7&S(|VgMFT)S+6qsA(N+L&p&ypuJ?;mXaD4I|H1sTzhUdnS!O>Z=wI(6=FPF^pZykFcN&=emSDX4JQ>*knaFsp{Ty3&3eEmckdLmT)xX|%Nh_aVpU0X9z3-CNJOuZnH4pk6bAF7jm+DD>y(05Wog{aDFi-UC+~{-9vGi1E-NU-BW7fZ4!g}!B^XosX2hZ(lP9_qs&nr7#$J@{JpPG3^<oA@mAKALTAE|D?AKALTA30<4jBda0SbFfjgI?x+$JTk@N#|EG<F(#*Y+c`XRJY%EY(0428U51+qetIQZC&3_Rkz<yZ9RBDEjhFyJkR=mT}J2qT6O#Vx{S{Ib*jcErXOp6z}9ttAkeM-0bAGo0cZ5q4dHpy_g~e^><2b|Au?~eA7bmeAELUwA7bmlen??Gqg(qqwyyg*fo|>R*t+iLc-3n~#;f~Ls@wZfrSZ}Is6e;&qmsXWYt9+0{V`h)_Q#gLw?4d%y1!@Zy1y6b*8ZNY>;7J<gzp7<9;fH;=t<5i)0~?JI_Hnsr=sy$J!jPOee|^ItIRpF>cR6(|4u;rN6&CBsd}PR-xldd&n2zv>bazzr>m~#k9uAo<bR6M^?X0bN6($@c|cEcejW6$=a~HcKoGCzsQUK_s&l@avUHudte(qjypGG(bshCw-p+?}=RntUSN%StI{5_Oe=Oaz;<Zk69)kFgzAQ%fm>*krnsaWh>!|18dOoi8p!ywV9fN+fK3T^=uUtBx;eLYi@qcr!UA8_W@yXKj@s2G+y8eBI{=J7|)uG*gP=|UxZs|@T=i}Bo27hm0uWz&HyansaI%eOn=AV945B|P|d~Dt6XYx@!_<I%3{Z+T`U)6)ZCm}xb>tiOLQO9qT`AVHUYG$17J^M#-SofZukkg&1H_VOGy{)^_k$%>VHRsT^+Rl&Dlke`H80ly5o?IPg&gi@#PWMV)c`>XfH=VvUE<Vuh_(m&@Zsil`c0SvZ=J&EaUUX+$biA1lM;g6)bUp+9IWwQhU%Q#>TIV~empRYceMaQ>PH>)O>A`uH>h^h-rR#ZCs^Q{wIo&$Hvvobc3v}!J&erw(&S_Yj)9v#|)$Q}g()j54qpj=tW2)C9>*D59^)mDMT4!@z>-^N#_53t*+;?lk^PuOywyx*Dfo`4u+In#Qd+w)eBlE*~wCeWxb!mL`{My#_{5pBu`bhu!eNuJ%`=r;+TN|DSJ%6`#J%7*s+S|N$TF(<(*XN1q_VdKn^?4HXV?9r7U7sgGKi2ca*7bR!y8S#UqucS;^Q4S!=VLujY+auxs@u<#GP*ub&VL~H``oL)a!+plORCOo71ERQ2JV%1LiNLgjJ{+=F5bCv_`_k{L(iUgLL}a4Yx=R{ljv#UGjH@V`!4669?2)rKd-(olFtu4jDCZOcdn*?^dx$akH$|i{Wxu`cy!Gtv8%uNzW>0K-Qj#x&vY9f$tOLipLw5HVB$3&)idatkLt-*<0JV5{h$Z=?ET!F6VAUg(!c5%^sF79+!g6Rh({0RKbtkr%kg(c#;dy5W>;jqiHSAl#^!@wCLfKr^U-)KpXBmW=f>rux}8t5C~s!m{Ht!yzv}k<2mM&{pDIthRS&A$^^iJLcY0hs2f9_y2@l<>XVvX`4&tqP4&tqPPJLCeIPQK|-M-&b4;)n-cfYG{-|wp1_j}Nfb-yQvo<FTsOg^gH`FJC)HT!?od<MEbpW~ao*(zqeRJYeFJ8D)A?RrzaO#PP>Er^R(-Hvy94l=q`|Ek;d@BLYBajTg6RNb!6%<JVB$BkF@GW9w5SF>+w)sO0Bo`*%hy%jhAfo{#e_fVy`TgB9m>URC8Zr4xHkNx}N7y7a4NA*bkbd3D#j{POm4qs5;al|S)c}~xQ&_C@EQGOKT|7k~`#{a8-+L7Nh|Nr|>J1Um*ll1LK@F;jW-^%+|5v&CN({-G`T;mrkPwanu{)cP)e-I;lk8dCOwio;u{-JN%(YB)t-{{*W{G0Fz|G>93_}AbQzRI`N_*df-zTUSD_&4AazSXyF__yH`zQebj_;=zHzRS1W_;=$Ip7rf>{Ga0!{&(NL#{V@w;s5aM2mC+a6Mo3IAMyW)Pxv>!eT)BFe8Ru*Z9o3~_`YGD_u}7+Px!CC{o>p2m~gk8!GFQUgjWC$!^MOj4gLfd6J8noCtOVU5#Y~oG2ssQZ@8H7-+cSjw=KSXh6z6iu7e+he+90De+B;@Tmk<c{vEg${vG^Fa5MZ%_yO<}_yPDn-+KFL50vKtcn^G(?|a6#CEz>o&GO9fZ7a9}UgF!EXm6qmpWxfe_+Q2+{2AZI;2(oe_-Nmr#s4fm;S+s(1^+AfgwOPC7XDfIgfI7PCH|H8gm3X}8~$zhgdg<nEBs&K6W+uh^Tn?53w}lH<vzc{HU2Az5q_C(ZCvATgHL#4-<slYick0fzppPH;}>j7>}KZm0Qe>RUf&9QD*}7L9|nhjz2Gl`<G{i2*L-`)w@1JS;g7%vfqmcw@D$h^K7yQ{0*m0!gAaq6<0SA!P;;C|PGiAG;A7!WgM;9M$m3qH0KR~n-Ugq7zYjhSYL0WjNucJqhMbmxW8ur-?}AUmHK!5az3|V->0|J1_;&DpP;*=j&H**YP2{u_Tn66>{}g-|t~o6LN5HRhO-@&VAHy$o4Q{8cIc@+~gPP-ha%$xo+zA&G-WL26t~q@ME`S%iCZ|`xtKipzmx7w(=Z?V*pyqh4YjU~~lss<4giiw7!ZoMsz|Y|GT$9su@D=z=;Ps&9SRa(Ut`FsSiEDD22;K;v2!8{d1lOF3!Rz32$!Qum9X=j>3Dg{$f%QSnvAJt<ngC9OPk_$=-+*gQ^T1;GRC0P5oCfa*jt4cze6Sg)Ii5pKH-Ho1H^5&7XTUY5x!^o_2XeX+d>P&X><DU(^}u{kbNs?FIkhCW8{jSBSA(y@HK(cIT=+i6<n$4ECHzCjU<=xsV-~F*ZOw6`V{+O7N*+6C3;zVX8m>8Y0H?y|J0_<k;79QHzz;#qaXpv?HOCJelhaag2Ye~~9q<#l=Clv&0DsgmIXww3fj<Yn2WpP1!1bW!IG3DW0GGmFfR6&-foo3l!F}+1$Y}uhB>W-pIZ$()4Xy$;$I0Y04157T3_cJX1=pM&1?R(4<kS-!03QrK1Zs}2g0n%*aXdK<1&6_h!h3@Qozm}sqqycMauGg`YrhKWHKm^ixsKpV@IJJAgG1r+eWZZg3mB*HA@~M^I@U3My}aj|@1BD1z@PJNscZa8@d<yyw+#LaKH+11TaJG@KH<;%whaF=e8Qjg?S1_3;}bsGw|DWsi%<B|zP*kAZG6I?^6f4BZ{ZXEgl~)RFTyAMG2a&8Uw}{eNV$jc&&MbHao-l=Ux-imlfEs+zZjoz`98k{{}Oz{W!>ca);h<04_oV)??3C%=g}5@4!US-Xp6oYU9?TKMc;rf+J4%ie~vDi{BHalU4BokLzCZ8(iXiLx@hvdq8WNVx@hvu&PT6@F4`BgMbC0w(KgZ+eLcEpAJ7(k6}o71X|Lt}T8B27_FC?Xb!g*hujL+k3Ez0M7tv?>xxMCF2_}3p*d9I^-VWUD7~T%P3lqK&Tm)YT9|=AN9|<o6`@sdf!3*Jc`8LD1H+;LuHQ2~Ce7eu4`F5de@B-KH>BLV1XN2M!;crA=)A`&*eD)$@w9gs%XK;PtvwchYHV14CALrZOe0vdm9X^h@zk#zuajo&U#y5`7&A~qhpY}N$|7?818~S#>Z^e$msgB_de14vM&N2A9V|WAN&jTBV;-=!CN?#55Trr<5CPw>gh`%A%7v9&mDZbqers2bVd%!mjydOTCxCg+#p|~{uG``_{?r!{d<I_I-;_r*^e(LoaYFRK1m)h!1tqJyrPbQ`Wd=oCUy_Z@Rd<$O4XGemM!%O(=OmG%_5ubewd?IvjJkEV1xEMZ@&%Opufj`D)`+@htUn8bHcrAP(eeMGH!29vpZeS01dp;}U7L+mX#wRg%f!*Qq*@<X^qv104%g9~ua=47Kgj@tOaJkMF=0<QiT*lIboCFV&myAR9EM#p355RknLwE2Q_$+dm0ycrm9L{7MGa18u<h7aHHZyO+r8XL~wv8E^@VChM32-J{YGVRxJApAj&KM3d?t_eZFKe@h`rX5rw3ZKWeZj`mX?MohADjUH&bRM<`xE>J{7<;!8vFq+CcHfOcet4F3gFjpG2w^NzJVWx{|tT${~7)(Cj39XT_9ui?LzQ6_=WI`FyW2Bo8XP$O~G5>P2tVKX7J|lOTm`#OX01-%iyiyS1?7g<$8;2u(NBp_>Lr2umW82Ifm;C9uJo>cXQ1g2o}I)j1J?LpNepq|032$uzzT+ZedLXJHus7Z^nN!IsQOS6&S1F5%62ctr>VCT-GP$ntTPj!7n7Y3&5k`QV)ZumqFwzTxzcqwI+Bo{8Dmg4wetC&xx#q;7M?)rJG!nmtYEh0Xeh-E5W4>AD~VjASdB+Uvwug!A|hz<j@o>2X9FZmw~6irRMK&O<saG!P}9;b>LZWssCQC$*UJR9p)Nxtwx{=m;3Y{@)hh3zl<EN0FQ+Kotpd_yaRq6Iot#u1DBeU+WQ&o1#d(S7l963>h2zDPf+r6xEIQE&GO8J@*`*;!I~+rK)V99rTj?Rg5BIwehTeV$W{4Cv`=DAm7hraL~20!@w5d8xuyIV+JZ%HDL;$$S&UzKCEAr(8|6pQK8o5>UXgZ1?g8ZvZTY#`E#)q4!CSazj+UH!I~H`|$HGqlkAR;5uLl0)7+wut9sCzuO!z6_FK{v8wZPxuV#1GdjR~*h<JCTP@a<agM)<Yx8!+Kbz?<Ps;Q8RK@O=0s;O+2B;7RZfcoN<Q><VuKzsk4cd^<t<a}D0+8ZN%mh!v~}mwf7ReZh0!GUh(af#5@M8Dka3Em#>Y^FNUF5%fZ9bt`KkcpF^S^gjIe5hJ_}xh28s@LS34cJN%dtj}Gp$@eaD6@D$bT@9WNmwLFLdbyumt5JJ})LJ1q2~U#4C1ADC`kc!;2%Zm@TIxdGbRnnTx%TPQj^LSasl&n4>0olI&VA9By!w)p@Jq-cA3Onm2RU>FPlZd(-${)Nc7b;wha17O;ZpxYxj%-Ilkj}5)dV~aF866a^6f{i!n=~gRp4pxpQy=yfp@}hB!`>9dhnyDy;|T<coTBC0jvV|$m0a?Sbc6VUvkZA%!Tsmw5zjb%4^cDNsTE#jkaJPx0IhsTks*bl%G#qaHw0#&!sIm*e&Jf&=$PkE#>uS3l4Nk`PsD3X8g*}q%GLbE#;@v7VPVm^2)RY3*Ay)g|^^*ZYe*Gw&1PYGnIY&OMGBC*Kjf6Rl!4!;Z@;z;E!-I;U|Otgo_D375q0`On6Q3H@KMaimox?fB4qcw`+WB4_*&%5ATQxZwz*VH-=vfc7|UJZvoy0Zvk%w-U)97zZ~oWzZ`z0++Q+JzV&bo-tHPMzFNcz)__Ysb-BJ^eYlMIVdg;aLAZ?ZXvQsA8!q!dob?fWB(zpNSQEk9;j*R!@DCuzL*!J0u?n6H?@VsDfeqlYKD}L&Z*Ow_gPdx!Zh{H8)Wf6H%cJC)NA2B9t=&s*!dsC;3otLVJ`Gq0!Smo!OI@iO!QSw;<Zumm23+cJ1a&%soKEJxxSPE0Ca1r+b{@5p$68;^wa=pt1RKJo=6h1(f?eU)ki+$09k|s05blp5<RtuJuGJVk7B2VcF!CKn&ceHp!<Aqy_>a`&Kf#{x>&c-LSQlQA+N%i;fj1_Hj^NSoN64cpcpSVc^Cj2JV=k1RO#5WkOnD93HK;A+wP@Gk9#P(qw%~(qDL;?4;1IWzH=r#z!Y$?XX$wB;mh!r^1&6z(ybkR;j9>W~v;~K`r9449L2W6oO}jStg7Twj3l4Bg`LVPGdvMR3;ae5o&IFH#p9!xGo(QiEKMOnweir;}@JRUC@H$`(cpZ3M@HBW``01GNgl`?&yXErA|4;vwcIl7&4s;^_v9|rm=$~nZKe^BEEBK?$j_oVRJDmTbST47*)>gg|I{yWeJ-1;'

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
