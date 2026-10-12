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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_008.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_008.stl', 'source_sha256': 'c72a420ec9d576d3c92d8a19748e43ebc7db950b138c2975de3ce007734bc5da', 'input_faces': 56, 'input_vertices': 40, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4167429804801941, -0.4499410092830658, -0.18048755824565887], [-0.04423445090651512, -0.014588862657546997, 0.2281416803598404]]}
GEOMETRY_BASE85 = 'c$}q`Z){Ul7{+fqMoTxhx<9zBqq{56;<5l{0~Rz}`9kLA*p0?SBx9}6$;^b>EhIo-#TfOA2>~4;z}9Rs!lv8!6E`EQcLIubY}832qOpnNg9c2DADDkY?|IHMEJhQfH+l1W?sMP!p7-2ydaBi?%*j#YRjkw>JzL_PqbMTMl^kVzAk@~pDbTufYjB52vBMYFEDx-Ex=vefQno9*Jevcpn?jz|s^_t$3Qwu(Y1$TQ3;DM;ZVPP=2!E}=r8Qvqty}!TfN{U1e0ix__He1XTm7$>&1gaYzW>Xp=%r)%5y5b6<ssbPc=Q_B66_U>lodq;_31~Xe<AS(SU&47m42hW2YfPm9Pdq+NdFb@K~P%;KRoSZeud0m=G-s+0_N{SzFu;7AL_(k_#FQ8)yHuE+&BG#-gv$AH!SHEOspA1J>QjF=|5|QuZ%7{iTaaYPs#d0)b~|ckRP7tk^WBYEsT3MHYBJ{ygHRUUvEQuAM(dl=?5ZjW84j^;QPiM()R`ByqeqJ1;>B?OwQK|U#~mfEB!mt?~HU}UQaZ_PsC=V-=Se$66*&~;Jw&S(vN6e=%=NA0R9gb<G6SAe1$sItMPr5xc>^C|9nXLQ(Yfb3HEnSB7ftWFEAgU1K%~#;hn&J!$$ae<?xuuPmBzWqu!}r)KM=Feu#QqbusvdPhLg6mmfbZ^7TCjKZReXqE2M*ucN5<%go2fs~C~_N8|5dyl3(+B5(3G{BTxfRMhca|Lp?C`>|d2^WD%T^nc(cd?k89_7g3;EPP*K+j-=z8<y*T#{Cq=vAu?V!})K@`fA_%prd;X&nIP{zLx6q^1EEpaep<2`o2{K=sPm@;s>ao$N3h{oD$=PdqX3rXWtKBzukxZ7I{5m7<tzlWdElJ^eXIwnltDx=bWrxbPn_Kc6zbz!U?X+t#9#t5;u-vU#K;o$aUPZcQmTqcly}h*_o!M7%4`~Gftl-f6~z-OmWTf?~k75@_%*otXTQKj~=tpLz)ph3BeSG(DTSNY76-QL+A`LjXHxmi%h4^qJGc_J82`+sYO`%+)kazu`)S+CjHr7EbLbyO{9g|!h92R1XD>XwUuM1GDmPOX`{BW&$*<T+RS%^_88$dVllahTCk9MG4%q5&|>>!lk>?!>iN_ThR`l@5w(kYA?c<rB305&?PjkkSxl``=aUan=TqmB+0@zWFP9;79_gUYqjr)mY8QKQCiUuM2wh-=R%<fnr2Nxg`=3`Bi<|sM|JOI~|5+x#xyPt=??<ZDriyhm7S*i0Wbm5UJ<1<;xVX#'

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
