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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_002.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_002.stl', 'source_sha256': '11cd62731a5e0ae149fe1f17ca5fdf3c1f6dd17af115ece3e958cb0cbf1e725d', 'input_faces': 1297, 'input_vertices': 801, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16641296446323395, -0.17766857147216797, -0.4416075348854065], [-0.1042187511920929, -0.07590331137180328, 0.18396763503551483]]}
GEOMETRY_BASE85 = 'c$}r3dAv>4ANTjY6p5r{NO5S81}RNMPNO2xpj6}_Q-lynvdhpU$xteBib_dko;k=oM;a8TQc)S2%dhh6?_KY;?p|N#kLUF~y<VT!=e<66-?i6Td+)XO@0@l0nl&y`v}|Dhs~X%lqSD~8je|f`GAJALY2UMV=XULT)$G=zUtVy0K`#GUA9YjnCe7~53;G28tKZwcSG%6o>n5t#>u_21a}(7&bnn@_XPa)VyZ5}ez2w)m>DsG(l=te?rbqjzeAZ>PE;u()yT-YR0g3;||4KwnNF3E<#gfRw%C9Xg@LwMNd`T=%EV!&7&(yhcM?4S6gDDF?i|3i=PRSJ1({$60ocWlV-tj?xtwrL=$BKO69iM0Nu-&0g<9TxTne%hipRl>AKYVuooLucsk?Zz{D^HyhABXIu9v>EzUzuorepIKA<9UiaIiuR<c%C3n*PXf|o@ZV*c~Gy(177{)VcRM*8^rUegH8SUUwG%Wc@X@*EuJUs@gKafIcMIo^`>|p*m^D+vocqnO|JMbo~PgC_{PPa$eI7uu4BCYDe|y;)9JbLO!EV?;(6ku8s_+`uiw5TM;<JB((7+vkN-J;OFYkRF?ss4p&PyNxB03rtGxD;Cl~*;+#5IYU_rx?IrD0526^qb_1ri9gLod;;|GkJ6VJ0V#+mb%dc*6l&BNc$@%oz~&n#%|^*2qPymrF|?>-?9TAs1myKikhHEMhPP1y6^Q+BL3&bFRThlYFYpU&}*-~L`a&yZ){C_T@+pR0URaK7NxAHDvjY~F46R&SiiGmYN#`kNq6Ty}-m-+(;XdFJX|dFI$RmwDq>+2rA>VdK1UBM;8{Zd8L@d5LQ8#`7e3X32T;z3cvJ2~&TGil2Dbcbv(yf6npxn;{S9ZuPIP%^QEa-fJg$rg^C~-guG+RhoGHP1wA~Z4<olv3cI27rg8H3i-I%?|9djJTrEe*Wc8{Y6a&@K3(1GZ<0I{PTra;4=(%K>u+F>Z?$rLt~`D9xn6&>uXElDYI^+*$uk?yNaxCf|4n+)YroAWT;=sQY3qOR)CJx+jIFmc*Yyp__4T#6zP>4&tLvMz^{DHcAWx|4n|+ab)b-7f>+74gxw^g~xxT*1a`$F(J->m?)$?m}{rqN6GI>%xzZsjW=QmBRpWhUDu-boqlQvh+Z^Gv4`3-FS>iJC-X}+W&SMzg{T+h#eJzmYvnS7HUF+Y<h^!!YoRr7Nu&*VXCe|`>a-oc-rlQviLbAmin^K)YFC5sDkwf+X=di~Ap;dr(FhU6Kw{w8g%*53rVUVl^HbKZq&{k3_*Uw;FetMxbg9p`<-Uw;$F4_Rc!+kd|b$P?=QDqY&-`u)o0p?beclI!=Ygw3z?->*`~kvH+*uUvl6f4>UIlj{8{TZ;Cm_p9Kdh9+0<vFX|-PpS9VBzZ=?$EGecd64wqV*~Oe@3Dzq^-TWhqLuOU+C1}#$?f~I%|mkg{%rFExqW}Od3HPXtMi5p825$2_9Z#;@Y>DW;(3ZZ=(50TPm(<I-AS9g_Skyf-nlZK2jt0h{Xg{jdj<7R9REx_Puo15?d`RnJRH1mT0BpYXWBkGJDz86tzz<zhI{?Z*!=vfw&lvh@P;j3du+bo?+xC#*?P7eTIG!!c_Q6<xi=2Bo+%%^kSh;L)E?%w{}%F=#ov$T8S>1$*>mH0dUHE-e~c^siPui@p!=$=UOR2xXt~$lBzdMzQLn!V@^r`jtG)J<Crfo*=8fkj>R-@uyf>aUuP}RzcYVpj<LgfGuCG0Q(QEU)aj4Jp+Ny)s-*kQZzw<hK{SC=8$5#Ew8wY#*?CaO(%7Y)@UgM2}t>>u^mU_=!J?iOv%In@Z)U)%=$X6QV$iw^_Cwt>So>^XDp*IdE+_v1@kFR<CO_FEdJAZ4gJj`q9^*10-&fB&wR~~M!ves*V8Iz~R*Y)}vl4n}}G|?M3@?hkZ6B^{m!&`g58PAjU_(j1YZyfA<?}S-?e{J5j($-vgwn-1azxKVl>bvW5<;n0mzrVcSrhhxp>u;JoTs(Y|*I%2TeRaA)uKbrRZ+QK+@74Qn_WGMV?bl4M>zg3g*VpFy`ev({Jf*I$&5yXgHrLmeJZR-#-=xje^|iUazJWbnUEl11spkDqJ-;FO5zntZUOm4Fd%Svn1M-A=elz<`o>k9pk~~z;Z+4%_gWBr(wYh$N$wT%0Cf2Sr?*nRn&aN@Jo}V)|SMzg7uIJ~J&DH#zAWy0JIb2Qs3;p>yY4h^_{G714nxC_)IPXG#eoifKy09Qu>u=KLYW)q!(`x<AEaP~+{*q_)`b(Zv>u+YM$%Co>`WxE3xWE1;$-}$-^*3R2wf-i4YPW#<-0N>Zo>uQy=^r^>y<gcptKP4Y<Z1POl^_q*`&H@(>VMOJzjFCl|NSbkxq83K?lpN*y<a63oM6tY-(%;SJf+@aQ{)--9vjXxd2o&Y9-FW^@3EP-RZTnBO*7AR$NnG2^W>Rd7X0s;^r2st#q)&Cw-#9$&$B<L3$A18=Z}`g^E7$(i_=!c^Gt;i^9t%4exG-INS;a#^NtT244j>-{v^4sKXqP%nYr4Zw7F`3vO~8S-Z=bN#<btIlRW4<#jLxhk2e3irO4|A*URQf^31fBo8x(cJh-&#%6OhWjr{ZV1LJu}p6PVyjQDwzm$oq9GwfQtEq;7J9#r~uV?57XV)F2Cix1;@iae-Lw_m*e1bOn%^4VU0>+Uw!VRE1CUVq8cw_mWuYY%xgT)WEaZyo9>S#yln9-B{D^M3ri>Aeli^|_$9*WVO*dhw7AUVH5EBlj)y#$k`igU<7w_xfe?8RO@9<GizvInSp2PrQDShXWRQ{mpzyzAL-hYp2co9DLQgA8cN$$CUVagY*mLJ*wUZTjR%PCy;OZc)d5C<f+N^z5XW2gR5%1=+$rYC;pr7jl&qTey2B9@%o!24<Gs5zrN(bhEvvf?HSGSUvHY=-Oo1fAHEYmZ|aWC=6$C2Mz6mK^32jQ-u2DiZt~QaeqMh=@}TLRW4!A~9=<!&>u<JkF?0Nu)!zM_vH8G3UVlUK%-3DL>zg1CM>TudYiA?sIXyYm8~;C66wII5JMZ%D=gjXW4@;lzJ-<ov#5d0`_wK9TOdc#d?<uc-@?@FY=f?BQKVO>njnhu>pI`Fq=JnoumHnT|QxE2O&u>5;v|IPAcij(}Jp8H8G_O6?I+*;wn%+E_u4?jZi>;fy@w9pUIxD>XCQKeA?!V4!XBG06#R@);N|broT(A9Q&F5^)+cr;>eYIdcO4NO6c{~qn{>I%a;(2y-Gqe8g{cTx1&yZ(#=dJW|yI%Y=*E`;=BOlfGj?XS$Hz#NP<huUUse@+cYJbw^s{QG!j-4GJhs?w_roVsBGUxg9@q+7O^UPl+&o-&QIi9D<6EA+XBA%znlZi32<9UKSxcxxicplii?2H-l_GBuIGv4B4uRS4o@Y0k`@jOYM9esk=o`5`+_;qGH&z7g2#E>iF=S`DmPHaBQ%kS!7&eLYM*Pax4xP81gJ_&pL<Vh>N_Sn2(`MKUW-)ZvTo8nJ;{k8eNTGQk0NzOUhoM*|(ZC?H4L5HH=_+)0AJkzGjhhF{UiTRUec>N*|N|x^%KX1b34^NyO&%^3V%zAX<>D#^QV)G|=dgBw2r%Il_%4_GD<fY5a^X@nDpnvHRUOR1mcFk#CJKwy+e2#HoygxqViM7)=dgpz^<f#=E{qZ4BKAz`|Pm(-n^hW5N*XDDsn&XepezQL2U#P~%<jKB2sqry+c5eeUJ|<7CYof--<YAZnYJ50vw?97cp09~dn(y6qzUz%oNS>Iy(Hoy6c{uT6Z+sFquV2R-pX}=<54LR_;5|p=nLm#6#wS(o9CO}_j`7APL7trap+7$4nZ^gb=PPrP$%EnVdCym9^OKhk^ZG@eeDfvm{t0`0W!Co*KY8PmB2SdO$$P#M<YBQ{-uMLML0&y?{>gMFPhQ)_J1==yyQKGgrKV3Y?>R5c_U50Y&5wJ)A0P6t!VUiTOfz|=dTNe0KIFmoO&|CAOCFZo<IO+ew&%=wE8gU{$L7O}`|}}ry23-={G8ot@@)0Rv%Gea2kFE2dhH|+%M3N&zjV%+=S{6&HrMNy&Gq_abG?4qT(4j5ylVY&=T+;M&Gq_abG?4K`qlbnbG?4KeyR1#<!b$M{Z;Fi>#thBTzk~|<@&4EFV|nSe!2dt^~=?-)-PATTEATVYW;HkQtOxNms-DEJ!<`O?NsZRYo}VjTszhJ<;GvFU#^{M{c`P8>z6yPTEE<R)%xZ7rPeRkFSUNT^Q!f$aD4prt8je$^{a4v{PnAFeEjvRaD4prt8je$^~=?x)-TsiwSKvFs`bnDSFK;}`BLkbYo}VjTszhJ<?2`Kmm43oez|_B^~?23tzWKRYW;G@tM$vZQ>|aFoofAZ?NsZRYo}Vj+<Ddd<<6_tFV}vxe!26i^~;@CtzYiEYW;HORqK~KUaeoQJ!<`O<D=Fucb};B%e7OjU+%nW{YsagZq9r9c9XLo*yh2OCry61)Q((vuz&w&@jQ7+SMxp2U43`t%9Eppc*kei{~Qz@?;UUVMF(HC_KwdSI50m~{b_Pte=xYwyj<<i4l?->?O!lsZhRaPhl-i&$oGlv^KkM6x%)hv-0stJpNEsX{dnvrvANrK$LHbcksHkOJpV59Ir)sk1)oRRJayTx1^o>Ue7QQFXD>B*vdE|f@jN6CCLJCZ&ja#Itvf#O&iipMQ%~_{wt2^sXIl04+LOGsq{(0UZB0B+kSDKMwJM%xZsGVAnMFDCsqN=^{Ur|ueExdQ{H8{uy>YnN<l&rK-))d1PYxYCJ)UO<UT3cR(ht4<rpc3&>U#YR{@Ypb{3lCxTI-$nUz2CI-0Jl=O`fU$)?)9v*yC3}I@cRF@}S}5N#1#FzTmwP-njikzHi7o@qVSrGhMpOi09$i6=&zVzA18jebbYt&B}FsL-Lfmz6pE0y1q8gs_UD1%j8LQeQh49>zlN>y1q8o*Ef0Xg|l)!N8$3dGjlyh0eMP2N9koI57l#&Ah*v^a=|qw|GR>D?wL<)p0<C7Qmgfjc<%l_W#;(L;(1~~3$tI8zaO!AKyLqj#O3_GNv2x^@A$O+dy_tkz2mdTygx5j{b_Ptzx(?U)&7*tRr^zAYR-<2L-_1Kvwo=W`)sbi@3Xo7zR%|R`#ziN@B3`7zwfiT{=U!U>ia&|PW64C&Gq+v?s)ZmpUd_4ed7n1@j0`t>BsS}dwFJQIdh&r1}%^0Y4U8vWh>%&SpG>fZpmrO;(3ZZn;p5*JN~Ha&3Nu>=N+FUPh6Dsj!$ekc7Cq<19Dw|vVDiSx!Ru~*X_5TKf7@_DsAo?wLaQhua7p@>!Z!}`e<{#KDzU&_0b)#)<>J`_0iR%)<>J`_3?<D`P21Rt&d0K%%5%?)cUA%JAb<Ks`b(4dVO@`pw>rMzgiz%J!*Y)*F~+5Zrs%R=+3LwN7sI}KDzU&_0gSIt&eUz)%xh_QR}0tN3D;p{c3&Gc~)Ity*}zZRM%Ipk2=@aSFew*{c3%5<E++4Hx6ojbp6unW5v(S_l0V|w9WN?X`Ac)(l*!orERYFOS^j1ercWC{n9qq`=xEJ_e;C>sQuEeziPj<>#y1`ZF9X}+O<>dmv-$``=#ADsQuFJylTI+&h36_*B-TB+O<dRmv-$@`=#ADsQuD9xBI1C`_+DF*G{!x+O<>dmv-$``=wnw)qZJrebs(xcYW1<Y1e+WU)r@(?U#1#RQsh}JJo(^*G{!x+SRZ2OS}5jerZ>~+Ar<uSNo-PZud*OaZvlE-StxYrCmGKercWC{nD<TYQMB=kJ>Nou9w;`t#iAd)?F{PUs~sOKdo!0+Ar<esrE~|cB=i-I=B02T|3o&X;;76FYS(3`=xbm_e;Besr}MAxBI1Cf7O0zcVDUf(ym`>zw{9~`=wnw)qZK0tNqgMepCCUb*`_k-Y>25Bd)L7FYU%(?U#1#RQsiMuCK4&FYVf+_Dj3-s{PVB*UzusFYV5&_Dj3|s{PWg{c69oYp2>T?dnncrCmGKereZEwO`uRul7s3`qh4ESHIdX?d~_VU)r5l?U#1-sQuDz9MpbkSC85+?b@&QOS|@{{nD;}wO`s@FSTFVjf2`R?b@&QOS|)`{nD-;wO`uRqxMU?cB=i-ZXDEpX_u@0(ym`>zqFfA)P8B5XVv?a-Y@OWtM*H~aZvlEkI2XR?^k-iw7b4)zqC8A+Ar<KS?!m0=T-Zq-T15h(yo5BUpg%Ni@E=9Tw|W=k<$vsN9Wm-uJiI_W0QwF@0gh@Pkl9bMm*0nGI@|*Hza31xB8>;JVl-ye8-FiIr7Y7XZ!7cYNffJy8YxqIlujhCrz%~Z}TJC{{;2CrrK}w`F{J8<huPfckS=k$9%3iGvR%{XY=HbZ<^1^s<hdWGhZ?8vv{7ptEKszqvO$E#PbY!a=@RT#&h@Y$=rCgcf9+2Z|r>U_~cD*&C6APK(6agop-{Vob9){YJckG%HHRDLB;-N9#NlP*<62qWpn-cmCg0%S2ow5U%BJe=T|n@pI_Nre}3iKuRgzW^{CIUTs`XZE7xE3`BnDBwFUL2M(tgcD-XuJZ|>`Hm*>uVmssJ|v%Z4KZ`i*)SDyZ~xqm$4kiKl|@?3d#PY>_-;FSIga@B8hU4MA%?)kae?{d}tp!qxV<KqyPeb3}a%x`{PIKP?v$ob9B3+D%uA349N+|6$$KXQIEd3yRj^EsGmr_BrJG3uXY^0aEF%|q4B6nWu1rt<lII|G}mcG^6Yd90cDuX>g2|HP&n>qjFS>6oBw(4kH2pY)QjVA%28|D;#vi~g_vNv{hotaIuA-@oZqVnfu1<#OBLjo~-)gW#2XlZk}q;m^Y&;rH<;V3F_}_yAZW{0iO+770I(-v^6?pTv8^BH@wvqp(PL9R4IM5`GgO35$e3z{kNN;raNRut@kr`~z4dypgfm!1#%T-^V|JMZ)v&uV9hza{NbFB)kFt9To|Hg8vT|34e+I0gHq`#eafD!W;3gVUh5M_@}T)cs{-n-pDuzUl#Exc|lMUKLHjApN^j#7(PBysi<5LFAs}^PYaBM&%>+2BH>E|BjGFYb6|0~w=Fm4UhgIMB4a&(u@ycuI_Bp*)Am!~6OeEz^fPTO4_8G$bMABCi;-{xBzz4Lu8V|g;b+2E$(%vE#BYa1!nHU~I3>@EJR5<juXSL~-5GBHi-dbI4#ETQYhaP^pukA@QM@iJF6Vj__2!=I%{?Z3PIOP47pVq*K3oH?j$Z&*htI@o!Dqr};Wgp2;IonNxsh&)+SV-6QFt-9iQEs7isJb(zJaoM0G~r!^YV;@4+qAp!y@5-19MCfeorKP9)1)o5<VX<28)C*z>kJS!nN?Cut>Njo)3$J&&2~+Bz!jhUr;!1!e`<C1chTOd?x-c{4f0#ZWz^5JkqsD_&OwfJrZt&gl}X#WL$2-Z-j5;n43^>uAz8SxEWjwHO(s=o1?kTN0T?fi^EOe#;7>gT)ZKC100}+j8{YYDJ&BH2fq#$3IB^<4~v8k<BjqP@1I88UybO09$o~V7>)JRNH5`Y;FsX%@TKr`@DO|*JOu8Ke+>7BAHctWAAmdK+u_b|PkcSx6Mh6=20sE1#pl99;Su<I@Cf*2Bs?k78PQl&ij)kDUlJHD6LHB%6$0a>1H%cq-y_L8ocIkvAzu{f*1&kHz_3Vo9sY5QJ5m<k72^jei|>W6i0ZsLQvbmC<AGt3@UQrx7(YT;{5QCc%ngw`1;+0Q4EMx;z_T&FhqCzg7~e)&e0_`?Q5Iho<0NJAxiP+kviN&3K9{oiq!?GDEdFwgD^M065#!R7#h-|AdCKC?#keYE@t0zJ4rTF)F}|3x_|zCTpe#No#y3zFUka~-Z^dtbC-O`#B`<hB@#kQX@Kk&VEE1lG_lHHoFX0csBH`!o&ag=M3A`sP5*~p+0*i!S#)rZp;Ys)iSXA(Q;xEG@;ko!ESR}j*e-9Q3ugB-YBH``$GFT*>#n;0k;UDnrut@kf{0mqld<g#-7771~uY*Oxd-0{PNO%|5dL7qaBs>-W7#0c7!FR#Cs7F|yBbnFE#mm4V;cB=%C)Ic^WWFnpmxD#ZRe2VK&%qP0NcdvB0nfqN%!_hQ%e*J^V@Lc7SS0)aF7w(0s6S)VpRp5`dHW!9cO|$CI>_8z5-x`h($)lgHaf`MeGz;GI>?-RHCzWBWDXTS15O5Jj+3(ZZLmoAe2x>2&$)G&%jF!8;B{beIpz`6lY6Zv_oDEt(KUW6(kOfyJPLjaUjRP^55!l%1K|hpP4I(o7yL803)}(U40nLL;w#~<a36dj+y@Tv>2L@?jZcQ3hDRge@sW;;#_E_zCj`bz28NqNx+BsGd{d0uP!|6z#$70je*-@lX<(#%_@6QELs@)(jJr}6-yP$&l*K=faSO`gn`3+vW$~3UzJ{{+!Wh@3EIvKPwJ3{Ej`5k4#mC3^6w2bGV|)T-@uy>4lCt>V7?+_e{#1-BQ5GK+<1;9WzZ&E7DT}`q<2sbZr^Wbc%Hj*)6>t;$YWP*2nFZtp&kz0-EE0YT9|((tU&SAUMZ%--F0e@WDZB$L5+00qg+;<o<9%R}@Mt`QMZ)9pr(sdS^Mj9uMZ(kZ@vumEAwC%v39rPb!y@6$_(E7D{5if7776dhH^U;~{rG3FNcc~D6D$(mhp&J|!r$NvV3F`=_%v7~yoq~Y1^0zW_$_=Byouw5<vy2rrwo1~EE2B7y)AqOekv>yKA-zpxDH+&7QdSNIvMdk`QIu?_*^7h4GC93!pEU~%$3K$C!&3{=~TEn621TlUydhXdG=*qkh;as3<}RBTmi2Ii`NYb+a_EMzXle+DJblV@VR&kSiEge*mvPe@UF0UpP+E8`Y?Xt17Yz8VUh6VjJNc^34Q@A5|%aO4!8||IoyUiy5Lf07xW<a;Dg+w!V{u<=<P^j@EPzJ_!)c={0#gUz6yQ}?u&1M`@;9*pTqaV9r2Igj&L`8HQWt;2wx081V4_?gdc~8;qSo1;1`f^I?`#;SXGQvFED;#V7PR|B_he!BjTk3!)M7ck(vg^?+gr!gjeBPV%(0h_>LIgPg(q1xNoE|(gFOh7(YZ={9uf`Q5OF$#`jVd|02eBQ5OFw#?2^;ua5C`l*JdvxE^KknK8bQviLhOK8vz=I>wbLi@y-#vXsS##kdq@@gXrjk+S$RF+P>D_?Q@1rz}1p#urc)e>=vPQx=~Q<7+94FM?OWP4R2t2|Qzq$P1n~{25pz{5Jj=EE1l8_k~5mWAOW7k?=EkM_4301n&lmgooh|!6M-o@W)}1a2g*5iwd4M`~_GfJQGjDBH_jOJFrN2H9iv-34eqyhDE|(;HzPg@OSt}ut@kI{y8iX{tMp%i-Zs0t6-7vw_MXzTxXH++xQk(Bs>G(0gHqe;orjFQopb~M>0>Hg_nj!!j*A(PAc<U$ozF8UKSP!pUSf!Tph0ri-a%W{ujO+KMNMWHYnt#-0N3Hyg$;VNccP?d>Y!%{96$&jrKGDmVnEm{j{$#d=}czynG>C55E$Yc}eChIj4BDps)?X=izt3;`auHZ5F;1?*@xM6cqOHA^I&I!s2~lk#IfM4QXpTydK<+pWlzm@%N*?+!KAd=Y(I2?ujXpUc_g?FT&5_OW<eWLHHVY5Zn*n3ipG%<2&H)a3_2l+zIZ1uZ4TS591m5VR$e;8y*Y~$KQpA!()-~>yb{6#_HrqR|Li{3Jf0~@v)K01;&pH4A+RbcBGpF<97#!MZ#<Ftuby-S^Ucwcc(1=J=`zSW08Kw|Bms)l*NCEaSzJkdt%&yviQyzx1=n-EylM{7GE3V>nV$8VtfT<@!2uHh_d**F+Q8J`0FuFP!=B><8qY6hsXFh%Hl&~d=h2xXJcH2viOTJu0dJ+wHVi?EIuX1^(l+big82A;!EH)@XdHb_%)ufCFBLq8~!XT5}tw&f<?lw;r(Ed@QZkNSS0)`-U${755;@HBH`iq!>~wrEIt?(3BQgHheZX?8$K2m3D3q~heg5}{9RZiycVAgi-fn~8CWE|6JHC9g!kavV3F`I_zqYk{5QT877721uYpCv-{VVQk?@!JELbGGm3v?f_k~D!3ceNI%JIVT9LYR&Hhw%T5>DXqoFsTIWd1tII$WSU^Bh!xYuF4H3D@TS7p{-jfW;dIg?uyj`c)Ahh;$heu8D+CM+caHPlk_22bh14g-=2UXkQh$20FmJTpO;BUj@s&By*OWQ~Z{ounodB@s_Z7hoG>{!k6JaVDX28!ahDszr`Pe#rwe`;rgr_($@BPeYib8?~cpy-BCa8seasZ!pBCE|DVdA@{IqOXZZU_dm|kk7%v_emSc)@TycIToQUqN-y&7R|9~sYGm&q8{tG`7J|)sYetwXj30H~qYot^0pW&*Je&^@E^E1oxvp@0E;BTTfeI@rrzL9XH$am+N`o6|1!Id~hcsE`oFcQwgzshr48wxnUzk%gH;e7mCSR`DOaTNca^0$n)jMrYqaxYne@e;0#e+!F*Pr<)|zoFlDjK%lkC&T;U19&C)0Q@tm#Q5)t>ii+kjIa0^v9T8a8$Sd78~%&?K<<ar@xS1|IOcTvE64qapAL(Jf5Ojz&!8PYA>m`WpM{UX_rN0IV)%EkNcbqOwfJtz-{lqFFXC13?_iN|ReTS;hj9`v8daJf>3Af393H^O!6otk@(q`SOW^;&BH`lrAy_1QH2yzWBwP&t7ZwR06Zx@4j31^f`C%k{DH6UI{~vrYTpK?G*M={||A8-rFT($WFM=<@Wh^eCEPNTB4~vBB;zi-QjC(!&C|D$1A1?xngfGYQV3BYg`d)|es6%eYCy((vmftOf7lBK`rSYTS(r_8PC|s0#r689vjqaz?_;0XCxIF$3ED}CG-$?jqepl*hh=gy3ll)wiq(1TMVbS%}C4LJm5<Z%&C44k|Jl-z9us!W)qxjwVg>Al@KHW{bO5;btMI!wjov#%BD=ZQ&haZAP!pG$s2^Wq0+DHwkL)3uZ6Tc1?UB~Z;H-kmOMak}hi^9j@ZSxDy+m^P-xr%W9Yw1r@ycFCNz7sD8m!lrxyhwk_T!;Sxi-b?Y|AIxrCG(Ah^CQ1H(iPMpx`N*mzXldv!|#aS1dD|8$y&hqa7pUT<2+Z>?k4!La1;0r{3Q4exD8$sE=m2u#UlM1oudr?J1i2efd2=Jgipvf5-!f~N?kV~;alM=`MKyy>Jx7SiyBdv_-(LAxH#E8aB=tq{NDV+_S{Pw#arbUwz(C3YDK%s;Kks+(Yd-r8icoo2f@$bx5CfCWAHoSG4NA(d-y4M01|#6(vnCs^33`B!d>vU;4W}$jv2)7ErHkJ&%x{9Pw+ADC-9f}Q}CDY7JLA_1zv$a0Iz`O;qBph@KpRxcq;rFek=SM{0iP0ZcTrMkBP3$;mA+K|A0lp6>)hntcZlmBH<E|8b`W{Iz(6TdxtqkV<g-hKM`&Yx5g{Nt>N}~S-3r%!b`v@_;x&iZ-;NhrCm4TSCRLL_`XPw<M+Ui!^81g;NkFSyahZOeiFYIeiD8J3HOM!IMVbybN)W?efXR3eegZ_%kVw$EqEHf1#W@A3%7vp#plBJ!aeX0;U4fK_~uyqH`6EaFJgWCf-&gB*eyoFYw_XmT6jA?8XiqO!VgC39O*H<75o_dEPgZmEIbOo10DrGfwzO7fcqoi?vWNnn#TDbggfJJz@6b%9P=2zw+LQ?KMSvcKgLJFAHzHFC*U3MCcHnq30{tOhnK^1@OJPVcnW?8JO!SB-waQHU&33#t>~}tLy@{h8jPpl!SD$DHh2X50)7|#0{k@I0e%{O6bbi?l!-Kx^FIW4#V5mE;S@d&PQka~ufw;&cj52BcflR-`EUogC%zKy2|tQ|6l?!S^htbYtdBbx1MyE|WAZ6u_7G#5LBi|t5%36(7k)TWw@5?rw(wARBz`+Q5*~}UgvY|e@J{eBI7Gs|BQ1+GoAW;mcf;R-yTNVo@o-!Cc6<_iJKPfg0B#9)!WY7w;NJLZxHlZqwxP6l8N3l632%fy$H&5-!&!V7oQ1dHAsljE;eL_sk2C~t0}p|p$D6~?!!P1@!!N?m;2q&-;DJcESEQwpW^w+0@csDP@cnQb{8hLO+#H_>H;3=W--qvpJK_uAj&Lv9Fobq3g*V{O!yDkw@E76F;9dAL@Gf{OJ`mmtuflu5y=af{&S>rbPTp;c7ztM_VkCSr{yn@)-cgE}viQmHPU_f&p9p`)&+IX~;8UZYmy7g6zVWZ~4S!Af8@xO$`jMZ14gWwr;+63qVL4uY_eZ=k{8glrBHoLi0%zr2s)+fy_(|{{erAvPD#m*_RwP`hh>`Fq_+Ge5qzaLK$~V3{-|)AQ_T`)MZdmdv9Gi%|S>wF?vPBC25c|Fnl?IP(96f`L%|1W-pFD5Tn@9Vey*u-l+4?vAKjDu5=Ju#A_Xpk08XqN}eMaw!`2`!^Tggt);Qs)EDlC)'

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
