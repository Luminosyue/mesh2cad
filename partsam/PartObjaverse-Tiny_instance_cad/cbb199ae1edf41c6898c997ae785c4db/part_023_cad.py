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

PART_NAME = 'part_023'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_023.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_023.stl', 'source_sha256': '7152ce8b99061ea97bfd3f88380724f2052100d23b88e2083b2b4b04d07ce8a0', 'input_faces': 168, 'input_vertices': 151, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.43123728036880493, 0.18604302406311035, -0.16765096783638], [0.1333347111940384, 0.2797674536705017, 0.16766323149204254]]}
GEOMETRY_BASE85 = 'c$}@6*>6;37{*Uq%Dz(&S!7sbSSna3Wv4?2v9v5R>}5Trol03snSrv)6c8wj>=-YUF`59uc;}5b3<iX_MZLkqm`q|Ke*hXUl<0ff=lz`X%x7YZlRSBz{^tAMdFRY~&YWqax}Z~$)A1PT+#OIg;Z|?Q@zm2Pa#~{XJ&kp-#H6O?19?v0cJ4jYuPj})BvO;-v^a-?^|3@<JUA;5oYOEPSR4p8?27M+*EVh56|awZd|~a5L`-;MYi)B({vKB{t)w_Gb$oH)NZ>y{x=Rb8`nP|$>-AFc&BJofukU?u*TUVax9(^2)UvT(c|1Vtl_z<9^r?M4xUNtBG{xEvbC=e0Kg_j$s^-VXw))InTF>>FYyHgkE!O(XU0ToenVbF>efgcWf8s8!Pb>fZ*8Oq|4?NrZAe-mBU*g<PD$>D2RA0G+`sqh8YyZr(f92di^8nT7{+TDKKKIXD`*#y9U)cI*uKg?Lewdr%x%>9#*3Xx?OY3t!FXHBWT(R<=^?WDp()yh9ow(^gdMa)0pSVlwbNVN4t`A>7`p{ONxl8MFt`Edb|DRpGZS9}9OY3v`CvN6#)F<z?^QRB}^GQ5s{VxxF^Xc~g^<9r=ipu<RMO^C`KCsMJC(!&+Tl>1w)^FQ6>M&2Cj`GmQPps>e^ZGP+0I%z8Uwx^4{iip4b(m`%<!NxO6RJD<R=I7SiJN%_=j#b`y`CuN<HI~f^_^+0_CCQge{|H(#Gkxl>z}##z5wU`nQQ;bxqs#<s?Ys1*Z!TM3(~g!nQQ;bL(0#T+_CY@@n<))c~beD-)@#$cse}sPB!P`!(5M#az0O$2lV>?=lf9`57j)5`s&d4h~adfW9lsL;7;BLQ5z4fq58_HK7YQ<Q}nuK{aOF<PlKmV_>aHxOfP?*%H1k|pUNHjyiA=6|L4W?#+>JkuQTR-foJ;o`&8~$QlE5PN)79G&o<A@&GjFg=b5?AvvQti<~q;HbMD`WoBKELobMyzN$Q{HoVm`qsl)es%IQ9zdCu$7{4>}2H+5+K&2gjoXP%<h<@q<qljfhf&OdXVf94K-zC8bCu4w+5>-?L!qVHekIq#Rw3+8%Wm_D=5i-_-6?u}=aVYjPn5p|Paxec{hKXE<iJ=E<#aT`nj-A~-I8UMpiTqj@D8QvASi{mvfV+Sul&O>(K`N*BIw+p-*a+~P9s1d#s`I`6MMSI|J<el(FcpSM6>(0ZkAs-dBddCyK1^J}tgs1^tkGuu$!t0TbVqGizB=S1ZHqn0g8RP?^v!eCz?a1qq*TJ_T@5kN)@UzHkMO#HJ@YBfq@SbbnjmR~~YvEgwTd;Q@ybZZhv{)2@uSAZDR*4qDmmn`fu7oc}j$m&Tz6!a&Xpm?K`~~Epq7kA2@aK>RAoqt4LLP#>L*XNk=Za>DUV&F2FBFAE^Wd|Q^|`t5dB|bxoeiIb9KzqH;g_?HpEqao;bCNbE(D*Cd<A>M@QSQGVXV;}La1{YH7;Ynm%a0;ljwE$ab%s(0(c>^K9>*IbMgfC7Q#Da?J2~XLU1on5tWL{;4_e?i)M<Z!lxlmMV<mLMJ~hM>F}Az6GX+LN${7ECyPo%6X7o*Peh&oFGik(y_4Z3$fHDKL}TIOkb|P}qS5ddkw+tsf{#HSi@ibkcx3NF*;CXT-WR!#sGq0@yccp0<nHjE$i1<*54<1pInhPY4tO*2b<tJPUU&kz8NLIaKt6|c7va~DlcHmyT6i7uDbX9E*WfYaI(RKShMdH@WAIbR8$?Z_gYY+z4~Z^_Ho|uyZ$#bzZ$dtZy@%izkT>ByABJB<J|em#+6>=~ycu~Dyczj0_8x&>Laq`m6)lIaMqVLWBdUfkL#{@yf-gm0j=d}3YmmL$gTbO<@Bs2~$Gc^4oPqG?kq06d!3QG`!`|WWk;vY?$Q;qD@CC?`>b(4-f`9rK{NInH_r>n}hdl4}-_~UB{8?(5o192>p?5DJ7nS_>1K;Xh<(<C(qHS#7'

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
