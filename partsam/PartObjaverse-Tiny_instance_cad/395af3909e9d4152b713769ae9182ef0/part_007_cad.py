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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_007.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_007.stl', 'source_sha256': '706a3cbcd21293684e83eb8540c4429fb5dca12add9f4e33526e16ed9b8cb995', 'input_faces': 920, 'input_vertices': 497, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37078994512557983, -0.30424436926841736, -0.46519678831100464], [0.37080812454223633, 0.26159366965293884, 0.18165001273155212]]}
GEOMETRY_BASE85 = 'c$}r22b2`mwuWmYse_1u5=?^$P{06Qkl?f;iewR#ATUT0i2@QNI1-dBSxGYFoQCWG(;#60fgy<q>Y$h~a@DKedwuuy?*8_nYInc2-g*z+>-*~G^y$;pRi{FiHmRR4e{nDNr;Jy3#K=EN-sgEzg}vfl|4x1Sb?wlpZ>65S2PJt$qq+Q1PHoh@VUw0gUVm?J*^Zt1cIZ>KdP>=vovW3tkW#jDuRi_ywC~xjSD%iZB!8lP_r9GXdEXb?_wE!~E?4E@sufZym#>gAH0A&J=jzB1!UeKUXGfU6^U(vsP=`;K2vZLA3*;GH`t6M_ue>^#zufXj^mV0Le;DYe_X8(|dFQG`^RyiUPelKI{xvJ3uPgcMDSw`_r)jkRv~!0~`TOx2*P5Lw%M+&r+GjMKcsRN|@TZghJUp~pl%aAx0=ZY>#8~MkWkcSHK>xRQc|Z2K799`t)2Mqi5BDr_+}}QL%;xRU@pR8U7U-vIskxGei+2g+;g^@?M!Eg3+`xJ`F?&n2{pmBgfqv#U_$c~5_iqoh_l8xQDD5+rv<l|??ussZtJfV3jDL64==bDxAGJR)p6csAjxG<avoA27;=Rs9-*;@o_haKIvQ6GE?T4Y8qJLlH^WD+cZ#=&)QSREmRyv$0&v<I=Vt<~}^WCt&pNyXe1p4=K{*#?B-}38Xf3E%5_AaM=+OrFGMYoGTlNU&y_t20{{#?fyIu_cSDEG>xwDsrd^~Ue<_mgs6YOwz)9kLVU=_wVL`g8ZWnqIRvVSeGKZvNbTF4NxSro9`d8IR^Vo>1t!a9}&n{Ui4GS>?ll?P}%syQ2Ajl?eMkmp8uOp6o<<>(S}{T;JEWcRB6DWvfNU>s{<W#J`=mobM%kr*|+>9%@iH`u>`SCf}Rm?<Z9Djh+7f!=pOwOq8e9D8JmF>-Q2GwCO;?{N3{zslHsl7u(+DroE2Sj>nCk@q|C`v)w;VZ}H&w6Xoe0k|+6d{a(TqPv<1cz4N)VQhm98FSfn=zD#=^ryY;xI-XGNecPhr{IS85Y~Oz5a=youGWQ%wl!tF^wLaCChrViYD6l_vp1#e$J*Ov^iq3DLZz=@dH)GLtI}+ugzj9albNznPy@Q7n=AX=regEY8{o3{}H|=%&c08K9@yx$roB#XGINf7^qTFj+_^ni5uIt~nci$K7^Tw^;>fhhJrN2gxBYA^|Yz?f>emy^l=B-z5@wX2@_WRi=yT7z0us$zV*qtc%YP>$npX+v*k+JrJM7dY<;Hp$#uG^t)@3v3V-mOnF9?ji&me$+s|Gc5y3u620O$#>pKX2a2<5|)E^CoQcf3EPiqoeb)&ArgNs)6=8&-A%)Fgrn>K78(Ce|t9%nD%b}vhDd?c0BI$GM@BhWi~|LH+k|x|NiK5Jr4eOAU9DSo>p<Izn{>!Uk>~C$MEPCng0GWM)uB1l;_nfw$`7!dG*dIxry>{k4CZcC~`Nin)aI8_Bu{G9yfl*<9+qydjB{>HKvCX<>8j|7W#ADZd2-<KAI@^x@_E->dSSzwe8*ZY})HM?RYfT@r0LTt_$ps8G~{X<>~z{yq)UH-Tq?QYp(4xE)-c4_#QK>MdyE;d%xX2C6Ke7hq`7RPLz9VhphAWuiLq8@8&VvUcW~(9?f+;d5iKb3w)34FE-cx#pSFw-5+hP`=jQ%-fVlfK5cvb9?f{%_!&>ioLi#jao#VDSNiu~m+SHLV3FgA@=$?Ccli5BtMkQC|NfiOaL^Ke|Do&|+Y;s-JFNHT?)W$<cD)pr-&!|%J*BxjKAQF}H|=$tc04X;Jn3g9FY=Ew<;KxF66N927gqRlcfK^M#Ic0=lO3b$Pjh#^WZJvjwAXRk@o28&$yhsJeqcSbzuR2*cbBst>3m{yoli8^{m8a=`<H3&*0ULp8$aU--LN3TzaP2t5R<#}7IHT~oAz$|r+v7^+p_}eN009&cgJ_l^*m6|A58AfAIRN#nrZKjr>4DIKW03dyYcMrF)1)kJ%2X2JD=BF=PNxwH@Q1MCwKFSY46sjY465q#-q88C;iSHW261dNsb;L-1!5!J5PA<^znrGGY`b}Z}PNpV{=pe{Y>sU#@~Nv|I{u1+|4IzrX5d|hi0_MPW9z(J~8dx`GaY%<I(r^c8wer7!UK0%k_Gnc`Pnx9@E@ikDK-`H|^bc^nLGWH_SgCJ)hCs9cMW&vbmlYxqkFGYudZ(Q`26@qwkxZuX*3V_N>?YHrM+D<ZgR2?OjfL@4b&-3VdF!n>2UFU#`F6a<0EzKYIK%?Okr#yU(ldTXImFRNr{?`dxE(-pGA`xSaa{t{*+GGwoe&+Ut1S`=0yvF#mY;{*UHv{c|5FF6Tay=5GC)_Aa;Wb^qmkGv+lL?;nr5Uq`O(HBVo9Y+AH^%`?IIM05Ia_Z!LG{Lg(no9lf%m+Sn=eI%RfeI%E&{pfuOo9lfEm+Ns>ubWKnuAB68>GcBVX*SpMG|k<0kj|?%*LhXnSLfR)rB7rh$n%PA4YYUHO{RaBoBrMPiy6P>cKq(V!mJ-R&)D_D{%F^~yUsQ1-yQGF_v`i}^ZmNxwb_2$c5b#G-EQr6nD)z#!12p_b=d4g+rQ>^`w!>*nvrP#)!gpCaXI^==63&$%k{qToNpHT-&f}o&FwrEmoqQ9e#|@;muvf?!<YEqSLapD?R*}WGe5h2%zPe~(>|O(b!lL|aomZ^^}aN@Jx;~tdR(iUu`KYp^!P|_kIOdK<E-n)9G7jb?Ng>dw8H<s?)u2)dcCH(Id6%}_4<q4p0~v1v`^2ev@-C%dj4keyw;sJ`182)I+MHeH1fFfI+JVr(CQJv_tpE)<o0|uE@$5J>L#xaY$u#2+g#6+U2e|XZLa6xn%nbso7?vGyxr#Ry#30e>;2=@>lB;ob&AW)b(78YI!JSS-DGpy-d;D^T*u?p%F6VwH@!}@xn3t~Zm%nC?yf_xzI#Jp{cxRYb9bGqxw-DPxn4(WZm+v-Zrj`IZkxON05{K#zRumxzpd`M7&mP6k6-UU*j(>FXm0O^#O2)I(A?e+iOWrUdq2eHI-c-HOEv|*7v{IPocT?2dp{~JXTH+h-j9mQO?!JkDlXUiQQn_{ak}$c&CUHfo4fNUa(llnoWJ{K|Mu_h|C`+X9-+CppJ{XV`vSSWpK0^B_U3-3&2>DXMeSq9J$-H=XK(cPrqH67xB17f_jPTq_jO%v?laq5?;C4w?=#yxuD!X>Y;zrtcjo3S|N7MX>NeN=>YCg8@HW@>=_NC>{OdvI2b=5spt=2>!sa^vXl{R}u(@q-f2Xjy``sj~_zwR#-F*y`yWeHV?e9c3clRsE?e9c3x9#okL^gN7TYWq(I8NOkH8;Pb*<7!8G`GK_dBy(N>EBLtKeD;*M=m$NGumADQ_bz~j5d#JZ+>UAx%-{5@x^dp``6>U$=&$|x&2+(=I;D~-2N_XbKBnjE^KohPsX>|yZq}-&mU~A=MS3O-`{Pn?NcTk+T~vl?mEci`aFQ<_W6XkT(6JF?eht7xoK~oPq4X;C!>1F-TravcI$HUT!+o|`dxGTT!**(AJN=Bx7Klb^!dV!u|3}ptbfjXZLa6Nn%n1LY_8|kn%n1LY;N1z=V5H_?&nt+xW_+Ez3#TTd;W*qK93ZabA7G3eI6+;H|_27NH*8;q_-co$N#-}6|anqyW+9H_}%xYxp|Ju=6ZidbA4aePv^pWqw7(hOKCbc_Pk1ohI<3wBiHG1IoIi$+vn5ba@wce({G=@AH6?gbA7%}bNjqsT+V$M&F%Akak*)4pZBx5jwjq~!#@9d3pWbwk8ZcUP6t1i?!V;rIZ2!A{V~n$bCTh!R__mdUcKLCbDrDO+&<?Sm+Nz(WlQAv`*GtZx6i5CT%S|bT>E#wgD)B$Xz%VDjF^5Pu>FtSk{)eWt<9l8&hu2^f|WlAY`2ASrbpWk>U`MWK78M*==DYD{*)tu_B_v)cc6T(Kldt^h|SA|Zao%w->Nsf9{pTBY9IIKX)V5u&SPl}_a6`Rlatmxx_oo~lm0yIy=FZB)#GHK|H5lx_cPCAo(kljbd6p&Wz22$VPJbJlpJf{H0yNWeY+Msp4}wyRQ<YhZ8J0OjdT&ItGwb~=k~rw>Lrvv%EXV<cdhcjdZhm02k-y?K2rZplINX@)K~C*JSS3LM=BFu!1G1MTr^Tw!eY3*w!Ig7z3>HGUi&kz7ygJB@nU^l53j`KwfFLRVFg@X`#rB0Uc|5PVto~Y*W)s_;*3vt170{%*V6a3^e_HXq^}?7`v>|LkNg{bj{>j|E`2^lzrttnYa(?W?{gjRQJDU}qi^B2xcoN_@*c^s04{w#N58@rxb$C;zJ*ue(&v}-EBpeN*S?$-d%dt3UXac8DwrRa*M7t6zhPStf0=Ef8O+45X1pHEkKe#}i?NQc^=%Wvui&-#wS11Rcu(;!;8nPk__r`WE+zg0OvaO0pFgm!#V^7_cp<i#i+tzeKf)`$%iHUZd}g8KnXnjMjL$3nEZ<iq>$;h5KgwZ0IK}$a?Y%wQiBR&wEQ?<Qzr?TMdnyRO!wa$<c<?9OWBZfu>S{a*>NYO*J^RxYcoFzBF7-2Wz|VXZaVc@#=ZdoZ7A1d*<s7!h9JVL%X_49!shN~`4ki8<{0}btTT;yb!XKc-+riGb@GZO@J{qpYN8`)jUVIt81D?ir;78$S_)+|0_&NSD{wd7EKgG|&kMOg2F5HLb;yd9wd?&sfPQsVtV_+A244ww7;%WGU(8C|Z|I3SUuNQME@dJ^X1*gNk_;h>@C4LA>Ux!#0zk>IvieG_OfnD$__zQ3n{sKM@uEWRSE8#wTB_4(!;bHtZCH@J_!}ItqKcU3W!_V;Z_&InQKZhTKd+}p<He8Em<0~lfvG6Ti*cl&-w}*ej+vAm?>`Rqd7EelwmH0vSwLSPjd^Vhh&&K;w;@v6nm*Gr&5S$NZ;xpOj=TqWG;9vL={9ly#y-6|3{x2?Uhu@1o2S?-2;puQ0o{rCfJMcO9CQAGOJc<iH#t-0!De({Cr}&5X5qK6qf**vrxNs+a5Z?@!<D2ohl=$m#3@%K=U&mX(2k{no1t|M@1(wDC&AxvC|2KZrHy0eG#1};BRoDm4!e=o@^r6IiP~!dI9K0Vsgc4swi64W9aG}g2$5<B6Pl;E8RdC@8cqP0Q9EZ2UN5GZ%2z(wTz7>XX;c<K`{sH_1{{TM;&*LZYGnDuVcn&{-AA-klVK#mU-$IGM3s>Op;=|!sT-Y8Tj<<xB@s@Z+n1olv^Ff(Y^06$Q%RDn1&&3zQzPNBOz7StYiN6`CF0c(8jJLrX!M=E3=B!4P_!IDD{0Y1PCEnUMueGMcJ5l1J;Cy@(z8oIGm*XelzwndzpOpArNioVCCoX&rzYA|fiT8u)xNr{M51$4%;nVO1l=udC02dy{H{e<DLp%%L1CQW)@a^y*z8&8PH{%=eg>Wvu5T6cT$EV}3P~weY3tU(MZ;am!WnR0RW$}M9*B!<GiJyWC@Kg8--`ux?5`QC7o#FHFRb1Eye;#j0i9ZQ@;KF|RlXzoFye%ApzX(UeA-Hf6J{n&IkKwEE(@^Hn(=3Y@Op37*UJx$_TjAyKr{M_vX?y^jhY!HthFkHs@x_$*d+-BXcoKgP-wn^;yYc<-1il~N1rOo7@NJa%BDe(?zKbuyXTah347@*ViTB5wz>0Viye!Ozm&FTE;vaf3${Z>#T!;%-;veF9l=v1({4Mw<u5;^Kl=$nB>I$2|E_gHiQP>856n_{t!i7)Z591F~;#FY-yeggwTjQyCQ`iY_ig%#IUxTCY*YF8&IX(g31W)3d@J}i6-{GIQQ0C>|Sr)%JDaJ<l&G=)mAO0BL4Nk+m;jh94_^bF7N_-aFfX~90z${$22Va7(f!pyl_)<!IHr$BM#;3xCxNtf?6(3BAcZaXw!p3-ayf(ZWuZ`bAiT~lnD08&9@D%<B{uw2{8Lq%L;}hW<_(VM2yF8DJcZAQt&iFHU2tJPs8{#3n8YNyCK8aVxtHZ{)uq|F4e~c1u?p>bun^WR1QR2hlXnZ(6i4xxmSK(Xn^YAn-lzIO=%i>oi#aIr%62FZSuLGaPg#++9cu)8?-V+}R7vn?mneaV)CO#kT#^>X!;eLEIz8>zv*W;_;HhdMH0T<yJ_&ab0{ti9__Q!|dJzx{O2mUxLi$9Lv3Jc)3;)S5h^@U&_E+u|dQmn+k;_tWMU*XyCEj$}vPl->4uj9h5_+)%cq=v$Fuq!TXhPT6OQ{wl*NAdgcvhZQNES>@%#D!Jy6#Oojir<A-q{M5%rg$y9CG3C?fFocBT=*J30v`t_;N$SMa1*{3-vK|xci<N&@!#O@xKNHOzp*S{A}Pkl@Dg}+*bT3a*QLa}!dG$O6uc|m2hPI#;KSe&d>H-)T!X)XPo%`(giCSZZ2V39H8>T24etvF<9+d$V0Zi_{3%!)e+sVwZ^3KeC7~QwO0q2e4@&$?_!<5sz7uZ7g%k0e_&S)5ufxYv;v>Dw$06~7uodixx56KR&)|>Xm0$?3gx?LT;lj%J-FO*Fyd12Km&5OekKy;@kHhBp<9Hf;2~Wd^QQ~9aaC|I2g%Zz%lW^fyJQEMY^LQBl8p?6&YnH{Yro>Cb+i+nWyfj{m60Z+?;`Q;~a46mz9|ULO!uj|hd=y-bkHROw_4ovQGF*jE#>c}9d^|o9zJrg%2f`uvK)e_1f%n4eQQ|e><GAovye3`>7Q%&B;id3oO8k2-MmcVY3$yX>@w0F}eiq+FiEo3Gap4$z8@}4Rd^}rCi7%$a=ThRYP~uHsJG=>A1J=fC;N{_cxUei<9=`>q;J4r<De;@&UHDD-9k3#P2mTPOg+GMXgDvrTcrWkru~7VNI1diMg(L8J_)<6yUy5&lYw-<u7A1ZL?!bi?@H6;D_#1u^|Ai92J}E{yE{Y4Q<JaRUlz25*7Z-NLtKlKo2M^&5;4r)a-kcI|1K+@f6Y(~9C-^4b32zHu!`tG|QsNC^UtIVS-VlG35`P#zg$rxo594KENxTeR49an_7|Y_ndNF>9|B8PHcjDjSA5-Gn;W}J69^Z~{gd_2d_%cd7!@GR!6n_Wyh6C~5czxIk7e0d5$Nxr&-w7+>cj7n0yYZXxQm_mzEQgoEZ>7ZVf%oIW$MJjcnw0p{Fb#hi?+=IJ{qc7x@g;C9z64(br{HVw_h2Ue9=;of@!j}2_%(hG|A7)OoD`!RgT;lV@xu5Gl=vO67Jdhw3hU#--gqkhBqja~9E1x;;m_dDQ{o-r1Y9^7?})z$$Kx;J9pFg31Kt`A#9QM{VK2NX{sbld2&{(-YvPaKw^QQ9VJTdgj2Fj?Myd$B1}5W0;Ll!+$+%FC$KplEeq{N3TzD3jHo|XMK8p)?;lgdWv=@HP@-|$!8kaW0k62!f3m4<kMtGd%#kg=TE^UM#usj!+T)2<rx%fVO27Cpdf%l}u>%t~@UAzjcfeXvyRq)#>@zU@Xyfl6zEQ#NUmw-3n!aML1_-&N<1MngI0lW^Zhu6Wo!CrVbe5!Z(yg~d@q~4FzemE7MN}K&~9)1ZPhV$@C@C2NP3zy=;4frMa3EY4Sv+zss3z&rq&)}Efx9|)uyog_dKf#OmCHQxE5f}b~3+24z@3a?Q%d+I+m&mST`FdQKf=e6WjV!0&!fLp*5#GddHC!0Ng$;0NFT9iG2Dq>}E^UP6S#FLC+u+hhcpuAcaLI)avD^k1cEW{iacM8SpXIi=@L62i2=9qhlln<l6wmiR{V%gG|B>HQy}<uK+rBdRSg`+<&qn%k4+%G^Um*Hy<`t2D<cH-4<kt)DzX66Km_h'

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
