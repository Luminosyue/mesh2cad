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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_015.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_015.stl', 'source_sha256': '5a7722ffaa0b1ebe3a02f8266c804f114fb2c9a076a8e3a4a4d731a5f99d5aca', 'input_faces': 196, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.12066151201725006, 0.3312707543373108, -0.16433949768543243], [0.1354552060365677, 0.4843359589576721, -0.11564096808433533]]}
GEOMETRY_BASE85 = 'c$}q}3v3lt8pjVUuRbWy7NiPvD&VEG6#9UcN83w<Qd%k3wp2hUx0DtONK0XfuCI%U8cBSBakDS=#`s8FR!MZ-r}s_;vL?hwB(5$*a}&*GlQm0J*bS&*=bZbS+4&}Hve~`K<oo@9clynlGjr}t8fnWMTd2~X5>@}hX9iV{gU*(#3e}<hk%NPM{Rb-c4c|RRO)=hls86+TTp!syMjcZ3gm(5H=o<+ww?Zoi>O$pKXkcjM;7ISj?L#9w`?YWG-Fu+l@dxhc9qxDX{L0Fza;v(u+`7;DA3xd75W>elPc%9;cDV9Sy4qKBlS!whu3R-<?XrxI6%+~|tGZeESl{ZT$(=>U$A2_e_;7Qp@TnsmN&j)x?)rrG_UT<o|8dp2i16-lT^}BPSnQuFT9Wj8cYn|S;%8!<_Mrz7e(#Rc^{K@3Vw|ysD@`B!$@j%^V=c!Me(%i>K7Qs4(I*~C8m|T~rH^~0`XgPfe;!Htee54oKGrq**uBDsyI%XmoL3^p7XH;0=gj`Mz9+n@fB(EWuVa5775&fb_|*9Ox11DxKK|=x=KJ@4d&-ReyDZy3e(U0!Z<*`+MxO1T2fOL4@a{Z#{&&-C|M{wLR?_e7;Tq#pkB+tdUY(z4=0Ux3MeaYf$oOzhhV*qWoB2`iwu(OX(65b;fBSQ>fB1NnnYY-noKfLVtTsM8<*4WryYrNp&(ztnx5fUs=ZsgyuggA*y3IVtzkd3p7*G4K@zGB#;ngF5HuIl)`KwdH=Uq15x^&q1)C1Ss{`*;7%uo2edq2BAe0NA*FSSv4?|R`?Wx2TSv2XUJ@AG%M<aMk$E4+Ih)sw}x-^aq^(%13v>C&IRA$=XMo)LZ2LocMS<M^Fof0g}v<HHvQlERl&r0@STb4Nx0)|PYWzdI!Q*k2~i^@``Nd0X^(>@(x7zx+h>3I8#YzFs}QJSqH}KQP{UZi4Wt<3n@3;ssf!#r|8brq|b_yUlg9FO7(Kjt=*v=V8u4dA&-Sg!ir&K6d^taX-X=^Zi?X@BI$r!~OS){_eVVz1!dQ*6986et7Yx#z$Xx`kL$7^}%)R`rx|u_7ALU&j;4E=L7578&6<edp@wPT_0T6-u{7g?fJmE_Qn%f*WURC*0tvY>pJ$z2{E7UbHVk&=YqF?;JM)Wz;nU%!RLb4Kk!`e`UIW}v5a4d`yqAtiS+Nu^goFEO7-0(y!RY;{hSZPeVaPnD7<^$dOqWGaa`NFlJ<+gkoWWa3Br5#Gd{KdOS$fjUNHA_{M!qnPxSKN5`ORYaeegli=vPE`oZ+?(z%RLF%JRn%>&+gDQ{HFL;Jf4zxU<=uO`nE`@4Ny@BRMc<B^48Jl^{WKKS0ET9=Rd&nsN=Z2Elnw_NkQTpv8I_>a3qALAq9?fKOWpAMeLQc7=G&fD`qukY1aOZ{={wO^eFYyP`e=VeR(-&f}i&KM%jcAK*;gEzp-$v45v;1D@Pp6+Z*oNc|cwZXOIYTP<_3Aqxt7Oo~Q!mWWT$*Y~M0$;&*nm5v~o4Oue$9G+D8+k3R6JAH|pkF6-Eqp7-?x3!Lb+2}3y9Mqhci~#$jpR;T3*1HSz%|32<eNEmGqnR=O20a4JKV~5HSjIuD*Dw>Tj9m@tD?5R3pw^;YBM~Ce)Fhxa1Gy;z)Q(hxMH}5Jd1wC)GGLTjy;RI7%rsWH0nIKgzpOAIpktoK3qbcO22$+F+7E1Po>U+Z=~N`>NL23?<}~GoR6Cg7m#PtZ#Fd_zJX)Uq)vsG(65#{7q<AW8orS{8&?Ti<e9id@N9Ag$6iF83D<J0Wz?H|JdLdDbRW+n>l*TL9a-1qK5i%L8u4*AS=ZZqyq>J<1|QdwYZ;^F-Oe`TY<uB5$(jeqy50fz!UOP5@;0~^?j!Gjx5547UGNTgkgRzRS=W8=UU&~YMD8I+;oaoh;U0K^ycxb7?j>)6H^bY=Ti{Lb4)Rub3%rZG9o`D>AxGiu@LqD5+ywWKH8+qO7_a7)a09%VyaHYcZz9*jE8s2UMz|i{N?rvw!rRGB@G3Y;o<Y724wL7@GvEfY<^|*hj8}6xyZ~N7E`!VAdU7dT1~-z6;8J)M`8v1=ZX%B-kAr8BHD{Bv8Mo$1a5lVvJQ<z@my`40$#5At2hM{_$(kpSCotYp##e+J#~5`ULssy3vgS;3CgasS5zd4sk#pgR@MLlpoD1iXHIF5aW!x@jkTV#s=1AL^jKa+S^smx?e`0#z;vc8Mzm%_u{=aN+dU-F6k+yOAe4RmLsQr2p^)Ijb7dsU%yZ'

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
