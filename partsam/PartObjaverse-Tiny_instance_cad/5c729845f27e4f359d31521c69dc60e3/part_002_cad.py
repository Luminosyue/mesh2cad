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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c729845f27e4f359d31521c69dc60e3/part_002.stl', 'relative_path': '5c729845f27e4f359d31521c69dc60e3/part_002.stl', 'source_sha256': '97c751241d39e33e6dd54481150286eaf86d10bfd919d529d9d1b86359a8fb93', 'input_faces': 254, 'input_vertices': 177, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0693003460764885, 0.23155896365642548, 0.07945962250232697], [0.08812754601240158, 0.49994876980781555, 0.23805828392505646]]}
GEOMETRY_BASE85 = 'c$}q~2~bp57KR_7sNlGwpdx8k(720&0;b&wTM$JQL>dJIQC1<cXxe?lEh@NRXaxx%8jXUukv5`e#3eCC6UW#wWhygC)X~w@q-JFLo%_GeySFn{Q!`z4>;L#UoOj<nuTS6Gga+ERaFW=omsGoI_G*`ok|d9|l9QAjpRpuqethPTl(ZZhsRQ})OVJ%6;lZJ^ZKP}|&pj?abAE>VSdF`Hg17r1jeA0B#*&QKl$g|vxOmy061ylf-t1>4#-_!afA$#e<uyn%a=;+XGR^<^axhQ9RCWINTV~Z9IDSJ`-K-TC-ctG6ke|sn#T8ss`}*zOZpvzueyiu=e`+M(G<e}9wXdsbcZ+^sm2j5JQ@M+Llk3yVT%MV?$T!|EsZ;x=<+-1ezI@)u<>_c7Upnw(Ef-&v{{`LO50O{YzEo=<Uzc)~yI*6`CGz!CGr2sP;VW;G7PxVFj29cp*LqAmrS=V7(!V4vp2W>l+EY!wbU)xUcfXrQ-l3m8zvI?T3Z6^8cJ8!uT>hLI@--Ws8@P4o(L}zkUuz>b&-A~r_z|5yrM!LGeN6FnU0B^qb1$fUUH1s`H6gVZ)xNfF9r?znP4#MD<1v}lJ@UdOwQp!s%AS)EWoJ0wF`nwHS)SC$&8P4X`TFp^r?~h#bE&?Do2##=eWUAP^0i~?Yq&h2IjrtCUvcr$^DE?QvwgUDW4|J*qi%5x7q2aRM81^uMlF}8x|r2BrjeV!<n@4jz4OdEF8}#7T7N^@gv;DKkCw3d#+0As{Djx6UPFT$xVqGI{fgq3p8JHGXMz{`h9A07eT^+fvbr3pqxqX6&anE%jArozYMEbE$DaRQ&sqM{rPt~2inBOh%KDLfQ|^}+)xKu2D|;UN#?`BR?ViW1Z^SlV;_?p-pyxqq<#a~v>!tCm4@7+0$mKb=hV=oj`?cJ4w**q%HQk?G;o|L!Ss!?6I;r-JP1)@Iek1WJ=Vx7G&%?VBT)ft|oIMYn`f~BwldstO{h@yi=dV3Sb=N%U&&@}lEKwb$xUy5+bqDTe&%@X2FZ1)c$)1N-{m*i~qbJo@lbqGStwZY&_B^=hKjG??kVd}g7dLtywD~Vt{M~7PCM}3z^%?e07C-)%`*gql$>eJ{HFLh<U<&i?LQk-I&tUW4bd~Pc7(JbQ-Gb??k3DW;e#IK{^&4F7(eE$%H&I@@4dk0Xb|&A@Gl+bBbOHH>uo|}h|Ej&9_H}O2>^Xn&g6d*CwUvBHI>kNDim$|*f`6rWDda4RkIndo*5TD}^jzyJ>RJ58bn<nfubCe_m^~LBo)0KqdyDmlJ0aw28(%%7c$-I`vHJ`sUmyR3eAA@%*VMkr=P8T#bKrb^*lXrrI?d(L3}|L~I-DS1vR%xs8$A45`u(xZSJl40rZ>eK>L*aVW=<vfM(;4T4%@5f{j2}}Gx7~n53u<0xs9x@H&~v%CG5IS@>qY{{W<x%ZAEll!}8`PwXa#Qn|#wfTefa~t=Rh`{UwVZHJbW>vB-gZ<B3Ig>Gw^`8aTh<1&e>=Me+Kejx5i}S#15!d~yAce4W!*tUo>SC13N=7&adVXS!dlpO$?6J#Uu3lPl|Ef15(S_O1)PFAT?*vd_Js0QUKCv>W-lh%EMgX&*(tRiA`!)hFRw^-1_veNxFU_DT3weNxFI_DSWsVxLsv#Xbq&s!uAu*e8`dVxLreu}><#*e8|y68ofbU9nGE<|Fh;#TWaevJPUORO%)4Nt0VVo9Ddnuj#rIe`5QYA*n3?o^kZt8Y^DXeoVVQgY&g@&1|3Mo5Sww`%pH2?`w3w+M;|Gzb%aI)4pvaU*CQwi+^~S_2GwA?ERQ@i+qDk67@-K@?X!>d>U@E`M;S+zA^Xj<QtcM!}9Nqr2EntUb6mh`vJSJ^eDDIQ=YT_`D`FPFWR4TsPAcmUeNQY2^_-t%0A!N?8*G0UHE<;=}o?|WmobwNt0PWKj}lhxX)C4ai6L9;yzRH#eJsYi~CHAFYGfd^AYx$mUv;GsrceP(~?KnXDYt9&$Q$b_L-LZ7515yJi<QH;tTssOMYRWX_=?6&$Rf$KGRYcVV`N4r?Ah|e>a=e<=hRnuQ)t~^+TU%ww{l#v;NsKfYtrke0E*?RPOWF7_flzP5XXjeRS<smR~%d!nZn~!nZn~D)Hj^6u#B@RLLWrPnA64`4qm@`Bcdxo==r{@q7y3>U;{{>U^rKk9a;+;>GhRe5>=Ra$WI!s@$)5K2_qy^Qn?wJfAA-Af8W^d8*H+q1?ABp3n3*65C3WJlaT3QbMfiD;3$4UyA<mS1L)K|J7G2BSv}tzh9})TA0UpXaIOTI1oAs90;BaoeG`|ej7Rg{5E(ZbO3lFc%XT#GLJm-*ar;)?*qp|!@#lNIpz@ooem8HPY2J$kU0t(1dam7K=Z&c;63KC0-6oY1LtAh*%&gvXC67w<<M2&<=~ajec+Ygz0g?jUa$^22do1}tL{G<L*`lL5dwV&8UcO>91NWf4hDxpXM#h)(=cQXhem<J!Ly+;;Mw50&^_R};N7bA-Hjo$-aPW5%b+X3%fOM)Y;ZQ#Iub+XTva`Cp;N%QV1MYlV1MvZXg)X}*ItSt^9*PtI1+hhK>fjm=CRW}mSD)70ev5w0ZxN%1E+ygpj*Hx;6=~^@FMU+=tl5Da3XX)I1!uxT?<YC$3a(v<G}NvYryls^P%g&^TF}Z4d8h20_Z020&o&^GdKyH4BZM&1}}zg2QLPvLU({u!RgRl;B;`Nd1OJ0pu50@(2p==J_g+dJ_bGt-2pxdu7++0SA(mdTftS}3g~8V1^5tj6ZjCg6uJRi3O)c`2R;BUfvy3UfcHaJgZG1rp=-g#;18hd!5@GP(2ZaN_#m_Zd=Oj)-2yHHe+b<M{t#RVeIHy2J`CLnJ`6qrEd&>$mPasTE{7fiA4C1hq1E7O)Tta=0j@wj%Auv;QmlJ9v;<s&^(}`MgNw0_<xm6Ifb}YemVwK#F6Gcla3$_v<~JmHdm>4rFl6?E_5pi=$3Xjm$AEpH?qDCVAJhZv2ObCQ4;}~hh4uyeg2zI8gU5osp&GC^cr?@vJR0l?bp?BZM?kxSM}UVxUBJV@L(F3kv@6sF+{HYc&EriBnFm9=fd_+!LVJLRf`^;ONN7)J4{$Hk>`xdnJ3@Pc9l@=kJ;1HO_Rwx%dvFV=Gq?rV7TN`D3znc=rQcsN+dy5wHefqwcd#9}CDaw%65I;v25tpz1J!`rfZIZQgWH1JLHmN+fjdC^gFApbK|R2oz)nziuoJj5v>&)LxFfU=xFfhdv=_J+YS|t`W(TMv*b((}fZBuYQ6~qeE!Y<IaDdu?ZLsb#hX&f%I@$fFfBpXc(#wCu{UccXOa6GH{>z!>T$aO5XkbfuzUIl<(g*B6<fl{mH#!}MLI'

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
