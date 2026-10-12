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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_002.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_002.stl', 'source_sha256': '2bab387248642a1a1885a93756e53564e201d42be4ec41d7651513f997500e88', 'input_faces': 312, 'input_vertices': 420, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07206384837627411, -0.4999999403953552, -0.32610809803009033], [0.15262021124362946, 0.2756817936897278, 0.39817893505096436]]}
GEOMETRY_BASE85 = 'c$}r13v?7k+J-xzYfKPOR8|2UL_ltG2@q~dBa0#-fFOY+Kqd*{4uJ%40nq_<5fHiKZPiIaf^4{nxGX`Sa{~dD3<09Vz=*mcm<WnjWck0U@9mkXO8@8l=ii+3p6~64ny;#>yQ{mpnqe_@Z@Asyzvf26c|#udw>Au+ddBU>+_a3@lT*_&ADl6BUYOBPa`9)!wL?b64vP;n<{ArHk59`?&1l`r)w<7w9<AHET2DyNn4OV4BPl&&e45~oCQr*uBc3@ad1e}IKhU*Hr}nO>Htk&tUH{L&2x@|LFk|Nd(Uz)5DnvAMhWq+bbRSI6_*lu!gK?6ZRk7f4%uDYEe^PQQ>t@M~(*L|GwmntjxO{d4$-N~tlDn%$qx=n$yNZT@$1~5Fu5hzzh~%D}Ig)z{?*ktWo-Vm%{k%hLd#k1}&u+!#t#doLJ>$Wfa(?Rwcq({nE<d-~cDY^o`6<~SvyN_e;{K!W?sDW+{r1TA%&Fcce_vUIJUQE)xcBI5yBv8{8=1$Pb5e3o*_|ikzh@mTV_v!~v|dkaPM&Pf>|BNWQyOh?;+_)UPABfJSijqeTjy{5z>#0NYrkXuYkjOxZts^lYwva^?moJCmlO9?_1vT6FS`T%aDw|`_IjnfKPFT5gO#~Za<i-f${#6XK3#23@|XEe++VzJrxW*_TDaSZTjwwDbu51=Y`<gqKRU_&F*64!+%<T)Y`>BDka`^Z{Aq&|clAijlKqp>QayiCuI4*&SIOa>PTZ_my4#VTzqZ$rU%q9(WBzO1tx#^2wdVf!diZ!{+@kh#@4WSLzcOxAub1d3xnJh2s;$cT8NFp0^N+W3{&vW}pe&So%3R=!B{yc3ZdJ~=KBu_eS^E@jM#pe}&fKb&@AlnNnSbVb<_G8cWcw@Eyf1$@bA{T@wH+tP{4*D#{CuT+kaHeS<znzToTqfSnm>K4(jLpRJ*}@3kD9hDlzU1?AkQ;0k0*Vk<nGcTlAE8u%=u^Bq2%#y=r~d4nYLmJ_h)n2pPsDm_&S<89lVL;X4V(Xr*zxG$E798|C{@N^1giL?YX@7b@2BkH+<1JUTc_7dI7vU%D*YOXJT5uvR|hYc)!5y{qj~$;Qg8yn;+WGW@Q}r^TYx9p~uB8Z*#l<ZEj8IpyY8^rf|Iz=Ko#hEkDNl`_<VpS#H7<@J}SSzWPRTPud{xk5K*$mrrX8egyn$E}t;}HQ5ed3inUVqvbLt3<943{ujwT@oly8k28;(|Elb-vd-L}H6xghYzy8Ad=%#&dH1V)ygGnC$vie<gXF&PykFJ5InUq=>$%<})N3-2DUjUbbF1YCURbB*kLCOWPlLAwkKyu<6@Wj8`~$iC&;{Azyzn2pBDekPkCw=G49$_;DEmorYuyrs`;Yy|e8a7!GCt8Fhs*ygxp(bjC86AZ><2FY%1|!<<VB^te@)|(Q0_l=S#tNQi)48-E@q?P-s^vymHXq(<MB%8S?3+OmEFzf$T#kF=DB|;-1>e08JR!#j9UKpy^@=`RgT<~`;{}_ly=;STbr*t^DVo|RlY}ZV_Urwq1^LRdX;R?)^p`5pC-Art>+0RZtU<na`U~BCsjU$`L3-hugR~JdEOhV@y(KZcI|TH#y^{!a^!o;G`>l4v!HcFC^x_P^fQ@%_oP!QuaMmO*M3KC7PP8x;>Nzy8b8V9_jmqOIUmmc%+Kcq?JHFN6F-OVUF^useHR?LVZE*8zry7Ue^PnHm6LLRKiHw<@mKsPxwX&u)QKAhQXIKec*|#w<%^RP?kV^4c(Tv0_D^{!^Zgyvb{^lv<JEy>YQ4S;E??9^&F>q<<96`^g?r0dpxzp_-;P}<=X!gn^?tI6$C(4G)p|dQ;_^l9mHfs>zaQs%=PKMhvW)qGX-XdB$b89-58hDw;qX8%zwbANdrF7N`<-PSR@+n3fqCJbvR-#wB9}i@#`oDPpUeIB#-;LpUBAxbTkh{X9|ZSazb3hnXB<~}U|jP1oVc;A{)tfTFKH+1HHz-~ER<U%ZIpKU<1#tVA-~d2o12FU!7KUrkILbG>p!$m{%-9<a-8>%%IA6y)$sG%m8uh=+&HvT%kv)c#L7IbwarUZ{)FVlx>1rFqxUM~xp6MKOyPF_?7!()C^vmW_&of6W4RMIE-sPB**&^aIWESz?q#7oSZ^<d2lMlJ>K*+hx4-NczTd6+r8tz^_d(ZdS*1#O^n<k~vP9+F59Ydb$zAbRxt+eLTyNoJc^(G&Wbj`lH{$E&%J|`LI4);+zrn48n{ZrCOYV+u#N3z8*D1y;Pka;3<Ld$bz2sJW3-F%c=fR_x_m7e7xBDT;NAUTxZV?~fgx-?-%eo@ZMc%K3{*s%eIegx)jFoxZ2{8)yuS|60*2=zIZ^BgYY`%Z5jMDf<eh;#0vgAf$rsS><jpItcfqM^n)qYD{i}pwH`CWJij|1R#KbUJS79UVJ_k*==MM)?RwzEyK%DJ8HRhiuW#2nPi&#Ok!ZL(e~@jV>JiQxB0Zj9OM*iP4&Vy)g5GJlYBy`EL`xIJTz=7ye!Mp089XU2T#T<_Q)InRf6)cyq5$4Q%82j5cq*+1rLZs_%8_ovPE=iVT{gzGN9RLO(mVyyY5SmpL{S*_%;`^UAid9lj5f4r*}NN$del<zG9^O2%v+&^R6@%tFxH1H-o4v&q>3qAks<6?9DxCFU+TwLS&=c)bA^_t^G<b|FmR$)VK&$!e)r}Hz&)$`Nl`uQ2;+W9$dD(CTaQ})Z|`gLR^@%t+Mx-*lOYxVN=8|3Qs>q*K1SH}mP+v9^bDPQ6CIAgkt^Fpr|dt9=)KE4IHI=*?_mFS0P<oTAz)mpqp;rjUOb$`j_wej3?U&L`&$8Ep+s&c-03V-1HLUP?rq1Ugc@E6J5$&EIJUSIZp*<8PW1<GspuOL_NU*6;<T(5SYwYh$uwYh$u^(RMZ<@tFaz_sTAo9oX5I=7z(Y_31I7%9EE9}ZP3&pBpFf2AMn=b0c^pJ&XJ5#Z``l$Dan{d4H7lHca8LzX&DramXRK7P7W*DC#NKWExpf6feW?KxBD_H(Aq_2<k$z1nl8H#J{5UiN&y7RP*F=k|QR7RP+Q7RP+w=K6d;P+ptw>)f92*W#G(>)f92*W#G(2e~@mx4Ayw4{~+BuXB68uXB68ALQzMKfty5evqs4eVyC${aPIJ{UBH8`!?6-`$4YG_jPX1_jPX1_k&!W?+4BYZN4Am>U>}4_IzLG_Iy9c)%kvaYx8}Z>+^k`+w=We<uTu{RUY&GK>us={XqX{^Zh_OwfTM^zc$|w<k#l=f%9CO?+5a0^ZfwV=KFzqwfVly_4$5azqI*&pu9HU50uyD`+@z^=KF#6X!CtDE%F_iUwi*)^IGpeCzUJZ?f0uT*Wa(2Q$}p&^6L9ro9pjy{ZkfztIxx(>h}xee%b3mcu#Itmlp8xx)<-62l0F6>cc3Hb&Z+<+}>(m0iO?Zkf#^dUtI-0TY2wo)O;<uaeTf~-g{{Uucu)>#jF|5^<G*H-VA&Q@5iOwy`1MM<-NDf1Lqsc8<)4D{L?7kpPyeY@6+;dKe)n6<^9-yW)Ifof93U;@I!q6*48`B@Q(}mJW<z2%<y9<KVRcMC6B%S;tnrIy#>7fo>jx|y~9s(`Lo4Jdu*<+?|8y1&>n3)DEzFtU)clr`8T{;$#3NJ2meuNkC7A0-!nw?E0R%L7c(OIOCDJ7exu`5*}jMoMWO8stgl6kRLXm!2QTj%!fUPH+2ytMJ9k84QD{Hg>w`Ae*9|=pV~axj-(F|*L?lUWp8Xj8&+B?NH_n#wc%F5RpHCu^mG;}~o1TbNCBI#-6)|1i-yX~5x~k3f^;Rn)T`6z&joT2)^>te-A`|UAi1uIL^EPsh+D@z&`y=LIe?P(Z9zFQ@Mn0?Tua(`8=T(tQlsrai?=4Q;D*1M&6L(i^-tCy@+h!j)asQ<b`<=Mw+M`w|*Vp%TZm;j_++N?W#j(C$i(`GiR(`DSn~}?vcG}+|n2{@#<6>oZ_l0u(dj>OdrMkbdNAp6t{#}G8GFQ!Gf8V0<!1pa04}9OE@xb>jI=8=X(evZ`7Ata-dY;d^y4{KUkCyIo;>MYgdqTPXos7=y?__jte<x!_ZrA#g=l@2%16=-iCf4h}k=Ki>Ua8t1eD9=l`+KKa9N#;c^*)x|zCW5-RWiT3-bu*=^KpC+;Hmc+%JY5G%I?bJaJ_0JkCojU{ChP|c4vMMR6ntp_sfHNeVo6368KZ#r}_JY`sv_{z(1ATUw@ub-u`~fUw?s;-^%XD<3od`YM$(tzP`hhuLI+cRDb1aAc`8s&BpD<gyfJ<0|hh;BM_ZG4V>Kd|MY2KROc@L?Wchq!VIH5sS9Ff_%86#h~43%;rl?s_a^m1?1tDKz8ice#Ln=Y;M*a#hi?bp3b8eOEBNM!_rW)ZZ;IFqzA1cT#6QC~hHnT7e=Fi$@VCO>Mrwq3H{xCJBHjakH~hVbE#U8kzaQ}d`1|48Aa;On1OFgm7x)L^qY$Ivqu_fW_JQvK{}AaB#D0i<;QQb>^@D_eIOJG93<+<N`Xcs3>;>NwzAIuk_^$9B5j(+mgl~)34!$jXOT<?2E#X~=&EZ|}O%R*HH-Wzsu`&Fe@VAp1AT~s74F4iskBdpqAufb}4*nU$zrsHQKaZ47noXJk37?5L4}KoXXF|efK*B$TxDfs+_@@yU!#@qbi1ataC5VgRMSKx{3H%DuE2K4~S0UloBCdd63;#0Wi|{YQFGYL~ekuI(h|j=35C1IUJosnf=OfOBpASC=F&%ym{7lkh#7T(h@RQ&tBF=!H2tNT5emY_%d?t>8@M$PF1#vq36!>Y7@Usvz;4^T{W<kQwMSL25F8l(-MeqyYJt4={0}1~EX+3ErX#;5;;wr?I@FFgQUj@G$@dfx7kaIaC{7Z;S;6+>kFX9^bm*7_;z5@RW+O!&R75pmHA$%lVV|S4LZm@)(iufOcy^!$lkhYRGlm38&zmE71`0MaS7{_<u-$5SX!%2T4mC@!+*cLu4jJJiqjBVSC_%$TF53vaTeR#n(Vq5quYzzMywuSd%TlgGo3%?87wimGw@fiFuZ2uea2lzT+>;)71R|oC)QhbZ_Ht99edeZBpY*G#>i}Z##4x~3p&y(ho=8%#}NhCLE8Yxp8BT^hGku*k(;Z#RgQWWV?(g4z9q-LahNw<;yLh4U?#NfX=d?<{YL|aMWq#H>$km`za!w?TkG`%LpQo$jlp`<5C!$~7aBS^zYPmp3rgGhr(U(s*Qk}64iN&h14CY>goA$>;LN%|-0JyIfREGZr_0e%GONz!P<c=&jf84U?Plr#i!7$p1?hzal_=Wyg3Ng73pLmS4R{$kP*(ubt)NS8?8lRhSWLOM*kLi&mHBWW`2^LWxk(pb`H(m2v2(hSlR(kK!=RvHPUKJ**;tWJ8IG>|ly)Qi-c)I;<+X%Hz!98>yDxj2SlEa88Fgg*fZza0{OJS2PyB)l6EejFrx5+r;wBz!6){5DAV<B;$_L&EnDV+lVXj3xYIVJzVv4`T^G5K-)>@VA8Vb5i{<z9+s#dYg2O^gHP)DW9~7w1rfU%0+|)pZ$bygm^Q&eXn{G68;Uu*WtxjD#k@IK0YO$KS&Ene<dv?Jwu{NgRzYCENMPzImttMnzVwnn3PU>PSi<CBh4mFAT1!hL|Q~zCH9T9mb8-e3TX}LWzq)HYSQ0G>qtvTvq&$HGDxYU>7*2ri`putI&BOw)uFMQ)RuG~=}uBRQVUXJQhQQM(p{tnNu5a#kh+tiNnJ<}lkO+|nbd)FE2%!IDXAgp7E%+Em@d^L-A%fO)QHrI)QKeimsK~?L!_Rhexz?nH&A=eBZ}=C5ii0E311iS0=$s$zk+=O|0{eo;yL(gct7Ij@P7D{h!yZB;Y$#Y!k57BK|Bb*2Yv_Q0r(y8xrqDWbK$cQKY-7M&qLe?p9lXgq6Pmhd;#Ji_yYJ+#E;-h;ZGrc3V#az3&bk;FW_qszl5)W|BW;(Caliwb^o{jdKdf?*My<`M?C$P>a;xcm-o;~8JMIGi@8zUpXi2FM?S>O6KAUNKWLxukN'

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
