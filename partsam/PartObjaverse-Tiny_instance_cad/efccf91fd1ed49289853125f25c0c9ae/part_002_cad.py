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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/efccf91fd1ed49289853125f25c0c9ae/part_002.stl', 'relative_path': 'efccf91fd1ed49289853125f25c0c9ae/part_002.stl', 'source_sha256': 'fcd6be6717351c923d3a28867e4fab7dea6bf9cd61b152484fcaabd10534e62f', 'input_faces': 794, 'input_vertices': 561, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0505923368036747, -0.011220309883356094, -0.45324403047561646], [0.050610098987817764, 0.23848965764045715, 0.30101311206817627]]}
GEOMETRY_BASE85 = 'c$}r23z$vi{>RrIhQ=+IaUH|vm@$MyC3KRVs3R#Ql@uFIj^xs~RTH*cM@L~&B#e%0hstG`8DuL8A(JGxnv&DeNs@!3QvdzF>+>#q{nqL{|L6brJn!@U%xB(t_q*QpuKU`$cP&*q*|PsNu-;zx%iLP6ElZUOR<boZGi&6a0huFO3?2S-z^bgh`e!otuAbex_X=2}t?b5+W{wz;)%eC><C`99+qhY<@ngfXMrQRJ+ILviqnXOz*6)cCnK3`&Fa3sR#(vIdeM75e!Rwkd3yux`AODq$bs^aPo0VH*8ELe4Q-@fV^jw&~HO_}x?s~`1hZp`B_4AP>&%NvCt>rD=Q$BPqaNN&Z$NL=et-t@;Ph9<Z>xLbE?KqzL;kIwBP+79PkKO*cQ^$NgpDTT2{~fM&B5#)2;n$Awrhc$--zB=8v?iNf;~;$G(fv6c;(TP)l<o2Lqcu9@>H4+K7U<7CIq<Nbm-R!7S8cP$=Re2deRT1j|LSG?#>@7db{<Gx=G#uEI~V);VCGfx;=NVy#0P%;iEN&^)6WODM0fi2(|FlW<7Gdcc4R-dFWl`r4tUdkq(&Rtul;hd@_BuBec<P<Q2nT%FX>uiUA)gbxcCj_qn{o*=;y7h{5`&2v~Rp@KYFS18eRX3vxnk+IJIKYfAg|GPJPiI$BX_LZ~7BT8v2So&wrYt`*ot`;dpQLII&RG5BL9Yr?0=aXuY2=>2c@Mcpu(Zyh8W?vpYZa^TDibd*Xfcn$=r$|9`mln4kZ>`m&#n7yUHe^fP>ENUolT%?h=To@sC_-sjElsQ0VZxgYKRTzbT=U;X?>-Ttj-^zWq)-PeAHpO5SqU+nAm+<HLI-;0-L>(8l@=xSej)4uekeUBII=hZq@;MczKvVG%a`;Mpm@VV2o^t`HAdqaHt(wp|BH|=}8Xg{xRaiL%P#>@7Nm+d>A_DjC&Hq&o?c|7%l-=%7wSFUq@e1D`j{gK|Z@A0zz`b&#^+sAv_$9vj0p7tY$etuDJzg3&Kme=D&{a~$a1%CA%PyOgeDKF^lu2QCJ{d&BpA5NKE=vUwI)DP{=o}uUYCsX$6?Udt%^x@mqY}5VQ(ffHl4rO!JyT(&^XFP>>##4H;zVMNT{WkfvZ@g^Zc-g+=&G@{RqJ6N!8rS^scv0V~*RIH~zT?gOfA{G0_<3$USpR+9pKZOh4_EEx>!URn6vX?IqNCGv`;}L3@bjTM?F-|5Xno35<x7&PyOzu2&3ea2f`^Oz>O0=7mo>fhan9^doc`m@e!zHZ&7Y>Yw)gi7i+%lvNp^qU+%#GDv+5vMeUBIQLp3K9_|<nj^~2TXYM-~|g56Ha@nSz83jX6`J<hAMwYL&auZy3D(wliGy|dqw-pmtxDDCnlzxIun?He!Kcf8rptZ$=zxa~04@=9-(*LW+GUEo*WcvC;TGJBHtRZeb*AAgTG<Bt#4PAv4R?|AA*BEL@5?G&Eg;OdX?PXF<tt-lob)i>VM5B=@u=k$6nKPTU{9T{J*XHmS5EY8-xq|zYQ@_M}KKR%Q)q0q0s<EdY=C`J27*;%grq{o~2gO4`swaKr(<Ed|r`EG)4r{gHscuH@^$M}-gqYC}%8}E$&qN5Yyw`*truyDTi;cAn8eY8fVYrhwnmmSglsZx8RpAXe4cGZtI8#7+FU-5E&{5X3&<7|Ai?&(6m`i?jInXS3w^zt4l?;1Dhoq2^1FZjIBufFl7eqQ>;v3lIfHF3>D#|O8$=3y{>qxPXvV_o|t>7C=F@Xqm3db6L$hbtFu@cUe=PU}KHUy?p#vtNIVm;Etb_Q&yN-tL;2t+z+^&v|uD*!#n}W3uDtTlD@f?epy$E$yQN7rE*iAF156Al_SbFFvD}D|xZ29pl3_x)sFxlC9&O*6k;Eb@vA!8L-IJezf`+?aguDv}3$E?mPXj)<*lhO8s2pZ+s*r$36blE<UCEU#6A&{7QPWe(|A3g`529JKmiCRNbh3wER-{_9ea9zVMNHos0bHJKh`@I$a*4*Zb6s`SII}^v-byAO7LmBER~^JNvN;7f0)PQYGMCzj$-~Wqc&#nD)`#zio(LkH$w<f9qPm;e;_Gb^WW3ua93Z#zz`d+2mS}zg-xiy*Q6DUY<vV4?Jc2oGq^Y7$5z<S)pq_UmmT!RoSlZEH6G-r+Hz#51qR(T#s|POxODLc(XsmhwD!+@~iK7>RZQ0X&=39lxzJ;@2oF;q}8Y*zxu|T`q9YBp?colH`O&h##@aBxW*@Rc!>7Fgx0S8r}WPK2jQLbWa-U$H9m6nWY_o`AFY#F=;wnO`I~+FgZK0Y@9B^6<~(7~kimK!DxP#5UyKi?Cc2I<B|C-;(&L$U-hCb`y=fnBrJdj8SKslbeuq$|9*3rnxYn2Pk!~~G>ucTVNA)}`yVA9N86T<ih<lvzp_CbgzP{ltuI<rUHl&}Px8>Tq=D)|A`HU~Azq-h;zT>GM+`B2PKR0-nYyL}b=CkqEgRd3&)i>VRAGSK$TlcfV4%hlMKAM{5TEBU<j`mbOuTp2%xH&#$scYP<ZG*KBR_p9qU&e<rm%7$h-m}}zzoR}sxua`&rFYJM@S$=yZSZTy8v3Sh`y~Tb6#2Dpywm=Vi@v&9El(iTwY^L4+^-YfxnC!}xgUtP62J7V?|4x^T6UgmJ{un@*W5J^J)U`Ge7HhkzHd8~+Pl{;z9eOJp`VYYwkq;##|myK^6QV|Wq%spv&pwVX-S*?#>equd?FcpUHe1n<@z#Sw(oe;{>y1SJNV6i<K_GxF;08W{Kw1rA6k?4u<p0m9*vjVqm{lRY|mHs{y}=@_=uPL2kD*r7$;}<)BO?qH;*^hp?JA}^LVp=J6APRd$E5uUhbcbm-}bO%l-2!U9^|S3*+VSBAS>xNVg-7UmkDHZ}IZ@<?*I|h1|i~i{q*B@^~7mRc)yD@_a*h=lCwXb9|THoNpK}&mV;Mv@g#eq&L?KwR5$X=QGC3^O?NEYlqsO=RO}ZUY?KTO?zgz{(EtLD7~{k$IJ6W>7DEG+@vS<{FLXn(wp;JyyyH@db7QZ8#_XOzBoTO-gADwAV+)8`8i&mp9dH1(%y656)&$BLa*nH)PFCoM~s)(Bf(EfM(g_GddGNqy<@FP8l!(Nucz?xdMf%u;3+*G;`&Z{=X@S7ukWOH=EK@u+RN)xk2l9Dyu3d3c(Z?7m-Mt=K6!mDz1d#yp6hGr&Gwt$MSFR@Z@j$Tj|`ruy}bWmyyyNyevbB@`ww_|{~`EI>1_S8xPM~2=l;p&B<(%-Pw?{oNpy3L_VT_>WaJ#}<$a#K9XVt5c!>L5(mUq^!aL^!(wp-Eyu5!Uy=-6Jzw&r9AKu@ky}Z9?yyrd}-gBSLv?J~ZMjxL$PJgbrKPkPlec|Q(N$H*Yy8Cj*YcKAvdc3*sjhFXVJ>JwmH7TM~-tWcB`@JQnCr!|wEAA&7@426R=IaUZ^Uc}5_I|IuydN&Ta~#3T`{B|%=UrzSJ*Vr*`}xwF>tej;e!lePIsVy6+RNt=9&hfm;pOuPk2m|hf0v%9=e2k~;&}0VB=o5@N&hUK*GTV-Ctg0Uk>0t^y)?;gM?P<o-YhTP^SnuVbKEa?<7EAN@w`lWr~i2Qyi9s$K3tw;d-*(3c;|Va@XmaY-pn7o=Xs*=vVG6<MCr|bY|yLP%jc)kJLB`~cI`dSbEP-qkM}&!mEN3pS)HfopT&8R@$$K|$BTA6&#y}-PSw8`&(l5LJg30R=jk4AjyvUcOw+#?&-aa&&-a5>GN<eHD&HT#d)^<YdUAUF@;ddC)1KEU-hc3Tv)=LY{RfXX&z-AhYA@dpk>1Qh>7Dmsq!;bW_d}$Y?aTK=Jl?FA)X6jS-;4KQq&M%w<ke4mL65(9KgZ)u`*`_&j>ntp&D?~Ux*y{GB99mK<@-e*Z;m4`HJoYBJNNrn(mU^i3GciQCcSK5yniLVr+xAMmB*X;Ip^M)uI<{)PwCD4ng7)+o#OpE>7Dr_yfc5K7wyaU>!g?M%lGR%-prpx3Ay_3<@=4oJLjvyJM&F?(Z1*XM&V`qp7$H2H`hCh`{%~57w3M3@Xq}T;hp;x(mU;E*<QSlYP{!t)HPYJ=%3~Ly3(8XV1;+y*Ts9@*A?D*{}%6gUsw3wt1tWMd0$s})6dA`?eesj?|TdHy#Fk`^FB7-^S-z6&imEUi}pS5dz;Ud?|b9r_XwnS-fzcy-VYaE_TTe<xb&j`^8Ik*<@Xny<r3dtkX|mA{QiQc9ljUfX@~CxNN>KsV7&bPg7NbE3&zXuFGw%@DZjtqX-D=`e1AcD)4uiWtR?zq@%<F(&G%D`m)}nb&N{VHd-=T~yytsEc+dBSOgr)48|v=*R#nD=CtDSy#YQ|<lB{Iwv3_x1sZvs}4$}WCRfDeoUwx&jO}p#=zh9{u8i*}>tlU6RoJ!V#Q{e>iKbFl2@K=_dyWy|kedGdoAN&S63Vs8gM?L}1gI^^3z%RmM$%o*va5mW;&W6X655wc(S!5WV1<xmk!t>!(<QRAryq{bI?}xu8_rPDnr2}^U1grc*z~*kTa!sr>rYQc|vh%!Uvnq=Bl3U=ta2`1w&V!#K2g6Un!^mFnFt{IiH{1_?guESo1ipvt0N(@mCU1p%!+puFa9?-`*%KZDk0uAgqv3_*6nG*0A-NI$5WYm7fiJ-+0Xu64Y*t0_Eo2w?7I+vr0UidwMy`ingSV3h;O+2U@+7<$K1!Z}kHTM&7vV49f04hz|AN0He}=z=kCW%%<M2o1DflD!eew|eKD>}DfEU6~l9S;l;akaWa5v_<;-;~3XRLIjC>~Buf``Kk$c^v<cnA3@yaV1x{uAB@A0vN+kHID6PjCtRE%___E&Mro0sb65LVgb)f%lMK!+YTO$dBRo;Q8b_cs@LojKD+T5cy{~1lJ*J!F6D@FIV}!WwR=Zcat07-S7f(GQ0pDMLq_Pf}bGogP(x=kaxg+;D^YL@I!ES@@BX@{4jYN{4g9Q?}EedQ1U@|C_ILI93BHNB6HwH@E&qAya)b?{5Sj)oF1@K&GmHVd`EaptYpW^9E#$X$!Fo0;g`r~;FsXp<Y;&{Je7PDo(gA?55rk-AM!4^58R3T6Wj@INj8I9!u81@Tpun+R)EXF7c4t}vusvH@iFoT_!zvCEP;2z1>~o20lb2IA6@}3Bj1IW!Ar@l@KSg=`5wF+UP*ocuY?Q9LvSIyi~JJa1s^BR!pGr@q!qCFB3wRTXGOR?+>mSlH-uY}&EZyXXYwYvGu)TF8}18_ARmE8z|+V~cp98bj)BK8*A*AX%86L{8%6O}@-(~^{(w9We*o_yFT=aw56MgLhwyIlEW8`uNqz(Ggx@6(!tcUM$PMrkIES1F=fM5Qu5drNJ=p|q52ummESuBd0J#ZPMe$MGH25gIjvNH9gXfYDz;oee$Zqg6@JO;VJQB_#+rwG#aPk&-IQ%5p1%479LH2-0z)zEz@YC=s<RthNcrBR^uZ540r{N>;uVl@D&A-BR19sjH*M)B+$HO<mVR9`ThNqCla4~aTvD#)E2Cl5%hOB>;t>WfGE9Q&J&T;dnGxJMj-?;hKm-(o2MBMxw!TeP@Ep9$fW4^1*jhp|uY#%D;#BDEg*q&6r9JsQ5Dc(iC6u7cID*k|+9k{anD&9&?4P4pYr!qz=vjSK44_S<x%0BQEI81hm8~;wMAC)cR)>li`r^@<q>$g60KxMhWmHD9f2zeoH{#;;wsXP`p-;OaKRql+NpF5eqDhuM~a{=>R<%+oZzk=;U<+8Z#Wf|L(%B6AJ*HX4WmCNI{$K`CVDp$sBzbo0kRTjo=?}h9SRPM5_>>m`bBad5G_9u#uk{7Kj`ya(>|D;mQ^#F4|4bF&_A1!-7*92DkHkC#2Id~H}72X6-BmV+Vg9nlK!-L=l$UET&;BI6mxEtJ=yb10Mw<kkzd-xXe&+sj97xG@X3*3Wz6z&0Mk`v)fcoMlDo&@KU-@*CtX|hJZ=F_m+x2e1ht_j~xj)QN9$CGQ|@$g!5KfD$$CclD<;S=O{@Co=d`EU3%e4hLTJ`Z0e{{vr!FOfgMm*BJHKj5?QH{>VqH}F9+A3g|gAfJObz!S+k;E8ZoG6T+Ft}AX7u<r%6Biq95;9lf|a4&cW`2;)!o<+`tXTh(Ni{aPdRpj5{Rq#9H7Wf@_8ySVS!JElV@Mic8awYr*oJTH#^WYcB7vLA+!Q|ucVE6&@e)s{n4S56H2Che@!u8-%WCC0YK4ICZ?scA^DE^4t2Y&?roqPlSJNzm+4}KM%NxlfrgvXI%;c@V@WH$UP93jWU5qLH^3!V+XM$U&{gIANQ;MH)kWzSDFUrUpTaA{cG?^Joxx^n+h@qV%xE~ZVz>RMP`8>{=B*TCu?r^?Ond3Xz%18;$+laIsG;lbpC@L;$Xc^BLZzMH%az8k)sycxb7?m%{gJHWS+cfhy8UCI04u5eHCF}No@kemz;gr|@j;3@D%@_TqAe1=r_dd~2(Vs(#G<)7i&a2GNHcY!C6>);9Sdh%m<J$!)t8a@D@B)^AG!e__}@EQ0b`73-8{*C+z{tf<_{1N^cK1co&J_ny7KZQ@hhscfaA-I5?1Q)=Q$vff6a5u6k+?2Vlcx<dZ9V<_fqu{6Dk>mh)B;23u4fls1BJY78g1eI);O_9v<R9Ui;TB{yxCLC5yc(_wS0XQ4HdlgwvF!X8{0sao`33wf{5g3T{v7^{+yQ?EZzs3G+u<lhvHCt)^;mzBW2H5DJ=_}ZN!|zdga?s-fd|1e$iKof;8)3c@T>3&ayh&Lew%y?ej6?#3*jR8O>#B-CcKPX3NM4_lCQvX;pfTe@bmCM@-cWI+=ILq?g3v%UJG9bS0O9IRp7E@8MrL`jb-OQESptPe1QBIJ^;T(z6rktzfLZOUx!~JbK#fZzmm_xe}$hTC&16aFOW0f7vPu4Iq=Ky67p~G5_k>yHoOKtXxZ~q&DX2QB={=$pO&4cESptP{0VswK1iF2{}d}X#!4W;PAkFYKgRI7SZPgBd;@tsd;{EuYzeo4+mfx|ws1T0TDVMt{r8FFb#QAwqilj*6kkQQfmKnQM7D)hQCyB}2dkpEe1cs{;Z!ChT&a^l8)f;7M2g}vWD=Z2{W7$p+ASR`>9Nmg7Axvef74iL5-Zn`X>b~K6t{?#=CP7NHik3cMij+=h?Rz9I@uUbhntbj;c5x?XV)N`!j<Xk)npo6f!|dmtH2fEN)*LaW2FvRo2&xYhHH_PVfEQH6YPFfgRdrQ!L_KbxCLWThtE=6l|HC!#LpRwlj^@3qsnAD+?4UIK_3*?B%8siD6T~x6xXH?>a&}Zwc*;-QJk!nGnOf2H8^Og*F$2*WO4vpNBvE#)TJn{uKtGK1<AT_5N<$GoJv-QYsE@^wJc;kxF%eKOodbVTg6q$Dr9xI3S5m$hHLYA4HE34I2g-%u~I+5ZbKEtHOU|xq`u;e82^EBQklZCnm(!aR92_$Cb4ojV2^>y0gOimZG0B6vp<}cU@vESf;}dU6YMcinGUB@ryhN1NIz6jT!*X+>-Cbr`b)6ab296@8e^p9Lv`jtb(WzDed<r&`!gRDtD=_eGcp5Kf1Av*r;}-nSq6P=2sa{|z)h&zh@!`WtOwVl{Z!g%#Bw&m)up7eoT=1T+<-aMgz-z`Gp|wGZtUl#WF=S?#m&gdaLZWvW2}_2?4me<YyqpHI6yXsRjPlA)&CWp6f22jX}CPUD?=v2s!j#!sVoau<ZrGb%fQ{c1`?7>{oa42edV9JF0x$zv9|n6_v>Que|dkbE$8L2?p+hrXU7&k!G18J-k!1k2W_5?bN'

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
