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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_009.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_009.stl', 'source_sha256': '5f17ab692d1ca238b725d516408aa2a89b66c8c81d2e1caa31a12f896656e271', 'input_faces': 1104, 'input_vertices': 642, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18954920768737793, -0.10740624368190765, 0.06135391443967819], [0.18805286288261414, 0.3738871216773987, 0.32497984170913696]]}
GEOMETRY_BASE85 = 'c$}r32Xqz1`}g-oKtQB}pa`K?DT?%RsfMN$X-WwtbPT<hivl7=1VlguV?;m+QUs(3T<HiTp(7#$P*mgx0zV5y{NHDu&n9;#|M#5tyf5cGen0!oWOnY%>^!@BC&$(;9?6i`(SJpqMvXr1x~`7nNMv*JI-_ESjp*MiW_ZQdhK%(&IgKy>TwU;D`&O+x`<zkE_|m;&hW8p)x>jWAI(=%Ct`J$ePwcP}!+N~dJ$6{{81b9-7&JU4<PY!HV@OQsxJ<RG&sK<hu55+KiIM-0|FTLON;NvTD<r|YleQauWm&L(nD5VA)%ec!2Rp<4xct9vGkSCLH{pITCYSM}{h4-z`;p_OZ#C*)x;xwt_?vGr`rR9z^9J`eHhysQr`tW{JC`+n-2Dho`M717w4NM3Z+qsg{K{ytlDoqF==gcY_rFwSkEi^={>G2&(9cs(Aj5Z?MN^)d?&$|-(G24|wLbHdcRt8t{J3{>c-kMg_`)Xh^KlJ5^+bO^-S~kuTRrup>>6hLxKH9e?R0)PztOa}YK*6zK<sSe2hK0@)Z@?m;7j8_xau9pV<(IsIsFw+JN=h;7~g5s%-f#k%Z(p*`=O^j(Y~(6PkC#Tx1XP^WBlORv!3w^bT6po?{)Ofw?Os{rvA?xe(jk*&AYBM<^AjSddffMH-7X^zh}Prhn87u{5wB*%SU(r!qk&k&Qm@Z@#GqFo=Zo)?Wxf#!T78E`#k-hv~;!k97#32^X<=7pPBZbUF9k7zx=ZCgYkQ}dHQEV!&RpI@n1aUgG+C$H0@k<-O~?oV<&!U{KbvE*U|a~@#g2h-QVx2XH(XXj352p0Z;kk3zwSDRVTN1{+Fu0#Q5VYd3^uvZHx50Q3pN!P-x?P^Yd=cc+Tq&R5pHGAi?{&-u-l*`T4t_d&)bxi@jsco4<~?pI5y**ObqH)_dOhJ>E9$IhV`xxtx;iW}AAp{pg)<oi4m(&OiUUXFfRpdF4&x?`-R>=Wf>5P5s||>n-mqI>pq#th1;8oyhkmnRY(g%UjR33geB={m0vW|Lt+69_N&|p4+uY8o%EvPy3x3_lBGLi=6kiXYbX)=JWMv;63lUFFTrg9(mf^pV2S-&F4CB+uQ%qovX@m+%sLh>x`4Vweg!x_0|)7p_3d3y1wqM=bd8R<v4oj2Jh#sF+SSVGuh`YU&A-S92fk>d)`-@y>5<Q@_FmIl<6%~Pya-3KMd|ROO7M&X7u*M{Y`UBJ0D)v_OC2^z>K$@@9@**JN$I{&aKDJclhb@9e%oe=hkEAJGZ=@@7(s-`OdA!&Ug6f@||1W&Ufy4?R<xyF5kJno$uUs+WF3HkDc%E)8#w2emmc}?X>e<>Nr~Y&TWsK@7(fszH{4S=R3FkcD{3cJKwqOwDX;NUOV5p^T*D2Zh1T3xxSt6T;I-j?zr3e&Mj}}JGcMseCO6<=eyMYwDO(XKX$%z>#_5lJ6?9abNkcIcWym)zH`gl`OYnG=R3FkcD{4_!OnN7<7nkOw|+a{x%Jrj&h_nl=lXWObA3DCxu4h0cW!w*-?_e>?_A%`cdl>eJJ+}Ko$K5A&h_nl=lXWObA3DCxxSt6T;I-jslJu(T;I-ju5af%*SGUsYWuBxm+D*j&h_nl=lXWObA3DCxxSU}0&{n3{@B|t$<%Wu{($<ejPHEi|Ck*6Z>>0F>MNVW_$hm5A2sEdZ~ivi5A>XqY|8JPW7-qk{h`Spfm1WoU%viGxF5XV?6~pkeQ5e2x=UY^C!)(QGWAF9ob|1ie_+=A$iL4VHpep)j)wbAY(LXZ=d7;tk!9~`{>XRKoHuS}k~weO+__rMzG(A#Q-&-{3iqAZVkh*x>rDUq%QiNCaK;a&ozAUxhqawIOkVNd9H#!x?@T)bUE+-IOvqvU=#GUFJ^szlPiXsR9aMji@#8N1!RP9BRL|RrdRA)xFaN;!&Yzi#pOWjLX?L*hk|g!NF?k|zxtS>+>=u(8?gwWKIce${dcll)aPCsgE2|sn__cj5Iox+{Rx#}lPS~z_;m_g5_gA`N$_2(ms&=Vs{OG@roAw2^ls*>j``iC&K5t;?Lv#J6?5?)nw7=UZJ@3%F`Z?xiHNHQ-f%gBcgNL;r?wEWQh<XRV_!0HLGk#q8DW-q@)ADIQm7Qe#VC}c*|7wZhejxK7Cv-l%dPv*TXI=RC#_f1J(c@=sWcn>|<||X)e|@0IqfVU#=JTg4i#z7=E0sQ_*F_(_ey3kF`880il9n&rS^KBRS0=wY4=$PG$Z1XV=hNn_(Rro)@8llp@dHsePinvQHrHwN_3{bYpI3A~jfpuH?gzJDHuVIq+}@(?nP&2I<or>lAEW<ne>~g|R$OfAkG|5#jC-){{?D}j5_<j5kJS0qwj6%dqx!k3>2<udx5?km*A2BCpEsqg-}r&{3z(m8czplmIi}x&XX=~z8CRtGN}X3fCu#p|Iv(yj`3`75m#C-L`}AEa^tvdj*Ym)EI)95i{)s8SwwjJ()+;)HwkDeUgW&!1IzO|H*LA5#-FR*P2IHsvz9uo;4@7M@^*BQd>N>FX;m10!I-BzTj*Sw-{a{qIDW9@qgPHG6yLwta{wrM%n>44LMU0<PK4`|(pRtF>cj{!;c{Xi?*Izr_oY!go=%#Q#(7wQF(+_95?NNVeoaxUd9ZkC<o4j};+;`_~<hq_)O?@ktf28$1cS7fht`Dy7tgWTxhjusfB3S>~kM#4N<2t&R<nc3K)b(fi12a$KvW;G5+OsdGIri_<_0s>{n@e?G>2)5xMb~5hcjMnT*L$~1Iv(8?d;GxmX6Ezyo82(?^ZpgVC0b8mQ{HLYQrC~+N6mekf9(!)zQ}zKlf(T$`*o-EdOxIjb9juFzZs+Ln|46QZFs?XIxc$M`lsd8_6+~Y+_yOs-ZOsmn3^6xxP7K+XJGjWGj9V|$IUe5A9T=hy|C_BxF5*;gqH8v+vLaK<df#UEpYi?y?)w^(ei;pdVjY1SG}K@|I~?a-@ovpj^o59H<)?~t_X-9nfrCkuNN|%4EF;E=b3&;X%^UQ>T_z2Hs$Ac(mZwHxX!yJvj&IvbFf>3li_}__G;7q$SW=NzCA<R{$?CkchUUa?T*$HEL+{Qb3%mnL*Yip!~MXFfjYh=8t8qO-(T4HJy+}J|1FD_uUxc`_WLE)flsvl2ZQ^nHqboR?TE(@*1l-!PdT$j?=vfZJjk4H;b~oOm;Y<#qf_PH2va_DYn{&>kL&y@_)kE~cQXAJeWtGIC#PkZsak$2d1SNJ)6#j<l#kCvJ-TiLe(FEd{5<xou0I#5>vgwb`fO9~@-6M(TQyDnfyo~jKag*)_QUG6$HRT+=4a+}IXnC4{o#fi>OUBy^XJ$|Eq^;|zR`uNS;yi{{{=d=Q-5DCoqx;TJ`wIamy2rqo4>fu9M4{1{K(vnnOFY5N1qJ$o!ArFKUcPIG(Rs{V}bVnH>Y%bPnh*2P%_&>y*^hkPd+;t?gzj4S;y;gf_Z-Q-|n(VKW}rc-;6r1ORh7%n>PblW3;|m#TJ|LYv<|smbk0y|Evzik1Ib$^Ul71_`Cy+A8h})Ue{Yno%Hy%^PDm5Xm)#-_UF6C4;);npMQBb9p6rmE-`wlx%S(c8+yODtJ(X;kAGdS(=A7IT`Bpp@%^W&>gSp{Li5+I^;$ma6z$KU{_V3LYCreoytQ>4OIBE_em3Uwer-?5X!Q^E)cc~}Uef!zl9iX~yjp7JN!+sA$HV>Ljb!pmiry!8dP&R2H`Vfmx9D};<k2{z+Xr!7Y|#6<gz|AZpC8k_pS87KFW1@`KV@g48NZZ_nf8VIL4T62Q{5Km{cvEi@tt<%biMLv{!jJSeW3ohPrUxLRXX2h4Di$wc>kc@SIq9{DIZ+>i?;Kd$34FPi+{DA**g+F^{>os`X~5U-egZbTXGmbdO;6w`DD%4foWfQ&wHt$uAg~sc-widjFz|CdA7b@7yUAO+j*n=>HoEz-_6$YONV;=;Or;Oe0COo;c0)si86j%skc17GpFwvowvO_zJJyv%GdGsL*cnv|HqGe{TG&~zk8+5+dsZHest}z`n>Sv`};h8!xDNQ)@kV8aNn7{T<3qbGKt}SaMC@U|LY&>^^%b9V^i*?qy1dsPrZ+J<`~~UDTDS;RLP`pKk#i%T~{kV=kfhJHD9OvqW3AO<+GMhKk26S^Xe6P-i<TPXnTewhx`8jexUs@vyH9;<&SFldbjjCTGTfw+z-tBNBv17J-+j>oX(T?KS~VugUzd}KSl3vow=8_{68bjd4v1sCx`p~)nBOpTV-v}#cT9iP1B!ob<b%()O?`+Yaf~RINx9O_`xS{>h*ZLXmYskf32qWPh*}VQ_H`l*HPVyiJtmf6gKTiIhyRPr^ObXZ+B*CKU~ZZZ+_1GkF&g|$M;_j==I*Qncl|+S{XmM_@cIR_VT1~-~ZEZ>JQ)G@dKaK(fRXf&%|)w`8`Vg*+bM{6>a>K&Xsk2%T#c`$1gtE%;&faclLz)PWFI4M|5A|smDLOu#S7zfX?S1dusbT_SWmM!TMy6-#V!CYG`ilxAMME%<&V+nqQvyJ}KM}ocmtu&w0(``@d+Z>&cT962txA&`!F(`D*EWo10(#Q!ndy{c|`u+z%X2()r*2ruOHL&9ptGb=~$C(DlLfgKe}uasO2D`2OmxG#@>^{-~#Xk2%_&U+#H)CxfnUaW{YU)Z^qmqIvwnKwUqFU)OrJ?AG}_GedH?@6VW|?V0$P#}B;GS?BZ9508fXPI8R4Gymf{j!}2DJnO1|_~qnqKe+O|`tR(~{uvXo+?1d3w&tUmb@V<kcW&c5YoF2a>Udu7f40puzQ5O8eO|ky?`>Q^b=>zi@%ZjIrp$WlXt*CJxkTIF;e^NcAIh%%x#b^EJ%KZ4bls@cNUyuXaeCfSt93q<pO@_Mj~>wZd9S<n=cbj$kKXgIxjy6O4c_nZw=LD{W!Oi1!hL6t-v7j1yO$X52WwT={yAJh@AvN9RlmSi9ml8hC5QX|n0?xBxe9swVDVns4}YFN8tywoVs*Xx;hOqWB0e?!5M59EA=91YaNpVWlYZX*dcW;YsBe6K{Hr{7=hWx^i}UgI{g{8B=3jru&$NDLq4xidEgs)#x=z=DvkScbQl00~m3n#WIebCebE}57Gv=)N?~m8{Hlm8h4<;Sf>vU*$ufL^>=9g+6j(Y03k)Z2ggD<_lb6@?I*^h<$&U@eM`tVmyo&SZ4t}uS}FLfM~iX?~ofqOgkI^9#s>u2n*`Fg>Dqv3wA%}DiUpQb$})t^*D$Ey<a89z|=y7pVfIl4ZKt*3sml6qe;Etk&QghpD=!EZJ1l=xi7w@CYyMr-}1>v@Iy9zXbA7tJrP)=v)i19{f#{LE0?<2%tiwEzDu>+#)n$zODe#}AhJg?#bO5l{WBSN_wvk9z7atIyrhWxnzF{*j|~d~+mu%ilh%>&CD}9zQtzd#&fWLdQJif2^kSEynTqfnR6oeBOM(`+4VV)Nz^mp7-<qn5^qb+Zb=ZMW5C6bJ~$akKg%c^<%Am+xs7_|NZGY-!^tMeq56qy8djLxj)>Gtg%+#hqRrtC){^3bl3GKR{>8w{)zQ<99L)8_W%h!j2}I}I?vaePK5iB7xj5KrOmRF;eK5CiQ2zoj(Gf(T<!IHjW&h6{=C2RdA3Otj~|Gysn^?u#N!@6-#hvo*DZ^uJ^uI_`uugE|5{J^8NcdvH?i2paNk)wnfG0t_k{bw8$aN0^!WZ$x(>umh}`D!50=pJ%0I?DU;7g#uhR1RT<qN1tM3~wPF<zvUC8@{lA0fjytV3oyRKb7-F4k}j@DzXGp=v1GpW9{&bWTMb*9K^EpM-@`03VF*SFVIw;p?4b$xqX#kbd0f5nWSX?ZJ;;HS$Yu5afNw;n5xIAbdt-@kA+_uIt|sXs~Ux%s%ZbNNAi{(2-q>#_2t>)UxVIB%oz)8%peba~t@Z|8A*JC8fZ9{JpSPWwK@_3ir*{B-vr`1XB>zi)OeZ{HWWzI|VGxVZ7{`#RUR@9SLOzOQqA`@Sx<e(Sz2wY+s-7s#EU=e>DM-y`jquh&uCO<LZ%zjb~4{?<v@u6|Sn?YHt7wI6ctR^Pf0cYXUl-1Y7IaMw?FAKp27wejue4*Yb_9r)><JKXa2bB9~M{oLXD_H)Odi?kl=xykj@JvZh4Y_(_Hd5&{^`#H|_?dLexPxl=6L-PdF4(qu!)wiBoUEh9gb^UbDtsl2Ae!AyY*SDWrGxSj3dQNwJ`#Ih9?dNpYx1ZCUj9;j4y~l8U`#py1+wU>b%6s2qq}Fe}$4ITmdXEukvQ_=He2>*+6zl3v{al$NwVgw=>HWys16sfJKF9U#_c_kkv+DCc#JQ#8>3`*t)?>eS!cX_!$t`cccfz;dI|a@?y2g~Z-h;V*y7yqyimGqDmveply<BQ}>%ClRdHcOw!W#AC`{{kp{JYwocan^s?meXI+wURq)4hkpx8FksGFJM+l(XJrr~1}=>{Q=+kL~*Qdu-RY-($PJ{T@5De(ODUYCYC_?9}qsd+gNm)_d&Kc3SVTQ_EZLu~XY=y~j>Huk{`~wI1s|cItVp_t>fRSnsh@&uhKMPOaa1kDcmU@3EZ^I~qUT_Zs-=zSl@tr0vXihkW`pdG>4k7x_NxU0u&tf3Q~Pt@Zs2zO!~1-`7mrqxG!N^7i*T`1bcZky#!!-|qzu4$yg(^*y~0iY;&a;P$ra&&;OpRpO7Re}9_ids5eTZeHd7yp4X}7h7k&(ad@Hp6geAK04jh`1bd1slN5Sn?K8N<NGgvtLH6oMfazidQ;0sy`k%8#sa!8EWWV$KHUDE(e>@`8J#Tij2~#fO4o<nv$USrO<Irjy{GHj-+MZzk7zyC_o}X+?t9hKd%iSkeQ)dff%Yx=p7$}c{zTVFRNwku*!Au2g@dPZ>G!e4<}r?}b6Fa0((~rj`8i~@K3`_eZT1BOW)#%*q;3J-Ul%`NvyS_G&HKOW{j<N$3f)IwegE$I_V@2`r^b9`es1jtaD96}Kp?h-+23UELvVe2A3`8@)K(oY@BRnZxA#8;;^U2<Zhr;7y}!cAvR>zlwXehV?R_0imJf8lxwUV^_3eEl{@Au=f0n(E#r5rdEWykVjc@OtaeaILj8i8{zsI)s|KQvEf1En&jBoERa{YAsi|X7mzP;bc_3iymslK(}$@T61PX1%{bRUPckIVJ#eO&%y!?e7$Pb_8Wq;K@|d-tKazP%4E<yuhp_1OE|@YC&ct3KcCceeNAxxT$0&pEbzx6X6#em~c@_xr_N)BWuBenQtzx1Vt8OnrW}_BW>b*8axm>ObmxFKho~s&DO|3=Sx#_ea)#&d8}rx^7wfNL@eOKGLQC8sFZ(>iYKn)ySzib)B&G$GX0~Kh~dtec9GN-c;Y($D6XW&HnIyaQ6v2%f{^2>(jg6*!AuG#&OryXnAX&v+LXYoTIBx*8SSn{%Y5^_g4o8Y%#vQf7|ub?cZK{M)$#4`@n-w=hl6E;rqs0d;Z$_^Tv(-_E!!4N+_~8d7VBz!v54*O!?>P|Nf`W{j2_8{i$=6DwV7L|NX6V)-^uIDHGv1d(b+tXn9ydcs=^Srz|0S1}zz(d<MRcJ_n1|hDA%m62hOMD}BnMS>ey%CkWx&j_M6ZSwi>+^f&ki_#FBjEE<H*!QY@?z~8{@(dF=Zcm?`CEV>k40e^~q41Wr5K-a<>;3I_aA@oaF^eB7?{u@0Di{6Jtv-p(%hO_%rbHUl+g6N~LXfwDV+!x&g?_nPFC4}doXW%*Tc=SGepK%?JJ^_!1A3CZst`7;}OXv^qCHMe(4nD{D9Uz3apzGl+@M?4gyn=CBO$cvAH^5urGw2cc415<o1Rr7y?xND~cR3c$!&nrA^T1JPU$`%Q8bt`_MaRSA>A$=j3*Vv-FTuCqMDzfBfPP6Ngm<H>;njTp-Gp!odInB`|3&Y@qVn1PMWf&-+WIf$gs-B~)~mER5l-aXSJ4!>UuX>(6pF5daCh`IxI5g95FQ+g5uxZGic#obcoaMueGMKBk3<K-BjMp_KX^Di0PP76fTKh4LMYmW;w3`(6*L--ru-{}a2rCnJ=zcMM_;rjgd3vW;b+lGgm442JKUZAYCs5gKnKHv>AMbua9cvS7diqK9SHY=yAZ-XLUA%QuIEE>4gC*%4SvL@n#rduA)J7&g%jW!5vtEeC`$-8N2B28a3}O-xDy<M_JCvHA?QGO2s{=Y0gr_zqNCu6Z~z?*2jB_lNO%G~1|1HMfn(7Da4g&#jfQ)}9np4hN4OdK0^AI)j#h=M!=Hxw_}9?5M1(XWA-n?p6c&~8D>xReOb9nZUw}nlf*Zk22;o-fE3jxAxE1V2+ry#_VfT9Q6T;7+mEdRK3TOkk0$d;M0E@PT>%%Xiy<pKU@QZL$Lbx^B0~UQ5ZVfj^qu|DH74&(y3cQZ%K(2>%gm5-A6PykHFV~q|Z~rBPub}7QEAVkbct3g)7TpE!hrc3(*M#E3P<#}M&(SsT=kN}67rX;LhMt6v!M~u_;9p>$PgT|qA0fONO@LR!wIWny?Wjcvw?v!6E#X(uPVlR6Uo-~p3lBqwz{BA2=va6>JQ<w`Pll(U0eA{L37r5>g2$m_;BoL!G!`BT_d$EZec;Y$N4PWG0&NDjfNP@F;hOMrpQ@}8%L!ozjes5aXVx28cYY>>lS1(|dIJ3wJ^^1xWu3atvG8Mr@G5i#EGp~NDvpKA62f)SMzClTxGr1`Z3T<^VbN#cYH%sE0$d9I*QZ(^mJqIp_aZFX6s`!@LtDe5jp2H5IkXB~4*tTYDr?6Vgm8W|8=N2h$5EBF;~zr!ck~MUJNy%R9R3NuNC@vm_rv>HNA?oJ+X>-S=o)wp>&q%a_!B~S3Hl){x(HqZFGSyk7s89t_u$3wGV}v@8JvKA1}DHf(XZjJnY%j);qTGw@b~Z?ROay=j)n6P!k?q7U{RUJpK~mnmAPFPuFJg4ik5=2!smRdG8fMg!W&STe;YU!-iy|Q>oL!S%Q4sX62eu{{BVBeS5=OMGoZi2zcYt~C4~RNy9oaUpGNn>dznM03E{(p@FsK>yox!ri4a~#2*;sI;3dqPI6^ocT@1&=E74`}N_aDx0B?r(p*!K7%#VG9@MZK4d>MX#%3OKCvG6$N&*!kHjQu$D9R4`Qem1%Ro(=aw_riM_zdnR;0W<?#0M3cZnB_z><4XuXP6+?O&!yZSjP+^wG-LS(A$$<s1aD&e4iduO62cqNI5>_m+eip+Ls!Dv;63POcn_S6?t}L+HpztWP4oeL6VAby$r$8dEM~(w;09<PxDWl?fDq1&=7e+7r@0B?KOI%+yFcl}gYZH6=ublU6uJ@KNMD>HgfF0b;0y4NXfmA4XZ{hD&-Nq7!uQYya0A*coSU}aqiv_)Q=IP}_1xoF-ciW=hLlh|9s1o@LeUVF<9>v2fDoRG7J}!(Z-=5}C<=$7I3Zk=5ROC(!I5wgq7Zc#2wiviLy-&33ybD~bHO>#+;9#!XDHqc)iod#ultm{aNLFC#>Bg{U339l5|;Kp6{@RHD4ryQ3!=r~g76b)QTPcs9~udZ7J)?z!};K+Lvh8YdN-t}d}*HW4vs|^!xF-7J;Hwy!YPFCadbX>9Nrd+GNC9Pin3@axGY==Edf`8E272Vitsapa0NoRJRw{z6iY)fI26-RIqpsfzd$VIoT7_h(Klexfv{-Tuy%G0`z*puLUEe9c820d_%wWvV^JB`r5p<{;=ICN`!s}4`ZR<uqlI7z;lKIJ-9ph69>nn=j;9jk7^`yh)nc>}Ecz-e+8^%En7ZRE$5TRa(WlqPAMi1bMYqDDb72W#_xci+>wSADPWbe?5xoS9{soH`;97hamg{N(EZ1@7P(*|x3nBanddH{y2>f54>aXyB;cMs*@HO}XdI-J%e~W$ve+zFx7s6ZM_s|*ed+=N6DEKXSG};p$4fjGjz`fv(XiK;w+zPD=w}R`T)!}+@4fJ`q23!rT4OfHfpv~bra0~QhxCPuEjfUI9J<t(w4|pUx9Uck4iM|8B3C|;hH=~<i(F5>i_#pZ{d=Ng5{tTaoe?f1-zreRqCqnr)?2Ay%1pDAe(admW=C1H2+C3MY?n}#+!U1%IFD<tU_d}z7Y57<96+*Zn`ZC-Qej05KKMfZ_Yx~mjtZ*dyye};m3l~MJ`_gi^aB;M*FD<_dmqc5_q8)r`IaJuqv%+1_o^Tg<06GdD0KbmTfM18-MHl+g))wLI=vT1lA$U7{0{sC#0bfFYg)hN>p?BcFU|GKkurB3CBe-YD&-#@Y%?#&-^PrjFOw6-9gu{JIZa60@bJSgvg=GyF{TcoPzKDJgUxbgL2jFAyR&*0AIv18}O|GkLgz$0nyf5wkLD;>=5dIVW#g}#;A}seNqPJmDU)cSRkNYMc*OPl6^(gmQk8-WK_gz`IFUvxnaPQNEpF$;1JjJnaA@mw7A^bPq1^93HGWxAAEsqPIM7Q|T^1krb=zG4jdjnzjo<aBx^ey-ecpy3&9td|ud%<1dCTK^v30xL!1&h}6rQQDsmqBa5W#H0iHMlff3atZ|f=i$+;1X~#Lbwsy9v1BZH-cY9N5Zed{n0n!{_qrZ9y|q}k8XxVx52N4VnQe;qVK~K;SbPV@CR@ZO@c*};UN4CA-p>j8`1rQ@OOmpRWupC3ja<BKO}@RMyMvi62ciGG=%>lgm0p|;G6JIgz#BHcpv&cybu185MDwE&qOD{GvP6WaBo7m6Z#t532sXW*C&K)hN4|4{Go_NYr(bnc`W)G91BlEC&CjM%SnXrhiDKEGJYQt!pqRzusg2H(2rozS@1G=EFnCY5T1s91W$vPq8oi_&l<uz(f#mF_%!+*d>a0d5Wa_Ah3~=gTq62AEcy_Z5SC}wqHrWCb1ss(mjRB1ix9$vQJIT{ITn5zz3EGPZWX?Z_Y*977QPE#LHEH|;8W<A@F{o)x&+<<FD8ViqBDJI&s@TT&@u2JxEtCV?glqSJHbuia%fvvv_4!8E|1pqr9Br5S3qm|(w?1#pF#b;wC8K#ifB7u+B3MY`}`~HK1U08CWI%Wv9RbQSoA|!bQvr<7M={ppo3x2?r?X`9fNj;C!=!wWGE_!;weJ-S@cEtS-3Si1a1uvBZTA8I5-|YiXMiK!vEpC&(W4A;VNhwxC;CdIvjop9*TYf4~0J_gpZ(!@DcbrdIP==XNyqH9-%BDTpTR{7l$81ABP`<fAguzXZ?-Od>HO4?*v29A1wk82}P+;3_v5{+M$>hiW2B+aDRUHHM9ggF%-{H-*eP81b-x+Xn9!9Q;c&BfCmx6L($T3d49hfIszWS&&#2uVQGJL+AcZ;t`!P@D5es^GYR3jXcKrYJP&;V7HtO4gBK9O^U)}HKKu^a6c%j+zXQ)9gx^4G!lG5+H{kJT1$aC>3M~tdf`=2r!_YGDFgO-13CF^N(c<u6cpzF79tihC3&Z{3K4>9W^a;2R+yl)8_kdqTv%;^!FQXaYm*E%D2>3;~CF;N};pT+=Yk~S;(MRAGa4R$u+zM`uW`|qDogBRe<(hm7je(zn^P%10?)+XpG&`I-6gfiCg%IwHW`jG!9ndUr2e=&}+y;FVZUeuBW`tjY+oG9a(Z}GnaC<_yBl<Yp5q<^D3BLk&Mf1R2;b=5J91ZtE3&OqN-sqEXZ@4FYD1Da~?FQ$C3!pvWp8T%xj8M!9MLj~e0bGZl&w!_+)!^xHfDoR9R)r_Q<Iu{mXhnD&JO+IR9s`digvX+lV9{scvG4>!cryAtELsDe48M-ng<pr?MC-$E!fz46v(bjIXk&Ob{5IMEZa_Z^%epS>`&6_RT#-I1&$vg1jhSc>G!hmq1s8!!5W=<5=iu6Kb+kNOp7T~mtHRacT4*)67VJmsz@qhFKiq^6egSO&zW_Hw8^ew1(`JNl6j~pSf}5gs;ihmSv<BP=u1N@2L7#_3pM|Ty70^m>1-LBw3|tm2LkO2dE5a4&>ym_UakLy<94?BMhDD3PMd8APa3M4j7A**i=7$TxPoQ~V(VXxTa4z(5I2W81eGJYDXFxN<8Q=&sBOC#{|Ac+$qp)ZeCv{7j;YZMH@FQ?0GzXjs&W`4Wv%_u<$_uw{;fu)o$p7howV3u#-j6$;|M8;zo8CWL3jfU;p}JE4h^cjpjMBzXM?{z#!2a?d=YIg~dQl_'

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
