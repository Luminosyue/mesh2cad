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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b5aa31a84cc746a982228827c5185ac3/part_008.stl', 'relative_path': 'b5aa31a84cc746a982228827c5185ac3/part_008.stl', 'source_sha256': 'd08e25946688d9e6d6ebbf34721f7ce0b5d1f94b07de1aa3eb34e8dba3b268be', 'input_faces': 828, 'input_vertices': 875, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5000007152557373, -0.2509249448776245, -0.052171990275382996], [0.47927987575531006, 0.4483131468296051, 0.080825574696064]]}
GEOMETRY_BASE85 = 'c$}r32ej2h)VAlID;)%+7cq1x(mTivMS8DSYUmvikS+v}4vG~!Q4qcKE+TM45h>CIq(?zi6j4!8EPOMw-+fGS^RM-<@5A-3{od!ynIwD9OmbRm*D~?G+=BiU70(~Y{?FVFLMUYwxy85vqsI>EH(*SKk)tLih#Z=$e;i+I)46rK#}mXjF}ZaA0b}}&E?vhcU2kBm(&dfP1D_Z@c66VSy`LD}e}Ljm`V1d4K=Ltz`-~bO|9-eu&FbZis%6R>PaFTsf0^Yj*a^Z*Rr~VPwqq)K1s0D^^>Js~R`Be0l8+k$dk}XgPfv~Fp??13!G7FP-88qp>$Jqrz0Bnf>o}}^pr1J3-#XBbou`cE&P)9R{fPCIKGy9s<bN_Xich!^=*Rq|yyni$jk+I;`%gFZ1@*UcE9r^U2<}Z^F+I?J-6GB1pL4vbq6u!5d&t%O9Bw;2HG+Fp8qM&x_l%;Ni{D2E`myUi^O^3acekOb5!}0WCD4ysX}0F}vNeHzoV*84=ziLMH8?ebdoL838QA}v2Q_!!yBO@J*MyUi{eY+G=kbXrqx!LGtc&c2x%b_pfqsn2>m&Pd9{w_Vf55~2SjE2z^kZ;7+f=-u`J5*Pruw*OUP*KB_470R?akU%quW=j7TI2mm>b#N9W*bpz1wLAwJ-O}0DpVC?an}ZE91Q@y8TNV_53oQyZb>Dx9?xFTIT`WoSYnJ&)l2UC9*wpr_(QM{ahHOX+GA;oZ{zB*^-)@*WO+o$;;l={TRGI=O5Pd(HK-Y#n0_qB{X+)>|Y(pyA)lg=MD4jZ_#`_Q+Rn4H-}g$0iIzEwSVBZ)lu9_Zm0YAG7z`&7T5FCOl-V7iaRgQNr~bjPl+{pJK$!ixq6<u6^AX4;>Mn}DSqx2nosSAHPZb!;9izPdY&2=CM}QR_K006e(t0{O!NAOZfl~r(R1y(KtCNPos8@sJlsF?H2t@kOuWk0VE^Sd5MMuIc@#Gq?N5npAMU@@#>oDSB3C2(XP&12{MRD;k8|{Ib6px$*7MQ4l(O8<?fO+Tcb>SJ62;8|GuA}%-j{;?SEwG@zgeb6WdF>={l|Hzf4lGe=>B^yi0&UeP5;b8{hKXzMfVRL?q58Xs=2r|Z%q{E{=F_g5nq<|qW-(zw0@~R?!J|cc&qWxBt>vHHt#h*w_m+qb0^aYy`M&pTeP1qX4l**w1MVt=3~^pTnEj?`l>zke&jfc`P-4UoBsH$qzG<rF8R8ji=v%0H*1xCFN!;dhOX58Wj~5_pfhc^MFv`j3w=i8`TI(Az4T78+4^sA^V9Bh{c~&9EFB9Hw|0D%s{6g1?HS!KxVxt=U02LpJX6mraN~wU*9p_A1h`eR-N`8K<enYiHn`bJ(E01g%QFJp?i|Vayy=Y_r@3n!CeGKfe>Bj?>ww3vKf#R;W>CGJOgOIj-&>a@`M5hyXwK)sFz5520O#|dyI|&eKj-tB-DiR3-up8G=PBpT+nT%J7N2(}Y}MQWce0eE^F{VUn%m&K{+rv+X>M_QtlQqCuY(-xEproGBrl|V{`Gf|V}6CXUGJwL|7<d~ACiy8=ZX6^=;JVkQ~M<&X#5Y#uetGYTguzOM4eCZC+c#vaCBY3!*#Jv6^g7&n2TvQXkLKF>vdgh@bh@Rc4Vae1drFNLt)JYxXJZ8RaJBEWT9ZahBl=<fXC}4x@+!md#=~%zCq6CM|Ys+Hn=EJlh(tolY$&|Ov8Eo3~{bwn48TXyy)i^@BbsyX`O5^m5%qqjm!Qz8mOZ+|B&YV`q8SN?`hpH^X|Q(d7l<K|JJqFrs)2_Mf-|7G_SC9vfkc2;@$*jr{2G9Hz(-*1Gh6?J*1DP%jWUAUvT5^E5|jzTO+`&UJK~DsMR0i^z*^R^XboPeq+~Der_InJd(S+7X-MG;TdXQvjbh<u1~aezu-=;q58P&e~(Pn$CIA8U1h0${bv8rS?9+EcQ<6v$7|0mJcY&$`292KcuQQJq@NFN<z7w4duTwAPw#xf&n@0=gFLkV$R~5RYSTz=)_p3Hi)Qae_tPMD!Ox9+(=YqyyUX((oae8>>u`u$nD1e3<MoID=lL!^*|)*ZdA@t=4$yec3y%3Nnp~uL0nYQ+zFlym9(UXx^Vd9BOmh>Q=cCo4PLN|hrs0i?==o(-udlhm+r_*~!z-?*>x9GO*GF;Vyi4;pbEiO_9iDdu+Xv>ah52h1Aa3@YK-W3r={)O9$sXv(%21rfbKcvR{M<wT#@w|5Zlk?Zt#^Q%Nz~r03Vz}#%Fm;=o=5Jbq(FNI<HWs4+^oKi&O1BX(d)#k^)LCygW&NK;wGQR!JWmOXq<HIw8_t{>cwfCG)UIm`--@CUr~B}`o%EKZEy$U#F@2Ha|_%`_>5jpHQB1U3C`oh`1DACyGd?<8_ZE(r_i+xQQUr|8EyAW&P)FKI=nugCeHPBP+w!t?u)eDHMIVJGopi^+jZ8`dA!5$g-H?I7JVGO-9_%jsCqFE*CoukE+#nF#m)FL<#{1-o-bnJ(9OCZaGoz=&f~-@Tz+MsJ<pfRjn_wUFY8l!-nj{@sGql{)B7P;Tc_y#1Gg4Cbp24PzUDUblg2Ln_m@RdXdDoC&Aa-29Q(?x4|KoW{}117)BC^afaV7Gv;U7zHSduU;BJR`M>XH@n&zG$ZtuN)R_AN&&;S?t8hsJP%>tt%xhS<Xx_$eS=k#{Z_0`;({L)4Lc=LF?O(M?Y&BJ)}KAIaCZ%*$~bY5`hM2;WkY36l^$H!0VoWM9S{$8)gg8?4jZpAU}Q+=GrvwL5rMgI2jb!O)KP82ta&R-emALGY$rmc_S=6fH~dcL-MWZsN5-6Qj6?&%uXe|JOW2~k|wf3@-R_;K}~t&ht-&?Pd@%)@yObI!B<X_r7A?CzJHDDJlPbbj1c^=Z4Mvmf`*BeA+X&38VJ;Jje0B5vWlAnMb3!QN6<a|8Ji6Of;u9-{3IS*GWaoxk!*-45JXcZBBAo}2+Lx+l{-YH*kKhx-|M?^qPKcRh04&%Im3ttlsH-sL_O<bzH}a>FhDMI_(ZF`6HnM!f#v0C&DmiR9MZbm#nB{9c5PYxg-?$C__l>F4eXGl`E`tGV|Zac9&Dy}pUJS7`2n8)Zyd-=3VNxdSe~>Z(8I5RWBmZVkyq{qXqQNaHrlt?4vwnOhjQ4#utXM8?24;c?5{3ys?_=W!e67Ooqek;IMAcn)(O&!WQD7b3^=jzgMTcpu3=TZ`V81~>TqALb|bUx=&=c$&JLAfBc!;A!dt?uF`NgNNsf#r=fl3-j=NF~Qw=Zybx_;d#V7JdX_U@H~q1&^%%uo=0)c^9bWV&O`Hvd3YYhw;P&AX5}px{NvCtX}z)@pBmsMxSdR#*D(w0n8?^GFn%1qu2^9P#)E^pGw1QZ+y>|IU|>90+z-ZsgYjT8zeeN1z<4mg4U7i|<3TXTcrY*?nDclrcs+d242*{`=kXBcJRX?4;9N(C^Izo6^ZI!BJc#uq4WC2niBsZ@^MQJu+(qjKIIjbC|5!>CH+bDBPMp^zbL)GH{G8VZi`R`1cd%|)e~%{4ud|AErS~(t_o4o=Zdh0!nDe^9T+A<{xf`mxH;;I@?l!mx)seZ^Em%hj+zHi@xe=<P$vj*y=9qV3&hswJdEPO%&wYF@sy*{?d$-ogbAfr6gn9SX{6If0pC7@wALdrEY3KaoM_~LgkDo^{eypNs&*!yGINyc1yAbC)a2{9Q78+N~dHk3dS7B~rTsftu2KGnr`=Xy%k;moSN<QZwhc3pU*QV(?|2Q-;-k9?^WbXd_`WOB@3zPC}{dnoD|9H*K$U}%5FCh=$oCllp0M5s2@cjDq;#vRknmm6)+__4hJ3F^82Kur1x-|XDv;N~X__)CNc)isoeV({$*crXO;W66o$O`)VB+gFa@#ES;#~bEOo%F5!oR8PQ@p^lQo{2iHFz4g)_7D%}C(QYHjs11b_>Y&5i+T8X?S>0aX+8+AQ%2+aIp7xZV2z+WFc;%74zd4XZejoJ2E=XT$IEzIzfT+HPE*PobCcKM&6GFhg4f$h*PSTtmiU(D%jr?Xc^xi6<6o5QOa1fbfXG9f<MTe|cIx$$nq&N%FE^ldX2sGIdVhJH8L~IU&rP0>;LiCBC;a(z_R#m8n7e#k@&5j0e$M%HYSZ^F!rbKXALeD~dl$|*;+$tQGvz<bMMsQVaL&J-`IANdemKuI@*n07=b!uM*Twk!%TE63xW6vO(VDt0)>~JP`|DyO|8b7GFn143Iqt8E^9t3)8~@2s-5=`WA^*$`)P=d7X)}F3!SgyR#%G9|Kj&!a=LWxi$wc{a^K7K|iMYOxj$PvC9-m)OU*-nS7p`xJyW3W*j^YCK6}i!WHJnFKmoT?b7yIP1#CzcN^)ckX{dnph`4=;qQU00p=iuPt<%@?j=Xr4>Mz7zq6h7$BzcCbf2Iu@cFMUk&;&kVI{=5m~%{xUrUYEY~xlfpT2{~K(dAu$esV>Yp4^Fxt={)Oo+~=>0yMpS%obzm;E@p_^s7o6DZvvf1E_V!U*ZuPr<saPQ_mTQ;r_Yf))ZZ7V%W<lUy`$_te_h<^l>azKU6^}&4($!p<p-*ZJ9g0?onIdR$iKJt(^Opt<ln7_aSJX+<GOmv(Pe&a^6}pPKuQ!hk)Jdi`LR}k^L11|s&ANkS*X6u1?nq$UDNe7!CfBbsBf6t$iJ1enmF?8Ow3Q$=l{&5{(1dDKI5F%A8_$(cH+pheUtJm@;<oDpHCb4v>zbO$7T1Y;|+5sHytl?K3=;g9j^t>$7SMpy|M+i`RgT6FXo(o3-t<f1NBP7xn89U1h#7-pJGa;ZT@^3lPI57$r~T~^JyV(agKa4cUo`yFp$q5DWBHVUR(A4@Ottxja%kCp5uJzsCV?ZK92K3<9%cG^XnGW+`)dDlW9MVC7CsMQ7_}0nYv!)V&VqZWgyin%#E#un(M#8z1mbSs|VG~*d3$xsEa$9>LS1`&NJ!~=Juks^m*uZ;tsDT=YOMhKEw^w#rp``<#ndsU3y<S$8AS*<kLdl1i1Gn<<m;tM7;L*#Ft?G=|bO=jPtS`0^FGO&Eh0q{|@>w!MT6t_KLGFCi&~tgzDvtp7=_Vzg{K()Za@t9@?fk?~je`n#{33%)LXuYaXxT_NVAP65{55s-rkeJYL7{R7Wu+y&e}_N3;DI`uqZ%>*ZW6kP^jBu49N>r!rCA#uMl5+NiGu&h>SU-l6jdIM>%~y=#3Gcew7W?$GDtd|ib6Gj~xJ=GK{m`g1v#>+<?6s!N-D`tueS`S;2t)BI(Q{4+OdRoSBVkJly68@L^Ry+C=h>k=2d{_miAg}FPZR8v29kvDTg;<I{x!W{WzZu2^Zd>X}T1op@2yOplHN)Z>xr>M1OeH6EmXEAWwc7L9Qi+KdjdA4t?qIq$y&Q5=x#ha98D|P!W-HxvZO4InaSMJ*7&%cX2$2reOaFHids{go5<T=c39Iut1IOo~iMfneNZ#3nfIp^6~Px-e)++FvN<L8`zlgD#nwp4#Ujne;8KHDGItsg&%_m_}2=A7p+=R7la*7n(}|3;pzw=kafw%DitMxNah=X9Q3aEI3!<TK8BodLH#n!Jz3B|ev*{IdRi3Ui0Y)wZHE&O_Wp{*8}`d-bti<*cdmALe2z<)68OJbUXX|6y(;|I95uk1V@K?~|;5n)<JR^F>V>=V2~T7v@fx4Oo9h>-jGV6*-{W-@rP<bpdyHodGv?)jH&_i@B8Q;=Oj{kiQ@CJ+)`f{V;bH^g8UXm&xlAbJR;DSTtX3>u{j%C#mjc&9@E*>i9I(k+~Rw*D0y1^y_y~n|Qolxu{-YZaho%Vjizoy5hQCX8EOu{o}#HII%+9t+|W7-%?>|pdS<UWzO}rQC|a`>*%1qVeXZp`ZDMGidy67bM}$lj{5WL3Cd@j^ZE}i+E_>Zc{WZ_p2g43QGb5y+>|%>+Pg>n`L~aEdD720|Mo7*KXVJ`7q8^yWqux?U&yBy;tui|=Hi2#G)}I+8`w{;TII)5eVp@ep^jm0@VW=ib+J$vhx<qV?PB}aM{zf2Y?Ggd>tbcdLErzwym0d@r}<Lou~V9(UJmLK=cpHRyYy(y4dmI%b=Z#LUY%w1y5?cxF6U=3zHb@gc2ndH+~#q6AMzIB&NJ!W(T^7!Lmc(B{`z{EpSwIS7L`ef;uh+ghCf|^t{aOJH&GXFLWWg-?jrvd>JsJ->SA<#_q67`Ugf3yGv~T6x0=2e*`9g0y_2Jx{(RIydn3dxv}f)Pn?UXPx~nyP&(;}E+`@WmG|#BlTO-4b$o`p!`*;2=_=Uf{8RFdDG~XmXd;oEbLvdyht<TJPeFk@%45z#drggx*N55+j&EKHyVH`SN)9*T&$B!4|gt^Cc$2bu!&>rK{9Y*6e4gaxjBR{uz-G02`vq_OW+dF=4@H&if<u-aVus?2A`n_A23ye><F>!~_zuD;b0%30cosPcWSo`hh{D7y)4|tmVggEb~sPlGo-a_2tyn(05TN;kMfrs-J??04>FpuYf`^P$I7n`KlNvGP<=y3}k9=B$z<a2?%wV`=rv?d;(M=fX`*|&cWw71aSK3@L3pW7jB?WOMncrE6v^mB9mtN?ew-O=>9u(xzPeLn=;euO?3_L|Y>{vNm(o~*wQ;58{jpYNX_?)9hd16T!P^gRJ^v4%cJ_V#|2;^$s6eU5D9KZWmm;JD_{=g3yW!vSs#zZc2vo%DSG<`%d$kiG|E@p{Ppq|*05!ra>3A(9(-y%6SHcMJ86_rvddFu$5ioUe0E)4C)!^`ZP=T{6XNT9-BxH~9UEY1{F7?S<(2f~To3c$)fxr>QTv7!j)Psu!Z`3!bLF+&)}i@HF)WPg7s;H1!2fQ(x{UTwiV<t}nL_*O&J*Twm@dR9~@p3FV)!b9kKu=XvVg#X1S@#oy1tI{7@>^SbALMC)OQyLYf2g7dm(@_HEJF0Y5+ydH`++37qo|JA_$ID8%n^A7a8X?FqfH0O~J=k?Rtu`8GdtXI~6e`$PH&adn1UBvf<!OhxD0^F;X;evm@*qAR~b>ci<Y@RP!vJ;>20P$n=yEBLR_dV%)Y&-p)OVpy@yIQRa)Ajb!s`NSq+-W~4z^x2Pk^94($AgLSz&t!2n1{!Ml@aYxcXKz5hcI{V(s*FbbvG~`!kotg^YC~uVrF1}cs!)x7!O7wajv_UmBvGu8yFAF`Fv{Od}>@67dS3!1YHk=xqBGzSAg?ziTCk6tIx+r=AU^u|IEYr4|C2#8jd_Tr^g5O$2qg#@$-0|$EK|GbIy;|n|=ox=H7%<`aRLnvw`vEV!SzT<hbZRUW3QmD>*OvkJmbWbD5v>{(F7t{t01j<9O3>uDd;!>cO8!w8gwGc`d+2JMco+={Wn&*RL-{g>@73{`aeSN&h{Aeh+BAYw7kb^IpB8d4Kvnp!sW2`rRM6*O`6~XfFPCqTYUg;?BaXvvr<q{Eh%zjK%K+3)A}sCb*HFekW)RtVi<>+`CJ^6SR8a`%B!uC;d(^%$+1Rk{dOD4saXXeU5%tXx(ix*3ZRJ`dy*bDr11#?t%b!9)5@V=j)0Dj1%utkRM95qqtj^?uTPtxO|D`Azr6n!?*(H`kFkhz{Lby=kvG<af`=Qm}6Yo%palO-?;<mcfk(t&#(0RJMXV@^mzlgcYC$|y{&k<5q^J4+{{G3w>5KhrFH%y`YAxa!?IF_((k00x2E6KilO6zyyV76?&P}`;3l~FDBYjI5c31vEmkv{cUc(V#-==%{dKXpj#j52=Q@VCC`WZ<9<C$va2=V4>lo(oI(F|I<XlH^Yc76Yd60gG$lT!iZkkN%9=At*MT_U?x&quqeT~B_=z9*_59({QqR*{F58@{3Yu`CS=Ob_{9sM3tY&#d^T=y{Nx`%kY?%*bG7j-w=+zfE8J9F#eaLw)UbYB8{)j(Ze8{ELU7v|1Qx^IKssVR*IZvPqGx50jQCEcF^-2JlJ^Ljh4|ETY);DL)H2k7&YZ`*4wE)h3fx}SqxV+(z*4eotQ_j9o4jtg+32HnrWuF^HYtz5Gsxsz^NfScf=CEe%2w(0sU&Zl*b<nFM!0q(vvf%d;nTRI>9{!HIU{@oURe-GxOdOJE_wfjKd-@|@&BK2RfJwAu>mPc`;QHhm)ZsL6>YmZC!A-VDf@%OV3$Nn&P-^m)-pD>T_5BG!DkMZq>IB!?XUqyKyO!u`g2hn}ZTyV2B-M7l_5YzWRVJ>P_jpS|>x<3`~r}NBesyoitF0Uux&ce;KU0zSX%_VeSsrY&l;^M0#^tyxj7`p$PSiEP6pSw>d2l@|l?w@&l{R#Ci^3#3c?7Ald{oBQGf2zs<EQ{jC{S5;B^E&2yc$(h-XMTn5Pi38?`$~nmU1xBLpYytBT>G2eADe}IHl_PeIrWyL1US}1^Lja5cLUtZMfZ;~hR}VM!rXbFW1u~+pKdbU$H@eDi_?9jywpo6QQSzHr2DaWe=^hkqdfDs6hG(n*10inO(d`M^}0Ym9q4{g;eME#?(@NZux?xFZwC7*yCJ$C@HG8koe%fp6{h<>IeGsH_Jj35+z)f^#|F0>(tV%e^B0`Y7tRmc*7&)2xJG1q=4smZSP<PFJWc!NyCU1WjZ*(>-!5<$%biu7!|h7TD|)F+BDWaW$9D@$1=T-}(YLT1Qtkim7M4|N{a<fkSw2CChEnAa8^D)?FN<ixmxV8bm;`@B9?Mp#&k(o3ca)FSm+A!7_dQ3&hY{<;U&QkcBW{6LaWlN?^HJY(R4k47D12%7Qi%27kICn6lRAp{A$(^Xe;28)h>Z{%!asso9<d>OC8;J-6%ikUpC|jBE45MTkklsljqvL66H?oyjw5~q-%UPW4hzu~`_ot|8SydrQ?lJjsh!X+LF^T&B~s5oGr{&sy(%>eN(FlvkI#f=fYp@Ss3DaL%AG*0np9P(98gZM7u0xGb402#@{$d@KY`d{`PlPP(*)&H<u5ao1v!3JKK7i{(^8r6m}<93&|_1e$%5EI#L3VkFg3>VW6YMvn9c+#UjVTzd|9+tegXQJ1Wgpg%3#dpgYsi6&&T5vp$UT6!x)Qsp?rA$R2-i=&I&m0EXZpWsq9b=FqPMrq^3(%N4|4H4<rz)4qpQ?7knj*$E;8`Ff||YVE^)9|CGNM6XIW~oQb3d5{bPlwN>gJ#4Yd+;udH#*hZ-hQg2DUDYahe4a9ZuMP=W`q_Rn6k;*Lf5M+S8CfmI(wH8_vBeq29RjJj`DzJ?5IfbP%AwCGN9$zW-3fg3lDkSwX*h(lRMoh&Iq+XILAlns`N-y;y*ay)2F=8*mzks*`K7S%TKb=$&9Gg1M>{9nj6_;8n+ijA18*w9iR^&kC;)eV?QO5fcDdvS&F&}&#scKTyrTWXUVo42vl<xx#1bac&`#q@@kn$fQZiH8H5B!Jldl8Sr?}a~&_!azV`0I#&!e58K3n`yo9$#y@-z}t?OFfGC7}Ok(DK+tN<r^S2g!kmJU6DEfDgOoH9r!Qce;3sL4?KPaUOo1e+^17gpF>w;#B#}P<dzbM3Gf2`n;6A!W8{^Tzl3-hUd5yEm*9^;%6}-;Lh5m;UWjAid%-^iDL)<2hMx|<4e>+x57EE!RpfqFm8ykU8@``BoL*ABr3y*qmntBYET7X{su`qwEvb@-wGo@cPmr~pAvF{6dH90zu}o5#5&uXapBeriNcpeT_>kMqpw0<G-5#7`X2cBe_ra&f{^pU&3l#wSP3nx)S?G7L`tq2Qq)e&vavzRMosjxYZu^wf=ZFX4KZidADZdqQ3%rWU;kUxCgp_{`@m2VFh;tENg`b1C1o2h)CGg7-m%}fE-;B5gelz?5#Dnk$acl=5<xfJ&UrV4G-9bH+?w~Gr@c7q=r{Gom4*qL+RnJMXpB_>@A?4d4wuNs8Uk@rPRW3%)&w??cVxic7V@COch~?nR;ki84R4f1~Uk0%(d>Qz<i1py>!nZ+e3*QF5J7N#`?(h>J<tHLef}aRKN9v^1&e(rzjf%Svcf#+2pNlvLeh&JX3n@Ptu_ydw_`Z<x?Gf9-w}($ctOs8Yc~ss+ERR?Yz8vyi9#XzAVix$q@L3_{|3y7jUH`@S_zwPG_#23y!{2~Ehj<A79Q<KO`HvB|!f(agQ+@~HD#VrWtKeTpd<~xGr}A$g&PSXFui{kr`S8;aN5fBpe+p85FybJ172CiMhHncgUktG*d@=a@AmtMw<qJc~w?=FO-v--j4JkhmQvONA(eR^jJWoQ(Pez;vui{+z$?%gB{#(l?LCQ~rl%I{b1b#OBE0FT<A})hhaWnk8@S7mzKSewMui{DgPvK7>UV}dYe--f#{8jkhA>}j1D5~`(Bi5M$@EPIrBbI^B5C1Tvd>zEP@O81i)Pa<53Mt<Wu{(TstTo*r<;Ta=PnP8CK&e@X<Kf4n%`C);@U!4&BhG=J4Zj0%C;U#VUpo*_!0&+n81Xp#aqQE_h_m2lVH?U9!gy_t*c!e$`~bv(@B`pSVZ4pP*c=6}{CVuh1?U9!SLq_yPx3n8U#Wi}<qM*pC$JqA`@^f)%(oBCeEX?<A;g04DylvU;cw;d37V(sIPc-_!g#!}^bbiDfs`+*URO$~w~$I9mV_?_Ujnf>d~rOl1f+a1#E0OE!5fhB4<Z(Ze-OT)R8A@NwpT8x98%e&?uV4mB9%@mBd*CZz-LCx0-pu#Geg;MeU}wJJ7Ny_?C=jD=7N6!J`a=&*L}ILpLr4U`K}4`;kqy%j;R1*VfX^@g%FFt%b}wGB_bxkr$@XGF#*1={G*0cO{iWXvA*)L!BT^yx=JNWbw}(0-&m@dR8y(HWru%BWs^IQFGeu~r2JhxrrPjpE9JkDdQs{nsb{37AkIR334Rv*%aHOPAifB%;`{I^h}$9MKSF#TUd3(jAHjcuxDS3i;(n<w5YHlh0{;oxpG7<ae-{2*#Bbog!Lcj<eF7Ej9^(BzpB;bKmntn)3Q|5Va+??V&I_)57g@iKQXLT6!FQ5s57rUB9i)64#J2D%wuEm3&#!Y^;&p8!ytZwM*aW@_+9+R39!@o>>WG!$tHW18tO&2R+X~Nbg+ACf!{1He8zDA^uOpxTs8l^j`6NUWUd2Z64KR*Ps4*V<Q_ySgFQL0&9i`eyb&~3dx$rn*GW_H4oe?|1cfxZ!L&~>@ly5Edm{fDjt7h=65L?5yM*CKf@@)}2!Z*geY=k`27L*$mYrxlmuL&t%Rq7F`N~lLg_$r81;j5y36{rU4Sp(bP`YK-wQob%?J@~rt^%0Zc>%%uhYy{sBz6oMe_$Kfz5L?2xfNz7?7QQWV)do_&1EhQxL2Fz$LF->Pu&#(5;X9(PT@jPvE6RD;NU9-XCwLV*!apcgLFy4m`38s$;TynrK<o(L0lpt%fB1gzQxT`ZPlca{I3Io<{BEf)q|Qq1LEH_$8*TPL$}f<5TCP)LrN%(Y_d^^4uVPF1BJiychrkb#^LB{TP-t)>v8&jRYtUKj<2k9X;lF@akGoQ-QfClP!>j1QpMn1pQvQ2LdG%gq9=vxMLrjE^!G9N{sM>x9DSrjggTDfQ4DmGlG5C)VQ{g{?pMiD$(HO1$_2F9~wuEm5Zz1-EZ;jYT)d+D4q6KfE{S?G;@KfMtBF=!HfqhfnkTr`*J%pG5{}8;Yb6?cF1!7D1mUz4cr2K=B@&YjdUcmn>NXq|$7=u42bzbUI#DnlEZh-$3em$i89I4rePeIC$6Z9F_ctM|&jR%{HI0t?%{6@qL;=j+)ls|-c5dIMS1;q347vOIr{sOO}I>y^r)0+9#Fcn)NHiPdg$7C<5K8fU2?2oym=F|Yhf$#(1`yuv+?+0%o_JOzHdm{FN?+M=xu{(S>_^yb_@Ll0M<GMt}E{MtSUEm*wl<$Gq9li&AZ^T~kz2Q|3%E-Kwl`1Fb8l!^v@4TjbdBk$?<<MUFwNmS(ZmQbJaer9qAao!`Y*bAB6jg|kkn%&MMoT>@wM=S&)Ih1h&>*n&vbGzfc1vB6x+!%TQvL@>`JbVmz?6^0=<lE46Jiu|!Y9DzKs4Z0d<ed?R8^^JQboWkAy$U3jK?b>R)t?EwJ1iPzbU-~X372OBQ;d&W0|`hf<E_EQlIB4HWGOniku8ZUWS4z-(Eg{xKsy7`4NcY;77oZN3`L`!%s(C2tOTu5#n3$i{RfzTm%0${943a@N3~y5s$#9!XHJv0DlzzBI1wm7vXOq{tAB!{x`(?V&s2=PZy(@8$KO;9>n7CdEiSRR);SEUjwl*d=2==q`D$@L2L})9`z^*l}I4=oYZ2ecOVC>yHpRUUKkfW;d{ZW$DhDlS_G+aq}XLSRxU~XDm7Yanbf;df2lDj=XXWuZj9KUQWfOik3fHbIcm&FJt1{R{#{-^Ru1|-My$8ok9JbSppgm0o|BKgC-te+m-6pRQs)tm!Jmi!4AF)E41TB7YQ%MjF1(jO{oaOt0ZWwI%O&*yq<k@`C|DJ#no>=q-j>HUTxtZgR1o`3K2}z(h0w1tVsFXEhT%EG(N?jCWt-bEYNw+5yEOC*n2PG}Qqa#}L*(;^O1**jCcJuFwJQnz6eFgh`nv>l3v8^QzFtRs1Af1JY_ZhyF{)iz)K5iqOv*3C@sETY<f4wu>EAMDRO3^|QBqGrYD_7n>a6NLT<TfbZh_RB(9#5Af2%byk;b2r8h48QAoY*bb?o0>sn4Lj;Md_*+ud?|r`0h*%4bL*DSu1Qv8rQUE;UT;lhhdKS@7lXs%>rg+`r`WeiZZ_nok6Mx8_xN7cqSTc^Ce3#9Hu5%KwPIlvjPL`K0Dmc}UG0#a@$b#t5q0Sky|f9Ep^Zo5;-%@HgaRtE5&#-wR?t%E$IeeIoUZ{QCo`6zE$)?0xX-h~L0}EwuuVzwcw$R9*4d3Lm>FwH%MV7h)=Yg>9;Buf+bUef&;pjnog=?{qRR#ijNLlJffy>%zBdnGnmJ`2YG}O8@syovTFPe=r?>X7Fo#{%7u&eZ{}j*REwc^`4)I$^X;<Z?C>BB>o3?PALf'

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
