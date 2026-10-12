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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_012.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_012.stl', 'source_sha256': '98910181c080f0cb4e807c7e60b6efdf1c8843c7dc046a8d5eccd0123c1a5329', 'input_faces': 295, 'input_vertices': 254, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-12.302543640136719, 100.98265075683594, -0.21424701809883118], [12.302542686462402, 149.9131622314453, 14.763995170593262]]}
GEOMETRY_BASE85 = 'c$}qL33!gzw*DkBk0FRCKA{pV<%pOn$wy1gVkRxVP)Zv^6E(HfUn#DGs#z6(b<o49I*Mu)f2V^|swf@QUv>2uYl_x%-M!xR{`aQ)ai8Zt_x{hbp7pMGuf6vA_P4)1C7B(gW8xhB)pTNh?(s!tyyJ+Ja^jq^LvqIqA3P-Qfsvyp6mrUemtREB@6xMtX1_wtSm)WK$A{z%&P{6JCbb;eEUBKGG;~z%nB44<14rdPK1BGo**SSb44*eFd-M=vCpSuMT+dCZThD#o{XhOnNDjZgnjA7JkajKGGurL>-Myl{P79Pzy$;^LGz+}@#ys%e`$YzU&#YfZbRbH3H&7CMaPkWH2bYcjADVCmal%y=g7=p-)i@t%yW!pOh~um(3_hHBQ``OhHT6%9Rz4<Q{dbmtzhA15#>t7&eEQ8)K5!uk?Ji>cQC}fWVBAUN>otRaVCh3i&`lOAf6)UU8u<|71f5yn1387jhqq4!?;gkk@7>aN!$lIbA6~1Y{<o6ByNmZDzPmkG2k{p)P=BurpEnJ>H*lEdvt>y#bfZS#!`am}PNThu<Fs9KFZgEU&n7A#w-US?p9kJ~A{D%s*af^dzdLxZ@u<3}H>gi-;r(WPmCt`h{aZWW1BcU;-;@o1XMNdP;QK1?EO-`qdb5uvf`4YI`lnR85B;~Nq4HZ-Yk!VOOV+$<fcJV&(C5u4dq2v1)~|_twmqkD-h2uEq4IyY!Uwzc({|Usjrf6Mb-{Z(x+y<pJ@O2s-l&Rx_<n}=bCbk+D4%`}d?5Bc^`Ef>?K-E%fcJ_I)_gw9RX#Hde6ZOz%|9im{V=bH#yLJy<7{26{GkmAh%-(5(^)hQd3qIgRRQ0AU4OCtB@fg<J8iy;7v5R6VF3ImuC9oDCw~Jz)O5D`w=Gm1?FVas4>XKb|E%7z(0?tW{+rIg-<f-&oao@by_FIF`Ay)xk5en7-QV&n!GG}c;N5y_62V_OtbE6FkD-2NryBTcbCoYYQ}a339lV#&4ZPp+l(y?_Mn2x1WbjVUwVG%AmP&}%tO9s1JxklYdZi}#h6gGN@2)SQ{^#14M?b_(2k*shQ~xDBkbkgsH27f40Q|kI9rwV$!mc>@mkg`_tTyrB_pJi&-rrU8teJ!N8`%Gx`q$`%_vL=(V4MU}hp7M4nczbkIX;(m0q@LPp#3nhF#5sWRapJ6<Y~WcpM-V;H4A|c_UWhjq-EoIL*E~)fH?Q|MgDG71Mp7!55WgIj7Gb`vqzARdt)(p_rBKJ?!YwU<6oEu-e0msdH=A!uk(#H{>5hy$7}p|j6>(lw({UBy`u4JE<k+mg_+>}2iIu+9~ako?5!B}AGJ*TVM=A~hjo`@g%6#4LZ2%frSCC)CHQdCVD0BaMG!yy#4GBb+*qIYRHzo>^q31i*ngbn-{yOLFHJjXoDnZ;{Nw!*-<^KD9Q=!Pc@*(W90l*a`4jlSq>;$q^Sfc54}Gu`e5hx89sm6gB7U&q8s&dU?*~3NXU`6aH|LGAXm?o)?YEV#&I5zCmJ!}Nsl2-`O2^6V9;MMgkJLuHfxU;y;CUNV2k$;rMDuC9rUK#&{bwn}+1FO%57?>i<%K-(;qXJ?!%t-+zJIkUc>ly5&C_d^pCSI6CYD6I<ELr-*mC$@oG-J%2Xg9ao=Y=yoUCuH{)s8-U-D#alwV2*?;jbi@BKm|zEkIBbMT=b@7H|h9@2hjUKG5$VnP<4w|2}O<l|l}0snWq!aumDoQ~T?N5F?CpVjwuWD&k!H)|ny|JoGr{@xCn&%8&#JDZmwA7}bXJXh#+3FXhe0Ny_{U-L{qT^!Hr^gz3T{HB`cx-XQkQBU)C^R=Ikt^*(bN!Q=d*QIn_$c|I~tFGEVyH8dDe`8BA<T*SQ{$7g%h#&6v2KeyQ705q0YB$E4v;6m>@Q+PV{|h?Lcr%rEmJdaIw|27x<a_Iw`uCfo<9zpM%_r>u_&_KDar`6W^t-q=Q~e(fYM$lRp?}<GGr_y<bUgU;eDsfBdwgNEyI;SH@WdVZTpe<hAKeS>2423S^S~F0;JxO$zIeU9#QGaNeJTe2t$ONrl-yqTb+u}M_cs3r`XN+oDfSQkCw?^gXMR=9^Vhd^pA)k+3VAMav>&Q|i}xOwl?pywyA0xlXYJGPy7TEm!Uvsp82|344X(?0^R5-WBj2mLDg=M`gPpn_RfxSUd@v?S<9GfT>#W!2+nd6N_NM7~8vir+VEm)toxJjRUjJNHebhTuP5p26(R^0*udQ+3zaf0M+LJnNySK%2dHsrAM?P!X>+^o_2i9w^%;$dy@6G*G=eHGY5Z@bF8+<TfhVt(|tbB79yz}iU#1DLZ4E-6}o^Vb0!1-I+|0f1uzY#kAWj^w3+FAKEvyo4DTnX_0rK9>@zPYXM<(H?gfKR)s{Iyg1UOpcTK0NZWKJTRR`hE-dz6d^jv-a~hy>;JG@^2TA=Xia;?wNO7#QVpv^T=n4&NI$W8^ODy-#G*Sw=#5m)@=knu%N+{+eKGu2|iRa2fQ=s!{Nd^ha2d;lzs(#a9~U-cxSHWdAWk_KkJ+ee=Kotah&8QI*8w6)5ezK-hQg~^L^9N&%t($w+SD9>l5XxOaUL-*77sqLkFXEJhaROA0BokD;?utpuYDP+o9h=uV)Ps-k(}o`yu1BKJV%u9*2LcfA!NmYat)M{fv>q2TOO-{$HD;<G*vIT;aWH8+1PT`bYG$JLJhR!UtmdV!rkNvM?I)M!s_<<1YOfTtDo5#$Ec~Gw&<oF7L}X?>FNv?^nh{#$CpPXU324k@4eS((w~A;|;tu-W)TY(JsexaKDac*L*L++uw_CzAv<Ee_!T%#B*8Sqhr2n@YZ)N^MLU7Jm8yo1MS-LhM8xOpEb`oQ7KVq@776-lkoXW<R3Ki6>Mw1lKBnwt@%ynL-^VAVf+g4PM;K=Z$E0K{$^f9ea@>+X`NRC?Q;sFea_p#**b6g<;R2fBlG+O&hutnKpbmbkaYyMwT{TTgK}%#@y$8~ZLL$XuA!c_uE{zGe`_5KnROHS+3TiRXW?(HvmrmOIQ;E(*{tK>t#v$*b{f3BAMnlo0rjl?gZJDc-~*BU#x&h;$o>R=*8U{C@CbN&KO_4e<YDiB%zg>l-Y=Q`75uIJRrq3hN$vMP@5el|e?vRg{!R9Kh->ZlLK`QlzqLOMnEfQ;Tl>j?*{`C$wO{qk{uXh#zYRwAw|)nlFTGuDbpGtJ4ErnDSEGGvUoHD^@YX(D_U*{a+PBL-AMvbxzMKotzI85;a|HaYbA+5bP;Q+&<eY+X>zpFz8ffcW6DS$0=h3|V$~W(>=Oc4&0-wKu^M7-luhuUI@4LEQyK`?Q!ZznMXzRS@ne!d|tn;0_cP;qfd!F)XXLQ{+=SSpiogd}A34iOn>6r5=Z0md~=UJ3n=UF)~!{0hD%lR7lTIXvyk3-w%adUo$ZJ*!Gc^|fQ-k19U_*?e_a-RS{>pns5ACR|w{}4S^`L9MOU$?mKH?GYEZ{K6cy$5*Sdjul)9>3))Z{3r~y$a%5_bPG^1AprtM(%A8&$_pfdmfZq_dIeh1V8IuNbZrKt$QT7k3v1`J}P*uuCD*q{g~Xdp}uv`7TnVi&u8D)x$Dc~yRq;6oI!nby|V5P!xdKQcWm85x^35hx9=_GUKH)w_o4@~^ghzMUzPh<<YV2(`b`$=e%ZRem3v^=);+M?8za7TZyZRD25;XphhHzOynQddtf|Ja?y&<)N9g^feeWGLPy5xnCzpG5#If$x<sKgKtb6$IsaKURcyFKir@uz52v*7LS;l-hMv6Oe&d}@ve~J)Nei425KSd00{J;BCMDx`D@1G)`GdVnO<SFVL;u%Kf7<rny8}ZY`9jIS1(ua5s?TJSI&B#n66KF@U=)W3yhPL3&M!Fd3Wu!ap2p0XAkw<Aqu;^h%o}fL9G5X27V!bW}u;|BGuU7#qdN}JpMm*WbTqCoMyhuBOMNcy_g?0pse#yvG+Je^@`J0hV)EkL65pSp7O1z!;6Y3DL)P0A(qTeOnNW7K$AH-XUL)0G-ziMQjk>%9$iI)?vpk6?{f_NdZ=#{Md5`ACdv(KkYW1VU2s|A$VtUsH5EBHPmwT;v<(tvgZi>_y+Ic>o*CWDTSvpK{&s6QhX`OwjExPw}J|7m2ikyX^M6~OP&7QKvEWR{VaiI>q9z0}Bb;_2k&Ec}I$L)75{_$%5X2aNng5xkfBQ(}>~jO-(Ro%UEGSw==vKT-fo*&yn11@OzvZ7lUTisbw(@hsY&k#<Jzr*2jN_oO}E$QVb*xacVba2{>ZFBZU)X$#J!{hg5$MvfafOk3~~;={zE_fvKo`G$BW?IX00Qufp5dzKv~7X2eRv5&ExBg7|Y3;u=nG0I7D$5{6y^^e3SiBItvelT*7_}^*&K>RcHuf%_GbX?ap(v(=Z6xtD-MqBj5M%og$pxuae3ULeC4QZzkKR~-a?G(0ApSV74$tRh1U23tDh?7`9i7_MiUfPR{EH?56^_vCo+q4BQq5Zj$uZ?_3{VlP`-;Jy$-bH()kr#}Nq7D?mQZ|BE^duwgjXY$eC3WKhc!-fU#81+e@g-yFFtO-8)CUXT<FwQGPMT7;CT>dHoVYpP@lYd!jbsyx9%v-S(O)6rqDBf67pJ|=$VW!jQg0x>W#qPz>x?P!dQ${<qRu3aVeH6Ha1?bh;`NLjX+!LF6v6LPZy~<U9R8rbNh~^__&W79>U?6+mx+fm?;g}03*b()#qTQPU8Q}QSo9?$MfjZ3pV71hm!(~jxCrfv<SG!CrCpqHijXT#T$)(8^0XtkEMrurEx0P}2(HMss*xA23bpWwEUQW!DNm%XX`~i?glk1Dd^*b#i6iAr$P3q>TKKLkODB$$cO);|U~1t9u&gU_q`U|D0ep`G$PZ<i*fPFk`x`}Fg198#Lka3A;?nHHQq-};#i+|r#}YfNTZlTEI8vu5bz$PtEGtf3l(;XSHG{epaVE<iq|PAj#IjWC2Z=kfEP_+nr%i}!QM<&oh^tZGLtKrxGIb^54CYpYx+d|1EUQjkgIKhTpLpV$v{PBfrLImK&vF@)<!B2|ATCENI*vGw`6W=_Q=shx>i7cXaeRMqe20;DDRv3!a>OoUMPeopOP%tJSDt-SiFKrIN$Lv3GH1&C@w<^5v;|+GeUWm5{COi6Sbm=RBFiH4&?VYe3zP}>8|_Q1dy(8Z+JeszpCi6N`wY3$M$VEK?qAfWiO<r`>{uu&F8Y7^_qhN51>~dn(?84EHUE5+Em(7oiS=Ix+suxIWj-_?TNDn6)nqr|{3otVsk{'

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
