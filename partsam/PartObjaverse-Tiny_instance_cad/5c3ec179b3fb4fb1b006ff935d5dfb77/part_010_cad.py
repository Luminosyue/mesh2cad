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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_010.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_010.stl', 'source_sha256': '63c59a617addebd439d8bb098b4e784e2f68b42c960192484f2dfe01cf75fab4', 'input_faces': 486, 'input_vertices': 571, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.38484001159668, 74.49857330322266, -0.30538368225097656], [5.65997314453125, 99.41752624511719, 25.526073455810547]]}
GEOMETRY_BASE85 = 'c$}qtcX&@r_wRgzh@L}~kmPL9yC8bmx`PnCv-N04Z;7&_2GJur8xfsoIYiqy99>9=a<KKIcSm<;)@S*>-uv7??sIQE>zUb~S$nNDYu1!KGhe}tQl<71_{%GbOz&cQlovu#M&Tt!^c*s*PxqcfOa4A+v`csruKs?c^P98^3U22TBScuC9zBP4A5y5YR;X&PiiL`6g?bGfGHgiK-@6PP(xa!s>viovw5P;}hIAd&Q$80CtPoIKD_f+vHdgz8{7WxQa3*ytYs*wmSF4q-(vAZPsZ_Xi2Hw)MH9gmQm0zV+la7SjW8#S4EYX{AaiJCP=uX71x7bQ@?4rTIdvs#?zZD?<19gG_+Z6JR*}w<af!>I0kUy+pVUp9k8u({HuZS&~kIDn95^k1eJGX@puIH)({yeCcIlVjVY+V6(4j<sls~05x=K+wDJd5O*L)iXiU&;`^up#vJ9+#KW{f`OPK3oF-?k&Wx<vB&TQ{gi3TG6D}NSp(F-WJF?alwb=-<=HkKm2@!@ol3Cw+6Fb<0RomL*V)X$k*SEC41~!ZDCLHP{`42;@2CrCR_}u+=lRBn^CWZeuNucYqmlCXOf-f-rT^;-)l+y`G%7mE#+GP;S1RQ>Th#W`sh93!afJRX}=J^Rpbr$OLD!E3+5udyI&D*UiODQjV8hVV~@a}sS)IV=uQ0EL5FaC3hHI1+=85l^UymY720upE^m78`6<W`98B`fXtblY;TYjo)hy84v*xc<@3VU#C$=B>=PjW)G}7-PTzeD?`)}?h`R1*4gge)}L(cX{#G%_N;BAk<Z!H?;COICnV1N5Zu)j&3JSugfBB6KvSmHN_3_yGBoC3Xz*w3}@c~O1SO@jTmTcEwVO(wrtCns>dJRm3C60~E$Fv9Ir@Td8tX?A)qe+ckN`H0_M*cSf38U*|Am4_et-Ge=0_2JK*QPA6XF3ESQ0=HJh0MC#3H+OhI{<akOt@z{|B)`z}(p2B+2U^f`UBscIT>##n>#MEwr1pAj6K+JTCi!-;!DOfL`5@uil|1nC=@n$BnX-p)ef~uFp?VwAYZl&3xHX^qQCHtz$ljJ4AU|*q>?wMO>Sdo?0{*>;gqyv`kY4@LY{KnaRp6g`=P3T|5o3T?ybU`C!Vmh}QIJ!!66_2Oq_`FL2NQ0N8V@<??!eDJU4X}4ft(L$M?0zsaPJ3XkEp-dkJ3{OP~RmN5r;L$`4fMv2L1u5fM2_ijqqJr2zPpXLcQM4r}#Ae(?U*>BWTAtBQ#1^qyhg$_M1nAj4HLRIi(2iS_$$OCsKTx-!>7hAK`Wx8chDTwuBQd663%h?ofT5$;}{VP`0+DZ#v?^I$xM@`}lpt&-i^=RBBwwPPqB$E&SGW5aQvuJLCuNgMUh5yfWvVD@pdW=eUXqO+$W&-blFcT?9D;3Sb-yUr)GEKP&9n*AC<M$?1e^li3fq=ev{rGlK}X*H?s`8POD1BETQ`3xD___vox7r(F)%6OjTtBbSnYM3L_$6mDfj{Fp(P;h+77fS0Tcd(tAVoXe{SHztgNKhJ$2`F6|@!o{%w;up6n(Kx0V{Rr1bK7rnUr&2tKK!b26;2iXh7)IlpzM%}{WGqf{%#S5#d~?Pzz9KdB#?{O~<!ApbPWbY|urqu-=EwMRz{jxv7ftwHL)n>o1L0<iebAd!oyH|+<$U1HDnS09buy{cS}+oLWu6zplLXaw*Dt`gG$y@vzBbfedWHAJs9qhz;s5J*soh1F$AnvNZX&MgT~9^&%U>hh@H~rtk=UC2X?DE~{!4z46IVJj$-j1naC28T=zX>k{e93$;5QM^qJ0eFa9bSYoWIHAKpGdN)i(mqeiwdd?S(k(GLmrdy*}hT3nhP=lNuAQZQcX^(AN}i=Ho`FZ&&tnXx@L7pS2i2@VDdn*KO1Xg`4X#0gq!p2ek4aIi;T$Rk$6<e(rzvBemDOr@%W@f&D8V5WnU+OSpEv65^!j3>ud#D-QV5A<$d$_$QK6C6aK_=K}Ob35-iVz_k*eAirSj=NeSr3HZRBkTY+{7qb6ZFywgu4mtBSrdO#^KOgLTxd(Eh6Td2cXMj_L{PX8$#Q%yL6t`k=65(P&LHIe>G#U@ZyAy<K``$vY-vNqS^J_5hrV)_u-=E~$Ly8h^J(~hQ%)mHi9?nF#dHhe<S@J2xv%Lzq_3t*=<A0yVH?z1P++NLba(UT1(tGz}Vd9U#dQa>+3jF4I;G=!Pzos3HOJdRy!u93ZQLo5YjKjkZ01xCi(W^fo|6JV#IghKs&RORXpI+MtxBGDXSo<DPTpiv_xR%WA+dSwc`N04#;(46(+4Y?8_;rLk+52LA=!<oWb9O2ChqZy7jfeY^oiF+U-!~4p??J3*u5=;XOy|JP>2b79Fw<8g+=z~XANtOs_!r)8u+x19__sz;+&Xh_7a~72b2uKlq@#98IzzbA5%DZyw_?8bJW9CTf!C|X8|oLPwGwiyMHmMLal7ZKO1QCf4&q_zO&W)FZy(5sIR!b-a#I`{Jv|7wX0?X>$@eI(%%krLlKfy^XZkn$rf^-mK)BtE+wn@xB;prG2sg8Hd%cWIQMl#37;^SahyR~kpz+*x+JWDLzZXjPze4h-R{{UH{ILJY9Gc&aSLF!T;upZ4^v`G<w#K|HK={O3z&{nB_!Q-?5w3?X;CAVSI9Z=UxH$&vPZ8)t@n*N*2E0>k)N6gzb+YH61vwW+pj{UIg>iM<GQ#cWiLigpt{bHH=_25}wxGVPHsO0`^L*f)|AAh;G{wJuX)f?vXAlpC52sbB)*HAevjlo04&nQ;`W*1rn+*TtF|dB_8VUQ8lHi9-n<%bK(GT|j(hzc54yOL7zw80|GeW^1Q;)_y^KDzg4Z{Qc`+cyk*b)T!?%eKT_B7((UJdetxZU;K351srkUz5y>bvnUjl=qHC-Re=uiSqJImakYRvjQ*``Q`u2c<hn?G+SBxOHPb{5iLwKl!Id5aiU@1UZX5C=Q)_MF`jPl;rwG(>QMybn=n>Bwxr+tbK{}##|xXZaWkHoLrsOpLYIJ{)E?wN4u0APUD;X+g`%OZN#%EG#~L08&A07$MIt%?IHV@?Iv8$&+UF?{8hrc>>ylwvl9K+qcgsz8c!nJ==KQh@}w8VgYnly*z<8S<a_o^JfxnZfot(IAiu$}`%1py2iy!l4*6>khgOgY`PH^Te(CSjkBo2QVZV20_~G$NiWAKl2m9S~vOky8e4&p5Zoaw;|K}=4{a4Ek+>YdU5L=EYJFS4RkW)AicJ>IM^?-J54Djka4%l-yQT)UMcQU62zk7PJQ^Wul)psEtdf_|8Di7T59|$|wyrgxMbubM6Sr^CS(zes&pR%KYx94^2gxVDUc2VGFK3<=6OY@rWjhFM1-@Yz|eD8_0-p~dm6RsWeK)a0Ul1Op>&%j>^PnZrlPb<;-!6@=O;a0>Y?k|DKRNqOJ!2dA~<WD(`dEx3cKdRTBYryYqz<Tf46~c{w@VzMt-*w2JlP>`ua1!m<7W+SDYT)+AJ-}OH-$Sc$fp9%fB=Fn)uy2q7xUv6N=uPcM>rW#t5psG}10G+H{4CM}*ACj~FB3mwef#x1;pUxUuruM0_vD{=;6^PTPeNuSsW@@w0oR`O=J_|C;?U{K_&t0-ihHYRKC%k}w?_X3`7aw&zcy2!L%n=?Jt;C;)L(+mLeBZ^@V~R`BH2?7xL$+DB_rKI8qfWhfAa>kV~*cxzR*sc^CtdcR&&Cu@5Vk}()wJ4_riCXe!Fx<^22H1Rw%wJO}C4LJDY*qFCbq#nzjPH*8#Z3`*O~_-j&Gzjag1H*y(J_O}Hq*a*pmGTs!j=^8JAuFGrGmtH4B(?_69*xX2Ix7~OP|V-Esu4m(fv(rcv9c<7V?ZWjP9W}PZcdP)MfrhXv*JB8gLCoOR8)-mEYv$+$$@gf#-HUSr_y7*I?4BYIN1K&Z_I+P`Q4*|EXmc>5F+h5C(o&?5IfSb|Xun({YxM+cRF!S6cKZuUZUkCAKZ=OPSIzhm-%55RXoQ-u|BjEa7#GCPZ6Y`s(v3!nCJJ$@dQ{-fPFUSA+j}-sfp|z;jU5<a>vuNKq;QAr(>qYjKr*sK$s|xIK;=BUM52=6~-0$pXTgeaR@fhemauw}W>qG#(w+^`WqyJtXMskdyz|Gv;-(!}Sp>)R@v`en>uz!CYj6Yi~@bkD~4<AA8==cEFhhdx%&##pr{jF9&Z{D#a$7<$D^>W%Q2me*xAJex}yV$=^2cBgk#`EXr$bO?^CD_vo<DuT|JK3-AJf4&4yK)!R*V)k;dQYt<-1=uF;;MED>{rySmP6rA-Zg~Vb-Na$bjR83RIkc0h|fhP?ejbJVhDFSuZEngO^Q-IRu1+e`R7g&Ze{(W6umc~KjB&%;QHhp{*?AOk&Wc@d|{_7q<Y!ywh^w)!F*wj{FnS-6^S6+ahnAHSG!97cUDaXf1fFclL!~$#0<|$emgpb`n40ggyKr8W)f}=$NreMy%Nbc>Wn2^8-V%I7(RyLN0bJxM^{9=egB4jcX|xr&LrUGln2zmtT5pEb9@(@J|5`rA&ghUysTZhOzon10XN(*j~lBike%Xl7~x`FZq%z}74)O8p}=!uonSxRP5f5z(ZIJoz`4W1zqwzJBHW(M>xbMG$sX<fNW!h}IpF`~Iut)*&v3~3vCdgDhxD3p!{E0q7;m)+eMpYAYcT2+iS?EBb~@sA>OklX#rjG_9iuqW7Y$(Cp?J^=Cs4cV)fm5Z1aY!168qR+`a|z{toQVVL1^Dj{eVBhdQaay4)xmB7xo{%fOx(fLjBR~)f;{u3S9iX1p8o7-O%p&93F4|Xx(Ce@`Qh0^ZIk~G?HT%Oa(a(*0)A-HX0vvpAWx~{r^5h|BX#1Kj^dG5ia`jIagkP%tx7T1J|*BHgokwy*3>3RJhX(ac=fGLG5C%jRBtVFy^Va8^mvZSVp-0661+zHiq_r&EMJ*t`#_kdbz(YNqEhcgqxLs+grxa_om@QWTATTI$v+^jsEzh6ye$_oX2U^?x9{;+z2-#=VJVSegSr_{+gNa!NA4Xa`YXoeX32k;O`DQT?^`8R;hWJ2=~~ExT^L7@iW7XaH}Mb8-1qXJH5RCUY+rD_lpyMt%QtZKYs^lEwfR3>4jW`J0EbqDNgeIo9%c8^4n9a6YPX6gzHVR5pK@PkAAn|JKDF-+w{ag3*T#IpGd3|rp5q|JA`r4htKa4RugV)W4tKh-x^l{cun*p`-z5mwn<Vt@`D@CzfS`Z&!M{r*N@c3zT%GbSTDVdAY9Y&9cpBKMgG*Mb|>8KI|AdLXB5VVi8Ua{lfQH8FQa~K6gcHUdedD(JXD*3ecJpdf#(NqwYo>+m9=3X;rd2=M{E01Q5;&mb`x$qS%z^kY(3&3WFz5L{mJ}&8i94r%2>k9txFLnUpi6T>WOQ?AAs+AZRd8<YddQQci!_pfVWP1jXuDI`D5Q;0@ih9RugVV-$%V(4o5s>0&dL&ZnnUFm%VE$_<3JKJVATe6UIVs&LPlSD+hh=+ZVzJ*Ww3b-BtQ6)?FbXu;<5qNP;`Xk6ofH@HmVE#@!PbpM!3tB|kK{h<LE#(Z3GF5Uz#l7zYMUq4v^_t^$7q<D*Yv{cp`9TsN_AW3}``eD<3N{>5KV-+3o#A5ZijN4RZ96TiNv9OCM8bHc^=PvD=rnaAe_?qpBcLag&^cw@cS^=lgP&sg4%>gokQh$)1NN8G=n6Vb1;OifMpBw+k>8m**pNq-tfxZe2;^max+GW5}e+rhxa(?8LVYUcreCjO3|fbrJpaX1y(*?_;BmOLh0yWEa&)76FSHx4%@`^}`MZVETnl|uV!`_NvI{}667Za#U3^Xqa+gq!=ZA81@_hjm4%Fv9g8`-e3yQT%IZKD)>s-ft9f^Ju&h^~ws8Q^XhZ+K`!;_iGILuD-*}AN!ndGGhL{bLE@DjcL3ux-tXC|AoZ}*PL+R{fFRuq*Oledjhw2EXR6A#C|0_6#K6FiM){0Cf^r@i!0ctwKpDwe*&(2B7WZ2)yHPUI-&bW!u15~18aUesh^6#4<G0|bqMy2&Dz%~e$1uo3D=`>&p{vjn)C|4#e|z)y#M?d{nT7Mk#MWlYsABhtC0U99C$w9`k95;_v;f1d`AV$M{5UR-QIUF;r2@2_pVk0aoz*Cb_(%nJ}!a&7}b|>!{G6Gcz56_4S{>yf!=1=FEZEFN4?yDiwegnKFtngP_M68znNJJ;aqq|Y3QBphW6Ss8ueXT5^`L5Fz<wHCBKPSU&z_u0^TqT=S>w~|4a5%MVy;n823!;2;u*8zVLMx){VEK2zN$eUq%0xjP@PV9dcIVoWlOn5ApE%@q3Dg4<WF>L3NzhC;UUWegU|BaRcJB%GY-!$LAL0d`dw)uj@;=eg@|$_O;50pT0qaJ56!^qNR)>+#EOYE#XgbUL$s)zniK1ydgY^&vyd5L4NJxFG%lsoCn!nb$|yBdrp3f!ugTeCYs_wX!bL*=iz7mp4|_7Ru6khaq=(<-(@|^qQ87^M7SOv#rF+<p>@9481;zs_T7u`dfyJvdv3x*lC!=z<b3}P?O4o*aKmo^=JC`H^ls_=fc%^X`x1K2{*d#*=Pv2pgmX6|WGwJOkMEG25S-K5BSyhaU(efwM<Sl}>(juWKHQ;rTkntf*^cj1(QE$=!ufnqBrSlQ`+csFpQ~Zt!_JHECei--Rgym(=Zw0U2mQC<s}$;YO~+y0Z&?=cmbt@a^8Xy{6WVW!fPYEtWWt-Gf9X@VLjL{$+OKuqd&AG}Dd_JZWzP`ajpN+^IQV@^5^mPqi}moXJ@CW52R8ZbGtOtN{9&l?oE5acrSW;LK4mEEw6hUzcxQ&*wdlXX$+D2@m7U``b1vu=2g7JT%;*4rCVz$B9Jl4Pe|ZDv%f^H(h_^xCSJ6KD4xC4eW-LFkBJJZE_i=u0w;zIdC>^<t_U$U-yjz>L2K8z%BcApzE3C!1abqp)*D4<%{^Waz|7F|Y=Zb3x*IVP9-T4#-+$)yO6U<dOmv<`WrukPykEVTDGc$iDj>?Ss>LIlMXE&~n`kusiC9>wl`BhcKiI&+9{LbEM#2<=wH$CQ|ULDW>P5XuQcwDthfIr@*b0NJW?i+{;|DaxlPu?Q=B`cx6MUoK@hw|ShJ4YiP^t?48XVI%WB>#9fj1Mz+K<|lDcgfF-asNT2jDr1neecnENd1Kvm%1!Qd)*oHknG8X`xVCg+O&@$GlW|=alb<M#rKZzX#JS%DT;d<dcW(C^U~u9>HTr9V{vP=W4Q^03mf-9%ykt|uX$tXJl0%*{dU_s4E(QVydZyiuR*<Pd7vGyHKp@9%fS3@e8v8W*=fKllGE`R{QTS(<N1{Gv`_B@;2w+CAQkLfcAaoB1NUC+opa&;_2u6X{uuXU%!DP_PkT_8aFfsJ^nK-FPuR}4B>yz_b+tc}!QaS5=Z#J%;!1DP1olkmNVqm&ApBE>`|0(GwEwM5#C)x_>BZwrZ#p-2R`R%!G8A}|P{NIsxEEx*=R!Q!o&x@0+#}NO3`D)&tie5tR)`-XW*Y2?yg}#2RuJ|T#WSAAjWTpDXEsMa(hC;GJT<)w;UWn4nzR9V;Llh0agLY$9pb-8IOg}1kC0Pz0LIBb=1{wv^+wUTitdMf8zZqM;%eLxIuCIUV?41BV;&UlZE0U$4BL)+m2g4t>j=6BVI0Q&E^Sf_>f7@%;rd1FOE{~;VSo3TI4=r7yExmHKyQh;I5$qRFn_h?{*tf;_j>wa-%M}fj`;jooA&#S3*25B_q(iZaZh11?ycD~zCljk4um`Rx?|i+EC4y)<8f|KjK>Ev0dh{wBi!oD`^;D7qrT}A2salmKzk(^X!k$Tx{>^uXkW+uG~~ql6K*}iy*tgU3%xlS5H9Y|ft<C?X?<><a|k!XFkd_0Z$NMGL&A;oGcX>OK8iR=YDfFo_EOyUGc&y7{m+Rw=XoE4_^A<!e(`M@;f@#X4eAGGVjek_IW@^Sj(dipI`#?8&kYC{y^kXP#Uj{WZ7cY1;l84+3#@z3TnE37`;B(pVpyjwuS)l=oI>1xPw~9@b|K+rX560?GwLCJ>OR4}ym;KVbb5rM9sB%B=e^nzzW3Yw8tUb55N`gsw>fz>?2kQ+^Wj;D6Z;(YE6hQE6K+kzzPJ5wHSBaU)48rlL_FKxzo1@^a^So-?8iRjcW%eLz_;T*s=m@hzk9iyaH}ukLHq29`0q27?wc4>4)DD@?q6XYX<u1ny8=IVSp+|%YmR-a1l*@JbMd-#9&mks6z?-T7|%aW!#$?QxUXw3`;PH>zBlc22p`<v)-Fwk{OGp8NAbOjRgtiNUj*UKJMO0^&%i%j{~-Lw{b6IzJ>agFkW-Y;#jd=8`~t;rzbOFskgbwfUzuSw2sg90gq?YKeORg?;m$(dkFvf)PL)u?H4FEmjq1MW7gZu5XFcDe?lA=ImFPp~qIP@SyLQsVg1>%w!o}(Kh{L5h5&zN6!T&ez)i|r}W8bppAB1bg)<OQ!(~#5qZ^Es3+z;0url9}6sY&PXP8-}O*H?tV|9$2VZjHjdbTQ^N><n6odtP<w!~gks|8RUpI`6W_!2h<J3w~Y{K)90;{<jkR2)8FS1O6WOk@QgbQ@`2@atbVg{PF9tuTrrs;d&{wm)X7)<mc@}xb>Xx?Z5p9{zXGQVRuFNb0VKB&6^DQQM@j)ab93&JOnv4OF?f}j8}HKw}cy25Qj!%%wMMFqWvwSC4P5cAH9qHx9|+Omwg}YE{e}YoHV~jxHAmj_2yah3%w!Vf4mC6X@7cPUuEAw+_xRxkbj?o{V`n(Cfu?3cM}_ad>5|*f7B%C?R6dYG+vGS3oUp(P#`tr80WD6!N23s1A*Je{OF#G)o3!-Gd}Exnhk+}!2D>W!+d8J*+IBb3HI2TpjSkA;+!V}^|FF79-4D25pJjD-<8;quRjgL{jB9Y?zKU^?C@p4=RD-`nd?>gAn+bsuW{hl|N4sa+j97QjkYHkdQETqZeYq_^!EZ7fAsCe2-j{tgWoo%rE@*KLongi2>g!5zJ3ID?hnB|-|#$Wm$a3zPnC8w_{;FT?3<eAHNEaQ$lqHN{F6MXpW2U1!p%CcQxB<w_4Ar#gd5@b-H=|e1oW<7Nw}EAzcXrZ1N-?$Ps5(`9l<Y(W4zk;8S=~W?~IZ%V0`csv_E0D;{CwoVerFrFT#yDwsRT#Vf$F@n|9@Xcls!Qm#u-E=^Q_2Bp&=<zaq>3TaQK!a!N}jr4wGFSJ$6@LZ(2f2B-h$pOEz__kZ;hvT_y6|Ns7k?4`6JgG+W-7t%7E|3y-;q}GfDGp?TdOPVa{H_iuhI*0K$Ec3HWm3$@ZnM_N{w27oTl6p!SE2%AGBN%@y`F@q@4Vikl@Q!-U&wTkLrI8dUsVbKTGLMpFGG7;#8OG&ZnE!!*tbCmJV4bO0hLXKe(kw|4k{n5YO1dEF5kISZDmPg-nZB0vk)KumJM*cs1ClndycB*`vKmS9l2nBC^kZErZNug71bAM_G*YI^B@LC7R_b{n(@&BL$b42wze@6P!*d}w@MMzo)rB&Z&o1e%3-4Z+w2x(O=KNohcDTT!^2w5Ny3~H75Sb;ll+=fxBRM}&(k+4Vn=<Vt(~6Q>NGiwgXO+}RQgumPIj_npahZDmu0UB07i5%XIfW%Xmu2Z?`i}sv@`Y5J%KDU%6d<Xzq;isqb6S$~<+)7pm2$&7ioYyBmylGM@rsfv@%t4RufQ_aNPROUO^{SdQU&FENu4?0fb$`e8cLeZ`N684q}}OcD)?QMFDU80q|1`da=M@MDqZJ-&acd;+N`;x+>&Zb>dViy*{;59TW;3(TGCdTA0}zFr1flz!WJ_=gx_7v`T3HjN&21BXi0-Ooxu5_%%^xBN;)IyqNE%Atnyzt|F5Lak{&arc#d*i6<>m+J)ExQyo%-Yl2UW3WT?E7af$UkWm!s2MmOkC@)f^&R(T)J=jPZ?&3!?oPuZ^r*)Ln!hJ&2H#Q8I9?;dWCJ?tx$-^J~;hV#ltt6b<m%0H@KUFWt_ZF-3Le()UP{B_Q&{-)w6n+tKJ(k}w}ru?kpDuka^-dEK_pe!Bp3vOE#iw!tNRLm9RHvWOtljQAEzX1`V7(Z*=?!CEvJ8)i=IRfP_#%lf~!^Q8Gbs_$;FkY7PwOB_c7sd{is_{a_Q%9DiQWe9sIbW7>HO6%3_qzXNS9g}Hvkn#S{|e|;=|=%Q%I<qSKB-iVQKMwuk`yk<U&g~PlKgm#D9q!7O8puCTk?I7bjOAKIZ3Bfy=7TWNokngFs91lC2eO?x|X=0SB-6IY|Jb9JSBNa%E05b8qa<C*^~8qu?{uoJab_V@sQ7NW$NyRd}c}CT(DK;z1>iz_}@tim9$WjTzrTq7sl?1KRr)mU#wtWH6JaNG)dAHNpmI5;B<kcshp1D{8BDg{A#Q%D5)r?c{yKzpNsQ&T#Wr)lFN$o9OnDe`~J+QNy;xNkEDE(iZGUq>+jCx*_bDQpB0~)le4&CPS!Y|gU9|NJpL=5T#V=AG#AV8V}GV&`R*(u9m`ay^0CUlmvmLqEly8!UbUf+<i_-hd3Q=WA!!@a3dWAOFduJbIY*f94$D;W_r!&HI+=N%aQ*}9RJ?*?=@aJ_kJ6o!?f4P5@A<uLtZOspqd0EjS?^9Ji?M$sU6GW?sm=LsT=tf+wH!xRxZfO?^aq!1;k=5W4b1a~``JyFlgP1uljC2-xQk<6rO#RCF_yJ~d5<x_(zl)M*v_%5@?E(PbmFun=fk;7^;I89ja^u8wBvYh%za@X$GzfFYn1N-Wu=*4t=+0f%E74*=M|6YJ8B&0#d4JFN&MV~(<+>Q%j>`#OiGW!)cPo|3u~nN0{Is*&Evw_DwhlSI}*Ds@T}HdS^2%{Kb0#?t-*f0f1B4_O0HUWjg<LilBP)7>%tm#6Xz8kE6Gn%Wl7m3_27Ja&a3xYN%|mA{zRt3Wx7bxI7#zd&@o=p7)dK#DF0EW@Yyb`qa#@7Y?gc5g|+rIelL#Y#z@-z6E=@=g`H&VHs_NhotJcv^Y^$ciRG&Gyjt^r<gy1W=RET$S%=vVhuJT&{O)1aq5O4#>rg^ckR*SuTMzbC&`<S#q`Iw4Q*&OWY5Co>jJr!J&-wCPmYUllh-Dfqvo7ZqUo|cp$NC=%yrbGDEk7%r0WN%t6yf&tbp5CORQ{<<>$~vXqWIp+=ZrG_Cexz)UPgYenG2Xo130f@VgO?*t<U+{{5*wadNRL~rM`=l{9)>wU41u5Qs);<)i<@I!;&mXOPFW6q)^6_ByHz1g^%U;TS{sosW#`EvdpTI%1A0Ksl22>RWHWXb15!Ucwb2)By~~Wmy#-|?_Ej9B`ue<i1Vi;9Z=tNjE~{>A~~<#tIqGXVYy0X5I@)B@*vJ<mXurdVM)KT?p!}TtGpNUWs)>c(k4ku*^Vu2#{x;~CC!&~jmu6ku6Q<b*}9)(Y-2emBwdlTi?I`&Ppjfq(DWnHNb(T0L=_qMITd4Wj4NLCf7%F6-8ugU>s!b9tCDuIO$XWT>zudQUYpC;^E>L@Kbg;F-b+8pJHaxCOX?}9yQIyM;v}sW>gUdQR{6gqB}&@C<$rO07V}M!G>V^9exIae%#+B^I~bcGX)^0o`Eio!NNOdiA={zy!IDNx8X~E;q=Ee0n=w-$R>pCes>38no!ADIA0Vk0r^8vcD(lAf?w7PiQY@zlk`}U_*^;J7ikI{^m(AvKg`ej4FYx=SY%24uWj>XvKCp;=uvJnFr~COmCHok^car(l^JPg#`MrzGub$@$^c|D!n9KROtWW8RW?ROwkE1ys&AOG|Biz2LB%SBybDXY_w3l(!*1Ne(VQ08pwe?Ja_MgOljpH_6%`}<IRC~7P_HEDYrP{Frw`E_(n=?;yE>nHJ7C)<eBT3aHRpC^Z6d<WMKL;?TVn@YP3FcMhttHiG87i;hqOBx<f$=0e=aq~?ET=L**JU{s`JG^vrSdAaR9vZ;Y9Xl^r>$96U4CxFa(`ugg;;(uwo{Yj$EiQt<HgS^A0la@q<)gJNXjGW7lE-!;o~KhmQ+(xIZl6*)L2qGPStZqmZjvVE!iS0t02Fpp4B*(QK-#aq*+*(rz9Uq-U8!pUV-s88|QtP*PCTm5|~%ioRUvcSxE&X`SNoPmg~#;0{o8R|6NkJq&@=k#bAMXL8TM8ybsq~)u+F}{HNx(p^`dF>LF<mKlfli4dS|w<aau=y!oteIX{nKY&_#DCGC;4SYYf|c{S#TF&4pkB3Sk|en-t08wBR#CH&q7en(-+l2Rm{m2`;9C-S>tEN>3WROwjG2RCxLd8PW#Cj5W@S8o6LQ~Sf>zy4#l|NYJX-oF3&&3aPS|7_+5H%deElbigf8sVhsk>Y;=;jeik'

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
