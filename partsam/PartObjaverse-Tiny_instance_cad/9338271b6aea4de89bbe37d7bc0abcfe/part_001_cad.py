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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_001.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_001.stl', 'source_sha256': 'baf56440c5aa8c7ff6e21e4c7dbfb238939578df6676d91f4170ea85ea23e87d', 'input_faces': 1250, 'input_vertices': 793, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17724153399467468, -0.11383000016212463, -0.39483898878097534], [0.21434636414051056, 0.3374382257461548, 0.2657228708267212]]}
GEOMETRY_BASE85 = 'c$}r2ca#*x8?Jko93_KF7%~C^5+v(LkSvHGSqB6q2}qC(EfPe2WJwA#5+vuG2Uv2>8HNmkqJS6(-ma>rdZ%mlk9+RL^PTtEcWbLFbyamuj}7W1N}S13|8iUV*Pc9bwzg%7NNr`ZzHHaMXNOPP^(fY*Ti+Nfo%F>&trOpCT(3d180$-`f5EoxdVJEoU<F^nN}rZ1SkzbW)2`inc5mI~<F4J?wiEultvmN<=lDI^x9--?`MFTp@}-LUO1)OpH_-S0_%EeXgwVNVySIt5{54?7+m6_kCmoSGsg?4Fm0T)+PM`dcRNv`c!uOZ^c$xS)*rBmXzjV6vt?*^#kNsArw{|v`zOP5+<?`o)$Bzp2t;!>P`%s-(k=G4<cRfz#^Xe9vKJZ#wnLgO%sPyd?F|#Af<G(pp`r*1SuaJJKfd}N@U2dZMHBF=+tlI0K%>SR7(hsFAHYc+D;Snz>f9;Yvk>$4!oZcz?;9s|7KA|0V_Q>?_?~}fNORc$)^|HErD19qUt)D&RFWOM0PuF*)%s1~a>Dw1xk-o3*I^};Kb4;e+8Y_LfTg<%3dig&;utVlkWzf9HdWDPZk-l$H##J(1xpmU_)odjFaKnkxx96Xi`Gn@wQu*wjK0mTv_RMn9x8F><TK+tA#7>z{hO{dG53j2HpFWoD7X0PJcA5Wcxn=r5?!t#<J0#sDefzJ_0-28bhE|W3zO}FN!pQpiQg@fWuk{$2Pw0;)vONAG^`syCdYvjy)=DxTf07C+pVyzrd;-+hy8UlRUbl9JHL_h|@2PQkW{>p!1O8kj%R@T^>Wz?oD91VFQ(ya@Eq&|j@rz|TUEjVnRQ`q2tNVre24+{2e&BG4wX*zQpO2H*-@k90%zx@VnLbRttQ5BNt;>~{dg|5oJ(b=!Xq{}AOwTvT>)IE#O25-1nchmI>J^$*V2f;@0$Jt#66U(W7e8&1`7a&5L6+}_H$yVN&Ywy@Fr=GI?<arz@qg=O{y#KQ<7xSeW3oS96qCOH>>f3q>X$n%e?GZ&oz(Z1?3aJv<haMT?><%Kn^#!o6G*yI`k{XP)HtU+!6(C&KXAcjnf}ZGIe&!fx01fE)-qL|97R?BgIY>ITt)eT#L5p3OQF(tsxJFAJnSEjAF5tk_LH5hw=7SvY@@Z(U-Q09Zyh*)Jks|aO)b-hD-TrZ4>VN%7L`79o%Gs2MfxTxy)VUvHL~7~bF2Fy-_7HZeyGuSHE#x|pOE#se|xno?~Jsn-3E8@`jZE$aW=TX$w)ttv5d^es@~#wr0-AKP~C6UGRk}cAI+D3X!>t5eW2O_<qvva<@4aneKMaBpL_k9CDph;KlZ4sZ=q+aWd5mBsq&|;eA44jY%i}H_^+8Nf1<n653DXM$BA`yxW~7jwN>+e^Sd&Cd(3r}&qvEo%IlsPdRG2?eunfz*N)2hB6N1nsYu`6|KD-h{#8$&mhCmdmcDOZLwVic>gFdR{lM(h^1A*;&*gPPFArAv3?}^$m0tV4m(!?qqKry!|M$N1twaq}IhWly8|nKuq&p?sXFxvbhi=wel~DU@--^wo?*IOGq;J1cRQkcY8Mn!HyA>nnv%sh<D*e(gWjh4Y{3qMN^}j1D+rc-dw%4CLSNg#|#m+?fey5*gJ}>o??H1a3eWm<;?s{^*wa%*h(ZBz&^nIgi%JTc_=2YVlKlu17)sO#G@c7~5wPd}*+xnb{^g}5=Q|n)kNvdC-Em7&0RFn60u=fd%?_aW7-WR^d-=6fOfA(DU<IyL_Jn3JoRqOH5rSiTAbg3?VtG-Y9)gPaT^zA;2WP93O2A_)bL#6Y}_VF$K=X9iRj?eIt0+gq%yifg^#+{7xtsge2`|+=&s^81sTOoDLKGmKZil2=1eLGvIc00P>lir`Wo7x{-+juI{x9{Il<Kf?`9zPhmEBoD_r_7m1KRiDm>t$8gdOFg#e(5Re6{-_D>$&dnd(yW*sU>~u-8gmK11Y5M?^xtqq#yqM!&9oAFRSZz`bpJmTxnTOf01`iNBaJ!pU83sGIsN%w^nwRzMUe)DUY9Hx-7r_M_HMVuTvkD|I{P0{X@H(pN#bF|B|bD?0IjGA3Qo-?MHW1JQ3;pht5{x<e#Q$9G3ZWx$OV%x~p+stHsGkKlH%}m5+b4C%xUHn(CJxw@yX+{(%`}y{uoed3>wHR^_h>oblvS{(rK*{sj|Gd-7>kOSXUD;=Qw;d_Ku4+dp(XhxC1UYb}%MD<zThd@%6yiAX>6e24S{n>TuV``5?Px5tn4`2JQM)qU6d@KI0tr?b_16w}1x`&J!P>&4(T(hrBLt9;&2`3D!M{Iwst@~>QHgCG6v@%>jis(IkTvXdTvNFmwp!S|PX{LsKzYF+-|3y&YXcTw#Jl8y2B_MwKVUaxoZ_`cSvzTxqQJ>|D==2i3d-DAf*<taNw-R~_2ddhE~pRUrc&+o0*m<{TF?^MO>pFOAM$&Gi8d;FUh)cCwR((CuluJ+Sanw|EPpZm@_|KyaXeFAyZ{4hMZ$G30PQRA@iH)lNUws)vnM;`v}ZMV8h)%`oUn<u@#Ps6*0c*+wlwOab2^SL~}RpfW&r>uU?lfGAZInKk|o}Tqw_uYbWoChAH@%Vx9-PHP<J5H^4N765m?UQG%+@I_9G~9LW;soz&{HXgHKkB~5kGik%qwZ^+k9l9~e9Ze==VRR0{v<OO$^JFwJ?)$Gp7zaoPy12xUZQ%7BFB%Ox3zE1+uAqhZPz#E?O^?6s+`6;qJ486vD$A~DEq}&H??oBo7y+mP3@cOruNNsQ~Tz+seN<Zbgyfyo1wu~R6fQ&LHp)DA^ak-@{N6q_RW2Z_RW2Z_M`SKS4%CBYVN!6qxM}oy}9qw>5YAtug1gqQjLA1_RW2x_RW2x_M`TVac!h;?uT99*blqDu^-mHxgWODJ)S48YwX*#Z|>WJ7w;+GcrMVs`CJgpJ4X8EbBgxO=M?{#(b6}cQ?zeBrv%b8P~|tCo3w8}HwCut{W+m=;(vXM^rN2R@S~pNzMZ1-F`g4$-*`?8zj=SI%-?tpb$#<WH0RrM6Y7_6Y-o;D<2l;(jpu0Xo6phOH=m>Z`*O^d>5b=l?MFS=SNr8B*)PVqf$JOR26o&n>6_;g+BeT7tU?2V(l^dMv~Qk!gg;+AQ>t-(66(EB`sR5{I7{9iWqFNr9_^dwJpQh2rb{)>i$arfPLpb!FIjuKOqS^r<xu;CBMnr$;@d;YsQtjXxkn;>tJYApj^wR$DAEtL+NS)H6^?rRRDVl9m^IFmf9Oy#InJ&8sl54I>!8-7Rk=O+SPRxGfB892dVir~Dxc-WRXGopn<(?yy-W6seN*i>v~M@9s`}-$dcO8ut}srf|4ZE$mOih;x3>3E>u*MNUKd`Q<A3r#`1_jj^?4({Z;z$cDb6zk3yzGG`G3_|t=F83YCq6G?d$xULu%ieGEMoMTWUW%<CvN^e4Kyc`=&mWe&}CyUg};q@vEvl`rH*i_+v}ezh%|=t?LhDU&Q&an@{S+%I7>;`~L6#QtKV(*lzme@2Guam0q6wL*KVn>vhV3p7MnHj#vH2xxHJSj3?AOe&D$Gy7`}~{KtIjY0qG;>~fwDw{PrihdmwC{w-Z{PkMXuROMIVbC8B@M!uaue`(+BFYTNCrG2x%v~Tv8dtIZyv~Tv8>l^*$=414i_Raos(;NNe`bK}bzR_Q9d5r#YuWR&|o8IUzH-DqQv>(-98#j%5JAwOA`{w;<g;R`^zc=o8?ML13hm%c|>5chB`{sONrKvnw{=GS`;z!M^_)+sJe$>3GeRE#bzB#XI-<((Vb<KHIm*1FI{o7xeCi5}Yk?^**)8+4tbth0I*N@US)-UZxtzX-g&Q#;iyFU6G3=GPAjdfQ0QS0pe+doO)SjV+*uH(L8IppV>=KdkHb({P=(%iRbKkA(S{9E$#$f$GXy1z)@++VrAvA+tuJ4JqeY3|=#-`u}7-l{(DH1>zuH}{9Wef8(5@!;K;YCmdUT6e7U&3&@=qt5dWJerqaJK&r9_K@91ehz9rN4UQ69O3%LbA<NI=Llb-htiLF4#JOm4#JOm4#GE|gMu?k$<JBM=QY<ip38z86U)y{&F4z(o6nWnH=irDZ$2*sD^`)d`JAhL^Eubbw?XA^KG)+%J=fz$J=fz$J=fz$J=fz$J=fz$J=g2&8qf8CRLSJ$$L2YP_RVvQ@V2_rk2+Vuk2+Vuk2+V;zIh(L{YRC*c^-}*bsml%bsmmyo(qMF%vGO@8|P-)H_y$qZ=RcJ-#j<dzIkru=3|_jx%n99W^O*lxmn<iobvN{U;pi%^FUwu8tU^d^PC(%>YN-u>YQBXW1f@i^yWD^zIje=udSu>G0weR-#GWyzIpDgee>K~`{uc~o4;|6?WQ-*vEB5>IkxK?=h&`qoMXGbagMEh^Bmi)uW^p;meV-LcH6-?$9B^j=h)ge&#|>{o@2Y|jdN@_y>X81Ue`Fs*1ma;9m@FU@&xZY{HXg5KkB~2kGk*hqwYJMk9ptee9Ze!=VRP=R;@nrJt}iv(!Mz_Y2Tcev>!Du)%s~g<T!CZXT*>CoDo0jb4Kl(=hb=RR5{J_YW%3rJ+t0Z?~R$C^WsN+&Wj)QIWK<H=e+n)pY!5Jea?#?^*OJ;uCcBKM-`Co>qM>N_)+V4-RjCW_7&PU_Z8YV_Z8ZY+E<)kqI`3oqkZ%IdH!MPNA0`tqxN0+QTs0ZsD0PtyXv|xHSxSJVRgtN-;*=<ldf;<CtcszPio)XPX_9gRPXau$>n`NWM@6;N4@8RZ|-~jm)=*tabB%`^SnAdVX*Y0-mAfn+K0!@ROK=D`Pz@#=XbuoDxrS&Pr0k|H_xB(qn<C4K2!M^&o8cTJipi(8mjjfjprlRH=d7tmFBNbsGY6-x211BuW8?WUJKt^FZ<1W?z5|Wpxz@i&w=sH=STl5Db@Re=JP4O`FtA4&`SDI&$$IhtMsQ=d)~*h+i#P;`5dkNsORXiA?3Fp>UrNUoV?h2nUC?D9{k3V?<tzk^`YsV<@tyILVvZ+==T+i&zEW?o8WoBF>s>j7Ww<Zd1QM1KBT?k>Q<>aQmXrt_a}Xm8p-=7)OV!keamq9;mRM|$n$<?=;;yV*N&CGexK7`S3ab!b5=dS9#!Wpp-nZU?=M)%^IoVmp|<ib7WBMFYCmkN@(K1)&$Z_{pGiDa`k~VEJ@2E2+kLCjA9>(?fAztBm4C6+GQED^HQ4Ysl@ISH`|_!Cp1^<4RX($Gc;1`!&q=mj`oCOI?Q$=bdXHB7iJr-EVvWqdBOyO{>)NJB-#;Ol8V8S;?M%qGb{|<E>4#G0*&*|Z@y8|PTlc-?(SB(0vUMJRUPaaJe|oR0eV=h%f4N<|q;J$q`_^r5y=>oyyCcgJ%u!k8e>t`67yW*6uxbO9{^AbL`^<K}UedQVPV>J1d}y4?r(Yw_`_ler8&p2MMyPY3Z0h{Y&be3Rv*3*9y=z~hGb*1UMLq9nhb~-Buzy|O=wH*<{i}Vme@$QaulCLUHGSQWu5a|C>HCcQ&3-g}-H&d)%zmtMMYZSjMe>~0dU7q!<IhljXqb`yNBl7z*LwVNchtOOrvGS=T9?fH@vX7meC#(as`+oYHy=CIQ`s-!k5qk4KhXU8rbs{Zhw7Kme$}3)Z{Iq)KGOH^&n^4K{-En#PyYD94*s}=e0#p?M>l``(1O`ZJ?Upx<h^-sd9)ui%k$E1)sG*0>#O~sQC}<D2eN;IHR|v2<c}X1Id+97{eZ^O_ZjUR8r4qj6T(T}ic823c3bVKuQhd;TsQqXpTg<Y{I%@9=lc}lbrq!_7@OYv{fjMiReSYb<^8@!powZ<{|xW<JBEL*@}Dz&j4aQ)yVd=r{hyVu$F1wnSAJmRPjb8ks_j>P;#{8Zm4t>JmcIY-cb@N|1Rp(9>8n1G<ISILm}+P3S5v;#qJV1W{4aJy-d~~OQ}=j$?j!qEOTG7bCW-p|Bu_Ta_hQ12a!5b?>2}ZeXu_WsRiA%8$t%An5xx;r-wVR`;|G}cwC}^Wum8F>(hrW#xlxv{M9!U&zKw6@6TtV^eY7Fcw@UQuAj@auqy3<fkM=`mK3N9H{_@}S*2~JK{HT0hQNHhns+YY3pK%gMrt)!pW1P4?<0PEyH<^#WdSlgY9fo?o-xL_$OtsI}k3HXqvWK<zT-WmFll|`c<Zn;DsrtR*VAWrG-YC6cU!<?+6T4OK1(Cj8;U9Is=kBsM(zhxq-|jwtsmCw<wc6h@51W37dDtya-y;Vi@9RLvgQ`4T0-o=Mg|DAe<!SIxJ+E{B218Fg?ch)Ut^D4d>(dVYrrFhd{5zCyGd}&ZM(&REE&Nb>Z+bmWf@XTggWW-;_Xjh`dDh=P&htIE@T}@_k@u;e_H=!{-gQ&$seOCZcN?V|>Fw3Z4}GE1`!m#4pO=QJdB2zUq`68zyS3+ge7=M2r5{*aNv;QW+oJ0GY50D8eLrg7r_<j!y(!YSx()b3wwsZU_Jc+~+P7}1e5}*G<0AXfck9X?kFWc2X*c!0`11*>zH{?=zPA{R+vv&1ztE@VL+$JPqQC=rUj(vmii;c%)+m);`+7VCru^nf@6H=$dd7n_Ri*chIHB@Slg<0R%O$teI^ARMa?gEzAirF9?ZIt4-|Mt5G*#>L!J5lG_r>m+(hrUQ)APO2aJh5JzuRkB<aqE;xVbB#_Hli)eOlbwm0<heN41ak&Gym0(LUCy*LEk^@7g!|J-Ddc?u5pz_RVpteRJGu-yFB5A2jkY$8GRti`@y`*RF5e*V;GlYu7jK>(G*b^53lG`5v)<@&Zr0>3Prfjd{<1Uis#{r+stYbA4mpbA5B(d$>~iq4^U%--8a<%cGvdjCDu*=DMSObKTLtx$d~WvF@0@UU%H`80(IesQjMD_SEaC>l^E-zf4c{o|LgK(!RMb(!RMb(!RMb(!RMba<6Obi?na<i%dUg<YVrOT;JFixxTS4a(!c8WbN+hX-~Z`a(!c8<od?G$WA|2`9(9zeXlP#W{<~zUHSHzbn1IkZD#L@ydU*`*!7M5urIds-pF$5eZK1(<#c^xpYIE8m%g1csl0#nIe_-9DectrX3P&e67uaO|7`T+Q#zkKCkqtmAD57CH7ma^(s!Tt|0ujGA>TfDZjI-<z7=X+GV<5H-^kxzd%T)ojq+<hY?R+$#;?Y^K3}T5V{c@?=yL$qH_icE-#7<wed8R!^^J1?)7R$!+P7;Yk^QC50o?S9+p2TZm8!m`AIhTY>-xd`vR~|f`^6>XTO%s0i}c-dfcJjh>nRVuwM6x!>HG6sSQF{H=KxQ3Eb;hp%i|I%kM?~=dF)AD)V!Ky@E%Y3CoA7~ulNd&|F-IP+iV|vUsiAX`2S!$813wDF-g4-@O87egnaAEfu3?&6E}O$0rtJF-WxE^-(24~e=~i3{-%BN{LS?B`J495^EcDi=WniWoWGgA&&c0Ae=~i3{^r)pIDZSAn3iDsxW3Uormx#a`_|&eTN290+ICQWJ`mVFb9+L*mG}3}k-pi^QNEGC+5T=hr`A{J^o3sDo}mBn^DQ2~#29s6w`uo|gnWOwSsOk6;Y{-UDLCZP_Jn+UVNXxJ%<*9Q{#_+^Cghv#Z=TPae#qz-H~;+mHzb&zap;!6Q!(|NZPp7vs$MD9sPiGC-LxOoZa+QRnP9)*+eW{b_eGR%wu5oMxcQ&IsOCLm9BSWhj>8)@cO{g+dEc47zVF=p&2#TnUDfA~qsyxC|65*<Z@*!w&%p-#ustE)?$vxtr0=htIh0^NMVhK{TQBGKg#6ISMq54Q={JGzMJ(CjN#AUzI<J0oVxz}j@RAz;4^DdW_mA|e@qcvKW{>}R3OU|<B{J+x$hVGV^<39VQ$hJ@t<4GfcKuY|^87E+&V<Tik1M5oqdaz)b0(v{{?PKB3D!65J(bVrzlIX>1DPLr`X%(>b#)GL;`TOA`rJF!c$?92dxHMjzrE$`QBaPnu*j!@=l_cJ{C?5G*(y3aZzob%nXFG+NBl3bgem@MP56I_)uHtN)&COfjgn<b{Qvzwu~PmLV_DCgxQ^a}e|O6E*olXP;6Dk$e-VQJCImkr1V17K|AGDv7j~}kx)VhS!Nm!|ZxDh@5Q2*lf{PG>UqcJSA3E14;lxbzeK?U5&abUl)PiH-q-bI|Df|+e4t@#Fie`ti!r9QAa5gw2nhDMbr=UEde96%ia0=2Sr!EDk&-?IeXcqW2I4_zS&I`YaCWn)g|EuKr8f`TbE{^7fi^GM`SK&f%J~R_7G#8wlYo{j!XSP&-6{dbA-~y-*E&yjiGsBt5M{p`9k~xt9O%G>)bKr|~NzjyV5;zT-7ES}dg1!vD0_R6_!};NYXdbvAoD0nX=b&u4X!GK<$A@rXv=Cev_M!P;ADkJ@1?M7v&6y~R(3}xv%SqXVW{;>#cIqlLT}0i}(KbR8N3>O9+A@Z=w$LPS64GcthVltb4xe^@SntFZv={uLbE9^4q6OLoZUI+A--D~cFJhEFi%~2>@NM)ed>g)rUV(4I|Dbo_f8f_Ck0@VB^mSOMNF!L(<s$Xz1)oFjz~|u0Xu(*;m*Hz@Nw_5WUn9?RwAB{)5_%cF1m8ff!8hQi=v`Q7p;*P@TH@O62*LGZRey!)tM%|jv_P!li|`$^K3t!C1b1_Es1q&Gc5q9$D85KH3jG2e1$RY1hr7b1(5i4L_}>_%`C$=)@1g(2C>HS_Z6Q>Yr4VIm2XCQ$PZO7DgG;n;n7Bb3+@OsG7od&nqlIXrLgcUcE@ipPSkz^^LfNk{c6D6@i@IKAtn0c9?uxz_(N^!#mYr$qF6bzD6lt{IneugJObY&2%uV9{KnudT9L?>756uJn;2da9I0yVPnhky#&WvV&GsBtC^l&CPE1Ct)3cpHuMESC#ufngAMzE+$0qRo_&X4AU^TT=3SKz#GMl?H|o%}PBXMWmBgy5%WURZ?S=V(S)gy0ywEU?hTaCWYpk`SCcM)lV-`bvc00_Y1^gy4K=a_X0yd<3U);w2|ipef-La1wlxE*+W{P6ww(Q^Bd>q-ZiYDQuyMU<>}wQW^`3h@~xJDNABBCHxQV`!Dg7c6mzsJ|mvfE<$5yj~8%q+Bz|unEW+op*%v<N0co+Wfz(uqAnSztI%u_b<alI2+bMMRyk?Q+_ZHbG##9dG}_Ni`EoNp1i$Ot!)={-18oX_;zV^PnxG}%iB9x!;%C%`=Q;6}6W^hI;Wx;$INBU84!?rdgkOPuTu)rL8Cnc(2G>Bd!ZqMpXfC)GTnEhq*MaMy`QUnRT{JIT7p{%^U>{|!P2ELXe2vb9zlKMnyWr9ASlUsv=NxnhJO|!^{tw;(??uPJd*MUqIQS5J1f2jMfe)kO;luDgbSylUGVi0GMV;HCO<~brV%(%gUxQP_Y0$!O8aQpN8k1t&6hYI%X-QLr_7UT+3HnKF{P+~@I3HaH&xaSF>){3PLi$UL*$wDIcp+&vP@dwHMQD0h=u2=~I1QREqK@fkgA!;lG#xC)l^Aom3BftgJa7*9RWuj;Dx3|?3TJ~eqs8FNa7Hv8oDt4|z6580Gok6>OmG&oIGhE38GQwQ8P1OS;OuZtG%uW&w#Z3eh`t$)_JxPTJqW>{p>1KI@4}zK?-PQnphe&+@H=Q>_#N1fz6Sf@255Cy=qGRk_)|h~ceD>IbRygx9!3cM37rrB1kXYjz_Z}l=t6iQ?In1-6PumbhHiwn!CTNx@D_Nh6MLLE5Ub{aeehxQU~K#xBKQcpKQ?~O5qt>U9UDJK3EqqDjE$eu1n)pYvGH@D;5q14cq`=;{4=@^-2|_L*P|QZ_3#FCGrR$wM+lyaZij`&!E@nV=pJ|v?Il>unPP2dN(gR_j)t4VH3`AB(XnuCxGp+AHh#?#To0WP8^6X0u7i$?jb9T5*Fwj{#;>7*YoPywg${|0Uw;KRLv2`S6S%z-4V~zSHiAbu(bI{M=$CLWC%$o_H~KC7ffF5^XpDA(zvS;bqV3_bPLy+^6(RT|Cq72Yqvha$6Rn-7KnSjgwt<CKf?M%7Wzh<78?I3aEf2RLuaAk=T)#Dc{}I{>p6WzDC#IqO;c4*q=m2<z6N8<Y?!-VResE$CIvt))8to6{Is>`JRPq`?egjB9gWnJ2nuGb>AhbW+pEQH$vrhD9C;CkAQ74W$agh*w2|WQ{g0G>c;A`+b^bC9t{+m26bDg8`ar6d!96pKu0iT3VqyNIE;j`#}@LBjgDh_wg^RwU!=!;mzA_Sj9|Azmj{DPA^>F+q268#0v=)@C;v!GAmq)yy&I1zdk7Jri_k;*SQoEA+7r-d`1ncxg?Rx~r570!lcgoS2-#kFH7S5i1J8Ve_elc34qByb8RUUDL}6X^-Tsn8T~3epRH9IO5&J^YZLMY%*<Wka9CA_QkepT)-4QE&$I&)E1j5u6tNJvP1#f2ZGs-ho9sh`xwHufQS%$D(0agy3Y9U)1A1nhF*n_%@mhPR8HfW~_)YlLmbNix8ZS@gw@|A2c&8LhxT`CRl{vM`$`Y9eF;Ytwo!sMt_Ax2u{KH6l3B#niv)#_$HbJ79sd9ngUKio`Ut<7bFDFM5n_u;UCc-V6g^?HD?m~Bm5(2CZSW|N$_NJ8ax@Ef_@KwPno6=g1<q(g~bO{_r<va`YS9#a3Xw>?l&|R79sd|G%+kf@FO%SEJE;~XmVJD;J?t6un56_qp4sKf}fx%U=e~Jqsd?qg8x91z#;@cKoh}<sJmdXu8Q@xG9maav=aOl{5D!1Zj63F2!0bS4+|{^zX_K?%fe;g(r5*^0%a<VHiCsVgcmunI5vJg5_}9k&hHn&OVE?>5_lPU8eRskK+nP};8o~(con<`y#TL)*P`d(weV{647?g%iJpR2!pqSU@N#%5dJH~BI|vr*pvBz$6n>71HT5|m_!;^y{0#mR{R93J{vEvm{|?_lFT-L!6m#Ei=wGnVN3hTbu+U%NyQrS81nW6X@GbNg_!fK>y#wE&JXg_+@KyK<dI`P)htX?r7`~0(gKxw4(Z6Hk*A&5z(HHOw`r|Pn_#yfPenQ<I5`uq?Xcxia-hUVqKR-N-iJwCr#>CGv4`brzqK7f@^VP$c_&M!iO#Hkj_&)KFdGlBJ0r8MI<{@*CVA~m5gPo{``r&GDDfD%?6kHT70vCl#qs8FTaCP(@xH>!({Tdz$pQSvad>7C&@CEojdI!D_KR|zjAHct&ci~^*i|ASSEM*Y<71yqXR)cH7WzbS^8Mq``6fOzBNj_gucA-b%Gw>bs7JLW(4gCfF4Ze%shVQ~>(PQvgcqlp~qRofUCqipS^igg4ur_5cjTVJ_J7Z{%6JHX751=RD1MnI2JbVVefS!aez-Q6D@LBjE+8;g$_oEDN$Eb4khO45b;i_<1v?N>>E`^qXOTpz(KU@y3hW3N|Q69m4oY)ajo*lG}&|~l(_yl?iJ^`QSZ>y4DAGiiu7Onx8M@zxw;WyE8@SAW2v>IFiu8H=CYr=iey>MT6Cwdaz2_Hw#!{@1&;K|Myn&?C~v@6^VZiF_38^JZv8gNaxG5P`A819aK0e6SLN2kEw!^_a6@G|%Sx(_}8pQ8MtK8w*M@M3r`x*y&PpF~f=r^r+AC~=QD@f{(!FWL_73x9@w41Wd(&`;q2+#c-%w}<<oW8i-9B=jeE5<Hu-&7!=c;2^ph4#F$ZE$~WsGr9)e46j0G!?U@r;OS2M?8H<;@EmkKJO^HjZiCmtThR^hR(Ksc4_*h)MQ6Zs;c4g~cp5wa?F<iqJ5uKU)MGk45bXdDggc?F;ZATHv?JV+`~`pG#6~AZ5Q4X(=iu$|74#B(1-_1+hp)p|(M|AGcqcj@-U&}Y+rkszkI<^{NAO#exh3`Z2L1%C1b+foK`X#j;J4AY;J3(Muoy#PEG;4gk3+}6<KQpRKJb@tbM#ZVIotsK7;XSJMcctm;ht!3xF`HAItu<4UVsMS1@JC(CA<qhgl>ip!F$kE@G9D357!z=S%mh8C|eK8F0@HRU7Ao=q4gu`UZ1uR+AN~2n$ea*dquQuFWO${*oeLuOZkK@jOe?ClzAlOo{uho=fiR6E;tT8h#rCu!n@Hu@E)!u_=poLEHxj@gJ+;W!ZYAOXcu@8+!=ij?hLm<--X-2ozQw#{5&9dAo{r#KW_-0j{ac9&ohF5Mwi1s!|Tz*@OpR~dK%saZ$OX0M`#PdVoen5pI*NN&qDXYv*6X}Nq9B91>Fa4f!Cl*;We;ckNR@`iEvl+Gq@|<5DmZ$;TmXrxCZ<I+7JE!{sNr@e*sTHXT!58r(iMvi}h(TA$SS87G47HN4LWJ;Zx{3_!N8qoomJKRRk|Xr&;lP8^PbB1FZPHkl^lUM=O5sB)Bo!+KS(639gBDu;TY-f*Yazt@yp1;BM$tcq(lnc(@b8oM?g8fm^^8(XwzwxIFp>Tpq5BmV+z9t<bt~D|j^eKX^2}gYt;-9Y;g(arg#$8NLDEL$AU2;G1X|z6qZ|cfdO+gJ3boiuqTsgMz<7M_Tdgrr?d}e0U>#4vmA)!I#j3@Fn;>x*I+ZZ$cNso8a;2Sa>|#7VQPMg{z{?;HvQ3Xnpu?xC+_?ZbDlK9zox<L|ecu;Yw&lSft-h+Tn1B*iOF*y#fop4qt|^p;zH+aG1DC9}3+G3!MP(fc1D2+zR~&7W$SIKUM|n@hrGJS^=&={mP>i;gQZW*i0ve6M}z4H^D!`8_-?w1~?Ag49CG6(VyUra1b302jOqg_VBmxXXtzIXK-E0+%87dV<h}3S_l3Vu7_5K>%s4$b>X_?FW7csgcB3c@8AjW9Q0>+4!jgy1}}x@qVwRn@I-VHJQ4m1{RaLD?t*rMyTC0erzm$<^mDi?+zM?0w}L-J8^a&MAE7PbmRw8lSSLm~(F6Sg?g6((KZaYwP0=QBQ@9NpfZM=5(e7|hcpUmacpN+podQpT7oiK_MeqvBFX}THoeEEe=c5bZ`S5ad1-ybh1rKy$fD_Ho58!6-J7^{N9r!J@BK#Iy1+5HMft#a^;O6j9bQnAoUV^TIm%#hcBk+Fs5ak#3S&1%&SHg$UeehxUD0&D!M4o~>JMnc){1_Je6*?m(e#{G=h^~u?zefbmMYqMo-&2B@qHAK}??J(H&>v#r?^(eU(7`eB_qbpi?FifO=V$}?bGQXs8*TwNMjOJ7;g)D;xHE0hlIw~x4I%`8kFJ5ghgYN9;MMR}bRE1EUW?9v*TU1$ui@$N5VSKq1nxxHI#Axha7VO0+!1bo)`A<rwbA$C+Hga(6WodG3LfLctQd8_j)kY9A$Tgh5Zw(ggjb;3;T7;AbaqVqTp@TGIzA?TZV@~VZ5tCm7YXi3*?LgkG4Lm%?sZ~fGbM`uQtke=Cy$)1ZCN5xTk-$Im~)<r+jZ~Rfp6KGf9d@?ZscEPaW=^AmvbA`Ng}`d8SDHf9#A@nU5@pC08U^N*Z'

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
