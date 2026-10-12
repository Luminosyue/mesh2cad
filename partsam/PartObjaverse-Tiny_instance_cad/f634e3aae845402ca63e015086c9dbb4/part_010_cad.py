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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_010.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_010.stl', 'source_sha256': '51d34d44b9d934754b37943cb962bc3410cb71c096cdc4b3e7a520849b8b7ba0', 'input_faces': 1388, 'input_vertices': 930, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31122010946273804, -0.49999988079071045, -0.4056658148765564], [0.27939289808273315, -0.1891596019268036, 0.4056857228279114]]}
GEOMETRY_BASE85 = 'c$}rY3AjzwAOFAZIVeL(lw>-F%rha=-DIXrh01V{qD)DH61&nUWon{wN?#QXL?OyH#dR<4b<tc$^CTMhMt$qI-~01k=kB%a|MUEx->;tc^M0N8UDjTEtv#;2&*|SMUaW$W|7xh(%O-ujYKT%$8C5~uI(F)`@ngo`++@;}=~?QWAjf~&7hZnlW&N+pQn#u*>s~wd<}p+2woBCQa9!KFjS_XQn>=;e)KQa0PM&)0SmfPDO}KfipWi%g)ReLQ=X#g4Y}P2zvVNn)U5Wq8|4R8y@Xq+DaI^2uRc$|oyK3)8n?t$U+e-4*UmAJ(*M>pvEI(%CsfVivxi{g2nIEsYCn{HUOYMoO$D8zLUet1(p}*#Z+v!^E_s;tFppmn@&K)aHfAsH;pdD5{>iQbrbPDGzuXC@2l|S*%j%+Nqgw>y;|2-I$dn5LI6wY-&tH%!;x$bB6*D)j4{p@TxVdm^-JJ<be*Q5K{UT&tJ?e^>bWc$@S%L{_f7p(j&SpL@?4+Z~jgPD7krUmsRzgiUJ=>@lZ5-y+q(#&;vr`Axjo=#&v*c_3kCR`AVZ@Q+LyPGdRfO<SD_vSx+2zmOIp2l+Bkyi)x+qpNsMo@p!&Yv3+)bH5!ESe|vANnm{miOHk;q`T_T(57c%tt}){`;>{K4ImV{u#K*s3$S3r1X!SPn;_KGr-K%3olFmSh+JlJ7~X}w8~g+di=qlJ$CMnTrT_FL@QtPX;6RC%Dv}G2lXd=-<=;G7ge&|hnpkv<O`h-1k3Mb=Faik3WN4rxf(X*gP?!L-JTyFmt?9zP`{n4`U9l?>#cmm15&@0I|q|N{c3bwbA4|a5%j;Erw3I%7|t{O-~YJ}qVnYQ&w}=(Mw#_^4-N|YQ|G$8`+E5xcdhd7ibaRQd1kry9SCyot#y0D<(-p@g7(;XBLCY1;XJe579RK@Do-6>ZkE^k-P;d-7?r2a{k<@pXZE9yZ~ZVTPybR(>R)TMzj#&Ip4Xb~aT|PAXym#*J?a~IX1}i0KFD3W{wBGH!g;12&Mf_bk?Z<@de6u+>s9tO*?uODmHH3O$qD?y+k^G8^W@#H6-MQ1`^x=MdE%kp3Zim%+OM)5Ofd7*C2b>f=g$dyqjK+_Q+ZLjI`hA~BkNf(J14T9arf*DKHK$tTJim;+&hup7FmABC0irQe-ZPd^2D%po5Fdz<2WgQ=^w%MfMb<U&hNE8Do-{3Yi(4n#>`z6nSaw{Mc{V-{IlZm?1<d+{&^+XK5w+zKj4;CQF*%ZS8Jp4)U4*~qjIPB(oIo$^0gzIgYDMJ)uzT<BlBMlY>UdB!qV?Y=E+-khVxASxBEW0j&iK>-t=GcBJ-oky-~Syaf|$@JTc{`$UHUs=Yq(5^MCdS<6^JxT`v_z<%!u-<v3jVTFFOEmvI^Xj9fo4S0`sl{bLUogmbsp4C()gb@Gk!=iDyqdwjoKuj%r=@0Rv_QekU2S8MK&{N<7I?=EEdmuAZ6&f_+Pb6q}F{#DtYtvsEzDA=ylh30ad{bz19a@L<}+F!P-O6Gd0@rnF!uIqP}4$3idy}m!cAB?+O$?P|0)F%buT=#S8swZSzaz;z}!#8leu38k-f7_@aPxiW2@-@3(3I4s6dyg)DMfS&@QqPwU$nmr5J950Wa;NXV`QhB_bIq=xJs&()7|xwjR|R?c$NU1L{L4dwTpj;ye^l<A*~%<`#F2Wwf2c4jcRu`ke`G#rcVs<YmyTvWs<qU=VMbw8?hP#+nI~(%8(B|sTOYapzEN^_-u>J@AKV+6Uso<SDtB&KvNN3P{!IK+E<Y+)ZGPMvnHRj67nzs2F*hpr{#z#}DtB8PG1`+Emv>9$N9FF-f9;LT`#+HvnKzx08<}5JF()!F_CK>ddc3OswJ$1nuel&H_kO!GFS2~Ir*k9A@BDjLWWMGC`FHj>#!qdF%zv)zh4aj~Y+1P@D)-7=wmq`^ialE*%b%JQU4NY~HimQEpX%t69Z|V+@rdn_<v)CPOH}UV&Ge%3^xd1y<?4RUc6UVO-q+K&N0zVm!j{PLdzN^SdCdod<vR9$H)Hdvs64f##0%kEAGh6O?)q@9`!lt(#)hce{cp{+QF-F&v8$tUZ^53IqjGg<;IeS8`!jiC=M7Q0Hz>X~Dt9{Gw>m0M^m+8<$nw<|n9F5<rY7FGAu4wV<gAIx6WN<rN7mE*!k43RRkOs4fm`E}yzS8Q*`Zwbk5jw%g2?>Mn#-bcHTl_>!+B<VKGJtqRPHUzogbCEr$#M{EMI4YSwGjynK0_^$o!G7=0)Yne-18-%2ll&UqbHPVD?YqhL=`F<<3`Sy>Onn4*7iC`f#4<p9d~m9hrYyYHd`We5>S!sN5^Rb7N#Zzm4{ya_9LiTf%u}`)oLIbyS}2{L`AK+`X#)hNwI>`K66fx!OL}i^`pStIhW4{%`!!>Zm-Ky?RY#e$AK-k@b|DvN1B>@t7BtyVaiv+T&W|>z+EYEh_gWJhn3`SHp|vhV#t0l<d4cGGD)RM^x_CKfE(4_kOuBC$gUSNMpH~@oF@1dsOax``C`i@_!xM8I^lgO6Nr8b*7lh)&2bG#O+bJ*LvEHsN7juW>;kS_l`y9b>{}lb@YD6>u0aW$^581;jG;s&NJh+bjIFrp6UNxPvu4BPLt0g%X=qF=SSA_?e2nbuCK$>@g|XZ>e$alJ2U;<<Keuh+#PUqZ)CoqSbkKV?9`?pDp&osN9O6m6J~q#`2ILKFDiEjmf07TdlimG=IQsk6-3sbSQnYQR}`1~GM)4O$SHit%ymC}eXp78dfvKK=Ie43!Sf7z-qp_aysOUbc~?8v^RCLON6)(|tGu3f^>$nB;k>KP?Ri&s^GtdEWX((4xt^DH-?MVgOFLGs=cS#$Cdl=>HLq^xF6Y&qQ)aH`)s>a&d3Ck+?7Z;$svG!Rz{>S=0cVYs^SOYsa{XMu`RPP%xZfQ8T*J=!T*LX%%=L2(W##(0hIi|`xyEw!bE{jdTt8>|@*$%hUEVot<t(o{e7-w8E-5}&vhy^bE2;KouAeJ;?aW+1S8{u8-W?tn{aoy{oX^GFo@TC}i#b-VpNpxSZf1M9zG|11>-DWt)2xT(y$h{e_h+>`-U-%EA7>io%KVs>rw$JY@}!j~w*OTSncs0wkh@my4r>(LkEg8Mx#&8%|F!cUH{?a;gLekwowoDJmF2ut-OSYk^`u=^?m2RQXXol$xxaI)+^sM7cS*baKHlG1dAhdT-`Tl0S?*I(R-PIp_bHy0JDue|C2iN=Tkccr+^Hk?DT#!YUnAG~j+J}&%5{Fy$`hyLI^WK{YI2?LT6wyGTz{tQ<#y!tr=4HL>rcC$v*r3TZRKjaTz{$>Rz20^`ZHnW-p6tsW#{h2avkN^<?pN#TrVZ9T%A)^uHWqC_Su*lm8&ma3(oH;yZnV$2j_9m&WF?qt~b(Fo|-nJAS(CXJ09e!rZrxl_9=|YojN<@Jaz0L$@Trqs~^e!Zsn;ryUPA<=Uq$fkIGe_TV#K?>;J5s?C)0Y?Cc}^yPf}ZC@(7amamlk-7a6Ht?ci=TID||Bg?mPbxh`w?A&cF^GJ?e{v(-3O4{}B;XIOEem3Wk?D{9ld`Qa5(^txTh-c-=Y?%*9+j&2k53zH%rp$*VezV$>EAs}9l{<4}-XLk`CuH8h&fS_aZ{XVX*O&X>l$Cqgy#KZG<PhHf+VxMA``@%(|2Db*Rli&LUb+8GSh?F!?$_+x`9|*79J_p;lKtJTzg#2P-|g~CmgYv~PI|ZO?{+<#vSok&-QGT1$^LHTscw@CqH-s@m^}ab!^&UlR2Y?e%L`?HU-XLPyg%~3{ZjU8=9zhtL+1wjwQJ?+Ntep}xs|K3-^=x`l{>%mko(2Qt$eG@8{4@mFZ0HZov)O6<D{Mc&3R)hPt@bQv6Xu{GXI&f^3+M0|Mcv3E|K}qw7uLXW&YF7osT*H`GmFH$};blv~u;j%=_87cZ1CPxmKQ@E%RL|JO7IFT~_X_;e3~sr^?BESK4mRuQK1Ip0x6m%y%WM+&e?&VeDM3lX;k=oqyF{_9MHV_@}}C;#qled`H<YtUOUrMz;T_%<VaO_*2==+q`P_!_<zlom;tAYEp2XO4;R)x0mygo!5CbIPa*oX6_c3=Q~b2D?i2gA1hat=Lg4)l%4<BG&nw_tvp$LoSfg=TjeLV3D!6HaD(8vZsz&>4SxprkI6^PT#fxLxW7mbYiHz6zb}LP`SeILS6vSU^C1b<(a7Dxr-JoO#mwB<^+>S3>1Ekw`GxYHM*2l7zf0bKNO$XE*7JK-(Eq6(X0AF<4d&I;J+1uv<3T%9kMuD6AuaEjBpx+$XQjMHk!adm@|F)tdv04V>($)KC%hW0SF)h5QBS%_O?f|UKXX0L`N@N_zJ+G4c1#J@H+j&kCsDtOypK1npRwHZzZK+tGo9=8>Tq6RRGw&YX|O#fZk1f!_ps#aD+kYsQg%M)r=UL*x1062jXD-Y<%u?BWqZ5bY^QVTY<d5!;y|N(vUdOAJYwh0@h(B0sBGq`qaA|%`n0@S?;uaVbA{Rem1fHOf6VoIxeITSe4|-DF;?FHNo_Lo)Ny&wCvD}bpS;hLe%Gp}!tMFtTrW30_r@Sk4Id)qr#~v~S$C1VH>`8r&(((R3Fo>Vb#8W$Cq|g%oy(ueF>?05*L_HETuNHyy<xSshV#t4?#)@jdt522y!!ruO-8QkpItN9kJ5JiP31i+ooD)CLvD~KMw;bQ%_pr0=PLU?*-i>71$oLYU#!!L>`<=DJ1_naya$rD%6paMJu97O+Oup;kSCH>{RNXZ8M$8H>E{RM!K78*8&Gj;IM2L)GVXYAzDrr<)ur=tj9ed2+V=^L|7okdQ@-z>aIV|$m1r5{iBaZum0n#v*dJ5sYAIiDuH>%{lJi>D)n@%8<o&ut+{_a_<$be6F|!`$rOV_v@ZvDDo|0>2-0b`_c|TC+x_{I&D!8soF1O0>m-o<go+&^7kKj2`qQ^+He7jDvo&Pw>%-@&y4AVMiKPO7<4)*u-PiC(ESRL%w$)C-7)JA!aE?H@^ng1#8Hzq5ax%acYU#IFc4A#S*XG_#Ib63x^6<!|X_B@_*z|3{|<e*(fJ!w6!XyuuC#VgEQ&nu>^T+b^ex_@UZSI>(&R<7qoogQYc=S7oNuIELapBDt@PkWv=dBn{1`g-pBa@}Oj1FL(?Jky`Y|268-^U_H>=e%_CgqiDkY1hv6`}Xfu+!bD~o>xy;d1hXHvz2pR-OlyAdZPHPyTap=(9Z>|Jo8+jgqiE-0!b^^&jpe>59~6=ML*ZD@`Qe_vD?fu@7r6sey-uYS4!R!)bmt7r{%qID|cQVEAOXmHgolTnf+0DYT5jPs60LAlKjYe9-FZ*DtFG#&69C4bN9Xjxly?qTstQ!clI>i6<NNs%p0Fpp7X}8m3y2wwsS|%8{6%?i1Wr)o}41{#;4VDh0Gh<d7AUap56YwGH-0>$+~>M#k0zv<oh00o~kPIz;^C%9{9BK9b_K(w0x+{13Pv-oCmgZZ=1{m+qvRAu${Y{2R^NS&I7x4`7JeeMdeQK3v!}zZ~Cs>$a-R%^CIiHcgnt~JbhnFc`w)QpJ(S3MCIzs68oca_l1##QMvc+$8x`Xvb^Ma9%<rHnFqG=RQ`}4cda}*uJZn<+?_VNAhLX!p81jGzew(j${o%xc~<TnT%Q}2yTzTHs9aS$cUM&Ia31)y`Z*7*PFdwS4{YaZugnA6d5ZJEcAl6d^T2lQ4wiY~)9QElUYuRNKi`Y9ms?Bbfn9sK$7NpE&XYAbuWRS^WM22QdN{9Z=iXq>>sonw0^e)0%Wvg-O?JMA?={)|&v{)tSDe>Xe_7?vEwL*qSEpL$MCI=8S92qC&QsaBS9ry~s617oi@Y~t=aXg@MCI=2^Y%yO-tGZ~QF-$EA7sDYTvu|=gSq`r%K3MTnWuXHF5jOjS6_0z?~&&7T%Bj;yIS2<5Y992+q_Ua*xx;?eB!zO`BAwVIdET8?zT9Y7nM6#uE>q7r~ZJP$h>b%{9LPk&NJJ&!+GY@a?UfKmUEuj&OOdEJ64|D&G&5WdQR~@TPsg<p4rY5Pw_olyZ%pPp4qkQc~$0<?L0MJ=94|UJ)BQIE!XqOc0F%$KH16@=acQ+JI41X?R=@sC#&+-cyT`2&b_x~KH1J4=fuv)ylS_c$a;D`C-1pgxvG04FDiEjb>A12J5Tk_kIIuxZYv1qdVfhgTP@hHU7hRw?h|=Fn?5Lc=KIBbZ%XHx?+feir5-ZNt1I|D)<b4_SHCy)fmuHD-qZ(HdA>K5u*&QArV>_p{oa)7x=s2)e?R?f`Cfmbo0)s9H-3%p={w!6@}uPY?B4DpL9V|??@r|J66l=Yqu05!$13m1_v<scF3&tM_*dC3ZZDY|Zl^QE%+=9%f_5f{TIJbJC+C#e{w)4JL#~;7!{z(<sSd?<2ji@NpW!9>T?L(Ies6(!BHJo|N`4<e=b7@%)l=mq*S`zVMt+|`=b7JaV4h%}Z1==IqaU6&^VA0R!(yvE`@vmoE>|t$?-eXIm#cIChCRqLzr(<OOW3(?&)sI8T*da>W0lwKv2xx2DqTCsGxNr)FO>b|OEXWrT0yqMnRRwYZO`dhW}bLP+N18a%4fEdM$$i=Pg6hCl=I+jGj~2aUyd^qni}nK`5eTXXy)E`^1MU6*UZSB8<z&pFLa)nKTLY^d}^~<-W$0vIDYCpGyi<$TA2qa+rsRhMe-a+=eoQzYmR*1<Q%hndWJmT(YY?4y8h-MS8H0C`M(MIK8uw*`Nx9i6yB9>%=R4S_lO6Zd1{3`-%&5Mm0Zv39;y|T_pDsyR+Rh4KQEEI%6#en^<Ct;h<T=eHjU?fhn24yF4v8x%z9F9c983?UhU2Pzq5<Xx9D6yCmMI7eE+nMnI}e%mG4*fvFf>{gB;J7bTGCnukXb&U&K7qZ;v-GjLOyT@_QVv&UL>X$&z`DXRQ42ahd;o)?9A7d(#8qJhOcs8CVdNCmw4k{qu82$vMC6{5@RmD|N2N_oMMa?)+kwPo5Ye*U!J0<<o^@B=3|h?c{TW)S0v8dX;&mKlz-<$u{%k<@|nkwpmX)HdF4?A9EzneT?(@!-C_q&NJ<AGe18ncN*R#$Mt!Rxn9c(*GA>;kMg~BooDv<{`-RVyH<H;Bfqz9<%vf&t_|mz=YyB53)a_}Z?2bnM*ltGJafFNJ~lG<n$HRP$35KH?4PNx$-lF5cU<xJBl7`ux5{?c*=WBvZNVlZ*W=Ypo=>SS&D<?EQ~J%yor9MJ&ztN#!RJcumu7psZk4x2<!boJ9pOCF&%^JK?_XQxo$H>L>x`C{n%ga(*LYU$_K@c_?(D8+`@h>Pf46d%&t=^E%-k#B?*P>8VU~ZRzg+LwIiIt*^{o6Id2XUc_cz<a=O${5nY(;$l5ROrt}Eha8P{X#Vl!7m<vg2cZI##O*{?mRpVzBN{$7gC_4R6+zl)N|_45?|{)x^r&q4S*CrPV*hrhexTJ?MUeHGWL-{bG7xK{n@sQg|^@*A@r{ktfcT+jdWcTseH+V7%#W42TAcUMwYu758jWiOY%my)uUtA8&gWi8jyzn8LiNM5*pegC3!`~D?imDl$#39G!me@W~!%j^3Wo!j>>j#XaYzc^O;%=bP%KA9I@Fa3PPvvU1>B=w1z>*phBE6+S1d9L)HaDVFOJ8G$!r}XbBS-F0`lSrAle!i3bX8azbKlS%MzBTg{pHHdp%v?X8N?5smKIOfB_nvUSCHZ{qv|Rt5)f;B6pRb*k^ZA-nYooE;w0=HV+syUzzVy0ZjCyo=wZY6Y&l86)-fQeH`uD`FT;0I$eT=lq^ZBNoXTJB*f5Tp5T(af)tY_tEKA-gln7MvFo3?WOeAdfvu`j&b%=+#(bG^Q5=HPwCa`p4*S!SN;&tiFU|FM6kTyOQ_{Z4T+S1){a9LM2w2{ZS4%5gY(z2u3kT~ZH^=gDzq?(JJG_i^K`@;siWwtgb@-*mrGPimW)d+Vg0)OM@9uIG*;vc9X|GV8h1%$;Xg&kU<P>q*T2L*{pnK5f*KSYYOf`BG0}p;cbjbLel$tGsO1^MRQ=vsurFR(XBC>rhJGGdi-|$i0E(f;_SLKW6^D<j&yb#&W%qwaoH5pD;McPn#c@Xy%EjtAciVR<4(;j=mjS?<cpsDEkq&E7#8Vd>m|7>X@0k+^(GClBeG=>+$TI^*ATYT-W23lJ7x!y1ZWB(q^7%|F&I0p85Su&O2pt{rj1EK5DyJ-qG_>+s*Picc<jbe4#y$WaXK5-ei^6<7?%ad5?t$<o%u9XY2{rqZXNYX1i)|Q2Nc9r_#ASPvtf=%PY=D={)oMmU^D*>yIQadyd(jZ_GTiUe2dd|H;41{;~2*|8%y>>v8O2m1qArB|ewsTJvT)x982=GtBat`K~j}@|k@8VHp=|zAKY2F2BcEFXl--f2Fr`tDemIGS~aBo$LB_?kq6tPtM`~vcRlgEnE4uk?Y@6W$sz^WcDwsp3FE}x$b|RpLV=jVD-=cM;_GE-}trP#(%FIIIpu(P)SumT{kN9Q@;rDpZ4gV`W@fu|JP6bHgDOs?f=_v{g$c_Q>wDB3n_3DdQ)-}@<nm+`f*_h+>YL!4DUy7N4}f_5BAmD*QLI?&|8takXz8}kXw*z(qD}U*CelqiPt5sAlIS52?|_|0@tFyO0GqIjgIBL#?RooY(pz@UGl~BOUW0Ld(eB6dyxCmyO8^myVF~cyOUeeYm!@%YtgaJwfGsllKoJJypmj#o**aK7d7eUlHuo*Ym!&e8-(g?z~#bg$BWufn{9-53bnZt*9kr_w2lMW2k@bxJ{ihBgAWSz;UM-gJUi6q*&Gviz0erd<2b?_#)`(YA;%nEF|-X-3~eVB*&h|?mFX49mB~%%4arT(^|{P?+*j(eJ?-h)<o4u#^g-l)<iYfz<iX_2=>y|M`x>|%y;Hnse*|AduN^Pim%&Xqh7CgdeghsG8gT6OvEqF8$N8bYInP&BUsWh@GkSA!GjgN2c=Nb$@Yz=fdPg#R0J#IXKLsA*tB<d4zPi%elDm>y)0>c6lN-}l#e^G^Uyq5`C%;avM}ccl;OZ3kBKj)wMda0VEN?YGgPXDqZOKi^m(aVBFCq7$_aXNpUq<grzKq<H-kRK#+=kwm+=kqMj&*Lp&)_%M5B11zkZaRxkZZ6nYSYV;;TMo=li#2>3f0+&%Y`?L7qy`w+X#0;ZFaa$@GC;=cm?|aepRSXu413TuMG9!mF#19=TM(_=9s{ng~q5E#}VE*Ry3xKIp*+6p>3d2XgjII{y2|bm0pQlmE4@(nA}`5m)VT_N^`cSBfT@ZBY6P*O7Z~m5c*Z*A>{t_E8<1_8n^@9i5KmU;70U@@uGbh+>B$`D75c4;<2F-$6g;RE?|FL5bB%C{xwo9Uo|OkYkC`UYjPiYKXM;(-7N8XS;FuR<htbc6u678*1nqgYD%v~Zc45}@2iAskb5fePUN2C4)mtv4&){jxGn|0hypjHcOo|=XVd$Vv&omy(Z0+08C;ufZbq(6ZbffRZbfcOZ%S@UZb`2}Zb`05$2!;KXK*j}LkDs%az}a-az}CldR=l|_C*7FB{IAkxdFK&y+x?b7F;I0cc=}$*-m)FtfDqI<T}B#L+hB$K7e-(^+{Lu8Qcl=p~F6gHwyK6BaRFFa#b`&mvao^Ekk44l4B099@++~hqjaI?2pRyTJ-AVTI4qLmgF|%e)P-9{mAv$#zx$4>aqPD=nlC9xeL83xeK{HJv+3oWpn?_W?$?55!{Dk(pwen%iz}Z7OH692iK%mQ$@#$YV40{p}x6L;T8?wCl!HP(Jv;qB6p|vAa^HUlqFs#OBmjcd=dE)3f$S(#lD*OYD}+2ZcMI9@2rHYk{u;}3E3gHr8g$GB{!nLbtrIc3S6Il3AsMGJ-suzJ^4~P+IJ~GgA;6X6LNywf_^c%1-T8qF}V%7IlU^mIk`F=>s+0m!Clx7ZOL88?dXlj?a1}$b;xzt7xm~Dkl|Ix^~mk$%|dlH<1*o0Lv85FcEamt6}7oO*9qP+w2mFw2k=WneR3)L4Bjc!hn?8R@CKniZ@_VZcT+`U)Qw{ZZyp-c<{Wc))zCIjHME^nWq({quR*U$u0g(--kf|fxd*))xd*up+t`5nO&zws9laB|9l108QgUbVCG?J=eXS$+zmDu{y+4Axb4)NcdS3>&qBm1T`#v~9ucC^M6;;?DRYHA}^sjB6^7W9fl&{gg9;W6p!`~lanTN>t(p@q<KPC*{PKLl!Sm$ikJC}Sn1>PSMpGt<n@B8kX@=X<^z{TlV<l^KKbVV*fK7)QH`3!PNdTDY=aw!U2hJH4=4EZbyd_KJ_`FwIkU*&yaitStqT#kMoxg7Z%dPQ<Y)&s82{@oB0f0I1P&nL%aJd@<7DDacMo}f>sz{Ba2$?!?!;p8#C#?!B(Pa;p^^1vH$@8tVCY!e*qt<Ee#M;Y*1j`2o%4c4)N>-7$O4H>?cyq5nCe5e2K-tv7$Tm*hQCgZ*>CffykbF64P0T-jc9V^<d-sZLje~S!(W8B`r@A2<g_IvyczAr95gM1(Pemd&CpT3z4f#=b;ktg_?=xd~}XMNq_Ybkvsc_hm$<-WR<`|wicqv;dKqsika@QoCBEPW(-hu@ZhnCye^ll55b=a}wip5Ry~xQ)UKxSi&+%y#+?@?7r!k5b@!=&1J|`n%)>{QE9`M!t&zpT~U%T#@_urdZK&U{k1n;j`$Q$T+6WiOcZ}K8p-T8JC|oh1P2mw^KNl_a?n083M1Nmmx#owe<7J=X0N5%XN5{+xxrhdobF0ldmNdSRYrx`nWljV>p$$?)M!$Cc}|W;ol!2kMMOZw}X-7vGg0rW63wtuMcfY*K_-Vj|y#Xqqq&ur7xk6B0oY;(nrOMj%ncQ=+~34Baf%wKpsyXL%)_hhCG};f}G>`!&YC9#YJGf|8C{}jeQ@UMc+z>z>1zj#(&^5>AT4gxHLVN49_D&;Irv_$Pl<JeJ2?LpTqMA+~a5D9tD0NE&|V|?;%6r=jeH42>dKPmkfay$3@^L=)1`fcp*K9oWuSG<NUZKR&+ju@8ahzp?w^@fX4ywgK-gfJ^zln*3-`=L*RAva^!OCr*#zguDCe*=q?I8ll~wXj(TU(*O9T!+|TU@J}+LhUCrbA!WWVCx%nyjLh?eE(dY3++&>;6&!NvF&mrSjg=6XS@uFh_I7NY%QqRYW#_@TM^8?%tbl=Wrf6wRN7to(4KhNdqaRJ}MenWqtUxxX9i?3^ZT}{840#BpgLcZPCGrn%~bu0aG3j8$v8S)$0=CObII!3P=7e9v#FGGgFmE$6C>9`1d#NVm!QsTqu$iZb;CwMrQJB*HYfS3E_@AfqzCIWY*4<W;ck|A)nm<T+Peh(P}KS6(q41vFhiNGKF+M>jF(qAG&;5_<0WC&b9A4(p|HiIE>z7m0R>35SM@cZ=T<oDSx5BvVR?_c@4R*Ar4lnCr85%??|d*kA#V&ce8(SIjH;Irc*a8_Id{)1()yg%p<lOJZ={@}lXKOPfbPF~LO1V8QbWM5auMBo<mZe$4DlHQ#Rfv=%YAw%HV^z~#2{7p;*{@&LkN_-xDJsAQoq)#D3;3w(b$q@JndN(ozUO=BrhQN=~pC&`#>Av^(H2~+sEb)RYVF<i8CIbHu6M>J!MBsxgi+_KRKAk+B%R0z^1HXs<H2G<c4|s{sH~Sh96M<XPdyye<8+vat1RhDBMuxx-(%&IN;KG;)yxZ4eCH@@!9Wn%dkv@$KfmhIblOgac^j>5Lyo`P`83I2`UqXh!cPbJ1OJ65r;t$Z5ke9Ikz|Z=8o3GI^5x5=wGBN~iPrsZDfydBqCqv*z=$pt8_`{e8ye|tsi6s64eG?f1zf8ZK41r&#UrvU=uhB0fL*SR_w~-<6^YmxQ5O}5%fq(K<GA=$RCjKn>S@s_|g>mq8T}%Y-L?1wg4<tk2?3f6AJ$(il0?(sAPlmu>#YEs^zE&ymwe;u75O@Q91{ngsM;}NY$Tou^@ViO`UQfT141w3sQ)CE?^YC3{oQH9ahCjyhbc&o}|A80#e3P$XF%h^Gy$2ZrUrg^whQPz=Q^^qcKKceS1pYB50>^xxtHkHik%J-d<MgRy2>dj?Cm8}iMejj|z>DZNks<J7^u=Tde1{T&KlgP!CVoGCF?lij4?M^({~5-ZeuxZ#aV~m<jB^prQ}AEthsY541pPBI^cmZ7ocuZej%9yNzk`h9DvqHC>D$Q=_+R=DWC;Afm<aqMKf@oQKSPGVN%}2h2;7$5hYW!)q4y<2;8FBj$q@Kq`bIJY{x&88|Lkjt5>L@Lk|FSN`mJOL{3^XK83M1Q_aQ^z|IlwCL*S+KXUGtE2K`4e1Rg^Ffee8M)3=i$@M5|?PvY4AewG~9am<H*K!2YMfiH-QpAi#=z@_3M@Gn`y@VWf_92o*%OP@}Lz#ZuQ$Pl<Ay+0WOkEP#1hQN=~my#hc?pKbHale9l2>6?H<X{NAj(!Ij0&k-CCqv+k^nPRr{5E|$83M1SKSzeZN%}8j2z(74{S1b{SJN>zS93fuuHavN-sNkw5`jl45qPWb+k7oUIr>a81l~ixf(#!-hQN5obu;-L`dwrQ{1*KMG6bHbMBt;o%EZOz$HZSCL*Q}ryT}mOp${StVw=GbxN}Sd9#5Z1hQJHx%g7M;)0hanpMOW+?Wb=gZ)M-^=f8n}Lf=J(|4N3yXT?QeJs}SMjb$-@zwvMIg)#9L$q@Jk`YbX8?n1wk3?EE}z?a5E;2Y^K83He&|A!2LaqkF$aqs9U@f~#JU<kaM?vf$!KKfwtV73_yf%hsAIEOxq41u@PUnE0dm;M|1H})+!?zeM~|9PYmfk!A27}svA$hdaHbshXLeGeIqx(-v|^Wq{fw(&CLqb!T%9p$oTkq`U&0Nb$=fpNVvmyGKjTnoXE(vctKXYfDt!(<4I`;U`k+<)NS1b!v`F!?Z-55CG*3IE>=rI#i{V4Odfka7O}mVRMe961;QSEQF9LttFXmn7p_9*$*$;WNp<`(Dof+e9S-PoS42-=oC;$`VHohQQ_GB5;+s2waU`j{GaV6didf{vGWA$Nl^%-%n(TugDUHj%Uf=A#mBa2>e$}{2OxdxcJ#IapY(7Gx&2Q0$;C0;Opqe$;Y{DFa(}MUqObz2kG~dA@E1^VPpvWnG%6NrC&pa-$#bPAJShTL*N5AZYuGQ_!;>}6gV9dfuE$`M~1+Y=+}@TaQB!9+=D)hJdEoLhQO2QE66K2mf+uf-HY=;miW3XVdy}X{2c=S920@}#YEt3zHV3Ix6u!f53nvU1b&ddjtqe>WcC#KLULvLByweP75YSS6>=r|ljKU|^7Jj_^5nCyKhm>e;#<fN`1_a${0jX^G6Z(%6Uh*GD18zc0$)XciVT78rmrKf<Jf@z_O;yCcUj_ZWeG#z*-8X1#cUC|6!{$b4dipk=hMfN&nKTpUr0WWT$a9>T$WtY*BSIY`et$-`9Mqr{tta283NCsk0(RmE9f_nA@G&-MPvwk7yT{rTkJb<1^>A8g75#!5?_-g41w=cBJfH2JTe6ShkhLy0>_z+CCAAz`eWo6`F~3MT`~mz)Av7=cs@TP&!@m2$3)=g>5q{i@a^=mWC+}!ejOPC51`K@L*VK3HRLtyyXidlJje49d{tJ_xe0s^&tKqg>5q^h@Xz$oWC;A55`llEk0Qh8kRk9-^f$;5_#5B9P~xZf8Tly+{B=wOewIFm41uT7N0A|L-<Sw|8GST)G}jjlfp4L&BClfKf&c64WnW)piNBpC41pg|B5-MDPmoKK&!tZwpG&@gek1t;az*;%<cj2SbdOw)T*g;%?J;qW41s@&iNG(>A16cLne-dU5O^?s0vQ4ip+7-}z_aLYliz0FfzemDDCs|VI@F)w|FX})f6_l8L*PGnF8G7zhd-F>^98sB1-?~@r^#t98;s-Ojx0G|o<W|f#Q!Bj;G1yW;%lwXXJ&~nAfHJ-n?8<wHn{@*dU6GFG5UORG4j7k{5>)RK80&ACH@aTBmaj2e-{&hm(k~wA@Cja>&Xy!AblJe0uQ1uAVc6g>1)Xl_(k7K#KrLf#*54q9sLM~-$cHN{j6Wu0;3KHd<K0783G@QiRY2wIJbdu+}`Pbo=h(p6NbQ(e4pa$O>BGgN68TQZ~C=l2%N=i3^|Le=yS=6{Ff46O@_cHlw9wh;5GjV=3oendxc-gOX+jT5cpR57%~LDoPI4C0{5doN`}C<(cdIP;FRy@#>M~UXXJmgEc)?p`Xurs_VeE?SCVx=;7W9i4HyD{6qEBQJfEMDgW-ShT%3ck!uINazT4NUK7UDnkPLypr;i{*;9ryoe1txn41a(Ofxn}#BtziCO75ZHxUV|QT;FGbaUTYOpJw&|83IqC4<|$5o-q-)7kvbI1lJb~fp4O}N`}CTeJ>Ul|C67Q|H-oG$3N-g$ngKN%%ALY)B%CdiHpFW#l&;SpU1=t`5Ad3^;(wv9Re?*KSYMWQ|Tkg5V&_t1nxsmlHm`NA@I%g*U1q08Q;st#ZU4x@{<(!UL^v5O@EjSfq$eY$q@LM5`mA>N0LW!eZdg;2l{Jd2>cbjkPLy-^c*q-9#6;kf%jtE{B^s5>jKC6!HdO;*0&h@0|K8P7lFTwiK8y?*UV1wGje?`2mXTBd*B=CSRVLepTG4rO^LuaE4hb)f5*?r^?eo?_hAtD%((c+WC;9wOs;w0#p%fPby2|lcUU$!7vt$`Ec)Nq%jj$RY%&D?fPOU@0)L`J;E(B7k>U4}A@CvJ`}fI;Rfre;m_zMllfGUx#J?6DBJY^$|1gi~AKAxFoi?7o?qL5*^JgH!|MC~VuFQ`@^zTzVc)vd8|Bn;z20X1){|9P;kQo'

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
