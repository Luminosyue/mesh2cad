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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_005.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_005.stl', 'source_sha256': '6da7ab80d2172f53bde9b37b5b3e0ec80622eb2da832d909086e2ff872d5543d', 'input_faces': 136, 'input_vertices': 104, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3503326177597046, -0.3962932527065277, -0.19312167167663574], [0.3858572542667389, -0.2711779475212097, 0.10987837612628937]]}
GEOMETRY_BASE85 = 'c$}q}dr%cs9LE>%38a`9&*GvYpd_y=prBmEH%RynHC>bonfU_3F*A0Wtfq0ukQyy@ZkbwOJ_?_xd#wh{5)~hX&FCE+r>5*5t!XrD+TU-#XWi4(OjGNe`F_sVA3uKQv1iXvlpoL~R571e<+ot}7hHjgLM>PcRjS<;Rf`w7D~B#yvD!}wVV@qM8w+PnDJu3;s+BeIrS8f_74ah+@i}E#@kx&OvgH+36(!3SEUzealRv)X*-E$JS3X^`!fo^uQd68sj`YMN$6CjKe5eYoW65QmO1iJKlWM~bpCVN|RQ9#sYtNG^Y3;47-3u?WztzeA?@Qc$!tSf^T{qee<QnST=#=8UO^3X?%@^^${&j~b-gWbb3)J_(*RD35)NQ_%zk2;qjxTyfidV7=KGSW!h}V*vn<-w?j<nn3y|FbMFMJX2?Q|To$GcXZzF?2{-cDfOTNA<Yj_Msp?Y;-T647Np=b0KU#jE~59@A~Uh*u+OKIZrd0doBIio?3i7xCVoGCt*bK6LfGJ>HjhkJm-`BHs1({EsMJIk8uY_k3S}P`CLaUfUJQ>!>&z*jKO4>)`RWp6Brj-zEH0-|XXhX1yoJ-*)qOg>S`It=q%v*lU9n?}?psM7Q}OUVDAPCp<rUR!Q}1&V1fi!nfwXV9-vkr><JcueMw|uG@T(U-^1RBj<0ODaW7eJfz!vtDZBv&G|3PlIQc}_yfAl*TnpvS$L4+TZhW|Z~tPh7krW5TUpNQ<=X2n&(F@jT#xXr_^xj?@p^5$bIx9mx4ebtNBClX95ur~;CkBI&q?cb)1&J)-<qEpeLm#*d8bjzuZHex(rvyNujl!@JYLr;9yxzVBkwoiTls7L;QGCRuS)Trrp#vD=3DcBWhL)7*BeWvc(wQou3z}p{46=Wi|1#}LaBbO;hH%=@U8cy>f(0Jzb0F*|K&Ebe)v}XLEoA4zbaD7@7sKx=STQrejLBH@cd}of~5SuYje1M;alU~^sYJo!TMRLp8D11{)BJ6U*XAIkG8(?th67d*PHJPeCs@E^V`AoZ&@Mb_wA}M&w2RPe6}rZ;QZCeay{Nn=6MC*nx9*}`F&B^lB9Z6rGwuW;amHs_8gx-T1{u0R8MK#aoy&N{Jz?5e10lxJEVBEzK3~U!MEbWJbXSYpSQ~K?{DS(CVXqWw}N=TX?u>f+3R<_bj4gR_}2LuxsCUm);wQ|_r*PDt`~eUUTv|{+&^3T$@yD4kLxyH#4B~hd|oN9-8du7XZbolKZS3_Ck*8CQyF(!iuc_4(i|^*YyW5JdpSO#M;(ttd{0vkyve`k%H50nz6u}TN8xMuZVF!$zW9#cH@~xLL&GI|9`PL)zQ`kdP52@{#r(cIauYAx^SH$Q0lsw)!To{mIqcu}<L|1H@!<Z$KJGsn?myn2tEBvzxX-}1#x=ma&-m0@DP9%#rIK1H-h=y+>-y$zIsV=p>GyiB?`L1@{K`D<GY+28i=^A<vVC_p__`Ut(r7)6+h<vc?dnM;JwpHf>bcnY@2;Nd8UOd{IoGJ+Nu$j}BQAypf=PqHJ<y+Rv~K7VcR`=nAARBg^ohHoPuv}S;-2Ue2cb_q2YuqF&?jDiKJg;-iQVWEm!eO+5PjnL=o8OHe>TQD7aWK_alX-J8f_AEI(QN|5BdZ+4?Ge&4oo^6JQAD<eH@$#PKFKuCxhdm{lM|ySTy1&XdiGCI1KgEc&0)pfTx0|Ku3c~v%yoqxzKcQE_fJp2zVGc5gG?h1V4&K+!q=H?hEb>jR5xsKLiZ}hhdDw1xA}?w8_vJ;K|^z&?4|y@F?hbFzE>JC~y{ZC^!q80v!lW0VhBo0Vja_qY+0#9|lK*!%;ttXBu=OcpA76ItEOd11<!+piZz0oB>S&XMhJo2Z0BJA44M!g*w2Y;1FmeI0W1a8V(M}7>Q{Q)80)5lO{tm!6U)s<)JT_RJ@PG`Dnxw(1=H)5oe<jr=t-MfyRMjz^SM)3LFECKqC%=MuBM$q$%beAsq!C3np(e`hwH2&IRC!&@tc~a2nPw$Hr+`w<Pc&r~^#(B)}u>4<?Pa#in7cBEjL%Xt1BrN|Xl=u?j5%tKf2@73KT+hX(x9pJpCB8YPzgQ1jQHls~KXpM25CWqo9e^1Je<)!+EH($LLxGAMrnT_`Wq'

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
