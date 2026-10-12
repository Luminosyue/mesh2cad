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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_002.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_002.stl', 'source_sha256': '8a41ebddd54cf389dac6471431ed4d5b2aa1fec0f836eab2bdd8fb5e6756a4d3', 'input_faces': 76, 'input_vertices': 61, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[2.66232967376709, 6.882991790771484, -1.0077707767486572], [3.369377613067627, 8.96556282043457, 0.958726167678833]]}
GEOMETRY_BASE85 = 'c$}q{ZD><h7{^cBv^IU2?V4@Ir1so&ZC-2}ownA_u?us<t?DvCR0Nk|)7CLGOKfF0;m!}G4)(@CVfdj={IG#v{IG#+yD9906Si3>tW4BYYwV=Hj12~Zy`1OX|BdHnXE3%K9{&IQ&N<I{@?3JyP4riIe9XQy_SU;!#(S$6qo`v(HkQg9+_yKC?b@Gyy^J+joGwQ{*t&g7Vpka(V~4|osqEfNxQ~Z74E2UPczEbQ=3r)E|H}t5gDK+A4ZNC737#DpNT<a2NYCmHz9!nikMRF`)rb;|?B+_HYKcz-NcBsRQ%_6W`24cPle0U%H)ZZIgBJgNq9F79=(!dv&rHjG*Zj~KZs}8}@3{ES+cZ@k<HT2*YF~ZNT}`f2U*%t7)nEH(K*jY<&)anx#*8WPWM5OWHNN%M4VgRj8(&W>D*5%Zcjf%K;diXxmCX0tHWl3XZTF%)e{wdWsrGeva-^={%0K<KrmA1Rf6m>9J2$K8JHIs=RB<-*sm&uFPn#0g)5CTjCZC;C^7F6Ukn`l;A6;S9bM#`tRPmGd7UcO(-;zI0FPJLs`SrG|&a;QODu0oe<j;Na2Upc!<R$gzYj<eMJ{&#d>SwMhUSsX|&BdUK^QKCxKZgFycc#QAkDs>r?1if;u8$v^lk?~`$L+oy+c|Hl_(w+y^88}oK8qDh6~FZ2f;>N$9_Fh2MP8EM_$1F&^*j7;^)JRXRUi1$E$)84FlFz1WzOnDa%lbsQ^Ac7yROOe^W#%oHQ(XReEp4I>^i%*HOu=toLzg<&OdVaTT|lsO((5B>(NYJ$v2+3F6Sve-$w7vnF^kK&o?j6PrfwBRr!m&B)>lX6Ia#Ac6%T6GvPXQ>e7Sf8$66rc*UtRG$0*01nF{AedO$0`>&3ibv^(4$SD^!(7EFkQ4TEwdqji}-iI+Sd=orrHP(0~UyXJw5%I8yMtIUHFfO76z6E2A@Xhd~OR=U=@}!j_{3604+Tcka16wDe8@?N3ZSZk;(pIc#lYA?F{~GI-G8Td-T?^KPUTDw|!iTjXXe-u)B;Sg?dqqS<w8NA3fGroX41O8L+TkCCCw&}i+9glA3jL#gcEXdc1f%|U!FOS-6Mh3c>62K~DS6V>xCeAE>fuQ}V6<NVK7g@$ct1R8E!Naap0omctQQf5k7EDzxW8feFvg<ret19jTZ!+E51_skB7!1f@T47J%hCHFG=_-aUd5n&SQC>x=@ZC7>mPzAtplU|8sHl+mgp}l_f`DUE9`^Ipg)=Gg|>91`!OW1922>U52ZwZrS<k(E<UdbouYp``wPwu_KN'

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
