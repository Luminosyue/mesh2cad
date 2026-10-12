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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_007.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_007.stl', 'source_sha256': '5e131221aac01af6116df34d8c36f7cfc174b8b2d3f72f7aff91df50501a74b6', 'input_faces': 618, 'input_vertices': 517, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30318817496299744, -0.4675174355506897, -0.3563027083873749], [-0.21523956954479218, -0.1414618194103241, -0.033238887786865234]]}
GEOMETRY_BASE85 = 'c$}r22UHc;x5fv>8Vh2H1Y@pUWA9iQyJA<2Sh*6rG1zO=u}3thu~3Y9RX|ZuEP&D+njpPfP;*V}(O6?Ik8}11@9zJ~TkEa&SnI6s$LDdMGc)^?DLQOmN$Y9~{nSy~24sEtrj??IQbDPvESfTJ!Hn;x%y04IoTXNZjr7G&k?t5WYVfczR>~q}d85fw=6^r0QD;M=u2UTvH8V7t>OOD5yh%U0y3d<DMfiOu{V;z@p+A56q&ZUxe{bBrb;o9gwoRHDRv7+|KjjO%V053BbD>bpm%?udH4J~4e8Ixktd2`xbsn8)>8k-VrLPC2#aa4_|9J8b%uKiRO>YKBU#pSN;u~Lgk-oBZ7K^W(|9D;Yr$?E1OJ5IrB7H?`$>N)Prc2-4{eC9%%f?Wg3P0&A{?=*I*R9U6`pT%WRR7I2R$q&}Um*4Rk#N=@n;Yc!nVrqzG~6P6b-;-TcHWk0(l<P8%Ig=zT$37+o5R|T3X{GXHY$Y037ac@qt`lCU-6wr^_%Pnwe$_m-LA?%-|rdB&i|CL(l<YSlFRD*)RDek-TE~1%iBrcICclCZ=RTUS!&%|d942pGNi9opLCSvLmhwV8{C(%`s)3C($|)43u5)18|KUYKdtD`&i|ac(l@Mk&u4yIS^2xRbNLbG|86aP-Kzwvul0A6$72pmW4<BWm`izE@(}B1Qy1y$SH`pY%H+}Hn>Gco`1cOV>#bcL!sCxQAbn-G9jmV-dsF>e(fqi&c#)sI<sj>i-%FXt+T=Uzcs2d0^c5c)7RPk$GSz>#f}hV<IW!(NtYG!c9Yf@JQ`*mF*UOM_MEd%l&Dix)27M=e^ZguteXkCnIK5v7GXJHXBK?FmEZ?-rr^qk8pXHmH>L`8lOr7Pka-xOwO~1Wo^|jo3mt=pJEo0+F_o*y><?Kv0UNrmlNixpfWIi58xJ%#I;9EW(55Bl4|9pBH8}GW)b?K{1+p+PkF6=CQy=DrVPt>h-sD8zTtiCp}dxG?nPO<q)U($g5_33<mTR%_En_8(qczqie>8n2OyuMFW>6^<|X7jDm;H{kB^?n`Me5)M!N&1GLbJ={Z`WvOM&YRBWb1k})^tFX~Y`xGUz9xUhJQiOowI^2o-tHb>j~1+uzShxM#y7toN&PX^m+Of6dPcIPukWit>rT>KR$ps$mFEBD_VJd!@o|du)tp-CEdIzov@Xm$l4<E1%ns5we)&#k?UtS`=Xqs#iAYOdt?MRz<NX@h%<nat=Iwejb6A`PgK1rO_aT(EoB0LJ=ZjXHW^u||OJ6OqFqifJ*IhK<wspy4=fPzw&9{c%PB1^<ldPxT^$BGC+4P>qbJ|T7$5?5UY_IUb<g@<tbEf&T*@?r<w+^7=U)hA!*BAQHd|0nLt8aSuk>;^;C6BWDH{Q`aR^}1wk2*S6UO$6AkRR{uM4GQQIk4l^Uq6)dhM~c6em<uc&^&W@6+54Lq>G$4%%zO%dZ}xAOJ84?%dVF?qLs`)WlkNI5Bj^B(l-RxX8EA>UoFSA$>AW&H`Q&r^fkZ7Jl~p+qj4Qlhvl<&UX{P=73%SPPDzmC&NL*QjTbE`kjDG5AF02ideC~~Uti|A7I`q4`E6=S-!yhFt8b3DCG*^*?~k|il>vFu*FC+{m>)cz{B>P2Eq!CkaPq&;j$!dfl$O5v=^Wml_8;VUF*M9z{ZZefV0^VtVC`bxrG{Ix{+M6*N?%_;B$~y~-$whcgX^-GpXEa1bild{OW$yIi1f|7;$m5U-k+4?)YNFM&g%OINZ+v7%+7=I?g07M&StZI9`dGrnpMVmOJBd2e?|Uz;se%C#gHL=t;#=<EKcka=^JAbLRddz=StrcdMJk-Z)T31H*|dgYgh3~qj_fidDc(eud(!%ZSJ|2zUgf}=^MX)c$&rUeNxT~rc<+6yGEa*w6D`&g|c?nMapq*hz<&7{hxN8{3iEVySmRj@`J6|@fudROTTCzUL0p-clq~C>pSMLcEh?!U-dk2lJ(QO0nHa}>{z>MR(;wZUhZ|4#W|Bp=c9UM-p{{sNc+@e_0_Zps&Ctr^~X?}eC<^?)*q#e2jxM}=InU2QyZmkymFHruky7jeRcMAem<3M(l_sU$@*!2I7H^Fx^ohXqdPiL9#79=*UNP1xEv?OW0QHD=mX?uMYDWRuZ^aC<Hy}B-?V81rLPvm@_bucS&nBz$G_R}>T9f|Z_Wwg`JCjODt}l0VB<wi>??h}(p5HIbUlXV&9%pPy9a}5KDv0E^;3=Zr+tj?3O3$V(@yDY!FTz1H;t0(h`RbGHlOG(deZvh7|!RDaanR-s{TBa&sT;h=_`jev*Xgub7&u%-ighJ`j_L9sGag`KGd6jkn^eL=Fa9@-R-XQb+0tOUd$aTe>Yw2z>Z5h(uvl)Rf%jq*B14c`(EXpKU**K+O5e?+Q<5%9*ULyHncdv=l`fc+7GAhq5j%;!F6<{=LQFYl9}&3lJ;-bJ9+(~_T(SX;w^pS^-2`yL|B@oZ)&)M)~VK`GA(`cvW?`I+aJT?V?EM$B}7^JdR44PHv_Vm|1pK`({J3&X6+u1rG4OwhUZ!RPrfw&r&@=wc0cVP|3yv?t3SLa&F7^9a@q0z-j(KO|Ei~1yH!(Z-nr#@($ZI6CrMw6tdnQyYfpR8{n+7o%vYO`uWCs_EKc1pYQNo7R$t!{Lh<fTX7x4a)-+!^K4SgR<}@e2WeXl>z*0G`%wv7o@tR(^)BIEQ{wdZ^-&C3(Fn<=uDIX>MqWQD9{`uK5&rBQh*!9vYjH7(@wc^(c<53B@&GJDF7%zSE%^;Q!n(b{lE{qq3vV7A9q)Xp)W*5sheP|wyml;2^d{*8>(SGt?6w7Dbbr9`8ZI83@qAY7m{=IE<Kjmjl{hSd;`=Sa{lP!IH-8tHi`4q7FhP@t?=dPm@Sp8KR`78fOW%0+_lizz#hNZ7q+tU8Z_kAp@|7tPqul|YFnLo{)?vF-?XIlE&(E!@#c%09&^v!|$rLUF_jbim59H;xHbHl?~{Kbdqc~`$R*{q*EcgTH<+POsz^SwN2pR@N-n5AzzYoz<HT4h36eb<R}KjXTC#W6HA(D)jV&wSmhHtj=J3=LuZe{_xhd~yn_uQnjxRJIYTuRhvC>&LGxS%0()ZyH}K_Odv}$1~;mHQcVxe68FxdLGd@o*l1x#Glsjm-E^A)Y|)ypYOrXXRi<%j~=Jl_0rDxlYehFyIxA?YV=%adJ4~nS|z2gUAn;Y!84Pd3;o@b=bLjRJx9uU!SYQn`<$K^c~4;Ztft?PzSiU(%V+)5YO4Rljg1#2em1SY<*(6t>a$87pKfhO<LGhUWJ_N=QJL;LzJ1H<AH75CMU~(L=G)((`-PNEsg}OFUZZibB_f^q7)NTnM;wb2{D{UynYA&NzVhI<^!4gvGFd;Xw4m|zjP{kq^{+Id`h#~}VDS$Rr2B>Rm60q?`@VF4ap^UWbJvN+*OVREtp6qY<y(%^BHuW!9jym<eb2FWOSQrCf+sAFw%dmG?YEoeu=p9YUpHKS9%kvA&px1W<XM;1*B{@f{92jD>Kj)k(s4NIyg!W-NIl-L{wQlsXIhSnBHys@1o=O;WXG#Dolg76$9viNRQgSz{NDDNolpI)AMKydb!NVHXSej#flJx-Qad!Eeez$wuzb)1>?qHEp2+f{c-+OGVfm(fdM5K*{ji4Ro9fz`#!2K^me0zWM$*?8dGdTdmP7mGiGA33Q9kR^H|=>%`_tFQWWV%?N0dJ!&R??hwE_3&y+gu=B<5>b^xP_86pLfbOQre&caklA)pakur)X0?mHB7A>3xJ%r;99(%P@-H{o4fA?t(#-&o-6PnD6&M=B;T}pLk2(+<P(I=LRf|WA*=}_dN#Vy;#<t)syHxH*q2J%~qG_Ib3@uUO%EGJ^%Y%<^Fab%FEiTn6KHErS-x4cjhbO*VDL}y_)q?bzDPvH0NSEyI#Lnrt4hpEjtfNTm>2jeI40(P%Z~iyd|yJ`BYv6k~&r6aWajh8%we4r92u>dZ#_RUdqX4QcZuj@VqM7m^Ai2%Ll!)EuGi6FrIH)D^i>e^!~v((1-HjuNZp2cJ$^YOW%Adg66{?Cb9b3A`|V~o$g(<^i}IUw9l{OoWkPUyV87nHagYPHw2EM_?0#!Fn{`I%EL+R;w^n8>K%<E*AnThKTFq<f2KtS^LJ^K|4r@UnBVp}J!gJn7t8#ie^Wm1rSnwW?y^Bt|NUI%YxSMTUo<6#oreqFv|lQ?tXukeD=)eqxgEsfs0**t{yrs_`Gyk(^!#=50TxHe{~FKT(^-9UCGySBcCz}~NH-c6LvAzQkYJ>B<hwKccpC*%o^Ser_p?0RCz!X7Wyfo3_XW-0L+Y{fsShhdar)b`IC{uZ>epWl+4a)PFC;&&GP_<z&yTX6)}$-T2i4&vtvij%vwToP9my{j&hpKi)lT|)?kbjVs%JE<6Vo2@e6~L=eXaXwmd~2sa`J24VB<w^?M~1CZ@ALF>|`pnrwyfj&Z+vzmcIE}U)o1av1j#*-j5rcYhJYUjal@5T-#J9)za7QCed?OqfI(%w{{HOk3VT2&*Hc0OZ%%oXU4KPEgdP&(BuqDzv#Vr(fh&T_$Rz+{LZ?kGyi!$jl0a67c6~Kzib-Ul}BW;_{098_2ps#_kVas`=}btqnO`WA-~zN2-fcHk95C%s#!KWt|gyoTo~P$Z#?x0@58IJI7-etx*y0Ill^bLcJx&^i@*Opt^b3Pc^s#=w2t8YY_VUnEUi1Aa`^GSw<f=86?VK@*G80&Iqlf_)V9~9acnb&#ZivMP#$_7W7kW)7)trE;X1osTHpe?J{dbLVELdPnM(KV{y97!Qs&Tp%)2blw@Yr6m!U0Lz9~~L$nm3ouEp|M$v;W=P3;=8eAeqvq4#2S>#^~o?i!V1IbO^On<$_0-H0;IKAHK;ZRmRvr-rP)vgEPM^P+XO$XA2!kdJk_xW2s?-AA0dmB#9SwT=9JljE6R;6&rA#H&k|zILq_jmK(EtUubC2Gnlv1FS#h)wRiQ?3-fg>-l!%2Oo`P$D40Uew8g5mcG%ufY#p`ZCU?|zN=BjR7qfQtd`JtzvYq1>U++k_5Enu7#6?N9E#J?D~_GF#F^xK>`!O$Bks_8-QgMQr($!9=8X<6?6|a?F!D#FU104tK12K7&<0uT{3NLq|8^(VPxI}rRR8b_c3k?K8}z*KeISdYT)#$s<7ZK<Ke-!d-Cy!IKR;n>>He<#k2;If={dcJ!2M=%9PE>g+upEtwM~(9KX_;#J6@$-IK^>m&FUM|-qCw|eD_tHho#Ba{GLRx^Izvaz3+{fko9lA-moq|&)?e8{yh9UR$u+T3dQMBj@4KDDCCc;$NHnJ{7la+)@QQ*sKXrTxy7b17RMaZjpj`^2iC6HRF3xlxZf;3Z`l7ETol%>mb#GsKEB^8?$6@+<a<qG*URYs4c#}tJIJrgW_y}v8|1NkQ1?gD`k&OB<(n3P@Bi%9@_ZZDm*!=MyZm?;_oRBE&G_~0Vn_48`5qfDhD%i`{)oYByqL;<L+yOp$Ht?fel_xkA7<mx^spkG5BK$~pK9rnST`E8<I<h_)B4h~Ih#-P%UvjLPz5%hsN>UQJ$><M)=%|;PVZf&?PABJTZhv9lF^UNhx+zFs-Lru&4=p9S@hiCKj&NXL|VT#^k?&}o|7%-cXdet>%W#APxtwk$MgBT==lTgql@F<`9sltcX55&Y+Bb+?bv#xt%;@Y%_8g5`!t8Ev@WLqMc=8~Jx{ju&82S8ce9@cCtCX2pT6|nQKvI;mcGI5F}+tRJ3_bgl{QuA`-*Iba2Dt7ReDc!^wL?@?yHrwp6<AMlEpXvN%OzWn<FevVjG%o)n5;><C-#s=BpRW4p{p7Xgo&?wr0M`l#Ki35`HXB-ZzwQswZn#O)NwG-B~-B9dF<(dM;yIKabU~?nwLWtB-P+Kd1@iN6mfgJg6QI=>0{das0gbWzut^%iFVAyS;1DcQWd$Oy*~Pr2Cm&eb{wTv#-(pl2rt|j(SEky?-6LIi0op!GZQ?9#2`G=(Fslue%ST@8aHUq4SwU-&YrZ=LTO@_EBEV9n0#gKTIJ1UQV2)ugn@s-(6pIOSkm(^fUCG+tUp?^YPuX{ys6B#Ww}fdmNkPA(np8cfy7tQNgU;M@h7QI39nL#m9HKYRqDPR{w=7-CrB#A7VbfcU5nEILO+4eGSho{$_Cu$!6Nu_HxN)?M69M9u|z{{kcN#v(2wJWLf%JkLlFT#osbn{c%I-&+VSD<JG%$r+hB@Ub^VKm3O4)kUJ`8u;apee0}-FRMzg}5A?joXAHaUN|G1NJDQ%u{9o46^GDwi?7C>F!|6NHjt|*&)bBdbKECL?^df)eW_rJ#TELI@)g1axY{fF3C;BK_pH39;d~4-E--#7{=U-I6Oc;#|JpU}Nzt~6m^4}2*WB+QxE$R8(C0`fr_zO!prJ6EzlEpun5T^Jk(trOa6EoWVul~tIht>}N-+waE+NyA>E-a%^1b+u@5B?532HF8U20Rwp2|N}&0ooZn0Xz}f1w0Y#3UvUxg2zKUg2#i$LEC}HfnA_&!7kv@&{p8lU}tDcurqihv;}x1co?)fco=vnv>A9Pcrdgncre%r`YqTAJOJ7RJOJDm+8Epy+y~ka+y~qf+5p@W+yhz{+ymSlS_j-6+zn~~cLR5Y)&qA1J3{M&9l<KJ5m;z1unOLWB6t_HH+UC#H?$vkH+T=UKX?y#A9NsiANUY-5cm){06GL506qd84n6`7f{p+OfrFu=z`@`U=y%`{@Hyxh@Hub<bSyXm91WcSjt0j;CxYX^@laQAJU9V59-IJ<g^mNqf-gW_z!$*b(9z&<@Oh{+_&oS5bR_sJ_!M*)_!Rg!bSU^ZI1oA*90)!Pbpjs-AA}A79|Z4*_66?;`$GGGeZgMPo?tKVPG}GCPVjbUckp)b7HBu{7Vu_hSMX-A2h<Vl0saN5f`x7a{{r5KBKT+MF7VIbt<c@zt>9mwd%(YfeW3fmKH%S=hrqvq4?qLJ2f%*NBVa%9QD_kODEK5a7<>|Z8X5vV4Gx2z1BZblp%LIna11mW90R@xjRRi<UxLPiFM*Sx3E*UK3N#j+0#1Tn04ISHq2b^}uns*B*1=KGv*0LjDD)IK6nqAH9DD|R0vZTD0X_yj3_b?-haLp`gH6!=U=w&R)EB%L><#q-dxLjCcY=3-J)zsdp5RT;E#OVy4baWt4dC@q5Ab^MI_NK8p&P+UVVPW5N<ycBg-!>T1Y4sBE(4tf7WxCY47e<c;4h%=V4-usUw|v12(AR32Nt>zTnStSMX)V&5m@L_ur0Vcir^a1WniHzz%{^jD1yI&t^^BR4gL!JHHzTc&^2J8Yr(a_-=GMt1=YYpSAlDR?NJ2Rg#H8;x*S{+{3VLuYS1NMp^L%Qz*SKM+dvn9h0X`tfGeX2t_YnA7WyN&BDg$?;BwH}V4*X?<-ny;1eb!&01KT8E(I=uBG?K#1uWDJYz6+LP!aqQIteV)2o^=~2Zf5@&(QC|LMMZTDqv9r7bsK&Ux$_iiz4`Us5Mv=!DeU~uqcB6gq8)1BKS7+3$Q4H??EeoMG<@-S_v$Q;D^vEU{M4=hT4Kf5&So_I#?9J&!9EHq6mHtwF8SH_#fz3U{M6Wf_@DaMeti_ZLlbU-$B0tiz4_vv=&$t!Ed1UU{M6WhSmg&BKRfrORy+{UqGvYMG^cIS`{pc;3rTUuqc8bK`Vnr5&RdlB3Kl`51{42q6oeVEe94w@EvGruqcB6fR+M_BKQ`x1XvWoH=$NwQ3T(BiZONrMesG~NANZ9Rp<xsRqz$)XYgl?CBg26<%hzu5Jm7j=xp#j@O<cx;Q8PM(7E6R;HA(-;HBVY&=ufi;8jo!yb8Pqx*og+yb<~{cq7;Y`U}_tycN0wycN71x*NP5yc4<yyc6sL-3Rso{{}q-{tbKpdIWp`><2vw_5&Y=27?cSk3!FYkAj1sr@=ws<Iq#!<KSb^6X0Xu0B9gM0PGJv2=)h?p!>ll@Ls4dcrVx+>IL=&?}Gjc-UZ$U-2&bQ_JnQ%dxAGZ*MT>KH$Yc|H-Ohde*&)suY@iJuLLiL&H*n6FM+y)g)RgSEG+#COBjmav(N$Hv)~Y@6F3AM3LOj%1)qlw0iOqlLx+RI!BNl=;3#l3bQCxm90UCh90QJpjseGl6QJY33E)KNcyJ;(3F-<?0;fQY;1qBw^m}kBI0HHvoB_^+P6KCxbD-0~IpAFAEO0LPGIS>RGB_VP1Dp@egH8qKfwQ4gz}es|s2ey7oDQ7?P6ww!CxX+!$<PVlWbh^ESnwtAMW_q-A~+s88XOOfgF1ubz&dm!SO;H#4g+5RM?!~!Bf$~SLEs4RIp{#J&@gaGg?`GQh#zaH71$bF3R(hO3S1gm4qO`i1+)VA3veZ96>ueRRcJMERd5Zc9k>SA9$E`*53UWZ1Fj9O2W<qd2W|lU7Tf^b7}^rt7~CA%2HYIn3fd9e3fvyr8QdQ10CfaAfV)9^gS&xMXg{zD?gi}&?gj1%?E~%!?g8x%?g8!!?E>x!?gZ@s?gVZJZ3}J(ZVhb#ZVhe*Z3=D%ZUSuxZUU|kHGu1b>q5T<*9CtAtqJ}H{1vo1_$%<2P#f@<U|VQKur0VUv@EzXxIDBZSZEpWeX+MKEU74h)1Y_3Y2b9|J#acW1Ns1*0nUUz1ZRS?pnrk0z}e78;B0UX^f5RGoD2OMoD0r_J^|-}^Px|{`QXdYXW+}=E6^9<E8wfpSKzDQ>(CG2>);#EkKh|%GgM4YX8bPr7SswXis0K&Yp^JS|AdwViz4_BXbG?=f`5m8wjvfq@J;9^@J(<5^gXx$d<{kLYZSrHQ3St)egeM){{#ID{s;U9D*E>ZzYBf~EeU>$V|xd+1`iu(RiawS|LMQF`|ls|{77N{@!fy^P5!#q@^5x1oG^-C{tg>hN~|Y^*Q<oQ8G0agX3Bp7Hi!Ua'

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
