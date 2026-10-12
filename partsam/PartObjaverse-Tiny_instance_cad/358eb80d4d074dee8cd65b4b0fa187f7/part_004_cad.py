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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_004.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_004.stl', 'source_sha256': 'cbf30d1113ddca84be2279437b0495f045994b905f74d42fe4660d28c73524a2', 'input_faces': 144, 'input_vertices': 124, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18954341113567352, -0.06453302502632141, 0.12518997490406036], [0.1933707445859909, 0.32983991503715515, 0.2875601649284363]]}
GEOMETRY_BASE85 = 'c$}qJYiv|S6uxbt6ew8AwiH|GZ7ba(rCM6Bg-W-rMPw-y5ET%*g+2vJ-IjNNHPWCaCPovUiPjkWA&DZGs7-_m6sf%AAu3>E6HSyKB8dpb#Ne5kZ^pf6*Tm>1U(R>G@66nDr)OsOw$>jvz+<UTmUVD(>_I!xvIG(>kF~Zj*x9<gv7?}^eM5|uBz5u8@%7mYYHAn8SZl3K-iF4G<w5Th+gsLD;?1|cO{;^Q!TPqk)xm~Fp--=0+0jUPM@xNsBVFeePAty1i^k>Ko9+Mj8A2rleyi*|LNQd<bwEVBr@FU1Ot;?q;WZI`x1k^U@}$&HedCDhP*=PYt~;l%$ZNZ}`J&Xf?))t3{LuOQ)}J?zOa1Nb$HcX>OwFTp=Ytoe9$NhIc@ew!pH}%VSHB~#Jt@ar`tdCXWIfHp9hd&mx*j=?bL~vH9!l9Lbzl6^FI@SDpbs8#)Rn*Jd8ykyd41u!Z{!}eK0S_mo@Gk64=2faoZG9MX!RSN)vxtXT9dqQ;DynBu6*`fCZ9c*$!E`{bzZ;8XZ2g#ukMrjryZ*9ahVrg`npc3`_gZn57&LOdgZ+KieKIOE~PuU?s=SRN)L^!aOr^|=j8bQtv;9DU#;}+ZSMKIS13K;Q}YLMuJ4Ujzt){4s{YU)$roJuMAS3Wt@HX#KC55ryne0o`nAsM5A8S+jMhI!XZ>Sz)+bu$ePZ%ipO}2s|61q$W9DJ~)4i=AORmF>?=H!8tHr*CZhQKrZeMOvf8V529=Sd{(=W^XI(7aSJuO4(fh=`yIPVwiD37u}M(6trdc^+H`Fwxre7?VQKHp!^BlefhXY1pu`e|=@l>XE@?@yz%{?t0}Pm|C3Q|r7xwa)uf>%2d^?^yd}{c}oB%Dh*GT?p5m{Ytm;Q(gJKU;LlT`@GBapJz!u^pcv#8g+GFwDmDMKYyS{oIhIU=MVIV^9Opw`2#)T{DIEb$Cr0P_Mh)&x!PAX>bZ<QuR`kf?o?O4Q<<Rl+g+CbrqZo9RDS5KA3uyXztP$JTIchdd^Uez`nQMWbzV!C+^?Ctjz!b0OPhPc_0Wz=8F{|eor@~JyYTLjsQm*yqJN-A^pDng|9n0FXtesduItx2ub=C>{y^FuH4i&~jLyy<qqB2H>-?NC`RtrA`RshwIzNBRJpBB*b?&&#`)ac~XC|rhS?gBz7OD4tg7f+8o!)5AYjpO!TIc7j$!F_e^4U6=e6|i+=g({M`S;OvkL)M@dsXZF_p0yr1FA1yJtODo|6Z+w)}0$?)$h(y{7$ZO`l8LRb=Um0uD6TpyDw$?29ZS=Om7!W^<l3TLKGhzqrY0T7XQ0fi{k(NYT>6E<`8N`O$705vk?8@_Y-p9=fD#@gOCnC9iHI#5i;Rt!pp!t#Jwt@i##vlSa2_R6=DT=1;z?K4K-vV=748|XCd0)j}Xc*t_)+Q;o0<a*WeyLpd##9GEhqfw6Ta4;NtnxaL+W{SMV8F!!pEj@G*pYu?Cso>4>AjM`NyZ<ajY|40tYKHlY&hG6%d0F&8`+`BljAW87@;nS{p?XCV5)mlEm-(-9v7uO>W7Sc3Qrxb~JJE&*Rac!Ka0;*;R>3G)bZ5o^J<w*YZ2_y)pyLM&n&_(Vbx{33W8;Kjj@gD3b(!YaZ;h=t%{OUA>Ghqn@5A^bvkgW#`+wjT3qKMsBzJbj-c_(kvpf0nR<(2Upu-bq*ke+@jrgM<$F9q>9arUiZrydcIjhvfvpn+VSlS`pj91sdUt*Z{s7*X@X{;9_hWcpLKCF{S~213bZp6Ye1lMN9-wC5(bU3ZCHNXib5i0xuO~65%Jp^I*)-upAG#_&>@>!Z5^SaDl<_MN9x6f$L<%Vc=qH5_l5wk})O$egZtf3kVMq#v|r~Pa#Z&KNX(fC4^G=rSPU;Og{X4cqJG!J}jpM`~kwlgb9d~!3D;_7cmcf60RpBP5>8Ui@}SLHyLB{;OD^;d>~-}AqLR`-$d9*SckY4d@*4WVIktv;Pr$6VL9S5aP5h4wf>k`PuxHKYwzz*NEG1uM;{;Q{@M;7xs)a{U*fg?fnv|n;SwvG`HJ`pTYmu-uRYW'

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
