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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_002.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_002.stl', 'source_sha256': '39e1078b9cb30af283f749c9f2e5012081bf3f5dc36254ad8db405c6bc18116d', 'input_faces': 348, 'input_vertices': 333, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5000000596046448, -0.20527885854244232, -0.08267569541931152], [-0.06487885862588882, 0.02961084246635437, 0.15580317378044128]]}
GEOMETRY_BASE85 = 'c$}r13s_EB+sAiga)?5MNq7)7CX91K!yaZd4%1+q5A{THoKiXDyb*Gk<P>AVmJpINjfu8#D8`U;CH17kltQH;@tU`F-~VUco_YJO>$|?sb*=gT_P^EI_qx~GYpuPzX2_uG<~9=lYbibHu*V~|g(Qh$DcMMKC;QKyHfeG|2cKE<%_M8`#XqBNb{p}{kTGV`Txp?$*W`dn{ti8L4ldr#4o*4;Z(sk}{+>P_zW!d5h2P(EX29eMKVYiotjQJEj$OKRang19*h#lo_ka9XyCMXgBpKpGEOvc2^{EiOVjd|}`|D{2`BL^uajhtproOp(u(;OEcZ#UWmx8nRnfP{IKZt8J;Idkkulz9lfQjFH7{w#`*{fCgy3j(ZuYbRV{hD5@sotHy@Tz=id-g#Szj<eBN4@5_qbgq?Zh4q~{;o0mW&KuAoL3xwH1SI(vA=6Q)mPp%LcdyZoIlqLtIAg*ZH|z>eUwhVbr9uETkP{Q`}f%|nzT$@8<w0QU;p+h`>_^*RBxI4IrcBJZ|Ozt=vR*Xh5G&Wtf@aY>@52y*^f#HpzD>rslK87kg@%F)X%_Hu@qPNUSpi=sQx*t4dPlY-_5?}x{%rrwvD6TE8od}*@_@>EoUAG71v66DEo=4mr(o#qc)rP=&!WyS8C^P-^Obl$I*D3xYn1iG0B^}zV>;_cllEGkGU?O`eg}W@s<7NB^xQu<2AR?@0BlMKkt%4_l*zUX5trSk#E@J70vB0HfcwTvWsDVA>u@Smij7mT|Ud$-^J9Q&=*1M`<Ujz!f}VVHoTdVj(N-dnpOJ@<@1fFNj??p#Bj?0n{g)NqI{UQlk)jyB>SIk@S%1Bu2VbGn~o;qs|#6sp7ZoE`%O5{Qs46v<H>JrI)6eNT%dT$Y%zaU&!PIacg+#ka+$eFe<dp$mGWQq=5gh5R2tgv;r_g2zotFU{~5WbsQuTO>=)IWOzrrdJI#Iu`$@=KTw<7spP0b@-W$;-zFh>3moCP6Gu`KPx{0qG3Zik8UdKMJoHs+rne*(QLj2~OA7#~8`uVFU_N~99_|=WxlppO?B>SNWv#9=%1!HO6z6xbuMc(Rfq5R0NmKodO_8Y&W{22c9M}8t{9n(#%#`*bE&%V~ogW{i&O1}Qj0ml4L{<XNgu&R7zZ(OvAZ##_hb2M;sRlam+Hs!}q+J$||ipE9x!Tr36ZxghZ>L+>nv)`J1-G-Uu&ssHt;xBE9e(`>xhPI`=DW#U|2Xo#uD|?<lrSH<X{p__o&rflFUKXTb{!o78$pcT)eP8CX-=r0f@3FGYRr%7vuGBB>We)p^uAH|EqqkM%D-l7IH|1pt`)V_q2g+1i%D?pTIN~(tJiPFvb;wW>&Ax%h%ecO2B@ygP8)lFnc!^Xk`H6i?j60rFr6d&fBUjPyPs%+({VoZDZ$)`l8VBy8c~!E+80Sce!#jrZBbCfX`(6~M+~6MNSu57FZ`**^x0A87PX3pFAdU7fwb%psNud1bw8U*y`P!c0{5%$qVc$A(4aH&BYAMaP;sI%xC)3Hl(~|ZjLs8o_%yY`KF1Q-+3q>Cyejaz-x~shJ6xo>MNAYy0{OF6!O~=ct5#>QHs&331=f7U^Pjp>W`iR@lrZ|<4$|#@ei%j;dz1XjNdpWiL;x2s7zf`nm0sFr{Lj06}ZKXf$v$_}O*{>NyaT<cV$Fctl`^Q{qf0x=FI!5#S`BAjb`B7>l|H%G9_M=u)ef85}Cukg>?`L04pmknywTodtl6~n;eX9RS?c?mLXg`Si)gX`em*+d#FADLd`khu$`}*gr*q5`$(>xnwf0Xq3GPFO(neyAEoa#%@ec3PEOZ%yEr6!%D{^_f`FVi{7@XUvO+rGRmopTPW%9r-pA7Otc^1%C=)~oAb>esU=CizslUpPtqdNv+$UhOAT>9z^}NaJ|%`o8=epRb+`gzq<n`YDf(CVl40zB!)9l|DSa&w3m4M)OK3cc62N?pY6${OFw9oucb!UC~Z9wIjLDJx=#8?1XuU`BtNh$Gxx(+SxFP@}_T2^IR*`ArG!|>AF*N6!ojHsmVARK8v9H>I<z*=8w|z4*a^0OrBHwjeH&{G-H3eg&$p8`>kOAeJc3|zZsO5?l%rnoCPn~FS<nMIwfH{jr)K3yB6`d7Zk8>>(A%3xa6>^d~I(U?_UKs*vEb<JC5H^_b)ilzPUNA59+wwW0dcLxYWw?U+H<B`l~BAk&5Sc3i<9~lz*w<u(4k=X`VREK0y6?x<A$AIdy4wn)3WK9PQZi`roC~dTQ_K7Q~rA`=Zk9Hm^@lH>Dz<6u;8yUL?i;bUE7L@s$@3r1QV-={)vBIsaO&!zPL+KY;z3Jb$#MB~;&#@5g>pF~zU7&E7|vKb?I`9$&5az!vtWvR|4->zbCBN8_dCd$V75iF{?}V17T!pTIuW0fX~I%BPw?hJCveG+u^?XkP#S_J1W`J@3rt?fkyRahy$gv%L{PdC2c$%o{z|hMws>UirPz-^;xIkLk<foBtX6IB#eecP-Bz^R1ZXr_}uN-uTMC>dN=+*oogW@>(PRku;9F2<K4hcV0uZ&+|lH5JK-q`n-A=M~v^!-_rY$oM*;9)(xfG5?W_;c@pC1`Kc}HOyecz{VRpX1@q?*9$)p3j1<f_+E>&bwK)%eoJ^@af277=(>`U$J)Bbcd6YU$<b5GmO)<%H)UCDbho_)le14dhO7Dqk?zWW5@k>^gbWYIcu4NzVjNIiZwJ+xev2TrY;JJ>J2VJg$e(`u|^Zog~GG~f09-jXeQ|UcO%bCPJ-mldw&O8ruCa|C6=S}T8wc`ED=ohu-`ME2I=BGYq2>Y=X^C`~gM1KFy`Nr6<NgVHJ+VA9?uMj`)`*PGf+F#_HFWASvqeX;AvoEucbH02a?udzRe80eXQkUam(qBXSLlnO*rx*K8>}kC)oCv0Kmz2|;{fK%zuETr$N<YtT&;AZ~id!2x?V^bv976kzJaQw|*RmavH(m$yj(zD|p=GybKkz-jhky5o+EKEbAkG9H-&YRw9<9%A$o~GA-K3+<E>WJd>tY^0r}L9xbT{~Q*xwRD<EnSttg&Cq*gnlerQLOkN0(iLeSMZY>0b`p+5an<uE#&5bH6sKnELg%KQo=aFX)GSc+tdny0ew;ckoL(=c`$n>|-6!T)Wb_NXdH0en>jqPYzoZPjO{EV1J@7trzm>I+xhL&A!Vp{(dxO7_BpM);0ETyjxH8zxj^(tIN8~zG}h!UGwdVcoUzWM|qGFouj0z)9jC0P0yP;_AuSo@FaqLYb$=Q_Zvv>_1cp?>`!jN`^T6;9OsiC**Bgaw%l4td3v&m{Z-9*o`hDT_b>gEHSEXQt)cvEX-j#KpR8aX`=)f-Dum*HqOfoLzJc{b_hcUX-@DR&Y#4c*=WV91F&_R-7;x?k`#$V@J)}G<V|R0ZGbbnGIpy`UdnuhO)XWL&FMqz3?zjFuzZYb>v41RX71a-IPW_TI2eR)rY!}s2ZTS3<Ie>kSc-n8YamANReB-{{Gwl%NDN|<O-<8e*((r%LeA5gL#yDv`(b`|8pR0xzn4h<3-<8IE!R;HY*`Irpo;!8b4mvl=hFWN+8NDYf-;X_Q;v2skbXrg6I@$2oL-GTTay&zOT<lZX4<AqSOj>u2-#0TdAL9A)pg8Sk@_8U5gMF_I%D;ZxEuKFax7nYydq2;|)BN0J#6QIIOY4K=V8=htILE&KHjc;5kLJH2{V4l*FOz+5^7owd-Rx_{(`X!LRwG}ZzLx!a?`Z#!7Wd}!Px>;%^N`PZ!)sAIa=OC4w*$?8ZOpVwTz>)k)^Fxh{bg=+o|n>Rqn!+DN8LJ>=DGS<&;Bu2I&Ubx=@gIh_*?dyyje)?&uq)%^7t$EFUPH;`4(s!%YHxheL7P6%0@Suhq}kk?3V@llfTH8`XxQ?hWZ<*zJBO;7uoN`zAkGR_rrzO14CLn<iFW)%CDb4uLEiJ7{}NA9F0n${HSRy*gq8)OzqEc<NZCYDf)~3v7tGwuS!}I_;&Oh$-Y-P4{0{=i>Fh)`R;uFNwdQEW(_BQjytt4r<Fe-f7)vr7sI+-numr*&)A=lK=V)UwvpzE^5`D>lRWr*HoPOxw?`M)pKe9<<-xV6zLpxnzS2{s-?!e*@2#m}?8mOA^ODlQnZAqaQ`fWaF^`^i!%#ndUQ(Bt_{#FNG*5J?3lL8{$FnJdzkjAoV1HaZ??>O}Q#^7?U-n18;O{Am-D!N)<mT*;T*~YDU<cj@ldag7K5b4~V>`Xy$;ovPzr`YoAK!=NWDEAkPT}vTYdZ6HgXFjO={oW~ofEXcwmdEmudyHfp7-mZ5}yALkFg&fL;2EgxX$0tA1s3Zp3g%|mh=345WxPX-V}#!?Gpapa(@E*Vb94|e8Tv-xc~Wm%o9(F=g$OMr?q=6*$?hb`;N9Em*SD{eZYRyYJTpD&(iyd;cm`7^2fa9yzT4C-<|Fzvmf=G`X!Gqr~OyCdx!n)OXwV;c}LK99{t^`?2q#0afw-Ul<s?1V}E@*#iRJS@%Q%IdiEpTD4)8ZH2V9Oa(e{(vtl;VedqK)%l<Hvcr^U|NO${l_IJckJbHaKeos%bXFte?&Q;1Zw^Qu5U_T;+=Bpetlj2m98nZ85{etT6enHQ%oMg`a79JNRAe#POrrt`ui+u8VWA)MHbpKmd*bnc`<GwjEit=zPp8X^j+Sm0nu2VdQn}^vCsz-53p6&R1+Rb(Bhu);~l5}`IpRa!RU_W>l=W~tIe!Bnf-@(7h{S7!paq50|VL#D@*H4d|$4z{7{Br(1{@$+LuxEckZ`wEYk)^bcOE+HKVV}>js#3a_;{WX#`$c85NHg~Ecah(6+28I;?`zT{Puf@YzujOze9<zB=ZMQu_OG*lBRqtEe(w;)c|DMQEsf4gN^<N@_UD-R($Xy)&$SustKmEzXB@Y(KZX6MG}^C~(02#e_h!E=Hh`Xo9pQ9e_1ZZ0ll*8M)*=)6{q))h_VGPgjTlY7{@P%~(`*8bcVOWj9>=3+sokD!uG7zdZb|c8Kez?^oBNZmKB~97D&JrpNApLw-s23#-7q1M{8(;ByM3F!i|CW`$yd<MKYb1D=<7EiUm7w!fqb+hjSAxT-Gl4Mm(h+AcA3B1Ia*#NMSVG~JNeqO_T)>(`!=1&@2O@nmnk09*L&vEdzf?~iF_@U>#Mmx@q1F3|0Sv~{2?ZP_3!`DvE5156(dnmYDqSdw`Zk4`3sYV30n1^{HJyO-~GwItMmW&PyQ(tF+8a#g(!kcpn2dD@LT9}@LO;VGuA)Bq6oHtz5xq0H)9q>uqCt(*b>|TS`XX+Yy)iwwgESSHUT#R>!8iSI&d2l!S>K*V4*F*_TaWqJFw8!;I`m)(3aqK;0{nnu+WZRp<Tcoz&)V7z@I|9qX>3^_5!<r`#?Vf3v~ty?Fkn8Ik*qFH;UkH(5~Qa;E$o5z(O6sAA_4hKLR%e*N0kzh1LYu2iHOoEJ5E%%tD`nMG^cAMerZcEbt%TOlTTd=yh-=I0+gLP6A(no&a9~pMxF*p93F(MuLxk51<GRhi(UlgMWao1^)n6pi99Dcs6taSm+$EP#>_+nc&&rsnF@*sbFvD_h4`EH0V6=G;jcl;3d!%V4>^5OTfV>f<vKOz@gxupu53BqrpFcqfi7NgPsNpy$U`Cz6gB?z6ef+-U26s@1Y2efgS?KfcHc9g7<^BLN|eh&IfM=FM>`1F9Oei>cKO>p3v{Wp5PJC{@@W{R}{g$pgqC8z#X9-z#YMkPzSIh*bdqTEVMaTs4ZCNM_@Z}W2im2F}O9fJ-9Xa6X<8)PryA;1owk}2^Km8+z;%AB6uux9C$2vB6Jd1=yLEx@G=y^A<zwAp(;28ya##;ya)UX^f>qz@XsiMcR<6yJHV@;LEu$jKd3KQ=xDGXcqDWXcqDiLv^RJFScY~6%iyk19k?sF1&ZK$P)l$<aBXN!aBc7hP;>AHU<q0cEYu7vv^rR54e3As1Y1CBfi1vwpmo7@z*f+fU@LGd6v5q~UBE*7fV+XeKoL9;Iv6|<JPJAnEOZul6xbg{@M`Evu+VMb)!-kYC&530&!PxE1C0fr0q=zF0`CN`fvy9u0WX9u1`G87F9f?ohlAb0!=T@Qhk?I_eh&T`>;mlsb^(8iBDgK|V{lur4YU#125b$j54Hw3gf;*R{SYj)30P=Ta6@o2XghE-uoJX9*a_?m?F)7We}y7=DD+#f(DC4*;0Y*#Cquo!lfi+|xnQ9i!GYk-D1!GvBfvrrgZF`tLhpc&f>WWn;8gGn6v3~cMPQ+?!LPvoLJ?fujMdDHS?FKztAneVaS>cDv6g|$!KKh*a49$+ngbU47@QAIhu#OLgC9VD13v)YgkA>U1SdkzgA>6Tir@>-IPeAVCFrl<OW@nk1hCK>V4-)xLLY%|gALGZumM~EEd&>UUqVa3FTw9o1b<-0`W7ryyc2$aBDgk+;JQ!?a9yw!)DkST0oV%sA&TI}P#dt&M&QO^Tc{3f3vLB%18xQW#Ejp+ggQanfQ8zFoxts(ZNWm@frWMew+DBI_5d5-_c}wJ!0n;p`uB=_W>l1G6{Ua0b-#-86^h`#D1zmR@&)uuXg~0mU{`2=uq$`~^lR_{@F3_w@F4KuiZW!7Sv8yL|I_~h@t=Q+nfPzz{~_X^ziIjzrSfmSs%Y!)k19h3)ez@}io-!QI_#K<ok03G1g;ST'

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
