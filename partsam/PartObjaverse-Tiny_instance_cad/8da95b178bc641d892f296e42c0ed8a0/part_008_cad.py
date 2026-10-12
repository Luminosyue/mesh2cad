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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_008.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_008.stl', 'source_sha256': '1764b3bf2356d2ce19f98656d146088f169826866695a57eb21d27981340a15c', 'input_faces': 992, 'input_vertices': 612, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11764144897460938, -0.49999964237213135, -0.23129802942276], [0.4634231626987457, 0.06691063940525055, 0.46973711252212524]]}
GEOMETRY_BASE85 = 'c$}r33Aj$x+yD1LMaD!*hKEQQGh~h@O6GZ195dyIOeLzVGG&ew6^~h*keSFfo+<N?F%Jo8P(PKS>D~8UpY@!**E#>|`d{zsy6)@ydA==cuYIq3uRXeI*(7t8e3trC%-a3c@7<#{EK4GXmCqW{d&sc<J$nx=KXCBKI4h6m%O9;Xo40G$vQwNj!WvboSMQ-chm@)rDpk8r^-^U+rTPpSGHgiqf!ziT>D62O2Hgh??d|$Q`*k1O+x`7m)rytMhAKZ^HuQSvfBENL8G}>!%N-(JcAgZC=KJ|@UGay1woQK9{r^4f`B!@>|K`Q5Ui+?VPY2qMd~l2BH`{j3^UGFJ{sSd9%5Q7Tg0q2se*9&<*Z+m`X9NBG)^CQ_Pq*(5d#c+%Q)jaGd(!DcUVmlteB=2IN4+b*BbR4;enfBgiTrQN@A&yg4tRc_-beg?be{6<rgP4E{;l29>t-}g?e9-K5*SZ|>$60i0(W`)8`k5gT79mkKfj%!Z?j(^?Y}kS<GLB;4d2R>a5%7E8zYOnep0u6<K>|*`(^l1y<ggYE5XZ;(<j(Ij33Lx<{?Y!W;E~GztsO&AP+B3TkiE!q~4jp{ys7;!PC!XXXra~&z=nQj~`w)`9z?9d^>XFXdrKe8m;o$*W2dx@96yCTRA>E>d%`UKX9$L-D>xp@{dRR@g+N)2#j;wqwBo(;l8RKbl&i7d`IUEKb$ku(LkQ@E&PaX|Ho+Mw=8-pFn;{-KaEZV=Dl_0&E9tH&Zh$7G5pwg@U3$>PXxw;@0`Wg?Q`yTyzSoK#p}mjGX9|7xA4PxZ=Le{_Ab>=*k~WtKJD#RrFW}(W`7S9+aK^3H1^ut_~BRED8IJKvmTH3om$F|r~jBgC+?_!JleOluiNKd<N4u^svbg{2cGf!*6XSsEbaF@y~oo^znu)U$G6`Y9&BH-?Oty@5$aR#7k+#mRiAo)?G}4IKb(W(g??gwMRmN`x5fq9M;5E&C2aUsvN~S$c;W|F-lvYo^<R7K56?=K-_fcoJl`2K&0E*)LY34!=G(2>XI00w-e2uUmzO#g=)cA>&$mBO=MksHoCAJ8Tz%OIzi&T$Ixrr)(F0zc$N&ChqBov4o4kI)Q|>wB_ig;p^4h2Uess*|Co*d9;9In}E4`xH>;0WqD%J1X_~B;ryzw}<CwhMPakU=m{A=G%Q0t-2f279MME`y{rB%P7_x@3SvRa=V>QnnplJafpGv?<|>vPy>Z{vsb@wIJGlGp!PbzY9;89#h{qc=_)Kl;>Q)qZKo-TrxxI=emJo-zBhKcCtU<Lms#{AZ4M{fCV97QW7ZczK~@Z$H?sb>n!d-`C@b7Jtsmf23+#&vz2Y=d0Jfbu98`JI}X=sPm?EP#s6w5BF5(&DeS}{x#)4^643W{cGQ;>Zs!dKlE!vjprQaaq3+A;aisu`|Cg2Z>MTMSk;eJZEK?6kEgDzxOPXqaW?x^^|N8%8Grq2-(Gyj8&5ob=<~)YUjKh)362Lp{&deH{_!}!uTt%Q%yq_JhcSO(XH^gQ(M<<DKRiKQ|L8i`zTHe+|HSG%oY~8hb#<!B!;*2E{k}cy-~Ac+VdmG#^;c4$A3g6y*Lm|B+L0^Oe;irUTYKwlC|iH!FH_fzy3S*Mg_=kGb#DJUDmc!osp~TIdp^D0@5jb(w2#+5?c=Y^SNmn(b=H5pXy4MlUaz!YvDZ=m@uL0c6Ux`ei?wpK>VL-6)BgI`zMXX1o5u*gbLPlbf&Dr%XLUxt^YB8)@5lDnXs`FzrhW9}_nz+z`tK?Kyl6lE+KA&`|I?Hoe*f<M{^K`1uI#al{P?QP)p_$!dCw1V9NE_3y?#H;aTF@_n%9q2^4xxZUD+e@C;I*966J@xFY}JO=(i83y7=ec^WHdFSG6C;*XwYs{i?$UR6PgVTljh%4wr4N+PAEGDzLwXZ|nWVckX}OJ5Pm-_S)C^2`!kewp;y(y8dU~(|-KO57hNM>t1AXM75v#!qLF-h#z^ZM~dH%@3cZ~x8pRgf4$CV-|EQymtJSO90~Tnb^1oXADx0fWAxTQdtIN8)mf3DfA{U3em_>9MtfbK&RxOwvHdc}6Z095{rqLM-Bz~)>#FwccLoL4`Oxxw>bjEig2Q^KeVg-wUMHRDk9oe6e^H{>p7U({!A8oj|F^e3SS`6;!VmvvfVbZ2b<9a^8R*B(-Zx{v{-3HodvsOfc{eq%E@?lkeSIF+ev?nU?S_o@7JlqJUNrt-VBQB^S?~8_^M1DEHox!a{2T3K^P<}qdPR+Ac&fVJ3>8lF`=P=-ABZdD_<g7Q`(Jr^aOUms`__epd%XSK)XO{X#Bbjn%-f`G`!n(*7g~FH2=%(C{Jv8I$C37<!z?xa#maY@{26Tj%h*jB`d!9v@%yoUt_R!4{LZR<eCI6QxU6Zdy!F<)QfHsvkMHuVy6)=yXJVjzwU<;~O&|58-w$W*rs}rV9VgJfz-;gM3jee%;D<h#o$B>JI&r(-kE~p<*Ylrgo$U9cWfrRIJ+3#xJqjKQ)DP!b?Z@he^Q`t`^<%WRwNHC1NAW{}Ja=EcF+=~_3tRnuEYI=5_A&o^)jm?B+97|PSaTcg&&ansPgeO_(lNN*q{16B^xwX|)$d!w*=}O6eQZ2$srKP>AE-R6nHQ)}?Z^7R{lkU~{Z_@k@cXfOY20s}-;d2p+>-5nKcv^~UR{<4`oRx>HE5ULkLdN>Xdk=2GTO)H-58IaciRe%CziKc!TpWptz~e3?QhQ~`;Xu7vX9kqaqvW7-PV3=-n(&sVfwE|4h8zr_d7ZI@ALby>yrh49rgRM>z{%P_5}Lj`X@Rk>Rl&<R<Bj#U)9t*AKCi;1>fp)+gs-&`aVMYjfbe~XMKOF`w4GX_X}K4#{9p|d)J?_>u}vqp>G4%Ii|0#b7H=J{!qQoF28SH2gbHrc%oY0Zd}|O@EeZx{E)HTFn+pzUYMxPBh!rW@6W03gPM0p3iR_(f_h$O<iRQUhgv_4yoL8J<ovjMyWfvwALRM*M*ibh7E<la`5InIo!2U~-x+AHkBbFG0=`qDoLYzTX9;ZA%9eefs{eJ#fjk_j9=J}n?>(8}x|GgmUDCd}E@|Ifmz<h$hXcn2>!j)HbuxZc&clK2vTmpIS+})suG{H+*6mQo{OWnCao*9sdEU{!dEU{!dET+}RSJ%i^L{#?^S<`Y^L{#?^L}_jonSwDoySji9WtmxFwb1)n7+QwadO40{2132+BdH&V(pFV3hkTM6|wflb%plL>k93g*A?0~uPdAtZwBX=>rCyN*QMGwuS>OWUYFW8rUmoKb$B|T>u~G7#Q|TRN31i;Rep@?TkV_Ix7s(aZ?&K9`Zn_hRiDQ7zxK`R|Cn!F|7+j8{<oU#P~$P~U$k%Dzu1%a1?PqPGVPo9iLv&^ePTMF`$X-V_lep!?-R9e-Y2H>^?hsfl-e)jzEAt+eP3wU`QZNQ`vrXSzT3L^t7>oDhiX6FeQ4I)>UocGpRWCM_vt$dDc^W*pndbXfz{?I&o`fAn7%&0Yu|j1Vfy;KY;9}o`RSh9;HP_Tv#X=puKC;sKizX1-QIj|gKs{!iL9BW`pH%7b8o!kYpLhgSLUdG-u!O0-;ck%KwTFY&#AO;KBuzh>{i>ox8*YLzb9<o8St|!-x|0>-Pc#yr?xwFq4(a^d8l2`-?CJ_kF_50uA`i%6OROr3;i6=@MF*Y@Y6l_!#AJ%*+nj>c{HBmnZBN1XEe_vjpu~gH=h$ma$DX!JEaoWdi_rz|B*P)w@3WG&hI-d@AiD_@|Y1`|CgTK5%A9{Kbq@Bb=}h^Yp{L7Lth5`)5;GO-k{EdALsP^_;*{Z^zx9s#IArp5kE^Cp2y`;&-L&AJHhieZP^*{?^1ra=a=fa*v2781M|goMLM7B3hkTErL}K9myXPwtnMd_=f>JMpBsmso~7Cw&#|>{KF5yv#&c}#o6oVsxmO4GOJBF(o9_#pNo!Pl<2irKH=gr{S8Y<`H{LI3-+aGdXFI2S<NZSPB==$Fdk}o{JxJ*19BQ32-m}Df<2{SBsjl*k_c+=&-{V+wJF51^dnN6g@0G&4UQ*AGjrU60PxoGF+f3EJ`JM~ke9vW<T&8^EJ(~8-_h|8VR;c?k<9(m@&G&syv#qKh<9(mqQu*flKJBM_-&fN*?(bi}-*hTu_I&gGruNPEn=#*bzo~um{ifZ%tn$tGu=wVCSm%dcs=e`ESo`LC;h1l{7uLS{UO3!z@Ns{g>-r3Dc-`~O_u$$$--Ac1%~#_$-h*r3d=DO~nXJZXyvNtR`5s^U=6n2DKgN4}tMVn~8{aL2yW9-yudaXl#vQd?<NE~do8KomD>9w%`Z2zL(7yToLv&5!6aMYSzOR@(#`DeZI%2-@U5EC~?>e+^e%BEyzSZ;1?@Y9BerMuXH`R8H?^v{-?mL$6AN$(#jq4x#^R~)2u1{jVaeWeA{;KC&brz}fFX!<{)+wHEeutxd^E(`S@>I_^uM;BsXQ}qa^+3!wt_PgUbJcb~jC$AM&JR7+dxiNQd%k(zkNL)V-+6Vb>fiWIN&Dt^N-^K~PD%UbcS=@0M{PG@R;quT+IQxZ4var?<)9jm@tsx7H@~xb`r(tF-}8K+f9;2PE}G8o|E0Pg&t2X7d$E4{;g1Web-u~)lNpU)`{~BNbneNF<|Vx9Z{-``r)l5(K27`P_i3?yjPKK&!#^-Tbrb#j75P0?tv9zPBzfbBzT|xmq5W`;OR9Z|3(5ZW;p)nF_I;P^Z*Ldvs@nIet=gaZO09o+e^%e4CVlTcZ_&Pea-Q-(d46w3zH?(llHZShwp~3}xte{C-*@nx<%!9D-?}}(d!FEISKr~q+TT*XeRO$Bz~6sf-M7ATW>;W5+Ru3_(B59yIys~MwQu%s{}h*$(fH%>&GAQfg%UH$kArXKCp_`+K7XD=JIkKQDF50w^KbgPf9;$3*S?v5?VI_JwKwt~^Nsw+#$)6^<{SApeY1Zv|Jpb6AKPCe|FLlz`PaUgf9nS8`l|j1GV<dulu&v8eA?cOeCygXNq*nD60hzfw)WqXk?&l1F*&f^>oryW*Dv1f_rv)1+43oVU+3Ss(k;+Ff}d``@WY=D4fGS;I5s(>?K=48cEdZmC1tc<A$)VctgUksGs;_Zi}KC9MSpCU7^wf3>wDh?J9esiF0}iSH*eavyS}UZeXk_@{dn!KY_rGjJ7wk{^!)IW)IdM@R;5RG1=@f9vYN*$5AF}N$G0PEoPa+wm)EcTM5TZq&YxNNPtOVVGe@0Y?6MyP{IK@Bln?ad%x>o8**3?6Z!HLpCt4_^-oHE@++PRZHug6(BEid-l^D#YrTv6pKCOzSmA^;Li`C#cHGboK6!VSqQE0?qHD9F)91P4azLmH~9bePmO3KK$FE-rk_d~hQsCjurZ8z2)-)eqsccA^K(cbZ8olQvzwAcP@E70C)_qST#LTh&U{cytXYQFkDl<N1>&9C8GwF?K@>v^}TuG*E6AFBua$TvAv`_fs1+tq%f-GP4W{q;DmgZmrSzOld79d*57)#;m(q5ovBV1CT{)Y~=dQ*YO(6Vtbi`7*Ct()lH)><RQU=8md!qkgn+eH*MFr}B2?zqu(fBj3)JH&~y=mhbb|zxLA|ce)?*xYKoL9(THb^SIN#dEBiZ6RfwfqxWazTi@1F>(IQngLSoak~f~{ukQuxaN0D_cPcCn`t!d~?Mo~PZue@=RKFih%B|Y3Jrr!;wWq4LF`0G;{K*ZK|8Gt;?**5t{Y_T=*e7nK`29$Z8)|(ia3kP{CpfAOZ?+Ef6InD})#189o*$oknc8kjC$-&5yHotWqsKFJyV`!1<+RVD`rjJe?f0Ec*HztKyrG`|-Nt9T_VG?Be&3$(l4`$YwwllDpQ?IjdRx_VO}+=gkJ7)j^mxFx-?&fpGp&ZI=SwS8-kLU7?Fybv@%zr?8>;>7OUZs;kH^|tCE$mD>#o}ODH-scW7(9ypm|`s_USXKF1H=?{P<HVgYCa~BPk=_Iy^eyTjRe{{k*>+F(cppCjUOaZx7oPI3Cma4NfU7zD@P>T4j}=erny0`O9~!ao)(A;`i;B52)>Kem}|YJCD8==s#LD|2fake@k7*PWhaF=c0VQUfJ7*r1;z0MU)>NGC9TH-YU>s^*<yz$=^Oy{g=J|?MAjNSN;5SN!8o<^Qm=P2L5&EjP^;htO_o=k<H3y_37^Wr=i||u&kJ7{7*ysSNZ??r=c}!{Gb16XuC|7)!vOK2;oX-M_9BITnVm-c7R3Oz!l*NXlq!s8C(G_hc<@G!DY~fu;_De8MqYs3@ln7E(MoF!?0*wxFq}tS_c-b4L<^h&|0u)O<1%T9D)nEk>8C1Zp0D7nF-;$(1&2rhvB>6dkEpIXd$=|+saA^XD5VnqL0Hl;oN8yI5&JBS{1$z&Wl!q^TK)1C*eGBF0?Y73(kQ)2Iqk9MT@}q!r91MCUTh{et-~u5X}NV2p2@}h6}=l(QI%wwpExAE{ax%MQgyKPr*gu;^@<`Xg#<%TmpR-7Ht5RfFDI0!J<vzN8!?Lv~;7a8%@#DaB12!C4^g`jbPE{a0|E#+8Gw@26us<N4vwKJz&unV9}1SXnR<+9sE4p7A+6Ag<GLz;j-*=E3_%xlznK0c7eOF4dHEZ?m5DZ4Q^~lce=3`-G^>~H_(0`A-pF}jja{^9&~^2cjJDSzjF0}8~I%B=|)#K;@#Ngdb{07b>o;DN8GrG9)d5zQS>kzg)b1o-=at1Z{hFI<M4Oz74&QP3j95K3Kl&Be-Hma2>*nhgGJB7Kf%}0Z{X|j&xG)g=vi3wH2focjS#+yo`kQ$m(dgO3G#cH5Wa+7gfGGWC4_%Lqi~d5|3V1=ihc|K3g1A#gKxmU6T&yqEASQady^2pgZ=>Df&U_e|3QC(|ADPcO0UBb!vEs^4F3!Njs6J#4gZN=gRhb6KMCR6gzz8eW%v*HH}n#GiCq6i2;V|~fqx;Vx6m8#4f1#ky$RnWN4L<w;J?VrEmU%G3;h@WU-tPH`X~G+`*sWc1O5$_--&J{yOBf)rx3zlpj+WD;F;)quxKNACfpdEY$<LGPa%X`6T+?B=!(unC&M%0FnvhBVfud$4#N`&;ZM=6@Tc$&G#O4N7dr^yFWp#<ZblQ~&F~g93El!PCWP0ZDexNjb3%9-`USiU9)r$=XOhP;gm4`~_yck+`Tc+p?t!+3d%$(vc+!okZj>d2%cFJR@^BTjHQbtcszL}?_RVEwLb#?I&Cmg8S9k!t2%QNpf~&_Vl{v0X2)}|(fM0<>L_dW;gqNZ_;HB^q^h<aN{DH3yJ|Kig5W?fp&G2}5Iw3p*-2!i+K4uWYwi~aZ3(&>z0(b?w23|uAtssO~62c47W$;3H6gmbT1=mLFz_sB8mQtyw1%z-vv<KV|u7}ov>rhYi2;u7JlW=vonj24}wa_QwC#lg|gm5K7xC|j&4lNItr$)=6mEm&m6KG9X*Xt96@Kc2FGlXzkLU<@T03Hf2MHj(K;qq}xrKZbM+poao;UR?ZH1tDw8XQ5F!b_>+2q8Ql{Q#a1PbGw3Mn}Le!{rF!YUp^l8eA8h4%daBLubIx!3|LxZU{f+J06}QgloA`8XbVX1`mKIp$p&z92=7e;koEacrN@gAv^_L2v30rqNCtZ947+_;j)Bqf~8cBnFK<36xt6S1$RR0!Sy&cIuXK+&}wia_&GwjgYQ`CKnRZ{g!`hk;J$Eov=ZDMZb=ANM9aVx;R<LuxE#k1&y75;jXnj}hU=rxz)Rd1;>M?h@T-Jyd$bMQ9&UivhwIa4146hV+7@mIcO-;gLx;kz!7I_F@JhH$oKiV%%W(V-fy==EA%rKR)8NVQM`#3&aIAhr2+u*M!gJtv3E`K}m*JP-$I)`|<FL-N@Dj8dEFruQtqV&CzlS~tO9;P<HiRXFC!tTl62i05TCjw0#7aB<g(ZYnSSm{U#$TF!D$Tl}_i+F@7{FSfb27=7w@Ku366=D_?Obv{mo?%ebc%0YrZ9(7SPS%=4)o3YKx$ziYeX3|!Ah%>1Zqljl&{7{QG=qLd^OpLniXy2tKmkz+HOSci#`X7cJLh+9XN(WNBWMbksNcMqASpmR$Bf?GAE*at+YAn%N&Y!x6<acJ994D5`K^RXn{_GC()(_S`lsm*FY=4qP5`~a8tBCEZPQc3crL7fkl_Vq6^`d;1|&M;P)8Q3uq0v2HSXnzxx8e|90bFHy(~tS~yOz=wtB1a4ED9Tna9T{$nXF2>)d%-3|W*??l(bJK=Tc9(WzRi`c_>_b_JRTW<X7#tw8lyaQf~eh#mN9rR1sf&Zi*>Gy#+r4Pm_mJlw9J_?tF3!o3d1>oN;rPBBBY~xFKoa@hX<3&RFO*h^~7oqduMetjM@Ehnj_zk$f8&9Jh&~b1FxIX$KTp#|gr9$`*^i5bo__mccR$&R@JFd!moNjLPcH;;1d$b$;J$%)TYiNJ88{8jmj@E^n!!M%o@Qd(G^bULz9?AG*oFfV0S?D5o7W^vu7W^uFjWG*fMc;rWguh4o$EEGB@DEnn-26a(gnx4NXG>{4ev4m^5blU}fIBc}9SPxQ2;m!+QkhHPv2M(8V>)^RzQKG?NB@AQ!>^;a;n(3l=pFbDdGA9AKa19d>rw~L62hZ>wK5w02_6kkwbF7l6`cl8h2KHP!eiNochJ}2ci`vIK5!q#^gKEm9?dp{m%DMnjg5rx0Ydm&LinyY6~g)BR0uy3r$V?yoC@LMaVmuK#i<a^;_78ro4NWdAv_cv4G)FiLEnepfhVG$z!TxI=xlf_JPdsu9tJl+o5Ky@?<}QPEX5MS6VdUoXfJpoJQ!^P4~Dy-VYmz24s8s#gF6$#gV3JvAb0{g4xRvCLNCLjlIu(S7S2LE%lte`-t~M9We$gucRi=?FwgIhcRlYDsfCH;UDw7~>SZi>*Yz`uni@vlb&Uy2-8EnybRB+2ZGK0t51@m6bvu|^9!!39ZFiyGyO7`Igz#dtGrSmHMhI^}2f-WQ{pbXEKYS6r1Ye@|FQOOlFLHe8zk9*g{{`O|E-<bOj9WOf+fOz(qL$M8VA1<w(LAtdR#-F>Ec%V5SoAO~nhJ}40gG;iMYqACU%{eB;3$0FjdN%cdIU~_*Pvg)YvB3lHh4b#KDrrxAD)MP0ndY1qp9#}I1xPzC&FjZZ{V|V4ss^B%RvZ-(5!F>eiF?CKMB`F?}ux`Rnhz4s&Fwh8(a*|iDrgBa>w?G8*idx;5Xsn=qvDW_&?}C_&@M4bObyMegn1PH{iMG$M9VEBzhV?30I6$S~*U!gm4?Q9oz=)jrN6m!-LSl@F2Jk+7Ipnw?*5-ZQ)9Ua20Y|g?v}R*ZFVH{IsVpJzxEp&wgxM&+lO7e=uX!_0X4k>C3+9`e{dfwIdh0-h|JRv(vu%JWc(cCfB;2Kc?P4W^Q!-+Z-P@bE%J)5gbn=n0tME4dnP6NUiAO@fD8OSEwz0{0b+bpIB+fyYM+e_ze0Hd<H({#@FaR^dop5yb662UIouVhr@H=S?GV@S@4JGF!)3GGxQDkGk7mL7v2k>Ku^La;CthgN`2o;2p2)yz(wE+Xm7XzTmu~h*MOfu`@m1YMbWl!Q8+tV36_ZCzl+}EYkv>@iRSk8pPTKA=JkyyFXI)><r{x4_D}R~-~QfBK13~FeuO1|qQ`vsJVw4n5Bl<dkogf!_RUu^^C`N;H@{n$f6-08de}t0h;H@O&sOS7G{skMDb%CrAzytSqJF=Ij}yX2(G)m^evhJ?;7yG0D4Gl>v!6%NWAHKZbriiDzMH%Y=VESz^D=+JxtU|(d#Hn>^ecQE%^sJwFT!7=mEzL&SNIfK1(py#W2LRF`gj*Uhh~mTTOWkaqftw-+!Os`sr$bf@C`y(-#-fL`$}PbA1eGaAv_Ho3(I}+kCwVu7VQ+5cJC}a3mqPpcCRfw673w9c5f~$_wJ&<S!wt3!g8<Q9DN)84SpNGj>_M^jt+;1Gmh(w@kiQUXZ&xW*I?29@LTZ9XmhwZ+kP3n4!?!UZ@KrB`$)N;jCZ%&)s2>DE4U@x1Z@g8fm^uI(~WL!yg&%IMq9uwXfM19O+cH%3GioVEBG^bJ=zss4{subd!X^KXfL=2+y#9e?gDp5d%`{0pYDY4I<z&c_h%g;yc$h_6WE8<=z4fP<6cb&uSI*nJs96wLU<$E9q!JyH=?WIwW$2gtd<cgiyL>Lnb0^Z_IZ)V@~4y=kGt_0AzYdeE`dG*mw@vV!t%NFeP|K%5x5BaDEc`3INN@d5H9IPVYC=p3N8j0M<0WW!w(U{MbXl5Q8+{h7eY(Gh2Y$1e)t~rUNk>^FPsg{2WNw``tl-tH<|;z56%G>K#RZy;D^yi;fLXZXi2yr{D3cy4-mrH3E@0wF*pyLmk_=mEe;nazxNZux!lN!KIlfvCUKeaW&VHtua(mN*k1AZ|3^#a-wb|s@Bf=cYFcR@;kRsZm*mwg=uF;X*GX1J>wf?deVz9'

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
