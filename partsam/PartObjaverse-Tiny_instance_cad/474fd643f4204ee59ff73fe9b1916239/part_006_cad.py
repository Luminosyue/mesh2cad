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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_006.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_006.stl', 'source_sha256': '885dd3ad9431f04ca04523560693fdcdc860f7457801cf6c1cd0d55910ddd241', 'input_faces': 742, 'input_vertices': 592, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2016495019197464, -0.20686979591846466, -0.48256561160087585], [0.20166581869125366, 0.24971431493759155, 0.4561471939086914]]}
GEOMETRY_BASE85 = 'c$}qt2Y5|c+xAWn<y8jJ#^4ye8)CFz6TSCA7)KpFgy?095+O=r^mZ7%w}_})mms1<FK2XyM42&+_V4xFxA#r<`~TPVU*DJOdanE4_gUvz&t846y-r#-NtN1L!(Tz|!avUAS`~|0mQnN8hW82_*0)Emp=AdR9_68ZBf9(%=QeNGtYt?JZMZh3SkGQVdjuA%<|yXdyGpUrj$*w70*3{58`L!*uxBr&*Y7r9XfI12+Nay#Ue<N-N>wYAc2q1;+A+@YKm5yJh2UCyKIX86`jEB9Ybnf->y+TBBBC3i6%VRwbK{tk3f-Nl2mT<s_5iwL^UGsO*Rt$fuda=mf5a(t7NCB1m*`rBXQI32R)&7yJMm-82)HEq)`4z}%a43N3=-X3aqg(3uU>AiTxYH!x~s}r=tZFGbA6HiU4Q5=)}9c(=CRX~{`B@EqJMljPV)Iz(+iTme?jQG5A2upS*D;I0_GeRJ!}^4t8Dvol0NCwLD9R9oT$*eUG|#XU*rksVZVrO+=s45%s7brJdVltv$u+u^rNRkfBNO9q;o(wlj07DpJz*4qQ9>!@tYA5&@0T?EqbO_u@YC>hx<j}KB}jrtI*dJTwWOZi=6P&p|jMpIqBj)$#>+lO$r^4C!Ll12ni5f`{vDI@$1MHi~8>oE&7fzOQgM=%O-Ie*ULuZK5HX=-aS&@T7mRPzpwRj$#?ATo8o75TIg##LZ1p<EA{JM@$<0tI*DW6V3bEX|0qd+`CO=c->0zDi#Fu^9?`EonJ)UXt7yMN#)|HocFUB{GqhVL>0J#(H>Zrj_g252CF#9&=*!chy{x)7N3e1kr0bO*?V^Trfy9@)km!2$FA|r&EmypJ|6xJsuLBNA`o<qtOI*ELN6K|GpLv3PnuSR@4Ji-3Pk(&RIY!FOY;$|J_$wKLe5=gIb=*)v*Z3o%8$KPR-i)Z8qC2`AK8k+%Vr_EW`C}!N!|}Lf;-`6I(T!=Xq@K;mt59E|^+nfLwn6<I2$S?$i@$eCy35C;JsFK3<9<6O>_R!V*(cwxUgxyLkv>**!+a>H_sJ~%*^D}b^eakBy_#j;UX=Uk6pZvGGN3%u?v(p*$BoAKa~9u@_{ZTs(vLv;-6qQK+zph6-%$8pdTX)x-CJ99*SG-au>~Uprxum=U`F+a-YSRmC-bksLx+>;dZ8OAKTkjL<9_uE%AwI=$ydLLamv-H9OCgygYWrO65ZK56ZFsJq@QZ{D(q3{-t>5<_-XwK{WGqVj91#cYocr4_eVQfIeVkh9p^7Ye;kPN>7GOU>*+5*k2!*J@!h{Ixvn>Uf;daulk|?wzlv@g&WQ2wz@Ji&?oOfbQ#2Iq(DfAUV%%`VS)(_;m#v?)3wPe3NZ%*p4vBkos~ZYkQGw9Y{tNnZ==!`0_<q;9F2RM_*TR1xq<=g0h@`JuBo_TAFZ2PI=7@gCcdqz%eFHzi(NbSVyi>+yBh&-;Tkjt!Z|BC&QeVy~XLpF7njfRo_noQ!yddd&AA#Pv?kK@e1D3(hR_N94Nt{-O!BYPBL!s|ZG^D=jhGD)uKMnfnJECi)pu7DhLLa&l^`EZEjuiU0ndZv<U){M6_ZuX-QEC(BnXbdPNV_T>xC8b1m(;u2FBAH~&EC-8uax$w&1xs#bKL0(|D|5Z{N-3U=CY*wvoZ7}P3BW)?ZQ{(+P?<$dqXhZ8zl}S&a%*79+NoqXAPx%9lw=8oC%SKq&`-Eyds}}){tJ$79sxA_dh4)|BSj<Cee+*`a!SqN$$g#UsKTC%pvvVD3~bM=C<NkXY>z}_+7E_xbK_`r60Msm%oVgOQ0wGjdp$}*9p=67C~>iUD}WSm%ofly8i;`<9DH5#X#5UPJ>=Am5isZ<^!ZZndVgJj$1Omna2lT5`E1W#DAfWtT)_AizH6R${|Sqsg=xM`X6T`9_>YI=neg4p3;58(SJ9$fc|Sk(T#i&=%@MX!hiNxk&-^gXX&So^S(@9Bv5cz(lWV^R8^t3$`FnFT_JJ0Z+r{=r^YhgYSZf^Nc>|w;D2%Sdigv@Gnx0Dff~}UZ6f2OG3q_$iQ<3CxT5WAB;{{}){=gtpL+%U^TAc(fASBvrJP>u72WW-F73ql`~>afToa^U{r5~s-zEg(*4;+X%{QVu@=k+3EkFEp-7e*?YhAC1zrk6M-m{kU3nOo1X;-FiT8w{Q1x0ss%_-%kb=2VJ@kbe#jOXXCN}L1VZI#bUC&@UhMV^y>VJ^QRy3t3MdC2^6@@3r5S?F&+V_n){CdzZsanbd<1I3SXQI2ckx8gzgU%K#s<U1lC{CC&_{os6=Z}ds6&!XRlLXRE$o22($9iKw~CQSTjUR#mx@(}15kX{>s^!ki;h;v?3DL2QMGg4pXxz<SE=hl3|#EB;b>ogJFtWh~e+H=~xm!ZFt{%>?Hf_ZXf?hS&ao{Dbz<U~CM^~U|L_#Nrby_WT+`-NNln1M^7m+y?{g?VW)F0Gy^x;Chcv=e=D9q0+;p-<~4<CrnqAN}rR7Wj#uF8AfCUsc8dqt2Jjf<INocy;$koLtX&FS_QxSms^Fqt__U60ecoy$=3ocE<gddWrP;I%55>y(HEZQ@0^~*T2!<2QRslLccQy>!ObnF|Gzrho9_sB)ySoj>M@?n<~2LE`fF3x*C|z>vTl=TN|X@^pZbg9vG>^{{j#3?;4Rs+Lf{42k1X{k^bl!)&%vtB1y(Ct;UwkQl2|YqI|rl|F%tZXFurrsaeo>*OGcP>NmuE)ing`%9+EZUbKBfq`hfTTyNgKEb9R0xL~a7KHl9ZpFi)2=ZomOSV!f!4LwgM(T%`cXzyDSL^n1k%J`@^*m*p;u7%}Ae|fV!0iVZ-?%uad=2vZ2Q9Lik9f6<sspa`ZZ@l+9%Iz@p)!C(d9C2(X(|(2CD)lbuzu%8X{uQf1KOYr^_Bk5u@Y5r-_Y#SCE{F>F4dq`>bR%GcJny)Jk6=9X%PYEBHXQZWyOQ*4{mKW7vtA|f-2Cbx#?c{<pznzhG~V4sy>`0FaXF97gL<6=v|GO*(aoE|7?<W?e%DF{h^}|<D(fg$|KVt#uAkvI#~;$JoG0$#z7E!be?K2tUz+VJoR{lXIiasjhxW6!6Z%nbTKH+0fcAg&0oq&K6`AL>Rn=vF*R)QRMW41obR$njnUCBr5x@Q@0`sEB&+`0h^z0z(J)=q&`0);wdUu6XK%9?i!O!Q5D3_Uu5|0^GP;__t0_aEUeK78a#ml<V6*)Q<?d19ji7Urm(cN{!q@8JfA|?wuR*SA>8IAe<eiLaY=8%<me!4sY^G?;K&|L$dXRCQu;$J@${ldT2THKenl(WmH9riUw`68ZY-4Rc#=hA=l&z{J4Sz9RweOhX?TmR>4<nu!FvA<B->xSsA`=Xl@rl9>i$c=Hd?rqVv@7Mn--)rx}c;4?E^wIrMj|a9&{hFU#q8p+9SZBM3qo1Cdj`a2KZ<T!S&XjW2_XZ=L@WGPaERb5BuZ_}Upr?&Ig8tJR^Kkeu(cLp&%eu;_`yB1u|IKRgKk2PJKkF-+%lAybaOkIlWFNrPVy;X2eoaL;cCL{7bWJ&d{`I*4^uIQvUCqiN^`b?*k$!1jC?xIQu{S{4zZTzAbZy#HJm+umz9s%2N3Ih6ZYS}t&#aDd#s|8w#vkRISPk_X-$ry-{+_7Uh8ZLdeOht&xfd$yE91*ajQ`(#Tq&R5c`oCN*?s%*6#C6(NFSG4#&dn8Q*`bA6pXjgrxAa26Vcs6`eU7XJm)0zH($|>@mJA)-V{6|<yYpFJhwQ8mq7aYThMRgcjLLM<$lBwb`kSh^cp<p9H}AgO@FfTw#4&g0@Amdh4FUsjM=r4>8{NCPAPOgY=?1iXvY<TnHyo>u61LnALDF8(M_+(QZMd)xL@PXq~)Sl%Z>e=vvZ`}jFqKC*B(xi{Xyeh6NyKg{vGriNir`RbsA$mceegg!TMP+jx78Y`!2(Rus?Oa+<7UNV;Q6$8CPd5l6<d~Mt^+oy;911UpchP<@>M>TpEw{+ofXAUq_3sr%$Py7dK)Yd$1M#baf9|SGn(WLizW|AnOb5fFb=;tNIA*9RKw)erV@)c@8vU*ULPjUAu7ea5CMjc~J6oFF7r`F?VvfVCkHaUSF{u`R@E3`&H|YO1pK$@5cSsi-aDO2hVHoMkD?gXJ*UikqeNoI~w`EXgo{wPu|#<7(5v1cV!V>+gBdz`7isCK0Jfy`fN?=*YtECU+>p5MK1+izgz(N`eI@7y^h-!3jQ2|b$rs+8S?q69a3M8DyG!Ck!4J%eEzPA%sX0A-<v7)q2;7}owFT?=he0l`TU!Qvd(umEpbb(8^4<>xUQMZ?`Hk>@Uvju6v5Q7*soYnRMKmY+hcyX*+$Yk66?eN;>W>)IS(U!uhQ^;Y6<k057AD7W<W1BUUXx*8|56f5c-ae*cbK<7ytU0hVbuqf2`<<gHX<!Ti!~ccZ?T54zKReJJ0GXeph~hf4_dxkH6|>myFmCjXx~ogZAzpq~9AfT>SeFNB{n+FI)t@Tq!e!-Y{l@lyk|!$5QCi%1jggH+@d0(04zT@xr}&!?_fC;((<RmwVH}6nd*>^8BcOza~C~{yuS&q<`7+VshP>at`Z|RpV0V+RG4`ubpRGCZy0auEz6PfzCHl=()0^oWs7kmcqZ^4U}{F3n_GM4(ibn;{iQ$+J2J$+bYt|joce<q|gfv!#;oKh}abR+G!X!(loxAT-O7R$-cIuMxhHS(tpY*>sxL3l}pKWEv}8!w_%jR{RR$!-hBk_Yrp@k<hpV08pe$r15@h3kFbtiw=IQkhCWAoUbHfWuAlo6_nV*h8#@8%m%o#E+@0>-Nv`W-dr806<IY}Bt{cC-h5qRZ#`*lIgCzdbhcGT@oCw{yc%)pfS-c(PS{LyIogF3mp{A=)Z}pLWU)T(}w)dm2x~(4>nfzsaVDFEH-y&(p|J8qg-!mKSEoFb#PN%}Yl6`y#*bm({p14o-2p9jh@yFrFi2X9#c%{Gj1-fl~b5CkE7yUcsIQehgHcmR*^!Zi%*vH!iQ|HP3*v4%~rV!}%alY3)(e3ksnQGTOwA+;Ph&gHKe9>+5j(MTZ0=c%$Q|=l8q8oo6LjO&`yykXfTPV719(4G}EfU=}pMKTt^QqbD!D31GJ?3Sj=0=&9U0e3bzM6gB|Ek;PeP@G%NN-<16i+4X*uD;N$M(X0nQfh83>*tR`*T^x8$-9^{iAtE^#58fmHq>|ZGGh~))4zao%^6&ufw`mFO~@1w%&8U3zGL#|Fxc661E!sG3EN)`O7-!w)Lucug)5|j>r1e{5=)Qp+x|6+dA11`xd%w9q#z>L3H~%T<=f~?`>@Be4|TO(e2L#X8F0$pDw|^_wwU1uDaZ-@jkG2BRr=pn<w9MPU?pD(+O2DFP2Xu<>xLM3q22>k2J3^c|OwGJr!Lq*bvWCAHq?7F&Q^VI@|M?GsZ{s|9ZX~&;;pi&x3lFNYUM0wqbsq<2yFFZhsDSPPh+0w&z)=`zg}fo@bq3e%pwCI#Hgx&BZ@pKOyFl=z9Ln5|29o&*`rI&ye2sTyOqfU*>81{(!!{o#^)c1Z{FCbld)e{xTB!PuRyW#|NQ)PZyBy+xJ8Cw#7tuFK&%`yirp2arD8%MYr$In86F-Cw7LcKaFC0<bAX2bnY#ZE;>M-YxJlDyf=&(CAxiI$Xw(S-MQ?btdpE;(p*fgYs&+$o=yD^-mBDzg6`8pp1+KUet19CKLP%2`%&(iUeeC&`&Uli3}}Ce*zeLhMoBwyx5)$j5cc29H#hMd6!aZ*+y2{E-3a17n-})k-2KLg?rem8Pe-W%c>l6!5&Q&Amwi+tAzH=<!*@IM+<oz$V@nzAL!6GnK0@1Zc%Q#&Bg!oax>mHQjO(rz9b!`G8$aQFM(tZE^(wPv95pUs-@;ua4*HEijN6B?Kk3N)5cw8wfqm3{rSRT-`v=kWcbO2U^SV6$Xgi?W-wPPNskTY_%eAGvj0e4Bf7@|4kLcR#K2zbRx~yZJ)a~ynTyKkuZnhqe=kCtI(k|S+%EFIrKh_ys9=dJ+R$ti{dc;|&N3GF4j5q0qK(BCG=6SPMbW94pA@+yOkjB#foi#%cr)@vkQDiahH%|=WG)u{Irv5e#@vr#=y><rFZ^H}lZ`<G2g0H~O^ZrObwzibBUgQP*Tz-V-hs{ay9O$HOe}AMsN<^HteRZSRTb6UmeR%iO+*lWm@x%Fu#7Br{<af|*`~2pe0-|dt+Mzu>t|I#au51p`^~&v`mn)M(*AD!R``US1p7WihsN3Ez81+j*&xhv`y(#*y))TtfH$D7hE+Wt8`nO$?-uAvjujCZnS-d&YZ|^WZx$X!Ui}LLALh4I9@(c7AB@zF~0(d^J)DQkU;601Epf=uDJ{^eivAvfung$@w)5qZd*Pik|(3x#0{A`H8{))>X?*a74Q21Fh8u=a_Ao~}N{Hsx(ucNph8ZPG=j18NRer|v0sZA+Q*VIFzyQf}-J~j&Dbkn1_ujh+V4%ecmOTO1);Qz6Pd~c1Kom{uS&oYb0A^r(?FQ(6m#k`<DfPQO?tdCq%e#89ImAdVHoXhJ8@(r(vd@p-pza|@W`+GWPL=xgT;EjE^T#fL4|Dy-i{kHdmT0k1;@4`?H;pwHko!g<?-#>oU|Lgr@B`?uU?^*EEGmZGsKBR~L7L5^q*`Ng||E$n`b=ki$CN7q97LIIrM0bq$M)~WnWE|5L7eIR3`&0Ka2lO!$rQNuOhDbiH62%cu_gXj)G2w)aV~&VANN;~HyrM4jjCe2XtUVR_ht4R6CpmFn9TPDQ^%wztd^GgHwCEQ%Ccw`h*DzmX#rtSSWH8c?d@1`-?tptZcXVtK(%av62dszwHjB&$u6Aqj-m2+-=(hLl+O?z5+pzq9-y`kcwd^GFojpP3M>ES@X`jv#aiY7roR|A_%^Qk-8kvCSy@6-o=kgJZ!@Y08zwN!hKJhX9+s+TTpClr^?HqzD-%IGX8sHpVwK>?wz5hmZXVxUtd+<fs&vkD28|f>&Mm&FaTbNwey)t3m{b@bsuYeCoe?K+e^Bl(cKX<wUJ0(urISO~7lA_zsU1(=3L*H}|`^sYnA4s9w&UF~Ct3bD%12LBkfNndd<U9%8Se_1gx7MN?WrjiT{;RYH=brL>?=VYreKpRj7^8<_{k+%(|F&~4TEI%^u8BBb(&N*G6ne>25$LZtKch9>jeHL*M!#7yS@!cB)b&YSv7SsbTHcTSTaWpO^O7&iUQD51J<4-rLDJ5hl@B3b+j{KZx^3O1_c$iHdA)|56VZoE!+9~UbBNP+F39}pA<_qY!1xe@b8e28kKn&tB-S}+tKeMFPl?cN=akIr+AgI3D9;PpgpHD3pPCB#(Sp*i%*Pq=KDTx{(G72$gVHx)-R>NbAL+|p$8*206YmZ563}huxQqzuwsT+RPgS5-*W~_PZEK%Nt{WL@$@?L*ucy?H>Fta3pN`>qB@*}RF4qA1(p9n_<9=9L{1^+GL*MAY{%7=Rq|f>@^aBRYt#ufP^PE?^A>TcfaGrPj6P#1@8G!V*^KY)vBcZohjrTtv>f=4x)S1wayJa2j&fvy+@_q#LJx?(XB)pLKF0MkGpxf4^j;mXt+t#JV)!m3Q%bzG8f1E$nl8!;oJ_Y-VEpQG{J8~L+0t+q?KgZgO?#y?OapuB%$X3(wK77<G=sAmGze+EJdKsS+=cF6QA;0KcIKPmu62^Dic}R1;FZAp^&|mJ)IGkM98upQWZ*Alr*}v2Nr~}=M7QbedMtJV=sf+dZ$5}YHc&vduFSwI_fq&!3UflmqobOBQi#Qu-IESmB#P_aGg#We)(r)$No1oqP83w(32<m;@8QfRajnG4m;e71z8R)N9x4^&ce6R6-2jV<j9Pu9*jPv3>A{l2V#5e2b=oEVYJ~%J(%OLpQZNh(sJjnOP1)K|7a2|T$D_Ad1OOkk<;g^tan*x{z8{?e1+3ODCk18#?{>>enM>U>8-&7Lid#i|`)8`rdd-)>1d*@_4)R(1}`Oo-p7w1J!-b|sJ*L2bKdB1E=uIm;1;{NO5e92c`o9l-E0W)yEDt}t|>F$m4DU)5|bQRAC{b?rL@A_cGo0tXq<*TT#GqZ4RThEI)cilz%99R?OF})(<IXVRAgc91~oc*Axh$r75#Pg;V%I$Dn_#f~W%IlRM@=5HD^!9VtXM&*H&TpGjmLT64ocDHge1!9dKKBu){oHugBzgX^pKo`4NF(EpaigBZXY_rBa!At>diQ-OpR2LB-vK{CA65zNFkzzHx2t+@?7y6EiSl`s2J45T%aDH8Qk28$TBx@?51^lJfH>P_h5xgUp^w>tepjIb>TAhc?E7a3!#ReM_r#y0#Xs18kIIVpC(T7%7c%1aC;fEfducw)+ZTFwC*rKLAO3H)$G*H4iG1(B!2G;^DD+taFwV>f#eC=<gY|5iqiFwcmgAi8`|(IWbwB3GgPm|5<Dm<`d&z})-@N%9;#_wU@f^=7`^kFk3pkfl?3C!v%DF{1H(VB7cick0<2(?5g-wXJh=;5%wegK*AJ`ZeiQj9aNd?{6I)(21IW_c3MX>JQQ4Q;zSTF1wmV$0BtS-9VKC|d%7}mYovY}YdmMn^M1l1d&oxFR3_Wz<jKA%|y^L^XR62J3Gd1=Q+_BJ>-G%`@yyQ}6LJYTg7!Fcnawd|j{o{z(GZ~Soiy^NltKlU50h2VUd{r5OELy^7&bS*P<cft|qw%-Bi*^falJSBzhDtirjQV{m}UzWpu;7I7^iQ&-O{(#>dwD<$>^;eF-{dOCP^zEQ){=-E#T+sF3>*1Win8~6$b9&;ORNh&5FX9=3{p>>c9g`M#3GZo^pkEmagU}DYT!Ze}0_{l;$2fH73-pB}&^|ml-_=Wt_eOd&^d>{07ycgS`)$9gGL~<He!ML9HU7r$u(aR-DBpYd-IkX71b+7vbQXG0DfEN%`2Cl8gt|X;eKd3<_m8rFt*!bN?-w59_hn`s>bBpV8Gj{0_uh=(d8L1j_cQ)U&~3kK)0P#ELHy<5e+7OA=XzK~bo=k)jB@d!>tU;<-)h%$pQ_a|#jginEZr5@u#mOFuq?git@ZAf?5BfDRDWOb|Nhg#zCQn7KOL;>^S}P-;CCL@6l7Um%idb?{At-=G{xW06#tv}54pm(<Zt;M#S43=;l_F-p($RBRw$XSxPzv6VPX;TwU(9jv>wGhV2YRY1p1OItVaIY%DaS>?v(~pytrjqEbe7lHJai>h<@Y)$@5qiW7!F61Ihh}!^ns6dx}@K^1g26(}*~dTwyG^!YP)Ov3Nbpnpjqarg#I(>RQ&!G9O|Sav$<qmer)6+QeA$+T=mRk>t8%pRE`xdB7C^L{t0$P4SBwe$iT1wNIMjKU!ANvQC!$Kx|0fke@4FTlEXen$r|-MN_;bP4P;!3YL{8Rwi%B&w^=+Hz1ZLZ$R!#tW54pUX%AyllM@QdRbxx^0MSV5-X8cVw^wHbl#)R`}~1rqOe7>`)@&0ygyCx_QdAo3oTn=SpZG(UNptKTGou%fw+Ra1Nk`OR`PM=b7_k2v23kn-&l2@)dSd>ysBk+EXzhy{En4&zXrTXQ~V`SrFqF~#lNK~UXoaqyd-%wn&K@iTTX0EtV&*$akM68C2vi>oY<LsIr(2ICSrSHXY$Ux=k_$kGt(5`#<Edmq<B4IE#g}8TI2>%#bNMT@hD<8@@y>2DD6LG8b#aB@0DSGrHQr3OOuzQDeg}+$o<Ke5%-fXBTpdSB)`czOQ0#9n{}z`FE{J4BzbP~TEuGP)mUe>Xo~-mtX_YiDSnRl7x_7IZ%>%wIX(YVe~K&2;R(KiWwe!8ntUty9%4E2J>;>(zT^t`k;jt%PE-5^@gDgL@=PAUEFRzrE0bp;FHLMoUYh(zn&S0{d&&2*4C?V(@wUXA<ZW3VKM`|~E9~U~-p8`-9=KL$k}Et--j->{&=hwOdy%`y<B6xq<H_BYHL<L`nwKoB?g7ljYo+I+DPECSguEhoC1P&!O5}fgz!ZP%0aN^$2TbuV#3JO%6n{=EPp(kK`kbct5%MGap2FeeY8h6*vJy1KOVJdsODs%Ym%K4e@%l8yvl9!DXD81~EJU7{ya-M4lEnPvCCQJ_6u&}rkY6D$Zdoy6L861)!S56#79uaidoD;TK_3chkf*ZB^Rrb>o}MtpKUntKvLwsi(iDGB{6PMm+`|)=*|Ib=#k0{A&rVbP8=B%-h#uq$mCr21&*Ta-GL16DGZ52}EBqI^!t~^mtoz(x*>K{zWL$l=gE);`;RNy><OgYrA1BTrS9pv3IC&EDP<f3e{zg8Ud;xJUxw61yX#(kE5^)+akX&I8@@eD~XgwI0LMQnQ@>?{;*AQEiuOXjk*-GMUVr%l*<n3sRcOg2-oy@xnF_1iv_t}NEfIb$m9NH1*B=bLqc`7`bEQX_uQQ=wgu2wr)VA*{S@Z-FGV%bp3&J(+nE9_6MaDOsBh}Zkc_tDpJ`oBcnMpHbBrg$XrIC&)bW#U!xtBmh5P4Rog^W@uzmx$-d&ojPD#C_xnkC7|9O@4`7#dV6fiFlh_-Rm^^*hhYhxRv}E`EB9|^4sK_h&{-6S{82EH4UctZVPv6z}37~y5c*jUDjZV_q43BWv%FMCwVwOQ)w;|!^y*$<|45R`9<=cG{v3te_umdg%`*bULsefco*VTa%GA;=}Ymi{;%>rmRLN@vZFM`H<BOlz~@WI7ZG=nFCw2$Q+zgYGx==tNyMe(lgJI?GIE1_B5@UY7;z(U6?qA3JgwjfuJ9=JU5quFc$8e_HJ84Zk*^{yBwt1T)xW|Syk1B?gM1)O@nOWd<ip5E5touLWm$}(DL$E|cm#15`7XvDK~sD&P4NxHqvS_f78`i2csZKlHHbBn@e;gNSe?8kxk{t{=Tk<@vJ$hAH?hpevR^FQLaa*kAy?>4UX?sIF)Mji`piwtNv`tEWLaurTJnD}od+!&^=ynUH8BIZinBUnQJ9b1huoW%kFhBHj$C0b@?7+(crmM7E?Ail@K76X`1^*KhCH2R-&$6OsID_xmWteypQYh-I&x3?@#J+2i`2L5M^A8tjV)_v*%>SU(w?xY)S6n>JlW?BlcjG?-kiP^Z)2rNXIXuk;#G+MBCkSTil%rjn&OEXOmR0c9l0{a&uB2kBQ==fX_>YS`Dn|$c-@9PEzK+0cNPED!rv`SWmz0e@s-3h<SWTX)6&qF7rFAIOz|<qROHGO@2J5PZ>qr*|3dtoTs2A$%XZKdKTPx_KTICO@5S)DG1R}%zrvr1O8=SHiuWXXkSkMsFi|5{G4$oN!qmw=Q@Dtjn*3X<P3V>tAl4x-K>j^VaX+F??nhpm_$|4@@5ud#U;WhPXV<N~Z&(&ioJnq4cF3|&Vgz|8`BY*UxxyvnQ_1HON0HAbA4Ci%4`;rE7{fVUD-0r^Nv_gtVtl=cq2!^=yEjeoZp8WI-N;7}2a%5;|A`nxu5cu|!nWi;k&j?JD!+|1#Rm|(kq;p6LmWZghkPutEqM^{e<V%u^YlM}b#jP2g4l;Vf;@~kmOPAn32iLvVJ!0<MQh7CY0JFBiRa0~$yM9wZkfxn&NRiB(-hxKQ+zwQ!tul@<O<u6k0)<L>`vZ@T;(&}vRRf*CWeqtCSOled==B2;<dt)<RRp%m|o#&;z{z;<nhE)<frI2o;aO+I^&3^O{R~@%;PlgqYcZY4e#GY+)m!q8XIO>)|{sJc;X!L@#G;i#rqKh$@`J7A?_w$Lq35xmAnSgmpGNYqh*IY5LZ+3nY2U9Q{hSSIpl%Fb>xBMyNTDxeVJEXn&MlCyUBMm{T9a4iFqpALw<<-B=I2mN%D2X-^dl-Bwt7VH4laBi8sl&5WmK$xF2I^&ODp5ZuZc|Gtcp?r-QT*<{!d(`i;1T{5SHO#0lg#$=A~+Fb2P5b$G(EvzB$EDc+mbA(^gtJK_rRcI3a(6u(1!N`8m@1nnvF2(@gUWx+JXXA%9$XOaI*YeX%W*pS$WT%~Q0EPVrhrmzlqBl3o{I>}<F!?;4p=Mfu_H((y~crV?O-D5YFK{u9*;yJATS=6$AG{xsxc9*z|Sd@Ghc{EM&!!*Sg6LXL&{GNOlzjK$S_-*20^4sKb#Kq)`=_igjl)SJt_ouZiFYzA_aE0&473OCeWr`Q3DPD@EctM)td5G%!d3de(pS)IBkobwbkY%YY%SY766?&07EGuqVQQ{BeKk)lSiTTL$@w-K7Ui9H0&qSVy{uE{<e__Qn*0L+aA>_*b@WAIU$Uo8)PoycH!0!!C_T9n!><{t;n&JWE0ra789Qh5)?ppSM_=@}i`6J>R@(08lG{tWb-;gVONd7(B+)!E$w(G~1J+tfyP4VY6#Xk@~k}J#ZfzO{XU3y+CUGX1?Wr*3y73L@ZK%Yue=$-6yg$0P-<jTtN^ZevxXyusa59Ad*a9<A@`!n*7#P{S1b1?sp<leL#%u``Oa)lL>#Z!^_l_OXA{$csasOmw3DgI7_DV~$2`1dr$eTZerpK9>+nD~hNG5JH{JMxF*?};jp_q@)@`^dq(3lhI4FGyaI=tEwSyaKT-c?I(Fj57o8`w#Mrv<ys_foT<AYNc6i*#Vm3$1H2v#KY4&)&J{Xc>m{5?PqBz{-L-1n<<a)B>!ej%h$gT^R#S|Mx7tA#ve~P2y#Tdk=6bW@LeM*'

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
