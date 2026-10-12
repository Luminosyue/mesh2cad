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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_016.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_016.stl', 'source_sha256': 'aef4f6a7da1d886f3d7fd8206d52ddc1dda1b31f956855f995bd911d8215a87b', 'input_faces': 96, 'input_vertices': 93, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06435893476009369, -0.11245019733905792, 0.12665945291519165], [0.07401140034198761, 0.13888822495937347, 0.35783708095550537]]}
GEOMETRY_BASE85 = 'c$}qI3s6;66g_~X_}2)nRIXwm1}Xwi6p?HG_{tMh)Fd9oL$NY_k09*hO)0=%p#+xIysXjj11g!|FJ2~!DT;yGWZ5%klzyWr+Q+QUS$k*N)J#)%X3tt@y?yuHd!Ky|7jwKv8*f2ZUy(X>Wl@Be5Xw3VZ;@-Y<zzo%wGWy*FW*gcg|4nYaMi>qiRS5UB3C>ekZH9)Vhb3d1&qv!2nf;wvYxQz*fQp(KVi$XDt&y$V|J_5?XxrHS><}b@X#PFG%!eeR{O74dzpf>DSvCNMB`*iQM5!??cgSbqIo)Wp(Tz}YwiAqj};nab(Qe{V%CdlZAqL){_zu_i+O#9E41|d8vZWrP=#7M_nmqf_iaBzaV|W!Nv-vsEz1--4s=8u{m1h4h;zw55BH5qf^KQwh4j|Mslb^v<X;oM263Y*_h6mXsTuh^*XuRtt@%rkPiY2pSNi!^@!aLcPOPH~5l72i1KrqN0$r>)0)J=mD(K==@G9Kb;t5^9V1@2nYN<s%6Z%j-nf*v#xQ6mtavHj`{`=L)qd{{(5B><c%l%3@>MyzIM4djF)HiD#bYrpmUbS}kW<%HQ+o5ZV-+v47OeVxJB9E0J&)S?F@C&z5p2y3fyL=9Qfc3?i<A{GYn*58qp>Ns=LG><s{1wDs`2ppV7Y={@Cs!%z`sTM9_<7|~{;!uo7hxXggUjO{>O*NBbi>O;eKzf<e0D^V9(e)&&Z8R|p}%{5CHgzN0?##e#ZkS>nn^!1n)2K;ndYb4mJ;N7bpLzs8<9r&clX1bIYJJ;3%@<-C$OKL&#gcoT0_tu*T{A!@w;($IpS30qCZCYUaI#<<5JXH@Feolb7M(w3@t{z&9v{9hpQ?7z?ve|Rd{YY)~z;*zuW}f5s`y@w0Yx@kFoltLhPS4bsO@Y6G8ri;$DRA-h#TEG1ti7`#=Hm@tuJ<&enbK*F$0#qd%!P5XWdZ58Y`W@I31J>{;YvsY#>wzU2n`aIASN`f|DlbaB3F0peR4HzVI2ZytbuVp2ZMXMcL`$PMJbwPOzaCzqn1+WBfa2U-m~{5>j=kN)k)<bQ4L9OxUbV*a&VzwCqlR1E3K2T`vjID+CNq|8D;J<^e<<;FtnkEp+a_h0XD-!A0m--3A%F-?=8|FEbE{)^)29EiCi4*ON_^(g!;ChVuYetuv1e|cpK@;|+c{PmfAk@uy$Ft?VbV2a;(F#-CLW0*r%>`u&s$n;N!el>Ix;$L1s^On#z1^voiiuevkG3lR%Sn#|#MO0T(IO#)XT7liuDskVr%k2Mf7UCBl+Jm_$zj~PZUoso|>hEwqIIGerA8ko4)*bF#i+!Gd{6py9{tVstH6Qti+Dhu@*J;lH^K7WgnA(VW7MHFS0=IR>`(&xhp?wK2Ek^zAPSQN|x01fQ7P@Gc_YmTw^``g@Udyp=+pr#(J(}v$wH3JkYQqNf$KIRtXC8uX44Ykn-;;OKzC0aU0=;Vu=FPF@4LTpL_ge+O?e}h^IrN9WQC~oMwG(rwt-V6$M(cafjg4OGpda~){EvH<!9Q^U&NqES4*F@BtIBEay)mDnuA2IM^6+Z-^<26GbDDJMBlt%jgD#3}c#kZPRv(03nf5Al*9$aP3*G2ES$6`u@lwj$c%Md`-48wd`?sJEET~4k<#pH>W7`935vTo>4D7G(5ZYhi{toWz7F31zAZAoO)*128U7NzT;XQCJIt2et>!BOh_hKHLTj%1rM$YH7Pd}c)bG0#tk7C_&X)`crH_mUp-zW9d=O3_7#(ZD=eb$R7pk96AE0|;B$~w%6!>_3U&sp!H=XLR*zr%~m5MKoP;k|W^EnK8@t#TdCA3ggrbfc*Nd0ASf)km9e`|8r|Wj?}FQfXfDt1BzxmQODHAjD1l`%kXyuz&Z-W%}QrTy13zcL<dznc^MU6z|OF$-Fc3E^LaoVf0|$hPfM~J9Bp~UGYKEf}{;#3}7B7EkfE@HpL_Pcjb2<o8ki*Bbi6Czv6!E7sxn}c_8!Qj1kO-Gatto$J|$%zqCGViuY$6!Ms27aK`b>6~-{{Ank5xcd{won=zDmJ85@GYtN>555{2TJ(v$+e1N&aSmp`ROwuN>DLzzMCuu#Ubz@V!7voUoL)l;PD51t#&b~BnMjyt$%zc>O!=`vYHpO+uDCUzGlNh6z`*W`Y8U2_~lV+BdDs8l&nd{E_ME-4zv}9?c*pgW{Gf!nx{6RLwXR;|ig>ek?Da_S79>N&LIEHx`^TCXxm=9)tKcktsnR8ZrBx54uMCOUiQy8Z)Phmcp^H+J#V4Tie;Z){o2I6@y6%J!=V&04KUgo`+|1leicV$!Dn@w?zaTs%rc@$$j^C;#?Y>H1}Oki$~cXRjl_@{qa|GW%!Xx#P>>|gJ^{n)+r&Rn^?c?g^1J=J+84<mOmU#Ra1wfY@x`aDt'

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
