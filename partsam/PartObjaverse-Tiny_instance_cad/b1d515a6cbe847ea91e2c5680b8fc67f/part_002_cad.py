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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_002.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_002.stl', 'source_sha256': 'eb21acd745143496f572f1c6006a7448e4441980f512a698b61b76ded6aeb2a2', 'input_faces': 78, 'input_vertices': 74, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.1569700241088867, 3.924858331680298, -1.5123482942581177], [-1.004469633102417, 6.9865922927856445, 0.11486448347568512]]}
GEOMETRY_BASE85 = 'c$}qI2~bsK6uy9p_(ZmcAfjAldEi43L3ZQ{ZivfsOh?P~qC6DCg+<KLnO8YzO>S6@OO6knv5m;Fau7wX;9!wDMwyh`b!$-)7gR#c{{Q<Ag-y*gb!X0;bH022??3-J=id9CCDW;kQ4-exsl;h>@)BoB;?h$xO2yWKqTIRG!iYsnmODu9!1>joH%**6!7{@^DwbY0Wm^m97MK!cQ*utcDO@(?EG{T2$XYaeaY43~<D;|k3atz;oS(JC%KXr{m~c5dEL>hG|JSPrOTo5$goDPkX5HbTFs)=wzf{At{Zb@wwdXibj@xqze+I6$J>lBs*x<!+=|Ey5_vONSz}57T;E@B5f6IOC)pvmFy-t8fi%z)BeW|4RG1tl!9Xz&B;|Jg!9RgerpY4bEAo(2p+J}#De@g^#sjU1s*85xnuI0UHME<2OG$C$X7;yFIJm9wSuW>Fl#Z~Z3dLOu)<P0A9=B$S}pK+n!pW$>3d7ge2xE8hF9XzqC&meBL1-PCv4d+t2Cfr9p{ZfHTieqn%>&J3VV_);NcHGbR11{~Ztp`uB+AivM-W&W?9y;(d{RMu0AL7;Sd8o7US`Xm1szb<M-<?{GxcD!A1wQaR>Z!Tp|A2VIyTFz2bI})VP3aAsCvz2Wy`@^@Q(18Ye%*W#zw<;N;H^>1Q+YmRp#q<FR-9`@2Ku7aUueVrj>&zI|Hag^$bVf`o8TXhc-z)Z`>_7YEx@&*cTs1hq`U#^ciw$~{M|f7{N~A55&zX?;PU2?g1>kQ`eJ{u0=PP>6m_t_;aUUU?b*Pk=w#9NsPq=_TvSE;sTHEXK}SDCenrm!w}*%LiFsIc9Xw42;9BKU)Kf_rhxwOMPNL6RL$P>XUh)&?`S?BHdiM!F;5RJZh4?8};Hvi;oJ(t2zZ<w=l;F9s9(7g@?%anu4+#P;`{%f!&ZZqdBLBf{_rSlkP4wj_-@QEE7E=dY&0dZ3s+Y}I5SLdg;ty@}Mf~`Wim-3{cHq*dyO5{0Asuy=TIT_my-te0OkIjO(Wl;T1%Le!%%{{X5B1mX*8#WHTg1K_SEBD)YZY**Z9n*xMq3r?+q?|8^5QY{Q6F|3&ygIh0@p7r0B$dNQiuJ*Vg*n9GQl&)74t964;1n7xp*Gsw}y&2D{~S2V-5;_;{w#d{>|gN$kTPB==<oI+fg@<bHJ5VyKpYen0Og+!Jh!vTlb2-TsI#`#XPJBu6m^jymnqS$K{q{!LwS-kJ9wrFIcb66#M?R7X11Ym(P*U%E^L1_;vKfw$K56RIX+UTrEMoTv3YmnB6-~@YHR?JlI;?;7g5hBA*TJ$j26zf%#O{`HFlVwTn5N^ZZ`ad4Z4MAC!jrD4u&T=W67wJBS~32e|ZHHR_;Fzbf!+bHw|t*^~OM1D6k%gWs0qdkXnvPP`-Xbi=unvJIG9Jt#rMuU#nmV(#Az{FP{dH&{g7GGlJyyn8Zki~O6wqdA8nPvv@`z$+WYb96Xg7w@&VZ(;umO`La4CEk15L{H%I(T5^_=4TgcEKhx{YvLx&4ecUHTwK`KIwz~sr<#NO>d=4xsm_i0cc1F`|NW^pupE4tbR*%m2R|Q^bS8tCjKHy2&ZN2DpUEgb_DoX9<~p9qNG8#|hNQWlN?d(u4<EAKnFKNMWYUi`_xsRVe<qQneaQ}H638TsH1~TmF)<0~WcQ|f9dSV<fyB@G_%9|u(!Nv!1KAyW8VFCK8Vn=N{lRo@na&<hwwZ||6aHJMJK0^yk7E)`xy4eh!Boq1;^X#M@_GKlnIw`OLH=;E(?~~=ok2Q^WDH?rh;J;}V+l{C{+TI%Gx^bU&rIS^SR~bK2<b?wQ$Qzd2>CIRxEz@9M<hhzKVgN<u`Xo0G8strP$tP_4<z46SP0q9)L%c+0c3M-CyH^Ry}2DueH+lJf82JF#2k8&=02ZE{tUP=@g~jvUXqv{j`bnwxX<g)XDfkp1obM4>;#e|!hDFYgV%@lHBg;p5`U__CDXyt==4v23I4onyr@t8LHO&+r(aK<S5`2tKVDXr%&vUq+2A@#`8-kV@;gY_v>p'

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
