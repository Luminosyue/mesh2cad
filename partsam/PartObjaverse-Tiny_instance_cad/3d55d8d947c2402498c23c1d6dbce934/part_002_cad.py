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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_002.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_002.stl', 'source_sha256': '75d167fc32011e448d647cddb41b0d7d24087ddaea6e1fab62c5c8582cdcce8e', 'input_faces': 336, 'input_vertices': 217, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4668574929237366, -0.4999999403953552, -0.48605799674987793], [0.4668676257133484, 0.5000116229057312, 0.48605799674987793]]}
GEOMETRY_BASE85 = 'c$}r032+uw7DhXu;=TrCC#(StpaBsHm|p}5gFplmj35L;Sd>iyLH1_TAe#s%C`%9}4j=?sv(khR2qZu@0?sJ0rqG#kbY{vbovn1<>prjTeza9nGpV}uo&MhK+qYk@e^=rM)xRm+aQ<2wKmFMJp(|oh#+^pEk)Aqp*5s7bv@X+T%ndW{wSD=gbi<H@!SP99M!GRSa(rr9%FM`K5s|$o^o)#(h@3Ee=B$}xr;V9Db9}1wpBXzPEminwlg7?S70Vr?AALM3qFbk^h=mdV<KOL~h0srRpPvwF{rvN_6LwF{Y*oJD@ngOD<G%VlC_lpE%X};0zR&FZzx1oNwOPKsZ0uNh)$5y;Pyf#6kIb(M%Fo1)_@R%jMi1+X)a2eDIP1TEw$|&LiKoxYK1_Ub%N*M`>OJ|cy+8QY&29X3Rt>ls<eTMjm%YAQU&~j%aly$Cb^NZ@yIo`d16PB5bMFEtzvl;+ecR2ue%0%{{kPf{=o^J+Y6JaV-`9A3x6gd1erEd-H9>vqzT0P9+nS(xQ@%bwp~L0XL4DR0^r^7N|N2ga^y{*Zmiqix@4RZ~AH+9*zGTn$n$ESpe0)9MXmIqBx4!jF|FR(8NRK?@^Qlv(=i^6^ANt!$Uq6QR?fD?z+PT=5@7B@smG9<P{r-Zl|Lw!egZ$8~jZ3_~+HPjM+Oi;D&71C<OE>!JxbvWISM{mYSN^ZnG3nD>lvNfqZ@RDMLHYW;>AuRZ8#c5o=(y{?I_|Eo9e3S#kNcSX^MUh;ub+p>*JIBIo#(Ev<(t=9p0&@r)%)%Hs(I`DOR+)z+L8*dZ#`I6WY^R3U7!5Ak_!7c7)kxVu<LLiR=$3Jc75&sto$49&!>x>{6%4QpP?m9ocY##)xYvX(H)BI^|gHEtNuePnmXsvzWdJE%TIk>B{eyz=(KmgRG-SPd%^Jy`c%IDoKk)!zS=MIrRk@Gwrl-;h12)9*UNo=tJGp&e&gDTK>y_*Yiz&ipHF#x^SuWugM8zUxpsct)*{<CCXTz{-EPG2gHC?d*S>y?w$GgM^_i1e8RQ$KlkEDT>bxRveWP%1Wsq+bw{h}w4-|Q~Ykiwt8RQ$ATG;vKn|q3a`gi@g;TL`Vk9T~tZu{r<@(!LW_{Nv`$9p;RR@~ajkNf5eZ@%)4f%xRt75s40*U!MatAc#<39H)Yt3LI7e3fsVE46(yGs*U?x!0<EzPg_;t@Qa;=NM-mhfVbPM))S@_%+#8>C3<8h?9TM!3wV*8kghbPs_LO525T4zJAQ>iB&<qb=Rb7uOG@^<lJ{s2K)2d9dP>JIl`B3thwe~&(*j4@~r{kPT%8}RQl@o=;HX-_Ez}ntc(uq-`MxAlmAJvzkXdqXTJ8G_SgSYjB}nfKjy1%jgGDI);F4j9KST(cm60pbS~X@{<wbhscS*`mh#C@zSz&Q=k4J`zWT~Hq7Ho#lpoR9s0+$ZRzCTe<<wXAnT&s33iSW+Tt%S2a>3;w-~4B#&sX;iYi~(KkZ;sB@Ymr!VE*(-Wsq+y-&W(RqprK8j+H^ak#acDw^}s~tYdWA?f1D(Z>WQ>*HPC+=t_&KAm3=Vv)Wgu*KFtf|E`fQ-`af~{}2A{F3)kU+wa%<>l`U?&hri5`0Knj$T^=!SNrSqPIJ!Z+T;G?yLOK6JU8#yP#AQcD_=j)U0*xT-8$NNZq}p}dgn*oXLMiPXOyqsXWV@4KBIj7KBIj7KI7Kc?lW#3?LOoB+I_~Yuia<d`gi*8Gj6_ipD{BR7x?CZ=Ys2N&jsb{&jsb{&jmMMdoCzne=bDiwlDBrFY39b`|7#o`r30)_f@`e_+q}jU)pn7`TBD?G`ld*&exv%%GaO!q1O1?dxh(3?-k~=*-m}!y+!xcdrPSCW?y~xy-4%bdyz4JS+4Et?_HX&-n*=I**V_ry8ZuqO-|r`88J@2_TH%b>b=qYA?~=>SMQ}a_`H`U_iJ$6*S~rno8SGYFJH~)(a#PC`JovZhwSrE`(2>>>UV+i_1^`$uYMPpG1b|2p8mT@_qF^RemCj9`kj({#}0dW!5I7dgi)AwDbUY~_vKrq^-F{DU7vjO{!YhY1M1)4Yx#Qp8+`Juj$hi>iT>SB`TBQ1H(&eir+nXczj)tQ(Zz{hwG7=WS{8Ae5pGNv>-i)qP5GxZ_><`5?*G*%(Qe&({J)<>?-D)SVaP`1CtSn0Tg0vCZSZa6NNyscv51Cva{c?zhHyi2B=;2YgosDbX!ubP-5Br2nB<2=bYZ*;W0Kp6=)iaf#w528(US3&j7e@QqCMm78I#;eL}$i3GuD=#q8X27Oy$bu9)#o=^a(fyejM!vKMr?AyTD!HHfRU94cr`U2{(sZqwV3=a1`1Z?o6*y^zaxxcE|69#=tS;^rD9ddVGxaJEC3TuH<y2hgS3$!TQb6=5TXznz7yP^wx^?Bhe^0iX6!y5l@L2DB@WWzY#GA9S9F3XAs)g!#A`1EZ);-U$_B!3)&a%%euFqH^GfWJRqVeA^AZ<ayTLRUPAKigyee&$@im;V0j)sWH{GCPxw(n^23DWc7)^>gygn_<WA@#@Jk}bh?pbdQxWfo$R;FjCL}LJ=fex(x#%2t4mBkwix@3po`{1Ywum@HNPd@)yZ~JUFMwY|=fU%+`5HYeqQ`^uy#?J2Zzg98eI<K(n+MN@7ov;cG0agiIvPI6K4hbx!q12pAfg}IA3h`EEaPVxlYCl43F9S<onf8+jQ3|u<;vwggydLs02~XKp=aST_#9dSmrzUclOlRkqc?sm>&o%-Xer!>ymM%&r%o(6YW?%<vzm{7?33h6A})%!fR@A6BB~g#VoY+ShziCl7^`NTa>mOUlU&bm{_3M)@D&l4Mbx4-a2R=)(HaleW4Ru=itDqi>M9OnIgA>TkBTT1k&m8&^WkIY3HTWNI=TdY9exoV2EPbDj}C^Phm+9f;3RkjYQihvqiCV0ce%WnkUSK94ju}}p@ZQ#I367a$HPm}CGb-CBzgiq2^XWM;9}T93*ka~m7F1BpNQjx<O1|CTma{wpTIfro9IgTP51?L9Q*=2932S{hex1e;Sul~Xa<}?uafiF|04D$m;KJgD@ISkiOlbEygcSL4{s?N4<~T^hTtV~+!FEP(4lZHeJsOEV6GGJ7NZuN%d(pPW$f27)_H?SU_KJqo|>N_%-;}tQuCR}d?&I$YW|mVe3rA%>UiaGJoA_@b$lfkpt*1^y-Ge{ILH2o;hZ!34d)!$k9QdT1RifV$9^@QTz@6H8eUC~<P^g>_M`CR`XkX%@F;RdvR&E7Dm=M<2D%DfMNS6!a``<%@)|S+UIV{^j)Gr-Q_=BoDm(>U4NrmBq6gr$@cZZy_<eXcx*y(8uaeV5OcU`ox*mQT{(z9Yjhfro<~DrQ!+LsLPpv8J<5cEA>N?Mytn<v9<gFsMqi><>;J4uE=v4S45g&@!i|&E<!aE7cndoofOn3+SF}wrbj%LBz;jQ$%l{wssznjSN%zqa1ltry=#K+9*$81~8v*caq9(WJ?COKWiY!RE#jqoP;BVr@#NZkN`2=8KByEx9f@YQjboJL5Vg>Hm5vTeyTMZ7BFWppz9GMr9KW*w=M;MwpjbRs+pPD3Yn`jM>8Evc#K1ml-$N3y!UBu_;r!c*bt=p=YLJVQkMps;%3^?&VOvVQq9?H3&HKWOP|`afHE*K8zy(7PWo;s@O<e+P*dpnCR1u9v?&jsE~w_~&x'

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
