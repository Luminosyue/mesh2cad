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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_007.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_007.stl', 'source_sha256': 'c876817795c8cea9c22a15c6710e2d59d47e0a7070decd753a6c133839b60c32', 'input_faces': 100, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0762644037604332, 0.24345889687538147, 0.040061138570308685], [0.12258089333772659, 0.44652697443962097, 0.20079471170902252]]}
GEOMETRY_BASE85 = 'c$}q|3vdlr9L7(CdXo@>h-^Y~LsCK#O-bBMLP&!~G2=CCaH&`5jnWQfF(ot9vy#r3)+M5z2@>x#E-k_61Z}+^SBg?qjG8H_>OJ526q(zZPP;QZ-*3Nr_J988?EjqIo1W%f-A||^SQN~==Kn!0A>>(4_=#yY`_yrxY+3Cyr+nxoeBjIDxvuCtuuuA6FELHbu#C24jj~(1XqNafah6EUGG?-Usy!of#AN$uoAgsMCT7{(e%8AgQ*7?*@VMAWExK)__L25qk2>xY44?T$2i$7zUvS<kbDGobE2-v<4LhW->Br8=Yu6y-5PlEav>ok3Zk&Z5k#$(A-fR_o<FgSL<+UU4-gd+px){D|LH`SA_sfwY{JuD6oAjN1U1t!db^kJ{&ZV6Tr7w0nevsGNnNdg4{z_B<{BddD!%xbDFCw39k-j7TKJwR-&X(f$z`5{UK^u{eQCzkg{d8^#-`v+hwZ9keHMH*2O^7om8+nRdX?t+r-nH<J>^7JObN1LHXrCIg5&5sKK>p@~T;yX+9QY;t;Wp$iGV_kXpE^Dt@gu4sf4yxme3zd;eErCe-(mb^HPyIsn&%-;V<+-40^i?{agBen2J<lbwwmXa8hpcAvJ&xA>ZtjdupV(-V`jkD^TU+Ct_b~VUe4vn({&i}&G^eD@Oxibit!daQ}GuS!8alg&V(N@7UMGgci?$BIxn1#Ix+jgcO^GQe8;@pv!$v&Fh9<cpO3!moA(yM*O$&Jd)e1d6sz%$-cj;O`$JEVkDd^V`V<eBO}BdJSG!p@)9N8lz4Gc(tA}wp3J)%~dYA{jrdWx%H&$FiT-L48doTQ|^Xy!HJV(__FnrhDB=l=6dE`L6kdG0^xHWSJ+9y`7v3hup`lJ?lRu9kJ;pd%?{=Th5ojB}Ej;Or+;a9C6{etfXH4Z!ab^KYe4c8S<H(5Q^d7in&>S4X;8RhWB$Y@o!w;fpT+WKKz;TI+%zIm#AGwxfTt^8#g+MAUrm<MfF#{&3O)~_)wyAbUx-iYJ8K6f4bJr?XA#*8f(mmb;_>r^XS48Q7r;+(fiwXd@O7+Zf+I(U(qx1ti{?<^RJ=b%4+fPKKl{LP2w;hPb)RGc%HFptg#zrz>Jem#ZXFV0u{UTHA;H$Ojt_}VoS;}r)+!PgFjpM-9<!FSD=ui97HZ(Xw%7bD(C72kQfjjEpwr<9-E5%ug0xsT`W8q|L$bjSp?|1A7TjjOT{z8*Xs`?E2;`#0z({pK#TYn_07Og~wA5ZBqK@tnn`3FWvyr#j*ok6NKFM57qwX%6d&xX!q6_>Mo0BaX0d#(Ht(+En}H?bUoPd$L8<%SQOFu%^hz5t@YOXp}#O@0=TZMy=Oj$kRNOv=`S6b1|RdRs!-7pA3iZ@Y$*6CuInHvqSz~HJ%2TAAS2B#L@Tk+lTh4lhCiT$b#|e^^dD{wy~`m?<!xs*UaSm@Wt9vv^Ni0)xH<F8Y%`1SNm1@P{c7(D&U*_E~CBp^f2bf$i1%ij|C^x`!Tjqt%p13@SHV!EA<>_pGF+VY#+R@^qenLohLL!K90v$^&a!yj`8YOL*W~Di{Tr-YmtxEI8)_0#Qy;DsW_nWOx}QgwP_j3FDipC0?zHUroZyll5aFBj;bMqJZrnZTE=9&^vNPkc|2FopDg2I{?#W-$Ec|P`OQ)%(w##`_ZdTdgB(NdN_~^umE4o6lcl~zmfDZplbk|LC#R5mQQsy@?M?1Q?%_VWQ&XwE$x`1Tr;^jC1ITIQKGgnXseQ?P$cfZsaw54CHI^*3Gr1Evni@rx`Z_t996@bMjv$9p+mJ)aLDXQf)RyERasag{Ie^@R+KAkQ>`Sdp_9fS)dXuGACrcINx@3NJ3omjlavh$M>rtzbrPd(VBiE<CMy^k8K&?q`KyFC&AxmvcZb<gyDY+TdpDeWnxf!`RPsxGQR^&i(2(>jigd9$_kfpXKhm$+-lpIHmAxrH_mfDjnHH92Uj;Hn_$CDGNJ;({<ZsNuI=|)W@cOzS=X=E!oiQ0!OHIbY|?n3QE?m})yjV4QtAh#ojQA5dLWQ`g`mKs1#PxGqg=lxHA5nmjpEV@_zFjl?u)ouFaJ9oKb{k>_Yr`3=(=q}u9;yrnztU~b@ZG8)@'

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
