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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_012.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_012.stl', 'source_sha256': 'e26d674ecccd523f628c94806186ed7e128018bdf79143e062e388cf0a276310', 'input_faces': 559, 'input_vertices': 350, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.43069425225257874, -0.44019895792007446, -0.41468992829322815], [0.4307461977005005, 0.073253333568573, 0.4530532658100128]]}
GEOMETRY_BASE85 = 'c$}r12Xsx@+s02sFCz#tN?bL}=rtnbAcPPiN_00y?-D)1Q777Hqqh?^Y6zms5oItKol);Fj6UipWBBfV-sk?^|9^eoTHpFUYrXUQ&U5$OXP<YMbN0EJ@Ft$=y*2q)R6Dz(VBzqhnx-PV=B*9u9zCS@cim&k4;VDkL-T^K{<(B+v({nZ?L4$$TC88U?lIp*`vuti0(<!Tm9_cx7#KYyI%+_dfzjQ%E5Bh>znJb$Kc-jIpzhA&(p9QeENiP$rmStW?f>{MtFsB_m|53Tood@W?V3{i;Tt<s-F(L;@f|O=qy{Pd`lB4zD0@Sx{yr4tUA{@*@GFe+#-b4T+P4{g#pf>;?MQX=t#8D46zO+Rl{Z6QUq-!Vw=4MkQHyP<ZocO7eM;;@`Fw3Jq1|l1b-Ts6R5#yb`}MxZE~xU_)O#0kz5dcptJ>4EscydAbzO&|P~Nt!y_9#g|L?&l@A3_{U;F<4d6YkT0_V50op#@Lr&8T~YlZk`frPVY|KT-9P!HR$S9^Lj)!k?NwL?+YRe8O10DPV8H!^fa`G5JY_Rl_lO_jIwl*4F;tNp{aO8#8FtNrOpqP*ilqeG~d?KkU>#&x=UlkIn$d2v~lw{NezAK&ln3txM@WHIV#-C`fwaU@)PdvwcGH{a&+2Z^t@KfV{o`>bSK=gYP~!9NiQ-wNG~{x|%4ZNcX$342g}z{jmP{_T&S@%fuYdt}@UN4vGJSMJ6*yz^-{&if+tJp8A@dyxNWui;x}HMGZgcWNb$<I73;;|-*p594rM_T!^>;n?@;HXL`!dKAZ+KYZip{WH+F7jPYBP<#rm`))C*|5Llw7>BV@@J*kE7^m9JEGcqb0r0i8d)8t+4e2F$c-a^8%$~U(^57Uh4)aJq90FfUjzqosh{Y#yT-RTG&lqX{`LuCCZoVVkfB5xgp+576!N{Z5vbBlvb0KDj<ndY(%KcOn*Qe#_Cw}uJw9~w?5_zz#Keioy^+(8$BdiF<nW2wN#(6KyI)TqK$HwD&`d!BS)`I7*LO*@<!F;hUUx07;)|P(!%fo_SCRNIRIxP9Q6(RGa*DmpMFGV};6O!4^4B~s;8wy=j2lLms>)49pUUA5;akbt?<THPq_?dc1e%{5+L%XfP;#=Fs<9Z)V|3&(}4}AS?kd%+qmg71qCML=Ei_S#9To`{E<;qSGe_sP!uij@0uGfCPi}>9_aXnV&tQZHj@-?@>f1PPQzTdmjY3aYJ;_vmq_&4U1M|-SK-r^U%hkTn^Yooli`tfFbZ^1~cLpHx~^p`#VSonIG6y(?No`CtR_h<rN8=G@2>WO-Vb~@H9*@XIhD#<(=8oLYm-g_VUGd@1X{4>9wf%?o=cKF(^Qn+3#V2||g^ym$ehtA2;KUc86ShqWg-|FOa^zW=xwBH`_Vm<t;&&QyBdBbHL9(4u2V_2qB(%(K9Uyf$y;oHMEBA<@p8)aM%+b#9P-yMbV9DNOWGoSR4^3lCzoyii6b;dT|F6GxWSciH_%}zr*GrvxhdeSXK`LI^fzsV29Kbrpn{No2PudNQZ;TwMk%J>WIxgGr$X-WCGH49MhtUFTw(*ok33&nZ0zrCgYJaf<=#-)A-aQ#z$mFwR24Sa3<Y-ztoWRkn@2s?ptM#<+ZgWSu%TOW<{U21(u#;=FeKXvMM_wi%D^kNOpw>Rf;lq+{j^1kLYd}ID^G7szjD(lqpneZJ=JIi|1wv2(#eWKuNhwQSBuNjBy)l=TDhM%LH+-HK~_y3#UV*}PVd#4brC;G;v;xFy7K>3c(ZPMh}2H%RSB=_g9s_#Ia`+Z!6<Il-*pDCIo<8#MU_}UY{DQHh>h|Gfrqj4WF&iTlCw#SD0jhi<3=GH7S-xH^dKt5mgO~7%cRS7uXfL4<4v=H%)Gw4tK)f?$wv!V(AbpOq&yjf1edZkysw?f8gsl~|S#Bs8IKEJdK{>vUq;2*G|eslgN@oiUT;Jlx2%lyiC4&}6CD`j0xx`ukps*@MXJejc(`CJ+#&jDkri2o`Ic{7{L+b82CD}4RZF&Q8A-X3uGwT_uE4)pY%@|;un)FSv*PGWu03)GkUV%AFVjVnXsx!~6!Qs0hJQhrE0)+Mc28rCzbMJnc%_B`)6w691@$$!22;?K&0e%Ho*h4$Odb;116y!LE&&$F@WG1hNuXd}7rybZwmWd^T;uf5oY_S**CK|R)^k?@VHpHPo2`%`(YDANB&ln+mmyw02~<Ne{@IXJF3IvV3}&NcL-Rk5-7Ue6?7b7D}BK6ue=_*Lsq!*QX~SbvN@9pLL8ljV7!Y%0c)wdv$690z8X^}2y4=99jDqxeBPai6wLTm|2XND$x0cM`szl0owPez^Ey<1qj2C2q=nX1*7Ey=z-pujakLxG+YZnThg+_AiAF&MfmdUr+e@#Ex<w*;h-(XV1CQ;g^=@FmqsI+*h?#M{u3SlN_>6mDn*E`d1QsE&E`(kG_kQdGqIB@k@Nbd5u$N<oW8`RZ}JJUu{6S;7Mq|Hs%NM@4R1+Jftm<b-qxq@1YAzU>z}w9h3E8U`z3Bmt|e=5G3_?zJhic1@p=NBrrt!H@t(iH}*5in@jh|I0`K+<u49Ey=GH8)(x#@!X)U`rkI!Zyh9`pJ=;u#j(<8A?O#wx+P~FP{NJzR`W*%8A49#fvrT|+-odfMx2UXJX9LGWGZ)5u*GhWI^(JP-JTZ@IvQK(6M&@V83aq=@ks{Kr)uYj0+MZWqq09e~@sr`Tv~&IYk&^#6GB2tX5<l*kJU{K6l!*54u7GxFS1QIp6M~U9N0h(h$Ez#uD_Yi5b5K72S;_N=t^LqWj|^zHy=`83J~RL54y_Q0`W^LkxzA+J8HIct|3;oS_cxRCe%u%iO}`w^SGK~*(oXH0s?c7Ea{u`Cy5!mXryMl6&J>(Kx`njo__JWNFC-E3RNLSy=WY7F9rD{YITr0nG-doeKhXu{ug#M6YWGz1r?zrbSIny&1!O&{vr5YE*x4PQ$0g0c_3mva{S_09^}_zJ3eIOGUpol@^b+`H^>vt!+MpV8oh$Fhz;Eg=*W=3n;7UVLzuoAD`JO&W>TmUK82lTNGXE~eN`BUK8;N|qza-Dct1HQRy8I^g0ruX_<T;~AZajY)nJ3_RSN9FT{I~rSEaRte?Fq=kyuoOv6(7Fc-PatsrCsl@$UO4>i1o-E-4xG1`mPqZUL)n=RMbDQGV*CGp1aoF*X)OT;PWy)rTx20%l(Y|Q!U%YOYXjFe`?HcbQRZ`Itcp&*Zx-@8~}CsI`_ZU$1SqI4l210%Kf#i&rA89%jf>u@utTOjEfHk;JfzkX2?`|KSJNm{k!eLCzQ90e-5C0c%(d^1WKMA+e+g7hyLqpd9J=V3hR_Uu@ii4R~*V)jSJv;+4!&y?^kTWe@gih&4vWI`~NJJ@wqhx^TXI4VB!1+x5<7gUryWyjSaKl>zm@`J%}|0<3@kE6uxm%lk#yJuwQeOTOsv~oh$uyE=cx?amU4f^jO++H((*YpKxFN%59{c<J<8(;P|QPA+*z6DE{w(c&^gIV&Lm_e~|Vx&%6kEY@7n$i1=ORMY<*i@>1X+e8<BJIImUa0iF{b(=Nfc*L{L^>VH;|_Y_61OZfuJB|k3<;C`a(+0)QYze6&ftNUTS)n`_NZ_gSl?Tp?g`|fYs!q;8CnS%SG{Zvn>=R-2uqwm`&?>lBBO8Jy&a=$aS$Kvy*d*B<_4cQkM9vGKK+r#3Qza{tO3_J1u!J795zLv06&ikqp_MeX0#SWwXH%BG^J7&o9bwGFcwhObRzg~C4{><KO5PW;N-cpbM&7P?LK#bHAu|?YXJogxUzxjTtXW=?|zqT+1?>FqnEcjZ!lW3>@x)IuMJ^AVgK7Tb|#`%Q;*vIG@io>_&?Blx80^>oiP#(U%d#?23(-7H5mS_dvQ7b{lLzyXfub@pD0^exUQQE(+;e7a~4XIz-je3lHvD;-_juXF6nmli5$rxAK+%53UvMr>ZjCHY&S%KM(qI{|Ka$N~G<o(C&qVSC;Bc=SpC_KN~M%9LIZ)3`MyFXF(#n~pqw<U#09vXC9gX1O3rJk7%*|*n!AnV1tMEF{#c*+0n@^~(^mY#ucy5?OCul>l^U+1L$JsTuHmmXoi>F97<%D>Jg=iPfm_W6Dvq<r<A=Ow>W<^9<4EXQ#E5yRzrb4SU(>7_S(BWEwU-d5E|Kyx>QZ^Z=5I6vP--p4-d1K;s(gS0>M&)qOS8&89;H^?aOM~5WH`{B2%;oAoPBlG(DNZA*yIS5~S__dt3|6AnWm|FNJoTtJ9nJ@h!a9%yp7ry1+LCV*Q#QnqGvjTkW?Hd^np#jK))!HAvk#4H21G^IN9HJ-Hf^RQzAMJO18jbO0E(@0W%h!_p+zQA0LoKM4l+Tqa*Za(C7V6D6Qrem663%P$+K6@EUUihTXX`5I$IrR&zQYJf5P#Yv@dJ;``uJwA`0>9<e!Lu5hmB?j#qauDu4`s8_PvgEhs59g0_7cnCoul?GdYi=J-<yt-W>Zhtjk)h0QmNF4P~5M-;ecNI~xSwad@JPtEVfm|FIuz1m9M$9nNc?cv05t_I=^&ALM<Cqvv-R|9Xwl;=fFj>#C3*>xCnFtoUVL$vE8HTkbbkr^C0r7fJa()v$lIdC!EeRlh0orT87}W6VQ|(*B0AG9I3JqkgN+7HQ|DYm&E$ck$d~-@i|;YuRR5f6{7V{9AcbrT){8Wc{4n2lLwA;*hknW;@hxx2nkX9%^y|^#%G!-aaqJzDe8P8NOpiyyVB&E9-TOZt%5}QzV~T@7VFZi_!3{2X|#%dRAH1nWvNC+iv!g^?zV%%y%vS9QgXH11PUQ$_L*uZZ3S+bCKicJIJ5Qcm3|5M@C-6_lqxuZ|*-P`3aeZ`?Y;|vb6K<0+|;L9%22lEj=scf4?vJ*)(qy{L}BGJ&T{qyx94>ycZu@@+5qF1G%nw10)aEE5kQ#o{;=3^N{uZT^0DY?%~p&78xzcV@;{&Rh;B4wl($>+L&nZJFb=Uo?a%;d6}2P*9!EO_j-%}#5!YoC&D*J{vg*Cp4t)G<N$o@?isnR<#{Kg-n2vFAG|8_I&Zg~Xiw}tX{WIX=e2jYW4$#V<op@u|6EVT)%R6#y|xz};X5`D5kKoX^sggtEPS)&GF+E+?TS2)7Mld$Hs+A5t9PqoKH3le__O=G(CYjpdAN}%{;qv8@5+VkMfn~Vr9G*AW&Hfo5x%~~A?>M`AkY89YRmIV*ZikY-e-rbC#5vmXJ2muU+?BG{gOL9@?hK4624Yc)-lcNz*=|TxYa}QziSkpUu{#m!?(Julj~g-D&r(+yVM`j9QE7gJ(TC;tbf3Fgl&`Ofy~SCyrG3<JdOGW$n&lJ^EJFLvSrUN{^hwcPOAE+xcgd3Q{JyF*)7k1`-j8Vxi2vO+%CU!(RckWW{oO+1^x8f7Wh^~U9{6&l2@KDlT+Xu({!}ckxTNUJ=-nyZ#gIVjEKNGV_RM13^abcyuW^Y7X4xk@q_P(lJ#6K@)7qn`>uv(WL(db=Zcr-abGqMHiqxor#Rxn<o8aO&wYyBI}PpE9}Ix6J=D=JwxmU}-uh0I^WJVPc`F--{99pf<-FY27-LVOewXk1UDA;?2>UEYMD|}${}~Tix8pkDdi9$%;2TvZaowni^O}hf@Ew&~%l)y_YMfW^Jy+_<^ONMW?oQ;{>bytF=NZR+#~NApD!zbk>pWb>73aH==84}|wXCU<x6t|UwdMuR;rwAOrJnIMWPIEbU+)qs<-hJP{rz`A__oa*WSp;`1mFC+u#~^jL&~pfE&biKE`050c|T^Az9QptatM4Qq?y!H^KY3ys~f?$-jxvlRE&(L0Zrt*{U?flHxj-hvb3z<u5~`ehW)t9cW|AzpUxupty$;rJFV+?b6cNfcwb@9PzmG0^}Duha5&y4xO~&~yZrYxv0i9@T!OE;##{Z5^8SIo;o29szbETg?~WK3y6f)>=1s-^-Q`;xKgOmQ<iX5RM}B|ic}=!cU-nLZ$7cOzU-6B$v$0>-SiepA;s5s67&!*yKEI=Yb0_4CESk60Bg*YhF_fwPx%9vPQ;gnK|5tyCQLS3d|L>n-v~jkfjx$<N>ylfL!>EDeFmedBDmjE4O07XwT9X_~Zpcs^Obs9hlWQ{+SD{uUS0R^WC@xGbO)g9>NG(NHT8><hT#TW(Jhd`eX?yYpXKZ!GV(LcnV)AV28uD!N4C*TK4DuA}a`F`NH0o0FH1bsHeDYNCWa<y($>bH(_2d=gEeyrmoH2)*NL^1(B(J9aKweEAN1aa|N1jeyN}f($NL@}|NH(df$R>Fmbq#qPc@uRbc@sH_x|N(n-t3II)V0*D<gM)2wG728oiT|zk-C9AkvxRDm^_3$fI6EzfZUHdgWQiikUE7tkQ_suMvfs5rA{ReB@d@gCJ!h7NL@kxk(@x?LY_%oMBPGGx{bVuyiEHtZk90=k7g+Tj-j|0HIdwlJc7EKJc2xmI*vSw+><(;+>_j&x{%zTJdA3Rhml88*O5n(<EWd+apVcqB=Q9Ec<N^IcyeFu%b4rSP~4KCxGO_(EOjke=}K}e*<dIhq<tBqikngEF%&naP9irax1vrYw<5Qr4k5QAM^XonBgt*4{m5;}9jF7z9mrj%G2|}fDC$sh6uBF9IJq0S2lYpC5AtAY0(mfbjP_-Gk6|c|c1CaNSn5o&(naL4<XO~Z<XPl-)Y0T6)OhM>ay+>^^*eHRvg>}QIGEZ?`*KfI+>km#`*IIe97-LfeYwvn4x#qczTBe~hf(`$U+(FOTTq8-U!DOJx1o+Cw;@MR<H!-@#?%Sq#^grS@#IG2AZlN75V;byCAkvW&l&3R$>xl27>cV?{m6bSU!B^O{0-Hg+Li22ZbFSED>cYX$epQ!$gX+VnW4BOL$NQl9@&>%grT@NwK=&s`CDo$^0(v))OO?w<Z9GNay4=-YFlzGvQF(l*2(p$UC8yx4X9D%2IQvHZsexqaB2^7IJq@-Fu66^P8~zGlRHtP$(_g@wJ-CzBSUd}hT=X9#otrMl9kRPe@|XOokw=fZN*<Zql`0roKeCVg*5fpFX}_~VHw34osr2IIT`t#v0dfX!#OUU(T3_xZbPn4Rb{L5Sn*DNKR<aVIWILQIWIW}H4`}pIRiB#IRiO8^(%6Ea&~9zaE99IBr_D}qh=>(XZd{8jO2`LM?Qw)Rvx0;$x78Vx8k+8BrEMeR@$1}iX1_$Mvfrop{jQ0p(c})*$&0|cz(qyKUtVRmD@dT`Bz-eLqc&K4++J)R9)0u)IH=qtSc8aFF7yIm5X`H%zP`=-14unf7Cw@xBl{Q>r)T6y0Wk>dC1wQ9^`CfPpU@tB&VZhCZ{8-zunJG^`d4bt320bj+O4_cu}#NV<a=L(~Ig&_GTF`#%`V`H#vo>>P_LX;@ZyW<cxOg|JLMcjCO2OU2<)P;z(*IawNGUwLQ5bxh?y;E&IPM{dyc5^*DFy(Ra<|_8hbAS#JkwYqG0e*SYGjEw!oYS|jPFFefR@eLAWqHHDnQvFXXa_T*Ubq@RcC8nY1``)Up}b4F8VgfkR3aYl0<hf<r6o3KnMLva|j8Chuy@>k9%=!^o?;^dOf$mEO)48>m5dz!Ep`7egz2MonGoN>|_SDbN{dV_qHe4BcYtW=%jHjfp*qn0GAP+W*!IdUPgAN5<ZAGwq>3R6o^za^I-mt`ofL@h_IM6OINNiNA8Rc0uzLiHk7As3~pd==%fVowhV#V?u92jrLJyVM)x8_ellhT=yI#kZ&@$+yTCoN=6*Mm<SRBOjxlB_AVSrrsvsW`A5}D1Js&{qc;)igU7${Kz@UMX067MaVX{KC@Btl5OPt)GXxu<ZRTBns7GqKMcjsopFcyg!+;Eg#3!C>Uzav#Tx6+OV-FasD;Tn$Uf8(WFK-dYFTmvXH;}XEr#Nn)H38UEL)RWmRy!&v?fEbKeaO1pBzZ7LJo08eP;wv1Id9b6F@CW4j`ANdXjyeQQjH3sin!KStd6_@n?>EHNF-9P5qOh_z&t!@=K2OKNyOiQXi3@lHW5Fzop(Hza>AWULZdv|K>JNeq$)U>Wo9q_{kaj7>W;2&yf$14^yv_ud<%Q48;ejY2<@si+YS~k$<6HCST?p`-P$SK2^=J`#e_c!FgAN>_N^)wUKR{OZgazGg7mWGm<}Wj;VR|fuZ;fL-A|sbMkBQL$`VOkoqh6A=yDaPj-;6QBRRCI^()CPB0Xop<W}OA^*%!e1v+6e1yE0p?E(-aVqsZ`8?Z~%20fidWU?Je46@%e42cT`igvse3Poymzz9R{5v%VS%u;kR3EYm#h)|@#aa1zF>+RNE@~Na8Lm6I7>Wxr6c=YGuE9{;kfAu3+JM}EYfUgiabssRqUzKTatPNNom!e)n(K?=AZk@=d2&_qH&kEp*VOD(U$QUPrtDO;?qv7)vNkEs%+J$Pm7ku+ioc?!^AJ{%jyY4Bfvi-mO|E<@cI8=dR_a@_(#P7D{(8**3~%C*&fD{U`rnVg{4+e%f8GCQ<p2EUzyDO`{>>kpb^Ysyv+yPv)ZWqgu$vAq21cu2p0xi0uGrK%'

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
