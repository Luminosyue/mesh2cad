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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_003.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_003.stl', 'source_sha256': '8d1f1f76396ae8777c100bb85e5f02f8dd44fc5f6d08be27841cf9a6e225eb38', 'input_faces': 42, 'input_vertices': 46, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0024710558354854584, -0.4499409794807434, -0.18048755824565887], [0.5, 0.0070188939571380615, 0.2281416803598404]]}
GEOMETRY_BASE85 = 'c$}q`e@xVM7{@<%fWI;%xr9TCuP7essZ21OBHc!@5~W*mSq=-5BONAi80C-ZAZ-4qP0?r!)Nk2ZqGQ8K(Fu39S=kS=mBt#)+v;ye)5BWbU7zRuJSMc-T7B7j&-1*#&*%9(pYP|x=iDW6@ixWJ40UeT@8L`FN|7cjn`-p>wrpJQZCJ3mZmUHlfzxx#9w_y!az9~FjcU82%G<Es=U8eu3aXbloQ9*i*0;r1x%sJDUzL}5apk54ujUOKD(k#D&d$5fY2?mv8ZR3E^_fIHEGVoBkX><ch^&7@Q$K9D%e<estq;5+qwiCST`j-8N7kRzdYO3eW>*i!pZ&R;crdjG+?D>zNs225J3hp?%b#<d{IpNVh8Eh-ppN|@^8H5F8I1ex%30!}Hk11~k$Vt%W!J%jrKi8ed>_nSjr^jY`jFp$4EaVN_e<n`vAmzG`PEIXKeaFbzAJhj{VeI_J`a6;imX|meF1#oDR9-Ab`<^2Uk$E0WL?b<zmK|)^nMI}@?Gw;=f{sQf6m3v@c!3!aPylZ$n)3iM_)$fQO<v8>2cJ%eqji8szdK!z6bl?#JC%&KY;JE)ZjaNyN}?z-B`ptC-w~1{q(iN=r_EW`D>~P@w6ef;e6)qSS{9<8*OF2ocTKQZN#bPnlXR4i1}l~Ci--})Ha6iG24+}RQ@`jlQQOmfgM<9;lLZ{H@t~?o6(8<gx+niBlXPdhS7&VGkquX=Y(J4{xZs2@I6PiN&R3Q;^F~(AJ@ok=Dn`H$X}L-c~xZbRq$qY0^c#;@fPNZtYogDWjF_(?he$6tYYp;D8~4_3|@ESQRc(0M#R$#USVFw{M8WZ2R+w1n6F{J)qf0i*OX%2!AJ%3&Jd5ES<dT?)-ca`8T+X6QcUL03Xgg5J=YGPjw{;2JZSZxj`PX=%y%;1{&*Mvf2Cl(!DtWjeFmR{2X^p&#jY^-4Dx)o&L-yHGe2zdc^Wy*>y8aE-($4%eid;4`snfgy3wD1S?At>d(3Uv=ehd)3s$8_6ZLIaT{-G1BuLLK`}bGj#=L)b6)yVUS0UYn30mXDTE!<DCqCJU;**^$KG{3OpCp#zM6GdJQ$*z7DIz~!G)~=q$hU~dpCC3-{8X*kT2r+$#3yExnEWg)L+dVipEWAqChu(W-jH`$5>MB<M{ACVe23U{@hNAPR<gwD*lxDT;wMYa45>3q#-(V@*ScFQ#ZIwl;?ujiT6T$v&l77G-!3`xq|RI!m#LMlHB&_XG_8BJk|fR+pSZikVztHn(@*&A$4?tF<_G<+BgY>1(IXS}f%^0CyGs(V-&XxsukCp{E$R<m$;|2'

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
