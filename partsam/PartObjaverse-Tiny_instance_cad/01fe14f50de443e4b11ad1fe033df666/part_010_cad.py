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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_010.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_010.stl', 'source_sha256': '4443374809ff68e9324ee526c21e52cec117a3550b0eda1e197cbbe29bfcfff9', 'input_faces': 840, 'input_vertices': 485, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4114878177642822, -0.293452650308609, -0.1439521163702011], [-0.29416072368621826, -0.11316424608230591, 0.3287442922592163]]}
GEOMETRY_BASE85 = 'c$}r22b2`mwuY-gRDueM3L?^&5CH>ORBRPc1Qfj@3J6UYas~;a(twh|Kro=#Ac9C1BWZdD1X04k43eb{SGXdWP|@qX_tl>IcD<@S{nmQxy>Xqj|MUHan!T$|ol3K8-J<vz<sI**s<WupUFA;KavW)8obt}FtieNjb<G-bUH^e2BTm^uE<YM)+}oyA>qjEaFlSV?ZdpUR4zAWHTJ4tZ4Xf3RR_i`s@X*1X`*#{JxLcO+W}W*E$#VISo}C9~x&3SEHmp}OTBmx==#$a^<4-BcVON_2*=|Ul*s@z<bbsxJw*`0t9^bw+7349vbMno+Aa|0#<Vj4g4sR#*y2oQ?JIej-%x+c4(|M6?g?t3tfhXWm-3~kkPoD^HCwjWXXNBA8AKp&tcaPicB;dN8=$LY${gZlo=A`TlJhtcJDZ%l&-<<q&H)P`R8z0CGa({o0ShzDIPmb6X<hq}orQv*hUJ%YF&3;br4(H<^7n6_j^zd*#Nj+ZVlR921bi87Vew&z`fv0wioE#jV)bTSe-w@<_d{eFO&JA)szR`zQ?hNuMJh@^>C?7rU36qb{O+IOz4<;X-CpI6QCpMorT=Pk^JGQ^Df7gjm3*)aZq_P7%26y^-^HX`cna6d0`rCo){EYYAQ^-@#PxFq~5^p=olW;xnlqcYN-ub+C9q+t*JiMJKJZiR+zOhc|yi1(g?Tvq{Tex0$Y7x8#^}^$Dzh2!A+&>@Zei+)HsZ$^1WCwTx9{v8{h9KAd9Lt(MCL^C(Zd`Et4m>{RyzC&?<C5IAD<_nX9<Tlv<YnT?ehmxfLvs7#(D6zvt(?ft#IIdDCe!$2k4D)+uE#f?vnD6V{o{M;vb>D^Sj|vA{&8O(&d2A~!}-ME36qb`lbFfJpC`YB^YQsnFP}u4MWOi<Yw~*G@m21?<E_rg4sw5972iEN6Hh%geoS!t3AppGSay)>Jd6+fASaX$Jh8b-UM3#B(91t{-BaH0U3PeDVg6mbd9FMT*Lkiy3fFm_D$&*B%RQbr*r;$nSf0A<^Xwqk-y5GXa!4kgJTiJ%aQm81?C2S(Ox#)hU`{9>&GXOu^D^;N`VWs^*wLGxdSCI&cQdmy@rg@k1;^|4F%d7mE)#c}KD05&_4*j=Hh)JZo?iUtt{~UzW76c~^9kX6^tu^0`S{nzCgFUPM@>F@-PC-NueJBK&-E+Oq(@;smdA_NpA{VMUpHG`xh}}{y6Nm}x-rQ0x|yuIYDbXkbu-of=TJU+eN38sl*ddy{&myjqt{KFk6t%zK6>5Md}3{H39a+#68&<s1KeNdKOM9_$aOtWJa%MiCLVja%k<#({dIoio9lzzU*`{x&kf}Rk9{_1XOJg!{r~NS!u;bi>xb6uSjkr>XJ_C}-6~TvjZc4jVttV7I-iPk&JA*ZJufzUXGVT75z0r`^HiyDKFSld!};hspECLAI-fN8`0IHjoKH&m0WY6qPQB1NA3bts;qg`Ouk#mgS|8-Pp2yB^H8~ScT$eW`xP4vcV^5q~ALP2ur{8}xH<XXA=Rd!)Gsqpij&ym-+n;?Zh1Ox`+4+U*vvNn*=MT=z4s!pxP@-WXBfrMG&MHsnx_xPb>>$_mIoW+(PADI}zEt(Dvz8~;)GEy1X}@t_ru>!L{FU4Mi*WK+Zu3`e^Y`;H`CG2}r_NZsFVp-{Zs(73JAW+K`J>#<ALVxb`1zRm<L6`Mk5l`teZlix*9XgWeXv~D2jzBsP;S?UBAoTX=VpDdT-OKXc70H8*9YZxeemlt>qB(Fe6KFE{wufZzjC|&TdwQBa=ZR3x9h*3k6Hiye9Zcvx@MfW9dmuRT(9rS?e$%`y}m2A*LUUi`tEaceYZSj^0C)<<@WmS=V`9*%I)<%xiaC^Ywiz=aPAM4+xtVy_5M(~y+5?vzaN9!`@<r9LO36Lf2iEvA6gzY`PlozcxqH=eb)Pb%k}<WxxN3lT<`yt+xvgZ_5R=gz2^Ska=rggyciGV>Awen+vg+Y_W8))j(t8F*dVn2>vN)V`<$rUJ||kP&xy+IbE0zloapCco)azipA%2l4Xx+;9-s*4J%Hu<9zeN$51`z>2Pndih4ZoR0gCYI;e70S0Oj^QfO7jDpa|zZK)lUWq4i(i^C-9Pd6e7tJViL~d6e7tJj(5R9zP%Rp2u>1&y(I&Iy66Z{wufd!IazgVE%T@d$80aCBydvy!TUX-}@=I@BMsk-uo%H@BNh9_kQU<zwHekFTY;6eb1@fzUTC}W8QNn59E8}&3k6c^*yt4`<_|3eb21izGqf$-!uE%yk{=LO+NNLvvT{M+0WCwXI5_CGdoSUd-a;{6qf6E3gz}Yh2{F4Lb?4;QH1kdK)L-+QG^$S^ReG4l-utVmg{#4zh3j5B7Vd3p?RX;m6Y4>O3LkbCFS<Jl5+c9$=|;Dt`z@uV(7T&cQ@tsyPI<R-A%du?xx&+ceC8z&dG9n3i;-7h39SRx6}E;W3!7Fa_6#oIT`tp1=&IFTzjyfF#j=oax!t<eyn2aj67N}uOP^s3f(pYx0CF*vmlsHbjHIOdA!}r1tCtJMaIK*e5_!3IRDZE^E2^eqcNfJex7E$avh&;GN+Ko-l>}#tV_9b_nh@X9)Dm|Xnf+(tc*NewnIUX>vrsT<^K4tUA*lq8R>0*Gx?Nk8{+APpJe3G2dftZxzpzKx*&JfwD86sZ5ygrxgPiQmZQ5f@x)c7_5^vNWv9^oNmjorbljcYr*>!JiJ^ZLggD2&$auJpPi$@!%0In*Q+_5MuTm>C-k&EwR?5%BQ-AFVjrZq?8Sl?4GhX+D%}2TB<6PM=e7th!<!9otzO6&!^*AbzJ$H3zzUg^nxqlwPb-vm0%Kh_n>p9{5d2m5~ChnZyDm31&*Nj)L<I|(cc=PJ-uWc;cZ#oY<l@9HP)csR4^Fvt$L9Y8pd2~W4k3Y65w0-6AhbD)A@8UBGd9r72My`3r-upH)Z&<n@$kSa$hJSDS;-P$^#gAp=iSJ4l1i9vE$1B(I>4lEBofB7VDy)NbBQ@wh`N6sp-yhG&oyeI5L9Y4R@yd04wCca}gTFUA^T+&5Jobm<&BN>eD&(=f+d}(CdHhuW5KqqdBQ!qs=}#GX`f_jk%5^(-yuW?MCvN;blxJ$9SFh#HLa*M$mY==-Ft>7OKP$KEwsM`HKJVf2WGXLIuX3#`di@U>d16Dcg3xw2jygY!aOS6Soo~)lU*>1xi2-Fp<8_|LCmqSp$h(~%8n5%yZr`7`X8Ss?Z2mqs`Rj4C`$xImKdDlEGVbTp8(l-!L4QA#ZWX$&B_2JQd7c=q^Cb4w@r?7<a-E0D?Yy;I$ERLDmhn7NZqK81zoQw?Q_J-{jh^vs#&yGTe;t6^b;EKUA3OF<==b{T)g@nr=Ao{8mg~Bw+^&<B`|ISkbSQs+|G@1!UxYIcmD_bbb@D(cPs{CfCoz40Xx-53T@lW8O}V|^Ie+d8<>_B{O6>KvW3J<t>vdVVy^dS1<5P_{c-t}eA(rcXg>rizV!4h_Y+V}K4|>03x!xBk_wRenczYj}T=8~jKj{6N<$C|7+}=-GuJ?z^?fs<XcD%ixv|RIvwVdm1$J}pQuJ_MAH}~6?>-hBAmqYu(e?EfS=LO64c|o~-UPymEEp#0H=NiNP=Nh;kM?2m=?<8xC%XnQ@UgWxbMeoqO)#o+K^?6OXeZI3?$2*gohqmKCf5GkZW^!Kr@Vw%A)^dHGRc@buE!Xjh&KHK}iJp&^`{$!_^ZahPj!(BJ70zFeJKVm1uw36iD7Wt)QVqY{9n7-`H}69d6Y_Tlw_nIxhyH4OM6AK2bT#)^x~-&B-s#>s@F(K}<ws-YKN;^;_kZ;#;|=TH@c;dj@ed>JEtcE1(M0d0iQY~V{Si&{Qkv*4G|>+c??kt8+mmkVOcT9?Ci(-K=+9`PchE$CN)!D)P4wF|(Q%sS2Wg^jr-_cyMBhPdgC63xC*0PLCVDVU^y4(q&(lP|OcVV&P4p`?(J#<Mk0K61-{rQO-S#))ZRiKw))>Drp6EyL9z{2%ztU~*!r#Rcy&EruewY4Mx9x%N!4sY1wtW12JkjsrtwQJ1@94I6@OF5ssG}pb+=kbYI&OqXya_FJG{kR+cQbXg#&3<+m^wD#Z@_zmI`-l3!+V!HzQq3$Z#Q-9$KQ{)hdQ$Hv+?q&<9_`6@!q3`oA7VKYeyZmU=r)0rH;Dzb@4>sgV!2em%h}o3BC!hHFX@qKZLh|I=;sL8gCzU9L7J4C;DT&Z1iFJQb!AT3%qP<sE1z<Pjn6Xwa_=vzaCZ>U4wp8*gfd$>2HB;LN}#<1a=6$h5k3NuhB>7r(uWD-_ZXA_Axq5zZt9r`V;!~sHFw58CvS736od{Ep^n!uZ<`AZoH=G+VrK4TzD>?=mU61(7E)bj<4Wf;T@rlgZKyWzM+nd_#5%k)X^NjIo>DK(TrN^;5DO;>tGTaprwxb`1SEb--~xQx;}lWV;y`Qp6Ji<4xrc3mpZ<He}Q*^I`-o4#S^_AZzFmyeW~L<_<eXAsiQfyG{BR7Bl_2&Z>4_=tUkICeW{}@ye(dR>UanL9lU#~BM(0hPjms^7wA0tyI_0K1@xtk)$rALd#U4L{D<+@Q^T$Jx8mJL9Zg^oTcM?nmiR648c|1k{PuXaP{(ro<#=tWV-5ZqymzQ$GyZ10JnC4BzZS26I#%GXz}rO~9q>Egt)_-n_^t3n_jH?kW9B@D9z=g2Yy`R|{mHPY=z;WKgUv!uroRaG68bgzb78a5i|9{*O+(M6KL|DwJ%xTZ`aRKo>Gy#RM0cY<5jGj!hrZ-BA3h&X^kTe4==t>DfXziOrauWb1^ov7LF6`tI0@Z}em8Uv`rToD(4FXyhfPFxr~f8wK6*TT$!i&W8J_5ccyFMW(VqaDgkDI$2dpo80{yP^JE42im%Mtxd*O+G8gD$h7yTscP4v_B--0beC+W|FEkwUX{~6c>^gQ~#VLi~#(3iZjU=jzQ`{VUOXVI6u#=^(q^&+o1_;c`{Ca(qf3-Cn0iZ>6vfWG844n7WV9ytxbAAl!%DE%z-aQeew{n10|CtzdI!|2a|%|R#VzX)4^o<V;m>{axO^vA%)p=Z(`4jX_TLtpOc<sSLDh<6`<7y429qF2%vouV&#D}B*9^hK|tFS;ZB=lDGx(Xs~08vZP?C0b&8w8Z6TiEGdjH=`x4MN3?Pme>K^f!`-u)=*i)rboPW^D*>P`l4si7yS}_(X;7`o<@H<+na_S&aoa%9EKjoF&#~ufu6y!8%>;vp2;y9O&pHC(S2r@NB365o6s%Y*3j|%hIpc<xNSK8a6Hj(xa|Y{5AZ~P?Y7_Xf5#L3m)p*ac)rBn8T*afPUD}(6TQG~AL4(ACwi*eM&OUYTR;sr;opQe6)y2%n&_Ft1?ZXRSBc-CUq$aD{)OI$K1BQ)eF(jm_y&3}dJb_4dJcL9u_by2x-IcWbX#<5Vk>kjY7;H*cuKhKV)V82C0-QJjp<*6?n-<T-4(r)xEQ??T{+^#f1ss_zLxkOv^3F|5x+xA6P*Wp8=Z&lMtln04Sg~3HuTf<R}$YwuSEYy{0{vix){IzKj>oQ_XF%7=pWE4h>OuH(Bp_tqQ{||5F4YLplcDYMb|<%CEkW^ihi2-6k5*9(vCOBC0>D+^YU{1%kf0Zc{u=o0G?<$FE`?E#1k#&Wx0swOWep<IWMo|yp>oEE$8L=5zjxLF{0(X+=Rc0F{0(X9O!udK)esB;R^gK@J3L_*)WNf(Nf2y_?P09rjB0tz3?ul#`XB?@di+1Y3h`?p0QF#RqCwDm~zxuhC0jOiIzGxP^ZK)jFmciQ)h3+Y@&wB)L9vCAa&G&)nXo0rj91~P4Ld9j&b<o@Ghms75FRgdQsyK_&?x@uF5%3n)m}_rH&u*B^IM*sbeK|O8gPsn|Zo{xDs8NT6z<oM$39s%<;};iRI9;E|tYEiziyvrAP4}#S<;-(pLPfc%o%px;Wzb61Or|)}?B!Th$m-nRTfG>sAFk(XuXm>Uh4y3XGL?siWih9T}5H4N^-tVn_51ZoArTEr<=!_qeS-etkUAlic<g{$qHe=eg}Y{P*xgf9bYg@qfh={ZH9{5zm+SD`UTM+i&>4;fbE_w)gSh#}hr-ZNu<~;mxOp2KWu|Cc`B@L=*i2aX$J5^ee=#(669BC;k)tIr<>+OY}kX9^yRo9`wt^N$8i+&lB%KKaXxhyaC+?eIKy}x&^g~zSV7Kxa~r8b@~#^2lOrU%cDCJN1;2Tw-Xnkx1%dXym%BXO>}kQztPe}UrIcNmL_@!>@D;TbQj_i=q~6BiMOK1(qB$|3%wkDl6VY#5*^|9{~H}4zZ0;d=o9E=#6{?3=rP1m=rQO!h_|5cK-VNzN7qE(NxT((CweUL3ACJ-^8YDnK&*<E^D>Gb#S<;(Wk39Wc%tRJ%)!sW6D{ZEc@fW-n8VmBIA`Vj6n!3jIWNmbJYE)0w49f@__>S`E$3x_$MgH+y-y8Q@vGtuqmHv+5-Xvlj!W<_!7D`_J@9+rMX7Nu{#v|#)L4=_C9Y+x)Dfl5C}Yl}#!}Q-3Qx4uv5q<=mSU{b(UUrRGA5TADp6-8y#CZt6IPRXP>DM3z`q0UEb178KL+m-YFviD46g?@p1?nWCpyYGP?C6pu~NrLe2EcimO7SGr^J(Jsbeg4j%Ca`YPgd+@5B==>yi7<3eRPU=b>d?Iv4+3Jkhc)wa0IdCtB8}E%;mTM9aE#VZ`$#ZegsfOINdQUCo$EtV<WMZe4^YTGpjc9M6|{5o2Xt>fm^O2gdB62C1bBu><;gw_WA7=EQpFyWLh7zb>BW32qyLKLk(o>uy_(zZy^UFL+1LtLgtK`!C{giN7!=?Y2|+r|?9-i<d;7qCe4XL*Ya5lGIQSzaHL1xWor(qMsus(a)h@BBs$Vp$mwAq6^Rmh)2)|(D}sI(fQ~Xi4)K-qMs$+jeZvWH{$i^zoG9XHb*z7Hqke`t+?ARKwm>&;`ssHi2nKLPQ;PuPUz2wZ=yd#SB!Y^?`UbFuOa>mElu<##Bb5kL~nyFL~ldKiI1b>=nIH9qZ9O(5*MPEqQ578i~b(%@caLTcF6BI?C<E~=q1EA(M!;yi6haY(J^8pbPQdCcn!J+`gY>Y=-bf=;^SyJFH1V!9G6%HE$8KB_?O{{mh-X?ejhy1a$aWRXXA;M^YWaC=S$3HtelsZbKXik2QBC2xe?DlmocK{yiDPz7$aKF%f621_r-gc8miz|!5c~)XTl^_L`xkN@GIbzq>e27EWFF8@gw|?@cK~WS=1@<BgRS{Rj9KHW6q(*v#IlJJke6e8tRmIHe;oZ?$p_xF)3=ONSzh&`cg*?SPkYuMe2y*$MDXij?ws|@hVW`68t52S=4wO|2UrLDx3pn5sx!g>i8aCqC?G6$5QH)_&r+cNKj{jF>9#dcIvzxPqeH@@^b<49JH)UW$?@3iI#Qg5&TE+M9aGLG5*JRqGesWAmaHFKW40~OINXOUB#G+tV`utx60#*mUU^f<M|THGdAw(c8=$_W6U;ckXquzcIfNecBR|yBGy4Sb6aiv+IXU$aoZsLL3pBHbK5HXRd}KgyX`0ZpYTNgA^R`l`4WF(>=$nP8UJTI(R1DQ4*olMqQ|>!F#ce?xztbxzYgAbxWor&qNfw*qNk&06Td*uM(-y6f!>YYPdtp?kKRRm4ZRCJi}(zB7J3@78G0J}ez&!55h+%_`2Y03l>P4?`6l6n{s*)6UxxpzF!(R)y9e6;Bg57$O2~Qb6m$QRgL=O_Sv&s)1OJ6m'

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
