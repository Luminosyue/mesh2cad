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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_009.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_009.stl', 'source_sha256': '02fbfc872d1ff1c3878c9990ee43a6086655439e47f2546d060e27056d6ec3a4', 'input_faces': 550, 'input_vertices': 384, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.12030459940433502, -0.13059696555137634, -0.1993708312511444], [0.2472916841506958, 0.16387906670570374, 0.09834872931241989]]}
GEOMETRY_BASE85 = 'c$}r130Tf~yT|`!%bsLO=*gBP$)1SE7D{9(OT|+vO9~a)(%-(MkY%LsU~I#TeTnec*BEBZh+!UM3loMhW`^PPyT9K#@4V+a=eo{yPVaTU-%nq6_wWAQ|MiIp^e<N2QNx$3_I>Ked3rrfQ&CQH)Fws6CypKwmEaLKeu|A|FTVQvTbK6<3J4rxqfOGLxkW}LjEHyhHn??&_HuJKxJ8ePPmB+b8$K>RGD`Wr;bRk`iu{C8;p3x<zHivltChQ<Wg~Y(vf=;uRi>x~W6vwcI~A$*(!Ik<jT79?pD0pG<pTIKY;u%pv1#IK`Om~RgshZ&OP>Z8ly5BgUVL+{vXXB(^zNMa&+DI%IvK;o*B`n_9fRu?@wH{y;+s#6mV8UPW|8{O{zCo=U3}fc9{!1zsK4lp)G>DGAijC-YxEz|Rr)b+>mj~T3qb#E&m(`q0OV)xfZwvO_~swNP`|~{gGx=qyP}_p(eO_?BmY!=sjuh2*VC$@&*@go=OcWRUu*G=Z4QaAe?L}yOOraNGx$gGty5#gx1Jh%MC$k-J}doX!8Zr`pnkC&)ZYc)l6yh+tChbGKPe7%ydT5gfptw4;!)?o2Fy(xhkl++LjQ9Iq0it9%;8EB>VMl4eMaPAZl|VV4zDVrPT%4(2g~benDgW?^f_l0>ewY?-L3o4kB=RW%NzKbTWQpvfORe3%}0KNY#hg|<=9us0`#+TzsyJTxFYj06r^L_b&XJGd0DA%-MSoeXg>%23|of%R$qbqT~n~%VoBIn<&~I2SM;Nwbj7|btKjF(K>dozIBzpnqt3Li(B}g;<lk6><389O^^c&wq0v_Kle>l2*JSJ~?f~jkDUN)HR9r{ihcJh>m3Y3j5MR4-7;{TsjXvv*K^=1r>Reod<8psI=9zK~e%FIox4Sp$r<}lXO!P;cyQpKZv!H%_WAsyU2#%NCdGvn;*PTA25$gOxKewbD7t3RJ%rp4{{ACHqUwjkwt6s*s8-7Ng?{VE3=D;_O+JkkU%)s$V%)>l8;QY~d$G{K%0mmhyF6umNE&UjZ-9!C{H88j0KIn4;d~4uW=*Kn@>t3{C-PSv?Zt+-LFUgN^zF99}-Swzr-uwjp)HI>a=g8OZy+!?>PvJbzjKlnEe1d=3i2MVXoBlvMDeF}~fIdsi#k$38#5dQ9#J)VMApeQ2_@=Av;4f^3^X)}(@%3`K=zm!@`td6vzTx72_?8s(6I%xLZx`Uc-P{xP$CQJgKN9sbbsWbX)x@{HPm}whW<O7^J4=DnNqirH{*CrHKMUdONnhi9>pc^7oSd=W)w@tXaU<sg-#j1-eFpu2`(f!?$Tud!kHvYb7rG$-=MeZe9C5u@bwz&em#BYx9qO1HU~a|Aqt8Ih(^Ah(d`o2;oVR;$zFFEfM1CrcueNJF>U4r{ZaWM9$wFLr#T#M2p=)t`$Kv^-yEeo8o2I}&^Af(ZC+a-Jel0uBVLs6<G3UC=kBVPq)fvfmYX$$}Z5*$jX5@d>2L0FbM4gVWQ2!DASU&IeqrS!62YsH2#oQi`z}(z=Ab)qhtZSOL6YD<jh5TcAsPp*))W7cs|D7l1_AC_jPlRA@*?51j*mu4t*VodC$Y1*y>-H$Xb@y=+j#n+8TpZ^&r=`Ac68!Gtaotr-k~-$bpP|pYizMINx+3~4dlLR{XXX5~_@5Equ;Db$&%e;8R(HG9*Gw-ke}BHWyq_cWjdfq5&zc$XK4ORrI4SviUg0=K)#r1>ANi@}PD!2Xw<X{BCS39@zc&%z*eX!ogS1XRS|q=7bMXycosMFEYw%t)(TF<F`5ZqRBK56{hl{VTh{F1z@yC>J>K!M(mR;|V)EOU+Igg(Kzwi?FJ<T;&>b%TCKPQjles(@Xe1m&7{NX=gez&S0m3ca?7vEH+G2TN?jJkkz52OAR59C+(l6>v^N8(#QJ(c5P82<*xW#|+5F~@P-Z_h=YDz#6`ez%OqeYfTunVU7HvG}Ij5wb7KvBkLFSHZX1wZc5Z?#gjApPMMYb`x{ep6}c*^<CG%?--5q@&0b{wK7g;WZn2^%)9@^T~hywulUBSWE}t0)#4lbW{R(SgdUK*YR&N+iC&NVu~XnX<9)_Z{d4iHCw#=$UJXLN$2RzDc8hOZ%KPoNU!qRRW%!w8a6RVl!Mgd&;kOCGeKlY|@<(T2-CnpJE#DtP{-_w7Us?CJi0_|+bt_**9eWqP59f-n+0{j#VM(ap=%o0Tw4aba71ycJ?;`w_>yV!l%6{PMSEnL>LOk|sa~1XHE;=Ut*p8Lwg}&jY_@;C-@(V8D{^@WJ^@qGg{lnOov5ghJ?<@Gh*Kq$a!q>Vj!SV8XA^X+mF<-BU{2dE%zNI{a-(wWk9X=a<M*M~TXK%theRENN<|pwDT~friq)bKrtrBM?|IBODA9fngh2^E;Z!C#APHD*RUrv0B$1(UL@qTDrYLEOB6Z%;(56`0!HIP615BRIDV-B_JiEkRy5c8bW4f9;x0QqaypikEmnCFs4;#=3H;d9lvbGYwaZ6dz;+Eetu49^9#PgB(SvZdUYv|(qZzA?Eu>MSme{vW1bo-NuS|E~!2na%lh?I^x>bvF7*i^h2#;0M3<e5_mS2G(^Bz#Jytf<N<n__g|?&uvR~<G9+PpGW<$?vZ@dcgFM7(78YSC)LpB&?wAv^#Ihly#)8U-(F?OpLYs^e{ek3og9w*jV9Fb+J=4g^T57phQn{?hk1q^!TqP?2ppG?vFPUqJbx|ek=Sp{3DnR174LOxM`FLTnxXzKBi5ZfN_^w$dB`8s34X^|<k#tgeJ!qr`FqE~-@Xy~5l*-s|D25DRj?WN=g3*vl3!vb`nh#zudLgx9NymoKf@e?rpufy(<{h*+d6j_@*D2Kb7$%Sd4B0$7vazST<YlF4w7$5{|0ktm~}|{xcfqUbH2?v>Eny}c#f6-a;E&;)mq{kZQn`%h8-X9+`m^}eBCY=&#&fI$v4bw4*#O#Vd>wd51#Lrj)-q^_QZ3??jg?etUUNHhv4~T(;odq6{60a1oRVob*c2x=LPadXW+iF^T-^Thv^UawRhk?F?@Qu^!dpCyv(i8g8PrrZJDfJvAXz{S5c_%_u~rrKB12In)hzh>6|xP`gHaX-|%%d*4<Y!Mf_B6@%0b3c)r^1ljoypO?&vWcjZWb;YRWG@B5>^|1s3x^uu!TM+`vz-Z1o8YuYMY=RxT6EZ$%AfmPRtHe7)Gkvq{(@Se$1$KfFB;C`?5i<vI#=iERY$A?&VNZZA7d_rG}Z+v(h`B&YN<h+{r8}>W;4xVGhYps<1y={F#^2R00dx@4eTHbTCu(skG^*i#tzPbN#@s9_HuTLqI>(MeTX0z0N)<=BP?e+Lv_@?z%IZk%{#5X_x8vPW{nksc>4n_X^C+Pn{o-X@}pNxJUb(M83Hyx!fb0U4;RO!R`sHFV4an3^c=YK{0U;1W9e!aEmKXAL`TLV7f{i<*;{J;J{{*}6mq|P<Ji?W}sz44wCeQUQ|&r?Q-uQ_|;{qIvc?l(uH#5XTJD$fP$>rQ*+=NHC^Z~VO#-jf48q>d?Xf%v-n4e7^FWtG%1cd)?sxsUhZF+(KZT<SII`yV-odG-_EILY>s^b?BTvsv#2%DRSW_TuYK6{Sz}_%Cq(-dS0ELuuaw@^b~f(NE`A@W))1`sR_nq>lbe8`SA@AAL@|CUuODgTyzx4U#&B&~B1%{UaFt?0<U{bLcL8nIi{@Z+U0N=bFqe_&jP3MV)K6#W&nvhWu$^$j_NAzIoXSeE!&M65lw{0rTAQLEcaGrV;2r`ULU|eih#oJW71)<r=sz`P4!EedDmNFAC7l;_axP4_|w62L06iPJBa;c=Y)+2K#D<&sBQ$$>>LKg8I!*p`XiB#Ww}rLB7`^yhq2TV_m<l$PYOuzWFhHL+eB6C&o_R)2#=WW8Kd}QRkflKL7b=BEM9}T&!cpy81f!H(p>4la`5Z{c02TRpC1JHRB`ZP<lK3JNM<fGWGgmn_M58_G4d*_Mx9a27InPcNqJMu7v(=BX}H-BLB-F=rg=2`VTpQey(+weCxAJ%;Dg99N#1F(2pe*{eN>6b<Xxh{)S`dzwXz_AC!sfea->t)0}x5^;2@u=Pyp^)A<4VY<L&`l6SbCzI=%KsS#LrZUfBoBYdqNj*Ip79`u><5`N|z)cN!|KIc7ok9G6&P^Z%G_`LXy?PVO#HkeOPRh&O%i;Hhu-5P$~huCkbo%j}qNvQJ_zt^{vD<i&Pk{$9Jtit&gY%jjv@e%r|d|T=mI#m|mYLD~Ty#AQvo4Qp)KL=fKy+k#{9G=xgKR1fQACQRtYr3NTrKPA-;WYC1)<>O9*sp0!UF5fGBEHFUH;((hiOAp9MSN|>aXGJa`}gbRxakv6e@40-M^pW5@%46Q)ET@G?*Z|ZaDPkq3H!R9C%);io!n=%wl7hCUOJvruGbexJ*(pt@n<%`^J(~R;%nuui?6@0jr`0}sq+1(Lh-GOJK_0m=dxVpIqbz1oNx2+{A)3Kk?g;+LmuWIgy-OfUh=+S+3qgB)=B$9`4*d<yQFS%Q}Hde(y(r`mGay-eDXq_Ehlk4YXg?apL_Ts|LYv_E#>a6kn_AxANZ#Wc8dROgVZ;T93;MRGxD`5r&1+<co_VS4tP)d<?$w2??D{;w7s`o@+ao)k?+ICiEp}*jNgxZNJT%pri*WQJq7Qb$6lbHvB~JC?k4o#=KW_f|28_-U6zgK&6^DA(|mI=)_t=>>R8IGmior9G}M2B`r7`6^4?-vuoU&@os<3Qqc2FG`ld|yUACc)`)TRN+HVckjSQ0aG2`_0@*bjH%Z6`@J~gY;Jo)pI+p(?>>S*=z@V@kTzxd{uILx7(<7!za;3(FOK7@6T`^$TsVf-oh@u{+3YoSH@G#)yO{g!&OPwLOCfb$_D59@ASi**aPVs6<tke`Khb-#tur#0j|^j~Er-dnabT_f{1JwzS<y~rP4Aje(%rU1wBJJi>2teh|PT|c4zM;&vxw|tiDuYZZFIB!cFl>I!cBiEhw5We|nJl;zp(=q=N<;6EF36uKP6W-E~>5L<M@6DJ`i)XSgeV&W>)|Y9R=a6lgvi`u9$iIg=`cWr&4>z9bBED`vMEcbC*TLsRYZvyJj=9x~k<SI1=Q#0=`Gc{qBS+<PiX|lxb&~uf-;m>iI-ioTuN$ke?zupjvw3?8>a?7W`bVeBzO2X6P-pd@@;S>~fak1bOuG1{!aMMHzrl0dHVbvuZQ%LSRNg<0p4sTXzn`2B=29DR-_D0`)I7vD9e9EFmJjgFdU^4!i~GZWvKIZ=<Y3);9r0Y)zEOP3^Iq6jyPk4<O^#on{;6r$muU+>@4&aFg<{?6gYjJR+<|p(aoxQwaX)Xd2gj=;`ZPByiRZp?FY3EC$NehgfXq#|z_(l+Ci#X%$#{-O9L5}K&PSii8_W5ie+A#Pu`=pMJ7T}*j-bzLD`mfij0E%(cm{JQAAvr-YN7v+XW_5-8Tsp?@f=)r2mZI7IInJQmN}RL?!w<N5_LWpux<i;?NM3y(_Y~3TPody-{76pH?;^wKL>w=|6LN+jZ4S-RksJ|e|;O-uXzvVqXj%h{`Jw~n;e|Pw<N(gISs{e@p_N<@w)|>=lrix|MwYKH|qoDKhy<%`X9&nnOWkR)b~N3*1`gOZrEQ+e2doz_&M|OezKyh_~zq1F#p%TVqFV->k;&+y&pbT&S#%;@Z+#AeOY~cPQO?F8qViqI6n_gMxPmu=%-dioF_wH%YD_n!Wrv6zKMOM1>wEo5`4|p7w1n}b=j8|R}=j&oQidAp33uG4{r=VARp^)vPJ$zck%V{Avj)d@xH1jc!+P<+XVaVT^{+ap4gYyLCj}QFy`~NCF;Ddfcs1%J6YFyu@n4(Lvf!;oF)6R*6W6T?$*cg?f(a!BfEUz_d|Vigct4`y?da}#2?Y;SlmzaCOt8Swc+Sz8{fM^;9EAA!+8=GkNnQP;K!E1+`No9AA<ehA3louH=OzR-u{@w@mSoi^srU3zm37@r&tE^7tX@<l@H%?BoY0uyNT;1c@U1f(^K@>ZZ7*7EWYX2JRIK#*U``QA*es+cf4P1sUzzePluwPc9^G@6S7e1IgG#@@-R=We3H!H(lQ2h`moOQZuq^>?L-{M`J<3O(FN}_-jmVi>{s}G!B4w0aJ{Br-8X%4UPU}#iFFquKf4Czlh;D})Gsc<zK$VZyVGQe%%k5L^fL+hx@n*EV~)&1eV^X&-EPRbTIa1e|Ff#X_s!2Z5%_Qadg)$+t&4ls&@>gLHAgKv{2%{xNtx>FZ~gE8>C)&{|Eqtx)Vj6j|M#CRWfk?Xy(qq5DBj6Xyo>rJS?M0~E^;pQC|T(_axVES^$Phc`7-q?`7-%B^;@#iJLK!+Th!mkx5zIUitTKmrES0}6qloxCo8olmm^o8Rw7p*SEN=ZS0q=b)*&lxMy^h7NcAKubt5+<*J3EHN;QzHk{zf{WCwB?YFV<<A2e_oa=r$=P0lBONBy4s9r-3h@i){PWTjt|zagKeULY$yK|W7DPCZOMPCi84Pd-H6P5p|jbRBs&c^fsEyp24cp?D%Skvx%{K#eCW9YanakEM<xk0p<$Mw3UAM^H`VVbq~i6L}~(lo~+}B~PG^BTpbNr|uvt-9TPWUPj$ZR=SU@bR~HiIgUD>97m3#jwCA`PL3jnQ$xr~2b06e1F7}NN}G@el6|Qy$x1trmG&Sj?L+n@2UGi!gULOq{m4qYl6#UnQoYC>$*mcR-KfpUZe$l~J+ceA3e}mcv;w&bxiqyrS!p?PX>uv59a*U@S*Z=V6uCH6Bdf1s<l^KK)UxCfWP567veGcJJvop%jI4AhIglJg4J8MWW2qC!vE<p*<z%JH$V%hLv&k{kD6-OUveJR%81fLRFIj0Yc?j8$+LNrbBiWDKjM|#4)Q#MX>_~MXE3HDV!sF`5P+W#uid>4vsSHDLNooml2_BD<48=96f#g8Wy(U9(BsG>C%b7+}W5_X_OC&?_AgUkPk9!`(P~4R2NOt5Nno>)WOR}e?)JXCms`@^)DAJ2!CPVQIhT^#l#Y-8Avl)ub48^OdspR$4&#0;7&&W#{iWf2z&!WyG&mvD_D4s%{L7qaM%22FR=aO~uJci=M)TQLb<P{9XYpB`eHRMeU#apRn@>cR@>T2@ebJ@&L{5eDMTIy%ywd7UQCFE7)H0nZf8hHUjaSC-7IfXo#I*mM;Jc&AmJc*n{ok~t3Pp9hS>Et=odE`0dMbyRQMdS?X3i1lhI)kA&le&qVN#01^O5RA`LfuT>%vme$UKAch;lohu$xvLIp|~nTaV>^ocZTBj)b8Z=<lYR$0aPDy0J$4Ou{YI|>`iXPP~4DOo7|A>%1~ULT9sU#T#2E$BDEH|BDoqvv4QGNHjo=I6t`d~ZbxlTZb$Ay?M?1N?$1y>fEqv^K=!A0Bm0w$RBy78+?Lvk+=?@5%TU~y>Pl`*u1l>>u1l^#twgRtu1u{+u1t2IRwFx*ou~$~6S)qx0l5yj5kqksY7253awlp#awl>xY8P@B&RX%<qL-LKMPXtn?#oczlcCs`p|~GI@o<LXG1Rf-G30oL;#jJQ97~R5C>~1fOCCxNVkquS?Md!U?#58uk?KqCNbbZ?+@0Ew+?^c2P#jDhP7WrAF%(BJ6vt7=kmJY+)Od0Nc|1e$Xlg8ZG&zDANsb^7rVb?!CI?c3$U&S@AVaYqwHw)wY@~K18_DgdoyhIU9jM*O9mt)j0p!kPe`+w<pWL4sM($4@!caVd8buyKj-kepW5^Sz3FHLMTJi5i*T64D@q(fFAw%&4hT^9T#cvsk|6(Xs9}1NIPA+Z(wWTWGmftJ>z)<{-q4*W`1^E^E8AI_S>O=A)@{bI~cc~A^cggn|il0!QlAn-&W+;9`eM^2r{*$5jBlR!xM{+S6sM>!qn}5xv7(;PMhT>9GTXHFK396b`34X8m6KD92{E7SrL-A|sEAngdbLunlbMj;ABl2UimHH#uO1?+EOTI_`iF%*>6S;u;gj_%_r2b6)nX@irDE^iDC;3<Md+JB>d$NrURL$CkGcQRVR}?-)(TkzD1w(NIhGKVy;&u$h;S9x-spH7gsWYhK$TP@O8Hz_zdyz+y2Qn0UQ(KU|$t@X*8&MmO8<AZZifdEd$+gM#7>b)x+mV}++b|S&rG}Hcl0z7ZCsHSq|DKEDNz`QObaFB|g*t<rLY_vQN}fg@MIA{VMIJyMNFG4;qI#3P$jzxO$t^j@<_yL48H$~$u4Grv)S02U21Bt6wI11p+?d*w+?d>o+J@YU+=bee+=U!U4IzhczM=n^dniM3ABN&+hT<e@GC7Gng_=U1LQbSkBPWuFQAd%7k$X@Fkb96@Q@zNo$xW!u$<28TnlKdCq&kyplB-Z_kgJd#sV-zkay4pWay4>YYAbSGvIj$PTWS|_7tXpZwGa7Z(S7MuQRFZbA7m&##!!5Qp*WAB_!>j;CF)7?Me1qlN%Cp3g`xNeHHUnJe4r=-{cUU=i~Udk3H`smbQ|^m|NIZ?|Lafw`(I!E^CyoN)%wrB%nI}`p?-g(*%tjz{nD<p{B7TV0IST1AO'

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
