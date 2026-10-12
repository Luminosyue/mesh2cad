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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b41e3e63867499cada873215bf255ee/part_004.stl', 'relative_path': '1b41e3e63867499cada873215bf255ee/part_004.stl', 'source_sha256': '8705d5a0da8e4af2d011fa0c04115831a11c45add3f7d854c64ac4c25d63e65d', 'input_faces': 256, 'input_vertices': 180, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12681372463703156, -0.18235237896442413, -0.2535141706466675], [0.12681372463703156, -0.08164762705564499, -0.15280941128730774]]}
GEOMETRY_BASE85 = 'c$}q~d2kg)0*5;sB9L%M<TNl4NdUtU2oR2i;aG&A5N<(^#}QUE1V}go(E-9Ka$l<)FCcQ?pe~{rA=hpouvf9GmNm-){-LW|t8Q)8{<Cj-z6sO4Z>zR;Usc!l`Lolnr@LRz^pH8SX03SPecFl>sjc!tjfHSatcVv&vvL>Do1K-{C1>G^7|}@P?#Jh@Q4?OwoE#&Tij~Q8vhrr<CigXx`_D~JPBD__F34S+J2Pj-g4{V-Za!>gc3xH_&wFL&!mP-DcSud|mSXhim|_$d|Kq1#qzmDkes;0jm*&^YT!zy-RTc+w>vw-Bl{_%|b}%<H(n?&~Nk3Et^U$LPH{}2S=H8uPZhyGEI9l%fwev@kdOKe{_(1-h_Py4ag!g4mKkaY&dj0SE(Ch#A;#W$(W}(c@hcDa;=HY9J^17VZfmOlWY@B*ie*eTRcY=AS=%M#_tHoU<pV8yvX!VUoqkkd4KTd1E;EL?OrS->5th_4wL;uCTMDP0!CzS`U%g>#&b!2WW>{A)cg>yz;uWe`D3g%XEbD4{e@^1(8(1S5@9KyZkS1Ij$HC@hccvspTrJbA%IX>o<3MCI6NRaa`K5cwg$r(4%x2=+k5mV%PFtqyCi5PD@wf61H_pV85{jsnA?L$ee|5lATa{ZXv^;)0yljHAb<72m9FUQ~3$8+#-bzV-^_U3EZ0Cir-!!_H;+>9Aesnox4!&`^<b8ZE5V`GZUt*<xS4(3kLEIBX64+T}h+-jCB=Or|C_?=)bwvUtZVikU=<i`1S-n?Wd+zsabyx8qKt9kO6;;8krzPlc+eP`^)a$YR0KjA^Ymh%$Q`fo1k@BOZ|>lJMqdA|#7d_?{vIsTS5p7ze>%Dk9Gdt|?@^h{-5{9Fv_CiBqNL6y<+@Mm^KFn7NGjW;j(OKt^oo7~RcQXb6B0sXw+*R~zEgSkO&e8xUR9<Iuf^J^d3T&47%+$>vGs`TgD67To8ec~OZ9ddi(=@O+s9j3_jVA$U(^#!>&*+i{>t-V|);rdB;mHOn)nD=i6bASC<r9GAU26<@eUZuVnm*I_{*1jF<<zlSbzUX;ht~XQbzm?|YhSq-(d&=7%wDAc&_&}~haa0}W@RNqOKWOu1pZw0-2ef%N|CuK9u)coc|9&O74xKgEKausuPEyvPpPSQqmwSIVq%xQr<i>>J3Z;JGAHDn9y5+ZmxgZbyc~iOaz2gVT+&Q@Cb}+ZdjmqpYrTstUdH46L+p3iQklUAYOM|)n%N26m#qp_kl<y@s&0{4>esQXIKYi&(rGALqZWO1~cLpZQ^=9wycvor1&wHQ0skGy-!(Dxp`u;jJ2X9mAiyF@tM{D1TA=lcsT7Ti~ds_dEZ;P%)8wXK*R<5_OHlE^(CUU(Qhtzp7SKRmZF@1i^lVomc>%{r|k+R<GNIo#idh>IAUHQ4be*9ctC)Mp}>!JF4wR!h*eSWL!Yx7v$zBXUg{n6&7y8q0JqqT4U#hVvP>reO-Z(ba&|MutJyo9vt70gRm8y~yOo0pI_p8CAF`-5yJ%Kb&Q6XiZ4$05r7LXJa}`+~f#DEq(s-YEOL%%kk*!SN67+p?cg_Gj6jDEqL?>wEjKqxXk>*wXqR^7mo=dfA7?d~JN#haGJ^|7{;WQQMZ|!}FN)@Mc9YH+UWswRe>VbKyUa737x%bK8F&`+jX{FgJM~vtzH7DD}5_&tvw3L?w65dCz0!j`EvIfBfgMgcC~cBzezcA+5gPdCbw;5Ai%E;?(|_Jdc@L|AqfNreCk&J&zgM_&6)P=P~1vI-dITnEU)JbN`(3kBW+5?w?bvqyy!_-1N^W=QflDbHhKUT-aTzwExIEr&zzgU81zZImNlsN68J&DaKb{-c)jb{r_03<koP`DSCa*DdMWyeu#5QSnrR2PSN^r`sWnwdQHwLwl+SNe@@ZIQ#+@)=SrD#o^_sDS`y6t>lJfjl-!x_oo7W8wZ7fZJI`95-6&Ps=R7M4ua*aM{XFZQ-{tr6en1p-DhcK$?+5hU;{8C_jw@B#;r)P<aj8schxY@{xqB7GnabOl<loLXWyMCCjFh?}Ud){tcs1jO?#E~JS2Od{{;O9r-Fx=>e_zc!AL+wS-StFqeL5V1PsgXiLHJaB3LJ<}!C!(u!C%5B!hZNfd_3%fkH^Qt-uPHN6ZXVij>1zSrE{bVqqsgCcEN|^BVbp21fBuA;TibINO=LK!ftpfZctor1H0mF@Yb*k-WpGUo$&<x8JL1UgSUdu;jQqNuoK=AZvi{vE%4^B1Ku2O29xn-cvF~!H^rZZ?eVAac=#+Hk2i^wr(hy{7Ei>}D6aQ{?eSiCI!waT@xCw_?~C_`9q|760N4>9fSa%rZsLRCbNFC<C``d!4#S7yGbygmg2VAy_-r@=pN-Ff8TcGL3y#FI@VVmg+MP>r{bv-{U!=I+9j4;l@wU*w+v1HVuGfKW@H%)y*cxw$KLHc)C-4UF8N2~r8@9r0<8iPh9*5V0E$~`+ENqU);x%D2ye3{BHpT1XHQ>{D4ZI$V$LrxSun8W6*A<U{4|OT7yPqc^Z}nx~nBsann25K-d%!e&6dVoH@X`1f*b5(nkAvy>ID7)^i%-BO!T$Ipd@>w>PsU${CjK%$4GzYq;WOY++~rI>KT<YF%1Zbqz7k&rx8SSr0{9kQfWHp6;;-Xxz-{;&xCOW47QPzpz*pmI;7)uEz83Dn*W!h6H(rRZgM09G_<Fb(UypB~xV|q^j>GrhUi>}$7~F#&!{3Fw@pti~a2I|QKLU5+NAM!J124kEa62Bx55sNvVf+x>iXXxc!ng2)_yM>DKY+gj-^Aa+--es<xAC7-T;Bxq@lE)ONO=X$gZcP8{8hLTe-(cXuEJl#vta?Ajn9X#<MZ(x_y(SXFMt-l0AC1K;|uXca1Fi)&xLF8Ts#jJ;(7RDxDH>8FM;dvCHPXf0bhzQi<ISXBiw+y+=p+(_lw8tem}+a6OnQbUWUi<%lKLN9)1?T1drjD@H6mT{0x2(9>p)>r{NL&G=2dV;TP~zFpQtV&%?v`dHiIgWR8rf5nuB^{nPT}kLBK=lz(W}|582n1po3-q^;^hQ0B<m?!7&7gRCJJ%VhViFa8B4&1g>'

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
