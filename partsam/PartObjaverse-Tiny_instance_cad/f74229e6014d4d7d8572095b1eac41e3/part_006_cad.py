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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_006.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_006.stl', 'source_sha256': '69c42024bc1ef78d2c9885c42fddcef0def5630621b600edec8a8d7690f322af', 'input_faces': 456, 'input_vertices': 296, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15511810779571533, -0.18718427419662476, -0.3759690523147583], [0.13708114624023438, -0.0661592185497284, 0.23603026568889618]]}
GEOMETRY_BASE85 = 'c$}r12Xqxx8prQ51PDn;Sb`w+AtmTiq$2`(2v%0iE+PvnngBs53MPO`^MUjLf~a%}H6+voA=K~)MWt8i5IRT`qzM6bzWM%lnD@QebN1}A=kEV^fA5<+cV_O)yz_F5Z4s0&O7Xw)>e`88Wj&>pq86s2RG);zUR^pSBvt>U=NB#&X?psnb3)73Z^gECsXnS-bf<)*j)~C?-O-IYH;At4j_%weu~%aJCm-}k?36(M)%fm735HMlD86Tc(XUeL#d=lUwV$i%9^n2T{}rM+TspFGy%BNqnrxx;<-dGzy@U6zt28;r=6yjyo1N;lm-U{RZ8tjAYcK0l9+k;)s@GoDtEBNhr+V!J=AW`4+j0Kz0pkx$T;n)CysY=`%UkJGuf4AKrd8(s_G`oEIXB|adMBS9I>}z|9iF?~sowIaS4YdUPrdz<y*|K;dUc@Y7N>g4qu$f|n;fU>E4@Bm?dA2AUe?R&E4{3j*H`+0@x}F(Ue?R&E4{TI4tCh!bbSN7KL7CY`UZHt9zI)`Y<}J*{YTUP++sWV+;(ZE_jX@wdf)UnP46i`oBiNS)2nuGnBLoVDv#57h3VsJyl#45uW{`AujcXdy~g#fA?)L_O`q#~h4=euFZRuIc>M31bA79h?5k`sy{B6<)2q~2_F-Fje9y~Vf4m|4>>cc@H|6;Zt-!wL9zL!h4<A>N5I(MF5Ab|$G+|%(>L{~*_9326Ze!l>fL-h>95cOpXCtm}ztr^J*(Z6PYhU91y2o<;&C~2RHss@N-IeP-=h<(4k?ZrCvu}Ti{hkKA-(qEXoW57sAF9vwk+(*gKH)n1d-ZreVO!b9-sE|fV6QGuGrc$DHXm<nUG`ghu+O>6zGofwqholS68HIh=G122GJ@-8<newV)Z+OJIzGaz-}s2n+gt2abUOPB%3OyjSvA==>1}#%p&--8g|PR%<Kg;k`AnZX`UO63Eeo<w&d>FCYw&eHxM#RI&NBtMzAt-Evq`2`eL}dtIO-e6asA#xruQwY&igG{iT%S+)4OBYdxu>fX8Jo}d>;j~SDlu!Ul-2DwXYh_Gc(EbYG`4e&rJ62aSgb>WW;h_kMJiS3^n@$*}L1Y_f%hRdhZhUo+hY&uQmHq?Bgn-K7Dm^jDz>~uQ)o!VH|I@c+<=MdQVK}dNEIr>oC{r;~D{<S!_&<!+G%Sk7X~<TbEJn<#|rt%wAj<&-jO?54et%>W__ay6)3IHoaUYYW7_AVqK}xM|d2u4!yl2zK(HPx4U0vFV?wtS})Vf`$8R=!}a1m@{~Bh_2Rzsm3ECYy|_=^i;A0G-q&$Us<Ic)fs~A<?8S2<u2O3rUp{B{e#l-tmr}C6;Bmxr%y(cE*Nf+#H(?6b%jabEH1^`Tnp-1_#}Uur+%B8AUOcyRi|uAFp7Sa9kFXc-h1}S)?8SQ|_v97!;=SWby~SR<r@W``vls6*Un@1<^zuDeKcDI4do$&o0_??m)_1xfk0aj8Dm{e#yR-Rx2DkL{-d)$1n)@x%eTTVDiu9jt`o4<mH*9hAagFQkG}ptUiR`D0^{baYpuSn+GRJy&UGIs!%)Wl{<@S2%1L{*RWjfZwTlF87nd5Z4(tB&3<$1QO$Ntzr|Kk-tpx!ljnPWY?uFuW-lzsGfe#a}lp1<}gt6Qd1z4p4^ck@dgr`<ij`Ae_oqrDnZaG6uR_PXAac9(s(kNmHf@Uq^UG%3@mUVB~d-ClXFInED3E9~{s>*Lkl>v@>rRIj~te)ddaKXt3${H3?fkM_;#WjfZwTk~HPG|$W`@B7bRcx(RfYQ?M!r+V$J`PXXC<J2hSH@@`N{NdG-a~V$c+Ut7vl*jD*&-5E#dOaWQy&XQtaH`kdI^I@|Q_XQg+xVX!;jQxt@7<S{;Z(1^u2=ga=bIV4&2N0^^?bDV9<H0=RIj~N|Mm+!&hdW!;|p)i2j1%%n&DKhz4d(XR7*4cgF}AfOK&|Nw2vL(Tn{hDS7SfVaH`inp#Ds>b3MFueuAG*cRWABTjvKp;QR=0)em|j-SPSgZ_Nij;Q9)$>r+&j1y1WzdOaWQ<@%J~n*Zu{3!LsR>8<(0%lk`u>wQ=LA$#$BkluPe!^`J`^w#}2<=us5%IBN#*8L72@O%^An*ZPpJdSuiOK;6zd+~gh-kSgL+KbHn%J+-#*8JfE-Y>#i&*$_GJdSujN^d=%;pO{Ldh2-OkFXc-cj;xle7{R?)la*~<B0Dk(p%RHUVcB3-a0?Q6&IW1i0@a@Tjxi6@%>7AtNuzO)2mMY-}j`q>YMf8am4pe>8<%|FTQ_DZ`HTXVK2TvOCL}#zCTNEJs+B#a6De=t@lNfrrDG!8Snf3ei-2Kd!Y7e%<s#c>MgH-zwO@4N9hi0%;U_<<KHu-7xlg_uFX#MmKXJEPW(ovddrLYl%17xoa!wv>f;V3`<&`6FXz)WCEIa6+RJ+VJFu+RUesH^1B-gg>)(50&iS0KZ-5u|^7;mNU4QHv?^pi*FTJP_`2AmcU7wr0!D;;jcu_CcPk<Noa{UB&Q7_j|fEV?0{RDV9AF+M{ysQ`NC%}t(xqbpX)yMk%_3^}?pAE?^Mn9=26{4b4=Xl$n9!Z+RAf5m8*rm>Y^{2-=b^q@_Jq8(ba2f3>qym>PT1lhjL*@qu8?AuRo<WuZ2P5+#OW3#+`lT?I<^t#!!1$Vj(GSKL#PpZivPLV2ECdcQTBy;=Aj^S6kOh&YZCnohau`c<DEgroUvmihAsB<$ZM0_<{dt+QFgV<35#}=BtN;#2h9TWHu7G|8jHNjO{RoV&IUN0Pj6qz&xOgR9d=V+10=tYBWVC0HrNAzvLYA;`DfCNWEX_ga2Vs28F7#a(gSfQO${H;nGCw%jXa$T`23ZaqjLe5DZR2w2m%~_^3!q;B<7*B^KNw>WyN&j&(F!69fkTWIYP9mm3g8fAL8RNp70|DMu{4LGAByochoB#VF^DT0r>dgSqLG!rkw*KA(TX68f-51TkwtCWM&k2GTWw`*UlAE;+h0+9UKF31wZ@zxjaC#{1e|Al_Q+@tk&nUjIb~7gWA$X)Jba#KtEKU2`$%M-da}RA*#BefgZOD9pEk0%PH>cw^r$VS6HK2MLk%T)y=@dek8(Y!rSYTm=NMP-kG6dp83nFL*UV^P$im=oqeU345;7VbjtoOqv~e{0(HKi}1o{yeUvoJ6;TVJXhB2qBM!SwY2fhxzfIJ1h06v2}3_b%sirfP}3f_nO1-uWu4Y>il4ZIP#2D}lx4!In>4xEKt1kM64LCys)0jHu7&p=KGQ+@}Y0iK8)51t5~fE)>)08U0D9&WS;M*GufchQLdK;8!b0ltL1488<DjywrI4nBZ92tEMbf!qb&0p5)K3A`D+3b`IkxeUAtoPkE1hFk!qoDEI`&qPiI&je3Kehr=s9)lbT9s~XgISBj}_)9e60gBh>dBy9O@*0?~=`>tJ%5TBfQF8<NJNP@)j7N?G-$2b(<Q4FE)Qm)q0AEGTIpkUJNYo5R4g;S<%_(FqcsOd3k)yz;P;(f02%L<X3CM52hf%W!xf?tIH4~BFgZH537v#@iy6@I1zAq_rz!S0U4CD{sU$E^4q)$D$&uQCj$gSWR*fte854-`}u0gH_Z^O3xkbA+Y*menWF?bEOU5@+_ybs$RMIHe!!M0h*73#?|hqhgWTnIjjZO<T2gR`*hI^<gLB5XSsIR|_O+g?DP2XDdo%0{jQ@5J$MLFRye#qsP!ZUvvf{C-951^<Tqoj@J|-@+VzL!JiTQ+)s2LY@cTSA3t`LtX>lQG7q#NB$1Jsd(MrL0$o0RJ^`#BF}=4DPG4Hk-6agir4Eg<RS2O#p`cBayNLB;`Ov0`7?N>;`Ol!=>soSe7#p9SA*x{`YlEN2u{H@osV1yo}~DBl!BZC9<BJfGYL5jJXrDbWi;|z@Ib}Sk-^Au;QorA7Xy(az+T1Ah5pE4;310de=l+rc&y_4c?j|w@D#=O=UC+T;8}|Aw<*XU!0C$bpIOLx;7rB$LppLXnAY@Ke7+W+5!1WrCwxx1#m2kPr`!pii*q|2ISouT2T@1)tBp^hPkF+|m(i#E&BnLUr@Uq3KhdYWXX6LxQ{K1nUGypM*!U0hDR0{N68e-EZG0Sk%40S@fIj7Z8}C4$a=VQ;qffcX#;ee$TxsJB^eLCxI1PQu`8J-3K4prHC!<d}$;M;QryOnLuh6F)Y~wG{ryOYG0q9fqxA7qKDZMrxiazBK8-I;H<yad}MW1qtjc21zIm^Zi(5Fnd@iO!&Gi|(HJ-HXM!F`SPh0*#UKL=BO2Bz!-rtA&wg`|Fx%_V}9z@MT|*%RCYN&Qc3?qe{y?qG7=z~s7u$#nsD1%HG-<%i(TNa`opTqiKOj$m>fz~th=<l?~OJ^;so-$$RaJ@`E&_5Wpa?ZD*Pg30|8+!ovhead&il&!(<AgSNV=KcXD_jfS4STMP_!Q@(k$-M<8_ct)P7GQF3g2}xBCigm++-qQRuY$?F0w&iSOs*N2+{<8cO~K?m;HKah^eLNw8zZUT$mU)GlWPbj_ac~F12DPzU~=`q<m!US)d7>M4JKC$Os*!F+zViGHNfPmgUM9`ldB3Q_g65v=fUKj1Cy%)CKubn^;A^QfBH{Tp8WH==>P5ip^Dtn|7T_UmIIBktRI<UTLjbZrRpi;e{`cyrXyDW1`ajmbN'

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
