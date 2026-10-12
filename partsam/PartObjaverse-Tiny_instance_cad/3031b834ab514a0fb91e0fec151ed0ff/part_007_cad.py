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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_007.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_007.stl', 'source_sha256': '894dcde811194729faf9fe1ec4f24eb2e2e930600e6d158f7fedb18e8b8466f9', 'input_faces': 1028, 'input_vertices': 669, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.19686895608901978, -0.25988835096359253, -0.27882203459739685], [0.18655438721179962, 0.48129522800445557, 0.2729041278362274]]}
GEOMETRY_BASE85 = 'c$}qu1#}c=)b?zGLrH<)wrGIj?hF<rxJ!V=f<uZEY=Q(xaF+m!J0v*41`8A~?rbTgI4w}Dh5mc*eP%N|&3Dd!zAruZJkLDuop)ZhnJvwNe3SSq@|Q<xv|~n4#Ttr2mPYYchW8viv`_b*Ly8X!9c5F#XPy2GoY$mv<7Vw`%5Y_LK#!h7x(^PhY!9d!QZb;YJs@Pz;Gu)N4(u{$aF3p(2X^g0q^DaS(z|PDPxp19^5rWPwU;Se)IQe!zx+$(PJ*VC`RS+|^>@v0aH^`l*h#3p4Paf3s=&IvO~g9Z2W4YjNn4k7J*@g+*0cJuuIXd0v99<Yk$Co=VLfEXZN46xC6;kQXV#V8j;r$AG6&7Nes>uAyP9XwIeb`4iKlQc_IFghu#5dCmyvjGzq-zPpPR>6pZ)1Hr~lXljz<r8zMA#^Z%=zYciO{ktUr6qy1w_!71p2BI4aM5B=L0a!tpx`gzqrx`VX^jnRTsBIf=jVaw&&DuSvO`%`EZc{*~j`u7n))()TWr^gj*Kz4VD^Z<%!^UlMt4{dF9_+Vzmc-}Fm7>%+cq{PyL2C7z6*MelZo<5zkVJI=V~oang<a6LM9K8t7n1-j^wt;N6o?=x91e}Hv0OC~NiEg%J#rxF<{{%cS1bDe&FN&E2|ApU2^vaUWkw3hu}S7BYbHI;R}^;*$gB}G4$?=I_o2Q1@w2KY++&7N^RI(*BVV7<!QQ`{ady}ZfK4Lop~<7x4Vb$xpN%N)<&Z}+m^`>D77Q>f^>eqvo6mW*{JboCyN|EH6zE1%Y1;_H4v`^>uT8*$gG-VYuS|0=(8JZjDYYdF3|yCj|cs&GAOU2bstl_A^2KRiVG#ev7{ujN=M{*y=XbM<s-_Il~LCa|s?n4PGuPWeOhNAo5AgSxcm{N<#6uT2yE$a~4}@O1Lr_;C`?!Cq3%>3^2=-|Q^;&AyiN>zJNZ+ToF$qBrVxho9SaiIo4u9HNh2Ed9m*FUjw<Eb`p;?<HS;aZY}&;wR<*?-DK_W&erRoQ{C!Cpn&HDL9>4@Acxp_8#l%gh$e@)_joksBx@ocQbj{OUpqL&)igZz4}pb7tyCx<n(K)pG9!`26qts_B+;<m@Az)ymE1gzwy0`eBH77A`VxIiC*Ln@$d1uC*v7~b;ajz_E&co5&xFoPH_4QXXAFO6@GY%^{J0p*B=+=bh>I@ILUgh4dOp*qIbU5Ok-VZH9`E-M##AIOBd0H=4M^Zl9S`tLTX7oTO+P}wa*zjMgKR4#Pcqbr02=v<E-z9lX0?3Ss6c{4q#omRNw;Z1=bDbbU$jry7nnh^mFe+`MN+I@jtp)%I$ZR+ldxhK>X*fX5Dda0gp@itIVQT-6HKa{`gtOD>l&sy2-dP^d7ed<>ZHBtk0g$?N(hlZWV`rjbL4^cHOJq^*v#tJN;z7Th#j;<LFVWD{q(l%;g-ud^yLLYy|6im$UcH<*W`EDDm{XD&v)ZEooQ&=_H<kv78=zzgFitzioUZ9^av?J0E|M{&@Ja&i>n`OFw!X$>W|Lw~KY{LS9afw*1R{4o@8;{_n?exjE}bO8FF7#=07Jo71TcZ^!eOK4FUZ@9oU#ROXe6k@h@V^yp)pe=X~TS)9I2-Q>BIe-pjl!kMg>b+E3NQaOI5YBq=THy_c*_mbxxo6qf5ThRR|hZm|S>xb`B|0MnRpCg>k)_r9BDe-Wu#J7NTZS+NyXEiQ2<!KAnl~Y%_-d*EPpW%28zBtVONw#wS)ukgAv){y{tSb*Li(c;WBEF7~5&vOFWgISjUCJ$RB<sfbrr3tcy5&;rLB8+sIvH=1eCf>hUwn0dF=LFh+b2%R*Pvmd|5}mTx1-4mi9eu^=xZjhzddzTM&)@P(VrcVela0>0$&%+z`C+C{SE0a{xbfxe7#@#QE84}uilx<$KE5Fb!~Y7_YeEiin}@fJpDy494hG<y;8>Kuyzv9mom~1CoPcnxxR_`ce%ms&|axO*P}W!qv#K^NdNP#BJn>+$-4exyR0`x50`T4{&FAtHNU{)h<g12*O!v?H`djgv!p-z4HCUTi@of>WHVo@S=OzjYggTdd(HV$<MPXTNiQM#??1D@zB?WJJC7z|T`ieg{2yjuf7So;9&`F#xsxWU>upl9u53ObdPrWLx19HipEK)5x!He>miAfh80+e#m6ES)WhGyMt0bO}%Vk`xm|OJmmG_wQ<$6C})^BlVc6*ic0~hN`o0YrG&vndoo;T}So?KjCu8B8g{=fLsE_3|OBaLJ|yc{~(r_(l7>b>87)|D)iWuDr#`jVIa?{3yz4S(lxU7Oo&mpPrPD}duy`qdNtLN$)xwX!nD?>LYH=^4cJ<5=)uw^>)d720LiwPd?@vVYd(^1KCyW&GI|wbPt0<?)qi9M7ZSqUWt2!}+y6mG-%@is(hU$~?IBrL@O~MR$6YbLl(NIi6qrMZeMbyg5C}-)UG^3&zO$_STupW?dP2Q`R9hpIkEQ`pqh`u2z$X9+67?yAQg@?RLx*nI}8ki)Fp-pU1qOYv^j1{bt=6zngX4XZ2;Xt`@1vx>n&{yjgeEs~l@Cf4xKQ?TP8y*llrU-KZC<zo8rcTA%b1&zoGFFKuRW=`Wq{aeXMcDoeZly~k?ydv;s&NPijM7S`waO>c2J#$5hd;KP{2boKH5{e0hr6B5ra-6j5@OdP)}cyEkXd$^c}=WDC39jGViPqkF8rv`BPor_2Dc<u_FALCWd2m8h*rfY**aC(%maEWJlevU`2)s5p(XO)aG*ROtI;Eu#}<z&)0FCF#%AAjhEzfyMV4zGImnH!Ust`+*>0O|H-RajRqKahP@ujd;H?Z188&hZ{B%KIF3@M9hiongCK*E<c7{am%98@OBxd@ugfs&TxoDY>OyB4%te>&|x*w(@gpf7{A>mMyF+Uu{zUl`4u}#c_!1@%$DpXXRum*0o%hxIO7#j?9yM>svTIbx(1>)-L|b>nNvhgDqb5HDLDk#B}xjP=2nn<+07?cIC=@ersa7mbI<S3#D6&j(Oav+GHH~e%B_Be@Ha1EA&$9FPL>@-}kbfnbMK{U1O(;{(ix7uYR2)4eMIA)x7R-?O)F85LKJE(cDj+7vHTn>qdY4pLDHuZHedIc!}q#tVfiV8z(V3N3yQ}nNQYrV^*Bw>w}%Wp6hzHnd8wvbl7NaSE}Rcmc(>D?5fPyx$1B9>UYI@ZcI#9BA4+wl0H42+n4h06JNWERO9mmN12lw%;jcJUpP@+&oZCeuk-NI4d(u({gif7V!A!P++i>MTg`)Je`V2~_2%?wOWR5R8at77y?8$<w-?o9-xb-^%U``Vna`<|m!H>h_`qmc@0DD@^Mcd)dY#!{8J3ybt$Jp)_z#~V^W^!^p{!>N6dm)RzBowcwQkSWvTn?4RZ_BUKM}Il?615XIg#5-Z1c6|=h{2f;&TthR!aQU=`xPZ50v%5*z{iUD-n~%al5#kY;9uw&Z>L*-Kauq%=M+!8yl0D?)bHaj8}akcwARHZ|8nuFSwBRp?cBws}t+LR^8~ou6{uh&-QgPF6^Hn=U44UtYSZ`=k1?9O8<`f=4AiZ^>`oUXgZwZcXW9zx?cv??RVSBc)4q*=omlkYdgz$)^CaEeImF#?7wA|eQW#}(O1cSP^*6f^GPXQ&uS?(-cLH4W#RK2``aZe66<$X-P7-`U*vLB%KL5Lc)}|4eqZk$FFM9ywcYWxiRs4ptdyQC{R-=R?PV99uU*kCquGCQPZ=Not;^$&>to|+ul8Wfn-<-eH}yl+Sl4pO{@n3uA<uV?tuK}))=sRt(N6Sg&qRNhTl(p}3!HD|(LT|!pK{e2A?uB2Z<lbqmT}3dd&Z?5PS%yrDY;&?Q|Y9A-V7JrGR|0aW1KN`wQn-r?5{r@C;naU$ap=mIqR+?F5cH_xzlm^s53T5`?`Htbj!S8=+=3`svGlyQ}dU2g6hk8F~&DTS9&#+a}&qy&57!bd+kh2*AC{{otUoF8?)EzxkFL!B~I`;yy`r^$gBNee$?+SVqJT;QO*^@K5_qZ`L<eQE(i7eR@uMr$t=2MJ!#dA^`!luxP_cf|B5TvZ^#SoFRs8PqAL@ZaJqeSaer~n86o=93w$o4&ub?7_^%5%{*&pYeBMvq?4@_d`;4zq-a6X9`t=Cw>e-p|IsQX8!?`^AOyhdgKI*a#dS6ZAU!8-~@A7ksJ})Wn$Mo1kTrYZkzj@~LD33>R{H~nk=bHVs79FI24f$n`xqLkPwc`ipnERb){<Y}F{HvwTCc3keJhw@AX(w;8irz_dduGw?$1;gtz(>;aZ?NbCTFjPmcp~HM&RpF8oHIYpGRJQ}GECa-&mUOVMs{J{)ijKC*PGX(Th_@|-B>3(dOnx<tNTiNUJR9aztLIVk18ck$hpVZ<UgBr&pB%FRCy0jYQFeq`%%)rVi>32HK)!De%^X{PowUiBkSks?IKxk_EGZnCRX-wm8wUY>&vxoDEAk8uX|HiKPl(n_GPbly`heXXI<+j<*E8N<9SbibX5HR?kN7nnzL?yG+O+B=^*u$`JJp=mW&ktve3JU?ue>6*_=+-@nBv*sNokTd6lzgKf6Qp*bqL?bG4f(<6-)I6U^yXs=pBbLq#=n{LY2RdEC%Pza7v1mVJ|<t8I0!eU`_+&y}NQ-CoC6^p(}QKI|!9%06cOR9@HoXa8u?js2s&P3%~X2kR48!-G8jC>z_3=I8mWkoRcGTgtro%f~Rj|6wy3CpTY^{t|X|q`4flrBAs$ok_w+uwJmev=iqidCspRS=XwHu5A<D-YLa!*4Jeef6Y(EleNu<%5%F)IiD#g<Hpn1Ls++-4_I_9bM`}K{Xgde7TxuCJ6;#)MeB!}>&3I*Njk6_`&-5hMJwEfpI34F1J2i$JG>uJw14VwJV%o8`v`l`2RRq*KCBjp53VZn$jHW=U%lcW(Kl9+a%j~=^y616Csw~!-Kbxs<I_?cPk|vaFK5Ag{rtS0^^A3;{L`+M_0Ns!>COGrSuC@Z|A>`7=KLDtr@H^{A4f>H%r8plZ*N%d_>Si}twC*G&)8FSxktJh&|KPoq1v*(3R-obI{C%5mHznk>mD!tLa>z2)-}9tboJ36SLgeqWF7n6jdezPNH@+0v^{HhKX2&9Ie-#1a;sVQ>@U(BoSB%e7ws2sj^DG7=$1C}Xd=2RFqgN#v2U$=WxAKYu|Im5w7c2gy59Eam{0A=7I@{?I*)sF%X+}0Th`Sc-Lk*%=olZI?=P%LOgF|2kB)V?tILUXiRs4r+@q)bPR_MgoLTRse;Fw2Rjh|S`idsfZXZZHacr6Pk@ccu<-O7ID{}s<ytlDm<OS}JdX5Kj?i<|vI}XSE=)Asii;P#r0$8`K_mmNZ8!}qXIUScSH|6*(<BwH0#vensjz3o27=IMyn#6NN-m}_M=aT)op?^p%=SP#zuJh8Dhsyr9+~%`h@$4AFy63&5V@n&xv*M?ZN+tUZ=*GFIYh@-r|93{WYR`V9x5@hdrhlASx6V@@y=RELzsi$}%R$jf2Q#id&FBA)ino5|cKvsyP)@gHyj7fQf8_K`87Ar9mPy_h>~jrCto*IIQT~Q*Eq|+Sl)vj{D?Ycd&O1u+<ilCF%u`zCF(VkQ^V;?sBl$kd{HX8z5GL_k=F<+b@?O!>zZ}aKkK=I5_;1xc<9|k<@r;&rg4*cucyoL9oZmvXu0uTjmil$%FRJl#E$bZR)BA9~@0Z!~{nDYDJl{FP@=h?9gRx%HYi^vx@mSVZuHNyYTh?Rt_v&QxbB*<z)^PL`M$0<Tne-6r#=2b}+(O2=F~`KeX=ktXq$AxK(PO>WpW3CnQ_Sf%)~k-y)goE9tZ()AZ6nR;G}gmPl9{aQx5nT*r5O3H=ZC-<>~C3DJC@Aj@0hIXaQ(uwS*#oT4y^O_s~=`bzJk5>5&8@0mVJa(H}(<gN9dS;olQouznZ7TY<{j~Ut^z{d5%|lun(erlezqjeUo-8o9LE(mR5eh=$7?{RX5gM>W{y%Zr%5(SIW&b*Nd@FRKBL2$Jds9rFwGZJhQ*C4|SY8Cc0(cO8Z<X2k(8ZQugZtbNt3W+M`?c(H`BhkEVS(hg;@%+SjvgS$EMn0PB`{-&xpyk-2<~^8~AIoF}NZcA{I(B^<YxiEcf|Sbmvx>$wM=ldwO|XN+?aLs!~2_|N$a>&7{Z={(1*o6l{${7vUJX5BN7E7@2#zL&7KD#G)Kt5MuybAF9;CquWMM_F~_JW3hjl6WlVT}qwKTu<t#>-^o65|~@g&mW9q-Fj}OUz;qt<y_9H8|QL{{-1NX?oRQyocp;ty<y#YerVN=^FvqlXG=LA%lV|f>CIAee>BcHt-5i}=?bkDZEokrd8yv7VYFBK!MUqdH_lz@{FdXloZo6ij){J(q^tvfIVk(4-tqiBRAT4GX5CnqI&WMQ-Fp7~X1Vk$>-!^%Zk%H~tCn8Ly5&4vOYt}BO0{W{&Xjrid|sJQ(P{4QYMS3=zteAt=+=F~uAQP=&h52IuSK_<^E>??t&)Bq<A!p-6vwai50du@*7pkwTFUzheD`JFa-HkJ8PZn1r?b9)wCKkB3wjU2@nM|QUVqx^rCZ*QXd{cPNvvI2b)#K5HbjYzanJEslX2BQ=~}OLh4(vF-FUx4?}->K?}_X?o6Ek|^1jJ=B1HTx@26bdo_WP%ywB1z2Cg&v8}GmLGpj|nyf3q_dcDs4T;u(kYg*IwX5I6iZqXet-SfULu8ZuST6w=Gb$(nd?-{J`87;c!J)@yp-ZR=u$8Rv#i!onYbz{D!_oU`@dft<^3zYY(mT}3dd&Z@b?KdXYAFaC4AC;gEqR;8e<=`k#L%v)6D_C^v`{H-wMYq0pj+^7<Z_EpZZk;czx@W%Fv`Tc0GkWTYlHcr7uGaVI`o4%wUhUtQXM<xlo8xhHJ}c+pGmdUfte;wSqn|pe)!UL-f3fODe{rc(Soe&djh0EhR<0=HndQ3(?dvAdG0te&^2qpF``cEpc#QXVqkoWfH0EpLdkII)N~{~>p}x1MjQ<fcM7Mmup^S-^-$_`$$Dr>(%>KrAAokI_<-FPQ-H7)2XYt2)rS9&<&vpLxQFP1qC-l7vUt7LcaShnK!`wbS=lK@hvkuq(*kLX=*B)8N+P9X7G51r?`LIPd_IDoL@_mj~H~h6Wp)uzC+Lg3&ZXdcJ#;cuRzP9Sdd~FZj7h~?f#=h068~av$P<)J6`!v3%vgn@gsm?0$-OZ#U(oPz-kndWbWRi8nk)!e*T}W^FKB`BhSabjNoC8~Q&v#|e|8s6^(G7pKUX@s{`Zdlma>;q8^}8=+M@P{u-<vsq-4*Lq&c=6!?eE8$>-Rsp<-0po@!x4KH;?|XsOXmO3Dtjx?ewZIe3$6zI9YUKo_b!E*Gcq!qm-NX_l-)DKjoY_PZO{27#%mV?=qLO=R6Jif4-}n+ijOQoyK>Y^u4J0xyJXRdfb`aUirfJsOtF2d(8gE_pA0v%SAWF`N{oc-|K&Qk2xOW`&+ASe1GdYnuOPP*6(<=g?3r@Z5!zQJ#D(`vM+f$$m{!C`hM7)PUHJw`kvV<U-+Kc(Ia}l+28n%TJuT5<A?RTXl3mH8E4~O%lAB4%kw$5GxH>Q?_r#ipDV=g&-A^?<opcdm@@2o6sN1y1Ub+1y)WO14m{n9^?iY|E=l!Bo;x^L&cnk(WxujPbmxPCqAMq5eKW!DoV3fX{9T3X_M^jI&wYA_ziU=cyb}LS&*eM$K`-Qcjxzh?{dwmfd7q`193$WJM|_t3Ro`j1%({9qme<GD@A<VEC3N$1b)O(!S2~m7oX+<0x;Y-b!A{v{wkpWq4Xg7f^Lt;d=Na+e<HNe%JgK~&UiZN(e#g}evcBq_R?aCbzngFlTq=6Msr<V+ZD_Q7w_Ny|pyhWTuG1gIf6NQ{onxQ=a!%atd-<Kp+$ZvV?~QRXpWe+WzpJ}a`j(gf`U;}wD{;&0Z;$K5y77A!$LGep-*A>4EjoVBqE8EveMr<?(JjBP(bsJ}?p4l(ib#8IvsIpJ`JIm1W1qz1h?U>hEZZXeZr^8#$N0TZsWADy)nR{WFUbmAH|I;AT3mkDwK3;)uW|^kD0<Uz@}14_a9OYJY%1}5nI<}Zm!}7{6Fq#EydQmDQu=f5ZmjFEV_A2!lJ^v9u>qow?=SHj{z=A>;7t+_e&3{g8^`-Y{rO8t&(V7FyP+LRWqdF2T7E~kte&*<YE@*vdgOz|^R~Fud+rK+{-x*mCh_3+Tw0pSe2(b~&L;f>zY9}}PmAFCEmT(e$AV4L-fG@tfBU6+;{RUba(1ms#rthn;B3)nOk-W0lT@BJWvh%gapR?4{4>b!5^6q?eq;PT?yoa^{$)SpE5F~u@9dP0VXQl+%oN@D-QV~!a_&`io9Ou6qO#{TpTF4mot58>)$PaStnU0Q>(G#kqT_dh`m57?Zl!*FBKxp^I!nL%l9c<SBl|0fAHQ={#|)BluEou`y%@g(Rh&IIJ&yhzM4ysU^40Jk*_TfZm2nQgCsl6cmi_nOVe&hw{+Za{UZXYpyPk}YcrJdBbE2c)L?5q7JjHWL{H+FZdvlzb9`9A2UCKy144Chw>$}>@`t-&ki9g*_`98AmC)v+_SuXK!@$>qfsjJpzN$0%3<oA!)%E>$zwO8UveL>#GJp97(*q;}d-}&HozWSz~TyC!V<>hxg72a_Cj>-YDZuD;^I(~PoewSJNzqVpsZT?8ob1Faks}W=6_dmscl>SnxKEEHbr;HMP-)3oVS&Pbd2{9`qp8kEs|8nht?0;mF=;5oxf7u)Pz9C1f=o9zjJO8wD&VJ{pq_b~JsmIjcrgA<GUK9U+c8Y&?KR&N_`u-yR!S%0r`cX5lU)`@b{pw>(Np}j}mQwLoLb{rMa!(>BADH-0?)#Me|N6;&sgk8D{@;FcpX$6j4cpxo4~zki2fqm127Vp51Go*Ga0~bj@E5>e!3itcguejqWfSZPPB;y`7x*op3!E^!kMLXI8GHn@fWNT`{sqhePM8jyjQCezCU7$1AAsM3lM#P!6C-{fc*7=~jQANKg`L4Q@k?&JZWFu-B>g6?i9fZ85zmI_X96e851tJ?Juo+Tdhis$)Zm0KY{FB3@3jd&0^bY12lxPd5BP2v@fhIm;4$D2ff;>-KLmdVtPD<A8=Q=I5*YEUz$V~X!E*qcg8yL?tb*&N;DqhLtAN*n5f1|P1}E$U9t7S1*b1Cb1+VM2K)2NZHUMt`pBgaYf7%4!+JqCf2mceiBaHY}MevFuoNyfYRqzSGAHfNSfKLD)1|vQc_#^mG@czKw;Dlk|{lP~Ar+|+Jj|5%=j|9I7Bi_L#M!cO(jCdR1W^gj%ZGl_C$%qF7kAf5a3{FP8lTD0xXW(OSGU8o;>1@Kuh&zDafjhvP0n>mJrUq{Y-WB*v5#ANNn@x;(ci=;CGU7de_rS@BhX9|0lM(L?d<9PU4xEg5AK>5MWW*b}v4Ks{1|;1E`~{rwGB_FWq`>pwWW*IWW^-FExA_1Sa0Na-z<6*n;=aI(;AF&;*b?R&;@2^+5Z{6MgE%406G?C{VNn?IsxabxVZ;Xldw~xGKL)%7PDt~|F<ZjCLY(j~@MGXQ@GH0ueiZltd;@S5jQA1Y2k=$EMKI!rfFHmK--8q02R{UU7<dN!Fn9yl8Pq@FCGbYzeQXJHmC=5#+Y;Is@etrmaKfjygtkiDXwSrrHc$LlAkAUF0@H(&5x)&g0ZvHs(`^`Wqkj?a3fyB$=!3+Y0e9OH`Ydq=Fvgb9--&ktKC~r_55zkI-`Ntz6XKnKG;bN>5Ak4NR-c41ig;UK4xfbajd&Yd!hB|ohs2FBlejUK5`PUNUJ>`vJXaA$ye6;~cunwzz##A-%v%j%#OnY9!2>bp5wGulR&%#ah7sQe><3O53truA{x-R<K6rCrTJW^Ehxih=4RG6HU@P!g`0NC>2Hyp23~UWP$!$~JHXXPUd<DW*0;hwMtwZ<<@EvZ82c8G61E1oymWZPzo<V#z!d3t$fk(S-soNF+=Yr1$P65sZp90<zMmz$z6g&caA<`L*G_C;7hV4MyJK#h79`5-CcpiMc+qT>2oLG$bR@B8Zw>3feHbL1pfxZhy{0eX@_!aPb!0q7oz~f=tk-qInM>K4`DW8NJf$PCHg0BTS!PkN>h7n%^+zP%GX<Y&w08VYv&n9iHAGp!B2)_sVf#-KyWw(_B)&MUDo*!5MJU@62w|!Iu|53z<r$<-;@XBZhHGoyXYk(I3mI5#6wqkB81S|>u1F#yfBzQ|;6<|s5D&VDn#lR_@>G7O`NTU%}3~49^y#Vq^_dEhV0nh0UE8@01z{22E4*|F)%m`i>JP$AfIAM11Jm5KD#IqvrS&{Fo&<nw`BOlojmyxdwrg|a%1eg(=jQAhG0C2JZw2j8VCcpsj0OXT+E99*R_yAmQc3WMyMFE4rqrfKuhk#E64+s7T9u7VaI0k$k_zYke_#n59!}U05#9O#+Cc<YTjQA{Ej|R2?*ANy891T7JVS|C8;E@Px2pkN)31Llv4Z$-5%L5yNXK`BvlvxFoQC;{`_@9d4Uy5)t;&*^2!S8^d2Ce`<4IT%a3VzpZr`+}y_yIf)K4*X{!Owu-1)c(bi+d>_gcXpd%Wk`X^0<JqApXp4-w^%{VZ{HYcIG4Dgx}zs%FQeJNH}2t_|I;;=(gv;f5HE8TOl90uMqAf{v1C404eMrwA(1e7lpWfM%hyx)dCI%r~K7MJ=I3r4T66y)Dz)1)DPJ=)Cu8X@RQ&xfD6G_fKLTZ2B-2qg0d$37ko16V=DL}T(1N_1w3M^=YLU8gtd_;s)v)Pr;}*Yk*K3&J`zrN624RqB~VX<$-t?+tD~N(!-qJP>nW5yVR9egB~eFIA0=^5C4?o1o*ZGssg5S1o+cu$izs`lBNZ45PWh{edLsN0ycWW#P6)rEe#pL}P6!Wy9|m6toDaSbd@^tnIF<J?lr>=rl=o!#ECMb7Uj%*xc+6DKDUgp8$U|+^(FxQOp$1O%kQDVqcmlpu55-VV#o&_+<y{T+R1IOosay}B4hVfs^-vu56~{f*5$20<UxX2-ItoWUg(J>WD0`}-vcS>cl)n<FC&Dq{D#EEw2*03y$iARX2+x5Z0-q0D4?Z7!5^xSUmG?oEHDPj;_ayi%0B!(Z0DcU3&{WUKk&ooaLrv7tIn)#3EO4raF9`pFFyd4Xc~MV!;gb~QT^{vR9%02$M{%ep!jz_Z$cOv#;ht&;ONsE52qR8)G!OMO4{;tq*;5^r0k#0A{FO#M5r%=6ML5+7;V0A&*(cNq;ZNY_z}ExUg0Bak1Dp*`<$V_QMEDte4tzEM*MV;UKL|XlB-AtATLM@bd7^sw3H3xc6P)Vd6T&|sj5yVU9rZ-`3BFX`<xo%M;FA}1bQbkQ_}P|F4|z~ed2mm8)DijQ1LlD*)zJ*p(+tEJhq9+SsskJZUI)B1Fbur7+j1j3H|{t1@2JDyQD+7}j_c#7GlOr$^+wd0!RO(69_ohp3Aa5(eLO`yo`ugQ_-#U+8T<sUPr!E_?zN*1?Z}hCi<|OT2Yi(~Y_8ju;aQZvDBv>iW$=jtt_I(Pd!m6+;8F022JQwwfqV7>qrs!$vln<9{3-5v0Ne|{7d{VwZ@?*!bWbYa1Mmm%Ax@agCY;KF?#Tp91x}a@oba_GJU8x13CskZ2|g)-x4@}w&^`BoDZvTJ=RSOQfm55Id-eeDgWreG9^fkQjksqSa1Zz%_z<W5y4oh|e!}_S)L-wQKi@&vO!Q^NN5Tp3z?b@KPV{F&1)Tb2DfH)3@Uf#W-$j2Ww3+&AF7)SIxThS#Z0PGYgb}B{yaxSw4dObBJj_R5pN}x&6ki3TBPV!aU|Dd&0^szVB1lIm@Cv|!;019{1*Gje+?NZy2+$AQ5BCtK^gcn}$cTRjd<9PEhd3x7`;pJP;7@?pz^~!nC&>F2<bMtLe&9jygSclu>UkgTn-9JPcoqCA?%9I2@f+@24ZaWf68t6Z*@rfh2JME7_;0|p;Dj#`M^4m(0xOLB3!{$G0Mmjy-EJe@wirfy5G;q==(otpsjpL?1KPoJgBNsLHMcczTUGGJxbES8Mpw6W^AX<Nblu-=1HilDI>K$!-8Kz;Dy|7<f=9Y-7Otb*HXGN(XW)9Q+eW%=9QX)a6ZSFjUbrR<Ht~+QCTwluEpbg&+HGaPTjH8*s7-X@!)$U*xI{_d%N4oq?6%f!>jd5g*Mzl9yf&_>3|pWa37dnr1vUaU2k(loHsFSD2b6akU{~-lsFTsa{@`7J9f1A8C*q!P;Arr^z%D=|j%m0j0vHZH5ZD)J#4!+cZ}<!{wS}o@3sa#-0z*x0Bogf+5_%NyNAMrfW(+>q)P@M>!-&rX4hAP23O*kg4I{o3I24>P3_KdR7)E>{Fbte<6!>D`A{g-nz)|3Y!@(B;m%)fH0S*Tz90tA&I0;640&o~OVF<XxNBUJy;CS$!;QfG;!TW&^0nPy*0v-aJgZL+a8|fiF4>%co9{3dCc<?FU8gMMQ20jkyAAxJ)opDXr%f#E^ny{mZH^VhyOA~MGlQ0$#&kWwubWQ!gH26r22O}{i7(7;y>z)`FB7lRzBfw)}gO!9ag)kI27<@494~2Ecn9~#EOK0$|xbBKE$KV}IV-R5l81YKL4&a2%!7Bhuz=)RuHU}pR0<Z73AKX?0m>#?acuin7@S5QDfJMOTfd|2gApR1-e83{$MR0#U81byY^x#>+)53@s0R8}80K7bmctv1+aKdKb<$+aU#H#_DffKd@Cv0ru4kcl(C9Do3t^yt4g#EyGx^0cyrU6HRPXq4<8wLOBz>&aF;G=N=NEmS^jQ9wf81do2o#2F{Y{EwXi~5KW{{c7(oY3D#IL&P|$5jQ^1Fs71532|NqQLsVdf@eNe|;EnnpelVpB3n~$H0%^zq!+_D-upfVPg?a+{Z_-zloDyf8YghyBjkrvUVcO0-nolNflXJ5he#O2%i9;A9x<OWx#zIa1Zf9ZYz!O(g@3gd;AdYhp<9;4*jJ9+Q2Donea@)G~lV=lNp!^oSyH4_<Rsoa@>;!&m{aFoYLiw`}}cFQlzUm!iys;1Mc}A;ol>yG@g?LX(3E$N>@odlkhum8+<YWOM=t$lOeujh)cme-{F~r>A)#n`Eg%<+~b3ERYrJag!$v1bO=v}u;O@5UZjOEyD44e@Jzxo;3?r#5?BtLo?jI46-8W0a8DULldvo}rK<|=tAcxyAze)o-V|Z^aZg!<mql1*Jf{)TLfF=nuJU*$VO8+#@F@o@4^Gc-iTGL~uDrOXDxOK$0G!g*4)?XgJw=hO>IkonuqwEx0m2&~jQAM0?Q`1*pawqPZI=*!31MRpMm~LkJ-~apt%cjV1M7hIg-<VF3-Ipn=>x0_-Uoajup9V5@ZrF4@QH47A-yi7bv(kt5gv}PiO9!Gq@8d&cwU=?T>^h;Dv#+%JK+FRJ_3<;!ouJ^;L`#aXey7w$P-~|@VemLfWhG1z{7zvO!=s1lXMd11rLXh3rJxu<ncYyPPi1D?yH1+623Q;$5N!7FvOIPhDbYMM(_df2?RDYl}AS8iO?53HFz+vJ$Nwq4B$*tK9(b&%aLZ{GvGtvgcMc}`N(IJv=bgcKIpzV2q(;EODK;6NIT(JQ$Cs??SwhOL*Ua8*u+#GIguyA6yUz#?SWmu+k?*p?pG4>aT@tNjWkz69`_@h@HEPU@-ZIyB)oxq(0#`dejGkVdE7wS31^w|(Gh7UEC${z$mZkk`#=2?g9(51?nUwX2M4WpdjCwqd?)>nxI90aXcm-|=OG{WfAo=ZS6a0z{|~xkT3!'

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
