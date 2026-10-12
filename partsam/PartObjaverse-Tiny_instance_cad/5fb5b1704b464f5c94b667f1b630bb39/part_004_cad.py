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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fb5b1704b464f5c94b667f1b630bb39/part_004.stl', 'relative_path': '5fb5b1704b464f5c94b667f1b630bb39/part_004.stl', 'source_sha256': 'e0dca833f33028ac377958d2ecbbbc5614daffaf720fb4484eaba8cf54b42873', 'input_faces': 541, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19440847635269165, -0.46236497163772583, -0.22320252656936646], [0.2613515853881836, 0.4999998211860657, 0.22298841178417206]]}
GEOMETRY_BASE85 = 'c$}r130O|~+s98MOJpq*!W=@3loTPxQ7DD7FIf&L*&7+g{$OO^$DqWMeQPY)5;}=w8T@UL@Qemw7&OM1vApMZ-`_{i<L$k!_j=#1>%P99^Y!cgZTI<|^E?O*E@tZ}@lP!&ew_D(HMJy3guUb_O^6sbet399jQg1ANj6di^2Lu?S9a;yIkc~hG(no;Iy53Ce4J}b*|k+<b5}RnHFE5@@#6-M88mj>&<Npo7(6N_Lib~$21iHe*Y&-cdb!D74cz2u^8fLtv_1rbdOs^oSJnOfEuqrr&S!<1+Fv2xm{5=XX*;>y=JTZTkyW{LJ@q1APd&zZ%>O27t@3njc%4kD<z2W<dD3UnwbWt{sd94E9qMni6ZNa+Z{**z?UzH^XWtp}izRZNg+EezLqazz-xPd=#$%{!L%z}@p2r(Gg~qQftHJFx?%$X;B%8)LEQ)-s<`m9TAk#Pv+Zu3x+F17IC)0S;o24_!zdf4g5wecvYs#BTzO-;K&ugAW`PJ(8PgB0f{n!s*P2)G(sQc*8(}Q_D@&C~Hjb76-EPcu42Kgq<oAPKEgLr+m*PuLF&y;jh+W__x=hOJrN2^ZI{2I06b=c!X<21&Eo+3ZckLTyNk=koRY!8sXwiWm5cZqzZerKAOA-x6f@893@e%Z$#vGkSfCERbo#KTtYAB-bkp7z^O@^gK-eZp$4pYF2{So-Q83a`W85i~F9Ni&|;L52EN?%ztY^rhy1)4oWJhta&G;!U~VkjK=o@njbHhDzS-zi^=ZQfMt&XG5bVoZoXX`O4@oX<m}AC$G<lqg=O(rthWkO?Tt=(`WNOj(T>$(pSQt-k|H`rnFz`+OK(>vv%=(_rIk)+E%VFrP)x<A6$a>G2NBd;nxVR=ifTgeAOp)cs%j|>Q}DX_86(}S6n}{rgQ#gds3-gU`@`Sznj)a&X|!*et31<ubJeV0?!_&-(OpW`^~sW_lsfv3L3wBvNGpMyUO?D#y5K?Pw|g*-<U>u@&1-OdeYK2_&RZWyWhE<9X^mRE6=G8l_&qwzNqf+aR1Gr_S%fRLzcc;V(AUu&qGv)YR7-L{ZxOtzl>3PD8D@8FV4TT0<~8>7E*p~TLF(}!BWa^yt+)|`g%sb(bS6OYb?`0!^$@f=W!OK(!Au}kJyjy$n$zznd(`+e3!?wrVo#QpC7e1x!>e|?~dm2zbcl&^Si?BPrjml)os~7)AiGH<V(9BQorhpp#9{RILqgmdkL=dWjVC(##(21Jbgnbk12f)jYsy#<bC;d)phEBN*^A7&?#QeB`f(nEV+W#**Gqp$2t5U^=p`L;~=$<Kf&X9Hk;Qc`Y_d}Vf%6Jw@oGT<>jlAD6hu>UjJVP)4mvPl&5j3LHjw6bH+8^_jQy<jo8cUkT-$PrPK3M=z4Jy&-dF*S~tx%hVP5FTe$sw9;edB$=a{yL-RG-<<L4SCD}JDKFjO8^ChjP+&YoR)6$vG=cHA1e;FgzbNlv*Tvv(Hk68Lr_toT^a-3;BjfQpH{`g~lj--s?x{8nEb-4C{#;JAN&*$)twVbD1De|Sg^XdGT8ZYC0N%Z1<FBwYrqoMUuUI&je{QMnJO5^>T&+U(S@;b~{c3b(Ya(MhdzT<OsW+abu>1$q}E18r>Iz5=ztzp4c@*Drg`CY=e{VyRrufDlEsa@lKTvwHT;qz@;44v~@WG~J$wm~*)7M*X(=@9lWe&G85%9+MveAbEmzAtDzl4oD4L;2re?zemh)rodKmDladAYO;wE4Uu=bE(da-vqFKqZa4MtH|p=-k<Ap))n^4=g~PPB`BP~vCQK+T#wE}>Bu)cuUf;&m$DOgkk;{Ge@_C9$K<@2&Q;a38SihZ8|Bx6x+Pos>cj7-y&)!;?rW({Q}(~NrS?jd^9L<`W7Axo?*o6TH?@;Dx1TVJ^9M}cPS?YlaQ#H3kS`D0$oI=q4_;4?&b%)z0#8`_hP4xDf3;T8R9ET|H(s|T9jLwGu021GObs~Crgk(Q*(sCm7sbw%$62L6^=rxx-NWl!lk+rK&+YpKY$L^cmZ4#B_JcC`Jg?)x{@!Sw@Avi@mcH^hoyQsH&gWRlUzxmK6M5aPKBDtPD*ck*M^49IAwR1F`KEXG*iSx2d6aT?TPa`X9DXmm^b_ZA`VZYN+WKq!9%tP3AIrKmmi~qN-SPYi-*?YxU*swmIDfC<e80GU<omZv7U#d#joKUMZQ?o)JHz>BG^X}yUM%nXhLh~qzQg&qz1U28RO5aV7G2@{pfl&ceuDijj^vxZen9t~+6B+UarG&`VY#nn=}XPV)4WUpC3rkuTiO3;&-X>88gyS6ug7tImlV!FEn^pruik9-tJkGG#zvmhuQXsZ`LgjQ`RdeCd|!NQ&FkZKiRZgo=5x}&7|-{}SY97VqVv`y{l@)w>reHduJfhmwbDHHv}M2gxTwzMoXPzD+q(+omuiL6`7gUQVn6R3wU^$;Qk|O?II>^y5Z6QAKz>i?n8fdcb)tB_JGaof$tC-cZ|dqrdE}7RTvtJDxxHf<%3~_`6U|G#dY<x0E6?ya&)lYYDeuRSZ?fyd^_iT{<4mo}?I-*3x|MrI_o-qN!}$j6<vOg@hM#Npp|jeEes6uC=f2Xa-+4=4OUdQu#r*{r+F1J6a*Fh&q`myS*xcoUWgcT_V}2fe=*I0M>=J}3-+sI;RDF4BD_sw-K)xIsNWQeW;dW{t8%(|-btU=6#UI&U5=OppPE;=aerm7H<R{J~Upl{^+G`byQ-1A!vGtVy?ImijzRpUd-+y37zQL&z`NosOwvqnsM83N39_5iortYAAo>wDZ`?(tTJNCpT(to`<|JEq(cYlX1<h#rv-#F7i?G5|=s9&jVI`_Nq0FP&89*tjVcZT!Vc|^XJ70Bz={Q>(^eeO`cj=|jDWUmcEP1{4rm#aTrP5F!l^5t{Uyl#&U?xKFPpOG(}sLJj4wAx62e*3QtyuK;qD`7)d&~>zpk;eJjmB+Ka*-pw|P=b8rVSUPPh&n{R^k+$KuWX<^h97g+P`l~X$(Np9q4tWR(z=-(gUFXZ9wpy&Ox;cWt_~qzt-6f&W%wc57iD`i_uJ$P%CBatG+%8;47WcW#p5q?YB~Mh{yE&<l)&q}=FvLp$9n<!#xX5<UNxO*Urg<Gl5hHB8jnArfYw=R&%Rc%_Fc;JqRD*9o4K3kHUBd2OK)i&Y4#<~Ur?Od8;`oIq<r`8@pwuu<T{D{oz`C&@__ptQ9$F79POxn)GFO*T(X}H*W1gpv_5j}2=?uLD8H0=c_RJ!u8HjLGx7M3yRW6ZEmxDTIt=AJNo{Dqw2bZK8>)5ZdPr(c<B>wsx&6W6Jl|0b7f`z%=lH(yk0sw=SU!o`M?PcUp)Rj~lS(TreW~s|9#32>t&cYPJ^9MYq1<mo^3U|=Q>#(`YQ$sq9S(j^<Dcrxe#|MZhpG>0-%Ybz+1K84UHJ{+yfF>Q*XFg%rgnj`UY5SRu*p3ue{N&m2M5ltUSCZ0W+>UjI?s#h9WDJ&dEhHf-&nQRS~RGWX5pLLn|--b2l5U6yf50Tb$q|CVBh4J#dUr(jQ2e?)OtMW?Ymq0pT+}UiR;Dr{|uo0Qp&!k^U!cUjOTkPk3Y}i{5LtOy#EgyQy%HLV@OfHv0R-2Z7h7vWgPpxOkrt7`0|@$L#^7|F5`8W^e{ZF2w!cVJi@ZQ^6?|LclYuoO&?~p4$}6;N}7dlUI(+UZW+bvx!jNI_H+xnA0_wc?0=ZT^_G8#&PmmM2IragGx;W;zI$kX@J*!;a6QjX!}EZB?d7k04jk@I&kJqOOkTHaH(vjhWp-NnvVR2obD#5bq~UC<c^Olm_qO!S^D_HJpXEHB{L7R_4soAC?K6$mb(m8tAkD)6REO}589R8KF8+M}EG?eI`;%ssNAbY=f99L^MfbJz&G|oX|EWIF-gFUpW>n|rquRQvm49eN(f<1*Mf=_*?-c2e>{+zGe^ZgZ@$t)|eOb9%q~Ci<(f<0}qW$Y%-?Q?&Xgr?j&U}8lx99V)|84evn8$hM{?5;vfp>YouJL(m_;82bALI`Airjaz|KIj~#2c<3*+_Y$_|tTrn|;HgDtteViJn1!KJst&<CFRMW%rWD^Xoh7dO&@e{ZIRDuG?27sosrQ<+*O{C8{^WcV)@fe%j5?ovUy8xf4`nlVyIxHomXTzB#|ySKoX^zWKZ|JmYihbKit>%<O-Dj(zT%&#_PbXXn`GzWE$8`{r}Zi2K4cqc*<>DH6~3cz=E$wyDeQw<YoWgH1|2_21RQY8~X0IRD|B*TL*d3!8JEmF>7rUbo`+mNG5azx|r>o1Eq>ro3fZvR~7g>n)=ty+5dne7WD3Mm`^W!}vWgSFsw8=EKi5v;V2y;43fuc>Nbv=I@a%1k>jQX+;OFhe=ncU+w1LRn-4c_7&SNt=en0U99WjB|m@7{-=6?FRkri)m{nW=f2thbY8*N>P2(E-VbTM^4LZ6KBMlM#N&65qxIA#-=fbW#)gyG4_L&{Yj<CqM~gU5#C(2Ft6f0P9n~q0{fdogUP_2BeLgazC9)sajn9F)x9I&xZo7qi!}wT!f9uwp-mA4U`*~iY_;Z1#4Ws9m9GJ}Ws^r3T)h>$HH}C-a{x19;W&a<3-#B-e#~(SL-$Q%{C0Y8ii!JAWmBsHx!;Y|Du?3A^@@qxoH+df8agO!n??1g;ldoJk!}GGg!SyraA>}va+~oS-6v=hiwND(4_s$*8v+fPo?WNxI`9vFZpZnb$!S88fN6~w)9R8TcpVyA_r1s#?6~F&WzS`j_pKni&({o(<L!$Fi$|%PBwc!Hg(O%f{=g1CEc^xL-raCu{w<q5a&!5+f;XU|$`%Oji&7YeLvmVlWyELgX`KHW~+^?rU`36HB&ht2w*RxGH)sLyT2cO>qocOsGpYa|2UM%~@b=lnhyK{VAm-lD?`9It~^DeztE3Maao)0(q^VI(8yuWQWa{J5cd0qoYQax+Eukt#0w&8hsRpYu+AMp4ClE^oWtWWt(zf_@lm=-qWzo&S(obE@nFYg>m-zO{TL@Qs5RQY@U(G#qEWoH<-pYolxZ$F;DPk0?@<(sm`7U@f)9N0I1k1?wOe}0k&^7u;)nM-+>C_K)-<@vszHz=0oy|y>E&*{p(%b)c5QEfDX+dCKVdfp7D&mHoSAGzOxFF5~&4%A*=Ry~#aS-tl%jiW)sEZU!?3i(ogGWm*onKQI5&w|M}H9t(gdL!mE{eJ&~OVs}B6MXJ{dt!>EZ(6g7zc2DP^`d^Wnq8)RJs0!$SF5|fK4IZ2;fwfts=uZ>(zwEgkS`s3cFi)smNJ^#50AQDly7(+Y2_=+Cvp211NnQ@#kJznEPQE2e``N%8t3WrjQ&1R-tB9&^tFT<{P!t2K7*;guECFKbi*=_)-Un0)%v9T^=(nUaweX9C36?&dE70>s$clZo32Irnr+d(x-itrm)@mto@F(y#&7nm<`ru7uR1#3{M8}1sw9c9lN_bU!506dLzv>ntVREmj^W<_tAEnb)Z6p_`%gNu^)ZyTk))f@GT`F6meAvh#Cla?w$u5B#O;LM1Q$o!lJG^lYtWM5l4v9ND)L@OzhWGvpx43I(MIr7o%8f~j1YVudI@|Vd=YvUd=Z=l%>-wGPeadxPlL}vbHL}ox1bNfx4;je|AHTY|AE@tF#iKCX2V(;Tny|8tqyhsJ4361oxxS1<-t|K<)9L{9QY&FQ0P;rgf+f`y)p06b?`Ot4QMtv8#QnPdsQ6!RUG?X3L&^O)DCQidMk}_J;8WHJi*@PfiEGRU=PoNGZ9a)SLeYwh$q;Shv0t^Pp}8J=(jS~TyS-)v*2o2Tfya_64q6$TfS7dwt~&;FW9_Cg3bFV*u2;IQei#hThvUxMP21v)Ly<tedb%#aK1&I3pU>i`Pk=tsc_FX>#<3Xoe07E^*9FI3f%<W3XVqz-U!_c-U$9#k2L5W=w|R9@HXg9@HX&4gy5sl{oteEyB1@;ixB*kzLrgGSl{AW_-_${4@0+t4}%k-@!&-8T7+ODbR*aZ-V6O1yce8du@)H!!8P=8wXk8W02O`(T+{OoZTEmR@B!#H@Bwf#^dLAHd>kS8HuNa?Hn@@v>s_!2!Hu9|9UCD8H@7KV>*ff--g?x8HiI?=Hv`v)iv6gMYr$u*M~A^@z)8?Va1wYObS-!t_$P$m^-v>tJ$N5<FL)pL0yG1B0qkPKD)z|*A=uZZa4&rkf?Mn11@(ls0DFRKLo0x5gWsVJ#D2d+2tElt06qy$fhL1fz$c)`!6(4KAq0P6!+IMmLa+=Kbs!@IyFnX)-M}8u=3ozSU8py>F4*3pR_qai@9BO1BC+N|g`bOS!FABK8MqF(3A8@A3D^ND>d67uf>TjrN#IoQcIZ0rc5njpCvXCI4MK1nbUio@ybHPyybF8^dI5Y2T+fD8)LA`*;8svya4T>Cv^6*Y+}@%V+am<K>+!pu-$&PHP<OBh!Ox*yU=f1<fO>*O2z~*r4HhBzB~;Y$ON8K8(39X--~wn0xB&bo^aS`%@N4LA;Md^45Q5)BMSZ`=wcv`Vc^O<0>;!cKJAunWJ-}tbe@m=&!6F3z3bhA|5PTUb>iaT6ut_Ss2TTaTHhSB}HmrAWE&MwO!RgRka60%6RNN<Ta4onY?wuy!hG18y1K1V(2=|Y;PaYuzAAxQM9|7-%CV+Q?w?Nl`w}5vb1h0n1fmee!KzD&RfDb`Wfe(Q{K*jy@0oQ_C;+|>+ZV3*A27m*>9ii>P9l;%-?qH!l;6Zxy)<e}}pdS787@$WlJ;HEZMUVgJWBSrYd@n3XZS?p?4?jKH>ERDwa9cf=>urBT)Y7lN)}w(QEA;DCdaTqVM8EE$N2ng%^ysQbcRf1m(GStr;<~3Eee~#|M<+dk^#~Hbr{`*=M;An>9svl!oe_eAp#ET?{lP)tDCjV76!=>`216sD!@v>Xp$NhKp#8!9z`YTIgQ5Ole~d2}A-FxX3%EVFHMAADHP{Cs_-lk<Z)jJrH@G=Ma9d~>a2Kqj;HJ=K&;W2Va3^SIaA&M(CxqY*2*Ev|QQ#=7X%B?p0T$~%03kR`kKxd0=wNU(cnmZG9D%(NJQ6wtIutw<`!ob0co4KVco4WRLU4CzFgO_d)EyyMfwl%K;5G=sjiEl^D$uG>AFvPhwJJie143|Js5iJSxDm8DxDmJpLa;luE!e#G?g+sR5rRFS&A=XDM}*)e&`#hc;1<vhV4*$0Ex_L(1h<0@0Jj78goc58f~QG^wIcWj=s4(b@Hp@UXf${NcoK9BcoKM`R9H_F5rW4f1cyV1fWyI~po74pz$2i2!6U$ZpxwcJz#&it90K-52<`}N0~XpC+!5SBDy+E%2*H*0s0NjxRlqX1KC~)Wr~|k@xE?~VGqf&PXd|#Q_$!3qn$Q~HFQN9(8epOBV4)4c_Fy}x2iOi=7U~Et3oZw30xk!3fwlm<fW4sKfW5$h2*G2a?Z85Ng2#eqL#KgfgXc<xbvzd#c!3^^q4S_Wfaif{LC1k-fu}+zfTx1LhfV?uoe2IOJOv@x038oDfF~ma$3VluG2qeAQQ*<wNazS~Bv^&^0juC%2*KT;A>eLcKd3KQXh*OgxFxg!xFy&PS{dvHu7wa>M=HE$1eb@_hE@aD20KAzuoKu7S|2R59@rIJ9U-_9)EO-FD{v)n1%%*=(3;?i;8IfIJtnv$v^YZW7YM<&&@aKZ;4)Bqa2aq3s2#Wj*!&~d23i(u11^RTTpC&qEYt;D8te)60(*i7A_UKX27-l-1<wG_fzAfc0ndld1<waBf-V3r0xv-bUM3aZx62TMmm&l&gw6vm1jj;Wfn&ilp;N&#!PBANgQtVPgH8d52HSk$SnPlL@4kgU2C*Sl|M~ax-?aWKCClHuq38Pa7fhkS#l`;X#q<Te=sgp6qx4@a8t9t'

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
