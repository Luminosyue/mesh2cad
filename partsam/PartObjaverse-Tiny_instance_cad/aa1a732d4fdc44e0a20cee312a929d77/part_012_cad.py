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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_012.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_012.stl', 'source_sha256': '1610491767da2565813a68c279da0ad6256dcee9919e23baf0bf243d959923fa', 'input_faces': 34, 'input_vertices': 43, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17977914214134216, -0.14077875018119812, -0.1499418020248413], [-0.12038831412792206, -0.10311777144670486, -0.09702110290527344]]}
GEOMETRY_BASE85 = 'c$}qGT}V_x6rSDnZ_`#YQ&&x|TCRo#p@>N6`h!}ME<#XXcvoG`SY6#U`w?O3VX5e;dg&oq2!f(|4Ab)7U3U#1^P!*z@g+lZ&7c0%vhJKY*4!wF8aRCCe)rt(erINwvDE3p5(pca<YZv~>ZLG3XvB~N(r<J2b++1E2fBOCYe*dMbZp`E`eR2eCp4s=44B$%u2!e1L@*s{FE-^1rgn$3&uQ&$b~xK?l&`khT{eYxowD}Wl;_;Sf_$MMFJBlG{&j3qEXYLnOrjW3?gOms0wm<+1Vu6GE<C%dZUfG2-e9~w#OkV-8UM8wcv&Crr)aKe0Q7!Y5AyYL?E}Vd3<r6A`S1qt^7_>v?}yYK90y!WQSs)1M-tD^Xd7gn7e6lsczv-nR_1wGJ0+?3Pxk}7Pj^`})B7j}_`XQ_sG9#~lz5(eh*#@W7=1kNCPyR{|9)zm_vx+dWPVrgjH~*sy2a{Oud#Y<9{f*sO+SVHS3JPGbuQrDJt@F@SNhrf=~kG}vm;}GD~(J)Y?9S?d!7I;7mf4tLoQqal$W%?3lSO2Pgg0_3rny3yuQ0M3G{?_Lu?;JcChvBs%QF(eSY4*P*wxz4HYw;sGF=$$3v)}S%~xVeTikb&I{8%)&A^lgnrF$hkPoXGg;8DJb%&0`!S!}1YVrCGo9tZQP61_dJMkio0#v=<q@dwtbq64xe{ErJn$!r2B<gBr2#L5Y)~)T<JtQ+ep#jCc*Ode^|1Z2W&__ud@&5~XPa>T=0?~$CbGU>r?Yih53*-#5&T!2T$XtMq&J7Hdr&W_>O1Z+UxDXi{D0l2J)@FEb&93iTaG7d38A4^PO)|?cZ5-rjxGHC5!PAwS4UVu;eQ`t2E{|V61$a1QzAu)T*MsAHH0?82E|CsBk?&2(TI7X5_CGU5i>ETEk~nXG=4*KdX7dZ5s$bNbBep@S|Vm)t|Rn%V0tmAMe|rCw$r&qOvIe}N>ySnq6u?)ix^PPfLdF59L@{H49wFp&qLgYc{tXEAsR5(qc<aBD(1=PZ4Y8L<`GKlKs`&HMw_7f)7AKMxakC{F3MlORBuQA%Lzs6$L6%uh135l6R9P=)F`a-cYbozqy'

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
