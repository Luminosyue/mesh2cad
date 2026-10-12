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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8915325eadc4f86af543daaf10702de/part_004.stl', 'relative_path': 'b8915325eadc4f86af543daaf10702de/part_004.stl', 'source_sha256': '776ede3f0ca44193c34e413ab21f479ad5993b43bdb43a94eb4f34f93a5470fe', 'input_faces': 96, 'input_vertices': 63, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16234935820102692, -0.16231966018676758, -0.13134878873825073], [-1.435448484699009e-05, 0.15656182169914246, 0.1623634546995163]]}
GEOMETRY_BASE85 = 'c$}q|O>7ip7{_OK`?cHc2e5_GmUhZVx2<bw+0xQ4mqhVkBiY1w(1>gUTT7IJThd5~vM6oh(RjdE553qF6Am64NEBx17BS(%!NikE@gw1)o+PM|IPc8w9p0IaiP34E{D1r3|GatT*?niW+3`qOLUWFGt^cjk_fr*`CMvEawAp;&%!y<9nV#v>XG2=O?TbU|hlgK$KKoKgo7K)GkLPEO6_Uexa&+=QGNmUcPZiD-CZ>;`Djd%X|JjK*X7ZLlGc|EKZ@umuNT>94S4w|d|F1{PYC-?*_L?Dj`Dp4jp~dOFzuXY7znOFV*@Y{C{;lQDGKydPwNw)R;-UF3jR0S+uOIpRvJvE8x^g+A`aj3NP}etCE|%1OwE83VI)1-+|5bY(*Qd`7dD%btV&=}Or~k><myG~FmpQqt=G{JhdFi|POYb@Uk6*2M=7Vnz#@5v9T`Vo!RP*bP?kyPs{^GYkEM*j5uH(;3U*>bsyQVt-gU_72W(4?)z0=q1{HGtA>YQ`=b|>%m-)-~ene&Fc^vM@L_`^`=tp7fI)d=u&KaE^f^K#DqygPsL=G<@B)w$_ow^ob*UwgT<qUPn?{CVli{QA?*{M>!S9R0p|{;p}C$2{Ect(=R`H=7r{dHKEd=kaCUeCW(W&TXB!_<jAIKMgf6=jPA5bC&s0XCCg{=9!Dn&lMhASM%=Ne0k~1y#9)FpK$LFk5)_ed3DY{mh;h5b6%f0NWYkO_NBaDbLGye>dWhrzWJB4Z`^%1^vO-tclQ^5?n0AuUnFnVTwGOsch2<h=IQ_7bMtE+pX<%N@U_?Hx;EtH=i*ym_G$N%^*p7H-tTx{E4R?9sP&YZoKPN7_8Xe!YVafKME}2fL=6r6??+VB>Y>c4Fsi{}IHt54qXajhTj3_SlM=k!st&Xf-3m9tRcJX}1&1Dw$mS4SiI%~Y@HR?t0~&=J;O$oJKx@z_Tmx62VYmXWMPqO++=@2At#AtMgj4W-N^lz84X5EgWp;g(;C)v0qupo++zq#&jc^MbN2}mC96>{H1g=Ia;cB=U-3B+qU6kNGXal?l-i2<5cfm>Jvq@5dpRj5#+K%pk+u<!}4ZH=eM=RiZIDyu}33w;k3h#t_(G=VZ52E|wLHH?3@EDqg$KX-44<3a_(0%X-Jgj{7!<675s}7(8Xg@pv_n_Ty53HjtunuoV<M3v<4voNd@Fuhx-UPRy&2St1B-#aM$3x*n<ez@xKR$}~4M6?D??2Of+f~n8vet5M!rAe1`@e&*_4lTw_e7W4--7La*Z'

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
