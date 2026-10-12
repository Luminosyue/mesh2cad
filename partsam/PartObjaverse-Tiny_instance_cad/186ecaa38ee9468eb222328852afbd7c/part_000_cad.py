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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/186ecaa38ee9468eb222328852afbd7c/part_000.stl', 'relative_path': '186ecaa38ee9468eb222328852afbd7c/part_000.stl', 'source_sha256': 'fbab218af94325d0706e074eb27e27b4bd4d7b9406c1a17f4e450337951cd4a6', 'input_faces': 512, 'input_vertices': 422, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3636288046836853, -0.2796439826488495, -0.07992154359817505], [0.2924744784832001, 0.25285160541534424, 0.30512338876724243]]}
GEOMETRY_BASE85 = 'c$}r233LtFyTvPnm_umuaE%FqkPu@lvlwI62scd-G?7S12t~|OA|WKEOT;W@p-pATKoFs6x((OV5>1<$Hg*5st#5Dtm%R1fT5r9l*ID~l`+oWA)H$clIaT+r_U@kFzKnu@)s=TcL$XV{D2h>vDP@!pzrZQ}BmIIJP7DaOQ%Z_&{QIggy$1C3{?1MbQKmbO@(UUn=-kre+<J6#XIGQ+=t+T70(~crm=rk5&+t3@P6+a|`9WiS1N>~qE*?#qxSHJSx|+gG|HpqtY*o<rcl!CXO|4rpvJ6$qSBq+E=&2g;_dbDt@@%Z(Yad?RG>%O^XW+j+vQFZwJ{4cRehmJRr}GV89k)(=tM_C0d#c7r{Mf1DE8%<K=R~X(KimuX?@oqaC@4(MyZh4(<5)ko9{wq(W#aF=0srSw@O$)GZTNbJ&EjhttHBRA<|Fk9>WBDC-Qdp%i;z5~M&euJoZ#1;7cG8~&p*j^9k_H={Oq4bOWvH_;%oQ+g5UL3keoMmq4@gl)9_0KE)ierFTQ0;7<{$EOo<y&5b>K5;cHVH%Xv>cye|2xPK2L+d$#ynlf*aw<^sRa@`a*JeZ^Ns^@H#BVzSixVQcYqYbDk{DM0c}FO2woNtvSU-b9HOIdM(mZ`dJT897IeN3RiINnD9|Q&M|;?kBz$QxyJ!=v8vOyd2^q&G2U&TO#%O{jIdG_Vmpa^vjT7@jW=6Zu-N&)FfUsa0=oBPs0DWAX@5k#an#6ZXfvj^3RpHa#fLM>V?aqrLJ!fEpSb)M=xCk@v6&eiT6#ybxzoe`0@eEM2E}}Un^f1zT2TqQqL}Kh(A07{=D?H;`b{qzB-{K{62$Yq@Ug=XClwyOX3gvm>}cqYBllI!*}67YiN=9oZC`AZNg;uYd%Olt?xtO-+YlFew6!G@n1ZV^Ql4Y5FbBrv)n&^o8T|HiTDpw*Gc}scJSZ!h3_?XyZG_?C5+ph@U78XB>#?i;%i!a_$U3Oo|Y_o_!}=>6o2RVof7}%AmY3mK}U^~dYXGjW#ow;RvGp5Ss};j`fc#<joBsnYc7&w-M0es6y7HJ&o2;PdwcL=p6jj9_(GoZ?w&67G<|Y_-#8I|c1oh;i9L}n`3Kj6Kk^*v-+y+R9QzbUd)}=q<IocAA-?Lh9)6CO^rL!deX7()Eev0E+97!+MWo2*#T_voR5y&<&6UO15|iP#H%mROB~G1}<Aut3<Nj3M{*_>;_2_=_)v52&#2*_X^QWnHKk@b6#gM0OHEAEcSsUcJn~M0!;}IX3c}~t-^f3IzcM@{@maqOI_-e&?@m1Gxx^b)>?zlxhpBf^*QaDQDwJqVBCH_fk_(ffCf5rYL^M<AK`Ll9d{5kv`!=*j7Un0b}j!MbMeO;F0LlB=+N7_NlIk8Q&cSZ3{ceIS$*Ja7PcqY$%{i!7Sw_uX^)|4KIFYplUNnc5Yui3*_7Dd31Dv9eVwnENp>FA3*d&?tF-Dz^Y=7HVCHzkZbBk?QhZI|{Op^C4~uJWV!!wyKhna3U1#Sa{Y`7o-{K*{&ImH7JoCs*?HZ|jEQn_gDId{bo@#!uSE)1nUE7$?=vNd5Im>EfHmF1eDseKbpJ@zw0jsp9Xu+F#<&m4rWODB`sdb>%!=i^6~8bP??mi}o+~;gqyP(|(BmB{U(oZ)!&WHhjI-8u-OZ!oTX^C%PkAe0_H?>hr4TAZeFobHukaE{youMWmgzwo}DduT4b!;Y8%`QBHhq`@oavuS{uwZMYrIThZsN#QT(%_Sd>zJ}KAts0-SE*IzPkC{MSFuSQKq{>OK)?vEKHzMh<TP>!8r66NzX87IVl;EwngSrV`RSx9`PMNh8RtyaqCH}4;pdLC_fRgOc=*#9IS5nriuDN~L={4*)HZyxaz{D=YQ$N34!(>(=#%z#a~eVx7*O+RZD^2{8L_(E!^)N}Ye@vRAi;4i6R5r4;2_!lc)5Z_H3Ab!^SA0<z}3|!Z(9cDRS<s9*K?>{fe`93>foIJ9MZyNX{UGkWZqkltF#J5(yo1VKLwekw`96yqtyZ!aZ<HzLhI(uRM(dJ7(s;!%fZ%Uq!o~QjUXC9S)teui9@m~54Q9Vk0i_1Zd!zSY;PgFSKU+#qecYw5;I@Bb-*})#|qfTlq{$2<1O;<i6KK<3^+`jtNPow`hC0XJ<4q)DhiuV;iY$yDvuE?KQSNc~!SXz9`o@m7D<2y;ayelcb5_T|8yyo!vh{S)h2=R;CVBS7@N__p^rmYf}nj-C>pYRvoe5xz<M_*pAk@yH-#Q)wYBhUDMoPAjOtNC;EduAocqqLbWz7|q4BX|3&=HB8fAEzMx^FY}zDHZ(>N&DFCI*#$_DEE<O4m>EIZ{Ol0`SOP%zq03m)U)kS)N|>*YvNb)6yIX~4*S6*Z}{4&{nDOih8>XO=6!dIZrrg?>OZHF#GCcCS>nHq65l)^68X=xx-Rv3d26p6A5X{p5R{1HTB}9P7rsY)a%r^x@+nEuZgKnJ?@UB}EW^cDC;cY-9wqJz#-Y>IJ!r?PXdk~vG9PHAqj$@3+TYSn+R4MxZ_0u3;#((8l>BO~1*qqg3gYXYy39}7t(EBKwkNP}n$rmD{2M2^AC>u|#5ceB3Hy`<PCF&OkAwK?ju7mlE54ET(Ypr8K1i#(5c^-H8S445*-l*N>?3mA|1;*pou6dCqo~91TvU8E=F8xJWMBF3=eP&XsK4iK@s;1d-zb0Y<SOyXgmL1l=^N3%nMDsveO`@%?-+>n{baDTlin~?_B-0U`e>iiEl_{@dWM(O-`b(R+&AjXvf`VA1|t58x6CW*ry0^umL(-o&rOHUNj-<!V}G4+QSw-(?N7yhv_$q7rb_eCK570Ja{E@_hP+>rFH8PWL&P`V^N{?Omf_cO`=-psh<{d7#<5<eD&i}n{`#<s*ryClmHoILP)hcTs>>M}?`lXv@hz5z5^w%?q4bxUnkx67X?hNxOSE&+KH4m+C3pRmI`5=iltnkh*E}}E4?K$bX2Z#ia$PTK;J#XZc%S6C^QSydn8FsI9d6W-`A-|^jpvN9>*1FzjQeipYwY{V^u#)xGHZ{-pNqr(dc=0LbE`_So+!Wlfakw1Nz&iStmcUKEQ<KzpRiBNH#tfC$n|mJzyAaMUUsYWi{^T3jhr_%K*qb$x5r-byC#coN^67hP~>;%Uv0rS@s(G5<$h7O<luU<U(0it^5<shA7w^iX@Bj*uXv8kSRi>!_SnB`Z9B&zPl-_RM|mBS>$<r_o{!Dr&taTrTV)(7RXxO4vj(F5&v(Lp;X&#OiE~*d&$0TI1+u;=PyLrmTtj#C`>bPFe_CtuoNa1VitkT0jTfELdA{VI-VN=1d>q=j$hFzxZ!0A4O-!p!9u?oyN6S4<Ecef1U(mmLxcFm##q~~hmVK_Wv#mVGTUMo`-#fg;{wVvUpVWJ*9p)L2(%84QzV3_rcB_nEW$^w(;wuXah=$i$ET0#&KP|_D8}u{OT-O<SHZ_-hw{mp9zubRK{+98pxW77qJo6^uK6@tnGHqy4tS@S(5V=m5+ZaD5ufm_uW2$HuN6f?h%ECW4ZjR(nia>wan=tQ{51lJIWZNt`&z}{fo?6dc^1jEs!vW8cLpRI#RI>)JkofoaR?7JF^TPi0c`(+`)172o=@af^oQ$oAeZiJAw2$W%jPp~^u>L5W(ZAV$%k`?WgI7uXG+mxc%@e}VKJ8}2i7ssWy~N+IE9ceoN354TH#ea@ix=2$99su8ll`EU-W~5Xj%P`KnaZ7!{gGurAM~&GOvbG##!vP;`k&dDZ?^f%_|z8#z>oe;<`+|^s@TUx+v9nwTfjUyZ?`VU@6#Fk`csdk9kdn8F-{%~mGw=J2*-W;#7@SExmZ5g?_18ep&bTwm2s%|^AcaF-3jaX%|MyY_0LD(-@J(D<)_!>K3A{25MPaU#e0CS@1x%Q3+r~)YiUo-yNNs(sv&W*eyV-8VxAd&LHb=iVHMw0uph=r=h3o$SsJ~@dOP5`<Wb5LI3<43D!b(G(*DHzm-7pyp6dBX^z)q-c;Dlnlp_6dZ@0`_|K2~`@?0cwn?8zfxrqBzKe0YJx3A92hxuX6Z0UDvkV)n<b?I%HPj&mD@|<VgA1J<Mx;N(8Sa(@>%rg!lenBeEJIP<>J?q_H#8=vkkaa=5?<;vs-&x^593<<fdSjW)1EvP$WPF(m<&$_z(hI~ttR=qbd^yZBU2DnnoZh}W#$!XQn@WdOczzEWF1|87NZRk~`l!215MRG~1><Mg7`a|;QMC9Lhbqz@=7S$)9y3kbz908dCi?AEAIW3Abp`Pi>Pb5&QMIL>=5O0#fBAfbj30B{1{n{g{k_GvM0ApP^};1w*JvNC&+nUHy*c{@d7MJ9ZX9}z`{;*ja(=z=Y{bv$i1FED<Wf1`spUBD*XLF}ptBrr*$Y4E*_GV)srJ)Z@%2@GF}|L+mFqHnvBLLH!#Y0s3)aV2N7;YrgT58tJn<0XgIZx<wrrY=M@w}b^M98>?C<`rgZlic$~<Gz!VteLO!DXxLoOnJ67tvgM1S>uei5HH!hHXv2*$f>DB7oDSMl`{iE_W_HO8c%KB4fZJ7N5UHp25q`vP*GsjhMI{>?mgtklyI-%NZh^Ap~84!A4h(Bgkqd_`|6?PeLXTkbo{^%=6SRi=)`K6C3Hd=K*1OZYWU<9c0IFOc(nQ$g-C(~!03$LK6Pe_gC2zQq)S`z3ib@*Ha|zIn&b@E=@~?@cU+R*0`wuZnTi=nS4~-Bx2B9eG#gC3R&9xn9-dL2~YKsOP^c?W5+n%DSQL3qbwT|CV*d^6Bs~jLV*QU;Avjw6i+&&avF>rdXe(Vcg$Go+fi~y=ALMir@Ds;<KAeeN62a%l^S~p`FaTU)KetM4Zg~mi5!{{wtgBL$cmroolyFd~30}@PnPC9W?i~@_eXPiIx18$b5LOkiGqQ?sm|=Jum&MZpHJYzQYdJ`@5sOZ_)amhrjG0-YW+jk$t%J_)P2z?Egaim`~C#nqvW(Z<LpXF#o%SUqO5o%tJ|T;_D|HVn6R$6Y<kup?#YCfam=x9Z%+NAN|QB%qPEe#`~$^&k=vSw$xLt7a_hWv^L-GX=sO@?~!M6ING^#alF?_be45PYv_adAtoGoM%EKwFW&?8fATx(85u3U(&&M-gQeAv(w_R_r-(nFAMg7|Z$SP71+ah7k4YZu?EviOAC(thpV9&C_D{I%WAwHwvF=^7NBoTia$eo;0sN-RCBLb2B|Ja2%E3PFRs*!do<Qsmj{Jf6!{6fmE%Xo0`&PlexMF?8Pun2ZYwhoheZ=)S@UzcIyP4~>5MTEU#{H658vEg5Ly*U3H^zC78)&z+6A_<SUfR<-c#PCj4-ST(nkMm<D=Vda%no~T-X)*WFHJUI!Fg{XK79%LCCQ3?UR*Zf@5JLi-LntRWsTq9xzn>R;={_~yww|EzqWoZ&O4~3oY(5wMSMMG0`>zgc>k=Vc<1qz#_#32bakNkYKyX%-+q3J^Ijc?_tcKpao)@kc)oZXiulMg$aCU@w5Ogg0r9S%Fs=$Tko~37dKcpPy@o0L8phAmTd03hcjSrRB>BxFs$#!6{RY~9L<hXDTT=)7U*A<||Mu>PABg>_l5kb>=p}we`<!16zup1Vzgh&^;h)&N{_j1do~qB9v$@+rs~3vvt)gRJFvcGBjA|tNVC$Wy$n#@2TyJ`)<S_@ohW}_g@{B)-`uyUH{aW{$xGu-7xUS<rW50RlGyFaAl1IDsE8Z*Q)A2paQM^ae!)wX9t!|tGKV<m^{C#cge@AV^_gq>Q^2EF3jkk`RDH_}e>wozHdGl`@gZ=e_O7OdTVV?0Dm)CE0O}+=$E3X${zZHabI9&*NHk6WeM(f!X*EQx1o;S?H#aAx9$M<X<tIF>LOvfUzE@iYq{=@C$x-2(h^7?9VP5hWx@hvS9;5Uhq=MdArc*Ku80-x_c6~}cc=!Z@4*JVtR`sHj!Js&kq&mC`?n}zr}>1fYscn@z`tm3^+i+EhGOIxYG#cnO$2YC0zb$tmIU+;AQ@wMOK`L^*mtmEU4;5d!Xy=DH9_OwhxoM~nq)N{QDp5In|M1F@_s88dgxUK+2;`GFhi1*nm?WQfY$8nbq&}mPl-?d`>@mzB19rENX!S6IK4n&;OJm|`{=*PH+_<n2aY5D&1>+d?$8;;Um>g`xuFV|C3zm{mnViS=+`Le_-@4vu*-va&;dwGALJ$AzSTw@gS>=}mdL5|eIe)Hv0oOiaP#H;i6VPAQ4KJxgviLcbK$37+Q6!LtX|J(P)zB24R@^ly`@#ZLh>?@ONqaRz0L46A6T+CDd4pzxy&TfI{2KzgRFTMfibr=c%R5H$MzXSD5Ta5i?vmp3hDbg=y_YCaIzCJ&eD~EaVU`6a-F0aP@^57@b$9FK+;cDTi&#n97TR+c--@g_7G7fk@dLjw_u^i-oFj(?i?|czoeb*oJ-tMyUK40-_BkQnIpbg>^s*7)aG#-A-&&Z$MM)GS<qOf03x1*kiBPGA3;C=D6%1)RkwVsm48dweM^VfA@>R|Cr#e2c${y{k~OY)l?gT&Xz_@SPQQZbLYox%FtF%$Xw&&Br<>+JBpwtq6}(=Hy@<>`j^k=Y^e=O2;$rWOOR{zTSbo<bO(LlVT-$1lY`p;{{HnfeIvzXYQ`-(=yuZiTT=arA&c<b~u{_hbK}B;QAV&JWfz?ZvlTsD=I8+b@zw>-s(7^SL8F$3fn|m^y{Q_k4}~<(%-nTiK;J@4a=X=UYwko1L-FSoh39{xo;VqxxJ&eBD>bf5=OG%g$$5mxd?7pWQ(6t24eJzMm`eBx4?1S~Cmd)(U?`u;kItc7Xq87wWT6!~3I>L*dUKkKeP5?j`vx4<?9j^<2z6A2FZ2i4ort@-3d<{dS`rTn-_AsR!bRC5x{GXW;$xw$gZ>y6TVlzsp_mO_j6xy$R=sJO7|QrK6GmbE9}UzE>0P*C$6K-ua{CH`i|^zP@BK^0%BP`IT#(@x9GFH7oahYU$YnzQbYoyRORb)66{<A<ya;$bWi<oL5O-F22cqCgQaV;_Go1_yL(X?-q-k*ZNzs_~u#eh@a)KuB~^TUlX2d5)q@7H<oloDXf%HM*HUaDWPG?X{i7GPYL}!{#QRGY})w${ZqnqwmKx*$`TfXBd9ychAt%=I*V-R1hS!h$Pwfb)Q;p4<gV0~<gVm4R8Mjna&xK&xjDHhwK2IV*^Sze>_%=ttxs-1u19qt*CRVqYm=SHwWu}7waC?})yUP!RjHN9Rmqj8708vy<*8-K<;mYrOOwALJ5fuLoyd;V;$%m1F=`QVF>+z51GzA{Al05+kepw^KSS-P_GCM9J{E%uP#wqx$c3my$c4y7sl~}f$t9>I$tB38sHMrJ$YrQy$z{mps1?ZN$Q7xT$rZ^}sMW|-$R=tHvWZ-iTAN&xT!-pHu0yU%txv8?cBM8XyOJAG8<QK6n@~N-O~~$4PqI6?8MP(38My_uBe?~+1GNvi1GzVK0=YMNBy|>fBzZQA!E32Y$%dXH8+wUs=vlI%Ka$syH&Tz1H<B&X!(<D26ZIf@6L~XrA9*u*D|HWfD>;F>i=05-K;2H>K#rxZC&!W_sjJA5<VDnF<VEBKwlbf(n7WL-n7o3;;5h0kavXUJbv=0tc?Wenc?UU(x{I7dK2F_3K2APK-A6u2K21GHK21JDJxo4BK1V%DK1V)J{gHg0oJKuMP9tBV-XI%#hivF0vY~g$hCU=;BmYdzA^%LiNBx_8kNg|8upRg}@?X@FWTO~dh+Y|TA#y2dC2}cpIcjxsIdWC13%M%UM6FLYk?T<1$aTo|sLjar$PKA2$qmU(scp$k$t`T<TWSYtTXJV=4;F*HsBOt!<WAI<<WA)F)Mn)N<W^KSax1bYwLaOC>`rwdyOSGGtCJg$>ryL`>ym3y%aCi5D^p97E0e#W7AAi~cA^?%$ce`W7op~mjbd;<>O-<o41PuLF8LKXoBD{HO@7W|@F(gWvZ1fZhC14TKaq>uK`WArlgm?UlgpE9P@9lzkQ-4|awBqUYB#c>UC765by#C7C#c)VDb!@@Hu51`*>5XZECy##_mVTn7pMow7swZF<qGu(^#J(@c_oX%G1R@}7;-dqKRKElMLk50A}^;VlaqN}%UKMbM_ognN1n+NWGlW@AF?mG7qut37r7m^Gr1kP6}3CL6<MVYB&+0ZwldaM2HVOs7K4AFb|ZIV{0}S!hqD+wiQ1h!i9C$jnLLc#m)euumpq*6Lmp0^ObsGWCeO8%)zpR5AaW4fcOi?xyIBm5r>-FzdW;-T)~TsvoqX9=ezBFGY~?14!I{*{<jaiDWHI<Ui^1vCV`M{5kd6E0DvwW))2X+~>E!FwC%N(){Hv`zp#DL9LjHqX&<@4mxAbn4-;y6wuaX~=Z&6dox5&nQe2AJ%O(CzdookJ)Y+x}sp1P78PmZNVkz>ix)TQKT@^b1z@^bQG>Rj?-@_edBo==`bok5;Mo=KfXo=Fa4F?fotbhMS8w$hcw;9k^$<X+@K)Dh%CWHZ%|Y$lJTjwg>LPoPdDPayw5olO3L96+5y4j>0nr;&rm!PFV#U~(u`BZrd1sdLHU<k{4P<k{qT)TQKk<VDmd@*?sw>Pqr5@(Su2@(S`Q>N@f&avaq{jw7$Pl}*$Hs)d|DPGm87Gj$!=&<*6x<Si@)Z=}YPH<H&<W65jDtEtiC)#MoJa&inglDe22NnS#oPhLV^K%GNgK#ri!Bu9{EQNzfy$kT0QDm8=}MmBT`+0e=45ON@OA~}#ei8`J<i9C+#M;=G^rH&x`k_S@<k_VIfP<xX5kh@bmlDm`JQJa(7kv*ucWDl}4wHn!(T!mVeT!mbkT8vzpT+~+X+vZTKt$d+=CL3ye{)JkMY!ri^Dkuh*;OAw@CCC-1)yNgdwWzM-TI9ym=H$lYHq?$}L%WjyWvjynTX}CQFQ_l6AILAs?^q1}$5!m^p!umE$cFxlJj14=Y-K8o!DDR2c!%s|E3H`!?nE6#?nL&cjv<d>9&Z+d2e26IN1Z`7G=$vOR;S^%;$tggsQ%R9WPkE#7K4Y{iZ``4bvW73zGORF`Di;&0h>D5K^3aue|<S<@EaC`f47xq)IX^o$%Yzv4c2TWR58A8g^ni&kj>Qo<SDiiW-I>G(PV$}cPs|?vz7L?@~y4(pmrhmAP=SXBM&8yqmCwzBL`E%$OCNGG0ax_*-C%vchq6z@5tY?7(B{WMpB1Rhmj2(K%QeeN1&}tXEAu9tqh@lPYon{cel$|CjbBRze4!Wf5zIW<oO>X{MWzC`?W{zzwBkp_3tl1yt@}L-XAOZZ2uV>=fdrbqyGS7TT<W'

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
