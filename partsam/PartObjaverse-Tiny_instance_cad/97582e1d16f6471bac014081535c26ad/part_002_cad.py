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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_002.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_002.stl', 'source_sha256': '81b4317da3df3dc32bb5d2ce937dc54f37ddb189dd12c7fae014195b1375ad64', 'input_faces': 56, 'input_vertices': 50, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.013724005781114101, -0.4581683874130249, 0.014719828963279724], [0.1501571536064148, -0.1501094251871109, 0.18291699886322021]]}
GEOMETRY_BASE85 = 'c$}q{TWkzb7{||UyV@;f(PFpMQLU+JwSq=eVxGJ-nhlDI#5A=_lV;oQ(zs`lxFkaHga=!fxIB<3(FfJhuF{BW5igQW#U<jwCGCSJ=kh-_J4l2{zWo35%eUuz^L=L~>#s~n%_8!eMm%dbSC_d6;W3J2k(NMsQ+-_^GCS0?)j>Rh^GoURs_Lcw8V6}1+qLz9NL^T4NVP@51zIuHf{o!#;o8u;#_;+8=SylEA_2xD8*7^a?7nb*SuveEvzYFr|9WMx5)vzN4lQOHZ4CEzF*OTMbn|;!EqUzuwI0r+fs9UmuY=PAz6YG^#}36s9=P6DF7oxuHSPS~1ShRSkHtED7kb2gD<wB8zCGofG+#BXTyOsz7x@Ft=fr-iP-pjtS0ev*{XHwEUxw}ro-x?U?+ul|&HIvbS|Zn1+&KC1naJPU-y!M%Cp*tbzQMR^<%a*wL%|2N!~8y>*8e2y(Sve*#q~D1Z=&suSf8#&e%rFwVx4|jzX5KZmihWFxo;GlzLM)lcMNn`dF=ddS?9h|Q4guXzISB4aZ|1ntE#^!>MC9SMC6AGL_WRo{knB7G0a7AqhgwvFKvj#llZAtc~0K$>9%s++bPdUp1U)N<2)ER54zfS#K^nyxz39D8sNY5M{(QShq-;e;P!K+xE_4*NbvHC!&Yve?{I#|*(dkCbX4r8_O;DD+R`PS+qCsruUR1anmCf&XT{APP4t<(UlX@-`t^$Jv!g-u*#M8(pG&PXkT3d~c=z<2l_zfXivF7i(>kr3+U61kxA%XT<9QAByozHk^tLS@bJ0s|`Rd&6m*-Y-UG;xROX5*8Q}%y*-Lb{~q_6Fqe%BV7!nS7NW?$Q2t>sh8A-|OV{!?2&@9#df<^TPuoy=;;W03~UgrCKtghdW?GJFpF7-$;2Pdqw%eGuHILn(YZ{3sUVpjim+r$Q<GRQTyEN}**?3Qw^|8G`#cP#-+kLii#UUKTSE+)rZRfTlpb@FSo;s2AP`UkELN&t;L#!iC^I6*>Vv72XM*2=9a^sE42y0zL^b(NaJ6GoTaTXTTRgv*8Qi^P#!$Ts3%Jvm1=-6!=_t4Z;0v7RAs!=oI)o_)Mr9ek2PIiwp$!qgjlFj)!{S{gn=9R?46L%KW^dqG8rQHuhg8zn0cthS*xeFR8!M#b?fj;UvvW`}nCPKLDZq-Q)'

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
