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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9d6b66aba431493097f289a6e42f3614/part_003.stl', 'relative_path': '9d6b66aba431493097f289a6e42f3614/part_003.stl', 'source_sha256': '3d04ba99c73bb86bed1687ed8a37bf5f92a0dbc8a6e930cd7e318f6d07b27f11', 'input_faces': 416, 'input_vertices': 320, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22906538844108582, 0.021838754415512085, -0.2750728130340576], [0.20169565081596375, 0.4875171482563019, 0.245427668094635]]}
GEOMETRY_BASE85 = 'c$}r133v_X+r}rBAZSqgl1@+wLWq6MY5z*?5o;|mL5P$H2|`2$u`jJ%tjAVDEU_dA&L}}+X=1I~rmdo=3bobt&HFs}Y0f0)yRPs0{<*Hl{hRx|^StYs<vo{xj`<6emiW(8D%11XIn_gwL==-sOXEVuL=7Jt5?MDqVuFiQf_(93*Tr3Wb`JQ;MH(l?cnt}O96ZLWx$M<)Xj3mA*=y*iF;QcJ!v~HUGbBX#ZG%Tdh8TWiXmCV`aqQi|ubz+Gpr(%;EB`<L+>9n@`2)|{M3Wu{?DIEN>0R}pIJOkKcSfi(Y{hlqYw54zsoc6t<m;h3e-^$J_182yZoQ3sIZeAJe09ml$y7cwihOHE><!^tUhSDddA}ddc`AQP`7JKd?C%TW^4IrKeyvfr>6G_nSI!@hMfol6{i$Bb`$-1nc`$_Y@9sK_{PhpWSMJU*wcnb3mwaoNG*kPfiodhJ^$z8ivW~<%^DP%r;%S`HZnD2}>`f~FHjDENKg#X-=fzLt+or_Qc!orCdt6?b+HZ9o&3S%y=X$rEp6blkla5XGcl1{TQoY*r7PIL%?rY9pw3BI^wfjxTS5GD$p!2QKDOCQ8%H+#ai|{xs<@u8Cm1e(Z9iGSGwc?%n;nipyEYIHlK>a=0gzDA$*rrgqphxUit4Zxt>wi3#@}y;wFD3hKp?Yg((Xll&nN*4EVjhQFzJ_toZ_i@C>Hr#N^-14J)ZhKXINz=h)E*V%Ben0ze%46NukpNCOLgLQ&WfQt+R1WMufDu4=lA>U7Ug-3b-VlhY5Kg`2Cnxbp2s|X$)3}w9+x-dTX)>x_PpVBVyX0)d?~){4q8vM`B<%RhE!Qqoa&WsJ(%ar*KYhaPpEA9j{O<uc)gwC_UHC3XG_qyX}!9WFQ3n(d9kSP7TBEmaW587{<v=JyJJ0P^El`Bt#3L_qVs~wv%jY#uM_n_xXp>L%{d=V`KlD)c3!H)^CCUEepHO3^!OBw=cyXp{wWt#8m}eS$(LQ0@cO^W<D(Sa%jG`=n&vULuVNge)ClsGdsErB=g;LUE)P`7H>fW8)=zeE`F7JL+MM{-z_Alan-=Fhr~lyf^W~a3bUeEV`RdB%d#Kz?KDPVPo>%+*aZKmc%E#rKG(JM@ICo&L&B0f8o<YA#jdbQqzrGkj^(@UkN#l@tnSJR2jkC1#82Q%Sn|QtX|Me}E>lnp;^`e}A?pC@!$U}#buUrqH@|M%p7di9gww{Zqy`J5<-u_K^9!tj1IOq1QrK4z^Eyuh$Pn%)f&UsvKZeN>wc`~)DZBh1J-|>2A&Fxp4O61F%7jmBDM$yiECDkjM&O7pJI{E#RxP1GrVKyheI<P?)oj3Cu`O4%J(|9W9@^krE4=!J6R1EcV**_=9cWuZ1QNI4D*B+8@9XguxROa%zea$O4hR$nqo%8rC=RBS}#@d|ta-DT!>AaxxCrs-$eeN)u6JNS9Y8aKjdYbcurJDMspIS-26m~v^=Be?j6E+85y;tfGl|Q}m1l8j<k9_4;(c3h?N#0AS-YJ9myjE*@z12=wO7rX6hJ4FM+ce7Wtt3-@ubXq8WM3+;Adh_Ah5gOj`TiySP3^S0-#<>Dzt{r*8L#tXoqX%TZR{uA@UuDd54^2U^#@+#Jh3}W`K67Q$yX|*@%XI!V~ov-udOK?NqNp(BwrtWp2xrQ=^-{}exIZvG)~X5xZYE%*vGof?c3L_-Ov5K)|X^(d(xvh&(I4KY>vLicigY7JPvvMPDzbu9ql^8{;J-l?~(rD;BnLVV?6WtUn0-?J>1UUT5@~V^0;YT7IXRS>rC^dER5&!Z8yR1(bne7_q+22je}n-`}bC}U%f?hn=^k_zh+c^`}kb-a{fF%@>||Ua-MUEruCq=4&n9Vx7m~@kB>aEKES*_(at<R+9_WM<UE~LnDXcGkzeWEi1UovU>>*JKFaF_%Ca9b$NYVH>Bjjt&SHP%rq6B8{Id-|r}0^lpU0<GG2F)=QXW-vVSl45KM!OS7-VzeOQ(VcQJ#|Tzb8L%9_ODE)!pXI-`KLdsr<Et?0=>7p#06=l5f56iq~zC)e+8oxzG<0{*Hd?OwJQNr>o7GA6>C4oj2)E_A`Fr_1wG(U59h~x_?c&4(n(CU_X74sb6_~^h>RBm;I&*rg@R?-5_5cyUa8%d3?-^tXyUP!zmtzCl|-r9DHl?VpD(f_~@@P!bZMQbhoL$mViXgzjrnJg)z=ytGT>uFxvl=+HXl)VfKgS?_hK0k6GNF#x4FE_MgJPQLVSlng8-(FY0fNS=^qKA?znF8(?$hp9>m5<;%yi9}>!bNccc;to04&b>;oFDNi2Xo@d$!&eJ;p>;F&cuXZt%$8&LK_7&vM<*T(yD)jl-VD_bvrvB#f(O)fn0FT3fHk{`iKL_UaHJzUWEmPWao^_45d}<_JhjaVNe(M+-|KrWMU+-#Q9<%wn2VcMK$<Kjv4lSoVkD8jxUs~PGsh>Th8|B~c%k{qal-o1ma-_}CzwgE6E7nn*`KmXMo19sd`+Lco{h&a)&*t`}k&TBqmbX^h&d(w5LlS7*N|h#G^<9%j{uDm8`_kr~NBwc^@8Ii2R$|^C^Y^qxDeiBxa;9<q*H5a&?UDC|P<?|-u<wz;d1_tk>(s9@vmfccV(iB>pyw+U<FE8A$nBZBgzKICXQ)$uRaPjqKQ=%6hkrx+pYZ+n{D))YXa35*Thm@PXZ~wmhyVJc>X^n~TJeH>`S)MA-hk82{hs{%BbCf%zr+IeyImP&bK+YD9~wnk`wscaYn{t?;^+3<zSN(e+pS+*Wj}camw!=mG?jNh&wg=~m%K($e=-h|Z*8rb+M`rTF_pL1tBt9yQTaLT_&s`jS9-qH60g{(ABSGssQiqpeC)ZCRBmvV-(P&?RaE|$=SRuk62|K@!F7!@UoM}24UPYXR^;ohZnPdO^*E1Zpx<Gt=Xf<*uTskfbgW6W+3%FLk;+GhXOiFVQ5yB@!V=!ExDvtZs&Yf}r9q1m$xllAk?M2%?GWj#>fHXnFRgLrTOzZlol?{W+Fz6pWpVky7wc?JeC5K^bu?cSJ;|5)jomGd_0havY4_Cy?P=dq>|;8XxBN1W-b0kF9-Mbx$N}od!^u3J&$*q-^ZMjl|6a)Zgg+l&LFc#VpGxhY@6O|SmB&GkKg;`PQ>)SVNTDjVU-@Ps`D(lB^xkecvVe{)kumJQ{f777?l;Mx&x5P%r}M^N<b5;iZL7_Ruj@Ch^tn1>AAMf851lUsjih7i1fBK+l;d~kdnebMNqMv<spLx&BziB?SMa`o-B%?y+D{Ps1@w8VaPnn!D(}~!U%7q#?j)KQDdWdI)SmIzc--?XqGN5^3R1b&6#kwbJiMNcJqnU<{irnWhg|1zwt8pKd!D>3C6n@x$=prtt7s$N>Q|QEcP>BL=;$j`=F)u0{r0bS=1Z&guBY=l4&?X97PI-fy@ua2?Y_2n9=~rI@1LamJg9y>&US_JM9kkp?Q3ym7oF!{p7*6cNYoy^Tto78e?Q)L#rWs;)rjddkGjv%om6j^>Bq>A<LjE;w?uzS-&4IrHhpgO*_1@}TbA)Y$@89@X<Xj7BwyEuU8X!1Pdb(o61P)3`yJu-41Ue`wKl`Zmzq62PVL|Q%I4^+l}=Ls<!Nu|`eb#F+D7@Y&#zz}t%Fx@rSf41Pg0&csfQhX%YuHio~(sZ57T+>eaY9g_ZPYU2{gWzDt%~N^><aTQv2^TO{Bad+kHpvdR91t$L+&GlkXeD-=D?r4^ln-UhsJAsm<Ttv$yHGCsog2Ke!BEpRs-{r6#a{D&hk92R&(h>ld_5^!e@0w4UXW>rx$kEi9XSOY04(v@Qw+ldnf6@w&|(M&DaY&>Nb6<<1V87p?lIJl}WA^129&<NJ$m5B`2__<c2%pEQHULB@Jh{aev}!`j~K68WxYXuVnrHK6@YJ>(jdmr|x}AphlE+Mm|%Ju|Hb?UWDwexk?6QGfM}IJ$1AZUyMRr~I^q+ON)goMQ5;9424c`6uo7NR2}1IZo>pOXHyU2l90pzQr${d_A}u&5I=Myxv;KofB*6_{_>Io1<UfwwdOy;)hH}UtQo!`=Y8(*pH?>ixa6G%9-+KP5%5KdQKDj-6sF5BwEMH^ptdyKln9$uQb<Y#~pn&u>-At{ib}(<llQu>s)`Ge$>&o_%xz*s6D>M&xzwbCr~@Kb-U!a&ZWa`W2qfC>(cc^&8|%ASX!U5l>J4fbts+nqx+<F+Blx~cV*~%Xq9BTe#o=7o7S84Rx;ne6T(gFR`G8C9r>NN{6O{Kd!&8cV=EnZ*i7|Gh23d=svc{}*Ag0=zSru9(CyT|G6AORhI-$&lg>|0r|YNvIwp1LzKh!TPqOKHu6ZlTRKAl&*99xC!+O^*_i(-8ru&F`{=i<!Tj4f+-|Y7<*|_gfzsjwpe(3}FKB%sbruCt2pG*1lUQPLTGUGl><@eR3e#y8m>&9~d`F%d4ep&FGp!BKA>-VrX_50uFjSlsBo=3Rxc;orUa;rA=NAmf51^IZ6vKr4>)UOfAG(Ps{F3ZfT{QTEzI(=@zbD%nf-zU@#aeRHTzjriV#rvrfZ_)VK_gyWo`1b+nS#y3K!|w>voX7k<cooF=Km4ww)y$&tlJ53jMk;=H3o!k9{q$r+xFimZC}R9GG}z&%Ysp>?>innc;SK*!KV3Jh-}t}%>3XcuhFM0;fLg&bz-yt0z-z&Kp=ZE*!Ka}a;M3rf(B0sZ;BC+);BDaf(Ba_u;Gxj2;Gy6EXd7?<xGl5+SZE_~TX1`X;3iOSa1*c(v=Z0{{D~1|pzhF0V4+39LS4b`U^i$%up77tv@o~`_+w}VaCIZf8{q-{82mBHctC4`J-~j@&%u7+FQI+GUxNEX_k;U`cR;hiJHVOHpTR<Z0%wBHBLrWO#P5`>ze0Zk3;i7|^eOmP@O|h@@O|)O=v(k(a5l7{3v)L31@t4Z2*K~5CBY&D7l2n9Tmb9_EdzD~7l)Pu3oQyR4t^qW2>ui53Kk*w9yA|Vgy7$xA0%cGf^R|p0p9{&g8mJ@1pX2F2Uutd_(yO*gy5FY-r$yC$ID!EXm7C48(^VV!Og*+8c`8?8G03b8C=1IwW15N2*FLEO~6gT{s_UXp^d?<!L6VTz^%Y7q4mKn!7ZS^;1=NK&^qAe;AT)Ca5HctXl-yKa6@QKa6_;k)En#vt_Sr3*8|suehRJ&t_7_It_7|E{TN&WTpd~hTpe5rS_E7Q><)DSyMqfuUrEe`!S5y3hv4_%zl`_=dK>x>Ec9ov&@Aw6@I~l;@I~+uXkYLV@K?~!!C!$b&{|-jHNX~dGlXDIBZ@;yL2H18Rsahv3@!yO04)eE0Cs`8f?dG*phdy?z=fb?!9q)b3xV?^1b<{i6{rj?0Tx;nEVKbw2G@tS0oMnA2JH&|4BQ1e9NYyw0=fje!iZ5uEQgK&k3gB_(B0tW;DgW%@Imld=o#=?@Hyxq@Hy~ts1<x1ydF9WydM0G5z)}m&{<%iW5Ghhz(NOtCmS)+h>6f(@I>%<BVwT8&|vTwr~(ZJE8qdpk>CMfd)))k_JQ!Dp_9Su(Vy=Sf|ok<c`0-<cqw=hbRu{Wcp-E=cp-SPLq8WI1TTZefww?6AOwF4jRSuRo&b#j$6$;mIE<a(1S67+ScMS03#x&4fxm|y0DliY4BZGm4BiZ#2Hp&wZbWAzdK%FS8UpSG4uwt!Psh2T2*E=Tg5#kZ!SUct&;#I2;54WPP6Ho<CV`KEcR~}uJHacBm;zOy31AgG6}k#M6+90icnx$Hcnx?D^n36ga60rbI2~+*ZU)=HiO}ibMDQGF2zU;7FtjIlFt|HHa3^SIaBHYPv@_Tr+zKJMBeWN|Be(}N6dZ~<?tu^-h!8vo8V?=>o(<guo(<j#O#^QQAB7$R9|fO)?gXCzCqq|)lfkQ{oHel;A$YD4lc15%Dd0$O1XKkFL8G85Sm;!66gU<-4;%{~hY&myx&}NGybihtybin%nhxFv{sC$O{{TJ(O$46;Z->qSZwD`c4hAm(4}*3G4+D2Iq8+pYv^!X6C$N1jc0dSjYD68VFSIq-7hDhO53UEU3vC6i3%0)(3vL4KDCN9I3vLhX0Tvo4<-CInw!fPT4uB4la^C9&4~5Q_a`piP&xdZ6a`p`bZ-X9{a`qVnpM;)}a`q(zpN1w&Ir|ub_d-`oIr|=h*Fxt?Ir}7nXGl3~-M+6Pcq}v$JQf@VjR4!%eHcRUK!jj%4_BaHLxaFVqrgIA!9vG@zc8Y)5e=a=!41LHpq0VZz~zi62`y%Xml3s%_>U16jJRgRbt62Chtvm#R)O9Dix6Dd&`K_>H*qZdn+U-z5Q6(aAAtLSQxSrnLq*-sp`U<72z~>V!6IZlR15XAKVXCNL#u-Gg9|~+gA0L+Aq1B-;;xbEnGuf=f?pdE(9tDd>HPoOe|^dMQ$<@${}CqlndWUr$1{%_x&GaR4Cq);yek+l3Hj)u@3q+dk^TptK3=T'

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
