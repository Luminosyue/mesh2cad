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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_009.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_009.stl', 'source_sha256': '85eb0675a05f8891eae043e1131d7812fce5024d09e0b46f94d4260d9dc5fee7', 'input_faces': 751, 'input_vertices': 526, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15827175974845886, -0.03885503113269806, -0.3565378487110138], [0.16206716001033783, 0.181783527135849, 0.06851580739021301]]}
GEOMETRY_BASE85 = 'c$}r22Urx>yT%6;!Cr#K?ive<y?0%W1xpk)_O_^4v3Ers6%`eG!vZeGf`wx5Fn~R%U_oQlY>XO1tg%I7^qzCRclJML+<Tw<-0Smv&-?CgzVn?kXJ=<-cMkfu&yv+!p?{^7ZZ+TLPOG6PJaQ@C%H+WD6Ne89oKSW2*lBJ`KEe4vT~~MP_MLw(H)XOi!)I{dghAtd8d`iB52^1{+2S)~%=n4p14a)RGk$O&=dA;RCIm7*VOYS}K=!&qotkwkTWVFTY?*2KKmN<XhM+ZTaXOKy`c1+QT&>jtgsRqZ5?4N)5^8_)Iz_zhuPzb!5B;}swLQHl^Vk@{l_`6OFHTx0v`mfd5)YacV&v+JLBzFLy_)eli`O3EueAa;;$yo^=3KpBTX4rFf8sCNjOE-B^ygtw$GsKmM0XN(UKgbN)=dOgV+uwIy?dW{LN&_&xN8E>*M<)eT=}&U<(Dld^6lk@3U2c*kMV?e=lM$Axq_?pJShKVZmM7UXR80|d9uhaTx7n`Lc2ts-6Ng&+Xi7m`wkV{(IA%i_f><%{{MA>`WwB3_@~UJVxF6y5$}`5YdY~%-xY%Q8+uWUv(ZH2p<QN+x`oFGuBbu8pUqz-@)ypd_xr{`;(nIplvk1ZJ=m7G<>CUNB_C1#-_41attjef^R8YHubVU^e!a|O!E-tUx38*BJdL;|^026{b^4Sf_}A}Oi}CDfCF)zNK1?#skFBvc%}=gW;+KD$C-{Y{G@gOU#QkaBEXh+vzU}rw;(6B7{N#)MQS_TTj`-<0s;K+pA;H!8QAx)4%TlBc%|q>?#E;z<`>RY&6#2HP1&CM3F-_!uN~JmpX`0|6ZsWvpJJ5HZ=)c?<;*UQ}6~~)@Tfvp`(Zmmyo5;EC>?+E)e=E4Ub=+2=yL0SoX5h-`I(C<QSkz3>-pu3w8fN5*XML)l+MbTvI!W<HuG~$JaLK0+2yw~1q9=*^I&ZTj(Kvp^Jx7d@>*G<~h}(O&PL#&8-gl3Y>-80ITf0h9ebu^npOHJ~$ISKlF>`%>z#R?p$>aIaDskuhn7KYbX0Fc<xK`AjAh>?M%`<4R;7te0{K4~3F%SOVCP?#HHG8a)JLj_s_(Tuled+wHR7hFCxn*$XDQUk_D(*FM=RAYk!q1(O>U`=nUmVwq#uE?4dEQ!Pp2SDsJP)qqoq9sNo=E3&<?+U7@%j7Im-sM`*`mEyI`Njph}WJ?pO<=lcM0zH$8o`*br+vgwe2*!80VFA;<<*2^Mmr@t0*xKVOxk_ZbjoPf5cAp!lXJ%{&phYVfk>B#{KAfp|?M*6ZP}`LR`sGS!n(I;bPuuM-k5#IzVXCitEMxm0dvG*0O`p&CNu<eRCh;AOEKFgXX(I92W&^5P#h_Sa82$f?Fa>gVXg+=}|<Shiq3r(e-N0{_%n@?inKLzy3gc><i+Kvr{Cl9-L;ZV`+b#_?_Rybx^I}kj67AjrfbFfnvTQuU(XQeR^N?`d{$rQ$mbfy?A=7v5v)SE9F~q(0+|rC-R;AZ|twKNYuCaMiLLD^QzLOz8Jq_^g3yr*08)k8oA!DldDrG|8&MAQKx!)QU43x<&YSUc5KICsZQZA8vll|hmHLzxtgUKxt?zUx1I=+xaM(Q)Uj`@E7egS2d5gjp09JOZ?i*Ee$hH~-S5!okd#0F9bNA#c}V$+*EqT#=;$WpD-&vo`i_j32c`V72QL}9GauY`>xh(Z%l|^+&hhAc<IMxo`xR;z<FuAJe?ZEQ2)aa{n+Q37(jAd+DYs0@cPx$;`RcgA`=#S{OF_Xc6MQ9Z3GPbc8GM7T!_{KwbH3=|bt6}cJ{9K+wfBr0Vm`a6l%K8PS}_kR-DG~Hn)saC=3KZg@ddR+9qYjLQob6uL!5WCE&~L&ot#Mg*HeP4YgY>HDA1AWTpK31wS1(^UlgF@D(ifz6Oq+rzLT5s)%0KEUG;0NpAqkBf1TX4zfNx2U!9xxSFJcF-qrl;+&us4;goeEKhi^7FV)76qb1%wYLloxd)gi`&rLfn6TH*J72-H)-8x?4Ro060wd2ki;=L<%75t8mxL#Vjmia;AGh?=hesAv;-(M_O3NI9|XXX_5C2GGGS6p%J$l}YQ{jhn9nz<N{lbgn)dS6*0_~Xja#`<P%M|~&v&Wv%H53Y~Let6qz!Fzn(VazvkyD8tfUp`x|xZ>*We=bSfRw~X_eVyy$u_ljN)6B*D>*S{QS9uVy!PWejxjud;H_eZk>*H|*r*3lf{+hXS{JnB)7Io&uuM#}_zvBCkV^0s_Grc1O??B%_wI?aWORSF+$Nx-~`1WQZPYI@cH8x#v%iNj7=Td#!%PjQ0X`h#9uihQBQ|OZ}qF>91kVt7fbLe}i<79fIaXj`LrKsP3n`|+T$NFYGeGeKOMEvaM4aR&YKUi|3(CkHJj`})xY`aA~B21h&v~1&K?!B4rlNyYaImV-bD^-2Pc|kct<FVCCruhkIZa2<@GPsr4U)!ud?Z$CB)LbbN$2fJaHh5(>?yuTEAB`unv^ak$p_9dZl=fZhHHokAnIXpCtzw46FV0%`KXJ>g!BnSr#VF(aSZ2}hBTkO_QTO$eIp)U>t`w?4Ja~}!Ua5@TeNE!2;o?3=eOD_(;`LY1{dxZja{k~fbYEA%Th5=^R$LcsA8c}d+Pbwa>w|w$C+0fkKb}o>mRgBdu1dep4Dk{97C%4YUMIwTp!UsyYZ4!)u5p<UuEq=(`L?=4qm1vbHSQqIXMyd+zoL1zdgM4O@tckfMy_?uzg3#I?|!@{aqr8-|2`sf%%^&<NQT7!K1uVusEo|@dHZj;I&Q37Kk?97m-WFNm*<Ln>ww!^rTv}x@r=av{RMaA-oH)o>-0N}I_vW_i5G7@Uhwhz>3(C!JK~{X;{>m_neKm97uqg(<|O(a_x9yAi7%$_(Y6Qq=sv1bN#Y$wi0`Lbn<Ju*eZ^wpSu^GcZvW?+#N*R~1pjqA_3OEj`1u2(U+XBh>k>a1K)+L+kEZ;TDB=~uMSW%edpbV%X~eybj1l9Eh@tU3@uu@mhaEJ}(M^&ij?cBuwVlO@@1x`2Qa&(A;%NbNy$H>8$({Mj%ZTfoV)YX9uWT$$pRWe(h+m-dj3YLc_?yne$Kvzy(>cM_UTU;)9<)W-h!+fvHqNJYm51Q=wB^JT=(w^Sjivm}`Nefnd32h-kEgt&d7IX0kM#a}zL0t4wj$s9Dfe}Wo6j>kH=Q>uFZ!d-OmTj&7Ck6)oCmC%N78xVo5{rY))(h<YxfwLcO66LZO0(`yp+l${?}`9JgCe6rTlg8_eh_2oClm7<J3QQ+Tm(@rTJO-N#^Fy_4s;wjmNFh&{NEhrFehA_3NFZ%t>)P*g8%kUVWe7_UHGAH}In0;cy+aS?4879M?get8elW$9d9`YZ2W)6l@)1Jf4-Nw`Gp&lrrwR%yFI4xy7#^@x2|z`9Z%f*#4R)^{b7h-{qY=n@5C^t7SLE80SIT6ic6r?)zhm^Pmn*r{8T`rBj{rbRD#Wq-RL{3eCUHEhinshx?1;LA%%>S>pQVTIW+A$GG}jI63NA`~s3Bu79rgJaWyEZ>{wr#?|N1$yf9nY5e?JpS_E5`MJJRNc>)?MAPx_h>Mds=0WH7yj6*t&Kuf-Cd5tW8AtP0vC{h(G9y{yI1a5xC&?Vgq0TK6`x3|XML$lQ9QU`5L3F=osXmyv>3nD#I3w10d^#SVO_n&0PbV)qFIIYg52ec7G*0`uUBtI76u&EJ1(Px)j``HN*7TS(KlVo@QY4P!{0pv+^X7TcueI1a;<%368&5bRaa_m0;HLX?)vHjPG@pIj5kFmm_@)MQUoc`k{XX-sD}8^9ZFx={=is(>bESOyk|i#==GRN&dL1R}ESKDxK7@Yf3Em)$)B3ay&Ht-tm*de!9E~&Xuci7hI!?TQak*dCHgDsM^Q_s9(LB3<B5unZF6!dG!a6liyz%p8PunT;$M<MHPo7J1#qG6!N-%P@MsNE5amtk6{kFKD()9f91&HhCfy{06yHKq{@y7jie&5MoG~Rfes0RbjNF2wB&K;?xiT^#1K1WrL)9)~$6^XyPB7S#K)1RhGyg(K4d&U=B{~mh1F+C6cT%ULadhTG~e38aKcqsC3trhRnPuZ_Z9QCc>YKxJ?)AG@MX09k2r)3Or{k}BdAl=t>SwQ^BeDVCwTID9?m)u2sQ~DZdzjSWeFD)*Eo~PmdLCGkZA#we_9o(_>HgVjCYtO$Xo;8#Bb$ULiOld*q?bv+#jdj%7&54J36IZ?I`S_zcGS~CL)r3mKasOlKUxCg`bs7=Zzn`|OMB{JOow$BKqwkl_QQuy(olCCg+kOck9*y(iTYoxlFH9!>$J{NV{m&EAB!0BYC~@5Cym{6Gf=^u%DfaWpa+xDv=i1t@i8pUazmw!lNtXD{X`7AQQlbU%l_3$*cyw+Wk7HX9@#Ny-cPy<y5AnOSVw*@@|9%nvk?vQUP9?5?kHGz~{rzm>`2J$O{zm3kdx_ueG`C*#e7S!taeQym@1LC<_to|{dFc08uN%Y<UZwFod`0(@DR+qL_n+-OM83U3&V%&6|FOV0er<lALxL9?PU}YS`<}XPGV#zw>&5HRIWJ2b&&PFc$-RJhiQVFJ?MQuhN#ZJfPt>{Me^hYw@&j6@va2xFId_ioi@XufLml6H2yVN1pZM3S==b0gg=9Xg@+2eI4p<HgKKk@haXjO^>f{T$FBk7S&f7XSpP!xirt`C6pGG|Nj5z*Pg?<OHUtK{Q=NaYp6LCIqXmP}G-m_(Tiu0R2>?(1bZ}oiZh>XL=&#Brtp1ybd`jGf(dah?3x<}?XZ|J}Cs4tZx;&pJiIG$}y!_SF%j`1R{|DG^+G>yNtH}RI8!$f|Sjprm@_YB=XpBqBoo7{^NA5n6psMD+gJ#Xq>jd-45`n|krBf+&3{fI}?^ElhqBpUyeK;ruMxK0yk{Hark>(42&*kq3JsPAXe=P^_zj_-HM@NqKVadMq;{A#JQ64&QJE#B}b&9nSG@e8g$PyAspano~8CpSI!w0o^4ZhGEof3!~Kc;2e4I7Qs_{8t&BMBMbeSS$F=G4cAFRIy)HpRi+zuK1_I;yJXM=ttc2TwA*`h`8xFxV9&XxaqmM?cP!1INz!dCW!N@lfTU)juQ*UW9IsJoV?Sb&BpP6!S(T<JW1U2eBYjWlQ^y~+UsRBp3l#SzsCI!K6g(3Yy>^G(Rug>;<&Ck_v_yZ#|7V;h1N-&KXO3gjY}_+_|KJz7k@WF)WLbcakM&dr32lEfZL9YAnr%Mk2%M)b~N#_dE{|+iYLBt7tQm?>E}heZ7Ian31Z!erFXF4HqXi@1V8GxRC-@b-1)xf9LJAs(2nD-xC86%oP6AaNa=kvbJVw7>qy+Re#2T}AaT=r54&GDant$`Ys4O@j=rA6-euECSI425>*H~9({cC(*N?-smjriS*J@^`=WDs{Qht2aCC1~&$;a*z_aQpBW;&=&zo+6lsNuS4e_ZsG$Zwgj#CSYAIqqk4uFWY=+|!$$cRqVX--C+PJY{^p^!@sRW4|034T$4DLBC$xRy8NSf}TgH#m2@+y!Gh$Ms7ddlXzy&FlipP_9echmppGeSM~=<^D}H{g5aigN=|NCr=)$}E4X=ml+M3cAN9RP+_XN*QT>z5vHr@*m7}WYr^6w!&cn%<-B@De$`g-7@!GWROXucwUzUG*6F03Nv%Fs;bF4SB^-m$5Hh!WQ$K5w{KXxD^QJM#=ThqCD{hO1U*1tKqdHvhNr_z4u>-2PPUccw$ruBPHZd$)*4RhB7PieW%xL?YQteUi6SWl>P^EyMVrx&=NxR15tc(!`yBVN15SW#d9+$9tt-uEJX55;}2^<{NUdLOYKQs?INkQPTx;<%61k8>wSzdCn(zd_zFti#l~c|E6-o7QtWxp_V3vu)D&^>wE@H?K!^a?^TLCpWD})duEF65K+cUv1?fu};OwvkjkX<m&HX#7*mOEkCRwZd$Kv|E)x_;HLGx+Q>@8&Fg{d*C1|MKWtBLOx(2ISQ+U@+_XN~9x;HpX+5(gaVl}s`e*IMUgD<p(w0q!iJR9~cTXU0T90ihaF)1f{kFa3UE=2T-uE68H?0rXc0VI-T2F4B@|w75{kbL8GevOIdUYk-m$+$tyEf>%6yyBp>*2M|K`F-fOJ6^4x#4qKaMRxxIJx=n3;K2;Zu&a~wcR+G<L?^maa#m8{~d%QB0=Kf?<V}EzXlmPrr-91W!N`u7TFbVWk`VGPeC~3|8#Zzry#>?|F8ZOq+XpG|KC3aIl#v7Ba3+GN%(m980Zmrt_R_{?t=fs;xh|(H&QP*@>!ssP%rpzu&q4Q6FxhOqAYSCxc5O6MNUz)FOTrVc2CszL0cb;#Rr`GENIKe@(JV3j&Mh9cjR#YlI6T$@e2Bv!T*ETTt6DNasLwf4}30nMaj+Lx*O>YH}W}{&*@Ivb0SC2&51m&SKR*7hU;bM6?iX}lii)_Wk*}?e?(4p)X0hLoL|JYi>Sf<ST@%2EQUiz!ViZZ3>^wT7=93R2t02)7O#iE4}uPdACC5V{t(n2f?C|yWl@JkLudndUlvtaRD@Q6ugRi1i{{X#2Jeg4zNp(2Q5QLNQCs)E=+hUq>mVv(92L=T1JtjH+?p5@_dYBtu&4yB3}1^yJr=d0_2H|rXo7aN(WVyE2i^xcdJV2tXcPDv&}z^o@YT@12DB1<1@u=LS|9!%3kQo|pufTwWXH-^ES~T=gxA?qg*cC=X!8?`KMed2)HuN+fyH11_d}qk;fKJFgr0yufi@!%+_yt;-vBxUz96(IbO`(qv~LP+2j3L_D+KqYpbg;lx}~6eze*v$6y~B7xIPz8F^5kv55GWvg8v2n9)kN@nEzX-aSL3Z+b8fnSzldPEQN-_cV^L>MQa52?V$_dxdy?vhK_&+!H<AXLU4Z`x)A<6{O<_vA0rlGJPXnHQUv!sp`GD-!goP*#{O`fW!SecLw)XlgU*8g4gMFzEW`L`8TM-y_Inok;Qnhirv+H#hvtPZq0qLX(ERX)Sma|-48eUtv@MAC1;O=NdC|5cv^0z2&_YnXc2VRPg64xS%%TX3ub|%W-(XuQ=vVM%u+0K31z!p|7St(&T4lhzp<lt*W^+`RMGa^*_!{t4p;h2{4sTN(S`)rHd=+R__$bzgoy8{TM)*zeYoTl4c@A&075W4GR`^Kh7Whc`b<p+j>)=;GSHrJ@Uj|(czYKm2bS*p|TR8k0cs)PdP&3@nZ@6J>;fC>tWB<ZY*N!o4K%dLu*CI9;=4u1xBMSZp#0Kp57Wnnh)$k)&^k)$W9RSbyFtGmcJ>YvFZvcF6_}*w62tN?o1HK393`EXA^fM5g`*AELuowj$13!_)By69AZMx^%MkBZnf)7IbG4P`hL1-I<{Bg*cfOZp5mwR7!j8<gf0nG~U234S0;frHiF{lFHoJDCCRs{DJL}}!dM*Ct21=|(Wx1g;BW3hl&L|?@*7GG#{ga>MSAcy;WEDErAq>w&V$UlHSgg%Dn`a67XmY)YTxaNn?kDB>VkNe-D`Q850o@*Yw&W{?+SX5$B4_d+CE3+sAEeT%<Z7M@s!B@bxGH721+nd3+g4TjB39si@!1fAYb)dE2`P<Q0p?_Q(!DnTWg@p%#dv~ZCyc=@ep^e~MqD?cXJG?t`njwelw+QZAKpVlgfal{{%{p7fVmWjf{2>;HS=d>ufNp>uhUa<^egk|s^Z<M~{6^>@_(Q0*5yAahLx0?_fv$wEfL{r}46y=ZUV(8ehlay1hhGid2)_|^R~!0UjaY;E=*8wJfJINJ4c?DMTNWKybcKEgZ41w}J^Xj@ouKXDJHdB^`oa65R!0Q)eGL8eL2%y}!Tt9bAJ<;cuJBzkj$Y7C@V(#zpdH~mqK^PXAMAf0^v8WUHb-BxC<`qF&m*TBZ7&C(3pu%vmkXSGZ)i4XPWZBTUBZx80>S;i3hCbpc^=%4ccb8b0`xgN5AH`HXB6s;0_Q#_`qsx#0=@)tvq7K3KS#gW(3dyz4>Ny=MFR8`Jl70(t~cQ?u}EdHAG!}d4jK#H2Y(293cAlw`xI)N0#7xxiGv=7kAvS2O@L3p*!Dv&!N1`9%;E|3PxyN*ZnL-x{R#da^abLsq1|)jJqPFh5sPbv{A-5VTrWYd!T$<<1ic3T1lwLfAHo03;tq?O&|C0NS^UA`88j3ADvMMW51|hDhwx9Kf51OQyPpxy4E@|e-8<l!=sOj;spwB{d(}|$D*Bws-h*Hkvk~0SL2$1^XTkIQ>0n%^zz4(6LU2C=eg@idoe!_V&w(y9^t;e79_~ZnL(u<Bc;5e1=v-(B{9O12(1q{|;O9Z-!_R}C2Au&v4Sq6o3jAdFsZf0^?(8D^FPqma&`<EMn7(E48o~WL_;<+r1kdx|A%}Y&-0QX7QO_Nm`>f1+vT)-UaTfpZ^9Gc&Y}n=rpADYpesCjw!_PTxq#vQ2e}sC%bM=6KkKE7TS+R{PXCBax@PnAnVKE=N2cGkxU|i=J@)ltG0&L@cFWSz7&N2ACXtx(_xIfF{42!>@FX7Wzq~rBV_`eY8hIU-HBe>rIO^4qOO@pSxA7gQxMKUx6J{kT9^eFrh_!wv`d<^_%XaxLb_;t|r@ay0sp<Cc1;rC%Ye0=+%`{4H>XFtXnhwaDU_aWj8HRBBZ#u>&IXBdAR_Ad@~kD#A;^tB)UI3gZ%lLCJf5sx{Dg^xhQV_)M@m;06M&|Se|33M@hD2qjSy$DR-#$WSxo6#l$x)OdRaw4Eh4L%gFxrV`qq1IAp1bm1a|8FPQH5Pgw{y5uqokb?}nZfgIH=rjB{sLZey=d5W5$!Hw8~41gCFt)y`~&pOH3Yf@J_Oz$!F_jVD13MLZqN|;5VYxr;J&aM?bDwu^16|7mKWRn;r&rJFM|6b&~EVE(547-il8<R?lYl<;R~a`OvIm<zvJ*1pwHl+Vb1jV<@5Ls!TlTP4fr?kAD}1TPoT{Q1oxBND7YU7eFM*f`!UcD@E_2Q`(w<XV{sIE9{xRxw=5>Qk&bmE&$nGxsNFI6G_*}a`!w+L2<~4aE~EBkLqG4~-$KvBpGTXwh}Reg5AH`p-^0Jhc)8b@PiAo%dImmSp>0>8r{S+6Cmot>$mMz$!ToR0Wcc6UZ$mYB4Q;sZ$i~!zMJH%4__i!sfc1dy3at;{1KJD0{r70kwIj4Ed{?yX2yF}B7PYu<%%UNSCeTLkQ&<dOF%@cqp8}l>od(|s+5|ccej4(cAf}?vsi@f)VMG57;d!4?EVi-e2kiqN038VJ58nsd`a%c7_rtdS(7y1SQ1>K)`*YAJc&>@?C!wbh++Tnu!e4;bkfWiU2Cny&i2f7Nhd!1~7-Jv!0B96^lwl5rvlzzWjzapgLY@crNzg?2B>1z?6!__Gd`*v{1iDeq71ZE*-%yi#-Y3^U^dE?}`dGNmhN|$h;TIveUksfN&vh>RVt74&E^5q0o?df0`kan&3_}EBE&?&upAq-5-}kX^iHIwhixl{4&?NXI%oFz=Sj{#pzJvO~Z)LHI#SaMXcf&_x`&Rg!(B1I6k-rnceK3Oinb589GvQ}Icf#*Pn;8i1J0OBF-e9zEgW&#K=nVK7X!9*{zQum}!MB8VfNu%U=b<&5qjD_DBDnX0dcu3bXNP8k&kmmp!9D-~K=VLzL$kr>hR+H0gwF|I9$F5*JbW8yYxp+s-JzY~yTkWGaNmtZ7pOn9GrT{1D`;!@)|d<Kx3SpHA{xQ{PUsGJp0gW_>mK;+@H?P;;dj9Ew*Kwi+`Y5>cmMtCfBx~$o+ABcu;!NXQXyl@JT;a7EFAK0@4@GueW!C54<r8NGot(#TRyg6'

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
