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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_007.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_007.stl', 'source_sha256': 'b845da0b78a63dada49895e25a57a6c06da15fd3fd2ba8fce4c815b8120965ca', 'input_faces': 576, 'input_vertices': 363, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.007984965108335018, 0.06696584820747375, 0.06490805745124817], [0.09176486730575562, 0.2632964253425598, 0.28946971893310547]]}
GEOMETRY_BASE85 = 'c$}r130RJ4yvE;Tix6W;$VVt;i3r&~3MEn0q%3_&vWHBTL9cx`_I>hMvV_SxOvGnjTErN$Fy@ne?8ZK3=JfpUdyYESIoEZrbGokQx_{r@|NB4h`|R%<!GX3#D{A<urBw~>J!wvDO;g2QtEeT$ju|^7CN`nb$Waq)Gzan3&%e5?dst9#gpHP{ed#(dHX&w=tB=98&7hX94GgY>;>U~~6Fo92e$2pF<#&!Ao)DYwCk&1r6`TLr&CA=Xfx)YO1H)v)|M90({v}w4Me6PIRX4`$RjPIK$yI8ISUgSq`fbHGTJBzw-;aryA^xs9;#+Lp#WziBJ6nFA+fRIRvPX_+_7wOBr(Trr9cd)_^*Eb3;`=O@c)g)hwo>byH1YLP8R8pK>t)I3dtK&Ae9@<fcj_s5tULR`-!Kc;@92r^cM6&(anZB($@MRqAiibXUGcTnE%wXzo9`4~a~M2dG$l`bt?n<#-**T6q(6>|?wWO_ps(M%eL?&iosi#m!~*e0x6Ks)ex|gKUSc}@fbj>!kAE-m#?005mp(vyUTh-YvtEBDzINw>#9L!aUY6gV+`mxb8%;(0_y>~Ta3^|^_{XOlk?&=M%XOMNe1PB4`JmLd&INg@#C;`k(@u!54d_$Y&&~KwzUN#;^61wmiLaO4`mN--wL;>xnC<Xq*ElTSPr3$w&qL&C>ysh=*CA-PI^K&VKIZv($rEG3c$k(Wz83fh<Hzx(w5zq$2l!KqqaWkSpnt7{mWZEo1><wgPRVDUH5-1Nxl(U_0;yLkw;%q%^%z&@+e^DypJ#}#|C)^aW1ArVS@)$9U;2QITkXO%#LqQ~ua`E-I5EDA%q`@1NtO0D?k<0&kgxg4I5w8}QRanl@+SCq9i)FP6KA2`sNJZynB6h)8=OVIxST@#!1#0Wdq31`IofHNe7>?7dGgjGPp8rF_q#~{>K;4L&Mm(eUw``x=8LC4uIJ+e_|uP{ly<b6iu<zsjXZOg9mn^3;d(aNEf;^m4!KT!!qh^(-X_%|pWVt7j^FHcLaC|z{oF$SE>Ee~7?3Q!X=X*_nZ94*we2Tx{g=bw_w6YCW$H5VQX$`C+$qUhEe7-JfC>41cbqOb-V7^;!GF^N*E!o0<92)^{An*_{2RAti*JpXiv0ClQSV<JvkUrK@n#3nPZuP=c}_O-ti*lxsc=?4mwyj`YIn?+&T}Nc`G>MA;M-xHX);jiv9|9dzW)3xsn7H#K~%3DjQBP8QE%rWlE-*27V$T8WS;6%+86S*gL|<q@4&ih3R#c%#5Xc-_1x2l_u7W|+j*E5&yPww8?)-K6kUyV)9~YLX;&?+8GMhQ(eD0VU>t>ptwjEnm@i(o=-=Et_!awM+;**B$k*E3J5z8zntPXBC7*vre#`H<(r?<WR^n^(7s++%OBTxgSx))Ezc=b=!SQKM=>h+2maH$vMi(%CW=Fyw942|R(fy@;tmS6Gw|S0r`vdkz>%^n*M-P?uHw-hPJ?_4QzxSQ2KYCoLeQ58JtEIkuBXB<+U1T2XBb--bJ|<#+^<5(Cjn$;Xf9I2q`7u$h-|%p!_}bw(sn>Kh7VWY71pN84k-u7&^r!i&EXMbc_SdUlm-aE4UDk*n`T*^gupk@b$Pd2zdE`BlA@kdCDIWd{7ikA$M{l`a%d(m9a|Up|N=HAo+6sTxQjGJ{9=QJMd&SoSt6_YmY{0xec^UDGwqf5)+KKDjasz&gH%AN3Q^Vkw$m9P+uE$h=CdTLYZfhkzBwf}GgU=1@j|aWP*Kb!iB)?zzTW&#Li`;^J>gE%)--H0f`xZqztVovo(A!4AuQFfS-`pboQbAw)`=E?_-Qg<wv&a|X8-K5ZbH+BS>{Hg;Nyw8^1nt0aXgM<vd1myG_0}+RPHsV8pI=7q%Q)jtoV(_k5kDY8@|yaa(GJ6R!mso|)<fgYTWE*x9wW~o53GBMy>bisTKs15P3zsz4pC*+N&N0}7$-xgOaJH{9O1uBlksWkRS)augO>15K12JoEr$MG6anAuqKre+n)@=|j2S87YrXox_c@$}@$?bCrx(^MyG>Z<mQ+|Teo6qYzvVI6$4p~uz_0X5)+19`8un|acH-;N$r!f_0+26Y9^%`U!Z~Nh74*-QgNSdiPWna5Xpie3e+_<-W#StGUD5uLw~%M+Ox$nSX6&bJ9wUCqLgaZh1nuwq7V+u7pgrpcV7_Zbz81ezO`Lbj-;v*2^6bUe@487I)9Y6`_<aQ8PcN16toPB;k429lzD;ec=l8PV$G?D|SPAR0eKm~FkdN@whD!SwQk!C5Yg!^%eqY{2;;rHB(9VAS#n;Qemi9O1ltnxLJ_Wx254i65%{bpBq#{qKqg<z@|MHwd{-~ZZKDFBw&^}=Yk!M{c+}FST=$MK4T7P06xon?R$dB-o_P5qf#{T%L75>r(GGENB*E-#1gZzH7LGqg&&SSrbwTIv80j|5oZ+qnTU8;z$6`zE2-IrfU{g!<}@SpENzl;pcDdg9Qka1<X8OP_Tk?@z^kajZ|=HPm&&p^G+j><SNmY#v}`OhNw^Xp3c=#%DRJv_Aqd6GS(UQ5XDa=+S~bj0@<Ci{x{X<fA2kTZzy8i;eOeq?VUzp9OV-*BcF+O5%b_&moNLZ;yQul|Yr-@d~7`J^(|`98L0%o|&*pOJrHUSySozb6dq_GMqJC*OPq|5l95Q?r+i#G7kYg`f9S?$`9s!#(KVuJAhy#yZ%{Am;+ZpP}Oadk)d<6L22*HOh?sEs624Y?X`?^Tsb&ub=Ew=J-cBh5Wd?@ZTh1epUDqd2*U!|E*OE^-R~{58W^AVDhelet9($e&8`_e@o)AJq3O3VRO_sJSDSG{HtBKuO>;@KV#=3e&;QW&plPKFI-y;ze#_&e{<s#dkXnCTFCj*H0XoWqq%Q{@0N#k)3!o(AwTwz^p_zv9^<6+F5d4N$)o3fjqC4l4)M3g$bMuDtcLl!FAMS9PmNd7u%5eILHv;wGCs`}hZOSlK9SPz`sR4FbFp8=w-o;h=f?OrjQ7Mm#3x;s_O}*2fpOyV4*8#-m;G34z8cqG-FBmV|6K&eS*b6MV7|DBuQ%<9^{tvg+TYwTQhd$7Ip%e!BlgXg@$i=~!t>+(;Qa-CV^(8~1Fwx|3;LE#yHRh+D>!$=e1Ur7zLx7W@my-^yA}ECW=Z>4pO%sKF{gbC|JnjsH_Yx1xUVAT;J>bOq+lLvLKgfX4p;{+O~t->?gr}Z{#fd@uCvQ2=;!B`bFXDbyTZQH9<09}gK@n(?jui^i5Q2idtiMS@fZBcZ!r$$zLk8Y9wj$nUS!JkYrUrC6!M$tGHxx4hKX+oXeGYp9EtI1&BDA`9{@kRGtP~d7GnIA=>dP|dpwsltcN_AE0EuC80QfCa;VpNEBx5m5^u0%<NEWCz@N|q?^Qz5(H>hb)Bhglxd}D#K4H!c)Vs|M?XV#g`_A>p@SjY>eO<kbb<`NTS-#Kr1G>+obA|lHw{Xr*dW7eOy%F%e%Amhyy~lG|(V^mNBW{UrcomXe(AOWe$2nokQ(RB*PQ-i8ka1$kwBmld-a!1>?Ral<`zg+EM{Xg$vcIg)ruQq5zrlU@PqxbaYdoi!pMQjZsEw>srr&~aP6!>iMe?O@l>0P}&qckSX7P<lV=-T<-N`8ETk6c<bIM1&SJ;>$zV^piys!B263#_k&cgQ(!hD?G4fP(*g#Y*h)}_A_rM(U7uEBrySnku3mWuazlW)O~7>o0scWI2P+!wh1&r)Rkm>Uhkd$JC15uf@w=0k#>RnRxud0@R7{SxCYu|kUExp!RF1vAI3b!S8IwR+)LR|ho5Iy}l3z5~u}7Ej+3m{$YgKMluu^vjWQ{?cA<K>i9&m?ul^G2UE{z(4Q}o`ZZRNWbZJXW?%igz;SVZ|vK5ZMI5%BWoc4`}(pT8=Pv0uT{#$^Ti}5v|C(%_{UE1JeGv<Qzr%fq0@Me`lhDbpW$IT{9RetxBmD`=7+A`LcJxNQ14Ii(r)@zn{A?16473HdFb~lCEy!E@Vq^=HTplOHvE{6SZDHLFkgNMg8wVt8ybJSkN)c1OMGp79h^@_)x<gdP;bQBW~04EFU51ZTmNkZ+g~phE#u4j<w*D+H({QvUXOL_aRTy0;oM+&@ej_A%a+4G(Fg6&a0<=~;i<^;b0?hlu8zcW&-pa?!&7Acv-13}FE|5#Mi1-<&-&v1-$^U{P)E$WNu#kI47S-W{`O2<NBsBV8~obBcMZpRwMe+Mley*u@%2Z)VZGWk9OtsdQ^YrFc;BJ*i<a}1ZZiXUuAD=?*Oz1c88a7o4%p$mIO}(;(;I(4e6R7?zwejEb3m6j;#;g<$RDr}@4eO)-yyoc7rr0d0P9~=b@BDTv7YKrQ_)|=+9LjHIpkT9D&yDs_Xxz7t&8zDss!4(*<8dQZ-sTIb<u+beSNwI&WodZ;+*g<8S&TpV%!XPBIDc|m<GQs)_qHJ3*KWLJpjLF2IlGfdzc^kMffEL;5}gL$GHASTB>|r5H0s<Tu>F`KcRv6mW$3<CmWu{`q^VJ;<<lWX1>Am*`P(K7>Dz5j@kSO&v~Zf@RyZC`#aCX`#R_1J4M%~W52kXjPa?Jhd=c%xeiOwC7A_%y<;Uj=ZtBN^=8@#_#+PBTr$vB?$5Gj8S)e>it|vcJ=WEGSK&WshtGlY@qX7@Y?tI&wLsPdQ}vx_hv3rUYr*62{-y3-`MuGrGUA8Vz&Ru%2K(%mYKX6Q3eUFzDLB_3>45m~@9_5y&l}PXmZWg_Uv<Sk7j+x&XM9J%A65+Ks<q|Nj|avezt?Nbe+L7egX@h){EE)fjs}|pn5SW<;UDWRzO``(&fS0Bfq!=t*01=q3x#~=et3?maS{2uzec^;c+aLyuZs0}dE9Q%6E)Fao9uC}Nqz>u*<+lufBJxSzFO)V`Ml&6-nZ8%hkp3BlK9%T-qPR37p0LeyEWqbY{GNUqY#|O4c!nQG!yG=x)a`4F9|_>m1(H=Wp}J+MZyv9<cIesiQeKH9y+B-T=P9Rr<Lt5?Qe)Qh_A&oz<3+HMf%J7el+5H_r*HmxD@wwY&QH2IcVohoHxyDP9YD^SC&SV@ce!0CgN}I#(Cvf9-b?WcMxA=9?l6LnoECKpE=3%kiIq>>!8D2w0~6>@ikL2uJ2t}tS2j5BfjWgXrB`fShvP^M*Qe7%;)&is3$T6@vm25-S*#v_syS$!oRo#f7h!}<w7B!e^)Z!wMu@Ie?0PkJ`{gPyf;qrS^oGQ@zFuJjztymeEh>r#M^pf{W-cF{ZjuK{C~_c4h%~V;ymEf8GnE6+X?G++0A&r?llg7PttzEx)ZYo=jBS%5I_7q_WO&kabBJ^8}UirI5)g_j&`#(BYxCcygxCP!~4{dci@k=M?1`~jCpb59(?y+c>W*R3g@vhZhVi=zr)@*kMZdl4S!`-oCj{)#&fef_J8f&T=Zkt2Y9ZXdl38ZjRZV@jmzf#e2e)<;QV>U3H>>$DB9`RAUs!GTaWjS8J*yJ3`6^r?1Fi;dMf;hFR@QKU&K0haxV7c3nS2f8`t1HV!u`J7mh=JAG5_gsI(S&YIeeS4bY?>L(Y1{7jZ|wzx@&8)(`uVHufFXN6rgNfV*6;?&FK~amr%3PQw8c{Jd*8r`kKBo{dv5PTz#09iF$u`&a)B@S8Wre4ZJF^<&I7_%|ox@4IQGWc(OH_aXnb<8qzWL}#4u&KzQ%)`+)M#q;jubi@Z<MEgvCj6B{Mh~L*5`$3~`@E&X1NyK02iTsDUVcre<iS^>VWa*oSb!deZdHy_vzeCjs$G9tg55C7bjGI**Fy736z#m-|&rNmL;Qd6b9rl~IKA1-{t6<;m=?Z`Ra;!(O-%Gn%mW9Euz5(s*@KD;-QnU~J%4vAdKcN}sYeH9yi^L&#4(Gfx%-D#(E4*^Vd%yVQ`2PLL=zoJR{0~pQZ693dU$LzJIq1G#O+B({nw?fr8x&pOpRg!X{rs!{{XbzD((HfrPgt6_@c#e)6PEj`No+K&v<=jQT$)^$+K#NWEx9h)Ky5`fkZVwzlWUM2sZGd^<cicr<cj3asP)N8>ybYrm!vwAOOkD<<;gbWHyX4USrx@EsJ3KP6hEUDC99(NJ+%s16~$%fH6)iI*P;fHYmqxp2a-FGyHkgdyOaA;hmw^JCif+WP~*rU<et<Ra!+z7i{d_16S)sLf*MIy+K(K{xF~7_If5}!)c$0p1ISV2U}`j3>F4BNav-$_Igsp|Us_Q8sXfU4<REG|Ifxua9Yj_dOAaIVqV^{DB6nj^>__cN_9J^z+mMx3BYTn^s4q3J1NpHAy+wXZzRHrJmU$M%$<!TWrE|#1WSu&etdrwe6o*p7$)V&9EQ<Z|ODAeSYB;$cc|3J2c`WN5&!TuKbq9GV`5P9+>C_BzIysAam3)=$lf|Mqm--tymwcIeo_v{nfqImDfqafd@hR#-@+tBW>Rz(ajpQTbebhzdedJXviYHUQAWtSou_%tnFCo+s)Gx>*$Wy3`$ctF_6c)uRse8#Q$!k~?ucjU(uO_EbkCKnF?NX`VlT*nXs6UW5kj>N^WTiinmF^;&$<wG`k*AT9sB_6mmynalGpT9hndG%BiceFs$*0M;sdvaq{~{|bVgtTS{)zgx23AG!HR>PaYvkk9`{d)~#Vm@iP}M$tg`X8ar`9DaHIP+N{Ek|Ktcv1~R7bKZil0&|l2uXsJM}ZN(voCV6yKxTkX2E9m#X&NyDW--p}rvhLjIZhjQle>kNTdRM}A0E`|d-2R{WM)i>!*`vh+HT%aYxw-N|m`*3`aar6J_j<o48_<o4uF)KIe0D6-OEveH0uCvr=wFS#Yz-R9H&=gy+IYJMq2b)~i-yOMpV{$w9=M`{qcBe@GTjI6X5xeK{7wHvuJ*~p^Ui|R-ABD+vM$x0o_F64hSsM-tvVNraYdX=p74EZ|w0E^<;)MT<!ojjX7iW*NIMGj+8>`x6P`;(heJCK`_tFtIJQ2odTa&7I?{#u(waozmlM(sxJMD9i&K<!5!K%PV$Po6|xNL@-^NZw8ThO9K5yqkQ2nnhNcOFlt9OTA21dVzeFe2jXItn?K582LNu5wg;K<nPE^sjJ9a$+K7#CsHSq6UmX(C~_pZEsNrI)Ch7rvXAy@KlWi!?44g+s77iC*+>qcjvxn+`%<Tnm98ZBC7Y;g$R=`c7R7_8tI31NL#e6cq2yuI4dh|uII5W(NA6FZM($6Jp(c@)&Lqc>hfvp&hmaGfr^yNA?bO?3r9Y9klb2Dik(C}NFC!18E+!8qch%HmJhTsWF<I#qav$;v>T~i6@)j1wC#mnqC&`)Ak7T7!$(iIs)ZfX6$m>}Y@1fo!?;#(i-X$yjg?yO&HT7rm*W?sx9yx`)pZbuzpKPJNC0odssA^BW#LtRvQr*a^DE>fgO;$zmYYjzl3I4u4xdgc!wG+7<*^b(hY)Af6gSwMdQT&Knm8^>5U$swrs^V`o=qsx7Ur}Ajswl2R&xc%z+<@AV+<@#&?Lzh@H)B!Ul-ilxl-!tVBsV74q<WESlI^K3WEbwS_WZ2)fd;)!en7rRJwU!lp2(tjICVBz=_vAWav(K~97t}#qS&44Pj)BQq&6kjBv+tTCs!bsWKmp#Y9N;&+fi$i?Z~C5b;+g3rL|9cb7>aE<?>5;YJI93xjs3F+Kn7Uj-?JD$CAfUCy~dIXHXZCXOK5hcaxQ#AS*pfR(g!A^gFWBt>jJQdDL0tdE^N!ibqlt$s@@<sgdNK<d)R7<d)=$EQ%{p+mS1gt5AK&RmhH1Z?Yq~vi50juFRtNGfn;XLugg13%M%UnQA0Elj~6f$o0q#seQ>xP2`5;2Gri<2IS@}iW^Y}ksFa4Q-_iplbcY7k(-b`sc~davIn(4*@NswjUg)?LiQpzqb87>kvmhjla($bD;-SkOm?MqCA*THv`>4p6N}<9`K2heEVUN7EV&M~4_WC7avgFT>K1Yva(foV!PJxFVDdm}CRynr@<4JA>Uweyaw`_a9jSZB9m&4b!(^pjlYPlus43(w<j<-5$)A&ZQ7z<N<Y?+8ax{4~^(J{V`Ag~t@|Wc0)Ys(Y<oPU$H&fOAy_ugC@1&L^tD<-t)sC!+;&oKDf3IUvJeB&0Je53#`YZY0y?hLd;_msSHFW{?Tk-<3mHLXTRPF0lepXzZdwm0PadLI4H@P~w4z(G%4!JgqVkc@-vJ<%iwK2H@S)<k@Yvd;y)Sj$V?dwli6z5Pcl5@z@sT0XHsMV+w$<@dX)Zt{Mfn*1AacT>4adI&h#kN#;vMsp?wI;a;*@jx-)2$1upWr~7A{A}_r~iWf=|@*zD)b-H|LZpk|JkqLH_zth`p-WC1_u^X_mqEeMPvd^RXdjUAK$<+(E'

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
