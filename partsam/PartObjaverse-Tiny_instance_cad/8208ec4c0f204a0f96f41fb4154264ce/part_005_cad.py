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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_005.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_005.stl', 'source_sha256': '1fa1aaa357a2da1a501b13a016f6a9f0eec281efcda94669da64114529e7e855', 'input_faces': 776, 'input_vertices': 466, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.32365143299102783, -0.4884619116783142, -0.1193392276763916], [-0.012729132547974586, 0.2768213152885437, 0.09349790215492249]]}
GEOMETRY_BASE85 = 'c$}qt2Xsx@`}Vm6(L2L1E`})4MK{jqqDLpVNQfSZGDgXfs8JI^^c$TF(YrWGjNZ#In5)caGno1Pv|;$){XWk%=YH$^*80}>W!Agi=Y96O-`)4wXP-OTwM_4mPs3kv?Mk^Dvn%^+nv!f<K5cYp#K?jDLL(~<3m<FKatW{gJbHecPOaN@vuUHXaeg78k^Lh4>e&72^{?gUZ};mzJYr--pJBa+M}&kbzG<H!k)durGOSN{sM{`6y+#dxd$qFu_6hd?$G<G@Di}L=Up=hqVmMDUP}=!(Kc!tY*9mX<j6Np(%Of3>c8pmhyeo?SKNsAjZ1dxM;q7^ci@))*=tlAT&=qk;%|0srj$fN8t@mmnyt97-c>i?b?}#ppI62=Y2w&^Q4B;bkq1<1tnZg^twU&AZeY_(6B_DyG5wStp`qo#%>s{;af&Z_AB!8c~!W+9Ypj>TlXNfcA4*XkJ+$enb=_s+c-9Y@N;|_`6>-USKKJgcYcfB34K>VAQij}zU&w-!YcCYa5dv3JyjuqLYTw~Xj_0n%IPoh4HLJvy({RI=nulNzfDbvdo{`e9pSFgMu^?W@&N#e9>ku3eVXSeX$vw^7R@vr7d+?%@)KV=H|(l=L%f7~YUws4fY@oO*MwX+NOvsvPVFS#E4z}=grUGq!HxEmAKfIpjfK>VYsN&W2)lMsJgC)9sh9jT9&5xm*6ANU8pQm&q|4F0hdjtZYp8||GjPk5&}2J<Si#ZKv;jx*7psVh<L-#J!TdF@#&_!5EflE2zC@PSpO-?S&4FmF#z!uY1If^vI>Ew}Re;?m&HupgcpsAqwNGXKpA_oY7eb`!zZY;Yd)XJ=2T&u@{4zhdJtiPQAAg~FE~hWb43JzjLC|0GCx_xq#0KABMeKHnx{+(OY_#y3W5m_OBfp`M#pA%6LDsAuP%s89D~@Qt!B6TgGqS<h(9hly#cth`yU6ZpcZlf^FH75u%1m=8ZCPm}nKx?tS1haMMx<-vts{PZE>ZyfWN_(o`F)N?`>v@3JjWmeu?@?pR5H(E+RIHq+%oPa`;q(7(iSzzUjSx&6qh#b=Y&Y~^BC-sqeW$diB%8Sq467#LzvMCbxL{s#0lVzySt*S{@-kduYe0;iDl0QomjN{ZWw6|N{rB+^F&<Fg((0Htax~PBVg{Nh_Iu=1aAJ+1oZ|&YYt-R}5QSdq5O_%m&1n-Rbg!s3d3$484-JAN-52?0=O1lOJpgsd<V}E|0XM@uE&hnUV+k1}?zSk=3&rQmr+y=HZNuQl{iIq3o{Ec$`YRngVKpB+l8OMiMzn}Rke_<T&j+J?6B$oysmt&38BkT9*htb8o=V#+HE3Lfiz*6w@*#C)k^jnoacpfdjvQE}txgv<)=9BFIx?{`^%+uW7;}z3%g_So~cL!f@(i|!8T`tro-6+}5jgMD<ko>E&flqFV{&^dZ{*TOramn})`@HW*Dc2~N9{hmj@Q>J<XyxrM8iSuODgj#a?*GDx%dEWp`fJp4$;NqDpZ{DI|KGaym2y8`n=j+O`knBO+Q(9)U*_1QpN&6XUq=33ST9vdtrdOnFX5d-3k$EWy|i8Y&pZ|082v5kbL)P*m3Leogz;_MR@$Zi@#L~sd#eX5vGT@`kKkW9MCxzP3En;{z04n@tFO#|t;%EJ&7b2iulzqGS$RDm41B9QvMyXfj}U)q73@p@{Ut`~x9&I8r$CBR+WAf9Wzrub!E43(VqZE~Y_<6BeTe>Sq+{QEy26n1ZaqMpb7O=z>Rc6n{l_~fcStbylX=y>cs-;c_=P(sNqYisBTjIET~eRAv*r2Yy8aX5Tz$A&`0PK){BgaxhB)WT%RXRCzMSO6f0G~kgJ&OmcmZ)vCt$q<x03UcnGw9}-g@wr=1V_2hMWcO*|%ShS?R?O>jb{@SF-M0mrkMFAO8VgV)Ak;uO<BnzVx`cQtp3Fg8x__^C4YVJb&|p|GbX=IJd;gyQ((wT3`COG?be&RQgdH(k5EgWy53eZ<2uX-m-A%KWF!YD0gHJJTFI<87<?Uc`xQ|U^wQ}uC`KtXTm1T!xHZ>Ke>;2c>TJ|YaesfU*}y<&T|iMep}CLy_luvgD>;kYyCQ#$D<$O-yZi`?>Whb<(Ig|mFIGf)t1gdoWT=frTx9Jzq$ULje72H;I+?q_|Ns>K4bTph4wnG9kKSCJ~kHZdKcsM9Q5#7<33)`K~tNCdKT&BwXc5WU$^(#SM~mrz2^hR*FI_j%6;kd+W$Sg9u()b|7(lJqg{KSV_bNC@bI6<i{}S(?I?`<@pfM45D)KMQ_|}^<H#BbK65Uw=dWHN0`)Im((8F`FFXYGZ}Sl4dd_LR27xd13jM(6sfYhOANV{qjtxNk$huzV6aClzh?6eJ>pbJ(&3Aph&u`?lzE!=>Z^rT-;D3GLb$+m)?|}9`>gsi#@$im1?Yz!2uJ-LwpF?HV37_#V>~GJS!2e87uk*Ht*SbY4k$LuJ%PuJ|J9y`c2(NRyw%}Xv+dFujCq2C0DADU2>*2M9bG^>J#)I;xPmcLs=WP$~JQ(8rp5j*y{*i^f&i@|X^vnmI|Fsrn5$B&N7iAs&UT&Q5HA-UszpU%^KIP#*&o{nLX}Jn|$H@^X&k@&$Txi$gW?t_{pLx$b;ro<R&xv&%o!9HVNqd?F@k_Vydhhe_pXUkR6J6JRFun`QdA)~ft3F-AxQ5BOOTY0z=DT_LPvLbRUCtAF%ISSpUi%a+=TBqHFzIh|5_sqBP>j>pm$!+&_wo|v%Qs%{xsI1l5dTa)ulH{I>{P@VJXOxsdd?u!Cuy7T#?qGiq(5_BLwz2lpgu>_$-ZZHF@<+k*n&6@VzvtZ#SG!?msi6-AR-y_YNzan#=%9x+gDt`Id;bTy^?=UJmUBj!8xksaqy+4Ucx-Qfbo8RL-t!o=ZUE2(<m8tBXGN%Gxf?5h*SK5oLBVnp%TZQzaRSH!HK!TubH|>_=yh0uh?db#Q!EE=5tbS_?Nnma@WjXCFNEKM!7ix<lL{NPLuaXqe&-}JFDgz;m0?U_Xx9OON`4&1M{=_06Awm*40M;<QOUS(PAFTIo#n}9&x7TU5t4@eX+zTQV!)FE+y^MnpYbye1tFRpEP2-#JTb!S@gYME=rs`jZnYkH#SRqUfdSmer`10r&e{|CjIg5C*iei{x}ab-MB^cc~f{t;v78hUN4n<3wzcC@Jk0=68>$BoR<vOY~hWIF<T{Gy$|D2zZr<1Fi!fxd{=(EmH!-PSV!5%>|3LScNNTodw}nJe~@wy>B8%_Q1}NmlKwWf7V_rpaXmyQ{BuG0-lNg~OMZ}Zqhsg<;f-&jXG{9ud$6yr?Jc}>dLP6I4aYs$lb*tx*V@YZb=G~4_0+Sa@Q!QWVE*r2E$h_&q#68ARhD_K-H(*@rH^Wi_^*$kf0{Rq6h2Ic|B-%p-}ITCDsgAmNBvu$pCjWmZa3CNp*rAu=96`5o*pavjk9+xwCh89tfOLmv2RqVhH{U;!1z9h5P#R9O2XS`<V=zJl$bnK`Z+^>#2FDP^F&K&eF*jccwXXNos0E#X3{<@Z*+5_y(>pax%%dRgtzbU!Fmabz<j>*0&xb-z;m$tE9nn=o-4vT{jbSBuJz5eQsVu7LU{doFN}*hcCw5^r8MES03Y1vgltEBTJJ%*UGL$%S|_)xFXulgi2tl8-j}XTMtyxl;NLi3xY!qa%l)M@Up=&IY<!sT&1$Tbe0ovgT{kbtxNFWq^1f(XyLV3FcL<hx8f!Mn{g}h&itzf=<A;TxYRI~CK0hJ6D{nVhU&h^c63@}^5d1^R<GyZP@(vl7Nh$Cj5QOK#mtWw0=*dLk&Bp(n6F#l5#L;(-1s}c#{pNc_&P&>yq2T8Z!@BTKK|h4`5#F(=JN$#I&6N5itvf6EYBt2Y?X@FX@^7s!yemgF*<ZBEd*t5RzO9PzhTa)*qR!x+<jZqsq@RZsmVHT^K69Sb(-*w!N-;TyX;;${t-R5<6XHDVGDT@uXfxsUz|0uOXP<D7yRnJzj{Bi#SKGmI&UaJ}KzzSDaz4{8-;sG`UM+|CA^ovW=8Tu;fFpN))bnHz%GKkM-s!?=(T94B6@JGJ={MKVlfvu!Y*<Hm>%?I`r-Ba&o+keLp6?cZ>MG$~S=%Fi*Cd%=de4QzJD#UvJ~Xc?`-bs)rttRCA!yf|x7f$}h9l1OwX&|wb6I8Gx#Ii6|9&}nZW&i9;W;?p0so|M>0k5Y0C^7T6FQ?^U$&Ba7=6-QDc4!NmGI7s2jzL7SBaMO<=osH@iSJJ_XOi~PU&Z7Y*Y9js)YR~FhAZKmXrm5@B`LMljKd39&AUsZQEkKtg3)}fWd{pf6{S2X@&O>Eu|p(Cm@5Y3)2=Uyg5Cq@aFSzXz%VD(q7}|bl?luk@cb<o`iiY_^(q^e?NcB+ag`%{lZc458)jZ+R3`rd>_lXRBy9ccw_1J@;or|?Zv%uz8{3w=eNc<_OC7XC(gfC3GbR!1JBLXALO~|y1fwP+T&y&(3ahlezi|o;2p=mC+>yX%@bZLxgY0&gGJ^2RqH)NcxTi-S?}8TiSm5Z{~iecOnFfMYtc9lH|zvHxdZl9Uu~rLr>l?p{MifVD0_c7PdfLXJSl#!D&ToE>71M|%mRyrH_i;jzWuO?+$THJe=oc<AsfC=1O~}>Cv(Us;T?s>iEVVi{jG7QuJC%*Pq@GSqB*{Uq|^}JUT*#OQorK5%q#oZa^SPo!v58LgPgA%Gv59v`7#v1zR_qi_WR2Zgm)ZyJ4@={)PJeO>*W&O)!_%c|D4_}=N4_*DfkCx#Cvk991&8#mPZi3<{H^A^k3Ua{avFD!GHM`>3=gNo2+Z&$hIFbE(>Jb^}<(#cO|a{f7V~d$+$We=Z)es5vO1t+_N3KA@R+i>B8$9<M7?>_EL$XHJAYYZddFBV^Z;axi><1`<y7;-(LF;=i9)d!fU7A%JW8>o*C;Ss4)8Bawe?P?<U|}5%uJRv_m^LLiFNha(=fDx+A>ZCjj^I?>FF_R%N^JdiTf~5;t8r+5a3rt{2{H)EV{Ex3-h=3avz(m!~mr@BbzB(F!aP-ql&dcSP5G`A({jj6;3W`(YhT_m%zDc{@sYXJ{wH5Br4g2x&uvcNFXB5Po+@c|I722ZDdG0_!f%L5X9=6hpa@zbumaA1i?Ohyw-DuK0xmq(0iJ7E*4{dvgC`KUh=dlNMfikmO5EOG7;y$+^L(v_<w6=Y|c!JNJ!7`~yA`-)V~y-aJ|y=c{ZP<okklF9PxF445r;{u;9GUG@5<p<X9&|9p7cdWpBZ58{mOvRm5IH;X)<o!vXZzu{5L&*;g*n<Hz0FB^*I%Y)3a-d(HS;J%>Ng6R@}UGBwL&$u@?PV*caRS)+tX^-K5yD`p_M}iS&@kQayF-dY>(ej1jIeB@8@cM>Pw<TYhUuKGb>LB>PYWR!rK2>G?>9_0i-p3c`o74zduV(Hnh*LS>CrKY29BbvZD*l)!AKs4>J^8KNUpRi+gZcK1_W-evgf|l(p*|t=<vi=*T_ttljTsAMpLec3hd33kWB!ELqGUciJ0rXv+!*D)oq~H{bBFNGaYyb-{1yLTzihi4{@)+FCARN1`A*`fje9zK$X;oe(XT7cnXjWz?v#A!=Y>hQUw!Ha|K(vf#BY1ecp2wjg;D=i>rkItQ8B`IGLIsDuWRD}O`zP58TXySo5?va4<F-vW!feP?>P1j{=47G{^|$}N1S}iF%R>clXJK|tS|0Os%1r-VPj<7xi*#(UN7@DP59S|GQZ4O*N#ZJ4TFD{d><>ydBAn~itw%?2l0D~A-CnZ;h1|=cs*e|{LM9Ze<bhhJN%~bA1cc^Uq6~8yyK&W{?Ario+ElnG|FA{MEY4z<-8p{0_DCLiSK(I@w)|WPYaY=E9tt}EAL_*RQ3a3;CFo2+8&1XwtXb`FU|w_E}_+GDCY;G!7kzLm8W0FywXyvync8f%Kf$!z5~Y2Mw|)%L7a-K<-DflC<gyR<<UR$5~aPyH_r}Bz7Z|pUwIYo3&+L@Z*Q^y{(X<*Tu}J6ykBZ#aIdD>%QqJP)Mvswr=`R1O}2b1=XU#@Ov3Aa$9V5`UG4*21-Ib4&bVaUXVgfO_dD0TnZi51>I(l`lVp6gU6b(MdA$7{iI=??&YvUj`w3^}PqHqI=)rhyCgD4i>t#k6U*mQKd2Sjn{BZ6omV|P*6qECnzTy(zzi04!b<_hn?>NsN!*{Ya-LUQwbI9}1G$-P`eBl+w<(&=lB)S>=Z*9OnlRZMtX~x-cxF^d|6y;{mDEqx@I=<&QR@cTn$-6-6W9$pwZ(Voh<>Rss>r-yx{%lNP#MwMb&R0h6>%trB&Y=I#oW%RYnpg6Cc5GUYdz2pw%KN7C<`F!%4<Eq%X*5-MZSEZDSJ!FYXJ<Vr`?0=$8qNj9|3d%d*@NHJ9Pci?WB)Y7KmN7syN-f?<6M&;_byu8Gu#&)swKSMunq2|9v715kK@0sWqh;?8DxBoMo*=F=J<VbuF>C}mHs!sdbP*O+do{#eM8JzJU8Bl3$NYJf%~L(b~y*RBHQ4*x1JB<c>bpJn?9=<&Xs09nJ0R{I;o!{=C+KdS!xpY)rYZo@6LG>=gOa3%l@gq9*%khMu8u7ALI21_f+=ee)wJ#*AIN(AlWw@TkC_*9EkbTGYsdfmxu5jIC(AB-J6Zz@2n8s8C(zJTjzlA#-kwkPZ<EdM-uK$7k-d(%;8&bFWyg=aWN0Y;G7;f0P|<NkMxh3^bYqZ%~H^x-@owU^#Q|$*M6F{Q~I-@pOoWxU}D|Hp2GWC%wgFloN>Vz_Y*^8eDx2@HetOwWPHu{%`p%B=i>bSBo^)68G`qu*^&5t&>=tU&jm}%I&zlzh<#;ZBIeJGiPA3DzN`5CnolX&=gqS#Wj>kx)(G$1KL^jFLoqmK{xBE!3av6r|C{z$oPX-~N1O^vu^#{EjQ6ke^@P_))x&<0V<67+A1fk$p^NC}T`sK0W`(gnT7_Vq)Q-mZE!ijSbKKm7_WoK;+T|)g5A8mufw!fCuXSCX|7OBc%;%*mW!&vKGvQqD=Nt6%>)tXhn)5E++d6)U@$C^M>)IZ68t*x^mVnRjLgKi-Y$Lqu^#qiA8Sj01Oec9CGB>8;xw-GE?8DC7OYyvVp<#dcbOgTxx!e!;DSLddzDnEVyM!ZsXPl$oMoRx1>x$uCH0>+l%_w|d)eeNp{j>AJBAl~oKZXB+sp$6ypYWaP7yK?pyA_Rd@9jJCy~uGRC&st;dU?(o4>aNRE`xB+x%4~kzmtEL^S-0+*YbQfbL^1yptmnCyz`64(q6-b^R02;CcGIm7yE+)=VWvBX}tIQ2cqACcgXh<XTwK${|?9RN3@D-<s9N1yjR|L^;gwV&n1uWooi00@WzP-=;!MX<7B*2y9jSK#qTAxkrU*;*O}`L?oA3;mUX11c9QoASJFA*T}Rg={-FQjJQ=bOzjOJBeOoiXm-k<1sowaV*O^e%|HN|qj`F*Y_%1p%6wfc`CV3Bb+`Nz9A91~Ce+`p!qx1MUd9QO6Xe#||)Q-h>-X%ZacW~tn;T%=6gv={5=R5o^^3-XRyRL)$-orRH9^b*1p2hkaW6J%!*|7usbCtz8|GVG9t-O6!O|-ZBb@?8ukI`_CaL>Rwyixr%81FW6U+-wR2j}(^ALP5UmR1$__}XK%tK+t*Vjswj-;-WS#QrncIqPscuU{Kq&GM{;>uYzF-I7_$r}gh+`KhrY)t^WI?|*7Mu=@YiPmOEV{Qv%`@e#EI-13m3@PE`Wy2Zx^{E*zA)QW#c{EocR>1@EK-Ext<;_{PMqVN|sq(3Bgg#N3jk1)++t9T{JD{d`qh0oDmMZa^ze-bP1qg!5+%Wi}HC%I?DN?##X`U3F<#!*<+J3HG_iMS4RCC2sG%C|jv#W~#4lw4Etp7f&3+mu*w<%m6;vfpdK?^*Ycv|qE%`z`goz<#+vel6R0mcD1nUtz5GOjmw>?BD&wYuWbvY>U!0i0cryC!daXVH@VqOAXk^Vk>=~Sm__tJaJ2UE+M6D+P{AaHzQX18*<9ehuDW{DozomDV>2hJ+bmD!L)S5KhQ2hT$R2>h_}0C3w>+T_TUnXvxRv}F#WEDQ~E0PPsDeLJ)E+0*dPl3O1aB;$|tuCd6oW&{vJE0Te4DDwV^LmTRXbtE4Tf^t)IK4p&Qra_|)XMDBRPAv_9k;lI!7?-fn43-G{i3J63PE%y3J*23z62#2!xB)rgfY$9#Q=l@xYMKH_S$E7HzK+?#d}V#Ni}_F$#+Qz|lVQQEnP11vr&JsZ>V6Duh|E-!I5`sOCi&9rRP{`4zPthhq7^U}W%vBNDrnO2>4d8St<E>9nSio!K03I|gZj-@C(pV~n@pLia9l)Z^saqBI%2P?gmqVNXlBnzHLd!}2a63?TZL{a>5;^oY%xER{Yi5C(py@GzriC2(cN<Ei&DRBZt;mMSVZV4wh(ZY>&%Xj3*lAA~_oO+lA52Zbp*uxEWOMBLRFuAd`hf>-zZ+rR#5-a_!C9N~1J^8k@Jy_{_)D<ka7VSV{4_C%5Uz0CGt`@lp)MYK$PWwyZubJ;lOS;0jsa0BW;^O3+x}`4dGPH|R3el%HeF{-m*Z!UF${s*bIE+%4vBKDgp8gIaKb1I!dBe!{W84A6O3$PWppS!T^N6ck?0)ne%yI&$%Mcf4zvL#aL)%WQ`m-9bCtcb7iIr|bzd9DIbWQ3O7Cex4e_{`(>{-N0PjSm2+EbWkAh~w56&^wzP27(5Am&s2_tbNUhtO8CfP6Ill|6>s1P$wP0_`!(KZkw^#0j*Q5>I9xrNfEaxTP!YR<y&(4JQsK9>YB0#5(;|zIwD<u@BnOu1Q;`v}2x{wCk~~AuMA!+cJiD2<<k^+m(6<v1;2g4SU!EVh`uk{@vdc-at`!EA=|<-+fr&ZPamY*{EU6<H$K_ucK_Fze<m%y^(k|)0CY|y_#61&!D}UcnPu6E9tkIcqRGS)YFJ(6L+CD+%k$j2DxeEx{&KZdlYeZ;_mcOx}gOJ(C$I(Nv}koO0<ho2M~MGN>dd6g1RX27sR>P2L|h|aBtcMaS!%$U-n;r;y8{;f8u4d)mTlTy?}TYZM83}y`Uzs(rO-7V@wrG&EvM@!-*BwnOJedXe+GtNA-MKNKsfl1JxW*&wDk$)(~&w_^u&V<C{n>k-P^_qCJ{eanosga3W)jrmgyZHt|Z@)5%qKOCxfnX?G#ljkp_QDf|_EN^`uvA}&Du1;?)dvC{rbQ@RH6SHzz3gIP{6+trOSiDlPdS|jGEK|G0kEO9LRXAQCHUv-95&jj`CXzo5kf9saI6omt*D-Z_|7pEwki8>c?CgNW-h|4VpG;l5px0(C_;>FaBi5C;Mq|QU!lDG;bqgzIh%V^>1lUI5l@d)B$)V~oQBYr^rH}M1Fw-kj7*`U9+0V`3s3`OB@*oS3^o6}bK3ES3^`U(4>3UN!;^9i|Q#3NXrC*<A|KVY4nkSjx6h-E$@7eHK>W2bNc$4lYj95aO#cYs)NkKB@~ssDEaTG@|@l|E`oi=-$VL`kKOlBaG-BYsS~7wt6qA0?N@^xrLZ2({u)T5N@*+!8^2inhXk&_2n0e^~OKWFF<4g;+^ure`9KV0tFvoWzRrC01M~+6p%(R@`3N3hyLV+|RW4QnzN>4r0aKrv90D2W_Qy(eD=V4&oj3y+&SfzBbq%taJt&<QDxa(=KlV_O<=%qteqeP1y=Jqo3jei51t0w!+<r71xAVacyWTtP?A)1#N}v6DzI}ZH225E3P{2M${#lmW5bxC1`taHRj7g`yY4PN)anQA8{$Bl_2*ewc_t<$gk2*xaG12?lO4~wy~U>#EMH{+6m%=w3WU|taL^j@?0mrNuTSMbcHk9AlEtOO79`wL;Ik`-bGQk14ZFb${zZ6pk0u9yjzM<htkKBR*YEbtkml6Jv;pykSj(mE7w**3syRWx|aoKr>$a?qMe;Mh&YHok>p2GM>4Gx^N+Knd9c!lDdRXU<2W`R+<^9O=25<jh!uB;w!+7W6?cZV!uK@nmCC+D`#8m9o;$QvzBlwy+$-81tn>}a9s2*5X^K-9k*~<*C01M>8*Gj9xfr=(<UP0uZ9n2-#Kk!OOA&v`HRDH4t;1U6YLQpC0qsV_rD-d%)2}qKhx?$R>`xl7oj#w4?W~*1tDYx{SI>;c^#4Rrd9vA%rfd&Z`giIoZYjw4Rp_6MoboA1z8*QH3s}<BbL9`>0u<#_o6^xO?Z|bsaLR5;taKatDZ3k`Bl$M;X+deg{%lFCxK7O9jeHfR)g$(BrOB&)dc?W)i2e4M{r-Wx!f!Z_@)EzY<he(AWSPg2TpK3wBCetFTt_)Hto_Wy9cZ_v-JG}sZC~olO!IIm-a*FPMSqnqBlkpqYPI+ITI`Axg+08on@}sRvc(RhR3u-Pd35587TcfsY~)pXN!lK)bbU%$=Cd(PJulSrRXuanb3YT?s@mSq%@1=+7`3v86DvL1ErV%?Tl@yo9!8&FrVS$QM_b8I@<VB>yuIi*h*;?n)R7iEl=cw%jUZNf617T?A&wzGfqn|lr>$@Tbqw)*+8f;xPkSxx`ILC(UrSr%+eaV8t)WgJ-c5Tq{S-dqmV>lU(%wg(lf?VzvythFzeIh^Ef=XzGM^{yq9yGd<*-{$lRHfAH1Q#~9HD)PqWG=UJBhavJINoTy_0x1@ou);Nn7DW+6qsj9Yei_edVzeIEK^6O`|=IqUOLzazicLVDcl0BW(Z9%Lt0XqbLf0@0KXq3Qwl3@C@3~l*#0$Gfi=G+%lWoZ1M^(qpi}H(w@WoQ<+zlKbqWV@(NFJ%OcvNX-_4$n0P92EOD%*p0TWh(o0xwEd7^Q(&kW>u#QWKS5U7aUO~K>qHqdjgIjiy+dys=%i2Imrq2epA(`omEa`jbqwpr$i-?nn7t-EDynuKw{rA#dN7+Q5b<}axh6OLAokYJlVx{L&tMrM)6Ui^9-&~5~$5V$Ak0<U+>Ef0ka$PK3EAm0attkq3rtU!8nYcf-O6y7-LOz6cSEjcm9zZ>WIE1#6UgW#dU)kM>yHG1Tm^hd|p0rj>@5i)(#NCOzv)!S@D&KJW3}hb<x8Q;7%ZbD)-&odr0`YgWzhhfGX#?1nSxg(tbcM%I6rM>vi+CRKSmO1xXA!R^UQK_+9i+XQ_yDoeE9tkIcqRG$l=E&mMeaPgQ^XhCa+dZ5isCO(pRwQrv=6WjXIMAYhIn$y-bh(bKAt|Ry`Fh9hWuFe<qjL>xtj0WXe(?IEAA-mZLFtB?kw%2tgA`;1hL{S(pLCKV#S@Kt#BH#=b4p8tn^-{dDg$;j??zwH0IkwdlyCFREok!D97o)oqj5P3$fx-h!yt(ZH3#lw57|J{{Qq(G5-6f=C|hc4>SI+IlX^YWz9Lv9qaRttlG8Apzb5JbngGuCEg76byfQxcR(R|'

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
