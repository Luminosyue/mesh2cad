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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_012.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_012.stl', 'source_sha256': 'e286d76b45308adf99ffd68b8762df98258dbdbb718207ec5c3fd944cd1b00ff', 'input_faces': 208, 'input_vertices': 156, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10168682783842087, -0.11845007538795471, 0.14503422379493713], [-0.09530642628669739, -0.10168205946683884, 0.2839246988296509]]}
GEOMETRY_BASE85 = 'c$}q~33N@@9>z}w5{Vc?3>mH|G1DZ5Mk*KO(I_{FN(eV3(U=lRgoreUm>csL^0=l@(`&0#jYmQaA(h}gd6Zj<c&JyZ^sR+=&i=mWIbGgbZ@qWd`mgWjTRZ=~_kZtw&OVDJ+{xKf!mo*xxvBn5Q%y<IqPpZMrN^hFC60+tZ9geF!$GPgeC=1MD+WY<Xo+%=(xuFRxcJmDDFGp-fY5}l0c}kI2}vnwDY27AC8fm0Ykr^D390d_pZalZa=iNQmhW`x+}0G-s;w!@^gsUG)FIegxE?yLs<lnEBbqAbekl!8RX*-4eCh69;oCl!$~4~|=qP;ofwS<fFE@+!O16YNal;O4YIgduNb{wF*WZYLFZmAn9IKub`Om)+zRfFIv^VXnU8MJw{UxHkeenKMBG1#8$g}a8XfHp1RVez+{TF<B9mccvp72fkeuEzpaa6Rw?N+Au?N4@y_V!&DOAY>-2$A2uKIfF)mwT3q@tBwTV4USI(7x*vjOXeW;amNmqu*&RBELDkvFKOn|10LTWg_x-Xe4}d>NDX>1v^E1>8ZEDSLP(4Zr<Zd^}g&k0pl6G?4rmY^-r`<SS9kvnSG1&zIFILtlRwt$S*&Je>oKO*?6f?@0&KJA^+i9qF-CVPiQ}Pr0{Kdr%|5^k1(D(PsO~X)1MdWePwqH`fXnq>;Cj1=DV_==+|8ObE)1pb&nExl)?K%9;uPBy^`cxruVJp)u?mGUeR8b?xFtQUBZ5}?>G2T-B|ebn~D0E*WE_@_MK1%Hy7dClv_rB&o1Qg_yOzQ<^}ex{W0n<-@thG{~+4izO9KmZ~q?ti!Aip*$d<E@ptV1n-wCD?V+2fryOtv{=f^EuU~PY-dC0<iabi6Z-j46yM%cu8$=yUX{)hMPLv|gtiK_T?e$xIdmTTV>*x~Hzw9-}6W>Po)|nSD{-FFLZ}TOu@rL%w_VZ|er2*Ex=eSb6Z|hqh=eqh*Q8#l*G4_u~F81xoqu95<oI{>lbuiys3rj>DdYr|&^ePnNmoD!Vb+C^;WAJ6)M+V;>T!B21tug+^r!n8iCK%@c?DI-r{tKUr{^!KHC|`XGf5HPi-!hltyj(klJeffl&*<_}y>GiP@5tNQo4*)}^HO2-?N?mT?|^#ZyhtriqTfw{$e+(TpHR?#$7MVpTvrt8ed(+R<~yRfsHdsZG5C-DP@lrCc#aJ}iagzXkLt&%lpI384|0(IY(Sabw+#to{`%PGj$av`SJozL3-!MBj4$e(a2V%$#BTVt4jSeqeYO+*9vgH_<jbgS@U0X3iae&g=E9ekY(xD^Hyg%p-@n!1OU`aZdS7t~#=L&ofag`K&6wA=P|>fs{4CC0{zla2Rd3--2XI~#?=`6B-44Pxjm19vqc4Zw$2l!pgnnB$!hWb&F7}l<W+D7VId~t%Ru}88ShC@teTDWXqVZh%a~A4z*BANAP&eDosn}QBs~ywVL4H2P;LBZ{u<o_Tp`N>wQJ?P{<9*$y2lD3^<GGPj2k*6v5Y%&-56-FmYcYQN#&?nbS~A|h0RdwC_T53KL-=Kke|rM*>}iU54GBiS7n@*Sv5tKH$ilaF^uoS9a{r+C`|AVne0%1O{H_(kS8})E-f}Mr`8(VbzI~*lq0aWE*M%>A@GHjeg!x*tiqPJrv*@?-9%6d+nea^~W?)?^x?r5m;mfyHi1TY5I;B{&58r|OQ(Iv?AK^J>UsHf_&R>u79_4#RtnZIoF)!DxxIZZ8OZ2|&=2)Ds-wxrt4BHGpya?m5xZ*ka^9JPUJp<=r3*RsC`RMnNVtBtO?kh0P^mBN>O9!$41DB%?qedB?8}{PG==ZNLP|w*8=(oWl_`^c+zOIV*>>K~u4dfr%5cjUIT==nj@ZOyMWue}e9;V<tw!Dq!@Rtiv|4SqIeDf6RZhbuu^Qyd8R6T=p)PFAOaLj`F=JS3<zw*5=d5skHms92-PfT;H*C?Mdy>C5z0_%0VvB5WI#2wPFyOcK@^D3JNe-Q3zZ~V%2bX+9X*Lpk$b?!YL_oxN9zuE81!hB28aStrOJ;z)fzWGU4!+ui&XJVY&LQwx3!I)QeHs-Z`D%OklE2-cU?A!7!@UK27)ce+d_`|<-(a_$y=?lE?dT%Y#`?m0&xW|SZDAD`o`=_z)z5K9$p3FeMYt4pxwGx(zJn>&+Kl2_^>C1a}q5j<^oV(l%Lwot<t5Ur$Wp~3kW9nj@`=+6uLr$VTL0d}ozIDnqoR<f8u;0q3qP_b-oX7e5F6w=GU@_XCj5wqBt@&rM?(Gho();$pGw}Pm;Cb~r9qsRQ$9S&e`>4{lIbJaAE2aMw<nb|KzCI3Rdf((-hW3$pqW-4TG}NJG66)E|y-e?$J@FinyF5c3loZ2!O*bAG{hC)X-}H5;!`;cqQ&^6DTQM2;oS<aGxwHD_;Jz1?gz>K_!*jbzh1hSlf{EClfqQW7qHs@^r3BRH>M6{3g8Kfo7{0D^8(8|A)o)fUs;OVs39-6QYt7VtmHPHi>%`#y>eD)~W7q%p)A}8C40Y7#K&?&gKyFX1Pi{}{L~Ty)MDD4^pQt^k&B;B;!BkIjFu5JICb=EC4YdZj4Y{ovq10N`8sr*Wj#>=u=RkENJCNO|P05<JB)gFtQM-~gZAETGZbt1x*0evl8M!re5LwgS<kn<wYA89BbMU4*kiE&(sBUC8j;R{88Mztz&^TO;Ks7#8V=%QZHIUqwY*wSO8dcQrrB)~Vk^>kT`>D~8>P)Rpb|yPftB{?@9t@3LsEx@k<OXVVp@vW!lS9bwQGLnpk$X`C$i2uPFf@Lj>PLQ`++8=f?hK8)snMD0MQup-B3Gq4ldF>5sZL~fato>lxdpkS8e!DBR1dNTYgCt^u`9I!*_G_0tD_I~U9u0k3Dr#2G?3hc>`x6RYdV1JPY$9EA#2)?97Hxz!^mNrgNf=&Hj(R5eaJo>Q$4Cb*`IxAJY0=PHHLBwL)qt0`u!M@>_1VBk!p-lBbGXXI+CpEN8}OYVbp=-VPp%n1-S*+&%)3+Lbt{d)JSp!Ihs10tf`e8O&&#^K-P3Dc@#N@8cUAl9Ac=$$T8$7s)cOfn4+lB<Y@Mx@p?6~)yU%*^4Mn{{jrQ}_MfB1Vm0P7G+shoL|#IkP0c0GCTCHXlC#J&sLRPS$g`-c$+O6xQrD0_C9kC}Bx|~gyq3Ixx{|zrEK`?}W%4J~735FI^B5YhQ)3P_le&VONuEMoMxH`Wr>-QYlT)dy$f@K>)P>|p<c}E|CsWsulgZPltI5;I)2YkJ)5#gsrQ{6qRBA4HDmjh1h@3`Fp)Mw;kS9}f$dk$A)kvU@qvnvuktb5;lP8js7#h!|E+Nk)&!o;K&m<>Ov&f0$IO+^?9C<W#7I`!|UJXmQgQKU@fBLVT-+!{W{OJFq=Z}AByteB9a-^E;%_Y_nUPXI%sTU?kQOI)bttR~&tK%y;'

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
