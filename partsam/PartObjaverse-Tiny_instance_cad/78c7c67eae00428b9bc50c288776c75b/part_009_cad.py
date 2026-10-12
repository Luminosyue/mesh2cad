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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_009.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_009.stl', 'source_sha256': '1ee46f8abad3f81f747ca5537fa9c4565f243b60cb14d293de8ebced87c8095c', 'input_faces': 604, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06714359670877457, -0.17412453889846802, -0.14058896899223328], [0.15221130847930908, 0.09484505653381348, 0.011776052415370941]]}
GEOMETRY_BASE85 = 'c$}r133N?Yyv7eA=CM(8+?Wy)8ch&G<(Lvg1|i1a8e$F+LqpJuqH3tQF_c?s2$Gs&9&Svnp(twBUQ<yst)Zyr|Np-9<-YaaT5r9VuCL$kemyz&-2LBspMCaCqr!5zc^LTdGU`tE-Id~H7@~rPhcPlPad`h;al>j3P8gNLD5|;qWcl2PnDD4hIgF7;vUl&eVZ9Q)>s!1V_6hR#vv~Izk~loE$KdWm5_`u<9@1mbu(<d6uzo!f;@-dZ38)?5X9=k0XBlhxKmO!@e+l+z|Bb<NE#*6JR<A$8u}|_p0+6rzOx-r@cg>B7b&=Qpc8mI$NX@NbO^{b@l_72^6sNf(xh3)rZ8Wz{U#+=ieH8MQ)AT%!BSkVLcMk7@JoU{cJ>Ht4xmhL@?^h#8&tvo`uII5`?zJWRc?|ojeR}<8N8t6L1{v9}(>`S@@|mIO;`UNudVa&Q6Z!OJ+76Bx74dnu??IjxkLx<PM002AHRR34s#_jp;QaX?BM&O7$2)%hC(|V_`bs~SQKFsZj-?Z}%4>7stV8;Ko2<k2d?%-BZfqEecJnK#pUc*FhUSibQ*nI5YM<%v-?)I|8;(N0Z29M!CtpGCa|qXY>E>R2--fS{=bxkJclQ5G&+j<<2G>*k;(k4kyJxcgUT(K-`o3$gARiNxAg`@o`D$(svf+IP4T;n1jcT#Y<vf$mP0)O8Kh2GZ>bo?*GH|fI-gX4X2j9i<FOPN7^GE)qx$SyKoWFqQ7kXUdCpb^lQ|T`Kvwp7an*X>~+u!`s7ya|JJ95u!8OYb{(a)Q+F!IobxSkDt+v)jUS3uq<b(!WtdwRO$!IQL~*z(`k_H_DsBX1Fws>j>r_0!jT8Y16?abRYy(z@Fwg(Cmx@<u&A_DyeX-|}I|{pw&mUbu&Glo5gapx+EV-hMhVID7uQ3F_FWw|*}3_ZZC`g|DMMM^2lp*PCv|@vYDwoj(@V^P5G6AYXB8n;!4)-(7!ybt3Xw{^%DgZ|V7M3l|_a62jCIT7>Jkp0*SDujtp-0#0pLv)n1<FE`Fqw|qHJ$3^S&$Y0mQ=Z%;@U+a~23;E5zwxZwoYdblb-$g!d#P{l6Y13Wutv6BMyIXd-<Q{MJJod24n>8Qt82Pj)jDs=0np+D0iTu?*jI%uR(llT7g4fd%^Wo96bF>}K{e!$qOPs$!h+e02aLyf?Z|;k6|6#yl&E4IRZ|jb6J@(jgZJ%ZNke^+u{n|RZ+D4b$ZI$NE8{T@IX5B(Nve(64{@7}lJUtoLf2qw5mpr~a#*N!R&Fy_XkdMK9V6RbNx7Ob%h5SHsw13aXTQpB8i#*{2^oM(w(_He+57C};U+D1;YgOd^9xp+^P8;Qtdv(LO5BU`BJi7++Lt8NaR~`4YwsWT-<OSwoKIoD&L*KVz(;eBzqj9CiJeRyg6564dW2?49bSvcUUYO7FpLWfE+JOA8nc6<a=8njh&qu$i)M$-fPgpGSa=&377<he&ey-$R$Wu1z`&y2rXk8p1^hI9fB<_#(Ml5&95AWCawFKV7^{gL&{P9WjpO*fM^!VJ<koVf8=W)bGqCbB#6S>DoJ>Gi1)*hF9`z4%ba-hDi<-~lK^JKNBV}Tuc<t^Xgdfg`K^>kl{Jmwtkr=y$haLGBZX0@~7vlV$RUmYLj%4X=d9rqv)Scmzl>rn0Imb<5s*SF~L*6^x&J+|@ZkbheS{pw{&oo{WWFCoug8s{$%jPY{)Ci3}#xSj<QbRMv|72T<MixH^flZbT914|-bRAH_9$cU*f`8-q4Z<|~m^J1JQ@*4ZlZ-W+VzqM5eN4~N+@|mS|9ND%-A>a19=Jwm0wB4MM?KHP#v~anvW#z_(M7^&W_mgJnf4|cKdB(X7`g>JgXg_y2`)h92`0#)pXC_<peH$m?_;vqi-OaEo+HZ}4vyu1l!uYzLzR)EPdy016vm5it;uPc;ifql^e;mD5Ag|H_>!rhPdY`l%+=x8yER2hnx8`adn}K}lS9X2BFUGgk>#E{F?qlk8+Gdwop~uJkfV`IbT0Q>d*jR192S<_f{$&pAqT|BwJdHfCAll1_cGK4-Z=#)_&cyxQ>K>r&U*tL3ZGLgIThN-x=w}6Xsk?=4(%g>qfFnm4<atZ!eaBf3>tx5m^2m+e!FqhrpSx*ZsX6kby4y8(lnn~bo-doN_YwQg$-3?`LK2W~#`@Q`D*)@>Uxy)&Iy_DNaK1!6{`@55rEY5-oi8vh%zlfJAFQYC@9Z-P_xFhxkOvN0tbV8WILYl{H;~udjP|dWgmva8d3I}FeHZFGZol?t$BWv?x!$%XH`jJ`J`P3R;+GZZCkrR(`|gNF?p6Ww-uPOWS2y)Wo;nfZbo^4CA8gkLBKO;ad8yfXtY?~zM$YxBc|IKT!{xEa_l9FW$#)Rzse+S`H=cs?`@Pk9$uVfI=H}%A7<XF-qwe1<!trk^rJ_E=bX{T8UW)u6)@x>~R9xpz-y$FV0?#j{9$-F+TZw!W)}i*u`B=BSU4#6`?K+N}$KPOmGJiet8-vlG$G6w@qj`8Ua^COE!6k71=Q~~NQYGy>t>etS$ZajqpObdBcgfpzPSf^m?4#=zW8Wd<oZl>+r)Ybc9gZLm{TuDMaH5WP>!aiRyyI{^+tz6v9Tm<ZFV`3AF+P|5n@2nGd3$*2{9}o_jNJJS_qzdcI<Go6+(lmFPs|VIxe$GymJg6W4AFVd_~*9;`rn(pL++l4`Jvy*sNn25$CqvCZ@TU>F6G>#IoB0N#Z-MCYoa^y5lMQy<=SZ-N0u`l$Spr`K3P^ruQQ+$@)vk6v~`|}b=|S5$YUZg@AbZfb;zM0&21BdQJ1B7F3ZY|*4^=3`P)T2r_5-IJmneYtCYzdweFssaGs>^FfW-C1NHURSRDT*RX>-b?noUk_U{KHx5c;9<JZsVspl^`7Wv1OF+X?);kha2w>W?J3d~pjW5TpQR6dU5lcK&<?^$HHUQfF-$U}x<-Sx;D>&EiGBEMq8dgIJ<%uB0t@5Se;j(MZ?j-A@hwQ3;0zkHE;&S;yqXSHDDNn<b%<Qam`^|U4OK5Ov&(rO#7w^AF;9ZRNQTqi|X^*YB4#qr-IU|#zA>1544M(};RVSVVGqU~)RJRf<E892}BWfOz5=SwQ;^;oZM*ZIWez7YB0)HUiGj_dQ8qmCVUze*U_ZnIKd@`DbHue8%xkDXkB{CG92ufFbw^-|x}$g}n_Di_Ld$$u%0=Y_ScbUfPLtwnzQ8QQu1M4f+ZU#BBq`VHo*xb>J%KH9`~xUgQ^dD@dXF8Q)$Sm)32!TRCH4CGHwW4u2Mz`lXcLA3wSLFng>O>yd-j^TKp)>!|Py^-dUzuks;U|0jp+fPm)Z}|r6{1aU<-%dS^d__*Ie+Hb@=K{x$i^w0wxa<S`n+K+$eIAz9dB*(1iQI<$14~E{?jvRHAa5IveH*`bx}LYLdy9Pac<twwq~CPDbzFAar}@?4I6nTd_D^GY-hJ8ozv(?)&toZA5P9+8I!^6tW4_h*ZTJE5F@12JqOlH_{B#M7ub)robFt%aea+3Q-O<j;kH_oh+n9jk&&<;ETlcKg@%V3^uK?~Bf6v4I*yJn7D@J1;YZHWhAx|fA<9n^Ixw0STrQ3fX&*+Nt6zqa^^=A)}A1{mfxwZ}Kb9-(F+UK<%Z|(ID?iWWqk#oPo8nFxWM$O8|n-9f&xcatUr?s0e^5jHZ=e<fg-W~h>k>@Rm@!R*g&L@U<9pv1%bhb9NF3x)`H8*$d!niKiK3@Iva2!AW7M`2dHNx{(R3!4uqu9qt-mC9xyAzF^>uTqdT<D)$+9AK38=uQ_kv{+0ZS6I8e7ObhyJgHct$*u|IG*=?>nu~p<G*>w<Cs4=E*zygvwdEo9}XLx>XNtXg6H&FWptdHC3+z*X2ZO3>Mic$X?<9iJm~+O52v~0cd<Wb`|8;Sm;9Sl>_1o^>ix&od;oIpXF4_<+v}1)ZjW_B)C#P-QimYt{)Wvwr0rv_N<yA11?$+Xb<yC7n%f%3p`U-;b!hh7Fv?=Qyvngu^Tl(K4=kkp(DC{1eJ*(?>>rz-{`igdhj%H+AGOf;HJ9Jl@n{@hgq-(rOZjFiwJv_C=szQR;d+X@jnU&~r{nmSL8#ZMQQF_EnHk7G9JCqr#{JH*^%Qb*lwPN`;(E**n=i88x}#qu#$bOY`6hDScm8dk5ALvzn18IcgWCSqD^J-UuIc#A+BbGwc#XW|GxUeh5L{30f|=;gqp&|beU{FXmYgM!M-0~USf^~l{II|a`H&RsZ)~Zl<HFgq5_0aVSfi(D|1n-yMP4fd_mLR~)@%NQPo_&h|0HvROU`{EOP6HrZ|2<U$hjY4xtX5fk{5rC`aT<n<GcGI=lb08sF3zIn{Um`?BmYJdVYWL5%Mxuu}@on&~BH!e-*4_hrGppj(1(;Uvx%4PYlKW*z|_Txes95Q3mr#$41D<JV3vCY-0RcS|WEoK|kcaw55DB@|huc-g)YS=i-oo$kXp=|1n2)!hUS=c+JiHFEGz6@JiHvw>AOCXMKO+{wMZ@MkXTXbE3nTuKnC7G7@?3l85zm#FAlp{_{5E&+Fj+652-R6XWbu<aNtoU6Hj9uw)+cp?Prr2?5v#KJp#%XN@pFpTu}E_ishceE=h|hqk}D>qq3xV=?aj{(GdJf8rT@-mLrJ*-7!*uC0H?@!Xd)0$yOB>gF{ZpIH;1t5ixCt<Q!Vn%lOvL|!yukhXuZr#R2XIMjvvIrc)YkvBGQ{_l^t=7CkUUUuG(94r69`~DG%^ZT@KqxsUJ`}O#+f#|oL=5BY%jda}C?&Z^Q;i%(*oa;KHL?w)uTpuFmKCN>_UL9ZN;?l?`-p0OeubbE(>suB%pU3S3PIG-&5qSd-<b8T<cF8AQ#d9?GlO4S(Bj3sIm%L_S|9qY=a;`I-15)&QY_kH9?>&t6EY%qGebNLu_b2VSZf<qSxes7IIH2Rs7SjUxmi}m;dfjxsvOfqz&V73$C>Hy}o^6qH{xo+N#k}!HJIx)=_UJ!{AL+h|HKH?)FES3#M}u!_9c^V|_q+5%|HQ`H-;xI)=W~tOeFpk@=pf`=|J&m8=y-QtPQv@H?}+ov!*iKwj>GZ%9@b(XtK-pe_DkfP$848x=saM=&t$u`#q%uplg*#!BHzCk*MBuypK~1xm$KciV?4erfal9TcH~nd(61`2!FV~k5_#75K9POD*YnKTfSmJ^F?5dRhVK^ST>lsmfoQj9dy$97<9;zS3Ez)A`T;qg?~Lce(Le8>LjJ`We(!2x-SzodmwsqE9P9Lb$6rOB^E<4&Cal-v&0E)zXYFe_590Z#<sIbwekALAAEWp)<b2MuKbnVrIP#^-=W<kSvfd@HzYy0`wmhEKn*5EN>rzXDi+D~f{04dK!Hn$fX}k0mdAUAVXCA$;_Yr6Q+y^wz+8;|ej`dQ5g2=f)V|m+C+s(eL7;>(w9fcyb9qa=?Kwcph?Zfq<BUee}yze`v?!)uld_Uwxa^w2H%!6@V!yoyvbex~<W9wQM`L!hEoPTW9>LLGoGy37!X!PgIhRByJ#(HlO_mi{oU*@3hP2%vJHKP&o^yg@|HJP~2R&9d(_ug1vz3{;LZCeNArSD=quKE<8w`kIV?BmgS;enptNKHo0`P>n?^V@w<E`QaLdct?WsdDdEcJGzX@G$!H$o3~463S1O|M!2=(LeBi^(P&5`~&~Lf6`GrhhgM+uQHUd2mK!dEdGov5`IewU#6cUi~mTzOg=?lNj^nhOHU@RC6A+otI{iz#S4?gi;%053(?)l;<?G<ZsbDbe3Wn=dM>hfPI4Y{UP`zC-5|?P4zhSbasjd@JwI8zJX!oxvL|^oC2XgsknQB3==;gy7sx-6f2D*A<beN87MFfdfD-nigg>H}A(vr4_=pm&NC_9EOaCZJzf2YhKcIxq(od03u^*hJgwrWu8+{yk9BXf*gsamFk*kwS(DRY=v92X3;bN4q2R$!2FKg*R30I_hk}HzO(npg=vu0x{;Wd=-8TwD;GvvqgU&+6+Zjbp|xHKhPhwer8Vx8(x!oieq5WOO~BI^`H374gWU$T}`zn84zS@KKrFZ6WsFXWAM8+jvnG9?^KuTHMc+Qd@Aew1(pdNFb_)}{g_>_Z8+rB@_ZWIfta!s997H2NBH8u>i^4EYS}ah?)>MG1SdW>P0l)~gQLlWbDLE$PAJVAi80CESz}u0$_OF3Va~;%nhIl<+0`FXUfXk4uzr1||FzeKL76>+uyO+=~)6>3(EC*2AQPYf{1ibRV)0>k&W+ccX+S(8rU<vo;eb;qNKoi}ds4i{#hzSL9c$)oZ>Mu0jci&`q+*dW2BIZ7Jav^rqydtVat<*pCu^$C^o<-mzYn$nVHk=^5m!<URDS$a~0NQ^LLJy~w>-kKUAU7$qD`uSu@SdIVF#jVR#`^ls#CtVah*_;X5l6a9PgCh`^fMe;?~;|e9LH(A!opDuOsXT3tm{^T%9xC6Z{xh?C_ffA0Ogg>VHk^NY!kNH|SXAVgC8tZkHe3kXMMhPFGgcs4jCV$O(ETV*aP{L94Fmf2{5k(2NqJ&%08<88a9xW;1j+F3J`sd`&S(~Yp@HR@=NxwpNlJn$%OP%ttUjF1f<UmTe4Lyt;#(K1&gkve;D0&1rg7t`^gaaty!t|VEaj8dPz7~GS8XX}&Bp;<OA|EBsr-ZxEdyspu9$hHmP)fKdy%o6?>(P`FZcGWs&^wYlvK}#%@DxgTH+>s<H~9wLNp`YUH~3mOA0_Nd4<rY&9=?=tI3?Vk9!rj8J=#;kttjCd^Z;@I>rsOeE<_1GV$GyBk65Fl<VWPgl<;)=eDZwOV>%_=i4tx|4<(1P9t|nsKuWkay)n5l>rtB$j;4es(Wj87ur`w@;a!yQb@~nRb#h+TOzM=E_3|a>C0D0}o72O|;jBk<N;sMlZbolKZpC^uqlBwb!tV4!<U*{KJ6{XmXN?Y%?~@PFr;`tnXHvpl>7B@(SdXrha05!X7Cn$0$a>VGgo7yI&h%(<H0#ls68?e`-b>#_-b?<Sew}=swfdc}g>zHF-t_9^>a2%1CESD(j-*GEqgjtgO1Lp4T$NspT#fapN(twpgzvFtQk#3M(IN6Z@<B>?Hhm^}ChIYq67ER}H>WosH())QQ^Iv9;U@GTauDm$gc9yf3D2N^LH>fZnL!Efql9nKe<$A}=V#5NPWf3cZ*qQeO-i^my$QJq>(QDL?nnuT(i@W-vmT+8un#5dM$bjg#ag-XweTOT(LwSb<V^Z(awd5pB|MPcliZW_7)S|6P{N<k>yYcP9-mOcttsLD^zP*DtVe%JcorqRgT9ZvgM6EQi+qc<y3N<ZMJVBV^qS<FtVcacIEE7LM(;@O$a-|6gxgWVwdg)%AJ(H5C0vjazQdYHZSJr}ndCd<os{qb`a<$T)?)!BJctsGq(_h=SdU0bxIQJ^j^3Kwn)PT$2`5m(bLg|kvsfG9rSG-uy-w2SkWZ42(|3@Mlb_RXlb@4Iu&z?e60B)GatU$+O1Kj}h8)A1b)tm3Q^H;7?a1v|vo4fyLrS<9y&$<D>sgGih3~SCJIQy+C+G{vC&<ew;Y9i%@*vhMkrHl03D=|7C)a1q>QTbslyE#fft<j4#M76Nm$8=dl<)vbxG#MPS$rP3FS!pTY^6^li%%q5$?YlOX7ta<;$z6o$RAO{HRwrX@nPf|WN%8?i#~)bK9uZ5u0#n}p^qesk0Mtg`%=Od`f##%KeBjPav6F_dRek~DYAG`vUqWFN%Du3aB2DnWbtz3(&TEC@CbSwS^P`#2=aH7@M-#1@@eu5`c1O<2RXnm$mJ>Fy7UTU@yg`7<oc9wZMual{vo+Gxf~_@#DM>1fW<eHpO6pG=aLVQSJC^C`>}qj=%dK1$m=NK)%20%k?c3CDdBG@;l=bJWbt9-#pG`(;Z%AOS$qsRmAsx3-a!A1EIyIEfxLwh-cFxJ7N1AnPIgejKhT$u#g~$QARnWjBp)L`rG)>YA18}HCyUEm{}*2im!yP0p*J8m;9UO+CES@3w$i(kyK}C$Qo>y+;YRd^<c6H<8&SfgDB(X1xXk;);wQ*|l7FUzSJ0P}#S_UZ$b%{27W6h`@p|MIWPeIHgdR>7k0*-{AdB}Uhmh-1!XMN7kj1U!sIVM4J#zg||BL&7{@8NJzq9`j@Bj5TUB5=n{+s9CpX=W*Rinak%lCUm&iDVw0J<i-TE>3>Q%ee}'

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
