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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_002.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_002.stl', 'source_sha256': '0df0f1c430cde39315b45a92b327f439aaa5ae600b775bcf674ae672695a20f5', 'input_faces': 1008, 'input_vertices': 628, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11728517711162567, -0.09137018024921417, -0.40370988845825195], [0.11699933558702469, 0.030681520700454712, 0.1559966802597046]]}
GEOMETRY_BASE85 = 'c$}rZ2b2`W7q>ltN`@7XBw<9593+bZgCxmO2?{JZNRlK$aSSAtAc{m`5mZoe&dh><hyoG?5f%g_3J3@&@_(!9K3y|i?sv|2-q&;P`91U7>RY#N*G~5iJ;$aEQazL{ApboPI1#SjEB@I)Ku3l^w!o0C0|xc%+;w27zWs-#2*ep*|L5t)jbCikv`vb@kidw-UAhkJJfLuuVBzPwRW4j2Sh!oi0fPo~?AxK=fG%CNU#Da5fnAk9ut&%KUDfL%70XsG5iD1<MDWev|K)$_R0)x8k8IhhwZYrVwTAY6@{`u25=oo2hIiC5et6hu@%tV$erUnd#*e)9?|!WbU6%R$K<_ig59OR;{J^ertBuazeN1bx?Reuy@(*5P^u)KuPulaY%)4ou86Ro(q47gihs*d{FUt7$$A};7E`FgaW_;-UCZ8XAx0$S~$v#t0()G@gf7NX>KD=hV86Te*FaE*yCV$}aI^%~swe`&#7_&y|EZa)P58o$s<{dBN=Qon^g`YR$Lj}h9{LqHp(uY+0r4OwuNq?5r6My++ssCOX$@AG+$un%5-;euJ=3Ty7^2{hE^>iI4eOR0*<4@$3@ndI8{To+H{flyozwKM`3y<>ow$5`O89(wzMj79Ei;QovR>n_EE%hINU-n7sU2@)2JlJGjubb;TU*TOxjURdBU8(bQMCw1j%lLthD~kX9A@N5f8b5S+m9PKd23y3x-$DAYV29K>e!2MTvP+(!QzcLPC6d2cO*!vLQ{=pN8zFv+>8oS=9AB@8_<KHD6T43Wxw}gKv|ZN5jt~6XOvab0wKle&!PyO@4|A%ljjcaey|#=$`j*ra+9iHcHSwpO@%1P4c4e9OR$h}QvSqZ-_x78&AFThwD{>w?9g+Sts~~>y&c6O6l`kOvwr8ZDnWsx1>SmGpS6*CXUca_p-Uo7ImO5{rFn(a&0^=tP+Pcxa{-LSyBfU2pKU8~@_?c=MKlIjO;|I3BW&H4Occl-5cA9w;e(ERVdz_Lw7k%pULzPeX))gAnM*LFief3BFY9e{c6_j~rMa;bMyBf;8gL4=^>C94D*VKA4KJH<8-*~s}&vL#)lK<w7W#+i<1B@RSQBnK~=ZqhCwWjft=46*VeO4Pk(()bSCp?-_#-FUX!syilX5QeLw8oDF=g9b>m1O*_dmGH_vboLpz|L9H&mDh>Kdy!3sdi5Cq`qYQz=cK&&FkSE514UB&l^8nx0jr+9*L4?!Eci1?oG4aggi%let1SFS?{{{WL-m(#2?qr<OvU7E`7^&T;{!zd!hV36_<H892CECLs{2}XMXni)yGJkdj^{E@gMA${Ed#9dg5=-k^C?JX#CLpIJ4eJp9|vO-zj-!oL*pFKib*kN%|}z{+oM^AG+Q`^7q{=`SX4!{;SU)kUBPqUm$GqCk6g6`NNslivLnB>BG*UKgarkjHP6~6>}c&`JXQ_`4cXc5P#V+e}6g;mO8_W#h;cz`m?*9ocBNHiO>6L{1@xw{BBPW|IVLFP5nzcn(@IdGsJ)Pce(x!SuORKpDOkDPm+1JjWF{DAO1xAEs0X+^xVczI6O)G-XYmnWp2ptb(`144-YqaLe=BU_)xJy^lgyw!-Yo5dH=h=?5m2;%6&q@rk`T{aIQRZzVf${^RlOp_%CNReq=^%>Cdn2WL<BSk$O(9l;7VbEoJ<{)Utn$J}P<2)?lAsUTMa2Ka;Sgu+)=rsp)et-FfNf?i{kO5|^0q-hGbeM@r<B_ksOeCC~J1{60>U-}fByz7gv6sMNWBkK}*(uB^98CaLGkeP5aS-fbiOPoJLO({19Htt)+dBZbuSPrVhf=P}gi!Fr=bddoh1=A!KXy#E+Kd~c-G&-FLH%w_Q#$?sjb&I%bHxM2Lq!Lj1M|Bv{;9TLCUUD=0uQyhr(14-L^RoC;UX`1NsTi@xg{e<xy{r=d3L$n_*emvsyudg3w{AHJoAJ~;B>zY=;)E}sDRr=p!ql_O`O8U?HcEa#)WL>@GeKpkRA?as>1ycX@r&h%NzC<4XLh|hY)A#;q{Q?(F|3gjMN}elo#qV-L{0E$uO|!-CU#h#Q|4R2npWn1iU+o8uzwY-dUwhs7r?y9Y{<3BxOh11(X#7yADdMj@CG~f?F6ZU+Na@e!*M0jie#Hps!=<J2dy$wR>w0G>=l!Vf_b&KjW%1X)B;&cR1v8hBzRjv>eDAsz2^WxgmzI;hRjMV|!NU*B`17gceK`28&krPAZ*E@K%bDo&!~NRp^(H+#DB|;-ep=t@Tj0X&b*8=<S7lvXAA`M57(cXYhVg?N9>{&gl6}Sx)LJF?rCh&)*S8rz!g%j`<oRy>)_3Z+zH{EK@0{OAWUJJ_ue-cId+!?um&*7vt)$M?Ddm0jv3cSLUKO9~PGt0S$y1}f)X()IP~>CrFBM!K`}-b$ccQGfU<27dTrWZukIMaM&7$%?#{EFTBZuVv^0xx={=oG;+_995-&A9XQLZBiqce%$=kQ`PZeV7=e>eYd-G|`ge{DB?YL#C6O#5U!*NcS0X~ds4?w#222|fRj`~Jb7oAKUtJXGbb+?QvcB|g{j;2W3M#LgSJmeu5mG`t|=^Yt|2z3WBz`5iJoczb|3zk{2a@zzgs{w?#m(Y0+xcYY&&(x+Wbo%cU9<AcX$ir-_L*|+g^8u@+l1S4_D`ri1+hoi(F+uppd#y>pD?|b9%la_ZCKRm0k>DLE|QvW0M#1HK0V)o(e<$j+$o*z1uMf$U6$Jgfk*KaTHdrLEm-+Qb0_ZrA`w(~u?{|;m?V*2^%S(7LJ3;8=-{bIE?>m2rz-}m}}pKxuF_<#4BW7b(Cd!iX%Ym)dGd(AW&zk1i!SbybvGmM_w>Gyj)Gu_mgyN2J-&~lpDCuy1)Kk22g_~Gr(8*O<*`sw+RH=CO}=A7{RUjJR6`V;b(h?sqzx2^aaPMG>bwSF}7T0j1dsXw&)q~G7T)6^NRSk&)#I6c+Wy|Ie%BNY-?8GrJPIY#Hc>G;3QGUuiEFFSp{Q;+qXc@vtBOg4Yi_vg31vo7m9^#`y1y)d~xTi@w(u=F1blRaNe3M@=+zggeeZ=t~{7bdrFldkkL_nq$hzx5-()-dNcF0bPcu4(q|%W3?6;Gsrl-UlW8e!Q$VT;bn{-<SHsCCm87C#8SI)a~7O*?Er|Km6kZe;(&LW&KG#<4r$P7xL%nU!kMP(>%`aH=SvG@A_-~GTl3wdWtRe`$=8oeTM5@bly(gOrD44`+ctaNyF;+=Z%}((~Q4=#6LbV@l`W^<`;gy>CHZ-|A+TDKG)?Z*82TGk%4CX-{1KC{cQ#rzx)BY-<Z&o@&5Nu>pSnC!AfQ5zyEzW{_X2uCAY7v@9e9n@84I}clMR_oqZMc{rk%L&c2Gy>)%(_clMR_oqc6}XJ1+0*;m$g_Eoe_|GtXO>)%(=dHws!`p&+JuGhb>qILTBRn+(IE9*Pg>*)FN?>Fl^`_1~!^*!OjcJZD23hO)f6|Qf`XPi$z{r4?_?5~OM-2YhLx&Mhzd-qG@bAJ^c^Vs&}{J_dPexLg~&revfMf}_Yry2jfw23}H%`xM9_XCj@>%`w%b%q)D%E5@wkIXZEXvJycCmo$FzH?o6eJ_9bjZ*WCpLfL<=J)i=Q@gju`i;XzgPjxo{<UF7Lv@z;{ekh~pKIp#SGO=4zHq?jho7k;<Gbeg-Z%buInm%ef1ck0Qcw7h-%oRTp4Ozb^ZkCwMDg3~_RrgImGJ{r*Z9XbpDX^+jJ|rp6EA#j>U{14f1a1NiGOmb@k1*X%uBAH)_3}8eW#z+clv34r=Onh_S24c`e}WqpVoK!X?>@kc3!8ScD&P1JKpK1^__l3+Wsi_Veb8&=T9#;+h~t>{Qj>`89%(TkKgZc{4=fbS3maqD`yx#G`^GH|F*pG1EZ$+{c)L$AHK83?`OPi?hiwSy7+zfzSQ$utu}t7{rmp$CuT~XuLt}6yc3P@-LG0d{vGjiW%v7+D@cCt{@L>@{blZlBQK}*``&$W&&7Vf?j+;Kw|LI)f7DdQe~`iN=X*%}l21Ez%6)QVXdb`6=d$_xC2%Q=-+ye8_#al1zhB<nJ3G1kV0~vlSl`(X)_3-U^_~4-eP=&d-`Nk=clJZHe*b>3zOx^!@9YQbJNv=<&VI1IvmdPQ><8;R`@#Coez3l?AFS`}hiIMt{a}4(KUm-04{_OsnswH#X0C6MEV~aS=La&p?(+lq;WHf$B<Dwd$>{e7$@{RI-}Bx4Vcxgh{GR`x{7>DI_sMY^4<+YEro89RUr79L>*fcN^}9YUpYv=vH!!*WxV~4v=ezxJeXoA&JN<EeH^18-*Z)s`r$4Um^~dIM`tu*3{zOXVE^6}hoja?#))&Uh{gvmpP5qhiADQ9z3-+F^Unc}x`TZ;hj2}7K+4%7XFPr;dxBss1^~dww{=2@{AL~2)cYQa%+ke;pPkyKWuJ85V=5hM}AK&YLq1;20>yPVu^?SbCAJ_Nlx4zRK*LU-~{c-*O<ahex`d)u*9;ZM5@##-|y8UK9xz{`EJJ&nwJJ&nwJJ&nwJJ&nwJJ&nwJJ&nwJJ-8t{r>Bn^_}aT^_}aT^_}aT^_}aT^_}aT^_}aT^_}aT^_}aT^_}aT^_}Zov`+u^&ic;v&ic;vE_8bDoaFX{^_~4-eP=&d-`Nk=clLwzo&8{aXFpiq*$>hB{rkcC&VI1IvmdPQ><8;R`@#Coez3l?AFS`}2kSfg!TQdAu)eb&qILTBgY}*LV14)gXVAiV(g*+Fo7Q*!-n72+_onrozc;P#{JrV<?%$hsyz}>_^_{;rt?&H3X?^GKO*^mi_of~1{Jm+%JAZFl-~D^Ddg=Me_0#%JKdtZd)A~+7t?%^H^WA>h@lHRj@AT99PCu>h^wZAk^wW-a`f0~I{j|Q*&)~UBUzt4azb|{f^Eq(T_kRv-edlvv>pPzVM}7b2z}9y@2ae9`{~Xx*?!SY3zVkV-^_|awt?zseY<=f*;Aoxx&w-=!`acJb&g=gi*!s@rz|r;kKL?K1>Hi!!>ia(jj-D6)=e^c<KJN`L?Y|(o{a}4(KSX{1ez3l?AFS`}hp6x057u|~Lv&vMez3l?AFS`}2kSfg!TQdAu)eb&qILTBLv&vMeu&QN-w)Pz_Cs{N{{0ZG)4w00zJEVN&x?OQSl|8krsJP2mi2Bl_rJlJW#n^s&%d&Ev{~=j9ou~V^?MU#o+W<2Q|ig4&x3a)`us)BKQ{Yn)i(e5-XBai^QI~-^NxvIVl+5wtnq6M+2-@zc|G5q*Yn+ZJ>Q+TL${U5&g=O_rc5yB<y0=e@7Ck_?!2Dw%$u}&&dTKaZ+)l#)_3Z$zEh9&oqDYA_F=`yRYslr+o<oqZ?wMqT!H61|Nb7DnwV_<sPEjDdcO1gfc2f{2g1*vG=BJprSk7cn{OY9^#l0f1^+v2>S~x`wegP?Sr9wk^TR)j?~RWi*>-hu^;qBOgY}&{t?%?F>5EC?JI|k3-+BJT`p)ww)_0yi2`-wv#;mJw#l^Af_51+7U2m0HYm)1a=ezw$>N#gka{c#wxBm%iR*S!Gimx8e53il#t0&=p%eBToxAq&~c>DmqH$Kp9r1<O7Es7oQ`Qf$Vd*j1<Mz7O;q+2z4UT%0NdH$`<B;$u#HkRk#rqq|`_byB~zV}>Qc=9mux34#TAl(Fc{%t`Od49XucJbZoujjkhHP3gR_p`q9ykEky-BSOkucV&$M)BPH74c6bN&U4d%ky{(?n|Dccf{wp%3$hL>yxX~`tJRh=R40;THkrDGW2d9<A-iM<$KOEc&32yBi{EE$_<n{6H1HE^U0wmFUz|An3?Rn)_0$e^?djFSkHH#kF9-JeCIi2>pRaOTi<yO+4|0N$dO_>H<-NcbKsv&HGX*bv8A#5Fsa3S@mKwCY3x1>pIK~t?|FXv+~)Z2WqkZ|zVAVVMjV%UPrSG+cAo@S2R52M2Sf7wSHYn_#rmOg^8C5Cf071dG=8{h3mO01M0x)6^El%NmM&NpyRQO`OG=*Ce_j@Q-a{uUiqH31yz?GEqo(-H<@s>$yocv^lR6h1knibSIw8+<rs^YpCHbCCc<(Lwp2g%LQqS0|QfHgb<+;;fSn7W*r95v~v4_-u@<SQlL7q>HG=59`^@}8b{IBNuvf#`q(w_=D#qT2DgG>1CNBMVw%;%;4qSNI2bXyP0^P>H(NPfPj7M^!iK5zW@w)km|nLP2S<a-41xzlbk`P+7r?-`9gE}vW0%V2!>`%saBC5#_hK1cdfdyG7vy#EF9&o!2H_1q=TwXXg^{BMdFKcVm;sq@-$$$vKcc=P*yzKr=?J+$_;&yT+sG=8}4)0>UID(xgw@2Ls$IsB3O;`i=g?nA=&=ZgPHEAjJ;9%WwNTqyZ(w)5o){W(&eqnJJ1mnW2Yvhjl@-}B`O^6v%lS$2u<-Cymz@Ar#MGxtBCQvXPv2}#CxzkeG1=B6)C_~$D!-t);5ul=UJZ|7dEl2j;CTD3w&+Ca8Iw~jGi&DEy<&(q|;n%lGd|F5s+K3%5F|KoRa)Adgg2)v<U5E_OD!9&sa;GyvA=)3Ui@Idq}cp%)5&^$uLn=0N`F_O^y4xxE8Itm`HLNzcj1RV?yfd>$pUxP>T^O5BB#=k?pcVco6hlin~;9>A!^lf-B{2K8#YigmQrHWQ)YxrgK6|^<nK}Ba3@r33sXm?m^4>%reNpvAs7sj+EdXT>d$G<{!r<NAf(Sc~ioL;S+(eChzDqd3225k$sL))Wm;f^Z0s^~;$?uPb+wf2HLp)V2L$kmN8ZHZpw@5S-$iJsK*B6V~m+AybAYge=<JVE^qeyCzR`T^WWML!io(c$n=cs!w5=NP5pT@|Cz_u%))I~tt;PvF?mgyvx?`l9{N;qWNNy^aopUx$0g9N(Mh%R2g!qYt%>Vx1qr-daYnzER{I$}vO9Hxys<?<)4HIEVfKpM%d6ntxPrRmC9{7t#IjMfi7OKlv`JIH2MW^f3Gfe3dv%zVpm;0o?~*fG?v5;J;Mdipg^;CjTwQXuSbzy#`-~FQC`q-&y}z^gMi?pPwZ(UqP?KTK|N#-iEKh_s~1=9oBG<(EK-{`6hZ5z6oDKFTxk8`x1H<-lO8Dn3{jW*Loa2PF~GNRUDzm```oU&#=~C-~;es^jG*We26?hQj69fV6A)MJ@8NHet17Qej*N0?{PQ@{S{7vPoXDatta49@Imw#e2n!UMEAk_s890^)_)B>0$+o#6GzDL7j@i1e}QkoH;7-zcbl5-peNxw@L$A9@?B@1Khb0GpYUz;1bm8h+(WOx$LXE7$29-V&;I7PzwtGHt74mq?PwzWExHNa0Bc<VYh49zR<V`i6XET|R*uuUK8E!%5p)Z@g*qbWxA3>j6CpHjRIw6Wg>HhkGHyM(5nhh2M7<oVSkFpg1!GrG?{d`3QC(fDs;MYSXfA?=V6DYs_<3FzgG-=wV6A0hxGt~Dz)z#KV6CNKT|@B{Qdf1j24iY4t_FT7^5{7l5}IqG&%@7CcTGZbRkRvhjrppgHQ=TynyF}v)`lCy4G7Kk2+c2`RpF}Se1XthKW1(9(YkPbxDnbA*4i9y1UEsO!Of_<3G)_a-C9e=^r0mAv{r=mn9?fB5}L~qnkx{RE2GcCmEkIc=4a67;Ah}UXhm3`%kn8?50uAy8m$OF4VOVnrikt<%_RuU#n8ejqI*?y5kj-K=QS5c%fe-;qc~a$uE+WFdh!BeU*MdTMa#!<BVLz>E1^x`CiKPQrZK&0N-woGh8xrCD%4ORMRf0JZorrZjB9|exf$o9Hd;D{n{iIGHiw^sD-xRZJ}IaoyNajKobcl+a;wNlXwHD<g|%jm;UKRw!&%S*u-0rb{3Nfl!H=O&z*@7yx`s!o>v1?gWAZaDKYmu`$i|wo!#UB%;GA#{G%K6~&V)V+KS~{$2+iry3~&b4pPtYhhh~AZP*WUv@-U~?LNPTIqQ*j;6OZ$-?kC{<L>_vhHCIfpa&g{r!+Ftsa9%iw7KDRv0rV-j0Q@9c2rfiTPm(`9`O>r2d_)}i;^>3s3MtjTR8a}73~Q|eSAuJy^<k|qz*SW|r=mJq4X%n-B&w6UGF%6(4cCF|qxE2&uO?%w!`{!e)<tW=_4(NgXkA#>R)KsKSX(u;7F-RkNz~%_TIA6DyXxI}6+aQ0_oEkJtp{TG60Z-yhtNM@tv|=`HD3P=A49LeT93fGhJz`juHWH{jJe3Ti};#<QE{Bt2jL^=3HS(n3_S&FJq;g&e<qKvV;{O7-p`u%5t<L9hu}lxI810hNoYQco`%oDzoBPftx522@KN+v_*d3{6g>zZq`srfdy87MUXH2la?DyZpHp#1#cj^pAMiEeHs?X>pRm^J@D=zXdIQ#b<~;e&b6(G(7vXd8RrCg|^(L(KFZe2a54{WDWexWT&3_Yj=)oP<c8mCf^=rKZU!v~I=sEZXYx{-Jd>s7~)_Nj_Z}a*Dd<wk--{IVQe3#d!;WOx8u+}74*YGQK-GIG5-DKQNd~Xlw-u;H&gLNNH(kHEFWBPWMac3E;`BC-WkwryTG#gw{MFAB-G#{J|&5GuOA4@5@a-dn^yl6f&E1aEUa-uol>}VDuCv#?lgJ^y@2p2@3guS_Q5_$P~e)viBi5Sku>wK*F38DaFo`iM&1l7CuRm?`m!n5HygywN7K3DN!3OVjWj?w(3ib?!@5<k;CU&RC!U!fntU%_7zA936q=9!Cr0MCWzqZ49Sj~j!Ig~w9c7((-S^h5YV<{VFG{uKQPo}pr<is|Sqcse{4{S^L`W2X|DKS3wJ6R7(WLi1#F46Jn`JQ@C&&^(3EJPn-*&!p~Y<k4&UjL<w!#Uk`mbUdv66)F}JnwO%>;id30Lh};z3wR0q4WW4<p?LxN8LZFc*PQ3C@#dnRrHJkU&EB5W?Cn*}3FtgH0sfrO{AJAgy}hUTD|9ium^!{f=g06T)b$DHW&trdW{s0MS31vBj+@FcU(>_s{Cqk;TTI`k(bs95N3YK_V){RW;}$Z{H|Ug@o=+j)6mogzM4zXL=uB9j`&sm05xfGO3D4vh&3je+pdx~9fp@4_t703v3f=~9Cp52C@tukd9JhgEG=HyR6F=X?&ou8=u~EeybThmM{+`&(aod?^7rGwa1@A^T!ig$&Qo|1TJM;(mJNSEaZ_K=VsYUCLF}3|jey!iayJ4@MZ>jfN>hOA%NdFS4X&Ym7t~G?_t(=3c%)b?XFTL2z&m-_wbR)bKUW2ZO*V8+1F3l^^Rq!g#-AY39I&=fP4&H)pf;Umq7LHxVS`%Tf_d6N06JK*7bq#w;MM<<2tfO>F`MK8Oa0$2!S{g3J@nz5waA6gXt0;=*g7fgY2wE7<&CiOVMc`cgtSDLxZW9OunyKhWXnqZC0lx;np<<wlkt(_onqNWRfZt&JD~#9Uo**>mL0^IMz}e6ia5gvt+6>MBr$gJo>EJBPRfPEm!XweA;F0hfXb^q_ehtkX(}&#jDL3<UMBBhA)Sj5D^j{UbRh&_=6a5F)`T+h~#Znbt5t_e1*TQQV`vswSKKcNDz?}2Zx$q7ZYgDWzG%rS%z>DDp=t6h_{5kq1{5hO}&Vv)+xx_qbm=AmP&tt9gINn?Pm-ORH=KGphNIw=*-%?@;y;;I~))H&z%^KFf6a5a}3GYTv!@J=#=w0{>{118`{s(?Q+^6^d!g??0&>TST!a6kn5AQVmKlnHFJNP&Fdvpi<J-iED4L_{%zpCO9v^U&GMQRm&(KPU@{H!<HH|Ch$jO&fBIi-qJDrN^nrw5{}fA$ceIUSl7p3b<L=tHm$&CAequnx`Z(6sP6=JdwQCWqGPaDVk4*Ih*~LUT_-^Q(mBekum4=%b<s+8fr|7w!QMV7z|aAMFmusmQD%Bbo`;ngQ0D9!{qswTiTa<}~Oda7JFoq3Pg&iU+DE|06X2OK84NX#PjV!)p9PDpH{-VXZ0PhtUA4kJa2-MSFeSAT)PU(M&}<6)gzOZP89}C&p{;pdwyHSF{`474C?3fjh#l5Sm{mUu%wQP2R4IX~A(Vn6o3=6>blEwRK}n-KePz^*3X_X3W`z@$DGf4o`Du6%ACprlP5e#wuD8nqML`w?Z4j%~iapq6wk75!woF#dwdOC!f|DG5KpSr`Bg<YIv5qv_1njg&U*g;Kp!6^l4aYS-2tGh#GWFA@oH!1Xn?u!&Tt&XcM>z`O2eZ;TmcSKBJ-`S_#(w*Ns{#Dx*!|%5X)rIozD%Dx#I(w^Y0hSA;90V`6fSVNR{@!_UICi1(RO>twho?A1|;Ip2cA=reE_eg~}qzXOj$8^Yt@kI?4uNAM@;WVo=3f+}*MIpADyCNw>q3C^hEX%)p(lp!=1A~fek^TT=JtY~&PE1U++2xnxjG|W|wd|Hdc#o+vCJ~%&|9gTyt!x_;>;EZr4G&Nk9UOY)?ehke7XJY(g^q~;FEC}ad4e4Xno1T88=jVCRLhwT>GOKtPeH?xmeiSVV7eLFRMd5O2akMC09L|S64nN5{3J{Nx?=jZ+D3O|4QqwQ5wnwP_5&HWO5yv{>m?ty(IJ`*35EY*hn(GsqUq-va->8_SVlY|{?t->O>%ogSW(YbM_Kq1sbYYGz9M_d-%e?i`dT3j?v5FT}ynwcYUx1qsnp>-wfzCnO!BbUCQ_&J_1-FE26Pl~3sEIa0TftK~W(Lucd0KLOYoa!F)#iAw&T7=|&Ec)3CTpEWy{*u8a68uDig=NFUgWq&Xid12iVi9!qMhNf=&NXFc#?_%Dn3Sg!9CILXfJqd%yE<80mQ3}dzJjXh|V0_nVPy29hj#ltZRQxMHLl;(5i5Mv;kTb9--nT6>p+-;W}sttqYGJ*Gp&v_$9b5S{1GfhtMi;2(Cj^p?3XW2^H<pQt%YCI-$8dS_)39B9)4qXi7LI+=EETaqVIK-=`{`R}qg^fVGx}Q=lc$(s0uTDN<%j_5bz1=8FEOpP>)<{zqNzk^Zj@#2z_Y<+5KQXxiXm{eGs3PiZ~?n67tB;Qs(IT9xw'

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
