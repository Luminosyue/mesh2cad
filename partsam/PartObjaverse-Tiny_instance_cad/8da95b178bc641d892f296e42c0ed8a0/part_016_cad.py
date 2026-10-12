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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_016.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_016.stl', 'source_sha256': 'b7b0828895b7a70e06784b7ee7c4b9cb8a89199bb0ebe2637d646281782ac146', 'input_faces': 416, 'input_vertices': 267, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44480371475219727, -0.19110876321792603, -0.3922714591026306], [0.36604851484298706, 0.4759441018104553, 0.3157866597175598]]}
GEOMETRY_BASE85 = 'c$}r033N@@8plseHMOSJD~jtGLTjigp_Hpiiy#C=f@?_3L_);aLk&Sy+n8xw#2krCLXdkhh$aydiHNbcYIxK<HZ}B}{eAzPo*Q{<z4e~8zW#srclX`*oW0LE``nYd_bOTHU4{SEQ<hX+6BtxOQAAZ#-c<s;{icr}?d{)uitj8Zr80T(PiAnRfxX>_I4J?j9Op6K{-gbzKQTFX^l9hZ)a2|l)o;4r$SEVH`i=1xzWc~Y{@%LxA2-t1TYufSm5XarQ|l&8P4i6u<G=D^8}`n;WYfd!>6X-)HtKnM@mg8yOWqoIoPE#NyNup0ef;KKBGr>q*}rO(Ox}7s&SvnI*YJ6V<EVZ9K<+=UdkXohYZJ*|>%iVM=eT%nKJR{l-al80`^nFu*Xs2)C+Yp*Qx}Cdb@ERmUv+i5NUeqk`$xZ1JFU8jKNk>qf%fCAa@pj=z4&{5wwxDUa~qgL-`634w;x{V4L`LTZ~xTa@~M5o<y`W8#?tt_;SZIj@iFh(%)Vd1Ssv#<c$|Cp$fI#{@5AHseds>we|>fGmX<E;OS}_C^ORGWymf8>`x(!UP(Ks<pQYS7@EC1}ZFUyr+z)c;bC-MMQ~OZYy_7j+$!qg-*eeCRJ=)V8@&(^>Kbc$7C|jIjzi}zIKX_~}wO>+jhQ=A+Yff68P1(3Hd8NG<dF8<V4C?1#De~HP`8M*q^VS=^D!p6H^)x@7gQ!1c6?~&lqihCmmhDr@N71-Nx5zSnuR1Uw(`N8i7x)IlGHG7+S0it(S~-zE*P!BRTXFv9zQMHL{S!`+m*e~*nYVjhTk;m!e)G*Rqc=%EWmy<)XYE?#Rk>f2Ca2g8-oBE(xx)ZHKPGylQ$KP%+bue6Gx);&dTZioYQNwC&6}y9F`W-;<`e2y*)oa!+?}-lN{{8d{ZR!c==(fF`8Yr1!Q<u^no9dM=h|`l{J0j&jovK%p@Tv6xfi48wJQCM_-!_WFKi$0wT-rGQ-$Nk@znPJmBa7%<nfT>mf@FR^osPcT@&bg%cUjJ=R+RyYk3_Dn?YWw7N6+g_e>yfz4}-q-!4Af=#}5#cMcAxO#6zw>Gdjy>!iAU0DIrJ*?Y}QFnSGM{joc3m%6J(l5rlj=yX0_o75$5_pZd}^|yDzjo#z~|8hBPj~ZN+z2|K9SIX1;6?!lDS&veU?d|LB?Ee{^U~F&M06%ykk6(8u$M&UW@b<u)WP9Igyggl?(R^4lBKdgDP`Q72(@FS}?%aPTJGY;Bo4k6gHf?{QpTyogq%>c*J(Jjb#L~K;2IbT7SLg?@*XnD$za<xww}*Ptx}b%&<m(~4X(xM=U&AbFA3ct|#ru6aU(7>4;`Z=XANHzqU23m9>&^XqnaRHCZ9X62Ej`#PC$i~$RP%E+YQOarop<WXU38pFZ{5aTN#8{0pE@psyv3*eDe}#K;P&wLvFt4`7V-JIBANT&;7?u+d&1XWc<V;?)>;2LL+!`4A+HRmN$a3uUdY#3cn#k4b^xXNv@Usb_E3K9lSl2PSI)3k+N5(%Oy&7McapbnLp)!9;FWy#YU^#he_7kfYX>Uvx|ukF#}i(Sg!lS_uWz1D`Fba>Cx;`WZ3b_We%r!mYM(poD80U(bB<o$$>-w@UX^}{#`hcVw&V8YYSVhBR`LJYX7DP!wr}Xq)PD4;c-sET_6yX0Y9qcr!JDhVmwSh=L#-{`-plnOy^h+(?cvSC*qhy!qkXHx^!|$`m+5ud{R6h*{Hufml)(jusQ(?`v2Qy&(pH=w*CUd*Kb^e!{ss2(ejsoKx4+iyii7Vzo$ik;avj{YJD11%n}g*0w&C&8Uiua5-7EM~f6sr5rSH8Ld6fId^*Megc~!Q@x+8sIKXTo9<U-zBbHC=$kE=8H(|(_g{Ft0@qc?v7pEZrI^UYqwkpJ*L_fvf-AFuFsc(wN+zK%IxXFn>>aee7~fxK0&Q@-~Tjow~`y?X5&e{RrW{$9Dh_a4IMBfN_B-5TS@=hvNO>?fDtb*Fj52%Ev%rQe*)`&Dr!`+=G4oBqQ41#cMyKRP_Y*xssrMb~-tNYxX@_SQu9=0Shb^;W6Zj{C{4&+Ee41w791R_V)_c)jS-ki4n+UG{R_gtx-WbyMkBiT%D5UN1gw#oHr&7<(<F2Co-4F7frCc0Ha)b^cE3Kk+>Kl^?PXyt3BlP0|mpwU);(kGy?VTgT&S+A(gQmdoqWH%X}uJ{`W!US5y#HgZ2LO7nb&KIiX+S3ZVU+wk{Bt|PCts_b}N-SOo9%eUv>JHc(UjNVd#y=G~`>slidw}0=Y<2nd$ss7So9aI)%)BUxn*)v|h;?ns#3~y=9Uh5ad*WuJ)x~|xxd(w5>-1QdUzrkB#*=v<A^Ez-tWgoJP+waTf_VD&C?DgNB-2S6!?CYH6b>jJ-ysp7pOzbTw_h?;HCwxY}@VXJxcazQF&C(AJ-bn42wBz=2y$EW>zx&`7>8F+C-+cqU=(=le*pb)4L92NkgjX7|x7QEi_b1e5Uuq4#HZLy6_uKFqytV%;KCiF%?<fD@7O#(Kw|L!zS0BQU&gSvBRhGQ+v>UIFmoj<2;8l1vAeQH=)2MwkZt}XF8phY{Q%QRq#_fZ*twvusZkL8_p?)4!W8Zukt()rj1N=U`2CtM_&+B7yWp0n_n|Xs5U*F&huWyPwkHhQTyXpP&ce(!oOXzot^eVh^e=;4v%FEat)Njc>yv{x-%lGl{8oaXn0iRFK?bxT(<@LALVQvp^KF(f^vGR3sdu#HlIe_<5S>ejZ?F9OLV?I!y*UgBC$YTA~`Ml0<%G^rthexoF_oMUb4S%-_{hn34gSPU1U3FZS7hj?IF<+VCxGq=PXDxOf;oq3Y;oc$S$Ch^N=g_bp9Omo#h-{;m^QF0Y@O*v#cvW%dk@Q8+Bc(y;s^ZR5>5HDHO3JcT#^YAIet?f#dui@xLK&W~T1$BzAJkan(7*exbw*#<|I6Eaz0Go&PW=v9#^b!<J)Rd+<FDwrEV_=vzp;*Mk32gYzgOP3z`t?d(l}$fgO~S9MZLUVD!*=>NUcjgAJ2#CC)4|RbGLRjj=#JghJWLJSRK#LrR48Wtpv|6yqsTi<7d1scs$$V(EsA{e4N7<_CNI^-+$g8M(e!%U9b3k#`6Vl3c>TD^KJS1w0JmeSJB`5(!cS0f8z}DmWbN4zM8Xh`S($C-xzxT`El9~t)M19zk6#{ti$%p=MwO5JePP@<q-8>^tlIo(dQm&uP%q_d+&7S^TFk>P-^dY>#)Oq#e2jXec^s>ZxB!IO8C(IsC+)4#^0sux%7qevMiUc=kxj{8^>AoFUjkv^cZLRg=e%rn!`4cFZ!HH`l8RNw5u!lIc$;VV{dpoAJdwh<lo^D)p*`JpQq<Y(p&b!$0XA4UDJd<G=COPem<ZDr}Oi{6Lsl6&eT7cpO5)QCK$cl9eyZ3uP_~b!S^@);2&J3`(f!#(l?zILG3E8q5Bx?&A<3}UaeF*{-w8HW3LX3=k>h88E!B8@v^P48N5aMtf#A~efdfmG(Sb2e@d^(>*xH{^xAU%B(LX5p*)Wr18KdJ-kJz+d#xG01zw(y(wn5WzgTPZb`5?&tF^}OwMvikx3GVBbDNu*!*<H{6-LnbnpaHX>qL>~&(d3P9BKtq=(RP&Mrr?c0Y4YY>_hj@_K7Xd6n7p;Z<bzJ$?NaKo!mY&oVO>c1Mg>tPw4)@dZjx5zVLA2=W&B3lefR0#P{<lF}rQ<4u8c7d=e6(h?jbm)Boc$((or7MYcm0|0kUBZT_o2;k0S#^8fw`=L3Bks_WGdCAbc<23TY@u*mnpb->QZe}YAR0(J(^L4FJtIT<_$9D&>mjsPbjPk<A_XOZW@XTdj+{{r6t-$OnH-vbvQOFA)&d;u@=CAa|m5GD9A@)cO*Yw%<6bClpekbi+iDo)IQfS)K_f*&EBz@h~Ii7WvYSr#m^6j+qt`^aYsvnatgk+;A%!Fk9FV3A4SJa8uR05}so8#xy|8{7)n7%Z|bSY#t`D{up3ZLr8%;0EA&D8VLVO|S`EANc{eKDZ^aAy{M`ut;aH$T?t<5#W~KSt!9Lk%?fDXTc}I7m+u>BJY7k7Jx-Q1YZPSLkYf(d<+)(9DEym2POC}@(-}cC*Zr_-%*0EBOigUgD)Zf1dF^67I_maG7l^=6MPArf}9Ob0dGaN0&fKmM+t6$YycKn58MLW3~2&412;w12R8*bM+qK=YzZC)wjyVNt>9$jNpLba2YC^E5%ZUW5_}GM8+;D@3rg^>$UERWn6qC|g0G?k+mXM6f5-gUQG)Z4m%#bpTx1G37i>cb4nuAQhk>^shl7V>KDM9)`=JC+MK%LZ1y4aX1y2D_LpBFb1BW1ofkVLikXG<MZ~`(JoB%$K%mE(<ry<XQ)4->YzkpAHvyi`nv%uNNtKe+#X`~%&$9$Yd2~J1mg44mNNE<j69ES`8hhYxlkbYo4jC&k%3U~^}Hx3yB4#7CaArrs}7_T^F8aNH(5{JwJXJP;2kf*_?v2StMmpHsGt*>9@^eV5{W&QO7y{_n0MX!J8RaLJhdVQqVhkE_2SB73^^eUr&<~Kdx((`*gztwAn!u$hXe+yo&*D~ZP<PTsCEIy~-%_;9Gd@HBneevF>diBt20rE%iO1&2A^)*WHJmfdvd0>BJAlM%~AGruTAFLvmfK_l1O7M4j?Lvklmw>~;F~~*W81P|~;G@Vua3HqzC`#}ll;CLOVsJEgKXN5_KX@lf@LH7MrO2<r3y=ZGufYM}>BxEDc^Jp(D8arc!84Ha!SgYWGf;wOB7?v)!3*^Y)~hFYA-I!X;&(y^y}F<TyCU0wUBRCrJAyw0e~vVRKL>xQS07||q#4`^*&b;Iw+Fi*JAymnyIoL%TcZTGMRovpz`nIb32vwG@h`F)vNO0FxGS;?xGQ)xO7K{e;E70Auq(!8B1-T$l;APQ&%tBB7UY*;3wWqu90d<T4nXz+4*<I%yMyIeyCHjm-N5cB!5fgl;0@q4$c12$L12;Jf!Bc7DSw~O>rjG!LT(5D1m1xXya%}pyaybG3<pPn4<cj02f;^>hrvg{$B;+C$H4K(L*RIDEHWA#3ywtY2S<W;BX@##gF{h*x1j`YMy>^K2Cqgg1<Py7YUGdL)!_BW9^m!hz9_-Hke`A@b_4eUe}U`@{sKG#IT}0?>5Uu>_6Cnfjs=egPeM)vPXbRsjss5s`yj`FeZZrT7Vs#r7jh`r3p`l)`}`S<65Jm-04&lCEYck;as#+OcoT9BSmZje$e+L>cYrs6Wj{L%+p`1PD{>E5WRziFq73^Rh4B!1&@es+F@7SCfJGiNjO{VQ_#eakh>Qn|j5W+%tYLlyk3>d-M}j?(yTKwu!Jgo+P=foR1aCxc1B=`Y7P%TMay@t>xF51FSY$7-C%$hWO0WmAAJ_xj8`%pi@(XZp@DSt(usk1zAU(mJ_`V@X4{%vUJbcsd_fUe%Aj^ZxfJ-AQf=h!-A>RR)0+&Em0+#^Ge}bKmZ-bq{C6N`t?!BB!yj$`={V(8u|5HT=4*x@V(N8))b~Ju6Rqw0tA*6e+(qg~$jV?hq^-khflk#t!R?9#'

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
