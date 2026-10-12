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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_004.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_004.stl', 'source_sha256': 'c59bfa0f43072bb63c46f49b32ad0c45cda5e2a8d96154c5ee3362546c235790', 'input_faces': 124, 'input_vertices': 109, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1083025187253952, -0.0745014101266861, -0.4999995529651642], [0.09948226809501648, -0.029201366007328033, -0.4999995529651642]]}
GEOMETRY_BASE85 = 'c$}q}c~Dh#6vuynh-;!zVJbY_@EM>8rikXvHGG0BisHt7zymSdz+9#&ua=QcWy|=775Y*~EkrPsRq~C?sAxKkX<9DNCLwilNzu@h?mfS+`401%Y3e#>z8}B*-ua#1d53%N5O48n;V0x3BrM*qDHUymFruCC6N_xQ3$xR0d0}(sFZB?<<Qvyx{UmNuY<!A`SR`H#&amaB=LQck1rN;}92{Z_&YYLKFxNUabzW|U&G5%qbMkDupEt`o-=_b+Pk8^R5L1LX#Po*gKVC)^j<U+?y}ByzbSgE}^r-2gp=#wy@}0-_mbm(ks%-M@{*}e9zSt8>zWQm09j?B!#!SAJcC^sdx9{~P-_bY!OIKgp_iYvV%i3>o^_BfK<cppsSv{shbI4Z;LfF3c!?Dtz{V}Uktqmn#J^dlyx7IB4?;E(C<vD(;lFrflCfis0Zk_ZKy0LR9r((&shi+#19cOP<kS4X-$?{y9M85s)a=!jj0{PmG**t$;L%Gy;tR8#)S@NArN?HBR`cvdPl6$dz)hoMYo`m;#-+r@_Z(q@u^<TZ7AlHxHzKPX&J%)TO|9e)y>1JrToQsC_EYIyLW%N0purJuYw=a{gmb7PcC>oAPKV<~3|85caqH`*r&wC${uQipjbE%CB$afw{Wc@Kch?VtRsAu&%|1`@y>&I_pbw2D&z7iJ6=d-DCH~oBE9qW(qI8DA*I*6awvy6NZcfWwu(>S4YxKXe9;MXkwAL-;PhgP!lD)$zX??^tx&wDqYeADtaMa*ybjC^Oop0C&(-YJ&*rcc|(`gwb=%pWnAombpGLB8E1V>9!AzbNbMJ!d1U^VSWSXX7e6+xKP@`P$t&)(7=k)-J;rd285t)n7M}ub%0~&gHBx-sP@NXWf4Cm7+PUPPOiY%zu9=>zk<iL9REiX7$@IUnF0vn#=m5T&^d-`F%iKz9!c<e$LLT{PJLzyYrfU4%|(Cz`7E5zUrIC?qepWg?vRT;C;T3N4|5gKl^^gg~hww?Q1{3Os;=mX8m!VTO-#eUuE^HKNXX2pShE-|FN2Uk-3D=&)K80&O2!=k2rI~eLbh!mQg($w(>rloJ_tW_X_XBiB05dYi;bjj^l;W@3?~1<2-hfeABxb{P*|hJ?R(L@cUt{S2^Xe>@0ETi|R+L4_d8{T;Ke@UE5Z!Z}$7H9qA%{dk*i<;Ru;$Kpda*gQ?Qr8o~EHm_>f``>J|iS-HFOiUav_{j9aDKlc4=$XCu^WpkzN+v>J{$2T`*{(DutKQ%rTv_3U}eP50}UC4K=va)m8t0Uz434--atsYe2u70h`LcZ2wIqQQ`HGzE9Zv&sh%4y^)P9OgKs+d>dcFxP+s&IE+XGw=j^0$?-`?IMekbG^)5!MG$+>d;xHJZ=uj^X61@4d<TpcEyMZ@=G~&(HQOxvygzpXb7Pm2SV6!aVYo55hLN^BqMG`F*%>vGmVP-QvzSm8^c!=XmzkJ2s}Z7T;0`BU<Zky_r^*S6;(3uE*;Bl{Y)`-@Wn<i2T2=y#9I(9rf^qwg>xypMtgpKLs}4mA#=Ypl!h|z+TW+U@x#Iv^Cfh>;d%w8`=&mpk1Ktz=n1J8|nw{0`3a!1nvs%27LzH4IBV{8XN!)g!+R6!6t-1ef3g(!M^BM5VQ^WaqohlEx|$H?$Bq!hCT=G4(<Vc9^3=m6WSSUXfJS#9+UKV1sVsA)gw`liF%CIW0W2*>oHxA8G5{mFgORA3eEv%Lsf7#c(xw1pjM~~Hujo;{YHV~p_9S!;3TLOY(<_Vgu%(sRB$pl5jq2$2%ZR?4xWy4PDG4DZ(_kC^oZ2sMLiUR!NYJCqi4er21h}Mfrnwe!Tt3ZqDMby6gUcN`XLMsgGPeGz@g9xa40xLk12XY>oEo~9^MpiijXrfQ^+|mbQ(AgoB*8)P5@h=Dc}_3v_QvzE#R@xXz*C@P-r-KD0rZdbNP~xGaCaQ2^|a`2_B@!3(&sM!Qj4NGjssh4DJIR2<`(8hK7T~QLDkdp=r=)a5VaxhA=oCngUJ-XF#WdGr%_JG_Vbv37rYf1ZN=(HfA^8;^FD%^-q6-d2(rVQ+54=O!H6j$C&FU@9Me!eyGJ;yy;QqssCG`>vH2MBK`t)f3!^'

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
