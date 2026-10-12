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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_004.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_004.stl', 'source_sha256': 'd415709f2cc324c719551a5d9c9d7dd4a829087cba46e34a28ad1a5f8d17e8cb', 'input_faces': 868, 'input_vertices': 498, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36111101508140564, -0.4999999403953552, -0.2916664183139801], [0.34722214937210083, 0.2909685969352722, 0.2916664481163025]]}
GEOMETRY_BASE85 = 'c$}r22b2`WzQ(%&1Be2ON_JEf!GwZ}=w$~%QId$FV!%N%B4I%gQ5X~x0tPUmGQgsOf{1`(U<X)O^6rw9=qQ*_QS@HD>ht>g-}U?Vbl1*1=biVKQ|J5YtD5Sss{Y+wUEPN+9V%9;>6pJ$on`-itxMDM9Y<1Cr=~NqPyUDjz4{D4Z}8C3u2bFD<xg>H=Wd<4ba$PR&X`8M`wZ`u->7A*(dB(xG&(2NsPB;c5&1m_-!UY=cOTKO>N#k5A5S0Nzvs|CUjD4+m$o=3)~xY4u?J%R$G<9`g~YIWpA>qS{`>FG1f9ljt}hJfarC68=Y{qA>*cJU9#b!8{mi8g?DO@WGfKnto&DGNda8v}7Oo$=_ZVN#%s4k%zvIrm{_#6bE)CaDADp+#Z)fhjErmJs#F@oqk#^AIo}QOOPkZfz_2k3zcKF!4TcjP;W1kO;_{>Z&y5s42IrNm*PQ?Eb<2!lDrJD<L=;@~U8zb|A9{2RTT)Njzr2VpbCBB~#e;0@KL}zn6=d=TBBki<5Ym<+=*Q|)>ZF+9->!Zhd?O&TKepI*PC(y0<3EHvZM|C@XRJY?tbvu57`d0h|$F<_e)-`^DcC7fZb&Vg@?f9{Ejh~>uR{Yqy#!ukWiXU6o_zA|}il1^i@e{OT#gFQC`~>Y-@e}A){3MnyS|#XAtZw4?<cV(<=FpQ*{xv78C!cu1*PVi{3v=no(p{-YJL{%y5=_;<W>GFZ{^9NyBkkO~$M1jo)b8)*(v$P1KO5HLn@%asRX@<}`ps4u-SQLYwx6=NKi_e?zvxa`w7=;s6O3LfI-Y_46yw=;tv_$c%2P`G@o9O%{9Jl^U*`fp?zWz=&j0<Dtrqz6c*V}Q!+Nr<(KDs5&Gh5(r_&<!6BqyRR#*?}4}7U0TL0A7{k&CQb>}WqKe6p1(@t^1%;S_DZ{^aH6X!<j&)MsbbIPudo~C}R_w04yaY%l(Xi+Xb{X+8>{C=Fh&e!8-4p{ED+uDqe>JEBb$LE(r(ec^eaZy;;@o`?<_+qra83((*>T&8Ps{bc44(UrTUX)8uwr})OL}wf_c71fGgQ*`&-Q{1WlLe1#@cX^$z?-@BShwkOBKqoeCJu|N`siuud)HB4kH31vR==NKK9}y)Eq*7gC%bg@ue0&H1}zNh3G~Euf2|AavG_{=`j)(``r4fO*oJc>$8ECRzrH!YUNk*YA3eS6+|~ZPYyEhW9pQFVPgh&E&DZf`>*_yfXG<e<T<^?Z9@1l~=M}H;ah}ngDn0i2=jV{2Wnn$}0{6SR#SuN#{<lwkKUV#Cok#rpf9k;K(y$&IHOj0DtmCTgU1)rtfxaPT)<KMqt*72kf0Rpielz1-PXFto>3LzFPd;hJxqpq#5&w+8^I*fd;rcQ36!Wfng1CwkSGJz4SNu-6ogm&eoceBI4&AwX(87pM;wtm&pGymK=(f*<#@m0a{-P%sx0u#%S+X}gU#iFVxA6O$-e}IFm^D7J-;5vCgE*vLwyyn(>v4yf^;?Ga1AX;svrc1PY~4B7rZ}u?+$M&PSQ*w+#H}|kD<V2^8@K9f+{Pa7SrpNUlgzi~xCv|A;?z%lJm1u}uIH-T*Ynu&5~Ew|8C%!&jOzA!#@2N`6SQNkXKY>9GeJAnddAjuJ)^q4o++o>^{w?xIo<YSt!Hdq*E6cy>zQ&o>zUN7O8)&u?>p&zI~L~BlS>L_M0D;uvCpjfdOuof>c{ppGrFz^UioB6F5Ma3=22hY+t=6i{+?NK`I4}%_xI%VI+LRHS?4T`)_2;XzijF!FU&XXa37D2ZLlPl?&MdU9MQRt$L;!he;;n@r%v7#@sq5vd|oa+<F0%ytS2A;+pGs_M(eAdtYqptgKKRJkB_b=RkzoZPUh5&k$LQ1<K0}kv*Cm1BD&6_T^~KZ(bP{2ZfW#$JDB*IkUuY{KK0nw!@4uRpZ~m<d^lP^(5IRDPS?vfM#k;w!3%Qf@$ofghxK6GrbX+k?o2TCV}Eru?QmU6cboEjE<IU1;Hj`4#No7$QaSZ%V;}b0>)OND^?I0jZqDLddUE)lMPXg%H`%WG(p-AHu%}t)EF5Oq(fjNyo_j6bsgwU!SdaCa>)&USGuq7y>kfLlV)sZpiMkK^_r*-x&1-V$$=UV%^}q9u(Nn)n_3szKI>*vIX4X0A@q*4~9WsAhQDF|<nNsv@SWmZoe0$iBt=oQLzxUi0?yu?&dWQb0o}^!?1LKzE(w*1q7378V%&5_39Wu4(*|45QkDX9|d0`ISnH=p`3ccJo>^x-FXV!QII_t)m`sBVJdttv>&uIOgop<{4d-bakJ#}IuvyR>JPDxl#==eWl`W3V0B|*Pb&oKTvJ~3-v(u`-!o|nD@m*&!)+3n_q+X>c_jk_%=%%MB=^WTd2B%bYdH2xDDH?HIM>Mv$Jb6KxVVcp3)&#Vs_AJyZ(9Jwbvo~p-|_B87#s~y$jC;wa=)-!$CcVr!yQ2mD%W?#<I)n|fs5|&Tz1Xvx`6Zmvi)G7+=x;{*tHf2?$K5<g6K5?S$$0tpWT<23Grq0i$XJ&stJFExS`Fo=ERZkaCf8OEfb^iC63v=n|*yX9P9$f$bh}IAE(@p(Y{#l#CJ`+{{emj@$R2@GvtgFx1vC;a0f9j{5)}|d@=bSY0y_|agJBIu5b>Mo_j$Y?K+O{;T2m2da7mtnBXMC*s!TM*Lsh@uHCex0tbADa0G^hUVW66lF>mR$mu74Jr`pE{<jIR3|J=!eJslWg8(-EC@MbfUX`ZDUT-y7+#Gq~?Nx%A}VzORJ!V0|?tT0dA1j4<^R3x0~sdwRv3g}L<Dv&~asJ&1>u(fX=qs2^+9!#qE{ve)c;ZC&+7SWmZ{;n$CEGkWsiy3M)#*t+^r-S%Va>L;<;JkQwUY3n+ks@vmf>pGsX`_3%M6%XZf;vvwjcqpe64~f#=CAs3coK8Fkx)sm1uJN3DzJE#1^AWw=`54r<&PUa)^D*=MXw!~$eJH1MeTY?=RuZ1~;Cf~0!SxEg-1W-R^?H>!v^MIW>#eQp^;UKJdRtECdYgRlGt-W>-nMmJZ>w&vx6A3Qw=;(h`ntW|wsl=^t8TBiZC%&fvBKj^!@53ysct`i#UDATG(0cC{n65c`y+a}`=g}?_s7%oO2hM_&qubd&qu1;&quZ%JRhAHkNDK*yK*|ucdFaZcja`R@8X?1nRcw_Q(M>P(?GYLPi<YFPm}SXk#W%Haa-5tan<eTaa-5t@mRA0qg(q4wyygLfo|<5*t+f~WcJRD#GCGisBZ6vWa~%wLjv8}4~h3M`%U)#jIHbbO#I}vrQ!2P_xDsUx4-x2uE;#<{*tZh{!*Y@`%AX2`%Cfr8<mCI(f28~uJ2O<-Fly5>-s(=mS|a)tG}w-{f)QnQ5K$eeSc)@`u-@;t@lT^uJ4Z$MSaV{@u2UsRJY%MW$Q=Zf7!ae|8gcxDvQJe@9%6~-`~ZmJ{$29To2L9T@UYE85swC|7h#_{xQ(4_m8%&?;o8t8>8dH`%u;G_ovzV(f6meuJ2D{O@5DzgTDW@b$$PvxTD*4za4!Jtz`BYlIZ%J9_Kk-b$w3H@LU<x=lLtmbExXUe#^hjcLG6u^d$QRw(d9!{e6SrxIEXV*?+M04A1+v?mTJsG0N#rn|*_Fdd>RFbLtDm6@_)(H;7$n_Ib+bUz+^{TTd34{U2L*UNid=<?4Iw<kI8bal^Xq7saf34EB-OPq6i5%IrIp)B6ov8g4(>$C$l;ZDf4V)9mlry3@q$hm_Onnti`=dOfpGlB=DFu5mld?4Q_r+#83muKOzXI0XBR);I*ZH4ec(n>D|IZq1|W_B^U?&!g^JI#yf-`<Yh!1p9kdJO{cJ&w*~oGkVH8kAnR`>par^z?5}9CfN70&v)Gqj9ce>cAwDfyQcKG>@USOnf)czb$=<v{!%K4PopQ<*HS&x%IrI3xGt%#`(t_?3v{k;arT!~*Zrk9`%9|pzFE@p<De%jKWX;U9IIctuc&bww4?it#CckE_S4i)+Ul43S3USnfc-RQe~TUdae1$r*6#sS58nHy&3-t#gRa-@puWDx|AY7YS|2^Wo9_g)zP`s#n(rur`sf*bkB_eJsndK%p?XSnzPnI8xGwRXiLEE~djQpWzhAB$)ve<?`aKEn*=^k!&wGFLOrFuxR=-qFj*E_iet+Wp$#(+UK6*yKudsCI_vrX%8lzj|?*!kUER4)=rp)Mip2l<>c)y?Fy?>zdo?YWd^-N{+-apOvC#q{4rukka(0T7~*AK^4UP#xtiY?=N3H8JG0BPGNdYtbQ0-f(D^n8q2@tM-^DD1dpeq(lg>h~3vo*ZPpuZY?4NgUd`!*?mF>-SFO+R^yrxN+6_enYRHacdrR98}luC6fAmg^n}dZ>05m3~L^f`u&EUkIZArs;}Q~`0aOzd~HAR?yjwxHg+6Im7SVS-=5)5?HikFin%|vAJF`N^{IV}i~rxB+E?~G9P6c{Ny4josXAB#JQiL9-WWUsewLRS^1FtiHcs=>nO-`bB)pNA&IX%+XTneR(urO=A3PU+o|n$?(n(-VczrL`_R=X}UHB>Rqri&rBfRADJD1<o$6I~;*5~)9k%U(PkAk1zrE2t}TBuKz2!kWR3h*Q04Zu3^2Jm`dEqFb6CD4H%4ORw^gja^23O0Z@W{%Dxox%K^L3u-x@EF(t-T)sl=0@h|c<?xQMaH)RSO;F4@vQ|q@MD;R(?K2kTKu*)SQj3{!_lCQ!SQ%Ffpi@6a2)efjZ}qWR$=arA!#feMIVkJRm86gcfbnpF<!wCFO3K9fj{e&J@2JUz)RsZys}fgbOLxP{30)1f_4eI@OEChhVpAD6Mnsyx>4SZGT~jlbOYr#P$v8;FI`Rf)szWu?xl+<znC)N4ZIYiJVu%D>RvjY^5ZEJ{)gAM|8h*Z;PKS`z~dh|ru-x72!G2<3mj9vfHL9pz4SKaZ&N1xLoa<y`NxzA|I<r<QT`WYA2QA|u2L@e7j;K?Jn5xD;JxrW!M@<V@b+K_uphjwmpXc>H`pKE8$KAk51xdN2gksBxW?0s;2?Ns@J>)YUIDfT)#HVD>H_wLcY)sw4u%iL#|SV9KMzl5f;YlX13QE2u_<^3s2=O#sUg?}-VlBkcr#o*^#Dh}E8yv9@Jx7B@H9|8)&ZM>>hUBz9S1gq9|x}jo&{G==Yc)ovmE2;4e)6ABFA7=^6IfBSO-*(4xSb}29JYF5<U;C0#{EJ!1Lf89pmW+@D2E@;37~x{s$Cai=3>-e>=ug3KSnHlJFbBd2sbK3#<T-JI2%1;0^Gb!B;``_$&AyP(8ly7*Dr=Dflh$_TY_h_0$oZ1#gX~Yrw1F-NBnd^|%!L6;zMQ@N_G93;b4i2e3U{J;lL}@J@K@23`Z70d@z~<9pyzP(A*Rr<vfb@R{(Nzz%Tr)EbP#XX9xu*bV+JI0ICVzk%<8>d|$LrzLos310$#6TAtoo;rc8;T2uusWLbheynToUGnPjZ}2xzJ)Z0uPt`#2QH{LtW574z>S;FE34Xq7JT(F<!%qi~1=Zt;p!ho0&3dfw8c%0{)!=8q8-vHd)l)@qHvA6Pc)AH}1iuzM9aN8X!4pCC*vvJat^?12UkC3FHioOG^TCSnd+>BOcoV!AcrB<NF97R;>hVfE^#QMg_kj-qyTjGf9pL%!@pu{y-VN^u_5#&o8}I^9J$Ay=0I&~y0DKHM#Lcb&yK~I$coE)#W48hIn9@#vjw9F+ejoWU-~hO+N0N9?(of-iDeDJnUtjd%<ub>tJq0g?PxsP498>-e%7nk-r98^>C=>p&ms(NYiZbCZdFgV>FQ-iS3tnnTc}vQKKj)<ul((Qv_%ttFO!>u>34g{*%_(nAneeB)bRp#zQYL(gmzq-ElrrH@dg%hnFQ82L(_U&uc{9p{PxaD8lwU-da9Ph^Lir_>372`3^;T`ytix)#X8lte{X+7hH$@k%9(mF0po?}AdC_a4i{_9QUG9&y(d6DJdC`AG7ftR_zoIWi7ftRJOVQs$7fr6&@1g&OE}BbT^uN(XJDI%bC*o7I`s78gi!NF-^0hd>YNK6Az82?2ZM070YjF;Bq^uKKd-VIg^njO!g2UiL;kSUd!f$~$0ndgD9szFxuLRC<46g()a134tFMxLeuY`Ajx0UnE`)x}vt#Ayc9m89A{8BH;9;Kk{AuUI5Ntxhfp?Yb`)3nus->u-cE2yJwUPk$49A9`FFTLZXE5L>D$zHnFOOwFP@X6G>7Hku$w~+FMluhP$S5SThW!h#N%G*#TyvR$dz0}GznCBY4%Hu1&^bgnI<*wnYsJ{{{3f0S_Jdd_k@w-<1wiR`>%_7Q+IKJ?aUW$8Z6xbS`@X|mp^#t#NC#W|N92u(Dn)23^CHUPa%12SAZH}aTBxQFIcdrv)g4e?(=Eo7^g2Un0QRhmq9b97gNMc;@9QZJPdn<T5{7Qb?7Q71Hgx}r*-WEEyZs&XwJQv=U-*y4J!f)ZXL&1D_7wQy%ufflz%_G30;6wTC{oq)50l$@g3m(aNd_Q#_0LQ`Qw^yMFc7;pd=i^=QEx7dYBD@Hm0+-`dXKVx;z@;xA;7RZgxb#EzEM#s4|74!8;#gh558yIZ&GFkDulXFm1|DiKKEfpiK4cC*qz}T+!P{+MbGXDnJLa$*eY>48{DW~6tWIB#;8=6$i+I<V{gW8{lVb}X%h-+suZNF=4+q=9-}TZGFD(X_!WY8}!S~>W@HF@kJPls~PJpj~zYjhPe;>XK{1Cnj{sBq&M_&5T>)TIW`W8G4{}z6bB>X$@XZUyUJ>W0!J@CEYKjC}f`@ny}_rbphe}I1vKjftWUK;47-LAnsuHjNPj=F-w;o|2JjxYEqT>AV4V<7lBT>3bcehW^3%lIE+eguCA&DCz^L~svW=5!b3yC@U>J>K?#gW$j5?VsRdaG9SBbCkiW@Ne<<Blr+p;^9Z)<wv}xiM^fp+KDIO`|z+Ayel+6k1-E|kHaOFRuVTW@$@0_^ANEk_%K}J@F(K*Cp@j-y!Z}Z-{DF4UOemp2g3h_habR+aEbZ7#Q0u33I7QXhruV{690!eKMvzb_#Te+9XJ3k=jr$O{T{Evf55{ba2)(0VqgNe7k(HIKZB3JKOpv&frsJW;o%@S7XAZ13c<zjfjVw3bLeLIAo7AM-7FtYUNGZk`8e`|U$|L5k-XsNZk9hzUhuG+<&TjU{K?JoN68ER=w|sN<OL78S^fn1C+NTOhsg_m?`HW!<ORQTvwQ-1!JTfFk0md-%gyou<OO$g&O9o8lYWCw!Y9I?0-uFH1%D2F3H}^>I`|-bI(#Ph27D&G0DK!>0H041{*IS6${c!WGx!C3GrW`}d@Hygz7@U({1Uzfz7G5bz7D<~+y-9{-wA#K-wEI4r9NJ|P3pP^H@JpNS%2yZ_JWI_@f=@pBwYIZDPthG4K97WhkgqVfy?-R$@~cJ56#tj=0tD<T;_Bw<!dPuz7ucj!36wEynO@S3zzxX!5r<ttMJWu+X&tbmw5P^c=;Ny&k=iT@U;d{!q?+r9e77*e(q%+1n+}OER_*AWq5j<__>?d5gZDaI6O$49>mjh&Wj>^72!$vIy|faZ-Z~c!zbVaaEbX%#P}vW3D4l+3or?n_%Gr7D8ZBPH5_Xz*at4>>1X);46njJ!NV@FKl~+P;6ZQ`{0ltn2gk$b6MF?<34ALaO2K>J`|<G<I1zpu<0Z!w+~j6?g1lgvo8`U83+`~UygzxtPu(nkfV|)~H_PuMFIeJc`Mu-?54u@ClDy#8ZkCTH@1L)3mM6(4>A&)!<OM%-v;1!If<<nY4<RqO#?A73$P2D@v%C*^!S$Rok9p|{FHHiUhEIY&13nLb2EH788NM9;3OEb?3Va4Q7d`_%2V4N31D{6{zDVX+#z4j&{2X2aFCz)x0v>>Gffs{c!HeN*!LQ+K;Typ1@D1=!!5#2V;k&)m*Gsp1X`O3uqieX7^`oxfopAB<AjcOR1(!a5!Wal{g-aiM({I6Ha2fxvm><Cdp}AVeoCt1&%bXTdUQC(rPw}<^><Rx0Z(oC>;W9tlnWOD^6<&h3P2ga-#KSkl%QtvkPVBA5*J?Zo-++g;V2{xJjAkAL$G|0)wh%X4@U(#V8BFX5=EEfpza>t;#nUUC7pw5K3Qxk<;-MJ49ljk8JHY$l67!ph@y&P={uv%V2S>mq{!2MOO7SGTm}6}L`@-cs-G|?Ocon__54*vB@Rx~!S>R^)=Xf{(J_w&j?9Bm7;al)f2KI&@z{fM-B>3%&mmE`Yvzz5T$qR0Av;0o-g4^9J??+zn6F1B6Coj0w&GIqi1xwv5A5C8HTQ|!`kr({N&GHAy`{%2h<s-<Cp#RGA$qVjtvwSdl!BuXS4<j$Q+RgIb<OPe}EbmKRa2@B&BVL;9r77T4_!Rgw@CEoZ_{ZR@@Q>jyg0tZ-!c*XD@D%)Y@J;yZ@V7|97ka5n2e(4aivQDpZJhm+cV<rHKRUL58U0K%{L8^!Tfs-0T{;}$f6G_F`zM3CQ{Kos{|yNo#3}'

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
