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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_000.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_000.stl', 'source_sha256': '30bb36c35e8d02d9be2f2874f9f1a2c8c7dc5dccf6d9c57337f50b1a0ac1e3e1', 'input_faces': 612, 'input_vertices': 400, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12965771555900574, -0.2549951672554016, -0.19968190789222717], [0.15020786225795746, -0.06778380274772644, 0.13382208347320557]]}
GEOMETRY_BASE85 = 'c$}r22UHbD+s6l6M8Og;CQ*E^#)=X()~JcAv137qB9;JBq}V_#h{{^PiW)I0)@!WTVlS~>L=Bc0lc>ZLy;d}~S50Dz@w?CS{K?(BZ{Bmh^L^yZ`Typ>&z+r}otd4T^(4T*Xfbake^piFu}0lgO$R!Xhw@gVq7sv0BcevUJ9K!mn<~dX|3Ndm_v#i9;-*Halv<HdBO(%OwXoD`72Uj6Jxi_VVTnnJ;X^}*B}PV(-ywYPh$x3YA|`xzlp|leaf1f+ERE{avy8X=AOA`@s$g5O$adJF`r}2rNbNE9HLWS%d8~`CiddGCZ;KnkzFKsWeLZi@X7aVs;o{#PypPmU<|3D)uC<qPIwgt!rO#%guhQf9lG?(~%XvN8Nqk!9ZliB|@V><VGKb4i=RaJ==hYiY{Nl(x#&~T^ZSfDMa`{&88hl<`$!g-eM{)VunH;_@^`1riaT#*nIeny_!+pg6C{5~lv^Jkt`Bsqn>`3GDT240Nc>6UE@dHM%uZ5K6cuR35<yg;4yUnXUgX=To;$hC;ZZ79dnZKR=3A+zVIeX=L^Ss#CdZ$Xf&n@=#*P>=~eX>&|{+lyg&#-5eIbMC)N8&sG!R6bRb!Xoa+Ee0JUXgnCuP=UZ2Z?XEl;c(I##!utuZchIJ1$=pH0Sf`o|UDX@3(O|>fyH;?1wBl#PL`Bq#S#<Al9ng#lPDAOK!LDh+Q22pq=<}w<Z2X<K29{{pzr<?gVhWYM$Pk{II0*;>Qi*cF+=%xg6`3y9c?P5x+?}d9ySw-?u>g2aTjXTNMOz`QxvN@3Tto<MwZ*K5MTWG~RdX^u_FJvu)z%cuG55U)+oRoM85CWh<ZM`kWf~CHtWs;zw-yhU0y<vv2LV{Q&2mO_h53y_m`6o}R$I9^Ya=m*YKfFSq}uK=CK6k#>01C7tv4n@c&VgT?<bo#WN6>f(2=BK4e=ypQV>_`3L;(xn|v%uG9M@bwa%<v!*FP33yO`4`tiFO$Xb)_1mX`FhD)?5hc3QhxuTT#l{bP4WFtu&@2_RN^}|miiT3lk2@>U&Q6b))K$oE~!`h+uT0N@>1?=eot;sThDy1zis9fsrQ6S{5ySm#RZ&i_@nq*fz-EDnf-j;S?gt-6#q(&9~}AFVWZ#rbI~Q92jsd|!C%1bplA6>`T27F`kD%IeRW%K`L^SerQAmA`Fi!XZMl3kc$~!V>nPWkktX$-KUB&c+g#dtZL5`heY?WNKUaqPwQWU{gM7c-Ye-!G2HcOd0X^8)xA;hW%cs%~r(U;8e^nB{{9E>|4VoO{dfs{}?LOw3{O<X&74rMv+1GnKl<WAt6Z>lRL-FVK;`^d?P2}@h)?JixI_umHmbKfZK4<eW&aX>5{B>nH=QEece0O@gw8x=@4P4%VEP1Y6+$8PuU<dnp$W)1c+a~>Iz`bnN&I#hrTp{D4Uns}hG6#x(<eXghbdBRJ1vSK<TuQF@c(e8FUw&KsPvyGwpIS-z)$(@o@8dE5ELpLZ%OAW?e0}LLj_>Lx_p#+x_VpJVrQbgPY#r;?Xz{}X<h(gW*O1y*1V}l-W97WZABo?%k;Hpll>6Sk#bNIM-787_lLK<S9nP-i`1a)_e(`he59+%v9Ip*4gYy3^^ZD`3t2q9H;u8PxYi?()Vr4EzU3<BM_555ZziL?<pZBLn;>TW;`_*smDk=9K`}$KKKCdM@n$N3e-xj~$Ww~E@E#<r?f0lBJwdd=#&R!<hb#<%wpA7hl<Ln2yeqkHLw{<Lcl;dYU;dZuP*(C9UI!OO~FKame?s7fxlh#W6&p4jRzrS2t>JxO3%hBgQ-pu7+_7FehzVy4h-%sQId}-%)&UXnu!pBGF%6<Q3z4)=EPxARnG?n}F%WC$uHnrq=9=e3bo%$t4;)Bxoy!Lyy<^KQtvBdj-!R1@>+jHLj<MnOqf3#A{nR{mw>xWa>SAlZ9nl^~*uYEe1eZ5|!wDazb9B&I9EB?=urT>q<vXS%KM@c!w-k19xmdWK<dqhh7nIp2^Sbaps(GOt~KdOq%GovEby7=*lQjYJ~EWYo#LE@)Xlld^Np0x810pds3l>4=}!wT`+i61;v+W(JPbGRPo8i=2<O6Hr~N<1E|301`3c|pp*`qxHjzu&gXeP1s3ee}9y?*Ba>iQm^l)`5)^WIX0yXWtf5|2UWbT3v2$+mdVS>s9<@Jo<N*dFkdk@qK4-|Fq1g&d(!D-=k9g@_xMDaXjy3yaeu(_}^B`dC$D$ajh=wlz9Jv(l3@S?ZfqavQ6TXU+{I=c4qRtWVLLS`0sV;XOF_Te0!T!;#a69^YFPm_ALcVq@11Ee821mhPwJyJ4^W|g18<2_D9Z^=XImyQqPD5;(r?>_xHwJzVF(s`EuT#snQRtKIeGru6Yta<Q&(>7ByYk;aolO$6b(h*|(>8ePaK<y0m|E+6m5|TPgQ-b<Zz2zR&M6uTJrjez>YL`?hv3WL&HswV2~q)nQ-j_D-(!#}uAtv=t4vaQvu=Uvocuk|58MPqU=Fj=OT$|EbpwqpzEM`<xK=)x_hn&dsXyh0)h_SKqp;qr`97Abz8L+zx;H`@ZFNuqNlY_<zsaL%w#6&-ayeWz2Qg_@c5NR28b`xWs2(llwb7a-&Oq-rOqdpT@hhUHmg?GLBxA*=+O+*AH6U=j&bK^S+UGY~Oo}OZ<_yWW90g;X0T2gzMZ-Z0f3OeBpX~bg*kY)(KkBC6{=W(?R@GSJt|e<MB$KYolwr##aoLd2dh~*YamokobFXF4wD`+T{73xY^};_3<Ced>9e8!NortAn%EJJ$SygXI$ZS)e|mB`%j2pZ}gSPw`Sx>eET{%(tnOGH2Rv!*E6!EoNh1qd0~H$u-E9@y8g4T1{RTV9TBn8=<DIGzLv34;`Isg-WGQ;)#&S~|Lm)=rDR;+c%0ta7@z!K{NZP$zg6?J8h!QO{EtV;`eoW1nJ)DS`e$Et>MQd|_3dFU@f}@#m60X!J<@pI(4xFPH~O~juD&+44&OJu?+|`oXsNmDjlO2`?dfkx{Lm4nxV*Ra^Yh=5mMzbpPdf5*M0+!Y{jf<7xnHZE&-lFd($e0AzAeDj*Hh~7ysO97mvzWD<F^`p&E#uiLU?_rwfkD;&s80G{?td;5x;9b_a9qKQJz1;G7qupWBSNEJozrKyEGLizG<Gf1xCwy(EMCjGf?79&k=oDu=u9u)Zf18IrX=1dQRC2I>~uW&q3X{zWC<n=D502j_En8eN|a})AQPv=q}}q-|h1J3fogceDiaE#SQK+=5>N<oF~3%U12$~LHeC(eWFhb6yLPY(U16{pSrG#^y>vYj?L>XHT0s4d((Qua{9RVruCk+#OG3uX?>_REtYuGdQ$sirue4yr+x55DW|vpF&P(2<UQ-YF1~3Us|JUQKk}s9N31jL@gd?TEp}Pg+2Y%X-?ojc+h$MZ^J;Nd<b5}~lssSdMe{n-7JGtyi=NN>Et;3C7i_WnWS!n8&Sm{+kC`atnAW!{rnC5+uJQbAJ(saf`e`*e&zQ%&-mu=jx7+CJCf|Odh{S(<S>8vy!*h+kZuWDkE#vxiI>qO;B^8zRSkBd@>`%NP{V+5|u5*9j63%xk%D=Z1G?D(|*Pq9|`F+Z|J5bhBeO=#!)b7{CPnzKJK4saoF-!W1>w8>SgE8!z-}|(bSn*BoiT1c4DaZ6)X}|0)@uv6Fu(xmU{*d{7Htg^(?3>?zZOgYwyy<;8?2CEqYdw~6`{*<G%lIl9DCL;nyEk9u=dc>o!u5SK_-FCW@9*nAm;Irze4Yo?!i};Xy*+?^^ZtN!)g;~@vIYDk_gmpTrr(bF9B<l}2-_Z#DfM>U_s|mD#5eDg+}tyd%QNk(sF_>YH}AtJ@2J`QyIwv#ek~Us%Jb7VmG>k6V?QTpxcKJ%pAWXp;5gHMk@`MUeAE7tUOA2Z|JaXe5ip(Aw6CQiE3p3``(S^zo5p@nGWT=Mqo=H=Ue)LQOY?r3x<6$K=ld6x=W_L)a^E(c7|;3GI{ZAfT<#_7jx6_NF30B1`;b=8zhr$hZF&;Ne|&<^t9&LOGy2NxPw6~@&l}>$>j(SYH8Q_8jg95<P5XrE$MG?oH}5O{us@3PrhQ1Y>9a`o&HI+VHzGK1+W%BzhOw{CddmK4r{ePbsvX{sebYXwnldAVee=F+?HatVZ;Q`9Dd#(%$6C1(`{w;yRj#JS$Ibh_Wt%1NIPM$H?PD$Wxs30MPZIffU=x>lQXMJa=Yx5lS=B8*mesT`tr|q9aDOrFW2^qN#!36R?uV<qZ1&Cj;cAvwD#x4m+jj)(9B<yA-?eul`=<STeZzkCwIQCoZnQjIDeb!84PHl^zZa;Z$7k~IOy3<;{u2H^qm8d2&%2rh(x216Vc-1yLbbXizUh01TKhtL)AteeRW13RWBQ(=e(xsVolM_f)X2ZYH+`>Bo8Owt<(R+wJUjR)*S~j19w)X^_vHIoXwOXko$0%h8g-q0^LHqf{#<<1cPo8O&G~%X^qotUZ^yp*yO{d=8;Li6N1Jp>;?3XPs_*}d)%2ZCmHlubE7tj%C5ZcVp<lSpFZA_Joh07$-B2GhLwwVBMm_uVLgW1{{4S~QyDGl<JLa&5;+wvE>c3WB#A^CZs{4)?-}GHoU%Qok^LJQ%mYeJgn!elWH%rQT%KV+TO*x4-eHYfR-IaLLcVyk?(qh(_i@c8%=6PS{;dkEU>j+C-!TsOnosw(xHIuKuGgPj-n~$`A#q#ppc)PW{kM=~~GgF=;l?&L{gR|uQs8%zX-|FSB=6VinB6;@=dEaU_XPuN^NzPX?RMxG{3)t5pPjS5FH;1o7Z}nuo^ur4BUglL_e%Cg51DD@*kN7@2jv0NMzpJnOhi&5c0k6rvdeL;5Km8YqKRS)qrJ8p{uF<!Ra`p9|t+#M|QtoN?Ylm=s_293*;P}oyvX5P~i>&XqKHkdL)xNZ>S3R>??b|}PaXEplr9I!N!}YT5$(Qfj!5g{W)`wSQ{@(jazHfI-<KJs<`X4p=%H*p9mv?YE?XGb9hCR)a_2Z$LJGniFt(5n1_gyxlubF)P&>V@^7ju8Il^iMe>&OzBp9a+6dh0dsh~|0iVSmCSURPKiX3IQuq89sFTlselnpf#uqpwW9esZ#uGx7{S2gBTtb9vgS9a2ufL0Qk=bd&LV`hmoEeJuCAa<cS?(`EU2VvEn==dWJnw)BVdE#<k9yhXl0m${c?^z|{WzJ5MP{1IKaKK5VbyQA%VDEqdkhTLDRFN+^A`nt*2E~LtN<9+#l*#D|3&-ouC<a=qyJ@P(vwJN`VXqSe`ch?R>q<$4&Nc&v=ihWz}5pq2~6GiP$*jLf_Wq$s{U7nj)=g4|+@Fe-}>3Q|A(N`v4UE43dzJT)<dn~W_v}=c@ocOjJA9gE2o+r0n@OM<zx8ZTQ@B8)|eOrjDuiq*w-{m5f$oMJ0hVPrY-AvvyMt^uv+QFUM!S?Ga`JR@VDD^9!BJp>hNPP4oF4z9@#(tx(N4fg?v&*tS(POH-_j)yBwLUA5{Sv$fS#EFMZS*yhZ-4ee;uCAi`-uB8?!VUOvJb7t6_Mxo{Tq9XzB2i?7em-DoFA+=E9^G<%H*p*M~WXGDD7YTi0q61`KkD0uS&b!EWX?5>&dRZ_VO6}wmz?9U*a_{nI~TLI>P02oGks#<0F~3)F$y0OGy8J?j!B&c7T1odkD8rnA;^8uWqL$e*AYb4?M0a>q<Af_^G~pAFU<l@o{^R7P)f0FS#D}CnLW+9N_Y=$I9KiRJMVSW2Ndy?#f$5ha3Ls7@71}sQ>&=$6_1*um0&+(}wT;fB)%NzM~E=9qA(U6`1rd@I~->=%3*8;O~%#&q7~-&w|fDpMlSSPe7l5Pk@g>AA^s9bD{qR=Yo$Q5kEj8F6Jg$!cCa8BDfgX8;RHgeFseXF4zLDi$we$v>BMRE%-g~2S~*2pdG-Z?ZNH98WM3+Xmc=WeQ;B-9};mjXmxNk@Eg##!KCisH^8qU5kFF*zbj!%#Cg!uVA2e59(XnqaSC)am^1*K0uF?>1P6j!ArUu%HUN{>1UCZLhQ1B14fa7I_JWoNlNJMef!&dai$jZoNnZmO2YVn9SA@O}Canyv2>urmu`je1nDjlcFSs!hu?GDBO!_fc1NTNEo`^)OLwkaC@C0ZN@C5K!XgBa!@JMJE@JMh1v?DkHJOqh27TO*h3yy}i1Cw?DM}r4JJAns*W1yYEG2l3;KR6CN9NHZ`96Z92#z2Fh-NB?Sz(L^FNW@K{^}(byz)it*k%+56-vX1C1y=#Tfka#i>INoN;8NfcNc2}4S_Dj54qO`SjYMpLRsxgO0b9WDA`!n2Z2~6!5d1#4EfR4Ev=^9k95@6#35j?v^iweDS76c{@Eqt-Xb$)&_&)S5n6!wS@O^MmB;wbh<-nvq;Mc+bLL#mM^#zkQ0oMUHMj~zn{SZw05x5n&4H9unXlpQOBXCP_LnPu_(0X9fs^D7SDoDiTp<ZCp;^6XNHzeYFO7x);COrwh2R@EOyab7O8T1?QGVluMx8N0EEA$-L3SJ4l0A2}R4$TKI2QP(Q1TO_IMj~DWJr5@R4!j7w0D2a@06ZUh20R};4|)PT51a`-2F?V32F(S323`m~0$vEtLfdAcy|dsShdwaeiwA~#L`?USv>5I!skh-?dmH+IH~I^y1x#Ak(3k2O`dD4`N7DDeq#qdi>Ia5C`~mtqX*)2fW*7^aVT@=PPoz!3q<)66=4Tj#ei*N$)xe~0xH-o%ap4#zE((3k%{f01)0{#22=fPNo^sA7#7CjCm2)m4o`Xa@9-0Ck4-SR~f=OF}gTZZ}jlgZd&5(%eL2H9aeZcj=Rgs7*K)t}E?%)bwPbA`!(BfcH4{%9v86@I2p%uZT{{p`Wu7*VH2lWM$HU|5Fn<Ei_1l7Q#y}=)W`ydggLMMWkK(n9|!CByiP+d94An|9=3CcNUi8G;Nm2->}&x4Ls&N+d2J~Tl&=Mdrr&>_k>=MXP~#)3(sm2<u#E}Y+pmqG_A=Nw4992%pXb0+ahXq<A+vBXyBaOIqniB~{JDCZnbyi7UQRfTi@80CB}j6r*+g8M*&z@)7W_pY_!o)R~QHU*Q`RnERaT-axbt3j)PN#9V;zDHcxCyC2IOMyvCC}-a$F6{Hfp3u@@Qg7uPJH&-!inuD&0w#S|Imae(;g}_E27Mn)+EzKoK5^lkKpYGW0h3Nr&iRCRJajI&a9u_Gjw4lfq=t^v)sgx+(kMmyEK1#Wq_62(9P?pKM|#VVW;@ahN1BL4oC2KyP5}>xCV+>72SLNZgTNus9^epgSLmDIuHaJ8y-K(gc%Kpt2k!$XLHmM}z!A_-z!Bg`Xc#yW90eT+jsnL+2Y}<jLmg=tv_EtJxIZ`%iFh(}Ab2u39U2Bs2Tz550-g#^gZ2fdfu}&j!BfD~pnJj7z?Y!Z)|Zecu8sEZ0j>@14GjnP2FE}Xz%k%t=mc;wcsg_jcsh6%67d}9Z15a#1`_d1=tS^LaJnOnhbBQMf+wOMCm|8XL5G9mz>&~F;7D+PXb8AJI1t(u90+a!Ed_1?E(4{0Tn2gK8|d3f;2Yrm&<OB;@H%KDcpZ2KGzvTeJPR5Ro&{b79SU9r&NlS*Y$W1sj<f@s3>^ke28TlXgG0fCp^4zZ;4hGfH$x|bH-k4q)4?0TYoJrXYrwmpY2aPpJ<uuOJ>Y}TY2bt4YtT#JYhVwI9~vhfNW`6?y}_Nqy`VARUf@t@GB^}G1Uel&1Uv>h3p@s_L+5~Xa2gWvG-w7m1LJ2J67ghcI=FCL5yv}Hq9YB3QhpSebe!SXI3)5X!KeHPM~X$BIKq*l;6=eF4nsZyJP`RPoOdX^czDDE9BCN5f#3n)Fhf2X8Vn9bz7Ns>#0MbX6C7-aq2v8<tPi*!e5&*N_zfNJ0w&KBdE&}o@~$h%d&2j}u?ArBN+Ms#mGQeu@X33wM88zRmE4^9l8C2R@;f3C*MOD<mqnh+D9o3JDzHNSmXcH!@mG+a4pxR3I=&XiZh_arr#jBWZ|L~XVDdgkp7=*FdFzoU{sm0lR^*8<gUQ>D{8s249Qy-&8BF>;(q;VaR~#eH?npnu`w2erDdaamPvO`m<n4xI<gG>wd56H{?L?mVFqpjE$P@nnChq|9#81Hoz`r3+dK3Hu_%QT0v?*}``~u{EM7oKX!efV^cffa${{^W4zoW9L4;1!=-%zigag2QGPvl)y&c0Qce~N4IK))le2AI4~=(8T^&o$tEj688SFnOOKPaFg$Z!q%2eZl07Mt(5ni@xwuktd$wCi6=wG#WhBk;dXU=}7QM#1YdR84qtP@*|Pr5jP6QCLxVQ*;JSAsB18|ubXpTD?ILx7=PruAQ1;ZgTaMy-JlJ?-N4k2h4-8K>lXB7JMwqX=L7uRig*|OZ~v<f=N~<*l*|9P!~9Fv&$Py0e&{Ic?~k?t{>6Duy@=yKdJ)g2H&69HEllC0'

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
