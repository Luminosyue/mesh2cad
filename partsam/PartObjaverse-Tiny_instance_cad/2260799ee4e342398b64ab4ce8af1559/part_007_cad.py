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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_007.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_007.stl', 'source_sha256': 'f3c4a2f3b7f2038a105c0b7926feadec40868ec8bb3af43341cf08ab390b8492', 'input_faces': 42, 'input_vertices': 46, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5, -0.4499409794807434, -0.18048755824565887], [-0.04423445463180542, 0.0070188939571380615, 0.2281416803598404]]}
GEOMETRY_BASE85 = 'c$}q`e@vBC7{|}Oh^Zl=-uNB7VR*5w)da&S=4}=;3A!uDYNYq3FX<$~3$gr>UQldVY=(w2Z}Nue=8w5yPH9WHWR_(itZb}Z*4^Ctt1-63^@~gA`92Q?t+rNYd+zspKKGpG{CLlMUQbcXB!}X1r^;wg4EIh_iXu)qRGsOsUBAYxxp!mrW}8X?r!uDdO3I2o&)8I*+Ui_u)~xY67a7iiiiJ*>;jF0g*ZO@MS6BJhn#2ozl{Kd3HS2uUrmpAYJ>W8O=emqnjQ?7u@hl=;^xNVIk_HwBUnljBhQ9;fV;ls}DrjW>E%U?HVd%~Cb<DqEUe<3x9l?6iP_&)-UITUY@U|vWBihJ(>(eLDKR@YR)T6tYhwNn-*R|?R<QaL9`Te8jQsU3{1etFTzT*YrDlZA+TO(fP!N^YJnO)BFA6dzKbKp3sdu0joxJOEv?~a^8-m<|%%%5OB<i<J!X$3o(7c+Oq7DDqfE#{9gSJBd?$a5NbLcc9w-k^}*%6DSD?whX-fOojD?`m=UTcnZUEzJ8v)!47Xo&(4;{1Wr(-ezcK`7Y+0gby|I^Ga`IUdg=0z&cfI#}<q`Tq^mywqZXX?7_Hdcp3AjhOnN1dwa_SzQ@9OP|M1jm@i@eoYe+R{;&b_zmd<}Gg?LY-MP_b<_nm=q4+!`hU=NnACTvZ=NNf@5a-K#BboVL+Xk%1Jl%@=kC(#GipYCt_edx2&)}s#>{r$i{2y4p=p@?p`FgSMKOY3QzH0r1#<5PeUB!N^dZ-`my=h00r~Awo=y&EA=V`zG5&E?jUjaYVehvK^9(^Cr`Fa+(`@VDFsyX!t@@zlwIqJm*@>})4c7p%%)2C>^u!Hlw({~R4@B86n>__KujB9k|eo6Vg>9rTpujKsK$ai+mlV~?!f=5~`p699D{n+nmuVTJ|l>NvbFiw2H=eMmJ<6Y(Xcq^A*<n><;L9bm2^ZS^J`Ki?_&hq<wfqCYI%XrVeKY9#&#b-S3y86y8&xG4>-rJ8iy=+&CVyeCkD}3XwLV{Gr^zX02^?Cp9DxCknufn-{4tMLw7QIV+w)okihIrB}@uW`i*`id>(2=7fQ-b^)3Gyxp^7ACf-y@NOZDh?5pQhs$9k)x6j~7pxq9a|$bRAQq{giR-rc0X?@#zv{ZD;DBuTz5PWbp~&XNbm$pCLX~`jSo+jT1jpl=3CZ@kkQ2iBA$gOVloYmUxHsC5;iai%%A%Lf^Dl9k=R86i@6n@pp(OiuV-R?2ed!`h@>k0yL=!AN0TWoOs;F_l(yA{&Dy{MX|Jhdh&L)NozMf8TC6x^5Tg'

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
