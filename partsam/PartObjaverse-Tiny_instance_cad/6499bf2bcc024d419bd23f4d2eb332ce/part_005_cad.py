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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_005.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_005.stl', 'source_sha256': 'fcd6a9150c7360c9d6022563a77978f8759f875abc99dad0921604cb83e3bd40', 'input_faces': 732, 'input_vertices': 427, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15864312648773193, 0.03945814073085785, 0.208413228392601], [0.1718679964542389, 0.2419186681509018, 0.2449273318052292]]}
GEOMETRY_BASE85 = 'c$}r22UJvN^zAQd?6IP#v0SlWFNnR3A{LB_z3W&ID|Ul5V;9AUU1J*?*4R<(69G#EOEhXsj8}~YP3*nD`<=Z<=Kj}vYrXZJS!eCvY!2ss_iMKdD<RF(rt{YDuc$V&;`TYSN@<#kteUqrCUnH80ewP8RtO(9)=SGFzWV3Zg)Q5+2<hyljnT&Y^$i`_XM|rZ-LFo+8h+(;zkWkUj2h7^yywsneM6PsxYyv3p{75wf3IPo=I2rY{?*IrRZ5rBC+h!?|1zsK3~HHh+!WV`DF^DCs)w{at5j=HLVVkYtl}FdONsAllMa4{$@|r3`?U<>J8ci*#qa!2tmLnI@r(HJe~Yih_S`Fevtp9(IP<&suH6kK-+uBT@(b>Vzoa$V^UZi1cjj8uU-E|>*SOYDeB17M@Yl8y-`Of3{N)bRc^-@U-@ljonr#&P%-(2ciO1sG(+x(Q4TJZ|ai>2K-*GPt?Qc~<+OKaZe%9iDJcaW*lvaFW%Z?M`XE?b>>OLrn{E&4gJo`ak^;zocuNRB&Smm|Pvmb2TqQrLv#h^W5|A}vWKOJ=*23yX{NaHx++5h^^{OGs!li;@;iT+s{Wc8CC!LRW>{LL>8Dc@N}j~D;V<|I#Fzwax)zWsyv+Sn_WeB*P=WNFu-OXAyqDuDcr9VFkD|3~qSM?T1}x=Ql(m5Y$SH@o=ubD1RH-n1d|Uu1<}>5k;PverWW3JrDq6Vd*Jiw7nD&yOdhZgi1zavr~&grD$8d}IC`$+u@|DZakx0rIQ2JcoI1L;i(p;@g9Jp#JrPapLc}41d}%$+!7#7vK5k3Dh}U5BcGR;2%3CzVp39@*S_Uimyj*L!I>%F@FxH6W><Pf%$(dFZ%PNm-wzj)8P*vh<=N@cfjHgOu)EgzXgBfLag6}Ba-hZx7Fh70b?ZJv2%m?w*Fg?zao>gQ)@Iyd?QN?&a3Mb@r|S*;@ht*K!2vGjD4VM8%rH$%}QvG9*pBIJ$1mdpN*@x_FMex&oM6fZ;J1X`vJ!d9EowcaYcMv+DFL0HWR-6qWJpl31|=Z2hH9U^&9<*^STs|ehv*mo$@|$(#|5WXirKo>Lf&9ymGh4_*SYbzVWah#_Loc)PHm)R_cd)OC9^&b?}ELh_7GhjXG!jP=Cxp<mU;*ad%v{_<CGh<R>pgfBrEFeu^*lsiRKmPrc9x@$IE`_?cT^9Q*c-MLT`4FXVVGzOk(X{9(DU@9ckv`B|a0_|CT>=;yQlVO~9Niu%q*@Xwu-eEn@*=6m6|O&VZ+#+MP_*3l;CWn`O=eoj{k`JZ2%k<ayZ;<%X$p&yP6NB+q>SQmLS;C!>(LcVhr>aTgVPwL!ifbp%k8NTmR@%5OR=r_N-*st!Th;M&>QR+C;490cg(-GuP*)P6sKZ*05d_a7oaSe=b=dR*APwc~S2UbS?PrcEf3zi^%TLtt_n^=qQ&ey-nlx)r4fcEtAM?Wl^BfjfnIQn7dJdAtM@#5S1I5AJcZeyN=_eT4BOp!YF#Mh|bs3!a~Lr{NgdhYX|_lkeCDb6={0jZ;h|0lj}<0>5Y)M{L(V*i5wZ4&(G3z+|hFNyCw?T>NUd>`{@)gtljpEBdPP0M3F?&~kUk?G}WY3GwaaDA`aNqpDbGpOI;80N{eVECh7;(P;lVBcO+8tpgEqE5fcm?w|l?UCa~?Gs<mW}trJMe$t+o?$(%{ulju_9T4Y{0GHf`911fJS@I`B1-BQKNZ8icYmJvM)H``XwP%Z_o+Rsb?TSEd~4D{eCN-t(ViRW(QlD$#kaMoF8M~CK-4c>9{J_!;=JbP!TNfU){^hMJ^<@F?)`2#ZsQg>Zo`i<?%KOI;@j&LMEhS{hu`8i@tt9r(f(JBF&}<Qu+(wx-jDWoIu8GH7u3(X6YC--2KARdJSFwpuEo0eXT2rgJ<qk$YvE6@qfT5mT(1M>pw3@6Q73j9_Q_dc;_Guxi|_R5f&7K7;m<!RzCC*q=7~`Qb;j-xUw7t`d|Roq;u|YB!4E2c`;7`ZeES;I`PK!0cLCH-vl{;L!RY7mzT1?qE$OjE+OvHGuA93GitmUXAijIwa0UOnRq}^y6W`v>2jl*9J^Y5Jwo88ZM>yY)bH#U5&c9Xi%l5@Q%r*r1`pci>xZ%mT4wh_y{AV?GN}Xkg;cux8-#bL=I0r;x|EZe?{>{K$;{P6pad%}$ePfU0>tUO4+@!Z#WWLQzLH^TI*eBcHhyQ%qZaH4jdzhcs?uhT$6p8y=UU&4ae~GW9<PcvUkQ?*r{aWPLd?&{>wl>H8z>;C`#}C;i{^pz5-#S0rEdIBN+dRindlxIdmcAMK(?9chX@6rs<hP9x-@fb>+Bxv<CdtoGRr=FN<0tvfnytlm{JIo=?>pEZx@AYcqw)@^)2)i+>pMrsh~In>{Ggl2Z(l)t$D8sPmwFW?Un}wBM)BjL#dq&Ndectu4`)X|XDlfBuAJvLh~K-O`1;U{INv=B#JAOVh;MX#gMD?hH}d_qi*JA9kNf0>H`a@P`Y!6cI*EPe+)((VGs!p_H3wl_=09DBe(nH&^bQ>N=jGyS73X5yAHGF?vq<rc;gh7U{Y)bKq^aWTYkR@}oIBamx0i{6pLYb-SNoBu<5L|zud{C7nROQYK7}!_dUZ$rE1$3*<y)R?@vn|L=eb^7j~l>`Y=i6E>&ckUBkQ0&KOV;Qa^f#&=d^E-U%V*tdEf5LkQeRo9ftj`%p*RhJYFmL34g=qbyhF(Kz#dL9rq>2(_nq=jYs}KJm(nE*Kr*=7>E4pNjOhlFYGNBzz=AJ`bCc8d9d9~@tt?aOTM%CTeLsLj{3Gws1vpu*TF$uk-xJ%=EvR}*q^6XgdepP`^B_aJQt@g1HV1ix$~FZXz!0{QU7%p95??jxUVeq$tmr8wFT!NITq(#@rL-iBRh`kexBWPReWc31oB%{Lwk<>3_lS2yI!scj(`8tDCxgHs%((swYr4<SwCg8_(c|Ol+WiHVIBtgkCA%qDv9sjAM})4;yWCNV<i7X5zNEc^S_h)!!2Sg>%DY?2>JPMZ#SVno<kjHpNOw5oFTrR+!FgwhorHh#RIYbw@!zCeKUTX__xn*7XMUd$v38U94~c7MPVOqj()P0%rHUn-PeWScF0fI51;#?{YV+)hxMB%b!K+NKG~rj_P0!VCt=>*mi^FquPxT~_C)cu(COkE&GMhed>j3}_~mZOeyE?Bjd_&ut@w^>QR3UD-^2PS|2R_W{*LE)d#D5RWO&Ot;*X2QJV}2D<2&Q4xsuoMSJZuc7xOy2GW_fVkss!Vai5a%gVfuV-?ENugS_X7A0C6_rg???&mA+O<@ZX3B0nMr=E=I1@VDMa{=Q3?w*{8Z7ymQnxAWlFIIrwG#Wzk=!TC&bNxp0H{sr>;aqqDHr%}fwiEk{&`RlHuSl2I)E|j`$>!WV9Yh0(7;O9(2{@Al<&yYil<n!L~*vBr!px^o@!XK0y=hG|&`L7o*7C!>_$L{w4+B2v4MiV@*8kN0qpRhb=iPXJ==S<zF81~zRA>!-ze}I3f1=e5NGw_!@#Bpz3#(ZmWS$t#OQPk)2ovnD$rII)4FZg$FSbU?>Yn<2IDOjgD8zMjVbNJUQU|y^oC+o)%`<uKUb5=Nl<Bm8bzH9Snyk~1Y4(rQRT-J$W^Jlr=a1IT`I^7Wj|4A6$vt_%2>tNbt;=3M=$NdTKEA;SV$bbA4{-unvE^PJl%DU1fKEQSG@+b7?);jPb2I2naW_eu4mvzT|%$o1<T*mtZ{mpXmZRbOzj{E(FHZT_JxyMoDNAANsF|f`ZO|ByUQXtm#(F|D60gLdQ6}%kJYZZ!#Z!-?!exT!99M`9n_*y3$>V!1Ie)ZKb+&{UWuOlC0zW3dZI^m^o|G<68(c&8F4A=sn`;6PyV|Jqbd_U$aTuJr|$IyDXFX|Y8agXdEzV_M&b?*9}_w@CunX!H@7UcV!^~euzgZr+6VVDoC5>Wq>uhcgVy+!`nGuWs2yl(_nK>rl*lizoIs3z*Xb^`lJnzr&;pI9Bowb#LXuYXZ|qsJTcbNjC`UPD9Wc+P~r$d71_<CeOQ^K4Qa{$C%UgBsvIFY5wJz9SO%bNam2@cI5$w<jZi@ezDpR}<^$IPTk=S0>@Q{wfRKkG00Q+W$tr`?>zZO!&vQB7b^WjLWq%@OR*T#mM>q&rS8-<NhxN`=g%R3FlkXAM?A2FOJ9OK_j>;*2&8^$PZtD`lF_aZ?vn5`Z)(+Ki;qo`6Ybd_rHd5x$Hvy9StyFYZt^mmiaRL2#lZm`Py;f7W}URk^j#b%!g0+;YZhn&-a<O_>QvvZ7oI~m7iCbjO$FNP4FuQz<*X3^%w2LzO!X!f++VTM@%|-|L*d!Bfr%$jAOCP;@f;491(xlSE%pIj`#J+4yj|*dw_OT8YsRqWIyWPXn=XRX&mZI_(tkG_npB!EbhQ@Pb`)Cy5AqzSM9S<XXgaeU$qPU+3z{NKgfO%{+;2dzwSNiY&<7*oV_0MJ!)F{p1}63KI-p3j`3;7??vWEppN@Fed$c(FC2?Hue@--<UJSuhTDh5@3!}>r>~bkiu0|!2<`cK7rwW+G#dW&e#no?E#E`9(iTB~dZ))eoGHKfHt$(d-#+dD&i7*leE$@64DHMigX>BE_TuZKM!_G_5&0)pqRyxUspH-^jE@`Or>TPae9z$QbH!5M{k*K7|6r-_UN6RYUEVLd{vLq(&3HY0Q$l=O*?Wg1|Hxy0?=b#=rGIuT$GA*bg8cbD=ug*PT)%2Bhu>-g>P+^<b#Tnu1D5{edroJQw`fm9vgA7_;r_z*9p86{A4>4_9mQ+Md5*jOGz!mCWn$ty=k1sG_FWR<Jm;bP^%0!cgTi>PbZHmzmw4m6l5)uWcHKXK@9*6Ez*ww9SH%GIYqS11-<?h1r!>Gg@V&bI_hI7O;(o$B${meyNuB|};xWuS_xFaedr)U){#eg()V7`$-|?w5=6hIgjAO`a_{*kXovqu6ehd2gnAFL>aGzz|%hwd&@o&mr%RKRICB9bl1NN1Sy|9kXOcdWX7W<QPAMU>#pQ2HR_btxDV{yKv4xx_MMcn7y?}z=NM>6U}U|)2WbYdN4d5Zkw-LWt7eW}?|@;=)3svFwb@*nK~SBr`7@c%=6_w`r5Si#~O**aie{Zv(a?cM<FH!B;VfBFSleSV+iXc!FN{k<pehuywoA@(7oWp~W0wawAar#H|Z-p}ik+Q8@cv+nD){=TE7j{QkqjC(aZ^4p}xxL59c&eL~I*ogeup?se_#OizJK!1Kc0(EL{j`i$+=h;!n4{fsFv;FpIQ!Kvw`)H><(&F29^uV~dX2Z{Y3-kYd5c)I!Qj72Ye$DZ675tM!@qJdM!f4Nk_3$s=!Ew7ZLH$-+E%{&OZNGy!FMf~a4EX`|*ZmBC`Up#X*OIH&ajcWf_ZhdX<HhGSd$T8&@p6AJpy_GiJ;%k}PNRCxc+WcS@9&I#dE-6%-)M*TI`)he;yvrT|E|F8f9Yr5cWEX4E%lvaao^$U8Wiu@Z}vOYaK2-kS=y<O%!&3~3$`5BKBOSVcVs(j{Z+Maz24a^-m^dLS97BNke=4_+LsOOFW1}JKYYJrJm_mVuJhMid=DHJ?>R2cKhI))tsh}&kNfWd-2Rt&n^ef+f0+-tZsPe^kFd7Kh5NoQKHG2qpkck-9A`bQmxl9QHPJd={JRU|!z4@pyZg;iW2U9woFzli4@+lR+G+2<3jNSwj&;1+|BAogh>f!LGmq=`zpPW<SL>tZS=#UZ`<5@h`|m>rm&CgBUtpaN?(eyhS6JJ__XEb9)t2_?9}+G8mww1t66d>RopnC*y@!@*gS9=Z<2V&#Ij(WMF6RG?E!J`Q`zhMlXuEZO`nSS$YQs;~erx&@-iOpXV4Wx4GtfV)<E-uHbCYrSh;^R0uNMo>S&pm!Tm|bf<f7$#b+6iJ|LI$n<LY<AFi&RuZ8@&~SjT+(_`<R-^u?=_J^e59itkbF`_m*?=GEGG>~G;Y5-js!#W`Fzjj{=r`JD0u{<EM2OaB*6hwIC|t_hZLcYi-vaA<<%eEELKIeL78WnEVsg7-!NlM+17*Zp4CIEUw!Fa23&FP^8qoohX>lyUste2wM2oN-IhKRI0g<Gf;VUbp_VoR_<QoWDJ@oYxn>%^OSm?N$BIp6%%pE$7R2x*BIow4B$wML6zPITJn4%l%ww{NbBuna{U_Q9q?gqGdf+?Tz;M^h@+?zw^Q%<bM~I=-EzVBj3jlnwV%guRURCXR$e!_8Sx0S^O{as&8ia4dz+S%Xk=o{-3zi+Ws+kPpNNmS=-O=Uu@M3OZ)XKeBXceg{7U&^DmK~_}SXdTDPpeyFJ@}PO2Yb`76exrbUWg@YOUGnKW;$UoVe8VN|C2=hpxIpD+#x_`muS#_Co4|9}64@w(ZD6=wWST~7X;e1*D{e1&|Ox{Q38{3}E8k7hKcHl!{iHze1iE+y9^*P$*a*CE%Xt{~SX*Qc%`*C#h(C|*syMpk;2yqfG}DE`fiG+xkj)T?9_iqliCkyR+pNWD&0p*REecd`n_Us11+RVYqNy-Zf2*o*orS%u=y48<3yKawwyS9*-iN@_5<ff-HB=x4@a>Jo<Hfz+mCrQebVl7~=RkcW`NsV&Lj<U!Qt<U!;xY7=r8xvv>D&FE={joO#ompO_DQ-@KTkcW{+P@9uSkVjEll1Gt8Q(KTnlSfj&C66Qzr#2-ICl94IAP*%EU?{F_Mh|LlY6EfujzMpaaq3N7MD{Vm&y0N3(&T*P0%jDXmZg>^kE2FVOOqqW-%<U@-;u{K6qls>kd@{omn4^><|mgTmocM|85PX<hFXSPhB=BGQR`FlYpH8rab0R&Ep@L@T!-qTrS2_?>rwM*se6&)hSUOD>fWWeu}42PW+)D3C@yS<KeZyYAh{s>x1vYCSEPPV&T6jfzf8?xs@>FXW|TAIfEjblh-4@ZqP8ZtW^NEeadB!la&dAe>PB)W@_IAgn(>PnuNjI@Q`eK%GygP0@kxf_P1J5=rFQZr@)m~TJ`BZ`spZJ!cy5&$iaRhA&!x^G&m|wE9v~ki|7S)svwypo@hwAfH|ivEH}W*<59Dd&d1fr5E~WlJUP@lVP&}79i9DD59kmPjJ91}gGjeBg6KW8-3ArJ)2Du@*7FC^hEq+$~n0;}8{Fod|jU>mCXEGGmq6U$JIJass6#G&;k$uVSsO!n?$ZM&;kk^uvsBg(h<o9Nj@PZblz9p+rT!{LbtU_^qFNETk{P}6}Y0l%948>0viW8`t$eTEi6Bvr)8H%@2`;fPh`!f_*qgEzY=KQY4P~6pw`P6yT4&)A;_wyKv4^t1450mdx|063^^W#20E3U>l6GW~?4yHCEH{<#VW+-mKP~3{zjogadgF21egFJ&ek354M?XljX8H#^oC|=7@yoS1zyoS7*x`e!%yo#ZCF?B9^F*%C*9XW~|PVGz%CwHPYA$KA-rZyxuCflgB$To5vs#>3Q_*wBYuGv`fGxA>QO!8jxbcW)p)LP_PT%T1Ligju`vQBP8T}y65UPDbHuOXkKz9*j}f7DXf@JD`DT*i!&W|T9d7_|(!7`X_w1i1+L8){MVH)J1bA+itIo0^~OP0qnkoSUllg51<6WEG0Ddm$7*;Lj7t3ET@FFcjZqC_X{mMm|CQiQ1p6?qhdqxX;~5Z!opLmU{oIv?jGbxj*-jn$)i3n&h5Z>i*J`p?IMgKU0rW=aY|<k5cE6l^!M^CEugoCo5HZ$~}Ho9N+~FCM#`04j}t86o*h-kweIBsXfST$#&`tvYkAO8cm)}T|kW{EB%qYfV_gCcpY^uc?)$jbuD=_c@uRFc@sH?x|$qA-bh_V-bi*b6fdVPCNC$?r$&+IlOw6&<VbRVYA14kaz|=oaz}C_s*T);T%THpT%TNzs`jjU{H*we2Hi`3LEcTBPToy+-#07ur%op;tx8s^ll{qsscp!G$-&e$TI#*M;+52M<dx(L)Q?)~bGPEpRJBiirk3+ceP&neewJ5Ufm)JWfn3@P{ZN{HRGPkf&sY4ITFfi;UQY3U)FNaRitkgu@k+h!E51kd@k(8rif>cB$tn~Z)Es1`>iI?SU)(zk>T$9`zD+$!KFZ_WrUvj>O8q^K>+h9XM{y<oJcL|{+=kkg+=kqNYA1If_odDvyZ3^=48?;OiszWIh`NwEo2+yJS?LP$Lh?#8)>Ai7SCEyiBfIyJ4b-h<^~|rH{na~zH)fnQ;~hhBGIc9CnY`JI&eZPIt>o_HUJS+Csb|UC$!Dl<$Y;o}%qZXmElhnwR-xFJ`i`tZaVal^;t%|JGWi4fJaseqJUPbW++wI5$uZ;&48?6V_39Q{jM|Z0j9h}+nOuTgp4y#Uo?M06i(G|VouN3Cx}6+K-a$P>-a$S^eMLS+e(urN&-qz#UNdf({I#h!HH6}vUeH|RT+GeMP@IQafSiY%k6M_Vk6e)IOD;&(sinv|xi~{{S*jY>viz+06UX{I`4jmfHHI9+vAoDoe2JlW9knfa9l4dq*eh;EEkZ3yu0#!>79|IeYfy`kYmft}CCGu~5NdgH2)RAA3b{SG3$;4A3%LhFacycSxi)zKb%&Pvj#2S0>M8Oraw7FPIg$L3s^-K)YA&)0#s8R^#nd~dW~2T?{)ai)_<LWIvyn4X)qGX_hpCxN{gaxRoS8X_UDRXL8{}i;Bh;H@rH9Bz$UiU?M^WR*QRLaw{p6fxOfn+}bpkmDIXgq~c*X?&?rd@tb&|)iCV8|+v4fhEtTY$dL7q&_O`c4i%22Gnp2|SYNX<>oNX|sfMb1RdOwCEoOwK~hLC!+{nwp)Qj+&L4ot%}NjXIv3jXaj2couawc{ayl7DMqqGg_N-W0)B&sRPL^$<3*u<mTk2)L!J;)Ie%4av-_8y5>^*QG1d5k%v%2$wSDasRPNQ$>XWR$m7WlhT`GW*5u*jc4kzjR-v{gS0PuWwj@_2SEn{7S0~q`HYL0Jr6xo1zwCFVdl-rzQB}?(epXzUzZXcZOKw2zPHsT%>e1I-8H#(F@x2*i%$Uef96=pG9%sg6Ge%O!l1Gw<QX|L_{N16{KIEa~FltY7PqrtFp?EO0A9*l&6m<xB6nO%5G<gDfDs?=0DtS89L7q;Y$xu9nI-ER(Jc8PeJc8WbD|HUFXDF`dg?&}&4Qgew3dJ|6RlHK~F%;jTRwb)Y{5Q2aS%u;hYE80IHHT8P)OnUd-A_&-|4oh4QftQXm`V?k53zl>s5#j-rFlHsnTKstn$M%1`Peq41-(++P>^j^s*_bHenc(qmAV!bKh+S5{rK~;WIu9ws=Dtf&(DfA>P52BOJo&_)pyrv$iMOD>&U;6ozzxj_dSr4q1gTXxMKHrZb}PLn~{|kA-nIH3NaL`@9`#5r%@}Br;%q+1IRPTv#2$+)IDGEY-*sEdTmu4MGetXudRxIptjdiud|Aysa?p?<OS3oWTlJ9N?l~7$H)uF(bOa4BRpO-)j?J|+2gpASwrbmkD60?%thoWRB!SWavm-9dY^}(IK75{O1-EVv@cUeI1M!;ISn~2H4`~4`73H>a!7NpG~Q|dPyb7=)PHJk(k%ajumAa*)<2{1{LPbQtuKF66Vm)EIj=P4f9ebNi|U(u?SBCi`NJX'

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
