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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_000.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_000.stl', 'source_sha256': 'aa59665b8b9844d8e68afe533d411f030771d1f105c1c08e2cb05cb6bf8d337d', 'input_faces': 384, 'input_vertices': 207, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15060491859912872, -0.15196062624454498, 0.023266073316335678], [0.1506020575761795, -0.048046939074993134, 0.4999999403953552]]}
GEOMETRY_BASE85 = 'c$}r033N@@9>$NDhnAv-qOK}IB8CW}$f*)ziK%KRH%N#Qn#2^69y3V{G1OSS=13&Qim4n@Q-q|gp~P#Cwy(6Wygo{Y*YfWE{@?A*z0X_gt@rL)|MmUumwos7pFN$u&q`R&;w7qT@~NjStaY*QP8Cg4Q9-M!O^Jw!iy9RX8xTEddNHjMeD!hZirxcX4;x%eo1)F|9UT!nD#o{+&9{AITVH>hZ{)<7xR~(h5ffuZM<_oue0*$#(~lh+J}JWay-~~NZTxM4js0y2w*T={&Y6OvWY?S%PPI4cw^yk(<o639MSMrwlY8*@0hKQm^^FGib}QA(B@`6(^#Wh`wo<J>QNCFi1Yi4m{eAd*c%{6ezHxgcuB&afN&OE3<+>+xab2y&+=8OMwt5VF<7zPK*Oy11LVmOC`=Q;(pDpSeKX=N4ewF;0^6hcM;M<n^AHa3;l2G23G6cRh@O$KM|7{V<J32pOs_$l2g>2+suh~h|^ZKI``2NFX_-4~V@b#C!`3T>QjkvBJmUmV8T8(4yty1-nzb)uv`1Ufrjv>FWj0|X<^0+U@fyVIl#5XdL*S%-OPyF#HzNZwxH{RWdb~7G+3*Wr3MB4vOFZ82Txd6WY-BjtXlbI;5C7pq9_^(Aij@(fwZ>~u_g8I)rKt7h<6766-A1nT&jkvDki)Qex4WA#z^{$^s|2nRWJA*uH9ufccD)fu~YBGGoFCOh>Yc(17XCJ*`Kk_jL!#A{+XeVQ8u>+{5|Ludg?f~f*tJS^F(av2@z}Ia#l7Id!_>S7c#J_UoL-?gfo9N%YufTUS*#I@Gq`<fPS}3PCZM+NDEj<YRqNn7**M?rk{aTm9q`!7|#{HP<*QO!=U%$clw4Ln)-x${`9lvY)z4#wCgRlKjh<eOx&87V>HWfd=Ij(DE)|K(!=6AHC(QmVi+j9B2xNe`{;F~}FhVu4GN8p>84w+YN%Irk>wRb;-e`CAMs~0apP5+G3xNgU9(O!DP5Y(>)EJV8*pPm+f|5wt^TNA~fv_-y;tc(6K2l($pJ>w$bYsU*@{7&EM=^tr`e5}9yeg*kVYa#Q&|1Rd8es#?Wv~yZhxlcbChi1)6h44>YmvL5a4D#1apF-*1g=ly4o0~FU<^&^8+no=#!(Vd`_1SM6x`FZexTp9{y2`x!IupKqdxx#4|ASSMfBlrbD1Rk*tIV%2WS(W$6#vXQ2l6<0P3n)2zTx37^hdt7O_Sl<{^+*>-=7ab{>HSHf5CPAGS;JA+Le|5JXa6CEw=A!e7_Ngb;zvv*=n>~sW0Ed?+ee!x^?%-TGVr;BYfxjDC2+rcQ;W_m+h-iE+kC)|H5_nR-M15BJUs1$a?<SHu#QKsql^dGQS+h_ewoSw=P3H)h2o7)4L^nGr*L50xGV<IO$WkRNB9X^z)tj`M7TGG5E&bp~%Nkc@NeZW6mV_dXq=+ZM7rMq2F8GUV?gRMWG(+#&N8B_TCE@qn<Z^!n`yRGf%;Pl97b(NAjfocfNHQ_ciwFBHaJ2zF4>P8TYc0|IXzL;8#B-`Ir4p+H=c5_-2>!9`~zdAD)Nb=gV`=k^2zqfO$U|zU^U_JO?s=*@f%QTsa4MbG&IWi?8E;ZK<=R-%Fyr{nucWw+*dipxp4<vOY&Hk@5x6GvOB=m-fl2C;if`%1o(e80L}r<jI%F=Q+Q4w1d4N+Q+<g7rxc+_EglHTT-6SM@Qg(9p$@Cep)@Y2|;oAZhKz(Ye7R?*St0&)}#J0tiML>cVrwkk#*GnzW7GyB;-Bih-Z5izBm#0U-LS~zZFs(^=p^5M&tME`^)+lJp}DwJFsU0>iML`N&G!(QwGM#j@Iz4=JRA8^~*%R*f#z;{%QB6FYW|iON^0r=#YqZFnU>0sDE=1^0$6`B>8X59EI;W5gzqese$kvhiai7%XME%9*sn~@~5z0(C2=ej`DL4!#CFV#&b>oIQXE4|Msp!xPF1psiMCA;Fzr2d2(Ma-(D?M`sEJWXV%P-(hl>Hr?&jo*`mG~YRPlv=F1m6%4e^UdN$4Yq^NJJF7;a_lJY&urv%A3^ecw>WsCEX@~_uM``eRBqaXFS;E^Fu@$Csy;Ctue^1btM`QG{bS>8LJS^MF8xAULAS3A4>e{VPOz1!dAd$+%y^rPIDSHIhqG#wT4v~iMFZ#4YEQ6A&U(X0Bnkf)48m#@EFQl9hM<bE9!yS<I_F|o3Lx8})sj-3ZzFSf{IUKoqok4OH8U%)&vg12EF+1EXQZ}lJSG4Jeq(kCF_PrvY(r}n$~6GNUdzwB*##GpLa0o%TRh<|f!EUvGod#nSNPu6t&J^5?dcbpHB=hWh|@u+9;Zz%8BFh$nqm7(yx*B|{{z|5!S(|C=6cDnSQ^kY(US!W)m&BO01u8{pt#tz)CWkxQ<?`CBl$NfH;g7w+FXu-F&FC+VtgWIKj64R5A&&}aj&y9f{GI70&fypReKF8zvVpV(%z7`PexgL(Fy9D(Nn<o39l$zJzUrShq>#W!0yi-|xTimi#l=psK*SZ4V`}uAiy9wWHn1=nhUT57Qlxux{IqIqZGxn2ObTY=3S=|ypXRJIoSAB)@+S;-!p%as{ik8<Z9EPt4k3qlKr~ggXu?Cr|P|tQh*>8VdAqVy6{R6%hYsmSforU?X{XF13+{c4)=r4O=8ukO`<5ckjugd=I$WK@|bSn+M!Sj)|s|xnpdgvGM9r<VFJlEqFw7<D8O!hBc`z!6?2+^8BGGDHIgzMUlHChk7{(|hI{9eXB%^H`!UdEf}{>>42&VlQD?E|gWdE#^5Xq!I)zT^8ZcOZYBckEXNV4rFHeqa0&)3GnL1%JB-d0)PkhCDN$;Cx~A?;z)(+uy_2GqU7du(U0F&B(_1HU1KgcC(_M;JW7U>oQKg_SJgu$ldteqU)&NSoJIR?MB&1@xAu*dgcb~_w`aoQQq$N1I`^rf<t_-^N4ol2k|Qwmvd6ww$n0??u%cnjhr9-XT!I8KNA1JPPCi(Sk6H%-#GnP&TGFMmGe<vW1J(6i(krkxX?n*#RvT4e93c`>pg>&rAv9&d2OGZ*X-|hhVMGx8L@vYknx!U-;q#V)~ga9VjXad%#`{o`p9$PhlB97TP<;Z)dp>m_X8^z;k;u-wTG{_xGv|^nZfYQ=Hb|%S_MIJ{@wlu>b3uKI(+Z*vOZ%A=B4Ac)v_)n^hUp%3ogif&6W26TGS934|k4!g!;YSKj=Sw4d45Hg}zif4*zs{tQ%(jP~>U*`X%_5-W|_VJya8aVl>XvdTM>S-&M1*4rq%F_>TTVWgUokOZ>PYqF(P??8Ao1zJ6+e$NL#QK3aV5_dN8y-}4xSfmm-`?~5E^?d1JQek<{_LuLHW>V$oTnG+<w*Ly0*-B9@d_I`}MUM5!R4{Vk1;TL@m7UuDmFz<2ZFGgjxq-$DPt*RCoUgQ;_GS$bWPk%)i)#|@`MHtw&)&Kj7aJ4gsOlM>;6rW%yKFv^kp86sAJUN%TpR9B*IhTBaq4*3#@ouVvtaL4TH~BF2J@R4lHtJ&X66$>FVzSbA$@9qx)M4ZV@(Akd<Pqcn)FAQzat~*8qBf-lk(JgZ*P=c{txHx~ll%<197Ayl>ht6h<f_z$WTh{YtCF9i)+Z~iPJWJDnxVKnwH~=VxgtYx9jYI>4!H%j6}bhu9Yb+PY8$fB5OPQIAco>M8H)Q-dz1T;hf?1n4<#p3XOfk!CMS|psTt%{avJpnd8;$how0(tnY@BL#~HJ!3mJ+RP&bnokX>aIZ=$A?H<5QbBb$1Nnodq<PKT&z<ZS8=Y8rV5`8Y%IN7NJK<5ZJ+f^3q{QBRZ4kuOotlP{4kQgg`{$$8WZ<UI0O>KXD`^2ZFtIn>=`rH9EmWLJ5`M;MAvF%+MqZX+u_N<KwBMm<VCM*e`Icq4Ti*|i33WErJPsY}R9$#bdm$#comsR`ui<dM`7<dNjT)B)td<et<X<eubLHTRnJDns!r48`rKP06nHt3AsoeSunw`~tZG^%-&nav5qlav8ElEupzTii<H6m!wuD7o%3DRwY*^`!E!jqCQ7fTAJ)bElw>>E>12>El(~>ewJF1{4BXPwGO#9xjD53xj8wQ+KwDd?#EEvpW2bEbP%~8bs%*Rc_4W>^-c0{a=0_%sdnm{WTkz{cJdJFQ1TG6K}{qpO(h%T6lxmTwVtLh6fdH#ATJ`%pw1z?*4Y`<cyc^*oxxB%i#minggMQkrjS#3J;lA8G2R*7sN=}p$f4A?$)V)e7>c79iYGD@ze62Ieuq4XI-Wd<9K%o?N$o`*Lk*+$B8QRNG8DI@b|beW2T()F0pv#1*T{{?FEJE%rbdyKjwN>{ccDg*yO6s&qnR@rJEJ?bE4e#)G&O=enjFhe97i2Xjw4T|Mv<e~2a_3!*E1AvpuR)iKz^S(iTpl!9W{o$j=YMYcnUR=?CP^A48>EO5lx*y9YdZ#euElDeuJ!2+mdy12ZrK6YD;n;xd}CZ+=OhSHX_@|)u=C#tC1@)6gQxDCM)eiZb0^>b|ouqO!g&LVJNOaZAPv^e$g5J)YjBy<ksXq)b8Xy<Wbbo<Wb~l)L8N~a<VhFQ&&=B$x7qME6Ho9lgUcglh=^<Fcj~jZXoX?AE3TZK0rQ5T}M7h&Z4d&XOVX?6fdJrAuF9qUPeyR+~YEdI**)0-ojA4oS`_L8cmKThf^nzmA*j^Cl9CUn)^AWcp$Zd=6<dzc0C^z2U7zz_cK&+b7~XK{mfNdn`+bC&uGQ2=eXjs)M}dhxv#i5wG!EfTA5mjth51HsV`Y+70ta@QS931@IQv2H8l4}v1`AixB~S>vTHuL_F9V7UhEa>t5ko@z28&ZliFHy?++CZruNa?`$@$ksiQRa{!{UE>NL&0UsXJpnoM@hCD&e8v1>o9*tM@#?AmWDcJ130AEB-!D_uiYx<_;G`4zj)0*cR4_i66)h2lKw0nL3LQS3UiD858JNLHGqxz9U_&rx@2?(>miQ<Jlm(jC-YWTnf<N|VS+w`lIOo8oMS;+@px<eg-7c3eoEO<hh_8n3zcPinuT_B~-ei}_S7{-6HE&HXXdAoci%H}7A1zV<5m%ZAQEf4&3@>seCmwVjj42M^d=>dl4rFY<MrJp'

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
