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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_004.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_004.stl', 'source_sha256': '0861aaa8eb69762c8c5ceaae455deada6c794a6925230134dff6fd1a45b4fb7e', 'input_faces': 230, 'input_vertices': 137, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.15850698947906494, -0.11491450667381287, -0.056722596287727356], [0.16000249981880188, -0.10086435824632645, -0.04267245903611183]]}
GEOMETRY_BASE85 = 'c$}q~SxgmI7{>=tP!>VK9dK~N1vhXn%7~&MqPUBQUQ|$uf`V&l=~ZhrY3&jl(>^r0+7=KnX__>#;&Rj4rmYV)J~T0H(%Yw|X&?H~#oEO5&dl$OGoRC>X>W4#|D9jXJ)C>KnGYsZmdEwW(Ck-^R`dPEyIWE;&3q?o8QPJ$mO~A@>RP8a9XKANrCHv5sXV`WV?||EjCMq8%iUeqx~nC3p`Ke<KR-85&#iB6In+|yw4=FYcb(~%*Y0bri~82RwFl~=<4Lm$=H=-Hlk@cF^#AxuH23gZ+3lie1P3<WxMhw5&6jVveE8LBUmv-*-tvLrFLnF*VAuLCx7VwdS>E_8*zM=Tf7W>Bhc~C&>-Rg?<L5(tYdhWEXo<Icr1n^kpVzn7d*|o%Ubn{8)xCZ`bna}2+XtK9wS4fkC7$^Kys_nyXTI^}G<*KqZ+m@xQ><rx_~InX2e#kv%n#v>ojKn1x4zwHt#dQ+ik}bM`N^}6jyJL%yyxfjDfc~I>&)o$+fSqeFZL5?Pwn&lzW9*%zQ+AGuUTH4r;eBBsh@qt^17&(h7XH+1-_nZd2Oe-9`J^^9wNU?wtP@tZ}_md-t_9<Kk~btHN5svT+fGpw0uz9FClzL+%J)<-&<Z6_nlsJ&*P1(HTL!S-E7Z&s=U5Px9_|0`?~#n;P%ljw-2}fU|nzFU(0&@yng46PPdQDKWE=ZCmwm{D_<1paC_tWXnUQBhkN~e@Z%=$e6CNe_$|+Tb=_+1C7$_#mvijvT&|Co>xWa{zvj395MCGi4}Y=I@)2=9A-o~ZCy<n7`G7co10NLUuQv?1=B{t}uXVotS$WxqrB{7edD&N`SAA7^*(aq}ebVuw?>*t^1CAGcOnKRtl$U+RSx594XC2Wul$U+OIXBS<obwTV!13a~R$kuM&VI!G8(vjo*Z0Fm*FE*c2ReVYd?cZ?+t2G)FLb%R*3oC5^W4EbeqR6JUZ-cBk|ulpA3Z(3{_}j#{9tjiy`P6Ey?#FY=~o?Yuj(5bmhYLb>KnY=>zS{|&+7AAUsGPLA9vUOJtFq6<K_NCmrmI8#rXvBhB%){@@l(34Dg<R7;lL4H_k8i+`qwR8@+w(Zby&X2fIovAO7Zy$46E?uzzmbLXX#Kuh~EM%FS-K4`jY>f3HunZGY;JZ{JW}_6_M(-%wum4e3?iP+s;8=~drwyyzQGc<yV*i@u?}>>J9<zTvDR`i8TP=o`w*zTupk=o`-Yh`!-?(KnQreZ$$0{JsDCGrsjzUe-~0Suf>fT^ujYUwL`X&U|s6%FA<e_9M>6@#1`xm*?Z`$9+DPo~N?hZSQ22CTW`a9vFQptFLuEl9|$csq}v&Ync779?9|xX8zwtvfa@=R7Kx)WHoGNy^CuY*TZ|r9q=A_FIfwlxgh%9MLq@Zf_IV&;hk`RoDT=!?c`i|JG_mY4R3?DlKJpfcndib-U4qTr^B1z4P+j?0bWN=f!D#6<RsY4wJx5_crCo1oC>dpH<Hufjqql22D}-rB4@!>a5Y%~SHm^r9JmJFLC%BcQA@=OT(uob4b7YgKLsx&$HC*MpW-o$$521TqZyB;eu{@Po(<=d8E^*mQ#_dQOn5q(0#AqY$boPkJcaBJPk|?qF>nm^Q{0d7WOyn$0G<j@Ba`82@C-5yPNRN`(;25zKgGis7r=AKQScmi9+?eiQ%l8TU9}xg4b9AjC&J^%3Gg_044DJxP(Q_4j7P)6$&v7IID;GtXTXEWRCq9)LMFi}@IW#FPN05@;~2+LKgAm37`Pu93&&DF#qo>>z{zAHoD8RtgWxncog4zE!^6lC@Gy83nF(i7KgBxZY<Mg=UVB{I3TkNP8aNl8K(2--z&Ye9I0w!mSGww1O0CRX4iAM>$z^aVoJ1DGNpJ#bzzJ|1xfqUvHL_59{3@hYW-fwb;drtLj)xP;C2%4<h+GN}f`^bL@DO+exdI*mXOd-bCaja?unvzWD`2x0ZJfQC$Kh4*O7f_yHY=&mNVt?d3Y&QtE`^tqt?+Vq8F>(11{agfa4~F<`(XoKOg6%c;X<+jE`%46Ps5AgB61&G1TP_*;3e=<@&LRPE+Jds5_ko92wnk~kw@S%xSTu&m%|n0GjIjGhPTPjk}tw$o`u(tt9hH;MxKSuJOj7E$H~+1Y3i-`1;$6=!{jOW6!lholJQCEt@s4vgK#q$gqz|0<n!=;xRGp!8{r1>Ik>VsCN?APpZ+!S_!YDox%(d_@{`^_-`$_Q5M9gpW4^Myzu6n2jU(3jawE;VNc$U84LZv'

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
