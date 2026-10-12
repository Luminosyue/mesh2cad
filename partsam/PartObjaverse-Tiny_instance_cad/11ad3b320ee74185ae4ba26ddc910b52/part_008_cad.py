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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_008.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_008.stl', 'source_sha256': '406f31581761ffbbe9601ea81ead6aeb706ea64de5531799111e414b6bc73f8d', 'input_faces': 695, 'input_vertices': 646, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.024026259779930115, -0.3899468779563904, -0.30193668603897095], [0.15585526823997498, -0.29924315214157104, 0.3924412727355957]]}
GEOMETRY_BASE85 = 'c$}r237AcF{Qu8PwlOo7qAaPa(qt)QD<xN=WGBoJ?$~9lV;{q1kbMau(Uq98FAav6GgPuKGjnIfRiwpODza35=bX>$aK3*2&+~u&f6w!I-mmZbe(vXdw{y-t_o7YnM+%hE<WEH{^64)5B^qd&8DUx}ZDj9Z!~6H_9sAOtA!CBH5|(fNv2{VK4lUb61!*I-xQJf8V|xyZsPBq+z0WHV)m#yM1`iuPEP7D)!NYp>HvOj2F|oZ3Kek`=klsf7g}SxtR&&*=T+J2l`hWaW)a*m2PnM(@68LdfmZ@4&(h*a=?bj|gRsZQP%l9N56u()OMW(vXwYGfkxpF5gZBk{SsjeTVTfTnodCPa#{a~J@XOCuD^?xmN%F6GRKF4YY3R(H?UrSrQcJqz5t=F^4`mOekrv8QwU(33gVb$N>T6|yp%a))0nqU0J;s<U&XVuBfvGUzJx|5&kZfMmnNBvHUuVn@KmHaPL-!j#c-I@CDi2p<CyQb<{wW-rV@wLqT)^WW%hKqk9wUw2h`5XNiApT#TwpRVDC#chs@p{@xfBwr5|2^>wM89XMJFB?#bNe%juV-GC`rE6C9~Rw7`dO3u&BZSj9cijB^CJE6h+if;%Br8;oct*9pN#IJ)Y<;D;(If*81Go|pNsBl)yX^|{`S|!e<8ZNRVO>vuZ-)H&7OwN_1gY~_@CB@Hr18=4)fni@dN%O*$+Erioc>p51F@HGH=^M6yKAX!FY#=zh-k!S+BkHv#R*(H}|soliiJe_7Hz<jovapZJ7V(#NW7C{LG{DXO{S1Z|)=YlUc_$;_s}{Pxhhgb3G|Ye0_6&Ic^tqf9|dEfwf-#ME3uicK!!)+`}AqqWFhu#8{e>z<%z-KCCfF=6`@+nFrhVZ;|=gxk~)>&6e-VJRtLv^jC)EpQ<rfj(dpw6?VSm`?CA{Wj<?&A5&(C?9ZPiKj~+wGkA&k{&lQNU%%?Fm2o8%#xFC}TKBBF>bwn&94g1{$GCcnKcdVq>HiNh|2r3mKRnX%z5Y))ZfEkB43lxCbKFqzN0*7U>SPs?`blS`|6?O#Wn7oY*Cc<;l2}>y6!u{`@yC@JF7rP``oF`g_-_9~_Wx7jkIxc6X9oFks&AiPJ2ySxAJ0(cXJX_C=lQND-H`rIS~5b$RZ!L|>9*o)nL8wZ=T51UkTpWt&)ZAjml<iTOZHg5vOgzBj+AxWs9u+*E)hR_pd5F{2=S+t8Ra~W+&jNee0%?UcT5m}Mx^9tw`4yQ5r6s;%h$5*vfr-CxMr0ZE$7{{>N?Jj94+;~q@NX~&YY~#&VK4UK2m&-f024UnIAbu>X%pN)Alp-Sg&uCe7Aop*PpuLFN_>3{rQ6P{SEP#l!>#}D`%=-+0RQN<D{P-(9aJQ-;-6^ugt?IS#i>zZ2Ggs@AU2SMc;Wy{N<73<a}Ad{M6#Qnq~P~j+g6Ir1+neiMR5zd-#=g{Cr8goG(|X|DEdlH*lUV5`R^h@s^)e&99taUqp_V`tNf;dR*}XS@jw31sU&`krO1pJM*^GulRnS`nh6V)&%Ey?cKRc@iqS>uIJpZJBE2>AGT$@+Z5lI6~TVEp5gSp{$=dv$yUC%V>PdwkA-EtI}hTw@X9=omO4Avir;CL)X6+2{YmzVAGuzsuWxT6{fRo_b<U5zGll$1lAl!(|A6Fot~OD|)rxU_CHY-qCQ3gGkiS>__h(I%evae39xQd<UoU?4E38*h$?tkeeD1&Qoogh&Ti7J&XFbN7r1;*fr~J<I$lI-&_}S6wxVp8NB<Im;&eLvEr+bX$YgwA~CplO0J?kea`*wR}#dl{nV;%pLb&NhTN%rT<>i+E6B0<L6nEo7>Iz3|&r2o%w+$`1if5yIQulR2NH1%^@&shm_zHoo!y5#NCVzT9D58^s7Rr34BOqTw<&it1Zzuzp&_he?W&$mjQ{$W$3{$`HbU;F_vQ)FH0Qm2^s120XHdF#gY-!1hAg-vz#)1H6tz-pH7$?nAYxJ>cg*{zw+LfrRbEI*KWgMRLi{2}Y7%Kk~sP|oY2m&DJ0mCqqn6yNJ#%y~CR{MZ&BD)~FtN&R6lAIf@_!T(zEwak4=9q))sAIkjHVt!nf?;aI1P4d5C9(wY*V%9VnZyWXcIp)$d*;g+ypADq`n6T+`zMoOY8`lCqOX-h3HfFliZ_a+MAa&v|O_%zWnV*-XPJGx5S+9-M87Xz*tId#ksGxif_l|EdL&jTQIp1yHoq0+buX{p_)X%(1{eE&>@2nYeKK{pko-cJKthanuRuSf>tMq4L*i5BAJ0?l}N!4aL*Gu32mgG;0nJLHpEkmg@`N&K;ZZP%RNu4QSvt&OsV1DZGIb_x>8P{R@FP~fVSx07@YG3EI9WA8J?65g<+~1XTanFshe0Nq+<$2Q;b>|B!|KxylD?jyGmg@J%ziIiNsK-`|KiKl!sn;#v8&%%&wUe*lU$J~W>RJ3(@qe*=t@CS^A2?AP|98uGcMV-*jq79|%h&c*$hO*DtFDpb#^9H?{6N=QYn*lT)Y6vk>eiV2zDgZ;xAx@MAisp=>)i&dk$%=u>iD9oCR+ZfIO(UpRr=YZF}@dn2Y!3Ycb{yAzgFg<#{lx<@z*Q9`{Y}SALtQh`L0uwWd8NdQorX+@|(-J^i`Jc>$y(yPd25_8d;Y<UA~m#j+6Y<JUMQkSo~4U|5;i0z6s)=Y$WrbpOQL#7mz=mI)2#?eV2VH{b{23df#>AkHOE9b?>+POX+80{KGP?ereQs8~=pl=MCI$)l09Op`0&yWAI<X?}$Iq^0oB8rT^QT$$6bOo&2ig%l8s`-h9gsr2UcZJdb>Ni^#98JV)z!%c*~h`tsZn$lE}jzwqVrkLOI#4yjXx>&!T*bEYJICFS|Tcc!fPX;)<3cMK!H0{PXH>wtE)68V3UKN9~%%lD;6kUv_^_p>$0zbfm__d@Qo4R%QXuTw{^tFHW{UDo`aaLN2!ek;v-U;cNN?>q6d)Vchw<$LoFl3yObiRJt9Pg;K9<Ou52w|qVSH2!dWcbe#hU9x}1D*3*vvv*7Viqvl>$GtiqzXE<M%MV;#z1z9Zwaf1)zVF1dO1^e&!*1n#x!l<DUDx(JP)Fv$bEDuMYyQ#>%DSKb`Gol4_=jaa&!3j>EpL>xeDA5n_-F7-lYfjlzgWJ0qb&JL$xpX@-;E07pHS-PH!54c=hR1vul-#Uf1y&xb#sd4-@E^AteI{d@8%-Q5BRs?*TG+E`I>*6+-EmdwtU~s<<!}%`1;MSsFOsU7ZqRgkHW8tzX5+dbt+oE>((CpG5F6)e{P*t=0QJyP3Ga&1sQMJDP=wbx2}<YM9H^(dw%ru7iHdV-y;90Qpfhar#@EJ*L^!^ulS!R`JUS$_{+#YD|PPF+$;0O_h6ek%6RWI!e1}fpG}dL@4nMyugvFG{FbVpF+#308=G6c=T6(bGH+waZ;ju9`aJ(`Y9s4-Cu*;AUG$BOWnJ#{$B!fbZN=BqUy%MM?>}nI=bfSWRd`O^V)@!XW28>{4Qn1;$=mSb$$!zx_aq;%eD^;S@wpBsCn>&`epBXo=VzAh`DeDwL)tZ^zW1L+Qitp0z5KgPQk?aD$=Oo>ZZrIvjO#n{JES=4*uL*>REl%Fb{*f{t|`(Vxvtvtpx=!qznU^${cish=eTS?aCad7?R4in__WVcoadu!UCl#QzP2{Sc^>I&D_Fi3wAJ$68Sh$tVC~cR+sU6O<6T#aI=jekA>&#bZuzdDy_WCtCs3!N<$Hp@C%>su-yL*J@-yC6>S)0Yb*VF1=3!kEsUO@Je~L0LcktV~)PLszznL!mpP<xn2RGN9<F)6(9o$lPj@Pc^32sY%OJyG1!R_%|E93PBcNL%Sr31@zzZX9mUp}|{mLIfyUvO{B_xhLMAI9%XzI>0WtvGA>dT@XI6H31Ad;LpgyvvjE2V1_!zd*?k1jphpQu2L|Buahzxgat6l(jD(*?=D=&lic2if=#nX^Bzzo5+{niM)xuEI;r_5`GElcTxO%zrQ55!QUbM%uK`YZ24M&6nuV9No;HRt^$XdpOfORxMGdVUEsJ<$6gnAfiz_v?yXmW4C)+F>UaxeGS7>Zb@UX-CjZz2bxt$hN3HP&<}KLo^zHBe?e+B)IE(+OvR>W-=cJ!mk6Cqm^Cnt#^a2-{w}9l&o3dZ(TqOSqj=Na#?eFV6^M+FASMlxd8RjM6Um-tNsUIltC;n-rj=Nw;s&n1-#5ikR+y#rLI@euK9A^2Rf+bU(`%O=bSA2WD?&p^!Ka_nnT=DOH|ByIB&FA+NZ(@JT_ZF;3KHonl#z;R4H5cFh{dfLq8CRj!`0~BFK5ssLd#RuOp7;sPbf<66kG<~hLLFpW*&U_-3H5Zv=X-MdxZXmYsB<>Mx$fRVQS?W?$MYpL(4D>~>v5%@-a=hDuKbQ1NNA}$eP7mday}+hR(x;fPZ`er<1N%(e10GFCA_LTeP8DJ3}ycm>P<hNQu^sD)EED0^|*x>GoLM_|GwlCR$k#{`25b|+l0SdSud||EB<HXw<Ui!{z_#Xy}qyTSCQY2{4JL6E1amTi`Tc!^7X>&lzF!6Xhrr&ot$}=@5#TNY^`UJ6#V(JzWILqROXZ45hh1j^WZA7AHN&x_4Y%3PyWx;IY9kIlAj;E%jw&{JLs48TKVoG2c`cxAItpb=P156%cbt;B8S;Oos@pszP%6c?dKv#Ic}8Fe|M4Nif{MdUF4*)Kka^cilnhWD=GWdT_giPLfMB}NYFm#I%+EqTI=EpDY#ELPkkwt?+yvsr<^aoRQ%9=&i$sXJcJ*<PsYpld%hj`#mVP;W1o&+a-Va*X)E{3ehYa5zk;&QJt5^SU(4Mu^OM$Nn>DW?6(m3RqU3jo|J><ox!;O^s=k%)3#quzx!?3tt*G;?__@bq-MhB@!s+{R*2p~fACai!=X_-Ou2at|bpqL=WL%?GuXXxb_M39tNqaUp{d>P(ALzJQ$<N#=pSzBHyhS-~MjN^A9q+T%>3h@8$mijcXB0nha;W78PQ9#-_e257PaCQD-eU{pxjlWO;_FAAm*@P9AMq<m|8swk{g&28@dG(KWq#iKccnG%kO=Y*%KW6g!MaoyKQF}k`$+BuyH+@TZ_Y|t_by4RoWA|Lo7V628mI5hepik={NJyfzP+D~8{Gz_zWw{}%+s5ceEWCgLq)eJ$IYlO_unJi72kf2b{~6ctJBv{_LJwS<HHnRJMpi4FLPq6;=7N{5&z_Gitjr5hJ3Gd>ZxrqpH=0!IZI@`m&@%E|3&6)sa${Z|44TF?wnc5{?|jQOP$;t@#pSZ?)2R`vz2|Wht!h#T%UdU|5^0|A$7=Kp!CP~wVa94pW0QAHFWsi?5@i7KM+!nI*XM42SQ$@&LpW{yR215EBYGi-irDa@f%P-TD|@kZ7B1}@AZ1^>f|>hzlU=Dw|)CM7N`|Yek1C9NPo&(zN_fl%09IF<1X3^zqwLJFFH{6N$w@-&(JB>zSWBk#?O~JL+aqia(zpdc^lf>^0m+roOipV|3fNRexT?m>ReOm2a1lt|ARUWs53$QoTLZpPo(~KrM^3KI@iy`TnEN(6MrWD5zhB^`14ucxytq26S{!w!}m%Z+qXYI*w+nr=wjyKfKuNZx{UmV>UAk}xw5b9I^NJ#tm8EHLt|@QyrHY{rz`u!7y1?J*n;(~BkLHtf&H1F)Ukd0zG?3VJ#-WE|C{uu(`xJfW&2vrWaYSe=r-mvUG~rWO}<ER_<GI;sULCnP(#IECw2NyNp$9GIdM{FWYSuvZ+|}Y)vl);*OlE=>Q6elLCNR2!*ig=W~ILUyXuk8w>W)IMmz3bW4AheZ(4x+*B^=>I5~{_SJQ3EaZePK?|IT^D8BdDBKiJ0eV^j%M<V3=@r)bzNm3^-)Vl8k#*SU`FyA{mXR*`Qa(B!A?@;M;r?2O1ly!_aYR!Kjbcgb}%U!#YT=zngsUI%)yM^UGOL6%2x_BcptU6lQZa(K^%X*F8W%bAQJ-Jyj|8bp{IDI{5tE^+hIi-#-CsFEj-muD<ujRzcKIxmkM)k)ruKh|K`+6IQ4PWcbw?EefCY0Ww_&i_hGp}z_eEa*ELyvD!j+^nieEvE5z2dvm(&YQ$V|BMG<K=f){rFVHx9_vAliw@8``BFWv;Qf+>u5vSKYU)&!uGIUC1jt(&0wBW@Jm|0XUuPloxYy4P3{X3$C<ZO*71zY&)lLbB!54j8%L6#Y2~}ZzT<pPQ`Xn^?|sf>U0h)Y)awKL#2a>+>&$ho|6RXQ{l6rC*arNcl+SPOVYBfsD87Ba(8DfL=ZaFt7xpXuRpq#PSU%^`9@(G67U5r!`N?z1c`<O4_4ki$U(4Mq=f%(_<X=<rb?>I$l7C&fZ~BH;m%o=B_P64@rd97F{w+B#@+v9E)xz&6zFl7nzbk(3FG_taJZQi8zbf_J;l=mMx}1`AEI0pv_$Bu{*Edi$-ts-+r7ho^<CA$VH=X<^@K=&Q!t%Z0Wi8*6n<?{CZUKII{4DY(;6F{BWlDW-cty+C^Qv0ob#>bQsp9i_z!P!pkkj|(e5&-v7yc}Ds>%7%x#@DJ@6LNn&X;k!to>~J_U8&u#A)hRQu2MHtH|{^Ji_v|yjy-}KkxZDV`Se(T#)-<cx5GD@6vI((|70kW!}bqLjB509Zy8sA?bfr##K}93z2I+eVBiLyj7KTagDycIK`Qtvssx>J^V$+TTGcB+t+ipsQ35q>f{%HV18=ucb?bx=cgv)8qaYrQm2-ZZ};E!y}7v$%ug-qOi=DqdUzf3^OW&w#hNicFUh|*iC(qN>UXi`itq06Cw@!%BcE4Y;f=l(zcuUlj~v&tY@O4$^L=42lHXSLRqh>G_vqirZ_jaSJ<uQ3zuzD6wcHe`6BhBU>dSS>9sVkQC;D@P{OS+&?QwaFMbXc{m2r8Cby0k~|DIx9Ic~CYTyL@Na{bABLH6gVZrvW{yFT31)9KsK3--9Y#d_1v-{tynu3LBU`%<T}?6*TBzJ8eRKD=D<?dKY8@+RxwZ|KGP%Rb3_PU+8m|5>H~da;3)Z+|}!xO-K1`uFDf(7>-B=6en=!XM1}Qj|J*y3@b+d^E0lFV(-Q%!6KRsIqVEd3eyb=Rq$Pt6rb)`t^tTF70>x5zIpcnV$=#cdP!B_zf&SP;8WP9k9pszx}I<Z$J0h^Y)-`&s(5a9KJlK_|Av#ewZJ)P)Gj$NAY;ZmBamL`2nYI-v{mSYQ-lou4m-BccJX=hxzt+@A+Jpv~n{KIDPwmYR|K)_!RET7nJ@#=-d6beQ(YR>1Vk`2gLu7`WaHE+-Hh!=WFFA;!juZFLpoO#b=YhO3vSMi}B|w*B@WUsh>K1JKt3<f&BU8*OvK-dVab1i<Rrf{W_{|=X;AUqfT|@xDWcC&X1G7Qn?P_&sTlBexP`=95=77^wYCo-NSr$^iTM^>E}(Zlg+H_l2&4mdfyMPho3_JZQ0MBnd`()Rs2A7F8+ST^|I2R2YtIgwtw&QD)*QB{x{0?Tr2UNdjF;Wt`Y|x@ay3pWL$TZ{y*s3{dbo*%yCn>{x_EUONpcS`;_~Rr$nam`9wQB^y`QDzQar9x?SQl*NsQTzZ=k1U!Hed+I7XZpD(<J`hTtZjQ8+-{BztdUR3&H`}XHXyFb1XKapQaxjxvweIM~$Xr%b|d8*&d(I4gq?p~(<7a3Rh1LIZw`{TW+?5q3ZRegKBz7oH4oss8-!1<E9AL?`c(M#kj*EhTWwr^io?f&Z}t}qWSWq$s*-w6Lt)+Jx*&x5}9^Q*fXwo(2y^+(Hk%qUe+)659bN@;zf9siWtG|fM@KK!3j_pkkb_fM%`t@Ho;PpQ8*`moc8Wb|t|8QzYrg-u-tuQy_g5gXx6v|9vgT6-hjLEFNnJ`TSF7bQ$CgqDI$)q{i!!Mh2QccFV=Q)A&>@L<B^LFiD})HmTla6`i6H&8ch>K#q^4frNu@(uKF*wo|j4frTw@*(svY-$R82;PJ4hWEg`&`q$Z8{joYe8pOsoJc#7ob~XRv`yV=#5Q;h?Q=%t8F3lTq#b08{feQ5g2Xpp{|UVUUm?%rl7<EwQP_x=jHqbD6SN->lGjVZkD*V%Pmpi&t435eqAC0g?bb%T9c2EUG2z!}_cS8fh{bR_+8-LR#E7kMZ`vD;*k+Cmo=!W|*n1ZZ4MBf~O}z|n<b9ja%kX9LO}<U77lVZ_(k^MlOGb2n?*vKvIU_n5(G7l-_UlG;H)0T6iT1lj3^rmUzWI6sbTB-aJd@uvVw4d>;O4YnFk+|?(Qsqh<~bW2Ea$hWkHDsS99)_9FG2F2qHr)Z5`)bDu0YP|E}W}_X`APEB4P3u=q}jQF0gq{UF7^T^*6`)_#5YG7iveLgWxE*3fd5^0#`=gfK4@Pnrxn%`#FzIJpdozJh%BG?GWQV*9{Fb^t7S5MqEYzg0I4Vpx5E+yx-)qLFU(In)YOna47AXMpQ7O4qTpgb0g{+(H5>nyRQ-LjfjC;(Oz!EKqFSc{b?r|vD%28u#ff)BmOkvFZ2)iFF2We^L;zeWH^}|lgk_HUOHInnffQS>lj?Yh}VLJpP=2@i26pn57(yM%ZRQ<d;oW$J=}-^MvQ}d)1G8Ryb+V}&DTeu@o+qOCXY2@iV<Eof%ZTn`WrD3jf39{mU~`Dv_0Grjv?QCe?K$^jv>e7$Eo!s+?IBhu_ydSq-nxAw9gxH&4_d~8_qD|j1i{@lLLgwKcZ*hyGA@>tiyk(2AgWW{vUZ~;Ub2A!O#Lh!hdSgE)gW}FNT_RO)g_ZK_g1RMQOW?c+`le(BklOM$|C(2>Isw%Auv<(&U)@iV@EmQ5$_4Ze~O!BVLDJrd{8NcZ_HW*Q5QO5q*qkfVP0!7}3p$9`L)gKQ*F*5g)+)X!kN=q!DA_?zF!)Vt^4#;m>G~Gh(d~>*3L~uNtw;h|TbJ+9!<g8*v=XgiYN5o4O7zZtS5ghW-v;3zD|^-s?u(gip|}VdUf+`VagV?OW!$85|ZY{5S1LBmOnl3a&-Fn4wP@Q88G!2<;w5lry3V97X$CBWfB^4}O~VFe9oO@fO^Zb|WL+Ho}cIg-v}0HuYtAyb(=|Xa&d8HsAZI5pTeaXpc6cwGl1JH{Uk_Z4I|3&*X+i)HUK6Bl;N8%!umn7}^m=+%@JVh<r2mdEyyfH`N74z~+0}8CuPV!ok9QX=_HDGG5OO68<kp+9eDwV8kW34ebo0z0Zi1M(j1>HzU4+!-J(g%!n_I=!$Q?{tfyi{3UrN|85-mmJ#{rKX5)=ja;+d5cGX`2>cfMBK#KI2(1R2YSuLQgeJ#6s0rVqZQifV`?vWydaov*p;OTmI2Aso$@SK}?v_H!!lhvI`NPz-AYn61-h+Mz?}1~{5pXO#6deu^h2KP*z;D8Cv@z_4&F2qO|J8)eF!^uvHvBhy96bpihYzF2;A6~*$+{8db7L}mgtqxyxLK2DL!H;ZLAS%($uW5o^S%Y$3!Bd^=JSX79FoC)Ttk@rIl2NiwG;d~+?g;r672|^8UaVbRSA<{K%a+A{Z$iw0lq|-{0sUsZ0dLLFYph9$={;;U{jOeZ{eMU$zP*e;jPS($>wvM`8@X(x)I*b9^XNjybax@-GA0IbpyH!o@$J7iV+_ZCNDxK!;9dBXac+tUVu)57r-B(6XB2G`KTA356?p<!1Lg_=y-T8JO_=3=fJbkICwTZ3mps3f@h+m;F<6=!sJiT8St-0q#JS4hzmxXH{uv!@=^3B_$Yh?{SiI_A4bo?hv7qL06qjCM9;zp;UCa5@DK0-^fY_`{vOSPzlXm?bKq~`{b)A4A5KM2!l`fynhqahE~XMDPeG5sQ{c(yVR$l}fF6Pq;7RB~coIAj{Q;f`d(i{17oLEA4^M!{qu;{g;dpdE91q8#sc;-T7EOW2!uI|e#e9vzPiL+^X8ugQ;NV5HFTm%~h46X!Cv*Y)6Z|9k5&R>34xJC5g9GS1H~^nT=fY><Gw2-n415}$4WEYd&{=REoP*AUbKq=r8k`NEL_dM;^Va4Wv}Z8KCVy&N6F)KHGs5Jh=mK~tJQtk}&xI$W6XD5l96B71gZrZ%xIf$pZ3}mTo1<^R&EYrESK&9|H_*E98*oGP6}TbX40XfJ;P=p0@OyAC^nJJ&JQ^JgkA^3q6W~ek9CSK72VR8EhZn&s(8cfy*oS@!f67{#{5iZ7{(|<$w3o78Gg!~1=*Q>`cpPlz_Fygh(~jfyI9?ma8okCE_8_+n+6nGNj>$E7&ztaTw9U1vhF^`>Y&Ku3jy8m=!}ZW+a6R~4^gZ}pxEtCF?go!SN5iI0b?_wGrY?k6vX+bR=kVGbUR%i8ts-X?zR9b3%?Gcd{RQ4<@M=en*<MDN{1N&&{1H42{TQAG$D=dgc(^w@4(<)NM0>z3;W}s=xDFhFz6M9YF0>}>g3F`T;PUWOXm$80xDr|qt^~h~z6-w$zk_yz-+{ZLqu{RaNOUSZ5>7xD!U^y^bR|3wUV^TIm%z)>)$nT8(&Pa~^f6)>Ve&w<GdvKEMq9(ta0j#j+yQQiz6dvkYopJ?wc!`gGVlxV(`a${X}B~R3YUgUqDA47a0xUVE&-Q9ABRi9Pofp!C*kMOD)94gEwnyd3vPn8fSbVW(I~h*+#T%+cZXxp58xPhC^`Thz*^cog7q}DAKVA-jCO=O!>!Rqa3j{z<f^dkRb@R*tpHbGEln;4SAfgV4uNeig!MGFFkBoCMGL{9a8a}fT!gi>IgEBV{5V<;ejKidR)#CWRnXVrDsX+Y9b6x7f%b)4z)@%{90m78$G|<|574pj2-b2eF#vy-5g$7I56Lyv3y*;Np+n$)a7VNY+!1bsz702mtD-gFs&EDLIk*B`3@r;6gG12A;1IYl`Y2o&E`&Y-7lMnR&%j0CF!Uuj3@(Q@hReZ~(MY&5{5m=aejRRyj)&X9ebFg!UpN+>3CF@?&{^;-*3#sHMiemO5i}Tn1P($qxJ~n*;8KtLpZ<IL`+v-5Gfnx=>K}Zk`d2ZW?`&n%y7w0|+B7d{u7lBuVC#aj+`PkS{{x^D$^H'

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
