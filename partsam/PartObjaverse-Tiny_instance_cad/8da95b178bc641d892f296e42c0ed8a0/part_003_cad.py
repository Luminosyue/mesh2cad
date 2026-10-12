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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_003.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_003.stl', 'source_sha256': '99b0408328bae3071e55f9323f668a26c0a890f5a1941d1e36550e4671560bd9', 'input_faces': 80, 'input_vertices': 84, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4552704691886902, -0.08603677153587341, 0.11053723096847534], [-0.4374975562095642, 0.07046964764595032, 0.24307364225387573]]}
GEOMETRY_BASE85 = 'c$}qIO-xi*6u!ehh^Rots^CzBK^+7H3!>lyMXaEV8W&xasSZ)w3J%t$Y1%#$bWvl~y1>Stf@zxASga%(HMUM{6Mx#$rVBUf!gS@vu&G-;_rC95-#s%;n)W4MzVCjVcRBaxoV<y2r)Lxk?<p7e&mZ}qFGmQ8d{Hd+$Kv~TZI2Bt-81-MK+IIWd^Dffv~6SL&4Ac1J__xK4Q-EyT7scf{mr3pFw{Q~-xrVWd21lPBPRWI(RYVp<PYtP4#sF)-P{-sHY^GUKMwxaCy!D{R8>5>N$eiTx*|EzdFJQUK7Vv9_p<UASKRXZuJ-#%Zd-m;>xAN;@)CYOsQrohyMEuvnsq_4XzKjI@-sc(nHst0_r;gh=M*pLx#9N{C*faRVa<~m@qDLm_AgeR;i=<_2P%HF<{v+LELA@41<y~)M_jFwV~4F*^ucHA75VRfs>U1USow&N;bArY=7=4C((~P?=YF;P(I<zL&(1}R!Dr_p#{T$R`Rsh%-D{4kam2Y}#lPeE?%Ju}EWhdT7iv6u-S$hzPpS2mylwyAGWefNPFnu+6Q|`^>^*Gx?wP>XYJ9lJp69IRi>-f7rt;m~(%&tA<+bx_Jjmt`hrd<x@H}ha^E{t@Hm>Gp>ve~t7nRTV?V#s7eBZkM`d*Fe4_W7!SpME6H4i&??K|w;-JZM&6_5MlZu{<Gs{5~fe$U;nvLB|ZckT0fH}S0AjnC>``@G(@&+FaztlqWH>s|Z2u1!3vUy~=RUlY&j*Z8b{jnC@W_^f`7&+6CstbUEp>i4B@*RNR@t6vk(>e0lr`Z7MN3*)nUZuXzuTNBUjXX5YY4^rJL?I-nr?eqQ*KdJx2PwMkJp7(S3N&Q^M^Zu-T-k<e6ynpI=-Vb#=?{C`YeM$Sg&*=5?zM<p&`ya8sPA(2yy6a?6N`zecI_Z!4K24-4AI+&hO?EZ@yHAt4|NUvQf^wK8j}1HndMQDs7zU?7R}w;m4#HN#7Qz~E2XqHwr0&LiJ%H5Bgqh$O;3nuEj5h*OxBA{`1-}Blmate}Q?P)RPXM}sFpaPrJRLe4<9fmygf7H(!D|3dgLViD2<_n4pfd@zgmiEX^c+GPa&1GtQqRNt^8Q2!y_mZfo&#P0y&3;!3($@|ZbuFs;7aID<k1DxVjZ=}wH}-ey@Ak3SPw|O44e-wITyN)kR`l3A~^$kJ^sE9(6P(#ZXGxax{x5trUkqTI)MFK0<M8>!MPQJr$etK6cJtr7eH^qzV`xc*w;3k&1&#G=n}$g!mD_{0DDk?^-H~oAiw9U!8y<+cyBJa6nZZ7d~gtYK6Dwl0=f*k99#um4!sZ@f{t_t(u&jn>8H`l$CaCE{ZQg>+HK4K=2@D{G_go`raV7t2x(%kT&z3=@dBL_>xB'

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
