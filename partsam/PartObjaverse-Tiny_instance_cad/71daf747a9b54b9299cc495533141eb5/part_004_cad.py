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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/71daf747a9b54b9299cc495533141eb5/part_004.stl', 'relative_path': '71daf747a9b54b9299cc495533141eb5/part_004.stl', 'source_sha256': 'e00009d74d1d0f2db04fa6bc362e3eeb436346fe2c9ae513b69c61bb14b439a1', 'input_faces': 1032, 'input_vertices': 537, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.38952821493148804, -0.2837282717227936, -0.4762970805168152], [0.2481846660375595, -0.0037814676761627197, 0.1626487672328949]]}
GEOMETRY_BASE85 = 'c$}r33Al~b`}d!1%sh0GLhVq-3<>>2wn#E{P#HoSkxFF97`7=He`QGKV^(Gvim-8zh(t2CNl2rVqQQUP>;61@?`Q4v{;&6X-*a8}_5JMcwa(gW-OqZ~v(|c?N^O)mONygE_c&#1KH(gDz%h~ANpbpi?$zhTPMv#K=>F;epOfGC^5g2{rcXCXZS8aVI)h3*-??|EUZraIOV#Z1P^t3%QeArV>eH)3_vd=_dcL#x^*eOy-8t&_?%Lti&e6}Mt5&IA-e09mdH-Pl|Km^2XcNNOe>%1;s%c#dd?D(r+m&8B!4F)!aY!`0{E){Fk2rrQv3#h(k6O=+(pt~+eLa3)PI2Q0hCY#@?|ib*TaVkG$)&yJn;t%tQTa%-&kiMiZ(wYp4BO-Sc6)5!tv^<e)t)4uJjCiDZ=o4QGxXhjx_-pXr&Yh5=U6@DA*uaVeq!}o`Ed$m_O!?K!<%ky74>iIy~}+6zdcTFOZ4{+PdC4p|E*I-JCEOH>TA)<_@U<Gjh}Y1;V$DhNPp9mD_Ze*hW?aRM@{>7byt7Vg0~XOC;4{ySL=i_Ebsc1505)w{J?;0reA@{15YISp`4esU!yvoO!WP?Wz~LldHGbLA0E+kr}<pyXOHjpE7bIk6B+q#JDstI)L;A2<p0&D{V_jSwoiuTU7zxSH;<@4@*dOv$l(De68*>s^#jv`Iu1sj(ER+he!F}QemwHDxn7x1X+2%OH~CM?^{nP66wy2!Xzb0W>qjaW-`Vk!r@XUZdwNFY0}n3Jc4qJ3DewQeuJQddhMw~HAE%rA2Yzko@tyO-jUUP7JMF1|VPP%b@sziGTA2yPPc3vJL!Ugy{7B!CraiffdCULSeq>^K|KAsNTn(<h&G-YZn)U>4T-N-b{o3R?ykeHeciyUFzSpVyqRB&~-_Kgl)Ul?#KUX(X-ueBimcON}87JYC#-@DW>NU-O+t<wZrY*^T#*D}A|I)8)#*Z{Ss`b2_Wp_sRqwR+;botWMcRsKBO9zfiEN}Zs<$uWYMuz3_-SYm9w;DgPYN%&ixxQ03sPod$?k5xd@b-!68J4%^CEE`)Z0D&b&}6CJ*IDwM_V}&dF}}Y>BTqe%%~y7q@?{Tr{6O_>n@pbHe(;RvdykdVd93-ZCo=Ti@#FfRHyCE_$DDp|`BRmKC6*7JzSH<=sekLZDzV~pqVFu-H^!9zr<eBkSP3n^q??YbLTyeb`k}H%O#A({TbTBz9Vw%EZa7)TPmz)yKlJ!QQ$Be9HjnS5Y@cG<aWbIyb+ZcU_vtwyaXi?*J04=b|Mrm?mdAI?M-Duo?b-PCR`b0rx9j~?<7sVw>90&XLl1N{?F?>gt@SK=+cVx=-+m6de%h+#p7}FY-g-X9$~PI5o>Bdgc0rxr_C4#VKV0~x&ST8mv3l^6zPJ85;|F)-Kkf0)jWWJ7q@Jfe{(9%lxOIN|#N#`EpP!OAu9AH6AM*$9G2=Egso;r>{G@uE$`doJ2j9JpF~1)3(yCToe@e>{8P<cJRL}SVW<B71>i4#@($%3Ewlnoc_y5&**C7wKSO57b`rIGbPsjNO&*?ny)PHrnt^L<rmq?}OwS1FICjb6<YxF){*;V}t9rb=}(?XwLOM9xnq3u-jxmYc|e;4)B`cud1Jm0E}&hsS)X!*^@b^I6oNay)tqcXhjY~RgW%(w14+jq+cioB`*kf+z1&v|O<JaGF&_2(C!W!hbTo*8e><f-cKzki1L-2X%4hw{(ReubKAJ=fcsdct{Udwl;rMU3y{Nz3qg;rjOT!u9RvMXbE_ys&-udExr@^CIS3&x=?)t>;Coe(SlA<h$!V*SDSvG2ePFM8?h2{?^=}&!bh{^m#OPVTR9f+mAh$U4Pa$<~b7nxc5nqZ#~~_KQ^v%EY|j<PSxi{ziT>Qy}3lo5C3DfsV8Nuj)$zvbv{3I!`v5v=a=h!k$F{y&o5`h>WtSjmLKca&<z<rrvigNQvaPZ@0!oAd}`Vgxv@pt)A%jVb1*z$n_l<T-+P`r;hzs`f5!%N+?MO3<MyX7)VJ2pG2dE0yS}}Cc71#O?E3clIp$mI=UDyL`Z-p=wSIQ}(Ce*CzrqzWd-`RstCM_pJiETNu8#TEx;pLBN%gIDa=3Fu^Vac<XI<_3&dTO<P5pBQ=sNA&vpRlK#(UP)u5a(ll6-fZyS}wAOY+@)S;q^SPir6Q`u0B5_3eGA>)ZQK*LUvv&a=*m`PTl__G9fodr^IBe-Uo~gMM$__jNw$c~hTjCx6j?wH~DR#l?JQJpR<e#t-HEO2^fStLj_(&0y=_^?U!VX70PR7e7Dc@vVKRKQ+r9Q%|3!o_$tuU#>mc{s9Zj_my}|$3w$BTK<L6tBqeihpq!3E2QNIe>C6J^F>hCjdkx(zt>AT&VRe%@dGpORe$jyeg5va)A-?(KRxT`aJZP(Q)!>(Z9yS@KGwcl>uIsnv?mn0sQKCE*YZ;zT4>7kE~DSOrG)x}x|s6*Y2~#2HA<`B;D#CJ;d#AvpIfbh)?f4o^Syy)RrPyUKCI>E7J1Kn-yPdDKji}Ice`)8DOY}<j;r_TseiJV$xkHfYkI$wuCKmzZj<D@_lxUW=Qc?`<wFaasNZh1X=k9v3~lGURO5&0>^6Cb<U644xu?07Kec|T@#}o6dAs{*^{XE-`3#0qbezm;t^R)>(|WQ$rq`>;v!3f7xvcYc+8yoH?=)Q3CqL`F7b^JDo{a9JB;Vb?<bOr|u@gP>Qd-ub>KD6e`kVG|Nbj%A!_^<Y$gG#b)j!hf;=HMTo=@kQ{$v`Y=QcyfsGri-<iUT%(fe`mc=cOO(|&!}PW$`!1kGpj+1jtPqPkA#KUK$bh4Usq;Ul|rz1nA{)|0vPBJ;iJdAxq0(;U-|!}=T#_nM>iH+s+19~@sx+w=2$_2-o`^#?{Y*7>T(LanFGTeCDT^YyuNYNz^FYP@gSm!-ev=g2|zYu;)4>#WFr#^Y~j?HRYhrYF=deqFEo#DiK-!-)F%3YmU6f!lOkJ@JjU^VR;Qd~lDB6Mxk#pP2Fw-)rWXV6%>z|H?Vlzg*w6Gq81-)?YD?@k4jr)cGfHN$>X+1&kl4zeV#<=>9W_zLWaC8Mpo_WwkxaQq+&EGW`v&_Gx<-`qkfZP3OJ&^|k&I#kKx&mv!D)mQ%-b!CG4WW^vQb;7>EP{<rF=KfI9{haukuZT}mo>Q~)seE+*)?e7C+_GdKylYI9%xcYwMCp`!8{jSeG*D2OS>#^pUBtN!K!MEm_B;TE9W;8Q?TA8t)_PBlsKisOru|z+%-?z#;u21_T=ay&KU)Q&v`>yXiTIy}%b3PFBt>?Jy$M&tkHO7zRDWL1aAA+Y6eS4jg<h%Q8*SFR=NxobD>$RHC?%(S=w#A?miGB#*&8O?z=hd!npI7^jZ8g5VevbLp`q}mE^|R~S>*rYcV}o`5Gr5V^Z#B=XKSP<U`mJ?ulJ7q6T;E#v#(Znt8$7yQ^Z8w4UC%$)PoEb@(zW~thxPntU_;%fG&rVtXg5L6fBJ4#zuuV)@2@2P<e0A#edpc2<~bG2F-yO9$2q-@k8U#chb|rR`1bv7`?2%k+85RTyPVngx#s|pT9?&tU&S*{Y(Lgc{NR-1-uuq>DetfOqt;{Ze=R?@Pjr2IpKJNC@*iE%aoazr=K#C(`IYw2RrRg&3fH&KD_q|`uW<d~ll|3y<_%B%_IX9jkEED$q)?kjy}ot+kmS4bx$BSr%X1D8^R07<m~Wj+q^<u${rN}IOn%yg^twNIUGGQERh;x1>X*s&nHirApYo0e%a4r*{J_!=z2m|5-SJR5ukr2kG24$_U)Q(J$80}Ven~##hgKce`=$Lkormu$pyl&-o@vT2+pqn7x0Lb2<7?}E{q{uNx29Co^7l_M>%B1h!ARbRj2~&0Z@0-C^R4TL@nd<zx6i#@-#+(_)&FR4S4Q=?ek}iPJ<KQ03w=GleSV(gTlEC%kJfo_@;Fa_?Q`{5d#rQySRSl%^;kXDxq2)={XaJMi!=KXPd)ZId6Ms*54*l~PHy{2^;qZRwjX=n;ri}+fb-{=Z=IjVeCzz&_LJ(j&d+1Mb$%Z6t@HCFKXy)7Td(gk)AhQ%`GDRR!<uUO;`MYNmv%;dCsqCT&*`~Gn@e7QbvxZ3T{xoi;m~G!efv)^=dNjOzt!@CpVIRC$}TaV$7I!Y@AYT3{I|>X{YY*-2TSYIDZ}}}_G8aA*SF>e+mDs+)g{CE&Gy~<!u9R>Ey;K9qn}^W?;TTH_mv-R)cK@GH|_8EZl=GH?t3&puk_G*CRNk>;;WH*-(Bjf^>i(>*p$0g^0deQ`=Xhb(w2A7`kx=7_oMwj7eDEJE`HMcTzvO=m-fymPyI>nb6wwh-o<?TJ*@4!>onK5o_8_den0E__Ve!SaP{r?=9V8D53X;&H@Ey)`QS*+bL+6aUkKl-``oWb>2s&iGQGccRoCm-ezewOudggWHh%Dv)>pRgK2J|f^vp}K``z+m?Qc2R^Sp?SXWMt{KRiRn=bEEBK8s$^@sK*#^E?f{{F%-JpDobx(_3nO9$De>LwEnE=SyQ}==e`xtK-nxU&MTCf8qM}{=)U`{Y9+2wZDk@*8U>qTl<S7-`y{`zO}!I`S!Vb-E}&Cx->KG3>NQoD$)0kc}&O8ZKGM|uh)9^jyC5c{_YRxJWyw&XPx7|caGHFq~%L4)^n=wy0FgQqVtcnPjr2IpXmDbKGF4)_K7vaTHZd-xBb|99^XFCw|#e?TVtpC$G7YA<@Gx?4<DuLb+`BX_(}VH{G|Q9>)ZQ%%a1*0tL@eA&3U`#XH6@;FRJcWzriLw|8d`ERs2%(AK0Sz(Pe!vnYQw%*8f@$J@1-yP0N=%ss2xO&3-MoX`Pl|a!&izvzxAOCrnZQzVmv&+`~EB?z!5Yg_pFRX&21;KXj(Q)<5ri^^3OHkyzgKL%%(!=TrqJXgz5^X}`Xjrt9RvtMvYzb4B~Lx}ABy;6B$PMXqW6uP-+H*+}kpw4Q1IXge46(D#h9&ujY&W<6lazg%Lm=9lN)+u4jCm|Ir!Gvs#l^WS3pV9kd59%}evt$%zz_1kSS{R;h4Sl1ib?$mm+mRV!Im-lr3On&3r=TWY2pGUdAeIDid_IXs=(30v~=V?j4``mGT>pU&VckiRW%4xsu>1Xl~D)6UXmx1?d`IMVF-#$4>{p%I9zbVh@x{H4&5d5W<_BXwzUKiH?X|FtbAfx-s^^=|>m+Nai)3>cMpEnlQ>-Ay-@>9vI1O2S`V!nNU*}mJ~i;eaAc3rB^mxh_Op7w3D{GJgTO!<;M^!lE8R{g&1Odi79mZ{&aowh$)KOHBm)6!0K(DwgX%ZwAJQ%@bwExTwv`8w)4`Gvz;{^$$FkNp0&smFb9>wo4&<A=X#VcHXHGFAP<uc%+Lr;gi+e{22^y{i7Yd8WL7^AlSC!QPtx95?mfpSb_-_py<hhu#0t_j*N!czkDA*0AYU;C*d>-O=h7x~%oM``Mb4wZAhf>3cE$U6a51ENxGgyG(n+TUKiMwF}f=vBLPyxQhC{l^1C{GnY4c3$+`l{avwK>!0}LW|N=SS}<R2)Ny!UcWwV?|9X74zu|RTn8!A2J;lE?zW-V?&D;E~+(!pZ{mz&NJbrlce&eU{o-R^kuYPacM|7OK>uvl{&)4+*3-5U&DPL+mMKhUx1@|+L<vXM0%bzmuS)4!gJyBY&^V%NXFZkE&)Oz0dUdu0At=G4}z1q$!zi5BUcGdaQ-Di!sqV>!SoAyV(y2Im#-dk$?5bu5bH~&<Bb0eJxvg>>veElD7zyFxYoAW`KdBAtj)L(kP@q>Rg(02Zw-T1+^ZMJ*bf420&#PQ&F^gar<t7QDZnkB}M<f@=~XkAVHPhK<a^fUkXk5|`v=4{gTpU$u457jk(DF0P`e|>eEmVdH=r=6i{T=$*NYWeRP>ivFTvexrRC-pbItM}dOk8Am=z0^O@PyI!&FrNEr{ki_$me?=<ngQDWVrSG}@{-n5VTiUrZKL<P;5)14daujkaavEoU$!OsY5CS1OuWACxQ+R<w|K|xh;*%I`p)=$l<N7bn8I&%ToS1iEgFp+PKwi|L&BfLh$%m=X8b2HFFyEx^(QfvD^+>m|L<>Na(0Zi;e}|FC4|eMU0~7Y;WBW8Xq=43N6{EY2=_w!!J?(%UT|ANxE^{JTn`SQcfyaNMbSIqqHqyH_zpt27<w0c7vEQm5H3Xs_eJ}`{pe3$Lij^M_yl?q7CjH2fWIMxkD<q5(T(sicmpB)G9lcJ5bi+;4@Hl|L*c1}@Er6!e4e(>A%x#Whr!d);pi}U7}s(*A>5k~Zilvo+j3po5yFoV!gbI9>|XCWgm7I#_*p`@4Iz9VS`-#70^bMUO9-bD!qw0_;A(J5Lii!H7%W-}eh6-k_Jy0nuMxtN(GTIt@EY_4yao=V-@svb6?zO7-2ktG-zJ2+qc6j$=)LI63Hf=MoQZaWMSCRVvqwVydn8;J;a3Ua5IPhVoeGEGcL?FR=p0z|UDzF$!oNi0YBc^p|AGI2|3ZB}<-g#Yj)riiX#DG_{)zhFKPmGYDs}xv2wy_4!k6H$2;uJt;RyN*9Dx@S!k-bsXVE|4v+!l~FZeS2GkO#L9=(Cygm1tOxsX0Pgz(=^JTJmOp;yp<;VbY(^iTLAd=&i+J__$fFTuOvdFWU0Ja`l#ybt{j-Upu{gug%|@E7nK=tB4n_!&a@IrKC5Id}>oycInQZ-oz_m*LCg{Qx0+B;nc|A%qV`V+VQ;{T@CC|Bl{(e}}K5a{aFJS@;?%*X$Z0{B6Q@{gx0;BZRl3SK#gN9zu96dJ$d=PeYHw)8PK-Zn!`E6gm%n3Vs+J1wRazCxk~5!h6wuu;>|hFZ?AT{3-ec{3$#FeFGMK1|9)7jmCe_N6=?r(dXbt;FjnVxFtN85T1{2h3CUN(F3sP5qKy333?Fz1WtG2V=En90H?$2(b@2NcscrCcscw&IuYKCE=4E8OX2a+=#0LIPJ|~?*NcSkON8(sbT&K)9)d1_hrlz?9kA#*cm}*5{T<#9|3C=;ie86*g?~h^!9T)>(Qo0y@at$A{5t#!A^aA)9exX5iSB_{!rRcb@HTigIt^Y8PeS{{li)sta5MBNxEWj>eHg9|mq5$ICE%)ra4kZ3COQ(H2_HiD!lGZohu~A_r|>EGb94m!IXoI|3Xg_cIr00p6(L+3EeF?zYof*Bn(%|@J@A9D{8tVtp?>rp*bi4Age#-P;mU9ov>aRou7Ums7JUS+0k=R~!lHxW7VtoHK0FYfh3<rB!5^TXz#qW7&~#XIJ-iFvf-Z-*z#pUU!|putF(JG-8jH|P=w^5myaZheFM-FR<KeOJ^G<v|a`&;K4bjf9=!<YexG^Ez1bqn>9RxRlpGJqkPs8oe8E|`e0J<L@0IxuQfLFk$3E>OqukZ!<YxGC>Yj_=c7+wdrMqh_p!%w2Gz^Q0=^c7h2Ex0@UHoDS@??;4Jq1&AJp2eK`p{t$ven)r>I?0LekAx?qeVq7yO4!|V2{%WZIq`j&@Iz>IC%%spE{T?K;(I{hYG_p_zE7;`#P^a_$;Xp$YqVBEK5LP0(U}SPpUL$RJ(O_04skt2Pr;&}CtPdc)97d?J~o6`psk$v_z@m})^_6KO}IT;(}|By;iu6Do%nbbZh}7G#K*sIV<$c*y7!K-drt{BAcQNTez+ohH(CL{8@@jp_0h-C3b1Hp_;L6Nv<mzL+z71!i?)Cp!CldTu;?tfD?9=H0G<FZLwCWVTi|8zd+5io=wkRic#IRD6UU%$!eihLXb=vPqYmif@Z<Eq10mcAZ3H)>Z=KKya3^>ix(r@MTgRbe;4yrMu$<@gbmHef!tS|{uzQXq?4B<PPbY-u62k7efpCZrcF!M#-E#@yx@aAENOXVHIvVd1!m|kBcL?Fv3E@_Ra05d40YbPOA^adA+>j7{799e&iN+J~vv5PSO2Y3}p+3>F3H6udJ4Guew4pNX5`8?OosZLY(Uu8)X_?T+mh@Y6P(mICksHye3Avg|{zPXc<Z~uD7M+%m^J(;7bTB*weim&57l}rmXcQ%c^P*Ydyl^%&7n}{wjotz0hVMjMz<0t=5yETG)$khl3-l2D1$+iQ4WEIJpoifj@CStO+Gw;x-#`z;Z@>%C)9?cLBSLr{dI+8ek3?6)BjKmf7H|vl@-!h_1I-23fQzA7;bL$;Lilbp4}3RV6D<PQgxe9q&k@2wv?v^e+YrJ}pn2gZ;3{Y~xC&gB5Uz~ohAYF5qj$oO!!6OLV9_;jOL!3a1w06zik^X|!ZQisY3LDn8ax>N03HmxdH8_bh^|e@)mn1tjx*ugqERRs*`u*88ec|ZJt2IQ5I%>Vg+;%D&%wtC;f?49ShPF55$-_<7e;S~MRUM~;hcnU7Bn-QnSNv;gl|C$!MDJT2;nY-a3?~zBYGR$5$;R~*Fm$xb>Na{X1FALD<OOzngh;3pYJ1t>!ID@dhjcR@I-V2yn(z=B!u55gtwq);j>)VErjq=LU<gy4ju=)d00noMAs+eYJEaJ*C*szxF32H?g#&u5T1^ngGG<Q)8V%X;Q{DIcmVto+5;9X48H_7A%v@=IpOMX1vCpRdJ9|uu8KB-Ux-HIguXZS#m8P_%7|8jMJvKpVYmK@v_<qGShQ(EJDVo-r78UreHj)Vn9%ou3Aq|bE=4E7FVOD(Xg|0g*Qq}t{1zcR1Dy^}r@k5JB>0NtD^qmegZ}GN{tW#U{TKcf&KxcK2bwdJs`xqiES!Q$y(xt7?Syb%RN9f3&%%F4BZBTnufY4^73kNn+wK*F@bGB7hHghcgSW$%(O==q@C{V@c7xBtKPUA6XF_;iH2R{)(Ldnha8`a#a+H-2&W)zPDdZ?OAzUCDx1oj6+u_^EU135vKPtJ)&u8JA3HiNA2w#fEr|1qe0`Gw5p!?xDaBp-4yn<Z!CWKQHu16{%Tqzpm(VpmQa8Gy}x*gsIpGPml=i%Sc8}JRT)9-}vkLW)5M|f|-wcJYx_lZUs^nSE2d_O!HJq}NXzenYIe~;#dC4{e`1z-tbU&6Kb5yIJ{u`*iblW6QDgfF1q!582xnN;QXvJk=r(c9pHa3QoXT$nLbh!D<)${5PWXW@SsSC`;_;BOPg*|&u7u4pVmH>01zo8iUi4tOy<9-RY^hr6P^;ogk7u7vQTXeIbjxOl?2EKUd)h{iqWV`zE!F?cB26CMhuqubzg_y_bn`~!R){T&wl5xx%pg6@TXfe)a4-~({T7azwVLij&~aA`s~1-&0mflCp>Pok6IC*cp#?_tqv@Q3h0RL1l{J_~<?W{0ygcE2Hn!{{e)7~YDmgtx+*2;qg%coUt1u7pK*!c*Yo=mmH=e3B6U3zhroFFp(B;a)2U=YelU3&FR-InaEtsN6p}_$>UJPxV{)H~0j)3qAp_^2P75RfO;uLU=48yo3<`7~KquE`~pb-$Td4@4*w$uJ8o78zEd5eH5+>--{N9?}ZDZ1z`7{EJz5KAcO;iaBV`kIr<pf98N=r!fEj5Xgd5kd=>oxz6xi`q<S3|{RNf~{uA#2{3m=04Z)}2x#)l3xo|VIG~5iXAB{&)KUy00!}-w^I6r(BS_-}kewYxhg+2+_f_tGK!lDP^Uhr)68(1_9&xV(wTVc^n@G^M5PtRCHKSDS8;%73#3($qW__>Yn8@~8l;GXjcyJsN6?Fr#m(J8R#a`;tv7<v*O2Jc4yf_K9|p)xQ0#Ao4b%oVr7+2CA+u!H7+9r&V8Rpy0@gzz5p1iS|xfv$o_z#Y&ru;^I01N=N8?Cwd0$DvDn@qMfCQuJeAe4i`41%1yK-wO-Bk52H#_tC-=(Qdx@UR&7Rn+w-N>-ysRcj5ccdwuc!zVNMRL0|l=K)57Y!WTbJ5Uzs;eDU*#Ktdh@3Hb?-Gtt@!Ijl{-MVlw&zd6@OG%ewJrExt)KTo*6!gBpZulnNSK{ywhiLoR4r!PL1gtMWieDU!n{1e_>UwnKD??#*X;^SF(7+T*KAOFJcJtExR7oVHl`%Bop?}Tfjeqa22QuuB(zb}5CDVz_z%NIZY6fTB7?2Dg~3d<R)oWaT&>oaH#xCUjOL2JR!z-`f9u;^^KEj$`s28+&zN5i9h@%d{MIuahq_l-i^!gBubqEF8r9)g<^!Y>oT0}0_tgzyYP*gZE8cFz-pUm%1V6T;QdituRKCGG3Pd#4W3xIG$$qfy9_|6N6NFA<HLgm4Z*I2R$DhY-$32p1rPZzY6N2;qW+aDGBKFPa;c@6AkGM6)EcEeqvDv%$IHyp)&U&x+=Pv%(IV$BF+4`_O!FKKkP$3UJF7pl|M!E}R`rfwRN6patR7M!rlbng37!%aHhwtRWoF|3Jk4P4AyoB>rZhDo*^5EK(a~mAph7n#sKAt1SPj!}%ZaO9e#'

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
