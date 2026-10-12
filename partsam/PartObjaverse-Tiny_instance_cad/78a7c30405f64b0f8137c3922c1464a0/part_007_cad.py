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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_007.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_007.stl', 'source_sha256': '40763a61de3acd3309a6d1a29b70139864c65a23aa6c20c3e6c44313e48ffd2e', 'input_faces': 160, 'input_vertices': 117, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22760751843452454, -0.4999997615814209, 0.08192374557256699], [0.2046087384223938, 0.5, 0.27581191062927246]]}
GEOMETRY_BASE85 = 'c$}q}drTBZ9LI-;C<yZK03RR+s3#Q>6nquDMXiDeo~`%-bq_fNiXaCf2CIvSZPLWlq)pSLNpt_G{llcSt*_YXYNgoLcdfQG)k|&FVAIsbSkoBn&dhht-Qk)v?Iyo`Kl|l-vokxhyAxbxVc|Byk92aadR=ela6)KB6C3I9c-tE`c-nHBH*X6eam=TO&^Ie8%U!EONC)Y1)Oy-BcpY=>j>5WGj%>T5uEpE#bvLhX@z#2%ztG*(<}v)XdiQ3JaXu+8Z)UcAdRDgm75jfYqKqymb2BcSqJ4S#^cGd$$<|9wlkXqkKDoR9irH81C;Y%v$_w9r$C@X%AALtvk@CWq^IBiu^<a77>r!5+8rjSI&!qO@`{e#qZtV${*Ozl&llxQg<LANh3Vb=QJJWP_T`8}@AJqQ*q(e;Q{=--0{;U42>|D;nm-AZvqOa(={;AX-_;$JdZRr<-<%Lh={Mmua^xP-s;mdjL>tC-1%L{){{+mCp(Q{4C!}tG!e9_P6+5NxX`>iD}`692)$zeX}d;L1QZ^+AjARlv+%^!I({uaA$A}{$m@_H;e#h<Sp<`d*)U*xrr+7rw-E@{rozQ`*%SN5@-r~FISPcdG}7xPQ<y7#m8wzOU_&#&x@`%g-{53=^o9I(u<?2Ekm!IKZ2LDr}2i}mR{{?5njy61{4>p}KK`~J@RCwV(fHEjNW?>)l&lBiSM-&xC^mq$rKeP4g)QP%!l8}pUEUdww%_QiWf_+;&F%X>!ndi8G0dqzE)%=1cx%iK@(wHe$e?aR&mlzq`p_1*&b*7YF!Vm<hKYH;1AMz&tQ*A55uhs7Ra{Xf{qeQhl3r<&TpuN(db+IOhtb_V%q$3FiA{4dt9cFsTG_qqEnuKR8)%kN4#9L)E<<vqsNpYiIX<N2xI^1YCK@x37aNS$BzLA|+s*%$5WTcVh+tmw78|AkNBi+R)%#&F-h-NWY5Th9CWxS0F7H#*pOA3pvhn6G5K&9D2>O78m)w3_p>AIMK}b6@?lnT<Dk6Z4haz1-g$vE4jg*%#wg`uB1F^6d^wUh+krl)jJt&u+JjxAP>w|JU*@?^W3s?@5w%mA7-QKr^qOK|a=xQgRRXp`^>4ALJviZ5-hKutVME=ScR&bEI90In8{%V3+xM)L*r6Uv=&<w<G(a9sRdV?q4q1X>Nyftzy2v|6w0%2kTb$1M9X+Wxlp-&sp<26utsKuute}=J^4i<+~&Mf$z@ti@cvV?pWqa_5<I|9XV&%-}_EmzJsza=e56%-?a2c@&n(gJ$HK8b>)2~e0iU#y_d`PE7Cqn`0_p~;7j``;am1mF3YaH*_ob9hS4QMNTjiAuXCHW?CcMO1T^@Ty&?bKZP{n!{@*S8M57OdMvaGV1XJAv9uLldz6{O)+fkIqK^ws1z$ws`V5+&`6z~`n<x$XV@F;K+^f_=6*an>hrkVq`ffI1+Lyc-dQQm-}ybu}=UI;FLMt~zQg#{?eGf|WmL!-cp!5(NdnCb|y2iyvc1Gj?Ppb6jvjEi!JQDNlS5r%Pug2SOhz~SHs=uj}#NN@xgYngErbT~K)91V>DQ;h{jgGWH)!6U$QOcMxSXPM9pFjYG^6P%8soCX~SP6MYxQ@~WmfK$O^QItnRM}bF!lc7oAWN;$X2DV{75>b>#LgT=381G1ok&byH)B&z1{Mjpl7J>`$_adkRyxFK)!skB(9EPgJ+)`Zx9s(W;odKpg3p^AYiJFDErCJ6a4vvA=fvI}IG2mEeJ2(~`k8w=ESc<^)&`fYWxEV#c37QUW0yjd_z>VNl&{S|L=6)55avqBE6zFL16!2tdGI%mL3z`T{#5`xAC{KmPgX3`@ref|0=93;R;8LSrFv?}rOGZ^1RRMK@UC2-_F=~NP#qj9wozQt;CpaJaJUAab4LTb<4Llt>2Rt1-7g`K1Mjt3IH|j;Bmcpa`D~B!xFGZ#t<D%oNhOPlugWb?|U^lo1x*l8uR-tRbD!2;Qr2ShBtpZmeLwSW!%h0b%unW2byae}G@O+$?g6BaM@H{ZR$F8!FP+QnP{mbv!p|J&G{s*A^OY647{L3RoTY*i8t855;uNxnRQ1)SYKvyLB8;|iYI{'

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
