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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_003.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_003.stl', 'source_sha256': 'c39d232827834a70d00bb1683f571183bd4b80bc3e8fc2e615ccc334c7a8649e', 'input_faces': 592, 'input_vertices': 530, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4990159869194031, -0.3272360563278198, -0.12054763734340668], [-0.19020694494247437, 0.08322793245315552, 0.12054615467786789]]}
GEOMETRY_BASE85 = 'c$}r233v|I+y76ZmJnK0?TnOITWXD^GNrXg?Mo~fOSFpEm!Bm@Y%R4U)<nnzwWju^NX?+FC?fW1(MM3asik)6J!j5${GNL{|Lgi+@2l5+eLwm1&i$M@GtXXa*E+{5uQU0l98+da^3|xxn5ba(IvW!`V${HX(IelE8TOw5_L}X*A14>I?HtjrdjK25CRFSnJ+j}3iVc*CjRu5Otfo{PFm%MI5q)B!hK}eTEqt>+gGWYlKl0-~!=m}mmFm>0QBA2;xtcOb`CtCY%a>sJ{`%SEsc83)iL~lm+;95(DCvErF76Na^F~%(=|g7h^zYXlpS5bczi05)?p53U=lD)Y&+^XL>F?Q-QnuHcXYDaPyl+I3r#D7-AnWlxmR^ZHPu8P3KKeXaj|#8%?6A|zTiuiPczN~hEaLT<e;l>@&&HE=I-Xf`$vUkW@R{?;?K<8{k0<keVK;5B^gKl7JKm_@i_BLXuk<4G9nYE`BJ-6-`)%*rGLp=9ymCE_%-0&C|7aSS?|5U$NHX7;y+is}SCRRSS7uD2=W&+wY{(=s-|_l`m1Mpa_@&&p7H8ARIs@RVpG_z0sk%VUsnUe52VNa?nXadb^h$@zbUpA|!6x*0t4)`4`VOV@;jPH+bbeLojrX?G`S421q4a!B8Y1^UK7gJt$LA=!i|oTh>8;<&><aht;{xb@Hti|*r&=hP?|5b46S97ziS(@96S98C8-+vZ`n!E7{V!X;GCjPqIfkykEBxXZx_)^5_|~t;{qbr8d0hFj$b84Ev)YmQR<`tPcsnxR@%r5pbpE<}a?aSUbUwUQ<_Mj?R(d1n5jr29_3ldM8|y2}<4t(5+w}0h994+-t&`sPt@7@05APfIfOw@x1$kV(<H;N?QhM!!c+zhLmy`a*U~;@K{o?K9c$woTZ70X;c=eaT<am`Q1*Pv2K(7aQJ-jSk=VR%Oh;n3|j#u6dp!1godmrzTV9(<<R`>tj-nSl^d&xepl3s6;xtClIdYJ81*Yl3!*-6*)BfQ~yesnx@KTkC;b;Q2?n8Rd$)MnD_oez`aWmV>8*nUTe&8CMpW~v*>Ix9<Wby7Emdw6Y1iOpm^9Y;y;I$p;suH$vQulx2*US7>!OV(p`!2Hc?$$A`bgl^yD<#pG7I^NgcwV(Go*q$Bylw1$iUFo%TpVI5!*HrfBPbA0Xc&kwjvd=2K9#n(wo8#{-rR$7sEN^%3F*+Y!$<Cnr25)W3Ap7vr8^_3eeNhoPXXapfJ-}NX2a|QO>-prq4N0TdExa~9h|JNi!8Z>ga~!XBN~72L^xqEK^FM7(=ffNCAEooB!52JA=fi75ThsY7E=r#`hR%mK-W*NmPlvxfiq41kO&&w{^V~PKS8wN~_jh>KFmwyKU3jZSr7hte-Z+<+UJuFJ<?YU@POk@e)d(Q-Rd{Pg0GaQ2eRy>`fB6@3ogeJmM&`h4RrhTpb1KKn^)xw8`{9k7-N|~aO6bq*PS)diz1;;ep9Rj7bIxjHzT<tJv&eisKzg-N7MbsO-#(4Z*SF7-zF`~sJO!_Xw4u*aIi|?@N1ksry?ozV#Os05>n&<+4fpWAb1#TzsT1V!E?P?G7}B$eOKJaradLj$QFMRcjla|B{zOZ!{*+Gl2cDH4MfYF*Snk7|Jaj(1vZ4}QXE^$&RieiWZ;i}D=3AHgdLFL|?>=7Z!o2V7dG6;0c%SR}OLh8P&tHyLT+bt{)H~9*ue^gCS4rvBdX;yO<H~;hTRTS#r27MJbsI>pH|5qhb|w{GMb_!~g9lT*yb*aYg{%`^9Z+}`Ij+R-ZEv~u$MMRis;Bpbr>*qzdfo_w?DJCib8U=p4{zj4Tj}Lh*Zw=+x5@Q99-1WA$*R)x3vYx}ru*jjTb1ZOz_Vjj=z0HPk=&oi1iBCKEaL##2kX4_#)1R%xZthO1UmnxL2}NJXtGZ0N9nDwXtGYLN?+*@w5P`luWEtxc;S8HbJ634XLH-r{rp~)>#y<+o#Xfihv<5a)|Bfh_R9v-!y7>{bdJ-1b_iXM(|_&y26FwEDrtLdL(A3V{sOO$X}Ox-zk=lar(MZ<9IuByBkN)C>fNVgJ&yMs?n>69K74k_{`cFjk@Z*)q}OAwk@Z+{H*K%(-MHTL@XGEqGDn3s;?l?*$NQ#lTu;{7;=1gQPyB)$Z*%FjUWs3j{+8$E`VT)^YkGKXL)02Fr-k&&n5Z@39^OcJw3hfMr(}P@Ds(<PyHuI<v$RZkTpg~gGd;X|Vgx;|jnZq&Mv&ujysylab;Ku{^1QITWWM9okXGb)8NBspOLDx9*Nz2|`D(qrp2us|-RpV0R-Xjv|H?^UcftG4<fO0blwS_oeeTEAveL6d^zq;EitF)ThgaQ?!wa4tu>DWL^zjW|TN6wl9~w8YJv%#ms+ZU6WX~n*zgJH7=X0(9uJoFF{qQVl%=B;%Zyb4lj+eK(yN=hH<2qiZ-?8le4-Im=FMa2*d0zd#>nUWuTILVitF>#9<6@5gJ&CTfwDd+qJ-Yw3580mWt4Q|&UJnVL@7dqJB3X}>|A1WQ!3yL$RN>XR707j{PTM2bQ};T3{Qz%8ET8MuZymcv_o4h!=~wnyVS0G2;i>sv{l2h1D~PW!OZHEBgRTc&eOzI_SHE8L4Z07bN67VrM=dwK{PHvLUj6#n-pk2(Z`4QL?#4T0j^mZ(P2#;gtJNglYYuzw4xRsQN4cH^CE4`wdL<>9T+bPe<-Ua`l77cq%CZD6Z|q7+@S0<#FD3KU)JAfCZZnDWuY6mse>q$1<<)aF6UlL@mF52AS+Ru7&lxJ`JP2N9dU)k#=t8f4Yj*H5;(sn8Z@2R0MP6RH(Tl7{o%EXLdf2`Q`}-;uR*<}YV|%4H0t=GYZ>(mR?X}tirkft#cbYyPI-Vuc$1%OghOceEtt9PlpCbJ$|4bu(Y7yJ37avR^b3y`T|KEqn9DT=Z`+Ey^sDke0jq3}^{f=E8F2Cn^`w*GWHU`^XyEkfr>EV@TBPWpguio5e_dl)>YkGLKP5D?d|Hl=!H&O?THa$H1yZ>l1|MqCxD-m19njT(D*)*2)H*F&49PBiN_-lpadU94AW_oy~YlUH?f9ebSb6a1P0=>xkfBn(+T8--)_WS$i$K~g|lgn#lPT%!%PWVmIujd$Vd*wy`rKG>!e*5!8<53oQ9M&@;?C(p|&$H-$MqaYtPpZrNZ4~qM^h5ITt^H8@eWh_`@*>m2vmul1`;p_><u<lg{%p6z^zeE}_a*-Q)`HjM{03*Im>ymkbjH4}^vxg1^$)#s#@>gJA3K;Ho~_o_?)UIUt1}(QoU|WouT-4f+4S&Q#PrVo{l@UKa?aSCB}@;mURYb)zu&rXM)q(0h^&WcU&;Ogm3o^VUauL_+kXy=*dpg_PHkp-c;(@uX8!$J{mpXyfy2q|Dq9m}|J1?*Ob@Rvd~E>Pp9^#3oCbeJnjT*1c_Wha&lzBQtNh##Ob>57j-%%VUhNn60ok|tjpRN&%V=SGcwgikGRN^&ov&Mv^HsXATxZe}+HamcZO?7gsGI5Gtqyg&`Oi_Fp0vHM=)yXthgXJ8tmEIWR{K!)N52?kdU$K_vq7Z4cyrl5xo<zy!|OAm`jP&}*{AIDAC)@J^zfE1WgNMF%pYv8Rev$c^zgnd&qtB-n7qXHYR~WDOb>4*e;Y^EGiIh-&x)Q?Ob@SI?m_Oq>~?3{>+ifZ%k=Qt@M^Qj^-!#-oPVOqXQqcY3RL-w^j9w-=gce`Pu365Di)0={qN_J>oHEvH$A+f%GaMSeb#R$?c1HvbP<^kuZA{V<lpbBea7~dtKWiGoc_qR_RnlcTl;%!qt?$~itARL+EDsGGwja+wR`8JzfoR#rj!)kikq88yf)na{y;r9!|rDzilYB~ls(5cSTjAm9x>2<-g)UUNBhgw53e_t{d(&HWc|MP+D$b*yw%}D`}Kxi@OhU1aakjAy}7(PU0!e2H&?U#=V&#G*yqdbS(noCb^eOebk4>e^GpwKq(|EC*YtO-EdTvfn{=ORdU)2m+g#d@{rp$I^uAuQU)}K)S*Ln&)?(AcTm5Ir*U72t$vU;+kL>Hm?R}3Q+SiYId5QF~F}7z3@_J)O=SiQk$^Kl}*Er6;UF+vK>GejoXCKEdwb%2-IJzFKxZ&klh2rvkX#7~|w{5dOH&;)WOtSYO&oJrZirAiAZ7*N9?-@ka&xZC$@$$yQNc(-6y5<w<-y3Luu3<baYQKMBK?BJ?EAMym^w!Ca_WP8V9@i~vCi|@gJ;?d>t-<?Hm$z!;{ifqF$G6Va4{z0U^<(}2>UZ{My~|@i6}QLv`j^Lf*W5lZ-S#@Xda@zeAAPXgf45hjVE-NO9B=Jbv>)Es-_q`9Q|poA)${eY``N~-<amvFTcvMRj2y3y>y4d$dcyyBeJ4iRUhnhu335OBq4-KKuO}C`-+!^T=_mZJf2HbAaz5K|g51BFrlxv%mM1mU&T$J*`0uk)v9RoSJofpeFE&#8#6bJ|PR;CSdtEOteY3i@H*TMi{b{!{{nxMMm!EsPJv${o_tvc|ndJUb<&NA3m-pSeE%#y5De3j*_U$sWx9m?kDLpG=U*}r6E-oJ;?-w^Z+jCxe-?=Eyeg%(v?tbi>5#s8{zB!&{OwRP*A8pP}*<a(GO#l5<&4F@%9+V~fqsM=@+ROVoe`kLl&W02t`=cCcB>P=no7u?j*V7A-^($o(?b~&GEqm!I((hak?tXZupB4D^xc~L3b<CE><?^gpw(K9h?zsQ`!gv-T*YEPmfe3lL8KaJq`&a4Jvft&k>{YTqSKH(M_fvhB{GP(?*#!ALh2FHzasT_fGA^I}dAr-Qck|hwx3j%(N$)&v^eblfyS-JZnBA`@R6Xv0y&08q%lVGS^=AE*OU{4t+cE#^*%vcG&VT9U^=#CcK>MBB9qQ_Ld~H|1^LXy=cb=!*{n)pE^*fJ;?tYw?fAz!vtKWGZALi<Z*WLZj_3Z9<u4i|@bKSbVbAKsZV-4}n{W12S^fmI>|9u#H6m5S##fq$3NWAkpv#|7fsoc^lh2?&xOqc#j4(ZExwLceQ@sZR!bLL6UG6SVQSwPMy87BMp1{@*RZMOXUkPUt=|NE-dntcB1bzy<L-#nK7kFRX6U6^fqcJ;pW0cmpn-Da}C`z`5DKbP}o?yx^cWo3Vt{=hByJ<SE(_Ik_}=^xaS_q+1j?Dr|G`OnfXDlh-Lgu*kW?|Dl4T>a$r5HUx-PpO?HeQbohe#VTHzT5%n-;S2|-^}rIiN7>azTS9Ger~Vd*qq^izKkseJ|`ague<%xA@X+9Tz>p?>JOxl_4qo(%lC1cR*>}=mt$<tHqR%=r3|h+)ApavrTZ}L&J24_@)WXf`lILeap<EblYM4Ctd-Z})=}iV=xgNXtNN@F<UCphSK04JSim51-jznN_WNA6Z2-AWlp%lHpQEz=eaUsDMt7IKa#V)@b*S&1IN8o3y)*o;Tm4Ku+q1x4bpLhvIo?a}yuKX|f4F;w|NTfg7+`ySdpB}^m1koo5$`-c-{-y^`P(LQ%Ixc@mg0xND~P?$2K4d!t0qE<KTdl8Rg;0W|Ns7~N&TAt*S~7=Z2)6m@j8SOybHMnybJs#auN7Ta6IyJa6EVxavFFRI1Z_U<G``VvEW$n7?j}2$SL5-;Hk*z;Hlu*$T{HI-~{AiZ~}M}aw~WfcsFtncsKYP<agk2z`vpd-$Z^7z6rj8%mCj2|AIUQ7MThD1$+&e1-=H(MxFv^gMG*|U?2E0@*Maw_#*NL@I~;CD8cE-{or(PGI9-A<T|j(6=0Ex;AHSj<Y(ZS;Bm+aV3Cu+BL4#xIT0*!JXqwX;Bnv?$fe*J;AJSm%aKXo<=_<L5^xIGKrRFu;8f%Sa4L8uaz1z^colLUSma!=$kkwx+rg{A+mIG`8`wl10gF5gHo*r_f)AnuA4OgV9|a#rUIiZqpFmy#p8%gk{tP||K8?HtJ`FyL{0V#(d>(lLEOH<CJoszmGVs^nFHnNlBA0{Lg4ZKc!0W*qkOp`Icq1|uoQiX~5hXYcxeA;H-i#8w1Gx>n1H2Pyf_H-VA`gJy<rU8BJznYj`Q;$58@$AGmiT!OueIW7nAevm!Ml)qz<bcY3zd#JU-R0{>ng87ykdBLj1ru}D^$E};nkj36tDMrwcyo~S8MT9juPA$*#g`c+yMDLxB<8(N^o6d6gUdESr_>>xGuN~N^l4=6dVFB#_Kg?DP$-(6mv_V1iy}ckvUO<^C8=V^MS?R?R*8<4%r^u4&2*s?|P#IM<WM<qrpRYjpQ|%*92ZukkgTq!NM=%^%<{u$VB8Ku<*-x#q*krT#8%<7PXnzLiC9I6eV~Xax-`uI2JXA*LalR5lmi7B4dzaz%k$yWGpxqGX?kL)eD>gcCJam{ZWFuB71_ng1aD7z+J#Akek6Pz?)Elw=;Ra5V;$<8N3^O6}c3=6#ID<C3qDw5uAwgvI-?Q6*(O|9p^U{ITkE(C^!{78#xdxG73B!+y~hLEV4CNWJ_=#a7W|^;0R<r<Okq-;D#u{;mDR?(Ni5W_`??~%PT*!2sjv75LpCV5L_H3xHPgX_)T6Fc~!-2)xz!7f~$_K2(Au}K$ZrV#!SKa_(BWvD#z;~|M?EDXG~rX;=CS0{t7+>K7tZ_0wwq-l;EFHg0Jv8i#*Tk4DvGa3it~8FC(9UFN1$X-T|LPX7c)$*HK;>$V~7-<PBsdI1|5n19=DhB{B^qcnwPMFDSvck$1qi!G9wkf}bE?ARmGs;&@&l%LGV%0nQm9GZ-x9hz!Kf!Qen}9$p2Ig^<DELf|s!5kD746@q_<S6yDUdDTJIL)Hb?12;qoZh))>7Fh$_09>C}C0-T4BHskp2Z!-0!K)Nltf`{kIt7<RhJnM-FSszW2(lEo2>1<T3Gf@>*HMCtA;Z80k>!wK;4rLNaP9zkUwQ>u4*UxEAAa5fkdIM<AE5r?bq^)@ca-2;$OqsD_}yDbG5;2R7W^BNC0IcT4ne*NeiP>)1SPmUvJ$vFI20wg8nQmPKF)77l;A2T!EYmLfpZ7)YnN9pl;Bs8Il!-g1CasXKrlnT2$0Oc{{+Z<3jPQD1o;U31pFBJ0Q?yI5cxOwA^1M>F8Dt99`ZK$9{3LO5AYrEU&!CVe}Qiye*@nF|A~AC{uBHh`C6dl=ivN-G7Ez9g9{*E1s4DZBlCfS!FiEE;Jn~G$lT!EIG2K(@HI5$^#Mw7b7V`f$hP1Qd9~uz9woR9vN^ap`r9Bof!lyPBD;b+g1hh<!7GN>D3st~$WOq-z=M$kz=OdbBm06s2KPty2KNVR$VjjT?uqOI?t*ppL<#PW65NZ|NM56P4Mh$I4+RfG4gn7We}o(e{s`O;84d0SjzabUM}d1Fdx3j^yCJ)RyMa3+JApfcBam&u?Ra(I)fyQAZVhgMYzr3I5-hSQxCOWwO7Q!<8u3zjHRiRCKSW&Pb%57uUK@CAMeYP|1%JhBKXM;(CwM332;R#po7WCrpYZyK*AQefxB{=Xyx!u~lvg)i&3QHB)r40gl;ALw;M%;}AUhzNfScg=JD>z>$X4K1xE&4I4XlA@AqRlPaje6!>_u)tt^;oYuSW@9&Z{%89=tjsBf*`({ZNtEn~%WB$R6Mxn3arN4qlGiN=A*w-hP4{jvNgh4*m~H@FZk1I2ki1p#)FmHHX(sUJH;@!Bf$*03~<{G8;SxIiJ_($Ry+v@DlVVAy<Nvz>D#_B4_Z@kqOAf;Kk@qKpNl#a2$SD<Tzf#kQ0${;5hV8L<t^+5<D0=3oLQ~crdsxvKzQBxI3~fxI6emUOA9K$hP1ha2{T-GWpbA7?}s02R(&Rf=ePRfL}!xMOFY81(!p<1uh4!j1pW2*%sUu$5RK{6kG@V4oYx+WOHzR@Vm%X;CI0)vKiR9|5xKxf>$A4Z=eJh;FTMh3t0%vkY$jCz=bfY45|eC?_-R(of;^?m6-TDvogygtAVTG_sSznfb;Ul*|NM|<CUM+tGsd{gTT4K;tld6CNl?q4gw4RoY!6CeXz(sz<0raGWi(3k;%tpkzasCUI$-C?=|Ef?7z<kA`kQW2KhZo@Nwida2E0c@*4OWW(q#d>k_YXyiOr~$V*`H7;7>47?2IViTn;M@)%g;4`7iO!51;_Ch`*aCip4x0{8;f`4o8{d>?!L6eYNHfJ|{tO5@xFfnP-i;anGmE9&>}Yx1hj>n)Vv$|%8A#cP1p0fDdQ_<#Mc?*98ne6PmH|M<@RoAhf-|KE(^vtE9Q*{*d?`#uuL{}E3VzlwV``yc0k@t^'

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
