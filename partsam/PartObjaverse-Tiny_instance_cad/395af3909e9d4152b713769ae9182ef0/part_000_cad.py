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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_000.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_000.stl', 'source_sha256': 'db8ab790f66444824d178560b9fc72394f0160da94aef98575a382151358ab1e', 'input_faces': 96, 'input_vertices': 74, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16225121915340424, -0.034868594259023666, -0.2518550157546997], [-0.08842914551496506, 0.05862819403409958, -0.18976280093193054]]}
GEOMETRY_BASE85 = 'c$}qIc~DkW9DOWqD6)MBV&HTAkVQchmk^&4;FdCuG~+nxhXU@3K&C15(z3xA*W4H;KOjm?Da>3_;kkzkT0?0z<tP22j#<s5W;t2kJ-?G_Q!`CH=FU0qeCM9~d-vXV-;god%iE^O)kV`@2@K6^rD>|Q(`?$JoczLB({l=X&(B-pq4`5s*B`iHZ055W6Fsy=+EROVPQmni`(WLklsnKKquX;A<QL{=&7Zm;KRZY1X<2g%a@=~s%&fc|_kHAmeldDNuNb{Z|F4&iy98JDi4*m1G_Sm{eyAJup7!(VUMo(Au7!NILFtZwU!fbfBgEg(Sgmwz+odz`o$dhLxY_U)a_-rnI~#sGj^B@Nd0XkO(_7A}d+X<u(2Y*}b|B}%R``vYI_TD&<adx$I{qB)%cz@`+mSQ=Y6EgR?~t55r90t&E))6M;_Wi-;Yn{O-I{Qu5%;TROODq6U8Nh*KFHVh<cc2Xu?zZ7`KZS#o+9~6ZX@6I;c<*>WK0tOvXxS2`9tJ5PmK}%>X*oIyx0x(=;H!Kk9}n~{DqCsoilty_k9iZI3CtYJ)OTghIwB5KJtx0TQL9Tj04b(>aUSwt(ynGUa$tbrPm@y|2$pRF+cT~Jl`thIGaK-4~|<Y;$Pui1OJQ%lH=$o<6fMG{b1HNUx5G4gQM`<OC*2mNvUVtfuoPt<9IzEx?_Er=z4FAYo05@xMp#t<SdPn`Cn#-?tGXC-8>S!7XIvri>SLMOmgnOgnZZGM&vt#nl1RFD`a0~9+&*^O6b=0wL4{fXG7O*3!xh}7uH4V>?`|WoLzE4?qS~=g^}{SzD@PWDPJM`GjfOI$1I0#Olu|kWJ(ltSKRJ8{C+i|3hUBlF>+j`6QEn|UfnLwTP5{e>jvHU=C16kAw8g5n>>%8u68e1V!bkxq@FLD4?{mV4fE-0yF}`r+yvdw_M%RsM&461pz08GpAi^W&)6&bVayuQJ^V3mPQPA~vw9wMYviE{)Ia1?dEWYxkKiAAR{Z`Gkz@G{fNsv&Eb~@zS@O%QgTVDOo!Ac}v*o$g)<QQXj={NMc4@+XGZ(HD|K(jp@P*95^XixSioVPX^XW=Vl>GDFlG9{Ccl^*--j}K~2Y?9?YfxwW^p9~rcpG%HD6I_Z*fSRIueEMDbSuvf^K6V+Ebn7LvE<YnZ^A#dQuf=eDWcETORye!vW{l0=vMn7m^WkNBGhC2GEBxTy<d(x9XBwpS!sxVBMtLo?5xE(<G7b3`GwJoG5<YAN&UwYp}R(3sla{n1v&QuT>FtTw+Zj5BPbNQUUL?@wz5L%zgUguGFETdFYDmD9(iGPa-Nr#NKVHCm>;Y42{~`~E{E<iCp+={txn4M9KJ~MZ;TcH!Be7tP$)UU_czM^xi0g3Zh+{`&u@nB_G!ugBtdc#YL{cZy0(}4`^1U=+xN=h@6jOV=a1j-gFoB33Hy20W$0$t8qx38t-^fX{SG;<QB|V*c*^`-zjmfR<B6~J>OOI&v=(maZf)FO>)fozKGpa^(;ng9f2wEo`&XapL5ctSQ=Q<h;c0hEB_@$897aCK-TJv(3ULT|3i$|PDtRjVjv%IyD;!Baf?Q<`<`~0?DdZ{iDBhpGWa4o0Wb$<4NOFbGkSiQYj<qCDCs!GLImSR@GI=sRiua)}o;Z*^o;;CgkSiQOt}u>VVQ=z8a+MLoF=C1F<ni>x5~Im`u}>5+mOPf8C}L0YNcOQ4qsXJ^u@k$I_h6syL_4{ip6*1Qyes>3A$BM4PLJZ9>5CwCA&(#rC+g%1JCQ5wK(4SOc{sVsc#30$5hKVW=m{g*$V1sDgcwF1Mvvmb^aT+^$b-lOh&FPCZO9e+k_WR-Ae-X;!~pUD`u*uq=*OnG57C$0hrA`xgIu9Tt}btKKlW+Qrg&>&OY)ZVx28v7TQ<d85WUG2dXl##wqsMg715Jip%;0^Xb(@D*FXKM^XFyafgb<I=dV4VJa!-NS>w)nbO>jRZh<-RbpI`M<4uh6JGoWVq5'

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
