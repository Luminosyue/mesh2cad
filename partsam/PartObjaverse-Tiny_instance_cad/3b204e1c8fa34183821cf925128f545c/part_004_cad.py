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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b204e1c8fa34183821cf925128f545c/part_004.stl', 'relative_path': '3b204e1c8fa34183821cf925128f545c/part_004.stl', 'source_sha256': 'a715a149631ed92fc877f33604c349173ebbddc0575f9cac1e9ce6e2c25ca9f3', 'input_faces': 160, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07044029235839844, 0.039122939109802246, -0.1114354133605957], [0.052701473236083984, 0.16484570503234863, -0.05757737159729004]]}
GEOMETRY_BASE85 = 'c$}q}2~d>x8OA>jWz{9FLKF&(YeYZ=L_kC&x&$PIbITDyR}N(n53U6ft1)O3VyB9zs8mrm;Rv3=3sDg_7HUE>$h0x)*hy&zIyo@iTB2Jt+Wr2|lSDi1OsCnIcb?z-@Za};fBOyESUY=X37^SQc9r7}(-=vTLn%2+WqL#D%H{eJzk;ImHj+yC^5;9<osb%@O}CNCqzzs<`jX`auTZsDSZ;`ykJ>A@&`@f~F32o2<mhETDtk?d-s+d+Wf$qKx%aF9e;;+=G#~Zr>i_dIS{_4|;`9|+7hW<gkackAl*s!xL7RNx8_j6fUjn~-_9fx>|K*&>j~Bu}eH(uD6!>Qg;5)f}ApFuD$T!AAGdkgC-DwfI`aX13`Bn6*M6Ub?^tu7#QFmiJQZM{zH__fD;(d|VHNzjNL;Z$v=&#}(_`^=W5&q}vPKsPr2S4dL#;>`C@vqUtAL>QFS%v7gW+{Btv3B7rdd`a6<iYXIZWVsbz<H4u{Q~0}a>aNoHmK7V2)}$E>eQ8^-?UNi4cE}Vr3-bd9pDFLqJB{n>Z=kl4~qqUc^7;a4gAi$%fdIuV4Ot*Cxp(p+9~`Ge~!HO0Mt^6e%mi&-O9t@dk&)g*2AcK>+W%UFA??IpP+u<%kZ})pT|0U-HLgAb4=*%C#WOc!hFoF@N@r+_93MhziAizdkxs%=C800md2w(ZF@R|@ALSK$lL1S$1g?wkP}?DD)?V&QOD;F=A~K+zq|dE@Z(%Bh&-$52=?(1>bJCFUYbbwcOAQg?;VIb>O0LsKl^Q)@Rk4MeAD6k)!@9P=+Rz^fPd``jMKXZe$hMc;oiM|8s}NUcv|+sPk0e^YBe}N(Hi(YT8#hJ{x*?oFE$B%9Dw>}N3=J8-6*u9fpz`>|MM>R>H}#1Nf&(MB>4T^IRBA6KQ4c25c+`yb#gXf{iDypm&z{+zq1YNpsI!Mwik7_K0uv{?eGJ?K)>p>sAIfeFLZp|8T4zyyo`<TAB3U3#vOH<cfvpFihU`)hdPQh_>w2q)4T|EqHn*8`@Na-eFJrRlZ@Dh+~Zi!gIIs{9QcbTo)x}_4s}{SIxKWvG|rX9f;#@y@H_vGd(^ud_qyfqA)M1;j7K+!bFNumhkd+^d!&9IzPe<;&~I*_{-X@6r++5=n~_+5&8Mhu?${^P$pF71;5^R{{N?xHM_xi5lOBHCh!YskWz5&VZ!hk9>p7f%U#@@D9-$kDQ0F+GZxxR4`+1%f8`*C|jZlx_Be-9=sBcVy|H1{VXF~_;?Aa~!qfFF^<9?Z6g`e{oeBBd1S0_{p{rv%)tD+lxZcM7exyxwAzWfgTRuosF{}{}-`6~Rr!7V}`ny_Dk9q3nc1b(R91>r~Uf^VwZB=lC`QQ@!2M;+<*I*fNK_DgYu{y>?~pcp(Kn*C5mQmqpD*2ie?t>ZYqT_JSHAM2czcM<LT6Y=-qCgJxx(eGX;bmvL5cj>3Enkv+FGyG4c)0f=P-&(ALe=Wxunj!L2!)$*B?JKV5iM*+vzf;L<|823zm1$UqZ3{U5_Dv$69*Xvo9oPBh7Lo4{zk+)jjQU1ZrN~q6pA`D>7T&vots-AvkNxd*zJ&UJ-6nE-N7PZ?M|;!V?IN$L!akb2(cUz$L*(w)8_|9l`t9?t7WtcxjtQ;tMV;#Kow&Cl*q5~McI@k~;s5d=#`B2lY?@bt{isF1wGHSut8b6UE8oNO*|~@7_67VmV^QDT6ZO?`dqqC6623A8zVzh*kx$UIU|yS1$Nb=+$d^^(9@V9Dzs4TM{^mCb4Jw9T^bo!!3C|f_5bD=XHH!R?iFj@sPjUP&!LO>tIxF5rdu=3qV-9|=Jw~FvCG}mb;|4spHEuj_8TGiIU*SB2IHOMAF8EPraKF^QLY<H{_`$pJKBN2;by~J#{{|f}FI@?Ib0hA<=)Yk+XFX6~k&gQxd<EkPx`F!A3OtWeZla$3A=LRW80T0y_&&y&jrJ`M;rI38d-iuPUeP}D_MiM#XQQN$yOg9+*0=xM?5AG+#UCW;d;QO^{wst2w^#q*AN}e-%{qpctTBVSfb36=pe`UskW;8yvaHL=DP%oE=0b+dMbu^FB62ZxDY=+jKusqXkXKL>$t%cN)P>|MavC+1oJNkP29e{*kqnu=sjg&i@_4Evc|6&U+bpX+)sbvZ9z}H~k0Otw{**k9>`wI|yOTYrA!J#nkv+)IGi07fok9L?zb7(e{)shSqy|#`$${ios1f8>$gfdT$g=9muaR@D;bx5~)|kbRc@EW&Jck@koktEQ$5ErnapXnRSn?wBVrl|;F<HluIfEhd&#dt>bv`wLoWNT188U}aqsd|9xzu^&x#XEtKk`iSWa<?1WU>p@jqF0UK3OCON&a_(B#oh}$YaP(R5!8{*^@ep>`B%zWR9WEA;*wYso~^Q@)Bwsc?mg(x`>=Z&Z90S=aKWNI&waFH8q30n!L&yYpB`O3~~ndFPkBA@>6@9%#b<C8dI$?+Zr!0WDcN4k)zl?fFZLlbv{|vFtRUsI(062I@yallk7#FM4e2YM4mu(Ax|KWrK-rXD#>HXqZu+Qs19TWd89Q)P;ICVWE-+Abqv{-{2bMZ{2W<L^(3pw!Bh=7nEWb3<|JwiIf<M}O(kcNS5lXdSCS3X9I}DDmYPRiOI}CKC$A%yQCE}8$feX(<Wh2p^urmISsQC(>umSm{&o1nr$S!rXa14+@85j(wd3h;KDO5S{v|{kJ3`(=>n7QXAK1B~!oL7q@a=p'

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
