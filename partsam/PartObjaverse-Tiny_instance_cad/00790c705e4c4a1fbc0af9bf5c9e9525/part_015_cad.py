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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_015.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_015.stl', 'source_sha256': '8410a78416331eb90681f8a261d415a075314e70f9fca72011c5e381788b3d2c', 'input_faces': 120, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15796016156673431, -0.20819245278835297, 0.1553688645362854], [-0.14973720908164978, -0.19884127378463745, 0.16156554222106934]]}
GEOMETRY_BASE85 = 'c$}q}2}~4c9L0x4!2`tu#j5CtSZ)PWL_k>;tO%??m4b>4$|{H)g4%jOwkUYj8tPTAx*kzeYmL#^R<urq)@rTQ#9M>ot*G_B5^K8qy=TibZPK($Ht)yFpZER0V~&s*=h(na!l#R5c=pIiYHCB<*F|!ZrkRVT<cu>Hch4`J?jW@gzW7j=m_{Tdra4H{q?z7X=HhWh-r=%$<oGb}0NHzdLD7_=%>0akqAauBADlU<*lhEQvoj0Lw%>h%gF^!3p1uKciTocwO>8Y_jl*gV*wi@2{fJ$qiM?y0?Aou7@RdON;i1A;*7Xv;)!-+5W7j0%s~^EPE^8osOY@Gxm)+oNyWp$I9?0L_Q}}Y3FLH(>NBP_ze#WE2!Y^o~^R>E%!na;_Le4^8^b-<^aZgXexW|2juVzOee=L0Kh0emalxiZ!GUr9L$WMW<?!5%R?wRndE!;7$Z3)P~QZ90g2iu~b74gEi-kgJVnB5Bb!+sGta`iotqgJ#;&cI{BmrQqsFO{@_Kj3H7->DP6CC?Q(@ki0m(%YzyX^8p`2T;HBrtppT9MS)g{lZtuZ(v@F4alk3CwwjUI_mu$u)n4%;j3BK(C7Zw)uO*2Mq|Ie`c%wI%Z9IdjuF1nd==Ky^rE_czU1bE_1X5kx_-Vk#T)yz^;vcO`C9zLg>UH!|IK`jJNxQ<&2>9+e!439)LuW;`Eq4DtiL~e)w&Jyy5x?2mOat=78yCJ$3x85dmVg}3v%2Zpnk?$tmlrV$f>)J{vB~n)RhVFGvKR9wa7`KfANkkUp<O-R$Sq$uRg)Lr8;7LBI|VH8cR@bJ#`!F)43A)XAHP5e!V7q`QSXPL;P=|UcP=+m#>V#IgwVtH>wrLdG!i@DeKE{eW^<n<X2yT-=5dqBKY!3_|m>yaUQhj%{ULyS9E<EhhbdH?8~T6$;16*_ZF=4yi3SmZNWMezr_A})nZ;VOVQ^@`YyG)`D)W}y%^_QgwJ_t+u=(|7tqh{8R)0YbL6x=uOGJp*Qs{n9O`F&fOQB&y|U^o){XsWH&Jgbgs*wMkNl}mG2b0$bmJ<0AD|y+`sb!#USFeLxpEro^LQ$9oStAGH=ow!YiW;=A9GsQr?MXTmeN!3*B4`6W09i_Jf#~~`Vl$O>J!4Z7UKRahfc=6mmfzzsl1<?;H#B2s1KTseZT(&uG1X{v7XK|vA^BFL{4NC_GLbwBYR5V@BRk)d*NG-!8ab-4FBaEUB23T6V~5(F78XawqsoS7Cw)($G8t$I&MHt$zOa|D{`L0w_Jv=by$e{+K-VRh4ZP^Ex>&Fe9@j(;5tp1hjCxQmsZh#ITtzZmB`QHIj<_m{ZQ?PoNlOB&ljN|K3`N1_IVP%RJ9!S%3AbuxB%mRYr=gvVm8(-3BI-6O7wGV4f0P+g8%(6)Q6X$&(&iv?&LMt_fD0l-<Ynu&#N1;FVd}%=>O(tnAf4j*vBaP(=+g#^_+!%UZ)_ZT0wr<4CJpeq5oU!;0Iy8QcS$={vaEtV!kJb;`~qCfO&bc|2;$C-_FOpS{LKKloW%0CKtj#Ux<E!qIBm|-HG=B%jN!9pXD3Te+kE38iD$=v*5qTLI3gaHJ8ok=XeqN@e9Mam8DppfC(6PYpAY&*((?0W`yd_v$V~O_3YFW_2)O?y~2<U|40bd$8kRU9E)+k3&whKU!;~<$S(@kokJ}r6a5>4FfX1HwFdWdqqzri?k>Q(#b%&>P<LFvG3$|UMZNWQAaeRGLH>($_~ilUKYca&8~|Tk?uUMomtouwN7h6o>fW9grR8psooqwdzKv~f&*L-ey*k@X`{#}R{i}0MuYdRI91`?@U!C)9Jrvl!dDL8T9(e+F9C-pclRAc+NlvGxk<-bk)Zye*ax!%oIhmY59ZF6h$5La+vE*p#0CF_hNDUwx$^O)?WPh?JwFB9c+@AUtxjnfZwG+7=*@N1J>_L{P-ej5Fjp|44M)siwlYPiR)KGE|xfeB@+>0DW?N1IPM^K~45#&f}KXN3wFSQT3FS$3hC%HE{gxZ}PLiVM;P4*>wQ9F~p$Q`L|$Q{XU)RttswjjHaTT@-ht;wzUwR3Z7Q*v{16RI=03E7G2NOmGOpi1NhWCyB&>_BcvZA5NJZcKF{Hzqfux|5rc+fsXw+mZvRgUEs8fz)@%1IdG_Ch}l%9Q9pt965>l9yy6Tf;yT!f;^I6J1f+&WV?<hE95NdBytuxo0?C~CQqd1ktdRKs1wLJWHU9BY$j(=)5#g+QPfoOC~^ulnVdpSq$ZFP$??=!ay)qmHJY3l=U{Mi{HK4-{Q0qn16KbZHGlm}{bQ;AU-q|U{qc}WjB6+!O$OV~WSg$EUs2NUrr%oF'

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
