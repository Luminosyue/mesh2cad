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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_002.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_002.stl', 'source_sha256': '47023386bff2b3c2ef147bb1bf6737859287de3a62e8aaa27ef1f31922f835c9', 'input_faces': 280, 'input_vertices': 185, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.016759566962718964, -0.14697130024433136, -0.26090046763420105], [0.13474410772323608, -0.11902584135532379, -0.15551285445690155]]}
GEOMETRY_BASE85 = 'c$}r02UHbz7RCpA*N9!wXNg#_H#A1Zjva%b2*|Ubhy@W55zAN+tTYut92G?Y8;F7!9W|CHiJGED*Z4N>8f%OtMPu1F_xrLjdv?#+v&%XE^ZoqJ<<9-z|DAbnNIV7=FHudwPeY}%akKZe_Y}ok6_jeq?7*3`CXWvcYdw8Nq=QmLeDmjbO&IDm#KXrynXN=QPY4VfKhwFJ#ku=LS7#TC^Td#uvu2K+9uP8fLZIpQ8#^^D(C&u?jhzu_|97)?uAN*g9h$pX=3D;9pK|sRv?<Nw-0W&ge0$=!`R^ImKQ+}zh!bD!5_D4j{j^AYt!A?L*755l-qPf+h|f%oH+}7`7xL`CD!!6&M||s7yCjdrdQ5!v;HgB(U!lIl>xuK>2lq%aeaq}TiPu_BLY}mo4H92e8uh$Pxghb^ABwLzg~4C7RD7*U-;Ls@ryzg#orrJxP<-R#1ro2`T7FLAhd+XEoHN8%lf_pWxh6{<AJk)fH3j*@-NaX3jF$Yi7VE`VmYz+Kenz(v-#W%kd?T`Cs?^`7Nb=aW)<K@0z0xHA&Niqga_(7)kGUznQa(iLv3kXbuifsWOP;>P(Vx@_pGmy;c=0W-Lg2sjfM1j#zR?for9BQ7UpcCauh-3yczt!idC}b$#aBxIEZ5abE)-uWR(-3~S>>R_E6=+~9!v8&;w$~VCBNFwPkgoa%573l;VbbCmxMF&du?`#uSKFi#_3w9)9al0`tysZ|C^tRM34O_zAdPu)MMO9lRU=Ch;*5&*3szOUzTAG=a<?c*Yz+^zpoDev}LE{Z+IN>cS0n;F{=Mg%)@J(d)`X%mA_ZckbTAeihb>Wc3RGDzrXm#vX&CB9sN~&<#ol~lHYe4=H&GS%ui^p_}08siMOo1g?StJW2Wq@RWjnUu3%2)MP^BVnx04e>AT`v9n0*IdP=pzdF?)e>)vZCzP87T{;WDAzIB@KUWu>egn7H``U(1^iLXDNB))ZEU)0meVW0SZaoE@1A>!Mf4Banvel{C@+cp6AQR$81>!-M{!NV}mg(nY4d>PE4>Y0T)y)KHcj?O}#Gj-Hi(<4Xvd2K%WP}^PV)I%nVum3a){`D6!|JKko;#<#cL7ioOh95O8SN8kG2+Ysx)0pR8DdKB2Bha6Fh2pEe(FbKtwx^>%X_0bWMOi7n8k>mzI93zi=8_8EhWyrR-=C8FzvYUrEZdIz;`7C_FC*eI{3egkpUg1$cdm%9A3cNTLqhx|si(sY<iG4EzT&X%68iB}e4Bd<^fPs}__}NPJn7qv>X^?P(c)W<v=LuB6M*=p8uDDy5FfD+^`F{`=gH(0@zn;oc+RX!LO&b*CceJyEc$#uQt~K;bq-1YM|fin3#Q?^Ew_kojB&+von58R#>*`6m9$)(W1CKxhum!VPsiX~+E^rBi~bIIJnG?jb-fAZBt|_f^*kzv{P(l5ujroQ8*ei39Nv(FetHfSUwhz&ey-Su_`74ox13OMUTxD*|G{zMD_u8Weli~7epxvle!)x3?XVpZZ(SDyKNNjXC!CacOPfvNt7(PCyXUJMOGBM!dZV7I-%Gr4O^08yGx980f%?D5gg@sIo|DZBFrN$Zu&*ae;BPuBzBTDB_LVXS&ppi_b-Gu`mpWbe9A4@P-?NhVws1T@Z8>l7T&>;%{-iUKNAbOj=k~Bp1yWDgGt_UJk9|3I6JLuMhyE;H4*x~~{433|ugyOA{!lKs0CVMo{I9#>bKgHoeA~87nCEfZC69J!9{gulalbrCg5P(I_!jr}_#RR-1N(AHM10Q}%<ZUT#4kt@Uzvi>cikEJmH5qwpSuWsC^b~}t7hFn{U6=LzPhx7pVQ%p<ax9Hxb*8yYvl3lEWUBsANN<>9o+9~SHwp|V?I|k$Njq}NPN9}ZQMr>@I2SG=p*PqK94M;ui$?1PePu!O!Vi%Uc}!^7hgT!9saEX@l~Z+q169nB+hG#59Vr-3;f!JQorSc0QkH5iElh@kNS_eoWr~a!*?2q`oEchewLahzQu1U<~+9;;!j43Zyi<@^^}i7{Ii9K@A(3K8xe~0da(xihiu1lAaEY~Qzub;TT~aE<ChWW^J~YW5}$wdnAGq0;G+EA9w+hjq4-{*G`KCkEqILh*5@5?Ur%&7i~VjDU%iDnG5Ws3{0Clz|LtSRZ+nXKvc%pHUu#?y&yDmwh>y1+KDZ99oAW-NGg~WuEc=~NguXqALj2i!;;Ug#G5=M&qyOGc;_DvH(jRLcd}DD#@om1@5^w9YM)GJ4+KO*1$;6yo?t^}==qSF@#25F=)ycSSR2TUBQ;@%?7y3E0JL<gM6?5LNAL<F}fq1uvIN#Z!cn<hvqW-ya(4U|H^!ZFS{6`9&+joY;cYTZcFV;nW(u;jA=euw4G1>3MSjnS)_o>9IH+{rc2j0iN98QR@f4f$EBhf(o=%2(_I;V(lS$`aJGUG?&sgZ^FrJZHJN~{CUaZ8T)*6rcgZw!2GTt56ZrO@ZTB`}BTOXP{)B-b^v_DKEO{oml1sDe4q-XXsA;~vLlPSy>@bLm=B`F^V<uN7Zkl7~EnwK2E7lf<_szQJ|<-V@()zDRs!2j);M-VgqouMpq-Yn)4goA}x<e?xrkMA@&_$P@XWKN8;-vJ(4!fOAoLJ{R98?}R?L7=^x_EN4jl8wX-vi*HE%)(y4b->!-LufG>xuT)=r%j3;B-wV~``?KZAF!A+{J@Nk4b%6B8(7ll7T7NtT(mmk!4uNlV!gUAD5?{FnU+uG6;%(O>5FZte_`_f0bIqd$zCS;lBfjxW$8~K#;QPGaJoqh&qYqJwaE^5rAkUqv=;u`p*X^<xz8juzwnob^xADoybN@@+N1iVwzZ#x_c-PNx-EQmg{pW6>_*QS$Q+^8GzmiXhuMGMQ^<S!v_np8?$Wu@O&!wzT%+Es`u3NAa_jRXu@ogpUBEIcq^lf3j<k1W7p>MTaabJ{8z<XKl4>*^Y0qDd1dbqCBbDX2M4d*yypY&7r_yu)3_J{und6cRz#J5eKgXh?J_?G%_;k(<Ae}5w8<Z{UqQja<u@vn}f&U{DljY~VQuXcEkHk#FdKLMZnwl6lL&Pe#`C$Z?y#(cbYIJ^(v=R-VyDkj3O&=h%=T|zzKTk)Rm-%@-{Sq=Z_Hk{-64&qyOr=gz@<1o)I-H|`%GVT|*^{8i%8}ej!!~MQ%ZP9U$KmAq6vEJnddPVzI?W?R(O_@0Moj(bgrup-`{`)@(P44(#{Yj|3Yuo?#PeNVnHFP$|lFQ^i)J|km+mic`U8&8<uH@EKXL4(DJ1&!3P#cm>txax0ZcMF0ZcKLKGPydn9JxBVGPM-BGPwe^1i1pa4Ap^LhFqGekV})xQj3wxk}Fb+lPi)dQA?65k!w)PlWUOcQ{N-kCpV$iBR3(pq&6bAB)6wFBey53)HY<5>`m=T_9l;|_9KraPoxebPb3FXKO&ntoE$`+L>)q&L=NOKc|3Ixc|6%l?L#)zm24$@QCpL}$ZphjWH)keE|WV@TaZm{OzuE-p*oRW$nSHR+<;o0+<;t{TA5szT$5UXT$AibEkkxBSEZIFS0z`YmL*ps*P>P=*CN-URwCCSTc|b27IIT+eR5NBD{2#RD{@C_OL9kYUut`DU-D?GN*+y~M)f97BZpJRlEcaKs1wQa$cv~!WK$=R7m*iG1IY`>kz6K6P{)%a$g`+cvZ-F=S>!2HH}Vv+54AUWi+ydiuLNomIe{EQT}h51FQjVZh2&5!lV{l1bn1MnMxIZOrLH8$k`t*(<V3Pg-AdNU*<2>?rEVebCGX)fc{i8Isni5=DmjiCLyjXyQx}q>$x+l$auhklzQ#}ksG;Og_9cMJWdC=1=g(!bFPF)FTqaMY&L>YL&!xta=aN@Y6Ui&c@l>50Pfnp`lT*kU_O;8t((UU2HG_PBe2AJ&&gOX>;xaj(x`&)kKFnou9(6Z4kGzk|<ek)1@=o$5Y8-hJc`Y@Xyq3I-8bw}4o=puQ&n5@IbH>43CXceOq13_DG33GI0n`9;0MB~>m&xu_U$Q&7KbOe^sea^vWDhQrM^dMfN0KK~=aMIr=TKLW=a83E<H^g(>!>N@b>w7f2HDhfax!^6m&s|=UF0<K4la|ks0YYd<o(n`WK;9W`^mY~!{l7@K`xVXsCncZawc^j+0>onO!7ABCh|7&2I^Y!2J$NEGV&_&V(M)2V)9ICFnK0<9CZ|V9NAO(V-`KROzz2L@`u#H<PXUoPzR7rbtiv7?ndoT?nds;WpWSdKynXqFRBOG)RE*~<Pp@#<Pqcv)H&n{<S^=Tau|6Dbsc#Lc{MeeZ0dUQYVuMplh;tw$ZN<OsXNFU$(y-M-cHRTdkk_YR;~Dd`cM9U{Alu`@b3Qr@UOr5=hwn_f3t@Di`ze65<Lc$G~ZF|FA~M%!{>?ltx@?0RA!=1'

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
