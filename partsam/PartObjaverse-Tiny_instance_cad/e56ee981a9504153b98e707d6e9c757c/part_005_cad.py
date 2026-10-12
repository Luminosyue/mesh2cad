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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_005.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_005.stl', 'source_sha256': '05f2cd68c1a0873d51cf9c1b4aa2a46f243d18e46b60e41c9bb19c5c2ea0f409', 'input_faces': 880, 'input_vertices': 658, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49791428446769714, -0.210149884223938, -0.27523273229599], [0.09535679221153259, 0.24717630445957184, 0.18083572387695312]]}
GEOMETRY_BASE85 = 'c$}qu2Xs|M*Y>%g7ZDYtsT>uI^xoT*jub<cDCH(3fq=9mbdZZ7fb=3t5xf)?L8bSS8xkO(6akf2K#qtADgrj-RpgsJ`<dgJN&dC|^?j_h*Ylj`?6aqrI|GZTj(PHyu=vlDR^;AE>uWZ*EV80j32StGQcB{0_~h!tMvU`W#idSv6fWx0vvX9m&l+t_h>VL*9*`8-*p6(P&@i&99hopZDJ3apSpVTkaq*<Ljd>+GUg*h#Vn)P^=V$BJYgpB;Q>m&w$^KvdDJ-(!oVj=@o$_+h3AGRq{$tRV7G8aM@m2I3%3SiXR}cQQQR=~YQ?_e*{~D|5*$$3br^UHDY7IU6+r7F=(@VBlE92i-v096Bzw&$Xx%vxxHUBRfy)XT*v|Fb6Keh1#srPaAYx=r;8)Uh%V&`l6;QxL^&(`hYVNKsKf1`XpQFF3a_fHzVS^8hilcDLU(Xzh$e@<?z=@aT~lh2Q2YX0Hj&&c`;OjweX?)CRq*eUhYwg<I1kx$F|3XX^idi}%S)!ZZX+Vge)a1&Wy;VYq3E&k}PvR;Cb%QXLRkKPAl{ulZ*f2U9#Sug%Tg61EXuuba0_QxlB{X_AaWjU>jziH)lE>@M_`<u2Hr1}4+Os4E7OFL-(p+2*uZk;STP)m12Y?dt7!UV0oLRPlaLsNd4>ecN!sfXnA#0>|uIH$joda&2zMVkM!qYumYb!+d_^z(bAZWqg1p_Qv=y(3a@Flx7^KQU11fiF_mYUyU~k-9%=>JBactItV2)MnCpEly(5Y?+@XFK&|WFMQ7Ze^0)ZGTraSZqfAEo>C9|Ip||ezr6Jw`P^&!cCQ|ci<aZvpT}CK=@{3})z5cn`u%Bge1@{WSf#~3HI>KjhQoU`|3z!wmHBU2d5PwKprK4Juw%>tO|SEg9KTM54YRa3pKbk6w%6RjVNJJQlI0BFZkFuT!w>u_>nk`qF+<Y}f6e1}W~;b#kM6&Aa;x-TUh|;l|H)}Nel3hUS5Lbl+s_}dPxpWMS02Cp_f6OQtuk_)+8YaGYW~M-aDB~eI7{<S>?_BqwfYg=zg~*0FRS0UnO^_EjZQosE?m^|WA{GG<8=OkG_QZC-o*^>xOV;D@5ke`L-Fxmf9I{9JWeZa)#@`);y91fS$k@G{q4s;=J8nRu-0Co_sYm|XLaBFsut(O*E~*-KcDW^ogoe7xC`8Ta)B0S*LkT2*KXgZ#Ti(U$6eX0%QgRttEC=1dTzJok8$U`d3KHF-@3XScY&%|J2e0DQBt=yKE7V7x0@5B?%y$MtLA?tP3lhjj<P@6y#{hWZ~DVhsn6KCQPay6mg`x-*M6&}|8+-}$A9nVb(+4m-P<y~j_Y=K_2Aw@a$MV05>{*eL%T}d+I?-e<{$H@EWiEDxFwo?Ym(Hh{=e_j;`knx>#x80hch*O^a82dy?3N*akgEN>u>1nv{y8}REiwe_W1`gyt=>pR#{*EaBsOjDm{EBKabzcq6fYH;d^_zzJ`3Arui=|CC9J-htG8X!GCkRe)Yy&ufIP}A31)*(dh3=-`+=#-@qT!7ijU@hov5VWU=o5^QXMdo_SyQPpc}&uU&e9=5H@sBF9OfP>*?De<wa$>fwYAy8nsBJWlK0o96Ym-yS4&F~Mr(4V2H6--qih9_959-2RE<Uiw9=|G-<3JRWDwi__8_)|vHtH^N@sX%;KTqw`sp8Jb@9HP+V;*7}25AMK`1-qPado6P#2Ra$>@o~y~@=$DUIY5A<$n#XDB1zLZ0*6o#g=y(lnyg18`NIkf*lQv%L-uaHodW*gFu~!duFC_I);x)O>2I8Z+pI1wh>uk8srHz{Y_+r+})!eG-^K0=sJ95|uUOm_+hR5TZaXU19P$aLj&6};!^s>XH9;h>Jx288PD%V-7{g=zMbWabFdZ^G#`!v1SIax2(wU+a>II~{h{8helK+_)_!29Hw-zI2!@-I>k_goqF>fv==<Twp~*tuQ0SMRz~>Q1M58JhpAHRL$8N1hz-_4hxW%KDV{2fhCO$6CvA>TF(_rupxBhu7abhjjn9#>#Q(T)+Fe=3nP5@1M8k$<+Mw?v~@%zqZj#%|BFv_mMmAYw-i=qq+Rw_MPVSx96<oae{q<(nCe^@c7L0z$CAK=zMkFXTMQj_fHzb>ulE27rp*Y+jpeyB#hDOGxX2VEbea&$9i@9%NwkZ4r=Wc*!2tVhaVp_SBvvjab9P~Zq)jNv+g?YlNYR8s>Pq@<9%$Pu-4x~XV**J`hD?gE!~WLtS@>}>(2qKzjn>^b(-F&A@7Ip7SzUzb9W?<>k7|m<I(wj6tCA)Px1I&+4O7K|0iFN^Nzn%>}E}G{g+(-f==cJO>e`x-RkRYn!de(Tz{P&f34N@9jphZw%w)atMbZyc;KtS?|Sv%^=vs01TW`Zq51#7y8Xv%do_K0DgK?D)P1EE$4TLRc%FwBX!<v-TU#a^&~)t2t*YULTKvoRWxa>b?ii=}f6IC(@J3kEGxE#*kbUispr#k<#`Ed$mhtIcy)g7AcV=k*C2Gm`vmWC8q|*KSD$4e=##>XpdRXaCh7Nk;_ygluA31xH=3gyV{{Hdr+%{L!tFs=8>zL_{6TY=n>h`6wuWR`kevI37?|Tb1eFW>_Tif(FQCIoA<4W>8E!|~p<v8&#+`cF`J#aL8zNRl%`Z+DW|GW3(`f6R(<NL3&?(Z3``yW2Y{`-vlA7MRY<lkA#^Nar*y&eMZvhHO4s@1<ebuqW=ZoQsE(1S)jJ3kbX&;Bubd)Ys-9-i1qi|_2K!~T=>{$THCJ#6d!!R|F)&U?-Ry<Y{OTPZ`dei$mfh0hr#>;2Y&?$~<24g8QL=THB)djAhW53P^V#!F~*ex5&%>Ep|R?l;Dlv;89LmGp6H?_fO?SzH^}PHZJPuZAss9<T?n9@wnU1EGCk_8+d#Cl2&r&nnvd6N-J9_g$Ct`O1Or|6QN2ocswqZ=ciWJ-Yzw_MyVsJQ-S>&U$x!UUi^{QuTQ?^wuYwpCx%d%uTmq4r=puAn6ACKdR6FPVGp!-wS`O&;LsIx76qVK#`6|wK!jvzeswH{h`v${h`v${UP)m`$MIh`$MIh`$MIh`$Ltkxj$68xj$5K%>AL#&HW+t9Q#0}oBKWJIreo*H}`K!H}`4KbL_{U=h%-y&#@m<y15@yy15^No?}0z{LTHC%8$7pQ~5XdV=9ihA5-a?`!N;Y+>fa^=6+12YwpLCZtlmFZtllae$4%t(vAIC=;}k<-;DDRS2xZ>T-`ViadqQ7MCs;vi0f~hhq(U6d5EhU=OJz!<2=OGjq?yUj&UC1>c)A9(#`V_rJLs=u5O%%xVmv3;_AkEh?}l)9^&f8d59awI1h3Cjq?!K-#8CZx_KU=bn`sK^*7E#T-`ViQM!2^;_AkEh^rgtA#Qx*JjBhXaUSC8#(9XV8|NWzeB(UC^*7E#+<Y46A+Eo19^&f8d5D{?aUP;{^E|{3thpfjxp5!i>c)M9s~h(bN;mH#T-~^jaCPH8!i{g-N4WmReT3_8+()>&aUbEvG43N=-MEiXx_KYr>c)M9(#`t_*Wb90aCPH8!qtuY2v;}mBV66Mk8pM4KEl<F`v|3*_Yq1r?<16M-bc9p#(jj+&HD&9UE@B&jbq$Lxak`A5pEpgKEh4cxQ}q-821rw9OFL1^*8P#Tz}&}!u2=qBV2#uKEf@paUbFO8}|{;pyk|e_uta*{guA3w0`do-8!GH-}@`QOAFpljG4Sni}QUN->-BWzf1Ek+F8H%SNfgW^4{NHr{i8t&+4Gx`zyWdPB~7km<#*0beEKr>#V&sX}+e%M9A{^e=Qc)^wmrFK4$KS$zDA?cDx*?{%gJrudeR>LyIOnuj#n=_m@uB{fAWM`YKR{@BNjId;d^c>w}vA(~*3hu%klI>mUB6F7Joy&({5M?{8O$N!8-x-ak}niRQ2F{e$N+Ui12^d;ef;oaV3Y{hhgUCVKtVy}w#F-8h#j^Y_{51GV_)OY!gj<?S^8P`}rC|Gd4(AWcsS@bB(7;<Wa1A`bKZIp*OsEuZzK@bB>{?;p_o&z|G)-e%q+&A)OA-|si7zE4Z{;%@$Z{r8y_n*U3+c>FdQxm(kpjA#A$thHL4BRlkaf0duLU+{QunzmlkM_asJpGw}U=|c)@e;*)Fea+{xedBKN`BnMdhtqS>gD2bRdIIZC!FGpR<e~>h?bh_rfW4egBfiqZM*L75>meh)(*20<|1*x$edDsMm+-F759Ou@4Sy%G71y)juXH#5al{$>4aeUGf9RpqmK+Cquy0?fhfCh${ZQG@52br_XG>kK2k4<%toxh5AN6DEPOR?l+^MV8r>WZm*gxF)kJGuuH+2<X>1KRWSMi;OtefRkx>;T)`{&cS)u+<U`n0CQ-)LV`SM95GvwclnwXbt<<LTV`zp1PK@9IYXH}#+q-|YXU9ya2e{omA8{)4^-$4R%cj|`LL%(F|zF?B!UD?QlhJg;kpztRKnw{CYkMrgOs;{KPo;<McJ@QksnH}1;%{X<gspFj3Vu6pcb)~B?RdMLa85iP!<yYY`bC-oq7Tg5kZ#19rJ&T-CvD$})R&N(IHb&HUC_;BSTUOiat-chM9JfW30m~vC<!BrKteERp_ka_^RN>}Nj1~FN=`72$OOX)%As@`(ws$Ay}a-6>xW^4I0bQM2XA%pYTW<j>M-g4+F{<h7W?gtaIy!GRs6Oy{sEKMs{@bww&AD@)1)hBfS$0MZfKNsSD7CVOPx$Gc4{~JbeoB;`1eyn$%<TzuhX3FnWKQVL%<qbJEIlUt<Nj-pcm2MZ0&eZxt<Ym^6CS+>)8R4)V9F*y;e}BY9uHUb>9o5>`(B1Zh9*o?2)LZ{Kbi@xNZera|J*w6JmXD<#fbQ1krqx`J14n833ET~_|E6Ruez0t`)U8)*%JU`*{nyk(AMQM?>EB;lkgGp**FWDs^1aow{XuVk&Y`RPD1BwygWmQvb=AJXikGDB+zfIY)K6g8Mb_VY?Vz{aov+SvoKg$5_~EC|uzq5ZmLKcx2T~7gd+nIFK22S<uk+kG9{=}($Gq*ELq~l3)NHBye`|fr+rFV+(^x-VM@u(6V-45q#v>Wt`plstzN`OvC_^i+p{x3IiY_~xTYoTh)xNH7^aoQ{{^660`MZk+wRTZ@_?ZG)I|gGGO5MM&oZcUxThLW`1GU<)UhAq>Z>Fx=OX=ZpSG4xZp(DPtqAAx~$2D4eg|9Z|ee2NqTDnfRCcMt&DW>IL={9t?y_PqUx>fP746S~kJ45egX#G6BHt#E2?9%!}4qeSx1#7WBV~5rsOkMQ{>)f|lx%PkPW`7PRI=mh%T&&j*^x*kLQdjepv+1<dt&A`9dNXu)d_fNv`dlAhrmn`<z1woW4z3xj)xXmH(B1x%c%Ai$(OUmhx_#(Ht$&8^9A`cGaczFfp{x3VZuVzWSM?t*xrX&03u@&G^;^Z|T3uMHH~W(%ylx#Wr`5mGgV5djuQQhQa=rBWH*~lDq5I={==E>vYX0<p&gCgsNn1DV*Uw1ZDpW~Z$NkffupU)TTd%EChd9oXGMQTc|9P3zLkq5J^`Apm={8u(`d8oU{lU=P`7nDi_k&yYwDnZ!e&}w0i=M{%2d%XATIu#L&uQzm)vXunEk|hkfgHMO_hmgeK6I5IQ&;U}&$YN*J?m@xM*GWuc>F_m`_I6eQn!j!&GOcNc;gMJ+tA&8-GDEp9;#DD-@ic*Of04C-|VJ`d474&*7kvRS{A2U+}8Guff;*QH-6Wcy82zCbn|zOsjJ^LcFFCWpX4IiemjS*^51VOr<+nluQx+?>%Y!SuIDLDwEcDtUCqxEXK<WG&9wS7b$36h^wMJv<>v2{8l(NrvNOkXy3d?AtmPki5c<FC-6;0|Ao-BDKR8#DHQnv!-wkB_;>p9__6=7{&~$g7GrTVAx8k+mi8*vNKkur|<$~_6?}o1GCv?98uYV)Y9ro6L4qerM`=`0zLU-%a(B1goUk>NiKTTcrPggIPEp@vP|E@RnK=dw6H~X`x2aNc^DAp|_zS8}OZ{2KhK&ET#_e@>w-&}nz>%k2>^*GS25Z_n0y0Jer^&IhUvYsP8bQM2*CSy--`8RcU|EY8%|E8WJzL9@Z&k^6qzp1PE{?w*BbL&5*uKJIw8~w-BRsT`C*?&wuV8l23kEyHv6P%fk@8O%3<nt+<Yni$_*HXGuVDquu{FSc!tpy9^-_r^8n5)G%b#)G@bmvxsW4ZY&-Sz)zzSQkM5WlRhhw?T&=G8-^rt>|Mksni6@s)1o$JCX-|IiGnoB2_?nV)d}_40nptbbEi^{I5T{!QI&uT5F3w`zA%_J{BI_lnX3ty#AlKgfSS;^HxRujbTPctSpJ9nI?#^gvD4?SlAwpuZpIzt<9ke}Mg!9)fP)9nF7_qRUCv$F9-xqjY=R8ZAHmG7jIn|J>@NH$O@b++^L&&-I>s4(|Jm>!&~bp$8&Z_ai_44!u}!0sk%Vhwec4Bffnt!1w6?y!MILU+E5X<sbOxTh?0~;rLg$yh;!FS@)y7!On^N?<`ZE{>1CAbbA!*(mzW3*XFY;72F=KB${4WA*+Oy5aao$<|NV|g}MJz^TfLUU;os+VZ)mL*MDl>B*L;<33~=u2Yi#yvi1wx4$K7qTUb%?{tsY&@Nxo+2zwM*0KAm2$Am=!>w=dQ_O!5K!1CY?g;fw%8TbVF6L@|Q_%L`o<hvQL33xuFao@*S47>pHcgM&0mydZQ^41vG8oV)hQ($}W2a$(=e2fv`<x!q0zy{zAkk=}}X5b%+Z#MY2z6m#i?-sVp$M1LH9r3S)T@rQ-_z5`Ws{`tfuo3uo;@uTtUjn}Xr~Kv-cFV_j+sB;Ru`KF{urT;V@$RUw^T5O4)D{&{7le<1Q+ey7tb}dBsjpC<xeF`=z6oXD58Mad3~lNMHU}>*%tkxd=pPTl=Nb4BJ_}w2bzT+d2S0{7+ymSTULM~(39JfkA#G~w;z*PD@4~(n_8agrIK}%IF$q5cC!bUBBRm2A5&S*?t_Kgp=OFMD_y_RW0o(~r@3!GP!Y$zR{t$c!v%s_Pd=B^@@Xh#kD{ve5Rbk&_J|MgYegNO31Gj?z2Y%;(SHWq%sU5-nt~UCdno9~}d=mcG$DCqiBOSsc;4~LK5W#Z{;p5<6!RG=n8~j&czxa5bAk2$7V?X-dap0%mk0EAVU_Ef^V~?Vr5tat0yi%UO16~2AzJ9~U<ACsIaGJYXMsR(!L|qWS0H3dbH^9qa?34oL2d6pbDU83TF!qR3`AVRSgeAf2qAaa}ZNOWDw+D6ruN1*)M*>TMXZU!HI0^g=ykG>+xqtc?X|DYfM*Jt>P4GsTM;ZbvfIDcfZ-BpotFcGplJGZh>W|b9{stBWFOP9t4EPZEakTX}KnJ`9%G?+j2~KlPHOxDNYK?j>g1>1BYz$86_>dMMtwqJq7Ehr)o<jQ(j}q2Z*dSmcc$~0!VV!`T!8?IR0lRv5Jf7nbNAWm3$00WHfx;4my#VY2-ci`|!Uh0i!3Tg31SWX+^LTz9aTM=}=Z=U?yq2(<!q)j1-}f<pPuRP{YD6$rk6>OM&ozPXgR6J7fHlG2MXdLM>%e=9chM2FA7zXI?<1_QupYpk;61>51EW2>FP{4%j^cgr+y}9V_ZQYr*o(kk;N69F6ZSIjCGeNQ`vd!VcsD$ELmb7s<GDLx6aP_^`3GU21J8n=5q4VGb>KDd>)<~EfAH|rcs`9dil4#r8N?<Y6lqTrHU&5xJWbeSVGDrsz~>8_D{Lz8Rq)xu=D=qGcp7jzcpCUr;56{5;PZjA!DoBYq&Tzi-7Msh_)Pc(fz!a};kyOkbMZVCc}@dP2A_$zvw?HKUlW!pYzFXk@cE+d<_en!oC7{Z*lWU80at^s5Vlg-B;c#y>YGKtRp4_x?<e8iJiH^H1<>ap_8e#{fGW*5e4N)sKox`Xyb#|l#5an+f#)~itKzLj%+)Bv3gqEc<nL9KnfNGCM`MJg07rul7B)oKE5M=P<AqJY`w4hQd<5Q)22KPY4W0shgvWmv_+aqyz!dNld`o<I1m|@aFa@0QJQC@QL|ny(<9RrIM<CuL#GHgOj7Q#v;{8y(BfePF(JWza0%wDd74MRSjRPiwFBR|7ge?P30}l$DEGz_k2RsD67Ptm{8op8AhQODBzYSaq{x<jw;8gG#;M0IX@Z~<v>)XI(;M4JL2Jmf9j8uG|iZTR|)*8HDgLhL=_UTA#I${u?DeQG&OMq{Imlt+NY(3foNBEfEr6U1>Nj}Es!O7<?{0K=S{;S}>3wy=KIL!Aif858<gl)l-g>@7*64(KJjIbAId;mLx|0Cl3Z80ZI_WjE%AYKK;BL0)me-PH!$M~|3`DkHXs2>5N!2c_J{<Js`gu{`a0m7OHivczQPePrf06T#fL)!I#lqT^B!nz9^2kZ(?`Klu<8dwXQ(r+hhD6kFqU|}s$w}h?1hoNpq0NaDt7S>1DOW<|!{GzZL!g>O$fm7LSq;Df_;?JNBIs-?cZEgtuGo3^E7-N0Rsm_a{d__?<;!mNjI{-(b?H@#}hCqrze4wxv!s3C=z{d;gCTt?G2lzGd?Ny8Gknly+XM(Wi!Uh5T;Jt)Z7uFkC6P(KOkdMnl*ciOOum<Q$4bZm4pAhzk#qC5m6m1qE%tBiejsY)>yw(CnqwQmnRvfS?IDPvpz9)PEe2B1C!V-bcfj=Vbrp4bA#vxWeVfE2Q^-;&f%L|{jG**GF!5<OUnCb%95PXra1@Iv(2fhe61lSt9h_Kog9V{}|1h<8?6ZRCa19&;aZ3#>SFD|Tsu!n(-z~>2@BdiRt6!<g3x(KTX>;yg#-}r%Lz)K6G^U<=v=fGzPdtF#b;3MDz@UAJaBzQq#HG~xg)&hS_SSw*q0Na35p5u{k!sg(VRt(aMK^qW%P*{Co4*=_e7Z6rmSUzA?@HAn4@m*hhLwt&`XtYl>+NKE7ZjSOaN12Gzad8u2j{=*4PZHJ>>Gwq1#QO`IZgIaMe8|Jo@SKLc5Pw?O^A;UPGqwkRSy(E{nToO!kF?~^X8DJBB|N_+Y%#tiEDuioswLW+&<~zRSY=BNGl|cFr=pG?02Tp%QP^aQ`!Qi5@VvsR2+I$w23}NH9bv_Q^}r{i?g{}5fR7W_75VClJQ1g{e9PkTOqhWAVXWX$sD~)j1^uD3|4b^QkFlJOIrZCkypM-ZI@+1qdjK#Ve5bHI!b<uWOZk{n`^MmX419K?jj6Bp2gZPJ7PigeIhF7c%&*kGeeu38d^V$v>!bba;~nu0!ak<9@G;W*L7dtp8t<dwvjJ^W8|_vb?})!EY#r6PkFki4d3THZ@w>ov;5447Z+8dw1P=*YEi9jpv4D^H3uwO(a5ea|Xww&fUBOogdq-G7A7g$W^KNL@Rls+^E1|8s0i(d*6Sl_UwU?0A8{)kL?}7I{;6t4HDfQQ0z#iZq3j07<aUUb?Z-~DncyGM#4Ikn(&(VDM60kS;7GWEOmGCh>>|@?f@IH9o2R_7Ue9$=Q2kZmBOW1Z{rG1Q#`k2QG9>Dtme2CNfK<h*-FaRDFwolk&KE|>><_Utw;e8x@h|@er^IZZk4m?{}mc@G|LfQuqA1wGFydMM~;<TR7x-u9z2>g_=Pc7cV64E}2_%Oj=!TVR>L!8zPT0e#XUjaWS?5xFm1j1*qUq}*s1m2H;4{=&=Y28f%jsX8g*acx#eT<cT%ts5Jg7+!#A>LV7M~mNg#5>}Su*<?K`53GCm?sN93hzh3hd8azv`!}jM}dDS?7XmwKE_BN^WlPz#QTx(Ax`TCtsldIBf(D!J7e*08p5Z2%xRA@6z_+^hdAwDXg@RrI28Pduum-hO+!e(qlnYKA`$Ns;X~YS@p>~5m<Uea(6?=Y?ZGKel(*-BoxrKgRQ4{wC~&G%s@rbB9^lkw)OOv0UBRhOP~Ug~*cqJq9QD19zz*Qlr>SqZ1GWLDF+*dg74SK58k00OTL7DZ)0n5R-vrnQoaPjoTN(iCfzzBtb5|W;EpVC>X>P0mtOibVF3r8wfi=NtPN%uOHn1)@tr@g-)CV>Mr!|SzrpCag;I!t^+SeTD2d6ca*4CE5*5I^8(>DqDwmJAji|5$9z$)OBF8%hPwU2NsIPHOtqTd`vzamciC|Xx{19yT`-fml*Kf*!2fB7$XCZyk!#A&_VVR2arZ-O7Ucu#*4I0T&brF$)2*9rH4)0x0=jIZPHB~CuK;ddMP+k>*)L3!?A91*{Ta!{S^M!AU7UhXrD!_P2IiPPSj_9^>;>EKjGYMa4mqn6;*Ms#M;8u$v@>~o9vj$Z<YgOd+^lL4gtQU>zy7xM8J<`d#eh5ZNf4&ixl8iVwkuq$vJ_&tl$u82H*34T%Fa*O9i!esC~;$2=J|K=r}06xLuy<<LL9&pOTedL3X<__X3gk7?Do+Z2tPBE(@E@5}@F&6JNeLxG`hrCt-I^bUmTxszdK{y(m<|ryd58y=bIjGloU?%t_l=(8S3i#W?zOs0|A-v$>RKFL1mBDHM)*W?1H~~B_@>&)64fq!Vmsz}45+;FLc=s&u9C&;5nJ0m7f!{|R(ODDWc<?1cKW*{4OL*49|G_gM&C$f^cMOezw!op_6tfcI5_SVWA>O@d@t%Qj7&x^*<tYkCd5J>%QhUAtd={MgHucdI^i?`XBmRcq$1L7|5Pk|yKGc87kFX0k?M=s9yl*9p0H<?2%4-GW`4sqJfeS6(I}r{Br*TGk>I9^`5T}?E5tlG8IOXlX$R8oCZN%pbJ81Dfj4;c?|G+aLt$D;>6&AGkHyvR?a5^`myxPcfHuwR7b1mLO5+;CC%-<|NCnBVC9OAu@Mm1o5aM~x(St{)%2oHhN?;-mAybZVm{0Mvo0_TC#@1ac=uXThsz^N>~Q69n?;B<yYYb~9l5!L{wHHp@ymw~C^KMMQE;&qj91Naqz-&%aeNJ!^y#OZg~6y$3P@<u#AzNrQzU*c0O{w+`xSO<KD#e4hWzy{#-+v7Ehf0qyz_VB5Ao{AX6={LqSi+_I*7W42Kc%FgS#AgbdZSfftVF~b9ylVt}7@U0K;78a5JOTZq8SqgLpO0t4(jGnt&x9?&X*|;SdkokLoa&tRMpW;F)xl|9rgieR_3wH~oYr?*Q}+V*gD*rHWr2@@Q(I3)dlSA0{=KmGE#7|-z6(zMl-Bi|z+2$dhiOl<1GpP}Fw%YwSQeb-Gn&`h0G|L~FYLO-zuO6E&qsU`-t`2o1E+pR{rCp(XK?D1sd%4?cbkyb5~N3HgRd3#oyEWN326_y8a^Z7N7xShJJb=KITO-3J@NIZ)9b(=!6%`9*8@KSr*)9ly$ZmN;8f=mQ167@!J|6*B1+`>fBjcO|Nf!7CQJK|hs-bazc%Xqa+rwa{w30=j`?UV6O(a-+z2I7ueJUMn*9hg'

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
