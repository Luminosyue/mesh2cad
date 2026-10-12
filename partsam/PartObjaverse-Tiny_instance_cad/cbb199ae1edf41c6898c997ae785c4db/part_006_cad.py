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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_006.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_006.stl', 'source_sha256': '9c0c445b600e75b6041fe55489b4b2e932047aa2998a51f35226884ddf2b3c16', 'input_faces': 219, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3645627200603485, -0.25712525844573975, -0.16250666975975037], [0.020853381603956223, -0.13004429638385773, 0.16251179575920105]]}
GEOMETRY_BASE85 = 'c$}qKS!|S56#iR4p`g?{xD|0IXh90tvX-qQV2hNc(pCi*rb1h4v6Plpk!^|_AX66>i%UByP_e!UvZTTAmrWBTlK3D*F!RWh#up>Rp!d%Io$H-%#>D6(C*OC!d(OGHXZ~|$GA$|Y)!XNIuc6NV{LrdMy5ndY;P{;8%7!&H%PJek)YY#|anfVDehKbaP(Ht8af;LItjk_r*|@ABdx}4MTGiz29DjDzs)jWU6?IEjH7u{xdSS)N#!96(uBfQ5RO=DBlk#%><3{HAH~9bKD@|P?dcEw26AImeHRm-tt;Y`)SbF5My<f*L?CF8io*w$r^LP7Zojj3554Ln4vi0beE3rJG-seu+dIY*Vvg@F&JBPe;qm(~-(9?s3mkuY>qd$N9MKax``?y8*G2Iz*@kreLKTr4WIk)Yotq0HV_$n6XPdR4m0q9Y>fAHGEq<U!hfTX&+CoO4y(G&cSh0n&;jxX--3WcY~^vEA&J#l*07*EgnKF&XQ^y-;p^%R}!=|B(sT6Wle9^50I9vOS?w5|J(FE|xDf6y;+@1y8$O?8|e`7tx5M}Dh475DdccgOsk@Hg@L#p#~@`=3d5u7lg_T2E4a^pT#Vd7vlw&&!Xk-RiCJ`lt(TEYI~T@%1m>7t>vO{zZ>aeT;uWS5iHSy7@D+&L-<e)}<ds=YABO`%!f6N0W#8k#%`~Sa<0@+>hq|)Q_TbKZ?%%XwLo4)8)A}=R$Y!+?qO|e<M^M?rU>T>T8pq`kM6wf9h+KU;3Kv!~Je_>UVR0>UY-p{o;N%_oRLoo%@}2m!4bhcaxv`-RRWstaBZr((hC^GY8OL2|DHB`M`RDKg|cD(|j=R7tIIOBUDeG53I|4aGQpD=hEl9=n0?i6E2@g<}W(?hq^C$&xg#P3*AZe(D<yAwjRWsiG;ci+PYun51uR0dCssd&#lQX{(K+N={`JvMCbWq^3(h=`Dy-`d(!+d=hFNU-NBp*QGML2m`mi(^T+tp{9!%8pXQIzw|jHO%`We;&y7G&xDU-AQ#YDFtn>TG^T*tW=8t)PX#TJ+^T*tu=8wrw^T+5ke^{3}VD683!gUkfA3bm~na+O~&mY$LT%JEhr}<;vFPbx~N2zY^Tu*oC{t@UQ+~3_@zDpy|2i9dih|cptbe<2Q^L$`ko-31|=7YHp%?HtWK8Viq!Q`j;VDi&^5S{zo<fpzi_o2RKJ;9&)+UV5R=3MGu^LJ7Ivd(qp{x#=P|C;xg`j>U-U(vaLO@8WMqf`H~E`4O~PyK8BsUKPAJlu~)r+zf`r+#ETN_F6VH1$d7$0eRWe;<Gz_xWBD_v=R2#HK5!(;P=zKgZ`(Raif5Xi>ielmE0)GyY%ww2_ya|9^kln5pjYpt3uFw}X$zdIE4J_$$g@SGE|q6nruG<G`oEUskpaaoZ51`2l60D0>OG8GIe^Mc`)emCDvC+Xeg({5iy|1g-^NqO3~UtH3wGwY`RYjZc7UtOl<}jOOnu+oP-jxEj0?xE#0|T)$G3l>y7aA6534vQL3s;F-#@l|2M31)rsCp|U%H!z^Bkbtz(GZy53ogPw_8rN~!`c+F>HeV3I-_#;?rycc{H*0X`7;B%DCS2hGV)Z+87*60T>!g>yHzLjGEd^Bc(7h-R)m47gNir}a5ZYw4WK3UKQBTo@>6d_*DTnJyOa~A5h05z2RWWuKqeuc;_F?Rh2TlFtQjzYw1uG{}MWe)%Y;G>nzP<A8GXYl~m0mR6j5BYr1(~v8Gd;!F3J_hT)RvzI6SZf>vJ{s#WzySC-WmA;h1iZ!K`B-aA2hYQL9B>NwWMxy84FqO@=VGrva3J_p<jMdJuwpXclL5Uy^5h{$9^&Q98Ss@lXP|CVQA4>;8hmo$my6sIW7ogGRsUS%$VI&7P0Cu7eE{qPe^1#yWsSg17VpHm6EU*43HdfbZ$hq4<m*Jd=I>*@#>yjnKh_#U)?N$FX@RbJMA^s6UI1>e_(xc4TyO1Zd>*(ST>I~Zrg0;9JNBBb{LS#`fL{l4NX$m~Y=qv7JRQi<fp|G{AAF_G8&S8tsG;1a2|n%cYe#O0vFqP#)xRA%+7YjLP+7gQ?Z7thEy{K)dlFb@@iwg65F>ka$X5qFh+J*R*M@k_w_^R2l}GqHSZiEm?bYL)dgz+Jp=^h;Wx!`G{x;ScYpgwu&j4${-%_?y*$QASco=&Xz!l)yrxkv!$RRPc@TrAffjq6q(TaFEb2ogY&b6r9PSjBD6NFC~eqrR67`y%zR{g`s5k|b`smg9pHUgLf-pkQn4!!+;*h|Hp_8AEr3%*EMiL(2E!@(cMdM<Dg_;h8(%5DYT13nEg(}Bg{qm)fj)(3bq`2E=H4eSH1^@-3*ic?a3z5eOndw;(|`U_FqKl?Z`{;RVc`IE|JzDSo8_tEuI1xt;6@w%)(X`R0S`VBFk'

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
