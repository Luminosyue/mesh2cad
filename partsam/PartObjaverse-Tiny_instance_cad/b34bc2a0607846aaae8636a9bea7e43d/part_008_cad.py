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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_008.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_008.stl', 'source_sha256': 'd5b791e7f157506825a97985164b3c2a1548ea4d75ea04b60092e3c56b6d700f', 'input_faces': 760, 'input_vertices': 455, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1366264820098877, -0.26239803433418274, -0.12955571711063385], [0.15301024913787842, 0.3660246729850769, 0.1320146918296814]]}
GEOMETRY_BASE85 = 'c$}r22T&AQ`0aa?HL)g)7{?qiiveR}&T&nsI0noC0WqM^1{4FXVpi0_oKZnh6loN7F}vnG>Y8&{^Xi}bo#VQ`davr$dv1Moesj2UyZh#QdurRYOzV_W!@nY$Q|-x5O1o*AieI&yTA+_#z@WZ9{uPG%j<smn#8>~m>%2CdTDR+F(E_!gQvH1V`}&otWi3^wf6Y?mtfl&o@C)$kJ-pWlzkWW-Z_<0HzfY>~Kd`s2PwMB=?$xT5vsNur&N{*R|M)MHx`$8WlM<B{ycH#yRMDuPDthp6_#YO^XRS^AV5R0wH}MUp61$X|7ouk<-*}J(>Ft>}N%~XsJImi!jyJ_`KXH|OZ(H`+^11kM_}QH7O0Dt9E9(E(KeIJZK5t$(Px7he4gW*SP`QtLC70I!uRrf@oTPtvVT^np-wgi4Q@F3DGv`VAww1*<9+%pM=e{&qsouK?{N|5h<bF=Pi;{BCvLT;ILpMnNTe>fn`^m1se|J}&*9@AlK+;c2Iw1b#&%2R6+w#Q!_{O(pNm5=Z389kDj5SC<zs4TPXWSoiB%ifWNbhw9_dh>rm{P~qDM+8GviR2MOl##j!@DHNb)H3~$lo8Md~Crf`z4>5DW>G>d_&6Hh}tN=Hh6&Ck7=zJCc3dEecvN;pN;QGed*PF_R0NT+kyP=oF5?9t=CL^?Q0J4&D{M^PR9$tFCD*HG{fUHa@}*^;^nh;x2Ih1aFO-uv)%0~{QHL^MMq8AB7b)^;n#GXF8MxfB;{?(HeGxpv7gkVet4*~FMH?a@Qdx;Df;x|w)+3^HJ8gMuX}?xO8S`%;h(#ISo~gAxnF&LN#-*Z<*=%Euv|AT9nv?cxLNM+#OL**2R!$Rf1}-T$;U56+O1>wyFKFX^V%i8Q|x9br@0r!*DuCOJ?aG=E98EToPnP;@{DNPMs~UG=@{hGDV?+vZR{R-4#%a1;u{%yp*`04x?Soywhz+R9kW)hcjBRxhiz3e_~x44(teIuV#S~KK2H3|57NFJQLE8@=Uj!~b;R#d4jX33b2yUE!ylPzw|xIy^bX0-c>(+*qgPA%8CIzuV`qQyjj@X)oj&He^jEvR75s5Y$K-nZo5=mzHdaJF$89Lj6Pk=a_75fD$NEeAu>Lh9R_^Eiukdp&OO*QP@_ws)E`L()&*)N2+PPL@l-!p!e~kFnBFCki&5&}F<$J{z!ml!3d?O|f^_-!x_*(ijay_kWefg|sFOB>+y^?w~4fpNh4@v`n!O_!F4p|Q`LjSpfapzlz)T3UjMU4FYul*>eo<524{24m!mFrfGMf=Xy75#2K#vg550Ma)|^N0L>MC49+F6#=ZPh<C?Wchw#cDWy0<$mI8dkY+p>*nx|!~J%LKgCtrxn8BAjC)4z9PqDI#r@A{gnsJuF$U$?TFTSfy@Fg<EBsD;tx~K!r)`wyzMuTPXC)sk(zmIUZ|3Xpjh8asIf6>Z%ilwKA^$v8q@8H}NAH*W>h6a0tF}tL+a_g|^076~F1|i45asi_uGG72ajdj=^Wo*Qa{s4WEtC5%unvB3jiYj%QP1SMw)|gly#_B2Nx6BBL_d6SAAX&lsITeo&~AGl5Z`DxIz{fgSYf0azYl()Su##rZGR<5{?8-e*R3e!>?oIihv@oXd@uV+Y5(T19x@NwlS(1IcQD%F>yLA#U#5SE_Vr@jY5AN~1MTtMN%76a;qtuZ$}}>*8DF=<pLSh*E&isjTyGoNg_f^?)T2JiA^qKaadVsaS4W?d^e^kmxTM|hD8BJ&&L84m9V6qN-eofSS%KgqqC<yB|I=nofdB3^o@;&%8JBG7Yr_A0=%l3c$|d#T@GS>FZ-_jvcGqQ-<Ui^47Ww?4*E;zem?-sP_dWoBalx_TzfF<*vCZ2fzLDZ8?algSw9JEgp3dUy?un=5d;d(5c4d0pk?~mj`Uw5ZvKZsh@ayo4Us)j6>!Blkiw*Dxu9SAG-Kr+-+*&F?e52@1nMbTH=P=&S9f<V1Tgf=C)x|t#tf~OtyR4M6d1{b6uMzWB)NC~t<=?cz1Sy{qC-C<cl~A8&2S~fJPv{`NR>+ib%DS+Gv}cFws}16Bz9#L=41Fx~vCS<`eB;45j8}10Wt_4PoR9RycAl4fR_R!m6)A`G$tO=pIl2v%``6DpWIWJ%E|C6Uw9bX`>drdxjp`n<9<k;>A>)nxXeXpMf5kX3O_zDu`uMigtLcB_jO4%MIp*!aKJdLpO1ss+x-63P6+f*-yY@!ADtjK||LnfvYtwu%?xg)2>z?Y>#MiAMCndkN!(<&~y-*DE;x%u1UM;bu)QA24BUz{DD>jR7l*jte2x=|9mTj(l-#nd3#sj0(eXMI|%$IT45x7&vO?#zhSWowEi02AzAmy+7Jb>S9^#!?)qXp!%)#Hq)xjpVM`e#YGj&U)!`1-9r=)dRY$@r%|ypDBT@wNvg|7BmW{wonLzPYN)pYr|Fb7Xw9@2Dldmd7IP$_RZU>tX954f%LaI3@ja&3&1V^bO%F#rG{Q?b%)<E$Vs1GOTAew3PcdBNNf?BT9*{)n9l4{o-Mmlt+&<G9MVhr*Z#Y=dh0K>kNPUHmtAW{+995=6qwJ<Wp`Z>hnfc>5q0V1OC8uK~i3~oMjxa=Ey6)e&(q>um1R{tPlV7BSYnR^<QpbUGL^9{n;#A4)yNw1pT<~t@)CFjvX?t8u{HZ-+cG8WRUT}e)rw3pZsy@<vO<bZt*|m^Uo}q7xes@WL&lX9SGmJKTFE(PcP{&MoKUE5Bpve|Lrxjk4f+6;dwtUmwdKlmhsJc`9cKRNAGC)d}@TWcU!I)@pX^$C*=OG-9tMs_*~`<t?1^BlFyUw*k@FV#6GNgtc=Ur*sNIBj*1PJ?`MpW^`!mtYOE&;Och^?%7*)_avbZ}@LjV+OLP`rTN;Xd2TY$KI?P#~UoYe(?MJ`7XS(>;vq=BccOR5-)!xBhe6!_esYfl%N9-TkoSQ1@x?TFa9)4BUNA^6G;Wy5S@hYI8JfFGc=@dM_Km1x(q#hmV(@8%z@8v+hdwoRqtu`%alB9n<OXeec;}SA%+xr)uDEUuGl6um5XOa6cJY2_#zb~)MbN1@pu}*$7X1MsDM_^rHseyILABzTv|N1$~=UaanFSJG7d&vFtN=_DCP({W`BU@lM`TN($82<~bLOB?dZyb>O_#n?^_KaI6f7iyQmG32aVjs823H!I>%RF#j?$WP~4IQLD^*)Kc#9y@<_tTp5mh%#ur0ela)<1f_K2i>5jl+E;U5~qxUUzMY_V>9)KS_T-OvX2JqL+-rdZ~W>CB2I-<!oO)R?5MAA2m$UeYhaLe)`NrsfW5=QzRen0oZ>PdM)>FPIH+m{<r;j-k>;XpSGj*r^)x*MPOX*6M=nCnUCUYT~jbWgmB-LewgfQwNEaxZZXD=mix52PZ3}Lv!bjAtj|u!ddoI@C(=)GlXjt{`wRW9epcCk8kW5n_ht>k{^p4>Q$El6it+8ubQwRbBaVo#?Fz+wV0kLzm_Dw(^ndNI&C>5}9W!EGaV7+QjVZ?^-KI!sUyf^;!o|<FO7gRw%rE`ju{RjL@98D-99=F+`Pfs^;{0G~y-V`<pcH9uHt(z$=bRQ}opm;ctRKwD9RD8MHlUoj4nN*;t~_7)d#K0m30OCGD;^=~77s=H`F;9O`TL~`GM{KOev^4!n|%`Pw(uhH_3H(to@}<Q*e`bSm@mHLtK?(+7A@--`-mChn~$pD{=az3cx}|FDd#K3YIm%+dmfkh&K%HIeC@+ssaIRsYSLeI6X!989wYT)ZMHzJZ;g&a`d=nt9p=|T`kgJxQ`Q$+eTVEft+iH2J=*t0h;Mw!EB(>#JX7{N`sc*Oa-YWsqdj!0iv9nLIZIH^`((T`KPE_fwl2tzb?B(p7(eSZmUX_hz>Z~-eouhZhjzsi`;2AI@^^#lYWvaln19R%I43irWSq3$XeG~O=FTnaOXJMSL(+bnw@Lf4W~mB)=X9*!X3mg#R$ta#e0@`oizuJ<(*DheF<7UL`zX(AJ6ICy$B8?U&!@Af_sH0OD!n7iHTYXCSg$PIkbwKFfqkS|9qYYP*QMOdr)_Yqmb;JCuestMX`hZRPmq4<O<B*_YIebS-n|^F{@bq|>_=ArI`ChPka69<3g;=Q6Bc}*iju#cc0cw()zeFV)jl_t{^)RjjQ#ndyzuSwu+HE3K-$0Ar;zyiXm7N`Zsl<<@}ddSYoleHaAf!g`_Kn{;SYR^_R=s(+Jil6HS)>y67x>ZOmhFWnCxpLea#5zk7nQ_>>~o*#n=1oK)*;jBmKv*WFXSNd?Vw&KF|f%of|5?@nk&KIr+MCe)PvV*YeI%{<>>=@f~-@h_Cw{ka1Nn&`SENzBL%>?bu(Zj!#$*_(s9!yr8X}Chf<pk}SUAjq?gUYdp?_zmCMb^ztj_g=RT%KHxST{`PY??>JgY+PSrh9sZeHvTo5neU|ycHW~AqvEexO%jL&l9Tj~F>5Yfj??t*wzj2)3B<FB?&1kewzv0*?+qa8vyi0RT>ig+Lw9{@c;m2l2{cayG^SwQJ7S1mnGq7%1IS>1$+o7_)FoyR>`r|p}oY2-_k@(u0OgN|bRmb_j=Zi@HwI0@)dHPDf(2ib*pZ}ngkCBoU_4PO#&dry5$Uei7+zsp1hV|j={)Rly>6&Q2Z<pcRxlm)Y^Bh-YpQb<E1HayG*+*Ct{9=FdUk{b^MuYK7rM~W7K>n|@V%>G4nDlq+wrlVwOg$>;+jNrqG#fpD-!%y9-sFm?m$e_@Pc4M?R(M~TFRaURZAN{K$NAdcc34*w=??$8zl@`fH3g;pSO*;v-{|q~pyZRm8~ev^r;xs&C;E${H1;D0Um<<xzOp_vrffp~L6y;tT`EaCHB*M;oTU0l_>%)AUu}~g)=M1*Z<Wu@LU8Up4(E4{ok8%6f0p%?-O?M+J8A{|xmnR4T35$8&Z!gP8>6;j-`aT&_BBiXMEckV=-00{$$5&sql@%EBg_Ns>Uj=XPwS(bU>;qTfd2Cq>k9kn0Hj|sSK7Z(yQB0Ydtnp)m*=R*UF)Nz9_Q7MM!vVPj@rHh{krN!_@6pp{~G@s`{BPoh;L-NhJD=E#WJ3njniPCaM?LP(mSokettd9b+mQcr2Osoe!+TdZ+ZA(@0UpW_oJnr^eI*0k7|Ja6?z-v@HbEReD7n7IgI^E_8#IJ*T3LAEKdgMALibP@F#qh`9gDQj`cv>aOAV+3+7u_AB_LUm%*R3O3K~3)O#z+V+H)7Ce}Sp8+QKW8#85JV5EPG_EY>A&euoHly#b|dS$HhUz|qzITxh7^uFn39I=I7gTG}q_T!@i<US1-C+TO}v%RwJHP_=@-TFWmU%&nZ`-1RCvd_~ew8A_*=9HW>SaZ&m`TbwN%0BGt&ptspr-?xRk$!m23dOL_udosR&E07C9}nRCA?FtH4Mzg{-TFl`zgYL5MfykmplzCC{(1Ni=^Hppd$R6Ddovfm!u=;##5yNWYrJ15nGfwa>6?t#`lbY&KTmUmAMb<tG4RmOev1_J7mup){>6SN5bLkLRk0uGbpq!?VIkrh4?9VHSzpw_db49F{6Tf`-YxkQ&Rsnd;cvBJpH*Q$_IJ6zz;_#j^YA>*(tqt+(#N2`&%-(Cm}_#LXzSk;zFU1MFGtOpG9NpBn+QKk8LU^M596Hb%R2Z8Z*l*3isGDWYc%{y&KL(qG?Viey-`;Ao{_hTv<H3YWI2yDYnKz>tauyq9oPAeysgkqgT2Ie)bqu-^tBDrx416#s|CBDKBK!J|2~_fA6Y$SV;%Lce@yDdVdlg8hIIkRKiU`Tit)8^PB0VuDn0Nx?x*D9k&?cSfqaS-#(HDy0PLqG&qqG5e38D^G3?*2AB6AyNZwx<)$l&cm~|ZaUwDgoJfy$O14hwHc&?yKa-YWO%2;2nxQBe)-DI3M%Y{k5|L*Ia`_Zm4w#B(;KJ;&W)g823qnpf+c3TF_C(T#FH{YNi`4z?aZo)0xfBbFP7hAjH{6HHxMAjKv=uH_9>?=Hw&y`&`C#-Nq#v5zB@!}g1!_iKvZpZuG>d%nRwH-LmyS4%6I1?;<FL!4k+Ut|~|Md+^d0FRcRnTtCrs<LX!zx*CX!Y*m{Ze_HOKFt`$@^A)SMkXD|MAVqhp=v`fpxO&rVD&aX6zSAj=(u>Kq2JA_qq15cVs@d6=(#%VmQiYPneuX*d}yBKI6l%Z*pq0Q2ySxEAD^y30b!pJHE`6>n0CE`o&$)U!u$7eBWyn@^>pB<D*vd^h){r#mUI$)l$@N++4gj**6vGlc&jk%Ls0S_54o0=Pc?e`xrC(biBv!o`QU$)8TxwRXeOV=j6e<quEyJFLu6Pb4+u`er0oGoHG=yBkk5)(gx>V8JnSfj>Y+~Eu=m6hdaySxg39CJ<tOC9wT>Jw12*jv(6oYe1^`%x?(wgH(>V+Kt78n;(7B0PLuX>DFpXp%_if&et$XMe}#o1|Mkw&k4zUk=I4&Hk^jyosF&Nzq(9o679pQ&F4)iCcgOD~PDjFDI1TFsy|$bS*gnS~e~<H0UXIzW(*CWbk0bq6w13m1jf}I7+c-zpHigM}r^UPvknfi+3}36*Ui>{4Ikz$&bALQ!E6$Ok%1Ar3H}r)+)D7)z;P5)=Z$Zc>OGmV;oqKWaR688$Kl@@{&b3eGL)(BgNFU%X=dRk&Yn`NDUp)=K?^~>kUU*?0n(hI7o^u*|p5Q(H*{AStdE$QjyUDuFp4Wo&#GIwz*J&i<w)sz5_*q&=IoWm`lJgz?FPsyb5p6I}y(=j5t-~CL^y@!j{gD0?-t+Fkysf>pW4(DK#80mK*EXCtZ}*V%4ZT5WsW(S-EYff7DEXQtI^y>{3*wMIx+%tOe^d6cHd_MxfVS8dG+H42&R*1ke9jb+^9Sw30)M&gxra#K*%jxp51U|q|Mm^%G$E5@KGLs_m3h+^&hw`n8_^E?PQrV~V(#J_P3}uR4oeKqSq3+Qf9xREw~hATy)}LP<2UrXPHE-5*y!zp{Kq%Pxz@gt(th;fVMyO?5ZYD2n^F$;l?&l-OhLW>IlilWKCu<~WNV9av<lf}9p%_?68?^G>@Nm%mVRVZe+NHTWsEnw!a}4REMMSfnuhB(nv3^PIdbp&>AJVO&XM%{?}~3^j+J$ee)EXbv!lZc_`@QkJgsN<$@!hx59f=<-Y*!>wI^sNo@K<>W>&?%>4GNh-MHkAee8~5xNebqeWcuajDyejKKd2Br_?WpA)j~MC4XDXl{oJWn~U^)W+MILySV>KaY+Andz^QT%_sHZID+>8X3*cL$8sy>T-X}%2hz`W#d|L6GU+ehePd-u)bC9EKEaXs64G17v7gqIab6$s5dN(_*e{%FEaQN=raJCp?LHZoQWtQg<vy2n#5(n8LGcZ*^Rn*!*Z+RLy=D&H&lP!wb`Vq;&l{X1`xNV+f5U%X4fnG?ROVZAd0U+K*H|m_wLM}o_A5b$&~D0Sz<u7se$dud!+Z6|=j8o@y_K8Ho5sSN;u~?EG7ji%)8Kbj;gyko!7ZGtA1^jq)aw>}-$i&Y@ct6ctLFLQ_hAc5W1aBH59hO4L$HqdyO88##GjCQ)N3!qIm(+8*l$|#`#|mK3Z%d9kMoV${5{0gZFq0mzMsrrcE8*>Z}g3ae<CCNwU_ZbqispZr@>nM-e7!B$zOl^2mHXNm<Km@lXjxj9f;reG{pYbd^1PZ)y6Yl_?-&kJ^PtEvK}zbEysRf@g*6@^a1tceVhI~8R^@8#qW^{)Ne0;-+K(dlUQ~G`47YT+~}PT^%VOC_v8CUuB(L>M|({ui}_{1DOt~$D@TcM^t+FB+NYFua@|bxk<Y*~xNe`0IQNc^L_WiA@%I~e|Ejg$0KeIDoU`%wIog95<ddcX(!1gPwORfT`2ByCdN&j6NqT+bMfmfg#Mibg7?Ox~!uIzN>-@Ox$iMGXT=%^P+DVt+<@Xm_aNR>_A9-=kyoK*~D>T8mVY4ep?|WC)A!hJg_{J^luic~YyQWJE;QJ-Wb<KU%mnOFR=~uP^)jl<~7Ef()sgY63srB#upP$$&Q<@|7fBzHPLGJ%oKe4S*z0&{hPi(y`sY7gP457{<4<Y+gr<0YAC3m9^q>d$fQ^!%qlE?D<<EV4VGg8AZHKtNWljl&!QAd+|P<^PQ$)ovwABN&C)PCeHWKV|T&Z)6CH4dc4eum;?>Opcc`3Th{Cs7YmP4Z!Kyefy(x}KjJOBjm(U??^<_0tDUE0h`?sJ+M?$RnwN<dNjAR2#V~IX|@+IX~Hnnvv{8zN0}OXkZnJ_ft*se)8|s`Q+cpeW(M;eaMYdqo^9PQlkpB9Jva)DYY@VF~8fCp?DZ|33(WK6+`hE>L27Y<PQwRFQ_Kj<a54YD9+CEQ00=Hp|~8i7`YsI7}Z7|Mh>P1l7q>EsJ+O8$YrR7$YsdR48^}t^N@cbe@VUH&l)rrKPx{MLved*2XcF|FLfl@m)wckmE4K!O3hDpC8wb}k<*YJ8dS9{2Saf@bw4?t98Ue698T^{?L+QOZb)rRZb){cmLt27^HU3u^OJvJC{9l;N={GCoEq7vrKm;8rO36YRmio-t*A}OP1%lHF%*xct|E^nZ)PaIMm<BmM*h_T{XlMFfx1(b@6OMPt<)Ff7i{}hhT@vka^#xiAnGu35czj%F!^`#80sMM7;+728FCGBKB_Z06ZM@2btbD&{Dk@oS%u=eRMj8uG8Es?e)O3e48_+|;}$io1^St+LU94A>Q@CAin~+Wle?1xsJ`R?a!+a}a!+z$sw=rLIXyKEIX(HF237s)9z$^=HJ+SEj-ZB<Bgg}&y~zW}O{fjYO~@6gZsdyOLe%`^LS$#^FJxzO8irzxnqK?yPqBrXnQS4a)qeEJv<$@=QX?xh7d0C>7ulU!itJ8qK&?e?K<-3sMOHeR+=)Dqx|uwY9LrGrih7Owid@11ReiOD<wqYb!BE^cH5O1OQJat_k^58K$^FS~s8+I-{kaW8@oZ`kc{X_|^>^}8ayWGiIh@>_T7%r2T#=fO{Jn2iWGF6}8W!qP4VsCpLh)s)>i?G+ice9WkWY~hQSXuukrSvl$O+`#)a&Hk<QVP87!kuzyf-zHsn4jl$j```El@R%WM(KXOD#YyOCCz?P991&r~zbyJe=B-Je*vfT9{m(>_SaXb|JskplTd>%}{)dnn*rIUP_H1FC`DB4j>OFx1ly6w;|W2RwUOZm!=jXmnOSVoyjibjMOybjO6SL#hIuYITP85Y9Tw3(^1os(~*CrW+4Ac&Z7MogR(Fb=cMK)=OkOH#mH82C8`Ix64{g5oa{;NNbOASNcN!)A^VU=QOA)-kte0b;ndia8V4AP*H9Oc*O2E>Cy^&HpE(T0iy4Y1Q-_czlLM)p$${kl)aK;=<lm?s<lo4RsKv;Q$d#$N$(6}Ps9DKMbCHXXb*ejAC%2_GAh#v=rFJ4Kok;FWo=uG<&n6#dD9&Jkz9Oqo>_Js?gW?jL4?Gx(Lo7e$j1Y$6wHEAAmF}i4AnzvcpiUz1AaA7hCvPOLq_!a|olRazUPoO@UPq3khLa=7eW=aJeaJesB3WrcvQDmU`7xJNXDH5_8jm#Sd8&o1Lh(_mns1IW6mO?qCT}Nipq?UcAV*OTk)y~9s0ri+<hj({<hkT&)EM$K@>J?x@>KFH?Z=!ni=lX7YOJQ7r6!ZllD|@)k-w5lTA*s)D#=h>hgz0ghdh}&lsuU{k7|(TkwdA&$)V)>)bix|WH+h{*^Qizs^+b9{H*w#20cbTM_x-^N?uD2q7Ekqk-Jjckh_vwP-~N0kn2)Qlk1Z6QeDV-$vLPQ$vMb*sM*PR$aNTsOHebBOOOjvoyY~ruGDm7S8_h;ujG8>!qhC}!sO!AoaEx<s#GhvD!CrD61g6^HPw^cn(RgGNcJN8Qhmt2<Y4M3axi&1brN|xc?ES5c?EeJbrX3TIf;6hoJ79BP<)f2_$u`P`6~G~L-7&n8uAhH7U~?b(#7O0<bw>w(bUQ0X!1&GAbBNu2DLwV204WK8##nLlG=zolI%^bO!g+XqZT16)yeJ1-KcHJ-N=5_zGS7d$$n%z^*Gs1zQRyk!~#`wXAy?tj#Lk_(hzb-as+iPIfA^&@?##|L^a8q$eXDL$(zaBsRzj0$vdfg$veqg8H!^WisPvJ$#LWuhT=WcWbz(z0`&;_`?+=kLvb`i@ivCyMCxI3BKZ(Co~(2?`4D*@bq9GLc^7pfc^7#LbtPHpI`S6s25KaE19<|q4|xK)H&rJqtxoPuZb!{aZbz<a`LTwmO8rDup|}Axiv_Gg@o&`P<lo2xsMW{=$fKx@$fL;Psh!E=$y2EP$WzE+R6nxP8RRhXVus@R)T!j}?`GyR6fdHVBQGK^XDD9HP`rwvcnw4G3Wnk()Vbs(<b~AfWTmsnN@tQ6l9w?QPosK~CsLbHy~xeTxfzP9P=}DKkQ-C|$=~0NHD)NT%uw8rI*|PRomoSM;?~r0<ksYt48^q>it92I*J3Dc!BE`F^5gwkD~95FR3Ea^E@Y*i<a*=^48@hGoykfYkt>mNQmc`3l0RzD;$#(yA5ycBAF}WKNmYI6Pln<Y>LYRrc_;Nec_(=z^(c8GIg+}a97ztPZXkz}Cs3ov6UhG51!RBnAnIK5AaXzIG;%+3PwG^1PjV0HEOHOBjk=I*BM;Votn~*o6pu-bnbcj>)#P2|m(;W5m*k=r=vT4|#Z9SdKhTt+crdjNc`(^dolLfq*Hh<_*OQ~Dq2ws?2x@)u2y$Dh8@VmH6g3^W6#1<NRr`Ur48{AXYsve_^Qb}OdE@|US8@Qk7qtbs7r6tqF1Z7_IyEo3I=Lh@2e~A<8Z{5O8o52S4!J$KJ410ZY6)^Pa!qPMa!qo1sw=rXxePTQxeU21wJ^CXxdOE~xdOQcwJNy=xjwZXxjwliwKcgVxeL{c+=V=p>PsF<9!m`-k0no`PA5+xFQcv?FC(v`ZX>TF@1Q1;caTp~FOW}?|6(Y9L%m7PYJvX4&o{~ckl$0UlHZfRQE!vKk+WG4ivOl}g#0)85_Jn%=|S=(@_mNl)6{74X>uHOB{`0~o;riPp1hnILS9Y|qmCqpk;hZL$>Yf*sO`u~yOBqb4XPhmshw<)w^FZ=l|CnLCGVlC1LHmXtoQ^q2U&&Ui>dlpgO*PH+^(f1P0qCcr~ifDkALc{MEmJ~==Z;V^XH!>{r8*wQ}g=wM@sEl{-XB!TAI}VRN*D59hde$K0bcf'

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
