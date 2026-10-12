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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_004.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_004.stl', 'source_sha256': '00b71965c137639ddf89c696429b0ce1de27ce65a211a21d2ac3b5d7c66c229e', 'input_faces': 718, 'input_vertices': 436, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10940626263618469, -0.15469889342784882, 0.15001311898231506], [-0.04468422755599022, -0.05158695578575134, 0.382790744304657]]}
GEOMETRY_BASE85 = 'c$}r233N@@`~FX2s(Fe^4RIBXF=kRR99p4bh&jgI5Q6xMxd?G$tg%!KX@YBrnM5Knb5M#PL5Z=h8mg*Q^UN=MKhL?&$@>1+`mf(FYrX6F<mvYAecnCXbI#3bU_g$X9twWSE7w135@)ZXC?X0d9?IAOBS#PJKVX#4u;Js~lp@j>KZY)9-?d#}4>x7365$;(U{wE+-i>VDjR*RASGRc&3?DgqWbm+W!$*b;5Wau#&`|@j{858~hY!g5y>h*}4XWGfR;g~AWcy$K<jWd@R=|DVK{1v=>yHSvY4=Yx%Tm4KhrROmHhZLR@7wo`@SWwROJDggUHVS1=d!&$a5CE8Tqb=-W(V0`D>g{_dU8kUtC{!Hgl`+zO#05nA<|cFYw0r2tTNKK_uFa7Z#!2Ue)ZF6KQTb&S0;YgBmJ{Y;om4J+bd1)N#9X5xAgUV%VfXGz4Ovng4&_|wa&6%$Gb(+w;dX0$)ozrN1i#a4@<w`1(`?d7$$vfZ=@xU{dhU#c~}kOKXDrU?sdmFePd)EwR!#w*>A?--Ll=H<<i%lT)}u6FO|L?l^eciHJL|^Z7+RQJ!WZd_(pq&dl>qS%-kjW^{);;(=L78`-t?Nlbaoq;~nZQeaE%=(${7VmA<wz560PKs`PC~{H3pUYa!b^KZHqN-8uvQtCOh1;2daQeGu~OY#`g)t3B8$+kLu0`u4`>aJ?heNnf9nUzhFMm%#NF8Y6xC_Da%s_;y9V9UrI4x@R_nAM*|J&pQRbRvziAkCw~)TH;3OtIVU8>jl5)3h8T|=I%#78Cah=qtM>%vGnz~IZv5=CG?G4kB->#CuE(2f{>@qC^^sSs-n_&I6A<eS`hxhy|SK4spitx>&MA?QvyD~kEoCQLGxsL=hJ(~<v17BLHjWQxZZyK<oKOOs$-lN3dntI@3cma)A1iq^qVhA`i_yOv7T2HL;m(LSVvb9WxuvR@*@Arcl#}ME145{JS(C7&;QEy&YEuUM~s!eE%S{Wr>*t-6xps<s`RxO-!o=k%lJ&L3w`U7bW8gKQ{+4=Eo07_edXaqte5rmGR(g2T?)Qmyv5goJm8-yEA!~%Uc$F8mUVC{FVoGw`p+}$<Hv(=T??L}-(w{Y$p60kU7E!|aTW98;g0pN@iF|Hm*AJFY4O#+*J59ueT{v0`2og15bH;);FV$a)m*Dlx69s`uY7-C{Nrk1{qP(%d}Ur7_OVY&y2WpkU;2uD{#moH|LBhMU~aPvOZ%xCu>Y=Yu=rZ?YUyiLOUXRWPQPKC3G*<{Vi&PKZ=ZtSd=SoqdWFu(_HR!h|B);E&FfZgc?kLEmcYFHGvbulS0{GExmd9`>M(y7+Gl<v+v_Pu(#^gyd^XPYp*=IqzUu!w#?$Ey#(y9QbqE_H^Qb|2Wq$497POBGhi`9S@wKLFF<(3n?Y?W#@AWpA-=00rntlCwUD>ar&O^-mpcTmf>cSq&y3%5ir)mcLLsd^%{JDv!!<grm_Nsm!^SGvowY|3w{6=N)xg4_$?bmKao=Fwpzn+V6?kkM*AuZbCtGq7zpHZkovDv6Ytys%>V(%4&ez|V-h#gqZqaxvt_C!5TbU$VBLwaC5cfUrSePb}5N-dCQ&;#W8btL>+pTpnV2%qomLy(7c(8shtYxeb|RQOy!`jTF_u6O;het4d%2|>u?-wS@uIygUXbV8oHO>sVy2t8x=m0O8eS0neOn|<xC&X#$1`Mb)X{ejtMEk4gfV?Vm`A3BJA7rDjatB-bD_M`ry1KLL}!sp2J@8rHyi?l=jdI8q;P`Qm|-zn=RSpDeEn3p4=sLzPz@ZY}2`5)g~=2!OkqThaZ<-T^t55|5xS0Cfd{|VO5%`V7Ow<_w{5_LB26AWK#wg7c5*f+!Mt9Sm!JQjM2{oB7H+Mno$&x>Iva6cC9h4CCsvg}hw!6NXB^7HL>qa$+sGu@Cs(g%5XU#hNrzeBe3Sc>!TZ3+1~?o59veI+d!<0*jqK;@hJXwP#}<^6+W{B8Jg&v6ddZzjjD9lpB5Tpu;?TAJBcZUtDzsa43>f%?bbJ}B^SdEPqwPQ!nG2G_BwF4|A~8TkW8U_A4mApf0RXz%eB{puahnSC`r#<Fgm?@}<H;4(PpH=I0c_VpHBWPaPb325JU6Y^*5kmIp8XmnKgwo9>SZ_FdlG40=F@R#0{^R7pqJ!kgSuj4VE&lg+TD~TSd=Igb8xd3_mTj9ARd?)gBoQLsTjmCOuF#n`%|I;+f{Msr{NB*QJ^gDhB>K|}PwpY?3(eE#nP=DT++TV<WzZ~<c@%h5=^%v!2d&ksSSSQs-p?&Yws6*a^XU)Dg`?aNR%DhnISw2bn&c}67&)hxG-fIrdlhz6Nd}+`b<8L(>d5#qSMds-c2*2?x_$w1ohtPKL-4c+$$Y|-SiC@DHoq}`27L;c8jeTd#i{UG$=g7L*?>s^N<IUkue1!YNT9wl*e$y+`cSaqS?H$gh$X~1{^8b<>?W;6^|HEZGPpnPG{%T$q^$FK4^|8;ciu^;DVm#}woizJu+goTqJy`B*eYH3Ih`C&kQ!t*tywLBzr*VIEEildEd(@G69QiiN{ix?CW2vW6e?6oK#?x;N_NmvxlNSGNJ)Dc7g)v`~3Su1V{cw)?Y&d7}?_S0_Eb<<Cj^;$3o&!*yzTs&Wf73S0dRBjPv#e*OfoGc8*K?P^d70xT>h}D7vK;r#*YdyH`W3>y@O~wIW!6UNJCwD^-|V^cb=z^QPwy>f&Az%d6ZJ2n%KF>8KS{RCSJS;Rk2CyV_(2IWzjMSO<agXho@vo|jye6@;%j$DTjs^_*)_E1=e5S?VwZp79qN&=R<?K6zKniTCs^i1>vta4wP+UF7v75Jy9pU+f9=&ybKTU<Cy}3@<HosR_}aV*SPx$uz<Rs-GukINNio;i`Q#A%K2>mCmETzXcIl|km08HscsKGN(=lI1+^zn>yjZ7CW=LO~o@lLS$OY-!Qa9nc7PiH@xPJ@Rb!I*CTq%hAvB@oP-rik{Jh5tuxt_L?E0L#Q1nO32wyc|N+#=L-YE6u%_Xdn-!2;wzb8V-2ex3Sk_-Tz&%<I|Zcdn0d_6Wni$U6nTmK*K8@*sbw@fgp}fv6kLAA9U@jHm0!9p?R|)c6+d_b<VEZtQo??CT|a;XL5yi=$i%)Pd)TasJr0*FyUmr7=$4$LcN0q5Ym8q&gZu#ruR_WzhcI++=h84POh1NH))-8u=<o`hVCh`3>L5uZ%l`eYfN}{34t;*59%1iS(7FNy+AVX7`P{>Bs(+zP|kd+VlC>QTQJ6x8Iv=sb}RoXdkr?_eDJ`<2iBoHMCEgB=0Acb0g2o@vpjweka_LzP2Su`pW&&@OxiMHrHPXI1In|&17@^)h($>=JjTbQ!Tg|{ifHz{d1SYay&NAIcOgciFp}6?X;|0TyNC*B<}-@?8W-u(F5%(q~ra`$(C}Q&Qsmsmpx?3<E#;Ye($xFzU|2v>FZ-#pncLMskX+EC(XWk>s*p~{p-Hf@VieQTrba0``}7wzuXh^;uCD~jrLB@Ral=%WpG`e=1Vs3JMH&RQBSTPW1P0pxsb=Rm1P||=DMSOQnY-3qQ5<K-t23^O_87HjGpW1cKJKsBdK>9VSc?HNnfp{9F&^59(fXOpgr#gl#I>TkF$?TUoVbz;b?Oe@1H|9OJD2r1oJz7GxA)IgYV~V>DShMKK#?glFfP4@Hz0GFT?$+chO(vJg%IMaVEy1-hpZ8xAtg^XX7K(Vac-dW?xMyfqD+{L!F=WM*C@{QJ*$N;dkkX_BUqYye*Y*-t6mxZ(90wo^FBmFZvxckJHww9(<oRxUXm!CVlPO+VJ^)NeT0WuUEqLdR&otw3hGBn|*as2>MM4$GXZ}7VQUwO5bTagYlOyh51q{qt5;{&s+R*Td|IQ=xS-Nhpt7QuQp?yd|49tk1s>NypOUEDT?uQSTB9M|2^cHQV4lE-bVYQCvZN*=10FnP&fVMSme2QCsF=hu{iQfD~9LC4w;GQ7w`R)h>@~Bj>I(StD};4Th`~^&G4Uhwd8T0-+(+7yWu_0sRA;O@*p1lmVa^3JTESPUK-{x=fm@6UpsVDUWbj}BPdH2qWz9!`CeULJNc4aw}q!l-xlE~-y170dSTr<Mxgx!?<8{`{m((tcf5Xq_x8c#kSC%$t}FgM#^0zv)=AeU@So~<pRmB~f~>>E*9r3a7y06Sdum(MZP_j9YnL8le)&1#e3dDErG5|0Gv9ltRnJM^IQNX_6kD%T(%0knVjlVVX!zPcNjL|1U+VI?Pwj2nTYR;}Y~<&Cls4xW+H)R_`%nGB9`xHM2-iENfV^H?*%aj28-e`SkD>jxHK@ZqJH8(oaxv5F+Zv6~u?|0%d6ekEs6(DOOC21Qg5Vd}f$v9BN?$PhdSr^_oHu;!tT*;Y%qpytZk^DtPdw)L_&GTq`;4|2KR>VaFY2K_K5w>R|AbreJLf-?zP_ZVJl~Yu(=V8PZO(rz{W=3LN#BwCXI$@&`?9_E`!Tft)C=o&gIA`-kHz~~?Z;Qx7x4+wS3GWFT?KT$X!dQzN@1M`7q|FoL_O@Ig~w&Tdaku-zxV^%zuqO=YcFSDoR@NAzIxonIQN8av&>_j(irE&Ahd5@S^CN+ZDk(&)=n7b)vwS#C<T7FAM#Y(j`5H5z<5^HN1hQ|P=}*eFfX+$V*LDGM)QxxymxU!{&(wf9&D?H_X(|TZ<XzH&cr%7HR7V#S7Pts^Yp7PEWY;nEqvcG`YPse|1$Wge_Qfv9cCiW;EC`HSHgR5ElT>j(k9uw{<WgR;s5Z)vVZlFAzRIL)^`4meYB=8+Vk_*b>I7I5c;it66aODj#mF-3hpnA_dGc}Z#B=Cv91hXd0)VC->WQX4!`G2oF}~RwIB1_`rqc);av;kJnV0oU&B|^E?7Qy?B7>J{*Vfm{i5#ng70_GQcvfZ-?qr>Y_S6KSYzNtvu`)PC+%C>;%ljeFuxblu}->O-Yk8-uQ1LrW#)N{@464^_^tGnV$Uqk-7dfC;~nPq`sl{+y>NeP|KzOIFLn>>l;6K77i&r1xNkJxx9ANj!M{HXdH5d55n2xZckfZp{c#w7Pj~4X_ff{Vq|bi4$(+aedn($O`Ahn)`)7Xc+a}$RzLL?wdS6=T4E#Sr6U^hcH9HQ!^c-AQ@<Y7exZDH&!6FG}-xl0uqwLRk?wIuu^<3Cq`pWI2a^BQU3-R9maBJynQI9d6{Dts+^q228$ac2(mO2~0UjKllZdx^`^p#yLvA)_a#&cG$EASr-LcjTENZ<a&K=_C5S$ws-9r^h_)2OrIE0ys*tnqoFUabxPP6a#{r`Jt0`|8Xf%om?uY@P0|m%sD5TU%Hr&Frf$*Cm_xkuudOedYR{RP%UT{<GilzOhh4%;T+JrLVQ_iu{W=owE3RZ(v(uv-nC}b@+d^K5c2w=UlDnCW~)8Z#tf4rkQ<x)CJt<|FXd1t97GrUF~z8vE=7{k@mWYHIEnWlWpB<TiPpgqHv$H=$17<@6UC9kK<}j-*ND`^}3AvobUEq>(jjr`c3I8+bb<kAkW}uSf6}<X!!b-nwIBKSNkJ6_Q&;tcrM;M3FCaM@_jA-{>1Q=ws`I~?*Ek=Ju#j-i!JkL`0B85%-0JKi?65RJ&)!Sc-rFM#`<*n?y>qUJ@G!%_`98Ke)fL#`GwK%z&J~LW1rgieXh%od5F4gXm06O<Nceqa)os~OZXn9wZ|Dt`(L(T{XG1`(y!7Z7X9*j4OgCYoNs#ABWu4EywUzyJ4<_w&rSC9&n^9`^A05aw|<TLaAUu_d_Kn+>(G^d@+!P12>IDE9_8j@<T-!H(q7^HxoaI7dHxy$|5;;eeH_jCTzt)1p9nnfI79ne=aJ7rN{$Rme)XxRWnZ}bt_3aQu@~-&{L9qM=5_A!V+Z5&r>Q&E|7GVoInHe7lFQF_E*XCIbIH{{+qvXwpY2>S{OsqF;b%XWT=}z|ORhZG&LvmB+0G?b{%q%xt9`a}$<=SRbIIjrJC|H}!vFkO=RnI}XI_2qKDzSfS)W*0kyr6h1_qn{G*g)3$I$=&r<sH6{eS&wX2aUP|JOgw6vOx;D=IJq*Pyl_*C3CjP9%>ducRiBh5k%lN#05QmAsRj!4UkK`iA_PT-gm;%?&I<a2IM<au@PYhT#7&1dpP2CyyeJq;?|@rFNlqGv)8b{)JX23w_OT?$6S-S+SiVcriopPt=WMp_|A*kz*NxXH%DwXOqWKBgsMslgE+!Q@fD+lRIWb2WlX-3ptSN%Mk2G9ZdEkccw;?JCnyS1ka}~CC?|vP&bh`u@*55!ON&?$;-&m)cxdW@>Yi6qtw%6q1VYr$rq@9lP{3(Q}elj@00T|1ly=($To6o>euAf<lfYt<lf|P>IkyX#pG~u1a&Dnf;@>KIFcGe78*;ABx}?-vPO=|ipkWUsBz>(Y7#Y$oJ8JEjU{g<Cs1R^F&tk4L-00+;4Rd}<i)JT7KY#%48eV<J;^;;-#!e%t*B+lt;pr5`N-wSxfp`~<eZCj@Fzp?Me23(b*`<848g~#`^iGLlMhlI)a_&kc@}jsc@}vN^(XQi@?2^xS?Fx?T=Ep^IPw(oNQU6{)c)l5<S(fm$zPHiDj(00h77@N7=piL2)0uL$#!x8)tB6c+K}pN%J0kmh5DJs<Hzv|?Q9x<XI`JsF=V0hP1io3^$;3ks!xomhB2(S&}C$y(WbeGHqBQw=Tqob)BFlPNIgnENIplsKo)wRe2#pVD$bz0{9Uj+LvVSjja;4_Ky6J9Ab(5kP43Ne=Uay0sSLr(s1f7{o<YkPf>$sEucStjSCUszHL}KYXB9*6YSY=YnjzT15WJircp~*D@<j3yhTyGkAJ4U|j6_qOL{t7m_9-;UG=?OOQRsHE&;--?6L_scx0$Yeo2fqASTmtpOf}rXdJCOF7TU)&7kxNCLR*>Us}<)~XgSkd3ocL1<@RxH2sYM_V6moz{;7OiV}EiD3cW}cdYo*WYl5d`#jvdCofSQ)Vbo#dFmgAB;JysO8g&|3BmYQ^BmYR=K;1#!K;BI~Mi#1*caxK-zmSv2`>1Eg`^ah3-^gj?%hZSD%jCZpf<JMC=5+&$5L}j8id>fLPyLGQPwqtxBKIN>q=t|Ol7~@;lZDPB4<nDK&LNK{k7EcPL;apCbS8NWc{Ftvc{F(}L-2PD!Lu2HH!uXRX9$j`&Lqc^*HOPGf6wu)V+h{J5WI;xkGzRIojRO6og7LHA%~LtQiI4roR7W?!ELCe$Zg18)VyRba&Cs;dt4)8t=wY>&ZPcE{*7xflOgyd^%wF<@*alZM5<0sB=4dgBkv-wqV6ECBG047k>`;oP^XcnasN+X2>y;CxD!LLzw+_y@Mj2a$q?LwA$SNij68(gmD-KmlIl<GX3F1<{R{0&7OI)XrkTbpcn0-H@(l74>ISmV-Q*?Y_0%Ntdh!Z};LX&1<jv$m)HL!T@>%L-ve3WCXUTt1#kunbe;1sCA-DpyEV%-?J=LGwo@}S~BHPJ>r~}DDhmi-7r%=a}r;ryh1pi1KNB)sKpE`ytbToNBc`kJ<c`o?}hTsL%@5s^A3Dob%6UYmxv&lj?kQb6SGtXw`*i3%`bv=0j*%;4yj!|g5Y0UAwCZX%dLN}VOcOz>fbd#x8n@siG#2O2oP8J$!s(&cwM`&NueD&qr3T<PWYr*ZQUTz=PhTsa++-@J&lHeRvajqF_@1F8;P2S_06`E;U!<k&~LQk63|4Hr-p?ggGWe@k0&_vVzO5~msx{EAym1#e&;(ir6&$NH%ajy%VK%T&JL2&-8Yblf!rKw+#OOu;Wo0FT6dr*VP1E_<k!Q?P%e`+wfKRJ-voE%8@p?*R3A(x;QA`5-4fJ>0yDbU;GcjN~Q!8fSq$v4O+sC&smlgTH@M;L-rscXoo<mC*(3mAf@G6XN8CX*MDS5x<rSCh9;&y%;1)2X+~>ExT#=j5B@Csa|pC)E7pCtMT7=#?fHBUhm|Ay*-{U<mF<?LqEG9%5Q6Ll}bBG6YX!2wp=SOg7fj8iwFxMwls2m??i4`w!!q>qiYVjV+L459B&CuEmGf=fkySTyF{1L#S9=Mtuao<a&EReo4MVy+OW1zC=AizC=F25S&6iLQWyaQ&Y+D<b~Ab<b~u(48b$03&=Cc5!9*V2=ZwD+tJK7n!b^LD*K<xb!?1h5y!iT>)06oYF^)JuHysLbknt`n`)BInx%6c8#TPi8sFsFeMuGbA=ocVt7gSF)Q045$nB_KlG~BnQhmun8<5+QTT;ErEy<0j9^^*k&!}$X&&Wj?f?p}nM+#Vk;9Jyd<Xhx*)bGjb$djo<$&<+=sNax<HYJZBhftf7L&%|2l^jYQNNq+QNFG3KLLNZwM{P{*M-HY|AqSJYGXyuFmM04>LvBDWOD#z*Oa6>noctNtgIa*>K`z7)oS*s$IX^i!)txLf2RS!64>cb-54j+<2)Q7+7(;L=swY`!IdUnoH}z|>H~Bvd!Qs?aWT9=z;p9=&*5py-;S9k+)T-nlaxZFivd}){UgYuAAIRg$+o-3=+sId_zmu<!A5))^ACq&sAp{qsz9owgT$rl3frS<z7bcgaeoih)u1#%Bu1)U15Zsxnk~@<-QJaxFQkznnk(-k1G6dJ7s^og)8q~(*#vES_hG0)>0kS9gg925^A6SzY3PSKxs;JjfhTwmx&&ba>AOA80JE^D0PV!;u59Gt-C~6;a6uBL>I=LOW5<_rBYE^PYa(!xRa(!|mYFlz6ay@D*ay@c2>epnU<;c~@UQ|!A7x`0a5%Q<x!qj}^!sJ|xd?>xt9Ar1LLUkt#{Y3frBRD5Ra9(Nwa$a&#YH_mAlH{V~64Wx}66Deh!8U4nvW;AsT7@jMF}X6?huVbfL#|0}My^S&O;yRY$#tmB$#uwesZGgs$+Z}QzoLFa{)#+^I+Q$!Je~SIc{=$j^&0sq`5)>d@;~JFRPlNLp6WpsA-D)VZ*mcGC29k5C2~!M;5t-avd}Ndb;$Lp4axP%wWw9ewa672f{QZ*e@gWu2L`ygd*t|k{V%{i{)q2U6wCh*Ec?H-{&|Y|U#`f?<@#flz<^xh^EPWUxXT+EH?fnI{{hUBKPU'

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
