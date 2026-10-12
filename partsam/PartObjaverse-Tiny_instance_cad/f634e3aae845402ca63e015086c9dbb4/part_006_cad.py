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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_006.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_006.stl', 'source_sha256': '772636766852e7e915dfa74fe9369e697e188dd66c151296ea37e7ac9673d59f', 'input_faces': 1152, 'input_vertices': 766, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3086753785610199, -0.22661805152893066, -0.34212663769721985], [0.205548495054245, -0.11042486131191254, 0.34212666749954224]]}
GEOMETRY_BASE85 = 'c$}r33AjyF{QlRzibNTb2sxBw$UKj`%*oI|NIEh^q%vg)n^2UDNmPy@37KWicDuT6m$;WE8ct~*kSSC3+wcCq``oja_57dz^ZWHY@AH24yVqHJ?cwab*4pQ)W7}L;6;bkE8MVBOdZ=S-rJ($(h#KB!@X-Ff`V6Tu=;@J`D(L6<FYwvzJGJZB)l$RN=<>b$4Cytve1k~&Mt$p*uN*1g_o=}{2lpKG=u?Ax_d(vW=fEL-ynIN%o=^AjmhY%rr%vTa%?gzxV<P{{|E~3#5beDC&@Qwk+u9G0jve~xE>m9e-^0dy+Y6yQdV6N3zrM}nPffXdVpzDIi%T=$k;i}Z%SW{GPJtiyB<Df-Adh#_wmat6vrUrnpnQ<WI$c?R)1*APe&o?k;r)$y`)ka-<73Rd<C&Z%+Ie!=VN-5<$1PM3+hcpjCse+!oodS6{mpkI=dtRmvi<$}eA9>i@%m$rF^{mk>h`vutNNwWlFRG4Ufw?3?n6`gAP>qr*)wFjy`50~dajp`E&n6cR6fXq@^+VJq@MVpQ2lzYmv<|_o@y!|<cae0TlsmkW|2Li@>;H!cfahCYAPS(LHXF76|<AiZ;-pCOJpaX-}ni+e)K$&xE_j1eym}roqDd9k5;IjYAPS(iS|73eU_ikZWF3s&-L>9b(qLYluiAA<v~4>`&Va~_Dj$8^7?-1dE$DmuprBH{G&U@WSP#pp6liH^RDNK@*PL{d2ru|@IK)D`#_fIde-yA_l3EBJ?nX5e?P66W%@qqxn5rXKI(a*J?%=%erfj;J=e?Y_Y*x&Tvx-2nXfA?PkbL!(?3Z*&hEsQ51aDn#;0VzUhgY8@56CEzx3SMu;P#@k8fF?ZOWtPPGp&K_tKvSeV-T3BlT+=b2Ubm_1r#xW}hi{QvUkbl)GcbWf;r9I6B>TJ+EK*BU7#x9sSUhyW4A}8p}_;u*;Okcdgu!oJVszvR_M&``<HLum6=MTTFQ@?c_#d{+YAZlsm(UuQ27&#*-JB@<_}0tN!+1yR!XF4S8(Jg<byjtmSG)tyEL)#*TiNoCn9jU2@#-pD5<Bt9SV4JGgHIdC;%W^W^K<lqbILLH&>ZAm=rDqcPXZyFEUZ@8h4}hH^(`NZ#U>aC-*s@^g1-Wn&&`k{#YJ-k<gM>-TM^K_AJh&X(gm?{)usYBP72&y(YD<eRKeK5dR%4})&?zjuncooBur|NhsfCg(x@Zl$i`^(A-ic}=$aX!jk-c~Cy`&RcSQYPq}Yt&RSE)xUDP$$3zJtVegb-s)Z1{^UHU-|^b%AD?<x9*5*S`MCM@9PK6L2hWgtTJ86*JH^~7Gf~?4+xR)A-2Qd^9MoeUxw0O={^uT(>#EHd`Q8m)_pZNQ%iU+zz3bO=w2kD>LaG0&@p9d0xsxkjrYTobUQIXUcC#~bJs#2OdHhD#n3q_;HaSlmw|2w)`;w!TkJ-l;CFjutkI4R3t@3Qs<nsLo@Aa>fl-y%Yxw?PctmHhB-c|CC@;av6IdN%ba&8}P@8|CPPsf{bC#C32IbYiTdhIvn-f>9I6W8;-!?uLV2ko!cXo)Fz7H(Q@%IzDvt~2Ga7m95(<&n&yTa)wPIN0BfSz^qO4_R)?<G+twXUf%@zc-k2cS+sQc7x*?dF1ycrd&Ofd$}oh`fgZf%H5hDY%u0M2l?AohU?ap<2n!JJZ|v`hqjw?`&d8Mlsj+k-EAztt5upQS0$G1NzN0;f5rOkrrhZ;(lwT^zGb(ue5EdF#(edwq3s68E%y89?WSB^H`g`g&X5JWO}RUDNSZ0PJB;$T>wbCV{l}Es-u=p0-n+jg=W6c|xvqY`{$QwlaGYEJly1u1>&s*q%Rkg7)0ppiYoD>6JjX)qNgU^m=h98Ns|shBa{I$!na1)3X6`eV&pu<^ZnVHPq2rJ^kArX6Ys%e4=ghe?E7O!aYlrPK=F<xuFy;2HGk)%9=PSBvf0ikCTTVNaoF~3V`KpJ?+xec6?H)Ukot!6*|H=AUrre#IZp_t)3&wilgC>XC6YN*CL+dP4u72KX%-zrO80(1*8tLb1Olvs~-^S#5@zG`(H!%;c|7f?%et*m!eP#KkNqORX<dyfgJF<xML#9sf`zt}eQO|>ZvfbdgERQM|DzE2>ar%YXGM~8UDj9bL^=r9e`FQ*1{QGy%zqQ%#)$>?m>Gwt^O_cln&P+d#vR@t9{<5D3{q5Kp=~qX~zv<_R{`tOQ(oQXp^<_W#iBa2{CZDe<(jSOvxw?3x-yd+bJl;i~YkKYul;>Jp%cH&Jxuyn$^H_Cxu0{0xQF*TEx$~>sw{0zV^T~ZXs+S)u_iaZnKSl1_dTzIu`*uvr)wr^9-_Yy7xu}1Ci|h6DP0cjrYU##(a=x|lC!+p+BckQ8xfT5D+1AVN7?)+rBS+8sc~r}l)!~pSkCoo*=k}wM{5)|#8T*-^M{a&Gl&ekB&$RXYXX$4~_55q;cU_VHCjBl)%iUk4-xbsH_$ujlxmq4uB>gTuk1UsdMO@3B_Uu=b(ArZ?`V|o^cPdK1;)?t|=~vi#UOJC|okX?V9a&w*UwXd$?Mzdyavk)qlbBxrj280T(emioy8d+%*YbG&!C9tUHOS-NKUGPsp8M{Sao?%sexB%8$FKIsBXKQv+Q@iBoet-2CF$quxxGO8`4KIT6k<PL%biKm&yQ-k%8-7(p1Y3pV;z0F-%CF>rsr=+Ki1Xj|3Lb&dhQmNer#ON3!V4-KkAHD|4(=M=RKn3?)<r#rrg>8oqyhKJ)cm=Kkrd3k5#hed8g&^Nl#>%a=Uav|GdZa`bRc6WXj!M-^zX9bZLLSA$YFYeBSA~)0)q_HD&!g@!pMjq}&~To|x~dd)A*{jZ_Hd(K=`4eVLX!e164e)(hpT`d8AA>CiA-e*Y|gydTZqB$UTz$oyesuN}(mm6v23n-R|4yJS8vlBwm(FZun_=-n+tdE{l8=ZrTC=g}8rJ}~xgYdJoR7fU^@)=NA8lRW6pL?(^#+Zk1DLV3&?<BzW+R+~^gPK)*abr{>$HoU)^OUrxM9c@G9Ri&#I`|GvbDRb3gfBD(=q1?WvuwPG%dE)q&D16A2$BWzYzGQT`o=Bd;a{bi0FMNFRwDbFcLGCVCBK7C7<-L@a$2Si0`-jom;d<OJWWG0AH(cJ?Fv$PD#I)SK+V;N}(Z3!DpU2#zrG71U^4`BcIS=ZwAFnU(b55~5`>VEH(w|3)G7pYJeEcqdJ}`DFT)*31=9z;$(I0MI(9a{M!+ETB!B_oyPlxNb$L#X&pRv>7_NXQ$rN4A0+<v!r{r!IV_c}}d{yV&G%lhXxvbuA)ovCv(lJmrMmDSPz-bc0aYGkR@<UBFX?R43n=Z`T@w5R?UdH<<z_am9-kE{vj@pYY6B<FV7x1|0#x%@oJJeV(aCq#z%?a<1{rsi7VU!QBk?TOSLBm22Fyj^E_snp~=F&?@9vh*kQ^6uP><UH}c`=p~h7uJQ3e`Io5>AyYERqnT4mND<>f4?FFx`yj-An$9UTCP&%JxhFGICpo-`-}LK;rinfJNnO&So!YZ`m5CQ&##`_c~;Bkf;<?n?YtoG0V;%ZXZr<zJ}UM@k8nG8%KM|(PvP9%Chtw+i+YBy^ZmR0?|Xc4ICuB%^5-Wba|VX%Uo7vfB6GvJvryi@#HxS(f&V#<`-114o(Io0^~Fs8`xJ~TgYtSFly_2_$$S#uKdQY;4x94mQ(ff!=DdM^e?)(tI`d;P{}jA8;keS(a);weRb-i;2jfbc<4R}RO6l)#T<LIJX*=)xd172Sy0|e9p380#SH@K(_DlWMzLxSsc89hbSyx83o0TftZT3;9{i<4;l>ad;-2U+grToAzL+w;e4oUf+z6tG@n*Ocy-!qSd>(}z2es^t;^w4>kz3H$icbB%5_TSocZ}NGG^1Qff^7`NJ#CUCzjIZ_F{hQ-!J%5PfYb}orkny!ztCjD?@wJvKj<2uCIlk8O_%ECn)pCd9YdyC)zP9!99AE3X;`sWC{CxSnrrhm#ONJ@8H-94ICcU15d-j=fXZWxKraU&c&Ou{6AHR}i%A@D<X3O=UwX?!whfKMB^*56LR7l1F!F(qB`Fif0ZGO;{M>-Xg@!HSfT=o7##_!E<2-mZg<8&=|f8hHdEsr0SarzbcFC3?9d4%J1J-0bd*K-w&)Ae?~Bja>Ew>eJNbGNFD)2}GcarzZG$LXqtmN&?^*O*`5FvFCqE*mmUxjXD(|GKiZ+_`ytmMOO@bdvM+<n6MZRh^`s4%P%y9xbfod}+CJ&$%V0Joew&cTBna^_F$UeDjtKrab<|5IJ9ZzJADdQ||1Y=Nj`(^LCqZ)pB^6F|RpX&etHVof|9eHRWnfi40>tG%M4XKajf5SpUqC2TXaiUTv9w)AKuKWSMd`@0x5=ZrAO7$dt#IeI@hcndPNF7|cI>F7qvVZnu*87FWw-6=l9f&m;3?zD3WSf->Kt=kbX$-=gQyy)xgT_G$HVzD3U!=UcAGIp3n^?oPfp)N+UOEw-LlzMO8%N43o`<?5cLnZ|tH>3yc$J<?8|3(SM}FR@?CWSes5{8_orSF9lCH+a8u_o%GoJW>DS_saEFDO^5!Uwe5!(&A2;SAM>`ocDs$98>NzT_f-7wLHGzttF;BR^Wl<raaPV>N-=dp8sKkF~6?0e?2(*b{j0-ZpxkSC%DFZ!Rp<n+>S=mjQO+E<h`oio&!bpnsSHpu6pkNu_M!z+pm4O&sctCuLH*VkI4L+YN?g~VN#YUR}G3}n{wxL*F&Z}-uf50t_m~_U2k^JdgDxabWQnLrd&Pu*b-Cjw3@y=Iak|y%XL!v&IzVG+Thz6{&GRBJ@p5!Gv#Vw%0^@USB0&n-0kdcH`YIVuxqU6-JQFW^Prv1u{T^}K7Wq%SM~buzc0<0PkLjIDObC%-fPS`->c{DH}7R8=Rtc^&rxZn+#Wt;k12N#RM~5+XXH&8#(esx(ofdglk2yArrf#Q>3}JZ6>M|Rl*jYSdni4RmM)c@oG12c?yh~N++8*1fGLkxta;Fst2(o?jP=x)_ZqI=&W|5BWXhve{tD%ZdYbn&=JxAH<a@eb&a+eV2|m|8mh-FS&cn|fNX{dl_LF?a%hG-=k7h>s9BCG+Cw6VW@uu9_e6N51SCzuKTXVW=%GEuK<@(pl7Z{Xg%ANFadyM7B%KK0~x9=z?%ldX(%J2R3Jie~MK~wG&x?awsUVr3!IX=&Iko>NZQvYwo_L_1x&+bf9?v(2<&)+eUt7Fef`HoYvOnLOtN2H&2q+_Ta+x^5b<&kc$%eY=Izi^Uk%AIdk%6;spR=!lPG-JMP>K;?Bc2<$=o4LDiROq>5>*eczvCou8gZD~WJ&EVh8@GP!Z$FrK9dwib_gwB<;oN@mCYcY>@+jwv>_e6OJeY5^Czd?m*K=6Q$Cs4n@AN96dK|v5v5!{`=WoBBo}4G<3CC`e-?yL8^3mI5ey3gaa6L2SJyDP+<`wx~#?f-c_cG4P8sXz}x4b_J@?btW`gUIb{fn#RvDfqZ?_Zo%lE+^jCGD9#Qu>ox9^HALoR@2B`FZfWSvB=odU9_6K3dxU_3TVj?o@9s_u+oEL-p9Hzl}8I@qCkK`}OGM^R{+PxjXb%xz77*<$t_A&6uD1Xpbp(3p^#)IdipqthB#ZY5)C&{ZXCJ@pt(?PNj$Q*kt}bKgd~6wDRKzO}W##soa->yn4DEhsHAB80695?-!h#Wd88Bdg1G2VJZK8kW((4y9-K5KY2oZKabq_uGDj;ssH{Z$P>Tw9NAC)&WCy8J=DcsGEe+`IFA*7bEx0$iQ!!R-AkTd6T|gKM)Z^C)WmRm+*3{EIrv?J(D&4>UPJy~hI!&XP@}0akAG1`{*LBYxSnXW8Zv**+%7U*+W&D&8Ams56e=It+)e)eka^;~|JO;55A($FAAMQoiS0(A`t963{okv*cDTIz>}C1g>|NpQ#x`}!PR@hhw?{U$ll!fne_KxG`QL0DK0ftJ%KcNzqt`s1oty{nr{Yz{%ijmR)i~6Cb$aEyO%1twW`^{`7d8&H$6a%5Pja3(&a3zySIgZ)SNZQ>?1ka>*msUUn4Aao+xuV2Fy(G)gZ;+xFAbCL-NNv3h}A7A&x^}Vq&(k?sdAn7?@G!O$Fu4ya(tKv=Sz*2zxUB|w`ikRlk>#!|5Dx~>v`lpc|WWE3D*<<r=kBI_KJK^asPdy`%k$2Zkf*had5iXq3@SdRn`Z2;(ESzpufK^^PnDkPMK6w9(#I{|GrN>9M0V>=^K;t#QvtA4CRUU=2KJU@28mC7p6+SWX15NhTKl;D9<l#yRr4@8%??M#H1aeJb3>*F?DTn9-lu&&g0EL8FTx_MO#d{)3>TTj~)&mXS?z{8OeF#c+M=7nw%%<{~>>xG5`7FbYtFdw9G?x4<DcCUr%Nw=ZXEAUP;Ca-NWa_ej_gLt+w73YQHM{pZt9s^ThXs?|B_9SEc*<*T32puE)LpKe-QV3zv`Zy|8mrvv55P<^8fdta<qQ?6OVTJG^=5zTvEjjc#hl-B*f9|3S~UbaG9(+H-WbvHYA`X{Ow{d#mi%vsyj#PNf_3XwM8&?*6_w)0l54wBMM&`QQOl9@)@S?vq*`A2A`zl&i1nXPa_&akoRp^88(mI@}`MkG;@F{=ES$xA~sk{!}Z^_w1@hD|rs~-6ZY2^;Z8mZfm)^cu%$|kN!9y%aq&Wh8#5J&z3)6%=6as?|Y7xyW>Y>nsR5;3mK-|emNuEn4gR9G39DXzBFTgbBf$=_58ict|^Z^*K&s`cNZ<#V#@8b7dIN~x$~%hA67NPd92vnca8aP4Hld7_<gnKm~u7plK*>{EAsla{eF?7=fmaqZF=s$TiG?`_Dw0N#`2T$r5Wo#9hdoDJ)e@1Zp_!ekYUR0u_H2#<#X5DZ_J05KVZt;F+*g&x0ZH1j}6E&<<ax^WSerQ?5)xdoY6XbexuFg?^S1o^H`5&GQK<BCj32pyR!5fwLF%RNAi>5Tm`=m(efyN|6sRo8|wEupRJpnoF{(IcITE6e*3lD&2H+Na{Jzsa^Kd=uf8SCl-qY4*kj7o`mfSWx%2a|3}gA+)8xM0LEEo}x9>OQu~q{P8p}V^EIT<*w7+ZP1E$<5KV0tTS{}ULao)Q(RKLBTgp3pWbqJqd{!Yp5AI@$3PN`$)Un9y@{}son<9)<aUR6Z(?V0pX5h28Xft&v+qW-o1zy2wr>eXx4_`m&IMAx23QEGyxMf7f-uA#sU$?%hw2waiN@H9&VzLv}I4=oWmFPGsbED^W@m*IIRa04=YAqDPAh99TE>*x*0Uvk|M3VedTj(mc=p5B1mfNfY$&r8nB{aa73NUq4^v!33Ke1blK-i`dMr^TL*(od4xdRpS?Yx*hjH=a(X;9ep=kqm#t)Aba%2^oII5`n958NSyNfp6e4Jlzt33v(HM+7f~9<TCs^3S5(1lWku@evtei_vaLO6TK$+Yp(l-I>miG#r3Bt@cZ<d<eF^5`}D%(!rZ_2=~c*8czoWcKSDlDpGbd%JiyaZPv6qdkmH`tdYVC>M27e9bRz|}$?$WQ2wauR@Q*DK_+~D{Gb|Cf2$$h!EfM%uF2f5@;9BHbZ2MAjCvqq5&l&P&dM)y|To<R#a9_`G{aFgUg<gwXi*49KFG4QD{o6vXO0LS|vxVM+e3m|m-h<rA(=t!r(a)2=$1(NvJbf}5-qX`f6!<PO{JbRsSK~5#pCtm9<T5<d5`jx_8UD8=0^i1Ecu@*mn_Qc1Uq<ds?#%r;Pu@zeP5zGSzNgM}U(a*>ISRauUYlH-ZP-RHK`z1l+eWWOuEyiDjoy=djy{>*lRVJV+n$cmFOYx0vG6p4K9UT7%u{g++>{KzXo<kpxeWir5`k~wGJL-!0+-@4{DLI{m*X<L7zM6FuEVy!O}?LeKlkSXc{{xh`54#zKwaRzUf}w_Dew+@9daGEVF$ewxfJ(r2faGEI*-o|`eWq3=_Bcnk)QN5*wfGSi{u|YUGnq{eH0nq+f#%B-%W;JwnX3>T!tUCMBuVqh99s*;4)l>U$R8t+qn!cO@Zr@>$2^G$q$ep;Qm}B@1)ly|IBqiQWv?e7rFit1^$3umt2=^_<&x9T!#Di0lfyf29M7N^xou4^ilNQ<gYya<!L3|A;Y_S%1?nCli{Z<5x6p!;U8Hda3L<k_gEruK`z7pvP9rYT!!bPz>Uc8#T58qGW;Y3-av0eKFW1pQ75^tC%OJF3cQith}?*6*hnu(F3A1cNUuz;%;U3>-ktmx-Jy3UKjCSfr_bnrl0PGVPJ#cRuOa_IUQ31#r@&pv@P924xIVMBWaRK)ED`t)u3Jk+4&Pykz$sj}mW&*}-4cN<u3Jk+4*%H_fy;B<S~7C@Kb8nwkL%Ww*K*(Mv0ObKzj@3aqOT#(qyI@?L;k`W2OakGFa1VK_+Rp3-scxvInM&{JM<gLpDU^BANs%Kf5?mYTv%k~JUbS#jz!!i_>hviim=Xq$PjodpCenXoM+8e*0Ggk{B3x?*VASC4VLg_a*X|on3dD_057B8K;EyUu1oaG<V)m*?1wD0a{4L@S;s<d6P&K3uEMPI5*Y$-VZUXImD9J`!aBCFjK2-fKf(~0UdR%@NPf$bzAHTF>w@2=7b0gWsp|s$BKZROO-uT^Z(2Eh<2PByo7^VY^?Z+~a+Y{OOBe!wYe^p%9`u>Po9P9~_-rOWpUHL<<a+RCes;5!(<k4|wrpk@zpb99c{)!oU<scmzhTLk3m%No!0*!wkTaCj^*8-I`ET+9OU7smtei330@ksB+XR28q^|2(=ig)qyvdR=-6kt%47iDPY+@Pk7F_$D&eG43&yrua<e35wo<ZRGbd&+(vm5yt_;p-&jy#{Ag$K_#@J9M|<dt6eF`jO*#2>SSA@CQTa;J!oPZ5C^&>tgX9%r1V+br=umM{eV#*#5L9OJ=><QTmVdA9f2S3RXz;=hw2@Vl1WSK-0^89beiGSivEgZn&q1|4N)Foy@v3-AgGoXgW(uk0L8f6$TrL7zdM!8-q7dtW8P=aOId_U%4T|5+mNAxi`<PQS|%hQRZc_-jh|X^+cTIrAUzppOAQ%5^9M&c`h1pMW<|;QaJ5<ox6fN(5d_f0_(mp@bKCTIMM?j)AB5Jnf>uvnlWiC7zoM$7jL2alSpJQsBAtzm)J?@+l?0oDAPYUgD{gSMDtwb0yxG%g7s3;P&3Jc`HTyY6|>0*P#sfYG!{@;58KZ8hR-*9PI$F@_e1A(zrgAEO%m#tP=(9n<Dda@L(Pf{3X|+3^)(7U=9$xjsjmxFHMG{4cGF#;vSTr*8{GDpic{aodV;Yw1L;eS$<{<?^T;Ut@m_B$z0_;D`##Kyq*H*qoZs-`g$_1>4i$J_y72P_>}^$q`+6vi<9B_EVzlMTdkb=KX@>=2L77sPzHP*vtV8hyomx|Prud5xzB^~9Du+d(3_Cq+m!GwUiU5qo<qm=K8HE{4+^}R0_XAcj#qZEr;~JKC+Ty@b6Dp|ewUV!;qQ<!PlY+SU|wqgpXCs^9KElV^V|o!N_@K##{BbZR?d9&Ydp8`(@J<A8Rr@PKKXrKH(<=qVD2fH&jJ5viNNLQ^(^6{Tp!E}fwxfL!u0Z1PJaxH{u%^MrPm|FcPL@ZOJL3=n8yJBV2QvL=mRa`Vq720hk&<I;3D)2R!+YcjD9f$&Y}+_!@p6&7>{GFAsD}df3ig2O7zDq;nG|m%maY8QQ)HVO5~#CPn8IqO@EvW|5^!S-0?)xSO%PBiNH6}qn7YLTo;Uw!0%Gv6#7k8&hs6N=RX9VNsp4@Gn6p?e+YMbYD$5d(OZ(6kz3JQlUtG7;MsuZtEWa3*rvB2+vMi-Hsm&}2V5HW0#CP4;Ij0J<g(-n^eW^E<U8p#$#;@#(Cd+Fkn7SLlN)m%>aq<tvt6ahCFn)TCCE3?i;!<3-$*Y;zL8v9;T4_tobwc+z$NL$$;DZ|B+pR;p0_6C`t&;F`s7;l+GKcjaxHQ-dS!AoawYoh<Vxh*=;g@exDU6{BV^1WWLr7&58zi)MBoRwz8Lud@<b&9&r;G?gy-Ti@>~=ceav6z!JNhl*1dvd!01Pye}ldR`X1<W?54o4QegCn;Mb7h_$(OD$)!r3m3X$|nYxn#&m_Y?pun@p@ZTu#DhhnHr?<VjW1f!FksYVcBEQY`ODXW5bd>p%K9f9?Z3DxvBEy&Rv*_30xq`k8`a<Xf1@BD3uTfw;i{RIi;rJ|g5xx)J@*AGdQ{qFpjC?5Nm+`KJH&euOQQ%Lx4rRc(nEg(H-=n~}=_SZ;v;&O(>{=y#TJ(p}_dQO5*HYlTbd=3YUrRpX`DdP#C2m>5(0@wSL*Or!JPY7>K77eMcwT_<Ji+q?9?V69m(WpW30*NiKo91$!At3i47bP!>A~DMcsbo7WB&FlOXeOOGUj_%l6za?Wy!tCk1G*)jgql5{5mcpzm5WLq<=*|MaT9xG6&;$ujDa@-@@|(-NJKqoR0A{1pb2AE##}b{4>wTrHH`uQ$*kgE%B1%2g#$A2>hm!z9Kvimyze8z^mz>k^i7$`>UCQm8ZiVk4+JQr>BU(JuUH@$vw$0C=qx8?+FWdKUl#0Y6`rHewh3l9ot{U9E@xDAg^P1WnL3dWnLSX>A^b}@G)kU$;jb&cQA^K_chOuTd-VZatrc!C92Hr<Gts1mb|l@OvZcC=gIe2;&+hmA&*re@J=OjoA4XBjQj=)yo~-G`8*xlU&b7axy0Q{<_F=oTfz_+bB5>W!Mk;EoZ0PU<Z!$ro<zob`5ENSEO$G(GkKB{-OlY}?hbQ9n2&>FKBxc%#vI)ldhi<z@HfnEBjfioM=bg6#{@EdZ?lNp%My=}dy$`0BJg`k#+~qdTt=Rc0%Od2k{<kqXFcm)&oW@lu^&(}Zw{|$2}5AarC+26?_|N>Gpk5O4#&I2kz~Bj9YJo(auvyK$&M0L<o2gwUp>7{fk)Fvkw=q9;#lLJ=cyq*KN)@xxgohN1@1?I<MeOI@bAcR^7r&(<nPHp(C@T_e;`+}#GfTsA&;PsB#-32fUA4@)%$$&6!8g`@Czy8FLD|AixhYg1s+d<e_<V{>lX_A6a^kg$F>L3pJ0B6ry-uo(+87r%nR~(Uq{YQfeX+Jk>UBs1<2P@;A`ZTsIF3pN4n3!f8bo6uBPXqUqy!JCg)~-c_?sRdOq@0Zv!uR`W@GDiue>RBcDQnCsN=SDDY(ZRPtnUa4x1Mog?rIJdfbt=-3{(Hjj06`VHjj<jVBI<jUmRDR4OoT!sRdqQJ!|a4-%62V*60FrEUJrWaB<<1g^76u2S<u0nw^&coQJ0k0i+Q!>068QzKvZ$lnJev;mT48MyEZ%l^QBiG~hpQINeKS>_oslTVHmN4`i*AJrqO#hAiGug4kpSOge=aa6J=aa4<@H@Q5z%5cl;2K<yx@yn|kO#1BVE7nv4KnKJ#kyYMGV)g_@HA=+@14()M^R&V&ly3kLa&;1zpBc68XU(fxW9pedmuPYfpJg8{TBDx>*@W-*OLp<`;+@~-wV<Uk#UcDTFHHDJnv^ea`|a8{2B6(<e%t+$b)$PexktREODH_aXgO`$rJfKA4h@5(kGKA^Lsv)KAsFmJI2y~B4h5Ls>+#X0N+M|gE2lhm<Ip{a|PgFZUG$3KY;J1z%40oYYN<)0^1Zgm@fj?rNF`b3^<s>0SEIu;9xEY9LyJiZ>GRSDR2=AT#R0lJR5yh?>Key^sEx^N`Hn7A4Z12U6cs?k`jTR^0eQpbDt-d0$-*NBg0YlGJP0%7`J<w<-jg|c2b>SY^Oe+o1Pv`5rN-L5rOBVh``-Fja1?f)1M&2>ysgHHzfkUtVG}rEQ{@R;4-)m1^$HoF8LGk0s0(rZSS*>c)B-51fH8B0>7Ff0(ZncM2YvHKSGArCPRL`N(6pIiNK9m7TasYWpFzRe2_kue2|<)f0aDdQxEJvzMD!sO7B62w;@B|N0kUXO^LumJiV48{xZD{xee<Czs&8fprak&*SId5zJi=hK182NuIqjFKAgi85qMgP2>eot2z<Y%=au+l^!v#0x?~94Q;ERSl?ZIJEVgHJ8QhTqAEr+uA0~fFe~J8*r>5TL2c?L>cY7MD#M{xElJ8aG)wqnj8U=2~I#4foH2oI}{44z_@~`An`XKVtDCgDn9K9tO0uM<Mfm`7opu{`STaqDgdwMf61U{-n;D@*#+kS}4;KwQOPZan=`g7#x*e38$PtCp0PodvShQMP|MBvt*hAZ*===YK#a7TJ`G6eogiNO819^3B6WuGZ<8U@}%pF*C(Hi27vs_A`x7QG!A0>79d0=M@xL5V*=Z%2l}_tR^VA@GYz1g^vN*mfN*gIiMIk0@|DeHM8Z+XUX_=}GVNtLcNt5O`*a2;9Zf2qoT$K8Or~AEZA?hQL#l2;7zHvF)y02KT4Hdns@ReKmPC+XQaosh0Qo_vrn}5O{ft2>h_8?n?Y2dVewm?o6*mhQL#m2;7kCvF(Oj2H!)0Kc>K$^!Lc`u}$FJo(6lL|A#)De1z+c(*GeJB|l4npXO)q*{3Nme*Xc1`zjH*4}CBhb1(2-Tt*(u&wv-PZD_|Lw&w`BftN=;A7F{Vt2}){|B@ahe@X63fjjYYs4Mub1sK1@fWW<#2;7T4fQ;Wn!5`x?^2aDJe*4t1t(8(FSI!@=Eia=U>gaVKq5LZ6KlGKoqtj>b(Ej{uHvN;~KYL65<SSlXi9dqt*!F6S*S*1iir-;xgI`>!{{iQPoNW'

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
