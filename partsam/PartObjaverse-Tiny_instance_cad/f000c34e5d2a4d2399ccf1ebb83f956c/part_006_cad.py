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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_006.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_006.stl', 'source_sha256': '3686f9649b8b912673e8475a3ae4224faa3102cb8f2a111516ff10d9da9fb9bc', 'input_faces': 256, 'input_vertices': 163, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06073174625635147, -0.13554823398590088, 0.2926675081253052], [0.06175248324871063, -0.04041573405265808, 0.3780031204223633]]}
GEOMETRY_BASE85 = 'c$}q~3sjBi8pq!*2$7*wh>cW8Dn;b-35iI;Ar0*)_bGO1kY>Ix%AJuR*F>aTPKI%bd|1OwbIdH{Zbq1ybH*Gq#xX8u45#;b{#)PPYi6yp&e_(p{=fbAc)$1ZeDC*uTXdwIy|ds?YcW4@>)FqogplDVoJD$)DQ)V+q*TA;nR9JKBl6|PtZSo24ULYq5$PhsJ25GBqRG35!Mo?A5N}_D_oNh4nkgYUKE;%nB>nJ&8L3Ite(IEjnMu{(eFD06@ila5?`z03{Ewe{)m>0R-42|pR_(y1gHqMQ&9C&4y4jI@5i33+|6~ODTEDXW<UjB%)#n@c#gMN(Jjm^|zg|iCUk~B@dy&+Ra@m3M70)`H|JwT){e8+V_P_smpT2$Ni(AxAzPCU5O7LdNSE{B_zM&#<FMS^ncY^eM&#Tl<+z9fudzYv`!oHl^QBMry{17AcM>zgSzM)Yo^2H9Xlhps{9BL;&_fZLbf7Z9uqMcRg<SUtul&^U>QogwAPrj(!&HaoYLj4pQ+}TgDD<}V}sg!TXyi-iyKXoNv9o*&`^?y?s`%~|7|8pw&x-YwuuX=cK|5w}aJgjWT`58f{NMB@AJKB!#_E7%V)KdMr<X7Hdf6p)6pN006Z`d}S{r15;uDoA)UCu<Xzv2sS|49t@b5Q{Mw+GXB)xPnZ?_fv1GE3ocMa0o~jUV6KO@1#AYDeAi1N%c~kgwf3OY5lKv}gZfFZQp$=IhSvN!P6!<wU-E;W+hEc`%;xwQY|J>HEEv<@)y3mV?PxyRYK)^%gwdzlN|s>=3sfGmLz3C}AhfZ?Y@*bMzt}?>9?#(BG#YqIyxY>RzVnHZNfR=0#d(?M^N7^UqhXf9?mKCxZ+5hT8Yo-_o~;t}}Hw`NqPB>_@osxYg_Ai-Yxcl1^FA^?QCO`Rb$A>=$1v(fiuUPVDa!CHnRazxQUpRVdese+v1^h5qb^_oaSnt-j@UY>%<O`X|0W{&nFJ&Hu%6^3|#?r)gZDUAm_Cm6x#^wNr4^!ndAJ!>kJS-G1Qy53iv1^Y`CnU;Shk`DIyL|I6$P$**Y4^>w9+`}4wu{gw}SKIhEi{5oCOzgJA{sQtR}y6o!BepM{3zqaWD`(Lgr<n@W7aVg(?cuntX$K83nBb#2=`-*)wjaL~v-y&am;!D2z;}Z+ty56)cn>fGULay8XC%E2jALM+ix>cY4lly<Ih}Y$kiTYoa_=^4Pf0z8BzxlYOU*)@teD`Nm?@Ehw-nW;JBH#Kx%0Il9eATmz?^Eno#xtL@?^sU0Xf&7aM{$?iFY)31`(Qb(mm%db`)ghKK5A6P>zLuRo31<Qw=(h-KfdmmK=MVL4c|w(7r9O<jqJz9)B1|=&OENv8SLjc(E1AHbH0!Inb?0hj_ZHeV;ZkGl~2C)K4Vz9i}MR(Y2CG>b1ZzVc|-C=P{4J)uYRA$^&d3BvYp1w$QN%pS>%i7QRVvkNEyGE{rZ37{p5KYevX8G#q*=wrTGzS)?d~8!fOT9zt+T!^N;+_e$%0pZ{8=>C(cFWxA~g)lgLD_|Fg}C`2KxG`?<E}Gk)%`HE_Oddy9M#=*#~29VL3-U>nH(aS!&tnrG>s)oA|3{Rvkr{P<F;L+xoC-@p02xIb3Ui>k2;IbVIj=ZmKuc)V9jIsfz$uFo$+cs^&J<ov-we7<=1TdE)JU?uyC!sEhzV$^;iU-N#S=OM&~>)Fq459MbZ<~scSG3BfEz1YuO!Otb1Fy23l1K2+{g6h+}&xpaj*mv}x{%E#7ybu2)g8dy4N2ouTpErK=YZ|Zl{9`;C#lBPcUVS@Nzb3IC@=>Y29^Uu?mx}fGi!msZ{nv|mTtCNiJzUCRKRb)-3eTgeS-I?c_S~(nPve0S@~zJa>iebSTkor8-+Es)`_}vF8{cYQHT!DbddvOu?Mm*aXvp(#8bEbr?0A!}TQum9zW@0Z-*JBLopirwuDkdgvfH7Ud_1q!&b_%l(;KqCpf%r*$+LOC3U?-7x&0lT)3lD;uIPOc{2R~nnM|Iyw%y2ATjlXN^VMj+@76@HZ*@*nGIH3rdj6Vy>*wzq-|Bp*KFDLgg&Uuvu<vQdwsHI8Tn_2$P;LAR_ka6LKDUcjeBPcORzhlZjy3j(AYVLKO?9j8&f#`Gn9sh|d04e6VgCbvuB$XhykA^q|6Y53zN8m$e&!9nuGKj_|9PFg<R4jArf<J$eG~S3-Q;z7e1h9A^e10DyU**gXcDhiT37Zv%;ooyPiOOf<u{*wtM>)tg>3fC=c}S){5%cK+so_w>SOW~vv_@voag>ny}y`!v1$vyf9(5->n-;I`Py<D9@m9}D|%lHn#T3n@IIgOCqClqcDupn^HWZ|UJpa}QGU^D-VYZf^LXQivTs_pPk&vl!wB|WH}JlJ{nl{0jC|#2)^X}j+Aa2vx$UR?ur=IH_dwpqa$2&#--q@$wW65k;ao8JT7tt-YUfrk?^o+W$yd(}<oU<@h4FF>w`295sBS#W{z@mlud$BGyVuEA95c9{r~RGs6;GQ3blr`G)E}*_iTe}K@_@emH}A!@wz7XZoZ3-GdSB@iZSgC>jd2Yws*ds~Bt%`|EG8xBegcrD{FwERe*%~q^k4l15E$I`|NRM|b9EnjR!0wLUvLj_B=l`?Bsdv5AN)RaA#^@?A$SG!1Mmv)YG@8v>WARf;0@4C;0@q>gyaI~Hn7w!-~#Y==ttn~;5_IWa2|L)Lh@SZO0d*-!E3>32+4`i8Q?_lbZ9JiI(Q7U4|oc6G_((RG`KfHvJbR9*azGeA=wilxgE3vxE<IF+7T?Z3)l-BfRH=_Iv6Z<ICunjEJE^R=s56Xa0YZLI0Kvooeh>c37iF<i;$cE{R=n&JQ5lXmf8<I5*!2V3624WK|6!Pz@Z4q-4T-gpgq8T;1FmeI0PI8O$JASXCWlNCu;7o_Yjgz2+64k$trXqSOsT8SAeCi24{npKsSJwfO8R&H$wBl8^K$l1z@S$!CS$bp?ToV;C0aT;C0|-2+50~Yr#^}z>C3g2+4z>iQqxtiO}ibiQs9_F<|q3I1M4$SRMVL@z5#YcyJPQG&l)73fdby3fv1J*&FHu_6E0swgtBV`ywR!Lp{O%;6Q}rAZR;q5I7j>1r7!)&;YR15nu)U4np!g=veSP@FM7B@FMVXXa-nn7I-;$6+-e-=v?qp@B(N8cma40bR<}640sMW9U*x<Gz>f*91RTxOYIJh1`k6>9*U6M4eAH(2JQq60e1p-g+_t9f`=d^r$A?cQ^1+f_rRIpnNSmWCfM9h6Z$SSRX3JY-566bA5vA_{HT~eso7wuOLTL)L^tP4us%|Ab?cRj^_03%x4x2BLAQdXZWcAQA$d7;ov5iF$%~-NL{05UHrJ=*cc6>GQsYETZA(@Vl7pdxM9uvoS>8{9&<N-tu+)j*2=D~xG_X`7cmjBUsM&W0K>fk~xZVJS<blu#a0J?tY$xQQR0w-$J+M8v4zwY-4!8ldDOjpIxB=J+A=w2Xxmk6zgnB^T!R~0w10lINLb4mQA=nMv7+Me982lErF4!6B2(1ft1lNYzfo-7zY6rH%9GO3oZJ>3)HsD$a$qvv4;0Bl@2ZZGMP#180aHHyI0(FJDfL$<;t_aC3baUMTA=x10YYA&BXiIQ(q>Zh!-JkszX3a;HgR}S#P3wPY`P!rZm$j=q{^lhpI<gkcuWj`oxlx^#y%hfe6_qHq'

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
