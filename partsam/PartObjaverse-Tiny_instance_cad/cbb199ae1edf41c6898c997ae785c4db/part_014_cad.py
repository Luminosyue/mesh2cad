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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_014.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_014.stl', 'source_sha256': '01113a4ae83623bb840a4833b153c4b8b29040e77abd4b55bf50a7a921806551', 'input_faces': 86, 'input_vertices': 76, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03678681701421738, 0.12832076847553253, -0.08332740515470505], [0.05209684744477272, 0.20530791580677032, 0.10417340695858002]]}
GEOMETRY_BASE85 = 'c$}qIU2GIp7`@wVMQCY3`U9=q&hpdUmbC~iZ7H?eA8fH3%tH8yM8j;_ZA2Srw++Fl$p9w)n*b3X&^Qv1L`-~YqCCio8o-1^LW~b2WJ3fs@daLa(C^+k-!OA`NQ_Q$a?YMT_sraTXLokfsc>nvaE_=r6aIUfJx>UU3Q;W%WOK87$FehR`=(wAiABnn2lMe~cWg;N7ZL}=tFiIy%vdhgW5jwVx?>3=HnBf9o6GFmvp+YUmHu#Mawbdu%!`?+EWM6*bta7VmW1)T@n4SxbP4&de>rtQUebp@UP%%c?rxvE;PDIa?atOezV-OV3CHiR+BugD@XdyE=T+amtG4oo-oC7I=x5)AZ=a5<{{DO8%C`nbeR=lt@a^qR-oEkG$Lji%RhPVZbNBU=>b!4`{N$Y%`zCz*hBGhrZTLJd-RF6kTfg~8^}kVZ#dlu#CVVs1qWY~Zzn@S&N3Qzj#eM<4dEc3r^~0~n)O@XDzIm}P4mrN@a!loo+0c6`fBVymYF^Q(vp&-=yrb6dw(0oS44-eYkNH}A`VOn>zqRT+bv*-3&h@~z;p=(!^H`t$=fj7T|MO&Cz1|sd_7{EuKKJN;QO}Z#s=qML@b|zk>VeNa*1M;sl;6DKd-eLVvp(z_F~{egLdD!mY8{$?Q|n_Mbn@)m@Hub(HMv>!UO%hOYu$0yjr}})J<mR0r@d_`lMGll_Vsmh^V<5jd2N02=Ub+O`q|g}-MrTC=JoZj{PX>we)fy@o%8zsa$f5<KBzq!)X%=&@8-3BH?Q^EpXW~ou0Q;u_2<04{+!qP#kpIb1ogA8_q%zm-_7g$n;AYGxWDj=_LuYe{&HUHFO2Ov6V%VX-tXqMemAf0@6?xH1nw{VqW#r;{v5eI`o44iA?NjdZ=`)s_nP=?O>dP7Au*qx?h_f$qg|TvU=Dt?@9p?kkM{2W|7e%LFdiX1N?1&&B0L6O1ig?@Nhk%ELCfC-^9doafGz`<f(7(K<SM}npz8^Zgc0y4^kzbe&;X7=^LzE+2Iv&VM!=1pF%e`U@axetijGl?m%5HnLRbkdhh8P*&ov>Ig2T}KULANTbOpwS!6lwCVPwMa>(En<j&h8bdKlL_2p)o#*Zd6OY49fKA@Cr06Z9~0BVb<VK7zcLd%zo^2MGOyr@+0?8^Jx`Ug$pLlHdX8PC^%99k?BO1EHI+9^3)l4qgZDfbK-D3%mikjj)E$3SJGpmhdFu32*{>HMkX=fNn!>4R|edGa*J;2Cj#0A;g7qKS_REJh-<Sk!gg#3_Wpl#4%oKx$nz`a}P+afnI_4YQc5TG808ka<ykn4Kg+GYta)$M-=0wZXy_jC4_V;R8k#&*k6<fhowHy-ajn*NdMQLcjQg#a=#4IsWSP!LpOhkm?r*Ao#h`AX~$v'

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
