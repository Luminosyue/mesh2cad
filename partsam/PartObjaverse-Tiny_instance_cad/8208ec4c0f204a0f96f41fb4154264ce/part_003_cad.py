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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_003.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_003.stl', 'source_sha256': '9610e4c0f74de879046d7c94ea83bfbd34bfd4ba83441fb4cec1849edab49d3b', 'input_faces': 949, 'input_vertices': 591, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26978838443756104, -0.355949729681015, -0.08087523281574249], [0.11402931064367294, -0.07620720565319061, 0.12205272912979126]]}
GEOMETRY_BASE85 = 'c$}r31$0zb*Z%JW*C4@dQXCSTK(GuhL4pJ+P$sx*pcEY}xVsM&cMAj`q-gN~r7dM}El{**zuEhF=FQB!{jc?3-`98T_5AKLXZAhk+;h)8_e@xCM0lda0S5jHG-mHjJ?c?8!;naA1Q>%l^^fk>q0@k3z5D)PGSaCp|G9N`!^j2^txU!sV`#ySod$I1U$BC?V5QFG3kI1BcJ9+Zx_?yfc76JH>?D4zsGb8lx%>fLqxyDo9TzGaS~AF7x^R$rxcPtiUrJXMY#}u+9d@aCYRj{thP93*%q5P~7WJ(KPrz@LX0fQHR&w<%pDUkHKV7kfTK>t=i*oEpR9?&5_I=nW>ddr3eRE#F^IHDpn1NE>vS|^^4}qWj{(L>YI$nKy)Wo0F@08Up<*kv`QT}4=DV%rND)EhSK`1{m?wp=?Qx-k1wQYX&ouj*JJsr_icj)IA)1f{QXH<;}9mY!@+f?TTZP&C-sz%&zn%}weh92AgHfg(!r)lSE{x8?nH*Z=1KRSA{)~EJ0_3ay$!S5Y3-qW{To(cc=hSN2FfuE3P-ZS_sM~wIMo&6ueue4F~+xi|;-x__}E05i|5Bc*K#dVoeWWD(2l<Saxep{5En{}ODuaJo-KkOKM)8tutzSHB-{?oDWhrU>=`PbOcE`JC75R>+U<>d(EpZYiYGcZ{5Tdadn&ueKftDj?+=6Cy!l?RX~#;(`h7SjiLG6bE&cvz15U+jhQHBuwb(wur;+q=#vzcU5=<rd9jxe|qbdsZEO%1sl(Jba^kCHSivP0{O;%ZfZ>%D{JC*Z#B?sD$#d9WV~Rd8y;aaUcl3`@8}1+CR=lg)x4<%*1&9++u_FTTnjqTl$sgpJxR(X#JM^qn;_Ekmvjn?H~KFl(;TU+ri&`V2<`<t0c%j_&fMd*U!`P&rIl_h27wfKdkjJuX(TaaNd{<zjv&TD{JT*^&R<pqW{N!T!;JQ75u$JQ2u4~49%1Ih5EL%FR!Q{Ia05$t<od)txb)1^^3=N`_J|v|IGuM-;(Vv`XzCc`nL3e+7H%Ex8NW2N1pwQG>_5ws`}=+IpOzN=jB@iwjh6xyX!UI)+;EVEE0axNSy~9)h?p`_Jx?oO!h5$y>^^b-!kMj+FR+F_K)TBPbi;dCF)u8v)0pGHxB(7au(&U#cTgK^Y4V;*$&@!aHeYEwaBx)Ag+7(6&(-GBr8$>ZDDBFp$oHgoZMN0JXIRP?|)N$BgH)UnOl4L&cRdBZ!fyQFYr`-bLvUwz3#h+b=v>dQe%*3!Qb#Zr_y>_{71mQHXnYRa~{U&VEEG$!++mf``KB(2lChbi2fN|N&CmKu08s*;5yW2)vifep9`(g55LBG`L?&s;O{u<<=ZDTM*a!MF|PfO?9{x~YUBFmyzHIlmvT67vUgtfw}<CNp3)8BziXrY;P@jCe0M#+cAnwsTi&KYyDlu->FL`aZ_(>$S-%?o{_M!}&o1Pt*Glu4?_@-t&kp$W!_~JXPlNmG$N|hJ2fA(7_AX9=Jn`qe%3B|O!t*RB&sFtLC&Bnh{}}#+jcC`!4!FLpA7b9L7Kh)XC+3;4@#;I{x}sg}7i;~kIet>#vG$ZcPi<Gf==|o4--q%8Tb{&y^bYfX;AZCUhx$Yho}>3mkB#cvBgdfrkIm@+nXBLj&w#(An3r$KKUV8$`)SVxT(_k-uX8ENH?E}R&HHDnZ=SR9-~DBMF&~%iruVg_;WV`Cb!5C}{}@FlqCPL9ynJV}vFcmD?WewNeRuTdkspx1#c-6TZ(bG+f7EvEPe<%PjL(w&;3tVi|NOpls*cZqX6QG|Va%T&Qea(Fp#l2g_0Q_tE~mq~<xMrzC*vO|&-ILLd>HZ%8g|9=yyi=lF&+v}^75UV%cK14g~(I4zn5>hk{#n@bYAcBwdZ1e)gpGI*8hD7{Qhxh*S*RZ=T*z1o==}3e@t$zr~P9Q^#86^Ugvd8Er@>b&wfp{ejCkiou3HTecu$6e>r}Gm%sEp=JPCn>w3Ue#6bPu<w5=H9#P+M@Uz}m_MH2Wr{o6YN%l#7=e8K+nO_Od<={8)7l*??GY#d3JW$`fIR*T$PW8<#ZmVxQ@$`zP??`uDeM@|Aw5!dNxmv!$anvViT8y76iO`?t9LRIO9<JM@iaYhbe!W+HNBVJBJ?|rDhwaGUtt!^BTc@Hwcg}}jy&1~qx`pw1bFBK-@fER-*fM@wn1^rQc>c8dQFGz%8;SZf+ll(W;&Y$A^TIehzgh-q{ml)Ap?v?UC_m{E)_VsBp#HJD(cTQDF`gY=(4Qmw!oPb9^>0-l^|`nIn&-GO+FDTl(h&Ib@+{HwzO01y&R>o^S!Zi~9E~38bKR1<DC*g1ochi?cj519i#%hKVE!q7O?~^Nky_sNW364DzU6sy%qJ<^t8W~;jPi$0qI~93>RTV5Ro|L=GS=Hq+U(H!lsconxqW)PCw0iD<!!@Gsqa|dN3WNy3Dzf;R>$D~TpG{A@S?l4{u%b7J`W3^{xh0lozrFy&U^bL{FICE{zBh*w-M&~>KXOCj?vrT-wM+6T0*L$J{MLZf5S-_C*7v&^T?cS1^hQlFuxVQjORt3iD=ic^SJ-g)kFT8qtQQ+cQBu?FNXZz42M4}9qyOPMNvL~Kh)=KIWON?s1w#_$Li^G$5H$Gc0JGGNR(gMmh(e-T$d#gs81yW*L~;2P1+Cl8>0RZn{i(h_^Q4!vNZawVS^Lu*Z5(zwzu6k=>JK5(Vxxnp6kew8t<`upEcrE>wRkNl#=Vn2rX}W_}3ae-&GUZoAn*eo3@Y61D4pAIzH?jp2O#SW&7<h?&tOA(XOT6p&v|l)wg_@f#+|g2YP=w8=qF++N1>PSt7CC7q-PG)wgBHh<<2&W3!&O^=gdE^w}_Oi;UFqX_U7k&#;a-FXvVJsAZ^U{xtCC?Zmt~b{6V0XFS#kQ3lot<73o!rs<0DlW|I{*0bX%<Z;i#c^hNha=j<&*=rh}FJT3>p0>aq$aDWP=G&{sw7u4u?a@Dv_UZMqO}e>7HM%D1zc?}G0nXcQ->AM5=bctW``>!663Rbo{ja{UewEjGjbas1{%&&QZxc1w(>MNTgnoYXkFGZyLxR;e-!yYQe`tfJZ@IS><BRjQIc*W-pZOi;(ba?Wes_GE6Zw}+)jXEUyKukIH}C0<dS=FWaQl|M5vb3h#2B9e8BqSwd(2~7o9cCRwoQkAZd#lB3AZqBk4=H=H6|zgx?3^c&Lu<nm?mh~w4La;_iyz1VQrTL=S>^DTl=T#>(gHKi8`U{M%$#nP(Cmjp4U~D&er=b{)PI+jW!t1H5N|t^sS95!T;w4*5|pNBR|(^#<zIR+CDylU!@wJYl~{>bIo%7F7kZ+5&cji5YO>^*VK2u=6%|=`0T?TzL8@D>c9TQR&DQ|%gk?J-l!F<_np(Yq`o~*7d|($#pv<DeefUrqW7=u%PAeVj)*<T^N#sj_Q&;F6sx{D#V_dpDbvwE-)}?tikDG;KG&=%H>3Pllh;0mZRvXW?sZ!3zwo@EZ%aHG<3HW>Y1%(SR-u1N<w5<M^<Q|{!?)}XL!N8(F+bRsB7ckDao*4%JineSM*i?t=$~`JtF^tQ7r|fiE6%%afS%Vnd;#)wpM&QG*S*HcdFZ!lXK{VQ?`wPAzI91y^xNAhI^OK*=ECRuoo)IstYbr_!GHA`_5Uq!t$uEsg6q4z;1$pMo6k&wzheRNT#Z4Vj1$#&JS~aqvNf^#Mwa1dSMf{S_w(0vzTG+$?RwfC@2!#5aKCT(0rla2g3)pp-qY#Z&Y#Eiy?1Dt-q)|c$M_t!5%YGPo*2)S2ci7)k!V-@TNsBi(daime;se<qyF@r|9rxE{R-$lk~w=n<ax#Va3906xflE%#nJ!kKI`=|CUwPl;Ck3`Dp>Q|uXINKxAU;x$UQ{g<1D#4p+8?w;=HsG`RUtB<%8egy*`(nojV}^^^vI0tH9ZwzWL_@cn;2*w^-}*u^sa7=ljCvv{Mgz_|_F2ysodk`gdqobYApZjW+YO|EIP=eWs4$zH6$PIzG*<aNhDak*CNnQx1Fh|9M`ld!pCf=-vYTkS7i9i}pLUKDM2a$iKWB^6cJ#dFD$~l%M$k{cs@@-XCW~Ab;>rxbB(EUcR~F^oySTZ|)V2@_~6YzopGitgCm|#kl1<(3p}``_p37L3#Ik=$PADpa1x4wxRrz^y|F*9G`wt4SF#``)76y_%+6G{0Cy3+{FBAS=5;0Je&5Xv9B`v|Lm_A=OLZ-yw*gO&_C|+=I&?u=JhpE&o(dCV!Twqc?V4JdS7<?_C>F;AC`6KR!`qjYYfKEsEVsSee;5F%vTGtOxOOJR~~tir^Py@(iW_Togp~ygi*L&vHrSG>-H^?pU|$$dB^GfTevLpH$Q`Z$Z<m3Ya37+dCK)fd(*AZeP;8)lE~A05!zMuownB!Q4H5HqN&$-bNg0n3A`^f`WEBlZV`;D=+hWKv&!na!tFbz=0!b^AJlcP5nLGc{Jj_Q-)ez<82Yvq9kH%^e_zLgeNaJ^AM_i_pE$4M+}iXTly6rX`wvIYYkh1Fa>K9R0QE`dug@bRO;*&i>uBT|ly#k_Z@UwKb>G7ub^UK^o*C_pNR56g`(n1IZ{O1#*X76?T~C_r0Vwb2fbr1djLv)Z#~DyQ=U~()vhE%!Z*P?n=Y7Hb<PuM`U2fk<cLL+bIH2Ri@?&!J=je?nf3AS;qdK1@MY}SsgI|{8JR}MH$lA!`*r&gLxn3+#pMwj~uD&HOPi8bwpFewf-4|}(`12m_3;!=VPONJ_>w4PmsE70Zfc;pvZ)D$!epr5Ojh^@ANA;}*-eEr`{G8q|w$Kk)-w$kpJVnau^)ionkMc#n#XRp9yw1~ic6*Kf52>v8i?iJ;)MwIE<oRfxrsZEhN1iSd;6H4H{pXmcDF1OR{6^EY-yC7Lk-v3e_{+;~@bvAUlVkih-J<Uuj-0=v{s)_*{G4feUTf!Hao#)pUErU=Grjz>CD1Om*X`SCB}2cp9jxuOeYl4DxaZZJyszE<&<gMq1$&jZe|n4lNzxemv3V}4|DXNIC!aNsvGZq?pZxWrXMHTSP9wj2Uv$=M9S@G_C*i+KhWhWWfcv!PQPki4yUg-KcrNdDpuG`2(XP#Lx<0qoJ&5zZ8H;+ZyQ%Lrw%_-vZ;1_#_Z)BL0&&Q1#2`=KT+OsTeRd;%?p>G%Cg$4Z>Dw-DL-~<s^!Hp#;Z3Ojp;Ooo&mE<|>lsPcV%!cJ#(m?IdjC4^tU$jl`Wv6mdZY80HOP+qH^;$0vv#?Thb9Zru2C&<-=tiq>u~4M87N=58TNaRro{D1JssaK_cQ8w^(xlA{$tP&sjyx%=3)QP+-elc4=s#+siOz*UR-t<`XRU{KJR^FqPDlqK(sdi>jGo(1N=@D+86%bQ0zCfy`=By)^^=+-briN&kL~L$ktAMb3@EGwuYbdxn{fE4CkAX1mz3(V;?eSQ}}7`LHqvIU;D9BW8}Yk0^_YrQC(-ceRG-s>~r*Nit93^9_o1_9`{|cnt1P{Z}j{g^GS|2KWhDVR7XDt*2TK3`AVz@K3BzcS+)?qW&A`>-`2hr-h)fGz<fTv3i`A43XGG~`A2H~dWNEW^cXzX`v0Nt3zj~?sAs`ODBmpv>;Jh0(5^<UaKG%jt@DQ4w~haR{x6wB=R?b#tZ3JeMXdjXG5YzyOejC63G%;-*1r?5G)af?StT{*fkXeqdHUwxgV3&Am^X~#sn8GZ^?dy9g}7h+aNb|)!Jjb<>&Zt3uGiHsIPaW&OT#>T`@27|ZgB+abJJYvAAR0fuAReq-+Vh-KX3WB`sN88u@AXu&>BzQ@}>&<bJPmGzUGzhQ2y)!oOf1I{2ui5%}Lzv*!MMFwi_V6bHrbG&K1p%`kV0HVaf0u`+7&dBL9t4*rytI1LgDe$93trSI58e{B^uPKl_Y%AZK&@epls!`u3`Wao$yUPjUO!-3QR#YDL$0mbWaK4Zo(JJ_oITABW#4EBfu=8q5z>kD)&KSK>Y$yk~^w$$bd^W+%!=mD{BHDGvUIOsM}#i#`Y4zB4!W18imQt-<;Cpg#-jLVY66_tk!m-Gct9(;xTI7VO*n$FExr_v4Cw>%9C0nUQDVYn@l^UpJv$xuQ_MeODbPmO2~JpCz#GYs>D3``xqx{pNnZj`q{}-x|Ig?b;TP{C%;`x8I(Q{6qVqf1b@9r1cqW^X|8oe2;536#2iy-^&;&TIjmV`dtf@@6id@F~xT56J}|E>&w4Su=TcL99F4?Jj2W2{z}<R?=MHkFqG%I&S(>@`!?n+mC;_yI?RV(Ut#}bdr9Q!`q69u&G=LtdA<zBdBa+(Z+mh_-xC}a>Z1NrvSHtHgF}61(MbG`bEiG7d-gc>t%-g?eYz#Zdql_G@b|vL^{sEyJdSPa@E-ERMfi?FIxpF0%vawYzx#scb+I)Vh4LLnBmexQdo|B7E9&{I2HI<zjy&m_s&DR)4}RXXdVkq}Y=rv1j)mW4zvegpiT!c=>x}4!F;%f|yrCS<yCM+h9o<X&*<#M(-QMBNa9wVsMxN?R`1c({@m$NB3g-<eg6kOiMEAjrUMW!jT>Sf*#q%`3b1&aN`Fn~jAQPTD2VcN%aTCv@;411{j$K#Z-f<Y}<G)|Wxoy)*^(`Au<GrTqaP{qB%hh+Ds|o*lu-3=k$sa!7r;H>E)HiQUgFM{Fvwe=y@oY><uD*F=4Ey0CuKV=Q$JGx=gYqeyTHYD{Kz&D<weT&y^m<wEpMhVb8uBb$qvOziw&X$W=f5HjsJ|v7eqWgSQIE}QuIT4Rt>WrCLe8k~SUELL{b4ocU_3Wa-*%<+VcfsH)OTjLsBcg2hu>Ffl+@?7xpb)d&ZKe3ADvF;L)ZHl@*K*tSN+cM<8c4K*{}LzRpfV88m#5Fzl6WojQTq!>O5wTe4xI$+y>;o6N3Hc^jFolHXe<Ax1=BOel&T9`VMzJLvBsh<EQh~w`HD*_WqVp=TD=1L-_7IEvIOC`yvbcjww;kf-~`VTvbAl|3G;M>OZKvmNWj@r}c54*IoY}^VK)I^N(tR-x1#Up?v>F$Y1XE5*;_=ZfJj5<KC#+HrHIC`gOM+JKgy$Iet_vGe&(&&Un=4<pk{0Hg2xIo#(Z+KebZ*Go?{Je?0nm-#+{<IUo_v_i*tc^|v>|{aELz_Ln25Dn5^@it&Hri29Z!BadkLb2ssKcRR<xXFY9gx}f~(D)2ieM?K5j#^1Nh%7g3Su4mmkTHbN2b*%QA|Fom}c>}Aq*OAWx|M<5!Z?7Tx+_aC&r@nQs>6rSzuCc4XG#C8+<Fvnx>(%uBvOT@C%d?)wqpUhFnb%#y@3+Np{f%n)`wH{i9r*q2OE|9AyYF;9alD<k%d7q~AK`xQ6OBBfYqh<$f{XP2wG{1u@)_7a`(I<7kSjOdhuq^NuD$x!AFFNCc67LS+_N97#lzG$yZgCVzx{gNXTk6@3_<zO_qzVK*UzB7GlKO@URulBihR=btYb$u+^<n@^?BiJdREsvM!)^q&$e5e(Qiw3t8aa@LHpTOrvmm9Cfw8WSbut<c`VNkqTVHU;r-*+!+1U<OQz${`Qqs+uYM>Nqw7*<vis^g@-IO7*v@)v&9HElXa88<7Q#CA^>FPEdzu<LzuIDN;rFtXgI9R=k8%9^LGAxBkt@9VA$FGfj>mbI;QsuAb;l2t7wG3p*Xr-R=DQa$u6VtSm$lTl=C1<(*?Jv6wo$pUPCvxoXXmHYac-<StNE-Wu--QwcUq*!sjlGfQWMR<^Xk`lJeRj+z~9fd#d^)weKYQt3Ma8oyuL8{XY_4-f3c4Y#D1;g7vv9!)_K+9w+p|IB|i?oi52r_-&wj}WzF`E?`P!(>Ujpo>b{6A0`DKjxnH%N&Tjp%&$P1~)^88$>2t)HcH3m!&)8ovQYXdl!kf;G*LoH?hkoc?MduSsz*YSn%(A7eS02Z*$)nJ}Uy)}?q3`wkp*e=?`E%TbUuXt?uiVf*T93bpLY|n;s85f9Z>xCvaV@=k+v-<d{p0qXQP?*!LhxSi_8nXJzLmYj63_BRhIm|;@R>V2%bR~sj^Cq)9$M#F-VvA#*Q?Wn-CpGv-N*QO8?e`_p3b|tznVVV?3u@&bPwjAhEooB)pJ;4eLh+mJ=yMEPu^bzJM8fC-S@?fDu=!DxaXfde|zO|xbK%fFAnMTnmac-?BDwTZrY(?|8l*|(c?yi{mb>WKRzE5_AleXJo=>m-O7KBpL^@^cl18v&3Y?Ff9L$K@!4RjzL)rpXG^Uq_&aW&@o)UOP1g~=_lu=_Zv0N-dw=CWj^AT_?nmol?63IVzm7K-^!Fv-``tSA)B;tX`N3JCu>Sjr|C&#Judcs$`OZJi<~!8)ov&>1X8k?TcYd>cXu3kb=QAG~U5BgxU-M_cAL?5!bip`(kqYn8U54qtj_*8d&(>S_KOBFKf$zT(ziUsJ58r1#cMiV`-)H`Jc6x$;&*AgDu&>>r`+UC77wgwM*#Gl+9+~YQ^}WhC+7tcL>kZ!Tt_;WDYjoMD>kV7C_P9^e$Krk0=XvKmeOi6r=cDCQz&5Y`<a5?uAQ*p7=kr`P{-}!g44>z_+xLCGn_K4E<=JoUb%LdH`(0lB!|QHu&<(%ybdA7z>1JnKm-Pcweb*<}67!J9XFcP%upNJQ=Cl5>HIGLgpY@V+;eDLfXMJTj^5Q%`>ojY-F!g=cb&jv!!uMGR+Rx>V^QtG;jaFx6?5p{#Gi}dD$9dN0KkL$fBk+CJvDPt9@Sf_k?sYv6be{HICp#0DR^NABZJ83OzVABR+Iuw0`>fl|p}X-M@LA_O5C5XR?|Xs0nBPA2ecvP2%v0a@y~AAbE6V%4r&xX{tK-Y}y~a|vI@XCk??Lvgjp6&eH#rK-gYWa6W&3G6^837(IqS!(|6lKMGwx%&`@HwrpT594*Y`cK-D~(h@0G^nRQjCseGhf^Dv#%<&wHygGE9Bn_gqW<2FT;{UTnMnv--a8(Uwym)c1Ywwk9p9^QhN*dW6@%5-j|3$dS)Mh9Qx{2rxQFdHfSWG37tE{`)@>>{jOg>z@dQmI?j8{u99yt~x}ST(=GNTe9d+1~|sWlU=cdx`-^gg1m&hnjyS~A^amlcph~Tc@gu@V+i+U2)CogkULPvQ)9?6tjBnk5uN3VRn(OX;RV$3<njFO0>%=SUBdRPq^|MEvxd1R%6N0d8R}JXZxgf=^(tBP53-aI?Z*)APL(p<>5E?BvG~F>sVk{}kpJMhR#NTcmE@V!iR87eSmlb*uINKuMqNezje3o`iu@b(4MX@LbrpFP&+(9DM1Q2NB@d>?P}h>zvK}#v(Jbq(t8imiwBT_OS7bNjpXWlekVP|*Mbna#P!qdiq$_&3q6{@7xePf6H7R+nD@M3tDMNSywJmu9d6X*#QA4S1$)b75q2yH59ON84Zz^hHaw>94YHD(7wlO6&4LK#*pCO!qA)KC?mYklPj+%*_j+~7loRgY`oRgf3nw^}BT#Q<TT#Q_bTAW;p9KsMT%@EE<EkZ8B_UH4s#`ze+$z73%YN93~o5%(=F*z~&-Tj}iA2lP{kDQDl+??8jyqvm*+Jn4?yp=kVyp?>4I+c8ioXP}UL6#7Xpzb3}2v4GxGJz$8XHZ*^XOL%8dyr?7mr}=)my%a8#&Uk0Mee{5&O_}%&O`p)fVLn@2p^@EA|GY_Hya48KULZ`gCRVGx`Mod{WgRl+=x1oELw&vnu9Ewmn_<rEINYRi0sZkf^`v{>ruD4th?xXvgko0p<M^rR?!PaLfbE}Z$vYC^i@XoWd~|IYDRK9visR8988s5!8{gz!2Acv56EY!>&a)ydl<s&sB_7pOUZqCj=>D!NUEG8lE=ap6GAu_^(<LJ_yxT^<QL>i)OF-b<kQrp<kRFs)CuH6<YUxP<YQ!qkuaw_7{Z6C1IdTU2dL5H1LRn0KXNR28?`@q8+jwOFL@(*19bp-19=Ped$Q;c<SpbK)bZpU<T!@#Zwz61{`a9arj93%XRgK!;gZzv$tB4pr~}9)$iWQZAZlN75V;VwKe-V38)`ptKlbl84B^ZS;Q;DDasW9ibr4xJlq{NxESi!m>QBx}4xnc6$e)4dZ^1sQOf5;SOs+&NL9RruNDU@eBv+sYkt>kPQ45jFk&9BlAr~c^shP={S!XjfJ=sjoLrq7{L(WajMz*=4gDb`{gnLqJlY5dQs5QwE<c8E5<c8!1)av90<a*Sy<a*>VYGHC1xjaKSKQ%WwH`|h*AzXl(lU#sYkeZ7uYwe*1*4s15!>Mh^!^u(9*5oL%mD-AICAXutB)21fN3BEtj@*Q5AvYn{r4}UDC0C*5B8wIyS0PuWmLgXrSEGiIr@LZ|E9NkS$5MNd$C7(fJCl2pyHPulyOFz6JCeJSyHLL+cOiGDHYIl_x2IMkw<kBFhLD?)!>Ogo;pF<%eB}D%TGZs^TI4_@VQm`75KbX^T+h2Qu1HNSM;5J2Zsdw)t{B7+9!+gX9!(zOikhxy<BHr2;c5)wUalD8ic#cV<o>Q`O6|fB9zh*Nj;0Q0jNo}ku*?|7DAsEf&*!e^5RbM9ccb<q_hLP}F@&2_Ym%Fjzhel8P;-+*$e9_!iK*4dsi|qG)yQecjj6rJz1SCxJ^HILL%0UD3%LflB}2G9bp+Ynr@}p{!>G~Zk<`}IXmV?EeTHyt>Tq&xavkazvS>qc9r9lWLO372X5@V2Kx!j$AUTCA=DWT-%oTg7o5*{~IZO!Qy43Sz3E?JG$=8H=8<CrkJ5mRc2XU-)q&6paBoCl|M;<`_o*`_dhLEk~A`Ic=)Xe1M<ZRT$WcS$0My*U1tw_#B4rK_JWC)j~RwkDvm#3B^mnWB?mLZoQ7pImc7bh2^rY9F8`%x2-{m5?(gz!rPA^g=q2tTK$C#UB*o^!5CO%_c<mJq&AZA=!eL6#5>px2TdKrT#ePj=r+g&D$Ou9)VE39eYi5T4Hvo=LTlXOgE-`;bN3lBbX-Qp3p;$wR4O<S^D}C_{K0br{)w&yQmWPj$sYSJ+*#oFVMqgB5n~U5YNH+D!@X^1`#J3rz{{{=ze;b4&?)1;Uf4Q^`|VANM|ka0IorDPdni*u8flEPETG^-T$T9l~3wwM_|oBf@K_b;zPJH@Wv!gqJgfe`W}qSXSmN6GJ#9HIOWtf}E24i-8c{PL=s+J41LebrX3pIg&bz97#^W7{=$n=zNd$z<jP3L?@F)CwZ(TCULDHI>lq{F@<Xr(P<uQm1!R98R7QS*<{gqM#5T1xI1-$k+60W?m}H?B&@ZByHXb!32QT9_xeq^H+2bFbhVMN_7j%1;T-CI>T2?Sa&;3zII9UE{Dq${A%7u1qAnsYVqG6Ggq_p{WGDG1bsqU9`8IVn`8N3(bsG5@`6G1-`6KxgL-;dw68SUvE_E_lbUyhmIfDthmn<RNfGW@01`Oe@4B>&)y5xc6AE-^pq8-Vi1IVJ^lYbz)^L)?qh*~|)Yh_(Ti+I$n2<tAI+?3E3VQH&qHd8{|g+Eh6O$q%b{E1r9l+e$@()U$3hLTaUl9Q2Nb8N{Ndd(2NMSVoRMZQjTlCP70rQRg}O8%32oBSs^lL`8aEFoNo`jPyRZ7Ia|l_eJ<7p0ab7bOQ#OOWOFDf#`W7PTI^7P$hoD!BqVC$%6sC;1-(nvN_X{DGR3EFt`uYLF#_)6&aMPD{>94I&4zEqSTM$$81&P>YejA)8&%$`zemk)K+LoS*DZEkO1sKQ*99$P&UgsP7E0=qvIKay&!$GWBn=XciOrGWibGOqLLSPc23k^&?9NKcUK6?FmEp9`z+zezQAiB<ukS$5D?M3HyY?JE*&jguO)JE!3Sx!rr6s2I?*&Vc$}CBlWnEu+J&Hje5~Y*cTOc@0|)Cpxz_jV_V$&uEOrUSz!nDtC6smD}0RloGf~uEGlbC_nxruA!=b$!XC2lX=)f*G~AT1|15lo+SZh?UoHHC+Q*czzb)+E0~fYXZKi}hbKywp1XIGky6|A?G;&|+JnA&E=rU8n@AAU#HKg!z>U>keI#YNtbtYMK3VAVkE_EV#E_ph2C|PtIS#&B{bPjns*_~$&&m+2!ypZ)1o@L<g8szUAp1O{oyW$Z;_?g^GJQlvsW8pt}{ETJ)B8$HCDD#ZR_gG%Mcdq!G{F29i(z{2#?TV{B{=nmV^nNGbBj4wDKX{b?#P6i{1B;i|565o)!0!dp7cY>Sg_^__X*`b8&=Z#L=HYkb^E}ktR4JR)<2Wlr{B+c$<aFeeu1H2rOifBoOg2&d$R_eD6ZDM<Eb)eY{1=a3(vx!U$nWU;v2Ajkl<eoxX7LKKozkXKt|&~eFn!^o>=W@qc<koF9^VV(cgnGhd|r#k!ZoQDaxIVJ5ay}xifa6<A&=c$%j0|1n710sR3Vq8UzW$E8P!;(3d`4{FUOUs^~j=iTv456>-c<DgIb*|TEP`n$rX9*{;Vo<RP^{<jw`t$h{u(vLHw?0aaZJ`2C<C$vx1BumdU|mH;aBYLCt>h=a<N1=4ZL+NtrJud`DP9{EsF?Y8St!m)bAEOHN-x_$@UNSwi@=2_Y=w`W27e<6M0Ay^z8W_evtN+mpQh^pks(6HP_+C(GxVc`T9L6*<Y7d7O&J85#a8lbQXKotl|_l!2U@k(uYo$+G#VdCB?6#XNH5WeArbmtYw)uT2Sta40{M<1*Axawx|_ZI-P>FO*)GN4YSD_~FzB<Z!ZueqA0*)TA%mkjHh&4S3GF{GM<f9*fo|*Coq$viV_*$yocxgk#|X^yRo9S-kQ*7Op@RuPTp)OZwp+misc8EM5^F3+E?`_YIGQGm*s$;IXhl7VoC3eqT-S{xIQKSiDRudxgGyeu*sJ&pZ}B<%)P7pXTu;Mm)cBn#b}z2g`_elzN=(@Hjrr@;m7tB_HCkgM5m*)fI=Shdj!jWtp=)mNMsfeAweV+vv;jF@|s~bsJf9tt-~?du!=!qZdov;))IAO+0pgwt?T<#N*B6^{&`Uc6)2-Z{lZLs3%-;fGWpl7{dD)dzr`modaai-3;L))So=~gvYVyN$O<}zQ*GdWcTO7zmi2S@;jHw7wP}Pxa*2r^zPETMSe(qOnyjy$`F3ecwxfY;W1gf*W|bS?1hIX<(`nAm=fl8;rG-Bri5pK@JFiCl<*u8{!G127QJCgc<u<h=LgZ>s5i*JkuNaLyW$|d^B&%Q`UlCos5{8J$lIwK$=k_s)IDU;qvSZU+<!9WcJlL$JQj`!H~9r5`hWf3t0ep<?=Xhf|JjP~H@*Ml+Vh(Q${PuPfE^K@ME{1*&-Fj~!;rS}Yq9Y^-`mBY'

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
