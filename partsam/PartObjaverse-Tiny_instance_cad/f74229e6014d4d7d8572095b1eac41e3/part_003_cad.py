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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_003.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_003.stl', 'source_sha256': 'bd0f9e7184571dabda19b1d0d608d5fcd37c97b6737bfd6c5f8cffd59a4c6ab8', 'input_faces': 156, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14791160821914673, -0.33732059597969055, 0.1261885166168213], [-0.0031670108437538147, -0.08484029769897461, 0.37888476252555847]]}
GEOMETRY_BASE85 = 'c$}q}2~btn8OINbqR}V_Q6nf9MUX`l#RWvTprVN215{S=u{;nFut+eBm|WuqT9Zjk-Aa?^5|<epjl{JEADYCBsfr@t)W$xY&ZtvtjF>c%+V-CB``f<Tp);NK&7ArF@9%u)JKtH};|`{Tp3WYEKR#lQX+VYOr(3=C7apR@Qc+o)Z&?{qwxZfexDuxibX(HGL{o;7s1mFF3oI-1EBqrA|H#6r{=tfWVR=PmMQ+)W@`?hB<Z-#nS6Xzwa%t`gi~c+&G;~6+GBF@nS)=@qpO^F!w9o&1;k>TO;q9$b?H@(oigw`I!7apXJGZwxa`WD0#MPX~ZH`<G3?nYwOa^W?KfFovOgr6b$Zy#~++G-D;OhER;^O|FZaQ+Y&y%=q#1R9xW!AUQxa>#+w{9Fr+?;!-#SnjN)eV||$2J4k^4qVIdM`F`5fDmT9TsWecF)>onrCRJfvX=kUh6Ji39q=?U4HF@&@0{5V}IiG+wSVu=03RWxL(_57kHl=G7RVVf{U&s;?|qH+YRv>Lil`Je{6H)TGcZ?m(|$@Za#2~xSIS`t0Df;0^;T|(MJB-2;x>ZCnJA;pU%bJb-_@-Xf7eHq%JaW<={O!FLifUiy==<5^>wwPYm2T@;IHBSXpD>wo$IcZE@K~zPp6ZQOrs<aItOcweI58U&LSSHve7ME8W#&_j>qsxAjM~U3Ofr_Lh&8>OXV#62%AC+bF(0>qFu{wK9+EB(DDL(FgP#{xNaw+-&0FL1R6|_jt_lyIyUQ+}dX!anaDp@w0bwyx%C|%I#Cc#S=f`_JL1#QQZD##BEo9<asA=B(B`M&hfJnIZxjYcM|t~#Q6jFb9|ToJ5<NR#@|qUt?NaKFM0oM%6nzSIno1vy+HfWd1EU*uene0)?b?_-ga>haqW$*6t86la-P~v%)h;TlD~iZh@0ak5LZ_n;dy)Cp#0`jL7e|+KF>S0nYfzb$$3uhIz{6G-ljbECi`Z3{{9ffTlYs9xOQLy%`4i^64$bunWuzso?CvOQ~c3$%=_GB-tc#>^GYOf@og#R|DloUu|57v9mUnZOkDi1oZ~$jh-+iQPgDKj8gW&rCoVc(=lsXLdEfrHmgB=u^8N^4;?_HH9N*}2hWMeSoTq3I^X9X(Z}zq`RFA!ILoM-V)s)9>4yJY4-bf>^jn1QbtXG?O9}XpQe9UOdZ`;0u>uLXP6U`Ua!0Rm?%Y4C2;@Xrh%A-DwU><vnxJdFNuFX+7|JSQIkEM?CsQp{G&UbP-{`YQFrxrAi;uYVzja0|r1H7L$!TXtUdjs*Op3E;T;CnUb7ID#e`2_XPxx)JsQ$t*<i{W*}AL08@Fok*AUD`L*yN&Dl?D~4*e{kk~UJ$@}YHEm!$DN%2n*p?+O09+Yn{~VopWfm1hIOnX?mn8h`C%x<i=2DR*Y&0P&DDc>U1}@yp{Gx9U0eCw%d6M%y$$32Jm$~!ly|&E@x9j2{n7TB`QGML5!b#-;PoEf&GE@8%sbxYc(?Cqy&_F;p7RQ?*M+|?%KlH*Qe4kQK9{^4%5RSHV4m7S+}!+xe+Lv7;vzQcjN$%o*sM`}yeH?m7{vQ<B80fOwS(3r9(=*)VjIHzn?Q=UZua5x^?L73;=`M0f7HY_Uf1s;iEAsqByK%l$@M=O!0{rR&t>~e-p?=7YKT8yPh1Jw$aPMOs-`^dQMk7*RHs&O@O6ss7l`}mPTbm&zKZzeM_kWG?{Ym}&#Q==+i0H^cRnxS<NO+pfAM=2J&yAqzE(-`&h4DPX(Dm8X%BI2{1E;fh-l$^_0y&b;-+%q%Fk1I-^Ld)?>&<8+kP3$^%TZ2KR%rI`Byu+o-KPzh~sz0HkbEbeEMB6#W__{9_trJFGiaTZ_k&~>-RRh=)X96>#M&#7v?&=I!h=&FSPqt=i;#c?$vqH<p1~8dAwf3IK54RhQUvQp9YPApQ5)&y-k3I!q3%Ps@`Tn6X2&|>>Owkyqrr#ZmDtbVem1~`S5bCM9e33CcK<08}ms`gO9=3BxnYFD8`P1s_+RI8wpK>Pr}$#Xf}M7-sF8)0*!}XsJGdAONU0mFF{N$bOC%iVzQvo@UpJy*n{cF6$hP;SgDiYWzMO{D|H@x6k?*G6XE4r@~|GM`S8(*iHA;g$Q_HkQcdtOX9QxUhQntgXBspIej;L~LSy0OT4o^M4CI=O{!Gj#buql`PeBf;i{R5RS0XeSJ{&Qz&`kIlh>3uvz{~z(%qP_XFZ&CSL+VoaM2w#aodLfHF`3X}_+-?V0xf`-{biU>>N0rQUy2-3%i(8YE)_Z*eko##p=IznIFABosYC7}#7bQb|KiTghc1LKM@$*C1YYLML%uxZDn(xj)+4nLUXINIlez>x4|5ek)8R`HQwYt4FG9?6Xcqi@jL(4P!3XMXjNXFa{qQWkKc1xzz_awhc$Pi{&(e>@b0G4`XZhVTqrQ3Yl9}KoTMTc)8JoeD!CSC4GgvOXWKM!VFaGSf!}mbnD^L&kp6DA4eFfebeM6vw;d`NPD0B$C{Ik_tZ^NLk!uLU+Cv+HmU-WrFJ>g$M-*BiGd_VM!fDVW6k3Mhc2zbdAy}b<YjpqSiK2QaIAo@l^ec)ZuHwrou-VJ@e&{6P%&^H?D3vWtr>fzDzKm9B1UmuMQ(D5H@|31?A8sRuHO3(GrmkLutFL@67q4p3z(=}e+1o02i?sMz'

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
