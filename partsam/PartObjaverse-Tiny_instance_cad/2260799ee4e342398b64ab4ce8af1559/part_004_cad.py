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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_004.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_004.stl', 'source_sha256': '480eb25f1e40cec3a9a91086a53387639ec7fb5907d0fc1002554cd73aa68bdc', 'input_faces': 56, 'input_vertices': 40, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.00247105211019516, -0.4499410092830658, -0.18048755824565887], [0.41674304008483887, -0.014588862657546997, 0.2281416803598404]]}
GEOMETRY_BASE85 = 'c$}q`e@xV69LJx7Ll8lM4&~s2uOJ*b0veQL1?SoriNq~en>pl2j-;5LhjXizoXxfVX;b<&XX<xRsJOr%3$q1xmHi+N3C&F^>$Y&Mwf=CeX>(cM=lyw8N2{&XcYF4Ff8Y1{exCR9eD9v~HYVB~O0K2qp~|`)9=lR{q$!8m?hkJ3-01Hv-yC?trZV8`YnCtE|6r4MolR|5Pr2Lu-5Z1Mm4^H7jv9BF;qKTH+!k!x+`1*$?$>^OTUWQ=^1C;+1^m{1X?10pQFTk1@wD+@uT-6(thPOD!B{=^m8Q9A=cs1ryYfACnz2<EasT7D!{E;YruLO%1oggxkxx+9P}Q&L`LYG|k&}ZF-0!-67@ueKUVwjf;JBuG=gOe=BRR+6dtBE}=zHJAeQ$vm#-;y?+>eoOZSyJgn>5hh*VXWWW~{<_8vUIwqEE;eIE{Yy&Ws>u_z3zK;i?JLowJW>8drKG=l92uKN7tMzBzeS`efCH;XildJ<MD4w&dJDg?)&m?LUM5O_Imlc^&&^ZY})~^%cXYSG~D?$b0Kr_-Y^5`^<eOF<<@gNAOSdOU{X*_pz>J^|G%m8zg7#DdY&<d3X%{H}Jjq^4`F6m1CbG?=O4hJ)S>^zM;qWVBMa=KJgn?9z}ihr*oLs^d3Z>uI53^JAO_4m%Xpze%;U!ssB~{1LgtrS<~8&^+kUZzcmHxj5HmBZ$|UZ!}kT?tInP`kvD3H?>ApZ|Me>dus>&?75_}^dE{y7fgd~DC;pS(m(c&+@nhiRCGmF!UcvKq$+FL%Wq%I;;gr`f?`RReZ=R`U@z<BakF6S#yi<>f|7ZjD(R}0^?2kE<J1zZpqkm-ijosqsi{Dx!>#E4_6@NMFJ*ZdSibLS#a@J=^{R3h6v6<VZ<JYUI3ry_u<-5f13dlZIiLZV*`h~ogO1zg)W9{Csch2cEQF7^PBhhMMjrrE;)6o`p^k`FGv;6y`r?dKB9X+?-@xPCrLMuaoHA<}ECYM<wpESr4>Jrv#olEAB1=KmzOE|Q?nJlC(#8!#c%%fgHE++G+7gJ}GF6wM*XI!Ry(n;-PO+MGC*HaX?&LYx9?Iw#!7qyFX7n4h=i>clG3M5#=#-Vj0ht{d&d}_^`s8gvkNe6W%brzXHokg8a&ZADJP9_z#VkWIqNIPkxwlS-nL+d0ml{$%f0hvj?fO-*`MZJi6A(>9SkUEV_rk>5GwYSlh;7I(ZzxF?`kPbfQkN&Su&iz@&Ke@x|^~aCY+n6*@USfjUYH=Dn_d8~2p`r'

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
