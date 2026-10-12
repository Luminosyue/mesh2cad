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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_012.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_012.stl', 'source_sha256': '3df588d0d31ffc982003518fd2353aa205dec7fac7ec3f603aab5788bc376ad5', 'input_faces': 104, 'input_vertices': 102, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2008998990058899, -0.21404153108596802, -0.16689945757389069], [-0.18839803338050842, -0.15520310401916504, 0.084695965051651]]}
GEOMETRY_BASE85 = 'c$}q|TWlLu5QdNKI5!{-B`FPYl5HDsZVhRgLP!Hy3glupiPI8FXxi9K95r0pVpkPORcWPyD4<3Ho&l>*?F&K(Xx_3CMQH$Wd*UJ_OQjD8sgFEB5uD@wXW27eBm^t{n(?>eIdjHipLHT0Dyb39wMCr$_JwQJl|m@pDr&^3bmrv3Y&zR{?8IU~R2R6q$i6u?IhvRXh*RQpbS|Bp%|!c*X#ad~w8MzbAJ3f3q>jxT&&;J2A51-)O-r6VnmUn|uUmF>b$1v$TRV(1#(%t271pN9>#Ne*jU}HcYkdB-z3Rj5_E$7+fm^A@<pB>j!Ock3ML#ay?z-d~AOG$HFSjax|FmFZ@0{1-!R_oXTD<t->RRDGtDksL{ogxWusVs`Z|QaBR@R*O{@<=>dBF4Ct1Dh^f?Fec{en2FKlk2g|NP)Z`N50w6KDC2<t5+#5a<2LonP|p4{_d~<nAG-?qR(igE*_lj164ztA}`=)sr7_xHY5Cn@zl4uamgRKSywZc{BT$oj!k*F3e%Bx&D(?KYrsI+mD+S=QN%KPo~bSc)0;?UBB>}cU=K4-l(|f%UgC`^5vraLoYY3Z*%ys(^~z4c<AP3FSmaJ|LUcewLXAb7v9zK=l)n<^UI$EH(7pz;=k1M=WimO=YM9=KR<X;ev0S$pI-FMZ@k!4_}mSaKY!NYJbw;ce4*!0QarE!{U1Lr^p(wz%h~)8PqO*3D4xxa2`;Yb^J9RUuj}*U@+g}h%Kv9up?+)qsFQzh)cM?JtyjHVfSZYNEk3{0>wNE0dVCICAl~k~an<kpRm9OB&guI_oPWQF^Z6&v=bt#AXE#5aXE&bBryI}a)2)Zi8*x5wZhkgDZXftOJlEiGcK#CQ=P&1U{uag4?;+)9=dT;j&R;j4ou{1BdEw?^=Ob}`KDzPjymRB(c}JX|U!3!L`1wVgpI^lJc|@F_N1U5%UF|$dXit;-);kxHVOg3~g?yTvPkA0C6;u~l|3}G%o`3l$+4FxNCAZ2N0w}##Dk0SaI|hH3)VS1c*a`TLsy<5%!?wWRCN(703OfQ{-S0rmF#H(S*^9M$;CI2s;KvZ(g|$@;eUS1WfF`hy3GAU4_3uFK<M2mOR~)sq!ru-%3V#&w+p({$*wYaFLG<A<^uU0>1$GerAmWvOo7C+>4TocE;Rj&pQhqsXE&OVs{-Ov`16vNi95Kqj3$`A%7XBV7Q|b}ehv6TVnwHuKZ325r>Pe|es0wUK>Y&sH=oYX;QZrI_LU(}emkJ?Q2)UF$C)J4eG~zwVe*)`NL8V}akTV5a2mdf?o`r3IKZV*Jhb@7B1os=D2-qa<mq1~#eOSK~3W6o2Hluf&(YtBzBgh-UJ;l;eP1tu6_B@9@)Zu;|?kWF(R2h0*hF%{8pG19O+&h4pg6MY;z21+yR1Mv*_rWhke><TzuzRsq8PpC|hraKG?gx7aduf6Oz#{1HgHS)%-KZ@HHG_rG_j{lySP*r!LCs(ru@9=h%Cpx9)=R_#!J5!N{nh{bvI;+f-ar2Qo%+wZ_nl)hm-{21h=*0JvcRBtUfQ2kC&gb{9L{P'

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
