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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4f9391e9db8b453ea08c7c0109077d17/part_003.stl', 'relative_path': '4f9391e9db8b453ea08c7c0109077d17/part_003.stl', 'source_sha256': 'bff3c3a47fe24a374cf97d949c3df90996b693e6c611707fef040601b1b40eb2', 'input_faces': 654, 'input_vertices': 442, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34728920459747314, -0.49999988079071045, -0.29374071955680847], [0.03125925362110138, 0.2602415382862091, 0.3015563488006592]]}
GEOMETRY_BASE85 = 'c$}r22XqtH*0x9V8ak#J5QL8DrWa4>U?8R#ObN)QgkpNH5xs`cdl3%3_YM}t0fQm7!So_}O-LX>=-=$UU+L=1)xXxizR!2<^*(xMpEG;ToEgm=aT5}pJVka*{t9XZ3J;C=tAwUeWYDr}L%R(e+_Ou!L1p^(A7Rllvrm6+o!30HSx7sJHdGr`tZTPHT?Q7bZY@@`d(~nA)?(fJ4IDf$yl>}z1G{!3zd?B9pl*ggs7HAJZpP>0fq@kQtQAWHSjSlZmw)Mu66~L<U5++X|LM#fQfK;!iP1iMy?EA(LF8Lfuy6nRRs5V&B;VxQ-sF({gBGP9`@&<AZ}PR>O*vm*HT4pI9-d-1sjGMU-=lr__Leo`Dc`!ToA|A!?j*H3K3s_Q;oBqAbG}xfh0>4X@3Y*$+1D2g;(Ys)GHU;uBRSvfI|J)W{>FQJeA>=lo4B7P)#IXl`H5}Lb3L67iJ$w-I@YVV&PDt1tqVWKDfyZISsdgmAO3&k=ZsuVpIyC{sQK`<HG9?kUWYf)XPX`t6Yayde;M+dlAn}mAANT0=zk*Gm;ZF;N$-67zip!Ve9!E1JlcnEi}~q<cfPaM^Ao=E-Tr^&&v_KX<IsHGrf46&Rw2c9?|eOI`e{C{;)9~1efX{n57v3-Tc`Dt`J`_Q_vugEHInNsu~|9qT7k_xAI!e())}4;j$7lE^X~YeIp_bEzp$5@KmGNRAYb`z-<&_P;41p;9R1{6v=864H-(z-pK}Wz*ZH+E(Z2jtCw}wJw`b|i=UrQV?L@RMKk3a$rT=FA_`GXbFCCBe<p=+D!aLvDRX^z~-{YI}2R7yU?0F(KNBi)#uZi2e^Yxk+Wj_3Q@z-b{zMfcbgLl3)ZoQoM%+XnV`Fa+|IQA=F=6dZfb6(}+d(tRA+RJxc|9pk#L$8g}{^CXUt>cFC{nC;B2H$^ds}rT4iSLrwKT%oo^^tOYG>_$e^sT?K@3=Wk`VY%1_uWH3%K0dmbd=kbs?PP;H;2S~`?j0~*>}y~A?M>*BKywSkGOx=+Boswoo8Rq+?M-y{e13sZ{OMQtJGOMT*<d*yUf1+wT$?&v-h&Uq$2Ov>1rPD?Yo}mW?w(MP04qayDP_g<1G6w%S`sIRl>O*Ei_*4+bgF@e$6y84zD8;y?tAC7uVyAC@=lgy1$D*Un?&A9n&=4+qVW}k~+I@k$$ebB)`U0uE&u%R{9xwdzT!4AF0PbNzP-oo08uptBl*xu8H2htJDh_pWiA<|7ADw{I!lgubf}|>Q(G(Qwk{OSM#sU_ZR!VyvlsjL#xUCC~dN<-t$eL70AA|(HLdE>8Hy|Kf#}r`KCL1tl@r4_bZQYx-WTr)BVTeo9;7i-+Vvu<eTmr`s{GYU%8vlr&j9Fa`r8)#INvC&i|nPazEd5hOcj}*MS4x`C5@f;(z&iz&qbw#wxz)ey&Yh7v((;p6_M1Z~ne^`{wUuw{QObb^GS;S@`DfQ~T(8;`cZe&Gq}8IL`Z@sfk}M>p^b+@6v^QT#L`IW<O7cLp)xwk9M&?b`|@M8GdpfpAaD9mSZOSTI7b)Jb&9%J;nL&`m%3(IFIw~X?Gmr{D7{jy~oY-T$B{SzMe9JoY!pIq|T^RQqSP9W88nbHM`lb_S(U9EHBFYwZC;9Wxw%u_MIh1oMONF+(ps8{42v(a-DrQNk6~;9?N;X({TNoYZ?36_0r<s^`FbWV<7w1aR=qN+BcT_?Aeae|CpEJ2c(jD6y8|!M;1BBpELF3d13!pn0-A@LX7u#+81i<+XAH?SGP3sobvR^D)uuq|4kWBdlLKhRVR*npGR%#Zua&1N!*Y9Mk5)YiyOu7TR`T`pguC5@7G8_AESO##?9<w+_Zs%#h)K^!h4=*9V@Z#Of^x?OR~@->?gmylJhnej8n#Q%iR_HdE<1cvrdd$H+3(F|8AD-w{E#U{JH;n_MIzF#wp_i-<CU8?jt>>tmXXF^QE5|cjUUNvSudhv!N^Gc(%%Z-v>yYQ@>+h4;#++J8Qxvu3H;_jPD1|3>UZ_{qR%%-q&7lXWyDU;4Js^s;Hco<`Lp&?RG|)CuZM0PfWgho@m*Mv+o$O=bSP=^OKfwJt67ky4%}iJ^Lw7vu~?hGFI8I$@ldCcq9AT20d08=bmk)|90ChDC2g$5&QbNQx}wRZvS>E>!r{*WgPr&vu~SLBS9I@v}4%U6X(b{p9_@ltt=hbcj(8Zo*AQMoImDe-(Ij%ta7|9f|tl~#mM(x@QFRXeCN6A1EjuIi&>W!O;Gk*toUM?=WXP9Woco4|I_*`<LkiDv)2V>JWal5JT==wKCUeLxPND^c{_uA`8Sryd&)B_`?lb4c@C&DZNFTXTNZeao2Q=Kq3qi&_b##~`TgqcJIcD)ceO0b&sExpqw_c~q+Ej1e+P&7-5Oj{#?9n=#;uArPwGh~&tWTSZ|3?Zyq(MYdz?o6zlX^E<n?3r^;}ulw^r`3m;G+n*thn`E6*QwK1ccTovr&EWIw7e`;J??<$2?61v#!WJ=wQ!-^;$X!(YZ>K%Y6R^S($uclOBjb+iln_P<l`IOv1!@N<=xrak+vf*IL&mHx1U{gn;acMkBAahsWR#Fy{bd441N>Gsa%e)TFBmGf@)-RJ#>Y3$o){*s`KgUR=d!#_jVx7}Qlpp0iwB>UFr)d|Y@&xl~(k#9qSa=se1{)O|$x8!lNK9uKU&HwT&*1@CXIWuwWIR0GbkDobj;fzFO98A7v95TnVuRU6jsEp^UUF<v0tVmSGf9fjs?bm)yRL<AszxaORN|B$RKb@m`tq$_x+n>EY>h0U3tMa_nOW!`=%hzf;<-M?ILAjrq)^oH5IcD(j<XzAG+s+)6@yWAjI`@+?UVO*P@$83PpTcThM>?B|eOK;}SCslqzNdcp&dE70EA^XvPyN>Nla%_g-lb*jGJ&=D63(|4y>`r(uZ`|4_p5&s?B4ae*V(iKfn&M8r?0Lk{g`}DKa1b=X3cn7?j!E!=N%cuU;T~xyq)H|2==d@+ppy33JYhA%%(hVYmQgVc)#Hfxqm&ZpnTuBnm1v;R2g|+99DEK=i75wN$n?Q?pN})DgnH`&87WHzJ9R*sq^v`K2H0%5Ayu!8sD1xSy@EprTh6ReqMXlmihVl+4KA}wUmwX*E?iA!u_1ws0ObOS--6y&qXV{%5&yl6}xc$@_g!Za*qw{>qi#I_sy6`QjfEAFV@6vd>?eZm@L<OnppOot#<J9i8eX+G4{i{_GbS|L4N+%qmD>F8$$b$IwrT1=geJ!r@VcA&VGIl(c}CVdi(YU$<*g+v+sUBe2~6BE8eG^T}H`!&z{i(cpR$MRiB^zXR~k5x0A=y^`M`OXOB_?*<UhTeXh=RoqgAWZSoxJ{{DTT4dVVYK9hBh;5_TOpTafRceV)S@z=`NlH=_<MDqPR%6sFw%`!e$pR#XDXs<k<YX=4lX8(DZJfC!#D$k$RN$k72cbE60KdZ=j96fFb_h0HtjB<YW9A@9qrm6beUas6w9{*3Br2pQl<^E80j`)57>hrnTcaQ&?HSBBo)=B@NAu><)q#VZMIs2}xyX0B2hy52p?AvynIj+p-syD<BdBpuYLn35e_0KV!^;kw8Pd&qFd47(|GJ=om<K}b9{0S_=z8+kFkIQy4hm8N!g1kOz-BW_+k2UHlKgXDTXHc}PPd~^vitF$ElIN%M$%i@Yx4t==^VeBol=BYX)_E(R7w5rePVPUj>lof{%P!B8W$wyzY?>M3cf8N}uJ^Cy{-no<zb%)HbA$YH|JrhueOG9+IAuPB6dlX^4a?2%eb%oJ<#~0cjeULD*cfG=bezJzJ-(&-{&H%m^i%4!Q@M^VePrMHMc(uEDv@#?Yi9b1^Iuoy<I<C_lJl~r5c_(jWU`Jkah2Q;GgoHc{z%S?J?V?gH|GQC=chL@%6T#Qp7T=tU-q2`XUqFVu@o{6aVhQGf7p5T{VOoH_}2c%mFrzE!0V&>p}pLX<I`dppG_6mw;ygT<Nso(ycaATD*5HRoKxlleE0oU_iG~KQ1g`J$NnkzVfX#V?7QzXCf{?PX<B4FpZ9XL&nfd~*Ddz#k@MwxDZWVZ<3F%(ZMj>0A2j)%{@awA!1Z=Mdq$aWCu+0r`0?_2WjtRT5&wJ*Iq!WFWL@moefI4$Qp73e<)$`~_xre+`W|<o9{a9T!7|Q&KkdbS<uLZ`yR-yl{yYn3-}dKcxgJAH$T%OF%D(%(+jAa^E|>hI88U8#D@&a%^GxFU3;X{reja(AEcBiDNB@@mH)r^{R;$yAeLZ^(&Ug5?ljn!&@7cG#Y$(_D5m}$tYA2t}{oEWZ@5}D{fXVk<?<U`K{bnu6zN^?RnV&bUhl9L)=hC?{ZVfN<x}8?8q4ab0*coL$JP2W5ORS;3x0-y<``6T!;x9>kPC38+NmKZ|tetX3IbYRZv9HyNI<JgdRLZG*-mf3#I$b4S$$20DGy6{eloyoq;@HH#BYXZ>W!y}@XM8?brg8tTH=I+($MHS;+O8Y%%K17HDfuza<CXKC^A!8eW_RViyMdp)FBC2^o&8EF<vufRG{$+d__@B9_vkuRq@U@xrhAW%=XkZ2GkBg%dVOBG9!<XIdW_FElluv1CFiABp*_BQ`-<36a=wbOZ|xkQt^=5T_xs@N#GkqT70=~&>j$IuaX*39S?uRI8?PK!%NFdLe@{32?%&h3f5)-!{$1WxL4KFlnl4p*_wV@H*u%5DuXoS*r+6X$+kEn#kSUJeKeS|Xe&IS7k2tT)6O-?mCmU|FZ%w~eU9af)gnjMSI(2=c$Hm#~TaI2-t{0Q<xn8P&U|&yNPsTZA1^Iq4`L5Vt8UKS#<$ELGO}sMxjXJQeUn?T>>icK%KKRdM$&bAruZ%;M#=NfSik&6n<9_dsY019h`BL%S@985uvadJYEbCzI_xgMN*tbn_%J;Q<eZb^<)&~k~l78Bqm2ub}D%UT3Ytk9<yUmvO_sd)6de0O0zxOcv?tky0)jTbJ(Rmk@`ET+)^FJ<0{DZ^Qb(=NUrJflh)peV<t>*E(%AOFfjPt=`>^pC4O;oNUv+ur+K3$f6`kqwRe|EaqxBV0=>rU?V2mPh=vt9P<S+Ds0Gy8h8n^KQ^-NWR2);*p@&*%O3Xsxd2n0(Lq8gW7V1D(|MoHV!CcP#C$uIC(m#J+uVq`IC{<b(7x>Vi7oZX{p8$949qI^TZD$iDU4N9ug*nU#G<hGueJF3y$Xt>-8G%x*60LetyJyvpy-zWvZU`TlijYl3|E+L0Hsj?rW(`&wo{b=_&!F7Yig|2)^J$@g5R)o!!zvgqnM)s<%ap5Yu2qOMb!e9!p`3YXuzj<;9WsowNrUtbfUu2XFs%)WJR4|SdD#Z2)V-dE?_={fS=)9;Bo-`Y5&|GY2N`Ic@I`>sdtWL~{)eZ-e<4M~vS8<WMcZ*$#~->Kc}OD5m5zU20sedg=bv%X~VJ?l%gQ!V1-S}E(sp7U$+J?Hm)cJ`e;tEuyOe17(AXM)uET)8;=`d{_b`F!r6^#886y8d?eU-q@9^VRjYNe$$EXi#}RURRob<i6yzv+sP@R_62CX_Hw~ED?WwK%z3vCf_s82cpC;Qc0aBjdsd@@to#4zlHX(?|QGR^CWIE|NgDdOD*e`sZPrM!Q^Xe8y;1Bt&pr|W(hs$%Xh|3l=F2jhJD+cXm!2O<a_3W+mE=Oq|67C@0kyYX_xYTBb&;4?3&ziUNY5V-}dW3Ij-^hWIgoZ+-2lDl6O+qAx*w#{c!zf_MM&QT~Wrz<a@@)?Z<6RQpU&Rd&WoKzk)Spzq+1j@;&u5sLtysjxoce&T7?<`SSHP8~J(0UfJT{@#(Sfig&)*=ll@mUyD{a7SyhI0pktYh_qUEt$VoFKNTgD{@m*OpNjSj{Qvr=qLnKJ{$Ky8Xb+=?AC33{LEI7A9o!Mz0oo1R0o)$i72F=&4%!9W4jcyU2Mz;AKoh|c;Iq&q@LBMAXfKQKd2mYvaVWGmI27C(+6r8V=8zHJBCLEWC5Q_^^MgtK!3Dtipn1Ugz<Hs$z<I&Bp*g|1!G6%}U_WpU1aUTKRxoL1a5iuj1aT(lH(=5<;7s7O2;$VxRA5pKoEmIF&|h){{Ut-tUkYd{a0+lbXc}-ja0ci%;0)lx(9Gb%;G)p1;G*E-(Cpyi;F8ds;F90~XfAL7xC}H8xD2=))E`_9TmhONTmc*iwSoh|m7#^emBCe^--4@xt3eBbtAVRP3xKPDD?#&tD}gIQ^MWga%R_U6%Y(~8{lI0xrJ*^%rNO13*}$d1C7@ZrCBVg?nZU)sMWAWHMZg)Mslge+>7f>IdT>f;a_|A;!#*PpLid9Yg7+G6$;i86#CD4)dE2pVKX^ad6JOM%%{H_pZyUDl1Ct&AU)H3}9<(KI54IfuA3#lepnJi4z|_ZO)J8RKF?59yTcIn#TfxhXa2k1WMoh7Yk~an0R)SZeJu!dp8Zi-V$(x96E5M{%z~?k+vkYy?TZV00z*|t$GU#&fGBEXV4z*E@c0+p_F%H@TJPzE?i1kL^E+aZvM9J%bZ9Tv}(4KgMCT-fIEqU#+ttXh&4&JFro4#mEUSDjpgYBrPFSH-HFPQq+iQ1^fNJE<%(FfWL+z0#voeLvxvk^5cqU6=Uwr1dFXivOClQz}Smb~iN))Y({3Erehn~rEpUPo+;1V^H#j?f>#9l_McCe%hXo-pF15z~y%gN^vvh(QSA*$CoQ2;yH6#IvA-!K6dLv%tR~<{05X5YvA5qmE$~QSydi+Z^y5v>yf?0v-mYJ}8LyLI;B>i1$DTfhmZ08@f*u9g5H74@K^5@N67E@o}`7Y7r%GDz>cxufiA+$7s@KCfbrW6We|T&jd$7XMtzon4=KHtDz3?YVdUEG%zWh-|5g(U<%?H&=_zGYMg<3qQFtu2k{akXO$5F2KP52+=#Z&24K>1;I`mKhzds3Ll9FxGc@TpJNhRtJGNB-S3vvh&~o7HVCsW{cqz02n1a}0=vqxQ1fR(dL2fuW9LGky5p8T1QSxlq)*oyGM?l+x+oIM81aS*!J#Y(feP{rfl*YL}bRC$2xD9k8cq3|TgL)#s5!eT@ZbVrlYD3F|YlDl?oH6=YXhd#{D0#WDtvt9q+7nOJq)leDB`-6!l?9i@zKIuU(xxQZl2;Pjbg+(^N<xc)OM<D7MW~Hx3^VjQBicdhfZKtCjhJubMHx}VB1&EnY^wvVgZ9MpG-*>9ZOJQ)ZQp@O!@#RGY10I4$!mgbVc;;-)C3v~ZUUx0R--nm(Q0TVBPtv54KzKp68LXTG%bQS5LyWw2rdA%f(w9WX%fW07&==MEr`$L7esDlu)8MW5oq%YO5Q8zH{fqj(<|*ib-zLok3bL)r|$#kOX%NVQaa9;&_Hk?j^`!vh=-w{0yxIo8vO*TX?LKvz<0nmjOc7cxDnT&H^4WLa}9bE+zD;2La%|ZA?GUeHrR$X*P&OzSCMladIx+5`@W92fj(?ts<E+gd_hLkf|df;0v9!6vXQsIhzu4{@-kpsDR3#YC!VWGn{UyUyl=5B2u#`-yj+tu)zFr_YS`8o+!!@ggBAr>15+Q%Q5)4*)6n8Z<b$RL=L07<VyKZf(TL|z@}5IegHxkD@gz;!q(j^1U{cCShuoUrIcQVJB1&E%Y^w>biJA&QlY<L^sgF6RiE7MgXi6jepsB!q;Lk?RU?avE@dxxXn3Qt<fTjcwLYo)RKft7v^8%U^Y)6|<&==qrsP7Zh5A27!J|RA%4?CD@++pObF=8ilEqEt*qY<Z#yx)zOXAvcD9=5FouSI*}-!y467j4O#i*0Mbq&vVDG-<N|ZOPk!Z9Bj_P}2tJM(_qO^>G2UQH{F{U1!8@=z8#O@Ma@ojl2Z9#w?=bEx@+*;Pq%vd`6Qt^U;>P`PjA&Ou7pkuSuItXiMHEY}*Cig_<@&H-k5UsgHQnMm0_{w388&p`F2#!2@Y*jl6?Kd~XpY?|W?P4DO8f#J_6Nra9V@*BskAfk`KU4`|Y60NRo_0NW;kC!wYR(1G9qVCv%lYNHwt8*#*l5yt1PMvO6{3xaq&f_Nc<cqxK-EVL__v>SLV_$R~!BNicuX}>#A$B!0K@_xj&3E&B6|0A>;_(w4HK|#C?+7(PeycOC7OhLTG(CwONcYG$lJ95W^$K&{k524L)izs=+v27uEA;yUKm?mvTqb+%(v27`MG<XSgEO;!Ac?p7eF?11lF?b|&1elc0??~uTFa_}_=rQmy)Hn+DECDaUK8WiYQN@T7&|KgW;Ea@K^fSeXcTn=)L34p~p*``>nzYG_w(r2Cl#>^^b-|0#ri?|DyfWBU7hD%Lm4RjimjP2Bi%}ER_>U1O47ONAbAT=2C&u=%bnO`N5&8s7N;w~)DZoR}<{9)O_#^i94EhiJK4|j*`V9OG^*w-6O%I??;6FeeeGpGjV}2v2v=LRI4Z&5x{zfd*=>Kx5X%#J^<W<DBhTw*1Pdr_dHrddYylmK38cdoWJVBE-$<UU(WZ0G;oF6qMgZhJ$fvJxPsEulTYQ!5OzCyEFguj9x8~PL7FOB#DeGGn#oG;Kf@cX09Bj^|K7wqE^^eMO}+PI*Pz>kpQf_?>m#lBsL$LOOcm}<;o)bppId7yuRDTry|x3?kVjkpIT?;i9o_@sY=duh_<F7zJw9&+wNY2U<S(B=d5F8D5TK0xz;Nj2~X)G-GA5L1n541H~ACg{Il3gY)h^fh9%5f7p7!S9j(5c(P%i8lA455W(Sb013kCLW14Z=v_W_mT4!nh8w$9yxDO$4JC`)Ho9NMY=!InggvL&^iLG9nm@vtp~L>@|qeEYDBOR^^B;GAPzzh*G3T6K@c~A27^gkfSZ6r5Uq@8iD-rWw$Y@Hw$M;;D013DL%<>Evn`?p`e+0G9vTe(9^4pOAKVyR*NB?XTG0C7`Z)et(AwbYXj21P3tS61HK29CI@){(tpToqobM3Cji61yO>oSO5X8-)Ey2yf&7h&+P@Lap&<5aU;D%5g91?6vmOc6Z>p#i#pFdiE*OdQ2lewk(^SpP<G9|VD{8%3noRWX@OlJI#ZZdP|tZ4rOF5>7m'

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
