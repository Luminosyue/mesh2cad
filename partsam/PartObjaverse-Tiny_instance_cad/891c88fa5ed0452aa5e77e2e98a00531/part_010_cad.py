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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_010.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_010.stl', 'source_sha256': 'fadfc924e97e4f400c3426f015626f576c2d335b21f1de0de0ec01010906bf60', 'input_faces': 1164, 'input_vertices': 1002, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3458224833011627, -0.4810865521430969, -0.358883261680603], [-0.17530708014965057, -0.12853050231933594, 0.24993136525154114]]}
GEOMETRY_BASE85 = 'c$}r2dAv>K7ytJ?J2I0fL=KX9o@F>B^H`}=I5JkIOqC%Ai9#}y;vmU9&(kqp_g>dLWQgNSNs*+I2L1Nh>$9J`*U}%q*YC&cd41mNv)5gFJm)-ncy{Y%_5-;r{#VFKe>V6=-wu{VEsK@Q8q~GlfY&>B?O(Qc-**$N9Ij9QJe|_AZHw0J60AYikYZiB_V3)USj}LuTHUG_D;+G>txvxJ{W|sT*r#8YuH-lD)U$tA$M4^xQ{S#mT)aa0@)b)5E0ri692We4`<KaCgy^q@PVICwR51AhX>|L(O?7>KtkFK#59U9*?!SEN>dtL`-)g^u{m6?kzaJUB+4V!?uded@p<NqXKm2BveWK2abzEmw{oQ^)xN0dc=cFu4ME=~U>&ME3=L>({49?#-cA8lJ^HX`glX4}B{9h(;{+*rgi1{uY&GqZXM(*_a(fkq4Pi#EP?}uL=!2aKlF7*4sYaLualCAU#zaLrolIzE(wM!D)ZFMW&Zco=p@#kA-o3g*=;#yJXxmvuxCKuT3_d^qF@O*b99}vq^t{l(zxyGr&4?f2EEAH*^`|<60c{@CEd!OHrHGhEj*LS;ji}}9&`#0|2oj;l^w)2;#Tt9j}<6*Hqw+wat(1PGWe}1$>*!6>Do<1VxJO0LbSI0C+75Rq_yMFwID>C0|#`(3X9P;PKe|y69BM)^yD%Q92=jYt~4}KH*(W{+YKl1Gnng8f_XWjgHBM<xY!$ZcoeyDNLV`BUKT7vTroDuo)meDir^l%T6AFtSl{n$S;f5xV--8y4`5`JXwJl7AES|I1!FCFK%Uo7&i^Ak_ITJVg>4?gkYY5sf_k?Xa5Ile!_V*A9}^<uwy?&G3P)AT(3((7V>1+#WO>E_RFAohDOP}}t*W4nqvv5fmqxa+<AmN>40p>picA0$3U(QN71FPtRn)ST_c;p)@m_duVl?C(D<zL&y}rMlZCRG``k@p=4awCh`&JMR(O|A{}{<0EqQy7)c}eLmCm!>?@+b>ewOxW4t*BRfR?z1w^o|CMcvs9$d|`{jph5X-;yP1lca3Y`?o`E4fG5AFGLjo4p>>bsxANcRIPME&fO4!M8#_W@BSbgPH!N5>CXB=VO|cfUs><p$3ce%HMRUHvi3L^0nlUUmKGgY{4O>qlR?>3-kE3XW<mw$GV@>}T&V+3$xJH%xZ@UMJ>><89_st{=`DmG!&7mgMTh7E46_nSt*2W2kD2)ndNO%e#KO-33{v<H$t!?;3{Ji~QbG_q*}rzT$g0e5AhXM{eB_b%H4?-0#y!zW25Zf8~(9?s|RsoyfQDUg7WAkJbx6^zDRQ?(~mdlliOq$J~1PZn^t0wt1kd-tSs;aqo?F|HBU+&A-L(Ta!m|{?PIp{>u;EdwHwh_kJI(eh=;N`;jg0@$X39(QEyFI3xSkx#l}X{i%aFe^rw;em@p@hx51p854Cf4`hG&v|WBb^hZDby}OlXuUOwk>_?uczw$r*Q`Pr~`38Hlf9}XKkw3Es*MDZkK9OIzD{r?aM=uh~xx5qmUGpv!>sy`s3GtC__KP~ZU*`FaUOiXTx%VR1$^Gr8B7bii-frLY{zPnli~AMPiw(y3{rLXITz~kzRw6&pko}vv`uL9@t5iK~hj%9U{rIDGdA^lmQ~Z9cTOD4ne6d8a-7Zw;I>WBc5&1o;aGh84&lmpYQe0>KpabG~d$A<1*TdPq63f}E2>ZjoU*h*8Gjel3>h9uIV)@%=XMaM;HNsz!j^{hNXR@gCLx7L}Yjf8NzXtrs`4sWF+k21uKW{Hi`Y%6NqtQmOzAgXaepH9glf-^MbI0|=BSs$d=Z8!F#C5V}+Uoa1k6w5ESnByik)M3o^{tYZw~6K1c!~Y-f9&`B(TnGKd4A2AERK`m$JigVI#tZK=MnDL9he>y{?^0nm%X%C)E|-L`jNSx?-JYd$N{cj@6sNTe_{jYPpWfB)PHt5=U2TWmNWMFK=yk)b6Dgz>dV`+T{uO29tX8%f6sQ2AGz`vFaO8I4vPIU@E^B78LHFrh&X<J`ic9W=SGTrufH1E77_WeJRftNd8JbQ`Ju`^UEj)dUgSrvz0CP-2Z{XHt*Y#Ql<uh5?}3}#zs(vrB$g-3Zr2aqY%TJm?Kg4$hqXn1xa?@xj~4DH^5eA{a(>^%B0qjS3;XL&%K3&Z*SFTJ6m=pqwsAjsX|i0N@zc3qy|BPxu{^t8;rv!Lgddz--1Xy$e~CI)o-5q1?%he&nRww0e;yw?Cf2L@V$L7lQ{;z!uHpKTH=Yvt(R7tuKlWfhkstl+F89wb^%8!3?KRgAcWWW%TY4<_+h;x}^9QuzI)iG<<^Q;<>qiO?5OpGhFL8hV_&;(#CdFMpxb1y8-;+yRKlI!QksqmDhwDu4Dg01@f}CGsnXL0?2KLvL6Zx^jd$|8HW~bb4t7o%+a;`X@gTe0Xw|`dn@#=r^{Fl!cpRZucU)lfVrrZuMC9?m|Ga^59b}AniA7wl)mZwSwp3jg$;`<?zw+#DJGYLPw1?MUC9uwa`@on2(Ka$)?)Q?*;TtD383-LW4eg75LkNwb1<j3Bv!uf;7iQmC^-}LM^y)Axcqo?Ncc};=!qF)i-Fv|5q<5r6L*5pBM9Pd&><Okm?#D4IY+&*9C=lb1JME@$Z_m;ce<5SW}KVb@=H%)tfw>Tbpb$9*9?vF+PEw-`=pMUjz;)H*`p<ouS^G0UT4~(Aqp3k#BZZ7h}xxeG{ta{f(ztnnn9Q%{1Y!k~ls)OqXAH6C1!_f-4Ie)@eqQ2FHzh{FvU)&_>*SY9^Uk9JBCi>g4-Wyy$5<DU5#MVsYd|ZDs+rL0B{@(v?gXlj;@)cqKhZd{Fe6J?3U%Konv0lYaxxZ)O%N0+G`IdZ(ugfg#yj0Zxw-oz%@-7y2#us$`_`dd{P9*pl{~j;8yFje(=638~oiI=MXOs9kRE5qng@5!@*N<OcCzrGT8182bdt-{opL&P;L*qV+h~?jT&GqAV&dNF|Yxz9%;;kNHyR|CHb()=th~uZ}6}}!<ZpS$B`JFS+^}|;SpYr>`MQu2LTIwv}U&!kEk#wQC!q1(|=dBAvqE7rqKi7|zAHPs6&%KiDAFeF=z46f>x&6yX(!a|^{<E(q@$><5IV;!W{^-({qCXs5yO+;@FOQMSQ*pNI$38ByR`~f_xqdLU=Q`mJTf*nd=PHT*Z9L~-*N^}Fg<PKGj-20i@Fu?>EqsyBug5PF`QbJ@*`HHK^n2r--sbb}JflVbHau~)d){reSt;wRD&+d%1B>PQCT4g0si6$hgdYn|bo-;xf}^EBbg_G$9!_X4{K&N0eEz<vzVNMnBi#OO<i>-t&IiR@KmOZgUcRjh-S3xBt)bkXsX8Fl@5es4>-IOIm;OBH_rpgAxqf*32;p0ce|7r_!D<<VAHDsS>qiqOq=@;Z+~nW!ez}An&)ti!9~PLMEan^jf!8Ooknn@md+>FRmlh?7`HuXS*E>*F_`%fIc>671cR<Ydi@5u}8G7j{J{|*ec)cF|#N9r@y?Impexy?m_=klb?UdE^BhSx0DC#WxmiuqLUl94hWgl@r@ZX{$KQ^i}_XG2OBmDTN4BVewvMj~#hYrQv?HphHn#d0y8qNK^=PQZ)c%BaMuPNW={rK&sWU;<KpL6$1_}@MvKl*dT_2U!kiu~YH?YJMf<ag!Y<LgQ__a}+<&3T%y^VJ+G@}r}N;JQ?EksogVJp4ei^zZWL;FIHGKgJgw<<H;550j)nh(8a(b|ODIycK^>)Xb42{a@YVB$#qBQLI<;LD#oZrtxu=d+L9Gj^N+-If8%R=Lr6NpCkD9eU9MY_c`+Bt3OBZ@B18i^VOdtFJFI-y!oonk(uw!_S}yR?B?&|w<mCZ>CF87Q*ZG>zaNWV<?S<~d8*$Jzde?>=k;<TKeDMSe=bTN7k;o+dag5LLyF(G?8|&!v+X63ADuOdw}1WGB0t(9%;!_xFA6_+#o{{0b|?G&P|*v#{d0B``SGpq@%|dtMC8Z&yu#-}+pY^goc?dV9$f55lJK{D&HJlGKan52@GgJ8j=doAgOgw2I(PmMezf=<KK_S&b3pj#kMr?Af4HpEe*hm3Sv!mT@VYkKk86=$<j0%-!sij2uF3s=?-1X&_-34}Gp!GQzB>06`Qawq{|=AM$^D40Kj8hieV%*#SeX(J`u)h(7x=vXy~2n5e)PeDd|tn<g~+$kpWyG?Y+t4N{m{kF_;~AhB1P0`-G;xnH<uOp@e=u5KYp{F$PX1i>>ejpm-S-4;Q=%FbNy*NS=8y*oWGy5)e`x^=DGPee5Sj|k2Fo@@7uY%<Z@1*%>K_el0=<pjre=JNn?>8yp)~4=Og_^e)QsA+z&V;mvhquJ`PL$DfUZvBlk<fbK8piu$`HY!;=w_A5VyJf34|xG2eKLv3wjx9+dT)^L@SW*-mmfi>BxA`5Y4x#d<xlm5-~@--|lY-qrbgsazl7hc>V0`+R4A<Kr;<yX=>GjDPnBh7bDv@c&Np@z8Qws^5<doay>j@M?<R4{mA8$H^a$iTrRZH`iI!Q{+b<IL^n(g85>;*32n<T)lETS=2e-nvau~B}9Joe>wQLN;g>K$DcgJ$HRpcV!oj*AG>~Jl_l%H)r|cQtBCyg16lZZdu2?LSl=c|{Ciz_o2=97L;l_WF^kBLPHD*Zoi5fF`N3k`uMJI~azOYO_VDr0=YXv9*8AKasFzRV$Jf_mKVK`koZAxkc>6Ib_Iudc$>-I3Ps%z|hV$?K&?iNH@atN9eWuT=d|Zw1jQ+q%{=NHc^g+KL?b6uw!;?E7^81kvWn4cR%_8!HEBEp5UF{!I{l2w$3Huc$r}+K&2T$|wU}_(cAB_~}e(AY9B0qdI#=nE_{4VAjN?FLicOT467R$4^4);F`4-@&Z+(r1hVudF~e)RTM_c)2B+9E%4Bg+1+rAeZGof`am+Tla7oL2S6`S-MEMUfxRy^;Gl8FGmH$Vk2(Xg#`F?3Zx3G9QO)r;Ftby_}cp?5ZpBt);8^_pU<$ksteFI)9HnyDw3!@5pley_De#v7F(X5A*No-_1mRD0Lb4qh^&5`LRb!^6}PSl~|tW%|(12?Wd}I|2bzn_RkjM-$9&Tcz!6B!p8~DUpzlpbfGxE@cdY&CgS|X)bCT6eVkvI`fc~~af0&~&kr|>it`K4x5_jS=P#ZgpHzT-oL_i;<n3MDU&8r|sek@cK7Me1Vb*JR9dZ6*{B?Qw_`&&wS>IXP_;(HGFJ^u3@p-#<eqrW&rG_|vG5)EC`F9ZK7iN98ZRFzz=Pzb`gOm99!TE)mZ~7|Y{KeFNGaDa21G|a*V4F4Ezry*8@t+>g-%G(8`^9{Vmlx+R(Rfw%zuUy$Kbi5I1^nowy6g{~aLDgRDpck3-wppu@%zE^+xYvZST2zt%(#w^pN2g|e(cGb>~EZvD*Wdva6j$VPsx5id~YNF-n|wS`Jp*0`1|Lxfg(TNxC$SKSr>`*iVrN!zo(7<P7>=iWexv6ZY(46BeBJNT%8^v@`G=dXTR}Uv0hf@V*EWeGK0vEt>@>UtlKr@cK9EzXO*5P_Dgs|DfT~)iS-JV;p>Kx)44^y_4QYLzSg*r$hXo(`MBynJ5j7x;V1bxyqzkyL#qN@Cud=iANq3vA6KKElk3%>5Py%AJu8=g;vDz;$~qI~^X^wGaGfdT`1pCxI_USqgZFTMsljilen0-ka_%pc7?a}nt$iUrPHqkn`H}S{xj%LytH_Ujwu8TCh9`)8%leA@OYcoh_WQxBPjP>&<XEws(bGlwxXPYS<i{#(=HuaHHjy7Hynv6Z&Cw*Wz8R}=KPoa!EN84|ko#R-iiv#d`E}f{E}38CM;grG{!;c8Vmn7mRb+qbJh7bC#K*XwKev+HFN0Qcf2mt>xnA97;d=I#MB&Fub3ZD_O0k@w)sJwU-$EikGII%^-)*fT@?(EZ;eOZL#QkD9FBfCK*;Zc8+I+vns=7^_-+6wdel0$(j?X^i_oI;-{QLOK@f5!wY+I4@U;S11kxemNmk5YD)`ZP`9O8V_)JfSO&Idg|UV0UOzg>S<_?BIV&o>_$o9g#tU8?bMTVk>B<MS(XKF%LKKm2wXKK^G|qJHe`R{oycmQB<Ntz5_7lQ^F>b#AN{=bL7}yOwZ%{V~E16|KR?fA?u(`^WEA5a++fuU3xpaeiv{%dFy@e<Q1?AM3M$KQ9mEm;3kVO70KfeA(2=zFeHon*DNRA^XFo2tU%OGW+xA$>Sk^8SYnX-Yxx?OY-Lw=f7sYWsC6leDQpuzBPF@f6uolF89mrCH(ot`M9a`#UgROZ1zj~dHnr<EGp-FzAXE9R><R_PH}PmZv3G|*~j^{*)Odh=iiZG#e^SPw~W94=U0)(!`OxVJ%ICl<L{p@&d1Gi7XOTYUy82~e*9hu+!xv^kB4v(aect}bAtRmv-M$7C)htPFXyI8!jGI<#J^MD)RV`<(kOrb;Ch1DFWaZ{?^ow7`$c}CqU?`7Ah-W-1;lj*Gv8ExPT0H75S{cjKS!&6?>t}s-g&<Mz4Ltid*}K3_s;Y6@13cme(yYA|K6E8>i5p`_3xcoU-f%u)>r-BnL6tC&Mc?;y))~pe(%h3s^2?PNB!QJ<y60SW_i@_o$=N0ovEXK@62+l-#b%B{oa}7)W3IGkMr@M`sbdn`{$mo`{$mo`{%}2{d3RP{d421{<-Jt{<-Jt{<&E%)jv1B>YtnSQvGw|tNyuJFV#QyeBD1c>!teV##jAwv%ac-Zq`@z&&_;Q|J?Yhe{R-G_0Ns3`sZf8s()^lU-i$;@~i%N@cb%1uGIAe&)3%zJYQc=@O*te!PHmR6HI+|J;C$!^#sq?*AqNnUr+FSeLca{SJxBFda3IP##h%9%=)V931)rO^#n6tbv?oO>Ux4%Uv)jftgpJBVCJi?Cz$%`dV*Ombv?oO>Ux5iuezQP>GUOU2X+0^^Y!&l&)3&KJzrn{^n88&)ARN9PcvV2{nPXH^-s^&*FVkjsOz6*ebx0(GhcQ6)2y$${%Pu~>z`(Q)%8!azUum?sjseon)OxJKh658>z`)6>iVZyUv>S{tgpKMY38f0f13HK>z}5+y8dbEtLvY^i=S{EeZL0&efMkN-*>+T{(bjrygK@R4gCA=*TBE;evMa0->>oN==(MB@4H{)t*^dc<JH&qYrH!8evP-j`hJa9N8hjUmQ&xa@#^UNHJ-2U*LZdG{TgpM_5B*Jj=o>xEvLR;<JHmkYrHz@eoZ9zDBfS{{<7!m`^%oM?=PD=>i)9l>-)>5j=I0>`TG8{siW>Md%nKEZ0e}{%bu_AFPrsM_m|Cbs{6~Pj=H~We06`>)KT}B&2p;y%VxdQ{bl2;`^%<|y1#6Eb${8^QTLb4a;p2wX1&z?Ws|S&FPr_P?k|TQ7{<$^o`>;#{XC54>*rxSUq27y`TBVn&)3hxc)orf#`x-a7*k(8599gzc^I?4>UkLBtLI_N`l{z)jIW-DG0UT#hcUi-9>%PfdLG93>UkJbM?DW?mPb7gW7bPO4`Y1wJdCNMo`*5MdLG6)GZ6hN`MjCu>*vipUq5f=`TBV?&)3hJdA@$$%*<CkZ|3>>c{4L#^}LzMSI?W7`Kss5%zV}JX3-ycJhOhD)ARN7oSv_r=QMTH^PHZqpXc;^{XD1V>*qN=Uq8?3`TBWIQ%60|ndZyqInDa2=Q+*#s^>Y)da36*(|q|nr&(Y1Jg2Fzp64{{rJm<Z^X2oLX1&z&oN2y%p3}@%J<plu%jY@Gda36*O@6MX+^-mzU-*&hi9Bv4xWKJrRqDd~Q9WPn`S*QJ;otW;g@51Y6#jjmQ*XZda|-{y&#5<G{W*ny-{;huul}5R`TBF}%~yR+gVzsm|4WS@*S<G?-1GJLaqWBK$30(<ANPDce%$l*_;FKTjUV@XJ$~HOQRBxwUymO*>#N3(-{)iexS6jSKW_5X_;Hi3#*drjRO83Z`l|8crj8mvZtAG<<0fB?A2-`yjUV@XJ$~HetMTJzIo0@aQ%8*-H_M~OkDKkL#*dqPHGbUqYW%o4-qiSUvz%)DxLGeXe%vg-8b5A)HGbUGQRByruf~s?^;P4?weO7|H|wj$kDL9j#*Z6cjUPA1zZySo^40ipvpj12xY^EX{J2?PHGbU8SB)Pxz8XJn>Z|eNroI|KZt~UmaZ_K7A2-`mjUPApYW%o4e$@DJvpj12xY?d+{J1%O)cA3;{A&ETSxz;6+$^UWKW>&sjUP94)cA3;oND~ISspch-1utzxT&MYkDK*X<HwD!#*dr&YW#TG=Twd#H~DJ(xLF=Ge%u_-YW%p_ziRxrsiVe^o8?#I$IX6G<HyZ%s`2B-SL4S`eKmgE_-g#P@zwZov;1oOxY?d+{J6<i<Ht>XHGbUGQRBzWc2MKTO&v9U+#H{3{J7aZYW%p_k81q5sjtS5n|w8X+$_HuKW>&^jUPA5qsEV$I%@p5Sspch-1utzxbfBaaWh{ve%x#~HGbUGQRBx=9W{R3>~}SOJgr|R$B&!ssm70+`fB{R*`8|rxbfBaakE}({J8Pe_;FK5jUPA5qsEV$^;P4?&HAeG<EFkEKW^%)@#ChB8b5A)HGbTzml{8Ad^LXDY=1R=+#H8${J5E~8b5B<ON}2l^Ht-=O?@?f+|*Iy$4$N(Kc3cqljFyYuf~rXUyUC(z8XJnd^LXDERPyLZt~UmakJgj_;GXmsPW_GbEn3SoBgH6kEiu}<@j;qtMTKez8XKC*8i8|$4$N(KW_5X_;E8|HGbUqYW%pVuf~rXUyUC(z8XJnd^LXD%vX&cH=jE-e%!2=8b5C8tMTJ$zwdJVxbfBaaZ^W)A2-L38b5A)HGbS2hid$|Io{OxaZ^W+A0O10pC4E6ef50(-dF8=?|t=r{oYs4*YABb^HuMCHFeZ`Up-&H_toU9_r4lmz4z5Dzk2Vh$ye`vHS<;Pef50(-dE4p?|n6O)O%me_EGPBHNJZ9t65I<-dB^a-ur5{vwH8VSswM?SL3VqzIwiX@2lCK>b<XKzUsZNX8F~7U(NPZ?|n7Cdhe^5uX^vR$ye`vHTmkjuV%f}dtZ&O-ur6mtM|T|eD&T}b3CZ`zMAc$-ur6msQ11aU%mI$`0Bl{=6F!=eKqq{?|n7<MZNdc91rTfuV%f}dtc3VR_}c^b<}%bjj!JOYJBzHS5sfT_toU9_r99_rQZ8$>Ztd=n(d(8`)bx#z4z7RtM|T|?XTYZYPP?6@2lC5>b<WfU%mI$)K~9)HOr&k`)Yjk-dD37)O%k|ef8c~vpnj(uO?r;_tp67y{~4z>b<XKf2sGrn(d?B`)c-!dhe?_9@KkZO?~y=SCg;a`)cN^-ur6msQ12_eD&T}vz+R^uV%jLy|2bs?|n7<QN8!o>=*UkSCj95?`v!Ew)#6aKWmbsnq^VTXyvlHb@IKco=p1Z>3_ef{`JcLcdx3iP_^>^=d0>FBv{rbPHT@wJQ2DZJQ2JLnkB%z3!FK?S_hmNTpQXKTpQd6Iv?BzJP#TNlU@YxbJ`}S?MEZt0^W@2`@kEaW5651qoHlVqruNXi-4a47lLL47Xqh;o=IR%4?dm1x(Iw4ybwANyb#<U`ZTydxE{1LxE{C^v;nvjxIT0cxITCQ^egZH@R!iD;4i^nLo)@KzXm@TV0{AoAh<B}1#n^T^U$&2=fNL9w}7``KNA1wwDV58jz)X|{0*l62tEg$3qA+_9NG)~IrvTJQ{XqjHK6IhHNXkboe9hd;Oz;l6TsWS<DjpA$AQ~H3xeB$3qUh~3xFSl2Eh-4ABVmQejNNV^keYL;PKEHcszIqG(&)S2l#;iYc22t;F{3h;F{o`&?vYkcn<Ue_yYDL@gAqGbJ|`s;tk;Sn7#+R7CH*N7CZvl20Q}X3R)1{3S0mh02ct?OJF^jz)X$!ICKH{ICviPE$}>WA81{0A8>7GNpNj&31|ph0$c~$4_pV_7y1RbFL*xm6nH-P1k?^Np8)?04T7l=KMwC%@Z;dt(D%Wu!6Ts?z#Fh1iLW{BYp4ByMtl~02Gg&BPeW&ePlIPcUkA?ucZXI3cL!I2{*%C51$;Mwbu0KTcr)}v@MiEB=!@Vn;I`1mz-_^Kq3OYS!Res+!Rf&Hpf7>*fnR`r1bzWL7P<{Q7Q6*&1(>&h|AtlvQzNbl?+tKOa1ZEb;2z*lp=ZHou^)+dIc=5GcB2um0k6jNUEr0_;oz0vVbB)fVc=%a$H2|Nd7*zMFy{sTp1^t({5$wCbT0TX_;YA4@aNz+p-+L|1lNET2iE`>gVq8U1J{K12G<1lghs(V!E>O;z;nPypnrjnfbT%_2bk}G^95L2g7bl!LnGkk;P;?wz-zD{iLW~Cgwwu9BR&N_iRo9t$DuR8$HCK}UBT19ouQS$oxv5Lza=nN0N+Yr-3Yz~UJo4&UJo7xeGWVd+y?q6xD7Zr^Z{^guno-vw!x1;p9enzeir%x_*wA#&`sd?!5g4|fH#1Dg;owQ{|c@cVC@F32<`%%3GM=(4m|}vh5bmp(`m~B^js1*;uYZKn7$Ld6gmXF6#Oo<3HV)bBj}^xM&R7gUlN#egMUh3O$Gl1PJzw_r+{ZcUkA?ucZXI3cL!I2J_)V@E()y<E()#+eFIz-+ynX<xCi)C=ppc@;DgZH;Dg|s&^!U=o8U(RtWCj>fEz=Hf*XSeLsx)TU_TOn>$D?I`worx82Bire+xbgodP}#o&@a#o&@d)EeGxhE(5)hz+47=ErE3{_!@XMbOd-ccsR5bcsRHP^kHxd@I%l5_#totG#5AloD<p_oD<v<IuhIx9D%L_N5E^KKZDnRuS3fRn6HD&23TJMmj#ERQ^8^IWau&QG3-a;?N0m3X*<w}mw*>z`gZUl=-c2$;DOL*zyrZgLmvh|4SopvLjv<d;O`Pxlfd7B6QMJ}iQs9_uHb3l&d^HW&fp5rC%_fJMWB_zMZguI-M|&WU7$0;UBJ_!$>8bW1JEDA2f$aMxdO~r!8rr04Z%6V4WRFU8-NEvmw=aGKN4Sd+CisXK_fl{PQ~=g;1uXYa0++=v^{tN_!Vd=@GIaF&~Fo%OMovWu&xAO0xyRS11|>;fi?pV0XKnW2R8v{g<9aO;D0UF9AIk1+2Az?X9G8dz6Wj!9tvFr9tvIo{T{pmd<9xMz<dQ<GQipaToU{$^b_!_;E$n)z=yCOiMKlK3#V;EBmNS+5YxAU7eM=i7l7Y_)&su<t_#f$t_#iz{a*reR`7)c)_vd$;62bO;630;&`#h<;EvF8;Ev!j(8Ay{;6l*y;6mWC(AU6a!C~lBa2Pxpx*t3lycc>Iycc{Cnj^q`5u7c+S|6MZ9D)u2hrs=yUxL5Hek8u+v;(w#(TJ15Ntk{KoCqBUP6U4lZ3q4k{35g%_(gD0=r;+>MZxD1SeJs&ffqyH1uq7_4Q&K|8~hA3Gx!;BM(90@IV1QVi#1CE^FQEB39OC5nZOO9gTW2K??9J<-vKXy#=%R#=b^;|%;&*R23TJPKM8&bIv)HI_#<dCI2rrV^=+qLPPcoYt$lnOF=<P1OT^=BZkKKLh{q!){TBS8({5SJxA6BK-$YE>!pCE5j!FOL;|~#kh}y&-IPE8k`6txz{)XZkXw5K<c(lziX&g*C8udOvZSqDr?MF=i(MroDrT7|JQ%oZsVRKA+5llJ)^+usKc@d|5kLllAX}QE#5tBCd@o<}C(r<hmK^#GC;$gHeEaq=f$NL+Kub?%;G~%H)$E4@Mq(f0}7;2L@n6?$B|IbRxCBB51w4smRwK*m|=i|YM2ctIeJG8AV<~Ztjd;u|O10N5vIVL^h<986hgWALcX<aPlZ&1hMbBIZw_HlokW74mEJP`3f)F$rdw6hlTS=90P3}VvyK7PyQnDn%d`yuX!+QfZGE#}jx<NXcAr_e%}M%>%xnDiu=v^VPYL2dGSI_(6epRm$$iH{>Dt?T1AZH`G#__!zHo~TXyhSQE&%*Rm2<D-a4Yy0?hn`6>rK7Ir78>mg(-D!s{=EJDt{SC#3&}v~CaW|V|(xYI~Zm8ECwaM$^w1b#_&`QfCPC-oil#e^x9FrdLaTmm0P@DKQrzKm=$*AM;0mP&=d>pnpCOzci*ATyk+Qc24w%=mjk2)UjLrhxT$L(#7NmG5?0dWV^CVtgvdoAX@sN?+&#e2}IVjA%)HpiqXK7JMPtEioV*3N0WEN+yWf_Nul(kecF(dL*m*~je=w?kdx7o4`kV%~u|9&blXTFJ+4ZH`F~`1l3HFQ7K@b57f8F>gg3?{6sHj8+lTh}+m4lO}>m+o0Zas7+pLr)|RYO;%bi@kYd?<$c`B=9qM!k6R;djoQR5oVMO#UXMB+uSHB+&d1Gcj!F0WxCP=Cs7>6|X=^OzHK^n9YQ&^veB8w5m~^*~n<8$C+Qf~Vw$fr=i8>xHM@(88TpIB+Hn&|id(WWOF6eG>1E(#sn3v)2y}zM&30g@^Bd%|AOu7?HS|9Zqpf-6Sr+tO#Us-9nq!cegD~@Tzb#0DGxBEDRIE327wVk%mVqS<k9)E$Dv>3P;;#xMhZ8m$gP-`1>JGiFP=3C73@%P@}P#i@oifP2vZH`H|__!wGny5`&)oF7q<~gY2@#lz1i}<*T%`xdFA6G?O6}5>gI_*=7`BT*K{)XaNXoWD1xPr|w=>{-q1=OpE+T@jU+6+veVWs5~PeV*v(8pzLj!D<~xE$hgs7+kTX;UobDX8Q94aJkt3Sb&>37ccmHDJ;bs8<TL$t&ixiI_goO3NjlfSB|#9~ZSbCSB#@Vu*{OHgOTBjkB1?p^o=A6n}`87t@Ff*&LIu0FxF%y&|YhUOuOd#PpF?S}rNYL(y_z8gVY0W736S(p;#Q54Fk5<g|X6-p@+QCGLZmG?R}Xv^gf7>*GvbjM~KaoO8Tx7IQb$@&1P5&S>c{jrgws$E2Uy%%l|GL!%nx-Ep`hrgyZ`a)~=3CQa|-y8(_#XWMCf2k{-ucQ)GZPTaxbM!DYKP~0BP#x&yJ0vwahw3$gM{vC~KkayeRS1|n*D=n9}9b(dek8cGyCY@n3lTv&ejcSnhGo6QH`b$<?E-A$?pjntk{8NBq(rGp`DaAjdQ4R8LINTP~+gfS4#4jQyP4Mx}0LP@$?KHlD_y*=n{0m)Eu$W&)9gkl{O!|P2e+_U<I?GPuUl9L-`OHH5!->NdH_9cC_%+0&5Bm7e0LP@C*=hU-;y*AS;=dj4Vlj6?9gn*rCe7gEe*zqner~7n--!Rle2D*bxVy#N9d$hJftWO-kLf_l2%Y0&sx=4tIi@8z?RAU!b=2|xhT=ESGGiKXz~-1V3MLJpUIJ>9XFKgpOn=i#%O&oKm^6!zAFw$lo#$g4v5nfq>73TfV(x`H9`{B}n$^eYZH`Ij`#2rqbf`_7!D)Rh=Dw)o@mq*Vv-voq%`xc$A7?<E0kw%UJFUOP+#hv39)OrMyN|Qj9Fu<G<IIRNqc(9?rwz222cnMmHxv&-%ZX{k*=&wU7lBE$p<Y(hCNGE6-of;Dth8L>A&5yI_Os0~=~q6^fj9?h6F=g#_blf3P{-p4V$w%^oX6&vbg7RY@nX~_&hNDME#~)8$KwwWljia9<2J{n%fY0Nqh5a0Ca<8=#$fswD=n9l;?Zc2Vj6J)n`6>tVA2ApR}i(y%j>iem_EWv%OxI;m^7D<AGHxXy4c5g5$8p1;+#$!Y%vc;9gp8eO!|<Iv)de#e(B?!h;yR0JI!hDTFmdFj`ued4@1k1X)fCwlP&?fih2*B_7b$moHokhW^xgaMaze2#6g>5(v@J+AZk5^y5tph+DDlFk(HK9O7VEK{Fp}kgv~MOYB1>&s8<-Z$$QdiA7lE*R$4CcCx}TO_i=HXW74%?(&DK1Bx;ja(rJ@1eX^C7OFR`ZY0$@|ZH`ITgGo!HUP;s@udLIiWBPO}EtizynP`PEjkvtcG3iDyX?fHui`wK>a@uT6pKYb(l2ZH`+7p;YT-oNBbTgQ=GU`=AZStx)Z7!zIwbF8l=OHG2(#JJyj!C!rxEkVWs7?Ho(-v6F3sA@7FA<ZL@NpfRW6~WyehTqZs7+jtK5G{9V$|{ehT^4Yr7(^7X`5rx7?|{F)T@Wu<TZ5K3QS*NrR5T@LQGoL$Bk`{N%#1;A>xLpP2AjR>n!GVsN?+&#T(EnU>b2tn`6@bVA7VT*BrI?qdn`iEfzN~mv|du(#k%5-sYGz$;Zzkein6!U!rxfm}98p@ovPV)qMQ2%`xdgAHRh7CDbPF=(I$OIT3X{PC`st)5o1`j!6&uxFh0@s7>6}X{i=-D(ZNA1TkqHANR01COz)su86y$HgPYfowS%wqK@}B6n~9Y57UVI+8mRf0+aSdy<VtI-T<ea$Mo}7S}yTL#H7#o_-&hG(z8AufOr6E6Ay9PWsCVT>UjJeV$vo)e$VEZ^n#CvARdC+#3P;dgT?#<>Ue)c@pZK3m`41*%`xdEACE*l616X(jdj}37B|Yhg!mW4q^*4Xk<Bsb6(5g9JQj6{Cphgli}^Ry@%VSdq-}isvCT2*cRrqgcmiq@PjuQHi}?=fc>D)q(r11AiOn(TRWRu%s5cR{$(!V~yO@60O3Nkw6EW#?KAvoIO!~c#Cn27M+Qd_w_Ls%{7wUL_L-F5e&tn?#RGVYcYv9(+5(2sGw83=g&j#P<+rjxvbl~$I?_b0{Q6JQ`-+<RKx=#P49ERur%N0&7GbpchvvhPl#0oh7>7?f_T^Y3g4?Z<M5C'

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
