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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_006.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_006.stl', 'source_sha256': '72ed0709bb1bb92db7ee6e1b5927ea25a4374227661d4ea9696ee07a4dd0638b', 'input_faces': 92, 'input_vertices': 88, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.21950876712799072, -0.2461540699005127, 0.04744872450828552], [0.3121674060821533, 0.07719594240188599, 0.34941425919532776]]}
GEOMETRY_BASE85 = 'c$}qI2~bs47{08ss1U0J$P<x=vikr*1fIsGfISPBwB(V1I-`hy3z>SgoR*PscalLgG1m}qK^zbsf`o|Tn&`Mvu2YUfW(7@l&;R`vHZ{}Ko%!ec&Nu)2&VT-M?%|?KGBI_K@C=epJ>A%7u#hAXeI*BJVP<ar>=~JP0ogePMv^V*;(37^#!pPqy=5dVl$NM7GV^BSsz<8Sqq4%)ekyg=yxjcU^z5{Gxfz*4k58YIm#OG^v(j@im9bBFxSvWh)K9fk^<N(=QNxV^Z7~AZ9;_6&-MsK3jXe)RU!PwgP@mHUeYVRP!sJK$1sX#4T%xhs3%YybA%VA7w_K+2y<+HfuKVhRzjV2Y##2k7Pq8c$sC~Q!K38g>SNGd0P|kM2yf=HGcg60Zddfz@-{1T!Va^lOf9CD4X`JW}{ebrYs%O_C__xGCzm&8MbsNE7zY4mPv6nE*3;ro3&@CD_2~^!HL;kUL=+TYaY2G~#F3@;_O*>)gihWf7eQWrfS3_4BeMWtoxd}e))1Ws${(|x!RUkiM8|iYqrc(6HuxHU%q}Nv>|6F7d^-Z-DKGD~azq7kh<V!)v8c@dr<Ohcx7P_{>wwcB&pFy{qUrIjiPUu^P!#P4jX@$tY?UI0b4QkS5*Nzjkk5*d@G;SM%{8^@}2=BzB&qaysqe~@!%`&P}ewq&5r(`wie*k^=64DL(2cE2_b@(-s9<~Pg9Xp$7-u+RS_t(Ryr_-;E@;?eZ9D{WuU)8gS`e1HH^~hUl;a?L)_21qR$n~Fx&)#Wgs6PQcbdDsGYtSv$p&m=SdK!Os2R_D2Pm})u8+t#aEpF#&J-1pYUs6?~|GtAsmsixal3wI-1p5qKT5Lt@GN|^#KhGQaSKAwCUi~TPRS~2ccJ(9w?Ts_hpUKgf_gPxA(DjaMX<gE)G01<Yqjkww9FLOzGjw^!H>ao`4>Qu`ty5m|m+wrkBRwz;dd2dy)F0<g>a*Ou5c-ZztZUt3de5Y#1@OOMTTS}3%cn_qU4s0scgRPwZ1|G$nhMc}&Bb(X<w$$1*Q5kKwe~fnf12G&dEUE`zxE)_Yv`~)MtSSX(1+L~)K6{9z2lU3xB~Nj+=>1Az`UCDyh`{i51{qxs}rzaX4S|a<OTm3DL7Z^8q`w|O8X)W`w9IyT??O$*Rk&_!qETdI_N$tj|yEieJAxnp3?vyt)BWXKbufR<L$RGuOT1(Y)+<oQ7*N>z0$p+oz^us0q65a8|WJvX@8|+H@c4{y%Y4CeaK(?{Z%?|(yc+ze>j49mmQ^hS}O4*UHj08`mdd%rFBUSLy#X3*ouAEqi=qG&^v>v&$5$-`Ye}6!{_s4+F$u@2+q~aIMNM1iPV3?Aq~!9>H_HcYdD8KyHS680rZNASl9U{bRWwL-XmR(2&<)fOcvw*o%9Lv@5a%-7(!3b`H^}yqR#g}Y$3hL8}HrZt*Eo;KF(nY{=P}G%At2(rS-~Zw_;z`S8<<R(a-X450XCPBI+4^5ch`DyOb{t?}Piex&Z$3kC#*4%Ko_LOl#=Ak~B&5cTA3oB3+vnOFo96Htd&MEcBun^#6G)^r<@14TBe>Zzq?be$%<oAML{VvD}RJ%eol4^)2-Cf-~Mz=L_(Ez8Cjr_b+&_Yj2=_-(sBqvP_(l!fxnYt+bDFYH($Y?xnAv!YYqL=S-EqOiEZPUq4yty*_<}D4rMi_n$tqL;lsLPsH&5{pq7qY8bD?M8;I+0w*&UIElHy3Ct%l*D)qB7Z}T2$2^7o1&(8Ujrlm{qc{Zj;}Co(hu|TMDa=#YKZJ2K^AP64IRy7%3}-Gdl(`S{!HjC=0$rJleGgM2nsFraXyzJ5U*;O-K^%e);Sk)7!<UW?a3u3V%!e_CF(1a<ONmG&qLlFG5Zse7khwq=bAj&6-PyyF!;3w<*x#Qqrk8&V&nY5KiFgjdU*{0~O%B1|;1E2SF_L*CdnR)TK9(_>`B>&-7&XktFxN5$F;8S1!5GAR1aoi3A<Vs*dvFNu%;?5kpgnVICG3>2Vcx&jSfCYSKjs3>dT~o0i{JKDq7QQ$9{1&3bLKX^#^QIz%&mAFtVDzo0gMUEEx0yop3{W$#kJ$4#48+vJ8-_E61E(Utcl-=$B08>ZJ-h^N(^9pmANj-$k@T;pZ*p6^O4D{_dkYz{pHKoXzySCrg;5vsp^u<L_d_q7)$fTV#TVZ-vLGW2B-'

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
