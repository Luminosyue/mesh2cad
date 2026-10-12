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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_005.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_005.stl', 'source_sha256': '17548d898ae5891bf1a01d3bd06c1b5312304c8704f7ddc2c76a5a9bd615c3f1', 'input_faces': 196, 'input_vertices': 157, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1409195214509964, -0.2359306514263153, 0.16431672871112823], [0.11846597492694855, -0.09744122624397278, 0.2221304476261139]]}
GEOMETRY_BASE85 = 'c$}q~c}!JD6vi*2DDJIj-Mwx_1$RY3sZRx5aCwNkfDaJ?tB7oBt@2!|b-{hBwJrUlHjTAvV;Tj;s|`Ltu>Vx6wvE&_tufJ9HEFbo>CAoKd7XEdCQbX2lkdB~d*;mCnYr_L>WmL;7-D!o-HoTUd(Mn(Wf(G=8zDwvdTxGJT6*4q?3^_LMr)hP59$7Cv!*)d1sH|K+R(-6d1<+!QD*4qB_l(_&Cn$)a`SUjvlp(&U7Rj?T<WsCbiwm7Q*+YAb)Uh*M}(V0`-YqA%>VdlDuz&UJow5bp|0=m)<`uz%kYfRa7Rw7YL#1i4pd7m*&cFL%Xclhrg9^0Ql+jwajNf5J$T8!E_ZnQ_mozu+<pJ|b1Jv?-78n~>stQm(Q#MPy;UlwIy~Q3ANl5ukG*v+S68b25;y0c^&6+_WP;7D=R>aB^U!UqN6ViNuU5GuEv(k&Gn-WCxT7Mw#^#TP`;EuC8C9v{?s225R8HgM`NS#TaqR9zdtL4{wEH!}&v@6d*#bXaw>w(Pjp&~CIE@w&7uE69Ef1>Hao35QDwWfCc)o9*Sw5|=_32KJj=NVr@XM$5<@v-Z-%*rt!5+sq3oUgXtOp4fbo0PD&4YC?*5;N`bjhy{xFhF<y$;5_<$9j~)Q`KXbIbkKB`o5CZa;8N>r0&P2hM%@kM5PJ^Wa-|#_4&9J8Jus>+*^7e7CdaqB;+pyI(%DxjDbKOt(Lc*y=LfdrF+Yr`DZPZ~dX??K;-|9FLBd3<|1Nx$EekHM)G_l<(NOtxVmAbk1;2=L~UvE^+S5Pf4*kKWFN3oHNAvIm5Z{oT+(PYWK&!7dWSLn>hbosK@cWK%9Rsa8C8D+S{dm^G53k&i5zhzW0&pu>Hw7&*%G-bK0Li&c3J2=vn^bp?w?v^LgDq<ec^ualQ{Zr+l-0na%n6L!6&K^*GKS;{5z^obCFh&HuPrWk27r7>|xytuJf28T?h1j=O&u;@!9BPMxv)dvW)g{amHDJv#1K_(7G*Emse1K5@#gYZK_L^L48lb^M&u_&KNXb57%TKP*0Nw|}z1+wW!5qvIuWXM5M{x9g{DKJbQLKIc5&4C}AWCr<fR<=QWF<Kf&_|M=mPy7}Rp=7)2dAI@ohN;cm5T(`cQ(|Qr->&rRio1^BR(CtsoedA}`H-5%x{B=F9?6u#!$E&^hp&xm){K<FT@%P<Ptd5iN>v7~e+Wq+W4P_oEzaB@v)wT4zt$5$-9#&MSoZf5KC!6%#3cjjxdf%yz`R%Pz`}uH=Ietjga@V%Vt172+mFE-Z`E;&Y9XD3!IE|BY-#NxOozL#Y$z^uG?0b-N`W_^1B-PgF@`+P^-Ls#{bn`%*&jaT?pU(s5G!LB9JaA6);5rs_LAOtc^L<i}qhI2DpE#-#%XRb2In5h!KF^%n`A)xI-K&m&xaD-PVaNy;zq*&CDnGd;lpj+4PwuQ?|L!MuWW@jd$=yqgp|^;c&{^=IB3>6U2Ra+RH}1`X&ViS_7g#T}k$$p>0V1YA2f+^%5iepebSiv*5tDF#67G?oi0diHpA3zMk4KL5;ixqLbqAr&Ah3bZ{_qpghT0B*m%Im<)Yss{;k!fI!A}=41nq{P%|wj9C+_#ez3J$`J?^*1y-BFm4)@#Pp7ioxYUDZl3e*9gAi^mk8JYy2Cn8tGLTC#7TO!tqSPfkRFZtVGQrE#R6_F|8O=y<l7voxLy5g7MT55*km*RRUYGgpO;IojMfjXIJmx(sgyF{dlm<yc;zf8n(++U7+($5#MNW=nY8hj4sWhFEZUbZbj`vTNYMV&&_keUs@Lc}W6U4`0dSc4?gOhSJvG1h#HEg$11Ux4cZjAI%4$VSa<^hdrB*M;a?`Unxj4e!2?>V%hTFZVzqbOyZ48G*c9j57tA1fK#w1L}l#qAk^uIubepJ_7xZL?j?L0dtgyNX8iRpev!t@X;b#iWmcJ4c`jaZ$P8r8;J-M5eJQd4=}u+anP~w4bdhR8V4VUHZjm~@D0#rJTw;Gz`e21@$g|HI*aHF?FipOg!~F=4t*7V7}^Yl_JwbYHf^BI;rpRYALvl{&S=vS+6G?s)d~Gc?V$L6xbBA<9Z*wVPe4c?3GD<Q3Eu@80^bF`3A6=#6Zjz1j6y%d;KQI@;ltoNLxbTv!?%S7!3Uwf^wZGCC}<@7DEMyBF7Tt#_cZ7PcoTh(hDO0RL*FK}D|};&qZu?9zA2u+F*FFi8^+KS+64Yx5!*!UhaQ06B4VqEz0iH|M@1YHu>)ERzg@&m5${3Yhd%~i4BZL8Uc^BWZs=k7A`yph{}Ar2$32;|0eS>}1AGzm5d2}ZJpw%hFP~vIo=@s#<yqgsb4uN#_)WN$x(j{_+HOT`My}M2@Eg&F>h3}Rd*NmO&iH@^A%Xw&Uo3xr-1Y&Z{)Y>1>HlY<+Okm8^8L~1jBh0Ogg8VR*au*$d<%`g0NgGv1^'

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
