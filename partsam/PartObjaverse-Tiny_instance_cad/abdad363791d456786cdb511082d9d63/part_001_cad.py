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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_001.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_001.stl', 'source_sha256': '9ebf5d5fcf0bbb5d8151d17a07cb36a367aaa5ca108f06996ff322a9bb0b8753', 'input_faces': 76, 'input_vertices': 71, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.014426792971789837, 5.107017993927002, -2.910902738571167], [3.369377613067627, 9.869258880615234, 3.121755361557007]]}
GEOMETRY_BASE85 = 'c$}q{e{2(F7{}js?Z#NQ*7bDEwQ}8b?Qpb=jR9qFuc*X1AkC5~iqY1sV;F_ejUhqFxx`IF;2#r+22AlsOia`O${z#VVMOPMMgt}UVpcQ?$#AZWm<@yaKJPs@-kV2a^pYpv?|t5TpZ9s6yX!U9l;e<yegw#Y{bk!id4xc?h(vmlsqT%f$*%CG&h0kh;T#S_Ut8O<Cia+(^pG9Fwq#dpDj1c64ed*U)pD?XbE-R)*!0xqR9h1Gs>HKhNyfW65}iqQ9$H*eE!S36%P-3R^_a~{h@alIdyuKT_c@8e`Pi{3IM;@CuDVZD0H?j5O~5%tE*G`x{Jn#A&4R~w^g2N0uaK|1B#GCjhs^7$wD40!;F<iEa-L`Wc&=u}E5~P1fg5!idDJg3e{r|WukUZn(=2%A@hP51+j2gu2z6?|_uDj)<GyamhdXk(j(&Mn5$mjYlh^+bzHfxDOGmvEicr7i-gOn~ODBgoH|k6`m+<;$@_6MW&y#73UK8_7_u){-B=76WBl`W_8J^_*+MbzGEc#DYJb#00p`Yg=%Rjj>Xu)af7~%KV;ED5+c)hmvIv+Ros}8j2eVf7Qo_gLl^_wai-{<Rp=+DW^N_J4-)6X07%+b?2$39THnm<=Fd0d*$pF`T?vy1tS{TkfJZ*cjM0f(v1kD~m(s9md_e4mk5$~gZvbWjnvdi(<Cao1ZHOx!W(<9yDCmqni0dU!6+^Yp^3>H6|_dHw3Tq2Ek=qB&rdN8R^%z-nFk<XAwgGk$8P)6}<YqyAo>ddF$HU)YCuq$yXte!6c9O7nOh3jQ+n!Qk|vMt#2@51$ixJnHpx?Qs1fa-$FGj~|SQT-&fmU-$a@D<V&y3k9t5Xy5G)SglLP51aZxfBl)iH}a*eJ}XYn9@XoAV&Z#|)6NaNemd~XPa@Y&{3%=UOu?f8%RIf?O!a8Fk=gvZuZMkBT=qKkb<d8T5qWy=+dA)i^`gkt_cO8;r&l5Yt30xMjk%tOPjasPaFOR%-w2P0Jkxhl7CC+4n!fI$X1}SQ$jQh{I=|e1M&z_FD_e20KL2JtG1FJJtmH`C;~)egpM7Q96T&AJARLBTe_}V*{ku<W{r~>N*035DvIw%ML9Jx50M88%dJl`mEb3V_pa)%!Y!QoP=$GMG1N!^XgFb+B8Uzn|ALfAhVf3K$k->Tq^bs5jqrV$HXa&v*3m&wb#S#`vS=6Gh#r*?|vZzB}hhw$qtI&gna89k@L)g1j@Jz5!(1SjREQ+})s)Df;Yf(^F;2cHppetGAuz-JOZuFpq$l(7{G5TU0bECftJ?Nb{$1Ql!5*BtAHWnWApe|&ySa{KUam<5WMi1)4IUd1--a+7nAS9PX5qi+uklFFtT+|{A7tSq0EyX!Sf(P}pa1#BH(1YHN3|_ec^aVI3p`U{uv<&A+f(M<8`@5IGYp(kM?hRNqi+Skh;aC8@AH5%I_2IeUOL1?pCYxQ#xz%6xn}-TF!Sn}y=1lX?kT|oQ<(mFciZwZ*->ms|vW4j(-l4w%@P{H2'

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
