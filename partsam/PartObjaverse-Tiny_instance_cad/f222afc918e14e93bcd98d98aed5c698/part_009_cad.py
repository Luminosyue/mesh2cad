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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_009.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_009.stl', 'source_sha256': 'a2a331528ec732e9aac2d77221c263ebd82910609714c673146027f3ef0f24c2', 'input_faces': 982, 'input_vertices': 656, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.36363595724105835, -0.5454549789428711, 0.09090910106897354], [0.45452916622161865, 0.4545450210571289, 0.818187415599823]]}
GEOMETRY_BASE85 = 'c$}r32e=o-*~R~R0Xt1;27wExh&1VfRB6%#?2RTxFbW7)Y^YbUf;Adj)L@SqV-HHAqKOhCh)7cuMHEHsQDbc3o0t8)d-tCC<MTb=N1l1kdC$z8eRuBc%no;nBZpS0TBnfyX<DeZ<>9%7UV(<PTcJ*2_N19*QzuNC)ppv9vywusZThx9;B|){Ieg@?Nnv*3oE8%&&6+T?MfcJcJtiO6qIGGD$<t?+%^W{%?DUxvCz(EQ{3)|01%1|(@iQicc)u>4yR<It*s^u$xuyTdKf8n!7B3&L_PKz4&K$6$cfbWJ1}yAdMDJ4=xFoM{7*w{RSbNvC{eqPP))s5;y0<U%FI%zA$FIK~eZ&0pI;xk~AGo%dUii4)`eORH?q%;4zwYP{@_H$#`M9q6xUTuQuKBpG`BYrDcs`{s4fv>1{xb$FDLQWG(YT>U<AxrM8+tTu*>x-D>AL1wc)b6@VtKl*dAhE7x~_S;u6b5mw{o7YM|l=r`}ecO@<fmFM33@BkMcy1^31L)d7?*ozR-VRvFFJ3C{Oe#PxL5H^eE5lx|Q?PbwhQ{$92ueb<M|h&8OnJG7n{4a$VP-KGo;Hy3J?bk6+j}AMT-_=o=oPANsfjg~i3%yRPlaAFlUMvG%TO`@&6ScNA;yy0<Uyzhc?8`|6oKcZ(mnb7e7oT+KzRis^-ED^?fN%a?9mlh=J5)ZcaWcU}EmSAQQj^><zUT~~kCqx^>rTv#-J^eBJyD1UVI_n)KsyRQDOtH0~&?>~3-cU}EmSAW+d|3a-zy^8sxNB-!MKf3#uK0bPBvH7XG`>XE$s;j@wPu105=cnrGuk%xN_1F2SdX&G+Pt~LRWqzuz{yINZSAU(Ks;j@wPu105=cnqCzsyh7BY&Bns=NQVOYeLo|8w{CR&`%*UDx$rb#1Tfzv|jv*MHT${bGO5llN!Ueg9S6_g~e0|5e@hU)S~hR`u<*_x)ORf6vLTEAO|eNB1S~x2i|?CGWTKbt~to@3*e&`>pDlr@r5+u6gSFZG7FzdFuOZrpx=S>QSEZeye(vr@Y_B*Offw{WjC({Z{oTPkFypJ<3zwZ{zDqp6HrqbY2!+^VIiV)iqCj?~SipIZxN4=Sa`#==wgq;W6f`tS74beW~vErMlmj>V99Y>w2QPw%6xf_2|0t{JO5sOQy>_R9(kG=b`GFkIuvRy6MkXb<I=fq3W8a&O_BTPo0PHbt~to^DrBKnTM`N^YF8}+xEq5|LwtbMK5p2b<wl^SK4RqUEY4ptUHSOi>~b#{Lm)Ve>Z<)F@5on`tKLh3qRahRPS?t+e-eWQx`2R=I^@tyRQDOtA8{;qG$KJ_3AHs6}w;2vwTF)@)14D2R*u9(bYe?U(qxF=`-&zT--A~H)r=NdUn6)8y2STS=!!pZ6D1a(YM#W^aq{`^k|$#&&EOYY#c<_afrrQboGzMS#<S}=9TC=4%z#&j6?Q5EI!$}LwvILVQHV8BfNd1v3GCNPvGxqeH=v3#zFLK97NB?0X>^n;_tfpyRQDOtA92R#ou-HcU}EmSO4sME&kd0UHr3iy7;@U{@HUO{@M9m{Iheq_`9zD*?bfK?EEhN**RVOU61nj^R?#h=XcHD&*_>!y837HT>P{1yZC44bn$mR^PkY>fui$Y^vqxM%wKf%kLJJV>L1O2(bYei|DvmZH2+0c|7iY;uKv;d7hV0M`7gTqNAq8F^^fMi=;|NMf6=4-b^ePU<*)N!boGzszv${8&41A||4ZsTl%H4Gej$3cU!X_t1EOpD=zT!+?X}PLLG<W-K=f=JM9;=SbRCE2eL!^ekKPAFSO4gJKy)34=zRb^dLIy7eWLdP(X;kl)89)+<1BhM4x(q{AbK_q=+QWfuKv+Di|+oV^$LrN%{SHkeqGo5Ro(MZ-Sbgh^U?cNUH$cbRabwVSE^_Cd+X*GijI%y+CK6ZJ!^jk=j1VE?`_jpq~~STOV@9GH?NO-Wb3=Xq>n4(y6B7VuD`yRzw7Gb`u2SKoV|HtUN615?Ydvm3x&$}TYe>fZzKM$tB>p3^Vx9micOXBykPXIU(y%vI`E^s-e<P|p1iWZ>+0kB_I%1~FWOw`=eWAwvR~52-Pm?Zr97V*xTKiB>+0jW`jj^wu&|hq>+0jW`V=<wy{~Bg=u!JZpUuw}88_E8AJ-%Qbp!9~UCamFeF`i2E<m0m)qS43uFsL`K0jU8=SX$+(dS5YpXaXYbELY@PuKN1QeA!YIa1xnIm=U?Bh_{M^*K^qee^j}-RDF0bCl;ub)Sb>p7I>2u0Hx4W#c2yk?QKB&rz1AJV&ZW?RhSAJoWifJ$f$W`O0*8zEqEVZXJ}qN60*PUFV_eIuBis?h8H2XVa|bi(VH!x-NQjUG!-F|HS$y&$a7%UDu=M4n2DA_GqxIs1JJNQy0{H(4%#xHGlv9V%v4a^k_ZoUw?hE_O55`SEauv*WYWa?!QNNU4O5wy0+KfYpbs9_4nGUXWv0RwRM}W-;Jp5zxP+&fA6ol|K8tq{cc2c_1Eu4R9AofZbWtU*Y8GDkMfuAMpTdTm+wYYSAYF(M0NGo??zNtfBkMmb@kWpMpTdd<+~BpBY*jBMD^^usdr9Tm48l47x6uw=>D9#?$4>V*XO#tLz-9gU7zULcUhum-(`uO<&PeH*C)FAN8j~{uKv+?eWI&>^j)9mQU3Z}pXgEk`dy#s>K}dAC%XDa-}Q;E{?T`RqN{)OU7zTYzkb&zdgQO)^@;BOh5GeZ=YQ_mdM<jl{-a0xi|E=u+FwN1_R;<#dbYo8p`V;PRQLVbbv<{e?(YMx>$yX9_0e;O>i&M>x}G~!_xB~&_1vMl`slesb${Q>^5lFG<&UoZdQMT@-(y|(^M(58`9*d0*Yk_&{=S{f2hJ(#@4EWyc}I0WFJ$-2`6U_$IR~k({(26|eqNkw)L+j>s;j@AkFxvX92AWYdNe+Ao>D#X=NzOzcRgpR9$i<?S*l0*aGuin?0S@soXb>?t}Ev<)uZdmxlHwF9OPV<>2fYpJ-V)(%T$ln2RWCiuGiIbnd;HHB<C{KBOf`JsUEGv@?NL9zo)4l?IZHOr@H#+Ij%fOW8J4z_xxSgeM)s7AJ=uCQeAy?pHkg_UasptrMk}_*L9y#U43+)Qr+i&mZ$7fs;j^5Q>y!O?Yiz$s%xIQPpQ5=e_yY%`5^n0>guoil<K|?XZI`nl<JzN?o+C(zwT42tH173s;j^5Q>sVfBm0!<k-zLysz=wAeM)t`U)`rNUG^!}qkLqaQa!q^>_@6c{<0sb9$i=V7uBQZTJ{&!b-mL4MfGSsk^M#W$Vc`U)wlVKtn{zP>x@3``ODfC3RZS5)G16JpZlldCfXmz;{SAfYN!9zKOOIOV2A(jKOMg?<ZwYKkAM%u9}Q)0D35^`!L3a>?F|2v<L46_K9u9<5gYyyJ`dj~z(?VahjKama@rYxGL$Pr`7?Mu{LWDB2;~{@ukgQx@`q6V4&D#9HVbHH_!syKq1;Em`{?sG+Wek&hKu0OhjK6d?xoKQw7H#jhEKy6!Jh{g!wv6&--Fll^u3L?hEKtthA#%6gB#urzZ<W`^u3j~h6~|O!Jh-4g&W=lzY8zp4-mfyJ_~=4x|hHg;k81s|6hXI;I28ob0`;r7v%U(#D?YY8pJihopXFg+8Le?uTES8+$qO*pq=4)@ZE^3gFC`63FYEKI@b)ZfH&Yi_5^o_Tbqk$XE+~TpRs5F)`nY~xwJE!2d_)M^}w3&%R;dw=5nxZj#nqHP9NiYaBp?M>hLSc>w56I9G_2Y_?sM`M{Ia)j$ck}cukJiB{tj(z87&LupYc2d0h=&1~<GEZg>^^SKM1eunzos^8Fon3w+;DnuO8<EQMdkecS@x4Bsb|#`J4UpM7a_E$s|%%JFN64R6fxy@(B)!<!TD4K{)|<34TxuZCaEz25--7T%PxXa+Wf-$Gt@fD7QQxwkgpzVMsLcLDhO9KVs+@OJqA+(RpH?;LMN+h*i=BjpDA8{P(QNxS{Q=I|T1$J@YL;rnsVEx~4RTX#DY()HS~V~)2bZq2<KxAnC>{o2#cxUH85P=5e*#%=v;M}0f$jN2O6mio5T8Sg~=0C*R?Gj$Jw55TL0lAtB@F<w$g|5O1Jcr~yy*a=>hKGi^PyCrn|Jd}Teufjhg{utZ>f0cL{_!->lUM7AS?K8YyMSB(9_~uYP4dox;QurstAAy_UONn0rKY?4_65=IjpWw9=Z7I6(uR{4(C@a9%bNt`LhHK#85`P8$3%-VUHTW(3EBw9%SHoYY&kArg{EJY&3}rd^T8@81Y`6;kHSrhVm+)1@E5WbfU*PvOxDx&veU^hO;Z?%qs2a+1Ns5b;lvfLUhmy2@2ih2aAxY!s!D?{p_X2$lpNIQ+`navh@gIl{*TKIh{ucDHUPt^U_&wZz4&Q@s!q?DeHTWjn$J57cRgV9M*zgVbcf?<VKGts#uLZw@`_JJ!a4mcleO7{N;XjA+-%!?r@8oz%Ng5k&q%J8*<Db$0i^tFOvwFk#;MQj&bsN!*{}{?op}YmYo#VD(ybW%kZY%MR;7@q`NWZP%yKw8X0c``i@f}0ookICrlH%W!l<yq)E+uLGF0?WJQj*3mf;+>l-%Ip0d=Y+hD93~{96U6~Parlt41PTE(cm%g!-z+L$HR}t?|5(&{80J~2S>q=4CSa$hJwR#{5WF6k?>=Qj|7i`k0c%e9t%Gbzhl7>@L}{B3XXt}4P{&?hl5At_=&`ZW8mY7$AaVFV~9tC<KbiR8xM|#A3>kP!O`#rq3jjPe+nu7R7iP4^!i`}_)oO^5o`#zy6@;`_#@oBtj~AgkMMe-?pLAwyO81!g_Q4!UKgwf|ABVjgL}fQ?pyj9eh)V<>+>!6J-kV%D-C69A;m(D?@er272ce<30MlRN?ZkO4sU{AbFd0^1^Sp)mA1wk1#BG3&xI8KTd3g8hz(2NP0<^Hjo~H43D^|g2=As~LY;Y)pq0?pc;|p!LV354;)X&6KakjPV<F{T(K~}(;2UZ89@rJ$8Sk#(dvNpG$h9`28}A<K4hrRiLW-LTDIXB{z$C37NE_o{7Si|&Z~(k}Qqj-w3%L1xiRYK-9~3Hn?*8+wn&bNs8}0;eLEIelIk6M*j$jM8&zBb9j_|7VsRHf@_n*7}d`ohCUt+@@;QJ6a1$|EJKwJ&n2k!G_AFvv{ggyya4c;o0)}ibQ?v~>R5F6Hlw<B%^wuaXtt_ik-x5BR-SQEY*eRc(F!dr&2e<(YHyX1IVV#6BnHpDH#{oyr;tAlOeE%9puR)_CGpPj+#aNB!qPwEBs&hf*D4g0}IC6)It-#7aaADmR|YX?);i?|osD7^Zi^+Pvqdynl&J;0thK9bn5FMLE&dH?c#voCR<q+(y|LtPKz9%v)*>WkJF-T3D4jC~x+o8Y<}|BTr19r&ljo57Fa?+~vCKZS3`?^AF+d>wt>1lPkq4CSLx)`D;3_$S1MZ^O3`e+YgAf1CI%a0~oH{I-B^!QY_ITJSA+w<KM&-p{RF&V3E@was{c^lo5xxUX}cgZ<&%@a_+O4)?Y3eeiR*KfnH**2?it#D;a?9f{k4{%qGF-UI9i_vgMNxCguzeQJVx!2S94=d?zScOW+09p0X}4d~DI?!>jh_Hcjh+k>^?HRw|vtPLL&$|0eARY>t)g$h1|*zlV|$_Jwl0uO<IL%XlR!SF$N4+g)6o7Xp7>l^g1nA0}bmxHh6_&dagtKjS9x$x(474gd4^Rkk<<;2U;*5kDbZ58@*=CsZAW#Fqh{x-4U>+rYax$x)lb>bDd=Vb+T%ZQhuy@l87Xs@Fie<hTqp)3Lak>hKK4gU#WP5cVD6#h@*m%-KWSMXa6z6}2deU^YP!$*fQK9s)T0QflK6Ts2%0mS{mad4~aL)-^#99{#^2A~^1K9sSc^alIE#}FR}9uMzFd@wi$Zgstgd!dcNs~=iFbmJ34nH0();NTpeN^CeBK81K9I0-(Sco;YZJ`uku;4t`L`WyldgP$16gir>8gL3>NV#A^E$;2mu6W~LMhk%peC*n6590DIipMl^I`0P;52&D_y6@F$YXHkC^b;i399|)ca?@C=4@Ibhar;pq496y!Va1{I$;whky^(f+z;3;tbIh+EHgb%0BFmNQ?$J57cXpaAy*l+~=Wa7!7kM#)RL&1~b{&P4PJQO~ZK10Am;WI)xEtDg`BXj(8V#8zMWyCYU)8I4cR|XyfKa##jfXBe6g)%*q!@$FHd=|0c(eRnX)4=KQY4n>39tA&~zK4NF!OsrmoKU)h2f^oraxV4fQfIs;aSw0~{2=POgFWC!l!SW@r8-z6$B!X4tPMXbl*2>W72GYyk0v&(1wV}XqrjT*-DtBbSQCC+D94Ag2UsV^#}FIVhg)vPlAq!3IX;@$upYcV{p*2VR}WqnJOREtb+y5|@DoFs5K2REuN*&#*sv6C*BZ<94IAY6WMac6@KX9W0llsXyfHWl?qf0uYz%KepZZ{9_^(14AIhHKIJoy~1WtteI86i_!G9gfDWU8Q?vvv)hz(o9?OvvEe}+wSd^)k=esCYdX<!R@Q`(e*E#S>VIXRSO;8eJe(^Rk-+{g7)a9?;?C})P!25b*+PkaD)27Fd1=Z4Z6>;msX+!>q$pBYLk;#O#La(!BXo#Cg4GCP#EU_1Ef;MrhDxchY?HvJs16TA~`jGq?D{_y>CZLIzR{0zIpyAyW<%i-4NV)`5QhW94!1zrUA+%5up!M#sMuowKiP|gpfD|jIMEWA48JUit4dWLdgC_O@%3-*Nfq|ID>I>0;R+F1Ri_!;(t_ai<SyaaB2=F{JB5PT5vKyV)1>w16#;Z}bovEg9&VB$l-E8v%ha&;&Jz@hM=#6!TV;FpEcpSVBTRk=R>!69(l8*CrAEJ^Y5q=MHbHoPK9xvlB8)?bpOcxh6>YY`jHPf~sb{pW*TH=lO%l8XIe9{%Q66PyRXls=b$^We6Z*uHU9lH%1#1+PzR_?sl<mc#DckKvU`1+PbJcx{q$zxTS}HE^rDmcG}b8@D~f_J`|}6n~pk@KR#Ko061UZVkxK@VcaeHz78>F-f_V8);*B1KieVTaRx^Qv6*~!CMj=-kzk~a%f5(hBqe_d_Q8t+me)9xs5i4x59l5y(3BSt|aAm5#I?O0QdE9L6YKqNy_gdzBj2@C-2SG{T{p*?rWCChWAr<Kk*;HZg5|J?nzSoQ<CyO5kHhvtV<8&>h1;~g8Ld_vEgIXJx2T}cre`S{s=w__w~WJ;h)j}O#Eb0v2GZ*wd27gjSZiKd!GlvC*hBT(l^vU4EBK^#9Ht`lHwCd%AX*99PFRt18L{EI3G-G_!QTEig+P-2;A$Q02k)2ITU}xMd*u&pH3>)E90Km5b$ZZ_jw$A8a^!44G-o0B*hPslz$k?$PjM=N5F^Cb_BQy{sDcw@1~@}^UzTKlBD?8B<0VBGAhK+fFt3<X*&{p2L4z2c;9E>wiesEI|-be<5v(HPKDc=XlvyJaAJ<nCpMe{pGyBJpw~@-pOjRrw<qC0fp`MiJiMl$O+hzqYq71nzXngq@!t>|PKR3#SCW_E$vJ*4vEekh-}^P-sqm9&GZj1)ZfmivyQhIObNnV^!_(oG+jZn;I3vezBsMIApHBZW(Cf<JvyzH+dlr4l@GL_!Zfm!#(`SHZ=J@TzhUdWTS~qij!`V508?oWpaKFb}!L#7AX>&Sw7TnkL^T2X=Iq~`6op4{b&jshg=MrC-RIKO5ZB3s;JO}OGT%S4Mg}HY36B}L(znJ(U@DFgWy8yfhK5}SMQm4xH{u5{wf9yUBmHvZh+OzWK@A;m+f>-u2{K%oz?0efnN%)`r<watDn^X87Kttv#'

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
