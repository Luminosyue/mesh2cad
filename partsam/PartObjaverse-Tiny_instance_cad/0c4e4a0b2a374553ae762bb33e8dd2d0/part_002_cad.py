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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0c4e4a0b2a374553ae762bb33e8dd2d0/part_002.stl', 'relative_path': '0c4e4a0b2a374553ae762bb33e8dd2d0/part_002.stl', 'source_sha256': '6142d0a34dd6c55a24a8714dc90fc0ac979770aba7910605c3fdee048851991c', 'input_faces': 92, 'input_vertices': 94, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10571891069412231, 0.06453236937522888, 0.02965092658996582], [-0.05480561405420303, 0.18453443050384521, 0.12848472595214844]]}
GEOMETRY_BASE85 = 'c$}q|2~ZYg7{^})R6GCy4-|Ag0S{CJQ9M``MMd=Uz>{nVQE3wN!!T5A)3H>_X~IdJ%vtfu5s}k_L)Qz_$q9Ax7_nBTGVjtn)9QQw&trWwHPh72yz~F<|9kd%pZ8i8Tda$#ub``)*pSmS-{vlaY>kDl$Vj#?NJ&ag4@sSuSx0!mm)A?p85198n_5R?h{b_3lhc#zfssn!fLVP5yD5RQ((DWDiK(xq*=Ht8e|X{>>B$a1eNN)MWXF9_zp!pf@8E7qmhxY(hO&lauku3<u~t_eigKvozw4k>J<S!qxEf~4d&O@7eDUB~ne_GS#)wz4H^W!G50M}8KH`n<eyv1&X(oK_=p@7`Aqh||PK9rJU#Iwhk%-qlFC0Mp=8tf%3^)(f=H<dy4-G#I-)n9K@~`rOuiQO`d+T%v;*H1k;9F-~9LN2#a0A-!(SGS0VY`q=>|9ok=k6rJ*KZ`F9?{bd)f1*ryxsQ*?jyFAVZ2Y`;S0A4iXSzRw8<d&%CK9M*DVuuY0>>CexnEF-H=L})QtQJPt>EA`p|r*y2H0x3_|^)I$;y?XkYKcJY+6IJ=&1#2k`sz%kYgM8rH?!KZ^47G{|?Kjr`V#B>b*Nu7z*TAC3Il&aPWAt|iOiD@~svzj-ni`L*_MlHaHS#$~KK162!R;9C#YVqMJ->Y2{IzA5V{>T^52A9;d9$$!zf3im-v_n|JWJJr)E1@%}rj>9*ecY&|@`y7K`m4rN2@6HroQ4Zhq^s42Ho9mHZMD{=)?b}AwZ@Gzi(6TaUpRazg7xBM5qk4Wivlq{moQAJ7P_W+C+3_^)nZ*=;qR$ERdou~~=9N$3t9R$pe$$`kBLC>M@Xb->*q2u81kAryKNY^^(gyQvJa`Mgn@@+3f34#Is_$W$voG{G^s79*QVL%P_<G(_^s8o7??69oYf4dn%sa?$9bJWeXs$U+{wK{bU!p@rnX|9veO2Lnu0?)6#dnTEzrtTdzm~@$`1<+pF@F8rX5=w!DHOlrCiT1EAm&Yv3#Is8IaD{FBfZKWzGeMD=jGmg%!3;4L-Fs<!2Z#5eaoGF@q9g<i;GLP!w>km1oQlH?-JDisD#exkGJ6)0UoGd%U*%sMQ9EAd%mIk%ip7Q_N#<1*3HMh(n@@5`KC__?W^!cv_7R}<S)BXgmK+6%ba~BwTjl|_6)>Zw@b-)^P_XOr3k*-v5@-Rcpv$7zf!D^xo9QjA2A;FTTx@^92G66`bR%Tf7)wlw0|lV!q<m=S%`Vy^;LbwQXboG^s9%r-G%iE7z$r2$fouE>^#nknbMi^JaR!EBQuBc#Q0FW`8n#eF6=8t{J8p*f5u~sM``6v@BiqUVvOtDCgfLFjimfjjuq2>SWy5!JDT#><ifXZT*WwzqKowY9GD7U+jf}hkKMKt{ok1YUpc&o&iM%w@%pN9#kI!OI+ylobXW4{WKsR6E@Rz{%4YD@{ZkQVO*w@;Mw_ces59Uh?W^c(bdKK6BY)d&jNh2`km|gf3t#M>SnHgs=a<7bKD<Qr5BA7MT`kk$o3nF@ob!n7!zg}p|0=5QH(Jm8LDX-_ak{Vkg8uH!t|`R4wQoS<wYj2S-Chk}KN5v_?e)coSEm({fAc!kvt?l(@&u>D*PeLO`|wH^JST3u!&j>JQay!j=p0?%QGoGA)}{GeKLP70=0(8QJ<`a}?}K>~_7i)MXG25yYKwcA2Xp4Fe9V8}C^}!4;xQlU(2U*4|8@}N*<?pO>SE74#1{sWAF;9^%2w-ZEOf%jjA~cMUrtAJcYKY_N_6@Zlcv00>fe8grG)*vPqEPd{V68D2%9-tQ*M$waFZO$8pIsR9K#yLEOjh%40Al|6y|v5Y1|~g!cB4lH_6jkCoxZFp2|9oS?Va}smzmEhcHiOp1@7=7}hZ6G0Y=byD>`*WFE;J&Dx$hnpx#0c>t@zJb<}BYa3>%t(f~WN3gbLj$rP`O>!h_0COaBA69>6sea6Tn8R6{Glw(x;wCwS)tfnlIheIEv($#n!OWdl>oa#^Zp%%wFRL4~FS8e`3$xTZ%wEh*SOs$v=0@D)<;hx?*^}9a)s<OlJ!T)~maGk!TQYa#Cb=uC2Xj~Eo~$jHrM6@4$vlv?GxI>^q1+@7XYIl~oOuLmcV?+Qm`5<jvi4?<Wgg8<avW=4<~U{>>mX*SgPCp2<5`C>k7u4JV`A&n^>z8De@*|qbS$9rKdOIyvi57#`N=ho+dp2awph1%w9s|Me1~q3voC%JWI<sH'

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
