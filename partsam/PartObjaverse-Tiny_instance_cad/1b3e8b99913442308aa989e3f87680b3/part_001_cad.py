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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_001.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_001.stl', 'source_sha256': '1ef6ad33049d1ae0b94b04102593f87288d00fd14813cbb9b46205280d670ede', 'input_faces': 72, 'input_vertices': 69, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18783079087734222, -0.11996284127235413, -0.4033467173576355], [-0.053875282406806946, 0.02684483304619789, -0.30389946699142456]]}
GEOMETRY_BASE85 = 'c$}q{3s4nR7{?DH<|}!4eOy6V1iYevsJvBJz)2lOqnUhW!$rJ?k*F8L2jQ&Q6gHw3lB15(rlMnt3W_6yy7>S#O=l1vspE>Fjz;C9#<FqR^Z!0eo0@5A?|k$B?{Ck3=R4=@*}WO*o^5S{jv#UM%!!ka+6f_}v#^N*mwVpKY*&6{-kgOV!UtR)PqlR1_^}z2Jw$;hbWC^UXS*GVievbUct^P6m@(Tu&z+T*IomzmCHYHPZ{@ozo}ZI7$7P-Ok4*?yhK7YJMaq9YI$9-|=Q|!hWT|?|Z<|zo!-;cJwT-tLq>8{Po24p6Tfo)2>)=}2hB~Rn^>ycQ?sXR2XnwFAdTA}%8@a{cdhXGUxIbV#xbx0Za3!@1@@O?#$fJ%sQ;+i_Q+MLJcWop1;sxNwsep25_k3_A{>D*U4{9k(mYOsL`OS!&Bghjq>j2tET)Y6j+zxJ3G@@VOyB6GOFFTC(aih^*$%q6u4!Vf%Yo_tOUIMN!UGgQ)zgm3|*Iyfp`o**YaCOuQ<S`FVya+AHqxN_2QNM+!kw+Pq39hx2?LfQxBaz3r?I5l{q<+8di9Ff?e{lV3Bi75jwi@mA;P#aN@|8`{H#}%Q?|pAzd`q)2Z|Yn(@d@SNnk@%)>OWS{xc09ES7VFT%lR~}l{cZ@)@<Tlk3YdYmo5R<QYH~^zK`|Nf~Pmpyo3{v_zra{TbiiOg#z5v3Q>=izK80`ByLm>-U2>RK^`T%;SjD*owOSL*4n}K+j-zdK_adDzCx;Jb|ARcTz!znb&C4Ue1dc1LIdVm9a&F&(aYc>#fP5rrgy>3`D-vQ+HZGPB7b!ZJy*f+6JPZJ?KOJ@t^2WI^qg&fyiT^)W`$Co)2&!P^KQRg(3}>kKjK?j*F_64pCX9X%dAKOcUHSF56<GxX#VwhYQH2H+<fy>njinYHK?QAofYUexB487cTWxNlQh)j9RKbmocC6Vzf(o~E-V>bUB74_`nmYt7r35xmUv_VxZxiSu05hWYJ-E?@6DrmUH*{v(fpHp(e9g~{oo%LqP-|D0oOO>?5F*D9NerM1g=inyavx(ZWi*WHBa{7{+L%wC3o(O1J}mpf{RW+&_3#xfPEo~f3Bi+ID_?7R$K;m{#prc)=vO8wuVyu3yP@ymDbPEe(OfGH%<=+HyTQ?kF;Z@lz&4X;sfF_|3X<z`_T}Tr`D`Mo<=vgKJZZ``gL|i9{s{q$`e#Y+&8fn`coA3dviCq*3z;}j#rtyoyJ@D0k~QnwMue5^%m{Z;L(*d?>q1unneRC&$OGnabIP9F`ftCR@xW-H^9Zi+mj_X&;EiuV*Og;6G~@-Z%d)~Rr+!~uUbeLUEjTu-iHNt>~r1IXDixykEZwP;xQP%$Q-o*b*9n#T>G#L-vf~_=51*7uJea7p8IN6jal}Q>1m~~qJ#C-oRRg+CsRUsJk`JdWX_EKSD(zdA^-c6+1{$5yA?fHgW30BAIciVK9v1n*5T|2vmeH)vLD7inKglZGW%H8X!fz}hq4Z0Ka_nW>p=FA?88~Z*oU(pz}kiV0QSDD9oYM_@5tJQy;LvuAyx!hk-{N;Jcsl#takP>?BiH_v5#Xv!is)Yq*~FJbp-pq>=o8t?Bzc#`RMfIklu$wdOuddULGFo{n*<$r0;5lKkEw|(zj*xU_Zo)2rCkK?1?-diOfS-`>>bea`2c^*^jg$jWvnY!9Iz7e<8P!5CL45Kl`p60bIM(-t2qw_+R9Zz7vP^omu_Z%No0JogwT4IlA#$N%dy$&G*?^{n*>t_hPlNw{dOKXQX?yv3dT}U+O;(O-}T4f3W|0=ku?XXYY))7VVFhOh&pF{*AY>ese8-Mb3iw9d&Hr(E'

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
