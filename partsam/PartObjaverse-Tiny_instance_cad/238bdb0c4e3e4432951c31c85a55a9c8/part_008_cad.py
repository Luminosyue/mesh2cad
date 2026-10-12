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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_008.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_008.stl', 'source_sha256': '1a5210a1919bd996e606f1cf793f2a9b91292fef89065fe702fb523bf5c2c63a', 'input_faces': 96, 'input_vertices': 66, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41155052185058594, -0.3718020021915436, 0.010266140103340149], [-0.07025069743394852, -0.13969850540161133, 0.48813489079475403]]}
GEOMETRY_BASE85 = 'c$}q|T}YEr9LCR_TF&`BzjeNwAKP@A-(P92E+UX(HwAT*LpL%)ZJH3G?8dI@$}YkyiNeb)y6HmF3qw;<AxjO)uA&=>ga`}jocWyBv$GRKz4GVz`IDXV_&Rocy`9Eb3pu!KWct_0x0!fC*qDih4Euvaz1{x7s=k4n29g@~?BY3b?)+KrMFSZoBaR;bV0X~bsyW&M%?`Kb2=oVsg1)}X{lOkT^QV2+2L03zUhxh1>G#gYMz>bya%-d7zg{NRVe`WFa~e~V%WqkdtMTI<qIXVgsC?J{u-e~#xvuis>Qki;eRi&>Jh}5_S>-*}^cN9+&l&bR_W6VUh1(0F_k411sC?HGv)X4buBrT#?UB-Z622~~JTcCw{ezG5qWA3YZi)RvhS3$#^Zv5u{i8hk%bxd-S|9yo&-+Jt^yfabcyCkeug%_F6Fu)Qd)`0FqrdEV|ETrRU-rCzlt+K==d49<BKm)yeJy&uzvT7)vgiFJulJYN=lvzG_m@5I&;7&TdPM(cqno1F`%7N$FMHl!@_K)HecoU4dVksT{@lO1u@v67dMVt0C$RTU^r4oq4VBm0eQLilv99uS$zu_oT$-MX*!O4Gd(rFrN?zYr_IzK->-$RHbEbAd^xEE!$6_CCvi*bTc^}#HK2aWhWY7CV`TM7qRi5_@dvC;PH@<pni^Nf+lR!_qfKNE;!apEHPxVpPTmM%_UCaL;b@{YIF`WVo;}Q(x3OcpOa%3^M9BfDCgYDovI_by^WIi|pY(W-)E#OQH<3eN!xDZ^5VeCd$fZgCa;dfx%jBG;If}6mN7{)coa&QgUg|vfRU>h<IYy;;C_aYa=IE}D3$U&Nr>0lE$5t#u_1e=i-uo;|$%mgQalQE35kcHqZuoYPfwt~y(R3R&orQlNB>q-pcdSo4#-}ib9;}$v{$P>tB@Ck4`vI*P{ZbLSL+rY;$j2n<O;0ACt(gm&tJCQc96RaU~!5TORnFh`QrwV`9R1D*z7{>f!Y(Sd825<~A5gY?HBF$hUI2M@%js?ddlfiLd_Mi3<WC}7F%rXm{0?tNS!P(#<WEr>!>>!8l8wZB*F*+ydw9@g=@pc+wEXF@QDjZ%Rc4HzQ9OPF<e(Z{`+@)*jAHv?wxbRa(4E?%J(-q$3Hw2HUfd'

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
