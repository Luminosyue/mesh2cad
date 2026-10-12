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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_006.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_006.stl', 'source_sha256': '682dbcf33a05dc079143582f6e35f3d2f4ca4b58b2775140141352db17cccaba', 'input_faces': 682, 'input_vertices': 414, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2845205068588257, -0.27325528860092163, -0.37717071175575256], [0.28262361884117126, 0.4999845027923584, 0.3771708309650421]]}
GEOMETRY_BASE85 = 'c$}r22b2`WzK44Okqi<Ighs-OWF#Z(fJk0gf<$3wB?o1Rk{N<T0ZEdCJE9m+Kmic}cZamA0!tP};g0B4F`{C+&#SMi{$Cd}CGVVf-rIBP{J#09sjjZB?&+i{9dqX?>BwJ2r`g-x$D|}Wjw*$mlFr1zW5*94ICxyG$I>S!IK{MAe}1m){7`aAp9E*3Gc|G0;Bf=TCN^~w?;p}Qv4)#CWc1kaW78f>9X)o?VCCDSjT$%D^W%o4r4RN#-&4PC{Tl9l)oQrY-T&iX0j~?8)eX*Mdg*Swa7tz1=>`WgV|-x8g%hzpaCzowl@9eI*Q%|L_0jE8Klp?A$VX>#bp5}YzL})_l>9kKu|9um?W1RYJR4WPu=wD)AJ3``eS7h^_A}cYP@luoi=NAj^>f6#GmD<n^*_oHKcJTO(RJnZa-$iwwGTHuulpa$ESweV16R(Ri1oojf%o+1%_9%$cAGZV%QgOa@!@8T^>QO4s%h^meOUWoYO-E#VCnK~?ax$wUbi!6;E6bYwXycj-bH#GjQ?JI@U2C99Grv2v=7n$K)ZxfvEHHoE<VsEHB0-$i)1}V&ei=l{-}8O(YZ2i8(N9)`qd8oIl4vn$M|02qn~U!8&`kPKxyZ<U3z^(3mb}evvmF7rU`m|!x;;X$aYz^N7t|Psovhk2l0uY%D5%Z6TfqV_QAJX$@utwkN7}lE8U+!sD}75$$I`c8*`+-@9z>H+LWW~M}lR<|4>)^$S0enpNn5Rto@7E_v+=oo1)t>{uS|oV=20w@UqViY5#G}{ks0kWlm<s`pe=Yua-F(SHE~u@ncfY#?>z^J~S>>w;xP<R=hJs_KSH9b$#RWhz~4isO!7^d+PnwnL8p=Z?6H<b$#O(hz|#+%ebv;DgM_{+PibQ>;4=6yZGq5?z;b>2?rwDr}Wn25Kb?x>l@!qygR;heEmpY8Mj^4&c@Y0BHnqUn#`*Y_h=t-Ga|bEqa|g3_x;`CBUvS7-ezx=cFt_k%X23*Jf9is&xv;?HaxG_qt<$9r{Io=%-dV#_)vDK_-8+m<5bov{k_2P{TaHQq2K83;&ckgyz>1>@zLaf?tirJTjGa_4|V9K$H({);@!^Obo;@pd$bR2d{K@wIdU8@{vYDqQ*s<|dsdcq&hOGbFk`%K-}v{%hh~kJ{{KF2zxL&->g^aD+D7{C`-=GCZDc-|o-MvSe#2;)&%SrXhc}JZ?MFiE-qQV?`|Ba?+x3*=x$ozR4|M1${r}hez1o-hO8e-?O{D+6FD>4UHj({h?iX+B<v#Xuw(d{UrFuRXpDsS!Y^ltLW;x=|^w--rIIWz_H{YKV@60GC^DWOI?L*WL)vqq|+4pC~M;ld_?Nxibw9{w3UanIhqUTGn&Xrx-zwwC7&%N99@2K&6#0U3nJEOn1;Ows0<p!=iBENsWXSvSjkI3=x)9unu`$C8H=YkRWo%VeP@zFvN-F`Hy?M_+m?J~}nC+YT$zh8Xt$|RZpJ>Py^Z@1ZHFX-`iL+@wC`Z?kwp4ZE-@{IPOKfcoYl{<f_{@sbLdG0mcpWk1}(DhR8(ET+2zr?%U?$G@VeZNY4%0}%&n_9{5u<yHxcQ&`u$LG+g?%T8vy|_>JXXSK#{$c!V@uAhzPwVx2Fd)AD2JORv+w||f@g2nnTi<qE=lj!M)&AlNy&pMWSC;MQ`;WwjzNxJHA6UHL742J(+O5C8^*i}}_I+FNfmgqi@i{s}{Ix;iNBybK8;t)EpZ@22y1zSmiEp-JtNwhbwXSb`5<aVSeEo8}wGS*?aw@KVCGpPkC35~y?a<5G&-z8?ZDN`pf8%G14^>ao;~#lt-%ENv6ly8w8O1y3<E`<9#k(as=y~C^pQL@@U}Nor^)AVNJ#5$WvR~JDTetJUlX^QEpN_xyq~4C<{+Bn)epEr9*M<JoK+flUzgK+VY6HC;op-~}>Ur_#)Hig08vUxr!T5B1lV7F3b4qIOoSHINuV<H1y1wysrfMJUTFR<lbExj$?$z(a)h|{{{NB~?=>FbbLVUhYU(xN~KUK~{eP2X;xW!Z%*Ahj=xBY9EUZ2Z}dVGxUfR84gj;sIPDm{OksxQA6SO2*9aJ859JPB?6cUb$J75~uNrPH=|Gh_Yx;=?K1-i@pO*<0F28nrwXSO1#$a1*wFkKe^#{(Xy{7wxv`^Hk$6;yZ22j;p`ys`yhiPsY_>j6YXXe%Eq+Bfi@#J#N8Q%gOrsz9;^*a(aE8DwoAK8?V>LajNUz1>>8G4<}TY^X<Nuv=6=gtsb{XMzLd=u|89L_)xK9y8mx{AnjBiqL=4pY}ChF<7<cy9Negnx8d_Aq@C}d+pY7?yn1|$|5kjoeBSK1`ZG6)Z!tC}uKslK;RnX*_T78tYah9*hCW_Lu4L%_)cCUEqn~D+kE_4Dv>gA}UpyUKKd?f4V8cb3Z+mCSdR6SA&zpj0r|I*4<6ZI53)8Y<>j#b|YabbP{6uX1z!CAGF~{XNU$%hu!I2;7{VF=Ily2Yn5#l3@OJ&8@j}*Nq{*C4*V(W*B;P*Ax?FXOxZj=6;TYf*Brw_>Qg5@I{4;|J1of9i{y@r=x(EaID`Q**KQ*ldnoUbR|t+GYVUo7u*tt{uK9X4wp%H9ySeT_f5A#VEyN32<Sv-xAZHGkZB3!c*L^?OerFN4Rr$o^&d$l~MKalRLR+41;x@S&4kr2qGH6F+a!9=+V6y`=w^5A?g173b%Q52s$sO1haZ*-OsH2REFr{rKW~d%8Ox)%~}9WZxIraXuZN@kMshO?-IIqjDa*^T-o=ed=D-=Xc?Jt#$ux?-q(?#rfLe1I40QNjLFs;ns3pob$;Tz1(-sJ)_(2KU2;#eV--XDezl%oX-&N7WpkZuAKwoBWW{b{4aVJaO&Tuyr|EkBXgU|_**{k*@dh)KS_M}%L`daH}R2$O?CgBZo50_++0&1FG3gA$?qvXgm*qzcPh4iD7}%?A6Vo4xcXznJA>pn<oihKflDgGyXKsZtse-AcX!V@9oL_Xzy7J~KUL|2*!oVUcz1cF4^&2vEtrsWlku^=KR(7=<70b&e1hA)o0N2u?Q6WXeT}!aukqIQ4c^^xVbV?Jr|tduX}mQ*ZST)d=lp?1I<5W7_Wu55ytRMX-rv8XS34}#+n4)SPOcBP$NCWWuObQJonWaII_=|$<<0TL_xAC`_8d=~jE>^1<DT)>aWB&6u=uqFpVQ-8B3X_<zF#FiTqare$IX3L>-DmZ&&FHF=g6$V;;rMq@%HiGS+4!xevd3~evf=_{~lT1|2>L)+dHh&`hB#$|NH3s06x0;(9xuu_|S#}`use!_iOF{_WSO8`}ZCHx8HZX{rm3r82GGSFYEloc<cPc_xAaT@z(i?b7YwI_W70Z*7=q3*7=q1?enYPm>tjFZ2lN;%^%~f^F!mU^FycWJ{br5eAxH)`LOS;^IPMs^V`6hgR)%f{MmTx{MqS$Oxm%|=Z&||=R@bkTh|xHTh|xiTP}*Xu6K;Lu6K;Lu6K;Lu6LYkc<cJbc>DTg$2IZx^_}nS>pS1u*LS|RuJ4=*zlgW4XN|Y6XK&Pxzn(STx}J4={wm(Oo;BXOo{dxrZPwe}x*j*)x*m`0efv4xj&;3nymh@FJiKCy_SXFb<E{G%p#}Y4(#zrZDA+$UGuHdhgIs*{O0So7{fOMh2-mqJ_jU1qyT8#nEcLDXB*t6!Ng{KemHRT*eHi1d`!IoTo4qRgZ~T2B<E{Hb##{G=jJNI!h1~(-t@~8QTlcAgpAQvp-3K$?z7JL+ZJX?;@%Pz`x9+nA!xiMbz`l>?d+R=)Tm3%q)_p?bt^0)T#yqcUZ{3G9-ntJNe6WOg>prLP_I=JD3+~jO`=z0IOXdCv{%`kDE7jEgZ}($;Z{Lp{|E9EK-S0Kty5H;Oswl@1>wdEF*8SvAg9o&??^hdd-LH1L^pJL}`{Bl0_roJjMR^X?TkfleZjH$KkMFJf?e5OHdt>|K-?um3x^Ex-vbnTlJr^+EdM*&|+Dp9s+`;$ubB7hb%5tse8pd1CHQZYHW&T;uO^mmnn;iK;o<CX7WsJ9;%ec4yF5Y_XW4!g;CzN}Y%x~+tlJVAarO4CrefznU@z!&z@Z{>++t1OAx1N_7Z#^$F-g@p9%$+6kAk6c-Bdg?m*!R|Ry<n*`;tR-g!0^wv%K4J-t>=Tz_A4?!tmllzThAGt$am6?^&Hc9>p5n0?$6SW^<33>>$$4&)^k<kt>>yv`eZrITF-fnx1RF`M=cX?Jx4a)dXDTi{!q_X`#H7o)^qCMkh1#tVm}8r-g*um-BeDz^_<;!>p6RL{Z;YSbA02i=lFrPU5;q~y}S<)y}ViOPx{_^Pr$u8SiJSVf$`S+2GL3x;;r`?jJMxsSRD~>y)R+B^}d9g{+L|vmX-G|!W$;Y@0ahb_c5H=Q^Z^Edl+xM?_vBxdEX=a^RAq@`u2MuHP(o?-aj$kdjBLc{#`k~=kT6PXrP?`_}+Sd#(3-f8RM<@XWXu7a$dYd-p`3XoGka}eQ&+D<NWlvJSVZ<|1sWr|Ho;aPsa6OdGE+wQ(nf$_xAfp50w;ez1L*C^<I;kkz1~-c>gN;^Ax$B^*!%v`98e)3z--G`&w%!?~n6-eSGjx0XcsCN8Z;8J)S=&&Rg$s8E?JEWxV|!SDqr`8_D^0_@$5Z^IhLZINy%qgR@G@b8P?o{P^evNija`pPwJ|d`jHgc=@KJ{yE8Y998l=C7mH@F|Xn&ss8-D`Kx%t>;JD_#cSBO-v9SiyezK|hrH4>LGtbdVO10l@X9=|JnfYk<WhJBJds=kPlSWyY&ZzFAqT(%SeD`iUI}?+Ek*HD<Rthh_(^gQ{3JY=>;%t+A0aElkHGhPrI@$ww|J#Ac`IBRE>9MM%fofal5kzPEqNc@7JihX_z2k(R{0LBQuXTySsA|9%X_?1h%5l#PUa;Gz#;EDL%lMa91e%b1>_WXnD?E>yfTEMcp5ncp2Fwx6vgQY(l^zQTI8K@Ex0~e9<C2JChNeB;nrjTZVh)JQ{WD853)C`aunPH?n|b_ec@r`V{l%^@E+FXUdD9_>pYF3cr2L?kA+8&qu>#6PqH`Mn|}ACDDF%j^055d;XBE)u*$0Nop5<dRmM+c3%CVs*P(P~EIYH@0P9?X<>!U-koDj^a9Oe;To$fMwt}m|Ehw#6rpk73XSgTXEoMx*F@7rh#f)b^##`l(nDHON_8G#z4Wsm9oA;wFe-0@2=ZWGDWV?hLb4+n-vQ@&3IjOiY*)ZY899CSPte0?O&MU6PIN!^--ixb2)`M$%`(#b8B$9W+D$BxZpB~6QJOv(4_J_yA>0}=`9Zn-V!)b6gvOU}let=AZAAp-t6jvh~!PVd@WNo-M>rsWGxFRKy^<2R5E5tg^X1y2i`AKp-{3JY<qIe{k4yUu8BPoh|P!vB%c7w|@?iI;OG5xGW-&IzRS(oapx60-*<Ip^2teP`^%~{R^WH)#y>p7Tw5*`evl4IdixF0zZ?gyukJ>VWJFNLDGBiS782)87w!!6+^WF@!>T$8*L9!kH5Qxp#*Q{jPdf4)<j_Ea{CX}=N6SD6H>Y#-CN_Vit4=a_Zr%(|-V6SMAp7^glgzaN<jf8&*FUilXOk<X5|um0PMTnWOzIr4dtSDyCDDtIZMukqdMd{=$17+D-H2A3pD!zJM&WInhE{HG)Nha;?t;$O(?@OAp2c%N7Hdu1oN3*HHDC0~KJ!kfwG;LY$0w3$PD`{9%1`|wHl0(k|#07uC$;V68S{2aate@1=`e+FM7&%l@9v*dg5S@;;40Uv`iDT?1D_rPz$JIL+u4)`VV1^5NV>LupJH0H-rcm_EUo&itt$}?VB>y=Fu#p}tZ;PvndaxT0Ao<~lCC(-^q+7El>S$Gqlql|Sv=9=O^aG$|{z}Lx3@Fm9gI(ZB}#+Y7bdEc^3mDk{F{QEPM>#XZ_zPpxu6MmC%UrW9OuZ5o?pM#%*=aR3$bKyzkE?DJ$_-VG;zbT4yu`eqwPR@X5@V(;f*NRJ%`(c$QVU-u)3v2_$QMQ9(wLflV+s%VlkT1Y0x5vzZ?aUFCdtj9ru*&z~Z`l4nlAGWk;a|x0@Or-c3wZ`s`7!(p{3rQ2tny3e#<5GWI<~32;@mjaDK1IA539_9Rqlh;@mL*a)p2+gtoFG@@HDa*tcv1^WJy@1YI7oO?}Sxug}1T|6z6i}Z&iZiiUi@}9;^Qj&P|ZK2&-J5AguD4gd24VQcvYau=@9n)KOUxR?E%JvUAI-=|8pH5-hs}Z7E)vAaz!gxnb4j2HI7rmRpf52p6O+f7umTKb0j|=6b&W47m}$$hxej%?+%#8l%;$hsxYBW0}A>CeZH{l$CsMCEr!N&MOPOvWA=w7xlh-hgWW+C@w>~a2dD)*#NEp*CUhRdT={(G~5n;%qvI9!{lf<5B<ms7v=L&{=G_qWTgaQRTL+aZQ*2iFqsAqh9{Gc!;|4zjEx$jndB^Z7IhTA>-8bqE4|3xa4)z%*$}P|mm+V6OTmT7B5+|iADJJ{2j?a8z^XsZ6QnQMaI*x-fp9Z8m3#tDh3Ak<;5qPOayh&hUPi8i*D<G-F@`hwyarxIJ`OK~7n5l*?WeK)G`64LpSJY3DC>R)nIFCbcF7{J3pXHdha14jWJ5R^9!>U!N5hB7Y*=M8=H_9z5@VhUr_z7Lx3OR4rIcaYmSMm0w{->PLIw6Ke{R%c?$l$y^5;@J=2|=UtNJnfn?Dba#>~~D%$;{(HD8XhpEajcVZJP68_yz_!?WPY<dT?uY6<(?66Th_4?e*@`UGt!lU3k?Ua97l!en*0AbBf!2Ry>-^DwW>A!or;$%W)Bc)0hSp<WqHPKQ-ah1D`^vy407yT}IcU2p}m30wiLOFjtKg<Fyx;g)b$@*%h@+=rt0QL;b$C_IK74i9HN#!wVbpp0fcZ)JQ7vW|sW?_2qN3walO3tWz(IFYOXS71F8DT<RQio1|4;i-)K1ae$VKgZE`l_O);WhCpZvRBMF^okj)UW{KameZAN30Gr1Ym&FXHR1cna`1g{BQg<g1V2C~!AUId0gB@GWG}cq+?^Z=cZVM)$H5Q7L&@oIHTqqhqPRABA6y%5z;}kzp343)?e}N-Dj$MXc8uv;NBXYv!I*V<kabnrBxc>4FiuTaek1ZexQ@3^-s6>86vcOu<=}FBzMG=Bsw4Zp+Rq1(6W~Gc0CEgG0PagZ0{4Zxklo=fa0jwA+yM@d_roghg#&P7vMSsdu0!4fFXR|CjCC2oajP8bd>2J=WwI(<8LmOz3)g^KkoUv))9)4(#ck-r5|%#|o<NR+RgQuuz+)(*7(bN{!4J{)Ba}9bWgC{;opm0<@)yEO$RNA~9!EY5kAp{%UExviLzJ#8Q)MT(4cvlk6*DHS7(bOwW5%;7<E^q*%=p)0`_$s!>QI`p&70DeKL->CD2h9fotztUOmP>ot8-&cD(*`@?A(~ciU*KE=f<2@Jcw}~!MKjV4IzW@_g?wID?h>C@j1cUSO3e)-{IVRUhI`MURegO=Ci7E8})L-CCE~63AhYd6fOhjC;xJU^TYpfB!7kf1OH6^1ph?e6~FD3H@tFyqIfsC4c-mEN^XH)g`cM#_5IW2Dfl$}A^8FPA^a)%3H&MiHTf0%HT(tnFZc`ipX6oupYVC|9DE)=K^})szz4|)ta2}W5Ppk%4SoxLoqQR79e$B~9)6y2dy%=J=E!t%COjQ}oSY0l4$t?>Mz8$CE9=M&@H%)oxe{IuKS9oi=hLR*l#U6xO6LBb{ue?w{?v1KC+>eJWPdaMb%)q*F7?_nFF&MoyhWYwdl&J!^ue;FI#YN48{k3Rt^'

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
