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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_007.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_007.stl', 'source_sha256': '0a2820cf47c2dc715c56af370a8ec52ce478ebf69dfa436fecfd0c6438bdfb31', 'input_faces': 994, 'input_vertices': 585, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36183759570121765, -0.1801966279745102, 0.058039382100105286], [-0.09195354580879211, 0.06489130854606628, 0.45058006048202515]]}
GEOMETRY_BASE85 = 'c$}qO2b2^=wC&kt2}=~0BnU%XGAJ1Zh9Fr$6eI`?VL`I6hytQRM#73D$qp;a29o3?Fl13c5s6C}P!N!?5>)c<s=BYI>ur0^KmV_%&b#;4o9bKD)zvjU&9P03@C;Fg`YUQoY?tL`hZ=?<N;V_P7#=fpSl^y8u@wh>Fv4ZzlDhb#IIC5=H`{b{8N-cH(Y<0~dk&4R?T&uEcg^VX?&#iwhYlOseNeZ-Lwm&ty>a&eu`#9|`+oNiVoYATTFq+Z-BrqzcaL`eAO9jv3&9ShPwf(3e(#Z3PsA3FQe~`AO6u+^CBGEhmu>ht5d*O$wR}&Gd#O%(V3JGbd$yI3x~KEu<@WYT4^)4y9XAkHOzGRV%i|hb-c#+IC@OVd$zPV+kIQxIxX``v_Y$4*NvC|HMq$-XO56;oC&p=d;B=RnlAmlO^<eeF`Z$zHOLfu%12V{bch*8`JUiEzBlF+>P_^?`K{Y<Dt}oZxVLG)#dZ6LuL?=B6o!aqTETH^s-!#WQo|YcBb&+i6^W~cEUlh4m^4rrj-Tg`v?L3km^o~!`=1(c5dy+nr?HeU`srfS?zZ(DU_vLtcR#nh+_v6j8?Z+iO(BjfOC*3`+*?jwWl5VW%yx6Y$*5_00e9=LhKU}BzK)NR^HpwZUbjo)>%8T=o_J!<k!$eKz*9+IJd01cRo^zKb3+{bshNcJV)|n#pnjh==YwFLn&reJL^F4Kb-#n?tXHp(D&zH`dDt#>Ors+oV_<7oVI2xt$M@*a~kNYH1(><^5jkBL$OW(G3zBb>eovkYuJL$$phBiK2x6TXc1%GtThi;8$9{9;{f12#?_9nVsWUXKF1;aGmd+xZ@1J62ZI$tOK@wrtyMdwbpkF%vOtU230o}~L1R8iyHf2W?`BTgRIQ*FAY8~Mg)>jT$m9kBFK&66DSp;Nx^`U~p3)N3%&ejdHhy@Q8HKfa$6G~JUmn>G%l2PW>)?<19!ZuDs_=ZX7FrE{8oW6CV)Z+u=&_c!k3w~tR?crJClUu){u<}-B9Pie|$&xWdBJ8~*L=Wcmj&^kl9@%>Xd4+DkN_2SK-ba%6edG_{6_jUh#nOzSy&!P0YyXE!n{wJTN`+wRu%kH1_z=V<u?AK}F%j`-&cXhlrf1rDoBx~yx*J+-U9=KOD$tj<7>;70In;M6z#pU_(UpSiTqz9Yibj-KLKPIbM|NC`XB6;odnjUzvO}k%^?wONIyI=TMMymYs@6Xc40lH^T_NDUtjVY(;z8PKOo$}p%Hz++AtGAQ?&T^-GFLW9QuG2VJ$8G&?qEkNU|CMjet9w~g`<}(pr}4=&O%EL0FLmD=YW?xlMt*q9uk6<g>A?rH<^1%m+oA3|(0v`!671t_>9ta|@elYitK;UID39yOr>=L>y=mu^p3*?mJ!3Ly^V7<QPV>!bKi9q_r+m_RzI##i6m^|ERO|e~OlltPn7%-}uAzJGKTy|K?mU|A8?i#o&kj*~{%4ityz*Slt?9;{LGkwSB;8%$zB*qy%W8VCe%5bf`>`+R?N9M9vyZ3cr|`;U_VaGFvu?9GkI}K3?rpMHwKJ`gru$QmN<ElXUvDSjSG8WXE2I0b9hAD;l}pp<I;DBbb@y-4j=H}_eMj9m-qBI_3>xaF2lh;LZl~)qN1dM+s~ucl);N$)T&LDJ^q-pOl<$Gg^GUbX!yGs-56>jq=O^hjZ{4*YIO^W(Pc_}BH%pu6?sgf~JlT6O+1?J<sU6aT!=|S=<&#eN{)G`rU-X*3uVA{huYm4;@I{hSKIzuJ;&KM9zt%pD>A}v=)jBXZT%E^v|4g>$bDigVgJV*h@=2$B|E4fCZXeFn*MI2VyX*D&K>1q+>)#icZtY8<`_aBNf0%AvU+lO%pLCw@KhrtM$q(t=PvFL6ZGMvO8FxXOZ{DXatcSC;`NnmcKcpLMo^ze&ySJWp%qQKN&yAp8nyBp`NDqG7D9K58-~3y@UYO3?H`x8fYJbcJDNgN>PVEGy7;2moSLpMW>DIi3?%ni6J1<uL=6)$oy63?56sPt{r}m9*&rZtu`STua9Jo&YEq(E_6vuq%*1D1KRO-QAM>YSXdyX&B=he+8O8@DdWGCI%)2q)nrd#ue^vFyr9P^>`{J@gjE9}ShRDs@dl(r6#9)xb~hna4z|Iq3CCeJ7Rzw*-^7xS6>^yF+Wb$|RbP4`0g9lWRM{<)v3{7ttVb>I4M?YO?iJC%Oy&r~PfKQE*1e`*#r&-3f~q`R|b*7E7R^Y%&S?FTo+B|G^io%{D@+>z`w4y5yO3oQ6vn}^28$Ev^XaoY9Eb?f>fJ>QKK$9(9N?+ZLq$EELIv<^e}w5_7A=S+9!G0xfb;J`jgZ*(iwN$2g8?!6eHwL{OZg1-ByPC8vjmcDC_nkSdj9Cf39nBM-nb;?h|^;AcFbQUe&NIj&E`&922>DIo2bee}%uBAHZe0)eZN<}!glNPDz{tp@^JNY4<`=RxU_t(-{e?8MaN_HGi=zKiA%@!m(oiEb)`SQK!*Va|8^L+pL1bv@C^A`6nKAxnfn^)Kmr<>2v`Fy5*9Y3zG)4>!+|In><J`>L4(6##g1v=dyt?Rw-->Sbc$F=Xpq<iCTBxu())2-)<(A~pIX!~cb(>x(P*s<$!r}jzb?fb`mxZKI7uUp<Er+x)@L~H8?>Bdf_8}07u{la~Ow@>@Y;FOz=I<4DQ`!xq9Ir(=(PdA>2KX&vV!0!mw{)GAk-P)f}{@Y7cI}87E)O|<waR|PgsC|FoIzL~=wUsI#>kQY88j*T`6Mj<THuz4elTP<9Ydpg*IgStMd_2A7|8+cHw2t`$SDkg-Pr071ztDZjSvB3ayiT%HzerElFIp$r`86V1>-$os^YiYn&|6#Qxz5Kw@K66_$N2!A&j<IOA^Lrv>DGOp<_Y#8+&}5uKmR_(b)HY_dAjwAt<ToDVcp}`De3$=^-sT|#*M85r1N!ye^0T_JJ#WJe(wB|;?!T#d4G+S5A=N$)A{%tee<tyY#%yr-*>Q#w*L>Vd7!PUv~TA+?c2F-J^zR9TXQnesU6aJJEU9t{}=8$?hi@l`$MkN`68X~54q0U=leseeYQX3y7l~ubhba_I_+mHo$U|P>DVuk&i990r*+KI+5V90e0=!+FkL&?ACk`Zhg|1=`2H}R&ic#uhg|35$@hm`=jV&BC)PY<`#rAndBXQymQS`1<T{_Xd>?4#v;CX9!(Wd3TdrHrc}QpbNv>0Va7mid+4n)N)4F8o?E4_sDc^hLj=JvH_kGg&_kGg&_kGg&_kFI@eVKIreV^-ezaX7|-{(4g-?#j;@B3Wm?WcSG!*pw(Pvgd(4{)9Lmp>oiIv;2Le8BR<pF1(#y1vSz9sYa?db;OJOt+pFK~ML5iRu59&yUNWzga%n^D!g#w(`TC?~%@*?*+ErQscm$H*(#2UP?N9-pF<9`fYO4aUViDe_m?D{i&^2*1m%2*1iHdf4<6f>-p`kH`M-+J(nh(KbN-h*>h>GTjK+rKbN-JXV0a%Zq37jHyrn$T<7`xc|O;9K7XFib!$J?<GMP(?DrI|Ti<t}^WQtT&hz>29i;Q$JAz5q)N$GGL8SBFaky^n>!9=Bak&0p`TV&2_b;wn_Z@17{r<&u%J)?NLpzV8yP0l{^XRK;Ua{W?xo&-bgwB5-<T}sizi)Egnm^D3?DtKsThFy3uW0)X>-iFNKF_(%+u^^@2EY1Ewa?yv;5yAu(gW=GXs%oHgz45if$nC%M{}L$^WU|t_SyRwT<8ANtxFd!tMkR)Ga=o}-ZKfV3u^u1I)6WhbpC!0*R64Y&fm}B`hVr~<GT5KN)Iop`CmnU4~lgDJ{8yLxW=Rls=w_0F0Nba8+87D7uT)xwKP?&SEJUi)W#XQ=k}4+GXKdYN8K~Oj@FK+^0061?f5F4RXTeQko0u#0S-T-#(}-Z$aQOdAf3I($aU-egz(c!XYXfvo1aqWYq<V?De3(EQcGv=mvY_uoxSi0?YP!+Z>C%C-NpQ>#)rL!%ypj6-$UlQ<)_v!YTmN<w7t*+>^<$kfuB`Ad;gs4G|r?4*n8$&xAHF?(Z_+#7t^U7Z^Iwdb<N)M=el*iNN4Z)bKT1CdQgoU|Mv*c`M*bSCme7*zg)Mj)4*QmdHDJcHJ$@|taQ@px(l9N>8!idd&{KzHZRhyM^F5d-Lk)*KG-kodlcUyeWm><b)(BcrLXpHmU_|;QV*P|y+_v9T(d!*m(LQU?kOE9^}v+J>*TyjT&nccUMhCFD0NTX;i{dD7ghVEugc?k_P?X_L)mx9{JUq?%HytVEOp<A@+vN_BX$34Zq@G9M+aoQ_NDBff22$4M{mjYJu&5^?yVaekiP#orQ(5gYvgfH4v;*!I@dwj{<8yWJv-7;>h6g*RXb7dNT1&D98&j=9HEZ;{Yk02$MlrG17{PGWgH&2Nsjlff=aL7Tjg(FAjd6`BTDH5FUa<d!*6Ys?ZiFbDS6xW`(*vZPi1~^+DWPV_Oy(b?JPaNQC%O$ls=`e%Fnq@>fR~ir5-#xSsgb+J?SU-PbH;iKekuum1oNF^gcMhLva7lu`=J+;Ng0^9(*ZsyVNsXRpWNzwA8)6d7I^NJ8n_)tK>1M8>KEtKgRwp^0>ZzyQS{C@HjzTPnl)=?r&x(y_`Q$=@sOB^RDe6b<a$%Y{!@JOXa^!Gv%}6n^N~w>?7MTW|UR!_$IHG$BiB$=Ud=nG1bo47IJ?2@;_fC+gY7a`R~0~o=;!<%~E&w$@rb@&xp3_xQ~m-@$|L7vt7-rn5|Mjv{B8g>NnK5Jgh6nGqCwXsrw?1O5Ip|OU;K$Go;Vpo!nA)e;>O+wpVGR?5}T1w{0?SZC!PJ^%^P1+1S=r>i#Z=RQrWTsPl5Ikks9|V-MKdaVO=Lx^b|%Y~L5$spiSBWzu)><*Vwt+xDW&HyTZry1UR^H6O;h)Vz&<L+bu^&9=znUd|<TkE^`W&!?*E;*+XszEwP;^5Wl8*WaQjIj@YCKB;>O4pQTv`=Zo?+eb^?w<A`~ml^w%pQ+uY9*oYS{FH1g=f7`3Yo(v~T^=`Z`j)yLPiK<4``R9P-aHrQC_h)ek@M1h>yXMXyhM$2qbX81M&?o1-_&9o>$TDTRo;<)Gc)C{WEi4kF`|s#-EIFQPl)1=qVqq=>s$4I^-uC@)vEgc{U><~O%Gq1Wj<n@4NnIbaR_j-Syn<5ai$G#1s8FV4etUMaf1!-0T*$b4etaOalH+10T*$h4X*%S0pEm^!IR-p;C*H}0PO&L6TSp~3BCn>4txoC7r4NgU5bmi#|YtP=*Kho7B~p}40sFpe&8VR3h@2#x&kp7xT4v9WtY-KJYa-yb#M_c86jL7T*T)_2)_<4VrCnz1zrn%AzTey#GnzvmB2;ZZ-j6~@QUy&@N5%LMBPO6h44q<AE7UVW5Hw57s3O<2cj>8hk_4<Z^FaDhodiqCxA~tUkJ|zpAC-!uQy8yv=sOz{5AO3@J)C=_<Z;#JQsW}d=s7rJ`cVHUIIK1csO`6@Dkt&;K}eh0dY3)Au&gw9e{7b-+_Mz--Hvu6X2WhBJf4<O?VmjGWaFD9eg|d65bEKAHE460zU+g0-rL=kI;UEZ^FC4cfmK|mEbGkoA7e*<?u~-1^5d1CL90{z&GI^z<+>m!l%Gb!K1*3&GJ38@8O&9PVk-ZO*jcW3BCz0244){gcHFN;hXRd@E!0?_#pT}_$GW9{4hKUyumE1p{<5*!b`!I!Z+cC;0xiK@K@kp!8hRr;0xfJupitH--K6zuYzyF8^AZfqrh{_G9B7<_$E98d<1+G{t)~__$E9Ad<c9K9tJ)Pz6Jgmco?uBd>Zh_z^lNg!Rso-4ZzLJ(iB=#_$J&KyfJ(eZUo*4z6mz~Zvfwf8-h24U&3#IzX895n}9cgZ^F&Mo57>Nhs=Ax_lD9$Z0ZW(-@rv|><Zyb=tm~_CY%L43w#sK2%ZtX312o87x4{O2p<F&v56~$4}l+oUx8Ch{4MIfMPCT-0N;VW2)rA32XH3zN#MQUB4%-gZ~$DyjII#=4qU{`HoOLW4f;Yj1v~{F1)d@9!O&*IH{m7VOW>FAX7J7MO?W%_cJzhtCh$$@3*p7!i_sUtv%qJ;H{luJGvHBRu@C(M+86LmcmenV_$Is>d^LO%-Uz-Cz6q}aUj^TU=Y!9OZ^Cilaqvxe2>1|q6gY!fG8^ho#Bdva0bIl!Hv9^>h$U^f0l0`YY`8MGh$U<|7r2PoZ8#ISh+#II0Xzdd3Y^a@ZfI`!CR_)+4tx`C3*HvK33mkV2;YR?0)Gp>3BL~hI(!o@0$v2Z3FiaP2af{xHOnAqgW#L+T=2Q@O*kGr9=-{$1z!u_gqMOZg>S-hz~{iXzypEj02cut2(LvD^8rVi*L*gY(nK6&gm4aU5$75qoC{pUcq4>g02gts5yCmaMO<oxaCUGJ=NKWJ6<oxDMhHiON5Zebr%ikmbw|+`!h68?pf7~K1^*U(Asi1LkG>FI1HJ}*A-o%WH~K>O2>227h45+c)9@(pGqXH~_87hir-7%zH{q+`SK*uRS@5&)P527<75FB62mB6v6Mh8#2)+qF1AhjO0!Nw`ai%b(iTKzR!Y*(T(_A6^0R4CX--K_0--2(#_rdSOH({}WTtU3!3gL|4B0h43a3pvn{0f}I#Mx1o9ep930XzfxLii#2@esZV-vhq~--Q1K{};XqM}#RZqG7|?z_Xz*gmZxBfJcF|nk5UgEbvV@96TJp3IF3#T*QYqd>i~Wd=vf~{BQUs92Tayh!HlN89Xz56V3{r6&?kCZhq#eOKBoz2@B!7;39^Hh43|S5&yB_OW>E_oA4jtf5124zrg>3Z^BQ&MHIdXKL>vfzXG2z@k!L3L|+K+1K)?f5MBqq4t*i~4fr?kO?WN%TKFcs7kn>#6Fvcc0(~KT2K)>>3LI^gQqW4lH(@up8@>tW2hR`Rg!6#sfp5YEzze`P;UeHg;G1ws@RIONI2t?}9tG}aULGG9N)xe^D}?8Pi|BTRa1ywP`CTEr4qU`Mt`JTH7qNgVguen8v4|^#2ZM`P(iOt}!27|k!1+yF40XlO7sB<x>!B}%-vNIIeIeWlyc7CD_-*jF(HFvX!Rw+ggo}a~MPCT#2hR_W0!N7ZF|<hdCY&2QH+&PW0$v5a2{#092;YQX1%DO33BL&bB776h0-goF2}giOz@xz8FC1Dpd=t(Ao&&xKmjo{f--K&`*MM)rCBRF-H{tBy+2NaT7<d?b6E?sNcoevpIfpu%r5s{+8}@;VIM#-{fQ#t0;S%5?mbKx(48=vfZ^I|SMLcc8cfdt_V8g=e1H^K``OMhPrL=bNP54vrPvM(zNAQmDO}H?4VfZF|%TQdzzijwd@L%DZ@OAL(@J(2Fy@OZ`_(e0ebt$bad=nl8J_^1CeiwKYa7S=~3xXGfZ^C~Xii>y)_!zLzj=}dW;H%(Q;hV7VdL1zzaBefUaVf10d=nlCJ`#QjzXSdbd=q{N{3ZA%e9ch&8vGLe8T@DXCj2}2@9<4nc)g1FB5;%$-*PGKE%+w<3HT@QO}IUHd-x_?2)qz{6TV?6F5)#C{ssIO_$GV>{0e*%7G8fx%nh8^jBmS?_BMPAJR10I;7`B>?f~8az6rk!{xW<MzG)~f;td-<4t^ZI3I7592YeG2UaufV0T(r6CzsMX!7t&@z(0d;!ta5<2j7H?gBOQy!fA%$BHpy&6W}M{oA7P$+we_Tc>M!0FK}ryc6BMOD|{0k13m`633mhU2H%9sfR}-9!uJftMNG5dQ{boIoA6!myYNj|c)g8S6!;Z0_Hrq$7km>Q2R;tI3HJc+0pEnngO`VI!haizi+In5&w!tSZ^HkA{|n!Qh1a`?rGe|1vA;`c{o$MNB=AY_O}ICBZ}=u$1-uG;6MkeUF5=%doC=-_--KN*#YOzr2;n;5b>LCpdS)Dix<T+Q@aMpTfG2?q{66^m@J+Y|cn$a_{KQaP#78!K9{fCf3mooJ_&l%+T;O`(_25z955VgK4+0l>D)?0RCfpCaAAA#j4g59uCTxHk@J;xlq4-7kB^=>WT*Po2t`A-x9tHN8WiYhC@J)CM_!Rgi+!wqrd=st-UK73vKQ$B=(Qt+E1@H^-O*jMkCSrsQd%!*LC~#e~41hKOz6nnTpA6rG`+)a>Z^Bi<tHL+o$A;n}KDFU<;OEd6!eQu#h#73SE_hvd6!=xM#6XLIZ^Glj$HO<_p5Q&<n{Wm23h+(%A472wAKUO*@U!qu_#ya1_$Dm8hQV`PV6hMF4y`+U6CMjb7QP94!M*TJxGZ>C_$Dm&#T5|$vEkF;r{SCM1Mmm%O;~t+i1;dSXS1|0ODn|Mz^#C5A(pe@0^lO%0T!PvgZeV46S$3-FJ|!|Rsi+@mq#pa!>zzu;h4qo+0Ll%jJgV_7soG%SO~Zva8AURZ8$Huh=qa6p)Z9H^8%O0@k=3Q1ug{~jp(xBg5U*lOcy>|3-z^7mlgHm_)&-zfun#+Beu5TO5h?k2YwlSsfbt!I2y+<i<l9(EO1rCY&IMP9))9O!)J4%J}2tv^P;{H;!D7dfZs%X!-kuIi`WM^8;<o7Vl&{@z@>qQf;R*1gBWYW9l%8#2HYBBH59Rf4L1cB@jc)Uz{3zfwBe7yMf@08e0Bip2cVAdXmAlf1^x*5W5myFcnr9RK49_Lv8W%5x=(SgtKoc$SRJ?$aC5|_HryM$H~cllXS<@lE9wZ30vGWU;NHLk5J%haIPh`sIvSrHkNWYb6Ifhp^$m5siTE0DUf{xr)oeHhJO=)%;j{fw-yd~^M}Uhs5;z99E8-{{o&Y`pUPs}x6Hz}AbpngEu8E=6I}sZL7XZ$KSl@<+gAa$l`uJ=Y)OSH0;g;Ycz7IScxIf|u8=eF{30_Cwvy)Lj8Fd2BG%xI}X896v3-BznY;&plZK$K%Uyvu_ufQVbIO>n1j&d&|Ps9trA}5IYAnGXhcjSrq8?eZ^jQY!{qulez6Y(6d$Vo+gD(WcrXXJ_a6R^lRhWcZuqukBN6LAx;$k~Ycji{sC8ORgy3t*8Ghx$0wQEm(5iP#)i<g`S6OVm;BVMFDK_#?2$`N2^2A|5tExyz6z;y1t|=WFDBjXKKpAy355fxpJQS%&Dd<#tD&h+bfk(+&0AP)E7#ktbq1V3G4K>fc2j<@Q9Lh&_NsPA}B=LLKE!L!O9Jfkn;~)K5Vj<t|5_hzY<V$B%kH>L~Xp@<coWEOLHA{ZFW)+*U4?C*qqnJQI8-t~r5Q<JxP5I1^a3De8_QwgSFx#v5kI8Kz>cFokcL_)oLs4pZ@kFoi|VP2}A~eJ<o&N8WX`_X2WmpsgFo5x9a`SHmo?nB{e|)HF*yv$)Mt#4N?lQqC;Z%u?1Ywail8EU%iS0eF40R5D8`vy?YWL9-MxOJTD_ndL>Z<TuMpW+`Bnm(5ZIpB3%oF-tzP<TXnjv%F!JCT3}DmWF0&YL?ef=P^rBvs5%oNwbtNOKG!IMyYL<s%D8cOBu5iGfQ3Qjm*-fg)1y7{J;KJH=#fAEZNZh$2a_w`s?`iPtG;lvR=+_(;`CbuZ%GBKk>rOb#ccv{s)Ymf%g'

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
