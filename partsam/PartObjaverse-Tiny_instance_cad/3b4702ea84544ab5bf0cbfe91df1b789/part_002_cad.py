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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b4702ea84544ab5bf0cbfe91df1b789/part_002.stl', 'relative_path': '3b4702ea84544ab5bf0cbfe91df1b789/part_002.stl', 'source_sha256': '3abcff4a1fa80aaf8556054659b4e48ee055d4fadfb48268be972a46aca12762', 'input_faces': 257, 'input_vertices': 144, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3783116936683655, -0.2383294403553009, -0.25735145807266235], [0.3783116936683655, -0.12484286725521088, 0.49927181005477905]]}
GEOMETRY_BASE85 = 'c$}q~eN0x@9mfwKwos_RsBefq=q#Z4g7T(Rc~C(GU#M2CWtE2_2%?~XfQsc&v|7bd*Jdxt){rdAk}lnBNVe3a-e+qqu8n}zt}a_L+AMYHlEtx?cK_JjbNQTybB}k)vOUSk_v6>!Irn#e_uO;O(Teh@Ny%dTmnOOnCKifEZM0jQNEYq2Eo}`owXKVr4jqjU36Agl&{wwX*j%wYLbQwH>3eHiYg*D*`qH1MD@f1srPnpLw6#<>RW-Nlt(AUh^?}w}+i$I}K2&S}IU_qKC(E}yGs}0v_dot(?G*fL^6pqtUp+Y_b@c4K>z0QfthxBRBF*=0iofCLNuMiT`To%h<MBh0u5o;YslT>7eE+K0-^=(=S%hnx{;RW{c+(eOjmHO$Z@caEFS&BfiQk#&#GAe-PjKS>OE%xu#|a%<J7RhG{+ZSvWPJa@O}AZn-e2d$n||o~Ay>Tk!HR3Hx_w?Y9{;^O#~)41aOyVt%J41M_${3yUVbR?@6PzjSL3UCn!c*1@<UfXd{=+Irmyl0CJfzj)q#9WU**$3I5z(GrHr5b&#Sucd%5mcE?-o+;{ACaz3%1r|E>7C?yGUkc;%~jfBe9(bG@>HkbYg?r4+{x4gAA$<@54uLwdabi_|wf{dayk=*+i3+>kzw-@5XKmmj!v&WR6pRNm0<OXM`2wLE-(QvQe@ukOo?57&Wsk=6Ero~P(Mzt8gUeT_SYo$*KRy|3pfmj1EW^6>rhW1RR<?w5mlp1}qGx@>v){y)EUOOIE1n(^WMiT8ch@SZFGX>a}5^6-Q2jD6_DfAQ5dSDn|r?f9d2@4I|anfSUhFM7s8uKNGP`h}P8?``}|k>-c%Z^Vc5CqDS<faT8ruRpgu{NQIDA36EQq*!{M!K%-HW_kGqc}{%rhrMsQ-iyGRUs@i%xH;>N9v^-$jQH?<5kI=F{<3SHkCt4uJpBIY@gF<$?UNao^*lq}X>VH|e!qCvsZZ$ByZ5eYd5-?2!MVQai|<^%qsNEW4I@6BzY(wU3?0Z1SsuRF_3e-K`0zacq{y;7eDU3KCqDS;jLStH_iOs<egmcTj&Ih}^uzW1QSX~Y9?#eG)$>xm`Fu@Z#rMaiSbCmnzCGYG-~8Viu=G6Dd^UYGp981ILasb{Urb-UFUmLHFVk1?qkp=8P0v%zj(6T`(^u<&xZCiaJOA<Z#PrpA63qK@P|s7XSEjGlE9IN(o9U}~|IK^vyYgqfHGQ?-ibZW7xbj!)x#5S`^Ulf}uKKI*h2e+4FZd69UkqQx2dd+STzRVRo#CtRUEtDdL$3MH_w)gu@2U7^%CJ6;`Yww{2Zr_d@OM0-YQ%M4><3I=?FW=^?jKBF#f$4>u5rTo;G6pyxi4~jkNuMF>-#rnUU=;Hbl;5k+SfUC^VrwvzS`G`-`*S_pZ#YbXQs1nl>1dzKHC1)m5;W+)$>u;HU03u*WOpV>Y(knU3Fu>E%)tCKac&q?yLR0JQwKW=;sC9SLX$J?$GZ`KaaTTK%M2eM)&pek?!l~BmKJi`N(y@@_ba`Iz1+ynLgMXCxmP<_UW;%T01&QQ~s2C9~~QV{;Q+ovfTXt_vn~t=MZnV<21=9(P;Q2d;yJsFTfX30bhiB(MfPGd>)O1&%;490S>~)7$=f`FEQ3R^gMhHK8*(9({Lwx4DN)dq6zR+I2MhAW8ul@BzO|JO(wTK?SA{Tn)FdKsV{0Ze32SUJ)_n949`UBQCR9U?RiN~q)p?wNqq#4hojMl;AmJqw+QYb5{^P2f@KX~pvLk(AEq8(vs;(l9uwpL8X{kVDKyDRb~|OaZo8d8li(y`PSBDWCz-JxV|=MG+BIUxD~8-+@T1Tva1^ZWYYMqfh95?gwEK}d6-|PZ$Xm?~$!h*|i-|ebO^v#_XH_q$FQKR4vpnw}v=8p%?|aZwa1Z=EdICN{U7km~;2!iW+NE7n>KU5kqi7f0Mct3mBu}GBeguty)$@>CZnw>LTZ`_1*TRM9vv48246TKi!3)uY@IrVVdI+8e&p{8sbKtq?UU)9N0R0BM0A7wh1uutJqMP8A@EV%rGP{-7ZI#`gq)Fb5=EA$-YIG4?4L6|k;Rd)BO@UkCc62)24!58);TE_a{W@F^2hc1y06&f9z)!;!=o4@SypGz+y4Rsia2>oKZG+p$Z$I^y{r8}C@E-U%bU*wQeRiUI;GOU@=yUKU`fNdW!du{N=reE`eKw$5;0<sox(!}KA3wSQ_QR{uQg|hO3Q#{>0Oz5r;pOyMiWb02;l*ekynsF#=u$WXejHs4&!vwK&47LIEc9`B4t-{$K6o}f1DyrWqfZ(-8%~2$(HZbU`edSMa3-9NrozkUlZ|G=+3*rH9WJEL3N#yD0q3Jj;I;HAMpwYaa1ojhm(yn>S`2T5*P})7X8LSJH^N)t?dW=V2Yq&-Tj5=BCAuAcmOfSJF1QM=K`Y@}`s_oi;C*l-S_2=XPcym?ZibJbjqoA*97dbr!*B<B1U^8YCiF1e1h=6bVq#s9+KzUJiFHzPD|$pstgDh6&_*$_4oj{^YsAF5EqOOuDJIr=$xou&#l&|(atXQ~E`e8}Mer&(7tM!r;YH{Yco94wO^4^hDQGHOQ63SQ9QB|68*JhibT*Cpe~Ots-A5q3=W2Vb@PVkJJX-F>?9ExE^Pr+-7UJKd#M2!'

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
