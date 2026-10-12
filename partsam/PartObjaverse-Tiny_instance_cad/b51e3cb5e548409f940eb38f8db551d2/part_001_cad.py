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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_001.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_001.stl', 'source_sha256': '6fa391256d470ab0780a4320cb39c1c9f16bcdb93da951492dddf0a6def42e39', 'input_faces': 64, 'input_vertices': 52, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.016433045268058777, 0.21067604422569275, 0.051355861127376556], [0.0768652856349945, 0.2610817849636078, 0.13803087174892426]]}
GEOMETRY_BASE85 = 'c$}q{ZA@Eb6vuB1tu2MgW_c+vxrNn&gF0Sh1{b*r(-}LqF4K%AB$SLct1&QIGP5n3;@lTM%qm3DDe26JvB=DHChjGAF(yku>jIK2nThzpu!yMBC`L2mea`t8d5k7TZ}Q~->yOjJ>2q(NG~mz4bt-(hmB`S*t09Y`h?TE6l|$j!V03>t?&~{v*rXJa7gsiicRkV(2%3~b%297`IKDsTZB@P7BKLUfRBxm|HW=&a>+X;BhJ}Bi=dpO$@bLpZ2gAnen!6k8)TY`x^$GRAUU_1Mxw+&AMrb#EnKmQU(dbm$8m})lkY8xuM_$|F=la=Z^7^-XxxV7~v*Z_B$ZM`n_O^@1sn6WmkHzbd)hGM+&yi2;C}&?h^ECCj?-F_aaw&VywPWO;{E&UuM)unq_R;?vAD*E;Uo7k7M<V3)3rX^Nlfw0{ob00d-7k|@$1JixGRF1YOWbGI^$_{fuXFwM_v90owm(mGeJj&cms*s4=dbL){EYjAqvW+SX6mEmEzAC@mHfiYEcYom!F@_Luuol;ytb62eMp@eNlW$f!@NHMKY8Uy|7-Mms6^_s>h%|-KC3?clGG=Wd7S-IHfjE>*Cz9M|6AtBYndUgZ@($+&#E6)X4dYH{^O<z%8vJV|C?{f-o5n`s=x7bTJnxo@`;}&c>W)Dkk?M6<@*b-SHDF*G|l%{yFbeHy{CBoF@8?6UO#_Ydam@3>}M(0U!(oeF7tDk_1afKdj3=QzA+*BD_#73`MR6D+V0^#+vd4Xql@|^rZo1m)8v%_pX|LE^6K0CebL5?-yuJ~m-`><l)QF$_EUO){m7eAeP*6~>hp)lCw|$=^}p?*K8fJNyl*>$T%X*@{mqX`UOT#*>(B7{p!g4P{mOOfug$+G`B3uREA;oO2Pf(8YLxs!**W&{=O#Iy;r<=p@ccz1yblAD><gC2FZ`aCyuPx`pDR5&)fSLW=kHnvPbPAVQe)YT(>c<!=4cjDT-p5lqdD6Aua4%H=Kp;(-)_uMBJMMmU>EXMunSy(%ma(GgT-YsRxZ*47HI?Lg2j6pja6r?CM?1A$UDIGU@uYyd%<p`3+x7$Aq&7|;B`nl*p7Jwn~i0~>?W`U=>S{6Hq0#MYrqn`8R-RY278chum@a;ECW}9OOflqrQkxO4Q#_ag2m%>3qFS#Y(?gStzZXc7W4VA1lJ%v;2LlhvJzYcE=QJv%fU`$A=n9Ck92??m`CsyW8Gz}TI8MJT5vUT6Sx{&f!qkL02d*P!A0N=$lJgHzsc;(`KO;&e_jdkP)I+t{`yY&YrpoLV@9vlLm=R{i2GpNB(pMLWRPnA08UHlga'

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
