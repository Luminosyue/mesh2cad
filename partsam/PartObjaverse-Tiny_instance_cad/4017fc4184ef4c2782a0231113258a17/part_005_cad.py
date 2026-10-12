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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4017fc4184ef4c2782a0231113258a17/part_005.stl', 'relative_path': '4017fc4184ef4c2782a0231113258a17/part_005.stl', 'source_sha256': 'd5a1fbb58840ff67908c1d2f8a237fc217a78b9451c4f82c530c3a96a8e6f8ac', 'input_faces': 108, 'input_vertices': 110, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06601141393184662, -0.01841360330581665, -0.23090672492980957], [0.09316650778055191, 0.03181642293930054, -0.014281757175922394]]}
GEOMETRY_BASE85 = 'c$}q}2~bs47{?E?2nq>exnyuL6%900N?g*bm?5Y=a|sdTAv}^LWQ%OGD`;v(I%J3_`VtM7hnk2~YTgnM(w3>lX>poo&5$-_R+dc8Nbh{#-+ITXnWpZ{ng8$p`QCTG^PO{-!II$V)kp9VCN72<S3l|@gdF~&k0`Mf7H6f~ibm$;Kj9$)$(P3seR=l$S(b$!qC`9uo?$CWFAN{Ag-^_k36IpmGnW+>7pCQ<E-TEiNq>4;ZjsI97cEW8x4F)TjT#jdsf`&PsXe3p$3s?OhISl0A!|9es&cYRj4M7Zbnf`(0BPj)jpPTsMZS4Y8T(#eR?zt?jx$oV6(#I9H>@PR-qj}6TJqI?I$s{VN~%8Or*^4^cPRVkv^8{Y9derTr94(o{zrYc$?KX|?|z&9zNCo#=(W|-7apNhk8@`s`}6!bKI!ngbnXd1ZYcRiS%OLDX$4BWk=Sxnp4%((;lE6MFs)znd~M6vkIJs0_}4F<B>!Zdl3)A6c!%;dEoR?xWgY3@1nQ47J(zv{!b>t<w`I5Te99c8_K<R#=g;NuQ+)B`>~EM-O#Z9fH{tchKGMYGC#jBe+&AmE@$5(Ctsp&g@ifPeWj|*98mj-Xt8`sw=dr!y3!T<WuQ)<=8p{vDub)MARt3;?^^Q^OpD8UPO?rvyw0{_a_-#?7Q!Z1y^F;d|Iv+N!g8Hc)r|a4em9p>LW01e1<rLNbWGef5MKWo^P^w=K8qNOBJYKKR@2LNJYR7K!19#H8=-=N#>!t0o?{<&3dh)vHp73L0$rp(uX<up0TiHK6hkSeKOxh><uBX{IN|#gou^QgbDa+aK_YChhuR7Xq#`M1IPpsHXby_CTeD$WD>|fqf&izcI`RX4u)sdg?UqJbfbKmro&ezC4IO!4cI|p+gK8|C5<N4<(k8=doV{U5O$^Hvek28?xYdGFuzirzp%5&-(#T()2wd4;RR7!b5&+`3vTXL=Yy!5VA?n7nT4)T4gxo_p1Uv!qds$94E6N<O4|GkF%;uiKJ5Fd1f{fw`99ZMUzZ$XxgeBX6({)m+vpFD&8xPjZL&xiQFcGf4Y=6$t*e6f%7m~X|iA2W`8eG#tv_$wBkR}uNfT;vbAi~Sc@lCOP<=SJJ;m6SL4D93-o`Sqhy+3$34J!R-~`hB#&h4nM8=V|2cKaG9MujJc3IgdEsv4#8&4?E?5t%~j+qu&MgH9zuo2lA)>pvH?ldd`}am)Kt%NWR(a2=}x0k`ga!-`hof%R9NlJzk%k{3hiIY*u_@`}2qSKE265U%=1z>=yO|hmx;FVqX5O>{s>Wdgk$cB=)zed9Jnc^ET&{;+y+_IzoOxo8r5!aESKRft&o=t<*O&vz`63A)No*v(z`!_dTT^y$9d#Mqp)~d%Sr$jPl#FHnBf@1pA+I|IMCNb?);O*Z6&8ZLd=D82gi`pL)(_#TQ~7^-~Y1u5+(P)bcvoo2!+0YclUcBXf&--PQd5vifdS>tDq0FJrIj>-E1-Kh21x4kb@q4qeyineA|&uQBr!<q_?wZ+7vzh@2cX&m3MC-8WB(7xlca#9r0cuk*e#Giwei@#VkSsh;3%?5~aHdb+ru)(q7bbGV<@#+%}&Eu(o^eYPw4jc-rW{ud3~m3Y&^eRF!+6<@#3eG~Il-*|8k&DU(OtNFdFX&-7C-5YqlV>!<b?vK_8zjXq~chvCv(#N+!$-nM*>Vq=_{*C^;Gnu~&miVc8ymNUS8&qHHZln1cUOkljqB6dU@*mD`bg$D`cZTB4;DSaak299ytqp~0eEe0a)Bf(~P2^9CXaC1v>?bVB*YJR#=B5qat}htZ@N<0)XQsJ*3QJQSH}vm6g|njn-KTI=%>Vrqe$-V%uH5FXkqOO$=7O`pHfT0j>Qb-`oP;5HF*F0b7`z1f2zUuN1)2_)ng&h*&%==XFf<wbFnA%<3SJ0a09^!L08WIaf~C#}CxT}|9|Aw<8dF^30l5{R<DpZ)<G~X#Bu|INgQd;}PY3JJxnLc9KXexOe(+@IL*U8aY0#PAY2X>qIp7)KSZD$`790n)fTd0a$AKq6?*mT&$3Vw{W58pf_kzcQqoMbJqrqdKqrqdqQP5G~DDX(=-C(Ja;E~`F7?LBP!@yECa0EEiHF`jOpc>c*><0}2`+)<XgTMh`U+6%vFW4V?2iPCn9eO8NYEN)?@Qp*V2ZrQc(EeblgTcMPeJ~^sfQEwyfWx4}!BX!6OC16Z1K)-rxgT^WSnBQIe&8TzZ?GrS3)&m(1@?vpgT2AGKyL+0?F*I~2$tFnY)SCw*2nXo{<ZPfVaTQ`|LC~+m+EW4{g=167U9pAf+fLQ?j2VF-9&*)KbO^rKLAm@t(g'

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
