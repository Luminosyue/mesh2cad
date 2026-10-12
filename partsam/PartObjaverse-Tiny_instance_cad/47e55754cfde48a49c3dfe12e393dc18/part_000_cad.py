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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/47e55754cfde48a49c3dfe12e393dc18/part_000.stl', 'relative_path': '47e55754cfde48a49c3dfe12e393dc18/part_000.stl', 'source_sha256': '1676a555519da725a0cc1451043562237b23fb1dcc2167028565ea706056f6cd', 'input_faces': 912, 'input_vertices': 630, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09770894795656204, 0.2723858952522278, -0.10599258542060852], [0.16414779424667358, 0.3914727568626404, -0.013335606083273888]]}
GEOMETRY_BASE85 = 'c$}r333L?2`u2N<9RX#N9U24@AYl!Agkj&pqU;c00!i3HWQkl<<c>RTs0bJka708<Kt+}W0(7=XCJEUW;G&MoRaE4<>qWr-y!AZIOndx)=R4oWIq!LXc_^x@tE#K3t15>n6RK5jqTx?_t+?XzUtb=qX%h9cCfeG#)k#Yi#jWX{xbh*Jc9-(ykEyRtnm%#LY@4=Ldn6<_Zq1_AA%pag$oK&vVR}gX1FMr($0ROzV0CPq_@iSI*2MY!HA`Yv#`%8^?boMgnBJ#LnEt5#|M;h_zX*C#wbZjx7GL=Jp(2q{@5#^ln#>fXzFx|AMMfxJTXXhrec$W{jwmf^R4%@A(E4}fXV>g8%6Aq0Sth=F&<hsdDALM<eaF@zhgALr_aOcFq{AxTt^JhmDCl7EU0WI`-^g#Gd@brK{AVf;D8DdE`L1alPN{sJKCXOMVUF^h(^@KDdu9{-{69)nJ#^jnL9p*DEK%u=sn<`ce4p62U(}s%M?T#Ok^YI@f9pHeH+To-tf_oo_uU@``|kXD%6D{Mt9<Q|#C__z`FG;FJ-$)C`@tD+qkcLfeeVsb9<{YY=!c_zdd)!nKG<FP&Vugr=OF!>O?y$FA<EZ#KdgMm>VC>MzNmje)!Ssdx?gQ|XXU%TxT)IRG5JT;Z}e4d|JHY}y!DpV|5f>pw5Z+c-<_L*_8PR|sLKCjYx=P$&%l0v@#C!ifr9PoIu}n@s`{Lir}B60Kd5}?#UsjhO*)DGz5fN}J1!njzH`!HlyiUdcJ$k3svkOrmL5|-?~9_}3jKNLMfh*mLq5ell&?AL$5sCB=+{)emHmnSJZkj`RgT?J%6FC3s!-`iKdyY=t}v!=tbE7lZOYeY%|5CAeZds;pH@5f1pCf&>(P$w!&JSyXT>SsQMey|NE+IE)>7sB@;f1)rmf#p*PHd2^0lIJqz|8_`k!ysv&cXHy6XR0yRmQJxjuyQ6xmP@5m(W_XQ#r?E5h^Ac->BQpL4!OKE>TF<A6T*rt<Z?w^e#~ohzyywYhapsdhT|H2QPsWmSIH-1^FQ7L3C4+wS07!M;)Gh2OKfDvx7s3*?hu8~1g0!kfXqR(zK#k840ZRUYTu_Q=QkiYkwzMoO|OPjtBQeR&0_hgPAg|GDS(LOvyPRX#pPy@Tq$qQ|lPE|jO)&NqX7N8x)YPwVO^fAmD$mv;l|P22xkuy1%b<GQssqJKwE$92u;rBS3i*f$C*F+Oxi!gCwF>Qr!hIYO_ZKBFH*c?!CsKeWi*g?t`md6ui|I&Z$SO_hJ%v&g^X8T9ATThut~oVOk2@j6k?KbkT9F62`juF@Of(W+m$=DmsQdRL;JZ!F#x?7O^cl<&In4~y^2*YLdGIpB5Gj`QATIg>2u1O7wG*KfYI4dpz9dhq@e^?c(5^FPM&&$X0ao1e<^Jdgf)^DErf{B%pZ=(lR&xt*7de&XGZ^tVDRzTth{;``>EWBT1F&#nH-cg`<?Upx!-)~8@Uu3Le8a%Ui)>$On+`4>>1dHYchf6ja@*f;X3P|liHl9B(vnf^o6zqXO-zf-=R|2_N`P1HE!oBspTpFsXvvP$os{|o)&C{Md3Zv^|!(xZ6Zqnf<0>T|(=QU7^qD!sveZp^=l`^}w<{&xMht--#LmxcUo=T&-rfh|pyBQFE(WlKSQ&aa_-ckV<>KBjLzU(R|PcUaQrW#fKrxt4rfc^-@JT+lEL<ten3$F-mZ{W7$p?TW>Bmpq~BK_3{2`OJbgEay11%k{5RIo%7|TYTStt1SNQcC`PF`d`pj`C9%LD5t%)YF}f)y~=mwe~tFCH@Eoig8MjbG~a3Ur(@h`G}hw#3Zn7cHA%Mkj=~QyzBO9!4)%@0ix}UUWnsK^4nzGH^u|1=UdoPOUoYs3@u&WIi|;BPg!k#lt7=^JEf~f7x`zH^4^0mCefh0$Uv+Y~TYbFm+;u~D1pDrD&!GIRHtzmA-_dHF#dn>14)xG_zr{DsJ&*FYPQkpyIT863RmXdwbrX#9&ih#YA1&n%_&@!vZ@#}AHGfyW+c_KUp4$oO|1;**VBeYlizOe^*9(uJeH%uo_HsJsA^*Y?xUWW0Xh&xZ{ZsT~-6&5S?yE2pe&d}M-&N>AJv2UO@g02cyE??G_mR)J6!li}G@gqI1&4!uSLtE2`_P^EzKB_c@|XFLzRU0rP|gS8=N-T}(BXGA{^&6e!S}AlbJU>u>&X96)LYRd)F<aZTFg@@XVDe-cSqxW9rGgk5659g$WhFrVs^pLX^iLb>f+78zN6?5OaH%}zO(}QbQz8Lf6M{gZ&6LWPn+LR>D@7hn13@%{zl9(_(hnvI9hbX_#AT@^_kNY&-=GyHY1;O*7M`&hhf##`&V0-4WIK^N6TpDQ^ImyKs}GVp`JVU!hfUQihClTR#_^&W8v3q-#$p+x?K6%qMNv{vOCl~*4OP<wAVu0X_db8Al_@erm6Rub5T>}8^x2*PufJ{d0Es(`R<%r=+9UF@ro+XqE5=!bABmN>AwoG_`c#9C}*2#Dj#D}IQ==e-?j<Lcf^jub<3)$a=OPwp&u?9r+jCQ4fX$3GnKzHcH-&acGUWBQQv`D?0vYel0>v)yEK)*9y=T5FEwyqT{o$EaK$cV{x?+l^)IVlR_Ws&g<tX*-kbW>w}O2a-y?4QhVp%}k6C<|{xj+=ZY!=^@;vH6uZQn~xLqiJSwnTduJAb@2K&zPzNiO&hq~epC|}FDsLH8*(M*-o7k3Eh%WmPigUjDVJ|Ds_eGm21DNH>tTD%waQy#AJcTU=(<^zuS3#^B0Du3VS$ln$J8LnHpALVa965plq-@z{{L;hW()%UQzxXu}r^NPyH$avr-)n1ERz%LI`*EKjlcQ5Xue3vIvrFWlsU=z}ZGoLTu8~?HRzLGa_zpaj{er_!8rF?hUAL#$xpTu|5;)%-FE9Rm9_Z))tjwQ2^f5mi^r%Sx*5BidM$lr4b^?YWsx~_Xk%o#ktyKr5OC#LTzyICIGUXCSkmh{eMX)3*M$tqm8^bq_O5qN%=KFj*)fO7WUi|29aE6AsO624DIMPU79=~mWHg({~b?WGrkeWN59`8WR=@BO8_;Fp%;d2bVi=W*!)<vTow(f?D6UQp#+`XTFi8``}&=AZ7R$LPD^x0q(}jq=IpS6tt4Ec3EFThJ~XC-r3&xNg~X_#L9rua<p`cJvgW-BaFI<#8?h4%aOoi}vcDrJi@ka@$#Ty^2RH<C|-F!?SoEUqpMgOhP>`ZwkNS36!%>sVb*?d5g2b{ZKo8=L^BUUasT1onrCcS>8tZj*2A9c;#5$Mftw$9V#E^M-M!Y@(etSdUy`^%XI@s!gS@k&F{EYX&AQ?X5+p*X?Tu~OnyGtH%eZ@bJzN^O7BdV$MPiNz6KXy9WNn{`Q!a=@O@$WM)@d}UhkT)59L{k>y|vl_e%lFv*J;tFRjG5ea}veV+oHbU#r}PaV+BQk5v9EcA-3;6ia<NR~$h7l(oZkyM$pKZN)M870Fm{nHa6cCHIO{=I=)O?i;ZFmUx==ycPYQ{nl8K&U#pe_6kqHcW&axXh+XcYrmrJt9TXZhnA~(jwA82zfJE;{Eq$VVbnvL2#oWIKOlYOJE;G@^Hn{#Pt-F|pKC4eLEni+2Cn-e`faaR^}K5-cPn2nNkTtq8;j@kM05C_4=_Hbz5imc?<iS^{?qnJ=HHtB8q0fDOX<k+tj74zHVN<Fl&;D*vNxl@aU9lD!jx~0+j^f2^}IM!x+8y%8`{|(n}U63Wg6-;v@7OUDLvtro<Vs!MdCS1>5Y6Uk70Zpk%e`elzvF>IfQYE<FM&FDpOI<{dRwZe1@a^l^Lkd9=Gs5O^IUq5AdA!jlw!|$|U8R>wdm&<*FYVDf4k%jwi0Z%T)fplz7yG=N<Hi%$L-AO;26I_KLU6Hyo)e(Z1#PBcEPTSO-g83%@cC<?ny-Blr(1-<|yu=22gSyd3QND$Dr(8ie;(s*Cmiwq-tG`g%zW#s|IptzciPszSSr-g^lC)5yQriT<WvQt92P8=22S%lyZc`rO~9H&S0f`729szXLkH8|?ckKgM;t?#BExbsO@p+>L(Ke=pYYQ<Hh!dFUtlW#+$w^}h$>>gC0#pOgDh52f#*JRt|)hJT#>;R5P;z}-iKeZA^3%F}B##{ZKB^WTm7|MIJsgMGc~JCw6q=?C!h*nj?m`U#K1KEcUCOFJ5z5Bp9QGyh!}uQ-o2eMi*~=>L&Fqux$dBLAx2a9wks<>V)<|NC&i?OWr$dFn@8w|oHZt4}%R52t=bKE+XZ4{}}lwqJDv*A1(yo)`Vp@Bd5s>;FgJQS}wZ?SbQu!mpl={A;T9e0{<tRes}C1Ng;bE%~@lHBr7VdmEnjZ$t2%b*eSeS3HUP8W5)HM@wsq^i_AM{I#J6vCnl%SH4m5GTJ5d=eOZ^Wd3+x_`aRF8To`FJ;y!w)qhxgGrjA!AEtb#=Q!Gz>zsO8Pu{PF{fj;qF;1rShVMCMN$*VSmyUk21^wZ>cQyz6MpaXlj}aC5K75Dey86u%+k$;Z)h`&|20pCn-<39&_0v}6<K}$ZNE?s*`5t$7--&*k7G=rbc{68Quz&lxzIPhxIc)~6TO7&nf=Jbl`ssMf{c5+kPD@`q-yHis;qmBirxTQ~d-fsyjWM{d(}~Q#KgO{R`0n_tZ(cXx53r=yPp`yvb3R2qH%xvV=~wf94_WTl^v&`+ZvBRJ?9)joXXSo8j{}Ds4fY-9!_e--Vh_S!$NR$k!NqlH(>LcozKGUp+;gAa$ny93%Y8k^eq}@cgZ80)Pj9m1ul<R2Z1?HS7T@tF*0Fu3ccL9RZ!tpa?F;su=X;``Oumfu;WKV)`Trb)_1-i4QBKaUbnYK%XAa}OJe8==J43NAaOSAB-6OhxgnW)8AJ0d49=T3#oGHL{i#uD!2h(?#o<;liIEww+GsUQ%^P};+jKDgHai)^}{|<}~gA0$szli&-Jb`hK<A!$DhxA4FSgvdOX8riOA5s0*cjj~UpCc$g*Wpe7ulWT0j(^GjOVm$s2aH$kJJSD#^?45MTR&N?mpaehVm@s-{x{hh?3?o$SKmnVtFu~0a5<e^pEu6d&IqnIU+5sb*Ur|pq<3?@-F>zJ(pS|$I}SgH@AtFKm9Le=S;yP69WD7d>{y34eP2}*<TLmho+G2T^7RYRD9@<%_|7#VkiPsr+}EHjShqL&S@L&r9o}gS`CH#*42OTd8?M_o5%Wf4B<{<TigH%NI<4s&JTKug=RZai)1Sq7UOQQ>ZyUxWr1xZ_o~tiO4))z1kHvQxQ*ghf2Q1^TVcd`OMR#)Eh53)$n3fUTAAHp}CI|awdI#rYK4S*U-_TNipD`x`&mF(ZYUZ+>(M(^T^E%8Mwe<OD-<%8R58Q|K8BX?};i%6Z*YI2zu}qJ38%NFaD!rZ_kL%`qiF)Avm!7^1^-#GB^R%H^`2I>?&Gf&coV5mQxBCCJ_<DL0>!A+DH*?*OzJ9(H#(~JX>YRWxeJ$=crzX~EYt3T*>yQuEIRpNB`VG1NyUyZk7iMAn>5}*X@^>-+7T6Esez7zCN%n_y)KA^tv5%boH0~=q5&f3?q^|UhD1UAU_PN;KOy61dJ;uYnc#pW!Ux1(eAo|IzW_aGyH=(_9`(quoPRjOR-;p~I_eI~Az8U2&o?@9-o4)xSp%2c(xSGBN*UcS``!)A{(zoG$vme9r!u?GnJsE!P{ix?U=W*U3V+YD}VFmitm`jI{kDL7p>x#aX19k`dzT9b+d`#a_^)1RdqTnF%-^=u~uphyFC}+kI<nMV4<*YVV^-o8}QPjV85%RB}tJ3Qk$Js6&upWNrSiJ8tQjm{#CVZZwFnw3iP3&`--`yE!=-<G84ZqW!83yWy^Lg_<>&VDp`Da`5cV%SZe!1V_;JSe`!^8fsWBw4?_88LVqP>c4VIPX?2Cj@kj&E28bMZMf{oC`LfpgIA8O0p;&Le%3jXQ&VSJCg-2W-prfBL?XS1~T}e2Y7ylH*B#mA|9k4t#fKoTonk{bBS@oF~ip1m*EQjOU_J=+0o@I6uNN57#n%thf1=debs5qaM7E;<;#y{Z?Pbm#m*(&@No(F@5*>NhoK}mMVWe^NMBM^VM2{aVhgE^M3;Uhx@i#<~5Y({2b&HJ_GaN%pc)%KTB(tg!S9ZpIQEe@HuYinZNSA8Hf7exj0AWb<`Wbn{>`|oS8Q`4n(5=w>ZBG>2IN&Rd&lbY5Mww2Y4=PFTO`I?V0Llb6<wzhBLEfCi;JzrJSbkyznr_$*~=A4luLs-=;S*>nYz|d@tUETrV;*@5;pUi2X#Z!Id4szE*Y~^Jjklx-%QW&)bRmZ&`ac(zirDIX~ci#Pd|9@5^a}`e8pYGTS0O&qw*ped^2($~Vt@80NlnR!64ierTIq<!f1;;TL^_=b|;%R~=bBkq^gVN8Q>xEWS6vQa`tS?vol^H`cRyqu$K#HO|wVSrNEy)ff0qH0NDe{giK%&$4{iII{+@oYyd(w7$x64nqD_e{!D5c~sUA)EmboXQPqsU|%o#H}~<e?(NEQ;JQ^UE%OI=*2qls&ta(Nc1Pa|_RVujW<9vFMx$SykFdOd-C1K<o~alg>NejI>^r=x{*ur5%;4wReD4@pQ7C7g7yX>)yG&m%Z*N(b@MTRwJ|+LedpQj2iteoYnGepZxEf7!2m9tZJ=6DPO+&ve`V9Nm+`llgW-uR|!!dZ?!<`k4df+)R^S*pp^Vy#pAbr!0ZwC8X{spub&kq<`PS($Z)^Rd>A=7^hzwuEw{CK8c`<L|aU6om!C*b=_&rU+U@m!Oe<<Ya(A-#7UeDj<heWUPSJQo*+ewgjT{qj7p`|enk-j)40?ziv)o-dx8GJU<c8^#mvUpTX$gwOY*HX7d@uI#5-p7oada%OMDbvaJn{%*>C4%f}QjQVe0@Mf^DS0v!M<NAp!`vpFaSclYl97q4p-o$o%)N)<Z_vP2ext(Ta{`3n!$MePW1Fr0s(XR@tFyG)lpy`|K;^z0bk-eGy7W-umuJgOIx1jz@Gx43mb!^kuD);ic4C@j`_BOT`&OJJtUu8Lyk-vGKkmnvvUn^*V`)Xbt=O40npnh`0(Y_ovG|z74<Fd{h>1*b>bndI_o_)xtAPnU(&sSvcXZ@7&TqyQuHP1oRC(jLPZR%kj<vEV@1;csn2;;Wty9!2foGiEaj;imm&ck&H|92P5|CD8(Z2D$9x?4mtpOeTxzZS0BrZwh`o;3L8y68Zh({_0>*ngg}%;!ztS6PU5=Q@wmlf`-{w7f@Lo?N6ah(Wuw8HsV&lZW~|w*=)e=XIV!T=!fe=eG$KUoT1Ec^mBanZBd)J(P#*fo@MR$8DTH^qK3!^xfWPE%#-3O6fm`^tIu;J>|%!^b^c8&3znCCDNaJ0{6x5MAJ9V|M<8+e%t5y83*?%{PSJb|3>tG&NB_qB|cvUzGt}}sO5YDKkqc&BloP|8|?eeC8Pd%Zp7#D;W;|D1LIix>U)EIt?+e}-#mYE+u!*Y|FWh38yyn%2K!pYBFnnHBj+2=Ti(I=W1iop@8s`g=pCZ4?~rqi?YIx^Xr8;y`5yUHZb$z#*RgYcM0%b>c5>fe&$*6zsMv(^3_XhZYL1qrelF;V=WFE8c#d-HS!j2RC%%xZw=I5QI?{KFu=vi3)p#Fqzr*xh6&uiA6D}Xdb!);eA7R-)a^=)kzE(0F@Au9L*vHJNt9+g3Kh5#Y^tE$SE$9DTISrI=c(<XRYhgXXopTq`SIkE_&HbR9Cb+Ni3EVGUdnDM`Dq>O2@#_yGpS$7bC0p`0a+)Kbk_~tsx$kfK=6M)Lw@US1^X0Tg{d2zR=o*W4;~X97i?I%A@Z5{(>*YPrAIyEgoDT50-sR)Iyf3FS>bcC0e!~4((>Kq<xcYyBb>rMnl>gi#C{K93cY^)f=fQeoKV8oaV>=GC>_2L`-I1Q>z<vA<HGOA!m}S4!^j+mW@xC5&5Wnw~+Y{yC?+5vKu3pRSjr%Qbg7K&O3(9xqMxx#Mdr$7JoAJGtI|TQe??Zc;zXy>!9M>&&@V$I+f3R<!`_j2@Zu;&r8|tm!9-PO>9f|x4_wo0MqW1^;Mp=E!zPT%RJp0ccl&2=v*-T$AS%G%sIULhBO3%UPISO}fl%+i8c>q`LB-B68N4a@!&B&dC`z`2)az@}g&h#DUR^dI)bE@v#8OX<+4@dmW^mACxW#}jUccNeAM&rK9KEwFKa~ekOeBSRq^oN?wF|Y7C*{|}^jy#v*%Z+DxjFaw~wedafU4nKgS%&odeJ;~CN=tb@?QxuA@h(IC@b^J{gD+v7$D6?WU5NYTd3DX3i2CPurFmV`*GgYQKI5k0Jd$@M>a#Q*^&HU>&yjaE^LZEZf1YPHeP?lRJV(PYo;$rs9QR_;4@X6!|9jV>oSe@agPz2>Bd?3?yPe-b*Rd|@eH`g?dm{ZEvvvgg#<^E;zeD%FXGveW2km8^*Ya*e`l1H7ukiVpKX^Cez6#o*-G?<f80@<WGm!tt>W6}T2hU6Rcn;9*O-8%qj>Y@>jsZJ@eHYh-d_4DM`i|nRC=bt7`n<bQpM}S9U7j~Kyl&Pf_D!^2IG5=2?#F%c_sg^~Snu+A528M~esy~tAnyqB&r8L7hx-Cr-cd_=jP85zzRNq#ddB?6&EE&n^HPvL?-b^x)z_gv<fZX`zejn(aK6r&cZT(uV!1Czo&lfp9L?PC$SdaiZX^0F*T)?BKk~W<k-o-$q|di!BcJ@h?{`eG{5J1`2dl~*-Q-o}pABkFwD_2yU*#23{+RmrzskEb;{WPbc?b6D{r~%`ybsznEy*9N8Nv@RgcBITv#D#yv&l0U!uK(RCo_acF@(dZ%gN#7E)3y%4B<N%!ggvL*-pM?LkRzBLkNFkLkRzyI-e{de2H3R14{^BWC#~Bg!37~21EEL^&I&q`3OV!J%;dG4B>6mv*c~$%?#le7{bpogrA|FBtJubk|F#AL)b<AknAEq$`F2pA^b4)9rDBEhZw?Z8Nv@Tgx64akk^n`GlW+%gqJgfmoS7EQ(q!4CdV>_7czuns2j;K<arF?ISk=h4B`72!s8giqZq=&sgIL~lZW}En?HK^V<5FRS#%It^j`A4{C5MXkCR3JNfwPD4<vV^hLS})lSK!RyODb{2Jrf#W5|QZ!x&?N?rTiYy^mpih)xfxpXovMHa)05rw7&Zbk@CSd{A4&2enarP&*1IGK4o!pC@l1?_>z4Qr{(~lFu`Qf1&1)e<9bkLw_Pm2)C!Uw1Xvt2Qq}Cs6)w7<Y<QQLaI()NM1&rKwd^pq%I*Rl2<W=S5k+NMPtY-$t$S6$fEa?SCE%7gq_s?*uYNmENXo_SVDLbLwGntxGzJv6E({Q?nG{3M+n>O2;m<X!XHzgCVx!MWC*{{5Kd+YuVV<$X9!QE4kk||I~c-Y4B^%c;ri6;8n{0B7DM<~hVWMm;Y-x-$(P85)EsglIfWtoE;WrTdVu^cIhpzvS#%RQnfx?Ecoy|Z@+|T&>Pqr3a(`+Bxj(r(LpY4un;b^&$`B5v_9TarL#VyTA>_`~KIG2iE)3yr)PCe{<Zy;?51D)UV~{@vQ~Q$p^6v*z`;iBeXHxr+MW>TRpCQjA&!=uAi^h>fW67fP$f9$|qW6(S$CJnN9_CXAll%JnVLyLNW%Ref>r3wCkG53#xfOpFZpoj6L;Uaj`Cju!4L=X@$4q~WraH-^$&(nuNetmb4B@TRndGhH$NaI|A1C~=l=>KXDR}~QCV3{yG=U-9o!X4to!rnLpZM?Nzy7#M74Igs8CgQO4ntU{4j~WWJ?jkNp43U?p5(dIB(ms><hf)wLpXz)L{4JeWiW)VP`8q=kV~kKkso6{mN10xvLl4Qr?;CdT1x(&T-y#kMwSr%!XH<u*$m<B)MMoB<P{9zr>LdmQeOKhhHx}>DLI-vf;xdbfo(j3A>4u5klcY>k1B0nk3S3l#QyLJS@d7zpU77k!j)7H`5ZNu>LKTnvl+q}4B^uZ;WG^3OzOYLnPe|RxS0A0xtM%`A^bV@Ci!#n*9_s`snXYf=g-2m7{X1cI$3A`Zo&|5&kzo02uD)qk|W7c4B-V-H+cd1Ifn2@4B;Y%@MUTS`7-$?L%5M0dW9?@+}e&1Zf8dbccqq)OZeP$WeE3X2uD!mnTg=f!u{<C;XYJ(e)=$kyEBA4Q|0;T%%6qZ+7ZHc+5^v?u!QiR4B`JWgnwiRf5#C1oFVL^W|Mv73WjhlLpYrwe1^K6e1`lsLwFZM_%(*`7KZSv4B>w;gdboCCs0?A6UfUL!f_1Y84TfR4B`82cux+s;XNrjo-8_<Jeg^yQdf{gpCXG!+XC-g;r`SSWYG@f{^VBFdSvtc+ngbMH$%8CL%605@8lbNFN@l3VA1O2>P%aM+KSwY*R4VQiTV7*F|G#xPWU^9@HY(MD-7W;8NwH-mE?=$^9<o~hHzQX7%Dv6A0s)h5gkQd<d5zCc#8Ta`6=>N>Ot~W@*C8T$ZwDjQw{QAaw@fioJuaBeo8JN`=~#XedOP$wQb<v$eIm$7g-}Wptc}4Acs)<kVD90sZ+>f$%`1mtNgK^I-5F$Jexd{+J`)n+?Cpb+?CvhdKbA3xhb_axhc6CRqCP|e-{3k_46tDXYyrg3HdU)ifWLn$obTd$ob^6)Pv-+<P+34$tTDkQn!;oBp+f3ze-(17M((VmHa$)1bH|03F-*4=n(P~<aN}0$?M1~7{UWJe49+w@J%B+S_^#R2zR3n)dJr^!d<A5THw1$xHENt7WlRj4xtXz0^ef7q11b|z_*)lSLzTg@U15tMjfFAz6XW7Q>SQw??>VO)J0n08&h}~^(igzO)5N#x>XB&!wNr5eM1X;^9m<Z4{L$%V&QkGsaoKhS~!JTpas6ig$t=ZE%41Qe2My-7Wl>&HrD}!f2GRvZ>|*x-=a3K1=bUU>(dLd1=bvd&2<UkFzQ%aVC_QKT+<MqNL^$Lta}KXYa_z4UXo0Gow|tpI{6KT@E+<a@*eU&hVX%)@#p|U_#i|00~_XeqR&y++XC}I;RV#$w!mCbIEp&b7MNQKM^d}m0`pJdaB3S{V7@Bcp4!wFn9~Y3p;og6=DotTs4{+;b7o<gM~hz80`qF&uc=j9U>+{~IW=Dk%+-Z2P|s?CxxH{P^@J9f{|kGmA8LW`1>sEUAuaGtAuQh<r>UnH!p9lHA5agGKOpa;zDgE-p1hy>4&$%<HbZz1^?9;6Zth_S@1j0I-bLQQ5Pppzyp6h!yp6ntA^ZwM_$BHJ@=N3w8N$yogrD`tKm4)59|_cdl0{u)(Z|T5kCPu~9tqSHWYK|S(E;SO)FkQvvS=hZiTof#csX?_c{zC*LwKn_9-t;thmu7{lM~5n7{aR=!jCY7AEizuKT3X>A^Z?Scojo<2}5`>LpYuxywD#p)Vb8DWYHdE(Z1vus*@qSfFT@B?Msd(&t?eEU<glR2;a{Tp3D%QL>)w)M4reHj$#N;U<i+62#=*Y$YaT4sH4cG{;2Rr7PW{hnn%teAEl;~MNg8ClHa2qBa0p(i@r~OkGzw*m%QE|FZknShVW*F@axo_<k!h=>R$43|G0W8C~~M>{L#rD9jW(_JCYkw+mS^ZlPg$XA5%Xge@y;@A^dNK@VC_ekiRAWz!3h0A^ZpRPx2pRn++j+hYcZoCsoRLC(GKHEc>mpFDrYnUVnV;4-Z558nuoce2v`D4!wumklc;hgWQcgh&q5gh&+-ymOPR?l{$qyl{}9+lRS?cOPx!OB`>DVAulG!Q>T&R$&08H$&1Jfs3XV=$kY9CUFy@XU)d1CnjIQK*2vANk>uv&Q0jPcD7hbXI(a&;+m9jKfg#+JI+5Iyd@pqx`ChVvI*05akEYHgk0y_!&Loc`kD*Q>k0B4EjwKHx52g+v4<?6EdyvD(9jW(_JCfT_>yX=!t5K!zR^!jYU$Q@Y$zPHSI9Dv<Jh6!02aJNCxux&{s@E2ne+rv(RN*~Tk1a5d6*lL(!ZQC&roK=0*aG{H!sfoD@W<3^w!q${u(`h}EPI}!@=Th0pu*<fsBkB0H+x|JRJbp7kUg;9Dm<Jz(jM586*l*3g=bNx+5`K!!cOWudtm=pcquj39@sAyUO`=K59}!mucXG?1N+g!tEh|YfxT?uMCt;2V82^<8Fjinus<%mkUHKT*iRRZrbgNW`|rY0)DU}Mk6w5nwXr?0r!U-|D&vK@?=M`J`l&5&PC!`B5y%;X!#12d5PiiKIENrC=M>~@gPdtF&#nlYXIg~Kb1%ZnsT*v8voXTvnHgd8ERC>v#zxpYha+sB&)L9t$Oe|>A?ho(z<C~F^Zbvnc`iuUJTD|{o+%QRb4JfnH&I_9Zz8`;JxqR?{3b(qFGG004e$6A8{YRR^m3?&$%k3*In-aszp#yR7@yh#^9SKd>UFZ{SL9RFG=}hLhHx=MxQroO&Je!95dIfK_!H_^<WI<-F@(Qm2>(o#chb-NS@<^_Lil$ZLii7AbFzf+4I4tZ21B?eL%0?-lw6D4z#q;0akoF3Qk#&Q@b8;aL&>83$f6y{P06k7*r%v&$KFMCdcv)k#@yEszLQ>0dtmQFxGnWwdtk3bxHHvZ5A3H1cc+fF2liit`%uT(1A8>W{i$Q@fju4J2<k9<VBbf$H+8T*uuml1l^SLb>?H}eqjt0h_MwDZQ`^`BdsV`XsMYL&{VZYG?-G@Fq`Chke3@E67A+#z@pl#Z|6J<%qlG{2_D6GSGjcnBwDCt<f867bPX6fV58WRfG&%C>Z!dqe^hax%xB8<g!(=%gdzZ{@sSW&5U*^63sO^th{;27X>i($Vk7^qJ*flJZH)I}-HJq=I^A2+EVaf!Xy-BtI?Z46q{E;zBv;4<8fBl!%W4posve2K`?L)j%Ce)~jg4xvv>p1y3)&2*FTJ2E'

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
