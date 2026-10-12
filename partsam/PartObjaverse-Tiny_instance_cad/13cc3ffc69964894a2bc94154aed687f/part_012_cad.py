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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_012.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_012.stl', 'source_sha256': '9cd2ded7811fb2072311d699a4d5e59b9ff0de0bce7f6a8e99b6e34b641ecc77', 'input_faces': 51, 'input_vertices': 59, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15437988936901093, -0.10501710325479507, -0.3077515959739685], [0.1543869823217392, 0.09990356862545013, -0.14917533099651337]]}
GEOMETRY_BASE85 = 'c$}q{T}YEr7{`yBmYJF6DyOEercG;_^V?-@-ROlRGy0(K4c*W%Kc<M0(F!c03oj%Pg_uZq;YBF<F~v5W5k;2hMG!<Qf-X|9Lb536JZI1B-MbS=z4Gw?o&S5@a~_}foSoNDCJ$B+@0CPabBiB_ZXg6AoG3_(+1gxFX>Q7_Yq%UlBAE}DPdm$xA2FN?A}!>Ks><9{X;o<jRk5W|r503{dTX=QRCl4?T4e^m#8lg4rhZeksliO!X?aCzAtzleTowNH3Zp3)$EMv*s&>o!aZqE$;&Z3SH!i&z0Tt9g{Cro(#|NOE)VW!)Z)-VopXuVsmtvos2=8O<!P>`uzRq%wY4_1No-ZuRnD2Vh@AX{;UCd8eU_Qxj#_=O=Go94Tv;QaIoY!ydXk*Xk3@tEqR7`>DYj2I|;QqmS<{RG>O^N4qWhq$x_LXl=)-LUIK!2fomW{6;P)_oEA;dDl9sk#egIj0x1L}-^K%LPKs5AP~db&z`n6HmrX8E`x4J;qqc)Np_zcK#0gI8z!jW`Fd&g9vrF<zaGiuqAq9XwAz5A)`=w`txzg1nBk_p<v-t8TF`9mnSfyqCjYhIPF0@63<tc;jepI(YpBXAf&j>*g|)kLyHvdWODx_et+*=KJbzi#pHNxvkAI!JAj#6*I}5_tL6!JwAES$KH#e)J}=>F=oWL#l9~ez5Ut@yT4K~#mh(P>r1k|<4?<{*}NBJBRbLhmHNJYs=s^It>df*TVu1=m#iP-p?<F~S#O@N)6AFd7pZTrY;}u$=|1xL(tYIfZ9fMGc;k@QZ`uBG^@h#(^_T3swf>Udw>4j~AEiF4o5AlCIZ$m?e~=LZv5B4{7L(`*0TV8t@{f?3-1QwHn*TmRHq#v7Gz-S`gJ^8U0FFeJAx9!dp~{h?khjr@Mh!ugBgfF#NuVg+01idnfgFmw5j7e)8pi<E(8!^YjRBm8nu`otfSiY%j{#hWT7+DPtVPX2)*@%1?negAL<UtOgYHEJ-6!Hb*alT0htt?XBMbvL0s~lqx*Zub7FmI;MBRm~M2^P*PDD*WPDD<^d?3G6)D+|tyq}5zETASJr_o5Kk&L<<IT<;QhM_D-rjY;bGwaV~gN5ez(ItJ-e`|@KETLnqZ8Sq!2>U{l(Z5EjX4dyNlM+`('

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
