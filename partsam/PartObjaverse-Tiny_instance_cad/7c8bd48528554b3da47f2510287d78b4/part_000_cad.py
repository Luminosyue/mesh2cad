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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_000.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_000.stl', 'source_sha256': '809ff7a7a8537b2439ed83e2dc1a66b0a2f79dc6219a94777feedbebfcd2d4ca', 'input_faces': 944, 'input_vertices': 631, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23647412657737732, -0.14302057027816772, -0.2362537980079651], [0.23647409677505493, 0.39529550075531006, 0.15940873324871063]]}
GEOMETRY_BASE85 = 'c$}r32XqzH7w+fMyGU>9rG^qp=uI*ZO6UOs(zy{x2uMrl3XFnCRUjatUwY^$MS2DjszI7ahf5I^MBoon1m(@%`#UfhE^EE@9<IIiw|{5Pxo6ItIWw6#vkYsVHeDV~{uR|S9R0mPLLE&b%ckYghV_ma65X?RY=r@XM!K||%;}%<ajn|74D005hH0M$^y(ekGbW(6JD_f4&4566K;*!fAu$mHdJK%|)th+Zh)-gBTRgT;#Gu|*T)KLdpg?z(GJ)>V?*GSsS*#|Qha3KsXnF6^^Co%s*TJ{yQQNjuWv+J(*yoSC9o#JZ>=?zym}64UiO`rt8~032VXkHG5fe;2!yn9j?-k;DjLBss-^mZ@oNp{Tn8NLho+tIJFE%I957+CKp2PW*wlUYA|0eudR>^m8&y&ol^4)LAcRTZ!eRG8Q)o#qaU*%t&=#Njxx0>?xHKUJ6KdhGezrLQ3=!YBAt|i#>^|$2fj(n|Z*Tc+DHA_r&Ttb^N*WSIEihExaWbS#tDs%JW_@NwUNzJ{tQigK<A7o(e?skm1p2@}ePVSprjq|;OvmWC1wK~6-^ZNFhpXi6{eLkMg`#a(3L5`=za6QJ=0M2)E^Kwbf_dUPD+;sJqet!JRrbIv7=zMMy*B^LP>Up$T#%Dn<=R3JKesQXN_gnJa&ir}34sbkgKkt|K{*bkaez<urb}f(p4Q-g4IXg;!W-HJ6PVUYc$oa;RiAkI{rR?rh$9KyJ=EjBtskjzAQ1V+pkmFc7d2^y4t|ugIruyAAyEE6eHsg9c3ETMiI=LQrM~-hq7pZ4Ved*^*v$%dIcXyq|^&5FxOFid)m3mGk3`_LGjhu<YDBq)P-p|Lg_;Kc5eKL;+CpYR%<ndr$UdCK&(svL4?zWcm6a8>)OLNY54=up+i@x<2X;1F)-2YDQ&NWVsSM{vSwMPTF9&=(7IbKfwRbx3`>0WaGYI_>VaW6b|YoZ_S9Xo9+kLRklWqd!sBIiY;NX~b1Gr4!FeB&+oh9lpdWgfRrkDDv~aHQnJy;NQ@o?~OxKdHynh!(OxlXLB2za;JOL_b_FQFA!Y51T@zo+2wHzgoLdiGH}g{i{*jpH~a>@0n#D@8si}rSif=KitSvX(892zknR?ytBC;-`KwwB>Lgnn1>7aeEhPW#N~Wa-?!0nK03H}b{{@o+LF4$Gc}TaD7upK-{9^QobM|hChgm}G1c*Pa?kuJTkZM!Tk>^h{;+1!FH`f#{F!5u<U6=AZ6oKKMQ(57@~e$yT+PWW<K|fkbI*<3QqQ$^JNWnF_c7Q0cUgXS+T*?cxDKv)Rx{UkZ;<-)b=l#M8{p=b{kgs7{(IaG&*^{pJk+PxWv<WGW&X^6+b=i3wfo^)m<Jw_cHEBtp37fWV(#nQUFON`$$q&8uIF0B^OL!!o6LuWx^DKzjWOMLzEa$HOTOXA_k1*rxv$(&Zm0Xf=Nvn^)_$DKhy7EyUFP4P@cx>$KjZ6)_GcV(ZTlAC34P@HR4SIar`FFhzeUzu>yPWbYsh@nZJ^Zu@P^FiX==!P=-|E?b>;dyvOjZoPF>oG`N2qulKd-uWuCmaYh<DyZgjmrlK1OfUD|VUrL+_CiQ?MS2FyJ>MsWMz;M<3<wbx^eZYAxU8aqGH57(v)o}VgzzmLyXb^UVkSNAh%eBbf*;eVawI5ucMd2imU%zcry&oR$7XCL=Z$9U$REh{+RT)dz2%?Z<(>qqNzzDK{w`DW4>sXy0KslUN+&etclV(t!~%=u=qmYnbFA0+t~8#DJ_D$n`8JEbJQ(q^v57xEu-&+>PqJ>K5Zp6nq>c5Y<Sr2U`#AniPzmbtlhn$#b^kbl>G?kV5bm`#o_*Q<C;&R=#|?svkQN;_u`=6bZDiNaT;Nd1F<;Cv%&6LX{2*HTaY+fx73rOZ8r6S<x47nP-*Wxkerre=`#<h;-IyE~0zu6_TL@UZM$j~3mQxqI#u>E{SJUPgy7=H3U=PIvhY(r;l6WWTmcJ-*u>uE!ISQR?q<MB3BFBkh^@_eRd2@T256-6Y3x%pK-N+idc?&)t$Aoyc4dN_(E;4W+psyjdnPcXw|n$36W|Np`M9G?RMrT$A=U_*j1Ti(k($9~GWt=k8|dxPHCZ7hJzqx;=Am(`4zNqR(agY-l0v`OlR3^WXj}cpR7gK-#}(pUlr?a?AZ?&D>IdzO-_`Gd$}`e_R7Mj%gd^yv^_n|89q`rJdm3T+&W&tqa^v{qLI_n4itU{a_q=%K5(PKQq^lb&&hdTrO^po+Ux@%j}i<k7rH}wsEt;4%y$j!E&BnTqJzwNv>b-@+H^rJ~#)zTbk=Jn<u5>9<NK<8C*%u>zm`Go@~?QcxBv^l!~XxCBJJlVQzjlNcb|`AHFy&e~(_OE%o1SA>+rLNyf?AAlcu!a)0RiY?sXI1xhkEinNgZE%-p{SA4>AIq!yz<8~Tno~`G4%3S7r-^s$scJ7<9R>uE^kut6(KV`1fmHQSmWP#jg)I7=Ds8&dhOObcD9^aVVQcoV-FMYH`^5?CPdTtKl-}PM2BgX~YSaV<If$&puo}T@bx#xoX{cFr<D1Q&P9w7PiA4&UvEY9`3;vtK<9^=UpIe*O%si&v>ovSsj%=P$^D@s3159H%$TzQ$u{WqqV@T)%Q|96VWe0x5fw7-d5U$j~)WZpdSa2=16TIXc`%(qm|)9JUF8+XgeIPrGo@$C7-w@%LMZ)M(ib}lIu4=*6cE2gK6p9hDT>od>D{qO3ta-H~LjpX;1aqihtTly2+Tr2aB_FWGd=XI7b*LGax`N6w<Lz11lAD5ASc)3N+yMx0dKXQW9)90$p|0jD&{eA!VMaD-h>HobSG51_d%Um<AC)v6CKuNCO-4^rkU+JX&5oP53>X#$g&h@_U$$WVHV;Q$+*YI`T+oFx^Z=IlIJ2wM!%KWx)>pt1PHq1RIKb3ZV9hz+C=D8QLUsuw}_2|z6avv0TNseRqR%!qFY?2=`SH}6QyE0#GODFgBQP*W2p4~>ym!BW3VLq*cTxSd8{8GGi7nuiIR+M>c<yq$LWiy1Iyd~pptZ*Yz&QoumFs{ebpa*mFPD43fl~Q=zdOokt+}k8X`uX?zGS4Sv6JF>rA9rn$nPlhYc%Aco)fdY3_vKZ7{-n3N%lYOH50g^y-)qb7W_u#n_pnXOJ-hO7JKaY<NVaohNszRsL~A)Ne~%VEsvhU-Wg8@?;*X2Tai6qY@@KVV?p@kXj^pi)$#$-<&o22rp2)a5RYLMREtGzn(lgo4wZ$^e=yjXQ@hbFz)RXV39IrvrKc3$UN<GKrxO>z7BmHnEhvc6PmwEpC(#ffKc!Z3rTh(OzypuudnUzb<_p8mM{bdHP;{E-y1-IYyY~$l-tczl<Pn{t1`{cGu6a8@Cq&7?K`DV+UGQSl%9hc~by9=C*<NdqXi@CO~nVc`(YRGXc>=E8quGhxUd~$tqaC1oB4cvZkUv%nxCs+Bt%^jJ0zE9+F<y)AXWar+QO{6__;<!ET2Q8%i5pqA{o%|%p&VAq3mvOk_u8iBLrqZ9$Iplf~-F!%*KfW?z2-ovVedg}WSyDfLUMJkFpIzpeA##23)vYQ0aJYtCckVSx#XZML%W-_VK<-!PRFwLU_m**9rCYL{>&0@*{tkH{_mhVMq@Jzu^1Gi$$+*4kmiC9?{`1FgWj-%gMDlCpl=<pTD;ZZ6_wjv}x5WNb&*2r<b-Aze9_}E=%gLvA+F-B83~wmUjdzV(n&^-3{9>s+U;BHpJTK7a4NUaIeTfGL+Veeu3*_(a+?i%2`r+QC*=O;7pQyq2p;{FFz9>9f=Iy{L%*}wgGJnS2l=J$-a?Fiy@5%klnufxQm5_Scc!c*0lJh$6>E*mXqjF3C*DWOT*z)DfJ!OMs9;-7)&X-&>nfuPlIP^}dBjfh&=giG0nTO58d-=R}Pad_5_p__?n|JShZihSH0O12J%5|_?6B#Fp2k(*lnN@LeU05B)TpJ?ufPN#M`^&eph2-B{CD-4-WS&u6>nHa!?w>;C@1xp{gn!gY`ZK<iTo(@Jka~8Hl=-}4u*`3Hv-9!S>ILwAX-^ZRA7=czg!!&pGT$bYPquS!(RDIzmrMJNv{xkm&JI4W^@!*sJ2#5UeTd$ymGtM=-!s=23D-{iD*YM1TI%^~m+Wu)3dwfvJ$6{`qg?Iez9o5;@FwTvxyp}M<vB@%$@07ISb5G<`X_lVf2kgG-<CKz-y_{pKe&1LveX}yL(a!u>7@RD<$0s`OtL)h+xw4Kj<Y;x*1{(7^C+Y6b>`a6IL<SE+{fO1<O*{=(*n7#SSS7FJA7X9??ub=nRz2oPYQG6>;7`Qif52{<ItCqA1d#&%o&UM{gYW^1aq_Ar*fT2*dy)VI9%%4BJZcnRo}?_Fb6llwHG~@d#8lT{MPQ8+^=@)BK5lyWZZt!SH|1Kv5TeubI5pjSzZ24Ss2UQ=&@7Af3|0-xH)30^z+CHQcqNb<fo*O{r%@NxsScyNb>I-lk4)hA#%M4zqE+k8~d5m^AYBa+dnbaJ6)6eoOc@}*}3V~<odE>pp3)YbC|o=%kv`ddk^G3{JWl#e^H);x$n8<InmS*=AQrllYTCePwxLW*OK4uK3B%o=?h7A?k#4@`Iz*(To<0Z`FXad<6kn)eMgh*+(`F@jFX?c$#K*_VD4)$LgumH%}I8yl{_T<@S9wxjG{;Q`L~&pQRdHovdQ_F=L_cg?qs>|z1CcgOTYqo|JL@DwCD25RNP3BzZcvA_`B)TvGV>cb0g`85%Dq)ENm})8|L#yazE+rGhrULf7f97-8Eh0xVV}!*MlZW`}Nb({*)l*=G`4~pO&YH<iET!m-BBWNq%Ig)bC3a{v<@&d7+c^+o7fLT+ibk@*KcbHp$L?-T#sH^jIY4<GT9Hb+<gPGsowVdVHms8}Z|1e-BlW``Flq{2tibe5@R=B3Gq7XYqd6^*<T61G`H7kN*9ZkJo`ZQqSTevcEM~FgNEcmi_&9mCSGFT+EHb^W-`C=vMN)<<#lf-2VP@AE=-FTduFWH#65S)Rg;&shj0_Ah`M9H|dA!dF43vY%IL5Jm2sR>m}#onOl6_Hky=^{km92?!$9VWbO+s!TFwt1Le3k9nSZszOKPMf4MJy6P4(P>z#K;aXsLsBj3qi<p=a(?#<tjxp{JL+eAOyvvE;dd%pTz^}N@~)$?AXl>hpjT-C3*>8RhyU)6swed>NV^<gJFH{Zg&ed|d*kGgf@_J97{O#Yp*t)$=7^K(PE$H_;gWA5FS&M)^Qr<L|U53iKyha1&bR}8js{ZtyMCrjDzL_b{n?~8DIzWMy6{2kFHvTve4er9H0d%h?CfAaSQ-X}V_d+u|7|7)(kIgQI3%6bxW&mCD8GU_OE?K@c?q9tBrZoY+U#*`^s&v9ALpkK}^>m>fIJVnk^S+`(TdB*D!%%rUoxja$cNBiCnk@wlZwikY@8Qzn&VQv=f@fGt0c)wY$qP!pddB>OhyZzr4UaOj1|J&Uf&*hV4y^S&bLs?Jr;YH^9lTz|L_N(&DwYP9{Uz>5fz1C0K`BRu&zlK%)ocpuXHMu{zTVCGN#Gf>HoQ!BL{SeWC`@x)+%-lUd)`xh<g)ld=5BQAzWc>a0qO|<|cH@b>*G-Xi2)^0lWc@+<8^Tv$9m1F)!sq5^Zhk1oS4-J9gMTMm0KZ4lddYcV><y5=f1P{}c;;kz{~Y6$`@N2<<nNh{A;ay*-E8qYA9wFtxHkH|;r4N*^?NG$V+Zixo!%1ie%!lsrX0th{>**j<^8ykI9=Xrm2EYMeNj!$i%XYyzx3~#46wIfo7Of?+L4+YQ-zyL2S#%}ZG+{#aMQkWyfOwc*YpG#H)%eU<9ob&AN#n~f6U0o%lm%sDEl~fUoIr;eqx*S<h&S}XN*qw<@}6E%{6fM+72EbKaX*~cYVnFr3DmWZWNJu(#Y_Uw7-;trx)(Imyx+|8U9YcT1)<Z-qN!N^LzWSK4*^{$AF-4`}w8MijZ|7IhTjA|6S%QE#^OI&yM_I_VZLb(N@OWj<n7A_c2duhi=Gxy4}GK3fI0r8p^+aUgl3D!X^Afz51zs_usU_x0I<GY};S$$e=jC{4n_R$-%+4{xl-rk$SF`Y0UYUAI$RY<@xmW{h`73<1!<+)N>;>H>L|Ws)cuCuI8Uj?c{m$ljA*twb$p1UgfkrFW7k96Ko%cNpVt-gKOY=?<ya2`!SzrX<Eqp^yk%k5m)2ixK&d2tD4b=_Y3oeStmlCgIq}~*8$8|`nVzT-Z!pGOse+e^v3z+?+7>V+>GV@!hB*p)@3}8sX3YJ$KN|z+v6$zxY<Uywy867^>>yr>Z<(RwEE}_;_AN3ymvyLA6eHa;?C==;?C==ldJ2j;?C==ldJ2j;?C>r8ywf!SHJ7H&N{ie&ic+|XRhu)wH$$RyvF_}+;P958N!|SA=-iT@|@CfpQE_*KF0um<G$!^`Eiw)tH1Y+pn|fF(2SIPJRi^omlJN?r!n_)zh~$6`#pR6?e}|j{%ZX|fdBfP+<w1m-(UOvs-3^8-?~q>|E~T1IaNQa`{!oEQ`Pe--@#SBG3X3GpHt5zysiVXuC8IW*?eB(xrg5UjBHmlV?5V`zn49Ie~|SeS}x|Vo`>v;kn3dOhRoI9-M*6(Ip4dzC3E$>#Zx*`%JZ~X!u8<!nD26VUhnFiXfRjL-^`Rr^8B>?@Z~%X@qSSMan})l+zsyAlOP=LC4IGzGdC;lTgmNlJa<*x`P}slj_0n5JD<D0!SUQxap!YaCs)s16?Z;&b#nFG)jU&w75AI-IeBDL=FaEsZ*V+sHw$@~zwv&-!PWZ$y|8fS`voU|mA@{Ex%0h=ldJb8iaXz%IJtUnqJJ_%>cM&gt@a#Q|8QZq>@U_un3vZaknz%5)?ed&y;;32x7V|M5_9$5-<LLmx$k-=Uf-?Wn`<E_Wc|_XM$Fawci+)ta(=X*C+orSURWQNPS)jazasf~Pp$v>vs@p~XI(Gnqx75Sv*ii?xEox5*p#_iKjw*aAM(d_#bY}#f3<GphiqJrabz=dwLZ<;zPjX(zwsUCW1XJ%>3+HIx{>pH&c}K`LqEsd`>xL1xgJb$=X$U=IM#zH?pzP%<Z3<GEAChi=HzO=b*Ds0`yK1toLsGQ^Nr}w+__%P(`}&SJJ#JfxmtJUD;X>O<5<_{<Z4}?abPTSwZ73zH;C6eI=KO^w^+qot)J9OgfgdfiJb3ey`r6~^@_fC7qNG)pLBAy9@3plxO4raldF7fj<$t8)}6ZdN6Gl=Uy`|6*Xn*4BlAS#Ud+|HQ%_ipUH-VPc(;kn)jC+SN)<W&!<y}6?pSB*<Z7L*r+651=el1fSL=Aa;LdfwPW~$2TXz@tgJT`?8(ghJ9$!zmW1X{;t98!ad<AxMJ00t&om{P>_FOH@+__HM$<;b-@5azQT#sWNxRa}O;GPjJm^;^*JGokC?kyQF^*Gk6`!dgC?p)vQsd}5=J2}_YJGojX?*(_Rt9Nph?@1@?kDTlLom{Q+H>ziq=d6zJ2;SiMjzAk)K-Q@_zEf~=^__xod6~Q?aeN2i<mx*JU6bd>&hIRoTzzMu=WQ*|=^fv3IJx?c!-$ag0M743oLqe;V!kEc$yL5qv%CDR<GU3nSKqDB_b*(JpYLMqTzwZ~Y#AZ%RUF^f=tm|>zT<lwV?&z*ydRG5dYoK+*JIA@#oYPbkdv$LhP1$=2l;m$-z7P@{W~V|{=Q?fbCs{XxWe4|U6qro@2a#3Pvv(V-)%X$`ff`fob?d*r{lXYCs*HvneS&f%<Xi1cjn~kyE7w8LFUfy*Yp>ux%%GC2yM#T`F$LHPsiIizNgdHj6TBkIKInsa{G6D?EQSlXXh%Pz8~cM^7CC`Dvs|8wMpAjxE{xMi%xF;&XMc!^PQuet9*UYLFUfyE}dL`cd2Li;~078cb#u=^<C#%^55Vpzwk5W&hJbWcYbGTY_9qfx6ApxD!B7IR^xC(=Bd7i4NLWvZ>6$B4w!*f6_#bz@@SC}woiNs(m&<>f8rZm_5bP<-&$3x{{MdBd&O$Q5zDT^ezfeGW&a>1eb}<C$h(602#oj-&_7`Nt;pF9y%1#!5ifylMb1>j-#{<4<xu%Dlr4e&5_uD$CnKJWZB^M+Y&RZdlsg8o(&RsfeTnTpMcL=j<j28N`B%1>^ho4W?g+$6lOGHF6x$6&4wVl>tTg#iuo2jf%7<ecvd{2)!=V)$53c&!3qKk9GL8!!!xYPWmK}p8zZdmTy`wE#W7*f1&9yAMOVe^%mKVN|P3J~T{(b0@mesJVJXlF+Vzr=&m9;VQ!7$Qw;LAb>T2{%jdX{~NSZVT&V5CE!$%k52*|Lh3<+m)8We=@=`U^(-G&K2>mi>wNBpBtKfhKR-%67v}gYSl)15f$;p~)|@l`TT~S(NREPDUBUE8vr%laX`Y7O#Up2z?Ood1&$%;U8P}6#6V;RrVB&+Vlwe5pvF;A1J1|Z>MEHS+)wA*ha*p=Yvx`9sNT4-NEYraLd}lw}x(MSyRN}h)K7D4u@`rn0yoHme5V%Yg<;|G99`J@^$DYC~pc@)3OSdHH6lob!=A~x&k!$a_}EmRv5Y_VpUccM(ka1iu1t}%VCRiz=)@VWw7j-CM*M3anzL$763**2s#KkO4mkQADUPz>|Z<RhKMs-mdmpAmTj_rdzWPi@SC9%pclZehh6|Z6MiN1Oz0`_i=n4LPlCl;HUTUijPxGF@zC3#XCQwD;%%@KmK}%QgZO*I$C1Ac>^RD=!~X_-9XhK^EQ@6YUBa?}-L-UPlo7v+GBV-?pbKDIVtEi3fUW{fzB=*>KvxHEY}qN)uYTtqe*0%=VwCeU^gifQ=!1PWeG2<}0-EYfLjFGJeK=P8u+3syO!^n(Q|<x8N+;p?uZO1X&LM}&55aGSK4*&$V7sFz+Xa2W79T?H1#C<46U3LG|3-WP`W(tGpuV5c9_qVk7!x!ezJMlXAf9F$XB5}P`A+9d1IwCQ)&fSly=6nJyco+|F7XsM1|#3XR+iQ!MtTq|201N|U){2{h-)LKg^g7QCtt#{ve1<gH-@(7l?88rvdYkb(BunY`^wN{`7Fz1Sq{XRkW<LU0+IJV%5uOcH=AX-5NAV94zRMwCsqtzam6YiE{1(63sw(t1@ud8urS1=dqETX7;zZ<Ae6m?CiX94rF&t!0WRUh2Dv0wn*1HuzsUdCC1u1qBmZOgLC~Kdrg9Hr(tV+c^+HU#4>YkT#H6F4iS<TIx*s&L9*BFxQ`{fE6Lf#*f$$N~<X>p7^=(b!2+MkE65ob?0pFbREo%ea6S}8uyMf5Bh8!xdg;;6wtzm7j?T08MR^GBQU}eCSE{-@mG_m*K%R^^J{4R7+%Q8YM_MVLw2g{0>a?(O)g)WG=AoA6A1+j1BgP`*wP757mD=%kRBlsYcSA%X23qlTAeai-;UmHO;haPCFt3FJ(EY`9BXvJf(Z8?+?3xv)GABb&KoEyFzbUJtqId+y8JU8-HoEQC|!Kb$@4dV3JUIR;y9P0B7C?ihuOD3>P;7aF1Ozj?k{fvdyT%yURamoHutTg%m;QQfRA*~@+WyA-f|A@Un-;?f-^GR{?6w~iN$8VF7j)sm#{gg8VdC#F;$aUfTk48+I_OSu>tpV}};J7tFAJCYlu}$X!jZYd|wXnSlb4_1dt3ClsYnz{FJ{$l>S}}?T;Wz2G=$cc*vMQDpwyY^Mu_n-pQCtz4e12?G1v)=?9`O7a3;DrZwisQ=JOiwNWm&)q*jN$pEYLYEt7KVK#03x+ft5l|5#*FYc|*iip+lj`*F;`b=uqVJhwf`xGx$(&mDdcKd|miHmbJ3Qt!&#<Sp{rE<!=0T1^AlKIT5?D%}vWZsH+e3P3T+jeW7nbKR^z}U0vdd^>n?CNs|$eg#RBj8R_2e_o2y1cY*&EnvC>E@He2zNOyz(9h!WUWj&A^rM+fN!Fxcrgs%bJ61onoq$cM}4QRzEE(}dRGx8{Y2UZe1GjeF0et<kGk4BqrKsP}g1>F>V5RIHqpoxVbCmK8iIvAQ*KluC5!M6AlTRp@}!$?<xZ>YT<<H4w-BJ%P;huC8B1>h?|_s91Ap!;DQ{15s*_9F!KJwP6ncXY`(qcPRpvOmDc--Px+6YGm@sg5yLSyjuvf~VLGO@6iZx-1MvdW$Aj6***-ztr;Kh}$7&wT&$WCqK)wPS8bN5>p*TU8(arfsaI4QRv~&<cnbYqR?bREGuQ%22J8p$SGoD!;#k;?b!gM+%lGZhqw%KNPmYmQ9iLqc*Pa#f;bZU(g~~s;x6cyc3>S5lkN&ltUKb4@LN!p4ab349Ac%rV!LTB;l#$fBvzXIx3D<mPjE>Yv2Tz+0e(F6w}`1c9x>?!(8OjVChdhLwiq$#CD6oHAtt>Xn%FYLtKcbK55E?AJ@ohR-$9e7n;)hBMV#BRJZU5*Bdviwv*PELeE?1D1C*)lo}->8F3F+tB8ZhH|32&kY+D#*#L`%n7A!5e(to=ozUmT9%!RTv&{x5)xJ19SY%8>4l&ARLU|SGV&SdB<(1#HpM!wpP;wSLGK*u4T4E>9(e7<ED;D15+6X<8KUywt#!m{(|_Y2U^pr707S^=AC**eR<fL44Rww;eMV#A?_zz@eZDjo|zA9^tSDCF2#9Qat|t2hq*FbaN>WuGFRgzZOxO+pU!c`V9^)BI8jtQ5G?Ll9HDXJ9|qL9d1;Z({$~*);h}@O1vHhhB|Xm90l#p9j-0&M%?tdmF!mn0|jA>RJuG1bPYTr<^e;n+N?BG<h#_=Rwmxj>L8&kv{{+Z6wNROuKL{(D<aWMdynbbuNI>wdz~2FxTt(iRQy;VA*Vp;w`u)(r?i<=dopHEIVY`Q)pu6pcSKdAvF1!*yarMOmG97;)(FYKC{K2!HCDehFVq{Y^aUB2VNSQu0g{rUji}Z41*?{hwIdP$eD-y5r|7b7lS6hT$8*K(8Z858s*h2TdRpL2CnjmlP2FDeurfr+2W71*V|KBXKd3R*Uouh^T0b}ALgN)wt2_ewj1iAxEmPhHt<w`8yM-&U6Mob9C%{0Z1F4@@kQ`+p%+1~gx>(Y5_&28Ht40$Yv3<JuYukK{{ou)KbGZ6Bm5s5dkRiQ`aSr^&}5_w<GS+5CFcvVN3PfGF~;K~_|3?p_%iGf_-5qLIQ<WKRDKq1x(Iy^@juW{vA<`Lvk{tD0&>oRCqPeuCN>>@1N0PIywO$<@o_NH!{A4_UXSr9sAD1W4Cn+~OnxZ*FzC_PemeAY9P_!*8?YY<sPA*+QTf*{8D})6zO-z%CTupwC}}lbXJed>MjhR)K5lAR7t2~gD^?#o2ytcjAe5=NB{ca;@S)J5h$CPvQGaHXXN0bdm@E)nZBOxUF3HOXBbFYV;v4Ykp~*;Jv;1zvd!c_rd<~5Bam!94zJ_=&*lwFXhWMamI}sm)-VOgNeq%fIPUxMs?S4bP4>?r+17fAg?}u&2wg*r~YzH*4pAeJY1x@T{#H9B?6FY&JbRsmddx%M2hgR%5@(QI9O*|hoG151YM|KnW8NgLJ#lNHcceH5_;$2{wtejiO&4hfiTi7?1w*$FZkWWV12kk>2?Lhnk%4rOzv#dOH7W__m=qxCw?b9KrGFWAdSylEcj$u0R`p7R2P5wi8`i%fvtTg#r@RXAQntV}PnbPEIz-K_;7lkirD=P^jPRFPTwx{yu(8Ss!CjAjKvEGPDM?n+ohnRGKXkvpA_k-_(vhL8tV&MlvcSk%7@lfap#1Y6*WwF?H5b}uiwJZiK2Ap(f%X)x)f>`Mo+jc#$O%MFuFy!iB<U^r*Ku3VrwX77pj_pFB17SLHRGu50;`H#u^4emh$<v%f{x8f=e<3c2ayN8A=n}A+mQ@F<X=7oQHA7p%z}$#y!kS^*X2^+z?qFGC_-5cLud%Hx96k~{9J&|m6ZC&1bT8;I#9?SpXXwu0e_?*6exNbcCXI}-C}<j^#Oot&1N|X1`R2%L1Kk{)&IdY|={%-6x`O4aSe6w=Iy-zt=<LwhEPDsO9DGISa?rsr(jo9wphKWrz*m570o}l|dhli8D?pcp&H<klItTRsTw<he!)J#kBmD<_HfS=^cU-UcjWikQhn9cf68|n@;_t#pmw_(_T?V=id@yt!=+-dOo!~>DJ3)7YZvov6+5_JJ+5_Fy)^}ZDq&r&H3cfacJ?PrdrQyp$mxj&>p94B4^nI6j>g)S3(kEf0kHFuCJ_4N#{|9t3^gj4I(EFg1;2%OKK_7L!J~l^Tq)%Cv0)H3&0rXwy0%^q4@hbo$T^zm)baCiv@O7Z8K{tYL4c!R39gK8O_)gG0p`+ouK}SOmg!e!XgdPIl6?zEt0Qip31EBlZj(r~(>5naI3*QjF6?8-Bs_?a;t3nrpFAZG`IzN0)=={)sy2R7?_!CC@NBEP_Va;7>@}zy+|KjNNKl-~uOZ7iIa&DP=*|dGjTUK4K7Ey;aPfzdWv^3U#^fL7ty?N6954>=)N&'

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
