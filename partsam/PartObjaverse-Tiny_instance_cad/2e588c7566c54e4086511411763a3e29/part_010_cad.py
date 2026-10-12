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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e588c7566c54e4086511411763a3e29/part_010.stl', 'relative_path': '2e588c7566c54e4086511411763a3e29/part_010.stl', 'source_sha256': '6ee3523f3d3202b8760c3d66b62fd2be9d07ad121b1a3fd0e444f0c0bca5429a', 'input_faces': 640, 'input_vertices': 383, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15299548208713531, -0.1753981113433838, -0.15351611375808716], [0.15922345221042633, -0.14721640944480896, 0.09762923419475555]]}
GEOMETRY_BASE85 = 'c$}r22XGWew}nS!5k(Lgu>>QM2qp<c7&2G{kwsnsLL!3%n9RTr7=B}tOf-fi2!zQd2$3{MWUx&RwtzL+<ZQr%r@rSb?9TsQ)vNcYx^=!i>h0<2x!u##vqea7+H`p|{41vIjcu4IvZSV|$g1VhMutZX@7Fs#y29Y0qrEgA@zp<<#<c3tGNiMYHc}hw-zPk}ca(oEn}6-Tf&S%f{(Xl;4UY;N+;d1&pK#?j2^$z4p6W+Oh7Ao*{am_AV3qQ=DrL&s#@qgn|1zgG!Pa$ta$>6LdgNiHM#PRy^-|TG{jK=g@Nn_XWAC;oUwb_Pe)K@`^;7d!E8iI~SbQ^EAMx!0DO;6q4;ui#>(7Ved$~7nRKEVMm-xnuc=7d-S69h#kM)2bI~2!F4w|EU+rln5ZkbI|-d?Mpw8wd}Im$oZkNR^goh8Tpp)Ss=ei+&rxbbH>ZuRQ$=fp{Q+o%T8PVIC6>S_G+pwzQw$x107SQ^KTik5n8AGgg@>KyO|$~U<u<@HLw8&r9RqY(T?uTjrm>A#is5Ai`grIOLk1Fd7E+{Lsg-}DB`_pG#8`eF6QB=P@VDdmljEYf~w>}&D05j}8TR|jpAcKTd}KQgV9cjgcHKGDrL5A;O+F~2#ae{x<#`OR0vH>Qn{{xq+iL3y(;%3nJ_Rr;stVfaa*D8Jk1C*>P?lF-imN9DL?&)YxA@vrYh`5r&w`kp!@?YG@tA-?XsEA==U*OLA>3oQ4j$3A`9&r+`CQuuLQk)M8k+ogQLMX2ZLD75oj!TD0(_5~=vHaq%Rn<DM8-<yi^b6cW(ct6QQGky~MXNS<vnVEKpP8$ioem0y}N<L|iqg@ov>)fBn>n6{Z%5~X25dG=6kLx`6{RHXf>5=ef9+Y|<&yx3vKIw}3%P)q1Z-`t+`@g%uAAd&LX?t{9`bRI>8GcGSv}ah4c=`MOPVhTSm-6<Yoap~f9h2Pi%}g0<y8C+BcIbzO9VFlErGn9KLoQ={>}tJMeE&u$|GYo0*ZrxICr0Ty9`$QpZ4OAeq#*cTze9T_U*GHQn@cr}mt>y>(w>)r@QY7Dd+M&=D*C!Cj@zIM<`ZXvTzA`>67a9SVtc&gylig^d*p-OY5Pt&pCkEkUY$*hqYa7DPJ1sO9Jg5t%C8zA`RO>88SS6dOMG+u6P$0KG^qdAEbxPt#>sIPeU$pl_0KRaDyE>HD}OkE;|_#>?e!k1x9Ss=@3{c&iOGn3j(7-v*a_rM%w>$PG`CRCS7YEe^IItSu=IxbS{iS(e|cT$H<z!En~L%qN(_*Gt9~8+cl&U?8kfWQ)c6DScL_)T|K^=2{hIC~e9niats}l4cn<C4eBy}ghw+=?82suVF)oh(y+g`h*ok)LnJ2#ORsIF;zA<qq=D(g>W&U^6{RziO36<;ad|zva<l&__)F1d%%G>MR-YxY-tz|t2(a)2vbDmrcf1QSYK66MuJJ<Y(db%WFyf2$6{ov4-;<zunp&x#VHlfqm4?ps_AJ)imH;h3&XYVFsT%D6~ZO=Ud<zr%S+=Ww+w;Q89uCFmI0{2<xQ23=Haoo4><hc5#fgZ;-Uai?8<;F&$odI=mU49vj`C)T7>dEyG^Tt`^z3r>+sAunF@tvom&<{7d!f&zwdGfK6TrWrdwy5V$Z(PR?d1W4O6bQz3EWHEw&3RWaPA1ny`AsuW&*lvY(!Tp;QNOVd$8Fn5<~Q5aGVu3}#rf9XB%f{5ilhFOS1|uX9+f=QY{gK1zYX>0KDS)j)6Nh5z<I#j7>@Sr&58CT7C`xeufLOV^f)_@>kt3(slKB7GNYaw6VcDNTgZInc=iU@|4~i&Ir}XXo%z~yZ@+#F<JM-rG~M&ok$t!1tz*_blz+Je`4E8fFlXO@U#Sf0IeG%u@!)0g&8baLE?-;8H%Gu>ln<DP`^AWVB(L<aWVF-w8v4O|8OAkzy<G#G@A8+M<vM(CqW*6Jk+-8mce(re^StQ)voB=*<EW5``a?RQo?N5XiGOS-%C`?fJq;RemwGF0Mg6sIpq|=S<+I~N9Q<3u#CH_++b`qAYZ3fzoiKhgy+(fi8iVsKUJ3p1*CrY7+UcqAb8NzOSs9P}*YYuFXYvM&>!Iy2US0n7-I%X>U%-0la!VYy`FZqz=X00`8dkx1y~u&{ed`-5`E#W*%9kvT_P44kdE#v12Y+D+kNb!*rjY4APPMGXaUY^@Ov3ut{x}Tt?f496XPXe5@7`|fRXt|f^B4ysJ7N7fs_9Pg>%@s~M(;yEOs<Xb6T4D;<JCIc_w8eG9*ri5uOFF%`9EQ@<fp#58|uHZ4%czyQn}yhw}Mf>nG5wF)n$G&x9RY|`W4q}ayopkqlWrtWyf_dvv-Y*_s-AcI-4yM&_7GMO5SR7&x)_bw?X^TR78Kxk4O2is<>Vz)=&D-Q1Oi^Em8i$d0B5e^?Li=``_{9NA&*|FVvs11=nlGLgZC}M{*uUH>|sz4}6h_2j+_JdM+@sEX3a{^xEgqKY@W;k^i0dx#x*lE>oQJTeU#=`Hy4XYf=)|xkgzWH=!Zg6Z9>{Mc&PlM_TUy^yl#y<jKPUd)@QF$mS*Y3;P!>;g`d6fPQob&j0uaSznkV<ItWDC$Y}a9_?|@AFW2#c<G<IvEsYt6K7x@<W-}wDF2-=jyo~CjCW_DK$PEI8~wlRAlkpPqWF5jz36`}7xHS!A{npxaevH9vGFqQv_Zq*&wGaP7F`ngRQO7Q`}NW`Jdu8OhOUHPb}g<;|26pgyRZcJe%2CepuMZoCm=7o;&YicGCychZ)Kh{-<3mq#%@7Bw;KlEXD#yf@pI`n$E!->Yfo|g%qf*+J*M}{f#(Cx^TvZ%=}+6TbFv<H-S_Q(o|FD`o<1$UYo0WBKa+m5j~*eu*}_D7madh4(>6w-{L4&ePw*)`U;nFOynDZy*QQIqITK&(bk84W{gyJm9P@q=-%Ngw^Ne`%qqI|72LBzN|Lg_-K|V#b6<@EPfc&g5S;mpQK~0Z(v<2o&segB}tQS7bGu>BXd=%R+zL|u1K`VbTLVR;E%HKSR>vg6UpZ^zNomemu$K78}<{$g)Sv%a%S6{Mzo0Km<3iWi(kN$KPTjK8PvopefcuDSe`jH_X<sF6Z$+}(p7$UxQtOD}($X-5I|FzwHyc=WiJYf6!5AlsX)o@-Z*=2s#rVqe<Z(2QEuP7g^GhPOvo|%PFe#SbvkC@eNZF3*L#-x*&H&^X|@1F<lUsg_@)Acb?@OwGY51VUaK6+5fqr7n@`)tXR=|1A?6>dm*XZnB3cr)J~#Pf8(JskJmLCGiQyPe`|&x)X()lc@6zyCHH<>zRqKlrHB>kJ$xzH5DDOnr)ec8o+lkH177w2EIWe#T+q8+$8w^uL*-=FcAEXjA=N(w}*Apng6dX{(0H_;T2e;rXUOGV-TweHmYR#R&0T_Y3>Io5=s{53pX2I*4|z&WY#iPTj?KJx|$EHsF5utUY|L)ATkgaUMxQ;%i$jV4R-7deGV18}-|Ra9=yOANjL(q4bCAKBb4hK%O+3B)&O(C$8_BoG2f2bd!5|=W(oS%@1qf7vsFPaRTnA%`<Ou&vSeDQ^_CuzpiYQa$GOz-JeMQ7`=LluN{7jJdO#&{zIL#;_Dr%qWrx(vd?CIePIK}?NiJ%$#IfD_UV1a*XO=L9?rfd`J;8}it-P2<WHtO!BYNR)(sx{yycSQk0av#dij2lcJLEREOz%@`D2`ZkN!$`9_9U7;C%1>iTvsR`&#k2KVZCAj{M0Qx7Iy>^i#)?KNDMtZ`?YB{F(Rz?stD*lJ&LmeIVw6%yqDCZ%|u&?b1oK^I$*8AEWGySSjCZI(%PmJpay*fX{sfE!QGk&&9#wyPnI8(dF?y@9glqhaj(JZNv2$eQLF|yHFUeOJba?bIkGE;m00@KinJh_pC<ZYpt<ws_iO-`KMfk)$V!adX6&&9b1KV=I6fVbId=N*NU$_Xo~(1idZ52FrhR2ve=KbpBaF4OozPixjxZz?3*j)JHK5ipE+;X3&%_TI2LXdUn`RV?YZ+1`&WI}taLwLO)F49>K{B9erQqDf5VCV$r1{`z!3QJ9gF09(QU<d&BNNRH<*{|H-&$<8_KsmhWr`lEBg>;_U>30jlU-O<J@_7KE}&J+}A=gi?4TEBEA`X1lQ~BCCMLcP+62eQX6?SXr$ziS#Y)NznT}$qCX3+ko<9^c`Ez9uKh;s!CcIXF5me*`lm--<kj-u#W!=lK>oBVg?TG(C44?NX+t()JyobV_LVcAM!B#Io<8?mw4zzC4`2SW>}PA+`@)~+i~Q-kVV--xnbrG9{y4MrnCE_7%&a#s|6DJKdR)(mQ<qBq7=<6rmGYdgjA=b3e{4Nx%tan>pW#A=dG*|U*ZN0GyAAnsrXqaTbJ-vFC4U?%N{X-L9|>RYR9f1(?!g>69-sHk3s-T!Y<gi1@(IuT<}V#3e{8-d#Mjz3_qeawZYH8U*C+bJUC5szv-{U`%OA7W2g#F9KKGYg&k-))wco4fE#p~!<4xq%!~l=-+RsP1zxRBndwIQF3tacO_#}_|UC*28XYcSR?|ljVvv|igkK?-bqrS`LQID2;G5q)zTRrOGzM`w&KKbMMUdS9;-o3o*x)?te-RN=L76Z|rySI4ur^_E)be?;8*YmPtS-t~_|BY`f9lqA%xSS95dmC1GwBL0f8TfFs$8l$r^~jS?^>AHe-cCvMD9`6&R~~-y4`f08ueR*==pW{@ZBSP{A8zc8eOyak={d&0x8$eGx8|pF^$+4(^W4$@=tB4Yca014<W<yf8ArC#0gK$*=^A%hmq78Y<J56$F3MZRwSMK8_||zqJMXnv%3J0QvqFgY)_KNwF;0BzyyU#`Kz!>wX8OK{Z<+UO!<sCSzgy->XXFI<mU-2A{Cn}O^RxMGIehE<e52_PqLz8y7I9g8>wUo}Sy$c{{l|U8m?^&XzGF5{KzYl3%D8_h*1bPn_ea~fw6adL-e=7^EyTCpmu<b*qrCP0-nI~~gJqrIj9RePeSEpr8}_$Zu>WCMpP19a#ka0=?D<x~x2%iw+=+2GuID<+X2!@qgmpcpr<BEe66^ZyT`YXdde8Rcjri8}q4Q2<S*KgqlSYXyc<*glKih6>+2Wr6u64LAlaJ(ubv<v`2O?iA>wib_9q=vB5%x)U@Lt;T+@armkNPdoDQ2!H^oRBNDATTO?&s@zo-%&D$^NrEe~rn5`;6szR*#s6JheO*>rdanw>(Gd+Zy0FmgjxPhJo-c`v#5yehG41%YKMs&Uo>y`zrSKyAnLw@7jmyvud~0W8LR@lzESox9k_$f`j)U|1JAV>n`n;@|JxqXQfvAq&=2>GvnC;@vZx8&P<{E#kcJ5IsE_J@7^BQKA~e<twfAd&wWToY)ezl%d(HEd(9XBKlXLQOw+wRu6<)8f9nI{TlT}vHA@b-pO@?Xg0cL>0r!6X^j_n*mLz|-yx%cqHcxWDUat3FMw{{QE$`{fB1V#X{h!|V<vyI`p0}>|q{bgN;alF@>KC<S_wnm`Uu^cP1mE&LT{~47zV-e4;i2MNe{Wzv^fk&`ez%|}%@p7II|rxVFXCH&r(v6N9`##(*J1c(J?MVjUB62)^5lkZ`5lXvt&#ZF-`m)Rgo*F*yPXh^Unx~zHQ}7$r%p}NytO=9-!QkIC@E9Zv`_lq|3s-@)&JE`l&V*)^#A>d(od;v*qa)=8H&%O#y#pe>R$3W@&)RC@&)omY9jd}`2ck*`2abIx{aJfK1kh8R{AsfAUT<#*raYEo8*1e4di{~J=Aq%rEAE0$O+UH<OFhjYHXn{qplz?BhRHSAkQU#L;a5Y4S6i}U*xgmfz*-Yf#i<V0pyP4#?)@)#^l=69%Q9G$+gLK8HyWG!^leek{gj*Fci0;_9M3;cc2a;cOZvS`;$Y-cIq&)ojip4HF*em40RHD40$T`-{h&}+0=RD+2n=PCFF(V)zr0QrMt<i$-Ag$$h*j=7>e&|pU2f*hGNYNp*W2fLh%Fs{T%rL`4RO3`4Ras^&<H(`7-qY`7-$rY7+SmatiezS!pskh5S21@g=HBzC=Dx-A6u8K1<z0K1)7LO&}|cC!Z$&s(l`NzcLgbXDB|#P`sYHjJ%%w14Hpl>Rj?nvO)cZY>=a<W64qE*3^OI*5n{+M{*Fk9JMjI9Jx5PHn}*t1hp=?1i2!$5xF9{2DJrQX&Z74avg@^hSUz^hUBKyP;ygpORAmRlH8R#gxr-pm^y|$m^_|3l{}t2gF2f$gB(L$NRA;psH@2i@=oe5@=o$^)Kg@ocgeqz?@-nFyu;6mKcq^PRP{}b!c^rIrfT#xj_1M*#l=#iBsCp14Oyug=jr%aaR%xmvI@l+sgKDj6hEbRnf#Reocag(Ir#-Og{<^<@(c1ahT<pGOXMfyht%`rhvfUzv*i2azo@6lN`EE)MZV2Ye4Tontn?W9I{DAkcujRukCC0^qtx}}qvSY-;>FY-$Vz9D7n7$`4f1sIC~6dW6giyQnjB7U%TU~ap}0Cjae0Q~vJAyVsX^qT<b2d}WTnN)`N(;wCCGWmc^Qg}P%Dy)kV{i*kV}&*QR|SEHY8UfSD`i~S0UG=wj|di>(s7fog7RZOb#Z8Fci0EDDJ{g+>4=jC`0jR>Ui>K@-*rUveFpxH1Zs(gFJ`4oVt^|oV<hj8+ix$7wR4IFXUU)59C|q_f$0pz2|4exfqJ8Qmc@wk{hK)2(=-#3b`S<GPN+dGPxqP7`Y-jz-^8TU??s@O-D}0xvT_3adB!!vW@CZ%}7?N<~47AR-A?UoUB4|R_Y6~(r089iZgp56lbD7A*)cFp8AliLUCH^eX<J0Uev$HN^g@@DE`P${15dyS?QnTf5>mN&vTsOJYLY;)Ys%%UeKHj#eef}s?6UE#n-4#@-^}i>QV9$ax68DtaLFsmb{2MoxF%Vg*u8ng*==ZP99F~Ol?c<Om0SPKyF5^#!y^}TAi%4Jh>FPAVaY)wJh0}>_aU|_917Z<|8Z3L(WFdLd{FgLe9=moSRyNoSW=NElu_#7o%1pE3HB<M)s%HB>R&qP<3(z@|V<L@|Wa5Y6v-yT%X#WT%X*Wp|~Bj3t4F|ayxQ&hT=%-P;w-B1a&ld1bH%b8d>Qa@?`QX>T>cd@{bI~o2fg<o5?4szmQLoZ&GiOZ<60p-;>{weK;?xx!8wua#gYqxf-<*xf;2#+Z^4Pp}0+Ibf$(<L&%}z*3^dNR@4U6hUA8v(;F}p*QZt_*C*@L0J2UlM=e1v!TGuzLvdM#;?i#OdufK^qEv6PH|O!948;YhS;<*BcNb(R&c{%kpPGrBpInHVo?M9RM@>uiBNw51k(H{sy9hrkF5rbwoR|6!S?L?HYwpg=P#j3jO%5d2^!hxf*JLPe&QSanLvav8aSm!uvQjng=iq0>uNaE2Qm>Jf9wA>PA7&_CMU5q|BG0ETBF`sJq)s7EBu7w(lOxEjsGZ5J$hD}=$hF8{P^*!@AQzyPA{QX%q!uLSBxk1jk~5PtQhmr7$?2%s$mz)GsaeQMvy;=4GcgqBpynnk^&{sX=cg7U=O-6pD7I1k$u@FHY6WshavAEE<TB&{Y9Kj)T$Ng%T$Nmp+MHaE{1vqw`73fKYIkxcavy3Wxeqy-I)WTco<N;Uo<RPVI*a@*c`5ZrveM1urR0s&ljM!$6AZ;Ss5i+s$Zx6d$ZyHny`XB|SFE%eIXk&JwK2Imxe2umxe2)~Lva_c&-aEd48?Y8PjX*sIJGCa548uiC%GrT--8-T?m_NEZB6b(?&$UT-qVqxxFxj#S!sQ8OL7aUPHsW2M=eKIT9#aoT$iD^4z)D74%wetl&rKM*`NFcLvbl;KC;sM<Wl4^)I#Jk<nmNMa(QwEY7ue;awUf1FR2B{O7oJxB-fw@l53EgQfrc%lABSRlbey-QNJQ9ZBJI(jogmhmD-Ekl^jNmB!`hBr~}9m<o?vb<o@JA)M4a7<RR1%<RRoJ>L_v)c{p_pc{urNhT^fQF@ZXsI)*%+JdQewJdQk?I)Xf!Jd!$$Jdzwu9ZZfU52X$u4<!$zMv@1T`%!z5`;mJy6nCd~BX=ivptdKs=k@NuP#nxqT$>t1R+@uco1BfI_@xF_YYW9nuaaMquP_uJq8=tIT}3`bUP+x#UP=C*p?Dm1B6%FSH#LIXo7{xjirj=;nOcinnOvCq1-URe7qtL67ulPdlk81SOU+D9OZK8>)IPl$64t2cw9o$(r=g}NE6qesL(afZoRyk`91`r6CQsV`>A%?c{LfGg@%Rrntl#u}?d|@}HK}!ddI=s9oL;phwQ*_Wg<hE24b=V%!HLr>'

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
