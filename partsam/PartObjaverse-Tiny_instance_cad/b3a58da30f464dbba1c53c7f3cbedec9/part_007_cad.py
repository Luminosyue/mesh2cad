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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_007.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_007.stl', 'source_sha256': 'dbe5e258ec1012a3bb318da724c03f623cee89cef4138844a81474e432a05959', 'input_faces': 1192, 'input_vertices': 869, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09671875834465027, -0.4999997019767761, -0.3079603910446167], [0.18805286288261414, 0.3183766007423401, 0.25275498628616333]]}
GEOMETRY_BASE85 = 'c$}r2b(9oGw8nb|cTFJZpo<2#V1xVOE*ae2gEh9eyALkG-D!M<T`XvjK@!|81Ol&b-LIRjTK;(FJ<hr3`}Mb%>gww1YO9_)HDbg}sqw!|T9zqGO8rw;(<l;ZDYXIZ`}FJFwte59d-NLY(vk|F{#iOJxM8h2O<mdmZAehN_I=y-3HrqoRH{Sqpgf+S4n6zy>(jc&uRZ&;YfpaV*4_HHH~qeyTK8&iF6Ss-v_u|Hp`3X<!#w}TfAP&K=+lnvJz}c=c>S|wP4!+|ahjGrIg<!KaC~wk`GM8D!=1j?X39D8jU!V|(6X;Z(mg_3RukoTnl3)ge#hNHbIlXw_>W8qclzGYVWJ%E%|=m<aqROhv7QfCB1AcpH%2;rqerLn<m=bw9i?TxMYo-z{x{ztzg48uH+lqfe)j7k-<Y;!yC{D{g>X^-dWFt8edBq73!)wL1Bb-+A1k_zw`+jN_xJgD*6DjMCFcAzBM*zbr@1$B{=HD)4{m?n>FWpXa{hzYq8*KTr`B_R)-X~2OwW0zZ~VMR<ZEeO>=VlwGcM=$G){~C607wEr*CZTdr@pxtvI5+{0Rpx<^7mc)F*H<$pxoxEH8)rf?|K@db&}f{0)yzaedNWbo$zy+ag~ZnMSmiw&=oOQC`yWqCWcVqZgdM)^MH3_dMvlLzL5`{!H=zPqY=~>&vEIbo$1fOn->=)(YM#{A~VN;{Sg*F7iG5@?CWL-nb7@pY39QXx-N?5#=0@e@kq~ovmleI(%*J)th3wW3`HO`rfl6gdg}Psg!Rluf@Lm5c?sWmx_9SE-8F}zR(D#Z%j`pe0^j$k#DS+!}<HGi~0oGxFRJ#IIZyYg{y?GxA?kD{Jq%P+rodfG|K7g$A$`DTUy|()7R1t;rycAq<mv_9pQWKeUZ!QfB#R>KDDZZOXX<$h41<In&f+j4(9x@h%hNXPHoN~&`K_6d`{u(*?UU)M)I%M#c^}dCFL6@w+de?ct2FCXPpq?8@C2X<#=Pa6~6!Y1SwyeQC#@GUg_lgSNE=na{gU=Qd;kjee54Cd5VwwxPGpG@mtRRVEOv2O=ACgllG2q`o{SUyx*Vy7b%rfC!_FvPg?N)y;hF%FKrV0#sAOxD9MjAmiJ?(VrM14O<&&cJ31)&)!D!CM)LI(Pel9s8`KMT`rf@qg>MYIE&1As-on=^p9+)m-&bY7XMHK(n4gc!&-<H{uSLWbexOktDPK>tp7+b<TcJ`pWp&<<SGvmOr0OjEK=^Da-&@Vg{p4*Xk#9U`%>GZEc)xtj7vc0Z*PR<;d$+~p<8E?i_NxyN``6pC>lw+f`BIeQnfr@qPj8tUT>j6!MLP%TbeH{7HTn1|^Gx!MTMxPazitxl^tETlx&3cnm3)0#PxkMf36uOK)w%u8*Oc<Tukv#HN9a<%w@+Md|Gk==-(fAcf6c!_rTRP=$?adFy}aI@9r?KHv`EU=UzX$cZ<LnX|5c3T!haIQ?NcLFl;oFNA$()Ny-268EpEv9E%%>w`rZ*aIe&b}Svfy}*pJ$}Bhq?}6@G4qcok&-+DvZGWvwHm@;BGv@oMCQP^q4QAkI(wces@Q^a_txeVT`U&-V|SAm!_MCUSlTx168rS8o3?U!;0^Zzg3w|7y8CQzf`6%4z61Ddjhud4>BepAWrS8uqVr<n8jE4s-h2l#0AvVdcW5e0O2)Cl@A3`Np24+;2<8mhuhHGVTwdw?m!2et8JjzhE<|9IxJ;`$?}gQodHSI=9<34<GM|^K*Wi=UmT^ZNnvhb%gM})oyZqs+Z>aG`J}GiSJ<cD9OJwU+QnR|EZPK-)w(;R^fY750rfG%%q~f>8a0#IeopvVs5v6Z6ch$R$-ph4{d*SLvGJk??a{XA7|$M_4{RMyR@2jxZP$=lze@1l++LH`p=ol`(<h}*)P<L{S+_c`jk#1^*4P-Ij+z2F5C|3x<)yD?P3)^zZAPGe69E)_FK*3{G#t8oxV3=E^hxO?an%VBQYPp#+5r^QaOi~bNl>TJHqMfM`m#Qgf*1%y_xv<)wacxe4~2~?mthChfC#@|C{^U#etIVog2n}fgYh!{;~<&{=r!#-@6CLZ-X1sdUYcsw{x$V><7K(`aB&k*B`z<u>se!WE#o$4$Q*+%C{q2@>jf&>u>o*4Y~f-dgF3`(5@AheC;Ur2kZLHu8$|DRDW;VubkiXXR*HmU-pGNee1aJPxbKrIum1sSZ~4d!uKXR7w+`6Zdrxz+fz)=f1H^8d2hocKi%)#AAYYX^7Y<72;ci<0-tC9_#El<jVnRiKS$Kz{+6w@@bwGL#rfScZEl3qH*TKe>-IJ8!=?OxL-@SkWKfjT*J6Jb_4G8n!soA)eb_%Zfv@X+IuP#ky{(RLKc6?4$DcYQc)h>Q<LmrIA0nK-cYPG!kF?&*<5-sQT>gQge0&9$mwa!9biBP+mareXfXl}?ruX|<^1Vyr^L1wEI6g10+spYUTJnA@(mUMgYfq~2ehg|Z``6?0`4{bJ`CjcEk9)e#`|IR=&for&$ARTrA|*er!Sy*aMDo3tit%>EOm<H4b0^?&yWsP)PTzQulgH<Kjl!J1{{ArcpI`qBmDZc0Kc7e1h0FEq--GXK4i1;{jmhyiKM*YCd%f@Z_zHb<T3YY?eLOywejP65zv1gHqv--Uzb#)!`Kxx6^7S9zTod)bo=`5QYff=Jp#8r0gjCO|{lxWvo-DU0-x!>5rO2Q9lKaDu<B?8Zo4Skrv?C<nTf02_Es~s*{2OujxNCa-tkXBj<mG;Hs7sjB*N5)p_QZ9*z1}G!c-;PUGD0f9ZXa&vxih7Fqcq<~=&?&m`P!)`-2SOPNZYF?Kf&$){CT+KpZ#6<dZA5n`;05i<>0=?&Y%7txBsMg?7z&;`Co#$-?n`gDfwDVz7ARYiqD&Ki*x-WN^yH0{xj0)dmp|Q<A8tobslG``#2x>gMrhFBAvcII|;Y{>BDCwKO`F;zn#a0Ieo3zMn1nZ`xGkWR~pBDrwtL(dJ}Zv<G1`4DPMb^h|gcmGRXP*JwA^dPa)+Sjn8m<mcI}#l{0ZA-^bk!J1ym(sl@&NSW!9uax5<A_EX-j*`wLVbwXhMmr%)n*q!@Zy5q9HHa_<&J${7K*JEGfev&+uoPXgmulG$<xYM`poAiA*PfO+CJ}B@ovz%Xtujf6}AMyG0+;lGgKoFnrW-gU{y(ZtM__wa$^TLV+>__o^lm2LJq~xPN7@b%1c=$NZD$$;M`*45gmLuHhdvCYm^HGIllCS;!hTEsf?FcD9VSwAYS{VBe>j_^!)SCN$y^WDhUn}>D@1yq?<o=n}x5|0E7*>CVuk8--dAWZY9#1Z&UoHHMJ^6V{+XfL%U(a=)&$B~zhC6-ZmwxPz-XA69SAN9j1^p-X2jye``67|8l^z=I^tC*j`25~)FW2*KAud1WdOlxY+ZW;VwU~$ae4XVfAMbOTbN-gkeEzC7Akyh;v(E8(d};;B*Q@h&i#JQ&bCRF;6ORwYQ^@|a5?s&K8N!^t_iYp(r<qoUO6%1y-VU!U`QGvExWBD%pONa1@z$7d;IvfEw2yq8W*8SCl{0)Vj{|92OZmn^e$L|`l1s|hujc3DYuvJMsr;YriSag&x{~a7E^(FnvwlMIW47bxb+y}y^?EzC<Mn>|%EwD%eqUkv`lORQt|qG{`9|G>JZ`tnbxz8^^?}>}a9qjvmMYEtYDeKPr*A*cS+y=yD*xz6K7UPaA^FyG9xda45t3i@6OS8-j!N5QU2k}-=Z#kRWe@OmMb3dzzP4f~k4qo2%K1P3EIqHV%lAAN?eCpamdCMbqj6ju<n|2e66y5y2p9VuU!Ilx+J(4(TK7Bfy;JykvTuJ_s8s%oLF~u75h3|)*!Qd$Cg<nX<oiU+zw(OPA@kkSPTz1H=5hXR3@P6m*v9>~?0hL-A5e_@XWLG4JLn%o`}jv>;C353o&At47(dU2O8&MXT+gkuWdGJ@-j7d9L^yrpEbdR&JUA`o$K(4`z2blJdaeCiYqOMZ1Qq6T@VwW~ALr)n`kb1#>-lW<KNRNsJ8!Qrr*9-3%kA$z&-HA)fZHwpRz8lb`x^L06F2+*3p}33Kg#7B!}xrM=lqth_wB;xsSS_AB)={{FAXG!b4DsB)+Mgby%#*5jQW$;TdW(Ok1|h;l>GV+`1o}<;{N&cHkb3H37?Npf7=hc%;%%krMUjyEo+4KSisj^Q(p3Q+Q!yvNdwc1;l0%^@gB<dlP(axak7ErYnMKY_f!5_8MaCOisIrum*;HfEn+{<9=`Uw+XY{(zn!maubr=Km!5FJ+VAZb%a7Ln{g<r$?*4)wZNC`C+VAxf%UAn}H|NQ<-|L5#ul7S@X4u;A9e1{`9Cx;_9Cwzl9(Q)Wa@^Uza@^VFD94?huO4@2FSD<XtMH?ZtCp{htMH?Zt5*5yxN7<8xN7<8xN7<8xC%eoxN6l$9apXTtK+IwzA~=rTi$W`%6Z)K)$_QWubjv2eC0fD`RaMx^40UWUA}T2x64<~<F>Dy$L;kh=W)Ay<vecJM>&t%`O10RE?+s18&BNpgeupimakryTE2Q+YWvD{sqHJ*rIxQ=m)h%9u1oEF<+{|azj9q_m!n*l+T|$MrFJ>Wb*Wu{<+{`^U%4)|edW5;_Lb{WqeymMuW}z@`RaXycUdm3k8+=4`RaX&w_+*wmHQ^kSMQrFU%hX#^OgH1?afDSPxU?yzIq?$%@=3AC`Y+Zw0!kG(a2Lz`09PD<*WCtmapEo+WG2zYk!05qufW^zH%RJR0-qqmHTwdSMSrcF_$@CeJ)}7>T?OpSD#D3kM>-`%2%IDz>oG^!YW67E@9;>&n2{|kKF$1b0_%Go;z8-`rHYAwC7G%zWUtBTCe)t$tp*E?qubw&z&q^eePtHqds@C^3~@~R=)DwNgtVMgUDB(<H1*-<LTK8ZEzkh)^kGJSDq6Zaq6+JKBt8r?K!QLuRf=>eDygk{AkZ<;YWK;Ypqv(PHUB~KBu+HSD({b<*3hTt@WzUX)RxUPHU}KeNJoTtIuic_UH8~?;UJkdGBEP>U#&<SKd2VzWUz5^40ea_Ij1~4z{nncd*M>-aFX!QQkY)>s8)6*!jwP2RmPR?_m4Ndk4E5<-LPlPvyOX-eWoY%6lctSKl9LS68#Iyl=96^}Ui&+u-t*_gt1A?LF7q^IX329?kOA_h|a*>s-F_p3d^4y{C)ukjq!z16scN9?*E5?srk1@?O&N)%TKizVcqu^40f}-Zd44uf8X>eDyu4w?-rOmG`!mufDgn^Og6uwy(UmHFh@Ra+LSTmLKgs@~e(qj{4plezf=I@T0vqw|w=zx#g?x&8_vS@6F*ydv9*lM|p3q1r~F@Ixhl#w0RNmqs@!3%2DS<z>hXB!YW^#7h#pJ&Wo_hQRhWi<*4%_tbBD|gq5$(i?H&Qc@f@rsW%E$=9yT2w0S0x>4dM&^Razpo{#M-^L%Vyndf8q>O3FISLgXyzB<px_LX@)cKOOYA3I-}=VPx|ndf8IUzz7)`^r2YyL@Gyk2hW}u8%U$%J!9cRz@l>`^vmB%U9=>+4;)6GRs%zmD#>Bugvn*d1ZF_%DghWKFYi@Eqfy_N12ys`^vmT%U9<mTE03j@msz;FVXVVd5N~K%uBS(SLP+!^;G61+WE@7MAf&R57^}>^AhcRWnQA~EAtZVa+G<AcD^z%QL8YDeP!OP?JM(UEnl5CYx(NDS<6@F&Dy>)Z`NL~GH=%Qm3gzaugsgZ>!Zw@wb!f6o3(vq-mEt1C6}YjL$-Zo9<r9-y-CzZndfZz>O5z?Olsjrn`dtM>O6DHSLd1A`N}+V_|fK>!;d!49DcNU=2pHs&)izCI?voHN1bPG)kmFYZk40XGq=i7=b2meQRbO@wMLw;eir~g+IIo)qkR`(m7{zYV03QA`O0@6mal&IVfpHJA9gv)cOP~+%6A`jIm&k*mal&IVdpE~eb~P8-G^Nt<+~5tSHAnO>#2PAVb@3b?!#WM^4*7>uYC7muUGl*L$91<vry$b9otvF)6p7cV_*Fa2)_Cqkls3kedW6(%U8ckvV8TsB)c5tyCiSCf!j&d@1!h0+ILcy&ur)8QT`6g^40IKyrn+x70b$ZUX~y2JFgWh_R(^*@5tb*-;sIKjygokfxcIciF%w&7V7l9&Grf3-)FGo>u>vV{`+yKr2JjYh40(HNXqv=kIUse`Fc<)r<05G$Neg=xB4yqZm^ZMU-Bzo<L?irtd!QPJ-;OUz<QtT2X7U=KYkC%_Z{mcd~e|#QhmI$y9r;5zyIj>e1EMChSYAK>+pKBy_U)k{8WzXxv;WSe<N;Q;rsI5I_&g4xia&5XQkaE<sXd2?a)2v5vl%juZnv3hL@Inquv4G>oH>PmC9ebh3h@zt+ZW6s&!mW=d5x$rFsfqd$w5GUTt)4v25H5l6<|_TJisV=hy6%+O7Fi;RlXp+bxx|u&?kvaf6RZ{vY*)@1NY{kmNTwB-$(R%adJF`7btbJ1+P|?pG%UvEQ_s+|H%Th-LkdN2-qzD8hMfi%R+4tGW66(h)DD{isKz6TY@Jz1*H%l5qKFdrIZ#iQ{lNZx>42>s|j=Y^QJO3AuefJ`=w2aGuo8zQuoWyTn_(Pb&YXt-|+Dowh?Nr_EK-F532&(($fuIwO3&VMTd+U+!i<Sw^{irmYvg=UJGvy?*%Gy&h71j8O~OufI~-Uq-HZ!Vk>)EbT8X^As*W`5LJlf83tJH^TeL{cU9nuBSJrRK8ZF0q3uqD!0$b!d#yPOXYIXW#;_;8xKh3%(yF-J^Bv0|GSn7-zboGn^aE8;llT)A1aSmxBCk}5VTd^k82BaIla0``^!6dtN8y~^TnH_e%n1r_<Be}X?)O=W)!}0CXG}dZRT^{{-KMd{pdRr#s01z<^5Z0Df=~>O5=vF+5+}t=G!XOv(jwgYfEBE$Gfqs_C9X6mC|_P{ig)y7mX#A<2m^sf7iY<zO-H=DSxN!ZyF-EzwZg>UzsRvZy?S?&aa(CD&JRRpYZj!x?KN8LwJ3c3rg$Np0yRrzC-V%@yB@K=DdPCrR~+{eHHs7aQrX1{^|Y@zCY82=F;}|zQFlAr%A`7uibIsYwh+({n@kgAb;QAVye_X{X5wA^lsNzYKINmg>TGW<SXmk-rdc){7s7nIep_}CH7}bl*g+-GxK`Ork^F1-`U06^(m{|&b!`;{-otSC-qNngNMTRduL6Q>OV7*zk9!1V2raq{w)*PFVb4tUhn(_T+Wxz6P@{i9?7}Ae21q={)mr!J>)JqLn^;aRpI+u9+)q+^Nm0F_X)=KlJY$jLxk_&vtDWk<Kb@6|BO8&rc3#4ck%c0{dZ56>QidG@B^uLPL;~Z`B=<D(vGy0+Q-}Y0Q)0{hd9g8YW}rZ)aS3eqow?%!`RO`c9@jEJe}|Zc|!+E{k*|3F~0c!ncT^l?_0D@_{OuuO~iKWILG}VQTH&>KB4h=z6E^m?M}is+O?E?BU?7%`%8V0e1FPh!uJiiA^BRR2I6-s^o4WsIM?glUxk0qqImK)&U{be%EAxmX*){!FEg`WbMGW6zlVqYVAlX=zSc4!|L#V$VZS-^^^-5f^_-`2*)dW*AN(bJy;kQDQv1x^$Nru1)1>@ii-aE-)Md1k|D_B2aS~6E+B0@};rp8`9xLUCe>y4l-=<{ar1Edy5x#F_;}B`Prj8PRKq<%P>A?9dpNy5-Csj`N2g~*J1=4Uiqq0iv;N5gf{BB5KYOvG}#^)>iyCk!==~6wjuM)l|!M6TVJ%3xl{=**zN%<ke`FBa~muP?FJANQXi7rxoYWEVpKS@v_X+PGBDZbb71wF_n)pJ-;{=TO~r_SH?|LEUAs?U-m!Vmm=ci@rl`NujBkk;FID}Qg1ZoYoxJHGem`4Linvg<rgf0}oURDPQK!uP)(JzA>Ijodt6a_T~9zk8Qd7QW~8O=<snzvw()^3$+!Qhn|m7ry7$qao7qyZbQDPpP|0?pINz`MteTzW&c*@%}BabE#BMz3@GLzqe|p)UUMVr}#a_*vfK0c`{Nwhx7NzIZDcJv67!tHm@P~lN3LQ=L-HUr@BkNF;w`zOFOGd+netzKet%Csi%BAP8Ij}zT^X>_SdtF-Xi=wYlcX^tKJ^bZWYHamio`xA;J$_Xe;}%4+-BtboByhyE=t)eyqw1#qnL@!eNm=vYGh3p1_mU{G0*4|56j-Yxkoh-`lAa|4vZ<nv(CknU8<>r`F$+uRlt_{=<us@5%8>jL-V9jS-UH>J0mrCrkN8Tps@e`9Dkf`sV^-T=j-_J|&f-#T33a;?7CQ$9U`AIYIKh2?IPHHuFfn;W;IIU(o#%(t4M-5x&uXm0bSm7Cb(Wdm@+PZOG-6?<Dzp!;-w-M+M~itS=#aZT?4TySzcgIKQGx@{Jeo#Q3S@z9*N{<T{V%e@~Xn2@B=%w#7cVJ|ov~e!+2)@9#H{%imE)E@w<79?#DvlH0#cdg1GtugT>H-iZ5BW21i1>1$Dgg&%l!WxrJZlg|7+=Y7dTQhv;a?CU?s{xA9YzISL+$@hJE#LqV>t~el-KlA}VS2@vM%J*cw&-p)emGb>dZt!!J+_$8By%Ik!^5ytTF8}ytem=8qos{n%H=Wnp>ldjV{D-=7IYuGL*Dp6>zj`7$|4n7#d+PT-EVV;|GyJ?|cBov=!{q!NpjP`0l0R`3-xqKGxJmN2bQQioTT{soMDX*hKy{CtfA=@O56w|;i_|~UH5a~qB++JRzoe`yeBZPslJ9M^N8HEx7gm;h?bcDgK5z6}uvE^lox(Tv)o5_U=?4$v-zWQgbg;C4s}JJq|BnNEI`ac>Q*b$#9{=X_^-B}^_sI%x8Rhi7^KXg!v_RD35NW-0lJouBt8Npda>f=D_XUAZ<tI9Q&zg^XUoa%o6sev2w-COrl%w5P%l8Fw2TzdNr|)$36P}amV?-9@-#H6;6e8`HBKP@z;lgrhyYv(Xg>OvokCOUZ8Xw<})vGSGPoRARF6T&<-=z9vk0*SsTFS0ceFn$j`<E<9x=Q=exFGIFJOc_oEJJ?JuUx+J`(~D}{=S)3>eUfZj`I6ymaqPPnr}>gL)0^FQ+{6Ev_h2A_g3|Z=j4GS+xa{;rXBmAZiswu!Xalwf9#U^m{_m!J8zb+{?40r{s8jj-;uL?^>^g7y6KPedhdweyYqxp62EKbS^Av)l2b)~ph?jvr?16*C+ewBZqD~l>5HClwp-wJXoT<|S3kk^k$(rz^3~tL3oQ96eD!zsEMNVdJ#Wkh;yj@Kj-TbLzvJhByouj)D8CbE`ReZk`ik8<#rs|P9YXl(?-2T8mN?DZEB~IM(Pc098|8NqEnodzL?eB2vHzssSF9ubYUHDkS-P({-CAl|JT0Zxp|#^DBgv$HmVW;yBRd!VU;SicfdVB8{{Mb6GJXt~rtLNBkpdbD9%t$$Go~SkZ$i_$m~Vo!xL6y2vw*8Y7lNyTr$Qfsr-E-lGrE~?fMd8>J>VGNn9#>A=9u7HF4iUBTi_Yc#^4#?8ZO?(E*fw5IB-2^S8zRWedr8ueeeWm06YPF6`I|}d=;F*#aaVg1N9*uYUZ3aqcwtf4>YNZc@J1~v9<+k;NH;9;NIYa&`;ol;N))BLT+XX;!4oM;7Z`i(EnV_mBBwiw}B~$kHG5)J_7C!O$qJ~j_KlU&#!TN3<Xz&764ZSSAw<!R{{@*?gtMCheK&S;n0-enP%KJV<Lk13N)LG`3g9_i?up9J-88cI=B&dG4wWgG585ImYewrIFp+-HaHVFGxUy&IWzc~i**+G8F(4A7I+!h9Dc+$Ho$hz1b2fr1a|{>hfW4}2hWCH2hRrIg?e1fcfmPatWCj9Q6J(-X3jMl9}&cNpc!4vcfdg|)+XQ}a82k^a82+`=u_}aZ~&Uc%^U#7akFLx#{tKMK6f$41>beC`oVX>v!Ttvv%$eG-o_ppZ}%i{BWO=>BXDEr9B^as6zDzh6!4$WoG#`+!I@mF!Qf!jhq$eov(JoS2;wlP+r=CPPVQpu3r-Gh4?PTS58et*>1N&v{tT@GrXVf?uPV3*xG3~Ta8d9V7pvi7rXb!99RS`A?&RWatgP{Nw*?o3Rsk0T7lMue7Xr73Mu6Lc4?ur#F&_ZOa<O&-cS3!L)0uI~%u5EotnqSPlM|ZptBW}`mPwCk-}r*Y%cKJwJO;~kQN}#zdhk5(U(k2pzrbnTta;tc6vXMEKZDbO|8}vycQI2CFM$3IUI4BSZ38Av0wzrZ{@08xu5aga(hkrqV7gYJbNNZ=U@%>)BzEz&32AF^1MouVM({%LL+C%?hhVxkAuWLG6p8}4HX$tt_JFNxlgHQ&Qu2xE`fG^x?K*+jx|SfWkL{rCDG#j&E)T8%tq-n`|69Sa{g=SB{j}WF<R)h1fMy5h0Oy1TfpdbJLz{t{gSSDqg13P`LH`BQx@g^-p<BS4!T&%%g8u<`cCmJGF;fulfbInE0LOE)#&<JQ5SN6O2A2evf|dc70w;hb1SbIRa<T4qF;ftCg?0mz(sp-+{tNzS#v(H|L23CBG{2kq5jcaJH6J(wI6d@(i#a{`fs1tm_yKr6)CZmqt_Mv7CjAL~Tw_iIzKCVwL0BdYaj+N5A>caDa^O1Py3pUib;0AIr@*9_!PHg_(Qcc-?V!mVoDRzwaE#HhMc2l3twz^nbnQXcpv$1!T;Hydh@V0KbA7v}BBpDuwkTsWbTN1{_!IOA_!GDguJh=6t`H&<uBkKOdaf{()>RnmO6vM{ok>jBp`>(gU|p9IPlOHy(|MWB!E{YT=We=YqU$MICQc3wLoO-(eHe5Sn95j+ayp<*8>3x`Q^4y0o`^a$fK~)I05^nI0yhLth7Jc$249DUgIk)>!i+r7T;M$5ywKd>ykH-+71#&f4c!Ue4R*P>d|Kaj=nn99@Mq|M;LqUhF4i6{W(wjx(7oV2;6!fL#BOE^;<C_k;Id#Zv^>}gP6AB^P6FQNVm;turXcPG?E@xtfqQ|!qAjRRi0OKQt}DtwgTZCMWudjfWx)fXW5EN#C!l|TN$K2gF<k@D@>GrQ+iyT`f^UE`yIARYL}mnW6=+p(74Q`3RPYq=pU@lNKfx|HD?N{JA&A}3m|!>fri+!HN8CgZPjhkoX?warJAu1^yFxpIyMkvxr-NsJ1JGOG0GOUPkY;r;QxMmHRs&Z<y=owcXFzX(>E4aTN*X&qm}UNE>T8XIc!Z1f40r_iJT$wT`8>FUo3$pm1h@{g2DlEmHZ&W!Hn^A>XI-oj&}?7|;*l;6;^oj9U<%^X(3)Th;!tRIa471(0!rJq0zo_q`Wtu@xD0~02$b59_yu$|l>F5QVn6gXcscY9^fj22+WifdiFNFY^I#o(0ZQ$D0n5a{U|-Y${{pUuAg&9o4Xz6=4lM>Q4nF7lwx7-+h=(JHharduLnFY0!KI)h!KJ_@5yYdR%fX|;E1{>sE5TvVP;eMH9J&G=4qgQv1zrUn11$p{11=3M0xk_M<odSn3t^e~nHiDLv(Ojdv)~%g)!-W7;!r=hIJktP-;_WQS3?l5guVf<1iyn)zj=pc;-TnE7r;ZoQBdkPQCKF<fxc7^oC6#TtqTqY*Mb%Y*8&GYsSgEVnK%;tYB)F&Jj9Hjp>H(~;#bh&;Nj?h#1zCYH4ftU(7|8|;==GsfeV8RLQ8@Rg7YAVD<Fs`Ku3cofG<K<f-iz!K*PW<z%QZU;FsV(psT=tfG0x7fXASZPDBt_L=fkN76Ru5KR`dG{`vqxyu{I`mmr8oB8b-_h}T2Ug4ctyL2H1sfipsjgEN9NK}&!$fwMrXfwO=YAc!|YSAsW!A4A`PAA|Gb*q~z|KZ4i`jRJeY<Dhg5jKebV31~2wg7`AD7MOzgl8b}*I5Y@+9LL94C>;-D5yWMoL%`N?QWim64ndsHj7J*lL+H<73gQ(|I>uHYh?hZMftP`oLSKTHf>%M`gI9r{L+KcMj%DJf(1KtJ;=iGJz!b#iG!Eh)@%IYgAHlVu6Tr2>bD$T&bHMkYFTnS}Ke<_7f+>j8K>q+!5Z{M45quv!7g`ZK7hDIL7hDIN3QEUeDl8M9$FaEtd>%X+Iubk@T+57_P#roFJQByPjv!uxAYKPu4_*h(3e5)23eEt{2+jcZKr?|o;LOl0;LPCp&;{W6;JFCmdC-mEdEiaZ$KXxiCr~=JpJ17|0FHMrxB$33bR4)mcs%q3cs%$N^fLGq_&W3w_&WF+^f>q$_#|{J_#`+4S{7Uu$94#UcoKrR5;PyU5;&LZ+gOkb%f$E1SP1<c`Uw0xcmwnycmud9bOpF7xEOR9xEQ!7bSbzfxH@zdxH>or`WzeuJ_CIUJ_BA1{TsX(JPLXaJPO<wL3{*C<H!*#6UW2YQX3o(+yXiW+ycA?dJnt?{2EH*$ZISU=f>EQ2Amt52TJ2e9xM~T#n>_z{1&_pS_ixi+zLUQ0GbL+O5;cZEE6BqSVx18g8M^jf%}6?Yv0D2(g@;GXxma~?^5us_OFTkL#jLWmyZ2Oy2i18*I@sXu5<K<b?7goSsnc+EBY5{21kF(fc{A8ar93Q`Y&l_M}H>X0G+RW>;J^RL+5JWju+yE2;yGQdEj2)-q20p-rz;hC*Vckzo0Zu{e@-X+!(vcgL8u`L&t+FgC|2zfhU8nLa&3bf;BhmH82J7S9mAEU%^+PA>a^<O~mvpke)}-^FVqgL7Wmwe<S`?<M{-;pnJf(z+a#=f8q<YH<*IBCxUoC^dOj&=1lCzGI3G_aRq24Fll9Q1#m?KaSG@U;1u9PE>@a9aR@=&585Bx4@`4>XnSe<^Fx0IljZ~G2NysPw}Z9;w*&8o?gf+5diG<PI40KJA571V=^1imXd`fCa204{a24<f=oIh>a0K*Ea0Hm%sglxr>>m)souJLYoxt=Sn4W3Vd+4PI;-}Eh;HO}k3qVTmp|c=}vqFo4vw~?Z04cqPevTmaL$`ysqdvqmAK;GmZ9WF^Z79uexQ%6EntMW86PyiP9Xb<S9XuTx08a<shSL0o+gK*1xhJG?!Lh)xp)|iCHkOHL?g{B^@EtJCJ)v!(c_h}n4&olr?%*Eap3vFgp5QsqyWlzCdr+D`au3VIIT6Ic&|2VHs8=v_Hn@Yv^8gA%3xW%Si$Dv3i-0>q+k-oT4?z!r4}s&jSm~WVG3fws9Pl6n@iC|YJ_b(hW~F%#sS(80-CTd#o_)}R;C*14yFnV;#Y{om7djB!7kn6c6nq#=b2ms+xtS@5t3a!PtAMLQtAnef&crS0m@#85g7^)BIG3A)IH#L~_!WY9HG;S~f;cXM_^`%7+(+Xe{zc;;E~#-4_tQ9t4UL01KFVteUTM~6yBW(6#B-th!E?de%t#W$9N*1|k06c*{Q(>goZO5NZu&`bb8JNr4};DC4+Bp#qk|be&FBd24JPdl?g;K?#z!;Wn(;66J@~O1f1B|XdLR50{2clh_&N9`^a1!K_%-wq_%-+q^a=P4_#N~a_#OBI^ac0>_#fyi@GET3KhTfhGiF>j;~ew~IKqq@`1=j~jX2VbTlo7e{Ehgmn|{NE{~o~Kh%cCN7k|HtzY+go#y$M~9{xsr*^E2*`yKp^_?j6v&A1Am@@_+~g0CWnxP=+5%xDhvfoGYq$c(AbdEj|iUI6ujH<_{1j3dy4;Iw96OlL+0s0W<Qj7(+(L9>H1ASWX<D>x%K6Er)xj2VT@@IniNz2NfDqTur2iqK-<%4QTdqYAVHxC*!u^cQd?a0O^dF!hT|=o_Tx!Qp0vnQ<B#3J!-}ghqicLC-^@z%k5q#4*DKjRmG-J}$-p(%4`Za@^3E;JEnzv7s@*>CH$MgZCS0B5-aq@?am5W(F5DBbOQZpgF)5&?e=erNI@^=9Qtv!9SVtqZw(SslchtNQu9v#NU3xIF|x{Pl3OsMxB$Q-ig2op^3o>!3m&Az@+iP`^>i9YsOLNaqs~*|LrjJD46>EHuQVa{b2gPd+`5BPl8XGvCE7T&@JFSSUw3o1wMhCW6;fD!;JMf*4E=VBpz$Va5E-DM}qs9(aX)_I%#(>jp@I-d5kCSg5}Bhztf<@z_Z<a?pO{T2cB-mBr_&Lhk$2c{Fn}%1RiR}AS@3;{v_0m>N)^A7(56%1UeYJ!_DK+YN#JP(2U>A=nI_yrs!%$KWGo|6f;I6Z#43VTe^8%Yzu7zrgLjMH=l1wJApgk|MY~m1=F^T$94||kAjAPM}c+JSw|go_{8(gm}$lw=os)A)O!we3Yhx9ShUqx?2{pAD{8xi(BHw-x2TU9(DmRoW^6TMBXl>I+ORd+k+d^-shj)78t7Iq<@|~~()QqWC~pUJH+YE|Yt2{z-2h&K`mTlk4yJ1nx+eJy{RI9D{tEpM{KZW-rMyh~6@Q~^7`mo;=;rZ=#-*IlEZ`uFec7Nn!8wtW4P$5qjIT6ydK_aZjjefO@Hv^z-+#KfoFK<|S^#4$o#W`7R|HxLTm+mOTF_B0>CXt_{Lq5nf+#;f#%LO=%f{fbj>fh_*hgKkpXivP<ARPC>hp9gbV3mO5X8;VKdHZ3*R;fo!K8HkI~)Cj`U_nH)AjKx#0q#Tu-~_%Ppn3NNpJ455_C<DAa3MlZQy36AZ`Y20&WJb5ref_3}y=AdeA!Hdf;ZzCg5h^R?rsUR^YZ!AGj^J9keyL9k>njS8y9}OK5X&OK?+YV{lV&U1)7^U2t`1Rd981Q#Wg4H!}rsLuh?)LvS${YjGDd1#udUHJ!#xLHr{$HTXwxa%f6$a&Tg3QgC8$d}u;&d~j@NTySi#3mQ|iKY<dgL1Sp&{t;ss&|+!!qesDUpz*+QzzLv<zzM)fpvk~Vz$u_VfKz}|L4N|L0;h$h2a{4?C$4W+w1F8l5yZjJM&Mv@Ed+5x>ccf$?vydUeVmwO%92w5)HUyU>T)|;|7hNZdB$zur(b7$t*HJ_`Ljmn|14Th`}UDzof@%dpO_8m77w1!)9g>}e*jH4DX9'

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
