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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_006.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_006.stl', 'source_sha256': '04a7bf3ea4bd55a545ed16905b95fb2073ad14bb275503d8282cd2c749876def', 'input_faces': 100, 'input_vertices': 81, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.01783621683716774, 0.19624066352844238, -0.1181442141532898], [0.14564599096775055, 0.4641207456588745, 0.11925210058689117]]}
GEOMETRY_BASE85 = 'c$}qIYfM~46dnpoEyap}JOt@2uPv}eC<WH?*jtvDymq6pjfrU&VNr|$3JswlZMV@<6MtFSG`9TM(k87+r9_2V+U|u!Q){%=7!`qf{pBxXqekODXXbvh&Q35fdXtmy?6+smeCM2d@6LK#qhpeZb!{QpQ^c9}03pocNirGs4<6|4@(&gF4IGRj37lt_!10b}+P%+4kzq1w@AeOM4cd2V_Uay|-J#ig`UejTcJ}S-AMExszOnP=AwT7ZUhEw3)6ZL-r4FsEz@Z(|{_7P-CFqyjCqfhh8&7`XVw!H{*KyqS+#8%9InQ|`Wpa}9r;i0V|J14#e;e^V-G>>kpS{odfbHm6j<dVR`S&knS$ucH49^E%>}w`%Iv>F!zuuZL!Er7!UOV~fB-b$)ncuuXW*Bd}b1u3hJtWrBqt!?9=9_!Z@c7J;i}JqYTdS_XH!)K#sSjGJ)dy4IeW%kbJ+F^U$vVk0@*F<#0k7|s>Dzq&tRJrM&kFC`J8^~OA^YM(eEo379nR<MxyIKiyxx^~EhO<q(pxKXyrJ;n_*jR*b&VbSg2&$-o#hDL_|47plb<a8f+zQWwD_f_cVs?rWd2LOu6XgP%<C^?e9hyd;<%oGlE*wZ`*uj;g&w`4Y&L>Ne&6`Pt1_>7MwjG$!}*(MmgTwxZ+u_3BI^$-I!*nf4?_|!@{4_gN`9d;sN@%Qh2uXxwIcVE#2hl@IR-E<P2n}nOYmZjBHpL)BHrj<wCcKC!ux5I-<jjO6kb0wHW!llEwL+dyfzTYi+JDBWsA@K_%p7f@7HOU#GCQ?*1RTdH@IFUUaNe5IwbMNLc(`)d{D`wt-o<SB=LdkPp``R8cH4!Zz%EMefLZ(a6KJ1u7}*mb1Hb;4|>P(n>??=llN+Gh9o{<e}6S1kNc~IwfZA?wLd{6Ug#9O+8;y76RsD$+8<NNBjQaZUhM1p^LNgZyAJC)y=3zDn&1Qe*Z96>v(tL6)%g9MsgTU~zPlvH2bDbf<)5wRPQ>>FSLA&SC69<V)OhS0Oh2_4G2dUTxrBLTzNW&9`3gQfU*s{zE?B(#$meVEB2Tbue4h99cqFggYMBp7yy5s`C7j0_ajJ;Ecg|B{BZS!odaCH@l#UdPWS79Tj}*N-{?(D9w4~&Jo+;uUq8ehTF*)n0v6Ie&zy$cw)S{@Z0}}Xg_<kdB6Z{Q?9jE9|IM4=vC$(Z~dBBI^7f^eIS{*PAel_b8wH9Cn{0?gA)arqc!Oy3bNUa7~3crC`CbdFf2K-iPmDF6oGWbn=jD&cA8vHzHege1+{w`{%s3R3MFu#qOlUglsJN!m!o2hw$x$y1Ol2CUNYOY3Yti~c>7JL^pZv`g9cTmel9oeX%34N$REj6g$13k6KSqmLS=yMBZ(SrHaL2Db<wMjL(sa2u3RhUO1dXa}d<w-qjrlupGj$B@R$70%nPr~;=a}!X^svdpn0E&C09c$gdD)>!U>i~+L6+&|ZP~1BX#54nS_(kYdJy6W54!tS>ihH~WvugxymU_P(IT$9vXL>TAnc<^Sj~|CdhKcZ5?{cAyVGexOHx0Eg%!JSC*nz$?bi!wKm!iiEE8(+#reHn{Q{l6E)6jE<>G0X?wxRb7%i**6RG>Eui{ZObV>>WKnqfKW_O?c?OOF1hzi@wF0sf+r|In!`BVW_<%H1?q_@(V_wXt^>ec`Pm`zbE4Hy!y498$@0'

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
