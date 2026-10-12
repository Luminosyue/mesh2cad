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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_003.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_003.stl', 'source_sha256': '0335ce3b81c652887239594185a0a45610b64d35e603df2ddb98789f8977ff41', 'input_faces': 1148, 'input_vertices': 658, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.20506641268730164, -0.41094517707824707, -0.33450832962989807], [0.3686320185661316, 0.1827491968870163, 0.15419314801692963]]}
GEOMETRY_BASE85 = 'c$}r33AjyF`2Y908jYDN)G?2dNFtn!WlA(5IWm?~hA5(wA|-Q*G8`q6G7kyeW1gpw<_^tD8a1l_dH4FPb@qAh{XNhB`Tg{~&-Zh_UTd#u@4eQ#=RS34ljodbp7~SOn>1in)hio&o<x4Hm^ZZdpdt74>^->VfCnE5c^CP<{INQ%{jKdfbPjn#y%Cjr^&Z@FP~`^U%GdR&U%5uOa-RnV4H?v9K=%g*_3ABt%O3X)?w#@n_v`Us@6_ii^{%d8BV4Cyjqu3u|ME}XR234lo9u3q(pZJRk7lPdx%S`P*#SRs`D4Bx+t>JD(2wDVk3P1||9AM2vX>t5KbK$hZqWDeqg56sGV+g|Ipmjn(~u)UKk=UNWAm!M9rWXqm+trd>HUrd{p2L$d*km|<LeybM@y92C7<KuTR&dh_z{(#_~YX({^t&+KGqN8M_xAdv3_i4jcmUkDwy^<e~0nCs;0f}y8CCW^V>^*THmui{psrS_G@eX`oCqyB|Nw4UcdZ4)wlYe8}%FS*9+gP@X==9pVeta&`*>%zIW*_3z`J{NZ(5D_<2k3%g)H}ZT#rmsc!}IlQSp!<t92#+ZxOd&oF+hb)`*yzuWu?cTJ(+c4P<rF~(2M+^{8>A2~DiRlj{IKk}FH<K)L|JqLR0{J-yH>SO)bVB>q#$NI_3+iv#%-7?c&>&L^!PtG>&b^b-gw)^GGG5zVv!H<+M{b~JZr(Qe!&+QnOu}${nI$roW#tUDMR}??|!$IFqP>%Iu+oo^wKd<kzJm^R8Be!4jYOowV?$+1i?(&Bf-Qdr|Czfsu=6geppBQ{}O)y{26IXvdPwaIM)b;C~DBpKWM)~{k>;0PTx6_ud=9Tl+ys~~|<-ZgCa$Y*JEtnsfZ~W-AzMF&j-kq<^_jOigexkea!zy3TTj%R}YsYKhg0=qNS1|2$`HPI7xH_}FIp(=7N6quN?T3X;{m<bsX1uH)d(HTfL1w&MzPc~0ukQ=%dn@*D^~>LA=9~2+_=!$tzPa*0ywKc7+!wBVb$_{hb$?l3-(S&s8%%vpwf)c^->ThTX%g@ga|-&t*Yn;bLEmf9^#i{jcNAI`^dq;HHoht+GVsUu{p)2{dm*D7eD9Yki!=Nm2O58mw>-nY`3B#QkA8h^M)}2;9rNe&%<(HT@@xJ6p5LyX)7J(4*lnAAKfd(K%=*{eX5QDzk9D2w`*F&N+5Cr&nfDymwSMf{CcYn`p3Z-<xbMezn|4`0amfpZ{r=f#`p4ztdq120ao4@Nzwbw?n0|KoEo%6Fa=RH9>wDinY}ON>ES#L1AM0Vp*OfE7fq5TOe&V9T`~B<Q`P=)!@pb;jJ-(k@=*`H@PyD;_^`NiE*ZPTkw-~=zk+He?iQco8Wt6YR-Q|y)<@;Xk<+la>7=E<ZIV;V5g0JR-^}VOo`@Wa&)%&vpeqyZgBL~}L=AX0Itdk0={5-}Ft9(7*Tsc|anR!*#)Zdj8GJaUqU(Z8V&SQ0qU)c1gD`%APqx7fi2Q@#Pzi+)iufhw=_-a3K){L(!U(IKiujaF>f6b}BA7j2bU(IuG&B+74ubwl`SM$^P>iJ`R{rqwHYCdb<&S&Q{pA$d-JUXL%HP5ZD=ehRnJhy&~dG4K8zh!ptx@!Kra@72H<*51ZeCB`n-hK~f=i=M@!nI4?7w)?1zHs^KzHs^KzHsg0zKHkFtdG85T>0vLapkM~#g$|4mny11)qNDU<*WP1`uaYyzP*oPr_FrOzP-PkukJ7H+xyF1SKVJOU)^8U*Y}t6)%_Kp_?Pb|+g<Oklas8Itsm=9&|eQHI_Fs)^dtDO=Q_?0mJ|NI-g-a3+nEi){NzdFC)<_w*HH<Z|M>i6e%{oRW}S{7f6Vw^@xR{*=0`U4pWt8jyjI(S`H44;@BRD1ri}9EH1_M4(E0Q5&zk(CEx&UK|NR}FX6j@8L>J?G#Y}yyAHDlX!vA;OO?$2H^)!C8t!c0G8@2M+d$F#jKizfly(y+Yy-D<2gW=o!>$f%Il3f0eX_wm9SYPjJtgrVq-U@uRPqDt<r&wR_J6yinces4Dk8r-)M})24HFF<f{g~QEIA84xtgrV45q!PQx4vHITVJo+t*_VZu6(_2FV^LtU%omoa{lJI<~jLRrmxSDT)sL-a{0}wn)3T!elRybI^&&;e0}a@eSPla@=F{s>&#vQGV}4H3&Q3(Ve{2FmG$*GmCLWR%lE?#D`w_bG=A*Y-s^+DKG(9oKG$;o50iX9vbtbKe%Sg2Hmwc%(YG4x$}K;>*7z}<ug=X}zB)H^ewX^@JV>?Iv;J?H?bYXOuKwzr&GqN-a{l;*dz<lc<ve2iq#7@MF6Vr8F6Y|Y_(%VGk^9VibM?pfW}5lt+N;j-T)sNTbLBTJ;rsR+&(&X@@5Rp!G2=Tkp7A`iexzDIzn$R~&6fv#4?of3sCj?ca-QGm_j@cdXk#!xKHd27D`%_;=7;y0=eReg(UxF-bdT|4)#qgg^COoH^q+gl-{x=2sAnPLM^9a2&K2+zXC5=py)!1?`mw+8RlfJ?LuUU;eOx&U@T-~nIRBb5{&UZ3YTE0{uW$TtEz@4>CrixppL@xbra!G8E@}Ko)1&h<${+iI|NgSi!(@1vDMzh0tgqJ_*4OI|>+AJ~D_^ZQT)tXwSYNL<+;!D@!}@x?;gzL)wcfD4UT;`muQy!2T5niiuQ#l(*Bj1P>kW5Zz23mr>y60Hn8{cBFXyZMm-E&B%ldl%<?_}3OZ#^J<$SgOa^<W2m-Y4jOZ#^JWqrN>a@SS+FISG*f4Oqh{>%Al|D}Dq|8nh8`!9E0wf}PYYX9Z()&9%1OYOh3AJg?w`!83%+JCun)cz}nuliH(zg+oh|K<8k?Z32d_g~Ie`!DU={g=D0+JCuxwf}PMQu{CG>+_9^Pn+@^{pi0J!@Sq5AIZPj_apb@-ItpmJ^z=TK|gW!I^)0h-u|E;!w<h$X-CkH?l|G+Mei<gFzAQzy*CbS3;M}gr}z5((`;ZyejGpY?WGy{(V-vh&MiNTAJzGveeJg=rt5<rR`m%l?qGg?pxW!<M^t;gi7mJL^Fj4za)R*_sz1ZkPnw@+FfPd#^B?m2Up)_<ubzj_SI<N1>*t}%SI<N3+vlP4)$`Dmubzk2*Uv-k+vlP6_4CkOS3M71IqG@n%F*Ys)>qF%?YnbY+b(@hYp<)%X>Gnfr?vU|oYuBWJrA`X)AiBkx3+wJerwB7&%+$P>dzeKy0(0Mu50^EJrA|-&U>w|&wG{c&U@{3^?9$&*XO;qUHZJ&`uaR-Y7tY8-WOYcSIu1g9Q$A8yZtY|S0vl?=a`=kWaJk%e&oA++k<|N{jV)Y?SEZ89~o)db*y4Wegr?hX}MYFT3_#fZGH6q*ZPYl`+lV3mctq4;CnMpZ3y}~_P_W!_P_Y?t^IsI(P(Z)eLU-bJ91q{IVXDT$}K;3-1y$f%={etYkOV2zqWp-Mds(?s=Xe5LbW%?{@Uj2{k84Sl?VL&ZH)19^~4WvR^z4j*R~wJzqb8w?o4ye#(Z=AhM#1<xqQ99w)uL0ZR=U-L*IA%Wm}HgM@OG%V*Jv(js))`>n9d>H~rP%jRU#)v8!+19`wBhwaomV^2MRt{CK;%n}dGjmu_a>4l(z=%g2uuZts7eB4+D(Sqn4YIyO8K^pj<bpPXJ`ebA4N8?!67{KQkn4?nN+69xT#j8Y$0ezx%=MO1yd^f&i8?X`Xw-)nE$YyHTa66X6M4NZT#`ph<dxSr`x>w6zQxFI-RUV-P$bx*&L`SUO9zu3$7<7>x07xW|ek>7{Ek>QU!Xx1m=E*KQ_J^W<6@rsP{Pn<IE>q^g#%+Aff_nOri`8$r8_wujzjt}NX@MBNyU6WCtElbUFTj%3Pb^dEJ&HJu;W_>(-PuC}Ftr^!?W_u&}QQh7j%Nc*Q>Q8*{OlE(2FP--9f482$U`DR%L+9(COXBDFxunh4KWDW0`sa-JIeu<v%h5kKwE6nyfXcV)uCOgft&6lD)A?$hlf$<^ceB^kKSxu(`#BnZj-QL!eEoAVdtLoKiji@Xe`9{L&*Hwbez@H+|GxE_4%i#?lWmP3t2t>`(2t*6#`v?A?+f}-{OFN3J2T38_g_CRI(y#!pr62x9PYX!qdp(aHT76f_CQ8C9~wX2`s3{x_1RNxkMFDeD1JiaM-T5Y?NRlK;73(`ym@c>?TM@QCgaABsrE)Y|Kk7qu<FkUeq8lutmq2!y+*tLid28s_tiSk`Rcu9eZAhZzFzM+U%dylZ{LINx@x^=eZAgu^-=Fl?c4XJyRKUAx$@O|&-v;->&jQ}S?lZdp37J3J=b3KUben|FI!)~mtDKmd)fMWJ?XBi)|0M$^&WTiQSWirUbUWd?N#eZcU|?~clA{7eb+9vo^<t8>q+l=#!IaetgqJz*4OJv>+AKT^>eH%@b$Ve)}n>Et~!shzCMrAzCDj}<*4&0>+AC<=j-P%evaobevaobevaobevap`_0>6;yRJG1bJx|+ZQEY`+_w4Z+|1QeotwGq>gT*IM?dFnIr=$o+ohlL)>r3p?z-w+&gJX(f*p7LUa<M<9M6@n&hf0D<2_>AtKTEGeElA=_0jJUJFnDx#MMWgAG-Re^F!yW^Fvopb$;l|*XM`BPMLDL{F-@Ah#&cAxB0&7>hop<eGfnJ``fQ)<hSl*{MOaRX5`~1KbyHM=*P~t=W^3-&&`j1?5zy?i9VdOeO><kVEtp(zu|^e8TF~aIorw1d=Ed_O65Oc&&@LH<Kc%@ePWTi=Dpl1v%S`j>Gm$&V4m+QGyBu}i8Gn~8M|^?=J%!+H$I%(cv)YMm&;e<<?_{dxqLNV*4N{ueLG&(*W=~#)p)u3sPS_3QRC(E)p)slHD2zzYP_@`)9qE`rF}bI&R65*Er=Lj@0YEw_sjTtzZ|x{+AmvQ@0YEw_scna_NUHQ`(<}swO@9=+AnKAs`J%;+0|d|mtB3-e%Y0y_RB6`?U!A?+Aq87>izQXC6D-j|NXP(dm4?+&z-HGc(<4N9@61)%YuFk-y7F0qnya(a_0BnekiyhnD0$8e&W-*roA@*rQ=KeycO-u?-f~phVc`fwrmXMC$fk7^^0|zzBQPiSZ@6AtyMM!^W%4IGT)n5`Qf{bpS&eAKlbX~{`kdIeY}OnPjoc(iP(D9ZEd~}@S|z3^^^F~PfUBQAI_d_et+z!=}+rN@ncV#{<MDL{cYy^1NQp>-}f@*7k$S3-ch4W-|O7Wd=KZgFP8`X#2xq(OPJrM!;idN)BJwarrGBAtImxa%e8#`9OdKZC?EfSDnAi7eth{B^Sv1SXp2Yv??1%vFy&i6=4~;*U&HrU5(PT=e)#1A=KGe7GyO#0kNodVC0Ep57W5<dk(NteZW8d5C%XIlnb?&6>x22p<HnCXK4n!fKeqVz692mQB{v20W3L%Mw)3kE!TiJ>g`V;AFS~eaMm<{_-z%{=k&*voU-R=Al^+>r{6uk+pS1n(<_UkEC8>|~<4cSm+hOWs{mA-5=6gs}O?#cc!T70;Se20<uVm)uD$}3VkKudGOn+KGIkBZbZ=-hJ_L`RKcv)YMm-Y2{SznKr^VN7+Uyqmb)p$j1ebjh4UyYaZ)p%K7k5|n0gBmaE>+!O_9xvys@p8TzFYD{^vc4X##Op7Z{LwYdxHQi66H`l>?<<e#xg_XEtFJQkD|gqM*&Q-|+k8!nWz9O&^E`<Qy<%RU9)Vvq7gPRN&HY!+@2UI$^{eK!YuEih{;ql62eUkHbSeg+Pr`%XA?R3m2s{)W2M>iGMxTKnhKHli!o%T53E_$8J+SD#u;>K%QFH`40UiNAf{uqDfrp__!^7Z*(5K*s;KAq^crZK=eF7c`KY%_CKLFp4J_g?p_s^1bkmn6Z#VGVXcoaMm?GN|o-;N}N`=I?`(YxV3a1`wTi?)ZOa1Zn*ShOeH1MZFXh5OQm-smW}H{1&y36G>sz0fEe<r=~ZQ}@NXR4hW*!;9d>=tg)k{3e<WzX>lzH^EEcC1?U(0>6R21HS>kj&6WohhIbAhF^mhq+&k$7Wy_^8@(ER8@?L82HgN(12;t9fg8e2&;;BBZia4xo59V|Y`8hx6x|3ng&U*m;l^+SbRFCPmd9INbS=6L7F`Ihg<nm@e`qLVbRjGuoCjS5O9-EfE`}w9&qv>cC4?_Tm%<Xl7obaE3E}h5H(&|jbI{je3E?dCHCRH}Ll?jj!v6;5%D;s0KdJZ&eHon(zYMQI--7MjT0;n5k&5bQEwnaV3$BA+4cCFMMX!Ocg&Uy_;YRTFXcPE)xFy;QZV9(So5QW(7HCtr1sp*e!x8v8v;lk_Tpz6m*N3n2(sT4GLbxU&d?g{g8eI#Ez6!5~U-8oO_!UC<Y%0D(Poe+8r{L45%=OcJ7XAs%14{`1f}RUY2>*tj4@(IDj$Q~$2%kYOfF*=~MbCpJgnvfQfhB~0M6+NC;U7>BmJt3PmAU>sA$$`32R;dZ<E8J1ZwTS9Qt@XhzD~s-=vVMp<orPh$I+MJIJ^p71B+e(uY#+3>3gXvAzUdHHBwPA71dHv94(4ggp0yO&<b!7xENXqE(VuCtHUMWi_u!}#qgzQ9r#kXG<q#u8omr|1YZV+(d*$bTn=psmxIfrt>E%-S+oUQ7QP&fz?Z{i(Cgqba4EDtTnfGfy$ZerE{WEJOTxv8nv9R=m2fq<1|hr>T@8!A0<VPUp=aTF@ZVng{{Nd0{x%giXBq8;eg{hk--@1sC4_HBPs0+zozb6Q3E{5jFR+AgH}p4HLbyBnJ1il57kUPk5WW-r6_yb0g8mFk2;YJJ2uldxhW-Fc2;YK!4@(GlL{GvJ!X40WU<u*&=vT0W@J;B~u*BDl&&}|+{QaNsxA5PLwdh>*Pk1go2mJ#Ujl*-`73eBhv?{y;u8dZKMJvFS;VNiFxFYko3L(54T?wzG4a?EF@N#$=ItQLZotB}M;mTZN8UJ<}pL?^em-YSRR7^?5q*RPcJ^!Ch#WRHPv*>vES$HBk0iFm?Mkm3O;i>2pcq;rHIt_jfejc3;KM&79Uw}nt!tbOaI~55+cr&^Q-VAR=x4>KB?dUdmJG>L!0q=x&qr2eU@LqHeycgb&?t?`Sz=cy|P$CtDQc*k=7p0;oS`aP@=STCx`QZ!D^WY2MEc6^W3;s7`)Pp62e@Fib8I}<K4gCxL4gMAV6aE!GgZ>Slf&W0y!hgX3p`k3p|G{~(jGhbUfiFbQhcAQ+p!whea51zHT!=m|MhG_!nGkLgG9g@&zb_1zgo|XEF%;d87KZJ(?nMh_rRRh2ZZuz3dj1ISM9<Gk&o|-i=($<x`6;{=4P~Y0v+!p0Y+(MM<^DL!7})#eZ|<SL8MAkYKe>ngWQ?<kzqp6~Voq!#{^1__hdH!`&%)c#bKq^vza8j#u!Qg~G%qY6yaz1^O9<~nFM=g5Vtfw3Mfm&Ta1pp9<1N|<Ee=ZvH$;oV62jM_`C$p+YtRc|3E`{JELcLg4l4Iy9YVM^`a4`3u7&;v*Me)Jzrr=)E73FXmGD*QAMjOhUGzV=E?f_l`>-CLh3lgi!V<y_&;qc8@O5Z0xES}J@YkvMHWi<vU&5cm$I;K=<M1cwNAM@`2k0^Q1NbO<7(NOgLJz`+;3Md}@DccZ^gZ}}_+#`#_+vPUehMey6X+N43HU4Y8~7{uB>Fvk68-`G5&i-G8T|$R89q%2|3nCnC4@(#Kf<HoQRw&ZD0n#f4LlqkihcnPg@>S@!b9K((GTGV;rr0{;QQcy=(}(~xHozb?hW6A9)|CM??;cp_rn9xkKlpuL+EGlL+~*4OL!PO0{s>q0Y63vpF+QePr=`X%(_VQIrQsLdL1P^75zMvUUvykMvsTm>onns=qI7{x=#36^n*}(9Vq+^dNh<?HwuqK55eQ$r_m$u)9`roeRw=P0sR=B08c`b@FaK&dIFvTPeZ?gr@_<Flkjx-1@s5_1$ZX<GdvTXfu4qEz;^9=n(-0+3H}Z~#aN3zf&K)Gj)lKWy*j^0#R)VCpMXC_KZZYrKSbY$KZM^ykHGK22hn%ogYaH-KfD*-iSCAX!dubp@K$&;x&_`0Z$o#$+u&X39(WhL4?O_ygAbvH;Y08-^eB7`{)iC%AQdA+Mjt_s!V<!R(ZjHW@B`=pSVFizx(AjJ?u+h#C4_sSTVM&{KInE>Lik>EH!LAM0NoEu2oFNvg(ZX^MvuS}!jGcw!xF+V^kY~;_(?PgO9(%OegR7ej|rI&KF;5N2_J_)Cxi>5C*Z<xAwswS`YBuh&WC;o=Yuaq--9oN&qoi!=fmfsd*O58Jm^k14;(_bdhSOJK6~h9Fa1Y23*821!RMg6;B(;f(0%ZE@CE20_yRaDdJN7B=SM$+^TP!R;m^<y;LqSsy!8F^37>@@=lLc&0v#Djzwd;Hp^t>p??>T>(7~bf`&4)!`amfC{uRC-?H@|NuZ8bH`-al*cj4Y>uTXkDAlwh_6H2cigzrP|4W-u`!VjVYLh1F1@DOxRD7~H$9*RC3O0R!}hog^%((5JRQD`ibUSA21MxP9&*JHwC(WgS`^_%b$=ot73*seFmFg~Jk?>)}v<BaEV?n67ipELdi(TmW};m^50g{!6}ag|h5CWI@ZmEekSd9(st9xjWPgUiB~qha`RxD0w3Tm~+MmWE5gm!Oxzq8G!@rP?qs6*JHw@C<ks`Y=2To{2sL&xEI=gW&1#6!Zaj3OoV551s&zNAHEl!%v}o;iupy&|dHp@MCBX_%V0{+8rJNkD?!>Uk0F);Q?@e^jWw+d=L5zd=K0Q9Siq?d!nP^o^TW$1&^X`!WB~Uwo59)=xuNqE{%4COT(9<9pFph5@=hv1Y88Y0WJa;M4Q6};e6Cb>US4f1-=Wu8?6D~4R=SY!rkGnXhpayd^=hez8&s_mVrCLH>0KCo8fk7Nw^(+BU%)`5pIDNf?L4Xqxs-`^oj85RJ@Xkm8n>c&O={;MO$PUo(DHeMQyYW+5)ZvUrh+NLZz%$d=`F{@>j#J!fR7;2YL&-8omW?kFJE<!>t4DX-x>XOhr?4DY_h93eQF7!J^W(xqKGBKG6Q_3E^5i>uT{Vtc7o%jkS4p)~1i_v$PJ++B)=?efC}*cs>hXgSLXNfp0{m?{4I?@Iv}?ExZt37wF%0gz%jqbB~DLhTZ|+26senfjhz-(DrZ#xGmZmZVTUlwuEnhn+L|JInk84x+WF#Q}GtM0DcR88+{Fa8{UAv4sU=r62gm9(JsqqTl95ULbx^h8Z04v1G)f~5N?Uihb4rYXPFRwnZI8HzYMQR#ZBm~=o<J|xHI||+!^kMz72PSd!QTO9&k@|Bis{?62j}z#qfG~QK0V@@maV{Dy~HvqV3>@a09e0+yJhRwubA&_0SvOdT?E|C0rN23T+Nw1z(wpnrKtBIV>t;(3H=@amHm89EVo~#%Tp1+$Ln6)uK0}H-*yAcHvIwt)cY0K=^jFb141p5blb03#H#R!rjpxq4c{+_-?dkDE%%Iz6*_p((gXuE`;!%=z920cpbVZlzwgqFGOXG?Q^CL&mlVx>~rZ_o?8{s%ILLO={2fwRkR^o6|RCdfUCfj(E4yCxB^-at^k)q>%!&WFnSdnhA%^}gfD|j2j)|0LfEchMQfln;TmuRZ3>IZ+=}p7cn<Sz1w02{hPHv1!L0)GuN8VD+zM`nwt$<#5%hXkv?&~c-$a+fZ^E<Dxv;3b7iaTXxJj1LT5uEiimddz^9r;Sd<9$`y#%ffS3@s`FQ$L15yFkp2rMf7*qG14v*_Dp@GN)<+6rz(e=Q+|-#{a9gnoI05Pk`r4U0<qU*fZHBl_eD_zK$Dh!DOGtp-=44cDPk@9X$1{32~x0xzLXFQPBOqH+!4YT~8V@>ig<VF}^t=u5DKaAoubSVFiwIt`W(z8swdO9)?rJ`GC<7e~jy62gVi$6*QK0wEK^BiUPxWbZYSe7hHWoW0uPlyCQLW7yk`p+0u6_cVLKr>Vc)8wyWBr+MkUr0{g~1uwn#6rPE`<fZqj!n4rXUV3jUJOh2vOYenWWH0y}{5&dS`8=P6D}~J7N3;rB4Xy&$K(Bynz*W)ea8<Y>S{begmqp9NW#KaD<!~9e6nY6<3NDEjhfBgm(ZX<1xDZ+ZE(FWIXKJb+%B6H7dKoMsJPy4WmJogtEe1;n$2=3l7lq6|RI~(IER^223SWv|97^wVg-fHCh0^<C;V@b*l-@^|V+<?6l~8G0B|cAO%%4Liqf_C@@U!Sd_*wWFbR7H)JQjTt9t)2~WAJEL&IU%HkD@VHRQl*qJ`3j$^kaUsAe<l0i{^v#F}`_GxwrH3S$MdYzW;}#Bj6ESdpIiB5N?}_HmSIQ5WW#@2j2*{M%%-!;hWG7@J;Z|Xh-;F_!hJid<%RVdMkVz+!ehY?h1E9JHy@JyU;H1UGSZR@ExfbiavsNfggc~p`GDj@L=?Icrg4RdMo@Od_UR=z8~&~c7*%Ez0nSEZ}@Jsz2!EctYUfor~mb7`j4F9dKv#CRQ)eAe~m5pF9)Q`a=+Bpq0PB+_U~n-{*%MGKjlQy`+qT^_ze'

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
