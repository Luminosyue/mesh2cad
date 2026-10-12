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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_010.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_010.stl', 'source_sha256': '013a707474bfb6838a5e6bd60c1438c311394e6d1f05d28e496a6d08bcc47e48', 'input_faces': 100, 'input_vertices': 113, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.33609747886657715, -0.3657739460468292, 0.17406396567821503], [-0.33566951751708984, -0.3069620132446289, 0.19496381282806396]]}
GEOMETRY_BASE85 = 'c$}qJe@s<n7(Rd?f(hYGkRp$fTnG>dLQvETfmk=;s$d}s_XZcaW`Mxl8tKmL*V<gI$i=F`-5UMVR;#(yTFzTGaBKb}Dlu$h>yLgcH|AK@nyv4>-*Z0i_jcS`o$cNGyw7>R_q^x3-}CN(&zrE!Wyov2F@L@IR#vKEkgYUa#<AewaHuOdw6SmCxi}*|%F|{0(Wcg2zP32ym@(q+4i0q<x;LBdnw~0mk?HQ~9~>SG^mX<Rb_a>y5jZjw6#P(cU?3>s{Iat0BD1`p$UJWT$18<;m^gXmoN(rB?<{%ii^i$#F}wjjk~co>#2cea7h-wqwbm%VFdmw6;&~mFKR2V*@f-<UChuqc*nEW5SNt97EWD}r88#cEym9g9loM}#_^qB_Q7`NN)I8<HTiw5E`ToKZ$^ZVjzCU{l<a@QxYP_*-we0ikTN)o(Oo{TIiI4UA=l-0D-f!vEcyn?w%6nctq1W;L80EvKtM&Z(Ihmj1)%&cwB>9;Hz0L>cqr6dlXxfQ4U03wqcjRkX=Y=$_&cbh>MR|*#hclnbI)Q*QpLtC`hxL<MoydXX@^^O?M)xhuc;jce|6%VNI)7<{-2Zo9()jS}rsT&?XuNf5ZIm~$51jYZJ+IflnI-c(_G`RZnJIbKu%4f~MxK+8n)H6o$aCV)KB?#1=ZEzfzK|~YmIg;YJn*94|0gS@E+$UteYWEq&eS^ck)|<6-uml(jrYHkET5bEwj&=YnAG2^KFP6u<a&bKH`b5MFO2K`FBHYg_qy?leom}g@_b(1sXsULhtyZe9=(3XO{t@lPQA{TOOE+g+M;9q@TOm8ocgyaesJVHH@<i7bNU+Qfd2b>lIA7P&uxR$yML}(&(Ho&)@SF<YP%}+&dz6K?6Tz9c~(5rg(pGsCeuaa^hL)$BWI^2&-Cc2`9|uU>-X;S`aF4W#BmPTJf8!KXLG>j`5dr$J_k5&&jD4R%>kR|b3o;@IiUJsb3o;@IiT{{9N@e?2UP!T4yZoa9N@gIQ`HaCug!D)a^BXj&2#;#-<RoEJ(uZM)o1!ub(ntDJ}~{NePjAn`Aom6KGU!2lj&FGGySUiOus6h=~v}5{i=On`uzvb&NJ7q%4hmjJkzhL!}P26Ay&UW?W=mUVd>@4M8hCkA-<}60x_S|MABt@=TGWT#lQQcE-n4PpVX`9RfMI(uLe#B&VauMI0M)PzZRJM8sK<g%Y?<jCjiF*8}Q4G+ZW*^gZ>PWJ_UX`@O`LH&&d>)E$m(x;T+tjye#+};2h*+p|=&n5@Cds;qL-Y22O=f117%;xJp<+m>;+rG5M!s@Mgs1yJGMb#FfH2g>?XLLL3yfRah^)2Y3tabpdZhe7~^Ag*^tm4l%7ejJ1U85Yv4xatND<4<qLp_(y^1{u9U{ydE*#4<UzeE#iD(K4E)-Hz3|7?1-=);CjSVuL(5?=OXrD?JoESfN9;cSWCD8aW0<O1e}kU)-_`-;Rg}Zx<0HWyaRE8uqTDJ02d*qb-S^aa2{e>*N?S?8xhmG{a8!*VZ?c;y&JdyF|8ZGTEaUK*J95?z}pa0y@RMp_z}bhfji(UfgcjKM_4PcJ0>m!M|dA%^2IUuDZ~}R+JzkeE=OD<Y@@JJ;9|sW$SDJEN9;G`nXdxwMBFXxkgyu~?Z7^7T)ZpcPXEHVeOWYYw0~&umHL>DUAa%xQbXJ4O{6&_21mScRQRuGG8%sa$8<Wd'

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
