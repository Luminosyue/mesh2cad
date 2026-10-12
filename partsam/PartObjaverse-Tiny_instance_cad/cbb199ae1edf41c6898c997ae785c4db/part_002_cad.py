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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_002.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_002.stl', 'source_sha256': 'bacf77f6bc5ab92dae388eda44447903ae987117077afcb437357ed7fc697afb', 'input_faces': 148, 'input_vertices': 118, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.20834623277187347, -0.3612685799598694, -0.19374004006385803], [0.3623257279396057, -0.19459937512874603, -0.15624159574508667]]}
GEOMETRY_BASE85 = 'c$}q}TTB#J7{>>eYX!uDTvTL$(p?ph6-1;6t5%>am!)+ni0C3L7rDBiDQQe6O`4e4G)>yHiBDtu(!>|zQ+a6FrfF*^H@RqRY_n+}>Wh8oYai%2v;S{9^RXsPyUCaTe}3P0PQE$2Gv{PIZd+WY68;n@&jMc-e7HkVWTYsW$~AvrW~ARgT{bZ_8>6HfTz*JDYV)>wx?_}U%G>q<|8#%AUZdJ;2dnKRs(o-WFcavTxHuUY@Jrs%H#Y4Te0sQV$}g@RPG@zAT5+I6y{`Vp&kLf3P}ZG=dfCe-kJsjf_?~S2Fdv2Mb6ek<x%$oAs=U^CJ$MlHzTcY{B@d>rY?$ZgTxa$A`!|*h&gwPr5bE`J3zv*}zNmd*?uT>gN4eg)6zzUF*I7Nk-$*^XUp1#}S#sA~Kd+nT=Uiv?!LLSF%<~i1!D)VNFc{`NA1s^eiEH4I`;Bq081v_~Ka|%l>Ys6q)oXzp3+DAF?gOXw*N!Tyl7|X9!s~el{eTC-mAhxZGjnC(Wcd4H^~6=wyM`TMKAf>>UQf<xJ&EhTY%QAmC$51<`fnHx_c_tBZs{Lf2aog*uAORJwe-(;r2pJc4eolcchkK7oYVRf*FPV%_7ARsQ~$1N#{+}=QZ~%}b58ve58h5&G51eg2dDnEzit`am5~3)+&|~kKXEnb;~&la6IZ}PtX}!->HTQ+q1$0j^`T$$){J`3Z<h7sT;ug=K1)BuL#aMXKcV?TgKJl2EbGZRttau|J9W$E^(3x?(|RgxUW5B=<;L&IHM@8}8V@Rk-<!F*ks7t0IMr+UmkjPIZnxBPzODY=A8Y1%b@9)r^F;Xb>cMG#wMJQwcE6nSdVas0Q+@Esk@aZb7w7bS5$E3*asGV;pB`I}_Iu-;es2-Zes9FL{oWqWtw(#lIM-M`f4+$G=PSb5^F^FLU%r9T4P)Kd`-F2^PvZQ2LY%)(g7>~QIDa2<9$8Ot{yrqm--l}Fvv5D`eNLRe&x!N*Ip@^B-e0<DtS8%#IH&!HINy(m^ZiI2@*14)r^NYwN}TVfoKyd*`)+t1b{^oI)}J^(4-nsW9+<CtXnc?C{KL7<>iPMHI6wcmy2>9J_3S*!xz6hOd6Ky0Jn6BV=2w5Zb#p3FQDh{G)BIqc=_oIu{E$XJ%8yk3yQ6&N|31p6iXLntVh}dmhSXSidEQSEu>+b4FY^f^lAtfbCyU6y98weEZSb+s1o$M3O@?N`r=#X&XcoL(M7D@s&_sC3r9*eYXJc$4Gy#4;t}CJC@JB^BMdU-X;VHKtnh)>9*lcJPd>O7^hn|IhLxfkvVW<<Ha%IrN@Lr5{Ld)UXa6JGWgZGOV7ts#&!c(pd+73UCv0ms|`181)g3iES5ph*SFLWH9a_6DF@K-T*96APnS;RRJ0q6w$w1`O&qtG6B%3X$z!cSss5A+<oM??#1q+WuT<N8H(KwIG{=Ye*>_hW1;v;|&1^7}-TK##zeil`8=8=41CxlHJ8_zH~8gYJWm6Oo1*sV~9Ham6Cyp*!Iz7YB`pFUHuN&@^~eM2?7Is1LqCL@x5V$f?N5nh|Ipyv*+rF$f)omt*%LzZbb2<YdhdbOc`J3q@Rj4#LZ^MaUN+w+A^{a}hcO-^u1V2!Fwpm-;6BA=DH>3*nn^-3hIR@5I<9=xgxDQF91-5WWi6P0(ieCXB6u9)owI<~Xz(-ht~XXcv4H#yX$};JZ=dhBm{ixOPB&@D7Ysp#|`LsOg4w!PkkX5zzoW1>Y#*w1|4>EAaL3b<i6428?Zlo`#qCS`n{88{p;G6Ud)Ht_C?-bH>!i8RT6ePKxljV`4LH&-?4`pN}RtL(3m=e57@oH;-Hvb450Nk2_xOH)5lUHC~Fda(7ey1_&C>sQ'

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
