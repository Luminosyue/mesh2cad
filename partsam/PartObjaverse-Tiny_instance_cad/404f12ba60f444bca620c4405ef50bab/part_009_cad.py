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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_009.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_009.stl', 'source_sha256': 'eac607c2eb384f10e65ab69f59a636848a2ce0e7325bdc5f4f98bb35b663c38f', 'input_faces': 710, 'input_vertices': 435, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40369024872779846, -0.35186058282852173, -0.23778802156448364], [0.3888229727745056, 0.4247070550918579, 0.35438764095306396]]}
GEOMETRY_BASE85 = 'c$}r22b5IB*0xU*CFhJxlcRtH8FG`8z<?qdnkZ3*tRT=tNg^3R97ci!$)JE-rO8PK4#EteK!XVZm8;hr_`1%1s_*HV`Pcf__u;CwpZA^WI{Q@B30>98xOV9?<hSHsN$aBZan;rpElZW`R(@;3pfTfy4j44H>Pzvjc&yxxum0({tV5Ufaos)E1Z#5nfrG{l7*oEUw|s-avE{3H%MTtkX55&5FZCTYX5b*@x9m4!?4Ynec1XYYL1A5?R?XT~yfrIU@lNsnFaKo?r;wN{`TCJ?3}oGMsj-UJt0y&f`93S(Wu-%F)7x&}s^Yn>v~Sprqi#P~a>Na#gXeaibpHPPr&9mP0!};La+z$mAN*mYQ{UI=1E+pq>Lu~p%y9CtHVsK~`+>&aNggv|?5O$=%Q^W36V@M%^6xH@_8-42`3y;t^P0Cz{NPl_4^_dhP{_$Man%#H+qbrllKNW@JN3OOXQchj%f<K1c6|S~6OQkVEh6XpQC8dS`$~+K`Zt4ezUPlf`wx3N=NlZ5kmUA*ZQD8LWrao@b^AWw2TnTyUo)qj;PbTe)Cy^T*#c?*(MMAM$N?Fb`fa5CnuF4Q;e%2?G0yQ5?;VhKY8R9ICuFzXzOU*SslVf-^k>pusb7)f{<%c@;oL46ul^i2LwE7}Y~g&1OFv)AVY~g{Z_<A7$XUtfi;dz>ZXo@WbTKK)|8Rti`?&f?qx{_|lF!vVGG4!I5P$po(*Ae-B%f*G`<lo&1{b~Q_*Qf3hptIGEecCJgA%0vTJf!AUg?J!E2aL+C7ko}ughsi`EABZ`_(Q))%X3LEbVuxB>8k-A^rAXulNmz%Xr;dLOx5y4<tyQDGQ`O4}B{B?Ap?AcV^N5yX3fi#!3CAGv&BjVq|<DNuJsdHk3RA8!pOm_XlJ?=ZKN(vBRH9Za+|QzV!dkxsJMhU(C;v&kJ9laN3KTCheF1MSSZ!#}8hgD)s+dEP3wQaMJAuN?ersi<`)GT6(hhEoi^aFHSq5q2t6~^rPgz#3TKXajf)DruSsLYEBW~6EDXdc~;uF+g`4hj-#ZVNnRPpW70p`_g!Ir7PVy@`wW-*dB2x-mgkf_ONk%+D1)@qq_pk!ttE@3o#I<$+$Z{_ekZxVc^B8R-M;VdP161}xzAV)sQ=wJa$a8-mwZn4m3;0UlYaPGuDj5S&r3V$Gs|^!rNqT3zvg-w$Cn-kqx_0FK6Bc=c+BZ%-=yax{{bOs|EJ2*ek1XHS#vt|t^H@6`iYM_N}hYNJAQEWr;hK<D}G>AikxRcbKC9v4jh*A8Zb!C*WW>o8@KwZ)6Tb3KZ)|I9}xfK#b`e%);X_0wKAup{GBg|pKZM3`@d={`P9xL=UXTwd7f_}`P@w5zEMx+&;DlOZ%Qxq_kQox_kUSW&bRqr(m%=nNIRSAIKF?w37H4$I@@kP@LrOfuV3!Z-UrpC{jNXBaUbQ9>!NWvX+P#$nGYjMO8?|5CGE7l?~H4paovk<-<NN{Jg+lc4!V6SON@-mz%6ne`AbUs$HWiJ+~xSzdatx|cUH3Vx#UqvM_j(8{lh2brsW6!6T8aYPT-FCfi^pn-F~QY>~Y68+V|mG$D`ZVe(+Ir`~FJe`*i!cVx)et5^}yb56QT6FDAaHsQArK%YErd@xA%pm+^|}W4rxe{aZ3FeQU^gO)4n<d--HOq)(CSWlU~qzfLyk&m;F_o*c}=eDlb0NB=4HpG_z2e9Qf9w%ktwL;twu)StCg=FPUjw%hleV?MN#`4H;z!11kuS7aV+YID);2Pz-oed%b>?fXhrlKda9l6-F8cl_W!{BG;SuaM&Sp^@t)pKpfSZa)}$B=g@cDA&u3y>i^$pE!B=ig&!|_N@+`<Ua86QrqqOZXJ_(TmE0cDF4b+(r>RVm3&%>?|=7s-Y1sZZa*-%s@#|Etd@D6jrs$7Nd5d$U;9>k6{){_qs)^Pd*r+(^p|>Pme^7L?edb($-UD4-QChZ6GlkAm9N`wKk(2i{W<cu%(v?JSznfV@4jZcecz2j(th4#Ip1cxB+rytQon4#cKd+`+;2<Wm-f5tl=?O4--#1#x9{6$Nj}Tve&rjoL-OCePTK!zr0w>t&2nF|4(65dT~=QD;olRS=bf+D;!9D!y<Gfr2cvxNwx6#!?VO0e5arL$=iJY&#G{VyT^66><oRW9nde!?o{aKOOcwvE<8q(uIN0%n`hGIbK7YjJNA4#Bo|}`V-^5z!ZYRL~#9O$pJZC2M6o1?AGQK}NycFfnm+ukY-Ua0Ss_U<EzYDaI`%?3YPCnYV@U2g`%y#>sY50F`Tj6fU!uML)B%j>x%6)eHXsKUt=eZ*;-=}?Vo!M#mzL+s9-0k?sQGe(KXM6&E=1TjU?w@k}{L`KGweQn@-8{41z861OrSA%NJHCz7zxP2@`~Cu+6OLamx*Z?B&uAxjWZUsH^U=Q1ju+o-$M-Sy$;Ya6@2b=P@lBoM1_p0j;P!PsR?eF*9!bO3_5Jf+J)73NjrhjA_5U>BY+Caw;+ylTNjb+4)%o6;2Z5J7pG5hEvOCYeK-<nyzOTT`Db8`b9X=c7|GYx{TG`Jz^C6-A8K)iNKA?T`J`g<KPJHt|gKyqvg7?};ed9i+ee*t+n4`7$#(h%z=6%w?wWZ{5+=sPq-iLiHS~$LWpO5&)eLmQ=x#OG95$&7L5$jGfsc$@|v~NDAe8cdK=ce|}=ce|}=Vrt=o|{(8AE%xEF`nbvH=pCa20uD}z`H{Fr~P=_?FUc(E%V`CI=Mezy6^bbLm8*gttqzK4<yU`wzWszpMy8PkbGKBmT_%5+jjfGxAV(*eRf0or`JvKZ;X=m^DnU7eqipC(ti9InLh`wNj~Z1{mEbH4cqPeo-ZT)lkT9@Pj}Vv6MyI}?T?rFp#9*N6{P;dt@7O8ecAE7-MdM>^-^E^=6jU?xGnh@?`hf(T3zJx=@#2=-+X`5eyaDkwfm&L@!qI?^Sv=Kd4u?Wt(E%Iq+hk4>b>-z<&yvF<Tq8WckP?+w~6y#llFJW^`00v)sFIw_hj$n$&T+o@QSp5ex~jA&G+q4%`wvd#(TT=&G&ZSN24YGF7eX-JejB3H@_EnI}MZihlWV~Df4W%Z+^c>+%ZV%w;dq$UYGjXH@|23+YFR`Grq@Z-zwtg`jI@fZ+^dv)HlB01%K!%?VpnQkeE&8gZ9numEP4YrT>Q~NIy1``@i<h@2A!mO}UQlIM0#bg_yHZeyzviZ;g-k%k7f<+l)UI<!8Dee%Vu}q(2(T_zqt0JO?db{G}+rWl;Q`Z$|lnzVhA{n1AJyD8KO(@duZ^AjhdI=WBdV*S`5ZJ@MTd(r@dQNx!rhYe)IUI)Ig_q>RhQ%!8lgdeOeQp5VJ)T-tf!u;kOWyY2Q<txIgoEB8<DbjiodeH7nZ->}+c72jBg(SE9RnD{5;epqUf)L-|i?e@)e9{;~R(tbL5PK3rueeI`OFPcRCzI!C^hJ9_fZ>~Efu6yjfN1E$e+P8imEuUW_`9|s+>s=AwSnmpcdC&0^|Gp@nPikYkeRG}7_v<%~ANpmpoM*#<w%a$?>jD9MW8F{t=DJ_7;$^9CtSf5YTvxRA*-}4l9nUSfZ)x9LxAa{)E55P*seN<((;9I`{4QrC|CSx>DBoCL^$tAd_}<Vr(mxeqZMSc((+1u;BKe<QCG`djv)#VA-Wx2xSL!d~IUOhOGuk)Tjf01`$#G8wrTu&IKBfKOeUI#aeOo5VPqki+Z?0E+leS9xUoB+*NdDS4*TWMtZkGNr*4wooN;h9VpCaR^eRCaN`{p{l@4-9b8|(ktH`o8I?Fo{<|E^rWnd{qb-`rpDA6@MD{%waO&-uLP;+y*v!9BC&yzcxX^?xmEyM1%NBk->&T-Tq=`R8e9yZu!ACc`F6{oebeea{QF+c)=XBEGR-qkVI~#@aMo#w&KG^iL^iU;C-{iN5J4^{Z@?e5%O%o%YTBra(OPH~cB>4=HE6{Z#u_GyT%e2Xa3Tb!lWr`NsZNXmcO&jr}$42S&?%EV0mYc2s?1-!0-B`)-MQyGs8X`+eFs_xl1jT8sbFWxl6L{@OS96N8tVN<Y;5P5QH=^pEz<eMxUZtoX+MruNPK%~0Jsa{oV^B=w3*KH4|;PXmjp$oy}Ap7;I+w%a%NVXadYdG7oy?e~}Yul-c}xz{StpT>SMe((<W;r{jPDBs*i#y9to6N|<$pQHD$wQufUdyf`medkB1_duRU5#QJ!Pb`pK+A;RowQugThZ3?$J2QWfdf%6{-M+bx?;Deu>o@xM1KKx#KM<*J{C*(f8^0e2y=qCG#_t)lZ~mUaiu>!Nb6n&171}p{U!i^T_Z8YVe_!E`-M_}EXY9*p-`tlmeZ4QEeRE$%`{urk_RW13Ux(0JPJYI^tM<)x)KKTjYn^<I^-OQ~-i~jsLnii^;P~b`r1s5qNbQ^JkdgYvI;8f^b;wA4V;wS*kFgFJsc)<+hWs}i-&|MJzPYYw`nrB_nP*2@?P%X@$Mki5UrOB_Y4xY}&HmKB*`Ja6Mt^GG?9WJjqdz1082uTkZ}ewkA)nMY*1f$w`#Qe4-X6F)Ye!o1Q~T!pw6^5mnb!5C{Z#v&h9BAY#80*FiJxlU6W_eP0-kMG(;9c}o8xZ!k#+26+9szp?%FrUUHj&^N9r5nu6=XdBlV4OkK|*Fd!)Xxo*&7_SkI5tH|B}&-iyg;%@ggL`y-~W_eZpE-j{+^4<)BH-?VS;?`YrL--*;W?uWke6;jfgx7s)Nvr_r&XK6pxe%32@ucbB5wQtUI)7SG{`{q2?zB$h$$2Io%O<(WtYd`9`h>Q9a=2uHIS3gtIvQ)`p<+ld+bNvKUnd+a8Y5xRsXs!RRpJ3K`y88e1CzxwImbE-wW)r8uv*C%vSK*29T1(;vOZcsDSsyMFJQ62+gjG>Ii#QdY1+OM9gIB|Ah|6Jhj13%T1IK!c@+LW`xEfaNtmHT<PIn!5I(ex$)|IDX)t-uP(zZJGD)L%ITZ-Qyk4f}_>WfJf#Z!pW;3@D@;&ON`IjeqEah$84$1x5n&Tx&(4EkgSIjteD6`Yfb0eCt*mN*6;3#;=~aTWd7J6sloOE2PlxKFq&<nIglo8lGWvMyYf6BFQ-;gZPT6ZxCsCB((V<?vEIvxKPYE+Eb)E`}HKnFT~$H&OMe8Xw}@@H#cN9{KxQ{7vyj;wIud@CH7!k*Mo#A#NpZf;aP-Eks>c_3PX8?c4Ovo0J5`K7syOO;Nmtm<W#ww-xV^^Hy=G^<N&1R&k~EUw#FxVj}&zm7KQ`-*xdjXcgDH_-(X`3Gn=Ina6q0<D50mMbD-0G|xfLVGI<{XH4f2-*EAAw2I4IoPbWCPZjs%b0a(wU-Ag6qIfZJKD-#-#rW-Eyj0u`Z-F-xcfq^(tm3`&-xA^icnLg`I0_yK_hC#Ia&7fuUiT!<gU5U1`d`DnVKwt%1$`JG&Vd8)7~;$D7+B3m6;;1E*F0moiug9X3SLQE3$KJ%5Z{9L(2skG+u$|K;qlBtH5bQI6wf5S2G4}wBqqSa!ewZ<EF!)RFM@Ya6mJig_lOILufq%BA;h8Z5V)%)MR7OcFjy7E-NUhmC2=@f`NJuS-ykl6-+*@#cffm@D?2GmsJn!@qCY#5wtH~QKE#o*nv=UZ@Au&C#69qKSRZ=_$KQdkxF^?;?uQZdjf#t1eYKdre2=(`xESuk^PvZ&H~rO{x!#@9i+=4&>`Ckew+@#&;qnaJ7Omo3xDH$|TxO_iKU{WD6dxrHfsevhiT&ZL@NHrod>j6i*b@E~_IM;VfK^ePhgc6*MR7jjTv)|TuquiR5&sSUKvep@aM@~!r{d4>&qiIP3x?yz;dnV*MpG0IBi@6D!Os)3dW4^ceZ&f|DvF;XHicDD{3P*tSQW*2h<;cV#ZM3i!>TAwM;r*NqSzw#fz?07nTVZXRTSqY`e0QQ7blj3RZ(1p_ynwq;>N_UEn!s@KS#U-KL-yb{tF%oj|!Kc7#}rGb1a$Pvxv{Yv*1O<y6_@+Gwp1qEmaifCDw&itPiWAI5)8ctcqfb*b!Dm@h^D&;9uZd#24XP@D<`n_zD~(PKSf=_Hfx4F0X~lBVrr)5&S(x@ivO$EyPyv7WhBJ+3<hhABi(z6<>#cgx{ra-*xr#kLWp!&1~XKSY69)$-ON(y~dc%A(uJSZAG2d)N75WSpCaH_p6v0R`;}BmfYu547hj?TE(d@-iKE4RTsaHR&kPx51>_i*~N#@Do$|mVYG_lTzmwr;uyG+NA68(o+_@4t_@d$pFuZ=Yr`$jZQ<r{JM;^1TevG)aSybLJ>mXv4|o825ZoVr5uG7?4(S;S#Tn7r;0$nfbWS)MoC{qL&IuPn7ljML#n7eUqHq~>CAc(P8T|}g39f_wC|o`amw4h>_#pftJRYt11GI`0UA!Ny;wvuRi&k;6i+7_{oZ{l0Xcecqcsp9f>2PnxqMt{20J=Ne8}5nj1b2tKqT9fo;CASSa2vP<`f0c!{0zDj{4`t{oewSr7eaR=_bza6wBq*Y_T;O$72F=~gl-JCg4>{L!j0jE=%?VC@YCpG@KbOpbRM`EoDW@}+?&B2(TeM$>yoeHI&fXM6}lQ+2X2fm4OfF}qKm+#;iu3!;39A_v<J=s=Rubx_lj_RbPQY;u8V#Wj)Ci-3&2mp)zG=%0&r<`W;hpI1pT)qoEgr+-xU9fR?)+`WDA#!<e!mz6{m+Y!ZGN_mT-FbN&faHtUSd9IG5jH<tfg^xqJsJPjP0><pHcb#ebu3!^*qOxhVaWCFk%hoRM?-0#=^l^qk8bSb2&cqi@2>yU95y{TX}{{vCZC{tW&OodREnAE2+oDe!IdMN4x36#fc*0lo--fj$pkfbXEs!sp?eXvL?|r^#3GN%%B;9eo@=38$cs!pGsO=)>fG1ipwq1RsVkpbx-@;PdGB;REnl^gj4~_%vGa9`qjaRlEz{10P54fOo-1(dv2J*CWql#l6ry;Qnwo^b2qgI1a72En3CaaC5jV+yGr0ZVp#RSAuK9CDDotqE*ZbtDK%AXT=@R-QZsEv*<Xu8{87z8jgb-p&P)h;Tq@$<W+-M#l<DjDi($F!X@F{Xq8hFa#maq{Vd!8jzzbGpM`6o8^JB%s^}VUBiM_s0@r{Gql>~-;Oyw!a8cMotDMS{v*I%7ShyZs0$mG^g^Q!B!nNT1XfIq9&WZMtS59IkI6GVz{>u_=!P#N;T}x?|Qx<YooB>?|E(51S7l%v0|5&2)!^Po0EYUgP{N(qWB{~zFlYAdqqE${0`Mcu#=wIN!;9F>w(>IpntoTbybUHW#`QEietDNrgcf}#}Kjal6eh&Wz{{i1XKZJjSuc7b558-6=E%-is1+8+j$ysp{`b+XkB7WlH5L(4^@aJ#{K7;<8yv`6$!Pnp$@CkG>d<{N^PA2DL#2~D4`iPtre~A7BPJ$1j&%vL-AE3{`=ivS5Q}7vhFZu+03f_%A2A_a;qJ!`;csp8sr^;f<cP_<Q(b?gQa1L}XI6IsVT?ozv7e*I@3&CD=8Mqi+9$gtO16N1afh)uH&?=|A<g7S9ItQE;E`ZJl=YWf#3&Z)~7_=8I43|TD$*UZ(B3vCV57$E1gR8?0&?=`A<gB<Px&WLXE`=^YUZsd-;TX6GTmc<JUKNN>!xiCjaBXxgxFXyL-2koyw?wO)s*<zfYUomMNw@~O6nWJk)`Tm-W#L%#({Kg2A-XpFG~5*32(Ar3i*5-wg5%ICrzYgAxEZ<zTn%oHt_jzG+o5COns9q`LpT=hfNlymggc?1g`2{i(Q)vzaDTMQsS7zPegWMaZU*;7w}YF*esp`d9XtTt0d5ZuM0bKaz=P18;ZE>ibbq)rJOr(B8cxoNN1)@{dD7)i|Nr`5asBt7+Mlzc{>NPAC!>Ep;{N2Ea9fcdlf<>lsMZCobm9NhqW(P96W0F#L;FN@'

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
