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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f044310ff65243f9b90fa0904025c034/part_004.stl', 'relative_path': 'f044310ff65243f9b90fa0904025c034/part_004.stl', 'source_sha256': 'ab6ba759f40df1c07ec52e1252a05c3d5e83cad3d723e794e38eb28dcba36dd3', 'input_faces': 600, 'input_vertices': 411, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11581755429506302, -0.005819946527481079, -0.03507115691900253], [-0.08871021866798401, 0.03552961349487305, 0.03794637322425842]]}
GEOMETRY_BASE85 = 'c$}r233N?YyvENpCT0=ybPy661fd}`*A!xmIfimcVjdzw48<`=sCkIUaAT^eHER%D^H^gLYPeczt|-+usF(f!K7BoJy|>m|?`5sMzTf?v?6dcO@BQEVoSP-MZO&Zo8h$EiSqpO3bMe$PRSIbC+PLt@s3D=@V``0zm|)S0h_8M=>Cz6}+6VWvXydd=o?+o*LL)sJ>7I=T`gwZmo&!fkMn(1?*>6;2Sh(^7`wt%zp6!nr+&>~b`?HsCojTrnz3SfjWc~m6lP|joy5EL_hgDnBe@+U>7U$cWiAuG}$?(ezv8&J42A_*>-?RX}$62{vi|Z%8^Fu8BnXlv3XZ@oiS*dMa4E&5hsmC$<T!PfMcqaVDC*^wUimGzGGsg({?Y4;Th}bIkF?J6(-Ph`<F89@^4T3+hy43G<-6-`ts)WH`mUoq0A5%mAU0c%^{`<#qa^1T<a$o&zFZeqPrbs`RHj#Sl1>2h2({HTY-*&hS{H=dTJyu(7smJko5d0z!5uY*5rJc5yE#SW?g?7YVm-@A|0QkAC!;kdFeLvKMAL533&weBIINa#_)RBJKYd%7Ia@K%fs|@N1X^nAQ>}iU#z3n2oUeBrw|NItQ-+lzfr7-<Bfr!g(e_UU@0{j?n%!dy5rG8^$N%+6rMcj^-M?Eu(!;gqwDfQcI@_YJNH^wJid_A;~_;&9?@WW<Gznp($B7W-&z%LY!-#_~z!Q`)7E%$YtIJa7UuX_R0JT%t6LHj@Eg72~d_r1D6`e&b?1O9jG(T?@=FkXW-__~+WYnwC&*I#~@CVqS;xv#a$8QizyTllSil=f@Ig5-M5$b^6Cz1-Ik+6eWudj@}51<e0|46GNgC-7a0Bc69kNq=ppZo!Y4BJ)j4ZGd@EgMRw&SYIA%5&x@K;J<k%zU^U4^sC32w13ZA-E|h)bL|-XMLjXEn)bqaaz6s!x0U#|`z{#&K3m{Njawo24X9@JOL(l2`X5}D_&5%4hHo|GdfUzMXm9!^_?vG@e~sL;<$C*x4ZLrfTyOtoAL28AJ=-6H_<#8|uFq$OAKP4f+xUm#YcrDIdjwz}cCjJP#KgmIP(iNOOGYDaELZ`*Tov)PqGge1@-Bz3-9bHbyCZJL=flq&iaby&1><sa9>-+~=3!hK>KQbb<C{<7X*A!&d^iVwfn!pSeSdMpzZw0E^Qgb;V6%UEGUlHf=9~4p0l#ZSX{Yl$Kjf2uui%G$Bi9>!=OX^cBH_nXST6qiNx1&?aLzYZ)c<q{;*=21d2&?xW&5xM`9C@o{>+-vFa7RV%-h`k+5X*_2QR!4pBcU3Z%;!Uo>h_gVr$b2zV3@S-^hXZ`1gR{p%BJ}`O5jcJJ(k+w9jzEKDDbG{KrnL-?h^bx8FL$KU)X&jJ<{amFoom_{T+Z{k7A`Z%^97Z&6v|qpxg@_H1th|NJXyr;!xD#^g5}gY~OV!#s=*V!ztTINB29FrQzxV%|taemK<5>_@G`xJMS1_8X-G;d^~y8W-#D%{i~W#lDt54E^0eKiFOBx0UEB^&7rT;rkrL?{|-u`t)}J^oK8ycKh!|{;c{1>yMT7Xw=z?`JdRB>vTKv*n-uF+k{4(Z=RSB4P!8`*80&8kb10-E7(nb4OfYy{oN7tFAsgM)%e`BI^wg*m-(%g)T2L)z<e%1zuhm`M_g-QT;l7%f8IpmU|&}f>)o?9=TH1N@vZN$zs#$}xD}ox*G(*zWb%t#nkV&Ez&dqwstN!735@r+3CO$mYQRq|HeTZLDGtr(8}%m3^{vk(n*4~Ii>2NM%glbCJc#Fk2iW&rtHbyEK0@mE>XcyeebbjpJ^7lh#qW8+cdv*%lhqXGzG<G!&m*NhPXCBxlfQ0}+}Gj%1LE)D!MxXDw6uRC`+dC%$HgD{<g-4A^BnrdN96yC7M$xkRHpxOs`w*&C!74#0@6-n@H*@##VavCZ^F5*;RwY4q|W$nlejr&ZA3l{sL1hM5i8ei#y+X#slagz8Y`dk4@flm-1m(fy|9kIFV8r;O^|kM4#qij2>l9|vEGK&#5wJLS@;k7<J?&E8us6%^sSdAKF(HNSYIvaU+O0Dx3OQ&w`Jfrz9RiHb_|elG&a&-a2oq=<Xp_FgQekzyu&%6!7b!ToqkMP%#-z(as8E2T<_gwy&E-SF(2yFFV_z9ZNMwU`B6#6tu)rf`SF+!tLVG<A<wrC!1<>w{iq$1SB)Me(B4>g?x#;>T<lY^|2zHZ>sMqx=)I?49qo35@9ZS;&rTF*e@Xh8nN#HVhsP$G{FuuN<@#KoN!+Ywiozf7k32AJ4A%Q3`r6>%4k_vHk8_1L{p~|B-wrLox_e!i`^(|^a^Ez&%uj7SecJ%c+k+X%hvf@#zjnnr{6G@U*B1*i&&0^}&Nh8hO#Yu=A}=$)ISu+Txh4MEitc7V<dyW-I5Zh~wJv>^`?#)U7V_xw0z7Zr!ntl>G34D=^tH{pe0FX_UjHjU+w%nbb#iUw!!7hTUYsc7?%@9X$)EoUaR~Yg`$Zr6i=Ii|u-@u|IFHT;e_1ohSGI4h(jKD<eUDw3&lkGk9Cgi=>%An-3HRn>-OZ+NeQO}jO_NQ&o{08zABH^B-i7mjef+<D=ZQSb!y6>eJL>1QoBZch@tj*@DDugVxmo|Uo=P3v%OK7#bJ1@q<KkGDWjFcf2TC5Wrtd)B?m|D;N1PJ|x5v8Mn-hMiNqBzAzYg=H41KK@&LI=tOFhQq99(x*mtbCYLH?{wzsS?Cq~6|sDJH*91<5noIXrJ#TUc0sOhu*o-2)h}Z#3q&7cySX^fp*uJ?U>fi1Sjv12`Y%qi?${`=E2}J-f+2e*yFCP7^!_q<uUfKA&4{p~DbooxUE_TQoH$-sIayVg6s8fV_SAZ}>AyV882G8u=>j1N=qq*k>brasK@FJ^b;LqU7^0YY>Ni^jn{emU>=9CYgLkBjmT=AElW5@dxlc)y4up>K**BBACy6W97cis`MZG;T)1U1MPqQ7yP(KGM^ngXW32ux?O0$J{JAj^(Xw{?#QQwao*R$>4$ho{<r_=f%Q^?{>&9JUbaqku@6rC1HN&*hf-&1GUoGV^taEEJnVQh2J7g~Tlkqa$>;jy=XhRUNMFA=SgAD+p6@i{HS4cfSK8zDMZC!$9E5#yRC&aq4*ikg=>N-s$n$}}!MEPQyxlVb^YG7C@H2jwaWsxL!*gLl`k5PKzte}V!2WwU6Mnl}$PcMgurAVH!jIS><7*Gr>?Xfd63#^-7<c{2uk7zynI}fCLuh|H`Ysc2epqP5{NMHhzE8Jd5}&!bSDXBZ=~(ZNN+g?n2lBon<s_a*ihZi*1NO)CKd=vvdk#PNwCtzG<S>lyt!G>>fjAG0-IrqW<M!gbv?&AcSL{!D->h(q+dG_(20h`rI3erKxvZYVU;F(Rwr4f=$CULrhlkL2B+7oRT?<D22OhGWe@7^_IYuRz{8CM^Pd(U<aU4Ovb&p7iFZ1nx`e@ImbCh0@zWtEo4STeEyvcvQ9{Ka$1+?eV1J0|fqvUh5(a1|He`dc%PLuvL!}Ew9ME^}Itj94QkoU5FVtcwFzF}(-x2^O;R>?eZ-2EQ;t;nbA`(Pi8ZiBoO<Akqm^pJVtUO2(z$Gt=Qn|8%Hq!Il^r$Xhr%#Da!;yw1Opp46>ea+Z;m+K`7?f*Lu_RZq-=O4v+ZsK0-zZ32-4_w6jsrDZEZNY8$mrjk4b{;&EVDek%mvOQ3JZZf8k>j3>^VQs4xKB6w+8<#uzDozBnEZCGc%B_S5Z4dA#W=i*RO*~v6z9XT^c&ZfebBnGFXrJ7HyNK-5@-7?A3PsTrC+Kq@=QQe%)^!$oImrsN&WF}SDXCd>3H8#zA*OLO*h~dScdt*_ejoO^rO09K0mF5IFGu{ct#`snUf_i*(=c>JadfP_rlIZlb_i@@|)&?bJst<wXww6{vjIU@;Dv-*1}T1HK_^a)rYI_ZS65GEpOmlw~hYeK~ldpdP}0oH~Pu^*XkIEla2nySj^|9qmoR1n3v>F?ThD_hi>$(L&X2|yr$p04BvTsxKdlYgm{x5vIp~Irx)^HEd5)Hk$?BRLLO*L-?$;?4ePf*WBqoz#Qy#=K<-=XiP?|2jOUT650RgDU!;%cChKuuoCiwL*Ih=-Ja@zMoqf^;&Xd}bhpit&F+cD9!1?UeQ2d3tu;0BoPk%|MQloDxtm_{1ADqSe&(uuR<4Qjx6Z_qn&N6Qu7teAXt&x1C&2E7G|G^o?GePE$mZv=Sk-tte{skoddZIth4`0%cyE#^=qr=QZlW(j<{w#p^rnbma?5`X0|MpJEw+&Bn{^&R-Z1BNzT*3+Fe-AlV8(C+NZ$BP~fBcc`zxvbTct5a%{`RsGXJfQ$vdIt0!277QAUs!w(zid6`#QrkoQF>yga79<$$OvP+vwxz8-6&qZ@Xdkx5vo7>AY-9H2LM`;Jr%QvB<YI=w~)TJAZC$H~D%V%>Suna6b9^D6d~KM6TD)*iF7sZJ@*}s0QMb`v~*W2Wh{Nz6kdn;^6hRp)wDjyiPFr35#*A{-zJ|Od0wi6Xmo0Sqk!7?Za&6Sn02=P-m=*`-gZAsW(!oeiq+f{o^~cdMS18zq!ifzrQ2#u@=peb~;+n*HZ?HPF{$-@%AA6)DU?dG*)`zxi3Hc?M>vIX1n|t@i~~rJmVWBaeI&Vg#Y-#GvqvA4XA;0)JXcN*mrHEbD-Zk{fvoxZ}=CUYw921{O>Dy%y}aP_kFaV?QbS|&(KRHn|x<pX{WV$9n{x`eyQJN9qE^<VST;d2midc>__^`d239*Zx=l8R5^+FFj1*oFFn7MdfM{+K*smX8+a~rysv<9Pu>eZeJ|o4y9fJS4*K>VWZl_H{A4%zQRA?mJsE`i?%Kop$4S3FJ&$N-c5~iVl=)zd`3cVv6X^%<#ruuK-_c)h`e8p|{%Zp<AJ*;U`0l`S@kbYodw2SpzvL@@Qg5tB7y7}j5;uFx(z1@6`*yHj-q<g4e8BuPwtvbG=vR#u$e$0kvHrVVl-kqs;+(LYevvrY7qqi(7?)P`TYJeqsQbOfy8i1s_^0!KE%kT&8SV7j3V(cQtkeBFk%ymbVZLo5anlaJM1EVn<<t7Yd6MsW{_(q3#JOeMC9L<4o8kLpNq>!~fr$5Z`u3aMWj&rw!v0l^enb$y*Kj_>d!7@Uc>M%C@0{L+=h<lbm!?bpG|pjvbb8VE=^riQ-ZTXJ-OFznhZ7P9?fM{$<K7LdKUMOQz7PACKA8R`k1(m{)Az!k{NP}z$C-B(?ptd;*Imm2QqSrxI8QEF$9`qWerNYAonrER<FT)uUyJ_cTg&rLA>_kvd!xT;Yk1$|nCF2F@H{>y3I5F9cwU|N0{yL;WX_+rhGPCSO5{3PhrE_(!Fo(e;5^SeNa8XFe_!BSu!`r3DH2cZ8P0+K_}WH!Ubgpsi+c90<hkXo<N@n1b5hKHBgxxF-p1H3mMv#|j!Ry(dHG;I2hz8VlKiQ?T#h{XVG;Mo>Eb&RhGW0(PoL*`+tqT|_vbBOJq=_YYKQQi)0y*Y#=k1Qw;K8y^Zem#&Yw(KU-n96FfLiMSbrC+-vZZhePQ~)Ttq%i?TK^Ik(pdaCFLA$=l6Pg;&k|4Q8I7se2%ke^fRyGyzS$M`ioCv-gcG!*LmhF=I1Gc>wO>Qd4yl0$+sPsd1!6Z3hkQmm1&+>cYTlR|Ck8B#d4fiPR_zU``tMByDfOX$M+}pyAj;iuFHLGXNsUbJx1}qzvFur<|T&<eLYa-gR{v(%!k&);lC+``uTmm@o^CMwWApKQ+#h3O5gdbjIX0?C9I>jHu!vgG~R!}^To)1JlE|+Jfp*tOg^6zZ55tkyn=h0_7`p7W$YKzTW}rWJa0_Nz`k>;iD|!f9ITJ=TIL6z@2eeAqj8^`bxe6)yLd*fcho<-SNvQ!N9w(LBpjB0oQ5A)8~fk7y5ifbor2#r6Y(mO2tW7){OhyP|Mc035~qpB;2XCw&&r)kl6mp^2>eEP-mp(CXP5C=N8h~*@^b8s6d7k1`utwoxv`hocfsGc=zGsgJ+|@=_`%8e9%9zT)#|hU;1K+Df2`Z5>&15-PJ{m|^J9>Xey!dQzr-orH_%)9WkjdK&+@{4)7mcmGE(-!&qN+^CRUdASi8`_g72Fh8E>Th#@;>feUOig@{7&>{yXriys#e*HvJXd;<$r7?B%kXm|a{ocWq$*fBgxaGS$x~{qO&TZiw&y>QCqz`1t&P|AfvvyA7XZ7k_GFvOl>KwF|iuc@=d7c@;U6n%4r(Bv-dUo0F@PeW^j@x!Gk&c8R4fCC8HIQJ0bDk>^vFljoDarmi4=O<q7<NnSu+OpPZmCNH9{A}=B@q{flEWS7Y7(u*2R?nUlN9ZT*>?nsRwcO*BXjvzN9dr=3Hy~stVeaJ<~e`wG)WK|SDqBbGl&o0HX`4zPqd1`i1^L{LKFL^9En)*FCnmnC)lsuihgnE&@guIRVki3n2hWdeghJ2r@+NxOR7}TcrBG)E+Q+txV$>pdW$>qoesm;g*$-in)FS06%Z%~VnRZ)C|s^WfxMe$bZBl0!&=?V1}c`(PoMjcDGk^57l$^FU0sME>A$djl`$dkx%)NSNA@&W1@@&WQS>V0xa3&x--wKlmbxeC>rT!rjTEk|}Izt^Az$*L&+k*ebUBa7nW)EngE<h9fz<hA5^)UD(f>_<Ke^a*(c#~_SqBZra0sr|{}<Ou38as+ucbrN|tc{4SRyqSD~dVqX^{DOLo+}MIKXicq3ZcPrPRv`zH8&ciL4ap^_D()rtS@CO*#gF9I<V)1!<V)n8)V1WD<Q3F;WFHIq(Uz)WuQ*=A7|fxDk>`+OsNv)oauPLyoJ3Be&L*dkZ&5dsZ;@Rs&<kW$F0j297<<KoEEt2~)YjzT<YCl6@-T8ZwIMm2+=E(z+=E<~s^VUkpB3k!ULvca_#VBT<a^{3)D`3*7W88jwJrIMhB3HGokPA#PN&9@)5$+klgK}jb6B8hWK|S@M!iK=MR9kkihFk!#Y3n*<jEWZgF2jSkf&0Ik*AU;QNziT$m6Iz$m7UEsddRi$(^Zr$eqbGsVeR@`B`yc>Iw2!?8h|fC~`fHK?UknvMP!zQPat)DE^%K6Im6-!BiFZU>3!Lsh^PtlgCiIlgE(1q7EUeefUcY&J9Y#$m+~cz=AV^QVUrX#otqNl2uWBlv;?aisFmZ(qvT>KcqGwtD^V=wH;ZNc5H7uwpDT8Y`<l88BJ|ZZkJuG*(H$r1v!x1oZ5)ooZO7sklc*ig4%@Kf*eE*AP12<Q=5`IllxLzlD}1JIJ=ytenmb_&Y;dEXOM4Fzb4-#U#HF@Und`<Mv;$^Q>X*TDP)7%ootW?QrnW3vmg7Zqsb#V2K}gk<bLFy)aK-#<Pd5zatOH(wFS8kIg}bi4keGHb|#M_FQ@h;|IRURvp`RiRZ;9g%^<6y*pqsbtcv0?)aztb6z8WNBdenLDZLc(Q}S7=K|V{~LLEr{f&F+)-A`W6F^Hx1Bgc}bP<xW6kS9<>$P>sjsC~#Y$cw3=<i+Ie)N$nP<R7TZ$+avPgH}`(_f{;5yHY*KUCAL-PjU#k1GNmf137@2pBzB0NL6vK$j^#3>RGZXihriJg?yX+_>=mW?BEz|q{fmrk`t&?$O+_?)CuI3WIJ^R*-qX;T}<9VK1tn9K1se!{ek?21!K^O+KSwX+?U#w+?Q;lhLCOK-qa4{-sJYw0CIb>AGIRck6fIpk&BbxaXeJ)6`x~2oYX(b-*F5QsT;|O<OS3O@&fXF>Pqr_@<OVeypX(xx`VuiypMX4ypMd2dYfF?f-z`B?L=-wZb9u!Zb5EIwUJwrn^Jp|o098L+mq{%OHuvErO3Id#mTwJ&orotz2Zge$2U|bc_PPP6g81NiaeCMfIO5uh&rD<h&-ISkUX3mNnJyZBu}I6BTpkQqMjrF!ZCP5ZA4Z@@keS4vMP#m(Q8T0MgCiZHYKZ~_$9RtSrx^1sinxOC_YckO;$zmL8^+q;+*QUre0h^^O0T2rKx4erOCCaHOaNfUs8LKza*EpK#N+yswkd9ok*TSo<p5Qo<okI&L*$s7;K`xA#Wn@p?)OqA*WJR+*A2k@h+;0`z{v6>!>fu>&Q!~cgai1GpXmvGs$D92g${<OGy<MY6<dR+2wh5xk5cfzCxZ%9Z#N2ZbfZPZbhz7Z9uM1_M%oNdy&ggb#gg!F=|P21x>vI*R(3ss^lu<8dPs`4YD8ApX^8ONbN-KNKU4%A}5oxsF~y}vcCnY-aGrVD7I34$%WaELe!$<8WxPfTaLvQ@>}vU>SXdVavN$ZavO3zYJGA&ay6<Kxf;1RwH&!PxiGaD*_~rhmRf~emh4HbLG~nnPW2;yP7bDaBnOjsQ<KTN$z?6jEV3$!`%zWg`>`nQPqmU=*pIx_LgWD!j6r>>ihF&2R(yzKv5b6(+=1GL+<{z|T8~_pT$x&pT$x;iTAW;j>_RO}F2FHxqn0JRkv*uMWDl}0^>eZ>xhpl8+?9Npx|@8N+|2@2aqq^WIEvbj97P^a?N83de&nF$B~P$m3__{($)V&291j)u2P}%aQ9F>kk$tFj$v))r)XL=Y<owhk<ox7ZR2Om{jzK}H8@V94BGrRjkz9xBORhuiLG4QJLH><;nfx1hqy?(tK9WW8bZQiNI(a5_JlVp2Xw)3!85WGeXlf{VG}(o!;_kxFihFY`x{-U6Yf*j3waBHY<;lTqEjiqC{!jl!$bbH*_iLKzKMeV=ziIwj^xwZ3m|fRDUy=s5&8@~TyW=_J;lGl48rS{<0?5`7'

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
