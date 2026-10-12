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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9f43d0ac857541e8a3a92e20ba284c44/part_006.stl', 'relative_path': '9f43d0ac857541e8a3a92e20ba284c44/part_006.stl', 'source_sha256': 'b8c4cdf8a66784e60a0d3c20357369791da5876c55dde73ef3704f05d1c6f432', 'input_faces': 648, 'input_vertices': 403, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06614961475133896, -0.33493006229400635, -0.048465535044670105], [0.08627773821353912, -0.041067659854888916, 0.07397451996803284]]}
GEOMETRY_BASE85 = 'c$}r22UHZ-+r|gf1XQe8V;Mw6QL$k|)QQ~~73|$b0R;;xMFEwuAlSi5QCthfh&A?DMic!TTkPGqwpbIBXiU_Y{JHP@EbQLoJLfy!$2sqLe*18_b7%JUI|sk+g$lbW{NtuHJL>hJYi&glQCx9VqJkzzgp3Lb_nI&<+CeErzWA}~vY!2V_ziMUqLf&Vz@YF^lRbP?58vRH9`#j^;IPRNlLID<2%8)jB>c_+<HCdT{O~aW6NB<T*YR%Dw7%N3ZhdvS`hWZ>npXsq*URlk^3+na`z4`9$oF&G3BS^F@{LZ}7lrDVThA80GW`ts`Yspp)r{gZgl~4;$9}!_<ZHjy9Vb+IzK!$wxfAFAHg|xnuNl!7=<gofkEDF|WRkB`bfSDLYaFKtHT6v9^jQ&<UhB0uj(*=^3Fp7+)_MB7o52$)pIb4UPc1*Xu3An_5x(U_6#44=E0o?Gw_+CM7amN$>3%L<S81QJQlwY=n)tr%yK(;Y62gS9z3IW}PgWt{Qa_&aNomdHIah}Bar<sLJ-0?4?3YhIN9l%bnMC<tbmjZH6VLwO4?30aP$~9r&Y=4>*DbM3q}P`@ae0pRqx;gAj9X9T`R4RCy53F;mB;w~S~8_i`<nf@om3tp;Osi`t8OM=%b9zI{IgwV(C6<$*pKtz`~8r``SkW@e{4m*uSG7Dk5=^VR{A_;4wX|m>u(mm@jQZjz2^`7d`4!hrRNY)kNwhXIG+XglIZ$x%8+k-(ty7g*I}IgY*F$p9~`;9oqw>D%2E5-7Se@bbY07;v&-pozoX<U_s(-ZpFdwgpI^mt`mGhXJU1tjueBJ!{)K^DPwoxQq4ImwV1H9AeJ|>b(v-jcg)`@0d^gwg!MC&N`8e;(B|l;sJx^ucBr2y;a{>9LKPvP6j_pS2wKc^#ec=TDelrheQ9dCVo9Q~Yo^UzS2a>Nu`jT(tH01C1bqn_On_tl94Y^cKv$HSxmKI~k*CuSC^62o5u2(iu`gKXCDE}rM$u~E1CSP}-eUfzO=j?}W%b|2{$5J_s*q_#trp_f_zi^hzQ?;L&u0P+Od?Uk^>(A!nlwNmf#p$2yIzi={<j3W2Q;K|Lek7G&PddGZe!u-#Hhu0DN#!>+7?Do--c2Rn_<6u_`hAzKl#f=V7^m;=@(q1o19xXq{)xY4QT}HJ(D!TkEn*8j=i$%DH~qPT`?oEQ<ZJb&k#9Vy!2OT9JD2j=I*Rk@6n%{HpICPzJx{mtS+@0GJsd{qjrzMX`MQtzIc)PG-((IZUrVh|zNvF<^38Rsl5fn&<mb@12K&Rl-bkOjW%2h|r5gEqIe+q%>GSA&)Zm*+AK1Y4YC3(73i2^r+{rht@1W;zx>K6-*`B+e(*4kno~O3)@@A?(Ek~`l{oYLx&pF?v?bq9W@8;*;C`Vh)M=wXuUvaNR`RKXj*sp^65VVK$+4*oCl_xHo>+SK?obQ_><SQ>y={akko!dm^8MT4^PT}+%)U}1_v*pVwq}uDEM=77(y{Y}GBRf)kRPNS1Lf7$ZL+#GorWpHmr|l$twqrb9cfcL0r^-r?FX{98C38p%on=4KlhW%RkH*k_jf`c#<R<bh9p@!c{b?1>_5FNHP9N}+#!aJ}C4<smZF&&xi0Y@-xD)w$<{v0e0*yPy{F<D;U3uzv&9C-E(BF-y!v4e`x!>*a>QhR;;uy6X{e7kV^nIPXwt@0bPbOd4`heQEQsOVSBewp<kGP%={nMG!cbUoggwE#Y@Wi10+3H*Ku|$7}wDXaV(cup&r*dix`>DTiIq!r`rFL}XBld%~aJw5Fy`8SR<Lqkkvpwm4ElQ&V@`oK_|IJwPO^4^rJ!0#lJjPdh!|l?eJX(LB2>QMjEhpcyqc`;f+RJ5p-BQyyecGell>hftd0cxOPQG!eES1wVZ91h_+@4ZDq>j{i9+EuM&d+~7U;aJY&PRDHgVi~d|A%dM=}pB?^L<%;Yx<}P<QrQjkgvD8PwhxgpUveTI-Ju_?L*H;w-n>?I;k-E+MGIe>GkyWX_Q~D)zt1x@Qo=UX}0AtUkhAp=c7EjXC(Q0mPWq*cH>U2&j-?}Jay}^Uv4$EQ%e#*A7jwpsg%#H6rPXt8<$M!TCX7A=o&};n1S?q=Didu|IG;M$5d<i{V$~0mQ$-2$oW`(l+)z$j_R#4vTcfOz0y`r;r8{g7U#czGml4YCh_xB(^uKGm&mQl?R?~KcFSP@%zXAQ_*4I>R%*%jTPu`&y~_{WuKRpOpN-qUuOvO}#^Y4NzHL-bz8T8?%<(**xsb@?3Vfy9W$F(tXHIXW>zdukH(x!+{i=G3(|`Al=R3W+b9>1e%-8k5&+{F(a$Fx?4B_-QQ^+^wMDRSv-G}Sl_9V{d@)+t@El$xiJ{m*y6?XNuh%@JJ^{vnU&`K(w<ts0~?q?A^&m7{nf$uMr=2J?A6VyMODkRW&p}ve<M&)ylq<&IaTb}xV^Xrb}D?z9B(eH=w{KVv5h0|ATPVHB{+mZS`wUi&vztC@+&#N>qRW^lFeX;hRMuTXox0WWJ$#(5`-pN!u-`c<3&n90#w_~wgJuLGZ*L$mP?N@t*a{IYkjs3>=_`04++-_Zi7xMS(O662t`%=H7?R_?z{5zYu|4H4pgRUFdg?#J!!o18vz7kuWd@b=a?%yJ#IQ{i+XkDTVi{o|H?2<dF{<LmSzV3aG>VxLli2S^9Y9^Hf^MA`2U-tXXAYao`sh$|{^}X+Dy`n2AXYBmS(c~LmG1RWjR=@ZHTDNIN7`1EDbdCKx?zH|eHsx@8RO+z**N183pZ25nWemT{_gnjVEM50fEuL?<1+(8}XAJ%Q)W_6b^!-0_zY*>kZQEYd?|blk6uuFec$DjdFZbt{vZva%7mM$oJilCCc&crCu?)XT?MN@8(mK^TKQVb{^So{M_fh26e$Vreliu8ZV{g#-slWbn7o~sKmgWQcz5eW9+_I0`-6)#RXvyWsS7s(qyHMjpH{1Dp9k?G>s?&N<+5a+}{Eu!>eKXyQ=k?S#i^6T|t={I!8av<G&yUL`Uys>7!8W~`lf&bX)wkAjm)cyP!`*q^A9;|k+j0@rXT8_7K=O0W?4Zwy4QL*tmNaObG~X|Bg?|5V1I?=~f#-Srj44XKzIQ8?U)yUTUxlyK@ajW<@B9n-+VYa*tE*iTZGB})3G%h+E-P(){nwY5DgP-YsGrf+ZKUy8{dPC`CO4k{TYX~$?+<9lKG|vKqdgim1MGbLF4|o}mYuKcMY~&g!_K$XPd)lP)zAF$pgo%JKDA44t)H4>f?axRJJqH1`SrGCP_|wA_bbo*TY77KHczXRX`5cJ8_nbO)93c(LA%!fdTIY0HfB@1wnSaA_fPbqc5T@lYwugzb*&FO?D9vuRzf4}d?j`sx8JpUw%hq=cY1E!ZFc!b#q;<QGQ#frwYEF+ivf1^A-|n|+c3-id*pU!IZ$kaou6@v>bcgiXNK)_v$jWNX13WbJ=%+Uw8Lt<^wxRE{I==;=9|4&uC>d@I{yCjRoan%@l~H7N^gF(i~R|_FQ>$8qUULTQa+yA-`(rHzm)Wdo~Nm;2m50OQoAtTq|@^>E@Us}cIr;;%e?*p&D-^_otMz>BWjRusrz9CrRx^J>!dqXIsKw6Dv#;qOgmqjS<R2?{q{CApVdxQvg;p=K0hs`@}l1`r+1<6OQ}_X_sM32ali5Y7?nqTIgxxVdII+k%5PL2?S(>W3JfLRKzWQG8k4WXx6I=5=v7-#|6wv+qUWF{CiA|*(<JisUcp=*ms~2R;#hwbsnqWo4|zXQ?k7zNlT&QJUu%Dx?@Rry>2X}DZF*~ep6^Tjxj8T;)wUj5#|3?fnS9M*06z!+HS|19x9^d!CQYUL)m%fi+xqf&l<!O9k>2RnRNMAt9oH;Z%cR-0FY7p1t8bcZ`?Zdn#*{$zrEykWvxa<mTsFp?AYUHGwX%=Nm*)dkU!D(WPThEYBh4!;aZAaU=OO0bZ;>z0TTEfKR+BHybF|iR<o{z{v~Lyp`tcV$uY2Xm`4qXq`AG9COP|U-ZcFnq!#sq1dH$xQFC_mT^Su>^I3H<#s6G6P=L^z&QgLdTLBE&gpK4=`{C~_>FD8>O&u=XW+o(QTjy2}?>;EOsmyFT0E|=%Y#;YsrOY>@D+q-qP?ZP@g&-bPIxw-Fy^|tA)^Z$Hbp8uC}qW)f9N2nd6*q7EFMvvR%%j*==o}W3rw5~ClI8*;2uY;7#+1#&4>n0`b5&7~uOAjrPX?tJR^;*6!t=IJB<=L0keafcFnYQgKf1McEF4MMsS=W{NhVGn?ybgUcgnV`WE$UCqCDOP*DQ3#FZIAiu*^FtNkF@?Zd7k3($m{5yg?JxbT6e4K%kqA+v`*Jff0AYUeDc@(R$p50o4f*e{Fn9(l=0&^{Xg~@_Sofb-LJ^^<^75hM>v0J-@|gfBJE$w`y|Sf9^}jWDoUCD>|b%>@p{{HN^kZX$>$Z){*1O{0{hZ_j`GK>Y}@i%_l5F(X<x{gx0cH(?JsF_&hxp4v>#;(`M~)|`&XuAMQD7G_q)tKwR7z1Gxp8$eQDoJKhqxj!S?%gR$tz)%lD=II>RfG&xNG@K&|7#9JD{X{X@&F6dvEC{YLY%Tuv|TXXg9TerCQe?Pr=@cjwsFH|u_>o^^qJX@6B&=g9qsv>$7}%j+I_zt`%^`@Q+TwBKuXu3(qmy3d^NOZ&{q+=hHzX}?+-H<Z&$``fy1Vqe-1H(#E}`AGZcO2A=GFYULRuYddnrI+^SwI7R-FYo6YhrHRB_WzB?zU)iq1?K2M>`Uhh+M1>8OXm@mmsrP3=NFc>zi_`Uop%_GOYnJ=bUvco@ZxhG={!Y!GK$kn=P%}c3)z>>Ym{?Id@dxN@2D@{aeC>TNa;3-_XVYMC8dWG_0#e>l<L2hed*jvOD#?Pw|vf}1&-x)hIB5b+}_3OIq4kDa`YaL0}pt9u074*`GdCuw*%=s&g|8Med+v88|cIB`*jJ*$6~He`RGl9cz;(qAJlrR=Kf4NPc#C|xUT*AqZ;MJ`*YIyrsms_=SR|csFKu<*Sm$^Qa+}Y2YEc*+KK%SM|dB@vj**}st<aRFQ3C2p`kl$zhCRQt?AMXo_|T_yn5{=NZ*dHn;w&9>uW##&FB90u+EKH%YIxc?}rRq!Sl2yo4%y`@;J%gOP?#;PrcgAzI2{$ZoH3t`TX5H#30`oT9og1)pp9qy#FGnm(KBZ$9wEQIKb&$VrZXKt?-C_>3smB-!ELAzkla^svb|I>z@307x~hA1(rrt$d}(k(C5@AUw&`FvY`q2`tbI=?ruAM5ncD1FZ<Ga5te68yXm^}`x|X5k*~%drTbE@e^2vNb!lDljrK)&eOl!JufKLQB>x}pjqDl8`TOtXd4lu#LG(P0K+fmKgX|w(%j-keNb=?PUQDCoIei_4=XIHdc^#O%h|^2&)hJoXyKSGdGS#R-*L}E#?@M|=$9TJr(@XF3nA>mX>t5f-<xDTMfS!B69`>d8g0yk_$d}(E(l4Lk{H6Df45w?HkM#bM)tBF2GBvr&&slm8N^NtG(<i^@=O5!UkFJ;giqlK)Q>iV=?4j#Q?_X)3mnYxueJww`x6smJ{*16x%S)0M&WfuN9ANVbnlQzWRsa1Jv=HzA)hlSty<7f&UqS1dSB4gO(HYtl+!@>fAy|Vp0c+rP(1zf4;I`0u;I`m4P)~3hurIVO*caRyS_j-3>;v@x`+!?PYlB;XTOtJ4LI|#i5L^lB0T%iRxDvQ5v^=;hxHz;VxHz~Jv>aHdJGd0s4cZv&25toH0&WEE1f2u!1lFM&z&dz6^eA{e_y|JqE9kG_SKtZ`tYsaTMF{Q#^#}I>2SbCvLMMTP!I98e;7IUX=sfUT@O<bZ@O<zBXcBk<cri2?ycoO?A$Tct4tOaz0Xhww0FHxB1jm8H5rPAuqridSRtUjup(DX<!7ZRBa0{?EbOhKN+!#6x+!)*tIuzUx>;)YH_5yoC2ZKGq9?(Hx4{&YhKyYnv4d?)H4RCd6KX7$$RfOOw(B9xG;POyEaCvYUXfJRXaA{~au+UE6(%@3imf%w0lF)kKlHd|~;R1Ds)&skP8$r8*g?0xw0=I#F25tjx2mKt}4%`{q6Wkfx1tHi6+5_wZt^?J;LaTx6fGa^i23G<*Ap}2CSRX3PA_Sj@o&yWr20jno3QYoU1usDeo&k*p&j5!(`-6pc2Zw=&LO%l!1^Xie_lABB?hPIU?Fk+P9s=zF9s(W%^#cnX4;}-K$cy>VdC>9TdEi8-37iN{fc60=fagMcfrWMh&jrUryMp7vGohWqGr`lK9l+DTF$lp^p&EE9I1<_p90{HTZ3~_Ro(OFNo(P@*^#xA=heBI}L%|_XA8-hGG_)0XG<YPmC3qw_03o<Jv=+EIxF$ky1!zTZ1#k(3;L^}aV4-EfrNKoIf}Nnn!A@WoXeqEzH?Rx1I<yhEI@k-^3G4;#2-U$I!Ew;_;5hI)=n?Qb@F9fY*U(qs*Wii{tYUsp5h1uQv=6v1I0PCD78(f-0Z)O>1y2D_h0X_01xG^{fTO{&(8b_ba13-II0hVr5F8I(3XTUafhK^LfM-MFz_Y<KpyA*d;K|TH@MLfRv=ul2TsJTNR9Fk)b1SgWw%|hGBG4A#BH+SMZ*XC-BeXHt5$phM2zCG~P%p3o{##-71d9;-7t{kRLhuJ@ZLkQz@1ZroA_TuvI0V0iRtJj^{0FouScKr;p;f>l1iyin2a6E=3$zSagy0{crNJTuzl4?oixB)Xv?N%B;Gdu+z#;@cQwruEf<*{^qHqW<hTpq`i-A>WBd`jtj}Y7p+6LSV+#1>r+#1{g+8Nvd{3)~x_)~Bbs1LXaxF)m?xF*;YS_$k5c7{5Eg^Ia|Gd>IcL18@){sDXeAvhPh6`TuR1YH6aIs?22JPR5Io&}x^9SWWd4ublFgTMozy}<*(eW8QEeZj+^L%_qpqo8BJqrhVkf}@}j;3)6{rC`3Y03rAbgy2okdEiap9B3jq2b>8_0B3@;pmV`l;B06-I2*hXIupDRY=%w)o52~-7;px74Rk7a4R|#)61*Cmju4y%odiw;r$Q%!Q^6_F3E&j)DrhKp6?i2y1iTWw0y-MJ0=yhL61*I|6dC|t3Qk4{9t>>`9t>^<tqE=hu7MEj3atQk1s8*s02c#WhXBEj(9&R`MZk{Wj}U@ChB|>i1{a08fQ42E7X?>?dV#Bf8$dgP8-UwG<G}5~)1m9Y)4^+@hrnyWUm*nl27L|w4g84%tC$acf)Lyv+85j(910Bq3!MTE1&@VJ1&;-fhem_PgC{^^!4tsapfTWa;L*@1@M!QDgy0BhJU9ZZLzjSca3XXzI1xM(Is-ftJRLe2JRKYc4FHFMhePXvhl49S6wH|_LtlVJ2>u9qA1p%fb9i^a&%qC%x4{p<7U)f|1$-BJ1AG_!J@h*G9`qLUI`|fNCqnR-2*JCcH^95VJD@kgJHXqax53-NyP<c$yTN;)_rZI>*Pt)J*T7eye}b=quRz7z^a`{HScKrc(86F5g7-lk!6F3jhdO{o2tEK+z#;@6go^p-L4@GL(7(Wk!3OjL*Z?1cz6T!ze+_*H{u=xZLhy0uTkvu43Fsf-6X5?qe+T~ud=mNwd=mUE^cV2A;8V~a!Kc8dp)bLw!Dpa9gU^7^LVp6E1%C&92L29w5&8st5qudT_$gG(U!UT$;NlLfD!4e<4O$=U25x{5+#K2r+#Ku+Z4LGXcZ7BTcLcYGehO|6ZVGJzZVIjitqHCLE(di5mjf4tI)jCZ`D;;p7W`OYy#Rg;zJw6G1)2-q0$vPV1Qt3Aycj$iIvG4091aZvhl7Km1Hi%HfzZC-f#817Vc>q?;m}dw;ov~%Sa2YC976CEXcTw~cp-EFcp-Q*^b7E2u(ck3fx0PllTBUSgt{y=$EI%QpzaIJR0`UH;4{!HrJ(HyJ`K%Q3fh|BQ_zh{LE9AkE!3<Ov}M63p&3d++ZX&F=o+P<uMm6!x>_mdTLd46rYi+~kzi|oCHQM-no`iG2|fl*RSNn*!3H!%Dd;l=ABL_{3i?>V2cavKf<9UB0q6>)pbr<kAG%yA=<@~dgDzDH#t6ZCp~*_Ym?GFZ?g(B69SmLu9sz9z9s%}-)&P5hRfOO&P*-pnurst6*cq%q9h8C}!G#fm3qc*hLO%i*0#`-|t^)lSTm@VeS`;j_8n`OBKC}V2KKN5;d+?{=Sm<=HUv~#b*Fyi(zi27=(dmY5|6z;#m-ff%wtqP{FR%PVcE9dL#J%P{6h~U9trNSS%6|cuPRyM'

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
