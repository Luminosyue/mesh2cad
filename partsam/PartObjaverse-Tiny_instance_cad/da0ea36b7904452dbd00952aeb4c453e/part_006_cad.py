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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_006.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_006.stl', 'source_sha256': 'fd874e282caa056968b3670ff302a435bacfd7f530cb2da9636f2caa8ca8dc39', 'input_faces': 854, 'input_vertices': 613, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3567792773246765, -0.4266328811645508, -0.4753398299217224], [0.32941940426826477, 0.4719806909561157, 0.4753398895263672]]}
GEOMETRY_BASE85 = 'c$}qu2Xqxh*!JcIP!JW7UT**mL<AuLLSHl#DIq}U?NSnIK&rIh(yJ(-AR-tL1r$&qRFy2Dq*6lfTtGlU!Ga1{_-E#M_GWkGJLf;&mvf%;KJ(1G@4h>`JF_!)_avrOaGoL>{z9~b#l=JJ*VQzMf?5%6Y~0AvgZjmdsy6J6@j+T4rOQ9dE{^WlCZ=nUHddP$+COeozmcK!yrB)^BSWitL*s{!96hqnu-?N*_K%Z#vpz#d#R+}Xz&>xpiE`!IHNvZU!>d&FCVKyue+5Je=D3rmQe-Z7p1;&s7=P3=n^SDMey51i%_g-sD?9Em^qam5vh0hGSfAq1`zT%SSMYObjd3R8U)ga^mc72@wJ8pLr_#0V1=p$V#_dF$AI_*aX0Ok7q&W1m(7PYoq2i6(taRh*3+GjwHZ`}VIP@2lp44jfR#iXl6U4bN>8v{5*GFzid5o^NSiMDU_vS+AIbWYr$J72%EoI-FrF1iU%}Et^@S_@PyEjK;zuAV;y@Q|pFy%425tsg<YQHgmo>cpfd+mU#KV0BMicL5BL-$Uoa>SwcqyNY&+4eXFb?wmD<Bs?x_J6AKyY%B}hh8aSy~^jP?}S75R#N9rJ74j1iqroK<$t7_%F{nGR_XpJ3$yL{Te?YIWB!(I7|@fLf51QSc9yc4H;&nLt;?mc_B;c+54wK&<ueXFV)!&1?_a0w`_&?$TlpuA$OFCp;qB^p&-rnlM?6&ZT9uJopkG$Hcf@t*mESRxex|cJuK~RUbn|qi)4%+tuT(zg9y<LiLN_i<#CdrmS?T7~EY&{d{wX;rHr+P`y1wt%qjrBSJ`v|Vt<o{OztNw1dM(wSNyA=+{?<RLowe-P<0&>>n+)AZd&c3fkKLG|>c^ixZ1>m4K=;1UD%<X__5bo6b-Wk%o_55a4&6L6>6F9&--@eLdmcXP%qLGJrRy1sRX+N#D#-s%xTC+y)gv7Jm3LSL#QFX$)o&Q=uX6P%O82tA@+TC<aa}p>=$HHnMW~;0^kZg1L7cB2?mPOcT>XKgze-BThd9@os(#5}zm$}amwJ@az3j(~g!`&Jj0?*h{Z+31k+Z)VnxS+vJ4y93I{P2D?qmOB4Bdk`>2pq?TtfM~b${GW<?kKRSLxcWCF=S!5<dSr#ikq7wS=o*D?6ko{O4>~rS8K{RSu@u^`8f#e;oW=mP3CdXP&aX^QSxF#6<N|*LT9!ES1;b&N!~_4^mb9mLdC6Y`WfY)?Q^hJaGX2o#5}QwO{#lIdU+?u6Nz4;&}T^Q~Nas<->8cZ<?Xn*Ec9V#jbaNZusUYe|_NR>i#prd+$|wADFD}-+&$gT|clWN5va3S?Sub(D&5-Zsf;xH=rx@$Y^!lm}d`SytMQN(5?Q;A0G|fdr$S}y6AsW?0V&2w;)cMQ?L4~qkr?qw}L)9N}Vrn_qu5*c713KbzZ!^pH;`36d#4->V8?Zo3HiTs{Jip@3>gCzrREE1MqKxIFpLwe5Ym}O|j|5MCf|cti5*KoIwA!7x&rY7}Sl_<3}Cwf9~SAt^#_@{=W9>$B3_o_`Yz*^$^gzZgyM`dVCn-WDi)P+Vi`0XVrFbg`t=D8{_N`pPg%L*Nc@|tMr?7&N=+cB`aO~dB6pSf0-icJeqg=TyXeT`a_Ku+WjGy9R3w=;rZ;(A(!C)G|yuL=XtdBp_|ot^z|-}>pU*sW6z_d>m3(5&tu%99Q%Fk>zbw7Eug#ZUnA~8&g1S=OLyO=zTU%+;<|N?vjN>T&IWYXI2+Ji<7`r|MoM>&vzG22XD!`5&RV*Aob~mp4&61*TDp6jwRHD58_-?jY#@$noDJx%aW<g4#@T@G8fVRat6`kad0Abrde2|JRokUjI*j|P<~g+Yt#6cG_1q!lKfZ?2ebv9-quOmtw$inGZO*In-th%oC)ADKpeOYY&#?RJzbsdAyrZsuYxnp63|(*WXs^Tnt-EN?fjOCWe|<7^-`I<X?Ec31dCJe*dig#_KI5Qk-PRve?QkF!`G4Q=9JbSOyun@IKcWHJVf_(xy#9}L<axP;(vvQCR{lnKG3fPnVO%QsB*y(_&m+#+X&8SttU`ahJ4oqfzxsHN2;QEo^2zrHp0fuvM?3snS?$-*f5P+hkrc$=SXIUGX5Lo1e^zVcvpGbaM<eMHuKQ*27+06?R{e(_b`j6(sXg&LG9tg)uhH-v;&;i5aj)@Nj3<S5BcGmlZt`v#uAZZfmYd<ft{~!H`3L<|!Uyml@CEvn$Q7y`jNS8bzpX!jc4+;Tim$Jk1bx&{99O+YIIbq+pugP$&wZV{qkSd}NBkXI(4U>%3;&Hnaa<Yk>U#G#si2-4Ej=l{JMM#KEjQc!^|`nYjp$*?c7JmYpM%>kLHi`fL%+Npd8TAxeBRgt`P}(UjT7du{u@&sqkG4X-l(ph4c(CE-KQ~5yt+i?Y3b%2=t(X1pglu7BLB3H)bV<I4B4jg*&l=arxr#&#uS{dn{^OBdOOZzzuvplby%Y$^7*GC=0(x@)p<0diot*Svv^)kYl-K&-=9&sci~QqljEA=JWhVvaejTjeuQ>N*@k&tg$?L8|IULvTO=#pKd}_fW5}xAQukf|68H1auW>!3bW(Bjnronc^B%^r&u*)HjNg|b&bei1huE9Dala43{a-K>{oUy^JC*;Jo$#D-?;Bi)zlEy!M(?(GUMSBv<F={$*DPNX`p!zY&X;dP{Mv_9f8p!#39h$G*|^`2Zd1CM`6c2M?Wp{<{e$2iy9xQ%t*HFHpY~U}G5L_%k5@cTrr30yy1(_Ut#;i^gl@(>lkA9N>3vpUeE-J>|B+j9ULKZK?dD$-1Kqm*Uz>pIjk<MT=*?HF>&;lx2>IL%LH|6W$fgvV?xk){>c2^y$2Ae~pL^1AA6dFN=cMC4($`c#|9iKf<NCLB^G-p>^{;($BI9xSTe>@cb9HJ4^7lIOw{$P{K>n*YDczsm-_dVadQy5fXTPy}Wd`o+Umf?mrTeH`_q)EVuX--i^g>P5b|<%-bm&HdA*!6SQq9A>%X%qY?|WB0uWDI89dqcu1f?4X&tQJ>{#eYn+~Y6x|BS!X|1<tl|Iheq`MbwoOLvdI)_&dNucf=jU+=<LJXigA<^$E9N6_DU7q*A)IlDsH6J1Y2kHNZFuca!ke(-V*^l13^siWFQ&%BHKb-_AScF&jHx;0<+Em(>6b<LOEx;0<+&wmxVYhE1Czgeu#lQoYv=H0+^v1?u#(Azh6%tO6%=PO;SjCr4Vx(U{uEZzIJV?OAeI~RJsDj%zOM`xdK=$;2F(9W%$`cOR28^?aab!h3n8grDMv&E^$T*Y$|=f45H&J(FBAI^WZxig`==7W~*p5Ixz-tCH-M`-DlkJ)vT^A|0x+%bC`t^2N2To2cB9PzvEp#P65AOGwI@SlHA&1>{Sn=$^(t_OX|=rzh7uY~o=*|nh`Zt<RqcVeQtUIO}_$ahtoBPC8iuZcXn1;b`lIPTE9OktiT?%&zf5XUu759pQuaLntqnRC_lMz>jrll9VZyKZ*AspeV6ft{)y{4*xOFTJ&DcW;*}>b~>On1FW4n2LFluQRU08AGApEPh7mt$s;`J{a+Dwo$qfTORYc=_N3K&RmOmRoC<CKKD*9#Qc6j{64{$_e{^n_(3X;zhyhD=S=%o<?a2xxze=`Z{j{r>|rYF8aMUCF3__)SU>H07X49TCll>n7}sU@cIamln<-ttz6k5ZE!(1f6QdC4`fALtTBj-9JE<Ua*Es8)ln3!M@1Q+<grwPZBhwF^{aezXKc=YtaKC2TANJXG^SkNDr_BhZ8}mMg9y$j1=h^qw^`p<2u5@2%tb^)5yrp#G_kqx}>tmkXVfX=DXZ@9~H=BU@McM%RcTu`=XezFc-fPjGzsD%uf32;`$7s0<_wnzo9eMgX4pHabEYTdtHQvO!^?OTHeE+=$O7~_*VZI$(AM0}WA`w4(0`%TbV7=wRKYP^nOAp}rbJ{@US@18VYtLT9dU25+xQ~9jpmhDamMR}_i{-d3FP~Gok!JzgEhkC&dw<J@|Mhp#&aubQKJ!hb`<qncy7)}Avv(Tee7qZRs;p4DR-_K%OgM$->h*o02OUu3r@5dh`io~LAkPzPpf?MLKDrI`zp5zRA6*&0tCX6G{nkmv_;B(%`lF;|)$bX3CMn%t^c&>)=oHq;hm?bVt<z|q;}0>fZ*_9F@*lGi=e<T*<hd+%H}1=HJpcc+4*nfJ+NJyxc0zyYPsG33OX<eNb1J@fW*g)aa%HEA+o~vztNkSScR!<aJrn0kzwJf8eRZGGeKQIwe|`8C#HqYU=}GUWqdn)YK|XzpC|yel#_u+rkHi1(zty_CcL3HkG=B;BXKYuxQFA|@|KIuudSV;s*N-UOpH>%o!&mToWBD|++sAJp{x1i&t8$&DnC~aPiu1L3z0!5A0~pK3;rfizmF}yAbpY*ZQTW$<xJ|XoU96wzQ<lL$U!2l?lcMn4d+KTUA1|kLV}3O}kBwaj|5@AAbF}|qJv<NZsRsY%A1K|3Kz!elIOuiq%vX81#*u(t`JrPRv2-K6pJN?6;9vWqV;wu-AN?HGh56hP&|S|h0p0anWa;LvOOD?c0{*V&F1KzycLnmy?&bI$)~yGAhrLk|^TI=`a**$r`=N&_T|ayZde4cfKi6))2L0+4{I1*Tcq;VfO4qIxM}OF91^UD9zl4A0M$AX7e)#(orTen(VSd5>*7w7C<dfYG{cz{!)p!xmUE_}Lhs#Pgvq#`Ob)855o6M)A%14hWyWg(+uRewTJo*zgzG$}|@wkrQd6E66cIzp%PGDRs=IAH=w<kh(jlcfeZz)~Nz`V&CXD!{I9?RzejLYWjSxWa_3v!IV=Iwb(*RMV27=O(Nf2rq7eL;r$UD@Dsh56tKtZ#kSn{nFF|0$*G=`T5+H_Qjcm7a9{Q{`_xSD1fiAx>5qocCUP)p@scGxG+HtJ7kf-@lJT|85R`?`-|TKIo?ze-Fl^jve41q@}3#S=k8V=RvHqn?ZS$ZnSHR=Y{O?=<kDyDBbK9#OKBk+}D=g<t;up?os!n?ukVF52k;n{Es(0>CoSuq@H7q!{^ce2S-6a(PEMEKaAfgwcr-eZ?ssd{7;NWzZ={Gx~o44=#~F<_9uC=p}U^*E#3W`ujlnEUGH|;@tkkz?&tP^fBPADj!Pefbsg$vyWY^#>R?_F>@ih7GcTy;d?RQ5iN<z)8h-yWj}CL{#t1bJ(vMv`;fOQtIW-T`bJkHW0KMlq<Ymows2jC@bM&iPa6$OH=5Ybti{GcMd7P0a9(v3&_P6L)E!{nTH1noHAA0eKy8o?ymAd|QapcE-Sbw6N%Fo^3x^=6+P0GI$dTbDW$4LvvI$!?XN;f;L!n`9Z3gdHuY#hI_dMw&)4ce{1Vdw+f%~1X)x2fwb>FH$jukLjW>i=1<uypsj1a<fNgH|XS&)2T?5KDKjdsw=AeIpRZwT|I`?jZbK>ox)1wQl1re1ZLOi{<J(ofw93tnel1=OWeps2}Zyd3VXr@Em>hPj!7HwMxZ0A$9Z813Zt#+}UdPH?m4%UeJB_cDrt7EXO>&^8`Hilx~FiN_r2BQ*YE%{ja6#Z!c5*usO8AH}Kc7eskjx`oo^>ciMI1%9r>Zy6*&xXQf+0zgB_sop?OQP*1uXj`66&f@HhDnfV>^>Gk;zyY9^xg5Q<9&BXf{We+~q-_rjlfA_d%>DGFz>GSMz#OJu2)IV&OJ^p{zW6P#L_INGbeZ0O(<I*43o|bN2{ljtIE#2MD0e{!^5b$?h4*`GI^<e4l>%r39*MkvOAoFqeucf>1-+=DAe=Xg8|C-U`l%CXU7RIMLhcNyozoT^DUsG|sYmTeyTYqUG^j33~?&~%H=XKR0<oWUp=nqS(=Oul?`_L2TBhCwz5a-ur*zfjfn6E|6#D1Hsf`7%m@GrIj{Xo?<$luk^Sh~BPv2=Go6Nuyfy)r6U>E=Vcub0#*1NwVk<9I)riS{|S3dg%A9r24-J7v#PkH}QIcjC8rUvJ3`=pl!&->IQ^FY-|p^cPPbMgA>b!F5=71KKU}BJyc}5A(ZI!FZ0E^&Rx{1F&v2y~O^<>SK})*mZwMBF@Xi!RR;p+(Q03&ad(95ab#C6V6LkBI2~G27U7{@E;y_%5hvp{y_Zkc)rmmpT+qNdH}unF6cjRMti<pAj`gAs~z;%=kZ?2<-BOmU560AR2ijvf1itXTic!eh!=Xn7jd7C{|fO3S45oPaX8+VA!wi7Vet3#MgA-5qn&G1h5q(fTyO8ajqA|+s?yD-WfA{Ob)K)Lh;NQTKFKw)-)YUDcOQ-Q^i^lk&No{kez#umKeGmLYPU!H_bVZvIa`ru%ow!KmTsr)`TJ_-!TSsD_ZX>bQ@T3ed$e@-`;FAy?_HQzLzHed2*td6UIy~7-9YL3Q!hXdDS~$UI|}h*Dq;RU#DM?hX?UNpMtRJm>(#+=Ma;*3CvS7S*J0^e;x@;79hUBXuOpzl-s=d&alO|O&|U9!1a#MX9Rc0_{^X)}u-~uC;<!r0<9Np$#{RDqhkmmR+Nb_$9Pf+J%^GuXT^0Ws@qaG@J?%KwEo(oC=OBIMBxU*DPCz%HTkq`z^s<8;@9hNikim}kc8n$`)bp$ReK~JP9;_F1eIN6n$p=&Hy54P$(v#Z!q{a(hNFl5{XjN9K{JSTlIrQv-i&dO9I9{znE$T}h?|o?%>MPx}<|%qnJeN~9x?hAIGX%doRd^k7?sxe}T_-(r(j2<=URK-UX#WcBpu67t(krxw?t0%WpciZ4c;76byWTeo=w%`t@0$hmihnrXD@&@-8|~SzJm$$AO5%MmOYdJ6>jM3z;dj#t!w_e5&TMs^k2!zHq5Ce4Q}_RXI_PIBjD+r*CtAAoexUdDj8wa>S?>*w==6;}j(c9|uQ2|x=gZRnbG|Ch;`tirJYSaXK3^3V@O)t&=bxx2IP@1ezv~oy(4o8LeF5Dyzs~jdsOL6oer;4-2Ho{uXh5&q%kdtmS?Lyz*Y!SXKo5^|zQ6inGyG2Je&5y7+rREu-}ApX3G?!PA-qmXV}4@k{mVP96K`lD;&ffg`!^H!FLk}!Jl?;z@%u~Y9L!g>x{mudpdX&?xPQH&bD@v^#c>@5bYCyWb!ddHMn10fNlVvuEp@C<YE}M)ziYni)~)%nUL`-q2iNb;Zr%Fb*<U3R>(G4P+j<Y&ty}Mbd&8Qdzvp}A-Zs@R9}H{e(5?5+y<x4fU%tog@3k81=>gsO9=kUz7IFBVeBisDu#OJhdVk&s>xw*G<EEv%$4yIjkDCGAHEsstxW>(Z?ix1(x@+7F=&o_o2<r>|dqcHDQhe3*DGuHF9f27(2-^j|Qz(G%ssg(6I|Var9Nq(UJr`NJ`?)BfyPk_I-ThqTuZrJ)+~aaUca6&d-8C);bl14-f4Lsk5nr6@SoiZ*i-KO~65c0c|KqLJ9KQ!n?}_&-`F)V38&j^}c=;VrKzDsNWa)Zh0<NFK_)f#p-QNubbk}!70p0c8P(XKmH>8En#k!#DyDdw1f43FTUEgh4y7k?bb-aQ2uJ5)2y6d~GfbRNk%jWO+ZYwD~8T)m8r{>nJ-$(r62a&(~d$))jrT^#qxQJ`eUEkTcb*sPfNBn~Q2EOA%f0e5{zvD9_?jsJr2ekStw{G=UW`u^kUEd+*>dx;Fy|tb}zs&C(4c_m$y7N0nZ>^%x`Msodzq@sHzsESf8twgB_jhMk)-;LyS`jV2kL{CDDat>~KK_%@K@tC7pNvM<iuk{NGFmuD(~1g|q%A{UlDrZj`3nLy1!@RX6{sxml0X=3Rq~fv4kZueHqurhuP9JfAcXdLa%l^bhme;Scu}B&EuRX^u>$K$(iSFvg}GJ}h!CjF{YqPlyaxHpwBh70lUFAsuS-Z?pOCyEZ7uSK<c(-+lh<Y*jR?sbFo&8fN02ulB(F#N3VA*9Nak6c$5@^DRimv#{t9g*Z5{FkjMa!X(w18!k0X-))^XLb9eW+_XREk|Hwk=ByN+DiPi*`{mZe=vF6{?4{;t46@`bFE+B+=o64)V-EU;PNOMz{+@;2IytXm=Qk-&QD>scrH7c754zxA}sxsBZ45^8drmCSt;_p^@J#(jNBKTF?8|77O;Iqe4W54i77h%cDeLhkbeVg>6qGRKvK<jZJ3B40-SJ|X#H+U4X+XjjlKCzp9`Wp109x0PEm^<CuK$hUEut>l|{%qw{gS2CxiwC|HICAZG^JIred`C{64$={{F<X<sY*_K-bwsZf|?zH8zlQ~Men|v3!?8g_8zfHT7d?#bQO-MeCkbDa57V@dI8)&zXZy?`F{uO<vlFuh3UqF1t<61!b9&=k{%lSR>_vn*C?BMZPIZdOTZ_9r^k7+*lVIAWF#$H4&W9Nu_`;fpH+AMNuPuO@m%hG0(OMBYJ4-1?mKgl|&9c6jDzyX1M0;vMY0y}Kw9kkn6mm#o6U>EgWtdsm8%LnPVi`L{ea(_pt$!$`YyR6To&o*wCLP)-sb`SYp^8K`#<jHK89Yhw}FP(fFZ8Et$?z3#qGd$)4%s-WFmCCj}O=Q@P?=+7olgDs`Fj>Es?QR`QHgl2t%(3nF1oyp<JeB8VACKb@{ddrAC(q_S4%6<po$sTze2y~5qpZ)Q-A{guImu%`C2*Ykkv5GyhkQHjPV(*KTLt{&w`kMIf22K5++y92EdNA%iu^Y1S=v+NXUTKOkJ0xw`4vL)%fvAr*JavE%*}7h`4agh`fMc*@c68pex$uZ{v-J<+RNm($o<4+#?}S;i~IW@fq%($>cfJdNn6+h-dNyo;nPop?MN>159=i)PY`&{11rn1+>hKxynrU^25NxhK_1k}{lwEpa#{CC*f_aQ+5zM;uH5${+BkBVugtrcu-ApwOz@k+-qB#ASeAMeA^BSZ6+EyNJ%Hp>Sl5hv3VCx{xsT>7OMX?hBkilS*U4WcZ%uoXyft~WmYZudA$cruhwUiOk+e-{?~vc&@iieNPo#Z|+&a!g+7jdvl24#5MqZ5VIf2)MPOftwl1~;e1eyw5(_mY$Y>>AgpDIwv0~<nXkV{BjoOUv~gycnO$CFEp=e716c>?QSB~Ku4OnX<$y;kqqu4QT4(%vO+OWsD{HQF1rcgdxdac{6J`D@(Qc=GW)me**TlD|g&otE2nl1tl!yb1UH9qkQ^b30j1<av<iqk<?`6sSZ<{(=TwmPgQzA|F9Ml6ExtNb-ubFWC4fmPav`6@LVMMsRz{Ula%xs7y#+g}N+{p?#Bl4Eb2vapYskLusqn_?s-h$yiqWG4vV3?IkZS?>Bi(X@KOh0_9j&j403gaxAy<z;^I}OGw_DHrA6HH`bFIC)Sg@O>6E)+VYHDTA-OIKd%9j#|V^SU16d$>r1iR+ymRz1Kx}_hLF51<HmS$<HUHJ+mzxyOEY#^ftI2ymobWvxAQ=k<ubHI$;*(x?tyLZ0dGm$j*z@P<F=!3QF8k>Ww_6>jQzg2rk4nOK}fzq;B$fZY`Wy{)5^NVwCl*1&~6|Wv+hHIWdiF7$=3=jW!*;NL)I^4`2*Tb<eRwN2gF)i+;z-lJ@s|mcD*hC_4L`mx-V!qF!nlbYvsR|dMkm}0;On6lNYBgL6l-$v_KnbZRlt5XvT|XEXh3r{RDyu$@^26WsNq7T-rY58hKx$54Z0}-k<vp=01a|MKew?b1qF@g1j~BgUI`EoBk}fCYO4QKwE)gv_;4}vD}$xOW$&=^Aep{UykJ>w8hAM0=)#Dpv_0#ljYt-FZ$+TU0$Lm>+`UjkI2h7ow=Qt_6hRdEXNQ&`o=IfYrn-9s~ESl_UmP=BjPlDDsYH4iTq=MY?hPAEqx8k+2n_5KP5j*E@ST(I4H1+ko+_9)vVu7en4QYKpM-d$q#UwgREamp2q!t%=*vBS25>RuJUT;wU*_z)RMUEr?%txjP*lB8x0ZoQ-l3O1COH~Pe?9(AF=LV4Txj?BbNW5{gZsUsGBBmS%bZ#<#Jg!gLWqQ1r7G12FzgH1(q)n7a1p>+yBdbUFQC0QXfi8XPz@zzQ|+$ld=9~yg!M{)b9zO-vr8d0Le>xpv&^_v}MU9B>#i99J#cm$^T#s87q&ldF6OXNbV&s<w1QO@?b)84{b?u4|!f%FL_z=a<pX`y9~E4OO&Esl69rYOR?-_xg1fFK7++E3=(*t!QR)v|Dt_JNPeGuKoIKxA|FUdKA3h8`MUz|2prd7k7?i%lIPGKC6{(#5O@yxBF0(7SnrU_x`*6;0As(y{U4=%pE$<c2XVXmjD3{#0~mJ@@eci(iMl9(VT9xf0&fVsZqp@iMl0)D&<-b$qD>%Lu&z1lto_JxQ^sjUy%~9PZr93IFUu{7C~h0Yatm(Ln|f37Ufi}1>zkAJrrwg}KIA^4CAV$KSdz~Wm?JQYb{_dG^3$~E$xqUrB~G*MB+D~s=h*mpmd`Vm<Z}gP3(O=WpH6;?^>fM35t5%FBtJn+x9QUvYc98$O?$@D#WgWUU^XH7Eb^~{P(PP^3nBStLh>((SvGwZW6k9@b7(h{&l7lCU_R{v^7-Un(|$|7oAw*xYu4>%c^>WCHvTQk-!hiuFN<S-NuUNHd3D+e<kiV13rrF)Se`&`=`XWvkk{b0lgTHut_J-l&~F0wC;4@e(=~w~2+42KzTyGDNgg3kQ=qm7<yXipUB;?S?K<PhZDsurw6)1=a{KFyE%zt+d4Y2R7YNBOQkUfh9@vH+a0$ul(>5ZnPcFBY_F_;jZ^&{(#<Jo!pnn5yFL_CMZwmgL21p+5fiBA>XbX{-AaCJ;ZQ}uNN*hf`-iC3b>05~0zD)`4vm|3z69^M{g|@1V%ewKjiR2S$-y+7dZX(N7X<xDNM3xg7%ZfjqK2}`GZ-_R!D)2q+cQ!8Ts(WC=J>WHHYY~!%Q<r7Ay|mv4<??Wr!x_tpU!DF|T*>bU+!gqlko*_wvfS7M+r$GdA-PWbD!EQBx0m*ppj_UB<tB_}#cxdi#@t@=D;m~x<Qk9Ujcw(Ytk(tn8rBZ|EH@H(Jt$X`YhQBB>v<2>$BL4Nu>2xXoO*i=>s;2lmR!SXPqbkkjkVmhF1a@Nf(L7XCCG~q#i&VMm}R+!Dc398(Z-U$s-dnC(VDtf;8{(+CILwPG*M9C8G+6sZWn=00#O1T1zsa0m-RmgzYYR@HSj-08%+vAS#qgO6!uqnooKKz8o1O8d7!Nk_(b4IQGUV$yP9RGuO?Onp<dd2o?PBVU^pT9&l({4lX83zyc;#EEcqURo&r4tzGYeRZ&>b5+k^ZU*+ydfHwekw6KkkRo8JSzhyHTAXN2~wz|$Vo%VR4b@RX?UE>Mt=yayq9SK4mmUC9g3<|luO+vg_=QjZnrDBGI$Ir3*{pCt;h?irRl(6%FQ$L%{19U1#0fzJe%6Ow;QE9*X{T|qAGO7f4%leq1tEUzS&`U8Rc^7uS}<OSGvl0QxR7x_bZ>>iZ=BA5CD#*p<7$z|O=ac)M7@^2a-`6z)mX~z+gkESlmw=~$>8o0Fg$ZwI$cwGgC%4?B!2ze*kK|~kUbz-?Q?O^huj5V0(O8r-X5h9P@H9+!_LC|ISN7|pre<U9h1UoheTy7(`9ZQU${si0oN!kMB@>(v$wv|5lSf46lW(t_J>EtH)UfK+DX|u@plJ6rVPo>Qye^OIFO=<ZE$u;V-T%R_Qyrw_|%aP>uxm|>o`ximqdIGfs>JpNNYw{&B)ICAeV|_5oLA1g24W?F$Hk`bN*l}NhUWDZRJ<w%2jJ7IyJ%LD;tCELtyGU-^pIrJ@5vU{Z5+QkAf$ps9NmOBdKY>0ry$^l+u&xemUGiEy_S%Hx4F#T}%}+FBoot7^Ha#zW^RlisZ7p&S&t)D$@&bh94QT6=%kx%;<@)3exNRNA^N>s5zHDnBA$d1K^2)Sf<g#6>u^dKTncG(5dFV?X$u^R0`!XSUs6bcR?nEf-WIOk!7Sk%oQzZC*`qvk^fAaS^&GC;g+*>+df3$B|Tbz`@%aAdx^2&QfG>}LAaP*+BEd4*m!Z6|'

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
