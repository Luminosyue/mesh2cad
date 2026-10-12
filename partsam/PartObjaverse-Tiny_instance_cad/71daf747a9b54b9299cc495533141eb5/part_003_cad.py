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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/71daf747a9b54b9299cc495533141eb5/part_003.stl', 'relative_path': '71daf747a9b54b9299cc495533141eb5/part_003.stl', 'source_sha256': '984163f8a555f7bd9203312f94dd9faef921289169d50539f90e7bbb5d88d192', 'input_faces': 180, 'input_vertices': 118, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4976252317428589, -0.28925418853759766, -0.03760692477226257], [-0.37317895889282227, -0.2726309299468994, 0.16794627904891968]]}
GEOMETRY_BASE85 = 'c$}q}eN0tl9LEnJf`AH0_=+A81r-$#1>fQ#f+C7&V)BxJyyPq3McrC+-sW1ajj~)hvDu|uv*{nU)N*rqo7u`<+|`=8UcAd(Thns=(d=cd^PKZ}F6TV=w6!|hZ{N@T?%{WT&+mEeZ)en0#SBW*tY@NjJm!AWfkaIck))+*yW71xH@CL;%<SxbB1%g(eep;=SY5larY=g`tv#9D*51?V&7QAkFYGAJ&egL!y1YBREuBqW-nMq(SF~*FX*c|yO)cH+#^;>;{Nh}F_S9T`kNzK@1fvAs$eXt=80!DD<f>5ZX5y(5yMKL#<^Pa(O!%IYXH8$fI@k0)*V4@OfxBl+-<OeP`o8zKnd^Pt*l)$>z~#kOo^$CJ&GlEJzA@LmP-Nw)+y6m{*^@uNHov#3)LI{1Zu-7E38wGM>$LJ8{KMggdKZzW;gVy$%zy5@bG<&^%G39=!}t99d(f=+`KU{7zOQVrGyf;ogKl|3_3s7UzSp<m-Jn~Y+WBXK_I(8=TfTp?&+0?lZig@X5P18Si;nfOZ_0YvpTNBr9qVO(0=@ap^|C)F|8lGk_aUas-GAq<Gr#PQl1KJO{a!!)QR@u(PY2!hCHtoKA@t!c$9ms{6JMF1v-Vm2=}kO(!R9x2bzA;ZdcUimdHJy256M0&c|1e;9X<EfYp#CW@t5s>fc|UxXuqp}`^FKwuTQkjMeG03@9Kx<^x1tM=b{yrzV7Dxb`|uyuYcpPtAA$yOO84@U$vgFuhgSASm&<pH|#6>4cs~#bn9o>SNf^-b5E3W@$Y%s+OKlH($^+A&sY1{%lBG&0&zdxu>bDDzf*j5{z%`yDaAUM)0Z6U!*k|j(AAf7M*4w$-v{0DsPjbn>OAo+yJyv-%oFLW^F;dU+z99C%W=))IhtwpVQ;0YuYGjPS&!_`!5rs$WzIzSed8SKL$W_=p6Y8s*Lv{PdP1u|3%cz~olDYJ=TA6~GJiaWzOdFS^GEvX{E6_HKhjs{OoY$xBJ4L#asA#<lWzGJ>tD6|0qHlNdc{%Co5_}+n(ue@ADlj7_tp6m;XkPNyZQyS?s=F$()X9$3A)u2_LX|{-Y<i0`wjcbegg-tIOa*%SLRZLuk>G?KdLY1PxziF^T+dSy6gRyzIy+|>y`VjP5bV;+kKF}dLN{(-UsQc_aVZk|I$~_J;LYQrLUfEgs<dR&o{zX>UW%PjpJ?p_O%m-?#FAIh#|(?d`FAzRbH6lk?Q^`zq#<=y~-Eo{ohylDx-$YMpUAk;7WKI`Z&A{UW%5(9?@zeO3^g96s|x=!f{3v84-^b!|`wux&Ris2u^~BqYuNw;bgQLPKL*$E8+2Q2D$>yfXAX0a0T^`B?ON`)8J8XI+_Zn!w(rT0!=|v;Z*vVLI@VWy~Su5>VeDPa<mjKhnJ!ia0UBWO03{KSFnG1zJe>!YHi>?2(BUoFGnASm%|IuMess+KDq#2z!}dc1kXc@;Cb*8`mlr^EWs~9<KPlFg+2=%g2ur^-~==tPJk29Bv|NhI1wI-Cc{JFVd!{x7(9*;JO<5x$H1e}v9Qol@M<F-(ZqPMLU0x#I2Ub%YmCs1Sc6W2g-(Unz;%S+jc7hBv=H71w-JIn(7CYCIdBKuP6%#A3*Z9kZABa54QK<}2sg6N214+9bTzylUPlOCO9)<tPJ~y%69~bXgy1QJ;2bmy&Vi?+x$ty&CRzX&u>YBa;5>9LoCnV)1kXYX;X=-479n^BIu)J)Pa_0pqm$rlcrvQPndk&mxAjM-XF_XiJ*=_yS#T}72Cju4B?Q-_b+FKla6SAOA-D-`gN1g$O>hg^4!6L~Xe%u5ncyu(Y_rubcpciQ4csNc>(Op);JyiNK)u?){q*u3LU+O&;AV6e+zhv%J+}IL*q_iHw*Bs)H$uB?z3QTWLbu!cxt-n%-D*3Ft(?zVbPKu_7PB!{vu5WAbTAqV4~7S6))Q?+6dD89R7FLn#r)I1J_jD3SnT*msQQ=A*DU*Aes1InzjW19#SXTLi8h<`o0;Kn;}Fg6'

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
