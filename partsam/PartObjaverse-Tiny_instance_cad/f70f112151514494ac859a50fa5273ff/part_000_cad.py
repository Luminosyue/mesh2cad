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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f70f112151514494ac859a50fa5273ff/part_000.stl', 'relative_path': 'f70f112151514494ac859a50fa5273ff/part_000.stl', 'source_sha256': 'bdd99e41993079df3a727b2be4ef19bb29e343da2ba03e144d2c7a3a82b46a52', 'input_faces': 76, 'input_vertices': 98, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11923184990882874, 0.09050530195236206, -0.047441717237234116], [0.35022464394569397, 0.3534872531890869, -0.018387258052825928]]}
GEOMETRY_BASE85 = 'c$}q|2~bs47{?EbDW<p~8n|3jc^IT9f{21wMO56Lih>L9P$3awm&r7})0j($817p76cBU@oorBZ;XVO16&Ju|O6{6s=0;jgI<(k1-}h<vI<J|g?#zGgcYp6Y|MQ)5&pBMoW1O7b7+&4j*7ut_?Q>yFs0DLlISHBBNwX8OdZ(r@aA2*0i|hG)?f5C<%+nlL4qIrNlaMt#(-bV31}6rYd?iz2T4r`;d}>@;=9~n<!{bx35;)JA8=s!QpS=eL`AYu1e5LoK|9Um&B`A#_92+8P@pC;3_ktB0EBH-b_5iqIjyVnYj4K-iSLN^uJ!gg1b%HB*(~SIR_9pO2N>+j2%c;?G?dW8ic$U?GGvaQ!dU8GFU)>6vU5Wv&L^-VmKED{aa%u!{Emr{_%R8T;&$^0p(5`<SaBKcU<k#OuAD1KG&qfY84$u9Lektzi>`~jn-;@oUjeQ7QYPZvBk6TltKM`DNx*L7wbUv*2u`IoV`Kxjd82lsRD}j#=#d+>jUjX^b7Xeqp0)bmU+P@ii`d7$f5`kOVKf(GJq*g)uQ`ezi_C*NP$z~l!ezWBf@VQpJ!ycFJltcY$M6+tB-(ma_y^p$P5O6lb=YXCoZJl8rS?rInF05q%;IH(XiSwI30p34T9__TtS31BvC<i}BZrfX-_mN}k(Z6Ry9lSUH#f4B$z+xD`vVPSeeLnj+1=f@7>IdtK*-X%{?6(5Ab#G%m%-f)VBH-5!VSb-<T#p6c724zSqZAzPxU1-sTU`tOQTs7JuGu+U=lhKPe%u|nyzMUJORcht!DpVgfomy$LjCIG`M|X@7aVWPYVcPso6m#)w!Fi7e|1qNaLwobC8+DfbgZXg4RDKlE%>OvoJO8{<-B1&J@!I9?CaaeeHwu)aYMl0`jg`YXuo$Z>>JDS67bP{-GM6u-C;hJlwL5O+B2^UxKH;%z7{>J*dDi*Kfw1TM*x=_pBnsG<tF4ycY(k3WIWdYRyq2t+<qCjv<m9ff-13|g5!{{g|0^bx+(*gZaU%ohuy+)z55vUrPgmZaCKn=aB0U4$d|o`<9hpnU4-YNp|Jm~PIF4^aZ7vy)_Jr&aK$t2n0{PxUKil%#m$xael^cL^!aw`CBwL44`TlPRD8dW!;9>3%Y=)tKBWzn*zeRWu)i%i`Mcmf2H(W|CHH`9BO^-f@}he1XFG2Jml{7b)FXZR3^>~zT&?$)?|Q&GR+e?N>Bps5Q-I4+xhKHqaR%hGwz-(Ed;?sw`Ig$_YS#l$k5XQWK4tzV4L*Z@1Fps#I<BwB(zY1aaqONdeZEw-2YFH+{5_JBBhjZzHSUuQw}GpJTb0`5%9hPIKeij_Qx$SX?_;??3D-^LYCNB|pM`mlZOOoy^?N+$GnSXw<>%U<|Hh@buWCYT^gfbD9r|Z2!E<6+EzWbp9pI|<3UEtwUWq*}m3Kh@>AzyX1rJW?>(`F|j{VjSIB)QGGvhi78;kogu^XNn`(to@M5SLayqA~w^Yh0#F&Wo!(mI2W8k-MXyQRST(l*}1^UY@saOKKe<UK12?Qv^!cib;ek+U;qgO5~G3|ub!<FtN0Rfj-0M`W8<jefkAka56SO{Brc>NXF!>UQw_i~7xmuRWK<f_AN)8545hUweu1x=%d;#r6Dd|5Goi|G)aw8xZ)vKlR%18k&iExLQ#x*ehJ3L>H2Xo03G_gyc-Q4m5m6E+>iw>m{}jmp4hoZ;(XnOX@<o{kTkA0bG6*3+7L;U@})<u0bRb2a`lRnADeY1E{U==*i{D)t##c#XaG*Vcdg$^CUKnE1oNgt0k8!*Q-o?#$znl46$CgVz~Nq4dWWX6-cpQy}5$8`cR(8pGgw&bdrVqLb*nAg-{#O_DzzAeMmv%-I>daOXBKEv0$%L+?9UwBK8_rCoT`JXd2@*>QD4Lge2mjTvI70n%aoA9Z4eYK<Y%^QItQG+K;3$4Wu~<q&XT!Ol%)_uJ$Amw<C$TEy<m7o74Qap!eZQEP^YNYcxs3V@M(%ONyl230$#UX0CA*3pSo&!KQG<aZMtLcp^!}lSy%uYo@lsBb;j#R~Xj_iUk`^@d)~D6fyG{2S+!jfBM()?@NIVr~gOt<(9@{NZ+!7KfXAW%ww8}{mVD5Bg+skL(C-m3#asaz5'

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
