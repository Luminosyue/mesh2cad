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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_003.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_003.stl', 'source_sha256': '1616b27f578a8d80abc0114c4e3f733433adf05ba2e1d6a67bb8a509121b1aa9', 'input_faces': 100, 'input_vertices': 91, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19128422439098358, -0.3184795081615448, -0.4999995529651642], [0.191738560795784, 0.1182035505771637, 0.16008985042572021]]}
GEOMETRY_BASE85 = 'c$}qIZ%ma{96tO@xFM2U13}{j!HY$BNliiUqQON1@hV<Y=jOe^Wzq@+%!;tx57w4*)s|B})m_eVZMBh%Wh=ehftS{nnYC);-}*!Pq4np3d@<{H&ikCpz2}~`R`2%g_q@;ZJLf&W-+S)i#nqUUY-Q$Ez_Q+Wq9!$sF^+U*Wk-FzM>^YlePvyTpG#nwLg$x^uQ$7Qxb`KmqwINGyRWaU*H&rRsya5=N)1~_ckhv2Z`Z-@-gY0?o!%$=e5Cgs@*eileMv=msj+TNsd3Esua||E;9&z3m-$*s4!y{ukv|x6Xmob{*jTJS*Te5wT)wH#ere{jH(P}6f9CrkF@IIkRgpJ*`wEYq(*+?O13#UcjL}c_2SuEi7J6X*EuqiOd%qHTU;30z_uoDs^8G7bh?zflt92?`_hbIRcdrWFxX~~4;LyQQG2gXYlR7<+++(hD;OB9X_uJr@xL=ep6Qj@lZa(*>Q|L7po*LK9uj+FCKzh@-u5ZD!b>q4|sJiS!@Qd7#Zk-WbS?BE4?oY({@R`x*e5nVW)0d<3*^P4_>-sEpwa@;qpVsC}UCp1(dF7&Rf2z9Np9^~I{#13jKmBPf@9OH6x?1n-)VJq#>z8_5y<H!^qpcUZnqM<^{B3dXz9ZJ-$qUa!>;56P$T#l%CG<dQ+i_igR9*IGL67Z^s>}Wu%{ebQH0zPNx*pH`+zE%KUa7~`+c0uUmoIfSpS?eG#-XWK)n&a>_n+Q&$)U-YdJy#nM_xXwn_t!C{8CrvSM|vJlbyr5dZixMp9335wEck|caDWVGWDCkn&-@W!!t2@UA>wA+Arq&a!y{-t&@GzGOFz-bT!{&JR8zIH=--gHLhO_>FScYT9;??nl@kRarxmAbN_zuqgaps(?6zT^z+qbzU^`IcU_QoMeKX!Tvc^>u6jPJ6}oz!tGYbTjSg2>m#^xPzb~2nVcmLEJ+huZKM!l`mAX<d8+1?T`YCm_pMf7vOz3_WsvbFKBD!+UD7rXjTrpo!16l1C>?w?Kq|sMYhd1gIii`Y`QU3|mx&B{$LY3R?|MMHlvX$1bjsG4A8wl$O>kuCT-$;0vP=UA!TzVT2E5P#!_Ysm16TuVEqLqj%z@?XuxDtFnVIScE#QVY5@b(k-B0dH#z5R%L!FLcE3C)O2;5!Ms;O~ORxr?wH{%&|XF{TNA6FkoECM;t7li7@^;7bTg;V*^9c_twXeipnX7?TP=6&~l061EfeAhv=x5bELA!{fY#;D+yp*MKpt@LS<=UQ2Ki9zm=F=li=Fel<MKw-Bn}SHW{&Odb3>c$_~-SW75HECaU@is2W-<9s!t2!0Vf8^)BuFN4Q<0bv!vKr95$Cgj1-gU9*3gk1Q!@Uk(c5Pl&%&X*CE6Re0i;28u9d<#6z)8H)zx8UB2v5OJY!0m)`LM7s6@XhFLC1Mr0BkDcWqVHSqezv3cJl2ErJt6nY9=!7g^mBDo&u!pEsJ|F-6}W+Z$R1{c=c1lG#O2^t)VB;VBdR|s=nIc`f!pz3%MsUtCll^Lo~tn-(VFy6|FSMzesS1D{{yRzj6J5KM>^>?a%j66Q}}b~5KCk|6o+^f>~BM`k`w'

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
