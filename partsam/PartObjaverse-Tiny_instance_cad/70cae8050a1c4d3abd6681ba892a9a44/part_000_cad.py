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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/70cae8050a1c4d3abd6681ba892a9a44/part_000.stl', 'relative_path': '70cae8050a1c4d3abd6681ba892a9a44/part_000.stl', 'source_sha256': '672c623845423a9fb44c996cc953c13ed48d665d4b63113a9cb6f4a804ac1242', 'input_faces': 876, 'input_vertices': 549, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18016831576824188, 0.14426502585411072, 0.10968883335590363], [0.031093070283532143, 0.3899739384651184, 0.28472036123275757]]}
GEOMETRY_BASE85 = 'c$}r22UHZxyX_kT9y|tA%!q@CVorzw!<fZ@m@uLP2#OIw#mp#*>6mjKbIw^&M+6gK0COC3&iSZ#`>VaZf4%FzwcdKqv-a9Qw&mB=)m7C!f#cUaV<smJe_XX3vGr<vsiJA3Y?_lcBqU-`Sa3*W`TpU<>@-J}%b#C9+qZp7zfN}A5N$-s9wCvz5hZIHO4bUkUb3vAWaxm1K@oxdyAO!y5h8ixz`l_odLG#;Fg!&6*`umwjk1O+rOFyc8U7#tWYxQ1I+pX~QQfT$<xbTVH%1;8H#*KZq4E>)C*^0$le#K5y!i+D539;et9{XaM|R{7Hzmr?wunt9RQ~){qU6SL;VL)e3Rk)L#ATIRJ^HBJST|bbrjovBKcbh)O=EJLQGV7=<=TlK395eWDW_GPun!3;Z}nB>=86kcZg@UH<;MI5bzWL>5B2wkX5Ce84!@4`+E@X(dq>pids*d%=5=wLK(FJfz1wQlKdU9Da!YS_m0Jhy!N0#1mZZE<X5?3c(LOm1<B{oSyvhT+tK3%UF2<wFW0f0kg`!T?cj|l%EpMn?>%%<xtIDkfjK@@aJB+inPEU1y=KWqO*D6OMcP@zY9^irYhx#Mmh4C<ycR+r6n7V$Z6A8&GKmE<B`WaMH<(7nDDmU$Yu5$BvFSK_Ur*doVjz?9#r#i0J(hKOPn-}t0PtkwxQOIW$RJqal5%N;8D%VP$Iim8fTP~?OPH%C2eG^q~ZL(VB=7$?pu5Dkaa?SJkMb*#wjZnvaw#v;L?yB6J@uzBU^_+?NmwR7U$GyE4`NA2<pYBlgE$1q$I>uR3Q75lSwb!<FM}Ou<Aa7nmjf1VtlN9y$HNw!JIP}x#(;M~Q2O_t;LqDByzQ+0;k$3K^>YF^Ds`kbl4RF3ydaB$u%>~DOR2#?jN{Uzg51ylrYdu~Z{qK8K)wk76K>M4{Xy5NN+80``+MBl&M*WM9S5*6`UKr1M1(Dy%q;k_dSM+C?J@VPRFg|u&RsYSO{ynVn+D}wJjgje?hbv#I+&H(K>W?YGg6sa}5!&B(Q@LSuXN-gYeU+O{=#QoFCiH*T9n`5j1miHr5yy=_gZ7=@U_4jtM4ip?D%S$Gsq13B?s8t8*Q5hD?yBnOPaYfEcU_14=OWb4{|f8n&1xL?%4e0Ey)I#V8ZSfp9Y@tTSR2*F^$nSa{%oIyaXaIM{#Tfb{#+QNa>KYcs=o35WYqao8~Lpy?7PK#BG2ZCe)cGV^WD%5b?m32zQb_Te^~<k+=>2MMrS$md#*idj_X_T2(IHkcl0wL72{TB9nPy<e&qgDaNO59lYY;Qi}zwZR>bu(Z~h#o>VJHK`hmxBUb&bb{-knab_X0c&wb==mZ;o%&4Ts|t|PB-5943>1o9HcRBp`p0rSDLCB}Kx9<(oGPE-AHOvidp+K%>?A;?GW!+fiN-2C|_*2RHC=>O_%Xx}a`?q_$Fo>O&FmZ;o1;6ASJ76Zn4;(Q!;Q$Fm6JJzZ8)|2B==lxV1_l7sdt<i8CckOD7!;U$q^Sue`S5L-z+3*14Z(j}dm$ta7@(i;uA3Up~e#tH>H|4&9@tIW#^{+ot$F(djf^kT7Mf;FW=+DQ=nCD-e(S87~i}}$&%yYAbd|U@rU%ONo{T%w^km~2>IIQ<h_0IgB8$H}`T~e1~z2A9)_Fqq_aW>{%hVy!Q1^I)q=;y6)H9khiG?km3v*EfVdLVb(f%>ukVqJU)MSt9vqRzE+?EkOqQGZ?(+J`Pv{WsWp;Jk`Os9f8*Mdg;28!&D@{r>2u!EPJIZBhXGQ~U?6O9m^B>)ZwPI~r9TYf=+jmz?!br{xCZJGpQ4DuFsLI;#F_w}+zrq^xM4?Ov+t&*V<(e9cAvQn~5VRh1hy<i<GozB{Pempz5?&xd`$=<r<S=1S;~twe3C3s;-UO_n>Vj_JW&T(8(WDz_ARhy3Xr%+CimRIb%LkL$jr5yt2HdE`xPs2@8Cc|^R*jSu!<e`vlO<KuY*{oLLk^K(oov_G&1`4mTW-3`4Kq5m<vkyqV{`MJLe`suY1=k+SzpZjpPHE8d81J^P79O@fZp#3g;Rmb*flR7VJ#^uO!ZN_uk<`DIKVw^M-`D$0J$KgvcZub3fzWJkZz3z6#aclI!aSeF>vwTm-b(zuw<M8io^uJyu<n4n||9L%}Z_8yEXUDFnb1wn=?YspThqb<F|F9P7Kg)uCHuXV!`(EmN%~3_Mf97tA<EA~pbs1U_>#kW<<n2FV{`Zc=_`G#QorAAYr};s&cd$qM=7Uhj>u=<1-yKkS*%US346#{pT@IXAxphlLtcwY$n9oi2p?#SRIIpr8Pi@(Dw2unFc-pnacqVRAx!J2c_8;FdXz#sL<=XSxxV~*&(Vq=dP-lHO&TC+9j6?Ytw4a0XvTX=P`?xTb+ujUS^V~KzJH~%cD2|)@6!WvhCbZ8TjJ#Dm`X3REePFE#^~?3eybA4t`-sH{`Ppc!mx4dl>jSfUJ@m8iDeP|@D`H)bDuMASwhsNt@e=bhJR9=$O)x%7eK0;h>{V_G^1(Vi*%R$gWX5sZw86fyek<zd{k~u2$E>(74|{|89Pvfv<_3lEy!wOp<vt%(Zk)Ci{RzB`^KJhEb+*}KU5p-#aZa_N&gdTK&(23UZmUaZUwjzuQ#n6kJlC96x%K8w?B}N^VSmVqTq_fY`I9#s=Q}J8?Z+HJotV6+Gjj*}`QZi5cTF<Jq2W5@8P4N5IbSHwD_{xgls<>+^41@9#?8lZJM_l$M&&AKpD+P+c6ej_EuAnA-;YNgb{g}|e>vLk>xXf$1tB-RQ`g;kyBG3|yKuhk!!S>J2O}?i49|_9gSn6Sp#GIZ*f(yK#Qe<J82x;-5zni&;_$qhwHE5Et%-S+J`C$ILk-l?T4Fr6jzd3RRKPe?n2x+(3||))NBh4Mu&?Hd#5|c%6nT|J7@ybqQKxNT<bF#rud3cboe~b{XQ`FgA6{I*dDTtdr;d97<74~l3HFC>pHyzVv<>&!Ej;e!G_;?V2hR^d?U9F`MLyIS;}FzLjf1&GqRO=jbMSoIDhmAx*r#&yJtO8rmTAb(Y`}5ryWstZWi3=4WAj+lITC~YFvJ1<KR*g}iY&x^t$Rm|v&$g#=l0hNs{hULy56{|kIGHi8)ID*tAOkHE)ebC&Bi=QYleB)svGh)J~-c;b+Ep62cSQ@1JrnGr*C2&-tU6`$Kd{G^DcySXY7c6=Jvzu%H(UfUWu)cCr`uvR(&?kYq~G;npIF|@*v!I%uP{$!dmpdS!UdK2G&PECsx4o%#jCbp6d^)sIzMmj+=e}=k>}9?Hf+OzR}H|?>|&U{i5Zueyw%!{y=^g_8<2VL+)vqCnJlXj{iu!PX88$@tOE#ujICjRyF>ngtOQOoZhS4Sm?CMEm`xT|Jr4hn@?21ePlGoN2_pA<(80Js8ier{rQrL_ML0sdGgpbjQ_eFD!29@g85+b#kftGiS}z6;{KksJ?2TvsmMcm;yKMD5p_0ALY?oe@ErSZY0S@6v1lK#8rNlIW}MfvVaRiI#P}@a^ZCS3oUe0d)t~=<|6z7Lv@eR+<K|{~Kg3+uQ{~$7>evrQr{g{qTM~KjC(P%+hhaWHaO3z4!t-ZH1&mMSLO5>sUg$sfJ#&L>IBxZ(80Y78(NFuoaK5HctoIr9F+T0m_o#ej0QRvF?if#(A1XI*X@L3WHxYI6|BF23C0^(5zk>aC@mrN^jVI%NoueuCjZ#-pf7J@?tM4D<zV<u;b^2Vy`&9l1@jglOIF;L?qA(6`o?-lJZ9w~t>+ych^nt3qvGE!l_uFI4|0&Zk&P`{k-1zMy*7bC}em5JK-(8F2J|BWQDHGApu5GbD$9Kg1FFhW)*Erlq+{<FzKE$Zp)NDWI?Tww7=M9FVKV$3Tb@y~9jKjd8=)Yr%s$*?Z2KmfzwjY4;nV@0(ed?&(64e#g{a|HPU#stp{>)y3dA=|O{kc>fdB7d?XYK^dpGT!tZn)^Fa@(}-m_G{*7>CVu(Ei10<cBh$eUJ8NKl~z&d;jNdRlnn2T;I((aX%gM1Nrwy*k}Acsrg{M{7~iE>$=E;ZexDtNK?7_BCd<=a5e0cwJ#uF<e<jiS`p7VTKp;0FSG{N@q9Ao+nW=}E4{;Wf}0uhbJQ^$m(PcWa68PmQoB`dEO#HTfBC#>e!dOIb<(ikMs~)29<@>Bw$)+Cr)R_Xd{~D1H9KPe?EePWtIcBcr`&d|qsPaQABe?qTeiXdacy<Xs~s^oZs$3upSBj`xpEZh%;R(Etpm7@$vu!e?83MWJc>Fs+oFDIDeMEae_%YT_^I4-=OXIwiN<~KhcEiy4&z|>!S`>?S#Z8CRnUGC?rYk@@4M7-^95smK6k);d;AXh*?8=eF$a;?exY(h@AK-uZh5%~>!QFdm77ZiqW<#hxGwi@AU_j{yyU&4KXOZ9JSU&)p!#V`N>#Zw=@s_>gKseouE}U$$%Ogv_!2(%2#iC2Vz*-*9b2X9n@$`;`_rS*{=s|9tBLziKM&sLv~s>_d3UPZVkv}mQ9DTO8@6FPRBl?cT%E6NkfX{?5nIu|<ZZOy(M}!L@_MDpjY%6YKK=Z$@A*%|aryqCxph@s$K8`L&b5xCeW$T_fB43Dw2z#O>mD`=`&)7}&Ud^U&UbJbd@k^96xv_Rg8SgkG^{W4VB|>yFb*3xV?2EZ;kb=j;W^nQpUN%oywQKxJ6K;$SE}o1YgHZNFg8*3)8M>N9oJT{8pb&>C&shdBYdv$y)^3l#Jn<o|EBt58u2&!voJr#Ek_T$Z(qR<dG%a)-_LUR6y{6%PE|j*6V_v%Qn<cvzpGpuIST9O%nhvTj~CHC#RKQX_kj&n6Ol*0!v5oa9-lj{S&lk$-l+EzZB4JCKPijQ-pio+V|%_A{VzOI<%S7%Y8*@^*R!fl+tH|V_%X(3UXU6e^ZrrD|0#leM+?>7^mv5It?{qaaSb=-r{M30<GAh`=Kqz^_}uMjPn8?%N2~F)2As!pTH8>xpPH;bUoaj|$8-DOAk<%g_tR`;;xT`21|n}9h4$Jr^s9R()HhYYbKS|37>DTAXuqi;p7Xi?TcUiC{~V3$;(H78KX()4p~F>u>%Au!r}>RB4hP=gx)}deb!;E%v!B(_4=0lvA9I5mDz~i5fcn2)*XJyb_AkBh+`euM=7}L6`u~XUA8z$VzS$A&FMr4WoEU@ox$f%@)jsqI#=lK8)?JC~D%XaWMt;dz^~bvEtjeu{iP#S-L}OkhoksgOZ|q~<xp3c~a|-P<JyQSP&@&42Wb{!SH^>|N$*pdvpY<T>m_DK1(qnMbF60?q@qFUi4)dYYc9q+b*JB^BZo&BP-Hi4}E1~~aUZPH6=1I$t&q-Cec6*)5%}%xO96M_k=9P7^%1v5X?Ax0^U_bXCkM`zkxUO+Mu@A(BBcD(j^QUlC%;%2*IPQ=-Sa*kC;d5PkKa5Ym=U8{ngH(G<a0}$k?yLUU4pl-wJv`AL&*?bd7Q<D4EV;^{ez*(9=Y0|M-{h)tL!Q@Y|D`paGdsHQd^!GY{m%ZLTfcV4>+1}7U&vCd2-;r_QT?=}q+>iA+Tpk^6VcBy>ycOewq4}~-(!3{8zujdm&E%9rXe=eZ~Ri_)-nrFXWKjF#=6f`Zf>w0`{ed+xNok0s&Z2YZ#>rp<ifmN@(6X@FQU$cqWC;z&kf|Bt+1b*DUAJm^mWuP*%bYG;)M0$c1GnE`!}fXUkaZ`M_5s(d`{dKf*)f)oV*8l){MA+1$0J#F05C%@kbcy6u61!953YNgS|1%GXhTko@;&EVSnh?9_ut@E%MXt@w#k0KJPFXmLs=deOaEnW8dgM7sox?4A(vP3OuJ}n2m8unuPwiwZ(ZAn}Rw+eJ~#mdZS*UiD>^g0r}?LXg_ou&iBC}yncyu!9HKpjN|riiT$D8Z9Ff{7>4s5fct{&hX<Y?whu)6S-r3xgK*u=yZWO)E;sP{rPCm+kKmrTE+5ZfpRDl(&s~Wjs8ee;K1ZwIr`ntH2O!^x{n-#cRE@uFP$$&Mm;?9CA~`UxrupKy&*q{|s4wai^g;eU0`Ctv@%_xvO)(B#{=xnhxft`dQw^2d@|VHBoiq{0olp(^ambBzk=h>5S1-I!Ct@V#!^iSi7walu{1XbGP6<Ek|Ch^QJcF;|KAMyp{q$y@X({Hv^#S&c3;A%|O099+L<6pGsD|U-v%~n_{u}Mf{Me@2@0o^q9u|b>sF2Gl*QzeS`v7&%A~&2v`%F(&KaK0YAir@^<>r41;Cj87g!^gh11h(g=HT`0-`KCTlN(XrZ5;NQDc3L`#;j7g?O`p<ANQYFU*+bZ{oBqs{~I>c_lQ=xVP`S4_c@2xzlnX&pZPOz-yGtL>o~9*>ih4*KA+G5^L9Ze^wY_T*9E?zSVxarp-!i>IPUrRxbA(Mpg%eDW8A7-MV*7SQRgD|M?*z3+B@gQxJ9PoxZC)C_zDNqzxe^zcjD)>zvtH7EAV_c?GpNbDiiVyc)!%r9q(&tT{EcM6cUg6(F@U^jbFB^_5}{2KXXr^KZa+>YwX56A3Xzg#vW0*@v{r&i2?T`W8{97o6GgY`Py*bv}T=#_W63_I`Y0?&K!mME#Ip4TIW32_dbQA&OqL;mk!1Gert;MF;~zZe&0Z=Sp)5RVt(3|;Cmp}I=NJ?H44S^cCS6?&*8UQRQrQzsB>W*p8u=dN1jp$uM_KkMSmQvD%ZmBoM~EL4cDd6HncxE5c$MUcwKpWp305GpWuCi&~iAgbu#LhSwFhiAGy`thWmBD$LP-iPt^Zf3H_YG?*)A=j`mASAm7XNSf~Gbb=<FMc)$8ab#<Ms-fk+_mbb_I&yk<iK5dS9v`*zs+oAndysxZ<j9I1XZyJx!D?i}=sci{Bo?(K@O$YG2WSr=)a$~JJXdk%^?dOFrQvLrt3EwkYxe)u6_GY0vZj-b4p4sXo<b4k!|9BpG_5|$14Kk_RIQI_v`FRccnL2raYCrg<%FW}EoAd6Uua4WhCBAp(_yX<6HkhUAd^@F{!)-+mtNCSKQ%U8&zDHqjeU0aY*CkYLP8h6mt*9ejN0@V=efkyjXJ85Bov+SR^>g5Rd&bH&kgrNXUKp=OEcy1J{>eis*OCh2zV`hw`s2A@<>m)NQ9m&o>NxH|d)^1NDQ?I+PF1<pr;<9Z_Sp-0LI<=j(N*QvVhxd3YKQvX=Tv`8m$#n#J=fxUqP=5FeC{*C2lbO~VgB4QAb-*bIX@pU#N9pjdv2UH0{y@3fc6P>kdLo|>+-=9`LOgEsy{!%(Ela)oJCvuLghx^s%YP%3i3yHRjys^hW1<QA#ZmZb+XtnK2Ak(zU8l|+&bg}&bRwUoUg-q<SC<YUaPX8&cjovvm2k+m>S)}d0CGk-;jduS?<RBuG-=i$WQb^e;VPr$$Wnv`oG2txw$g(qtkKRr)l_JX}eg|89WAgrji){EtAo{OeE@byNmNWjMvTD;9h87+JyNw!-)J|59E*fW89jBqRs+;)Y+Maaj1*$3;oK?4rZ*Q7WRL(e`Z8~^2H!;)fD6Z#(?YYejVd;xFL=^sTz)(9p|f+sfYHP`l3#1Q{)kuP=C)o95+{yKXNUK<M0UMpp|<#UDZEZ5A|=2MSlOX%C+zR<G9SNIRlYr;5-?0Z2Is0G4AtWKX<9zXc~iYUXdC3;iW1!kGO<!d$I=S8#x_y4iv*YIeQg(rr~Hmxi#jAw-MJjyv!f{{52nb<yQ9w=x6L0<jspCUwHq|@yVDE^^K*_|I?F@@6UqzH8{=(nj^P+FzxqwVoj=#y!Zi?8~2U<<9yA1=OQ;<#(vd#E#^tF2`bkdi{txd#%nm=^k}qCYlQR49gRATyP|z~ZyeX+i{oBxJni@M`Zb@;VU^JSRT+#!y9sFD>*v(p*Sqz3BeeheROROPO_A>(fjl%t<wnn57@xjvP{-w{%B_oI{+#EZ#-n~ucbu2Q4V-Uq81mQ_IIj^=s8crx$2D`GkH@;uKDNbiokEa1cR(Ig4RwC)!=?B+a%?u#ne2!2of(1lwbK7l{TzdNYpv52?M-PaH`=vFf4ur3&zGojZBzj2qy-{R*^Au16Z+GuC-QaMQ0FuDVe8e=$lpvs`#BxaetawR=d?lPW?OZ%zc3WJS0?n+xgCz1*dF<bxGAbWp9jnxd0r#8s@z<q75cve=cQR<&^~KJ)UVQq?MJFyyXu4XIeQ>K-g>agyOzTGib%se)Xqn$I#C|TPhUiSv3G<z?yQk`4srW|=aWKtRjxVUb-sB~Ou`>|5qxh$t9Kgt`jmm{eCzGR`|L4=@jkgzOXPX*`oYxf0@`<&9j@xU{D$`R2BZB8;{esq<rz@FdOze>dk3jJzboF4h?{*(<*6$JRh=Myf2;C{qgWS%yQt$j^}=&}wyS9G6xm6g@4bHf{_$DlBh&p=?)4t;J9wTzo$qas_rmvq%zn3#n|qH|?LO>N<7SyS1kb&Fz04|)eu6qPo#IsPaYW@>!<l&fU#&Cpxa-K>%iw+&g7+WH^D>W7{?~N0&(k*!$M2$Y>x1H|y}@n^Uk3$`ReztOBJ#P_@i|>Us~DVLS=685i9G+#iOSEtMEm+F$lDE?iSr7=?|Zbx`@ohww`QrIJ=SCX)WG+MtZ%Z+R{xIQi?TIx!|#vOte|ph`(^ljiemrb`fsl@N3}1H?+x4j8H(Sl2=zg}<_zAi;qRLmTBgob|2_oYJG9ksQ`gHl^x!<zpUo37UKbju+&b)q%8h-;BG2cma&ykjOH_Slye_iDW52N!PhPItuYZU4rxLBmZ(dfpR_+<{UHUxt`{TEU{5uV5J)@MSi5xU1Ei~}AUm226{`~U){a1#<JpZqLWvF^Jum9g)89HO9?*O_|=$FXim&xLH$>Mj&;?Kz9kICY1$>J}_;$O+)Z^+``$l@Q!;y=jZpUC1r$>Lwg;#vl<_-E$g>16SbWbyB0@pokLf63x6$>Q(H;!nup&&lHV$l~|O;@8OHSIH^lG)nji{We+rDftT7MhQQlzaopjCW}8JU#H)sKO&1iB#Yl5i=QRmBwwI}6Y0mv;s?ly<Ty%rH+>gbd@EUe8(Dlic{h0vCA^ougDk$2yqCO>65dZgNIuAM-%kl2rG$@B!Y3)=WO^Dojn^ZY5>BOrFVbyf8^`_PZ`b1@C47#4lYEn7eU6?;K1WWVgb&l>$Z;II!}LAmJshLMl<*-+_y~O;c^}8<2>mGeD97jsC2XaHPti}3PjZY-(NoE(JpWUaa1#9-If)!kPar4o9OCJR$cNacc)FEr<uT$}GoC+h*0o937F`+ieIuhTJ6+-W&;4}u(Y03BI$djYt=6?l*GgUa^>+Dm70~6TtC+6hx(ewksLNTGi>|`Dis;It%TZU}4D#8KrWMuYsw=myT)LceW!IHeS2kUz^<&)9bwZbe{<FQVzjWo$^|!8^x-#p^q$`WAje5KFx;E&#FZV@Vw{;cLRZv#}UBh(^(G{s{m#*z{d(|bkq>{Rd>B^<cQCD_(B+!*lS6*FJ?BpYM{r0EpFa75%y6kny?Jtk6+`9hOCBKX6fNfZ_<E=5Lt{j^DDy`mUU72)c)YU>)GpVg>r>+gU)>FdEDd8RTo#gU*@glm~QNpz;VK=%RS^TjEb|YuCgM>e5@Uvv`1LP0nyOeM$eH(cj`;|%wr%=LY=sU?fd7ft|;e(X$Ci+~m_&D+=@+?Z&OdmuRH<8WcP)gXJ-ij<<o9s`nM+ujugey_PUX*YhO4yg)irk9F^QDBlP{KXwgUEw;K0PVn5tMK&eJ*(}$19e;oV=Xl9!uXw-p1<}O9{`XgtySolEojBw~$X!!uRMh&+gHSkVV28C0vkRo}7<fgI=Cop7Xl~B^*cz|3e8!Q^MWpwaK+P@4HjNjVR#~^sHoYnfE35vv2`BNH`<?E?GR4EE0Z02|uK#kj2lC#jldZpOYVwzf;25?cf>gz~T<%?Bx8E@J|h%ft-Q={wF1TixN(vUnO5<|B~nj$>N*HN#s40@JjkDvbdSNl02Cb9!3u(i~Ey@k-JmEKJ<EI@v>wea%D=mI3;YLgx%?t$l_jPcXCBaxE8$*S=^Ugi`<wJZcpz*7Vk-JPY$Al2hvB7#be0>$)hRZN%Z+-@h#*@WD6yHn0|^Zevf>Ze4P^hM3;5@iC&QWYuyUJXIm%!EV&c^z6RNeT%8g&(F4hWT+b#-cq%2loDyD23D2WPlcTxL=TX8VDdA4^M&w3Z=bb3wdX#V(dI53)uJbaKaA8W=o-XU(p8k+5{+%qIo$c+phKo_c73ulO`MHiO@@L_HDdBVUTV(MhviKgd_)79Q@*zriHGMK!d>DB(c`79wMej})_aR4-J5$0&dS$YBak7!@NeP#ygo{wZh3N*exI4KpxhN%EnqHACUW;6sT%8hbKyOSIZ%=MOZcPbyqX&`22a>yy`%uE8=%dNvlgOjU6DZ-ObPHMhFnK9?KP7yHew{4-iTrEb3a8QE(%+NCW!=8z&%!w<VNZH>a&@j-PfEBmB|MHkl{}T}c^oCYkP==-39q1pE%c@2rCjG0N_Y_^97`Wb9?5kcO9}U)gnjAt$o06+eJSDklyGHwVRB)v=gRbA<YHX6l_}w-lyC?o+=>#eO9>aHgr8|}S^vV~=g8uR$l|NX&&Zc3;iL4aWbr8SQSxF+cqqLyS=>k-O727nx1@WL#mkdhlABP%O)23Dl&}lE2wA)^*@f&(3A@sZlEq7tUCCuA;TrVnWbp>%8sz$vuphlOS-czBj~qY=_onwDi;p7rCXb|q$I~Z}#g~%DlNV9KyXpJM;#bJO*152ieuJJy7Jo~=LH<YyXX9QV>pvU!0Z(!^a&b!7hu)dond{t#5*|zm&!8_PFXZ~4K?%>HglAF03n<|w^cCb4+!vNm!iy>4`SeBPMcfzWQ^FG|;r{eq<X+qt`cuMPDB%wD`sDgt{~hQ}$xXTbJ5a*IDB%f|u$dC>O>aeR#r>i;CES`4Zb%7NrGy>nMakl_UpUe)k;RXaMZ%9L;p6nhWbvWo<K$_Sa0I;*S-d4Vf*eK(_n<c+i#H|rAcs)Gy(r<fl(09w0$JRJ>`nHdgx%=QWN}xr8@U7}T#jCbEM9|Lj$D%xZb+|B7WX4JB)6l41L*-|@!sS>az9Eqnm&>&KAs#+{)ZA?L0?1`-%b9tj|j)pFVn4L@f+mJ<ad;CPCNKVvbgLc!s5lr;y&b@<VuvVAAK-cd<NN%JdhF|L7zhwpG6))9z_X{r!OFjFCmX7Posn<(-)J)=aa=JlEwRzCzB&7;U4rZ<SyJ7dQie)l<*k(FtYdr@)+`LN_Yz0Ocw7=o<feIggeq(lf@g7JCYkv!lmd{$>NUWQslgp@M{e&`-rgkaq?^OX-aq=eHvLjf-D|J7VklxN1jOu&!C5p#e0!wkS9{Y{poGV;@;%`<TjLWUAhNZ+>Kn9T#XX0N-secFGm)yNfvKNu1ao133s5kBZ~);JCK7Z;lcENWbtV7U~&v4ypTSfEWU)iki3o(UPYfyp3Z;2iV|K%32&tTLl$2_7LO;Nr$3;_lf^HSACP}g!iDVM@5th^zX<2#{!)nUM=nIJMhUm14<rxdKGKpB?n(&<(?^j<aUTh$ga=T<L+I1U)3{#@p+}M<xi1W%gnLrLed%H3FzyR|Dd8AOcrJZ5c{cZjxs>p9N_Z$eiX6p#VJIcso)R|F8;~1tUocX_B`M)N^t|M}+%xj<XW>_r@Jae<viLl*_)N0+4Dw0x2}*b`eIi-BKY1^C4kbK*-i9n*mpp*nkrHlBuSOQHN)~TKZp3xloD%Lz35U~z$-!K=;gs+gN_aLsh8)9nJDU>TObN%)*OAw8-NsSE$0*?h`ZDq|uFr(u)~)ap`WO0n@_DY?FO=}#c95`v{)7C3>)60`T8&(d>(D?6*P?`5(7Temavipyg#9VuZu9}<0bFn0=sn3jxvsiV!l9J#XnG7ehU;oHB|MW7o<yHcp3ZeOi4u;Wgxk>DliPD$wV{OTP{Qu?lH`(HSMHQ>E=u?%*Pg7mmt1!z$tSsfUefoHUy|=o!u#lR$aA<(_EEx9DB-^Jj^vJ94}Ixf$z3_``%=PVDd7e5G2}6v_X{ZDt(0&geKUD8=Y1k2e1Q_aNk2wD#`%5ow|Ou8nV#7W{)GI5^Ilja>|zHAm!->kD9d$WAR9Qp%hFqr%aR*Y!fomPWPi@rw)9YPDCcEcN_Y?@JeEF_Jd^WsEG0ag5)PtAkRv!RgDBzVl(09w4!I8Jr8gy9ni9@J&qdC~Ih%!khkS?gEDPHSU!;WB(x;H8a6YZ2k0p=gyje>LAEAVk>08NLId76F;cJxeQ~Cw+1<sSFzs(!rOnRTwb^nY0l>C%!gg<j0{Y448Qo>$z7qScIiWj{xxiPQ37bV<;5)PmbA`jxV51<bx59c)wpoE)I!Zqp5$<29<Ytl=TOY@r5q=cO*;TOEFaxGu*nyw|U<+XW1PbR-0f2D-K(XWxOah$)=)5+<)9^d%0aBe&JU*z0m54tPam1F8bZ$fUuG4h}{BRAtYd(fT9&OC1q`d9K-_Q`{N@L)gvn%iY?%J_f!U%>z8kGwwA{`eol|IdH<=hr}g|Ce5#+JC+j>eoE8e1AsEp#LWyfY`~qqS}7}aIwMw'

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
