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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_001.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_001.stl', 'source_sha256': '79726e940f6525119367965bfa0a108bd20d21d7cdc08a325a8f3169a12e5b3c', 'input_faces': 110, 'input_vertices': 97, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[0.19444438815116882, -0.48611095547676086, -0.2916664183139801], [0.36111611127853394, -0.2139057219028473, 0.2916664481163025]]}
GEOMETRY_BASE85 = 'c$}q|T}&KR6vr>n)`CDOf)rR`3eu%5B1kI>R(2I^EwpsCqNPB0S6FP5mX8IS7-KRI+81q_)IL-nntd^8*BATHs4*!^ngY>kZB2_GRoBp``t^W`FD82K%>Rsc?yiZ^NlyO%``bJBo;i1B?rg9pXGMvykM&}3?$XxNxkAXu7bW6oG&X%`I6BohHt|xHD6+UbSl{gJ+a2uB5=X_$-jV3kaLn6oc(;xEybXqTbUZd4i;RWFV<S<?w?__7MTt)xj7&tSUEkK)V6<#(FkUhK>ybw(B#$pG_@&-Sd_6-NKbN>ZlYxgf%wJQv01puNXW&U1N9E>giJOv}BYm!Mm>WM#ey;M=t2P(J{TX<i#!-3lf}OY7+V<H@2A*t+T~T=eJV4x^iPJbLk6-s(wa%aZbKW)nHJc0KYX9&aI}cHNdqM3V?gg*8z2K@_PyMGBzcn}O%Cp<%fp6w!UH!WvpJeRc3C{h`B|f$^_rNWyK9|a8XA~YdZLgPEIq%}(?%%)6)L&E_TeQ||p#P$apEzN!%Uh>DaPcLdy^hb%pO=~fH`=d$Yu#5E$Ke>q^ew+*otFTg^n7pC0pmFQ^5yTW^D(c^MVot^0Ol1(zBr|Fu8;UF@uJGZs1F?nI}~oBK6-zyk2q|PpL%cdimT2gBB^pC()*QFuOIJRRC&16YmJ{ea^oXwyz@4X|Ln7_%j7zMCp#ML>l$<S7t5=x>q=pK<~*<1bo`{sP0TB5m(Hj>bs=J1m-)-PXI=S>dKT4nF~9?7mhF6gwfh@-o*19Gfjl`MGt_s($_Lk*#Q4m4{J7uuekN{WUgplcb@seYf2>Oq>!NcpG4Y1Vow_x+^AzC5Pj;P|^Ew8wE;`rq;W~%4>tfFJl+TqlFP;lAjQfE(?*H)HcrG+<w&S?~=jSnn=aISdT>OFi96S!5#QTA{Q%}54nDhHY@6TKxpP!?+mXGs%jpO-cj`xP4UoW`Ou9x3Sd|w$_9mIq^zM)+g9YOgXNFMVnTJ_QQO^rMICV1Musc~oD1W(&HHSX-2;A#7&#+`kW^VIiEjXV1$c-p?HbKW<>)AmgsU*9*u)Ami~`o76^)AvozN8dNOzrJsBe|6ssy1wdO-}^%F>`EbI<kDB&Xhiv>lTaS4nLp_cZTVN9bj{68|MQzJZv*8}Mo|a77k-m09mQs7Eqoirc8W)!Pr`dCJQR)4D)?54Cnz3<?t*Woc$DHHXa{^9a=0H_3cndSG(aoieR7GAR~K?>!`w252cgyQ?G!tZ*AC>=iaF$58=)oeEfjv_>qoB5m|N!X0JI!_D@7;r>O@XH%q??hf*SDKD0U*Roye&jbITm+p%w5w$YTq%1-=yZ>V$SFz6|X$)Q9~#wAW!B*_Wd&wOjF(XjdXv_O)o&B7gQZXxE_5?AN0$b(i7|w52|#_-eGPasBM8(5^x)*n80SV7=JihqlxX#aEy$HK6zsw52`{FCW`1il?Ey@J~_frdR<L@OM$<P&@+-!tbTnL$L~)4L?K?qBsBz!`}m63=P4r#cxH>V)(T<uLwE>Ur4c9$iJJm=ECR0_d}nB?}s0N_Q4Op7eZIV7f{ImiEE&D!w*vIqu3994t@>#3_|z8??;~kXdZkq=HY9}hcAL3g7(7?!H1v&@FDnOXrWTi0@Shq`AHw_$;vLt`KQ0`e;=m2DO`W#^)ubugL>voYC4-muxF*bALz!&7L%kO%1p#x3Om12'

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
