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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_013.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_013.stl', 'source_sha256': 'd82e469f788d9ada007481fecd31d4a298ccbac7a53037b346d798ebbc68feea', 'input_faces': 1056, 'input_vertices': 598, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11488630622625351, -0.15198169648647308, 0.24832449853420258], [0.03437517583370209, 0.21835535764694214, 0.49999988079071045]]}
GEOMETRY_BASE85 = 'c$}r32T&B-yX_mq9Kf7V#|&b^fT*aWhzAp5JSKEdF$YxiprW=}K?TKtiZYlm=Nxbhm;>fSGJ6ygiaA{Ox0e44uimSAb+4zsTEAIrzTUl4@9t^pc(=}CQ%J+Vvf9c5;RV86HBChxt&ld>Z&bjbzJ8;t5BDEurP+zE{{7K#ug-0~yIE;twF#B``Hk*7s&WHEWw-vWm8%*m_a8ATV3hCh-Xli!^HY8c-=U-Ze*2>b`uh9*{_Ie<zH3!OZO5vHiH85-zg)koV5&Lj=&|3bcUrWk$!|4=I^9#6va_7{T8Vf2)n{$v+q+6F(_@c_f28D2^;z%HRLYw@R={6BR`OV)bBV9NcZEMbO7d9j;v|o`SUvdT!Zu6(DZQn<<)%S={XucbZz*3vd{g}shjCm7$**U<D0z$tGvRlLl03RoE7ad6P<(w{89A<Aa*~u!iR=sC?%fXg{k&=7Yeom;@i@CXV|jDMEb!YN-Y4}jR}o+L`fy16TCdhho)yz^+^Addi#zUCYD`VOD!*6n1pF}zaoj#JIPT`{@IUmG`Wwd;M|(Pq6<>c;T<T-IQRr?ae{xpTXVS4d;@576JS#s)eRRV}<hjrQ{;cx5<o7;(minZ4<b!{_<X$Q7&`R<c_U3@U_QNKrU*bLVd*YXa;u{`r7yoKg)IZB-@pY4FmwbM)9`(7r73DWJ+$-8S;F|QK{YsSgJdAdBI(l33?^ulT=3U#BTC595`ILnd;lI8m=cWDfkn=KH2g1L1VViv3{78;#syr5cMBkN?x56om!;zzKTtg!nSH>%4rMz)@UzE=sg8I9-pgu1>;IGTQS$^+rEvb)Tog4fdMWlT!u~X4LB}>8Yl_LGCKU;rG%I_!)e_EqGG9EU~K|6fSkNQN|p}hABIc|!7+5su=AGS8*crdkl2LENQt#Z6(Bhb#V58%IfwN~=Y?j`xP>Iv}2Uyydt=N^zehQK@U3w@V7+PQpEPu*<;{7<*G$Z<n*OMSGDt5_fNO3B}BG4hvO2|qI5Myb!tifD(@VeoG@7GK*HbW`fNZvy=NUw2BL0;?pC#cKfk%@#Rd%i#AnL`VC<AAAbqFzSWW$MC2({O1!Tzp>o}slO$6d-!(F3uOFMeT4CIwgLPN-$si6-RZjIajgr#)|FL~XL_I<*XUCleo`*XqnkHyUPY?FKiW#hr=}f4JNQ<DzvxJ~{C=5F$iKN9>ytJ~{2w9WoBI`qZ~YnLv%wPS7p=6N__}T4J{c!IC8WIm-3H~gBI~65nzz!PmZa4En5P3`B!B6hG9L8oN$|&n#b8|ZK)cnv0>8cEM#*pcQtGcqorB*r$}II5(I5TwVHNzx+1H4=+N1t+gW($wVm>xXkoHfxHB)?j^-Y=YmLkqlKIPkVls_B3M9Qytfp*?I0sh|NYvg>4L1^dUqu_6Qut3VYyWP*^x0r(Qd}biVbCx0SQ)kVRa?$?C?=T2{<weqNdi#c0AKDIp@6u(N)U!z+)H7Qz`1YQ2FweH2{d2X4ueEg*?UPsXr@Su>|I7txH@%Cmw1e@R4ccMTHd+6*b4`)Q`la-%_RwjeoL5|3IWP0E8}I}FT`m5-Ls)-uUWNbkK!p5$#BJ#pE&qP_)q2Q0GOq0_`AzG#!=Jw*TFULtiS>EoYWR&;L`oi)@>oAZg7=}n`pEdQ<cLE%%%6zzd;Xp)zkj>C95<!XAozZz<a~|Z4W*vO!@ls>L~N1z><&eq*iP`{V@Jqwv!zM9nF3qG-!xp>K_6j2J3RA%pR{eg=+^_7NA(@xNB1*J{;X;6dsTvOs)zd6uETmhtpfZH6&IoZ8_99aX{F&8+ca6uyYfoZ=gt>gpH_~Lelt$Hb3K#4w#EvnXUH9CPm})>_#dWAzZkO~L%$c?v^Qh_8asc(btioR{Gf?p(yvoJFkj{b!|z#J`o+?-4z9oZhKsMS^Tf|RpQAqahvKt$IjkplZb-YO{Obz8`3I?wb~6C`lUGjg&w7o|IDS%kRzm)7b}~LKC2g?Y4)`V4C+)}?nWx5<d$DeO{{&w<GgQjo8zy;74his!+wYKk!z!VjN8N!RkXM)Emb)tTG*rC;zr%W&*ZP1%Sofliz~A3$leGVyc9O?%>Ja=Jcjim}rA4tWt=`T&6IMuldYnQ1&uoQnJ6Nu(mcwJvzZcB#$7{Gg9-EDN7G4S8y1ksQe#jR4$>DzR_2u&=?<`l0^Hpx}C!rs;DU-3^3v!0<mWcCBK7@WLR7!k()d;NLTjyZin3W6VZNjCz#qScXzvchMdQqtv#!rb=SkI>|g|Dq^Ci#MgNO|*y#qc-$jpMpUVx3G|AimzSjf{88$Yod$ug*mIexdWE{Fq8;|6zXc4dX&E4ys{a;olW`Vj4<)E$?@s{)alD{M#-wM7vl?eYBNs@WUSW6FoUKLCVJzhQA<4)+>wmWz@$lAN(r*OQhc`Zo;_w@=5lo+L?!#@1Om|*Gqqd?_;}F@)$m$AGIX-2lmOlu*~s8J5)@7Up7wG6Mb(Dte^gOun#WkE&E(c-)iC;4&6X`|I4$boXbhvFFcHcU$f{$sdw>Mtk0cy!#51}6@9MD`5Ibvhp)Y<C*^W>K>4<9cV!%(x<ezJ*Vx9)AB=grrV7@>3k8{fLU(D0$HOGQ>4OdYwIioU`8*vk-&@|3_SL#x)usIT*BB>GC*XG+jrHyNUucK73*di<ko}Ue<N_&gnjQ?_c*sZmpl;~LMpNLM<44Q!UOdHmHG3j_JHG%q&!ty!eYrLcey9G}4`k_$b{^9h{(;CyX@|wlv487W8~egWF>-#!?}2Ea=yE8Z?~Ck1Ebo3{|6^AQew~!r@_T3MCQ5$2DExNuvQIPKUXFF|Qa1Pl@5}y2uXrBy+3|V@`YVf@<S!72>&Vv^@KaLIzr(6YJ80z-;Cpu*D4!kv!TBz{g>^7xp^PhI>Bng2X~8J}{Lw7=`RaO7&y;z6nWt@#l#j}V{YkP1{6V`gPVT?DnaTHGK2YlE`vL2!xg6_X!B)zL=ElCL%O~tpD-@FBYNecT+@vM&_ZUN^{PcCW?`S_A{>fL^*OdE&cCKK6|2<-<)N{HAt_uf?!S}WvCiVFkh56Fy(>9DBi|n`mtV^casqmv7;=1IQ7wg`{=kUAsl6o487n6FLZtZ}dtF^2T7SjXNe`F~9Au(7V%6~#0y@&Yv?DDv-`BcVu?(c%~9`3RZ7_0BVdKFq3et~_`eiql3xGp=V%KD<cC@cFJ%a1_Z$JM_EKX7TF_-8%ky!2_8#n+o2$9nQ30{Q!#MET|mr^wHpYfAeV%4~&yDh=b|Q!3_lrEvJJ+ZRioga69;YEv(7!TfqNSNx+VFiz&|5nqpch5O6HtI-Z&%Td0~LhNG=u~?U?j)PyoS@LUf4-+%_kGn`cjf;}-+~ED;%^0^ArM!N&2d)d{!*M^{zZULSR&GN3)as4$>m89l@+$gqOD*_sABBkOLott<I>Gn1!~Fd=3eSIb7lS{u3HsMLI4P5Fy-e;ywO3y-4zqrfeS>D}gZrlFqv-d@{_vMZ$hu+Nxe?=hd=K&Uh&Q;tZMlW|r&mY$3G+5c`3EN4|CTnu|1k~w?d2G6#$CnWNBE$9l49h1^%nWzd&XcL2yZWWOe3t}kJjY8^zC6duY*5jJ<>X5mHB8%D=zJ0jCc=!%yEpbHV)W_Y+DC^S9+L~_q0ZTT`Ld&Lq(Y{T8kizp9<MFvfZL2&*Bg{uI7}w0quNV#*Z<z8|qo>8vM&K=*L=N*cXK?hi_wEC*{`_O_uX56Au5#ecX4~*@5fV_G0jdo8`C`+sSfVbMl)Q@tbXz{hJ<J4)Y@RG5qhjWu38Xtts`lOx+{Co=^byDVKfGk1eJ%kGs@Ie`!cYyY+`Zbu;$=|Fl4Tu9Qcf2Z6Zn2_GqW^v{J*e(#!S$zLKC>;DjI`1Y|<e=WAB)Zega9qvy)Hpg?aR)z0m@`uliko+4Hr62VJBeDN*9D{w7_1xPTeeFqhw5O-N)L%Q(2>yE$)MhB^)58UyeWqd@HL({z<xO??yR&0okYx+T?bc%O+r(p?%buLs|FBEyX`FEl`@m0y;JZ6weBQ4k=WD8dZ5_sK9hrZYTESA!lrOX3N6f)~dqq*SLqHGsUDIX1ZG2M@=XI$({Ppq6C4Zj)jPs%f_`4i2ulXF<9C25EU%U7n_XTgmC6D2s%kV2Mka}vRUt%3=H5mJQeFxTak8>Cg?Y&XHygl~eYf52Xy`l~L<+(9_R=&f0ENp=9Ul7l`y640G=UPtqPsYnQ(G2hKyu#xXo{xOLj(UzmJ@o^R*JPSsk5bTI&kw`DQx@YbUliu)`gP*#6+$sSvsA@8|7jM=Z;Y1nGS;{)`OTh#;d@1*UO#8xet&rz`2D<aUR}<jAJ3PE-y$CMG=xYVOUZ2Tzf{F~o4g$NFL&Oo7XL>W?pH>)z&NaO4Sv#RTxY+fqF*|mguiZ*%zOP(b<}6&G4b_gb<hrL6D5!3bu|31VKQzlrUA%bG#q&vFUP*7=Y5>7Zz%jJ^KjkUmw@)%H4=VAZc)pF23R*L_J-fKKiX{p?x&14op4+SYdoh}`V#r;IHCN2`)Hq&BQVal{X~C%KZtR<Y!b%F=dbXqKF58`qR+@vHWmKVZaB`XO4z5>JRp8bxqy@M^CL%OTv_sMMfqX=;#-_PVZ5zgC%!q@6Xgr9!*$aXit?f5u^z@hKzn|eCBEK21nrjPI_BLR9p#%hkvzr^^`(7`*Mm^r@(R~Y%Xggb&XFj8)`b0M&=!pIZ^KYN>J8@mHS~+|ULTaVEr{#$^fnm(!+W57+~*UbpXVlK^tF*Ca9#GkiSruU6n^&nM=;L!BTpxnOzmv!`3>W(wiEn91JQ2Qr?HPZQy#~C7b(ZJv`CQSn)4e_{&qvG$NOBQAN2<LGv(30{YuE_TPC<6|KqKheEpOw@?Uh2JSidXW&RlI)<&MW9ys5@&&4-iJ9S*jyZYn$8-5q-?2h{Ia~#C=#rq`IwHGhZ&e@(~o<2Sdzx5M2u5r!M#7usc()iwN_A!jZ>IdMLb;Y=i+K+X9+#Vcvt=S@a^;=R#UmFsE@sO5^`I2`l{M~1dNqvG^pgu37#ZQ^BSn8vhA7fmdUt-SKK1Tm)$lp5@{u4Y0)qnkxJf>MX{PHfblE2st<i8q(<7R(>ecFX|^t=7IOzo*91YmvJF%spuZW!P0#`qc51Nm>(L-{R7QJ*&6;#<naNIPide~NER@kE|0r*XaT-hl7js(8TvY{LGxOm5^4XbQj8KG`oASL6Ffv$GTY3Y%qpww&mLc|D;r+qo9{>&yw9mz@EAzb2etzIcAv-5&n&ub7WV{zdz&Er#<-Pm+GoJX&HtUdoB`J<>7GC*8$;ldm<$o2Rt1_Fxv)hbgb4GPaK;_6X+1#$@r0b{nL9EOmcid^Wy=^6txVU3i%d_kAgm*e5;QhW$0aS2YJLrvDkwU+euqzn}g`e8b`g7(XlCp?zKtMETVHxQ<s|fOekdE55n&B#f)x$FYAX)*bcP{7~9K|JxJe-`E;?M*PJ3JT?XGJjf0H>y4PdgYP9|^bOzZ!he4d>+_E~C|_<5{3pY3U$d|p%2&ID`mAuy<m>kKIPS|zXrDu+(Vpi^OFQe!Vv{oZ7MoCMXXDRb7|)MvalQ@iqF-tqO~~kL*E&i+8newrKL+N&ai5Qs^2TTLu;0#O1^;1Id~ZAv>xrRm+A7H#H6HaZaUe0HuSdT^eO8^4<C=XQiEqAF1?6qBC1vz2K{Zg%9VgK*Y4^p~R_(%ldG(dJj+D5B{I}|3{HIzl9=6AcZ|Zv<^YmHUq>R3{a~$%wIf4A{vG6_Paoq_zjd{J;EWYvMRE*pHXHb8~WjL<mMj0o@%NQqy4#CLNdm!dZ>>IgW8*KwnzRSo={bH%-hw}Tz<9Slf-q`2(c7cC?FvoL#?CW;9qJ4^9Mtv$>#X57}5x$)R&iADm^J_#o9M_=)@^rnQkkL2J%z-@T&tg186vT0#y5l-~COwmHsA<HwEftcO(bs*CVgJMHyRm8>w7=<Z^lwkE#Eib4cRI$~fw5R;{!PdJctA1S*LY(c(<Z$Z-@<nLQ_nxXKBO3q%XQ4OJ{kUzYv|vf*Ag=N#xi?wooae6ldnzIu+RK83gfon9UOP-X|!j#(n%S8t#2^q-KUEQnac0LxY7blnab;5({Wv>aUScym3Z+@maJ%>`!^CZ`dSSm^4nj)IyUzZ^2|Grbt$A4)+NJk`1bqo{G^5to_i!lBF~R1n5Ug?Vn4QgCj6xju^v|c8|~cHAO4MwxGsmpVSl3gBL4*w-mh7@8RZAK!B4iscn(KB|KnS4M*n*ELBI5PB+q9x{~~DrXdBf3<~}^Py;YU(eH6lTutD3!x44f&{*E^>9~YWYe&r$fsn-)S`dUDY^rPjej(K-@0sK)FQ6HBb=&yFckr~I8acg`gU+X;;&#^WP#yovA75<=_=*Qug5;FNS`(YhOJd@e?ZG-1{E=SQ0ffG>wuqD{H+}wltk|zM==hVb=^{!`8{+tiWKbe8{zpxnXmga@}KRSu_^jnma(bsF(Vw{|>i|e~q68U>P#yqNp=L!Gu&$ht(B)pF^EiTCC>E-d>*4D6uO#b?Zc<<?SXS9EnJmMR(g<{@$xM81g)CT3p1z|j=7R=-uH+F=d?F-ufS-L#OG4A++^D5W@=Vkj0evf`AfAk3E%f<K=8S@)wOwQzM>8J2KGd2|WP3gzs$3|nE>zu#z_2TwehfmsKzRWoU|0mW}{T;4Tdg<Np8|A@#x4cQn=xgtWp#8IE!}_*sGyIlyFb>D;M)|6f;dhF}dlbB1FirA>zn1R{eJ_CVe8nBU&r@9QE)PV1&8-Ii&vWD8tjOQ8DEyL%IA5-Ze|+6B6y-<G!}Tl47Uka#!Ty>17IQW$l#frrdCiZ*yg2znp1)`x_hTIn?}hI%^&9X*%H#Xtzc1su);Jdaa4&fdY5bB0*RKKF@f>Ga5xhV6b74Xze|$gW?>#>`lYekLz87uN4&yx3jQr&)V_xr`hJ8_+V3hYMigCr~X<DuTl<#{C`}6pG7$;|Z;Qtx_*0nM3-gt>`^zVXoAV+<y^TmwF|7aTK*N9gbhg)3XcW4aX{w4aisWbff+fdJ>0g0J>k3E=QvpQrdulc3p`7OWiP8n1Ve*I;rPt2yoO#bK)tgA!k;d_&X1(DzFGM+bn>Xw|z|F8+qVS-Z8UzPKSZ}AOA{hf*?X7sf!?>1%ZFY{p=<VjeG^UBvGF_Zt7AN)}o_5;z$^4^SIcrfM#_u-~q=iqzjc>b`WAHIj$u^Il5N%;OZco+KDeJ%WXYw&$jcvp;v#WUf5vBPtrKi^Z^br)Z&I|k!zT53{8Uym&$zH#t!tPhvm>CeLTw2}?3%O*GYqkrQ2@%(<c&$6+CfA%!?Gj`bTnUBA~^W20ocn`FHA+&$zNARaTMtz(&q5Py9;%h}`V&7|uM*n_}fxjB>$ykhzSkLF0;a?br`?3mGG0w9GApgCC@RufK@->6I`1;J=7|*ACP`<-^w5K(myBeqbh4OLPu@0oZPsr%&ADUymUAEwUCcoxoeBbc{`Av<TktZ-W&Nl?lqyG4M-hZThjD0$xp4S~wKGy=&e{pWC!{184=kr*-Y<|q&u!6`FJwozW{4e3W9;D0n0ov!Q$W!Mi#^I`D@%1&|(GEk#qn&Hrfq(WZ#^=Q1nAc6$BG2wZSl|4&qQ7oN!Y`4C@+;b-d^>;mLyF<P^<WV0>!Uj$f79a_58WpuW%RY+Mp&QE<v{z?Z4KWG-$(0x>mYwGH~98nWSkh&4q_jbRtNd>4@P?~>6MVt*NVC0x!;dtIPUh+@K0oyez62${nwt|m+yh}2L-SX>4N7}<_S0O{m{Ak_@4cRhIwQYfbv&5N_oqWdsqh|hQg2gisy2F_Fcz)=$kO!9E;+;i_Tr(SDK1;_VL2_dEtfQe!+V;`rHW2yBJrLcNvKG%s&e4*3cRL(M71w6h1%vTmpXoT?aCb|3AJ~ArkH5wHWm&n+N49q~p1ek1xh~s~`A&>)b2k_r`rwN>Vz$&%1pP?e?l8`fJo{ly|!i|4K=$tC7hlzu-IOOE+AP^i%Qhe`dk+tADR!J?wT4KA&&=XCMCRIP$+v!uoGl0P8~=fA~(;cz(|7?;l@}P2u|{;g}b-TciA#cle&&=QZw+ydUBFFwS>NzGIj#kME1G2mZwM<-i=Y|M`6=|0N9P)dtV6486C*j|js0*`fx%Ut2sBe*9_VzvYYiRPjT8@6p&l7g&h)?9c_}YmPyAu7}zsN0jG2{LlO~ek=k1?S4F0Y37JLrSl+9&gqzUf1ca?@f#h-{(S8wTu*n~Adh(j%0ExR{5l>VF69S@;QgSh_}<6z;&?dvF%0cltrfl>iP?<u9o}PoXpi?#Oi2Ubx7W~*_1)2KqkZ9r&B1f*ONTK&vv-Gou|BRl+~1mB)q(%lJnZvtOp)^1)M}{D)K=JE1;-&z;YuhUJ0A1#$txVU?W2WK&S@&<#mmu|{dOAW5!dsSRdMiLkK_5?s_AH->1Oe@sprv;yFa2m!-v9ea2)UX)UAnjyM4`7>RZ3)Ss5SIipbv`7`AO~ApVhf@eOx0@r|W}d&qI-)ITGipH&s#{Aj$d_>F_li9g{<y!d&)43IpNhn<(7yPp+5WkM@?KS_HMa9YaOb(1_=DaSx5x6<Q+d^WE^`EF0giN7Q+PRjRci+Y-e$$NF$&2-e~+y^PI2L{3K*HC=@OK#Nv=LWoomv^_Em&NM=${$@gRdi;3$*=o$M17p~Y4W-EY^kSqwFLf7WZxF}`QJ-Djb2kEkIB$<x|9nWD(zsNcS?L?%VRUeceyS3wO-YbCvT{{53NTzNj(iel2HC^R(Zcoe^pu9&60aF>bYqc-g_&05$EN267AeA1mzt<q@McgG}PzgpgHn+%XB$kUE3wTmfT$4Bh(iakUS=@X!!H{z#nfuC2H)9b}RE-eC@<ODX-bgK>o{F<^5y*bOQRNs14d}T_L=eJa?$n$6R8+l($rAit_${N%@q5&gjP>k5RrxV`(?bnk6{j6ZPf&PTi{eS<I^;sOQ8T;%kYQ(Vnd@qx{>Ip`yMwrQK2v&c^szGfv(I)m>Xjd2@0$j9Z_#cu#cn4LPo<+jz8p-Crm_`jE7Pwy+-R8CV$a#ikiCPKMr%&*b<2hI+=dgx`57-k+Y*Lh@K9c%XeEw&MNrN*Ba8zb*hjI$ZufL612F-v;x@lxKzb+O4UW7X$m_e7B^+pAn9EH=-)exBB`;;@=o3d5jwz(T^=JEJ8c<llCz->5TSFAG26AehkXz!F(}QYKy-Ii1>UmQ#<_V0Y7pG#>q^KTRqE_rQ&NCxB7r=Xa}t)-jB~$9PPQq9_L%>9{iGd<h)E(T~PnX2Fv8<bE+bLxgW^?_fGgLoZv6G4ZlJ0<rr_tsHa_N)c<OJd2d^5_(Ocli(eRrFJ0h!?!Y)HcJ7Ltx6?iN1@fT3xIP%G-;=*T(GQ%IJcebckICUfl=x4cA^*UqIN$1J@OK)czQTWc5qUoQ%6tF%x4YsS&)q=zIt$@D{1o5pbsXmvwG4kJFd{q7_xQH>Cf=F;n(_IPv=dsb-}pOnYK64^z8U_MQGTFl|Iz>ZpE3@r^Z)gyjLtRdy8Q3{mN8d;tKU`r9k$d`WTghOE!mD*o@_@h#86zETA5s&T$);qth740G`SqL7P%a`0z+{{Y8`S#autT+x>O^%F1aZ~u{X6H*_-UkP~4B&k=&2$$51?m+JiiXJevA9S!rkTX!1YQHspWEgBXg3P}`D+ko!_S$Vyw0`;rGz{~`}0_h%^fr?w{hlLM&j$x3^Y1IU5YuH-=SScc+})Gp+a<l)p_WTgYh!^xAW6Umdw!3@RG)S2XH@>Xg%S?MD3R`LPrI`RSXIfmlH)D`5z<XzOMWTg$syU63IMabjHE)2ys)Gr#?hWtu{J|ru>OnybaNj*TmNj}O@yq>y-yq+9N4JIocO%5fGqjn~bBbykC-Kh=9?&J#8;$)@y$Vv;5m6jw|AlIOlCD$O=V<>Jybs#q(H>Fl3E3Hj#N^V81LvBTG%~0HiTA$p8>`8ScE3HfRBsZtlBsV7;8H(Mg)yZz;TGT3JrRB-B$WBxP*@;|{p|}jS1i1{k7_~52X#sLEa(-$aa(;4dhT`nhoaF4}EL0n^QY*4jjjaAzle3VsQL~b>k#jH<7o_GT7bH7UOOuthAUl%VQ3sIQk%u!B&!bKw&m*s;t|TknNnT4nOg&9LOuoWUoJhS*P9(phrjnJuC%+?qr&?QqzmxMa6c?uEA{QoCq8249ElF1DKz5@xpgNEnkeg6zl9g5^Hz7BoRv{~`OKwE=q&6ih^(K3gdsBVMy~*Pkil<Qfk*AQSQT@nD$B?IyL#d<5q2vgL;#Jgt$g9Z9sDsE#hme<%ms9(amy;JW6fdC;BrhQ^rS>N)^(QYSM^OXFQRD>-#nY*Q<mu#D)UjlxBgwPKbEw0~N+*-&kRz$VWTnyMNb&~iR`Le&S%%^})C1%@<VVzVWTl76kH|NvyT~`m_ZW&dQOA=vkq1*<$VzR<gUJP`>bhHipA~;#C{Cc>BqxwhP>+(8t|y-$Z>ENlH<K4J6i=d#BTpjtr<%x0-O2sQUepR?r8UT2<POw&WTj2W9mrj&P03x!Js666Qd^OGl6z5Gla;n1_agVEdXjsSyD=1Zp*AOXA-AU*$x7YG?a6Jawa9JB%@~RsQ=Q0-$<EY@WTj=u&g9C}V&ux?QVhjKsrku8$+pzoWTn~3w&YyYEM%qG$hpXN)Es1`1<7_~d#WSZp4@<;xI48SxjQ+KI-IO@9yyS_fV!5vfV`2R_!#vt`55^I^$J;OBKZdS3H2TM3HdWaaW*UHcd`n__EdGfRIIcx*`8d3T8aGUx>$puxH&^{Cx+tg)CT14<POv(WTlPBN<GO+dy_kmhf>Fphmv)M;xOtIav0f6okms~N;Z=>QX|M4$vYT|_fS`n_mKBemywk&C+{U6qAn&MBJXD?wosRlE#z40QnJ!0axD2cbpiP}c^^aZPU>{>PV#!{EV9x$WTla0r5niW$tS31$tTFS8H%4$?~tF8zfm8NmEI(OBfqEKBflrVVkkaO-9$c5o=Y7}R$72Om+VAU*Dxo3R{V{jIGLJ2P9~qFo**mTOg>BAPF+OaPF}`PJcT-mJcT@%+Mle{i>$N*S!q}DVDd0(5ArawKSOZ<wI?}%Jc`<jth6_I6nP}I8+jyoC`0ieY8Ub#azAQ&veLHXe&jyXX5>EPzZr_Xsg23r<d#%tveL@rmgGj%QshSDY7E8Ys71-;$VI5OWTm;tO6|x>?a4*Rm8cEKmB@cF6!)ceC-)^!qz00eE+9`NFQINEFCp(>C_YI&Mm|ZtOT9r>`h<L!{F?fi{F?lWp}3$GR9$ZhG88*g?a4}Okd-zkx1^4sHYblDPoQ=pEA396K%PYHKvp`GJc&G?s*{z5k>``wQqAPG<lPL#XQ&&=XULbRJIG4+kS~$1QTLLsk?%4TCr}TO6Ud3w{bZ#Uaw0i}8cR+gCovS?pdKgRAYY~KBP-oWzDka#t|u!!L5?Rsr`{$jeM){#eoOsEeoM}3jZmDE`kt&pu{HG-S?PJQ3dIlT%_Tn|Z)PZNMs*@LBU@3`^}vdnOje=zF}<_o$K>-2#k;B7$-BubsLRMor;t~Wr&9-$l@23MC(ok#la&ULXOZVnN0H}{XEGGeppGQZAWx+ZB`Y07o=Og)_9F+8$1@a<rS>6@B@dzgO;+kn9zyn`wj}$JeHe;6QX7#wl0B%^$V$tRJ;*N9B4nkN$S&kg)W66|`;t46M^Gn{N04VT6h~8+kfX_ms5{6?Pm&LjFH!H3FOeTG6sJ>Plhet$t)RciO4S;jo1wTi)tUTfU9Qbg+=8Ka7(?+q>Im{YatL(-S?MIQ()nbiYsn$x80v0v4EYE{@kQzx@<sA}>Ls$$YvlXnht#{|hva`5ieFL_$S=w7sEK5yDdczLkJKdcNAf3z;&kc_aymJcdX=m+o~-maS?ODHDp@^DR;t!ejiERnLvaCWPI3Wq9;!82saiMl@U!AKR?yAlH{_!X#a`5AWG`}7sufwOS~s)uv*PC(^gQ`F`65H{Ug~c0Uh*pH3bNAaWTmsnO6QPQk)x<H$x-A;hT`Sa8RX^U#nh=}r9tGy<Z$YEayWTDL-AbdSn^!5P8~v4>PObe6R1Aq3FI*h#RI7w$pgv0R1dOJ7qZe$WThj>zT|(Xv&sLE!x)NVsL|vYaxC=_S?MKmEcrV10r@)lB}4H~YC8ERxtJAHt#OK#)+Q@$L9Ry)qP8Fhkrz^jk(JIPFC=fHhLDxUkhhWJs7J_3FOuWP*Qxi(*U8TqiqohM$!X;8)PKoJUy{F*e^K9&f046TBNS(&ek7|<oQwL2tTdghLU9giDmj&FQVxdVLezZZd|ZPHF%%c2<{=j)=VvJX!nH}QL0=e(Pg9SQk8%w<%~0Hjnw8v#oRgvWUk$3(pnn;PuTn3PmF^{9CGVrIA}fs|?<4P_Mv|2-C+{KeqAn)yB5z?R-b4*2Zz8Xw&L=CKOI}AdQ+2YLyp*AMA$0<IAvuIPhOBfTIfOi!>PuGo4|y^<f*M9v8bgjCZ==SNw~<dV6yK*_C*LQhQD2gk{v@Z7^H@RE{LhnNUC6^wT!x|8hoN{SHHf^Dyq&s`ypU_bc4{0sj`MswL-7UbGx7y;GDGoeY8v@9`6u-|`8((NPljR}Yp9y@HVnmi8Hx*1vylsu3sZBEb8&7LrWPU>;=C=)P+W|fpInS=%TWB;3aaMwXNKaF)YIhCoVO<#in~#BlDm<!GZa75plUupV<^5ry-L2yxq5-RhrEaL@B%~eIqDYjIr15X;^Wj!<m2Qc)OF-_oQFpkiVsqkk`I!%G8Av1E+lUtucn5OLpb+VQzOU`oL8$EiuY4bk@u718HyiK?~@;qzf#l4X`E+Ysb$D26gOrlo=x>3`*2>(W+*;I-A>-ld2))O_!c#poXmN0i=p@h^(XlS`3FOBc5A4bC)pW_?WlRlc{xw)7>bKf3zG|T+!tXe&P}x?+j1V{=4ZtpI2TTmKadYH6uVQqk=@BzsM*QcIS;b%v*M?m3m3>2IF6q(6sJ(nkk4=&r!W-XqaGpOBi~{uzD7MrzDACtZY6K!IF4f|woq4-S94ri7>e&u<H_+Hmv<P7-%!7j-;i@~T&l6CxCC_+wJ~`Vc?)$mc{a!27V0hXEsm`%48@nJKggHKj~R-;Qq`FI%Fl|eI1cT|b{tPu)ZApHYOGlCv*ITlKL^QA$ZHsiU8(M5SMm=HnuV-XjgKE3Cn@9<_Wcir;!o6D<WJ<c48<>~*T^r(Nz^!U9Q!+odWU?6eVN2i{E@2q@1yqL{rZtVQ(T|kC~|%BYU&p97WUI>hT>z?$K=QCr(+DoSE#BFu27%QzrsG4L0v;$!*-v+Q0z!mZR$w<L{_0VAN4KyE!$DC3dI^ViJZi?(AX~O{56JR6LmFtHP6jNy+Xdix|*ntWJexbalPN?UgdYVGZfcnD6T`TOs+$&MlDZPT9#am>_ja`b|O166j!BIBv&OnQys`kYm=SHuG9u(S8`*9;^x$5<mTj7R8O+fw&YgicGULdcH|BW#hn?7J24b@WGMD#C~iY-OKwB<pn8%$Sw9bk;zra4<VNHg48;|wwaFF82C4(uf$eKxC@xJcM=nh+$xvLJT9#a#T!LDjth6$@1lgWig=|kQ#ZX*^T8~_YT#2FB$WYvp>P~J+_F^dhi&~%j7r7}zu^Y7x*^OM6T8*sKiCmXllj=yWNv_UNT#H(jT#M{NbtWryCA*LtQX7*SlAACTx1csBw;;EswjwKSNA_-QWnC!C|LcE+_22*0_j6jN|1sA8`J0*l>?GrFUjCiyKYxVc-8!p!KS;Cw{h#_mBd2<Tru`SX%2MS'

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
