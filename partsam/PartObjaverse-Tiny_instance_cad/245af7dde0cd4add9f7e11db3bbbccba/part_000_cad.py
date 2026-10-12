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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_000.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_000.stl', 'source_sha256': 'bd1979017c8000114a9d46a8a4fd32af2a60ed193fc80a4a850ab60cb98da216', 'input_faces': 700, 'input_vertices': 388, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2542729079723358, -0.2676115036010742, -0.20517848432064056], [0.3601413369178772, -0.06418421864509583, 0.33963918685913086]]}
GEOMETRY_BASE85 = 'c$}r22XqzH-nS<dMWhp&v_lO|2)&a7NGJgey#+Xw(0lI;1n`O=ipUiZ2u<Mv3euC1ObVb#FQJMD5J3?ODqirSFMIyaBzw5$TkBizo4fY<J$deC&z`;a%-J(1%gBhV*@6xEDPv6T<q7teHw;yB8NtSs=n0dC4~m{xeayJ&K}J5?s~;!d>)5SBWUnA&iZL@}aP-7M6G9q!LYfR|5K_$(GGy$8NfQQ)=|6VD;ArK;2aK8+{mf4sHeg)zv)?P#ZqT5br*`FPp4p!N<xfu4m7wr5Vb9W>RQ*Vj>eELF7uE0nNxf`uG@EhE_7#`Aym$Mp6x~~UqFwEn2R7Q?H)fi&Q*)5rj(6*Hw?FteMfd(rOQoGM>%Xx5&*j8NEtlgCU1EE4cM+F2=AW^2Z{GRT_Ez-)QomU?mp9`6v~=%#cvOyiW6qcMadSssu>HOh;=LjEdHLJ6JZ_(Nj<YWB>r>hGvEg4yKhK@B&&&VEclPo9e!ukRrHS@9cxIe+dGFL~DJ~y;PyB@Tc7Lp@1MU9!Ke;dM#MH9Ae^D=&H+S?%bon+vx%%me|4GJU_+Qfg(>`{8eDSMY-dON3#pTy#KWiU1=#iY~vi5fSjyF!9Ow_%nST6C|4%*}FD{}91`}lkEir>6Q&h!3xx9|9crTf^>N@w+TWgVSj&zI4=iuC76FS{L2%a85)j`uG5&C<O;xq;NLR9x2c%r3Hi@TS!~Rrl7FuHvf{m+@TLL*^}O5Am;8mGM8^+V*BVeqeZ_?tR_*$Z@|9J7Kr~^RV+_nm3*{OwhfNeYo`hX1d*P@AMxo=-zs9QL^qWbFBEN2ll*J531P5b-d9gB~kaWzl;;#<+0s=U!EcMaUE|~J(i$*Pq$rXUF#=mu07tq+`FZn^xxv`c4tJ%{2UQ)?r&h9uNmIW?N?My(7o^Dy>h-o>bcgH<E{A>EthY9Sn6-gYoCw*R$b{2-n!8&Rrj&mj!HjEKeW#`c0>Ckx;Ik~Cb<0kbg6HwxBKtgKG{CL_t#6}m#wvZ?1+Bn!ZdI0nG>)3*zK2H>(={^LiW1yCf|~FzW+kj<&r@%&v<8k9q-?GN4$05s6B4u9?Nx&H!5vO)xEjko{Z0y&UQbob<yW^Z@v+npnKn$m*xNeptxK=FK@lz@{!F`Ts~VtIq&jC?C~`I8FOCu#>lr5U4C6*@qJdxddOGJ?yuv`h;i|Oys@;Q%Ug>}$#MS*k^65UxsDz0tP{t_)(DYy#z)x4^}pCKRrhA;7ZP;u{ko2{vtfapSI5h;PH%=w{YSE%jPoHf&Uo*`ipje7*N!-+UoXB!d*%N2ZddVrn%n*H-sxh`hvS|5fa9&8?oxlu9(&$Bm8aY7WcUJWQeD1?@0@;Jd+$a|J9y{1cD%2w%)gamx!oVn#!GUaP8cSB?aOk1s5a|}?v0}h6LlZEXR`S4B66OGP9D>}w{iUxmrtA_{o(%LjmVbl^4uRBZ%myj?c^CK=aprP91m~o`~9%)WADzA{{PWkuG6|t<o<zo?pMB#<nupvo=HDX%KXk=eaK!H``(cH&VA#C%(LS&?i+aX%Xh`kx-ae2e8XP<j<-gQw{-9M^dmX$=9=>Px;ahe8E;)Lk*s^4_kgtT?62nJm+LViLE5?6Th?urPvtto8y)T**1eH%SbV-8Wj}K&t9-uTt+wORbRSzkO^(}eirv21dzIau<DGqo^}^sYuKLHjCc6B{FQq>F2W#gXmp68uNp$%sXT+PU?DO|dyLR5?ho`3M-aGH29GA~!V{19Py$t_a+eDWyenr}8)=K(c>#xHu-?pe-&kPQdea(#<(*Kh`+Wj|MzU}hH(4<7&o8R3Qf3AS6+Z)H^{)@LN-<8j;e@{B%s^4R%708>_S0w7~_&0pR{kfX-=fe4Oy7#_R%hJ6S{y;LStn617u05}Nb4jCAmoJl7#`WjCGCuqL_Ik|l=M!ar{$`&z-5XiWM7_Qdkzc&?91-`r{Ep9fj==k>1<Q5A{nMN6Em{Bdi^;#c{;jOr&12nu%g{94$G%xo{N<&x4`|))beQgIFSNZC@p8PYKF<;VRiAxnM*VVSWSn@uh#j*`>f?>7Pc7YhujAPd8@0Z&$1Qe6SvlVa|CIYi<W<{yvzM3l+249sy&tc8XMdaF*M~^^JIdMX!GADIn(n<9t5~}C_oyWG+b_4r%P3spsLR()NOk#Ns!D%)-<SJ#md>eRnl~qPl>Wa}<%sUR`($6`>wePZtw-&W1JyS@QSo~F-hWk-`ZrFWQQl+iIOOtMK0j@bWB5c%_vY4h`vQ5R&#$}nc47y<Dt?LQtliHR+ji^TtSHB|+IQOIs^8?%?tngR=Ptb+|0~tyexG*4?x%TWX^ifT>G$Nh;8OVFB+Z*yJIHuey}m~G&Ul)0C&s$!4{e_usJ@w{e|*69M{VAx_s0xvAmiEhN4YPBmN}<;<E=54?)|+QiJ$v{+)vs*cKZ=&DK0-aOpY7BT<XsWKWNWGNv|B2=Q7WYHAi&s?O8ij_x`2L#cv8dF6+vW`yt-i|Ei^Xb5n$Pp1aK&`Rvbk$2-s6j`w{MDW2zI@77OT-gz#5-g^g}wY@d&ihW+zkWO;k(zB(VW$EILZd@<Ub3t~gH@>^;K56#rc1rioebVv1TRo&c?^XP(H@iLWRUGe0>n-insv)1hKQxo)W4zU|w55CBtUj*$urb;v{om5pHJ-6CPttVnjHly`)BWA|^KIGeakIh(xV&|uqTRl4*Fe`e#CkT$a|+%W2ge(0N4Un*-_JM|$eRzk$oO;{DebiRM%MZCcjP?>-fA$y(!D?L96qn!mFJBy;b|^k?{JFlV_%Wy9`EG_vac&S*ItK?H}aQHcKN-F<hXn;8{Oo2!12!Kvg6I9x1{}2XJz02)qpd)w;C@^cKM|%rT)&-@|^kFH}*cq@#gtC$u1wV+BGkp)xGWW^2}K0ns=+$@>JbB^X_<S!6rFhXa6=(p6fEavww5^vaNF5l<IQdYt}-}1Mf{NoveFb*nVk;eXNo8qdeE(oqcSEZx=81(+kUeCg+pWy0;31r|Ld7OM>gZWd8lLtUJ7OUvj(=pWt3^!8hf&6Aw!}zZI1Gz(sk^bG$RZj`x0(DE*vKO6KcT-qSgLY_k;I$BsDezK(8vB>R(VU%L8ZP1s|fm;cy#*XO=@Y@Dof$Md<L;m=)`b_NH_^WEx3mdlrDl%jj{-YwTY&D>Th#pT(jW%&Geq@9g%vQF~ukag?$@Qtau_xyU-b-unUL9*_0JanC}5w=X~pZG(@f5|S{=hQ2cl%#p%x3#G*zdFkWy?yWRJMI0fCx0W`JI`yr`StC6i{s5ZHDsJSTy^_>)sh3&KU_lIZ#?do>hi7n+n>w+rlzHPqtI@9zu`TZYVTXjFR1_L=@WW8jyL|;W7jwQ6F0f)`^MP&li1OR?fr>oeq(vgyPI-GZ{P8r1D~9B^#^a}h?f0Bv7iO^?~R(s`^Xgq&+6?v-djW3&*+ciD^_P8xY6FXINmVJ%D(0O^KaV6e<<F(xc#(#T*q6*PM!!<-&;HM3%&h}c9<{kgeZF-WmN7i$DK1!_O~ydND0%t_q|8<`uA;EoThtgc~x0&J<1)?y_t1ja-jM~%^%|R_I)?0U+kbgKEBtj-MY6DN6P+lZP(3#yl+gGL%R3eE^3dDas0i-0sY28mhPSNHQqdDCTZR|U!zFBmAZG%*Gw(9CZKP!{)p?m7>DQEamL~K;~GQf?hn-e4F7!pYh~FJXnY+1{P-Bh&g|C5*;>^@`dQ>7S)YwI9MZkN-7I_De8u})y7w;nm%Ly7Iy6=H#`Kc%xu0qrakc+;6M28s`R_EBXMb*usqtJp@%Hs)HH>l{*IZueGvz%!*U5F-xu^8A%kQrB<9MV07P+pECvI~2NoDMIjHPLAzv1RC*ZAa=?~#nFGvvDKRArIwtwP&m{d|9QQIcLiM+q5+yf;_rKI3}1cwwFH&A*$<I(hS=tG;=AfUJ|RQr+!0NtXLhRCBvOM%7{BFV>a!_6wJ#=-#{NYgx~$TBPYdqd%iByS$lidUBxpMog;&z5UqR)Ze_^9%tvim*L}Di_f!tb3os<!Xe%J23$X7AGbs6rGdQl%h@E|JLhX$2%eFo`Hb_uP;!OtGp^G~CqB@9#`!*1-#Ops+c!r3dw-yQI{x{7nk|;^2{;ape{LL%HA6nr$J3vCmVED*<dc2T(VZ!}ch1YX9vyF9`XgDd?>$O8&U?Skb&_3vcf~~An{#H1ulV*!`+RGjI;?y1=88kQ_t%>v-zy%-W?wI!+Sw24-aP#AewY7vuI)W}=1cvAwYzn1<lnhZ_h!*~(tgZSSr7T9eWZJ%;{N@*_r5t_zIV#EK>FYE$@{uDa&0@Ldw=s78P5X^<vr?>$T7M%5}PLK-t&a|fA*I3c4Ow;B;7mL*Qn$-Tz>V_WWB!cT+?*BUjqxs`^+`H-U-vZH8@G0k17nE>GDqd@5GGKy-{mbN}&2?op4KU-&)*EjyvN!Sr4~LuGhWM@J52}JuSn;zgJks^X}EHx;I~35T|?dPx0RCv+Vk2-Q~M=Z%jULNcWz-UTMc$z^?Bvw0FPD?^qJ2d*7($($0a~@}7BAr+AlNpG(Fw?mvmTxBiH*0(mp(y9B)*t9%P-CniD0f68`C_Zj0KS}<AnX2B0r^!n!2tI|%P+VVa#=bYWTx3(JW)3SUL$a_ye*`s@N|7f`neE!C^fWAQE{jTE{SuFi;_jpSn@9C7~psStVhs*nAbLXZ&-l$jUkgK1JgZK39jRAe0rLOvB=!4XN?c@Ke{kf-70`=eV&-dT!|2{d;_+<F!#>aZlBRSys<Ns^?=T%77=h6Fiu1l`-RX)=7*HN!sOX(h2#xPWQ$p|)v4AA~GN=fzOWZ*xI8eZrB>rbQVhlc)N|1>Jsvp(c`R&rAm=Oc^3`QYMY8MruHj(im^2iG9O;Tmu&vOnAk?n6$2`@oaPW$+|;33(7+0`DV_!296jXJs#Wh&%$T{1iR}&nJDb$_RKqJc_IbtLz4kf+v&xV3iYLm5brY@H^yQcrSf=hnx@3=NO8!1{p@SXQdKFab@yFxH4Rg%mG(}UnO6HUxllaIpOMX4Kh1i0}dr$fJ5P$WEQw4T#Nk65UvGRA^(O|QCyY$53Gvf5b{r06~z_FC$K7tE0B+2RTP&e{|&36xM+|R#eY02|0F*k{|$ctuOc7AtKik-6L>YehWry=1Fs|h1FwVElYhhO;Z5XU@FsX8sm6LEzbpP1`2wtp;%#JhSQW)v$(*n%ia#b_f>lxc5t##4Me!E$MOYQZo5^gjDvCFdS>X+=``Bmsp&@DTyYdD_v4^Y#2a^TJN^k)<A6XgB2j?fN!TI5W<g0K&xDZ(#E(8}QYruu!B4j9B1TIF_gp0wikhS1f;NoNzxHw#rtO}QeOOqjRX}A<w5iSLnAS=Kn;JjpcI4_)sEDGm=b3ZG&$Z}*+Sf#qI%JIA6r`ommlw1oxg@b}5KZHMIT?A1Smmxi{vnI-rFT-WvvScne7kw&As$-WWgYX5^x>swN%m%**2a#Dbm#WPMncc|zQJjU$31@+GkVWAfa6z&vToA56hQSr!24q*b0USw=gCpTF<lFEV_$@LKehW?@zkn0q&&k8^=Wsl^6pn}Ad{#!2W67oPSokxF;&bF-_#FH-`33wn{2iGHe+T=?w_!hgo*W0Chxd?O;XUvyG7O#t_a&>sec_g5QMe^slgtU%ghR;ea0u)nv%(&@1epyk0hcCUf=j~{DT<4b1z?rs;UaJqvOZh|ZbrTiH-o#7qv6raYZr>*>Evhdba*>O@hS2gd<y=S{2Kli{+av^{u%z2^uxcxzmVtQU*Nms9{4VNnw$lnhIf#C;T`ZCvL!qR9!%DR2g4o65V!-}ob<rW;ihB>xGCI_EDbk=n~)XZCa{;HIFu{`tE>Wt!Y#;Va0@t!>;iXTUZW_AXOr9E+3-$^;-lm#_$Yja{1!d~Um<^nufSiCzrtU^x5;1N+wcwYE_?&NN}h(V!e_}H@LBj6IR`!le?kt1KY<sL9pHtqNj8T~cmmlJo&b*|8^R;up=1+yC_IAn!Xx1E6vgeyP*`OPxIH|GjDn+>*FhA;3&@@D0yvI53Lj-&<H#%U73MFFyba%Gp5n->@Kxp`jywh*W8CA&h44bgH;$YDPhcG5$f591#w(5-568iC$@Xx2#$qnH09MbB?;7&FsB%BN7~V^!!F%Ck@&KF+?<1ERna|FOmypwp%x7)IlgNQa=CirtK4d#1^I2YTE3&SU`RuQ_23gt2d{>~j99hc9e7B&uI9b@pd>5fO9~o?9zPnJIn=E8xzUxq&mn;eAg<pAA%954Hl5i!sHAQhFvJl(|u0;mJwcu)GVYnJxn=A#_h8vTW;l^+qvM$^P?m@PLd%(lVf$(rRhMWe+z!te2w&0880r(<(hfIU-!1u`g@ICk&@?H2F_yR@oRB|G$vNt>x9zebZ4}jZ})#0{q9kMK3mU*p1QQVzu4R?oUP!va#jo@gwCs_;b33no^!JXiaWNo-3+?i|)cZPeBZQx$;5V8k61fEF_hiAeo$QXD9{3U6@U&7bPi|}>$0eJ_00RK+jgMWt~k>9|N;NQp#@Ne)B6vav8RCp@$okUSQk8BIigNKoI;5y9fFpA>$$Qkf^@Cl0I6fzo4fp?KT;a%|iWGDE2_zkin{06*;><ll0|3UVG{{gQghrlc0-Q-MoH=IhYfK%a<<d^VC_%eANz6{?YAHcWZ`{eKNefTHx5&RSUko*mP2>(d_0RISoPf>i0OoEe`?`ssr$H`&vFy{3*Me!x_1bhijCsW`Q<~5ysAAX<tOD7k>i<qZ$awWWy`A8>I;Z(*woxBWRW_;7h`|y3nF`aw}KV-bp$?xHG_$GM`zQ$PGBrn10eMoKIf2gbjzYOOh>%zI<++;mCH=Kv8ue}SZ&$}X(Ewy(?EqS-3vX%C(NpUGMJSg+sl;YClYeAXsvJ{sjTLfjk`%+w-Y#x;Pu1xVOq&Fz@-J0TJWLQw<yEw%~$Yw#A@9q>ACYuIjzUx!0-USvU8<S1p#&B1P;_hTKxI5gF41;^Zy+|+I3+_!ehkL_4$QE!9xEuKz+zswRhQnRpPGl>%6Z|^a5`G=-K-Pylz!79UI09}<)`i=`ZOA%s8@M%D8*UA^qbP1d2E!@~z)j#rWInhN+<?pvH-H<G1>u6sYeS0S&SY1(Gdz%@*hhAUeQ+PLC)@{)B74D6a9^@F+!yXg_JI4r{mE`{e|P}d1s(toB0Ir@;Arx7I2s;Gc7TV%BgqJOBs_v_3y*-ukZs^G@My9%JQ^NFwu48(!zqf}lTF|z%y)Z=;*MkkxFZ}%HiR28uaOkRgUNyLV0bJ=@i@{4kAo+Wec%c3Br*z~1WzIR!c*XBWIuQsJcH~H&wyu<1K?Tk9C8pm2R6xQ*o5bkL*e=GJaQyF51vbofak)q$uaP3cqTa-o(WGUN5RwKspN2YDm<B@co^9pZqIxVqbMFiM#7QI>kx|K@#I)|JRC!ggU2ziG2|q867v^BPJ^d0Pch^ycoy>!Lz=M3xW|z5;CYO13^^N~%{a!8)8XliR}48Bj)5nV!{A|z#YA#E97C$#)7f{Z{fBxVqTX|;_Z{lH81=o1`hG=ySFXPIR^NZ;e^y?2R$hKqA|ryb1ZVw!{ikX&f7JOKuK#e&^Z(NQXB_&!ELFkC{G*P@i0tavMwVy)Q!i|`slRM6{s$=9yR!'

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
