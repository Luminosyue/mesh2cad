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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_003.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_003.stl', 'source_sha256': '55ce8540db9ca54637ab23b2fa3c9f054523cc046623731a5ae755901d9a9795', 'input_faces': 68, 'input_vertices': 72, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12212668359279633, -0.0923030823469162, -0.30596721172332764], [-0.03303816542029381, 0.24574190378189087, -0.2695809006690979]]}
GEOMETRY_BASE85 = 'c$}q{TWC~Q6oz*$Y7&zeH8mO&bE45n%xGewW3J}JTm~8{gJ94ibOxQ&h$e9+hP3fAAe3T!5EXrsiP9JA{X#9$X7oiY6pf=G6eRUAFIxK0QYh`(d;cfS-e(s|d*J8)=bN?GS#xqSX97JLnT1Rq<t(=<=SzDYV_dnckd1^R!~J{0(e(pEpQW(^!TI6%*=;*M3hYW_BW%pGHyqs)@ibYUmc9m$*YflYMusDyflme_d&8V}hYm!;#H0H{Lt%Pdxw+13)mM3~qt<^ta%hFbt&Yh_?%s)SxW|4wmz*?k7CT|&)|m<;w|6cw^4R`6&yDkcoiK8{f18m9Ygz=4C;$B3w7<@s{dMl_uXAUA*L>{nnveZmbFjb8XZL^bmEf#y@Sd3e%dw=9Kkg9q_V{_hW1nwQ>RlZ5R{3Fh-koDgz0TRmPI;Z*h2@+JTa<bi$NXTTSI(KrzbkzCXwt;(yRCBn(|$Rp_~o6{dYwD<EW1?l-;3p(*RtNlQ6GPmC(mpDtjyQBQ$OvW{!YxR|M0e$_u_EU#M!}SQ6DRs5<D?hpwzqgl_q&Tzql-TY*(*RuXAU9u=kui@1+u@Ugxv>ycv||or&KRpKEA;(#X4O<o$3vD7an!sZ#IasAttax#z-bO1;h#S+(->{;@{x`EgXKcX7;*|MWn9o|nh(w{d>sl##P*kETT5*H`6rIrXhluk*yrLs4(FkIOmNqe{Kbo%xA^Ba-jFqSWi$na@f`Cd7G1ho6f2t{;p%@#B4Sed9$l|7+aHV{aoy&PGG#^ZK`&=RdOrpAOE%1rHA>`|I4<-&K$OT^#%C+}U5}@q0n@d9lB1KHoo}JbfdJpS-=9!5CLIJ$?H^DUV(b`Qf<v(c8cAUp;z#4gdSm>!TeulQxkykm^ab@H%Avz7Na?&htj})u#0G+<;5b2v0+9XZ(WDHG^j%GxTJ^ZRAGuw!^cLn@H)TW_Sj22WdWOD?A4|9X&blt;o&j?SRimZXsooTH$k$yGVJYPIxYICVFz=oye`|?SkhaZz0VkwZZ2h`$-E(-SB+mx#-D<cO$o<*AHKS>?N%yt%KJfSCOhomGHI5HK?nGuSNEvuQH{d=L*sq(rUN|xtz3$WWiS=dr-Fuz7n|teO5|8&n2W4q*8bp@-otL(o%Ra@(R2zLoUYaQoLW1($8P>f7K<V58y?}3rUMf1@J}4MX2K}(36&4nDI|Pwcj5xe#0t1y!B4?Ya+Gt7|ojf(g^g-;eUU+iPPC3@_v4ovcCa?(c@e'

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
