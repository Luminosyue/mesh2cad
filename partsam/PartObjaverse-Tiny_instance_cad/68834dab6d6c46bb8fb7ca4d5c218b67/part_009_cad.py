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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_009.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_009.stl', 'source_sha256': 'c80da52f95539bfe3b185d3539da3a6c16d8cd530a0dc400450b359e99f3c824', 'input_faces': 360, 'input_vertices': 236, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3436862826347351, -0.45629191398620605, -0.49999961256980896], [2.3558735847473145e-05, 0.45629990100860596, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r02UJvNw}uaB;%`i16k?5WP$T;5Z({k429;w25m8VPJA;5FA~qD!YaES=QBh-y-LXroV8sFluwg;K3JMGg2m<zKG?qJOzpoMQx_7O+?q#iSz0Y}P&;IsT&NpXf;ptwkyuE@y2W8p#PimQ~DT>}cRqU0?ffGVT`3FvH7CbJ@M)^W~{qMal>*?*`IlxAltW0wZ2%P9Y!SM%!W4qyP9Ge;(hmV~QGQls{ckG0KK;3uo3z`^c^(T(>8y9H3Zq%Y>>!ya5jhh;#8~%@fpIA%Kp1r*mXI0bq=BJ!>_1?N&uAddb4-QMzePzJ&!}_)1Stk53b;LIhn6g}6f0hh?>@LK6he#gt(<9<5V{F9NeAY-F<I_m^qazZe-$6$ukMZda<Qe5GzB;K|tmJtz1@Y0XPe}eD_Yceao{WJ%A~Ig$Ll;TB;mIK633L|U<WeC);+}XQe(bU`by^;GhaZ)8T=y+L#}3K(9=AfCpodbA)-PD<H$QF(|Hm-#m3~u}N&Sx-z+dliS^Ay0;iS~__$&AUIhy#LD#XLDf`0e^F8!)LbJ6dk=U2rKZxJQ^c23pG_$%BlNxXmg-=&^M&)}aJ7>hh^XQaPJPsKOQpK)I5oNbvRbw0Wef5cjuA8k?xnYX|F4dGJ1Iwg&M9{gojF6zF)wF&0)(M9w-H-Ep3t7B)>`S2+GfNZ%|I%R6|{)dt957#>>`MqOKOa6yD;Ky~3lX#agQkU`JR`k2PqKsE@+avv|54XTy_*lke>EkDPl!p<>GbcgnQ93$E|CR^y;IF@qeKT_7dBo3!KR8L&&)n;-><jh5Q2LSLYaSl-`=j3_wPhYOufkKZe@eO|{zx+!m$7feY51=27kOWhe#eiSC-szcr2jS=>viEYd=>ucJF*Y7z>*|c-;(d(+t%49c|x{al6fnsTc&=k$G@abLrD$zGY*`Uc^KXCg6y}FYT~PIPci<!p_sRl${3gXVu@2-of8oMnfRJV^@|c0IyV;am5|3XUVL?6iz71L;tGiGv-%S5Z~NVHU0j}ZMqQTibeV0I@fO=4en55cl>tj;$vBGNT#<VG>dN}5Ze8U*GZ#M+UrFq<S@QJ$1?N_A3H;X~doa)0QkSW?P<+jGfsEJWl`iXLEY3yznpZN<O5n*P_;=xtOJ5~*Obe5`)Z#4UajPuzV|00k`?oj)@jX_HZ<<su7V$U4S9>~R-rk>|#n&*d0hJ`L<)<1OWW9>7BEOfN%$sR+`Q3=Wg8bfvn9nYamWdXpAiqy|vRwE4!X)!ql!SQg_$JBY`6dzmIry{u&&jxgBBfqSQ9S&Bq!m)fun2kGShSh*&{pO_ow7puF%+$Y|7+R-i5s~7jLcur0{F4h&~LA7oUcXm;0Im6`e~z5<n{Zb;lFB!^%}QH=E->9559dvnJ?9=y{xa{et-D6MRML5;+IGsOQ8$qGh<DfjBCpCSomF8e<A7*^^^Lw!gh!c4#ekId{hejw(#xJ4oSbgqU3c`VH4z8yb1TO@1vh(+=X=!KP(LATelbZ{3-kj@fkCv9#e;Ma_*^xwc)2t+m89JoFwBatO-BwxQxpf_jL;5Yrx;QTFzm!8X<WMg;hD9FMpFd0(~WqR`4!O#*wjG`c+(-May-;Tk)01v>3^A{uSa1pr)$ZWxU3ozhOQKp2J^NE?M%pH%XM&3-Xa?dGJB$cYqJpz2H3jmA-O5n|fEoxpyy#_3Xhsgv{G0*Y{2!KF3MMYl*eRez><A{_ds6WL_@zm2n#HnZ;KfL-Bdj6VD^+y$y)3y%*=sup_c>E%|d%fBiAIKTo-*O27G`$kVVn^7Qxv&mH+=kSC<^8W~qW?Iidk;iviIIc7vA{Sol52W^${U$MjIcYaUgPw$WMdK_ILb>+EY9_mk&denpr?6<r&tfw~X$wobSO;CUM0jz6qOWYTEb<wYDpqyg{x0nR@U&GIDwNu7_#YO5-^J*c#Tam<DoQGil<k=(M-52M4P}XtypTYOYhVT7E_Jt+a7I`{{;e2#IE_GURZ7?pcCOEH#-&~9M*QvPw7f9XO*miql{&HW4uk_u9bF7VJ68xuFAMeUI$3pl2BKt761io|FImvf=TWVY>-&AY6th+iq0_&1nD85?XN9NfQAB+1a_XgrSHA%vJbd>rHxvB8Kog|+Jn%|gn@KaFdWv6Y@-|$GuZ@#-1`JJarJ?6w#a&5T#8|v&>Me-|dO^~0yX=19JU+O6z)PH9z@~7Y3A@94@<A%iD@k4y|EIIc~f&S93ddCy-&i>M`npj<~Ejccz=lY^l8GqOQ%S!vE>r2Hqcd9P)q1@?;I{SHJp3hd6^)u!;z>iAAzI0iQ=dPSu==Zx7GCzjE&N#1fK7r5YRpqk1e12OjHt2Vt$7QV7Zq#Xci@aVAvhIeFpULx@W_g{0ee1MK#*w*G=0USO6W<uMAMfk(CC*jLHJlUwo{Hy>%(aNmjuzh#wFT?l#Rm0f^Lk)=smE}75#}p<CHno=OU9)JRL4ALFNQyRvOG7MuZH5j&YlPV=DMvI|IVAzZ&n!V?;`h|!Qv~vIcpN?^r(X8kI{E!yymR&@LM&*^FdaT)Njb@jyk^&l;?FzW*Wwo>4f|#yRZ*);w8T^(*g5xxT36|IiSAOuVj9T_}BJ(rJjsi*QLLh60Ap$R6L*jcmUr6VlKgN?IisgvK=J<dtb@2i$uQ~#(VS#eAhvEj>>w4eS35h{E}`rByYD-cs@TeiqB0o#J9NJ72kAZ5d5SAQlEK7vOMo=hh8S*{wzfPY-j1$bm*!0rsy{^KJ(dP?Ds>3@RKe|9>cU~`QD=(N`+rCPWsh+Hy@Sj1OCXLbb|4VB;FL=7|#VI^CjLiYAg0*v;+KoE?A$lH_`9@JvhITA7K1L7s&IqX`es*xH@>wJu_3{m3>`tJ{C7YJwEoh@Au-|)RL>oIMpFu$g|f`e05&~tn-<}=y%T_I8XCT*JQuCx0lalbypueUuK+={izj4+>+~EuJ8*&WPh5AdWdg|yeIoWdD}(yiSb^G49UAQ27YQe`MfifY?pX-C!TAS!d};<j=qECb!|JoPbit4BeBjCC0^T_h|ilV{^|01VseVqwb=>ldUc`rTEbEI=C~y6(_^xq4VnG04(s#IVV_sR=gjTyn7?%~I0sK3!1w9&FsVyhU2<0Z!}oDM-L8rKxY9;^L;B$i)KyOA&#*jP_Pv&#Exvjs>#EGt(kAd<{+uE6>^Voy3DeTL@c(p$-}|Nb%3^1E-qBtqif;;eAm8`R5jlAMQN^25N1v7wXIL1H?;mkL$UZSVe0)n@Ul@jd{(32SEG|Rk`Au2iggp5{IA@+0WWsL?KjSver5FFqlK0QA3;%6joCA+{-<JO7e~Hhz^VMYET8h4uevQAR%05zFEtGzhsk!?kZr(2OwG)fvIn4YZS>ny}wj`F`C&m|@&~Nx4_?b?!9}Lg`%7pJDz9sV^_GSLYbXl)CC2}5^vudKgym8_i<|N|$I58Iemdr-Kvp3>7>G@iTQzjqWE7uRB@%vDso9qYUn`znd`u$<D4w|+|=GpjK6<;l|Jz4s`Gre4xCF_>i{g_<m+(JE1pWT-DTd^@Ro;wQW{mDM~=?!CWzc<4D{%0e}qiEN$ZZ<t7PV3_<>u!omfUnqzZ}d(r<D1I8MBd&%$a9w|HduVscCGm44wdEkO*y_YO6s?nFTTZf1M(hfxL@=|3g*YBIez~MxFqwWzTG18XzKbo@(yc{`OBUdiTRn8E%APD_F#SOu)c53i?8|4fqyd>`|Zs>#QRQ%pC5qd&%c7<5A}xsHURtZg<}@RfAG%^y4-Dv`TS#WrgJG@y;Dhi%O6|I_{Pg!WxXtaeVtv}H=GK>^X|KMWqdXMAbwYPv!#r$#o_lG^UF0^rTxG6?VBUnW$H}1E1$o{x9`gO84b3{c;Dod^$XVFynVf~tglR$c`(25DKih+i;r<`^j~qNO#Hhn+@CJpqf7fHrKzmD!N;{sylOKN`^5Xk=`!)Q$FSeJrIpE}*`CM#boSE9#FuY{dG9m)P@HF(U$<`+)U9c(Vohaj6%~7BxL>KCwslkgd$0ffPurtf{jYx7ZrS>~|L;%R^{h2iwzmG%n&i9IcGKE&*>p~)o*<`_W2uqkSn}`G2=edbWz>=6W#k2HI?tjGBJ0|nJc}I0rt@&BGg;Sq<a!*F&K0e#j<wlY+YD<PZ*9M^>AZwGl)Qu-PIV=Rlc!Q!lkZqtj<wyOUMJrmpQI*`Pm*_1cae9J7gB#EFC-76P9;xe4a3-U?n`wf>spuGm)wO-=f+e!vK{A2=U=StKdkL%Hl0JM6Um|E0O~+;0NIo3M)o9kWYf7NwJTZIf0J918?xzKi&~$oYfZAQmC5>ASUC5(UL#*8Cr}f~3FKYWJ>*^FU#Tm}zmlg?=a8q8_5HF|!9H6-T|!<#UQ7)qhx5IQxeoQX7W%!Z@3WiK8|0hh6V#LB6XZzhPI4qUg1V3#K^{pRMjlBXMD0r+MD9-QLhep>rZy%w=2)D$J{7q}`u(Wyt?|@Q@_6!4Y5;jC*_G-^b|tr_b|kkZJ5pPc9m#d64as%McGOzrTCCZQTAAxpnd7R%`e$&>XK=lB{)e@FWo=(l`<3Eqyw=r=e9zkQtnD)O3R#co$v7|aPt?`qpU69?N60(KG1SZC%gi6cnm%Q{{~(vAenKu!E=T>0T#oz^^$YSx<Vw`9$(6`8sEx=q$PU!bWCwBwsyDd<*_|3lb|?E%r;vTgA=b9h+SXg!JnCHXT)sY!I)$vSS9Pv~uAh^uk@a;b;QA#~FO!qWhp9)%hsmp`tI4a#-KaguJ=s?`uF=P=>tojR700rM<M^0yHq`QD8?r(zr+oO+*_Qed*_K>^T8UhNT!mVLT!n0)I*<+I7Ss;p7GxKyJK2RinCeR&Ob()kkb}r3>Rj?%&WVYt&(UV;Hu7fjUg|#bUh+ZeA@V`;De7tRDe?vCMe+smEoufi-`WbT?J6~mtgA-8N<K^7N<K^8P4y@5CQrAv9@GX@e{v712emobgX}}?MD`&YslCZY@?@$Xc`|t#bpm-Bc|LU}c|LhLbrD(DP2}a|?bImpcJcvgJoy0m3^j>-hJ4A|vZ-0rByy&;owK&v)br%q<Xdd#xwg8-DIeBa=Tp>Z<-^|4`5<+R@?kIOyqCIE`LOqN*7xQbs)@Rktp8P2a8K)JfPT+^PPHN1Fy?bMox4%{kh_srQ8y?b&LW);Q;#Yi&Muvksj13`vrgv%Hl6QVTM;#dno3R~AEzEAA19ls8^~tz0BRrd0J1%`D!D4>=>69<Te3a5Hnjq|Hu)QB74kP^m1-cX<X+Sk<X+?<R2T9P@+9hD@+9(XY7kjh6Is`#WL>wAXOq`aqsi;Y`>Ao{{p4fR^JHDmk@fwb#cN%Y$mhs<jDB9}>zYPQA*Ycw>T$A0-byu-x03y-1IYg522^`;19Ed}ZE|yRC+aukPUPNHmE4=`N9{%SBTt|XAx|LBq)sBwBrl@QCNCmyqOK!vB1cj8lcUJ-)MMmhoO7K=SX(P=8%6z|Jc|4ywGH`4@@Q&X@@R4})rlNT9z$(M9zz~WZBHIc9!LFw{4M!A*7;A?rE3%N_vALzrsOu{w$y)-+mfBA&B#t<y)I988(aHw|I@!7e)u!#hhmw3MEtMsEc>%g>33#XbN&4zkEi=b`dMo|L~P}YOPK!Ts{AKa0Tog'

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
