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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_011.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_011.stl', 'source_sha256': '67e1a3b6997a051d75c53300da96aa39d0a17d8aa2b3c00cbf64e0d8d96d5d40', 'input_faces': 80, 'input_vertices': 55, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.44436410069465637, -0.2099791169166565, 0.12655621767044067], [0.4634816348552704, -0.16151300072669983, 0.17899787425994873]]}
GEOMETRY_BASE85 = 'c$}q{ZD><h7{^c2bk=LvXq#%=wDm5li;2<1zR}5CFDtl7Xo)acMbrdMwfNFD?F!NfaX2>6L2=#YCTyjmtxo3{m2IH&nq;=s4^nX-hAqSw1QjgWFD)Bm_nh;uz0c@iY!@E>zy3&`p7Y#$4+#Y`Yz`)`mze(&dp3~C7_V&RV4cxeNAvb*`>K7d`z>st@cf#|PZ~DXhc;PQC+l+Wh_-K!x!0)f*P3eFKGogS66=UX_HAp4?TB)}F0!XRYWVhDk=Cg3_wuSLpIYJZsRz{mdMU;d)XvtiS|j7f($_BY{IguIHF@?~{V?}>-3984)vLna@+Qn)d-rTg^l4~JiO&rlr2S8B(C6}6d5`F$jrCCP|3>)u=%>^_{X+WVUlPxhgTklFPE!AdF4tLfiuQT(9r5b0U9R)(Uy0WjOpb^?j@!bA?ft^{j%*S>KBXkhUO)Vn@LFH4@cQ(C@aev8InRw9!n29fa&E!tA-S(7#IqkJr2k+_c=i4nI?s=eB+Q-#8{|3{JtJN}JSqCbiyxCdy&vutUf+B?W%l98i16(E8R7NhIXchgO3|OWE)uVIttX!CuaI*{4ic~RCuM)vB{{eEbH>TOe*fx<m{)Z^@%oX=#HaJ8<UH5bB+S0IbgSG~;}$vpyJ6BtJ9J(?hkJI@{zFHJXMePb{_%SI6|>j!qT>0F-`Sfm`*e@(7tv?%Ju$a**XOkV<CyHzc8vOWnuXUg`(z&{-mmVbskuDsnj~I7a8dkUw)5dtvHyt^at=SfDxaV6HA%DA?^Vh9fB(Ah+Kp3kUm5qreziI!VfK36xby`%^1Vy-%lUZEj+pPubKmlt{QMys{rspZ*YmX}Y4+OnX|ewJ+Pf*U4>umA`}%2s%#Hp0v3wrBJx!k<OB?ap>S4K_^<%`VUh9zg{hjgQ?os)FAKgsVhR7*Dy7|ok&1SSRYQAyGH$_ZGJeT~M$+?gC=E{F{#McD=_YuFsSi?%Ae8^Q`AJ~tq1pC2ND9$carP#hK&MLA3tb&)KIG3R~FGH4tmw}zgVz3ju1X%!H0?tC_f_c6G&H~RvaaNGIU<I6q;#`O<02hKwki}r0E5IdS57GzrVU8XYXRlGOAOlE0*pFEUP@Jn#oL@$|z!^v@(gk+m-dItbEl3q?0W;)MHhXclA<MvJxKB2u6YRwOupzU+S(v*G#W@qjc|KABFF<A^6|jPPla1p1B8qbkinAT*0NcR}QJfbUm5*GEbbuFwi;#I>o`v8da4E6`%+mwr=>?a9-E8*WyO9C#a^z}c0L-%*912>jj*Nf$i8*`4`Hdw%IRE}ldTg1$`M~J){16KTGx@t>JU~{~W@Lol3HBE!gEYY'

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
