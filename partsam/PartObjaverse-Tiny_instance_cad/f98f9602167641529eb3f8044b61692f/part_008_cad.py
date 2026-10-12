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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_008.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_008.stl', 'source_sha256': '699a4d1ecb779399b8456bd423005108320d3d8902294fd8dcf2c0b5ecb31f87', 'input_faces': 152, 'input_vertices': 99, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09419852495193481, -0.23958544433116913, -0.10609529167413712], [0.37140899896621704, 0.21042406558990479, 0.18297313153743744]]}
GEOMETRY_BASE85 = 'c$}q}drTBp6vpqef`U*{msU~hAmH+*sHnVT@C8VD_~0qU-Rc^REh?yuvD#_lKbkZeF{#=nAYzTSLbSC?weBe3qrqyaiH|B-Y8u-nmT1%d(WIqw&wR6;z0jm-hn#%B`|X`Gch9{$_lA-J>o6PBuL!m*?$@|$fsFA8W;V9PRkvyFN>_bS?S`!u7D_(93~eYXEi9?Duq|wxeU+<zWt}};vS+TIZBLNwtJl|Us&m$^SYNlw#r=iO*XmuGU%$q=!KJlh($W&7>9GmYcIm%fL3|9ZN$0XPk+a_a!mX+LsIQgU$<gFXJ$0SrpZxTM*;n^8U*vw%4?U;MzT&=nj{9=sn`hl7UoMM3$=gcEuusSjpH04FU`#9J=@>XgpD$l>iTaPJZ6`f_rX$<rdmax^TfXqqdo+&iWtX|KDr*<lrYk$?J|%D(^<zgjkvfv@s%BqF+joWXEUuvOvw&yhtD}c^QvbD`G(MKvMs4Y78$Cy@?RJ}ePj!v{+@0qskK=wX`Rc>N*Qu>6Y@z2hG*ds>FH+BQy|B~AfAHuk<(qMz`m@`2$Y*b~(zrbL6urI;8))3pg#&t?8z~pfzEa((KR@8+X?p&XtK_TSzf1K~|LDDJ_T@E-uKf+i=>7u{*GT(YsXv>#<C58zVq0lkYG~lcq>hKWfAqkY)c>O;`>7s%x%B-#4|4ST%Rabb_Ek$4-N&pl&7&Oun0%?Xo90O_yw_>=<pnuZAJ$jVNV@I_Jx{XQD1X!2whptegyqxo9L;S<>HemcZfajR@fBZZEX;G*ZSp-yO!q(B{Fd2Q;VTDw+RVN*HN2bpKj}GR_L<=)?b~C1u97kDI`=(iyV~7D`10KSjpqJR`Hx-nyBHOF-aUlxxwW_1+`sAkp36h#hcD(=LN~g(FA3v!z*iD|$M5;Gg~q`S`PM--{A0d#b37{kobsT~inZYe<=eW8=9i7#P3y?(|NKy&_v+>jv(I{-k?%Ra?yA{W2X^S|>9?&%eEi!x^?s>05BlW!ZY-@M_W0UfA3w2QU$?!RcT>Knl{bf4Cx$Ps6T=tRiQ$Xu#PG#+V))`Z5q)DGz4?W8BKpQUF??~Ic=HSE#On*|#9JR>op|dbtP^j2gmvQ0Bdim3SI(`We%FRC{;oZ*H|qU`_lDt%?+vA>pM3GXWccEHiPgXJHGM9;4-H>@A2#JB_fT7S-x|L7zE#_+$QR$|hCk?iUV4mtabHl|FX{P({l)7G`-|F=@eMs!*w+kS+}GsHL*$G5qmuqR`GfXZ_~JgRur;@-zp!6Bw*5lBxbGYOpnd=JXLqPAoLdZEJXgqZUE~is&%hsao`FB;JOkh7JX7Lx3OxSg;<ru1wNzRJYNx=}PSX*PoBT3#=p*3T8UN}Cn36i}f1Uw@mTP0E)*=8p9Lz6&Enb1vfEhFZy4=JyXxAW@!TxCbBfr56ZH6429a_Aqg&%Yn*rJ71ixp5O*aG!~I!x?D+lgETThX>6zrhx?Ey%$+Ns9z65}|S6L~uMb1{@ELMR2x5r-Hdgf$iXE=oD}?I1(BGjs!~x&XcuRpv8PG<{>!eK<9$F%HSMuHgpa+8=M8r1ZROWpy}WYa2j+LI1M}-!FeXWdyFY(44xT-IvQh$!x-aGcVo;6_<jkP8{_*Xp$18qn+1qO)F2UaGanI;dc<R%<|1NIk66r&jIg5~cFfHjL^SFVjk(E0M4}#%n5T4vgjz_Lw^@kEsLy1~=}bff>c@48sh(3%W3ExAnnz(yqEPD$XcjnEi)mU+M{u49eGxnn90q*>90m@7js=H+M?yz~M}mW)W5B^+8}xaw4Lkul2|NLu41Ecl49<ft1m}T^pf7`qz@^X<a4EPPx&&MfE`u%xmw}6+h2UavJ~S7ci(2O+IL|<E4u?(zhl4|*Vc<}35HtiF1Ren$2_69sga(5H!K0uy@F?(j=mhY1a0)aToC011%>yq2FNGF?mx3#xrQiy16|@{&1+Ijafh)nwpvB;2-~wnqI3KkxKyXe)a2^K@2af|kr$tGD#m{E_r+@MMeJOm?@cD<2c&G2Nz<g(bHi6zlLP>!??Z1B7-$qUQ_%Db31vrVfvH'

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
