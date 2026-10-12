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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_005.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_005.stl', 'source_sha256': '993b8d17552bc020192300c2422f04d7712356697436d52ed056e6e01b190cdf', 'input_faces': 86, 'input_vertices': 56, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09512653946876526, 0.38425448536872864, 0.0037525631487369537], [-0.02525981515645981, 0.47775962948799133, 0.23179638385772705]]}
GEOMETRY_BASE85 = 'c$}q{du$YC6vbyBr4QTMmwiGz+hTW1x22D5K}6Yq6iq2?Bt+VPPD8h$5&GCR#fFwFO_er+LHNTO11>Gb&;lYzN_>PxFe2;(5G_T(Yzr|lF}6M`m=yH;?sryZ8cd8%a&yl7a^~JUvy;iXDoo}iNgNjGlQ$M!_J>IluV^VrYIA#9>({wk3LBc*4N@F&euQ-Q@>P|tDudJ}ZMN3BTh@83i)8EKx`kG|Y^`hbw0de9UTpN#x;cNkW<!gc@s{;9O>TB>D=W9lrFnL_Q~s|<6kEYtUVY*uQza_%+a-LbzUP{``hRa6=3Kt|<5l8EKW*UZJwI`rb6@1yQGPCu?hI(TQhZtTIW)D2bbA<a+4m;prE^^Y9hdq={)f^wuF3|Z=o5ZG@LO);K6~nilpon7xV*oWtJB+ajPiFnX;0te=K&pG-E)odr~0<geXaTEDDlD<1iur}N!+=YxctR3>f;?B4(Pb`d6B<6(n0rad7F4JY$fGo<HrFlpV{9z=i&#HpSBBLwsbS`u_MIgJ=xSpsT~Sv`OLi3>?H2{=1F=E{u6%&biC}@>$LyP3te1;uBs!n&;A(7`v!jw=(stR@=o)_R@(oU6@pJiP(GMG8PM@niIn%x8lik};L>5*|I8KIKiClrXn8PaT<mY1@)9@PK16#?|4RLxmmI2&uem4oZ?e2f&!a2*Ak97h8Rg~ExvGxmt0Mop^A(!2<H`{A`RYrNUujcyyyWZa;{B_lyb@y?q(1xl#C!Erx~k=}VL;>uU+yN&-gtoS>sCMAmr}i6)pB3-;TyEi-Kt)CPGfuDBYv!z^3G+|s+KF)Iw&t?w)fEQvvH}&|FMPgzL(ajI$qT)`X>)jUMXmQm-?Koq`ZIa3RTNx+iH<_oZCioe)2ppAL8=ljJ$ffpZHjT_}zcoscN||^0DtIKXCIky1(Vag3AudE8V+PEmxjdLV0Q5H08aO6Fz#L?@x>S{k}`pa%D7J<j)vI{|n=SPZ-5}+t#gWxttO!@+UJy|J#qhL;Q(e@jGrEQgwXKZp!=Xx9=c+{Ki|f&%tf_Jh&3G>wey)`}%tq2QT)RC5cxg`})__Xg>WM@*|`V{`A*7{?(^{;s5{iKg4#3kocmaqFHhFD61S+#n1wHu4V9C7r>XZa<D35H5ZzV;@%E*z|X~uB4{yuk)~fU`iFX#<9q>TJ5XilnS*%+P&>RGnGnyx{2a{Yeh#Y)R(Vh>JlFZ~Tub3gSQWCev6>A{M{%DEErg$q88&DhyiL<D5B)>EOK@I_*@dY2=$V0eR%kAKE;1pWf%zGj&HW>+5+(k+3eAGg!gUsCKKwlNm02Z06Hwe|LUZAhFhhn~;AKre3;Kt8&%=4X<~~CAl!-kPuww#P7SyWYiI|^=+1&GgS|(QU&{%k`Dezp=;8R&8vx;M7h8j`a$3T<e&6p7fjfaoZ^ovLTR8$(SPs8kFR0?{UFfSGw10RD-Ean=KHDNYq21y*@&{^<Yqu{wd4DYHi7?Vu@^cVL2;ibmfKeRKi)PMf8SKed2{{9%cD#G|KY<Z*9%=8rBM*0hiD<`4'

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
