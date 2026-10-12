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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_002.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_002.stl', 'source_sha256': 'c7f2f39a67f7cc94d5a7921642a2f519983bb9ff381cc12e05055a7601993ac4', 'input_faces': 732, 'input_vertices': 507, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18619617819786072, -0.05438138544559479, -0.4399629831314087], [0.18359270691871643, 0.1863100379705429, 0.20288591086864471]]}
GEOMETRY_BASE85 = 'c$}r22UJv7*tIXBMvc9fL`TJ5qEWF%M~%Jr63f`JD=La4dM&YF0Sj1xQBknBD0W8?>;)TwsADhKLSi@i&3X48GMANqt$%$VS!eBMHi!3~`<^;;$Fy(do<6UJpW<3dvoZ@aRnat6vTAuXpF!T^hYlDtuJWiczHVAh@zsx0m$dEDrhN}L%}4VqGjPzj0p4Zmn99@}T&qk)Q<=e|y~lg^8`XET_rO8QZ`yCfxIqqooL9dwgB-8R)~HgmqN!TBil*O8|I42&jwaZeUORczp?bjDjY@4_j@(dcy?6rt@(=68|Ii>oG;9O>^TFbqer_qgHhr!5wo+c3#J?FMarEdg@wL+n!j+n9S){(H<4nX!F~h$yRD5%t38=sKxWqTd*OWL~pHZmq`EZT+<JX}*Uq;}%K4sR6ZuCR^=z*x;GWTZjSDZqe)}0Z5>1(;Jed$cJKdJ%z8%x(p{8@*^w|1)!e{{uAiI?w|_?9nK5kIK7)VCFHB=JpQRm3-Y9Fz9gLlz~t`g$)vxi5W3X{m2(;(_@6w=b91gOZSk=LK+IM*?tP<yN4bIdh@@AM?UQPrX4q_oheu&-Kw?!{ZFTw!&kj__N-NZ+CwlEB=%=xZexq(eL5U#J6?svO(IN(TeszdW`zXebFz?3rc-Ur9}8~D^|(h&CQu8^*dY<-#nt6#L*T<;J%9Q5npe5!z%u?#>hkeU5L}>eX#t#`enqQZ$+GWw<V5#Z$pBs@9ZyI#v;gnr7-xW`>RE(PDQ`(SOLHP800@RE5>KSY_zA;R*7#OwGHw6PlRvpC*wrx@DO=$_d%RF7Z*#uqW_dQX0H+OYj`Y^*XBcr-_i^ImdrA4Z3Szfe%Fq;uk#%uq(6SdeK~z?-8;E2y-03DeJ#03h_s{782AaT;UC|Ee%b8~|L0n)UpT_`zBI3@@W*_T_S=fxM4l^_gTLV-=Hr?NQeV$r3jT;Ox@byK>0hmV3HaJ<xnJ9)Ey(|#g79Z_#r@8&1pi<*_<L8+khq;|NgT5&J^Y8mr2Y2cxo#NzCC}u3^;<*WXMYwWzCFuqiC?=l+Oz$M`1-LS5w7FJ>1#EHE|LC<JcBrI6UDcED8Ak>?|iSJ{#s9&kNSdj7@x&X!*6~9>(8x<@FVx(x<&pr%nQ@AJ*ZzGPSy>rGTLv=6ApjN&@uA&zP*v>nj!GxN-h;Y+cBwcpR`hZbD0&muQSU~zt}?feLJE3ZO&u9yZIwd>F-y_>nUr{zmdPecWW-=$~3e(#%H$i@LSK3es``*_PF7=ughVWU%9nJS6}nLA?uH|=SbX__b~W@lf32cGBv_{Db@*bLN{WZ|32N|Ywhv{$$hlLzGI7Niu%_F$bIQOqHtf$8>0S#I<k&gKW)H$J#7I0+96p_%-!-~{mE7vakkx+_FLkxK3m&*8v8xG9`ew+0^(dcFhS}Ktbp+oTo!Rsen<Q~ez<OYDb#PV1M{@#Gweqm+2BY0DC?Lu@;JuB)AZ=Ch=X!nEq`~cOC!FX5WP1^)=#a=ZnS6XXYuu}vt(RZ26w}_ZTkuJPhXby=)1pQJOsT!{Q^~FeCqEP;(iN0LH(KOC(GY2EQI<QFTl_6E9P(h3y2?a4sradVBIV04Zr+J)USA6)>WH-EZUhA4u9#isq*?kHssA?8T`hNWFDDb+(CPOm<E5`6&dGRSR?5#+sYB}r?r><HNSp`arm`A{QNJbV?JfZJl$o6?;bAWNBdL(>p;U&@LM*SCG~u=pnk4z;2$a@{o>rG^gb`6#qV`zuIR4Z=*RrW;E(cMAb(%DIL7ViQ21xZ1<LE~H4uN{bD3`z|BfdcsJL~<-IU)SUJ8FwE%9x&g5hV$D84;wZt=BKd&IZb+O{11_BmGSN5)7yts`5BZ+~)2d~@wMsc&BUMEcJ<@i_dZTQE;czLWbjeVit~o^yrKpIHLe{cr;FrJ+rHOVw#;=b6P4-{#XBzQ-epqrGMP6-C6i&g_ji`*%xy%jS>LA69D}v?ppl*7?M>;+y8Kfq!uo`YTH-_){t&Z*wn69Bch2GCu5OU&V;;KMQf%pM*cA8`^U%kn7SlS>G)k*Ghf!iaADqWftUf@B-ZLt5ESxfz8nVOeaylXfya_eI<_O{TX@oEQ0+bE;I6ze!JAS^hm%tpv2J_*Y=qEUJ&12ySw<dnTw3R_Y_0FYYTnEw|K_jzHWzLe6DYa_!p`o{?J$Gm%~L-KU*8*ZTV%yx%qgJ_*o{zxaQgRC{BE9Xdd{j*C2k%LHI{}aoq=tk)JX>;Q#sRgw(H=gzNTtE92gJ=bHGsISS*me=__^)nZ)7Nvc1m0`fm00C`)qM11@9D8$jDF@6p-72i^92<|KPH1cMvi#P|@NPXMR%ZMMJ1NAGtM>|`bF!~*D#kk&=?di?{`Msr_#5YIp#5i=HCBCV|O!Sxg2ehYfPxycO;=1M(w5LTn@hy#4p&vc>BR?~iE=2xLNqw#G-9%U4KIlI3{2~l_Ugd@Qb(Ub9S4O{EuYHtt$3Ck8+JEaY){Pez#J5iI!gae{gI}W+>Msn&{8}4?IHPaP7cJwCIEfcgfA&uCO<`?g4CDEA@;r&ty?LzbxV7~tExx5eZj7JqvB<-IAAhMoVHM)!{&dsTw?@B*pRyG5EB{GZXHB*5A)jUM8+_;bqy2sk*Y&Cd->(bW|NN=M*T)wS-|F2M<D}{y#F>{oN9woU8snO0OLATDtu=R|-@^|f5ARCBFH#8Yd=h8$xejZ;tV4S``^dS|-eCyp=fU`~Ppm%MFt1~7pq(>{if?MP9dY_CNBvv{WPh?RE{A*$IfZ<dOa5K1yQMGsu`%*y^6MbJW%D-FkNXGf<evL8<@XofBA+!MqW<|P@$FIB5ohNz#LrV5^>=!q{U4Lj&MBkhTyD904E`sq4`%=F;+s;+<GK-7G0smsll|Bf8-(?6?In!2{2j!%eA69%*goXHL|yo^Cu5wK*o}7jteGbM)|}{<(;KiZEtnv_DSI^fH@6Mz+o^BFx1Oqpc9uGeILR^c{v>rD<ho}~w-Wx-h3J?2T*sQ{7vB_p7;yr$B)M*94fVq_!EgE)?YCW(^Ns1Aw;`XFsS~D%e|jSBYyV5M^H$7n5@(?a^Jw%+w5Lvf@$H*xA)kA%W8Z(X*H3;Qbp_*g*m~q4ccicQU;NRYz`gK4zn&=9|7ipAW4nrVEN_hXR(mVNe{df8>DdtVo$Ko1Luk*V+CJjP6hnR<Z$g|e*~B;X&W|`5o*_=5dvZRu96p71esPz)S^D-7-!$YR`u)xcjL-Fn<K_1Oamd?Gn2+}4uH%va>Bw7|6x1*Lb)5YE{tCp=?jk=HKk-egbew03p?}Sj+M#}UW3<yF5%c%E@8o@msaa*@e?chsyFhv0Wy)no`)@>|AN{`_C4Tp1h|_LA^7F%+VWNp$V+`YbtEZRzUAN+>KkfzY%PW4c#QAUu@ke|k`LRtqHBjn@&4vHyZ|pC33W{&Ku^sten1FR=c&-8BPiq-t7`OB-g}gCeZrYHC_nG@kyST48*K^y`juwei{-$9avpf&(BlR0!N1Uyvk^hLAz2!b?_#665x0U?`^T3LBUU-Q1Clu--_3ze1p1E$AzWv-;e&6~D^5Z<0*1O$aeqTKl_cih`+W$#!A-~_-8-6Z~XIq~p4aKik7USgZYmCqP70bEK7jt43$+NxF@LUqV&wRr^ZmO3thkBj5-*H@7pW51r-(?Tx#V@zfo&q`Bi(k_R`Qd)2?>{QO^;Tv0m$8nSzZC5#^&{*UpJh3&9#-ls^*b#z<llO@URU+n{<SXZ7s9${3vbn3>JNL4JPh1n@a=91=-<f~FfZoy>?!q&twsA+J;VN6Im<8Vb?SMT<HVA$P;c=kSdfRxH_$Jk@qHye_aj@ozu7N61~hQVv-Una*2!}_#ZS$1aqdSUnFmUo25sPvdVqG`7&zATzHHO}NObj`d2p^jsr8vRXFi?2Gta5-N1XN9FV1~OKNg7iDOOyU@28x;vwu_fkxhr-=kJU0);h`PJIBcloLj7mpCG<-e2#pN_JoIxlRQ7TiumuYV4q!ZR(yN$7HH4>C)h81-odxeLYxL}Nv^&rT`1xde2qN!DLG!^*SUcDF?poE^{1PD5+|Pr`hDJK^keC7ewF&~d%_=P$9Q<xM|{(@)riCMw*ACj@vSc&8P-EBIQwrBpYvV+1M7^v-D2@AkIbmw^Tkb9-?^UX>$f6rne$JP>#m=IJY>z7<my}JCZT`F?Ls@FSD^ma7>vUu1(RHT%hB?fkLQkHz6@$HRq7uY1HWS&`n}kB@h!gF;B#LyR|(doKF>4eCU22vk1gWcBhSI-{$hR>Fh}C#dx~>ccQ>pvC*#Dozbl6O;(5%nyxd&zul7Tp8(%~o<~I=Ec|LdUgZAFb<{I+pT;J%MUTlsr+;6@j{;uQ4Z23OP)wkUJjQBh!n{Up6U!xuRh37FXDC<0lU*3xRzsCDJTiZbRmY3KU_&&>=_lx+}p4E|`sqq*O@x$j!eC|`Ws#v#88>7XyHt&Lc#QFYua*+j6zruXOzOR*99w66Eo{2n<PcZtSA$XrvIwSU@SJ?t3e*3-f-@G;Y`c=gF1O09}+fIDTjuiM2Ig(s`>!AXM{YYOOA%5!l?N*5-gU|kT=EpYjtN5m2JK^^^h&<HpzeujzCta-T{IX;|Aik+nC+w%+p?}SfKEXd&0q=7g-Nt&7m}{~4{9MJkj+qZPhkxvs6Rvr-Z5}GV^PH?VDwJgKXFNun&9~5x>&L_2{_6?Xe$*FO#kZT5!}rL?bIxAzEuGV2JhXK;`u9u1&;AbW91{<J{t>j3=O2CG3tZQ;F2)Jp|7xAGFOmB?l!VU>dX`1}8coD^p4*-4nDyl;@tvQ;q@I_yHC!s!t-KNa`|DBM@5lq<n@WC!&(Fv7iq(Q7{>mokFRmx%9K*!7oEd<;6*XbqPO*w_Upf!-XwCz)C-EHWN32Kv@|f4===b8Af@0Ax&;CJsHhBcgb-5m<zP||H8ZB}A4&Ed2%D+D?_3rEu-`p(IUWw;<Pkha<2J*XpxqNP94n2p@IU9JvU$G6(gMLfK=bSrdz}G|MeYU=S7d{8BJQseh!FbM<c^{v{uE#hiHcp=Zn)BU@clEW{3h)o*ykV%Hako5o*3#EE_*zmP@y!dojDG9Jk@C7*pwZ`jY4-Gq27lv&t+>C5Q4L&tz0R8LlBdv}2Mm6hEjz?tmwZ_Ca3tE9XRfs0c4U{_m)&nO>ihnT=ZO{YyxUS|8?HP0kUV!bFHeeh_4UP*H@oJ+>6@>(iSK+)k?L3Ni0j6C8-0&o@w|R?n9;vf4tZPr*l=Cjhos2=yl&J`@wM5t48ETEl02`mHR@x$uRn9(d19b$^fw)m=XB2J@~Lq;ZP+5$pSDi&pIYCm_crlo-8$gv>waa?FQeNU>g%(-(Jy;{H`Ld1wcROk4jh&KvcKPf`u2Fqr+y*={pIwV)sg&IypD)(?syn+oX;_zT*vdKom`Ke%*OM+;lX%rQuzdYpG)$&j-{9t&v9PFBF_Pj<@t_f(pZD9XDWy1gVB5O++_1<_#;Ni^CRt-NYu}89r5`*RKGMo!Qju<@H{bg37)4!-+*6jk$hfjw}fDxezn67JTK4b>{o;EJmtHG@cCTT*6BFnuY3moLMyBT`3hp6`jCuvUOXw!o2(O-qW#@pp#Jcm@I33|WaKUCCF&R1F5^V&(a`8m>W=Rl>|Bj@{)Nx2^y`s$Ufgm|!hiYZ$N-GDF`o_nWp4GF&tEjG*KxPue>Vr~Lu;I?Y`$Od{eflu(4NOxQNMp7JSQrJ{FpZ6fZrqn`ES1o^#|tW=h{EudGvtEXwTOo@Jk+)ezC><X7nTX$mh_uM1S;eU7XAHTVF9xOIA*B^_}z4_PLwE*ONjd58B~bh`+KF{P40?!*%Iv3*JaOwY@hnZa<Vp9`>zV?>e4MHGV*xsK2bP_hr9`^NoIKH}b#r0@~B2KH?noj&SXF(;0mJqJ7^U^GJ8czFDpb{D#@lFToR#=X)LD?>N8CbsXBi;&T?wbD?}rseiKwdFzY)TN~0>o<BOj4`5x1_pw^oRjfashGTs08;E?S+l2M=*-r_szU}cpl4tw$VFq8%UKHPJ@@s2|qYd%JJYCY;==1vk+Uj8jU$2}Ve$DY{XMw?}U*(KEH*kJ0#ad$+{P-4z=jpbk!x5)oy!4kT$5xE<PNNL>YfFBK_4d*@)X&lr<DnJuU~Puy8G4Qw^jAOt@@x%6obXQgzRmNYsDFJOpA+<);W{sDHP*wA*^ck|RO^NDHWr_=>jx`gy<OTO!PVEwkCkz**PUeaZ_mX#@T#dXPL<afZ|^%9{coGXPw8Xyp9kW({FK24U(22z<H4;T`sL*=_|J#oIm~fB$IluCztaGGzsu4e<E=TL=LH?d`ndyfEJfqs`z7Q17+u5AFP{87@t<w-Jkxez5a!X#7w~%x#q;Zn*e|Se-|>A#aXk0u_W?|Uzu>-jPS8yq5?p=TjD0vSP1Fs(*7%^|dmX8MwjYh(PjmWxmrFkNvu%vm<vQT}zQMokX@POY^ME<#E8_GUhWU6O<H73ThV$;E0rEV`X2&?UYnkAOpAK>DN4;K7_%FW?GsO2U8S9#7^PiDee=1akU*9vxb=;c#e}up7;xvhq{tv{z)dGH--78(kt^TPE{Cgqt9L(ZB4{-{0#JSu(80WMfIwiRJ+N28@&oyQk{Vppd&-TpK3~}_Lx$ymv<7R`ez5Es9c|>cYAAL*mY>(({^uwxQeZJb$=m&kX+I5`U;yWAjACQ61t$M;w7#!j{&Mkrc;eQ_+>N?I%Eylo)T_^d}hMb2VI|2Dwd=%%y?VGWlSf-->kf-u|-nq_O3oYRLpJDR+P`mXU^QB7={GwGP|9Z|)j1%t_@W+f@iT=YnuW!TqTW#x2nJ><DUK<%6`(N|L>8G79PCxB@N%hmrmsCH^d`Z1-n)&i?d(zC87Ml_0VSCBHbDg)(+-=CebKTa`?dSMRhwp=Z#5u?GIU0VSEr@^bF3u+h@V?Pjf23i)n0!y8zV9h~Z{jS@MV4__;g>HwA9;^Lo=4u{=X%$%K9|3WIP>`2+V2<ii}RdN>IMABN7xs54l)0Z&xy3^cQEhx{W@)33fupke4oO+JRbXRzc;vUntjCSr`<<V>n|#Z^FtYYPdK%Hn*AlUewzIy)laj(r21+07nA8d;-CLD#PxplsUP6ydW-K(c^*OD4!Ys<i@$S+x#rFK7T+UrjuYqk%IQ15A7!q*7USVZd{0Q9`Zvz8+;^;*Jm7l|z_{f(%6zgk;`j`f{5#(-*dO3?Qf-qv`q4ca`|`1>@TXLh^~Cvp!F;eDe4Zzr=YMPA`uLnK%{j{H>xm;I56*K-s-Nb3<@D2@uTuRq=d08>Y0g)cJ^UWeswnIud>@h4cfOC%&v%7?xhKA#%yW_1%L2b%BIY~K|K@j7aozCy(thWDo$CKyd7W!JQ+>X_bM||x?|PnZZ}?XPGY(bye5r({sghaCs}1hw@=pkqseYXL-~WVQX!ZZEe?m~R+K>O&e?l<N(T3%YvWP|TYH9>|HF*<t4|x-LAN4qSA3274fgD4=NWDeANWM*dPQFckLH&pPg8Yg4jT`tAIfENC4><!l7qtXA7uiJpk!&JYq7EllA~&bbAU7v_Qx}t!P9b}fEi8(MQKylIk;hPfCyycfP#2MX$Wy6H$y3SGSrq%TC|*HbOI|^apzb6`kfW%_$x-Cf)GOqh)FkQ^veL)oB=QRu#c!zh$#2Lnsn^Lb$xo=4$x0uRpOD|ODE^C@K>myTj2cINMoy$2At#bgP-~G-kn2#(la*E`*CE$qQCyW;m|T@yg!(PH2stbDvj)ye{-8mhkUx+gQ{%~x$=9f{<ZI+;>L282@=oeH@=kIXbul@Nyny-}c>#Gcbqskjc_eiRS?M71Nb+zN#RI87l9m2I9!MU*qPU`?<fP`M{y<h*kgPN}IWIY@T1%+kQgf4)<{>N1MgEqYg(Z`tWN;KmcWLPyB|S9*IRon`)~N2(Ok{U*W){WSsaeQbc-`zQit|$ok@J(kqngOykxQ{CE=Mg+R$75vj$DmegItYVkNOk29{Fb$#Z9RV$xX>^sLjc3$Q`LY$sNhPsXk<-zmj{C`?4sWMx94ix`;fD{5y-{rPS5rrDQ906WL1MLfuE+LOwu^As-;0qFyAQBF9m0ljF#Ds4vKO$S<j%$S=tsscQfG$k&S9-JrS1?&O?Q6FDcjD76x~jH7(#DCMX{$wgVG9JM*Q9NA3uCM&g&&Ey6wiW^afksFb_Q^%0IllxJ9$o<HJsZ+^=$s?)L$s@_*9c2{Nk2;;K)So<=I+yBCo=aX%T|r(>-aw5YZy@ibMv?cDPf<^koqMg~CXPO>?<j3q6gOj0T-#A9Q>#+zldF<FsZGe9<hqWs(NXq0$_5t2QPk7qDDp|_4f09yb?QU%b@Bs8N$<FaKOLIR4Mp*54f=rmfc0OqD1ODF_!0F6`4KsRdYYU-K11D4K0`i8-AF!2-b`IV-b@Z<Q9PGL@k|!Q!PJf9jm%>(i{d3Lio>Z<<Z$wC>Phl$@(Jp7@(J=)>I3ps@_p)`<oo0ls_KsvzE+&k4VsUfk({4eikzQZnp%Tgn(RrPMfM~IQ^Ux?<ZaY-<Za|#)b-?D<Ugoe$$yX!Q@4{3laEq&kdKmW)I($&`GTXIryispA|E7gW>LI_x`VuhyoS1+yoPM0ZY5jEq15%{Q1UYBI`T4d5H*Y(L=K?NA_tHsP-~DUkgHQmk*kwEsQJhq<h<1MWTolIdC9q16uVK?e0HP0BCDcU4o>91`TIxYzsXOj3FN2bMCuuGBKa)!Ao(o$5Op*85P3T_l)Rn1mPK(ObuKxOJjqeIJIXjm>CB>dEOiojEO|V2E_p83k?|~wy;&6N)L?Qj*AbmXu^)@#0BSfnfV_sfo4kg+gL;CzgKVQ-CELhXsQ1ZN$oHrz<a^}5sA^65i?0=Da)ah4XCfD%mL?Y<m!*1=%aUtSgUL0?;nZ#9aPl7NF7h67H1!X1G&z=fm>f$!Nj*wFNxn$6kuQ=jQ7@1$k?*?wyYAd&QEX>Xe2zu&0qQ~W0rDp5X7VQTDi+17sawda$syD=<Ph=_s+GKi97qi%2a@Mdmyst?XH%Dvl?IV#lV?%`$TP{l)Cpu?a(`-da({9)st36mxg<3&S!r%^Npf)(#W|>MWThH82RS>7;;$N1tyy1L6u+fDCBG#<qb8D{k#ADZl5djFQ4f*Nk&jTflaG*hQP+}pk=HxQGHMWYEm>(GIfy)kI*F`w9C-@am)f1|OYTLjOIF&1+>6|Y+LqjhY;lx+)GpMvWTnl>UC8ZO6gQ&QCO4qgq}C=o&&@Si6qjaE{5^|e4{BAi2e}N@lU#;eiCULjiCmr9ovgGoxjMN#i{e()vE)|dQPlBdrQYOG<e@BzM^kmOQa|!&@(32i6R82@iDZB38nQn*gt~(qLf%HTk++eLQm>GYk}p&5kuQ_)QvV{~CBLDn{o@T^E6(f&EkMppE=Vm)E=aCGtx2vxu1yUm*Cy|#?ji3c$55lmG32Y%Sn^eJJoO|wo_vFPk$i)Ek9vuGkNkjom;8X7Lba1q$bUM@Yw8`Uovid6`40Iki{ky%1LR2RM(P2w(oN)z<dxJ_<dx)kEQ;q-SCi+H7f?gU3&;zpOUP{;WuT)BqK+mHB9Ep1N*+trsSC*q8B?bQl6CTL)H!75p7$Gz;t?#0hdRm->O|@!veMaPr8CJB$>XTL<Z)y#YJaj9xgoV0xgog<wIo?-adH)MMHa=ys5!_=vy+RFzh_aLjjHy)Y<#Wwiw1p5{z86FeMWvyPNv=@CzF$?=g3Lq^VB2c^W<aHUF2irz0~#Oz2r#k-#s#tMe#~USxB8jT}GZmo<R*FE1g1C>PwzMo=WXSR@#R=l{}qlAx|gI*8bfiXR|1t&!V`$qx?ecLG4FY+J&sNJ-G+Do1=81wx+fxD{Vw}?ys#`6t{4cc8=23QCd<vkXw??)D~njxfZnnxfZz!wI*3<X>wU=F=}aYF>(Rw_v8ZP9FCIBQ8GG8K57nf4%W#>^&saX7p9gW7bX{_Rw5TAm!wuFD=kkhNiM>oxCFHoxdgc}brf0YP;z5(9Tvr2)X`+6BgkIl!7Pf0Q74jzktb07$rH%4s3GK8<W<yd<W=OY)T89B<ipg<<iq4k)Vt(MWIOc@*-m~(Rr~!rzE+&Y4O)<#g<ObQfn13E1GP5!2XbBNZgO4nF=`C?82K9YD)}1u5jCFti2Rg#gZz}7Oua`=CO@Y>AU`MnO-&*HP5wyzll+nV!R_BO!3P$_?^PbDuc)udugJHlcgRZ5l5bJZP|uRjkoQsdlbz=Y#jPBrrK9v@QQU*tf~>SPxd*uqwK2I5xh?f)a$9mcY7=rha(il1a(i+IN9jmyMr}%NM(*Y)1E^i8P039ew=0X{F4UjNUC5oOjme$Kov5wJoydKuEy#VzzpyCoMQus$Mea>)MOOL~xi`7K%0nx+ba~zXU;j(Ze}B|DNi+NpHq-v4@oO}$f7#R#EA>k??OSC~YqOTl@t=Cr(?RV_+W!DmL*}~'

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
