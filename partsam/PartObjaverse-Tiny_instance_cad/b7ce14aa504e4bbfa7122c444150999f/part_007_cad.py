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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_007.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_007.stl', 'source_sha256': '5f38f6afa0955bf76aab3365c8341b7eabb22ae67402490ae30cc192a5e1e341', 'input_faces': 618, 'input_vertices': 520, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15198317170143127, -0.10107368230819702, -0.0018504783511161804], [0.15198460221290588, 0.31624269485473633, 0.1485264003276825]]}
GEOMETRY_BASE85 = 'c$}r22Xqxx*Z$899U?`LA|RJ0QbQ+{z@>w<P^5%n0-=}CUpj*zO*&CJgwR3}0-=NiVJMO2izrP%A#^YzO+fm0&fd>l=1lH?t^fKyTzfsw`R$!EXU?3NJ2x{ixLKOCxdi_!EH({0Qr%NQ2o?S!ml)Y|=<vQhdJZc$Xz*y4$WC1Svvgt0FIoh5a*2^*Y>Dum!+H!YQNvxLR<FPkW!xotMGPH2G;Gk95ktd!D&8n;z_6Z@59<>)xTkD?R;6P3GVV$x%ecq8|Cj$VtDyu8KYT!q<@wdUO5Lq9n02I@g@$N6`FU32QH#4ARBa=v+Gf(sbq*=+p3zC;$$?FnCrvV`pS8E=D-BJ2L0ps@uW|F9-(jjx{`~;)S@qVawkPYRT^jFwc%7Y_EsrtJ*l8-&RWWFsq3#1ZPnk*F=rWFZy|=5WpFLZ4Ydki?20IUZoktsw`Q^4f8pn7nZg%|de&WTSGjBDKdG(_jH@3_tZiF38q<LF0WDn)@P5Xi7ITLfSDuVfy>BNnKiCjNx5OHJBcf^xVCTR6W>BYp&9gpIP2fSWO`}J>Dnm5msyE+dqM%-w*Io^I8-D5lRdML1odFentzG2Lx0@i8u#>Q~s$uHOF^^wfot;g~Hq+iG53s{v%T4b2UjpaLuyIV!?A|8E>)``e`p8D}TT)j(MKex|u|7DkJ^-)R5T>r~5tzN8Pp4_3`PWw7BR`1wH<H-T;=}p|697kMKZ>iOLvL5652Q9RE@rt>TxgqmSN0O-ScoFXB_nI2_R1IWabVnTV&9k@B&%dij$0cgkcIH3LCvG;V&&TVZ80IGza((}fT;C~1s~7v2o6G;*!RKvY9M#{-J)d~7yTrw(%}-K$*DG58X1ePd7e#W=y7l-S<9=?IrhY`nm;HQktABBF!FK8=_bXa&BC+ufn*Xlzx7*jD`F9iIV(|>E-l!i+JTzdsULVqp>%aPlxcSyNP4z+BHfnsy290~l-HBD)vwa}**6TOfxp5^?<Hn`<SbP7X;JVEkNB<TVSN*rqI1j9)_3X*9A)a_<aIAAtXdUy>FSpw3&5?VVfB#~uR{u=`aii`;=C>E}I3xPdIL$P}G%iZcCN9Q)_C1aB?ru5{jQSh*()kj`TznAE=f}Dj;v%SkRxhFwxxQclt=^M`dFbb}H&MU14wyj$c>Ul0hB>YS#%t!G(GxXpcAv=n{ur$v&(aCZYv*8o3+GGsL9|`-fd3}@d1QPrfcYe$aWQ5RanEmWH){PHGl&}p>ut2JbK~NgowUCR9_IecJ-;v)BP(m%sJfeYRCsx<A5o3D@onZ9ZQXXL5KH<bLyWf0%Ty$81pd20t3T6}>t{dRpq)o+8#BLri#e`uo=)la6EAUtIj)DsjSS3JT-586@-x42UaJ>PKPGNGZ^azfH*5Yq=bAIe_0TL3!F-WN<Hn3BJkRrkw0^|J$-LegR9a6w!<+5YPnLXi{qXD!U|tBkPG06Cit2n_DZUQfaclh;efT=$8UOoQ?R+Wu(|V=JO@1TpIgIlq_i^TFf6};-_8;ON_X({ZapNIz_n5b<?dPvCr3zm^pTAjcKYz_1D--ureXQ62*_iA1KGNzvl|Co#el>QLeZ83}m-u@4Xz(g+y`8^I+!)bO<3`25`8pZULGP#aedgO-EA8it`E3Z_x9oqn!hXIOH#-v-mF}(3&O5)s%&Xne>dnqWn2$cPLYx2Nvv^(iJG4TZ|9x|KT_0Gb*GKOm9<_3XUOzpK&zrt$zq6k&#<-<)9Zo*G@;mMPI=+Oj&n>2ETwFZC*Yj-?^?rt*WIprFTx~pip40uK`&7zYZ9F~x<@?J02|90GG@8brd#B#dyduO!P~mTgcdy3B<H$xjuf?ST%*!%2;$oOzPnl`w9`}B}4y?T})83D#)IQ=-|0GVgpLf>!6bIv{Yv=FzYP>$X4AttzE3Cs75qf>S7Q~b5&z-EedA|gIUK9=D`;+B!hzoZq{@i&`hwnowcGK%;wBq}gwO#f4Am&Dli}}Le&QLq?O{6a_rcM5q#(BQlSK4_|=LpZwui#k!qWK}>?knlFde8FnJkN*IYxU-#3p}4a%1)x=+xCSv9w)cP6O|{{upf63IVXy?+jg6wt&`czlM7AM>s!VV53M&rt2a6_H-DWqp6adZM)hfYJ?u4uxpkdcGnIMDi*fdPbKP>jU#s$LoW0)s7<^5wv2;AF&++7(bRS{{WoM4hYf<e(zHe!{b&Q>RB8w6CjMzBF-jCVnQ@)?sU5dCUbV@(I4sOk-Xa9gve7vq`^-gZp8^?YgLF4$jJM%$zB7O2G57(ERLfrfLSSd>a<qwTxj?YI=QfA^t^v60cU66U*N5k#?h<VICe*Kv*_(B^`DsGLZ$fUtEZ?~-bnTLEIk}ia}_dcg9c)-I5JNG2`@p*LPa)iAfPcn1)g}En<`;a(Gbra@B`r=|tV;+yYOE?|B+$FSnC%5W_F{C?<=Vp4ne+T#0cgxmY8&9JFI-gTq=lhF=5?_>7=kc$*(*92P<BYal2lsB*;uRkIt_OG4n<16X`l`3Mw_e0{rhdK-(8oEdL<o&P!__msxJY=S^BQ&AQa`J5=>2T*XZ{$xNq^>Zl7eYG)pIeQU5ELARxPOiy@mCDZoY0#^$~^je!@#Nqxzkn=>43{(S){J=Pr-4$ROr}%QmL^8h7>aw|m=w`mcDK=d)l#=EDmx&wEmze+T!@=U*Sxqj~est&b->OI_kSe%7~}oURV_6Prul-_W(SseWrNeSiDBtKoBhPybql>Pz0z$K&Mt+iKj%_Lt9kFSqK=gB5AJZG!Z5<>20aMrAMW^LWLE1^67NlUv&bPc=>_chsj^Kj7xL>N*!$9_&}V_a%Luh-c@C54@xwFVXx_Z6zs}^mSt7%|lxFH+`H=ZjBS%I=`ItUT)QgZY@mX2!ExICv<)h(!f{x_(LC;^*J6V_x8^`)p(rTS?@fKPVT5rbsU}CyWZARBYy6kKF@(=0)1}R$*q3CQ*GDDt@<WGHGR&TlRN5D&6|^3^-<eAKF9Cmj`~#NcXF#fS71G#<9BjLeX8+0xp&>ZBW_;C=b*LTEPmJTtbSfFH<o1f$<3<S^nT3h^@#^YYxg0kIPOEla+A3C^U*plz*Bu*gNwG=d~)yogR`F-m33aMX+xjK(aEiO15b4vo!qKl{!1gD$I;0h^{I}dlUwyuDmC+Ye!2TM^SNCoxB3B3wOuE7);s6T$sP5n=FQ2i`Zj*SKF9Cmj`~#NcXDUFbNo*3s82P1C%5XSmv2q#yq=$)Nj%l{KUb?ZzR!0D_nz;}Q=jh+?yPt2uai6KQ|+&lTlI5-+LAgyPtTgfQ++N+USRJ0Tt2m|ozHPPxwT#JRO57VtA5_y_OxB+{lnQU9Y~$`8y0uoFFCk(yVsM5r@CLtSf?Y6f7B%Xdg$cV^|1TmPSnq5g&g;XKZFo>-e-EA5l?lWnfa^E#GUu61=@8X?!3P}b*d}%@4QcTaPR)!c6B4}yx(r#;Y(8I{rUQDh^M-rAGbNw=l&LShxwe(VwJ;u9<R;yyVHIp<<$F0`lJW7o!@I}^k(k-UUP4LFZ+4qtp`u_y{Tb*Z)!Wgf33gLhv(7pJ<-9v^J#JC_e2MG)~EWO=-}S^ThV=KzntG^znR^ixbypO%me1m&tLFV-@6^$yWR7@4WND+9n#molUwV*$)$lbe#h?toZQ?0CJ~{H)2erHZ~YASFsl1-kv<+Lx5m>xdIa@j{XVVF!(~*rdiMxE53JwkKOrvW=N)P1Vsx$Ll%HB<q}ES^M$37>7LFygp8LG{dMjzvTISa8+v|YOOFvHId19H@b`v)yw&(S;>{_HxKCBn-*XU2j*|#fFxF2zJI&t%hlluHPx%GRbyW_`G+xortf`93K1Q9%kx%GSR`%n2jg&dcOo0;0`<8*S2)5w=&g1vvkC`!*qj2eX}X#FR-iHjpQi5nTaX#J<+);xfF`u6f!@8wo~S3iT=Tej%)<K))-oNPthT+mV9UnjTr7hJ6C;j`Y$QE&R6B<_h1WsculI=S_GOEcr9NmLgSq1QXORWH`1OeVFSBjiolLUqj_F}I#06ax>cGDWMuneBTT$AKDC?DgUbbK}5Fe*WjUKBVH9PjlMl8Pvw_lST1pelFL3D|73)_NFz=7yYi)dzSBE-twweZ>HbPyhF)Zq}J~<vjoLa-QT5Vald#DwW|hkqj!j2Kcp4&8=bX!qew7uGvy0@e*w=UJa1xYKFodX`Mn7|zwl&@<L50UyK}vDJ!vp}5vi*OaqsmcZY*)L_aLo*5ptN1PlE`pf6?O*_rGq8*1z%WIQKJstk%ELEQz>h^I6>2;CanlLHp&|eF66)c%HlG9Ute~4>fL-`-tbE=L@YL<27?JX!3W|#_#j3=Qu|5S<J2X0h+gAer&DAjg8^NJvCzVejbD|ZyddpwqrfN&X}H`Cl=hu+<O1#Ne1Ri4r<&8{+Qph%6U}l$DEj-pKq=TTtVEru3ih__do(_Gq<kWAGT+{xxLO)41VvTe^<Sq?<W$EYSf3G&v>tgq8vRRG)whkj_aXFD9gOhNR1l{IuZ}vGDh#`Z|3fcZKJjIu(#$ss;}Bh=l$k0FZwgR$7Ve@H@b}G=h`9Qcy2C6jbz^YvR?n$O6H3%YxPF(YJP5B@#Px(c_hZ4=Jy#YiM96g&YXLSc<6upH7+vT<mYkon0udJT)Iv?xm`3rH@4ox=^Zyk<JNmP;86kbc%F>w&z8UFI_CaxKXdDSv+Cf%Cp0deWT($r^V<`8KcjN+=kM#c{Qex?BNDskPPcRGJtB*nYdWvf#(#6>ER9>^2RG^#jj^vck>yAJJS|r|Mq6)qZ^0N^LF3-{7FJf#`@wq)X6vsuYwIxIn<eyf_rBh&t+%7;==?FuF3|a!&cr=iBei~v3}5p3_9`QN&UmjI!)EdOYv=r#Ti2N#c;78wKAo?Q=lTx$^?sV|;rfUy+wAMdXflC6ziRkz)7D`Y=4M<Ty*}p}t{;_Gt2dIOiAVMMlAjw}??G+i{qaOF_r5n(j(OCyo?5-pqb!emeowvrWf|hhem7#Z^)@35y`L8PIk@%Qc3~#s$%XIf^$p7N`)mX5Y4u`KW#aC2Rrvh$KA(Nc=iNtDnOoP}fzSB7J5p1t_e5r(wx?Pxz5Yx_Za;3o*9+@<yFU|uzVvIz+<G4RXGZ><&CyJ+FI9+m=&WX1y%F{a^UbH2<9$eR`3~KONA>=hx%GZy{4L_4GtTKevL;=Z-Ip#f$9s}uP7q(Ohj-qgofmC$^L2A!n8pqNn*9F8_`<ui^X10z*|fh~O6mOY>^W55Z^v$J-S$hz?<GzGx7In1Z|IUlt=>AmQE`b{y>)y;;}7oE)_G)hI?tnSpV0Y$ntcAZx)`smpQbtJdL26cy2g#dwfH*z^htttycQng>)xl&613wr>^Sk{#;-Ll!u}y1RrHP4j~Mub`C<>f=WD%REk?EOcEHZ@eznDo0;`$h{cVxFfquW><#>PF;$m71bG&yg2E>mhUB6Z5RkQK;w<y;>Z9K-?Q5v_#18&q=x=%YVT6Ci0Vzvag&btDgi5p>2dVRhLTt6^Mt2fS1<aH8xiMMOL2c8%A2TuO$QsSPq%&qsyjkF_mZoM~tn(IY{oCme_cBwCM!;@R*agofAmO8Ahhq~4Id)$Sx8W;J)iAUvacUar613&V8&bE#^ADzOy^bqa`e|I2O4dDCJn!|OT`Oefj!P;M6>?|3OcT_>SQe<QjxkRrp+n-)2NXrQ7`%f?WR{sC`(~GJV0{^dndQn!6p`46TGHR*mlJOZd8+;8JpUU_cniakVv<b8rd^2ciXfgONkqd&BhVPDCZD<gDOXSKxYr{81t~j&|d@bbiLyN<Iiv7q6%?AIijEypSK?lNr1HTczFWSnFL0jn%`2WC<fsa62`59;{?PK#XXe;dx9}d3|8Ux=MxpB~i@ZFFb4;=?T9{bh}+6%roj#Ga4VrUn~92SF?hR=q4R`~pAm%%YA4PP7Wr!FB<WL$;*3jdFc-(~y>Jq>>sdK`Kh{w_2bx(_}XJ_b4mUg<`gUx4;T_-oJu@Ymq)K~KWpgHM6}3jfr$A6Kyt%5RtPjf~yUY4Fi9!jTV0PWez7^9ARXhNJdN8FK~amClD>Eu#nWJ&;p=tBe`Q&p^)dD)%*X7yQ@o6QP^oC&EvHeh<GJ`|>?>68t^eal41P`4h+G8u&Hj?qc5lw9Vl^Xm3Pa3^W-&uiU>hGIBy)@VRB=kl_av@VTJ{p=sgW(2UTu@a2)q1<eSr_(w7-!skM}2v{cQNAQJ^O9#yapBK3_&~)%Qupa{If?pzIt&B#{FKqrRw3T+U`H^TVZEf?z&{o>Y<_)x!cC`7`Xe(_CUmt!kbTxb(<fcFu!`DS_Ds&3`RP0+_Xe0P^I8JHc)1sXTJ{^2Uv|Y#x_%ycqT&T;0<D%LbWHOzMH!jv!F81lAe=RjF^aZ@1AM0OeE3UjBn1J522I9y5I+zKs^oGqJM*9Z5%a8Royb9&hKp()Xc!04heFdMv@BMx#eGPv}>Pi{sp-bV9%2?#${37I(UoRs9`3U5cUniqK^8Jxh{)mi7<Rg(&{x=ybkY9nE<yCG8^ep@m_*u}O;Ag?lgPwvvk9|1>od=)B@BML0gJYc*^XZ4<<3i34^On}{{T!x8`v#7~b*O+(E8~Q0UK6Z8z+Z!pQ)^k)RF}~jp?qOPb@Xvr)*X>?9J&wwIDDdvrn1f>qX|O!nh52~$oO1F1sQFi>EYYJr-NP;?3E_Kt5AN2jGtxvSH@}RDfkOA&dE3rJqv#db?2aG;ZGxX0eTKTx7=1P8F`=|!55NIP{t?F0`MQ9t{}7kd>-TqK?}m)liRo><4@>a_y;oX%lI4m7yMn+-G}}K|0i+}p!eY`%WYJW@vC6{MX=v0<9ivg&~5Nv$eMOCIzc<aca{<2;(Q2l%D0r!0{IrmDZfSbwOPg<=x%tmoh{hbHsrP-r)qXVcfu<@YV$v$eH6a7i#5o_zPXHM7*{ilN%<h;YQr}}J6J|57td2G%vELVb4TPmBB%UbxvhB2Up(ec`MsFec<3+iYK{Jeb*sFI_70qLCiDmRnm9ky`BVnyoAPZj-|D<<i#b;9Sj=A>bi2*(L0joQo8N`D(nR>9@VnrTi}&YpXKb@6=CU(<6SSLPE?eRpZw^+|c1(`qSRIGfgjeTv1+32sn0w2Aj`ru6d&{>$yA6(0Fy^8Y=BE>Kt#Q0A;+QC(fc9P-w*=@8_&E4j=vH`j{M2zv3q1kf8ry1wP`&{)9ee}$iqN$1N~^>FEBkvX;|25;{397pWITjEhJS^+C(y_6FOYi#eF9%ZZljotqR`^-`DEmmkr(<gd~wv}hkguS6uErR{P5Xjd?+IaG$*{jjI1)UKtF)biMp)N58!hk=MT*a|Cx+WWt4=LfG;njoQwcyS@;sDD+etLUlO_U&~orM<Q(0SaT9tQ{)&ub8Gk^p!rw++GW06^P2{dXli{Dq_(#Tb=u`O2a@!eYWP)aZe~LQAlx9HwIes=XY7|r6kTF)aC%{h-+@9iM7Kxl<%1?K3ZUbr*Q@*>4b2Cw+nDX<G8wFKN`31<0hK_>o?c&@l)QpCo>Ehfb)F`I>R2S#ILycm}t9_Y@{h5lq@{MH-kWn4l1HQTH7x~`EDIY3hF!F<uQ$9?_P~?Xqr+f<;{gCg6obsQ`7=-*F<dm-|qbKq`kyE~lj1m}M35-$slE`(1FM)PRu$s`G@H<`V&qw9w3iO!GN1?6s2b=GPw$i!qVesAH7ox5F8nl(}xA|DKm7cKqJ!mUE1Fy#Phl|InbQAm)_&?ycpuGqF4D<^8Y#H-qOctzP3-*hVTO?Q&Q+~ONbJ3_#O!;qJoSTRm#gy;o;@oi5C^j5?ggSmM_KK<YcP?g=kW)<gRW8o0L5*U{FLQBjDQXm3ihWsz{aJ>*@&#nHlaUA70KTw{4#;;vPWb>C!N><Ar@Z>V-n2o!4RXpCl@Wq`2y)7QBBMR>?U7SHpNxjcH$+Z(kBsaXUv`X9`Fb)wME*nMEME`()k9y(pOgE3QO3W}`!=71w$fWRzZPw!2W@@>+DZ@E{EuiWy<_v2(N_Am&0j!U=}UMurnfF0uhRe8{5!Oj{tSNs{w4Gsyt<!J_Z{jxjk;%0->KRnly8bq-Vd4vUg<T#-Vc5sLiz0o<>OH2L4T^|i0x;USGg=wpGeIBeFXo3jOWNJeFE<<<C%-|N}t24|G&{=7w45egHJExp^NiMAH%C{sBNW(K7_9-W3Tj;p>gnmG7?>!SGpHI!Ns|1@QG+wkrD4=t~3F@l8hZL&MS?FSKCp!%J4hT&LZB=hqa&n;{86P$NW6T+&zarfq#bF2dK}C{e6smt}5Q|pEd4k(8?HZBE}hq{foo?Ct|<ivCoyo`+bSWKCF=Kl`_V;SjW5AkC8D}#xlXWT(F-lV~*gTn}eTSft;$D2AvMC`Wlb^#-mT=r=zcFsGWoMbo~4r#Byw7ImWRPIv)Njsgq?4hmL^n>*8D=_{nHjld(>%Blz`#+fg#qFW6SWyIkB>{dGZ~%6COuX;quAhIV@y9kAUF*mfWE<wD+tTzmA{7k%^v?~3Svemmf2tnn(1g1X=*<L6a>*JV3J#yjX+c%^RFd!Nn4ZKbcpd;dmoTj_P1PeJ>VjNfG(h9<$6mOop{#d)Q_qqeT}bzGdUgBs-z<7ZV~smdvTQ2IkM&Om>HKLdXfdJJCaew#mlw$g((e+cb*avP0h)OWFOh_=!iHeU;ErB!S`5bY}P^`Z6Pf5NtoK@Y$;L`^MdApBq%Lu3qv4uk)Xi~%x6!Vg5d7k;KE{1CJUf(?N0h4v^JqtVZ3^rd`oGnZekH2<&vW#0RL>fTyt{{ubePwJ0*?LRp|_T_!}8{90Nx*iHY`JZ|?SV8?JUi=SAG&&C'

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
