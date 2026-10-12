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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_005.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_005.stl', 'source_sha256': 'a1fd436d2011ffde4abd5f4fa7fa7ee482159690c9d766a6f96c4344646cc265', 'input_faces': 195, 'input_vertices': 133, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2583797574043274, 0.2641400098800659, -0.0652661919593811], [-0.07110168039798737, 0.47614753246307373, 0.10074084997177124]]}
GEOMETRY_BASE85 = 'c$}q}3shBA9>zB>1;tDS-^w*HFrS2|AbF4Z07MkiCQwn3N1E~`Q9(UENNr3q%*o8UI-{jw;sXVrXK96L%^*JVkwjUVjh3ltlhw@K-~V&aSu<<Rnz?K3_5IFwzWeQc_P&?A#YVfi`zU#JQfGeXfBh$KrS$MtK59m4PTthy)ZCsKS+iW!!|?U%o|cS!Iwm&WMa@tJ0V%1u$vFXGwt(=o{sG->0cn{zc{xcLlQMHsQnf!UX?kv|)6bofl$Gkd4h#wo?rsb2+TAwC_CLNFIhSBWFRec4RP)`-)pot6sPZygpH2|JOWbkz^WWa2uhsc+@U76B@XbA~-+`Y$R{Y<N!#BP^xe>lOQhIhp)o9-ezAk?INXe)4gRgp@l%9os;Hz7f^o&2W4!L)NrRU&a<jtWD@e6H|Z+=O7hTVJ%e(SdIjobz&Fz?EbkvA5(NzZ|OlJ8cr`T@UPAo6DD{Pp_UmVE3l@YBQKt4qgM>gz;XmH7F4rRUVIuOdJF1M%x*UUPEn27T@D-Ur_(3z78~+;|QC)g|!Nl?vG(pT|q!`xi>j6MJOd-}V;k>$-2V#Sc0s{o}T+zTa27zm(@ac4P(StLY^9IkuDNnH-DtJBmAq-=hnB(-?&Hs3LFp*3zx=TxISr;kw_QKO-L#Cq1Djmm~k%RrqS{VOeKLu8Hf0mnENKh~ML65!RV<7QS(Au=LDXQiy!uI{217N!D}84eK#iWl6sLq~zD8K979YK$$mlz4(Q)pNW?`i|^9zl&mvd`n`Vq1U(72kvC2qdj;p^e-Xa<rtGKcJ|GGHgwx_j50{>e?u+n#BM!c0O_zD|{HNRHIqC10e0AYKy#GbJ^dwx9eydG{R>uXK<j;J-e9QTmcT`8oe=|$+-&IV;^^hi#zgjK%_rG{nYvQRbALD+n4yWOtxru(Ydj))Jou{mG<Fs_-OHIjdc~bJX7S6-D44wnuI5SXuYuadhPS)Q(hW%SnB))t9F<Ae(EAXwXM&gfsZ@Jbw`$72TFB#$=EnSMw<JxVKuU&!lTWwYqYqf1yDgJ@2$eaC|E<pd#-;2MwG4jT`*O#Ghz-;kvl*l>S+!n(hk_X@DSSj-s_DDnDFOP9vL-yfl<U-6_{N+)s^U6)hXN{SMKF`DA&pQj>@$!h5aX+mbzP0)idMu;)3f%uF7rwEt*{8^P9La+onIQR}o1({PG<y~Hr~T8?UvLyXHoxQ2lN}@ZcJ0t(E}nq>v|Su7{k2ipheSWOS26$W2<f>h>oiZTE<w+kQ244_S6R=dnkAU`&SxK?=k<A#pS0#R^!2QSZ??TF{jQtf8)>ER)%8)*(_rF@xc`GGJ*_@LzRrK)YTQqrD?Qhqf$u2!5`Lm>w)kG3%YI%TAoC_Y3*S1FF8#ybD}q0$kMtMki{B~*=Ux~1)e-bm=EApy7q7(qj2Gam@-A|Y-uZ80o>9+9zPc27%l_^wxbHU(zA@*R^l!|-`I^1@iQjmj<V&Ag1ATv475tDJ=uh08w@$wIQSeR2SI8SRE&qV~Q6BKshikb1eb=I=^^YGS?{`-EYa(CAyge3+KcU$f_%S_Y|6ADL8`*!9e$TBA^o8$yAN#f-PV!Z^-om`MPV9x>C9D?vbH{rF^2@5lZ*}(qa)DdKpSuFSxz#Rt+u)5@Prw5B#^AY<Z<(?Q{?2sCZ_2Heb1~49_+gUt`@V5O&ZA^A)-|p-d=-8XzN7!Z&C=&9{R_Os_bw_$e`9y)51xg7N25+ykG1d9J?O8x{TZ$+!{5XGzgELndyCOy-Ywe#jXDh9tQ!X3Sns_RpPzx-;Twlt(O(z#HP&PPyh?gfuA|>*+Pn<wJeMr_*uKac8*XDCR8FGgeTvX;#fPI`4f(DT>pZa>J&y15x1s-9EqwF1Df`o5H2SUTv+z|&B>K$=cdW;lavHv|^^QE(-r;yIBl@`HGY&~lub;3FX3vkMzv3IrYmT^xc~#XYS<mu5$lG4~Lj2p2l3#OG_U9`TJ%;y<3i$i|rRU1d?O3PBD)`FRSN5U7A=&5AE8$zsF3ab{btCq{d}Y4$IO?RQDt8C=yX#!>OJ>Qw4XVL<tRo51)5Ip{8@Lkr#A-wGyOv6iTbG@<A9`#ze6P;%)%nHnZN2uuSMzG+9Ot%&Z)CkK{<U55dCPuE=6&ODyWppPi+o)x3wiU-e(_6!kgtpH17DTp!8a#YpGQx^-E#Q3;o^6GQr6$2V3(YGFnr_J64~bld$6BIMQu6qS2N^%pLt21H>?uA3N4kM+L7o{<z<rJ79;1rY&_Oe_o_R5>!F|Ic|%(uZ+*RcC-UPqoR{x;)o#pF)Dgbr2$Y`u8d?7vRXecGy)VdqetsEw!(}aeE8zrstW&ou;P1Gz9sMuM^V%+)g|80n7yrOc+0S-1$yWr!x9oqH^#mNPw8uX1tLcz^f6$-2l+we?`Ku`{>As&#+SIRm`tN@-P3`mF{bULa`G0>hwRWzdt<pd5M4OR4sV%6@$jz8*L2XZNMeRs!Pu3bh*4mleksL@3AP16rQ+twolLt`ylC?fT9zc$8ju_{Na*k2d2=Yj3G&O=8!S_Z}hmfPmcIp#ktv$$Edy%z<lI>)J+Ka3;i2NiqoEk*#M}3?cMD9xUrv{O=K0?-NBm0xvP#+;{ZB2fd+JxGgtks*WwGp`qxgph?eD8Ck*^TN-^(4Dfy{Mk#=2Rc5Cs}I?^1aWQ549uNhun!8NY>hg+=<+d>PLQv+JWjv_G7LChvvsPG<T<VBX{F`-Ko9F!PF3HZ?e__<Ph>e4$Xt85oE1VWUa%<{i#E#!^p#!8_J=1IEUs~Y7ANHC~_?MDGtq}RsHv8G&Pz$nmmGPC*$uWc?3C9)qn0Iso~^E@?Z|lVXFT75Jr8R97gWLq4`l&|2=t>>Q8=@+>+Xc+>+c>)qfwFQk#&Qk{eJPk{gg+RQ>1Ph3ZOnA>Vsx_E7cT2M?+j*@N7eL$j}{|DO0#eaKonkyD&wvU5!3$Z(Ea=Xjo4z@d32hvsZ*204T8&*soPg*ur$g*=g(K#rrvQxnJu%*AtPp2VT~S!xP7h4X1nqdv!>Ig>h-JeALo$)S11ea}CGT0ovbp2MMeA=M-=Brl*AkPEnXnio;$Q)iOrQuC=Z$uqg9`P3Y8J~@k;P0r?CYo10;rcNPG;a(?G6UoWs3Dk+?d*`Hi9QAk9IPzHP7-}3jj^{Uq`ZReA`59_FIi6>%c|0|VI*B}qXPKnx&pV0w965=c%At8Whvsw+&3V*J@+|6XY9?9h4DxJpA&2I9&Ji2!;_Bn}pZ>Ra{max}^auVY`M<vN!G9Xw|IWV7KPvzHhhl8BhyJ_b`~%^N!}rzywNw89&P(>h'

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
