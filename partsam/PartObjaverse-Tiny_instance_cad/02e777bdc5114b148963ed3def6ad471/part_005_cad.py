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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/02e777bdc5114b148963ed3def6ad471/part_005.stl', 'relative_path': '02e777bdc5114b148963ed3def6ad471/part_005.stl', 'source_sha256': 'aea86a91b7909cbfd942c3bc64b5bee7a68f5dc7d7435f7e7d14e7de24f341f8', 'input_faces': 720, 'input_vertices': 614, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18342536687850952, -0.4050856828689575, -0.19834329187870026], [0.19814889132976532, -0.09736377000808716, 0.1973378211259842]]}
GEOMETRY_BASE85 = 'c$}r22XNO$*Y5Q<y_z0s5TTgfdlkKd31A4tmci5z0vHG#(R+*OkRWVBLNU#N0UKMc*rE5(5(Nk))P(i|F?`-VkHqdb@141GFEcyO&nN5E(dz7KwR;@j&Y3b7Qs`e9#lM99eZIzu!b)zXkTP+|xbY(f4+*Y5ddy^xl8@WjKSx8l_3rBXl}DMVO!WyG5<GaEPh-`m>ClEgRaKv%-;NtUE^u_fx8s6_FnhbeQNcqp?7_nW#|+8%xnliVb*rj%DpggdtN)Mxa%Q+-Or3HfE<?51+fOpJ%beKNg8i(IBzw0cvY(FRc4P706tTW~b<_cFZ)T>5_4Stl+-@(Q!0pNx$FFdE`oo_5_v-pfcB5**O5RQdKgq6qbMt%NZU=A4ZdH0@vij=#kI7Q~zGXvs`_~?EyYcw(HEzE<n_t)La#^<5e7=JF+5EI**Cq_7>o(q<EcH*Ow8N~v9{oeIc)#X@BiycSSS0ylhfdzX>`M9q`MNg^?!Ucvl4Q5fAKJ?AFL$uij<tTzPJW&FS>$#y|Nb-Yhj&ktM7z;FC$Dd<I-4Z*bH4lgxSxr^Nz!wy_vje!{{lmk#QU<QU*mRdYXI3-uDr-~*4Kylea-JKT~`a3!P~b#{*fqN*SzrOLEdlaVcc#!e0q*wcj&dFy!~~<62*3`)kArGWnZI2@w)2mZoIy-GJB%vzxDQ1EcZX+eS+w}n&Sw!E8P+kB!9LaIKusmS;Fnc^M8-<cEU4J{TIGe|MFvQ*F9m!ncXT!cK3d@61*L?WBUa0zO;Ma^ZH7YyYW)L<$V>y+qpL(UW$_)8n^2|jgA-ZONpu(&)W|i950Q>G3B{kJDD?H@~7wOXx<OS(=GA7%oNMw?e|Hs#QRdrCERXKJ#LBqE3ap9yU}s5CHk-EmAG9AeIF-{yX;Hic>8LvI4Q33pHJZRYqp4!#>>A++-`i)AWn*ZD~<QR8nPf(^xyc|kJndwmX8(vH-0NY?KdnOEBbHLEkN!2j6W{<pSX|ro8l82BlUmN)?|O5J4W=!JbsP(Ep&RccwgqBR!Q96ZDh1~U&_UL+^#fFJ0|*XhsGxI=WYid6aCjN%p`l@kYm!g=r@7e)ooXgO8)Q2&FxC9hDSyJwf1Z2eqU`mBKof%E645H?Z7C}f35MHWFG%1J)%VawdnEOuK%8TSn|K~Ykpr=ka1Y@e|#jjtFwa-Oa52?ncK}n?+%Ino4FcMzl{t&B>Jy6jN$iX_jz_u^k4b071<N=M2h~~Y0FZ0KiEp7=)W~>2De+sR~-=j*GInN_hpv%J0SY6_B%-Ssa+0;{#$K-=5}k#gZ-ladbhe%zu46MqW@No{rtY{8s7Uw|J75q$bO@6gcLt(15a@O7kWiV{Xew_w;QMX?3VgJB$eNnzA1f|)c?f{Zr6+_yCnZJkEi;@{B}wHqaUnw^geONZ|PueH@eY#!;PQZ&*=G<NC^}DH#WTEep(HWhKc^`GybCcYS}hS^k4D!r~0|Ghl&0xlM9l4(1%dbe|>FMZr8f43l;s>RxRfDW&6>4-tk{;@saN99KAo?{!f@h_WVm%Oa5Qzo67sA#>~}H|3`J;b~PpQYSDkA>M^>nlfQ&W{Xcm$x7+uRhlu_=&({j{4Uzi))g6k@k+iOH<ENn?#d9#NJKXtj_9^ba()3Ah$<MxDr%HC*mmWNo{4Y|vx9E?yY4!=p?u?6%Hzd1rU-tAB)c?<Ydx`$rRWj54UZHiI+y7f9aQ}_tw9azl=g}kT|A`fQw-BzYJ-NZxmyX@JuJ!c_T6fM_!R^{bmBvf0fK<_L%zFL{zy8(sl3i26x!ovQTe4eqs&Knque@A;*UYs4X1D%{;y>%1YRUG-&$)kQ<94z?CEIhmx;ap`2dI3WwuY7Cc60M<x~}uQ0;fuLWBNRr$IRK1-I^3c_3ImQJL6kp-9BEfzwkU?FPj%;$@TLtqILS!Q2Dxv1GwE78!y`@tmErVyWa)bzI+6?t4g$NZ>v&$@9nbvuL!<Q)T?cf{cM)&zuL9HE_{8bZwr&#IlPpwv&=O|WcxP{XnpkNqGVT27oqoRyA;{peg}Up_PR~nt{fidN6)<!?+0tnUy@yU`Y+vY;@^^8D{+JFx59JT-r*>>TYLVL+nG3?`)R*_DPK3CBCX?;B59I6^bKEsS;One_Cbwl9rs5I$*xr`PV2S#6(zgT<1$}onQ!w;c4Yyr%d9DxWV`POzMe9#rpx{}9KqL9*0v9l-Iy2<^WW@Bt5JM?WYqnST;G4kF|mJ)ge0mTvY+lNVqltNw^new>N{AnTYbiGyZ)KZ?P@*xo^!v0R$k)sk6MGiFWvQ0JAZm_woT!7cYgDF%<bkxbro;Nc^{1%N%P)U)wtcAujWsrdGd}<^_}-!;{>vgJj3no_ee+&nzwIUBD=F5+Y`v`R)qoIi_hJ>Up$TbGv!-uH-=oKb$Y%!+^!9n_Py9|=D=3mZahm05&cw$ji&i&K$g{_pL+3QG!Lh?<#uPDR0n5D746PE`M>SX{AQ<kxLs}1h1zlE&mDQW+Pl7_b}&DiZSzt66#>)^=5uErcI@tayP+(#({nPl<GdGEHkItoJglX)pm=LApXxjFq|t-?|7q!JssF9MG(Qv#p>~{k_+x-%cjjSj%|O}i%(r+?8KbsSJI=hfbfRQ;<~=obf@F8+rPq__J#uR|`H6X39X?aGJM&~_n&++Vk#t>W9v(f1>esT!?#$Z(>t(w$ufAME_Z5~xcDxsKuOI1o7CKFSVqSITXKmg^s*m@D^=J>Z^X3}ao%z{sKRw@T_sD<DlSYdK$?nV#j@{_|1aU?4vr*`TWOwJ`d8f(Gm>1+H=56hZv$7rYu(kBOY{z`1C0`<cs=XsS=0junb=i*j(5!z$vODvkV>h-aYj}Okw`MMz>d(r<?autKulh%_JM*@&_$kHnWtH2VdEV}jnU71oy$`j6dBdoJdA?Fzvg3VWjV;OT)|0N}k27z4+eo%!zO@RpknGNUt6pzH*S$siSnmFV_d=R)tI+<OyYJM`o7T6JdT-_aJKux5H`082`vAAQ>*txD@%htS8pG}GJhr+leIG4+P4%7iB-Y_(-k?z4zO&CT>^-g9{~i-6j(25FE}DlYybqQ7ZB9IW7xc*<CSKPXT9D5xN?KlScjw_L*QuT0qG3{ho_NUZ#?rQ7qMuf0f8LI<U?$lyf2x(Y(L6jPB~0{FU+|9G^{c0-KISE7zSXMObY09F=CfinA8x)!?KtyBjWSffQhJy;uGRO=Y2MhFDO?=a>bcfrZ<8ln9M^i0?i9}frNYJWtBo8a*`4w0*zI*{xHx{b7Q-mc&zB7s$FF{S6t$DXCtMuA){N2APRq*S;y88Iy+&lsaB<u@>uMugn{aV_*-utcI}d%s#c|}!V^&DNa4{Z~h5N|fEGS$YN6xxe|7tw>Q?VD-?{$XyIn#`AF&>l;S0%eMj-2_#YBDQa9Czy0TjYNh+TV4*2iIre<4X(2zOu8QxoZ)PyC<b~isMTODM0%GJ9q6A$Cn<kgxl5R=$+E|YPFue<K}zs664m0v8kQ2bPnKt?_*u0mBqP%vmd)`3XQva>AS@Cm23vZUD3X~#rDlvsr3Gww|=)Y9*<Vx<H)?WYqvOF%)~r2j^-TNEsjU+c57Z=`!RX9*#Bzam()(hw^Tp2FO9pD&eTqYA`znh#@s+!FRd>bA&xui)i9a|);5Ze#@*)z*|pXY;<&R{%%^d^XJ~{t?(Ah@v`$gKi4ez~U2_Mmcf6)Vh~rM#5lQt^Ln6d+XH`#;?C!c6cBRqA2yxt5nNCvsJIx4jd}*yONOt#qy8RsWL&={a#BrzJyGr(?(-GqM((b;b>lXbZLL6V_=`0lIwf~L~pRc;F0L=r1KSW65t6xbPFQJ9@h~rD$Q-jtObIa@zpRc{BA+>Y7+#YFsB{ZRSUi<73$Cpx#<~>!X^9pyrXnl9S-=*cJa}sxdIP5I#XZrWpFODzsa8KHw@j9?y9ADbBRND9OKDJ+sf9HEd%k^@<6#r&%8jqd*4v6*b_6KRb_KMEa+<ngOChdda{LLMAoA=Up&7D;T#P-#`?`WOX>X!r3II7W%#$Eq62gK*1mG4jQ)0+Pt5XXzPW-_h6_U4Qf$DO@@EU&LW$P+2~6Sa)ikH-r{isMMFw3_1aRpChSIa)Oh`p(K%AyOP)_MBaG-Pu(m#qp)S+E4A|Z5=6&FRR=c(mU-V#qnjmy+G}>9ULi+3**BJs(*Myq&P0@X7B0TvFN-=G0x3aB`MBZ{tzkk+qi~gU$al@ALVp+ng_l+F5mC;fn@KJ5Glr|r4FWfX$_r&x!<!phVlJy{UV*Gx!<z|Zqs?eY&w^7;?sx>p!0|#e;g9y(}`zoz~e(=yy-`7(EfbmI)}yhQC5CVal6<!EY{ZsMbi1-L!5s)>#oy3&^~!)IxltCGhKE|c6VLW=rwQ0YL_=kj8Eg&dK9;xb&V3^P|5l&&41YjMTzYz73a`%n>0L1j5qD%!eol`2~pznGS~RhINEANiScIj*+TPf!39xbyxH%<$^KwTl=OUi4W;$%u#HjD^Tj^Al0Q63j8AQO9JSN?RFoKp)`q(@AE#W165~+GMd#UCoq|V1|LsfVX&khqb4Yg{Yv4=gJ_D*85&hIcn$Y!cG&&;sskG@x<KQPc7j@%GPo(p;J9O^qp2H?IqI0NWbbjlu+r7ide((NKF;1)nd$`@)-sG70+>HuPxn0XT{+JY3)=WAN9-JoCw^zn;yEy~r(oVdU8%l9rpU$z}_xR;tnztVnix%TbdGn6WkG+DT#kjH`)ueOoD$}CHcFeJ@=^VY$+-NbbtU?{>JH8jrU7c}yD<_>NHrN_1#+8!ApY{XV?1&cQO8t2-T{kf*T8hu{d1>5zb~0LwA9c$#@~8a8Xz}^lL1k$jsNIPcpRdurCY|q`dK)dqo2qT0>t6T7i1DV~38(S6lg_2xeg3x-_<b46y2glp8sl$LJI{v4i2hhXe{;LJeM*ezk2*P>`puip!`<_du6OCY`#znYyX)2d?RgyPUUUxc&R1D_aJ#jQ&h6dz-PtAFZcZv6E7mtom7sl&BMYSZ+FCzuS94Onfcu_}d(Ydk<LO-5J(q0XfS-4p?<nuUo!>&UQ~WQu6D!7>;j^6b2|Cd4Iq_x`wz%DH+bd3NM?HO>@)&v!h!f*Y4ZT9`ES?r8#ntPFWUo6vPKv7y&&ZyG&gb3lg_QTy?v34XVqDoTveLMlcQ{UbzFOLP8o#A4$BEBZE47>6M_#w%q_`STf!Yav5GOu&tJV>!zxz>~7;nbus=U56SGA=0Ulc&?An(B4r|mzO|7>rmX^H-rx5n}McE`q+cwOb68PtxG*WlziEI&@?`^bZE=c^GZ{Acw9<xRNnsjBH@ADJT8U$%teI+pSU-28#kc__ZCrAzG?2QB*U9E&^-XMcFxAR1rD`*7!<qoXCed#*I*1+~)*`3uhT?HtRmYyapUFUFhFw+vsusK-W2?Q6lc$i5;tUW&I4^=ZA+ZeF|?Z`Q~5WG}HeUW_;MQWt9H`j&Vxu9W0JI^RJ4h5H`qGM<lTbJc!ozdx-<jcLJ@A5%RtUW&t0|Iqxf{dl|>Z&tz#x^BnBcrmW*A#=&kKa=9cII-tsrukvu*?1{Ve(|RH1lMt|TOyM7=jPJyx$Rs?qWi+{x!)t5&XWK2kcZ;rr3@%c^U?3fTXEv&JDR6#<ZHO!`^7d>o)YFcciy`d%J&^@<i)t(5m7X+nVA3FxHU4-c@FYK+;ivN4f%W8u8w>hXFsZY0I#p6lii6=qgM->_mJ1)uDhK1>(T23G2V=;dwDw+=0!K&E}x?PROGX`>(#WY<WJkYiDDcocP{bz_J%TvVjSwlUeSH6Yn~{^n{}ov?VBQh#2t^*p3!>xQIAA1-t;VOczyMZf1(&y#;d-Rx3oDRQHlr5Q|j|^iDEn$n2${4@3`-;`9t`+#LP_jKJI%N^OS`=pil2LS`S&6cis1_ewfbdFz>qa-n&cW=fXWwJEnD?@`q|4k+0kB0k3Z(@5X(<uL$Pf19}+cE4gtsh}L0>&r{hxs|oEFE~}g*#*dw2DYu)*e{uW2mp6U)B2UWAn+hJu*ClFh$`5ka1J~bif7HX2Z{@ycE7SVS#P_=UUT!jDAJ>BcQakFvuX(<aI$KW?<5PKXf%37g1WWBJ`5)1JO`e=2#-aK73)<Hlu{=qPL)FO3_eD(PJ-O@Q?ZNyz$2uR8B*v$%H>7ihoRl}@_J8xKynig@Rk`u7h`zh*_=F@eZq<aIv>y|GR&M9<J>C!2xN}KTJWn1%`=<ELbJyDq9#cNnf}2TVyqQaBoo6Et$j#4Omy`AxcRWuL<4}J}>p#5<<%_xNcI3_4OVX3XIJCCWx=`Oh`<m`^jQ;IsejgKP{p<Ln{}@H*$@m_1-=~G^Q2yBvTK~G^;^PHgU+F;WUw57_afkW=`CM*(QPKn6|7uiE$!;|2L3v&2{>fsTtI-qby2zh$znlKp!~4fVKApRseAI(~*O|yma`R-0ALi#77V`4kJh!a$eQV)d#jPJ=nEd*?7fIJuLZ<EDzgKyEvKZ(3vq<iz){gSp+<D3DLV4QwE_e5BkpHK}9!M7B-}XJr?H2Op-1zK7`&JhAy_|7j-1?LHXU-|fe=XYxI=5bRNwTZn&sM|<c6Z-+K{W4web&QdaU7Xla`5~`8+k@<J8zcs<oAVqH~0At_S+@e-E;8Uv|nZ-kIX%{GRyMwAv=$fB8|IirRlm$^QK7S>tzjYSNh|;%X!b*fAQyKVn5!EtFTf$-%j01`+u%K_g+xE-7lXa#=lXUzW<f&O;V(B*Pp)gO}~yQVw~&O={sLt>npXR*PlRnpN;$^KlSvRlz)Ky2zNf&?7uQjusiXu@2Jf4CQa;rxa*>XCDeWv+W&C#64Rd0IRWhMda30`Uf)C>*{6K<7yLQu(<!gh9Y>ixwC{%eNB8^gE}b`6$P;w?dEGkx9Q9u)Z`9o%xKI0)CeA(FcBV$tbBWj}wWCz;y;Zck=Lqln@qW;L*ekVf9vH>#x^^f<97pDYv1DJJDm{0z2%U>4n@**O<H)=*m)BR1+fseCsW;E>w2@cnzVBZ7^861Y(__hQ?Mvp*QP252MI1+JGn4$OO8I^6{g&$2i^o6mG2Q*c-5)|lyE877RgsiOi@Z*E{QBWM^={!4;&?HGEs7tU>$>$@$520iEPq0bH#L0_<-g8rctVV4O{0BSJ%9HTVjQZgX&=@`Uak9`b>5548?evq=2_K$L(g&Lz!Oq@PNaQX6M3xezUUG<-&NNIO8uiwiwzO&?z*BpoikZygHA~CQz(MpmxXg|_r2Nt^;XgDo(nvt{2u+lSm}O^#W{ICw7y`X+@C2`SMmE=K1K3JyOu)v!L<zee$N%Ac0Q8biCewXY4Q{Kr0#p9emsv8eZ~sux>k3}@6;=9I3dQf-r+BLj@6Dy_iKEG{G@d;C&c(PD;A=BXyjG7^Q5oN?@PBXNpWaasKx8s$ZvJOgW!*O<E|8k#*{WxANkAfx^(tYireH@((}@L4y63!jqjxX)Pv~!ULF2kYR60(O!>{oJ8<j&G=|&Fm-$nrc&<g~WJ+RzRI&e6JDBR1s+=l5cdbTVI^Q~0MQX=rvYy|Uxw&Dg_<Yqlbbe;xywu&tZghy(w~z<z_Cvx<%CmXXJym)xwZh3C<h8lqiC0eZ=VIa9)y<3Ol}zo|?~^J%FZEzSe*Udq>?`$;x{dO*Eab<zaohe9Z{O}QELD1rYbnn_RfkLMoAaV5kNoLysXy%_*U3-hQ@i=q11Nu2&oNnQUmu>t+p&>n?auQPD6iBm^rO^2%2vvwvY&64?D~alJkQ(OxKDas=E;GS2ar2T^4}U_Q#<$LB)e9j1m%&>jhCMb{Bi8=d%wzi?!WGHLb@-d;}hh2rAqN&eLj}@^ZYrfzL~uuzpk0@SLylM9^^elT$B4B{-{&0%kefdFaLW0HT9v?j#8;8{r$k&zohG`D=2?dZJs|(yf3Q_<v*zpic5C;`~LKIeDx})iPtr9w50m^>qvI{-e{^HQCDimxvn<5QJOT49#LMD>fcJTYiUz?J9>CmsePv%{qF%%ePdISUkhL9uSw&6tFl!4BBQB{l0zw^3=I_il$06SKS%%jpOTKK`+xPPqz!7<{Qvz^Qk6Y2?lu+1l~EYihSmbt1~-N_0yhS?g0=*=0(XLT1a|^|3GD&?65J2^6}TUG5Ht|XbR>8X_-ho#q0lfe(_7$B@J$rPiigzWA!b@0tbofwTY}4hH5A5QLHmK327|u>kAp4+j{`4({tR9M-iE?B8X6B~dJP;6K99oq3G@~C2{^kKX+AGvRu~t9egQ59_JP&}Gp!5u0ar(1TnSnmTnStPS^-=FoC{h2%=Ep7I2ZVD59uxN-{8wAjANk*;8^fa&>di=E5JX2m!U8o51jxW5AF{g0PYWN1#Js%1+D<C1g-$i49x=04E{qQy{izj!gvRCCwL6>Tj);kx8TVrj3ZDO{|UVdzKiSqiJuu~gD;iA*}yqb7*~b116KvNM`5f(1HeotgLUu}6vnHe--B0!_ds`nnI?kwfPaDB2LA$nh{8CJ7pa#QF)NJALra30HUKlN0cM&XTpsMS!<b!%=~LmlPvHyG(}HiO;XBg<V5aMY`&x%SU^-pslj-O)ra?j<1_^x|gy+Dtv+!Ix<5@ASB|N)Y!t-UE2U-`*G#{AhBZW8*_<=&20Db_D&M1qai=YYMMc|Fl6z~S<NoWd~=~M7Y@ITOk9%81SftkKQ9adi8_n4jmZ-B0co&m21uY;ZjGd%@f2VRT9cn$O{cnx?p^gNj91@LNcNJjY{dI@>~%=8ub68H_Yn1`5Y2{0>+{{t-vW`*%P=;vUjrNK<!E5uB%fZu_yW|SYGo1s_0o1mAWSHM@$)@2mNZ=vjZZ}BtZQt+h-xD>cCv^TghxDg8DUeIsBy}+YU7%zk_0y7N*F9e68Fg^~A12g>{d>s56G>aGUZ{SQ`q*cI~z!gy#YtS}erv1ShxF2*dxF1-D4gu@nAm|`)5I6wZ7aRcggSG(sftx|gfSZ9oM`4`qA^qSXW_lf*4*nH-4E!tj2-E~00dGNJJR3R}%ya~JHh4G+<F3$d;I80m(3)VTIl$Gx*`aq7;_Tqt3hB>arayt1ZU-~9!A!Gyh;M_PHnZZIOsfb!RDr)tI|=@G!u>HF3T8S>xc6B?pUgu4G2JZm=VtUV(<q_Oqwq|aUJ;(r6+A<x|ALv8^7{0AO9}B%3Nga8i4ZeQ5K~Nj!Au7V@itJ1$$^Mjrh#Cl{z5$aBi@<z65_uX#s|~p!gy&ejH%`re@s;{(~q7{W0P?v=uOY3@q5$rX^h{*9KbY2m=hR>LbrmM&i8zpTNp2de&hKx|1fsuE5^N`UwS^xX^a~|8+ty?fsBho8-SS>1v7oA5Elo(R!Gl*UxP2AFkXeicqIzs70_S6E5Hk(N#KRx1yBpT06ZUh96TR94|)vD^eA{9crG*+JQq9%8V8;Oo{hqI7BmsO9GVPG1T%dMP6j`L=JyaYEdXX(1kCg~>a+43Z7@w0+DygumxGs~FkT8x11|+HL1BCXh4C}!-{5E9LLSn>9%82T!G*x}pgq9#z`iJqM?${_j|9(w&I2?35j+R{1N1O>6Z8=DFqr8j@FDO8=zqW$z;93(7xf}7?nTTB<2ulKV5VKbb-*2=eZU>TUqT0fzXX4U!ng;tH<)P$Fw?eRrrp3ydxCp_oi=;oI!wERnYI#qXaygc))IWKg?nOJSh&Z+=ntm<cs}*dKj=TEXNCSeEA;bOJO`$c;7!mC&`2=T^<btmz#G5@3gcnWAz-Fmz{9}Zp|!!?!F5m=dqeYry}^Geqz@HhRv5=aW55P<CNu^-6FdWY1Uv&g2^tBW1pW@XAN(D7B6JUUB6tFHH<;-z@C5L96vn~Oz2IQ*IOskw(*xjf;IYty;IZK8D2%5;qrglLgQtO~qA;F<!uSyMKKKy$9yGUy_#QZyhqMMb7q~jKBe*)a0}A6n=pZoDY2ZNcROnjpRPY)U#(Sar!F$0cp{Kx1AA?VVAE7YL>qYAAMa;A+I4`&|3ggDmreLO>z)ahN8-p96Fm8>)xHGgXm}xt3XK+gt#`U2M!S%tVq2<7(!P%fW!A$RYh_iw3qA*T|o&YnA04IZYqcC0xT?J-33A_?K5$X?~2p)*SxHYs5m}y0DYp@SA6W9mr1^rzi_5%N=kZuG21`dY~2Zw`)K?A_Uz&Z-!zR*74zF=Qycd#$G1GGJuX$x=%u!h38A+!OwA-D##I+$q%a1F2zv=rC}{5cBaBGAI%BH%pG++e0&;5^_=Pz9U`>|yO>{D*=WB`XSJ1%>fz4`~iCD~#_zUwVjHVSEm1gPEp)&w(uz#yg?=z)UxScY;Gu7|(<*05cr}o(UcW?E@YK_JcMD`+=LGFfIfA0?hP-LR<!%u8>{_r-QFSP4G4F78J(cKu3X@27$i;4?$r(5IO+Nv=?|FxHk&puFx)ErftAo!EI3(H-k0>Gp!452Cj#~xEi!7m}xn1HE?+p#-%d~JGLv9Q9gr~27d-F2`vXM2`-MpxGc0PxGcB|v@W;`xDK=_xDL1p3ggz$HsChsuhuAxJ41VcJA->d2Y`Em`$L1k{lSA#7>|IC0y8ziBfwjs*TGxCH=rNDH^3jEEM7n2XU1g_!_C2E!7ZSDz%9Uip<}>(!DFEdz+=ISQ5c6qH-a}}Jcpw&J_=0%9|fO*+Tb(bzfc%w_9A@=eu+6KGYaF+P#Bkm76dab0xk=#hQhcIG%J{?2h8-Xhqw?pw-*)0?>wXrz-bxfkBo8=`VRaKbr`2YZ$KY_AE2!pD2(r;Fn$hYK0SwK1+&8Vg@+2`XHW&KU@m`#!uU_<9q^yvt0;_<py$9$EpQU}Aap1AAb2}81iT%*9EI_B(3xPSqrl&R2Sfe9gTXza&A>guO;H%D&@y1AZ0=U^Gvj|1(re&<!M{ScfPV%5h{AX@^c(PK@KERwFw=qHp<sV#Z?Heu584&%2kwT#xE-`Dm}xU`J8*MoJ#ceyeH6wuq1C`O!4;w9!AwhoD}uj(76X3)E`h?hD6|l`D7XMLFPLdIZ~?G4Gz-`poD+p{4rpdD)2!ee;9St`;9TH*(EQ+h;DQ;&x3kBqP^SOW|H}N+KlY8SNdIH=|NWbC+KTv_-7?y8lURH^XJI~Oj8iZEv6#l*D9Zl;K|%Jg'

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
