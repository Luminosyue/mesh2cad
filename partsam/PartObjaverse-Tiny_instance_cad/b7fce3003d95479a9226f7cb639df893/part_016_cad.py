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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_016.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_016.stl', 'source_sha256': '090c36247cd6f6b551d94d03c51cb5dc2ee5c0e2c4a26a8537231bff9271e1bb', 'input_faces': 848, 'input_vertices': 512, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.38022857904434204, -0.2838820517063141, -0.24899092316627502], [0.21970006823539734, 0.21142345666885376, 0.27436235547065735]]}
GEOMETRY_BASE85 = 'c$}r22b2^=yM}v3l#Jvc%BVy|egug>%Ag=3k|hc_L_radD3XRKiXgBg6=euYh9zfqSYS!J3yVuo5J!R{ihzPhl3U@ap{Hg%=bn4l^PTsZcfR?$y1Kf$dU~))gG~45cl6(5PFjse=lCl)j*J{merI6UzWsZ2?%J<>uReq0oQISz|BS{rYSFMsn>c5nGo*BvuKhaqEnUM?x@Na(rOSCrckA7^f8UP1-ss)8OIPW?)Ujv3uEOuvy<?xQ;&qwI&r~eusZ_R{XPD>z_?JyI!Mmiz@kH5{ilG%s)3P<I6~p)Teqe(11JAy!{Xfnwcjw!_$@l(MSNk<Hbp0$PpH7V7dwVaKDD#7HRh935cKlj*ecLzngAGe-zxt@P?)tWG>N`zJX#d3Ri2Al~>U%mruKlye5>)=ai%pf@Dy;o%GZJ*W`ma!RvYa@k`)x`@|JZ)Gf3h9d{-AM@{bTv2{oWb-mG6K4+A8&a{>(n9p(V*WKUk}e>KFgOA?moC->mb!#n!9$Pv0Dx7{d>4KQY~%?<7rF9V_4XCg1ZIb=tI!=zrTc?e{&gLHoB3NA$n#hx_NwdhK6IRQv0#m?J^@p%$}sdvf-V*e}~R?KFOPe~&L7lNiJIUb!+WqQ2Q*E8qB0`Gu>lj@cgkaKGL6iS|2f{amUqp}gL&TB9S5qqjh4X<`iD@m*K>z5>0pKlY9qhn`<*EmHY!yh?tlcB;;pHLH~7sHJ`9{x+)4f)08-uCA&5MtSC_<DK(CmG9Y*U;FuX>i(ZHb+OuyWqXgt>VMle`)ho=|83v&XSj~l|F$2MZ}q?JhsSx!6z%t%GcDqL>DVa3_t!~P{crohj0>v&gTXS|-&%aCyPw0pukKWLKL_uQ%20mgU)BD4nv4mm{r{`E_J>^2{gZ#vHgz0tzpQ-!(T6su*XbQqzUQeT5x)1$;VM6{HjA$FWQ9*vo%0K}sPXmY<!_YV^ry|rPuQKL_V2<4?O#1KQ{_z@tMWs8e%5}SacVsIuN>c@@|zyh{@$ObtL;^OOy_4$*Zz#<YP+F&BedTtMfv`Wq3X5&ax1mnkbjrX&)%K!)O<&TfBViXrAtR`SMT@Tru|ud)jxqdwN;(qqB*+$>x-2idOAVX3GSR6(N5>cE!98Xcj{~Z^#Zy*WuMxmj@$Se-?;lfFz@tE^*Xt{_K%jEtMZ$z3#$D2Pien@qxs6O-bwkv_9eCd+&EqT!NogOzkOar`=`4pKUiwf?g*cLHoj9b>o@M>>+B1t_V@>9*7>;}QR6u<c;hbhxtp1Ee*XO0PybE%PQAYmEB{Pzzj_^a|F~Lie^QApv3zIrH}hipfw!jAisfhjWuM#kj5(w07u>7r2ZlD+`}@)H!|w6vojgYEm#5SLoxl3b8g(2iZP~3}zq3R8JziAT1z)XY%6G18)&AkPR_o6XSNrR^nV{<rs-xz^K+|bDf5umb-Q&SO@fF>lndfQ0>&2C-A5Ra{+buRm*KgKQU#BuRRlc{}2%X<&!6#}zmo8HCM%ZV5FuteTpu_It5?s?MS-pO@yUwpZU9T%jmR9wH>pN=ycaJ(x1AkQ8qw06UXB-AU7^BB+mN#_$4%ZTuzH%nn?K^wxZ*%+3rVf$ymt0c5|3>@6?r|j+nyQ`7Yi*SutXW&lJH9b~T?gOPH@+v=i`uVuUY)o8O`}!&gL$9R?Yz-YwKLSyt9<99nmYgQ8+v`i{2BK9FPyAiGk=DC`uX2{Q^%iCBVvC&t=8%Oxm+RQya;`HS{(=5_uT5bJ|ds<B`P1^&Nt_gop1c8e9o_^eEg_<&bz35e3S2aw7hO-#+&;3IQDNn&My{;I4=Go59s6aN&blA9?G37+3lO-Zv4P!*>s)XavxB6%mdzA4@QiKV1s;nrSD6)nXY`UgTdn!_b6@lOM1lk%-ccb`=_5vcegXJKfm&w{b||{URQPe53k>=v|6h6nLquRe^TQ)xMEjC{m{o<b^Sg`5%s-;zEl0+N!qIOnXjC+19hFD>(e97yZIwj9pi`3JA9|?;)wQy2DQ}f{BUkWdwd(q={l9;siWtsP`Q$N-Y7CQ-F;mA*+10n#}988-?=?N``NapCc2J`zkM&=o}T^mb?WG;eQrN|-Nz4(>!y8ky?dq17Il2Db<sZ8eQ*7C>k{2Q?GO9wn`@tWEYxnCs^iPuINd#df)$6V`PlaT18T2R`dY1se(=pKxYzB6=OujaOVxB8u1EfIAL;#i|IQ(I`+ZqQs^b&(X}|IPV|E;h=+6o{R>bl>{Xbl*wp(KTA@}|Us%}y32`n40eE+JS^!eDjj+$?RAC5ib?q}y(yk5^3pE}0(kMFMQG)~m(=U_usC*W_X{j8gm?<;$JpL+kZCnNUPshF`n!Z+(BeE-SI2i5DMqjkUCw^yIvo*$HN=E>j(4R<8Q@B@`|?~2H0o{Y-JxAV<BY3Cb1DxY~WDjz>8pLsGWAK&ErJEUo!b*bmTaMho_TH_A7&zIowMkzAi^J<@i?*8-~DX;r~N9Tj?ap)^HTlJ^!OP}`3Wme~juYWVuf8Hvsbe*|>t96Ly)f1|YXWqlKbE5v<;M;)CUw1Q2@5k554<?k=$EWvI?X%tvRV}O98Jag+`^;~lI$c%1KmI-Kb6*fDTuIl-)iEvNe4m?HuPb}DPm4HzZ&eP)@;ytg>vemb7t`GR6L`0<u9I3I%{|V2)t^$I^G>^w>fWyBr3p!iZr}7XzGrPxs{1_hR;r@M?X0yCerUn|-4VW-m+<{5JyYH1wKpS|p6@N+SGc~~FQ>ry{qA-KvzO58Pvg^0<9myB*zewMpg?s!Uk$0YKcf8!J(M3RUL>M^=<O=%x)Aow^}_i79NFtWA47}ub;tHSWechP3HxT9W9OT7j+Gx?=UDmSb&j2H);V^*S?AdKW}Rc_n{|%K@4J0Z#5lZ~q5Hw|o%u8L=YGt+C*nA^IIE6}?fWx*t*<ZH)6_iSPc5(40VRJukQmGVYu46SexPiw9kJ?oGM1&O<6iT3eO;fnP0h!Fk`0sGzIViGJ+GHY()07J`oV~H-e|oqmLG19<%ip2`JshHQ`~-do^P}&B{7B{y50AnJ3rWOL(F{RN9AXmyFXStjc>OzxTRq*W_{z^b@2bKj%iQm<3IKKuUS^z-#xxn^=;o@=<|qtb6(i_#<%m$d12=pKPsQ|A}Sw0DxdQrDj(nEd#~ltexq#Z5#tTtyX1Dnc=JAZaJ&0F@-HlKAg15qSgJbzI<3;j;h*<X+;xoa&FGZk-mZVd5be+UR<G~I=N=c~-{_a>_Pwuk*7pg;pE~UJoxD$OcK5%hePcaeTfTp6mP0b%_sYSI>ir)UeXa6`zoq8`+b>v9<vX`pZgd~7;6>do+jr86s{Fvf3me>Z%=ol@Gd`W&1@wB8dBEG}`s!GI=v1)-Zr{ugp*&~x{AKz6Vk6Y|nZAa5_4l?<zo6RdPmWKG<(qcezG<iJdpAF+_SgH;Lhbk5?N^_Fe1^V$TE3}o`=-9_d(S_m>u+4S&OL5}*YtgX?R#cl-{<ztcn)RVr{-PT_t*SY-*=Q>rPf>i#G?9p!%L?Q#`1%Q79WV2ziy<O&uu?Yv0b{`cP8(f5v#uO?fT(-tG@9~eW!+ht^2$Sj|a;)<H7jmd<>5_%QxdK@LSil?(@_)f0Q1-mha7zln{~6`5TpwZ}R=#)@$77b?BLsdS0}A?_Xz@tK)kjpw{0`wNWGG>rlb&Y8`3&;qhkq;qhkq{?pSAMfhgjV%InGu$^z#Eq1<{hpqhZI(hrYDTy(B=lO<e-u8G4Opnz+wr~0;_{pisv5uGRoBj{`*736a@bOwOXmYIaX8UHm8Q&gnwjZ9~N)P=c*7<1r=6s3D=X|mK@cDvopO3b0*SF6{+c)+7t^0kTd~3e4eKTJf-=42*-^^D|oy=-}H1njt$;{MPz8U|vAHMEbzIQ}9eZBjv?r`Os`Ty!PUElJ<_3eC9-}1dp^?dGpKlVM<Zu@#?`Qh<^A9cO6{P6si@L~t0*7eu+!|klFx`y)2^}TZ+zVC_jovcN4`@L7%)^gSHCU@2Ow!b-_&VP2oAa$J0^Op%tbiU>Li)GdMZ<ie^HENwR=+Y#q_IfGoTk9p~pI6oQ>Gpce_)+Vz;z{cHs=eNe@>%aW^|pMf)LKs(-(FAptGxDwdjHV^5$kQ+H|tg7+v{!HxAX1ww(UpdTkCDxkIJ{!+qNIhpVwuM^3DC`4;}RVn&pS@Uo1a-|6<pf=t*(==Dy6=X=6%aEdQbRBia+JyFO-q*thbXcV_I5*-m`Bo#s9(s=j@{X8HeGhxT}n516Okx9^wn?fYf#l%%gzzPTT-{>On>et4Z==bLqc?f<++&Hw(A*Y)$OlRiDZXJyvk@9jOJ=d<zk_5Dij)%ts_9XZ!T9N*k))pN-xf7^g$cfSAC#rtFBhkZNWwA0QvzLg*De=9%ioBWqo={lq8>E9(}`&Q4x9{*Z*`#qgYCCBo;dCu$S6orzsUu2}d-{>$(eZS+aQ+>UA+<KSf+84|Bv_7Q!)A;m5R6c%GKK&4tZ@!<g@=ZV3`Nj|DH)yNtgmUQTGJ{L0=hRVt>GP^TgWXPP-}?T__RaTK{>HCvRO+nM_qp%3*3XarJh9PT-`BsB>QCGEKVCxD8=iBM+c)2{*}nOnE$mz06WYF=Z-4J+`%(GU_kOl-^1X*jYk%2Hb-x>EnMr@Ie<$x|eco-*{m}Sb)&KsKC)9H%Cvn*(l|R3zejYmV>NfZI3>AKUTP)wd*{A0vd^4`>eB(#uGp?fY@$LNZ_f%HC@x%EwR&945FYgm|^!t|YPtUA=mlEvVT>Wmv*|tQ@OHP}@>Ul?SL%j0+o4!`(W6(LLpW6qMbbgO`eP4cPm;N2Xwg>fdswbPO`NFrhx?WcoFQ(gd`E$Jv%=lb?&*-nZ!`+|3#HHI~`V$MO`8<$oke+w_b=CK#p3<M_`{;7Hk|NF*o;%pSdF~K6^o71Ye6UFWUZiPFbzc^mn6C35_)d@i1;42FhN_lQ{p6i8S3Oq<<~ytMeH)wajOfpmAMS|hw{M{P=UN-(J4I8}c=I-_slSI>JxS;PxJ%!^@Epqa!_T3NZ#_q|eLLTNE@t~t`POqW+c){4>+yQK)eq?BS*Ko5<HJ`!lYY*2ZjJuFYUf4mk1eFPW7Z*icz$d912XN5$mcwY$~V59&v_J;Z+t61ysohF!#?@WjtcsCrrl8e5?r}UuZ!{qbp4Xw>hDeCtLgjteU)~*$Fq4}Z2RHo#Y@wa?``|MzV6P*(DTZvM#&N5oaf`VAAUYQvW51$RMq41!Z7_k(#F}z5$!R*2iUV~kGqcXLxH?|-N(iJ&cyc3?@YqJ^*b5cxAX1az1V(KzV*8o+YkTl<+C@m|L{OPZ<HOU=YzJX+CQzIa|d!gqu0-8TkGGk{kcv*U)<9|&&Q4C?sM;NxZjL#{f^G~_V4AwzV&;#V1pm^>pLs-czgIR*MS-OxPIDL&#Og_>v`z$fWGdvc|bq!d}O8moz>}_dO!GGN-+L)y&ib1xbnU8U)JaIJ0o`{Hi`Jx3txFY8t*M5Qbc5R@;lu+y8h{cH07Vs*#C5)$Fu*df4WfZ*=qmaf4VR{PV9q-FGb82F&wTUq9wXS#8)Dg@wyl~Qp9KxBM8aE(4la$h!Y|<px?tA;7!y{r2aBEjgXv<ZiCa|AJHxFkMIxZCU_Iu`hk6!&o;k;XQFfAnecQGQ$)mz_>7SJ1tED3Ivt+QXC+@0$M;te7erig^lQl@=$kLl&)~%(mWo(FNZyX7!iltd8#)u7$+ou<)9Hihv~LR$Pk(HJH=tACJ|bF+=!&+23ya7mqL7FdA}WjUp%263M2Mm6d`z@qEXaM9<KYTA8onyxtfOm6y#h-e&9+8Urw}3eA=C%^XoKV`w5cW90&WR+LVa*2xQmFkXdBcA?-uc$Y$N&`d=|bCr^orZI6cNsz!wS0*U<~`1wMP7V|$3>D>Vdfhqt1q;H~gx+P0o{eFvXJH^LjqJ&B%zTZ?`kF8i90JR4mP&xUuQ-^07$AJDt-4{)Y9tu^8_%aB|X9Sqlm-$7Ty@4ySuWAH+FANnV}4?d6HgwMmj5|V#L|A3_)g@1<kqO0J&@Ym>j@Yirpv^v}q{xABEqxrw^edtM8hU8Nmi_aZ>d|Jc9(4FuwcpZ8QK1EH*@|>0DOb+xRI0u|7?%sS}nUMT2nhVZFzGQih$aA6_A^BZG@(1WR_yc$%`Y|kZG%R%_EXTYY-)0V!JcE!t4c!b+gQub!;i>RsbUiGub@CcF3Vk1zIs}$^pHf5WY*^}-@M79G51j$epiT1#$pLgKJe4|<<(zt*c~9y!=iXd*jX6^4Iru7kmN>_}d5&w$72*=t8hLGz*O)2jP<RR~=lo>!96A&}2g|ui&NFA}$4}{__le2$-DKV$f}VxXQey}@6jrqz%|qZ{M4U%Mgya-L@;pNFH1q;I4W3U(P9-G&NL=9B{H)mSYa)sgl5?YPz`5aqXlwY4`23$DF0&7^9i!08@MUr&OD)J4D@dJDgyae6Sa>*N?tS!AxD|Pw(Kq1Ea7Pi9L^O}n`}ZvT8rl)=NWSC(v?(i}m7ghs7KMwzInms3PB=StvQsNNzGS(s7(;to!(-8p;IZ%o;v@P-svrJM^kIgG-(6$nH`i;)w?up^;szo47`hrh1}BJk4}Bk94ZjZ$B_yv!zlGPrC(v8)3HXkPexltgL<|ry2u(m&z*4_~6W}B0CHM$@1^pYo0^cAcUq*k2r5=Va!x`vuI0IgZ_JyVPhgZS_Wqq-4M@8I3kHa_N+l1ur&{gnv@EUpUpo7s>@L+flA$cWw96rvrR}zw!6GvTRMe1qvD0~|JgOL0e`ZxR+oR$5(2^Zj8$&N}tJFg|@L~lFy&JoE)(5kL;sw(GPCAc{{5N-~4MEk=X;m&AZxE0zJ?F)B>`=HC=KJXY~x$B&h`XwPbKu9*%ILV9A<?v#7DIqx(Jq)M9htS{QLvV<Ye2S2Kl8|iHy^?=J|Av2qucMdX>#$s#pFqDyFTvl#KM<15J*MPz^qaVQ_oR~3&=qm_?qMaHdt1p%(0=d|Sl)xmdqa6IIFgV&5uF1|oeR(9a}x>4AE5o>?ybQjn{}FGxpr%dc0v2WQU}0Y;7)P(<}Y*KB)KJ8E$-fZmgFjg<YK6t3ybkuaxU~1EJLzfpUSnX)NH8qv!OR&8IrH#9fPmK*9ghy2+5ZS$rlO9N6-ZL2)x2|omfFg9w_29v<3Pe+yZWiz7MyATcJbYR<K#~OCFA{g@?oI(G&1`_<QsY{5^aZmB-*NuO-*uxD0}8z=P2Qcrd&gJp!+WkD*uKWALBo4fs#^CL#F`^fD|p1O5X(imrr@!mH4M@GAH{v?}}_TpgA3Z*^Wv{)c(`JNO^?B)SGZ39obRUANW|l815ZhH*TH;hW<-gyS!DuxmUFX1qup<QhMN7+<f!1JISQ)a9^T`^f8@TyM(jkz8|`>zCv|P`L&**E`9l(KGNFYMe%Yhc9wI{7Ojvk&v8<u5j+Hw<XU<2RirG<dUa3_s$=)ZkId{9pKzs=S!Arf4R1k>%9y#1ZTj@(G)m^&q}T<_Wf-UuM?8T6O!AZFTqmF!R_F@Xl6Js{F9?Yavr>=V5xQCx@=o=6A_P!=!H74)JI^cjp1IfX@6ttG$t<(>cDwm(>90pI&9Ch|55huQQFiF?d96{Ui4Ehwk^4ihz=s&LO+D1wuj$>UnKuYay!8J(fi^2@XwA8$@%cg!eyzK4{Z-O6X6lj8;ygd7Kf!ag?q#8iKf(PN?txR4$cRgw#CujIJRfn?_vKuw5bEy+qLh#>8IXoTk<4PvxkU@Xm|Jv5mQBsM0>)c(09<D@RuUu`CL4o`GWVmlhd7TNS?%Y;?b#acRn)_o$6}aBtC0CKMIY9<7tQF{bJuz<Tylsfq#PkLT|yh(Yxp^So#O>r0#(Kf`3BSy6Q{bPe`5x&!R0-KZjG`U(j{%FYqmN7kmr8iynmU!ne@_@EsBVh`5SggRjD;(KGN)bPsw4mi{C>sf*y#@KrSEsvl(gci`jjaoQsFTlgRN8kz)OgU_IA;4|<Z^b>dwyc3-Sml9D@#N+5=a03yqil~Ra4A&#40a_A%UPMI^Z=zXXsn5VtpM#$k@qmc`5RxB6%fk=C6;Ll+0e%7P4!;2RKx@H0;M#1fHrua_|1|CQ(snP~t4Ne*Kg!d-EW`us(*x9ahIpF&e46^t5w+NNFWc*mz6rlcj%4}xvbcyxL=+V9gd-niI!+-GkBcZF;!zPE5e4uI!cz0Y<;i;*eFXjw^`Ai>gDbJEXVDUHMYdZ3^}zq3UUBphxDxfAKp%sP)3(RZf^bE)^Eg@peuA75Xd%~og=j}1_SM7wR$yN%;62K=9wF}$JjrE5UzZk90(}B*D58;w`sgbzF2n0G<VxNwYAq8n2b~Vjf!m;sVX3dcZQw>|Em&$Dc&3QYM0|}dgujOOi%3Tg5t0v}3t?IBWojmiSRi5}A$bNNxe59v+yt&oNPd-glWi=751<R+1#IsCkxU!Y(S2w#oJ^bc5t8Ne{mtkybR)cxb}u7l(BISH#%L3`F>Lx<YCW_G+=TtCN59pg?`q+_Oh~Sa)`n}-FLepY4LObtIff1KKSLM7okjE$(FyGX=N0jkh+-m2izq3gEK!p8q~?Tkl50MblNwTUz*5V=Qp>^Rc>N?=3YJ<0eiE*Z_JyUs>*CJ5?#zC?OZ#QJtD@E5s&GHF4_t<}mLeqQqfS2dJ0E^YA_x20k8M{)E4#K;nHr_xd_-l}wkorKmHB)XqBHv!6tP>x4iV3b@QQdr#8weoL~KX5!Q1%Ec0zIzx&z)p%_KtdVe}hV)?ZBRE$|{j@_6(Ucsx87{ScPg6dnsVKx@Jc;2MPF|Dw;qvRwyh+hI5j-3zC|d(fru9(V~l7hVDf&`)8hvtYUX7iq(P;pd4LIUZj41#}iXi&~O5iP#`wiir9m-VpH;A-OF&1#Sy}jBbEGhQH!ieC0YulDDB7;B9aa-2?|=bIf<sm%H%~5}WADO|)Y#F@?UILc5ou_2H$k>DRgR!(99qi2C$pefq-m?Mtpcms|sF>)abBk{h5OJNL$tWHa6*k4L|PP2WlOiRdcgZFB@I{bqPl+q<|OucdZ`-{!OJ(2j5i5nV(yCnUd4bm4Pv!#=bF?1P)3&EaNnJM?w<b!tg|KtvW1^8Z&W|LzlUzoWhqa59U?BqF;bf3zmn!uSsC@OjA(lUEeY1{bFOL+Jf*F1D2$%>?IRyG78faAE3YL9@ZRsCOTFKb(cO-H$qO9=4Mi%>>^^P9`+Y^<Et9h+|)~vcE;x*CKe?*;Y34vf)V{C!(8(F=#J%f`|_s`ELxg_J;eTZ=t>6$s#`Db06`U3DkRwye19e?#rL)-~QLh_x}9qV7mWD%JwHCf41oU<aSXj{3FID4Kk}fzEAw8F1m6x>HH4@NNHF'

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
