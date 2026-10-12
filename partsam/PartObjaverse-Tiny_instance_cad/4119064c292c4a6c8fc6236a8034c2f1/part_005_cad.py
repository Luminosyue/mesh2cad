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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_005.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_005.stl', 'source_sha256': '9a1b1432d2c889a5cc533d7a1a71950a566c0c030e9371cc9c3a7bf6bd98812f', 'input_faces': 60, 'input_vertices': 66, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1677371859550476, 0.16155903041362762, -0.15459078550338745], [0.11405381560325623, 0.41810205578804016, 0.16058889031410217]]}
GEOMETRY_BASE85 = 'c$}qHeN2^A7(bT}3j|cUfFd8S==J)6K!6}0%Bx{&KwR0hthO%6Wf#Xpx$1I7dzH-P$~91HWaBC&Mu8uYn&x=@0A=WuB*Ruo{b7wsYO|rHt@r$%=N7ls*6L-?e!uhMcb@Z{=bU%%wdMKxnFT!)#M`YWzTQ7V2pK`bEY>+H*OV=HxDr;bT5l4gq07gEwNEZ7uq`u*b>by!iNm$L(weDQvrA`L;}vUZMdg~x;+4-=RF*iT{&;b@%VFp)XYneBF`kl^7O$jCjaRCa|M~<PC1_<YcC;I)4-|ZrBWt=J>Xc*mRm*9K+O^YHpf_Kv#&~2TbS3d5`3KA{iS{Y;PGR1La~&8jb+y6&+3k}O`xAmXrLLd9c@*nuXP}Ge8I(tzRt#UvPUw2W59CjMSI79U3%WLU+c~LgJD%Q+bxak|?GFaKkjHPZMxy(fGSUO;F2KLv{Gr7D-OH$+==L-4Z;L5G-V23X&*~odzi~EW{a3T8o*PAH<ybvZg?-vPQlKlZk4K%_$Gvs%<xeGlxAhWqN5Vd=yY0aVtou$V`lIjM-bDMn16|4et{3&>FKNNNC>^>Q@#bZWgTHUWeus`gw+}U+hQDeO`mDUS5xSNd)rb7|?z|8G!BSc`_!j*APSY{?@8;6FSIf^MPj62h_E)RYx&=Pnq-Sk{elrugo)&QtdczwH5|y3F<QHw|zuweL`~Nha{6&6rE{%N~Fs`0R^&i-QK8riAG-6&{Aas%Y8qP(%A6}3B%n6|S{jQ*I{hNDmAC&6?y8G5->htkvoUc06hyS}%x8qzy>z0q;pWjRODBvjitQ}jr7yobC16}-DfOWN9T{vH{!VO*fQN2ucCVznZo9m$4BQxmSlYHo&XFH**?&dGy@7ht1dTR<P|IM}VyBE%*`yZY_`FnrHd1<#B-a;Q@e`!aaibd3iTnqU&X0+4$x9=?7+q=}~Ny*27i|&1nJTumEKS|eGEYRJot0f_H{!fr!ufBc=^IjmmpZy+PU)G8Ji9GVFW7Bo$Pm!+gvv}!B%)veAPd@p@k`<?rKazCifW=F<2h}dXx&@qn##Y=@cWe!G_d$!7u17z+AZM80?p$~P`wV;zy2tO)?OXl#VEsbQU+^;46*Z)*Z5A)xJ*E}9o&8$5sRen$NLSeJ(bej@Hq>R~{Iz-LgV;p6_KC$y*DiH>`L*?_yO8ILPA|Vl*9QlVqOQf{ch7(9Fy`MN-G0d8rK{hD92@QzzYUfH`$_lsJ-S|>d>rE<&VMawFTDq(>z@2lw|RZ-77ukd+I)qO5nz1nN{fem>ZB+i5B~k9t}ON6ed?0__or^EQNwg2rf^6;jd2F^Y0Tp}Bu`*WWS+o0$%tel(u_#qkUX6+lX*JxEXFy^vzX^Fs?2kk&*hMOHe)t(iL;o`W}d;A$~=SlOvWVUGnqfin8@5J@3s+R8H1S1$Hxd0qd#+t5sw%#k#P+3iOeT3j%GfAc`RcH^H}E5j3b#xGmm5pU>?alg7G2d5zNCFA7&oLJe)C*c{uZNjKR#uF(1!3iurivF^r+iW0=P=nwiHjpJc>j#wbQJ^C;#cI3)LD3}x=e+?R0_b6cLt$L#x0KRy3^G<jHFKScjJ)B80ZKJzCd*B>vnEzcjnT78Va)dsGYT@$|pYNB&Y'

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
