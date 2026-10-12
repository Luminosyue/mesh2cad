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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/614459e9cdfb4a06abbf2d6ac962a08a/part_011.stl', 'relative_path': '614459e9cdfb4a06abbf2d6ac962a08a/part_011.stl', 'source_sha256': '203ee07557dd7d2fd351bf62e530088b5853beef681614fb044049d8d0a2cd17', 'input_faces': 818, 'input_vertices': 494, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.15827886760234833, -0.09813006967306137, -0.19857922196388245], [0.21680347621440887, 0.028899598866701126, 0.2713891863822937]]}
GEOMETRY_BASE85 = 'c$}r22T&AQ^zIwOn%2yk!>n;t%n6Kb&Wfw97-<7221F4vI_8X+QBg<C7%-w@YQ+FzPHT3|+0}JTyQ{vr=lf=z`PX|@uikU()c51#a{BhUw{PF>nOff#snd9B`1i9mVa~wA=gVoDiXSykZCJpNp+UU@Ldyk*jP%g5iLd@Sb$;s(t$aIqXv4J8C3^>i_8L;MhNWb!K<|=XmXd*kh729jBiMh?klq2xZ`@-*Xn?~H?b{<H!141hReY*=St^(EvV>dyAOB@^bio*1|5#mzT0;lL9acXN4?3uRw)JZ$zFBa$`1X&Q_||4k#n+p@-=utNOk?rw-p%0;FSA+sTEiO$)X!R$f#MsPJ+~|0e312!<oObe_O?3WTN-SVJo>F6;%o6;*DK%F`Gojp%24FlJX(A$p$GaCZ~%GAU0x;qX?#WU>kUox|HV!5?Q28C*NPq!-*W1u9M^i=@36G<ND|*xGye|p^M8`|md%-u%kSIgTPpt9Kcu}eDyR6`gBMGrZZGDEZ!xNfZ~dd5<k6}Iny6zf@hv?<#5Z^Nh_B@zfjk$-L@Hme6odBH#^Ja@<;B<Lj1=G6d$#!YdKb4zeKyV5C;iF3SbY8K$XM|Y7EF-#hiveZOUXEDtqMtdz4=xgx7Mm@QvbhF9TETI9`ygmN84TVIDK<$(p2$#T$BD7C0--{(p2N6{}n?ek9qVn{3jW$Qvcb_#kT|&IU$;^o7BP9yy#J>d#ZBcn<HkTZd1NWdu!Kv;%ntAhe_QU{2=YMmJQI}YlpPgPn?r}YM)!8eM*B+$shbc@)!&K;BOCHE$7>}m$bM194NkCy66@e-!N^Dv@aBc_J54)EB%k#EXTDcY=PhVr-gFd(|^f4G-Bi6hivR6{;8SL-aK*&{q#8%iE$q-^TeL?M0{)h)|iKv&h3=HU;GOF*)({DwBJ-f>Z}L6L!LoLCn0}(@huHMqJ6t+s6)+yyQH2T-_V~qvEkDHg^Mt+#$-7uexZE6GH>68B})4)ImFkK{>D16$Y1(neNq_h$L#VE|G6L9XY~=^IxE#O@dq4`dfIQ-5#KnnY_0S^^Uiqb=NTRCmoE)*oo}`S^~JY@Kg77F^GE*^{c+q`t;9FhU>&g)3`IY0jl*@?|2OzK=ZSBRF1%Nco4Utg(LWc$e`FwkaCn^LJ+e%EGj(ODzmYY&`1X@~(LQU|osxh4MYP|Ofc7WOAphralHWe`DEgTyu({N~?iS43yO-cUswjEv<AZTtvu?w0w$hN}lzxYGs`CTXVNk5})85E?zqD)q2<;~t!{xY_hRgiX^SnTRiWQwDzQro*l`Y*X^ndq1$n#U@jjp~m@DtYCy{|UN@jkvrJwJ_{F4s$^#mMvc4UTJj8z6so?>6eZ>jT>7o-#*{o90JpZ?67?<3>E%BX#~b>7X3H{0~WzN1HTPj=SJT++VU}6yFScBI}7!x`*Vkf60XQgLCea`fph$b+*3BEWT}9D8}Vh&TZ0<rMbm7<_s6#_#7|itCc7&zW&cl884%4l=R1Xv;y+~wG``5rn)h5+{kKZU$50XIj`2wQU9{_#kZH4DEamHNzz{1*G7D6k&e-lKlcKe=lawR$RGE6M>&802DnZGJHc<*vY+VYH(19j`=kFsky1D7*M9ru?{f4)eS8keaV=~9mGiR11*3iD!crge%Qeiy6(Q))iWP(8?<(Ar{6_fDB-eRse{d9aps#Owf%6L5B<E#*nuvb38izV>ueQzAxAyQDE&jtgxL-e=jB#054)we{4(ogTOw{c|CDgzA1e{mseDwdOujJQeCe4ucKQB*my-v+`L$KbRS%>})E4xeDckeY*e%>4lpZ6o{h$z`_*qg?qpB@cR&zP=KC+)*w9M_sf^4OQ$!?<5g#Q9dL(?j}sz7_TfSLnwz9wGTE4U_)Zj0@sh#_UG_FI9?_p9@{bao1ju^R-lYk2=%0`y`B%eEGW|Pv)EGPxJ)okI{IQoR|IITgbm^1jZ|Qv(!ybxsUvL-$;Ed3oFQa;`H^ARp-m`ocn=<hsd+-9_mnVfYia(=QZ-Q|7(c!BU1-i&kbAJWa*#tei2wj=D#^7o%oj8Po$sblGq42eygnF+sEICm!E4#i|SrEk*7wg-tzZ9ufe`0sSx~K%O#Jk>RmZs%U%ooTlEJ^yD$y+%|*q;x0d)v>TD+EUM=V8Q4Q@6<;T3rITPyyedm0zw_k<((VOaMAMj%z>EERrxUTI!=>NwaQXkv(_0oUaxtciNAIjmn2p@s@f2ek{>$q4y-<NT*ZLJIczz*C;+F!#uKDz<>|HNyz<cV)3bu+p&gYS1p+S{k}PQ?6ZmF#w%S}Grs`Ss*C_zn9>|BUqYa9v*Y!+G^tDEYN>F}UB-x0Stz{EN<Gy{^{}c@n<LJh9{oz&?k*Wnbi2(HDoXpRO<f{nWF|akUqk>^C(_u=x7zQnIfzg7e9Iv)&Fvf7(3@#QB%NK6%DCv_Ezcc}msB{cz-X^ykhf%>R1kOw?tv_(s-n85c|C{qlF#>eJDFqPLu{HFkj1(?(x=c)!1#|33$?zs)rp{jc=9w6|x+e#CZZ0mi-lk5Xsby4{#RiHnfmGhm|hzg{k^FFT@;zmh5YWUcGez0$wA(WrBBXUzM~f6BheM&B&FUh1z+>x%V%{0j8v;^F>sd~0*83;r>v&#G&a<TwM~VZ7R`L7whmQg`Fp5?s$4_rMPwEBkHj`d@P2u}1Afp5ebQkh+bpyIa~%+mGX>IvFCrk7<nK1|CNL->$@S#OH-rM;axfeck(R<7IXF+`k!ti)H@Ub0(udC%dBm38k^`Or3&x)g%DxVfleFpH1^3@>uF)zkTaZu2Yv$=bKk$AENad81LrC)*K-Hy_yF5?Uh$CjziD6k1u`8-)-^yQaBv@mWXTcd#A_#t!|YAavlS3p>8!g%X~9hT#a}2EmM2C&3{X`J2>u!H`up3pN~F2Lmm9%FmDf?mw9E-x4g}a>og)6^OnB;vG@jQcNFWU{pky?KTE>p_x}`@{iOZmAE-mhRH>W(>J7$g&s)^9aFXmR?5lBK(I<aIzCt6g4}AVy_Veb@&p2+`wJ~zsK?Qj|e8X{zUcmh&evYhrTK2T3<o7{Eu)n(bQ0{j&EuHwfmpAr51xliSZ_>lx)Kbn%yOf>lbr$4t?xQ*+U_Ga=*UT*Q)7XXkr7b##_}Wk#uK(sfxZlq56yN$TJ;v+ABaGMRT;iMij$%De86oq{(m#**#)e&P=WFepPkc-FH?l9)Zj^KLtpkh7{@fOs7xnTfg#Og86e|Avw78GtDFXk<2F$~B37Cf;ilaYm!!RFy>L~L~`$)fPUbng#k4vIIf0vg1kaOL(UMVHM?Vo~JCxeS)|3hDk8P-(lvl#b3`>`_c{k%}OhMt(W$KhN53Af7c&*U*NU&_NzEP{Pw;$>OiY(1(YPg0od|1GO>BfqZ?>iHqYt!|D1#Q4tf#D1gmEt&t8R}FE#jgzo{3v49M4aTj;IN!2uq@VWpTQKiVH^p(Ih7@x>FKtsx%#&|zW=ns69fk3l?&~&B>^<L#n)IzZHQbj=|Ay;`zGZbi)N#~&jPJ-_;UCI|dPR=G`-{HqabCZC!1a5tFxJa72F`2l5R7|*UB=zMJqX9$c4w;eYk{}yXY^J5k-y9PY2rWrhJ8-tK#cFDb=U`27>)N|)<MW~c(kmmw(f=TUaNH&{Di}j-?W6`{RVxlUHBZylOX`}s`hZ?Pe5HP#b;q1_8N(L9{0e$XYFV_PZt;sKl_i7a^Bk>qt2PaQHPQzu^zS#micU_Z{*A&<6^J=70)$)kA=VIq}0dObfDDDygmVSGwz^2vrCww$&-*j?`-7%_yqUmy;C?|SeLD7BBlSv;u-M&h(n%C!=yhZeIuZ*)Im$L4%gAJ2pqRiW4XWUccv!0`qqi}BjooDvg7<a%!6imHC^g=G7|5*8ZLl;FAV*;@<RG)ue=EUi3&JhudM5&UsdR5iIexDwp^*?{%919LjOlk!FAzdm+QioV=4Oc=q&OtFDCWTa?<Y_FXLic(GJ%|s%VVw4=HGWWHI)Q^o{r^)Ti?o$z!}-j^pzAMPD{U=AF&H67~6Y4eFm9j(XB}z7MhODzQfX{`@NR=UO86w<m_<`S0**<l%ccOM^<A<nQU**Bf)CUsthS7%SEzPtjnk<MZF)IfcISdC>ZL-L|?ezJBDP^xL@NjrVw6<B)IpcI+?fT;JyASM81G=$M+jU47?!PP0O0@og=(qn>X<aDOkcbf2ql{}3$m+>&OH9M`O|6ZyOCa;t+@lm4f7sLT98lE>*g*D-x{m^`=YrFSELfqZyAeUW9Y{5^erM-!Q!_SCoWo+R%cjN`$3a$VU!T)=zy^!spJKIfXL9vzkAe@bw>E}ZXMoW9nt`$DNl+u`Wv(*vkawHwmj`fmLJS6`d%KVSTE1?4_yp>KIsYM$i(6ZO@9KZNrN`-<njfD&?D81&6SBV;~XwVl}4IolTrk$IvAT$SS*CrtF`2QT^D!6<R-n4I74qd4yViP+~P^iGs<j)$-5L-GF5>#*dptUZQ2VP|9?Wyv2Xd2IBx?e*liX4#qec~TPEXM8H3JD8!(k4wJLQ#ik_kL7*4w&}FwvG+WU^IEwX>wpFCv-Mu|i(j54=hwe9`u*!!9OuzI<o{Gd^4sd2$M5+*(3)mcqN{J8y-CL1TJO2|cKWuEVQ%Y>(>MQqjrtcUhjpnw^IYj8<E8DnjCNVC;(TY^m-pm$&p7Fioxa)b5}v>A%)|Bl?RU3&8fAJ*9ke?)(f?j&vF^|Kmgwqh_pYLDr<0_;LErSK7l-ldCHFP$;9Z<ohl<jFJ))4jN4IRg2mf`b)XiGDs`S%b_5jD7Zc2M=hl#ST>Z6{ZpKDTYm3HewG4Aw@Qq!F8f$^R^=$U&Rs&10}T0i*zy$|7hwsd-d`H(HM+x&F;)-IbRkM4B}d78a)ThGlKxUU!`-=Yr7<0Oy%SDus7Px|`4;@AhKFNe<)=-bNIl{)K#n#ubFr>`fbk^7Eie-Ze(-nq>;t-dej^AGRQK1W83@4c#WUN-v9`EQHY@cGdD59nv#_Oj2{J2aDiYL7ngxS!>G&ETVwU#D+*m<sFL-R*K;)sFp({{Lp+IWsYftn2!`R4MZNC4N}Xznz!+jy^t33dZG?)W`HKnS9vAH=j)t-=6&i&dW%T_BVcZn?Kez8O68whob*q{gYgMXaB7y*PW1j&i1RYkJ0ap!M>|p7Ub_RPx6>AD@lKxzShc)`I)Ps<T2^nGR5OQ(JvnFmkMUXarwEbEw+Z_(F)N|XpiTgo9Cr&_J4E2-_i{4OJ`W*{$+ph6Y4Oq?i%U$(-=9f?PhKqH?E;u9n4dC-TH4-YbwXJB;*(0D4hrU+KcVPw{I+n{QR6w&oLkSfmrzZuzzK~>1kISbMv<pk^Q!D+Yj@6NnzCIeKPL9S|hwiqHk7NI81*2HZj@F=l#MShx?x~?Puiq^(sD(K3YiTq21}{Iaoz><X1cwk0^>d>^+8cPcMXV?NeOT{-m&+ub!zt&iA*HsLzpgvc8#L9^idW<5F(pVl8%E_Vs45vdFWmEapRww$dM`ua{{e<Dx|`72i@EzO{xQ*1fGo@ZQX`JlgYfE=!A8sk7DTZ+(dSSEcJm-F)Z$h|e81`u5j_WxQ>7eDOI=>WZjmY-_B~Gdtt``Ja{0e%wXrrxDo&*VjAvM&mLVuSWxMU#4%it0Kp>mpUfvgYAA5xAFaN|3=@s_5_}@y7<YsoAmX2v*q(d=RR4#SPktn<(BJ6|1?k5G0PEex9dfpUI+7*zU|5^>A$`?3hSq{J>Pq1jV|JIw{10eo#OKjd(PZ)eHpe|@Sm1OosXZ!^YWZJ$kTaCgw$b0fs?Mj_GX#4{5{`e=;L(wEw^JnWQjlF>RUVIm3eOa6o`2qTp#(5_r&M;%kyF!>6^uN<9i5CQm_tpYl!wamr8!SXG^Rb-QgRvbewOlXgpUs{h_zydekR2!aks7W8}$t2lYJAN7h42EBMwgcs{g5#9$q!Z|}DQ`?<wE@i_v0t+St8U-n*ia6hQk6#YN_2<x+TmgKk5cYY7V-ZlgF;m-Dj9?JdNaDE>ne@pjqFJDH^*Gk{oVkh>)ldEDqakhWe81tN;pW2-MsJ$EI@136`JN+E}#n(z!$NSQZt<j&632yV*>1%n4;r;mM^0<yZw?ThObj5qHpuuv!`m?rf>x{K_K(d?f8;yAzwI20P>VW(Ydr2N!*+t^p*L89mcWu9Sva4^aeFN*ibKU+QzTqE<{OjTW_q@jOH5YY3e=;msB*!mv68G;Z-7tUn`M&mi&T&`YR(m(r)yg^1KFlBa_ddhAS8O-#v-Gu7elouQz2|J#3whR-bi3~u?R#-ONh|L?^bJ+;zO_Ms`?|#EI6Hl9kr&pb_ju3l^sNbHm&orkMB{ixg3x}kuY6y~vXP&^X77(WERDze{E90v?oPizh)w!e;=&16UyDugmAn(PU>)!nh~qxUx>(wEJ%ak!LoklHE6Vef-aad?m#xE4x2b=*9oOkw>o&kXb4Ev59}N1sS64YNv&JHv*YXjl&#*{*j=;}rO#0f20&?Fnk}Kf-@9a@HuY5UV-Ow9far3Qxn$MK}B=yF7{sCig+=veHKG1gMN|LLuHJI)v{kWP2b?9Pco|4#aFYu7@GMi68d*}DQ7Oar<M6WRk{U6Z=`?0B~j=B0;&M=vuX3gWLTzyO12}|Yoe?C4f$1gR-ZC$b!`3dV@o@r>`KESO%T3-0tvuw+y4rg8-clFJ05%Rq+=YIIV_All|xz=A#KLhPA+?4yft!QT4H|cB5ipe-?J{~D<{=w}%r9a-wFwZ~Egg-Hte12yRX>!WdcYYtk677f2AD_&I&+ifG8M~cu^WR0wdtm2thts#0Z8=4bGu0dK53kPQ^*asg+lYVU{jin(f6wC&c%PuJ=P+;`)qR-g>TBuCVE^VZ4)c?~F|WlkInJ%N7hHX9>Dg$>H?o`f=JC16pR1Cr8@8RXcppOFmUK$qW9Y%fPrLe-zoR6-(Ld^}{C@X*w|%2AIm&eNwQG1TSYjS=^P?MMUCMSF*PYYfR$bONYo7k6-TW0ZmblJCbIn53DR;{uQqTFGDXzXYZEq{-Z)i4rPCs!8et+rIaPgO<LY^VZ-1bq{Il1Jzw$s;3<aC>#de7y^?|B*f%&8ujhxDEAwaiqHkiYFp<R7$L)&ctx?icBs1u98?J@C3)dp)!+>i>4n8R>7mRmi{hoLrB_p$MtJt-@-wU-+lww@n$8;_90(GrG+mr|<l{L(kY(@|aGa^F&+G^1S$k*TP>`MCOU*Lk#8#eY0#D`QDVi2jBlQvaZKG`8S)4qb+-D%%86tP=_lG<okX`=#~^$-}!w5OXO5JU+r})&SP{QxBY<A*N458{LX#5PT$#oGo-uBbK~}A<mY<;%bt1o9);6i_C@+*4|$g2>TBifV`V<{?{V7I*XLavFa4Ssa8A_e-(0+0v~Y7=U#GVsU&Kbt|CjN&FFSpHj%@h0JLBpb1>ebgElY4$85ivg{qeW(KCOO785jM)HXQfE7MVYejp=b$-!!Ml_X?~f)}D6tjS6{WowtncBmFm=dD4uM>)N`%!v$C0-v1<gvoz+zrXA@2q2p09zO4_PcJul9sipSZGp@e#b0X)u;q)~lT;{p0&syn^oxXYdy&PB1+f|Nh%!o(()FCntwb*2Q|Czq^=pR$$d`Aqx{28?ud7R%vsP8NJE%cqwt@^qasAo_D+PC+^^|It+qO0#1=+xrhZ!P_|`yD{tDvghJ9d~<^L-6^&$oV~Fqq>Rw-hbfzfam!muKs`fw0>`n*7bG!HoVW(GySiXa4e*b$e?*@fjwNl3a?D{&#C|Wufhja`M>%qymv+K|KG2|m-EoHI*usDP+X0nxDB;CS?M@(8}exCB=TtTSn3qA(oy8G<lm?*$iI>6Il`N&Q(KUAa$o8w@+cmoFGF!SbrLz8Jcc@sJcc}y+MPU-+?ra4+?wn|El2htm!|$qE=?{-%|%w4ja-nNkD8gBkDSL5Ij9+_naLT+>8L-F(~(P1%aWB=C6^#qqI#1nk!w<Qa!qnKYF~0U@(^k`Ih^$!!caVjp}0SFBzYw3+n=GhDb<JElw6rwnp~M&lv<Enkaa9d%|k9qF6>g@!VJZEsp-ji$=Ml-zdEkt^A5f3i06*z>WFrZD8*2mpW2eF)R&yBLBCLa$x1trm448`Dip^!q7QW=^#l2}BQ`nWEp;RLE%`n51Nl9<GmoQ=r#O^4g4%&Rf;^b&OCC(_L2XIyK@Oz0BL|WPQoE7|l7k%4#SwiR;ZF@B2eFMmL$MdN6xoaXP(vtAq2?#2u<k3g@8hw8p?DNSaRl`X`3vhF!BAY&Wo#4|r20_%kbTI%F%%D@ZX|Ey_zhzy-b{T>zT$}Ej<`-eO}<WkKs`f#Kz>9$Mt($oPCY<Y8b^Lkeo5U--pu~IWGJrhfl%Cu`j-5bb55}e#UWHR&q7@0pW<oM1=LXT0`eN_2=W^84(ed?4)Shl5AtquJT;IUPu@cvNZv!<N(~}!CC5<vkT*KwkRujTW5_XVvzVc{C$$T?C%L^Nj%v^ZY8SE!#k;8fWPe@*id87yN>$gxR)*sB48;qnDddIZvD6jhvE(k)QRFV<N({yMsS)G|UJv;hinF?0Gg%pmGcgpWWhl<YP+WoPL#{w>Lj8^0gxr>)xF>ZOc^Kz(Pih>wCwVaS0C_NZGDGni>M`;f@?Pp0@?P>G>S?ml<K#o+?V9=yB6J7!IC%#-iF$>cM1DoRPJTsB;{km@R-w26^$}Tx;tJH~WTh|3O4T)AfuXn-LvdSbCvsczaB2wIdCe=HMO{jrMqWzZOkF_UOg>CqLq1GSrtTmolP^$rlP{33Qsc?-y#B8;6rZDRC7&aopvI76c>SMXD89i^e2Th}e2TnZUFVKC;D}2M#lJh^8r7s8Ae-bkhT>Ri0$J%gax8fhbw7C%c?oqRc?mg!x|poACpm)Li`t&ti`>lP`?}VQdV;J%@exPdrEX&^aKuc8;vNje?Ho~q+J?G-+=e`dx{W-Cyn%Xzyn!4~Jwc8qAEX{7A0+RlCXjcNw@`PHw~%A0TgkEHwbb?GwdAGLh2*8=xzw@bx#SVlF60qpKWZhiAGsnmKe-|~A2lmEA2|y(6FCbxBQ-5KBRP$x9+e$yiX)0TqCB+_wE$UZ9&#aaUg}TeyyV=}Y~<YJ?9?C0*~yuy>B*VN8K^&yGmz6!Q<2k=Q&Tl^YO)744LJ?Z-GiEo>_N^!tw7E}{)M5q8np?z8o4R8Ex9SV14FStwI^BWV6s1X5Op$n5P2$f4S6bgIdw02Ie8WJ5LxMV@+$Ho?fd;~5kv75M+~9PpxVeY$g8P4$g9bT)Fg5u`6l%h`6l@jL$Rj^RNem+D=k3wB$uRCAS<m!u0m}^twnA{9zbnNRyv&Qyw43_D4xquY@;qE+sFs0o5@NKlMj;5Qj^JN$q%U)$PdXcs8`7^$S<kq$S=vSs3*v;$WN&^$WO`948^Ocr^u_w8>suq8^}@Ab>t}WdTIiBJ^3{C68SXwB17>_>hI*6WV^@r`>UOy_?{!~Q*TkPk#CU`sU|s*yptM7UQJz2jUz87ucXG3m2M)hBrl{cAul9PrACmI_99Ou2T+@l1IUf3M>Md~yJQuL8+srVXZ1iRKE<}%$Vz9DPmxbD6h~5fkR!>x8H(#s+mW63_<GdR<a%T;>d$1QMaf=dZ|(cN$D7)k>`e}4D4s|)$P>xY)S={P@*albX^xmc?N1#_?oaMWHOL*wwWzJht=ZRF48^6Wg~&?tl1q_GQgf3_l1ostlS`0`Q8SZ^k&7@Cm!)PPmn9dbrXv?7=cJ}4=OlYlJ;+LPkd^*I_9Pc)D6T@SMpoLCT!mbRp|~Zr1Gy!+D?@Pr)t{_%5IKN6k~)<<l02QdoIIU8o4SgubP;(rc@lLBc@jB{p*TqUevee#%n_X&(Vn3=kQzh|V*5ab;^EX8<l*F%)Yasb<bBjc@;>tK)SKkn)ce$%WTl_T_sLm2pz8jbg`v0zwItbje=WjLT$iEPptd3#WGi(5S?OG|m0W|NxHi>Bu1#)4JxFdu?npgLR{D_Kkvx?8f;^Nwnfj7EnLLmBiad|JjQW(UG@87O9L7*Qfx3!3fjpbKfjpZ$lNv>yNnS)<PhLbmLOo4ZdXapDe4L^9E<^Dn>P@mzJNXg$8TB6d8Tqlt_j~YThT<n4c>k{S0rful0r?K~7WoeO7&Vc6jJ%J!lkB`_?_(&Q&rm#vx|}?R97$bCR=SWJNuEfZN}fpWM-3n=ZA@0$klc^lgrT@NH7mI|ITJ&%U4yE7vz?*%D)l7!D)|ya@qTI~c|SRd+M66jwo>bnt>k`GFS1f^azAniHJBViUPqlsUPnGmjV2!^U!d+GUm*YO2oDeFM~31*se8zOl1=I~vPoX7eZSu?W+<NLh-K7S)CuHS<WOpVawxeQwIjJ3xe>J%S!pS<(vsvxWSv@qtdna~i;-)S>r;!6>ysNY6t|$3CAT2=b;Nu}jB`XQYF~0+wrNEzOm0OkN6kqtN48Ks$x4fpE#xu`#Z{?Q$V%&wtCH(76gQ`~BsV8_rgkNFCJ&$nkd=-k4<LtAr<23U<EgXB<H=*FlgMMp1F2!;f#mMgAaZxIFSQfdm)wBbjNE`+nW4BkLvdqjdvas)uMEY#sDWgq!^yqKqp2&&qsdDcig!}?k(K^V-buc!ecxwXW+=Yph-Z$t;fTl7Tja;&rwqj}sJF>4$Zx3k$x79}<PCpToSUJz47CVZX<c#|a!!WgLR5oXh+LkbxFXd`R$7Bxk^GN_Q2dTso2)|dU(`lq6^cJ=2*nxr`;KI#L&+J)7V2cOg<PFFk6fMnD|H!JX&CtzY6EH*xdGXaI)Us*?oFLdRyvd1n>>uVh&+ruoqB{koxGNMoV=F2g`qfwdY8PHdX##Xe3X2K`iOjne3JT%e3E>b`k1Wr3HdVly2tnZ&2{Q+@^$hyhT`qi^W^R1E7a#?r4Ptg$Vt>Y<RtPg>M`;z@(SucveNnF733KV#p9`S$Vwy0N+*)XlY^=K$V!`#gUQVqihrUOC;voFP0d73P5wiJ+BLA!tK>h(PpFs3O81kWknd2V$al!s7>dtRt>p9MbJTw1bL6ws5VF#B<g?_948`}ThsjDWknfTIWhnke{hR!aoYv#}ekd(N@ed5esi<n7l!`wqRuAvKEj&_rrv5+uFJiy{Q|p@M_CJjMpMUB8bvoC-%u-(a{^dH~7HQSHc`cRWKlK9pXZ2~W_P+o~9OJS'

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
