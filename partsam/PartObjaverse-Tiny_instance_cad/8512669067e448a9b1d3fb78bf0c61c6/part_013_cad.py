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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_013.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_013.stl', 'source_sha256': 'd90a5982cee138e9f4d72b4e39ef4a52ae1f3ead0922f2c0d38900fafc8c7b6b', 'input_faces': 566, 'input_vertices': 330, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09430338442325592, 0.005296468734741211, -0.3706812858581543], [0.3089037835597992, 0.4695931375026703, 0.3859369158744812]]}
GEOMETRY_BASE85 = 'c$}r133v_H-^b6DkRl<m?-^8LiP+Z!V@o5pP}S1n`V$RpiP+jICMaqNA&S;A#J(h!5X3S;QhQ^Ioe8=`qm<f8dGGoCzT@8OdEe)GpZ86lU%#LE_T1l`IdkUBIcJ_mcJ}ZrCHSwZn7HWo^)dcJ$nX}W#Mr3V(L)DCjS3zf^Oa5bk}v-(UC`}=u91CgVyqY+I5=w5pxD5cN?_=a=7B*<;E)lqqhkjSA21?zaFq1J27W#&%HfZS9vBnlIIh{KQT-sLQLP|lg7Sa-E8?hv+Tq>Z2W4F*zI&{VL$s2g9X{ydtJB7vlD;@Sn|uYn-hFqb^p&ZZhN~~qzRjjQO)6*5vE_SAK0<z8$R0O;w|a*Bj-~g?W1~I$rsp%tFOHPi=IR>>Ybd`FkVU?3`T4V`{%XL8^{&2ne1qz*_&y@v?46QEI<V(yI`4w3Yvi$ZaSQo+p+62uUq82Z2j#uAj(o-DeVFo3k3T@i6Hf1<@&m4NyRE;UNynZ#`I`MSU6<j%lG;IqZ{%i?Z=TJdW4l)Zsd=L}U6;Ca_Yul7w-5PhlX-l-6;iqWNq2Tq{?>s%Q=a1romX9Rm3)ybsNK{aU(x;2j(TwUja3fPbxqj6oyv82kV^F_^o)G7P0Rh1e`qNATFq)Zq;IeGD_y@~`70yX&yCtj<(HJFcG3#x?xA+r*PiZ+R-qjE!s`L~MxAYRfAu7j&aYMNx{K=hM?>llcKBj-8}jYhCn&!?J(B&GVbiGo8&j!1>RY}jTqA|bA8gM4wWpgYf5a1R$G3cCq!;BEJ<f1_Z)F&i=et^m=(^7BCtqxRy@l%E(U04~@>AYPrh4A@qddyR_3SsiznJnrpGx)7K3vCs{TJjLt=e*)K0mTwcGeo#dg^cccW-bW`$+cn@5WL+eSF9_%@OR+$RppZafbVMfz@02K8&LKrFES{&#Bt`6Z)OFeH`s`Z87=%Lijw72JfYIUJy;?jp13zRDQ=@Y6s1y!w=+-k4tvVqZOY_<+XVp<ZII&(0$Zm${nQqOLuOe^3}umx<=nzM#rm`ZE?-7Bt~&P58U5Oer<m$uMKTSd9>?6>^D6_?P;ITPp9&~6l6d2Ao<$d{`8z`d3QIt_7iP(4Ed@@CpZ61o?^b6T-(!Fl}FEoD0h0JtN*5a^Rna{c^CLOeHKs8qtT3gv3%KCx?lVM;_I^f)nAdXPF_pTr_q#sZBH{EA8wRiP36_!HjuUr=W(_4pe#BLJ50Vg;Mz&ble_FE%Ja`;8qZAMtvn92{(|abHYrE>%&6gXUhU;kI<I}U-zuul>qT6j;epi7c75qeD&Krx2KmWdXj~G>9mzMcqN%+8(3799^uKg|USfDWf4qq5XFrxizE&cM`l0gsa2gMdpV${gE|V`dSBa%^_sg#!zv@T(C{L0%jbkF8eeHaebn^ROpGwD1Z!f3kMvdqC%>0J#uhHeoQmX&wQ@B2hkJ5cr<NN+dzk5|Rjm}#niTmv=_QlYZ<ZBZe&!pq^o2kEx?N6wGiu|E=y3gCcVgFlO3LPij;c-3%{uCebg;BjH<<EMyg#0>Xs6UIlso#))%v|EyuSC(@X>@#X^%B?fYK2<TxMbwOx5mS#ei?4Q^}LMnCttJtrq}toIDDM1_ndnk>%4D#JV$Tp^Gl?AJv~lw9$lNy&tL3us?X!C{66Y(Z64LD!Zx}u#=WjwpFQ`eU5!d>&bsC?pBf2Nzec}M9yR~qIlkXx=2N*A;rza<`S2)}hi}Y2%+FoQd({8M1@_hIZMpv!PR?@mwK5UZAH<b#@)gV1;<=yi;QHI)3*}?#hx+wx)c+03$9=H}J~`y(TlYPE62C_*-`F;W&U5x*hMRA-e`b64^0jL$q4E{?xtFh5gYK{W{I71lHpAp`{%{w!Jldio{9O0=hv#EC$n&@__wz<UZoau^7njeA=6-bveugK{XD+Ou=fs4sPQSzRmSP<f>Aqh^{?==ElYW`}1-0j8_jVBW;o)sueXAYb_N{&hU$gwcn*1EqydCT2<9>-d&4<u^vwW=@-<L-rQ(S%Rc}ObxAKlUD`YyZQUvaYOOm5driS)ZF%}&tq_=NM+ZtMTEkbW2UA^A$XQ`B$O<txZH`wyl5ta%>b{+v{45#_1(1C<w-yvbMkN04vNK0@Wqobksg&yqgms~PcBUJdWV=N&ea+a)5M${P#jl5el@n4k0B=Qw|-UX<S`G=ln*K6Ud+zK?n2i-;FL(0SV_oc}=)u4mpS%jkOQbm#KZ=TUyW@&@wtTfNvHa+`du{Gb)|`&X;Tw;zh&{EhnP<fmoxdn*3bS*lNC_O&4+`T6b9fS<dRaqP!D=lZlCK<yynPLOZ+xy;u!DVOV$`SnVwPq9KY&o|0+;`S+Zk9?zM5cyi4G^&sOZTKqJ`fF=nQhm(m*W@daQC$A;ILf0YCnr()xl4H+F+u0+(r&J%`V4qN>jmT8Z>j#uzCTxU|H$L^xjKg1=Rr%J_xNW1MD?GT%J)SqC*Rzw@Oc+5=k`Alyq3<_BH$?HiH_lRxSBw|IogMO)i#~4w|(t(bR5!&@~hu(=lrVIdaD1%I4ZAo^yGG^8%MsXCvbV6X`H9x3--TDC*M4m!S(6TU<1_y<F;yz|7kbb_q#{sjg0P`C-DjSBBvmoSMTA$dFo%?NbOcPgzLYnGx_$Hx5>BO7vfKTU#JnbO;nHQKwjT1x=Hzs&g>h;C&##-4y5)mjLST~-@JjZH+v@6Cxd;p;chCg<Gve9A8`4^P2A2Y*SUQC5;VV8E)=2i;!zmY(+ud&^ZwGUxc=Que%?zRBVX?q%H<FK!}-Ij@VJBbrqyoxz!37yH6i@I+w>Lp=eFTo9^;Q;z4t92<D_Z5_bngqeFN`()AI4&H}KxKw|CDYiu3#Zjc<*&@YU8s-0E-nN@y(m)_mq6&u7e(E#xZ$22(rOL&EsF>ZNjd%$LMMo-f%Oz_;F;CeN4bbx*prgSf`?E|K85mD>5UZ+P7MD2e-dydU}2yiUcu&OVp@H}kqUp4S<n{^T3s@l;PEY8OA(nUS3T=mZ{@CY8MC>T8px@cVAn&ljkDCXFQDnrG@uc%EtRyO8tj&fxqQPn5hz>|?&F&f@v1+VUmWbCICy5+hggbq%p?qhrj64a|r2PuYJnA0EW>VKs0p%KyamAAC8-)z=;zXMeFb`DXW7>|=heS@ZKq_TS9Uck}#QZM&4qKdwc2#9}{c9}T|P6U^(By{D*sM8tOXu`V#4@VY=dbe()_9icwrb%Y2hyq($;>ki#ocZ9O9eBFrG>ATzYp>_@rCExyhKIK<?jiu|dZ);D!wXQL-uF(p;N7rMmgVcX{9i;vqL%v#p_oGDXJr`YlQJ@{KBZAtIZ@2uFo!Hmc(e-NZ^%<Qx&)oXto1ebq^I~0QU|psU-beEf?Y(^NSH06HziIh9pK?3@Sda23S3ccI*Sp=|>ur2J$JICEj_`S-eaYA6RHAjbwNBKrPSj=w^ZpCgl_u7eMxl=6TkBczoY%9$i+yW7t6J+>%g1_FnZoN?4ZgLW)lFW{+C%4X`RecRx}bIi?mzI=D?XgRYYsnO&sK7Ij6cdGth*l`a`TNOUZ-mXPII1+G~Tzod7RsA_)RX4anH)570>1C{cH!7SGN}D=iOdE&9%IJ4(}Tn*ITiVane4I_ZjpaD*1YFG(Yd_TJwD1;~rcd`xVxC^@wfkTkEx9yuV>)p5k$8TsPW>Q4)C{MxAku$F;~*zQ4`Nb3cTydF|zX7<HceTY6!he`8-o$G(cTw>10KKFpWA52JLeOuoLwhuiIsW1MGJ5cx`0QJ!BN_2K)qBb59%`#d9gpGRyM&-t-0Bz$>a$gIBHtv;F`?;~kt^W4g--FQDrnG-<!hN4&&sq)21YBytRJNCyd=X(C*$>Ug+Zsc3@G?8_NeDQib?@KONMfFr>R-rt~pEuaY{+Q^-`(tL>E%qn0r}d`xP9XQg0tM-QXj!e;PfOu`(scv*YPq?zk7{J?<bHl~<6hVPDFS(4&faA+``E`*it|36(lLj9?EBd}W8d;^KcDvl?d@-|k9|e6HSa4bhi|iweMt2M??W1Gp0aQ4XNK{9rfK=u&(t39ex|)yAiY=ARflN2)vzyWcr+y6xW9z=&r1bx`<!dy=8J%3?5A|$Jj(avs|T81<o?!+e6x8X`Nq#%*xxjYd~2WfO*_2htFgR)tE`)q?)sb>o3KCpmai7&{b5~6O?SKR%Wd5M=T_wXChSYw^RX`t-`bbf&R}2KHk`{BdPM!j4C4K5HEsl#FMNml<9^-`S8~U2`Ro@w&b*4|{yFR=?=NgzK;IX{ss*%vC%!JSpX%`}ir)(!NBMm^y)yfr?2Fu@)NcBq#^f7I5~zQwRSHmk$6JDYecN32Z~V;f#}CGlZ|(Ez)p?&^vwZCHYqzk^-!SX|Kkv_}pDS(odx2X2Bl6XaRrx!@ME<^DX7*vfMhTt|RLr9K+dYPIo>snG|9eIFJ?mSVes6uhFs<(w@&4pn-#fGu{JleYIiGy%`-obZzmFJyo#1-ldx~j&Pq}}E^WeLTx;T=bclg$K8Ra~GmoavDQopyp@2DI2`;K`aoaY~3uDwdW=*#o8q)*8=7R{#hsXoHs_e<3=<XhjH)bIIwli@#+^JMUMC4B~eSJM3B$hT+lcPMdzzeB119(+6~gUXvd&+>TN&yRfdRwnsIxF>z55fid`UApr;t;>{g6{sDwv`3t$@l9U$^%}O0@<$Y)?{nsBjGs@c@_yIU8sw`J*Rdb@EtS{%r;@MyP$GxU^Y?7Jzxu!FT>iE<`C`BjzP}%qr~7Kp_PIgj-~Eu+gE=k9*AAAX_P3w<o32Ya---9{R+Q%ZbvS^o%f8XfqH^&;7b#Eu9hcg;_(ExO+0_?;-RU~DzK70}-)S1v)5z>izMhg!zDOOw<4^n|F2BAf<yWV~P#()S3zom^>KnPMIge*Pmw&$#&o`ozd7VGx4*A-qt^B^|e~RY^jdxvet0#Q>7rU;w`pW$BynnRTFUPGu@bwpcuekc=b}!zaI@y%UYlh0>a0@^3%@)CYUuvwQ`WRi-o^s7Etm}er<+prOdw9yV{u=6O`BwccU#(O++qFHdJeF^@r+CxOG1;#7*UDr0*8R17y-6>g58dd;^T~1_@qR+7%yabLkDj9YtI6jy((P+~!o<Q`-l-^rjKZRn7&6f1Q@u3hpQZo(r~09d|5u;tn>20u|NT_|j-w9pdwpSqWG|>6*b7`7A-N?q1T3{ZxFuM&PdjKQXnSxc@aNDkz@LM6Lyv%WgEJA5k0T^sf?ftot!!hy1Xd7|8$jO$Hvk7gtAm5UwV}S?n$Q5KFE{{P4*E<mmjf4r{sopH+1sJ_WruKR5gTh6a1rp|g4G-Bjo<!_kh~xI6Ikjf@P6=c=zCzPox#JwW1t<uQoDhrjs{EJ3LXQ_fZhj7mDi8~{TqG;>YWPR58jV@q(aAl&pYB1M_hpR1Lr^oK>LB4Lqnnc!2R(1P=w@Gj%W?-5B&uE3C`UgA^B%VRJ5^Hg`Nk?kX#9R0W3pu6`Ql(lKpM07jZ0o$;Y5SLUX`Bf`>u}fURpDijdq#$hib-3utq2F{m%JIk-96#TOyD1hf^n1lY%=?R*fDOFE*ABPuwe7D93`v^+Q%TnAbjTnDT`y}{ndtw39Y6>wW<e{fr{9U(aj`ZG8SY_mD<t7NG)z&3DMM-+8LX-7PEl+6>Yuc6YHETCnerSS}x!Ee2xMZw<SVo)EObA0f@_~C=|TjNPtj5lRbH*5T<f$^y(I1pM990;xjtqQIMt^=(Eu7v(s$L8#>br6#4+j#txszCj1&hb{V9E1JQ$1l0`Z)<#(EXVRp=w9eC@LupD=#St<;Lo5#!JmQqLi>RGg2RRL*$78SZikTE1|hj6v<29DeysPMWchCNf)<1p0~Z8)Ac}DpA@v1IEdiG51Ga$$w4`wUNiG2O1{VN(I-(G?DAXG)wKTXWxD>QJxD>b?v;w#sxFWO+xFWc$BdS5GLd$@q)&f@r*LOr$Xa{I5u+(612XF+m4mbiF235dP+k&Oq!C~Nm2+8}PSzxL1ncs(F$-hF&g3IEWlq^H?J!nyIQH&G!5Rwhy96JnX3fKTgLkEEep^c)U9l#xM{m}@?!=Pc{FkI&_=sxf;@DAv&;9pVK9Z&;o;2e@0IpSSMG(bqM0j&<M0S<sR1P6fYL3@MifxAOTg1dubp_{<5;4RQQ;4R?0&{yEQ;Fr*U!7srtptry;z`r<RJ#+)~7I+;r7kUev3x3DO`Y%|9<igNb;8&=tWEqlg!rKJC3Eqg190MH*9*MS#K}h}pA-M^(A-D;+GPF9lI__m<gyc%lM&L@|#*XL-?FDTF?gf4y+5p@GS{K>?To+sgS_51K><<k9ORWd?2iJyn2iFF7fyRQnfX5;vZ-Z_DZv#Jo-UUAZd)ZiDf~CFy%aB|M`U_Zw<UfV8Z~cjoyjJk@F7-bM$)7^kgFgiifo=d>{c;FGauh=HV1(q=2+7x>x!~*I=TO;qpW|5aKhVNpsj`p$gOGd;x)FR0ycr>R1T+RL^#kw-a3n%<GiVcVGjJfZGFWOQa3HuQv@y6QxT$dV<E9A7A0m3Xv|CS?_Uwr^mfFju&3obgNPQn{^?U2y^>DerJ#fzlfxANMg1dt2BP3UaRuRtkspM)<e{eN$5VSTp2;2?Y1>6lh8afs%bsKmzcq{Y)cq{lmR6YauaqNZ3j2E5(YjRTvb7ZOV8F-D5oQIH{0$mHXo)gLPT_)d4^8J({c)cjsjg1^R8#<yHLUL1ROK?+gD6}0o6s$tSz$&-{^gVC~a7Uc0m5tBe2pj@!3l0Idhjs*aL>|d=9M|xXBgP{nPlJ97o(5h9y$xOlPJqq<&q1yP{B|aerD`tc(okk5%B_Gd1FrxlLKDCV_^sp_j+o?#?+}uwAS6#jNd6Kb`5T1fIOq)Ua!0Ik#A1Zx?-7!JKuBJRkh~KiIT^Yf9Ebd~5Rzv@zXQ((PlZkaPX&Jsoe2IK{4w-P@W<eB&~L!wz>}eI;5gK2GU_VptRo~Zgf0dz1TTPo4_*LX0{sEJ1e^q22~Gm1LwADH!F!;|;AGTE@;pbJaYQ`yFgPAO9lk901iBsk1bhR!27Ci-LYIO~@FD1Q@N}F@aw*5NRNN7s2+5BGhvbKXL$U`#a!F_@@Ht1BqmDR*kbDp!`2a%lNrdFH&~xCD$XNj)xggXNTo9ZuSY=)F5t9FaJ_P>(E`aNi*H8c<xjeKaxFpUk`7G*o6(RXF^c46sI1PFboCe+nJpkSXJ^?)mJ^{W0JqtdIb6-K3Y~+yM@9?Gm2EGEea{h+jWP_hVOW2qTLMuQ^xU_!>w1ZSXaCxw7zii|)g)^54&3EaC`RJ$lxF1%(mHY%M^F4w3*_?e|@)@YS&NH~)tKh4+2WJqH4@1+yhrx%SyTH59E{C8dxV7V4jUCYj+63GN+yWX5ZUJtNkX#q_mHHbr7%U?g?HY_+B@j(;{Y`LgKSX2XlhGLYrM3pQ#<?ZS=Y785XI+jJavZVVO_JriOOC4(1dqE?zY@-ISn}6UO*qGG$y1>-g>#&jJR3SsINuABXF=nI^F1PYGITn4GT0jPr=woeaV=IIrOt)U2QPpwgw7YvF<-I{T`HXK2+4b(YruQJ>Co-MIkrnqg02wGcY)+3&_v;UcO(ku`y~<eN<`bug?<I@<hW<`91#w!29E4(D^SYgfBIiuoqw85{@e9`fPMRy?w{XWf0^va_2y$-Waol%Z%h<${3935f5}}u@n7^+7h?'

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
