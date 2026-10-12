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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_004.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_004.stl', 'source_sha256': '25924e6121a2a6ecd6a1cdd587e1c892fac61de453dc9091f4a26c27e1e67806', 'input_faces': 1740, 'input_vertices': 902, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.166567862033844, -0.2769809663295746, 0.1261885166168213], [0.07949766516685486, -0.057878851890563965, 0.42419901490211487]]}
GEOMETRY_BASE85 = 'c$}r2dALpG8~67)TVx&*2|4C@Ry5ivQ&N(dI5KA*L*bYyO_HIMLqaO)N9MATN@meHhU!FVB&BE|@4nabxtG1~z5jTx_pNJP-_P@XzU$fRJnLR-J$s#VY1JZ_t#H8oS30m^&42w1v<(Dg%M&OZ7}aaoh<-hK4X-h1$e5%+0neBJR9}3cZOc|2lLDgxPgLyLYj}@g6>m$act`IB6|1FG>^*qch+*9absIdaXD{)abRRIhSHvIQxBHM@k#?n9Yt^ZiQnzxolyNElkN@S0975U+t#@t}T~+X)X!^QPX2U2yd?CN*XQft2=!a{yi}6#7=5+q{>l6BEEBnX#zg#}x<paqH{jBH5$M{(z&w75^p>r9D{FJTF#pKibpYZ(j>rQ1P^26g^jm_`<#N|KA%t+)1_AZZ|hgVj6erVgFjD-H%t77tj#}>HbuYMpSk)P6Ybxc0gU{b>Iecz0qmc4(%<5%Ave_G#m3Fk+BJ3pbW_a>Zw_3iwJzpt0@{HkxyZ+J`P1BvQK{kZ!1vdn=*^{KwC&-C)84@B2_DErWlym7zkbuf{iHM@IEJzHOoNBxx5ZQMB1e#uDWhjYz|$p_Ac+&G&)&Pe13)@+K&hicaK{M2i9$N1?(%Dd0K^^J@~exSqg*yH~-==mvIW@aSvLq{&e&QIB|-1+@yWJV%Cb$ITh(SGXpYu))O+AkxKpE9;+Og`=WOm`l4_smG-hj$i_$){iGns9ve<HlcfOXB0lx5u9{w7km)l4JbP#ry{n&71mm-oi`2+MnpWsBh0pVCC}t3F`sh)<a;>`2C6MO?_K$q14{{6V<c&ww?pK9@!s#U8L<V;O5OfFYx1@7smImNBp?wh4KCCU48q!Fus33!H;`h7~j8N;m18MjPKtM)wj<J<NNnpod^58u)f~U@#CHs#`m8W_;Jq*>znc8o)^Zq#~=5+Fut9ixaWoO?fl0*FN|-`Z`||3_;K}PpBKir^=Y3MfvV@Wd&ggCxx246y)(uS2bQ?|^N?#2`spP{#*VY<g@e)O*ZSeqm9gXGdEDKfZ&{R)$j_>KA|`L2YrdcC{O~)!#rXDlXMLSd_3iV{`g;HI{lgEtae5EWNaSZ#%yBf@x6eoG>;2H5H}iZ{KQ&t=cRbZwWhC-b?x-5`x%PQ#eZ6n{^JAW;*4O8P|MTX(=<0LU%^8XOa8l!#<FU_Q>+AE&pNF$ySLe5u&q(B_v}qfYx6f<q>+{tAT%OCRg;FvS`T88UzCOpTpVq!}?EIVOyY=nyWR+;0@aI+E{=9ZQV0}BEc0J(N;eW*wo=5fVd9>>X>&Ml}l<e+4oN;T+ICfoOeOsStdB517sQ%Tr^>5c9*0<MPxP03FMAx<Yao4q3w^-laH|)B_`u4tL*De0>T&nN+araMrd;bh?Om^d&`?LCS_vbyQ_IdSV@BjGr{vY@_!}Iky656-dofosdQs1txtgp{6_3iq~`u=)PeY3u@zCM4|x9cnG>+@ZGyS}o%t{;5gtgo!E>l1$-%=#+MXZ@qTU0+#W*H`M>^;Mj2#<%M$>)YeE>nrQq`LXLO>)ZLa>nrQq^J~{v){m<nv%a#vt<Sji)zn$r64k%@w*IZJ<EwA$-}?T2Lw!^K*4Oz_-`2nNb^g`2^>2MWzrJtk-}+iV{ydoakMpTd^=<uIU+Z6eTmNys8Q<2w_3iQ7`nSHFA6x&{xASl7-}?6a+WNPCT>Y5(x4x}UTmM<Nw+JVyfAwwsTVKal-`2nN_4s|?)W7w0e$==1Z+)GA^=<uIU(c`aoBFrD){j3ArvBr6>QjAN|JK*~SKrouoNvar^>2N9{I>qBZ|BF>zxD0>+xoY@J-@d8tshrErv9yO>oe|s?046Fn5h2Mk6Zs3-+#W~$E|;i??1oPx9cC{`_D)Gxb=_m{pT-!-1^7({_|aZyZ$l0zkbkpu<IY|>-q#gZvA6?fBl0WxBjud89#3QV|;u3aqA!B+xdxG{}|uSf86@V`1bt9t$&OkS3h?BV|-hmaqFME&u{UL-@aeMk9)sleE<7}j$_|18Q=f@qT|^2OUC!VAK}NnN5YSL&trW5`yhVY`x)c=-%oWM`~JlE{`YSEdF}fU<NNOi^yjkgH;nJUufUIc|6qJOe%yNl<J;qpdk>(;W53rM-_Bdy_jKdi^Ah)c+4!~|;=V5%Kd#>F_hsYTdbZz}vs%Bf+50@ZUc!%CFB#u|9^uEWmyGW}@6@;JCFA?gQ~bE~lJWiLHGbTB$@u<yKz+MjGQPjw(0Q=yCF|>Y20w1SWPE?UgdewFvc4HVZoOoDd;D?hCF9%qiCZrj-_C#Bddc|q{Kl=9j2~A&cD-bLTc7rMks8joF;V@iZ|mRsI==e0{;jXa@B60yt*`T=zO8@j>-?*4>)-l%etqB6zxB0#{CP0-ALmn_>f8FazSh6`w*KRMGrp~V>)YeE^>2MUKeqm@Z|C3EzxD0;we@fPxcV{mZ+%;zw*JGJ8#Z|Pe4AXI2X-Ed@!xvd{aoMX%ZT>%Ii7x9h2znFp!9n0`I2?xU@xCiW7fJv*O&VC`m(+rzxww2vcArb@0;t(`a1vW+w05vdVbZn*O&FReth3tU)I<9^yk4`UvWP5ufDy$tgqLX`u6&Y^Ue77`m(+~etUgc-_DP{zN~NO-(FwVx98VhU)GPSA9H<K-`1zSzS3XGxi(S#t8eSy`Z~V)w*IZJ$M5^5{;jX`qrR<w>+AfhZ|mRsdVYQ1)W7w$e*Aeb^&jU`pX%HCx4zcD`nLY#d^5hSf9u=hxAkv*J3qGmt#9Yw*1z@b`L*?L{kZxu^>2M!pK<S_a!!9Qy8gp0o5%QC=YhZKB=oaB=^Eo}ou_oVDWRW!_lQ_u>wI3WgnppX^cdf-|Hl7hB=SS;=EvmyI$!y7Mj}6}@UqxEbsp~gO-3T$e_y2YK%J*{IG&Nvzh`|+UhCX{Uu68yzZ+umTIY6r-#6oHo!jGA-yXkT=VpG?xAWuIznOpa?fm<7ZqBdz_WWv{+xk&Iu70R<Tc7@QVd_)sU+X+=TANi~-mI^D->k3Hx9cnQ?fNSH%(bhcudl3khGs_ldL5<I>ypsV3eJe}^*Rb{YLd{;TD&mU*X!tT-Gsh>zs1+<DEvm5gnsJmZ85%o9i1+m&<{McKi20u(t5CdO8U{*dEh!q-w;gfzy5WMuh)@(zcqfS{>d0$uOmCY@0;=UI<m*_Uti|<{p-lgkNS3g^g6QhufCms|2i_~SABba^*XZkqkdfda2?tD^sg^dpL%_1ou~eIX+?DX``;h&{rb=Maza1r%bhX4)_G{i)P%nNU6AkV^TiyGU;lTVjq$b4(>r%h=%)_2660%~r)+DT&<|D3do;$^`XAaXGm)=<_vOz6b)Gh;QD#EF<4rMnzy6Ok%uM8m3Z}&5wa)GMzHi3&>)#x|U;pO#wa)GQsBh;->)g)2U;k$Q{pX80zkdCj^Q(1k>&L$?Z2f5coBH(Y-_)npzt(y9ql>S{)c<=IV|=ai)Xv`|^mTsJ_v`<IJ(-F8z#C;^^VGSnE3BXT^vyAOt#e%`TR(kclbF0;|ICl|L!;Zo=C#gQC&&4pbdAYtorgEi%uMJn>lKsNI@fiD_0zldiOFl7+wpzhjPKXEIey<a$M4s_nIFIY&HQMc+xhpe3p4*(=l1-nZ_lq^|E7NY`nUB%o!k0U-`1yJ|I~Tfq|)i`xHo;`<*O|Wd-;sci#-3|BhGJf-t$BMoq5e`-@3~4)3!AA{6LFBo}ap_!^hr!r(8a*;die_UtjwBBlZ2~NSAU6{q$<BVtoHP+L}M1pY>VKSfA@C{nEdgiTtctqhs>^b7bF7nTh<A%`;>2{`xBamzjzDz}R`QdHwz#K9rfr&-!$6>^$iA^lx@&CiM3#kIDPr-z$HXnaB^Mu8hh1-_y<bzHi3&zrUN~_n$lF`2F>jnIC_BW#-3!j+puPzrUOL*XzihU;nvd&aZzRnfme9SGIoiIb!NleOsS;eQBMCOICIH+#|f}BJJ{h+q~=LhYuHe`Q&r%`dU!T^V8Eedw!t#{a!vie384pDwOs7l;i8YeBk#A?)u97_7yL8PZcj88kfx*Cp@LU=cg`g;QZQkJU^{W9p|T&b>r{PaO2l__GRz*3O(zNv(->{oY`_azkL&zZ_>o`v-1D3!1I^>?Hx~e-(TK1sh^(n{H&kay3c)cyt|*|-01m%^h$1=`5(Lc$t}}7Kjq{>_j5IF>5eDoqWPX*?u@(7R9WizS<k-c`Qb(_+&KAfcE>ZLgXf1j-{Sm}$K3cge?8A@uesOVm*!sU=BMor&re-D&+`M*TDkeje0ZLl-@)$qFS*YRy)|I2=hu7M`9&_d`Tz6Si{A0+`e9}NqtU+qex_EtgnrhQi7~#vepnYu=m%b#8|&+RY=8BHzJI;r`|E_oB@+6n|JxMf`}eU^`4ajmEqBHGx=xsrEwR7w^VoUNb@JNFnF;+xM`QB-Izg{@<A>^=h{^lwWHY|+oALd1f;oQQH^=Ya$ISfr>k2bJ{yM?TzklB|^Y7os%=z`dSDN$duOCeP`1d_qKl*;g)Te*nGxh1OAE@)tKNX+zKJUj5-S6RN6xiWizy0St>wWItAzM6Mc4@me&iO;nc<piDyWc0j)5^<-cP#e&wDHe)`Ls?|JU?}PRhNIaha0E*0dJhFZCOuwpZn(u&re@^m&@<H!}9~b4s`y7550W&+{Kw*eqmnE4_p}FJ~!jH>7HM2jmr<L?)hoEpKyM!nVuiY^SL)pO1YWSyyGac%#9NcxX<l)e5&XFQQY~TwDJ6`p7lLHt^GId_xz>4@Wu&rJvrISP0s1%Q^yo>pWAV<=ll1Q0TYf!`~LTlBK;Ejq0@6>eE)vJI@bDr{iv_sN3?#7pVH)m7~g*%HN9p+KYhf$7~j8d>?)nm_pe{|&G+s&f70pLdC>12qY5VU)4HFD@%?p?UcbgqFZOGU?|<(w<NNm$Grs-a9p{_l_wO5Ke*EtvW`6wlQD*-A`;3`?|NDqJzy9}ebAJ8%iK!p|eq!rKzmJ&u^uLdo`t<K7)Oq0febpL9*FX0e_3iW2`g*@o-#$;RulGaWH_ub+>(8sceV$rh@8{~<=c)DedExu!c^c>QJo4wkJWu0%o_Ffo=c)Cz-qg3x(>ULZZ=a`ezBzvTJhi@^ANxGDzMX&jJhi?(zxH`*{kZxu&r|E$`n1o}K(6`Sz43RpckABT!&sLV?cwR~m)yUPGH|x@k6d`ntG8(ndiksm3b}Rru6F%B&9UWOFF)yP_xxRV+Vj)y?e50^ZoeC6?FE-_aIbs+o%DlyPAwfZ!0TW0hx>O>{&wFZ0t?qUf9qWL@2^yQ#f>wy_dsv{YiIY?$*HB!x%Kv`*+ael6Ti6M$A0#@JDxAMdwy#8c{k4cZC(EOA(tPU!~Ooe*(xs|I&|YOuYdfjZXU{h?T%-~qr*MTGspeB1^c_>PhaBvJ4(8rtH21i9+>lw^OJt^^5HcPx##b!+eUbPonh|1`|lmydS=R4&rkcJ#QR>o<y!2<e`MuI&kt@}<Bk96YUg+S%=ulva=-6w+tPh*t6ZZz|H;3+eBf|<HxKvS=KN!qU4Ft}?&obZ*7F0SZ*aed|1a4)o>0Tt&ObM5wfDKfO!v8WtaN^}t?zjAx$Q^i7e4v8ryUA<$Dj6MXLmd~8jbe+BUL;<eD`-Q|K~yHPkrAV=fS})|6}Dbo<C`?=clHfbN=bOJwMd6rTacR`A7G?>5FYH|670WIJ0ukbK@WQ&GWPF>FvHhru?}r+7Gl?;T?b0u4OL2FKMioAO5@h_lmaWboo66JwI@EvNwKcb5Xah`>46|8z1w=36HMo&hL(gJU>0~oHtI&#`@kkq4n>1e%g@S?t5a1>)rgXIq3PJyB538P5H-t?zjeN?z+tD&0FfcJGV#sfo{jV^ObUACFhUn;PRLL@a8Q%zm6M!)BxvC{hzC!!w<Xp95LFB)25C$e(1j|&L1|z<vZr^{J_7(+|M;=h09+o?f#BnOu1Np;$d(6ln-*c`RQ}Q`FUr0^&gnuz|~=&EI0mdeO+DcAM1{@=U*;=XCZf86lvuA)Eg#x{{2h5c~09q(~Z-ug!2bJ<&6{gtCqWtx-@Wp(@$M~;`eTTIyH0tgd~?gJKi0Chc?c?=LeS`+1UB*dOE-6)9&|&XQsL9qV*KdPYKU<|K8I3t=;|P{?(qJHhz&ikL6Cd^Il`&B+=Aqt=;`_d_H%6E1dBBP_~}#y~OF=&M$Mx^HbJbboZ-GHQe~c?wIV=XRVy>eZt9~-Tkm|PtOl+UEuzmu(#*Ban4Pc;`LA2=$)5P!GYBIbmyD*rRv-FrPkN?QR>_GrPkN?UA}MLms(%nr>Sq>ms(%n*Qsycms(%n2l~EwUuu1Q-{{YSd0!gm^FC93`@Yor{(1o4zAugQ&G`0xsrBvg+xMl`xASA)ms;P>zkOe7eS3cG`%>%2)sJ~!YJFRu_I+vS%!}^lZGXMHzs>33?t4Eicjsl|L3jTQpK<>8Tb+NnhPzKDpLEyJH|L%I+hF%x$TP>?myVa3>gk#3o*&*^*xfgd*7W?)&d%QTo?2&syRMJ4@ch7itKIXIbxY{L<IZn<()nX5x%=DR=R7~_w}5+3IB1r;-ghr@`L3tj-;2G}+#UbNTix;ed)eLp3%7B{zvH;ecM7`a@`OK}zx7|2zgW`!9o${+xe!{{aGK{&`q(|McfIY#e|Na&2firdjgzu_p__;0Yn(s$Nq4{f$i3ePyj*;`r_FY|=jKGW9!MK^(fM8eaO<)AUUTD*DLTXR|IX)*XV(fh&f`^`pL>b-d<h-u#dGa;=igq{-M0(6bwz04<IcZw(XHRs-tX@7{ii#>R+?MCt#R*F((*s}wC7)Qz~%38>z}l|-JE}O2lsan+q2y9)P7)&cV5izPt~`-C-r^v`%v}m?>*JGzu#2f{vK0(`}<1YH@}w*JkjB`=;PPlzpHQm&cXN1-!rIh|87Bj`}Yaz+rL9l-~PQp`qsH`c-Oo6doABLf3Ky!{d+C-?cZyq{n>GCqVav-{yi9e+~0%Y$Bf@9=3i6oIp)T?1zHCJvgHgE4)pFG{ZFa3b}`k&|CDOKdjD7dlxpqz^=ke9{adQJ?hFP34I|rNbO<~cejFVQ-%YzAJe2kjcr-c&zK8bR@G#m#;W6k~STc?AM2Ew};IZfvQ9OdS=#x=AlD6nLSjKG1eoe^<H;0?TBWbsQo5Q1Mf1ex({Fv<WqRrWNSA=)dC;Bt|BP==57L2(UU$VkyXrCdY+>+1VPg}CWztTPfOHTB`pkv7#q)+rW_*YnRq7MZfe~vF%;q$c5lTm&+=-QGwf+zYXd>)pZXxpG;$sDFn^bhz?SaPCmf{qX2OIG-I+P{-gZXI;(1GFV8e2(_-u;fHr1szLfAAO={;j?6v9|*d(WcJ{R{sR9(M*04rYfI)cJkg)vpU5cR7j$jOe2ORf1N;LS<z_+G{+PC8g-_G|0hXL-lc3{|@Fgq!E$!2=<V5ccI+o0K`b1B{-@=j;Z4`7YnJ|5#S@20%a-yN2W669-pXgWcS7em$3c9vrw&01LfWLwzCwfQFv1B&UCwdG%0ZUHwwxHt;_>vXQq@77dxk1pig}<OJdP~r;?7NQaIx@=ZX^UpSU%;}zX#JpL$!w%g^eB9kjPk8P*Ots?JkjIuQCM=Kw+9_d<^%dfzl6Ueqb$z}X>X-1S>dl~e@#YNo)34D--ajp4g57MIZ=5&2uo%MeWIt}Q)HCoIU#M~?`Vt4{rw*9&yDefn{w~p$^J6-PWF}dC-6@Ad)mUgXp8;`FCaS){)Bd~$kqo>^c8pk{0X`X?nk>1{3`8N;9cl$STg<bL>Iw}$SCinEt!FMqKn~0@LqI3ESbT0qOZe?;r-}ASTaNLMBjklAfx;_ZOIJB6I~9!0e_Ajfh98xPjnf)96o{`hKJA|1}~+(l#KEr+L9TBC%Ob)LPq%j?E$n0!RfS@zz5KM@ME+Gz^~Cxhxeg-;J&mUgBQ|%4c>!(2KT1j7k-)cLijWEQ&=)R@kHmt^T{ZGOj|OK;)%|M=aNzWh;}ONN8vfN=fWSM+u^RXQ{maP=fK<1Fx-W9SNM6_v*9rMA>4^}7x-D)&%+<0TVTm_z!RMXKMQX`H^J>_cYvRw{S+DH4YY-4&=y?>%f4;sZ$qDQTiT*C;TiBcbUiGY_IRRC!%ve@-blM6?e_39w4a7IqMPB)v^&Dj(SDAM@&~jZq1_pNf%Xezl(*8BOgB8y7vUG+t?0HWeu=i|4tO5?61<akclPN9zeHQO2kjp0Bisw_0WY9^XJl*0ehujtE*05I<B8r4H-vkjy<o|d#S^^;zK4u*AKH>Bk0;s~ZcIkGAMJ{?%fn4+H-`J6{b9*e#uIH0H--D717XQj#S?7-H-`tJgW>A5tHLd5w}1zuLt)9(#1nlGZV3-Xhr^PofhYO^{2)9W9R^FL8lLF=@B{ELbO<b&DtMyz!S};M&_Qq|+Ew6YwC{rlp#xyaRKOE$0yl#PppU_lDTgO|FWdxv4DAa`rVO5FBe)S6<=(U<lY%E2f*ZlT(VnnmZo(723l70O(MMs)l)w|c1HKD>6itOCb0ePUZSWm%D%us6%nf*=4dC10u4osy2<;o-TWB|cyP%z5$rQ#Dtq0!%cS1YBk|~5IS_iHNcR<_0wct8%8``pO0sI2=DHo(IS{tqfw?W&&*U>Hr*QH$>Zi}{uC38KV=*@6lxINktmP}DR(fV+GGRmE47o%MizLj=;xHI|)d^>zA+>N&IowP-}!!l-Z^2Nz1m!w^ieUwYl7HtS$PICMFo8-78V;qg}aXis0@MTzXqNN!7OMJ-+C((ZemYis5_-lO03J2*Al2I;8TQc8}6TOCh*{&fcS{|0nDRQDY=$9=AInj!+WWFOOnv;Ina*`9R3`^#Fa-zBEmn}Cr(W<ayek3QFmwwsuk`t{COXg>CqWS5UEk8NYny_SkA}5-Ue%bPo6RiPD<_B`3dFYod4>{3l@M$uV70yM!Y`MsZR)N1IBU#~V>A#kYawXc5IY~}5JN>d{Cns6~&LSgO;cWEFmW`ZfIao4ZkrPd(U$$g&qGjL{WF#vbpkKBCInfkYGRMe?{s+q@oPyrOK9b2KCwd9~50;#$JST)D^96mP|G<}E$%)EyLRd0~=@b16{s)$vs5~EpC3A>A(F^beGRpFtkoE!Ek`?}g_61mSqVk+5LVh28qQAp`z>*V{=YjG$+M@D25SD%Su+JVc%6n;x{sy0eWq(n5J_t)@KYgO-;oo4%iOO?A_#nPyh5w{|9+sS_JST)d$Cs?|McRMDk`tBZgYw_BMdkjk{4Z@$xi=SM{3DEYgngAWXlJmm@KHDezD#>P`@9cl&|W}$9=wtEdN>0;3QOh{JkibYW-`jhX-no+Jkbx}56CEgNqZ6PSK+O+KY+hPzlJ5V7*BK?yp4?VH?$@5I-ckbcn2BfQ?w=X2A=3ncn5q6{SKDQay-#b;GOVy==ZQ>-oz8#1@9uG{3GqRXuk>XroEet^3Sv-vl37AGk7=rGx`%OnH6}VpTeJ#QT~CpWR~HHehhyK|A3x`C9@Py^dtCV_%!-0yoB~rcsuRwWRy?RPN%&D4$}^kQO=?*nb+_{KZL_@7Wx&ukoIfv7TR0LD4(GHGVO)%CfZxz6X-EmGV}37H^7_VV`wHUnYnnP>);J=Ci(>|nK^i(YvHwIln>LE%xpZ-|G{hF!{{McGSB0Qu7>{yA3_hnl6e+SbQQdcjPgF(!f(?S-2=<Mv*@2ipYk)bMc;wnhWDU*VaYs)C;Be@E*a(hv?cQbp6Gk<yYPPWU=**RE&4h9KD-7#LR-dsk^NqzU->24FR_pEJldk`;lYt@DEkd1C;U)kdl*l2I6M@737rSGrTs8GlJ-b4$_r>qrahkM<M2p$0s0ConT~j(W8lZ(SI}4C&a^wiPtbmXjPfGdl6eGAbR7Hyya-(kOQsv1=mdBiycm5QmP~g%(TVT`_;vIRSTa5EL?^=&;WyCbuw;7SiB5$l!^_b(VafEt6P*rEh2KQqf+f=%PjnhQ9exX42}`CYp6C>K8oUx+0ZZmlJkd$;6nF)?43<nPo@g3830{USg(cG!Pjoz-1}{aIz>?{LC;B8j9$tc`!;<NQCps2>5>7{7gFDdf1dpaYnvC*7+U;m}fJf0DMMn8$+LCF5CprQi1;32Whb7Y*PjnbO0-le~g(cGpPjm=844#Y5fhF?*p6DQW2s{U!4NK;JJkbI0Ab2+VJS>^}@I)Vj2f)vx&%%A-$KYACW#4A_&FB+u4mX4Q(eB5-%Foc2Oba~G{%}9|8T7d*9!OjCg(x0OTl7U(#%#%cEy*cANc%zdQGSTF=ukL!WXsEbdC3W%iF|eaHQ+qa{PfF~pIm;%dXUU-<U|Y7FIz!!q7TF8$w*fCI{L38quiFZWd0;4dOiKJT~AK5JuI1v<V1_oFI!P^q8;JC$w*eX82!b_D0ikUnSaTN7N=jf;^aghfhBX9oM=h<Wh+Tev>Pm$E968=(Jxyma-!W~$t2;4mWE5g-O(PfWP*62W#Q6r540C7nQQPw%fn^iUT7aU8|`c0a<t3CebC;pWRmej%fRK}-e^x)G66i%6u1oB6MYnx%zpvriQYuNY&Ve;O@$?MiJWK&`eiFYPP8j5nSaQM-blY}H<A<W0!!vEa-uiTFWU{|L_5J3$VgVW2>nIKD0iU!2N}r<7pA{38Rd4gCG$Hu(L(ggR*0Nv8(1>u$cYx9U$z3|L|em>IZIA7AN{iBBPZGlmdr2YMDx%uTOM+v55SW7iJWLI`en;SPV|0QGCz<Ly_SC2t|cdWUleDjE!qs0eNVH$X!fM5{5@^a9PF2aeU+Qj7S2gqv_%x>rY+hMmN9>1T+y6KSNUh!qPdf<@)_D^xUUQEituj6+ReVgZ$-9u@I?2*yWyYFGq7ad#S`5R?}g8xzrvDv4^Q+UydVA*{S972`#tz`+MknAK2KXR@8gLcfj@`OqkqDZS&t{00Uv??L@&Y{X|IQm(mqN?`ES~i*^DQ896k#Fjs6Qu<^w#@FX7|xzvyLHGF$OPzlOhrFQZpr$!x<D{RaLTzJkhg;tH7^c%rA^Z(zxZ%5y?kGCS!L{SH0_OHNdt55ki9h(6J8;qPF{iOO?ASTft`6Fmuk3rkK^o)f~73DYN<1)qc^Co0bg;Scd8EBqDhELd`)|G|>kLZ9df_$&B7^b#zYO?aZm;1lpA^dDF<8}LLk;bZVW=wI+U+8f|6Xn#RQ`2y{=wAaChX&)w|{0D8x{0~p`5PTT^1N|MA%xXN*1MngEck~=AnN@hA```ocIrJ<nnYZyo_rUw$v*<6dWLDydeg^M>e?fnOC9?ug^i%jV_$Ty-DE^qX=xJE?T}J;h`h-6r^D+EAZQ)(CMSp~slU)XXLR<Jv+HbOt@>{e;cf<EYw#Mw&n4EB=qys_vgY;>(DY>SM^(L8X=)Z<O%{C_|`VK6a9Q5a)PqQt^iM|U<CMW$l>C<dWa-#3SlF3bfZu*2DB-0XJLpv{CZur5d%tPcv--jiWpZ@&xY4%}qqU&MF6r{f(eZp<YJPdE7eH~swxNTIXJvq_Muw<^M|9bi~+mW2;2e4#{(qEK5&2}ayx)qj8G5U+qr`boyiEe`>Q=I<d^l7#mInf=kWJ=Osl0MCLCnvfSmP{%7OVOv<RC1yp!IHU&{+sC2Y*%uk+hNI+puYrtn(abPGz?4TM*450PqUrKiGB!6<_7w2pii?M$cb)&B~yg{BJ^pt9XZiWuw)9;Uzk44wjn3F0hUZ5`U}w~+?q@qcpdEmc!l8Bv|EvB4X>r053c~+Dk}2;Inn>YlF37V9{MzUKRMCWuw-)4pNl@t-bYS!6)c%+>A#jf%{C(^`Zg???DS`+PqR(PiLQhtla2mt^lA29a-u6>$t2UCOrLP0fV=N5Lzlz%(zgO#2Frg*cuDNjh%p1~7r+xf8wvdy*`7k5hG#^!nex2~Jp<1`pF+<@@fq4@7)yC3?U{_PJcITO#t@zod5}yE%D?B~bRs-HvQ3C=lhDcVcr*>262+5gPi8FT3A86LzVdk5;~7KvxyT$n71`>e_2Ah7*LN#gAD$E0p22&DeV)U=Gs$_Px54x2n~gpPi{CKGd7^j1iz3_INv>bCA-q`5b&~5By&GP{SaZ?Y@M8L2M(4tF$=r_K3Txk;=<V=A`Wm8l!mrVHH`)+>ozGr~z6^`sILUdU_rPz^_Zqqo7Qbnd^F$lNOXa#ra{Z!B;U!Y<Nv>bC3A~iCUPWJnm(ceL`YQY?nGkw6tbKQ(A$T5rcc6E{FVc4#dIy}&XU{`lfyHl><UG-P;RW=)h|Yt>4<$KIv=RJ*d{%^CLhpiQ6JCIZ;1}qdg+3p}3urIkGoNP@Zh+nf&!X=Zv;q7yeK(`Gz|-lgi{1=B%P~ET&Vt3iJ;`~Zcfd30n~pvWi+^j9^F(ilr$)B=Nv>b?R(OIOLz3$ktq)IStSRVpcmjPB(JAm0GPTjVu=dqNYs2H{tB%%$$Iw?5tqwoIXOBZC!s6FWa-QhT@JRZ`pyOciYbQBRv@ZOZd{%^qpfzFHgh!&a;m7D3jy@j6BWaK1GaqLYu8dZNhtpRPtqc#NuL4>T9z<U`v;y3hV;Y7IhsCd!<UG;paBunsp~GPDt0Xy3v>MzqvQ<iQ{i0RiN97ojT)$`~xF=%`KnKB(($^0i01qHj1}z6`UkX|V?oVH7GzA_=Us<#?+=I{VkM@JbubAXK(F$-c`Uax?Veu;`IZw1A+(*u7lIs_(3=fWMHIiJvXjQlmV+}<I!h`7>g${*>k|~dtg|)8|S{@!vUlp_x{3LzV&?@i<K6^Ae3KqXslJi7sz+>rq5*-bTUnj|VqP5`hk*!{m>ldv9k7u7W^htOUeUs5NIE_pVv>L2^wa^;yH2UhGwcw}dtB2NsXYkq6(8=&K^gV@6gT<FM&kVEyESvBo^cGk);qhoaxM*Zec1ixm68#IV6WO{(wpwUs_`gVh@reF|UJuK@7ujF*0^F6cI-|AVx<R*p?cmjMgo~29E-HT=8Tst%(SKlhQF0^4eq-?J&r>s^_4u56{0zd$k?nG_8{;y^DqMqc>IAQjqa2_eU~J(Uj9Vva{5p(Zf@3TZb=(0y_fpj73fE!mTIh9A^L&w?Q|D8-E}vC9>b%sBI<CKxua5Iq)X#Sz`Rcq~NWMBBdM;|i#c5w3<qPZaUP!)LC&D=*efjy>@&~W}oTVe$fw>T^3HPL3FUl8|aSE_+fvEE&W0qvxl2PZQ17p=h>%j#WD;bqBgxj%yji_;IMD<@pb>4NnuBgs?3EIV@{NjugU>vQJi_}0e86CfP)aPq0X&vZ1)eT;)AFbgU9E0YCZ;EU=`I&MCug+Ju$kvCSyAN|DoIA3WVV*=w!?N!c=KD(2dF{hkJ<)b>clPfPHBJYPr(4u9=)9NVvrD4|VEz0O!K>%J1pBmOp4tVkUY{M<rzWcBLw~+{QTclO4Dz!CqUs?K_4&zB<7l1qWPhzIt(p8BgVwoluE<u3`70H5J|2y1eVM1e%%gCg$d<$$Br(^*sqEh^Y8>TUv~w}`P2~HM(eb-6ep$vZ8#V8__`IA^pPQ3?ZsO;@DQezxlPM5Y4+Z!c`fwh!t~x{=SN^DRw3c!+_j=xQM9qiRl3vecXqS%iOGh1Vj^Ncg7rr*K7360s81-|Oi)`(ggZ7*c;U2X6M)`dirx5!ViaJj+W(wn`M4gZJjP)qm7cRtDdC(;IX7*2w8YeZXUw*zkQS+|j^+9#s%hE0r<(FZcT<oiLB3zd7%LK2EUnc7FwU)FFbe_5guhx&&a4N^3dEvs5tpf8@fuBvdS7htR+;rsU7p@%HZs7dfz<iY>(~Dd$vNz*bfOUM$bRyR&>U_wUc^Nlv)Oqd1XSYYSKFZNwHtM{WjryEYs9vAC&!ecG4?W(#QTe{i#kHIpt%qDuKX;y}akNf)u)o%o)=WW;LF-(&NMy?v*(#wG;UMRxeAGEAPbNq%h$oycvi+Ov#uLrP*ncOxc?>e2g`>vK%dzM@7i8bR*<UosXXfSHTpM-Xg|DG4Sv_~c75I!4RIkJA>?5CZ4O!t%)I|H>)%p=G#y<H_$>xjtS+0#5U$}Z?t4g*ipOu~Y>&P)^JquT3pJHfsSoW>V{#x_G10q|0vi-?bC)0^q(0Uergng=^)#3i+ss^vtc2z#7GV`l-E<7l*4P=ag>@VD#zDLjj@IdCVfAH$HCj3}r>qoX9IpHq!^+pH5{g|(T!K>G}u+(Tp_N&M~!sVIkeo=GYk4$-T<?)1zFjf`LaS^x}?JCSyG58VMRXDy!;4ZYQFkTlpEmAMjBHKiCI@~I<JsjCuqod%~@Z;!scw}UIBC<V%j({gJ<~VdJ{5bojq0``p*tZq>Fg%WZN1{)_(m$GG5giMUg2$s1VA=0U#ugm|%dt&iY|%;Zc=nx!PKHOY@5AV5cq;oofj$XOW8dlM6j;Vwg(vzREMvaKxT0^uGUjT=6@3Su%)V35|G}f#cP#ogJQkjSu7aOr%rWR&@D#?Jgsz6Ae<fp!u7IU~4P%JD3(K*sWem~x;Z`k@k_!i~{$r9G*8JDMK-<WAs;&E7o&G0(e;+x!y@rkG$G<LV_l*5#D5Lj$ATpN!k5aa3agF@WEsz}fUtaJmkl&OA{tpceCiM'

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
