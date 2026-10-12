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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/74c05ea2f5d64357a75e4ecafb9570f9/part_000.stl', 'relative_path': '74c05ea2f5d64357a75e4ecafb9570f9/part_000.stl', 'source_sha256': '5cc5fc595bb3b402032209f51f939402a7e9475744218fa41a0fa9891ea9ac39', 'input_faces': 580, 'input_vertices': 549, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17668487131595612, -0.12965768575668335, 0.21276023983955383], [-0.16841381788253784, -0.04953960329294205, 0.23638007044792175]]}
GEOMETRY_BASE85 = 'c$}r22Xqxx*ZyY`N(e1L=n7Xr0un)_ND;X-=@2@Rb|bx)PzB^tq!;NuT<N_xsTTyKBtbeN!WBUf=|vDkzO&DM=8(<Gf35%eKGu5H^Lw9nb7t=3o}4{r2BT^RrwF(B&wJLhe2qSSUc$0S>8x<8fBQatJGX5gTeL^7LADj9bNb`>^m<L|Mn&6Je`|0=yY{hd`$Uv;MSR+!OhlwBqC?L<efz}pXw$P#yY`fS9@8zhy~<-d#q?^g{&%5LCCf&-N)(QC4R!r5|AeYja4lGPWWRDx&+e<p{mq-4s7U8lWr4`u$69kfzJ<=ci{|*rt*)VoNpow)49;i0Oh}shhfLJDJNCZFEqfT}EpN*D(>-+Vjrv{IZ~QXZ++Q(T=l%@0MeZ)ygzJm{E$feF;^PMYA#!iFjGT|TD00{Glsrz_6SBVXgZ;X`?jezTR-e|n|JFW{`!?@LHn&bM<^1&#dH&rO>D-&|j6CkF9DLj-2jy{xh3VYNyH(_YxL5o1-}`rktdG9I`He;Ld|n;Wxpis2ybdW>C!1Rr=IY!(d$Bz3{;53vuJv-9KSOoyo){<3XH-hg!=}og*OEtj^*A#|%HyuR!1?(h^7_=@p>u!l0rI$^i;~TKg(vFV8aGUilX(=6zh;6Q=ici*`aFjYmY?_hGtO6blb`GF>pJ&;<B{jTDPHH^9?jqSUai%+)wZ#`4lSo9o4ba5&EvaT$Z@g{;_<6=l%LoAXtzGktj%P7;oF?gttrp5<^`R5-~Ck92k+OpuT3d=J}csM?tf8C9yexmvbk$`tj?{>W#n<YbmjVzRb~D3>$~*vQ<aqGQ}n9NJ;mRbKbN}kI`?PDDaUELiN|>sCiAt^b#C2BC+FkVfyw6nGwpf&RaxZu_w?}i@p<L=bAJ9_j~ACw)(=0Wb5Fh?`MG@ibnadLBwmcuV!6)!x9*DE_un@<w?^F(c_3BSWOM(;FF2q7K;+&74SD>%|H}H?CwA)pf65(^TceL~zUx<!dzNj{xqtR4InKH{T<<+5KUaf+I=A{Amgk?=qw_#tnY)VA<@yrwG7qoD<2Sh|k9*(0Ltp=hqw@1!+^KWVnqBg9Jzu7CZ?SdqI&Yq&b6@Y}^0-aA>)cBJogBY)!(?;+(2ATFSS82FS&qm5e4EJKmA7oy<K<W;^CD|>?x`|Mo@cE&I`_H8%ledF9w*HRc|I%K=-m2msH|^WJ=xqpq9o^gM#<xLjnujS%D3|8IAhs1J>EvI{JbCebnYt|E61rnN$38Z?d5Ts_2K##t>5}yHP*Q`D_Z^>x0g*e_na%p`MMZ+++OeTaZh%a<IkP9RbRL7TD^50rg0u$Pkye&!*uRnRaw@z?8y1Fa`HM`)pc%-DJ{Q0A(6@ER-v4nSF0e$`5_CB-?63~=g!0}+RK)e=QC!E&V74}$njV7)w#b?9(mn1L~}keyBw!sS)E&XGt1+qe=pfQ5Sc;e?$WvBI9XHi_{|H-aUKreto?&*^7CFA#Cem{^5^(Z2c7#rekuA`_ttux=YA~mK(nGcx5Dm=-11~eHuny*bnZ%gDsq3Wmz(r>4{UiotM=8o@8Cl@{)gRk?*II{$USwUd7R_tWqs;OT%YbIc|NOMI(Mx+E^=4<kYsc3sHYqCarU2<$L)Ss=hn3=@^j7VpmX1rM0wqc$LQR9Wxu@64eIGUuzQO<ZgdIGm#&fdhOB%(b63do>G^a+a=Cl`Nu9fzt(VuwyI<#lLAzxACp*^b^RK;HUY|58*7JN{AU|*Q;W`gAnj-7>M(Ny|HC7%sMVQWA#Yc+V7k+77a=E+FR-JolOpwPNw~Fh#&X(8V^8B^>d_El`>oZT)xv%3unK$UFb62%)^8CLn#p8U~PM*)ICu{U^@_FR>=Q)&Y?rs&Qb9bPFybi@C>pTz?E5{k`U9HdS?3c2BXFtxJ`%vfn|E{m|z~$<)zFS_MyYg0&=d<Ms-?#26FOU1f%4BnQ&`6zoPF0cPmmR2c*OU6m=V_bk+?OW@kMsF#zJDy7DKTko{nCi@`~M~+&3!$?_<s4o9g%xO=JEX<?n9m2bv-NRn~%x*^i%l0Y2Y@I`%8!L{aUSMBDXxl^?i+VpXKD9aWDA(rThq4-@ZTRb`M!U`9AmUXIjbg+0jYdM>u&P@SE<3-G|D_&lTE2=f3d;W&Mrw+z+?RChIdsi9XpJx6Co!?|JGzju+P<rZV?|S+0uQny{Puz#EAo_jUM0^ns@S+l{)Pai3o!a@Y5TxxZR4Tjbtri*^6t=`lv0Puh1xpJVE8&erR-r%gLqAC^hyzW1Z#`IH;4*GJE@iX!*44HoOT8E4`Uy-xXVy(4mWr{}yLtq+mcVQO!kd%VxZ_uSfjTmOD`)+sa2^|rh&^gbtYSMFW>d-#(BBKLP+tA9^=(`=ICzrR%f-gABroB9E>^zSSGi%BB)93Q)e=g}Zp|IT3keKM`Htbc32%iS$2*O!~l^RaPIV$$6EM>F34iGPrgG<WY!&-K-=irklXG4I>7ix;_-ke=u7ue(I<>NA7)Nt&#BYaEN`b>eJUKVTg1OWYkL>kB;PdD<aX<o;uWd4J$aj6DAVH+h~mi<0$;z4*Sne+5}T<TB6S`$c5_UR#|9I_7$7oJ78F4TOk15Zi?BD_=j2m*X7J^VB`?y2$+lYw`W#gVVCU;C7y;oezlIbK+B-2ga@!d0^m5p1<}&k-PE~(|KUf1X(|Hp`NGSM}tIe<u9P~K&FoJxIazd{(pQEk$d}P(|I7M>RaQC;68lt$FlybwA?4p&nxQ-4dDJZO9q)IyyCuY;=d>4IGuIwP4Sofp67kQeO-ZzvVK@=p1%u@h}={2xSqf6tlLEHTKXOLQInR4+;?xip1;<*Z{_$kM{|Gj{xF$8pTqq_Tz8o_>c#7Rww7}Ig+qD$EnQRRt}NkPe|((S?{#wjt2SbP*vYNBDR^Bzc1q-KYa7qs<%dP?x${EoXF7SH;R><;X~wU3m)F^b<K_7@TfqB}#lDvHRj-NtI&<9Blg0j?`Mk5v^1j?JmE}0EygCo;EG_Hj9~1jgraq{@*uOIQz1@1A`r5sW7vnVUr1L<f`y%(d*Xw!e!+wjYk8UOQXPn$uZ3*wI+}$E_Yi)g<`;V^>xqHq`v7cbZ`LB}Le=zk6$MgK{-%ZvBf5P*(kw>2Y{UPFh*~wi^3yb?}^K+@(lh@hT1!R4TJUS0t&LPjIdOJOTo%=y^+;w5%{?S~Ac};m;9{a1vJytN^54Jxg@<3c|zMsPVj`_Ty55)bEInUn*^ZibySt9puIIHKc`~EmtKi0$d3+U&~_}}jn{l7W?X|?qHwdU88d7CBNhYzf*^T79+`M4{FiswX5?j6)!%wH#WExyb16whUx+*d6@JWp|QYsEEQPnRs0^|cO)`D^lj&Wh&_=C}*DisuDR?ymEr*yn$9o~y+CHT4blh<$Z)9iGe=`{5>EvYzMfw(N48>XXI%HT5f(h<#&oK6OTl{a!Q9%b8-I){GO^Pt0E@57Zqi_C?>EXBV-bY3dse<^9GV$BNwZcS|vU&Ch*VPqFW3evUQki~Tw?&gyo&{zg@j_4TTX`D^l5O~t;JIj*m?*pD)K{hHiA|NM{m-nt$a67$#8H~viQ+nD<2?{Z&_{T6fmSA4|l@0Xk9yr>nnG3op@<3Fw@_9e_Xi$Zno>?fG|SH*b#{?$d~o~rl7{5AE9!^M5KnHPVa5%<f1eHRbw`roGV`nxe-V$$5*zaG!ulNm*BwM)nK-@Q&qntL8j<@ww3FOmClrRDiv_7{-{s*K|M+~}hscXxlq>+A<RWqpl7Jbxc9k@bBZ@jN{^UF6>RUHQ4&HLuA1hpzKH-P%j!u6wOG|Ei^|KlU@v)7o`p{o{r@cXcf*&*z<ZUS~foEU!bgYCL~~v&zraV;|4ovngbKt#UedJ$V=}>SMQXpM3Z?k-Ha0>fALkLFC>e%lJOG)n1YN@8{9EYv^i`drr*bb++C-S^p%9&RtnYi`>dHiRbCfe)4>(r_#AARa<#Jy@qk0e6gXduk%vRM|a$3vc6wm-oNctR9=U;yWA&F$t}k@+Ck@5Oj`N59$wY+(H-$jeE<EqqPegB=MRww?yS=5uQ$h8IbSL+(DT%N`v;M`rcLJkz>OP3?z`^geY_EiMDG41b`8&?iE{jVUG)6*#14`5m0I!qE!&CrwZ1sRd9f)xPbXzdOq%<LH{^ABU9iZ#%|p2U{YME&b63;Ze4iT^5V<!vnBPyxep2LCi;280m);}mL!R?I-LP8Z{&in-UmY=59=FA9o~OPsBKK{M<-U4<UwK^5Ri3A1+KSwrvIDQn8ymbe&MAKWTi7k~K(prj+_}bwZ;f+^=jnmmvc6?q?yJj&%KFgnd7a(-JU(ge*-(-9wNBj-xxeKaUT15a6?wq^n4cRSJScKsjF0DO`AxDuRRljb{31@|?yb{!ojo&A<lg9<ynj`Du*j{{-{^VjKGa#(x6Z)(SHCxv$4&bc&)=5S<T#rw?yJw1cx#+)Jg@8Klb<X2F+T_CmQmKXjp23n#w+nX_lDf!{i{}YL~d<w#LpehUlO@z`&K=F{ZD_C^Ci<nUT1r3m-YTQzW=?sRMzM2ujj9)&2)J_?ML!H`PW`q@Bf15@3S5v_lI`U^VjOtO6T5sC;58r`$oK%<>anMEqI-+@n1sH-2Kxlo~L*Z%E|quSMxd>_*vvu{s%ly@!pZCFTaTIi%)GAc_88j&r`hTV~#s{D)-f$r-|JA)dlfhjTt8}lGo)gdWzgLEMC0FV(M=U<oWxkmdIVF_lfsL%s6Gb^1A$cgvfmbHi`E%Onn6p&)>npvcB+g@m_?vZr?WK`{Hf^k-LV>5$_?G>u{|q_th!($ok=v#B+aBf3qy#7eAdNa{rlO;yJrHpK_7hS5N9Ia(BT#;<>h|ulOF{7k}MA))(n0o+F#<Ff|L`|7QD8p3l%|@!Zyob3G;B7pD%D^&{$u=cK0o&lh~3yXc0<z31HGxunSlT;luRsRu=FMRgF*0ZskzLwf!O3dPC!6&)p>yP5MWxJu7oSFXWw{MRMLb1qYVViM2a%}sUgd78lWRR)T6*2(?hoy7b#^%HLJdW!vLC-)XTEc#?8_x*Z7tg~jE;XB0qb#m87$9eu@|Jl@!Udw$o`eajIYQI=#&G}r66Z6-c&zMbO|JljiMW*upGx}sxKXJKOXWyLXXfc1yI9KP0{bwf+j2OuK&*+oQbuK=E=P%aTH|N=1%wJPq+AH>-&2cZa;q@1NvdPEw5$miupU8${{+jy99mW3hoAa#B>oWRe^K<zvTCB6?`j09r=C8?1)Dip7W}FK}cwI)HZ0gHY;`b%6&YJqmE-`=2&t*ahvH$$$`<aFNYV^tGbN%{0ugh3x-<)U2#-#JtT%W_G#Qw9Bd(u7S=jP~>P2MFJ&tI&wX8cV*i}`ED@0&vGKbvuO{~(|Lc3H^dVE@^_rBY(j+`Y3pughP3C~{~2*<brzk-L5v&hr}UxRX2k&sK#O2}yH**1kNi@gB7qAN$YNxpT5US7)BrSjSC0_MfdIn?>&K-h$U<tmEeMV*lA{Jz3;|{dIX>V;wj3*nhU_ca`;rD)YLG_h8NWVE@^=`MJnF*-P=f#yW037xtg6i}^WUJB!E3F@~@I)KZB_b5A8pKCegaAM=#2XRdo<9QUQ0+_zxA(bPv?;_HKbMUxjl$=AVop6(oX)B*myk!@r?ZaaT2><2n|;Fp#BdkOn~-bOQd{4TZl`;(?XV$wViF@}HtV_(JOkwbW&bJ}H*dxrH8`y?hG)s}y6=bkBY>p~N;@8RUW!ZrB!@Y1>>_ZF=n_A&hTrttY=zt{WY2Z>2@=Y0wP(mWzJ`@L;aiQIW#!kHIl9PIZx|6ah<<9!LM=mn8G`@PQl`DPrvFX7A!CwKOHo%i8Qz4N}rjw!Mp`@PQl=jMFyzJxO`%=N*3uk*gQxej<=!tJgh>#^VKykBkV@xFvJFT67+^Y@`hFZumJ?r$0+uD{7!o|E4z<j(Ul=ihype8Z3O`{o=M&&!<aZ*qH={2n^T#q%=f-!+)}R2$^?6S?!e%(?z1kN!@6Z;?CC%bfT2O?~TG^84)6<9V5L{Y}1UtoWWgx%0eCzn2~*{?*X5qnT50%xzhuG*-CPAtuQ`8KRK>IG+4J8R}f}|L>m+mHFuZ`cH=bwJqzh(qM?Vk<ufj6hW5N&}I>T1rG<4h!?{PfJwy1mFHKUMd_H$BK{8k(q<+R4}w1g4+1w(dY}}n{!Wz5A|43O3?>o#;Q7EL;-kvnQ=UobN1H{w2>!xmCJ_&S-v<u>*H^ly6r}!6J)1?`A07rK5y!z@U=r~W<$0B7R61<4h!?{Dv6)H4{or@O{lImV?kL&n@6@qb#C_ozz$D@Y@H}7=@ge2!Do?NUgUuqI4}WemlZa#Ce}QAcwUut$G^Z@9mdzsW15XDg5zm9a111q4RGwRTTBQRvi+C>lnaxZh?hXGF+#6g|>6X%Kr5X@%FL-DWb1(25crGxB*snaN@-#~OZ5Hut_}?}&iMS{HCb%cKy3!v?|0#VA5%++H1Tpsj&w}RwlZf{z&#pYR(q5ZIJQM!ZW+oALhu;8q2Uk<NuJlT&Dn#53o+^mB8+Zmh8<<4AM|oD|DV28HEaK_#CpI&QxGVg3a93~@rQ_<W@<{1Bh}Z`a=dzi}7r`roNyKr=7b;bvpPS80z5xEvVkQyKhaUsa2hUSFs`Nl<E<`*Bp2KFI1D*|cgGt1*l+RSENIy55nS2KPzQs%;o(}&JJRLku>4?%jrKu3{xA1H>^S9tB@Xx>`;>pS<DOI4Ko6Sr<5q{TVCJ|479|lhVk5@XRbVq3%L_8KE4!4=f$G|@YlZZzvFRwg{(l-{1c$CE={tHY#68-~tBzT0<L8aSD!y#fXM4Z`XCLabb2PP4Jt-P%AOiDv77V!}HpB6KTcrg3`crf@Yr9n!5rCVU~fe>++%}hQ3UIt7e?ytO`(kF^D+RWsA;WsU25^*eiKR6cLM`@qZA4<I;;$H9!Hghj<Pk3oCiMWUI?n<Q;r?;8OyTNZ*%p~Hj@V(%!;4Vsgl&&jvhKM^s#OZ8i@{aJ5U=nc$<t3D-Rcddsh}&5#;@`pKZQ;AYZNXnE?NYj?6ax`^AmUJ)nY@j~BK{cvo4mF1;>yz~wX#^mEiD%DZ(#Bk5b^h5@-LKjDg~6HA>!r`afr=K-VFW`m_*!Ec@w2#ic{On<c;B1EoKsNBZznhn7pCVcBLyy4Ittucq*GY3S1vv6igznr@XGxhqOM}%;a_8zgo;B;@a?S;M(9?N?VmKE7gREYe2*)Y-aN6@JKL;_;ck&lm{zSvslDc;lEhSB;qRYE#NBP%1WD+E-6)lh}{rzkj+e95&i*~MEsfZ3QC0)+cq=#rxuI&XE1qr_$F|9a5<%oN*9&NLd0btV#{VG{{&tLOd>9=yp&Re;@4pElJE=QlHd~X4d4>skCoOdomVOj5q|{#5Bw3h7`&j(Tnt>4zB@|qD}DtgkA$BCM}mvM*MW<GKcH)@v{vaXn7k1DUvMFC1iXOF904v!=c1Hf@k=my0r(kk0dRi!8gPDaK8tQ6Eo-&XX)w79B7OlT&kN6IGv@{8p}(vAALZ{t#P2}Fr@-X7;j6&8!MT)jDy>xd2~3^?B7P1g&klFl%-O-&lxL;$Q~V4}9u7YV4hLs}h*yBgGb=4uN>s`O5r@J528V$&!t>b78NnHpr>E<p_$in?9XtV?4xARg44f8B|J{wHO7Rxm@Uw_R;7`CI;MDMUZ06M9RLWD*byxftOr8RM0-ORI3=uB@ldD$S>Y~P&W^*4+B7Owl1tt;aLUs+D3rs!qZ%W_W+(TCa=Y&rM=LA#lOx_txBBma?lk#tE?xRV>58yk&B;p*%0^l5A>Y=H3zN)kXOr9M+1)LpBy)$`7Fo~FY=nl#!+uTQ!i0{F-gGt2MkX-?115*$EtI{@`d*}+_tnf+TtYGS$$=icT#MDE#Q$Eq=KAJ>)2fh_dA`VA(85|C#9{LxhEjIVj<-u9t6Tn%()H{>61(S%WhyGIec$@oZ67g;LW-y63GqOwI%wX!Fsek@iX%m<{6MP&v6PS8u@)$6Q_<(Yc^07Ae&?Mqp@Qq*+aTv0T;4m=t(9}C$P}%?{&j=p_&IqR7nY;~{L`*$&YvrSD?xRV>f56v+NyHhDod;(CQx8qO^Est;VDj|vZ@}rn)H{>60+WcThi<8Sl+ArKiTFBvEto`{4%u07IxzLnXO!01+((xHr-hFMrv+2*Ox^-aBBmbt3*{qh?xRV>*WjzcB;rtHr@^6M>Y-05t+Kg~E)Gru9}Z3f{>@^K29t=Xhi<OiYjYn>A`ZY;f=R?7$bJHcfT@Q*skFl89=aGfHGCL2HJJKl@@8NXG4;?*m49t>A59{@0$&a$5vM|y2u=m29-4aR1f^wQ@|5tQ;FMtMoynVkNyOAcH&#Bx=02K4d>OtJOd?K!EFPQ!Og;1or6o4^(M7<)@WJ3<F!j#ljld*g>Y-`Rnf8~dk0udcf-eS>h=Y(F2M2+vho(Je+FvdV5!>)VU>i)mGkF6riI{q5+H<D;W$L3z#24W{Fp1bgb`)%ZsfVULXWCzmfQYGgCLaJM5nq7U2a|}Yho(Je+FzzVnnZja9tS27{|7$;CJ|E)O}#ViJ1+#2Q}0aP4@@FH2d@hz5mOIMd(O1KOg%J-_$+(@m_+<9{1BK#Og%L1In(}feu$WQXYyDuiTDh>Hkd?AJv8k()BZB`&?Ms1@OfYo@eBAtFo~FYXzHJ7-+3;Wocd<+-e3~(DR@mViI{q5+H<D;W$K|x#6Q93fJwy9;eIfQn0jd1bEf^}ybv+<&g4D8B;u3s>R=Kv_0Y8EO#92!N0W#X;j_Rb;=kehz$9Yop{aMKedn2Az1M89cL$S*6X4arBx35JY0sJVm#L2?5y!)4fJwwp;CsL%V(Ou(ccy*k>0ol|oyog`NyI1MRlp=->Y*1~yzgv7#PlbswjC56{Qvq-1itx0>xw1*gMn}VP5GEG>EA4^ZlKLW!>HOR>ApZU^+9^0?mgO7vHl0B9WS{'

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
