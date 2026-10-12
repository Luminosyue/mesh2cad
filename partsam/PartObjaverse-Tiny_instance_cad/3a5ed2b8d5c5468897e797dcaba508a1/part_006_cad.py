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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_006.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_006.stl', 'source_sha256': '8476624c4ef8e00ee9ec4e12da0cac0e5a679067ec15d2cc608df418cfb4ec30', 'input_faces': 1018, 'input_vertices': 586, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15869523584842682, 0.23991382122039795, -0.15631842613220215], [0.1400822252035141, 0.3207644820213318, 0.16109752655029297]]}
GEOMETRY_BASE85 = 'c$}r33D{Os*T>KEloF94mBw45QS<OL--<MNNybDyNs%dvsKjk}%WKFiGCiLul)3VfxSK<osZ_d!qRE?x-tc~VJ?FQ!bJl&n>-w(m>$=vp{_B6%-ur*{UVEQ&pLFTlr%c((LHOsmVC$ZN<F9QO1Y#9~%E9QNBd;GmWay}-*IYZMAUL9wmp|$sKI7cK_3d8}j1I=tzjWxRAtUQ|NY(E&tf+pIRQ+KiMqWR1@HK-*jJ$NH@I3}!HEO8iM_oSn+MzCP(59$ulT@pQO;Y1i|HnUvI0>m#-vu8zpT4g1ny$|04h(#)YXYC1w)FKRKDYGBnMr)f3w38j`3!t&O4SdN_+aF+WWMEDbCdYo)6+}&^ybq_`Rw%rOZm*|V_r|<vqg(%M)}}|kPpg@`XG`2{+81Ig9#^x{IDvq{w=TlE1!nf{_}YHPmgUH>a1BaoS&OEO;6&pP0x5EF~4t<nMr(l*pOLKKByJ)#kJPWPU1^iRhpB?k7_YDiO>DHG@PGd4a0S5d}*k2#?I+UeDG73H<I|w?p8As^Op>m73H(q|Lo1PllbCC%g;&TbKTm^P2x+MeO$^HH>@73+h9|h>52R&zr2yem)yQ?MiQTE_3o@F@9VkmowJkpRKburNqq74a&wdTlJE9~_toRbkneMIygm)@>k~c;@9Wd@)Ms&p!jM1p&()>(#ra@)Js<M&IUg*q=Y#S=kC4~%!SZ@O<nf#jme=zkGivAj(s4NlQiXM<C-KGo%DtJGzv9ywNqlDO{8>?6&yCE}H_lGtOWqkVCy{SeFgJ-$KlOVlpSx#!$m_X5edh7hr{%RiEwA;dyg!$yPs?k4T3+kZ@>-wiGdIkS)gkAD<@J29yq*tv`J4~RYu)PkV0k?sEU)K-<@J0>HJcyK+qk`}qx;M9y1$f9!|VRa<Jn)H*ZrPaG%blw&u{r=B0uQa8HxN+KhBEs{@iHNXLb^w**s-V5}!V>J)6X5*Bmu3#$PrucK%r2&QBKJ&X4Ey`B-UM$m@Bc^<#KnKZf`9WAn9s;Pu?_^<#KnKZf`9V|cBf;D)EddC=$4#&G{yUiYu%b^qq|!~RuXpKH2*EwB66^16R5ulqN1-;|Ko_X<5f4e!rS!~65o@c#US*Y^s4ej47NpO)A2)9`wJ2It-xKYw_BSze!Cme=Q(<@Nccyq+8S{Ia}0zw&sVUzXSBS1|jAcs=X$-SGbT4)33j`h2&%zTdXFDt2z@^Cgeh`ZT<+Ps98AgtzZMmiP5(cwe7}*ZRy&xj6n@<9x8Zo)4DS^C2&v^FeuiuIc$;c|9L2ujhm1^?WFqa6#<7BH;bs^7{U7d42!4yuSY{ukRK5{%?7G|Ig!j|F^up|L4Y@8atP?J}s~Hsk}e0sLwo}`YbuFYy8}xf6HtC%Ii6x{pa!YpUt(6*DdFR<@J2X%jbNsyq*ur+uy&I*YhEd=X|ido)4+|lRoYu{I<o*O8HL1OY@WuQeTzwC1<}I=Zg<tUOJz5?U)zkGoKw>%BObiisffUUsTHH`fQBl2R({IzH|8g?fIc4A%E|;@%$aHl=A64TjTxTwZ4=uSyCge^Q~_}oeO8j`MEzXPrBbso1en-t+SbjwjrO}dgOxWyaoOK2+vP5KN<LvkqhQW^Rw3-6RxkBxAaK(&JV=;&ornJ){mLbpkc@tufH$We`Z;yaNSQg^SnIdb8DZ8^`D;ACCu*<pa0B4&XfDh{4au^{8(IPyCI<-vo1kV$Y)wU64RMJe_Xil%z9<vOa2%X@4tE`<jp!}M@?9hv|j1!LtfV_n78e`u914qUeYMs&&sbE5Z1#<`;vL;R(Y+rpz6!<eAYc@`qz30=Jt*0Nsni}n#RZV{OR#=v+%iJ?wsE>iD!L%Kg?&!==Aekadl}w*=Zv#iOx^%qT9mrQF-=z$*ARVp8Z(za+w&f^OLK2Ry<$l;o^AzIzPEZ`(t`^zhuq0x?eK=rpNNN4zos&)?v2RO$(y=IzK_JxK5p)T)9T!e2y71q_ls|x9pxj!gYZUHas2H!(D6UM|s`9Ih)V^4O)(m^`FgL9Ilt?Cw*JU7k8OjdcWz0o34(oOYZh=;qyaz>NaSXP2{uPj*9cFW9rxYW4z9Pa7Vm<KmXm^FNo^Vx=opJmCu=RwQjRJ-;dpw@~N*ckM*zXn>ITA`Zn27+D~rms1eciO5OHQX}<EhUa2S3G2WlIHlOuMo%%zpe_gM%=||Tq)wpA*e`#i9bpG|ZqrBhmo#VXU*PLUSX6L+G>h(DepPTsVt6?42jO$dM_b$~F?3!Q7>-(gxqw@ZDI_qM2T^Hs3_f_V<Wa5?6qI$H>J+JSR)N}EIu_3R&i#Z3B_d40{%KLHI*PhqkLG0h+LwCjc*K=5TKcAedc|7N;^8P!Io}XKu55Ft$eMZ+sdH=hf_W_@;@AEwOeZGEg=lSmW8{*Gj<#itPIqP}V$@A3nd?)eG$JrOYmNY-g+xf}k^|=F|H$OLi66@ce^YC_kmAC8bd9%LRch<j_RBxU)^_DvGw%3#DUwK>qme=}M-qwG5#+28S_M_*`eoQ^KH`c$dOYwVG&Pe1NJw79;f6tr#a~ofnk#xVx+xxY=-mmg``~B75VtV|3SKiEj&?}gkR1eDAdQjfhgXisjuU{1F-|u($y!~!@-S6<Wo>LD$JTqy(D{uF^&o}$s=bQcRd9&Y@xBK1mX1{yh?DzD4b|=n{@^*gmc;-iWJ3r~V4Q3^+ukv<%mAC8bd9%JH*=Dm6>rHw4e3^7dd|c{Zd0YRM*ZNo9)_?ZEq?jJvkDfRCF?-eQSpWWcad3n1`_}IM;rrXRIB)Yy#+(!KTdRh@iy2q>VDeKT&$ym9Iz4Z6rke~7`yW#=e9zbSJ$Tib)Au*Sr}h0!`ziZ!n6Kv~yj>TcZ`Q@~Dbv4Qm(2bdvH3|+C(7&mWT+F*o4WG6sjJ-N55oT2Z!G=Y6fE8!=XKtwbI<EMQ0JaMWnH-L<r~F#yN{H&`$&1ak34VoQF`>xG5sk$2jG1j?&BP={JLl2{h&Xq=YZzhb4K&+Ib->?@&4^O6KpxN^t)FkShOs<Up&u!WjTjE&$?tehdoc7WH^VF*E&gY4*Pu8v4nHj^EwZl!@i&KyO$^Fw9gTrZ=NGQ-#kZrzIl##-aJQ?x6cvJo9Bq<&2uDm#<bWxYyBv1>nD$=etbWsetf>EAD?gPCy!qn@88x>$#vhx^y~ihyxG5=H~ZJ~X8$U0_pkDH|0-|yujlP^u+q+0-Rk+KyglDMZ=ajWoAWKbsq38BJm~ohpLhNn-k<;4k3Ik4^Ui<Gx97j%Q>K4={^#yLeNJ?K^!cc~eLi~L{*G4OKF5PGvHSJUYxun1>F+Nr{rm9Xs$Q{t<<k##UYW#aw=Z0k)KA{;g1sBU{)d*2-LL0I-4nZC<+JzIT$z}^b>PaR{LHo&Rz>GW`Sk9stD^Jc`?0@MlsEHPa{88#|LwrCXuWx!dDD8cyw;oN@0c8`H|5i7tE^1wU+3TUue|L)`_!c?llsqWer8p)o_#*+m^J+?pR)R2+_@@R&t8w&FMeFJUo3C?&wF2LRdH^#e*F8A^3;!iUxL^A$;+pHY`)e{VDhzoicNmr`<U|Pyvi0H5%&M?r?K-~d0$uhok4l66aCJhd}?v*JXb#b?w>1?`uBBZ`uBBW`p<lD^U9?DGapR|_xqxF|GuuQeytO$e_`41xl=CQf8KW()o;JUsDAq$MtSo*%I#?!n}2;DP~M+=ybt8@ybpMu`PcUW<#qmT|Ni_m{d?Z@uk&yF*ZB`j|Nb2QCEma1*BbrIe~IbezR&n^&HGFqZ~D*s&Nj7w*#E6FWADSt>$>Rsu+L{-==-qeIS2H8*z=qN`abM=_L061dtTR3ze6hDf79|Lo!KdSS0wSe?pD9<JF8#Mr9AzdOIE+`Q>)+CiP4{(IB{i?&dkr_V$W;OQ&%NMzwYZ2qhHU-VxwQr$-vG(=Rn5Jzt*AApZ>bi>Li_c-?6nH`yE^J?RRX=x8Jdqx8JdKKJ9mG<?VND<?Zj0;I72;M|pex<nj7@M0s=mC~wan&ztink2n3>^T+e%{88SXKY9FGqu-oAp0~fJbX@y;%JQcFyzhQLKA-sfRo*^-J#U`Bo;S~5<?Zv=^XB=hynX(9o#y%LdGq}Bym|h5o#y%LdGq}By!|e!`t5g7)o;IxDsP^@nGdHXzrQJO-{0W#-rqFezQ4iey}!Zdy}xNc_WezH`<?d1mGL^!@3hLB_kYXl`?=@M`@iz`{onKE{onGofBXKgynX-o`R4uK@+qs|y#ISW_B*zYYrkU~-u9pO_c(v9jn$9;o~*q2{iwYC{pj<}??>hB??>hB??>N{{a&rS{d=yqyW{7%{*H#v`+W_c_xl<?_WQbT>|g8Mdr{lrMa_ditU^#Z7&bWaPxXY9KkAeJsowC`|Eqth*P?lgqW|B&)jQ-Ar{Mx;*E_4`Oybtg8i1>TFCadcxEguFUFz%s`gq*ggEIY6D$d$CJJs2-&W>P;QnC!r`pP^ydrH>L*?&2^+SzT+&T@8S>2wA`0d1vSC)!H8yJ#!z{y|%5*O|7`uA;Nkoi%ZG5m@}qVDT4|FS#edUkq;MOxF2mXM@1az#}4YQ)hp3b{M!B_$Xq@zlS#C!Gpk06AQkZcp!K@_!?rtU5J~42ZE0xmT?P-%YY99S0EPM$8%q2gS&#;5sRif(EL339`M7&qUkv_-wwVT{1CBd>WAjK;4a{{#G<VR`i=*e0k<O-ZI=<>0X`f2FtKQRg7`V`^WcYwMcXjqe&E}|ZHYx&b>c#BU2p|r(bSOmG;j@Yf8xuCMe~i|%fS7KpCA^^qrp#r`x6f%7R^1t!@&KCs}r|n>>h9p$?1XChLL;g5t)n8k-57uGS{bZUq^BOby>@P%-hq<ugvoZ)<f3iXx6U`ZR-Yq)vmPDT9<aZH>92JH)$tzEBi|7dmvc+c(C|E<V$Wd_(9+n&Q5lAjI+Vu7U1h5u^h)|I6EBN0$iC`^6#U~E#Sf6XNU#gOI!@T1$-^B;52b_a51<tv5Z@m_#p7%;6sQ-_X*tBx!{w*?TJOx-_iUc_&)HX#G>g1G~Wrn7yJmZXgUYY^}uOx5wU2ig}xKO2Z7rYi?-p!e+Qonew0|WO(A{({37@fV$pUv@j2i-!9~QPttN3<a6RxL#G<JYaW8N!@P)*~iAD1m@Nn>j#8Zex^G)C>;0uW_Cl<{;!Iy(CB(6zZ#MnLI8j;fzt&Jl0)-y5}H$~=dOk}QmabK0W|9Y(DIn3KL%&*Mzb*zW1%Q39qLA0$G{8hWsPHSD->E4iby5FRo)UE6*sqbR2_*=l@2a_+kE#L=(TRH3Qtg5pi;8x&Kk+`L^Go4iew*promi+r^b1QfV_*r7XlZY<?-wGZ{EVvtSOYkM&D#S8wIpXr*O5j6@MR$Gf>wIu`a7SX%G!e~H!S{nF6N{#o&^!S=3H%tbXgUwgCxW|yI}nSuI_RqpE)VWVEZVLlo(Mi4JegRuJxTl$cq;fYV$pU5@p<40;10y1tu}Ev@QL6<iA7Um;y&Oy-~q%}5{u?>;48rch@T`D&11n&f(H;^K`fekgRcM&Ag)c^fw6nTH72JwS{q01t#@QD#zy9DTx72Ma9>rp{}Wlu^O(11nO~XbQLKloOI6mdJZ(=5{;FMRr?oEabZ<yI-EY!P>Q?rZ)b}M|@wbA-4<TQ2Tfq+juXeV^*&b)#JIguy#M!UJKXHAUvn9^H;QHInUZ(wGXW!Asuk`T-d2;Play4%=?Ovhp&l%?n@?PQkR<19h%{FHrJA0Gdx5-(;nA_<8SMtAuTY{b(8rRV7bNYInF{g2D8+txR`)0;nj4mBxD|57s_$Trg(`GAUe$TjD$y-hQ9c{kne!c+9yuF6*Y4j=MPj~hf*WZBKhR(O)-{PJ=r@tliCHen!w!+y5&el3x?`*HLADw;UY^Af`h=1Ywd(J*{wu$QtoxMZ*Po4chAHUH@mOQ!kF1ecbHSK27_Xft<MBYrU@8J4pwAtxwnX`H1E+pqO#@tE&zmfj~+-K<d294`!w}HMsWX$)twi7)Y(Ec^!eu^#~V+V7zllT|%Kc&qM#{7|ScaXQ1_y^kj$o*^ruVj68JKN}Nm9x3d7QyX<pToV0?teM^mfWSR@eK0jJNwAlm(JdIwj6t(e&6N(W;^?ezE*)(G44jj6>c4U{p@Tzem~=EBxfJ}e1)#L^d)U)(S8f}vjSfG`zO~{(C1fZ*hRbLwA;?OKXYwA{C>vYLe6fke~YG{=||h_f}h2le97FcV=nh|eIN05`kq0Xb!eK)7`uqSC4XJyzLwH<0qdM)?xlvL-WI~k^?7icSm!z9UtSOd7dbn}S#d!aD;D1u?pkLVXCsLfi+_N8$sO$MI%37*M}fuv!`WTLip4(#7XJu+-xa}+FxE)??ar<sRxJK{w99>+=j;q(#p2IGmuNoM*>GaT;x9&*Xui$aqr{5EKZq{TT;l98V#VU0Mw{rmgz>M4;7ibR2L61;KO=(AN6&El4U9iLf^R_2qxi{;|7ZkHM$cpTyP31cBKYozR`H{q4Ix%6{zi121$QN};vwYRfM((DAXa=OIg`;W+&#pK?;z)HG~dJccSrC&<XjIwn%v1;dysMOK+E}zeHQm6S|4B@Zf89oWzI%1&oak-Sr=K8i&)3=X!{85rR_gxFKq|YUfP~Rducn8_OiF6&NJZahy@oDOaA4wxfU$fzIRrx(7oq5>*}n9vtylAakkA}t6CW5d_i7)XFD9O;C!>f@Ot^e@S3z~>TJ8aUd{QP^e=rM?Cf=iKXmqHf&3HUuze3_&%sS~w$|Aj&OV}DbJ{jzoceG*&?{}0IQ!Vydi<_}Q2P()m%iTO`nrNp-xBVpDfj*ZW6KzCkT2~-+w16iiCC`pKvN6m;0M}%$QW-jhK#k7`C5;*6B$?T<4y9H(C>4ME&VM<(^|C1yf<SGWZaj~_8fXzFefr!)mVoQS%Y=V%@XviXPl2&i>lnu4#tw}Ef`C*Z!HMdw;c7+0{%JHP5Ro(yjNlTuH=@d-}>~kh`gQD$+2i|PP-4Ox9`c3>$@0ZDw?;Fvxw^z$f>|sS_?aw^XBNOhMu*|r>@gfa+*?GYnlHyn7f0SPr0`)<ZUBI)~YGIv|UWCXxr~;Uxj(@Lfb{O|APCGxn0DXz6Adv@glgz;4k36be47YwzE%&6^nlvZnv{TT>t+fRxG|jVVEzupE~=I_KL;t0gJEU@~anyv10LQu=tjRVc*pwxFuuBxZ*21+gK3BipBqgcDb(^&YmY$EdCXAiRO2lZ6H=GelGe%^P$eSLZ@Q!4bdf<Pjl9qSh4t%(I&c<GXBO0UW%UQ@iQ6!`3Rngo(=fDXxb3L;v1q(d>h7Z6~S%L(;8osd2AiQH4FdJD*k6@pAjn-{|mZaf!jo^_%m|$qFK1Z(5ZM6Ic?A^TrG4e7B4w9(Jb80#ENT?^Ao&qC(}<Y`rgZ!bJ4j8?Mu<xfO)9MdbVQD_Au`<$1k%k?@(VGS;Gdbdu!U(p#2`|Y6G?QHtn<2?MC)ib!vP!`=mPf6XGoU?qB48$+fSX&2u)(*)n3q;$MZ^=j?FT=WoP{#WyMp^Cfq=vtMbiSp0sl_&P4Xc3~JR7T*mlzHMRHckKvn%UCk5_#>R<3c^^i_<y5a?(3h<ULaO1ej2(&^SjPA6Dt-!AAO>^lJo7*saSktbcyDk&WeZ?i|>v$(Y1o{a}m4(Jul$jWBeB)_&xM&#vee_<_H$w7;WO)Gk&`WZjYWKe2RH2ir`e?Us}cg?rbHoV)1{VYZ~0w#EMsva{$f49f?lGUz5`w&B7grPQ~ISCxvF=ekWFZ96A4n7p^<~97o>=7;`>4zef8Cv^HWMj$l38F=zXkcbVf?S(kUIuN-UGh;=WbZ5`V0r>-_rYqMxSkGjpVw`x=4``9P7!OMu}vG0B(|0}L-akjwO`_5JoD;7T;?oVe&xjyADL$^e*_$Gy6zT~cU_8;0S7GF>pV)4g2t4pj{{3&4Z9q7Am1b1Mp0AJbJw*_IWSbSk&s9o;s17|OCFN(##hAz=O+u1k7ip4KPpJ+bXSx0m#7Jm}DL~}1^oro2SKNW4FYYpQ|tauH2Uc}E~{1+p54tl=9mtp*GBDf5CI^sJse#Z#zjGj*Tddyv?2(DN7msas*oqdi@#o`Yt40VZS;l4wsV(|x|Ya!e*#EQQor!$&`JAqj7F^p9Y%_pF#UId>&P9c0*ayxVFB*r}kEpyQG8uukyn=lWRS<jBlSpoAbb3C1OnN59t%NjOe-8<3tc-l+b)vVie>hML{2GoV@t-93spX`~s;8ny6*oOi97Oq|8Y@o9XoLx$+SbRUYo1ES0Y%H;2@eh$NxkH_eAyzDY99aB)&h8~vEdCj=_{Zt{-Uxo2vBu&jIJ<^evG|+OF86hzvonbmi$5D(qPf4btBDnhAA~N^{C8(h5Gxk{FuFwZe>s~%tXTZBXcJw-82_3G9)_MX@dFtD%m^NUo~!ZW8UN}C9*>?U@J}-S6A}C*dZyqfF=taEcv3{G_*<M^Myy!;t>`)%ZUnL7%g7mzX5l6hD;`14lV}$1eqzNF$(e-a`x$>y1m922&G5I7`y|&MX55Kr8Nk?Qb6=wMA?9HM>-hw8Hja6gIqt{0$eIjf9WSKq<FuEy_t9S34yC=cy@2-8b}a2>Z%Lis2_8c%_)=oYzlt_Df#q5YXN{fJcXkr7V(}-ywQ<(jSvz9I;!h=Ca+^A9ORQLY5m<aTXD1UY7T*Uf{xteNIf74PtakXW&RP*G7T+H2a$gOd)gx9c{zP<%<_6AM5-S$p1YM%Ji?g1@ipBRpmuUW*vtGoC#h;Eg(bbIcTSag)^wh&QV*Gj$+z34_@f{eyWdwIXPfvVr#_t)yz0uPP-<>(@6~WyjTE%yC)|^<e_)h3L5w10{;^yRZK(laZV#Te=>5XRLP9avDCZ{`^PhtG-5qt_c?cqC;+nZ}W7&ncUMvQ$T_a$0SWgfb+o;{hfBIa4<_ypEP)}%4(*pRlT(O%kiqrJ3kN_%NrpZ3zW9qnarNu75Fw<Q*Q60zjBpiLXFTr2Oaz}X+}(OiaDvG@Z)$Q|nJXlI9!qgZ^6f-qll%Q|0?Sh4uS!Q!hqt4gd`{BdCMwdlKQ1lMA$!|=yAt3a$+d?mEYef`Jze+OZ#Sp4s370rJ-I~bjc#TTMWG*@<3n^>{<n&=YE$2+S-tXO<qw27{R&{QFU#s7{r@d4xiJA%cFo`dm6F#f?2d<1%G<5P@ZJAzZ_se?b3Ija-F$40b@Khjw_V#VT*DhPFnX5kJYR$PvpBhV~d6=KDQkds2QaMg(wS0U$EG*@T*V<WgaIhEj#Bsayinv7coEdgWy&it37rs^;U$1!imv;GG&#|K!KKdG+@tYHn-y$)@w(O%k?rG4K%1%;K%{7?Ujpuhge-y;RF|6!1A8UN=B(Uz~fzWhI4=-cNY`EQThJ9lB}f9Q9d{8xv;e**^Mh+h'

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
